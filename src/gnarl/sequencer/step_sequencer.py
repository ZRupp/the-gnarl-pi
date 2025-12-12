"""16-step sequencer module (Pocket Operator style)."""

import logging
import threading
import time
from dataclasses import dataclass
from typing import Callable, Optional

logger = logging.getLogger(__name__)


@dataclass
class Step:
    """Individual sequencer step."""

    active: bool = False
    note: int = 60  # MIDI note (Middle C)
    velocity: int = 100
    length: float = 1.0  # Step length multiplier (0.25 = 1/4, 1.0 = full, 2.0 = double)
    probability: float = 1.0  # Probability of playing (0.0-1.0)

    def __post_init__(self) -> None:
        """Validate step parameters."""
        self.note = max(0, min(127, self.note))
        self.velocity = max(0, min(127, self.velocity))
        self.length = max(0.1, min(4.0, self.length))
        self.probability = max(0.0, min(1.0, self.probability))


class StepSequencer:
    """16-step sequencer with Pocket Operator-style workflow."""

    def __init__(self, num_steps: int = 16, bpm: int = 120):
        """Initialize step sequencer.

        Args:
            num_steps: Number of steps (8 or 16 typically)
            bpm: Tempo in beats per minute
        """
        self.num_steps = num_steps
        self.bpm = bpm
        self.steps = [Step() for _ in range(num_steps)]
        self.current_step = 0
        self.playing = False
        self.recording = False

        # Timing
        self._timer_thread: Optional[threading.Thread] = None
        self._stop_flag = threading.Event()

        # Callbacks
        self._on_step: Optional[Callable[[int, Step], None]] = None
        self._on_note: Optional[Callable[[int, int], None]] = None

        logger.info(f"Step sequencer initialized: {num_steps} steps @ {bpm} BPM")

    def _step_interval(self) -> float:
        """Calculate time interval between steps in seconds.

        Returns:
            Interval in seconds
        """
        # 60 seconds per minute / BPM = seconds per beat
        # Divide by 4 for 16th notes (16 steps = 4 beats)
        return (60.0 / self.bpm) / 4.0

    def _timer_loop(self) -> None:
        """Internal timer loop for sequencer playback."""
        while not self._stop_flag.is_set():
            if self.playing:
                self.advance()

            # Sleep for one step interval
            interval = self._step_interval()
            self._stop_flag.wait(interval)

    def start(self) -> None:
        """Start sequencer playback."""
        if self.playing:
            return

        self.playing = True
        self.current_step = 0

        # Start timer thread
        self._stop_flag.clear()
        self._timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
        self._timer_thread.start()

        logger.info("Sequencer started")

    def stop(self) -> None:
        """Stop sequencer playback."""
        if not self.playing:
            return

        self.playing = False
        self._stop_flag.set()

        if self._timer_thread:
            self._timer_thread.join(timeout=1.0)

        logger.info("Sequencer stopped")

    def advance(self) -> None:
        """Advance to next step and trigger note if active."""
        step = self.steps[self.current_step]

        # Trigger callbacks
        if self._on_step:
            self._on_step(self.current_step, step)

        # Play note if step is active
        if step.active:
            # Check probability
            import random

            if random.random() <= step.probability:
                if self._on_note:
                    self._on_note(step.note, step.velocity)

        # Move to next step
        self.current_step = (self.current_step + 1) % self.num_steps

    def toggle_step(self, step_num: int) -> None:
        """Toggle step on/off.

        Args:
            step_num: Step number (0-indexed)
        """
        if 0 <= step_num < self.num_steps:
            self.steps[step_num].active = not self.steps[step_num].active
            logger.debug(f"Step {step_num}: {'ON' if self.steps[step_num].active else 'OFF'}")

    def set_step_note(self, step_num: int, note: int) -> None:
        """Set note for a specific step.

        Args:
            step_num: Step number (0-indexed)
            note: MIDI note number (0-127)
        """
        if 0 <= step_num < self.num_steps:
            self.steps[step_num].note = max(0, min(127, note))

    def set_step_velocity(self, step_num: int, velocity: int) -> None:
        """Set velocity for a specific step.

        Args:
            step_num: Step number (0-indexed)
            velocity: MIDI velocity (0-127)
        """
        if 0 <= step_num < self.num_steps:
            self.steps[step_num].velocity = max(0, min(127, velocity))

    def set_step_length(self, step_num: int, length: float) -> None:
        """Set length multiplier for a specific step.

        Args:
            step_num: Step number (0-indexed)
            length: Length multiplier (0.25-4.0)
        """
        if 0 <= step_num < self.num_steps:
            self.steps[step_num].length = max(0.25, min(4.0, length))

    def set_bpm(self, bpm: int) -> None:
        """Set sequencer tempo.

        Args:
            bpm: Beats per minute (20-300)
        """
        self.bpm = max(20, min(300, bpm))
        logger.info(f"BPM set to {self.bpm}")

    def clear(self) -> None:
        """Clear all steps."""
        for step in self.steps:
            step.active = False
        logger.info("Sequencer cleared")

    def clear_step(self, step_num: int) -> None:
        """Clear a specific step.

        Args:
            step_num: Step number (0-indexed)
        """
        if 0 <= step_num < self.num_steps:
            self.steps[step_num].active = False

    def set_pattern(self, pattern: list[bool]) -> None:
        """Set step pattern from list of booleans.

        Args:
            pattern: List of active states (must match num_steps)
        """
        if len(pattern) != self.num_steps:
            logger.warning(f"Pattern length {len(pattern)} doesn't match {self.num_steps} steps")
            return

        for i, active in enumerate(pattern):
            self.steps[i].active = active

    def get_pattern(self) -> list[bool]:
        """Get current step pattern.

        Returns:
            List of active states
        """
        return [step.active for step in self.steps]

    def on_step(self, callback: Callable[[int, Step], None]) -> None:
        """Register callback for each step advancement.

        Args:
            callback: Function(step_number, step)
        """
        self._on_step = callback

    def on_note(self, callback: Callable[[int, int], None]) -> None:
        """Register callback for note triggers.

        Args:
            callback: Function(note, velocity)
        """
        self._on_note = callback

    def start_recording(self) -> None:
        """Start recording mode (capture button presses as steps)."""
        self.recording = True
        self.current_step = 0
        logger.info("Recording started")

    def stop_recording(self) -> None:
        """Stop recording mode."""
        self.recording = False
        logger.info("Recording stopped")

    def close(self) -> None:
        """Clean up sequencer resources."""
        self.stop()

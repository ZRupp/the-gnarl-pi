"""LED bar graph display for visual parameter feedback."""

import logging
from typing import Optional

from gnarl.hardware.shift_register import ShiftRegister

logger = logging.getLogger(__name__)


class LEDBarGraph:
    """10-segment LED bar graph for parameter visualization.

    Can use direct GPIO or shift registers for output control.
    """

    def __init__(
        self,
        num_segments: int = 10,
        shift_register: Optional[ShiftRegister] = None,
        start_output: int = 0,
    ):
        """Initialize LED bar graph.

        Args:
            num_segments: Number of LED segments (typically 10)
            shift_register: Optional shift register for output control
            start_output: Starting output index on shift register
        """
        self.num_segments = num_segments
        self.shift_register = shift_register
        self.start_output = start_output
        self.current_level = 0

        logger.info(f"LED bar graph initialized: {num_segments} segments")

    def set_level(self, value: int, max_value: int = 127) -> None:
        """Set bar level based on value.

        Args:
            value: Current value
            max_value: Maximum value (for scaling)
        """
        # Calculate how many LEDs to light
        num_leds = int((value / max_value) * self.num_segments)
        num_leds = max(0, min(self.num_segments, num_leds))

        self.current_level = num_leds

        if self.shift_register:
            # Update shift register outputs
            for i in range(self.num_segments):
                output_idx = self.start_output + i
                self.shift_register.set_output(output_idx, i < num_leds)
            self.shift_register.update()

    def set_level_percent(self, percent: float) -> None:
        """Set bar level as percentage.

        Args:
            percent: Percentage (0.0-100.0)
        """
        self.set_level(int(percent), 100)

    def set_pattern(self, pattern: list[bool]) -> None:
        """Set custom LED pattern.

        Args:
            pattern: List of LED states (must match num_segments)
        """
        if len(pattern) != self.num_segments:
            logger.warning(
                f"Pattern length {len(pattern)} doesn't match {self.num_segments} segments"
            )
            return

        if self.shift_register:
            for i, state in enumerate(pattern):
                output_idx = self.start_output + i
                self.shift_register.set_output(output_idx, state)
            self.shift_register.update()

    def clear(self) -> None:
        """Turn off all LEDs."""
        self.set_level(0)

    def fill(self) -> None:
        """Turn on all LEDs."""
        self.set_level(self.num_segments, self.num_segments)

    def test_pattern(self) -> None:
        """Display walking LED test pattern."""
        import time

        logger.info("Running LED bar test pattern")

        # Walk up
        for i in range(self.num_segments + 1):
            self.set_level(i, self.num_segments)
            time.sleep(0.1)

        # Walk down
        for i in range(self.num_segments, -1, -1):
            self.set_level(i, self.num_segments)
            time.sleep(0.1)

        # Flash all
        for _ in range(3):
            self.fill()
            time.sleep(0.2)
            self.clear()
            time.sleep(0.2)


class VUMeter(LEDBarGraph):
    """VU meter display using LED bar graph."""

    def __init__(self, *args: any, **kwargs: any):
        """Initialize VU meter."""
        super().__init__(*args, **kwargs)
        self.peak_hold = 0
        self.peak_decay_rate = 0.95

    def set_audio_level(self, level: float) -> None:
        """Set audio level with peak hold.

        Args:
            level: Audio level (0.0-1.0)
        """
        level_percent = level * 100

        # Update peak hold
        if level_percent > self.peak_hold:
            self.peak_hold = level_percent
        else:
            self.peak_hold *= self.peak_decay_rate

        # Display with peak indicator
        num_leds = int((level_percent / 100) * self.num_segments)
        peak_led = int((self.peak_hold / 100) * self.num_segments)

        pattern = [False] * self.num_segments
        for i in range(num_leds):
            pattern[i] = True
        if peak_led < self.num_segments:
            pattern[peak_led] = True

        self.set_pattern(pattern)

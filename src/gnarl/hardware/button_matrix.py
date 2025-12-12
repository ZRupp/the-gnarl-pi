"""Button matrix scanner for compact multi-button input."""

import logging
import time
from typing import Callable, Optional

from gpiozero import Button, OutputDevice

logger = logging.getLogger(__name__)


class ButtonMatrix:
    """Matrix keyboard scanner for efficient multi-button input.

    Uses matrix scanning to read many buttons with fewer GPIO pins.
    Example: 16 buttons using 4 rows + 4 cols = 8 GPIO pins instead of 16.
    """

    def __init__(self, row_pins: list[int], col_pins: list[int], debounce_time: float = 0.02):
        """Initialize button matrix.

        Args:
            row_pins: GPIO pins for rows (outputs)
            col_pins: GPIO pins for columns (inputs with pull-ups)
            debounce_time: Debounce time in seconds
        """
        self.num_rows = len(row_pins)
        self.num_cols = len(col_pins)
        self.num_buttons = self.num_rows * self.num_cols
        self.debounce_time = debounce_time

        # Initialize GPIO
        self.rows = [OutputDevice(pin) for pin in row_pins]
        self.cols = [Button(pin, pull_up=True, bounce_time=debounce_time) for pin in col_pins]

        # Button state tracking
        self.state = [[False] * self.num_cols for _ in range(self.num_rows)]
        self.last_scan_time = 0

        # Callbacks
        self._on_press: Optional[Callable[[int], None]] = None
        self._on_release: Optional[Callable[[int], None]] = None

        # Turn off all rows initially
        for row in self.rows:
            row.off()

        logger.info(
            f"Button matrix initialized: {self.num_rows}x{self.num_cols} = {self.num_buttons} buttons"
        )

    def _button_number(self, row: int, col: int) -> int:
        """Convert row/col to button number (0-indexed).

        Args:
            row: Row index
            col: Column index

        Returns:
            Button number
        """
        return row * self.num_cols + col

    def scan(self) -> list[int]:
        """Scan button matrix and return list of pressed buttons.

        Returns:
            List of pressed button numbers
        """
        current_time = time.time()
        if current_time - self.last_scan_time < self.debounce_time:
            # Don't scan too frequently (debouncing)
            return []

        pressed = []
        changed_presses = []
        changed_releases = []

        for row_idx, row in enumerate(self.rows):
            # Activate this row
            row.on()
            time.sleep(0.0001)  # Small delay for signal stabilization

            # Check each column
            for col_idx, col in enumerate(self.cols):
                is_pressed = col.is_pressed
                was_pressed = self.state[row_idx][col_idx]

                if is_pressed:
                    button_num = self._button_number(row_idx, col_idx)
                    pressed.append(button_num)

                # Detect state changes
                if is_pressed and not was_pressed:
                    # Button just pressed
                    self.state[row_idx][col_idx] = True
                    button_num = self._button_number(row_idx, col_idx)
                    changed_presses.append(button_num)
                    logger.debug(f"Button {button_num} pressed")

                elif not is_pressed and was_pressed:
                    # Button just released
                    self.state[row_idx][col_idx] = False
                    button_num = self._button_number(row_idx, col_idx)
                    changed_releases.append(button_num)
                    logger.debug(f"Button {button_num} released")

            # Deactivate this row
            row.off()

        self.last_scan_time = current_time

        # Trigger callbacks for state changes
        if self._on_press:
            for button_num in changed_presses:
                self._on_press(button_num)

        if self._on_release:
            for button_num in changed_releases:
                self._on_release(button_num)

        return pressed

    def is_pressed(self, button_num: int) -> bool:
        """Check if a specific button is currently pressed.

        Args:
            button_num: Button number (0-indexed)

        Returns:
            True if pressed, False otherwise
        """
        if button_num >= self.num_buttons:
            return False

        row = button_num // self.num_cols
        col = button_num % self.num_cols
        return self.state[row][col]

    def on_press(self, callback: Callable[[int], None]) -> None:
        """Register callback for button press events.

        Args:
            callback: Function(button_number)
        """
        self._on_press = callback

    def on_release(self, callback: Callable[[int], None]) -> None:
        """Register callback for button release events.

        Args:
            callback: Function(button_number)
        """
        self._on_release = callback

    def get_button_coords(self, button_num: int) -> tuple[int, int]:
        """Get row/col coordinates for a button number.

        Args:
            button_num: Button number (0-indexed)

        Returns:
            Tuple of (row, col)
        """
        row = button_num // self.num_cols
        col = button_num % self.num_cols
        return (row, col)

    def close(self) -> None:
        """Clean up GPIO resources."""
        try:
            for row in self.rows:
                row.close()
            for col in self.cols:
                col.close()
        except Exception as e:
            logger.error(f"Error closing button matrix: {e}")


class ButtonMode:
    """Defines different button matrix modes."""

    SEQUENCER = "sequencer"  # 16-step sequencer
    KEYBOARD = "keyboard"  # Chromatic keyboard
    CHORDS = "chords"  # Chord triggers
    PRESETS = "presets"  # Preset selector

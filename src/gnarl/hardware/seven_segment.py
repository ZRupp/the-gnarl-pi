"""7-segment display handler for numeric output."""

import logging
from typing import Optional

from gnarl.hardware.shift_register import ShiftRegister

logger = logging.getLogger(__name__)


class SevenSegmentDisplay:
    """4-digit 7-segment display (common cathode or anode).

    Can use shift registers or direct GPIO for control.
    """

    # Segment mapping (bits: DP G F E D C B A)
    DIGITS = {
        "0": 0b00111111,
        "1": 0b00000110,
        "2": 0b01011011,
        "3": 0b01001111,
        "4": 0b01100110,
        "5": 0b01101101,
        "6": 0b01111101,
        "7": 0b00000111,
        "8": 0b01111111,
        "9": 0b01101111,
        "A": 0b01110111,
        "b": 0b01111100,
        "C": 0b00111001,
        "d": 0b01011110,
        "E": 0b01111001,
        "F": 0b01110001,
        "H": 0b01110110,
        "L": 0b00111000,
        "P": 0b01110011,
        "U": 0b00111110,
        "-": 0b01000000,
        " ": 0b00000000,
        ".": 0b10000000,  # Decimal point
    }

    def __init__(
        self,
        num_digits: int = 4,
        shift_register: Optional[ShiftRegister] = None,
        common_anode: bool = False,
    ):
        """Initialize 7-segment display.

        Args:
            num_digits: Number of digits (1-4)
            shift_register: Optional shift register for control
            common_anode: True for common anode, False for common cathode
        """
        self.num_digits = num_digits
        self.shift_register = shift_register
        self.common_anode = common_anode
        self.buffer = [" "] * num_digits

        logger.info(
            f"7-segment display initialized: {num_digits} digits, "
            f"{'common anode' if common_anode else 'common cathode'}"
        )

    def _encode_char(self, char: str) -> int:
        """Encode character to 7-segment pattern.

        Args:
            char: Character to encode

        Returns:
            Segment pattern byte
        """
        char = char.upper()
        pattern = self.DIGITS.get(char, 0b00000000)

        # Invert for common anode
        if self.common_anode:
            pattern = ~pattern & 0xFF

        return pattern

    def show(self, text: str, right_align: bool = True) -> None:
        """Display text on 7-segment display.

        Args:
            text: Text to display (max num_digits characters)
            right_align: Align text to right if True, left if False
        """
        # Truncate or pad text
        if len(text) > self.num_digits:
            text = text[: self.num_digits]
        elif len(text) < self.num_digits:
            if right_align:
                text = " " * (self.num_digits - len(text)) + text
            else:
                text = text + " " * (self.num_digits - len(text))

        self.buffer = list(text)
        self._update_display()

    def show_number(self, value: int, leading_zeros: bool = False) -> None:
        """Display integer number.

        Args:
            value: Number to display
            leading_zeros: Show leading zeros if True
        """
        if leading_zeros:
            text = f"{value:0{self.num_digits}d}"
        else:
            text = str(value)

        self.show(text, right_align=True)

    def show_float(self, value: float, decimals: int = 1) -> None:
        """Display floating point number.

        Args:
            value: Number to display
            decimals: Number of decimal places
        """
        text = f"{value:.{decimals}f}"
        self.show(text, right_align=True)

    def show_hex(self, value: int) -> None:
        """Display hexadecimal number.

        Args:
            value: Number to display in hex
        """
        text = f"{value:0{self.num_digits}X}"
        self.show(text, right_align=True)

    def _update_display(self) -> None:
        """Update physical display with buffer contents."""
        if not self.shift_register:
            logger.debug("No shift register configured, display update skipped")
            return

        # Encode each digit and send to shift register
        # This is a simplified version - real implementation depends on
        # your specific hardware configuration (multiplexing, etc.)
        for i, char in enumerate(self.buffer):
            pattern = self._encode_char(char)
            # Set appropriate shift register outputs
            # (Implementation depends on your wiring)
            logger.debug(f"Digit {i}: '{char}' = 0b{pattern:08b}")

    def clear(self) -> None:
        """Clear display (show blanks)."""
        self.show(" " * self.num_digits)

    def test_pattern(self) -> None:
        """Display test pattern (count 0-9)."""
        import time

        logger.info("Running 7-segment test pattern")

        # Count 0-9999
        max_val = 10**self.num_digits - 1
        for i in range(0, min(100, max_val), 11):
            self.show_number(i)
            time.sleep(0.2)

        # Show all segments
        self.show("8" * self.num_digits)
        time.sleep(0.5)

        self.clear()


class SingleDigitDisplay:
    """Single 7-segment digit display."""

    def __init__(self, shift_register: Optional[ShiftRegister] = None, start_output: int = 0):
        """Initialize single digit display.

        Args:
            shift_register: Optional shift register for control
            start_output: Starting output index
        """
        self.display = SevenSegmentDisplay(num_digits=1, shift_register=shift_register)
        self.start_output = start_output

    def show(self, char: str) -> None:
        """Display single character.

        Args:
            char: Character to display
        """
        self.display.show(char)

    def show_number(self, value: int) -> None:
        """Display single digit number (0-9).

        Args:
            value: Number to display (0-9)
        """
        if 0 <= value <= 9:
            self.show(str(value))
        else:
            self.show("-")

    def clear(self) -> None:
        """Clear display."""
        self.display.clear()

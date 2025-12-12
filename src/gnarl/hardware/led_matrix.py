"""8x8 LED matrix display for waveforms and patterns."""

import logging
from enum import Enum
from typing import Optional

from gnarl.hardware.shift_register import ShiftRegister

logger = logging.getLogger(__name__)


class WaveformType(str, Enum):
    """Waveform types for visualization."""

    SINE = "sine"
    SAWTOOTH = "sawtooth"
    SQUARE = "square"
    TRIANGLE = "triangle"
    NOISE = "noise"


class LEDMatrix8x8:
    """8x8 LED matrix display for waveforms, patterns, and graphics.

    Can use shift registers (2 registers for 8x8 = 16 outputs) or
    MAX7219 driver chip.
    """

    def __init__(self, shift_register: Optional[ShiftRegister] = None, use_max7219: bool = False):
        """Initialize 8x8 LED matrix.

        Args:
            shift_register: Optional shift register for row/column control
            use_max7219: Use MAX7219 driver chip if True
        """
        self.shift_register = shift_register
        self.use_max7219 = use_max7219
        self.buffer = [0b00000000] * 8  # 8 rows of 8 bits

        logger.info("8x8 LED matrix initialized")

    def set_pixel(self, x: int, y: int, state: bool) -> None:
        """Set individual pixel.

        Args:
            x: X coordinate (0-7)
            y: Y coordinate (0-7)
            state: True for on, False for off
        """
        if 0 <= x < 8 and 0 <= y < 8:
            if state:
                self.buffer[y] |= 1 << x
            else:
                self.buffer[y] &= ~(1 << x)

    def get_pixel(self, x: int, y: int) -> bool:
        """Get pixel state.

        Args:
            x: X coordinate (0-7)
            y: Y coordinate (0-7)

        Returns:
            True if pixel is on, False otherwise
        """
        if 0 <= x < 8 and 0 <= y < 8:
            return bool(self.buffer[y] & (1 << x))
        return False

    def set_row(self, row: int, pattern: int) -> None:
        """Set entire row pattern.

        Args:
            row: Row number (0-7)
            pattern: 8-bit pattern
        """
        if 0 <= row < 8:
            self.buffer[row] = pattern & 0xFF

    def set_pattern(self, pattern: list[int]) -> None:
        """Set complete 8x8 pattern.

        Args:
            pattern: List of 8 bytes (one per row)
        """
        if len(pattern) != 8:
            logger.warning(f"Pattern must have 8 rows, got {len(pattern)}")
            return

        self.buffer = [p & 0xFF for p in pattern]
        self._update_display()

    def draw_waveform(self, waveform: WaveformType) -> None:
        """Draw waveform visualization.

        Args:
            waveform: Type of waveform to draw
        """
        import math

        pattern = [0] * 8

        if waveform == WaveformType.SINE:
            # Sine wave
            for x in range(8):
                y = int(3.5 + 3 * math.sin(x * math.pi / 4))
                pattern[y] |= 1 << x

        elif waveform == WaveformType.SAWTOOTH:
            # Sawtooth wave
            for x in range(8):
                y = 7 - x
                pattern[y] |= 1 << x

        elif waveform == WaveformType.SQUARE:
            # Square wave
            for x in range(8):
                y = 1 if x < 4 else 6
                pattern[y] |= 1 << x

        elif waveform == WaveformType.TRIANGLE:
            # Triangle wave
            for x in range(8):
                if x < 4:
                    y = 7 - (x * 2)
                else:
                    y = ((x - 4) * 2) + 1
                pattern[y] |= 1 << x

        elif waveform == WaveformType.NOISE:
            # Random noise
            import random

            for x in range(8):
                y = random.randint(0, 7)
                pattern[y] |= 1 << x

        self.set_pattern(pattern)

    def draw_icon(self, icon_name: str) -> None:
        """Draw predefined icon.

        Args:
            icon_name: Icon name (e.g., 'skull', 'note', 'play')
        """
        icons = {
            "skull": [
                0b00111100,
                0b01111110,
                0b11011011,
                0b11111111,
                0b01111110,
                0b00111100,
                0b00100100,
                0b01000010,
            ],
            "note": [
                0b00000110,
                0b00000110,
                0b00000110,
                0b01100110,
                0b11110110,
                0b11110110,
                0b01100110,
                0b00000000,
            ],
            "play": [
                0b00010000,
                0b00110000,
                0b01110000,
                0b11110000,
                0b01110000,
                0b00110000,
                0b00010000,
                0b00000000,
            ],
            "pause": [
                0b01100110,
                0b01100110,
                0b01100110,
                0b01100110,
                0b01100110,
                0b01100110,
                0b01100110,
                0b00000000,
            ],
            "heart": [
                0b01100110,
                0b11111111,
                0b11111111,
                0b11111111,
                0b01111110,
                0b00111100,
                0b00011000,
                0b00000000,
            ],
        }

        if icon_name in icons:
            self.set_pattern(icons[icon_name])
        else:
            logger.warning(f"Unknown icon: {icon_name}")

    def draw_step_position(self, step: int, total_steps: int = 8) -> None:
        """Visualize current step position in sequencer.

        Args:
            step: Current step (0-indexed)
            total_steps: Total number of steps
        """
        pattern = [0] * 8

        # Draw all steps as dots
        for s in range(min(total_steps, 8)):
            pattern[7] |= 1 << s

        # Highlight current step
        if step < 8:
            for y in range(7):
                pattern[y] |= 1 << step

        self.set_pattern(pattern)

    def scroll_text(self, text: str, delay: float = 0.1) -> None:
        """Scroll text across display.

        Args:
            text: Text to scroll
            delay: Delay between frames in seconds
        """
        import time

        # Font data (5x7 pixels per character)
        # Simplified - you'd need a full font library for all characters
        font = {
            "A": [0x3E, 0x41, 0x41, 0x7F, 0x41],
            "B": [0x7F, 0x49, 0x49, 0x36, 0x00],
            # Add more characters as needed...
        }

        for char in text.upper():
            if char in font:
                char_data = font[char]
                # Scroll character across display
                for offset in range(8):
                    pattern = [0] * 8
                    for col, data in enumerate(char_data):
                        if offset + col < 8:
                            for row in range(8):
                                if data & (1 << row):
                                    pattern[row] |= 1 << (offset + col)
                    self.set_pattern(pattern)
                    time.sleep(delay)

    def clear(self) -> None:
        """Clear display."""
        self.buffer = [0b00000000] * 8
        self._update_display()

    def fill(self) -> None:
        """Fill display (all LEDs on)."""
        self.buffer = [0b11111111] * 8
        self._update_display()

    def _update_display(self) -> None:
        """Update physical display with buffer contents."""
        if self.shift_register:
            # Send buffer to shift registers
            # Row-by-row multiplexing or direct control
            # Implementation depends on your specific wiring
            logger.debug("Updating LED matrix display")
        elif self.use_max7219:
            # Send to MAX7219 via SPI
            # Would need MAX7219 library integration
            pass

    def test_pattern(self) -> None:
        """Display test pattern."""
        import time

        logger.info("Running LED matrix test pattern")

        # Checkerboard
        pattern1 = [0b01010101, 0b10101010] * 4
        self.set_pattern(pattern1)
        time.sleep(0.5)

        # Horizontal lines
        pattern2 = [0b11111111, 0b00000000] * 4
        self.set_pattern(pattern2)
        time.sleep(0.5)

        # Border
        pattern3 = [
            0b11111111,
            0b10000001,
            0b10000001,
            0b10000001,
            0b10000001,
            0b10000001,
            0b10000001,
            0b11111111,
        ]
        self.set_pattern(pattern3)
        time.sleep(0.5)

        # Draw all waveforms
        for waveform in WaveformType:
            self.draw_waveform(waveform)
            time.sleep(0.5)

        self.clear()

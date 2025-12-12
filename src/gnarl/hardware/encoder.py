"""Rotary encoder handler."""

import logging
from typing import Callable, Optional

from gpiozero import Button, RotaryEncoder as GPIOZeroEncoder

from gnarl.config import EncoderConfig

logger = logging.getLogger(__name__)


class RotaryEncoder:
    """Handler for rotary encoder with optional push button."""

    def __init__(self, config: EncoderConfig) -> None:
        """Initialize rotary encoder.

        Args:
            config: Encoder configuration
        """
        self.config = config
        self.value = config.default
        self._on_change: Optional[Callable[[int], None]] = None
        self._on_press: Optional[Callable[[], None]] = None

        # Initialize hardware
        try:
            self.encoder = GPIOZeroEncoder(
                a=config.clk_pin,
                b=config.dt_pin,
                bounce_time=0.01,  # 10ms debounce
            )
            self.encoder.when_rotated_clockwise = self._handle_clockwise
            self.encoder.when_rotated_counter_clockwise = self._handle_counter_clockwise

            # Optional push button
            self.button: Optional[Button] = None
            if config.sw_pin is not None:
                self.button = Button(config.sw_pin, pull_up=True, bounce_time=0.05)
                self.button.when_pressed = self._handle_press

            logger.info(
                f"Encoder '{config.name}' initialized on pins {config.clk_pin}/{config.dt_pin}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize encoder '{config.name}': {e}")
            raise

    def _handle_clockwise(self) -> None:
        """Handle clockwise rotation."""
        if self.value < self.config.max_value:
            self.value += 1
            self._trigger_change()

    def _handle_counter_clockwise(self) -> None:
        """Handle counter-clockwise rotation."""
        if self.value > self.config.min_value:
            self.value -= 1
            self._trigger_change()

    def _handle_press(self) -> None:
        """Handle button press."""
        if self._on_press is not None:
            self._on_press()

    def _trigger_change(self) -> None:
        """Trigger change callback."""
        logger.debug(f"Encoder '{self.config.name}' value: {self.value}")
        if self._on_change is not None:
            self._on_change(self.value)

    def on_change(self, callback: Callable[[int], None]) -> None:
        """Register callback for value changes.

        Args:
            callback: Function to call with new value
        """
        self._on_change = callback

    def on_press(self, callback: Callable[[], None]) -> None:
        """Register callback for button press.

        Args:
            callback: Function to call when button is pressed
        """
        self._on_press = callback

    def reset(self) -> None:
        """Reset encoder to default value."""
        self.value = self.config.default
        self._trigger_change()

    def set_value(self, value: int) -> None:
        """Set encoder value directly.

        Args:
            value: New value (clamped to min/max)
        """
        self.value = max(self.config.min_value, min(self.config.max_value, value))
        self._trigger_change()

    def close(self) -> None:
        """Clean up encoder resources."""
        try:
            self.encoder.close()
            if self.button is not None:
                self.button.close()
        except Exception as e:
            logger.error(f"Error closing encoder '{self.config.name}': {e}")

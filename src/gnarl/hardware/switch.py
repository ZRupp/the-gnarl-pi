"""Switch/button handler."""

import logging
from typing import Callable, Optional

from gpiozero import Button

from gnarl.config import SwitchConfig

logger = logging.getLogger(__name__)


class Switch:
    """Handler for momentary switches/buttons."""

    def __init__(self, config: SwitchConfig) -> None:
        """Initialize switch.

        Args:
            config: Switch configuration
        """
        self.config = config
        self._on_press: Optional[Callable[[], None]] = None
        self._on_release: Optional[Callable[[], None]] = None

        try:
            self.button = Button(config.pin, pull_up=True, bounce_time=0.05)
            self.button.when_pressed = self._handle_press
            self.button.when_released = self._handle_release

            logger.info(f"Switch '{config.name}' initialized on pin {config.pin}")
        except Exception as e:
            logger.error(f"Failed to initialize switch '{config.name}': {e}")
            raise

    def _handle_press(self) -> None:
        """Handle button press."""
        logger.debug(f"Switch '{self.config.name}' pressed")
        if self._on_press is not None:
            self._on_press()

    def _handle_release(self) -> None:
        """Handle button release."""
        logger.debug(f"Switch '{self.config.name}' released")
        if self._on_release is not None:
            self._on_release()

    def on_press(self, callback: Callable[[], None]) -> None:
        """Register callback for button press.

        Args:
            callback: Function to call when pressed
        """
        self._on_press = callback

    def on_release(self, callback: Callable[[], None]) -> None:
        """Register callback for button release.

        Args:
            callback: Function to call when released
        """
        self._on_release = callback

    @property
    def is_pressed(self) -> bool:
        """Check if button is currently pressed."""
        return self.button.is_pressed

    def close(self) -> None:
        """Clean up switch resources."""
        try:
            self.button.close()
        except Exception as e:
            logger.error(f"Error closing switch '{self.config.name}': {e}")

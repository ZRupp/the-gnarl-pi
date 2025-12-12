"""Analog joystick handler via MCP3008 ADC."""

import logging
from typing import Callable, Optional

from gpiozero import Button, MCP3008

from gnarl.config import JoystickConfig

logger = logging.getLogger(__name__)


class AnalogJoystick:
    """Handler for dual-axis analog joystick with MCP3008 ADC."""

    def __init__(self, config: JoystickConfig) -> None:
        """Initialize analog joystick.

        Args:
            config: Joystick configuration
        """
        self.config = config
        self._on_move: Optional[Callable[[int, int], None]] = None
        self._on_press: Optional[Callable[[], None]] = None

        try:
            # Initialize MCP3008 channels for X and Y axes
            self.x_axis = MCP3008(channel=config.x_channel, device=config.spi_device)
            self.y_axis = MCP3008(channel=config.y_channel, device=config.spi_device)

            # Initialize button if configured
            self.button: Optional[Button] = None
            if config.sw_pin is not None:
                self.button = Button(config.sw_pin, pull_up=True, bounce_time=0.05)
                self.button.when_pressed = self._handle_press

            # Calibration values (center position)
            self._x_center = 0.5
            self._y_center = 0.5
            self._calibrated = False

            logger.info(
                f"Joystick initialized on MCP3008 channels {config.x_channel}/{config.y_channel}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize joystick: {e}")
            raise

    def _handle_press(self) -> None:
        """Handle button press."""
        logger.debug("Joystick button pressed")
        if self._on_press is not None:
            self._on_press()

    def read_raw(self) -> tuple[float, float]:
        """Read raw joystick values (0.0 to 1.0).

        Returns:
            Tuple of (x, y) values
        """
        return (self.x_axis.value, self.y_axis.value)

    def read(self) -> tuple[int, int]:
        """Read joystick values as MIDI CC values (0-127).

        Applies deadzone and centers at 64.

        Returns:
            Tuple of (x, y) values in MIDI range
        """
        x_raw, y_raw = self.read_raw()

        # Apply deadzone
        deadzone = self.config.deadzone / 100.0
        x_centered = x_raw - self._x_center
        y_centered = y_raw - self._y_center

        # Apply deadzone
        if abs(x_centered) < deadzone:
            x_centered = 0.0
        if abs(y_centered) < deadzone:
            y_centered = 0.0

        # Convert to MIDI range (0-127, centered at 64)
        x_midi = int((x_centered + 0.5) * 127)
        y_midi = int((y_centered + 0.5) * 127)

        # Clamp to valid range
        x_midi = max(0, min(127, x_midi))
        y_midi = max(0, min(127, y_midi))

        return (x_midi, y_midi)

    def calibrate(self) -> None:
        """Calibrate joystick by reading center position.

        Call this when joystick is at rest/center position.
        """
        x, y = self.read_raw()
        self._x_center = x
        self._y_center = y
        self._calibrated = True
        logger.info(f"Joystick calibrated: center=({x:.3f}, {y:.3f})")

    def on_move(self, callback: Callable[[int, int], None]) -> None:
        """Register callback for joystick movement.

        Args:
            callback: Function to call with (x, y) MIDI values
        """
        self._on_move = callback

    def on_press(self, callback: Callable[[], None]) -> None:
        """Register callback for button press.

        Args:
            callback: Function to call when button is pressed
        """
        self._on_press = callback

    def poll(self) -> None:
        """Poll joystick and trigger callbacks if changed.

        Should be called regularly (e.g., 50-100Hz) from main loop.
        """
        x, y = self.read()
        if self._on_move is not None:
            self._on_move(x, y)

    def close(self) -> None:
        """Clean up joystick resources."""
        try:
            self.x_axis.close()
            self.y_axis.close()
            if self.button is not None:
                self.button.close()
        except Exception as e:
            logger.error(f"Error closing joystick: {e}")

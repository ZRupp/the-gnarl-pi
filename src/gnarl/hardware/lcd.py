"""LCD display handler for 1602A displays."""

import logging
from typing import Optional

from gnarl.config import LCDConfig, LCDType

logger = logging.getLogger(__name__)


class LCDDisplay:
    """Handler for 1602A LCD display (I2C or parallel)."""

    def __init__(self, config: LCDConfig) -> None:
        """Initialize LCD display.

        Args:
            config: LCD configuration
        """
        self.config = config
        self.lcd: Optional[Any] = None
        self._initialize()

    def _initialize(self) -> None:
        """Initialize the LCD hardware."""
        try:
            if self.config.type == LCDType.I2C:
                self._initialize_i2c()
            else:
                self._initialize_parallel()
            self.clear()
            logger.info(f"LCD initialized: {self.config.type.value}")
        except Exception as e:
            logger.error(f"Failed to initialize LCD: {e}")
            raise

    def _initialize_i2c(self) -> None:
        """Initialize I2C LCD."""
        try:
            from RPLCD.i2c import CharLCD

            self.lcd = CharLCD(
                i2c_expander="PCF8574",
                address=self.config.address,
                cols=self.config.cols,
                rows=self.config.rows,
            )
        except ImportError:
            logger.error("RPLCD library not installed. Run: pip install RPLCD")
            raise

    def _initialize_parallel(self) -> None:
        """Initialize parallel LCD."""
        try:
            from RPLCD.gpio import CharLCD
            import RPi.GPIO as GPIO

            if not all([self.config.rs_pin, self.config.e_pin, self.config.data_pins]):
                raise ValueError("Parallel LCD requires rs_pin, e_pin, and data_pins")

            self.lcd = CharLCD(
                pin_rs=self.config.rs_pin,
                pin_e=self.config.e_pin,
                pins_data=self.config.data_pins,
                numbering_mode=GPIO.BCM,
                cols=self.config.cols,
                rows=self.config.rows,
            )
        except ImportError:
            logger.error("RPLCD library not installed. Run: pip install RPLCD")
            raise

    def write(self, text: str, row: int = 0, col: int = 0) -> None:
        """Write text to LCD at specified position.

        Args:
            text: Text to display
            row: Row number (0-based)
            col: Column number (0-based)
        """
        if self.lcd is None:
            logger.warning("LCD not initialized")
            return

        try:
            self.lcd.cursor_pos = (row, col)
            # Truncate text if too long
            max_len = self.config.cols - col
            self.lcd.write_string(text[:max_len])
        except Exception as e:
            logger.error(f"Failed to write to LCD: {e}")

    def clear(self) -> None:
        """Clear the LCD display."""
        if self.lcd is None:
            return

        try:
            self.lcd.clear()
        except Exception as e:
            logger.error(f"Failed to clear LCD: {e}")

    def display_preset(self, name: str, parameter: str = "", value: str = "") -> None:
        """Display preset name and current parameter.

        Args:
            name: Preset name (displayed on row 0)
            parameter: Parameter name (displayed on row 1)
            value: Parameter value (displayed on row 1 after parameter)
        """
        self.clear()
        self.write(name, row=0, col=0)
        if parameter:
            display_text = f"{parameter}:{value}" if value else parameter
            self.write(display_text, row=1, col=0)

    def close(self) -> None:
        """Clean up LCD resources."""
        if self.lcd is not None:
            try:
                self.lcd.close()
            except Exception as e:
                logger.error(f"Error closing LCD: {e}")


# Type hint fix
from typing import Any

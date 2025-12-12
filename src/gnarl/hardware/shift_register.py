"""SN74HC595 shift register handler for LED control."""

import logging
from typing import Optional

from gpiozero import OutputDevice

from gnarl.config import ShiftRegisterConfig

logger = logging.getLogger(__name__)


class ShiftRegister:
    """Handler for SN74HC595 shift register chains."""

    def __init__(self, config: ShiftRegisterConfig) -> None:
        """Initialize shift register.

        Args:
            config: Shift register configuration
        """
        self.config = config
        self.num_outputs = config.num_registers * 8
        self._state: list[bool] = [False] * self.num_outputs

        try:
            # Initialize GPIO pins
            self.data_pin = OutputDevice(config.data_pin)
            self.clock_pin = OutputDevice(config.clock_pin)
            self.latch_pin = OutputDevice(config.latch_pin)

            # Clear all outputs
            self.clear()

            logger.info(
                f"Shift register initialized: {config.num_registers} chips, {self.num_outputs} outputs"
            )
        except Exception as e:
            logger.error(f"Failed to initialize shift register: {e}")
            raise

    def _shift_out(self, bit: bool) -> None:
        """Shift a single bit into the register.

        Args:
            bit: Bit value to shift in
        """
        # Set data pin
        if bit:
            self.data_pin.on()
        else:
            self.data_pin.off()

        # Pulse clock
        self.clock_pin.on()
        self.clock_pin.off()

    def _latch(self) -> None:
        """Latch data to outputs."""
        self.latch_pin.on()
        self.latch_pin.off()

    def update(self) -> None:
        """Update shift register outputs with current state.

        Shifts out all bits and latches them to outputs.
        """
        # Shift out all bits (MSB first, rightmost chip first)
        for i in range(self.num_outputs - 1, -1, -1):
            self._shift_out(self._state[i])

        # Latch to outputs
        self._latch()

    def set_output(self, index: int, value: bool) -> None:
        """Set a single output.

        Args:
            index: Output index (0 to num_outputs-1)
            value: Output state (True=on, False=off)
        """
        if 0 <= index < self.num_outputs:
            self._state[index] = value
        else:
            logger.warning(f"Invalid output index: {index}")

    def set_all(self, values: list[bool]) -> None:
        """Set all outputs at once.

        Args:
            values: List of output states (must match num_outputs)
        """
        if len(values) != self.num_outputs:
            logger.warning(
                f"Value list length ({len(values)}) doesn't match outputs ({self.num_outputs})"
            )
            return
        self._state = values.copy()

    def set_byte(self, register_index: int, value: int) -> None:
        """Set an entire 8-bit register (one chip).

        Args:
            register_index: Register index (0 to num_registers-1)
            value: 8-bit value (0-255)
        """
        if not (0 <= register_index < self.config.num_registers):
            logger.warning(f"Invalid register index: {register_index}")
            return

        # Set 8 bits for this register
        start_bit = register_index * 8
        for i in range(8):
            self._state[start_bit + i] = bool((value >> i) & 1)

    def clear(self) -> None:
        """Clear all outputs (set to off)."""
        self._state = [False] * self.num_outputs
        self.update()

    def test_pattern(self) -> None:
        """Display a test pattern (walking LED)."""
        logger.info("Running shift register test pattern")
        import time

        # Walking LED
        for i in range(self.num_outputs):
            self.clear()
            self.set_output(i, True)
            self.update()
            time.sleep(0.05)

        # All on
        self.set_all([True] * self.num_outputs)
        self.update()
        time.sleep(0.5)

        # All off
        self.clear()

    def close(self) -> None:
        """Clean up shift register resources."""
        try:
            self.clear()
            self.data_pin.close()
            self.clock_pin.close()
            self.latch_pin.close()
        except Exception as e:
            logger.error(f"Error closing shift register: {e}")

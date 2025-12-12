"""MPU-6050 accelerometer/gyroscope for gesture control."""

import logging
import math
from typing import Callable, Optional, Tuple

logger = logging.getLogger(__name__)


class MPU6050:
    """MPU-6050 6-axis accelerometer/gyroscope (GY-521 module).

    Provides tilt, rotation, and shake detection for expressive control.
    """

    def __init__(self, i2c_bus: int = 1, address: int = 0x68):
        """Initialize MPU-6050.

        Args:
            i2c_bus: I2C bus number (1 for Raspberry Pi)
            address: I2C address (0x68 or 0x69)
        """
        self.bus = None
        self.address = address
        self.i2c_bus = i2c_bus

        # Callbacks
        self._on_tilt: Optional[Callable[[float, float], None]] = None
        self._on_shake: Optional[Callable[[], None]] = None

        # Calibration offsets
        self.accel_offset = {"x": 0, "y": 0, "z": 0}
        self.gyro_offset = {"x": 0, "y": 0, "z": 0}

        # Shake detection
        self.shake_threshold = 2.5  # G-force threshold
        self.last_accel_magnitude = 0

        self._initialize()

    def _initialize(self) -> None:
        """Initialize I2C connection and wake up MPU-6050."""
        try:
            import smbus2

            self.bus = smbus2.SMBus(self.i2c_bus)

            # Wake up MPU-6050 (it starts in sleep mode)
            self.bus.write_byte_data(self.address, 0x6B, 0)

            logger.info(f"MPU-6050 initialized on I2C bus {self.i2c_bus}, address 0x{self.address:02X}")

        except Exception as e:
            logger.error(f"Failed to initialize MPU-6050: {e}")
            raise

    def _read_word_2c(self, reg: int) -> int:
        """Read signed 16-bit value from two registers.

        Args:
            reg: Register address

        Returns:
            Signed 16-bit value
        """
        high = self.bus.read_byte_data(self.address, reg)
        low = self.bus.read_byte_data(self.address, reg + 1)
        val = (high << 8) + low

        # Convert to signed
        if val >= 0x8000:
            return -((65535 - val) + 1)
        else:
            return val

    def read_accel_raw(self) -> Tuple[int, int, int]:
        """Read raw accelerometer data.

        Returns:
            Tuple of (x, y, z) raw values
        """
        x = self._read_word_2c(0x3B)
        y = self._read_word_2c(0x3D)
        z = self._read_word_2c(0x3F)
        return (x, y, z)

    def read_gyro_raw(self) -> Tuple[int, int, int]:
        """Read raw gyroscope data.

        Returns:
            Tuple of (x, y, z) raw values
        """
        x = self._read_word_2c(0x43)
        y = self._read_word_2c(0x45)
        z = self._read_word_2c(0x47)
        return (x, y, z)

    def read_accel(self) -> Tuple[float, float, float]:
        """Read accelerometer data in G (gravity units).

        Returns:
            Tuple of (x, y, z) in G
        """
        x, y, z = self.read_accel_raw()

        # Convert to G (±2g range, 16384 LSB/g)
        x_g = (x / 16384.0) - self.accel_offset["x"]
        y_g = (y / 16384.0) - self.accel_offset["y"]
        z_g = (z / 16384.0) - self.accel_offset["z"]

        return (x_g, y_g, z_g)

    def read_gyro(self) -> Tuple[float, float, float]:
        """Read gyroscope data in degrees/second.

        Returns:
            Tuple of (x, y, z) in deg/s
        """
        x, y, z = self.read_gyro_raw()

        # Convert to deg/s (131 LSB/deg/s)
        x_dps = (x / 131.0) - self.gyro_offset["x"]
        y_dps = (y / 131.0) - self.gyro_offset["y"]
        z_dps = (z / 131.0) - self.gyro_offset["z"]

        return (x_dps, y_dps, z_dps)

    def get_tilt(self) -> Tuple[float, float]:
        """Calculate tilt angles (pitch and roll) in degrees.

        Returns:
            Tuple of (pitch, roll) in degrees
        """
        x, y, z = self.read_accel()

        # Calculate pitch (rotation around Y-axis)
        pitch = math.atan2(y, math.sqrt(x**2 + z**2)) * (180.0 / math.pi)

        # Calculate roll (rotation around X-axis)
        roll = math.atan2(-x, z) * (180.0 / math.pi)

        return (pitch, roll)

    def get_tilt_midi(self) -> Tuple[int, int]:
        """Get tilt as MIDI CC values (0-127).

        Returns:
            Tuple of (pitch_cc, roll_cc)
        """
        pitch, roll = self.get_tilt()

        # Map -90 to +90 degrees to 0-127
        pitch_cc = int(((pitch + 90) / 180) * 127)
        roll_cc = int(((roll + 90) / 180) * 127)

        # Clamp to valid range
        pitch_cc = max(0, min(127, pitch_cc))
        roll_cc = max(0, min(127, roll_cc))

        return (pitch_cc, roll_cc)

    def detect_shake(self) -> bool:
        """Detect shake gesture based on acceleration magnitude.

        Returns:
            True if shake detected, False otherwise
        """
        x, y, z = self.read_accel()

        # Calculate total acceleration magnitude
        magnitude = math.sqrt(x**2 + y**2 + z**2)

        # Detect sudden change (shake)
        delta = abs(magnitude - self.last_accel_magnitude)
        self.last_accel_magnitude = magnitude

        is_shake = delta > self.shake_threshold

        if is_shake and self._on_shake:
            self._on_shake()

        return is_shake

    def calibrate(self, samples: int = 100) -> None:
        """Calibrate accelerometer and gyroscope.

        Call this when device is at rest on a flat surface.

        Args:
            samples: Number of samples to average
        """
        logger.info("Calibrating MPU-6050... (keep device still)")

        accel_sum = {"x": 0.0, "y": 0.0, "z": 0.0}
        gyro_sum = {"x": 0.0, "y": 0.0, "z": 0.0}

        for _ in range(samples):
            x, y, z = self.read_accel()
            accel_sum["x"] += x
            accel_sum["y"] += y
            accel_sum["z"] += z - 1.0  # Subtract 1G for gravity

            x, y, z = self.read_gyro()
            gyro_sum["x"] += x
            gyro_sum["y"] += y
            gyro_sum["z"] += z

        # Average
        self.accel_offset = {axis: accel_sum[axis] / samples for axis in ["x", "y", "z"]}
        self.gyro_offset = {axis: gyro_sum[axis] / samples for axis in ["x", "y", "z"]}

        logger.info("Calibration complete")
        logger.debug(f"Accel offset: {self.accel_offset}")
        logger.debug(f"Gyro offset: {self.gyro_offset}")

    def on_tilt(self, callback: Callable[[float, float], None]) -> None:
        """Register callback for tilt changes.

        Args:
            callback: Function(pitch, roll) in degrees
        """
        self._on_tilt = callback

    def on_shake(self, callback: Callable[[], None]) -> None:
        """Register callback for shake detection.

        Args:
            callback: Function with no arguments
        """
        self._on_shake = callback

    def poll(self) -> None:
        """Poll sensor and trigger callbacks.

        Should be called regularly (e.g., 50-100Hz) from main loop.
        """
        # Check for shake
        self.detect_shake()

        # Get tilt
        if self._on_tilt:
            pitch, roll = self.get_tilt()
            self._on_tilt(pitch, roll)

    def close(self) -> None:
        """Clean up I2C resources."""
        if self.bus:
            try:
                self.bus.close()
            except Exception as e:
                logger.error(f"Error closing MPU-6050: {e}")

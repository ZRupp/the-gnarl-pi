"""HC-SR04 ultrasonic distance sensor for Theremin-style control."""

import logging
import time
from typing import Callable, Optional

from gpiozero import DistanceSensor

logger = logging.getLogger(__name__)


class UltrasonicSensor:
    """HC-SR04 ultrasonic distance sensor.

    Measures distance (2cm to 400cm) for gesture control,
    Theremin-style performance, or proximity triggers.
    """

    def __init__(
        self,
        trigger_pin: int,
        echo_pin: int,
        min_distance: float = 2.0,
        max_distance: float = 100.0,
    ):
        """Initialize ultrasonic sensor.

        Args:
            trigger_pin: GPIO pin for trigger
            echo_pin: GPIO pin for echo
            min_distance: Minimum distance in cm
            max_distance: Maximum distance in cm
        """
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.min_distance = min_distance
        self.max_distance = max_distance

        # Callbacks
        self._on_distance_change: Optional[Callable[[float], None]] = None
        self._on_proximity: Optional[Callable[[bool], None]] = None

        # State
        self.last_distance = 0.0
        self.proximity_threshold = 20.0  # cm
        self.in_proximity = False

        try:
            self.sensor = DistanceSensor(echo=echo_pin, trigger=trigger_pin, max_distance=max_distance / 100.0)
            logger.info(
                f"Ultrasonic sensor initialized on pins {trigger_pin}/{echo_pin}, "
                f"range {min_distance}-{max_distance}cm"
            )
        except Exception as e:
            logger.error(f"Failed to initialize ultrasonic sensor: {e}")
            raise

    def read_distance(self) -> float:
        """Read distance in centimeters.

        Returns:
            Distance in cm, or -1 if out of range
        """
        try:
            # DistanceSensor returns distance in meters
            distance_m = self.sensor.distance
            distance_cm = distance_m * 100

            # Clamp to valid range
            if distance_cm < self.min_distance or distance_cm > self.max_distance:
                return -1.0

            return distance_cm

        except Exception as e:
            logger.warning(f"Error reading distance: {e}")
            return -1.0

    def get_midi_value(self) -> int:
        """Get distance as MIDI CC value (0-127).

        Returns:
            MIDI value, or -1 if out of range
        """
        distance = self.read_distance()

        if distance < 0:
            return -1

        # Map distance range to 0-127
        # Closer = higher value (more intuitive for control)
        normalized = (self.max_distance - distance) / (self.max_distance - self.min_distance)
        midi_val = int(normalized * 127)

        # Clamp to valid range
        return max(0, min(127, midi_val))

    def get_note_offset(self, octave_range: int = 2) -> int:
        """Get distance as note offset for pitch control.

        Args:
            octave_range: Range in octaves (1-4)

        Returns:
            Note offset in semitones, or 0 if out of range
        """
        distance = self.read_distance()

        if distance < 0:
            return 0

        # Map to semitone offset
        normalized = (distance - self.min_distance) / (self.max_distance - self.min_distance)
        semitones = int(normalized * 12 * octave_range) - (12 * octave_range // 2)

        return semitones

    def check_proximity(self) -> bool:
        """Check if object is within proximity threshold.

        Returns:
            True if within threshold, False otherwise
        """
        distance = self.read_distance()

        if distance < 0:
            return False

        is_close = distance < self.proximity_threshold

        # Detect proximity state change
        if is_close != self.in_proximity:
            self.in_proximity = is_close
            if self._on_proximity:
                self._on_proximity(is_close)

        return is_close

    def on_distance_change(self, callback: Callable[[float], None]) -> None:
        """Register callback for distance changes.

        Args:
            callback: Function(distance_cm)
        """
        self._on_distance_change = callback

    def on_proximity(self, callback: Callable[[bool], None]) -> None:
        """Register callback for proximity detection.

        Args:
            callback: Function(is_close)
        """
        self._on_proximity = callback

    def poll(self) -> None:
        """Poll sensor and trigger callbacks.

        Should be called regularly (e.g., 20-50Hz) from main loop.
        """
        distance = self.read_distance()

        if distance >= 0:
            # Check for significant change (reduce noise)
            if abs(distance - self.last_distance) > 1.0:  # 1cm threshold
                self.last_distance = distance
                if self._on_distance_change:
                    self._on_distance_change(distance)

        # Check proximity
        self.check_proximity()

    def calibrate_range(self, samples: int = 10) -> None:
        """Calibrate min/max range based on current environment.

        Args:
            samples: Number of samples to collect
        """
        logger.info("Calibrating ultrasonic sensor... (move hand from min to max distance)")

        distances = []
        for _ in range(samples):
            dist = self.read_distance()
            if dist > 0:
                distances.append(dist)
            time.sleep(0.2)

        if distances:
            self.min_distance = min(distances)
            self.max_distance = max(distances)
            logger.info(f"Calibrated range: {self.min_distance:.1f} - {self.max_distance:.1f} cm")
        else:
            logger.warning("Calibration failed: no valid readings")

    def close(self) -> None:
        """Clean up sensor resources."""
        try:
            self.sensor.close()
        except Exception as e:
            logger.error(f"Error closing ultrasonic sensor: {e}")

"""Main controller that coordinates hardware and synth."""

import logging
from typing import Optional

from gnarl.config import GnarlConfig
from gnarl.hardware import AnalogJoystick, LCDDisplay, RotaryEncoder, ShiftRegister, Switch
from gnarl.synth import SynthInterface

logger = logging.getLogger(__name__)


class GnarlController:
    """Main controller for The Gnarl Pi."""

    def __init__(self, config: GnarlConfig) -> None:
        """Initialize controller.

        Args:
            config: Complete configuration
        """
        self.config = config
        self.current_preset = 0
        self.octave_offset = 0

        # Initialize hardware
        self.lcd: Optional[LCDDisplay] = None
        self.encoders: list[RotaryEncoder] = []
        self.switches: list[Switch] = []
        self.joystick: Optional[AnalogJoystick] = None
        self.shift_register: Optional[ShiftRegister] = None

        # Initialize synth interface
        self.synth: Optional[SynthInterface] = None

        logger.info("Initializing Gnarl Pi controller...")

    def start(self) -> None:
        """Start the controller and initialize all components."""
        try:
            # Initialize synth first
            logger.info("Initializing synth interface...")
            self.synth = SynthInterface(self.config.synth)

            # Initialize LCD
            if self.config.hardware.lcd:
                logger.info("Initializing LCD...")
                self.lcd = LCDDisplay(self.config.hardware.lcd)
                self._update_display()

            # Initialize encoders
            logger.info(f"Initializing {len(self.config.hardware.encoders)} encoders...")
            for enc_config in self.config.hardware.encoders:
                encoder = RotaryEncoder(enc_config)
                encoder.on_change(lambda val, cfg=enc_config: self._handle_encoder_change(cfg, val))
                if enc_config.sw_pin is not None:
                    encoder.on_press(lambda cfg=enc_config: self._handle_encoder_press(cfg))
                self.encoders.append(encoder)

            # Initialize switches
            logger.info(f"Initializing {len(self.config.hardware.switches)} switches...")
            for sw_config in self.config.hardware.switches:
                switch = Switch(sw_config)
                switch.on_press(lambda cfg=sw_config: self._handle_switch_press(cfg))
                self.switches.append(switch)

            # Initialize joystick
            if self.config.hardware.joystick:
                logger.info("Initializing joystick...")
                self.joystick = AnalogJoystick(self.config.hardware.joystick)
                self.joystick.calibrate()  # Calibrate at startup
                self.joystick.on_press(self._handle_joystick_press)

            # Initialize shift registers
            if self.config.hardware.shift_registers:
                logger.info("Initializing shift registers...")
                self.shift_register = ShiftRegister(self.config.hardware.shift_registers)
                self._update_leds()

            logger.info("Gnarl Pi controller started successfully!")

        except Exception as e:
            logger.error(f"Failed to start controller: {e}")
            self.stop()
            raise

    def stop(self) -> None:
        """Stop the controller and clean up resources."""
        logger.info("Stopping Gnarl Pi controller...")

        if self.synth:
            self.synth.all_notes_off()
            self.synth.close()

        if self.lcd:
            self.lcd.clear()
            self.lcd.close()

        for encoder in self.encoders:
            encoder.close()

        for switch in self.switches:
            switch.close()

        if self.joystick:
            self.joystick.close()

        if self.shift_register:
            self.shift_register.clear()
            self.shift_register.close()

        logger.info("Controller stopped")

    def update(self) -> None:
        """Update controller state (called from main loop).

        Handles joystick polling and other periodic tasks.
        """
        # Poll joystick if configured
        if self.joystick and self.synth:
            x, y = self.joystick.read()
            # Send as MIDI CC
            self.synth.send_cc(self.config.hardware.joystick.x_midi_cc, x)
            self.synth.send_cc(self.config.hardware.joystick.y_midi_cc, y)

    def _handle_encoder_change(self, config: any, value: int) -> None:
        """Handle encoder value change.

        Args:
            config: Encoder configuration
            value: New encoder value
        """
        logger.debug(f"Encoder '{config.name}' changed to {value}")

        # Update display
        if self.lcd:
            self.lcd.display_preset(
                self._get_current_preset_name(),
                config.name,
                str(value)
            )

        # Send MIDI CC if configured
        if config.midi_cc is not None and self.synth:
            self.synth.send_cc(config.midi_cc, value)

    def _handle_encoder_press(self, config: any) -> None:
        """Handle encoder button press.

        Args:
            config: Encoder configuration
        """
        logger.debug(f"Encoder '{config.name}' button pressed")
        # Could be used for parameter page switching, etc.

    def _handle_switch_press(self, config: any) -> None:
        """Handle switch press.

        Args:
            config: Switch configuration
        """
        logger.debug(f"Switch '{config.name}' pressed")

        if config.action == "load_preset" and config.preset is not None:
            self._load_preset(config.preset)
        elif config.action == "octave_shift" and config.value is not None:
            self.octave_offset += config.value
            logger.info(f"Octave offset: {self.octave_offset}")
            self._update_display()
        elif config.action == "toggle_effect":
            # Send MIDI CC for effect toggle
            if config.midi_cc is not None and self.synth:
                self.synth.send_cc(config.midi_cc, 127)

    def _handle_joystick_press(self) -> None:
        """Handle joystick button press."""
        logger.debug("Joystick button pressed")
        # Could be used for sustain, etc.
        if self.synth:
            self.synth.send_cc(64, 127)  # Sustain on

    def _load_preset(self, index: int) -> None:
        """Load a preset.

        Args:
            index: Preset index
        """
        if 0 <= index < len(self.config.presets):
            self.current_preset = index
            preset = self.config.presets[index]
            logger.info(f"Loading preset {index}: {preset.name}")

            # Send program change
            if self.synth:
                self.synth.send_program_change(index)

            self._update_display()
            self._update_leds()
        else:
            logger.warning(f"Invalid preset index: {index}")

    def _get_current_preset_name(self) -> str:
        """Get current preset name.

        Returns:
            Preset name or "No Preset"
        """
        if 0 <= self.current_preset < len(self.config.presets):
            return self.config.presets[self.current_preset].name
        return "No Preset"

    def _update_display(self) -> None:
        """Update LCD display with current state."""
        if self.lcd:
            preset_name = self._get_current_preset_name()
            octave_info = f"Oct:{self.octave_offset:+d}" if self.octave_offset != 0 else ""
            self.lcd.display_preset(preset_name, octave_info)

    def _update_leds(self) -> None:
        """Update LED indicators."""
        if self.shift_register:
            # Light up LED corresponding to current preset
            num_leds = min(len(self.config.presets), self.shift_register.num_outputs)
            leds = [False] * self.shift_register.num_outputs
            if 0 <= self.current_preset < num_leds:
                leds[self.current_preset] = True
            self.shift_register.set_all(leds)
            self.shift_register.update()

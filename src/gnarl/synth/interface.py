"""Synth engine interface for MIDI control."""

import logging
from typing import Optional

import rtmidi

from gnarl.config import SynthConfig

logger = logging.getLogger(__name__)


class SynthInterface:
    """Interface to synth engine via MIDI."""

    def __init__(self, config: SynthConfig) -> None:
        """Initialize synth interface.

        Args:
            config: Synth configuration
        """
        self.config = config
        self.midi_out: Optional[rtmidi.MidiOut] = None
        self._initialize_midi()

    def _initialize_midi(self) -> None:
        """Initialize MIDI output."""
        try:
            self.midi_out = rtmidi.MidiOut()

            # Try to find the synth's MIDI port
            available_ports = self.midi_out.get_ports()
            logger.info(f"Available MIDI ports: {available_ports}")

            # Look for the configured JACK client
            port_index = None
            for i, port_name in enumerate(available_ports):
                if self.config.jack_client_name.lower() in port_name.lower():
                    port_index = i
                    break

            if port_index is not None:
                self.midi_out.open_port(port_index)
                logger.info(f"Connected to MIDI port: {available_ports[port_index]}")
            else:
                # Create a virtual port if synth port not found
                self.midi_out.open_virtual_port("GnarlPi")
                logger.warning(
                    f"Synth port '{self.config.jack_client_name}' not found, "
                    "created virtual port 'GnarlPi'"
                )

        except Exception as e:
            logger.error(f"Failed to initialize MIDI: {e}")
            raise

    def send_cc(self, controller: int, value: int, channel: Optional[int] = None) -> None:
        """Send MIDI Control Change message.

        Args:
            controller: CC number (0-127)
            value: CC value (0-127)
            channel: MIDI channel (0-15), uses config default if None
        """
        if self.midi_out is None:
            logger.warning("MIDI not initialized")
            return

        if channel is None:
            channel = self.config.midi_channel

        # MIDI CC: [0xB0 + channel, controller, value]
        message = [0xB0 + channel, controller, value]
        self.midi_out.send_message(message)
        logger.debug(f"MIDI CC: ch={channel} cc={controller} val={value}")

    def send_note_on(
        self, note: int, velocity: int = 100, channel: Optional[int] = None
    ) -> None:
        """Send MIDI Note On message.

        Args:
            note: MIDI note number (0-127)
            velocity: Note velocity (0-127)
            channel: MIDI channel (0-15), uses config default if None
        """
        if self.midi_out is None:
            logger.warning("MIDI not initialized")
            return

        if channel is None:
            channel = self.config.midi_channel

        # MIDI Note On: [0x90 + channel, note, velocity]
        message = [0x90 + channel, note, velocity]
        self.midi_out.send_message(message)
        logger.debug(f"MIDI Note On: ch={channel} note={note} vel={velocity}")

    def send_note_off(self, note: int, channel: Optional[int] = None) -> None:
        """Send MIDI Note Off message.

        Args:
            note: MIDI note number (0-127)
            channel: MIDI channel (0-15), uses config default if None
        """
        if self.midi_out is None:
            logger.warning("MIDI not initialized")
            return

        if channel is None:
            channel = self.config.midi_channel

        # MIDI Note Off: [0x80 + channel, note, 0]
        message = [0x80 + channel, note, 0]
        self.midi_out.send_message(message)
        logger.debug(f"MIDI Note Off: ch={channel} note={note}")

    def send_program_change(self, program: int, channel: Optional[int] = None) -> None:
        """Send MIDI Program Change message.

        Args:
            program: Program number (0-127)
            channel: MIDI channel (0-15), uses config default if None
        """
        if self.midi_out is None:
            logger.warning("MIDI not initialized")
            return

        if channel is None:
            channel = self.config.midi_channel

        # MIDI Program Change: [0xC0 + channel, program]
        message = [0xC0 + channel, program]
        self.midi_out.send_message(message)
        logger.debug(f"MIDI Program Change: ch={channel} prog={program}")

    def send_pitch_bend(self, value: int, channel: Optional[int] = None) -> None:
        """Send MIDI Pitch Bend message.

        Args:
            value: Pitch bend value (0-16383, 8192=center)
            channel: MIDI channel (0-15), uses config default if None
        """
        if self.midi_out is None:
            logger.warning("MIDI not initialized")
            return

        if channel is None:
            channel = self.config.midi_channel

        # MIDI Pitch Bend: [0xE0 + channel, LSB, MSB]
        lsb = value & 0x7F
        msb = (value >> 7) & 0x7F
        message = [0xE0 + channel, lsb, msb]
        self.midi_out.send_message(message)
        logger.debug(f"MIDI Pitch Bend: ch={channel} val={value}")

    def all_notes_off(self, channel: Optional[int] = None) -> None:
        """Send All Notes Off CC message.

        Args:
            channel: MIDI channel (0-15), uses config default if None
        """
        self.send_cc(123, 0, channel)  # CC 123 = All Notes Off

    def close(self) -> None:
        """Clean up MIDI resources."""
        if self.midi_out is not None:
            try:
                self.all_notes_off()
                del self.midi_out
            except Exception as e:
                logger.error(f"Error closing MIDI: {e}")

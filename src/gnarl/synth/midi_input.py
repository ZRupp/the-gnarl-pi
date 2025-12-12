"""MIDI input handler for external keyboards and controllers."""

import logging
from typing import Callable, Optional

import rtmidi

logger = logging.getLogger(__name__)


class MIDIInputHandler:
    """Handle MIDI input from external keyboards/controllers."""

    def __init__(self, port_name: Optional[str] = None) -> None:
        """Initialize MIDI input.

        Args:
            port_name: Specific MIDI port name to connect to, or None for first available
        """
        self.midi_in: Optional[rtmidi.MidiIn] = None
        self.port_name = port_name

        # Callbacks
        self._on_note_on: Optional[Callable[[int, int], None]] = None
        self._on_note_off: Optional[Callable[[int], None]] = None
        self._on_cc: Optional[Callable[[int, int], None]] = None
        self._on_pitch_bend: Optional[Callable[[int], None]] = None
        self._on_program_change: Optional[Callable[[int], None]] = None

        self._initialize()

    def _initialize(self) -> None:
        """Initialize MIDI input port."""
        try:
            self.midi_in = rtmidi.MidiIn()
            available_ports = self.midi_in.get_ports()

            if not available_ports:
                logger.warning("No MIDI input ports available")
                return

            logger.info(f"Available MIDI input ports: {available_ports}")

            # Find port by name or use first available
            port_index = 0
            if self.port_name:
                for i, port in enumerate(available_ports):
                    if self.port_name.lower() in port.lower():
                        port_index = i
                        break

            self.midi_in.open_port(port_index)
            self.midi_in.set_callback(self._handle_midi_message)
            logger.info(f"MIDI input connected to: {available_ports[port_index]}")

        except Exception as e:
            logger.error(f"Failed to initialize MIDI input: {e}")
            raise

    def _handle_midi_message(self, event: tuple, data: Optional[any] = None) -> None:
        """Process incoming MIDI message.

        Args:
            event: MIDI event tuple (message, deltatime)
            data: Additional data (unused)
        """
        message, deltatime = event

        if len(message) < 2:
            return

        status = message[0] & 0xF0
        channel = message[0] & 0x0F

        # Note On
        if status == 0x90 and message[2] > 0:  # velocity > 0
            note = message[1]
            velocity = message[2]
            logger.debug(f"MIDI Note On: note={note} vel={velocity} ch={channel}")
            if self._on_note_on:
                self._on_note_on(note, velocity)

        # Note Off (or Note On with velocity 0)
        elif status == 0x80 or (status == 0x90 and message[2] == 0):
            note = message[1]
            logger.debug(f"MIDI Note Off: note={note} ch={channel}")
            if self._on_note_off:
                self._on_note_off(note)

        # Control Change
        elif status == 0xB0:
            controller = message[1]
            value = message[2]
            logger.debug(f"MIDI CC: cc={controller} val={value} ch={channel}")
            if self._on_cc:
                self._on_cc(controller, value)

        # Pitch Bend
        elif status == 0xE0 and len(message) >= 3:
            lsb = message[1]
            msb = message[2]
            value = (msb << 7) | lsb  # 0-16383
            logger.debug(f"MIDI Pitch Bend: {value} ch={channel}")
            if self._on_pitch_bend:
                self._on_pitch_bend(value)

        # Program Change
        elif status == 0xC0:
            program = message[1]
            logger.debug(f"MIDI Program Change: {program} ch={channel}")
            if self._on_program_change:
                self._on_program_change(program)

    def on_note_on(self, callback: Callable[[int, int], None]) -> None:
        """Register callback for Note On events.

        Args:
            callback: Function(note, velocity)
        """
        self._on_note_on = callback

    def on_note_off(self, callback: Callable[[int], None]) -> None:
        """Register callback for Note Off events.

        Args:
            callback: Function(note)
        """
        self._on_note_off = callback

    def on_cc(self, callback: Callable[[int, int], None]) -> None:
        """Register callback for Control Change events.

        Args:
            callback: Function(controller, value)
        """
        self._on_cc = callback

    def on_pitch_bend(self, callback: Callable[[int], None]) -> None:
        """Register callback for Pitch Bend events.

        Args:
            callback: Function(value)
        """
        self._on_pitch_bend = callback

    def on_program_change(self, callback: Callable[[int], None]) -> None:
        """Register callback for Program Change events.

        Args:
            callback: Function(program)
        """
        self._on_program_change = callback

    @staticmethod
    def list_ports() -> list[str]:
        """List all available MIDI input ports.

        Returns:
            List of port names
        """
        midi_in = rtmidi.MidiIn()
        ports = midi_in.get_ports()
        del midi_in
        return ports

    def close(self) -> None:
        """Clean up MIDI input resources."""
        if self.midi_in is not None:
            try:
                self.midi_in.close_port()
                del self.midi_in
            except Exception as e:
                logger.error(f"Error closing MIDI input: {e}")

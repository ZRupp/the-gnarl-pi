# The Gnarl Pi

A Raspberry Pi-based hardware synthesizer designed for grungy, dirty, and aggressive sounds. Built with custom GPIO hardware including rotary encoders, switches, analog joystick, and LCD display.

## Features

- **Hardware Synthesizer**: Standalone instrument powered by ZynAddSubFX/Yoshimi
- **Custom Hardware Interface**: Rotary encoders, switches, and analog joystick control
- **1602A LCD Display**: Real-time parameter feedback and menu navigation
- **Low Latency Audio**: JACK-optimized for <15ms latency on Raspberry Pi 3
- **Grungy Sound Design**: Optimized for dirty, aggressive, lo-fi synthesis
- **LED Feedback**: SN74HC595 shift register control for visual feedback
- **WiFi Connectivity**: Patch management and MIDI over network (Pi Zero W / Pi 3)

## Hardware Requirements

### Required Components

- **Raspberry Pi 3** (recommended) or **Pi Zero W** (limited polyphony)
- **1602A LCD Display** (16x2 character, I2C or parallel)
- **Rotary Encoders** (as many as you want - typically 3-6)
- **Switches/Buttons** (for preset selection, octave shift, etc.)
- **B103 Joystick** (dual-axis analog with push button)
- **MCP3008 ADC** (for reading analog joystick - 8-channel SPI)
- **SN74HC595 Shift Registers** (3x for LED output control)
- **Resistors** (10kΩ pull-ups for encoders/switches)
- **USB DAC or I2S DAC** (Pi's built-in audio is poor quality)
- **Breadboard or custom PCB**

### Optional Components

- LEDs for visual feedback (controlled via shift registers)
- Power supply (5V 2.5A minimum for Pi 3)
- Enclosure (3D printed or custom fabricated)

## Quick Start

### 1. Hardware Assembly

See [docs/HARDWARE.md](docs/HARDWARE.md) for complete wiring diagrams.

**Basic connections:**
- Encoders: 2 GPIO pins per encoder (CLK, DT) + optional switch (SW)
- Switches: 1 GPIO pin each + ground (with pull-up resistors)
- LCD: I2C (SDA, SCL) or parallel (6-8 pins)
- Joystick: MCP3008 ADC via SPI (CH0=X-axis, CH1=Y-axis) + GPIO for button
- Shift registers: 3 GPIO pins (data, clock, latch) for all 3 chips

### 2. Software Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/the-gnarl-pi.git
cd the-gnarl-pi

# Run installation script (installs dependencies, sets up audio)
sudo ./install.sh

# Configure hardware pins
sudo nano /etc/gnarl/config.yaml
```

### 3. Audio Setup

The installer configures JACK for low-latency audio, but you may need to:

```bash
# Test audio output
speaker-test -c2 -twav

# Start JACK server manually (if needed)
jackd -dalsa -dhw:1 -r48000 -p128 -n2

# Connect synth to audio output
jack_connect ZynAddSubFX:out_1 system:playback_1
jack_connect ZynAddSubFX:out_2 system:playback_2
```

### 4. Run The Gnarl Pi

```bash
# Start the synth
gnarl run

# With verbose logging
gnarl run --verbose

# Test hardware only (no synth)
gnarl test-hardware
```

## Configuration

Edit `/etc/gnarl/config.yaml`:

```yaml
hardware:
  # LCD display (I2C)
  lcd:
    type: "i2c"
    address: 0x27
    cols: 16
    rows: 2

  # Rotary encoders
  encoders:
    - name: "filter_cutoff"
      clk_pin: 17
      dt_pin: 18
      sw_pin: 27  # optional push button
      min_value: 0
      max_value: 127
      default: 64

    - name: "resonance"
      clk_pin: 22
      dt_pin: 23
      min_value: 0
      max_value: 127
      default: 32

  # Switches
  switches:
    - name: "preset_1"
      pin: 5
      action: "load_preset"
      preset: 0

    - name: "octave_down"
      pin: 6
      action: "octave_shift"
      value: -1

  # Analog joystick (via MCP3008)
  joystick:
    spi_device: 0
    spi_channel: 0
    x_channel: 0  # MCP3008 channel for X-axis
    y_channel: 1  # MCP3008 channel for Y-axis
    sw_pin: 24    # Push button pin
    x_midi_cc: 1  # Modulation wheel
    y_midi_cc: 2  # Breath controller

  # LED shift registers (SN74HC595)
  shift_registers:
    data_pin: 10
    clock_pin: 11
    latch_pin: 9
    num_registers: 3

synth:
  engine: "zyn"  # or "yoshimi", "fluidsynth"
  jack_client_name: "ZynAddSubFX"

  # Audio settings
  sample_rate: 48000
  buffer_size: 128

  # MIDI settings
  midi_channel: 0
  polyphony: 8

presets:
  - name: "Dirty Lead"
    file: "/home/pi/.local/share/zynaddsubfx/banks/GnarlyBank/001.xiz"

  - name: "Grungy Bass"
    file: "/home/pi/.local/share/zynaddsubfx/banks/GnarlyBank/002.xiz"
```

## Usage

### Hardware Controls

**Encoders:**
- Rotate to change parameter values
- Push to toggle parameter assignment or enter/exit menus

**Switches:**
- Load presets
- Shift octaves
- Toggle effects
- Access different parameter pages

**Joystick:**
- X-axis: Modulation (vibrato, filter sweep, etc.)
- Y-axis: Expression (volume, brightness, etc.)
- Push: Momentary effect (sustain, pitch bend hold, etc.)

**LCD Display:**
- Line 1: Current preset/patch name
- Line 2: Active parameter and value

### Software Interface

```bash
# Run the synth
gnarl run

# List available presets
gnarl list-presets

# Test individual hardware components
gnarl test-encoder 0    # Test first encoder
gnarl test-switch 2     # Test third switch
gnarl test-joystick     # Test joystick axes
gnarl test-lcd          # Display test pattern

# MIDI utilities
gnarl list-midi         # Show MIDI ports
gnarl send-cc 1 64      # Send CC#1 value 64
```

## Creating Grungy Sounds

The Gnarl Pi is optimized for dirty, aggressive synthesis. Here are some tips:

### ZynAddSubFX Patches

1. **Aggressive Filters**: Use low-pass filters with high resonance
2. **Distortion**: Enable distortion on the output
3. **Detuning**: Add slight detuning between oscillators
4. **Bit Reduction**: Lower bit depth for lo-fi crunch
5. **Ring Modulation**: Creates metallic, clangorous tones

### Recommended Effects Chain

```
Oscillator → Filter (high resonance) → Distortion → Bit Crusher → Chorus → Output
```

### Example Parameter Mappings

- **Encoder 1**: Filter cutoff (0-127)
- **Encoder 2**: Filter resonance (0-127)
- **Encoder 3**: Distortion amount (0-127)
- **Joystick X**: Filter cutoff modulation
- **Joystick Y**: Bit depth reduction

See [docs/SOUND_DESIGN.md](docs/SOUND_DESIGN.md) for detailed synthesis techniques.

## Architecture

```
┌─────────────────────────────────────────────┐
│           Python UI/Control Layer           │
│  - GPIO input handling (gpiozero)           │
│  - LCD display updates (RPLCD/smbus)        │
│  - Menu system and state management         │
│  - Hardware abstraction                     │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│           JACK Audio Server (C++)           │
│  - Low-latency audio routing                │
│  - Real-time priority scheduling            │
│  - <15ms latency on Pi 3                    │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│        Synth Engine (ZynAddSubFX)           │
│  - Subtractive/FM/Additive synthesis        │
│  - Real-time audio processing (C++)         │
│  - MIDI input, OSC control                  │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
         USB/I2S DAC → Audio Output
```

## Performance

**Raspberry Pi 3:**
- Audio latency: ~10-15ms
- Polyphony: 8-16 voices (depending on patch complexity)
- CPU usage: 30-60% (one core for audio)
- Boot time: ~30 seconds to ready

**Raspberry Pi Zero W:**
- Audio latency: ~15-20ms
- Polyphony: 4-6 voices
- CPU usage: 60-90%
- Boot time: ~45 seconds to ready

## Troubleshooting

### Audio Issues

**No sound:**
```bash
# Check JACK is running
ps aux | grep jack

# Check audio device
aplay -l

# Test audio
speaker-test -c2
```

**Crackling/pops (xruns):**
```bash
# Increase buffer size in config
buffer_size: 256  # or 512

# Check CPU governor
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
# Should be "performance"
```

### Hardware Issues

**Encoder not responding:**
```bash
# Test encoder directly
gnarl test-encoder 0

# Check wiring and pull-up resistors
```

**LCD not displaying:**
```bash
# For I2C LCD, check address
i2cdetect -y 1

# Test LCD
gnarl test-lcd
```

**Joystick readings unstable:**
```bash
# Test ADC readings
gnarl test-joystick

# May need calibration or smoothing in config
```

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for:
- Code architecture
- Adding new hardware components
- Creating custom synth engines
- Testing and debugging

## Related Projects

- [numpad2midi](https://github.com/ZRupp/numpad2midi) - USB numpad to MIDI converter (sibling project)
- [Zynthian](https://zynthian.org/) - Full-featured Pi synth platform
- [mt32-pi](https://github.com/dwhinham/mt32-pi) - MT-32 emulation on Pi Zero
- [PiSound](https://blokas.io/pisound/) - High-quality audio interface for Pi

## License

MIT License - see [LICENSE](LICENSE) for details

## Contributing

Contributions welcome! Please open issues or pull requests.

Areas for contribution:
- Additional synth engine support (Pure Data, Yoshimi, etc.)
- Hardware designs and PCB layouts
- Preset banks for grungy sounds
- 3D-printable enclosures
- Documentation improvements

## Credits

Created for musicians who want tactile, grungy synthesis without a computer.

---

**Make it dirty. Make it gnarl. 🎛️🔊**

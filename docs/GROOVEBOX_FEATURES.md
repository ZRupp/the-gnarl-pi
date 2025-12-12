# Groovebox Features - The Gnarl Pi

Complete guide to the new groovebox features added to The Gnarl Pi.

## Overview

The Gnarl Pi has been upgraded from a simple parameter controller to a **full-featured groovebox** with:

- ✅ MIDI Input (play from external keyboard)
- ✅ 16-Step Sequencer (Pocket Operator style)
- ✅ Button Matrix (16 buttons for sequencer/keyboard)
- ✅ LED Bar Graphs (visual parameter feedback)
- ✅ 7-Segment Displays (numeric values)
- ✅ 8x8 LED Matrix (waveforms, patterns, sequencer visualization)
- ✅ Accelerometer/Gyro (tilt and gesture control)
- ✅ Ultrasonic Sensor (distance-based Theremin control)

---

## MIDI Input

### Features

- **Play from external MIDI keyboard** while controlling parameters
- **Merge internal + external MIDI** (buttons, sequencer, keyboard)
- **Full MIDI message support**: Note On/Off, CC, Program Change, Pitch Bend

### Configuration

```yaml
midi:
  input:
    enabled: true
    port_name: null  # Auto-detect first MIDI keyboard
    merge_with_internal: true
```

### Use Cases

1. **Desktop Synth Module**: Play from MIDI keyboard, adjust with encoders/joystick
2. **MIDI Processor**: External keyboard → Gnarl Pi effects → synth
3. **Hybrid Performance**: Keyboard for notes, sequencer for rhythm, hardware for tweaking

---

## 16-Step Sequencer

### Features

- **Pocket Operator-style workflow**
- Adjustable BPM (20-300)
- Per-step parameters (note, velocity, length, probability)
- Record/playback modes
- Pattern storage

### Controls

**Via Button Matrix (16-button mode):**
- Press button to toggle step on/off
- Encoders adjust step parameters
- Switches control play/stop, record, pattern select

**Pattern Display:**
- 8x8 LED matrix shows current step position
- LED bars show step velocity/length
- 7-segment shows BPM

### Usage

```python
# In code
sequencer.set_bpm(130)
sequencer.toggle_step(0)  # First step
sequencer.toggle_step(4)  # Fifth step
sequencer.start()

# Via YAML
sequencer:
  enabled: true
  num_steps: 16
  bpm: 120
  auto_start: false
```

---

## Button Matrix

### Modes

The 16-button matrix supports multiple modes:

#### 1. **Sequencer Mode** (Default)
```
[1][2][3][4][5][6][7][8]       ← Steps 1-8
[9][10][11][12][13][14][15][16] ← Steps 9-16
```
- Press to toggle steps on/off
- LED matrix shows active steps

#### 2. **Keyboard Mode**
```
[C#][D#]   [F#][G#][A#]     ← Sharps
[C][D][E][F][G][A][B][C]    ← Naturals
```
- Play chromatic scale (1 octave)
- Octave shift with switches

#### 3. **Chord Mode**
```
[Maj][min][7th][m7] [sus4][aug][dim][9th]
[I]  [ii] [iii][IV] [V]  [vi] [vii][...]
```
- Trigger preset chords
- Great for quick composition

#### 4. **Preset Mode**
```
[P1][P2][P3][P4] [P5][P6][P7][P8]
[P9][10][11][12] [13][14][15][16]
```
- Quick preset selection
- One button per preset

### Hardware

**4x4 Matrix = 8 GPIO Pins:**
```yaml
button_matrix:
  row_pins: [7, 8, 9, 10]
  col_pins: [11, 0, 1, 2]
  mode: "sequencer"
```

---

## LED Bar Graphs

### Features

- **10-segment bar graphs** for visual parameter feedback
- Real-time display of encoder positions
- VU meter mode for audio levels
- Driven by existing shift registers

### Display Modes

**Parameter Visualization:**
```
Filter Cutoff:  [████████░░]  80/127
Resonance:      [███░░░░░░░]  30/127
Distortion:     [██████░░░░]  60/127
```

**VU Meter:**
```
Audio Level:    [█████▌░░░░]  Peak hold
```

### Configuration

```yaml
led_bars:
  - name: "cutoff_bar"
    num_segments: 10
    start_output: 0  # Shift register outputs 0-9

  - name: "resonance_bar"
    num_segments: 10
    start_output: 10
```

---

## 7-Segment Displays

### Features

- **4-digit display** (HS410361k-32) for parameter values
- **Single-digit display** (A5161BS) for octave/page

### Display Modes

**Parameter Values:**
```
[0064]  ← Cutoff value
[P.03]  ← Preset number
[120b]  ← BPM
```

**Octave Indicator (single digit):**
```
[+2]  ← Up 2 octaves
[-1]  ← Down 1 octave
```

### Configuration

```yaml
seven_segment:
  num_digits: 4
  common_anode: false

single_digit:
  start_output: 24
```

---

## 8x8 LED Matrix

### Features

- **Waveform visualization** (sine, saw, square, triangle)
- **Sequencer step display**
- **Spectrum analyzer** (8 frequency bands)
- **Icons and patterns**

### Display Modes

**Waveform:**
```
▓░▓░░▓▓░  ← Sawtooth wave
░▓░▓▓░▓░
▓░░░▓░░▓
░░▓░░░▓░
```

**Sequencer:**
```
█ ░ █ ░ █ ░ ░ ░  ← Active steps
▲                 ← Current position
```

**Icons:**
- Skull (heavy distortion)
- Note (clean sound)
- Play/pause symbols

### Configuration

```yaml
led_matrix:
  use_max7219: false  # Using shift registers
```

---

## Accelerometer/Gyroscope (GY-521/MPU-6050)

### Features

- **6-axis motion sensing** (accelerometer + gyroscope)
- **Tilt control** (pitch and roll)
- **Shake detection**
- **Gesture recognition**

### Control Mappings

**Tilt Forward/Back (Pitch):**
- Maps to filter cutoff, vibrato, or custom CC
- -90° to +90° → MIDI 0-127

**Tilt Left/Right (Roll):**
- Maps to resonance, pan, or custom CC
- -90° to +90° → MIDI 0-127

**Shake Gesture:**
- Toggle distortion on/off
- Trigger effect bypass
- Pattern change

### Configuration

```yaml
accelerometer:
  i2c_bus: 1
  address: 0x68  # Default MPU-6050 address
  pitch_midi_cc: 75  # Vibrato depth
  roll_midi_cc: 76   # Brightness
  shake_threshold: 2.5
```

### Performance Tips

- Calibrate on startup (flat surface)
- Tilt synth for expressive sweeps
- Shake for dramatic effect changes
- Combine with joystick for multi-axis control

---

## Ultrasonic Distance Sensor (HC-SR04)

### Features

- **Theremin-style control** (2cm to 400cm range)
- **Hands-free parameter sweeps**
- **Proximity detection**

### Control Modes

**Distance → MIDI CC:**
```
Hand Position:   [----✋--------]
Distance:        20cm
MIDI Value:      87/127
Parameter:       Filter cutoff
```

**Distance → Pitch:**
```
Closer  = Higher pitch
Farther = Lower pitch
Range: ±2 octaves
```

**Proximity Trigger:**
```
< 20cm: Effect ON
> 20cm: Effect OFF
```

### Configuration

```yaml
ultrasonic:
  trigger_pin: 3
  echo_pin: 4
  min_distance: 5.0    # cm
  max_distance: 80.0   # cm
  midi_cc: 77  # Controlled parameter
```

### Performance Tips

- Mount sensor pointing up/forward
- Wave hand over sensor for sweeps
- Works great for filter cutoff or pitch
- Combine with accelerometer for 3D control!

---

## Visual Feedback System

### Complete Display Setup

```
┌────────────────────────────────────────────────┐
│  LCD: "Dirty Lead"      7-Seg: [0064]         │
│       "Cutoff: 64"      Octave: [+1]          │
│                                                │
│  Cutoff:    [████████░░]  ← LED Bar 1         │
│  Resonance: [███░░░░░░░]  ← LED Bar 2         │
│  Level:     [██░░]        ← LED Bar 3         │
│                                                │
│  8x8 Matrix:                                   │
│  ▓░▓░░▓▓░  ← Sequencer step visualization     │
│  ░▓░▓▓░▓░                                      │
│  █ ░ █ ░   ← Active steps                     │
│  ▲         ← Current position                 │
└────────────────────────────────────────────────┘
```

---

## Complete Hardware Setup

### GPIO Pin Usage (Total: ~35-40 pins needed)

**I2C Devices (2 pins shared):**
- LCD (1602A): SDA, SCL
- Accelerometer (GY-521): SDA, SCL (shared)

**SPI Device (4 pins):**
- MCP3008 ADC: MOSI, MISO, SCLK, CS

**Encoders (9 pins):**
- 3× Encoders: CLK, DT, SW each

**Switches (6 pins):**
- 6× Switches: 1 pin each

**Button Matrix (8 pins):**
- 4× Row + 4× Column

**Shift Registers (3 pins):**
- Data, Clock, Latch (controls 24 LEDs)

**Other:**
- Joystick button: 1 pin
- Ultrasonic: 2 pins (Trig, Echo)

**Total: ~35 pins** (Pi has 28 GPIO, so need to prioritize or multiplex)

### Optimization Strategies

1. **Use shift registers** for all LED outputs
2. **Share I2C** for LCD + accelerometer
3. **Matrix scan** for buttons (16 buttons = 8 pins)
4. **Reduce switches** if needed (keep most essential)

---

## Use Cases

### 1. **Standalone Groovebox**
- Program sequences with buttons
- Play from internal sequencer
- Adjust parameters in real-time
- No computer needed

### 2. **Desktop Synth Module**
- MIDI keyboard for note input
- Hardware controls for parameters
- Motion sensors for expression
- Visual feedback via displays

### 3. **Live Performance Instrument**
- Sequencer for rhythm
- MIDI keyboard for leads
- Tilt/shake for dramatic effects
- Distance sensor for filter sweeps

### 4. **Experimental Controller**
- Multi-axis gesture control
- Distance-based Theremin
- Accelerometer expression
- Pattern-based composition

---

## Getting Started

### 1. Hardware Assembly

Follow [docs/HARDWARE.md](HARDWARE.md) for wiring all components.

### 2. Configuration

Use the groovebox config:
```bash
sudo cp config/groovebox.yaml /etc/gnarl/config.yaml
```

### 3. Calibration

```bash
# Calibrate accelerometer
gnarl calibrate-accel

# Calibrate ultrasonic range
gnarl calibrate-ultrasonic
```

### 4. Test

```bash
# Test all hardware
gnarl test-hardware

# Test sequencer
gnarl test-sequencer

# Test MIDI input
gnarl test-midi-input
```

### 5. Run!

```bash
gnarl run
```

---

## Next Steps

- Load/save sequencer patterns
- MIDI clock sync with external gear
- Pattern chaining
- Performance macros
- Preset morphing
- Recording to SD card

The Gnarl Pi is now a complete groovebox instrument!

---

**Make it gnarl! 🎛️🎹🔊**

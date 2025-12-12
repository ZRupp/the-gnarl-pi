# Hardware Guide

Complete hardware documentation for The Gnarl Pi synthesizer.

## Bill of Materials (BOM)

### Essential Components

| Component | Quantity | Notes |
|-----------|----------|-------|
| Raspberry Pi 3 | 1 | Pi Zero W works but limited polyphony |
| 1602A LCD Display | 1 | I2C or parallel interface |
| Rotary Encoders | 3-6 | KY-040 or similar, with push button |
| Tactile Switches | 6-12 | Momentary push buttons |
| B103 Joystick | 1 | Dual-axis analog (10kΩ pots) |
| MCP3008 ADC | 1 | 8-channel 10-bit SPI ADC |
| SN74HC595 Shift Register | 3 | For LED control (optional) |
| LEDs | 8-24 | For visual feedback (optional) |
| 10kΩ Resistors | 20+ | Pull-ups for encoders/switches |
| 220Ω Resistors | 24 | For LEDs (if used) |
| USB Audio Interface | 1 | Or I2S DAC (Hifiberry, etc.) |
| Breadboard | 1-2 | Or custom PCB |
| Jumper Wires | Lots | For breadboard prototyping |

### Power Supply

- **Raspberry Pi 3**: 5V 2.5A minimum (3A recommended)
- **Pi Zero W**: 5V 1.5A minimum

## Wiring Diagrams

### GPIO Pin Assignments

**Raspberry Pi 3/Zero W GPIO Header (40-pin):**

```
     3V3  (1) (2)  5V
   GPIO2  (3) (4)  5V
   GPIO3  (5) (6)  GND
   GPIO4  (7) (8)  GPIO14
     GND  (9) (10) GPIO15
  GPIO17 (11) (12) GPIO18
  GPIO27 (13) (14) GND
  GPIO22 (15) (16) GPIO23
     3V3 (17) (18) GPIO24
  GPIO10 (19) (20) GND
   GPIO9 (21) (22) GPIO25
  GPIO11 (23) (24) GPIO8
     GND (25) (26) GPIO7
   GPIO0 (27) (28) GPIO1
   GPIO5 (29) (30) GND
   GPIO6 (31) (32) GPIO12
  GPIO13 (33) (34) GND
  GPIO19 (35) (36) GPIO16
  GPIO26 (37) (38) GPIO20
     GND (39) (40) GPIO21
```

### Recommended Pin Mapping

```yaml
# LCD (I2C)
SDA: GPIO2 (pin 3)
SCL: GPIO3 (pin 5)

# Encoders (3x)
Encoder 1 (Filter Cutoff):
  CLK: GPIO17 (pin 11)
  DT:  GPIO18 (pin 12)
  SW:  GPIO27 (pin 13)

Encoder 2 (Resonance):
  CLK: GPIO22 (pin 15)
  DT:  GPIO23 (pin 16)
  SW:  GPIO24 (pin 18)

Encoder 3 (Distortion):
  CLK: GPIO5 (pin 29)
  DT:  GPIO6 (pin 31)
  SW:  GPIO13 (pin 33)

# Switches (6x)
Switch 1 (Preset 1): GPIO4  (pin 7)
Switch 2 (Preset 2): GPIO14 (pin 8)
Switch 3 (Preset 3): GPIO15 (pin 10)
Switch 4 (Octave Up): GPIO25 (pin 22)
Switch 5 (Octave Down): GPIO12 (pin 32)
Switch 6 (Effect Toggle): GPIO16 (pin 36)

# MCP3008 ADC (SPI)
MOSI: GPIO10 (pin 19)
MISO: GPIO9  (pin 21)
SCLK: GPIO11 (pin 23)
CS:   GPIO8  (pin 24)

# Joystick Button
SW: GPIO26 (pin 37)

# SN74HC595 Shift Registers (3x chained)
DATA:  GPIO19 (pin 35)
CLOCK: GPIO20 (pin 38)
LATCH: GPIO21 (pin 40)
```

## Component Wiring Details

### 1. LCD Display (I2C 1602A)

**I2C Module Connections:**
```
LCD I2C Module    →    Raspberry Pi
─────────────────────────────────────
VCC               →    5V (pin 2 or 4)
GND               →    GND (pin 6, 9, 14, etc.)
SDA               →    GPIO2 (pin 3)
SCL               →    GPIO3 (pin 5)
```

**Note:** Most 1602A LCDs come with an I2C backpack (PCF8574). If you have a parallel LCD, you'll need 6-8 GPIO pins.

**I2C Address Detection:**
```bash
sudo apt-get install i2c-tools
i2cdetect -y 1
```
Common addresses: `0x27` or `0x3F`

---

### 2. Rotary Encoders (KY-040 style)

**Single Encoder Wiring:**
```
Encoder Pin    →    Raspberry Pi
───────────────────────────────────
CLK            →    GPIO17 (example)
DT             →    GPIO18 (example)
SW (button)    →    GPIO27 (example)
+              →    3.3V (NOT 5V!)
GND            →    GND
```

**Important Notes:**
- Use 3.3V, NOT 5V (Pi GPIO is 3.3V logic)
- Internal pull-ups can be enabled in software
- External 10kΩ pull-up resistors recommended for stability
- Debouncing is handled in software

**Pull-up Resistor Schematic (optional but recommended):**
```
          3.3V
           |
         [10kΩ]
           |
    ───────┴────────> to GPIO
           |
       [Encoder]
           |
          GND
```

---

### 3. Switches / Buttons

**Single Switch Wiring:**
```
Switch Pin    →    Raspberry Pi
────────────────────────────────
One side      →    GPIO pin
Other side    →    GND
```

**Pull-up Configuration:**
```
          3.3V
           |
         [10kΩ] (or use internal pull-up)
           |
    ───────┴────────> to GPIO
           |
        [Switch]
           |
          GND
```

When pressed: GPIO reads LOW (0)
When released: GPIO reads HIGH (1)

---

### 4. Analog Joystick (B103) with MCP3008 ADC

**MCP3008 Chip Pinout:**
```
    ┌─────┴─────┐
CH0 │1        16│ VDD (3.3V)
CH1 │2        15│ VREF (3.3V)
CH2 │3        14│ AGND (GND)
CH3 │4        13│ CLK (GPIO11)
CH4 │5        12│ DOUT (GPIO9 - MISO)
CH5 │6        11│ DIN (GPIO10 - MOSI)
CH6 │7        10│ CS (GPIO8)
CH7 │8         9│ DGND (GND)
    └───────────┘
```

**MCP3008 to Pi:**
```
MCP3008 Pin    →    Raspberry Pi
─────────────────────────────────
VDD (16)       →    3.3V (pin 1 or 17)
VREF (15)      →    3.3V (pin 1 or 17)
AGND (14)      →    GND
DGND (9)       →    GND
CLK (13)       →    GPIO11 (pin 23) - SCLK
DOUT (12)      →    GPIO9  (pin 21) - MISO
DIN (11)       →    GPIO10 (pin 19) - MOSI
CS (10)        →    GPIO8  (pin 24) - CE0
```

**Joystick to MCP3008:**
```
Joystick Pin    →    MCP3008
────────────────────────────────
VCC (+5V)       →    3.3V (or voltage divider for 5V joystick)
GND             →    GND
VRx (X-axis)    →    CH0 (pin 1)
VRy (Y-axis)    →    CH1 (pin 2)
SW (button)     →    GPIO26 (pin 37) on Pi
```

**Note:** If your joystick is 5V, use a voltage divider to bring output to 3.3V range:
```
Joystick VRx ──[10kΩ]──┬──> to MCP3008 CH0
                       │
                     [10kΩ]
                       │
                      GND
```

**Enable SPI on Raspberry Pi:**
```bash
sudo raspi-config
# Interface Options → SPI → Enable
sudo reboot
```

**Test SPI:**
```bash
ls /dev/spi*
# Should show: /dev/spidev0.0  /dev/spidev0.1
```

---

### 5. SN74HC595 Shift Registers (for LEDs)

**Single SN74HC595 Pinout:**
```
    ┌─────┴─────┐
 QB │1        16│ VCC (5V)
 QC │2        15│ QA
 QD │3        14│ SER (DATA from Pi)
 QE │4        13│ OE (GND)
 QF │5        12│ RCLK (LATCH from Pi)
 QG │6        11│ SRCLK (CLOCK from Pi)
 QH │7        10│ SRCLR (VCC)
GND │8         9│ QH' (to next chip's SER)
    └───────────┘
```

**First Shift Register to Pi:**
```
SN74HC595      →    Raspberry Pi
─────────────────────────────────
VCC (16)       →    5V (pin 2 or 4)
GND (8)        →    GND
SER (14)       →    GPIO19 (pin 35) - DATA
RCLK (12)      →    GPIO21 (pin 40) - LATCH
SRCLK (11)     →    GPIO20 (pin 38) - CLOCK
SRCLR (10)     →    5V (active low, tie high)
OE (13)        →    GND (active low, always enabled)
```

**Chaining Multiple Shift Registers:**
```
Chip 1 QH' (pin 9) → Chip 2 SER (pin 14)
Chip 2 QH' (pin 9) → Chip 3 SER (pin 14)

All chips share:
- VCC, GND
- RCLK (LATCH)
- SRCLK (CLOCK)
- SRCLR (tie to VCC)
- OE (tie to GND)
```

**LED Connections:**
Each output pin (QA-QH) can drive an LED:
```
SN74HC595 Output ──[220Ω]──>|── GND
                           LED
```

---

## Complete System Wiring Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Raspberry Pi 3                           │
│                                                             │
│  GPIO2,3 ────────────────────> LCD (I2C)                    │
│                                                             │
│  GPIO17,18,27 ────────────────> Encoder 1 (Filter)          │
│  GPIO22,23,24 ────────────────> Encoder 2 (Resonance)       │
│  GPIO5,6,13   ────────────────> Encoder 3 (Distortion)      │
│                                                             │
│  GPIO4,14,15,25,12,16 ────────> Switches (6x)               │
│                                                             │
│  GPIO10,9,11,8 ───────────────> MCP3008 (SPI)               │
│  GPIO26 ──────────────────────> Joystick Button             │
│                                                             │
│  GPIO19,20,21 ────────────────> SN74HC595 (x3 chained)      │
│                                                             │
│  USB ─────────────────────────> USB Audio Interface         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
         │                              │
         │                              │
         ▼                              ▼
    Power Supply                  Audio Output
     (5V 2.5A)                    (Speakers/Amp)


MCP3008 ADC:
  CH0 ← Joystick X-axis
  CH1 ← Joystick Y-axis


SN74HC595 Chain (3 chips = 24 LED outputs):
  Chip 1: QA-QH → LEDs 1-8
  Chip 2: QA-QH → LEDs 9-16
  Chip 3: QA-QH → LEDs 17-24
```

---

## Assembly Steps

### 1. Prepare the Breadboard

1. Place MCP3008 on breadboard
2. Place 3x SN74HC595 chips
3. Connect power rails (3.3V and 5V)
4. Connect ground rails

### 2. Connect LCD First

Start with I2C LCD - easiest to test:
```bash
i2cdetect -y 1
```

### 3. Add One Encoder

Wire one encoder, test with:
```bash
gnarl test-encoder 0
```

### 4. Add Switches One at a Time

Add each switch, test individually.

### 5. Wire MCP3008 and Joystick

Enable SPI, test analog readings.

### 6. Add Shift Registers and LEDs (Optional)

Test LED output with blink patterns.

---

## Testing Individual Components

### Test LCD:
```bash
# Install i2c-tools
sudo apt-get install i2c-tools python3-smbus

# Detect I2C device
i2cdetect -y 1

# Test with gnarl
gnarl test-lcd
```

### Test Encoder:
```bash
gnarl test-encoder 0
# Rotate encoder, watch for value changes
```

### Test Switch:
```bash
gnarl test-switch 0
# Press switch, watch for state changes
```

### Test Joystick:
```bash
gnarl test-joystick
# Move joystick, watch X/Y values
```

### Test LEDs:
```bash
gnarl test-leds
# Should see LED test pattern
```

---

## Troubleshooting

### LCD not detected:
- Check I2C address with `i2cdetect -y 1`
- Verify SDA/SCL connections
- Check contrast pot on I2C backpack

### Encoder values jumping:
- Add external 10kΩ pull-up resistors
- Check for loose connections
- Enable software debouncing

### Joystick readings noisy:
- Add smoothing/averaging in software
- Check power supply stability
- Ensure good ground connection

### LEDs not lighting:
- Check 5V power supply
- Verify shift register wiring (especially clock/latch)
- Test each chip individually

---

## PCB Design (Future)

For a permanent build, consider:
- Custom PCB with all components
- Panel-mount encoders and switches
- 3D-printed enclosure
- Power supply integrated

PCB design files will be added to `/hardware` directory.

---

## Safety Notes

- **Never connect 5V to GPIO pins** (they are 3.3V only!)
- Use appropriate current-limiting resistors for LEDs
- Ensure adequate power supply for Pi + peripherals
- Be careful with shift register outputs (can source/sink 35mA max per pin)

---

## Next Steps

Once hardware is assembled:
1. Run `sudo ./install.sh` to configure software
2. Edit `/etc/gnarl/config.yaml` with your pin assignments
3. Test each component with `gnarl test-*` commands
4. Load synth patches and start making grungy sounds!

See [../README.md](../README.md) for software setup and usage.

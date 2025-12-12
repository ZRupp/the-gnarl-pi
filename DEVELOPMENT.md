## Development Guide

Complete guide for developing and contributing to The Gnarl Pi.

## Architecture

### Project Structure

```
the-gnarl-pi/
├── src/gnarl/              # Main Python package
│   ├── config/             # Configuration models (Pydantic)
│   │   └── models.py       # Config data classes
│   ├── hardware/           # Hardware abstraction layer
│   │   ├── lcd.py          # LCD display handler
│   │   ├── encoder.py      # Rotary encoder handler
│   │   ├── switch.py       # Switch/button handler
│   │   ├── joystick.py     # Analog joystick via MCP3008
│   │   └── shift_register.py  # LED control via SN74HC595
│   ├── synth/              # Synth engine interface
│   │   └── interface.py    # MIDI communication
│   ├── ui/                 # User interface logic
│   │   └── controller.py   # Main controller
│   └── cli.py              # Command-line interface
├── config/                 # Example configurations
├── docs/                   # Documentation
│   └── HARDWARE.md         # Hardware wiring guide
├── tests/                  # Unit tests
├── pyproject.toml          # Python project config
└── README.md               # Main documentation
```

### Component Diagram

```
┌─────────────────────────────────────────────┐
│              CLI (cli.py)                   │
│  - Parse arguments                          │
│  - Setup logging                            │
│  - Run main loop                            │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│         GnarlController (ui/controller.py)  │
│  - Coordinate hardware & synth              │
│  - Handle events                            │
│  - Update display                           │
└────┬─────────────────┬──────────────────────┘
     │                 │
     ▼                 ▼
┌─────────────┐   ┌──────────────────────┐
│  Hardware   │   │  SynthInterface      │
│  Components │   │  - MIDI output       │
│  - LCD      │   │  - CC, Note, PC      │
│  - Encoders │   │  - Pitch bend        │
│  - Switches │   └──────────────────────┘
│  - Joystick │            │
│  - LEDs     │            ▼
└─────────────┘   ┌──────────────────────┐
                  │  JACK Audio Server   │
                  │  (External)          │
                  └──────────┬───────────┘
                             ▼
                  ┌──────────────────────┐
                  │  ZynAddSubFX         │
                  │  Synth Engine        │
                  │  (External)          │
                  └──────────────────────┘
```

### Data Flow

1. **Hardware Event** (encoder rotation, switch press, etc.)
2. **Hardware Layer** captures event → triggers callback
3. **Controller** receives callback → processes event
4. **Synth Interface** sends MIDI message
5. **JACK Server** routes MIDI to synth engine
6. **Synth Engine** generates audio
7. **Controller** updates **LCD Display** and **LEDs**

## Development Setup

### Prerequisites

- Raspberry Pi 3 or Pi Zero W
- Python 3.9+
- Git
- Hardware components (see HARDWARE.md)

### Initial Setup

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/the-gnarl-pi.git
cd the-gnarl-pi

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e ".[dev]"

# Install system dependencies (on Raspberry Pi)
sudo apt-get update
sudo apt-get install -y \
    python3-dev \
    libasound2-dev \
    libjack-dev \
    jackd2 \
    zynaddsubfx \
    i2c-tools
```

### Enable Hardware Interfaces

```bash
# Enable I2C, SPI, and GPIO
sudo raspi-config
# Interface Options → I2C → Enable
# Interface Options → SPI → Enable

# Reboot
sudo reboot
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=gnarl --cov-report=html

# Run specific test file
pytest tests/test_config.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code with Black
black src/ tests/

# Lint with Ruff
ruff check src/ tests/

# Type check with mypy
mypy src/

# Run all checks
black src/ tests/ && ruff check src/ tests/ && mypy src/
```

## Adding New Features

### Adding a New Hardware Component

1. **Create hardware module** in `src/gnarl/hardware/`:

```python
# src/gnarl/hardware/my_component.py
import logging
from typing import Callable, Optional
from gpiozero import ...

logger = logging.getLogger(__name__)

class MyComponent:
    """Handler for my custom component."""

    def __init__(self, config: MyComponentConfig) -> None:
        """Initialize component."""
        self.config = config
        # Initialize hardware here

    def on_event(self, callback: Callable[[], None]) -> None:
        """Register event callback."""
        self._callback = callback

    def close(self) -> None:
        """Clean up resources."""
        # Cleanup here
```

2. **Add configuration model** in `src/gnarl/config/models.py`:

```python
class MyComponentConfig(BaseModel):
    """Configuration for my component."""
    pin: int = Field(ge=0, le=27)
    # Add other config fields
```

3. **Update HardwareConfig**:

```python
class HardwareConfig(BaseModel):
    # ... existing fields ...
    my_component: Optional[MyComponentConfig] = None
```

4. **Integrate in controller** (`src/gnarl/ui/controller.py`):

```python
def start(self) -> None:
    # ... existing initialization ...

    if self.config.hardware.my_component:
        self.my_component = MyComponent(self.config.hardware.my_component)
        self.my_component.on_event(self._handle_my_component)
```

5. **Add tests** in `tests/test_my_component.py`:

```python
import pytest
from gnarl.hardware.my_component import MyComponent

def test_my_component():
    # Test your component
    pass
```

### Adding a New Synth Engine

1. **Create synth engine interface** in `src/gnarl/synth/`:

```python
# src/gnarl/synth/my_synth.py
class MySynthEngine:
    """Interface for my synth engine."""

    def load_preset(self, path: Path) -> None:
        """Load preset file."""
        pass

    def set_parameter(self, param: str, value: float) -> None:
        """Set synth parameter."""
        pass
```

2. **Update SynthEngine enum**:

```python
class SynthEngine(str, Enum):
    ZYN = "zyn"
    YOSHIMI = "yoshimi"
    MY_SYNTH = "my_synth"  # Add new engine
```

3. **Integrate in SynthInterface**:

```python
def _initialize_synth(self) -> None:
    if self.config.engine == SynthEngine.MY_SYNTH:
        self.engine = MySynthEngine(self.config)
    # ... existing engines ...
```

## Testing

### Unit Tests

Test individual components in isolation:

```python
# tests/test_encoder.py
import pytest
from gnarl.config import EncoderConfig
from gnarl.hardware.encoder import RotaryEncoder

def test_encoder_initialization():
    config = EncoderConfig(
        name="test",
        clk_pin=17,
        dt_pin=18,
        min_value=0,
        max_value=127,
        default=64
    )
    # Mock GPIO hardware
    # Test encoder behavior
    pass
```

### Hardware Tests

Test on actual hardware:

```bash
# Test all hardware
gnarl test-hardware

# Test specific components
python -m gnarl.hardware.lcd    # Test LCD
python -m gnarl.hardware.encoder  # Test encoders
```

### Integration Tests

Test complete system:

```bash
# Run with test config
gnarl run -c config/test.yaml -v
```

## Audio Configuration

### JACK Setup

Create `/etc/jackdrc`:

```bash
/usr/bin/jackd -dalsa -dhw:1 -r48000 -p128 -n2 -Xseq
```

### ZynAddSubFX Setup

Start ZynAddSubFX:

```bash
# Command line mode
zynaddsubfx -O alsa -o hw:1 -r 48000 -b 128

# Or via JACK
zynaddsubfx -O jack -r 48000 -b 128
```

Create presets in `~/.local/share/zynaddsubfx/banks/`.

### Low-Latency Tuning

Edit `/boot/config.txt`:

```ini
# Disable audio (use USB/I2S DAC)
dtparam=audio=off

# Reduce GPU memory
gpu_mem=16

# Performance governor
force_turbo=1
```

Edit `/etc/security/limits.conf`:

```
@audio - rtprio 95
@audio - memlock unlimited
```

Add user to audio group:

```bash
sudo usermod -a -G audio $USER
```

## Configuration

### Config File Format

YAML configuration in `/etc/gnarl/config.yaml`:

```yaml
hardware:
  lcd:
    type: "i2c"
    address: 0x27
    cols: 16
    rows: 2

  encoders:
    - name: "filter_cutoff"
      clk_pin: 17
      dt_pin: 18
      sw_pin: 27
      min_value: 0
      max_value: 127
      default: 64
      midi_cc: 74  # Brightness

synth:
  engine: "zyn"
  sample_rate: 48000
  buffer_size: 128

presets:
  - name: "Dirty Lead"
    file: "/path/to/preset.xiz"
```

### Validation

Config is validated using Pydantic:
- Type checking
- Range validation (0-127 for MIDI, 0-27 for GPIO pins)
- Required fields enforced

## Performance Optimization

### Python Optimization

- Use `gpiozero` for hardware (built on RPi.GPIO, well-optimized)
- Minimize work in event callbacks
- Use logging at appropriate levels (DEBUG only when needed)

### Real-Time Audio

- Set JACK to real-time priority (`-R` flag)
- Use small buffer sizes (64-128 samples)
- Disable unnecessary services:

```bash
sudo systemctl disable bluetooth
sudo systemctl disable wifi-powersave
```

### CPU Governor

Set to performance mode:

```bash
echo "performance" | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

## Debugging

### Enable Verbose Logging

```bash
gnarl run --verbose
```

### Monitor MIDI Traffic

```bash
# Using aseqdump
aseqdump -p "GnarlPi"

# Using JACK
jack_midi_dump GnarlPi
```

### Check JACK Status

```bash
jack_lsp                    # List ports
jack_connect GnarlPi:out ZynAddSubFX:in  # Manual connection
```

### GPIO Debugging

```bash
# Check GPIO state
gpio readall

# Monitor I2C
i2cdetect -y 1

# Monitor SPI
ls /dev/spi*
```

## Contributing

### Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Run tests and code quality checks
5. Commit with clear messages
6. Push to your fork
7. Open a pull request

### Code Style

- Follow PEP 8
- Use type hints
- Document functions with docstrings
- Keep functions focused and small
- Add tests for new features

### Commit Messages

```
feat: Add support for new encoder type
fix: Correct LCD display timing issue
docs: Update hardware wiring diagram
test: Add tests for joystick calibration
```

## Common Issues

### Import Errors

If you get `ModuleNotFoundError`:
```bash
# Ensure package is installed
pip install -e .
```

### GPIO Permission Denied

Add user to gpio group:
```bash
sudo usermod -a -G gpio,input $USER
```

### I2C Not Working

```bash
# Check I2C is enabled
ls /dev/i2c*

# Should show /dev/i2c-1

# Check device address
i2cdetect -y 1
```

### Audio Crackles (xruns)

- Increase buffer size in config (`buffer_size: 256`)
- Check CPU governor is set to "performance"
- Reduce polyphony
- Close unnecessary applications

## Release Process

1. Update version in `pyproject.toml` and `src/gnarl/__init__.py`
2. Update CHANGELOG.md
3. Run full test suite
4. Tag release: `git tag -a v0.1.0 -m "Release v0.1.0"`
5. Push tag: `git push origin v0.1.0`
6. Create GitHub release

## Resources

- [gpiozero Documentation](https://gpiozero.readthedocs.io/)
- [ZynAddSubFX Manual](https://zynaddsubfx.sourceforge.io/doc.html)
- [JACK Audio Documentation](https://jackaudio.org/api/)
- [RPLCD Documentation](https://rplcd.readthedocs.io/)
- [Raspberry Pi GPIO Pinout](https://pinout.xyz/)

## License

MIT License - see [LICENSE](LICENSE) for details.

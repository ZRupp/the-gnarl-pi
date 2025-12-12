"""Configuration data models using Pydantic."""

from enum import Enum
from pathlib import Path
from typing import Any, Literal, Optional

import yaml
from pydantic import BaseModel, Field, field_validator


class LCDType(str, Enum):
    """LCD interface types."""

    I2C = "i2c"
    PARALLEL = "parallel"


class SynthEngine(str, Enum):
    """Available synth engines."""

    ZYN = "zyn"
    YOSHIMI = "yoshimi"
    FLUIDSYNTH = "fluidsynth"


class ActionType(str, Enum):
    """Types of actions for switches."""

    LOAD_PRESET = "load_preset"
    OCTAVE_SHIFT = "octave_shift"
    TOGGLE_EFFECT = "toggle_effect"
    PARAMETER_PAGE = "parameter_page"


class LCDConfig(BaseModel):
    """LCD display configuration."""

    type: LCDType = LCDType.I2C
    address: int = Field(default=0x27, ge=0x00, le=0xFF)
    cols: int = Field(default=16, ge=8, le=40)
    rows: int = Field(default=2, ge=1, le=4)
    # Parallel mode pins (only used if type == parallel)
    rs_pin: Optional[int] = None
    e_pin: Optional[int] = None
    data_pins: Optional[list[int]] = None


class EncoderConfig(BaseModel):
    """Rotary encoder configuration."""

    name: str
    clk_pin: int = Field(ge=0, le=27)
    dt_pin: int = Field(ge=0, le=27)
    sw_pin: Optional[int] = Field(default=None, ge=0, le=27)
    min_value: int = Field(default=0, ge=0, le=127)
    max_value: int = Field(default=127, ge=0, le=127)
    default: int = Field(default=64, ge=0, le=127)
    midi_cc: Optional[int] = Field(default=None, ge=0, le=127)

    @field_validator("default")
    @classmethod
    def validate_default_in_range(cls, v: int, info: Any) -> int:
        """Ensure default is within min/max range."""
        data = info.data
        if "min_value" in data and "max_value" in data:
            if not (data["min_value"] <= v <= data["max_value"]):
                raise ValueError(f"default must be between min_value and max_value")
        return v


class SwitchConfig(BaseModel):
    """Switch/button configuration."""

    name: str
    pin: int = Field(ge=0, le=27)
    action: ActionType
    preset: Optional[int] = Field(default=None, ge=0)
    value: Optional[int] = None  # For octave_shift, etc.
    midi_note: Optional[int] = Field(default=None, ge=0, le=127)
    midi_cc: Optional[int] = Field(default=None, ge=0, le=127)


class JoystickConfig(BaseModel):
    """Analog joystick configuration via MCP3008."""

    spi_device: int = Field(default=0, ge=0, le=1)
    spi_channel: int = Field(default=0, ge=0, le=1)
    x_channel: int = Field(default=0, ge=0, le=7)
    y_channel: int = Field(default=1, ge=0, le=7)
    sw_pin: Optional[int] = Field(default=None, ge=0, le=27)
    x_midi_cc: int = Field(default=1, ge=0, le=127)  # Modulation wheel
    y_midi_cc: int = Field(default=2, ge=0, le=127)  # Breath controller
    deadzone: int = Field(default=10, ge=0, le=100)  # Deadzone percentage


class ShiftRegisterConfig(BaseModel):
    """SN74HC595 shift register configuration."""

    data_pin: int = Field(ge=0, le=27)
    clock_pin: int = Field(ge=0, le=27)
    latch_pin: int = Field(ge=0, le=27)
    num_registers: int = Field(default=3, ge=1, le=8)


class HardwareConfig(BaseModel):
    """Complete hardware configuration."""

    lcd: LCDConfig
    encoders: list[EncoderConfig] = Field(default_factory=list)
    switches: list[SwitchConfig] = Field(default_factory=list)
    joystick: Optional[JoystickConfig] = None
    shift_registers: Optional[ShiftRegisterConfig] = None


class SynthConfig(BaseModel):
    """Synth engine configuration."""

    engine: SynthEngine = SynthEngine.ZYN
    jack_client_name: str = "ZynAddSubFX"
    sample_rate: int = Field(default=48000, ge=22050, le=96000)
    buffer_size: int = Field(default=128, ge=32, le=2048)
    midi_channel: int = Field(default=0, ge=0, le=15)
    polyphony: int = Field(default=8, ge=1, le=32)


class PresetConfig(BaseModel):
    """Synth preset configuration."""

    name: str
    file: Path
    description: Optional[str] = None


class GnarlConfig(BaseModel):
    """Root configuration model."""

    hardware: HardwareConfig
    synth: SynthConfig
    presets: list[PresetConfig] = Field(default_factory=list)

    @classmethod
    def from_yaml(cls, path: Path) -> "GnarlConfig":
        """Load configuration from YAML file."""
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return cls(**data)

    def to_yaml(self, path: Path) -> None:
        """Save configuration to YAML file."""
        with open(path, "w") as f:
            yaml.dump(self.model_dump(mode="python"), f, default_flow_style=False)

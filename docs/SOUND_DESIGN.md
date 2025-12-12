# Sound Design Guide for The Gnarl Pi

Tips and techniques for creating grungy, dirty, and aggressive sounds.

## Philosophy

The Gnarl Pi is designed for **lo-fi, aggressive, and characterful** synthesis. Think:
- Gritty basslines
- Distorted leads
- Degraded textures
- Analog imperfection
- Happy accidents

## ZynAddSubFX Tips

### 1. Aggressive Filters

**High Resonance:**
- Set filter resonance (Q) to 80-127
- Use low-pass filter type
- Sweep cutoff with encoder for screaming tones

**Multiple Filter Stages:**
- Enable formant filter for vocal-like tones
- Combine with SVF filter for extra grit

### 2. Distortion & Saturation

**Built-in Distortion:**
- Enable distortion on ADsynth or PADsynth
- Set distortion level to 60-100
- Use "Crunch" or "Overdrive" types

**Waveshaping:**
- Use non-linear waveshaping on oscillators
- Try "Sigmoid", "Quantize", or "Wrap" types

### 3. Detuning for Width

**Oscillator Detuning:**
- Add 2-3 voices per oscillator
- Detune by 5-15 cents
- Creates chorus-like width and movement

**Octave Doubling:**
- Layer oscillators at -12 and +12 semitones
- Blend to taste for massive sound

### 4. Bit Reduction

**Lo-Fi Effect:**
- Reduce bit depth in effects chain
- 8-bit or 4-bit for vintage digital grit
- Combine with sample rate reduction

### 5. Modulation Chaos

**LFO Randomness:**
- Use random LFO shapes
- Modulate multiple parameters simultaneously
- Fast rates (10-20 Hz) for glitchy effects

**Envelope Hardness:**
- Very short attack times (<5ms)
- Sharp decay for percussive sounds
- Long release for drones

## Preset Templates

### Dirty Lead

```
ADsynth Voice 1:
  Waveform: Sawtooth
  Detune: +10 cents
  Voices: 3

Filter:
  Type: Low-pass 2-pole
  Cutoff: 60 (modulate with encoder!)
  Resonance: 95
  Envelope Amount: +80

Distortion:
  Type: Overdrive
  Level: 75

Envelope:
  Attack: 5ms
  Decay: 100ms
  Sustain: 60
  Release: 200ms
```

### Grungy Bass

```
ADsynth Voice 1:
  Waveform: Square
  Octave: -1
  Detune: 0

ADsynth Voice 2:
  Waveform: Sawtooth
  Octave: -1
  Detune: +7 cents

Filter:
  Type: Low-pass 4-pole
  Cutoff: 40
  Resonance: 70
  Key tracking: 100%

Distortion:
  Type: Crunch
  Level: 85

Envelope:
  Attack: 1ms
  Decay: 150ms
  Sustain: 80
  Release: 100ms
```

### Lo-Fi Pad

```
PADsynth:
  Base waveform: Sine
  Bandwidth: 80
  Overtones: Add odds (3rd, 5th, 7th)

Effects:
  Bit Crusher: 8-bit
  Sample Rate: 22kHz
  Chorus: Depth 40, Rate 0.5Hz
  Reverb: Room, Decay 3s

Filter:
  Type: Band-pass
  Cutoff: 70
  Resonance: 45
  LFO: Slow sine (0.2 Hz)
```

## Hardware Control Mapping

### Essential Parameters to Map

**Encoder 1 - Filter Cutoff (CC 74):**
- Most immediate sound change
- Sweet spot: 40-80 range
- Modulate in real-time for expression

**Encoder 2 - Resonance (CC 71):**
- Adds character and edge
- Be careful above 100 (can self-oscillate)
- Pair with cutoff for filter sweeps

**Encoder 3 - Distortion/Drive (CC 94):**
- Instant grit control
- 0 = clean, 127 = destroyed
- Great for dynamics

**Joystick X - Modulation (CC 1):**
- Vibrato depth
- Filter wobble
- LFO amount

**Joystick Y - Expression (CC 2):**
- Overall brightness
- Reverb mix
- Dry/wet balance

## Advanced Techniques

### 1. Feedback Routing

Create feedback loops in ZynAddSubFX:
- Route LFO to modulate its own frequency
- Envelope modulates attack time
- Filter cutoff modulates resonance

### 2. Ring Modulation

For metallic, clangorous tones:
- Enable ring mod between oscillators
- Detune oscillators for more chaos
- Great for industrial/harsh sounds

### 3. Multi-Timbral Layers

Split MIDI channels:
- Bass on channel 0
- Lead on channel 1
- Effects/noise on channel 2
- Control all from one interface

### 4. Velocity Tricks

Even without velocity-sensitive keys:
- Map switches to different velocities
- Low velocity = soft/mellow
- High velocity = aggressive/bright

## Sound Design Workflow

1. **Start Simple:**
   - Single oscillator
   - Basic filter
   - No effects

2. **Add Character:**
   - Detune for width
   - Filter resonance for edge
   - Distortion for grit

3. **Movement:**
   - LFO modulation
   - Envelope shaping
   - Parameter sweeps

4. **Polish:**
   - Bit reduction
   - Reverb/delay
   - Final EQ

## Sample Patch Settings

### "Rusty Saw"
- 3 sawtooth oscillators, detuned
- Harsh low-pass filter (Q=90)
- Heavy distortion
- No reverb (keep it dry and dirty)

### "Broken Radio"
- Square wave + noise
- Band-pass filter (moving)
- Bit crusher (6-bit)
- Sample rate reduction
- Random LFO on pitch

### "Grinding Bass"
- 2 square waves, octave apart
- Very short envelope
- Distortion → Bit crush → Filter
- Filter cutoff at 30, resonance at 100

## Tips from the Gritty Side

- **Embrace imperfection:** Slight detuning is your friend
- **Less is more:** Sometimes one dirty oscillator beats three clean ones
- **Movement matters:** Static sounds are boring - add modulation
- **Trust your ears:** If it sounds good, it is good
- **Save everything:** Your "mistakes" might be your best sounds

## Hardware Performance Tips

### Live Tweaking

1. **Filter Sweeps:** Slow, dramatic cutoff movements
2. **Resonance Peaks:** Quick resonance spikes for accent
3. **Octave Jumps:** Switch octaves mid-phrase
4. **Preset Morphing:** Rapid preset changes for glitches

### Recording Workflow

1. Set base sound with encoders
2. Record while tweaking cutoff/resonance
3. Capture multiple takes
4. Layer different preset variations

## Resources

- ZynAddSubFX has hundreds of built-in presets - start there!
- The "Will_Godfrey_Collection" banks have great starting points
- Study presets you like - see what makes them tick
- Share your patches with the community

---

**Remember:** The Gnarl Pi is about exploration and happy accidents. Turn knobs, mash switches, and embrace the grit!

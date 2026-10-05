import math
import struct
import wave
import random

SAMPLE_RATE = 44100
DURATION = 48.0  # seconds
TOTAL_SAMPLES = int(SAMPLE_RATE * DURATION)

BPM = 85.0
BEAT_DUR = 60.0 / BPM  # ~0.7058 sec
EIGHTH_DUR = BEAT_DUR / 2.0

# Chord frequencies (Hz) for Cmaj7, Am7, Dm7, G7
CHORDS = [
    # Cmaj7 (C4, E4, G4, B4)
    [261.63, 329.63, 392.00, 493.88],
    # Am7 (A3, C4, E4, G4)
    [220.00, 261.63, 329.63, 392.00],
    # Dm7 (D4, F4, A4, C5)
    [293.66, 349.23, 440.00, 523.25],
    # G7 (G3, B3, D4, F4)
    [196.00, 246.94, 293.66, 349.23]
]

samples = [0.0] * TOTAL_SAMPLES

# 1. Generate Lo-Fi Chords
print("Synthesizing warm lo-fi chords...")
for i in range(TOTAL_SAMPLES):
    t = i / SAMPLE_RATE
    beat_num = t / BEAT_DUR
    bar_num = int(beat_num / 4.0)
    chord_idx = bar_num % len(CHORDS)
    chord_freqs = CHORDS[chord_idx]
    
    # Envelope within each bar (soft attack, gentle decay)
    bar_t = (beat_num % 4.0) * BEAT_DUR
    env = math.exp(-0.4 * bar_t) * (1.0 - math.exp(-15.0 * bar_t))
    
    chord_val = 0.0
    for freq in chord_freqs:
        # Soft sine wave + subtle harmonic for warm electric piano feel
        v = math.sin(2.0 * math.pi * freq * t) + 0.25 * math.sin(4.0 * math.pi * freq * t)
        chord_val += v
    
    samples[i] += chord_val * env * 0.18

# 2. Add Bouncy Lo-Fi Drums (Kick, Snare, Hi-Hat)
print("Adding bouncy lo-fi drum rhythm...")
for i in range(TOTAL_SAMPLES):
    t = i / SAMPLE_RATE
    beat = (t / BEAT_DUR) % 4.0
    beat_t = (t % BEAT_DUR)
    
    # Kick drum on beat 0 and beat 2.5
    kick = 0.0
    if beat_t < 0.2 and ((0.0 <= beat < 0.5) or (2.4 <= beat < 2.7)):
        k_t = beat_t if beat < 1.0 else (beat_t - 0.4 * BEAT_DUR)
        if k_t > 0:
            k_freq = 110.0 * math.exp(-25.0 * k_t)  # pitch sweep down
            k_env = math.exp(-12.0 * k_t)
            kick = math.sin(2.0 * math.pi * k_freq * k_t) * k_env * 0.45
            
    # Snare / Rimshot on beat 1.0 and 3.0
    snare = 0.0
    if (1.0 <= beat < 1.3 or 3.0 <= beat < 3.3):
        s_t = beat_t
        s_env = math.exp(-20.0 * s_t)
        noise = (random.random() * 2.0 - 1.0)
        tone = math.sin(2.0 * math.pi * 180.0 * s_t)
        snare = (tone * 0.3 + noise * 0.7) * s_env * 0.25
        
    # Hi-Hat on 8th notes with slight swing
    hihat = 0.0
    eighth = (t / EIGHTH_DUR) % 8.0
    eighth_t = (t % EIGHTH_DUR)
    if eighth_t < 0.08:
        h_env = math.exp(-40.0 * eighth_t)
        hihat = (random.random() * 2.0 - 1.0) * h_env * 0.12
        
    samples[i] += kick + snare + hihat

# 3. Add Soft Vinyl Crackle / Ambient Texture
print("Applying lo-fi analog texture...")
for i in range(TOTAL_SAMPLES):
    if random.random() < 0.003:  # occasional crackle pop
        samples[i] += (random.random() * 2.0 - 1.0) * 0.08
    samples[i] += (random.random() * 2.0 - 1.0) * 0.008  # background tape noise

# Normalize to avoid clipping
max_val = max(abs(s) for s in samples)
if max_val > 0:
    samples = [s / max_val * 0.85 for s in samples]

# Write to WAV
wav_path = "lofi_track.wav"
print(f"Saving WAV to {wav_path}...")
with wave.open(wav_path, "w") as wf:
    wf.setnchannels(1)  # Mono
    wf.setsampwidth(2)  # 16-bit
    wf.setframerate(SAMPLE_RATE)
    packed_data = bytearray()
    for s in samples:
        int_sample = int(s * 32767.0)
        packed_data.extend(struct.pack("<h", int_sample))
    wf.writeframes(packed_data)

print("Lo-fi music track generated successfully!")

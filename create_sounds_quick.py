import wave
import math
import os

def create_wav_file(filename, frames_array, sample_rate=44100):
    """Create a WAV file from an array of sample frames."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)   # 2 bytes per sample
        wav_file.setframerate(sample_rate)
        for frame in frames_array:
            wav_file.writeframes(frame.to_bytes(2, byteorder='little', signed=True))

# Generate jump.wav
frames = []
sample_rate = 44100
duration = 0.2
total_samples = int(duration * sample_rate)
for i in range(total_samples):
    progress = i / total_samples
    freq = 400 + (400 * progress)
    sample = int(32767 * 0.3 * math.sin(2.0 * math.pi * freq * i / sample_rate))
    frames.append(sample)
create_wav_file('D:\\splotch\\assets\\sounds\\jump.wav', frames, sample_rate)
print("Created jump.wav")

# Generate death.wav
frames = []
total_samples = int(0.5 * sample_rate)
for i in range(total_samples):
    progress = i / total_samples
    freq = 800 - (600 * progress)
    sample = int(32767 * 0.3 * math.sin(2.0 * math.pi * freq * i / sample_rate))
    frames.append(sample)
create_wav_file('D:\\splotch\\assets\\sounds\\death.wav', frames, sample_rate)
print("Created death.wav")

# Generate win.wav - uplifting/victorious sound
frames = []
notes = [
    (523.25, 0.2),  # C5
    (659.25, 0.2),  # E5
    (783.99, 0.4),  # G5
]
for freq, dur in notes:
    total_samples = int(dur * sample_rate)
    for i in range(total_samples):
        sample = int(32767 * 0.3 * math.sin(2.0 * math.pi * freq * i / sample_rate))
        frames.append(sample)
create_wav_file('D:\\splotch\\assets\\sounds\\win.wav', frames, sample_rate)
print("Created win.wav")

# Generate background_music.wav
frames = []
notes = [
    (261.63, 0.5), (293.66, 0.5), (329.63, 0.5), (349.23, 0.5),
    (392.00, 0.5), (440.00, 0.5), (493.88, 0.5), (523.25, 1.0),
]
for _ in range(4):
    for freq, dur in notes:
        total_samples = int(dur * sample_rate)
        for i in range(total_samples):
            sample = int(32767 * 0.2 * math.sin(2.0 * math.pi * freq * i / sample_rate))
            frames.append(sample)
        gap_samples = int(0.1 * sample_rate)
        for _ in range(gap_samples):
            frames.append(0)
create_wav_file('D:\\splotch\\assets\\sounds\\background_music.wav', frames, sample_rate)
print("Created background_music.wav")
print("All sound files created!")


"""
Generate simple placeholder sound files for Rage Bait.
Run this script once to create the sound files.

This creates simple WAV files with tones:
- jump.wav: A short, high-pitched "jump" sound
- death.wav: A descending tone "death" sound
- win.wav: An uplifting "victory" sound
- background_music.wav: A looping background theme
"""

import wave
import math
import os

def generate_sine_wave(frequency, duration, sample_rate=44100):
    """Generate a sine wave at the given frequency and duration."""
    frames = int(duration * sample_rate)
    sample_max = 32767
    frames_array = []
    for i in range(frames):
        sample = sample_max * 0.5 * math.sin(2.0 * math.pi * frequency * i / sample_rate)
        frames_array.append(int(sample))
    return frames_array

def create_wav_file(filename, frames_array, sample_rate=44100):
    """Create a WAV file from an array of sample frames."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)   # 2 bytes per sample
        wav_file.setframerate(sample_rate)
        for frame in frames_array:
            wav_file.writeframes(frame.to_bytes(2, byteorder='little', signed=True))

def generate_jump_sound():
    """Generate a jump sound: ascending tone."""
    filename = os.path.join(os.path.dirname(__file__), 'assets', 'sounds', 'jump.wav')
    frames = []
    # Ascending tone: starts at 400Hz, ends at 800Hz over 0.2 seconds
    sample_rate = 44100
    duration = 0.2
    total_samples = int(duration * sample_rate)
    for i in range(total_samples):
        progress = i / total_samples
        freq = 400 + (400 * progress)  # 400Hz to 800Hz
        sample = int(32767 * 0.3 * math.sin(2.0 * math.pi * freq * i / sample_rate))
        frames.append(sample)
    create_wav_file(filename, frames, sample_rate)
    print(f"Created {filename}")

def generate_death_sound():
    """Generate a death sound: descending tone."""
    filename = os.path.join(os.path.dirname(__file__), 'assets', 'sounds', 'death.wav')
    frames = []
    # Descending tone: starts at 800Hz, ends at 200Hz over 0.5 seconds
    sample_rate = 44100
    duration = 0.5
    total_samples = int(duration * sample_rate)
    for i in range(total_samples):
        progress = i / total_samples
        freq = 800 - (600 * progress)  # 800Hz to 200Hz
        sample = int(32767 * 0.3 * math.sin(2.0 * math.pi * freq * i / sample_rate))
        frames.append(sample)
    create_wav_file(filename, frames, sample_rate)
    print(f"Created {filename}")

def generate_win_sound():
    """Generate a win sound: ascending chord (uplifting)."""
    filename = os.path.join(os.path.dirname(__file__), 'assets', 'sounds', 'win.wav')
    frames = []
    sample_rate = 44100
    # Three ascending notes: C5, E5, G5 (major chord)
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
    create_wav_file(filename, frames, sample_rate)
    print(f"Created {filename}")

def generate_background_music():
    """Generate background music: a simple looping melody."""
    filename = os.path.join(os.path.dirname(__file__), 'assets', 'sounds', 'background_music.wav')
    frames = []
    sample_rate = 44100
    
    # Simple melody notes (frequency, duration in seconds)
    notes = [
        (261.63, 0.5),  # C4
        (293.66, 0.5),  # D4
        (329.63, 0.5),  # E4
        (349.23, 0.5),  # F4
        (392.00, 0.5),  # G4
        (440.00, 0.5),  # A4
        (493.88, 0.5),  # B4
        (523.25, 1.0),  # C5 (longer)
    ]
    
    # Play the melody 4 times to create a ~16 second loop
    for _ in range(4):
        for freq, dur in notes:
            total_samples = int(dur * sample_rate)
            for i in range(total_samples):
                sample = int(32767 * 0.2 * math.sin(2.0 * math.pi * freq * i / sample_rate))
                frames.append(sample)
            # Add small gap between notes
            gap_samples = int(0.1 * sample_rate)
            for _ in range(gap_samples):
                frames.append(0)
    
    create_wav_file(filename, frames, sample_rate)
    print(f"Created {filename}")

if __name__ == '__main__':
    print("Generating sound files...")
    generate_jump_sound()
    generate_death_sound()
    generate_win_sound()
    generate_background_music()
    print("Done! Sound files created in assets/sounds/")


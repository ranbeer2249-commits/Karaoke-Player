#!/usr/bin/env python3
"""
Create demo audio files for testing the MP3 player
"""

import numpy as np
import soundfile as sf
import os

def create_sine_wave(frequency, duration, sample_rate=44100, amplitude=0.3):
    """Create a sine wave at given frequency"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    return amplitude * np.sin(2 * np.pi * frequency * t)

def create_demo_track1():
    """Create demo track 1 - a simple melody"""
    sample_rate = 44100
    duration = 10  # 10 seconds
    
    # Create a simple melody
    frequencies = [440, 494, 523, 587, 659, 587, 523, 494]  # A, B, C, D, E, D, C, B
    note_duration = duration / len(frequencies)
    
    audio = np.array([])
    for freq in frequencies:
        note = create_sine_wave(freq, note_duration, sample_rate)
        audio = np.concatenate([audio, note])
    
    # Add some fade in/out
    fade_samples = int(0.1 * sample_rate)
    fade_in = np.linspace(0, 1, fade_samples)
    fade_out = np.linspace(1, 0, fade_samples)
    
    audio[:fade_samples] *= fade_in
    audio[-fade_samples:] *= fade_out
    
    return audio, sample_rate

def create_demo_track2():
    """Create demo track 2 - a different melody"""
    sample_rate = 44100
    duration = 12  # 12 seconds
    
    # Create a different melody
    frequencies = [330, 349, 392, 440, 392, 349, 330, 294]  # E, F, G, A, G, F, E, D
    note_duration = duration / len(frequencies)
    
    audio = np.array([])
    for freq in frequencies:
        note = create_sine_wave(freq, note_duration, sample_rate)
        audio = np.concatenate([audio, note])
    
    # Add some fade in/out
    fade_samples = int(0.1 * sample_rate)
    fade_in = np.linspace(0, 1, fade_samples)
    fade_out = np.linspace(1, 0, fade_samples)
    
    audio[:fade_samples] *= fade_in
    audio[-fade_samples:] *= fade_out
    
    return audio, sample_rate

def main():
    print("Creating demo audio files...")
    
    # Create demo directory
    demo_dir = "demo_audio"
    if not os.path.exists(demo_dir):
        os.makedirs(demo_dir)
    
    # Create track 1
    print("Creating demo_track1.wav...")
    audio1, sr1 = create_demo_track1()
    sf.write(os.path.join(demo_dir, "demo_track1.wav"), audio1, sr1)
    
    # Create track 2
    print("Creating demo_track2.wav...")
    audio2, sr2 = create_demo_track2()
    sf.write(os.path.join(demo_dir, "demo_track2.wav"), audio2, sr2)
    
    print(f"Demo files created in '{demo_dir}' directory:")
    print("  - demo_track1.wav (10 seconds, melody in A major)")
    print("  - demo_track2.wav (12 seconds, melody in E minor)")
    print("\nYou can now test the MP3 player with these files!")

if __name__ == "__main__":
    main()
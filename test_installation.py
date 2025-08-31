#!/usr/bin/env python3
"""
Test script to verify installation of all required dependencies
"""

def test_imports():
    """Test if all required packages can be imported"""
    print("Testing package imports...")
    
    try:
        import sys
        print("✓ sys")
    except ImportError as e:
        print(f"✗ sys: {e}")
        return False
    
    try:
        import numpy as np
        print("✓ numpy")
    except ImportError as e:
        print(f"✗ numpy: {e}")
        return False
    
    try:
        import pygame
        print("✓ pygame")
    except ImportError as e:
        print(f"✗ pygame: {e}")
        return False
    
    try:
        import librosa
        print("✓ librosa")
    except ImportError as e:
        print(f"✗ librosa: {e}")
        return False
    
    try:
        from PyQt5.QtWidgets import QApplication
        print("✓ PyQt5")
    except ImportError as e:
        print(f"✗ PyQt5: {e}")
        return False
    
    try:
        import matplotlib
        print("✓ matplotlib")
    except ImportError as e:
        print(f"✗ matplotlib: {e}")
        return False
    
    try:
        import soundfile
        print("✓ soundfile")
    except ImportError as e:
        print(f"✗ soundfile: {e}")
        return False
    
    try:
        import pyaudio
        print("✓ pyaudio")
    except ImportError as e:
        print(f"✗ pyaudio: {e}")
        return False
    
    return True

def test_audio_system():
    """Test if audio system is working"""
    print("\nTesting audio system...")
    
    try:
        import pyaudio
        p = pyaudio.PyAudio()
        
        # Get default output device info
        default_output = p.get_default_output_device_info()
        print(f"✓ Default audio output: {default_output['name']}")
        
        # List available devices
        device_count = p.get_device_count()
        print(f"✓ Found {device_count} audio devices")
        
        p.terminate()
        return True
        
    except Exception as e:
        print(f"✗ Audio system test failed: {e}")
        return False

def main():
    print("Dual MP3 Player - Installation Test")
    print("===================================")
    
    # Test Python version
    import sys
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 7):
        print("⚠ Warning: Python 3.7 or higher is recommended")
    
    # Test imports
    imports_ok = test_imports()
    
    # Test audio system
    audio_ok = test_audio_system()
    
    print("\n" + "="*50)
    if imports_ok and audio_ok:
        print("✓ All tests passed! Installation is complete.")
        print("You can now run the application:")
        print("  python3 main.py          # Basic version")
        print("  python3 advanced_player.py # Advanced version")
    else:
        print("✗ Some tests failed. Please check the installation.")
        if not imports_ok:
            print("  - Install missing Python packages: pip install -r requirements.txt")
        if not audio_ok:
            print("  - Install system audio dependencies (see README.md)")

if __name__ == "__main__":
    main()
# Dual MP3 Player with Waveform Visualization

A Python application that allows you to load and play two MP3 files simultaneously with real-time waveform visualization and separate volume controls for each track.

## Features

- **Dual Track Playback**: Play two MP3 files simultaneously
- **Real-time Waveform Visualization**: See the audio waveform for each track
- **Separate Volume Controls**: Independent volume control for each track
- **Modern Dark UI**: Sleek dark-themed interface
- **Progress Tracking**: Real-time progress bars and time display
- **Multiple Audio Formats**: Supports MP3, WAV, FLAC, and OGG files
- **Playback Controls**: Play, pause, stop, and global controls

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Install Dependencies

1. Clone or download this repository
2. Navigate to the project directory
3. Install the required packages:

```bash
pip install -r requirements.txt
```

### System Dependencies

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install python3-dev portaudio19-dev python3-pyaudio
```

#### macOS
```bash
brew install portaudio
```

#### Windows
PyAudio should install automatically with pip, but if you encounter issues, you may need to install it from a wheel file.

## Usage

### Basic Version (Single Track + Simulated Dual Track)

Run the basic version:
```bash
python main.py
```

### Advanced Version (True Dual Track Playback)

Run the advanced version with true simultaneous playback:
```bash
python advanced_player.py
```

## How to Use

1. **Load Tracks**: Click "Load Track 1" and "Load Track 2" to select your MP3 files
2. **Play Individual Tracks**: Use the Play/Pause/Stop buttons for each track
3. **Play Both Tracks**: Click "Play All" to start both tracks simultaneously
4. **Volume Control**: Adjust the volume sliders for each track independently
5. **Monitor Progress**: Watch the waveform visualization and progress bars

## File Structure

```
├── main.py              # Basic MP3 player (single track + simulated dual)
├── advanced_player.py   # Advanced MP3 player (true dual track playback)
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Technical Details

### Basic Version (`main.py`)
- Uses pygame.mixer for audio playback
- Simulates dual-track playback
- Good for basic audio playback needs

### Advanced Version (`advanced_player.py`)
- Uses PyAudio for true simultaneous playback
- Real-time audio processing
- Better performance for dual-track scenarios

## Troubleshooting

### Audio Issues
- Ensure your system's audio is working properly
- Check that the audio files are not corrupted
- Try different audio formats (WAV, FLAC) if MP3 doesn't work

### Installation Issues
- Make sure you have the correct Python version
- Install system dependencies for PyAudio if needed
- On Linux, you might need to install additional audio libraries

### Performance Issues
- Use the basic version for simpler needs
- Close other audio applications
- Ensure sufficient system resources

## Supported Audio Formats

- MP3 (.mp3)
- WAV (.wav)
- FLAC (.flac)
- OGG (.ogg)

## System Requirements

- **OS**: Windows, macOS, or Linux
- **Python**: 3.7 or higher
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 100MB free space
- **Audio**: Working audio output device

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application.
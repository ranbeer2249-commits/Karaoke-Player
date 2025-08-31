#!/bin/bash

echo "Installing Dual MP3 Player Dependencies..."
echo "=========================================="

# Check if running on Linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Detected Linux system"
    
    # Update package list
    echo "Updating package list..."
    sudo apt-get update
    
    # Install system dependencies
    echo "Installing system dependencies..."
    sudo apt-get install -y python3-dev portaudio19-dev python3-pyaudio
    
    # Install Python dependencies
    echo "Installing Python dependencies..."
    pip3 install -r requirements.txt
    
    echo "Installation complete!"
    echo "You can now run the application with:"
    echo "  python3 main.py          # Basic version"
    echo "  python3 advanced_player.py # Advanced version"
    
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS system"
    echo "Please install dependencies manually:"
    echo "1. Install Homebrew if not already installed"
    echo "2. Run: brew install portaudio"
    echo "3. Run: pip3 install -r requirements.txt"
    
else
    echo "Unsupported operating system"
    echo "Please install dependencies manually according to the README"
fi
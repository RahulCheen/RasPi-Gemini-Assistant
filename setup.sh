#!/bin/bash

# Exit on error
set -e

echo "Starting setup..."

# Update and install system dependencies
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y libasound2-dev portaudio19-dev ffmpeg python3-venv python3-pip wget

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install Python requirements
echo "Installing Python dependencies..."
pip install -r requirements.txt


# Pre-download openwakeword models
echo "Downloading openWakeWord models..."
python3 -c "import openwakeword; openwakeword.utils.download_models(['hey_jarvis'])"

echo "Setup complete!"
echo "1. Edit config.json and add your Gemini API Key."
echo "2. Run the assistant with: source venv/bin/activate && python main.py"

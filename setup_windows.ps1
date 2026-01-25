# Check for Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found $pythonVersion"
} catch {
    Write-Error "Python not found. Please install Python 3.10+ and add it to PATH."
    exit 1
}

# Create Virtual Environment
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

# Activate Venv
Write-Host "Activating virtual environment..."
& .\venv\Scripts\Activate.ps1

# Install Dependencies
Write-Host "Installing dependencies..."
pip install -r requirements.txt


# Pre-download wake word models
Write-Host "Downloading openWakeWord models..."
python -c "import openwakeword; openwakeword.utils.download_models(['hey_jarvis'])"

Write-Host "Setup complete!"
Write-Host "1. Edit config.json and add your Gemini API Key."
Write-Host "2. Run with: .\venv\Scripts\python.exe main.py"

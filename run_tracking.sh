#!/bin/bash
# Startup script for Gaze Tracking System
# Automatically uses the correct virtual environment

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Setting it up..."
    # Try to find python3.11, fallback to python3
    if command -v python3.11 &> /dev/null; then
        PYTHON_CMD="python3.11"
    else
        PYTHON_CMD="python3"
    fi
    echo "Using python: $PYTHON_CMD"
    $PYTHON_CMD -m venv venv
    ./venv/bin/pip install -r requirements.txt
fi

echo "Starting Gaze Tracking System (MediaPipe)..."
./venv/bin/python main.py --mode gui

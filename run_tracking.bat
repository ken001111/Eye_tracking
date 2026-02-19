@echo off
REM Startup script for Gaze Tracking System (Windows)

cd /d "%~dp0"

if not exist venv (
    echo Virtual environment not found. Setting it up...
    python -m venv venv
    venv\Scripts\pip install -r requirements.txt
)

echo Starting Gaze Tracking System (MediaPipe)...
venv\Scripts\python main.py --mode gui

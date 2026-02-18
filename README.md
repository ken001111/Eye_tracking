# Real-Time Eye Tracking Pipeline

A modular real-time eye tracking pipeline designed for behavioral and clinical research. The system supports multiple ML and non-ML tracking methods and enables high-precision timestamped data export for synchronization with physiological signals (e.g., EEG, EMG, TMS-EEG).

## 🎥 Demo


https://github.com/user-attachments/assets/1a2c9992-02c6-429d-b597-5c0acc8bcc18



## Key Features
*   **Real-Time Tracking**: Hybrid MediaPipe + OpenCV pipeline (Processing at ~30+ FPS).
*   **Visual Safety Alarm**: Prominent **"FACE NOT DETECTED"** warning banner on the video feed if the participant moves out of frame.
*   **Data Export**: Automatic CSV logging with microsecond timestamps.

## Quick Start

Run the system with a single command (handles venv & dependencies automatically):

```bash
./run_tracking.sh
```

## 💻 Installation on a New Machine
1.  **Copy this folder** to the new computer.
2.  **Install Python** (3.10+).
3.  Open Terminal, `cd` into the folder, and run:
    ```bash
    ./run_tracking.sh
    ```
    (This script automatically sets up the virtual environment and installs all dependencies including `mediapipe`, `opencv`, `Pillow`, and `pygame`).

## System Pipeline

The system processes every frame in 5 steps:

1.  **Input**: Webcam capture (OpenCV).
2.  **Face/Landmarks**: MediaPipe Face Mesh (468 landmarks) for robust head pose & eye ROI.
3.  **Eye Processing**: Bilateral filtering + Adaptive thresholding to isolate pupil from iris/sclera.
4.  **Feature Extraction**:
    *   **Pupil**: Ellipse fitting for sub-pixel diameter accuracy.
    *   **Blink**: Eye Aspect Ratio (EAR) < 0.22.
    *   **Drowsiness**: PERCLOS (Percentage of Eyelid Closure).
5.  **Output**: Data logged to `recording_output/*.csv` with microsecond timestamps.

## File Structure

| File | Description |
|------|-------------|
| `main.py` | Entry point. |
| `gui_app.py` | GUI (Tkinter) for visualization & control. |
| `core.py` | Central class orchestrating detection logic. |
| `pupil.py` | Image processing algorithms for pupil detection. |
| `eye.py` | Eye object holding pupil/blink state. |
| `data_logger.py` | Thread-safe CSV logging to `recording_output/`. |
| `safety_monitor.py` | Drowsiness & distraction logic. |
| `trackers/*.py` | Modular tracker backends (currently MediaPipe). |

## Data Export

CSVs are saved to `recording_output/` and contain:
`timestamp`, `tracker_method`, `left/right_pupil_x_y`, `left/right_pupil_diameter`, `eye_state`, `face_detected`.

## Authors
**Jongseo Ken Lee** ([@ken001111](https://github.com/ken001111)) for **Stanford Eye Tracking Project (2026)**.

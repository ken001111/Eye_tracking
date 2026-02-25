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
1.  **Copy this folder** git clone "https://github.com/ken001111/Eye_tracking.git"
2. Make a virtual environment and install dependencies.
    *   **Install Python** (python 3.11 recommended for this project).
    *   **macOS / Linux**:
        ```bash
        python3.11 -m venv venv 
        source venv/bin/activate
        pip install -r requirements.txt
        ```
    *   **Windows**:
        ```cmd
        python3.11 -m venv venv
        venv\Scripts\activate
        pip install -r requirements.txt
        ```
3.  Open Terminal, `cd` into the folder, and run the startup script for your OS:
    *   **macOS / Linux**:
        ```bash
        ./run_tracking.sh
        ```
    *   **Windows**:
        ```cmd
        run_tracking.bat
        ```
    (These scripts automatically set up the virtual environment using Python 3.11 and install all dependencies including `mediapipe`, `opencv`, `Pillow`, and `pygame`).

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

CSVs are saved to `recording_output/` and contain high-precision timing, pupil geometries, and landmark-normalized coordinates.

| Column | Description |
|--------|-------------|
| `timestamp` | Datetime down to microsecond precision. |
| `frame_idx` | Sequential frame counter from the webcam feed. |
| `tracker_method` | The backend tracker used (e.g. `mediapipe`). |
| `left_pupil_x`/`y`, `right_pupil_x`/`y` | Absolute pixel coordinates of the pupil center. |
| `left_pupil_diameter`, `right_pupil_diameter` | Estimated pupil diameter in pixels (sub-pixel accuracy). |
| `x_norm_L`/`y_norm_L`, `x_norm_R`/`y_norm_R` | Landmark-normalized coordinates of the pupil within the defined eye geometry. |
| `valid_L`, `valid_R` | Binary flag (1/0) indicating if the eye's normalized coordinates were safely calculated. |
| `left_eye_state`, `right_eye_state` | Binary flag (1 = Open, 0 = Closed or Blinking) based on Eye Aspect Ratio (EAR < 0.22). |
| `face_detected` | Boolean indicating if a face is currently tracked in the webcam area. |

## Authors
**Jongseo Ken Lee** ([@ken001111](https://github.com/ken001111)) for **Stanford PNT Lab Eye Tracking Project (2026)**.

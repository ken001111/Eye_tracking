# Gaze Tracking System

A modular, real-time eye tracking system using OpenCV with support for multiple tracking methods (ML and non-ML). Designed for clinical research applications with EEG/TEP/EMG data correlation.

## Features

- **Multiple Tracking Methods**: Support for OpenCV DNN (ML), Haar Cascade (non-ML), and Hybrid approaches
- **Real-time Performance**: Target 100Hz processing (minimum 50Hz)
- **Advanced Metrics**: Pupil diameter, eye state classification (independent per eye)
- **Safety Monitoring**: Out-of-frame detection
- **Data Export**: CSV export with high-precision timestamps for correlation with other data
- **GUI Application**: User-friendly interface with real-time visualization
- **Modular Architecture**: Easy to extend with new tracking methods

---

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Webcam
- OpenCV 4.8.0 or higher

### Easy Start (Recommended)
Use the provided shell script to automatically handle dependencies and run the app:

```bash
./run_tracking.sh
```

### Manual Installation

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the GUI**
   ```bash
   python gui_app.py
   ```

---

## Usage

### GUI Controls
- **Start/Stop Tracking**: Activates the camera and tracking algorithms.
- **Start/Stop Recording**: Logs data to CSV.
  - Files are automatically saved to the `recording_output/` folder.
  - Filename format: `gaze_tracking_data_YYYYMMDD_HHMMSS.csv`

### Data Export Format
The system exports a CSV file with the following columns:

| Column | Description |
|--------|-------------|
| `timestamp` | High-precision timestamp (microsecond accuracy) |
| `tracker_method` | Method used ('dnn', 'haar', 'hybrid') |
| `left_pupil_x`, `y` | Left pupil coordinates |
| `right_pupil_x`, `y` | Right pupil coordinates |
| `left_pupil_diameter` | Diameter in pixels |
| `right_pupil_diameter` | Diameter in pixels |
| `eye_state` | 1 = Open, 0 = Closed |
| `face_detected` | True/False |

---

## Accuracy & Optimization

### 1. Calibration
The system performs auto-calibration during the first 20 frames.
- **Distance**: Maintain 20-30 inches from the camera.
- **Lighting**: Ensure even, front-facing lighting. Avoid strong backlighting.
- **Positon**: Keep head relatively still during the first few seconds of tracking.

### 2. Tracker Methods

| Method | Type | Accuracy | Speed | Use Case |
|--------|------|----------|-------|----------|
| **MediaPipe** | ML | High | Fast | **Default**, best balance of accuracy and speed |
| **OpenCV DNN** | DL | High | Medium | Good fallback for older machines |
| **Haar** | CPU | Low | Fast | Use only on very low-end hardware |

### 3. Improving Results
- **Camera Position**: Mount camera at eye level.
- **Reflections**: If wearing glasses, try to minimize screen reflection on the lenses.
- **Resolution**: Lower resolution (640x480) yields higher FPS without significant accuracy loss.

---

## Architecture

The system uses a modular architecture:

```
gaze_tracking/
├── trackers/
│   ├── base_tracker.py       # Abstract base class
│   └── mediapipe_tracker.py  # MediaPipe-based tracker
├── gaze_tracking.py          # Main API
├── eye.py                    # Eye detection
├── pupil.py                  # Pupil detection with diameter
├── safety_monitor.py         # Safety features (blinks, etc.)
├── data_logger.py            # CSV export logic
└── performance_monitor.py    # FPS tracking
```

---

## System Pipeline

The system follows a strict 5-step processing pipeline for every frame:

1.  **Input Acquisition**
    -   Captures raw video frames from the webcam via OpenCV.

2.  **Face & Landmark Detection**
    -   **Engine**: MediaPipe Face Mesh.
    -   **Output**: 468 3D facial landmarks.
    -   **Role**: Provides robust head pose estimation and precise eye region coordinates, even with head rotation.

3.  **Eye Region Processing**
    -   **ROI Extraction**: Cuts out the eye regions based on specific landmark indices.
    -   **Preprocessing**:
        -   *Bilateral Filtering*: smooths skin texture while preserving pupil edges.
        -   *Adaptive Thresholding*: dynamically separates the dark pupil from the iris/sclera, handling uneven lighting.
        -   *Morphological Ops*: cleans up noise and small gaps.

4.  **Feature Extraction**
    -   **Pupil**: Finds the largest contour in the thresholded eye region and fits an ellipse to calculate the exact center and diameter (in pixels).
    -   **Blinks**: Calculates Eye Aspect Ratio (EAR). If EAR < 0.22, it counts as a blink.
    -   **Drowsiness**: Monitors PERCLOS (Percentage of Eyelid Closure) over a sliding window.

5.  **Data Output**
    -   Syncs all metrics with a microsecond-precision timestamp.
    -   Logs data to `recording_output/` as a CSV file.

---

## File Structure

Here is a quick overview of the Python files in the repository:

| File | Description |
|------|-------------|
| **`main.py`** | Entry point. Handles command-line arguments and launches the system. |
| **`gui_app.py`** | The graphical user interface (Tkinter). Handles the window, buttons, value display, and video feed. |
| **`core.py`** | Contains the `GazeTracking` class. This is the central brain that orchestrates face detection, eye processing, and data collection. |
| **`config.py`** | Central configuration file. Contains constants for thresholds, colors, and camera settings. |
| **`pupil.py`** | Handles the image processing algorithms to find the pupil within an eye region (filtering, thresholding, contour detection). |
| **`eye.py`** | Represents a single eye. Stores the pupil object, coordinates, and blinking state. |
| **`calibration.py`** | Manages the initial calibration phase to adapt thresholds to the user's lighting. |
| **`data_logger.py`** | Handles thread-safe CSV logging. Creates `recording_output/` and saves data. |
| **`safety_monitor.py`** | Analyzes tracking data over time to detect drowsiness (PERCLOS) or distraction. |
| **`performance_monitor.py`** | Tracks system metrics like FPS and processing latency. |
| **`trackers/`** | Directory containing the tracker implementations. |
| ↳ `mediapipe_tracker.py` | Implementation using Google MediaPipe Face Mesh (468 landmarks). |
| ↳ `base_tracker.py` | Abstract interface that all trackers must adhere to. |

---

## Authors & Acknowledgments

**Primary Developer**: Jongseo Ken Lee
- Email: jongseo001111@gmail.com
- GitHub: [@ken001111](https://github.com/ken001111)

**Project Information**:
Developed for the **Stanford Eye Tracking Project (2026)**.

**Acknowledgments**:
- OpenCV (Computer Vision)
- MediaPipe (Face Mesh)
- NumPy, Pandas, Pillow

---

## License
MIT License - See LICENSE file for details.

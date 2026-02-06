# Gaze Tracking System (Stanford Eye Tracking Project)

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

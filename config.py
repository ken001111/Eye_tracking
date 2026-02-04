"""
Configuration file for gaze tracking system.
Contains all configurable parameters.
"""

# Tracker Configuration
DEFAULT_TRACKER = 'dnn'  # Options: 'dnn', 'haar', 'hybrid'
TRACKER_MODEL_DIR = None  # None = use default locations

# Performance Settings
TARGET_FPS = 100.0  # Target frames per second
MIN_FPS = 50.0  # Minimum acceptable FPS
FPS_WINDOW_SIZE = 30  # Number of frames to average for FPS

# Distance Validation
DISTANCE_RANGE_INCHES = (20.0, 30.0)  # Valid distance range (min, max)

# Safety Monitor Settings
OUT_OF_FRAME_THRESHOLD = 5  # Consecutive frames without face to trigger alarm
PERCLOS_THRESHOLD = 0.7  # PERCLOS threshold for drowsiness (0.0-1.0) - increased to reduce false alarms
BLINK_FREQUENCY_THRESHOLD = 0.05  # Minimum blinks per second (reduced threshold)
DROWSINESS_WINDOW_SIZE = 120  # Frames to analyze for PERCLOS (increased for more stable measurement)
DROWSINESS_SUSTAINED_SECONDS = 3.0  # Must be drowsy for this many seconds before alarm
DROWSINESS_ALARM_COOLDOWN = 10.0  # Seconds to wait before allowing another alarm

# Alarm Settings
ENABLE_AUDIO_ALARMS = True
ENABLE_VISUAL_ALARMS = True

# Data Logging Settings
DATA_LOG_BUFFER_SIZE = 100  # Number of records to buffer before writing
DATA_LOG_AUTO_FLUSH = True  # Automatically flush buffer when full
DATA_LOG_DIR = "logs"  # Directory for log files

# GUI Settings
GUI_UPDATE_RATE = 30  # GUI update rate in Hz (lower than processing rate)
GUI_SHOW_ANNOTATIONS = True  # Show face boxes, pupils, etc.
GUI_SHOW_METRICS = True  # Show performance metrics

# Calibration Settings
CALIBRATION_FRAMES = 20  # Number of frames for calibration

# Pupil Detection Settings
PUPIL_DETECTION_THRESHOLD = 50  # Default threshold (will be calibrated)
PUPIL_DIAMETER_METHOD = 'average'  # 'average', 'circle', 'ellipse', 'box'

# Eye State Detection Settings
EAR_THRESHOLD = 0.05  # Eye Aspect Ratio threshold for open eye (very low = very permissive)
EAR_THRESHOLD_CLOSED = 0.02  # Threshold below which eye is definitely closed (extremely low to reduce false positives)
USE_TRACKER_EYE_STATE = False  # Disable tracker eye state (it's causing false positives)
USE_MULTI_METHOD_DETECTION = False  # Disable multi-method to reduce false positives (use only EAR)
HISTOGRAM_THRESHOLD = 0.2  # Histogram variance threshold for closed eye (lower = less sensitive)
CONTOUR_AREA_THRESHOLD = 0.05  # Minimum contour area ratio for open eye (lower = less sensitive)

# Webcam Settings
WEBCAM_INDEX = 0  # Default webcam index
WEBCAM_WIDTH = 640  # Desired width
WEBCAM_HEIGHT = 480  # Desired height
WEBCAM_FPS = 30  # Desired FPS (may not be achievable)

# Export Settings
CSV_EXPORT_ENABLED = True
CSV_EXPORT_DIR = "exports"  # Directory for CSV exports

# Debug Settings
DEBUG_MODE = False  # Enable debug output
VERBOSE_LOGGING = False  # Enable verbose logging

"""
Enhanced GazeTracking class using modular tracker backends.
Supports multiple tracking methods (DNN, Haar, Hybrid) via unified API.
"""

from __future__ import division
import cv2
import math
import numpy as np
from eye import Eye
from calibration import Calibration
from trackers import create_tracker, BaseTracker


class GazeTracking(object):
    """
    This class tracks the user's gaze using modular tracker backends.
    It provides useful information like the position of the eyes
    and pupils and allows to know if the eyes are open or closed.
    Enhanced with pupil diameter and face detection.
    """

    def __init__(self, tracker_type='dnn', tracker=None):
        """
        Initialize GazeTracking.
        
        Args:
            tracker_type: Type of tracker ('dnn', 'haar', 'hybrid'). Default: 'dnn'
            tracker: Optional pre-initialized tracker instance
        """
        self.frame = None
        self.eye_left = None
        self.eye_right = None
        self.calibration = Calibration()
        self.face_bbox = None
        self.face_detected = False
        
        # Initialize tracker
        if tracker is not None:
            if not isinstance(tracker, BaseTracker):
                raise ValueError("Tracker must be an instance of BaseTracker")
            self.tracker = tracker
        else:
            self.tracker = create_tracker(tracker_type)
        
        self.tracker_type = tracker_type

    @property
    def pupils_located(self):
        """Check that the pupils have been located"""
        try:
            if self.eye_left is None or self.eye_right is None:
                return False
            if self.eye_left.pupil is None or self.eye_right.pupil is None:
                return False
            if self.eye_left.pupil.x is None or self.eye_left.pupil.y is None:
                return False
            if self.eye_right.pupil.x is None or self.eye_right.pupil.y is None:
                return False
            return True
        except Exception:
            return False

    def _analyze(self):
        """Detects the face and initialize Eye objects using the tracker"""
        if self.frame is None:
            self.eye_left = None
            self.eye_right = None
            self.face_detected = False
            return
        
        # Detect face
        self.face_bbox = self.tracker.detect_face(self.frame)
        self.face_detected = self.face_bbox is not None
        
        if not self.face_detected:
            self.eye_left = None
            self.eye_right = None
            return
        
        # Detect eyes
        eyes = self.tracker.detect_eyes(self.frame, self.face_bbox)
        
        # Initialize Eye objects
        try:
            # Left eye
            left_eye_region = eyes.get('left_eye')
            if left_eye_region is not None and left_eye_region.size > 0:
                left_coords = self.tracker.get_eye_region_coords(self.face_bbox, 'left')
                try:
                    self.eye_left = Eye(
                        self.frame,
                        eye_region=left_eye_region,
                        side=0,
                        calibration=self.calibration,
                        eye_coords=left_coords
                    )
                except Exception as e:
                    # If Eye initialization fails, try with just coordinates
                    self.eye_left = None
            else:
                # Fallback: use region-based detection
                left_coords = self.tracker.get_eye_region_coords(self.face_bbox, 'left')
                left_eye_region = self.tracker.extract_eye_region(self.frame, left_coords)
                if left_eye_region is not None and left_eye_region.size > 0:
                    try:
                        self.eye_left = Eye(
                            self.frame,
                            eye_region=left_eye_region,
                            side=0,
                            calibration=self.calibration,
                            eye_coords=left_coords
                        )
                    except:
                        self.eye_left = None
                else:
                    self.eye_left = None
            
            # Right eye
            right_eye_region = eyes.get('right_eye')
            if right_eye_region is not None and right_eye_region.size > 0:
                right_coords = self.tracker.get_eye_region_coords(self.face_bbox, 'right')
                try:
                    self.eye_right = Eye(
                        self.frame,
                        eye_region=right_eye_region,
                        side=1,
                        calibration=self.calibration,
                        eye_coords=right_coords
                    )
                except Exception as e:
                    self.eye_right = None
            else:
                # Fallback: use region-based detection
                right_coords = self.tracker.get_eye_region_coords(self.face_bbox, 'right')
                right_eye_region = self.tracker.extract_eye_region(self.frame, right_coords)
                if right_eye_region is not None and right_eye_region.size > 0:
                    try:
                        self.eye_right = Eye(
                            self.frame,
                            eye_region=right_eye_region,
                            side=1,
                            calibration=self.calibration,
                            eye_coords=right_coords
                        )
                    except:
                        self.eye_right = None
                else:
                    self.eye_right = None
        except Exception as e:
            # Silent fail - don't print errors in production
            self.eye_left = None
            self.eye_right = None

    def refresh(self, frame):
        """Refreshes the frame and analyzes it.

        Arguments:
            frame (numpy.ndarray): The frame to analyze
        """
        self.frame = frame
        self._analyze()

    def is_face_detected(self):
        """Returns True if a face is detected in the current frame"""
        return self.face_detected

    def pupil_left_coords(self):
        """Returns the coordinates of the left pupil"""
        if self.pupils_located:
            x = self.eye_left.origin[0] + self.eye_left.pupil.x
            y = self.eye_left.origin[1] + self.eye_left.pupil.y
            return (x, y)
        return None

    def pupil_right_coords(self):
        """Returns the coordinates of the right pupil"""
        if self.pupils_located:
            x = self.eye_right.origin[0] + self.eye_right.pupil.x
            y = self.eye_right.origin[1] + self.eye_right.pupil.y
            return (x, y)
        return None

    def pupil_left_diameter(self):
        """Returns the diameter of the left pupil in pixels"""
        if self.pupils_located and self.eye_left.pupil.diameter is not None:
            return self.eye_left.pupil.diameter
        return None

    def pupil_right_diameter(self):
        """Returns the diameter of the right pupil in pixels"""
        if self.pupils_located and self.eye_right.pupil.diameter is not None:
            return self.eye_right.pupil.diameter
        return None

    def pupil_diameter(self):
        """Returns the average diameter of both pupils in pixels"""
        left_d = self.pupil_left_diameter()
        right_d = self.pupil_right_diameter()
        
        if left_d is not None and right_d is not None:
            return (left_d + right_d) / 2.0
        elif left_d is not None:
            return left_d
        elif right_d is not None:
            return right_d
        return None


    def _get_eye_region_frame(self, eye_obj):
        """Extract eye region frame from Eye object for tracker analysis"""
        if eye_obj is None or eye_obj.frame is None:
            return None
        return eye_obj.frame
    
    def _detect_eye_state_advanced(self, eye_frame):
        """
        Advanced eye state detection using multiple methods.
        Assumes eye is OPEN unless proven closed (conservative approach).
        
        Args:
            eye_frame: Grayscale eye region
            
        Returns:
            1 for open, 0 for closed
        """
        if eye_frame is None or eye_frame.size == 0:
            return 1  # Assume open if no frame
        
        import config
        
        # Method 1: Use tracker's get_eye_state (only if enabled)
        if config.USE_TRACKER_EYE_STATE:
            try:
                tracker_state = self.tracker.get_eye_state(eye_frame)
                if tracker_state is not None:
                    # Only trust tracker if it says closed (be very conservative)
                    if tracker_state == 0:
                        # Double-check with EAR before declaring closed
                        ear = self._calculate_improved_ear(eye_frame)
                        if ear is not None and ear < config.EAR_THRESHOLD_CLOSED:
                            return 0
                    # If tracker says open, trust it
                    return tracker_state
            except Exception:
                pass
        
        # Method 2: Improved EAR calculation (primary method)
        ear = self._calculate_improved_ear(eye_frame)
        if ear is not None:
            # Extremely conservative: only declare closed if EAR is extremely low
            # Most eyes will have EAR > 0.02, so this should rarely trigger false closes
            if ear < config.EAR_THRESHOLD_CLOSED:
                return 0  # Definitely closed (only if EAR is extremely low)
            # Otherwise always assume open (very permissive)
            return 1
        
        # Method 3: Histogram analysis (only if multi-method enabled)
        if config.USE_MULTI_METHOD_DETECTION:
            hist_variance = np.var(eye_frame)
            hist_max = np.max(eye_frame)
            if hist_max > 0:
                hist_normalized = hist_variance / (hist_max + 1e-6)
                
                # Only use histogram if it strongly suggests closed AND EAR confirms
                if hist_normalized < config.HISTOGRAM_THRESHOLD:
                    if ear is not None and ear < config.EAR_THRESHOLD_CLOSED:
                        return 0
        
        # Method 4: Contour analysis (only if multi-method enabled)
        if config.USE_MULTI_METHOD_DETECTION:
            try:
                _, thresh = cv2.threshold(eye_frame, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                if contours:
                    total_area = sum(cv2.contourArea(c) for c in contours)
                    frame_area = eye_frame.shape[0] * eye_frame.shape[1]
                    area_ratio = total_area / frame_area if frame_area > 0 else 0
                    
                    # Only use contour if it strongly suggests closed AND EAR confirms
                    if area_ratio < config.CONTOUR_AREA_THRESHOLD:
                        if ear is not None and ear < config.EAR_THRESHOLD_CLOSED:
                            return 0
            except Exception:
                pass
        
        # Default: assume open (conservative - only declare closed with strong evidence)
        return 1
    
    def _calculate_improved_ear(self, eye_frame):
        """
        Improved EAR calculation using better image processing.
        
        Args:
            eye_frame: Grayscale eye region
            
        Returns:
            EAR value or None
        """
        if eye_frame is None or eye_frame.size == 0:
            return None
        
        h, w = eye_frame.shape[:2]
        if w == 0 or h == 0:
            return None
        
        # Use horizontal projection to find eye opening
        # Closed eyes have less variation in the middle horizontal region
        horizontal_projection = np.sum(eye_frame, axis=1)
        
        # Find the region with maximum variation (where eye opens)
        # For open eyes, there should be a clear valley in the middle
        mid_h = h // 2
        top_region = horizontal_projection[:mid_h]
        bottom_region = horizontal_projection[mid_h:]
        
        if len(top_region) == 0 or len(bottom_region) == 0:
            return None
        
        # Calculate vertical distance (eye opening)
        top_max = np.max(top_region)
        bottom_max = np.max(bottom_region)
        vertical_dist = abs(top_max - bottom_max) / (np.mean(horizontal_projection) + 1e-6)
        
        # Horizontal distance is the width
        horizontal_dist = w
        
        if horizontal_dist == 0:
            return None
        
        # Improved EAR: accounts for actual eye opening
        ear = vertical_dist / (2.0 * horizontal_dist)
        
        # Normalize based on frame size
        ear = ear * (h / w)  # Adjust for aspect ratio
        
        return ear
    
    def left_eye_state(self):
        """
        Get left eye state independently.
        Very permissive - defaults to open unless strongly proven closed.
        
        Returns:
            1 for open, 0 for closed
        """
        # If pupil is detected, eye is almost certainly open
        if self.pupils_located and self.eye_left is not None and self.eye_left.pupil is not None:
            if self.eye_left.pupil.x is not None and self.eye_left.pupil.y is not None:
                return 1  # Pupil detected = eye is open
        
        left_frame = self._get_eye_region_frame(self.eye_left)
        if left_frame is not None:
            return self._detect_eye_state_advanced(left_frame)
        
        # Default to open (very permissive)
        return 1
    
    def right_eye_state(self):
        """
        Get right eye state independently.
        Very permissive - defaults to open unless strongly proven closed.
        
        Returns:
            1 for open, 0 for closed
        """
        # If pupil is detected, eye is almost certainly open
        if self.pupils_located and self.eye_right is not None and self.eye_right.pupil is not None:
            if self.eye_right.pupil.x is not None and self.eye_right.pupil.y is not None:
                return 1  # Pupil detected = eye is open
        
        right_frame = self._get_eye_region_frame(self.eye_right)
        if right_frame is not None:
            return self._detect_eye_state_advanced(right_frame)
        
        # Default to open (very permissive)
        return 1
    
    def is_blinking(self):
        """
        Returns true if the user closes his eyes (binary classification).
        Eye is considered closed if EITHER eye is closed (more sensitive).
        """
        left_state = self.left_eye_state()
        right_state = self.right_eye_state()
        
        # Eye is closed if EITHER eye is closed (more sensitive and accurate)
        return (left_state == 0) or (right_state == 0)

    def eye_state(self):
        """
        Get binary eye state classification.
        
        Returns:
            1 for open, 0 for closed
        """
        return 0 if self.is_blinking() else 1

    def eye_left_center(self):
        """Returns the center coordinates of the left eye region"""
        if self.eye_left is not None and self.eye_left.origin is not None:
            x = self.eye_left.origin[0] + self.eye_left.center[0]
            y = self.eye_left.origin[1] + self.eye_left.center[1]
            return (int(x), int(y))
        return None

    def eye_right_center(self):
        """Returns the center coordinates of the right eye region"""
        if self.eye_right is not None and self.eye_right.origin is not None:
            x = self.eye_right.origin[0] + self.eye_right.center[0]
            y = self.eye_right.origin[1] + self.eye_right.center[1]
            return (int(x), int(y))
        return None

    def annotated_frame(self):
        """Returns the main frame with pupils highlighted and annotations"""
        frame = self.frame.copy() if self.frame is not None else None
        
        if frame is None:
            return None

        # Draw eye center dots (yellow)
        if self.eye_left is not None and self.eye_left.origin is not None:
            center = self.eye_left_center()
            if center:
                cv2.circle(frame, center, 3, (255, 255, 0), -1)
        
        if self.eye_right is not None and self.eye_right.origin is not None:
            center = self.eye_right_center()
            if center:
                cv2.circle(frame, center, 3, (255, 255, 0), -1)

        # Draw pupils in green (only circles, no rectangles)
        if self.pupils_located:
            color = (0, 255, 0)  # Green in BGR
            x_left, y_left = self.pupil_left_coords()
            x_right, y_right = self.pupil_right_coords()
            
            # Only draw pupils if eyes are open - just circles, no crosshairs
            if x_left is not None and y_left is not None and self.left_eye_state() == 1:
                # Draw circle for pupil only
                if self.eye_left.pupil.diameter is not None and self.eye_left.pupil.diameter > 0:
                    radius = max(3, int(self.eye_left.pupil.diameter / 2))
                    cv2.circle(frame, (x_left, y_left), radius, color, 2)
                else:
                    # Default circle if diameter not available
                    cv2.circle(frame, (x_left, y_left), 5, color, 2)
            
            if x_right is not None and y_right is not None and self.right_eye_state() == 1:
                # Draw circle for pupil only
                if self.eye_right.pupil.diameter is not None and self.eye_right.pupil.diameter > 0:
                    radius = max(3, int(self.eye_right.pupil.diameter / 2))
                    cv2.circle(frame, (x_right, y_right), radius, color, 2)
                else:
                    # Default circle if diameter not available
                    cv2.circle(frame, (x_right, y_right), 5, color, 2)

        return frame

    def switch_tracker(self, tracker_type):
        """
        Switch to a different tracker method.
        
        Args:
            tracker_type: Type of tracker ('dnn', 'haar', 'hybrid')
        """
        self.tracker = create_tracker(tracker_type)
        self.tracker_type = tracker_type

"""
MediaPipe Face Mesh tracker implementation.
Provides high-accuracy facial landmark detection (468 points).
"""

import cv2
import numpy as np
import mediapipe as mp
from typing import Tuple, Optional, Dict
from trackers.base_tracker import BaseTracker


class MediaPipeTracker(BaseTracker):
    """
    Tracker implementation using MediaPipe Face Mesh.
    Provides 468 facial landmarks for high-accuracy eye region extraction.
    """
    
    # MediaPipe Face Mesh eye landmarks (indices)
    # Left eye indices
    LEFT_EYE_INDICES = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
    # Right eye indices
    RIGHT_EYE_INDICES = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
    
    # Iris indices (for pupil detection fallback)
    LEFT_IRIS = [468, 469, 470, 471, 472]
    RIGHT_IRIS = [473, 474, 475, 476, 477]

    def __init__(self, **kwargs):
        """Initialize MediaPipe tracker."""
        super().__init__()
        
        # Initialize MediaPipe Face Mesh
        # refine_landmarks=True enables iris landmarks
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.is_initialized = True
        self.current_landmarks = None
        
    def detect_face(self, frame: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect face using MediaPipe.
        Also runs full landmark detection and caches it.
        
        Args:
            frame: Input frame (BGR)
            
        Returns:
            Bounding box (x, y, w, h) or None
        """
        h, w = frame.shape[:2]
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            self.current_landmarks = None
            return None
        
        # Get first face
        face_landmarks = results.multi_face_landmarks[0]
        self.current_landmarks = face_landmarks
        
        # Create a bounding box from landmarks
        x_coords = [lm.x for lm in face_landmarks.landmark]
        y_coords = [lm.y for lm in face_landmarks.landmark]
        
        min_x = int(min(x_coords) * w)
        max_x = int(max(x_coords) * w)
        min_y = int(min(y_coords) * h)
        max_y = int(max(y_coords) * h)
        
        # Add some padding
        padding_x = int((max_x - min_x) * 0.1)
        padding_y = int((max_y - min_y) * 0.1)
        
        min_x = max(0, min_x - padding_x)
        min_y = max(0, min_y - padding_y)
        max_x = min(w, max_x + padding_x)
        max_y = min(h, max_y + padding_y)
        
        bbox = (min_x, min_y, max_x - min_x, max_y - min_y)
        return bbox

    def detect_eyes(self, frame: np.ndarray, face_bbox: Tuple[int, int, int, int]) -> Dict[str, Optional[np.ndarray]]:
        """
        Extract detailed eye regions using landmarks.
        Accuracy comes from using the polygon define by landmarks.
        """
        if self.current_landmarks is None:
            return {'left_eye': None, 'right_eye': None}
        
        h, w = frame.shape[:2]
        landmarks = self.current_landmarks.landmark
        
        def extract_eye_from_indices(indices):
            # Get points for the eye
            points = []
            for idx in indices:
                pt = landmarks[idx]
                points.append((int(pt.x * w), int(pt.y * h)))
            
            points = np.array(points, dtype=np.int32)
            
            # Create a mask for the eye polygon
            mask = np.zeros((h, w), dtype=np.uint8)
            cv2.fillPoly(mask, [points], 255)
            
            # Extract bounding box of the eye polygon for cropping
            x, y, ew, eh = cv2.boundingRect(points)
            
            # Add margin
            margin = 5
            x = max(0, x - margin)
            y = max(0, y - margin)
            ew = min(w - x, ew + 2 * margin)
            eh = min(h - y, eh + 2 * margin)
            
            # Crop the eye region
            eye_roi = frame[y:y+eh, x:x+ew]
            
            # Mask the ROI to only include the eye (blacking out skin/eyebrows)
            # This is what gives high accuracy - no eyebrow noise
            mask_roi = mask[y:y+eh, x:x+ew]
            eye_masked = cv2.bitwise_and(eye_roi, eye_roi, mask=mask_roi)
            
            # Make background gray instead of black to avoid high contrast edges
            # (optional, but can help some thresholding algos)
            
            return eye_masked

        left_eye_img = extract_eye_from_indices(self.LEFT_EYE_INDICES)
        right_eye_img = extract_eye_from_indices(self.RIGHT_EYE_INDICES)
        
        return {
            'left_eye': left_eye_img,
            'right_eye': right_eye_img
        }

    def detect_pupils(self, eye_frame: np.ndarray) -> Optional[Tuple[int, int]]:
        """
        Detect pupil in the masked eye frame.
        Since we have MediaPipe iris landmarks, we could use those directly,
        but for compatibility with the project's 'Pupil' class logic (thresholding),
        we'll return None here and let the core 'Pupil' class handle it if desired,
        OR we can implement a hybrid approach where we use MediaPipe's iris for coarse
        location and image processing for fine-tuning.
        
        For now, let's rely on the core Pupil class which uses our high-quality masked image.
        """
        # Return None to let the standard image processing pipeline handle it.
        # This keeps the behavior consistent with 'nice accuracy' repo which uses dlib + image processing.
        return None 

    def get_eye_state(self, eye_frame: np.ndarray, eye_side: str = 'left') -> Optional[int]:
        """
        Classify eye state using MediaPipe landmarks.
        Calculates Eye Aspect Ratio (EAR) from landmarks.
        """
        if self.current_landmarks is None:
            return None
            
        landmarks = self.current_landmarks.landmark
        
        # Define vertical landmark pairs for EAR calculation
        # These correspond to top/bottom eyelid points
        if eye_side == 'left':
            # Top-Bottom pairs for left eye
            vertical_pairs = [(159, 145), (158, 153)] 
            horizontal_pair = (133, 33) # Inner-Outer corners
        else:
            # Top-Bottom pairs for right eye
            vertical_pairs = [(386, 374), (385, 373)]
            horizontal_pair = (263, 362)
            
        # Calculate avg vertical distance
        v_dist = 0
        for top, bottom in vertical_pairs:
            p1 = landmarks[top]
            p2 = landmarks[bottom]
            dist = np.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)
            v_dist += dist
        v_dist /= len(vertical_pairs)
        
        # Calculate horizontal distance
        p_left = landmarks[horizontal_pair[0]]
        p_right = landmarks[horizontal_pair[1]]
        h_dist = np.sqrt((p_left.x - p_right.x)**2 + (p_left.y - p_right.y)**2)
        
        # Calculate EAR
        if h_dist == 0:
            return None
        ear = v_dist / h_dist
        
        # Threshold for blink detection
        # Typical EAR for open eye is > 0.25-0.3, closed is < 0.2
        EAR_THRESHOLD = 0.22
        
        return 1 if ear > EAR_THRESHOLD else 0

    def get_pupil_location(self, frame: np.ndarray, face_bbox: Tuple[int, int, int, int], eye_side: str) -> Optional[Tuple[int, int, float]]:
        """
        Calculate iris location and diameter using MediaPipe landmarks.
        """
        if self.current_landmarks is None:
            return None
            
        h, w = frame.shape[:2]
        landmarks = self.current_landmarks.landmark
        indices = self.LEFT_IRIS if eye_side == 'left' else self.RIGHT_IRIS
        
        # Get iris points
        try:
            points = []
            for idx in indices:
                pt = landmarks[idx]
                points.append((pt.x * w, pt.y * h))
        except IndexError:
            return None
        
        if not points:
            return None
            
        # Calculate centroid (pupil center)
        avg_x = sum(p[0] for p in points) / len(points)
        avg_y = sum(p[1] for p in points) / len(points)
        
        # Calculate diameter (average distance from center * 2)
        import config
        if config.USE_HYBRID_DIAMETER:
            # Return None for diameter to trigger hybrid calculation in Pupil class
            diameter = None
        else:
            # Use MediaPipe iris diameter
            radii = [np.sqrt((p[0] - avg_x)**2 + (p[1] - avg_y)**2) for p in points]
            diameter = sum(radii) / len(radii) * 2.0
        
        return (int(avg_x), int(avg_y), diameter)

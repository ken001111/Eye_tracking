import numpy as np
import cv2


class Pupil(object):
    """
    This class detects the iris of an eye and estimates
    the position of the pupil and calculates its diameter.
    """

    def __init__(self, eye_frame, threshold, x=None, y=None, diameter=None):
        self.iris_frame = None
        self.threshold = threshold
        self.x = x
        self.y = y
        self.diameter = diameter
        
        # If coordinates provided but no diameter, use hybrid method
        if self.x is not None and self.y is not None and self.diameter is None:
            self.measure_diameter_at_location(eye_frame, self.x, self.y)
        # If no coordinates provided, use full detection
        elif self.x is None or self.y is None:
            self.detect_iris(eye_frame)

    @staticmethod
    def image_processing(eye_frame, threshold):
        """Performs operations on the eye frame to isolate the iris.
        Improved to better separate pupil from eyebrow and shadows.

        Arguments:
            eye_frame (numpy.ndarray): Frame containing an eye and nothing else
            threshold (int): Threshold value used to binarize the eye frame

        Returns:
            A frame with a single element representing the iris
        """
        # Use adaptive thresholding instead of fixed threshold for better pupil isolation
        # This helps separate the dark pupil from other dark areas like eyebrows
        if eye_frame.size == 0:
            return eye_frame
        
        # Apply bilateral filter to reduce noise while preserving edges
        filtered = cv2.bilateralFilter(eye_frame, 9, 75, 75)
        
        # Use adaptive thresholding - better at handling varying lighting
        # This will make the pupil stand out more clearly
        adaptive_thresh = cv2.adaptiveThreshold(
            filtered, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Morphological operations to clean up
        kernel = np.ones((3, 3), np.uint8)
        # Close small gaps in the pupil
        new_frame = cv2.morphologyEx(adaptive_thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
        # Remove small noise
        new_frame = cv2.morphologyEx(new_frame, cv2.MORPH_OPEN, kernel, iterations=1)

        return new_frame

    def detect_iris(self, eye_frame):
        """Detects the iris and estimates the position of the iris by
        calculating the centroid. Also calculates the diameter.
        Improved to focus on center-lower region to avoid eyebrow detection.

        Arguments:
            eye_frame (numpy.ndarray): Frame containing an eye and nothing else
        """
        if eye_frame is None or eye_frame.size == 0:
            self.x = None
            self.y = None
            self.diameter = None
            return
        
        h, w = eye_frame.shape[:2]
        
        # Focus on the center-lower region of the eye (where pupil actually is)
        # Exclude top 40% (eyebrow/shadow area) and focus on lower 60% where pupil is
        top_margin = int(h * 0.4)  # Skip top 40% (eyebrow/shadow region)
        eye_roi = eye_frame[top_margin:, :]  # Region of interest (lower 60% where pupil is)
        
        # Process the ROI
        roi_processed = self.image_processing(eye_roi, self.threshold)
        
        # Find contours in the ROI
        contours, _ = cv2.findContours(roi_processed, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[-2:]
        
        if not contours:
            self.x = None
            self.y = None
            self.diameter = None
            return
        
        # Filter contours by:
        # 1. Size: pupil should be reasonable size (not too large/small)
        # 2. Position: should be in center-lower region
        # 3. Circularity: pupil should be somewhat circular
        
        valid_contours = []
        roi_h, roi_w = eye_roi.shape[:2]
        min_area = (roi_w * roi_h) * 0.01  # At least 1% of eye area
        max_area = (roi_w * roi_h) * 0.3   # At most 30% of eye area
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Filter by size
            if area < min_area or area > max_area:
                continue
            
            # Get centroid
            M = cv2.moments(contour)
            if M['m00'] == 0:
                continue
            
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            
            # Filter by position: should be in center region (not too far left/right)
            # Allow some margin on sides
            center_x = roi_w // 2
            if abs(cx - center_x) > roi_w * 0.4:  # Too far from center
                continue
            
            # Check circularity (pupil should be somewhat circular)
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue
            
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            if circularity < 0.3:  # Not circular enough
                continue
            
            valid_contours.append((contour, area, cx, cy))
        
        if not valid_contours:
            self.x = None
            self.y = None
            self.diameter = None
            return
        
        # Sort by area and position (prefer larger, more centered contours)
        # Weight: area (70%) + centrality (30%)
        def score_contour(contour_data):
            contour, area, cx, cy = contour_data
            center_x = roi_w // 2
            center_y = roi_h // 2
            centrality = 1.0 - (abs(cx - center_x) / (roi_w * 0.5) + abs(cy - center_y) / (roi_h * 0.5)) / 2.0
            centrality = max(0, centrality)  # Clamp to 0-1
            return area * 0.7 + centrality * max_area * 0.3
        
        valid_contours.sort(key=score_contour, reverse=True)
        
        # Get the best contour (pupil)
        pupil_contour, _, cx_roi, cy_roi = valid_contours[0]
        
        # Convert ROI coordinates back to full eye frame coordinates
        self.x = cx_roi
        self.y = cy_roi + top_margin  # Add back the top margin
        
        # Calculate diameter
        self.diameter = self.calculate_diameter(pupil_contour)
    
    def calculate_diameter(self, contour):
        """
        Calculate pupil diameter from contour using multiple methods.
        
        Arguments:
            contour: Contour of the pupil
            
        Returns:
            Diameter in pixels (average of multiple methods for accuracy)
        """
        if contour is None or len(contour) < 5:
            return None
        
        # Method 1: Using minimum enclosing circle
        (_, _), radius = cv2.minEnclosingCircle(contour)
        diameter_circle = radius * 2
        
        # Method 2: Using bounding box
        x, y, w, h = cv2.boundingRect(contour)
        diameter_box = max(w, h)
        
        # Method 3: Using area (assuming circular pupil)
        area = cv2.contourArea(contour)
        if area > 0:
            diameter_area = 2 * np.sqrt(area / np.pi)
        else:
            diameter_area = 0
        
        # Method 4: Using fitEllipse (most accurate for elliptical pupils)
        try:
            if len(contour) >= 5:
                ellipse = cv2.fitEllipse(contour)
                (_, _), (width, height), _ = ellipse
                diameter_ellipse = max(width, height)
            else:
                diameter_ellipse = diameter_circle
        except:
            diameter_ellipse = diameter_circle
        
        # Return average of all methods for robustness
        diameters = [d for d in [diameter_circle, diameter_box, diameter_area, diameter_ellipse] if d > 0]
        
        if len(diameters) > 0:
            return float(np.mean(diameters))
        
        return None

    def measure_diameter_at_location(self, eye_frame, target_x, target_y):
        """
        Measure pupil diameter around a known location (Hybrid approach).
        Uses image thresholding but focused on the tracker-provided coordinates.
        """
        if eye_frame is None or eye_frame.size == 0:
            return

        # Perform image processing
        processed = self.image_processing(eye_frame, self.threshold)
        
        # Find contours
        contours, _ = cv2.findContours(processed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return
            
        # Find the contour that best matches the target location
        best_contour = None
        min_dist = float('inf')
        
        for contour in contours:
            # Check if target point is inside contour
            dist = cv2.pointPolygonTest(contour, (target_x, target_y), True)
            
            if dist >= 0:
                best_contour = contour
                break
            else:
                if abs(dist) < min_dist:
                    min_dist = abs(dist)
                    closest_contour = contour
        
        # If no contour contained the point, use the closest one if it's very close
        if best_contour is None and min_dist < 5.0 and 'closest_contour' in locals():
            best_contour = closest_contour
            
        if best_contour is not None:
             self.diameter = self.calculate_diameter(best_contour)

"""
GUI application for real-time gaze tracking.
Uses tkinter for cross-platform compatibility.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageDraw, ImageFont
import threading
import time
from collections import deque
from core import GazeTracking
from safety_monitor import SafetyMonitor
from data_logger import DataLogger
from performance_monitor import PerformanceMonitor
import config


class GazeTrackingGUI:
    """
    Main GUI application for gaze tracking.
    """
    
    def __init__(self, root, tracker_type=None):
        """
        Initialize GUI.
        
        Args:
            root: Tkinter root window
            tracker_type: Override default tracker type
        """
        self.root = root
        self.tracker_type = tracker_type
        self.root.title("Gaze Tracking System")
        self.root.geometry("1200x800")
        
        # Initialize components
        self.gaze = None
        self.safety_monitor = None
        self.data_logger = None
        self.performance_monitor = None
        
        # Video capture
        self.cap = None
        self.is_running = False
        self.is_recording = False
        
        # GUI update
        self.update_thread = None
        
        # Diameter graph data (3-second window at ~30 FPS = ~90 data points)
        self.diameter_window_seconds = 3.0
        self.left_diameter_data = deque(maxlen=300)  # Store (timestamp, diameter) tuples
        self.right_diameter_data = deque(maxlen=300)
        self.last_left_diameter = None  # Last open diameter
        self.last_right_diameter = None
        
        # Create GUI
        self._create_widgets()
        
        # Initialize system
        self._initialize_system()
        
        # Auto-start webcam after a short delay (allows GUI to fully render)
        self.root.after(500, self._auto_start_webcam)

    
    def _initialize_system(self):
        """Initialize gaze tracking system"""
        try:
            # Use provided tracker type or fall back to config default
            tracker = self.tracker_type if self.tracker_type else config.DEFAULT_TRACKER
            self.gaze = GazeTracking(tracker_type=tracker)
            self.safety_monitor = SafetyMonitor(
                out_of_frame_threshold=config.OUT_OF_FRAME_THRESHOLD,
                perclos_threshold=config.PERCLOS_THRESHOLD,
                sustained_seconds=getattr(config, 'DROWSINESS_SUSTAINED_SECONDS', 3.0),
                alarm_cooldown=getattr(config, 'DROWSINESS_ALARM_COOLDOWN', 10.0),
                enable_audio=config.ENABLE_AUDIO_ALARMS,
                enable_visual=config.ENABLE_VISUAL_ALARMS
            )
            self.data_logger = DataLogger(
                buffer_size=config.DATA_LOG_BUFFER_SIZE,
                auto_flush=config.DATA_LOG_AUTO_FLUSH
            )
            self.performance_monitor = PerformanceMonitor(
                target_fps=config.TARGET_FPS,
                min_fps=config.MIN_FPS,
                distance_range=config.DISTANCE_RANGE_INCHES
            )
            self.status_label.config(text="System initialized - Starting webcam...", foreground="green")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize system: {e}")
            self.status_label.config(text="Initialization failed", foreground="red")


    
    def _create_widgets(self):
        """Create GUI widgets"""
        
        # Configure grid weights for Root
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1) # Main content
        self.root.rowconfigure(1, weight=0) # Bottom bar (fixed height)

        # Main container (Video + Metrics)
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for Main Frame
        main_frame.columnconfigure(0, weight=4) # Video (80%)
        main_frame.columnconfigure(1, weight=1) # Metrics (20%)
        main_frame.rowconfigure(0, weight=1)
        
        # Left panel: Video display
        video_frame = ttk.LabelFrame(main_frame, text="Video Feed", padding="5")
        video_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        self.video_label = ttk.Label(video_frame, text="No video feed")
        self.video_label.pack(expand=True, fill=tk.BOTH)
        
        # Right panel: Metrics Only (Controls moved to bottom)
        right_panel = ttk.Frame(main_frame)
        right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        right_panel.columnconfigure(0, weight=1)
        
        # --- BOTTOM ACTION BAR ---
        bottom_bar = ttk.Frame(self.root, padding="10")
        bottom_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        bottom_bar.columnconfigure(0, weight=1)
        bottom_bar.columnconfigure(1, weight=1)
        
        # Start/Stop Button
        self.start_stop_btn = ttk.Button(bottom_bar, text="Start Tracking", 
                                         command=self._toggle_tracking)
        self.start_stop_btn.grid(row=0, column=0, padx=5, sticky=(tk.W, tk.E), ipady=10)
        
        # Record Button (Middle, Big)
        self.record_btn = ttk.Button(bottom_bar, text="🔴 Start Recording", 
                                     command=self._toggle_recording, state=tk.DISABLED)
        self.record_btn.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E), ipady=10)
        
        # Metrics frame (Moved up since controls are gone)
        metrics_frame = ttk.LabelFrame(right_panel, text="Metrics", padding="10")
        metrics_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        metrics_frame.columnconfigure(1, weight=1)
        
        # Create metrics labels
        self.metrics_labels = {}
        metrics = [
            ("Left Eye Center:", "left_eye_center"),
            ("Right Eye Center:", "right_eye_center"),
            ("Left Eye State:", "left_eye_state"),
            ("Right Eye State:", "right_eye_state"),
            ("Face Detected:", "face_detected"),
        ]
        
        for i, (label_text, key) in enumerate(metrics):
            ttk.Label(metrics_frame, text=label_text).grid(row=i, column=0, sticky=tk.W, pady=2)
            value_label = ttk.Label(metrics_frame, text="N/A", foreground="blue")
            value_label.grid(row=i, column=1, sticky=tk.W, padx=40) # Increased spacing
            self.metrics_labels[key] = value_label
        
        # Diameter graphs frame
        graphs_frame = ttk.LabelFrame(right_panel, text="Pupil Diameter Graphs", padding="5")
        graphs_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        right_panel.rowconfigure(1, weight=2)  # Give graphs more space
        graphs_frame.columnconfigure(0, weight=1)
        graphs_frame.rowconfigure(0, weight=1)
        graphs_frame.rowconfigure(1, weight=1)
        
        # Left eye diameter graph
        left_graph_frame = ttk.Frame(graphs_frame)
        left_graph_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=2)
        left_graph_frame.columnconfigure(0, weight=1)
        left_graph_frame.rowconfigure(0, weight=1)
        
        ttk.Label(left_graph_frame, text="Left Eye", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W)
        self.left_graph_canvas = tk.Canvas(left_graph_frame, width=300, height=150, bg="white", highlightthickness=1)
        self.left_graph_canvas.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Right eye diameter graph
        right_graph_frame = ttk.Frame(graphs_frame)
        right_graph_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=2)
        right_graph_frame.columnconfigure(0, weight=1)
        right_graph_frame.rowconfigure(0, weight=1)
        
        ttk.Label(right_graph_frame, text="Right Eye", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W)
        self.right_graph_canvas = tk.Canvas(right_graph_frame, width=300, height=150, bg="white", highlightthickness=1)
        self.right_graph_canvas.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status frame
        status_frame = ttk.LabelFrame(right_panel, text="Status", padding="10")
        status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Ready", foreground="green")
        self.status_label.pack()
        
        # Alarms frame
        alarms_frame = ttk.LabelFrame(right_panel, text="Alarms", padding="10")
        alarms_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.alarm_label = ttk.Label(alarms_frame, text="No alarms", foreground="green")
        self.alarm_label.pack()
    
    def _initialize_system(self):
        """Initialize gaze tracking system"""
        try:
            # Use provided tracker type or fall back to config default
            tracker = self.tracker_type if self.tracker_type else config.DEFAULT_TRACKER
            self.gaze = GazeTracking(tracker_type=tracker)
            self.safety_monitor = SafetyMonitor(
                out_of_frame_threshold=config.OUT_OF_FRAME_THRESHOLD,
                perclos_threshold=config.PERCLOS_THRESHOLD,
                sustained_seconds=getattr(config, 'DROWSINESS_SUSTAINED_SECONDS', 3.0),
                alarm_cooldown=getattr(config, 'DROWSINESS_ALARM_COOLDOWN', 10.0),
                enable_audio=config.ENABLE_AUDIO_ALARMS,
                enable_visual=config.ENABLE_VISUAL_ALARMS
            )
            self.data_logger = DataLogger(
                buffer_size=config.DATA_LOG_BUFFER_SIZE,
                auto_flush=config.DATA_LOG_AUTO_FLUSH
            )
            self.performance_monitor = PerformanceMonitor(
                target_fps=config.TARGET_FPS,
                min_fps=config.MIN_FPS,
                distance_range=config.DISTANCE_RANGE_INCHES
            )
            self.status_label.config(text="System initialized - Starting webcam...", foreground="green")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize system: {e}")
            self.status_label.config(text="Initialization failed", foreground="red")
    
    def _auto_start_webcam(self):
        """Automatically start webcam when GUI opens"""
        if not self.is_running:
            self._start_tracking()
    
    
    def _toggle_tracking(self):
        """Toggle video tracking"""
        if not self.is_running:
            self._start_tracking()
        else:
            self._stop_tracking()
    
    def _start_tracking(self):
        """Start video tracking"""
        try:
            self.cap = cv2.VideoCapture(config.WEBCAM_INDEX)
            if not self.cap.isOpened():
                raise Exception("Could not open webcam")
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.WEBCAM_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.WEBCAM_HEIGHT)
            self.cap.set(cv2.CAP_PROP_FPS, config.WEBCAM_FPS)
            
            self.is_running = True
            self.start_stop_btn.config(text="Stop Tracking")
            self.record_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Tracking active", foreground="green")
            
            # Start update thread
            self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
            self.update_thread.start()
            
            # Auto-start recording if enabled
            if config.CSV_EXPORT_ENABLED and config.AUTO_START_RECORDING and not self.is_recording:
                self._toggle_recording()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start tracking: {e}")
            self.status_label.config(text="Start failed", foreground="red")
    
    def _stop_tracking(self):
        """Stop video tracking"""
        self.is_running = False
        
        if self.is_recording:
            self._toggle_recording()
        
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        
        self.start_stop_btn.config(text="Start Tracking")
        self.record_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Tracking stopped", foreground="orange")
        self.video_label.config(image='', text="No video feed")
    
    def _toggle_recording(self):
        """Toggle data recording"""
        if not self.is_recording:
            self.data_logger.start_logging()
            self.is_recording = True
            self.record_btn.config(text="⬛ Stop Recording")
            self.status_label.config(text="Recording...", foreground="red")
        else:
            # Prevent double-clicking
            self.record_btn.config(state=tk.DISABLED, text="Saving...")
            
            # Stop in background thread to avoid freezing GUI (esp. on network/cloud drives)
            threading.Thread(target=self._async_stop_recording, daemon=True).start()

    def _async_stop_recording(self):
        """Stop recording in background thread"""
        try:
            self.data_logger.stop_logging()
        except Exception as e:
            print(f"Error saving log: {e}")
        finally:
            # Schedule GUI update on main thread
            self.root.after(0, self._finish_stopping_recording)
            
    def _finish_stopping_recording(self):
        """Update GUI after recording stops"""
        self.is_recording = False
        self.record_btn.config(state=tk.NORMAL, text="✅ Saved")
        self.status_label.config(text="Recording saved", foreground="green")
        
        # Revert button text after 2 seconds
        self.root.after(2000, self._reset_record_button)
        
    def _reset_record_button(self):
        """Reset record button text if not recording"""
        if not self.is_recording:
            self.record_btn.config(text="🔴 Start Recording")
            self.status_label.config(text="Ready", foreground="black")
    

    
    def _update_loop(self):
        """Main update loop for video processing"""
        while self.is_running:
            # Safety check: ensure all components are initialized
            if self.performance_monitor is None or self.gaze is None:
                time.sleep(0.1)
                continue
            
            frame_start = self.performance_monitor.start_frame()
            
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Process frame
            self.gaze.refresh(frame)
            
            # Update performance monitor
            frame_height, frame_width = frame.shape[:2]
            self.performance_monitor.update_distance(
                self.gaze.face_bbox, frame_width, frame_height
            )
            self.performance_monitor.end_frame(frame_start)
            
            # Update safety monitor
            eye_state = self.gaze.eye_state()
            if self.safety_monitor is not None:
                self.safety_monitor.update(
                    self.gaze.is_face_detected(),
                    eye_state,
                    time.time()
                )
            
            # Log data if recording
            if self.is_recording and self.data_logger is not None:
                self.data_logger.log(
                    tracker_method=self.gaze.tracker_type,
                    left_pupil_coords=self.gaze.pupil_left_coords(),
                    right_pupil_coords=self.gaze.pupil_right_coords(),
                    left_pupil_diameter=self.gaze.pupil_left_diameter(),
                    right_pupil_diameter=self.gaze.pupil_right_diameter(),
                    eye_state=eye_state,
                    face_detected=self.gaze.is_face_detected()
                )
            
            # Update diameter data for graphs
            current_time = time.time()
            left_diameter = self.gaze.pupil_left_diameter()
            right_diameter = self.gaze.pupil_right_diameter()
            left_eye_open = self.gaze.left_eye_state() == 1
            right_eye_open = self.gaze.right_eye_state() == 1
            
            # Left eye: use actual diameter if open, otherwise use last open diameter
            if left_eye_open and left_diameter is not None:
                self.last_left_diameter = left_diameter
                self.left_diameter_data.append((current_time, left_diameter))
            elif self.last_left_diameter is not None:
                # Eye closed, use last open diameter
                self.left_diameter_data.append((current_time, self.last_left_diameter))
            
            # Right eye: use actual diameter if open, otherwise use last open diameter
            if right_eye_open and right_diameter is not None:
                self.last_right_diameter = right_diameter
                self.right_diameter_data.append((current_time, right_diameter))
            elif self.last_right_diameter is not None:
                # Eye closed, use last open diameter
                self.right_diameter_data.append((current_time, self.last_right_diameter))
            
            # Update GUI (throttled)
            if config.GUI_UPDATE_RATE > 0:
                time.sleep(1.0 / config.GUI_UPDATE_RATE)
            
            # Schedule GUI update on main thread (only if components are initialized)
            if self.performance_monitor is not None:
                self.root.after(0, self._update_gui, frame)
    
    def _update_gui(self, frame):
        """Update GUI elements"""
        if not self.is_running:
            return
        
        # Update video display
        if config.GUI_SHOW_ANNOTATIONS:
            annotated_frame = self.gaze.annotated_frame()
            if annotated_frame is not None:
                frame = annotated_frame
        
        # Convert frame for display
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_pil = Image.fromarray(frame_rgb)
        
        # Draw "REC" indicator if recording
        if self.is_recording:
            draw = ImageDraw.Draw(frame_pil)
            # Red circle
            draw.ellipse((20, 20, 40, 40), fill="red", outline="red")
            # Text
            draw.text((50, 20), "REC", fill="red")
            
        # Check for Out of Frame Alarm
        if self.safety_monitor is not None and self.safety_monitor.out_of_frame_monitor.is_alarm_active():
            draw = ImageDraw.Draw(frame_pil)
            width, height = frame_pil.size
            
            # Load large font (try system fonts)
            try:
                # Try common system fonts for "Bold" look
                # macOS
                font = ImageFont.truetype("Arial.ttf", 30)
            except IOError:
                try:
                    # Linux/Windows generic
                    font = ImageFont.truetype("arial.ttf", 30)
                except IOError:
                    # Fallback to default (will be small, but readable)
                    font = ImageFont.load_default()
            
            # Draw red banner at top (increased height for bigger text)
            banner_height = 40
            draw.rectangle([0, 0, width, banner_height], fill=(255, 0, 0, 128))
            
            # Draw text centered in banner
            text = "FACE NOT DETECTED"
            
            # Calculate text size for centering
            try:
                left, top, right, bottom = font.getbbox(text)
                text_width = right - left
                text_height = bottom - top
            except AttributeError:
                 # Fallback for older Pillow versions
                 text_width = len(text) * 20
                 text_height = 40
            
            x = (width - text_width) // 2
            y = (banner_height - text_height) // 2
            
            draw.text((x, y), text, fill="white", font=font)
            
            # Update status label to red warning
            self.status_label.config(text="Face Not Detected", foreground="red")
        elif not self.is_recording and self.status_label.cget("text") == "⚠️ NO FACE DETECTED":
            # Reset status if alarm clears (and not recording)
            self.status_label.config(text="Ready", foreground="black")
            
        frame_tk = ImageTk.PhotoImage(image=frame_pil)
        
        self.video_label.config(image=frame_tk, text="")
        self.video_label.image = frame_tk  # Keep a reference
        
        # Update metrics
        if config.GUI_SHOW_METRICS:
            # Note: FPS, Latency, Distance removed per user request
            pass
            # Eye center coordinates
            left_eye_center = self.gaze.eye_left_center()
            if left_eye_center:
                self.metrics_labels["left_eye_center"].config(
                    text=f"({left_eye_center[0]}, {left_eye_center[1]})"
                )
            else:
                self.metrics_labels["left_eye_center"].config(text="N/A")
            
            right_eye_center = self.gaze.eye_right_center()
            if right_eye_center:
                self.metrics_labels["right_eye_center"].config(
                    text=f"({right_eye_center[0]}, {right_eye_center[1]})"
                )
            else:
                self.metrics_labels["right_eye_center"].config(text="N/A")
            
            # Individual eye states
            left_eye_state = "Open" if self.gaze.left_eye_state() == 1 else "Closed"
            right_eye_state = "Open" if self.gaze.right_eye_state() == 1 else "Closed"
            self.metrics_labels["left_eye_state"].config(text=left_eye_state)
            self.metrics_labels["right_eye_state"].config(text=right_eye_state)
            
            # Update diameter graphs
            self._update_diameter_graphs()
            
            face_detected = "Yes" if self.gaze.is_face_detected() else "No"
            self.metrics_labels["face_detected"].config(text=face_detected)
        
        # Update alarms with different colors and messages
    
    def _update_diameter_graphs(self):
        """Update the pupil diameter graphs"""
        current_time = time.time()
        window_start = current_time - self.diameter_window_seconds
        
        # Update left eye graph
        self._draw_graph(self.left_graph_canvas, self.left_diameter_data, window_start, current_time, "Left Eye")
        
        # Update right eye graph
        self._draw_graph(self.right_graph_canvas, self.right_diameter_data, window_start, current_time, "Right Eye")
    
    def _draw_graph(self, canvas, data, window_start, current_time, title):
        """Draw a diameter graph on the canvas"""
        canvas.delete("all")
        
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            return  # Canvas not yet sized
        
        # Filter data to window
        window_data = [(t, d) for t, d in data if t >= window_start]
        
        if not window_data:
            # No data, draw empty graph
            self._draw_empty_graph(canvas, width, height, title)
            return
        
        # Calculate min/max diameter for Y-axis scaling
        diameters = [d for _, d in window_data]
        min_diameter = min(diameters) if diameters else 0
        max_diameter = max(diameters) if diameters else 50
        
        # Add padding
        range_diameter = max_diameter - min_diameter
        if range_diameter < 10:
            range_diameter = 10
        y_min = max(0, min_diameter - range_diameter * 0.1)
        y_max = max_diameter + range_diameter * 0.1
        
        # Draw axes (black)
        margin = 60  # Increased from 40 to prevent overlap
        graph_width = width - 2 * margin
        graph_height = height - 2 * margin
        
        # X-axis (time)
        canvas.create_line(margin, height - margin, width - margin, height - margin, fill="black", width=2)
        # Y-axis (diameter)
        canvas.create_line(margin, margin, margin, height - margin, fill="black", width=2)
        
        # Draw axis labels
        canvas.create_text(margin // 3, height // 2, text="Diameter (px)", angle=90, fill="black", font=("Arial", 9))
        canvas.create_text(width // 2, height - margin // 3, text="Time (s)", fill="black", font=("Arial", 9))
        
        # Draw Y-axis scale
        num_ticks = 5
        for i in range(num_ticks + 1):
            y_val = y_min + (y_max - y_min) * (1 - i / num_ticks)
            y_pos = margin + graph_height * (i / num_ticks)
            canvas.create_line(margin - 5, y_pos, margin, y_pos, fill="black", width=1)
            canvas.create_text(margin - 10, y_pos, text=f"{y_val:.1f}", fill="black", font=("Arial", 8), anchor="e")
        
        # Draw X-axis scale (time)
        time_range = current_time - window_start
        for i in range(4):
            t_val = window_start + time_range * (i / 3)
            x_pos = margin + graph_width * (i / 3)
            canvas.create_line(x_pos, height - margin, x_pos, height - margin + 5, fill="black", width=1)
            time_label = f"{time_range * (1 - i / 3):.1f}s"
            canvas.create_text(x_pos, height - margin + 15, text=time_label, fill="black", font=("Arial", 8))
        
        # Draw data line (red)
        if len(window_data) > 1:
            points = []
            for t, d in window_data:
                x = margin + graph_width * ((t - window_start) / time_range)
                y = margin + graph_height * (1 - (d - y_min) / (y_max - y_min))
                points.append((x, y))
            
            # Draw line connecting points
            for i in range(len(points) - 1):
                canvas.create_line(points[i][0], points[i][1], points[i+1][0], points[i+1][1], 
                                 fill="red", width=2)
    
    def _draw_empty_graph(self, canvas, width, height, title):
        """Draw an empty graph with axes"""
        margin = 60  # Increased from 40
        graph_width = width - 2 * margin
        graph_height = height - 2 * margin
        
        # X-axis
        canvas.create_line(margin, height - margin, width - margin, height - margin, fill="black", width=2)
        # Y-axis
        canvas.create_line(margin, margin, margin, height - margin, fill="black", width=2)
        
        # Labels
        canvas.create_text(margin // 3, height // 2, text="Diameter (px)", angle=90, fill="black", font=("Arial", 9))
        canvas.create_text(width // 2, height - margin // 3, text="Time (s)", fill="black", font=("Arial", 9))
        
        # No data message
        canvas.create_text(width // 2, height // 2, text="No data", fill="gray", font=("Arial", 12))
        status = self.safety_monitor.get_status()
        if status['out_of_frame_alarm']:
            self.alarm_label.config(text="⚠️ OUT OF FRAME - Participant not visible!", foreground="orange")
        elif status['drowsiness_alarm']:
            self.alarm_label.config(text="⚠️ DROWSINESS DETECTED - Alert participant!", foreground="red")
        else:
            self.alarm_label.config(text="✓ No alarms", foreground="green")
    
    def on_closing(self):
        """Handle window closing"""
        if self.is_running:
            self._stop_tracking()
        self.root.destroy()


def main(tracker_type=None):
    """Main entry point for GUI application"""
    root = tk.Tk()
    app = GazeTrackingGUI(root, tracker_type=tracker_type)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()

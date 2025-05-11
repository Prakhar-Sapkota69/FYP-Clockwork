import sys
import os
import time
import psutil
import threading
from PySide6.QtCore import Qt, QTimer, Signal, QObject, QPoint
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtGui import QColor, QPixmap

# Windows APIs for better process tracking
try:
    import win32gui
    import win32process
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

# Try to use psutil for basic system monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
    print("[DEBUG] Successfully initialized psutil")
except ImportError:
    PSUTIL_AVAILABLE = False
    print("[DEBUG] Failed to import psutil. Please install with: pip install psutil")

class PerformanceMonitor:
    def __init__(self):
        self.running = False
        self.game_process = None
        self.last_fps_time = time.time()
        self.frame_count = 0
        self.last_fps = 0
        self.last_frame_time = time.time()
        self.active_window_title = ""
        self.process_name = ""
        
        # For FPS calculation
        self.last_paint_time = 0
        self.frames = []
        self.max_frame_samples = 60  # Keep 1 second of frames at 60fps
        self.min_frame_interval = 1/1000  # Minimum time between frames (1ms)
        
        # For CPU usage calculation
        self.last_cpu_time = time.time()
        self.cpu_samples = []
        self.max_cpu_samples = 10  # Keep last 10 samples for smoothing
        self.last_cpu_percent = 0
        
        # For GPU usage
        self.gpu_available = False
        self.last_gpu_time = time.time()
        self.gpu_samples = []
        self.max_gpu_samples = 10  # Keep last 10 samples for smoothing
        self.last_gpu_percent = 0
        
        if PSUTIL_AVAILABLE:
            try:
                # Check if we can access process information
                if psutil.Process().cpu_percent() >= 0:
                    self.gpu_available = True
                    print("[DEBUG] System monitoring initialized")
                else:
                    print("[DEBUG] Could not access process information")
            except Exception as e:
                print(f"[DEBUG] Could not initialize monitoring: {str(e)}")

        print("[DEBUG] Performance monitor initialized")

    def start_capture(self):
        self.running = True
        self.last_fps_time = time.time()
        self.frame_count = 0
        self.frames = []
        self.last_frame_time = time.time()

    def stop_capture(self):
        self.running = False
        self.frames = []

    def register_frame(self):
        """Call this when a frame is rendered"""
        if not self.running:
            return
            
        now = time.time()
        
        # Only register frame if enough time has passed since last frame
        if now - self.last_frame_time >= self.min_frame_interval:
            self.frame_count += 1
            self.frames.append(now)
            self.last_frame_time = now
            
            # Remove frames older than 1 second
            while len(self.frames) > 1 and (now - self.frames[0]) > 1.0:
                self.frames.pop(0)

    def get_fps(self):
        """Calculate FPS based on registered frames"""
        if not self.frames:
            return 0
            
        if len(self.frames) == 1:
            return 1.0 / (self.frames[-1] - self.frames[0]) if (self.frames[-1] - self.frames[0]) > 0 else 0
            
        # Calculate FPS based on the last second of frames
        time_span = self.frames[-1] - self.frames[0]
        if time_span > 0:
            return (len(self.frames) - 1) / time_span
        return 0

    def get_cpu_usage(self):
        try:
            if self.game_process:
                # For game process, get direct CPU usage
                return self.game_process.cpu_percent(interval=0.1)
            else:
                # For system-wide CPU usage, use a smoother approach
                current_time = time.time()
                
                # Only measure CPU every 0.5 seconds to reduce fluctuations
                if current_time - self.last_cpu_time >= 0.5:
                    self.last_cpu_time = current_time
                    current_cpu = psutil.cpu_percent(interval=0.1)
                    
                    # Add new sample
                    self.cpu_samples.append(current_cpu)
                    
                    # Keep only last 10 samples
                    if len(self.cpu_samples) > self.max_cpu_samples:
                        self.cpu_samples.pop(0)
                    
                    # Calculate average of last 10 samples
                    if self.cpu_samples:
                        self.last_cpu_percent = sum(self.cpu_samples) / len(self.cpu_samples)
                
                return self.last_cpu_percent
        except:
            return 0

    def get_ram_usage(self):
        try:
            if self.game_process:
                return self.game_process.memory_percent()
            else:
                # For system RAM, also use a smoother approach
                return psutil.virtual_memory().percent
        except:
            return 0

    def get_gpu_usage(self):
        """Get GPU usage percentage with smoothing"""
        if not PSUTIL_AVAILABLE or not self.gpu_available:
            return -1
            
        try:
            current_time = time.time()
            
            # Only measure GPU every 0.5 seconds to reduce fluctuations
            if current_time - self.last_gpu_time >= 0.5:
                self.last_gpu_time = current_time
                
                # Get system load as a proxy for GPU activity
                system_load = psutil.cpu_percent(interval=None)
                
                # Add new sample
                self.gpu_samples.append(system_load)
                
                # Keep only last 10 samples
                if len(self.gpu_samples) > self.max_gpu_samples:
                    self.gpu_samples.pop(0)
                
                # Calculate average of last 10 samples
                if self.gpu_samples:
                    self.last_gpu_percent = sum(self.gpu_samples) / len(self.gpu_samples)
            
            # Return smoothed value
            return min(100, max(0, self.last_gpu_percent))
            
        except Exception as e:
            print(f"[DEBUG] Error getting system usage: {str(e)}")
            return -1

    def set_active_window_process(self):
        """Track the active window and its process for game-specific metrics"""
        if not WIN32_AVAILABLE:
            return
            
        try:
            hwnd = win32gui.GetForegroundWindow()
            new_title = win32gui.GetWindowText(hwnd)
            
            # Only update if window changed
            if new_title != self.active_window_title:
                self.active_window_title = new_title
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                
                try:
                    new_process = psutil.Process(pid)
                    # More flexible process name matching
                    if not self.process_name or (
                        self.process_name.lower() in new_process.name().lower() or
                        self.process_name.lower() in new_title.lower()
                    ):
                        self.game_process = new_process
                except psutil.NoSuchProcess:
                    self.game_process = None
                    
        except Exception as e:
            self.game_process = None

class OverlayBackend(QObject):
    metrics_updated = Signal(dict)

    def __init__(self):
        super().__init__()
        self.monitor = PerformanceMonitor()
        self.running = False
        self.update_interval = 0.1  # More frequent updates for smoother display
        self.last_metrics = {}
        self.frame_timer = QTimer()
        self.frame_timer.timeout.connect(self.register_frame)
        self.frame_timer.setInterval(16)  # ~60fps

    def start_monitoring(self, process_name=""):
        """Start monitoring with optional process name filter"""
        if not self.running:
            # Reset monitor state
            self.monitor = PerformanceMonitor()
            self.monitor.process_name = process_name
            self.running = True
            self.monitor.start_capture()
            
            # Start frame timer
            self.frame_timer.start()
            
            # Start metrics update thread
            self.thread = threading.Thread(target=self.update_metrics, daemon=True)
            self.thread.start()

    def stop_monitoring(self):
        """Stop monitoring and cleanup"""
        if self.running:
            self.running = False
            self.monitor.stop_capture()
            self.frame_timer.stop()
            
            # Wait for thread to finish
            if hasattr(self, 'thread') and self.thread.is_alive():
                self.thread.join(timeout=1.0)
            
            # Reset metrics
            self.last_metrics = {}

    def register_frame(self):
        """Register a new frame for FPS calculation"""
        if self.running:
            self.monitor.register_frame()

    def update_metrics(self):
        """Update metrics in a separate thread"""
        while self.running:
            try:
                self.monitor.set_active_window_process()
                
                # Get all metrics
                metrics = {
                    'fps': self.monitor.get_fps(),
                    'cpu': self.monitor.get_cpu_usage(),
                    'ram': self.monitor.get_ram_usage(),
                    'gpu': self.monitor.get_gpu_usage(),
                }
                
                # Only emit if values changed significantly
                if not self.last_metrics or any(
                    abs(metrics[k] - self.last_metrics.get(k, 0)) > 0.5 
                    for k in metrics
                ):
                    self.metrics_updated.emit(metrics)
                    self.last_metrics = metrics.copy()
                    
                time.sleep(self.update_interval)
            except Exception as e:
                print(f"Error in update_metrics: {e}")
                time.sleep(self.update_interval)

class OverlayWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint | 
            Qt.Tool |
            Qt.X11BypassWindowManagerHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        # Default position (top-right)
        self.position = "top_right"
        self.update_position()
        
        # Default text color and size
        self.text_color = "#FFFFFF"  # White
        self.text_size = 12  # Default font size
        
        # Setup UI
        self.setup_ui()
        
        # Initialize backend
        self.backend = OverlayBackend()
        self.backend.metrics_updated.connect(self.update_metrics)
        
        # Make window click-through
        self.setClickThrough(True)
        
        # Track if we're currently monitoring
        self.is_monitoring = False

    def show_overlay(self):
        """Show the overlay and start monitoring"""
        if not self.is_monitoring:
            self.backend.start_monitoring()
            self.is_monitoring = True
        self.show()

    def hide_overlay(self):
        """Hide the overlay and stop monitoring"""
        self.hide()
        if self.is_monitoring:
            self.backend.stop_monitoring()
            self.is_monitoring = False
            # Reset metrics display
            self.reset_metrics()

    def set_position(self, position):
        """Set the overlay position"""
        if position in ["top_left", "top_right", "bottom_left", "bottom_right"]:
            self.position = position
            self.update_position()
            if self.is_monitoring:
                self.show()  # Only show if we're monitoring

    def update_position(self):
        """Update window position based on current position setting"""
        if not self.parent():
            return
            
        screen_geometry = self.parent().screen().geometry()
        window_size = self.size()
        
        if self.position == "top_left":
            self.move(10, 10)
        elif self.position == "top_right":
            self.move(screen_geometry.width() - window_size.width() - 10, 10)
        elif self.position == "bottom_left":
            self.move(10, screen_geometry.height() - window_size.height() - 10)
        elif self.position == "bottom_right":
            self.move(screen_geometry.width() - window_size.width() - 10, 
                     screen_geometry.height() - window_size.height() - 10)

    def resizeEvent(self, event):
        """Handle window resize to maintain position"""
        super().resizeEvent(event)
        self.update_position()

    def set_text_color(self, color):
        """Set the text color for all metrics"""
        self.text_color = color
        self.update_metrics_style()

    def set_text_size(self, size):
        """Set the size of the entire overlay window and its elements"""
        self.text_size = size
        
        # Calculate scaling factor based on the new size (using 12 as base size)
        scale_factor = size / 12.0
        
        # Update all metric labels with new size
        for label in self.metric_labels.values():
            label.setStyleSheet(f"color: {self.text_color}; font-weight: bold; min-width: {int(40 * scale_factor)}px; font-size: {size}px;")
        
        # Update container styles
        for container in self.metric_containers:
            container.setStyleSheet(
                f"background-color: rgba(30, 30, 30, 0.8);"
                f"border: {int(1 * scale_factor)}px solid {container.property('border_color')};"
                f"border-radius: {int(6 * scale_factor)}px;"
            )
            
        # Update layout margins and spacing
        self.layout().setContentsMargins(
            int(10 * scale_factor),
            int(10 * scale_factor),
            int(10 * scale_factor),
            int(10 * scale_factor)
        )
        self.layout().setSpacing(int(5 * scale_factor))
        
        # Update metric layout margins and spacing
        for container in self.metric_containers:
            layout = container.layout()
            layout.setContentsMargins(
                int(8 * scale_factor),
                int(6 * scale_factor),
                int(8 * scale_factor),
                int(6 * scale_factor)
            )
            layout.setSpacing(int(8 * scale_factor))
        
        # Update name labels
        for name_label in self.name_labels.values():
            name_label.setStyleSheet(f"color: {name_label.property('text_color')}; font-weight: bold; min-width: {int(40 * scale_factor)}px; font-size: {size}px;")
        
        # Adjust window size
        self.adjustSize()
        self.update_position()

    def update_metrics_style(self):
        """Update the style of all metric labels"""
        for label in self.metric_labels.values():
            label.setStyleSheet(f"color: {self.text_color}; font-weight: bold; min-width: 40px; font-size: {self.text_size}px;")

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Store containers and name labels for later reference
        self.metric_containers = []
        self.name_labels = {}
        
        # Custom style for metrics
        self.metric_styles = {
            'fps': {
                'color': '#FF6B6B',
                'suffix': ''
            },
            'cpu': {
                'color': '#4ECDC4',
                'suffix': '%'
            },
            'ram': {
                'color': '#45B7D1',
                'suffix': '%'
            },
            'gpu': {
                'color': '#96CEB4',
                'suffix': '%'
            },
        }
        
        self.metric_labels = {}
        for metric, style in self.metric_styles.items():
            container = QWidget()
            container.setProperty('border_color', style['color'])
            container.setStyleSheet(
                f"background-color: rgba(30, 30, 30, 0.8);"
                f"border: 1px solid {style['color']};"
                f"border-radius: 6px;"
            )
            self.metric_containers.append(container)
            
            metric_layout = QHBoxLayout(container)
            metric_layout.setContentsMargins(8, 6, 8, 6)
            metric_layout.setSpacing(8)
            
            # Name label
            name_label = QLabel(metric.upper())
            name_label.setProperty('text_color', style['color'])
            name_label.setStyleSheet(f"color: {style['color']}; font-weight: bold; min-width: 40px;")
            self.name_labels[metric] = name_label
            
            # Value label
            value_label = QLabel("0" + style['suffix'])
            value_label.setStyleSheet(f"color: {self.text_color}; font-weight: bold; min-width: 40px; font-size: {self.text_size}px;")
            value_label.setAlignment(Qt.AlignRight)
            
            metric_layout.addWidget(name_label)
            metric_layout.addStretch()
            metric_layout.addWidget(value_label)
            
            layout.addWidget(container)
            self.metric_labels[metric] = value_label

    def setClickThrough(self, enable):
        """Make window click-through if supported"""
        if sys.platform == 'win32' and WIN32_AVAILABLE:
            try:
                hwnd = self.winId().__int__()
                style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                if enable:
                    style |= win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
                else:
                    style &= ~(win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
                win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style)
            except Exception as e:
                print(f"Couldn't set click-through: {e}")

    def update_metrics(self, metrics):
        for metric, value in metrics.items():
            if metric in self.metric_labels:
                if metric == 'gpu' and value == -1:
                    self.metric_labels[metric].setText("N/A")
                elif metric == 'fps':
                    self.metric_labels[metric].setText(f"{value:.0f}")
                else:
                    self.metric_labels[metric].setText(f"{value:.1f}%")

    def reset_metrics(self):
        """Reset all metrics to initial state"""
        for metric in self.metric_labels:
            if metric == 'fps':
                self.metric_labels[metric].setText("0")
            elif metric == 'gpu':
                self.metric_labels[metric].setText("N/A")
            else:
                self.metric_labels[metric].setText("0.0%")

    def start_monitoring(self, process_name=""):
        """Start monitoring specific process"""
        if not self.is_monitoring:
            self.backend.start_monitoring(process_name)
            self.is_monitoring = True

    def get_fps(self):
        """Get current FPS value"""
        return self.backend.monitor.get_fps() if self.is_monitoring else 0
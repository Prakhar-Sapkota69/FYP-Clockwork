import sys
import os
import time
import psutil
import threading
from PySide6.QtCore import Qt, QTimer, Signal, QObject, QPoint
from PySide6.QtWidgets import QWidget, QApplication, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtGui import QWindow

# Try to import GPU monitoring libraries
try:
    import pynvml
    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False

try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False

# Try to import DXcam
try:
    import dxcam
    DXCAM_AVAILABLE = True
    print("DXcam imported successfully")
except ImportError:
    DXCAM_AVAILABLE = False
    print("DXcam not available, using fallback FPS monitoring")

class PerformanceMonitor:
    def __init__(self):
        self.running = False
        self.thread = None
        self.game_process = None
        self.last_cpu_times = None
        self.last_cpu_time = 0
        self.fps_counter = 0
        self.last_fps_time = time.time()
        self.camera = None
        self.frame_count = 0
        self.start_time = time.time()
        self.last_fps = 0
        self.fps_samples = []
        self.max_samples = 10  # Number of FPS samples to average
        
        # Initialize DXcam if available
        if DXCAM_AVAILABLE:
            try:
                self.camera = dxcam.create()
                print("DXcam initialized successfully")
            except Exception as e:
                print(f"DXcam initialization failed: {e}")
                self.camera = None

    def start_capture(self):
        """Start screen capture"""
        if DXCAM_AVAILABLE and self.camera and not self.running:
            try:
                self.running = True
                self.start_time = time.time()
                self.frame_count = 0
                # Capture the entire screen
                self.camera.start(target_fps=60)
                print("Screen capture started")
            except Exception as e:
                print(f"Failed to start screen capture: {e}")
                self.running = False

    def stop_capture(self):
        """Stop screen capture"""
        if self.camera and self.running:
            try:
                self.camera.stop()
                self.running = False
                print("Screen capture stopped")
            except Exception as e:
                print(f"Failed to stop screen capture: {e}")

    def get_fps(self):
        """Get FPS using DXcam with fallback to process-based monitoring"""
        try:
            if DXCAM_AVAILABLE and self.camera and self.running:
                # Get the latest frame
                frame = self.camera.get_latest_frame()
                if frame is not None:
                    self.frame_count += 1
                    
                    # Calculate FPS based on elapsed time
                    elapsed_time = time.time() - self.start_time
                    if elapsed_time >= 0.5:  # Update FPS every 0.5 seconds
                        current_fps = self.frame_count / elapsed_time
                        
                        # Add to samples and maintain max_samples size
                        self.fps_samples.append(current_fps)
                        if len(self.fps_samples) > self.max_samples:
                            self.fps_samples.pop(0)
                        
                        # Calculate smoothed FPS
                        smoothed_fps = sum(self.fps_samples) / len(self.fps_samples)
                        self.last_fps = smoothed_fps
                        
                        # Reset counters
                        self.frame_count = 0
                        self.start_time = time.time()
                        
                        print(f"Screen FPS: {smoothed_fps:.1f} (Current: {current_fps:.1f})")
                        return smoothed_fps
                    
                    # Return last calculated FPS if less than 0.5 seconds has passed
                    return self.last_fps
            
            # Fallback to process-based FPS monitoring
            if self.game_process:
                try:
                    current_cpu = self.game_process.cpu_percent(interval=0.1)
                    fps = (current_cpu / 100.0) * 60
                    fps = max(1, min(60, fps))
                    print(f"Process FPS: {fps:.1f} (CPU: {current_cpu:.1f}%)")
                    return fps
                except Exception as e:
                    print(f"Process FPS Error: {e}")
            
            return 0
            
        except Exception as e:
            print(f"FPS Error: {e}")
            return 0

    def get_cpu_usage(self):
        """Get CPU usage for the game process or system"""
        try:
            if self.game_process:
                return self.game_process.cpu_percent(interval=0.1)
            else:
                return psutil.cpu_percent(interval=0.1)
        except Exception as e:
            print(f"Error getting CPU usage: {e}")
            return 0

    def get_ram_usage(self):
        """Get RAM usage for the game process or system"""
        try:
            if self.game_process:
                return self.game_process.memory_percent()
            else:
                return psutil.virtual_memory().percent
        except Exception as e:
            print(f"Error getting RAM usage: {e}")
            return 0

    def get_gpu_usage(self):
        """Get GPU usage using available methods"""
        try:
            # Try NVIDIA NVML first
            if NVML_AVAILABLE and self.nvml_initialized:
                try:
                    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                    info = pynvml.nvmlDeviceGetUtilizationRates(handle)
                    return info.gpu
                except:
                    pass
            
            # Try WMI as fallback
            if WMI_AVAILABLE:
                try:
                    w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
                    temperature_infos = w.Sensor()
                    for sensor in temperature_infos:
                        if sensor.SensorType == 'Load' and sensor.Name == 'GPU Core':
                            return float(sensor.Value)
                except:
                    pass
                    
            # If all else fails, return 0
            return 0
            
        except Exception as e:
            print(f"Error getting GPU usage: {e}")
            return 0

    def set_game_process(self, process_name):
        """Set the game process to monitor"""
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'].lower() == process_name.lower():
                    self.game_process = proc
                    return True
            return False
        except Exception as e:
            print(f"Error setting game process: {e}")
            return False

    def cleanup(self):
        """Cleanup resources"""
        self.stop_capture()
        if self.thread:
            self.thread.join()
        if self.camera:
            try:
                self.camera.stop()
            except:
                pass

class OverlayBackend(QObject):
    metrics_updated = Signal(dict)  # Signal to emit all metrics at once

    def __init__(self):
        super().__init__()
        self.monitor = PerformanceMonitor()
        self.running = False
        self.update_interval = 1.0  # Update every second

    def start_monitoring(self, game_process_name=None):
        if not self.running:
            self.running = True
            if game_process_name:
                self.monitor.set_game_process(game_process_name)
            self.monitor.start_capture()  # Start screen capture
            self.thread = threading.Thread(target=self.update_metrics, daemon=True)
            self.thread.start()

    def stop_monitoring(self):
        self.running = False
        self.monitor.stop_capture()  # Stop screen capture
        self.monitor.cleanup()

    def update_metrics(self):
        while self.running:
            metrics = {
                'fps': self.monitor.get_fps(),
                'cpu': self.monitor.get_cpu_usage(),
                'ram': self.monitor.get_ram_usage(),
                'gpu': self.monitor.get_gpu_usage()
            }
            self.metrics_updated.emit(metrics)
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
        
        # Create layout for metrics
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Create metric labels
        self.metric_labels = {}
        metrics = [
            ('fps', 'FPS', '#FF6B6B'),
            ('cpu', 'CPU', '#4ECDC4'),
            ('ram', 'RAM', '#45B7D1'),
            ('gpu', 'GPU', '#96CEB4')
        ]
        
        for metric, label, color in metrics:
            container = QWidget()
            container.setObjectName(f"{metric}Container")
            container.setStyleSheet(f"""
                QWidget#{metric}Container {{
                    background-color: rgba(0, 0, 0, 0.7);
                    border-radius: 12px;
                    border: 1px solid {color};
                }}
            """)
            
            metric_layout = QHBoxLayout(container)
            metric_layout.setContentsMargins(12, 8, 12, 8)
            
            # Metric label
            name_label = QLabel(label)
            name_label.setStyleSheet(f"""
                QLabel {{
                    color: {color};
                    font-size: 14px;
                    font-weight: bold;
                    min-width: 40px;
                }}
            """)
            
            # Value label
            value_label = QLabel("0")
            value_label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                }
            """)
            
            metric_layout.addWidget(name_label)
            metric_layout.addWidget(value_label)
            metric_layout.addStretch()
            
            layout.addWidget(container)
            self.metric_labels[metric] = value_label
        
        # Set initial position
        self.move(QPoint(50, 50))
        
        # Setup backend
        self.backend = OverlayBackend()
        self.backend.metrics_updated.connect(self.update_metrics)
        
        # Setup timer to ensure window stays on top
        self.top_timer = QTimer()
        self.top_timer.timeout.connect(self.ensure_on_top)
        self.top_timer.start(1000)  # Check every second

    def ensure_on_top(self):
        """Ensure the window stays on top"""
        try:
            if not self.isActiveWindow():
                self.raise_()
                self.activateWindow()
                # Only call requestActivate if windowHandle exists
                if self.windowHandle():
                    self.windowHandle().requestActivate()
        except Exception as e:
            print(f"Error ensuring window stays on top: {e}")
            # Fallback to basic raise
            self.raise_()

    def update_metrics(self, metrics):
        """Update all metric labels"""
        for metric, value in metrics.items():
            if metric in self.metric_labels:
                if metric == 'fps':
                    self.metric_labels[metric].setText(f"{value:.0f}")
                else:
                    self.metric_labels[metric].setText(f"{value:.1f}%")
                
                # Also update parent window if available
                if hasattr(self, 'parent') and self.parent():
                    try:
                        self.parent().update_overlay_metrics(metrics)
                    except:
                        pass
                
    def show_overlay(self):
        """Show the overlay window"""
        self.show()
        self.ensure_on_top()
        self.backend.start_monitoring()
        
    def hide_overlay(self):
        """Hide the overlay window"""
        self.hide()
        self.backend.stop_monitoring()
        
    def mousePressEvent(self, event):
        """Handle mouse press events for dragging"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        """Handle mouse move events for dragging"""
        if event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def closeEvent(self, event):
        """Ensure the monitoring stops when closed"""
        self.top_timer.stop()
        self.backend.stop_monitoring()
        event.accept()

import sys
import psutil
import time
import threading
import random  # Temporary for FPS, replace with actual FPS tracking
from PySide6.QtCore import Qt, QTimer, Signal, QObject, QPoint
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout
from PySide6.QtGui import QFont, QPainter, QColor

class OverlayBackend(QObject):
    fps_updated = Signal(str)
    cpu_updated = Signal(str)
    ram_updated = Signal(str)

    def __init__(self):
        super().__init__()
        self.running = False

    def start_monitoring(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.update_metrics, daemon=True)
            self.thread.start()

    def stop_monitoring(self):
        self.running = False

    def update_metrics(self):
        while self.running:
            fps = self.get_fps()
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent

            self.fps_updated.emit(f"FPS: {fps}")
            self.cpu_updated.emit(f"CPU: {cpu:.1f}%")
            self.ram_updated.emit(f"RAM: {ram:.1f}%")

            time.sleep(1)

    def get_fps(self):
        return random.randint(30, 144)  # Replace with real FPS tracking

class OverlayManager:
    def __init__(self):
        self.fps_counter = 0
        self.frame_times = []
        
    def get_fps(self):
        """Simulate FPS calculation for now"""
        return 60  # Placeholder return

class OverlayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint | 
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Create FPS label
        self.fps_label = QLabel("FPS: 0")
        self.fps_label.setStyleSheet("""
            QLabel {
                color: #00FF00;
                font-size: 16px;
                font-weight: bold;
                background-color: rgba(0, 0, 0, 150);
                padding: 5px;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.fps_label)
        
        # Set initial position
        self.move(QPoint(50, 50))
        
        self.backend = OverlayBackend()
        self.backend.fps_updated.connect(self.fps_label.setText)

    def update_fps(self, fps):
        """Update the FPS display"""
        self.fps_label.setText(f"FPS: {fps}")
        
    def show_overlay(self):
        """Show the overlay window"""
        self.show()
        
    def hide_overlay(self):
        """Hide the overlay window"""
        self.hide()
        
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
            
    def paintEvent(self, event):
        """Custom paint event for rounded corners"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create rounded rectangle
        rect = self.rect()
        painter.setBrush(QColor(0, 0, 0, 150))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 10, 10)

    def closeEvent(self, event):
        """Ensure the monitoring stops when closed."""
        self.backend.stop_monitoring()
        event.accept()

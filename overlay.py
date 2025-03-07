import sys
import psutil
import time
import threading
import random  # Temporary for FPS, replace with actual FPS tracking
from PySide6.QtCore import Qt, QTimer, Signal, QObject
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout
from PySide6.QtGui import QFont

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

class OverlayWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Initially hidden
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setWindowOpacity(0)  # Start hidden

        layout = QVBoxLayout()
        self.fps_label = QLabel("FPS: --", self)
        self.cpu_label = QLabel("CPU: --", self)
        self.ram_label = QLabel("RAM: --", self)

        for label in [self.fps_label, self.cpu_label, self.ram_label]:
            label.setFont(QFont("Arial", 16, QFont.Bold))
            label.setStyleSheet("color: white; background-color: rgba(0, 0, 0, 150); padding: 5px;")
            layout.addWidget(label)

        self.setLayout(layout)
        self.resize(200, 100)
        self.move(50, 50)

        self.backend = OverlayBackend()
        self.backend.fps_updated.connect(self.fps_label.setText)
        self.backend.cpu_updated.connect(self.cpu_label.setText)
        self.backend.ram_updated.connect(self.ram_label.setText)

    def show_overlay(self):
        """Show the overlay and start monitoring."""
        self.setWindowOpacity(1)  # Make visible
        self.backend.start_monitoring()
        self.show()

    def hide_overlay(self):
        """Hide the overlay and stop monitoring."""
        self.setWindowOpacity(0)  # Make invisible
        self.backend.stop_monitoring()
        self.hide()

    def closeEvent(self, event):
        """Ensure the monitoring stops when closed."""
        self.backend.stop_monitoring()
        event.accept()

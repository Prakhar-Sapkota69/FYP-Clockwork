from PySide6.QtWidgets import QSplashScreen, QProgressBar, QVBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QColor, QPainter

class CustomSplashScreen(QSplashScreen):
    def __init__(self):
        # Create a pixmap for the splash screen background
        pixmap = QPixmap(400, 300)
        pixmap.fill(QColor("#464655"))
        super().__init__(pixmap)
        
        # Create layout for splash screen content
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Create container widget
        container = QWidget(self)
        container.setLayout(layout)
        
        # Add title
        title = QLabel("Clockwork")
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 28px;
                font-weight: bold;
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Add subtitle
        subtitle = QLabel("Game Library Manager")
        subtitle.setStyleSheet("""
            QLabel {
                color: #00b0f4;
                font-size: 16px;
            }
        """)
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        # Add spacer
        layout.addSpacing(30)
        
        # Add progress bar
        self.progress = QProgressBar()
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #565666;
                border-radius: 5px;
                text-align: center;
                background-color: #363644;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #723D46;
                border-radius: 3px;
            }
        """)
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        
        # Add status message label
        self.status_label = QLabel("Initializing...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
            }
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Position the container in the center of the splash screen
        container.setGeometry(0, 0, 400, 300)
        
        # Add shadow effect to the splash screen
        self.setStyleSheet("""
            QSplashScreen {
                background-color: #464655;
                border: 2px solid #565666;
                border-radius: 10px;
            }
        """)
    
    def set_progress(self, value, message=""):
        """Update progress bar value and status message."""
        self.progress.setValue(value)
        if message:
            self.status_label.setText(message)
        self.repaint()  # Force repaint to update immediately
    
    def mousePressEvent(self, event):
        """Prevent closing splash screen when clicked."""
        pass  # Override to prevent closing on mouse click 
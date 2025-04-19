from PySide6.QtWidgets import (
    QFrame, QLabel, QVBoxLayout, QDialog, QMessageBox, 
    QHBoxLayout, QGraphicsDropShadowEffect, QWidget, QPushButton
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QUrl, Signal
from PySide6.QtGui import QPixmap, QColor, QDesktopServices, QImage, QIcon
from game_details_dialog import GameDetailsDialog
from models import Game
import requests
import subprocess
import os
import webbrowser
from urllib.parse import quote
from io import BytesIO

class GameCard(QFrame):
    clicked = Signal(object)  # Emits Game object when clicked
    
    def __init__(self, game: Game, parent=None):
        super().__init__(parent)
        self.game = game
        self.parent = parent
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the game card UI"""
        # Set frame style
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setLineWidth(1)
        self.setMinimumSize(200, 300)
        self.setMaximumSize(200, 300)
        self.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-radius: 10px;
                border: 1px solid #3d3d3d;
            }
            QFrame:hover {
                border: 1px solid #4d4d4d;
                background-color: #323232;
            }
            QLabel {
                color: white;
            }
        """)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Add poster image
        self.poster_label = QLabel()
        self.poster_label.setFixedSize(180, 100)
        self.poster_label.setAlignment(Qt.AlignCenter)
        self.poster_label.setStyleSheet("background-color: #1a1a1a; border-radius: 5px;")
        self.load_poster()
        layout.addWidget(self.poster_label)
        
        # Add game name
        self.title_label = QLabel(self.game.name or 'Unknown Game')
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 5px;")
        layout.addWidget(self.title_label)
        
        # Add genre if available
        if self.game.genre:
            self.genre_label = QLabel(self.game.genre)
            self.genre_label.setAlignment(Qt.AlignCenter)
            self.genre_label.setWordWrap(True)
            self.genre_label.setStyleSheet("font-size: 12px; color: #aaaaaa;")
            layout.addWidget(self.genre_label)
            
        # Add metadata status
        if not self.game.metadata_fetched:
            status_label = QLabel("Metadata not fetched")
            status_label.setAlignment(Qt.AlignCenter)
            status_label.setStyleSheet("color: #ff4444; font-size: 12px;")
            layout.addWidget(status_label)
        else:
            # Add rating if available
            if self.game.rating and self.game.rating > 0:
                rating_label = QLabel(f"★ {self.game.rating:.1f}/5.0")
                rating_label.setAlignment(Qt.AlignCenter)
                rating_label.setStyleSheet("color: #ffd700;")  # Gold color for stars
                layout.addWidget(rating_label)
        
        # Make the card clickable
        self.setCursor(Qt.PointingHandCursor)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
    def load_poster(self):
        """Load the game's poster image"""
        try:
            # Try loading from local path first
            if self.game.poster_path and os.path.exists(self.game.poster_path):
                pixmap = QPixmap(self.game.poster_path)
                scaled_pixmap = pixmap.scaled(180, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.poster_label.setPixmap(scaled_pixmap)
                return
                
            # If no local path or file doesn't exist, try URL
            if self.game.poster_url:
                response = requests.get(self.game.poster_url)
                if response.status_code == 200:
                    image = QImage.fromData(response.content)
                    pixmap = QPixmap.fromImage(image)
                    scaled_pixmap = pixmap.scaled(180, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.poster_label.setPixmap(scaled_pixmap)
                    return
            
            # Load default image if no poster or loading fails
            self.poster_label.setText("No Image")
            self.poster_label.setStyleSheet("""
                QLabel {
                    background-color: #3d3d3d;
                    border-radius: 5px;
                    color: #888;
                    font-size: 12px;
                }
            """)
        except Exception as e:
            print(f"Error loading poster: {str(e)}")
            self.poster_label.setText("Error")
            self.poster_label.setStyleSheet("""
                QLabel {
                    background-color: #3d3d3d;
                    border-radius: 5px;
                    color: #ff4444;
                    font-size: 12px;
                }
            """)
        
    def launch_game(self):
        """Launch the game"""
        if hasattr(self.parent, 'launch_game'):
            self.parent.launch_game(self.game)

    def show_details(self, event):
        dialog = GameDetailsDialog(self.game, self)
        dialog.exec_()
                
    def launch_manual_game(self, path):
        try:
            if os.path.exists(path):
                # Use shell=True to handle paths with spaces
                subprocess.Popen(path, shell=True)
                return True
            else:
                QMessageBox.critical(self, "Error", f"Game executable not found at: {path}")
                return False
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to launch game: {str(e)}")
            return False
            
    def launch_steam_game(self, app_id):
        try:
            url = f"steam://rungameid/{app_id}"
            QDesktopServices.openUrl(QUrl(url))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to launch game: {str(e)}")

    def enterEvent(self, event):
        """Handle mouse enter event for hover effect."""
        # Create animation for scaling up
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Calculate new size (5% larger)
        new_width = int(self.width() * 1.05)
        new_height = int(self.height() * 1.05)
        
        # Calculate new position to keep card centered
        new_x = self.x() - (new_width - self.width()) // 2
        new_y = self.y() - (new_height - self.height()) // 2
        
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(QRect(new_x, new_y, new_width, new_height))
        self.animation.start()
        
        # Increase shadow effect
        shadow = self.graphicsEffect()
        if isinstance(shadow, QGraphicsDropShadowEffect):
            shadow.setBlurRadius(25)
            shadow.setColor(QColor(0, 0, 0, 100))
            shadow.setOffset(0, 4)
        
    def leaveEvent(self, event):
        """Handle mouse leave event to restore original size."""
        # Create animation for scaling down
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Calculate original size
        original_width = int(self.width() / 1.05)
        original_height = int(self.height() / 1.05)
        
        # Calculate original position
        original_x = self.x() + (self.width() - original_width) // 2
        original_y = self.y() + (self.height() - original_height) // 2
        
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(QRect(original_x, original_y, original_width, original_height))
        self.animation.start()
        
        # Restore original shadow effect
        shadow = self.graphicsEffect()
        if isinstance(shadow, QGraphicsDropShadowEffect):
            shadow.setBlurRadius(15)
            shadow.setColor(QColor(0, 0, 0, 80))
            shadow.setOffset(0, 2)

    def mousePressEvent(self, event):
        """Handle mouse click events"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.game)
        super().mousePressEvent(event) 
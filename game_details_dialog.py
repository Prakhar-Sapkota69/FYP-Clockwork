from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QScrollArea, QWidget, QSizePolicy, QMessageBox)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QImage
from models import Game
import requests
from io import BytesIO

class GameDetailsDialog(QDialog):
    def __init__(self, game, parent=None):
        super().__init__(parent)
        self.game = game
        self.setWindowTitle(f"{game.name} - Details")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
            QPushButton:pressed {
                background-color: #4d4d4d;
            }
            QScrollArea {
                border: none;
                background-color: #1a1a1a;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #2d2d2d;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #4d4d4d;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #5d5d5d;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header section with game name
        header_layout = QHBoxLayout()
        title_label = QLabel(self.game.name)
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #ffffff;
            margin-bottom: 10px;
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Main content area
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        # Left side - Game poster and launch button
        left_panel = QVBoxLayout()
        left_panel.setSpacing(15)
        
        # Game poster
        poster_label = QLabel()
        poster_label.setMinimumSize(300, 400)
        poster_label.setAlignment(Qt.AlignCenter)
        poster_label.setStyleSheet("""
            background-color: #2d2d2d;
            border-radius: 8px;
        """)
        
        if self.game.poster_url:
            try:
                response = requests.get(self.game.poster_url)
                if response.status_code == 200:
                    image_data = response.content
                    pixmap = QPixmap()
                    pixmap.loadFromData(image_data)
                    scaled_pixmap = pixmap.scaled(300, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    poster_label.setPixmap(scaled_pixmap)
            except Exception as e:
                print(f"Error loading poster: {e}")
                poster_label.setText("No Image Available")
        else:
            poster_label.setText("No Image Available")
        
        left_panel.addWidget(poster_label)
        
        # Launch button
        launch_button = QPushButton("Launch Game")
        launch_button.setStyleSheet("""
            background-color: #4CAF50;
            color: white;
            padding: 12px;
            font-size: 16px;
            border-radius: 6px;
        """)
        launch_button.clicked.connect(self.launch_game)
        left_panel.addWidget(launch_button)
        
        content_layout.addLayout(left_panel)

        # Right side - Game details
        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)

        # Description
        description_label = QLabel(self.game.description or "No description available")
        description_label.setWordWrap(True)
        description_label.setStyleSheet("""
            font-size: 14px;
            line-height: 1.5;
            color: #cccccc;
        """)
        right_panel.addWidget(description_label)

        # Metadata section
        metadata_widget = QWidget()
        metadata_layout = QVBoxLayout(metadata_widget)
        metadata_layout.setSpacing(10)

        # Create metadata fields with improved styling
        metadata_fields = {
            'Genre': self.game.genre or 'Not specified',
            'Release Date': self.game.release_date or 'Not specified',
            'Playtime': lambda: f"{self.game.playtime} minutes" if self.game.playtime < 60 else f"{self.game.playtime/60:.1f} hours",
            'Rating': f"{self.game.rating:.1f}" if self.game.rating else 'Not rated',
            'Platforms': ', '.join(self.game.platforms) if self.game.platforms else 'Not specified',
            'Developers': ', '.join(self.game.developers) if self.game.developers else 'Not specified',
            'Publishers': ', '.join(self.game.publishers) if self.game.publishers else 'Not specified',
            'Metacritic': str(self.game.metacritic) if self.game.metacritic else 'Not rated',
            'ESRB Rating': self.game.esrb_rating or 'Not rated'
        }

        for field, value in metadata_fields.items():
            field_widget = QWidget()
            field_layout = QHBoxLayout(field_widget)
            field_layout.setContentsMargins(0, 0, 0, 0)
            
            label = QLabel(f"{field}:")
            label.setStyleSheet("""
                font-weight: bold;
                color: #4CAF50;
                min-width: 120px;
            """)
            
            value_label = QLabel(str(value() if callable(value) else value))
            value_label.setStyleSheet("color: #ffffff;")
            value_label.setWordWrap(True)
            
            field_layout.addWidget(label)
            field_layout.addWidget(value_label)
            field_layout.addStretch()
            
            metadata_layout.addWidget(field_widget)

        # Add metadata section to right panel
        right_panel.addWidget(metadata_widget)
        right_panel.addStretch()

        content_layout.addLayout(right_panel, stretch=2)
        layout.addLayout(content_layout)

    def launch_game(self):
        """Launch the game using the parent window's launch_game method."""
        if self.game.app_id or self.game.install_path:
            self.parent().launch_game(self.game)
        else:
            QMessageBox.warning(self, "Error", "No launch command available for this game.")

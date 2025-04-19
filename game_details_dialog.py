from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QScrollArea, QWidget, QSizePolicy, QMessageBox,
                             QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QImage, QColor
from models import Game
import requests
from io import BytesIO

class GameDetailsDialog(QDialog):
    def __init__(self, game, parent=None):
        super().__init__(parent)
        self.game = game
        self.setWindowTitle(f"{game.name}")
        self.setMinimumWidth(900)
        self.setMinimumHeight(600)
        self.setStyleSheet("""
            QDialog {
                background-color: #464655;
                color: #ffffff;
                border-radius: 15px;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #723D46;
                color: #ffffff;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #8B4B55;
            }
            QPushButton:pressed {
                background-color: #5E323A;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #363644;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #565666;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666677;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QWidget#content-panel {
                background-color: #363644;
                border-radius: 12px;
                border: 2px solid #565666;
            }
            QWidget#poster-container {
                background-color: rgba(54, 54, 68, 0.5);
                border-radius: 12px;
                border: 2px solid #565666;
            }
            QLabel#title-label {
                font-size: 24px;
                font-weight: bold;
                color: #ffffff;
                padding: 10px 0;
            }
            QWidget#info-panel {
                background-color: rgba(54, 54, 68, 0.5);
                border-radius: 8px;
                border: 2px solid #565666;
                padding: 15px;
                margin: 5px;
            }
            QLabel#section-title {
                color: #00b0f4;
                font-weight: bold;
                font-size: 16px;
                padding: 5px 0;
            }
            QLabel#info-label {
                color: #ffffff;
                font-size: 14px;
                padding: 3px 0;
            }
            QWidget#detail-item {
                background-color: rgba(54, 54, 68, 0.5);
                border-radius: 8px;
                padding: 8px;
                margin: 4px;
            }
            QWidget#separator {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #565666, stop:1 transparent);
                height: 2px;
                margin: 10px 0;
            }
        """)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 20, 25, 25)

        # Header with game name and separator
        header_container = QWidget()
        header_layout = QVBoxLayout(header_container)
        header_layout.setSpacing(0)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel(self.game.name)
        title_label.setObjectName("title-label")
        header_layout.addWidget(title_label)

        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFrameShape(QFrame.HLine)
        separator.setFixedHeight(2)
        header_layout.addWidget(separator)

        layout.addWidget(header_container)

        # Main content area
        content_widget = QWidget()
        content_widget.setObjectName("content-panel")
        
        # Add shadow to content panel
        content_shadow = QGraphicsDropShadowEffect()
        content_shadow.setColor(QColor(0, 0, 0, 100))
        content_shadow.setBlurRadius(25)
        content_shadow.setOffset(0, 4)
        content_widget.setGraphicsEffect(content_shadow)
        
        content_layout = QHBoxLayout(content_widget)
        content_layout.setSpacing(25)
        content_layout.setContentsMargins(25, 25, 25, 25)

        # Left side - Game poster and launch button
        left_panel = QVBoxLayout()
        left_panel.setSpacing(20)
        
        # Game poster container with shadow effect
        poster_container = QWidget()
        poster_container.setObjectName("poster-container")
        poster_layout = QVBoxLayout(poster_container)
        poster_layout.setContentsMargins(0, 0, 0, 0)
        
        # Game poster
        poster_label = QLabel()
        poster_label.setMinimumSize(280, 400)
        poster_label.setMaximumSize(280, 400)
        poster_label.setAlignment(Qt.AlignCenter)
        poster_label.setStyleSheet("""
            background-color: rgba(2, 45, 74, 0.7);
            border-radius: 10px;
            padding: 0;
        """)
        
        if self.game.poster_url:
            try:
                response = requests.get(self.game.poster_url)
                if response.status_code == 200:
                    image_data = response.content
                    pixmap = QPixmap()
                    pixmap.loadFromData(image_data)
                    scaled_pixmap = pixmap.scaled(280, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    poster_label.setPixmap(scaled_pixmap)
            except Exception as e:
                print(f"Error loading poster: {e}")
                poster_label.setText("No Image Available")
        else:
            poster_label.setText("No Image Available")
        
        poster_layout.addWidget(poster_label)
        
        # Add shadow effect to poster
        poster_shadow = QGraphicsDropShadowEffect()
        poster_shadow.setColor(QColor(0, 0, 0, 120))
        poster_shadow.setBlurRadius(20)
        poster_shadow.setOffset(0, 4)
        poster_label.setGraphicsEffect(poster_shadow)
        
        left_panel.addWidget(poster_container)
        
        # Launch button
        launch_button = QPushButton("PLAY GAME")
        launch_button.setFixedHeight(45)
        launch_button.setStyleSheet("""
            QPushButton {
                background-color: #723D46;
                color: white;
                padding: 12px;
                font-size: 15px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8B4B55;
            }
            QPushButton:pressed {
                background-color: #5E323A;
            }
        """)
        launch_button.clicked.connect(self.launch_game)
        
        # Add shadow to button
        button_shadow = QGraphicsDropShadowEffect()
        button_shadow.setColor(QColor(0, 0, 0, 100))
        button_shadow.setBlurRadius(15)
        button_shadow.setOffset(0, 3)
        launch_button.setGraphicsEffect(button_shadow)
        
        left_panel.addWidget(launch_button)
        
        # Add close button
        close_button = QPushButton("CLOSE")
        close_button.setFixedHeight(40)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #022d4a;
                color: white;
                padding: 10px;
                font-size: 14px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #033860;
            }
            QPushButton:pressed {
                background-color: #022d4a;
            }
        """)
        close_button.clicked.connect(self.close)
        
        # Add shadow to close button
        close_shadow = QGraphicsDropShadowEffect()
        close_shadow.setColor(QColor(0, 0, 0, 100))
        close_shadow.setBlurRadius(15)
        close_shadow.setOffset(0, 3)
        close_button.setGraphicsEffect(close_shadow)
        
        left_panel.addWidget(close_button)
        left_panel.addStretch()
        
        content_layout.addLayout(left_panel)
        
        # Right side - Game details
        right_panel = QScrollArea()
        right_panel.setWidgetResizable(True)
        right_panel.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        details_layout.setSpacing(20)
        details_layout.setContentsMargins(0, 0, 10, 0)
        
        # Game type and installation status
        status_panel = QWidget()
        status_panel.setObjectName("info-panel")
        status_layout = QVBoxLayout(status_panel)
        
        # Platform info with icon
        platform_container = QWidget()
        platform_container.setObjectName("detail-item")
        platform_layout = QHBoxLayout(platform_container)
        platform_layout.setContentsMargins(12, 8, 12, 8)
        
        platform_icon = QLabel("🖥️")
        platform_icon.setStyleSheet("color: #00b0f4; font-size: 16px;")
        platform_text = QLabel(f"Platform: {self.game.type.capitalize() if self.game.type else 'Unknown'}")
        platform_text.setObjectName("info-label")
        
        platform_layout.addWidget(platform_icon)
        platform_layout.addWidget(platform_text)
        platform_layout.addStretch()
        
        status_layout.addWidget(platform_container)
        
        # Installation status with icon
        install_container = QWidget()
        install_container.setObjectName("detail-item")
        install_layout = QHBoxLayout(install_container)
        install_layout.setContentsMargins(12, 8, 12, 8)
        
        install_icon = QLabel("💾" if self.game.is_installed else "❌")
        install_icon.setStyleSheet("color: #00b0f4; font-size: 16px;")
        install_text = QLabel(f"Status: {'Installed' if self.game.is_installed else 'Not Installed'}")
        install_text.setObjectName("info-label")
        
        install_layout.addWidget(install_icon)
        install_layout.addWidget(install_text)
        install_layout.addStretch()
        
        status_layout.addWidget(install_container)
        details_layout.addWidget(status_panel)
        
        # Game details panel
        if self.game.description or self.game.genre:
            details_panel = QWidget()
            details_panel.setObjectName("info-panel")
            details_inner_layout = QVBoxLayout(details_panel)
            
            if self.game.genre:
                genre_container = QWidget()
                genre_container.setObjectName("detail-item")
                genre_layout = QHBoxLayout(genre_container)
                genre_layout.setContentsMargins(12, 8, 12, 8)
                
                genre_icon = QLabel("🏷️")
                genre_icon.setStyleSheet("color: #00b0f4; font-size: 16px;")
                genre_text = QLabel(f"Genre: {self.game.genre}")
                genre_text.setObjectName("info-label")
                
                genre_layout.addWidget(genre_icon)
                genre_layout.addWidget(genre_text)
                genre_layout.addStretch()
                
                details_inner_layout.addWidget(genre_container)
            
            if self.game.description:
                desc_title = QLabel("Description")
                desc_title.setObjectName("section-title")
                details_inner_layout.addWidget(desc_title)
                
                desc_label = QLabel(self.game.description)
                desc_label.setObjectName("info-label")
                desc_label.setWordWrap(True)
                details_inner_layout.addWidget(desc_label)
            
            details_layout.addWidget(details_panel)
        
        # Additional metadata panel
        if any([self.game.release_date, self.game.developers, self.game.publishers, self.game.playtime]):
            metadata_panel = QWidget()
            metadata_panel.setObjectName("info-panel")
            metadata_layout = QVBoxLayout(metadata_panel)
            
            if self.game.playtime is not None:
                playtime_container = QWidget()
                playtime_container.setObjectName("detail-item")
                playtime_layout = QHBoxLayout(playtime_container)
                playtime_layout.setContentsMargins(12, 8, 12, 8)
                
                playtime_icon = QLabel("⏱️")
                playtime_icon.setStyleSheet("color: #00b0f4; font-size: 16px;")
                
                # Format playtime to show hours if >= 60 minutes, otherwise show minutes
                if self.game.playtime < 60:
                    playtime_text = QLabel(f"Playtime: {self.game.playtime} minutes")
                else:
                    hours = self.game.playtime / 60
                    playtime_text = QLabel(f"Playtime: {hours:.1f} hours")
                
                playtime_text.setObjectName("info-label")
                
                playtime_layout.addWidget(playtime_icon)
                playtime_layout.addWidget(playtime_text)
                playtime_layout.addStretch()
                
                metadata_layout.addWidget(playtime_container)
            
            if self.game.release_date:
                release_container = QWidget()
                release_container.setObjectName("detail-item")
                release_layout = QHBoxLayout(release_container)
                release_layout.setContentsMargins(12, 8, 12, 8)
                
                release_icon = QLabel("📅")
                release_icon.setStyleSheet("color: #00b0f4; font-size: 16px;")
                release_text = QLabel(f"Release Date: {self.game.release_date}")
                release_text.setObjectName("info-label")
                
                release_layout.addWidget(release_icon)
                release_layout.addWidget(release_text)
                release_layout.addStretch()
                
                metadata_layout.addWidget(release_container)
            
            if self.game.developers:
                dev_container = QWidget()
                dev_container.setObjectName("detail-item")
                dev_layout = QHBoxLayout(dev_container)
                dev_layout.setContentsMargins(12, 8, 12, 8)
                
                dev_icon = QLabel("👨‍💻")
                dev_icon.setStyleSheet("color: #00b0f4; font-size: 16px;")
                dev_text = QLabel(f"Developer: {self.game.developers}")
                dev_text.setObjectName("info-label")
                
                dev_layout.addWidget(dev_icon)
                dev_layout.addWidget(dev_text)
                dev_layout.addStretch()
                
                metadata_layout.addWidget(dev_container)
            
            if self.game.publishers:
                pub_container = QWidget()
                pub_container.setObjectName("detail-item")
                pub_layout = QHBoxLayout(pub_container)
                pub_layout.setContentsMargins(12, 8, 12, 8)
                
                pub_icon = QLabel("🏢")
                pub_icon.setStyleSheet("color: #00b0f4; font-size: 16px;")
                pub_text = QLabel(f"Publisher: {self.game.publishers}")
                pub_text.setObjectName("info-label")
                
                pub_layout.addWidget(pub_icon)
                pub_layout.addWidget(pub_text)
                pub_layout.addStretch()
                
                metadata_layout.addWidget(pub_container)
            
            details_layout.addWidget(metadata_panel)
        
        details_layout.addStretch()
        right_panel.setWidget(details_widget)
        content_layout.addWidget(right_panel, stretch=1)
        
        layout.addWidget(content_widget)

    def launch_game(self):
        """Launch the game using the parent window's launch_game method."""
        try:
            if self.game.app_id or self.game.install_path:
                self.parent().launch_game(self.game)
                self.close()  # Close the dialog after launching
            else:
                QMessageBox.warning(self, "Error", "No launch command available for this game.")
        except Exception as e:
            print(f"Error launching game: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to launch game: {str(e)}")

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                            QPushButton, QFileDialog, QFrame, QScrollArea, QWidget,
                            QGraphicsDropShadowEffect, QProgressBar, QMessageBox)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor, QPixmap
from models import Game
import requests
import json
import os
from urllib.request import urlopen
from io import BytesIO

class MetadataFetcherThread(QThread):
    """Thread for fetching game metadata without blocking the UI"""
    metadata_fetched = Signal(dict)
    error = Signal(str)
    progress = Signal(int, int)  # current, total

    def __init__(self, game_name):
        super().__init__()
        self.game_name = game_name
        self.base_url = "https://store.steampowered.com/api"

    def run(self):
        try:
            self.progress.emit(1, 3)
            
            # Search for the game using Steam Store search
            search_url = f"{self.base_url}/storesearch/"
            params = {
                "term": self.game_name,
                "l": "english",
                "cc": "US"
            }
            
            response = requests.get(search_url, params=params)
            if response.status_code != 200:
                raise Exception(f"Steam API request failed: {response.status_code}")

            data = response.json()
            items = data.get("items", [])
            
            if not items:
                raise Exception("No matching game found on Steam")
                
            # Get the first match
            game = items[0]
            app_id = game.get("id")
            
            self.progress.emit(2, 3)
            
            # Get detailed game info from store API
            details_url = f"{self.base_url}/appdetails/"
            params = {
                "appids": app_id,
                "l": "english"
            }
            
            response = requests.get(details_url, params=params)
            if response.status_code != 200:
                raise Exception(f"Steam API request failed: {response.status_code}")

            detailed_data = response.json()
            app_data = detailed_data.get(str(app_id), {}).get("data", {})
            
            if not app_data:
                raise Exception("Failed to fetch game details")
                
            self.progress.emit(3, 3)

            # Extract relevant metadata
            metadata = {
                "name": app_data.get("name", ""),
                "app_id": app_id,
                "genre": ", ".join(g.get("description", "") for g in app_data.get("genres", [])),
                "release_date": app_data.get("release_date", {}).get("date", ""),
                "description": app_data.get("short_description", ""),
                "developers": app_data.get("developers", []),
                "publishers": app_data.get("publishers", []),
                "poster_url": app_data.get("header_image", ""),
                "background_url": app_data.get("background", ""),
                "type": "steam"
            }

            self.metadata_fetched.emit(metadata)

        except Exception as e:
            self.error.emit(str(e))

class ManualAddGameDialog(QDialog):
    def __init__(self, parent=None, game=None):
        super().__init__(parent)
        self.game = game  # Store the game being edited
        self.setWindowTitle("Edit Game" if game else "Add Game Manually")
        self.setMinimumWidth(600)
        self.poster_path = None  # Store local poster path
        self.setup_ui()
        if game:
            self.load_game_data(game)
        
    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 20, 25, 25)
        
        # Create scroll area for the form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        # Create form container
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(0, 0, 0, 0)
        
        # Required fields section
        required_section = QWidget()
        required_section.setObjectName("required-section")
        required_layout = QVBoxLayout(required_section)
        required_layout.setSpacing(15)
        
        # Game name with fetch button
        name_container = QWidget()
        name_layout = QHBoxLayout(name_container)
        name_layout.setContentsMargins(0, 0, 0, 0)
        
        name_label = QLabel("Game Name:")
        name_label.setStyleSheet("font-weight: bold; color: #ffffff;")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter game name")
        self.name_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #2d3748;
                border-radius: 4px;
                background-color: #1a202c;
                color: #ffffff;
            }
        """)
        
        fetch_btn = QPushButton("Fetch Metadata")
        fetch_btn.setStyleSheet("""
            QPushButton {
                background-color: #3182ce;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4299e1;
            }
        """)
        fetch_btn.clicked.connect(self.fetch_metadata)
        
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        name_layout.addWidget(fetch_btn)
        required_layout.addWidget(name_container)
        
        # Progress bar for metadata fetching
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #2d3748;
                border-radius: 4px;
                background-color: #1a202c;
                color: white;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3182ce;
                border-radius: 3px;
            }
        """)
        self.progress_bar.hide()
        required_layout.addWidget(self.progress_bar)
        
        # Game executable
        exe_container = QWidget()
        exe_layout = QHBoxLayout(exe_container)
        exe_layout.setContentsMargins(0, 0, 0, 0)
        
        exe_label = QLabel("Game Executable:")
        exe_label.setStyleSheet("font-weight: bold; color: #ffffff;")
        self.exe_input = QLineEdit()
        self.exe_input.setPlaceholderText("Select game executable")
        self.exe_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #2d3748;
                border-radius: 4px;
                background-color: #1a202c;
                color: #ffffff;
            }
        """)
        browse_btn = QPushButton("Browse")
        browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d3748;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4a5568;
            }
        """)
        browse_btn.clicked.connect(self.browse_executable)
        
        exe_layout.addWidget(exe_label)
        exe_layout.addWidget(self.exe_input)
        exe_layout.addWidget(browse_btn)
        required_layout.addWidget(exe_container)
        
        form_layout.addWidget(required_section)
        
        # Add poster image section after the required fields
        poster_section = QWidget()
        poster_section.setObjectName("poster-section")
        poster_layout = QVBoxLayout(poster_section)
        poster_layout.setSpacing(15)

        # Poster preview label
        self.poster_preview = QLabel()
        self.poster_preview.setFixedSize(200, 300)  # Set fixed size for poster
        self.poster_preview.setStyleSheet("""
            QLabel {
                background-color: #1a202c;
                border: 2px dashed #4a5568;
                border-radius: 4px;
            }
        """)
        self.poster_preview.setAlignment(Qt.AlignCenter)
        self.poster_preview.setText("No poster selected")

        # Poster buttons container
        poster_buttons = QHBoxLayout()
        
        # Browse poster button
        browse_poster_btn = QPushButton("Browse Image")
        browse_poster_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d3748;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4a5568;
            }
        """)
        browse_poster_btn.clicked.connect(self.browse_poster)

        # Clear poster button
        clear_poster_btn = QPushButton("Clear Image")
        clear_poster_btn.setStyleSheet("""
            QPushButton {
                background-color: #e53e3e;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #f56565;
            }
        """)
        clear_poster_btn.clicked.connect(self.clear_poster)

        poster_buttons.addWidget(browse_poster_btn)
        poster_buttons.addWidget(clear_poster_btn)
        poster_buttons.addStretch()

        poster_layout.addWidget(self.poster_preview, alignment=Qt.AlignCenter)
        poster_layout.addLayout(poster_buttons)

        # Add poster section to form layout after required section
        form_layout.addWidget(poster_section)
        
        # Optional metadata section
        metadata_section = QWidget()
        metadata_section.setObjectName("metadata-section")
        metadata_layout = QVBoxLayout(metadata_section)
        metadata_layout.setSpacing(15)
        
        # Genre
        genre_container = QWidget()
        genre_layout = QHBoxLayout(genre_container)
        genre_layout.setContentsMargins(0, 0, 0, 0)
        
        genre_label = QLabel("Genre:")
        genre_label.setStyleSheet("color: #ffffff;")
        self.genre_input = QLineEdit()
        self.genre_input.setPlaceholderText("Enter game genre")
        self.genre_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #2d3748;
                border-radius: 4px;
                background-color: #1a202c;
                color: #ffffff;
            }
        """)
        
        genre_layout.addWidget(genre_label)
        genre_layout.addWidget(self.genre_input)
        metadata_layout.addWidget(genre_container)
        
        # Release Date
        date_container = QWidget()
        date_layout = QHBoxLayout(date_container)
        date_layout.setContentsMargins(0, 0, 0, 0)
        
        date_label = QLabel("Release Date:")
        date_label.setStyleSheet("color: #ffffff;")
        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText("Enter release date (e.g., 2023-01-01)")
        self.date_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #2d3748;
                border-radius: 4px;
                background-color: #1a202c;
                color: #ffffff;
            }
        """)
        
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_input)
        metadata_layout.addWidget(date_container)
        
        # Description
        desc_container = QWidget()
        desc_layout = QVBoxLayout(desc_container)
        desc_layout.setContentsMargins(0, 0, 0, 0)
        
        desc_label = QLabel("Description:")
        desc_label.setStyleSheet("color: #ffffff;")
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Enter game description")
        self.desc_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #2d3748;
                border-radius: 4px;
                background-color: #1a202c;
                color: #ffffff;
            }
        """)
        
        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(self.desc_input)
        metadata_layout.addWidget(desc_container)
        
        # Developers
        dev_container = QWidget()
        dev_layout = QHBoxLayout(dev_container)
        dev_layout.setContentsMargins(0, 0, 0, 0)
        
        dev_label = QLabel("Developers:")
        dev_label.setStyleSheet("color: #ffffff;")
        self.dev_input = QLineEdit()
        self.dev_input.setPlaceholderText("Enter developers (comma-separated)")
        self.dev_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #2d3748;
                border-radius: 4px;
                background-color: #1a202c;
                color: #ffffff;
            }
        """)
        
        dev_layout.addWidget(dev_label)
        dev_layout.addWidget(self.dev_input)
        metadata_layout.addWidget(dev_container)
        
        # Publishers
        pub_container = QWidget()
        pub_layout = QHBoxLayout(pub_container)
        pub_layout.setContentsMargins(0, 0, 0, 0)
        
        pub_label = QLabel("Publishers:")
        pub_label.setStyleSheet("color: #ffffff;")
        self.pub_input = QLineEdit()
        self.pub_input.setPlaceholderText("Enter publishers (comma-separated)")
        self.pub_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #2d3748;
                border-radius: 4px;
                background-color: #1a202c;
                color: #ffffff;
            }
        """)
        
        pub_layout.addWidget(pub_label)
        pub_layout.addWidget(self.pub_input)
        metadata_layout.addWidget(pub_container)
        
        form_layout.addWidget(metadata_section)
        
        # Buttons
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d3748;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4a5568;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        add_btn = QPushButton("Save Game")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #3182ce;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4299e1;
            }
        """)
        add_btn.clicked.connect(self.accept)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(add_btn)
        
        form_layout.addWidget(button_container)
        
        # Set up scroll area
        scroll.setWidget(form_container)
        layout.addWidget(scroll)
        
        # Set dialog style
        self.setStyleSheet("""
            QDialog {
                background-color: #1a202c;
            }
            QLabel {
                color: #ffffff;
            }
            #required-section, #metadata-section {
                background-color: #2d3748;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
    def fetch_metadata(self):
        """Fetch game metadata from Steam API"""
        game_name = self.name_input.text().strip()
        if not game_name:
            QMessageBox.warning(self, "Error", "Please enter a game name first")
            return
            
        # Show progress bar
        self.progress_bar.setRange(0, 3)
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        
        # Create and start the metadata fetcher thread
        self.fetcher = MetadataFetcherThread(game_name)
        self.fetcher.metadata_fetched.connect(self.on_metadata_fetched)
        self.fetcher.error.connect(self.on_metadata_error)
        self.fetcher.progress.connect(self.on_metadata_progress)
        self.fetcher.start()
        
    def on_metadata_error(self, error_msg):
        """Handle metadata fetch error"""
        self.progress_bar.hide()
        QMessageBox.warning(self, "Error", f"Failed to fetch metadata: {error_msg}")
        
    def on_metadata_progress(self, current, total):
        """Update progress bar"""
        self.progress_bar.setValue(current)
        self.progress_bar.setMaximum(total)
        
    def load_game_data(self, game):
        """Load existing game data into the form."""
        self.name_input.setText(game.name)
        self.exe_input.setText(game.install_path)
        self.genre_input.setText(game.genre or "")
        self.date_input.setText(game.release_date or "")
        self.desc_input.setText(game.description or "")
        self.dev_input.setText(", ".join(game.developers) if game.developers else "")
        self.pub_input.setText(", ".join(game.publishers) if game.publishers else "")
        
    def browse_executable(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Game Executable", "", "Executable Files (*.exe);;All Files (*)"
        )
        if file_path:
            self.exe_input.setText(file_path)
            
    def browse_poster(self):
        """Open file dialog to select a poster image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Poster Image", "",
            "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
        )
        if file_path:
            self.set_poster(file_path, is_local=True)

    def clear_poster(self):
        """Clear the current poster image"""
        self.poster_preview.setText("No poster selected")
        self.poster_preview.setPixmap(QPixmap())
        self.poster_path = None
        self.poster_url = None

    def set_poster(self, path_or_url, is_local=False):
        """Set the poster image from either a local file or URL"""
        try:
            pixmap = QPixmap()
            if is_local:
                # Load local file
                pixmap.load(path_or_url)
                self.poster_path = path_or_url
                self.poster_url = None
            else:
                # Load from URL
                response = urlopen(path_or_url)
                data = response.read()
                pixmap.loadFromData(data)
                self.poster_url = path_or_url
                self.poster_path = None

            # Scale the pixmap to fit the preview label while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                self.poster_preview.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.poster_preview.setPixmap(scaled_pixmap)
            self.poster_preview.setText("")  # Clear the "No poster selected" text
        except Exception as e:
            print(f"Error loading poster: {str(e)}")
            self.poster_preview.setText("Error loading image")

    def get_game_data(self):
        """Return a Game object with the entered data."""
        # If editing an existing game, preserve its ID
        game_id = self.game.id if self.game else None
        
        # Get all form data
        name = self.name_input.text()
        install_path = self.exe_input.text()
        genre = self.genre_input.text() or None
        release_date = self.date_input.text() or None
        description = self.desc_input.text() or None
        developers = [d.strip() for d in self.dev_input.text().split(',') if d.strip()] or None
        publishers = [p.strip() for p in self.pub_input.text().split(',') if p.strip()] or None
        
        # Create game object with all data
        return Game(
            id=game_id,
            name=name,
            type='steam' if hasattr(self, 'steam_app_id') else 'manual',
            app_id=getattr(self, 'steam_app_id', None),
            install_path=install_path,
            launch_command=install_path,
            genre=genre,
            is_installed=True,
            playtime=self.game.playtime if self.game else 0,
            metadata_fetched=True,
            release_date=release_date,
            description=description,
            developers=developers,
            publishers=publishers,
            poster_url=self.poster_url,
            poster_path=self.poster_path,
            background_url=getattr(self, 'background_url', None)
        )

    def on_metadata_fetched(self, metadata):
        """Handle successful metadata fetch"""
        self.progress_bar.hide()
        
        try:
            # Update form fields with fetched metadata
            self.name_input.setText(metadata.get("name", self.name_input.text()))
            self.genre_input.setText(metadata.get("genre", ""))
            self.date_input.setText(metadata.get("release_date", ""))
            self.desc_input.setText(metadata.get("description", ""))
            self.dev_input.setText(", ".join(metadata.get("developers", [])))
            self.pub_input.setText(", ".join(metadata.get("publishers", [])))
            
            # Store the Steam app ID and URLs for later use
            self.steam_app_id = metadata.get("app_id")
            
            # Load the poster image if available
            poster_url = metadata.get("poster_url")
            if poster_url:
                self.set_poster(poster_url, is_local=False)
            
            QMessageBox.information(self, "Success", "Game metadata fetched successfully!")
            
        except Exception as e:
            print(f"Error processing metadata: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to process metadata: {str(e)}") 
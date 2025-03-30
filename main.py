import sys
import os
import requests
import asyncio
import psutil
import qasync
import sqlite3
import subprocess
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QPushButton, QStackedWidget, 
    QWidget, QLabel, QGridLayout, QVBoxLayout, 
    QSizePolicy, QScrollArea, QSpacerItem, QFileDialog, QHBoxLayout,
    QFrame, QProgressDialog, QDialog, QTextEdit, QStatusBar
)
from PySide6.QtCore import QTimer, QUrl, Qt
from PySide6.QtGui import QAction, QIcon, QDesktopServices, QImage, QPixmap
from datetime import datetime

from game_search import search_local_games, STEAM_API_KEY, get_steam_id, get_steam_games
from system_optimizer import SystemOptimizer
from overlay import OverlayWindow, OverlayManager
from save_file import SaveFileManager
from store_tab import create_store_tabs
from interface_ui import Ui_MainWindow
from database import DatabaseManager
from game_card import GameCard
from game_details_dialog import GameDetailsDialog
from metadata_fetcher import MetadataFetcher
from game_manager import GameManager
from timer_manager import TimerManager
from ui_manager import UIManager
from models import Game
from filter_dialog import FilterDialog

# Get Steam ID at startup
STEAM_ID = get_steam_id()

class MainWindow(QMainWindow):
    # Common styles for progress dialogs
    PROGRESS_DIALOG_STYLE = """
        QProgressDialog {
            background-color: #2d2d2d;
            color: white;
        }
        QProgressBar {
            border: 2px solid #3B82F6;
            border-radius: 5px;
            text-align: center;
            background-color: #1a1a1a;
        }
        QProgressBar::chunk {
            background-color: #3B82F6;
            border-radius: 3px;
        }
        QLabel {
            color: white;
            font-size: 11px;
        }
        QPushButton {
            background-color: #2C5A68;
            color: white;
            border: none;
            padding: 5px 15px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #3B82F6;
        }
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clockwork")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet("background-color: #1e1e1e;")
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Create scroll area for game cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")
        main_layout.addWidget(scroll_area)
        
        # Create widget to hold grid layout
        grid_widget = QWidget()
        scroll_area.setWidget(grid_widget)
        
        # Create grid layout for game cards
        self.grid_layout = QGridLayout(grid_widget)
        self.grid_layout.setSpacing(10)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("QStatusBar { color: white; }")
        self.setStatusBar(self.status_bar)
        
        # Load games
        self.games = []
        self.load_games()
        
        # Create event loop
        self.loop = asyncio.get_event_loop()
        
        # Create and setup UI first
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon("icons/clockwork.png"))
        
        # Initialize managers after UI is created
        self.db_manager = DatabaseManager()
        self.game_manager = GameManager(self.db_manager)
        self.overlay_manager = OverlayManager()
        self.save_file_manager = SaveFileManager(self.ui, self)
        self.metadata_fetcher = MetadataFetcher()
        self.timer_manager = TimerManager(self)
        self.ui_manager = UIManager(self)

        # Connect metadata fetcher signals
        self.metadata_fetcher.progress.connect(self.update_metadata_progress)
        self.metadata_fetcher.finished.connect(self.on_metadata_fetch_complete)
        self.metadata_fetcher.error.connect(self.on_metadata_fetch_error)

        # Initialize game lists
        self.session_games = []  # Games added in current session

        # Create overlay window
        self.overlay_window = OverlayWindow()
        
        # Setup the library UI and store references to layouts
        self.ui_manager.setup_library_ui()
        self.games_layout = self.ui_manager.games_layout
        self.games_container = self.ui_manager.games_container

        # Store sidebar buttons
        self.sidebar_buttons = [
            self.ui.libraryBtn,
            self.ui.storeBtn,
            self.ui.optimizationBtn,
            self.ui.overlayBtn,
            self.ui.savefileBtn
        ]

        # Initialize store view
        self.store_view = create_store_tabs()
        self.store_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.ui.storeLayout.addWidget(self.store_view)
        
        # Initialize filters
        self.current_filters = {
            'genre': 'All Genres',
            'platform': 'All Platforms',
            'install_status': 'All Games'
        }
        
        # Connect signals
        self.setup_connections()
        
        # Set initial page and button state
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.libraryBtn.setChecked(True)
        
        # Load games from database and fetch metadata if needed
        self.loop.create_task(self.load_initial_games())
        
        # Show the window
        self.show()

    def load_games(self):
        try:
            # Connect to database
            conn = sqlite3.connect('games.db')
            cursor = conn.cursor()
            
            # Get all games
            cursor.execute('SELECT * FROM games')
            game_data = cursor.fetchall()
            
            # Get column names
            columns = [description[0] for description in cursor.description]
            
            # Create Game objects
            self.games = []
            for row in game_data:
                # Convert row to dictionary and remove unnecessary fields
                game_dict = dict(zip(columns, row))
                fields_to_remove = ['last_played', 'created_at', 'updated_at']
                for field in fields_to_remove:
                    if field in game_dict:
                        del game_dict[field]
                game = Game(**game_dict)
                self.games.append(game)
            
            conn.close()
            
            # Display games in grid
            self.display_games_in_grid()
            
        except Exception as e:
            print(f"Error loading games: {str(e)}")
            
        self.update_game_count()

    def create_game_card(self, game):
        try:
            card = QWidget()
            card.setObjectName("game-card")
            card.setStyleSheet("QWidget#game-card { background-color: #2d2d2d; border-radius: 10px; padding: 10px; margin: 5px; }")
            
            layout = QVBoxLayout()
            layout.setSpacing(5)
            
            poster_label = QLabel()
            poster_label.setFixedSize(300, 140)
            poster_label.setScaledContents(True)
            
            if game.poster_url and game.metadata_fetched:
                image = QImage()
                if image.loadFromData(requests.get(game.poster_url).content):
                    poster_label.setPixmap(QPixmap.fromImage(image))
            else:
                default_image = QPixmap(300, 140)
                default_image.fill(Qt.gray)
                poster_label.setPixmap(default_image)
            
            layout.addWidget(poster_label)
            
            title_label = QLabel(game.name)
            title_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
            title_label.setWordWrap(True)
            layout.addWidget(title_label)
            
            if game.genre:
                genre_label = QLabel(game.genre)
                genre_label.setStyleSheet("color: #aaaaaa; font-size: 12px;")
                genre_label.setWordWrap(True)
                layout.addWidget(genre_label)
            
            if game.rating and game.rating > 0:
                rating_label = QLabel(f"Rating: {game.rating:.1f}")
                rating_label.setStyleSheet("color: #aaaaaa; font-size: 12px;")
                layout.addWidget(rating_label)
            
            button_layout = QHBoxLayout()
            
            launch_button = QPushButton("Launch")
            launch_button.setStyleSheet("QPushButton { background-color: #5865f2; color: white; border: none; padding: 5px 10px; border-radius: 5px; } QPushButton:hover { background-color: #4752c4; }")
            launch_button.clicked.connect(lambda: self.launch_game(game))
            button_layout.addWidget(launch_button)
            
            details_button = QPushButton("Details")
            details_button.setStyleSheet("QPushButton { background-color: #4f545c; color: white; border: none; padding: 5px 10px; border-radius: 5px; } QPushButton:hover { background-color: #40444b; }")
            details_button.clicked.connect(lambda: self.show_game_details(game))
            button_layout.addWidget(details_button)
            
            layout.addLayout(button_layout)
            card.setLayout(layout)
            return card
            
        except Exception as e:
            return None

    def display_games_in_grid(self):
        try:
            # Store reference to current layout
            current_layout = self.grid_layout
            
            # Create new layout
            new_layout = QGridLayout()
            new_layout.setSpacing(10)
            new_layout.setContentsMargins(10, 10, 10, 10)
            
            # Calculate number of columns based on window width
            window_width = self.width()
            card_width = 320  # Card width + margins
            max_cols = max(1, window_width // card_width)
            
            # Add game cards to new layout
            row = 0
            col = 0
            for game in self.games:
                card = self.create_game_card(game)
                if card:
                    new_layout.addWidget(card, row, col)
                    col += 1
                    if col >= max_cols:
                        col = 0
                        row += 1
            
            # Get the parent widget
            parent_widget = current_layout.parent()
            if parent_widget:
                # Remove old layout
                parent_widget.layout().removeItem(current_layout)
                
                # Delete old layout and its widgets
                while current_layout.count():
                    item = current_layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                current_layout.deleteLater()
                
                # Set new layout
                parent_widget.setLayout(new_layout)
                self.grid_layout = new_layout
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to display games: {str(e)}")

    async def add_game(self, game: Game):
        """Add a new game to the database or update existing one."""
        try:
            # Validate Steam games have app_id
            if game.type == 'steam' and not game.app_id:
                return False
                
            # Add game to database
            game_id = self.db_manager.add_game(game)
            if game_id:
                # Update display
                self.show_games(self.db_manager.get_all_games())
            return True
            return False
        except Exception as e:
            print(f"Error adding game: {e}")
            return False

    async def load_initial_games(self):
        """Load games from database ONLY - NEVER fetch metadata on normal startup."""
        try:
            # Get all games from database
            self.games = self.db_manager.get_all_games()
            self.filtered_games = self.games.copy()
            
            # Update display with games from database - NO API calls
            self.ui_manager.update_library_display()
            
        except Exception as e:
            print(f"Error loading initial games: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load games: {str(e)}")

    def update_game_statuses(self):
        """Update the status of running games and installation status"""
        try:
            # Update running games
            for game in self.session_games[:]:  # Create a copy of the list to modify it
                if hasattr(game, 'process') and game.process:
                    # Check if the game process is still running
                    if not game.process.is_running():
                        # Game has closed
                        self.session_games.remove(game)
                        # Stop FPS monitoring if no games are running
                        if not self.session_games:
                            self.timer_manager.stop_fps_timer()
                            self.overlay_window.hide_overlay()
            
            # Update installation status for all games
            for game in self.games:
                game.check_installation_status()
            
            # Update the display to reflect any changes
            self.display_games_in_grid()
        except Exception as e:
            print(f"Error updating game statuses: {e}")
            self.timer_manager.stop_system_timer()

    def show_games(self, games):
        """Display games in a grid layout with metadata."""
        try:
            # Update the games list
            self.games = self.db_manager.get_all_games()
            self.filtered_games = self.games.copy()
            
            # Display games
            self.display_games_in_grid()
            
            # Update game count
            self.ui.gameCountLabel.setText(f"{len(self.games)} Games")
            
            # Populate filter dropdowns
            self.populate_filter_dropdowns()
            
        except Exception as e:
            print(f"Error showing games: {e}")
            QMessageBox.critical(self, "Error", f"Failed to display games: {str(e)}")

    def show_game_details(self, game):
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle(f"{game.name} - Details")
            dialog.setMinimumSize(600, 400)
            dialog.setStyleSheet("background-color: #2d2d2d; color: white;")
            
            layout = QVBoxLayout()
            
            # Add game details
            details_text = f"""
            <h2>{game.name}</h2>
            <p><b>Genre:</b> {game.genre or 'Unknown'}</p>
            <p><b>Release Date:</b> {game.release_date or 'Unknown'}</p>
            <p><b>Rating:</b> {f'{game.rating:.1f}' if game.rating and game.rating > 0 else 'Not Rated'}</p>
            <p><b>Developers:</b> {', '.join(game.developers) if game.developers else 'Unknown'}</p>
            <p><b>Publishers:</b> {', '.join(game.publishers) if game.publishers else 'Unknown'}</p>
            <p><b>Description:</b></p>
            <p>{game.description or 'No description available.'}</p>
            """
            
            details_label = QLabel(details_text)
            details_label.setWordWrap(True)
            details_label.setStyleSheet("color: white; padding: 10px;")
            layout.addWidget(details_label)
            
            # Add close button
            close_button = QPushButton("Close")
            close_button.setStyleSheet("""
                QPushButton {
                    background-color: #4f545c;
                    color: white;
                    border: none;
                    padding: 10px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #40444b;
                }
            """)
            close_button.clicked.connect(dialog.close)
            layout.addWidget(close_button)
            
            dialog.setLayout(layout)
            dialog.exec_()
            
        except Exception as e:
            print(f"Error showing game details: {str(e)}")

    def launch_game(self, game):
        """Launch a game based on its type."""
        try:
            if game.type == "steam":
                # Launch Steam game using steam:// protocol
                url = f"steam://rungameid/{game.app_id}"
                QDesktopServices.openUrl(QUrl(url))
            elif game.type == "epic":
                # Launch Epic game using os.startfile
                if game.launch_command:
                    os.startfile(game.launch_command)
            else:
                # Launch regular executable
                if game.launch_command:
                    subprocess.Popen(game.launch_command)
                    
            # Update playtime tracking
            game.last_launched = datetime.now()
            self.db_manager.update_game(game.id, {'last_launched': game.last_launched})
            
        except Exception as e:
            print(f"Error launching game: {e}")
            QMessageBox.critical(self, "Error", f"Failed to launch game: {str(e)}")

    def apply_filters(self, filter_type):
        """Apply filters to the game list"""
        # Map filter_type to actual UI filter names
        filter_map = {
            'genre': 'genreFilter',
            'platform': 'platformFilter',
            'install_status': 'installFilter'
        }
        
        # Get the actual filter widget name
        filter_widget = filter_map.get(filter_type)
        if filter_widget:
            self.current_filters[filter_type] = getattr(self.ui, filter_widget).currentText()
            self.filter_games()
            self.display_games_in_grid()

    def filter_games(self):
        """Filter games based on current filter settings"""
        self.filtered_games = self.games.copy()
        
        # Apply genre filter
        if self.current_filters['genre'] != 'All Genres':
            self.filtered_games = [game for game in self.filtered_games 
                                if game.genre and self.current_filters['genre'].lower() in game.genre.lower()]
        
        # Apply platform filter
        if self.current_filters['platform'] != 'All Platforms':
            platform = self.current_filters['platform'].lower()
            self.filtered_games = [game for game in self.filtered_games 
                                if game.type and game.type.lower() == platform]
        
        # Apply install status filter
        if self.current_filters['install_status'] != 'All Games':
            is_installed = self.current_filters['install_status'] == 'Installed'
            # Update installation status before filtering
            for game in self.filtered_games:
                game.check_installation_status()
            self.filtered_games = [game for game in self.filtered_games 
                                if game.is_installed == is_installed]
        
        # Update game count label
        self.ui.gameCountLabel.setText(f"{len(self.filtered_games)} Games")
        
        # Display the filtered games
        self.display_games_in_grid()

    def populate_filter_dropdowns(self):
        """Populate filter dropdowns with available options"""
        try:
            # Get unique values
            genres = set()
            platforms = set()
            
            for game in self.games:
                # Add genre
                if game.genre:
                    genres.add(game.genre)
                    
                # Add platform
                if game.type:
                    platforms.add(game.type)
                    
            # Sort values
            sorted_genres = sorted(list(genres))
            sorted_platforms = sorted(list(platforms))
            
            # Clear and populate genre filter
            self.ui.genreFilter.clear()
            self.ui.genreFilter.addItem("All Genres")
            self.ui.genreFilter.addItems(sorted_genres)
            
            # Clear and populate platform filter
            self.ui.platformFilter.clear()
            self.ui.platformFilter.addItem("All Platforms")
            # Add common platforms first
            common_platforms = ['steam', 'epic']
            for platform in common_platforms:
                if platform in sorted_platforms:
                    self.ui.platformFilter.addItem(platform.capitalize())
                    sorted_platforms.remove(platform)
            # Add remaining platforms
            self.ui.platformFilter.addItems(sorted_platforms)
            
            # Set up install status filter
            self.ui.installFilter.clear()
            self.ui.installFilter.addItems(["All Games", "Installed", "Not Installed"])
            
        except Exception as e:
            print(f"Error populating filter dropdowns: {e}")
            
    def on_metadata_fetched(self, games_with_metadata):
        """Handle fetched metadata"""
        try:
            # Update games in database with new metadata
            for game in games_with_metadata:
                game.metadata_fetched = True  # Mark as fetched
                self.db_manager.update_game(game)  # Update in database
            
            # Update the games list with the new metadata
            self.games = self.db_manager.get_all_games()
            self.filtered_games = self.games.copy()
            
            # Display all games
            self.display_games_in_grid()
            # Update game count
            self.ui.gameCountLabel.setText(f"{len(self.games)} Games")
            # Populate filter dropdowns
            self.populate_filter_dropdowns()
            
        except Exception as e:
            print(f"Error handling fetched metadata: {e}")
            QMessageBox.critical(self, "Error", f"Failed to update games with metadata: {str(e)}")

    def update_metadata_progress(self, current, total):
        """Update the progress dialog with detailed information."""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.setValue(current)
            percentage = int((current / total) * 100)
            self.progress_dialog.setLabelText(
                f"Fetching game metadata... ({current}/{total})\n"
                f"Progress: {percentage}%\n"
                f"Please wait while we gather information about your games..."
            )
            
    async def on_metadata_fetch_complete(self, games):
        """Handle completion of metadata fetching - ALWAYS mark as fetched"""
        try:
            # Update database with metadata
            updated_count = 0
            for game in games:
                # Build the update data - ALWAYS set metadata_fetched to True regardless of success
                # IMPORTANT: Do NOT include playtime in the update data to preserve actual playtime values
                update_data = {
                    'genre': game.genre,
                    'poster_url': game.poster_url,
                    'background_url': game.background_url,
                    'description': game.description,
                    'release_date': game.release_date,
                    'rating': game.rating,
                    'metacritic': game.metacritic,
                    'esrb_rating': game.esrb_rating,
                    'platforms': game.platforms,
                    'developers': game.developers,
                    'publishers': game.publishers,
                    'metadata_fetched': True  # <-- CRITICAL: ALWAYS set this to True to prevent endless retries
                }
                
                # Update game in database
                success = self.db_manager.update_game(game.id, update_data)
                if success:
                    updated_count += 1
            
            # Update UI
            self.games = self.db_manager.get_all_games()
            self.filtered_games = self.games.copy()
            self.ui_manager.update_library_display()
            
            # Close progress dialog if it exists
            if hasattr(self, 'progress_dialog') and self.progress_dialog:
                self.progress_dialog.close()
                
        except Exception as e:
            print(f"Error in on_metadata_fetch_complete: {e}")
            if hasattr(self, 'progress_dialog') and self.progress_dialog:
                self.progress_dialog.close()
            QMessageBox.critical(self, "Error", f"Failed to process metadata: {str(e)}")

    def on_metadata_fetch_error(self, error_msg):
        """Handle metadata fetching errors."""
        QMessageBox.warning(self, "Metadata Fetch Error", 
                          f"An error occurred while fetching game metadata: {error_msg}\n\nSome games may have incomplete information.")

    def browse_and_launch_game(self):
        """Open a file dialog to browse for a game executable and add it to the database."""
        try:
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Select Game Executable", "", "Executable Files (*.exe);;All Files (*)", options=options
            )

            if file_path:
                game_name = os.path.splitext(os.path.basename(file_path))[0]
                game = Game(
                    name=game_name,
                    type="manual",
                    install_path=file_path,
                    launch_command=file_path,
                    genre=None,  # Will be set by metadata
                    is_installed=True,
                    playtime=0,  # Initialize playtime to 0
                    metadata_fetched=False
                )
                
                # Add to database
                game_id = self.db_manager.add_game(game)
                if game_id:
                    # Update display
                    self.show_games(self.db_manager.get_all_games())
                    QMessageBox.information(self, "Success", f"Game added successfully: {game_name}")
                else:
                    QMessageBox.critical(self, "Error", "Failed to add game to database")
        except Exception as e:
            print(f"Error adding manual game: {e}")
            QMessageBox.critical(self, "Error", f"Failed to add game: {str(e)}")

    def handle_sidebar_button(self):
        """Handle sidebar button clicks and their states."""
        clicked_button = self.sender()
        for button in self.sidebar_buttons:
            if button != clicked_button:
                button.setChecked(False)

        # Stop timer for all tabs except optimization
        if clicked_button != self.ui.optimizationBtn:
            self.timer_manager.stop_system_timer()

        # Handle the specific button action
        if clicked_button == self.ui.libraryBtn:
            self.ui.stackedWidget.setCurrentIndex(0)
        elif clicked_button == self.ui.storeBtn:
            self.ui.stackedWidget.setCurrentIndex(4)
            self.store_view.updateGeometry()
        elif clicked_button == self.ui.optimizationBtn:
            self.ui.stackedWidget.setCurrentIndex(3)
            self.update_system_usage()
            self.timer_manager.start_system_timer()
        elif clicked_button == self.ui.overlayBtn:
            self.ui.stackedWidget.setCurrentIndex(2)
        elif clicked_button == self.ui.savefileBtn:
            self.ui.stackedWidget.setCurrentIndex(1)

    def show_store_tab(self):
        """Switch to the storeTab in the stacked widget."""
        if self.store_view:
            store_tab_index = self.ui.stackedWidget.indexOf(self.store_view)
            if store_tab_index != -1:
                self.ui.stackedWidget.setCurrentIndex(store_tab_index)

    def show_savefile_tab(self):
        """Switch to the saveFileTab in the stacked widget."""
        if self.ui.saveFileTab:
            savefile_tab_index = self.ui.stackedWidget.indexOf(self.ui.saveFileTab)
            if savefile_tab_index != -1:
                self.ui.stackedWidget.setCurrentIndex(savefile_tab_index)

    def show_overlay_tab(self):
        """Switch to the overlayTab in the stacked widget."""
        if self.ui.overlayTab:
            overlay_tab_index = self.ui.stackedWidget.indexOf(self.ui.overlayTab)
            if overlay_tab_index != -1:
                self.ui.stackedWidget.setCurrentIndex(overlay_tab_index)

    def toggle_overlay(self):
        """Show or hide the overlay window."""
        if self.overlay_window.isVisible():
            self.overlay_window.hide_overlay()
        else:
            self.overlay_window.show_overlay()

    def ask_for_game_search(self):
        reply = QMessageBox.question(self, 'Game Search', 'Do you want to search for games on your system?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.search_for_games()

    def search_for_games(self, query: str):
        """Search for games in the library."""
        if not query:
            self.filtered_games = self.games.copy()
            self.ui_manager.update_library_display()
            return

        query = query.lower()
        self.filtered_games = [
            game for game in self.games 
            if query in game.name.lower() or
               (game.genre and query in game.genre.lower())
        ]
        self.ui_manager.update_library_display()

    def show_optimization_tab(self):
        if self.ui.optimizationTab:
            optimization_tab_index = self.ui.stackedWidget.indexOf(self.ui.optimizationTab)
            if optimization_tab_index != -1:
                self.ui.stackedWidget.setCurrentIndex(optimization_tab_index)
                self.timer_manager.start_system_timer()

    def update_system_usage(self):
        """Update the system usage displays."""
        try:
            # Get system usage values
            cpu_usage, ram_usage, disk_usage = SystemOptimizer.get_system_usage()
            
            # Format the values
            cpu_text = f"{cpu_usage:.1f}%"
            ram_text = f"{ram_usage:.1f}%"
            disk_text = f"{disk_usage:.1f} MB/s"
            
            # Update the displays with the new values
            self.ui.cpuLabel.setText(cpu_text)
            self.ui.ramLabel.setText(ram_text)
            self.ui.diskLabel.setText(disk_text)
            
        except Exception as e:
            print(f"Error updating system usage: {e}")
            self.timer_manager.stop_system_timer()

    def show_homepage(self):
        """Switch to the homepage in the stacked widget."""
        self.ui.stackedWidget.setCurrentIndex(0)
        
    def show_filter_dialog(self):
        """Show the filter dialog and connect signals."""
        try:
            # Get current filter values
            current_filters = {
                'genre': self.ui.genreFilter.currentText(),
                'platform': self.ui.platformFilter.currentText(),
                'install_status': self.ui.installFilter.currentText()
            }
            
            # Create and show dialog
            self.filter_dialog = FilterDialog(self, current_filters)
            self.filter_dialog.filtersApplied.connect(self.apply_filter_dialog_results)
            
            # Show dialog as modal
            self.filter_dialog.exec_()
            
        except Exception as e:
            print(f"Error showing filter dialog: {e}")

    def apply_filter_dialog_results(self, filters):
        """Apply filters from the filter dialog."""
        try:
            # Update current filters
            self.current_filters = filters
            
            # Update UI dropdowns to match (for compatibility)
            self.ui.genreFilter.setCurrentText(filters['genre'])
            self.ui.platformFilter.setCurrentText(filters['platform'])
            self.ui.installFilter.setCurrentText(filters['install_status'])
            
            # Apply filters to games
            self.filter_games()
            
            # Update status message
            active_filters = []
            if filters['genre'] != 'All Genres':
                active_filters.append(f"Genre: {filters['genre']}")
            if filters['platform'] != 'All Platforms':
                active_filters.append(f"Platform: {filters['platform']}")
            if filters['install_status'] != 'All Games':
                active_filters.append(f"Status: {filters['install_status']}")
                
            if active_filters:
                self.status_bar.showMessage(f"Filters applied: {', '.join(active_filters)}", 5000)
            else:
                self.status_bar.showMessage("All filters cleared", 3000)
                
        except Exception as e:
            print(f"Error applying filter dialog results: {e}")
            QMessageBox.critical(self, "Error", f"Failed to apply filters: {str(e)}")
            
    def optimize_pc(self):
        """Run the PC optimization process."""
        try:
            # Delete temporary files
            deleted_files = SystemOptimizer.optimize_pc()
            
            # Close unnecessary processes
            SystemOptimizer.close_unnecessary_processes()
            
            QMessageBox.information(self, 'Optimization Complete', 
                                  f"Successfully deleted {deleted_files} temporary files.")
            # Update the system usage after optimization
            self.update_system_usage()
        except Exception as e:
            QMessageBox.warning(self, 'Optimization Error',
                              f"An error occurred during optimization: {str(e)}")

    def setup_connections(self):
        """Set up all button connections."""
        try:
            # Connect sidebar buttons
            for button in self.sidebar_buttons:
                button.clicked.connect(self.handle_sidebar_button)
            
            # Connect library buttons
            self.ui.manualAddBtn.clicked.connect(self.browse_and_launch_game)
            self.ui.searchGames.clicked.connect(self.ask_for_game_search)
            self.ui.refreshGames.clicked.connect(self.refresh_games)
            
            # Connect filter button
            self.ui.filterBtn.clicked.connect(self.show_filter_dialog)
            
            # Connect filter dropdowns (keep these for compatibility)
            self.ui.genreFilter.currentTextChanged.connect(lambda: self.apply_filters('genre'))
            self.ui.platformFilter.currentTextChanged.connect(lambda: self.apply_filters('platform'))
            self.ui.installFilter.currentTextChanged.connect(lambda: self.apply_filters('install_status'))
            
            # Connect search box
            self.ui.lineEdit.textChanged.connect(self.search_for_games)
            
            # Connect optimization buttons
            self.ui.optimizeNowBtn.clicked.connect(self.optimize_pc)
            
            # Connect overlay buttons
            self.ui.toggleOverlay.clicked.connect(self.toggle_overlay)
            
            # Connect store buttons - check if they exist first
            if hasattr(self.ui, 'steamStoreBtn'):
                self.ui.steamStoreBtn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://store.steampowered.com/")))
            
            # Connect save file buttons
            self.ui.browseBackupButton.clicked.connect(self.save_file_manager.browse_backup_folder)
            self.ui.backupButton.clicked.connect(self.save_file_manager.backup_save_files)
            
            # Set up periodic installation status check
            self.install_status_timer = QTimer()
            self.install_status_timer.timeout.connect(self.update_game_statuses)
            self.install_status_timer.start(30000)  # Check every 30 seconds
            
            # Ensure the store tab expands properly
            self.ui.storeTab.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.ui.storeLayout.setSpacing(0)
            self.ui.storeLayout.setContentsMargins(0, 0, 0, 0)
            
        except Exception as e:
            print(f"Error setting up connections: {e}")

    def resizeEvent(self, event):
        """Handle window resize events."""
        super().resizeEvent(event)
        # Only recalculate layout if we have existing games
        if hasattr(self, 'games') and self.games:
            try:
                # Calculate the number of columns based on window width
                available_width = self.width()
                card_width = 320  # Card width + margins
                max_cols = max(1, available_width // card_width)
                
                # Create new layout
                new_layout = QGridLayout()
                new_layout.setSpacing(10)
                new_layout.setContentsMargins(10, 10, 10, 10)
                
                # Add game cards to new layout
                row = 0
                col = 0
                for game in self.games:
                    card = self.create_game_card(game)
                    if card:
                        new_layout.addWidget(card, row, col)
                        col += 1
                        if col >= max_cols:
                            col = 0
                            row += 1
                
                # Get the parent widget
                parent_widget = self.grid_layout.parent()
                if parent_widget:
                    # Remove old layout
                    parent_widget.layout().removeItem(self.grid_layout)
                    
                    # Delete old layout and its widgets
                    while self.grid_layout.count():
                        item = self.grid_layout.takeAt(0)
                        if item.widget():
                            item.widget().deleteLater()
                    self.grid_layout.deleteLater()
                    
                    # Set new layout
                    parent_widget.setLayout(new_layout)
                    self.grid_layout = new_layout
                    
            except Exception as e:
                print(f"Error refreshing layout: {e}")

    def refresh_games(self):
        """Manual refresh - ONLY called when user explicitly requests it"""
        try:
            # Create a confirmation dialog to prevent accidental API calls
            reply = QMessageBox.question(
                self, 
                'Refresh Games', 
                'This will fetch games from Steam API. Continue?',
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                # Start the fetch_steam_games task
                self.loop.create_task(self.fetch_steam_games())
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to refresh games: {str(e)}")

    async def force_refresh_games(self):
        """Force refresh all games metadata regardless of previous fetch status"""
        # Show a confirmation dialog
        reply = QMessageBox.question(
            self, 
            "Force Refresh Metadata",
            "This will clear all existing metadata and fetch it again from Steam.\n"
            "This process may take several minutes.\n\n"
            "Do you want to continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Clear all metadata from database
            self.db_manager.clear_all_metadata()
            
            # Set force refresh flag
            self.metadata_fetcher.force_refresh = True
            
            # Show loading indicator
            self.ui.statusbar.showMessage("Refreshing all game metadata...")
            
            # Refresh games with fresh metadata
            self.loop.create_task(self.refresh_games())
            
            # Reset force refresh flag
            self.metadata_fetcher.force_refresh = False
            
            # Update status
            self.ui.statusbar.showMessage("Metadata refresh complete!", 5000)

    def update_fps(self):
        """Update FPS display for the currently running game."""
        try:
            # Get the currently running game's process
            for game in self.session_games:
                if hasattr(game, 'process') and game.process:
                    if game.process.is_running():
                        # Calculate and update FPS
                        fps = self.overlay_manager.get_fps()
                        if fps:
                            self.overlay_window.update_fps(fps)
                        break
        except Exception as e:
            print(f"Error updating FPS: {e}")
            self.timer_manager.stop_fps_timer()

    def create_progress_dialog(self, title, message, maximum):
        """Create a styled progress dialog"""
        dialog = QProgressDialog(message, "Cancel", 0, maximum, self)
        dialog.setWindowTitle(title)
        dialog.setWindowModality(Qt.WindowModal)
        dialog.setMinimumWidth(300)
        dialog.setStyleSheet(self.PROGRESS_DIALOG_STYLE)
        return dialog

    def update_library_display(self):
        """Update the library display with current games"""
        self.display_games_in_grid()
        self.ui.gameCountLabel.setText(f"{len(self.games)} Games")
        self.populate_filter_dropdowns()

    async def fetch_steam_games(self):
        """Fetch games from Steam API - this should ONLY be called manually when user explicitly requests it"""
        try:
            # Show progress dialog
            self.progress_dialog = self.ui_manager.create_progress_dialog(
                "Loading Games", 
                "Fetching games from Steam...", 
                100
            )
            self.progress_dialog.show()
            self.progress_dialog.setValue(10)
            
            # Fetch owned games from Steam
            games = await self.metadata_fetcher.fetch_owned_games()
            if not games:
                self.progress_dialog.close()
                QMessageBox.warning(self, "Warning", "No games found in your Steam library.")
                return
                
            self.progress_dialog.setValue(30)
            self.progress_dialog.setLabelText(f"Found {len(games)} games. Checking for new games...")
            
            # Get existing games from database to avoid duplicates
            existing_games = self.db_manager.get_all_games()
            existing_app_ids = {game.app_id for game in existing_games if game.app_id}
            
            # Filter for new games ONLY - we'll only process these
            new_games = []
            for game in games:
                if game.app_id and game.app_id not in existing_app_ids:
                    # This is a new game
                    game_id = self.db_manager.add_game(game)
                    if game_id:
                        game.id = game_id  # Set the database ID
                        new_games.append(game)
            
            total_new_games = len(new_games)
            
            if total_new_games > 0:
                self.progress_dialog.setValue(50)
                self.progress_dialog.setLabelText(f"Fetching metadata for {total_new_games} new games...")
                
                # ONLY fetch metadata for NEW games
                if new_games:
                    await self.metadata_fetcher.fetch_metadata_for_games(new_games)
                
                # Update the games list with all games from database
                self.games = self.db_manager.get_all_games()
                self.filtered_games = self.games.copy()
                
                # Update the UI with the new games
                self.ui_manager.update_library_display()
                
                self.progress_dialog.setValue(100)
                self.progress_dialog.close()
                
                QMessageBox.information(
                    self, 
                    "Success", 
                    f"Successfully added {total_new_games} new games to your library."
                )
            else:
                self.progress_dialog.close()
                QMessageBox.information(self, "No Updates Needed", "Your game library is already up to date.")
            
        except Exception as e:
            print(f"Error fetching Steam games: {e}")
            import traceback
            traceback.print_exc()
            if hasattr(self, 'progress_dialog') and self.progress_dialog:
                self.progress_dialog.close()
            QMessageBox.critical(self, "Error", f"Failed to fetch Steam games: {str(e)}")

    def update_game_count(self):
        try:
            total_games = len(self.games)
            games_with_metadata = len([g for g in self.games if g.metadata_fetched])
            games_without_metadata = total_games - games_with_metadata
            
            # Update the game count label with more detailed information
            if hasattr(self, 'ui') and hasattr(self.ui, 'gameCountLabel'):
                self.ui.gameCountLabel.setText(f"{total_games} Games in Library")
            
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(f"Total Games: {total_games} | With Metadata: {games_with_metadata} | Without Metadata: {games_without_metadata}")
        except Exception as e:
            print(f"Error updating game count: {str(e)}")

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        
        # Create and show the main window
        loop = qasync.QEventLoop(app)
        asyncio.set_event_loop(loop)
        
        with loop:
            window = MainWindow()
            loop.run_forever()
            
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)
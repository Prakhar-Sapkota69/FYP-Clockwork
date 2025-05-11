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
    QFrame, QProgressDialog, QDialog, QTextEdit, QStatusBar, QGraphicsDropShadowEffect,
    QColorDialog, QInputDialog
)
from PySide6.QtCore import QTimer, QUrl, Qt
from PySide6.QtGui import QAction, QIcon, QDesktopServices, QImage, QPixmap, QColor, QMovie
from datetime import datetime

from game_search import search_local_games, STEAM_API_KEY, get_steam_id, get_steam_games
from system_optimizer import SystemOptimizer
from overlay import OverlayWindow
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
from splash_screen import CustomSplashScreen
from manual_add_dialog import ManualAddGameDialog

# Get Steam ID at startup
STEAM_ID = get_steam_id()

class SpinnerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setModal(True)
        self.setAttribute(Qt.WA_TranslucentBackground)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.movie = QMovie("./icons/loading.gif")
        self.label.setMovie(self.movie)
        self.label.setFixedSize(48, 48)
        layout.addWidget(self.label)
        self.setFixedSize(100, 100)

    def start(self):
        self.movie.start()
        self.show()

    def stop(self):
        self.movie.stop()
        self.hide()

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
        
        # Create and show splash screen
        self.splash = CustomSplashScreen()
        self.splash.show()
        self.process_events()
        
        # Initialize overlay window first
        self.overlay_window = OverlayWindow(self)
        self.overlay_window.hide()  # Start hidden
        
        # Initialize UI with loading indicators
        self.init_ui_with_loading()

    def process_events(self):
        """Process pending events to update the splash screen."""
        QApplication.processEvents()

    def init_ui_with_loading(self):
        """Initialize the UI with loading indicators."""
        total_steps = 10
        current_step = 0
        
        # Set window properties
        self.splash.set_progress(current_step, "Setting up window properties...")
        self.setStyleSheet("""
            QMainWindow {
                background-color: #202C59;
            }
            QLabel {
                color: #B4CDED;
            }
            QPushButton {
                background-color: #B4CDED;
                color: #202C59;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #9BB8E0;
            }
            QPushButton:pressed {
                background-color: #8AA8D0;
            }
            QLineEdit {
                background-color: #2A3A6A;
                color: #B4CDED;
                border: 2px solid #B4CDED;
                border-radius: 6px;
                padding: 8px 12px;
                selection-background-color: #B4CDED;
                selection-color: #202C59;
            }
            QLineEdit:focus {
                border: 2px solid #9BB8E0;
            }
        """)
        current_step += 1
        
        # Create central widget and UI
        self.splash.set_progress(current_step * 10, "Creating user interface...")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon("icons/clockwork.png"))
        current_step += 1
        
        # Initialize managers
        self.splash.set_progress(current_step * 10, "Initializing database...")
        self.db_manager = DatabaseManager()
        current_step += 1
        
        self.splash.set_progress(current_step * 10, "Setting up game management...")
        self.game_manager = GameManager(self.db_manager)
        self.save_file_manager = SaveFileManager(self.ui, self)
        current_step += 1
        
        self.splash.set_progress(current_step * 10, "Configuring metadata fetcher...")
        self.metadata_fetcher = MetadataFetcher()
        self.metadata_fetcher.api_key = STEAM_API_KEY
        self.metadata_fetcher.steam_id = STEAM_ID
        self.metadata_fetcher.db_manager = self.db_manager
        current_step += 1
        
        # Setup image cache
        self.splash.set_progress(current_step * 10, "Setting up image cache...")
        self.image_cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache", "images")
        os.makedirs(self.image_cache_dir, exist_ok=True)
        self.image_cache = {}
        current_step += 1
        
        # Initialize timer manager
        self.splash.set_progress(current_step * 10, "Initializing timer manager...")
        self.timer_manager = TimerManager(self)
        current_step += 1
        
        # Setup scroll area and grid
        self.splash.set_progress(current_step * 10, "Creating game library interface...")
        self.setup_scroll_area()
        current_step += 1
        
        # Setup status bar
        self.splash.set_progress(current_step * 10, "Setting up status bar...")
        self.setup_status_bar()
        current_step += 1
        
        # Style sidebar buttons
        for button in self.ui.leftMenu.findChildren(QPushButton):
            button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #B4CDED;
                    border: none;
                    border-radius: 8px;
                    padding: 12px;
                    text-align: left;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2A3A6A;
                    color: #FFFFFF;
                }
                QPushButton:checked {
                    background-color: #B4CDED;
                    color: #202C59;
                }
            """)
        
        # Style toolbar buttons (filter, refresh, etc.)
        toolbar_buttons = [
            self.ui.filterBtn, 
            self.ui.refreshGames, 
            self.ui.searchGames, 
            self.ui.manualAddBtn
        ]
        
        for button in toolbar_buttons:
            button.setStyleSheet("""
                QPushButton {
                    color: #202C59;
                    font-size: 14px;
                    font-weight: 700;
                    background: #B4CDED;
                    border-radius: 8px;
                    padding: 8px 16px;
                    border: 2px solid #9BB8E0;
                    min-height: 36px;
                }
                QPushButton:hover {
                    background: #9BB8E0;
                    border: 2px solid #8AA8D0;
                }
                QPushButton:pressed {
                    background: #8AA8D0;
                    border: 2px solid #7A98C0;
                }
            """)
            
        # Style manual add button separately with more rounded corners
        self.ui.manualAddBtn.setStyleSheet("""
            QPushButton {
                color: #202C59;
                font-size: 14px;
                font-weight: 700;
                background: #B4CDED;
                border-radius: 12px;
                padding: 8px 16px;
                border: 2px solid #9BB8E0;
                min-height: 36px;
                min-width: 36px;
            }
            QPushButton:hover {
                background: #9BB8E0;
                border: 2px solid #8AA8D0;
            }
            QPushButton:pressed {
                background: #8AA8D0;
                border: 2px solid #7A98C0;
            }
        """)
        
        # Make the sidebar background darker
        self.ui.leftMenu.setStyleSheet("""
            QWidget#leftMenu {
                background-color: #1A2547;
                border-right: 1px solid #2A3A6A;
            }
        """)
        
        # Style the search box and its clear button
        self.ui.lineEdit.setStyleSheet("""
            QLineEdit {
                color: #B4CDED;
                font-size: 14px;
                font-weight: 700;
                background: #2A3A6A;
                border-radius: 8px;
                padding: 8px 16px;
                border: 2px solid #B4CDED;
                min-height: 36px;
            }
            QLineEdit:focus {
                background: #2A3A6A;
                border: 2px solid #9BB8E0;
            }
        """)
        
        self.ui.clearSearchBtn.setStyleSheet("""
            QPushButton {
                color: #202C59;
                font-size: 14px;
                font-weight: 700;
                background: #B4CDED;
                border-radius: 8px;
                padding: 8px 16px;
                border: 2px solid #9BB8E0;
                min-height: 36px;
            }
            QPushButton:hover {
                background: #9BB8E0;
                border: 2px solid #8AA8D0;
            }
            QPushButton:pressed {
                background: #8AA8D0;
                border: 2px solid #7A98C0;
            }
        """)
        
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
        
        # Style game count label
        self.ui.gameCountLabel.setStyleSheet("""
            QLabel {
                color: #B4CDED;
                font-size: 14px;
                font-weight: 700;
                background: #2A3A6A;
                border-radius: 12px;
                padding: 8px 16px;
                border: 2px solid #B4CDED;
                min-height: 36px;
            }
            QLabel:hover {
                background: #2A3A6A;
                border: 2px solid #9BB8E0;
            }
        """)
        
        # Connect signals and initialize game lists
        self.splash.set_progress(current_step * 10, "Connecting signals...")
        self.connect_signals()
        self.initialize_game_lists()
        self.setup_connections()
        
        # Set initial page and button state
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.libraryBtn.setChecked(True)
        
        # Create event loop
        self.loop = asyncio.get_event_loop()
        
        # Final setup
        self.splash.set_progress(100, "Loading complete!")
        QTimer.singleShot(1000, self.finish_loading)  # Show 100% for 1 second

    def setup_scroll_area(self):
        """Setup scroll area for game cards."""
        self.scroll_area = QScrollArea(self.ui.homePage)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea { 
                border: none; 
                background-color: #202C59; 
            }
            QScrollBar:vertical {
                border: none;
                background: #2A3A6A;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #B4CDED;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #9BB8E0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        # Create container widget with expanding size policy
        self.grid_widget = QWidget()
        self.grid_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.grid_widget.setStyleSheet("background-color: #1e1e1e;")
        self.scroll_area.setWidget(self.grid_widget)
        
        # Create main layout for the grid widget
        self.main_layout = QVBoxLayout(self.grid_widget)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(20)
        
        # Create grid layout with proper spacing
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(20)
        self.main_layout.addLayout(self.grid_layout)
        
        # Add stretch to push content to the top
        self.main_layout.addStretch()
        
        # Add to main layout
        self.ui.homeLayout.addWidget(self.scroll_area)

    def setup_status_bar(self):
        """Setup the status bar."""
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar { 
                color: #B4CDED; 
                background-color: #1A2547;
                padding: 5px;
                font-size: 13px;
            }
        """)
        self.setStatusBar(self.status_bar)

    def connect_signals(self):
        """Connect metadata fetcher signals."""
        self.metadata_fetcher.progress.connect(self.update_metadata_progress)
        self.metadata_fetcher.finished.connect(self.on_metadata_fetch_complete)
        self.metadata_fetcher.error.connect(self.on_metadata_fetch_error)

    def initialize_game_lists(self):
        """Initialize game lists and persistent card widgets."""
        self.games = []
        self.session_games = []
        self.filtered_games = []
        self.card_widgets = {}  # {game.id: GameCard}

    def finish_loading(self):
        """Complete the loading process and show the main window."""
        self.splash.finish(self)
        self.show()
        self.spinner_dialog = SpinnerDialog(self)
        self.spinner_dialog.start()
        asyncio.create_task(self.load_initial_games())

    def load_games(self):
        try:
            print("[DEBUG] Starting load_games")
            # Get games from database manager instead of direct SQL
            self.games = self.db_manager.get_all_games()
            print(f"[DEBUG] load_games: Retrieved {len(self.games)} games from database")
            
            # Initialize filtered_games with all games
            self.filtered_games = self.games.copy()
            
            # Use our new force refresh method to ensure UI is updated correctly
            self.force_ui_refresh()
            
            # Update game count
            self.update_game_count()
            print("[DEBUG] load_games complete")
            
        except Exception as e:
            print(f"Error loading games: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to load games: {str(e)}")

    def create_game_card(self, game):
        # Reuse card if it exists
        if hasattr(self, 'card_widgets') and game.id in self.card_widgets:
            return self.card_widgets[game.id]
        card = GameCard(game, parent=self)
        card.clicked.connect(self.show_game_details)
        if hasattr(self, 'card_widgets'):
            self.card_widgets[game.id] = card
        return card

    def setup_connections(self):
        """Set up signal connections"""
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
            
            # Connect search box and clear button
            self.ui.lineEdit.textChanged.connect(self.handle_search)
            self.ui.clearSearchBtn.clicked.connect(self.clear_search)
            
            # Connect optimization buttons
            self.ui.cleanTempBtn.clicked.connect(self.clean_temp_files)
            self.ui.manageProcessesBtn.clicked.connect(self.manage_processes)
            
            # Connect overlay buttons
            self.ui.toggleOverlayBtn.clicked.connect(self.toggle_overlay)
            
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
            
            # Initialize available filter options
            self.available_genres = []
            self.available_platforms = []
            
            # Connect signals for overlay tab
            self.ui.topLeftBtn.clicked.connect(lambda: self.handle_position_click("top_left"))
            self.ui.topRightBtn.clicked.connect(lambda: self.handle_position_click("top_right"))
            self.ui.bottomLeftBtn.clicked.connect(lambda: self.handle_position_click("bottom_left"))
            self.ui.bottomRightBtn.clicked.connect(lambda: self.handle_position_click("bottom_right"))
            self.ui.colorPicker.clicked.connect(self.handle_color_click)
            self.ui.sizeSlider.valueChanged.connect(self.handle_size_change)
            
            # Set initial position
            self.handle_position_click("top_right")
            
        except Exception as e:
            print(f"Error setting up connections: {e}")

    def handle_color_click(self):
        """Handle color picker button click"""
        try:
            # Get current color from overlay
            current_color = QColor(self.overlay_window.text_color)
            
            # Open color dialog with current color
            color = QColorDialog.getColor(current_color, self, "Choose Text Color")
            
            if color.isValid():
                # Convert to hex
                hex_color = color.name()
                
                # Update overlay text color
                self.overlay_window.set_text_color(hex_color)
                
                # Update color picker button color
                self.ui.colorPicker.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {hex_color};
                        border: 2px solid #2C5A68;
                        border-radius: 8px;
                    }}
                    QPushButton:hover {{
                        border: 2px solid #3B82F6;
                    }}
                """)
        except Exception as e:
            print(f"Error in handle_color_click: {e}")

    def handle_size_change(self, value):
        """Handle size slider value change"""
        try:
            # Update overlay text size
            self.overlay_window.set_text_size(value)
        except Exception as e:
            print(f"Error handling size change: {e}")

    def resizeEvent(self, event):
        """Handle window resize events."""
        super().resizeEvent(event)
        # Only recalculate layout if we have existing games and cards
        if hasattr(self, 'filtered_games') and self.filtered_games and hasattr(self, 'game_cards'):
            try:
                # Calculate the number of columns based on window width
                available_width = self.scroll_area.viewport().width() - 60  # Subtract margins
                card_width = 220  # Fixed card width
                spacing = 20  # Spacing between cards
                
                # Calculate new number of columns
                new_max_cols = max(1, (available_width + spacing) // (card_width + spacing))
                
                # Only update if the number of columns has changed significantly
                if abs(new_max_cols - self.max_cols) > 0:
                    print(f"[DEBUG] Resize: updating from {self.max_cols} to {new_max_cols} columns")
                    self.max_cols = new_max_cols
                    
                    # Remove all widgets from the layout
                    while self.grid_layout.count():
                        item = self.grid_layout.takeAt(0)
                        if item.widget():
                            self.grid_layout.removeWidget(item.widget())
                    
                    # Re-add all cards in the new layout
                    row = 0
                    col = 0
                    for card in self.game_cards:
                        # Let the card expand, do not set fixed width
                        self.grid_layout.addWidget(card, row, col)
                        col += 1
                        if col >= self.max_cols:
                            col = 0
                            row += 1
                    
                    # Add spacer at the end
                    spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
                    self.grid_layout.addItem(spacer, row + 1, 0, 1, self.max_cols)
                    
                    # Force layout update
                    self.grid_widget.updateGeometry()
                    self.grid_layout.update()
                    self.scroll_area.viewport().update()
                
            except Exception as e:
                print(f"Error in resize event: {str(e)}")
                import traceback
                traceback.print_exc()

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
                        fps = self.overlay_window.get_fps()
                        if fps:
                            self.overlay_window.update_fps(fps)
                        break
        except Exception as e:
            print(f"Error updating FPS: {e}")
            self.timer_manager.stop_fps_timer()

    def create_progress_dialog(self, title, message, min_value=0, max_value=100):
        """Create a styled progress dialog"""
        dialog = QProgressDialog(message, "Cancel", min_value, max_value, self)
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

    def force_ui_refresh(self):
        """Force a complete refresh of the UI to ensure games are displayed correctly."""
        try:
            print("[DEBUG] Starting force_ui_refresh")
            
            # Make sure we have the latest data
            self.games = self.db_manager.get_all_games()
            self.filtered_games = self.games.copy()
            
            print(f"[DEBUG] Force refresh: retrieved {len(self.games)} games from database")
            
            # Remove all existing widgets from the grid layout
            if hasattr(self, 'grid_layout') and self.grid_layout:
                while self.grid_layout.count():
                    item = self.grid_layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
            
            # Create new grid widget if it doesn't exist
            if not hasattr(self, 'grid_widget') or not self.grid_widget:
                self.grid_widget = QWidget()
                self.grid_layout = QGridLayout(self.grid_widget)
            
            # Update grid widget styling
            self.grid_widget.setStyleSheet("""
                background-color: #1e1e1e;
            """)
            
            # Configure grid layout
            self.grid_layout.setSpacing(20)
            self.grid_layout.setContentsMargins(30, 30, 30, 30)
            self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            
            # Calculate optimal number of columns
            window_width = self.width()
            card_width = 340  # Card width + margins + spacing
            max_cols = max(1, int((window_width - 60) / card_width))
            
            print(f"[DEBUG] Force refresh: Window width {window_width}px, using {max_cols} columns")
            
            # Check if filtered_games is empty
            if not self.filtered_games:
                # Create a message for empty library
                empty_widget = QWidget()
                empty_layout = QVBoxLayout(empty_widget)
                
                icon_label = QLabel("🎮")
                icon_label.setStyleSheet("font-size: 64px; color: #4f545c; margin-bottom: 20px;")
                icon_label.setAlignment(Qt.AlignCenter)
                
                message_label = QLabel("Your game library is empty")
                message_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff;")
                message_label.setAlignment(Qt.AlignCenter)
                
                sub_message_label = QLabel("Click 'Import Games' to add games from Steam or 'Add Game' to manually add a game")
                sub_message_label.setStyleSheet("font-size: 14px; color: #b9bbbe;")
                sub_message_label.setAlignment(Qt.AlignCenter)
                sub_message_label.setWordWrap(True)
                
                empty_layout.addStretch()
                empty_layout.addWidget(icon_label)
                empty_layout.addWidget(message_label)
                empty_layout.addWidget(sub_message_label)
                empty_layout.addStretch()
                
                self.grid_layout.addWidget(empty_widget, 0, 0, 1, max_cols)
            else:
                # Add game cards to the layout
                row = 0
                col = 0
                cards_added = 0
                
                for game in self.filtered_games:
                    card = self.create_game_card(game)
                    if card:
                        self.grid_layout.addWidget(card, row, col)
                        cards_added += 1
                        col += 1
                        if col >= max_cols:
                            col = 0
                            row += 1
                
                print(f"[DEBUG] Force refresh: Added {cards_added} game cards to grid")
            
            # Set the widget to the scroll area
            self.scroll_area.setWidget(self.grid_widget)
            
            # Update game count
            self.ui.gameCountLabel.setText(f"{len(self.filtered_games)} Games")
            
            # Force layout updates
            self.grid_widget.updateGeometry()
            self.grid_layout.update()
            self.scroll_area.viewport().update()
            QApplication.processEvents()
            
            print("[DEBUG] Force UI refresh complete")
            
        except Exception as e:
            print(f"Error in force_ui_refresh: {str(e)}")
            import traceback
            traceback.print_exc()

    async def fetch_metadata_for_new_games(self):
        """Fetch metadata for games that don't have it yet."""
        try:
            # Get games without metadata
            games_without_metadata = [game for game in self.games if not game.metadata_fetched]
            
            if not games_without_metadata:
                print("[DEBUG] No games without metadata found")
                return
                
            print(f"[DEBUG] Fetching metadata for {len(games_without_metadata)} games")
            
            # Create progress dialog
            self.progress_dialog = self.create_progress_dialog(
                "Fetching Metadata", 
                f"Fetching metadata for {len(games_without_metadata)} games...",
                0,
                len(games_without_metadata)
            )
            self.progress_dialog.show()
            
            # Fetch metadata
            updated_games = await self.metadata_fetcher.fetch_metadata_for_games(games_without_metadata)
            
            # Close the progress dialog
            self.progress_dialog.close()
            
            if updated_games:
                # Refresh the UI
                self.force_ui_refresh()
                QMessageBox.information(
                    self, 
                    "Metadata Update", 
                    f"Successfully updated metadata for {len(updated_games)} games."
                )
            
        except Exception as e:
            print(f"Error fetching metadata: {e}")
            import traceback
            traceback.print_exc()
            if hasattr(self, 'progress_dialog') and self.progress_dialog:
                self.progress_dialog.close()
            QMessageBox.critical(self, "Error", f"Failed to fetch metadata: {str(e)}")

    async def fetch_steam_games(self):
        """Fetch games from Steam and add them to the database."""
        try:
            # Create progress dialog
            self.progress_dialog = self.create_progress_dialog(
                "Loading Games", 
                "Fetching games from Steam..."
            )
            self.progress_dialog.show()
            
            print("[DEBUG] Starting to fetch games from Steam...")
            
            # Fetch games using metadata fetcher
            games = await self.metadata_fetcher.fetch_owned_games()
            
            print(f"[DEBUG] Fetched {len(games) if games else 0} games from Steam")
            
            if games:
                total_new_games = 0
                self.progress_dialog.setMaximum(len(games))
                
                # Add each game to database
                for i, game in enumerate(games):
                    # Update progress
                    self.progress_dialog.setValue(i)
                    self.progress_dialog.setLabelText(f"Processing {game.name}...")
                    print(f"[DEBUG] Processing game {i+1}/{len(games)}: {game.name}")
                    
                    # Add game to database
                    game_id = self.db_manager.add_game(game)
                    if game_id:
                        total_new_games += 1
                        print(f"[DEBUG] Added game to database: {game.name}, ID: {game_id}")
                
                print(f"[DEBUG] Added total of {total_new_games} new games to database")
                
                # Force a complete UI refresh to update the game list display
                self.force_ui_refresh()
                
                # Also populate filter dropdowns
                self.populate_filter_dropdowns()
                
                self.progress_dialog.setValue(100)
                self.progress_dialog.close()
                
                QMessageBox.information(
                    self, 
                    "Success", 
                    f"Successfully added {total_new_games} new games to your library."
                )
                
                # Fetch metadata for new games if any were added
                if total_new_games > 0:
                    await self.fetch_metadata_for_new_games()
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

    def clean_temp_files(self):
        """Clean temporary files from the system."""
        try:
            # Delete temporary files
            deleted_files = SystemOptimizer.optimize_pc()
            
            # Show success message
            QMessageBox.information(
                self, 
                'Cleanup Complete', 
                f"Successfully deleted {deleted_files} temporary files."
            )
            
            # Update the system usage display
            self.update_system_usage()
            
        except Exception as e:
            QMessageBox.warning(
                self, 
                'Cleanup Error',
                f"An error occurred while cleaning temporary files: {str(e)}"
            )

    def manage_processes(self):
        """Show dialog to manage high-demand processes."""
        try:
            # Get list of high-demand processes
            processes = SystemOptimizer.get_unnecessary_processes()
            
            if not processes:
                QMessageBox.information(
                    self, 
                    "System Processes", 
                    "No high-demand processes found.\nAll system processes are running normally."
                )
                return
            
            # Create process list text with better formatting
            process_list = "\n".join([
                f"{idx}. {name} (PID: {pid})\n   • CPU Usage: {cpu:.1f}%\n   • Memory Usage: {mem:.1f}%" 
                for idx, (pid, name, cpu, mem) in enumerate(processes, start=1)
            ])
            
            # Show dialog with process list and options
            input_dialog = QInputDialog(self)
            input_dialog.setWindowTitle("High-Demand Processes Found")
            input_dialog.setLabelText(
                "The following processes are using high system resources:\n\n"
                f"{process_list}\n\n"
                "To end processes, enter their numbers (comma-separated)\n"
                "Example: 1,3 (to end processes 1 and 3)\n"
                "Or type 'all' to end all listed processes:"
            )
            input_dialog.setTextValue("")
            
            ok = input_dialog.exec_()
            if ok:
                input_text = input_dialog.textValue().strip()
                
                if not input_text:
                    return
                
                if input_text.lower() == 'all':
                    to_kill_indices = range(1, len(processes) + 1)
                else:
                    try:
                        to_kill_indices = [
                            int(i.strip()) for i in input_text.split(',') 
                            if i.strip().isdigit()
                        ]
                    except ValueError:
                        QMessageBox.warning(
                            self, 
                            "Invalid Input", 
                            "Invalid input format. Please enter numbers separated by commas."
                        )
                        return
                
                if not to_kill_indices:
                    QMessageBox.warning(
                        self,
                        "Invalid Input",
                        "No valid process numbers entered."
                    )
                    return
                
                # End selected processes
                terminated_count = 0
                failed_count = 0
                for idx in to_kill_indices:
                    if 1 <= idx <= len(processes):
                        pid = processes[idx - 1][0]
                        name = processes[idx - 1][1]
                        try:
                            psutil.Process(pid).terminate()
                            terminated_count += 1
                        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                            failed_count += 1
                
                # Show summary message
                summary = []
                if terminated_count > 0:
                    summary.append(f"Successfully terminated {terminated_count} process(es)")
                if failed_count > 0:
                    summary.append(f"Failed to terminate {failed_count} process(es)")
                
                if summary:
                    QMessageBox.information(
                        self,
                        "Process Management Complete",
                        "\n".join(summary)
                    )
                
                # Update system usage display after terminating processes
                self.update_system_usage()
            
        except Exception as e:
            QMessageBox.warning(
                self, 
                'Process Management Error',
                f"An error occurred while managing processes: {str(e)}"
            )

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
            # Clear search when switching to library tab
            self.clear_search()
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

    def handle_search(self, query: str):
        """Handle search input and update clear button visibility"""
        # Only perform search if we're in the library tab
        if self.ui.stackedWidget.currentIndex() != 0:
            return
            
        # Show/hide clear button based on whether there's text
        self.ui.clearSearchBtn.setVisible(bool(query))
        
        # Perform search
        self.search_for_games(query)
    
    def clear_search(self):
        """Clear the search box and reset the display"""
        # Only clear if we're in the library tab
        if self.ui.stackedWidget.currentIndex() != 0:
            return
            
        self.ui.lineEdit.clear()
        self.ui.clearSearchBtn.setVisible(False)
        self.filtered_games = self.games.copy()
        self.display_games_in_grid()
        self.ui.gameCountLabel.setText(f"{len(self.games)} Games")

    def search_for_games(self, query: str):
        """Search for games in the library."""
        # Only search if we're in the library tab
        if self.ui.stackedWidget.currentIndex() != 0:
            return
            
        if not query:
            self.filtered_games = self.games.copy()
            self.display_games_in_grid()
            return

        query = query.lower()
        self.filtered_games = [
            game for game in self.games 
            if (
                # Search in game name
                query in game.name.lower() or
                # Search in genre
                (game.genre and query in game.genre.lower()) or
                # Search in platform/type
                (game.type and query in game.type.lower()) or
                # Search in installation status
                (game.is_installed and "installed" in query) or
                (not game.is_installed and "not installed" in query)
            )
        ]
        
        # Update display
        self.display_games_in_grid()
        
        # Update game count with search results
        if query:
            self.ui.gameCountLabel.setText(f"{len(self.filtered_games)} Games Found")
        else:
            self.ui.gameCountLabel.setText(f"{len(self.games)} Games")

    def toggle_overlay(self):
        """Toggle the overlay window visibility"""
        try:
            print("[DEBUG] Toggle overlay called")
            if self.overlay_window.isVisible():
                print("[DEBUG] Overlay is visible, hiding it")
                self.overlay_window.hide_overlay()
            else:
                print("[DEBUG] Overlay is hidden, showing it")
                self.overlay_window.show_overlay()
        except Exception as e:
            print(f"[ERROR] Error in toggle_overlay: {e}")
            import traceback
            traceback.print_exc()

    def ask_for_game_search(self):
        """Ask user if they want to search for games and handle the search process."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Import Games")
        msg_box.setText("This will import games from your steam account. Do you want to continue? (Steam needs to be installed)")
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        
        # Set the Steam icon for both window and message box
        icon = QIcon("./icons/steam.png")
        msg_box.setWindowIcon(icon)
        
        # Set the Steam icon as the dialog's icon
        steam_pixmap = QPixmap("./icons/steam.png")
        if not steam_pixmap.isNull():
            # Scale the icon to a reasonable size (48x48 pixels)
            steam_pixmap = steam_pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            msg_box.setIconPixmap(steam_pixmap)
        
        reply = msg_box.exec_()
        if reply == QMessageBox.Yes:
            # Call fetch_steam_games instead of search_for_games since this is for finding new games
            self.loop.create_task(self.fetch_steam_games())

    def browse_and_launch_game(self, game=None):
        """Open dialog to browse for game executable and add/edit game."""
        try:
            print(f"[DEBUG] browse_and_launch_game called with game: {game.name if game else 'None'}")
            if game:
                print(f"[DEBUG] Editing game with type: {game.type}")
                
            dialog = ManualAddGameDialog(self, game)
            if dialog.exec_() == QDialog.Accepted:
                game_data = dialog.get_game_data()
                print(f"[DEBUG] Game data type after dialog: {game_data.type}")
                
                if not game_data.name or not game_data.install_path:
                    QMessageBox.warning(self, "Error", "Game name and executable path are required.")
                    return
                
                if game:  # Editing existing game
                    # Convert game object to dictionary for update
                    update_data = {
                        'name': game_data.name,
                        'type': game.type,  # Preserve the game type
                        'install_path': game_data.install_path,
                        'launch_command': game_data.launch_command,
                        'genre': game_data.genre,
                        'release_date': game_data.release_date,
                        'description': game_data.description,
                        'developers': game_data.developers,
                        'publishers': game_data.publishers,
                        'poster_url': game_data.poster_url,
                        'background_url': game_data.background_url,
                        'metadata_fetched': True
                    }
                    
                    # Update the game in the database
                    if self.db_manager.update_game(game.id, update_data):
                        print(f"[DEBUG] Successfully updated game in database with ID: {game.id}")
                        # Refresh the games list
                        self.games = self.db_manager.get_all_games()
                        self.filtered_games = self.games.copy()
                        
                        # Clear and rebuild the grid layout
                        while self.grid_layout.count():
                            item = self.grid_layout.takeAt(0)
                            if item.widget():
                                item.widget().deleteLater()
                        
                        # Display games and update UI
                        self.display_games_in_grid()
                        self.populate_filter_dropdowns()
                        self.update_game_count()
                        
                        QMessageBox.information(self, "Success", f"Game updated successfully: {game_data.name}")
                    else:
                        QMessageBox.critical(self, "Error", "Failed to update game in database")
                else:  # Adding new game
                    # Add to database
                    game_id = self.db_manager.add_game(game_data)
                    if game_id:
                        print(f"[DEBUG] Successfully added new game to database with ID: {game_id}")
                        # Refresh the games list
                        self.games = self.db_manager.get_all_games()
                        self.filtered_games = self.games.copy()
                        
                        # Clear and rebuild the grid layout
                        while self.grid_layout.count():
                            item = self.grid_layout.takeAt(0)
                            if item.widget():
                                item.widget().deleteLater()
                        
                        # Display games and update UI
                        self.display_games_in_grid()
                        self.populate_filter_dropdowns()
                        self.update_game_count()
                        
                        QMessageBox.information(self, "Success", f"Game added successfully: {game_data.name}")
                    else:
                        QMessageBox.critical(self, "Error", "Failed to add game to database")
        except Exception as e:
            print(f"Error {'editing' if game else 'adding'} manual game: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to {'edit' if game else 'add'} game: {str(e)}")

    def edit_game(self, game):
        """Open the edit dialog for an existing game."""
        self.browse_and_launch_game(game)

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

    def on_metadata_fetch_complete(self, games):
        """Handle completion of metadata fetching."""
        try:
            # Update database with metadata
            updated_count = 0
            for game in games:
                # Build the update data - ALWAYS set metadata_fetched to True
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
                    'metadata_fetched': True  # Mark as fetched to prevent endless retries
                }
                
                # Update game in database
                success = self.db_manager.update_game(game.id, update_data)
                if success:
                    updated_count += 1
            
            # Update UI
            self.games = self.db_manager.get_all_games()
            self.filtered_games = self.games.copy()
            self.display_games_in_grid()
            
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

    def remove_game(self, game):
        """Remove a game from the database and update the UI."""
        try:
            # Confirm removal
            reply = QMessageBox.question(
                self,
                "Confirm Removal",
                f"Are you sure you want to remove {game.name} from your library?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Remove from database
                if self.db_manager.remove_game(game.id):
                    # Update games list
                    self.games = self.db_manager.get_all_games()
                    self.filtered_games = self.games.copy()
                    
                    # Update UI
                    self.force_ui_refresh()
                    QMessageBox.information(self, "Success", f"{game.name} has been removed from your library.")
                else:
                    QMessageBox.critical(self, "Error", "Failed to remove game from database.")
        except Exception as e:
            print(f"Error removing game: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to remove game: {str(e)}")

    def update_overlay_metrics(self, metrics):
        """Update the overlay metrics in the UI"""
        try:
            if hasattr(self.ui, 'fpsValue'):
                self.ui.fpsValue.setText(f"{metrics['fps']:.0f}")
            if hasattr(self.ui, 'cpuValue'):
                self.ui.cpuValue.setText(f"{metrics['cpu']:.1f}%")
            if hasattr(self.ui, 'ramValue'):
                self.ui.ramValue.setText(f"{metrics['ram']:.1f}%")
            if hasattr(self.ui, 'gpuValue'):
                self.ui.gpuValue.setText(f"{metrics['gpu']:.1f}%")
        except Exception as e:
            print(f"Error updating overlay metrics: {e}")

    def closeEvent(self, event):
        """Cleanup when closing the application"""
        if hasattr(self, 'overlay_window'):
            self.overlay_window.close()
        event.accept()

    def handle_position_click(self, position):
        """Handle position button clicks"""
        # Uncheck all position buttons
        self.ui.topLeftBtn.setChecked(False)
        self.ui.topRightBtn.setChecked(False)
        self.ui.bottomLeftBtn.setChecked(False)
        self.ui.bottomRightBtn.setChecked(False)
        
        # Check the clicked button
        if position == "top_left":
            self.ui.topLeftBtn.setChecked(True)
        elif position == "top_right":
            self.ui.topRightBtn.setChecked(True)
        elif position == "bottom_left":
            self.ui.bottomLeftBtn.setChecked(True)
        elif position == "bottom_right":
            self.ui.bottomRightBtn.setChecked(True)
        
        # Update overlay position
        self.overlay_window.set_position(position)

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

    def display_games_in_grid(self):
        """Display games in a grid layout, reusing GameCard widgets."""
        try:
            print("[DEBUG] Starting display_games_in_grid (optimized)")
            self.grid_widget.setUpdatesEnabled(False)
            # Clear existing widgets from grid
            while self.grid_layout.count():
                item = self.grid_layout.takeAt(0)
                if item.widget():
                    item.widget().setParent(None)
            # Calculate number of columns based on window width
            available_width = self.scroll_area.viewport().width() - 60  # Subtract margins
            card_min_width = 200  # Minimum card width
            spacing = 20  # Spacing between cards
            self.max_cols = max(1, (available_width + spacing) // (card_min_width + spacing))
            print(f"[DEBUG] Grid width: {available_width}, Columns: {self.max_cols}")
            # Add only filtered games to grid, but reuse cards
            row = 0
            col = 0
            for game in self.filtered_games:
                card = self.create_game_card(game)
                card.setVisible(True)
                self.grid_layout.addWidget(card, row, col, 1, 1, Qt.AlignCenter)
                col += 1
                if col >= self.max_cols:
                    col = 0
                    row += 1
            # Hide cards not in filtered_games
            filtered_ids = set(g.id for g in self.filtered_games)
            for gid, card in self.card_widgets.items():
                if gid not in filtered_ids:
                    card.setVisible(False)
            # Set stretch factors for all columns
            for i in range(self.max_cols):
                self.grid_layout.setColumnStretch(i, 1)
            for i in range(row + 1):
                self.grid_layout.setRowStretch(i, 0)
            self.grid_layout.setRowStretch(row + 1, 1)
            self.grid_widget.setUpdatesEnabled(True)
            self.grid_widget.updateGeometry()
            self.grid_layout.update()
            self.scroll_area.viewport().update()
            print("[DEBUG] Finished display_games_in_grid (optimized)")
        except Exception as e:
            print(f"Error displaying games in grid: {e}")
            import traceback
            traceback.print_exc()

    def load_image(self, url):
        """Load an image from a URL or local path, with caching support."""
        try:
            print(f"[DEBUG] Attempting to load image from URL: {url}")
            
            # Check if image is in memory cache
            if url in self.image_cache:
                print(f"[DEBUG] Image loaded from memory cache: {url}")
                return self.image_cache[url]
            
            # Generate a unique filename for the image
            import hashlib
            url_hash = hashlib.md5(url.encode()).hexdigest()
            cache_path = os.path.join(self.image_cache_dir, f"{url_hash}.jpg")
            
            # Check if image exists in file cache
            if os.path.exists(cache_path):
                print(f"[DEBUG] Loading image from file cache: {cache_path}")
                img = QImage(cache_path)
                if not img.isNull():
                    print("[DEBUG] Successfully loaded image from file cache")
                    # Add to memory cache
                    self.image_cache[url] = img
                    return img
                else:
                    print("[DEBUG] Failed to load image from file cache - image is null")
            
            # Image not in cache, need to download it
            if url.startswith(('http://', 'https://')):
                print(f"[DEBUG] Downloading image from URL: {url}")
                response = requests.get(url, stream=True, timeout=5)
                if response.status_code == 200:
                    print("[DEBUG] Successfully downloaded image")
                    # Save to file cache
                    with open(cache_path, 'wb') as f:
                        f.write(response.content)
                    
                    # Load into memory and cache
                    img = QImage()
                    success = img.loadFromData(response.content)
                    if success and not img.isNull():
                        print("[DEBUG] Successfully loaded downloaded image")
                        self.image_cache[url] = img
                        return img
                    else:
                        print("[DEBUG] Failed to load downloaded image - image is null")
                else:
                    print(f"[DEBUG] Failed to download image - status code: {response.status_code}")
            else:
                # Try loading from local file
                print(f"[DEBUG] Attempting to load from local file: {url}")
                img = QImage(url)
                if not img.isNull():
                    print("[DEBUG] Successfully loaded image from local file")
                    self.image_cache[url] = img
                    return img
                else:
                    print("[DEBUG] Failed to load from local file - image is null")
                    
            print(f"[DEBUG] Failed to load image: {url}")
            return None
        except Exception as e:
            print(f"Error loading image: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def show_filter_dialog(self):
        """Show the filter dialog with current filters and available options."""
        try:
            # Update available filter options
            self.populate_filter_dropdowns()
            
            # Create and show dialog with current filters and available options
            dialog = FilterDialog(
                parent=self,
                current_filters=self.current_filters,
                available_genres=self.available_genres,
                available_platforms=self.available_platforms
            )
            
            # Connect the dialog's signal
            dialog.filtersApplied.connect(self.apply_filter_dialog_results)
            
            # Show dialog as modal
            dialog.exec_()
            
        except Exception as e:
            print(f"Error showing filter dialog: {e}")
            QMessageBox.critical(self, "Error", f"Failed to show filter dialog: {str(e)}")

    async def load_initial_games(self):
        """Load games from database ONLY - NEVER fetch metadata on normal startup."""
        try:
            print("[DEBUG] Starting load_initial_games")
            self.games = self.db_manager.get_all_games()
            self.filtered_games = self.games.copy()
            print(f"[DEBUG] load_initial_games: Retrieved {len(self.games)} games from database")
            self.force_ui_refresh()
            print("[DEBUG] load_initial_games complete")
        except Exception as e:
            print(f"Error loading initial games: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to load games: {str(e)}")
        finally:
            if hasattr(self, 'spinner_dialog'):
                self.spinner_dialog.stop()

    def show_game_details(self, game):
        dialog = GameDetailsDialog(game, self)
        dialog.exec_()

    def populate_filter_dropdowns(self):
        """Populate available_genres and available_platforms for the filter dialog based on current games."""
        genres = set()
        platforms = set()
        for game in self.games:
            if game.genre:
                for genre in str(game.genre).split(','):
                    genres.add(genre.strip())
            if game.type:
                platforms.add(game.type.strip().capitalize())
        self.available_genres = sorted(g for g in genres if g)
        self.available_platforms = sorted(p for p in platforms if p)

    def apply_filter_dialog_results(self, filters):
        """Apply the selected filters to the game list."""
        self.current_filters = filters
        filtered = self.games

        # Filter by genre
        if filters.get('genre') and filters['genre'] != 'All Genres':
            filtered = [g for g in filtered if g.genre and filters['genre'].lower() in g.genre.lower()]

        # Filter by platform
        if filters.get('platform') and filters['platform'] != 'All Platforms':
            filtered = [g for g in filtered if g.type and filters['platform'].lower() == g.type.lower()]

        # Filter by install status
        if filters.get('install_status') == 'Installed':
            filtered = [g for g in filtered if getattr(g, 'is_installed', False)]
        elif filters.get('install_status') == 'Not Installed':
            filtered = [g for g in filtered if not getattr(g, 'is_installed', False)]

        self.filtered_games = filtered
        self.display_games_in_grid()
        self.ui.gameCountLabel.setText(f"{len(self.filtered_games)} Games Found")

    def launch_game(self, game):
        """Launch the selected game."""
        try:
            if hasattr(game, 'type') and game.type == 'manual' and game.install_path:
                import subprocess
                subprocess.Popen(game.install_path, shell=True)
            elif hasattr(game, 'app_id') and game.app_id:
                from PySide6.QtCore import QUrl
                from PySide6.QtGui import QDesktopServices
                QDesktopServices.openUrl(QUrl(f"steam://rungameid/{game.app_id}"))
            else:
                QMessageBox.warning(self, "Error", "No launch command available for this game.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to launch game: {str(e)}")

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
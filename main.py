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
    QFrame, QProgressDialog, QDialog, QTextEdit, QStatusBar, QGraphicsDropShadowEffect
)
from PySide6.QtCore import QTimer, QUrl, Qt
from PySide6.QtGui import QAction, QIcon, QDesktopServices, QImage, QPixmap, QColor
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
                background-color: #1e1e1e;
            }
            QLabel {
                color: white;
            }
            QPushButton {
                background-color: #5865f2;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4752c4;
            }
            QPushButton:pressed {
                background-color: #3b45b5;
            }
            QLineEdit {
                background-color: #40444b;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                selection-background-color: #5865f2;
            }
            QLineEdit:focus {
                border: 1px solid #5865f2;
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
        self.overlay_window = OverlayWindow()
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
                    color: #dcddde;
                    border: none;
                    border-radius: 8px;
                    padding: 12px;
                    text-align: left;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #36393f;
                    color: white;
                }
                QPushButton:checked {
                    background-color: #5865f2;
                    color: white;
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
                    color: #FFFFFF;
                    font-size: 14px;
                    font-weight: 700;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                              stop:0 #033860, stop:1 #044a7a);
                    border-radius: 8px;
                    padding: 8px 16px;
                    border: 2px solid #055a9a;
                    min-height: 36px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                              stop:0 #044a7a, stop:1 #055a9a);
                    border: 2px solid #066aba;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                              stop:0 #055a9a, stop:1 #066aba);
                    border: 2px solid #077cba;
                }
            """)
            
        # Style manual add button separately with more rounded corners
        self.ui.manualAddBtn.setStyleSheet("""
            QPushButton {
                color: #FFFFFF;
                font-size: 14px;
                font-weight: 700;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #033860, stop:1 #044a7a);
                border-radius: 12px;
                padding: 8px 16px;
                border: 2px solid #055a9a;
                min-height: 36px;
                min-width: 36px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #044a7a, stop:1 #055a9a);
                border: 2px solid #066aba;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #055a9a, stop:1 #066aba);
                border: 2px solid #077cba;
            }
        """)
        
        # Make the sidebar background darker
        self.ui.leftMenu.setStyleSheet("""
            QWidget#leftMenu {
                background-color: #2f3136;
                border-right: 1px solid #202225;
            }
        """)
        
        # Style the search box and its clear button
        self.ui.lineEdit.setStyleSheet("""
            QLineEdit {
                color: #FFFFFF;
                font-size: 14px;
                font-weight: 700;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #033860, stop:1 #044a7a);
                border-radius: 8px;
                padding: 8px 16px;
                border: 2px solid #055a9a;
                min-height: 36px;
            }
            QLineEdit:focus {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #044a7a, stop:1 #055a9a);
                border: 2px solid #066aba;
            }
        """)
        
        self.ui.clearSearchBtn.setStyleSheet("""
            QPushButton {
                color: #FFFFFF;
                font-size: 14px;
                font-weight: 700;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #033860, stop:1 #044a7a);
                border-radius: 8px;
                padding: 8px 16px;
                border: 2px solid #055a9a;
                min-height: 36px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #044a7a, stop:1 #055a9a);
                border: 2px solid #066aba;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #055a9a, stop:1 #066aba);
                border: 2px solid #077cba;
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
                color: #FFFFFF;
                font-size: 14px;
                font-weight: 700;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #033860, stop:1 #044a7a);
                border-radius: 12px;
                padding: 8px 16px;
                border: 2px solid #055a9a;
                min-height: 36px;
            }
            QLabel:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #044a7a, stop:1 #055a9a);
                border: 2px solid #066aba;
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
                background-color: #1e1e1e; 
            }
            QScrollBar:vertical {
                border: none;
                background: #2d2d2d;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #4f545c;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #5865f2;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        self.ui.homeLayout.addWidget(self.scroll_area)
        
        self.grid_widget = QWidget()
        self.grid_widget.setStyleSheet("background-color: #1e1e1e;")
        self.scroll_area.setWidget(self.grid_widget)
        
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(20)
        self.grid_layout.setContentsMargins(30, 30, 30, 30)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

    def setup_status_bar(self):
        """Setup the status bar."""
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar { 
                color: #b9bbbe; 
                background-color: #2f3136;
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
        """Initialize game lists."""
        self.games = []
        self.session_games = []
        self.filtered_games = []

    def finish_loading(self):
        """Complete the loading process and show the main window."""
        self.splash.finish(self)
        self.show()
        
        # Start loading games after the window is shown
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
        try:
            # Create the card widget with fixed dimensions for consistent layout
            card = QWidget()
            card.setObjectName("game-card")
            card.setFixedWidth(300)
            card.setMinimumHeight(360)  # Increase height for better spacing
            card.setStyleSheet("""
                QWidget#game-card { 
                    background-color: #033860; 
                    border-radius: 15px; 
                    padding: 0px; 
                    margin: 8px;
                    border: 3px solid #044a7a;
                }
                QWidget#game-card:hover { 
                    background-color: #044a7a;
                    border: 3px solid #055a9a;
                }
                QLabel { 
                    color: white; 
                }
                QPushButton { 
                    background-color: #7C8483; 
                    color: white; 
                    border: none; 
                    padding: 8px 15px; 
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 13px;
                }
                QPushButton:hover { 
                    background-color: #8a9291; 
                }
                QPushButton:pressed {
                    background-color: #6e7675;
                }
            """)
            
            # Create main layout
            layout = QVBoxLayout()
            layout.setSpacing(10)
            layout.setContentsMargins(0, 0, 0, 15)
            
            # Create image container with rounded top corners
            image_container = QWidget()
            image_container.setFixedSize(300, 170)
            image_container.setStyleSheet("""
                background-color: #022d4a; 
                border-top-left-radius: 12px; 
                border-top-right-radius: 12px;
            """)
            image_layout = QVBoxLayout(image_container)
            image_layout.setContentsMargins(0, 0, 0, 0)
            
            # Add game poster/image
            if game.poster_url:
                try:
                    img = self.load_image(game.poster_url)
                    if img:
                        poster_label = QLabel()
                        poster_label.setFixedSize(300, 170)
                        poster_label.setScaledContents(True)
                        poster_label.setPixmap(QPixmap.fromImage(img))
                        poster_label.setStyleSheet("""
                            border-top-left-radius: 12px; 
                            border-top-right-radius: 12px;
                        """)
                        poster_label.setAlignment(Qt.AlignCenter)
                        image_layout.addWidget(poster_label)
                    else:
                        placeholder = QLabel(f"[No Image Available]")
                        placeholder.setFixedSize(300, 170)
                        placeholder.setStyleSheet("""
                            background-color: #022d4a; 
                            color: #7C8483; 
                            font-style: italic;
                            border-top-left-radius: 12px; 
                            border-top-right-radius: 12px;
                        """)
                        placeholder.setAlignment(Qt.AlignCenter)
                        image_layout.addWidget(placeholder)
                except Exception as e:
                    print(f"Error loading poster for {game.name}: {str(e)}")
                    placeholder = QLabel(f"[Image Error]")
                    placeholder.setFixedSize(300, 170)
                    placeholder.setStyleSheet("""
                        background-color: #022d4a; 
                        color: #7C8483; 
                        font-style: italic;
                        border-top-left-radius: 12px; 
                        border-top-right-radius: 12px;
                    """)
                    placeholder.setAlignment(Qt.AlignCenter)
                    image_layout.addWidget(placeholder)
            else:
                placeholder = QLabel(f"[No Image]")
                placeholder.setFixedSize(300, 170)
                placeholder.setStyleSheet("""
                    background-color: #022d4a; 
                    color: #7C8483; 
                    font-style: italic;
                    border-top-left-radius: 12px; 
                    border-top-right-radius: 12px;
                """)
                placeholder.setAlignment(Qt.AlignCenter)
                image_layout.addWidget(placeholder)
                
            layout.addWidget(image_container)
            
            # Create info container for text
            info_container = QWidget()
            info_container.setStyleSheet("""
                QWidget {
                    background: transparent;
                    border-left: 2px solid #044a7a;
                    margin-left: 15px;
                }
            """)
            info_layout = QVBoxLayout(info_container)
            info_layout.setContentsMargins(15, 0, 15, 0)
            info_layout.setSpacing(12)
            
            # Add game name with enhanced styling
            title_container = QWidget()
            title_container.setStyleSheet("""
                QWidget {
                    background: transparent;
                    border: none;
                }
            """)
            title_layout = QVBoxLayout(title_container)
            title_layout.setContentsMargins(0, 0, 0, 8)
            title_layout.setSpacing(0)
            
            title_label = QLabel(game.name)
            title_label.setStyleSheet("""
                font-weight: bold; 
                font-size: 18px; 
                color: #ffffff;
                padding-bottom: 4px;
            """)
            title_label.setWordWrap(True)
            title_label.setAlignment(Qt.AlignLeft)
            title_label.setFixedHeight(50)
            title_layout.addWidget(title_label)
            
            # Add separator line
            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setStyleSheet("""
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #044a7a, stop:1 transparent);
                border: none;
                height: 2px;
                margin: 0;
            """)
            title_layout.addWidget(separator)
            
            info_layout.addWidget(title_container)
            
            # Add info layout for platform and status
            details_layout = QVBoxLayout()
            details_layout.setSpacing(12)
            
            # Add game type/platform with icon
            if game.type:
                platform_layout = QHBoxLayout()
                platform_layout.setSpacing(10)
                
                platform_container = QWidget()
                platform_container.setStyleSheet("""
                    QWidget {
                        background: rgba(2, 45, 74, 0.5);
                        border-radius: 8px;
                        padding: 4px;
                    }
                """)
                platform_inner_layout = QHBoxLayout(platform_container)
                platform_inner_layout.setContentsMargins(8, 4, 12, 4)
                platform_inner_layout.setSpacing(8)
                
                platform_icon = QLabel("🖥️")
                platform_icon.setStyleSheet("color: #00b0f4; font-size: 14px;")
                platform_inner_layout.addWidget(platform_icon)
                
                type_label = QLabel(f"{game.type.capitalize()}")
                type_label.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: bold;")
                platform_inner_layout.addWidget(type_label)
                
                platform_layout.addWidget(platform_container)
                platform_layout.addStretch()
                details_layout.addLayout(platform_layout)
            
            # Add installation status with icon
            status_layout = QHBoxLayout()
            status_layout.setSpacing(10)
            
            status_container = QWidget()
            status_container.setStyleSheet("""
                QWidget {
                    background: rgba(2, 45, 74, 0.5);
                    border-radius: 8px;
                    padding: 4px;
                }
            """)
            status_inner_layout = QHBoxLayout(status_container)
            status_inner_layout.setContentsMargins(8, 4, 12, 4)
            status_inner_layout.setSpacing(8)
            
            status_icon = QLabel("💾" if game.is_installed else "❌")
            status_icon.setStyleSheet("color: #00b0f4; font-size: 14px;")
            status_inner_layout.addWidget(status_icon)
            
            status_text = "Installed" if game.is_installed else "Not Installed"
            status_label = QLabel(status_text)
            status_label.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: bold;")
            status_inner_layout.addWidget(status_label)
            
            status_layout.addWidget(status_container)
            status_layout.addStretch()
            details_layout.addLayout(status_layout)
            
            # Add genre if available
            if game.genre:
                genre_layout = QHBoxLayout()
                genre_layout.setSpacing(10)
                
                genre_container = QWidget()
                genre_container.setStyleSheet("""
                    QWidget {
                        background: rgba(2, 45, 74, 0.5);
                        border-radius: 8px;
                        padding: 4px;
                    }
                """)
                genre_inner_layout = QHBoxLayout(genre_container)
                genre_inner_layout.setContentsMargins(8, 4, 12, 4)
                genre_inner_layout.setSpacing(8)
                
                genre_icon = QLabel("🏷️")
                genre_icon.setStyleSheet("color: #00b0f4; font-size: 14px;")
                genre_inner_layout.addWidget(genre_icon)
                
                genre_label = QLabel(game.genre)
                genre_label.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: bold;")
                genre_label.setWordWrap(True)
                genre_inner_layout.addWidget(genre_label)
                
                genre_layout.addWidget(genre_container)
                genre_layout.addStretch()
                details_layout.addLayout(genre_layout)
            
            info_layout.addLayout(details_layout)
            layout.addWidget(info_container)
            
            # Add spacer to push buttons to bottom
            layout.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
            
            # Add buttons with updated styling
            button_layout = QHBoxLayout()
            button_layout.setContentsMargins(15, 0, 15, 0)
            button_layout.setSpacing(8)  # Reduced spacing between buttons
            
            # For manually added games, create two rows of buttons
            if game.type == 'manual':
                # Create a vertical layout for the buttons
                button_container = QVBoxLayout()
                button_container.setSpacing(8)  # Space between rows
                
                # Top row layout (Play and Details)
                top_row = QHBoxLayout()
                top_row.setSpacing(8)
                
                launch_button = QPushButton("PLAY")
                launch_button.setFixedHeight(36)
                launch_button.setMinimumWidth(100)  # Ensure minimum width for text
                launch_button.setStyleSheet("""
                    QPushButton {
                        background-color: #723D46;
                        color: white;
                        border: none;
                        padding: 8px 15px;
                        border-radius: 8px;
                        font-weight: bold;
                        font-size: 13px;
                    }
                    QPushButton:hover {
                        background-color: #8B4B55;
                    }
                    QPushButton:pressed {
                        background-color: #5E323A;
                    }
                """)
                launch_button.clicked.connect(lambda: self.launch_game(game))
                top_row.addWidget(launch_button)
                
                details_button = QPushButton("DETAILS")
                details_button.setFixedHeight(36)
                details_button.setMinimumWidth(100)  # Ensure minimum width for text
                details_button.setStyleSheet("""
                    QPushButton {
                        background-color: #022d4a;
                        color: white;
                        border: none;
                        padding: 8px 15px;
                        border-radius: 8px;
                        font-weight: bold;
                        font-size: 13px;
                    }
                    QPushButton:hover {
                        background-color: #033860;
                    }
                    QPushButton:pressed {
                        background-color: #022d4a;
                    }
                """)
                details_button.clicked.connect(lambda: self.show_game_details(game))
                top_row.addWidget(details_button)
                
                # Bottom row layout (Edit and Remove)
                bottom_row = QHBoxLayout()
                bottom_row.setSpacing(8)
                
                edit_button = QPushButton("EDIT")
                edit_button.setFixedHeight(36)
                edit_button.setMinimumWidth(100)  # Ensure minimum width for text
                edit_button.setStyleSheet("""
                    QPushButton {
                        background-color: #3182ce;
                        color: white;
                        border: none;
                        padding: 8px 15px;
                        border-radius: 8px;
                        font-weight: bold;
                        font-size: 13px;
                    }
                    QPushButton:hover {
                        background-color: #4299e1;
                    }
                    QPushButton:pressed {
                        background-color: #2b6cb0;
                    }
                """)
                edit_button.clicked.connect(lambda: self.edit_game(game))
                bottom_row.addWidget(edit_button)
                
                remove_button = QPushButton("REMOVE")
                remove_button.setFixedHeight(36)
                remove_button.setMinimumWidth(100)  # Ensure minimum width for text
                remove_button.setStyleSheet("""
                    QPushButton {
                        background-color: #dc2626;
                        color: white;
                        border: none;
                        padding: 8px 15px;
                        border-radius: 8px;
                        font-weight: bold;
                        font-size: 13px;
                    }
                    QPushButton:hover {
                        background-color: #ef4444;
                    }
                    QPushButton:pressed {
                        background-color: #b91c1c;
                    }
                """)
                remove_button.clicked.connect(lambda: self.remove_game(game))
                bottom_row.addWidget(remove_button)
                
                # Add rows to the button container
                button_container.addLayout(top_row)
                button_container.addLayout(bottom_row)
                
                # Add the button container to the main layout
                layout.addLayout(button_container)
            else:
                # Regular two-button layout for non-manual games
                launch_button = QPushButton("PLAY")
                launch_button.setFixedHeight(36)
                launch_button.setStyleSheet("""
                    QPushButton {
                        background-color: #723D46;
                        color: white;
                        border: none;
                        padding: 8px 15px;
                        border-radius: 8px;
                        font-weight: bold;
                        font-size: 13px;
                    }
                    QPushButton:hover {
                        background-color: #8B4B55;
                    }
                    QPushButton:pressed {
                        background-color: #5E323A;
                    }
                """)
                launch_button.clicked.connect(lambda: self.launch_game(game))
                button_layout.addWidget(launch_button)
                
                details_button = QPushButton("DETAILS")
                details_button.setFixedHeight(36)
                details_button.setStyleSheet("""
                    QPushButton {
                        background-color: #022d4a;
                        color: white;
                        border: none;
                        padding: 8px 15px;
                        border-radius: 8px;
                        font-weight: bold;
                        font-size: 13px;
                    }
                    QPushButton:hover {
                        background-color: #033860;
                    }
                    QPushButton:pressed {
                        background-color: #022d4a;
                    }
                """)
                details_button.clicked.connect(lambda: self.show_game_details(game))
                button_layout.addWidget(details_button)
                
                layout.addLayout(button_layout)
            
            card.setLayout(layout)
            
            # Set up hover effects with graphical effects
            shadow = QGraphicsDropShadowEffect()
            shadow.setColor(QColor(0, 0, 0, 150))
            shadow.setBlurRadius(20)
            shadow.setOffset(0, 5)
            card.setGraphicsEffect(shadow)
            
            # Store shadow as an attribute of the card for reference in event handlers
            card.shadow = shadow
            
            # Connect mouse events to change shadow on hover
            def enter_event(e):
                card.shadow.setColor(QColor(0, 0, 0, 200))
                card.shadow.setBlurRadius(25)
                card.shadow.setOffset(0, 8)
                # Move card up slightly on hover for "pop out" effect
                card.setContentsMargins(0, -5, 0, 5)
                
            def leave_event(e):
                card.shadow.setColor(QColor(0, 0, 0, 150))
                card.shadow.setBlurRadius(20)
                card.shadow.setOffset(0, 5)
                # Reset to normal position
                card.setContentsMargins(0, 0, 0, 0)
                
            card.enterEvent = enter_event
            card.leaveEvent = leave_event
            
            return card
            
        except Exception as e:
            print(f"Error creating game card: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
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

    def display_games_in_grid(self):
        """Display games in a grid layout."""
        try:
            print("[DEBUG] Starting display_games_in_grid")
            
            # Clear existing widgets from grid
            while self.grid_layout.count():
                item = self.grid_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            # Calculate number of columns based on window width
            grid_width = self.scroll_area.viewport().width()
            card_width = 220  # Card width + spacing
            columns = max(1, grid_width // card_width)
            
            print(f"[DEBUG] Grid width: {grid_width}, Columns: {columns}")
            
            # Add games to grid
            row = 0
            col = 0
            for game in self.filtered_games:
                try:
                    card = self.create_game_card(game)
                    if card:
                        self.grid_layout.addWidget(card, row, col)
                        col += 1
                        if col >= columns:
                            col = 0
                            row += 1
                except Exception as e:
                    print(f"Error creating card for game {game.name}: {e}")
                    continue

            # Add spacer at the end
            spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
            self.grid_layout.addItem(spacer, row + 1, 0, 1, columns)
            
            # Force layout update
            self.grid_widget.updateGeometry()
            self.grid_layout.update()
            self.scroll_area.viewport().update()
            
            print("[DEBUG] Finished display_games_in_grid")
            
        except Exception as e:
            print(f"Error displaying games in grid: {e}")
            import traceback
            traceback.print_exc()

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
            print("[DEBUG] Starting load_initial_games")
            # Get all games from database
            self.games = self.db_manager.get_all_games()
            self.filtered_games = self.games.copy()
            print(f"[DEBUG] load_initial_games: Retrieved {len(self.games)} games from database")
            
            # Update display with games from database - NO API calls
            self.force_ui_refresh()
            print("[DEBUG] load_initial_games complete")
            
        except Exception as e:
            print(f"Error loading initial games: {e}")
            import traceback
            traceback.print_exc()
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
        """Show detailed game information in a dialog."""
        try:
            print(f"[DEBUG] Showing details for game: {game.name}")
            print(f"[DEBUG] Game object: {game}")
            print(f"[DEBUG] Game attributes: type={game.type}, app_id={game.app_id}, genre={game.genre}")
            
            # Verify GameDetailsDialog is imported
            print("[DEBUG] Creating GameDetailsDialog instance")
            try:
                dialog = GameDetailsDialog(game, self)
                print("[DEBUG] GameDetailsDialog instance created successfully")
            except Exception as dialog_error:
                print(f"[DEBUG] Error creating dialog: {str(dialog_error)}")
                import traceback
                traceback.print_exc()
                raise
            
            # Show the dialog
            print("[DEBUG] Executing dialog")
            dialog.exec_()
            print("[DEBUG] Dialog closed")
            
        except Exception as e:
            print(f"Error showing game details: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to show game details: {str(e)}")

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
            
            # Start monitoring the game process
            if hasattr(self, 'overlay_window'):
                # Get the process name from the launch command
                process_name = os.path.basename(game.launch_command)
                self.overlay_window.backend.start_monitoring(process_name)
                self.overlay_window.show_overlay()
            
        except Exception as e:
            print(f"Error launching game: {e}")
            QMessageBox.critical(self, "Error", f"Failed to launch game: {str(e)}")

    def populate_filter_dropdowns(self):
        """Get available filter options for the filter dialog"""
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
            self.available_genres = sorted(list(genres))
            self.available_platforms = sorted(list(platforms))
            
        except Exception as e:
            print(f"Error collecting filter options: {e}")

    def filter_games(self):
        """Filter games based on current filter settings"""
        try:
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
            
        except Exception as e:
            print(f"Error applying filters: {e}")
            QMessageBox.critical(self, "Error", f"Failed to apply filters: {str(e)}")

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

    def apply_filter_dialog_results(self, filters):
        """Apply filters from the filter dialog."""
        try:
            # Update current filters
            self.current_filters = filters
            
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
            
            # Initialize available filter options
            self.available_genres = []
            self.available_platforms = []
            
        except Exception as e:
            print(f"Error setting up connections: {e}")

    def resizeEvent(self, event):
        """Handle window resize events."""
        super().resizeEvent(event)
        # Only recalculate layout if we have existing games
        if hasattr(self, 'filtered_games') and self.filtered_games:
            try:
                print("[DEBUG] Resize event triggered, rebuilding game grid")
                # Calculate the number of columns based on window width
                available_width = self.width()
                card_width = 340  # Card width + margins + spacing
                max_cols = max(1, int((available_width - 60) / card_width))
                print(f"[DEBUG] Resize: calculated {max_cols} columns based on width {available_width}px")
                
                # Create new layout
                new_layout = QGridLayout()
                new_layout.setSpacing(20)
                new_layout.setContentsMargins(30, 30, 30, 30)
                new_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
                
                # Add game cards to new layout
                row = 0
                col = 0
                cards_added = 0
                print(f"[DEBUG] Resize: Adding {len(self.filtered_games)} game cards to new layout")
                
                for game in self.filtered_games:
                    card = self.create_game_card(game)
                    if card:
                        new_layout.addWidget(card, row, col)
                        cards_added += 1
                        col += 1
                        if col >= max_cols:
                            col = 0
                            row += 1
                
                print(f"[DEBUG] Resize: Added {cards_added} game cards to new layout")
                
                # Create new widget for the layout
                new_widget = QWidget()
                new_widget.setLayout(new_layout)
                new_widget.setStyleSheet("background-color: #1e1e1e;")
                
                # Replace old layout with new one
                print("[DEBUG] Resize: Replacing old layout with new layout")
                if self.grid_widget:
                    self.grid_widget.deleteLater()
                self.grid_widget = new_widget
                self.grid_layout = new_layout
                self.scroll_area.setWidget(self.grid_widget)
                print("[DEBUG] Resize: Layout replacement complete")
                
                # Force layout update
                self.grid_widget.updateGeometry()
                self.grid_layout.update()
                QApplication.processEvents()
                
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
        if not hasattr(self, 'overlay_window'):
            self.overlay_window = OverlayWindow(self)
            
        if self.overlay_window.isVisible():
            self.overlay_window.hide_overlay()
        else:
            self.overlay_window.show_overlay()

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
            dialog = ManualAddGameDialog(self, game)
            if dialog.exec_() == QDialog.Accepted:
                game_data = dialog.get_game_data()
                
                if not game_data.name or not game_data.install_path:
                    QMessageBox.warning(self, "Error", "Game name and executable path are required.")
                    return
                
                if game:  # Editing existing game
                    # Convert game object to dictionary for update
                    update_data = {
                        'name': game_data.name,
                        'install_path': game_data.install_path,
                        'launch_command': game_data.launch_command,
                        'genre': game_data.genre,
                        'release_date': game_data.release_date,
                        'description': game_data.description,
                        'developers': game_data.developers,
                        'publishers': game_data.publishers,
                        'poster_url': game_data.poster_url,  # Add poster URL to update data
                        'background_url': game_data.background_url,  # Add background URL to update data
                        'metadata_fetched': True  # Mark as metadata fetched if we have poster/metadata
                    }
                    
                    print(f"[DEBUG] Updating game with data: {update_data}")
                    
                    # Update game in database
                    if self.db_manager.update_game(game.id, update_data):
                        print(f"[DEBUG] Successfully updated game in database")
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
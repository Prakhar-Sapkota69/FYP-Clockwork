from PySide6.QtWidgets import (
    QMainWindow, QProgressDialog, QWidget, QVBoxLayout, 
    QHBoxLayout, QGridLayout, QScrollArea, QSizePolicy,
    QMessageBox
)
from PySide6.QtCore import Qt
from game_card import GameCard
from models import Game

class UIManager:
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

    def __init__(self, main_window):
        self.main_window = main_window
        self.games_layout = None
        self.games_container = None

    def setup_library_ui(self):
        """Set up the library UI components."""
        # Create the main library widget
        self.main_window.library_widget = QWidget()
        self.main_window.library_widget.setObjectName("libraryWidget")
        self.main_window.library_widget.setStyleSheet("#libraryWidget { background: transparent; }")
        
        # Create the main library layout
        library_layout = QVBoxLayout(self.main_window.library_widget)
        library_layout.setSpacing(0)
        library_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create the games container widget
        self.games_container = QWidget()
        self.games_container.setObjectName("gamesContainer")
        self.games_container.setStyleSheet("#gamesContainer { background: transparent; }")
        
        # Create a horizontal layout to center the grid
        center_layout = QHBoxLayout()
        center_layout.setSpacing(0)
        center_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create the games grid layout
        self.games_layout = QGridLayout()
        self.games_layout.setSpacing(20)
        self.games_layout.setContentsMargins(20, 20, 20, 20)
        self.games_layout.setAlignment(Qt.AlignCenter)  # Center the grid contents
        
        # Add the grid layout to a container widget
        grid_container = QWidget()
        grid_container.setLayout(self.games_layout)
        
        # Add the grid container to the center layout with stretches
        center_layout.addStretch(1)
        center_layout.addWidget(grid_container)
        center_layout.addStretch(1)
        
        # Set the center layout as the games container layout
        self.games_container.setLayout(center_layout)
        
        # Create scroll area
        self.main_window.scroll_area = QScrollArea()
        self.main_window.scroll_area.setWidget(self.games_container)
        self.main_window.scroll_area.setWidgetResizable(True)
        self.main_window.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Disable horizontal scrolling
        self.main_window.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #2C5A68;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #3B82F6;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        # Add scroll area to library layout
        library_layout.addWidget(self.main_window.scroll_area)
        
        # Add the library widget to the first page of the stacked widget
        if hasattr(self.main_window.ui, 'stackedWidget'):
            first_page = self.main_window.ui.stackedWidget.widget(0)
            if isinstance(first_page, QWidget):
                if first_page.layout() is None:
                    QVBoxLayout(first_page)
                first_page.layout().addWidget(self.main_window.library_widget)

    def create_progress_dialog(self, title, message, maximum):
        """Create a styled progress dialog"""
        dialog = QProgressDialog(message, "Cancel", 0, maximum, self.main_window)
        dialog.setWindowTitle(title)
        dialog.setWindowModality(Qt.WindowModal)
        dialog.setMinimumWidth(300)
        dialog.setStyleSheet(self.main_window.PROGRESS_DIALOG_STYLE)
        return dialog

    def display_games_in_grid(self, games=None):
        """Display games in the grid layout."""
        try:
            # If no games provided, use filtered games
            if games is None:
                games = self.main_window.filtered_games
            
            # Clear existing items
            for i in reversed(range(self.games_layout.count())): 
                self.games_layout.itemAt(i).widget().setParent(None)
            
            # Calculate grid dimensions
            available_width = self.games_container.width()
            card_width = 220  # Card width + spacing
            max_cols = max(1, available_width // card_width)
            
            # Create game cards and add them to the grid
            row = 0
            col = 0
            
            for game in games:
                # Create game card
                card = self.main_window.create_game_card(game)
                if card:
                    self.games_layout.addWidget(card, row, col)
                    
                    # Update grid position
                    col += 1
                    if col >= max_cols:
                        col = 0
                        row += 1
                    
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"Failed to display games: {str(e)}")

    def update_library_display(self):
        """Update the library display with current games"""
        try:
            # Get the latest games from the database
            self.main_window.games = self.main_window.db_manager.get_all_games()
            self.main_window.filtered_games = self.main_window.games.copy()
            
            # Display games in grid
            self.display_games_in_grid()
            
            # Update game count
            self.main_window.ui.gameCountLabel.setText(f"{len(self.main_window.games)} Games in Library")
            
            # Populate filter dropdowns
            self.main_window.populate_filter_dropdowns()
            
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"Failed to update library display: {str(e)}") 
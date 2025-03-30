from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QWidget, QScrollArea, QFrame, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon

class FilterDialog(QDialog):
    # Signal to notify when filters are applied
    filtersApplied = Signal(dict)
    
    def __init__(self, parent=None, current_filters=None):
        super().__init__(parent)
        self.setWindowTitle("Filter Games")
        self.setMinimumSize(350, 300)
        self.setMaximumSize(400, 400)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # Store current filters
        self.current_filters = current_filters or {
            'genre': 'All Genres',
            'platform': 'All Platforms',
            'install_status': 'All Games'
        }
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title_label = QLabel("Filter Games")
        title_label.setStyleSheet("""
            QLabel {
                color: #E2E8F0;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Filter container
        filter_container = QWidget()
        filter_layout = QVBoxLayout(filter_container)
        filter_layout.setSpacing(12)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        
        # Genre filter
        genre_label = QLabel("Genre:")
        genre_label.setStyleSheet("font-weight: bold; color: #E2E8F0;")
        
        self.genre_combo = QComboBox()
        self.genre_combo.setObjectName("genreCombo")
        self.genre_combo.setFixedHeight(30)
        
        # Get genres from parent's genreFilter if available
        parent = self.parent()
        if parent and hasattr(parent, 'ui') and hasattr(parent.ui, 'genreFilter'):
            for i in range(parent.ui.genreFilter.count()):
                self.genre_combo.addItem(parent.ui.genreFilter.itemText(i))
        else:
            # Default genres
            self.genre_combo.addItems(["All Genres", "Action", "Adventure", "RPG", "Strategy", "Sports", "Racing", "Simulation"])
        
        # Set current selection
        index = self.genre_combo.findText(self.current_filters['genre'])
        if index >= 0:
            self.genre_combo.setCurrentIndex(index)
            
        genre_layout = QHBoxLayout()
        genre_layout.addWidget(genre_label)
        genre_layout.addWidget(self.genre_combo)
        filter_layout.addLayout(genre_layout)
        
        # Platform filter
        platform_label = QLabel("Platform:")
        platform_label.setStyleSheet("font-weight: bold; color: #E2E8F0;")
        
        self.platform_combo = QComboBox()
        self.platform_combo.setObjectName("platformCombo")
        self.platform_combo.setFixedHeight(30)
        
        # Get platforms from parent's platformFilter if available
        if parent and hasattr(parent, 'ui') and hasattr(parent.ui, 'platformFilter'):
            for i in range(parent.ui.platformFilter.count()):
                self.platform_combo.addItem(parent.ui.platformFilter.itemText(i))
        else:
            # Default platforms
            self.platform_combo.addItems(["All Platforms", "Steam", "Epic", "GOG", "Other"])
        
        # Set current selection
        index = self.platform_combo.findText(self.current_filters['platform'])
        if index >= 0:
            self.platform_combo.setCurrentIndex(index)
            
        platform_layout = QHBoxLayout()
        platform_layout.addWidget(platform_label)
        platform_layout.addWidget(self.platform_combo)
        filter_layout.addLayout(platform_layout)
        
        # Installation status filter
        install_label = QLabel("Status:")
        install_label.setStyleSheet("font-weight: bold; color: #E2E8F0;")
        
        self.install_combo = QComboBox()
        self.install_combo.setObjectName("installCombo")
        self.install_combo.setFixedHeight(30)
        
        # Get installation statuses from parent's installFilter if available
        if parent and hasattr(parent, 'ui') and hasattr(parent.ui, 'installFilter'):
            for i in range(parent.ui.installFilter.count()):
                self.install_combo.addItem(parent.ui.installFilter.itemText(i))
        else:
            # Default installation statuses
            self.install_combo.addItems(["All Games", "Installed", "Not Installed"])
        
        # Set current selection
        index = self.install_combo.findText(self.current_filters['install_status'])
        if index >= 0:
            self.install_combo.setCurrentIndex(index)
            
        install_layout = QHBoxLayout()
        install_layout.addWidget(install_label)
        install_layout.addWidget(self.install_combo)
        filter_layout.addLayout(install_layout)
        
        main_layout.addWidget(filter_container)
        
        # Add spacer
        main_layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Close button
        close_button = QPushButton("Close")
        close_button.setFixedHeight(30)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #4B5563;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6B7280;
            }
            QPushButton:pressed {
                background-color: #374151;
            }
        """)
        close_button.clicked.connect(self.reject)
        button_layout.addWidget(close_button)
        
        # Reset button
        reset_button = QPushButton("Reset")
        reset_button.setFixedHeight(30)
        reset_button.setStyleSheet("""
            QPushButton {
                background-color: #4B5563;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6B7280;
            }
            QPushButton:pressed {
                background-color: #374151;
            }
        """)
        reset_button.clicked.connect(self.reset_filters)
        button_layout.addWidget(reset_button)
        
        # Apply button
        apply_button = QPushButton("Apply")
        apply_button.setFixedHeight(30)
        apply_button.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton:pressed {
                background-color: #1D4ED8;
            }
        """)
        apply_button.clicked.connect(self.apply_filters)
        button_layout.addWidget(apply_button)
        
        main_layout.addLayout(button_layout)
        
        # Set dialog style
        self.setStyleSheet("""
            QDialog {
                background-color: #204B57;
                color: #E2E8F0;
                border-radius: 8px;
            }
            QLabel {
                color: #E2E8F0;
            }
            QComboBox {
                background-color: #2C5A68;
                border: 1px solid #3B82F6;
                border-radius: 6px;
                padding: 4px 8px;
                color: #E2E8F0;
                font-size: 13px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(icons/down-arrow.png);
                width: 12px;
                height: 12px;
            }
        """)
    
    def reset_filters(self):
        # Reset all filters to default
        self.genre_combo.setCurrentText("All Genres")
        self.platform_combo.setCurrentText("All Platforms")
        self.install_combo.setCurrentText("All Games")
    
    def apply_filters(self):
        # Collect filter values
        filters = {
            'genre': self.genre_combo.currentText(),
            'platform': self.platform_combo.currentText(),
            'install_status': self.install_combo.currentText()
        }
        
        # Emit signal with new filters
        self.filtersApplied.emit(filters)
        
        # Close dialog
        self.accept()
        
    # Override closeEvent to ensure dialog closes properly
    def closeEvent(self, event):
        self.reject()
        event.accept()

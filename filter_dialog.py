from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QWidget, QCheckBox, QScrollArea, QFrame, QStyleOptionButton
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor, QPalette, QFont, QPainter, QPen, QBrush

class CustomCheckBox(QCheckBox):
    """Custom checkbox with a more modern look"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QCheckBox {
                color: #f2f3f5;
                font-size: 13px;
                padding: 10px;
                border-radius: 6px;
                margin: 2px 0px;
            }
            QCheckBox:hover {
                background-color: #1a1c1e;
            }
            QCheckBox:checked {
                color: white;
                background-color: #2a2c2e;
            }
        """)
    
    def paintEvent(self, event):
        """Custom paint event to draw a modern checkbox indicator"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get the checkbox rect
        option = QStyleOptionButton()
        self.initStyleOption(option)
        rect = self.rect()
        
        # Draw the checkbox background if checked or hovered
        if self.isChecked() or self.underMouse():
            if self.isChecked():
                painter.setBrush(QBrush(QColor("#2a2c2e")))
            else:
                painter.setBrush(QBrush(QColor("#1a1c1e")))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(rect, 6, 6)
        
        # Draw the checkbox indicator
        indicator_size = 20
        indicator_x = 10
        indicator_y = (rect.height() - indicator_size) // 2
        
        # Draw the checkbox border
        if self.isChecked():
            painter.setBrush(QBrush(QColor("#033860")))
            painter.setPen(QPen(QColor("#033860"), 2))
        else:
            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(QColor("#7C8483"), 2))
        
        painter.drawRoundedRect(indicator_x, indicator_y, indicator_size, indicator_size, 6, 6)
        
        # Draw the checkmark if checked
        if self.isChecked():
            painter.setPen(QPen(QColor("white"), 2))
            # Draw a checkmark
            check_x = indicator_x + 5
            check_y = indicator_y + indicator_size // 2
            painter.drawLine(check_x, check_y, check_x + 5, check_y + 5)
            painter.drawLine(check_x + 5, check_y + 5, check_x + 15, check_y - 5)
        
        # Draw the text
        text_rect = rect.adjusted(indicator_x + indicator_size + 10, 0, 0, 0)
        painter.setPen(QPen(self.palette().text().color()))
        painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, self.text())

class FilterDialog(QDialog):
    filtersApplied = Signal(dict)  # Signal emitted when filters are applied
    
    def __init__(self, parent=None, current_filters=None, available_genres=None, available_platforms=None):
        super().__init__(parent)
        self.setWindowTitle("Filter Games")
        self.setMinimumWidth(450)
        self.setMinimumHeight(500)
        
        # Set window background color
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#121416"))
        self.setPalette(palette)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #121416;
                color: white;
                border-radius: 12px;
                border: 1px solid #1a1c1e;
            }
            QLabel {
                color: #f2f3f5;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton {
                background-color: #033860;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #044a7a;
            }
            QPushButton:pressed {
                background-color: #022d4a;
            }
            QPushButton#resetButton {
                background-color: #7C8483;
            }
            QPushButton#resetButton:hover {
                background-color: #8a9291;
            }
            QPushButton#resetButton:pressed {
                background-color: #6e7675;
            }
            QWidget#filterSection {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                          stop:0 #1a1c1e, stop:1 #121416);
                border-radius: 10px;
                padding: 15px;
                border: 1px solid #1a1c1e;
            }
            QWidget#filterSection:hover {
                border: 1px solid #7C8483;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #1a1c1e;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #7C8483;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #033860;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        # Store current filters
        self.current_filters = current_filters or {
            'genre': 'All Genres',
            'platform': 'All Platforms',
            'install_status': 'All Games'
        }
        
        # Store available options
        self.available_genres = available_genres or []
        self.available_platforms = available_platforms or []
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Add title
        title_label = QLabel("FILTER YOUR GAMES")
        title_label.setStyleSheet("""
            font-size: 22px; 
            font-weight: bold; 
            color: white; 
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 2px solid #033860;
            letter-spacing: 1px;
        """)
        layout.addWidget(title_label)
        
        # Create scroll area for filters
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Create container for filters
        filter_container = QWidget()
        filter_layout = QVBoxLayout(filter_container)
        filter_layout.setSpacing(15)
        
        # Genre filter
        genre_section = QWidget()
        genre_section.setObjectName("filterSection")
        genre_layout = QVBoxLayout(genre_section)
        genre_layout.setSpacing(8)
        
        genre_label = QLabel("GENRE")
        genre_label.setStyleSheet("""
            color: #033860; 
            font-size: 13px; 
            font-weight: bold;
            padding-bottom: 5px;
            border-bottom: 1px solid #7C8483;
        """)
        genre_layout.addWidget(genre_label)
        
        # Add "All Genres" checkbox
        self.genre_all = CustomCheckBox("All Genres")
        self.genre_all.setChecked(self.current_filters['genre'] == 'All Genres')
        self.genre_all.stateChanged.connect(lambda state: self.handle_genre_all(state))
        genre_layout.addWidget(self.genre_all)
        
        # Add genre checkboxes
        self.genre_checkboxes = {}
        for genre in self.available_genres:
            checkbox = CustomCheckBox(genre)
            checkbox.setChecked(self.current_filters['genre'] == genre)
            checkbox.stateChanged.connect(lambda state, g=genre: self.handle_genre_check(state, g))
            self.genre_checkboxes[genre] = checkbox
            genre_layout.addWidget(checkbox)
        
        filter_layout.addWidget(genre_section)
        
        # Platform filter
        platform_section = QWidget()
        platform_section.setObjectName("filterSection")
        platform_layout = QVBoxLayout(platform_section)
        platform_layout.setSpacing(8)
        
        platform_label = QLabel("PLATFORM")
        platform_label.setStyleSheet("""
            color: #033860; 
            font-size: 13px; 
            font-weight: bold;
            padding-bottom: 5px;
            border-bottom: 1px solid #7C8483;
        """)
        platform_layout.addWidget(platform_label)
        
        # Add "All Platforms" checkbox
        self.platform_all = CustomCheckBox("All Platforms")
        self.platform_all.setChecked(self.current_filters['platform'] == 'All Platforms')
        self.platform_all.stateChanged.connect(lambda state: self.handle_platform_all(state))
        platform_layout.addWidget(self.platform_all)
        
        # Add platform checkboxes
        self.platform_checkboxes = {}
        # Add common platforms first
        common_platforms = ['steam']
        for platform in common_platforms:
            if platform in self.available_platforms:
                checkbox = CustomCheckBox(platform.capitalize())
                checkbox.setChecked(self.current_filters['platform'] == platform.capitalize())
                checkbox.stateChanged.connect(lambda state, p=platform: self.handle_platform_check(state, p))
                self.platform_checkboxes[platform] = checkbox
                platform_layout.addWidget(checkbox)
        
        # Add remaining platforms
        for platform in self.available_platforms:
            if platform.lower() not in common_platforms:
                checkbox = CustomCheckBox(platform.capitalize())
                checkbox.setChecked(self.current_filters['platform'] == platform.capitalize())
                checkbox.stateChanged.connect(lambda state, p=platform: self.handle_platform_check(state, p))
                self.platform_checkboxes[platform] = checkbox
                platform_layout.addWidget(checkbox)
        
        filter_layout.addWidget(platform_section)
        
        # Installation status filter
        install_section = QWidget()
        install_section.setObjectName("filterSection")
        install_layout = QVBoxLayout(install_section)
        install_layout.setSpacing(8)
        
        install_label = QLabel("INSTALLATION STATUS")
        install_label.setStyleSheet("""
            color: #033860; 
            font-size: 13px; 
            font-weight: bold;
            padding-bottom: 5px;
            border-bottom: 1px solid #7C8483;
        """)
        install_layout.addWidget(install_label)
        
        # Add installation status checkboxes
        self.install_all = CustomCheckBox("All Games")
        self.install_all.setChecked(self.current_filters['install_status'] == 'All Games')
        self.install_all.stateChanged.connect(lambda state: self.handle_install_all(state))
        install_layout.addWidget(self.install_all)
        
        self.install_installed = CustomCheckBox("Installed")
        self.install_installed.setChecked(self.current_filters['install_status'] == 'Installed')
        self.install_installed.stateChanged.connect(lambda state: self.handle_install_check(state, 'Installed'))
        install_layout.addWidget(self.install_installed)
        
        self.install_not_installed = CustomCheckBox("Not Installed")
        self.install_not_installed.setChecked(self.current_filters['install_status'] == 'Not Installed')
        self.install_not_installed.stateChanged.connect(lambda state: self.handle_install_check(state, 'Not Installed'))
        install_layout.addWidget(self.install_not_installed)
        
        filter_layout.addWidget(install_section)
        
        # Add spacer at the end
        filter_layout.addStretch()
        
        # Set the scroll area widget
        scroll_area.setWidget(filter_container)
        layout.addWidget(scroll_area)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        reset_button = QPushButton("RESET")
        reset_button.setObjectName("resetButton")
        reset_button.clicked.connect(self.reset_filters)
        
        apply_button = QPushButton("APPLY FILTERS")
        apply_button.clicked.connect(self.apply_filters)
        
        button_layout.addWidget(reset_button)
        button_layout.addWidget(apply_button)
        layout.addLayout(button_layout)
    
    def handle_genre_all(self, state):
        """Handle the 'All Genres' checkbox state change."""
        if state == Qt.Checked:
            # Uncheck all other genre checkboxes
            for checkbox in self.genre_checkboxes.values():
                checkbox.setChecked(False)
                checkbox.setEnabled(False)
        else:
            # Enable all genre checkboxes
            for checkbox in self.genre_checkboxes.values():
                checkbox.setEnabled(True)
    
    def handle_genre_check(self, state, genre):
        """Handle a genre checkbox state change."""
        if state == Qt.Checked:
            # Uncheck 'All Genres'
            self.genre_all.setChecked(False)
            # Uncheck other genre checkboxes
            for g, checkbox in self.genre_checkboxes.items():
                if g != genre:
                    checkbox.setChecked(False)
    
    def handle_platform_all(self, state):
        """Handle the 'All Platforms' checkbox state change."""
        if state == Qt.Checked:
            # Uncheck all other platform checkboxes
            for checkbox in self.platform_checkboxes.values():
                checkbox.setChecked(False)
                checkbox.setEnabled(False)
        else:
            # Enable all platform checkboxes
            for checkbox in self.platform_checkboxes.values():
                checkbox.setEnabled(True)
    
    def handle_platform_check(self, state, platform):
        """Handle a platform checkbox state change."""
        if state == Qt.Checked:
            # Uncheck 'All Platforms'
            self.platform_all.setChecked(False)
            # Uncheck other platform checkboxes
            for p, checkbox in self.platform_checkboxes.items():
                if p != platform:
                    checkbox.setChecked(False)
    
    def handle_install_all(self, state):
        """Handle the 'All Games' checkbox state change."""
        if state == Qt.Checked:
            # Uncheck other installation status checkboxes
            self.install_installed.setChecked(False)
            self.install_not_installed.setChecked(False)
            self.install_installed.setEnabled(False)
            self.install_not_installed.setEnabled(False)
        else:
            # Enable other installation status checkboxes
            self.install_installed.setEnabled(True)
            self.install_not_installed.setEnabled(True)
    
    def handle_install_check(self, state, status):
        """Handle an installation status checkbox state change."""
        if state == Qt.Checked:
            # Uncheck 'All Games'
            self.install_all.setChecked(False)
            # Uncheck other installation status checkboxes
            if status == 'Installed':
                self.install_not_installed.setChecked(False)
            else:
                self.install_installed.setChecked(False)
    
    def reset_filters(self):
        """Reset all filters to their default values."""
        # Reset genre filters
        self.genre_all.setChecked(True)
        for checkbox in self.genre_checkboxes.values():
            checkbox.setChecked(False)
            checkbox.setEnabled(False)
        
        # Reset platform filters
        self.platform_all.setChecked(True)
        for checkbox in self.platform_checkboxes.values():
            checkbox.setChecked(False)
            checkbox.setEnabled(False)
        
        # Reset installation status filters
        self.install_all.setChecked(True)
        self.install_installed.setChecked(False)
        self.install_not_installed.setChecked(False)
        self.install_installed.setEnabled(False)
        self.install_not_installed.setEnabled(False)
    
    def apply_filters(self):
        """Collect and emit the current filter values."""
        # Get selected genre
        genre = 'All Genres'
        if not self.genre_all.isChecked():
            for g, checkbox in self.genre_checkboxes.items():
                if checkbox.isChecked():
                    genre = g
                    break
        
        # Get selected platform
        platform = 'All Platforms'
        if not self.platform_all.isChecked():
            for p, checkbox in self.platform_checkboxes.items():
                if checkbox.isChecked():
                    platform = p.capitalize()
                    break
        
        # Get selected installation status
        install_status = 'All Games'
        if not self.install_all.isChecked():
            if self.install_installed.isChecked():
                install_status = 'Installed'
            elif self.install_not_installed.isChecked():
                install_status = 'Not Installed'
        
        # Emit the filters
        filters = {
            'genre': genre,
            'platform': platform,
            'install_status': install_status
        }
        self.filtersApplied.emit(filters)
        self.accept()

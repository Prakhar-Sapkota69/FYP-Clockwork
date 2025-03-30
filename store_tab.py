from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (QVBoxLayout, QToolBar, QWidget, QTabWidget, 
                              QPushButton, QHBoxLayout, QFrame, QLabel, QSizePolicy)
from PySide6.QtGui import QAction, QIcon, QFont
from PySide6.QtCore import QUrl, Qt, QSize

class StoreWebView(QWebEngineView):
    def __init__(self, url):
        super().__init__()
        self.setUrl(QUrl(url))
        # Set a modern user agent to ensure proper website rendering
        self.page().profile().setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

class NavigationBar(QWidget):
    def __init__(self, web_view, home_url):
        super().__init__()
        self.web_view = web_view
        self.home_url = home_url
        self.setup_ui()
        # Set fixed height for the navigation bar
        self.setFixedHeight(36)

    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(4, 0, 4, 0)  # Reduced vertical margins

        # Create a container frame for the buttons
        button_container = QFrame()
        button_container.setStyleSheet("""
            QFrame {
                background-color: #2C5A68;
                border-radius: 4px;
            }
        """)
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(1)
        button_layout.setContentsMargins(2, 2, 2, 2)

        # Create navigation buttons with modern styling
        self.back_btn = QPushButton()
        self.forward_btn = QPushButton()
        self.refresh_btn = QPushButton()
        self.home_btn = QPushButton()

        # Set icons
        self.back_btn.setIcon(QIcon("./icons/backward.png"))
        self.forward_btn.setIcon(QIcon("./icons/forward.png"))
        self.refresh_btn.setIcon(QIcon("./icons/refresh.png"))
        self.home_btn.setIcon(QIcon("./icons/home.png"))

        # Set tooltips
        self.back_btn.setToolTip("Go Back")
        self.forward_btn.setToolTip("Go Forward")
        self.refresh_btn.setToolTip("Refresh")
        self.home_btn.setToolTip("Home")

        # Set styling
        button_style = """
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 3px;
                margin: 0px;
            }
            QPushButton:hover {
                background-color: #3B82F6;
                border-radius: 2px;
            }
            QPushButton:pressed {
                background-color: #2563EB;
                border-radius: 2px;
            }
        """
        for btn in [self.back_btn, self.forward_btn, self.refresh_btn, self.home_btn]:
            btn.setStyleSheet(button_style)
            btn.setFixedSize(24, 24)
            btn.setIconSize(QSize(16, 16))

        # Connect signals
        self.back_btn.clicked.connect(self.web_view.back)
        self.forward_btn.clicked.connect(self.web_view.forward)
        self.refresh_btn.clicked.connect(self.web_view.reload)
        self.home_btn.clicked.connect(lambda: self.web_view.setUrl(QUrl(self.home_url)))

        # Add buttons to button container
        button_layout.addWidget(self.back_btn)
        button_layout.addWidget(self.forward_btn)
        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.home_btn)

        # Add button container to main layout
        layout.addWidget(button_container)
        layout.addStretch()
        self.setLayout(layout)

class StoreTab(QWidget):
    def __init__(self, url, title, icon_path=None):
        super().__init__()
        self.url = url
        self.title = title
        self.icon_path = icon_path
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create web view
        self.web_view = StoreWebView(self.url)
        self.web_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Create navigation bar
        self.nav_bar = NavigationBar(self.web_view, self.url)
        self.nav_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Add loading indicator
        self.loading_label = QLabel("Loading...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("""
            QLabel {
                color: #E2E8F0;
                font-size: 16px;
                padding: 10px;
                background-color: #2C5A68;
                border-radius: 4px;
            }
        """)
        self.loading_label.hide()

        # Connect loading state signals
        self.web_view.loadStarted.connect(lambda: self.loading_label.show())
        self.web_view.loadFinished.connect(lambda: self.loading_label.hide())

        # Add widgets to layout
        layout.addWidget(self.nav_bar)
        layout.addWidget(self.loading_label)
        layout.addWidget(self.web_view, 1)  # Give web view a stretch factor of 1

        self.setLayout(layout)

def create_store_tabs():
    """
    Creates a tabbed widget containing both Steam and Epic Games stores.
    """
    # Create main container
    container = QWidget()
    layout = QVBoxLayout()
    container.setLayout(layout)

    # Create tab widget with modern styling
    tabs = QTabWidget()
    tabs.setStyleSheet("""
        QTabWidget {
            background-color: #204B57;
        }
        QTabWidget::pane {
            border: none;
            background-color: #204B57;
        }
        QTabBar::tab {
            background-color: #2C5A68;
            color: #94A3B8;
            padding: 12px 20px;
            margin: 2px;
            border: none;
            border-radius: 4px;
            font-size: 14px;
            font-weight: bold;
        }
        QTabBar::tab:selected {
            background-color: #3B82F6;
            color: white;
        }
        QTabBar::tab:hover:!selected {
            background-color: #3B82F6;
            color: white;
            opacity: 0.8;
        }
    """)

    # Create Steam store tab
    steam_tab = StoreTab(
        url="https://store.steampowered.com/",
        title="Steam Store",
        icon_path="./icons/steam.png"
    )

    # Create Epic Games store tab
    epic_tab = StoreTab(
        url="https://store.epicgames.com/",
        title="Epic Games Store",
        icon_path="./icons/epic.png"
    )

    # Add tabs
    tabs.addTab(steam_tab, QIcon("./icons/steam.png"), "Steam Store")
    tabs.addTab(epic_tab, QIcon("./icons/epic.png"), "Epic Games Store")

    layout.addWidget(tabs)

    return container
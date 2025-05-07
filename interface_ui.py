from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QGroupBox,
    QHBoxLayout, QLCDNumber, QLabel, QLineEdit,
    QMainWindow, QProgressBar, QPushButton, QSizePolicy,
    QSpacerItem, QStackedWidget, QVBoxLayout, QWidget, QComboBox, QButtonGroup, QSlider)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(950, 600)
        MainWindow.setMinimumSize(QSize(800, 600))
        MainWindow.setStyleSheet(u"* {\n"
"            background-color: #204B57;\n"
"            color: #E2E8F0;\n"
"            font-family: 'Segoe UI', Arial, sans-serif;\n"
"        }\n"
"        QPushButton {\n"
"            border-radius: 8px;\n"
"            padding: 8px 16px;\n"
"            font-size: 14px;\n"
"            font-weight: 600;\n"
"            color: white;\n"
"            background-color: #3B82F6;\n"
"            border: none;\n"
"        }\n"
"        QPushButton:hover {\n"
"            background-color: #2563EB;\n"
"        }\n"
"        QPushButton:pressed {\n"
"            background-color: #1D4ED8;\n"
"        }\n"
"        QPushButton:checked {\n"
"            background-color: #1E40AF;\n"
"            color: white;\n"
"        }\n"
"        QLabel {\n"
"            font-size: 16px;\n"
"            font-weight: bold;\n"
"            color: #E2E8F0;\n"
"        }\n"
"        QSpacerItem {\n"
"            background-color: transparent;\n"
"        }\n"
"        QWidget {\n"
"            background-color: #204B57;\n"
"            border-radius: 12px;\n"
"        }\n"
"        #leftMenu {\n"
"            background-color: #1E293B;\n"
"            border-radius: 0;\n"
"            border-top-right-radius: 24px;\n"
"            border-bottom-right-radius: 24px;\n"
"            padding: 8px;\n"
"        }\n"
"        #leftMenu QPushButton {\n"
"            border-radius: 8px;\n"
"            text-align: left;\n"
"            padding: 12px 16px;\n"
"            margin: 2px 8px;\n"
"            color: #94A3B8;\n"
"            background-color: transparent;\n"
"            font-weight: 500;\n"
"        }\n"
"        #leftMenu QPushButton:hover {\n"
"            background-color: rgba(59, 130, 246, 0.1);\n"
"            color: #E2E8F0;\n"
"        }\n"
"        #leftMenu QPushButton:checked {\n"
"            color: white;\n"
"            background-color: rgba(59, 130, 246, 0.2);\n"
"            border-left: 3px solid #3B82F6;\n"
"        }\n"
"        #gameButton, #systemButton {\n"
"            font-size: 18px;\n"
"            font-weight: 900;\n"
"            color: #1a1a1a;\n"
"            background-color: transparent;\n"
"            border: none;\n"
"            margin-top: 10px;\n"
"            margin-bottom: 10px;\n"
"            cursor: default;\n"
"            padding: 12px 16px;\n"
"        }\n"
"        #gameButton:hover, #systemButton:hover {\n"
"            background-color: transparent;\n"
"        }\n"
"        #gameButton:pressed, #systemButton:pressed {\n"
"            background-color: transparent;\n"
"        }\n"
"        #gameButton:checked, #systemButton:checked {\n"
"            background-color: transparent;\n"
"            border-left: none;\n"
"        }\n"
"        #centerMenu {\n"
"            background-color: #204B57;\n"
"            border-radius: 0;\n"
"        }\n"
"        #stackedWidget {\n"
"            background-color: transparent;\n"
"            border-radius: 16px;\n"
"        }\n"
"        #stackedWidget > QWidget {\n"
"            background-color: #204B57;\n"
"            border-radius: 16px;\n"
"            border: 1px solid #2C5A68;\n"
"        }\n"
"        QLineEdit {\n"
"            background-color: #2C5A68;\n"
"            border: 2px solid #3B82F6;\n"
"            border-radius: 20px;\n"
"            padding: 0 16px;\n"
"            color: #E2E8F0;\n"
"            font-size: 14px;\n"
"        }\n"
"        QLineEdit:focus {\n"
"            border: 2px solid #60A5FA;\n"
"        }\n"
"        QLineEdit::placeholder {\n"
"            color: #94A3B8;\n"
"        }\n"
"        QProgressBar {\n"
"            border: none;\n"
"            border-radius: 8px;\n"
"            text-align: center;\n"
"            background-color: #2C5A68;\n"
"            height: 8px;\n"
"            font-size: 12px;\n"
"        }\n"
"        QProgressBar::chunk {\n"
"            background-color: #3B82F6;\n"
"            border-radius: 8px;\n"
"        }\n"
"        QLCDNumber {\n"
"            background-color: #2C5A68;\n"
"            color: #3B82F6;\n"
"            border: none;\n"
"            border-radius: 8px;\n"
"            padding: 8px;\n"
"        }\n"
"        QGroupBox {\n"
"            border: 2px solid #2C5A68;\n"
"            border-radius: 12px;\n"
"            margin-top: 12px;\n"
"            padding: 8px;\n"
"            background-color: #204B57;\n"
"            font-weight: bold;\n"
"        }\n"
"        QGroupBox::title {\n"
"            color: #94A3B8;\n"
"            padding: 0 8px;\n"
"        }\n"
"        QFrame {\n"
"            background-color: #2C5A68;\n"
"            border: 1px solid #2C5A68;\n"
"            border-radius: 12px;\n"
"        }\n"
"        #gameGridWidget {\n"
"            background-color: transparent;\n"
"            border: none;\n"
"        }\n"
"        #manualAddBtn {\n"
"            border-radius: 20px;\n"
"            padding: 8px;\n"
"        }\n"
"        #searchGames {\n"
"            padding: 8px 20px;\n"
"            background-color: #10B981;\n"
"        }\n"
"        #searchGames:hover {\n"
"            background-color: #059669;\n"
"        }\n"
"        #backupButton, #optimizeNowBtn {\n"
"            background-color: #10B981;\n"
"            padding: 8px 24px;\n"
"        }\n"
"        #backupButton:hover, #optimizeNowBtn:hover {\n"
"            background-color: #059669;\n"
"        }\n"
"        #toggleOverlay {\n"
"            background-color: #6366F1;\n"
"            padding: 12px 24px;\n"
"        }\n"
"        #toggleOverlay:hover {\n"
"            background-color: #4F46E5;\n"
"        }\n"
"        #steamStoreBtn {\n"
"            background-color: #1B2838;\n"
"            padding: 12px 24px;\n"
"            font-size: 16px;\n"
"        }\n"
"        #steamStoreBtn:hover {\n"
"            background-color: #2A475E;\n"
"        }")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)

        # Left Menu
        self.leftMenu = QWidget(self.centralwidget)
        self.leftMenu.setObjectName(u"leftMenu")
        self.leftMenu.setMinimumSize(QSize(200, 0))
        self.leftMenu.setMaximumSize(QSize(200, 16777215))
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        self.leftMenu.setSizePolicy(sizePolicy1)
        
        self.verticalLayout = QVBoxLayout(self.leftMenu)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        # Menu buttons
        self.menuBtn = QPushButton(self.leftMenu)
        self.menuBtn.setObjectName(u"menuBtn")
        self.menuBtn.setIcon(QIcon(u"icons/menu.png"))
        self.menuBtn.setIconSize(QSize(24, 24))
        self.verticalLayout.addWidget(self.menuBtn)

        # Add GAMES label just above the game-related buttons
        self.gameButton = QPushButton(self.leftMenu)
        self.gameButton.setObjectName(u"gameButton")
        self.gameButton.setText(u"GAMES")
        self.gameButton.setIcon(QIcon(u"icons/game.png"))
        self.gameButton.setIconSize(QSize(24, 24))
        self.gameButton.setEnabled(False)
        self.gameButton.setStyleSheet("""
            QPushButton {
                color: #E2E8F0;
                text-align: left;
                padding-left: 10px;
                font-weight: bold;
                border: none;
                background-color: transparent;
            }
            QPushButton:disabled {
                color: #E2E8F0;
                opacity: 1.0;
            }
        """)
        self.verticalLayout.addWidget(self.gameButton)

        self.libraryBtn = QPushButton(self.leftMenu)
        self.libraryBtn.setObjectName(u"libraryBtn")
        self.libraryBtn.setText(u"Library")
        self.libraryBtn.setIcon(QIcon(u"icons/lib.png"))
        self.libraryBtn.setIconSize(QSize(24, 24))
        self.libraryBtn.setCheckable(True)
        self.verticalLayout.addWidget(self.libraryBtn)

        self.storeBtn = QPushButton(self.leftMenu)
        self.storeBtn.setObjectName(u"storeBtn")
        self.storeBtn.setText(u"Store")
        self.storeBtn.setIcon(QIcon(u"icons/store.png"))
        self.storeBtn.setIconSize(QSize(24, 24))
        self.storeBtn.setCheckable(True)
        self.verticalLayout.addWidget(self.storeBtn)

        self.verticalLayout.addStretch()

        # Add SYSTEM label just above the system-related buttons
        self.systemButton = QPushButton(self.leftMenu)
        self.systemButton.setObjectName(u"systemButton")
        self.systemButton.setText(u"SYSTEM")
        self.systemButton.setIcon(QIcon(u"icons/system.png"))
        self.systemButton.setIconSize(QSize(24, 24))
        self.systemButton.setEnabled(False)
        self.systemButton.setStyleSheet("""
            QPushButton {
                color: #E2E8F0;
                text-align: left;
                padding-left: 10px;
                font-weight: bold;
                border: none;
                background-color: transparent;
            }
            QPushButton:disabled {
                color: #E2E8F0;
                opacity: 1.0;
            }
        """)
        self.verticalLayout.addWidget(self.systemButton)

        # System-related buttons
        self.optimizationBtn = QPushButton(self.leftMenu)
        self.optimizationBtn.setObjectName(u"optimizationBtn")
        self.optimizationBtn.setText(u"Optimization")
        self.optimizationBtn.setIcon(QIcon(u"icons/monitoring.png"))
        self.optimizationBtn.setIconSize(QSize(24, 24))
        self.optimizationBtn.setCheckable(True)
        self.verticalLayout.addWidget(self.optimizationBtn)

        self.overlayBtn = QPushButton(self.leftMenu)
        self.overlayBtn.setObjectName(u"overlayBtn")
        self.overlayBtn.setText(u"Overlay")
        self.overlayBtn.setIcon(QIcon(u"icons/overlay.png"))
        self.overlayBtn.setIconSize(QSize(24, 24))
        self.overlayBtn.setCheckable(True)
        self.verticalLayout.addWidget(self.overlayBtn)

        self.savefileBtn = QPushButton(self.leftMenu)
        self.savefileBtn.setObjectName(u"savefileBtn")
        self.savefileBtn.setText(u"Save files")
        self.savefileBtn.setIcon(QIcon(u"icons/savefile.png"))
        self.savefileBtn.setIconSize(QSize(24, 24))
        self.savefileBtn.setCheckable(True)
        self.verticalLayout.addWidget(self.savefileBtn)

        self.verticalLayout.addStretch()

        self.horizontalLayout.addWidget(self.leftMenu)

        self.centerMenu = QWidget(self.centralwidget)
        self.centerMenu.setObjectName(u"centerMenu")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(1)
        sizePolicy2.setVerticalStretch(0)
        self.centerMenu.setSizePolicy(sizePolicy2)
        self.centerMenu.setMinimumSize(QSize(600, 0))
        
        self.verticalLayout_5 = QVBoxLayout(self.centerMenu)
        self.verticalLayout_5.setSpacing(10)
        self.verticalLayout_5.setContentsMargins(10, 10, 10, 10)

        # Stacked Widget
        self.stackedWidget = QStackedWidget(self.centerMenu)
        self.stackedWidget.setObjectName(u"stackedWidget")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(1)
        self.stackedWidget.setSizePolicy(sizePolicy3)
        
        # Home Page
        self.homePage = QWidget()
        self.homePage.setObjectName(u"homePage")
        self.homeLayout = QVBoxLayout(self.homePage)
        self.homeLayout.setSpacing(15)
        self.homeLayout.setContentsMargins(15, 15, 15, 15)

        # Title Label
        self.label_3 = QLabel(self.homePage)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setText(u"Your Games")
        self.label_3.setAlignment(Qt.AlignCenter)
        self.label_3.setStyleSheet("""
            QLabel {
                color: #E2E8F0;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
            }
        """)
        self.homeLayout.addWidget(self.label_3)

        # Header Layout
        self.headerWidget = QWidget(self.homePage)
        self.headerLayout = QHBoxLayout(self.headerWidget)
        self.headerLayout.setSpacing(15)
        self.headerLayout.setContentsMargins(0, 0, 0, 0)

        # Game count label
        self.gameCountLabel = QLabel(self.headerWidget)
        self.gameCountLabel.setObjectName(u"gameCountLabel")
        self.gameCountLabel.setText(u"0 Games")
        self.gameCountLabel.setStyleSheet("""
            QLabel {
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
            QLabel:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #044a7a, stop:1 #055a9a);
                border: 2px solid #066aba;
            }
        """)
        self.headerLayout.addWidget(self.gameCountLabel)

        # Filter button
        self.filterBtn = QPushButton(self.headerWidget)
        self.filterBtn.setObjectName(u"filterBtn")
        self.filterBtn.setText(u"Filters")
        self.filterBtn.setIcon(QIcon(u"icons/filter.png"))
        self.filterBtn.setIconSize(QSize(20, 20))
        self.filterBtn.setStyleSheet("""
            QPushButton {
                background-color: #2C5A68;
                border: 1px solid #3B82F6;
                border-radius: 8px;
                padding: 8px 16px;
                color: #E2E8F0;
                font-size: 14px;
                font-weight: 600;
                min-height: 36px;
            }
            QPushButton:hover {
                background-color: #3B82F6;
                color: white;
            }
            QPushButton:pressed {
                background-color: #2563EB;
            }
        """)
        self.headerLayout.addWidget(self.filterBtn)

        # Create search container
        search_container = QWidget(self.headerWidget)
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(0)

        # Create search box with icon
        self.lineEdit = QLineEdit(search_container)
        self.lineEdit.setPlaceholderText("Search games...")
        self.lineEdit.setMinimumHeight(36)
        self.lineEdit.setMinimumWidth(300)
        self.lineEdit.setAlignment(Qt.AlignCenter)
        self.lineEdit.setStyleSheet("""
            QLineEdit {
                background-color: #2C5A68;
                color: #E2E8F0;
                border: 1px solid #3B82F6;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
                min-height: 36px;
            }
            QLineEdit:focus {
                border: 1px solid #3B82F6;
                background-color: #3B82F6;
            }
        """)
        
        # Add search icon to the center inside the QLineEdit
        search_icon = QLabel(self.lineEdit)
        search_icon.setPixmap(QPixmap("icons/search.png").scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        search_icon.setStyleSheet("background: transparent; border: none; padding: 0px;")
        
        # Add clear button
        self.clearSearchBtn = QPushButton(self.lineEdit)
        self.clearSearchBtn.setFixedSize(30, 30)
        self.clearSearchBtn.setIcon(QIcon("icons/clear.png"))
        self.clearSearchBtn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 5px;
                margin-right: 5px;
            }
            QPushButton:hover {
                background-color: #3B82F6;
                border-radius: 15px;
            }
            QPushButton:pressed {
                background-color: #2563EB;
            }
        """)
        self.clearSearchBtn.setVisible(False)
        
        # Position the icon and clear button
        self.lineEdit.setStyleSheet("""
            QLineEdit {
                background-color: #2C5A68;
                border: 3px solid #3B82F6;
                border-radius: 12px;
                padding: 8px 40px;
                color: #E2E8F0;
                font-size: 15px;
            }
            QLineEdit:focus {
                border: 3px solid #60A5FA;
                background-color: #1E3A4A;
            }
            QLineEdit::placeholder {
                color: #94A3B8;
            }
        """)
        
        # Position the icon and clear button within the QLineEdit
        def updateIconPosition():
            # Center the search icon
            icon_x = (self.lineEdit.width() - search_icon.width()) // 2 - 35  # Offset to account for text
            icon_y = (self.lineEdit.height() - search_icon.height()) // 2
            search_icon.move(icon_x, icon_y)
            
            # Position clear button on the right
            clear_x = self.lineEdit.width() - self.clearSearchBtn.width() - 5
            clear_y = (self.lineEdit.height() - self.clearSearchBtn.height()) // 2
            self.clearSearchBtn.move(clear_x, clear_y)
        
        # Connect the resize event to update positions
        self.lineEdit.resizeEvent = lambda event: updateIconPosition()
        
        search_layout.addWidget(self.lineEdit)
        self.headerLayout.addWidget(search_container)

        # Add stretch to push right-side buttons to the right
        self.headerLayout.addStretch()

        # Manual Add button
        self.manualAddBtn = QPushButton(self.headerWidget)
        self.manualAddBtn.setObjectName(u"manualAddBtn")
        self.manualAddBtn.setIcon(QIcon(u"icons/plus.png"))
        self.manualAddBtn.setIconSize(QSize(20, 20))
        self.manualAddBtn.setStyleSheet("""
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
        self.headerLayout.addWidget(self.manualAddBtn)

        # Import Games button
        self.searchGames = QPushButton(self.headerWidget)
        self.searchGames.setObjectName(u"searchGames")
        self.searchGames.setText(u"Import games")
        self.searchGames.setIcon(QIcon(u"icons/import.png"))
        self.searchGames.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                border: 1px solid #059669;
                border-radius: 8px;
                padding: 8px 16px;
                color: white;
                font-size: 14px;
                font-weight: 600;
                min-height: 36px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """)
        self.headerLayout.addWidget(self.searchGames)

        # Refresh button
        self.refreshGames = QPushButton(self.headerWidget)
        self.refreshGames.setObjectName(u"refreshGames")
        self.refreshGames.setText(u"Refresh")
        self.refreshGames.setIcon(QIcon(u"icons/refresh.png"))
        self.refreshGames.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                border: 1px solid #059669;
                border-radius: 8px;
                padding: 8px 16px;
                color: white;
                font-size: 14px;
                font-weight: 600;
                min-height: 36px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """)
        self.headerLayout.addWidget(self.refreshGames)

        self.homeLayout.addWidget(self.headerWidget)

        # Game Grid Widget
        self.gameGridWidget = QWidget(self.homePage)
        self.gameGridWidget.setObjectName(u"gameGridWidget")
        self.gameGridLayout = QGridLayout(self.gameGridWidget)
        self.gameGridLayout.setSpacing(15)
        self.homeLayout.addWidget(self.gameGridWidget)

        self.stackedWidget.addWidget(self.homePage)

        # Save File Tab
        self.saveFileTab = QWidget()
        self.saveFileTab.setObjectName(u"saveFileTab")
        self.saveFileLayout = QVBoxLayout(self.saveFileTab)
        self.saveFileLayout.setSpacing(20)
        self.saveFileLayout.setContentsMargins(30, 30, 30, 30)

        # Title with Icon
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setSpacing(15)
        
        title_icon = QLabel()
        title_icon.setPixmap(QIcon("icons/savefile.png").pixmap(32, 32))
        title_layout.addWidget(title_icon)
        
        self.label_7 = QLabel("Save Files Manager")
        self.label_7.setObjectName(u"label_7")
        self.label_7.setStyleSheet("""
            QLabel {
                color: #E2E8F0;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        title_layout.addWidget(self.label_7)
        title_layout.addStretch()
        self.saveFileLayout.addWidget(title_container)

        # Main Container
        self.saveFileContainer = QWidget(self.saveFileTab)
        self.saveFileContainer.setMaximumWidth(800)
        self.saveFileContainer.setStyleSheet("""
            QWidget {
                background-color: #2C5A68;
                border-radius: 12px;
                border: 1px solid #3B82F6;
            }
        """)
        
        self.saveFileContainerLayout = QVBoxLayout(self.saveFileContainer)
        self.saveFileContainerLayout.setSpacing(20)
        self.saveFileContainerLayout.setContentsMargins(20, 20, 20, 20)

        # Backup Location
        folder_widget = QWidget()
        folder_layout = QHBoxLayout(folder_widget)
        folder_layout.setSpacing(10)
        folder_layout.setContentsMargins(0, 0, 0, 0)

        self.backup_folder_path = QLineEdit()
        self.backup_folder_path.setObjectName(u"backup_folder_path")
        self.backup_folder_path.setPlaceholderText("Select backup folder...")
        self.backup_folder_path.setReadOnly(True)
        self.backup_folder_path.setStyleSheet("""
            QLineEdit {
                background-color: #204B57;
                border: 2px solid #3B82F6;
                border-radius: 8px;
                padding: 8px 16px;
                color: #E2E8F0;
                font-size: 14px;
            }
        """)
        folder_layout.addWidget(self.backup_folder_path)

        self.browseBackupButton = QPushButton("Browse")
        self.browseBackupButton.setObjectName(u"browseBackupButton")
        self.browseBackupButton.setIcon(QIcon(u"icons/folder.png"))
        self.browseBackupButton.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton:pressed {
                background-color: #1D4ED8;
            }
        """)
        folder_layout.addWidget(self.browseBackupButton)
        self.saveFileContainerLayout.addWidget(folder_widget)

        # Progress Section
        self.progressBar = QProgressBar()
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(0)
        self.progressBar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 4px;
                text-align: center;
                background-color: #204B57;
                height: 8px;
            }
            QProgressBar::chunk {
                background-color: #723D46;
                border-radius: 4px;
            }
        """)
        self.saveFileContainerLayout.addWidget(self.progressBar)

        self.statusLabel = QLabel("Select a backup folder and press Backup to begin")
        self.statusLabel.setObjectName(u"statusLabel")
        self.statusLabel.setAlignment(Qt.AlignCenter)
        self.statusLabel.setStyleSheet("""
            color: #E2E8F0;
            font-size: 14px;
            margin-top: 10px;
        """)
        self.saveFileContainerLayout.addWidget(self.statusLabel)

        # Backup Button
        self.backupButton = QPushButton("Backup Now")
        self.backupButton.setObjectName(u"backupButton")
        self.backupButton.setIcon(QIcon(u"icons/backup.png"))
        self.backupButton.setStyleSheet("""
            QPushButton {
                background-color: #723D46;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #8B4B55;
            }
            QPushButton:pressed {
                background-color: #5A3037;
            }
        """)
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.addStretch()
        button_layout.addWidget(self.backupButton)
        button_layout.addStretch()
        self.saveFileContainerLayout.addWidget(button_container)

        # Add container to main layout with some spacing
        container_wrapper = QHBoxLayout()
        container_wrapper.addStretch()
        container_wrapper.addWidget(self.saveFileContainer)
        container_wrapper.addStretch()
        self.saveFileLayout.addLayout(container_wrapper)
        self.saveFileLayout.addStretch()

        self.stackedWidget.addWidget(self.saveFileTab)

        # Overlay Tab
        self.setup_overlay_tab()

        # Optimization Tab
        self.optimizationTab = QWidget()
        self.optimizationTab.setObjectName(u"optimizationTab")
        self.optimizationLayout = QVBoxLayout(self.optimizationTab)
        self.optimizationLayout.setSpacing(20)
        self.optimizationLayout.setContentsMargins(30, 30, 30, 30)

        # Title Label with Icon
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setSpacing(15)
        
        title_icon = QLabel()
        title_icon.setPixmap(QIcon("icons/monitoring.png").pixmap(32, 32))
        title_layout.addWidget(title_icon)
        
        self.label_2 = QLabel("System Information")
        self.label_2.setObjectName(u"label_2")
        self.label_2.setAlignment(Qt.AlignLeft)
        self.label_2.setStyleSheet("""
            QLabel {
                color: #E2E8F0;
                font-size: 28px;
                font-weight: bold;
            }
        """)
        title_layout.addWidget(self.label_2)
        title_layout.addStretch()
        self.optimizationLayout.addWidget(title_container)

        # Container for main content
        self.optimizationContainer = QWidget(self.optimizationTab)
        self.optimizationContainer.setStyleSheet("""
            QWidget {
                background-color: #204B57;
                border-radius: 15px;
                border: 1px solid #2C5A68;
            }
        """)
        
        self.optimizationContainerLayout = QVBoxLayout(self.optimizationContainer)
        self.optimizationContainerLayout.setSpacing(15)
        self.optimizationContainerLayout.setContentsMargins(20, 20, 20, 20)

        # System Info Cards Layout
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(10)
        cards_layout.setContentsMargins(0, 0, 0, 0)

        # CPU Usage Card
        cpu_card = QFrame()
        cpu_card.setStyleSheet("""
            QFrame {
                background-color: #2C5A68;
                border-radius: 12px;
                padding: 15px;
                border: 2px solid #3B82F6;
                min-width: 150px;
            }
            QFrame:hover {
                background-color: #265461;
                border: 2px solid #60A5FA;
                box-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
            }
        """)
        cpu_layout = QVBoxLayout(cpu_card)
        cpu_layout.setSpacing(10)
        cpu_layout.setContentsMargins(0, 0, 0, 0)
        
        cpu_header = QHBoxLayout()
        cpu_icon = QLabel()
        cpu_icon.setPixmap(QIcon("icons/cpu-usage.png").pixmap(24, 24))
        cpu_icon.setStyleSheet("background: transparent;")
        cpu_header.addWidget(cpu_icon)
        
        cpu_title = QLabel("CPU Usage")
        cpu_title.setStyleSheet("""
            color: #94A3B8;
            font-size: 14px;
            font-weight: bold;
        """)
        cpu_header.addWidget(cpu_title)
        cpu_header.addStretch()
        cpu_layout.addLayout(cpu_header)
        
        # Add CPU value label
        self.cpuLabel = QLabel("0%")
        self.cpuLabel.setStyleSheet("""
            color: #E2E8F0;
            font-size: 24px;
            font-weight: bold;
        """)
        cpu_layout.addWidget(self.cpuLabel)
        
        cards_layout.addWidget(cpu_card)

        # RAM Usage Card
        ram_card = QFrame()
        ram_card.setStyleSheet("""
            QFrame {
                background-color: #2C5A68;
                border-radius: 12px;
                padding: 15px;
                border: 2px solid #3B82F6;
                min-width: 150px;
            }
            QFrame:hover {
                background-color: #265461;
                border: 2px solid #60A5FA;
                box-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
            }
        """)
        ram_layout = QVBoxLayout(ram_card)
        ram_layout.setSpacing(10)
        ram_layout.setContentsMargins(0, 0, 0, 0)
        
        ram_header = QHBoxLayout()
        ram_icon = QLabel()
        ram_icon.setPixmap(QIcon("icons/ram-usage.png").pixmap(24, 24))
        ram_icon.setStyleSheet("background: transparent;")
        ram_header.addWidget(ram_icon)
        
        ram_title = QLabel("RAM Usage")
        ram_title.setStyleSheet("""
            color: #94A3B8;
            font-size: 14px;
            font-weight: bold;
        """)
        ram_header.addWidget(ram_title)
        ram_header.addStretch()
        ram_layout.addLayout(ram_header)
        
        # Add RAM value label
        self.ramLabel = QLabel("0%")
        self.ramLabel.setStyleSheet("""
            color: #E2E8F0;
            font-size: 24px;
            font-weight: bold;
        """)
        ram_layout.addWidget(self.ramLabel)
        
        cards_layout.addWidget(ram_card)

        # Disk Usage Card
        disk_card = QFrame()
        disk_card.setStyleSheet("""
            QFrame {
                background-color: #2C5A68;
                border-radius: 12px;
                padding: 15px;
                border: 2px solid #3B82F6;
                min-width: 150px;
            }
            QFrame:hover {
                background-color: #265461;
                border: 2px solid #60A5FA;
                box-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
            }
        """)
        disk_layout = QVBoxLayout(disk_card)
        disk_layout.setSpacing(10)
        disk_layout.setContentsMargins(0, 0, 0, 0)
        
        disk_header = QHBoxLayout()
        disk_icon = QLabel()
        disk_icon.setPixmap(QIcon("icons/ssd-usage.png").pixmap(24, 24))
        disk_icon.setStyleSheet("background: transparent;")
        disk_header.addWidget(disk_icon)
        
        disk_title = QLabel("Disk Usage")
        disk_title.setStyleSheet("""
            color: #94A3B8;
            font-size: 14px;
            font-weight: bold;
        """)
        disk_header.addWidget(disk_title)
        disk_header.addStretch()
        disk_layout.addLayout(disk_header)
        
        self.diskLabel = QLabel("0 MB/s")
        self.diskLabel.setStyleSheet("""
            color: #E2E8F0;
            font-size: 24px;
            font-weight: bold;
        """)
        disk_layout.addWidget(self.diskLabel)
        
        cards_layout.addWidget(disk_card)
        
        self.optimizationContainerLayout.addLayout(cards_layout)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("""
            QFrame {
                border: none;
                background-color: #3B3B3B;
                max-height: 1px;
            }
        """)
        self.optimizationContainerLayout.addWidget(separator)

        # Optimization Section
        optimize_section = QWidget()
        optimize_layout = QVBoxLayout(optimize_section)
        optimize_layout.setSpacing(15)
        
        # Optimization description
        description_label = QLabel("System Optimization")
        description_label.setStyleSheet("""
            QLabel {
                color: #94A3B8;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        optimize_layout.addWidget(description_label)
        
        features_widget = QWidget()
        features_layout = QHBoxLayout(features_widget)
        features_layout.setSpacing(10)
        
        # Feature bullets
        bullet_points = [
            "🗑️ Clear temporary files",
            "⚡ Manage system processes",
            "💻 Improve system performance"
        ]
        
        for bullet in bullet_points:
            bullet_label = QLabel(bullet)
            bullet_label.setStyleSheet("""
                QLabel {
                    color: #E2E8F0;
                    font-size: 14px;
                    padding: 8px 16px;
                    background-color: #2C2C2C;
                    border-radius: 8px;
                }
            """)
            features_layout.addWidget(bullet_label)
        
        features_layout.addStretch()
        optimize_layout.addWidget(features_widget)
        
        # Buttons container
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 10, 0, 0)
        button_layout.setSpacing(15)  # Add spacing between buttons
        
        # Clean Temp Files button
        self.cleanTempBtn = QPushButton("Clean Temporary Files")
        self.cleanTempBtn.setObjectName(u"cleanTempBtn")
        self.cleanTempBtn.setIcon(QIcon(u"icons/clean.png"))
        self.cleanTempBtn.setStyleSheet("""
            QPushButton {
                background-color: #723D46;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #8B4B55;
            }
            QPushButton:pressed {
                background-color: #5A3037;
            }
        """)
        button_layout.addWidget(self.cleanTempBtn)

        # Manage Processes button
        self.manageProcessesBtn = QPushButton("Manage System Processes")
        self.manageProcessesBtn.setObjectName(u"manageProcessesBtn")
        self.manageProcessesBtn.setIcon(QIcon(u"icons/process.png"))
        self.manageProcessesBtn.setStyleSheet("""
            QPushButton {
                background-color: #723D46;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #8B4B55;
            }
            QPushButton:pressed {
                background-color: #5A3037;
            }
        """)
        button_layout.addWidget(self.manageProcessesBtn)
        
        button_layout.addStretch()
        optimize_layout.addWidget(button_container)
        self.optimizationContainerLayout.addWidget(optimize_section)

        # Add the container to the main layout
        self.optimizationLayout.addWidget(self.optimizationContainer)
        self.optimizationLayout.addStretch()

        self.stackedWidget.addWidget(self.optimizationTab)

        # Store Tab
        self.storeTab = QWidget()
        self.storeTab.setObjectName(u"storeTab")
        sizePolicy4 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy4.setHorizontalStretch(1)
        sizePolicy4.setVerticalStretch(1)
        self.storeTab.setSizePolicy(sizePolicy4)
        
        self.storeLayout = QVBoxLayout(self.storeTab)
        self.storeLayout.setSpacing(0)
        self.storeLayout.setContentsMargins(0, 0, 0, 0)

        self.stackedWidget.addWidget(self.storeTab)

        self.verticalLayout_5.addWidget(self.stackedWidget)
        self.horizontalLayout.addWidget(self.centerMenu)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(0)

        # Update stylesheet to handle maximized state
        MainWindow.setStyleSheet(MainWindow.styleSheet() + """
        QMainWindow {
            background-color: #204B57;
        }
        QWidget#centralwidget {
            background-color: #204B57;
        }
        #centerMenu {
            background-color: #204B57;
        }
        #stackedWidget {
            background-color: #204B57;
            border: none;
        }
        #stackedWidget > QWidget {
            background-color: #204B57;
            margin: 0px;
            border: none;
        }
        #storeTab {
            background-color: #204B57;
            margin: 0px;
            padding: 0px;
            border: none;
            border-radius: 0px;
        }
        #storeTab > QWidget {
            background-color: #204B57;
            margin: 0px;
            padding: 0px;
            border: none;
            border-radius: 0px;
        }
        QWebEngineView {
            background-color: #204B57;
            border: none;
        }
        """)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.menuBtn.setText("")
        self.gameButton.setText(QCoreApplication.translate("MainWindow", u"GAMES", None))
        self.libraryBtn.setText(QCoreApplication.translate("MainWindow", u"Library", None))
        self.storeBtn.setText(QCoreApplication.translate("MainWindow", u"Store", None))
        self.optimizationBtn.setText(QCoreApplication.translate("MainWindow", u"Optimization", None))
        self.overlayBtn.setText(QCoreApplication.translate("MainWindow", u"Overlay", None))
        self.savefileBtn.setText(QCoreApplication.translate("MainWindow", u"Save files", None))
#if QT_CONFIG(whatsthis)
        self.centerMenu.setWhatsThis(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><br/></p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Your Games", None))
        self.manualAddBtn.setText("")
        self.searchGames.setText(QCoreApplication.translate("MainWindow", u"Import games", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Save files manager", None))
        self.backupButton.setText(QCoreApplication.translate("MainWindow", u"Backup", None))
        self.browseBackupButton.setText(QCoreApplication.translate("MainWindow", u"Browse backup folder", None))
        self.statusLabel.setText(QCoreApplication.translate("MainWindow", u"Press Backup button after selecting folder.", None))
        self.toggleOverlayBtn.setText(QCoreApplication.translate("MainWindow", u"Toggle Overlay", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"System Information", None))
        self.cleanTempBtn.setText(QCoreApplication.translate("MainWindow", u"Clean Temporary Files", None))
        self.manageProcessesBtn.setText(QCoreApplication.translate("MainWindow", u"Manage System Processes", None))
    # retranslateUi

    def setup_overlay_tab(self):
        """Setup the overlay tab with enhanced UI"""
        # Create main container with gradient background
        self.overlayTab = QWidget()
        self.overlayTab.setObjectName("overlayTab")
        self.overlayTab.setStyleSheet("""
            QWidget#overlayTab {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1c2e, stop:1 #2d2b55);
            }
        """)
        
        # Main layout with proper spacing
        overlayLayout = QVBoxLayout(self.overlayTab)
        overlayLayout.setContentsMargins(20, 20, 20, 20)
        overlayLayout.setSpacing(20)
        
        # Title section
        titleContainer = QWidget()
        titleContainer.setObjectName("titleContainer")
        titleContainer.setStyleSheet("""
            QWidget#titleContainer {
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 12px;
                padding: 15px;
            }
        """)
        titleLayout = QVBoxLayout(titleContainer)
        titleLayout.setContentsMargins(15, 15, 15, 15)
        
        titleLabel = QLabel("Overlay Customization")
        titleLabel.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 24px;
                font-weight: bold;
                padding: 5px;
            }
        """)
        titleLayout.addWidget(titleLabel)
        overlayLayout.addWidget(titleContainer)
        
        # Position section
        positionContainer = QWidget()
        positionContainer.setObjectName("positionContainer")
        positionContainer.setStyleSheet("""
            QWidget#positionContainer {
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 12px;
                padding: 15px;
            }
        """)
        positionLayout = QVBoxLayout(positionContainer)
        positionLayout.setContentsMargins(15, 15, 15, 15)
        
        positionLabel = QLabel("Overlay Position")
        positionLabel.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        positionLayout.addWidget(positionLabel)
        
        # Position buttons grid
        positionGrid = QGridLayout()
        positionGrid.setSpacing(10)
        
        # Create button group for position buttons
        self.positionGroup = QButtonGroup()
        
        # Create position buttons with enhanced styling
        self.topLeftBtn = QPushButton("↖")
        self.topRightBtn = QPushButton("↗")
        self.bottomLeftBtn = QPushButton("↙")
        self.bottomRightBtn = QPushButton("↘")
        
        positionButtons = [self.topLeftBtn, self.topRightBtn, self.bottomLeftBtn, self.bottomRightBtn]
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        
        for i, (button, (row, col)) in enumerate(zip(positionButtons, positions)):
            button.setObjectName("positionBtn")
            button.setCheckable(True)
            button.setStyleSheet("""
                QPushButton#positionBtn {
                    background-color: rgba(255, 255, 255, 0.1);
                    color: white;
                    border: 2px solid #5865f2;
                    border-radius: 8px;
                    padding: 15px;
                    font-size: 20px;
                    min-width: 60px;
                    min-height: 60px;
                }
                QPushButton#positionBtn:hover {
                    background-color: rgba(88, 101, 242, 0.2);
                }
                QPushButton#positionBtn:checked {
                    background-color: #5865f2;
                }
            """)
            positionGrid.addWidget(button, row, col)
            self.positionGroup.addButton(button)
        
        positionLayout.addLayout(positionGrid)
        overlayLayout.addWidget(positionContainer)
        
        # Customization section
        customizationContainer = QWidget()
        customizationContainer.setObjectName("customizationContainer")
        customizationContainer.setStyleSheet("""
            QWidget#customizationContainer {
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 12px;
                padding: 15px;
            }
        """)
        customizationLayout = QVBoxLayout(customizationContainer)
        customizationLayout.setContentsMargins(15, 15, 15, 15)
        
        customizationLabel = QLabel("Text Customization")
        customizationLabel.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        customizationLayout.addWidget(customizationLabel)
        
        # Color picker section
        colorContainer = QWidget()
        colorContainer.setObjectName("colorContainer")
        colorContainer.setStyleSheet("""
            QWidget#colorContainer {
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                padding: 10px;
            }
        """)
        colorLayout = QHBoxLayout(colorContainer)
        colorLayout.setContentsMargins(10, 10, 10, 10)
        
        colorLabel = QLabel("Text Color")
        colorLabel.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14px;
                margin-right: 10px;
            }
        """)
        colorLayout.addWidget(colorLabel)
        
        self.colorPicker = QPushButton()
        self.colorPicker.setObjectName("colorPicker")
        self.colorPicker.setFixedSize(40, 40)
        self.colorPicker.setStyleSheet("""
            QPushButton#colorPicker {
                background-color: #ffffff;
                border: 2px solid #5865f2;
                border-radius: 8px;
            }
            QPushButton#colorPicker:hover {
                border: 2px solid #4752c4;
            }
        """)
        colorLayout.addWidget(self.colorPicker)
        colorLayout.addStretch()
        customizationLayout.addWidget(colorContainer)
        
        # Size slider section
        sizeContainer = QWidget()
        sizeContainer.setObjectName("sizeContainer")
        sizeContainer.setStyleSheet("""
            QWidget#sizeContainer {
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                padding: 10px;
                margin-top: 10px;
            }
        """)
        sizeLayout = QVBoxLayout(sizeContainer)
        sizeLayout.setContentsMargins(10, 10, 10, 10)
        
        sizeLabel = QLabel("Text Size")
        sizeLabel.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14px;
                margin-bottom: 5px;
            }
        """)
        sizeLayout.addWidget(sizeLabel)
        
        self.sizeSlider = QSlider(Qt.Horizontal)
        self.sizeSlider.setObjectName("sizeSlider")
        self.sizeSlider.setRange(8, 72)
        self.sizeSlider.setValue(12)
        self.sizeSlider.setStyleSheet("""
            QSlider#sizeSlider {
                height: 20px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #5865f2;
                height: 8px;
                background: rgba(255, 255, 255, 0.1);
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #5865f2;
                border: none;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #4752c4;
            }
            QSlider::sub-page:horizontal {
                background: #5865f2;
                border-radius: 4px;
            }
        """)
        sizeLayout.addWidget(self.sizeSlider)
        customizationLayout.addWidget(sizeContainer)
        
        overlayLayout.addWidget(customizationContainer)
        
        # Toggle Overlay Button
        self.toggleOverlayBtn = QPushButton("Toggle Overlay")
        self.toggleOverlayBtn.setObjectName("toggleOverlayBtn")
        self.toggleOverlayBtn.setStyleSheet("""
            QPushButton#toggleOverlayBtn {
                background-color: #5865f2;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton#toggleOverlayBtn:hover {
                background-color: #4752c4;
            }
            QPushButton#toggleOverlayBtn:pressed {
                background-color: #3b45b5;
            }
        """)
        overlayLayout.addWidget(self.toggleOverlayBtn)
        overlayLayout.addStretch()
        
        # Add the overlay tab to the stacked widget
        self.stackedWidget.addWidget(self.overlayTab)

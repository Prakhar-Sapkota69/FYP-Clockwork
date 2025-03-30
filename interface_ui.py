# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'interface.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

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
    QSpacerItem, QStackedWidget, QVBoxLayout, QWidget, QComboBox)

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

        # Search Line Edit
        self.lineEdit = QLineEdit(self.centerMenu)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setMinimumSize(QSize(0, 40))
        self.lineEdit.setMaximumSize(QSize(16777215, 40))
        self.lineEdit.setPlaceholderText(u"Search for games....")
        self.verticalLayout_5.addWidget(self.lineEdit)

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
        self.headerLayout = QHBoxLayout()
        self.headerLayout.setSpacing(10)

        # Left side - Game count and filters
        self.leftHeaderWidget = QWidget(self.homePage)
        self.leftHeaderLayout = QHBoxLayout(self.leftHeaderWidget)
        self.leftHeaderLayout.setSpacing(15)

        # Game count label
        self.gameCountLabel = QLabel(self.leftHeaderWidget)
        self.gameCountLabel.setObjectName(u"gameCountLabel")
        self.gameCountLabel.setText(u"0 Games")
        self.gameCountLabel.setStyleSheet("""
            QLabel {
                color: #E2E8F0;
                font-size: 16px;
                font-weight: 600;
                background-color: #2C5A68;
                border-radius: 8px;
                padding: 8px 16px;
                border: 1px solid #3B82F6;
            }
        """)
        self.leftHeaderLayout.addWidget(self.gameCountLabel)

        # Filter button
        self.filterBtn = QPushButton(self.leftHeaderWidget)
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
            }
            QPushButton:hover {
                background-color: #3B82F6;
                color: white;
            }
            QPushButton:pressed {
                background-color: #2563EB;
            }
        """)
        self.leftHeaderLayout.addWidget(self.filterBtn)
        
        # Keep the filter dropdowns but hide them - they'll be used in the filter dialog
        self.genreFilter = QComboBox()
        self.genreFilter.setObjectName(u"genreFilter")
        self.genreFilter.addItems(["All Genres", "Action", "Adventure", "RPG", "Strategy", "Sports", "Racing", "Simulation"])
        
        self.platformFilter = QComboBox()
        self.platformFilter.setObjectName(u"platformFilter")
        self.platformFilter.addItems(["All Platforms", "Steam", "Epic", "GOG", "Other"])
        
        self.installFilter = QComboBox()
        self.installFilter.setObjectName(u"installFilter")
        self.installFilter.addItems(["All Games", "Installed", "Not Installed"])

        self.headerLayout.addWidget(self.leftHeaderWidget)

        # Right side - Action buttons
        self.rightHeaderWidget = QWidget(self.homePage)
        self.rightHeaderLayout = QHBoxLayout(self.rightHeaderWidget)
        self.rightHeaderLayout.setSpacing(10)

        # Action Buttons
        self.manualAddBtn = QPushButton(self.rightHeaderWidget)
        self.manualAddBtn.setObjectName(u"manualAddBtn")
        self.manualAddBtn.setMinimumSize(QSize(40, 40))
        self.manualAddBtn.setMaximumSize(QSize(40, 40))
        self.manualAddBtn.setIcon(QIcon(u"icons/plus.png"))
        self.manualAddBtn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """)
        self.rightHeaderLayout.addWidget(self.manualAddBtn)

        self.searchGames = QPushButton(self.rightHeaderWidget)
        self.searchGames.setObjectName(u"searchGames")
        self.searchGames.setText(u"Import games")
        self.searchGames.setIcon(QIcon(u"icons/import.png"))
        self.searchGames.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """)
        self.rightHeaderLayout.addWidget(self.searchGames)

        self.refreshGames = QPushButton(self.rightHeaderWidget)
        self.refreshGames.setObjectName(u"refreshGames")
        self.refreshGames.setText(u"Refresh")
        self.refreshGames.setIcon(QIcon(u"icons/refresh.png"))
        self.refreshGames.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """)
        self.rightHeaderLayout.addWidget(self.refreshGames)

        self.headerLayout.addWidget(self.rightHeaderWidget)
        self.homeLayout.addLayout(self.headerLayout)

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
        self.saveFileLayout.setSpacing(15)
        self.saveFileLayout.setContentsMargins(15, 15, 15, 15)

        # Title Label
        self.label_7 = QLabel(self.saveFileTab)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setText(u"Save Files Manager")
        self.label_7.setAlignment(Qt.AlignCenter)
        self.label_7.setStyleSheet("""
            QLabel {
                color: #E2E8F0;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
            }
        """)
        self.saveFileLayout.addWidget(self.label_7)

        # Container for main content
        self.saveFileContainer = QWidget(self.saveFileTab)
        self.saveFileContainer.setMaximumWidth(800)  # Limit maximum width
        self.saveFileContainer.setStyleSheet("""
            QWidget {
                background-color: #2C5A68;
                border: 1px solid #3B82F6;
                border-radius: 12px;
                padding: 20px;
            }
            QLabel {
                color: #E2E8F0;
                font-size: 14px;
                font-weight: bold;
            }
            QLineEdit {
                background-color: #1E293B;
                border: 1px solid #3B82F6;
                border-radius: 8px;
                padding: 8px;
                color: #E2E8F0;
                font-size: 14px;
            }
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
            QProgressBar {
                border: none;
                border-radius: 8px;
                text-align: center;
                background-color: #1E293B;
                height: 8px;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background-color: #3B82F6;
                border-radius: 8px;
            }
        """)
        
        self.saveFileContainerLayout = QVBoxLayout(self.saveFileContainer)
        self.saveFileContainerLayout.setSpacing(15)

        # Backup Folder Selection
        self.widget_12 = QWidget(self.saveFileContainer)
        self.gridLayout_4 = QHBoxLayout(self.widget_12)
        self.gridLayout_4.setSpacing(10)

        self.backup_folder_path = QLineEdit(self.widget_12)
        self.backup_folder_path.setObjectName(u"backup_folder_path")
        self.backup_folder_path.setPlaceholderText("Select backup folder...")
        self.backup_folder_path.setReadOnly(True)
        self.gridLayout_4.addWidget(self.backup_folder_path)

        self.browseBackupButton = QPushButton(self.widget_12)
        self.browseBackupButton.setObjectName(u"browseBackupButton")
        self.browseBackupButton.setText(u"Browse")
        self.browseBackupButton.setIcon(QIcon(u"icons/folder.png"))
        self.gridLayout_4.addWidget(self.browseBackupButton)

        self.saveFileContainerLayout.addWidget(self.widget_12)

        # Progress Section
        progress_container = QWidget(self.saveFileContainer)
        progress_layout = QVBoxLayout(progress_container)
        progress_layout.setSpacing(5)

        self.progressBar = QProgressBar(progress_container)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(0)
        progress_layout.addWidget(self.progressBar)

        self.statusLabel = QLabel(progress_container)
        self.statusLabel.setObjectName(u"statusLabel")
        self.statusLabel.setText(u"Press Backup button after selecting folder.")
        self.statusLabel.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.statusLabel)

        self.saveFileContainerLayout.addWidget(progress_container)

        # Backup Button
        self.backupButton = QPushButton(self.saveFileContainer)
        self.backupButton.setObjectName(u"backupButton")
        self.backupButton.setText(u"Backup Now")
        self.backupButton.setIcon(QIcon(u"icons/backup.png"))
        self.backupButton.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """)
        self.saveFileContainerLayout.addWidget(self.backupButton)

        # Center the container
        self.saveFileLayout.addWidget(self.saveFileContainer, 0, Qt.AlignCenter)
        self.saveFileLayout.addStretch()

        self.stackedWidget.addWidget(self.saveFileTab)

        # Overlay Tab
        self.overlayTab = QWidget()
        self.overlayTab.setObjectName(u"overlayTab")
        self.overlayLayout = QVBoxLayout(self.overlayTab)
        self.overlayLayout.setSpacing(15)
        self.overlayLayout.setContentsMargins(15, 15, 15, 15)

        self.overlayWidget = QWidget(self.overlayTab)
        self.overlayWidget.setObjectName(u"overlayWidget")
        self.gridLayout_2 = QGridLayout(self.overlayWidget)
        
        self.gridLayout = QGridLayout()
        self.cpu = QLabel(self.overlayWidget)
        self.cpu.setObjectName(u"cpu")
        self.cpu.setText(u"TextLabel")
        self.gridLayout.addWidget(self.cpu, 0, 0, 1, 1)

        self.fps = QLabel(self.overlayWidget)
        self.fps.setObjectName(u"fps")
        self.fps.setText(u"TextLabel")
        self.gridLayout.addWidget(self.fps, 0, 2, 1, 1)

        self.ram = QLabel(self.overlayWidget)
        self.ram.setObjectName(u"ram")
        self.ram.setText(u"TextLabel")
        self.gridLayout.addWidget(self.ram, 0, 1, 1, 1)

        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.overlayLayout.addWidget(self.overlayWidget)

        self.toggleOverlay = QPushButton(self.overlayTab)
        self.toggleOverlay.setObjectName(u"toggleOverlay")
        self.toggleOverlay.setText(u"Toggle Overlay On/Off")
        self.overlayLayout.addWidget(self.toggleOverlay)
        self.overlayLayout.addStretch()

        self.stackedWidget.addWidget(self.overlayTab)

        # Optimization Tab
        self.optimizationTab = QWidget()
        self.optimizationTab.setObjectName(u"optimizationTab")
        self.optimizationLayout = QVBoxLayout(self.optimizationTab)
        self.optimizationLayout.setSpacing(15)
        self.optimizationLayout.setContentsMargins(15, 15, 15, 15)

        # Title Label
        self.label_2 = QLabel(self.optimizationTab)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setText(u"System Information")
        self.label_2.setAlignment(Qt.AlignCenter)
        self.label_2.setStyleSheet("""
            QLabel {
                color: #E2E8F0;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
            }
        """)
        self.optimizationLayout.addWidget(self.label_2)

        # Container for main content
        self.optimizationContainer = QWidget(self.optimizationTab)
        self.optimizationContainer.setMaximumWidth(800)  # Limit maximum width
        self.optimizationContainer.setStyleSheet("""
            QFrame {
                background-color: #2C5A68;
                border: 1px solid #3B82F6;
                border-radius: 12px;
                padding: 20px;
            }
            QLabel {
                color: #E2E8F0;
                font-size: 14px;
                font-weight: bold;
            }
            QLabel[value="true"] {
                color: #3B82F6;
                font-size: 18px;
                font-weight: bold;
                background-color: #1E293B;
                border: 1px solid #3B82F6;
                border-radius: 8px;
                padding: 8px;
                min-width: 100px;
            }
        """)
        
        self.optimizationContainerLayout = QVBoxLayout(self.optimizationContainer)
        self.optimizationContainerLayout.setSpacing(20)

        # System Info Layout
        self.widget_4 = QWidget(self.optimizationContainer)
        self.widget_4.setObjectName(u"widget_4")
        self.horizontalLayout_5 = QHBoxLayout(self.widget_4)
        self.horizontalLayout_5.setSpacing(20)

        # Labels Column
        self.labelsWidget = QWidget(self.widget_4)
        self.labelsLayout = QVBoxLayout(self.labelsWidget)
        self.labelsLayout.setSpacing(20)

        # CPU Label and Value
        cpu_container = QWidget()
        cpu_layout = QHBoxLayout(cpu_container)
        cpu_layout.setSpacing(10)
        cpu_label = QLabel("CPU Usage:")
        self.cpuLabel = QLabel("0%")
        self.cpuLabel.setProperty("value", True)
        cpu_layout.addWidget(cpu_label)
        cpu_layout.addWidget(self.cpuLabel)
        self.labelsLayout.addWidget(cpu_container)

        # RAM Label and Value
        ram_container = QWidget()
        ram_layout = QHBoxLayout(ram_container)
        ram_layout.setSpacing(10)
        ram_label = QLabel("RAM Usage:")
        self.ramLabel = QLabel("0%")
        self.ramLabel.setProperty("value", True)
        ram_layout.addWidget(ram_label)
        ram_layout.addWidget(self.ramLabel)
        self.labelsLayout.addWidget(ram_container)

        # Disk Label and Value
        disk_container = QWidget()
        disk_layout = QHBoxLayout(disk_container)
        disk_layout.setSpacing(10)
        disk_label = QLabel("Disk Usage:")
        self.diskLabel = QLabel("0 MB/s")
        self.diskLabel.setProperty("value", True)
        disk_layout.addWidget(disk_label)
        disk_layout.addWidget(self.diskLabel)
        self.labelsLayout.addWidget(disk_container)

        self.horizontalLayout_5.addWidget(self.labelsWidget)

        # Optimize Button
        self.optimizeNowBtn = QPushButton(self.widget_4)
        self.optimizeNowBtn.setObjectName(u"optimizeNowBtn")
        self.optimizeNowBtn.setText(u"Optimize Now")
        self.optimizeNowBtn.setIcon(QIcon(u"icons/optimizenow.png"))
        self.optimizeNowBtn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """)
        self.horizontalLayout_5.addWidget(self.optimizeNowBtn)

        self.optimizationContainerLayout.addWidget(self.widget_4)

        # Center the container
        self.optimizationLayout.addWidget(self.optimizationContainer, 0, Qt.AlignCenter)

        # Description Label
        self.label_4 = QLabel(self.optimizationTab)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setText(u"The optimize now button will delete temporary files.")
        self.label_4.setAlignment(Qt.AlignCenter)
        self.label_4.setStyleSheet("""
            QLabel {
                color: #94A3B8;
                font-size: 12px;
            }
        """)
        self.optimizationLayout.addWidget(self.label_4)
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
        self.cpu.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.fps.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.ram.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.toggleOverlay.setText(QCoreApplication.translate("MainWindow", u"Toggle Overlay On/Off", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"System Information", None))
        self.optimizeNowBtn.setText(QCoreApplication.translate("MainWindow", u"Optimize Now", None))
    # retranslateUi

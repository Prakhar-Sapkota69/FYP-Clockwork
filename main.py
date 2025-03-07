import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QPushButton, QStackedWidget, QWidget, QLabel, QLCDNumber, QGridLayout
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QTimer
from game_search import search_local_games
from system_optimizer import SystemOptimizer  # Import the new SystemOptimizer class
from overlay import OverlayWindow  # Import the OverlayWindow class
from save_file import SaveFileManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.load_ui()

        # Initialize the timer after loading the UI
        self.timer = QTimer(self)  # Create the timer instance here
        self.timer.timeout.connect(self.update_system_usage)

        # Create an instance of the OverlayWindow
        self.overlay_window = OverlayWindow()
        self.save_file_manager = SaveFileManager(self.ui)

        self.ui.browseBackupButton.clicked.connect(self.save_file_manager.browse_backup_folder)
        self.ui.backupButton.clicked.connect(self.save_file_manager.backup_save_files)

        self.ui.progressBar.setStyleSheet("""
    QProgressBar {
        border: 2px solid #333333;
        border-radius: 10px;
        background-color: #f0f0f0;
        text-align: center;
        color: #ffffff;  /* Text color */
        font-size: 14px;  /* Font size */
        font-weight: bold;  /* Bold text */
    }

    QProgressBar::chunk {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #FF5733, stop:1 #C70039);
        border-radius: 10px;
        width: 10px;  /* Width of each chunk */
    }
""")

    def load_ui(self):
        # Load the .ui file
        ui_file = QFile("interface.ui")  # Path to your .ui file
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        if self.ui is not None:
            self.ui.show()

        # Set the first page (homepage) of the stacked widget as the current page
        self.stacked_widget = self.ui.findChild(QStackedWidget, "stackedWidget")  
        if self.stacked_widget:
            self.stacked_widget.setCurrentIndex(0)  # Set the first page (home page) as the default page

        # Connect the "Library" button to switch to the homepage
        self.library_button = self.ui.findChild(QPushButton, "libraryBtn")  
        if self.library_button:
            self.library_button.clicked.connect(self.show_homepage)

        # Connect the "searchGames" button inside the homepage to trigger game search
        self.search_games_button = self.ui.findChild(QPushButton, "searchGames")
        if self.search_games_button:
            self.search_games_button.clicked.connect(self.ask_for_game_search)

        # Connect the "Optimization" button to switch to the optimization tab
        self.optimization_button = self.ui.findChild(QPushButton, "optimizationBtn")  
        if self.optimization_button:
            self.optimization_button.clicked.connect(self.show_optimization_tab)

        # Connect the "Overlay" button to switch to the overlay tab
        self.overlay_button = self.ui.findChild(QPushButton, "overlayBtn")  # Sidebar Overlay button
        if self.overlay_button:
            self.overlay_button.clicked.connect(self.show_overlay_tab)

        # Connect the "Toggle Overlay" button inside the overlay tab
        self.toggle_overlay_button = self.ui.findChild(QPushButton, "toggleOverlay")  # Inside overlayTab
        if self.toggle_overlay_button:
            self.toggle_overlay_button.clicked.connect(self.toggle_overlay)

        # Connect the "Optimize Now" button to the optimize_pc function
        self.optimize_now_button = self.ui.findChild(QPushButton, "optimizeNowBtn")
        if self.optimize_now_button:
            self.optimize_now_button.clicked.connect(self.optimize_pc)

        # Connect the "Save Files" button to switch to the save file tab
        self.savefile_button = self.ui.findChild(QPushButton, "savefileBtn")
        if self.savefile_button:
            self.savefile_button.clicked.connect(self.show_savefile_tab)

        # Find the QLCDNumber widgets for CPU, RAM, and Disk usage
        self.cpu_lcd = self.ui.findChild(QLCDNumber, "cpuLcd")
        self.ram_lcd = self.ui.findChild(QLCDNumber, "ramLcd")
        self.disk_lcd = self.ui.findChild(QLCDNumber, "diskLcd")

        # Customize the QLCDNumber widgets
        for lcd in [self.cpu_lcd, self.ram_lcd, self.disk_lcd]:
            if lcd:
                lcd.setDigitCount(4)  # Display up to 4 digits (e.g., 12.3)
                lcd.setSegmentStyle(QLCDNumber.Filled)  # Use filled segments
                lcd.setSmallDecimalPoint(True)  # Enable small decimal point

    def show_savefile_tab(self):
        """Switch to the saveFileTab in the stacked widget."""
        savefile_tab = self.ui.findChild(QWidget, "saveFileTab")
        if savefile_tab:
            savefile_tab_index = self.stacked_widget.indexOf(savefile_tab)
            if savefile_tab_index != -1:
                self.stacked_widget.setCurrentIndex(savefile_tab_index)

    def show_overlay_tab(self):
        """Switch to the overlayTab in the stacked widget."""
        overlay_tab = self.ui.findChild(QWidget, "overlayTab")
        if overlay_tab:
            overlay_tab_index = self.stacked_widget.indexOf(overlay_tab)
            if overlay_tab_index != -1:
                self.stacked_widget.setCurrentIndex(overlay_tab_index)

    def toggle_overlay(self):
        """Show or hide the overlay window."""
        if self.overlay_window.isVisible():
            self.overlay_window.hide_overlay()  # Hide the overlay
        else:
            self.overlay_window.show_overlay()  # Show the overlay

    def ask_for_game_search(self):
        print("ask_for_game_search triggered.")  # Debugging line
        # Prompt the user if they want to search for games
        reply = QMessageBox.question(self, 'Game Search', 'Do you want to search for games on your system?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.search_for_games()

    def search_for_games(self):
        print("search_for_games triggered.")  # Debugging line
        # Use the imported function to search for games
        found_games = search_local_games()

        # Show the results to the user
        self.show_games(found_games)

    def show_games(self, games):
        print("show_games triggered.")  # Debugging line
        # Find the gameGridWidget and gameDisplayGrid layout
        game_grid_widget = self.ui.findChild(QWidget, "gameGridWidget")
        game_display_grid = self.ui.findChild(QGridLayout, "gameDisplayGrid")

        if game_grid_widget and game_display_grid:
            # Clear any existing widgets in the layout before adding new ones
            for i in range(game_display_grid.count()):
                item = game_display_grid.itemAt(i)
                if item:
                    widget = item.widget()
                    if widget:
                        widget.deleteLater()  # Remove old widgets from layout

            # Add new game entries to the grid layout
            row, col = 0, 0
            for game in games:
                game_label = QLabel(game)  # Create a label for each game
                game_display_grid.addWidget(game_label, row, col)  # Add the label to the grid layout

                # Move to the next column, and start a new row if needed
                col += 1
                if col > 2:  # Change 3 to the number of columns you want
                    col = 0
                    row += 1

            # Show the game grid widget (if it's not already visible)
            game_grid_widget.setVisible(True)
        else:
            QMessageBox.information(self, 'No Game Grid', "Game grid widget or layout not found.")

    def show_optimization_tab(self):
        print("Showing optimization tab...")  # Debugging line
        # Find the "optimizationTab" page inside the stacked widget
        optimization_tab = self.ui.findChild(QWidget, "optimizationTab")  # Get the "optimizationTab" widget by object name
        if optimization_tab:
            optimization_tab_index = self.stacked_widget.indexOf(optimization_tab)
            if optimization_tab_index != -1:
                self.stacked_widget.setCurrentIndex(optimization_tab_index)

            # Start the timer to update system usage every second
            self.timer.start(1000)  # 1000 milliseconds = 1 second
            print("Timer started.")  # Debugging line

    def update_system_usage(self):
        print("Updating system usage...")  # Debugging line
        # Use the SystemOptimizer class to get system usage
        cpu_usage, ram_usage, disk_usage = SystemOptimizer.get_system_usage()

        # Update the QLCDNumber widgets for CPU, RAM, and Disk usage
        if self.cpu_lcd:
            self.cpu_lcd.display(f"{cpu_usage:.1f}")  # Display CPU usage with 1 decimal place
        if self.ram_lcd:
            self.ram_lcd.display(f"{ram_usage:.1f}")  # Display RAM usage with 1 decimal place
        if self.disk_lcd:
            self.disk_lcd.display(f"{disk_usage:.1f}")  # Display disk usage with 1 decimal place

    def show_homepage(self):
        # Switch to the homepage (first page) when the Library button is pressed
        print("show_homepage triggered.")  # Debugging line
        self.stacked_widget.setCurrentIndex(0)  # Set to the first page (home page)

        # Stop the timer when leaving the optimization tab
        self.timer.stop()

    def optimize_pc(self):
        print("Optimize Now button clicked.")  # Debugging line
        # Use the SystemOptimizer class to delete temporary files
        deleted_files = SystemOptimizer.optimize_pc()
        
        # Get the unnecessary processes
        processes = SystemOptimizer.get_unnecessary_processes()
        
        # Automatically close the unnecessary processes
        SystemOptimizer.close_unnecessary_processes()

        # Show a message box with the results
        QMessageBox.information(self, 'Optimization Complete', f"Deleted {deleted_files} temporary files.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
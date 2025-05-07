import sys
import subprocess
from PySide6.QtWidgets import QApplication, QPushButton, QFileDialog, QVBoxLayout, QWidget, QMessageBox

class ManualAddGame(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Create the button
        self.manualAddBtn = QPushButton('Add Game Manually', self)
        self.manualAddBtn.setObjectName("manualAddBtn")  # Set the object name
        self.manualAddBtn.clicked.connect(self.browseGameExecutable)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.manualAddBtn)
        self.setLayout(layout)

        # Store the game executable path
        self.game_executable_path = None

    def browseGameExecutable(self):
        # Open a file dialog to browse for the game executable
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Game Executable", "", "Executable Files (*.exe);;All Files (*)", options=options)
        
        if file_path:
            self.game_executable_path = file_path
            QMessageBox.information(self, "Success", f"Game executable selected: {file_path}")
            # Optionally, you can add logic to launch the game immediately or store the path for later use
            self.launchGame()

    def launchGame(self):
        if self.game_executable_path:
            try:
                # Launch the game using subprocess
                subprocess.Popen([self.game_executable_path])
                QMessageBox.information(self, "Success", "Game launched successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to launch game: {e}")
        else:
            QMessageBox.warning(self, "Warning", "No game executable selected!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ManualAddGame()
    window.show()
    sys.exit(app.exec_())
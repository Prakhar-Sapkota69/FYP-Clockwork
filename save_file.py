# save_file.py
import os
import subprocess
from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtCore import QTimer

class SaveFileManager:
    def __init__(self, ui):
        self.ui = ui
        self.backup_folder = None
        self.ludusavi_path = os.path.join("tools", "ludusavi.exe")  # Path to Ludusavi
        self.timer = QTimer()  # Timer for simulating progress
        self.progress_value = 0  # Current progress value

    def browse_backup_folder(self):
        """Browse for the backup folder."""
        backup_folder = QFileDialog.getExistingDirectory(self.ui, "Select Backup Folder")
        if backup_folder:
            self.ui.backupPathLineEdit.setText(backup_folder)
            self.backup_folder = backup_folder

    def backup_save_files(self):
        """Backup save files using Ludusavi."""
        if not self.backup_folder:
            QMessageBox.warning(self.ui, "Error", "No backup folder selected.")
            return

        # Reset progress bar
        self.ui.progressBar.setValue(0)
        self.progress_value = 0

        # Start the backup process
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(100)  # Update progress every 100ms

        try:
            # Call Ludusavi to back up save files (use --force to skip confirmation)
            result = subprocess.run(
                [self.ludusavi_path, "backup", "--path", self.backup_folder, "--force"],
                capture_output=True,
                text=True,
            )

            # Stop the timer and set progress to 100% when done
            self.timer.stop()
            self.ui.progressBar.setValue(100)

            if result.returncode == 0:
                # Backup successful
                self.ui.statusLabel.setText("Backup successful!")
                QMessageBox.information(self.ui, "Success", "Save files backed up successfully.")
            else:
                # Backup failed
                self.ui.statusLabel.setText("Backup failed.")
                QMessageBox.critical(self.ui, "Error", f"Backup failed: {result.stderr}")
        except Exception as e:
            self.timer.stop()
            self.ui.statusLabel.setText("Backup failed.")
            QMessageBox.critical(self.ui, "Error", f"Backup failed: {str(e)}")

    def update_progress(self):
        """Simulate progress by incrementing the progress bar."""
        if self.progress_value < 100:
            self.progress_value += 1  # Increment progress
            self.ui.progressBar.setValue(self.progress_value)
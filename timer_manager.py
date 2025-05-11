from PySide6.QtCore import QTimer, QObject
from PySide6.QtWidgets import QMainWindow

class TimerManager(QObject):
    def __init__(self, main_window: QMainWindow):
        super().__init__()
        self.main_window = main_window
        
        # Initialize timers
        self.system_timer = QTimer(main_window)
        self.system_timer.timeout.connect(self.main_window.update_system_usage)
        self.system_timer.setInterval(1000)

        self.fps_timer = QTimer(main_window)
        self.fps_timer.timeout.connect(self.main_window.update_fps)
        self.fps_timer.setInterval(1000)

        self.game_status_timer = QTimer(main_window)
        self.game_status_timer.timeout.connect(self.main_window.update_game_statuses)
        self.game_status_timer.setInterval(5000)  # Check game status every 5 seconds

    def start_system_timer(self):
        """Start the system usage timer"""
        self.system_timer.start(1000)

    def stop_system_timer(self):
        """Stop the system usage timer"""
        self.system_timer.stop()

    def start_fps_timer(self):
        """Start the FPS monitoring timer"""
        self.fps_timer.start(1000)

    def stop_fps_timer(self):
        """Stop the FPS monitoring timer"""
        self.fps_timer.stop()

    def start_game_status_timer(self):
        """Start the game status monitoring timer"""
        self.game_status_timer.start(5000)

    def stop_game_status_timer(self):
        """Stop the game status monitoring timer"""
        self.game_status_timer.stop()

    def stop_all_timers(self):
        """Stop all timers"""
        self.stop_system_timer()
        self.stop_fps_timer()
        self.stop_game_status_timer() 
import os
import subprocess
import psutil
from typing import Optional
from models import Game
from database import DatabaseManager

class GameManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        
    def launch_game(self, game_id: int) -> Optional[psutil.Process]:
        """Launch a game and return its process."""
        try:
            # Get game data from database
            game = self.db_manager.get_game_by_id(game_id)
            if not game:
                print(f"Game with ID {game_id} not found")
                return None
                
            # Check if game is installed
            if not game.is_installed:
                print(f"Game {game.name} is not installed")
                return None
                
            # Launch based on game type
            if game.type == 'steam':
                # Use os.startfile for Steam URLs
                os.startfile(game.launch_command)
                return None
            else:
                # For regular executables
                if game.install_path and os.path.exists(game.install_path):
                    process = subprocess.Popen(
                        game.launch_command,
                        cwd=os.path.dirname(game.install_path),
                        shell=True
                    )
                    return psutil.Process(process.pid)
                else:
                    raise Exception(f"Installation path not found: {game.install_path}")
                    
        except Exception as e:
            print(f"Error launching game: {e}")
            raise
            
    def check_game_running(self, process: Optional[psutil.Process]) -> bool:
        """Check if a game process is still running."""
        if process is None:
            # For Steam/Epic games, we can't track the process
            return True
            
        try:
            return process.is_running()
        except psutil.NoSuchProcess:
            return False
        except Exception as e:
            print(f"Error checking game process: {e}")
            return False 
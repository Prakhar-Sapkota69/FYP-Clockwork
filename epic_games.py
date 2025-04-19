import os
import json
import winreg
from typing import List, Optional
from models import Game

class EpicGamesManager:
    def __init__(self):
        self.epic_path = self._get_epic_path()
        
    def _get_epic_path(self) -> Optional[str]:
        """Get the Epic Games Launcher installation path from registry."""
        try:
            # Try different registry paths
            registry_paths = [
                r"SOFTWARE\WOW6432Node\Epic Games, Inc\EpicGamesLauncher",
                r"SOFTWARE\Epic Games, Inc\EpicGamesLauncher",
                r"SOFTWARE\Epic Games\EpicGamesLauncher"
            ]
            
            for path in registry_paths:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
                    epic_path = winreg.QueryValueEx(key, "AppPath")[0]
                    winreg.CloseKey(key)
                    return os.path.dirname(epic_path)
                except WindowsError:
                    continue
                    
            # If not found in HKEY_LOCAL_MACHINE, try HKEY_CURRENT_USER
            for path in registry_paths:
                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path)
                    epic_path = winreg.QueryValueEx(key, "AppPath")[0]
                    winreg.CloseKey(key)
                    return os.path.dirname(epic_path)
                except WindowsError:
                    continue
                    
            print("Epic Games Launcher not found in registry")
            return None
            
        except Exception as e:
            print(f"Error getting Epic Games path: {e}")
            return None
            
    def get_installed_games(self) -> List[Game]:
        """Get list of installed Epic Games Store games."""
        if not self.epic_path:
            return []
            
        try:
            games = []
            manifest_path = os.path.join(self.epic_path, "Data", "Manifests")
            
            if not os.path.exists(manifest_path):
                return []
                
            for manifest_file in os.listdir(manifest_path):
                if manifest_file.endswith('.item'):
                    try:
                        with open(os.path.join(manifest_path, manifest_file), 'r') as f:
                            manifest_data = json.load(f)
                            
                        game = Game(
                            name=manifest_data.get('AppName', 'Unknown'),
                            type='epic',
                            epic_app_id=manifest_data.get('AppId'),
                            epic_launch_command=f"epic://launch/{manifest_data.get('AppId')}",
                            install_path=manifest_data.get('InstallLocation'),
                            is_installed=True,
                            metadata_fetched=False
                        )
                        games.append(game)
                    except Exception as e:
                        print(f"Error reading manifest {manifest_file}: {e}")
                        continue
                        
            return games
        except Exception as e:
            print(f"Error getting Epic Games: {e}")
            return []
            
    def launch_game(self, game: Game) -> bool:
        """Launch an Epic Games Store game."""
        try:
            if not game.epic_launch_command:
                return False
                
            os.startfile(game.epic_launch_command)
            return True
        except Exception as e:
            print(f"Error launching Epic game {game.name}: {e}")
            return False 
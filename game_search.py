import os
import sys
import subprocess
import requests
import winreg
from PySide6.QtWidgets import QApplication, QPushButton, QFileDialog, QVBoxLayout, QWidget, QMessageBox, QDialog, QLabel, QLineEdit, QHBoxLayout
from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile
from urllib.parse import urlencode
import json
import vdf  # for reading Steam config files
from pathlib import Path
import re
from models import Game

STEAM_API_KEY_FILE = "steam_api_key.txt"
STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"

def read_steam_api_key():
    """Read Steam API key from file"""
    try:
        api_key_path = Path("steam_api_key.txt")
        if api_key_path.exists():
            with open(api_key_path, 'r') as f:
                return f.read().strip()
        else:
            print("Error: steam_api_key.txt file not found")
            return None
    except Exception as e:
        print(f"Error reading Steam API key: {e}")
        return None

# Get Steam API key from file
STEAM_API_KEY = read_steam_api_key()

def get_steam_path():
    """Get Steam installation path from Windows registry."""
    try:
        hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\WOW6432Node\\Valve\\Steam")
        steam_path = winreg.QueryValueEx(hkey, "InstallPath")[0]
        winreg.CloseKey(hkey)
        return steam_path
    except WindowsError:
        try:
            hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Valve\\Steam")
            steam_path = winreg.QueryValueEx(hkey, "InstallPath")[0]
            winreg.CloseKey(hkey)
            return steam_path
        except WindowsError:
            return None

def get_steam_id():
    """Get Steam ID from registry and convert to Steam64 ID"""
    try:
        # Try to get Steam ID from registry
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam\ActiveProcess")
        steam_id = winreg.QueryValueEx(key, "ActiveUser")[0]
        winreg.CloseKey(key)
        
        # Convert to Steam64 ID
        if steam_id > 0:
            steam64_id = steam_id + 76561197960265728  # Convert to Steam64 ID
            print(f"Converting Steam ID {steam_id} to Steam64 ID: {steam64_id}")
            return steam64_id
        else:
            print("Error: Invalid Steam ID from registry")
            return None
    except Exception as e:
        print(f"Error getting Steam ID: {e}")
        return None

# Get Steam ID at startup
STEAM_ID = get_steam_id()

def get_steam_games():
    """Get list of games from Steam library"""
    try:
        if not STEAM_API_KEY:
            print("Error: Steam API key not found")
            return []
            
        if not STEAM_ID:
            print("Error: Steam ID not found")
            return []
            
        print(f"Using Steam ID: {STEAM_ID}")
        print(f"Using API Key: {STEAM_API_KEY[:5]}...")  # Only show first 5 chars for security
            
        # Get owned games from Steam API
        url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={STEAM_API_KEY}&steamid={STEAM_ID}&include_appinfo=true&include_played_free_games=true"
        print(f"Fetching games from URL: {url}")
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Steam API response status: {data.get('response', {}).get('game_count', 0)} games found")
            
            if 'response' in data and 'games' in data['response']:
                games = []
                for game_data in data['response']['games']:
                    app_id = str(game_data.get('appid'))
                    if not app_id:
                        print(f"Warning: Game {game_data.get('name')} has no appid")
                        continue
                        
                    game = Game(
                        name=game_data.get('name', 'Unknown'),
                        type='steam',
                        app_id=app_id,
                        launch_command=f"steam://rungameid/{app_id}",
                        genre=None,  # Will be fetched by metadata
                        is_installed=True,
                        playtime=game_data.get('playtime_forever', 0),
                        metadata_fetched=False
                    )
                    games.append(game)
                    print(f"Added game: {game.name} (AppID: {game.app_id})")
                
                print(f"Found {len(games)} games with valid appids")
                return games
            else:
                print("No games found in response")
                print(f"Response data: {data}")
        else:
            print(f"Error getting Steam games: {response.status_code}")
            print(f"Response text: {response.text}")
        return []
    except Exception as e:
        print(f"Error getting Steam games: {e}")
        import traceback
        traceback.print_exc()
        return []

def search_local_games():
    """Search for locally installed games"""
    try:
        # Get Steam installation path from registry
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
        steam_path = winreg.QueryValueEx(key, "SteamExe")[0]
        steam_path = os.path.dirname(steam_path)
        winreg.CloseKey(key)
        
        # Get library folders
        library_folders_file = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
        if not os.path.exists(library_folders_file):
            return []
            
        with open(library_folders_file, 'r') as f:
            content = f.read()
            
        # Extract library paths
        library_paths = []
        for line in content.split('\n'):
            if '"path"' in line:
                path = line.split('"')[3].replace('\\\\', '\\')
                library_paths.append(path)
                
        games = []
        for library_path in library_paths:
            apps_path = os.path.join(library_path, "steamapps")
            if not os.path.exists(apps_path):
                continue
                
            # Get installed games
            for item in os.listdir(apps_path):
                if item.startswith("appmanifest_") and item.endswith(".acf"):
                    try:
                        with open(os.path.join(apps_path, item), 'r') as f:
                            manifest = f.read()
                            
                        # Extract game info
                        name_match = re.search(r'"name"\s+"([^"]+)"', manifest)
                        appid_match = re.search(r'"appid"\s+"(\d+)"', manifest)
                        
                        if name_match and appid_match:
                            game = Game(
                                name=name_match.group(1),
                                type='steam',
                                app_id=appid_match.group(1),
                                install_path=os.path.join(apps_path, "common", name_match.group(1)),
                                is_installed=True,
                                metadata_fetched=False
                            )
                            games.append(game)
                    except Exception as e:
                        print(f"Error reading manifest {item}: {e}")
                        continue
                        
        return games
    except Exception as e:
        print(f"Error searching local games: {e}")
        return []

class ManualAddGame(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Game Manually")
        self.setFixedWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Game name input
        name_label = QLabel("Game Name:")
        self.name_input = QLineEdit()
        layout.addWidget(name_label)
        layout.addWidget(self.name_input)
        
        # Game path input
        path_label = QLabel("Game Executable:")
        self.path_input = QLineEdit()
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_file)
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(browse_btn)
        layout.addWidget(path_label)
        layout.addLayout(path_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Game Executable", "", "Executable Files (*.exe);;All Files (*)"
        )
        if file_path:
            self.path_input.setText(file_path)
            
    def get_game_data(self):
        return Game(
            name=self.name_input.text(),
            type='manual',
            install_path=self.path_input.text(),
            launch_command=self.path_input.text(),
            is_installed=True,
            metadata_fetched=False
        )

class SteamAuthWebPage(QWebEnginePage):
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        self.parent = parent
        
        # Accept all certificates (only for Steam's domain)
        self.certificateError.connect(self.handleCertificateError)

    def handleCertificateError(self, error):
        if "steamcommunity.com" in error.url().toString():
            error.acceptCertificate()
            return True
        return False

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        url_string = url.toString()
        print(f"Navigation request to: {url_string}")  # Debug print
        
        # Handle the Steam login response
        if "/openid/login" in url_string and "openid.claimed_id" in url_string:
            self.parent.handle_auth_callback(url)
            return False
            
        # Allow navigation to Steam domains
        if "steamcommunity.com" in url_string:
            return True
            
        return True 
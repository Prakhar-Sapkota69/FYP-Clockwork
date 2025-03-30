from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import os
import json
import re
import winreg

@dataclass
class Game:
    """Represents a game in the library."""
    id: Optional[int] = None
    name: str = ""
    type: str = ""  # steam, epic, etc.
    app_id: Optional[str] = None
    install_path: Optional[str] = None
    launch_command: Optional[str] = None
    genre: Optional[str] = None
    is_installed: bool = False
    playtime: int = 0
    metadata_fetched: bool = False
    poster_url: Optional[str] = None
    background_url: Optional[str] = None
    release_date: Optional[str] = None
    description: Optional[str] = None
    rating: float = 0.0
    platforms: List[str] = None
    developers: List[str] = None
    publishers: List[str] = None
    metacritic: int = 0
    esrb_rating: str = "Not Rated"
    epic_app_id: Optional[str] = None  # For Epic Games Store
    epic_launch_command: Optional[str] = None  # For Epic Games Store
    last_launched: Optional[datetime] = None  # For tracking when the game was last launched

    def __post_init__(self):
        """Initialize lists if they are None and extract app_id if possible."""
        if self.platforms is None:
            self.platforms = []
        if self.developers is None:
            self.developers = []
        if self.publishers is None:
            self.publishers = []
        
        # Try to extract app_id from launch command if not set
        self.extract_app_id_from_launch_command()
            
        # Check if game is installed
        self.check_installation_status()

    def check_installation_status(self):
        """Check if the game is installed."""
        try:
            if self.type == 'steam':
                # Get Steam installation path from registry
                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
                    steam_path = winreg.QueryValueEx(key, "SteamPath")[0]
                except:
                    try:
                        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\Valve\Steam")
                        steam_path = winreg.QueryValueEx(key, "SteamPath")[0]
                    except:
                        self.is_installed = False
                        return
                
                # Read libraryfolders.vdf to get all library paths
                vdf_path = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
                if not os.path.exists(vdf_path):
                    self.is_installed = False
                    return
                
                with open(vdf_path, 'r', encoding='utf-8') as f:
                    vdf_content = f.read()
                
                # Extract library paths using regex
                library_paths = re.findall(r'"path"\s+"([^"]+)"', vdf_content)
                library_folders = [steam_path] + library_paths
                
                # Check each library folder for the game's manifest
                for library in library_folders:
                    manifest_path = os.path.join(library, "steamapps", f"appmanifest_{self.app_id}.acf")
                    if os.path.exists(manifest_path):
                        # Read manifest to check if game is fully installed
                        with open(manifest_path, 'r', encoding='utf-8') as f:
                            manifest_data = f.read()
                        
                        # Check StateFlags (4 = fully installed)
                        state_flags = re.search(r'"StateFlags"\s+"(\d+)"', manifest_data)
                        if state_flags and state_flags.group(1) == "4":
                            self.is_installed = True
                            return
                
                self.is_installed = False
                
            elif self.type == 'epic':
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Epic Games\EpicGamesLauncher")
                    epic_path = winreg.QueryValueEx(key, "AppDataPath")[0]
                except:
                    try:
                        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Epic Games\EpicGamesLauncher")
                        epic_path = winreg.QueryValueEx(key, "AppDataPath")[0]
                    except:
                        self.is_installed = False
                        return
                
                # Check for game manifest
                manifest_path = os.path.join(epic_path, "Data", "Manifests", f"{self.app_id}.item")
                if os.path.exists(manifest_path):
                    with open(manifest_path, 'r', encoding='utf-8') as f:
                        manifest_data = json.load(f)
                    
                    # Check if installation location exists
                    install_location = manifest_data.get('InstallLocation', '')
                    if install_location and os.path.exists(install_location):
                        self.is_installed = True
                        return
                
                self.is_installed = False
                
        except Exception as e:
            self.is_installed = False

    def extract_app_id_from_launch_command(self) -> Optional[str]:
        """Extract app_id from launch command if possible."""
        try:
            if self.launch_command:
                if 'steam://rungameid/' in self.launch_command:
                    app_id = self.launch_command.split('steam://rungameid/')[-1].strip()
                    app_id = ''.join(filter(str.isdigit, app_id))
                    if app_id:
                        self.app_id = app_id
                        return app_id
                elif 'epic://launch/' in self.launch_command:
                    app_id = self.launch_command.split('epic://launch/')[-1].strip()
                    if app_id:
                        self.epic_app_id = app_id
                        return app_id
        except Exception as e:
            pass
        return None

    def update_metadata(self, metadata: Dict) -> None:
        """Update game metadata from a dictionary of metadata values."""
        try:
            # Update basic metadata fields
            for field in ['name', 'genre', 'poster_url', 'description', 'release_date',
                         'rating', 'metacritic', 'esrb_rating']:
                if field in metadata:
                    setattr(self, field, metadata[field])

            # Update list fields
            for field in ['platforms', 'developers', 'publishers']:
                if field in metadata:
                    value = metadata[field]
                    if isinstance(value, str):
                        value = [v.strip() for v in value.split(',') if v.strip()]
                    elif isinstance(value, list):
                        value = [str(v).strip() for v in value if str(v).strip()]
                    setattr(self, field, value)

            # Mark metadata as fetched
            self.metadata_fetched = True

        except Exception as e:
            pass

    def to_dict(self) -> dict:
        """Convert the game to a dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'app_id': self.app_id,
            'install_path': self.install_path,
            'launch_command': self.launch_command,
            'genre': self.genre,
            'is_installed': self.is_installed,
            'playtime': self.playtime,
            'metadata_fetched': self.metadata_fetched,
            'poster_url': self.poster_url,
            'background_url': self.background_url,
            'release_date': self.release_date,
            'description': self.description,
            'rating': self.rating,
            'platforms': self.platforms,
            'developers': self.developers,
            'publishers': self.publishers,
            'metacritic': self.metacritic,
            'esrb_rating': self.esrb_rating
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Game':
        """Create a Game instance from a dictionary."""
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            type=data.get('type', ''),
            app_id=data.get('app_id'),
            install_path=data.get('install_path'),
            launch_command=data.get('launch_command'),
            genre=data.get('genre'),
            is_installed=data.get('is_installed', False),
            playtime=data.get('playtime', 0),
            metadata_fetched=data.get('metadata_fetched', False),
            poster_url=data.get('poster_url'),
            background_url=data.get('background_url'),
            release_date=data.get('release_date'),
            description=data.get('description'),
            rating=data.get('rating', 0.0),
            platforms=data.get('platforms', []),
            developers=data.get('developers', []),
            publishers=data.get('publishers', []),
            metacritic=data.get('metacritic', 0),
            esrb_rating=data.get('esrb_rating', 'Not Rated'),
            epic_app_id=data.get('epic_app_id'),
            epic_launch_command=data.get('epic_launch_command'),
            last_launched=data.get('last_launched')
        )

    def update_from_dict(self, data: dict) -> None:
        """Update the game's attributes from a dictionary."""
        for key, value in data.items():
            if hasattr(self, key):
                if key in ['platforms', 'developers', 'publishers'] and isinstance(value, str):
                    value = [v.strip() for v in value.split(',') if v.strip()]
                setattr(self, key, value)

    def __str__(self) -> str:
        """Return a string representation of the game."""
        return f"Game(name='{self.name}', type='{self.type}', app_id='{self.app_id}')"

    def __repr__(self) -> str:
        """Return a detailed string representation of the game."""
        return f"Game(id={self.id}, name='{self.name}', type='{self.type}', app_id='{self.app_id}', " \
               f"genre='{self.genre}', is_installed={self.is_installed}, playtime={self.playtime}, " \
               f"metadata_fetched={self.metadata_fetched})" 
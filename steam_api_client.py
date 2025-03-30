"""
Steam API Client
A dedicated module to fetch data directly from Steam API
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any

class SteamAPIClient:
    def __init__(self, api_key: str, steam_id: str):
        self.api_key = api_key
        self.steam_id = steam_id
        self.session = None
        
    async def ensure_session(self):
        """Ensure we have an active session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
        
    async def close(self):
        """Close the session properly"""
        if self.session and not self.session.closed:
            await self.session.close()
            
    async def get_owned_games(self) -> Dict[str, Any]:
        """
        Fetch all owned games with playtime directly from Steam API
        Returns a dictionary mapping app_id to game data
        """
        try:
            session = await self.ensure_session()
            url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
            params = {
                "key": self.api_key,
                "steamid": self.steam_id,
                "include_appinfo": "true",
                "include_played_free_games": "true",
                "format": "json"
            }
            
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    print(f"Steam API error: {response.status}")
                    return {}
                    
                data = await response.json()
                
                if not data or 'response' not in data or 'games' not in data['response']:
                    print("Invalid response from Steam API")
                    return {}
                
                # Create a dictionary mapping app_id to game data
                games_dict = {}
                for game in data['response']['games']:
                    app_id = str(game['appid'])
                    games_dict[app_id] = {
                        'name': game.get('name', 'Unknown'),
                        'playtime_minutes': game.get('playtime_forever', 0),
                        'playtime_2weeks': game.get('playtime_2weeks', 0)
                    }
                
                return games_dict
                
        except Exception as e:
            print(f"Error fetching owned games: {e}")
            import traceback
            traceback.print_exc()
            return {}
            
    async def update_database_playtime(self, db_manager) -> bool:
        """
        Update the database with accurate playtime data from Steam
        Returns True if successful
        """
        try:
            # Get all games from the database
            games = db_manager.get_all_games()
            if not games:
                print("No games found in database")
                return False
                
            # Get playtime data from Steam
            steam_data = await self.get_owned_games()
            if not steam_data:
                print("No data received from Steam API")
                return False
                
            print(f"Got playtime data for {len(steam_data)} games from Steam API")
            
            # Update each game's playtime in the database
            updated_count = 0
            for game in games:
                if game.type == 'steam' and game.app_id in steam_data:
                    playtime = steam_data[game.app_id]['playtime_minutes']
                    
                    # Force update playtime regardless of current value
                    db_manager.update_game(game.id, {'playtime': playtime})
                    print(f"Updated playtime for {game.name}: {playtime} minutes")
                    updated_count += 1
                        
            print(f"Successfully updated playtime for {updated_count} games")
            return True
            
        except Exception as e:
            print(f"Error updating database playtime: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    @classmethod
    async def from_file(cls, api_key_file: str, steam_id: str):
        """Create a client from an API key file"""
        try:
            with open(api_key_file, 'r') as f:
                api_key = f.read().strip()
            return cls(api_key, steam_id)
        except Exception as e:
            print(f"Error reading API key file: {e}")
            return None

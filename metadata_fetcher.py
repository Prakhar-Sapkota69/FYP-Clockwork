import os
import json
import asyncio
import aiohttp
from datetime import datetime
from functools import lru_cache
from typing import List, Dict, Optional
from PySide6.QtCore import QObject, Signal
from models import Game

class MetadataFetcher(QObject):
    progress = Signal(int, int)  # current, total
    finished = Signal(list)  # list of games with metadata
    error = Signal(str)  # error message
    
    # Steam API rate limits
    MAX_REQUESTS_PER_MINUTE = 30
    REQUEST_DELAY = 2.0  # seconds between requests
    
    def __init__(self):
        super().__init__()
        self.api_key = None
        self.steam_id = None
        self.session = None
        self.db_manager = None
        self.force_refresh = False
        self.last_request_time = datetime.now()
        
    async def ensure_session(self):
        """Ensure we have a valid aiohttp session."""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
        
    async def close(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
            
    async def _rate_limit(self):
        """Implement rate limiting for Steam API requests."""
        now = datetime.now()
        elapsed = (now - self.last_request_time).total_seconds()
        if elapsed < self.REQUEST_DELAY:
            await asyncio.sleep(self.REQUEST_DELAY - elapsed)
        self.last_request_time = datetime.now()
        
    @lru_cache(maxsize=1000)
    async def _fetch_steam_store_metadata(self, appid: str) -> Optional[Dict]:
        """Fetch metadata for a single game from Steam Store API."""
        try:
            await self._rate_limit()
            session = await self.ensure_session()
            url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    try:
                        data = await response.json()
                        if data and appid in data and data[appid]['success']:
                            return data[appid]['data']
                    except json.JSONDecodeError:
                        pass
                        
            return None
        except Exception as e:
            print(f"Error fetching Steam store metadata for app {appid}: {e}")
            return None
            
    async def _fetch_metadata_batch(self, games: List[Game]) -> List[Optional[Dict]]:
        """Fetch metadata for a batch of games in parallel."""
        if not games:
            return []
            
        # Create tasks for each game
        tasks = []
        for game in games:
            if game.app_id:
                task = asyncio.create_task(self._fetch_steam_store_metadata(game.app_id))
                tasks.append(task)
            else:
                tasks.append(None)
                
        # Wait for all tasks to complete
        results = []
        for task in tasks:
            if task:
                try:
                    result = await task
                    results.append(result)
                except Exception as e:
                    print(f"Error fetching metadata: {str(e)}")
                    results.append(None)
            else:
                results.append(None)

        return results

    async def fetch_metadata_for_games(self, games: List[Game]) -> List[Game]:
        """Fetch metadata for a list of games from the Steam Store API."""
        if not games:
            return []
        
        # First, fetch playtime data from Steam API for all games
        await self.update_playtime_data(games)
        
        # Filter out games that already have metadata, unless force_refresh is True
        if not self.force_refresh:
            games_needing_metadata = [game for game in games if not game.metadata_fetched]
            if not games_needing_metadata:
                return games
        else:
            games_needing_metadata = games
            
        steam_games = [game for game in games_needing_metadata if game.type == 'steam']
        
        # Extract app IDs from launch commands if not present
        for game in steam_games:
            if not game.app_id and game.launch_command:
                try:
                    if 'steam://rungameid/' in game.launch_command:
                        app_id = game.launch_command.split('steam://rungameid/')[-1].strip()
                        app_id = ''.join(filter(str.isdigit, app_id))
                        if app_id:
                            game.app_id = app_id
                            # Update the database with the extracted app ID
                            self.db_manager.update_game(game.id, {'app_id': app_id})
                except Exception as e:
                    continue

        # Filter games with valid app IDs
        games_with_app_ids = [game for game in steam_games if game.app_id]
        if not games_with_app_ids:
            # Mark all games as processed to prevent endless retries
            for game in games:
                if not game.metadata_fetched:
                    self.db_manager.update_game(game.id, {'metadata_fetched': True})
                    game.metadata_fetched = True
            return games

        total_games = len(games_with_app_ids)
        processed_games = 0
        batch_size = 10

        try:
            async with aiohttp.ClientSession() as session:
                self.session = session
                
                for i in range(0, total_games, batch_size):
                    batch = games_with_app_ids[i:i + batch_size]
                    results = await self._fetch_metadata_batch(batch)
                    
                    for game, metadata in zip(batch, results):
                        if metadata:
                            # Extract metadata fields
                            if self._update_game_metadata(game, metadata):
                                # Update the database with the extracted metadata
                                update_data = {
                                    'genre': game.genre,
                                    'poster_url': game.poster_url,
                                    'description': game.description,
                                    'release_date': game.release_date,
                                    'rating': game.rating,
                                    'metacritic': game.metacritic,
                                    'esrb_rating': game.esrb_rating,
                                    'platforms': game.platforms,
                                    'developers': game.developers,
                                    'publishers': game.publishers,
                                    'metadata_fetched': True
                                }
                                self.db_manager.update_game(game.id, update_data)
                    
                    processed_games += len(batch)
                    self.progress.emit(processed_games, total_games)
                    
                    # Add delay between batches
                    if i + batch_size < total_games:
                        await asyncio.sleep(self.REQUEST_DELAY)
            
        except Exception as e:
            error_msg = f"Error fetching metadata: {str(e)}"
            self.error.emit(error_msg)
            return games

        self.finished.emit(games)
        return games

    async def update_playtime_data(self, games: List[Game]) -> None:
        """Fetch and update playtime data for all Steam games"""
        try:
            if not self.api_key or not self.steam_id:
                return
                
            # Get all Steam games with app_ids
            steam_games = {game.app_id: game for game in games 
                          if game.type == 'steam' and game.app_id}
            
            if not steam_games:
                return
                
            await self._rate_limit()
            session = await self.ensure_session()
            url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={self.api_key}&steamid={self.steam_id}&include_appinfo=true&include_played_free_games=true&format=json"
            
            async with session.get(url) as response:
                if response.status == 200:
                    try:
                        data = await response.json()
                        if 'response' in data and 'games' in data['response']:
                            # Create a mapping of app_id to playtime
                            playtime_data = {
                                str(game['appid']): game.get('playtime_forever', 0)
                                for game in data['response']['games']
                            }
                            
                            # Update playtime for each game
                            for app_id, game in steam_games.items():
                                if app_id in playtime_data:
                                    # Convert minutes to hours and round to 1 decimal place
                                    playtime_minutes = playtime_data[app_id]
                                    game.playtime = playtime_minutes
                                    
                                    # Update the database
                                    self.db_manager.update_game(game.id, {'playtime': playtime_minutes})
                    except json.JSONDecodeError:
                        pass
        except Exception as e:
            pass

    def _update_game_metadata(self, game: Game, steam_data: Dict) -> bool:
        """Update a Game object with metadata from Steam store data."""
        if not steam_data:
            return False

        try:
            print(f"[DEBUG] Updating metadata for {game.name} (App ID: {game.app_id})")
            
            # Only update fields with valid data
            if 'name' in steam_data and steam_data['name']:
                game.name = steam_data['name']
                print(f"[DEBUG] Updated name: {game.name}")
            
            # Get header image - primary source
            if 'header_image' in steam_data and steam_data['header_image']:
                game.poster_url = steam_data['header_image']
                print(f"[DEBUG] Set poster_url from header_image: {game.poster_url}")
            # Fallback to screenshots if available
            elif 'screenshots' in steam_data and steam_data['screenshots'] and len(steam_data['screenshots']) > 0:
                game.poster_url = steam_data['screenshots'][0]['path_full']
                print(f"[DEBUG] Set poster_url from screenshots: {game.poster_url}")
            # Fallback to background image if available
            elif 'background' in steam_data and steam_data['background']:
                game.poster_url = steam_data['background']
                print(f"[DEBUG] Set poster_url from background: {game.poster_url}")
            else:
                print(f"[DEBUG] No poster image found for {game.name}")
                
            # Get background image for details page
            if 'background' in steam_data and steam_data['background']:
                game.background_url = steam_data['background']
            
            # Get description - prefer short_description as it's more concise
            if 'short_description' in steam_data and steam_data['short_description']:
                game.description = steam_data['short_description']
            elif 'detailed_description' in steam_data and steam_data['detailed_description']:
                # Truncate detailed description to a reasonable length
                desc = steam_data['detailed_description']
                if len(desc) > 500:
                    desc = desc[:500] + "..."
                game.description = desc
            else:
                game.description = 'No description available'
            
            # Get genres
            if 'genres' in steam_data and steam_data['genres']:
                game.genre = ', '.join(genre['description'] for genre in steam_data['genres'])
            else:
                game.genre = 'Uncategorized'
            
            # Get platforms
            if 'platforms' in steam_data and steam_data['platforms']:
                game.platforms = [
                    platform for platform, supported in steam_data['platforms'].items()
                    if supported
                ]
            else:
                game.platforms = []
            
            # Get release date
            if 'release_date' in steam_data and steam_data['release_date']:
                if 'date' in steam_data['release_date']:
                    game.release_date = steam_data['release_date']['date']
                else:
                    game.release_date = 'Unknown'
            else:
                game.release_date = 'Unknown'
            
            # Get metacritic score
            if 'metacritic' in steam_data and isinstance(steam_data['metacritic'], dict) and 'score' in steam_data['metacritic']:
                game.rating = steam_data['metacritic']['score'] / 20  # Convert to 5-point scale
                game.metacritic = steam_data['metacritic']['score']
            else:
                game.rating = 0
                game.metacritic = 0
            
            # Get ESRB rating
            if 'content_descriptors' in steam_data and 'notes' in steam_data['content_descriptors']:
                game.esrb_rating = steam_data['content_descriptors']['notes']
            else:
                game.esrb_rating = 'Not Rated'
            
            # Get developers and publishers
            if 'developers' in steam_data:
                game.developers = steam_data['developers']
            else:
                game.developers = []
                
            if 'publishers' in steam_data:
                game.publishers = steam_data['publishers']
            else:
                game.publishers = []
            
            # Mark as having metadata
            game.metadata_fetched = True
            
            print(f"[DEBUG] Metadata update complete for {game.name}")
            return True
            
        except Exception as e:
            print(f"Error updating game metadata: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def fetch_owned_games(self) -> List[Game]:
        """Fetch owned games from Steam API."""
        if not self.api_key or not self.steam_id:
            self.error.emit("Steam API key or Steam ID not set")
            return []
            
        try:
            await self._rate_limit()
            session = await self.ensure_session()
            url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={self.api_key}&steamid={self.steam_id}&include_appinfo=true&include_played_free_games=true&format=json"
            
            async with session.get(url) as response:
                if response.status == 200:
                    try:
                        data = await response.json()
                        if 'response' in data and 'games' in data['response']:
                            games = []
                            for game_data in data['response']['games']:
                                game = Game(
                                    name=game_data['name'],
                                    type='steam',
                                    app_id=str(game_data['appid']),
                                    launch_command=f"steam://rungameid/{game_data['appid']}",
                                    playtime=game_data.get('playtime_forever', 0),
                                    metadata_fetched=False
                                )
                                games.append(game)
                            return games
                    except json.JSONDecodeError:
                        self.error.emit("Failed to parse Steam API response")
                else:
                    self.error.emit(f"Steam API request failed with status {response.status}")
        except Exception as e:
            self.error.emit(f"Error fetching owned games: {str(e)}")
            
        return []

    async def test_steam_api(self) -> bool:
        """Test Steam API connection."""
        if not self.api_key or not self.steam_id:
            return False
            
        try:
            await self._rate_limit()
            session = await self.ensure_session()
            url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={self.api_key}&steamids={self.steam_id}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    try:
                        data = await response.json()
                        if 'response' in data and 'players' in data['response']:
                            return len(data['response']['players']) > 0
                    except json.JSONDecodeError:
                        pass
        except Exception as e:
            print(f"Error testing Steam API: {e}")
            
        return False

    def fetch_metadata(self, game):
        """Fetch metadata for a game based on its type."""
        if game.type == 'steam':
            return self._fetch_steam_metadata(game)
        else:
            return None

    def _fetch_steam_metadata(self, game):
        """Fetch metadata for a Steam game."""
        try:
            if not game.app_id:
                return None
                
            url = f"https://store.steampowered.com/api/appdetails?appids={game.app_id}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if data and game.app_id in data and data[game.app_id]['success']:
                    return data[game.app_id]['data']
                    
            return None
        except Exception as e:
            print(f"Error fetching Steam metadata: {e}")
            return None 
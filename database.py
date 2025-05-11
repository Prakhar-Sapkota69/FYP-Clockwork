import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from models import Game

class DatabaseManager:
    def __init__(self, db_path='games.db'):
        """Initialize database connection and create tables if they don't exist."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.init_database()
        self.update_database_schema()  # Add this line to update schema on initialization
        self.remove_duplicates()
        
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            # Enable foreign keys
            self.cursor.execute("PRAGMA foreign_keys = ON")
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise
        
    def init_database(self):
        """Initialize the database with required tables."""
        try:
            # Create games table with all fields if it doesn't exist
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    install_path TEXT,
                    launch_command TEXT,
                    genre TEXT,
                    is_installed BOOLEAN DEFAULT 0,
                    metadata_fetched BOOLEAN DEFAULT 0,
                    last_played DATETIME,
                    playtime INTEGER DEFAULT 0,
                    poster_url TEXT,
                    poster_path TEXT,
                    app_id TEXT,
                    description TEXT,
                    release_date TEXT,
                    rating REAL,
                    metacritic INTEGER,
                    esrb_rating TEXT,
                    background_url TEXT,
                    platforms TEXT,
                    developers TEXT,
                    publishers TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create platforms table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS platforms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id INTEGER,
                    platform_name TEXT,
                    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
                )
            ''')
            
            # Create developers table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS developers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id INTEGER,
                    developer_name TEXT,
                    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
                )
            ''')
            
            # Create publishers table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS publishers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id INTEGER,
                    publisher_name TEXT,
                    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
                )
            ''')
            
            self.conn.commit()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Error initializing database: {e}")
            import traceback
            traceback.print_exc()
            raise
        
    def remove_duplicates(self):
        """Remove duplicate games from the database."""
        try:
            # First, identify duplicates based on name and platform
            self.cursor.execute('''
                DELETE FROM games 
                WHERE id NOT IN (
                    SELECT MIN(id)
                    FROM games
                    GROUP BY name, type
                )
            ''')
            
            self.conn.commit()
            print("Successfully removed duplicate games from database")
            
        except Exception as e:
            print(f"Error removing duplicates: {e}")
            self.conn.rollback()
            
    def reset_metadata_fetched(self):
        """Reset metadata_fetched flag for all games to force a refresh."""
        try:
            self.cursor.execute("UPDATE games SET metadata_fetched = 0")
            self.conn.commit()
            print("Reset metadata_fetched flag for all games")
            return True
        except Exception as e:
            print(f"Error resetting metadata_fetched: {e}")
            self.conn.rollback()
            return False
            
    def clear_all_metadata(self):
        """Completely clear all metadata from games table to start fresh."""
        try:
            self.cursor.execute("""
                UPDATE games SET 
                    genre = NULL,
                    poster_url = NULL,
                    description = NULL,
                    release_date = NULL,
                    rating = NULL,
                    metacritic = NULL,
                    esrb_rating = NULL,
                    playtime = 0,
                    metadata_fetched = 0
            """)
            
            # Also clear related tables
            self.cursor.execute("DELETE FROM platforms")
            self.cursor.execute("DELETE FROM developers")
            self.cursor.execute("DELETE FROM publishers")
            
            self.conn.commit()
            print("Successfully cleared all metadata from database")
            return True
        except Exception as e:
            print(f"Error clearing metadata: {e}")
            self.conn.rollback()
            return False

    def add_game(self, game: Game) -> Optional[int]:
        """Add a new game to the database."""
        try:
            # Check if a game with the same name and type already exists
            self.cursor.execute(
                "SELECT id FROM games WHERE name = ? AND type = ?",
                (game.name, game.type)
            )
            existing = self.cursor.fetchone()
            if existing:
                print(f"Game {game.name} already exists in database")
                return existing[0]

            # Insert the new game
            self.cursor.execute("""
                INSERT INTO games (
                    name, type, app_id,
                    install_path, launch_command, genre, is_installed,
                    playtime, metadata_fetched, poster_url, poster_path, background_url,
                    release_date, description, rating, platforms,
                    developers, publishers, metacritic, esrb_rating
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                game.name, game.type, game.app_id,
                game.install_path, game.launch_command, game.genre, game.is_installed,
                game.playtime, game.metadata_fetched, game.poster_url, game.poster_path, game.background_url,
                game.release_date, game.description, game.rating,
                ','.join(str(p) for p in (game.platforms or [])),
                ','.join(str(d) for d in (game.developers or [])),
                ','.join(str(p) for p in (game.publishers or [])),
                game.metacritic, game.esrb_rating
            ))
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Error adding game to database: {e}")
            import traceback
            traceback.print_exc()
            return None

    def update_game(self, game_id: int, update_data: Dict) -> bool:
        """Update an existing game in the database with the provided data."""
        try:
            # Build the SQL update statement dynamically based on the provided data
            update_fields = []
            values = []
            for key, value in update_data.items():
                if key in ['platforms', 'developers', 'publishers'] and isinstance(value, list):
                    value = ','.join(str(v) for v in value)
                update_fields.append(f"{key} = ?")
                values.append(value)
            
            # Add the game_id to the values list
            values.append(game_id)
            
            # Construct and execute the SQL statement
            sql = f"UPDATE games SET {', '.join(update_fields)} WHERE id = ?"
            self.cursor.execute(sql, values)
            self.conn.commit()
            
            return True
        except Exception as e:
            print(f"Error updating game in database: {e}")
            import traceback
            traceback.print_exc()
            return False

    def get_all_games(self) -> List[Game]:
        """Get all games from the database."""
        try:
            self.cursor.execute("""
                SELECT id, name, type, app_id, install_path, launch_command,
                       genre, is_installed, playtime, metadata_fetched,
                       poster_url, poster_path, background_url, release_date, description,
                       rating, platforms, developers, publishers,
                       metacritic, esrb_rating
                FROM games
            """)
            rows = self.cursor.fetchall()
            
            games = []
            for row in rows:
                game = Game(
                    id=row[0],
                    name=row[1],
                    type=row[2],
                    app_id=row[3],
                    install_path=row[4],
                    launch_command=row[5],
                    genre=row[6],
                    is_installed=bool(row[7]),
                    playtime=row[8],
                    metadata_fetched=bool(row[9]),
                    poster_url=row[10],
                    poster_path=row[11],
                    background_url=row[12],
                    release_date=row[13],
                    description=row[14],
                    rating=row[15],
                    platforms=row[16].split(',') if row[16] else [],
                    developers=row[17].split(',') if row[17] else [],
                    publishers=row[18].split(',') if row[18] else [],
                    metacritic=row[19],
                    esrb_rating=row[20]
                )
                games.append(game)
            
            return games
        except Exception as e:
            print(f"Error getting games from database: {e}")
            import traceback
            traceback.print_exc()
            return []

    def get_game_by_id(self, game_id: int) -> Optional[Game]:
        """Get a game by its ID."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT id, name, type, app_id, install_path, launch_command,
                       genre, is_installed, playtime, metadata_fetched,
                       poster_url, background_url, release_date, description,
                       rating, platforms, developers, publishers,
                       metacritic, esrb_rating
                FROM games WHERE id = ?
            """, (game_id,))
            row = cursor.fetchone()
            
            if row:
                return Game(
                    id=row[0],
                    name=row[1],
                    type=row[2],
                    app_id=row[3],
                    install_path=row[4],
                    launch_command=row[5],
                    genre=row[6],
                    is_installed=bool(row[7]),
                    playtime=row[8],
                    metadata_fetched=bool(row[9]),
                    poster_url=row[10],
                    background_url=row[11],
                    release_date=row[12],
                    description=row[13],
                    rating=row[14],
                    platforms=row[15].split(',') if row[15] and isinstance(row[15], str) else [],
                    developers=row[16].split(',') if row[16] and isinstance(row[16], str) else [],
                    publishers=row[17].split(',') if row[17] and isinstance(row[17], str) else [],
                    metacritic=row[18],
                    esrb_rating=row[19]
                )
            return None
        except Exception as e:
            print(f"Error getting game by ID from database: {e}")
            return None

    def get_game_by_app_id(self, app_id: str) -> Optional[Game]:
        """Get a game by its Steam app ID."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM games WHERE app_id = ?", (app_id,))
            row = cursor.fetchone()
            
            if row:
                return Game(
                    id=row[0],
                    name=row[1],
                    type=row[2],
                    app_id=row[3],
                    install_path=row[4],
                    launch_command=row[5],
                    genre=row[6],
                    is_installed=bool(row[7]),
                    playtime=row[8],
                    metadata_fetched=bool(row[9]),
                    poster_url=row[10],
                    background_url=row[11],
                    release_date=row[12],
                    description=row[13],
                    rating=row[14],
                    platforms=row[15].split(',') if row[15] else [],
                    developers=row[16].split(',') if row[16] else [],
                    publishers=row[17].split(',') if row[17] else [],
                    metacritic=row[18],
                    esrb_rating=row[19]
                )
            return None
        except Exception as e:
            print(f"Error getting game by app ID from database: {e}")
            return None

    def delete_game(self, game_id: int) -> bool:
        """Delete a game from the database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM games WHERE id = ?", (game_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting game from database: {e}")
            return False

    def update_game_playtime(self, game_id: int, playtime: int) -> bool:
        """Update a game's playtime."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE games SET playtime = ? WHERE id = ?", (playtime, game_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating game playtime: {e}")
            return False

    def get_game_playtime(self, game_id: int) -> Optional[int]:
        """Get a game's playtime."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT playtime FROM games WHERE id = ?", (game_id,))
            row = cursor.fetchone()
            return row[0] if row else None
        except Exception as e:
            print(f"Error getting game playtime: {e}")
            return None

    def update_database_schema(self):
        """Update the database schema with new fields."""
        try:
            # Check if poster_path column exists
            self.cursor.execute("PRAGMA table_info(games)")
            columns = [column[1] for column in self.cursor.fetchall()]
            
            # Add poster_path column if it doesn't exist
            if 'poster_path' not in columns:
                self.cursor.execute("ALTER TABLE games ADD COLUMN poster_path TEXT")
                self.conn.commit()
                
        except Exception as e:
            print(f"Error updating database schema: {e}")

    def remove_game(self, game_id: int) -> bool:
        """Remove a game from the database."""
        try:
            self.cursor.execute("DELETE FROM games WHERE id = ?", (game_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error removing game from database: {e}")
            import traceback
            traceback.print_exc()
            return False

    def __del__(self):
        """Close database connection when object is destroyed"""
        if hasattr(self, 'conn'):
            self.conn.close() 
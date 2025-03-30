#!/usr/bin/env python
"""
Reset Metadata Script
This script completely clears all metadata from the database and allows you to re-fetch it.
"""

import asyncio
import sys
from database import DatabaseManager
from metadata_fetcher import MetadataFetcher

async def reset_and_fetch_metadata():
    """Reset all metadata and fetch fresh data"""
    print("Starting metadata reset process...")
    
    # Initialize database and metadata fetcher
    db = DatabaseManager()
    metadata_fetcher = MetadataFetcher()
    
    # Clear all existing metadata
    print("Clearing all existing metadata...")
    db.clear_all_metadata()
    
    # Get all games from database
    games = db.get_all_games()
    print(f"Found {len(games)} games in database")
    
    # Fetch fresh metadata
    print("Fetching fresh metadata for all games...")
    await metadata_fetcher.fetch_metadata_for_games(games)
    
    print("Metadata reset and refresh complete!")

if __name__ == "__main__":
    print("=== Metadata Reset Tool ===")
    print("WARNING: This will clear ALL existing metadata and fetch it again.")
    print("This process may take several minutes depending on the number of games.")
    
    response = input("Do you want to proceed? (y/n): ")
    if response.lower() == 'y':
        asyncio.run(reset_and_fetch_metadata())
    else:
        print("Operation cancelled.")

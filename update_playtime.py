#!/usr/bin/env python
"""
Update Playtime Script
This script ONLY updates playtime data directly from the Steam API.
It doesn't touch any other metadata.
"""

import asyncio
import sys
import os
from database import DatabaseManager
from steam_api_client import SteamAPIClient
from game_search import STEAM_ID, STEAM_API_KEY

async def update_playtime():
    """Update playtime data only"""
    print("Starting playtime update process...")
    
    # Initialize database
    db = DatabaseManager()
    
    # Get Steam ID directly from game_search.py
    steam_id = STEAM_ID
    
    if not steam_id:
        print("Error: Steam ID not found")
        return
    
    print(f"Using Steam ID: {steam_id}")
    
    # Create Steam API client directly with API key
    client = SteamAPIClient(STEAM_API_KEY, steam_id)
    
    try:
        # Update playtime data in database
        print("Fetching playtime data from Steam API...")
        success = await client.update_database_playtime(db)
        
        if success:
            print("Playtime data updated successfully!")
        else:
            print("Failed to update playtime data")
    finally:
        # Close the client session
        await client.close()

if __name__ == "__main__":
    print("=== Steam Playtime Update Tool ===")
    print("This will update ONLY the playtime data for your games.")
    
    try:
        asyncio.run(update_playtime())
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

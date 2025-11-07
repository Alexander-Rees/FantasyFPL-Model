#!/usr/bin/env python3
"""
Database Population Script for FPL Player Data
==============================================

This script fetches fresh FPL player data and populates the MySQL database
with player information that the Spring Boot backend can read.

Usage:
    python populate_database.py
"""

import mysql.connector
from mysql.connector import Error
import requests
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'fantasy_soccer',
    'user': 'root',
    'password': 'NewPassword',
    'port': 3306
}

# FPL API Configuration
FPL_BASE_URL = 'https://fantasy.premierleague.com/api'
FPL_STATIC_URL = f'{FPL_BASE_URL}/bootstrap-static/'

def get_db_connection():
    """Get MySQL database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        logger.error(f"Error connecting to MySQL: {e}")
        return None

def fetch_fpl_data(endpoint, timeout=30):
    """Fetch data from FPL API with timeout handling"""
    try:
        logger.info(f"Fetching data from: {endpoint}")
        response = requests.get(endpoint, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        logger.error(f"Timeout fetching data from {endpoint}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from {endpoint}: {e}")
        return None

def process_player_data(static_data):
    """Process FPL player data into standardized format"""
    enhanced_players = []
    
    for player in static_data['elements']:
        # Get team name
        team_name = next((team['name'] for team in static_data['teams'] if team['id'] == player['team']), 'Unknown')
        
        # Get position name
        position_map = {1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD'}
        position = position_map.get(player['element_type'], 'Unknown')
        
        enhanced_player = {
            'id': player['id'],
            'name': player['web_name'],
            'team': team_name,
            'position': position,
            'value': player['now_cost'] / 10,
            'total_points': player['total_points'],
            'weekly_points': player['event_points'],
        }
        
        enhanced_players.append(enhanced_player)
    
    return enhanced_players

def clear_existing_players():
    """Clear existing player data from database"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Disable foreign key checks temporarily
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        # Clear team_players table first (due to foreign key constraint)
        cursor.execute("DELETE FROM team_players")
        logger.info("Cleared team_players table")
        
        # Clear players table
        cursor.execute("DELETE FROM player")
        logger.info("Cleared player table")
        
        # Re-enable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        logger.info("Successfully cleared existing player data")
        return True
        
    except Error as e:
        logger.error(f"Error clearing existing players: {e}")
        return False

def upsert_players_to_db(players):
    """
    Insert or update player data in MySQL database using UPSERT.
    This preserves existing player IDs, keeping team_players references intact.
    """
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Use INSERT ... ON DUPLICATE KEY UPDATE
        # This updates existing players (matched by fpl_id) or inserts new ones
        # Preserves existing player.id values, so team_players references stay valid
        upsert_query = """
        INSERT INTO player (name, position, team, fpl_id, value, total_points, weekly_points)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            name = VALUES(name),
            position = VALUES(position),
            team = VALUES(team),
            value = VALUES(value),
            total_points = VALUES(total_points),
            weekly_points = VALUES(weekly_points)
        """
        
        # Prepare data (don't specify id - let auto-increment handle it for new players)
        player_data = []
        for player in players:
            player_data.append((
                player['name'],
                player['position'],
                player['team'],
                player['id'],  # fpl_id (used for matching)
                player['value'],
                player['total_points'],
                player['weekly_points']
            ))
        
        # Upsert all players
        cursor.executemany(upsert_query, player_data)
        connection.commit()
        
        logger.info(f"Successfully upserted {len(players)} players into database")
        logger.info("✅ Player IDs preserved - team references remain intact")
        
        cursor.close()
        connection.close()
        return True
        
    except Error as e:
        logger.error(f"Error upserting players: {e}")
        return False

def main():
    """
    Main function to populate database with FPL player data.
    Uses UPSERT to preserve existing player IDs and team references.
    """
    logger.info("Starting database population with FPL player data...")
    logger.info("Using UPSERT strategy to preserve player IDs and team references")
    
    # Step 1: Fetch fresh FPL data
    logger.info("Step 1: Fetching fresh FPL data...")
    static_data = fetch_fpl_data(FPL_STATIC_URL)
    if not static_data:
        logger.error("Failed to fetch FPL data")
        return False
    
    # Step 2: Process player data
    logger.info("Step 2: Processing player data...")
    players = process_player_data(static_data)
    logger.info(f"Processed {len(players)} players")
    
    # Step 3: Upsert players into database (updates existing, inserts new)
    logger.info("Step 3: Upserting players into database...")
    logger.info("  - Existing players will be updated (preserving their IDs)")
    logger.info("  - New players will be inserted")
    if not upsert_players_to_db(players):
        logger.error("Failed to upsert players into database")
        return False
    
    logger.info("✅ Database population completed successfully!")
    logger.info(f"📊 Upserted {len(players)} players")
    logger.info(f"🕒 Completed at: {datetime.now().isoformat()}")
    logger.info("✅ Player IDs preserved - all team references remain valid")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

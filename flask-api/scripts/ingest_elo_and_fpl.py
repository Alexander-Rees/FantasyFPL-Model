#!/usr/bin/env python3
"""
FPL Data Ingestion Script
========================

This script runs as part of GitHub Actions to ingest fresh FPL data twice daily.
It combines FPL-Elo-Insights data with official FPL API data for comprehensive player stats.

Usage:
    python scripts/ingest_elo_and_fpl.py

Environment Variables:
    DB_HOST: PostgreSQL host (default: localhost)
    DB_USER: PostgreSQL username (default: postgres)
    DB_PASSWORD: PostgreSQL password (required)
    DB_NAME: PostgreSQL database name (default: fantasy_soccer)
"""

import os
import sys
import logging
import requests
import pandas as pd
import psycopg2
from psycopg2 import Error
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration - PostgreSQL (Supabase)
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME', 'fantasy_soccer'),
    'port': int(os.getenv('DB_PORT', '5432'))
}

# FPL API endpoints
FPL_BASE_URL = "https://fantasy.premierleague.com/api"
# ELO_DATA_PATH is relative to flask-api directory when script runs from there
ELO_DATA_PATH = os.getenv('ELO_DATA_PATH', "../temp-elo-data/data")

def get_db_connection():
    """Get PostgreSQL database connection"""
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        logger.info("Successfully connected to PostgreSQL database")
        return connection
    except Error as e:
        logger.error(f"Error connecting to PostgreSQL: {e}")
        raise

def fetch_fpl_data():
    """Fetch fresh data from official FPL API"""
    try:
        logger.info("Fetching data from FPL API...")
        response = requests.get(f"{FPL_BASE_URL}/bootstrap-static/", timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract players data
        players = []
        for player in data['elements']:
            players.append({
                'fpl_id': player['id'],
                'name': player['web_name'],
                'first_name': player['first_name'],
                'second_name': player['second_name'],
                'position': get_position_name(player['element_type']),
                'team': get_team_name(player['team'], data['teams']),
                'value': player['now_cost'] / 10.0,  # Convert to millions
                'total_points': player['total_points'],
                'weekly_points': player['event_points'],
                'form': player['form'],
                'selected_by_percent': player['selected_by_percent'],
                'transfers_in': player['transfers_in'],
                'transfers_out': player['transfers_out'],
                'news': player['news'],
                'news_added': player['news_added'],
                'chance_of_playing_next_round': player['chance_of_playing_next_round'],
                'chance_of_playing_this_round': player['chance_of_playing_this_round'],
                'value_form': player['value_form'],
                'value_season': player['value_season'],
                'cost_change_start': player['cost_change_start'],
                'cost_change_event': player['cost_change_event'],
                'in_dreamteam': player['in_dreamteam']
            })
        
        logger.info(f"Fetched {len(players)} players from FPL API")
        return players
        
    except Exception as e:
        logger.error(f"Error fetching FPL data: {e}")
        raise

def get_position_name(element_type):
    """Convert element type to position name"""
    position_map = {1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD'}
    return position_map.get(element_type, 'UNKNOWN')

def get_team_name(team_id, teams_data):
    """Get team name from team ID"""
    for team in teams_data:
        if team['id'] == team_id:
            return team['name']
    return 'UNKNOWN'

def load_elo_data():
    """Load Elo data from FPL-Elo-Insights repository"""
    try:
        # Find the most recent season directory
        season_dirs = []
        if os.path.exists(ELO_DATA_PATH):
            for item in os.listdir(ELO_DATA_PATH):
                if os.path.isdir(os.path.join(ELO_DATA_PATH, item)) and item.startswith('20'):
                    season_dirs.append(item)
        
        if not season_dirs:
            logger.warning("No season directories found in Elo data")
            return None
        
        # Use the most recent season
        latest_season = sorted(season_dirs)[-1]
        season_path = os.path.join(ELO_DATA_PATH, latest_season)
        logger.info(f"Using Elo data from season: {latest_season}")
        
        # Load players data
        players_file = os.path.join(season_path, 'players.csv')
        if not os.path.exists(players_file):
            logger.warning(f"Players file not found: {players_file}")
            return None
        
        elo_df = pd.read_csv(players_file)
        logger.info(f"Loaded {len(elo_df)} players from Elo data")
        return elo_df
        
    except Exception as e:
        logger.error(f"Error loading Elo data: {e}")
        return None

def merge_data(fpl_players, elo_data):
    """Merge FPL API data with Elo data"""
    try:
        fpl_df = pd.DataFrame(fpl_players)
        
        if elo_data is not None:
            # Merge on player name (this is approximate matching)
            merged_df = fpl_df.merge(
                elo_data, 
                left_on='name', 
                right_on='name', 
                how='left',
                suffixes=('_fpl', '_elo')
            )
            logger.info(f"Merged data: {len(merged_df)} players")
        else:
            merged_df = fpl_df
            logger.info("Using FPL data only (no Elo data available)")
        
        return merged_df
        
    except Exception as e:
        logger.error(f"Error merging data: {e}")
        return pd.DataFrame(fpl_players)

def update_database(players_df):
    """
    Update the database with fresh player data using UPSERT (PostgreSQL).
    This preserves existing player IDs, keeping team_players references intact.
    """
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Use INSERT ... ON CONFLICT (PostgreSQL syntax)
        # This updates existing players (matched by fpl_id) or inserts new ones
        # Preserves existing player.id values, so team_players references stay valid
        upsert_query = """
        INSERT INTO player (name, position, team, fpl_id, value, total_points, weekly_points, form, selected_by_percent, elo_rating, elo_form)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (fpl_id) DO UPDATE SET
            name = EXCLUDED.name,
            position = EXCLUDED.position,
            team = EXCLUDED.team,
            value = EXCLUDED.value,
            total_points = EXCLUDED.total_points,
            weekly_points = EXCLUDED.weekly_points,
            form = EXCLUDED.form,
            selected_by_percent = EXCLUDED.selected_by_percent,
            elo_rating = EXCLUDED.elo_rating,
            elo_form = EXCLUDED.elo_form
        """
        
        # Prepare data (don't specify id - let auto-increment handle it for new players)
        player_data = []
        for _, player in players_df.iterrows():
            player_data.append((
                player['name'],
                player['position'],
                player['team'],
                player['fpl_id'],  # Used for matching existing players
                player['value'],
                player['total_points'],
                player['weekly_points'],
                player.get('form', 0),
                player.get('selected_by_percent', '0.0'),
                player.get('elo_rating', 0),
                player.get('elo_form', 0)
            ))
        
        # Upsert all players
        cursor.executemany(upsert_query, player_data)
        connection.commit()
        
        logger.info(f"Successfully upserted {len(player_data)} players")
        logger.info("✅ Player IDs preserved - team references remain intact")
        
        # Log ingestion run (PostgreSQL syntax)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ingest_runs (
            id BIGSERIAL PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            players_count INT,
            status VARCHAR(50),
            notes TEXT
        )
        """)
        
        cursor.execute("""
        INSERT INTO ingest_runs (players_count, status, notes)
        VALUES (%s, %s, %s)
        """, (len(player_data), 'SUCCESS', f'Ingested {len(player_data)} players'))
        connection.commit()
        
    except Error as e:
        logger.error(f"Database error: {e}")
        if connection:
            connection.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def main():
    """Main ingestion function"""
    try:
        logger.info("Starting FPL data ingestion...")
        
        # Check required environment variables
        if not DB_CONFIG['password']:
            logger.error("DB_PASSWORD environment variable is required")
            sys.exit(1)
        
        # Fetch data from FPL API
        fpl_players = fetch_fpl_data()
        
        # Load Elo data (optional)
        elo_data = load_elo_data()
        
        # Merge data
        merged_data = merge_data(fpl_players, elo_data)
        
        # Update database
        update_database(merged_data)
        
        logger.info("Data ingestion completed successfully!")
        
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

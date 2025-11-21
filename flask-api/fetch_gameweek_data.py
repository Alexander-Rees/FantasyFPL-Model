import requests
import pandas as pd
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
FPL_API_BASE = 'https://fantasy.premierleague.com/api'
DATA_PATH = '../model-files/df_combined.pkl'

def fetch_current_gameweek():
    """Fetch current gameweek number from FPL API"""
    try:
        response = requests.get(f'{FPL_API_BASE}/bootstrap-static/')
        response.raise_for_status()
        data = response.json()
        
        # Find current gameweek
        for event in data['events']:
            if event['is_current']:
                return event['id']
        
        # If no current, return next
        for event in data['events']:
            if event['is_next']:
                return event['id'] - 1
                
        return None
    except Exception as e:
        logger.error(f"Error fetching current gameweek: {e}")
        return None

def fetch_player_gameweek_data(player_id, gameweek):
    """Fetch a specific player's data for a gameweek"""
    try:
        response = requests.get(f'{FPL_API_BASE}/element-summary/{player_id}/')
        response.raise_for_status()
        data = response.json()
        
        # Find the specific gameweek in history
        for match in data['history']:
            if match['round'] == gameweek:
                return match
        
        return None
    except Exception as e:
        logger.error(f"Error fetching player {player_id} GW {gameweek}: {e}")
        return None

def fetch_all_players_gameweek(gameweek):
    """Fetch all players' data for a specific gameweek"""
    logger.info(f"Fetching data for gameweek {gameweek}...")
    
    # Get all players
    response = requests.get(f'{FPL_API_BASE}/bootstrap-static/')
    response.raise_for_status()
    bootstrap = response.json()
    
    players_data = []
    total_players = len(bootstrap['elements'])
    
    for idx, player in enumerate(bootstrap['elements'], 1):
        if idx % 50 == 0:
            logger.info(f"Progress: {idx}/{total_players} players")
        
        player_id = player['id']
        gw_data = fetch_player_gameweek_data(player_id, gameweek)
        
        if gw_data:
            # Combine player info with gameweek performance
            row = {
                'name': player['web_name'],
                'team': bootstrap['teams'][player['team'] - 1]['name'],
                'position': ['GK', 'DEF', 'MID', 'FWD'][player['element_type'] - 1],
                'GW': gameweek,
                'value': player['now_cost'] / 10.0,
                'total_points': gw_data['total_points'],
                'minutes': gw_data['minutes'],
                'goals_scored': gw_data['goals_scored'],
                'assists': gw_data['assists'],
                'clean_sheets': gw_data['clean_sheets'],
                'goals_conceded': gw_data['goals_conceded'],
                'saves': gw_data['saves'],
                'bonus': gw_data['bonus'],
                'bps': gw_data['bps'],
                'influence': float(gw_data['influence']),
                'creativity': float(gw_data['creativity']),
                'threat': float(gw_data['threat']),
                'ict_index': float(gw_data['ict_index']),
                'expected_goals': float(gw_data['expected_goals']),
                'expected_assists': float(gw_data['expected_assists']),
                'expected_goal_involvements': float(gw_data['expected_goal_involvements']),
                'expected_goals_conceded': float(gw_data['expected_goals_conceded']),
                'selected_by_percent': float(player['selected_by_percent']),
                'transfers_in': gw_data.get('transfers_in', 0),
                'transfers_out': gw_data.get('transfers_out', 0),
            }
            players_data.append(row)
    
    logger.info(f"Fetched data for {len(players_data)} players")
    return pd.DataFrame(players_data)

def append_to_historical_data(new_data):
    """Append new gameweek data to historical dataset"""
    if os.path.exists(DATA_PATH):
        logger.info(f"Loading existing data from {DATA_PATH}")
        df_historical = pd.read_pickle(DATA_PATH)
        
        # Check if this gameweek already exists
        if 'GW' in df_historical.columns:
            max_gw = df_historical['GW'].max()
            new_gw = new_data['GW'].iloc[0] if len(new_data) > 0 else None
            
            if new_gw and new_gw <= max_gw:
                logger.warning(f"Gameweek {new_gw} already exists in historical data (max GW: {max_gw})")
                return False
        
        # Append new data
        df_combined = pd.concat([df_historical, new_data], ignore_index=True)
        logger.info(f"Combined data: {len(df_historical)} + {len(new_data)} = {len(df_combined)} rows")
    else:
        logger.info("No existing data found, creating new dataset")
        df_combined = new_data
    
    # Save updated dataset
    df_combined.to_pickle(DATA_PATH)
    logger.info(f"Saved updated data to {DATA_PATH}")
    
    # Also save as CSV backup
    csv_path = DATA_PATH.replace('.pkl', f'_backup_{datetime.now().strftime("%Y%m%d")}.csv')
    df_combined.to_csv(csv_path, index=False)
    logger.info(f"Saved CSV backup to {csv_path}")
    
    return True

def main():
    """Main function to fetch latest gameweek and update historical data"""
    # Get current gameweek
    current_gw = fetch_current_gameweek()
    
    if not current_gw:
        logger.error("Could not determine current gameweek")
        return
    
    logger.info(f"Current gameweek: {current_gw}")
    
    # Fetch data for the just-completed gameweek
    # (Usually run on Monday after weekend games)
    completed_gw = current_gw - 1 if current_gw > 1 else current_gw
    
    logger.info(f"Fetching data for completed gameweek: {completed_gw}")
    new_data = fetch_all_players_gameweek(completed_gw)
    
    if len(new_data) == 0:
        logger.error("No data fetched")
        return
    
    # Append to historical data
    success = append_to_historical_data(new_data)
    
    if success:
        logger.info("✅ Successfully updated historical data!")
        logger.info("Next step: Run train_model.py to retrain with new data")
    else:
        logger.info("ℹ️ Data already up to date")

if __name__ == "__main__":
    main()

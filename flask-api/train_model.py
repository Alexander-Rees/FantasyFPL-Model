import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
MODEL_DIR = 'models'
DATA_PATH = '../model-files/df_combined.pkl'  # Primary data source
FALLBACK_DATA_PATH = '../model-files/df_2024_25.csv'

def load_data():
    """Load historical player data"""
    if os.path.exists(DATA_PATH):
        logger.info(f"Loading data from {DATA_PATH}...")
        try:
            df = pd.read_pickle(DATA_PATH)
            return df
        except Exception as e:
            logger.error(f"Failed to load pickle: {e}")
    
    if os.path.exists(FALLBACK_DATA_PATH):
        logger.info(f"Loading data from {FALLBACK_DATA_PATH}...")
        df = pd.read_csv(FALLBACK_DATA_PATH)
        return df
        
    raise FileNotFoundError("No training data found!")

def prepare_features(df):
    """
    Engineer features to match app_with_db.py requirements.
    Crucially, we must simulate 'past knowledge' to predict 'future points'.
    
    We will:
    1. Sort by player and Gameweek (GW).
    2. Calculate cumulative stats up to GW N.
    3. Use these cumulative stats as features for GW N+1.
    4. Target is points in GW N+1.
    """
    logger.info("Preparing features...")
    
    # Ensure required columns exist (mapping common FPL CSV headers)
    # Adjust these mappings based on actual CSV columns if needed
    col_map = {
        'total_points': 'match_points', # In history files, total_points is usually the match points
        'GW': 'gameweek',
        'name': 'name',
        'element': 'player_id'
    }
    
    # If 'total_points' is cumulative in the input, we need to handle it differently.
    # But usually in 'df_combined' or 'df_2024_25', rows are matches.
    # Let's assume rows are matches.
    
    df = df.copy()
    
    # Basic cleaning
    df['gameweek'] = pd.to_numeric(df['GW'], errors='coerce')
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    
    # Sort
    df = df.sort_values(['name', 'gameweek'])
    
    # Calculate Cumulative Stats (The "Current State" before the match)
    # We want to predict 'total_points' (match points) using stats from *previous* matches.
    
    # Group by player
    grouped = df.groupby('name')
    
    # Features needed by app_with_db.py:
    # value, form, points_per_game, minutes, goals_scored, assists, clean_sheets, 
    # goals_conceded, saves, bonus, bps, influence, creativity, threat, ict_index, 
    # expected_goals, expected_assists, expected_goal_involvements, expected_goals_conceded
    
    # Calculate cumulative sums for counting stats
    cumsum_cols = ['minutes', 'goals_scored', 'assists', 'clean_sheets', 
                   'goals_conceded', 'saves', 'bonus', 'bps', 
                   'influence', 'creativity', 'threat', 'ict_index',
                   'expected_goals', 'expected_assists', 'expected_goal_involvements', 'expected_goals_conceded']
    
    # Ensure columns exist, fill with 0 if not
    for col in cumsum_cols:
        if col not in df.columns:
            df[col] = 0
            
    # Shifted features: The stats *before* this gameweek
    # We calculate cumulative sum up to the *previous* row
    for col in cumsum_cols:
        df[f'cum_{col}'] = grouped[col].transform(lambda x: x.cumsum().shift(1)).fillna(0)
        
    # Cumulative points (to calculate points_per_game)
    df['cum_points'] = grouped['total_points'].transform(lambda x: x.cumsum().shift(1)).fillna(0)
    df['games_played'] = grouped['minutes'].transform(lambda x: (x > 0).astype(int).cumsum().shift(1)).fillna(0)
    
    # Derived features matching app_with_db.py
    # Note: We map our 'cum_' columns to the names expected by the model (without 'cum_')
    # because the model in app_with_db.py expects 'goals_scored' to mean "Total goals scored so far".
    
    feature_df = pd.DataFrame()
    feature_df['name'] = df['name']
    feature_df['team'] = df['team_x'] if 'team_x' in df.columns else df['team']
    feature_df['position'] = df['position']
    feature_df['value'] = df['value']
    feature_df['target_points'] = df['total_points'] # The points they actually got in this match
    
    # Map cumulative stats to feature names
    for col in cumsum_cols:
        feature_df[col] = df[f'cum_{col}']
        
    feature_df['total_points'] = df['cum_points'] # For feature generation
    
    # Calculate rates
    feature_df['points_per_game'] = feature_df['total_points'] / (df['games_played'] + 1e-6)
    feature_df['points_per_minute'] = feature_df['total_points'] / (feature_df['minutes'] + 1)
    feature_df['goals_per_minute'] = feature_df['goals_scored'] / (feature_df['minutes'] + 1)
    feature_df['assists_per_minute'] = feature_df['assists'] / (feature_df['minutes'] + 1)
    
    # Form (Average points over last 5 games)
    feature_df['form'] = grouped['total_points'].transform(lambda x: x.rolling(window=5, min_periods=1).mean().shift(1)).fillna(0)
    
    # Other features from app_with_db.py
    feature_df['value_per_point'] = feature_df['total_points'] / (feature_df['value'] + 0.1)
    feature_df['form_per_value'] = feature_df['form'] / (feature_df['value'] + 0.1)
    
    # Position flags
    feature_df['is_gk'] = (feature_df['position'] == 'GK').astype(int)
    feature_df['is_def'] = (feature_df['position'] == 'DEF').astype(int)
    feature_df['is_mid'] = (feature_df['position'] == 'MID').astype(int)
    feature_df['is_fwd'] = (feature_df['position'] == 'FWD').astype(int)
    
    # Availability (Assume available for training)
    feature_df['is_available'] = 1
    feature_df['is_injured'] = 0
    feature_df['is_suspended'] = 0
    feature_df['chance_of_playing_next_round'] = 100
    
    # Elo/Strength (Defaults if not in history)
    feature_df['elo_rating'] = 1500
    feature_df['elo_per_value'] = 1500 / (feature_df['value'] + 0.1)
    feature_df['team_strength'] = 3
    feature_df['strength_per_value'] = 3 / (feature_df['value'] + 0.1)
    
    # Transfers
    feature_df['transfers_in'] = df['transfers_in'] if 'transfers_in' in df.columns else 0
    feature_df['transfers_out'] = df['transfers_out'] if 'transfers_out' in df.columns else 0
    feature_df['selected_by_percent'] = df['selected_by_percent'] if 'selected_by_percent' in df.columns else 0
    feature_df['net_transfers'] = feature_df['transfers_in'] - feature_df['transfers_out']
    feature_df['transfer_ratio'] = feature_df['transfers_in'] / (feature_df['transfers_out'] + 1)
    
    # More derived
    feature_df['clean_sheets_per_minute'] = feature_df['clean_sheets'] / (feature_df['minutes'] + 1)
    feature_df['xg_per_minute'] = feature_df['expected_goals'] / (feature_df['minutes'] + 1)
    feature_df['xa_per_minute'] = feature_df['expected_assists'] / (feature_df['minutes'] + 1)
    feature_df['xgi_per_minute'] = feature_df['expected_goal_involvements'] / (feature_df['minutes'] + 1)
    feature_df['ict_per_value'] = feature_df['ict_index'] / (feature_df['value'] + 0.1)
    feature_df['influence_per_minute'] = feature_df['influence'] / (feature_df['minutes'] + 1)
    feature_df['creativity_per_minute'] = feature_df['creativity'] / (feature_df['minutes'] + 1)
    feature_df['threat_per_minute'] = feature_df['threat'] / (feature_df['minutes'] + 1)
    feature_df['ownership_tier'] = 1
    feature_df['form_consistency'] = 1
    
    # Add gameweek for recency weighting
    feature_df['gameweek'] = df['gameweek']
    
    # Drop first row per player (no history)
    feature_df = feature_df[feature_df['minutes'] > 0] # Only train on rows where we have some history? 
    # Actually, shift(1) makes the first row NaNs or 0s.
    # We should drop rows where games_played == 0 if we want robust stats, but maybe 0 is fine.
    
    return feature_df

def calculate_recency_weights(data):
    """
    Calculate sample weights based on recency.
    Recent games are weighted higher to emphasize current form.
    
    Args:
        data: DataFrame with 'gameweek' column
        
    Returns:
        numpy array of sample weights
    """
    max_gw = data['gameweek'].max()
    gw_age = max_gw - data['gameweek']
    
    # Exponential decay: recent games weighted higher
    # Decay factor of 10 means games 10 GWs ago have ~37% weight
    # Games 20 GWs ago have ~14% weight
    weights = np.exp(-gw_age / 10.0)
    
    # Normalize weights to have mean of 1.0
    weights = weights / weights.mean()
    
    logger.info(f"Recency weights - Min: {weights.min():.3f}, Max: {weights.max():.3f}, Mean: {weights.mean():.3f}")
    logger.info(f"Recent 5 GWs avg weight: {weights[gw_age <= 5].mean():.3f}")
    logger.info(f"Older (>20 GWs) avg weight: {weights[gw_age > 20].mean():.3f}")
    
    return weights.values

def train_model():
    # 1. Load Data
    df = load_data()
    logger.info(f"Loaded {len(df)} rows of data")
    
    # 2. Prepare Features
    data = prepare_features(df)
    logger.info(f"Prepared {len(data)} rows for training")
    
    # 3. Encoders
    logger.info("Fitting encoders...")
    team_encoder = LabelEncoder()
    position_encoder = LabelEncoder()
    
    data['team_encoded'] = team_encoder.fit_transform(data['team'].astype(str))
    data['position_encoded'] = position_encoder.fit_transform(data['position'].astype(str))
    
    # Save encoders
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
        
    joblib.dump(team_encoder, os.path.join(MODEL_DIR, 'enhanced_team_encoder.joblib'))
    joblib.dump(position_encoder, os.path.join(MODEL_DIR, 'enhanced_position_encoder.joblib'))
    
    # 4. Define Features
    # Must match enhanced_feature_columns.json exactly
    feature_cols = [
        "value", "form", "points_per_game", "selected_by_percent", "transfers_in", "transfers_out", 
        "chance_of_playing_next_round", "minutes", "goals_scored", "assists", "clean_sheets", 
        "goals_conceded", "saves", "bonus", "bps", "influence", "creativity", "threat", "ict_index", 
        "expected_goals", "expected_assists", "expected_goal_involvements", "expected_goals_conceded", 
        "team_encoded", "position_encoded", "value_per_point", "form_per_value", "points_per_minute", 
        "goals_per_minute", "assists_per_minute", "is_gk", "is_def", "is_mid", "is_fwd", 
        "is_available", "is_injured", "is_suspended", "elo_rating", "elo_per_value", "team_strength", 
        "strength_per_value", "clean_sheets_per_minute", "xg_per_minute", "xa_per_minute", 
        "xgi_per_minute", "ict_per_value", "influence_per_minute", "creativity_per_minute", 
        "threat_per_minute", "net_transfers", "transfer_ratio", "ownership_tier", "form_consistency"
    ]
    
    # Save feature columns
    with open(os.path.join(MODEL_DIR, 'enhanced_feature_columns.json'), 'w') as f:
        json.dump(feature_cols, f)
        
    # 5. Train/Test Split
    X = data[feature_cols].fillna(0)
    y = data['target_points'].fillna(0)
    
    # Calculate recency weights BEFORE split
    sample_weights = calculate_recency_weights(data)
    
    X_train, X_test, y_train, y_test, weights_train, weights_test = train_test_split(
        X, y, sample_weights, test_size=0.2, random_state=42
    )
    
    # 6. Train Model with Recency Weighting
    logger.info("Training Random Forest Regressor with recency weighting...")
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train, sample_weight=weights_train)
    
    # 7. Evaluate
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    
    logger.info(f"Training R2: {train_score:.3f}")
    logger.info(f"Test R2: {test_score:.3f}")
    logger.info(f"Test MAE: {mae:.3f}")
    
    # 8. Save Model
    model_path = os.path.join(MODEL_DIR, 'enhanced_random_forest_model.joblib')
    joblib.dump(model, model_path)
    logger.info(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_model()

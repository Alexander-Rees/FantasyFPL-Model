import requests
import pandas as pd
import numpy as np
import joblib
import json
import os
from pulp import LpMaximize, LpProblem, LpVariable, lpSum

# Constants
FPL_URL = "https://fantasy.premierleague.com/api/bootstrap-static/"
MODEL_DIR = 'models'

def fetch_data():
    print("Fetching data from FPL API...")
    response = requests.get(FPL_URL)
    data = response.json()
    return data

def process_data(data):
    print("Processing data...")
    players = []
    teams = {t['id']: t['name'] for t in data['teams']}
    element_types = {1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD'}
    
    for p in data['elements']:
        player = {
            'id': p['id'],
            'name': p['web_name'],
            'team': teams.get(p['team'], 'Unknown'),
            'position': element_types.get(p['element_type'], 'Unknown'),
            'value': p['now_cost'] / 10.0,
            'form': float(p['form']),
            'points_per_game': float(p['points_per_game']),
            'selected_by_percent': float(p['selected_by_percent']),
            'transfers_in': p['transfers_in_event'],
            'transfers_out': p['transfers_out_event'],
            'chance_of_playing_next_round': p['chance_of_playing_next_round'] if p['chance_of_playing_next_round'] is not None else 100,
            'minutes': p['minutes'],
            'goals_scored': p['goals_scored'],
            'assists': p['assists'],
            'clean_sheets': p['clean_sheets'],
            'goals_conceded': p['goals_conceded'],
            'saves': p['saves'],
            'bonus': p['bonus'],
            'bps': p['bps'],
            'influence': float(p['influence']),
            'creativity': float(p['creativity']),
            'threat': float(p['threat']),
            'ict_index': float(p['ict_index']),
            'expected_goals': float(p['expected_goals']),
            'expected_assists': float(p['expected_assists']),
            'expected_goal_involvements': float(p['expected_goal_involvements']),
            'expected_goals_conceded': float(p['expected_goals_conceded']),
            'total_points': p['total_points'],
            'status': p['status']
        }
        players.append(player)
        
    return pd.DataFrame(players)

def generate_features(df):
    print("Generating features...")
    df = df.copy()
    
    # Load encoders
    team_encoder = joblib.load(os.path.join(MODEL_DIR, 'enhanced_team_encoder.joblib'))
    position_encoder = joblib.load(os.path.join(MODEL_DIR, 'enhanced_position_encoder.joblib'))
    
    # Encode
    # Handle new teams/positions if any (though unlikely in season)
    # We use a safe transform or just map knowns
    try:
        df['team_encoded'] = team_encoder.transform(df['team'])
    except ValueError:
        # Fallback for unknown teams (shouldn't happen with standard data)
        print("Warning: Unknown teams found, using 0")
        df['team_encoded'] = 0
        
    df['position_encoded'] = position_encoder.transform(df['position'])
    
    # Derived features
    df['value_per_point'] = df['total_points'] / (df['value'] + 0.1)
    df['form_per_value'] = df['form'] / (df['value'] + 0.1)
    df['points_per_minute'] = df['total_points'] / (df['minutes'] + 1)
    df['goals_per_minute'] = df['goals_scored'] / (df['minutes'] + 1)
    df['assists_per_minute'] = df['assists'] / (df['minutes'] + 1)
    
    df['is_gk'] = (df['position'] == 'GK').astype(int)
    df['is_def'] = (df['position'] == 'DEF').astype(int)
    df['is_mid'] = (df['position'] == 'MID').astype(int)
    df['is_fwd'] = (df['position'] == 'FWD').astype(int)
    
    df['is_available'] = (df['status'] == 'a').astype(int)
    df['is_injured'] = (df['status'] == 'i').astype(int)
    df['is_suspended'] = (df['status'] == 's').astype(int)
    
    # Defaults for missing data in live feed vs training
    df['elo_rating'] = 1500
    df['elo_per_value'] = 1500 / (df['value'] + 0.1)
    df['team_strength'] = 3
    df['strength_per_value'] = 3 / (df['value'] + 0.1)
    
    df['clean_sheets_per_minute'] = df['clean_sheets'] / (df['minutes'] + 1)
    df['xg_per_minute'] = df['expected_goals'] / (df['minutes'] + 1)
    df['xa_per_minute'] = df['expected_assists'] / (df['minutes'] + 1)
    df['xgi_per_minute'] = df['expected_goal_involvements'] / (df['minutes'] + 1)
    df['ict_per_value'] = df['ict_index'] / (df['value'] + 0.1)
    df['influence_per_minute'] = df['influence'] / (df['minutes'] + 1)
    df['creativity_per_minute'] = df['creativity'] / (df['minutes'] + 1)
    df['threat_per_minute'] = df['threat'] / (df['minutes'] + 1)
    df['net_transfers'] = df['transfers_in'] - df['transfers_out']
    df['transfer_ratio'] = df['transfers_in'] / (df['transfers_out'] + 1)
    df['ownership_tier'] = 1
    df['form_consistency'] = 1
    
    return df

def predict():
    # 1. Fetch
    raw_data = fetch_data()
    df = process_data(raw_data)
    
    # 2. Features
    df_features = generate_features(df)
    
    # 3. Load Model
    print("Loading model...")
    model = joblib.load(os.path.join(MODEL_DIR, 'enhanced_random_forest_model.joblib'))
    
    # 4. Predict
    with open(os.path.join(MODEL_DIR, 'enhanced_feature_columns.json'), 'r') as f:
        feature_cols = json.load(f)
        
    X = df_features[feature_cols].fillna(0)
    predictions = model.predict(X)
    
    df['predicted_points'] = predictions
    
    # Save predictions to CSV
    df[['name', 'team', 'position', 'value', 'predicted_points', 'minutes', 'total_points']].sort_values('predicted_points', ascending=False).to_csv('predictions.csv', index=False)
    print("Predictions saved to predictions.csv")
    
    # Save to Database
    print("Saving predictions to Database...")
    try:
        import psycopg2
        
        # DB Config (same as check_db.py)
        DB_CONFIG = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'postgres'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD'),
            'port': int(os.getenv('DB_PORT', '5432'))
        }
        
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Update batch
        update_query = "UPDATE player SET predicted_points = %s WHERE fpl_id = %s"
        data_to_update = []
        
        for _, row in df.iterrows():
            # Filter: Only save positive prediction if minutes >= 90 and chance >= 75
            # Otherwise set to 0 to avoid polluting UI with outliers
            pred_points = row['predicted_points']
            if row['minutes'] < 90 or row['chance_of_playing_next_round'] < 75:
                pred_points = 0.0
                
            data_to_update.append((pred_points, row['id']))
            
        cursor.executemany(update_query, data_to_update)
        conn.commit()
        print(f"Successfully updated {len(data_to_update)} players in DB")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error saving to DB: {e}")
        print("Ensure DB is running and V4 migration has been applied.")

    # Debug: Inspect top 5 predictions
    print("\nTop 5 Predictions (Debug):")
    print(df[['name', 'minutes', 'total_points', 'predicted_points']].sort_values('predicted_points', ascending=False).head(5))
    
    return df

def optimize(df):
    print("\nOptimizing Team...")
    
    # Filter unavailable players
    df = df[df['status'] == 'a']
    
    # Filter low-minute players (User Feedback)
    # We want players who play regularly.
    # Let's require at least 90 minutes total (1 full game equivalent) 
    # AND chance_of_playing_next_round > 75
    print(f"Pre-filter count: {len(df)}")
    df = df[df['minutes'] >= 90]
    df = df[df['chance_of_playing_next_round'] >= 75]
    print(f"Post-filter count: {len(df)}")
    
    players = df.to_dict('records')
    
    # Problem
    prob = LpProblem("FPL_Team", LpMaximize)
    
    # Variables
    player_vars = LpVariable.dicts("Player", [p['id'] for p in players], cat='Binary')
    
    # Objective
    prob += lpSum([p['predicted_points'] * player_vars[p['id']] for p in players])
    
    # Constraints
    # 1. Squad Size = 15
    prob += lpSum([player_vars[p['id']] for p in players]) == 15
    
    # 2. Budget = 100
    prob += lpSum([p['value'] * player_vars[p['id']] for p in players]) <= 100
    
    # 3. Positions
    prob += lpSum([player_vars[p['id']] for p in players if p['position'] == 'GK']) == 2
    prob += lpSum([player_vars[p['id']] for p in players if p['position'] == 'DEF']) == 5
    prob += lpSum([player_vars[p['id']] for p in players if p['position'] == 'MID']) == 5
    prob += lpSum([player_vars[p['id']] for p in players if p['position'] == 'FWD']) == 3
    
    # 4. Max 3 per team
    teams = set(p['team'] for p in players)
    for t in teams:
        prob += lpSum([player_vars[p['id']] for p in players if p['team'] == t]) <= 3
        
    # Solve
    prob.solve()
    
    # Extract
    selected = [p for p in players if player_vars[p['id']].varValue == 1]
    
    # Pick Starting XI (Top 11 by points, valid formation)
    selected.sort(key=lambda x: x['predicted_points'], reverse=True)
    
    # Simple heuristic for Starting XI:
    # Must have 1 GK, at least 3 DEF, at least 1 FWD.
    # We'll just take the best 1 GK and best 10 others who fit a formation?
    # Actually, let's just list the squad.
    
    print(f"Optimal Squad (Total Predicted: {sum(p['predicted_points'] for p in selected):.2f})")
    print(f"Cost: {sum(p['value'] for p in selected):.1f}m")
    
    for p in selected:
        print(f"{p['position']} {p['name']} ({p['team']}) - £{p['value']}m - Pred: {p['predicted_points']:.2f}")

if __name__ == "__main__":
    df = predict()
    optimize(df)

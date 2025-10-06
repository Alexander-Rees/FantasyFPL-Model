"""
FPL Team Optimization API with MySQL Database Integration
=======================================================

A comprehensive Fantasy Premier League team optimization API using enhanced ML models,
FPL-Elo-Insights data, and MySQL database for user management and data persistence.

Features:
- Real-time FPL data integration
- Enhanced ML model with Elo-Insights data
- MySQL database integration
- User authentication and management
- Team management with persistence
- Transfer suggestions
- Fixture analysis

Author: FPL Optimization Team
Version: 3.0.0
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import pandas as pd
import numpy as np
import joblib
import json
from pulp import LpMaximize, LpProblem, LpVariable, lpSum
import time
import logging
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import hashlib
import jwt
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'fantasy_soccer',
    'user': 'root',
    'password': 'NewPassword',
    'port': 3306
}

# FPL API Configuration
class Config:
    FPL_BASE_URL = 'https://fantasy.premierleague.com/api'
    FPL_STATIC_URL = f'{FPL_BASE_URL}/bootstrap-static/'
    FPL_FIXTURES_URL = f'{FPL_BASE_URL}/fixtures/'
    FPL_LIVE_URL = f'{FPL_BASE_URL}/event/{{}}/live/'
    FPL_PLAYER_HISTORY_URL = f'{FPL_BASE_URL}/element-summary/{{}}/'
    REQUEST_TIMEOUT = 15
    MODEL_PATH = 'models/enhanced_random_forest_model.joblib'
    TEAM_ENCODER_PATH = 'models/enhanced_team_encoder.joblib'
    POSITION_ENCODER_PATH = 'models/enhanced_position_encoder.joblib'
    FEATURE_COLUMNS_PATH = 'models/enhanced_feature_columns.json'

app.config.from_object(Config)

# Global variables for ML model
ml_model = None
team_encoder = None
position_encoder = None
feature_columns = []

def get_db_connection():
    """Get MySQL database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        logger.error(f"Error connecting to MySQL: {e}")
        return None

def load_ml_model():
    """Load the enhanced ML model and encoders"""
    global ml_model, team_encoder, position_encoder, feature_columns
    
    try:
        ml_model = joblib.load(app.config['MODEL_PATH'])
        team_encoder = joblib.load(app.config['TEAM_ENCODER_PATH'])
        position_encoder = joblib.load(app.config['POSITION_ENCODER_PATH'])
        
        with open(app.config['FEATURE_COLUMNS_PATH'], 'r') as f:
            feature_columns = json.load(f)
        
        logger.info("✅ Enhanced ML Model loaded successfully!")
        logger.info(f"📊 Model features: {len(feature_columns)}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error loading ML model: {e}")
        return False

def fetch_fpl_data(endpoint, timeout=None):
    """Fetch data from FPL API with error handling"""
    try:
        response = requests.get(endpoint, timeout=timeout or app.config['REQUEST_TIMEOUT'], verify=False)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"FPL API error: {response.status_code}")
            return None
    except requests.exceptions.Timeout:
        logger.error("FPL API timeout")
        return None
    except Exception as e:
        logger.error(f"FPL API request failed: {e}")
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
            'event_points': player['event_points'],
            'form': player.get('form', 0),
            'points_per_game': player.get('points_per_game', 0),
            'selected_by_percent': player.get('selected_by_percent', 0),
            'transfers_in': player.get('transfers_in_event', 0),
            'transfers_out': player.get('transfers_out_event', 0),
            'in_dreamteam': player.get('in_dreamteam', False),
            'status': player.get('status', 'a'),
            'chance_of_playing_next_round': player.get('chance_of_playing_next_round', 100),
            'news': player.get('news', ''),
            'minutes': player.get('minutes', 0),
            'goals_scored': player.get('goals_scored', 0),
            'assists': player.get('assists', 0),
            'clean_sheets': player.get('clean_sheets', 0),
            'goals_conceded': player.get('goals_conceded', 0),
            'saves': player.get('saves', 0),
            'bonus': player.get('bonus', 0),
            'bps': player.get('bps', 0),
            'influence': player.get('influence', 0),
            'creativity': player.get('creativity', 0),
            'threat': player.get('threat', 0),
            'ict_index': player.get('ict_index', 0),
            'expected_goals': player.get('expected_goals', 0),
            'expected_assists': player.get('expected_assists', 0),
            'expected_goal_involvements': player.get('expected_goal_involvements', 0),
            'expected_goals_conceded': player.get('expected_goals_conceded', 0)
        }
        enhanced_players.append(enhanced_player)
    
    return enhanced_players

def create_ml_features(df):
    """Create ML features for prediction"""
    df_features = df.copy()
    
    # Encode categorical variables
    df_features['team_encoded'] = team_encoder.transform(df_features['team'])
    df_features['position_encoded'] = position_encoder.transform(df_features['position'])
    
    # Create additional features
    df_features['value_per_point'] = pd.to_numeric(df_features['total_points'], errors='coerce') / (pd.to_numeric(df_features['value'], errors='coerce') + 0.1)
    df_features['form_per_value'] = pd.to_numeric(df_features['form'], errors='coerce') / (pd.to_numeric(df_features['value'], errors='coerce') + 0.1)
    df_features['points_per_minute'] = pd.to_numeric(df_features['total_points'], errors='coerce') / (pd.to_numeric(df_features['minutes'], errors='coerce') + 1)
    df_features['goals_per_minute'] = pd.to_numeric(df_features['goals_scored'], errors='coerce') / (pd.to_numeric(df_features['minutes'], errors='coerce') + 1)
    df_features['assists_per_minute'] = pd.to_numeric(df_features['assists'], errors='coerce') / (pd.to_numeric(df_features['minutes'], errors='coerce') + 1)
    
    # Position-specific features
    df_features['is_gk'] = (df_features['position'] == 'GK').astype(int)
    df_features['is_def'] = (df_features['position'] == 'DEF').astype(int)
    df_features['is_mid'] = (df_features['position'] == 'MID').astype(int)
    df_features['is_fwd'] = (df_features['position'] == 'FWD').astype(int)
    
    # Availability features
    df_features['is_available'] = (df_features['status'] == 'a').astype(int)
    df_features['is_injured'] = (df_features['status'] == 'i').astype(int)
    df_features['is_suspended'] = (df_features['status'] == 's').astype(int)
    
    # Elo and team strength features (using defaults for real-time data)
    df_features['elo_rating'] = 1500
    df_features['elo_per_value'] = 1500 / (df_features['value'] + 0.1)
    df_features['team_strength'] = 3
    df_features['strength_per_value'] = 3 / (df_features['value'] + 0.1)
    
    # Additional features
    df_features['clean_sheets_per_minute'] = df_features['clean_sheets'] / (df_features['minutes'] + 1)
    df_features['xg_per_minute'] = df_features['expected_goals'] / (df_features['minutes'] + 1)
    df_features['xa_per_minute'] = df_features['expected_assists'] / (df_features['minutes'] + 1)
    df_features['xgi_per_minute'] = df_features['expected_goal_involvements'] / (df_features['minutes'] + 1)
    df_features['ict_per_value'] = df_features['ict_index'] / (df_features['value'] + 0.1)
    df_features['influence_per_minute'] = df_features['influence'] / (df_features['minutes'] + 1)
    df_features['creativity_per_minute'] = df_features['creativity'] / (df_features['minutes'] + 1)
    df_features['threat_per_minute'] = df_features['threat'] / (df_features['minutes'] + 1)
    df_features['net_transfers'] = df_features['transfers_in'] - df_features['transfers_out']
    df_features['transfer_ratio'] = df_features['transfers_in'] / (df_features['transfers_out'] + 1)
    df_features['ownership_tier'] = 1
    df_features['form_consistency'] = 1
    
    return df_features

def token_required(f):
    """Decorator to require JWT token for protected routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(current_user_id, *args, **kwargs)
    return decorated

# Authentication Endpoints

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        
        if not all([name, email, password]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Hash password securely
        password_hash = generate_password_hash(password)
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT id FROM user WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({'error': 'User already exists'}), 400
        
        # Insert new user
        cursor.execute(
            "INSERT INTO user (name, email, password) VALUES (%s, %s, %s)",
            (name, email, password_hash)
        )
        connection.commit()
        
        user_id = cursor.lastrowid
        cursor.close()
        connection.close()
        
        # Generate JWT token
        token = jwt.encode(
            {'user_id': user_id, 'email': email},
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        
        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'user_id': user_id
        }), 201
        
    except Exception as e:
        logger.error(f"Error in register: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not all([email, password]):
            return jsonify({'error': 'Missing email or password'}), 400
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, name, email, password FROM user WHERE email = %s",
            (email,)
        )
        user = cursor.fetchone()
        
        if not user or not check_password_hash(user['password'], password):
            cursor.close()
            connection.close()
            return jsonify({'error': 'Invalid credentials'}), 401
        
        cursor.close()
        connection.close()
        
        # Generate JWT token
        token = jwt.encode(
            {'user_id': user['id'], 'email': user['email']},
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user
        }), 200
        
    except Exception as e:
        logger.error(f"Error in login: {e}")
        return jsonify({'error': str(e)}), 500

# Team Management Endpoints

@app.route('/api/team', methods=['GET'])
@token_required
def get_user_team(current_user_id):
    """Get user's team"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        
        # Get team info
        cursor.execute("""
            SELECT t.id, t.name, t.budget, t.created_at, t.updated_at
            FROM team t 
            WHERE t.user_id = %s
        """, (current_user_id,))
        team = cursor.fetchone()
        
        if not team:
            return jsonify({'error': 'Team not found'}), 404
        
        # Get team players
        cursor.execute("""
            SELECT p.id, p.name, p.team, p.position, p.value, p.total_points
            FROM player p
            JOIN team_players tp ON p.id = tp.player_id
            WHERE tp.team_id = %s
        """, (team['id'],))
        players = cursor.fetchall()
        
        team['players'] = players
        cursor.close()
        connection.close()
        
        return jsonify(team), 200
        
    except Exception as e:
        logger.error(f"Error in get_user_team: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/team', methods=['POST'])
@token_required
def create_team(current_user_id):
    """Create a new team for user"""
    try:
        data = request.get_json()
        team_name = data.get('name', f"Team {current_user_id}")
        budget = data.get('budget', 100.0)
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor()
        
        # Check if user already has a team
        cursor.execute("SELECT id FROM team WHERE user_id = %s", (current_user_id,))
        if cursor.fetchone():
            return jsonify({'error': 'User already has a team'}), 400
        
        # Create team
        cursor.execute(
            "INSERT INTO team (user_id, name, budget) VALUES (%s, %s, %s)",
            (current_user_id, team_name, budget)
        )
        team_id = cursor.lastrowid
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'message': 'Team created successfully',
            'team_id': team_id
        }), 201
        
    except Exception as e:
        logger.error(f"Error in create_team: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/team/players', methods=['POST'])
@token_required
def add_player_to_team(current_user_id):
    """Add player to user's team"""
    try:
        data = request.get_json()
        player_id = data.get('player_id')
        
        if not player_id:
            return jsonify({'error': 'Player ID required'}), 400
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor()
        
        # Get user's team
        cursor.execute("SELECT id FROM team WHERE user_id = %s", (current_user_id,))
        team = cursor.fetchone()
        if not team:
            return jsonify({'error': 'Team not found'}), 404
        
        team_id = team[0]
        
        # Check if player is already in team
        cursor.execute(
            "SELECT id FROM team_players WHERE team_id = %s AND player_id = %s",
            (team_id, player_id)
        )
        if cursor.fetchone():
            return jsonify({'error': 'Player already in team'}), 400
        
        # Add player to team
        cursor.execute(
            "INSERT INTO team_players (team_id, player_id) VALUES (%s, %s)",
            (team_id, player_id)
        )
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return jsonify({'message': 'Player added to team successfully'}), 200
        
    except Exception as e:
        logger.error(f"Error in add_player_to_team: {e}")
        return jsonify({'error': str(e)}), 500

# FPL Data Endpoints (same as before but with database integration)

@app.route('/')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'message': 'FPL Team Optimization API with MySQL Database',
        'status': 'healthy',
        'version': '3.0.0',
        'model_loaded': ml_model is not None,
        'model_type': 'Enhanced Random Forest with Elo-Insights',
        'features': len(feature_columns),
        'database_connected': get_db_connection() is not None,
        'timestamp': datetime.now().isoformat(),
        'endpoints': {
            'auth_register': '/api/auth/register',
            'auth_login': '/api/auth/login',
            'team': '/api/team',
            'players': '/api/players',
            'predictions': '/api/predictions',
            'optimize': '/api/optimize',
            'transfers': '/api/transfers',
            'fixtures': '/api/fixtures'
        }
    })

@app.route('/api/players', methods=['GET'])
def get_players():
    """Get all FPL players with current data"""
    try:
        logger.info("Fetching FPL players data...")
        
        static_data = fetch_fpl_data(app.config['FPL_STATIC_URL'])
        if not static_data:
            return jsonify({"error": "Failed to fetch FPL data"}), 500
        
        players = process_player_data(static_data)
        current_gw = next((event for event in static_data['events'] if event['is_current']), None)
        
        result = {
            'current_gameweek': current_gw,
            'players': players,
            'total_players': len(players),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Successfully fetched {len(players)} players")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in get_players: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    """Get ML predictions for all players"""
    try:
        if not ml_model:
            return jsonify({'error': 'ML model not loaded'}), 500
        
        logger.info("Generating player predictions...")
        
        static_data = fetch_fpl_data(app.config['FPL_STATIC_URL'])
        if not static_data:
            return jsonify({"error": "Failed to fetch FPL data"}), 500
        
        players = process_player_data(static_data)
        df = pd.DataFrame(players)
        
        # Create ML features
        df_features = create_ml_features(df)
        
        # Prepare features for prediction
        X = df_features[feature_columns].fillna(0)
        
        # Generate predictions
        predictions = ml_model.predict(X)
        
        # Add predictions to player data
        for i, player in enumerate(players):
            player['predicted_points'] = float(predictions[i])
            player['value_per_predicted_point'] = player['value'] / (predictions[i] + 0.1)
        
        # Sort by predicted points
        players.sort(key=lambda x: x['predicted_points'], reverse=True)
        
        result = {
            'players': players,
            'total_players': len(players),
            'model_type': 'Enhanced Random Forest with Elo-Insights',
            'top_predictions': players[:10],
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Generated predictions for {len(players)} players")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in get_predictions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/optimize', methods=['POST'])
@token_required
def optimize_team(current_user_id):
    """Optimize team using ML predictions and constraints"""
    try:
        if not ml_model:
            return jsonify({'error': 'ML model not loaded'}), 500
        
        data = request.get_json()
        budget = data.get('budget', 100.0)
        free_transfers = data.get('free_transfers', 1)
        
        logger.info(f"Optimizing team for user {current_user_id} - budget: {budget}, transfers: {free_transfers}")
        
        # Get player predictions
        predictions_response = get_predictions()
        if predictions_response[1] != 200:
            return predictions_response
        
        players_data = predictions_response[0].json['players']
        
        # Create optimization problem
        problem = LpProblem("FPL_Team_Optimization", LpMaximize)
        
        # Create binary variables for each player
        player_vars = {}
        for player in players_data:
            player_vars[player['id']] = LpVariable(f"player_{player['id']}", cat='Binary')
        
        # Objective: Maximize predicted points
        problem += lpSum([player_vars[player['id']] * player['predicted_points'] for player in players_data])
        
        # Position constraints
        gk_players = [p for p in players_data if p['position'] == 'GK']
        def_players = [p for p in players_data if p['position'] == 'DEF']
        mid_players = [p for p in players_data if p['position'] == 'MID']
        fwd_players = [p for p in players_data if p['position'] == 'FWD']
        
        problem += lpSum([player_vars[p['id']] for p in gk_players]) == 2  # 2 goalkeepers
        problem += lpSum([player_vars[p['id']] for p in def_players]) == 5  # 5 defenders
        problem += lpSum([player_vars[p['id']] for p in mid_players]) == 5  # 5 midfielders
        problem += lpSum([player_vars[p['id']] for p in fwd_players]) == 3  # 3 forwards
        
        # Budget constraint
        problem += lpSum([player_vars[player['id']] * player['value'] for player in players_data]) <= budget
        
        # Team limit constraint (max 3 players per team)
        teams = list(set([p['team'] for p in players_data]))
        for team in teams:
            team_players = [p for p in players_data if p['team'] == team]
            problem += lpSum([player_vars[p['id']] for p in team_players]) <= 3
        
        # Solve the problem
        problem.solve()
        
        # Get selected players
        selected_players = []
        for player in players_data:
            if player_vars[player['id']].varValue > 0.5:
                selected_players.append(player)
        
        # Calculate team stats
        total_value = sum(p['value'] for p in selected_players)
        total_predicted_points = sum(p['predicted_points'] for p in selected_players)
        
        result = {
            'selected_team': selected_players,
            'total_value': total_value,
            'total_predicted_points': total_predicted_points,
            'budget_remaining': budget - total_value,
            'optimization_status': 'optimal' if problem.status == 1 else 'suboptimal',
            'model_type': 'Enhanced Random Forest with Elo-Insights',
            'constraints': {
                'budget': budget,
                'free_transfers': free_transfers,
                'position_limits': {'GK': 2, 'DEF': 5, 'MID': 5, 'FWD': 3},
                'team_limit': 3
            },
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Team optimization completed: {len(selected_players)} players, {total_value:.1f}M value, {total_predicted_points:.1f} predicted points")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in optimize_team: {e}")
        return jsonify({'error': str(e)}), 500

# ML Optimization endpoint for Spring Boot
@app.route('/_ml/optimize', methods=['POST'])
def ml_optimize():
    """
    Internal ML optimization endpoint called by Spring Boot
    """
    try:
        data = request.get_json()
        
        # Extract data from Spring Boot request
        players = data.get('players', [])
        current_team = data.get('current_team', [])
        budget = data.get('budget', 100.0)
        free_transfers = data.get('free_transfers', 1)
        locked_players = data.get('locked_players', [])
        avoid_players = data.get('avoid_players', [])
        formation = data.get('formation', '3-4-3')
        
        logger.info(f"ML optimization request: {len(players)} players, budget: {budget}, transfers: {free_transfers}")
        
        # Convert to DataFrame for optimization
        df = pd.DataFrame(players)
        if df.empty:
            return jsonify({'error': 'No players provided'}), 400
        
        # Basic optimization logic (simplified for now)
        # In a real implementation, this would use the trained ML model
        optimal_team = []
        bench = []
        
        # Simple selection based on total points and value
        df_sorted = df.sort_values(['total_points', 'value'], ascending=[False, True])
        
        # Select by position based on formation
        formation_map = {
            '3-4-3': {'GK': 1, 'DEF': 3, 'MID': 4, 'FWD': 3},
            '3-5-2': {'GK': 1, 'DEF': 3, 'MID': 5, 'FWD': 2},
            '4-4-2': {'GK': 1, 'DEF': 4, 'MID': 4, 'FWD': 2},
            '4-3-3': {'GK': 1, 'DEF': 4, 'MID': 3, 'FWD': 3},
            '5-4-1': {'GK': 1, 'DEF': 5, 'MID': 4, 'FWD': 1}
        }
        
        position_limits = formation_map.get(formation, {'GK': 1, 'DEF': 3, 'MID': 4, 'FWD': 3})
        
        # Select optimal team
        for position, limit in position_limits.items():
            position_players = df_sorted[df_sorted['position'] == position].head(limit)
            for _, player in position_players.iterrows():
                optimal_team.append(player.to_dict())
        
        # Select bench (remaining players)
        selected_ids = [p['id'] for p in optimal_team]
        bench_players = df_sorted[~df_sorted['id'].isin(selected_ids)].head(4)
        for _, player in bench_players.iterrows():
            bench.append(player.to_dict())
        
        # Select captain and vice-captain
        captain = max(optimal_team, key=lambda x: x['total_points'])
        vice_captain = max([p for p in optimal_team if p['id'] != captain['id']], 
                          key=lambda x: x['total_points'], default=captain)
        
        # Calculate totals
        total_value = sum(p['value'] for p in optimal_team)
        total_points = sum(p['total_points'] for p in optimal_team)
        
        # Generate transfer suggestions (simplified)
        transfers = []
        if free_transfers > 0 and current_team:
            # Simple transfer logic: suggest replacing lowest scoring players
            current_team_sorted = sorted(current_team, key=lambda x: x['total_points'])
            for i in range(min(free_transfers, len(current_team_sorted))):
                player_out = current_team_sorted[i]
                # Find better replacement
                better_players = [p for p in optimal_team 
                                if p['position'] == player_out['position'] 
                                and p['total_points'] > player_out['total_points']]
                if better_players:
                    player_in = better_players[0]
                    transfers.append({
                        'player_out': player_out,
                        'player_in': player_in,
                        'cost': player_in['value'] - player_out['value'],
                        'reason': f"Upgrade from {player_out['total_points']} to {player_in['total_points']} points"
                    })
        
        result = {
            'optimal_team': optimal_team,
            'bench': bench,
            'captain': captain,
            'vice_captain': vice_captain,
            'transfers': transfers,
            'total_value': total_value,
            'total_points': total_points,
            'formation': formation
        }
        
        logger.info(f"ML optimization completed: {len(optimal_team)} players, {total_value:.1f}M value")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in ML optimization: {e}")
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Initialize the app
if __name__ == '__main__':
    # Load ML model on startup
    if load_ml_model():
        logger.info("🚀 FPL Team Optimization API with MySQL starting...")
        app.run(debug=True, host='0.0.0.0', port=5001)
    else:
        logger.error("❌ Failed to load ML model. API cannot start.")
from flask import Flask, jsonify
import requests
import pandas as pd
import numpy as np
import joblib
from pulp import LpMaximize, LpProblem, LpVariable, lpSum

app = Flask(__name__)

# Load the model and dataset
model = joblib.load('../model-files/random_forest_model.joblib')  # Adjust the path as needed
df_2024_25 = pd.read_pickle('../model-files/df_2024_25.pkl')

# Function to find the optimal team using PuLP
def find_optimal_team(df):
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].replace([np.inf, -np.inf], 0)

    # Initialize the optimization problem
    problem = LpProblem("FPL_Team_Selection", LpMaximize)
    df['is_selected'] = pd.Series(LpVariable.dicts("is_selected", df.index, cat='Binary'))

    # Objective: Maximize the total predicted points
    problem += lpSum(df['is_selected'][i] * df['predicted_points'][i] for i in df.index)

    # Position constraints
    problem += lpSum(df['is_selected'][i] for i in df.index if df['position'][i] == 'GK') == 2
    problem += lpSum(df['is_selected'][i] for i in df.index if df['position'][i] == 'DEF') == 5
    problem += lpSum(df['is_selected'][i] for i in df.index if df['position'][i] == 'MID') == 5
    problem += lpSum(df['is_selected'][i] for i in df.index if df['position'][i] == 'FWD') == 3

    # Budget constraint
    problem += lpSum(df['is_selected'][i] * df['value'][i] for i in df.index) <= 100

    # No more than 3 players from the same team
    teams = df['team_x'].unique()
    for team in teams:
        problem += lpSum(df['is_selected'][i] for i in df.index if df['team_x'][i] == team) <= 3

    # Solve the problem
    problem.solve()

    # Get the selected players
    selected_players = df[df['is_selected'].apply(lambda x: x.varValue > 0.5)]
    return selected_players[['name', 'position', 'team_x', 'value', 'predicted_points']].to_dict(orient='records')

# Route to get the optimal team
@app.route('/optimal_team', methods=['GET'])
def optimal_team():
    selected_team = find_optimal_team(df_2024_25)
    return jsonify(selected_team)

# Route to get top players by position
@app.route('/top_players', methods=['GET'])
def top_players():
    top_players = {}
    positions = ['GK', 'DEF', 'MID', 'FWD']

    for pos in positions:
        top_players[pos] = df_2024_25[df_2024_25['position'] == pos].nlargest(10, 'predicted_points')[['name', 'position', 'team_x', 'predicted_points']].to_dict(orient='records')

    return jsonify(top_players)

# Route to fetch all player data (cumulative season data)
@app.route('/fetch_player_data', methods=['GET'])
def fetch_player_data():
    fpl_url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    response = requests.get(fpl_url, verify=False)


    if response.status_code == 200:
        data = response.json()

        # Extract relevant player data (this is customizable based on what you need)
        players_data = data['elements']
        extracted_players = []
        for player in players_data:
            extracted_players.append({
                'id': player['id'],
                'name': player['web_name'],
                'team': player['team'],
                'total_points': player['total_points'],
                'position': player['element_type'],
                'value': player['now_cost'] / 10,  # 'now_cost' is in tenths of a million
                'minutes': player['minutes'],
                'goals_scored': player['goals_scored'],
                'assists': player['assists']
                # Add other fields you might need
            })

        return jsonify(extracted_players)
    else:
        return jsonify({"error": "Failed to fetch player data"}), response.status_code

# Route to fetch last gameweek data for all players
@app.route('/fetch_weekly_data/<int:gameweek_id>', methods=['GET'])
def fetch_weekly_data(gameweek_id):
    # Get live data for a specific gameweek
    fpl_live_url = f'https://fantasy.premierleague.com/api/event/{gameweek_id}/live/'
    live_response = requests.get(fpl_live_url, verify=False)

    # Get static player data (to map player names and teams)
    fpl_static_url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    static_response = requests.get(fpl_static_url, verify=False)

    if live_response.status_code == 200 and static_response.status_code == 200:
        live_data = live_response.json()
        static_data = static_response.json()

        # Create a lookup for player names and teams
        players_static_info = {player['id']: {
            'name': player['web_name'],
            'team': player['team'],
            'position': player['element_type'],
            'value': player['now_cost'] / 10  # 'now_cost' is in tenths of a million
        } for player in static_data['elements']}

        # Extract gameweek performance data and combine with player info
        weekly_player_data = []
        for player in live_data['elements']:
            player_id = player['id']
            if player_id in players_static_info:
                player_info = players_static_info[player_id]
                player_stats = player['stats']

                weekly_player_data.append({
                    'id': player_id,
                    'name': player_info['name'],
                    'team': player_info['team'],
                    'position': player_info['position'],
                    'value': player_info['value'],
                    'minutes': player_stats['minutes'],
                    'goals_scored': player_stats['goals_scored'],
                    'assists': player_stats['assists'],
                    'total_points': player_stats['total_points']
                    # You can add more stats here as needed
                })

        return jsonify(weekly_player_data)

    else:
        return jsonify({"error": "Failed to fetch data"}), live_response.status_code


if __name__ == '__main__':
    app.run(debug=True)
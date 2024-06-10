import requests
import joblib
import pandas as pd
import numpy as np

# Load the model and preprocessors
model = joblib.load('baseball_model.pkl')
imputer = joblib.load('imputer.pkl')
scaler = joblib.load('scaler.pkl')
encoder = joblib.load('encoder.pkl')


def fetch_schedule(date):
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('dates', [])[0].get('games', [])
    return []


def fetch_lineup(game_id):
    url = f"https://statsapi.mlb.com/api/v1.1/game/{game_id}/feed/live"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('liveData', {}).get('boxscore', {}).get('teams', {})
    return {}


def get_starting_pitcher(players):
    for player_id, player in players.items():
        if player['position']['abbreviation'] == 'P':
            return player['person']['fullName'], player['person']['id']
    return "N/A", "N/A"


def get_lineup(players):
    lineup = []
    for player_id, player in players.items():
        if 'battingOrder' in player:
            lineup.append({
                'id': player['person']['id'],
                'name': player['person']['fullName'],
                'position': player['position']['abbreviation'],
                'battingOrder': player['battingOrder']
            })
    lineup.sort(key=lambda x: int(x['battingOrder']))
    return lineup


def print_lineup_data(lineup_data, team_type):
    team = lineup_data[team_type]
    team_name = team['team']['name']
    print(f"\n{team_name} lineup:")

    pitcher_name, pitcher_id = get_starting_pitcher(team['players'])
    print(f"Starting Pitcher: {pitcher_name} (ID: {pitcher_id})")

    lineup = get_lineup(team['players'])
    for player in lineup:
        print(f"{player['name']} (ID: {player['id']}) - {player['position']} - Batting Order: {player['battingOrder']}")


def prepare_data_for_prediction(lineup_data):
    # This function should extract and preprocess features for prediction
    # For demonstration, we return dummy data
    return pd.DataFrame({
        'total_strikeouts': [10],
        'total_walks': [5],
        'total_hits': [12],
        'total_home_runs': [3]
    })


def main():
    date = '2024-06-09'  # Set the date you want to test
    games = fetch_schedule(date)

    if games:
        for game in games:
            game_id = game['gamePk']
            home_team = game['teams']['home']['team']['name']
            away_team = game['teams']['away']['team']['name']
            print(f"\nGame ID: {game_id}")
            print(f"{home_team} vs {away_team}")

            lineup_data = fetch_lineup(game_id)
            if lineup_data:
                print_lineup_data(lineup_data, 'home')
                print_lineup_data(lineup_data, 'away')

                # Prepare data for prediction
                X_new = prepare_data_for_prediction(lineup_data)

                # Impute missing values and scale the features
                X_new = imputer.transform(X_new)
                X_new = scaler.transform(X_new)

                # Make prediction
                prediction = model.predict(X_new)
                result = encoder.inverse_transform(prediction)
                print(f"Predicted result: {'Home win' if result[0] == 1 else 'Away win'}")


if __name__ == "__main__":
    main()

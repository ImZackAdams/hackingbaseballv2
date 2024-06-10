import pandas as pd
import sqlite3
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
from flask import Flask, request, jsonify
import numpy as np
import requests
import json
import os


# Function to fetch schedule
def fetch_schedule(date):
    schedule_url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date}"
    schedule_response = requests.get(schedule_url)
    if schedule_response.status_code == 200:
        schedule_data = schedule_response.json()
        games = schedule_data.get('dates', [])[0].get('games', [])
        return games
    else:
        print(f"Failed to fetch schedule data: {schedule_response.status_code}")
        return None


# Function to fetch lineup
def fetch_lineup(game_id):
    lineup_url = f"https://statsapi.mlb.com/api/v1/game/{game_id}/boxscore"
    lineup_response = requests.get(lineup_url)
    if lineup_response.status_code == 200:
        lineup_data = lineup_response.json()
        return lineup_data
    else:
        print(f"Failed to fetch lineup for game {game_id}: {lineup_response.status_code}")
        return None


# Function to get starting pitcher
def get_starting_pitcher(team_info):
    if team_info['pitchers']:
        starting_pitcher_id = team_info['pitchers'][0]  # First pitcher listed is typically the starter
        starting_pitcher_info = team_info['players'][f'ID{starting_pitcher_id}']
        starting_pitcher_name = starting_pitcher_info['person']['fullName']
        return starting_pitcher_name, starting_pitcher_id
    return "N/A", None


# Function to get lineup features
def get_lineup_features(lineup_data):
    home_team_pitcher, home_pitcher_id = get_starting_pitcher(lineup_data['teams']['home'])
    away_team_pitcher, away_pitcher_id = get_starting_pitcher(lineup_data['teams']['away'])

    home_batters = [player_id for player_id in lineup_data['teams']['home']['players'].keys() if
                    lineup_data['teams']['home']['players'][player_id].get('battingOrder') is not None]
    away_batters = [player_id for player_id in lineup_data['teams']['away']['players'].keys() if
                    lineup_data['teams']['away']['players'][player_id].get('battingOrder') is not None]

    return home_pitcher_id, away_pitcher_id, home_batters, away_batters


# Function to load data from SQLite database
def load_data_from_db():
    conn = sqlite3.connect('baseball_data.db')
    data = pd.read_sql_query("SELECT * FROM statcast_data", conn)
    conn.close()
    return data


# Function to get historical stats
def get_historical_stats(data, pitcher_id, batter_ids):
    stats = {'strikeouts': 0, 'walks': 0, 'hits': 0, 'home_runs': 0}
    print(f"Fetching historical stats for pitcher {pitcher_id} against batters {batter_ids}")
    for batter_id in batter_ids:
        batter_data = data[(data['pitcher'] == pitcher_id) & (data['batter'] == batter_id)]
        if not batter_data.empty:
            print(f"Historical data for pitcher {pitcher_id} vs batter {batter_id}:\n", batter_data)
        else:
            print(f"No historical data for pitcher {pitcher_id} vs batter {batter_id}")
        stats['strikeouts'] += (batter_data['events'] == 'strikeout').sum()
        stats['walks'] += (batter_data['events'] == 'walk').sum()
        stats['hits'] += (batter_data['events'].isin(['single', 'double', 'triple', 'home_run'])).sum()
        stats['home_runs'] += (batter_data['events'] == 'home_run').sum()
    print(f"Computed stats: {stats}")
    return stats


# Function to predict game outcome
def predict_game_outcome(model, home_stats, away_stats):
    # Combine home and away stats into a single feature set with column names
    features = pd.DataFrame([home_stats, away_stats], columns=['strikeouts', 'walks', 'hits', 'home_runs'])
    print(f"Features for prediction: {features}")
    prediction = model.predict(features)
    return prediction


# Main function to fetch lineups and predict outcomes
def main():
    # Example game ID and date for testing
    date = "2023-06-9"
    game_id = 745571  # Example game ID, replace with actual game ID

    # Load the model
    model = joblib.load('baseball_game_predictor.pkl')

    # Fetch schedule
    games = fetch_schedule(date)
    if not games:
        print("No games found for the given date.")
        return

    for game in games:
        game_id = game['gamePk']
        home_team = game['teams']['home']['team']['name']
        away_team = game['teams']['away']['team']['name']
        print(f"\nGame ID: {game_id}")
        print(f"{home_team} vs {away_team}")

        # Fetch lineup
        lineup_data = fetch_lineup(game_id)
        if not lineup_data:
            continue

        # Extract features from lineup
        home_pitcher_id, away_pitcher_id, home_batters, away_batters = get_lineup_features(lineup_data)

        # Load historical data
        data = load_data_from_db()
        print(f"Historical data loaded:\n{data.head()}")

        # Get historical stats for the pitchers against the lineups
        home_stats = get_historical_stats(data, home_pitcher_id, away_batters)
        away_stats = get_historical_stats(data, away_pitcher_id, home_batters)

        # Predict game outcome
        prediction = predict_game_outcome(model, home_stats, away_stats)
        result = "Home Team Wins" if prediction[0] == 1 else "Away Team Wins"
        print(f"Prediction for {home_team} vs {away_team}: {result}")


if __name__ == "__main__":
    main()

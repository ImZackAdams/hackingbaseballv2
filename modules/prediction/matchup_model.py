import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from preprocessor import preprocess_data, engineer_features, print_dataframe_info
from datetime import datetime, timedelta
import requests
import joblib
import os

from lineup import get_lineups_for_teams, team_name_to_abbreviation

MODEL_CACHE_FILE = 'trained_model.joblib'
DATABASE_FILE = 'baseball_data.db'


def batch_preprocess(engine, batch_size=10000):
    offset = 0
    while True:
        query = f"SELECT * FROM statcast_data LIMIT {batch_size} OFFSET {offset}"
        df = pd.read_sql(query, engine)

        if df.empty:
            break

        preprocessed_df = preprocess_data(df)
        print_dataframe_info(preprocessed_df, "Preprocessed")

        engineered_df = engineer_features(preprocessed_df)
        print_dataframe_info(engineered_df, "Engineered")

        X = engineered_df[['batting_average', 'on_base_percentage', 'total_bases', 'is_home']]
        y = engineered_df['winning_team']

        yield X, y

        offset += batch_size


def train_model():
    if os.path.exists(MODEL_CACHE_FILE):
        print("Loading cached model...")
        return joblib.load(MODEL_CACHE_FILE)

    engine = create_engine(f'sqlite:///{DATABASE_FILE}')

    print("Training the model in batches...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)

    X_test, y_test = None, None

    for i, (X_batch, y_batch) in enumerate(batch_preprocess(engine)):
        if i == 0:
            X_train, X_test, y_train, y_test = train_test_split(X_batch, y_batch, test_size=0.2, random_state=42)
            model.fit(X_train, y_train)
        else:
            model.fit(X_batch, y_batch)

        print(f"Processed batch {i + 1}")

    if X_test is not None and y_test is not None:
        print("Evaluating the model...")
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Model Accuracy: {accuracy}")
        print(classification_report(y_test, y_pred))
    else:
        print("Not enough data to evaluate the model.")

    print("Caching the trained model...")
    joblib.dump(model, MODEL_CACHE_FILE)

    return model


def predict_matchup(model, pitcher_id, batter_id, is_home):
    engine = create_engine('sqlite:///baseball_data.db')
    query = "SELECT * FROM statcast_data WHERE pitcher = ? AND batter = ?"
    df = pd.read_sql(query, engine, params=(pitcher_id, batter_id))

    if df.empty:
        print(f"No historical data found for the matchup between pitcher {pitcher_id} and batter {batter_id}.")
        return 0.5  # Return 0.5 as a default probability when no data is available

    preprocessed_df = preprocess_data(df)
    engineered_df = engineer_features(preprocessed_df)

    batting_average = engineered_df['batting_average'].mean()
    on_base_percentage = engineered_df['on_base_percentage'].mean()
    total_bases = engineered_df['total_bases'].sum()
    input_data = [[batting_average, on_base_percentage, total_bases, is_home]]

    try:
        probabilities = model.predict_proba(input_data)[0]
        if len(probabilities) == 2:
            return probabilities[1]  # Probability of the positive class
        elif len(probabilities) == 1:
            return probabilities[0]  # If only one probability is returned, use it directly
        else:
            print(f"Unexpected number of probabilities: {probabilities}")
            return 0.5  # Return a default value
    except Exception as e:
        print(f"Error in predict_matchup: {e}")
        return 0.5  # Return a default value in case of any error


def predict_game(model, home_lineup, away_lineup):
    home_pitcher = home_lineup[0]
    away_pitcher = away_lineup[0]

    home_win_probability = 0
    total_matchups = 0

    for batter in away_lineup[1:]:
        outcome = predict_matchup(model, home_pitcher, batter, 1)
        home_win_probability += (1 - outcome)
        total_matchups += 1

    for batter in home_lineup[1:]:
        outcome = predict_matchup(model, away_pitcher, batter, 0)
        home_win_probability += outcome
        total_matchups += 1

    if total_matchups > 0:
        home_win_probability /= total_matchups
    else:
        home_win_probability = 0.5

    return home_win_probability


def get_today_games():
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={today}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch today's games: {response.status_code}")
        return None

    schedule_data = response.json()
    games = schedule_data.get('dates', [])[0].get('games', [])

    today_games = []
    for game in games:
        home_team = game['teams']['home']['team']['name']
        away_team = game['teams']['away']['team']['name']
        today_games.append({
            'home_team': team_name_to_abbreviation.get(home_team, home_team),
            'away_team': team_name_to_abbreviation.get(away_team, away_team)
        })

    return today_games


def main():
    # Train or load the model
    model = train_model()

    # Get today's games
    today_games = get_today_games()
    if today_games is None:
        print("Failed to fetch today's games. Exiting.")
        return

    # Get all teams playing today
    all_teams = set([game['home_team'] for game in today_games] + [game['away_team'] for game in today_games])

    # Get lineups for all teams playing today
    lineups = get_lineups_for_teams(all_teams)
    if lineups is None:
        print("Failed to fetch lineups. Exiting.")
        return

    print(f"\nPredicting {len(today_games)} games for today:")

    # List to store all predictions
    all_predictions = []

    for game in today_games:
        home_team = game['home_team']
        away_team = game['away_team']

        home_lineup = lineups[lineups['team_abbr'] == home_team]['player_id'].tolist()
        away_lineup = lineups[lineups['team_abbr'] == away_team]['player_id'].tolist()

        if not home_lineup or not away_lineup:
            print(f"\nMissing lineup data for {away_team} @ {home_team}. Skipping.")
            continue

        print(f"\nAnalyzing matchup: {away_team} @ {home_team}")

        # Analyze matchups
        total_matchups = 0
        matchups_with_data = 0
        home_win_probability_sum = 0

        for batter in away_lineup[1:]:  # Skip the pitcher
            outcome = predict_matchup(model, home_lineup[0], batter, 1)
            home_win_probability_sum += (1 - outcome)
            total_matchups += 1
            if outcome != 0.5:  # Assuming 0.5 is our default when no data is found
                matchups_with_data += 1

        for batter in home_lineup[1:]:  # Skip the pitcher
            outcome = predict_matchup(model, away_lineup[0], batter, 0)
            home_win_probability_sum += outcome
            total_matchups += 1
            if outcome != 0.5:  # Assuming 0.5 is our default when no data is found
                matchups_with_data += 1

        home_win_prob = home_win_probability_sum / total_matchups if total_matchups > 0 else 0.5

        # Store prediction
        all_predictions.append({
            'home_team': home_team,
            'away_team': away_team,
            'home_win_prob': home_win_prob,
            'total_matchups': total_matchups,
            'matchups_with_data': matchups_with_data
        })

        # Print results
        print(f"Prediction for {away_team} @ {home_team}")
        print(f"Home team ({home_team}) win probability: {home_win_prob:.2f}")
        print(f"Away team ({away_team}) win probability: {1 - home_win_prob:.2f}")
        print(f"Total matchups analyzed: {total_matchups}")
        print(f"Matchups with historical data: {matchups_with_data}")
        print(f"Matchups without historical data: {total_matchups - matchups_with_data}")
        print(f"Percentage of matchups with data: {(matchups_with_data / total_matchups) * 100:.2f}%")

    print("\nNote: A win probability of 0.50 indicates no historical data for that matchup.")

    # Print summary of all predictions
    print("\n===== Summary of Today's Predictions =====")
    for pred in all_predictions:
        print(f"{pred['away_team']} @ {pred['home_team']}: "
              f"Home {pred['home_win_prob']:.2f} - Away {1 - pred['home_win_prob']:.2f} "
              f"(Data: {pred['matchups_with_data']}/{pred['total_matchups']})")

    # Print the most confident predictions
    print("\nMost confident predictions:")
    sorted_predictions = sorted(all_predictions, key=lambda x: abs(x['home_win_prob'] - 0.5), reverse=True)
    for pred in sorted_predictions[:3]:  # Top 3 most confident predictions
        confidence = max(pred['home_win_prob'], 1 - pred['home_win_prob'])
        favored_team = pred['home_team'] if pred['home_win_prob'] > 0.5 else pred['away_team']
        print(f"{pred['away_team']} @ {pred['home_team']}: {favored_team} ({confidence:.2f})")


if __name__ == "__main__":
    main()
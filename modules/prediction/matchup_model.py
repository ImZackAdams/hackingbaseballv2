import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from preprocessor import preprocess_data, engineer_features, print_dataframe_info
from datetime import datetime
import requests
import joblib
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from lineup import get_lineups_for_teams, team_name_to_abbreviation

MODEL_CACHE_FILE = 'trained_model.joblib'
DATABASE_FILE = 'baseball_data.db'


def batch_preprocess(engine, batch_size=50000):
    offset = 0
    while True:
        query = f"SELECT * FROM statcast_data LIMIT {batch_size} OFFSET {offset}"
        df = pd.read_sql(query, engine)

        if df.empty:
            break

        preprocessed_df = preprocess_data(df)
        engineered_df = engineer_features(preprocessed_df)

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
    model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)

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


def predict_matchup(model, pitcher_id, batter_id, is_home, engine):
    query = "SELECT * FROM statcast_data WHERE pitcher = ? AND batter = ?"
    df = pd.read_sql(query, engine, params=(pitcher_id, batter_id))

    if df.empty:
        return 0.5

    preprocessed_df = preprocess_data(df)
    engineered_df = engineer_features(preprocessed_df)

    batting_average = engineered_df['batting_average'].mean()
    on_base_percentage = engineered_df['on_base_percentage'].mean()
    total_bases = engineered_df['total_bases'].sum()
    input_data = [[batting_average, on_base_percentage, total_bases, is_home]]

    try:
        probabilities = model.predict_proba(input_data)[0]
        return probabilities[1] if len(probabilities) == 2 else probabilities[0]
    except Exception as e:
        print(f"Error in predict_matchup: {e}")
        return 0.5


def predict_game(model, home_lineup, away_lineup, engine):
    home_pitcher = home_lineup[0]
    away_pitcher = away_lineup[0]

    matchups = [(home_pitcher, batter, 1) for batter in away_lineup[1:]] + \
               [(away_pitcher, batter, 0) for batter in home_lineup[1:]]

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_matchup = {
            executor.submit(predict_matchup, model, pitcher, batter, is_home, engine): (pitcher, batter, is_home)
            for pitcher, batter, is_home in matchups}

        results = []
        for future in as_completed(future_to_matchup):
            matchup = future_to_matchup[future]
            try:
                result = future.result()
                results.append((matchup, result))
            except Exception as exc:
                print(f'{matchup} generated an exception: {exc}')

    home_win_probability = sum(1 - result if matchup[2] == 1 else result for matchup, result in results)
    return home_win_probability / len(results) if results else 0.5


def get_today_games():
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={today}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch today's games: {response.status_code}")
        return None

    schedule_data = response.json()
    games = schedule_data.get('dates', [])[0].get('games', [])

    return [{'home_team': team_name_to_abbreviation.get(game['teams']['home']['team']['name'],
                                                        game['teams']['home']['team']['name']),
             'away_team': team_name_to_abbreviation.get(game['teams']['away']['team']['name'],
                                                        game['teams']['away']['team']['name'])}
            for game in games]


def main():
    model = train_model()
    today_games = get_today_games()
    if today_games is None:
        print("Failed to fetch today's games. Exiting.")
        return

    all_teams = set([game['home_team'] for game in today_games] + [game['away_team'] for game in today_games])
    lineups = get_lineups_for_teams(all_teams)
    if lineups is None:
        print("Failed to fetch lineups. Exiting.")
        return

    print(f"\nPredicting {len(today_games)} games for today:")

    engine = create_engine(f'sqlite:///{DATABASE_FILE}')

    all_predictions = []
    for game in today_games:
        home_team, away_team = game['home_team'], game['away_team']
        home_lineup = lineups[lineups['team_abbr'] == home_team]['player_id'].tolist()
        away_lineup = lineups[lineups['team_abbr'] == away_team]['player_id'].tolist()

        if not home_lineup or not away_lineup:
            print(f"\nMissing lineup data for {away_team} @ {home_team}. Skipping.")
            continue

        print(f"\nAnalyzing matchup: {away_team} @ {home_team}")

        home_win_prob = predict_game(model, home_lineup, away_lineup, engine)

        all_predictions.append({
            'home_team': home_team,
            'away_team': away_team,
            'home_win_prob': home_win_prob
        })

        print(f"Prediction for {away_team} @ {home_team}")
        print(f"Home team ({home_team}) win probability: {home_win_prob:.2f}")
        print(f"Away team ({away_team}) win probability: {1 - home_win_prob:.2f}")

    print("\nNote: A win probability of 0.50 indicates no historical data for that matchup.")

    print("\n===== Summary of Today's Predictions =====")
    for pred in all_predictions:
        print(f"{pred['away_team']} @ {pred['home_team']}: "
              f"Home {pred['home_win_prob']:.2f} - Away {1 - pred['home_win_prob']:.2f}")

    print("\nMost confident predictions:")
    sorted_predictions = sorted(all_predictions, key=lambda x: abs(x['home_win_prob'] - 0.5), reverse=True)
    for pred in sorted_predictions[:3]:
        confidence = max(pred['home_win_prob'], 1 - pred['home_win_prob'])
        favored_team = pred['home_team'] if pred['home_win_prob'] > 0.5 else pred['away_team']
        print(f"{pred['away_team']} @ {pred['home_team']}: {favored_team} ({confidence:.2f})")


if __name__ == "__main__":
    main()
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from preprocessor import preprocess_data, engineer_features, print_dataframe_info


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
    engine = create_engine('sqlite:///baseball_data.db')

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

    return model


def predict_matchup(model, pitcher_id, batter_id, is_home):
    engine = create_engine('sqlite:///baseball_data.db')
    query = "SELECT * FROM statcast_data WHERE pitcher = ? AND batter = ?"
    df = pd.read_sql(query, engine, params=(pitcher_id, batter_id))  # Changed to tuple

    if df.empty:
        print(f"No historical data found for the matchup between pitcher {pitcher_id} and batter {batter_id}.")
        return 0.5  # Return 0.5 as a default probability when no data is available

    preprocessed_df = preprocess_data(df)
    engineered_df = engineer_features(preprocessed_df)

    batting_average = engineered_df['batting_average'].mean()
    on_base_percentage = engineered_df['on_base_percentage'].mean()
    total_bases = engineered_df['total_bases'].sum()
    input_data = [[batting_average, on_base_percentage, total_bases, is_home]]

    prediction = model.predict_proba(input_data)[0][1]  # Probability of the positive class
    return prediction


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


if __name__ == "__main__":
    model = train_model()

    # Example lineups (player IDs)
    home_lineup = [123456, 234567, 345678, 456789, 567890, 678901, 789012, 890123, 901234]
    away_lineup = [111111, 222222, 333333, 444444, 555555, 666666, 777777, 888888, 999999]

    print("\nPredicting game outcome...")
    home_win_prob = predict_game(model, home_lineup, away_lineup)
    print(f"Home team win probability: {home_win_prob:.2f}")
    print(f"Away team win probability: {1 - home_win_prob:.2f}")
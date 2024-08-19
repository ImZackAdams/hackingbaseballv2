import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.metrics import accuracy_score
import joblib

from modules.prediction.preprocessor import preprocess_data, engineer_features

DATABASE_FILE = 'baseball_data.db'
MODEL_CACHE_FILE = 'trained_model.joblib'

def fetch_historical_data(engine, start_date, end_date):
    query = f"""
    SELECT game_date, game_pk, pitcher, batter, events, home_team, away_team,
           post_home_score, post_away_score
    FROM statcast_data
    WHERE game_date BETWEEN '{start_date}' AND '{end_date}'
    """
    return pd.read_sql(query, engine)


def backtest_model(model, historical_data):
    # Apply your existing preprocessing and feature engineering functions
    preprocessed_data = preprocess_data(historical_data)
    feature_engineered_data = engineer_features(preprocessed_data)

    # Prepare data for prediction
    X = feature_engineered_data[['batting_average', 'on_base_percentage', 'total_bases', 'is_home']]
    y_true = feature_engineered_data['winning_team']

    # Debug: Check the distribution of y_true
    print("Distribution of y_true labels:")
    print(pd.Series(y_true).value_counts())

    # Predict outcomes
    y_pred_proba = model.predict_proba(X)
    print("Shape of y_pred_proba:", y_pred_proba.shape)
    print("First few entries of y_pred_proba:", y_pred_proba[:5])

    if y_pred_proba.shape[1] == 1:
        y_pred_proba = y_pred_proba[:, 0]
        y_pred = (y_pred_proba > 0.5).astype(int)
    else:
        y_pred = (y_pred_proba[:, 1] > 0.5).astype(int)
        y_pred_proba = y_pred_proba[:, 1]

    # Evaluate predictions
    accuracy = accuracy_score(y_true, y_pred)
    print(f"Backtest Accuracy: {accuracy:.2f}")
    return y_true, y_pred, y_pred_proba


# Example usage
engine = create_engine(f'sqlite:///{DATABASE_FILE}')

# Fetch historical data (e.g., June 2023)
historical_data = fetch_historical_data(engine, '2023-06-01', '2023-06-30')

# Load the pre-trained model
model = joblib.load(MODEL_CACHE_FILE)

# Backtest the model
y_true, y_pred, y_pred_proba = backtest_model(model, historical_data)

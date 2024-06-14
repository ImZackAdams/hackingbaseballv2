import pandas as pd
import joblib
from datetime import datetime
from modules.game_management.utils import get_todays_lineups
from modules.prediction.preprocess import preprocess_data

# Define the date we are interested in
date_to_check = datetime.strptime('2024-06-13', '%Y-%m-%d')

# Fetch today's lineups
todays_lineups = get_todays_lineups(date_to_check)
if todays_lineups is None:
    print("No lineups found for today.")
else:
    # Load the trained model and preprocessors
    model = joblib.load('game_outcome_predictor.pkl')
    model_columns = joblib.load('model_columns.pkl')  # Load the column names used in the model
    imputer = joblib.load('imputer.pkl')
    scaler = joblib.load('scaler.pkl')

    # Prepare features for today's lineups
    lineups_features = preprocess_data(todays_lineups)

    # Ensure all columns used in training are present
    for column in model_columns:
        if column not in lineups_features.columns:
            lineups_features[column] = 0

    # Impute and scale the features
    lineups_features_imputed = imputer.transform(lineups_features[model_columns])
    lineups_features_scaled = scaler.transform(lineups_features_imputed)

    # Predict outcomes
    predictions = model.predict(lineups_features_scaled)

    # Print predictions
    for team, prediction in zip(lineups_features['team_abbr'], predictions):
        print(f"Team: {team}, Predicted Outcome: {'Win' if prediction == 1 else 'Lose'}")

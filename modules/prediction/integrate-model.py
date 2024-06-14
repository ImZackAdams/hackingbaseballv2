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
    # Load the trained model
    model = joblib.load('game_outcome_predictor.pkl')

    # Prepare features for today's lineups
    lineups_features = preprocess_data(todays_lineups)

    # Predict outcomes
    predictions = model.predict(lineups_features)

    # Print predictions
    for team, prediction in zip(lineups_features['team_abbr'], predictions):
        print(f"Team: {team}, Predicted Outcome: {'Win' if prediction == 1 else 'Lose'}")

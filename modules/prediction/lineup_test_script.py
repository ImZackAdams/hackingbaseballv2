import pandas as pd
import joblib
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

# Load the trained model and preprocessors
model = joblib.load('game_outcome_predictor.pkl')
imputer = joblib.load('imputer.pkl')
scaler = joblib.load('scaler.pkl')
encoder = joblib.load('encoder.pkl')


# Define a function to predict the outcome for a game
def predict_game(total_strikeouts, total_walks, total_hits, total_home_runs):
    # Create a DataFrame for the input features
    features = pd.DataFrame({
        'total_strikeouts': [total_strikeouts],
        'total_walks': [total_walks],
        'total_hits': [total_hits],
        'total_home_runs': [total_home_runs]
    })

    # Impute missing values
    features_imputed = imputer.transform(features)

    # Scale the features
    features_scaled = scaler.transform(features_imputed)

    # Debug: Print the intermediate steps
    print("Features before imputation and scaling:", features)
    print("Features after imputation:", features_imputed)
    print("Features after scaling:", features_scaled)

    # Predict the outcome
    prediction = model.predict(features_scaled)

    # Decode the prediction
    decoded_prediction = encoder.inverse_transform(prediction)

    return decoded_prediction[0]


# Example usage
games = [
    {
        'game_id': 745571,
        'home_team': 'Philadelphia Phillies',
        'away_team': 'New York Mets',
        'home_features': [16, 0, 17, 1]
    },
    {
        'game_id': 745003,
        'home_team': 'Texas Rangers',
        'away_team': 'San Francisco Giants',
        'home_features': [17, 0, 14, 2]
    }
]

for game in games:
    home_team_prediction = predict_game(*game['home_features'])
    print(f"Game ID: {game['game_id']}")
    print(f"{game['home_team']} vs {game['away_team']}")
    print(f"Predicted result: {'Home win' if home_team_prediction == 1 else 'Away win'}")

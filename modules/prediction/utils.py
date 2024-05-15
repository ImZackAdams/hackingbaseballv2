import random
import pandas as pd

def get_game_predictions(selected_games):
    # Fetch the current game schedules
    schedules = pd.read_json('game_schedules.json', convert_dates=['Date'])

    # Filter the schedules to include only the selected games
    selected_schedules = schedules[schedules['id'].isin(selected_games)]

    predictions = []
    for _, game in selected_schedules.iterrows():
        prediction = {
            'id': game['id'],
            'away_team': game['Opp'],
            'home_team': game['Tm'],
            'prediction': random.choice([f"{game['Opp']} wins", f"{game['Tm']} wins"]),
            'odds': round(random.uniform(1.5, 3.0), 2)
        }
        predictions.append(prediction)

    # Debugging: Print the filtered predictions
    print(f"Filtered predictions: {predictions}")

    return predictions

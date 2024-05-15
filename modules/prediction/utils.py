def get_game_predictions(selected_games):
    # Mock implementation
    all_predictions = [
        {'id': '1', 'away_team': 'Team A', 'home_team': 'Team B', 'prediction': 'Team A wins', 'odds': '1.5'},
        {'id': '2', 'away_team': 'Team C', 'home_team': 'Team D', 'prediction': 'Team D wins', 'odds': '2.1'}
    ]

    # Filter the predictions to include only the selected games
    predictions = [game for game in all_predictions if game['id'] in selected_games]

    # Debugging: Print the filtered predictions
    print(f"Filtered predictions: {predictions}")

    return predictions


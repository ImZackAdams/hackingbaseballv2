from flask import render_template


def render_results(predictions):
    games = []
    for prediction in predictions:
        game = {
            'away_team': prediction['away_team'],
            'home_team': prediction['home_team'],
            'prediction': prediction['predicted_winner'],
            'odds': prediction['odds']
        }
        games.append(game)

    return render_template('results.html', games=games)

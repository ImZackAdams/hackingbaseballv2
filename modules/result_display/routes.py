from flask import Blueprint, render_template, session
from ..prediction.utils import get_game_predictions

result_display = Blueprint('result_display', __name__)


@result_display.route('/results')
def results():
    # Get the selected game IDs from the session
    selected_games = session.get('selected_games', [])

    # Debugging: Print the selected game IDs
    print(f"Selected games: {selected_games}")

    # Fetch the predictions for the selected games
    predictions = get_game_predictions(selected_games)

    # Debugging: Print the predictions
    print(f"Predictions: {predictions}")

    return render_template('results.html', games=predictions)


@result_display.route('/game/<game_id>')
def game_detail(game_id):
    predictions = get_game_predictions([game_id])
    if not predictions:
        return render_template('game_detail.html', game=None)
    return render_template('game_detail.html', game=predictions[0])

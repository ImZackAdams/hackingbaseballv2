from flask import render_template, request
from . import results


@results.route('/results')
def show_results():
    # Dummy data to illustrate the function
    games = [{'game': 'Team A vs Team B', 'prediction': 'Team A wins', 'odds': '2:1'}]
    # Retrieve real game data, predictions, and odds here
    # This could involve calls to the prediction and game_management modules
    return render_template('results/results.html', games=games)

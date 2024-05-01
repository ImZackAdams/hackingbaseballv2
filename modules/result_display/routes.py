from flask import render_template, request
from . import results


@results.route('/results')
def show_results():
    # Dummy data to illustrate the function
    games = [{'game': 'Team A vs Team B', 'prediction': 'Team A wins', 'odds': '2:1'}]
    # Retrieve real game data, predictions, and odds here
    return render_template('results.html', games=games)

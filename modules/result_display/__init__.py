from flask import Blueprint, render_template

bp = Blueprint('result_display', __name__, template_folder='templates')

@bp.route('/results')
def results():
    # Logic to fetch and prepare the results data
    # Replace this with your actual implementation
    games = [
        {
            'away_team': 'Team A',
            'home_team': 'Team B',
            'prediction': 'Team B Wins',
            'odds': '-110'
        },
        {
            'away_team': 'Team C',
            'home_team': 'Team D',
            'prediction': 'Team C Wins',
            'odds': '+120'
        }
        # Add more games as needed
    ]
    return render_template('results.html', games=games)
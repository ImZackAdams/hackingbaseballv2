from flask import Blueprint, render_template



bp = Blueprint('result_display', __name__, template_folder='templates')

@bp.route('/success')
def success():
    # Dummy data for testing
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
    ]
    # Render the results template with the dummy data
    return render_template('results.html', games=games)


@bp.route('/test')
def test():
    return "This is a test route"

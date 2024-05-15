from flask import Blueprint, render_template
from ..prediction.utils import get_game_predictions

result_display = Blueprint('result_display', __name__)


@result_display.route('/results')
def results():
    predictions = get_game_predictions()
    return render_template('results.html', games=predictions)

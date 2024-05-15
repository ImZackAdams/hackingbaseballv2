from flask import Blueprint, render_template
from ..prediction.utils import get_game_predictions

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/results')
def results():
    predictions = get_game_predictions()
    return render_template('results.html', predictions=predictions)

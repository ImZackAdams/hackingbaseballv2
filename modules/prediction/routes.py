# File: prediction/routes.py

from flask import Blueprint, jsonify, request
from modules.game_management.utils import get_team_roster
from modules.prediction.utils import get_historical_stats, make_predictions
from modules.result_display.utils import render_results  # Import the render_results function

prediction_bp = Blueprint('prediction', __name__)

@prediction_bp.route('/predict', methods=['POST'])
def predict_game():
    data = request.json
    team_id = data.get('team_id')
    opposing_pitcher_id = data.get('opposing_pitcher_id')

    roster = get_team_roster(team_id)

    if roster is None:
        return jsonify({'error': 'Could not fetch the team roster'}), 500

    predictions = make_predictions(roster, opposing_pitcher_id)

    # Render the results template with the predictions
    rendered_results = render_results(predictions)

    return jsonify({'results': rendered_results}), 200
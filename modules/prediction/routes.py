# File: prediction/routes.py

from flask import Blueprint, jsonify, request
from modules.game_management.utils import get_team_roster  # Importing from game_management module
from modules.prediction.utils import get_historical_stats, make_predictions  # Import utility functions

prediction_bp = Blueprint('prediction', __name__)


@prediction_bp.route('/predict', methods=['POST'])
def predict_game():
    data = request.json
    team_id = data.get('team_id')
    opposing_pitcher_id = data.get('opposing_pitcher_id')

    # Fetch the latest roster for the team
    roster = get_team_roster(team_id)

    # If roster is None, there was an error in fetching it
    if roster is None:
        return jsonify({'error': 'Could not fetch the team roster'}), 500

    predictions = make_predictions(roster, opposing_pitcher_id)

    return jsonify({'predictions': predictions}), 200

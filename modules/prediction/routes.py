# File: prediction/routes.py

from flask import Blueprint, jsonify, request
from modules.game_management.utils import get_team_roster
from modules.prediction.game_lineup import predict_game_outcome_from_lineup
from modules.prediction.model import train_model
from modules.result_display.utils import render_results

prediction_bp = Blueprint('prediction', __name__)

# Train the model
model = train_model()

@prediction_bp.route('/predict', methods=['POST'])
def predict_game():
    data = request.json
    game_id = data.get('game_id')

    if game_id is None:
        return jsonify({'error': 'Missing game_id parameter'}), 400

    predicted_outcome = predict_game_outcome_from_lineup(game_id, model)

    if predicted_outcome is None:
        return jsonify({'error': 'Could not predict the game outcome'}), 500

    # Render the results template with the predicted outcome
    rendered_results = render_results(predicted_outcome)

    return jsonify({'results': rendered_results}), 200
from flask import Blueprint, redirect, url_for, request, jsonify, current_app
import stripe
import logging

payment = Blueprint('payment', __name__)

stripe.api_key = 'sk_test_51PG1mPIiIqA6x4U9hpM7pK01VfggMYuC0vBeNWjX8Y3N8bM9mSEylGSz5LQA9mJUECiMQJpQXCGJ1milmSeCdUSH00ffMMFhAH'

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@payment.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        data = request.get_json()
        selected_games = data.get('selectedGames', [])

        # For demonstration purposes, we'll assume each selected game costs $5
        line_items = [{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': f'Prediction for game {game_id}',
                },
                'unit_amount': 500,
            },
            'quantity': 1,
        } for game_id in selected_games]

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=url_for('main.results', _external=True),
            cancel_url=url_for('game_management.index', _external=True),
        )

        return jsonify({'sessionId': session.id})
    except Exception as e:
        logger.error(f"Error creating Stripe checkout session: {e}")
        return jsonify({'error': str(e)}), 403

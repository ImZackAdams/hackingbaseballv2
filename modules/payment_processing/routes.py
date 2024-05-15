from flask import Blueprint, redirect, url_for, request, jsonify, session
import stripe
import os
import logging

payment = Blueprint('payment', __name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load Stripe keys from environment variables
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
public_key = os.getenv('STRIPE_PUBLIC_KEY')

@payment.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        data = request.get_json()
        selected_games = data.get('selectedGames', [])

        # Debugging: Print the received game IDs
        print(f"Received game IDs: {selected_games}")

        # Store the selected game IDs in the session
        session['selected_games'] = selected_games

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

        stripe_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=url_for('result_display.results', _external=True),
            cancel_url=url_for('game_management.index', _external=True),
        )

        return jsonify({'sessionId': stripe_session.id})
    except Exception as e:
        logger.error(f"Error creating Stripe checkout session: {e}")
        return jsonify({'error': str(e)}), 403

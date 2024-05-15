import stripe
from flask import Blueprint, jsonify, request, render_template

bp = Blueprint('payment', __name__)
stripe.api_key = 'sk_test_51PG1mPIiIqA6x4U9hpM7pK01VfggMYuC0vBeNWjX8Y3N8bM9mSEylGSz5LQA9mJUECiMQJpQXCGJ1milmSeCdUSH00ffMMFhAH'

@bp.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    selected_games = request.json['selectedGames']
    line_items = []

    # Retrieve the necessary information about the selected games from your database
    for game_id in selected_games:
        # Example line item for each game
        line_item = {
            'price_data': {
                'currency': 'usd',
                'unit_amount': 2000,  # Example price in cents
                'product_data': {
                    'name': f'Game Report {game_id}',  # Example product name
                },
            },
            'quantity': 1,
        }
        line_items.append(line_item)

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url='http://localhost:5000/success',
            cancel_url='http://localhost:5000/payment/cancel',
        )
        return jsonify({'sessionId': checkout_session.id})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/cancel')
def cancel():
    # Handle payment cancellation
    return render_template('cancel.html')
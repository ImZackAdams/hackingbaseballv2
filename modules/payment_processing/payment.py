import stripe
from flask import Flask, jsonify, request

app = Flask(__name__)
stripe.api_key = 'your_stripe_secret_key'


@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': 2000,  # Amount in cents
                    'product_data': {
                        'name': 'Baseball Game Report',
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://localhost:5000/results',
            cancel_url='http://localhost:5000/cancel',
        )
        return jsonify({'id': checkout_session.id})
    except Exception as e:
        return jsonify(error=str(e)), 403

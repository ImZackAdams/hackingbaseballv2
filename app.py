from flask import Flask, request, render_template
from modules.game_management.routes import game_management
from modules.result_display import bp as result_display_bp
from modules.payment_processing import bp as payment_bp
import stripe

app = Flask(__name__)

# Set your Stripe API key
stripe.api_key = 'sk_test_51PG1mPIiIqA6x4U9hpM7pK01VfggMYuC0vBeNWjX8Y3N8bM9mSEylGSz5LQA9mJUECiMQJpQXCGJ1milmSeCdUSH00ffMMFhAH'

# Set the endpoint secret for webhook verification
endpoint_secret = 'whsec_6b4960c6fb572c46aa0926d0c14759e89235a4fb16c6a2b5099872ecc181c257'

app.register_blueprint(game_management)
app.register_blueprint(result_display_bp)
app.register_blueprint(payment_bp)


@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
        print("Received event:", event)  # Add this line for debugging
    except ValueError as e:
        print("Invalid payload:", e)  # Add this line for debugging
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        print("Invalid signature:", e)  # Add this line for debugging
        return 'Invalid signature', 400

    # Handle the event
    if event.type == 'checkout.session.completed':
        print("Checkout session completed")  # Add this line for debugging
        # Handle successful payment completion
        # Add your custom logic here
    elif event.type == 'payment_intent.succeeded':
        print("Payment intent succeeded")  # Add this line for debugging
        # Handle successful payment intent
        # Add your custom logic here
    elif event.type == 'charge.succeeded':
        print("Charge succeeded")  # Add this line for debugging
        # Handle successful charge
        # Add your custom logic here

    return 'OK', 200

@app.route('/success')
def success():
    # Render the results template
    return render_template('results.html')

if __name__ == '__main__':
    app.run(debug=True)

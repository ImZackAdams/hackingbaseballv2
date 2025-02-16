import os
from dotenv import load_dotenv
from flask import Flask, render_template

# Load environment variables immediately
load_dotenv()

# Validate required environment variables
required_env_vars = ['STRIPE_SECRET_KEY', 'STRIPE_PUBLIC_KEY']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise RuntimeError(f"Missing required environment variables: {', '.join(missing_vars)}")

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_secret_key')  # Better to get from env
app.config['STRIPE_SECRET_KEY'] = os.getenv('STRIPE_SECRET_KEY')
app.config['STRIPE_PUBLIC_KEY'] = os.getenv('STRIPE_PUBLIC_KEY')

# Import blueprints after app creation to avoid circular imports
from modules.result_display.routes import result_display
from modules.payment_processing.routes import payment as payment_processing
from modules.game_management.routes import game_management as game_management_bp

# Register blueprints
app.register_blueprint(game_management_bp)
app.register_blueprint(result_display)
app.register_blueprint(payment_processing)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/terms_of_service')
def terms_of_service():
    return render_template('terms_of_service.html')

@app.route('/privacy_policy')
def privacy_policy():
    return render_template('privacy_policy.html')

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', '0') == '1')
import os
from flask import Flask
from dotenv import load_dotenv
from modules.result_display.routes import result_display as result_display
from modules.payment_processing.routes import payment as payment_processing
from modules.game_management.routes import game_management as game_management_bp
from flask import Flask, render_template

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['STRIPE_SECRET_KEY'] = os.getenv('STRIPE_SECRET_KEY')
app.config['STRIPE_PUBLIC_KEY'] = os.getenv('STRIPE_PUBLIC_KEY')

# Register blueprints
app.register_blueprint(game_management_bp)
app.register_blueprint(result_display)
app.register_blueprint(payment_processing)


#Footer Terms of Service 
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
    # Use FLASK_DEBUG environment variable to set the debug mode
    debug_mode = os.getenv('FLASK_DEBUG', '0') == '1'
    app.run(debug=debug_mode)
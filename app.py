import os
from flask import Flask
from dotenv import load_dotenv
from modules.result_display.routes import result_display as result_display
from modules.payment_processing.routes import payment as payment_processing
from modules.game_management.routes import game_management as game_management_bp

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Register blueprints
app.register_blueprint(game_management_bp)
app.register_blueprint(result_display)
app.register_blueprint(payment_processing)

if __name__ == '__main__':
    app.run(debug=True)

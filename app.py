from flask import Flask
from modules.result_display.routes import main as result_display_main
from modules.payment_processing.routes import payment as payment_processing
from modules.game_management.routes import game_management as game_management_bp

app = Flask(__name__)

# Register blueprints
app.register_blueprint(game_management_bp)
app.register_blueprint(result_display_main)
app.register_blueprint(payment_processing)


if __name__ == '__main__':
    app.run(debug=True)

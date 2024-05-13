from flask import Flask, request, jsonify, render_template
from database import db
from modules.game_management.routes import game_management
from modules.result_display import bp as result_display_bp
from modules.prediction.game_lineup import predict_game_outcome_from_lineup
from modules.prediction.model import train_model
from modules.payment_processing import create_checkout_session, bp as payment_bp

app = Flask(__name__)

app.register_blueprint(game_management)
app.register_blueprint(result_display_bp)
app.register_blueprint(payment_bp)

# Train the model
model = train_model()


@app.route('/predict_game_outcome', methods=['POST'])
def predict_game_outcome():
    game_id = request.json['game_id']

    predicted_outcome = predict_game_outcome_from_lineup(game_id, model)

    return jsonify({'predicted_outcome': predicted_outcome.tolist()})


@app.route('/success')
def success():
    # Render the success page with the user's results
    return render_template('results.html')


@app.route('/cancel')
def cancel():
    # Render the cancel page
    return render_template('cancel.html')


# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hacking_baseball.db'
# db.init_app(app)
# with app.app_context():
#     db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
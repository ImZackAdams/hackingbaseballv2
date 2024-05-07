from flask import Flask, render_template, url_for

from database import db
from modules.game_management.routes import game_management
from modules.result_display import results
#from modules.prediction.routes import prediction_bp  # Import the prediction Blueprint

app = Flask(__name__)

app.register_blueprint(game_management)
app.register_blueprint(results)
#app.register_blueprint(prediction_bp)  # Register the prediction Blueprint

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hacking_baseball.db'
# db.init_app(app)
# with app.app_context():
#     db.create_all()

# @app.route('/')
# def index():
#     return render_template('index.html')

@app.route('/terms_of_service')
def tos():
    return render_template('terms_of_service.html')



if __name__ == '__main__':
    app.run(debug=True)

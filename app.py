from flask import Flask
from database import db
from modules.game_management.routes import game_management

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hacking_baseball.db'
# db.init_app(app)
#
app.register_blueprint(game_management)
#
# with app.app_context():
#     db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
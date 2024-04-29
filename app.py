from flask import Flask, render_template
from datetime import datetime
from config import Config
from flask_caching import Cache
# Import SQLAlchemy and Migrate here
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Import the game_management blueprint
from modules.game_management.routes import game_management_bp
# Import the get_or_update_schedules function from the utils module within game_management
from modules.game_management.utils import get_or_update_schedules

app = Flask(__name__)

# Configure the Flask app (you can separate this out into different environment configurations if needed)
app.config.from_object(Config)

# Set up caching
cache = Cache(app)
cache.init_app(app)

# Set up the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Register the blueprint from the game_management module
app.register_blueprint(game_management_bp, url_prefix='/games')


@app.route("/")
@cache.cached(timeout=86400)  # Cache this page for one day
def index():
    year = app.config.get('CURRENT_YEAR', datetime.now().year)
    today = datetime.today().date()
    games_today = get_or_update_schedules(year)
    games_today = games_today[games_today['Date'].dt.date == today]

    games = [{
        'game_date': game['Date'].isoformat(),  # ISO format is fine for internal use
        'formatted_date': game['Date'].strftime('%B %d, %Y'),  # Pre-format for display
        'home_team': game['Tm'],
        'away_team': game['Opp'],
    } for game in games_today.to_dict(orient='records')]

    if not games:
        message = "No games scheduled for today."
        return render_template("index.html", message=message)
    else:
        return render_template("index.html", games=games)

# Only for local development!
if __name__ == "__main__":
    app.run(debug=app.config.get('DEBUG', False))

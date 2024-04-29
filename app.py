from flask import Flask, render_template
from datetime import datetime
# Import the game_management blueprint
from modules.game_management import game_management
# Import the get_or_update_schedules function from the utils module within game_management
from modules.game_management.utils import get_or_update_schedules

app = Flask(__name__)
# Register the blueprint from the game_management module
app.register_blueprint(game_management, url_prefix='/games')


@app.route("/")
def index():
    year = 2024
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


# The app.run() call is only necessary when running the application directly and not when deploying to a production server
if __name__ == "__main__":
    app.run(debug=True)

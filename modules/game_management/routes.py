from flask import render_template
from modules.game_management import game_management
from modules.game_management.utils import get_or_update_schedules
from datetime import datetime


@game_management.route('/')
def index():
    today = datetime.now().date()
    schedules = get_or_update_schedules(today.year)

    # Filter schedules for today's games
    todays_games = schedules[schedules['Date'].dt.date == today]

    # Create a list of game objects
    games = []
    for _, row in todays_games.iterrows():
        game = {
            'away_team': row['Opp'],
            'home_team': row['Tm'],
            'formatted_date': row['Date'].strftime('%Y-%m-%d')
        }
        games.append(game)

    return render_template('index.html', games=games)
import pandas as pd
from flask import Blueprint, render_template
from .utils import get_or_update_schedules
from datetime import datetime

game_management = Blueprint('game_management', __name__)

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
            'id': row['id'],  # Ensure the id is properly added here
            'away_team': row['Opp'],
            'home_team': row['Tm'],
            'formatted_date': row['Date'].strftime('%Y-%m-%d') if not pd.isnull(row['Date']) else 'Unknown Date'
        }
        games.append(game)

    return render_template('index.html', games=games)

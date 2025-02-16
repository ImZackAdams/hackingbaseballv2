import pandas as pd
from flask import Blueprint, render_template
from .utils import get_or_update_schedules
from datetime import datetime

game_management = Blueprint('game_management', __name__)

@game_management.route('/')
def index():
    # Hardcoded test date from the 2024 season (adjust if needed)
    test_date = datetime.strptime('2024-03-28', '%Y-%m-%d').date()

    # Load the schedules
    schedules = get_or_update_schedules(test_date.year)

    # Ensure 'Date' column is a datetime object
    schedules['Date'] = pd.to_datetime(schedules['Date'], errors='coerce')

    # Filter schedules for the test date
    test_games = schedules[schedules['Date'].dt.date == test_date]

    # Create a list of game objects
    games = []
    for _, row in test_games.iterrows():
        game = {
            'id': row['id'] if 'id' in row else 'Unknown',
            'away_team': row['Opp'],
            'home_team': row['Tm'],
            'formatted_date': row['Date'].strftime('%Y-%m-%d') if not pd.isnull(row['Date']) else 'Unknown Date'
        }
        games.append(game)

    return render_template('index.html', games=games)

# Original dynamic code for reference (commented out)
# @game_management.route('/')
# def index():
#     today = datetime.now().date()
#     schedules = get_or_update_schedules(today.year)

#     # Ensure 'Date' column is a datetime object
#     schedules['Date'] = pd.to_datetime(schedules['Date'], errors='coerce')

#     # Filter schedules for today's games
#     todays_games = schedules[schedules['Date'].dt.date == today]

#     # Create a list of game objects
#     games = []
#     for _, row in todays_games.iterrows():
#         game = {
#             'id': row['id'] if 'id' in row else 'Unknown',
#             'away_team': row['Opp'],
#             'home_team': row['Tm'],
#             'formatted_date': row['Date'].strftime('%Y-%m-%d') if not pd.isnull(row['Date']) else 'Unknown Date'
#         }
#         games.append(game)

#     return render_template('index.html', games=games)

from flask import Flask, render_template
from datetime import datetime
# Import the game_management module which contains the blueprint and the utility functions
from modules.game_management import game_management, get_or_update_schedules


app = Flask(__name__)
# Register the blueprint from the game_management module to structure the endpoints for game management
app.register_blueprint(game_management, url_prefix='/games')

@app.route("/")
def index():
    # Set the current year or make it dynamic based on the current date
    year = 2024
    today = datetime.today().date()
    # Get the games scheduled for today using the utility function
    games_today = get_or_update_schedules(year)
    games_today = games_today[games_today['Date'].dt.date == today]

    # Prepare the data to be displayed on the index page
    games = [{
        'game_date': game['Date'].isoformat(),
        'home_team': game['Tm'],
        'away_team': game['Opp'],
    } for game in games_today.to_dict(orient='records')]

    # Render the index page with the games information or a message if no games are scheduled
    if not games:
        message = "No games scheduled for today."
        return render_template("index.html", message=message)
    else:
        return render_template("index.html", games=games)

# The app.run() call is only necessary when running the application directly and not when deploying to a production
# server
if __name__ == "__main__":
    app.run(debug=True)




""" old code below"""

# import pandas as pd
# from pybaseball import schedule_and_record
# from datetime import datetime, timedelta
# import os
# import json
# from flask import Flask, render_template
#
# app = Flask(__name__, static_url_path='/static')
# cache_file = 'game_schedules.json'
#
#
# def fetch_and_process_schedules(year=2024):
#     team_abbreviations = [
#         'ARI', 'ATL', 'BAL', 'BOS', 'CHC',
#         'CIN', 'CLE', 'COL', 'CHW', 'DET',
#         'HOU', 'KC', 'LAA', 'LAD', 'MIA',
#         'MIL', 'MIN', 'NYM', 'NYY', 'OAK',
#         'PHI', 'PIT', 'SD', 'SEA', 'SF',
#         'STL', 'TB', 'TEX', 'TOR', 'WSN'
#     ]
#
#     all_games = pd.DataFrame()
#
#     for team in team_abbreviations:
#         try:
#             team_schedule = schedule_and_record(year, team)
#             all_games = pd.concat([all_games, team_schedule], ignore_index=True)
#         except Exception as e:
#             print(f"Failed to retrieve schedule for {team}: {e}")
#
#     all_games = all_games.dropna(subset=['Date', 'Tm', 'Opp'])
#     all_games['unique_id'] = all_games.apply(lambda row: row['Date'] + ''.join(sorted([row['Tm'], row['Opp']])), axis=1)
#     unique_games = all_games.drop_duplicates(subset=['unique_id'])
#     unique_games = unique_games.drop(columns=['unique_id'])
#     unique_games['Date'] = pd.to_datetime(unique_games['Date'], errors='coerce', format='%A, %b %d')
#     unique_games['Date'] = unique_games['Date'].apply(lambda d: d.replace(year=year))
#     unique_games_sorted = unique_games.sort_values(by='Date', ascending=True)
#     unique_games_sorted = unique_games_sorted.reset_index(drop=True)
#
#     return unique_games_sorted
#
#
# def get_or_update_schedules(year):
#     if os.path.exists(cache_file):
#         modified_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
#         if datetime.now() - modified_time < timedelta(days=1):
#             with open(cache_file, 'r') as file:
#                 return pd.read_json(file, convert_dates=['Date'])
#
#     schedules = fetch_and_process_schedules(year)
#     schedules.to_json(cache_file, date_format='iso')
#     return schedules
#
#
# @app.route("/")
# def index():
#     year = 2024
#     today = datetime.today().date()
#     games_today = get_or_update_schedules(year)
#     games_today = games_today[games_today['Date'].dt.date == today]
#
#     games = [{
#         'game_date': game['Date'],
#         'home_team': game['Tm'],
#         'away_team': game['Opp'],
#     } for game in games_today.to_dict(orient='records')]
#
#     if not games:
#         message = "No games scheduled for today."
#         return render_template("index.html", message=message)
#     else:
#         return render_template("index.html", games=games)
#
#
#
#
# if __name__ == "__main__":
#     app.run(debug=True)

import pandas as pd
from flask import Blueprint, render_template
from datetime import datetime
import statsapi  # MLB-StatsAPI

game_management = Blueprint('game_management', __name__)

# Mapping of team names to abbreviations for logo lookup
team_name_to_abbreviation = {
    'Arizona Diamondbacks': 'ARI', 'Atlanta Braves': 'ATL', 'Baltimore Orioles': 'BAL', 'Boston Red Sox': 'BOS',
    'Chicago Cubs': 'CHC', 'Cincinnati Reds': 'CIN', 'Cleveland Guardians': 'CLE', 'Colorado Rockies': 'COL',
    'Chicago White Sox': 'CHW', 'Detroit Tigers': 'DET', 'Houston Astros': 'HOU', 'Kansas City Royals': 'KCR',
    'Los Angeles Angels': 'LAA', 'Los Angeles Dodgers': 'LAD', 'Miami Marlins': 'MIA', 'Milwaukee Brewers': 'MIL',
    'Minnesota Twins': 'MIN', 'New York Mets': 'NYM', 'New York Yankees': 'NYY', 'Oakland Athletics': 'OAK',
    'Philadelphia Phillies': 'PHI', 'Pittsburgh Pirates': 'PIT', 'San Diego Padres': 'SDP', 'Seattle Mariners': 'SEA',
    'San Francisco Giants': 'SFG', 'St. Louis Cardinals': 'STL', 'Tampa Bay Rays': 'TBR', 'Texas Rangers': 'TEX',
    'Toronto Blue Jays': 'TOR', 'Washington Nationals': 'WSN'
}

@game_management.route('/')
def index():
    today_str = datetime.now().strftime('%m/%d/%Y')
    today_display = datetime.now().strftime('%Y-%m-%d')

    # Get today's games
    games_data = statsapi.schedule(start_date=today_str, end_date=today_str)
    
    games = []
    for game in games_data:
        away = game['away_name']
        home = game['home_name']
        game_obj = {
            'id': game['game_id'],
            'away_team': away,
            'home_team': home,
            'away_abbr': team_name_to_abbreviation.get(away, 'default'),
            'home_abbr': team_name_to_abbreviation.get(home, 'default'),
            'formatted_date': today_display
        }
        games.append(game_obj)

    return render_template('index.html', games=games)

import os
from datetime import datetime, timedelta
import pandas as pd
from pybaseball import schedule_and_record
import requests
import numpy as np

# Define the cache file location
cache_file = 'game_schedules.json'

# Dictionary to map full team names to abbreviations
team_name_to_abbreviation = {
    'Arizona Diamondbacks': 'ARI', 'Atlanta Braves': 'ATL', 'Baltimore Orioles': 'BAL', 'Boston Red Sox': 'BOS',
    'Chicago Cubs': 'CHC', 'Cincinnati Reds': 'CIN', 'Cleveland Guardians': 'CLE', 'Colorado Rockies': 'COL',
    'Chicago White Sox': 'CHW', 'Detroit Tigers': 'DET', 'Houston Astros': 'HOU', 'Kansas City Royals': 'KC',
    'Los Angeles Angels': 'LAA', 'Los Angeles Dodgers': 'LAD', 'Miami Marlins': 'MIA', 'Milwaukee Brewers': 'MIL',
    'Minnesota Twins': 'MIN', 'New York Mets': 'NYM', 'New York Yankees': 'NYY', 'Oakland Athletics': 'OAK',
    'Philadelphia Phillies': 'PHI', 'Pittsburgh Pirates': 'PIT', 'San Diego Padres': 'SD', 'Seattle Mariners': 'SEA',
    'San Francisco Giants': 'SF', 'St. Louis Cardinals': 'STL', 'Tampa Bay Rays': 'TB', 'Texas Rangers': 'TEX',
    'Toronto Blue Jays': 'TOR', 'Washington Nationals': 'WSN'
}


# Function to fetch and process schedules
def fetch_and_process_schedules(year):
    team_abbreviations = list(team_name_to_abbreviation.values())
    all_games = pd.DataFrame()

    for team in team_abbreviations:
        try:
            team_schedule = schedule_and_record(year, team)
            all_games = pd.concat([all_games, team_schedule], ignore_index=True)
        except Exception as e:
            print(f"Failed to retrieve schedule for {team}: {e}")

    all_games = all_games.dropna(subset=['Date', 'Tm', 'Opp'])
    all_games['unique_id'] = all_games.apply(lambda row: row['Date'] + ''.join(sorted([row['Tm'], row['Opp']])), axis=1)
    unique_games = all_games.drop_duplicates(subset=['unique_id'])
    unique_games = unique_games.drop(columns=['unique_id'])
    unique_games['Date'] = pd.to_datetime(unique_games['Date'], errors='coerce', format='%A, %b %d')
    unique_games['Date'] = unique_games['Date'].apply(lambda d: d.replace(year=year) if not pd.isnull(d) else d)
    unique_games_sorted = unique_games.sort_values(by='Date', ascending=True)
    unique_games_sorted = unique_games.reset_index(drop=True)
    unique_games_sorted['id'] = unique_games_sorted.apply(
        lambda row: f"{row['Tm']}_{row['Opp']}_{row['Date'].strftime('%Y%m%d')}" if not pd.isnull(
            row['Date']) else None, axis=1
    )
    unique_games_sorted['Attendance'].replace(r'^Unknown$', np.nan, regex=True, inplace=True)

    return unique_games_sorted


# Function to get or update schedules
def get_or_update_schedules(year):
    if os.path.exists(cache_file):
        modified_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        if datetime.now() - modified_time < timedelta(days=1):
            with open(cache_file, 'r') as file:
                schedules = pd.read_json(file, convert_dates=['Date'])
                if 'id' not in schedules.columns:
                    schedules['id'] = schedules.apply(
                        lambda row: f"{row['Tm']}_{row['Opp']}_{row['Date'].strftime('%Y%m%d')}" if not pd.isnull(
                            row['Date']) else None, axis=1
                    )
                schedules['Attendance'].replace(r'^Unknown$', np.nan, regex=True, inplace=True)
                return schedules

    schedules = fetch_and_process_schedules(year)
    schedules.to_json(cache_file, date_format='iso')
    return schedules


# Function to fetch starting lineups
def fetch_starting_lineups(date):
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch schedule data: {response.status_code}")
        return None

    schedule_data = response.json()
    games = schedule_data.get('dates', [])[0].get('games', [])

    lineup_data = []
    for game in games:
        game_id = game['gamePk']
        game_date = game['officialDate']

        lineup_url = f"https://statsapi.mlb.com/api/v1/game/{game_id}/boxscore"
        lineup_response = requests.get(lineup_url)

        if lineup_response.status_code != 200:
            print(f"Failed to fetch lineup for game {game_id}: {lineup_response.status_code}")
            continue

        lineup_info = lineup_response.json()

        for team in ['home', 'away']:
            team_info = lineup_info['teams'][team]
            team_name = team_info['team']['name']
            team_abbr = team_name_to_abbreviation.get(team_name)
            if not team_abbr:
                print(f"Warning: No abbreviation found for team {team_name}")
                continue

            starting_pitcher_id = team_info['pitchers'][0] if team_info['pitchers'] else None
            for player in team_info['players'].values():
                player_position = player.get('position', {}).get('abbreviation', '')
                if 'battingOrder' in player or player['person']['id'] == starting_pitcher_id:
                    player_info = {
                        'game_id': game_id,
                        'game_date': game_date,
                        'team': team_name,
                        'team_abbr': team_abbr,
                        'player_id': player['person']['id'],
                        'player_name': player['person']['fullName'],
                        'batting_order': player.get('battingOrder', ''),
                        'position': player_position
                    }
                    lineup_data.append(player_info)

    lineups_df = pd.DataFrame(lineup_data)
    return lineups_df


# Function to get today's lineups for all teams
def get_todays_lineups(date):
    schedules = get_or_update_schedules(date.year)
    games_today = schedules[schedules['Date'] == date]

    if games_today.empty:
        print(f"No games found for {date}")
        return None

    lineups = fetch_starting_lineups(date.strftime('%Y-%m-%d'))
    if lineups is None:
        print(f"No lineups found for {date}")
        return None

    # Sort by team abbreviation and batting order
    lineups_sorted = lineups.sort_values(by=['team_abbr', 'batting_order'])
    return lineups_sorted


# Define the date we are interested in
date_to_check = datetime.strptime('2024-06-13', '%Y-%m-%d')

# Get today's lineups
todays_lineups = get_todays_lineups(date_to_check)

# Print the lineups
if todays_lineups is not None:
    for team_abbr, group in todays_lineups.groupby('team_abbr'):
        print(f"Team: {team_abbr}")
        print("Starting Lineup:")
        print(group[['player_name', 'position', 'batting_order', 'player_id']])
        print("=" * 50)

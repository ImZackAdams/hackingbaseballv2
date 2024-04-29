import os
from datetime import datetime, timedelta
import requests
import pandas as pd
from pybaseball import schedule_and_record

# Define the cache file location, ideally this should be set via configuration
cache_file = 'game_schedules.json'


def fetch_and_process_schedules(year):
    # Abbreviations for all teams
    team_abbreviations = [
        'ARI', 'ATL', 'BAL', 'BOS', 'CHC',
        'CIN', 'CLE', 'COL', 'CHW', 'DET',
        'HOU', 'KC', 'LAA', 'LAD', 'MIA',
        'MIL', 'MIN', 'NYM', 'NYY', 'OAK',
        'PHI', 'PIT', 'SD', 'SEA', 'SF',
        'STL', 'TB', 'TEX', 'TOR', 'WSN'
    ]

    all_games = pd.DataFrame()

    # Fetch schedules for all teams
    for team in team_abbreviations:
        try:
            team_schedule = schedule_and_record(year, team)
            all_games = pd.concat([all_games, team_schedule], ignore_index=True)
        except Exception as e:
            print(f"Failed to retrieve schedule for {team}: {e}")

    # Process the gathered data
    all_games = all_games.dropna(subset=['Date', 'Tm', 'Opp'])
    all_games['unique_id'] = all_games.apply(lambda row: row['Date'] + ''.join(sorted([row['Tm'], row['Opp']])), axis=1)
    unique_games = all_games.drop_duplicates(subset=['unique_id'])
    unique_games = unique_games.drop(columns=['unique_id'])
    unique_games['Date'] = pd.to_datetime(unique_games['Date'], errors='coerce', format='%A, %b %d')
    unique_games['Date'] = unique_games['Date'].apply(lambda d: d.replace(year=year))
    unique_games_sorted = unique_games.sort_values(by='Date', ascending=True)
    unique_games_sorted = unique_games_sorted.reset_index(drop=True)

    return unique_games_sorted


def get_or_update_schedules(year):
    # Check if the cached file exists and is up-to-date
    if os.path.exists(cache_file):
        modified_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        if datetime.now() - modified_time < timedelta(days=1):
            with open(cache_file, 'r') as file:
                return pd.read_json(file, convert_dates=['Date'])

    # If not, fetch, process, and cache the schedules
    schedules = fetch_and_process_schedules(year)
    schedules.to_json(cache_file, date_format='iso')
    return schedules

def get_team_roster(team_id):
    url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}/roster"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Ensure we catch any errors related to the HTTP request
        roster_data = response.json()

        roster = []
        for player in roster_data['roster']:
            player_info = {
                'id': player['person']['id'],
                'name': player['person']['fullName'],
                'position': player['position']['name']
            }
            roster.append(player_info)

        return roster
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    return None

# Example usage
team_id = 147  # Example for New York Yankees
roster = get_team_roster(team_id)
for player in roster:
    print(player['name'], "-", player['position'], "-" ,player['id'])
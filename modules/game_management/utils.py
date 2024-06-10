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
def get_today_lineups_for_all_teams():
    today_date = datetime.now().strftime("%Y-%m-%d")
    lineups = fetch_starting_lineups(today_date)
    if lineups is None:
        print("Failed to fetch lineups.")
        return None

    starting_lineup_and_pitcher = lineups[(lineups['batting_order'] != '') | (lineups['position'] == 'P')]
    return starting_lineup_and_pitcher

# Function to get today's schedules and lineups
def get_today_schedules_and_lineups(year):
    today_date = datetime.now().strftime("%Y-%m-%d")
    schedules = get_or_update_schedules(year)
    todays_games = schedules[schedules['Date'] == today_date]

    if todays_games.empty:
        print("No games scheduled for today.")
        return None

    lineups = get_today_lineups_for_all_teams()
    if lineups is None:
        print("Failed to fetch lineups.")
        return None

    lineups['game_date'] = pd.to_datetime(lineups['game_date'])

    home_merged = pd.merge(todays_games, lineups, left_on=['Tm', 'Date'], right_on=['team_abbr', 'game_date'],
                           how='left', suffixes=('', '_home'))
    away_merged = pd.merge(todays_games, lineups, left_on=['Opp', 'Date'], right_on=['team_abbr', 'game_date'],
                           how='left', suffixes=('', '_away'))

    return home_merged, away_merged

# Function to display lineups for each game
def display_lineups_for_each_game(home_data, away_data):
    games = home_data[['Date', 'Tm', 'Opp']].drop_duplicates()
    for _, game in games.iterrows():
        date = game['Date']
        home_team = game['Tm']
        away_team = game['Opp']

        print(f"Game Date: {date}")
        print(f"{home_team} vs {away_team}")

        print(f"{home_team} lineup:")
        home_lineup = home_data[(home_data['Tm'] == home_team) & (home_data['Date'] == date)]
        print(home_lineup[['player_name', 'position', 'batting_order']])

        print(f"\n{away_team} lineup:")
        away_lineup = away_data[(away_data['Opp'] == away_team) & (away_data['Date'] == date)]
        print(away_lineup[['player_name', 'position', 'batting_order']])

        print("\n" + "-" * 40 + "\n")

# Test case
if __name__ == "__main__":
    year = datetime.now().year
    home_data, away_data = get_today_schedules_and_lineups(year)
    if home_data is not None and away_data is not None:
        display_lineups_for_each_game(home_data, away_data)

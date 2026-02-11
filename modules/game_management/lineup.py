import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import requests
from pybaseball import schedule_and_record

CACHE_FILE = "game_schedules.json"
MLB_API_BASE = "https://statsapi.mlb.com/api/v1"
DEFAULT_TIMEOUT = 15

# Dictionary to map full team names to abbreviations
TEAM_NAME_TO_ABBR = {
    'Arizona Diamondbacks': 'ARI', 'Atlanta Braves': 'ATL', 'Baltimore Orioles': 'BAL', 'Boston Red Sox': 'BOS',
    'Chicago Cubs': 'CHC', 'Cincinnati Reds': 'CIN', 'Cleveland Guardians': 'CLE', 'Colorado Rockies': 'COL',
    'Chicago White Sox': 'CHW', 'Detroit Tigers': 'DET', 'Houston Astros': 'HOU', 'Kansas City Royals': 'KC',
    'Los Angeles Angels': 'LAA', 'Los Angeles Dodgers': 'LAD', 'Miami Marlins': 'MIA', 'Milwaukee Brewers': 'MIL',
    'Minnesota Twins': 'MIN', 'New York Mets': 'NYM', 'New York Yankees': 'NYY', 'Oakland Athletics': 'OAK',
    'Philadelphia Phillies': 'PHI', 'Pittsburgh Pirates': 'PIT', 'San Diego Padres': 'SD', 'Seattle Mariners': 'SEA',
    'San Francisco Giants': 'SF', 'St. Louis Cardinals': 'STL', 'Tampa Bay Rays': 'TB', 'Texas Rangers': 'TEX',
    'Toronto Blue Jays': 'TOR', 'Washington Nationals': 'WSN'
}


def _normalize_attendance(df):
    if "Attendance" in df.columns:
        df["Attendance"] = df["Attendance"].replace(r"^Unknown$", np.nan, regex=True)
    return df


def _add_game_id(df):
    if "id" not in df.columns:
        df["id"] = df.apply(
            lambda row: f"{row['Tm']}_{row['Opp']}_{row['Date'].strftime('%Y%m%d')}"
            if not pd.isnull(row["Date"])
            else None,
            axis=1,
        )
    return df


def fetch_and_process_schedules(year):
    team_abbreviations = list(TEAM_NAME_TO_ABBR.values())
    team_schedules = []

    for team in team_abbreviations:
        try:
            team_schedule = schedule_and_record(year, team)
            team_schedules.append(team_schedule)
        except Exception as e:
            print(f"Failed to retrieve schedule for {team}: {e}")

    if not team_schedules:
        return pd.DataFrame()

    all_games = pd.concat(team_schedules, ignore_index=True)
    all_games = all_games.dropna(subset=['Date', 'Tm', 'Opp'])
    all_games['unique_id'] = all_games.apply(lambda row: row['Date'] + ''.join(sorted([row['Tm'], row['Opp']])), axis=1)
    unique_games = all_games.drop_duplicates(subset=['unique_id'])
    unique_games = unique_games.drop(columns=['unique_id'])
    unique_games['Date'] = pd.to_datetime(unique_games['Date'], errors='coerce', format='%A, %b %d')
    unique_games['Date'] = unique_games['Date'].apply(lambda d: d.replace(year=year) if not pd.isnull(d) else d)
    unique_games_sorted = unique_games.sort_values(by='Date', ascending=True)
    unique_games_sorted = unique_games_sorted.reset_index(drop=True)
    unique_games_sorted = _add_game_id(unique_games_sorted)
    unique_games_sorted = _normalize_attendance(unique_games_sorted)

    return unique_games_sorted


def _load_cached_schedules():
    if not os.path.exists(CACHE_FILE):
        return None

    modified_time = datetime.fromtimestamp(os.path.getmtime(CACHE_FILE))
    if datetime.now() - modified_time >= timedelta(days=1):
        return None

    with open(CACHE_FILE, "r") as file:
        schedules = pd.read_json(file, convert_dates=["Date"])
    schedules = _add_game_id(schedules)
    schedules = _normalize_attendance(schedules)
    return schedules


def _save_schedules(schedules):
    schedules.to_json(CACHE_FILE, date_format="iso")


def get_or_update_schedules(year):
    schedules = _load_cached_schedules()
    if schedules is not None:
        return schedules

    schedules = fetch_and_process_schedules(year)
    _save_schedules(schedules)
    return schedules


def fetch_starting_lineups(date):
    url = f"{MLB_API_BASE}/schedule?sportId=1&date={date}"
    try:
        response = requests.get(url, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch schedule data: {e}")
        return None

    schedule_data = response.json()
    dates = schedule_data.get("dates", [])
    if not dates:
        return pd.DataFrame()
    games = dates[0].get("games", [])

    lineup_data = []
    for game in games:
        game_id = game["gamePk"]
        game_date = game["officialDate"]

        lineup_url = f"{MLB_API_BASE}/game/{game_id}/boxscore"
        try:
            lineup_response = requests.get(lineup_url, timeout=DEFAULT_TIMEOUT)
            lineup_response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to fetch lineup for game {game_id}: {e}")
            continue

        lineup_info = lineup_response.json()

        for team in ['home', 'away']:
            team_info = lineup_info["teams"].get(team, {})
            team_name = team_info.get("team", {}).get("name")
            pitchers = team_info.get("pitchers") or []
            starting_pitcher_id = pitchers[0] if pitchers else None
            for player in team_info.get("players", {}).values():
                player_position = player.get("position", {}).get("abbreviation", "")
                # Only include players with a batting order or starting pitchers
                player_id = player.get("person", {}).get("id")
                if "battingOrder" in player or player_id == starting_pitcher_id:
                    player_info = {
                        'game_id': game_id,
                        'game_date': game_date,
                        'team': team_name,
                        'team_abbr': TEAM_NAME_TO_ABBR.get(team_name, None),  # Add abbreviation
                        'player_id': player_id,
                        'player_name': player.get("person", {}).get("fullName"),
                        'batting_order': player.get("battingOrder", ""),
                        'position': player_position
                    }
                    lineup_data.append(player_info)

    return pd.DataFrame(lineup_data)


def get_lineups_for_date(date):
    lineups = fetch_starting_lineups(date)
    if lineups is None:
        print("Failed to fetch lineups.")
        return None

    # Ensure 'team_abbr' column is present
    if 'team_abbr' not in lineups.columns:
        lineups['team_abbr'] = lineups['team'].map(TEAM_NAME_TO_ABBR)

    # Filter for starting batting lineup and starting pitchers
    starting_lineup_and_pitcher = lineups[
        (lineups['batting_order'] != '') | (lineups['position'] == 'P')]

    # Sort by team and batting order to get the correct lineup order
    starting_lineup_and_pitcher = starting_lineup_and_pitcher.sort_values(by=['team', 'batting_order'])

    return starting_lineup_and_pitcher


def get_yesterday_lineups_for_teams():
    yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    return get_lineups_for_date(yesterday_date)


if __name__ == "__main__":
    # Set pandas display options to show all columns
    pd.set_option('display.max_columns', None)
    pd.set_option('display.expand_frame_repr', False)

    year = datetime.now().year
    schedules = get_or_update_schedules(year)
    print("Schedules for the year:")
    print(schedules)

    lineups_yesterday = get_yesterday_lineups_for_teams()
    if lineups_yesterday is not None:
        print("Starting lineups for yesterday:")
        print(lineups_yesterday)

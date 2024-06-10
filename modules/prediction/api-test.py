import requests
import json


def fetch_schedule(date):
    schedule_url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date}"
    schedule_response = requests.get(schedule_url)

    if schedule_response.status_code == 200:
        schedule_data = schedule_response.json()
        games = schedule_data.get('dates', [])[0].get('games', [])
        return games
    else:
        print(f"Failed to fetch schedule data: {schedule_response.status_code}")
        return None


def find_tbr_game_id(games):
    for game in games:
        home_team = game['teams']['home']['team']['name']
        away_team = game['teams']['away']['team']['name']
        if 'Tampa Bay Rays' in [home_team, away_team]:
            game_id = game['gamePk']
            print(f"Game ID for TBR: {game_id}")
            return game_id
    print("Tampa Bay Rays game not found for the given date.")
    return None


def fetch_lineup(game_id):
    lineup_url = f"https://statsapi.mlb.com/api/v1/game/{game_id}/boxscore"
    lineup_response = requests.get(lineup_url)

    if lineup_response.status_code == 200:
        lineup_data = lineup_response.json()
        return lineup_data
    else:
        print(f"Failed to fetch lineup for game {game_id}: {lineup_response.status_code}")
        return None


def get_starting_pitcher(team_info):
    starting_pitcher_id = team_info['pitchers'][0]  # First pitcher listed is typically the starter
    starting_pitcher_info = team_info['players'][f'ID{starting_pitcher_id}']
    starting_pitcher_name = starting_pitcher_info['person']['fullName']
    return starting_pitcher_name


def print_lineup_data(lineup_data):
    home_team = lineup_data['teams']['home']['team']['name']
    away_team = lineup_data['teams']['away']['team']['name']

    print(f"\n{home_team} lineup:")
    starting_pitcher = get_starting_pitcher(lineup_data['teams']['home'])
    print(f"Starting Pitcher: {starting_pitcher}")
    for player_id, player in lineup_data['teams']['home']['players'].items():
        player_name = player['person']['fullName']
        player_position = player['position']['abbreviation']
        batting_order = player.get('battingOrder', 'N/A')
        if batting_order != 'N/A':
            print(f"{player_name} - {player_position} - Batting Order: {batting_order}")

    print(f"\n{away_team} lineup:")
    starting_pitcher = get_starting_pitcher(lineup_data['teams']['away'])
    print(f"Starting Pitcher: {starting_pitcher}")
    for player_id, player in lineup_data['teams']['away']['players'].items():
        player_name = player['person']['fullName']
        player_position = player['position']['abbreviation']
        batting_order = player.get('battingOrder', 'N/A')
        if batting_order != 'N/A':
            print(f"{player_name} - {player_position} - Batting Order: {batting_order}")


def main():
    date = '2024-06-09'  # Set the date you want to test
    games = fetch_schedule(date)

    if games:
        game_id = find_tbr_game_id(games)
        if game_id:
            lineup_data = fetch_lineup(game_id)
            if lineup_data:
                print_lineup_data(lineup_data)


if __name__ == "__main__":
    main()

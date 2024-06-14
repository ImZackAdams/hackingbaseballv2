import requests


# Function to get the starting lineup for a specific date
def get_starting_lineup(date):
    # MLB API endpoint for the schedule
    schedule_endpoint = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date}"

    # Make the request to the API
    response = requests.get(schedule_endpoint)
    data = response.json()

    # Iterate over the games and get the starting lineups
    for game in data['dates'][0]['games']:
        game_id = game['gamePk']
        lineup_endpoint = f"https://statsapi.mlb.com/api/v1/game/{game_id}/boxscore"
        lineup_response = requests.get(lineup_endpoint)
        lineup_data = lineup_response.json()

        away_team = game['teams']['away']['team']['name']
        home_team = game['teams']['home']['team']['name']

        print(f"Game: {away_team} at {home_team}")
        print("Starting Lineups:")

        # Print away team lineup
        print(f"Away: {away_team}")
        starting_pitcher_found = False
        for player_id, player_info in lineup_data['teams']['away']['players'].items():
            if 'battingOrder' in player_info:
                print(
                    f"{player_info['battingOrder']}: {player_info['person']['fullName']} - {player_info['position']['abbreviation']}")
            if player_info['position']['abbreviation'] == 'P' and not starting_pitcher_found:
                print(f"SP: {player_info['person']['fullName']} - {player_info['position']['abbreviation']}")
                starting_pitcher_found = True

        # Print home team lineup
        print(f"Home: {home_team}")
        starting_pitcher_found = False
        for player_id, player_info in lineup_data['teams']['home']['players'].items():
            if 'battingOrder' in player_info:
                print(
                    f"{player_info['battingOrder']}: {player_info['person']['fullName']} - {player_info['position']['abbreviation']}")
            if player_info['position']['abbreviation'] == 'P' and not starting_pitcher_found:
                print(f"SP: {player_info['person']['fullName']} - {player_info['position']['abbreviation']}")
                starting_pitcher_found = True

        print("\n")


# Specify the date for the games
yesterday = "2024-06-13"
get_starting_lineup(yesterday)

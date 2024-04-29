import requests


def get_team_roster(team_id):
    url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}/roster"
    response = requests.get(url)
    roster_data = response.json()

    # Extracting player names and positions from the roster
    for player in roster_data['roster']:
        print(player['person']['fullName'], "-", player['position']['name'])


# Example for New York Yankees (you need to replace 'team_id' with the actual ID)
get_team_roster(team_id=147)
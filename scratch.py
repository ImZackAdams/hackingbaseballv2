import requests
from datetime import datetime


def get_game_data(game_pk):
    base_url = "https://statsapi.mlb.com/api/v1.1"
    game_endpoint = f"/game/{game_pk}/feed/live"

    game_response = requests.get(f"{base_url}{game_endpoint}")

    if game_response.status_code == 200:
        game_data = game_response.json()

        result = {
            'game_info': get_game_info(game_data),
            'status': game_data['gameData']['status']['detailedState'],
            'date': datetime.strptime(game_data['gameData']['datetime']['dateTime'], "%Y-%m-%dT%H:%M:%SZ").strftime(
                "%Y-%m-%d"),
        }

        if game_data['gameData']['status']['statusCode'] != 'S':
            result['linescore'] = get_linescore(game_data)

        return result
    else:
        print(f"Error: Unable to fetch data. Status code: {game_response.status_code}")
        return None


def get_game_info(game_data):
    return {
        'home_team': game_data['gameData']['teams']['home']['name'],
        'away_team': game_data['gameData']['teams']['away']['name'],
        'venue': game_data['gameData']['venue']['name'],
        'weather': game_data['gameData'].get('weather', 'Not available'),
    }


def get_linescore(game_data):
    linescore = game_data['liveData']['linescore']
    return {
        'home_score': linescore['teams']['home'].get('runs', 'N/A'),
        'away_score': linescore['teams']['away'].get('runs', 'N/A'),
        'inning': f"{linescore.get('currentInningOrdinal', 'N/A')} {linescore.get('inningState', '')}".strip(),
    }


# Example usage
game_pk = 747014  # This is the game ID from your original URL
game_data = get_game_data(game_pk)
print(game_data)
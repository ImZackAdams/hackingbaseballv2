import requests
from datetime import datetime


def get_detailed_game_data(game_pk):
    base_url = "https://statsapi.mlb.com/api/v1.1"
    game_endpoint = f"/game/{game_pk}/feed/live"

    response = requests.get(f"{base_url}{game_endpoint}")

    if response.status_code == 200:
        data = response.json()

        result = {
            'game_info': get_game_info(data),
            'linescore': get_linescore(data),
            'batting_stats': get_batting_stats(data),
            'pitching_stats': get_pitching_stats(data),
            'highlights': get_highlights(data)
        }

        return result
    else:
        print(f"Error: Unable to fetch data. Status code: {response.status_code}")
        return None


def get_game_info(data):
    game_data = data['gameData']
    return {
        'home_team': game_data['teams']['home']['name'],
        'away_team': game_data['teams']['away']['name'],
        'venue': game_data['venue']['name'],
        'date': datetime.strptime(game_data['datetime']['dateTime'], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d"),
        'status': game_data['status']['detailedState'],
        'weather': game_data.get('weather', {}).get('condition', 'Not available'),
        'temp': game_data.get('weather', {}).get('temp', 'Not available'),
        'wind': game_data.get('weather', {}).get('wind', 'Not available')
    }


def get_linescore(data):
    linescore = data['liveData']['linescore']
    return {
        'home_score': linescore['teams']['home']['runs'],
        'away_score': linescore['teams']['away']['runs'],
        'inning': f"{linescore['currentInningOrdinal']} {linescore['inningState']}".strip(),
    }


def get_batting_stats(data):
    batting_stats = {}
    for team in ['away', 'home']:
        batting_stats[team] = []
        for player in data['liveData']['boxscore']['teams'][team]['batters']:
            player_data = data['liveData']['boxscore']['teams'][team]['players'][f'ID{player}']
            stats = player_data['stats']['batting']
            batting_stats[team].append({
                'name': player_data['person']['fullName'],
                'position': player_data['position']['abbreviation'],
                'ab': stats.get('atBats', 0),
                'r': stats.get('runs', 0),
                'h': stats.get('hits', 0),
                'rbi': stats.get('rbi', 0),
                'bb': stats.get('baseOnBalls', 0),
                'so': stats.get('strikeOuts', 0),
                'avg': stats.get('avg', '.000'),
                'ops': stats.get('ops', '.000')
            })
    return batting_stats


def get_pitching_stats(data):
    pitching_stats = {}
    for team in ['away', 'home']:
        pitching_stats[team] = []
        for player in data['liveData']['boxscore']['teams'][team]['pitchers']:
            player_data = data['liveData']['boxscore']['teams'][team]['players'][f'ID{player}']
            stats = player_data['stats']['pitching']
            pitching_stats[team].append({
                'name': player_data['person']['fullName'],
                'ip': stats.get('inningsPitched', '0.0'),
                'h': stats.get('hits', 0),
                'r': stats.get('runs', 0),
                'er': stats.get('earnedRuns', 0),
                'bb': stats.get('baseOnBalls', 0),
                'so': stats.get('strikeOuts', 0),
                'hr': stats.get('homeRuns', 0),
                'era': stats.get('era', '0.00')
            })
    return pitching_stats


def get_highlights(data):
    highlights = []
    for highlight in data.get('highlights', {}).get('highlights', {}).get('items', []):
        highlights.append({
            'title': highlight['headline'],
            'description': highlight['description'],
            'duration': highlight['duration'],
            'video_url': next((p['url'] for p in highlight['playbacks'] if p['name'] == 'mp4Avc'), None)
        })
    return highlights


# Example usage
game_pk = 747014  # This is the game ID from your original URL
detailed_game_data = get_detailed_game_data(game_pk)
print(detailed_game_data)
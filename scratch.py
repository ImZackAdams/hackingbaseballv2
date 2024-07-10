import os

import requests
from datetime import datetime
import time


def get_schedule(date):
    base_url = "https://statsapi.mlb.com/api/v1"
    schedule_endpoint = f"/schedule?date={date}&sportId=1"

    url = f"{base_url}{schedule_endpoint}"
    print(f"Requesting schedule from: {url}")

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: Unable to fetch schedule. Status code: {response.status_code}")
        print(f"Response content: {response.text}")
        return None


def get_detailed_game_data(game_pk):
    base_url = "https://statsapi.mlb.com/api/v1.1"
    game_endpoint = f"/game/{game_pk}/feed/live"

    url = f"{base_url}{game_endpoint}"
    print(f"Requesting game data from: {url}")

    response = requests.get(url)

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
        print(f"Error: Unable to fetch game data. Status code: {response.status_code}")
        print(f"Response content: {response.text}")
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
        'home_score': linescore['teams']['home'].get('runs', 'N/A'),
        'away_score': linescore['teams']['away'].get('runs', 'N/A'),
        'inning': f"{linescore.get('currentInningOrdinal', 'N/A')} {linescore.get('inningState', '')}".strip(),
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


def get_all_games_data(date):
    schedule = get_schedule(date)
    all_games_data = []

    if schedule:
        if 'dates' in schedule and len(schedule['dates']) > 0:
            games = schedule['dates'][0]['games']
            for game in games:
                game_pk = game['gamePk']
                game_data = get_detailed_game_data(game_pk)
                if game_data:
                    all_games_data.append(game_data)
                time.sleep(1)  # Add a 1-second delay between requests
        else:
            print(f"No games scheduled for {date}")
    else:
        print("Failed to retrieve schedule")

    return all_games_data


# Example usage
date = "2024-07-09"
all_games_data = get_all_games_data(date)

if all_games_data:
    for game in all_games_data:
        print(f"Game: {game['game_info']['away_team']} at {game['game_info']['home_team']}")
        print(f"Score: {game['linescore']['away_score']} - {game['linescore']['home_score']}")
        print("---")
else:
    print("No game data retrieved")

import matplotlib.pyplot as plt


def create_batting_chart(game_data):
    print("Starting to create batting chart...")

    try:
        away_team = game_data['game_info']['away_team']
        home_team = game_data['game_info']['home_team']

        away_batters = game_data['batting_stats']['away']
        home_batters = game_data['batting_stats']['home']

        print(f"Processing data for {away_team} vs {home_team}")

        # Sort batters by hits and get top 5
        away_top5 = sorted(away_batters, key=lambda x: x['h'], reverse=True)[:5]
        home_top5 = sorted(home_batters, key=lambda x: x['h'], reverse=True)[:5]

        # Prepare data for plotting
        players = [player['name'] for player in away_top5 + home_top5]
        hits = [player['h'] for player in away_top5 + home_top5]
        rbis = [player['rbi'] for player in away_top5 + home_top5]

        print("Data prepared, creating plot...")

        # Set up the plot
        plt.figure(figsize=(12, 6))

        # Plot bars
        x = range(len(players))
        plt.bar([i - 0.2 for i in x], hits, 0.4, label='Hits')
        plt.bar([i + 0.2 for i in x], rbis, 0.4, label='RBIs')

        # Customize the plot
        plt.ylabel('Count')
        plt.title(f'Top 5 Batters: {away_team} vs {home_team}')
        plt.xticks(x, players, rotation=45, ha='right')
        plt.legend()

        # Add a vertical line to separate teams
        plt.axvline(x=4.5, color='red', linestyle='--')

        plt.tight_layout()

        print("Plot created, attempting to save...")

        # Get the current working directory
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, 'batting_chart.png')

        plt.savefig(file_path)
        print(f"Chart saved as '{file_path}'")

        plt.close()

        # Verify if the file was created
        if os.path.exists(file_path):
            print(f"File successfully created at {file_path}")
            print(f"File size: {os.path.getsize(file_path)} bytes")
        else:
            print(f"File was not created at {file_path}")

    except Exception as e:
        print(f"Error in create_batting_chart: {e}")
        import traceback
        traceback.print_exc()


def main():
    date = "2024-07-09"
    all_games_data = get_all_games_data(date)

    if all_games_data:
        for game in all_games_data:
            print(f"Game: {game['game_info']['away_team']} at {game['game_info']['home_team']}")
            print(f"Score: {game['linescore']['away_score']} - {game['linescore']['home_score']}")
            print("---")

        # Create and save the chart for the first game
        first_game = all_games_data[0]
        print("Structure of first_game:")
        print(first_game.keys())
        print("Structure of batting_stats:")
        print(first_game['batting_stats'].keys())
        create_batting_chart(first_game)
    else:
        print("No game data retrieved")


if __name__ == "__main__":
    main()

# First, ensure you have PyBaseball installed. Uncomment the line below to install it if you haven't.
# !pip install pybaseball

from pybaseball import team_schedule, team_batting, team_pitching
import pandas as pd

# Define the date we're interested in
date = '2024-06-13'

# List of team abbreviations (you can get the full list from pybaseball documentation or manually list them)
teams = [
    'ARI', 'ATL', 'BAL', 'BOS', 'CHC', 'CHW', 'CIN', 'CLE', 'COL', 'DET', 'HOU',
    'KCR', 'LAA', 'LAD', 'MIA', 'MIL', 'MIN', 'NYM', 'NYY', 'OAK', 'PHI', 'PIT',
    'SDP', 'SEA', 'SFG', 'STL', 'TBR', 'TEX', 'TOR', 'WSN'
]

# Fetch schedules for all teams
schedules = []
for team in teams:
    team_sched = team_schedule(team, 2024)
    team_sched['Team'] = team  # Add a column for the team
    schedules.append(team_sched)

# Combine all team schedules into a single DataFrame
full_schedule = pd.concat(schedules)

# Filter the schedule for games on the specified date
games_on_date = full_schedule[full_schedule['Date'] == date]

# Retrieve team batting and pitching data
team_batting_data = team_batting(2024)
team_pitching_data = team_pitching(2024)


# Function to get the starting lineup for a given team and game
def get_starting_lineup(team, game_id):
    # Filter batting and pitching data for the given team and game
    batting = team_batting_data[(team_batting_data['Team'] == team) & (team_batting_data['game_id'] == game_id)]
    pitching = team_pitching_data[(team_pitching_data['Team'] == team) & (team_pitching_data['game_id'] == game_id) & (
                team_pitching_data['starter'] == True)]
    return batting, pitching


# Extract the starting lineups and pitchers for each game
starting_lineups = []
for _, game in games_on_date.iterrows():
    home_team = game['Home Team']
    away_team = game['Away Team']
    game_id = game['game_id']

    home_batting, home_pitching = get_starting_lineup(home_team, game_id)
    away_batting, away_pitching = get_starting_lineup(away_team, game_id)

    starting_lineups.append({
        'team': home_team,
        'game_id': game_id,
        'batting': home_batting,
        'pitching': home_pitching
    })
    starting_lineups.append({
        'team': away_team,
        'game_id': game_id,
        'batting': away_batting,
        'pitching': away_pitching
    })

# Convert the list of dictionaries to a DataFrame
lineups_df = pd.DataFrame(starting_lineups)

# Sort the DataFrame by team
lineups_df_sorted = lineups_df.sort_values(by='team')

# Print the lineups
for _, row in lineups_df_sorted.iterrows():
    team = row['team']
    game_id = row['game_id']
    print(f"Team: {team} | Game ID: {game_id}")
    print("Starting Batters:")
    print(row['batting'].to_string(index=False))
    print("Starting Pitcher:")
    print(row['pitching'].to_string(index=False))
    print("=" * 50)

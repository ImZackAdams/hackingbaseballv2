import pandas as pd

# Sample data (replace this with actual data loading)
data = {
    'game_pk': [1, 1, 1, 2, 2, 2],
    'post_home_score': [0, 2, 4, 0, 3, 5],
    'post_away_score': [0, 1, 1, 0, 2, 4],
    'home_team': ['A', 'A', 'A', 'B', 'B', 'B'],
    'away_team': ['X', 'X', 'X', 'Y', 'Y', 'Y']
}
df = pd.DataFrame(data)

# Forward fill scores to ensure the last known score is carried forward within each game
df['post_home_score'] = df.groupby('game_pk')['post_home_score'].ffill().bfill()
df['post_away_score'] = df.groupby('game_pk')['post_away_score'].ffill().bfill()

# Determine the final scores for each game
final_scores = df.groupby('game_pk').agg({'post_home_score': 'last', 'post_away_score': 'last'}).reset_index()

# Determine the winning team based on final scores
final_scores['winning_team'] = (final_scores['post_home_score'] > final_scores['post_away_score']).astype(int)

# Merge the winning team back into the main dataframe
df = df.merge(final_scores[['game_pk', 'winning_team']], on='game_pk', how='left')

# Debugging output
print("Sample of games and their final scores:")
sample_games = df[['game_pk', 'post_home_score', 'post_away_score', 'winning_team']].drop_duplicates()
print(sample_games)

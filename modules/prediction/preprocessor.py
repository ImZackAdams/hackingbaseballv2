import pandas as pd

def preprocess_data(df):
    # Filter and select relevant columns
    relevant_columns = ['game_date', 'game_pk', 'pitcher', 'batter', 'events', 'home_team', 'away_team',
                        'post_home_score', 'post_away_score']
    df = df[relevant_columns].copy()

    # Ensure 'pitcher' and 'batter' columns are treated as strings
    df['pitcher'] = df['pitcher'].astype(str)
    df['batter'] = df['batter'].astype(str)

    # Create binary flags for hits and walks
    df['is_hit'] = df['events'].isin(['single', 'double', 'triple', 'home_run']).astype(int)
    df['is_walk'] = (df['events'] == 'walk').astype(int)

    # Determine the winning team for each game
    df['winning_team'] = df.groupby('game_pk')['post_home_score'].transform(
        lambda x: (x.iloc[-1] > df.groupby('game_pk')['post_away_score'].transform('last')).astype(int))

    # Fill NaN values with 0
    df.fillna(0, inplace=True)

    return df

def engineer_features(df):
    # Aggregate data for pitcher-batter matchups
    matchup_stats = df.groupby(['pitcher', 'batter']).agg({
        'is_hit': 'sum',
        'is_walk': 'sum',
        'game_pk': 'count'
    }).reset_index()

    matchup_stats.rename(columns={'game_pk': 'at_bats'}, inplace=True)
    matchup_stats['batting_average'] = matchup_stats['is_hit'] / matchup_stats['at_bats']
    matchup_stats['on_base_percentage'] = (matchup_stats['is_hit'] + matchup_stats['is_walk']) / matchup_stats['at_bats']

    # Merge matchup stats with the main DataFrame
    df = df.merge(matchup_stats, on=['pitcher', 'batter'], how='left')

    # Rename columns to original names
    df.rename(columns={
        'is_hit_x': 'is_hit',
        'is_walk_x': 'is_walk',
        'is_hit_y': 'is_hit_agg',
        'is_walk_y': 'is_walk_agg'
    }, inplace=True)

    # Debugging line to check columns before accessing 'is_hit'
    print("DataFrame columns before accessing 'is_hit':", df.columns)
    print("First few rows of the DataFrame:\n", df.head())

    # Create a binary flag for home team
    df['is_home'] = (df['home_team'] == df['pitcher'].str[:3]).astype(int)

    # Create a feature for total bases
    df['total_bases'] = df['is_hit'] * df['events'].map({'single': 1, 'double': 2, 'triple': 3, 'home_run': 4}).fillna(0)

    return df

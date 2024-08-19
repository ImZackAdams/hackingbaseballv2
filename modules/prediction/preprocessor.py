import pandas as pd
import numpy as np


def preprocess_data(df):
    # Create a copy of the dataframe to avoid SettingWithCopyWarning
    df = df.copy()

    # Filter and select relevant columns
    relevant_columns = ['game_date', 'game_pk', 'pitcher', 'batter', 'events', 'home_team', 'away_team',
                        'post_home_score', 'post_away_score']
    df = df[relevant_columns]

    # Check if 'events' column exists
    if 'events' not in df.columns:
        print("Warning: 'events' column not found. Setting 'is_hit' and 'is_walk' to 0.")
        df['is_hit'] = 0
        df['is_walk'] = 0
    else:
        # Create binary flags for hits and walks
        df['is_hit'] = df['events'].isin(['single', 'double', 'triple', 'home_run']).astype(int)
        df['is_walk'] = (df['events'] == 'walk').astype(int)

    # Aggregate data for pitcher-batter matchups
    matchup_stats = df.groupby(['pitcher', 'batter']).agg({
        'is_hit': 'sum',
        'is_walk': 'sum',
        'game_pk': 'count'
    }).reset_index()

    matchup_stats.rename(columns={'game_pk': 'at_bats'}, inplace=True)
    matchup_stats['batting_average'] = matchup_stats['is_hit'] / matchup_stats['at_bats'].where(
        matchup_stats['at_bats'] > 0, 1)
    matchup_stats['on_base_percentage'] = (matchup_stats['is_hit'] + matchup_stats['is_walk']) / matchup_stats[
        'at_bats'].where(matchup_stats['at_bats'] > 0, 1)

    # Determine the winning team for each game
    df['winning_team'] = (df.groupby('game_pk')['post_home_score'].transform('last') >
                          df.groupby('game_pk')['post_away_score'].transform('last')).astype(int)

    # Merge matchup stats with the main DataFrame
    df = df.merge(matchup_stats, on=['pitcher', 'batter'], how='left', suffixes=('', '_agg'))

    # Create a binary flag for home team
    df['pitcher_team'] = np.where(df['pitcher'] == df['home_team'], df['home_team'], df['away_team'])
    df['is_home'] = (df['pitcher_team'] == df['home_team']).astype(int)

    # Fill NaN values with 0
    df.fillna(0, inplace=True)

    return df


def engineer_features(df):
    # Create a copy of the dataframe to avoid SettingWithCopyWarning
    df = df.copy()

    # Check if 'events' column exists
    if 'events' not in df.columns:
        print("Warning: 'events' column not found. Setting 'total_bases' to 0.")
        df['total_bases'] = 0
    else:
        # Create a feature for total bases
        df['total_bases'] = df['is_hit'] * (
            df['events'].map({'single': 1, 'double': 2, 'triple': 3, 'home_run': 4}).fillna(0))

    return df


def print_dataframe_info(df, name):
    print(f"\n{name} DataFrame Info:")
    print(df.info())
    print("\nFirst few rows:")
    print(df.head())
    print("\nColumn names:")
    print(df.columns.tolist())
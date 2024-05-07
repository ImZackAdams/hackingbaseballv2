import pandas as pd


def preprocess_data(df):
    # Filter and select relevant columns
    relevant_columns = ['game_date', 'game_pk', 'pitcher', 'batter', 'events', 'home_team', 'away_team',
                        'post_home_score', 'post_away_score']
    df = df[relevant_columns]

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
    matchup_stats['batting_average'] = matchup_stats['is_hit'] / matchup_stats['at_bats']
    matchup_stats['on_base_percentage'] = (matchup_stats['is_hit'] + matchup_stats['is_walk']) / matchup_stats[
        'at_bats']

    # Determine the winning team for each game
    df['winning_team'] = df.groupby('game_pk')['post_home_score'].transform(
        lambda x: x.iloc[-1] > df.groupby('game_pk')['post_away_score'].transform('last'))

    # Merge matchup stats with the main DataFrame
    df = df.merge(matchup_stats, on=['pitcher', 'batter'], how='left')

    # Create a binary flag for home team
    df['is_home'] = (df['home_team'] == df['pitcher'].str[:3]).astype(int)

    # Fill NaN values with 0
    df.fillna(0, inplace=True)

    return df


def engineer_features(df):
    # Perform additional feature engineering if needed
    # For example, you can create new features based on existing ones or encode categorical variables

    # Example: Create a feature for total bases
    df['total_bases'] = df['is_hit'] * (
        df['events'].map({'single': 1, 'double': 2, 'triple': 3, 'home_run': 4}).fillna(0))

    return df

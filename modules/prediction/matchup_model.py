from sqlalchemy import create_engine
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from modules.prediction.preprocessor import preprocess_data, engineer_features
import os

DATABASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'baseball_data.db'))


def train_model():
    # Load data from the SQLite database
    engine = create_engine(f'sqlite:///{DATABASE_PATH}')
    query = "SELECT * FROM statcast_data"
    df = pd.read_sql(query, engine)

    # Preprocess the data
    preprocessed_df = preprocess_data(df)
    print("Preprocessed DataFrame columns:", preprocessed_df.columns)  # Debugging line

    # Perform feature engineering
    engineered_df = engineer_features(preprocessed_df)
    print("Engineered DataFrame columns:", engineered_df.columns)  # Debugging line

    # Prepare the features and target variable
    X = engineered_df[['batting_average', 'on_base_percentage', 'total_bases', 'is_home']]
    y = engineered_df['winning_team']

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create and train the Random Forest classifier
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Make predictions on the test set
    y_pred = model.predict(X_test)

    # Evaluate the model
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy}")
    print(classification_report(y_test, y_pred))

    # Check if both classes are present in y_test before calculating ROC-AUC score
    if len(set(y_test)) > 1:
        roc_auc = roc_auc_score(y_test, y_pred)
        print(f"ROC-AUC Score: {roc_auc}")
    else:
        print("ROC-AUC Score: Not defined (only one class present in y_test)")

    return model


def prepare_matchup_data(pitcher_id, batter_id, is_home):
    engine = create_engine(f'sqlite:///{DATABASE_PATH}')
    query = "SELECT * FROM statcast_data"
    df = pd.read_sql(query, engine)
    preprocessed_df = preprocess_data(df)
    engineered_df = engineer_features(preprocessed_df)

    matchup_data = engineered_df[(engineered_df['pitcher'] == pitcher_id) & (engineered_df['batter'] == batter_id)]
    if matchup_data.empty:
        return None

    batting_average = matchup_data['batting_average'].mean()
    on_base_percentage = matchup_data['on_base_percentage'].mean()
    total_bases = matchup_data['total_bases'].sum()
    input_data = [[batting_average, on_base_percentage, total_bases, is_home]]

    return input_data


def predict_game_outcome_based_on_lineups(model, lineups):
    game_predictions = []
    skipped_games = []

    for game_id, group in lineups.groupby(['game_id']):
        # Debugging line to check the columns in the group DataFrame
        print("Group DataFrame columns:", group.columns)

        # Check unique values in 'Home_Away' column
        print("Unique values in 'Home_Away' column:", group['Home_Away'].unique())

        # Identify home and away teams based on 'Home_Away' column
        home_team_rows = group[group['Home_Away'] != '@']
        away_team_rows = group[group['Home_Away'] == '@']

        # Debugging lines to check the content of home_team_rows and away_team_rows
        print("Home team rows:\n", home_team_rows)
        print("Away team rows:\n", away_team_rows)

        if home_team_rows.empty:
            print(f"No home team rows for game_id {game_id}. Skipping this game.")
            skipped_games.append((game_id, 'No home team rows'))
            continue

        if away_team_rows.empty:
            print(f"No away team rows for game_id {game_id}. Skipping this game.")
            skipped_games.append((game_id, 'No away team rows'))
            continue

        home_team_abbr = home_team_rows['team_abbr'].iloc[0]
        away_team_abbr = away_team_rows['team_abbr'].iloc[0]

        home_team = group[group['team_abbr'] == home_team_abbr]
        away_team = group[group['team_abbr'] == away_team_abbr]

        home_team_wins = 0
        away_team_wins = 0

        # Predict outcomes for home team batters vs away team pitcher
        away_pitcher_id = away_team.iloc[0]['player_id']  # assuming first player listed is the pitcher
        for _, row in home_team.iterrows():
            batter_id = row['player_id']
            is_home = 1
            matchup_data = prepare_matchup_data(away_pitcher_id, batter_id, is_home)
            if matchup_data is not None:
                prediction = model.predict(matchup_data)
                if prediction == 1:
                    home_team_wins += 1
                else:
                    away_team_wins += 1

        # Predict outcomes for away team batters vs home team pitcher
        home_pitcher_id = home_team.iloc[0]['player_id']  # assuming first player listed is the pitcher
        for _, row in away_team.iterrows():
            batter_id = row['player_id']
            is_home = 0
            matchup_data = prepare_matchup_data(home_pitcher_id, batter_id, is_home)
            if matchup_data is not None:
                prediction = model.predict(matchup_data)
                if prediction == 1:
                    away_team_wins += 1
                else:
                    home_team_wins += 1

        if home_team_wins > away_team_wins:
            game_predictions.append((game_id, home_team_abbr))
        else:
            game_predictions.append((game_id, away_team_abbr))

    print("Skipped games due to missing data:", skipped_games)
    return game_predictions






if __name__ == '__main__':
    from datetime import datetime
    from modules.game_management.utils import get_today_schedules_and_lineups

    # Load today's lineups
    lineups = get_today_schedules_and_lineups(datetime.now().year)

    if lineups is not None:
        # Train the model
        model = train_model()

        # Predict the outcome of each game based on the lineups
        predicted_outcomes = predict_game_outcome_based_on_lineups(model, lineups)
        print(predicted_outcomes)

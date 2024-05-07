
from sqlalchemy import create_engine
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report, roc_auc_score
import os


def train_model():
    # Set display options to show more rows and columns
    pd.set_option('display.max_rows', 100)
    pd.set_option('display.max_columns', 50)

    # Get the absolute path to the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the baseball_data.db file
    db_path = os.path.join(current_dir, 'baseball_data.db')

    # Create the SQLite database engine with the full path
    engine = create_engine(f'sqlite:///{db_path}')

    query = "SELECT * FROM statcast_data LIMIT 1000"
    df = pd.read_sql(query, engine)

    # Create binary flags for hits and walks
    df['is_hit'] = df['events'].isin(['single', 'double', 'triple', 'home_run']).astype(int)
    df['is_walk'] = (df['events'] == 'walk').astype(int)

    # Aggregate data for pitcher-batter matchups
    matchup_stats = df.groupby(['pitcher', 'batter']).agg({
        'is_hit': 'sum',
        'is_walk': 'sum',
        'game_pk': 'count'  # Assuming each row is an at-bat; adjust as necessary
    }).reset_index()

    matchup_stats.rename(columns={'game_pk': 'at_bats'}, inplace=True)
    matchup_stats['batting_average'] = matchup_stats['is_hit'] / matchup_stats['at_bats']
    matchup_stats['on_base_percentage'] = (matchup_stats['is_hit'] + matchup_stats['is_walk']) / matchup_stats[
        'at_bats']

    print(matchup_stats)

    df['winning_team'] = df['post_home_score'] > df['post_away_score']  # Simplification for demonstration
    df = df.merge(matchup_stats, on=['pitcher', 'batter'], how='left')

    # Encode winning_team as binary target variable
    label_encoder = LabelEncoder()
    df['winning_team_encoded'] = label_encoder.fit_transform(df['winning_team'])

    X = df[['batting_average', 'on_base_percentage']].fillna(0)  # Fill NaN values
    y = df['winning_team_encoded']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(random_state=42)

    # Example of hyperparameter grid tuning
    param_grid = {
        'n_estimators': [100, 200, 300],
        'max_depth': [None, 10, 20, 30],
        'min_samples_split': [2, 5, 10]
    }

    grid_search = GridSearchCV(estimator=model, param_grid=param_grid, cv=3, n_jobs=-1, verbose=2)
    grid_search.fit(X_train, y_train)

    # Use the best estimator
    best_model = grid_search.best_estimator_
    y_pred_best = best_model.predict(X_test)
    print("Improved Model Accuracy:", accuracy_score(y_test, y_pred_best))

    print(classification_report(y_test, y_pred_best))
    print("ROC-AUC Score:", roc_auc_score(y_test, y_pred_best))

    return best_model


def predict_game_outcome(lineup_data, model):
    # Perform necessary data preprocessing steps
    preprocessed_data = preprocess_lineup_data(lineup_data)

    # Make predictions using the trained model
    predicted_outcome = model.predict(preprocessed_data)

    return predicted_outcome

from sqlalchemy import create_engine
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from modules.prediction.preprocessor import preprocess_data, engineer_features


def train_model():
    # Load data from the SQLite database
    engine = create_engine('sqlite:///baseball_data.db')
    query = "SELECT * FROM statcast_data"
    df = pd.read_sql(query, engine)

    # Preprocess the data
    preprocessed_df = preprocess_data(df)

    # Perform feature engineering
    engineered_df = engineer_features(preprocessed_df)

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
    print(f"ROC-AUC Score: {roc_auc_score(y_test, y_pred)}")

    return model


def predict_game_outcome(model, pitcher_id, batter_id, is_home):
    # Load the preprocessed data
    engine = create_engine('sqlite:///baseball_data.db')
    query = "SELECT * FROM statcast_data"
    df = pd.read_sql(query, engine)
    preprocessed_df = preprocess_data(df)
    engineered_df = engineer_features(preprocessed_df)

    # Filter the data for the specific pitcher and batter
    matchup_data = engineered_df[(engineered_df['pitcher'] == pitcher_id) & (engineered_df['batter'] == batter_id)]

    if matchup_data.empty:
        print(f"No historical data found for the matchup between pitcher {pitcher_id} and batter {batter_id}.")
        return None

    # Prepare the input features for prediction
    batting_average = matchup_data['batting_average'].mean()
    on_base_percentage = matchup_data['on_base_percentage'].mean()
    total_bases = matchup_data['total_bases'].sum()
    input_data = [[batting_average, on_base_percentage, total_bases, is_home]]

    # Make the prediction
    prediction = model.predict(input_data)

    return prediction[0]


# Example usage
if __name__ == '__main__':
    # Load data for a specific date range
    start_date = date(2020, 4, 1)
    end_date = date(2020, 10, 5)
    load_data(start_date, end_date)

    # Train the model
    model = train_model()

    # Example prediction
    pitcher_id = 123456  # Replace with the desired pitcher's ID
    batter_id = 789012  # Replace with the desired batter's ID
    is_home = 1  # 1 if the pitcher's team is playing at home, 0 otherwise

    outcome = predict_game_outcome(model, pitcher_id, batter_id, is_home)
    if outcome is not None:
        print(f"Predicted game outcome: {'Win' if outcome else 'Loss'}")

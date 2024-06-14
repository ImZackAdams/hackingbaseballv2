import pandas as pd
import sqlite3
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import numpy as np

# Connect to the SQLite database
conn = sqlite3.connect('baseball_data.db')

# Load data into a pandas DataFrame
data = pd.read_sql_query("SELECT * FROM statcast_data", conn)

# Close the connection
conn.close()

# Calculate historical performance metrics
pitcher_batter_stats = data.groupby(['pitcher', 'batter']).agg(
    strikeouts=('events', lambda x: (x == 'strikeout').sum()),
    walks=('events', lambda x: (x == 'walk').sum()),
    hits=('events',
          lambda x: (x == 'single').sum() + (x == 'double').sum() + (x == 'triple').sum() + (x == 'home_run').sum()),
    home_runs=('events', lambda x: (x == 'home_run').sum())
).reset_index()

# Merge game data with pitcher_batter_stats
merged_data = data.merge(pitcher_batter_stats, on=['pitcher', 'batter'], how='left')

# Check if 'post_home_score' and 'post_away_score' are in the data
if 'post_home_score' not in merged_data.columns or 'post_away_score' not in merged_data.columns:
    raise ValueError("Columns 'post_home_score' and 'post_away_score' are required in the data.")

# Aggregate stats for each game by summing the individual player stats
game_stats = merged_data.groupby(['game_date', 'home_team', 'away_team', 'pitcher', 'batter']).agg(
    total_strikeouts=('strikeouts', 'sum'),
    total_walks=('walks', 'sum'),
    total_hits=('hits', 'sum'),
    total_home_runs=('home_runs', 'sum'),
    home_score=('post_home_score', 'max'),
    away_score=('post_away_score', 'max')
).reset_index()

# Determine the winner
game_stats['home_win'] = (game_stats['home_score'] > game_stats['away_score']).astype(int)

# Set pandas to display all columns
pd.set_option('display.max_columns', None)

# Print out the head of the DataFrame before training
print("Head of the DataFrame before training:")
print(game_stats.head())

# Prepare features and labels
X = game_stats[['total_strikeouts', 'total_walks', 'total_hits', 'total_home_runs', 'pitcher', 'batter']]
y = game_stats['home_win']

# Encode labels
encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)

# Check data balance
print("Training set class distribution:", np.bincount(y_train))
print("Test set class distribution:", np.bincount(y_test))

# Impute missing values
imputer = SimpleImputer(strategy='mean')
X_train_imputed = imputer.fit_transform(X_train)
X_test_imputed = imputer.transform(X_test)

# Scale the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_imputed)
X_test_scaled = scaler.transform(X_test_imputed)

# Train the model
model = RandomForestClassifier(random_state=42)
model.fit(X_train_scaled, y_train)

# Evaluate the model
y_pred_train = model.predict(X_train_scaled)
y_pred_test = model.predict(X_test_scaled)

print("Training accuracy:", accuracy_score(y_train, y_pred_train))
print("Test accuracy:", accuracy_score(y_test, y_pred_test))
print("Classification report:\n", classification_report(y_test, y_pred_test))

# Save the model and preprocessors
joblib.dump(model, 'game_outcome_predictor.pkl')
joblib.dump(imputer, 'imputer.pkl')
joblib.dump(scaler, 'scaler.pkl')
joblib.dump(encoder, 'encoder.pkl')


# Function to preprocess today's lineups
def preprocess_data(lineups):
    # Assuming `lineups` is a DataFrame with the necessary columns
    # Extract relevant features for prediction
    features = lineups[['player_id', 'team_abbr', 'position', 'batting_order']]

    # Encode categorical variables
    label_encoders = {}
    for column in ['team_abbr', 'position', 'batting_order']:
        le = LabelEncoder()
        features[column] = le.fit_transform(features[column])
        label_encoders[column] = le

    # Standardize numerical features
    scaler = StandardScaler()
    features[['player_id']] = scaler.fit_transform(features[['player_id']])

    # Aggregate stats for each team (this is a simplified example)
    team_features = features.groupby('team_abbr').mean().reset_index()

    return team_features

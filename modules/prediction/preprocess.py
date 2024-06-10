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

# Filter data for the date range from 2023-01-01 to 2024-06-09
data['game_date'] = pd.to_datetime(data['game_date'])
start_date = pd.Timestamp('2023-01-01')
end_date = pd.Timestamp('2024-06-09')
filtered_data = data[(data['game_date'] >= start_date) & (data['game_date'] <= end_date)]


# Print the first few rows of the data to inspect
print(data.head())

# Calculate historical performance metrics
pitcher_batter_stats = data.groupby(['pitcher', 'batter']).agg(
    strikeouts=('events', lambda x: (x == 'strikeout').sum()),
    walks=('events', lambda x: (x == 'walk').sum()),
    hits=('events', lambda x: (x == 'single').sum() + (x == 'double').sum() + (x == 'triple').sum() + (x == 'home_run').sum()),
    home_runs=('events', lambda x: (x == 'home_run').sum())
).reset_index()

# Print the aggregated stats to inspect
print(pitcher_batter_stats.head())

# Merge game data with pitcher_batter_stats
merged_data = data.merge(pitcher_batter_stats, on=['pitcher', 'batter'], how='left')

# Check if 'post_home_score' and 'post_away_score' are in the data
if 'post_home_score' not in merged_data.columns or 'post_away_score' not in merged_data.columns:
    raise ValueError("Columns 'post_home_score' and 'post_away_score' are required in the data.")

# Aggregate stats for each game by summing the individual player stats
game_stats = merged_data.groupby(['game_date', 'home_team', 'away_team', 'pitcher']).agg({
    'strikeouts': 'sum',
    'walks': 'sum',
    'hits': 'sum',
    'home_runs': 'sum',
    'post_home_score': 'max',
    'post_away_score': 'max'
}).reset_index()

# Create the target variable
game_stats['home_team_win'] = (game_stats['post_home_score'] > game_stats['post_away_score']).astype(int)

# Define features and labels
features = ['strikeouts', 'walks', 'hits', 'home_runs']
X = game_stats[features]
y = game_stats['home_team_win']

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate the model
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Classification Report:\n", classification_report(y_test, y_pred))

# Save the model
joblib.dump(model, 'baseball_game_predictor.pkl')

# Load the model to ensure it was saved correctly
loaded_model = joblib.load('baseball_game_predictor.pkl')

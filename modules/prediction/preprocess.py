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
game_stats = merged_data.groupby(['game_date', 'game_pk', 'home_team', 'away_team']).agg(
    home_score=('post_home_score', 'sum'),
    away_score=('post_away_score', 'sum'),
    total_strikeouts=('strikeouts', 'sum'),
    total_walks=('walks', 'sum'),
    total_hits=('hits', 'sum'),
    total_home_runs=('home_runs', 'sum')
).reset_index()

# Create a target variable 'result'
game_stats['result'] = np.where(game_stats['home_score'] > game_stats['away_score'], 1, 0)

# Select features and target variable
X = game_stats[['total_strikeouts', 'total_walks', 'total_hits', 'total_home_runs']]
y = game_stats['result']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Impute missing values
imputer = SimpleImputer(strategy='mean')
X_train = imputer.fit_transform(X_train)
X_test = imputer.transform(X_test)

# Scale the features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Encode the target variable
encoder = LabelEncoder()
y_train = encoder.fit_transform(y_train)
y_test = encoder.transform(y_test)

# Train a RandomForestClassifier
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate the model
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# Save the model
joblib.dump(model, 'baseball_model.pkl')
joblib.dump(imputer, 'imputer.pkl')
joblib.dump(scaler, 'scaler.pkl')
joblib.dump(encoder, 'encoder.pkl')

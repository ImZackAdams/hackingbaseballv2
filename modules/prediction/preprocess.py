import pandas as pd
import sqlite3
from sklearn.model_selection import train_test_split, GridSearchCV, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from imblearn.over_sampling import SMOTE
import joblib
import numpy as np
import time

# Connect to the SQLite database
conn = sqlite3.connect('baseball_data.db')

# Load data into a pandas DataFrame and limit to 50,000 rows
query = "SELECT pitcher, batter, game_date, events, post_home_score, post_away_score FROM statcast_data WHERE game_date BETWEEN '2023-04-01' AND '2024-06-09' LIMIT 700000"
data = pd.read_sql_query(query, conn)

# Close the connection
conn.close()

# Ensure data has the required columns
required_columns = ['pitcher', 'batter', 'game_date', 'events', 'post_home_score', 'post_away_score']
missing_columns = [col for col in required_columns if col not in data.columns]
if missing_columns:
    raise ValueError(f"Missing columns in the data: {missing_columns}")

# Handle missing values
imputer = SimpleImputer(strategy='mean')
data[data.select_dtypes(include=np.number).columns] = imputer.fit_transform(data.select_dtypes(include=np.number))

# Encode categorical variables
label_encoders = {}
for column in data.select_dtypes(include=['object']).columns:
    label_encoders[column] = LabelEncoder()
    data[column] = label_encoders[column].fit_transform(data[column])

# Standardize numerical features
scaler = StandardScaler()
numerical_features = data.select_dtypes(include=np.number).columns
data[numerical_features] = scaler.fit_transform(data[numerical_features])

# Convert game_date to datetime
data['game_date'] = pd.to_datetime(data['game_date'])
data.sort_values(by='game_date', inplace=True)

# Initialize columns for historical metrics
data['at_bats'] = np.nan
data['batting_avg_against'] = np.nan
data['avg_home_score'] = np.nan
data['avg_away_score'] = np.nan

# Calculate historical performance metrics for each pitcher-batter pair
for i, row in data.iterrows():
    past_data = data[(data['game_date'] < row['game_date']) & (data['pitcher'] == row['pitcher']) & (data['batter'] == row['batter'])]
    if not past_data.empty:
        data.at[i, 'at_bats'] = len(past_data)
        data.at[i, 'batting_avg_against'] = past_data['events'].mean()  # Ensure 'events' is numeric or change this calculation
        data.at[i, 'avg_home_score'] = past_data['post_home_score'].mean()
        data.at[i, 'avg_away_score'] = past_data['post_away_score'].mean()
    else:
        data.at[i, 'at_bats'] = 0
        data.at[i, 'batting_avg_against'] = 0.0
        data.at[i, 'avg_home_score'] = data['post_home_score'].mean()
        data.at[i, 'avg_away_score'] = data['post_away_score'].mean()

# Drop rows with NaN historical metrics (first occurrences)
initial_data_size = len(data)
data.dropna(subset=['at_bats', 'batting_avg_against', 'avg_home_score', 'avg_away_score'], inplace=True)
remaining_data_size = len(data)
print(f"Initial data size: {initial_data_size}, Remaining data size: {remaining_data_size}")

# Check if the dataset is empty after dropping rows
if data.empty:
    raise ValueError("No data left after dropping rows with NaN historical metrics.")

# Define the target variable and feature set
data['game_outcome'] = (data['post_home_score'] > data['post_away_score']).astype(int)
X = data.drop(columns=['game_outcome', 'game_date', 'post_home_score', 'post_away_score', 'events'])
y = data['game_outcome']

# Train-test split without shuffling for time series data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# Use SMote on the training data only to avoid data leakage
smote = SMOTE()
X_resampled, y_resampled = smote.fit_resample(X_train, y_train)

# Use TimeSeriesSplit for time series data
tscv = TimeSeriesSplit(n_splits=5)

# Start the clock time and CPU time
start_time = time.time()
start_cpu_time = time.process_time()

# Train a Random Forest Classifier
clf = RandomForestClassifier()
param_grid = {
    'n_estimators': [100, 200],
    'max_depth': [None, 10, 20],
    'min_samples_split': [2, 5],
    'min_samples_leaf': [1, 2]
}

grid_search = GridSearchCV(clf, param_grid, cv=tscv, scoring='accuracy', n_jobs=-1)
grid_search.fit(X_resampled, y_resampled)

# End the clock time and CPU time
end_time = time.time()
end_cpu_time = time.process_time()

# Calculate the elapsed times
elapsed_time = end_time - start_time
elapsed_cpu_time = end_cpu_time - start_cpu_time

# Evaluate the model on the separate test set
y_pred = grid_search.best_estimator_.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Classification Report:\n", classification_report(y_test, y_pred))

# Display the elapsed times
print(f"Clock time elapsed: {elapsed_time:.2f} seconds")
print(f"CPU time elapsed: {elapsed_cpu_time:.2f} seconds")

# Save the model
joblib.dump(grid_search.best_estimator_, 'baseball_game_outcome_predictor.pkl')

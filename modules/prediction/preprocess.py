import pandas as pd
import sqlite3
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
from flask import Flask, request, jsonify
import numpy as np

# Connect to the SQLite database
conn = sqlite3.connect('baseball_data.db')

# Load data into a pandas DataFrame
data = pd.read_sql_query("SELECT * FROM statcast_data", conn)

# Close the connection
conn.close()

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

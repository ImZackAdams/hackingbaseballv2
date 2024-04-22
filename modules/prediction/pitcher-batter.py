from sqlalchemy import create_engine
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder

# Set display options to show more rows and columns
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 50)

# Assuming the data is stored in a SQLite database (adjust if different)
engine = create_engine('sqlite:///baseball_data.db')
# df = pd.read_sql("SELECT * FROM statcast_data", engine)  # Replace your_table_name with the actual table name


query = "SELECT * FROM statcast_data LIMIT 1000000"
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
matchup_stats['on_base_percentage'] = (matchup_stats['is_hit'] + matchup_stats['is_walk']) / matchup_stats['at_bats']

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
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print("Model Accuracy:", accuracy_score(y_test, y_pred))

df['is_home'] = (df['home_team'] == 'YourTeamName').astype(
    int)  # Replace 'YourTeamName' with the actual team name or logic to handle all teams

X = df[['batting_average', 'on_base_percentage', 'is_home']].fillna(0)

from sklearn.model_selection import GridSearchCV

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

from sklearn.metrics import classification_report, roc_auc_score

print(classification_report(y_test, y_pred))
print("ROC-AUC Score:", roc_auc_score(y_test, y_pred))


# TODO CLEANUP BELOW


# In[ ]:


# df_sorted = df.sort_values(by=['game_date', 'game_pk', 'at_bat_number', 'pitch_number'])


# # find last play
# last_play_per_game = df_sorted.drop_duplicates(subset=['game_pk'], keep='last').copy()

# # Now apply changes to 'last_play_per_game', which is a copy to avoid SettingWithCopyWarning
# last_play_per_game['winning_team'] = last_play_per_game.apply(lambda row: row['home_team'] if row['post_home_score'] > row['post_away_score'] else row['away_team'], axis=1)
# last_play_per_game['losing_team'] = last_play_per_game.apply(lambda row: row['away_team'] if row['post_home_score'] > row['post_away_score'] else row['home_team'], axis=1)

# # Selecting the required columns along with game_date
# winners_losers = last_play_per_game[['game_pk', 'game_date', 'winning_team', 'losing_team', 'post_home_score', 'post_away_score', 'home_team', 'away_team']]

# # Reset the index of the DataFrame and drop the old index
# winners_losers_reset_index = winners_losers.reset_index(drop=True)


# In[ ]:


# print(winners_losers_reset_index)


# In[ ]:


# hit_types = ['single', 'double', 'triple', 'home_run']
# at_bat_events = hit_types + ['field_out', 'strikeout', 'fielders_choice', 'grounded_into_double_play', 'force_out']
# df['is_hit'] = df['events'].isin(hit_types)
# df['is_at_bat'] = df['events'].isin(at_bat_events)
# df['is_strikeout'] = df['events'] == 'strikeout'
# df['is_walk'] = df['events'] == 'walk'


# In[ ]:


# stats = df.groupby(["game_pk", 'pitcher', 'batter']).agg({
#     'is_at_bat': 'sum',
#     'is_hit': 'sum',
#     'is_strikeout': 'sum',
#     'is_walk': 'sum',
# }).rename(columns={'is_at_bat': 'at_bats', 'is_hit': 'total_hits', 'is_strikeout': 'strikeouts', 'is_walk': 'walks'})


# In[ ]:


# stats['batting_average'] = stats['total_hits'] / stats['at_bats']
# stats['on_base_percentage'] = (stats['total_hits'] + stats['walks']) / (stats['at_bats'] + stats['walks'])


# In[ ]:


# stats.reset_index(inplace=True)


# In[ ]:


# print(stats)


# In[ ]:


# data = pd.merge(stats, winners_losers_reset_index, on='game_pk')


# In[ ]:


# print(data)


# In[ ]:


# label_encoder = LabelEncoder()
# data['winning_team_encoded'] = label_encoder.fit_transform(data['winning_team'])


# In[ ]:


# Drop the columns not needed for training
# X = data.drop(['game_pk', 'game_date', 'winning_team', 'losing_team', 'post_home_score', 'post_away_score', 
#                'home_team', 'away_team', 'winning_team_encoded'], axis=1)
# y = data['home_team']


# In[ ]:


# Split the data into training and test sets
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


# In[ ]:


# Initialize the RandomForestClassifier
# model = RandomForestClassifier(random_state=42)


# In[ ]:


# Train the model
# model.fit(X_train, y_train)


# In[ ]:


# Predict on the test set
# y_pred = model.predict(X_test)


# In[ ]:


# accuracy = accuracy_score(y_test, y_pred)
# print(f'Model accuracy: {accuracy}')


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# CODE SHELVED BELOW


# In[ ]:


# hit_types = ['single', 'double', 'triple', 'home_run']
# at_bat_events = hit_types + ['field_out', 'strikeout', 'fielders_choice', 'grounded_into_double_play', 'force_out', 'strikeout']
# walk_events = ['walk']


# In[ ]:


# # Create a new column in the DataFrame to flag hits and at_bats
# df['is_hit'] = df['events'].isin(hit_types)
# df['is_at_bat'] = df['events'].isin(at_bat_events)
# df['is_strikeout'] = df['events'] == 'strikeout'
# df['is_walk'] = df['events'] == 'walk'


# In[ ]:


# # Group by pitcher and batter pairs
# stats = df.groupby(['pitcher', 'batter']).agg({
#     'is_at_bat': 'sum',         # Total number of at-bats
#     'is_hit': 'sum',            # Total number of hits
#     'is_strikeout': 'sum',      # Total number of strikeouts
#     'is_walk': 'sum',           # Total number of walks
# }).rename(columns={'is_at_bat': 'at_bats', 'is_hit': 'total_hits', 'is_strikeout': 'strikeouts', 'is_walk': 'walks'})


# In[ ]:


# # Calculate batting average (AVG) and on-base percentage (OBP)
# stats['batting_average'] = stats['total_hits'] / stats['at_bats']
# stats['on_base_percentage'] = (stats['total_hits'] + stats['walks']) / (stats['at_bats'] + stats['walks'])


# In[ ]:


# # Reset index to make 'pitcher' and 'batter' columns again if necessary
# stats.reset_index(inplace=True)


# In[ ]:


# # Display the statistics DataFrame
# print(stats)


# In[ ]:


# print(winners_losers_reset_index)


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:

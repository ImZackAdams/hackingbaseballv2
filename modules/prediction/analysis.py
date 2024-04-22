#!/usr/bin/env python
# coding: utf-8

# In[1]:


conda install pandas sqlalchemy


# In[2]:


from sqlalchemy import create_engine
import pandas as pd
import numpy as np



# In[3]:


# Set display options to show more rows and columns
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 50)


# In[4]:


# Create a SQLite engine to connect to the baseball data database
engine = create_engine('sqlite:///baseball_data.db')


# In[5]:


query = "SELECT * FROM statcast_data LIMIT 1000"
df = pd.read_sql(query, engine)


# In[6]:


df.columns


# In[7]:


df_sorted = df.sort_values(by=['game_date', 'game_pk', 'at_bat_number', 'pitch_number'])

# Drop duplicates, keeping the last entry (which should be the last play of each game)
# Use copy() to explicitly create a copy of the slice
last_play_per_game = df_sorted.drop_duplicates(subset=['game_pk'], keep='last').copy()

# Now apply changes to 'last_play_per_game', which is a copy to avoid SettingWithCopyWarning
last_play_per_game['winning_team'] = last_play_per_game.apply(lambda row: row['home_team'] if row['post_home_score'] > row['post_away_score'] else row['away_team'], axis=1)
last_play_per_game['losing_team'] = last_play_per_game.apply(lambda row: row['away_team'] if row['post_home_score'] > row['post_away_score'] else row['home_team'], axis=1)

# Selecting the required columns along with game_date
winners_losers = last_play_per_game[['game_pk', 'game_date', 'winning_team', 'losing_team', 'post_home_score', 'post_away_score']]

# Reset the index of the DataFrame and drop the old index
winners_losers_reset_index = winners_losers.reset_index(drop=True)
print(winners_losers_reset_index)


# In[8]:


hit_types = ['single', 'double', 'triple', 'home_run']
at_bat_events = hit_types + ['field_out', 'strikeout', 'fielders_choice', 'grounded_into_double_play', 'force_out', 'strikeout']
walk_events = ['walk']


# In[9]:


# Create a new column in the DataFrame to flag hits and at_bats
df['is_hit'] = df['events'].isin(hit_types)
df['is_at_bat'] = df['events'].isin(at_bat_events)
df['is_strikeout'] = df['events'] == 'strikeout'
df['is_walk'] = df['events'] == 'walk'


# In[10]:


# Group by pitcher and batter pairs
stats = df.groupby(['pitcher', 'batter']).agg({
    'is_at_bat': 'sum',         # Total number of at-bats
    'is_hit': 'sum',            # Total number of hits
    'is_strikeout': 'sum',      # Total number of strikeouts
    'is_walk': 'sum',           # Total number of walks
}).rename(columns={'is_at_bat': 'at_bats', 'is_hit': 'total_hits', 'is_strikeout': 'strikeouts', 'is_walk': 'walks'})


# In[11]:


# Calculate batting average (AVG) and on-base percentage (OBP)
stats['batting_average'] = stats['total_hits'] / stats['at_bats']
stats['on_base_percentage'] = (stats['total_hits'] + stats['walks']) / (stats['at_bats'] + stats['walks'])


# In[12]:


# Reset index to make 'pitcher' and 'batter' columns again if necessary
stats.reset_index(inplace=True)


# In[13]:


# Display the statistics DataFrame
print(stats)


# In[14]:


print(winners_losers_reset_index)

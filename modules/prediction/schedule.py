#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from pybaseball import schedule_and_record


# In[ ]:





# In[2]:


# List of MLB team abbreviations
team_abbreviations = [
    'ARI', 'ATL', 'BAL', 'BOS', 'CHC', 
    'CIN', 'CLE', 'COL', 'CHW', 'DET', 
    'HOU', 'KC', 'LAA', 'LAD', 'MIA', 
    'MIL', 'MIN', 'NYM', 'NYY', 'OAK', 
    'PHI', 'PIT', 'SD', 'SEA', 'SF', 
    'STL', 'TB', 'TEX', 'TOR', 'WSN'
]

all_games = pd.DataFrame()

for team in team_abbreviations:
    try:
        team_schedule = schedule_and_record(2024, team)
        all_games = pd.concat([all_games, team_schedule], ignore_index=True)
    except Exception as e:
        print(f"Failed to retrieve schedule for {team}: {e}")


all_games = all_games.dropna(subset=['Date', 'Tm', 'Opp'])


all_games['unique_id'] = all_games.apply(lambda row: row['Date'] + ''.join(sorted([row['Tm'], row['Opp']])), axis=1)


unique_games = all_games.drop_duplicates(subset=['unique_id'])


unique_games = unique_games.drop(columns=['unique_id'])



# In[3]:


pd.set_option('display.max_rows', None)


# In[4]:


# print(unique_games)


# In[5]:


unique_games.shape


# In[6]:


unique_games['Date'] = pd.to_datetime(unique_games['Date'], errors='coerce', format='%A, %b %d')


unique_games_sorted = unique_games.sort_values(by='Date', ascending=True)


unique_games_sorted = unique_games_sorted.reset_index(drop=True)



# In[7]:


unique_games['Date'] = unique_games['Date'].apply(lambda d: d.replace(year=2024))


unique_games_sorted = unique_games.sort_values(by='Date', ascending=True)

unique_games_sorted = unique_games_sorted.reset_index(drop=True)

print(unique_games_sorted)


# In[8]:





# In[ ]:





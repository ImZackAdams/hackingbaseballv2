# Step 1: Import necessary modules
from pybaseball import batting_stats, pitching_stats, fielding_stats

# Step 2: Define the year for which you want to collect data
year = 2022

# Step 3: Fetch batting stats
batting_data = batting_stats(year)

# Step 4: Fetch pitching stats
pitching_data = pitching_stats(year)

# Step 5: Fetch fielding stats
fielding_data = fielding_stats(year)

# Optional: Save these data frames to CSV files for further analysis or use
batting_data.to_csv(f"batting_stats_{year}.csv", index=False)
pitching_data.to_csv(f"pitching_stats_{year}.csv", index=False)
fielding_data.to_csv(f"fielding_stats_{year}.csv", index=False)

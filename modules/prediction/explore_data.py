import sqlite3
import pandas as pd

# Database file path
db_path = 'cleaned_baseball_data.db'

# Connect to the database
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print(f"✅ Connected to database: {db_path}\n")
except Exception as e:
    print(f"❌ Failed to connect to database: {e}")
    exit()

# 1️⃣ List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
if not tables:
    print("⚠️ No tables found in the database.")
    conn.close()
    exit()

print("📋 Tables in the database:")
for table in tables:
    print(f" - {table[0]}")

# 2️⃣ Show schema for each table
for table in tables:
    table_name = table[0]
    print(f"\n🔍 Schema for table '{table_name}':")
    cursor.execute(f"PRAGMA table_info({table_name});")
    schema = cursor.fetchall()
    for col in schema:
        print(f" - Column: {col[1]}, Type: {col[2]}")

# 3️⃣ Preview first 5 rows of each table
print("\n🛠️ Sample Data:")
for table in tables:
    table_name = table[0]
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 5;", conn)
        print(f"\n📊 Sample from '{table_name}':\n", df)
    except Exception as e:
        print(f"❌ Failed to read sample from '{table_name}': {e}")

# 4️⃣ Analyze key baseball data table
target_table = 'cleaned_statcast_data'
print(f"\n🔍 Analyzing table: '{target_table}'")

# Check if target_table exists
if target_table not in [table[0] for table in tables]:
    print(f"⚠️ Table '{target_table}' not found in the database.")
    conn.close()
    exit()

# Load the entire table into a DataFrame
try:
    df = pd.read_sql_query(f"SELECT * FROM {target_table};", conn)
except Exception as e:
    print(f"❌ Failed to load data from '{target_table}': {e}")
    conn.close()
    exit()

# 5️⃣ Check missing values
missing = df.isnull().sum()
missing_values = missing[missing > 0]
if not missing_values.empty:
    print("\n🔍 Missing Values:")
    print(missing_values)
else:
    print("\n✅ No missing values detected.")

# 6️⃣ Basic statistics
print("\n📈 Basic Statistics (first 10 numeric columns):")
print(df.describe(include='all').T.head(10))

# 7️⃣ Distinct games and teams
game_count = df['game_pk'].nunique() if 'game_pk' in df.columns else "N/A"
home_teams = df['home_team'].nunique() if 'home_team' in df.columns else "N/A"
away_teams = df['away_team'].nunique() if 'away_team' in df.columns else "N/A"

print(f"\n🏟️ Correct unique games count (using game_pk): {game_count}")
print(f"🏆 Unique teams as home: {home_teams}")
print(f"🚀 Unique teams as away: {away_teams}")

# 8️⃣ Check correct win outcomes using the final pitch per game
if 'game_pk' in df.columns and 'pitch_number' in df.columns:
    final_pitches = df.loc[df.groupby('game_pk')['pitch_number'].idxmax()]
    final_pitches['home_win'] = (final_pitches['post_home_score'] > final_pitches['post_away_score']).astype(int)
    print("\n⚾ Home Wins Distribution (Game-Level Calculation):")
    print(final_pitches['home_win'].value_counts(normalize=True))
else:
    print("\n⚠️ Game-level final pitch data not available. Cannot calculate accurate home win distribution.")

# 9️⃣ Investigate potential data issues
print("\n🔍 Investigating potential data issues...")

# Count missing or duplicated game_pks
missing_game_pk = df['game_pk'].isnull().sum() if 'game_pk' in df.columns else "N/A"
duplicate_game_pk = df['game_pk'].duplicated().sum() if 'game_pk' in df.columns else "N/A"
print(f"🔍 Missing game_pk count: {missing_game_pk}")
print(f"🔍 Duplicate game_pk count: {duplicate_game_pk}")

# Identify games with suspiciously low pitch counts
if 'pitch_number' in df.columns:
    pitch_counts = df.groupby('game_pk')['pitch_number'].max()
    print(f"📊 Median max pitch count per game: {pitch_counts.median()}")
    print(pitch_counts.describe())
    short_games = pitch_counts[pitch_counts < 30]
    print(f"⚠️ Potential incomplete games: {len(short_games)}")
    print(short_games.head(10))

# 1️⃣0️⃣ Check daily game distribution
if 'game_date' in df.columns and 'game_pk' in df.columns:
    date_game_counts = df.groupby('game_date')['game_pk'].nunique()
    print("\n📆 Games per date distribution:")
    print(date_game_counts.describe())
    print(date_game_counts.head(10))

# Close the connection
conn.close()
print("\n✅ Data exploration complete!")

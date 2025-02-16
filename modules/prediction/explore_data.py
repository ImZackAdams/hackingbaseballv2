import sqlite3
import pandas as pd

# Database file path
db_path = 'baseball_data.db'

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1️⃣ List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
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
    df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 5;", conn)
    print(f"\n📊 Sample from '{table_name}':\n", df)

# 4️⃣ Check missing values for key table (assume statcast_data)
target_table = 'statcast_data'
print(f"\n🔍 Checking missing values for '{target_table}':")
df = pd.read_sql_query(f"SELECT * FROM {target_table} LIMIT 10000;", conn)
missing = df.isnull().sum()
print(missing[missing > 0])

# 5️⃣ Basic stats
print("\n📈 Basic Statistics (first 10 numeric columns):")
print(df.describe(include='all').T.head(10))

# 6️⃣ Check distinct games and teams
print("\n🏟️ Unique games count:", df['game_date'].nunique() if 'game_date' in df.columns else "N/A")
print("🏆 Unique teams as home:", df['home_team'].nunique() if 'home_team' in df.columns else "N/A")
print("🚀 Unique teams as away:", df['away_team'].nunique() if 'away_team' in df.columns else "N/A")

# 7️⃣ Check win outcomes distribution
if 'post_home_score' in df.columns and 'post_away_score' in df.columns:
    df['home_win'] = (df['post_home_score'] > df['post_away_score']).astype(int)
    print("\n⚾ Home Wins Distribution:")
    print(df['home_win'].value_counts(normalize=True))

# Close connection
conn.close()
print("\n✅ Data exploration complete!")

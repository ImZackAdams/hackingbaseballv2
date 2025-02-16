import sqlite3
import pandas as pd

# Connect to the original database
source_conn = sqlite3.connect('baseball_data.db')
df = pd.read_sql("SELECT * FROM statcast_data", source_conn)
source_conn.close()

# Drop deprecated columns
deprecated_cols = [col for col in df.columns if 'deprecated' in col]
df.drop(columns=deprecated_cols, errors='ignore', inplace=True)

# Fill missing numerical values with median
num_cols = df.select_dtypes(include='number').columns
df[num_cols] = df[num_cols].fillna(df[num_cols].median())

# Fill missing categorical values with 'Unknown'
cat_cols = df.select_dtypes(include='object').columns
df[cat_cols] = df[cat_cols].fillna('Unknown')

# Save the cleaned dataset to a new SQLite database
dest_conn = sqlite3.connect('cleaned_baseball_data.db')
df.to_sql('cleaned_statcast_data', dest_conn, if_exists='replace', index=False)
dest_conn.close()

print("✅ Data cleaning and saving to SQLite complete!")

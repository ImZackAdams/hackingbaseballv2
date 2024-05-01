from pybaseball import statcast
import pandas as pd
import sqlite3
from datetime import timedelta, date
import time


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)


def fetch_data_for_date(single_date, retries=5, wait_time=10):
    for attempt in range(retries):
        try:
            day_data = statcast(start_dt=single_date.strftime("%Y-%m-%d"), end_dt=single_date.strftime("%Y-%m-%d"))
            return day_data
        except Exception as e:
            print(f"Error fetching data for {single_date}: {e}")
            if attempt < retries - 1:
                print(f"Retrying... (Attempt {attempt + 2}/{retries})")
                time.sleep(wait_time)
            else:
                print("Max retries reached. Skipping this date.")
    return None


start_date = date(2020, 4, 1)
end_date = date(2020, 10, 5)

all_data = pd.DataFrame()

for single_date in daterange(start_date, end_date):
    print(f"Fetching data for {single_date.strftime('%Y-%m-%d')}")
    day_data = fetch_data_for_date(single_date)
    if day_data is not None and not day_data.empty:
        all_data = pd.concat([all_data, day_data], ignore_index=True)

conn = sqlite3.connect('baseball_data.db')
all_data.to_sql('statcast_data', conn, if_exists='append', index=False)
conn.close()

print("Data fetching and storage complete.")

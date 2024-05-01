from pybaseball import schedule_and_record
import pandas as pd


def fetch_season_data(years, team):
    # Collects data for the specified years and team
    frames = []
    for year in years:
        try:
            frames.append(schedule_and_record(year, team))
        except Exception as e:
            print(f"Failed to fetch data for {year}: {e}")
    return pd.concat(frames, ignore_index=True)


if __name__ == "__main__":
    years = [2020, 2021, 2022, 2023]  # Example years
    team = 'BOS'  # Example team abbreviation

    # Fetch the data
    season_data = fetch_season_data(years, team)

    # Save the data to a CSV file
    season_data.to_csv('season_data.csv', index=False)

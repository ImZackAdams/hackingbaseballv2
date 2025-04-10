import os
import time
import pandas as pd
import logging
from datetime import datetime
import statsapi

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger()

def fetch_todays_games():
    """Fetch today's MLB games using statsapi"""
    today = datetime.now().strftime('%m/%d/%Y')
    logger.info(f"Fetching MLB games for today: {today}")
    
    try:
        games_data = statsapi.schedule(start_date=today, end_date=today)
        if not games_data:
            logger.info("No games scheduled for today.")
            return pd.DataFrame()

        games_list = []
        for game in games_data:
            home = game['home_name']
            away = game['away_name']
            game_time = game['game_datetime']
            game_id = game['game_id']
            games_list.append({
                'id': game_id,
                'Date': game_time,
                'Home Team': home,
                'Away Team': away
            })

        return pd.DataFrame(games_list)

    except Exception as e:
        logger.error(f"Failed to fetch today's games: {e}")
        return pd.DataFrame()

def display_games(df):
    """Print game matchups"""
    if df.empty:
        print("🛑 No games found today.")
        return

    print(f"\n📅 MLB Games for Today ({datetime.now().date()}):\n" + "=" * 40)
    for _, row in df.iterrows():
        time_str = pd.to_datetime(row['Date']).strftime('%I:%M %p ET')
        print(f"{row['Away Team']} @ {row['Home Team']} – {time_str}")

if __name__ == "__main__":
    games_df = fetch_todays_games()
    display_games(games_df)

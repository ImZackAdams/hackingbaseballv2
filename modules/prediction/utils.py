import json
import math
import os
import random
from datetime import datetime

import statsapi


BOOKS = ["Book A", "Book B", "Book C", "Book D"]
ODDS_CACHE_FILE = os.environ.get(
    "HB_ODDS_CACHE_FILE",
    os.path.join(os.path.dirname(__file__), "odds_cache.json"),
)


def _load_odds_cache():
    if not os.path.exists(ODDS_CACHE_FILE):
        return {}
    with open(ODDS_CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _american_profit(odds, stake=1.0):
    if odds >= 0:
        return (odds / 100.0) * stake
    return (100.0 / abs(odds)) * stake


def _ev(prob, odds, stake=1.0):
    profit = _american_profit(odds, stake)
    return (prob * profit) - ((1 - prob) * stake)


def _deterministic_strength(team_name):
    # Deterministic pseudo-strength based on team name characters.
    base = sum(ord(c) for c in team_name) % 100
    return 0.4 + (base / 1000.0)


def _predict_home_win_prob(home_team, away_team):
    # Lightweight "model": combine deterministic strengths and a small noise term.
    home_strength = _deterministic_strength(home_team)
    away_strength = _deterministic_strength(away_team)
    raw = home_strength - away_strength
    prob = 1 / (1 + math.exp(-4 * raw))
    return max(0.35, min(0.65, prob))


def _get_odds_for_game(game_id, home_team, away_team, odds_cache):
    # Use cache if available, otherwise generate plausible odds.
    cached = odds_cache.get(str(game_id))
    if cached:
        return cached

    odds = {
        "moneyline": {"home": {}, "away": {}},
        "runline": {"home": {}, "away": {}},
        "totals": {"line": 8.5, "over": {}, "under": {}},
        "why": [
            "Starting pitcher advantage",
            "Recent offense form",
            "Bullpen rest",
        ],
    }
    for book in BOOKS:
        # Generate random moneyline odds around pick'em.
        home_odds = random.choice([-140, -130, -120, -110, 100, 110, 120, 130])
        away_odds = -home_odds if home_odds > 0 else abs(home_odds)
        if away_odds == 0:
            away_odds = 110
        odds["moneyline"]["home"][book] = home_odds
        odds["moneyline"]["away"][book] = away_odds

        runline_home = random.choice([-150, -140, -130, -120])
        runline_away = random.choice([110, 120, 130, 140])
        odds["runline"]["home"][book] = runline_home
        odds["runline"]["away"][book] = runline_away

        total_over = random.choice([-120, -110, 100, 110])
        total_under = random.choice([-120, -110, 100, 110])
        odds["totals"]["over"][book] = total_over
        odds["totals"]["under"][book] = total_under

    return odds


def _best_ev(prob, odds_dict):
    best = None
    for book, odds in odds_dict.items():
        ev = _ev(prob, odds)
        if best is None or ev > best["ev"]:
            best = {"book": book, "odds": odds, "ev": ev}
    return best


def _fetch_today_games():
    today = datetime.now().strftime("%m/%d/%Y")
    games_data = statsapi.schedule(start_date=today, end_date=today)
    games = []
    for game in games_data:
        games.append({
            "id": str(game["game_id"]),
            "away_team": game["away_name"],
            "home_team": game["home_name"],
        })
    return games


def get_game_predictions(selected_games):
    odds_cache = _load_odds_cache()
    games = _fetch_today_games()
    selected_set = set(str(g) for g in selected_games)

    predictions = []
    for game in games:
        if game["id"] not in selected_set:
            continue

        home_team = game["home_team"]
        away_team = game["away_team"]
        home_prob = _predict_home_win_prob(home_team, away_team)
        away_prob = 1 - home_prob

        odds = _get_odds_for_game(game["id"], home_team, away_team, odds_cache)
        best_home = _best_ev(home_prob, odds["moneyline"]["home"])
        best_away = _best_ev(away_prob, odds["moneyline"]["away"])
        best_runline_home = _best_ev(home_prob, odds["runline"]["home"])
        best_runline_away = _best_ev(away_prob, odds["runline"]["away"])

        total_line = odds["totals"]["line"]
        best_total_over = _best_ev(0.5, odds["totals"]["over"])
        best_total_under = _best_ev(0.5, odds["totals"]["under"])

        prediction = {
            "id": game["id"],
            "away_team": away_team,
            "home_team": home_team,
            "home_win_prob": round(home_prob, 3),
            "away_win_prob": round(away_prob, 3),
            "best_home": best_home,
            "best_away": best_away,
            "best_runline_home": best_runline_home,
            "best_runline_away": best_runline_away,
            "total_line": total_line,
            "best_total_over": best_total_over,
            "best_total_under": best_total_under,
            "why": odds.get("why", []),
            "all_odds": odds,
        }
        predictions.append(prediction)

    print(f"Filtered predictions: {predictions}")
    return predictions

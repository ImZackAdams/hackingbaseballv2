import os
import tempfile
import unittest
from datetime import datetime
from unittest.mock import Mock, patch

_PANDAS_IMPORT_ERROR = None
try:
    import pandas as pd
except Exception as exc:  # pragma: no cover - environment-dependent
    pd = None
    _PANDAS_IMPORT_ERROR = exc

_LINEUP_IMPORT_ERROR = None
try:
    from modules.game_management import lineup
except Exception as exc:  # pragma: no cover - environment-dependent
    lineup = None
    _LINEUP_IMPORT_ERROR = exc


@unittest.skipIf(
    pd is None or getattr(pd, "__HB_STUB__", False) or lineup is None,
    f"pandas import failed: {_PANDAS_IMPORT_ERROR} | lineup import failed: {_LINEUP_IMPORT_ERROR}",
)
class TestLineup(unittest.TestCase):
    def test_fetch_starting_lineups_empty_dates(self):
        response = Mock()
        response.raise_for_status = Mock()
        response.json.return_value = {"dates": []}

        with patch("modules.game_management.lineup.requests.get", return_value=response):
            df = lineup.fetch_starting_lineups("2025-06-15")

        self.assertIsInstance(df, pd.DataFrame)
        self.assertTrue(df.empty)

    def test_fetch_starting_lineups_parses_players(self):
        schedule_response = Mock()
        schedule_response.raise_for_status = Mock()
        schedule_response.json.return_value = {
            "dates": [
                {
                    "games": [
                        {"gamePk": 123, "officialDate": "2025-06-15"}
                    ]
                }
            ]
        }

        boxscore_response = Mock()
        boxscore_response.raise_for_status = Mock()
        boxscore_response.json.return_value = {
            "teams": {
                "home": {
                    "team": {"name": "New York Yankees"},
                    "pitchers": [111],
                    "players": {
                        "ID111": {
                            "person": {"id": 111, "fullName": "Pitcher Home"},
                            "position": {"abbreviation": "P"},
                        },
                        "ID112": {
                            "person": {"id": 112, "fullName": "Batter Home"},
                            "position": {"abbreviation": "1B"},
                            "battingOrder": "100",
                        },
                    },
                },
                "away": {
                    "team": {"name": "Boston Red Sox"},
                    "pitchers": [211],
                    "players": {
                        "ID211": {
                            "person": {"id": 211, "fullName": "Pitcher Away"},
                            "position": {"abbreviation": "P"},
                        },
                        "ID212": {
                            "person": {"id": 212, "fullName": "Batter Away"},
                            "position": {"abbreviation": "2B"},
                            "battingOrder": "100",
                        },
                    },
                },
            }
        }

        with patch("modules.game_management.lineup.requests.get") as mocked_get:
            mocked_get.side_effect = [schedule_response, boxscore_response]
            df = lineup.fetch_starting_lineups("2025-06-15")

        self.assertEqual(len(df), 4)
        self.assertIn("team_abbr", df.columns)
        self.assertIn("player_id", df.columns)
        self.assertIn("batting_order", df.columns)
        self.assertIn("position", df.columns)
        self.assertIn("NYY", set(df["team_abbr"]))
        self.assertIn("BOS", set(df["team_abbr"]))

    def test_get_or_update_schedules_uses_cache(self):
        with tempfile.TemporaryDirectory() as tempdir:
            cache_path = os.path.join(tempdir, "game_schedules.json")
            sample = pd.DataFrame(
                {
                    "Date": [datetime(2025, 6, 15)],
                    "Tm": ["NYY"],
                    "Opp": ["BOS"],
                    "Attendance": ["Unknown"],
                }
            )
            sample.to_json(cache_path, date_format="iso")

            original_cache_file = lineup.CACHE_FILE
            lineup.CACHE_FILE = cache_path
            try:
                with patch(
                    "modules.game_management.lineup.fetch_and_process_schedules"
                ) as mocked_fetch:
                    mocked_fetch.side_effect = AssertionError("Cache should be used")
                    schedules = lineup.get_or_update_schedules(2025)
            finally:
                lineup.CACHE_FILE = original_cache_file

        self.assertIn("id", schedules.columns)
        self.assertTrue(pd.isna(schedules.loc[0, "Attendance"]))


if __name__ == "__main__":
    unittest.main()

import pytest

import app as flask_app


@pytest.fixture()
def client():
    flask_app.app.config["TESTING"] = True
    flask_app.app.secret_key = "test_secret"
    with flask_app.app.test_client() as client:
        yield client


def test_index_renders_games(client, monkeypatch):
    sample_games = [
        {
            "game_id": 123,
            "away_name": "Boston Red Sox",
            "home_name": "New York Yankees",
        }
    ]

    def fake_schedule(*args, **kwargs):
        return sample_games

    monkeypatch.setattr("modules.game_management.routes.statsapi.schedule", fake_schedule)

    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "Today's Games" in body
    assert "Boston Red Sox" in body
    assert "New York Yankees" in body


def test_results_renders_predictions(client, monkeypatch):
    sample_predictions = [
        {
            "id": "123",
            "away_team": "BOS",
            "home_team": "NYY",
            "home_win_prob": 0.58,
            "away_win_prob": 0.42,
            "best_home": {"book": "Book A", "odds": -120, "ev": 0.05},
            "best_away": {"book": "Book B", "odds": 130, "ev": 0.03},
            "best_runline_home": {"book": "Book A", "odds": -140, "ev": 0.02},
            "best_runline_away": {"book": "Book B", "odds": 120, "ev": 0.01},
            "total_line": 8.5,
            "best_total_over": {"book": "Book C", "odds": -110, "ev": 0.01},
            "best_total_under": {"book": "Book D", "odds": -110, "ev": 0.01},
            "why": ["Starting pitcher advantage"],
        }
    ]

    monkeypatch.setattr(
        "modules.result_display.routes.get_game_predictions",
        lambda selected_games: sample_predictions,
    )

    with client.session_transaction() as sess:
        sess["selected_games"] = ["123"]

    resp = client.get("/results")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "Game Results" in body
    assert "BOS at NYY" in body
    assert "EV:" in body
    assert "Book A" in body
    assert "Book B" in body


def test_results_includes_probabilities_and_ev_labels(client, monkeypatch):
    sample_predictions = [
        {
            "id": "999",
            "away_team": "LAD",
            "home_team": "SFG",
            "home_win_prob": 0.62,
            "away_win_prob": 0.38,
            "best_home": {"book": "Book C", "odds": -135, "ev": 0.08},
            "best_away": {"book": "Book D", "odds": 150, "ev": 0.02},
            "best_runline_home": {"book": "Book C", "odds": -140, "ev": 0.02},
            "best_runline_away": {"book": "Book D", "odds": 120, "ev": 0.01},
            "total_line": 8.0,
            "best_total_over": {"book": "Book C", "odds": -110, "ev": 0.01},
            "best_total_under": {"book": "Book D", "odds": -110, "ev": 0.01},
            "why": ["Recent offense form"],
        }
    ]

    monkeypatch.setattr(
        "modules.result_display.routes.get_game_predictions",
        lambda selected_games: sample_predictions,
    )

    with client.session_transaction() as sess:
        sess["selected_games"] = ["999"]

    resp = client.get("/results")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "SFG" in body
    assert "LAD" in body
    assert "62.0%" in body or "62%" in body
    assert "38.0%" in body or "38%" in body
    assert "EV:" in body
    assert "Run Line" in body
    assert "O/U" in body
    assert "Why" in body


def test_checkout_is_one_dollar_report(client, monkeypatch):
    captured = {}

    def fake_create(**kwargs):
        captured.update(kwargs)
        class FakeSession:
            id = "cs_test_456"
        return FakeSession()

    monkeypatch.setattr("stripe.checkout.Session.create", fake_create)

    resp = client.post(
        "/create-checkout-session",
        json={"selectedGames": ["101", "102"]},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["sessionId"] == "cs_test_456"
    line_items = captured.get("line_items")
    assert line_items is not None
    assert len(line_items) == 1
    assert line_items[0]["price_data"]["unit_amount"] == 100


def test_game_detail_page(client, monkeypatch):
    sample_predictions = [
        {
            "id": "777",
            "away_team": "SEA",
            "home_team": "TEX",
            "home_win_prob": 0.55,
            "away_win_prob": 0.45,
            "best_home": {"book": "Book A", "odds": -115, "ev": 0.04},
            "best_away": {"book": "Book B", "odds": 105, "ev": 0.01},
            "best_runline_home": {"book": "Book A", "odds": -140, "ev": 0.03},
            "best_runline_away": {"book": "Book B", "odds": 120, "ev": 0.02},
            "total_line": 8.5,
            "best_total_over": {"book": "Book C", "odds": -110, "ev": 0.01},
            "best_total_under": {"book": "Book D", "odds": -110, "ev": 0.01},
            "why": ["Starting pitcher advantage"],
            "all_odds": {
                "moneyline": {"home": {"Book A": -115}, "away": {"Book A": 105}},
                "runline": {"home": {"Book A": -140}, "away": {"Book A": 120}},
                "totals": {"line": 8.5, "over": {"Book A": -110}, "under": {"Book A": -110}},
            },
        }
    ]

    monkeypatch.setattr(
        "modules.result_display.routes.get_game_predictions",
        lambda selected_games: sample_predictions,
    )

    resp = client.get("/game/777")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "SEA at TEX" in body
    assert "Moneyline Odds" in body
    assert "Run Line" in body
    assert "Totals" in body


def test_create_checkout_session(client, monkeypatch):
    class FakeSession:
        id = "cs_test_123"

    def fake_create(*args, **kwargs):
        return FakeSession()

    monkeypatch.setattr("stripe.checkout.Session.create", fake_create)

    resp = client.post(
        "/create-checkout-session",
        json={"selectedGames": ["123"]},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["sessionId"] == "cs_test_123"

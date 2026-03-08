import json

from betting_odds_scraper.scrapers.betclic.parser import (
    extract_ng_state_from_html,
    extract_rows_from_ng_state,
)


def test_extract_ng_state_from_html():
    ng_state = {"root": {"ok": True}}
    html = f'<html><body><script id="ng-state" type="application/json">{json.dumps(ng_state)}</script></body></html>'

    result = extract_ng_state_from_html(html)

    assert result == ng_state


def test_extract_rows_from_ng_state():
    ng_state = {
        "root": {
            "payload": [
                {
                    "market": {
                        "name": "Resultado (Tempo Regulamentar)",
                        "mainSelections": [
                            {
                                "name": "Barcelona",
                                "odds": 1.21,
                                "status": 1,
                            },
                            {
                                "name": "Empate",
                                "odds": 6.25,
                                "status": 1,
                            },
                            {
                                "name": "Sevilha",
                                "odds": 9.00,
                                "status": 1,
                            },
                        ],
                    },
                    "matchInfo": {
                        "matchId": "1047164918075392",
                        "matchDateUtc": "2026-03-15T15:15:00.0000000Z",
                        "isLive": False,
                        "contestants": [
                            {"name": "Barcelona"},
                            {"name": "Sevilha"},
                        ],
                        "competition": {
                            "id": "7",
                            "name": "Espanha - La Liga",
                        },
                    },
                }
            ]
        }
    }

    rows = extract_rows_from_ng_state(
        ng_state=ng_state,
        site_name="betclic",
        target_name="laliga",
        country_name="espanha",
        league_name="laliga",
        competition_id=7,
        source_url="https://www.betclic.pt/futebol-sfootball/espanha-la-liga-c7",
    )

    assert len(rows) == 1
    row = rows[0]

    assert row.site == "betclic"
    assert row.country == "espanha"
    assert row.league == "laliga"
    assert row.target_name == "laliga"
    assert row.league_id == 7
    assert row.home_team == "Barcelona"
    assert row.away_team == "Sevilha"
    assert row.odd_1 == 1.21
    assert row.odd_x == 6.25
    assert row.odd_2 == 9.0
    assert row.live is False
    assert row.match_date == "2026-03-15"
    assert row.match_time == "15:15"
    assert row.fixture_date == "2026-03-15T15:15:00+00:00"
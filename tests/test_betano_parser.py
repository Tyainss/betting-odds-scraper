from betting_odds_scraper.scrapers.betano.parser import (
    extract_initial_state_from_html,
    extract_rows_from_initial_state,
)


def test_extract_initial_state_from_html():
    html = """
    <html>
      <body>
        <script>
          window["initial_state"] = {"data": {"blocks": []}}
        </script>
      </body>
    </html>
    """

    initial_state = extract_initial_state_from_html(html)
    assert initial_state["data"]["blocks"] == []

def test_extract_rows_from_initial_state():
    initial_state = {
        "data": {
            "blocks": [
                {
                    "events": [
                        {
                            "name": "Villarreal - Elche",
                            "startTime": 1772974800000,
                            "liveNow": False,
                            "participants": [
                                {"name": "Villarreal"},
                                {"name": "Elche"},
                            ],
                            "markets": [
                                {
                                    "type": "MRES",
                                    "selections": [
                                        {"name": "1", "price": 1.44},
                                        {"name": "X", "price": 4.55},
                                        {"name": "2", "price": 6.2},
                                    ],
                                }
                            ],
                        }
                    ]
                }
            ]
        }
    }

    rows = extract_rows_from_initial_state(
        initial_state=initial_state,
        site_name="betano",
        target_name="laliga",
        country_name="espanha",
        league_name="laliga",
        league_id=5,
        source_url="https://www.betano.pt/test",
        source_timezone="UTC",
    )
    assert len(rows) == 1

    row = rows[0]
    assert row.site == "betano"
    assert row.country == "espanha"
    assert row.league == "laliga"
    assert row.target_name == "laliga"
    assert row.league_id == 5
    assert row.source_url == "https://www.betano.pt/test"
    assert row.live is False
    assert row.home_team == "Villarreal"
    assert row.away_team == "Elche"
    assert row.odd_1 == 1.44
    assert row.odd_x == 4.55
    assert row.odd_2 == 6.2
    assert row.fixture_date is not None
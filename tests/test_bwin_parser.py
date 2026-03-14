from betting_odds_scraper.scrapers.bwin.parser import extract_rows_from_bwin_widget_data


def test_extract_rows_from_bwin_widget_data():
    widget_data = {
        "widgets": [
            {
                "payload": {
                    "items": [
                        {
                            "activeChildren": [
                                {
                                    "id": "/mobilesports-v1.0/layout/layout_standards/modules/competition/matches",
                                    "payload": {
                                        "fixtures": [
                                            {
                                                "participants": [
                                                    {
                                                        "name": {"value": "Vitória SC"},
                                                        "properties": {
                                                            "type": "HomeTeam"
                                                        },
                                                    },
                                                    {
                                                        "name": {
                                                            "value": "FC Famalicão"
                                                        },
                                                        "properties": {
                                                            "type": "AwayTeam"
                                                        },
                                                    },
                                                ],
                                                "optionMarkets": [
                                                    {
                                                        "name": {
                                                            "value": "Resultado do Jogo - 2GV"
                                                        },
                                                        "options": [
                                                            {
                                                                "name": {
                                                                    "value": "Vitória SC"
                                                                },
                                                                "price": {"odds": 2.10},
                                                            },
                                                            {
                                                                "name": {"value": "X"},
                                                                "price": {"odds": 3.30},
                                                            },
                                                            {
                                                                "name": {
                                                                    "value": "FC Famalicão"
                                                                },
                                                                "price": {"odds": 3.40},
                                                            },
                                                        ],
                                                    }
                                                ],
                                                "stage": "PreMatch",
                                                "scoreboard": {"started": False},
                                                "startDate": "2026-03-14T15:30:00Z",
                                            }
                                        ]
                                    },
                                }
                            ]
                        }
                    ]
                }
            }
        ]
    }

    rows = extract_rows_from_bwin_widget_data(
        widget_data=widget_data,
        site_name="bwin",
        target_id="primeira_liga",
        sport_id="football",
        country_id="portugal",
        league_id="primeira_liga",
        source_sport="futebol",
        source_country="portugal",
        source_league="liga-portugal",
        source_target_name="primeira_liga",
        source_league_id=102851,
        source_url="https://www.bwin.pt/test",
    )

    assert len(rows) == 1

    row = rows[0]
    assert row.site == "bwin"
    assert row.sport_id == "football"
    assert row.country_id == "portugal"
    assert row.league_id == "primeira_liga"
    assert row.target_id == "primeira_liga"
    assert row.source_url == "https://www.bwin.pt/test"
    assert row.live is False
    assert row.home_team == "Vitória SC"
    assert row.away_team == "FC Famalicão"
    assert row.odd_1 == 2.10
    assert row.odd_x == 3.30
    assert row.odd_2 == 3.40
    assert row.source_sport == "futebol"
    assert row.source_country == "portugal"
    assert row.source_league == "liga-portugal"
    assert row.source_target_name == "primeira_liga"
    assert row.source_league_id == 102851
    assert row.match_date == "2026-03-14"
    assert row.match_time == "15:30"
    assert row.fixture_date == "2026-03-14T15:30:00+00:00"

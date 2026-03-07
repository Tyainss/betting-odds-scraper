from betting_odds_scraper.scrapers.betano.parser import (
    is_valid_match_block,
    parse_match_block,
)


def test_is_valid_match_block_for_prematch():
    text = """07/03
18:00
SC Braga
Sporting CP
1
3.60
X
3.45
2
2.07"""

    assert is_valid_match_block(text) is True


def test_is_valid_match_block_for_live():
    text = """AO VIVO
Moreirense FC
CD Nacional Madeira
1
9.00
X
1.11
2
7.10"""

    assert is_valid_match_block(text) is True


def test_is_valid_match_block_rejects_small_odds_only_block():
    text = """1
3.60
X
3.45
2
2.07"""

    assert is_valid_match_block(text) is False


def test_parse_match_block_for_prematch():
    text = """07/03
18:00
SC Braga
Sporting CP
1
3.60
X
3.45
2
2.07"""

    row = parse_match_block(
        text=text,
        site_name="betano",
        country_name="portugal",
        league_name="primeira_liga",
        source_timezone="UTC",
    )

    assert row["site"] == "betano"
    assert row["country"] == "portugal"
    assert row["league"] == "primeira_liga"
    assert row["live"] is False
    assert row["match_date"].endswith("-03-07")
    assert row["match_time"] == "18:00"
    assert row["home_team"] == "SC Braga"
    assert row["away_team"] == "Sporting CP"
    assert row["odd_1"] == 3.60
    assert row["odd_x"] == 3.45
    assert row["odd_2"] == 2.07
    assert row["fixture_date"].endswith("18:00:00+00:00")


def test_parse_match_block_for_live():
    text = """AO VIVO
Moreirense FC
CD Nacional Madeira
1
9.00
X
1.11
2
7.10"""

    row = parse_match_block(
        text=text,
        site_name="betano",
        country_name="portugal",
        league_name="primeira_liga",
        source_timezone="UTC",
    )

    assert row["live"] is True
    assert row["match_date"] is None
    assert row["match_time"] is None
    assert row["fixture_date"] is None
    assert row["home_team"] == "Moreirense FC"
    assert row["away_team"] == "CD Nacional Madeira"
    assert row["odd_1"] == 9.00
    assert row["odd_x"] == 1.11
    assert row["odd_2"] == 7.10
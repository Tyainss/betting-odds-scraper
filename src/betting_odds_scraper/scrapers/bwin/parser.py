from datetime import datetime, timezone

from betting_odds_scraper.models import OddsRow


MATCHES_WIDGET_ID = "/mobilesports-v1.0/layout/layout_standards/modules/competition/matches"
MATCH_RESULT_MARKET_NAMES = {
    "Resultado do Jogo - 2GV",
    "Resultado 1X2",
    "Resultado do Jogo",
}
DRAW_SELECTION_NAMES = {"X", "Empate", "Draw"}


def _parse_fixture_datetime(start_date):
    if not start_date:
        return None

    normalized = start_date.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized).astimezone(timezone.utc)


def _extract_matches_payload(widget_data):
    widgets = widget_data.get("widgets", [])
    if not widgets:
        raise ValueError("Bwin widget data does not contain widgets")

    root_payload = widgets[0].get("payload", {})
    items = root_payload.get("items", [])
    if not items:
        raise ValueError("Bwin widget data does not contain payload.items")

    container = items[0]
    active_children = container.get("activeChildren", [])
    if not active_children:
        raise ValueError("Bwin widget data does not contain activeChildren")

    for child in active_children:
        if child.get("id") == MATCHES_WIDGET_ID:
            payload = child.get("payload", {})
            fixtures = payload.get("fixtures")
            if not isinstance(fixtures, list):
                raise ValueError("Bwin matches payload does not contain fixtures")
            return payload

    raise ValueError("Could not find Bwin competition matches payload")


def _extract_teams(fixture):
    participants = fixture.get("participants", [])
    home_team = None
    away_team = None

    for participant in participants:
        participant_type = participant.get("properties", {}).get("type")
        participant_name = participant.get("name", {}).get("value")

        if participant_type == "HomeTeam":
            home_team = participant_name
        elif participant_type == "AwayTeam":
            away_team = participant_name

    return home_team, away_team


def _find_match_result_market(option_markets):
    for market in option_markets:
        market_name = market.get("name", {}).get("value")
        if market_name in MATCH_RESULT_MARKET_NAMES:
            return market
    return None


def _extract_match_result_prices(market, home_team, away_team):
    prices = {}

    for option in market.get("options", []):
        option_name = option.get("name", {}).get("value")
        odds = option.get("price", {}).get("odds")

        if option_name is None or odds is None:
            continue

        if option_name == home_team:
            prices["1"] = float(odds)
        elif option_name in DRAW_SELECTION_NAMES:
            prices["X"] = float(odds)
        elif option_name == away_team:
            prices["2"] = float(odds)

    if {"1", "X", "2"}.issubset(prices.keys()):
        return prices

    return None


def extract_rows_from_bwin_widget_data(
    widget_data,
    site_name,
    target_id,
    sport_id,
    country_id,
    league_id,
    source_sport,
    source_country,
    source_league,
    source_target_name,
    source_league_id,
    source_url,
):
    matches_payload = _extract_matches_payload(widget_data)
    rows = []

    for fixture in matches_payload.get("fixtures", []):
        home_team, away_team = _extract_teams(fixture)
        if not home_team or not away_team:
            continue

        market = _find_match_result_market(fixture.get("optionMarkets", []))
        if not market:
            continue

        prices = _extract_match_result_prices(
            market=market,
            home_team=home_team,
            away_team=away_team,
        )
        if not prices:
            continue

        fixture_dt_utc = _parse_fixture_datetime(fixture.get("startDate"))
        fixture_date = None
        match_date = None
        match_time = None

        if fixture_dt_utc is not None:
            fixture_date = fixture_dt_utc.isoformat()
            match_date = fixture_dt_utc.date().isoformat()
            match_time = fixture_dt_utc.time().replace(tzinfo=None).isoformat(timespec="minutes")

        live = fixture.get("stage") != "PreMatch" or bool(
            fixture.get("scoreboard", {}).get("started", False)
        )

        rows.append(
            OddsRow(
                site=site_name,
                sport_id=sport_id,
                country_id=country_id,
                league_id=league_id,
                target_id=target_id,
                source_url=source_url,
                scraped_at=datetime.now(timezone.utc).isoformat(),
                live=live,
                match_date=match_date,
                match_time=match_time,
                fixture_date=fixture_date,
                home_team=home_team,
                away_team=away_team,
                odd_1=prices["1"],
                odd_x=prices["X"],
                odd_2=prices["2"],
                source_sport=source_sport,
                source_country=source_country,
                source_league=source_league,
                source_target_name=source_target_name,
                source_league_id=int(source_league_id),
            )
        )

    return rows
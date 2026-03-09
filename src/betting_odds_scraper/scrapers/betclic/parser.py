import json
import re
from datetime import datetime, timezone

from betting_odds_scraper.models import OddsRow


NG_STATE_PATTERN = re.compile(
    r'<script id="ng-state" type="application/json">(.*?)</script>',
    re.DOTALL,
)


def extract_ng_state_from_html(html):
    match = NG_STATE_PATTERN.search(html)
    if not match:
        raise ValueError('Could not find <script id="ng-state"> in page source')

    return json.loads(match.group(1))


def _iter_dicts(value):
    if isinstance(value, dict):
        yield value
        for nested_value in value.values():
            yield from _iter_dicts(nested_value)
    elif isinstance(value, list):
        for nested_value in value:
            yield from _iter_dicts(nested_value)


def _parse_match_datetime(match_date_utc):
    if not match_date_utc:
        return None

    normalized = match_date_utc.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized).astimezone(timezone.utc)


def _extract_teams(match_info):
    contestants = match_info.get("contestants", [])
    if len(contestants) < 2:
        return None, None

    home_team = contestants[0].get("name")
    away_team = contestants[1].get("name")
    return home_team, away_team


def _extract_match_result_prices(market, home_team, away_team):
    if market.get("name") != "Resultado (Tempo Regulamentar)":
        return None

    selections = market.get("mainSelections", [])
    prices = {}

    for selection in selections:
        if selection.get("status") != 1:
            continue

        selection_name = selection.get("name")
        selection_odds = selection.get("odds")
        if selection_name is None or selection_odds is None:
            continue

        if selection_name == home_team:
            prices["1"] = float(selection_odds)
        elif selection_name in {"Empate", "Draw"}:
            prices["X"] = float(selection_odds)
        elif selection_name == away_team:
            prices["2"] = float(selection_odds)

    if {"1", "X", "2"}.issubset(prices.keys()):
        return prices

    return None


def extract_rows_from_ng_state(
    ng_state,
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
    rows = []
    seen_match_ids = set()

    for item in _iter_dicts(ng_state):
        market = item.get("market")
        match_info = item.get("matchInfo")

        if not isinstance(market, dict) or not isinstance(match_info, dict):
            continue

        competition = match_info.get("competition", {})
        if str(competition.get("id")) != str(source_league_id):
            continue

        match_id = match_info.get("matchId")
        if not match_id or match_id in seen_match_ids:
            continue

        home_team, away_team = _extract_teams(match_info)
        if not home_team or not away_team:
            continue

        prices = _extract_match_result_prices(
            market=market,
            home_team=home_team,
            away_team=away_team,
        )
        if not prices:
            continue

        fixture_dt_utc = _parse_match_datetime(match_info.get("matchDateUtc"))
        fixture_date = None
        match_date = None
        match_time = None

        if fixture_dt_utc is not None:
            fixture_date = fixture_dt_utc.isoformat()
            match_date = fixture_dt_utc.date().isoformat()
            match_time = fixture_dt_utc.time().replace(tzinfo=None).isoformat(timespec="minutes")

        rows.append(
            OddsRow(
                site=site_name,
                sport_id=sport_id,
                country_id=country_id,
                league_id=league_id,
                target_id=target_id,
                source_url=source_url,
                scraped_at=datetime.now(timezone.utc).isoformat(),
                live=bool(match_info.get("isLive", False)),
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
        seen_match_ids.add(match_id)

    return rows
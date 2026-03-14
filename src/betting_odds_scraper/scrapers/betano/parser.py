import json
import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from betting_odds_scraper.models import OddsRow

INITIAL_STATE_PATTERN = re.compile(
    r'window\["initial_state"\]\s*=\s*(\{.*?\})\s*</script>',
    re.DOTALL,
)


def _get_zoneinfo(timezone_name):
    if timezone_name.upper() == "UTC":
        return timezone.utc

    return ZoneInfo(timezone_name)


def _parse_start_time_millis(start_time_millis, source_timezone):
    source_tz = _get_zoneinfo(source_timezone)

    utc_dt = datetime.fromtimestamp(start_time_millis / 1000, tz=timezone.utc)
    local_dt = utc_dt.astimezone(source_tz)
    return local_dt.astimezone(timezone.utc)


def extract_initial_state_from_html(html):
    match = INITIAL_STATE_PATTERN.search(html)
    if not match:
        raise ValueError("Could not find window['initial_state'] in page source")

    return json.loads(match.group(1))


def _extract_match_result_prices(event):
    for market in event.get("markets", []):
        if market.get("type") != "MRES":
            continue

        prices = {}
        for selection in market.get("selections", []):
            selection_name = selection.get("name")
            selection_price = selection.get("price")

            if selection_name in {"1", "X", "2"} and selection_price is not None:
                prices[selection_name] = float(selection_price)

        if {"1", "X", "2"}.issubset(prices.keys()):
            return prices

    return None


def _extract_teams(event):
    participants = event.get("participants", [])
    if len(participants) >= 2:
        return participants[0].get("name"), participants[1].get("name")

    event_name = event.get("name", "")
    if " - " in event_name:
        home_team, away_team = event_name.split(" - ", 1)
        return home_team, away_team

    return None, None


def extract_rows_from_initial_state(
    initial_state,
    site_name,
    target_id,
    sport_id,
    country_id,
    league_id,
    source_sport,
    source_country,
    source_league,
    source_target_name,
    source_timezone,
    source_league_id,
    source_url,
):
    rows = []
    data = initial_state.get("data", {})
    blocks = data.get("blocks", [])

    for block in blocks:
        for event in block.get("events", []):
            prices = _extract_match_result_prices(event)
            if not prices:
                continue

            home_team, away_team = _extract_teams(event)
            if not home_team or not away_team:
                continue

            start_time_millis = event.get("startTime")
            fixture_date = None
            match_date = None
            match_time = None

            if start_time_millis is not None:
                fixture_dt_utc = _parse_start_time_millis(
                    start_time_millis=start_time_millis,
                    source_timezone=source_timezone,
                )
                fixture_date = fixture_dt_utc.isoformat()
                match_date = fixture_dt_utc.date().isoformat()
                match_time = (
                    fixture_dt_utc.time()
                    .replace(tzinfo=None)
                    .isoformat(timespec="minutes")
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
                    live=bool(event.get("liveNow", False)),
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
                    source_league_id=source_league_id,
                )
            )

    return rows

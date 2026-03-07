import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from betting_odds_scraper.models import OddsRow

ODD_PATTERN = re.compile(r"\d{1,2}[.,]\d{2}")
DATE_PATTERN = re.compile(r"\d{2}/\d{2}")
TIME_PATTERN = re.compile(r"\d{2}:\d{2}")


def normalize_text_block(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def is_valid_match_block(text):
    lines = normalize_text_block(text)

    if len(lines) < 8 or len(lines) > 10:
        return False

    has_live = lines[0] == "AO VIVO"
    has_date = bool(DATE_PATTERN.fullmatch(lines[0]))
    has_time = any(TIME_PATTERN.fullmatch(line) for line in lines)
    has_labels = all(label in lines for label in ["1", "X", "2"])

    odds = [line for line in lines if ODD_PATTERN.fullmatch(line)]
    if len(odds) != 3:
        return False

    if has_live:
        return has_labels

    return has_date and has_time and has_labels

def _get_zoneinfo(timezone_name):
    if timezone_name.upper() == "UTC":
        return timezone.utc

    return ZoneInfo(timezone_name)

def _infer_fixture_year(date_str, source_tz):
    now = datetime.now(source_tz)
    candidate = datetime.strptime(
        f"{now.year}-{date_str}",
        "%Y-%d/%m",
    ).date()

    previous_year_candidate = candidate.replace(year=now.year - 1)
    next_year_candidate = candidate.replace(year=now.year + 1)

    candidates = [
        previous_year_candidate,
        candidate,
        next_year_candidate,
    ]

    return min(candidates, key=lambda value: abs((value - now.date()).days)).year


def _parse_fixture_datetime(date_str, time_str, source_timezone):
    source_tz = _get_zoneinfo(source_timezone)

    fixture_year = _infer_fixture_year(date_str, source_tz)
    local_dt = datetime.strptime(
        f"{fixture_year}-{date_str} {time_str}",
        "%Y-%d/%m %H:%M",
    ).replace(tzinfo=source_tz)

    utc_dt = local_dt.astimezone(timezone.utc)

    return utc_dt


def parse_match_block(
    text,
    site_name,
    target_name,
    country_name,
    league_name,
    source_timezone,
    region_id,
    league_id,
    source_url,
):
    lines = normalize_text_block(text)

    if lines[0] == "AO VIVO":
        return OddsRow(
            site=site_name,
            country=country_name,
            league=league_name,
            target_name=target_name,
            region_id=region_id,
            league_id=league_id,
            source_url=source_url,
            scraped_at=datetime.now(timezone.utc).isoformat(),
            live=True,
            match_date=None,
            match_time=None,
            fixture_date=None,
            home_team=lines[1],
            away_team=lines[2],
            odd_1=float(lines[4].replace(",", ".")),
            odd_x=float(lines[6].replace(",", ".")),
            odd_2=float(lines[8].replace(",", ".")),
        )

    fixture_dt_utc = _parse_fixture_datetime(
        date_str=lines[0],
        time_str=lines[1],
        source_timezone=source_timezone,
    )

    return OddsRow(
        site=site_name,
        country=country_name,
        league=league_name,
        target_name=target_name,
        region_id=region_id,
        league_id=league_id,
        source_url=source_url,
        scraped_at=datetime.now(timezone.utc).isoformat(),
        live=False,
        match_date=fixture_dt_utc.date().isoformat(),
        match_time=fixture_dt_utc.time().replace(tzinfo=None).isoformat(timespec="minutes"),
        fixture_date=fixture_dt_utc.isoformat(),
        home_team=lines[2],
        away_team=lines[3],
        odd_1=float(lines[5].replace(",", ".")),
        odd_x=float(lines[7].replace(",", ".")),
        odd_2=float(lines[9].replace(",", ".")),
    )
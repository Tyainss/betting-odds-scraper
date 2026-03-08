from dataclasses import dataclass
from typing import Literal, Optional


OutputFormat = Literal["csv", "json"]


@dataclass(frozen=True)
class BrowserConfig:
    headless: bool
    language: str
    page_load_timeout_seconds: int
    wait_after_load_seconds: int
    wait_after_overlay_dismiss_seconds: int


@dataclass(frozen=True)
class OutputConfig:
    default_format: OutputFormat
    allowed_formats: tuple[OutputFormat, ...]


@dataclass(frozen=True)
class DateTimeConfig:
    timezone: str


@dataclass(frozen=True)
class BetanoTarget:
    name: str
    sport_slug: str
    country_slug: str
    league_slug: str
    league_id: int


@dataclass(frozen=True)
class BetanoSiteConfig:
    site: str
    base_url: str
    browser: BrowserConfig
    output: OutputConfig
    datetime: DateTimeConfig
    targets: tuple[BetanoTarget, ...]



@dataclass(frozen=True)
class OddsRow:
    site: str
    country: str
    league: str
    target_name: str
    league_id: int
    source_url: str
    scraped_at: str
    live: bool
    match_date: Optional[str]
    match_time: Optional[str]
    fixture_date: Optional[str]
    home_team: str
    away_team: str
    odd_1: float
    odd_x: float
    odd_2: float
from dataclasses import dataclass
from typing import Literal


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
    region_id: int
    league_id: int
    market: str


@dataclass(frozen=True)
class BetanoSiteConfig:
    site: str
    base_url: str
    browser: BrowserConfig
    output: OutputConfig
    datetime: DateTimeConfig
    default_market: str
    targets: tuple[BetanoTarget, ...]
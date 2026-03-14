from dataclasses import dataclass
from typing import Literal, Optional


OutputFormat = Literal["csv", "json"]
DriverLifecycle = Literal["per_target", "per_run"]


@dataclass(frozen=True)
class BrowserConfig:
    headless: bool
    language: str
    page_load_timeout_seconds: int
    wait_after_load_min_seconds: float
    wait_after_load_max_seconds: float
    wait_after_overlay_dismiss_min_seconds: float
    wait_after_overlay_dismiss_max_seconds: float
    delay_between_targets_min_seconds: float
    delay_between_targets_max_seconds: float
    retry_backoff_base_seconds: float
    retry_backoff_max_seconds: float
    driver_lifecycle: DriverLifecycle
    abort_run_on_blocked: bool


@dataclass(frozen=True)
class OutputConfig:
    default_format: OutputFormat
    allowed_formats: tuple[OutputFormat, ...]


@dataclass(frozen=True)
class DateTimeConfig:
    timezone: str


@dataclass(frozen=True)
class SiteConfigBase:
    site: str
    base_url: str
    browser: BrowserConfig
    output: OutputConfig
    datetime: DateTimeConfig


@dataclass(frozen=True)
class CanonicalTarget:
    target_id: str
    sport_id: str
    country_id: str
    league_id: str


@dataclass(frozen=True)
class BetanoTarget(CanonicalTarget):
    name: str
    sport_slug: str
    country_slug: str
    league_slug: str
    source_league_id: int


@dataclass(frozen=True)
class BetanoSiteConfig(SiteConfigBase):
    targets: tuple[BetanoTarget, ...]


@dataclass(frozen=True)
class BwinTarget(CanonicalTarget):
    name: str
    sport_slug: str
    sport_id_numeric: int
    region_slug: str
    region_id_numeric: int
    competition_slug: str
    source_league_id: int


@dataclass(frozen=True)
class BwinSiteConfig(SiteConfigBase):
    targets: tuple[BwinTarget, ...]


@dataclass(frozen=True)
class BetclicTarget(CanonicalTarget):
    name: str
    sport_slug: str
    sport_code: str
    competition_slug: str
    source_league_id: int


@dataclass(frozen=True)
class BetclicSiteConfig(SiteConfigBase):
    targets: tuple[BetclicTarget, ...]


@dataclass(frozen=True)
class OddsRow:
    site: str
    sport_id: str
    country_id: str
    league_id: str
    target_id: str
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
    source_sport: str
    source_country: str
    source_league: str
    source_target_name: str
    source_league_id: int

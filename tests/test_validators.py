import pytest
from dataclasses import replace

from betting_odds_scraper.models import (
    BetanoSiteConfig,
    BetclicSiteConfig,
    BetanoTarget,
    BetclicTarget,
    BrowserConfig,
    DateTimeConfig,
    OutputConfig,
)
from betting_odds_scraper.validators import validate_betano_site_config, validate_betclic_site_config


def build_site_config(**overrides):
    config = BetanoSiteConfig(
        site="betano",
        base_url="https://www.betano.pt",
        browser=BrowserConfig(
            headless=False,
            language="pt-PT",
            page_load_timeout_seconds=60,
            wait_after_load_min_seconds=5,
            wait_after_load_max_seconds=9,
            wait_after_overlay_dismiss_min_seconds=1,
            wait_after_overlay_dismiss_max_seconds=3,
            delay_between_targets_min_seconds=0,
            delay_between_targets_max_seconds=0,
            retry_backoff_base_seconds=30,
            retry_backoff_max_seconds=120,
            driver_lifecycle="per_target",
            abort_run_on_blocked=True,
        ),
        output=OutputConfig(
            default_format="csv",
            allowed_formats=("csv", "json"),
        ),
        datetime=DateTimeConfig(
            timezone="UTC",
        ),
        targets=(
            BetanoTarget(
                target_id="primeira_liga",
                sport_id="football",
                country_id="portugal",
                league_id="primeira_liga",
                name="primeira_liga",
                sport_slug="futebol",
                country_slug="portugal",
                league_slug="primeira-liga",
                source_league_id=17083,
            ),
        ),
    )

    if overrides:
        config = replace(config, **overrides)
    return config



def test_validate_betano_site_config_accepts_valid_config():
    site_config = build_site_config()
    validate_betano_site_config(site_config)


def test_validate_betano_site_config_rejects_empty_targets():
    site_config = build_site_config()
    site_config = replace(site_config, targets=())

    with pytest.raises(ValueError, match="At least one target must be defined"):
        validate_betano_site_config(site_config)


def test_validate_betano_site_config_rejects_invalid_default_format():
    site_config = build_site_config()
    site_config = replace(
        site_config,
        output=OutputConfig(
            default_format="parquet",
            allowed_formats=("csv", "json"),
        ),
    )

    with pytest.raises(ValueError, match="output.default_format"):
        validate_betano_site_config(site_config)



def test_validate_betclic_site_config_accepts_valid_config():
    site_config = BetclicSiteConfig(
        site="betclic",
        base_url="https://www.betclic.pt",
        browser=BrowserConfig(
            headless=False,
            language="pt-PT",
            page_load_timeout_seconds=60,
            wait_after_load_min_seconds=5,
            wait_after_load_max_seconds=9,
            wait_after_overlay_dismiss_min_seconds=1,
            wait_after_overlay_dismiss_max_seconds=3,
            delay_between_targets_min_seconds=8,
            delay_between_targets_max_seconds=18,
            retry_backoff_base_seconds=30,
            retry_backoff_max_seconds=120,
            driver_lifecycle="per_run",
            abort_run_on_blocked=True,
        ),
        output=OutputConfig(
            default_format="csv",
            allowed_formats=("csv", "json"),
        ),
        datetime=DateTimeConfig(
            timezone="UTC",
        ),
        targets=(
            BetclicTarget(
                target_id="laliga",
                sport_id="football",
                country_id="spain",
                league_id="laliga",
                name="laliga",
                sport_slug="futebol",
                sport_code="football",
                competition_slug="espanha-la-liga",
                source_league_id=7,
            ),
        ),
    )

    validate_betclic_site_config(site_config)
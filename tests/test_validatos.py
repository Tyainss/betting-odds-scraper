import pytest

from betting_odds_scraper.models import (
    BetanoSiteConfig,
    BetanoTarget,
    BrowserConfig,
    DateTimeConfig,
    OutputConfig,
)
from betting_odds_scraper.validators import validate_betano_site_config


def build_site_config(**overrides):
    config = BetanoSiteConfig(
        site="betano",
        base_url="https://www.betano.pt",
        browser=BrowserConfig(
            headless=False,
            language="pt-PT",
            page_load_timeout_seconds=60,
            wait_after_load_seconds=8,
            wait_after_overlay_dismiss_seconds=2,
        ),
        output=OutputConfig(
            default_format="csv",
            allowed_formats=("csv", "json"),
        ),
        datetime=DateTimeConfig(
            timezone="UTC",
        ),
        default_market="matchresult",
        targets=(
            BetanoTarget(
                name="primeira_liga",
                sport_slug="futebol",
                country_slug="portugal",
                region_id=11382,
                league_id=17083,
                market="matchresult",
            ),
        ),
    )

    for key, value in overrides.items():
        setattr(config, key, value)

    return config


def test_validate_betano_site_config_accepts_valid_config():
    site_config = build_site_config()
    validate_betano_site_config(site_config)


def test_validate_betano_site_config_rejects_empty_targets():
    site_config = build_site_config()
    site_config = BetanoSiteConfig(
        site=site_config.site,
        base_url=site_config.base_url,
        browser=site_config.browser,
        output=site_config.output,
        datetime=site_config.datetime,
        default_market=site_config.default_market,
        targets=(),
    )

    with pytest.raises(ValueError, match="At least one target must be defined"):
        validate_betano_site_config(site_config)


def test_validate_betano_site_config_rejects_invalid_default_format():
    site_config = build_site_config()
    site_config = BetanoSiteConfig(
        site=site_config.site,
        base_url=site_config.base_url,
        browser=site_config.browser,
        output=OutputConfig(
            default_format="parquet",
            allowed_formats=("csv", "json"),
        ),
        datetime=site_config.datetime,
        default_market=site_config.default_market,
        targets=site_config.targets,
    )

    with pytest.raises(ValueError, match="output.default_format"):
        validate_betano_site_config(site_config)
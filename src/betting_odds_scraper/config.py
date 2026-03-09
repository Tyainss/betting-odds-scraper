from pathlib import Path
from typing import Any

import yaml

from betting_odds_scraper.models import (
    BetanoSiteConfig,
    BetanoTarget,
    BetclicSiteConfig,
    BetclicTarget,
    BrowserConfig,
    DateTimeConfig,
    OutputConfig,
)
from betting_odds_scraper.validators import (
    validate_betano_site_config,
    validate_betclic_site_config,
)


def _read_yaml_file(file_path: str | Path) -> dict[str, Any]:
    path = Path(file_path)

    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if not isinstance(data, dict):
        raise ValueError(f"Config file must contain a top-level mapping: {path}")

    return data


def _build_browser_config(browser_data: dict[str, Any]) -> BrowserConfig:
    return BrowserConfig(
        headless=bool(browser_data["headless"]),
        language=browser_data["language"],
        page_load_timeout_seconds=int(browser_data["page_load_timeout_seconds"]),
        wait_after_load_seconds=int(browser_data["wait_after_load_seconds"]),
        wait_after_overlay_dismiss_seconds=int(browser_data["wait_after_overlay_dismiss_seconds"]),
    )


def _build_output_config(output_data: dict[str, Any]) -> OutputConfig:
    return OutputConfig(
        default_format=output_data["default_format"],
        allowed_formats=tuple(output_data["allowed_formats"]),
    )


def _build_datetime_config(datetime_data: dict[str, Any]) -> DateTimeConfig:
    return DateTimeConfig(
        timezone=datetime_data["timezone"],
    )


def load_betano_site_config(file_path: str | Path) -> BetanoSiteConfig:
    data = _read_yaml_file(file_path)

    browser_data = data["browser"]
    output_data = data["output"]
    datetime_data = data["datetime"]
    targets_data = data["targets"]

    targets = tuple(
        BetanoTarget(
            target_id=target["canonical"]["target_id"],
            sport_id=target["canonical"]["sport_id"],
            country_id=target["canonical"]["country_id"],
            league_id=target["canonical"]["league_id"],
            name=target["name"],
            sport_slug=target["site_data"]["sport_slug"],
            country_slug=target["site_data"]["country_slug"],
            league_slug=target["site_data"]["league_slug"],
            source_league_id=int(target["site_data"]["source_league_id"]),
        )
        for target in targets_data
    )

    site_config = BetanoSiteConfig(
        site=data["site"],
        base_url=data["base_url"],
        browser=_build_browser_config(browser_data),
        output=_build_output_config(output_data),
        datetime=_build_datetime_config(datetime_data),
        targets=targets,
    )

    validate_betano_site_config(site_config)
    return site_config


def load_betclic_site_config(file_path: str | Path) -> BetclicSiteConfig:
    data = _read_yaml_file(file_path)

    browser_data = data["browser"]
    output_data = data["output"]
    datetime_data = data["datetime"]
    targets_data = data["targets"]

    targets = tuple(
        BetclicTarget(
            target_id=target["canonical"]["target_id"],
            sport_id=target["canonical"]["sport_id"],
            country_id=target["canonical"]["country_id"],
            league_id=target["canonical"]["league_id"],
            name=target["name"],
            sport_slug=target["site_data"]["sport_slug"],
            sport_code=target["site_data"]["sport_code"],
            competition_slug=target["site_data"]["competition_slug"],
            source_league_id=int(target["site_data"]["source_league_id"]),
        )
        for target in targets_data
    )

    site_config = BetclicSiteConfig(
        site=data["site"],
        base_url=data["base_url"],
        browser=_build_browser_config(browser_data),
        output=_build_output_config(output_data),
        datetime=_build_datetime_config(datetime_data),
        targets=targets,
    )

    validate_betclic_site_config(site_config)
    return site_config
from pathlib import Path
from typing import Any

import yaml

from betting_odds_scraper.models import (
    BetanoSiteConfig,
    BetanoTarget,
    BrowserConfig,
    DateTimeConfig,
    OutputConfig,
)
from betting_odds_scraper.validators import validate_betano_site_config


def _read_yaml_file(file_path: str | Path) -> dict[str, Any]:
    path = Path(file_path)

    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if not isinstance(data, dict):
        raise ValueError(f"Config file must contain a top-level mapping: {path}")

    return data


def load_betano_site_config(file_path: str | Path) -> BetanoSiteConfig:
    data = _read_yaml_file(file_path)

    browser_data = data["browser"]
    output_data = data["output"]
    datetime_data = data["datetime"]
    targets_data = data["targets"]

    targets = tuple(
        BetanoTarget(
            name=target["name"],
            sport_slug=target["sport_slug"],
            country_slug=target["country_slug"],
            league_slug=target["league_slug"],
            league_id=int(target["league_id"]),
        )
        for target in targets_data
    )

    site_config = BetanoSiteConfig(
        site=data["site"],
        base_url=data["base_url"],
        browser=BrowserConfig(
            headless=bool(browser_data["headless"]),
            language=browser_data["language"],
            page_load_timeout_seconds=int(browser_data["page_load_timeout_seconds"]),
            wait_after_load_seconds=int(browser_data["wait_after_load_seconds"]),
            wait_after_overlay_dismiss_seconds=int(browser_data["wait_after_overlay_dismiss_seconds"]),
        ),
        output=OutputConfig(
            default_format=output_data["default_format"],
            allowed_formats=tuple(output_data["allowed_formats"]),
        ),
        datetime=DateTimeConfig(
            timezone=datetime_data["timezone"],
        ),
        targets=targets,
    )

    validate_betano_site_config(site_config)

    return site_config
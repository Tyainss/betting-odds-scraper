from pathlib import Path
from typing import Any

import yaml

from betting_odds_scraper.models import (
    BetanoSiteConfig,
    BetanoTarget,
    BetclicSiteConfig,
    BetclicTarget,
    BwinSiteConfig,
    BwinTarget,
    BrowserConfig,
    DateTimeConfig,
    OutputConfig,
)
from betting_odds_scraper.validators import (
    validate_betano_site_config,
    validate_betclic_site_config,
    validate_bwin_site_config,
)


def _read_yaml_file(file_path: str | Path) -> dict[str, Any]:
    path = Path(file_path)

    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if not isinstance(data, dict):
        raise ValueError(f"Config file must contain a top-level mapping: {path}")

    return data


def _get_range(
    browser_data: dict[str, Any], prefix: str, legacy_key: str
) -> tuple[float, float]:
    legacy_value = float(browser_data.get(legacy_key, 0))
    min_value = float(browser_data.get(f"{prefix}_min_seconds", legacy_value))
    max_value = float(browser_data.get(f"{prefix}_max_seconds", legacy_value))
    return min_value, max_value


def _build_browser_config(browser_data: dict[str, Any]) -> BrowserConfig:
    wait_after_load_min_seconds, wait_after_load_max_seconds = _get_range(
        browser_data=browser_data,
        prefix="wait_after_load",
        legacy_key="wait_after_load_seconds",
    )
    wait_after_overlay_dismiss_min_seconds, wait_after_overlay_dismiss_max_seconds = (
        _get_range(
            browser_data=browser_data,
            prefix="wait_after_overlay_dismiss",
            legacy_key="wait_after_overlay_dismiss_seconds",
        )
    )

    return BrowserConfig(
        headless=bool(browser_data["headless"]),
        language=browser_data["language"],
        page_load_timeout_seconds=int(browser_data["page_load_timeout_seconds"]),
        wait_after_load_min_seconds=wait_after_load_min_seconds,
        wait_after_load_max_seconds=wait_after_load_max_seconds,
        wait_after_overlay_dismiss_min_seconds=wait_after_overlay_dismiss_min_seconds,
        wait_after_overlay_dismiss_max_seconds=wait_after_overlay_dismiss_max_seconds,
        delay_between_targets_min_seconds=float(
            browser_data.get("delay_between_targets_min_seconds", 0)
        ),
        delay_between_targets_max_seconds=float(
            browser_data.get("delay_between_targets_max_seconds", 0)
        ),
        retry_backoff_base_seconds=float(
            browser_data.get("retry_backoff_base_seconds", 30)
        ),
        retry_backoff_max_seconds=float(
            browser_data.get("retry_backoff_max_seconds", 120)
        ),
        driver_lifecycle=browser_data.get("driver_lifecycle", "per_target"),
        abort_run_on_blocked=bool(browser_data.get("abort_run_on_blocked", True)),
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


def load_bwin_site_config(file_path: str | Path) -> BwinSiteConfig:
    data = _read_yaml_file(file_path)

    browser_data = data["browser"]
    output_data = data["output"]
    datetime_data = data["datetime"]
    targets_data = data["targets"]

    targets = tuple(
        BwinTarget(
            target_id=target["canonical"]["target_id"],
            sport_id=target["canonical"]["sport_id"],
            country_id=target["canonical"]["country_id"],
            league_id=target["canonical"]["league_id"],
            name=target["name"],
            sport_slug=target["site_data"]["sport_slug"],
            sport_id_numeric=int(target["site_data"]["sport_id_numeric"]),
            region_slug=target["site_data"]["region_slug"],
            region_id_numeric=int(target["site_data"]["region_id_numeric"]),
            competition_slug=target["site_data"]["competition_slug"],
            source_league_id=int(target["site_data"]["source_league_id"]),
        )
        for target in targets_data
    )

    site_config = BwinSiteConfig(
        site=data["site"],
        base_url=data["base_url"],
        browser=_build_browser_config(browser_data),
        output=_build_output_config(output_data),
        datetime=_build_datetime_config(datetime_data),
        targets=targets,
    )

    validate_bwin_site_config(site_config)
    return site_config

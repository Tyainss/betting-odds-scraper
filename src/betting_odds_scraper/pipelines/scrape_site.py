from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Protocol
import random
import time

from betting_odds_scraper.browser.selenium_driver import build_chrome_driver
from betting_odds_scraper.logger import get_logger
from betting_odds_scraper.storage.csv_writer import (
    append_rows_to_csv,
    write_rows_to_csv,
)
from betting_odds_scraper.storage.json_writer import (
    append_rows_to_json,
    write_rows_to_json,
)
from betting_odds_scraper.scrapers.exceptions import (
    PageStructureChangedError,
    SiteBlockedError,
    TransientNavigationError,
)


class ScrapeTargetProtocol(Protocol):
    name: str


class SiteScraperProtocol(Protocol):
    site_name: str

    def scrape_target(self, target: ScrapeTargetProtocol) -> list[dict[str, Any]]: ...


def _build_latest_output_path(base_dir, site_name, output_format):
    return Path(base_dir) / "latest" / f"{site_name}_latest.{output_format}"


def _build_history_output_path(base_dir, site_name, output_format):
    return Path(base_dir) / "history" / f"{site_name}_history.{output_format}"


def _build_output_path(base_dir, site_name, output_format):
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return Path(base_dir) / f"{site_name}_{timestamp}.{output_format}"


def _build_target_output_path(base_dir, site_name, target_name, output_format):
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return Path(base_dir) / f"{site_name}_{target_name}_{timestamp}.{output_format}"


def _write_rows(rows, output_path, output_format):
    if output_format == "csv":
        write_rows_to_csv(rows, output_path)
    elif output_format == "json":
        write_rows_to_json(rows, output_path)


def _append_rows(rows, output_path, output_format):
    if output_format == "csv":
        append_rows_to_csv(rows, output_path)
    elif output_format == "json":
        append_rows_to_json(rows, output_path)


def _filter_targets(targets, target_names):
    if not target_names:
        return targets

    selected_targets = tuple(
        target for target in targets if target.name in target_names
    )

    if not selected_targets:
        raise ValueError(f"No targets matched: {sorted(target_names)}")

    return selected_targets


def _sleep_between_targets(browser_config, logger, site_name, target_name):
    delay_seconds = random.uniform(
        browser_config.delay_between_targets_min_seconds,
        browser_config.delay_between_targets_max_seconds,
    )
    if delay_seconds <= 0:
        return

    logger.info(
        "Sleeping between targets site=%s target=%s delay_seconds=%.2f",
        site_name,
        target_name,
        delay_seconds,
    )
    time.sleep(delay_seconds)


def _compute_retry_delay_seconds(browser_config, attempt_number):
    upper_bound = min(
        browser_config.retry_backoff_max_seconds,
        browser_config.retry_backoff_base_seconds * (2 ** (attempt_number - 1)),
    )
    return random.uniform(
        browser_config.retry_backoff_base_seconds,
        upper_bound,
    )


def _build_site_scraper(
    site_config, scraper_factory, chromedriver_path, headless_override
):
    driver = build_chrome_driver(
        browser_config=site_config.browser,
        chromedriver_path=chromedriver_path,
        headless_override=headless_override,
    )
    scraper = scraper_factory(
        driver=driver,
        site_config=site_config,
    )
    return driver, scraper


def _scrape_target_with_retries(scraper, target, retries, retry_delay_seconds, logger):
    last_error = None

    for attempt in range(1, retries + 2):
        try:
            logger.info(
                "Scraping site=%s target=%s attempt=%s/%s",
                scraper.site_name,
                target.name,
                attempt,
                retries + 1,
            )
            return scraper.scrape_target(target)
        except SiteBlockedError:
            logger.exception(
                "Blocked site=%s target=%s attempt=%s/%s",
                scraper.site_name,
                target.name,
                attempt,
                retries + 1,
            )
            raise
        except PageStructureChangedError:
            logger.exception(
                "Structure changed site=%s target=%s attempt=%s/%s",
                scraper.site_name,
                target.name,
                attempt,
                retries + 1,
            )
            raise
        except TransientNavigationError as exc:
            last_error = exc
            logger.exception(
                "Transient failure site=%s target=%s attempt=%s/%s",
                scraper.site_name,
                target.name,
                attempt,
                retries + 1,
            )
            if attempt < retries + 1:
                delay_seconds = _compute_retry_delay_seconds(
                    browser_config=scraper.site_config.browser,
                    attempt_number=attempt,
                )
                logger.info(
                    "Retrying site=%s target=%s after delay_seconds=%.2f",
                    scraper.site_name,
                    target.name,
                    delay_seconds,
                )
                time.sleep(delay_seconds)
        except Exception as exc:
            last_error = exc
            logger.exception(
                "Failed site=%s target=%s attempt=%s/%s",
                scraper.site_name,
                target.name,
                attempt,
                retries + 1,
            )
            raise

    raise last_error


def run_site_scrape(
    site_config,
    scraper_factory: Callable[..., SiteScraperProtocol],
    output_format=None,
    output_dir="data/processed",
    chromedriver_path=None,
    split_by_target=False,
    target_names=None,
    headless_override=None,
    continue_on_error=False,
    retries=1,
    retry_delay_seconds=2,
    write_latest=True,
    append_history=False,
):
    logger = get_logger(__name__)

    selected_output_format = output_format or site_config.output.default_format
    if selected_output_format not in site_config.output.allowed_formats:
        raise ValueError(
            f"Unsupported output format: {selected_output_format}. "
            f"Allowed formats: {site_config.output.allowed_formats}"
        )

    selected_targets = _filter_targets(site_config.targets, set(target_names or []))

    all_rows = []
    target_output_paths = []
    failed_targets = []
    stopped_reason = None
    driver_lifecycle = site_config.browser.driver_lifecycle

    shared_driver = None
    shared_scraper = None

    if driver_lifecycle == "per_run":
        shared_driver, shared_scraper = _build_site_scraper(
            site_config=site_config,
            scraper_factory=scraper_factory,
            chromedriver_path=chromedriver_path,
            headless_override=headless_override,
        )

    try:
        for target_index, target in enumerate(selected_targets):
            target_rows = []
            driver = None

            if driver_lifecycle == "per_run":
                scraper = shared_scraper
            else:
                driver, scraper = _build_site_scraper(
                    site_config=site_config,
                    scraper_factory=scraper_factory,
                    chromedriver_path=chromedriver_path,
                    headless_override=headless_override,
                )

            try:
                try:
                    target_rows = _scrape_target_with_retries(
                        scraper=scraper,
                        target=target,
                        retries=retries,
                        retry_delay_seconds=retry_delay_seconds,
                        logger=logger,
                    )
                    all_rows.extend(target_rows)
                except SiteBlockedError:
                    failed_targets.append(target.name)
                    stopped_reason = "site_blocked"
                    logger.exception(
                        "Stopping run because site=%s returned a blocked page for target=%s",
                        site_config.site,
                        target.name,
                    )
                    if site_config.browser.abort_run_on_blocked:
                        break
                    raise
                except Exception:
                    failed_targets.append(target.name)
                    if continue_on_error:
                        logger.exception(
                            "Skipping failed site=%s target=%s",
                            site_config.site,
                            target.name,
                        )
                        continue
                    raise

                if split_by_target and target_rows:
                    target_output_path = _build_target_output_path(
                        base_dir=output_dir,
                        site_name=site_config.site,
                        target_name=target.name,
                        output_format=selected_output_format,
                    )
                    _write_rows(target_rows, target_output_path, selected_output_format)
                    target_output_paths.append(target_output_path)
                    logger.info(
                        "Saved site=%s target=%s rows=%s path=%s",
                        site_config.site,
                        target.name,
                        len(target_rows),
                        target_output_path,
                    )

                is_last_target = target_index == len(selected_targets) - 1
                if not is_last_target:
                    _sleep_between_targets(
                        browser_config=site_config.browser,
                        logger=logger,
                        site_name=site_config.site,
                        target_name=target.name,
                    )
            finally:
                if driver_lifecycle == "per_target" and driver is not None:
                    driver.quit()
    finally:
        if shared_driver is not None:
            shared_driver.quit()

    merged_output_path = _build_output_path(
        base_dir=output_dir,
        site_name=site_config.site,
        output_format=selected_output_format,
    )
    _write_rows(all_rows, merged_output_path, selected_output_format)

    latest_output_path = None
    if write_latest:
        latest_output_path = _build_latest_output_path(
            base_dir=output_dir,
            site_name=site_config.site,
            output_format=selected_output_format,
        )
        _write_rows(all_rows, latest_output_path, selected_output_format)

    history_output_path = None
    if append_history:
        history_output_path = _build_history_output_path(
            base_dir=output_dir,
            site_name=site_config.site,
            output_format=selected_output_format,
        )
        _append_rows(all_rows, history_output_path, selected_output_format)

    return {
        "merged_output_path": merged_output_path,
        "latest_output_path": latest_output_path,
        "history_output_path": history_output_path,
        "target_output_paths": target_output_paths,
        "rows": all_rows,
        "failed_targets": failed_targets,
        "stopped_reason": stopped_reason,
    }

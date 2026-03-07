from datetime import datetime, timezone
from pathlib import Path

from betting_odds_scraper.browser.selenium_driver import build_chrome_driver
from betting_odds_scraper.config import load_betano_site_config
from betting_odds_scraper.scrapers.betano.scraper import BetanoScraper
from betting_odds_scraper.storage.csv_writer import write_rows_to_csv
from betting_odds_scraper.storage.json_writer import write_rows_to_json


def _build_output_path(base_dir, site_name, output_format):
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return Path(base_dir) / f"{site_name}_{timestamp}.{output_format}"


def run_betano_scrape(
    config_path,
    output_format=None,
    output_dir="data/processed",
    chromedriver_path=None,
):
    site_config = load_betano_site_config(config_path)

    selected_output_format = output_format or site_config.output.default_format
    if selected_output_format not in site_config.output.allowed_formats:
        raise ValueError(
            f"Unsupported output format: {selected_output_format}. "
            f"Allowed formats: {site_config.output.allowed_formats}"
        )

    driver = build_chrome_driver(
        browser_config=site_config.browser,
        chromedriver_path=chromedriver_path,
    )

    try:
        scraper = BetanoScraper(
            driver=driver,
            site_config=site_config,
        )

        all_rows = []
        for target in site_config.targets:
            target_rows = scraper.scrape_target(target)
            all_rows.extend(target_rows)

    finally:
        driver.quit()

    output_path = _build_output_path(
        base_dir=output_dir,
        site_name=site_config.site,
        output_format=selected_output_format,
    )

    if selected_output_format == "csv":
        write_rows_to_csv(all_rows, output_path)
    elif selected_output_format == "json":
        write_rows_to_json(all_rows, output_path)

    return output_path, all_rows
from betting_odds_scraper.config import load_bwin_site_config
from betting_odds_scraper.pipelines.scrape_site import run_site_scrape
from betting_odds_scraper.scrapers.bwin.scraper import BwinScraper


def run_bwin_scrape(
    config_path,
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
    site_config = load_bwin_site_config(config_path)
    return run_site_scrape(
        site_config=site_config,
        scraper_factory=BwinScraper,
        output_format=output_format,
        output_dir=output_dir,
        chromedriver_path=chromedriver_path,
        split_by_target=split_by_target,
        target_names=target_names,
        headless_override=headless_override,
        continue_on_error=continue_on_error,
        retries=retries,
        retry_delay_seconds=retry_delay_seconds,
        write_latest=write_latest,
        append_history=append_history,
    )
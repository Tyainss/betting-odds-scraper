
import time
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from betting_odds_scraper.logger import get_logger
from betting_odds_scraper.scrapers.betano.parser import (
    extract_initial_state_from_html,
    extract_rows_from_initial_state,
)
from betting_odds_scraper.scrapers.betano.selectors import (
    COOKIE_ACCEPT_XPATHS,
)
from betting_odds_scraper.scrapers.betano.url_builder import build_betano_league_url


class BetanoScraper:
    def __init__(self, driver, site_config):
        self.site_name = site_config.site
        self.driver = driver
        self.site_config = site_config
        self.logger = get_logger(__name__)
        self.debug_dir = Path("data/raw/debug")

    def scrape_target(self, target):
        url = build_betano_league_url(
            site_config=self.site_config,
            target=target,
        )
        return self.scrape_target_url(target=target, url=url)

    def scrape_target_url(self, target, url):
        self.logger.info("Scraping target=%s url=%s", target.name, url)

        try:
            self.driver.get(url)
        except Exception:
            self._save_debug_artifacts(target.name)
            raise

        self._wait_for_page_ready(target.name)

        self._dismiss_overlays()
        self._wait_for_page_ready(target.name)
        time.sleep(self.site_config.browser.wait_after_overlay_dismiss_seconds)

        try:
            html = self.driver.page_source
            initial_state = extract_initial_state_from_html(html)
            parsed_rows = extract_rows_from_initial_state(
                initial_state=initial_state,
                site_name=self.site_config.site,
                target_id=target.target_id,
                sport_id=target.sport_id,
                country_id=target.country_id,
                league_id=target.league_id,
                source_sport=target.sport_slug,
                source_country=target.country_slug,
                source_league=target.league_slug,
                source_target_name=target.name,
                source_league_id=target.source_league_id,
                source_url=url,
                source_timezone=self.site_config.datetime.timezone,
            )

            self.logger.info("Target=%s parsed_rows=%s", target.name, len(parsed_rows))

            return [row.__dict__ for row in parsed_rows]
        except Exception:
            self._save_debug_artifacts(target.name)
            raise


    def _dismiss_overlays(self):
        for xpath in COOKIE_ACCEPT_XPATHS:
            try:
                button = self.driver.find_element(By.XPATH, xpath)
                self.driver.execute_script("arguments[0].click();", button)
                time.sleep(1)
            except Exception:
                continue

    def _wait_for_page_ready(self, target_name, timeout=25):
        wait = WebDriverWait(self.driver, timeout)
        wait.until(lambda driver: 'window["initial_state"]' in driver.page_source)
        self.logger.info("Page ready for target=%s using initial_state", target_name)
    

    def _save_debug_artifacts(self, target_name):
        self.debug_dir.mkdir(parents=True, exist_ok=True)

        screenshot_path = self.debug_dir / f"{target_name}.png"
        html_path = self.debug_dir / f"{target_name}.html"

        try:
            self.driver.save_screenshot(str(screenshot_path))
            html_path.write_text(self.driver.page_source, encoding="utf-8")
            self.logger.info("Saved debug artifacts for target=%s", target_name)
        except Exception:
            self.logger.exception("Failed to save debug artifacts for target=%s", target_name)
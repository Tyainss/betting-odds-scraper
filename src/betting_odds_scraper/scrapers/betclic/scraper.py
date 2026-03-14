import random
import time
from pathlib import Path

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from betting_odds_scraper.logger import get_logger
from betting_odds_scraper.scrapers.betclic.parser import (
    extract_ng_state_from_html,
    extract_rows_from_ng_state,
)
from betting_odds_scraper.scrapers.betclic.selectors import (
    BLOCK_PAGE_MARKERS,
    COOKIE_ACCEPT_SELECTORS,
    PAGE_READY_MARKERS,
)
from betting_odds_scraper.scrapers.betclic.url_builder import build_betclic_league_url
from betting_odds_scraper.scrapers.exceptions import (
    PageStructureChangedError,
    SiteBlockedError,
    TransientNavigationError,
)


class BetclicScraper:
    def __init__(self, driver, site_config):
        self.site_name = site_config.site
        self.driver = driver
        self.site_config = site_config
        self.logger = get_logger(__name__)
        self.debug_dir = Path("data/raw/debug")

    def scrape_target(self, target):
        url = build_betclic_league_url(
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
        self._sleep_random(
            self.site_config.browser.wait_after_load_min_seconds,
            self.site_config.browser.wait_after_load_max_seconds,
        )
        self._dismiss_overlays()
        self._wait_for_page_ready(target.name)

        try:
            html = self.driver.page_source
            ng_state = extract_ng_state_from_html(html)
            parsed_rows = extract_rows_from_ng_state(
                ng_state=ng_state,
                site_name=self.site_config.site,
                target_id=target.target_id,
                sport_id=target.sport_id,
                country_id=target.country_id,
                league_id=target.league_id,
                source_sport=target.sport_slug,
                source_country=target.country_id,
                source_league=target.competition_slug,
                source_target_name=target.name,
                source_league_id=target.source_league_id,
                source_url=url,
            )

            self.logger.info("Target=%s parsed_rows=%s", target.name, len(parsed_rows))
            return [row.__dict__ for row in parsed_rows]
        except SiteBlockedError:
            self._save_debug_artifacts(target.name)
            raise
        except Exception as exc:
            self._save_debug_artifacts(target.name)
            raise PageStructureChangedError(
                f"Failed to parse Betclic page for target={target.name}"
            ) from exc

    def _dismiss_overlays(self):
        for selector in COOKIE_ACCEPT_SELECTORS:
            try:
                button = self.driver.find_element(By.CSS_SELECTOR, selector)
                if button.is_displayed():
                    self.driver.execute_script("arguments[0].click();", button)
                    self._sleep_random(
                        self.site_config.browser.wait_after_overlay_dismiss_min_seconds,
                        self.site_config.browser.wait_after_overlay_dismiss_max_seconds,
                    )
                    return
            except Exception:
                continue

    def _wait_for_page_ready(self, target_name):
        wait = WebDriverWait(
            self.driver, self.site_config.browser.page_load_timeout_seconds
        )

        try:
            wait.until(
                lambda driver: (
                    self._page_has_ready_markers(driver.page_source)
                    or self._page_is_blocked(driver.page_source)
                )
            )
        except TimeoutException as exc:
            if self._page_is_blocked(self.driver.page_source):
                raise SiteBlockedError(
                    f"Betclic blocked access for target={target_name}"
                ) from exc
            raise TransientNavigationError(
                f"Betclic page did not become ready for target={target_name}"
            ) from exc

        if self._page_is_blocked(self.driver.page_source):
            raise SiteBlockedError(f"Betclic blocked access for target={target_name}")

        self.logger.info(
            "Page ready for target=%s using ng-state/card markers", target_name
        )

    def _page_has_ready_markers(self, page_source):
        return all(marker in page_source for marker in PAGE_READY_MARKERS)

    def _page_is_blocked(self, page_source):
        normalized_page_source = page_source.lower()
        return any(marker in normalized_page_source for marker in BLOCK_PAGE_MARKERS)

    def _sleep_random(self, min_seconds, max_seconds):
        if max_seconds <= 0:
            return

        delay_seconds = random.uniform(min_seconds, max_seconds)
        time.sleep(delay_seconds)

    def _save_debug_artifacts(self, target_name):
        self.debug_dir.mkdir(parents=True, exist_ok=True)

        screenshot_path = self.debug_dir / f"{self.site_name}_{target_name}.png"
        html_path = self.debug_dir / f"{self.site_name}_{target_name}.html"

        try:
            self.driver.save_screenshot(str(screenshot_path))
            html_path.write_text(self.driver.page_source, encoding="utf-8")
            self.logger.info("Saved debug artifacts for target=%s", target_name)
        except Exception:
            self.logger.exception(
                "Failed to save debug artifacts for target=%s", target_name
            )

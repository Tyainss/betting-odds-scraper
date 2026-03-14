import json
import random
import time
from pathlib import Path

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

from betting_odds_scraper.logger import get_logger
from betting_odds_scraper.scrapers.bwin.parser import extract_rows_from_bwin_widget_data
from betting_odds_scraper.scrapers.bwin.selectors import BLOCK_PAGE_MARKERS
from betting_odds_scraper.scrapers.bwin.url_builder import (
    build_bwin_league_url,
    build_bwin_widgetdata_path,
)
from betting_odds_scraper.scrapers.exceptions import (
    PageStructureChangedError,
    SiteBlockedError,
    TransientNavigationError,
)


class BwinScraper:
    def __init__(self, driver, site_config):
        self.site_name = site_config.site
        self.driver = driver
        self.site_config = site_config
        self.logger = get_logger(__name__)
        self.debug_dir = Path("data/raw/debug")

    def scrape_target(self, target):
        url = build_bwin_league_url(
            site_config=self.site_config,
            target=target,
        )
        widgetdata_path = build_bwin_widgetdata_path(target=target)
        return self.scrape_target_url(
            target=target,
            url=url,
            widgetdata_path=widgetdata_path,
        )

    def scrape_target_url(self, target, url, widgetdata_path):
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

        try:
            widget_data = self._fetch_widget_data(widgetdata_path)
            parsed_rows = extract_rows_from_bwin_widget_data(
                widget_data=widget_data,
                site_name=self.site_config.site,
                target_id=target.target_id,
                sport_id=target.sport_id,
                country_id=target.country_id,
                league_id=target.league_id,
                source_sport=target.sport_slug,
                source_country=target.region_slug,
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
                f"Failed to parse Bwin widget data for target={target.name}"
            ) from exc

    def _wait_for_page_ready(self, target_name):
        wait = WebDriverWait(
            self.driver, self.site_config.browser.page_load_timeout_seconds
        )

        try:
            wait.until(
                lambda driver: (
                    driver.execute_script("return document.readyState") == "complete"
                )
            )
        except TimeoutException as exc:
            if self._page_is_blocked(self.driver.page_source):
                raise SiteBlockedError(
                    f"Bwin blocked access for target={target_name}"
                ) from exc
            raise TransientNavigationError(
                f"Bwin page did not become ready for target={target_name}"
            ) from exc

        if self._page_is_blocked(self.driver.page_source):
            raise SiteBlockedError(f"Bwin blocked access for target={target_name}")

        self.logger.info("Page shell ready for target=%s", target_name)

    def _fetch_widget_data(self, widgetdata_path):
        result = self.driver.execute_async_script(
            """
            const callback = arguments[arguments.length - 1];
            const widgetdataPath = arguments[0];

            fetch(widgetdataPath, {
                method: "GET",
                credentials: "include",
                cache: "no-store"
            })
            .then(async (response) => {
                const text = await response.text();
                callback({
                    ok: response.ok,
                    status: response.status,
                    url: response.url,
                    content_type: response.headers.get("content-type"),
                    body: text
                });
            })
            .catch((error) => {
                callback({
                    error: String(error)
                });
            });
            """,
            widgetdata_path,
        )

        if result.get("error"):
            raise TransientNavigationError(
                f"Bwin widget fetch failed: {result['error']}"
            )

        body = result.get("body") or ""
        content_type = (result.get("content_type") or "").lower()

        if self._page_is_blocked(body):
            raise SiteBlockedError("Bwin widget fetch returned a blocked response")

        if "application/json" not in content_type:
            raise ValueError(
                f"Bwin widget fetch returned non-JSON content_type={result.get('content_type')}"
            )

        return json.loads(body)

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

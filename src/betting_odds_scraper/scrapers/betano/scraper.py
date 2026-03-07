import re
import time
from pathlib import Path

from selenium.webdriver.common.by import By

from betting_odds_scraper.logger import get_logger
from betting_odds_scraper.scrapers.betano.parser import (
    is_valid_match_block,
    parse_match_block,
)
from betting_odds_scraper.scrapers.betano.selectors import (
    COOKIE_ACCEPT_XPATHS,
    MATCH_BLOCKS_XPATH,
)
from betting_odds_scraper.scrapers.betano.url_builder import build_betano_league_url


class BetanoScraper:
    def __init__(self, driver, site_config):
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

        time.sleep(self.site_config.browser.wait_after_load_seconds)

        self._dismiss_overlays()
        time.sleep(self.site_config.browser.wait_after_overlay_dismiss_seconds)

        try:
            raw_blocks = self._get_candidate_blocks()
            valid_blocks = [block for block in raw_blocks if is_valid_match_block(block)]

            self.logger.info(
                "Target=%s candidate_blocks=%s valid_blocks=%s",
                target.name,
                len(raw_blocks),
                len(valid_blocks),
            )

            parsed_rows = [
                parse_match_block(
                    text=block,
                    site_name=self.site_config.site,
                    target_name=target.name,
                    country_name=target.country_slug,
                    league_name=target.name,
                    region_id=target.region_id,
                    league_id=target.league_id,
                    source_url=url,
                    source_timezone=self.site_config.datetime.timezone,
                )
                for block in valid_blocks
            ]

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

    def _get_candidate_blocks(self):
        elements = self.driver.find_elements(By.XPATH, MATCH_BLOCKS_XPATH)

        blocks = []
        seen = set()

        for element in elements:
            try:
                text = element.text.strip()
                if not text:
                    continue

                normalized_text = re.sub(r"\s+", "\n", text.strip())
                if normalized_text in seen:
                    continue

                seen.add(normalized_text)
                blocks.append(text)
            except Exception:
                continue

        return blocks
    

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
import re
import time

from selenium.webdriver.common.by import By

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

    def scrape_target(self, target):
        url = build_betano_league_url(
            site_config=self.site_config,
            target=target,
        )

        self.driver.get(url)
        time.sleep(self.site_config.browser.wait_after_load_seconds)

        self._dismiss_overlays()
        time.sleep(self.site_config.browser.wait_after_overlay_dismiss_seconds)

        raw_blocks = self._get_candidate_blocks()
        valid_blocks = [block for block in raw_blocks if is_valid_match_block(block)]

        parsed_rows = [
            parse_match_block(
                text=block,
                site_name=self.site_config.site,
                country_name=target.country_slug,
                league_name=target.name,
                source_timezone=self.site_config.datetime.timezone,
            )
            for block in valid_blocks
        ]

        return parsed_rows

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
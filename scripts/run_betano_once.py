from betting_odds_scraper.browser.selenium_driver import build_chrome_driver
from betting_odds_scraper.config import load_betano_site_config
from betting_odds_scraper.scrapers.betano.scraper import BetanoScraper


CONFIG_PATH = "configs/sites/betano.yaml"
CHROMEDRIVER_PATH = None


def main():
    site_config = load_betano_site_config(CONFIG_PATH)
    driver = build_chrome_driver(
        browser_config=site_config.browser,
        chromedriver_path=CHROMEDRIVER_PATH,
    )

    try:
        scraper = BetanoScraper(
            driver=driver,
            site_config=site_config,
        )

        for target in site_config.targets:
            rows = scraper.scrape_target(target)

            print(f"\nTarget: {target.name}")
            print(f"Rows found: {len(rows)}")

            for row in rows:
                print(row)

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from betting_odds_scraper.models import BrowserConfig


def build_chrome_driver(
    browser_config: BrowserConfig,
    chromedriver_path: str | None = None,
    headless_override: bool | None = None,
) -> webdriver.Chrome:
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"--lang={browser_config.language}")
    options.add_argument("--disable-notifications")

    run_headless = (
        browser_config.headless if headless_override is None else headless_override
    )

    if run_headless:
        options.add_argument("--headless=new")

    if chromedriver_path:
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
    else:
        driver = webdriver.Chrome(options=options)

    driver.set_page_load_timeout(browser_config.page_load_timeout_seconds)

    return driver

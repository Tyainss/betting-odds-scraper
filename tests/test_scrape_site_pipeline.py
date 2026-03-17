from types import SimpleNamespace

import pytest

from betting_odds_scraper.pipelines.scrape_site import run_site_scrape
from betting_odds_scraper.scrapers.exceptions import TransientNavigationError


class _DummyDriver:
    def quit(self):
        return None


class _FakeScraper:
    def __init__(self, driver, site_config):
        self.driver = driver
        self.site_config = site_config
        self.site_name = site_config.site

    def scrape_target(self, target):
        if target.name == "missing":
            raise TransientNavigationError("page unavailable")

        return [{"target": target.name, "site": self.site_name}]


def _build_site_config(tmp_path):
    return SimpleNamespace(
        site="test-site",
        targets=(
            SimpleNamespace(name="ok"),
            SimpleNamespace(name="missing"),
            SimpleNamespace(name="ok-2"),
        ),
        output=SimpleNamespace(
            default_format="json",
            allowed_formats=("json", "csv"),
        ),
        browser=SimpleNamespace(
            driver_lifecycle="per_target",
            delay_between_targets_min_seconds=0,
            delay_between_targets_max_seconds=0,
            retry_backoff_base_seconds=0,
            retry_backoff_max_seconds=0,
            abort_run_on_blocked=True,
        ),
    )


def test_run_site_scrape_continues_after_target_failure_by_default(
    monkeypatch, tmp_path
):
    site_config = _build_site_config(tmp_path)

    def _fake_build_site_scraper(**kwargs):
        driver = _DummyDriver()
        scraper = _FakeScraper(driver=driver, site_config=kwargs["site_config"])
        return driver, scraper

    monkeypatch.setattr(
        "betting_odds_scraper.pipelines.scrape_site._build_site_scraper",
        _fake_build_site_scraper,
    )

    result = run_site_scrape(
        site_config=site_config,
        scraper_factory=_FakeScraper,
        output_format="json",
        output_dir=tmp_path,
        retries=0,
    )

    assert [row["target"] for row in result["rows"]] == ["ok", "ok-2"]
    assert result["failed_targets"] == ["missing"]


def test_run_site_scrape_can_still_fail_fast(monkeypatch, tmp_path):
    site_config = _build_site_config(tmp_path)

    def _fake_build_site_scraper(**kwargs):
        driver = _DummyDriver()
        scraper = _FakeScraper(driver=driver, site_config=kwargs["site_config"])
        return driver, scraper

    monkeypatch.setattr(
        "betting_odds_scraper.pipelines.scrape_site._build_site_scraper",
        _fake_build_site_scraper,
    )

    with pytest.raises(TransientNavigationError):
        run_site_scrape(
            site_config=site_config,
            scraper_factory=_FakeScraper,
            output_format="json",
            output_dir=tmp_path,
            continue_on_error=False,
            retries=0,
        )

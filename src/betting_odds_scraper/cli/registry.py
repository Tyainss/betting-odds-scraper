from dataclasses import dataclass
from typing import Any, Callable

from betting_odds_scraper.pipelines.scrape_betano import run_betano_scrape
from betting_odds_scraper.pipelines.scrape_betclic import run_betclic_scrape
from betting_odds_scraper.pipelines.scrape_bwin import run_bwin_scrape


RunnerFn = Callable[..., dict[str, Any]]


@dataclass(frozen=True)
class SiteDefinition:
    site_name: str
    default_config_path: str
    runner: RunnerFn


SITE_REGISTRY: dict[str, SiteDefinition] = {
    "betano": SiteDefinition(
        site_name="betano",
        default_config_path="configs/sites/betano.yaml",
        runner=run_betano_scrape,
    ),
    "betclic": SiteDefinition(
        site_name="betclic",
        default_config_path="configs/sites/betclic.yaml",
        runner=run_betclic_scrape,
    ),
    "bwin": SiteDefinition(
        site_name="bwin",
        default_config_path="configs/sites/bwin.yaml",
        runner=run_bwin_scrape,
    ),
}


def get_site_definition(site_name: str) -> SiteDefinition:
    try:
        return SITE_REGISTRY[site_name]
    except KeyError as exc:
        supported = ", ".join(sorted(SITE_REGISTRY))
        raise ValueError(f"Unsupported site '{site_name}'. Supported sites: {supported}") from exc


def get_supported_sites() -> list[str]:
    return sorted(SITE_REGISTRY)
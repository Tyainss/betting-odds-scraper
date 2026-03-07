
from betting_odds_scraper.models import BetanoSiteConfig, BetanoTarget


def build_betano_league_url(
    site_config: BetanoSiteConfig,
    target: BetanoTarget,
) -> str:
    return (
        f"{site_config.base_url}/sport/"
        f"{target.sport_slug}/competicoes/"
        f"{target.country_slug}/{target.region_id}/"
        f"?bt={target.market}&sl={target.league_id}"
    )
from betting_odds_scraper.models import BetanoSiteConfig, BetanoTarget


def build_betano_league_url(
    site_config: BetanoSiteConfig,
    target: BetanoTarget,
) -> str:
    return (
        f"{site_config.base_url}/sport/"
        f"{target.sport_slug}/"
        f"{target.country_slug}/"
        f"{target.league_slug}/"
        f"{target.source_league_id}/"
    )

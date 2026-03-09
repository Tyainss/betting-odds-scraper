from betting_odds_scraper.models import BetclicSiteConfig, BetclicTarget


def build_betclic_league_url(
    site_config: BetclicSiteConfig,
    target: BetclicTarget,
) -> str:
    return (
        f"{site_config.base_url}/"
        f"{target.sport_slug}-s{target.sport_code}/"
        f"{target.competition_slug}-c{target.source_league_id}"
    )
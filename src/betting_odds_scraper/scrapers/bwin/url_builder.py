from betting_odds_scraper.models import BwinSiteConfig, BwinTarget


DEFAULT_WIDGET_ID = (
    "/mobilesports-v1.0/layout/layout_standards/modules/competition/defaultcontainer"
)


def build_bwin_league_url(
    site_config: BwinSiteConfig,
    target: BwinTarget,
) -> str:
    return (
        f"{site_config.base_url}/pt/sports/"
        f"{target.sport_slug}-{target.sport_id_numeric}/"
        f"apostar/"
        f"{target.region_slug}-{target.region_id_numeric}/"
        f"{target.competition_slug}-{target.source_league_id}"
    )


def build_bwin_widgetdata_path(
    target: BwinTarget,
    widget_id: str = DEFAULT_WIDGET_ID,
) -> str:
    return (
        "/pt/sports/api/widget/widgetdata"
        f"?layoutSize=Large"
        f"&page=CompetitionLobby"
        f"&sportId={target.sport_id_numeric}"
        f"&regionId={target.region_id_numeric}"
        f"&competitionId={target.source_league_id}"
        f"&compoundCompetitionId=2:{target.source_league_id}"
        f"&widgetId={widget_id}"
        f"&shouldIncludePayload=true"
    )

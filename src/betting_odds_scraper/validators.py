def validate_site_config_common(site_config):
    if not site_config.site:
        raise ValueError("site must not be empty")

    if not site_config.base_url:
        raise ValueError("base_url must not be empty")
    
    if not site_config.targets:
        raise ValueError("At least one target must be defined")

    if site_config.output.default_format not in site_config.output.allowed_formats:
        raise ValueError(
            "output.default_format must be included in output.allowed_formats"
        )

    supported_formats = {"csv", "json"}
    unsupported_formats = set(site_config.output.allowed_formats) - supported_formats
    if unsupported_formats:
        raise ValueError(
            f"Unsupported output formats found: {sorted(unsupported_formats)}"
        )

    if not site_config.datetime.timezone:
        raise ValueError("datetime.timezone must not be empty")


def validate_betano_site_config(site_config):
    if site_config.site != "betano":
        raise ValueError(f"Unsupported site value: {site_config.site}")

    validate_site_config_common(site_config)

    for target in site_config.targets:
        if not target.target_id:
            raise ValueError("Each target must have a target_id")

        if not target.sport_id:
            raise ValueError(f"Target {target.name}: sport_id must not be empty")

        if not target.country_id:
            raise ValueError(f"Target {target.name}: country_id must not be empty")

        if not target.league_id:
            raise ValueError(f"Target {target.name}: league_id must not be empty")

        if not target.name:
            raise ValueError("Each target must have a name")

        if not target.sport_slug:
            raise ValueError(f"Target {target.name}: sport_slug must not be empty")

        if not target.country_slug:
            raise ValueError(f"Target {target.name}: country_slug must not be empty")

        if not target.league_slug:
            raise ValueError(f"Target {target.name}: league_slug must not be empty")

        if target.source_league_id <= 0:
            raise ValueError(f"Target {target.name}: source_league_id must be > 0")

        if " " in target.league_slug:
            raise ValueError(f"Target {target.name}: league_slug must not contain spaces")


def validate_betclic_site_config(site_config):
    if site_config.site != "betclic":
        raise ValueError(f"Unsupported site value: {site_config.site}")

    validate_site_config_common(site_config)

    for target in site_config.targets:
        if not target.target_id:
            raise ValueError("Each target must have a target_id")

        if not target.sport_id:
            raise ValueError(f"Target {target.name}: sport_id must not be empty")

        if not target.country_id:
            raise ValueError(f"Target {target.name}: country_id must not be empty")

        if not target.league_id:
            raise ValueError(f"Target {target.name}: league_id must not be empty")

        if not target.name:
            raise ValueError("Each target must have a name")

        if not target.sport_slug:
            raise ValueError(f"Target {target.name}: sport_slug must not be empty")

        if not target.sport_code:
            raise ValueError(f"Target {target.name}: sport_code must not be empty")

        if not target.competition_slug:
            raise ValueError(f"Target {target.name}: competition_slug must not be empty")

        if target.source_league_id <= 0:
            raise ValueError(f"Target {target.name}: source_league_id must be > 0")

        if not target.source_country_name or not target.source_league_name:
            raise ValueError(f"Target {target.name}: source_country_name and source_league_name must not be empty")
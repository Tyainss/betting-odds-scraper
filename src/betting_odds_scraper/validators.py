def validate_betano_site_config(site_config):
    if site_config.site != "betano":
        raise ValueError(f"Unsupported site value: {site_config.site}")

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

    for target in site_config.targets:
        if not target.name:
            raise ValueError("Each target must have a name")

        if not target.sport_slug:
            raise ValueError(f"Target {target.name}: sport_slug must not be empty")

        if not target.country_slug:
            raise ValueError(f"Target {target.name}: country_slug must not be empty")

        if target.region_id <= 0:
            raise ValueError(f"Target {target.name}: region_id must be > 0")

        if target.league_id <= 0:
            raise ValueError(f"Target {target.name}: league_id must be > 0")

        if not target.market:
            raise ValueError(f"Target {target.name}: market must not be empty")
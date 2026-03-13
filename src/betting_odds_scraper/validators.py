def _validate_browser_config(browser_config):
    if browser_config.page_load_timeout_seconds <= 0:
        raise ValueError("browser.page_load_timeout_seconds must be > 0")

    if browser_config.wait_after_load_min_seconds < 0:
        raise ValueError("browser.wait_after_load_min_seconds must be >= 0")

    if browser_config.wait_after_load_max_seconds < browser_config.wait_after_load_min_seconds:
        raise ValueError("browser.wait_after_load_max_seconds must be >= browser.wait_after_load_min_seconds")

    if browser_config.wait_after_overlay_dismiss_min_seconds < 0:
        raise ValueError("browser.wait_after_overlay_dismiss_min_seconds must be >= 0")

    if browser_config.wait_after_overlay_dismiss_max_seconds < browser_config.wait_after_overlay_dismiss_min_seconds:
        raise ValueError("browser.wait_after_overlay_dismiss_max_seconds must be >= browser.wait_after_overlay_dismiss_min_seconds")

    if browser_config.delay_between_targets_min_seconds < 0:
        raise ValueError("browser.delay_between_targets_min_seconds must be >= 0")

    if browser_config.delay_between_targets_max_seconds < browser_config.delay_between_targets_min_seconds:
        raise ValueError("browser.delay_between_targets_max_seconds must be >= browser.delay_between_targets_min_seconds")

    if browser_config.retry_backoff_base_seconds <= 0 or browser_config.retry_backoff_max_seconds <= 0:
        raise ValueError("browser retry backoff values must be > 0")

    if browser_config.driver_lifecycle not in {"per_target", "per_run"}:
        raise ValueError("browser.driver_lifecycle must be 'per_target' or 'per_run'")


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

    _validate_browser_config(site_config.browser)


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


def validate_bwin_site_config(site_config):
    if site_config.site != "bwin":
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

        if target.sport_id_numeric <= 0:
            raise ValueError(f"Target {target.name}: sport_id_numeric must be > 0")

        if not target.region_slug:
            raise ValueError(f"Target {target.name}: region_slug must not be empty")

        if target.region_id_numeric <= 0:
            raise ValueError(f"Target {target.name}: region_id_numeric must be > 0")

        if not target.competition_slug:
            raise ValueError(f"Target {target.name}: competition_slug must not be empty")

        if target.source_league_id <= 0:
            raise ValueError(f"Target {target.name}: source_league_id must be > 0")
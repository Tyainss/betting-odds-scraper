from dataclasses import dataclass
from typing import Any

from betting_odds_scraper.logger import configure_logging
from betting_odds_scraper.cli.registry import get_site_definition


@dataclass(frozen=True)
class ScrapeRunRequest:
    site_name: str
    output_format: str | None
    output_dir: str
    config_path: str | None
    chromedriver_path: str | None
    split_by_target: bool
    target_names: list[str] | None
    headless: bool
    headed: bool
    continue_on_error: bool
    retries: int
    retry_delay_seconds: int
    log_level: str
    log_file: str | None
    write_latest: bool
    append_history: bool


def run_scrape_request(request: ScrapeRunRequest) -> dict[str, Any]:
    site_definition = get_site_definition(request.site_name)
    config_path = request.config_path or site_definition.default_config_path
    headless_override = _resolve_headless_override(
        headless=request.headless,
        headed=request.headed,
    )

    configure_logging(
        log_level=request.log_level,
        log_file_path=request.log_file,
    )

    return site_definition.runner(
        config_path=config_path,
        output_format=request.output_format,
        output_dir=request.output_dir,
        chromedriver_path=request.chromedriver_path,
        split_by_target=request.split_by_target,
        target_names=request.target_names,
        headless_override=headless_override,
        continue_on_error=request.continue_on_error,
        retries=request.retries,
        retry_delay_seconds=request.retry_delay_seconds,
        write_latest=request.write_latest,
        append_history=request.append_history,
    )


def _resolve_headless_override(*, headless: bool, headed: bool) -> bool | None:
    if headless and headed:
        raise ValueError("Use either --headless or --headed, not both")

    if headless:
        return True

    if headed:
        return False

    return None
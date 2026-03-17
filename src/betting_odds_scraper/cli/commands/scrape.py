from typing import Optional

import typer

from betting_odds_scraper.cli.common import emit_scrape_result
from betting_odds_scraper.cli.registry import get_supported_sites
from betting_odds_scraper.cli.service import ScrapeRunRequest, run_scrape_request


scrape_app = typer.Typer(no_args_is_help=True)


def _build_site_command(site_name: str):
    def scrape_site_cmd(
        output_format: Optional[str] = typer.Option(
            None,
            "--output-format",
            help="Output file format: csv or json.",
        ),
        output_dir: str = typer.Option(
            "data/processed",
            "--output-dir",
            help="Directory where outputs are written.",
        ),
        config_path: Optional[str] = typer.Option(
            None,
            "--config-path",
            help="Custom path to the site YAML config.",
        ),
        chromedriver_path: Optional[str] = typer.Option(
            None,
            "--chromedriver-path",
            help="Explicit ChromeDriver path when it is not on PATH.",
        ),
        split_by_target: bool = typer.Option(
            False,
            "--split-by-target",
            help="Write separate output files per target in addition to merged output.",
        ),
        target_names: Optional[list[str]] = typer.Option(
            None,
            "--target",
            help="Target name from config. Repeat to run multiple targets.",
        ),
        headless: bool = typer.Option(
            False,
            "--headless",
            help="Run browser without opening the UI.",
        ),
        headed: bool = typer.Option(
            False,
            "--headed",
            help="Force visible browser window.",
        ),
        continue_on_error: bool = typer.Option(
            True,
            "--continue-on-error/--fail-fast",
            help="Keep running remaining targets if one target fails.",
        ),
        retries: int = typer.Option(
            1,
            "--retries",
            help="Number of retries after the first failed attempt.",
        ),
        retry_delay_seconds: int = typer.Option(
            2,
            "--retry-delay-seconds",
            help="Wait time between retries.",
        ),
        log_level: str = typer.Option(
            "INFO",
            "--log-level",
            help="Logging verbosity.",
        ),
        log_file: Optional[str] = typer.Option(
            None,
            "--log-file",
            help="Save logs to a file.",
        ),
        no_latest: bool = typer.Option(
            False,
            "--no-latest",
            help="Do not write the site latest snapshot file.",
        ),
        append_history: bool = typer.Option(
            False,
            "--append-history",
            help="Append rows to a cumulative site history file.",
        ),
    ) -> None:
        request = ScrapeRunRequest(
            site_name=site_name,
            output_format=output_format,
            output_dir=output_dir,
            config_path=config_path,
            chromedriver_path=chromedriver_path,
            split_by_target=split_by_target,
            target_names=target_names,
            headless=headless,
            headed=headed,
            continue_on_error=continue_on_error,
            retries=retries,
            retry_delay_seconds=retry_delay_seconds,
            log_level=log_level,
            log_file=log_file,
            write_latest=not no_latest,
            append_history=append_history,
        )

        result = run_scrape_request(request)
        emit_scrape_result(result)

    scrape_site_cmd.__name__ = f"scrape_{site_name}_cmd"
    return scrape_site_cmd


for _site_name in get_supported_sites():
    scrape_app.command(name=_site_name)(_build_site_command(_site_name))

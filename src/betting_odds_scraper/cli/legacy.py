import argparse

from betting_odds_scraper.cli.common import emit_scrape_result
from betting_odds_scraper.cli.registry import get_site_definition
from betting_odds_scraper.cli.service import ScrapeRunRequest, run_scrape_request


DEFAULT_OUTPUT_DIR = "data/processed"


def run_legacy_site(site_name: str) -> None:
    site_definition = get_site_definition(site_name)
    args = _parse_args(default_config_path=site_definition.default_config_path)

    print(
        f"\n[deprecated] This legacy script entrypoint is still supported, "
        f"but please migrate to: 'uv run odds scrape {site_name} ...'\n"
    )

    request = ScrapeRunRequest(
        site_name=site_name,
        output_format=args.output_format,
        output_dir=args.output_dir,
        config_path=args.config_path,
        chromedriver_path=args.chromedriver_path,
        split_by_target=args.split_by_target,
        target_names=args.targets,
        headless=args.headless,
        headed=args.headed,
        continue_on_error=args.continue_on_error,
        retries=args.retries,
        retry_delay_seconds=args.retry_delay_seconds,
        log_level=args.log_level,
        log_file=args.log_file,
        write_latest=not args.no_latest,
        append_history=args.append_history,
    )

    result = run_scrape_request(request)
    emit_scrape_result(result)


def _parse_args(*, default_config_path: str) -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--output-format",
        choices=["csv", "json"],
        default=None,
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
    )
    parser.add_argument(
        "--config-path",
        default=default_config_path,
    )
    parser.add_argument(
        "--chromedriver-path",
        default=None,
    )
    parser.add_argument(
        "--split-by-target",
        action="store_true",
    )
    parser.add_argument(
        "--target",
        action="append",
        dest="targets",
        default=None,
        help="Target name from config. Repeat to run multiple targets.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--retry-delay-seconds",
        type=int,
        default=2,
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
    )
    parser.add_argument(
        "--log-file",
        default=None,
    )
    parser.add_argument(
        "--no-latest",
        action="store_true",
        help="Do not write the site latest snapshot file.",
    )
    parser.add_argument(
        "--append-history",
        action="store_true",
        help="Append rows to a cumulative site history file.",
    )

    return parser.parse_args()
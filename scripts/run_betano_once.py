import argparse

from betting_odds_scraper.logger import configure_logging
from betting_odds_scraper.pipelines.scrape_betano import run_betano_scrape


DEFAULT_CONFIG_PATH = "configs/sites/betano.yaml"
DEFAULT_CHROMEDRIVER_PATH = None


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-format",
        choices=["csv", "json"],
        default=None,
    )
    parser.add_argument(
        "--output-dir",
        default="data/processed",
    )
    parser.add_argument(
        "--config-path",
        default=DEFAULT_CONFIG_PATH,
    )
    parser.add_argument(
        "--chromedriver-path",
        default=DEFAULT_CHROMEDRIVER_PATH,
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


def main():
    args = parse_args()
    headless_override = None

    if args.headless and args.headed:
        raise ValueError("Use either --headless or --headed, not both")

    if args.headless:
        headless_override = True
    elif args.headed:
        headless_override = False

    configure_logging(
        log_level=args.log_level,
        log_file_path=args.log_file,
    )

    result = run_betano_scrape(
        config_path=args.config_path,
        output_format=args.output_format,
        output_dir=args.output_dir,
        chromedriver_path=args.chromedriver_path,
        split_by_target=args.split_by_target,
        target_names=args.targets,
        headless_override=headless_override,
        continue_on_error=args.continue_on_error,
        retries=args.retries,
        retry_delay_seconds=args.retry_delay_seconds,
        write_latest=not args.no_latest,
        append_history=args.append_history,
    )

    print(f"Rows scraped: {len(result['rows'])}")
    print(f"Saved merged output to: {result['merged_output_path']}")
    if result["latest_output_path"]:
        print(f"Saved latest output to: {result['latest_output_path']}")
    if result["history_output_path"]:
        print(f"Appended history output to: {result['history_output_path']}")

    if result["target_output_paths"]:
        print("Saved target outputs to:")
        for path in result["target_output_paths"]:
            print(f" - {path}")

    if result["failed_targets"]:
        print("Failed targets:")
        for target_name in result["failed_targets"]:
            print(f" - {target_name}")


if __name__ == "__main__":
    main()
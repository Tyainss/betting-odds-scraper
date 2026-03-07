import argparse

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
    return parser.parse_args()


def main():
    args = parse_args()

    result = run_betano_scrape(
        config_path=args.config_path,
        output_format=args.output_format,
        output_dir=args.output_dir,
        chromedriver_path=args.chromedriver_path,
        split_by_target=args.split_by_target,
        target_names=args.targets,
    )

    print(f"Rows scraped: {len(result['rows'])}")
    print(f"Saved merged output to: {result['merged_output_path']}")

    if result["target_output_paths"]:
        print("Saved target outputs to:")
        for path in result["target_output_paths"]:
            print(f" - {path}")


if __name__ == "__main__":
    main()
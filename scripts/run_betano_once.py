import argparse

from betting_odds_scraper.pipelines.scrape_betano import run_betano_scrape


CONFIG_PATH = "configs/sites/betano.yaml"
CHROMEDRIVER_PATH = None


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
    return parser.parse_args()


def main():
    args = parse_args()

    output_path, rows = run_betano_scrape(
        config_path=CONFIG_PATH,
        output_format=args.output_format,
        output_dir=args.output_dir,
        chromedriver_path=CHROMEDRIVER_PATH,
    )

    print(f"Rows scraped: {len(rows)}")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()
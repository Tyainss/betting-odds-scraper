# Betting Odds Scraper

A Python project for scraping football betting odds from multiple bookmakers in a clean, config-driven way.

Currently supported:

* Betano
* Betclic
* Bwin

## What it does

* Scrapes pre-match 1X2 odds from configured league pages
* Uses Selenium to load bookmaker pages when direct requests are not reliable
* Keeps site-specific scraping logic isolated per bookmaker
* Normalizes results into a shared output schema
* Writes timestamped snapshots, plus optional latest/history outputs

## Project structure

```text
betting-odds-scraper/
├── configs/
│   └── sites/
├── scripts/
├── src/
│   └── betting_odds_scraper/
│       ├── browser/
│       ├── pipelines/
│       ├── scrapers/
│       │   ├── betano/
│       │   ├── betclic/
│       │   └── bwin/
│       ├── storage/
│       ├── config.py
│       ├── logger.py
│       ├── models.py
│       └── validators.py
└── tests/
```

## How it works

The scraper is split into shared and site-specific parts.

Shared:

* config loading
* validation
* browser setup
* scrape pipeline / retries
* output writing

Site-specific:

* URL building
* overlay dismissal
* page readiness checks
* parsing bookmaker page data

### Current site strategies

**Betano**

* loads the league page with Selenium
* reads `driver.page_source`
* extracts `window["initial_state"]`
* parses structured event / market / selection data

**Betclic**

* loads the league page with Selenium
* reads `driver.page_source`
* extracts the Angular `ng-state` payload
* parses structured match / market data

**Bwin**

* loads the league page with Selenium
* fetches the competition `widgetdata` payload from inside the browser context
* parses structured fixture / market / option data from the returned JSON

## Installation

### Requirements

Before running the scraper, make sure you have:

* Python 3.11 or newer
* `uv` installed
* Google Chrome installed

### 1. Install Python

Check that Python is installed:

```bash
python --version
```

If Python is not installed yet, install Python 3.11 or newer first.

### 2. Install `uv`

Recommended installation methods:

**Windows (PowerShell):**

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS / Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Alternative:

```bash
pip install uv
```

Then confirm it worked:

```bash
uv --version
```

### 3. Install Google Chrome

Make sure Google Chrome is installed on your machine.

Note on ChromeDriver:

* in most cases, you do **not** need to install ChromeDriver manually
* Selenium will usually resolve it automatically
* if that fails in your environment, you can pass a manual path with `--chromedriver-path`

### 4. Clone the repository

```bash
git clone <repo-url>
cd betting-odds-scraper
```

### 5. Install dependencies

```bash
uv sync
```

This creates the project virtual environment and installs the project dependencies.

## Getting started

For most users, these are the only commands you need:

```bash
uv sync
uv run python scripts/run_betano_once.py --target primeira_liga
```

After `uv sync`, run project commands with `uv run ...`.

### 1. Run a simple scrape

Betano:

```bash
uv run python scripts/run_betano_once.py --target primeira_liga
```

Betclic:

```bash
uv run python scripts/run_betclic_once.py --target laliga
```

Bwin:

```bash
uv run python scripts/run_bwin_once.py --target primeira_liga
```

### 2. If ChromeDriver is not found automatically

Usually, having Google Chrome installed is enough.

Selenium will often handle the browser driver automatically. If that does not work in your environment, run the same command with an explicit driver path:

```bash
uv run python scripts/run_betano_once.py --chromedriver-path "C:/path/to/chromedriver.exe"
```

### 3. Where outputs are written

By default, files are written to:

```text
data/processed/
```

That is enough to get started. No extra virtual environment activation step is required.

## Configuration

Each bookmaker has its own YAML config under `configs/sites/`.

Targets use two layers:

* `canonical`: internal IDs used across all sites
* `site_data`: bookmaker-specific scraping inputs

Example:

```yaml
site: betclic
base_url: "https://www.betclic.pt"

browser:
  headless: false
  language: "pt-PT"
  page_load_timeout_seconds: 60
  wait_after_load_seconds: 8
  wait_after_overlay_dismiss_seconds: 2

output:
  default_format: "csv"
  allowed_formats:
    - "csv"
    - "json"

datetime:
  timezone: "UTC"

targets:
  - name: "laliga"
    canonical:
      target_id: "laliga"
      sport_id: "football"
      country_id: "spain"
      league_id: "laliga"
    site_data:
      sport_slug: "futebol"
      sport_code: "football"
      competition_slug: "espanha-la-liga"
      source_league_id: 7
```

## Output schema

Rows are normalized across sites.

Main fields:

* `site`
* `sport_id`
* `country_id`
* `league_id`
* `target_id`
* `source_url`
* `scraped_at`
* `live`
* `match_date`
* `match_time`
* `fixture_date`
* `home_team`
* `away_team`
* `odd_1`
* `odd_x`
* `odd_2`
* `source_sport`
* `source_country`
* `source_league`
* `source_target_name`
* `source_league_id`

Notes:

* canonical `*_id` fields are the stable internal identifiers for cross-site analysis
* `source_*` fields preserve bookmaker-specific traceability
* `source_league_id` is the bookmaker competition/league identifier

## Running

Run Betano:

```bash
uv run python scripts/run_betano_once.py
```

Run Betclic:

```bash
uv run python scripts/run_betclic_once.py
```

Run Bwin:

```bash
uv run python scripts/run_bwin_once.py
```

Run a specific target:

```bash
uv run python scripts/run_betano_once.py --target primeira_liga
uv run python scripts/run_betclic_once.py --target laliga
uv run python scripts/run_bwin_once.py --target primeira_liga
```

Useful options:

```bash
--output-format csv|json
--output-dir data/processed
--config-path configs/sites/<site>.yaml
--chromedriver-path /path/to/chromedriver
--target <target_name>
--headless
--headed
--split-by-target
--continue-on-error
--retries 1
--retry-delay-seconds 2
--log-level INFO
--log-file scraper.log
--no-latest
--append-history
```

Brief description:

* `--output-format`: choose output file format
* `--output-dir`: directory where outputs are written
* `--config-path`: custom path to the site YAML config
* `--chromedriver-path`: explicit ChromeDriver path when it is not on PATH
* `--target`: run only selected target names; repeat to run multiple targets
* `--headless`: run browser without opening the UI
* `--headed`: force visible browser window
* `--split-by-target`: write separate output files per target in addition to merged output
* `--continue-on-error`: keep running remaining targets if one target fails
* `--retries`: number of retries after the first failed attempt
* `--retry-delay-seconds`: wait time between retries
* `--log-level`: logging verbosity
* `--log-file`: save logs to a file
* `--no-latest`: skip writing the latest snapshot file
* `--append-history`: append rows to the cumulative history file

## Outputs

The pipeline supports:

* timestamped run outputs
* latest site snapshot
* optional cumulative history file
* optional per-target outputs

Design intent:

* timestamped outputs are the source of truth
* latest is convenience
* history is optional and may contain duplicates across runs

## Adding a new bookmaker

To add another site cleanly:

1. create a new scraper package under `src/betting_odds_scraper/scrapers/<site>/`
2. add site-specific:

   * `scraper.py`
   * `parser.py`
   * `url_builder.py`
   * `selectors.py` if needed
3. add a site config YAML under `configs/sites/`
4. add a pipeline entrypoint under `pipelines/`
5. add tests for parser / validation behavior

Keep shared orchestration generic. Keep bookmaker-specific scraping logic isolated.

## Current scope

This project currently focuses on:

* football
* league-level manual target lists
* 1X2 odds
* pre-match first, with live included when naturally present on the loaded page

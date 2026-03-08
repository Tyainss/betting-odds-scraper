# betting-odds-scraper

Generic betting odds scraping project with site-specific scraper modules.

## Current status

Initial support is implemented for:

* Betano

Current Betano strategy:

* use Selenium to load league pages
* extract structured data from `window["initial_state"]` in the loaded page source
* normalize results into a shared output schema
* save timestamped outputs and a site-level latest snapshot

---

## Design principles

* Generic repo, site-specific scraper modules
* Config-driven scrape targets
* Clear separation between:

  * browser interaction
  * scraping
  * parsing
  * storage
  * pipeline/orchestration
* Prefer robust, maintainable approaches over brittle DOM scraping when possible

---

## Project structure

```text
betting-odds-scraper/
├─ configs/
│  └─ sites/
│     └─ betano.yaml
├─ data/
│  ├─ processed/
│  └─ raw/
├─ scripts/
│  └─ run_betano_once.py
├─ src/
│  └─ betting_odds_scraper/
│     ├─ browser/
│     ├─ pipelines/
│     ├─ scrapers/
│     │  └─ betano/
│     ├─ storage/
│     ├─ config.py
│     ├─ logger.py
│     ├─ models.py
│     └─ validators.py
└─ tests/
```

---

## Requirements

* Python 3.11+
* [uv](https://docs.astral.sh/uv/)
* Google Chrome installed
* ChromeDriver available through Selenium/Chrome setup in your environment

---

## Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd betting-odds-scraper
```

### 2. Initialize and sync the environment

```bash
uv sync
```

This installs:

* runtime dependencies
* dev dependencies
* the editable local package

### 3. Run tests

```bash
uv run pytest -q
```

---

## Configuration

Betano targets are defined in:

```text
configs/sites/betano.yaml
```

Example:

```yaml
site: betano
base_url: "https://www.betano.pt"

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
  - name: "primeira_liga"
    sport_slug: "futebol"
    country_slug: "portugal"
    league_slug: "primeira-liga"
    league_id: 17083

  - name: "laliga"
    sport_slug: "futebol"
    country_slug: "espanha"
    league_slug: "laliga"
    league_id: 5
```

### Target fields

Each target defines one league page to scrape.

* `name`: internal target name
* `sport_slug`: Betano sport path segment
* `country_slug`: Betano country path segment
* `league_slug`: Betano league path segment
* `league_id`: Betano league ID

These are used to build URLs like:

```text
https://www.betano.pt/sport/futebol/portugal/primeira-liga/17083/
https://www.betano.pt/sport/futebol/espanha/laliga/5/
```

---

## How it works

For each configured Betano target, the scraper:

1. opens a fresh browser session
2. loads the target league page
3. waits for the page to contain `window["initial_state"]`
4. dismisses cookie and overlay banners if needed
5. extracts structured event data from the page source
6. parses match result odds (`1`, `X`, `2`)
7. normalizes the output rows
8. writes results to disk

A fresh browser session is used per target because reusing the same session across Betano targets can trigger anti-bot and security blocks.

---

## Output schema

Current normalized output includes:

* `site`
* `country`
* `league`
* `target_name`
* `league_id`
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

### Notes

* `scraped_at` is UTC
* `fixture_date` is a full ISO datetime in UTC
* `match_date` and `match_time` are derived from the event start time
* live matches may still include fixture timing if Betano exposes it in structured data

---

## Usage

### Default run

Runs all configured Betano targets and writes:

* one timestamped merged file
* one site-level latest snapshot

```bash
uv run python scripts/run_betano_once.py
```

### Choose output format

```bash
uv run python scripts/run_betano_once.py --output-format json
```

### Run only specific targets

```bash
uv run python scripts/run_betano_once.py --target primeira_liga
```

Multiple targets:

```bash
uv run python scripts/run_betano_once.py --target primeira_liga --target laliga
```

### Save outputs to a custom directory

```bash
uv run python scripts/run_betano_once.py --output-dir data/processed/betano
```

### Write one file per target as well

```bash
uv run python scripts/run_betano_once.py --split-by-target
```

### Disable latest snapshot output

```bash
uv run python scripts/run_betano_once.py --no-latest
```

### Append to a cumulative history file

```bash
uv run python scripts/run_betano_once.py --append-history
```

This appends rows to a site-level history file, for example:

```text
data/processed/history/betano_history.csv
```

### Run headless

```bash
uv run python scripts/run_betano_once.py --headless
```

### Force headed mode

```bash
uv run python scripts/run_betano_once.py --headed
```

### Continue if one target fails

```bash
uv run python scripts/run_betano_once.py --continue-on-error
```

### Configure retries

```bash
uv run python scripts/run_betano_once.py --retries 2 --retry-delay-seconds 3
```

### Save logs to file

```bash
uv run python scripts/run_betano_once.py --log-file data/logs/betano.log
```

### Use a custom config file

```bash
uv run python scripts/run_betano_once.py --config-path configs/sites/betano.yaml
```

### Use a custom ChromeDriver path

```bash
uv run python scripts/run_betano_once.py --chromedriver-path "C:/path/to/chromedriver.exe"
```

---

## Output files

By default, runs create:

### Historical timestamped output

Example:

```text
data/processed/betano_20260307T205455Z.csv
```

This is the source of truth for run history.

### Latest site snapshot

Example:

```text
data/processed/latest/betano_latest.csv
```

This is overwritten on each run and is meant for convenience.

### Optional cumulative history file

If `--append-history` is used:

```text
data/processed/history/betano_history.csv
```

This appends rows from each run into one growing site-level history file.

Note:

* this is a convenience output
* duplicates are expected if you scrape the same leagues multiple times
* timestamped files remain the primary source of truth

### Optional per-target files

If `--split-by-target` is used:

```text
data/processed/betano_primeira_liga_20260307T205455Z.csv
data/processed/betano_laliga_20260307T205455Z.csv
```

---

## Debug artifacts

When scraping or parsing fails, the scraper may save debug artifacts to help investigation, such as:

* page screenshot
* page source HTML

These are stored under a raw/debug-style directory used by the scraper logic.

---

## Testing

Run all tests:

```bash
uv run pytest -q
```

Current test coverage includes:

* Betano parser logic
* config validation
* storage writers

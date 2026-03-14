import csv
import json

from betting_odds_scraper.storage.csv_writer import (
    append_rows_to_csv,
    write_rows_to_csv,
)
from betting_odds_scraper.storage.json_writer import (
    append_rows_to_json,
    write_rows_to_json,
)


def test_write_rows_to_csv(tmp_path):
    rows = [
        {
            "site": "betano",
            "league_id": "primeira_liga",
            "home_team": "SC Braga",
            "away_team": "Sporting CP",
            "odd_1": 3.7,
            "odd_x": 3.45,
            "odd_2": 2.05,
        }
    ]

    output_path = tmp_path / "rows.csv"
    write_rows_to_csv(rows, output_path)

    with output_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        loaded_rows = list(reader)

    assert len(loaded_rows) == 1
    assert loaded_rows[0]["site"] == "betano"
    assert loaded_rows[0]["league_id"] == "primeira_liga"
    assert loaded_rows[0]["home_team"] == "SC Braga"


def test_write_rows_to_json(tmp_path):
    rows = [
        {
            "site": "betano",
            "league_id": "primeira_liga",
            "home_team": "SC Braga",
            "away_team": "Sporting CP",
            "odd_1": 3.7,
            "odd_x": 3.45,
            "odd_2": 2.05,
        }
    ]

    output_path = tmp_path / "rows.json"
    write_rows_to_json(rows, output_path)

    with output_path.open("r", encoding="utf-8") as file:
        loaded_rows = json.load(file)

    assert len(loaded_rows) == 1
    assert loaded_rows[0]["site"] == "betano"
    assert loaded_rows[0]["league_id"] == "primeira_liga"
    assert loaded_rows[0]["home_team"] == "SC Braga"


def test_write_rows_to_csv_with_empty_rows_creates_no_file(tmp_path):
    output_path = tmp_path / "empty.csv"
    write_rows_to_csv([], output_path)

    assert output_path.exists() is False


def test_write_rows_to_json_with_empty_rows_creates_file(tmp_path):
    output_path = tmp_path / "empty.json"
    write_rows_to_json([], output_path)
    assert output_path.exists() is True



def test_append_rows_to_csv_appends_without_rewriting_header(tmp_path):
    output_path = tmp_path / "history.csv"

    rows_1 = [
        {"site": "betano", "league_id": "primeira_liga", "home_team": "A"}
    ]
    rows_2 = [
        {"site": "betano", "league_id": "laliga", "home_team": "B"}
    ]

    append_rows_to_csv(rows_1, output_path)
    append_rows_to_csv(rows_2, output_path)

    with output_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        loaded_rows = list(reader)

    assert len(loaded_rows) == 2
    assert loaded_rows[0]["league_id"] == "primeira_liga"
    assert loaded_rows[1]["league_id"] == "laliga"


def test_append_rows_to_json_appends_to_existing_list(tmp_path):
    output_path = tmp_path / "history.json"

    rows_1 = [
        {"site": "betano", "league_id": "primeira_liga", "home_team": "A"}
    ]
    rows_2 = [
        {"site": "betano", "league_id": "laliga", "home_team": "B"}
    ]

    append_rows_to_json(rows_1, output_path)
    append_rows_to_json(rows_2, output_path)

    with output_path.open("r", encoding="utf-8") as file:
        loaded_rows = json.load(file)

    assert len(loaded_rows) == 2
    assert loaded_rows[0]["league_id"] == "primeira_liga"
    assert loaded_rows[1]["league_id"] == "laliga"
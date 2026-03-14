import json
from pathlib import Path


def write_rows_to_json(rows, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(rows, file, ensure_ascii=False, indent=2)


def append_rows_to_json(rows, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        return

    existing_rows = []

    if output_path.exists():
        with output_path.open("r", encoding="utf-8") as file:
            content = file.read().strip()
            if content:
                existing_rows = json.loads(content)

        if not isinstance(existing_rows, list):
            raise ValueError(
                f"Cannot append to non-list JSON history file: {output_path}"
            )

    existing_rows.extend(rows)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(existing_rows, file, ensure_ascii=False, indent=2)

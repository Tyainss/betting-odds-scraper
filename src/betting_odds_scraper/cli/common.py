from typing import Any


def emit_scrape_result(result: dict[str, Any]) -> None:
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
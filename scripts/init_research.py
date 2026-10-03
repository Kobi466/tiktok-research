"""Workspace initialization for TikTok affiliate research."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.research_io import (
    load_definitions,
    processed_csv_path,
    table_fields,
    write_csv_records,
)

_TARGET_DIRECTORIES = ("data/raw", "data/processed", "reports")


def _get_definitions(root: Path) -> dict:
    """Load canonical definitions from workspace or fallback to project root."""
    workspace_config = Path(root) / "config" / "field-definitions.json"
    if workspace_config.is_file():
        return load_definitions(root)
    return load_definitions(_PROJECT_ROOT)


def initialize_workspace(root: Path, force: bool = False) -> list[Path]:
    """Initialize research directories, .gitkeep markers, and canonical empty CSVs."""
    target_root = Path(root).expanduser().resolve()
    target_root.mkdir(parents=True, exist_ok=True)

    # 1. Create expected directory structure with .gitkeep markers if absent
    for rel_dir in _TARGET_DIRECTORIES:
        directory = target_root / rel_dir
        directory.mkdir(parents=True, exist_ok=True)
        gitkeep = directory / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.touch()

    # 2. Inspect canonical tables and their CSV paths
    definitions = _get_definitions(target_root)
    created_paths: list[Path] = []

    for table_name in definitions["tables"]:
        csv_path = processed_csv_path(target_root, table_name)
        fields = table_fields(definitions, table_name)

        if csv_path.exists():
            if csv_path.is_dir():
                raise FileExistsError(f"Target table path is an existing directory: {csv_path}")

            with csv_path.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.reader(handle)
                rows = [row for row in reader if any(cell.strip() for cell in row)]

            if len(rows) == 0:
                # 0 non-empty rows (empty file)
                write_csv_records(csv_path, fields, [])
                created_paths.append(csv_path)
            elif rows == [fields]:
                # Exact generated header only (no data rows)
                if force:
                    write_csv_records(csv_path, fields, [])
                    created_paths.append(csv_path)
            else:
                # Contains data rows or mismatched/non-header records
                raise FileExistsError(
                    f"Table file '{csv_path}' already exists and contains non-header records. "
                    "Initialization will not overwrite or delete existing records."
                )
        else:
            write_csv_records(csv_path, fields, [])
            created_paths.append(csv_path)

    return created_paths


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for research workspace initialization."""
    parser = argparse.ArgumentParser(
        description="Initialize TikTok research workspace directories and canonical schema CSVs."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Target workspace root path (default: current directory).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Recreate headers on empty CSV files without touching files with data rows.",
    )

    args = parser.parse_args(argv)
    target_root = args.root.expanduser().resolve()

    try:
        created = initialize_workspace(target_root, force=args.force)
    except FileExistsError as err:
        sys.stderr.write(f"Initialization error: {err}\n")
        return 1
    except Exception as err:
        sys.stderr.write(f"Unexpected error: {err}\n")
        return 2

    # Print summary of created and skipped paths without printing file contents
    print(f"Workspace root: {target_root}")
    print(f"Created files ({len(created)}):")
    for path in created:
        print(f"  + {path.relative_to(target_root) if path.is_relative_to(target_root) else path}")

    definitions = _get_definitions(target_root)
    all_table_paths = [processed_csv_path(target_root, name) for name in definitions["tables"]]
    skipped = [path for path in all_table_paths if path not in created]
    if skipped:
        print(f"Skipped existing empty files ({len(skipped)}):")
        for path in skipped:
            print(f"  - {path.relative_to(target_root) if path.is_relative_to(target_root) else path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

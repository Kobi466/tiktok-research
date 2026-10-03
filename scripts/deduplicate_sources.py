"""Non-destructive duplicate detection for TikTok affiliate research sources."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.research_io import (
    processed_csv_path,
    read_csv_records,
    write_json,
)


def find_source_duplicates(records: list[dict[str, str]]) -> list[dict[str, Any]]:
    """Scan records for duplicate non-empty source_ids and exact URLs.

    Performs non-destructive grouping without altering or deleting records,
    and without normalizing away query strings, fragments, or path details.
    """
    id_map: dict[str, list[dict[str, str]]] = {}
    url_map: dict[str, list[dict[str, str]]] = {}

    for record in records:
        source_id = str(record.get("source_id", "") or "").strip()
        url = str(record.get("url", "") or "").strip()

        if source_id:
            id_map.setdefault(source_id, []).append(record)

        if url:
            url_map.setdefault(url, []).append(record)

    duplicates: list[dict[str, Any]] = []

    for sid, matched in id_map.items():
        if len(matched) > 1:
            duplicates.append(
                {
                    "kind": "id",
                    "value": sid,
                    "record_ids": [str(r.get("source_id", "") or "").strip() for r in matched],
                    "count": len(matched),
                }
            )

    for url_val, matched in url_map.items():
        if len(matched) > 1:
            duplicates.append(
                {
                    "kind": "url",
                    "value": url_val,
                    "record_ids": [str(r.get("source_id", "") or "").strip() for r in matched],
                    "count": len(matched),
                }
            )

    duplicates.sort(key=lambda item: (item["kind"], item["value"]))
    return duplicates


def audit_duplicates(root: Path) -> dict[str, Any]:
    """Audit duplicate sources in data/processed/sources.csv non-destructively.

    If sources.csv is missing or empty, returns zero counts and an empty duplicates list.
    Never modifies sources.csv or any data files.
    """
    resolved_root = Path(root).expanduser().resolve()
    sources_path = processed_csv_path(resolved_root, "sources")

    if not sources_path.exists() or not sources_path.is_file() or sources_path.stat().st_size == 0:
        return {
            "summary": {
                "total_records": 0,
                "duplicate_groups": 0,
                "duplicate_id_groups": 0,
                "duplicate_url_groups": 0,
                "affected_records": 0,
            },
            "duplicates": [],
        }

    records = read_csv_records(sources_path)
    if not records:
        return {
            "summary": {
                "total_records": 0,
                "duplicate_groups": 0,
                "duplicate_id_groups": 0,
                "duplicate_url_groups": 0,
                "affected_records": 0,
            },
            "duplicates": [],
        }

    duplicates = find_source_duplicates(records)
    duplicate_id_groups = sum(1 for d in duplicates if d["kind"] == "id")
    duplicate_url_groups = sum(1 for d in duplicates if d["kind"] == "url")
    affected_ids = {rid for d in duplicates for rid in d["record_ids"] if rid}

    return {
        "summary": {
            "total_records": len(records),
            "duplicate_groups": len(duplicates),
            "duplicate_id_groups": duplicate_id_groups,
            "duplicate_url_groups": duplicate_url_groups,
            "affected_records": len(affected_ids),
        },
        "duplicates": duplicates,
    }


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for non-destructive duplicate source auditing."""
    parser = argparse.ArgumentParser(
        description="Audit duplicate source IDs and URLs in research sources without modifying data."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Target workspace root path (default: current directory).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to output JSON duplicate audit report.",
    )

    args = parser.parse_args(argv)
    target_root = args.root.expanduser().resolve()

    if not target_root.exists() or not target_root.is_dir():
        sys.stderr.write(
            f"Duplicate audit invocation error: root does not exist or is not a directory: {target_root}\n"
        )
        return 2

    try:
        report = audit_duplicates(target_root)
    except Exception as err:
        sys.stderr.write(f"Duplicate audit runtime error: {err}\n")
        return 2

    if args.output is not None:
        try:
            write_json(args.output, report)
        except Exception as err:
            sys.stderr.write(f"Failed to write duplicate report to {args.output}: {err}\n")
            return 2
    else:
        print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    sys.exit(main())

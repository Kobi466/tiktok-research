"""Unit tests for non-destructive duplicate detection in research sources."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON_BIN = sys.executable

from scripts.deduplicate_sources import (
    audit_duplicates,
    find_source_duplicates,
    main,
)
from scripts.research_io import (
    load_definitions,
    table_fields,
    write_csv_records,
    write_json,
)


def sample_source(**kwargs: str) -> dict[str, str]:
    record = {
        "source_id": "SRC-001",
        "url": "https://example.com/item1",
        "title": "Item 1",
        "publisher": "Example Publisher",
        "source_type": "article",
        "accessed_at": "2026-10-02T10:00:00Z",
        "published_at": "2026-10-01T10:00:00Z",
        "access_status": "accessible",
        "collection_method": "web_fetch",
        "content_hash": "hash1",
        "limitations": "",
        "notes": "",
    }
    record.update(kwargs)
    return record


class TestDeduplicateSources(unittest.TestCase):
    def setUp(self) -> None:
        self.definitions = load_definitions(ROOT)
        self.source_fields = table_fields(self.definitions, "sources")

    def test_duplicate_ids_are_reported(self) -> None:
        records = [
            sample_source(source_id="SRC-001", url="https://example.com/one"),
            sample_source(source_id="SRC-002", url="https://example.com/two"),
            sample_source(source_id="SRC-001", url="https://example.com/three"),
            sample_source(source_id="SRC-003", url="https://example.com/four"),
            sample_source(source_id="SRC-002", url="https://example.com/five"),
            sample_source(source_id="SRC-002", url="https://example.com/six"),
        ]

        duplicates = find_source_duplicates(records)
        id_duplicates = [d for d in duplicates if d["kind"] == "id"]

        self.assertEqual(len(id_duplicates), 2)

        # Sorted by kind, then value -> SRC-001 comes before SRC-002
        self.assertEqual(id_duplicates[0]["value"], "SRC-001")
        self.assertEqual(id_duplicates[0]["count"], 2)
        self.assertEqual(id_duplicates[0]["record_ids"], ["SRC-001", "SRC-001"])

        self.assertEqual(id_duplicates[1]["value"], "SRC-002")
        self.assertEqual(id_duplicates[1]["count"], 3)
        self.assertEqual(id_duplicates[1]["record_ids"], ["SRC-002", "SRC-002", "SRC-002"])

        # SRC-003 is unique and must not be in id_duplicates
        reported_ids = {d["value"] for d in id_duplicates}
        self.assertNotIn("SRC-003", reported_ids)

    def test_duplicate_urls_are_reported_without_normalizing_away_evidence(self) -> None:
        exact_url_1 = "https://www.tiktok.com/@creator/video/12345?is_from_webapp=1&sender_device=pc#t=10"
        exact_url_2 = "https://www.tiktok.com/@creator/video/12345?is_from_webapp=1&sender_device=pc"
        exact_url_3 = "https://www.tiktok.com/@creator/video/12345"

        records = [
            sample_source(source_id="SRC-001", url=exact_url_1),
            sample_source(source_id="SRC-002", url=exact_url_2),
            sample_source(source_id="SRC-003", url=exact_url_1),
            sample_source(source_id="SRC-004", url=exact_url_3),
            sample_source(source_id="SRC-005", url=exact_url_1),
        ]

        duplicates = find_source_duplicates(records)
        url_duplicates = [d for d in duplicates if d["kind"] == "url"]

        self.assertEqual(len(url_duplicates), 1)
        group = url_duplicates[0]
        self.assertEqual(group["kind"], "url")
        self.assertEqual(group["value"], exact_url_1)
        self.assertEqual(group["count"], 3)
        self.assertEqual(group["record_ids"], ["SRC-001", "SRC-003", "SRC-005"])

    def test_audit_does_not_modify_csv(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            sources_path = root / "data" / "processed" / "sources.csv"

            records = [
                sample_source(source_id="SRC-001", url="https://example.com/dupe"),
                sample_source(source_id="SRC-002", url="https://example.com/dupe"),
                sample_source(source_id="SRC-001", url="https://example.com/unique"),
            ]
            write_csv_records(sources_path, self.source_fields, records)

            content_before = sources_path.read_bytes()
            stat_before = sources_path.stat()

            report = audit_duplicates(root)

            content_after = sources_path.read_bytes()
            stat_after = sources_path.stat()

            self.assertEqual(content_before, content_after)
            self.assertEqual(stat_before.st_size, stat_after.st_size)
            self.assertEqual(report["summary"]["total_records"], 3)
            self.assertEqual(report["summary"]["duplicate_groups"], 2)

    def test_empty_or_clean_sources_reports_zero_duplicates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            # Case A: Missing sources.csv file
            report_missing = audit_duplicates(root)
            self.assertEqual(
                report_missing,
                {
                    "summary": {
                        "total_records": 0,
                        "duplicate_groups": 0,
                        "duplicate_id_groups": 0,
                        "duplicate_url_groups": 0,
                        "affected_records": 0,
                    },
                    "duplicates": [],
                },
            )

            # Case B: Empty sources.csv file (0 bytes)
            sources_path = root / "data" / "processed" / "sources.csv"
            sources_path.parent.mkdir(parents=True, exist_ok=True)
            sources_path.write_text("", encoding="utf-8")

            report_empty = audit_duplicates(root)
            self.assertEqual(
                report_empty,
                {
                    "summary": {
                        "total_records": 0,
                        "duplicate_groups": 0,
                        "duplicate_id_groups": 0,
                        "duplicate_url_groups": 0,
                        "affected_records": 0,
                    },
                    "duplicates": [],
                },
            )

            # Case C: Clean sources.csv with unique records
            clean_records = [
                sample_source(source_id="SRC-001", url="https://example.com/clean1"),
                sample_source(source_id="SRC-002", url="https://example.com/clean2"),
                sample_source(source_id="SRC-003", url="https://example.com/clean3"),
            ]
            write_csv_records(sources_path, self.source_fields, clean_records)

            report_clean = audit_duplicates(root)
            self.assertEqual(report_clean["summary"]["total_records"], 3)
            self.assertEqual(report_clean["summary"]["duplicate_groups"], 0)
            self.assertEqual(report_clean["summary"]["duplicate_id_groups"], 0)
            self.assertEqual(report_clean["summary"]["duplicate_url_groups"], 0)
            self.assertEqual(report_clean["summary"]["affected_records"], 0)
            self.assertEqual(report_clean["duplicates"], [])

    def test_cli_invocation_stdout_and_output_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            sources_path = root / "data" / "processed" / "sources.csv"
            records = [
                sample_source(source_id="SRC-001", url="https://example.com/dupe"),
                sample_source(source_id="SRC-002", url="https://example.com/dupe"),
            ]
            write_csv_records(sources_path, self.source_fields, records)

            script_path = ROOT / "scripts" / "deduplicate_sources.py"
            out_file = root / "out_report.json"

            # 1. Output file flag
            proc_file = subprocess.run(
                [PYTHON_BIN, str(script_path), "--root", str(root), "--output", str(out_file)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc_file.returncode, 0)
            self.assertTrue(out_file.is_file())
            data_file = json.loads(out_file.read_text(encoding="utf-8"))
            self.assertEqual(data_file["summary"]["total_records"], 2)
            self.assertEqual(data_file["summary"]["duplicate_groups"], 1)
            self.assertEqual(data_file["summary"]["duplicate_url_groups"], 1)
            self.assertEqual(data_file["summary"]["affected_records"], 2)

            # 2. Stdout (no --output flag)
            proc_stdout = subprocess.run(
                [PYTHON_BIN, str(script_path), "--root", str(root)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc_stdout.returncode, 0)
            data_stdout = json.loads(proc_stdout.stdout)
            self.assertEqual(data_stdout["summary"]["total_records"], 2)
            self.assertEqual(data_stdout["summary"]["duplicate_groups"], 1)

            # 3. Invocation error on missing root
            proc_err = subprocess.run(
                [PYTHON_BIN, str(script_path), "--root", str(root / "nonexistent_dir")],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc_err.returncode, 2)

    def test_non_destructive_input_immutability(self) -> None:
        records = [
            sample_source(source_id="SRC-001", url="https://example.com/same"),
            sample_source(source_id="SRC-002", url="https://example.com/same"),
        ]
        original_copy = copy.deepcopy(records)

        _ = find_source_duplicates(records)

        self.assertEqual(records, original_copy)

    def test_missing_or_empty_ids_and_urls_not_grouped(self) -> None:
        records = [
            sample_source(source_id="", url=""),
            sample_source(source_id="   ", url="   "),
            sample_source(source_id="SRC-001", url="https://example.com/one"),
        ]

        duplicates = find_source_duplicates(records)
        self.assertEqual(duplicates, [])

    def test_summary_affected_records_count(self) -> None:
        records = [
            # Two records sharing SRC-001 (id dupe)
            sample_source(source_id="SRC-001", url="https://example.com/a"),
            sample_source(source_id="SRC-001", url="https://example.com/b"),
            # Two records sharing same URL (url dupe) with different IDs
            sample_source(source_id="SRC-002", url="https://example.com/dupe_url"),
            sample_source(source_id="SRC-003", url="https://example.com/dupe_url"),
            # Clean record
            sample_source(source_id="SRC-004", url="https://example.com/clean"),
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            sources_path = root / "data" / "processed" / "sources.csv"
            write_csv_records(sources_path, self.source_fields, records)

            report = audit_duplicates(root)
            # Duplicate groups: 1 ID dupe (SRC-001), 1 URL dupe (https://example.com/dupe_url)
            self.assertEqual(report["summary"]["total_records"], 5)
            self.assertEqual(report["summary"]["duplicate_groups"], 2)
            self.assertEqual(report["summary"]["duplicate_id_groups"], 1)
            self.assertEqual(report["summary"]["duplicate_url_groups"], 1)
            # Affected records: {SRC-001, SRC-002, SRC-003} = 3 unique record IDs
            self.assertEqual(report["summary"]["affected_records"], 3)


if __name__ == "__main__":
    unittest.main()

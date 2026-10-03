from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.init_research import initialize_workspace

ROOT = Path(__file__).resolve().parents[1]
PYTHON_BIN = sys.executable

EXPECTED_TABLES = {
    "sources": ["source_id", "url", "title", "publisher", "source_type", "accessed_at", "published_at", "access_status", "collection_method", "content_hash", "limitations", "notes"],
    "observations": ["observation_id", "source_id", "entity_type", "entity_id", "attribute", "observed_value", "unit", "observed_at", "published_at", "evidence_excerpt", "collection_method", "confidence", "limitations"],
    "products": ["product_id", "product_name", "category", "seller_name", "product_url", "price_value", "currency", "price_observed_at", "commission_value", "commission_type", "commission_source_id", "customer_problem", "benefits_observed", "video_potential", "competition_notes", "evidence_type", "confidence", "limitations"],
    "competitors": ["competitor_id", "platform", "handle_or_name", "profile_url", "niche", "observed_at", "public_metrics", "metrics_observed_at", "content_patterns", "confidence", "limitations"],
    "videos": ["video_id", "competitor_id", "video_url", "published_at", "observed_at", "views_observed", "likes_observed", "comments_observed", "hook_observed", "story_structure", "product_presentation", "call_to_action", "affiliate_disclosure", "evidence_type", "confidence", "limitations"],
    "findings": ["finding_id", "finding_text", "source_ids", "observation_ids", "evidence_type", "calculation_method", "confidence", "limitations", "created_at", "status"],
    "hypotheses": ["hypothesis_id", "hypothesis", "basis_finding_ids", "target_audience", "proposed_test", "success_metric", "required_data", "status", "limitations"],
    "audit_findings": ["audit_id", "record_type", "record_id", "audit_rule", "result", "issue", "recommended_action", "audited_at"],
}


class InitResearchTests(unittest.TestCase):
    def test_initialize_creates_expected_directories_and_headers(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            created = initialize_workspace(root)

            self.assertTrue((root / "data" / "raw").is_dir())
            self.assertTrue((root / "data" / "processed").is_dir())
            self.assertTrue((root / "reports").is_dir())

            self.assertTrue((root / "data" / "raw" / ".gitkeep").is_file())
            self.assertTrue((root / "data" / "processed" / ".gitkeep").is_file())
            self.assertTrue((root / "reports" / ".gitkeep").is_file())

            self.assertEqual(len(created), 8)
            for table_name, expected_fields in EXPECTED_TABLES.items():
                csv_path = root / "data" / "processed" / f"{table_name}.csv"
                self.assertTrue(csv_path.is_file())
                self.assertIn(csv_path, created)
                with csv_path.open("r", encoding="utf-8", newline="") as handle:
                    reader = csv.reader(handle)
                    header = next(reader)
                    self.assertEqual(header, expected_fields)
                    # Verify no data rows yet
                    rows = list(reader)
                    self.assertEqual(rows, [])

    def test_initialize_never_overwrites_existing_records(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            initialize_workspace(root)

            sources_path = root / "data" / "processed" / "sources.csv"
            record_row = "src-001,https://example.com/test,Test Source,,,,,,,,\n"
            with sources_path.open("a", encoding="utf-8") as handle:
                handle.write(record_row)

            with self.assertRaises(FileExistsError):
                initialize_workspace(root, force=False)

            # Assert existing record is preserved
            content = sources_path.read_text(encoding="utf-8")
            self.assertIn("src-001", content)
            self.assertIn("https://example.com/test", content)

    def test_initialize_force_flag_behavior(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            initialize_workspace(root)

            # force=True on workspace with only headers succeeds without error
            recreated = initialize_workspace(root, force=True)
            self.assertEqual(len(recreated), 8)

            # Append a record to products.csv
            products_path = root / "data" / "processed" / "products.csv"
            record_row = "prod-001,Sample Product,beauty,,,,,,,,,,,,,,\n"
            with products_path.open("a", encoding="utf-8") as handle:
                handle.write(record_row)

            # force=True MUST still raise FileExistsError if data rows exist
            with self.assertRaises(FileExistsError):
                initialize_workspace(root, force=True)

            # Record must remain intact
            content = products_path.read_text(encoding="utf-8")
            self.assertIn("prod-001", content)

    def test_initialize_single_data_row_raises_file_exists_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            processed_dir = root / "data" / "processed"
            processed_dir.mkdir(parents=True, exist_ok=True)
            sources_path = processed_dir / "sources.csv"
            # Write a single non-header row (e.g. data without header)
            single_row = "src-only,https://example.com/single,Title,Pub,article,2026-10-02T10:00:00Z,,accessible,manual,,,\n"
            sources_path.write_text(single_row, encoding="utf-8")

            # force=False MUST raise FileExistsError and preserve record
            with self.assertRaises(FileExistsError):
                initialize_workspace(root, force=False)
            self.assertEqual(sources_path.read_text(encoding="utf-8"), single_row)

            # force=True MUST also raise FileExistsError and preserve record
            with self.assertRaises(FileExistsError):
                initialize_workspace(root, force=True)
            self.assertEqual(sources_path.read_text(encoding="utf-8"), single_row)

    def test_cli_invocation_creates_workspace_and_summarizes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            script_path = ROOT / "scripts" / "init_research.py"

            # Fresh init via CLI
            proc = subprocess.run(
                [PYTHON_BIN, str(script_path), "--root", str(root)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0)
            self.assertIn("created", proc.stdout.lower())
            self.assertNotIn("source_id,url", proc.stdout)  # No raw file contents printed

            # Second init without --force (should skip)
            proc_skip = subprocess.run(
                [PYTHON_BIN, str(script_path), "--root", str(root)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc_skip.returncode, 0)
            self.assertIn("skipped", proc_skip.stdout.lower())

            # Put a record and check CLI fails with non-zero exit code
            sources_path = root / "data" / "processed" / "sources.csv"
            with sources_path.open("a", encoding="utf-8") as handle:
                handle.write("src-cli,https://example.com,,,,,,,,,\n")

            proc_err = subprocess.run(
                [PYTHON_BIN, str(script_path), "--root", str(root), "--force"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(proc_err.returncode, 0)


if __name__ == "__main__":
    unittest.main()

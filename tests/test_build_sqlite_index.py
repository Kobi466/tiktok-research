"""Unit tests for reproducible SQLite index builder."""

from __future__ import annotations

import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON_BIN = sys.executable

from scripts.build_sqlite_index import build_index, main
from scripts.research_io import (
    load_definitions,
    processed_csv_path,
    table_fields,
    write_csv_records,
)


def sample_source(**kwargs: str) -> dict[str, str]:
    record = {
        "source_id": "SRC-001",
        "url": "https://www.tiktok.com/@creator/video/1234567890",
        "title": "Video đánh giá sản phẩm",
        "publisher": "Creator Name",
        "source_type": "video",
        "accessed_at": "2026-10-02T10:00:00Z",
        "published_at": "2026-10-01T12:00:00Z",
        "access_status": "accessible",
        "collection_method": "manual_review",
        "content_hash": "hash_val_1",
        "limitations": "",
        "notes": "Đánh giá chi tiết sản phẩm",
    }
    record.update(kwargs)
    return record


def sample_observation(**kwargs: str) -> dict[str, str]:
    record = {
        "observation_id": "OBS-001",
        "source_id": "SRC-001",
        "entity_type": "video",
        "entity_id": "VID-001",
        "attribute": "hook_type",
        "observed_value": "problem_solution",
        "unit": "",
        "observed_at": "2026-10-02T10:30:00Z",
        "published_at": "2026-10-01T12:00:00Z",
        "evidence_excerpt": "Mở đầu bằng câu hỏi về da dầu mụn",
        "collection_method": "manual_observation",
        "confidence": "high",
        "limitations": "",
    }
    record.update(kwargs)
    return record


def sample_product(**kwargs: str) -> dict[str, str]:
    record = {
        "product_id": "PRD-001",
        "product_name": "Serum phục hồi da",
        "category": "beauty",
        "seller_name": "Official Store",
        "product_url": "https://example.com/product/1",
        "price_value": "250000",
        "currency": "VND",
        "price_observed_at": "2026-10-02T10:00:00Z",
        "commission_value": "15",
        "commission_type": "percentage",
        "commission_source_id": "SRC-001",
        "customer_problem": "Da nhạy cảm cần phục hồi",
        "benefits_observed": "Làm dịu da kích ứng",
        "video_potential": "Dễ làm demo trước sau",
        "competition_notes": "Nhiều creator đang review",
        "evidence_type": "direct_source",
        "confidence": "high",
        "limitations": "",
    }
    record.update(kwargs)
    return record


class TestBuildSqliteIndex(unittest.TestCase):
    def setUp(self) -> None:
        self.definitions = load_definitions(ROOT)

    def test_build_index_creates_all_tables_and_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            # Populate sample records for 3 tables
            sources = [
                sample_source(source_id="SRC-001", title="Nguồn số 1"),
                sample_source(source_id="SRC-002", title="Nguồn số 2"),
            ]
            observations = [
                sample_observation(observation_id="OBS-001", source_id="SRC-001"),
            ]
            products = [
                sample_product(product_id="PRD-001", product_name="Sản phẩm A"),
                sample_product(product_id="PRD-002", product_name="Sản phẩm B"),
                sample_product(product_id="PRD-003", product_name="Sản phẩm C"),
            ]

            write_csv_records(
                processed_csv_path(root, "sources"),
                table_fields(self.definitions, "sources"),
                sources,
            )
            write_csv_records(
                processed_csv_path(root, "observations"),
                table_fields(self.definitions, "observations"),
                observations,
            )
            write_csv_records(
                processed_csv_path(root, "products"),
                table_fields(self.definitions, "products"),
                products,
            )

            # Build index with default database location
            db_path = build_index(root)
            expected_db = root / "data" / "research.sqlite"
            self.assertEqual(db_path, expected_db)
            self.assertTrue(db_path.is_file())

            # Connect and verify database integrity
            conn = sqlite3.connect(db_path)
            try:
                # PRAGMA integrity_check
                integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
                self.assertEqual(integrity, "ok")

                # Verify all 8 canonical tables exist
                cursor = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
                )
                tables = {row[0] for row in cursor.fetchall()}
                expected_tables = set(self.definitions["tables"].keys())
                self.assertEqual(tables, expected_tables)

                # Verify primary key and columns for sources table
                table_info = conn.execute('PRAGMA table_info("sources")').fetchall()
                col_names = [col[1] for col in table_info]
                self.assertEqual(col_names, table_fields(self.definitions, "sources"))
                # Verify primary key column is source_id
                pk_cols = [col[1] for col in table_info if col[5] == 1]
                self.assertEqual(pk_cols, ["source_id"])

                # Verify row counts
                source_count = conn.execute('SELECT count(*) FROM "sources"').fetchone()[0]
                self.assertEqual(source_count, 2)
                obs_count = conn.execute('SELECT count(*) FROM "observations"').fetchone()[0]
                self.assertEqual(obs_count, 1)
                prod_count = conn.execute('SELECT count(*) FROM "products"').fetchone()[0]
                self.assertEqual(prod_count, 3)

                # Unpopulated tables have 0 rows
                comp_count = conn.execute('SELECT count(*) FROM "competitors"').fetchone()[0]
                self.assertEqual(comp_count, 0)

                # Verify content and Vietnamese UTF-8 preservation
                row = conn.execute(
                    'SELECT "source_id", "title" FROM "sources" WHERE "source_id" = ?',
                    ("SRC-001",),
                ).fetchone()
                self.assertEqual(row, ("SRC-001", "Nguồn số 1"))
            finally:
                conn.close()

    def test_rebuild_removes_stale_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            sources_csv = processed_csv_path(root, "sources")
            fields = table_fields(self.definitions, "sources")

            # 1. Build initial index with 1 row
            write_csv_records(sources_csv, fields, [sample_source(source_id="SRC-001")])
            build_index(root)

            db_path = root / "data" / "research.sqlite"
            conn = sqlite3.connect(db_path)
            self.assertEqual(conn.execute('SELECT count(*) FROM "sources"').fetchone()[0], 1)
            conn.close()

            # 2. Clear rows from CSV
            write_csv_records(sources_csv, fields, [])

            # 3. Rebuild index
            build_index(root)

            conn = sqlite3.connect(db_path)
            self.assertEqual(conn.execute('SELECT count(*) FROM "sources"').fetchone()[0], 0)
            conn.close()

    def test_transactional_atomic_failure_preserves_existing_db(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            sources_csv = processed_csv_path(root, "sources")
            fields = table_fields(self.definitions, "sources")

            # 1. Build initial valid index with 1 record
            write_csv_records(
                sources_csv,
                fields,
                [sample_source(source_id="SRC-001", title="Bản ghi hợp lệ")],
            )
            db_path = build_index(root)
            self.assertTrue(db_path.is_file())

            # 2. Inject an error into CSV: duplicate primary key violating UNIQUE constraint
            write_csv_records(
                sources_csv,
                fields,
                [
                    sample_source(source_id="SRC-001", title="Bản ghi 1"),
                    sample_source(source_id="SRC-001", title="Bản ghi trùng ID"),
                ],
            )

            # 3. Call build_index and assert error is raised
            with self.assertRaises(sqlite3.IntegrityError):
                build_index(root)

            # 4. Verify existing database is still intact with original single record
            self.assertTrue(db_path.is_file())
            conn = sqlite3.connect(db_path)
            try:
                self.assertEqual(conn.execute("PRAGMA integrity_check").fetchone()[0], "ok")
                rows = conn.execute('SELECT "source_id", "title" FROM "sources"').fetchall()
                self.assertEqual(rows, [("SRC-001", "Bản ghi hợp lệ")])
            finally:
                conn.close()

            # 5. Verify temporary file was cleaned up
            tmp_db = db_path.with_name(f"{db_path.name}.tmp")
            self.assertFalse(tmp_db.exists())

    def test_cli_invocation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            sources_csv = processed_csv_path(root, "sources")
            fields = table_fields(self.definitions, "sources")
            write_csv_records(
                sources_csv,
                fields,
                [sample_source(source_id="SRC-001"), sample_source(source_id="SRC-002")],
            )

            custom_db = root / "custom" / "my_research.sqlite"
            script_path = ROOT / "scripts" / "build_sqlite_index.py"

            proc = subprocess.run(
                [
                    PYTHON_BIN,
                    str(script_path),
                    "--root",
                    str(root),
                    "--database",
                    str(custom_db),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(proc.returncode, 0, f"CLI stderr: {proc.stderr}")
            self.assertIn("sources", proc.stdout)
            self.assertIn("2", proc.stdout)
            self.assertTrue(custom_db.is_file())

            conn = sqlite3.connect(custom_db)
            try:
                self.assertEqual(conn.execute("PRAGMA integrity_check").fetchone()[0], "ok")
                self.assertEqual(
                    conn.execute('SELECT count(*) FROM "sources"').fetchone()[0], 2
                )
            finally:
                conn.close()

    def test_cli_invocation_invalid_root_exits_2(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            nonexistent = root / "does_not_exist"
            script_path = ROOT / "scripts" / "build_sqlite_index.py"

            proc = subprocess.run(
                [PYTHON_BIN, str(script_path), "--root", str(nonexistent)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 2)
            self.assertIn("error", proc.stderr.lower())

    def test_missing_and_empty_csvs_produce_empty_tables(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            # Create an empty 0-byte CSV for sources
            sources_csv = processed_csv_path(root, "sources")
            sources_csv.parent.mkdir(parents=True, exist_ok=True)
            sources_csv.write_text("", encoding="utf-8")

            # Other tables do not exist at all on filesystem
            db_path = build_index(root)
            self.assertTrue(db_path.is_file())

            conn = sqlite3.connect(db_path)
            try:
                self.assertEqual(conn.execute("PRAGMA integrity_check").fetchone()[0], "ok")
                for table_name in self.definitions["tables"]:
                    count = conn.execute(f'SELECT count(*) FROM "{table_name}"').fetchone()[0]
                    self.assertEqual(count, 0)
            finally:
                conn.close()


if __name__ == "__main__":
    unittest.main()

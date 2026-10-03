"""End-to-end integration tests for TikTok Affiliate Research System (Task 8).

Verifies the complete research lifecycle across all 5 scripts:
1. Workspace initialization (init_research)
2. Synthetic fixture writing (TEST_FIXTURE_ONLY)
3. Record validation (validate_records)
4. Duplicate source auditing (deduplicate_sources)
5. SQLite query index construction (build_sqlite_index)
6. Truthful Markdown summary export (export_research_summary)

Ensures zero external network calls, strict evidence separation, and truthful reporting.
"""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts import (
    build_sqlite_index,
    deduplicate_sources,
    export_research_summary,
    init_research,
    research_io,
    validate_records,
)

REQUIRED_HEADINGS = [
    "## Tóm tắt phạm vi và phương pháp",
    "## Nguồn thông tin đã sử dụng",
    "## Phát hiện có bằng chứng",
    "## Sản phẩm và nhóm sản phẩm",
    "## Dữ liệu video/kênh công khai",
    "## Giả thuyết chưa xác minh",
    "## Dữ liệu cần thu thập tiếp",
    "## Giới hạn và rủi ro",
    "## Kiểm toán dữ liệu",
]


class TestEndToEnd(unittest.TestCase):
    """End-to-end integration test suite."""

    def setUp(self) -> None:
        self.definitions = research_io.load_definitions(PROJECT_ROOT)

    def _write_synthetic_fixture(self, root: Path) -> dict[str, list[dict[str, str]]]:
        """Write synthetic test-only fixtures conforming strictly to canonical schemas.

        All URLs are under https://example.com to guarantee isolation.
        Marked as TEST_FIXTURE_ONLY.
        """
        now = "2026-10-02T10:00:00Z"

        # TEST_FIXTURE_ONLY
        fixture_sources = [
            {
                "source_id": "SRC-001",
                "url": "https://example.com/source-report-2026",
                "title": "Báo cáo thị trường gia dụng thông minh Việt Nam 2026",
                "publisher": "Hiệp hội Thương mại Điện tử",
                "source_type": "official_report",
                "accessed_at": now,
                "published_at": "2026-09-01T00:00:00Z",
                "access_status": "accessible",
                "collection_method": "public_web",
                "content_hash": "a1b2c3d4e5f67890",
                "limitations": "Khảo sát tập trung tại các đô thị lớn",
                "notes": "TEST_FIXTURE_ONLY",
            }
        ]
        research_io.write_csv_records(
            research_io.processed_csv_path(root, "sources"),
            research_io.table_fields(self.definitions, "sources"),
            fixture_sources,
        )

        # TEST_FIXTURE_ONLY
        fixture_observations = [
            {
                "observation_id": "OBS-001",
                "source_id": "SRC-001",
                "entity_type": "product",
                "entity_id": "PRD-001",
                "attribute": "price_point",
                "observed_value": "250000",
                "unit": "VND",
                "observed_at": now,
                "published_at": "2026-09-01T00:00:00Z",
                "evidence_excerpt": "Mức giá bán lẻ niêm yết phổ biến là 250.000 VND",
                "collection_method": "public_web",
                "confidence": "high",
                "limitations": "Số liệu tại thời điểm quý 3/2026",
            }
        ]
        research_io.write_csv_records(
            research_io.processed_csv_path(root, "observations"),
            research_io.table_fields(self.definitions, "observations"),
            fixture_observations,
        )

        # TEST_FIXTURE_ONLY
        fixture_products = [
            {
                "product_id": "PRD-001",
                "product_name": "Robot hút bụi cầm tay mini",
                "category": "Gia dụng thông minh",
                "seller_name": "SmartHome Official Store",
                "product_url": "https://example.com/product/robot-vacuum-01",
                "price_value": "250000",
                "currency": "VND",
                "price_observed_at": now,
                "commission_value": "25000",
                "commission_type": "percentage",
                "commission_source_id": "SRC-001",
                "customer_problem": "Làm sạch bụi mịn trên bàn làm việc và khe cửa sổ",
                "benefits_observed": "Nhỏ gọn, pin sạc Type-C, lực hút mạnh",
                "video_potential": "Dễ quay cận cảnh cảnh hút các hạt bụi và mẩu rác",
                "competition_notes": "Nhiều shop bán nhưng ít video review chi tiết",
                "evidence_type": "direct_source",
                "confidence": "high",
                "limitations": "Thời lượng pin thực tế cần được kiểm chứng thêm",
            },
            {
                "product_id": "PRD-002",
                "product_name": "Máy khuếch tán tinh dầu cảm biến",
                "category": "Gia dụng thông minh",
                "seller_name": "Aroma Lifestyle VN",
                "product_url": "https://example.com/product/diffuser-02",
                "price_value": "",
                "currency": "",
                "price_observed_at": "",
                "commission_value": "",
                "commission_type": "",
                "commission_source_id": "",
                "customer_problem": "Khử mùi phòng ngủ và tạo độ ẩm tự nhiên",
                "benefits_observed": "Tự ngắt khi cạn nước, đèn ngủ 7 màu",
                "video_potential": "Quay hiệu ứng phun sương trong phòng tối",
                "competition_notes": "Chưa có đơn vị phân phối độc quyền tại Việt Nam",
                "evidence_type": "direct_source",
                "confidence": "medium",
                "limitations": "Chưa xác minh được giá bán lẻ và tỷ lệ hoa hồng chính thức",
            },
        ]
        research_io.write_csv_records(
            research_io.processed_csv_path(root, "products"),
            research_io.table_fields(self.definitions, "products"),
            fixture_products,
        )

        # TEST_FIXTURE_ONLY
        fixture_competitors = [
            {
                "competitor_id": "CMP-001",
                "platform": "TikTok",
                "handle_or_name": "@giadung_thongminh_review",
                "profile_url": "https://example.com/creator/giadung-review",
                "niche": "Gia dụng thông minh",
                "observed_at": now,
                "public_metrics": "250.000 người theo dõi, 3.2M lượt thích",
                "metrics_observed_at": now,
                "content_patterns": "Hook vấn đề -> Giải pháp nhanh -> Trình diễn công năng",
                "confidence": "high",
                "limitations": "Chỉ số tương tác quan sát tại thời điểm nghiên cứu",
            }
        ]
        research_io.write_csv_records(
            research_io.processed_csv_path(root, "competitors"),
            research_io.table_fields(self.definitions, "competitors"),
            fixture_competitors,
        )

        # TEST_FIXTURE_ONLY
        fixture_videos = [
            {
                "video_id": "VID-001",
                "competitor_id": "CMP-001",
                "video_url": "https://example.com/video/review-robot-hut-bui",
                "published_at": "2026-09-15T14:30:00Z",
                "observed_at": now,
                "views_observed": "480000",
                "likes_observed": "32000",
                "comments_observed": "1500",
                "hook_observed": "3 giây đầu đổ hạt cà phê xuống bàn và bật máy hút",
                "story_structure": "Đặt thử thách làm sạch trong 10 giây",
                "product_presentation": "Quay macro cận cảnh đầu hút và hộp chứa bụi",
                "call_to_action": "Bấm vào giỏ hàng góc trái màn hình nhận mã giảm giá",
                "affiliate_disclosure": "Gắn nhãn quảng cáo và giỏ hàng TikTok Shop",
                "evidence_type": "direct_source",
                "confidence": "high",
                "limitations": "Video có thể đã được chạy quảng cáo tăng tương tác",
            }
        ]
        research_io.write_csv_records(
            research_io.processed_csv_path(root, "videos"),
            research_io.table_fields(self.definitions, "videos"),
            fixture_videos,
        )

        # TEST_FIXTURE_ONLY
        fixture_findings = [
            {
                "finding_id": "FND-001",
                "finding_text": "Nhu cầu máy hút bụi mini bàn làm việc gia tăng ở tệp nhân viên văn phòng",
                "source_ids": '["SRC-001"]',
                "observation_ids": '["OBS-001"]',
                "evidence_type": "direct_source",
                "calculation_method": "",
                "confidence": "high",
                "limitations": "Mẫu khảo sát giới hạn tại Hà Nội và TP.HCM",
                "created_at": now,
                "status": "accepted",
            }
        ]
        research_io.write_csv_records(
            research_io.processed_csv_path(root, "findings"),
            research_io.table_fields(self.definitions, "findings"),
            fixture_findings,
        )

        # TEST_FIXTURE_ONLY
        fixture_hypotheses = [
            {
                "hypothesis_id": "HYP-001",
                "hypothesis": "Video thử thách hút sạch bụi bàn làm việc trong 10s sẽ đạt tỷ lệ xem hết cao hơn review thông thường",
                "basis_finding_ids": '["FND-001"]',
                "target_audience": "Nhân viên văn phòng, người thích góc làm việc gọn gàng",
                "proposed_test": "Sản xuất 2 video cùng kịch bản nhưng khác 3 giây hook đầu tiên",
                "success_metric": "Tỷ lệ xem lại (rewatch rate) tăng 25% so với mức trung bình",
                "required_data": "Số liệu thời gian xem trung bình từ TikTok Analytics",
                "status": "unverified",
                "limitations": "Cần kênh có lượng người theo dõi tối thiểu để có lưu lượng tự nhiên",
            }
        ]
        research_io.write_csv_records(
            research_io.processed_csv_path(root, "hypotheses"),
            research_io.table_fields(self.definitions, "hypotheses"),
            fixture_hypotheses,
        )

        # TEST_FIXTURE_ONLY
        fixture_audit_findings = [
            {
                "audit_id": "AUD-001",
                "record_type": "source",
                "record_id": "SRC-001",
                "audit_rule": "source_reachability",
                "result": "pass",
                "issue": "Nguồn công khai có thể truy cập, định dạng hợp lệ",
                "recommended_action": "Duy trì bản ghi nguồn và lưu trữ bản sao",
                "audited_at": now,
            }
        ]
        research_io.write_csv_records(
            research_io.processed_csv_path(root, "audit_findings"),
            research_io.table_fields(self.definitions, "audit_findings"),
            fixture_audit_findings,
        )

        return {
            "sources": fixture_sources,
            "observations": fixture_observations,
            "products": fixture_products,
            "competitors": fixture_competitors,
            "videos": fixture_videos,
            "findings": fixture_findings,
            "hypotheses": fixture_hypotheses,
            "audit_findings": fixture_audit_findings,
        }

    def test_end_to_end_python_pipeline(self) -> None:
        """Verifies the complete Python API pipeline from init to export."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            # 1. Initialize workspace
            created_paths = init_research.initialize_workspace(root)
            self.assertTrue(len(created_paths) > 0)
            self.assertTrue((root / "data" / "processed" / "sources.csv").is_file())

            # 2. Write synthetic fixture (TEST_FIXTURE_ONLY)
            fixtures = self._write_synthetic_fixture(root)
            self.assertEqual(len(fixtures["sources"]), 1)
            self.assertEqual(len(fixtures["products"]), 2)

            # 3. Validate workspace
            validation_errors = validate_records.validate_workspace(root)
            self.assertEqual(
                validation_errors,
                [],
                f"Validation errors encountered on synthetic fixture: {validation_errors}",
            )

            # 4. Duplicate audit
            audit_result = deduplicate_sources.audit_duplicates(root)
            self.assertEqual(audit_result["summary"]["duplicate_groups"], 0)
            self.assertEqual(audit_result["summary"]["affected_records"], 0)
            self.assertEqual(len(audit_result["duplicates"]), 0)

            # 5. Build SQLite index
            db_path = build_sqlite_index.build_index(root)
            self.assertTrue(db_path.is_file())
            self.assertEqual(db_path.name, "research.sqlite")

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check;")
            integrity_row = cursor.fetchone()
            self.assertEqual(integrity_row[0], "ok")

            for table_name in self.definitions["tables"]:
                cursor.execute(f"SELECT count(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                expected_count = len(fixtures[table_name])
                self.assertEqual(
                    count,
                    expected_count,
                    f"Table {table_name} row count mismatch in SQLite: expected {expected_count}, got {count}",
                )
            conn.close()

            # 6. Export truthful Markdown summary
            report_path = root / "reports" / "test-summary.md"
            out_file = export_research_summary.export_summary(
                root, report_path, title="Báo cáo Nghiên cứu Thử nghiệm Pilot"
            )
            self.assertTrue(out_file.is_file())
            content = out_file.read_text(encoding="utf-8")

            # Verify title
            self.assertIn("# Báo cáo Nghiên cứu Thử nghiệm Pilot", content)

            # Verify all 9 required level-2 headings in exact order
            last_index = 0
            for heading in REQUIRED_HEADINGS:
                idx = content.find(heading)
                self.assertNotEqual(
                    idx,
                    -1,
                    f"Required heading '{heading}' not found in exported report",
                )
                self.assertGreater(
                    idx,
                    last_index,
                    f"Heading '{heading}' appeared out of order",
                )
                last_index = idx

            # Verify evidence separation:
            # Verified finding is in findings section, not hypotheses section
            findings_part = content.split("## Phát hiện có bằng chứng")[1].split(
                "## Sản phẩm và nhóm sản phẩm"
            )[0]
            hypotheses_part = content.split("## Giả thuyết chưa xác minh")[1].split(
                "## Dữ liệu cần thu thập tiếp"
            )[0]

            self.assertIn("FND-001", findings_part)
            self.assertIn("máy hút bụi mini bàn làm việc", findings_part)
            self.assertNotIn("HYP-001", findings_part)

            self.assertIn("HYP-001", hypotheses_part)
            self.assertIn("thử thách hút sạch bụi", hypotheses_part)
            self.assertNotIn("FND-001", hypotheses_part)

            # Verify commercial pricing truthfulness:
            # PRD-001 has verified price "250000 VND"
            # PRD-002 has blank price rendered as "Chưa có giá xác minh"
            products_part = content.split("## Sản phẩm và nhóm sản phẩm")[1].split(
                "## Dữ liệu video/kênh công khai"
            )[0]
            self.assertIn("PRD-001", products_part)
            self.assertIn("250000 VND", products_part)
            self.assertIn("PRD-002", products_part)
            self.assertIn("Chưa có giá xác minh", products_part)
            self.assertNotIn("| 0 VND |", products_part)

            # Verify public video metrics with observed_at timestamp
            videos_part = content.split("## Dữ liệu video/kênh công khai")[1].split(
                "## Giả thuyết chưa xác minh"
            )[0]
            self.assertIn("VID-001", videos_part)
            self.assertIn("480000", videos_part)
            self.assertIn("2026-10-02T10:00:00Z", videos_part)
            self.assertIn("observed_at", videos_part)

            # Verify source URL presence
            sources_part = content.split("## Nguồn thông tin đã sử dụng")[1].split(
                "## Phát hiện có bằng chứng"
            )[0]
            self.assertIn("https://example.com/source-report-2026", sources_part)

    def test_end_to_end_cli_pipeline(self) -> None:
        """Verifies CLI execution of all 5 scripts in sequence via subprocess."""
        python_bin = sys.executable

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            # 1. init_research.py CLI
            res1 = subprocess.run(
                [python_bin, str(PROJECT_ROOT / "scripts" / "init_research.py"), "--root", str(root)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res1.returncode, 0, f"init_research CLI failed: {res1.stderr}")

            # Write synthetic fixture (TEST_FIXTURE_ONLY)
            self._write_synthetic_fixture(root)

            # 2. validate_records.py CLI
            val_json = root / "reports" / "validation.json"
            res2 = subprocess.run(
                [
                    python_bin,
                    str(PROJECT_ROOT / "scripts" / "validate_records.py"),
                    "--root",
                    str(root),
                    "--output",
                    str(val_json),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res2.returncode, 0, f"validate_records CLI failed: {res2.stderr}")
            self.assertTrue(val_json.is_file())
            val_data = json.loads(val_json.read_text(encoding="utf-8"))
            self.assertEqual(val_data["summary"]["errors"], 0)

            # 3. deduplicate_sources.py CLI
            dup_json = root / "reports" / "duplicates.json"
            res3 = subprocess.run(
                [
                    python_bin,
                    str(PROJECT_ROOT / "scripts" / "deduplicate_sources.py"),
                    "--root",
                    str(root),
                    "--output",
                    str(dup_json),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res3.returncode, 0, f"deduplicate_sources CLI failed: {res3.stderr}")
            self.assertTrue(dup_json.is_file())
            dup_data = json.loads(dup_json.read_text(encoding="utf-8"))
            self.assertEqual(dup_data["summary"]["duplicate_groups"], 0)

            # 4. build_sqlite_index.py CLI
            res4 = subprocess.run(
                [
                    python_bin,
                    str(PROJECT_ROOT / "scripts" / "build_sqlite_index.py"),
                    "--root",
                    str(root),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res4.returncode, 0, f"build_sqlite_index CLI failed: {res4.stderr}")
            sqlite_file = root / "data" / "research.sqlite"
            self.assertTrue(sqlite_file.is_file())

            # 5. export_research_summary.py CLI
            report_md = root / "reports" / "cli-report.md"
            res5 = subprocess.run(
                [
                    python_bin,
                    str(PROJECT_ROOT / "scripts" / "export_research_summary.py"),
                    "--root",
                    str(root),
                    "--output",
                    str(report_md),
                    "--title",
                    "Báo cáo CLI Tích hợp Đầy đủ",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res5.returncode, 0, f"export_research_summary CLI failed: {res5.stderr}")
            self.assertTrue(report_md.is_file())
            content = report_md.read_text(encoding="utf-8")
            self.assertIn("# Báo cáo CLI Tích hợp Đầy đủ", content)
            self.assertIn("FND-001", content)
            self.assertIn("PRD-001", content)

    def test_end_to_end_empty_workspace_truthfulness(self) -> None:
        """Verifies clean handling of an empty workspace without hallucinating or failing."""
        python_bin = sys.executable

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            # Initialize empty workspace
            init_research.initialize_workspace(root)

            # Validate returns 0 errors
            errors = validate_records.validate_workspace(root)
            self.assertEqual(errors, [])

            # Duplicate check returns 0 duplicates
            dup = deduplicate_sources.audit_duplicates(root)
            self.assertEqual(dup["summary"]["total_records"], 0)
            self.assertEqual(dup["summary"]["duplicate_groups"], 0)

            # SQLite builds with 0 rows
            db_path = build_sqlite_index.build_index(root)
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            for table in self.definitions["tables"]:
                cur.execute(f"SELECT count(*) FROM {table};")
                self.assertEqual(cur.fetchone()[0], 0)
            conn.close()

            # Export reports that no verified data exists
            smoke_report = root / "reports" / "smoke.md"
            export_research_summary.export_summary(
                root, smoke_report, title="Báo cáo Smoke Hệ thống Trống"
            )
            self.assertTrue(smoke_report.is_file())
            smoke_text = smoke_report.read_text(encoding="utf-8")

            # Must contain unverified notice across empty sections
            self.assertIn("Chưa có dữ liệu được xác minh", smoke_text)
            self.assertIn("# Báo cáo Smoke Hệ thống Trống", smoke_text)

            # Must contain all 10 required headings in sequence
            last_index = 0
            for heading in REQUIRED_HEADINGS:
                idx = smoke_text.find(heading)
                self.assertNotEqual(idx, -1, f"Heading '{heading}' missing from smoke report")
                self.assertGreater(idx, last_index)
                last_index = idx


if __name__ == "__main__":
    unittest.main()

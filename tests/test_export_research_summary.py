"""Unit tests for truthful Markdown research summary exporter."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON_BIN = sys.executable

from scripts.export_research_summary import export_summary, main
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


def sample_competitor(**kwargs: str) -> dict[str, str]:
    record = {
        "competitor_id": "CMP-001",
        "platform": "tiktok",
        "handle_or_name": "@creator_a",
        "profile_url": "https://www.tiktok.com/@creator_a",
        "niche": "skincare",
        "observed_at": "2026-10-02T10:00:00Z",
        "public_metrics": '{"followers": 50000}',
        "metrics_observed_at": "2026-10-02T10:00:00Z",
        "content_patterns": "review chi tiết, thử nghiệm trên da",
        "confidence": "high",
        "limitations": "",
    }
    record.update(kwargs)
    return record


def sample_video(**kwargs: str) -> dict[str, str]:
    record = {
        "video_id": "VID-001",
        "competitor_id": "CMP-001",
        "video_url": "https://www.tiktok.com/@creator_a/video/123",
        "published_at": "2026-10-01T12:00:00Z",
        "observed_at": "2026-10-02T10:00:00Z",
        "views_observed": "125000",
        "likes_observed": "3200",
        "comments_observed": "45",
        "hook_observed": "Da dầu mụn dùng gì mùa hè?",
        "story_structure": "hook -> problem -> solution -> CTA",
        "product_presentation": "Thoa tinh chất lên mặt",
        "call_to_action": "Bấm vào giỏ hàng góc trái",
        "affiliate_disclosure": "Có gắn thẻ sản phẩm TikTok Shop",
        "evidence_type": "direct_source",
        "confidence": "high",
        "limitations": "",
    }
    record.update(kwargs)
    return record


def sample_finding(**kwargs: str) -> dict[str, str]:
    record = {
        "finding_id": "FND-001",
        "finding_text": "Serum dạng lỏng thẩm thấu nhanh trong 30 giây",
        "source_ids": '["SRC-001"]',
        "observation_ids": '["OBS-001"]',
        "evidence_type": "direct_source",
        "calculation_method": "",
        "confidence": "high",
        "limitations": "",
        "created_at": "2026-10-02T11:00:00Z",
        "status": "audited",
    }
    record.update(kwargs)
    return record


def sample_hypothesis(**kwargs: str) -> dict[str, str]:
    record = {
        "hypothesis_id": "HYP-001",
        "hypothesis": "Hook tập trung vào giải quyết mụn đầu đen sẽ đạt tỷ lệ xem cao hơn",
        "basis_finding_ids": '["FND-001"]',
        "target_audience": "Học sinh sinh viên có da dầu",
        "proposed_test": "Sản xuất 3 video thử nghiệm hook khác nhau",
        "success_metric": "Tỷ lệ giữ chân 3s > 40%",
        "required_data": "Số liệu retention 3s từ video thử nghiệm",
        "status": "unverified",
        "limitations": "Chưa có quyền truy cập dữ liệu retention chi tiết",
    }
    record.update(kwargs)
    return record


def sample_audit_finding(**kwargs: str) -> dict[str, str]:
    record = {
        "audit_id": "AUD-001",
        "record_type": "product",
        "record_id": "PRD-001",
        "audit_rule": "price_currency_consistency",
        "result": "pass",
        "issue": "",
        "recommended_action": "",
        "audited_at": "2026-10-02T12:00:00Z",
    }
    record.update(kwargs)
    return record


class TestExportResearchSummary(unittest.TestCase):
    def setUp(self) -> None:
        self.definitions = load_definitions(ROOT)

    def _extract_section(self, content: str, heading: str, next_heading: str | None = None) -> str:
        """Extract markdown content between heading and next_heading."""
        start_idx = content.find(heading)
        self.assertNotEqual(start_idx, -1, f"Heading not found: {heading}")
        start_pos = start_idx + len(heading)
        if next_heading:
            end_pos = content.find(next_heading, start_pos)
            self.assertNotEqual(end_pos, -1, f"Next heading not found: {next_heading}")
            return content[start_pos:end_pos]
        return content[start_pos:]

    def test_empty_workspace_states_that_no_verified_data_exists(self) -> None:
        """Empty workspace exports successfully and states no verified data exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            out_file = root / "reports" / "summary.md"

            returned_path = export_summary(
                root=root,
                output=out_file,
                title="Báo cáo trống kiểm thử",
            )
            self.assertEqual(returned_path, out_file.resolve())
            self.assertTrue(out_file.is_file())

            content = out_file.read_text(encoding="utf-8")
            self.assertIn("Chưa có dữ liệu được xác minh", content)
            self.assertIn("Tóm tắt phạm vi và phương pháp", content)
            self.assertIn("Giới hạn và rủi ro", content)

    def test_hypotheses_are_separate_from_verified_findings(self) -> None:
        """Verified findings appear under findings section; hypotheses appear under hypotheses section."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            findings_csv = processed_csv_path(root, "findings")
            hypotheses_csv = processed_csv_path(root, "hypotheses")

            write_csv_records(
                findings_csv,
                table_fields(self.definitions, "findings"),
                [
                    sample_finding(
                        finding_id="FND-001",
                        finding_text="Phát hiện xác minh thực tế 1",
                        evidence_type="direct_source",
                        status="audited",
                    ),
                    sample_finding(
                        finding_id="FND-002",
                        finding_text="Phát hiện giả thuyết chưa kiểm chứng 2",
                        evidence_type="hypothesis",
                        status="draft",
                    ),
                ],
            )
            write_csv_records(
                hypotheses_csv,
                table_fields(self.definitions, "hypotheses"),
                [
                    sample_hypothesis(
                        hypothesis_id="HYP-001",
                        hypothesis="Giả thuyết tăng trưởng kênh mới",
                        status="unverified",
                    )
                ],
            )

            out_file = root / "summary.md"
            export_summary(root=root, output=out_file, title="Kiểm thử phân tách giả thuyết")
            content = out_file.read_text(encoding="utf-8")

            findings_section = self._extract_section(
                content, "## Phát hiện có bằng chứng", "## Sản phẩm và nhóm sản phẩm"
            )
            hypotheses_section = self._extract_section(
                content, "## Giả thuyết chưa xác minh", "## Dữ liệu cần thu thập tiếp"
            )

            # Verified finding must be in findings section, not hypotheses
            self.assertIn("Phát hiện xác minh thực tế 1", findings_section)
            self.assertNotIn("Phát hiện xác minh thực tế 1", hypotheses_section)

            # Hypothesis finding and hypothesis must be in hypotheses section, NOT findings section
            self.assertNotIn("Phát hiện giả thuyết chưa kiểm chứng 2", findings_section)
            self.assertIn("Phát hiện giả thuyết chưa kiểm chứng 2", hypotheses_section)

            self.assertNotIn("Giả thuyết tăng trưởng kênh mới", findings_section)
            self.assertIn("Giả thuyết tăng trưởng kênh mới", hypotheses_section)

    def test_blocked_source_rendered_under_limitations(self) -> None:
        """Blocked source is explicitly reported under limitations and risks."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            sources_csv = processed_csv_path(root, "sources")

            write_csv_records(
                sources_csv,
                table_fields(self.definitions, "sources"),
                [
                    sample_source(
                        source_id="SRC-BLOCKED-01",
                        url="https://example.com/blocked-source-url",
                        access_status="blocked",
                        limitations="Bị chặn bởi Cloudflare CAPTCHA",
                    ),
                    sample_source(
                        source_id="SRC-OK-01",
                        url="https://example.com/ok-source-url",
                        access_status="accessible",
                        limitations="",
                    ),
                ],
            )

            out_file = root / "summary.md"
            export_summary(root=root, output=out_file, title="Kiểm thử nguồn bị chặn")
            content = out_file.read_text(encoding="utf-8")

            limitations_section = self._extract_section(
                content, "## Giới hạn và rủi ro", "## Kiểm toán dữ liệu"
            )

            self.assertIn("SRC-BLOCKED-01", limitations_section)
            self.assertIn("https://example.com/blocked-source-url", limitations_section)
            self.assertIn("blocked", limitations_section.lower())

    def test_product_with_blank_price_not_numeric(self) -> None:
        """Product with empty price_value displays unverified text and never 0 or invented price."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            products_csv = processed_csv_path(root, "products")

            write_csv_records(
                products_csv,
                table_fields(self.definitions, "products"),
                [
                    sample_product(
                        product_id="PRD-NOPRICE",
                        product_name="Kem dưỡng ẩm chưa có giá",
                        price_value="",
                        currency="VND",
                    ),
                    sample_product(
                        product_id="PRD-HASPRICE",
                        product_name="Sữa rửa mặt có giá",
                        price_value="180000",
                        currency="VND",
                    ),
                ],
            )

            out_file = root / "summary.md"
            export_summary(root=root, output=out_file, title="Kiểm thử giá sản phẩm")
            content = out_file.read_text(encoding="utf-8")

            products_section = self._extract_section(
                content, "## Sản phẩm và nhóm sản phẩm", "## Dữ liệu video/kênh công khai"
            )

            self.assertIn("Kem dưỡng ẩm chưa có giá", products_section)
            self.assertIn("Chưa có giá xác minh", products_section)
            self.assertIn("180000 VND", products_section)

            # Ensure we don't display 0 VND or 0 for the unpriced product
            lines = [ln for ln in products_section.splitlines() if "PRD-NOPRICE" in ln]
            self.assertTrue(lines)
            row = lines[0]
            self.assertNotIn("0 VND", row)
            self.assertNotIn("| 0 |", row)
            self.assertIn("Chưa có giá xác minh", row)

    def test_video_metrics_labeled_with_observed_at(self) -> None:
        """Video metrics explicitly display observation timestamp."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            videos_csv = processed_csv_path(root, "videos")

            obs_time = "2026-10-02T10:00:00Z"
            write_csv_records(
                videos_csv,
                table_fields(self.definitions, "videos"),
                [
                    sample_video(
                        video_id="VID-METRIC-01",
                        views_observed="350000",
                        likes_observed="12000",
                        comments_observed="340",
                        observed_at=obs_time,
                    )
                ],
            )

            out_file = root / "summary.md"
            export_summary(root=root, output=out_file, title="Kiểm thử số liệu video")
            content = out_file.read_text(encoding="utf-8")

            videos_section = self._extract_section(
                content, "## Dữ liệu video/kênh công khai", "## Giả thuyết chưa xác minh"
            )

            self.assertIn("VID-METRIC-01", videos_section)
            self.assertIn("350000", videos_section)
            self.assertIn(obs_time, videos_section)

    def test_headings_exact_order(self) -> None:
        """All 10 required headings appear in the exact required order."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            out_file = root / "summary.md"

            export_summary(root=root, output=out_file, title="Kiểm thử thứ tự tiêu đề")
            content = out_file.read_text(encoding="utf-8")

            expected_headings = [
                "# Kiểm thử thứ tự tiêu đề",
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

            last_pos = -1
            for heading in expected_headings:
                pos = content.find(heading)
                self.assertNotEqual(pos, -1, f"Missing heading: {heading}")
                self.assertGreater(
                    pos, last_pos, f"Heading '{heading}' is out of order in output."
                )
                last_pos = pos

    def test_cli_invocation(self) -> None:
        """Test CLI invocation via subprocess."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            sources_csv = processed_csv_path(root, "sources")
            write_csv_records(
                sources_csv,
                table_fields(self.definitions, "sources"),
                [sample_source(source_id="SRC-CLI-01")],
            )

            out_file = root / "reports" / "cli-report.md"
            script_path = ROOT / "scripts" / "export_research_summary.py"

            proc = subprocess.run(
                [
                    PYTHON_BIN,
                    str(script_path),
                    "--root",
                    str(root),
                    "--output",
                    str(out_file),
                    "--title",
                    "CLI Test Report Title",
                    "--accessed-at",
                    "2026-10-02T15:30:00Z",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(proc.returncode, 0, f"CLI stderr: {proc.stderr}")
            self.assertTrue(out_file.is_file())
            content = out_file.read_text(encoding="utf-8")
            self.assertIn("# CLI Test Report Title", content)
            self.assertIn("SRC-CLI-01", content)
            self.assertIn("2026-10-02T15:30:00Z", content)

    def test_cli_invocation_invalid_args_exits_2(self) -> None:
        """CLI invocation with invalid or missing args exits with code 2."""
        script_path = ROOT / "scripts" / "export_research_summary.py"

        # Missing required --output and --title
        proc1 = subprocess.run(
            [PYTHON_BIN, str(script_path), "--root", "."],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc1.returncode, 2)

        # Nonexistent root directory
        with tempfile.TemporaryDirectory() as temp_dir:
            nonexistent = Path(temp_dir) / "does_not_exist"
            proc2 = subprocess.run(
                [
                    PYTHON_BIN,
                    str(script_path),
                    "--root",
                    str(nonexistent),
                    "--output",
                    str(Path(temp_dir) / "out.md"),
                    "--title",
                    "Test Title",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc2.returncode, 2)
            self.assertIn("error", proc2.stderr.lower())

    def test_escaping_pipe_and_newlines(self) -> None:
        """Markdown table cells must escape pipe characters and flatten newlines."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            findings_csv = processed_csv_path(root, "findings")

            write_csv_records(
                findings_csv,
                table_fields(self.definitions, "findings"),
                [
                    sample_finding(
                        finding_id="FND-PIPE-01",
                        finding_text="Nội dung có ký tự | pipe và\nxuống dòng",
                        evidence_type="direct_source",
                        status="audited",
                    )
                ],
            )

            out_file = root / "summary.md"
            export_summary(root=root, output=out_file, title="Kiểm thử escape")
            content = out_file.read_text(encoding="utf-8")

            findings_section = self._extract_section(
                content, "## Phát hiện có bằng chứng", "## Sản phẩm và nhóm sản phẩm"
            )
            # Pipe must be escaped with \|
            self.assertIn(r"\|", findings_section)
            # No raw newline within table row
            matching_lines = [ln for ln in findings_section.splitlines() if "FND-PIPE-01" in ln]
            self.assertEqual(len(matching_lines), 1)
            self.assertIn("Nội dung có ký tự \\| pipe và xuống dòng", matching_lines[0])

    def test_deterministic_sorting_by_id(self) -> None:
        """Records in each section must be sorted by primary ID deterministically."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            sources_csv = processed_csv_path(root, "sources")

            # Write out of order: SRC-003, SRC-001, SRC-002
            write_csv_records(
                sources_csv,
                table_fields(self.definitions, "sources"),
                [
                    sample_source(source_id="SRC-003", title="Nguồn 3"),
                    sample_source(source_id="SRC-001", title="Nguồn 1"),
                    sample_source(source_id="SRC-002", title="Nguồn 2"),
                ],
            )

            out_file = root / "summary.md"
            export_summary(root=root, output=out_file, title="Kiểm thử sắp xếp")
            content = out_file.read_text(encoding="utf-8")

            sources_section = self._extract_section(
                content, "## Nguồn thông tin đã sử dụng", "## Phát hiện có bằng chứng"
            )
            pos_1 = sources_section.find("SRC-001")
            pos_2 = sources_section.find("SRC-002")
            pos_3 = sources_section.find("SRC-003")

            self.assertTrue(pos_1 < pos_2 < pos_3, "Sources are not sorted by source_id")

    def test_commercial_commission_and_audit_findings(self) -> None:
        """Commission details and audit findings are accurately rendered."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            products_csv = processed_csv_path(root, "products")
            audit_csv = processed_csv_path(root, "audit_findings")

            write_csv_records(
                products_csv,
                table_fields(self.definitions, "products"),
                [
                    sample_product(
                        product_id="PRD-COMM-01",
                        commission_value="20",
                        commission_type="percentage",
                        commission_source_id="SRC-001",
                    )
                ],
            )
            write_csv_records(
                audit_csv,
                table_fields(self.definitions, "audit_findings"),
                [
                    sample_audit_finding(
                        audit_id="AUD-001",
                        record_type="product",
                        record_id="PRD-COMM-01",
                        audit_rule="price_currency_consistency",
                        result="pass",
                        issue="",
                        recommended_action="",
                    )
                ],
            )

            out_file = root / "summary.md"
            export_summary(root=root, output=out_file, title="Kiểm thử hoa hồng và kiểm toán")
            content = out_file.read_text(encoding="utf-8")

            products_section = self._extract_section(
                content, "## Sản phẩm và nhóm sản phẩm", "## Dữ liệu video/kênh công khai"
            )
            self.assertIn("20 (percentage) [Nguồn: SRC-001]", products_section)

            audit_section = self._extract_section(content, "## Kiểm toán dữ liệu")
            self.assertIn("AUD-001", audit_section)
            self.assertIn("price_currency_consistency", audit_section)
            self.assertIn("pass", audit_section)


if __name__ == "__main__":
    unittest.main()

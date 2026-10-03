from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.init_research import initialize_workspace
from scripts.research_io import write_csv_records
from scripts.validate_records import validate_workspace

ROOT = Path(__file__).resolve().parents[1]
PYTHON_BIN = sys.executable


def valid_source(**kwargs: str) -> dict[str, str]:
    record = {
        "source_id": "src-001",
        "url": "https://example.com/source1",
        "title": "Source Title 1",
        "publisher": "Example News",
        "source_type": "article",
        "accessed_at": "2026-10-02T10:00:00Z",
        "published_at": "2026-10-01T10:00:00Z",
        "access_status": "accessible",
        "collection_method": "web_fetch",
        "content_hash": "hash123",
        "limitations": "",
        "notes": "",
    }
    record.update(kwargs)
    return record


def valid_observation(**kwargs: str) -> dict[str, str]:
    record = {
        "observation_id": "obs-001",
        "source_id": "src-001",
        "entity_type": "creator",
        "entity_id": "comp-001",
        "attribute": "follower_count",
        "observed_value": "15000",
        "unit": "count",
        "observed_at": "2026-10-02T10:00:00Z",
        "published_at": "",
        "evidence_excerpt": "15k followers",
        "collection_method": "web_fetch",
        "confidence": "high",
        "limitations": "",
    }
    record.update(kwargs)
    return record


def valid_product(**kwargs: str) -> dict[str, str]:
    record = {
        "product_id": "prod-001",
        "product_name": "Test Desk Lamp",
        "category": "home_office",
        "seller_name": "Lamp Store",
        "product_url": "https://example.com/lamp",
        "price_value": "250000",
        "currency": "VND",
        "price_observed_at": "2026-10-02T10:00:00Z",
        "commission_value": "10",
        "commission_type": "percentage",
        "commission_source_id": "src-001",
        "customer_problem": "Poor lighting",
        "benefits_observed": "Eye protection",
        "video_potential": "high",
        "competition_notes": "low",
        "evidence_type": "direct_source",
        "confidence": "high",
        "limitations": "",
    }
    record.update(kwargs)
    return record


def valid_competitor(**kwargs: str) -> dict[str, str]:
    record = {
        "competitor_id": "comp-001",
        "platform": "tiktok",
        "handle_or_name": "@creator_desk",
        "profile_url": "https://tiktok.com/@creator_desk",
        "niche": "desk_setup",
        "observed_at": "2026-10-02T10:00:00Z",
        "public_metrics": "",
        "metrics_observed_at": "",
        "content_patterns": "unboxing",
        "confidence": "high",
        "limitations": "",
    }
    record.update(kwargs)
    return record


def valid_video(**kwargs: str) -> dict[str, str]:
    record = {
        "video_id": "vid-001",
        "competitor_id": "comp-001",
        "video_url": "https://tiktok.com/@creator_desk/video/100",
        "published_at": "2026-10-01T12:00:00Z",
        "observed_at": "2026-10-02T10:00:00Z",
        "views_observed": "50000",
        "likes_observed": "2000",
        "comments_observed": "150",
        "hook_observed": "Check this desk light",
        "story_structure": "Hook -> Demo -> CTA",
        "product_presentation": "Live demonstration",
        "call_to_action": "Buy from yellow basket",
        "affiliate_disclosure": "true",
        "evidence_type": "direct_source",
        "confidence": "high",
        "limitations": "",
    }
    record.update(kwargs)
    return record


def valid_finding(**kwargs: str) -> dict[str, str]:
    record = {
        "finding_id": "fnd-001",
        "finding_text": "Desk lamps have strong review video engagement.",
        "source_ids": '["src-001"]',
        "observation_ids": '["obs-001"]',
        "evidence_type": "direct_source",
        "calculation_method": "",
        "confidence": "high",
        "limitations": "",
        "created_at": "2026-10-02T10:00:00Z",
        "status": "draft",
    }
    record.update(kwargs)
    return record


def valid_hypothesis(**kwargs: str) -> dict[str, str]:
    record = {
        "hypothesis_id": "hyp-001",
        "hypothesis": "Publishing unboxing reviews will generate conversions.",
        "basis_finding_ids": '["fnd-001"]',
        "target_audience": "Remote workers",
        "proposed_test": "3 review videos",
        "success_metric": "1000 views per video",
        "required_data": "View counts",
        "status": "unverified",
        "limitations": "",
    }
    record.update(kwargs)
    return record


def valid_audit_finding(**kwargs: str) -> dict[str, str]:
    record = {
        "audit_id": "aud-001",
        "record_type": "source",
        "record_id": "src-001",
        "audit_rule": "url_accessible",
        "result": "pass",
        "issue": "none",
        "recommended_action": "none",
        "audited_at": "2026-10-02T10:00:00Z",
    }
    record.update(kwargs)
    return record


def write_full_valid_workspace(root: Path) -> None:
    initialize_workspace(root)
    write_table_records(root, "sources", [valid_source()])
    write_table_records(root, "observations", [valid_observation()])
    write_table_records(root, "products", [valid_product()])
    write_table_records(root, "competitors", [valid_competitor()])
    write_table_records(root, "videos", [valid_video()])
    write_table_records(root, "findings", [valid_finding()])
    write_table_records(root, "hypotheses", [valid_hypothesis()])
    write_table_records(root, "audit_findings", [valid_audit_finding()])


def write_table_records(root: Path, table_name: str, records: list[dict[str, str]]) -> None:
    csv_path = root / "data" / "processed" / f"{table_name}.csv"
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        header = handle.readline().strip().split(",")
    write_csv_records(csv_path, header, records)


class ValidateRecordsTests(unittest.TestCase):
    def assertIssue(
        self,
        issues: list[dict],
        *,
        table: str,
        rule: str,
        severity: str,
        record_id: str | None = None,
    ) -> None:
        matched = [
            i for i in issues
            if i["table"] == table and i["rule"] == rule and i["severity"] == severity
            and (record_id is None or i["record_id"] == record_id)
        ]
        self.assertTrue(
            len(matched) > 0,
            f"Expected issue (table={table}, rule={rule}, severity={severity}, record_id={record_id}) "
            f"not found in: {issues}",
        )

    def test_valid_records_have_no_issues(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_full_valid_workspace(root)
            issues = validate_workspace(root)
            self.assertEqual(issues, [])

    def test_missing_absolute_url_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_full_valid_workspace(root)
            write_table_records(root, "sources", [valid_source(url="not-a-url")])
            issues = validate_workspace(root)
            self.assertIssue(issues, table="sources", rule="url_absolute", severity="error")

    def test_missing_source_reference_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_full_valid_workspace(root)
            write_table_records(root, "observations", [valid_observation(source_id="src-missing")])
            issues = validate_workspace(root)
            self.assertIssue(issues, table="observations", rule="foreign_key", severity="error")

    def test_calculated_without_method_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_full_valid_workspace(root)
            write_table_records(
                root,
                "findings",
                [valid_finding(evidence_type="calculated", calculation_method="")],
            )
            issues = validate_workspace(root)
            self.assertIssue(issues, table="findings", rule="calculation_method", severity="error")

    def test_estimate_without_limitations_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_full_valid_workspace(root)
            write_table_records(
                root,
                "products",
                [valid_product(evidence_type="estimate", limitations="")],
            )
            issues = validate_workspace(root)
            self.assertIssue(issues, table="products", rule="estimate_limitations", severity="error")

    def test_hypothesis_is_not_verified(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_full_valid_workspace(root)
            write_table_records(
                root,
                "findings",
                [valid_finding(evidence_type="hypothesis", status="accepted")],
            )
            issues = validate_workspace(root)
            self.assertIssue(issues, table="findings", rule="hypothesis_status", severity="error")

    def test_invalid_enum_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_full_valid_workspace(root)
            write_table_records(
                root,
                "observations",
                [valid_observation(confidence="extremely_high")],
            )
            issues = validate_workspace(root)
            self.assertIssue(issues, table="observations", rule="enum_value", severity="error")

    def test_missing_observed_at_for_video_metric(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_full_valid_workspace(root)
            write_table_records(
                root,
                "videos",
                [valid_video(views_observed="1000", observed_at="")],
            )
            issues = validate_workspace(root)
            self.assertIssue(issues, table="videos", rule="missing_observed_at", severity="error")

    def test_missing_currency_when_price_present(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_full_valid_workspace(root)
            write_table_records(
                root,
                "products",
                [valid_product(price_value="150000", currency="")],
            )
            issues = validate_workspace(root)
            self.assertIssue(issues, table="products", rule="missing_currency", severity="error")

    def test_invalid_timestamp_format(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_full_valid_workspace(root)
            write_table_records(
                root,
                "sources",
                [valid_source(accessed_at="not-a-timestamp")],
            )
            issues = validate_workspace(root)
            self.assertIssue(issues, table="sources", rule="timestamp_format", severity="error")

    def test_duplicate_id_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_full_valid_workspace(root)
            write_table_records(
                root,
                "sources",
                [valid_source(source_id="src-dup"), valid_source(source_id="src-dup", url="https://example.com/2")],
            )
            issues = validate_workspace(root)
            self.assertIssue(issues, table="sources", rule="duplicate_id", severity="error")

    def test_duplicate_source_url_is_a_warning(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_full_valid_workspace(root)
            write_table_records(
                root,
                "sources",
                [
                    valid_source(source_id="src-001", url="https://example.com/same"),
                    valid_source(source_id="src-002", url="https://example.com/same"),
                ],
            )
            issues = validate_workspace(root)
            self.assertIssue(issues, table="sources", rule="duplicate_url", severity="warning")

    def test_invalid_json_array_and_foreign_key_in_array(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_full_valid_workspace(root)

            # Malformed JSON in source_ids
            write_table_records(
                root,
                "findings",
                [valid_finding(source_ids="not-json")],
            )
            issues = validate_workspace(root)
            self.assertIssue(issues, table="findings", rule="invalid_json_array", severity="error")

            # Missing referenced foreign key inside valid JSON array
            write_table_records(
                root,
                "findings",
                [valid_finding(source_ids='["src-nonexistent"]')],
            )
            issues = validate_workspace(root)
            self.assertIssue(issues, table="findings", rule="foreign_key", severity="error")

    def test_missing_commission_source_when_commission_value_present(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_full_valid_workspace(root)
            write_table_records(
                root,
                "products",
                [valid_product(commission_value="15", commission_source_id="")],
            )
            issues = validate_workspace(root)
            self.assertIssue(issues, table="products", rule="missing_commission_source", severity="error")

    def test_truncated_csv_row_does_not_raise_attribute_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_full_valid_workspace(root)
            sources_path = root / "data" / "processed" / "sources.csv"
            # Append a truncated row with only 2 columns instead of 12
            with sources_path.open("a", encoding="utf-8") as handle:
                handle.write("src-trunc,https://example.com/trunc\n")

            # Must not crash with AttributeError and should report missing required fields
            issues = validate_workspace(root)
            self.assertIssue(
                issues,
                table="sources",
                rule="required_field",
                severity="error",
                record_id="src-trunc",
            )

    def test_cli_execution_json_report_and_exit_codes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            initialize_workspace(root)
            script_path = ROOT / "scripts" / "validate_records.py"
            report_file = root / "report.json"

            # 1. Clean workspace -> exit 0
            proc_ok = subprocess.run(
                [PYTHON_BIN, str(script_path), "--root", str(root), "--output", str(report_file)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc_ok.returncode, 0)
            self.assertTrue(report_file.is_file())
            data = json.loads(report_file.read_text(encoding="utf-8"))
            self.assertEqual(data["summary"]["errors"], 0)
            self.assertEqual(data["summary"]["warnings"], 0)
            self.assertEqual(data["summary"]["tables_checked"], 8)

            # 2. Warning with and without --fail-on-warning
            write_table_records(
                root,
                "sources",
                [
                    valid_source(source_id="src-001", url="https://example.com/same"),
                    valid_source(source_id="src-002", url="https://example.com/same"),
                ],
            )
            proc_warn_allow = subprocess.run(
                [PYTHON_BIN, str(script_path), "--root", str(root)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc_warn_allow.returncode, 0)

            proc_warn_fail = subprocess.run(
                [PYTHON_BIN, str(script_path), "--root", str(root), "--fail-on-warning"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc_warn_fail.returncode, 1)

            # 3. Nonexistent root -> exit 2
            proc_bad_root = subprocess.run(
                [PYTHON_BIN, str(script_path), "--root", str(root / "nonexistent_dir")],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc_bad_root.returncode, 2)


if __name__ == "__main__":
    unittest.main()

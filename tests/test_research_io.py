from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from scripts.research_io import (
    load_definitions,
    read_csv_records,
    table_fields,
    utc_now,
    write_csv_records,
    write_json,
)


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

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_TABLES = {
    "source-record.json": "sources",
    "observation-record.json": "observations",
    "product-record.json": "products",
    "video-record.json": "videos",
    "finding-record.json": "findings",
    "hypothesis-record.json": "hypotheses",
}


class ResearchIoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.definitions = load_definitions(ROOT)

    def test_all_exact_expected_table_fields(self) -> None:
        self.assertEqual(set(self.definitions["tables"]), set(EXPECTED_TABLES))
        for table_name, expected_fields in EXPECTED_TABLES.items():
            self.assertEqual(table_fields(self.definitions, table_name), expected_fields)

    def test_utc_now_is_iso_8601_utc(self) -> None:
        timestamp = utc_now()
        self.assertTrue(timestamp.endswith("Z"))
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        self.assertIsNotNone(parsed.tzinfo)
        self.assertEqual(parsed.utcoffset().total_seconds(), 0)

    def test_csv_round_trip_retains_vietnamese_and_empty_strings(self) -> None:
        fields = ["name", "note", "empty"]
        records = [{"name": "Đèn học", "note": "Nội dung có dấu", "empty": ""}]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "records.csv"
            write_csv_records(path, fields, records)
            self.assertEqual(read_csv_records(path), records)

    def test_unknown_table_raises_key_error(self) -> None:
        with self.assertRaises(KeyError):
            table_fields(self.definitions, "unknown_table")

    def test_missing_or_malformed_schema_names_path_and_key(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "config"
            config.mkdir()
            path = config / "field-definitions.json"
            path.write_text('{"version": "1.0.0"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, r"field-definitions\.json.*evidence_types"):
                load_definitions(root)
            path.write_text('{not valid json', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, r"field-definitions\.json.*malformed JSON"):
                load_definitions(root)

    def test_structurally_malformed_schemas_name_path_and_offending_key(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "config" / "field-definitions.json"
            path.parent.mkdir()
            cases = [
                ("tables", []),
                ("tables.sources.required", "not a list"),
                ("tables.products.enums", []),
                ("tables.videos.fields", ["video_id"]),
            ]
            for key, replacement in cases:
                with self.subTest(key=key):
                    schema = json.loads(json.dumps(self.definitions))
                    target = schema
                    parts = key.split(".")
                    for part in parts[:-1]:
                        target = target[part]
                    target[parts[-1]] = replacement
                    path.write_text(json.dumps(schema), encoding="utf-8")
                    escaped_key = key.replace(".", "\\.")
                    with self.assertRaisesRegex(
                        ValueError, rf"field-definitions\.json.*{escaped_key}",
                    ):
                        load_definitions(root)

    def test_invalid_top_level_values_name_path_and_key(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "config" / "field-definitions.json"
            path.parent.mkdir()
            schema = json.loads(json.dumps(self.definitions))
            schema["evidence_types"] = ["invalid"]
            path.write_text(json.dumps(schema), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, r"field-definitions\.json.*evidence_types"):
                load_definitions(root)

    def test_json_output_parses_and_has_final_newline(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "output.json"
            value = {"message": "Dữ liệu trống", "items": []}
            write_json(path, value)
            self.assertTrue(path.read_bytes().endswith(b"\n"))
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), value)

    def test_json_templates_are_empty_canonical_templates(self) -> None:
        for filename, table_name in TEMPLATE_TABLES.items():
            with self.subTest(filename=filename):
                template = json.loads((ROOT / "templates" / filename).read_text(encoding="utf-8"))
                self.assertIs(template["_template"], True)
                self.assertIn("_note", template)
                for field in EXPECTED_TABLES[table_name]:
                    self.assertIn(field, template)


if __name__ == "__main__":
    unittest.main()

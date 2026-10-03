"""Shared, standard-library I/O helpers for the research data set."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_DEFINITIONS_RELATIVE_PATH = Path("config") / "field-definitions.json"
_EXPECTED_VERSION = "1.0.0"
_EXPECTED_EVIDENCE_TYPES = ["direct_source", "calculated", "estimate", "hypothesis"]
_EXPECTED_CONFIDENCE_LEVELS = ["high", "medium", "low", "unverified"]
_EXPECTED_ACCESS_STATUSES = ["accessible", "partial", "blocked", "not_verified"]
_EXPECTED_TABLES = {
    "sources": [
        "source_id", "url", "title", "publisher", "source_type", "accessed_at",
        "published_at", "access_status", "collection_method", "content_hash",
        "limitations", "notes",
    ],
    "observations": [
        "observation_id", "source_id", "entity_type", "entity_id", "attribute",
        "observed_value", "unit", "observed_at", "published_at", "evidence_excerpt",
        "collection_method", "confidence", "limitations",
    ],
    "products": [
        "product_id", "product_name", "category", "seller_name", "product_url",
        "price_value", "currency", "price_observed_at", "commission_value",
        "commission_type", "commission_source_id", "customer_problem",
        "benefits_observed", "video_potential", "competition_notes", "evidence_type",
        "confidence", "limitations",
    ],
    "competitors": [
        "competitor_id", "platform", "handle_or_name", "profile_url", "niche",
        "observed_at", "public_metrics", "metrics_observed_at", "content_patterns",
        "confidence", "limitations",
    ],
    "videos": [
        "video_id", "competitor_id", "video_url", "published_at", "observed_at",
        "views_observed", "likes_observed", "comments_observed", "hook_observed",
        "story_structure", "product_presentation", "call_to_action",
        "affiliate_disclosure", "evidence_type", "confidence", "limitations",
    ],
    "findings": [
        "finding_id", "finding_text", "source_ids", "observation_ids", "evidence_type",
        "calculation_method", "confidence", "limitations", "created_at", "status",
    ],
    "hypotheses": [
        "hypothesis_id", "hypothesis", "basis_finding_ids", "target_audience",
        "proposed_test", "success_metric", "required_data", "status", "limitations",
    ],
    "audit_findings": [
        "audit_id", "record_type", "record_id", "audit_rule", "result", "issue",
        "recommended_action", "audited_at",
    ],
}
_EXPECTED_REQUIRED = {
    "sources": ["source_id", "url", "title", "source_type", "accessed_at", "access_status", "collection_method"],
    "observations": ["observation_id", "source_id", "entity_type", "entity_id", "attribute", "observed_value", "observed_at", "collection_method", "confidence"],
    "products": ["product_id", "product_name", "category", "evidence_type", "confidence"],
    "competitors": ["competitor_id", "platform", "handle_or_name", "profile_url", "observed_at", "confidence"],
    "videos": ["video_id", "competitor_id", "video_url", "observed_at", "evidence_type", "confidence"],
    "findings": ["finding_id", "finding_text", "evidence_type", "confidence", "created_at", "status"],
    "hypotheses": ["hypothesis_id", "hypothesis", "basis_finding_ids", "target_audience", "proposed_test", "success_metric", "required_data", "status"],
    "audit_findings": ["audit_id", "record_type", "record_id", "audit_rule", "result", "issue", "recommended_action", "audited_at"],
}
_EXPECTED_ENUMS = {
    "sources": {"access_status": _EXPECTED_ACCESS_STATUSES},
    "observations": {"confidence": _EXPECTED_CONFIDENCE_LEVELS},
    "products": {"evidence_type": _EXPECTED_EVIDENCE_TYPES, "confidence": _EXPECTED_CONFIDENCE_LEVELS},
    "competitors": {"confidence": _EXPECTED_CONFIDENCE_LEVELS},
    "videos": {"evidence_type": _EXPECTED_EVIDENCE_TYPES, "confidence": _EXPECTED_CONFIDENCE_LEVELS},
    "findings": {
        "evidence_type": _EXPECTED_EVIDENCE_TYPES,
        "confidence": _EXPECTED_CONFIDENCE_LEVELS,
        "status": ["draft", "audited", "accepted", "rejected"],
    },
    "hypotheses": {"status": ["unverified", "testing", "supported", "rejected"]},
    "audit_findings": {"result": ["pass", "warning", "fail"]},
}
_EXPECTED_FOREIGN_KEYS = {
    "sources": {},
    "observations": {"source_id": {"table": "sources", "field": "source_id"}},
    "products": {"commission_source_id": {"table": "sources", "field": "source_id"}},
    "competitors": {},
    "videos": {"competitor_id": {"table": "competitors", "field": "competitor_id"}},
    "findings": {},
    "hypotheses": {},
    "audit_findings": {},
}
_TABLE_KEYS = {"id_field", "fields", "required", "enums", "foreign_keys"}


def _definitions_path(root: Path) -> Path:
    """Return the canonical definitions path below an absolute project root."""
    return Path(root).expanduser().resolve() / _DEFINITIONS_RELATIVE_PATH


def _schema_error(path: Path, detail: str) -> ValueError:
    return ValueError(f"{path}: {detail}")


def _validate_exact_value(path: Path, key: str, actual: Any, expected: Any) -> None:
    """Require one schema element to have its prescribed type and content."""
    if type(actual) is not type(expected) or actual != expected:
        raise _schema_error(path, f"malformed key '{key}'")


def _validate_definitions(definitions: Any, path: Path) -> dict:
    if not isinstance(definitions, dict):
        raise _schema_error(path, "malformed schema: expected a JSON object")

    expected_top_level = {
        "version": _EXPECTED_VERSION,
        "evidence_types": _EXPECTED_EVIDENCE_TYPES,
        "confidence_levels": _EXPECTED_CONFIDENCE_LEVELS,
        "access_statuses": _EXPECTED_ACCESS_STATUSES,
    }
    for key, expected in expected_top_level.items():
        if key not in definitions:
            raise _schema_error(path, f"missing key '{key}'")
        _validate_exact_value(path, key, definitions[key], expected)

    if "tables" not in definitions:
        raise _schema_error(path, "missing key 'tables'")
    tables = definitions["tables"]
    if not isinstance(tables, dict) or set(tables) != set(_EXPECTED_TABLES):
        raise _schema_error(path, "malformed key 'tables'")

    for table_name, expected_fields in _EXPECTED_TABLES.items():
        table_key = f"tables.{table_name}"
        table_config = tables[table_name]
        if not isinstance(table_config, dict):
            raise _schema_error(path, f"malformed key '{table_key}'")
        for key in _TABLE_KEYS:
            if key not in table_config:
                raise _schema_error(path, f"missing key '{table_key}.{key}'")
        if set(table_config) != _TABLE_KEYS:
            raise _schema_error(path, f"malformed key '{table_key}'")

        expected_values = {
            "id_field": expected_fields[0],
            "fields": expected_fields,
            "required": _EXPECTED_REQUIRED[table_name],
            "enums": _EXPECTED_ENUMS[table_name],
            "foreign_keys": _EXPECTED_FOREIGN_KEYS[table_name],
        }
        for key, expected in expected_values.items():
            _validate_exact_value(path, f"{table_key}.{key}", table_config[key], expected)

    return definitions


def load_definitions(root: Path) -> dict:
    """Load and validate the canonical field-definition document."""
    path = _definitions_path(root)
    try:
        with path.open("r", encoding="utf-8") as handle:
            definitions = json.load(handle)
    except FileNotFoundError as error:
        raise _schema_error(path, "missing key 'field-definitions.json'") from error
    except json.JSONDecodeError as error:
        raise _schema_error(path, f"malformed JSON: {error.msg}") from error
    return _validate_definitions(definitions, path)


def table_fields(definitions: dict, table_name: str) -> list[str]:
    """Return a copy of the canonical ordered fields for a known table."""
    return list(definitions["tables"][table_name]["fields"])


def processed_csv_path(root: Path, table_name: str) -> Path:
    """Return the processed CSV location for a table without changing cwd."""
    return Path(root).expanduser().resolve() / "data" / "processed" / f"{table_name}.csv"


def utc_now() -> str:
    """Return the current time as an ISO 8601 UTC timestamp."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def read_csv_records(path: Path) -> list[dict[str, str]]:
    """Read UTF-8 CSV records while retaining empty string values."""
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv_records(path: Path, fields: list[str], records: list[dict[str, str]]) -> None:
    """Write UTF-8 CSV records using exactly the supplied column order."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        for record in records:
            writer.writerow({field: record.get(field, "") for field in fields})


def write_json(path: Path, value: object) -> None:
    """Write deterministic, indented UTF-8 JSON with a final newline."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")

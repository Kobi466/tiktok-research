"""Schema and data validation for TikTok affiliate research workspace."""

from __future__ import annotations

import argparse
import csv
import json
import sys
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Any

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.research_io import (
    load_definitions,
    processed_csv_path,
    read_csv_records,
    table_fields,
    write_json,
)

_JSON_ARRAY_FIELDS = {
    "findings": {
        "source_ids": "sources",
        "observation_ids": "observations",
    },
    "hypotheses": {
        "basis_finding_ids": "findings",
    },
}

_URL_FIELDS = {
    "sources": ["url"],
    "products": ["product_url"],
    "competitors": ["profile_url"],
    "videos": ["video_url"],
}


def _get_definitions(root: Path) -> dict:
    """Load canonical definitions from workspace or fallback to project root."""
    workspace_config = Path(root) / "config" / "field-definitions.json"
    if workspace_config.is_file():
        return load_definitions(root)
    return load_definitions(_PROJECT_ROOT)


def _val(record: dict[str, Any], key: str) -> str:
    """Safely extract stripped string from record, treating None as empty string."""
    v = record.get(key)
    return "" if v is None else str(v).strip()


def _is_valid_iso_timestamp(val: str) -> bool:
    """Check if value parses as ISO 8601, allowing trailing Z or timezone offset."""
    s = val.strip()
    if not s:
        return True
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        datetime.fromisoformat(s)
        return True
    except (ValueError, TypeError):
        return False


def _is_valid_url(val: str) -> bool:
    """Check if value has http/https scheme and non-empty network location."""
    s = val.strip()
    if not s:
        return True
    try:
        parsed = urllib.parse.urlparse(s)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def validate_workspace(root: Path) -> list[dict[str, str]]:
    """Validate all processed CSV tables in the workspace against canonical rules."""
    target_root = Path(root).expanduser().resolve()
    definitions = _get_definitions(target_root)
    tables_config = definitions["tables"]

    raw_issues: list[dict[str, Any]] = []
    table_records: dict[str, list[dict[str, str]]] = {}
    table_ids: dict[str, set[str]] = {name: set() for name in tables_config}

    # Step 1: Read all tables, verify CSV presence, header match, and collect IDs
    for table_idx, (table_name, t_config) in enumerate(tables_config.items()):
        csv_path = processed_csv_path(target_root, table_name)
        canonical_fields = table_fields(definitions, table_name)
        id_field = t_config["id_field"]

        if not csv_path.is_file():
            raw_issues.append({
                "_table_idx": table_idx,
                "_row_idx": -1,
                "table": table_name,
                "record_id": "",
                "rule": "missing_table",
                "severity": "error",
                "message": f"Missing canonical table file: {csv_path}",
            })
            continue

        try:
            with csv_path.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.reader(handle)
                header = next(reader, None)
        except Exception as err:
            raw_issues.append({
                "_table_idx": table_idx,
                "_row_idx": -1,
                "table": table_name,
                "record_id": "",
                "rule": "unreadable_csv",
                "severity": "error",
                "message": f"Failed to read CSV header from {csv_path}: {err}",
            })
            continue

        if header != canonical_fields:
            raw_issues.append({
                "_table_idx": table_idx,
                "_row_idx": -1,
                "table": table_name,
                "record_id": "",
                "rule": "header_mismatch",
                "severity": "error",
                "message": f"Header mismatch in {table_name}: expected {canonical_fields}, got {header}",
            })
            continue

        records = read_csv_records(csv_path)
        table_records[table_name] = records

        # Pre-collect IDs for foreign key validation
        for record in records:
            rec_id = _val(record, id_field)
            if rec_id:
                table_ids[table_name].add(rec_id)

    # Step 2: Validate each row within each loaded table
    for table_idx, (table_name, t_config) in enumerate(tables_config.items()):
        records = table_records.get(table_name)
        if records is None:
            continue

        id_field = t_config["id_field"]
        required_fields = set(t_config.get("required", []))
        enums_config = t_config.get("enums", {})
        foreign_keys = t_config.get("foreign_keys", {})
        all_fields = table_fields(definitions, table_name)
        date_fields = [f for f in all_fields if f.endswith("_at")]
        url_fields = _URL_FIELDS.get(table_name, [])

        seen_ids: set[str] = set()
        seen_source_urls: set[str] = set()

        for row_idx, record in enumerate(records):
            record_id = _val(record, id_field)

            # Rule 2: Primary ID duplication check
            if record_id:
                if record_id in seen_ids:
                    raw_issues.append({
                        "_table_idx": table_idx,
                        "_row_idx": row_idx,
                        "table": table_name,
                        "record_id": record_id,
                        "rule": "duplicate_id",
                        "severity": "error",
                        "message": f"Duplicate primary ID '{record_id}' in table '{table_name}'",
                    })
                else:
                    seen_ids.add(record_id)

            # Rule 10: Non-destructive source URL duplication check
            if table_name == "sources":
                url_val = _val(record, "url")
                if url_val:
                    if url_val in seen_source_urls:
                        raw_issues.append({
                            "_table_idx": table_idx,
                            "_row_idx": row_idx,
                            "table": table_name,
                            "record_id": record_id,
                            "rule": "duplicate_url",
                            "severity": "warning",
                            "message": f"Duplicate source URL found: '{url_val}'",
                        })
                    else:
                        seen_source_urls.add(url_val)

            # Rule 1: Required fields
            for req_field in required_fields:
                if not _val(record, req_field):
                    raw_issues.append({
                        "_table_idx": table_idx,
                        "_row_idx": row_idx,
                        "table": table_name,
                        "record_id": record_id,
                        "rule": "required_field",
                        "severity": "error",
                        "message": f"Missing required field '{req_field}' in table '{table_name}'",
                    })

            # Rule 3: Date/timestamp fields
            for d_field in date_fields:
                d_val = _val(record, d_field)
                if d_val and not _is_valid_iso_timestamp(d_val):
                    raw_issues.append({
                        "_table_idx": table_idx,
                        "_row_idx": row_idx,
                        "table": table_name,
                        "record_id": record_id,
                        "rule": "timestamp_format",
                        "severity": "error",
                        "message": f"Invalid ISO 8601 timestamp in field '{d_field}': '{d_val}'",
                    })

            # Rule 4: URLs
            for u_field in url_fields:
                u_val = _val(record, u_field)
                if u_val and not _is_valid_url(u_val):
                    raw_issues.append({
                        "_table_idx": table_idx,
                        "_row_idx": row_idx,
                        "table": table_name,
                        "record_id": record_id,
                        "rule": "url_absolute",
                        "severity": "error",
                        "message": f"Field '{u_field}' must be an absolute HTTP/HTTPS URL: '{u_val}'",
                    })

            # Rule 5: Enum fields
            for e_field, allowed_values in enums_config.items():
                e_val = _val(record, e_field)
                if e_val and e_val not in allowed_values:
                    raw_issues.append({
                        "_table_idx": table_idx,
                        "_row_idx": row_idx,
                        "table": table_name,
                        "record_id": record_id,
                        "rule": "enum_value",
                        "severity": "error",
                        "message": (
                            f"Invalid enum value '{e_val}' for field '{e_field}'. "
                            f"Allowed values: {allowed_values}"
                        ),
                    })

            # Rule 6: Foreign keys
            for fk_field, fk_info in foreign_keys.items():
                fk_val = _val(record, fk_field)
                if fk_val:
                    target_table = fk_info["table"]
                    target_field = fk_info["field"]
                    if fk_val not in table_ids.get(target_table, set()):
                        raw_issues.append({
                            "_table_idx": table_idx,
                            "_row_idx": row_idx,
                            "table": table_name,
                            "record_id": record_id,
                            "rule": "foreign_key",
                            "severity": "error",
                            "message": (
                                f"Referenced foreign key '{fk_val}' in field '{fk_field}' "
                                f"does not exist in {target_table}.{target_field}"
                            ),
                        })

            # Rule 7: JSON-encoded array fields
            table_json_fields = _JSON_ARRAY_FIELDS.get(table_name, {})
            for j_field, ref_table in table_json_fields.items():
                j_val = _val(record, j_field)
                if j_val:
                    try:
                        parsed = json.loads(j_val)
                        if not isinstance(parsed, list) or not all(isinstance(x, str) for x in parsed):
                            raw_issues.append({
                                "_table_idx": table_idx,
                                "_row_idx": row_idx,
                                "table": table_name,
                                "record_id": record_id,
                                "rule": "invalid_json_array",
                                "severity": "error",
                                "message": f"Field '{j_field}' must be a JSON array of strings: '{j_val}'",
                            })
                        else:
                            for ref_id in parsed:
                                if ref_id not in table_ids.get(ref_table, set()):
                                    raw_issues.append({
                                        "_table_idx": table_idx,
                                        "_row_idx": row_idx,
                                        "table": table_name,
                                        "record_id": record_id,
                                        "rule": "foreign_key",
                                        "severity": "error",
                                        "message": (
                                            f"Referenced ID '{ref_id}' in '{j_field}' "
                                            f"does not exist in target table '{ref_table}'"
                                        ),
                                    })
                    except Exception:
                        raw_issues.append({
                            "_table_idx": table_idx,
                            "_row_idx": row_idx,
                            "table": table_name,
                            "record_id": record_id,
                            "rule": "invalid_json_array",
                            "severity": "error",
                            "message": f"Field '{j_field}' failed JSON decoding: '{j_val}'",
                        })

            # Rule 8: Evidence rules
            evidence_type = _val(record, "evidence_type")
            if evidence_type == "calculated":
                if not _val(record, "calculation_method"):
                    raw_issues.append({
                        "_table_idx": table_idx,
                        "_row_idx": row_idx,
                        "table": table_name,
                        "record_id": record_id,
                        "rule": "calculation_method",
                        "severity": "error",
                        "message": "Field 'calculation_method' is required when evidence_type is 'calculated'",
                    })
            elif evidence_type == "estimate":
                if not _val(record, "limitations"):
                    raw_issues.append({
                        "_table_idx": table_idx,
                        "_row_idx": row_idx,
                        "table": table_name,
                        "record_id": record_id,
                        "rule": "estimate_limitations",
                        "severity": "error",
                        "message": "Field 'limitations' is required when evidence_type is 'estimate'",
                    })

            if table_name == "findings" and evidence_type == "hypothesis":
                status = _val(record, "status")
                if status in ("audited", "accepted"):
                    raw_issues.append({
                        "_table_idx": table_idx,
                        "_row_idx": row_idx,
                        "table": table_name,
                        "record_id": record_id,
                        "rule": "hypothesis_status",
                        "severity": "error",
                        "message": (
                            f"Finding with evidence_type='hypothesis' cannot have status '{status}'; "
                            "must be 'draft' or 'rejected'"
                        ),
                    })

            # Rule 9: Commercial and metric integrity
            if table_name == "products":
                if _val(record, "price_value") and not _val(record, "currency"):
                    raw_issues.append({
                        "_table_idx": table_idx,
                        "_row_idx": row_idx,
                        "table": table_name,
                        "record_id": record_id,
                        "rule": "missing_currency",
                        "severity": "error",
                        "message": "Field 'currency' is required when price_value is present",
                    })
                if _val(record, "commission_value") and not _val(record, "commission_source_id"):
                    raw_issues.append({
                        "_table_idx": table_idx,
                        "_row_idx": row_idx,
                        "table": table_name,
                        "record_id": record_id,
                        "rule": "missing_commission_source",
                        "severity": "error",
                        "message": "Field 'commission_source_id' is required when commission_value is present",
                    })

            if table_name == "videos":
                has_metric = any(
                    bool(_val(record, col))
                    for col in ("views_observed", "likes_observed", "comments_observed")
                )
                if has_metric and not _val(record, "observed_at"):
                    raw_issues.append({
                        "_table_idx": table_idx,
                        "_row_idx": row_idx,
                        "table": table_name,
                        "record_id": record_id,
                        "rule": "missing_observed_at",
                        "severity": "error",
                        "message": "Field 'observed_at' is required when video metrics are observed",
                    })

    # Sort issues stably: table order, row index, record_id, rule
    raw_issues.sort(key=lambda item: (
        item["_table_idx"],
        item["_row_idx"],
        item["record_id"],
        item["rule"],
    ))

    # Strip internal sorting keys
    clean_issues: list[dict[str, str]] = []
    for item in raw_issues:
        clean_issues.append({
            "table": item["table"],
            "record_id": item["record_id"],
            "rule": item["rule"],
            "severity": item["severity"],
            "message": item["message"],
        })

    return clean_issues


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for research schema and data validation."""
    parser = argparse.ArgumentParser(
        description="Validate TikTok research workspace schema and data records."
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
        help="Optional path to output JSON validation report.",
    )
    parser.add_argument(
        "--fail-on-warning",
        action="store_true",
        help="Exit with code 1 if warnings are detected even without errors.",
    )

    args = parser.parse_args(argv)
    target_root = args.root.expanduser().resolve()

    if not target_root.exists() or not target_root.is_dir():
        sys.stderr.write(f"Validation invocation error: root does not exist or is not a directory: {target_root}\n")
        return 2

    try:
        definitions = _get_definitions(target_root)
        issues = validate_workspace(target_root)
    except Exception as err:
        sys.stderr.write(f"Validation runtime error: {err}\n")
        return 2

    errors = sum(1 for i in issues if i["severity"] == "error")
    warnings = sum(1 for i in issues if i["severity"] == "warning")
    report = {
        "summary": {
            "errors": errors,
            "warnings": warnings,
            "total_issues": len(issues),
            "tables_checked": len(definitions["tables"]),
        },
        "issues": issues,
    }

    if args.output is not None:
        try:
            write_json(args.output, report)
        except Exception as err:
            sys.stderr.write(f"Failed to write report to {args.output}: {err}\n")
            return 2
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))

    if errors > 0:
        return 1
    if args.fail_on_warning and warnings > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

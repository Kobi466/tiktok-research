"""Reproducible SQLite index builder from processed CSV data."""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.research_io import (
    load_definitions,
    processed_csv_path,
    read_csv_records,
    table_fields,
)


def _get_definitions(root: Path) -> dict:
    """Load canonical definitions from workspace or fallback to project root."""
    workspace_config = Path(root) / "config" / "field-definitions.json"
    if workspace_config.is_file():
        return load_definitions(root)
    return load_definitions(_PROJECT_ROOT)


def build_index(root: Path, database: Path | None = None) -> Path:
    """Build or rebuild reproducible SQLite index atomically from processed CSV data."""
    resolved_root = Path(root).expanduser().resolve()
    if database is None:
        resolved_db = resolved_root / "data" / "research.sqlite"
    else:
        db_path = Path(database).expanduser()
        if db_path.is_absolute():
            resolved_db = db_path.resolve()
        else:
            resolved_db = (resolved_root / db_path).resolve()

    resolved_db.parent.mkdir(parents=True, exist_ok=True)
    definitions = _get_definitions(resolved_root)

    tmp_db = resolved_db.with_name(f"{resolved_db.name}.tmp")
    if tmp_db.exists():
        tmp_db.unlink()

    try:
        conn = sqlite3.connect(tmp_db)
        try:
            conn.execute("PRAGMA foreign_keys = ON;")
            for table_name in definitions["tables"]:
                fields = table_fields(definitions, table_name)
                id_field = definitions["tables"][table_name]["id_field"]
                col_defs = ", ".join(f'"{col}" TEXT' for col in fields)
                create_sql = f'CREATE TABLE "{table_name}" ({col_defs}, PRIMARY KEY ("{id_field}"));'
                conn.execute(create_sql)

                csv_path = processed_csv_path(resolved_root, table_name)
                if not csv_path.exists():
                    records: list[dict[str, str]] = []
                elif csv_path.is_dir():
                    raise IsADirectoryError(f"Expected CSV file but found directory: {csv_path}")
                elif csv_path.stat().st_size == 0:
                    records = []
                else:
                    records = read_csv_records(csv_path)

                if records:
                    quoted_cols = ", ".join(f'"{col}"' for col in fields)
                    placeholders = ", ".join("?" for _ in fields)
                    insert_sql = f'INSERT INTO "{table_name}" ({quoted_cols}) VALUES ({placeholders});'
                    rows_to_insert = [
                        tuple(
                            str(record.get(col, "") if record.get(col) is not None else "")
                            for col in fields
                        )
                        for record in records
                    ]
                    conn.executemany(insert_sql, rows_to_insert)

            conn.commit()
        finally:
            conn.close()

        tmp_db.replace(resolved_db)
    except Exception:
        if tmp_db.exists():
            tmp_db.unlink()
        raise

    return resolved_db


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for building SQLite index."""
    parser = argparse.ArgumentParser(
        description="Build a reproducible SQLite query index from processed CSV data."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Target workspace root path (default: current directory).",
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=None,
        help="Optional destination path for SQLite database (default: data/research.sqlite under root).",
    )

    args = parser.parse_args(argv)
    target_root = args.root.expanduser().resolve()

    if not target_root.exists() or not target_root.is_dir():
        sys.stderr.write(
            f"Build index invocation error: root does not exist or is not a directory: {target_root}\n"
        )
        return 2

    try:
        db_path = build_index(root=target_root, database=args.database)
    except Exception as err:
        sys.stderr.write(f"Build index error: {err}\n")
        return 2

    print(f"Database: {db_path}")
    print("Indexed tables:")
    conn = sqlite3.connect(db_path)
    try:
        definitions = _get_definitions(target_root)
        for table in definitions["tables"]:
            count = conn.execute(f'SELECT count(*) FROM "{table}"').fetchone()[0]
            print(f"  - {table}: {count}")
    finally:
        conn.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())

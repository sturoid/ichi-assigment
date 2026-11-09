"""CLI:  (from the src/ directory)

  python -m services.htmlParser <file.html> --as matrix --spec ibc2018-504.3 -o out.json
  python -m services.htmlParser <file.html> --as records
  python -m services.htmlParser <file.html> --as kv
  python -m services.htmlParser <file.html> --as grid
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys

from . import SCHEMA_VERSION, SPECS, KeyValueSheet, MatrixTable, RecordTable, parse_tables


def build(path: pathlib.Path, kind: str, spec: str | None, table: int, include_grid: bool) -> dict:
    data = path.read_bytes()
    grids = parse_tables(data.decode("utf-8"))
    if not grids:
        raise SystemExit(f"{path}: no <table> found")
    grid = grids[table]
    if kind == "matrix":
        if not spec:
            raise SystemExit(f"--as matrix needs --spec (one of {sorted(SPECS)})")
        body = MatrixTable(grid, SPECS[spec]).to_dict(include_grid)
    elif kind == "records":
        body = RecordTable(grid).to_dict(include_grid)
    elif kind == "kv":
        body = KeyValueSheet(grid).to_dict(include_grid)
    else:
        body = {"kind": "grid", "table_index": grid.table_index, **grid.to_dict()}
    return {
        "schema_version": SCHEMA_VERSION,
        "source_file": path.name,
        "source_sha256": hashlib.sha256(data).hexdigest(),
        "tables_in_file": len(grids),
        **body,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m services.htmlParser")
    ap.add_argument("file", type=pathlib.Path)
    ap.add_argument("--as", dest="kind", choices=["grid", "matrix", "records", "kv"], default="grid")
    ap.add_argument("--spec", choices=sorted(SPECS))
    ap.add_argument("--table", type=int, default=0, help="which <table> in the file (default 0)")
    ap.add_argument("--no-grid", action="store_true", help="omit the resolved grid from the output")
    ap.add_argument("-o", "--out", type=pathlib.Path)
    a = ap.parse_args(argv)
    out = build(a.file, a.kind, a.spec, a.table, not a.no_grid)
    text = json.dumps(out, indent=2, ensure_ascii=False)
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(text + "\n", encoding="utf-8")
        print(f"wrote {a.out} ({len(out.get('warnings', []))} warnings)", file=sys.stderr)
    else:
        sys.stdout.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

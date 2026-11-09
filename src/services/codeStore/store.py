"""Build the code store from a manifest, and answer lookups with an explicit status.

The store is exact. It never maps project wording to table values ("R-3" is not
"R"); that is a separate, rule-based resolver whose every rule cites code text.
See DESIGN.md for the contract.
"""
from __future__ import annotations

import copy
import hashlib
import itertools
import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path

from services.htmlParser import SPECS, MatrixTable, parse_tables, warning_dicts
from services.htmlParser.matrix import normalize_key

from .table_notes import load_table_notes

STORE_SCHEMA_VERSION = "1.0"
AUTHORITIES = ("code_text", "challenge_brief", "project_submitted", "project_decision")
DOC_STATUSES = ("available", "unavailable")
LOOKUP_STATUSES = ("found", "not_found", "unavailable", "invalid_input")


class StoreError(ValueError):
    pass


def slug(identifier: str) -> str:
    """A filesystem-safe name for an id: 'IBC:2018:T504.3' -> 'IBC-2018-T504.3' (Windows forbids ':')."""
    return re.sub(r"[^A-Za-z0-9.\-]+", "-", identifier).strip("-")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dumps(obj) -> str:
    """The one serialisation used for store files, so equal content gives equal bytes."""
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #

def cell_id(pid: str, row_labels: dict, order: list[str], column: str) -> str:
    parts = [f"{d}={row_labels[d]}" for d in order[:-1]] + [f"{order[-1]}={column}"]
    return f"{pid}[{';'.join(parts)}]"


def cell_keys(dims: dict, order: list[str]) -> list[str]:
    """The lookup keys a cell must carry, derived from its dims alone."""
    atoms = [dims[d] if isinstance(dims[d], list) else [dims[d]] for d in order]
    return ["|".join(normalize_key(x) for x in combo) for combo in itertools.product(*atoms)]


_RESERVED = ("|", ";", "=", "[", "]")


def _table_provision(doc: dict, file_entry: dict, base: Path) -> tuple[dict, dict]:
    parse = file_entry["parse"]
    spec = SPECS[parse["spec"]]
    if spec.table_id != doc["id"]:
        raise StoreError(f"spec {parse['spec']!r} has table_id {spec.table_id!r}, manifest says {doc['id']!r}")
    for fld, spec_val in (("short_name", spec.short_name), ("title", spec.title)):
        if doc.get(fld) and spec_val and doc[fld] != spec_val:
            raise StoreError(f"{doc['id']}: {fld} is {spec_val!r} in the spec but {doc[fld]!r} in the manifest")
    src = base / file_entry["path"]
    grids = parse_tables(src.read_text(encoding="utf-8"))
    grid = grids[parse.get("table", 0)]
    m = MatrixTable(grid, spec)
    cells = []
    for rec in m.cells:
        printed = [*rec["row_labels"].values(), rec[spec.col_dim]]
        bad = [t for t in printed if any(ch in t for ch in _RESERVED)]
        if bad:
            raise StoreError(f"{doc['id']}: label(s) {bad} contain a reserved character {_RESERVED}; "
                             "ids and keys would be ambiguous")
        cells.append({
            "id": cell_id(doc["id"], rec["row_labels"], [*spec.row_dims, spec.col_dim], rec[spec.col_dim]),
            "dims": {**{d: rec[d] for d in spec.row_dims}, spec.col_dim: rec[spec.col_dim]},
            "value": rec["value"],
            "value_kind": rec["value_kind"],
            "value_text": rec["value_text"],
            "unit": rec["unit"],
            "printed": {"row_labels": rec["row_labels"], "column_header_path": rec["column_header_path"]},
            "conditions": rec["conditions"],
            "authority": doc["authority"],
            "source": {"document": doc["id"], "file": file_entry["path"],
                       "grid_row": rec["src"]["value"]["grid_row"], "grid_col": rec["src"]["value"]["grid_col"],
                       "inherited": rec["src"]["value"]["inherited"]},
            "keys": rec["keys"],
        })
    grid_file = f"grids/{slug(doc['id'])}.grid.json"
    provision = {
        "id": doc["id"],
        "kind": "table",
        "short_name": spec.short_name or doc.get("short_name", doc["id"]),
        "title": spec.title,
        "unit": spec.unit,
        "dimensions": {
            "order": [*spec.row_dims, spec.col_dim],
            "values": m.dimension_values(),
            "printed_headers": {"row_dims": m.row_dim_headers, "column_prefix": m.column_header_prefix},
            "value_tokens": spec.tokens,
        },
        "table_footnotes": [{"mark": mk, "source": spec.table_footnotes_source} for mk in spec.table_footnotes],
        # set true by _attach_notes when the manifest lists the table's notes file
        "conditions_loaded": False,
        "lookup_key_format": "|".join(f"<{d}>" for d in [*spec.row_dims, spec.col_dim])
                             + " (upper-cased, single spaces)",
        "cells": cells,
        "index": {k: c["id"] for c in cells for k in c["keys"]},
        "warnings": warning_dicts(m.warnings),
        "review_items": m.review_items,
        "grid_file": grid_file,
        "source": {"file": file_entry["path"], "table_index": grid.table_index, "tables_in_file": len(grids)},
    }
    sidecar = {"provision": doc["id"], "file": file_entry["path"], **grid.to_dict(), "layout": m.layout.to_dict()}
    return provision, sidecar


def _attach_notes(prov: dict, doc: dict, file_entry: dict, base: Path, documents: list[dict]) -> None:
    """Fill every condition's text from the notes file and mark the provision loaded.
    A mark printed in the table with no footnote in the notes is a build error."""
    notes = load_table_notes(base / file_entry["path"], file_entry["path"], documents)
    missing = sorted({c["mark"] for cell in prov["cells"] for c in cell["conditions"]} - set(notes["footnotes"]))
    if missing:
        raise StoreError(f"{doc['id']}: footnote mark(s) {missing} are printed in the table but not in {file_entry['path']}")
    for cell in prov["cells"]:
        for c in cell["conditions"]:
            c["text"] = notes["footnotes"][c["mark"]]["text"]
    prov["notes"] = notes
    prov["conditions_loaded"] = True


def build_store(manifest_path: Path) -> tuple[dict, dict[str, dict]]:
    """Return (store, sidecars). Sidecar keys are paths relative to the store file."""
    manifest_path = Path(manifest_path)
    base = manifest_path.parent
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    documents, provisions, sidecars = [], {}, {}
    seen: set[str] = set()
    for doc in manifest["documents"]:
        if doc["id"] in seen:
            raise StoreError(f"duplicate document id {doc['id']!r}")
        seen.add(doc["id"])
        d = {k: v for k, v in doc.items() if k != "files"}
        if doc["status"] == "available":
            d["files"] = []
            for f in doc.get("files", []):
                path = base / f["path"]
                if not path.is_file():
                    raise StoreError(f"{doc['id']}: file {f['path']!r} not found")
                d["files"].append({**f, "sha256": _sha256(path)})
                if doc["kind"] == "code_table" and f.get("parse", {}).get("as") == "matrix":
                    prov, side = _table_provision(doc, f, base)
                    provisions[doc["id"]] = prov
                    sidecars[prov["grid_file"]] = side
            for f in doc.get("files", []):
                if f.get("parse", {}).get("as") == "table_notes":
                    if doc["id"] not in provisions:
                        raise StoreError(f"{doc['id']}: table notes listed before (or without) the table body")
                    _attach_notes(provisions[doc["id"]], doc, f, base, manifest["documents"])
        documents.append(d)
    store = {
        "schema_version": STORE_SCHEMA_VERSION,
        "manifest": {"file": manifest_path.name, "sha256": _sha256(manifest_path),
                     "project": manifest.get("project")},
        "documents": documents,
        "provisions": provisions,
    }
    return store, sidecars


def write_store(manifest_path: Path, out_dir: Path) -> Path:
    store, sidecars = build_store(manifest_path)
    out_dir = Path(out_dir)
    (out_dir / "grids").mkdir(parents=True, exist_ok=True)
    for rel, side in sidecars.items():
        (out_dir / rel).write_text(dumps(side), encoding="utf-8", newline="\n")
    out = out_dir / "store.json"
    out.write_text(dumps(store), encoding="utf-8", newline="\n")
    return out


# --------------------------------------------------------------------------- #
# Lookup
# --------------------------------------------------------------------------- #

@dataclass
class LookupResult:
    status: str  # found | not_found | unavailable | invalid_input
    query: dict
    errors: list[dict] = field(default_factory=list)
    value: object = None
    value_kind: str | None = None
    value_text: str | None = None
    unit: str | None = None
    citation: dict | None = None
    conditions: list[dict] = field(default_factory=list)
    conditions_complete: bool = False
    # why a found value is not yet enough for a verdict, e.g. footnote text not loaded
    limitations: list[dict] = field(default_factory=list)
    authority: str | None = None
    source: dict | None = None
    parser_notes: dict = field(default_factory=dict)  # the provision's parser warnings and review items

    @property
    def found(self) -> bool:
        return self.status == "found"

    @property
    def is_complete(self) -> bool:
        """True only when a value was found AND nothing is known to be missing for it.
        A check must not issue Pass/Fail on a result that is not complete without
        saying what is missing."""
        return self.status == "found" and not self.limitations

    @property
    def numeric_limit(self) -> float | None:
        """The value as a number to compare against: inf for 'unlimited', None when the
        value is not numeric (or nothing was found). Avoids `actual <= None` mistakes."""
        if self.status != "found":
            return None
        if self.value_kind == "unlimited":
            return math.inf
        if self.value_kind == "number":
            return float(self.value)
        return None

    def error_codes(self) -> list[str]:
        return [e["code"] for e in self.errors]

    def to_dict(self) -> dict:
        d = {"status": self.status, "query": self.query, "errors": self.errors}
        if self.status == "found":
            d.update({"value": self.value, "value_kind": self.value_kind, "value_text": self.value_text,
                      "unit": self.unit, "citation": self.citation, "conditions": self.conditions,
                      "conditions_complete": self.conditions_complete, "limitations": self.limitations,
                      "is_complete": self.is_complete, "numeric_limit": _json_number(self.numeric_limit),
                      "authority": self.authority, "source": self.source, "parser_notes": self.parser_notes})
        return d


def _json_number(x):
    return "inf" if x == math.inf else x


class Store:
    def __init__(self, data: dict):
        self.data = data
        self.documents = {d["id"]: d for d in data["documents"]}
        self.provisions = data["provisions"]
        self._cells = {pid: {c["id"]: c for c in p["cells"]} for pid, p in self.provisions.items()}
        self._norm_values = {pid: {d: {normalize_key(v) for v in vals} for d, vals in p["dimensions"]["values"].items()}
                             for pid, p in self.provisions.items()}

    @classmethod
    def load(cls, path: Path, manifest: Path | None = None) -> "Store":
        """Load a built store. Pass ``manifest`` to verify it: the store is rebuilt from
        the manifest and its sources and must match byte for byte, so a stale or
        edited store.json is refused. Without it the store is only shape-validated."""
        from .validate import validate_store
        text = Path(path).read_text(encoding="utf-8")
        data = json.loads(text)
        problems = validate_store(data)
        if problems:
            raise StoreError(f"{path}: {len(problems)} validation problem(s); first: {problems[0]}")
        if manifest is not None and dumps(build_store(manifest)[0]) != text:
            raise StoreError(f"{path} does not match a fresh build from {manifest} (stale or edited)")
        return cls(data)

    @classmethod
    def from_manifest(cls, manifest_path: Path) -> "Store":
        return cls(build_store(manifest_path)[0])

    def lookup(self, provision_id: str, /, **dims) -> LookupResult:
        """Exact lookup. Never raises for bad input; the status says what happened.

        found          the cell exists
        not_found      every value is valid, but the table has no cell for the combination
        unavailable    the document is listed but we don't have it, or it is not loaded yet
        invalid_input  missing_dimension / unknown_dimension / unknown_value / invalid_type /
                       unknown_provision (every problem is listed, not just the first)
        """
        query = {"provision": provision_id, "dims": {k: (v if isinstance(v, (str, type(None))) else repr(v))
                                                      for k, v in dims.items()}}
        if not isinstance(provision_id, str):
            return LookupResult("invalid_input", query, [{
                "code": "unknown_provision", "message": f"provision id must be text, got {type(provision_id).__name__}"}])
        prov = self.provisions.get(provision_id)
        if prov is None:
            doc = self.documents.get(provision_id)
            if doc is None:
                return LookupResult("invalid_input", query, [{
                    "code": "unknown_provision", "message": f"{provision_id!r} is not in the manifest"}])
            if doc["status"] == "unavailable":
                return LookupResult("unavailable", query, [{
                    "code": "unavailable_document", "document": provision_id,
                    "message": f"{provision_id} ({doc.get('title', '')}) is listed but we do not have it",
                    "referenced_by": doc.get("referenced_by", [])}])
            return LookupResult("unavailable", query, [{
                "code": "not_loaded", "document": provision_id,
                "message": f"{provision_id} is available but has no lookup provision loaded yet"}])

        order = prov["dimensions"]["order"]
        values = prov["dimensions"]["values"]
        errors: list[dict] = []
        for d in order:
            v = dims.get(d)
            if v is None or (isinstance(v, str) and not v.strip()):
                errors.append({"code": "missing_dimension", "dimension": d,
                               "message": f"no value given for {d!r}"})
            elif not isinstance(v, str):
                errors.append({"code": "invalid_type", "dimension": d, "value": repr(v),
                               "message": f"{d!r} must be text, got {type(v).__name__}"})
            elif normalize_key(v) not in self._norm_values[provision_id][d]:
                errors.append({"code": "unknown_value", "dimension": d, "value": v, "allowed": values[d],
                               "message": f"{v!r} is not a {d} in {prov['short_name']}"})
        for d in dims:
            if d not in order:
                errors.append({"code": "unknown_dimension", "dimension": d, "allowed": order,
                               "message": f"{prov['short_name']} has no dimension {d!r}"})
        if errors:
            return LookupResult("invalid_input", query, errors)

        key = "|".join(normalize_key(dims[d]) for d in order)
        cid = prov["index"].get(key)
        if cid is None:
            return LookupResult("not_found", query, [{
                "code": "no_cell", "key": key,
                "message": f"{prov['short_name']} has no cell for {key} (each value exists, the combination does not)"}])
        cell = copy.deepcopy(self._cells[provision_id][cid])  # results never alias the store
        limitations = []
        if cell["conditions"] and not prov["conditions_loaded"]:
            limitations.append({
                "code": "conditions_text_not_loaded",
                "marks": [c["mark"] for c in cell["conditions"]],
                "message": "footnotes apply to this cell but their text is not loaded; they may change or "
                           "qualify the value"})
        notes = prov.get("notes", {}).get("footnotes", {})
        for c in cell["conditions"]:
            fn = notes.get(c["mark"])
            if fn:  # where the footnote text is printed, and which documents it points to
                c["source"] = copy.deepcopy(fn["source"])
                c["references"] = copy.deepcopy(fn["references"])
        return LookupResult(
            "found", query, [],
            value=cell["value"], value_kind=cell["value_kind"], value_text=cell["value_text"], unit=cell["unit"],
            citation=self.citation(prov, cell), conditions=cell["conditions"],
            conditions_complete=prov["conditions_loaded"], limitations=limitations, authority=cell["authority"],
            source={**cell["source"], "cell_id": cell["id"]},
            parser_notes=copy.deepcopy({"warnings": prov["warnings"], "review_items": prov["review_items"]}))

    @staticmethod
    def citation(prov: dict, cell: dict) -> dict:
        row = " / ".join(f"`{t}`" for t in cell["printed"]["row_labels"].values())
        col_dim = prov["dimensions"]["order"][-1]
        col = cell["dims"][col_dim]
        return {
            "provision": prov["id"],
            "short_name": prov["short_name"],
            "title": prov["title"],
            "row_labels": cell["printed"]["row_labels"],
            "column": col,
            "column_header_path": cell["printed"]["column_header_path"],
            "cell_id": cell["id"],
            "text": f"{prov['short_name']}, row {row}, column `{col}`",
        }

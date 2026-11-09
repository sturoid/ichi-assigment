"""Layer 3a: MatrixTable - code tables where a value sits at (row labels x column header).

Every value cell becomes a self-describing record (all dimensions named, footnotes
merged, provenance attached), plus an exact-match index so a lookup never depends
on table geometry. Built for "law" tables, so ambiguity is an error, not a guess.
"""
from __future__ import annotations

import itertools
import re
from dataclasses import dataclass, field
from typing import Callable

from .grid import Grid
from .headers import Layout, detect_layout
from .notes import W, warning_dicts

_NUMBER = re.compile(r"^-?\d+(?:\.\d+)?$")


class MatrixError(ValueError):
    pass


@dataclass
class MatrixSpec:
    """Declares how to read one code table. Explicit on purpose: code tables are few and
    are law, so the dimensions are stated once and verified, rather than guessed."""

    table_id: str  # the provision id used in the store, e.g. "IBC:2018:T504.3"
    row_dims: list[str]  # one name per stub (row-label) column, left to right
    col_dim: str = "column"
    title: str = ""
    unit: str | None = None
    stub_cols: int | None = None  # defaults to len(row_dims)
    multi_value_dims: set[str] = field(default_factory=set)  # labels like "A, B, E" -> atoms
    column_key: Callable[[list[str]], str] | None = None  # header path -> canonical key
    tokens: dict[str, str] = field(default_factory=dict)  # non-numeric values, e.g. {"UL": "unlimited"}
    header_rows: int | None = None  # override header detection
    short_name: str = ""  # how a citation names the table, e.g. "Table 504.3"
    # footnote marks printed on the table title (they apply to every cell). The scrape
    # may drop the title, so they are declared here with the line that shows them.
    table_footnotes: list[str] = field(default_factory=list)
    table_footnotes_source: dict | None = None  # {"file": ..., "line": ...}


def normalize_key(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().upper()


def guess_stub_cols(layout: Layout) -> int:
    """Leading columns whose header path is shallower than the deepest one.
    In Table 504.3 the value columns are TYPE OF CONSTRUCTION / TYPE x / A|B (depth 3),
    while OCCUPANCY (depth 1) and SEE FOOTNOTES (depth 2) are row labels."""
    depth = max((len(c.path) for c in layout.columns), default=0)
    n = 0
    for col in layout.columns:
        if len(col.path) < depth:
            n += 1
        else:
            break
    return n


def _split_atoms(label: str) -> list[str]:
    return [a.strip() for a in label.split(",") if a.strip()]


def _common_prefix(paths: list[list[str]]) -> list[str]:
    prefix: list[str] = []
    for level in zip(*paths):
        if all(x == level[0] for x in level):
            prefix.append(level[0])
        else:
            break
    return prefix


class MatrixTable:
    def __init__(self, grid: Grid, spec: MatrixSpec):
        self.spec = spec
        self.grid = grid
        self.layout = detect_layout(grid, spec.header_rows)
        self.warnings: list[str] = list(grid.warnings) + self.layout.warnings
        self.review_items: list[dict] = list(self.layout.review_items)
        self.cells: list[dict] = []
        self.index: dict[str, int] = {}
        self._build()

    # ------------------------------------------------------------------ build
    def _build(self) -> None:
        spec, grid, layout = self.spec, self.grid, self.layout
        stub = spec.stub_cols if spec.stub_cols is not None else len(spec.row_dims)
        if stub != len(spec.row_dims):
            raise MatrixError(f"spec has {len(spec.row_dims)} row_dims but stub_cols={stub}")
        guessed = guess_stub_cols(layout)
        if guessed != stub:
            self.warnings.append(W("matrix.stub_mismatch", f"header structure suggests {guessed} row-label columns; spec says {stub}"))
        if not layout.data_rows:
            raise MatrixError("no data rows found")

        value_cols = layout.columns[stub:]
        if any(not c.path for c in value_cols):
            raise MatrixError(f"value columns without a header: {[c.id for c in value_cols if not c.path]}")
        prefix = _common_prefix([c.path for c in value_cols])
        self.column_header_prefix = prefix
        self.column_keys: list[str] = []
        for col in value_cols:
            rel = col.path[len(prefix):] or col.path
            key = spec.column_key(rel) if spec.column_key else " / ".join(rel)
            self.column_keys.append(key)
        dupes = {k for k in self.column_keys if self.column_keys.count(k) > 1}
        if dupes:
            raise MatrixError(f"column keys are not unique: {sorted(dupes)}")
        self.row_dim_headers = {d: layout.columns[i].label for i, d in enumerate(spec.row_dims)}

        for r in layout.data_rows:
            labels: dict[str, dict] = {}
            for i, dim in enumerate(spec.row_dims):
                s = grid.slot(r, i)
                if s is None or s.cell.is_empty:
                    raise MatrixError(f"row {r}: missing label for {dim!r}")
                atoms = _split_atoms(s.text) if dim in spec.multi_value_dims else [s.text]
                labels[dim] = {"label": s.text, "atoms": atoms, "footnotes": s.cell.footnotes,
                               "src": s.provenance()}
            for col, key in zip(value_cols, self.column_keys):
                s = grid.slot(r, col.index)
                if s is None:
                    self.warnings.append(W("matrix.missing_cell", f"row {r} col {col.index}: no cell"))
                    continue
                self._add_record(r, labels, col, key, s)

    def _parse_value(self, text: str) -> tuple[object, str]:
        if text in self.spec.tokens:
            return None, self.spec.tokens[text]
        if _NUMBER.match(text):
            f = float(text)
            return (int(f) if f.is_integer() else f), "number"
        return None, "empty" if text == "" else "text"

    def _add_record(self, r, labels, col, col_key, slot) -> None:
        spec = self.spec
        value, kind = self._parse_value(slot.text)
        if kind in ("empty", "text"):
            self.warnings.append(W("matrix.unexpected_value", f"row {r} col {col.index}: unexpected value {slot.text!r}"))
        footnotes: list[str] = []
        for lab in labels.values():
            footnotes += [f for f in lab["footnotes"] if f not in footnotes]
        footnotes += [f for f in slot.cell.footnotes if f not in footnotes]
        # where each footnote mark is printed: on the title, a row label, or the cell
        conditions = [{"kind": "footnote", "mark": m, "attached_to": "table", "text": None}
                      for m in spec.table_footnotes]
        for dim, lab in labels.items():
            conditions += [{"kind": "footnote", "mark": m, "attached_to": f"row_label:{dim}", "text": None}
                           for m in lab["footnotes"]]
        conditions += [{"kind": "footnote", "mark": m, "attached_to": "cell", "text": None}
                       for m in slot.cell.footnotes]

        rec: dict = {"table_id": spec.table_id}
        for dim, lab in labels.items():
            rec[dim] = lab["atoms"] if dim in spec.multi_value_dims else lab["label"]
        rec[spec.col_dim] = col_key
        rec.update({
            "value": value,
            "value_kind": kind,
            "value_text": slot.text,
            "unit": spec.unit,
            "footnotes": footnotes,
            "conditions": conditions,
            "row_labels": {d: lab["label"] for d, lab in labels.items()},
            "column_header_path": col.path,
            "src": {
                "value": slot.provenance(),
                "row_labels": {d: lab["src"] for d, lab in labels.items()},
            },
        })
        idx = len(self.cells)
        rec["keys"] = []
        atom_lists = [labels[d]["atoms"] for d in spec.row_dims]
        for combo in itertools.product(*atom_lists):
            key = "|".join(normalize_key(x) for x in (*combo, col_key))
            if key in self.index:
                prev = self.cells[self.index[key]]
                raise MatrixError(f"ambiguous key {key!r}: grid rows {prev['src']['value']['grid_row']} and {r}")
            self.index[key] = idx
            rec["keys"].append(key)
        self.cells.append(rec)

    def sentence(self, rec: dict) -> str:
        return render_sentence(rec, self.spec)

    # ----------------------------------------------------------------- lookup
    def key_for(self, **dims: str) -> str:
        order = [*self.spec.row_dims, self.spec.col_dim]
        missing = [d for d in order if d not in dims]
        extra = [d for d in dims if d not in order]
        if missing or extra:
            raise KeyError(f"lookup needs exactly {order}; missing={missing} extra={extra}")
        return "|".join(normalize_key(dims[d]) for d in order)

    def lookup(self, **dims: str) -> dict | None:
        """Exact match only. Returns the cell record or None. Mapping project wording
        (e.g. 'R-3' -> 'R', 'NFPA 13D' -> 'S13D') is the caller's job, not the table's."""
        i = self.index.get(self.key_for(**dims))
        return None if i is None else self.cells[i]

    def dimension_values(self) -> dict[str, list[str]]:
        out: dict[str, list[str]] = {d: [] for d in self.spec.row_dims}
        for rec in self.cells:
            for d in self.spec.row_dims:
                vals = rec[d] if isinstance(rec[d], list) else [rec[d]]
                out[d] += [v for v in vals if v not in out[d]]
        out[self.spec.col_dim] = list(self.column_keys)
        return out

    def to_dict(self, include_grid: bool = True) -> dict:
        d = {
            "kind": "matrix",
            "table_index": self.grid.table_index,
            "table_id": self.spec.table_id,
            "short_name": self.spec.short_name,
            "title": self.spec.title,
            "unit": self.spec.unit,
            "dimensions": {
                "order": [*self.spec.row_dims, self.spec.col_dim],
                "values": self.dimension_values(),
                "row_dim_headers": self.row_dim_headers,
                "column_header_prefix": self.column_header_prefix,
            },
            "value_tokens": self.spec.tokens,
            "lookup_key_format": "|".join(f"<{d}>" for d in [*self.spec.row_dims, self.spec.col_dim])
                                 + " (upper-cased, single spaces)",
            "cells": self.cells,
            "index": self.index,
            "layout": self.layout.to_dict(),
            "warnings": warning_dicts(self.warnings),
            "review_items": self.review_items,
        }
        if include_grid:
            d["grid"] = self.grid.to_dict()
        return d


def render_sentence(rec: dict, spec: MatrixSpec) -> str:
    """One readable line per cell, built on demand (not stored): e.g.
    'Table 504.3 | occupancy: R; sprinkler: S13D; construction: V-B -> 40 ft [footnotes: h]'."""
    labels = "; ".join(f"{d}: {t}" for d, t in rec["row_labels"].items())
    kind = rec["value_kind"]
    shown = rec["value_text"] + ("" if kind == "number" else f" ({kind})")
    unit = f" {spec.unit}" if spec.unit and kind == "number" else ""
    name = spec.short_name or spec.table_id
    marks = [c["mark"] for c in rec.get("conditions", [])]
    return (f"{name} | {labels}; {spec.col_dim}: {rec[spec.col_dim]} -> {shown}{unit}"
            + (f" [footnotes: {', '.join(marks)}]" if marks else ""))

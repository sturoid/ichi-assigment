"""Layer 3b/3c: project-document tables.

RecordTable  - one record per data row, cells keyed by column id (never by header text,
               because OCR'd schedules repeat headers, e.g. two "TYPE" columns).
KeyValueSheet - label/value sheets such as a code analysis (2-column, paired, or
               'LABEL: VALUE' in one column).

Both keep raw text and line-break join candidates. Neither guesses meanings: mapping
"FIRE SPRINKLE RS" to a canonical field, or the second TYPE column to "type mark",
belongs to a later, vocabulary-driven layer.
"""
from __future__ import annotations

from .grid import _LINE_BREAK, Grid, Slot, collapse_ws
from .notes import W, warning_dicts
from .headers import Layout, _is_unit_like, _is_value_like, detect_layout, review_item


def _cell_view(s: Slot | None) -> dict:
    if s is None:
        return {"text": "", "raw": "", "missing": True}
    d = {"text": s.text, "raw": s.cell.raw}
    if s.cell.footnotes:
        d["footnotes"] = s.cell.footnotes
    if s.cell.join_candidates:
        d["join_candidates"] = s.cell.join_candidates
    d["src"] = s.provenance()
    return d


class RecordTable:
    def __init__(self, grid: Grid, header_rows: int | None = None):
        self.grid = grid
        self.layout: Layout = detect_layout(grid, header_rows)
        self.warnings = list(grid.warnings) + self.layout.warnings
        self.review_items = list(self.layout.review_items)
        if not self.layout.header_rows:
            self.warnings.append(W("records.no_header", "no header rows detected; columns are identified by position only"))
        for col in self.layout.columns:
            if col.duplicate_of:
                self.warnings.append(W("records.duplicate_header", f"column {col.id} header {col.label!r} duplicates {col.duplicate_of}"))
            if not col.path:
                self.warnings.append(W("records.empty_header", f"column {col.id} has no header text"))
        self.rows = [
            {"grid_row": r, "cells": {col.id: _cell_view(grid.slot(r, col.index)) for col in self.layout.columns}}
            for r in self.layout.data_rows
        ]

    def column(self, label: str) -> list[str]:
        """Column ids whose header label matches (case/space-insensitive). May return several."""
        want = " ".join(label.split()).upper()
        return [c.id for c in self.layout.columns if c.label.upper() == want]

    def to_dict(self, include_grid: bool = True) -> dict:
        d = {
            "kind": "records",
            "table_index": self.grid.table_index,
            "title": [self.grid.slot(r, 0).text for r in self.layout.title_rows],
            "columns": [c.to_dict() for c in self.layout.columns],
            "rows": self.rows,
            "layout": self.layout.to_dict(),
            "warnings": warning_dicts(self.warnings),
            "review_items": self.review_items,
        }
        if include_grid:
            d["grid"] = self.grid.to_dict()
        return d


_NOT_LABEL_PREFIXES = ("SEE ", "PER ", "REF", "IBC", "TABLE", "SECTION", "NOTE")


def _looks_like_label(text: str) -> bool:
    """A word label such as 'CONSTRUCTION TYPE', not 'SF', 'IBC 304' or 'SEE A3.1'."""
    t = " ".join(text.split()).upper()
    return (not _is_unit_like(t) and not any(ch.isdigit() for ch in t)
            and not t.startswith(_NOT_LABEL_PREFIXES) and sum(ch.isalpha() for ch in t) >= 3)


class KeyValueSheet:
    """Label/value sheets. Three layouts are recognised, and the one used is
    recorded in ``mode``:

    label_value   label in column 0, value in the rest (the usual 2-column sheet)
    paired        label, value, label, value ... across the row: an even width of
                  4+ where every label column is text, not a value
    inline_colon  one column, "LABEL: VALUE" in each cell, split on the first ':'.
                  Leading cells without ':' are the title.
    """

    def __init__(self, grid: Grid):
        self.grid = grid
        self.layout: Layout = detect_layout(grid, header_rows=0)
        self.warnings = list(grid.warnings) + self.layout.warnings
        self.review_items = list(self.layout.review_items)
        self.title = [grid.slot(r, 0).text for r in self.layout.title_rows]
        self.entries: list[dict] = []
        if grid.n_cols == 1:
            self.mode = "inline_colon"
            self._inline_colon()
        elif self._is_paired():
            self.mode = "paired"
            self._paired()
        else:
            self.mode = "label_value"
            self._label_value()
        labels = [e["label"]["text"].upper() for e in self.entries]
        for lab in sorted({x for x in labels if labels.count(x) > 1}):
            self.warnings.append(W("kv.duplicate_label", f"label {lab!r} appears more than once"))

    # -- layouts --
    def _label_value(self) -> None:
        grid = self.grid
        for r in self.layout.data_rows:
            cells = grid.origin_cells_in_row(r)
            non_empty = [c for c in cells if not c.is_empty]
            if len(cells) < 2:
                self.warnings.append(W("kv.short_row", f"row {r}: expected label + value, found {len(cells)} cell(s)"))
            key_slot = grid.slot(r, 0)
            value_cells = []
            for c in range(1, grid.n_cols):
                sl = grid.slot(r, c)
                if sl is not None and sl.cell.id != key_slot.cell.id and all(v.cell.id != sl.cell.id for v in value_cells):
                    value_cells.append(sl)
            if not non_empty:
                continue
            self.entries.append({
                "grid_row": r,
                "label": _cell_view(key_slot),
                "value": _cell_view(value_cells[0]) if len(value_cells) == 1
                else {"text": " ".join(v.text for v in value_cells), "parts": [_cell_view(v) for v in value_cells]},
            })

    def _is_paired(self) -> bool:
        grid = self.grid
        if grid.n_cols < 4 or grid.n_cols % 2:
            return False
        saw_second_pair = False
        later_labels: list[str] = []
        for r in self.layout.data_rows:
            for c in range(0, grid.n_cols, 2):
                lab, val = grid.slot(r, c), grid.slot(r, c + 1)
                if lab is None or val is None or lab.cell.id == val.cell.id:
                    return False  # a cell straddles a label/value pair
                if c > 0 and lab.cell.id == grid.slot(r, c - 1).cell.id:
                    return False  # a cell straddles two pairs
                if not lab.cell.is_empty and _is_value_like(lab.cell):
                    return False  # a "label" column holds values: not pairs
                if c > 0 and not lab.cell.is_empty:
                    if not _looks_like_label(lab.cell.text):
                        return False  # a unit, a code reference or a number: not a label
                    saw_second_pair = True
                    later_labels.append(lab.text.upper())
        # a repeated "label" in a later column (FT, FT, SF ...) is a unit or note
        # column of a label | value | unit sheet, not a second label column
        return saw_second_pair and len(later_labels) == len(set(later_labels))

    def _paired(self) -> None:
        grid = self.grid
        self.review_items.append(review_item(
            "kv.paired",
            f"read as {grid.n_cols // 2} label/value pairs per row (columns 0/1, 2/3 ...): every "
            "even column holds distinct word labels (no units, numbers or code references). If the "
            "extra columns are units or notes for column 1, this reading is wrong.",
            cols=list(range(0, grid.n_cols, 2)), chosen="paired", alternative="label_value"))
        for r in self.layout.data_rows:
            for c in range(0, grid.n_cols, 2):
                lab, val = grid.slot(r, c), grid.slot(r, c + 1)
                if lab.cell.is_empty and val.cell.is_empty:
                    continue
                if lab.cell.is_empty:
                    self.warnings.append(W("kv.value_without_label", f"row {r} col {c + 1}: value {val.text!r} has no label"))
                self.entries.append({"grid_row": r, "grid_col": c,
                                     "label": _cell_view(lab), "value": _cell_view(val)})

    def _inline_colon(self) -> None:
        """Each line of each cell is one item: a cell may hold several
        'LABEL: VALUE' lines separated by <br>/<p>. Leading lines without ':'
        are the title; a later line without ':' continues the previous value."""
        grid = self.grid
        lines = []  # (grid_row, line_index, n_lines, text, slot)
        for r in self.layout.data_rows:
            sl = grid.slot(r, 0)
            if sl.cell.is_empty:
                continue
            parts = [collapse_ws(p) for p in _LINE_BREAK.split(sl.cell.raw.strip())]
            parts = [p for p in parts if p]
            if sum(":" in p for p in parts) < 2:
                parts = [sl.text]  # one item per cell; line breaks are just wrapping
            lines += [(r, i, len(parts), p, sl) for i, p in enumerate(parts)]
        while lines and ":" not in lines[0][3]:
            self.title.append(lines.pop(0)[3])
        for r, i, n, text, sl in lines:
            src = _cell_view(sl)["src"]
            if n > 1:
                src = dict(src, line=i)
            label, sep, value = text.partition(":")
            if not sep and self.entries:
                prev = self.entries[-1]["value"]
                prev["text"] = (prev["text"] + " " + text).strip()
                self.warnings.append(W("kv.continuation_line", f"row {r}: {text!r} has no ':'; appended to the previous value"))
                continue
            if not sep:
                self.warnings.append(W("kv.no_colon", f"row {r}: no ':' in {text!r}; kept as a label with no value"))
            self.entries.append({
                "grid_row": r,
                "label": {"text": label.strip(), "raw": sl.cell.raw, "split": "before first ':'", "src": src},
                "value": {"text": value.strip(), "raw": sl.cell.raw, "split": "after first ':'", "src": src}
                if sep else {"text": "", "raw": "", "missing": True},
            })

    def to_dict(self, include_grid: bool = True) -> dict:
        d = {
            "kind": "key_value",
            "table_index": self.grid.table_index,
            "mode": self.mode,
            "title": self.title,
            "entries": self.entries,
            "layout": self.layout.to_dict(),
            "warnings": warning_dicts(self.warnings),
            "review_items": self.review_items,
        }
        if include_grid:
            d["grid"] = self.grid.to_dict()
        return d

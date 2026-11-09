"""Layer 1: HTML <table> -> fully resolved grid.

Generic: knows nothing about building codes. Every grid slot points at the
source cell that fills it, so values carried down by rowspan / across by
colspan are explicit (``inherited``) rather than silently duplicated or lost.
"""
from __future__ import annotations

import itertools
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser

from .notes import W, warning_dicts

_WS = re.compile(r"\s+")
_LINE_BREAK = re.compile(r"[ \t\r\f\v]*\n\s*")
_MAX_JOIN_BREAKS = 4  # 2**4 = 16 candidates max


def collapse_ws(s: str) -> str:
    return _WS.sub(" ", s).strip()


@dataclass
class Cell:
    """One physical <td>/<th> from the source HTML."""

    id: int
    source_row: int  # index of the <tr> it was written in
    tag: str  # "td" | "th"
    raw: str  # text exactly as in the source (excluding <sup> content)
    text: str  # whitespace-collapsed
    footnotes: list[str]  # tokens from <sup>, e.g. ["c", "d"]
    footnotes_raw: str
    classes: list[str]  # classes of the cell and inline children ("bold", "changed_ICC", ...)
    rowspan: int
    colspan: int
    attrs: dict[str, str]
    join_candidates: list[str] = field(default_factory=list)
    origin: tuple[int, int] | None = None  # grid (row, col) of top-left slot
    warnings: list[str] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return self.text == ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source_row": self.source_row,
            "tag": self.tag,
            "raw": self.raw,
            "text": self.text,
            "footnotes": self.footnotes,
            "footnotes_raw": self.footnotes_raw,
            "classes": self.classes,
            "rowspan": self.rowspan,
            "colspan": self.colspan,
            "origin": list(self.origin) if self.origin else None,
            "join_candidates": self.join_candidates,
            "warnings": warning_dicts(self.warnings),
        }


@dataclass
class Slot:
    """A view of one grid position."""

    row: int
    col: int
    cell: Cell

    @property
    def inherited(self) -> bool:
        return self.cell.origin != (self.row, self.col)

    @property
    def text(self) -> str:
        return self.cell.text

    def provenance(self) -> dict:
        return {
            "grid_row": self.row,
            "grid_col": self.col,
            "cell_id": self.cell.id,
            "origin": list(self.cell.origin),
            "inherited": self.inherited,
            "raw": self.cell.raw,
        }


class Grid:
    def __init__(self, cells: list[Cell], slots: list[list[int | None]], warnings: list[str]):
        self.cells = cells
        self.slots = slots
        self.warnings = warnings
        self.table_index = 0  # position among the top-level tables of the source file
        self.n_rows = len(slots)
        self.n_cols = len(slots[0]) if slots else 0

    def slot(self, r: int, c: int) -> Slot | None:
        cid = self.slots[r][c]
        return None if cid is None else Slot(r, c, self.cells[cid])

    def row_slots(self, r: int) -> list[Slot | None]:
        return [self.slot(r, c) for c in range(self.n_cols)]

    def origin_cells_in_row(self, r: int) -> list[Cell]:
        """Cells whose top-left slot is in row r (i.e. not carried down from above)."""
        seen: list[Cell] = []
        for cid in self.slots[r]:
            if cid is None:
                continue
            cell = self.cells[cid]
            if cell.origin[0] == r and cell not in seen:
                seen.append(cell)
        return seen

    def text_matrix(self) -> list[list[str]]:
        return [[("" if cid is None else self.cells[cid].text) for cid in row] for row in self.slots]

    def to_dict(self) -> dict:
        return {
            "n_rows": self.n_rows,
            "n_cols": self.n_cols,
            "text": self.text_matrix(),
            "slots": self.slots,
            "cells": [c.to_dict() for c in self.cells],
            "warnings": warning_dicts(self.warnings),
        }


# --------------------------------------------------------------------------- #
# HTML tokenising
# --------------------------------------------------------------------------- #

# Tags that start a new line inside a cell. A block element's boundary is a line
# break: "<p>BED</p><p>ROOM 101</p>" reads "BED\nROOM 101", so both "BED ROOM 101"
# and "BEDROOM 101" are offered as join candidates instead of silently gluing.
_BLOCK_TAGS = ("p", "div", "li")
_LINE_TAGS = ("br",) + _BLOCK_TAGS


class _TableCollector(HTMLParser):
    """Collects top-level tables as rows of raw cell dicts. Tolerates missing end tags."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tables: list[list[list[dict]]] = []
        self._depth = 0
        self._row: list[dict] | None = None
        self._cell: dict | None = None
        self._sup = 0
        self.table_warnings: list[list[str]] = []  # parallel to self.tables

    def _warn(self, msg: W) -> None:
        if self.table_warnings and msg not in self.table_warnings[-1]:
            self.table_warnings[-1].append(msg)

    # -- helpers --
    def _close_cell(self) -> None:
        if self._cell is not None and self._row is not None:
            self._row.append(self._cell)
        self._cell = None
        self._sup = 0

    def _close_row(self) -> None:
        self._close_cell()
        if self._row is not None and self.tables:
            self.tables[-1].append(self._row)
        self._row = None

    # -- HTMLParser hooks --
    def handle_starttag(self, tag, attrs):
        a = {k: (v if v is not None else "") for k, v in attrs}
        if tag == "table":
            if self._depth == 1 and self._cell is None:
                # <table> inside a table but not inside a cell: the previous table was
                # never closed. Browsers start a new table here; so do we.
                self._close_row()
                self.tables.append([])
                self.table_warnings.append([W("grid.unclosed_table",
                                              "the previous <table> was not closed before this one; "
                                              "read as two separate tables")])
                return
            self._depth += 1
            if self._depth == 1:
                self.tables.append([])
                self.table_warnings.append([])
            else:
                self._warn(W("grid.nested_table", "nested <table> found; its cell texts are merged into "
                             "the enclosing cell, separated by spaces"))
                if self._cell is not None:
                    self._cell["text"].append(" ")
            return
        if self._depth != 1:
            if self._depth > 1 and self._cell is not None:
                if tag == "br":
                    self._cell["text"].append("\n")
                elif tag in ("td", "th", "tr"):
                    # nested cell boundary: keep the texts apart ("in1 in2", not "in1in2").
                    # A space, not a line break, so no false join candidates are offered.
                    self._cell["text"].append(" ")
            return
        if tag == "tr":
            self._close_row()
            self._row = []
        elif tag in ("td", "th"):
            self._close_cell()
            if self._row is None:  # cell without <tr>
                self._row = []
            self._cell = {"tag": tag, "attrs": a, "text": [], "sup": [],
                          "classes": a.get("class", "").split()}
        elif self._cell is not None:
            if tag == "sup":
                self._sup += 1
                if self._cell["sup"]:
                    self._cell["sup"].append(",")
            elif tag in _LINE_TAGS:
                self._cell["text"].append("\n")
            if tag in ("b", "strong"):
                self._cell["classes"].append("bold")
            for cls in a.get("class", "").split():
                if cls not in self._cell["classes"]:
                    self._cell["classes"].append(cls)

    def handle_endtag(self, tag):
        if tag == "table":
            if self._depth == 1:
                self._close_row()
            elif self._depth > 1 and self._cell is not None:
                self._cell["text"].append(" ")
            self._depth = max(0, self._depth - 1)
            return
        if self._depth != 1:
            return
        if tag in ("td", "th"):
            self._close_cell()
        elif tag == "tr":
            self._close_row()
        elif tag == "sup" and self._cell is not None:
            self._sup = max(0, self._sup - 1)
        elif tag in _BLOCK_TAGS and self._cell is not None:
            self._cell["text"].append("\n")

    def handle_data(self, data):
        if self._cell is None:
            return
        (self._cell["sup"] if self._sup else self._cell["text"]).append(data)


# --------------------------------------------------------------------------- #
# Cell construction + span resolution
# --------------------------------------------------------------------------- #

def _parse_span(value: str | None, name: str, warnings: list[str]) -> int:
    if value is None:
        return 1
    s = value.strip()
    if s == "":
        return 1  # e.g. colspan="" all over the IBC scrape
    if s.isdigit() and int(s) >= 1:
        return int(s)
    warnings.append(W("grid.invalid_span", f'{name}="{value}" is not a positive integer; treated as 1'))
    return 1


def _join_candidates(raw: str) -> list[str]:
    """For text broken across lines, list both readings of every break.

    "SCREE\\n   N" -> ["SCREE N", "SCREEN"]. The first candidate is always the
    plain whitespace-collapsed reading. Which one is right is a vocabulary
    decision for a later layer; the parser only records the options.
    """
    stripped = raw.strip()
    parts = [collapse_ws(p) for p in _LINE_BREAK.split(stripped)]
    parts = [p for p in parts if p]
    if len(parts) < 2:
        return []
    n_breaks = len(parts) - 1
    if n_breaks > _MAX_JOIN_BREAKS:
        return [" ".join(parts), "".join(parts)]
    out: list[str] = []
    for seps in itertools.product((" ", ""), repeat=n_breaks):
        s = parts[0] + "".join(sep + p for sep, p in zip(seps, parts[1:]))
        if s not in out:
            out.append(s)
    return out


def _footnote_tokens(sup: str) -> list[str]:
    return [t for t in re.split(r"[\s,;]+", sup) if t]


def _build_cells(rows: list[list[dict]]) -> list[list[Cell]]:
    out: list[list[Cell]] = []
    next_id = 0
    for r, row in enumerate(rows):
        built = []
        for raw_cell in row:
            w: list[str] = []
            raw = "".join(raw_cell["text"])
            sup = "".join(raw_cell["sup"])
            cell = Cell(
                id=next_id,
                source_row=r,
                tag=raw_cell["tag"],
                raw=raw,
                text=collapse_ws(raw),
                footnotes=_footnote_tokens(sup),
                footnotes_raw=collapse_ws(sup),
                classes=raw_cell["classes"],
                rowspan=_parse_span(raw_cell["attrs"].get("rowspan"), "rowspan", w),
                colspan=_parse_span(raw_cell["attrs"].get("colspan"), "colspan", w),
                attrs=raw_cell["attrs"],
                join_candidates=_join_candidates(raw),
                warnings=w,
            )
            next_id += 1
            built.append(cell)
        out.append(built)
    return out


def _resolve(rows: list[list[Cell]]) -> Grid:
    """HTML table placement algorithm: each cell takes the next free slot."""
    warnings: list[str] = []
    n_rows = len(rows)
    occupied: dict[tuple[int, int], int] = {}
    cells: list[Cell] = [c for row in rows for c in row]

    for r, row in enumerate(rows):
        c = 0
        for cell in row:
            while (r, c) in occupied:
                c += 1
            cell.origin = (r, c)
            rs = cell.rowspan
            if r + rs > n_rows:
                msg = W("grid.span_clipped",
                        f"rowspan={rs} at source row {r} runs past the table end; clipped to {n_rows - r}")
                cell.warnings.append(msg)
                warnings.append(msg.prefixed(f"cell {cell.id}: "))
                rs = n_rows - r
            for dr in range(rs):
                for dc in range(cell.colspan):
                    key = (r + dr, c + dc)
                    if key in occupied:
                        msg = W("grid.overlapping_spans",
                                f"slot {key} claimed by cell {cell.id} already belongs to "
                                f"cell {occupied[key]} (overlapping spans); kept the first")
                        cell.warnings.append(msg)
                        warnings.append(msg)
                        continue
                    occupied[key] = cell.id
            c += cell.colspan

    n_cols = max((k[1] for k in occupied), default=-1) + 1
    slots: list[list[int | None]] = [[occupied.get((r, c)) for c in range(n_cols)] for r in range(n_rows)]
    for r, row in enumerate(slots):
        missing = [c for c, v in enumerate(row) if v is None]
        if missing:
            warnings.append(W("grid.ragged_row", f"row {r} has no cell at columns {missing} (ragged row)"))
    for c in cells:
        for w in c.warnings:
            if w.code == "grid.invalid_span":
                warnings.append(w.prefixed(f"cell {c.id}: "))
    return Grid(cells, slots, warnings)


def parse_tables(html: str) -> list[Grid]:
    """Parse every top-level <table> in an HTML string into a resolved Grid."""
    collector = _TableCollector()
    collector.feed(html)
    collector.close()
    grids = []
    for i, (rows, table_warnings) in enumerate(zip(collector.tables, collector.table_warnings)):
        grid = _resolve(_build_cells(rows))
        grid.warnings = table_warnings + grid.warnings
        grid.table_index = i
        grids.append(grid)
    return grids


def parse_table(html: str, index: int = 0) -> Grid:
    grids = parse_tables(html)
    if not grids:
        raise ValueError("no <table> found in input")
    return grids[index]

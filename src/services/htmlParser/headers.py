"""Layer 2: find title rows, header rows, separator rows and per-column header paths.

Tags and styling are hints, not the rule: scrapes put headers in <tbody> as <td>
and OCR is inconsistent about <th>. The header region is found like this:

START   (first row after any title rows) when either
          - every non-empty cell is <th> or bold, or
          - STRUCTURE: the row has a merged cell (rowspan/colspan > 1) and no
            value-looking cells (numbers, dimensions).
EXTEND  through every row that
          - is covered by a header cell's rowspan (unconditional, so numeric
            header labels such as 5 / 10 / 30 under a merged cell still count), or
          - sits directly under a column-group cell (colspan > 1 implies child
            labels below), does not look like values, and - when the header
            started from th/bold - is itself th/bold, or
          - is made entirely of <th> cells.
          Bold alone does not extend the header: highlighted data rows are bold.
          Tie-breaker for the column-group rule: a plain column whose label is
          already in the header (colspan 1, not merged down) cannot have a
          child label below it. If the candidate row has text under such a
          column, the row is read as DATA and a review item is recorded.
          The tie-breaker yields to a row made entirely of <th> cells.
A flat header of unstyled <td> with no merged cells gives no signal; it is
reported, not guessed (pass header_rows=N).

BODY    After the header, any run of rows whose text repeats the header block
        exactly (case and whitespace aside) is a header reprinted after a page
        break. Those rows are dropped from the data and reported in warnings.

``warnings`` are parser-quality notes. ``review_items`` are readings the
parser had to choose between; the chosen reading is used and the alternative
is recorded so a person (or a later check) can confirm it. Each review item is
a dict: code, rows, cols, chosen, alternative, override (how to force the
other reading, or None), message.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .grid import Cell, Grid

# numbers, fractions, percentages, feet-inch dimensions, ranges: "55", "1,000", "1/2", "2' - 6\"", "10-20"
_VALUE_LIKE = re.compile(r"^[\d\s,./'\"′″’”\-–−%]+$")
_VALUE_TOKENS = {"UL", "NP", "NR", "N/A", "—", "-"}
# units rows under a header: "(hr)", "(ft)", "FT", "SQ FT" ...
UNIT_TOKENS = {"FT", "IN", "SF", "SQ FT", "SQ. FT.", "FT2", "EA", "HR", "HRS", "MIN", "%", "LBS", "PSF", "IN.", "FT."}


def review_item(code: str, message: str, *, rows=(), cols=(), chosen: str, alternative: str,
                override: dict | None = None, **extra) -> dict:
    d = {"code": code, "rows": list(rows), "cols": list(cols), "chosen": chosen,
         "alternative": alternative, "override": override, "message": message}
    d.update(extra)
    return d


def _is_unit_like(text: str) -> bool:
    t = " ".join(text.split()).upper()
    return (t.startswith("(") and t.endswith(")")) or t in UNIT_TOKENS


def _is_header_like(cell: Cell) -> bool:
    return cell.tag == "th" or "bold" in cell.classes


def _is_value_like(cell: Cell) -> bool:
    t = cell.text
    return bool(t) and (t.upper() in _VALUE_TOKENS or (any(ch.isdigit() for ch in t) and bool(_VALUE_LIKE.match(t))))


def _row_has_value_like(grid: Grid, r: int) -> bool:
    return any(_is_value_like(c) for c in grid.origin_cells_in_row(r))


def _row_all_th(grid: Grid, r: int) -> bool:
    cells = [c for c in grid.origin_cells_in_row(r) if not c.is_empty]
    return bool(cells) and all(c.tag == "th" for c in cells)


def _row_has_merge(grid: Grid, r: int) -> bool:
    return any((c.rowspan > 1 or c.colspan > 1) and c.colspan < grid.n_cols for c in grid.origin_cells_in_row(r))


def is_title_row(grid: Grid, r: int) -> bool:
    """A single non-empty cell spanning the full width (e.g. 'CODE ANALYSIS - SHEET A0.1')."""
    cells = grid.origin_cells_in_row(r)
    return (grid.n_cols > 1 and len(cells) == 1 and cells[0].colspan >= grid.n_cols
            and cells[0].rowspan == 1 and not cells[0].is_empty)


def is_separator_row(grid: Grid, r: int) -> bool:
    """A row that introduces cells but all of them are empty."""
    cells = grid.origin_cells_in_row(r)
    return bool(cells) and all(c.is_empty for c in cells)


def _row_is_header_like(grid: Grid, r: int) -> bool:
    cells = grid.origin_cells_in_row(r)
    non_empty = [c for c in cells if not c.is_empty]
    if not non_empty:
        return bool(cells) and all(c.tag == "th" for c in cells)
    return all(_is_header_like(c) for c in non_empty)


@dataclass
class Column:
    index: int
    id: str
    path: list[str]  # header texts top -> bottom, empty levels dropped
    path_candidates: list[list[str]]  # per level: alternative readings of line-broken text
    header_cell_ids: list[int]
    duplicate_of: list[str] = field(default_factory=list)

    @property
    def label(self) -> str:
        return " / ".join(self.path) if self.path else self.id

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "id": self.id,
            "label": self.label,
            "path": self.path,
            "path_candidates": self.path_candidates,
            "header_cell_ids": self.header_cell_ids,
            "duplicate_of": self.duplicate_of,
        }


@dataclass
class Layout:
    title_rows: list[int]
    header_rows: list[int]
    separator_rows: list[int]
    data_rows: list[int]
    columns: list[Column]
    method: str
    repeated_header_rows: list[int] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    review_items: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "title_rows": self.title_rows,
            "header_rows": self.header_rows,
            "repeated_header_rows": self.repeated_header_rows,
            "separator_rows": self.separator_rows,
            "data_rows": self.data_rows,
            "columns": [c.to_dict() for c in self.columns],
            "method": self.method,
        }


def detect_layout(grid: Grid, header_rows: int | None = None) -> Layout:
    """Classify rows. Pass ``header_rows`` to override detection with an explicit count
    (counted after any leading title rows)."""
    r = 0
    titles: list[int] = []
    while r < grid.n_rows and is_title_row(grid, r) and not _row_is_header_like(grid, r):
        titles.append(r)
        r += 1

    headers: list[int] = []
    review: list[dict] = []
    if header_rows is not None:
        headers = list(range(r, min(grid.n_rows, r + header_rows)))
        method = f"explicit header_rows={header_rows}"
    else:
        headers, method = _detect_header_rows(grid, r, review)

    body_start = (headers[-1] + 1) if headers else (titles[-1] + 1 if titles else 0)
    repeated = _repeated_header_rows(grid, headers, body_start)
    warnings: list[str] = []
    if repeated:
        # dropping rows is a data decision: record it as a review item and keep the text
        review.append(review_item(
            "header.repeat_dropped",
            f"rows {repeated} repeat the header rows {headers} exactly (e.g. reprinted after a page "
            "break), so they were dropped from the data. If they are real data rows, pass "
            "header_rows explicitly and filter them yourself.",
            rows=repeated, chosen="dropped as repeated header", alternative="data rows",
            matches_header_rows=headers, text=[[s.cell.text if s else "" for s in grid.row_slots(rr)]
                                               for rr in repeated]))
    separators, data = [], []
    for rr in range(body_start, grid.n_rows):
        if rr in repeated:
            continue
        (separators if is_separator_row(grid, rr) else data).append(rr)

    columns = _column_paths(grid, headers)
    return Layout(titles, headers, separators, data, columns, method, repeated, warnings, review)


def _row_key(grid: Grid, r: int) -> tuple[tuple[str, str], ...]:
    """Text and footnote marks per slot, so 'A<sup>1</sup>' and 'A<sup>2</sup>' differ."""
    return tuple((" ".join(s.cell.text.split()).upper(), s.cell.footnotes_raw) if s else ("", "")
                 for s in grid.row_slots(r))


def _repeated_header_rows(grid: Grid, headers: list[int], body_start: int) -> list[int]:
    """Body rows that reprint the whole header block, slot for slot. A repeat must
    follow at least one real data row: a header reprinted after a page break has
    data before it, while a first body row that happens to equal a one-row
    header ("SF | SM" under "SF | SM") is kept as data."""
    if not headers:
        return []
    block = [_row_key(grid, h) for h in headers]
    if not any(any(t for t, _ in row) for row in block):
        return []
    out: list[int] = []
    r = body_start
    seen_data = False
    while r + len(block) <= grid.n_rows:
        if not seen_data:
            seen_data = not is_separator_row(grid, r)
            r += 1
            continue
        if all(_row_key(grid, r + i) == block[i] for i in range(len(block))):
            out.extend(range(r, r + len(block)))
            r += len(block)
        else:
            r += 1
    return out


def _plain_label_conflicts(grid: Grid, r: int) -> list[str]:
    """Columns where row r has new text under a plain (colspan 1) header label
    from the row above that was not merged down. A real child header row has
    nothing there: the label above would have been given rowspan instead."""
    hits = []
    for c in range(grid.n_cols):
        above, here = grid.slot(r - 1, c), grid.slot(r, c)
        if above is None or here is None or here.cell.id == above.cell.id:
            continue
        a = above.cell
        if a.colspan == 1 and not a.is_empty and a.origin[0] + a.rowspan == r \
                and here.cell.origin[0] == r and not here.cell.is_empty \
                and not _is_unit_like(here.cell.text):  # "(hr)" under ELEMENT: a units row
            hits.append((c, a.text))
    return hits


def _detect_header_rows(grid: Grid, start: int, review: list[str]) -> tuple[list[int], str]:
    if start >= grid.n_rows:
        return [], "no header rows detected"
    if _row_is_header_like(grid, start):
        signals = ["start: th/bold row"]
        styled = True
    elif _row_has_merge(grid, start) and not _row_has_value_like(grid, start):
        signals = ["start: merged cells, no values"]
        styled = False
    else:
        return [], "no header rows detected"

    headers: list[int] = []
    span_end = start + 1  # rows covered by header rowspans
    group_end = start + 1  # rows that should hold children of column-group cells
    r = start
    while r < grid.n_rows:
        if r == start:
            reason = None
        elif r < span_end:
            reason = "rowspan"
        elif is_separator_row(grid, r):
            break
        elif r < group_end and not _row_has_value_like(grid, r) and (not styled or _row_is_header_like(grid, r)):
            # a styled (th/bold) header's children must be styled too; otherwise a
            # text-only first data row under a colspan header would be swallowed
            # an explicit all-<th> row beats the structural tie-breaker
            conflicts = [] if _row_all_th(grid, r) else _plain_label_conflicts(grid, r)
            if conflicts:
                named = ", ".join(f"{t!r} (column {c})" for c, t in conflicts)
                review.append(review_item(
                    "header.row_read_as_data",
                    f"row {r} could be header labels under the column group above, but it has text "
                    f"under {named}, whose label is already in the header and not merged down; "
                    f"read as data. If row {r} is a header row, pass header_rows={r - start + 1}.",
                    rows=[r], cols=[c for c, _ in conflicts], chosen="data", alternative="header",
                    override={"header_rows": r - start + 1}))
                break
            reason = "column-group children"
        elif _row_all_th(grid, r):
            reason = "th row"
        else:
            break
        if reason and f"extend: {reason}" not in signals:
            signals.append(f"extend: {reason}")
        headers.append(r)
        for cell in grid.origin_cells_in_row(r):
            span_end = max(span_end, r + cell.rowspan)
            if 1 < cell.colspan < grid.n_cols:
                group_end = max(group_end, r + cell.rowspan + 1)
        r += 1
    return headers, "; ".join(signals)


def _column_paths(grid: Grid, header_rows: list[int]) -> list[Column]:
    cols: list[Column] = []
    for c in range(grid.n_cols):
        path, cands, ids = [], [], []
        for r in header_rows:
            s = grid.slot(r, c)
            if s is None or s.cell.id in ids:
                continue  # same cell spanning vertically: count once
            ids.append(s.cell.id)
            if s.cell.is_empty:
                continue
            path.append(s.cell.text)
            cands.append(s.cell.join_candidates or [s.cell.text])
        cols.append(Column(c, f"c{c}", path, cands, ids))
    by_label: dict[str, list[Column]] = {}
    for col in cols:
        if col.path:
            by_label.setdefault(col.label, []).append(col)
    for group in by_label.values():
        if len(group) > 1:
            for col in group:
                col.duplicate_of = [o.id for o in group if o is not col]
    return cols

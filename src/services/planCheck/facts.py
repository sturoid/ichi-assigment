"""Project facts from the parsed code analysis and window schedule.

Fields are found by label alias, and schedule columns by header alias, never by
position, so another project's sheet with other names in another order still reads.
Each fact keeps what was read (raw text, grid row/column) so a reviewer can trace it,
and the parser's line-break join candidates are used for split words
("FIRE SPRINKLE RS" -> "FIRE SPRINKLERS").
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from services.htmlParser import KeyValueSheet, RecordTable, parse_tables

from .rooms import classify, room_key
from .units import parse_length


def label_norm(text: str) -> str:
    t = (text or "").upper().replace("&", " AND ")
    t = re.sub(r"[^A-Z0-9 ]+", " ", t)
    return " ".join(t.split())


# --------------------------------------------------------------------------- #
# Code analysis
# --------------------------------------------------------------------------- #

CODE_ANALYSIS_FIELDS: dict[str, tuple[str, ...]] = {
    "project": ("PROJECT", "PROJECT DESCRIPTION", "DESCRIPTION OF WORK", "SCOPE OF WORK", "SCOPE"),
    "applicable_code": ("APPLICABLE CODE", "APPLICABLE CODES", "CODE", "CODES", "BUILDING CODE", "GOVERNING CODE"),
    "occupancy": ("OCCUPANCY GROUP", "OCCUPANCY", "OCCUPANCY CLASSIFICATION", "OCCUPANCY TYPE", "USE GROUP",
                  "OCCUPANCY GROUPS"),
    "construction": ("CONSTRUCTION TYPE", "TYPE OF CONSTRUCTION", "CONSTRUCTION", "CONSTRUCTION CLASSIFICATION"),
    "sprinklers": ("FIRE SPRINKLERS", "SPRINKLERS", "SPRINKLER", "FIRE SPRINKLER", "SPRINKLER SYSTEM",
                   "AUTOMATIC SPRINKLER SYSTEM", "FIRE SPRINKLER SYSTEM", "SPRINKLERED", "FIRE PROTECTION"),
    "stories": ("NUMBER OF STORIES", "STORIES", "NO OF STORIES", "BUILDING STORIES"),
    "height": ("BUILDING HEIGHT", "BUILDING HEIGHT ABOVE GRADE PLANE", "HEIGHT", "HEIGHT ABOVE GRADE PLANE",
               "ACTUAL HEIGHT", "ACTUAL BUILDING HEIGHT", "PROPOSED HEIGHT", "PROPOSED BUILDING HEIGHT"),
    "allowable_height": ("ALLOWABLE HEIGHT", "ALLOWABLE BUILDING HEIGHT", "MAXIMUM HEIGHT", "MAX HEIGHT",
                         "ALLOWED HEIGHT"),
    "allowable_stories": ("ALLOWABLE STORIES", "ALLOWABLE NUMBER OF STORIES"),
    "grade_plane": ("GRADE PLANE", "GRADE PLANE ELEVATION"),
    "room_numbering": ("ROOM NUMBERING", "ROOM NUMBERS", "ROOM NUMBER KEY"),
    "egress_claim": ("EMERGENCY ESCAPE AND RESCUE", "EMERGENCY ESCAPE AND RESCUE OPENINGS", "EMERGENCY ESCAPE",
                     "EGRESS", "EGRESS WINDOWS", "EERO", "EMERGENCY EGRESS"),
}

_ALIAS_TO_FIELD = {label_norm(a): f for f, aliases in CODE_ANALYSIS_FIELDS.items() for a in aliases}


@dataclass
class Fact:
    field: str
    value: str
    label: str                      # the label as printed (normalised spacing)
    matched_alias: str
    via_join: bool                  # matched only after joining a word split across lines
    src: dict
    flags: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"field": self.field, "value": self.value, "label": self.label, "matched_alias": self.matched_alias,
                "via_join": self.via_join, "src": self.src, "flags": self.flags}


@dataclass
class CodeAnalysis:
    file: str
    facts: dict[str, Fact]
    unmatched: list[dict]           # labels no alias recognised
    conflicts: dict[str, list[Fact]]  # a field given more than once
    title: list[str]

    def get(self, name: str) -> Fact | None:
        return self.facts.get(name)


def _match_label(label: dict) -> tuple[str, str, bool] | None:
    """(field, alias, via_join) for a label, trying the printed text then join candidates."""
    cands = [(label.get("text", ""), False)] + [(c, True) for c in label.get("join_candidates", [])]
    for text, via_join in cands:
        n = label_norm(text)
        if n in _ALIAS_TO_FIELD:
            return _ALIAS_TO_FIELD[n], n, via_join and n != label_norm(label.get("text", ""))
    return None


def read_code_analysis(html: str, file: str = "code-analysis.html") -> CodeAnalysis:
    grids = parse_tables(html)
    facts: dict[str, Fact] = {}
    conflicts: dict[str, list[Fact]] = {}
    unmatched: list[dict] = []
    title: list[str] = []
    for grid in grids:
        kv = KeyValueSheet(grid)
        title += kv.title
        for e in kv.entries:
            lab, val = e["label"], e["value"]
            hit = _match_label(lab)
            src = {"file": file, "table": grid.table_index, "grid_row": e["grid_row"]}
            if hit is None:
                unmatched.append({"label": lab.get("text", ""), "value": val.get("text", ""), "src": src})
                continue
            fld, alias, via_join = hit
            f = Fact(fld, val.get("text", ""), lab.get("text", ""), alias, via_join, src)
            if via_join:
                f.flags.append({"code": "label_split_word",
                                "message": f"label printed as {lab.get('text')!r} (a word split across lines); "
                                           f"read as {alias!r}"})
            if fld in facts:
                conflicts.setdefault(fld, [facts[fld]]).append(f)
            else:
                facts[fld] = f
    return CodeAnalysis(file, facts, unmatched, conflicts, title)


# --------------------------------------------------------------------------- #
# Window schedule
# --------------------------------------------------------------------------- #

# roles -> header aliases (normalised). Matching uses the column's leaf label and its full path.
COLUMN_ROLES: dict[str, tuple[str, ...]] = {
    "mark": ("SYMBOL", "MARK", "WINDOW", "WINDOW NO", "WINDOW NUMBER", "NO", "ID", "TAG", "WINDOW MARK", "WINDOW ID"),
    "room": ("LOCATION", "ROOM", "ROOM NAME", "SPACE", "ROOM NO", "ROOM NUMBER"),
    "width": ("WIDTH", "W", "NOMINAL WIDTH", "WIDTH NOMINAL"),
    "height": ("HEIGHT", "H", "HT", "NOMINAL HEIGHT", "HEIGHT NOMINAL"),
    "operation": ("OPERATION", "OPERATOR", "WINDOW TYPE", "STYLE", "OPERATION TYPE", "TYPE"),
    "type_mark": ("TYPE MARK", "TYPE"),
    "head_height": ("HEAD HEIGHT", "HEAD HT", "HEAD", "HEAD HGT"),
    "sill_height": ("SILL HEIGHT", "SILL HT", "SILL", "SILL HGT"),
    "net_clear_area": ("NET CLEAR OPENING", "NET CLEAR AREA", "NET CLEAR", "CLEAR OPENING", "NCO",
                       "CLEAR OPENING AREA", "NET CLEAR OPENING SF", "NET OPENING"),
    "clear_width": ("CLEAR WIDTH", "NET CLEAR WIDTH", "CLEAR OPENING WIDTH"),
    "clear_height": ("CLEAR HEIGHT", "NET CLEAR HEIGHT", "CLEAR OPENING HEIGHT"),
    "egress": ("EGRESS", "EGRESS WINDOW", "EERO", "EMERGENCY ESCAPE", "EMERGENCY EGRESS", "ESCAPE", "EGRESS Y N"),
    "screen": ("SCREEN", "SCREENS"),
    "notes": ("NOTES", "REMARKS", "COMMENTS"),
}
_SIZE_GROUPS = ("NOMINAL SIZE", "SIZE", "UNIT SIZE", "ROUGH OPENING", "FRAME SIZE", "NOMINAL")
_CLEAR_GROUPS = ("NET CLEAR OPENING", "CLEAR OPENING", "NET CLEAR", "EGRESS OPENING")

OPERATIONS = {
    "casement": ("CASEMENT", "CASM'T", "CASMT", "CSMT", "CSM", "CASE", "CAS"),
    "awning": ("AWNING", "AWN"),
    "hopper": ("HOPPER", "HOP"),
    "single_hung": ("SINGLE HUNG", "S.H.", "SH", "S/H", "S H"),
    "double_hung": ("DOUBLE HUNG", "D.H.", "DH", "D/H", "D H"),
    "slider": ("SLIDER", "SLIDING", "SLDR", "HORIZONTAL SLIDER", "HORIZ. SLIDER", "XO", "OX", "XOX"),
    "fixed": ("FIXED", "FIX", "FX", "PICTURE", "F.G.", "FIXED GLASS"),
}
_HANDING = re.compile(r"\b(L\.?\s?H\.?|R\.?\s?H\.?|LEFT HAND|RIGHT HAND)(?=\s|$)")


def classify_operation(text: str) -> tuple[str | None, str]:
    """('casement', "CASM'T") from "L.H. CASM'T"; (None, text) when not recognised."""
    t = " ".join((text or "").upper().split())
    core = _HANDING.sub(" ", t).strip()
    core = " ".join(core.split())
    for op, forms in OPERATIONS.items():
        for f in sorted(forms, key=len, reverse=True):
            if core == f or re.search(rf"(?<![A-Z]){re.escape(f)}(?![A-Z])", core):
                return op, f
    return None, core


def _looks_like_mark(text: str) -> bool:
    return bool(re.fullmatch(r"[A-Z]{1,2}\d{0,2}|[A-Z]?-?\d{1,3}[A-Z]?", " ".join((text or "").upper().split())))


@dataclass
class ColumnMap:
    roles: dict[str, str]             # role -> column id
    labels: dict[str, str]            # column id -> printed label
    notes: list[dict]                 # how ambiguous columns were assigned
    missing: list[str]                # roles a check needs that no column has

    def to_dict(self) -> dict:
        return {"roles": self.roles, "labels": self.labels, "notes": self.notes, "missing": self.missing}


NEEDED_ROLES = ("mark", "room", "width", "height", "operation", "head_height", "egress")


def _col_names(col) -> tuple[str, list[str]]:
    """(leaf name, all normalised readings of the path, including join candidates)."""
    leafs = [label_norm(x) for x in (col.path_candidates[-1] if col.path_candidates else [col.label])]
    groups = [label_norm(x) for cands in col.path_candidates[:-1] for x in cands] if col.path_candidates else []
    return leafs, groups


def map_columns(table: RecordTable) -> ColumnMap:
    roles: dict[str, str] = {}
    notes: list[dict] = []
    labels = {c.id: c.label for c in table.layout.columns}
    type_cols: list = []
    for col in table.layout.columns:
        leafs, groups = _col_names(col)
        in_size = any(g in _SIZE_GROUPS for g in groups)
        in_clear = any(g in _CLEAR_GROUPS for g in groups)
        role = None
        for leaf in leafs:
            if leaf == "TYPE":
                role = "TYPE"
                break
            if leaf in ("WIDTH", "W", "HEIGHT", "H", "HT") and in_clear:
                role = "clear_width" if leaf in ("WIDTH", "W") else "clear_height"
                break
            if leaf in ("HEIGHT", "H", "HT") and not in_size and groups:
                continue  # HEIGHT under some other group is not the unit height
            for r, aliases in COLUMN_ROLES.items():
                if r in ("operation", "type_mark") and leaf == "TYPE":
                    continue
                if leaf in aliases:
                    role = r
                    break
            if role:
                break
        if role == "TYPE":
            type_cols.append(col)
        elif role and role not in roles:
            roles[role] = col.id
        elif role:
            notes.append({"code": "duplicate_role", "message": f"column {col.id} ({col.label!r}) also looks like "
                          f"{role!r}; the first such column ({roles[role]}) is used"})
        # report split-word headers the reader joined ("SCREE N" -> "SCREEN")
        printed = label_norm(col.path[-1]) if col.path else ""
        if role and printed and printed not in COLUMN_ROLES.get(role, ()) and role != "TYPE":
            joined = next((x for x in leafs if x in COLUMN_ROLES.get(role, ())), None)
            if joined and joined != printed:
                notes.append({"code": "header_split_word",
                              "message": f"header {col.path[-1]!r} read as {joined!r} (a word split across lines)"})
    _assign_type_columns(table, type_cols, roles, notes)
    missing = [r for r in NEEDED_ROLES if r not in roles]
    return ColumnMap(roles, labels, notes, missing)


def _assign_type_columns(table: RecordTable, type_cols: list, roles: dict, notes: list) -> None:
    """Two TYPE columns: the first is the operation, the second the type mark (the
    brief's convention for this schedule), *checked against their contents*. If the
    contents say otherwise, contents win and the swap is reported."""
    def op_share(col) -> float:
        vals = [r["cells"][col.id]["text"] for r in table.rows if r["cells"][col.id]["text"].strip()]
        return sum(classify_operation(v)[0] is not None for v in vals) / len(vals) if vals else 0.0

    free = [c for c in type_cols]
    if "operation" not in roles and free:
        shares = [(op_share(c), i, c) for i, c in enumerate(free)]
        best = max(shares, key=lambda x: (x[0], -x[1]))
        first = free[0]
        if best[0] >= 0.5:
            chosen = best[2]
            if chosen is not first:
                notes.append({"code": "type_columns_swapped",
                              "message": f"the first TYPE column ({first.id}) does not hold window operations; "
                                         f"{chosen.id} does, so it is read as the operation"})
        else:
            chosen = first
            notes.append({"code": "operation_column_unrecognised",
                          "message": f"no TYPE column holds recognisable operations; {first.id} is assumed"})
        roles["operation"] = chosen.id
        free.remove(chosen)
        notes.append({"code": "type_column_roles",
                      "message": f"TYPE column {chosen.id} read as the operation "
                                 f"({op_share(chosen):.0%} of its entries are known operations)"})
    if "type_mark" not in roles and free:
        roles["type_mark"] = free[0].id
        notes.append({"code": "type_column_roles", "message": f"TYPE column {free[0].id} read as the type mark"})
        for extra in free[1:]:
            notes.append({"code": "duplicate_role", "message": f"extra TYPE column {extra.id} not used"})


@dataclass
class Window:
    mark: str
    room_name: str
    room_key: str
    room_class: dict
    width: dict
    height: dict
    head_height: dict
    sill_height: dict | None
    net_clear_area: str | None
    clear_width: dict | None
    clear_height: dict | None
    operation_text: str
    operation: str | None
    type_mark: str
    egress_text: str | None          # None: the schedule has no egress column
    egress: bool | None
    screen_text: str | None
    src: dict
    raw: dict                        # role -> printed cell text
    flags: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {k: getattr(self, k) for k in self.__dataclass_fields__}


_YES = {"Y", "YES", "X", "✓", "√", "•"}
_NO = {"", "N", "NO", "-", "—", "N/A", "NA"}


@dataclass
class Schedule:
    file: str
    columns: ColumnMap
    windows: list[Window]
    review_items: list[dict]
    dropped_rows: list[dict]
    title: list[str] = field(default_factory=list)


def read_window_schedule(html: str, file: str = "window-schedule.html") -> Schedule:
    grid = parse_tables(html)[0]
    table = RecordTable(grid)
    cmap = map_columns(table)
    roles = cmap.roles
    windows: list[Window] = []
    dropped: list[dict] = []

    def cell(row, role):
        cid = roles.get(role)
        return None if cid is None else row["cells"][cid]["text"].strip()

    for row in table.rows:
        mark = cell(row, "mark") or ""
        room = cell(row, "room") or ""
        if not mark and not room:
            texts = [c["text"] for c in row["cells"].values() if c["text"].strip()]
            if texts:
                dropped.append({"grid_row": row["grid_row"], "texts": texts,
                                "reason": "row has no window mark and no location"})
            continue
        flags: list[dict] = []
        egress_text = cell(row, "egress")
        if egress_text is None:
            egress = None
        elif egress_text.upper() in _YES:
            egress = True
        elif egress_text.upper() in _NO:
            egress = False
        else:
            egress = None
            flags.append({"code": "egress_value_unrecognised",
                          "message": f"EGRESS cell reads {egress_text!r}; neither yes nor no"})
        op_text = cell(row, "operation") or ""
        op, _ = classify_operation(op_text)
        rc = classify(room)
        lengths = {r: parse_length(cell(row, r)).to_dict() if roles.get(r) else None
                   for r in ("width", "height", "head_height", "sill_height", "clear_width", "clear_height")}
        if not _looks_like_mark(mark):
            flags.append({"code": "mark_unusual", "message": f"window mark {mark!r} does not look like a mark"})
        windows.append(Window(
            mark=mark, room_name=room, room_key=room_key(room), room_class=rc.to_dict(),
            width=lengths["width"] or parse_length(None).to_dict(),
            height=lengths["height"] or parse_length(None).to_dict(),
            head_height=lengths["head_height"] or parse_length(None).to_dict(),
            sill_height=lengths["sill_height"], net_clear_area=cell(row, "net_clear_area"),
            clear_width=lengths["clear_width"], clear_height=lengths["clear_height"],
            operation_text=op_text, operation=op, type_mark=cell(row, "type_mark") or "",
            egress_text=egress_text, egress=egress, screen_text=cell(row, "screen"),
            src={"file": file, "table": grid.table_index, "grid_row": row["grid_row"]},
            raw={r: cell(row, r) for r in roles},
            flags=flags))
    title = [grid.slot(r, 0).text for r in table.layout.title_rows]
    return Schedule(file, cmap, windows, table.review_items, dropped, title)

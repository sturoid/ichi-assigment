"""Check 1 (height vs Table 504.3) and Check 2 (IBC 1030 escape openings).

Every verdict comes from code limits (citations.py), project facts (facts.py) and the
named policy rules (policies.py). Nothing here refers to a particular window or room.
"""
from __future__ import annotations

import re
from collections import OrderedDict
from dataclasses import dataclass, field

from services.codeStore import Store

from . import citations as C
from . import confidence
from .facts import CodeAnalysis, Schedule, Window
from .findings import CNE, FAIL, NA, PASS, Attention, Criterion, Finding, worst
from .resolver import resolve
from .units import fmt_in, parse_length

T504 = "IBC:2018:T504.3"


def _doc_title(store: Store, doc_id: str) -> str:
    d = store.documents.get(doc_id, {})
    return d.get("title", doc_id)


def _settle(store: Store, *doc_ids: str) -> list[str]:
    return [f"{_doc_title(store, d)} ({d}, not provided)" for d in doc_ids]


def _ev(label: str, value, source: str) -> dict:
    return {"label": label, "value": value, "source": source}


def _row(src: dict) -> int:
    """Table row counted from 1 at the top of the table, header rows included."""
    return src["grid_row"] + 1


def _src(fact) -> str:
    return f"{fact.src['file']} table row {_row(fact.src)}, label '{fact.label}'"


# =========================================================================== #
# Check 1: building height
# =========================================================================== #

def check_height(store: Store, ca: CodeAnalysis) -> tuple[Finding, list[Attention]]:
    attn: list[Attention] = []
    prov = store.provisions[T504]
    allowed = prov["dimensions"]["values"]
    facts = ca.facts
    evidence, flags, policies, interps, working = [], [], ["POL-H-STATED-HEIGHT"], [], []
    code_refs = [C.T504_SECTION.ref()]
    settle = _settle(store, "PROJECT:BUILDING-SECTIONS", "PROJECT:C1.0:CIVIL")
    for name in ("occupancy", "construction", "sprinklers", "height", "allowable_height"):
        f = facts.get(name)
        if f is not None:
            evidence.append(_ev(f.label, f.value, _src(f)))
            flags += f.flags
        for dup in ca.conflicts.get(name, [])[1:]:
            flags.append({"code": "field_conflict", "message": f"{name} is given twice: {dup.value!r} "
                          f"(table row {_row(dup.src)}) and {facts[name].value!r}; the first is used"})

    def cne(summary, extra_settle=()):
        return Finding("H-1", "height", "Building height", CNE, summary, code_refs, evidence, [], working, flags,
                       policies, interps, settle + list(extra_settle)), attn

    # dimensions --------------------------------------------------------------
    dims, problems = {}, []
    for dim, fname in (("occupancy", "occupancy"), ("sprinkler", "sprinklers"), ("construction", "construction")):
        f = facts.get(fname)
        if f is None:
            problems.append(f"the code analysis gives no {fname}")
            continue
        r = resolve(dim, f.value, allowed[dim])
        if r.status != "resolved":
            problems.append(f"{fname} {f.value!r} could not be read as a Table 504.3 {dim}: {r.reason}")
            continue
        dims[dim] = r.value
        rule_ids = ", ".join(x["id"] for x in r.rules)
        working.append(f"{fname} {f.value!r} -> `{r.value}` (resolver rule {rule_ids})")
        for it in r.interpretations:
            interps.append(f"{fname} {f.value!r} read as row `{r.value}`: {it.get('note', '')} "
                           f"(authority: {it['authority']}, {it['cites']['file']} line {it['cites']['lines'][0]})")
            policies.append("POL-H-INTERPRETATION")
    if problems:
        return cne("; ".join(problems).capitalize() + ".", ["the code analysis with the missing value"])

    spr_fact = facts["sprinklers"]
    if dims["sprinkler"] != "NS":
        policies.append("POL-H-SPRINKLER-COVERAGE")
        if not re.search(r"\bTHROUGHOUT\b", spr_fact.value.upper()):
            flags.append({"code": "sprinkler_coverage_not_stated",
                          "message": "the sprinkler entry names a standard but does not say 'throughout'; the "
                                     f"`{dims['sprinkler']}` sub-row is for buildings equipped throughout"})

    # height -------------------------------------------------------------------
    hf = facts.get("height")
    h = parse_length(hf.value if hf else None)
    if h.status != "parsed":
        return cne("The code analysis gives no building height that can be read.")
    if h.ocr_repaired:
        flags += h.flags
        policies.append("POL-GEN-OCR")
        return cne(f"The building height {hf.value!r} needed an OCR repair; confirm it on the sheet.")
    height_ft = h.inches / 12
    working.append(f"building height {h.matched!r} = {h.inches:g} in = {height_ft:g} ft")

    # lookup -------------------------------------------------------------------
    res = store.lookup(T504, **dims)
    if not res.found:
        return cne(f"Table 504.3 has no value for {dims}: {res.errors[0]['message']}.")
    limit = res.numeric_limit
    cite = res.citation["text"]
    code_refs.insert(0, f"{cite} = {res.value_text}" + (" ft" if res.value_kind == "number" else ""))
    working.append(f"lookup {cite} -> {res.value_text}")
    if limit is None:
        policies.append("POL-GEN-UNCOVERED")
        return cne(f"{cite} holds {res.value_text!r}, which is not a height; needs a policy decision.")

    # footnotes on the cell ---------------------------------------------------------
    policies.append("POL-H-FOOTNOTES")
    unresolved: list[str] = []
    for cond in res.conditions:
        refs = cond.get("references", [])
        missing = [f"{r['ref']} ({r['document'] or 'not in manifest'}, {r['status']})" for r in refs
                   if r["status"] != "available"]
        line = cond.get("source", {}).get("line")
        code_refs.append(f"Table 504.3 footnote {cond['mark']} (code/table-504.3-notes.md line {line})")
        where = ("the whole table" if cond["attached_to"] == "table" else
                 f"the {cond['attached_to'].replace('row_label:', '')} row label" if cond["attached_to"].startswith(
                     "row_label") else "this cell")
        if missing and "exception" in cond["text"].lower():   # an exception we can't read could reverse a Fail
            unresolved.append(f"an exception in {' and '.join(r['ref'] for r in refs if r['status'] != 'available')} "
                              f"(Table 504.3 footnote {cond['mark']}), not provided")
        working.append(f"footnote {cond['mark']} (printed on {where}): "
                       f"\"{cond['text']}\"" + (f" Points to: {'; '.join(missing)}." if missing else ""))
        for r in refs:
            if r["status"] != "available" and r["document"]:
                s = (f"{_doc_title(store, r['document'])} ({r['document']}, not provided; related through "
                     f"footnote {cond['mark']})")
                if s not in settle:
                    settle.append(s)

    project = facts.get("project")
    has_d = any(c["mark"] == "d" for c in res.conditions)  # footnote d is printed only on some NS labels
    if dims["sprinkler"] == "NS" and has_d and project and re.search(r"\bNEW\b", project.value.upper()):
        policies.append("POL-H-NS-NEW")
        return cne(f"The building resolves to the NS sub-row, but the project is new work and footnote d says NS "
                   f"values are only for existing buildings. Confirm the sprinkler system.")

    # architect's allowable height ------------------------------------------------------
    af = facts.get("allowable_height")
    if af is not None:
        a = parse_length(af.value)
        if a.status == "parsed" and abs(a.inches / 12 - limit) > 1e-9:
            arch_ft = a.inches / 12
            policies.append("POL-H-ARCHITECT")
            matches = _cells_holding(store, dims, arch_ft)
            msg = (f"The code analysis states an allowable height of {fmt_in(a.inches)} ({af.value!r}); "
                   f"{cite} gives {res.value_text} ft.")
            if matches:
                subs = " and ".join(f"`{m}`" for m in matches)
                msg += (f" {arch_ft:g} ft is the value of the {subs} sub-row{'s' if len(matches) > 1 else ''} in the "
                        f"same row and column, so the architect may have read the wrong sprinkler sub-row (this "
                        f"building resolves to `{dims['sprinkler']}`).")
            flags.append({"code": "architect_allowable_mismatch", "message": msg})
            attn.append(Attention("architect_allowable_mismatch", "Architect's allowable height disagrees with "
                                  "Table 504.3", msg, ["H-1"]))

    # verdict ----------------------------------------------------------------------
    margin = height_ft - limit
    if height_ft <= limit:
        verdict = PASS
        summary = (f"{fmt_in(h.inches)} is within the {res.value_text} ft allowed by {cite}"
                   + (f" ({fmt_in(-margin * 12)} to spare)." if limit != float('inf') else "."))
    else:
        verdict = FAIL
        summary = f"{fmt_in(h.inches)} exceeds the {res.value_text} ft allowed by {cite} by {fmt_in(margin * 12)}."
    working.append(f"{height_ft:g} ft {'<=' if verdict == PASS else '>'} {limit:g} ft"
                   + (f"; over by {margin:g} ft = {fmt_in(margin * 12)}" if verdict == FAIL else ""))
    return Finding("H-1", "height", "Building height", verdict, summary, code_refs, evidence, [], working, flags,
                   list(dict.fromkeys(policies)), interps, settle,
                   unresolved=unresolved if verdict == FAIL else []), attn


def _cells_holding(store: Store, dims: dict, value_ft: float) -> list[str]:
    """Other sprinkler sub-rows in the same row and column that hold value_ft: a likely
    explanation for an architect's figure."""
    out = []
    vals = store.provisions[T504]["dimensions"]["values"]
    for spr in vals["sprinkler"]:
        if spr == dims["sprinkler"]:
            continue
        r = store.lookup(T504, occupancy=dims["occupancy"], sprinkler=spr, construction=dims["construction"])
        if r.found and r.numeric_limit == value_ft:
            out.append(spr)
    return out


# =========================================================================== #
# Check 2: emergency escape and rescue openings
# =========================================================================== #

_ORDINALS = {"FIRST": 1, "SECOND": 2, "THIRD": 3, "FOURTH": 4, "FIFTH": 5, "SIXTH": 6, "SEVENTH": 7, "EIGHTH": 8,
             "NINTH": 9, "TENTH": 10, "1ST": 1, "2ND": 2, "3RD": 3, "4TH": 4, "5TH": 5, "6TH": 6}


def room_numbering(text: str | None) -> dict[str, int]:
    """'1XX = FIRST FLOOR, 2XX = SECOND FLOOR' -> {'1': 1, '2': 2}."""
    out = {}
    for m in re.finditer(r"\b(\d)\s*XX\s*[=:-]\s*([0-9A-Z]+)\s+(?:FLOOR|STORY|LEVEL)", (text or "").upper()):
        n = _ORDINALS.get(m.group(2)) or (int(m.group(2)) if m.group(2).isdigit() else None)
        if n:
            out[m.group(1)] = n
    return out


@dataclass
class Scope:
    verdict: str            # PASS (applies) | NA | CNE
    reason: str
    cite: str


def occupancy_scope(ca: CodeAnalysis) -> Scope:
    f = ca.facts.get("occupancy")
    if f is None:
        return Scope(CNE, "the code analysis gives no occupancy group", C.SCOPE_OCCUPANCIES.ref())
    groups = set(re.findall(r"\bR-?([1-4])\b", f.value.upper()))
    if groups & {"3", "4"}:
        return Scope(PASS, f"occupancy {f.value!r} is listed in 1030.1 item 2", C.SCOPE_OCCUPANCIES.ref())
    if "2" in groups:
        return Scope(CNE, f"occupancy {f.value!r}: 1030.1 applies to R-2 only in stories with one exit; the "
                          "exits per story are not given", C.SCOPE_R2.ref())
    return Scope(NA, f"occupancy {f.value!r} is not R-2, R-3 or R-4", C.SCOPE_OCCUPANCIES.ref())


def story_scope(ca: CodeAnalysis, room_key: str) -> Scope:
    numbering = room_numbering(ca.facts["room_numbering"].value if ca.facts.get("room_numbering") else None)
    m = re.match(r"[A-Z]?(\d)\d{2}", room_key)
    if m and m.group(1) in numbering:
        n = numbering[m.group(1)]
        if n < 4:
            return Scope(PASS, f"room {room_key} is on floor {n} (code analysis room numbering), below the fourth "
                               "story above grade plane", C.SCOPE_SLEEPING.ref())
        return Scope(NA, f"room {room_key} is on floor {n}, not below the fourth story", C.SCOPE_SLEEPING.ref())
    st = ca.facts.get("stories")
    if st and re.match(r"^\s*(\d+)", st.value) and int(re.match(r"^\s*(\d+)", st.value).group(1)) < 4:
        return Scope(PASS, f"the building has {st.value.strip()} stories, so every room is below the fourth",
                     C.SCOPE_SLEEPING.ref())
    return Scope(CNE, f"the story of room {room_key} is not known", C.SCOPE_SLEEPING.ref())


def _len_desc(d: dict | None) -> str:
    if not d or d["status"] == "empty":
        return "(blank)"
    if d["status"] != "parsed":
        return f"{d['text']!r} (not a dimension)"
    return f"{d['text']!r} = {d['inches']:g} in"


def _ocr(*ds) -> list[str]:
    return [f["message"] for d in ds if d for f in d.get("flags", []) if f["code"] == "ocr_repair"]


def _guard_ocr(cr: Criterion, *ds) -> Criterion:
    """POL-GEN-OCR: a Pass or Fail resting on a repaired value becomes Could Not Evaluate."""
    reps = _ocr(*ds)
    if reps and cr.verdict in (PASS, FAIL):
        cr.reason = (f"would be {cr.verdict}, but it rests on a repaired value ({'; '.join(reps)}); "
                     f"check the sheet. " + cr.reason)
        cr.verdict = CNE
        cr.policies.append("POL-GEN-OCR")
    return cr


def evaluate_window(w: Window, store: Store) -> list[Criterion]:
    """The 1030 criteria for one window, as if it were the room's escape opening."""
    crit: list[Criterion] = []
    W, H = w.width, w.height
    wd = _settle(store, "PROJECT:WINDOW-DETAILS")[0]

    # how it opens --------------------------------------------------------------
    if w.operation is None:
        crit.append(Criterion("Opens by normal operation", C.OPERABLE.ref(), f"type {w.operation_text!r}", CNE,
                              "window type not recognised", ["POL-E-OPERATION-UNKNOWN"], wd))
    elif w.operation == "fixed":
        crit.append(Criterion("Opens by normal operation", f"{C.OPERABLE.ref()}; {C.NORMAL_OPERATION.ref()}",
                              f"type {w.operation_text!r} (fixed)", FAIL, "a fixed window does not open",
                              ["POL-E-FIXED"], brief=f"scheduled as {w.operation_text!r}, which does not open"))
    else:
        crit.append(Criterion("Opens by normal operation", C.NORMAL_OPERATION.ref(),
                              f"type {w.operation_text!r} ({w.operation.replace('_', ' ')})", PASS,
                              "the scheduled type opens", brief=w.operation.replace('_', ' ')))
    fixed = w.operation == "fixed"
    half_note = {"single_hung": "only the bottom sash opens", "double_hung": "each sash opens about half",
                 "slider": "a slider opens about half its width"}.get(w.operation)

    # net clear area -------------------------------------------------------------------
    areq = f"Net clear opening >= {C.MIN_AREA.value:g} sq ft ({C.MIN_AREA_GRADE.value:g} if grade-floor)"
    aref = f"{C.MIN_AREA_CITE.ref()}; {C.MIN_AREA_GRADE_CITE.ref()}"
    nca = _number(w.net_clear_area)
    if fixed:
        crit.append(Criterion(areq, aref, "fixed: no opening", FAIL,
                              "no net clear opening results from normal operation", ["POL-E-FIXED"],
                              brief="no clear opening"))
    elif nca is not None:
        if nca >= C.MIN_AREA.value:
            v, why = PASS, f"scheduled net clear opening {nca:g} sq ft >= {C.MIN_AREA.value:g}"
        elif nca < C.MIN_AREA_GRADE.value:
            v, why = FAIL, f"scheduled net clear opening {nca:g} sq ft < {C.MIN_AREA_GRADE.value:g} (both limits)"
        else:
            v, why = CNE, (f"{nca:g} sq ft meets the grade-floor {C.MIN_AREA_GRADE.value:g} but not "
                           f"{C.MIN_AREA.value:g}; whether this is a grade-floor opening is not shown")
        crit.append(Criterion(areq, aref, f"net clear opening column {w.net_clear_area!r}", v, why,
                              ["POL-E-GRADE-FLOOR"], "" if v != CNE else _settle(store, "PROJECT:C1.0:CIVIL")[0]))
    elif W["status"] == "parsed" and H["status"] == "parsed":
        nominal = W["inches"] * H["inches"] / 144
        read = (f"nominal {W['inches']:g} in x {H['inches']:g} in = {W['inches'] * H['inches']:g} sq in "
                f"= {nominal:.2f} sq ft (upper bound)")
        pol = ["POL-E-NOMINAL-UPPER", "POL-E-GRADE-FLOOR"]
        if nominal <= C.MIN_AREA_GRADE.value:
            cr = Criterion(areq, aref, read, FAIL,
                           f"the net clear opening is smaller than {nominal:.2f} sq ft, so below "
                           f"{C.MIN_AREA_GRADE.value:g} and {C.MIN_AREA.value:g} sq ft whether or not it is a "
                           "grade-floor opening", pol,
                           brief=f"nominal {fmt_in(W['inches'])} × {fmt_in(H['inches'])} = {nominal:.2f} sq ft; the "
                                 f"clear opening is smaller, so under both {C.MIN_AREA_GRADE.value:g} and "
                                 f"{C.MIN_AREA.value:g} sq ft")
        elif nominal <= C.MIN_AREA.value:
            cr = Criterion(areq, aref, read, CNE,
                           f"below {C.MIN_AREA.value:g} sq ft, but could meet the grade-floor "
                           f"{C.MIN_AREA_GRADE.value:g}; grade-floor status needs the finished ground level", pol,
                           _settle(store, "PROJECT:C1.0:CIVIL", "PROJECT:ELEVATIONS")[0])
        else:
            cr = Criterion(areq, aref, read, CNE,
                           f"the nominal size exceeds {C.MIN_AREA.value:g} sq ft, but the net clear opening is "
                           "smaller by the frame and is not given", pol + ["POL-E-NO-FRAME-ASSUMPTION"], wd)
        if half_note and cr.verdict == CNE:
            frac = nominal / 2
            cr.reason += f". Note only: {half_note}, roughly {frac:.2f} sq ft (POL-E-PARTIAL-OPENING)"
            cr.policies.append("POL-E-PARTIAL-OPENING")
            if frac <= C.MIN_AREA.value:
                cr.policies.append("POL-E-AT-LIMIT")
                at = (f"exactly the {C.MIN_AREA.value:g} sq ft minimum, leaving nothing for the frame"
                      if frac == C.MIN_AREA.value else f"below the {C.MIN_AREA.value:g} sq ft minimum")
                cr.flags.append({"code": "partial_opening_at_minimum",
                                 "message": f"expect a Fail on net clear area: {half_note}, about {frac:.2f} sq ft "
                                            f"before the frame, {at}. Ask for "
                                            "the sash split and the manufacturer's clear opening."})
        crit.append(_guard_ocr(cr, W, H))
    else:
        crit.append(Criterion(areq, aref, f"width {_len_desc(W)}, height {_len_desc(H)}", CNE,
                              "the nominal size can't be read", [], wd))

    # clear height and width ---------------------------------------------------------------
    if not fixed:
        for dim, lim, cite, nom, clear, note_dim in (
                ("height", C.MIN_CLEAR_HEIGHT, C.MIN_HEIGHT_CITE, H, w.clear_height, "single_hung"),
                ("width", C.MIN_CLEAR_WIDTH, C.MIN_WIDTH_CITE, W, w.clear_width, "slider")):
            req = f"Net clear {dim} >= {lim.value:g} in"
            if clear and clear["status"] == "parsed":
                v = PASS if clear["inches"] >= lim.value else FAIL
                crit.append(_guard_ocr(Criterion(req, cite.ref(), f"clear {dim} column {_len_desc(clear)}", v,
                                                 f"scheduled clear {dim} {clear['inches']:g} in "
                                                 f"{'>=' if v == PASS else '<'} {lim.value:g}"), clear))
                continue
            if nom["status"] != "parsed":
                crit.append(Criterion(req, cite.ref(), f"nominal {dim} {_len_desc(nom)}", CNE,
                                      f"the nominal {dim} can't be read", [], wd))
                continue
            if nom["inches"] <= lim.value:
                cr = Criterion(req, cite.ref(), f"nominal {dim} {_len_desc(nom)} (upper bound)", FAIL,
                               f"the clear {dim} is less than the nominal {nom['inches']:g} in, so below "
                               f"{lim.value:g} in", ["POL-E-NOMINAL-UPPER"],
                               brief=f"nominal {dim} {fmt_in(nom['inches'])}, so the clear {dim} is under "
                                     f"{lim.value:g} in")
            else:
                cr = Criterion(req, cite.ref(), f"nominal {dim} {_len_desc(nom)} (upper bound)", CNE,
                               f"nominal {nom['inches']:g} in exceeds {lim.value:g} in; the clear {dim} is smaller "
                               "by the frame and is not given", ["POL-E-NOMINAL-UPPER", "POL-E-NO-FRAME-ASSUMPTION"],
                               wd)
                hung = w.operation in ("single_hung", "double_hung")
                if (dim == "height" and hung) or (dim == "width" and w.operation == "slider"):
                    cr.reason += (f". Note only: {half_note}, roughly {nom['inches'] / 2:g} in "
                                  "(POL-E-PARTIAL-OPENING)")
                    cr.policies.append("POL-E-PARTIAL-OPENING")
                    if nom["inches"] / 2 <= lim.value:
                        cr.policies.append("POL-E-AT-LIMIT")
                        at = (f"exactly the {lim.value:g} in minimum, leaving nothing for the frame"
                              if nom["inches"] / 2 == lim.value else f"below the {lim.value:g} in minimum")
                        cr.flags.append({"code": "partial_opening_at_minimum",
                                         "message": f"expect a Fail on clear {dim}: {half_note}, about "
                                                    f"{nom['inches'] / 2:g} in before the frame, {at}. "
                                                    f"Ask for the sash split and the "
                                                    "manufacturer's clear opening."})
            crit.append(_guard_ocr(cr, nom))

    # sill --------------------------------------------------------------------------------
    sreq = f"Bottom of clear opening <= {C.MAX_SILL.value:g} in above the floor"
    sref = C.MAX_SILL_CITE.ref()
    HH = w.head_height
    if w.sill_height and w.sill_height["status"] == "parsed":
        sill, read, used = w.sill_height["inches"], f"scheduled sill {_len_desc(w.sill_height)}", (w.sill_height,)
    elif HH["status"] == "parsed" and H["status"] == "parsed":
        sill = HH["inches"] - H["inches"]
        read = (f"derived frame sill = head height {HH['inches']:g} in - nominal height {H['inches']:g} in "
                f"= {sill:g} in ({fmt_in(sill)})")
        used = (HH, H)
    else:
        sill, read, used = None, f"head height {_len_desc(HH)}, nominal height {_len_desc(H)}", ()
    sbasis = "derived" if used == (HH, H) else "printed"
    if sill is None:
        crit.append(Criterion(sreq, sref, read, CNE, "the sill height can't be worked out", ["POL-E-SILL-LOWER"],
                              _settle(store, "PROJECT:ELEVATIONS")[0]))
    elif sill > C.MAX_SILL.value:
        crit.append(_guard_ocr(Criterion(sreq, sref, read, FAIL,
                                         f"the clear opening's bottom is at or above the {sill:g} in frame sill, "
                                         f"more than {C.MAX_SILL.value:g} in", ["POL-E-SILL-LOWER"],
                                         brief=(f"frame sill = {fmt_in(HH['inches'])} head − "
                                                f"{fmt_in(H['inches'])} height = {sill:g} in, above "
                                                f"{C.MAX_SILL.value:g} in" if used == (HH, H) else
                                                f"scheduled sill {sill:g} in, above {C.MAX_SILL.value:g} in"),
                                         basis=sbasis),
                               *used))
    else:
        cr = _guard_ocr(Criterion(sreq, sref, read, CNE,
                                  f"the frame sill is {sill:g} in ({C.MAX_SILL.value - sill:g} in below the "
                                  f"limit), but the clear opening's bottom sits higher by the bottom frame, "
                                  "which is not given", ["POL-E-SILL-LOWER"],
                                  f"{wd} or {_settle(store, 'PROJECT:ELEVATIONS')[0]}", basis=sbasis), *used)
        if cr.verdict == CNE and C.MAX_SILL.value - sill <= 1e-9:
            cr.policies.append("POL-E-AT-LIMIT")
            cr.flags.append({"code": "sill_at_limit",
                             "message": f"expect a Fail on sill height: the frame sill is exactly "
                                        f"{C.MAX_SILL.value:g} in, so any bottom frame puts the clear opening above "
                                        "the limit. Confirm with the manufacturer's clear-opening dimensions."})
        crit.append(cr)

    # what no schedule shows --------------------------------------------------------------------
    if not fixed:
        crit.append(Criterion("Operable from inside without keys or tools", C.OPERABLE.ref(),
                              "hardware not scheduled", CNE, "not shown on the schedule", ["POL-E-UNSEEN"], wd))
    scr = (w.screen_text or "").strip()
    crit.append(Criterion("Screens, bars or grilles release from inside", C.SCREENS.ref(),
                          f"SCREEN column {scr!r}" if w.screen_text is not None else "no screen column",
                          CNE, "a screen is scheduled; whether it releases from inside is not shown" if scr
                          else "no screen scheduled; any device fitted must release from inside", ["POL-E-UNSEEN"],
                          wd))
    crit.append(Criterion("Opens onto a public way, yard or court", C.PUBLIC_WAY.ref(), "not on the schedule", CNE,
                          "the window's location on the site is not shown", ["POL-E-UNSEEN"],
                          _settle(store, "PROJECT:FLOOR-PLANS")[0] + " or site plan"))
    return crit


def _number(text: str | None) -> float | None:
    """A net clear area in sq ft. Square-inch values are converted; a bare number
    outside 0-50 is refused (likely square inches or a misread), as is anything else."""
    if not text:
        return None
    m = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*(SF|SQ\.?\s*FT\.?|FT2|FT²|SQ\.?\s*IN\.?|SI|IN2|IN²)?\s*", text.upper())
    if not m:
        return None
    v = float(m.group(1))
    unit = re.sub(r"[ .]", "", m.group(2) or "")
    if unit in ("SQIN", "SI", "IN2", "IN²"):
        return v / 144
    if not unit and not (0 < v <= 50):
        return None
    return v


def _window_evidence(w: Window, schedule: Schedule) -> list[dict]:
    src = f"{w.src['file']} table row {_row(w.src)}"
    labels = schedule.columns.labels
    roles = schedule.columns.roles
    ev = []
    for role in ("mark", "room", "width", "height", "operation", "type_mark", "head_height", "sill_height",
                 "net_clear_area", "egress", "screen"):
        if role in roles:
            ev.append(_ev(f"{labels[roles[role]]} ({role.replace('_', ' ')})", w.raw.get(role), src))
    return ev


def _window_flags(w: Window) -> list[dict]:
    fl = list(w.flags) + list(w.room_class.get("flags", []))
    for d in (w.width, w.height, w.head_height, w.sill_height):
        if d:
            fl += [f for f in d.get("flags", []) if f["code"] == "ocr_repair"]
    return fl


_SHORT = (("Opens", "opening type"), ("Net clear opening", "net clear area"), ("Net clear height", "clear height"),
          ("Net clear width", "clear width"), ("Bottom", "sill height"), ("Operable", "hardware (keys/tools)"),
          ("Screens", "screens"), ("Opens onto", "public way, yard or court"))


def short_name(c: Criterion) -> str:
    return next((s for p, s in reversed(_SHORT) if c.requirement.startswith(p)), c.requirement)


def _summary(crit: list[Criterion], verdict: str) -> str:
    fails = [c for c in crit if c.verdict == FAIL]
    if verdict == FAIL:
        return " ".join(f"{short_name(c).capitalize()}: {c.read}; {c.reason}." for c in fails)
    if verdict == CNE:
        measurable = [c for c in crit if c.verdict == CNE and "POL-E-UNSEEN" not in c.policies]
        bits = []
        for c in measurable:
            n = short_name(c)
            if n == "net clear area" and "nominal" in c.read:
                n += f" (nominal {c.read.split('= ')[-1].replace(' (upper bound)', '')} is only an upper bound)"
            elif n == "sill height" and c.basis == "derived":
                n += f" (frame sill {c.read.split('= ')[-1]})"
            elif n == "net clear area" and "below" in c.reason:
                n += " (meets only the grade-floor limit)"
            bits.append(n)
        lead = "Nothing fails at nominal size. " if not fails else ""
        out = lead + ("Not settled by the schedule: " + "; ".join(bits) + "." if bits else "")
        return (out + " Also unverified (never on a schedule): hardware, screens, public way.").strip()
    return "Every requirement is met by scheduled values."


def check_egress(store: Store, ca: CodeAnalysis, schedule: Schedule) -> tuple[list[Finding], list[Finding], list[Attention]]:
    """Returns (room findings, window findings, attention items)."""
    attn: list[Attention] = []
    occ = occupancy_scope(ca)
    has_egress_col = "egress" in schedule.columns.roles
    if not has_egress_col:
        attn.append(Attention("no_egress_column", "The window schedule has no EGRESS column",
                              "No window is designated as an escape opening. Every sleeping room is judged from all "
                              "of its windows as candidates (POL-E-NO-EGRESS-COLUMN).", []))

    # rooms in schedule order ---------------------------------------------------------
    rooms: "OrderedDict[str, list[Window]]" = OrderedDict()
    for w in schedule.windows:
        rooms.setdefault(w.room_key, []).append(w)

    window_findings: dict[str, Finding] = {}
    window_crit: dict[str, list[Criterion]] = {}
    room_findings: list[Finding] = []

    def wid(w):
        return f"W-{w.mark}"

    for key, ws in rooms.items():
        names = list(dict.fromkeys(w.room_name for w in ws))
        kinds = {w.room_class["kind"] for w in ws}
        kind = "sleeping" if "sleeping" in kinds else ("ambiguous" if "ambiguous" in kinds else "not_sleeping")
        room_name = next((w.room_name for w in ws if not w.room_class.get("flags")), ws[0].room_name)
        rid = f"R-{key.replace(' ', '-')}"
        room_flags = []
        if len(names) > 1:
            room_flags.append({"code": "room_name_variants",
                               "message": f"one room number, several spellings: {', '.join(repr(n) for n in names)} "
                                          "(POL-E-ROOM-KEY)"})
        story = story_scope(ca, key)

        for w in ws:
            src_pol = []
            fl = _window_flags(w)
            if kind == "not_sleeping" or (kind == "ambiguous" and w.egress is not True):
                why = (f"{w.room_name!r} is not a sleeping room" if kind == "not_sleeping" else
                       f"{w.room_name!r} is not clearly a sleeping room (flagged for review)")
                if w.egress:
                    fl.append({"code": "egress_in_non_sleeping_room",
                               "message": "marked egress, but the room is not a sleeping room"})
                window_findings[wid(w)] = Finding(
                    wid(w), "egress_window", f"Window {w.mark}, {w.room_name}", NA,
                    f"{why}; 1030.1 requires escape openings in sleeping rooms.", [C.SCOPE_SLEEPING.ref()],
                    _window_evidence(w, schedule), [], [], fl,
                    ["POL-E-NOT-SLEEPING" if kind == "not_sleeping" else "POL-E-SLEEPING"])
                continue
            crit = evaluate_window(w, store)
            window_crit[wid(w)] = crit
            if w.egress is False or not has_egress_col:
                why = ("Not marked egress" if has_egress_col else
                       "The schedule has no EGRESS column, so no window is designated")
                window_findings[wid(w)] = Finding(
                    wid(w), "egress_window", f"Window {w.mark}, {w.room_name}", NA,
                    f"{why}; 1030 needs one complying opening per sleeping room, not every window. "
                    f"Considered in {rid}.", [C.SCOPE_SLEEPING.ref()], _window_evidence(w, schedule), [], [], fl,
                    ["POL-E-NOT-DESIGNATED"] + ([] if has_egress_col else ["POL-E-NO-EGRESS-COLUMN"]),
                    related=[rid])
                continue
            # designated (or undesignatable) egress window
            v = worst([c.verdict for c in crit])
            scope_notes = []
            for sc in (occ, story):
                if sc.verdict == NA:
                    v = NA
                elif sc.verdict == CNE and v in (PASS, FAIL):
                    scope_notes.append(f"would be {v}, but {sc.reason}")
                    v = CNE
            if kind == "ambiguous":
                fl.append({"code": "egress_in_ambiguous_room",
                           "message": "marked egress in a room whose use is unclear; evaluated as if a sleeping room"})
            if w.egress is None:
                fl.append({"code": "egress_designation_unknown",
                           "message": "no EGRESS column" if not has_egress_col else
                           f"EGRESS cell {w.egress_text!r} is neither yes nor no"})
            fl += [f for c in crit for f in c.flags]
            pols = list(dict.fromkeys(p for c in crit for p in c.policies)) + ["POL-E-SCOPE"]
            summary = _summary(crit, v) if v != NA else f"1030 does not apply: {occ.reason}; {story.reason}."
            if scope_notes:
                summary = "; ".join(scope_notes) + ". " + summary
            settle = list(dict.fromkeys(c.settle for c in crit if c.settle and c.verdict == CNE))
            working = [f"scope: {occ.reason} ({occ.cite}); {story.reason} ({story.cite})"]
            window_findings[wid(w)] = Finding(
                wid(w), "egress_window", f"Window {w.mark}, {w.room_name}", v, summary,
                list(dict.fromkeys(c.code for c in crit)), _window_evidence(w, schedule), crit, working, fl, pols,
                [], settle, [rid])

        if kind != "sleeping":
            continue

        # room roll-up (POL-E-ROOM-ROLLUP) -------------------------------------------------
        designated = [w for w in ws if w.egress is True] if has_egress_col else []
        dv = {wid(w): window_findings[wid(w)].verdict for w in designated}
        pols = ["POL-E-ROOM-ROLLUP", "POL-E-SLEEPING", "POL-E-ROOM-KEY"]
        working = [f"windows in this room: {', '.join(wid(w) for w in ws)}",
                   f"designated egress: {', '.join(f'{k} {v}' for k, v in dv.items()) or 'none'}"]
        flags = room_flags + [f for w in ws for f in w.room_class.get("flags", [])]
        settle = []
        if any(v == PASS for v in dv.values()):
            verdict = PASS
            summary = f"{next(k for k, v in dv.items() if v == PASS)} complies."
        elif any(v == CNE for v in dv.values()):
            verdict = CNE
            cn = [k for k, v in dv.items() if v == CNE]
            fl_ = [k for k, v in dv.items() if v == FAIL]
            summary = (f"{', '.join(cn)} could not be evaluated" + (f"; {', '.join(fl_)} fails" if fl_ else "")
                       + ". The room has a complying opening only if " + ("it" if len(cn) == 1 else "one of them")
                       + " is shown to comply.")
            settle = list(dict.fromkeys(s for k in cn for s in window_findings[k].settle))
        else:
            cands = [w for w in ws if w not in designated]
            cv = {}
            for w in cands:
                c = window_crit.get(wid(w)) or evaluate_window(w, store)
                cv[wid(w)] = worst([x.verdict for x in c])
            working.append("other windows as candidates: "
                           + (", ".join(f"{k} {'could comply' if v != FAIL else 'cannot comply'}"
                                        for k, v in cv.items()) or "none"))
            possible = [k for k, v in cv.items() if v != FAIL]
            lead = ("No window is designated as the escape opening" if not designated else
                    f"The designated opening{'s' if len(designated) > 1 else ''} "
                    f"({', '.join(dv)}) fail{'' if len(designated) > 1 else 's'}")
            if possible:
                verdict = CNE
                code = "no_opening_designated" if not designated else "no_complying_opening_designated"
                summary = (f"{lead}; {', '.join(possible)} could comply at nominal size but is not marked egress. "
                           "Ask the architect to designate a complying opening.")
                flags.append({"code": code, "message": summary})
                settle = list(dict.fromkeys(s for k in possible for s in
                                            (window_findings[k].settle or [_settle(store, 'PROJECT:WINDOW-DETAILS')[0]])))
                if not settle:
                    settle = [_settle(store, "PROJECT:WINDOW-DETAILS")[0]]
            else:
                verdict = FAIL
                summary = (f"{lead}, and no other window in the room could comply. "
                           "Unless Exception 2 applies (an exit door to a public way), the room has no escape opening.")
                pols.append("POL-E-EXCEPTION-2")
                settle = [_settle(store, "PROJECT:FLOOR-PLANS")[0] + " (Exception 2: exit door)"]
            if not has_egress_col:
                pols.append("POL-E-NO-EGRESS-COLUMN")
        for sc in (occ, story):
            if sc.verdict == NA:
                verdict, summary = NA, f"1030 does not apply: {sc.reason}."
            elif sc.verdict == CNE and verdict in (PASS, FAIL):
                summary = f"would be {verdict}, but {sc.reason}. " + summary
                verdict = CNE
        working.insert(0, f"scope: {occ.reason}; {story.reason}")
        room_findings.append(Finding(
            rid, "egress_room", f"{room_name} (room {key})", verdict, summary,
            [C.SCOPE_SLEEPING.ref()] + ([C.EXCEPTION_2.ref()] if verdict == FAIL else []),
            [_ev("windows", ", ".join(f"{w.mark} ({w.operation_text}, egress {w.egress_text!r})" for w in ws),
                 f"{schedule.file}, LOCATION {', '.join(repr(n) for n in names)}")],
            [], working, flags, pols, [], settle, [wid(w) for w in ws],
            unresolved=([f"IBC 1030.1 Exception 2 (an exit door to a public way), which the "
                         f"{_doc_title(store, 'PROJECT:FLOOR-PLANS').lower()} (not provided) would show"]
                        if verdict == FAIL else [])))

    ordered_windows = [window_findings[f"W-{w.mark}"] for w in schedule.windows]
    return room_findings, ordered_windows, attn


# =========================================================================== #
# Cross-checks and run-all
# =========================================================================== #

@dataclass
class Results:
    height: Finding
    rooms: list[Finding]
    windows: list[Finding]
    attention: list[Attention]
    unavailable_amendments: list[str] = field(default_factory=list)  # titles from the manifest
    project: str = ""                                                # the code analysis project description

    @property
    def all(self) -> list[Finding]:
        return [self.height, *self.rooms, *self.windows]


def schedule_gaps(marks: list[str]) -> str:
    """'9, 15-19' for whole-number marks with numbers missing between the lowest and highest; '' otherwise."""
    if not marks or not all(re.fullmatch(r"\d+", m.strip()) for m in marks):
        return ""
    have = {int(m) for m in marks}
    runs: list[list[int]] = []
    for n in range(min(have), max(have) + 1):
        if n in have:
            continue
        if runs and n == runs[-1][1] + 1:
            runs[-1][1] = n
        else:
            runs.append([n, n])
    return ", ".join(str(a) if a == b else f"{a}–{b}" for a, b in runs)


def run_checks(store: Store, ca: CodeAnalysis, schedule: Schedule) -> Results:
    height, a1 = check_height(store, ca)
    rooms, windows, a2 = check_egress(store, ca, schedule)
    attn = a1 + a2
    likely = [(f.id, fl["message"]) for f in windows for fl in f.flags
              if fl["code"] in ("sill_at_limit", "partial_opening_at_minimum")]
    if likely:
        attn.insert(0, Attention("likely_fails", "Likely Fails the schedule can't prove",
                                 " | ".join(f"{i}: {m}" for i, m in likely), list(dict.fromkeys(i for i, _ in likely))))
    gaps = schedule_gaps([w.mark for w in schedule.windows])
    if gaps:
        attn.append(Attention("schedule_number_gaps", "Window numbers skip",
                              f"The schedule has no window {gaps}. Rows may have been lost in scanning, or the windows "
                              "renumbered; check the schedule sheet (POL-GEN-SCHEDULE-GAPS).", []))
    claim = ca.facts.get("egress_claim")
    bad = [r for r in rooms if r.verdict in (FAIL, CNE)]
    if claim and bad:
        attn.append(Attention(
            "egress_claim_not_supported", "Code analysis claim about escape openings is not supported",
            f"The code analysis says {claim.value!r} (table row {_row(claim.src)}). The schedule does not show a "
            f"complying opening in: " + "; ".join(f"{r.subject} ({r.verdict})" for r in bad) + ".",
            [r.id for r in bad]))
    ocr = [(f.id, fl["message"]) for f in [height, *rooms, *windows] for fl in f.flags
           if fl["code"] in ("ocr_repair", "ocr_room_name", "label_split_word")]
    ocr += [("schedule", n["message"]) for n in schedule.columns.notes if n["code"] == "header_split_word"]
    if ocr:
        seen = list(dict.fromkeys(f"{i}: {m}" for i, m in ocr))
        attn.append(Attention("ocr_readings", "OCR damage the tool read through",
                              "Confirm these on the sheets: " + " | ".join(seen),
                              list(dict.fromkeys(i for i, _ in ocr if i != "schedule"))))
    amb = [w for w in windows if any(f["code"] in ("ambiguous_room", "unrecognised_room") for f in w.flags)]
    if amb:
        attn.append(Attention("ambiguous_rooms", "Rooms that may be used for sleeping",
                              "Not treated as sleeping rooms: " + "; ".join(sorted({w.subject.split(', ', 1)[1]
                                                                                   for w in amb}))
                              + ". If any is a sleeping room, it needs an escape opening (IBC 1030.1).",
                              [w.id for w in amb]))
    attn.append(Attention("unscheduled_rooms", "Sleeping rooms with no window are invisible to this tool",
                          "The tool only knows rooms that appear in the window schedule. A bedroom with no scheduled "
                          "window would need an escape opening too; check the floor plans "
                          f"({_doc_title(store, 'PROJECT:FLOOR-PLANS')}, not provided).", []))
    for n in schedule.columns.notes:
        if n["code"] in ("type_columns_swapped", "operation_column_unrecognised", "duplicate_role"):
            attn.append(Attention(n["code"], "Window schedule columns", n["message"], []))
    if schedule.columns.missing:
        attn.append(Attention("missing_columns", "Window schedule columns not found",
                              "No column for: " + ", ".join(schedule.columns.missing), []))
    for d in schedule.dropped_rows:
        attn.append(Attention("schedule_row_skipped", "Window schedule row skipped",
                              f"table row {d['grid_row'] + 1}: {d['reason']} ({d['texts']})", []))
    if ca.unmatched:
        attn.append(Attention("code_analysis_unread", "Code analysis rows not used",
                              "; ".join(f"{u['label']!r}" for u in ca.unmatched), []))
    amend = [d.get("title", d["id"]) for d in store.data["documents"]
             if d.get("kind") == "local_amendments" and d["status"] == "unavailable"]
    proj = ca.facts.get("project")
    confidence.assign(height, rooms, windows)
    return Results(height, rooms, windows, attn, amend, proj.value if proj else "")

"""Render REPORT.md and findings.json from the findings.

The report is for a plan checker writing a correction letter. Order: what fails (worded
as correction items), what to check before relying on the tool, what to ask the
architect for, then the evidence tables, then an appendix with the rules, code lines
and inputs. Every finding keeps its verdict, code section and evidence; internal ids
and file paths stay in the appendix and in findings.json.

Deterministic: no timestamps, fixed ordering, input files named by basename and sha256.
"""
from __future__ import annotations

import json
import re

from .checks import Results
from .findings import CNE, FAIL, NA, PASS, VERDICTS, Criterion, Finding
from .policies import POLICIES

_LINE = re.compile(r"\s*\(([^()]*?\.(?:md|html)) lines? ([\d-]+)\)")
_DOC = re.compile(r"\(([A-Z][A-Z0-9]*(?::[A-Z0-9.\-]+)+), not provided(?:; related through footnote (\w))?\)")
_ID = re.compile(r"(?<![\[#\w-])([HRW]-\d+)\b")
_OCR_CODES = ("ocr_repair", "ocr_room_name", "label_split_word")

# What to ask for, by manifest document id. Anything else falls back to the manifest title.
_REQUEST = {
    "PROJECT:WINDOW-DETAILS": "Manufacturer data or window type details{types}: the net clear opening (width, "
                              "height, and the height of its bottom above the floor), the operating hardware "
                              "(1030.1.1: no keys or tools) and screen release from inside (1030.5)",
    "PROJECT:ELEVATIONS": "Elevations or wall sections dimensioning each escape window's sill and head",
    "PROJECT:FLOOR-PLANS": "Floor plans showing room uses, any exterior door from a sleeping room (1030.1 Exception "
                           "2), and that each escape window opens onto a yard, court or public way",
    "PROJECT:BUILDING-SECTIONS": "Building sections or roof plan dimensioning the height to the average of the "
                                 "highest roof surface",
    "PROJECT:C1.0:CIVIL": "The civil sheet with the grade plane calculation",
}


# --------------------------------------------------------------------------- helpers

def _md(text) -> str:
    """Escape table pipes and newlines."""
    return str(text if text is not None else "").replace("|", "\\|").replace("\n", " ")


def _plain(text: str) -> str:
    """Drop file/line parentheticals and policy ids from body text (the appendix keeps them)."""
    text = _LINE.sub("", text)
    text = re.sub(r"\s*\(POL-[A-Z0-9-]+\)", "", text)
    text = re.sub(r"\s*\(resolver rule [^)]*\)", "", text)
    text = re.sub(r"\s*\(authority: [^)]*\)", "", text)
    return text


def _sections(*refs: str) -> str:
    """'IBC 1030.2 (file line 35); IBC 1030.3 (...)' -> 'IBC 1030.2; IBC 1030.3', deduplicated."""
    parts = [p.strip() for r in refs for p in _plain(r).split(";") if p.strip()]
    return "; ".join(dict.fromkeys(parts))


def _link(fid: str) -> str:
    return f"[{fid}](#{fid.lower()})"


def _room(f: Finding) -> str:
    return f.subject.split(" (room ")[0]


def _brief(c: Criterion) -> str:
    return c.brief or f"{_plain(c.read)}; {_plain(c.reason)}"


def _docs(settle: str) -> list[tuple[str, str, str]]:
    """[(title, id, footnote)] named in one 'would settle it' entry ('A (ID, not provided) or B (ID2, ...)')."""
    out, start = [], 0
    for m in _DOC.finditer(settle):
        title = re.split(r";\s*|\s+or\s+", settle[start:m.start()])[-1].strip()
        out.append((title, m.group(1), m.group(2) or ""))
        start = m.end()
    return out


def _linkify(text: str) -> str:
    """Link bare finding ids (W-11) in running text."""
    return _ID.sub(lambda m: _link(m.group(1)), text)


def _cap(text: str) -> str:
    return text[:1].upper() + text[1:]


def _type_mark(f: Finding) -> str:
    return next((e["value"] for e in f.evidence if "(type mark)" in e["label"]), "") or ""


def _ev(f: Finding, role: str) -> str:
    return next((e["value"] for e in f.evidence if e["label"].endswith(f"({role})")), "") or ""


def _bound(c: Criterion) -> str:
    """The number a schedule-derived criterion rests on, as a bound: '≤ 10.00 sq ft', '≥ 32 in'."""
    if c.requirement.startswith("Net clear opening"):
        m = re.search(r"= ([\d.]+) sq ft", c.read)
        return f"≤ {m.group(1)} sq ft" if m else ""
    if c.requirement.startswith("Net clear"):
        m = re.search(r"= ([\d.]+) in", c.read)
        return f"≤ {m.group(1)} in" if m else ""
    if c.requirement.startswith("Bottom"):
        m = re.search(r"= ([\d.]+) in \(", c.read)
        if m:
            return f"≥ {m.group(1)} in" if "frame sill" in c.read else f"{m.group(1)} in"
    return ""


def _cell(c: Criterion | None) -> str:
    if c is None:
        return "—"
    b = _bound(c)
    if c.verdict == FAIL:
        if not b and c.read.startswith("fixed"):
            b = "does not open"
        return "**Fail**" + (f" ({b})" if b else "")
    if c.verdict == PASS:
        return "Met" + (f" ({b})" if b else "")
    return f"? {b}".strip() + (" ⚠" if c.flags else "")


def _crit(f: Finding, prefix: str) -> Criterion | None:
    return next((c for c in f.criteria if c.requirement.startswith(prefix)), None)


# --------------------------------------------------------------------------- sections

def _n_corrections(results: Results) -> int:
    failed_rooms = [r for r in results.rooms if r.verdict == FAIL]
    in_rooms = {w for r in failed_rooms for w in r.related}
    return ((results.height.verdict == FAIL) + len(failed_rooms)
            + sum(1 for w in results.windows if w.verdict == FAIL and w.id not in in_rooms))


def _header(results: Results, counts: dict, out: list[str]) -> None:
    out.append("# Plan check report: building height and emergency escape openings")
    out.append("")
    if results.project:
        out.append(f"**Project:** {_md(results.project)}")
        out.append("")
    amend = (f" {'; '.join(results.unavailable_amendments)} were not provided, so every verdict is subject to them."
             if results.unavailable_amendments else "")
    out.append("Checked against IBC 2018 Table 504.3 (allowable building height) and Section 1030 (emergency escape "
               "and rescue openings), as printed." + amend)
    out.append("")
    out.append("**Result: " + ", ".join(f"{counts[v]} {v}" for v in (FAIL, CNE, PASS, NA)) + ".**")
    n_items = _n_corrections(results)
    if counts[FAIL] and n_items != counts[FAIL]:
        out.append(f"The {counts[FAIL]} Fails are {n_items} correction items (§1): a room and its failing window are "
                   "one problem.")
    if counts[PASS] == 0 and any(f.verdict == CNE for f in results.windows):
        out.append("Nothing passes because a window schedule gives nominal sizes, which include the frame, and the "
                   "code regulates the net clear opening, which is always smaller. A nominal size can prove a Fail, "
                   "never a Pass.")
    out.append("")


def _corrections(results: Results, by_id: dict, out: list[str]) -> None:
    """Numbered correction items, grouped by room."""
    out.append("## 1. Corrections")
    out.append("")
    out.append("Raw material for the correction letter: the problem, the arithmetic and the deciding code section. "
               "Each ID links to its evidence.")
    out.append("")
    items, covered = [], []
    h = results.height
    if h.verdict == FAIL:
        body = [_plain(h.summary)]
        for fl in h.flags:
            if fl["code"] == "architect_allowable_mismatch":
                body.append("Also revise the code analysis: " + _plain(fl["message"]).replace(
                    "The code analysis states", "it states", 1))
        items.append((f"**Building height exceeds Table 504.3** ({_link(h.id)})", body,
                      _sections(h.code_refs[0].split(" = ")[0])))
        covered.append(h.id)
    for r in results.rooms:
        if r.verdict != FAIL:
            continue
        body, codes = [], []
        for wid in r.related:
            w = by_id[wid]
            if w.verdict == FAIL:
                fails = [c for c in w.criteria if c.verdict == FAIL]
                body.append(f"{_link(w.id)}, the designated escape window: " +
                            "; ".join(f"{_brief(c)} ({_sections(c.code)})" for c in fails) + ".")
                codes += [c.code for c in fails]
                covered.append(w.id)
        others = next((x.split(": ", 1)[1] for x in r.working if x.startswith("other windows as candidates")), "")
        if others and others != "none":
            body.append(_linkify(f"Other windows in the room: {others}."))
        if "POL-E-EXCEPTION-2" in r.policies:
            body.append("This stands unless the room has an exit door that opens directly to a public way, yard or "
                        "court (IBC 1030.1 Exception 2); the floor plans would show it.")
        items.append((f"**{_room(r)} has no complying escape opening** ({_link(r.id)})", body,
                      _sections(*r.code_refs[:1], *codes)))
        covered.append(r.id)
    for w in results.windows:
        if w.verdict != FAIL or w.id in covered:
            continue
        fails = [c for c in w.criteria if c.verdict == FAIL]
        body = [_cap("; ".join(_brief(c) for c in fails)) + "."]
        room = next((r for r in results.rooms if w.id in r.related), None)
        if room is not None and room.verdict != FAIL:
            body.append(f"The room ({_link(room.id)}) is {room.verdict}: {_linkify(_plain(room.summary))}")
        win, where = w.subject.split(", ", 1)
        items.append((f"**{win} in {where} is designated as the escape opening but cannot be one** ({_link(w.id)})",
                      body, _sections(*[c.code for c in fails])))
        covered.append(w.id)
    if not items:
        out.append("None.")
    for n, (title, body, code) in enumerate(items, 1):
        out.append(f"{n}. {title}")
        for b in body:
            out.append(f"   - {b}")
        out.append(f"   - *Code:* {code}")
    out.append("")


def _checks(results: Results, by_id: dict, out: list[str]) -> None:
    out.append("## 2. Check these before relying on the report")
    out.append("")
    out.append("Places where the tool may be wrong, or where the drawings may hide a problem.")
    out.append("")
    bullets = []
    for a in results.attention:
        rel = (" (" + ", ".join(_link(r) for r in a.related) + ")") if a.related else ""
        if a.code == "likely_fails":
            for part in a.detail.split(" | "):
                fid, msg = part.split(": ", 1)
                m = re.match(r"expect a Fail on ([^:]+): (.*)", msg)
                head, rest = (m.group(1), m.group(2)) if m else ("a requirement", msg)
                bullets.append(f"**{_link(fid)} is a likely Fail on {head}.** {_cap(rest)}")
        elif a.code in ("architect_allowable_mismatch", "ocr_readings"):
            continue  # in Corrections item 1 / the OCR table below
        elif a.code == "egress_claim_not_supported":
            tally: dict[str, int] = {}
            for rid in a.related:
                tally[by_id[rid].verdict] = tally.get(by_id[rid].verdict, 0) + 1
            claim = re.search(r"says ('.*?') \((table row \d+)\)", a.detail)
            said = f"{claim.group(1)} ({claim.group(2)})" if claim else ""
            bullets.append(f"**The code analysis claim is not supported.** It says {said}; "
                           "the schedule proves a complying opening in none of the sleeping rooms (" +
                           ", ".join(f"{n} {v}" for v, n in tally.items()) + ").")
        else:
            bullets.append(f"**{a.title}.** {_plain(a.detail)}{rel}")
    for i in results.height.interpretations:
        bullets.append(f"**Interpretation in {_link(results.height.id)}.** {_cap(_plain(i))}")
    for b in bullets:
        out.append(f"- {b}")
    out.append("")
    ocr: dict[str, list[str]] = {}
    for f in results.all:
        for fl in f.flags:
            if fl["code"] in _OCR_CODES:
                ocr.setdefault(fl["message"], []).append(f.id)
    ocr_attn = next((a for a in results.attention if a.code == "ocr_readings"), None)
    if ocr_attn:
        for part in ocr_attn.detail.replace("Confirm these on the sheets: ", "").split(" | "):
            fid, msg = part.split(": ", 1)
            if fid == "schedule":
                ocr.setdefault(msg, []).append("schedule header")
    if ocr:
        out.append("**OCR damage the tool read through.** Confirm on the sheets:")
        out.append("")
        out.append("| Where | What was printed, and how it was read |")
        out.append("|---|---|")
        for msg, ids in ocr.items():
            where = ", ".join(_link(i) if re.fullmatch(r"[HRW]-[\w-]+", i) else i for i in dict.fromkeys(ids))
            out.append(f"| {where} | {_md(_plain(msg))} |")
        out.append("")


def _requests(results: Results, out: list[str]) -> None:
    out.append("## 3. Information to request")
    out.append("")
    out.append("What would settle the Could Not Evaluate findings, written as requests to the architect.")
    out.append("")
    reqs: dict[str, dict] = {}
    code_docs: dict[str, list[str]] = {}
    for f in results.all:
        if not (f.verdict == CNE or (f.verdict == FAIL and f.check != "egress_window")):
            continue  # a window that already fails needs a revision, not more information
        for s in f.settle:
            for title, did, foot in _docs(s):
                if not did.startswith("PROJECT:"):
                    code_docs.setdefault(title + (f" (footnote {foot})" if foot else ""), []).append(f.id)
                    continue
                r = reqs.setdefault(did, {"title": title, "ids": [], "types": []})
                r["ids"].append(f.id)
                if f.check == "egress_window" and _type_mark(f):
                    r["types"].append(_type_mark(f))
        for fl in f.flags:
            if fl["code"] in ("no_opening_designated", "no_complying_opening_designated"):
                cands = re.findall(r"([HRW]-\d+) could comply", " ".join(f.working))
                why = ("none is marked egress" if fl["code"] == "no_opening_designated" else
                       "the designated one fails")
                reqs.setdefault(f"designate:{f.id}", {
                    "title": "", "ids": [f.id], "types": [],
                    "text": f"Designate a complying escape opening for {_room(f)}: {why}"
                            + (f"; {', '.join(cands)} could comply at nominal size" if cands else "")})
    out.append("| # | Request | Settles |")
    out.append("|---|---|---|")
    order = [k for k in _REQUEST if k in reqs] + [k for k in reqs if k not in _REQUEST]
    for n, k in enumerate(order, 1):
        r = reqs[k]
        types = sorted(set(r["types"]))
        text = r.get("text") or _REQUEST.get(k, "Provide: {title}").format(
            title=r["title"], types=(f" for window type{'s' if len(types) > 1 else ''} {', '.join(types)}"
                                     if types else ""))
        out.append(f"| {n} | {_md(_linkify(text))} | {', '.join(_link(i) for i in dict.fromkeys(r['ids']))} |")
    out.append("")
    if code_docs:
        out.append("Code text the tool was not given, which the plan checker may want to confirm: " +
                   "; ".join(f"{t} ({', '.join(_link(i) for i in dict.fromkeys(ids))})" for t, ids in code_docs.items())
                   + ".")
        out.append("")


def _height(h: Finding, out: list[str]) -> None:
    out.append("## 4. Building height (IBC Table 504.3)")
    out.append("")
    out.append(f'<a id="{h.id.lower()}"></a>')
    out.append(f"### {h.id} · Building height · **{h.verdict}**")
    out.append("")
    out.append(_plain(h.summary))
    out.append("")
    if h.evidence:
        out.append("| Read from the code analysis | Value | Where |")
        out.append("|---|---|---|")
        for e in h.evidence:
            out.append(f"| {_md(e['label'])} | `{_md(e['value'])}` | {_md(e['source'].split(', label')[0])} |")
        out.append("")
    steps = [w for w in h.working if not w.startswith("footnote ")]
    notes = [w for w in h.working if w.startswith("footnote ")]
    if steps:
        out.append("**How it was decided:**")
        out.append("")
        out += [f"{n}. {_cap(_plain(s)).replace(' -> ', ' → ')}" for n, s in enumerate(steps, 1)]
        out.append("")
    if notes:
        out.append("**Footnotes on this cell:**")
        out.append("")
        for x in notes:
            x = re.sub(r"\s*Points to: .*$", " It points to code text not provided (see §3).", _plain(x))
            out.append("- " + x[0].upper() + x[1:])
        out.append("")
    out.append(f"**Code:** {_sections(*h.code_refs)}")
    out.append("")


def _rooms(results: Results, by_id: dict, out: list[str]) -> None:
    out.append("## 5. Sleeping rooms (IBC 1030.1)")
    out.append("")
    out.append("A sleeping room needs at least one complying escape opening. The room follows its designated egress "
               "window; with none designated, or all of them failing, its other windows are considered.")
    out.append("")
    scope = next((x for r in results.rooms for x in r.working if x.startswith("scope: ")), "")
    occ = scope[len("scope: "):].split("; ")[0] if scope else ""
    if occ:
        out.append(f"Scope: {_plain(occ)}. Each room's story comes from its number, using the code analysis room "
                   "numbering; 1030.1 covers sleeping rooms below the fourth story above grade plane.")
        out.append("")
    out.append("| ID | Room | Story | Verdict | Windows (EGRESS on the schedule) | Why | Code |")
    out.append("|---|---|---|---|---|---|---|")
    for r in results.rooms:
        wins = [f"{_link(wid)} (egress): {by_id[wid].verdict}" if by_id[wid].verdict != NA else
                f"{_link(wid)} (not egress)" for wid in r.related]
        v = f"**{r.verdict}**" if r.verdict == FAIL else r.verdict
        story = next((m.group(1) for x in r.working for m in [re.search(r"is on floor (\d+)", x)] if m), "?")
        why = _linkify(_plain(r.summary))
        for fl in r.flags:
            if fl["code"] == "room_name_variants":
                why += " The schedule spells this room more than one way; windows are grouped by room number."
        out.append(f'| <a id="{r.id.lower()}"></a>{r.id} | {_md(_room(r))} | {story} | {v} | {", ".join(wins)} | '
                   f"{_md(why)} | {_md(_sections(*r.code_refs))} |")
    out.append("")


def _windows(results: Results, out: list[str]) -> None:
    egress = [w for w in results.windows if w.verdict != NA]
    if not egress:
        return
    out.append("## 6. Egress windows (IBC 1030.2, 1030.3)")
    out.append("")
    out.append("Windows marked EGRESS on the schedule. How to read the results:")
    out.append("")
    out.append("- **Nominal size is an upper bound (≤).** It includes the frame, so the net clear area, height and "
               "width are at most the nominal figure. It can prove a Fail, never a Pass.")
    out.append("- **The sill is a lower bound (≥).** Sill = head height − window height, which is the frame's sill. "
               "The clear opening starts higher, by the depth of the bottom frame.")
    out.append("- **?** = not settled by the schedule. **⚠** = likely Fail (see §2). **Met** = satisfied as "
               "scheduled.")
    out.append("- **No schedule shows these, so they are open for every window below:** opening without keys or "
               "tools (IBC 1030.1.1), screens that release from inside (IBC 1030.5), and opening onto a public way, "
               "yard or court (IBC 1030.1). §3 lists what would settle them.")
    out.append("")
    out.append("| ID | Room | Type | Nominal W × H | Head | Opens (1030.2.1) | Area ≥ 5.7 sq ft (1030.2) | "
               "Clear height ≥ 24 in (1030.2.1) | Clear width ≥ 20 in (1030.2.1) | Sill ≤ 44 in (1030.3) | Verdict |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for w in egress:
        tm = _type_mark(w)
        v = f"**{w.verdict}**" if w.verdict == FAIL else w.verdict
        out.append(f'| <a id="{w.id.lower()}"></a>{w.id} | {_md(w.subject.split(", ", 1)[1])} | '
                   f"{_md(_ev(w, 'operation'))}" + (f" (type {_md(tm)})" if tm else "") + " | "
                   f"{_md(_ev(w, 'width'))} × {_md(_ev(w, 'height'))} | {_md(_ev(w, 'head height'))} | "
                   f"{_cell(_crit(w, 'Opens'))} | {_cell(_crit(w, 'Net clear opening'))} | "
                   f"{_cell(_crit(w, 'Net clear height'))} | {_cell(_crit(w, 'Net clear width'))} | "
                   f"{_cell(_crit(w, 'Bottom'))} | {v} |")
    out.append("")
    out.append("The area limit is 5.0 sq ft for a grade-floor opening (1030.2 Exception), and grade-floor status is "
               "not shown, so a nominal area fails only at or below 5.0. Values are as printed on the schedule; "
               "Appendix B gives each window's row.")
    out.append("")


def _not_applicable(results: Results, out: list[str]) -> None:
    na = [w for w in results.windows if w.verdict == NA]
    if not na:
        return
    out.append("## 7. Windows: Not Applicable")
    out.append("")
    out.append("| ID | Room | EGRESS cell | Verdict | Why | Code |")
    out.append("|---|---|---|---|---|---|")
    for w in na:
        if "POL-E-NOT-DESIGNATED" in w.policies:
            why = (f"Not marked egress; 1030.1 needs one escape opening per sleeping room, not every window. "
                   f"Considered in {', '.join(_link(r) for r in w.related)}.")
        elif "POL-E-NOT-SLEEPING" in w.policies:
            why = "Not a sleeping room (1030.1 applies to sleeping rooms)."
        elif "POL-E-SLEEPING" in w.policies:
            why = "Not clearly a sleeping room, so not evaluated. Confirm its use (see §2); if it is a sleeping room, it needs an escape opening."
        else:
            why = _plain(w.summary)
        egress_cell = _ev(w, "egress").strip() or "(blank)"
        out.append(f'| <a id="{w.id.lower()}"></a>{w.id} | {_md(w.subject.split(", ", 1)[1])} | {_md(egress_cell)} | '
                   f"{w.verdict} | {_md(why)} | {_md(_sections(*w.code_refs))} |")
    out.append("")


def _appendix(results: Results, inputs: list[dict], command: str, out: list[str]) -> None:
    fs = results.all
    out.append("## Appendix")
    out.append("")
    cites: dict[str, str] = {}
    for f in fs:
        for ref in [*f.code_refs, *(c.code for c in f.criteria)]:
            for part in ref.split(";"):
                m = re.match(r"\s*(.+?) \(([^()]*?\.(?:md|html)) lines? ([\d-]+)\)", part)
                if m:
                    cites.setdefault(m.group(1), f"`{m.group(2)}` line {m.group(3)}")
    out.append("### A. Code text cited")
    out.append("")
    out.append("Every code limit the checks use is quoted word for word from these lines; the tool refuses to run if "
               "a quote is not found there.")
    out.append("")
    out.append("| Section | Where in the code files |")
    out.append("|---|---|")
    for sec, where in sorted(cites.items()):
        out.append(f"| {_md(sec)} | {where} |")
    out.append("")
    out.append("### B. Where each value was read")
    out.append("")
    out.append("Rows are counted from 1 at the top of each table, header rows included.")
    out.append("")
    out.append("| ID | Source |")
    out.append("|---|---|")
    for f in fs:
        srcs = list(dict.fromkeys(e["source"].split(", label")[0] for e in f.evidence))
        rows: dict[str, list[str]] = {}
        other = []
        for x in srcs:
            m = re.fullmatch(r"(.+?) table row (\d+)", x)
            if m:
                rows.setdefault(m.group(1), []).append(m.group(2))
            else:
                other.append(x)
        srcs = [f"{k} table row{'s' if len(v) > 1 else ''} {', '.join(v)}" for k, v in rows.items()] + other
        if srcs:
            out.append(f"| {_link(f.id)} | {_md('; '.join(srcs))} |")
    out.append("")
    used: dict[str, list[str]] = {}
    for f in fs:
        for p in f.policies:
            used.setdefault(p, []).append(f.id)
    if results.unavailable_amendments:
        used.setdefault("POL-GEN-AMENDMENTS", [])
    for a in results.attention:
        for p in re.findall(r"POL-[A-Z0-9-]+", a.detail):
            used.setdefault(p, [])
    out.append("### C. Rules the tool applied")
    out.append("")
    out.append("Judgement calls are named rules, the same for every project, each with a test.")
    out.append("")
    out.append("| Rule | What it says | Rests on | Used by |")
    out.append("|---|---|---|---|")
    for pid in [p for p in POLICIES if p in used]:
        p = POLICIES[pid]
        ids = list(dict.fromkeys(used[pid]))
        by = ", ".join(_link(i) for i in ids)
        out.append(f"| `{p.id}` {_md(p.title)} | {_md(p.rule)} | {_md('; '.join(dict.fromkeys(p.rests_on)))} | "
                   f"{by or 'whole report'} |")
    out.append("")
    unused = [p for p in POLICIES if p not in used]
    if unused:
        out.append("Not needed for this project: " + ", ".join(f"`{p}` ({POLICIES[p].title})" for p in unused) + ".")
        out.append("")
    out.append("### D. Inputs")
    out.append("")
    out.append("| Input | File | sha256 (first 12) |")
    out.append("|---|---|---|")
    for i in inputs:
        out.append(f"| {i['role']} | `{i['name']}` | `{i['sha256'][:12]}` |")
    out.append("")
    out.append(f"Generated by `{command}`. The same findings are in `findings.json`.")
    out.append("")


def render(results: Results, inputs: list[dict], command: str) -> str:
    fs = results.all
    by_id = {f.id: f for f in fs}
    counts = {v: sum(f.verdict == v for f in fs) for v in VERDICTS}
    out: list[str] = []
    _header(results, counts, out)
    _corrections(results, by_id, out)
    _checks(results, by_id, out)
    _requests(results, out)
    _height(results.height, out)
    _rooms(results, by_id, out)
    _windows(results, out)
    _not_applicable(results, out)
    _appendix(results, inputs, command, out)
    return "\n".join(out)


def to_json(results: Results, inputs: list[dict]) -> str:
    doc = {
        "schema": "plancheck-findings/1",
        "inputs": inputs,
        "summary": {v: sum(f.verdict == v for f in results.all) for v in VERDICTS},
        "findings": [f.to_dict() for f in results.all],
        "attention": [a.to_dict() for a in results.attention],
        "policies": {pid: p.to_dict() for pid, p in POLICIES.items()},
    }
    return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"

"""Render REPORT.md and findings.json from the findings.

The report is for a plan checker writing a correction letter, and is written so a reader
without code training can follow it. Order:

1. Summary, with a short key to the verdicts, confidence and IDs.
2. Corrections to send: one short labelled item per problem (a room and its failing
   window are one problem).
3. Look at these yourself: where the tool may be wrong or the drawings may hide something.
4. What to ask the architect: the Could Not Evaluate findings as numbered requests.
5. Every finding in full, one block each with the same labelled lines: what was read,
   the arithmetic, the code section and the confidence. Windows the rule doesn't apply
   to are grouped by reason.
6. Appendix: code lines, named rules and input files, for checking the tool.

Standalone Markdown: no HTML, no in-page links, so it reads the same in any viewer.
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
_OCR_CODES = ("ocr_repair", "ocr_room_name", "label_split_word")

# What to ask for, by manifest document id. Anything else falls back to the manifest title.
_REQUEST = {
    "PROJECT:WINDOW-DETAILS": "Manufacturer data or window type details{types}: the clear opening (width, height, "
                              "and the height of its bottom above the floor), the hardware (it must open without "
                              "keys or tools, IBC 1030.1.1) and whether screens release from inside (IBC 1030.5).",
    "PROJECT:ELEVATIONS": "Elevations or wall sections that dimension each escape window's sill and head height.",
    "PROJECT:FLOOR-PLANS": "Floor plans showing what each room is used for, any door from a bedroom straight to "
                           "the outside (IBC 1030.1 Exception 2), and that each escape window opens onto a yard, "
                           "court or public way.",
    "PROJECT:BUILDING-SECTIONS": "Building sections or a roof plan that dimension the height to the average of the "
                                 "highest roof surface.",
    "PROJECT:C1.0:CIVIL": "The civil sheet with the grade plane calculation.",
}

# The measurable window requirements, in table order: requirement prefix -> plain label.
_TESTS = [
    ("Opens by normal operation", "Opens normally"),
    ("Net clear opening", "Opening area: at least {a} sq ft ({b} on the ground floor)"),
    ("Net clear height", "Opening height: at least {n} in"),
    ("Net clear width", "Opening width: at least {n} in"),
    ("Bottom of clear opening", "Sill: no more than {n} in above the floor"),
]


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
    return text.replace("\\'", "'")   # repr escapes a quote inside a quoted feet-inch value; viewers may show the slash


def _sections(*refs: str) -> str:
    """'IBC 1030.2 (file line 35); IBC 1030.3 (...)' -> 'IBC 1030.2; IBC 1030.3', deduplicated."""
    parts = [p.strip() for r in refs for p in _plain(r).split(";") if p.strip()]
    return "; ".join(dict.fromkeys(parts))


def _room(f: Finding) -> str:
    return f.subject.split(" (room ")[0]


def _where(f: Finding) -> str:
    """'BEDROOM 203' from 'Window 10, BEDROOM 203'."""
    return f.subject.split(", ", 1)[1] if ", " in f.subject else f.subject


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


def _cap(text: str) -> str:
    return text[:1].upper() + text[1:]


def _ev(f: Finding, role: str) -> str:
    return next((e["value"] for e in f.evidence if e["label"].endswith(f"({role})")), "") or ""


def _row(f: Finding) -> str:
    """The source table row a window was read from, or ''."""
    return next((m.group(1) for e in f.evidence for m in [re.search(r"table row (\d+)", e["source"])] if m), "")


def _crit(f: Finding, prefix: str) -> Criterion | None:
    return next((c for c in f.criteria if c.requirement.startswith(prefix)), None)


def _confidence(f: Finding, lead: str = "**Confidence:**") -> list[str]:
    """The confidence line, with its reasons as sub-bullets when there is more than one."""
    rs = [_cap(_plain(x).replace("rests only on a derived value", "rests only on a worked-out sill height")
               .replace("rests on a repaired room name", "rests on a room name corrected for a scanning error"))
          for x in f.confidence_reasons]
    if not rs:
        return [f"- {lead} {f.confidence}. It rests on values printed on the sheets."]
    if len(rs) == 1:
        return [f"- {lead} {f.confidence}. {rs[0]}."]
    return [f"- {lead} {f.confidence}, for {len(rs)} reasons:"] + [f"  - {x}." for x in rs]


def _heading(f: Finding, title: str) -> str:
    """The finding heading the eval scorer reads: '### ID · title · **Verdict**'."""
    return f"#### {f.id} · {title} · **{f.verdict}**"


def _correction_findings(results: Results) -> list[Finding]:
    """One finding per correction item: the height, each failed room, and each failing window not in one."""
    failed_rooms = [r for r in results.rooms if r.verdict == FAIL]
    in_rooms = {w for r in failed_rooms for w in r.related}
    return ([results.height] if results.height.verdict == FAIL else []) + failed_rooms + [
        w for w in results.windows if w.verdict == FAIL and w.id not in in_rooms]


def _rests(x: str) -> str:
    """'src/NOTES.md decision: X' -> 'project decision: X' (the reader has no repo)."""
    return re.sub(r"^src/NOTES\.md(?: decision)?[:,]\s*", "project decision: ", x)


# --------------------------------------------------------------------------- window wording

def _shows(c: Criterion) -> str:
    """What the schedule shows for one requirement, in plain words."""
    r = _plain(c.read)
    if c.requirement.startswith("Opens"):
        m = re.match(r"type ['\"](.+?)['\"] \((.+?)\)", r)
        if m:
            return f"{m.group(1)}: {'does not open' if m.group(2) == 'fixed' else 'a ' + m.group(2)}"
        return r
    if r.startswith("fixed"):
        return "no opening (fixed)"
    m = re.search(r"nominal ([\d.]+) in x ([\d.]+) in = [\d.]+ sq in = ([\d.]+) sq ft", r)
    if m:
        return f"{m.group(1)} × {m.group(2)} in = {m.group(3)} sq ft, including the frame"
    m = re.search(r"head height ([\d.]+) in - nominal height ([\d.]+) in = ([\d.]+) in", r)
    if m:
        return f"{m.group(1)} in head − {m.group(2)} in height = {m.group(3)} in, at the frame"
    m = re.search(r"nominal (?:height|width) .*= ([\d.]+) in", r)
    if m:
        return f"{m.group(1)} in, including the frame"
    m = re.search(r"scheduled sill .*?([\d.]+) in", r)
    if m:
        return f"{m.group(1)} in, as scheduled"
    return r


def _result(c: Criterion | None) -> str:
    if c is None:
        return "—"
    if c.verdict == FAIL:
        return "**Fail**"
    if c.verdict == PASS:
        return "Met"
    return "Not settled, likely Fail" if c.flags else "Not settled"


def _label(prefix: str, label: str, c: Criterion) -> str:
    nums = re.findall(r"[\d.]+", c.requirement)
    if prefix == "Net clear opening" and len(nums) >= 2:
        return label.format(a=nums[0], b=nums[1])
    return label.format(n=nums[0] if nums else "")


# --------------------------------------------------------------------------- sections

def _summary(results: Results, counts: dict, out: list[str]) -> None:
    out.append("# Plan check report: building height and emergency escape openings")
    out.append("")
    if results.project:
        out.append(f"**Project:** {_md(results.project)}")
        out.append("")
    out.append("## Summary")
    out.append("")
    items = _correction_findings(results)
    unsettled = counts[CNE]
    bottom = (f"{len(items)} correction{'s' if len(items) != 1 else ''} for the letter, {unsettled} finding"
              f"{'s' if unsettled != 1 else ''} these sheets can't settle, and "
              + ("nothing passes." if counts[PASS] == 0 else f"{counts[PASS]} pass."))
    out.append(f"- **Bottom line:** {bottom}")
    line = "- **Verdicts:** " + " · ".join(f"{counts[v]} {v}" for v in (FAIL, CNE, PASS, NA)) + "."
    if counts[FAIL] and len(items) != counts[FAIL]:
        line += (f" The {counts[FAIL]} Fails are {len(items)} corrections, because a bedroom and its failing window "
                 "count as one problem.")
    out.append(line)
    if counts[PASS] == 0 and any(f.verdict == CNE for f in results.windows):
        out.append("- **Why nothing passes:** the window schedule gives frame sizes. The real opening is always "
                   "smaller, so a frame size can prove a window too small but never big enough.")
    amend = (f" {'; '.join(results.unavailable_amendments)} were not provided, so every verdict is subject to them."
             if results.unavailable_amendments else "")
    out.append("- **What this is:** an automated check of the code analysis sheet and the window schedule. It "
               "checks two things only: building height and bedroom escape windows. Everything else on the code "
               "analysis (stories, floor area and so on) was not checked.")
    out.append("- **Checked against:** the 2018 IBC as printed: Table 504.3 (building height) and Section 1030 "
               "(emergency escape openings)." + amend)
    out.append("")
    out.append("**How to read this report**")
    out.append("")
    out.append("- **Verdicts.** **Fail:** breaks the rule. **Could Not Evaluate:** the rule applies, but these sheets "
               "can't settle it. **Pass:** meets the rule. **Not Applicable:** the rule doesn't apply here.")
    out.append("- **Confidence** says how likely a verdict is to stand once the full drawing set is seen. **High:** "
               "send the correction as written. **Medium:** one thing could change it; confirm it first, or send "
               "the correction with that condition stated. **Low:** more than one thing could change it; confirm "
               "them first, or send a request for information instead of a correction.")
    if any(c.basis == "derived" for w in results.windows for c in w.criteria):
        out.append("- **Sill heights are worked out,** not read: the schedule doesn't list them, so the sill is the "
                   "head height minus the window height. That is the bottom of the frame; the opening itself starts "
                   "a little higher.")
    out.append("- **Terms.** R-3 is the occupancy group (houses), V-B the construction type, and S13D a house-type "
               "sprinkler system (NFPA 13D). Head height is the floor to the top of the window. A casement opens on "
               "a side hinge; a single hung window opens only its bottom half. Scanning errors are letters or "
               "spaces the scan got wrong.")
    out.append("- **IDs.** H- is the building height, R- a bedroom, W- a window. Search for an ID to find its full "
               "entry in section 4.")
    out.append("")


def _corrections(results: Results, by_id: dict, out: list[str]) -> None:
    out.append("## 1. Corrections to send")
    out.append("")
    items = _correction_findings(results)
    if not items:
        out.append("None.")
        out.append("")
        return
    out.append("Each item is worded as raw material for the correction letter.")
    out.append("")
    for n, f in enumerate(items, 1):
        body: list[str] = []
        if f.check == "height":
            title = "Building height is over the limit"
            body.append(f"- **Problem:** {_plain(f.summary)}")
            for fl in f.flags:
                if fl["code"] == "architect_allowable_mismatch":
                    body.append("- **Also correct the code analysis:** " + _plain(fl["message"]).replace(
                        "The code analysis states", "it states", 1))
            body.append(f"- **Code:** {_sections(f.code_refs[0].split(' = ')[0])}")
        elif f.check == "egress_room":
            title = f"{_room(f)} has no working escape window"
            codes = list(f.code_refs[:1])
            why = []
            for wid in f.related:
                w = by_id[wid]
                if w.verdict == FAIL:
                    fails = [c for c in w.criteria if c.verdict == FAIL]
                    why.append(f"{w.id}, its escape window: " + "; ".join(_brief(c) for c in fails) + ".")
                    codes += [c.code for c in fails]
            others = next((x.split(": ", 1)[1] for x in f.working if x.startswith("other windows as candidates")), "")
            if others and others != "none":
                why.append(f"Other windows in the room: {others}.")
            body.append(f"- **Problem:** {_room(f)} needs at least one window a person can escape through, and has "
                        "none that works.")
            body.append("- **Why:** " + " ".join(why).replace("nominal ", "listed size "))
            if "POL-E-EXCEPTION-2" in f.policies:
                codes.append("IBC 1030.1 Exception 2")
                body.append("- **Unless:** the room has a door that opens straight to a public way, yard or court "
                            "(IBC 1030.1 Exception 2). The floor plans would show it.")
            body.append(f"- **Code:** {_sections(*codes)}")
        else:
            win = f.subject.split(", ", 1)[0]
            title = f"{win} in {_where(f)} is marked as the escape window but can't be one"
            fails = [c for c in f.criteria if c.verdict == FAIL]
            body.append(f"- **Problem:** {_cap('; '.join(_brief(c) for c in fails))}.")
            room = next((r for r in results.rooms if f.id in r.related), None)
            if room is not None and room.verdict != FAIL:
                body.append(f"- **The room ({room.id}):** {room.verdict}. {_plain(room.summary)}")
            body.append(f"- **Code:** {_sections(*[c.code for c in fails])}")
        out.append(f"**{n}. {title}** ({f.id})")
        out.append("")
        out += body
        out += _confidence(f, "**Confidence before sending:**")
        out.append("")


def _look(results: Results, by_id: dict, out: list[str]) -> None:
    out.append("## 2. Look at these yourself")
    out.append("")
    out.append("Places where the tool may be wrong, or where the drawings may hide a problem.")
    out.append("")
    bullets = []
    for a in results.attention:
        rel = (" (" + ", ".join(a.related) + ")") if a.related else ""
        if a.code == "likely_fails":
            for part in a.detail.split(" | "):
                fid, msg = part.split(": ", 1)
                m = re.match(r"expect a Fail on ([^:]+): (.*)", msg)
                head, rest = (m.group(1), m.group(2)) if m else ("a requirement", msg)
                bullets.append(f"**{fid} is likely to fail on {head}.** {_cap(rest)}")
        elif a.code in ("architect_allowable_mismatch", "ocr_readings"):
            continue  # in Corrections item 1 / the scanning list below
        elif a.code == "egress_claim_not_supported":
            tally: dict[str, int] = {}
            for rid in a.related:
                tally[by_id[rid].verdict] = tally.get(by_id[rid].verdict, 0) + 1
            claim = re.search(r"says ('.*?') \((table row \d+)\)", a.detail)
            said = f"{claim.group(1)} ({claim.group(2)})" if claim else ""
            bullets.append(f"**The code analysis claim is not supported.** It says {said}. The schedule does not "
                           "show a working escape window in any bedroom (" +
                           ", ".join(f"{n} {v}" for v, n in tally.items()) + ").")
        else:
            bullets.append(f"**{a.title}.** {_plain(a.detail)}{rel}")
    for i in results.height.interpretations:
        bullets.append(f"**A reading the brief decides ({results.height.id}).** {_cap(_plain(i))}")
    for b in bullets:
        out.append(f"- {b}")
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
        out.append("- **Scanning errors the tool read through.** Confirm each on the sheets:")
        for msg, ids in ocr.items():
            out.append(f"  - {', '.join(dict.fromkeys(ids))}: {_plain(msg)}")
    out.append("")


def _requests(results: Results, out: list[str]) -> None:
    out.append("## 3. What to ask the architect")
    out.append("")
    out.append("These would settle the Could Not Evaluate findings.")
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
                if f.check == "egress_window" and _ev(f, "type mark"):
                    r["types"].append(_ev(f, "type mark"))
        for fl in f.flags:
            if fl["code"] in ("no_opening_designated", "no_complying_opening_designated"):
                cands = re.findall(r"([HRW]-\d+) could comply", " ".join(f.working))
                why = ("none is marked egress" if fl["code"] == "no_opening_designated" else
                       "the one marked egress fails")
                reqs.setdefault(f"designate:{f.id}", {
                    "title": "", "ids": [f.id], "types": [],
                    "text": f"Mark an escape window for {_room(f)}: {why}"
                            + (f", but {', '.join(cands)} could work at its listed size." if cands else ".")})
    order = [k for k in _REQUEST if k in reqs] + [k for k in reqs if k not in _REQUEST]
    for n, k in enumerate(order, 1):
        r = reqs[k]
        types = sorted(set(r["types"]))
        text = r.get("text") or _REQUEST.get(k, "Provide: {title}.").format(
            title=r["title"], types=(f" for window type{'s' if len(types) > 1 else ''} {', '.join(types)}"
                                     if types else ""))
        out.append(f"{n}. {text} *Settles:* {', '.join(dict.fromkeys(r['ids']))}.")
    out.append("")
    if code_docs:
        out.append("Code text the tool was not given, which you may want to confirm: " +
                   "; ".join(f"{t} ({', '.join(dict.fromkeys(ids))})" for t, ids in code_docs.items()) + ".")
        out.append("")


def _height(h: Finding, out: list[str]) -> None:
    out.append("### Building height")
    out.append("")
    out.append(_heading(h, "Building height"))
    out.append("")
    out.append(f"- **Result:** {_plain(h.summary)}")
    out.append("")
    if h.evidence:
        out.append("| Read from the code analysis | Value | Where |")
        out.append("|---|---|---|")
        for e in h.evidence:
            out.append(f"| {_md(e['label'])} | {_md(e['value'])} | {_md(e['source'].split(', label')[0])} |")
        out.append("")
    steps = [w for w in h.working if not w.startswith("footnote ")]
    notes = [w for w in h.working if w.startswith("footnote ")]
    if steps:
        out.append("**How it was decided:**")
        out.append("")
        out += [f"{n}. {_cap(_plain(s)).replace(' -> ', ' → ')}" for n, s in enumerate(steps, 1)]
        out.append("")
    if notes:
        out.append("**Footnotes printed on this cell:**")
        out.append("")
        for x in notes:
            x = re.sub(r"\s*Points to: .*$", " It points to code text that was not provided.", _plain(x))
            out.append("- " + _cap(x))
        out.append("")
    out.append(f"- **Code:** {_sections(*h.code_refs)}")
    out += _confidence(h)
    out.append("")


def _rooms(results: Results, by_id: dict, out: list[str]) -> None:
    out.append("### Bedrooms")
    out.append("")
    out.append("Every bedroom needs at least one window a person can escape through (IBC 1030.1). A bedroom follows "
               "the window marked as its escape window. If none is marked, or the marked ones fail, its other windows "
               "are considered.")
    scope = next((x for r in results.rooms for x in r.working if x.startswith("scope: ")), "")
    occ = scope[len("scope: "):].split("; ")[0] if scope else ""
    if occ:
        out.append("")
        out.append(f"The rule covers this building because {_plain(occ)}. It covers bedrooms below the fourth story; "
                   "each room's floor comes from its room number, using the numbering on the code analysis.")
    out.append("")
    for r in results.rooms:
        story = next((m.group(1) for x in r.working for m in [re.search(r"is on floor (\d+)", x)] if m), "")
        out.append(_heading(r, _room(r) + (f", floor {story}" if story else "")))
        out.append("")
        wins = [f"{wid} (escape window): {by_id[wid].verdict}" if by_id[wid].verdict != NA else
                f"{wid} (not marked egress)" for wid in r.related]
        src = next((e["source"] for e in r.evidence), "")
        out.append(f"- **Windows:** {'; '.join(wins)}." + (f" Read from the {_plain(src).replace('.html,', ',')}."
                                                          if src else ""))
        why = (_plain(r.summary).replace("The designated opening", "The marked escape window")
               .replace("is designated as the escape opening", "is marked as the escape window")
               .replace("designate a complying opening", "mark a window that complies")
               .replace("at nominal size", "at its listed size"))
        for fl in r.flags:
            if fl["code"] == "room_name_variants":
                why += " The schedule spells this room more than one way; its windows are grouped by room number."
        out.append(f"- **Why:** {why}")
        out.append(f"- **Code:** {_sections(*r.code_refs)}")
        out += _confidence(r)
        out.append("")


def _windows(results: Results, out: list[str]) -> None:
    egress = [w for w in results.windows if w.verdict != NA]
    if not egress:
        return
    out.append("### Escape windows")
    out.append("")
    out.append("Windows marked EGRESS on the schedule. Each is tested against the five requirements a schedule can "
               "show. Three more can't be shown on any schedule, so they stay open for every window: it opens without "
               "keys or tools (IBC 1030.1.1), any screen releases from inside (IBC 1030.5), and it opens onto a yard, "
               "court or public way (IBC 1030.1). Section 3 asks for them. A fixed window "
               "doesn't open, so its size tests are skipped.")
    out.append("")
    for w in egress:
        out.append(_heading(w, f"{w.subject.split(', ', 1)[0]}, {_where(w)}"))
        out.append("")
        tm = _ev(w, "type mark")
        row = _row(w)
        read = (f"{_ev(w, 'operation')}" + (f" (type {tm})" if tm else "") +
                f", {_ev(w, 'width')} wide × {_ev(w, 'height')} high, head height {_ev(w, 'head height')}, "
                f"EGRESS {_ev(w, 'egress').strip() or '(blank)'}")
        out.append(f"- **Read from the window schedule" + (f", table row {row}" if row else "") + f":** {_md(read)}.")
        out.append("")
        out.append("| Requirement | Code | The schedule shows | Result |")
        out.append("|---|---|---|---|")
        for prefix, label in _TESTS:
            c = _crit(w, prefix)
            if c is None:
                continue
            out.append(f"| {_label(prefix, label, c)} | {_sections(c.code)} | {_md(_shows(c))} | {_result(c)} |")
        out.append("")
        likely = [fl["message"] for c in w.criteria for fl in c.flags
                  if fl["code"] in ("sill_at_limit", "partial_opening_at_minimum")]
        for msg in likely:
            m = re.match(r"expect a Fail on [^:]+: (.*)", msg)
            out.append(f"- **Likely to fail:** {_cap(m.group(1) if m else msg)}")
        if w.verdict == CNE:
            need = list(dict.fromkeys(t for s in w.settle for t, did, _ in _docs(s)
                                      if did in ("PROJECT:WINDOW-DETAILS", "PROJECT:ELEVATIONS")))
            if need:
                out.append(f"- **Would settle it:** {' or '.join(need).lower()}.")
        room = next((r for r in results.rooms if w.id in r.related), None)
        if room is not None:
            out.append(f"- **Room:** {_room(room)} ({room.id}, {room.verdict}).")
        out += _confidence(w)
        out.append("")


def _not_applicable(results: Results, out: list[str]) -> None:
    na = [w for w in results.windows if w.verdict == NA]
    if not na:
        return
    out.append("### Windows the rule doesn't apply to")
    out.append("")
    groups = [
        ("POL-E-NOT-SLEEPING", "**Not in a bedroom.** The escape-window rule applies to sleeping rooms only "
                               "(IBC 1030.1)."),
        ("POL-E-NOT-DESIGNATED", "**In a bedroom, but not marked egress.** A bedroom needs one escape window, not "
                                 "every window to be one (IBC 1030.1). Each is still considered in its bedroom's "
                                 "entry."),
        ("POL-E-SLEEPING", "**Room use unclear.** The name isn't clearly a bedroom, so the rule wasn't applied. If "
                           "people sleep there, it needs an escape window (IBC 1030.1). Confirm the room's use."),
    ]
    shown: set[str] = set()
    for pol, text in groups + [("", "**Other.**")]:
        ws = [w for w in na if w.id not in shown and (pol in w.policies or not pol)]
        if not ws:
            continue
        shown |= {w.id for w in ws}
        out.append(text)
        out.append("")
        out.append("| ID | Room | EGRESS cell | Schedule row | Verdict | Confidence |")
        out.append("|---|---|---|---|---|---|")
        for w in ws:
            out.append(f"| {w.id} | {_md(_where(w))} | {_md(_ev(w, 'egress').strip() or '(blank)')} | "
                       f"{_row(w) or '—'} | {w.verdict} | {w.confidence} |")
        out.append("")


def _appendix(results: Results, inputs: list[dict], command: str, out: list[str]) -> None:
    fs = results.all
    out.append("## Appendix: for checking the tool")
    out.append("")
    out.append("Not needed to read the verdicts. File names are the tool's input files; rule ids (`POL-…`) are the "
               "tool's named judgement calls. Table rows are counted from 1 at the top of each table, header rows "
               "included.")
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
    used: dict[str, list[str]] = {}
    for f in fs:
        for p in f.policies:
            used.setdefault(p, []).append(f.id)
    if results.unavailable_amendments:
        used.setdefault("POL-GEN-AMENDMENTS", [])
    if any(f.confidence for f in fs):
        used.setdefault("POL-GEN-CONFIDENCE", [])
    for a in results.attention:
        for p in re.findall(r"POL-[A-Z0-9-]+", a.detail):
            used.setdefault(p, [])
    out.append("### B. Rules the tool applied")
    out.append("")
    out.append("Judgement calls are named rules, the same for every project, each with a test.")
    out.append("")
    out.append("| Rule | What it says | Rests on | Used by |")
    out.append("|---|---|---|---|")
    for pid in [p for p in POLICIES if p in used]:
        p = POLICIES[pid]
        by = ", ".join(dict.fromkeys(used[pid]))
        out.append(f"| `{p.id}` {_md(p.title)} | {_md(p.rule)} | "
                   f"{_md('; '.join(dict.fromkeys(_rests(x) for x in p.rests_on)))} | {by or 'whole report'} |")
    out.append("")
    unused = [p for p in POLICIES if p not in used]
    if unused:
        out.append("Not needed for this project: " + ", ".join(f"`{p}` ({POLICIES[p].title})" for p in unused) + ".")
        out.append("")
    out.append("### C. Inputs")
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
    _summary(results, counts, out)
    _corrections(results, by_id, out)
    _look(results, by_id, out)
    _requests(results, out)
    out.append("## 4. Every finding in full")
    out.append("")
    out.append("Each entry gives the verdict, what was read from the sheets, any arithmetic, the code section and the "
               "confidence.")
    out.append("")
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

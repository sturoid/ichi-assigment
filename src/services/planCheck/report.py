"""Render REPORT.md and findings.json from the findings. Deterministic: no timestamps,
fixed ordering, input files named by basename and sha256."""
from __future__ import annotations

import json

from .checks import Results
from .findings import CNE, FAIL, NA, PASS, VERDICTS, Finding
from .policies import POLICIES

ICON = {FAIL: "❌", CNE: "❓", PASS: "✅", NA: "➖"}


def _md(text) -> str:
    """Escape table pipes and newlines."""
    return str(text if text is not None else "").replace("|", "\\|").replace("\n", " ")


def _v(verdict: str) -> str:
    return f"{ICON[verdict]} **{verdict}**"


def _anchor(f: Finding) -> str:
    return f"#{f.id.lower()}"


def _link(f: Finding) -> str:
    return f"[{f.id}]({_anchor(f)})"


def _dedupe(items: list[str]) -> list[str]:
    """Drop an entry that another entry already contains ('X' when 'X or Y' is listed)."""
    items = list(dict.fromkeys(items))
    return [s for s in items if not any(s != o and s in o for o in items)]


def _finding_block(f: Finding, out: list[str], level: str = "###") -> None:
    out.append(f'<a id="{f.id.lower()}"></a>')
    out.append(f"{level} {f.id} · {f.subject} · {_v(f.verdict)}")
    out.append("")
    out.append(f"**Why:** {f.summary}")
    out.append("")
    out.append("**Code:** " + "; ".join(dict.fromkeys(f.code_refs)))
    out.append("")
    if f.evidence:
        out.append("| Read from the drawings | Value | Where |")
        out.append("|---|---|---|")
        for e in f.evidence:
            out.append(f"| {_md(e['label'])} | `{_md(e['value'])}` | {_md(e['source'])} |")
        out.append("")
    if f.criteria:
        out.append("| Requirement | Read / derived | Result | Why | Code |")
        out.append("|---|---|---|---|---|")
        for c in f.criteria:
            out.append(f"| {_md(c.requirement)} | {_md(c.read)} | {ICON[c.verdict]} {c.verdict} | {_md(c.reason)} | "
                       f"{_md(c.code)} |")
        out.append("")
    if f.working:
        out.append("**Working:**")
        out.append("")
        out += [f"- {w}" for w in f.working]
        out.append("")
    if f.interpretations:
        out.append("**Interpretations (not code text):**")
        out.append("")
        out += [f"- {i}" for i in f.interpretations]
        out.append("")
    if f.flags:
        out.append("**Flags:**")
        out.append("")
        out += [f"- ⚠️ {fl['message']}" for fl in f.flags]
        out.append("")
    if f.settle and f.verdict in (CNE, FAIL):
        out.append("**Would settle it:** " + "; ".join(_dedupe(f.settle)))
        out.append("")
    if f.policies:
        out.append("**Rules applied:** " + ", ".join(f"`{p}`" for p in f.policies))
        out.append("")


def render(results: Results, inputs: list[dict], command: str) -> str:
    fs = results.all
    counts = {v: sum(f.verdict == v for f in fs) for v in VERDICTS}
    h = results.height
    out: list[str] = []
    out.append("# Plan check report: building height and emergency escape openings")
    out.append("")
    out.append("Checked against **IBC 2018 Table 504.3** (allowable building height) and **IBC 2018 Section 1030** "
               "(emergency escape and rescue openings).")
    out.append("")
    out.append("| Input | File | sha256 (first 12) |")
    out.append("|---|---|---|")
    for i in inputs:
        out.append(f"| {i['role']} | `{i['name']}` | `{i['sha256'][:12]}` |")
    out.append("")
    amend = (f" {'; '.join(results.unavailable_amendments)} were not provided, so every verdict is conditional "
             "on them (`POL-GEN-AMENDMENTS`)." if results.unavailable_amendments else "")
    out.append("> **Read this first.** Verdicts use the 2018 IBC as printed." + amend +
               " Pass and Fail are used only where the two sheets decide the question; everything else is "
               "Could Not Evaluate with the document that would settle it.")
    out.append("")

    # summary ------------------------------------------------------------------------
    out.append("## Summary")
    out.append("")
    out.append("| " + " | ".join(f"{ICON[v]} {v}" for v in VERDICTS) + " |")
    out.append("|" + "---|" * len(VERDICTS))
    out.append("| " + " | ".join(str(counts[v]) for v in VERDICTS) + " |")
    out.append("")
    out.append(f"- **Building height:** {_v(h.verdict)}. {h.summary}")
    rooms = results.rooms
    for v in (FAIL, CNE, PASS):
        rs = [r for r in rooms if r.verdict == v]
        if rs:
            out.append(f"- **Sleeping rooms, {v}:** " + ", ".join(f"{_link(r)} {r.subject}" for r in rs))
    out.append("")

    # fails --------------------------------------------------------------------------
    fails = [f for f in fs if f.verdict == FAIL]
    out.append("## Fails: raw material for the correction letter")
    out.append("")
    if not fails:
        out.append("None.")
    for n, f in enumerate(fails, 1):
        refs = ([c.code for c in f.criteria if c.verdict == FAIL] if f.criteria else f.code_refs[:1]
                if f.check == "height" else f.code_refs)
        out.append(f"{n}. **{_link(f)} {f.subject}.** {f.summary} *Code:* {'; '.join(dict.fromkeys(refs))}")
    out.append("")

    # attention ---------------------------------------------------------------------------
    out.append("## Needs your attention")
    out.append("")
    for a in results.attention:
        rel = (" (" + ", ".join(f"[{r}](#{r.lower()})" for r in a.related) + ")") if a.related else ""
        out.append(f"- **{a.title}.** {a.detail}{rel}")
    out.append("")

    # index ---------------------------------------------------------------------------------
    out.append("## All findings")
    out.append("")
    out.append("| ID | Verdict | Subject | Why |")
    out.append("|---|---|---|---|")
    for f in fs:
        out.append(f"| {_link(f)} | {ICON[f.verdict]} {f.verdict} | {_md(f.subject)} | {_md(f.summary)} |")
    out.append("")

    # check 1 -----------------------------------------------------------------------------------
    out.append("## Check 1: Building height (IBC Table 504.3)")
    out.append("")
    _finding_block(h, out)

    # check 2 -------------------------------------------------------------------------------------
    out.append("## Check 2: Emergency escape and rescue openings (IBC 1030)")
    out.append("")
    out.append("Nominal sizes on the schedule include the frame. The net clear opening is always smaller, so a "
               "nominal size can prove a Fail but never a Pass (`POL-E-NOMINAL-UPPER`). Sill heights are derived "
               "as head height minus window height, which is the frame sill; the clear opening's bottom is at or "
               "above it (`POL-E-SILL-LOWER`).")
    out.append("")
    out.append("### Sleeping rooms")
    out.append("")
    for r in rooms:
        _finding_block(r, out, "####")
    egress = [w for w in results.windows if w.verdict != NA]
    out.append("### Egress windows")
    out.append("")
    for w in egress:
        _finding_block(w, out, "####")
    na = [w for w in results.windows if w.verdict == NA]
    out.append("### Windows not evaluated (Not Applicable)")
    out.append("")
    out.append("| ID | Window | Why | Flags |")
    out.append("|---|---|---|---|")
    for w in na:
        flags = "; ".join(f"⚠️ {fl['message']}" for fl in w.flags)
        out.append(f'| <a id="{w.id.lower()}"></a>{w.id} | {_md(w.subject)} | {_md(w.summary)} | {_md(flags)} |')
    out.append("")

    # could not check -------------------------------------------------------------------------------
    out.append("## What this report could not check")
    out.append("")
    settle: dict[str, list[str]] = {}
    for f in fs:
        if f.verdict in (CNE, FAIL):
            for s in f.settle:
                settle.setdefault(s, []).append(f.id)
    out.append("| Document | Would settle |")
    out.append("|---|---|")
    for s, ids in settle.items():
        out.append(f"| {_md(s)} | " + ", ".join(f"[{i}](#{i.lower()})" for i in dict.fromkeys(ids)) + " |")
    out.append("")

    # rules ---------------------------------------------------------------------------------------------
    used = list(dict.fromkeys(p for f in fs for p in f.policies))
    if results.unavailable_amendments:
        used.append("POL-GEN-AMENDMENTS")
    out.append("## Rules the tool applied")
    out.append("")
    out.append("Judgement calls are named rules, the same for every project. A finding lists the rules it used. "
               "Rules that did not come up for this project are listed after, for reference.")
    out.append("")
    out.append("| Rule | Used here | What it says | Rests on |")
    out.append("|---|---|---|---|")
    for pid in used + [p for p in POLICIES if p not in used]:
        p = POLICIES[pid]
        out.append(f"| `{p.id}` {_md(p.title)} | {'yes' if pid in used else 'no'} | {_md(p.rule)} | "
                   f"{_md('; '.join(p.rests_on))} ({p.authority}) |")
    out.append("")
    out.append("---")
    out.append("")
    out.append(f"Generated by `{command}`. Findings are also in `findings.json`.")
    out.append("")
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

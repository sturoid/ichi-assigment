"""Score findings against a hand-typed eval set (run from src/):

  python -m services.planCheck.evals ../tests/fixtures/expected/verdicts.json ../findings.json \
      --report ../REPORT.md

Checks every expected verdict and flag, flags findings the eval set doesn't know
(so a new finding can't slip in unreviewed), and, with --report, checks that every
verdict in REPORT.md's index table agrees with findings.json. Exit 1 on any miss.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def report_verdicts(md: str) -> dict[str, str]:
    """{id: verdict} from the 'All findings' index table of REPORT.md."""
    section = md.split("## All findings", 1)[1].split("\n## ", 1)[0]
    out = {}
    for m in re.finditer(r"^\| \[([A-Z]-[^\]]+)\]\([^)]*\) \| \S+ ([A-Za-z ]+?) \|", section, flags=re.M):
        out[m.group(1)] = m.group(2).strip()
    return out


def score(expected: dict, findings: dict, report_md: str | None = None) -> dict:
    got = {f["id"]: f for f in findings["findings"]}
    rows, misses = [], []
    for e in expected["expected"]:
        f = got.get(e["id"])
        if f is None:
            rows.append((e["id"], e["verdict"], "(missing)", "MISS"))
            misses.append(f"{e['id']}: no finding")
            continue
        ok = f["verdict"] == e["verdict"]
        have = {fl["code"] for fl in f["flags"]}
        lacking = [c for c in e.get("flags", []) if c not in have]
        if lacking:
            ok = False
            misses.append(f"{e['id']}: missing flag(s) {lacking}")
        if f["verdict"] != e["verdict"]:
            misses.append(f"{e['id']}: expected {e['verdict']}, got {f['verdict']}")
        rows.append((e["id"], e["verdict"], f["verdict"], "ok" if ok else "MISS"))
    known = {e["id"] for e in expected["expected"]}
    unexpected = sorted(set(got) - known)
    for u in unexpected:
        misses.append(f"{u}: finding not in the eval set ({got[u]['verdict']})")
    have_attn = {a["code"] for a in findings.get("attention", [])}
    for a in expected.get("attention", []):
        if a["code"] not in have_attn:
            misses.append(f"attention item {a['code']!r} missing")
    if report_md is not None:
        rv = report_verdicts(report_md)
        for fid, f in got.items():
            if rv.get(fid) != f["verdict"]:
                misses.append(f"REPORT.md shows {fid} as {rv.get(fid)!r}, findings.json says {f['verdict']!r}")
    n_ok = sum(r[3] == "ok" for r in rows)
    return {"rows": rows, "misses": misses, "correct": n_ok, "total": len(rows), "unexpected": unexpected}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m services.planCheck.evals")
    ap.add_argument("expected", type=Path)
    ap.add_argument("findings", type=Path)
    ap.add_argument("--report", type=Path)
    a = ap.parse_args(argv)
    res = score(json.loads(a.expected.read_text(encoding="utf-8")),
                json.loads(a.findings.read_text(encoding="utf-8")),
                a.report.read_text(encoding="utf-8") if a.report else None)
    w = max(len(r[0]) for r in res["rows"])
    for fid, exp, got, st in res["rows"]:
        print(f"{st:4}  {fid:<{w}}  expected {exp:<20} got {got}")
    print(f"\n{res['correct']}/{res['total']} expected verdicts (with flags) correct")
    for m in res["misses"]:
        print(f"  MISS {m}")
    return 1 if res["misses"] else 0


if __name__ == "__main__":
    sys.exit(main())

"""Plan check CLI (run from the src/ directory):

  python -m services.planCheck <code-analysis.html> <window-schedule.html> -o REPORT.md [--json findings.json]

The code library (Table 504.3 store, Section 1030 text) comes from the manifest,
default ../tests/fixtures/manifest.json. The store is loaded verified against its
sources, and every cited code quote is checked on its line before anything runs.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

from services.codeStore import Store

from .checks import run_checks
from .citations import verify_quotes
from .facts import read_code_analysis, read_window_schedule
from .report import render, to_json

REPO = Path(__file__).resolve().parents[3]
DEFAULT_MANIFEST = REPO / "tests" / "fixtures" / "manifest.json"


def run(code_analysis: Path, schedule: Path, manifest: Path = DEFAULT_MANIFEST, store_path: Path | None = None,
        command: str | None = None) -> tuple[str, str]:
    """(report markdown, findings json) for two project files."""
    manifest = Path(manifest)
    store = Store.load(store_path or manifest.parent / "store" / "store.json", manifest=manifest)
    problems = verify_quotes(manifest.parent)
    if problems:
        raise SystemExit("cited code text does not match the code files:\n  " + "\n  ".join(problems))
    ca_text = Path(code_analysis).read_text(encoding="utf-8")
    ws_text = Path(schedule).read_text(encoding="utf-8")
    ca = read_code_analysis(ca_text, Path(code_analysis).name)
    ws = read_window_schedule(ws_text, Path(schedule).name)
    inputs = [
        {"role": "Code analysis" + (f" ({ca.title[0]})" if ca.title else ""), "name": Path(code_analysis).name,
         "sha256": hashlib.sha256(ca_text.encode("utf-8")).hexdigest()},
        {"role": "Window schedule" + (f" ({ws.title[0]})" if ws.title else ""), "name": Path(schedule).name,
         "sha256": hashlib.sha256(ws_text.encode("utf-8")).hexdigest()},
    ]
    results = run_checks(store, ca, ws)
    cmd = command or (f"python -m services.planCheck {Path(code_analysis).name} {Path(schedule).name} "
                      "-o REPORT.md --json findings.json")
    return render(results, inputs, cmd), to_json(results, inputs)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m services.planCheck")
    ap.add_argument("code_analysis", type=Path)
    ap.add_argument("window_schedule", type=Path)
    ap.add_argument("-o", "--out", type=Path, default=Path("REPORT.md"))
    ap.add_argument("--json", type=Path, help="also write the findings as JSON")
    ap.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    a = ap.parse_args(argv)
    md, js = run(a.code_analysis, a.window_schedule, a.manifest)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(md, encoding="utf-8", newline="\n")
    if a.json:
        a.json.write_text(js, encoding="utf-8", newline="\n")
    print(f"wrote {a.out}" + (f" and {a.json}" if a.json else ""), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""CLI (from the src/ directory):

  python -m services.codeStore build <manifest.json> -o <out_dir>
  python -m services.codeStore validate <store.json>
  python -m services.codeStore lookup <store.json> <provision> dim=value [dim=value ...]

  e.g. lookup ../tests/fixtures/store/store.json IBC:2018:T504.3 occupancy=B sprinkler=NS construction=II-B
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .store import Store, dumps, write_store
from .validate import validate_store


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m services.codeStore")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("manifest", type=Path)
    b.add_argument("-o", "--out", type=Path, required=True)
    v = sub.add_parser("validate")
    v.add_argument("store", type=Path)
    lk = sub.add_parser("lookup")
    lk.add_argument("store", type=Path)
    lk.add_argument("provision")
    lk.add_argument("dims", nargs="*", help="dimension=value")
    a = ap.parse_args(argv)

    if a.cmd == "build":
        out = write_store(a.manifest, a.out)
        problems = validate_store(json.loads(out.read_text(encoding="utf-8")))
        print(f"wrote {out}; {len(problems)} validation problem(s)", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        return 1 if problems else 0
    if a.cmd == "validate":
        problems = validate_store(json.loads(a.store.read_text(encoding="utf-8")))
        for p in problems:
            print(p)
        print(f"{len(problems)} problem(s)", file=sys.stderr)
        return 1 if problems else 0
    dims = dict(d.split("=", 1) for d in a.dims)
    sys.stdout.write(dumps(Store.load(a.store).lookup(a.provision, **dims).to_dict()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

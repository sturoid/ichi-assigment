"""The committed deliverables are exactly what the tool writes, and the eval scorer passes."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from _setup import EXPECTED, FIXTURES, REPO

from services.planCheck.__main__ import run
from services.planCheck.evals import report_verdicts, score

DELIVERABLES = REPO  # REPORT.md, findings.json and NOTES.md live at the repo root
CA, WS = FIXTURES / "code-analysis.html", FIXTURES / "window-schedule.html"


class Deliverables(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.md, cls.js = run(CA, WS)

    def test_committed_report_equals_tool_output(self):
        self.assertEqual((DELIVERABLES / "REPORT.md").read_text(encoding="utf-8"), self.md,
                         "REPORT.md is stale: regenerate with the command in NOTES.md")

    def test_committed_findings_equal_tool_output(self):
        self.assertEqual((DELIVERABLES / "findings.json").read_text(encoding="utf-8"), self.js)

    def test_deterministic(self):
        self.assertEqual(run(CA, WS), (self.md, self.js))

    def test_eval_scorer_passes(self):
        res = score(json.loads((EXPECTED / "verdicts.json").read_text(encoding="utf-8")), json.loads(self.js),
                    self.md)
        self.assertEqual(res["misses"], [])
        self.assertEqual(res["correct"], res["total"])

    def test_scorer_catches_a_wrong_verdict(self):
        bad = json.loads(self.js)
        next(f for f in bad["findings"] if f["id"] == "W-7")["verdict"] = "Pass"
        res = score(json.loads((EXPECTED / "verdicts.json").read_text(encoding="utf-8")), bad, self.md)
        self.assertTrue(any("W-7" in m for m in res["misses"]))

    def test_report_index_lists_every_finding(self):
        js = json.loads(self.js)
        self.assertEqual(report_verdicts(self.md), {f["id"]: f["verdict"] for f in js["findings"]})

    def test_cli_writes_files(self):
        with tempfile.TemporaryDirectory() as d:
            out, jsn = Path(d) / "REPORT.md", Path(d) / "findings.json"
            r = subprocess.run([sys.executable, "-m", "services.planCheck", str(CA), str(WS), "-o", str(out),
                                "--json", str(jsn)], cwd=REPO / "src", capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(out.read_text(encoding="utf-8"), self.md)

    def test_only_the_four_verdicts(self):
        for f in json.loads(self.js)["findings"]:
            self.assertIn(f["verdict"], ("Pass", "Fail", "Could Not Evaluate", "Not Applicable"))


if __name__ == "__main__":
    unittest.main()

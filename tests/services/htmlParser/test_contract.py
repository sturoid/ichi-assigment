"""Output-contract checks across every scenario and real fixture: coded warnings,
structured review items, table_index, no timestamps."""
import json
import unittest

from _setup import FIXTURES

from services.htmlParser import SPECS, KeyValueSheet, MatrixTable, RecordTable, parse_tables
from services.htmlParser.__main__ import build

SCEN = FIXTURES / "scenarios"
REVIEW_KEYS = {"code", "rows", "cols", "chosen", "alternative", "override", "message"}


def _objects():
    man = json.loads((SCEN / "scenarios.json").read_text(encoding="utf-8"))
    for sc in man["scenarios"]:
        if sc.get("status") != "pass" or "html" not in sc:
            continue
        grids = parse_tables((SCEN / sc["html"]).read_text(encoding="utf-8"))
        grid = grids[sc.get("table_index", 0)]
        if sc["kind"] == "records":
            yield sc["id"], RecordTable(grid)
        elif sc["kind"] == "kv":
            yield sc["id"], KeyValueSheet(grid)


class OutputContract(unittest.TestCase):
    def test_every_warning_has_a_code_and_review_items_are_structured(self):
        for sid, obj in _objects():
            d = obj.to_dict(include_grid=True)
            with self.subTest(sid):
                for w in d["warnings"] + d["grid"]["warnings"]:
                    self.assertNotEqual(w["code"], "unclassified", f"{sid}: {w['message']}")
                for item in d["review_items"]:
                    self.assertTrue(REVIEW_KEYS <= set(item), f"{sid}: {item}")
                self.assertNotIn("review_items", d["layout"], "review items live in one place")
                self.assertIn("table_index", d)

    def test_table_index_follows_the_source(self):
        grids = parse_tables((SCEN / "P10-multiple-tables-warnings-isolated.html").read_text(encoding="utf-8"))
        self.assertEqual([g.table_index for g in grids], [0, 1])
        self.assertEqual(RecordTable(grids[1]).to_dict()["table_index"], 1)

    def test_cli_output_has_no_timestamp(self):
        a = build(FIXTURES / "table-504.3.html", "matrix", "ibc2018-504.3", 0, False)
        b = build(FIXTURES / "table-504.3.html", "matrix", "ibc2018-504.3", 0, False)
        self.assertEqual(a, b)
        self.assertNotIn("parsed_at", a)
        self.assertEqual(a["table_index"], 0)

    def test_matrix_warnings_coded(self):
        m = MatrixTable(parse_tables((FIXTURES / "table-504.3.html").read_text(encoding="utf-8"))[0],
                        SPECS["ibc2018-504.3"])
        self.assertTrue(all(w["code"] != "unclassified" for w in m.to_dict(False)["warnings"]))


if __name__ == "__main__":
    unittest.main()

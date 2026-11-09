import json
import random
import re
import unittest

from _setup import read_fixture
from services.htmlParser import KeyValueSheet, RecordTable, detect_layout, parse_table


class WindowScheduleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.t = RecordTable(parse_table(read_fixture("window-schedule.html")))

    def test_layout(self):
        lay = self.t.layout
        self.assertEqual(lay.header_rows, [0, 1])  # row 1 is <td>, caught via header rowspans
        self.assertEqual(lay.separator_rows, [2])
        self.assertEqual(len(lay.data_rows), 17)

    def test_column_paths(self):
        labels = {c.id: c.label for c in self.t.layout.columns}
        self.assertEqual(labels["c2"], "NOMINAL SIZE / WIDTH")
        self.assertEqual(labels["c3"], "NOMINAL SIZE / HEIGHT")
        self.assertEqual(labels["c6"], "HEAD HEIGHT")
        self.assertEqual(labels["c8"], "GLAZING / SAFETY")
        self.assertEqual(labels["c10"], "HARDWARE")  # empty <th> parent dropped
        self.assertEqual(labels["c11"], "EGRESS")
        self.assertEqual(labels["c13"], "NOTES")
        screen = self.t.layout.columns[9]
        self.assertIn("SCREEN", screen.path_candidates[-1])

    def test_duplicate_type_columns_kept_apart(self):
        self.assertEqual(self.t.column("type"), ["c4", "c5"])
        self.assertEqual(self.t.layout.columns[4].duplicate_of, ["c5"])

    def test_rows_keep_raw_ocr_text(self):
        by_symbol = {row["cells"]["c0"]["text"]: row for row in self.t.rows}
        self.assertEqual(sorted(by_symbol, key=int),
                         [str(n) for n in [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 20, 21, 22, 23]])
        w4 = by_symbol["4"]["cells"]
        self.assertEqual(w4["c2"]["raw"], "3' - O\"")  # letter O kept; repair is a later layer's job
        self.assertEqual(by_symbol["12"]["cells"]["c1"]["text"], "BEDRROM 205")
        self.assertEqual(by_symbol["7"]["cells"]["c2"]["text"], "2'-6\"")
        self.assertEqual(by_symbol["13"]["cells"]["c4"]["text"], "FIXED")
        self.assertEqual(by_symbol["13"]["cells"]["c11"]["text"], "Y")
        self.assertEqual(by_symbol["21"]["cells"]["c11"]["text"], "")  # GUEST BED, not marked egress
        self.assertEqual(by_symbol["20"]["cells"]["c6"]["text"], "8' - 0\"")

    def test_column_order_does_not_matter(self):
        """Shuffle the schedule's columns: every (header label, symbol) -> value pair survives."""
        html = read_fixture("window-schedule.html")
        base = {(c.label, r["cells"]["c0"]["text"], i): r["cells"][c.id]["text"]
                for c in self.t.layout.columns for r in self.t.rows
                for i in [self.t.column(c.label).index(c.id)]}
        # Build a simple flat-header variant with shuffled columns (spans removed)
        cols = list(range(14))
        random.Random(7).shuffle(cols)
        head = "".join(f"<th>{self.t.layout.columns[c].label}</th>" for c in cols)
        body = "".join("<tr>" + "".join(f"<td>{r['cells'][f'c{c}']['raw']}</td>" for c in cols) + "</tr>"
                       for r in self.t.rows)
        t2 = RecordTable(parse_table(f"<table><tr>{head}</tr>{body}</table>"))
        sym = t2.column("SYMBOL")[0]
        got = {}
        for c in t2.layout.columns:
            for r in t2.rows:
                i = t2.column(c.label).index(c.id)
                got[(c.label, r["cells"][sym]["text"], i)] = r["cells"][c.id]["text"]
        # duplicate TYPE columns can swap order when shuffled; compare them as a multiset
        norm = lambda d: sorted((k[0], k[1], v) for k, v in d.items())
        self.assertEqual(norm(got), norm(base))

    def test_serialises_to_json(self):
        json.dumps(self.t.to_dict())


class CodeAnalysisTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kv = KeyValueSheet(parse_table(read_fixture("code-analysis.html")))

    def test_title_and_entries(self):
        self.assertEqual(self.kv.title, ["CODE ANALYSIS - SHEET A0.1"])
        self.assertEqual(len(self.kv.entries), 12)
        self.assertEqual(self.kv.warnings, [])

    def test_values_verbatim(self):
        e = {x["label"]["text"]: x["value"]["text"] for x in self.kv.entries}
        self.assertEqual(e["OCCUPANCY GROUP"], "R-3")
        self.assertEqual(e["CONSTRUCTION TYPE"], "V-B")
        self.assertEqual(e["ALLOWABLE HEIGHT"], "60' - 0\" PER TABLE 504.3")
        self.assertTrue(e["BUILDING HEIGHT ABOVE GRADE PLAN E"].startswith("41' - 6\""))
        self.assertEqual(e["EMERGENCY ESCAPE & RESCUE"][:8], "PROVIDED")

    def test_split_word_labels_offer_the_joined_reading(self):
        cands = {x["label"]["text"]: x["label"].get("join_candidates", []) for x in self.kv.entries}
        self.assertIn("FIRE SPRINKLERS", cands["FIRE SPRINKLE RS"])
        self.assertIn("BUILDING HEIGHT ABOVE GRADE PLANE", cands["BUILDING HEIGHT ABOVE GRADE PLAN E"])
        self.assertIn("APPLICABLE CODE", cands["APPLICABLE CODE"])


class LayoutDetectionTest(unittest.TestCase):
    def test_table_504_header_rows(self):
        lay = detect_layout(parse_table(read_fixture("table-504.3.html")))
        self.assertEqual(lay.header_rows, [0, 1, 2])
        self.assertEqual(lay.data_rows, list(range(3, 19)))
        self.assertEqual(lay.columns[1].path, ["TYPE OF CONSTRUCTION", "SEE FOOTNOTES"])
        self.assertEqual(lay.columns[8].path, ["TYPE OF CONSTRUCTION", "TYPE IV", "HT"])

    def test_explicit_header_override(self):
        g = parse_table("<table><tr><td>A</td><td>B</td></tr><tr><td>1</td><td>2</td></tr></table>")
        self.assertEqual(detect_layout(g).header_rows, [])
        self.assertEqual(detect_layout(g, header_rows=1).header_rows, [0])


if __name__ == "__main__":
    unittest.main()

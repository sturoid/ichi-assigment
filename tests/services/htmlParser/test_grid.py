import unittest

from _setup import read_fixture
from services.htmlParser import parse_table, parse_tables


class Table504GridTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = parse_table(read_fixture("table-504.3.html"))

    def test_shape_is_complete(self):
        self.assertEqual((self.g.n_rows, self.g.n_cols), (19, 11))
        for r in range(self.g.n_rows):
            self.assertTrue(all(cid is not None for cid in self.g.slots[r]), f"row {r} has holes")
        self.assertEqual(self.g.warnings, [])

    def test_empty_span_attributes_count_as_one(self):
        # 'A' under TYPE I has colspan="" rowspan=""
        cell = self.g.slot(2, 2).cell
        self.assertEqual((cell.text, cell.rowspan, cell.colspan), ("A", 1, 1))

    def test_sup_footnotes_are_separated_from_text(self):
        ns = self.g.slot(3, 1).cell
        self.assertEqual((ns.text, ns.footnotes), ("NS", ["b"]))
        h_ns = self.g.slot(5, 1).cell
        self.assertEqual((h_ns.text, h_ns.footnotes), ("NS", ["c", "d"]))
        r = self.g.slot(15, 0).cell
        self.assertEqual((r.text, r.footnotes), ("R", ["h"]))

    def test_rowspan_carry_down_one_cell_row(self):
        # H-1.. 'S' row is written as a single <td>S</td>; everything else comes from above
        self.assertEqual(self.g.slot(6, 1).text, "S")
        self.assertFalse(self.g.slot(6, 1).inherited)
        for c in range(2, 11):
            s = self.g.slot(6, c)
            self.assertTrue(s.inherited, c)
            self.assertEqual(s.cell.origin, (5, c))
        self.assertTrue(self.g.slot(6, 0).inherited)

    def test_rowspan_carry_down_partial_row(self):
        # I-1 Condition 2 / S: cols 2-4 are its own cells, 5-10 inherited from the NS row
        row = [self.g.slot(12, c) for c in range(11)]
        self.assertEqual([s.text for s in row[1:5]], ["S", "UL", "180", "85"])
        self.assertEqual([s.inherited for s in row[2:5]], [False] * 3)
        self.assertEqual([s.inherited for s in row[5:]], [True] * 6)
        self.assertEqual([s.text for s in row[5:]], ["55", "65", "55", "65", "50", "40"])

    def test_header_spans(self):
        self.assertEqual(self.g.text_matrix()[1][8], "TYPE IV")
        self.assertEqual(self.g.text_matrix()[2][8], "HT")
        self.assertEqual(set(self.g.text_matrix()[0][1:]), {"TYPE OF CONSTRUCTION"})

    def test_changed_marker_is_kept(self):
        self.assertIn("changed_ICC", self.g.slot(16, 1).cell.classes)  # S13D
        self.assertIn("bold", self.g.slot(0, 0).cell.classes)


class SyntheticGridTest(unittest.TestCase):
    def test_line_break_join_candidates(self):
        g = parse_table("<table><tr><td>SCREE\n        N</td><td>FIRE SPRINKLE\n RS</td></tr></table>")
        self.assertEqual(g.slot(0, 0).text, "SCREE N")
        self.assertEqual(g.slot(0, 0).cell.join_candidates, ["SCREE N", "SCREEN"])
        self.assertIn("FIRE SPRINKLERS", g.slot(0, 1).cell.join_candidates)

    def test_raw_text_is_preserved(self):
        g = parse_table("<table><tr><td>3' - O\"</td><td>A &amp; B</td></tr></table>")
        self.assertEqual(g.slot(0, 0).cell.raw, "3' - O\"")
        self.assertEqual(g.slot(0, 1).text, "A & B")

    def test_bad_spans_warn_and_fall_back(self):
        g = parse_table('<table><tr><td rowspan="0">a</td><td colspan="x">b</td></tr></table>')
        self.assertEqual((g.n_rows, g.n_cols), (1, 2))
        self.assertTrue(any('rowspan="0"' in w for w in g.warnings))
        self.assertTrue(any('colspan="x"' in w for w in g.warnings))

    def test_rowspan_past_end_is_clipped(self):
        g = parse_table('<table><tr><td rowspan="5">a</td><td>b</td></tr><tr><td>c</td></tr></table>')
        self.assertEqual((g.n_rows, g.n_cols), (2, 2))
        self.assertEqual(g.slot(1, 0).text, "a")
        self.assertEqual(g.slot(1, 1).text, "c")
        self.assertTrue(any("runs past the table end" in w for w in g.warnings))

    def test_overlapping_spans_warn(self):
        html = ('<table><tr><td>a</td><td rowspan="2">b</td></tr>'
                '<tr><td colspan="2">c</td></tr></table>')
        g = parse_table(html)
        self.assertEqual(g.slot(1, 1).text, "b")  # first claim wins
        self.assertTrue(any("overlapping" in w for w in g.warnings))

    def test_ragged_row_is_reported(self):
        g = parse_table("<table><tr><td>a</td><td>b</td></tr><tr><td>c</td></tr></table>")
        self.assertIsNone(g.slot(1, 1))
        self.assertTrue(any("ragged" in w for w in g.warnings))

    def test_missing_end_tags(self):
        g = parse_table("<table><tr><td>a<td>b<tr><td>c<td>d</table>")
        self.assertEqual(g.text_matrix(), [["a", "b"], ["c", "d"]])

    def test_multiple_tables(self):
        self.assertEqual(len(parse_tables("<table><tr><td>1</td></tr></table><p/><table><tr><td>2</td></tr></table>")), 2)

    def test_multiple_sups(self):
        g = parse_table("<table><tr><td>NS<sup>a</sup><sup>b, c</sup></td></tr></table>")
        self.assertEqual(g.slot(0, 0).cell.footnotes, ["a", "b", "c"])


if __name__ == "__main__":
    unittest.main()

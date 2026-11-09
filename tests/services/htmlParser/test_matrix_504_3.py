"""Table 504.3 against values hand-transcribed from the printed table
(tests/fixtures/expected/table-504.3.expected.json), not against parser output."""
import json
import unittest

from _setup import EXPECTED, read_fixture
from services.htmlParser import SPECS, MatrixError, MatrixSpec, MatrixTable, parse_table


def _as_expected(rec):
    return "UL" if rec["value_kind"] == "unlimited" else rec["value"]


class Table504MatrixTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = MatrixTable(parse_table(read_fixture("table-504.3.html")), SPECS["ibc2018-504.3"])
        cls.exp = json.loads((EXPECTED / "table-504.3.expected.json").read_text(encoding="utf-8"))

    def test_no_warnings(self):
        self.assertEqual(self.m.warnings, [])

    def test_columns(self):
        self.assertEqual(self.m.column_keys, self.exp["construction_order"])

    def test_full_snapshot(self):
        order = self.exp["construction_order"]
        for row in self.exp["rows"]:
            atoms = [a.strip() for a in row["occupancy"].split(",")]
            for atom in atoms:
                for con, want in zip(order, row["values"]):
                    with self.subTest(occupancy=atom, sprinkler=row["sprinkler"], construction=con):
                        rec = self.m.lookup(occupancy=atom, sprinkler=row["sprinkler"], construction=con)
                        self.assertIsNotNone(rec)
                        self.assertEqual(_as_expected(rec), want)
                        self.assertEqual(rec["row_labels"]["occupancy"], row["occupancy"])
                        self.assertEqual(set(rec["footnotes"]), set(row["footnotes"]))

    def test_spot_checks(self):
        for sc in self.exp["spot_checks"]:
            with self.subTest(**{k: sc[k] for k in ("occupancy", "sprinkler", "construction")}):
                rec = self.m.lookup(occupancy=sc["occupancy"], sprinkler=sc["sprinkler"],
                                    construction=sc["construction"])
                self.assertEqual(_as_expected(rec), sc["expected"])

    def test_counts(self):
        self.assertEqual(len(self.m.cells), 16 * 9)
        # every expanded (occupancy atom, sprinkler, construction) triple is indexed exactly once
        n_keys = sum(len(r["occupancy"].split(",")) * 9 for r in self.exp["rows"])
        self.assertEqual(len(self.m.index), n_keys)

    def test_lookup_is_exact_not_fuzzy(self):
        # project wording must be mapped by the caller; the table never guesses
        self.assertIsNone(self.m.lookup(occupancy="R-3", sprinkler="S13D", construction="V-B"))
        self.assertIsNone(self.m.lookup(occupancy="I-1", sprinkler="NS", construction="V-B"))
        # but case / spacing are normalised
        self.assertEqual(self.m.lookup(occupancy="i-1  condition 2", sprinkler="s", construction="ii-b")["value"], 55)
        with self.assertRaises(KeyError):
            self.m.lookup(occupancy="R", construction="V-B")

    def test_provenance_points_back_to_source(self):
        rec = self.m.lookup(occupancy="I-2", sprinkler="S", construction="V-B")
        src = rec["src"]["value"]
        self.assertEqual((src["grid_row"], src["grid_col"], src["inherited"]), (12, 10, True))
        self.assertEqual(src["origin"], [11, 10])
        self.assertIn("V-B -> 40 ft", self.m.sentence(rec))

    def test_unlimited_is_not_a_number(self):
        rec = self.m.lookup(occupancy="A", sprinkler="NS", construction="I-A")
        self.assertEqual((rec["value"], rec["value_kind"], rec["value_text"]), (None, "unlimited", "UL"))

    def test_monotonic_with_sprinklers(self):
        # Within an occupancy row, the full-NFPA-13 'S' value is never below the NS value.
        # (Not true for S13R/S13D: R / NS / I-A is UL but S13R / S13D cap at 60 ft.)
        def num(rec):
            return float("inf") if rec["value_kind"] == "unlimited" else rec["value"]
        for occ in self.m.dimension_values()["occupancy"]:
            for con in self.m.column_keys:
                ns = self.m.lookup(occupancy=occ, sprinkler="NS", construction=con)
                for spr in ("S",):
                    other = self.m.lookup(occupancy=occ, sprinkler=spr, construction=con)
                    if other is not None:
                        self.assertGreaterEqual(num(other), num(ns), (occ, spr, con))

    def test_serialises_to_json(self):
        d = self.m.to_dict()
        json.dumps(d)
        self.assertEqual(d["dimensions"]["order"], ["occupancy", "sprinkler", "construction"])


class MatrixGuardsTest(unittest.TestCase):
    def test_duplicate_row_labels_are_an_error(self):
        html = ("<table><tr><th>K</th><th>X</th></tr>"
                "<tr><td>a</td><td>1</td></tr><tr><td>a</td><td>2</td></tr></table>")
        with self.assertRaises(MatrixError):
            MatrixTable(parse_table(html), MatrixSpec(table_id="t", row_dims=["k"]))

    def test_wrong_stub_count_is_rejected(self):
        html = read_fixture("table-504.3.html")
        spec = MatrixSpec(table_id="t", row_dims=["occupancy"], multi_value_dims={"occupancy"})
        with self.assertRaises(MatrixError):  # sprinkler column would be read as values -> NS twice per row
            MatrixTable(parse_table(html), spec)


if __name__ == "__main__":
    unittest.main()

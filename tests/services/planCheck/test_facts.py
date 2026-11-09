"""Facts: label aliases, join candidates, column roles by alias (not position),
feet-and-inches with OCR flags, sleeping-room classification. Expected values are
hand-typed from the fixture sheets."""
import unittest

from _setup import FIXTURES

from services.planCheck.facts import classify_operation, read_code_analysis, read_window_schedule
from services.planCheck.rooms import classify, room_key
from services.planCheck.units import fmt_in, parse_length

CA = (FIXTURES / "code-analysis.html").read_text(encoding="utf-8")
WS = (FIXTURES / "window-schedule.html").read_text(encoding="utf-8")


def flat_schedule(headers, rows):
    return ("<table><tr><th>" + "</th><th>".join(headers) + "</th></tr>"
            + "".join("<tr><td>" + "</td><td>".join(r) + "</td></tr>" for r in rows) + "</table>")


class Lengths(unittest.TestCase):
    def test_forms(self):
        cases = {"2' - 6\"": 30, "2'-6\"": 30, "6' - 8\"": 80, "30\"": 30, "2' - 6 1/2\"": 30.5, "8'-0\"": 96}
        for t, want in cases.items():
            with self.subTest(t):
                x = parse_length(t)
                self.assertEqual((x.status, x.inches, x.ocr_repaired), ("parsed", want, False))

    def test_ocr_damage_is_flagged_not_silent(self):
        x = parse_length("3' - O\"")
        self.assertEqual((x.status, x.inches, x.ocr_repaired), ("parsed", 36, True))
        self.assertIn("'O'", x.flags[0]["message"])

    def test_trailing_text(self):
        x = parse_length("41' - 6\" (TO AVG. HT. OF HIGHEST ROOF SURFACE)")
        self.assertEqual(x.inches, 498)
        self.assertEqual(x.flags[0]["code"], "trailing_text")

    def test_unparsed(self):
        for t in ("SEE ELEVATIONS", "3-0", "LEFT"):
            self.assertEqual(parse_length(t).status, "unparsed")
        self.assertEqual(parse_length("").status, "empty")

    def test_fmt(self):
        self.assertEqual((fmt_in(18), fmt_in(498), fmt_in(44)), ("1'-6\"", "41'-6\"", "3'-8\""))


class Rooms(unittest.TestCase):
    def test_sleeping(self):
        for n in ("BEDROOM 101", "ADU BEDROOM 107", "GUEST BED 303", "BDRM 2", "MASTER BED RM", "BED ROOM 4"):
            with self.subTest(n):
                self.assertEqual(classify(n).kind, "sleeping")

    def test_ocr_near_match_counts_and_is_noted(self):
        for n in ("BEDRROM 205", "BEDROM 1", "BEDRUOM 3", "BERDOOM 9"):
            with self.subTest(n):
                c = classify(n)
                self.assertEqual(c.kind, "sleeping")
                self.assertEqual(c.flags[0]["code"], "ocr_room_name")

    def test_ambiguous(self):
        for n in ("OFFICE 102", "DEN", "LOFT 301", "STUDY", "ROOM 210", "FLEX SPACE"):
            with self.subTest(n):
                self.assertEqual(classify(n).kind, "ambiguous")

    def test_not_sleeping(self):
        for n in ("LIVING 103", "KITCHEN 104", "LAUNDRY 108", "BATH 206", "HALL 302", "STAIR S1"):
            with self.subTest(n):
                self.assertEqual(classify(n).kind, "not_sleeping")

    def test_bed_inside_other_words_does_not_count(self):
        self.assertNotEqual(classify("FLOWERBED STORAGE").kind, "sleeping")

    def test_room_key_by_number(self):
        self.assertEqual(room_key("BEDRROM 205"), room_key("BEDROOM 205"))
        self.assertEqual(room_key("STAIR S1"), "STAIR S1")


class Operations(unittest.TestCase):
    def test_vocabulary(self):
        self.assertEqual(classify_operation("L.H. CASM'T")[0], "casement")
        self.assertEqual(classify_operation("R.H. CASM'T")[0], "casement")
        self.assertEqual(classify_operation("S.H.")[0], "single_hung")
        self.assertEqual(classify_operation("FIXED")[0], "fixed")
        self.assertEqual(classify_operation("SLIDER")[0], "slider")
        self.assertEqual(classify_operation("AWNING")[0], "awning")
        self.assertIsNone(classify_operation("TILT-TURN")[0])
        self.assertIsNone(classify_operation("A")[0])


class CodeAnalysis(unittest.TestCase):
    def setUp(self):
        self.ca = read_code_analysis(CA)

    def test_fields(self):
        f = self.ca.facts
        self.assertEqual(f["occupancy"].value, "R-3")
        self.assertEqual(f["construction"].value, "V-B")
        self.assertIn("NFPA 13D", f["sprinklers"].value)
        self.assertTrue(f["height"].value.startswith("41' - 6\""))
        self.assertTrue(f["allowable_height"].value.startswith("60' - 0\""))
        self.assertIn("PROVIDED AT ALL SLEEPING ROOMS", f["egress_claim"].value)
        self.assertEqual(self.ca.unmatched, [])

    def test_split_labels_use_join_candidates_and_are_flagged(self):
        self.assertTrue(self.ca.facts["sprinklers"].via_join)   # FIRE SPRINKLE RS
        self.assertTrue(self.ca.facts["height"].via_join)       # ... GRADE PLAN E
        self.assertFalse(self.ca.facts["occupancy"].via_join)

    def test_rows_reordered_and_renamed(self):
        html = ("<table><tr><td>TYPE OF CONSTRUCTION</td><td>II-B</td></tr><tr><td>USE GROUP</td><td>B</td></tr>"
                "<tr><td>SPRINKLERS</td><td>NONE</td></tr><tr><td>HEIGHT</td><td>52'-0\"</td></tr></table>")
        f = read_code_analysis(html).facts
        self.assertEqual((f["construction"].value, f["occupancy"].value, f["sprinklers"].value),
                         ("II-B", "B", "NONE"))

    def test_conflicting_fields_recorded(self):
        html = "<table><tr><td>OCCUPANCY</td><td>R-3</td></tr><tr><td>OCCUPANCY GROUP</td><td>R-2</td></tr></table>"
        ca = read_code_analysis(html)
        self.assertEqual([x.value for x in ca.conflicts["occupancy"]], ["R-3", "R-2"])


class Schedule(unittest.TestCase):
    def setUp(self):
        self.s = read_window_schedule(WS)
        self.w = {w.mark: w for w in self.s.windows}

    def test_column_roles(self):
        r = self.s.columns.roles
        self.assertEqual((r["operation"], r["type_mark"], r["egress"], r["screen"]), ("c4", "c5", "c11", "c9"))
        self.assertEqual(self.s.columns.missing, [])

    def test_seventeen_windows_no_separator(self):
        self.assertEqual([w.mark for w in self.s.windows],
                         ["1", "2", "3", "4", "5", "6", "7", "8", "10", "11", "12", "13", "14", "20", "21", "22", "23"])

    def test_egress_set(self):
        self.assertEqual({m for m, w in self.w.items() if w.egress}, {"1", "3", "7", "10", "12", "13", "20"})

    def test_window_21_screen_not_egress_regression(self):
        """GUEST BED 303: Y is under SCREEN (c9), not EGRESS; a column shift would make it egress."""
        w = self.w["21"]
        self.assertEqual((w.screen_text, w.egress_text, w.egress), ("Y", "", False))

    def test_window_values(self):
        w = self.w["7"]
        self.assertEqual((w.width["inches"], w.height["inches"], w.head_height["inches"], w.operation),
                         (30, 36, 80, "casement"))
        self.assertEqual(self.w["4"].width["flags"][0]["code"], "ocr_repair")
        self.assertEqual(self.w["12"].room_class["flags"][0]["code"], "ocr_room_name")
        self.assertEqual(self.w["13"].operation, "fixed")

    def test_columns_in_another_order(self):
        flat = flat_schedule(["LOCATION", "MARK", "WIDTH", "HEIGHT", "OPERATION", "HEAD HT", "EGRESS"],
                             [["BEDROOM 2", "W-A", "2'-0\"", "2'-0\"", "CASEMENT", "6'-8\"", "Y"]])
        w = read_window_schedule(flat).windows[0]
        self.assertEqual((w.mark, w.room_name, w.width["inches"], w.operation, w.egress),
                         ("W-A", "BEDROOM 2", 24, "casement", True))

    def test_type_columns_swapped_by_content(self):
        flat = flat_schedule(["SYMBOL", "LOCATION", "WIDTH", "HEIGHT", "TYPE", "TYPE", "HEAD HEIGHT", "EGRESS"],
                             [["1", "BEDROOM 1", "3'-0\"", "4'-0\"", "A", "CASEMENT", "6'-8\"", "Y"],
                              ["2", "BEDROOM 1", "3'-0\"", "4'-0\"", "B", "FIXED", "6'-8\"", ""]])
        s = read_window_schedule(flat)
        self.assertEqual(s.windows[0].operation, "casement")
        self.assertEqual(s.windows[0].type_mark, "A")
        self.assertIn("type_columns_swapped", [n["code"] for n in s.columns.notes])

    def test_missing_egress_column(self):
        flat = flat_schedule(["SYMBOL", "LOCATION", "WIDTH", "HEIGHT", "TYPE", "HEAD HEIGHT"],
                             [["1", "BEDROOM 1", "3'-0\"", "4'-0\"", "CASEMENT", "6'-8\""]])
        s = read_window_schedule(flat)
        self.assertIn("egress", s.columns.missing)
        self.assertIsNone(s.windows[0].egress)
        self.assertIsNone(s.windows[0].egress_text)


if __name__ == "__main__":
    unittest.main()

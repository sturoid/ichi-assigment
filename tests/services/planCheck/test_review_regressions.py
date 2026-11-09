"""Regressions for the independent Sonnet review of the checks (2026-11-08). Each test
is the reviewer's failure scenario; each failed before the fix."""
import unittest

from test_policies import HEAD, S, code_analysis, crit, egress, win

from services.planCheck.checks import _number, check_height
from services.planCheck.findings import CNE, FAIL, NA, PASS
from services.planCheck.rooms import classify, room_key
from services.planCheck.units import parse_length


class Review(unittest.TestCase):
    def test_1_ns_new_only_where_footnote_d_is_printed(self):
        # README worked example with a 'NEW' project line: B / NS has no footnote d -> Pass
        h, _ = check_height(S, code_analysis(OCCUPANCY_GROUP="B", SPRINKLERS="NONE", CONSTRUCTION_TYPE="II-B",
                                             BUILDING_HEIGHT="52'-0\"", PROJECT="NEW OFFICE"))
        self.assertEqual(h.verdict, PASS)

    def test_2_decimal_feet(self):
        self.assertEqual(parse_length("41.5 FT").inches, 498)
        self.assertEqual(parse_length("41.5'").inches, 498)
        h, _ = check_height(S, code_analysis(BUILDING_HEIGHT="41.5 FT"))
        self.assertEqual(h.verdict, FAIL)

    def test_4_no_egress_column_gives_no_window_fails(self):
        hdr = [x for x in HEAD if x != "EGRESS"]
        rows = [[c for i, c in enumerate(win(str(n), op=op)) if HEAD[i] != "EGRESS"]
                for n, op in ((1, "FIXED"), (2, "CASEMENT"))]
        f, _ = egress(rows, headers=hdr)
        self.assertEqual((f["W-1"].verdict, f["W-2"].verdict), (NA, NA))
        self.assertEqual(f["R-201"].verdict, CNE)

    def test_5_unnumbered_rooms_with_ocr_spelling_are_one_room(self):
        self.assertEqual(room_key("BEDRROM 2"), room_key("BEDROOM 2"))
        self.assertNotEqual(room_key("BED 2"), room_key("BATH 2"))
        f, _ = egress([win("1", "BEDROOM 2", op="FIXED"), win("2", "BEDRROM 2", egress="")])
        rooms = [k for k in f if k.startswith("R-")]
        self.assertEqual(rooms, ["R-BEDROOM-2"])

    def test_6_compound_room_name_is_ambiguous(self):
        c = classify("BEDROOM BATH 206")
        self.assertEqual(c.kind, "ambiguous")
        self.assertEqual(c.flags[0]["code"], "ambiguous_room")

    def test_7_net_clear_units(self):
        self.assertEqual(_number("5.9"), 5.9)
        self.assertEqual(_number("5.9 SF"), 5.9)
        self.assertIsNone(_number("840"))           # bare 840 is not 840 sq ft
        self.assertAlmostEqual(_number("864 SQ IN"), 6.0)
        hdr = HEAD + ["NET CLEAR OPENING"]
        f, _ = egress([win() + ["840"]], headers=hdr)
        self.assertNotEqual(crit(f["W-1"], "Net clear opening").verdict, PASS)


if __name__ == "__main__":
    unittest.main()

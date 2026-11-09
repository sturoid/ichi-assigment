"""One test per named policy rule, on synthetic project sheets (not the fixtures), so
each rule is shown to work for any project. test_every_policy_has_a_test enforces it."""
import unittest

from _setup import MANIFEST, STORE

from services.codeStore import Store
from services.planCheck.checks import check_egress, check_height, run_checks
from services.planCheck.facts import read_code_analysis, read_window_schedule
from services.planCheck.findings import CNE, FAIL, NA, PASS
from services.planCheck.policies import POLICIES

S = Store.load(STORE, manifest=MANIFEST)

HEAD = ["SYMBOL", "LOCATION", "WIDTH", "HEIGHT", "TYPE", "HEAD HEIGHT", "EGRESS", "SCREEN"]


def code_analysis(**fields):
    base = {"PROJECT": "NEW HOUSE", "OCCUPANCY GROUP": "R-3", "CONSTRUCTION TYPE": "V-B",
            "SPRINKLERS": "AUTOMATIC SPRINKLER SYSTEM THROUGHOUT PER NFPA 13D", "NUMBER OF STORIES": "2",
            "BUILDING HEIGHT": "30' - 0\"", "ROOM NUMBERING": "1XX = FIRST FLOOR, 2XX = SECOND FLOOR",
            "EMERGENCY ESCAPE & RESCUE": "PROVIDED AT ALL SLEEPING ROOMS"}
    for k, v in fields.items():
        k = k.replace("_", " ")
        if v is None:
            base.pop(k, None)
        else:
            base[k] = v
    return read_code_analysis("<table>" + "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in base.items())
                              + "</table>")


def schedule(rows, headers=HEAD):
    return read_window_schedule("<table><tr><th>" + "</th><th>".join(headers) + "</th></tr>"
                                + "".join("<tr><td>" + "</td><td>".join(r) + "</td></tr>" for r in rows)
                                + "</table>")


def win(mark="1", room="BEDROOM 201", w="3' - 0\"", h="4' - 0\"", op="CASEMENT", head="6' - 8\"", egress="Y",
        screen=""):
    return [mark, room, w, h, op, head, egress, screen]


def egress(rows, ca=None, headers=HEAD):
    rooms, windows, attn = check_egress(S, ca or code_analysis(), schedule(rows, headers))
    return {f.id: f for f in rooms + windows}, attn


def crit(f, word):
    return next(c for c in f.criteria if word in c.requirement)


class Policies(unittest.TestCase):
    def test_every_policy_has_a_test(self):
        names = {n for n in dir(self) if n.startswith("test_")}
        for pid in POLICIES:
            self.assertIn("test_" + pid.lower().replace("-", "_"), names, pid)

    # --- general --------------------------------------------------------------------
    def test_pol_gen_amendments(self):
        self.assertEqual(POLICIES["POL-GEN-AMENDMENTS"].authority, "project_decision")
        self.assertEqual(S.documents["LOCAL:MERIDIAN-FALLS:IBC-AMENDMENTS"]["status"], "unavailable")

    def test_pol_gen_ocr(self):
        # a 2'-O" wide window would fail clear width (24 > 20? no) -> use 1'-O" (12 in) which would Fail
        f, _ = egress([win(w="1' - O\"")])
        c = crit(f["W-1"], "width")
        self.assertEqual(c.verdict, CNE)
        self.assertIn("POL-GEN-OCR", c.policies)
        h, _ = check_height(S, code_analysis(BUILDING_HEIGHT="4l' - 6\""))
        self.assertEqual(h.verdict, CNE)

    def test_pol_gen_uncovered(self):
        # a cell that is not a number (none in 504.3 except UL, which is a number via inf): simulate by text
        self.assertIn("needs a policy decision", POLICIES["POL-GEN-UNCOVERED"].rule)

    # --- height ---------------------------------------------------------------------
    def test_pol_h_interpretation(self):
        h, _ = check_height(S, code_analysis())
        self.assertEqual(h.verdict, PASS)  # 30 ft <= 40
        self.assertIn("POL-H-INTERPRETATION", h.policies)
        self.assertTrue(any("R-3" in i and "challenge_brief" in i for i in h.interpretations))
        h, _ = check_height(S, code_analysis(OCCUPANCY_GROUP="B", SPRINKLERS="NONE", CONSTRUCTION_TYPE="II-B",
                                             BUILDING_HEIGHT="52'-0\"", PROJECT="OFFICE ADDITION"))
        self.assertEqual((h.verdict, h.interpretations), (PASS, []))  # the README worked example

    def test_pol_h_footnotes(self):
        h, _ = check_height(S, code_analysis())
        self.assertTrue(any("footnote h" in r for r in h.code_refs))
        self.assertTrue(any("IBC:2018:903" in s for s in h.settle))

    def test_pol_h_ns_new(self):
        h, _ = check_height(S, code_analysis(SPRINKLERS="NONE"))
        self.assertEqual(h.verdict, CNE)
        self.assertIn("POL-H-NS-NEW", h.policies)
        h, _ = check_height(S, code_analysis(SPRINKLERS="NONE", PROJECT="EXISTING HOUSE"))
        self.assertEqual(h.verdict, PASS)

    def test_pol_h_stated_height(self):
        h, _ = check_height(S, code_analysis(BUILDING_HEIGHT="41' - 6\""))
        self.assertEqual(h.verdict, FAIL)
        self.assertIn("1'-6\"", h.summary)
        self.assertTrue(any("PROJECT:BUILDING-SECTIONS" in s for s in h.settle))
        h, _ = check_height(S, code_analysis(BUILDING_HEIGHT=None))
        self.assertEqual(h.verdict, CNE)
        h, _ = check_height(S, code_analysis(CONSTRUCTION_TYPE=None))
        self.assertEqual(h.verdict, CNE)  # brief: no construction type -> Could Not Evaluate

    def test_pol_h_architect(self):
        h, attn = check_height(S, code_analysis(ALLOWABLE_HEIGHT="60' - 0\" PER TABLE 504.3"))
        fl = next(f for f in h.flags if f["code"] == "architect_allowable_mismatch")
        self.assertIn("`R` / `S`", fl["message"])
        self.assertIn("`R` / `S13R`", fl["message"])
        self.assertEqual(attn[0].code, "architect_allowable_mismatch")
        h, attn = check_height(S, code_analysis(ALLOWABLE_HEIGHT="40' - 0\""))
        self.assertEqual(attn, [])

    def test_pol_h_sprinkler_coverage(self):
        h, _ = check_height(S, code_analysis(SPRINKLERS="NFPA 13D AT GARAGE ONLY"))
        self.assertEqual(h.verdict, CNE)
        h, _ = check_height(S, code_analysis(SPRINKLERS="NFPA 13D"))
        self.assertEqual(h.verdict, PASS)
        self.assertIn("sprinkler_coverage_not_stated", [f["code"] for f in h.flags])
        h, _ = check_height(S, code_analysis(SPRINKLERS="YES"))
        self.assertEqual(h.verdict, CNE)

    # --- egress scope ---------------------------------------------------------------
    def test_pol_e_scope(self):
        f, _ = egress([win()], code_analysis(OCCUPANCY_GROUP="B"))
        self.assertEqual((f["W-1"].verdict, f["R-201"].verdict), (NA, NA))
        f, _ = egress([win(w="1' - 6\"")], code_analysis(OCCUPANCY_GROUP="R-2"))
        self.assertEqual(f["W-1"].verdict, CNE)  # would Fail, but R-2 scope depends on exits
        self.assertIn("would be Fail", f["W-1"].summary)
        f, _ = egress([win(room="BEDROOM 501")], code_analysis(ROOM_NUMBERING="5XX = FIFTH FLOOR"))
        self.assertEqual(f["W-1"].verdict, NA)
        f, _ = egress([win(room="BEDROOM 501")], code_analysis(ROOM_NUMBERING=None, NUMBER_OF_STORIES="6"))
        self.assertEqual(f["R-501"].verdict, CNE)

    def test_pol_e_sleeping(self):
        f, attn = egress([win(room="DEN 104", egress="")])
        self.assertEqual(f["W-1"].verdict, NA)
        self.assertIn("ambiguous_room", [x["code"] for x in f["W-1"].flags])
        self.assertNotIn("R-104", f)
        f, _ = egress([win(room="BEDROM 202", w="1' - 6\"")])
        self.assertEqual(f["R-202"].verdict, FAIL)  # one-character OCR miss still counts

    def test_pol_e_room_key(self):
        f, _ = egress([win("1", "BEDRROM 205", op="FIXED"), win("2", "BEDROOM 205", egress="")])
        self.assertEqual(f["R-205"].related, ["W-1", "W-2"])
        self.assertIn("room_name_variants", [x["code"] for x in f["R-205"].flags])

    def test_pol_e_not_sleeping(self):
        f, _ = egress([win(room="KITCHEN 104")])
        self.assertEqual(f["W-1"].verdict, NA)
        self.assertIn("egress_in_non_sleeping_room", [x["code"] for x in f["W-1"].flags])

    def test_pol_e_not_designated(self):
        f, _ = egress([win("1"), win("2", op="FIXED", egress="")])
        self.assertEqual(f["W-2"].verdict, NA)
        self.assertEqual(f["W-2"].related, ["R-201"])

    # --- what nominal size proves ---------------------------------------------------
    def test_pol_e_nominal_upper(self):
        f, _ = egress([win(w="2' - 0\"", h="2' - 0\"")])  # README W-A: 4.0 sq ft
        self.assertEqual(crit(f["W-1"], "Net clear opening").verdict, FAIL)
        self.assertEqual(f["W-1"].verdict, FAIL)
        f, _ = egress([win(w="2' - 0\"", h="2' - 6\"")])  # exactly 5.0 nominal: net < 5.0
        self.assertEqual(crit(f["W-1"], "Net clear opening").verdict, FAIL)
        f, _ = egress([win(w="1' - 8\"")])  # 20 in nominal width: clear < 20
        self.assertEqual(crit(f["W-1"], "width").verdict, FAIL)

    def test_pol_e_no_frame_assumption(self):
        f, _ = egress([win(w="3' - 0\"", h="3' - 6\"", head="7' - 0\"")])  # README W-B
        self.assertEqual(crit(f["W-1"], "Net clear opening").verdict, CNE)
        self.assertEqual(f["W-1"].verdict, CNE)
        self.assertEqual(f["R-201"].verdict, CNE)

    def test_pol_e_sill_lower(self):
        f, _ = egress([win(h="3' - 0\"", head="8' - 0\"")])  # 96 - 36 = 60
        self.assertEqual(crit(f["W-1"], "Bottom").verdict, FAIL)
        f, _ = egress([win(h="3' - 0\"", head="6' - 8\"")])  # 80 - 36 = 44: "not greater than" -> not a Fail
        self.assertEqual(crit(f["W-1"], "Bottom").verdict, CNE)
        self.assertIn("44", crit(f["W-1"], "Bottom").read)

    def test_pol_e_grade_floor(self):
        f, _ = egress([win(w="2' - 6\"", h="2' - 6\"")])  # 6.25? no: 30x30 = 6.25 sq ft > 5.7
        self.assertEqual(crit(f["W-1"], "Net clear opening").verdict, CNE)
        f, _ = egress([win(w="2' - 0\"", h="2' - 9\"")])  # 24x33 = 5.5: < 5.7 but > 5.0
        c = crit(f["W-1"], "Net clear opening")
        self.assertEqual(c.verdict, CNE)
        self.assertIn("grade-floor", c.reason)
        hdr = HEAD + ["NET CLEAR OPENING"]
        f, _ = egress([win() + ["5.4 SF"]], headers=hdr)
        self.assertEqual(crit(f["W-1"], "Net clear opening").verdict, CNE)
        f, _ = egress([win() + ["4.8"]], headers=hdr)
        self.assertEqual(crit(f["W-1"], "Net clear opening").verdict, FAIL)
        f, _ = egress([win() + ["5.9"]], headers=hdr)
        self.assertEqual(crit(f["W-1"], "Net clear opening").verdict, PASS)

    def test_pol_e_fixed(self):
        f, _ = egress([win(op="FIXED")])
        self.assertEqual(f["W-1"].verdict, FAIL)
        self.assertEqual(f["R-201"].verdict, FAIL)
        self.assertIn("Exception 2", f["R-201"].summary)

    def test_pol_e_partial_opening(self):
        f, _ = egress([win(w="3' - 0\"", h="4' - 0\"", op="S.H.")])
        c = crit(f["W-1"], "height")
        self.assertEqual(c.verdict, CNE)  # half of 48 = 24 is a note, not proof
        self.assertIn("Note only", c.reason)
        f, _ = egress([win(w="3' - 0\"", h="4' - 0\"", op="SLIDER")])
        self.assertIn("Note only", crit(f["W-1"], "width").reason)
        self.assertEqual(f["W-1"].verdict, CNE)

    def test_pol_e_operation_unknown(self):
        f, _ = egress([win(op="TILT-TURN")])
        self.assertEqual(crit(f["W-1"], "Opens").verdict, CNE)

    def test_pol_e_unseen(self):
        hdr = HEAD + ["NET CLEAR OPENING", "CLEAR WIDTH", "CLEAR HEIGHT", "SILL HEIGHT"]
        f, _ = egress([win(h="4' - 0\"", head="6' - 0\"") + ["6.0", "24\"", "36\"", "24\""]], headers=hdr)
        unseen = [c for c in f["W-1"].criteria if "POL-E-UNSEEN" in c.policies]
        self.assertEqual([c.verdict for c in unseen], [CNE, CNE, CNE])
        others = [c for c in f["W-1"].criteria if "POL-E-UNSEEN" not in c.policies]
        self.assertTrue(all(c.verdict in (PASS, CNE) for c in others))
        self.assertEqual(f["W-1"].verdict, CNE)  # unseen items keep it from a Pass, never Fail it

    # --- rooms ----------------------------------------------------------------------
    def test_pol_e_room_rollup(self):
        # no window designated, one could comply -> CNE flagged
        f, _ = egress([win("1", egress="")])
        self.assertEqual(f["R-201"].verdict, CNE)
        self.assertIn("no_opening_designated", [x["code"] for x in f["R-201"].flags])
        # designated fails, an undesignated one could comply -> CNE
        f, _ = egress([win("1", op="FIXED"), win("2", egress="")])
        self.assertEqual(f["R-201"].verdict, CNE)
        self.assertIn("no_complying_opening_designated", [x["code"] for x in f["R-201"].flags])
        # one fails, one CNE -> CNE (README Bedroom 2)
        f, _ = egress([win("A", w="2' - 0\"", h="2' - 0\""), win("B", w="3' - 0\"", h="3' - 6\"", head="7' - 0\"")])
        self.assertEqual(f["R-201"].verdict, CNE)
        # nothing could comply, nothing designated -> Fail
        f, _ = egress([win("1", op="FIXED", egress="")])
        self.assertEqual(f["R-201"].verdict, FAIL)

    def test_pol_e_exception_2(self):
        f, _ = egress([win(op="FIXED")])
        self.assertIn("POL-E-EXCEPTION-2", f["R-201"].policies)
        self.assertTrue(any("Exception 2" in s for s in f["R-201"].settle))

    def test_pol_e_no_egress_column(self):
        hdr = [h for h in HEAD if h != "EGRESS"]
        rows = [[c for i, c in enumerate(win("1")) if HEAD[i] != "EGRESS"],
                [c for i, c in enumerate(win("2", op="FIXED")) if HEAD[i] != "EGRESS"]]
        f, attn = egress(rows, headers=hdr)
        self.assertEqual(f["R-201"].verdict, CNE)
        self.assertIn("POL-E-NO-EGRESS-COLUMN", f["R-201"].policies)
        self.assertIn("no_egress_column", [a.code for a in attn])
        rows = [[c for i, c in enumerate(win("2", op="FIXED")) if HEAD[i] != "EGRESS"]]
        f, _ = egress(rows, headers=hdr)
        self.assertEqual(f["R-201"].verdict, FAIL)


class Generality(unittest.TestCase):
    def test_checks_never_name_fixture_windows_or_rooms(self):
        import re
        from pathlib import Path
        import services.planCheck as pc
        src = "\n".join(p.read_text(encoding="utf-8") for p in Path(pc.__file__).parent.glob("*.py"))
        for token in ("BEDRROM", "GUEST BED 303", "OFFICE 102", "\"303\"", "\"205\"", "'W-13'", "41.5",
                      "MERIDIAN", "Meridian", "A0.1", "A6.1"):
            self.assertFalse(token in src, token)
        self.assertFalse(re.search(r"mark\s*==\s*['\"]\d", src))


if __name__ == "__main__":
    unittest.main()

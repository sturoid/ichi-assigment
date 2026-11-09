"""Resolver: every mapping cites its rule; unresolved never guesses."""
import unittest

from _setup import MANIFEST, STORE

from services.codeStore import Store
from services.planCheck.resolver import RULES, resolve

S = Store.load(STORE, manifest=MANIFEST)
VALUES = S.provisions["IBC:2018:T504.3"]["dimensions"]["values"]


def r(dim, text):
    return resolve(dim, text, VALUES[dim])


class Occupancy(unittest.TestCase):
    def test_r3_to_r_is_an_interpretation(self):
        x = r("occupancy", "R-3")
        self.assertEqual((x.status, x.value), ("resolved", "R"))
        self.assertEqual([i["id"] for i in x.interpretations], ["occupancy.numbered_group"])
        self.assertEqual(x.rules[0]["cites"]["lines"], [54])
        self.assertIn("IBC:2018:310", x.rules[0]["unavailable"])

    def test_numbered_group_with_own_row_is_exact(self):
        x = r("occupancy", "I-4")
        self.assertEqual((x.value, x.interpretations), ("I-4", []))
        self.assertEqual(r("occupancy", "I-1 Condition 1").value, "I-1 Condition 1")
        self.assertEqual(r("occupancy", "B").value, "B")

    def test_numbered_group_without_letter_row_is_unresolved(self):
        self.assertEqual(r("occupancy", "I-9").status, "unresolved")

    def test_mixed_occupancy_unresolved(self):
        x = r("occupancy", "R-3 / U")
        self.assertEqual(x.status, "unresolved")
        self.assertIn("several", x.reason)

    def test_description_ignored(self):
        self.assertEqual(r("occupancy", "R-3 (SINGLE FAMILY)").value, "R")

    def test_missing(self):
        self.assertEqual(r("occupancy", "").status, "unresolved")


class Construction(unittest.TestCase):
    def test_forms(self):
        for t in ("V-B", "VB", "V B", "TYPE V-B", "type vb", "Type V - B", "V–B"):
            with self.subTest(t):
                x = r("construction", t)
                self.assertEqual((x.status, x.value), ("resolved", "V-B"))
                self.assertEqual(x.interpretations, [])
        self.assertEqual(r("construction", "IV-HT").value, "IV-HT")

    def test_not_in_table(self):
        self.assertEqual(r("construction", "VI-B").status, "unresolved")
        self.assertEqual(r("construction", "IV-A").status, "unresolved")  # no IV-A column in 504.3
        self.assertEqual(r("construction", "WOOD FRAME").status, "unresolved")


class Sprinkler(unittest.TestCase):
    def test_fixture_wording(self):
        x = r("sprinkler", "YES - AUTOMATIC SPRINKLER SYSTEM THROUGHOUT PER NFPA 13D (IBC 903.3.1.3)")
        self.assertEqual((x.status, x.value), ("resolved", "S13D"))
        self.assertEqual(x.rules[0]["cites"]["lines"], [15, 39])

    def test_each_standard(self):
        self.assertEqual(r("sprinkler", "NFPA 13").value, "S")
        self.assertEqual(r("sprinkler", "per 903.3.1.1").value, "S")
        self.assertEqual(r("sprinkler", "NFPA 13R").value, "S13R")
        self.assertEqual(r("sprinkler", "IBC 903.3.1.2").value, "S13R")
        self.assertEqual(r("sprinkler", "NFPA-13D").status, "unresolved")  # unusual spelling: not guessed

    def test_none(self):
        for t in ("NONE", "No", "NOT SPRINKLERED", "NONE REQUIRED"):
            with self.subTest(t):
                self.assertEqual(r("sprinkler", t).value, "NS")

    def test_unsure_cases(self):
        self.assertIn("not stated", r("sprinkler", "YES").reason)
        self.assertIn("throughout", r("sprinkler", "NFPA 13D AT GARAGE ONLY").reason)
        self.assertIn("disagree", r("sprinkler", "NFPA 13R PER 903.3.1.1").reason)
        self.assertEqual(r("sprinkler", "PARTIAL - NFPA 13").status, "unresolved")


class Format(unittest.TestCase):
    def test_every_rule_cites_and_has_authority(self):
        for rule in RULES:
            self.assertTrue(rule["cites"])
            self.assertIn(rule["authority"], ("code_text", "challenge_brief"))

    def test_resolved_value_is_found_in_store(self):
        q = {d: r(d, t).value for d, t in (("occupancy", "R-3"), ("sprinkler", "NFPA 13D"), ("construction", "VB"))}
        self.assertEqual(S.lookup("IBC:2018:T504.3", **q).value, 40)


if __name__ == "__main__":
    unittest.main()

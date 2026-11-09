"""Phase 2: the Table 504.3 notes file loaded into the store. Expected values are
hand-typed from code/table-504.3-notes.md (line numbers checked by eye)."""
import unittest

from _store_setup import MANIFEST

from services.codeStore import Store, build_store
from services.codeStore.table_notes import extract_references, link_reference

T504 = "IBC:2018:T504.3"


class NotesLoaded(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data, _ = build_store(MANIFEST)
        cls.p = cls.data["provisions"][T504]
        cls.notes = cls.p["notes"]

    def test_conditions_loaded(self):
        self.assertTrue(self.p["conditions_loaded"])

    def test_footnotes_a_to_h_with_lines(self):
        want = {"a": 19, "b": 21, "c": 23, "d": 25, "e": 27, "f": 29, "g": 31, "h": 33}
        got = {k: v["source"]["line"] for k, v in self.notes["footnotes"].items()}
        self.assertEqual(got, want)
        self.assertEqual(self.notes["footnotes"]["d"]["text"],
                         "The NS value is only for use in evaluation of existing building height in accordance "
                         "with the International Existing Building Code.")
        for fn in self.notes["footnotes"].values():
            self.assertEqual(fn["authority"], "code_text")

    def test_footnote_references_link_to_manifest_ids(self):
        refs = {k: [(r["ref"], r["document"], r["status"]) for r in v["references"]]
                for k, v in self.notes["footnotes"].items()}
        self.assertEqual(refs["a"], [("IBC CH 4", "IBC:2018:CH4-CH5", "unavailable"),
                                     ("IBC CH 5", "IBC:2018:CH4-CH5", "unavailable")])
        self.assertEqual(refs["d"], [("IEBC", "IEBC:2018", "unavailable")])
        self.assertEqual(refs["f"], [("IBC 903.2.6", "IBC:2018:903", "unavailable"),
                                     ("IFC 1103.5", "IFC:2018:1103.5", "unavailable")])
        self.assertEqual(refs["h"], [("IBC 903.2.8", "IBC:2018:903", "unavailable")])

    def test_legend_per_sub_row_value(self):
        leg = self.notes["legend"]
        self.assertEqual(set(leg), {"UL", "NS", "S", "S13R", "S13D"})
        self.assertTrue(all(v["source"]["line"] == 15 for v in leg.values()))
        self.assertIn("Section 903.3.1.3", leg["S13D"]["text"])
        self.assertIn("not equipped throughout", leg["NS"]["text"])
        self.assertEqual(leg["UL"]["text"], "Unlimited")
        # every sprinkler sub-row in the table has a legend entry
        self.assertTrue(set(self.p["dimensions"]["values"]["sprinkler"]) <= set(leg))

    def test_sprinkler_shorthand_with_lines(self):
        got = [(x["section"], x["standard"], x["source"]["line"], x["supplementary"])
               for x in self.notes["sprinkler_shorthand"]]
        self.assertEqual(got, [("903.3.1.1", "NFPA 13", 37, True), ("903.3.1.2", "NFPA 13R", 38, True),
                               ("903.3.1.3", "NFPA 13D", 39, True)])

    def test_lookup_conditions_carry_text_and_source(self):
        r = Store(self.data).lookup(T504, occupancy="I-4", sprinkler="NS", construction="III-B")
        self.assertEqual(r.value, 55)
        self.assertEqual([(c["mark"], c["source"]["line"]) for c in r.conditions], [("a", 19), ("d", 25), ("g", 31)])


class ReferenceExtraction(unittest.TestCase):
    def test_forms(self):
        self.assertEqual(extract_references("see Exceptions 2 and 3 of Section 903.2.6."), ["IBC 903.2.6"])
        self.assertEqual(extract_references("Section 903.2.6 and Section 1103.5 of the International Fire Code"),
                         ["IBC 903.2.6", "IFC 1103.5"])
        self.assertEqual(extract_references("See Chapters 4 and 5"), ["IBC CH 4", "IBC CH 5"])
        self.assertEqual(extract_references("no references here"), [])

    def test_unlisted_reference_is_kept_not_dropped(self):
        self.assertEqual(link_reference("IBC 907.2.10", [{"id": "X", "status": "available", "covers": ["^IBC 903"]}]),
                         {"ref": "IBC 907.2.10", "document": None, "status": "unlisted"})

    def test_most_specific_cover_wins(self):
        docs = [{"id": "IBC:2018:1030", "status": "available", "covers": [r"^IBC 1030(\.|$)"]},
                {"id": "IBC:2018:1030.4", "status": "unavailable", "covers": [r"^IBC 1030\.4(\.|$)"]}]
        self.assertEqual(link_reference("IBC 1030.4.2", docs)["document"], "IBC:2018:1030.4")
        self.assertEqual(link_reference("IBC 1030.2", docs)["document"], "IBC:2018:1030")


if __name__ == "__main__":
    unittest.main()

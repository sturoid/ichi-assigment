"""Store contract tests: golden lookups, every status, an exhaustive sweep against the
hand-typed expected values, determinism, and validator mutations."""
import copy
import json
import os
import tempfile
import unittest
from pathlib import Path

from _store_setup import EXPECTED, FIXTURES, MANIFEST

from services.codeStore import Store, StoreError, build_store, dumps, validate_store, write_store
from services.codeStore import store as store_mod

T504 = "IBC:2018:T504.3"


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data, cls.sidecars = build_store(MANIFEST)
        cls.s = Store(cls.data)

    def q(self, **dims):
        return self.s.lookup(T504, **dims)


class GoldenLookups(Base):
    def test_readme_worked_example(self):
        """README Check 1: B / no sprinklers / II-B -> 55, cited by its printed labels."""
        r = self.q(occupancy="B", sprinkler="NS", construction="II-B")
        self.assertEqual(r.status, "found")
        self.assertEqual((r.value, r.value_kind, r.unit), (55, "number", "ft"))
        self.assertEqual(r.citation["row_labels"], {"occupancy": "A, B, E, F, M, S, U", "sprinkler": "NS"})
        self.assertEqual(r.citation["column"], "II-B")
        self.assertEqual(r.citation["text"], "Table 504.3, row `A, B, E, F, M, S, U` / `NS`, column `II-B`")
        self.assertEqual(r.authority, "code_text")
        self.assertEqual(r.source["file"], "table-504.3.html")

    def test_project_case(self):
        """The project's own cell: R / S13D / V-B is 40 ft (the architect claims 60)."""
        r = self.q(occupancy="R", sprinkler="S13D", construction="V-B")
        self.assertEqual((r.status, r.value), ("found", 40))

    def test_unlimited_token(self):
        r = self.q(occupancy="A", sprinkler="S", construction="I-A")
        self.assertEqual((r.status, r.value, r.value_kind, r.value_text), ("found", None, "unlimited", "UL"))

    def test_matching_ignores_case_and_spacing_only(self):
        self.assertEqual(self.q(occupancy=" r ", sprinkler="s13d", construction="v-b").value, 40)
        self.assertEqual(self.q(occupancy="R", sprinkler="S13D", construction="VB").status, "invalid_input")

    def test_table_footnote_a_on_every_cell_and_conditions_loaded(self):
        """Phase 2: footnote text is loaded from the notes file (was: text None, incomplete)."""
        a_text = "See Chapters 4 and 5 for specific exceptions to the allowable height in this chapter."
        for c in self.data["provisions"][T504]["cells"]:
            self.assertIn({"kind": "footnote", "mark": "a", "attached_to": "table", "text": a_text}, c["conditions"])
        r = self.q(occupancy="B", sprinkler="NS", construction="II-B")
        self.assertTrue(r.conditions_complete)
        self.assertEqual([(c["mark"], c["attached_to"]) for c in r.conditions],
                         [("a", "table"), ("b", "row_label:sprinkler")])


class Statuses(Base):
    def test_not_found_combination(self):
        r = self.q(occupancy="A", sprinkler="S13R", construction="I-A")
        self.assertEqual((r.status, r.error_codes()), ("not_found", ["no_cell"]))

    def test_unknown_value_lists_allowed(self):
        r = self.q(occupancy="R-3", sprinkler="S13D", construction="V-B")
        self.assertEqual((r.status, r.error_codes()), ("invalid_input", ["unknown_value"]))
        self.assertIn("R", r.errors[0]["allowed"])

    def test_missing_dimension_none_blank_or_absent(self):
        for dims in ({"sprinkler": "S13D", "construction": "V-B"},
                     {"occupancy": None, "sprinkler": "S13D", "construction": "V-B"},
                     {"occupancy": "  ", "sprinkler": "S13D", "construction": "V-B"}):
            r = self.q(**dims)
            self.assertEqual((r.status, r.error_codes()), ("invalid_input", ["missing_dimension"]), dims)
            self.assertEqual(r.errors[0]["dimension"], "occupancy")

    def test_unknown_dimension_and_type(self):
        r = self.q(occupancy="R", sprinkler="S13D", construction="V-B", floor="1")
        self.assertEqual(r.error_codes(), ["unknown_dimension"])
        r = self.q(occupancy="R", sprinkler="S13D", construction=5)
        self.assertEqual(r.error_codes(), ["invalid_type"])

    def test_every_problem_is_listed(self):
        r = self.q(occupancy="R-3", construction="TYPE V-B", floor="1")
        self.assertEqual(sorted(r.error_codes()), ["missing_dimension", "unknown_dimension", "unknown_value", "unknown_value"])

    def test_unavailable_document(self):
        r = self.s.lookup("IBC:2018:310", occupancy="R-3")
        self.assertEqual((r.status, r.error_codes()), ("unavailable", ["unavailable_document"]))
        self.assertTrue(r.errors[0]["referenced_by"])

    def test_available_but_not_loaded(self):
        r = self.s.lookup("IBC:2018:1030")
        self.assertEqual((r.status, r.error_codes()), ("unavailable", ["not_loaded"]))

    def test_unknown_provision(self):
        r = self.s.lookup("IBC:2018:T999")
        self.assertEqual((r.status, r.error_codes()), ("invalid_input", ["unknown_provision"]))

    def test_non_found_results_carry_no_value(self):
        d = self.q(occupancy="R-3", sprinkler="S13D", construction="V-B").to_dict()
        self.assertNotIn("value", d)
        self.assertNotIn("citation", d)


class ExhaustiveSweep(Base):
    """Every hand-typed value (typed from the printed table, not from parser output)
    must come back from the store, and every store cell must be one of them."""

    def test_every_expected_cell(self):
        exp = json.loads((EXPECTED / "table-504.3.expected.json").read_text(encoding="utf-8"))
        hit = set()
        for row in exp["rows"]:
            atoms = [a.strip() for a in row["occupancy"].split(",")]
            for con, want in zip(exp["construction_order"], row["values"]):
                for occ in atoms:
                    with self.subTest(occ=occ, spr=row["sprinkler"], con=con):
                        r = self.q(occupancy=occ, sprinkler=row["sprinkler"], construction=con)
                        self.assertEqual(r.status, "found")
                        if want == "UL":
                            self.assertEqual(r.value_kind, "unlimited")
                        else:
                            self.assertEqual(r.value, want)
                        self.assertEqual(r.citation["row_labels"]["occupancy"], row["occupancy"])
                        marks = {c["mark"] for c in r.conditions if c["attached_to"] != "table"}
                        self.assertEqual(marks, set(row["footnotes"]))
                        hit.add(r.source["cell_id"])
        cells = {c["id"] for c in self.data["provisions"][T504]["cells"]}
        self.assertEqual(hit, cells, "store cells not covered by the expected values")
        self.assertEqual(len(cells), 144)


class Determinism(unittest.TestCase):
    def test_same_bytes_twice_and_from_another_directory(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            write_store(MANIFEST, Path(a))
            cwd = os.getcwd()
            try:
                os.chdir(b)
                write_store(MANIFEST, Path(b) / "out")
            finally:
                os.chdir(cwd)
            for rel in ("store.json", "grids/IBC-2018-T504.3.grid.json"):
                self.assertEqual((Path(a) / rel).read_bytes(), (Path(b) / "out" / rel).read_bytes(), rel)

    def test_no_absolute_paths_or_timestamps(self):
        text = dumps(build_store(MANIFEST)[0])
        self.assertNotIn(str(FIXTURES), text)
        self.assertNotIn(str(FIXTURES).replace("\\", "/"), text)
        self.assertNotIn("parsed_at", text)

    def test_committed_store_is_current(self):
        """tests/fixtures/store is generated; rebuild it after any parser or manifest change."""
        store, sidecars = build_store(MANIFEST)
        self.assertEqual((FIXTURES / "store/store.json").read_text(encoding="utf-8"), dumps(store),
                         "run: cd src && python -m services.codeStore build ../tests/fixtures/manifest.json "
                         "-o ../tests/fixtures/store")
        for rel, side in sidecars.items():
            self.assertEqual((FIXTURES / "store" / rel).read_text(encoding="utf-8"), dumps(side), rel)


class Validator(Base):
    def test_built_store_is_valid(self):
        self.assertEqual(validate_store(self.data), [])

    def mutated(self, fn):
        d = copy.deepcopy(self.data)
        fn(d)
        return validate_store(d)

    def assertCaught(self, fn, fragment):
        errs = self.mutated(fn)
        self.assertTrue(any(fragment in e for e in errs), f"expected {fragment!r} in {errs}")

    def p(self, d):
        return d["provisions"][T504]

    def test_mutations_are_caught(self):
        def first_cell(d):
            return self.p(d)["cells"][0]
        cases = [
            (lambda d: first_cell(d).update(authority="challenge_brief"), "must be 'code_text'"),
            (lambda d: first_cell(d)["conditions"][0].update(text="See Chapters 4 and 5"), "differs from its footnote"),
            (lambda d: [c.update(text=None) for c in first_cell(d)["conditions"]], "has no text"),
            (lambda d: self.p(d).update(conditions_loaded=False), "conditions_loaded is false"),
            (lambda d: self.p(d)["notes"]["footnotes"]["a"].update(authority="challenge_brief"), "code_text authority"),
            (lambda d: self.p(d)["index"].update({"ZZ|NS|I-A": "nope"}), "missing cell"),
            (lambda d: self.p(d)["index"].pop(first_cell(d)["keys"][0]), "is not indexed"),
            (lambda d: self.p(d)["cells"].append(copy.deepcopy(first_cell(d))), "duplicate cell id"),
            (lambda d: self.p(d).update(grid_file="grids/IBC:2018:T504.3.grid.json"), "Windows"),
            (lambda d: d.update(schema_version="0.9"), "schema_version"),
            (lambda d: first_cell(d).update(value_kind="number", value=None), "value_kind 'number'"),
            (lambda d: first_cell(d)["source"].update(document="IBC:2018:310"), "source.document"),
            (lambda d: next(x for x in d["documents"] if x["id"] == T504).update(status="unavailable"),
             "marked 'unavailable'"),
            (lambda d: d["documents"].append({"id": "X", "kind": "k", "status": "maybe", "authority": "code_text"}),
             "status 'maybe'"),
            (lambda d: d["documents"].append({"id": "Y", "kind": "k", "status": "unavailable", "authority": "rumour"}),
             "authority 'rumour'"),
            # found by Sonnet review: each of these passed the first validator
            (lambda d: num_cell(d).update(value=140), "disagrees with printed text"),
            (lambda d: num_cell(d).update(value=True), "value_kind 'number'"),
            (lambda d: num_cell(d).update(value=float("nan")), "value_kind 'number'"),
            (lambda d: num_cell(d).update(value=-5, value_text="-5"), "value_kind 'number'"),
            (lambda d: num_cell(d).update(value_kind="unlimited"), "must have value null"),
            (lambda d: first_cell(d).update(value_kind="not_permitted"), "means 'unlimited'"),
            (lambda d: num_cell(d).update(unit="m"), "differs from the table's"),
            (lambda d: first_cell(d).update(conditions=[]), "missing from conditions"),
            (lambda d: swap_keys(d), "are not the keys of its dims"),
            (lambda d: first_cell(d)["printed"]["row_labels"].update(occupancy="Z"), "disagrees with printed label"),
            (lambda d: first_cell(d).update(id=first_cell(d)["id"] + "x"), "does not match its printed labels"),
        ]

        def num_cell(d):
            return next(c for c in self.p(d)["cells"] if c["value_kind"] == "number")

        def swap_keys(d):
            a, b = self.p(d)["cells"][0], self.p(d)["cells"][1]
            a["keys"], b["keys"] = b["keys"], a["keys"]
            for c in (a, b):
                for k in c["keys"]:
                    self.p(d)["index"][k] = c["id"]
        for fn, frag in cases:
            with self.subTest(frag):
                self.assertCaught(fn, frag)


class ResultSafety(Base):
    def test_numeric_limit(self):
        self.assertEqual(self.q(occupancy="R", sprinkler="NS", construction="I-A").numeric_limit, float("inf"))
        self.assertEqual(self.q(occupancy="R", sprinkler="S13D", construction="V-B").numeric_limit, 40.0)
        self.assertIsNone(self.q(occupancy="R-3", sprinkler="S13D", construction="V-B").numeric_limit)
        self.assertEqual(self.q(occupancy="R", sprinkler="NS", construction="I-A").to_dict()["numeric_limit"], "inf")

    def test_found_with_loaded_footnotes_is_complete_and_carries_references(self):
        """Phase 2 flip (was: is_complete False, conditions_text_not_loaded). Footnote h is
        the condition Check 1 depends on; its reference is an unavailable document."""
        r = self.q(occupancy="R", sprinkler="S13D", construction="V-B")
        self.assertTrue(r.found)
        self.assertTrue(r.is_complete)
        h = next(c for c in r.conditions if c["mark"] == "h")
        self.assertEqual(h["source"], {"file": "code/table-504.3-notes.md", "line": 33})
        self.assertEqual(h["references"], [{"ref": "IBC 903.2.8", "document": "IBC:2018:903", "status": "unavailable"}])

    def test_results_do_not_alias_the_store(self):
        r = self.q(occupancy="R", sprinkler="NS", construction="I-A")
        r.conditions[0]["mark"] = "ZZ"
        r.citation["row_labels"]["occupancy"] = "X"
        again = self.q(occupancy="R", sprinkler="NS", construction="I-A")
        self.assertEqual(again.conditions[0]["mark"], "a")
        self.assertEqual(again.citation["row_labels"]["occupancy"], "R")

    def test_odd_calls_never_raise(self):
        self.assertEqual(self.s.lookup(T504, provision_id="x").status, "invalid_input")
        self.assertEqual(self.s.lookup(T504, self="x").status, "invalid_input")
        self.assertEqual(self.s.lookup(["x"]).error_codes(), ["unknown_provision"])
        r = self.q(occupancy=["R"], sprinkler=True, construction="V-B")
        self.assertEqual(r.error_codes(), ["invalid_type", "invalid_type"])


class Provenance(unittest.TestCase):
    def test_load_verifies_against_a_fresh_build(self):
        Store.load(FIXTURES / "store/store.json", manifest=MANIFEST)  # committed store is current

    def test_consistent_edit_passes_validator_but_not_verified_load(self):
        data, _ = build_store(MANIFEST)
        cell = next(c for c in data["provisions"][T504]["cells"] if c["value"] == 40)
        cell["value"], cell["value_text"] = 140, "140"
        self.assertEqual(validate_store(data), [], "shape and consistency alone cannot catch this")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "store.json"
            path.write_text(dumps(data), encoding="utf-8")
            Store.load(path)  # unverified load accepts it
            with self.assertRaises(StoreError):
                Store.load(path, manifest=MANIFEST)

    def test_reserved_characters_in_labels_are_refused(self):
        from services.htmlParser import SPECS, MatrixSpec
        html = "<table><tr><th>K</th><th>V</th></tr><tr><td>A|B</td><td>1</td></tr></table>"
        SPECS["test-reserved"] = MatrixSpec(table_id="T:RES", row_dims=["k"], col_dim="c")
        try:
            with tempfile.TemporaryDirectory() as tmp:
                (Path(tmp) / "t.html").write_text(html, encoding="utf-8")
                (Path(tmp) / "m.json").write_text(json.dumps({"documents": [{
                    "id": "T:RES", "kind": "code_table", "status": "available", "authority": "code_text",
                    "files": [{"path": "t.html", "parse": {"as": "matrix", "spec": "test-reserved"}}]}]}),
                    encoding="utf-8")
                with self.assertRaises(StoreError):
                    build_store(Path(tmp) / "m.json")
        finally:
            del SPECS["test-reserved"]


class BuildErrors(unittest.TestCase):
    def test_spec_and_manifest_ids_must_agree(self):
        man = json.loads(MANIFEST.read_text(encoding="utf-8"))
        man["documents"][0]["id"] = "IBC:2018:T504.3-typo"
        with tempfile.TemporaryDirectory() as tmp:
            m = Path(tmp) / "manifest.json"
            m.write_text(json.dumps(man), encoding="utf-8")
            for f in ("table-504.3.html", "code/table-504.3-notes.md", "code/section-1030-emergency-escape-and-rescue.md",
                      "code-analysis.html", "window-schedule.html"):
                (Path(tmp) / f).parent.mkdir(parents=True, exist_ok=True)
                (Path(tmp) / f).write_bytes((FIXTURES / f).read_bytes())
            with self.assertRaises(StoreError):
                build_store(m)

    def test_slug_is_windows_safe(self):
        self.assertEqual(store_mod.slug("IBC:2018:T504.3"), "IBC-2018-T504.3")


if __name__ == "__main__":
    unittest.main()

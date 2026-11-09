"""Data-driven structure scenarios: tests/fixtures/scenarios/scenarios.json (catalogue in README.md).

- status "pass": the scenario must pass.
- status "known_gap": the scenario must FAIL, and the failure message must contain its
  gap_signature. Anything else fails the run: a gap that now passes (update its status)
  or a gap that fails for a different reason (typo, broken fixture, new bug).
  Verified known gaps are reported as skipped, with the gap text as the reason.
- Unknown expect keys, duplicate ids and missing files fail the manifest test, so a typo
  can't silently turn a check off.
"""
import json
import re
import unittest

from _setup import FIXTURES
from services.htmlParser import SPECS, KeyValueSheet, MatrixSpec, MatrixTable, RecordTable, parse_tables
from services.htmlParser.specs import construction_type_key

SCEN = FIXTURES / "scenarios"
MANIFEST = json.loads((SCEN / "scenarios.json").read_text(encoding="utf-8"))
SHARED = MANIFEST["shared"]
BY_ID = {sc["id"]: sc for sc in MANIFEST["scenarios"]}
COLUMN_KEYS = {"construction_type": construction_type_key}

TRANSFORMS = {
    "strip_bold": lambda h: re.sub(r'\s*class="bold"', "", h),
    "th_to_td": lambda h: re.sub(r"<(/?)th\b", r"<\1td", h),
    "strip_thead": lambda h: re.sub(r"</?(thead|tbody|tfoot)\b[^>]*>", "", h),
}

EXPECT_KEYS = {
    "common": {"tables_count", "header_rows", "separator_rows", "data_row_count", "title_contains", "caption",
               "warnings_empty", "warnings_contain", "repeated_header_rows", "review_items_contain",
               "review_items_empty"},
    "matrix": {"column_keys", "cell_count", "index_size", "lookups", "absent_lookups", "bad_lookup_dims", "same_index_as"},
    "records": {"column_labels", "no_column", "records", "override_header_rows"},
    "kv": {"title", "entry_count", "entries", "mode"},
}
LOOKUP_KEYS = {"dims", "value", "kind", "footnotes", "inherited", "qualifier"}
CELL_CHECK_KEYS = {"text", "raw", "missing", "join_candidates_contains"}


def _ref(v):
    return SHARED[v[1:]] if isinstance(v, str) and v.startswith("$") else v


def _html(sc):
    if "html" in sc:
        return (SCEN / sc["html"]).read_text(encoding="utf-8")
    text = (SCEN / sc["source"]).read_text(encoding="utf-8")
    for t in sc.get("transforms", []):
        text = TRANSFORMS[t](text)
    return text


def _spec(raw):
    raw = _ref(raw)
    if isinstance(raw, str):
        return SPECS[raw]
    kw = dict(raw)
    if "multi_value_dims" in kw:
        kw["multi_value_dims"] = set(kw["multi_value_dims"])
    if "column_key" in kw:
        kw["column_key"] = COLUMN_KEYS[kw["column_key"]]
    return MatrixSpec(**kw)  # an unsupported spec feature raises TypeError naming it


def _build(sc):
    grids = parse_tables(_html(sc))
    grid = grids[sc.get("table_index", 0)]
    obj = {"matrix": lambda: MatrixTable(grid, _spec(sc["spec"])),
           "records": lambda: RecordTable(grid),
           "kv": lambda: KeyValueSheet(grid)}[sc["kind"]]()
    return grids, grid, obj


def _index_values(m):
    return {k: (m.cells[i]["value"], m.cells[i]["value_kind"]) for k, i in m.index.items()}


class ScenarioChecks(unittest.TestCase):
    def check(self, sc):
        exp = sc["expect"]
        grids, grid, obj = _build(sc)
        lay = obj.layout
        if "tables_count" in exp:
            self.assertEqual(len(grids), exp["tables_count"], "tables_count")
        if "header_rows" in exp:
            self.assertEqual(lay.header_rows, exp["header_rows"], "header_rows")
        if "separator_rows" in exp:
            self.assertEqual(lay.separator_rows, exp["separator_rows"], "separator_rows")
        if "data_row_count" in exp:
            self.assertEqual(len(lay.data_rows), exp["data_row_count"], "data_row_count")
        if "repeated_header_rows" in exp:
            self.assertEqual(lay.repeated_header_rows, exp["repeated_header_rows"], "repeated_header_rows")
        if "caption" in exp:
            self.assertEqual(getattr(grid, "caption", None), exp["caption"], "caption")
        if "title_contains" in exp:
            title = " ".join(grid.slot(r, 0).text for r in lay.title_rows)
            self.assertIn(exp["title_contains"], title, "title_contains")

        {"matrix": self._check_matrix, "records": self._check_records, "kv": self._check_kv}[sc["kind"]](obj, exp, grid)

        # warnings last, so the substantive checks above always run first
        for frag in exp.get("warnings_contain", []):
            self.assertTrue(any(frag in w for w in obj.warnings), f"warnings_contain {frag!r}: {obj.warnings}")
        if exp.get("warnings_empty"):
            self.assertEqual(obj.warnings, [], "warnings_empty")
        for frag in exp.get("review_items_contain", []):
            self.assertTrue(any(frag in w["code"] or frag in w["message"] for w in obj.review_items),
                            f"review_items_contain {frag!r}: {obj.review_items}")
        if exp.get("review_items_empty"):
            self.assertEqual(obj.review_items, [], "review_items_empty")

    # ------------------------------------------------------------- matrix
    def _check_matrix(self, m, exp, grid):
        if "column_keys" in exp:
            self.assertEqual(m.column_keys, exp["column_keys"], "column_keys")
        if "cell_count" in exp:
            self.assertEqual(len(m.cells), exp["cell_count"], "cell_count")
        if "index_size" in exp:
            self.assertEqual(len(m.index), exp["index_size"], "index_size")
        if "same_index_as" in exp:
            _, _, other = _build(BY_ID[exp["same_index_as"]])
            self.assertEqual(_index_values(m), _index_values(other), f"same_index_as {exp['same_index_as']}")
        for lk in _ref(exp.get("lookups", [])):
            dims = lk["dims"]
            rec = m.lookup(**dims)
            self.assertIsNotNone(rec, f"no cell for {dims}")
            if lk.get("value") == "UL":
                self.assertEqual(rec["value_kind"], "unlimited", f"kind for {dims}")
            elif "value" in lk:
                self.assertEqual(rec["value"], lk["value"], f"value for {dims}")
            if "kind" in lk:
                self.assertEqual(rec["value_kind"], lk["kind"], f"kind for {dims}")
            if "footnotes" in lk:
                self.assertEqual(sorted(rec["footnotes"]), sorted(lk["footnotes"]), f"footnotes for {dims}")
            if "inherited" in lk:
                self.assertEqual(rec["src"]["value"]["inherited"], lk["inherited"], f"inherited for {dims}")
            if "qualifier" in lk:
                self.assertEqual(rec.get("qualifier"), lk["qualifier"], f"qualifier for {dims}")
        for dims in exp.get("absent_lookups", []):
            self.assertIsNone(m.lookup(**dims), f"expected no cell for {dims}")
        for dims in exp.get("bad_lookup_dims", []):
            with self.assertRaises(KeyError, msg=f"lookup({dims}) should reject the dimension set"):
                m.lookup(**dims)

    # ------------------------------------------------------------ records
    def _col(self, t, label):
        ids = t.column(label)
        self.assertEqual(len(ids), 1, f"column {label!r} -> {ids}")
        return ids[0]

    def _check_records(self, t, exp, grid):
        if "column_labels" in exp:
            self.assertEqual([c.label for c in t.layout.columns], exp["column_labels"], "column_labels")
        for label in exp.get("no_column", []):
            self.assertEqual(t.column(label), [], f"unexpected column {label!r}")
        for want in exp.get("records", []):
            (klabel, kval), = want["key"].items()
            kid = self._col(t, klabel)
            rows = [r for r in t.rows if r["cells"][kid]["text"] == kval]
            self.assertEqual(len(rows), 1, f"rows with {klabel}={kval!r}")
            for label, checks in want["cells"].items():
                cell = rows[0]["cells"][self._col(t, label)]
                where = f"{klabel}={kval} / {label}"
                if "text" in checks:
                    self.assertEqual(cell["text"], checks["text"], f"text at {where}")
                if "raw" in checks:
                    self.assertEqual(cell["raw"], checks["raw"], f"raw at {where}")
                if "missing" in checks:
                    self.assertEqual(cell.get("missing", False), checks["missing"], f"missing at {where}")
                if "join_candidates_contains" in checks:
                    self.assertIn(checks["join_candidates_contains"], cell.get("join_candidates", []),
                                  f"join_candidates at {where}")
        if "override_header_rows" in exp:
            ov = exp["override_header_rows"]
            t2 = RecordTable(grid, header_rows=ov["header_rows"])
            self.assertEqual([c.label for c in t2.layout.columns], ov["column_labels"], "override column_labels")
            self.assertEqual(len(t2.layout.data_rows), ov["data_row_count"], "override data_row_count")

    # ----------------------------------------------------------------- kv
    def _check_kv(self, kv, exp, grid):
        if "mode" in exp:
            self.assertEqual(kv.mode, exp["mode"], "mode")
        if "title" in exp:
            self.assertEqual(kv.title, exp["title"], "title")
        if "entry_count" in exp:
            self.assertEqual(len(kv.entries), exp["entry_count"], "entry_count")
        got = {e["label"]["text"]: e["value"]["text"] for e in kv.entries}
        for label, value in exp.get("entries", {}).items():
            self.assertEqual(got.get(label), value, f"entry {label}")


class ManifestTest(unittest.TestCase):
    def test_manifest_is_well_formed(self):
        ids = [sc["id"] for sc in MANIFEST["scenarios"]]
        self.assertEqual(len(ids), len(set(ids)), "duplicate scenario ids")
        for sc in MANIFEST["scenarios"]:
            with self.subTest(sc["id"]):
                self.assertIn(sc["status"], ("pass", "known_gap"))
                self.assertIn(sc["kind"], ("matrix", "records", "kv"))
                for field in ("title", "why", "expect"):
                    self.assertTrue(sc.get(field), f"missing {field}")
                if sc["status"] == "known_gap":
                    self.assertTrue(sc.get("gap") and sc.get("gap_signature"), "known_gap needs gap + gap_signature")
                else:
                    self.assertNotIn("gap_signature", sc)
                self.assertTrue(("html" in sc) != ("source" in sc), "exactly one of html/source")
                path = SCEN / (sc.get("html") or sc["source"])
                self.assertTrue(path.exists(), f"missing file {path.name}")
                for t in sc.get("transforms", []):
                    self.assertIn(t, TRANSFORMS)
                _html(sc)  # loads + transforms without error
                allowed = EXPECT_KEYS["common"] | EXPECT_KEYS[sc["kind"]]
                unknown = set(sc["expect"]) - allowed
                self.assertFalse(unknown, f"unknown expect keys {unknown}")
                for lk in _ref(sc["expect"].get("lookups", [])):
                    self.assertFalse(set(lk) - LOOKUP_KEYS, f"unknown lookup keys {set(lk) - LOOKUP_KEYS}")
                for rec in sc["expect"].get("records", []):
                    for checks in rec["cells"].values():
                        self.assertFalse(set(checks) - CELL_CHECK_KEYS, f"unknown cell checks {set(checks) - CELL_CHECK_KEYS}")
                ref = sc["expect"].get("same_index_as")
                if ref:
                    self.assertEqual(BY_ID[ref]["status"], "pass", "same_index_as must point at a passing scenario")
        for f in SCEN.glob("*.html"):
            self.assertIn(f.name, {sc.get("html") for sc in MANIFEST["scenarios"]}, f"{f.name} not in manifest")


def _make(sc):
    if sc["status"] == "pass":
        def test(self):
            self.check(sc)
    else:
        def test(self):
            try:
                self.check(sc)
            except Exception as e:  # noqa: BLE001 - verified against the signature below
                msg = f"{type(e).__name__}: {e}"
                if sc["gap_signature"] not in msg:
                    self.fail(f"{sc['id']} is a known gap but failed for a different reason "
                              f"(expected {sc['gap_signature']!r}):\n{msg}")
                self.skipTest(f"known gap: {sc['gap']}")
            self.fail(f"{sc['id']} is marked known_gap but now passes - set its status to 'pass'")
    test.__doc__ = f"{sc['id']}: {sc['title']}"
    return test


class ScenarioTest(ScenarioChecks):
    pass


for _sc in MANIFEST["scenarios"]:
    setattr(ScenarioTest, f"test_{_sc['id']}", _make(_sc))


if __name__ == "__main__":
    unittest.main()

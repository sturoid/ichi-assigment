"""Every cited constant's quote is on its line, word for word; the limits match the
numbers hand-typed from the code text; tampering is caught."""
import tempfile
import unittest
from pathlib import Path

from _setup import FIXTURES, REPO

from services.planCheck import citations as c


class Quotes(unittest.TestCase):
    def test_code_quotes_on_their_lines(self):
        self.assertEqual(c.verify_quotes(FIXTURES), [])

    def test_brief_quotes_on_their_lines(self):
        self.assertEqual(c.verify_quotes(REPO, c.BRIEF_CITES), [])

    def test_only_code_text_in_code_cites(self):
        self.assertTrue(all(x.authority == "code_text" for x in c.CODE_CITES))
        self.assertTrue(all(x.authority == "challenge_brief" for x in c.BRIEF_CITES))

    def test_limits_hand_typed(self):
        # hand-typed from section-1030 lines 35, 37, 41, 45
        self.assertEqual((c.MIN_AREA.value, c.MIN_AREA.cite.line), (5.7, 35))
        self.assertEqual((c.MIN_AREA_GRADE.value, c.MIN_AREA_GRADE.cite.line), (5.0, 37))
        self.assertEqual((c.MIN_CLEAR_HEIGHT.value, c.MIN_CLEAR_WIDTH.value), (24, 20))
        self.assertEqual((c.MAX_SILL.value, c.MAX_SILL.comparison, c.MAX_SILL.cite.line), (44, "<=", 45))
        self.assertEqual(c.OPERABLE.line, 31)

    def test_tampered_file_is_caught(self):
        with tempfile.TemporaryDirectory() as d:
            src = (FIXTURES / c.S1030_FILE).read_text(encoding="utf-8")
            (Path(d) / "code").mkdir()
            (Path(d) / c.S1030_FILE).write_text(src.replace("5.7 square feet", "5.0 square feet"), encoding="utf-8")
            (Path(d) / c.NOTES_504_FILE).write_text((FIXTURES / c.NOTES_504_FILE).read_text(encoding="utf-8"),
                                                    encoding="utf-8")
            problems = c.verify_quotes(Path(d))
            self.assertEqual(len(problems), 1)
            self.assertIn("1030.2", problems[0])


if __name__ == "__main__":
    unittest.main()

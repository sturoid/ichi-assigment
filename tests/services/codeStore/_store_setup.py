"""Shared test setup: put <repo>/src on sys.path and expose fixture paths."""
import pathlib
import sys

TESTS_DIR = pathlib.Path(__file__).resolve().parents[2]
REPO = TESTS_DIR.parent
FIXTURES = TESTS_DIR / "fixtures"
MANIFEST = FIXTURES / "manifest.json"
EXPECTED = FIXTURES / "expected"

if str(REPO / "src") not in sys.path:
    sys.path.insert(0, str(REPO / "src"))

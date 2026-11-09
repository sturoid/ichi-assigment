"""Cited constants: every code requirement and every brief rule the checks use.

Code requirements are the same for every project on IBC 2018, so they live here as
plain constants, not as values extracted from prose. Each carries the file, the line
and a word-for-word quote. ``verify_quotes`` re-reads the files and refuses to run if a
quote is not on its line, so an edited or different code file cannot pass silently.

Only ``code_text`` can be cited as code. Rules from the challenge brief are cited as
``challenge_brief`` and are reported as interpretations.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

S1030_FILE = "code/section-1030-emergency-escape-and-rescue.md"
NOTES_504_FILE = "code/table-504.3-notes.md"
BRIEF_FILE = "instructions/README.md"  # challenge brief; verified by the test suite, not at run time


@dataclass(frozen=True)
class Cite:
    id: str
    label: str          # how the report names it, e.g. "IBC 1030.2"
    document: str       # manifest id
    file: str           # relative to the manifest (brief: relative to the repo)
    line: int
    quote: str          # appears word for word on that line
    authority: str = "code_text"

    def ref(self) -> str:
        return f"{self.label} ({self.file} line {self.line})"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class Limit:
    id: str
    value: float
    unit: str
    comparison: str     # ">=" (minimum) or "<=" (maximum)
    cite: Cite


def _c(id_, label, line, quote, document="IBC:2018:1030", file=S1030_FILE, authority="code_text"):
    return Cite(id_, label, document, file, line, quote, authority)


# --- IBC 1030 --------------------------------------------------------------- #
SCOPE_OCCUPANCIES = _c("1030.1.occupancies", "IBC 1030.1 item 2", 11, "Group R-3 and R-4 occupancies.")
SCOPE_R2 = _c("1030.1.r2", "IBC 1030.1 item 1", 9,
              "Group R-2 occupancies located in stories with only one exit or access to only one exit")
SCOPE_SLEEPING = _c("1030.1.sleeping", "IBC 1030.1", 13,
                    "sleeping rooms below the fourth story above grade plane shall have not fewer than one "
                    "exterior emergency escape and rescue opening")
PUBLIC_WAY = _c("1030.1.public_way", "IBC 1030.1", 13,
                "Such openings shall open directly into a public way or to a yard or court that opens to a public way.")
EXCEPTION_2 = _c("1030.1.exc2", "IBC 1030.1 Exception 2", 19,
                 "Emergency escape and rescue openings are not required from basements or sleeping rooms that have "
                 "an exit door or exit access door that opens directly into a public way")
OPERABLE = _c("1030.1.1", "IBC 1030.1.1", 31,
              "Emergency escape and rescue openings shall be operational from inside the room without the use of "
              "keys or tools.")
MIN_AREA_CITE = _c("1030.2", "IBC 1030.2", 35, "minimum net clear opening of 5.7 square feet")
MIN_AREA_GRADE_CITE = _c("1030.2.exc", "IBC 1030.2 Exception", 37,
                         "The minimum net clear opening for grade-floor emergency escape and rescue openings shall "
                         "be 5 square feet")
MIN_HEIGHT_CITE = _c("1030.2.1.h", "IBC 1030.2.1", 41, "The minimum net clear opening height dimension shall be 24 inches")
MIN_WIDTH_CITE = _c("1030.2.1.w", "IBC 1030.2.1", 41, "The minimum net clear opening width dimension shall be 20 inches")
NORMAL_OPERATION = _c("1030.2.1.op", "IBC 1030.2.1", 41,
                      "The net clear opening dimensions shall be the result of normal operation of the opening.")
MAX_SILL_CITE = _c("1030.3", "IBC 1030.3", 45,
                   "the bottom of the clear opening not greater than 44 inches (1118 mm) measured from the floor")
SCREENS = _c("1030.5", "IBC 1030.5", 49,
             "such devices shall be releasable or removable from the inside without the use of a key, tool or force")
GRADE_FLOOR_DEF = _c("202.grade_floor_opening", "IBC 202 GRADE FLOOR OPENING", 55,
                     "the sill height of the opening is not more than 44 inches (1118 mm) above or below the finished "
                     "ground level adjacent to the opening")
HEIGHT_DEF = _c("202.height_building", "IBC 202 HEIGHT, BUILDING", 59,
                "The vertical distance from grade plane to the average height of the highest roof surface.")

MIN_AREA = Limit("net_area_min", 5.7, "sq ft", ">=", MIN_AREA_CITE)
MIN_AREA_GRADE = Limit("net_area_min_grade_floor", 5.0, "sq ft", ">=", MIN_AREA_GRADE_CITE)
MIN_CLEAR_HEIGHT = Limit("clear_height_min", 24, "in", ">=", MIN_HEIGHT_CITE)
MIN_CLEAR_WIDTH = Limit("clear_width_min", 20, "in", ">=", MIN_WIDTH_CITE)
MAX_SILL = Limit("sill_max", 44, "in", "<=", MAX_SILL_CITE)

# --- Table 504.3 text ----------------------------------------------------- #
T504_SECTION = _c("504.3", "IBC 504.3", 7,
                  "The maximum height, in feet, of a building shall not exceed the limits specified in Table 504.3.",
                  document="IBC:2018:T504.3", file=NOTES_504_FILE)
T504_LEGEND = _c("504.3.legend", "Table 504.3 legend", 15,
                 "S13D = Buildings equipped throughout with an automatic sprinkler system installed in accordance "
                 "with Section 903.3.1.3", document="IBC:2018:T504.3", file=NOTES_504_FILE)
T504_LEGEND_NS = _c("504.3.legend.ns", "Table 504.3 legend", 15,
                    "NS = Buildings not equipped throughout with an automatic sprinkler system",
                    document="IBC:2018:T504.3", file=NOTES_504_FILE)
T504_LEGEND_S = _c("504.3.legend.s", "Table 504.3 legend", 15,
                   "S = Buildings equipped throughout with an automatic sprinkler system installed in accordance with "
                   "Section 903.3.1.1", document="IBC:2018:T504.3", file=NOTES_504_FILE)
T504_LEGEND_S13R = _c("504.3.legend.s13r", "Table 504.3 legend", 15,
                      "S13R = Buildings equipped throughout with an automatic sprinkler system installed in accordance "
                      "with Section 903.3.1.2", document="IBC:2018:T504.3", file=NOTES_504_FILE)
SHORTHAND_13 = _c("504.3.shorthand.13", "Table 504.3 notes, sprinkler shorthand", 37,
                  "Section 903.3.1.1 is an NFPA 13 system.", document="IBC:2018:T504.3", file=NOTES_504_FILE)
SHORTHAND_13R = _c("504.3.shorthand.13r", "Table 504.3 notes, sprinkler shorthand", 38,
                   "Section 903.3.1.2 is an NFPA 13R system.", document="IBC:2018:T504.3", file=NOTES_504_FILE)
SHORTHAND_13D = _c("504.3.shorthand.13d", "Table 504.3 notes, sprinkler shorthand", 39,
                   "Section 903.3.1.3 is an NFPA 13D system.", document="IBC:2018:T504.3", file=NOTES_504_FILE)

# --- Challenge brief (interpretations; never cited as code) -------------------- #
def _b(id_, line, quote):
    return Cite(id_, "Challenge brief", "BRIEF", BRIEF_FILE, line, quote, "challenge_brief")


BRIEF_NUMBERED_GROUP = _b("brief.numbered_group", 54,
                          "A numbered group like `R-3` goes in the Table 504.3 row for its letter, `R`, unless the "
                          "table gives the numbered group its own row")
BRIEF_SLEEPING_ROOM = _b("brief.sleeping_room", 60,
                         "Anything named as a bedroom (`BEDROOM`, `BED`, `BDRM`, `GUEST BED` and so on) counts.")
BRIEF_AMBIGUOUS_ROOM = _b("brief.ambiguous_room", 60, "People do sometimes sleep in dens, offices and lofts")
BRIEF_NOMINAL = _b("brief.nominal", 63, "It's always smaller than the nominal size")
BRIEF_HEAD_HEIGHT = _b("brief.head_height", 64, "Height from the floor to the top of the window.")
BRIEF_TYPE_COLUMNS = _b("brief.type_columns", 52, "In the fixture schedule it's the second of the two `TYPE` columns.")
BRIEF_OPERATION = _b("brief.operation", 66, "A single hung slides up, so only the bottom half opens.")

CODE_CITES = [v for v in list(globals().values()) if isinstance(v, Cite) and v.authority == "code_text"]
BRIEF_CITES = [v for v in list(globals().values()) if isinstance(v, Cite) and v.authority == "challenge_brief"]


def verify_quotes(base: Path, cites: list[Cite] | None = None) -> list[str]:
    """Problems with cited quotes: each quote must appear on its line. Empty means all good."""
    problems = []
    cache: dict[str, list[str]] = {}
    for c in cites if cites is not None else CODE_CITES:
        path = Path(base) / c.file
        if c.file not in cache:
            if not path.is_file():
                problems.append(f"{c.id}: file {c.file} not found")
                cache[c.file] = []
                continue
            cache[c.file] = path.read_text(encoding="utf-8").splitlines()
        lines = cache[c.file]
        if not lines:
            continue
        if not (1 <= c.line <= len(lines)) or c.quote not in lines[c.line - 1]:
            problems.append(f"{c.id}: quote not found on {c.file} line {c.line}: {c.quote!r}")
    return problems

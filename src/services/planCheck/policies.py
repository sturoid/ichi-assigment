"""Named policy rules: every judgement call the checks make, in one place.

A check never decides case by case. When the code text alone does not settle how a
schedule value may be used, one of these rules does, and the finding names it. Each
rule has an id, a statement, what it rests on (code text, the brief, or a recorded
project decision) and a test in tests/services/planCheck/test_policies.py. Nothing
here mentions a particular window or room.

Anything no rule covers becomes Could Not Evaluate with "needs a policy decision".
"""
from __future__ import annotations

from dataclasses import dataclass

from . import citations as C


@dataclass(frozen=True)
class Policy:
    id: str
    title: str
    rule: str
    rests_on: tuple[str, ...]      # citation refs or decision records
    authority: str                 # code_text | challenge_brief | project_decision

    def to_dict(self) -> dict:
        return {"id": self.id, "title": self.title, "rule": self.rule, "rests_on": list(self.rests_on),
                "authority": self.authority}


_DECISIONS = "src/NOTES.md, Plan from here: open decisions"

POLICIES: dict[str, Policy] = {p.id: p for p in [
    # --- general -----------------------------------------------------------------
    Policy("POL-GEN-AMENDMENTS", "Local amendments not provided",
           "The project is reviewed against the 2018 IBC as printed. If the manifest lists local amendments as not "
           "provided, every "
           "verdict is conditional on them and the report says so once, at the top.",
           ("the local-amendments document listed in the manifest (unavailable)",), "project_decision"),
    Policy("POL-GEN-OCR", "OCR-repaired values never decide a verdict alone",
           "A value the reader had to repair (a letter read as a digit, a word one character off) is shown with the "
           "repair. If a Pass or Fail would rest on it, the line is Could Not Evaluate until the sheet is checked.",
           ("src/NOTES.md decision: keep raw OCR text; record repairs, never fix silently",), "project_decision"),
    Policy("POL-GEN-UNCOVERED", "No rule, no verdict",
           "A situation no policy covers is Could Not Evaluate with 'needs a policy decision'.",
           ("src/NOTES.md decision: judgement calls are named policy rules",), "project_decision"),
    Policy("POL-GEN-SCHEDULE-GAPS", "Gaps in a numbered schedule are reported",
           "When every window mark is a whole number, numbers missing between the lowest and highest are listed for "
           "the plan checker: rows may have been lost in scanning, or windows renumbered. No verdict changes.",
           ("src/NOTES.md decision: report review rounds, 2026-11-08",), "project_decision"),
    # --- Check 1: height ---------------------------------------------------------
    Policy("POL-H-INTERPRETATION", "Brief rules may support a verdict, disclosed",
           "A mapping that rests on the challenge brief rather than code text (R-3 read as row R, because IBC 310 is "
           "not provided) may support a Pass or Fail, but the finding names it as an interpretation. The limit "
           "value itself always comes from code text.",
           (C.BRIEF_NUMBERED_GROUP.ref(),), "challenge_brief"),
    Policy("POL-H-FOOTNOTES", "Footnotes are cited; pointed-to documents are listed, not assumed",
           "Every footnote on the looked-up cell is quoted in the finding. Where a footnote points to a document we "
           "don't have (Chapters 4 and 5 exceptions, IBC 903.2.8), the finding lists it as not provided. It does "
           "not block the verdict: an exception has to be claimed by the applicant, and the finding says which "
           "claims the code analysis makes.",
           ("Table 504.3 footnotes (code/table-504.3-notes.md lines 19-33)",), "project_decision"),
    Policy("POL-H-NS-NEW", "NS limits are for existing buildings",
           "If the building resolves to the NS sub-row and the code analysis describes new work, the NS limit is not "
           "a basis for a verdict (footnote d): Could Not Evaluate, with the sprinkler status to be confirmed.",
           ("Table 504.3 footnote d (code/table-504.3-notes.md line 25)",), "code_text"),
    Policy("POL-H-STATED-HEIGHT", "The stated height is used as submitted",
           "The building height is the architect's figure. The tool compares it with the table; it cannot check the "
           "measurement (grade plane and roof heights are on sheets not provided), and says so.",
           (C.HEIGHT_DEF.ref(),), "project_decision"),
    Policy("POL-H-ARCHITECT", "The architect's allowable height is checked, not trusted",
           "If the code analysis states an allowable height that differs from the looked-up cell, the finding flags "
           "it and lists the cells in the same row and column that hold the architect's figure, as a likely "
           "explanation. The verdict uses the looked-up cell.",
           ("brief: the allowable height 'is worth checking against the table rather than trusting'",), "challenge_brief"),
    Policy("POL-H-SPRINKLER-COVERAGE", "Sprinkler coverage must be 'throughout'",
           "S, S13R and S13D are for buildings 'equipped throughout'. Wording that says partial coverage resolves to "
           "no sub-row (Could Not Evaluate). Wording that names a standard but not 'throughout' is resolved and "
           "flagged.",
           (C.T504_LEGEND.ref(),), "code_text"),
    # --- Check 2: scope ----------------------------------------------------------
    Policy("POL-E-SCOPE", "Which buildings and floors 1030 covers",
           "R-3 and R-4: applies. R-2: Could Not Evaluate unless the exits per story are known. Other groups: Not "
           "Applicable. Sleeping rooms must be below the fourth story above grade plane; the story comes from the "
           "code analysis room numbering (floor n read as story n above grade plane), else from the number of "
           "stories. Unknown story: Could Not Evaluate.",
           (C.SCOPE_OCCUPANCIES.ref(), C.SCOPE_R2.ref(), C.SCOPE_SLEEPING.ref()), "code_text"),
    Policy("POL-E-SLEEPING", "What counts as a sleeping room",
           "Room names with a bedroom word (BEDROOM, BED, BDRM, GUEST BED ...) are sleeping rooms, including a word "
           "one character from BEDROOM (OCR), which is flagged. Dens, offices, lofts and unrecognised names are "
           "ambiguous: not treated as sleeping rooms, but listed for the plan checker to confirm.",
           (C.BRIEF_SLEEPING_ROOM.ref(), C.BRIEF_AMBIGUOUS_ROOM.ref()), "challenge_brief"),
    Policy("POL-E-ROOM-KEY", "Room identity",
           "Windows belong to the same room when their location has the same room number ('BEDROM 12' and "
           "'BEDROOM 12'); without a number, when the names match. Different spellings under one number are flagged.",
           ("window schedule LOCATION column",), "project_decision"),
    Policy("POL-E-NOT-SLEEPING", "Windows outside sleeping rooms",
           "Windows in rooms that are not sleeping rooms are Not Applicable. A window in such a room that is marked "
           "egress is noted.",
           (C.SCOPE_SLEEPING.ref(),), "code_text"),
    Policy("POL-E-NOT-DESIGNATED", "Sleeping-room windows not marked egress",
           "Not Applicable as a window finding: 1030 needs one complying opening per sleeping room, not every "
           "window. They are still considered in the room finding.",
           (C.SCOPE_SLEEPING.ref(),), "code_text"),
    # --- Check 2: what nominal size can prove -------------------------------------
    Policy("POL-E-NOMINAL-UPPER", "Nominal size is an upper bound",
           "The net clear opening (area, width and height) is always smaller than the nominal size. A nominal value "
           "at or below a minimum proves a Fail; a nominal value above it proves nothing.",
           (C.BRIEF_NOMINAL.ref(), C.MIN_AREA_CITE.ref(), C.MIN_HEIGHT_CITE.ref()), "challenge_brief"),
    Policy("POL-E-NO-FRAME-ASSUMPTION", "No frame-deduction assumption (decision 2)",
           "The tool assumes no frame size, so nominal size never proves a Pass. Without a net clear opening (from "
           "the schedule or manufacturer data) a minimum is Could Not Evaluate, with the nominal upper bound shown.",
           (f"{_DECISIONS} #2",), "project_decision"),
    Policy("POL-E-SILL-LOWER", "A derived sill is a lower bound",
           "Sill = head height - nominal height (head height is floor to top of window). The bottom of the clear "
           "opening is at or above that frame sill. A frame sill above 44 in proves a Fail; at or below 44 in it "
           "proves nothing, because the bottom frame depth is unknown. A scheduled sill height is treated the same "
           "way unless the column says it is to the clear opening.",
           (C.MAX_SILL_CITE.ref(), C.BRIEF_HEAD_HEIGHT.ref()), "code_text"),
    Policy("POL-E-GRADE-FLOOR", "Grade-floor limit (decision 4)",
           "Whether an opening is a grade-floor opening needs the finished ground level, which these sheets don't "
           "give. The area is decided only when the 5.0 and 5.7 sq ft limits give the same result.",
           (C.MIN_AREA_GRADE_CITE.ref(), C.GRADE_FLOOR_DEF.ref(), f"{_DECISIONS} #4"), "code_text"),
    Policy("POL-E-FIXED", "A fixed window is not an escape opening",
           "A window scheduled as fixed does not open, so it can't be operated from inside and has no net clear "
           "opening by normal operation: Fail.",
           (C.OPERABLE.ref(), C.NORMAL_OPERATION.ref()), "code_text"),
    Policy("POL-E-PARTIAL-OPENING", "Single hung and slider bounds are notes only (decision 5)",
           "A single hung opens only its bottom sash and a slider about half its width. The tool shows the "
           "half-size figure as a labelled note, never as proof of a Fail, because panel splits vary (a three-panel "
           "slider opens two thirds; sashes can be unequal).",
           (C.BRIEF_OPERATION.ref(), f"{_DECISIONS} #5"), "challenge_brief"),
    Policy("POL-E-AT-LIMIT", "A bound sitting exactly at a limit is flagged as a likely Fail",
           "A frame sill exactly at the 44 in maximum, or a partial-opening note (bottom sash, half a slider) at or "
           "below a minimum, cannot prove a Fail from the schedule, so the verdict stays Could Not Evaluate. The "
           "window is flagged 'expect a Fail' and listed first among the items to check, because any frame "
           "deduction tips it over.",
           (C.MAX_SILL_CITE.ref(), C.MIN_HEIGHT_CITE.ref(), "src/NOTES.md decision: report review rounds, 2026-11-08"),
           "project_decision"),
    Policy("POL-E-OPERATION-UNKNOWN", "Unrecognised window type",
           "If the operation isn't recognised, whether and how the window opens is Could Not Evaluate.",
           (C.OPERABLE.ref(),), "code_text"),
    Policy("POL-E-UNSEEN", "Requirements no schedule shows",
           "Operation without keys or tools, releasable screens and opening onto a public way, yard or court are "
           "each a Could Not Evaluate line on every egress window, naming the document that would settle it. They "
           "never cause a Fail; they do keep a window from a Pass.",
           (C.OPERABLE.ref(), C.SCREENS.ref(), C.PUBLIC_WAY.ref()), "code_text"),
    # --- Check 2: rooms -------------------------------------------------------------
    Policy("POL-E-ROOM-ROLLUP", "Room verdict (decision 3)",
           "A sleeping room Passes if a designated egress window Passes, and is Could Not Evaluate if one is Could "
           "Not Evaluate. If none is designated, or every designated one Fails, the room's other windows are "
           "evaluated as candidates: if any could comply the room is Could Not Evaluate, flagged 'no complying "
           "opening designated'; if none could, the room Fails.",
           (C.SCOPE_SLEEPING.ref(), f"{_DECISIONS} #3"), "project_decision"),
    Policy("POL-E-EXCEPTION-2", "Exit-door exception is not assumed",
           "A room Fail says 'unless Exception 2 applies (an exit door to a public way)'. The floor plans would "
           "settle it; the tool does not assume a door it can't see.",
           (C.EXCEPTION_2.ref(),), "code_text"),
    Policy("POL-E-NO-EGRESS-COLUMN", "Schedule without an egress column",
           "If the schedule has no egress column, no window is designated. Every sleeping room is then decided by "
           "POL-E-ROOM-ROLLUP from its windows as candidates, and the missing column is reported.",
           (C.SCOPE_SLEEPING.ref(),), "project_decision"),
]}


def policy(pid: str) -> Policy:
    return POLICIES[pid]

# Plan check report: building height and emergency escape openings

**Project:** NEW 3-STORY SINGLE-FAMILY DWELLING WITH ATTACHED ACCESSORY DWELLING UNIT (ADU). SLEEPING ROOMS ON ALL FLOORS

Checked against IBC 2018 Table 504.3 (allowable building height) and Section 1030 (emergency escape and rescue openings), as printed. City of Meridian Falls amendments to the 2018 IBC were not provided, so every verdict is subject to them.

**Result: 6 Fail, 8 Could Not Evaluate, 0 Pass, 10 Not Applicable.**
The 6 Fails are 4 correction items (§1): a room and its failing window are one problem.
Confidence in the 4 corrections: 1 High, 2 Medium, 1 Low. §1 says what to confirm before sending any that is not High.
Nothing passes because a window schedule gives nominal sizes, which include the frame, and the code regulates the net clear opening, which is always smaller. A nominal size can prove a Fail, never a Pass.

## 1. Corrections

Raw material for the correction letter: the problem, the arithmetic and the deciding code section. Each ID points to its evidence: H-1 in §4, rooms (R-) in §5, windows (W-) in §6 or §7.

**Confidence** says how likely a correction is to stand once the full drawing set is seen. **High:** send it as written. **Medium:** one thing could overturn it; confirm that first, or send the correction with that condition stated. **Low:** more than one thing could overturn it; confirm them before sending, and if they can't be confirmed, send it as a request for information instead of a correction. A wrong correction costs the applicant a redesign.

1. **Building height exceeds Table 504.3** (H-1)
   - 41'-6" exceeds the 40 ft allowed by Table 504.3, row `R` / `S13D`, column `V-B` by 1'-6".
   - Also revise the code analysis: it states an allowable height of 60'-0" ('60' - 0" PER TABLE 504.3'); Table 504.3, row `R` / `S13D`, column `V-B` gives 40 ft. 60 ft is the value of the `S` and `S13R` sub-rows in the same row and column, so the architect may have read the wrong sprinkler sub-row (this building resolves to `S13D`).
   - *Code:* Table 504.3, row `R` / `S13D`, column `V-B`
   - *Confidence:* **Medium**. It could be reversed by an exception in IBC CH 4 and IBC CH 5 (Table 504.3 footnote a), not provided.
2. **BEDROOM 203 has no complying escape opening** (R-203)
   - W-10, the designated escape window: nominal 2'-0" × 2'-6" = 5.00 sq ft; the clear opening is smaller, so under both 5 and 5.7 sq ft (IBC 1030.2; IBC 1030.2 Exception); frame sill = 6'-8" head − 2'-6" height = 50 in, above 44 in (IBC 1030.3).
   - Other windows in the room: W-11 cannot comply.
   - This stands unless the room has an exit door that opens directly to a public way, yard or court (IBC 1030.1 Exception 2); the floor plans would show it.
   - *Code:* IBC 1030.1; IBC 1030.2; IBC 1030.2 Exception; IBC 1030.3
   - *Confidence:* **Medium**. It could be reversed by IBC 1030.1 Exception 2 (an exit door to a public way), which the floor plans (not provided) would show.
3. **BEDROOM 301 has no complying escape opening** (R-301)
   - W-20, the designated escape window: frame sill = 8'-0" head − 3'-0" height = 60 in, above 44 in (IBC 1030.3).
   - This stands unless the room has an exit door that opens directly to a public way, yard or court (IBC 1030.1 Exception 2); the floor plans would show it.
   - *Code:* IBC 1030.1; IBC 1030.3
   - *Confidence:* **Low**. It could be reversed by IBC 1030.1 Exception 2 (an exit door to a public way), which the floor plans (not provided) would show; W-20: it rests only on a derived value (frame sill = 8'-0" head − 3'-0" height = 60 in, above 44 in); confirm on the elevations that head height is measured to the top of the window.
4. **Window 13 in BEDROOM 205 is designated as the escape opening but cannot be one** (W-13)
   - Scheduled as 'FIXED', which does not open; no clear opening.
   - The room (R-205) is Could Not Evaluate: W-12 could not be evaluated; W-13 fails. The room has a complying opening only if it is shown to comply.
   - *Code:* IBC 1030.1.1; IBC 1030.2.1; IBC 1030.2; IBC 1030.2 Exception
   - *Confidence:* **High**. It rests on printed values only.

## 2. Check these before relying on the report

Places where the tool may be wrong, or where the drawings may hide a problem.

- **W-7 is a likely Fail on sill height.** The frame sill is exactly 44 in, so any bottom frame puts the clear opening above the limit. Confirm with the manufacturer's clear-opening dimensions.
- **W-12 is a likely Fail on clear height.** Only the bottom sash opens, about 24 in before the frame, exactly the 24 in minimum, leaving nothing for the frame. Ask for the sash split and the manufacturer's clear opening.
- **Window numbers skip.** The schedule has no window 9, 15–19. Rows may have been lost in scanning, or the windows renumbered; check the schedule sheet.
- **The code analysis claim is not supported.** It says 'PROVIDED AT ALL SLEEPING ROOMS PER IBC 1030. SEE WINDOW SCHEDULE, SHEET A6.1' (table row 13); the schedule proves a complying opening in none of the sleeping rooms (4 Could Not Evaluate, 2 Fail).
- **Rooms that may be used for sleeping.** Not treated as sleeping rooms: OFFICE 102. If any is a sleeping room, it needs an escape opening (IBC 1030.1). (W-4)
- **Sleeping rooms with no window are invisible to this tool.** The tool only knows rooms that appear in the window schedule. A bedroom with no scheduled window would need an escape opening too; check the floor plans (Floor plans, not provided).
- **Interpretation in H-1.** Occupancy 'R-3' read as row `R`: IBC 310 (occupancy classification) is not provided; the brief's rule places a numbered group in its letter's row unless the table gives the numbered group its own row (as for H and I).

**OCR damage the tool read through.** Confirm on the sheets:

| Where | What was printed, and how it was read |
|---|---|
| H-1 | label printed as 'FIRE SPRINKLE RS' (a word split across lines); read as 'FIRE SPRINKLERS' |
| H-1 | label printed as 'BUILDING HEIGHT ABOVE GRADE PLAN E' (a word split across lines); read as 'BUILDING HEIGHT ABOVE GRADE PLANE' |
| R-205, W-12 | room name 'BEDRROM' is one character from 'BEDROOM'; read as a sleeping room (likely OCR damage; confirm on the floor plan) |
| W-4 | inches 'O' read as '0' (a letter where a digit belongs; OCR damage) |
| schedule header | header 'SCREE N' read as 'SCREEN' (a word split across lines) |

## 3. Information to request

What would settle the Could Not Evaluate findings, written as requests to the architect.

| # | Request | Settles |
|---|---|---|
| 1 | Manufacturer data or window type details for window types A, F, J: the net clear opening (width, height, and the height of its bottom above the floor), the operating hardware (1030.1.1: no keys or tools) and screen release from inside (1030.5) | R-101, R-107, R-205, R-303, W-1, W-3, W-7, W-12 |
| 2 | Elevations or wall sections dimensioning each escape window's sill and head | R-101, R-107, R-205, W-1, W-3, W-7, W-12 |
| 3 | Floor plans showing room uses, any exterior door from a sleeping room (1030.1 Exception 2), and that each escape window opens onto a yard, court or public way | R-101, R-107, R-203, R-205, R-301, W-1, W-3, W-7, W-12 |
| 4 | Building sections or roof plan dimensioning the height to the average of the highest roof surface | H-1 |
| 5 | The civil sheet with the grade plane calculation | H-1 |
| 6 | Designate a complying escape opening for GUEST BED 303: none is marked egress; W-21 could comply at nominal size | R-303 |

Code text the tool was not given, which the plan checker may want to confirm: Chapters 4 and 5 (height exceptions) (footnote a) (H-1); Automatic Sprinkler Systems (903.2, 903.3.1.1-903.3.1.3) (footnote h) (H-1).

## 4. Building height (IBC Table 504.3)

### H-1 · Building height · **Fail**

41'-6" exceeds the 40 ft allowed by Table 504.3, row `R` / `S13D`, column `V-B` by 1'-6".

| Read from the code analysis | Value | Where |
|---|---|---|
| OCCUPANCY GROUP | `R-3` | code-analysis.html table row 4 |
| CONSTRUCTION TYPE | `V-B` | code-analysis.html table row 5 |
| FIRE SPRINKLE RS | `YES - AUTOMATIC SPRINKLER SYSTEM THROUGHOUT PER NFPA 13D (IBC 903.3.1.3)` | code-analysis.html table row 6 |
| BUILDING HEIGHT ABOVE GRADE PLAN E | `41' - 6" (TO AVG. HT. OF HIGHEST ROOF SURFACE)` | code-analysis.html table row 8 |
| ALLOWABLE HEIGHT | `60' - 0" PER TABLE 504.3` | code-analysis.html table row 9 |

**How it was decided:**

1. Occupancy 'R-3' → `R`
2. Sprinklers 'YES - AUTOMATIC SPRINKLER SYSTEM THROUGHOUT PER NFPA 13D (IBC 903.3.1.3)' → `S13D`
3. Construction 'V-B' → `V-B`
4. Building height '41' - 6"' = 498 in = 41.5 ft
5. Lookup Table 504.3, row `R` / `S13D`, column `V-B` → 40
6. 41.5 ft > 40 ft; over by 1.5 ft = 1'-6"

**Footnotes on this cell:**

- Footnote a (printed on the whole table): "See Chapters 4 and 5 for specific exceptions to the allowable height in this chapter." It points to code text not provided (see §3).
- Footnote h (printed on the occupancy row label): "New Group R occupancies are required to be protected by an automatic sprinkler system in accordance with Section 903.2.8." It points to code text not provided (see §3).

**Code:** Table 504.3, row `R` / `S13D`, column `V-B` = 40 ft; IBC 504.3; Table 504.3 footnote a; Table 504.3 footnote h

**Confidence:** Medium. It could be reversed by an exception in IBC CH 4 and IBC CH 5 (Table 504.3 footnote a), not provided.

## 5. Sleeping rooms (IBC 1030.1)

A sleeping room needs at least one complying escape opening. The room follows its designated egress window; with none designated, or all of them failing, its other windows are considered.

Scope: occupancy 'R-3' is listed in 1030.1 item 2. Each room's story comes from its number, using the code analysis room numbering; 1030.1 covers sleeping rooms below the fourth story above grade plane.

| ID | Room | Story | Verdict | Confidence | Windows (EGRESS on the schedule) | Why | Code |
|---|---|---|---|---|---|---|---|
| R-101 | BEDROOM 101 | 1 | Could Not Evaluate | High | W-1 (egress): Could Not Evaluate, W-2 (not egress), W-3 (egress): Could Not Evaluate | W-1, W-3 could not be evaluated. The room has a complying opening only if one of them is shown to comply. | IBC 1030.1 |
| R-107 | ADU BEDROOM 107 | 1 | Could Not Evaluate | High | W-7 (egress): Could Not Evaluate | W-7 could not be evaluated. The room has a complying opening only if it is shown to comply. | IBC 1030.1 |
| R-203 | BEDROOM 203 | 2 | **Fail** | Medium | W-10 (egress): Fail, W-11 (not egress) | The designated opening (W-10) fails, and no other window in the room could comply. Unless Exception 2 applies (an exit door to a public way), the room has no escape opening. | IBC 1030.1; IBC 1030.1 Exception 2 |
| R-205 | BEDROOM 205 | 2 | Could Not Evaluate | Medium | W-12 (egress): Could Not Evaluate, W-13 (egress): Fail | W-12 could not be evaluated; W-13 fails. The room has a complying opening only if it is shown to comply. The schedule spells this room more than one way; windows are grouped by room number. | IBC 1030.1 |
| R-301 | BEDROOM 301 | 3 | **Fail** | Low | W-20 (egress): Fail | The designated opening (W-20) fails, and no other window in the room could comply. Unless Exception 2 applies (an exit door to a public way), the room has no escape opening. | IBC 1030.1; IBC 1030.1 Exception 2 |
| R-303 | GUEST BED 303 | 3 | Could Not Evaluate | High | W-21 (not egress) | No window is designated as the escape opening; W-21 could comply at nominal size but is not marked egress. Ask the architect to designate a complying opening. | IBC 1030.1 |

## 6. Egress windows (IBC 1030.2, 1030.3)

Windows marked EGRESS on the schedule. How to read the results:

- **Nominal size is an upper bound (≤).** It includes the frame, so the net clear area, height and width are at most the nominal figure. It can prove a Fail, never a Pass.
- **The sill is a lower bound (≥).** Sill = head height − window height, which is the frame's sill. The clear opening starts higher, by the depth of the bottom frame.
- **?** = not settled by the schedule. **⚠** = likely Fail (see §2). **Met** = satisfied as scheduled.
- **No schedule shows these, so they are open for every window below:** opening without keys or tools (IBC 1030.1.1), screens that release from inside (IBC 1030.5), and opening onto a public way, yard or court (IBC 1030.1). §3 lists what would settle them.

| ID | Room | Type | Nominal W × H | Head | Opens (1030.2.1) | Area ≥ 5.7 sq ft (1030.2) | Clear height ≥ 24 in (1030.2.1) | Clear width ≥ 20 in (1030.2.1) | Sill ≤ 44 in (1030.3) | Verdict | Confidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| W-1 | BEDROOM 101 | L.H. CASM'T (type A) | 2' - 6" × 4' - 0" | 6' - 8" | Met | ? ≤ 10.00 sq ft | ? ≤ 48 in | ? ≤ 30 in | ? ≥ 32 in | Could Not Evaluate | High |
| W-3 | BEDROOM 101 | R.H. CASM'T (type A) | 2' - 6" × 4' - 0" | 6' - 8" | Met | ? ≤ 10.00 sq ft | ? ≤ 48 in | ? ≤ 30 in | ? ≥ 32 in | Could Not Evaluate | High |
| W-7 | ADU BEDROOM 107 | L.H. CASM'T (type F) | 2'-6" × 3' - 0" | 6' - 8" | Met | ? ≤ 7.50 sq ft | ? ≤ 36 in | ? ≤ 30 in | ? ≥ 44 in ⚠ | Could Not Evaluate | High |
| W-10 | BEDROOM 203 | L.H. CASM'T (type H) | 2' - 0" × 2' - 6" | 6' - 8" | Met | **Fail** (≤ 5.00 sq ft) | ? ≤ 30 in | ? ≤ 24 in | **Fail** (≥ 50 in) | **Fail** | High |
| W-12 | BEDRROM 205 | S.H. (type J) | 3' - 0" × 4' - 0" | 6' - 8" | Met | ? ≤ 12.00 sq ft | ? ≤ 48 in ⚠ | ? ≤ 36 in | ? ≥ 32 in | Could Not Evaluate | Medium |
| W-13 | BEDROOM 205 | FIXED (type K) | 4' - 0" × 4' - 0" | 6' - 8" | **Fail** | **Fail** (does not open) | — | — | ? ≥ 32 in | **Fail** | High |
| W-20 | BEDROOM 301 | L.H. CASM'T (type F) | 2' - 6" × 3' - 0" | 8' - 0" | Met | ? ≤ 7.50 sq ft | ? ≤ 36 in | ? ≤ 30 in | **Fail** (≥ 60 in) | **Fail** | Medium |

The area limit is 5.0 sq ft for a grade-floor opening (1030.2 Exception), and grade-floor status is not shown, so a nominal area fails only at or below 5.0. Values are as printed on the schedule; Appendix B gives each window's row.

## 7. Windows: Not Applicable

| ID | Room | EGRESS cell | Verdict | Confidence | Why | Code |
|---|---|---|---|---|---|---|
| W-2 | BEDROOM 101 | (blank) | Not Applicable | High | Not marked egress; 1030.1 needs one escape opening per sleeping room, not every window. Considered in R-101. | IBC 1030.1 |
| W-4 | OFFICE 102 | (blank) | Not Applicable | Low | Not clearly a sleeping room, so not evaluated. Confirm its use (see §2); if it is a sleeping room, it needs an escape opening. | IBC 1030.1 |
| W-5 | LIVING 103 | (blank) | Not Applicable | High | Not a sleeping room (1030.1 applies to sleeping rooms). | IBC 1030.1 |
| W-6 | KITCHEN 104 | (blank) | Not Applicable | High | Not a sleeping room (1030.1 applies to sleeping rooms). | IBC 1030.1 |
| W-8 | LAUNDRY 108 | (blank) | Not Applicable | High | Not a sleeping room (1030.1 applies to sleeping rooms). | IBC 1030.1 |
| W-11 | BEDROOM 203 | (blank) | Not Applicable | High | Not marked egress; 1030.1 needs one escape opening per sleeping room, not every window. Considered in R-203. | IBC 1030.1 |
| W-14 | BATH 206 | (blank) | Not Applicable | High | Not a sleeping room (1030.1 applies to sleeping rooms). | IBC 1030.1 |
| W-21 | GUEST BED 303 | (blank) | Not Applicable | High | Not marked egress; 1030.1 needs one escape opening per sleeping room, not every window. Considered in R-303. | IBC 1030.1 |
| W-22 | HALL 302 | (blank) | Not Applicable | High | Not a sleeping room (1030.1 applies to sleeping rooms). | IBC 1030.1 |
| W-23 | STAIR S1 | (blank) | Not Applicable | High | Not a sleeping room (1030.1 applies to sleeping rooms). | IBC 1030.1 |

## Appendix

### A. Code text cited

Every code limit the checks use is quoted word for word from these lines; the tool refuses to run if a quote is not found there.

| Section | Where in the code files |
|---|---|
| IBC 1030.1 | `code/section-1030-emergency-escape-and-rescue.md` line 13 |
| IBC 1030.1 Exception 2 | `code/section-1030-emergency-escape-and-rescue.md` line 19 |
| IBC 1030.1.1 | `code/section-1030-emergency-escape-and-rescue.md` line 31 |
| IBC 1030.2 | `code/section-1030-emergency-escape-and-rescue.md` line 35 |
| IBC 1030.2 Exception | `code/section-1030-emergency-escape-and-rescue.md` line 37 |
| IBC 1030.2.1 | `code/section-1030-emergency-escape-and-rescue.md` line 41 |
| IBC 1030.3 | `code/section-1030-emergency-escape-and-rescue.md` line 45 |
| IBC 1030.5 | `code/section-1030-emergency-escape-and-rescue.md` line 49 |
| IBC 504.3 | `code/table-504.3-notes.md` line 7 |
| Table 504.3 footnote a | `code/table-504.3-notes.md` line 19 |
| Table 504.3 footnote h | `code/table-504.3-notes.md` line 33 |

### B. Where each value was read

Rows are counted from 1 at the top of each table, header rows included.

| ID | Source |
|---|---|
| H-1 | code-analysis.html table rows 4, 5, 6, 8, 9 |
| R-101 | window-schedule.html, LOCATION 'BEDROOM 101' |
| R-107 | window-schedule.html, LOCATION 'ADU BEDROOM 107' |
| R-203 | window-schedule.html, LOCATION 'BEDROOM 203' |
| R-205 | window-schedule.html, LOCATION 'BEDRROM 205', 'BEDROOM 205' |
| R-301 | window-schedule.html, LOCATION 'BEDROOM 301' |
| R-303 | window-schedule.html, LOCATION 'GUEST BED 303' |
| W-1 | window-schedule.html table row 4 |
| W-2 | window-schedule.html table row 5 |
| W-3 | window-schedule.html table row 6 |
| W-4 | window-schedule.html table row 7 |
| W-5 | window-schedule.html table row 8 |
| W-6 | window-schedule.html table row 9 |
| W-7 | window-schedule.html table row 10 |
| W-8 | window-schedule.html table row 11 |
| W-10 | window-schedule.html table row 12 |
| W-11 | window-schedule.html table row 13 |
| W-12 | window-schedule.html table row 14 |
| W-13 | window-schedule.html table row 15 |
| W-14 | window-schedule.html table row 16 |
| W-20 | window-schedule.html table row 17 |
| W-21 | window-schedule.html table row 18 |
| W-22 | window-schedule.html table row 19 |
| W-23 | window-schedule.html table row 20 |

### C. Rules the tool applied

Judgement calls are named rules, the same for every project, each with a test.

| Rule | What it says | Rests on | Used by |
|---|---|---|---|
| `POL-GEN-AMENDMENTS` Local amendments not provided | The project is reviewed against the 2018 IBC as printed. If the manifest lists local amendments as not provided, every verdict is conditional on them and the report says so once, at the top. | the local-amendments document listed in the manifest (unavailable) | whole report |
| `POL-GEN-SCHEDULE-GAPS` Gaps in a numbered schedule are reported | When every window mark is a whole number, numbers missing between the lowest and highest are listed for the plan checker: rows may have been lost in scanning, or windows renumbered. No verdict changes. | src/NOTES.md decision: report review rounds, 2026-11-08 | whole report |
| `POL-GEN-CONFIDENCE` Every finding carries a confidence level, from named reasons | Confidence (High, Medium, Low) says how likely a verdict is to survive review with the full drawing set. It starts at High and drops one level for each of: a Fail whose only failing grounds are derived values; a Fail that a document not provided could reverse (an exception it points to, not ruled out); a verdict resting on a repaired room-name reading. A verdict decided by a guess at a room's use is Low. A room's Fail takes on the lowered levels of the failing windows it rests on. Interpretations the brief itself gives do not lower it. Confidence never changes a verdict. | src/NOTES.md decision: confidence levels, 2026-11-08 | whole report |
| `POL-H-INTERPRETATION` Brief rules may support a verdict, disclosed | A mapping that rests on the challenge brief rather than code text (R-3 read as row R, because IBC 310 is not provided) may support a Pass or Fail, but the finding names it as an interpretation. The limit value itself always comes from code text. | Challenge brief (instructions/README.md line 54) | H-1 |
| `POL-H-FOOTNOTES` Footnotes are cited; pointed-to documents are listed, not assumed | Every footnote on the looked-up cell is quoted in the finding. Where a footnote points to a document we don't have (Chapters 4 and 5 exceptions, IBC 903.2.8), the finding lists it as not provided. It does not block the verdict: an exception has to be claimed by the applicant, and the finding says which claims the code analysis makes. | Table 504.3 footnotes (code/table-504.3-notes.md lines 19-33) | H-1 |
| `POL-H-STATED-HEIGHT` The stated height is used as submitted | The building height is the architect's figure. The tool compares it with the table; it cannot check the measurement (grade plane and roof heights are on sheets not provided), and says so. | IBC 202 HEIGHT, BUILDING (code/section-1030-emergency-escape-and-rescue.md line 59) | H-1 |
| `POL-H-ARCHITECT` The architect's allowable height is checked, not trusted | If the code analysis states an allowable height that differs from the looked-up cell, the finding flags it and lists the cells in the same row and column that hold the architect's figure, as a likely explanation. The verdict uses the looked-up cell. | brief: the allowable height 'is worth checking against the table rather than trusting' | H-1 |
| `POL-H-SPRINKLER-COVERAGE` Sprinkler coverage must be 'throughout' | S, S13R and S13D are for buildings 'equipped throughout'. Wording that says partial coverage resolves to no sub-row (Could Not Evaluate). Wording that names a standard but not 'throughout' is resolved and flagged. | Table 504.3 legend (code/table-504.3-notes.md line 15) | H-1 |
| `POL-E-SCOPE` Which buildings and floors 1030 covers | R-3 and R-4: applies. R-2: Could Not Evaluate unless the exits per story are known. Other groups: Not Applicable. Sleeping rooms must be below the fourth story above grade plane; the story comes from the code analysis room numbering (floor n read as story n above grade plane), else from the number of stories. Unknown story: Could Not Evaluate. | IBC 1030.1 item 2 (code/section-1030-emergency-escape-and-rescue.md line 11); IBC 1030.1 item 1 (code/section-1030-emergency-escape-and-rescue.md line 9); IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13) | W-1, W-3, W-7, W-10, W-12, W-13, W-20 |
| `POL-E-SLEEPING` What counts as a sleeping room | Room names with a bedroom word (BEDROOM, BED, BDRM, GUEST BED ...) are sleeping rooms, including a word one character from BEDROOM (OCR), which is flagged. Dens, offices, lofts and unrecognised names are ambiguous: not treated as sleeping rooms, but listed for the plan checker to confirm. | Challenge brief (instructions/README.md line 60) | R-101, R-107, R-203, R-205, R-301, R-303, W-4 |
| `POL-E-ROOM-KEY` Room identity | Windows belong to the same room when their location has the same room number ('BEDROM 12' and 'BEDROOM 12'); without a number, when the names match. Different spellings under one number are flagged. | window schedule LOCATION column | R-101, R-107, R-203, R-205, R-301, R-303 |
| `POL-E-NOT-SLEEPING` Windows outside sleeping rooms | Windows in rooms that are not sleeping rooms are Not Applicable. A window in such a room that is marked egress is noted. | IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13) | W-5, W-6, W-8, W-14, W-22, W-23 |
| `POL-E-NOT-DESIGNATED` Sleeping-room windows not marked egress | Not Applicable as a window finding: 1030 needs one complying opening per sleeping room, not every window. They are still considered in the room finding. | IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13) | W-2, W-11, W-21 |
| `POL-E-NOMINAL-UPPER` Nominal size is an upper bound | The net clear opening (area, width and height) is always smaller than the nominal size. A nominal value at or below a minimum proves a Fail; a nominal value above it proves nothing. | Challenge brief (instructions/README.md line 63); IBC 1030.2 (code/section-1030-emergency-escape-and-rescue.md line 35); IBC 1030.2.1 (code/section-1030-emergency-escape-and-rescue.md line 41) | W-1, W-3, W-7, W-10, W-12, W-20 |
| `POL-E-NO-FRAME-ASSUMPTION` No frame-deduction assumption (decision 2) | The tool assumes no frame size, so nominal size never proves a Pass. Without a net clear opening (from the schedule or manufacturer data) a minimum is Could Not Evaluate, with the nominal upper bound shown. | src/NOTES.md, Plan from here: open decisions #2 | W-1, W-3, W-7, W-10, W-12, W-20 |
| `POL-E-SILL-LOWER` A derived sill is a lower bound | Sill = head height - nominal height (head height is floor to top of window). The bottom of the clear opening is at or above that frame sill. A frame sill above 44 in proves a Fail; at or below 44 in it proves nothing, because the bottom frame depth is unknown. A scheduled sill height is treated the same way unless the column says it is to the clear opening. | IBC 1030.3 (code/section-1030-emergency-escape-and-rescue.md line 45); Challenge brief (instructions/README.md line 64) | W-1, W-3, W-7, W-10, W-12, W-13, W-20 |
| `POL-E-GRADE-FLOOR` Grade-floor limit (decision 4) | Whether an opening is a grade-floor opening needs the finished ground level, which these sheets don't give. The area is decided only when the 5.0 and 5.7 sq ft limits give the same result. | IBC 1030.2 Exception (code/section-1030-emergency-escape-and-rescue.md line 37); IBC 202 GRADE FLOOR OPENING (code/section-1030-emergency-escape-and-rescue.md line 55); src/NOTES.md, Plan from here: open decisions #4 | W-1, W-3, W-7, W-10, W-12, W-20 |
| `POL-E-FIXED` A fixed window is not an escape opening | A window scheduled as fixed does not open, so it can't be operated from inside and has no net clear opening by normal operation: Fail. | IBC 1030.1.1 (code/section-1030-emergency-escape-and-rescue.md line 31); IBC 1030.2.1 (code/section-1030-emergency-escape-and-rescue.md line 41) | W-13 |
| `POL-E-PARTIAL-OPENING` Single hung and slider bounds are notes only (decision 5) | A single hung opens only its bottom sash and a slider about half its width. The tool shows the half-size figure as a labelled note, never as proof of a Fail, because panel splits vary (a three-panel slider opens two thirds; sashes can be unequal). | Challenge brief (instructions/README.md line 66); src/NOTES.md, Plan from here: open decisions #5 | W-12 |
| `POL-E-AT-LIMIT` A bound sitting exactly at a limit is flagged as a likely Fail | A frame sill exactly at the 44 in maximum, or a partial-opening note (bottom sash, half a slider) at or below a minimum, cannot prove a Fail from the schedule, so the verdict stays Could Not Evaluate. The window is flagged 'expect a Fail' and listed first among the items to check, because any frame deduction tips it over. | IBC 1030.3 (code/section-1030-emergency-escape-and-rescue.md line 45); IBC 1030.2.1 (code/section-1030-emergency-escape-and-rescue.md line 41); src/NOTES.md decision: report review rounds, 2026-11-08 | W-7, W-12 |
| `POL-E-UNSEEN` Requirements no schedule shows | Operation without keys or tools, releasable screens and opening onto a public way, yard or court are each a Could Not Evaluate line on every egress window, naming the document that would settle it. They never cause a Fail; they do keep a window from a Pass. | IBC 1030.1.1 (code/section-1030-emergency-escape-and-rescue.md line 31); IBC 1030.5 (code/section-1030-emergency-escape-and-rescue.md line 49); IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13) | W-1, W-3, W-7, W-10, W-12, W-13, W-20 |
| `POL-E-ROOM-ROLLUP` Room verdict (decision 3) | A sleeping room Passes if a designated egress window Passes, and is Could Not Evaluate if one is Could Not Evaluate. If none is designated, or every designated one Fails, the room's other windows are evaluated as candidates: if any could comply the room is Could Not Evaluate, flagged 'no complying opening designated'; if none could, the room Fails. | IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13); src/NOTES.md, Plan from here: open decisions #3 | R-101, R-107, R-203, R-205, R-301, R-303 |
| `POL-E-EXCEPTION-2` Exit-door exception is not assumed | A room Fail says 'unless Exception 2 applies (an exit door to a public way)'. The floor plans would settle it; the tool does not assume a door it can't see. | IBC 1030.1 Exception 2 (code/section-1030-emergency-escape-and-rescue.md line 19) | R-203, R-301 |

Not needed for this project: `POL-GEN-OCR` (OCR-repaired values never decide a verdict alone), `POL-GEN-UNCOVERED` (No rule, no verdict), `POL-H-NS-NEW` (NS limits are for existing buildings), `POL-E-OPERATION-UNKNOWN` (Unrecognised window type), `POL-E-NO-EGRESS-COLUMN` (Schedule without an egress column).

### D. Inputs

| Input | File | sha256 (first 12) |
|---|---|---|
| Code analysis (CODE ANALYSIS - SHEET A0.1) | `code-analysis.html` | `a0dc18fc9c36` |
| Window schedule | `window-schedule.html` | `85de501d0b3c` |

Generated by `python -m services.planCheck code-analysis.html window-schedule.html -o REPORT.md --json findings.json`. The same findings are in `findings.json`.

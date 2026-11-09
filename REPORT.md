# Plan check report: building height and emergency escape openings

Checked against **IBC 2018 Table 504.3** (allowable building height) and **IBC 2018 Section 1030** (emergency escape and rescue openings).

| Input | File | sha256 (first 12) |
|---|---|---|
| Code analysis (CODE ANALYSIS - SHEET A0.1) | `code-analysis.html` | `a0dc18fc9c36` |
| Window schedule | `window-schedule.html` | `85de501d0b3c` |

> **Read this first.** Verdicts use the 2018 IBC as printed. City of Meridian Falls amendments to the 2018 IBC were not provided, so every verdict is conditional on them (`POL-GEN-AMENDMENTS`). Pass and Fail are used only where the two sheets decide the question; everything else is Could Not Evaluate with the document that would settle it.

## Summary

| ✅ Pass | ❌ Fail | ❓ Could Not Evaluate | ➖ Not Applicable |
|---|---|---|---|
| 0 | 6 | 8 | 10 |

- **Building height:** ❌ **Fail**. 41'-6" exceeds the 40 ft allowed by Table 504.3, row `R` / `S13D`, column `V-B` by 1'-6".
- **Sleeping rooms, Fail:** [R-203](#r-203) BEDROOM 203 (room 203), [R-301](#r-301) BEDROOM 301 (room 301)
- **Sleeping rooms, Could Not Evaluate:** [R-101](#r-101) BEDROOM 101 (room 101), [R-107](#r-107) ADU BEDROOM 107 (room 107), [R-205](#r-205) BEDROOM 205 (room 205), [R-303](#r-303) GUEST BED 303 (room 303)

## Fails: raw material for the correction letter

1. **[H-1](#h-1) Building height.** 41'-6" exceeds the 40 ft allowed by Table 504.3, row `R` / `S13D`, column `V-B` by 1'-6". *Code:* Table 504.3, row `R` / `S13D`, column `V-B` = 40 ft
2. **[R-203](#r-203) BEDROOM 203 (room 203).** The designated opening (W-10) fails, and no other window in the room could comply. Unless Exception 2 applies (an exit door to a public way), the room has no escape opening. *Code:* IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13); IBC 1030.1 Exception 2 (code/section-1030-emergency-escape-and-rescue.md line 19)
3. **[R-301](#r-301) BEDROOM 301 (room 301).** The designated opening (W-20) fails, and no other window in the room could comply. Unless Exception 2 applies (an exit door to a public way), the room has no escape opening. *Code:* IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13); IBC 1030.1 Exception 2 (code/section-1030-emergency-escape-and-rescue.md line 19)
4. **[W-10](#w-10) Window 10, BEDROOM 203.** Net clear area: nominal 24 in x 30 in = 720 sq in = 5.00 sq ft (upper bound); the net clear opening is smaller than 5.00 sq ft, so below 5 and 5.7 sq ft whether or not it is a grade-floor opening. Sill height: derived frame sill = head height 80 in - nominal height 30 in = 50 in (4'-2"); the clear opening's bottom is at or above the 50 in frame sill, more than 44 in. *Code:* IBC 1030.2 (code/section-1030-emergency-escape-and-rescue.md line 35); IBC 1030.2 Exception (code/section-1030-emergency-escape-and-rescue.md line 37); IBC 1030.3 (code/section-1030-emergency-escape-and-rescue.md line 45)
5. **[W-13](#w-13) Window 13, BEDROOM 205.** Opening type: type 'FIXED' (fixed); a fixed window does not open. Net clear area: fixed: no opening; no net clear opening results from normal operation. *Code:* IBC 1030.1.1 (code/section-1030-emergency-escape-and-rescue.md line 31); IBC 1030.2.1 (code/section-1030-emergency-escape-and-rescue.md line 41); IBC 1030.2 (code/section-1030-emergency-escape-and-rescue.md line 35); IBC 1030.2 Exception (code/section-1030-emergency-escape-and-rescue.md line 37); IBC 1030.2.1 (code/section-1030-emergency-escape-and-rescue.md line 41)
6. **[W-20](#w-20) Window 20, BEDROOM 301.** Sill height: derived frame sill = head height 96 in - nominal height 36 in = 60 in (5'-0"); the clear opening's bottom is at or above the 60 in frame sill, more than 44 in. *Code:* IBC 1030.3 (code/section-1030-emergency-escape-and-rescue.md line 45)

## Needs your attention

- **Architect's allowable height disagrees with Table 504.3.** The code analysis states an allowable height of 60'-0" ('60\' - 0" PER TABLE 504.3'); Table 504.3, row `R` / `S13D`, column `V-B` gives 40 ft. 60 ft is the value of row `R` / `S`, column `V-B`, row `R` / `S13R`, column `V-B`, so the architect may have read a sprinkler sub-row other than `S13D`. ([H-1](#h-1))
- **Code analysis claim about escape openings is not supported.** The code analysis says 'PROVIDED AT ALL SLEEPING ROOMS PER IBC 1030. SEE WINDOW SCHEDULE, SHEET A6.1' (row 12). The schedule does not show a complying opening in: BEDROOM 101 (room 101) (Could Not Evaluate); ADU BEDROOM 107 (room 107) (Could Not Evaluate); BEDROOM 203 (room 203) (Fail); BEDROOM 205 (room 205) (Could Not Evaluate); BEDROOM 301 (room 301) (Fail); GUEST BED 303 (room 303) (Could Not Evaluate). ([R-101](#r-101), [R-107](#r-107), [R-203](#r-203), [R-205](#r-205), [R-301](#r-301), [R-303](#r-303))
- **OCR damage the tool read through.** Confirm these on the sheets: H-1: label printed as 'FIRE SPRINKLE RS' (a word split across lines); read as 'FIRE SPRINKLERS' | H-1: label printed as 'BUILDING HEIGHT ABOVE GRADE PLAN E' (a word split across lines); read as 'BUILDING HEIGHT ABOVE GRADE PLANE' | R-205: room name 'BEDRROM' is one character from 'BEDROOM'; read as a sleeping room (likely OCR damage; confirm on the floor plan) | W-4: inches 'O' read as '0' (a letter where a digit belongs; OCR damage) | W-12: room name 'BEDRROM' is one character from 'BEDROOM'; read as a sleeping room (likely OCR damage; confirm on the floor plan) | schedule: header 'SCREE N' read as 'SCREEN' (a word split across lines) ([H-1](#h-1), [R-205](#r-205), [W-4](#w-4), [W-12](#w-12))
- **Rooms that may be used for sleeping.** Not treated as sleeping rooms: OFFICE 102. If any is a sleeping room, it needs an escape opening (IBC 1030.1). ([W-4](#w-4))
- **Sleeping rooms with no window are invisible to this tool.** The tool only knows rooms that appear in the window schedule. A bedroom with no scheduled window would need an escape opening too; check the floor plans (Floor plans, not provided).

## All findings

| ID | Verdict | Subject | Why |
|---|---|---|---|
| [H-1](#h-1) | ❌ Fail | Building height | 41'-6" exceeds the 40 ft allowed by Table 504.3, row `R` / `S13D`, column `V-B` by 1'-6". |
| [R-101](#r-101) | ❓ Could Not Evaluate | BEDROOM 101 (room 101) | W-1, W-3 could not be evaluated. The room has a complying opening only if one of them is shown to comply. |
| [R-107](#r-107) | ❓ Could Not Evaluate | ADU BEDROOM 107 (room 107) | W-7 could not be evaluated. The room has a complying opening only if it is shown to comply. |
| [R-203](#r-203) | ❌ Fail | BEDROOM 203 (room 203) | The designated opening (W-10) fails, and no other window in the room could comply. Unless Exception 2 applies (an exit door to a public way), the room has no escape opening. |
| [R-205](#r-205) | ❓ Could Not Evaluate | BEDROOM 205 (room 205) | W-12 could not be evaluated; W-13 fails. The room has a complying opening only if it is shown to comply. |
| [R-301](#r-301) | ❌ Fail | BEDROOM 301 (room 301) | The designated opening (W-20) fails, and no other window in the room could comply. Unless Exception 2 applies (an exit door to a public way), the room has no escape opening. |
| [R-303](#r-303) | ❓ Could Not Evaluate | GUEST BED 303 (room 303) | No window is designated as the escape opening; W-21 could comply at nominal size but is not marked egress. Ask the architect to designate a complying opening. |
| [W-1](#w-1) | ❓ Could Not Evaluate | Window 1, BEDROOM 101 | Nothing fails at nominal size. Not settled by the schedule: net clear area (nominal 10.00 sq ft is only an upper bound); clear height; clear width; sill height (frame sill 32 in (2'-8")). Also unverified (never on a schedule): hardware, screens, public way. |
| [W-2](#w-2) | ➖ Not Applicable | Window 2, BEDROOM 101 | Not marked egress; 1030 needs one complying opening per sleeping room, not every window. Considered in R-101. |
| [W-3](#w-3) | ❓ Could Not Evaluate | Window 3, BEDROOM 101 | Nothing fails at nominal size. Not settled by the schedule: net clear area (nominal 10.00 sq ft is only an upper bound); clear height; clear width; sill height (frame sill 32 in (2'-8")). Also unverified (never on a schedule): hardware, screens, public way. |
| [W-4](#w-4) | ➖ Not Applicable | Window 4, OFFICE 102 | 'OFFICE 102' is not clearly a sleeping room (flagged for review); 1030.1 requires escape openings in sleeping rooms. |
| [W-5](#w-5) | ➖ Not Applicable | Window 5, LIVING 103 | 'LIVING 103' is not a sleeping room; 1030.1 requires escape openings in sleeping rooms. |
| [W-6](#w-6) | ➖ Not Applicable | Window 6, KITCHEN 104 | 'KITCHEN 104' is not a sleeping room; 1030.1 requires escape openings in sleeping rooms. |
| [W-7](#w-7) | ❓ Could Not Evaluate | Window 7, ADU BEDROOM 107 | Nothing fails at nominal size. Not settled by the schedule: net clear area (nominal 7.50 sq ft is only an upper bound); clear height; clear width; sill height (frame sill 44 in (3'-8")). Also unverified (never on a schedule): hardware, screens, public way. |
| [W-8](#w-8) | ➖ Not Applicable | Window 8, LAUNDRY 108 | 'LAUNDRY 108' is not a sleeping room; 1030.1 requires escape openings in sleeping rooms. |
| [W-10](#w-10) | ❌ Fail | Window 10, BEDROOM 203 | Net clear area: nominal 24 in x 30 in = 720 sq in = 5.00 sq ft (upper bound); the net clear opening is smaller than 5.00 sq ft, so below 5 and 5.7 sq ft whether or not it is a grade-floor opening. Sill height: derived frame sill = head height 80 in - nominal height 30 in = 50 in (4'-2"); the clear opening's bottom is at or above the 50 in frame sill, more than 44 in. |
| [W-11](#w-11) | ➖ Not Applicable | Window 11, BEDROOM 203 | Not marked egress; 1030 needs one complying opening per sleeping room, not every window. Considered in R-203. |
| [W-12](#w-12) | ❓ Could Not Evaluate | Window 12, BEDRROM 205 | Nothing fails at nominal size. Not settled by the schedule: net clear area (nominal 12.00 sq ft is only an upper bound); clear height; clear width; sill height (frame sill 32 in (2'-8")). Also unverified (never on a schedule): hardware, screens, public way. |
| [W-13](#w-13) | ❌ Fail | Window 13, BEDROOM 205 | Opening type: type 'FIXED' (fixed); a fixed window does not open. Net clear area: fixed: no opening; no net clear opening results from normal operation. |
| [W-14](#w-14) | ➖ Not Applicable | Window 14, BATH 206 | 'BATH 206' is not a sleeping room; 1030.1 requires escape openings in sleeping rooms. |
| [W-20](#w-20) | ❌ Fail | Window 20, BEDROOM 301 | Sill height: derived frame sill = head height 96 in - nominal height 36 in = 60 in (5'-0"); the clear opening's bottom is at or above the 60 in frame sill, more than 44 in. |
| [W-21](#w-21) | ➖ Not Applicable | Window 21, GUEST BED 303 | Not marked egress; 1030 needs one complying opening per sleeping room, not every window. Considered in R-303. |
| [W-22](#w-22) | ➖ Not Applicable | Window 22, HALL 302 | 'HALL 302' is not a sleeping room; 1030.1 requires escape openings in sleeping rooms. |
| [W-23](#w-23) | ➖ Not Applicable | Window 23, STAIR S1 | 'STAIR S1' is not a sleeping room; 1030.1 requires escape openings in sleeping rooms. |

## Check 1: Building height (IBC Table 504.3)

<a id="h-1"></a>
### H-1 · Building height · ❌ **Fail**

**Why:** 41'-6" exceeds the 40 ft allowed by Table 504.3, row `R` / `S13D`, column `V-B` by 1'-6".

**Code:** Table 504.3, row `R` / `S13D`, column `V-B` = 40 ft; IBC 504.3 (code/table-504.3-notes.md line 7); Table 504.3 footnote a (code/table-504.3-notes.md line 19); Table 504.3 footnote h (code/table-504.3-notes.md line 33)

| Read from the drawings | Value | Where |
|---|---|---|
| OCCUPANCY GROUP | `R-3` | code-analysis.html row 3, label 'OCCUPANCY GROUP' |
| CONSTRUCTION TYPE | `V-B` | code-analysis.html row 4, label 'CONSTRUCTION TYPE' |
| FIRE SPRINKLE RS | `YES - AUTOMATIC SPRINKLER SYSTEM THROUGHOUT PER NFPA 13D (IBC 903.3.1.3)` | code-analysis.html row 5, label 'FIRE SPRINKLE RS' |
| BUILDING HEIGHT ABOVE GRADE PLAN E | `41' - 6" (TO AVG. HT. OF HIGHEST ROOF SURFACE)` | code-analysis.html row 7, label 'BUILDING HEIGHT ABOVE GRADE PLAN E' |
| ALLOWABLE HEIGHT | `60' - 0" PER TABLE 504.3` | code-analysis.html row 8, label 'ALLOWABLE HEIGHT' |

**Working:**

- occupancy 'R-3' -> `R` (resolver rule occupancy.numbered_group)
- sprinklers 'YES - AUTOMATIC SPRINKLER SYSTEM THROUGHOUT PER NFPA 13D (IBC 903.3.1.3)' -> `S13D` (resolver rule sprinkler.nfpa13d)
- construction 'V-B' -> `V-B` (resolver rule construction.exact)
- building height '41\' - 6"' = 498 in = 41.5 ft
- lookup Table 504.3, row `R` / `S13D`, column `V-B` -> 40
- footnote a (printed on the whole table): "See Chapters 4 and 5 for specific exceptions to the allowable height in this chapter." Points to: IBC CH 4 (IBC:2018:CH4-CH5, unavailable); IBC CH 5 (IBC:2018:CH4-CH5, unavailable).
- footnote h (printed on the occupancy row label): "New Group R occupancies are required to be protected by an automatic sprinkler system in accordance with Section 903.2.8." Points to: IBC 903.2.8 (IBC:2018:903, unavailable).
- 41.5 ft > 40 ft; over by 1.5 ft = 1'-6"

**Interpretations (not code text):**

- occupancy 'R-3' read as row `R`: IBC 310 (occupancy classification) is not provided; the brief's rule places a numbered group in its letter's row unless the table gives the numbered group its own row (as for H and I). (authority: challenge_brief, instructions/README.md line 54)

**Flags:**

- ⚠️ label printed as 'FIRE SPRINKLE RS' (a word split across lines); read as 'FIRE SPRINKLERS'
- ⚠️ label printed as 'BUILDING HEIGHT ABOVE GRADE PLAN E' (a word split across lines); read as 'BUILDING HEIGHT ABOVE GRADE PLANE'
- ⚠️ The code analysis states an allowable height of 60'-0" ('60\' - 0" PER TABLE 504.3'); Table 504.3, row `R` / `S13D`, column `V-B` gives 40 ft. 60 ft is the value of row `R` / `S`, column `V-B`, row `R` / `S13R`, column `V-B`, so the architect may have read a sprinkler sub-row other than `S13D`.

**Would settle it:** Building sections / roof plan (PROJECT:BUILDING-SECTIONS, not provided); Civil sheet C1.0 (grade plane) (PROJECT:C1.0:CIVIL, not provided); Chapters 4 and 5 (height exceptions) (IBC:2018:CH4-CH5, not provided; related through footnote a); Automatic Sprinkler Systems (903.2, 903.3.1.1-903.3.1.3) (IBC:2018:903, not provided; related through footnote h)

**Rules applied:** `POL-H-STATED-HEIGHT`, `POL-H-INTERPRETATION`, `POL-H-SPRINKLER-COVERAGE`, `POL-H-FOOTNOTES`, `POL-H-ARCHITECT`

## Check 2: Emergency escape and rescue openings (IBC 1030)

Nominal sizes on the schedule include the frame. The net clear opening is always smaller, so a nominal size can prove a Fail but never a Pass (`POL-E-NOMINAL-UPPER`). Sill heights are derived as head height minus window height, which is the frame sill; the clear opening's bottom is at or above it (`POL-E-SILL-LOWER`).

### Sleeping rooms

<a id="r-101"></a>
#### R-101 · BEDROOM 101 (room 101) · ❓ **Could Not Evaluate**

**Why:** W-1, W-3 could not be evaluated. The room has a complying opening only if one of them is shown to comply.

**Code:** IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13)

| Read from the drawings | Value | Where |
|---|---|---|
| windows | `1 (L.H. CASM'T, egress 'Y'), 2 (FIXED, egress ''), 3 (R.H. CASM'T, egress 'Y')` | window-schedule.html, LOCATION 'BEDROOM 101' |

**Working:**

- scope: occupancy 'R-3' is listed in 1030.1 item 2; room 101 is on floor 1 (code analysis room numbering), below the fourth story above grade plane
- windows in this room: W-1, W-2, W-3
- designated egress: W-1 Could Not Evaluate, W-3 Could Not Evaluate

**Would settle it:** Window type details (PROJECT:WINDOW-DETAILS, not provided) or Elevations (PROJECT:ELEVATIONS, not provided); Floor plans (PROJECT:FLOOR-PLANS, not provided) or site plan

**Rules applied:** `POL-E-ROOM-ROLLUP`, `POL-E-SLEEPING`, `POL-E-ROOM-KEY`

<a id="r-107"></a>
#### R-107 · ADU BEDROOM 107 (room 107) · ❓ **Could Not Evaluate**

**Why:** W-7 could not be evaluated. The room has a complying opening only if it is shown to comply.

**Code:** IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13)

| Read from the drawings | Value | Where |
|---|---|---|
| windows | `7 (L.H. CASM'T, egress 'Y')` | window-schedule.html, LOCATION 'ADU BEDROOM 107' |

**Working:**

- scope: occupancy 'R-3' is listed in 1030.1 item 2; room 107 is on floor 1 (code analysis room numbering), below the fourth story above grade plane
- windows in this room: W-7
- designated egress: W-7 Could Not Evaluate

**Would settle it:** Window type details (PROJECT:WINDOW-DETAILS, not provided) or Elevations (PROJECT:ELEVATIONS, not provided); Floor plans (PROJECT:FLOOR-PLANS, not provided) or site plan

**Rules applied:** `POL-E-ROOM-ROLLUP`, `POL-E-SLEEPING`, `POL-E-ROOM-KEY`

<a id="r-203"></a>
#### R-203 · BEDROOM 203 (room 203) · ❌ **Fail**

**Why:** The designated opening (W-10) fails, and no other window in the room could comply. Unless Exception 2 applies (an exit door to a public way), the room has no escape opening.

**Code:** IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13); IBC 1030.1 Exception 2 (code/section-1030-emergency-escape-and-rescue.md line 19)

| Read from the drawings | Value | Where |
|---|---|---|
| windows | `10 (L.H. CASM'T, egress 'Y'), 11 (FIXED, egress '')` | window-schedule.html, LOCATION 'BEDROOM 203' |

**Working:**

- scope: occupancy 'R-3' is listed in 1030.1 item 2; room 203 is on floor 2 (code analysis room numbering), below the fourth story above grade plane
- windows in this room: W-10, W-11
- designated egress: W-10 Fail
- other windows as candidates: W-11 cannot comply

**Would settle it:** Floor plans (PROJECT:FLOOR-PLANS, not provided) (Exception 2: exit door)

**Rules applied:** `POL-E-ROOM-ROLLUP`, `POL-E-SLEEPING`, `POL-E-ROOM-KEY`, `POL-E-EXCEPTION-2`

<a id="r-205"></a>
#### R-205 · BEDROOM 205 (room 205) · ❓ **Could Not Evaluate**

**Why:** W-12 could not be evaluated; W-13 fails. The room has a complying opening only if it is shown to comply.

**Code:** IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13)

| Read from the drawings | Value | Where |
|---|---|---|
| windows | `12 (S.H., egress 'Y'), 13 (FIXED, egress 'Y')` | window-schedule.html, LOCATION 'BEDRROM 205', 'BEDROOM 205' |

**Working:**

- scope: occupancy 'R-3' is listed in 1030.1 item 2; room 205 is on floor 2 (code analysis room numbering), below the fourth story above grade plane
- windows in this room: W-12, W-13
- designated egress: W-12 Could Not Evaluate, W-13 Fail

**Flags:**

- ⚠️ one room number, several spellings: 'BEDRROM 205', 'BEDROOM 205' (POL-E-ROOM-KEY)
- ⚠️ room name 'BEDRROM' is one character from 'BEDROOM'; read as a sleeping room (likely OCR damage; confirm on the floor plan)

**Would settle it:** Window type details (PROJECT:WINDOW-DETAILS, not provided) or Elevations (PROJECT:ELEVATIONS, not provided); Floor plans (PROJECT:FLOOR-PLANS, not provided) or site plan

**Rules applied:** `POL-E-ROOM-ROLLUP`, `POL-E-SLEEPING`, `POL-E-ROOM-KEY`

<a id="r-301"></a>
#### R-301 · BEDROOM 301 (room 301) · ❌ **Fail**

**Why:** The designated opening (W-20) fails, and no other window in the room could comply. Unless Exception 2 applies (an exit door to a public way), the room has no escape opening.

**Code:** IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13); IBC 1030.1 Exception 2 (code/section-1030-emergency-escape-and-rescue.md line 19)

| Read from the drawings | Value | Where |
|---|---|---|
| windows | `20 (L.H. CASM'T, egress 'Y')` | window-schedule.html, LOCATION 'BEDROOM 301' |

**Working:**

- scope: occupancy 'R-3' is listed in 1030.1 item 2; room 301 is on floor 3 (code analysis room numbering), below the fourth story above grade plane
- windows in this room: W-20
- designated egress: W-20 Fail
- other windows as candidates: none

**Would settle it:** Floor plans (PROJECT:FLOOR-PLANS, not provided) (Exception 2: exit door)

**Rules applied:** `POL-E-ROOM-ROLLUP`, `POL-E-SLEEPING`, `POL-E-ROOM-KEY`, `POL-E-EXCEPTION-2`

<a id="r-303"></a>
#### R-303 · GUEST BED 303 (room 303) · ❓ **Could Not Evaluate**

**Why:** No window is designated as the escape opening; W-21 could comply at nominal size but is not marked egress. Ask the architect to designate a complying opening.

**Code:** IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13)

| Read from the drawings | Value | Where |
|---|---|---|
| windows | `21 (L.H. CASM'T, egress '')` | window-schedule.html, LOCATION 'GUEST BED 303' |

**Working:**

- scope: occupancy 'R-3' is listed in 1030.1 item 2; room 303 is on floor 3 (code analysis room numbering), below the fourth story above grade plane
- windows in this room: W-21
- designated egress: none
- other windows as candidates: W-21 could comply

**Flags:**

- ⚠️ No window is designated as the escape opening; W-21 could comply at nominal size but is not marked egress. Ask the architect to designate a complying opening.

**Would settle it:** Window type details (PROJECT:WINDOW-DETAILS, not provided)

**Rules applied:** `POL-E-ROOM-ROLLUP`, `POL-E-SLEEPING`, `POL-E-ROOM-KEY`

### Egress windows

<a id="w-1"></a>
#### W-1 · Window 1, BEDROOM 101 · ❓ **Could Not Evaluate**

**Why:** Nothing fails at nominal size. Not settled by the schedule: net clear area (nominal 10.00 sq ft is only an upper bound); clear height; clear width; sill height (frame sill 32 in (2'-8")). Also unverified (never on a schedule): hardware, screens, public way.

**Code:** IBC 1030.1.1 (code/section-1030-emergency-escape-and-rescue.md line 31); IBC 1030.2 (code/section-1030-emergency-escape-and-rescue.md line 35); IBC 1030.2 Exception (code/section-1030-emergency-escape-and-rescue.md line 37); IBC 1030.2.1 (code/section-1030-emergency-escape-and-rescue.md line 41); IBC 1030.3 (code/section-1030-emergency-escape-and-rescue.md line 45); IBC 1030.5 (code/section-1030-emergency-escape-and-rescue.md line 49); IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13)

| Read from the drawings | Value | Where |
|---|---|---|
| SYMBOL (mark) | `1` | window-schedule.html row 3 |
| LOCATION (room) | `BEDROOM 101` | window-schedule.html row 3 |
| NOMINAL SIZE / WIDTH (width) | `2' - 6"` | window-schedule.html row 3 |
| NOMINAL SIZE / HEIGHT (height) | `4' - 0"` | window-schedule.html row 3 |
| TYPE (operation) | `L.H. CASM'T` | window-schedule.html row 3 |
| TYPE (type mark) | `A` | window-schedule.html row 3 |
| HEAD HEIGHT (head height) | `6' - 8"` | window-schedule.html row 3 |
| EGRESS (egress) | `Y` | window-schedule.html row 3 |
| SCREE N (screen) | `Y` | window-schedule.html row 3 |

| Requirement | Read / derived | Result | Why | Code |
|---|---|---|---|---|
| Opens by normal operation | type "L.H. CASM'T" (casement) | ✅ Pass | the scheduled type opens | IBC 1030.1.1 (code/section-1030-emergency-escape-and-rescue.md line 31) |
| Net clear opening >= 5.7 sq ft (5 if grade-floor) | nominal 30 in x 48 in = 1440 sq in = 10.00 sq ft (upper bound) | ❓ Could Not Evaluate | the nominal size exceeds 5.7 sq ft, but the net clear opening is smaller by the frame and is not given | IBC 1030.2 (code/section-1030-emergency-escape-and-rescue.md line 35); IBC 1030.2 Exception (code/section-1030-emergency-escape-and-rescue.md line 37) |
| Net clear height >= 24 in | nominal height '4\' - 0"' = 48 in (upper bound) | ❓ Could Not Evaluate | nominal 48 in exceeds 24 in; the clear height is smaller by the frame and is not given | IBC 1030.2.1 (code/section-1030-emergency-escape-and-rescue.md line 41) |
| Net clear width >= 20 in | nominal width '2\' - 6"' = 30 in (upper bound) | ❓ Could Not Evaluate | nominal 30 in exceeds 20 in; the clear width is smaller by the frame and is not given | IBC 1030.2.1 (code/section-1030-emergency-escape-and-rescue.md line 41) |
| Bottom of clear opening <= 44 in above the floor | derived frame sill = head height 80 in - nominal height 48 in = 32 in (2'-8") | ❓ Could Not Evaluate | the frame sill is 32 in (12 in below the limit), but the clear opening's bottom sits higher by the bottom frame, which is not given | IBC 1030.3 (code/section-1030-emergency-escape-and-rescue.md line 45) |
| Operable from inside without keys or tools | hardware not scheduled | ❓ Could Not Evaluate | not shown on the schedule | IBC 1030.1.1 (code/section-1030-emergency-escape-and-rescue.md line 31) |
| Screens, bars or grilles release from inside | SCREEN column 'Y' | ❓ Could Not Evaluate | a screen is scheduled; whether it releases from inside is not shown | IBC 1030.5 (code/section-1030-emergency-escape-and-rescue.md line 49) |
| Opens onto a public way, yard or court | not on the schedule | ❓ Could Not Evaluate | the window's location on the site is not shown | IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13) |

**Working:**

- scope: occupancy 'R-3' is listed in 1030.1 item 2 (IBC 1030.1 item 2 (code/section-1030-emergency-escape-and-rescue.md line 11)); room 101 is on floor 1 (code analysis room numbering), below the fourth story above grade plane (IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13))

**Would settle it:** Window type details (PROJECT:WINDOW-DETAILS, not provided) or Elevations (PROJECT:ELEVATIONS, not provided); Floor plans (PROJECT:FLOOR-PLANS, not provided) or site plan

**Rules applied:** `POL-E-NOMINAL-UPPER`, `POL-E-GRADE-FLOOR`, `POL-E-NO-FRAME-ASSUMPTION`, `POL-E-SILL-LOWER`, `POL-E-UNSEEN`, `POL-E-SCOPE`

<a id="w-3"></a>
#### W-3 · Window 3, BEDROOM 101 · ❓ **Could Not Evaluate**

**Why:** Nothing fails at nominal size. Not settled by the schedule: net clear area (nominal 10.00 sq ft is only an upper bound); clear height; clear width; sill height (frame sill 32 in (2'-8")). Also unverified (never on a schedule): hardware, screens, public way.

**Code:** IBC 1030.1.1 (code/section-1030-emergency-escape-and-rescue.md line 31); IBC 1030.2 (code/section-1030-emergency-escape-and-rescue.md line 35); IBC 1030.2 Exception (code/section-1030-emergency-escape-and-rescue.md line 37); IBC 1030.2.1 (code/section-1030-emergency-escape-and-rescue.md line 41); IBC 1030.3 (code/section-1030-emergency-escape-and-rescue.md line 45); IBC 1030.5 (code/section-1030-emergency-escape-and-rescue.md line 49); IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13)

| Read from the drawings | Value | Where |
|---|---|---|
| SYMBOL (mark) | `3` | window-schedule.html row 5 |
| LOCATION (room) | `BEDROOM 101` | window-schedule.html row 5 |
| NOMINAL SIZE / WIDTH (width) | `2' - 6"` | window-schedule.html row 5 |
| NOMINAL SIZE / HEIGHT (height) | `4' - 0"` | window-schedule.html row 5 |
| TYPE (operation) | `R.H. CASM'T` | window-schedule.html row 5 |
| TYPE (type mark) | `A` | window-schedule.html row 5 |
| HEAD HEIGHT (head height) | `6' - 8"` | window-schedule.html row 5 |
| EGRESS (egress) | `Y` | window-schedule.html row 5 |
| SCREE N (screen) | `Y` | window-schedule.html row 5 |

| Requirement | Read / derived | Result | Why | Code |
|---|---|---|---|---|
| Opens by normal operation | type "R.H. CASM'T" (casement) | ✅ Pass | the scheduled type opens | IBC 1030.1.1 (code/section-1030-emergency-escape-and-rescue.md line 31) |
| Net clear opening >= 5.7 sq ft (5 if grade-floor) | nominal 30 in x 48 in = 1440 sq in = 10.00 sq ft (upper bound) | ❓ Could Not Evaluate | the nominal size exceeds 5.7 sq ft, but the net clear opening is smaller by the frame and is not given | IBC 1030.2 (code/section-1030-emergency-escape-and-rescue.md line 35); IBC 1030.2 Exception (code/section-1030-emergency-escape-and-rescue.md line 37) |
| Net clear height >= 24 in | nominal height '4\' - 0"' = 48 in (upper bound) | ❓ Could Not Evaluate | nominal 48 in exceeds 24 in; the clear height is smaller by the frame and is not given | IBC 1030.2.1 (code/section-1030-emergency-escape-and-rescue.md line 41) |
| Net clear width >= 20 in | nominal width '2\' - 6"' = 30 in (upper bound) | ❓ Could Not Evaluate | nominal 30 in exceeds 20 in; the clear width is smaller by the frame and is not given | IBC 1030.2.1 (code/section-1030-emergency-escape-and-rescue.md line 41) |
| Bottom of clear opening <= 44 in above the floor | derived frame sill = head height 80 in - nominal height 48 in = 32 in (2'-8") | ❓ Could Not Evaluate | the frame sill is 32 in (12 in below the limit), but the clear opening's bottom sits higher by the bottom frame, which is not given | IBC 1030.3 (code/section-1030-emergency-escape-and-rescue.md line 45) |
| Operable from inside without keys or tools | hardware not scheduled | ❓ Could Not Evaluate | not shown on the schedule | IBC 1030.1.1 (code/section-1030-emergency-escape-and-rescue.md line 31) |
| Screens, bars or grilles release from inside | SCREEN column 'Y' | ❓ Could Not Evaluate | a screen is scheduled; whether it releases from inside is not shown | IBC 1030.5 (code/section-1030-emergency-escape-and-rescue.md line 49) |
| Opens onto a public way, yard or court | not on the schedule | ❓ Could Not Evaluate | the window's location on the site is not shown | IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13) |

**Working:**

- scope: occupancy 'R-3' is listed in 1030.1 item 2 (IBC 1030.1 item 2 (code/section-1030-emergency-escape-and-rescue.md line 11)); room 101 is on floor 1 (code analysis room numbering), below the fourth story above grade plane (IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13))

**Would settle it:** Window type details (PROJECT:WINDOW-DETAILS, not provided) or Elevations (PROJECT:ELEVATIONS, not provided); Floor plans (PROJECT:FLOOR-PLANS, not provided) or site plan

**Rules applied:** `POL-E-NOMINAL-UPPER`, `POL-E-GRADE-FLOOR`, `POL-E-NO-FRAME-ASSUMPTION`, `POL-E-SILL-LOWER`, `POL-E-UNSEEN`, `POL-E-SCOPE`

<a id="w-7"></a>
#### W-7 · Window 7, ADU BEDROOM 107 · ❓ **Could Not Evaluate**

**Why:** Nothing fails at nominal size. Not settled by the schedule: net clear area (nominal 7.50 sq ft is only an upper bound); clear height; clear width; sill height (frame sill 44 in (3'-8")). Also unverified (never on a schedule): hardware, screens, public way.

**Code:** IBC 1030.1.1 (code/section-1030-emergency-escape-and-rescue.md line 31); IBC 1030.2 (code/section-1030-emergency-escape-and-rescue.md line 35); IBC 1030.2 Exception (code/section-1030-emergency-escape-and-rescue.md line 37); IBC 1030.2.1 (code/section-1030-emergency-escape-and-rescue.md line 41); IBC 1030.3 (code/section-1030-emergency-escape-and-rescue.md line 45); IBC 1030.5 (code/section-1030-emergency-escape-and-rescue.md line 49); IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13)

| Read from the drawings | Value | Where |
|---|---|---|
| SYMBOL (mark) | `7` | window-schedule.html row 9 |
| LOCATION (room) | `ADU BEDROOM 107` | window-schedule.html row 9 |
| NOMINAL SIZE / WIDTH (width) | `2'-6"` | window-schedule.html row 9 |
| NOMINAL SIZE / HEIGHT (height) | `3' - 0"` | window-schedule.html row 9 |
| TYPE (operation) | `L.H. CASM'T` | window-schedule.html row 9 |
| TYPE (type mark) | `F` | window-schedule.html row 9 |
| HEAD HEIGHT (head height) | `6' - 8"` | window-schedule.html row 9 |
| EGRESS (egress) | `Y` | window-schedule.html row 9 |
| SCREE N (screen) | `Y` | window-schedule.html row 9 |

| Requirement | Read / derived | Result | Why | Code |
|---|---|---|---|---|
| Opens by normal operation | type "L.H. CASM'T" (casement) | ✅ Pass | the scheduled type opens | IBC 1030.1.1 (code/section-1030-emergency-escape-and-rescue.md line 31) |
| Net clear opening >= 5.7 sq ft (5 if grade-floor) | nominal 30 in x 36 in = 1080 sq in = 7.50 sq ft (upper bound) | ❓ Could Not Evaluate | the nominal size exceeds 5.7 sq ft, but the net clear opening is smaller by the frame and is not given | IBC 1030.2 (code/section-1030-emergency-escape-and-rescue.md line 35); IBC 1030.2 Exception (code/section-1030-emergency-escape-and-rescue.md line 37) |
| Net clear height >= 24 in | nominal height '3\' - 0"' = 36 in (upper bound) | ❓ Could Not Evaluate | nominal 36 in exceeds 24 in; the clear height is smaller by the frame and is not given | IBC 1030.2.1 (code/section-1030-emergency-escape-and-rescue.md line 41) |
| Net clear width >= 20 in | nominal width '2\'-6"' = 30 in (upper bound) | ❓ Could Not Evaluate | nominal 30 in exceeds 20 in; the clear width is smaller by the frame and is not given | IBC 1030.2.1 (code/section-1030-emergency-escape-and-rescue.md line 41) |
| Bottom of clear opening <= 44 in above the floor | derived frame sill = head height 80 in - nominal height 36 in = 44 in (3'-8") | ❓ Could Not Evaluate | the frame sill is 44 in (0 in below the limit), but the clear opening's bottom sits higher by the bottom frame, which is not given | IBC 1030.3 (code/section-1030-emergency-escape-and-rescue.md line 45) |
| Operable from inside without keys or tools | hardware not scheduled | ❓ Could Not Evaluate | not shown on the schedule | IBC 1030.1.1 (code/section-1030-emergency-escape-and-rescue.md line 31) |
| Screens, bars or grilles release from inside | SCREEN column 'Y' | ❓ Could Not Evaluate | a screen is scheduled; whether it releases from inside is not shown | IBC 1030.5 (code/section-1030-emergency-escape-and-rescue.md line 49) |
| Opens onto a public way, yard or court | not on the schedule | ❓ Could Not Evaluate | the window's location on the site is not shown | IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13) |

**Working:**

- scope: occupancy 'R-3' is listed in 1030.1 item 2 (IBC 1030.1 item 2 (code/section-1030-emergency-escape-and-rescue.md line 11)); room 107 is on floor 1 (code analysis room numbering), below the fourth story above grade plane (IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13))

**Would settle it:** Window type details (PROJECT:WINDOW-DETAILS, not provided) or Elevations (PROJECT:ELEVATIONS, not provided); Floor plans (PROJECT:FLOOR-PLANS, not provided) or site plan

**Rules applied:** `POL-E-NOMINAL-UPPER`, `POL-E-GRADE-FLOOR`, `POL-E-NO-FRAME-ASSUMPTION`, `POL-E-SILL-LOWER`, `POL-E-UNSEEN`, `POL-E-SCOPE`

<a id="w-10"></a>
#### W-10 · Window 10, BEDROOM 203 · ❌ **Fail**

**Why:** Net clear area: nominal 24 in x 30 in = 720 sq in = 5.00 sq ft (upper bound); the net clear opening is smaller than 5.00 sq ft, so below 5 and 5.7 sq ft whether or not it is a grade-floor opening. Sill height: derived frame sill = head height 80 in - nominal height 30 in = 50 in (4'-2"); the clear opening's bottom is at or above the 50 in frame sill, more than 44 in.

**Code:** IBC 1030.1.1 (code/section-1030-emergency-escape-and-rescue.md line 31); IBC 1030.2 (code/section-1030-emergency-escape-and-rescue.md line 35); IBC 1030.2 Exception (code/section-1030-emergency-escape-and-rescue.md line 37); IBC 1030.2.1 (code/section-1030-emergency-escape-and-rescue.md line 41); IBC 1030.3 (code/section-1030-emergency-escape-and-rescue.md line 45); IBC 1030.5 (code/section-1030-emergency-escape-and-rescue.md line 49); IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13)

| Read from the drawings | Value | Where |
|---|---|---|
| SYMBOL (mark) | `10` | window-schedule.html row 11 |
| LOCATION (room) | `BEDROOM 203` | window-schedule.html row 11 |
| NOMINAL SIZE / WIDTH (width) | `2' - 0"` | window-schedule.html row 11 |
| NOMINAL SIZE / HEIGHT (height) | `2' - 6"` | window-schedule.html row 11 |
| TYPE (operation) | `L.H. CASM'T` | window-schedule.html row 11 |
| TYPE (type mark) | `H` | window-schedule.html row 11 |
| HEAD HEIGHT (head height) | `6' - 8"` | window-schedule.html row 11 |
| EGRESS (egress) | `Y` | window-schedule.html row 11 |
| SCREE N (screen) | `Y` | window-schedule.html row 11 |

| Requirement | Read / derived | Result | Why | Code |
|---|---|---|---|---|
| Opens by normal operation | type "L.H. CASM'T" (casement) | ✅ Pass | the scheduled type opens | IBC 1030.1.1 (code/section-1030-emergency-escape-and-rescue.md line 31) |
| Net clear opening >= 5.7 sq ft (5 if grade-floor) | nominal 24 in x 30 in = 720 sq in = 5.00 sq ft (upper bound) | ❌ Fail | the net clear opening is smaller than 5.00 sq ft, so below 5 and 5.7 sq ft whether or not it is a grade-floor opening | IBC 1030.2 (code/section-1030-emergency-escape-and-rescue.md line 35); IBC 1030.2 Exception (code/section-1030-emergency-escape-and-rescue.md line 37) |
| Net clear height >= 24 in | nominal height '2\' - 6"' = 30 in (upper bound) | ❓ Could Not Evaluate | nominal 30 in exceeds 24 in; the clear height is smaller by the frame and is not given | IBC 1030.2.1 (code/section-1030-emergency-escape-and-rescue.md line 41) |
| Net clear width >= 20 in | nominal width '2\' - 0"' = 24 in (upper bound) | ❓ Could Not Evaluate | nominal 24 in exceeds 20 in; the clear width is smaller by the frame and is not given | IBC 1030.2.1 (code/section-1030-emergency-escape-and-rescue.md line 41) |
| Bottom of clear opening <= 44 in above the floor | derived frame sill = head height 80 in - nominal height 30 in = 50 in (4'-2") | ❌ Fail | the clear opening's bottom is at or above the 50 in frame sill, more than 44 in | IBC 1030.3 (code/section-1030-emergency-escape-and-rescue.md line 45) |
| Operable from inside without keys or tools | hardware not scheduled | ❓ Could Not Evaluate | not shown on the schedule | IBC 1030.1.1 (code/section-1030-emergency-escape-and-rescue.md line 31) |
| Screens, bars or grilles release from inside | SCREEN column 'Y' | ❓ Could Not Evaluate | a screen is scheduled; whether it releases from inside is not shown | IBC 1030.5 (code/section-1030-emergency-escape-and-rescue.md line 49) |
| Opens onto a public way, yard or court | not on the schedule | ❓ Could Not Evaluate | the window's location on the site is not shown | IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13) |

**Working:**

- scope: occupancy 'R-3' is listed in 1030.1 item 2 (IBC 1030.1 item 2 (code/section-1030-emergency-escape-and-rescue.md line 11)); room 203 is on floor 2 (code analysis room numbering), below the fourth story above grade plane (IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13))

**Would settle it:** Window type details (PROJECT:WINDOW-DETAILS, not provided); Floor plans (PROJECT:FLOOR-PLANS, not provided) or site plan

**Rules applied:** `POL-E-NOMINAL-UPPER`, `POL-E-GRADE-FLOOR`, `POL-E-NO-FRAME-ASSUMPTION`, `POL-E-SILL-LOWER`, `POL-E-UNSEEN`, `POL-E-SCOPE`

<a id="w-12"></a>
#### W-12 · Window 12, BEDRROM 205 · ❓ **Could Not Evaluate**

**Why:** Nothing fails at nominal size. Not settled by the schedule: net clear area (nominal 12.00 sq ft is only an upper bound); clear height; clear width; sill height (frame sill 32 in (2'-8")). Also unverified (never on a schedule): hardware, screens, public way.

**Code:** IBC 1030.1.1 (code/section-1030-emergency-escape-and-rescue.md line 31); IBC 1030.2 (code/section-1030-emergency-escape-and-rescue.md line 35); IBC 1030.2 Exception (code/section-1030-emergency-escape-and-rescue.md line 37); IBC 1030.2.1 (code/section-1030-emergency-escape-and-rescue.md line 41); IBC 1030.3 (code/section-1030-emergency-escape-and-rescue.md line 45); IBC 1030.5 (code/section-1030-emergency-escape-and-rescue.md line 49); IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13)

| Read from the drawings | Value | Where |
|---|---|---|
| SYMBOL (mark) | `12` | window-schedule.html row 13 |
| LOCATION (room) | `BEDRROM 205` | window-schedule.html row 13 |
| NOMINAL SIZE / WIDTH (width) | `3' - 0"` | window-schedule.html row 13 |
| NOMINAL SIZE / HEIGHT (height) | `4' - 0"` | window-schedule.html row 13 |
| TYPE (operation) | `S.H.` | window-schedule.html row 13 |
| TYPE (type mark) | `J` | window-schedule.html row 13 |
| HEAD HEIGHT (head height) | `6' - 8"` | window-schedule.html row 13 |
| EGRESS (egress) | `Y` | window-schedule.html row 13 |
| SCREE N (screen) | `Y` | window-schedule.html row 13 |

| Requirement | Read / derived | Result | Why | Code |
|---|---|---|---|---|
| Opens by normal operation | type 'S.H.' (single hung) | ✅ Pass | the scheduled type opens | IBC 1030.1.1 (code/section-1030-emergency-escape-and-rescue.md line 31) |
| Net clear opening >= 5.7 sq ft (5 if grade-floor) | nominal 36 in x 48 in = 1728 sq in = 12.00 sq ft (upper bound) | ❓ Could Not Evaluate | the nominal size exceeds 5.7 sq ft, but the net clear opening is smaller by the frame and is not given. Note only: only the bottom sash opens, roughly 6.00 sq ft (POL-E-PARTIAL-OPENING) | IBC 1030.2 (code/section-1030-emergency-escape-and-rescue.md line 35); IBC 1030.2 Exception (code/section-1030-emergency-escape-and-rescue.md line 37) |
| Net clear height >= 24 in | nominal height '4\' - 0"' = 48 in (upper bound) | ❓ Could Not Evaluate | nominal 48 in exceeds 24 in; the clear height is smaller by the frame and is not given. Note only: only the bottom sash opens, roughly 24 in (POL-E-PARTIAL-OPENING) | IBC 1030.2.1 (code/section-1030-emergency-escape-and-rescue.md line 41) |
| Net clear width >= 20 in | nominal width '3\' - 0"' = 36 in (upper bound) | ❓ Could Not Evaluate | nominal 36 in exceeds 20 in; the clear width is smaller by the frame and is not given | IBC 1030.2.1 (code/section-1030-emergency-escape-and-rescue.md line 41) |
| Bottom of clear opening <= 44 in above the floor | derived frame sill = head height 80 in - nominal height 48 in = 32 in (2'-8") | ❓ Could Not Evaluate | the frame sill is 32 in (12 in below the limit), but the clear opening's bottom sits higher by the bottom frame, which is not given | IBC 1030.3 (code/section-1030-emergency-escape-and-rescue.md line 45) |
| Operable from inside without keys or tools | hardware not scheduled | ❓ Could Not Evaluate | not shown on the schedule | IBC 1030.1.1 (code/section-1030-emergency-escape-and-rescue.md line 31) |
| Screens, bars or grilles release from inside | SCREEN column 'Y' | ❓ Could Not Evaluate | a screen is scheduled; whether it releases from inside is not shown | IBC 1030.5 (code/section-1030-emergency-escape-and-rescue.md line 49) |
| Opens onto a public way, yard or court | not on the schedule | ❓ Could Not Evaluate | the window's location on the site is not shown | IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13) |

**Working:**

- scope: occupancy 'R-3' is listed in 1030.1 item 2 (IBC 1030.1 item 2 (code/section-1030-emergency-escape-and-rescue.md line 11)); room 205 is on floor 2 (code analysis room numbering), below the fourth story above grade plane (IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13))

**Flags:**

- ⚠️ room name 'BEDRROM' is one character from 'BEDROOM'; read as a sleeping room (likely OCR damage; confirm on the floor plan)

**Would settle it:** Window type details (PROJECT:WINDOW-DETAILS, not provided) or Elevations (PROJECT:ELEVATIONS, not provided); Floor plans (PROJECT:FLOOR-PLANS, not provided) or site plan

**Rules applied:** `POL-E-NOMINAL-UPPER`, `POL-E-GRADE-FLOOR`, `POL-E-NO-FRAME-ASSUMPTION`, `POL-E-PARTIAL-OPENING`, `POL-E-SILL-LOWER`, `POL-E-UNSEEN`, `POL-E-SCOPE`

<a id="w-13"></a>
#### W-13 · Window 13, BEDROOM 205 · ❌ **Fail**

**Why:** Opening type: type 'FIXED' (fixed); a fixed window does not open. Net clear area: fixed: no opening; no net clear opening results from normal operation.

**Code:** IBC 1030.1.1 (code/section-1030-emergency-escape-and-rescue.md line 31); IBC 1030.2.1 (code/section-1030-emergency-escape-and-rescue.md line 41); IBC 1030.2 (code/section-1030-emergency-escape-and-rescue.md line 35); IBC 1030.2 Exception (code/section-1030-emergency-escape-and-rescue.md line 37); IBC 1030.2.1 (code/section-1030-emergency-escape-and-rescue.md line 41); IBC 1030.3 (code/section-1030-emergency-escape-and-rescue.md line 45); IBC 1030.5 (code/section-1030-emergency-escape-and-rescue.md line 49); IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13)

| Read from the drawings | Value | Where |
|---|---|---|
| SYMBOL (mark) | `13` | window-schedule.html row 14 |
| LOCATION (room) | `BEDROOM 205` | window-schedule.html row 14 |
| NOMINAL SIZE / WIDTH (width) | `4' - 0"` | window-schedule.html row 14 |
| NOMINAL SIZE / HEIGHT (height) | `4' - 0"` | window-schedule.html row 14 |
| TYPE (operation) | `FIXED` | window-schedule.html row 14 |
| TYPE (type mark) | `K` | window-schedule.html row 14 |
| HEAD HEIGHT (head height) | `6' - 8"` | window-schedule.html row 14 |
| EGRESS (egress) | `Y` | window-schedule.html row 14 |
| SCREE N (screen) | `` | window-schedule.html row 14 |

| Requirement | Read / derived | Result | Why | Code |
|---|---|---|---|---|
| Opens by normal operation | type 'FIXED' (fixed) | ❌ Fail | a fixed window does not open | IBC 1030.1.1 (code/section-1030-emergency-escape-and-rescue.md line 31); IBC 1030.2.1 (code/section-1030-emergency-escape-and-rescue.md line 41) |
| Net clear opening >= 5.7 sq ft (5 if grade-floor) | fixed: no opening | ❌ Fail | no net clear opening results from normal operation | IBC 1030.2 (code/section-1030-emergency-escape-and-rescue.md line 35); IBC 1030.2 Exception (code/section-1030-emergency-escape-and-rescue.md line 37); IBC 1030.2.1 (code/section-1030-emergency-escape-and-rescue.md line 41) |
| Bottom of clear opening <= 44 in above the floor | derived frame sill = head height 80 in - nominal height 48 in = 32 in (2'-8") | ❓ Could Not Evaluate | the frame sill is 32 in (12 in below the limit), but the clear opening's bottom sits higher by the bottom frame, which is not given | IBC 1030.3 (code/section-1030-emergency-escape-and-rescue.md line 45) |
| Screens, bars or grilles release from inside | SCREEN column '' | ❓ Could Not Evaluate | no screen scheduled; any device fitted must release from inside | IBC 1030.5 (code/section-1030-emergency-escape-and-rescue.md line 49) |
| Opens onto a public way, yard or court | not on the schedule | ❓ Could Not Evaluate | the window's location on the site is not shown | IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13) |

**Working:**

- scope: occupancy 'R-3' is listed in 1030.1 item 2 (IBC 1030.1 item 2 (code/section-1030-emergency-escape-and-rescue.md line 11)); room 205 is on floor 2 (code analysis room numbering), below the fourth story above grade plane (IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13))

**Would settle it:** Window type details (PROJECT:WINDOW-DETAILS, not provided) or Elevations (PROJECT:ELEVATIONS, not provided); Floor plans (PROJECT:FLOOR-PLANS, not provided) or site plan

**Rules applied:** `POL-E-FIXED`, `POL-E-SILL-LOWER`, `POL-E-UNSEEN`, `POL-E-SCOPE`

<a id="w-20"></a>
#### W-20 · Window 20, BEDROOM 301 · ❌ **Fail**

**Why:** Sill height: derived frame sill = head height 96 in - nominal height 36 in = 60 in (5'-0"); the clear opening's bottom is at or above the 60 in frame sill, more than 44 in.

**Code:** IBC 1030.1.1 (code/section-1030-emergency-escape-and-rescue.md line 31); IBC 1030.2 (code/section-1030-emergency-escape-and-rescue.md line 35); IBC 1030.2 Exception (code/section-1030-emergency-escape-and-rescue.md line 37); IBC 1030.2.1 (code/section-1030-emergency-escape-and-rescue.md line 41); IBC 1030.3 (code/section-1030-emergency-escape-and-rescue.md line 45); IBC 1030.5 (code/section-1030-emergency-escape-and-rescue.md line 49); IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13)

| Read from the drawings | Value | Where |
|---|---|---|
| SYMBOL (mark) | `20` | window-schedule.html row 16 |
| LOCATION (room) | `BEDROOM 301` | window-schedule.html row 16 |
| NOMINAL SIZE / WIDTH (width) | `2' - 6"` | window-schedule.html row 16 |
| NOMINAL SIZE / HEIGHT (height) | `3' - 0"` | window-schedule.html row 16 |
| TYPE (operation) | `L.H. CASM'T` | window-schedule.html row 16 |
| TYPE (type mark) | `F` | window-schedule.html row 16 |
| HEAD HEIGHT (head height) | `8' - 0"` | window-schedule.html row 16 |
| EGRESS (egress) | `Y` | window-schedule.html row 16 |
| SCREE N (screen) | `Y` | window-schedule.html row 16 |

| Requirement | Read / derived | Result | Why | Code |
|---|---|---|---|---|
| Opens by normal operation | type "L.H. CASM'T" (casement) | ✅ Pass | the scheduled type opens | IBC 1030.1.1 (code/section-1030-emergency-escape-and-rescue.md line 31) |
| Net clear opening >= 5.7 sq ft (5 if grade-floor) | nominal 30 in x 36 in = 1080 sq in = 7.50 sq ft (upper bound) | ❓ Could Not Evaluate | the nominal size exceeds 5.7 sq ft, but the net clear opening is smaller by the frame and is not given | IBC 1030.2 (code/section-1030-emergency-escape-and-rescue.md line 35); IBC 1030.2 Exception (code/section-1030-emergency-escape-and-rescue.md line 37) |
| Net clear height >= 24 in | nominal height '3\' - 0"' = 36 in (upper bound) | ❓ Could Not Evaluate | nominal 36 in exceeds 24 in; the clear height is smaller by the frame and is not given | IBC 1030.2.1 (code/section-1030-emergency-escape-and-rescue.md line 41) |
| Net clear width >= 20 in | nominal width '2\' - 6"' = 30 in (upper bound) | ❓ Could Not Evaluate | nominal 30 in exceeds 20 in; the clear width is smaller by the frame and is not given | IBC 1030.2.1 (code/section-1030-emergency-escape-and-rescue.md line 41) |
| Bottom of clear opening <= 44 in above the floor | derived frame sill = head height 96 in - nominal height 36 in = 60 in (5'-0") | ❌ Fail | the clear opening's bottom is at or above the 60 in frame sill, more than 44 in | IBC 1030.3 (code/section-1030-emergency-escape-and-rescue.md line 45) |
| Operable from inside without keys or tools | hardware not scheduled | ❓ Could Not Evaluate | not shown on the schedule | IBC 1030.1.1 (code/section-1030-emergency-escape-and-rescue.md line 31) |
| Screens, bars or grilles release from inside | SCREEN column 'Y' | ❓ Could Not Evaluate | a screen is scheduled; whether it releases from inside is not shown | IBC 1030.5 (code/section-1030-emergency-escape-and-rescue.md line 49) |
| Opens onto a public way, yard or court | not on the schedule | ❓ Could Not Evaluate | the window's location on the site is not shown | IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13) |

**Working:**

- scope: occupancy 'R-3' is listed in 1030.1 item 2 (IBC 1030.1 item 2 (code/section-1030-emergency-escape-and-rescue.md line 11)); room 301 is on floor 3 (code analysis room numbering), below the fourth story above grade plane (IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13))

**Would settle it:** Window type details (PROJECT:WINDOW-DETAILS, not provided); Floor plans (PROJECT:FLOOR-PLANS, not provided) or site plan

**Rules applied:** `POL-E-NOMINAL-UPPER`, `POL-E-GRADE-FLOOR`, `POL-E-NO-FRAME-ASSUMPTION`, `POL-E-SILL-LOWER`, `POL-E-UNSEEN`, `POL-E-SCOPE`

### Windows not evaluated (Not Applicable)

| ID | Window | Why | Flags |
|---|---|---|---|
| <a id="w-2"></a>W-2 | Window 2, BEDROOM 101 | Not marked egress; 1030 needs one complying opening per sleeping room, not every window. Considered in R-101. |  |
| <a id="w-4"></a>W-4 | Window 4, OFFICE 102 | 'OFFICE 102' is not clearly a sleeping room (flagged for review); 1030.1 requires escape openings in sleeping rooms. | ⚠️ 'OFFICE' rooms are sometimes used for sleeping; not treated as a sleeping room. Confirm the use on the floor plan.; ⚠️ inches 'O' read as '0' (a letter where a digit belongs; OCR damage) |
| <a id="w-5"></a>W-5 | Window 5, LIVING 103 | 'LIVING 103' is not a sleeping room; 1030.1 requires escape openings in sleeping rooms. |  |
| <a id="w-6"></a>W-6 | Window 6, KITCHEN 104 | 'KITCHEN 104' is not a sleeping room; 1030.1 requires escape openings in sleeping rooms. |  |
| <a id="w-8"></a>W-8 | Window 8, LAUNDRY 108 | 'LAUNDRY 108' is not a sleeping room; 1030.1 requires escape openings in sleeping rooms. |  |
| <a id="w-11"></a>W-11 | Window 11, BEDROOM 203 | Not marked egress; 1030 needs one complying opening per sleeping room, not every window. Considered in R-203. |  |
| <a id="w-14"></a>W-14 | Window 14, BATH 206 | 'BATH 206' is not a sleeping room; 1030.1 requires escape openings in sleeping rooms. |  |
| <a id="w-21"></a>W-21 | Window 21, GUEST BED 303 | Not marked egress; 1030 needs one complying opening per sleeping room, not every window. Considered in R-303. |  |
| <a id="w-22"></a>W-22 | Window 22, HALL 302 | 'HALL 302' is not a sleeping room; 1030.1 requires escape openings in sleeping rooms. |  |
| <a id="w-23"></a>W-23 | Window 23, STAIR S1 | 'STAIR S1' is not a sleeping room; 1030.1 requires escape openings in sleeping rooms. |  |

## What this report could not check

| Document | Would settle |
|---|---|
| Building sections / roof plan (PROJECT:BUILDING-SECTIONS, not provided) | [H-1](#h-1) |
| Civil sheet C1.0 (grade plane) (PROJECT:C1.0:CIVIL, not provided) | [H-1](#h-1) |
| Chapters 4 and 5 (height exceptions) (IBC:2018:CH4-CH5, not provided; related through footnote a) | [H-1](#h-1) |
| Automatic Sprinkler Systems (903.2, 903.3.1.1-903.3.1.3) (IBC:2018:903, not provided; related through footnote h) | [H-1](#h-1) |
| Window type details (PROJECT:WINDOW-DETAILS, not provided) | [R-101](#r-101), [R-107](#r-107), [R-205](#r-205), [R-303](#r-303), [W-1](#w-1), [W-3](#w-3), [W-7](#w-7), [W-10](#w-10), [W-12](#w-12), [W-13](#w-13), [W-20](#w-20) |
| Window type details (PROJECT:WINDOW-DETAILS, not provided) or Elevations (PROJECT:ELEVATIONS, not provided) | [R-101](#r-101), [R-107](#r-107), [R-205](#r-205), [W-1](#w-1), [W-3](#w-3), [W-7](#w-7), [W-12](#w-12), [W-13](#w-13) |
| Floor plans (PROJECT:FLOOR-PLANS, not provided) or site plan | [R-101](#r-101), [R-107](#r-107), [R-205](#r-205), [W-1](#w-1), [W-3](#w-3), [W-7](#w-7), [W-10](#w-10), [W-12](#w-12), [W-13](#w-13), [W-20](#w-20) |
| Floor plans (PROJECT:FLOOR-PLANS, not provided) (Exception 2: exit door) | [R-203](#r-203), [R-301](#r-301) |

## Rules the tool applied

Judgement calls are named rules, the same for every project. A finding lists the rules it used. Rules that did not come up for this project are listed after, for reference.

| Rule | Used here | What it says | Rests on |
|---|---|---|---|
| `POL-H-STATED-HEIGHT` The stated height is used as submitted | yes | The building height is the architect's figure. The tool compares it with the table; it cannot check the measurement (grade plane and roof heights are on sheets not provided), and says so. | IBC 202 HEIGHT, BUILDING (code/section-1030-emergency-escape-and-rescue.md line 59) (project_decision) |
| `POL-H-INTERPRETATION` Brief rules may support a verdict, disclosed | yes | A mapping that rests on the challenge brief rather than code text (R-3 read as row R, because IBC 310 is not provided) may support a Pass or Fail, but the finding names it as an interpretation. The limit value itself always comes from code text. | Challenge brief (instructions/README.md line 54) (challenge_brief) |
| `POL-H-SPRINKLER-COVERAGE` Sprinkler coverage must be 'throughout' | yes | S, S13R and S13D are for buildings 'equipped throughout'. Wording that says partial coverage resolves to no sub-row (Could Not Evaluate). Wording that names a standard but not 'throughout' is resolved and flagged. | Table 504.3 legend (code/table-504.3-notes.md line 15) (code_text) |
| `POL-H-FOOTNOTES` Footnotes are cited; pointed-to documents are listed, not assumed | yes | Every footnote on the looked-up cell is quoted in the finding. Where a footnote points to a document we don't have (Chapters 4 and 5 exceptions, IBC 903.2.8), the finding lists it as not provided. It does not block the verdict: an exception has to be claimed by the applicant, and the finding says which claims the code analysis makes. | Table 504.3 footnotes (code/table-504.3-notes.md lines 19-33) (project_decision) |
| `POL-H-ARCHITECT` The architect's allowable height is checked, not trusted | yes | If the code analysis states an allowable height that differs from the looked-up cell, the finding flags it and lists the cells in the same row and column that hold the architect's figure, as a likely explanation. The verdict uses the looked-up cell. | brief: the allowable height 'is worth checking against the table rather than trusting' (challenge_brief) |
| `POL-E-ROOM-ROLLUP` Room verdict (decision 3) | yes | A sleeping room Passes if a designated egress window Passes, and is Could Not Evaluate if one is Could Not Evaluate. If none is designated, or every designated one Fails, the room's other windows are evaluated as candidates: if any could comply the room is Could Not Evaluate, flagged 'no complying opening designated'; if none could, the room Fails. | IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13); src/NOTES.md, Plan from here: open decisions #3 (project_decision) |
| `POL-E-SLEEPING` What counts as a sleeping room | yes | Room names with a bedroom word (BEDROOM, BED, BDRM, GUEST BED ...) are sleeping rooms, including a word one character from BEDROOM (OCR), which is flagged. Dens, offices, lofts and unrecognised names are ambiguous: not treated as sleeping rooms, but listed for the plan checker to confirm. | Challenge brief (instructions/README.md line 60); Challenge brief (instructions/README.md line 60) (challenge_brief) |
| `POL-E-ROOM-KEY` Room identity | yes | Windows belong to the same room when their location has the same room number ('BEDROM 12' and 'BEDROOM 12'); without a number, when the names match. Different spellings under one number are flagged. | window schedule LOCATION column (project_decision) |
| `POL-E-EXCEPTION-2` Exit-door exception is not assumed | yes | A room Fail says 'unless Exception 2 applies (an exit door to a public way)'. The floor plans would settle it; the tool does not assume a door it can't see. | IBC 1030.1 Exception 2 (code/section-1030-emergency-escape-and-rescue.md line 19) (code_text) |
| `POL-E-NOMINAL-UPPER` Nominal size is an upper bound | yes | The net clear opening (area, width and height) is always smaller than the nominal size. A nominal value at or below a minimum proves a Fail; a nominal value above it proves nothing. | Challenge brief (instructions/README.md line 63); IBC 1030.2 (code/section-1030-emergency-escape-and-rescue.md line 35); IBC 1030.2.1 (code/section-1030-emergency-escape-and-rescue.md line 41) (challenge_brief) |
| `POL-E-GRADE-FLOOR` Grade-floor limit (decision 4) | yes | Whether an opening is a grade-floor opening needs the finished ground level, which these sheets don't give. The area is decided only when the 5.0 and 5.7 sq ft limits give the same result. | IBC 1030.2 Exception (code/section-1030-emergency-escape-and-rescue.md line 37); IBC 202 GRADE FLOOR OPENING (code/section-1030-emergency-escape-and-rescue.md line 55); src/NOTES.md, Plan from here: open decisions #4 (code_text) |
| `POL-E-NO-FRAME-ASSUMPTION` No frame-deduction assumption (decision 2) | yes | The tool assumes no frame size, so nominal size never proves a Pass. Without a net clear opening (from the schedule or manufacturer data) a minimum is Could Not Evaluate, with the nominal upper bound shown. | src/NOTES.md, Plan from here: open decisions #2 (project_decision) |
| `POL-E-SILL-LOWER` A derived sill is a lower bound | yes | Sill = head height - nominal height (head height is floor to top of window). The bottom of the clear opening is at or above that frame sill. A frame sill above 44 in proves a Fail; at or below 44 in it proves nothing, because the bottom frame depth is unknown. A scheduled sill height is treated the same way unless the column says it is to the clear opening. | IBC 1030.3 (code/section-1030-emergency-escape-and-rescue.md line 45); Challenge brief (instructions/README.md line 64) (code_text) |
| `POL-E-UNSEEN` Requirements no schedule shows | yes | Operation without keys or tools, releasable screens and opening onto a public way, yard or court are each a Could Not Evaluate line on every egress window, naming the document that would settle it. They never cause a Fail; they do keep a window from a Pass. | IBC 1030.1.1 (code/section-1030-emergency-escape-and-rescue.md line 31); IBC 1030.5 (code/section-1030-emergency-escape-and-rescue.md line 49); IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13) (code_text) |
| `POL-E-SCOPE` Which buildings and floors 1030 covers | yes | R-3 and R-4: applies. R-2: Could Not Evaluate unless the exits per story are known. Other groups: Not Applicable. Sleeping rooms must be below the fourth story above grade plane; the story comes from the code analysis room numbering (floor n read as story n above grade plane), else from the number of stories. Unknown story: Could Not Evaluate. | IBC 1030.1 item 2 (code/section-1030-emergency-escape-and-rescue.md line 11); IBC 1030.1 item 1 (code/section-1030-emergency-escape-and-rescue.md line 9); IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13) (code_text) |
| `POL-E-NOT-DESIGNATED` Sleeping-room windows not marked egress | yes | Not Applicable as a window finding: 1030 needs one complying opening per sleeping room, not every window. They are still considered in the room finding. | IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13) (code_text) |
| `POL-E-NOT-SLEEPING` Windows outside sleeping rooms | yes | Windows in rooms that are not sleeping rooms are Not Applicable. A window in such a room that is marked egress is noted. | IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13) (code_text) |
| `POL-E-PARTIAL-OPENING` Single hung and slider bounds are notes only (decision 5) | yes | A single hung opens only its bottom sash and a slider about half its width. The tool shows the half-size figure as a labelled note, never as proof of a Fail, because panel splits vary (a three-panel slider opens two thirds; sashes can be unequal). | Challenge brief (instructions/README.md line 66); src/NOTES.md, Plan from here: open decisions #5 (challenge_brief) |
| `POL-E-FIXED` A fixed window is not an escape opening | yes | A window scheduled as fixed does not open, so it can't be operated from inside and has no net clear opening by normal operation: Fail. | IBC 1030.1.1 (code/section-1030-emergency-escape-and-rescue.md line 31); IBC 1030.2.1 (code/section-1030-emergency-escape-and-rescue.md line 41) (code_text) |
| `POL-GEN-AMENDMENTS` Local amendments not provided | yes | The project is reviewed against the 2018 IBC as printed. If the manifest lists local amendments as not provided, every verdict is conditional on them and the report says so once, at the top. | the local-amendments document listed in the manifest (unavailable) (project_decision) |
| `POL-GEN-OCR` OCR-repaired values never decide a verdict alone | no | A value the reader had to repair (a letter read as a digit, a word one character off) is shown with the repair. If a Pass or Fail would rest on it, the line is Could Not Evaluate until the sheet is checked. | src/NOTES.md decision: keep raw OCR text; record repairs, never fix silently (project_decision) |
| `POL-GEN-UNCOVERED` No rule, no verdict | no | A situation no policy covers is Could Not Evaluate with 'needs a policy decision'. | src/NOTES.md decision: judgement calls are named policy rules (project_decision) |
| `POL-H-NS-NEW` NS limits are for existing buildings | no | If the building resolves to the NS sub-row and the code analysis describes new work, the NS limit is not a basis for a verdict (footnote d): Could Not Evaluate, with the sprinkler status to be confirmed. | Table 504.3 footnote d (code/table-504.3-notes.md line 25) (code_text) |
| `POL-E-OPERATION-UNKNOWN` Unrecognised window type | no | If the operation isn't recognised, whether and how the window opens is Could Not Evaluate. | IBC 1030.1.1 (code/section-1030-emergency-escape-and-rescue.md line 31) (code_text) |
| `POL-E-NO-EGRESS-COLUMN` Schedule without an egress column | no | If the schedule has no egress column, no window is designated. Every sleeping room is then decided by POL-E-ROOM-ROLLUP from its windows as candidates, and the missing column is reported. | IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13) (project_decision) |

---

Generated by `python -m services.planCheck code-analysis.html window-schedule.html -o REPORT.md --json findings.json`. Findings are also in `findings.json`.

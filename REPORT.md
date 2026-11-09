# Plan check report: building height and emergency escape openings

**Project:** NEW 3-STORY SINGLE-FAMILY DWELLING WITH ATTACHED ACCESSORY DWELLING UNIT (ADU). SLEEPING ROOMS ON ALL FLOORS

## Summary

- **Bottom line:** 4 corrections for the letter, 8 findings these sheets can't settle, and nothing passes.
- **Verdicts:** 6 Fail · 8 Could Not Evaluate · 0 Pass · 10 Not Applicable. The 6 Fails are 4 corrections, because a bedroom and its failing window count as one problem.
- **Why nothing passes:** the window schedule gives frame sizes. The real opening is always smaller, so a frame size can prove a window too small but never big enough.
- **What this is:** an automated check of the code analysis sheet and the window schedule. It checks two things only: building height and bedroom escape windows. Everything else on the code analysis (stories, floor area and so on) was not checked.
- **Checked against:** the 2018 IBC as printed: Table 504.3 (building height) and Section 1030 (emergency escape openings). City of Meridian Falls amendments to the 2018 IBC were not provided, so every verdict is subject to them.

**How to read this report**

- **Verdicts.** **Fail:** breaks the rule. **Could Not Evaluate:** the rule applies, but these sheets can't settle it. **Pass:** meets the rule. **Not Applicable:** the rule doesn't apply here.
- **Confidence** says how likely a verdict is to stand once the full drawing set is seen. **High:** send the correction as written. **Medium:** one thing could change it; confirm it first, or send the correction with that condition stated. **Low:** more than one thing could change it; confirm them first, or send a request for information instead of a correction.
- **Sill heights are worked out,** not read: the schedule doesn't list them, so the sill is the head height minus the window height. That is the bottom of the frame; the opening itself starts a little higher.
- **Terms.** R-3 is the occupancy group (houses), V-B the construction type, and S13D a house-type sprinkler system (NFPA 13D). Head height is the floor to the top of the window. A casement opens on a side hinge; a single hung window opens only its bottom half. Scanning errors are letters or spaces the scan got wrong.
- **IDs.** H- is the building height, R- a bedroom, W- a window. Search for an ID to find its full entry in section 4.

## 1. Corrections to send

Each item is worded as raw material for the correction letter.

**1. Building height is over the limit** (H-1)

- **Problem:** 41'-6" exceeds the 40 ft allowed by Table 504.3, row `R` / `S13D`, column `V-B` by 1'-6".
- **Also correct the code analysis:** it states an allowable height of 60'-0" ('60' - 0" PER TABLE 504.3'); Table 504.3, row `R` / `S13D`, column `V-B` gives 40 ft. 60 ft is the value of the `S` and `S13R` sub-rows in the same row and column, so the architect may have read the wrong sprinkler sub-row (this building resolves to `S13D`).
- **Code:** Table 504.3, row `R` / `S13D`, column `V-B`
- **Confidence before sending:** Medium. It could be reversed by an exception in IBC CH 4 and IBC CH 5 (Table 504.3 footnote a), not provided.

**2. BEDROOM 203 has no working escape window** (R-203)

- **Problem:** BEDROOM 203 needs at least one window a person can escape through, and has none that works.
- **Why:** W-10, its escape window: listed size 2'-0" × 2'-6" = 5.00 sq ft; the clear opening is smaller, so under both 5 and 5.7 sq ft; frame sill = 6'-8" head − 2'-6" height = 50 in, above 44 in. Other windows in the room: W-11 cannot comply.
- **Unless:** the room has a door that opens straight to a public way, yard or court (IBC 1030.1 Exception 2). The floor plans would show it.
- **Code:** IBC 1030.1; IBC 1030.2; IBC 1030.2 Exception; IBC 1030.3; IBC 1030.1 Exception 2
- **Confidence before sending:** Medium. It could be reversed by IBC 1030.1 Exception 2 (an exit door to a public way), which the floor plans (not provided) would show.

**3. BEDROOM 301 has no working escape window** (R-301)

- **Problem:** BEDROOM 301 needs at least one window a person can escape through, and has none that works.
- **Why:** W-20, its escape window: frame sill = 8'-0" head − 3'-0" height = 60 in, above 44 in.
- **Unless:** the room has a door that opens straight to a public way, yard or court (IBC 1030.1 Exception 2). The floor plans would show it.
- **Code:** IBC 1030.1; IBC 1030.3; IBC 1030.1 Exception 2
- **Confidence before sending:** Low, for 2 reasons:
  - It could be reversed by IBC 1030.1 Exception 2 (an exit door to a public way), which the floor plans (not provided) would show.
  - W-20: it rests only on a worked-out sill height (frame sill = 8'-0" head − 3'-0" height = 60 in, above 44 in); confirm on the elevations that head height is measured to the top of the window.

**4. Window 13 in BEDROOM 205 is marked as the escape window but can't be one** (W-13)

- **Problem:** Scheduled as 'FIXED', which does not open; no clear opening.
- **The room (R-205):** Could Not Evaluate. W-12 could not be evaluated; W-13 fails. The room has a complying opening only if W-12 is shown to comply.
- **Code:** IBC 1030.1.1; IBC 1030.2.1; IBC 1030.2; IBC 1030.2 Exception
- **Confidence before sending:** High. It rests on values printed on the sheets.

## 2. Look at these yourself

Places where the tool may be wrong, or where the drawings may hide a problem.

- **W-7 is likely to fail on sill height.** The frame sill is exactly 44 in, so any bottom frame puts the clear opening above the limit. Confirm with the manufacturer's clear-opening dimensions.
- **W-12 is likely to fail on clear height.** Only the bottom sash opens, about 24 in before the frame, exactly the 24 in minimum, leaving nothing for the frame. Ask for the sash split and the manufacturer's clear opening.
- **Window numbers skip.** The schedule has no window 9, 15–19. Rows may have been lost in scanning, or the windows renumbered; check the schedule sheet.
- **The code analysis claim is not supported.** It says 'PROVIDED AT ALL SLEEPING ROOMS PER IBC 1030. SEE WINDOW SCHEDULE, SHEET A6.1' (table row 13). The schedule does not show a working escape window in any bedroom (4 Could Not Evaluate, 2 Fail).
- **Rooms that may be used for sleeping.** Not treated as sleeping rooms: OFFICE 102. If any is a sleeping room, it needs an escape opening (IBC 1030.1). (W-4)
- **Sleeping rooms with no window are invisible to this tool.** The tool only knows rooms that appear in the window schedule. A bedroom with no scheduled window would need an escape opening too; check the floor plans (not provided).
- **A reading the brief decides (H-1).** Occupancy 'R-3' read as row `R`: IBC 310 (occupancy classification) is not provided; the brief's rule places a numbered group in its letter's row unless the table gives the numbered group its own row (as for H and I).
- **Scanning errors the tool read through.** Confirm each on the sheets:
  - H-1: label printed as 'FIRE SPRINKLE RS' (a word split across lines); read as 'FIRE SPRINKLERS'
  - H-1: label printed as 'BUILDING HEIGHT ABOVE GRADE PLAN E' (a word split across lines); read as 'BUILDING HEIGHT ABOVE GRADE PLANE'
  - R-205, W-12: room name 'BEDRROM' is one character from 'BEDROOM'; read as a sleeping room (likely OCR damage; confirm on the floor plan)
  - W-4: inches 'O' read as '0' (a letter where a digit belongs; OCR damage)
  - schedule header: header 'SCREE N' read as 'SCREEN' (a word split across lines)

## 3. What to ask the architect

These would settle the Could Not Evaluate findings.

1. Manufacturer data or window type details for window types A, F, J: the clear opening (width, height, and the height of its bottom above the floor), the hardware (it must open without keys or tools, IBC 1030.1.1) and whether screens release from inside (IBC 1030.5). *Settles:* R-101, R-107, R-205, R-303, W-1, W-3, W-7, W-12.
2. Elevations or wall sections that dimension each escape window's sill and head height. *Settles:* R-101, R-107, R-205, W-1, W-3, W-7, W-12.
3. Floor plans showing what each room is used for, any door from a bedroom straight to the outside (IBC 1030.1 Exception 2), and that each escape window opens onto a yard, court or public way. *Settles:* R-101, R-107, R-203, R-205, R-301, W-1, W-3, W-7, W-12.
4. Building sections or a roof plan that dimension the height to the average of the highest roof surface. *Settles:* H-1.
5. The civil sheet with the grade plane calculation. *Settles:* H-1.
6. Mark an escape window for GUEST BED 303: none is marked egress, but W-21 could work at its listed size. *Settles:* R-303.

Code text the tool was not given, which you may want to confirm: Chapters 4 and 5 (height exceptions) (footnote a) (H-1); Automatic Sprinkler Systems (903.2, 903.3.1.1-903.3.1.3) (footnote h) (H-1).

## 4. Every finding in full

Each entry gives the verdict, what was read from the sheets, any arithmetic, the code section and the confidence.

### Building height

#### H-1 · Building height · **Fail**

- **Result:** 41'-6" exceeds the 40 ft allowed by Table 504.3, row `R` / `S13D`, column `V-B` by 1'-6".

| Read from the code analysis | Value | Where |
|---|---|---|
| OCCUPANCY GROUP | R-3 | code-analysis.html table row 4 |
| CONSTRUCTION TYPE | V-B | code-analysis.html table row 5 |
| FIRE SPRINKLE RS | YES - AUTOMATIC SPRINKLER SYSTEM THROUGHOUT PER NFPA 13D (IBC 903.3.1.3) | code-analysis.html table row 6 |
| BUILDING HEIGHT ABOVE GRADE PLAN E | 41' - 6" (TO AVG. HT. OF HIGHEST ROOF SURFACE) | code-analysis.html table row 8 |
| ALLOWABLE HEIGHT | 60' - 0" PER TABLE 504.3 | code-analysis.html table row 9 |

**How it was decided:**

1. Occupancy 'R-3' → `R`
2. Sprinklers 'YES - AUTOMATIC SPRINKLER SYSTEM THROUGHOUT PER NFPA 13D (IBC 903.3.1.3)' → `S13D`
3. Construction 'V-B' → `V-B`
4. Building height '41' - 6"' = 498 in = 41.5 ft
5. Lookup Table 504.3, row `R` / `S13D`, column `V-B` → 40
6. 41.5 ft > 40 ft; over by 1.5 ft = 1'-6"

**Footnotes printed on this cell:**

- Footnote a (printed on the whole table): "See Chapters 4 and 5 for specific exceptions to the allowable height in this chapter." It points to code text that was not provided.
- Footnote h (printed on the occupancy row label): "New Group R occupancies are required to be protected by an automatic sprinkler system in accordance with Section 903.2.8." It points to code text that was not provided.

- **Code:** Table 504.3, row `R` / `S13D`, column `V-B` = 40 ft; IBC 504.3; Table 504.3 footnote a; Table 504.3 footnote h
- **Confidence:** Medium. It could be reversed by an exception in IBC CH 4 and IBC CH 5 (Table 504.3 footnote a), not provided.

### Bedrooms

Every bedroom needs at least one window a person can escape through (IBC 1030.1). A bedroom follows the window marked as its escape window. If none is marked, or the marked ones fail, its other windows are considered.

The rule covers this building because occupancy 'R-3' is listed in 1030.1 item 2. It covers bedrooms below the fourth story; each room's floor comes from its room number, using the numbering on the code analysis.

#### R-101 · BEDROOM 101, floor 1 · **Could Not Evaluate**

- **Windows:** W-1 (escape window): Could Not Evaluate; W-2 (not marked egress); W-3 (escape window): Could Not Evaluate. Read from the window-schedule, LOCATION 'BEDROOM 101'.
- **Why:** W-1, W-3 could not be evaluated. The room has a complying opening only if one of them is shown to comply.
- **Code:** IBC 1030.1
- **Confidence:** High. It rests on values printed on the sheets.

#### R-107 · ADU BEDROOM 107, floor 1 · **Could Not Evaluate**

- **Windows:** W-7 (escape window): Could Not Evaluate. Read from the window-schedule, LOCATION 'ADU BEDROOM 107'.
- **Why:** W-7 could not be evaluated. The room has a complying opening only if W-7 is shown to comply.
- **Code:** IBC 1030.1
- **Confidence:** High. It rests on values printed on the sheets.

#### R-203 · BEDROOM 203, floor 2 · **Fail**

- **Windows:** W-10 (escape window): Fail; W-11 (not marked egress). Read from the window-schedule, LOCATION 'BEDROOM 203'.
- **Why:** The marked escape window (W-10) fails, and no other window in the room could comply. Unless Exception 2 applies (an exit door to a public way), the room has no escape opening.
- **Code:** IBC 1030.1; IBC 1030.1 Exception 2
- **Confidence:** Medium. It could be reversed by IBC 1030.1 Exception 2 (an exit door to a public way), which the floor plans (not provided) would show.

#### R-205 · BEDROOM 205, floor 2 · **Could Not Evaluate**

- **Windows:** W-12 (escape window): Could Not Evaluate; W-13 (escape window): Fail. Read from the window-schedule, LOCATION 'BEDRROM 205', 'BEDROOM 205'.
- **Why:** W-12 could not be evaluated; W-13 fails. The room has a complying opening only if W-12 is shown to comply. The schedule spells this room more than one way; its windows are grouped by room number.
- **Code:** IBC 1030.1
- **Confidence:** Medium. It rests on a room name corrected for a scanning error: room name 'BEDRROM' is one character from 'BEDROOM'; read as a sleeping room (likely OCR damage; confirm on the floor plan).

#### R-301 · BEDROOM 301, floor 3 · **Fail**

- **Windows:** W-20 (escape window): Fail. Read from the window-schedule, LOCATION 'BEDROOM 301'.
- **Why:** The marked escape window (W-20) fails, and no other window in the room could comply. Unless Exception 2 applies (an exit door to a public way), the room has no escape opening.
- **Code:** IBC 1030.1; IBC 1030.1 Exception 2
- **Confidence:** Low, for 2 reasons:
  - It could be reversed by IBC 1030.1 Exception 2 (an exit door to a public way), which the floor plans (not provided) would show.
  - W-20: it rests only on a worked-out sill height (frame sill = 8'-0" head − 3'-0" height = 60 in, above 44 in); confirm on the elevations that head height is measured to the top of the window.

#### R-303 · GUEST BED 303, floor 3 · **Could Not Evaluate**

- **Windows:** W-21 (not marked egress). Read from the window-schedule, LOCATION 'GUEST BED 303'.
- **Why:** No window is marked as the escape window; W-21 could comply at its listed size but is not marked egress. Ask the architect to mark a window that complies.
- **Code:** IBC 1030.1
- **Confidence:** High. It rests on values printed on the sheets.

### Escape windows

Windows marked EGRESS on the schedule. Each is tested against the five requirements a schedule can show. Three more can't be shown on any schedule, so they stay open for every window: it opens without keys or tools (IBC 1030.1.1), any screen releases from inside (IBC 1030.5), and it opens onto a yard, court or public way (IBC 1030.1). Section 3 asks for them. A fixed window doesn't open, so its size tests are skipped.

#### W-1 · Window 1, BEDROOM 101 · **Could Not Evaluate**

- **Read from the window schedule, table row 4:** L.H. CASM'T (type A), 2' - 6" wide × 4' - 0" high, head height 6' - 8", EGRESS Y.

| Requirement | Code | The schedule shows | Result |
|---|---|---|---|
| Opens normally | IBC 1030.2.1 | L.H. CASM'T: a casement | Met |
| Opening area: at least 5.7 sq ft (5 on the ground floor) | IBC 1030.2; IBC 1030.2 Exception | 30 × 48 in = 10.00 sq ft, including the frame | Not settled |
| Opening height: at least 24 in | IBC 1030.2.1 | 48 in, including the frame | Not settled |
| Opening width: at least 20 in | IBC 1030.2.1 | 30 in, including the frame | Not settled |
| Sill: no more than 44 in above the floor | IBC 1030.3 | 80 in head − 48 in height = 32 in, at the frame | Not settled |

- **Would settle it:** window type details or elevations.
- **Room:** BEDROOM 101 (R-101, Could Not Evaluate).
- **Confidence:** High. It rests on values printed on the sheets.

#### W-3 · Window 3, BEDROOM 101 · **Could Not Evaluate**

- **Read from the window schedule, table row 6:** R.H. CASM'T (type A), 2' - 6" wide × 4' - 0" high, head height 6' - 8", EGRESS Y.

| Requirement | Code | The schedule shows | Result |
|---|---|---|---|
| Opens normally | IBC 1030.2.1 | R.H. CASM'T: a casement | Met |
| Opening area: at least 5.7 sq ft (5 on the ground floor) | IBC 1030.2; IBC 1030.2 Exception | 30 × 48 in = 10.00 sq ft, including the frame | Not settled |
| Opening height: at least 24 in | IBC 1030.2.1 | 48 in, including the frame | Not settled |
| Opening width: at least 20 in | IBC 1030.2.1 | 30 in, including the frame | Not settled |
| Sill: no more than 44 in above the floor | IBC 1030.3 | 80 in head − 48 in height = 32 in, at the frame | Not settled |

- **Would settle it:** window type details or elevations.
- **Room:** BEDROOM 101 (R-101, Could Not Evaluate).
- **Confidence:** High. It rests on values printed on the sheets.

#### W-7 · Window 7, ADU BEDROOM 107 · **Could Not Evaluate**

- **Read from the window schedule, table row 10:** L.H. CASM'T (type F), 2'-6" wide × 3' - 0" high, head height 6' - 8", EGRESS Y.

| Requirement | Code | The schedule shows | Result |
|---|---|---|---|
| Opens normally | IBC 1030.2.1 | L.H. CASM'T: a casement | Met |
| Opening area: at least 5.7 sq ft (5 on the ground floor) | IBC 1030.2; IBC 1030.2 Exception | 30 × 36 in = 7.50 sq ft, including the frame | Not settled |
| Opening height: at least 24 in | IBC 1030.2.1 | 36 in, including the frame | Not settled |
| Opening width: at least 20 in | IBC 1030.2.1 | 30 in, including the frame | Not settled |
| Sill: no more than 44 in above the floor | IBC 1030.3 | 80 in head − 36 in height = 44 in, at the frame | Not settled, likely Fail |

- **Likely to fail:** The frame sill is exactly 44 in, so any bottom frame puts the clear opening above the limit. Confirm with the manufacturer's clear-opening dimensions.
- **Would settle it:** window type details or elevations.
- **Room:** ADU BEDROOM 107 (R-107, Could Not Evaluate).
- **Confidence:** High. It rests on values printed on the sheets.

#### W-10 · Window 10, BEDROOM 203 · **Fail**

- **Read from the window schedule, table row 12:** L.H. CASM'T (type H), 2' - 0" wide × 2' - 6" high, head height 6' - 8", EGRESS Y.

| Requirement | Code | The schedule shows | Result |
|---|---|---|---|
| Opens normally | IBC 1030.2.1 | L.H. CASM'T: a casement | Met |
| Opening area: at least 5.7 sq ft (5 on the ground floor) | IBC 1030.2; IBC 1030.2 Exception | 24 × 30 in = 5.00 sq ft, including the frame | **Fail** |
| Opening height: at least 24 in | IBC 1030.2.1 | 30 in, including the frame | Not settled |
| Opening width: at least 20 in | IBC 1030.2.1 | 24 in, including the frame | Not settled |
| Sill: no more than 44 in above the floor | IBC 1030.3 | 80 in head − 30 in height = 50 in, at the frame | **Fail** |

- **Room:** BEDROOM 203 (R-203, Fail).
- **Confidence:** High. It rests on values printed on the sheets.

#### W-12 · Window 12, BEDRROM 205 · **Could Not Evaluate**

- **Read from the window schedule, table row 14:** S.H. (type J), 3' - 0" wide × 4' - 0" high, head height 6' - 8", EGRESS Y.

| Requirement | Code | The schedule shows | Result |
|---|---|---|---|
| Opens normally | IBC 1030.2.1 | S.H.: a single hung | Met |
| Opening area: at least 5.7 sq ft (5 on the ground floor) | IBC 1030.2; IBC 1030.2 Exception | 36 × 48 in = 12.00 sq ft, including the frame | Not settled |
| Opening height: at least 24 in | IBC 1030.2.1 | 48 in, including the frame | Not settled, likely Fail |
| Opening width: at least 20 in | IBC 1030.2.1 | 36 in, including the frame | Not settled |
| Sill: no more than 44 in above the floor | IBC 1030.3 | 80 in head − 48 in height = 32 in, at the frame | Not settled |

- **Likely to fail:** Only the bottom sash opens, about 24 in before the frame, exactly the 24 in minimum, leaving nothing for the frame. Ask for the sash split and the manufacturer's clear opening.
- **Would settle it:** window type details or elevations.
- **Room:** BEDROOM 205 (R-205, Could Not Evaluate).
- **Confidence:** Medium. It rests on a room name corrected for a scanning error: room name 'BEDRROM' is one character from 'BEDROOM'; read as a sleeping room (likely OCR damage; confirm on the floor plan).

#### W-13 · Window 13, BEDROOM 205 · **Fail**

- **Read from the window schedule, table row 15:** FIXED (type K), 4' - 0" wide × 4' - 0" high, head height 6' - 8", EGRESS Y.

| Requirement | Code | The schedule shows | Result |
|---|---|---|---|
| Opens normally | IBC 1030.1.1; IBC 1030.2.1 | FIXED: does not open | **Fail** |
| Opening area: at least 5.7 sq ft (5 on the ground floor) | IBC 1030.2; IBC 1030.2 Exception | no opening (fixed) | **Fail** |
| Sill: no more than 44 in above the floor | IBC 1030.3 | 80 in head − 48 in height = 32 in, at the frame | Not settled |

- **Room:** BEDROOM 205 (R-205, Could Not Evaluate).
- **Confidence:** High. It rests on values printed on the sheets.

#### W-20 · Window 20, BEDROOM 301 · **Fail**

- **Read from the window schedule, table row 17:** L.H. CASM'T (type F), 2' - 6" wide × 3' - 0" high, head height 8' - 0", EGRESS Y.

| Requirement | Code | The schedule shows | Result |
|---|---|---|---|
| Opens normally | IBC 1030.2.1 | L.H. CASM'T: a casement | Met |
| Opening area: at least 5.7 sq ft (5 on the ground floor) | IBC 1030.2; IBC 1030.2 Exception | 30 × 36 in = 7.50 sq ft, including the frame | Not settled |
| Opening height: at least 24 in | IBC 1030.2.1 | 36 in, including the frame | Not settled |
| Opening width: at least 20 in | IBC 1030.2.1 | 30 in, including the frame | Not settled |
| Sill: no more than 44 in above the floor | IBC 1030.3 | 96 in head − 36 in height = 60 in, at the frame | **Fail** |

- **Room:** BEDROOM 301 (R-301, Fail).
- **Confidence:** Medium. It rests only on a worked-out sill height (frame sill = 8'-0" head − 3'-0" height = 60 in, above 44 in); confirm on the elevations that head height is measured to the top of the window.

### Windows the rule doesn't apply to

**Not in a bedroom.** The escape-window rule applies to sleeping rooms only (IBC 1030.1).

| ID | Room | EGRESS cell | Schedule row | Verdict | Confidence |
|---|---|---|---|---|---|
| W-5 | LIVING 103 | (blank) | 8 | Not Applicable | High |
| W-6 | KITCHEN 104 | (blank) | 9 | Not Applicable | High |
| W-8 | LAUNDRY 108 | (blank) | 11 | Not Applicable | High |
| W-14 | BATH 206 | (blank) | 16 | Not Applicable | High |
| W-22 | HALL 302 | (blank) | 19 | Not Applicable | High |
| W-23 | STAIR S1 | (blank) | 20 | Not Applicable | High |

**In a bedroom, but not marked egress.** A bedroom needs one escape window, not every window to be one (IBC 1030.1). Each is still considered in its bedroom's entry.

| ID | Room | EGRESS cell | Schedule row | Verdict | Confidence |
|---|---|---|---|---|---|
| W-2 | BEDROOM 101 | (blank) | 5 | Not Applicable | High |
| W-11 | BEDROOM 203 | (blank) | 13 | Not Applicable | High |
| W-21 | GUEST BED 303 | (blank) | 18 | Not Applicable | High |

**Room use unclear.** The name isn't clearly a bedroom, so the rule wasn't applied. If people sleep there, it needs an escape window (IBC 1030.1). Confirm the room's use.

| ID | Room | EGRESS cell | Schedule row | Verdict | Confidence |
|---|---|---|---|---|---|
| W-4 | OFFICE 102 | (blank) | 7 | Not Applicable | Low |

## Appendix: for checking the tool

Not needed to read the verdicts. File names are the tool's input files; rule ids (`POL-…`) are the tool's named judgement calls. Table rows are counted from 1 at the top of each table, header rows included.

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

### B. Rules the tool applied

Judgement calls are named rules, the same for every project, each with a test.

| Rule | What it says | Rests on | Used by |
|---|---|---|---|
| `POL-GEN-AMENDMENTS` Local amendments not provided | The project is reviewed against the 2018 IBC as printed. If the manifest lists local amendments as not provided, every verdict is conditional on them and the report says so once, at the top. | the local-amendments document listed in the manifest (unavailable) | whole report |
| `POL-GEN-SCHEDULE-GAPS` Gaps in a numbered schedule are reported | When every window mark is a whole number, numbers missing between the lowest and highest are listed for the plan checker: rows may have been lost in scanning, or windows renumbered. No verdict changes. | project decision: report review rounds, 2026-11-08 | whole report |
| `POL-GEN-CONFIDENCE` Every finding carries a confidence level, from named reasons | Confidence (High, Medium, Low) says how likely a verdict is to survive review with the full drawing set. It starts at High and drops one level for each of: a Fail whose only failing grounds are derived values; a Fail that a document not provided could reverse (an exception it points to, not ruled out); a verdict resting on a repaired room-name reading. A verdict decided by a guess at a room's use is Low. A room's Fail takes on the lowered levels of the failing windows it rests on. Interpretations the brief itself gives do not lower it. Confidence never changes a verdict. | project decision: confidence levels, 2026-11-08 | whole report |
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
| `POL-E-NO-FRAME-ASSUMPTION` No frame-deduction assumption (decision 2) | The tool assumes no frame size, so nominal size never proves a Pass. Without a net clear opening (from the schedule or manufacturer data) a minimum is Could Not Evaluate, with the nominal upper bound shown. | project decision: Plan from here: open decisions #2 | W-1, W-3, W-7, W-10, W-12, W-20 |
| `POL-E-SILL-LOWER` A derived sill is a lower bound | Sill = head height - nominal height (head height is floor to top of window). The bottom of the clear opening is at or above that frame sill. A frame sill above 44 in proves a Fail; at or below 44 in it proves nothing, because the bottom frame depth is unknown. A scheduled sill height is treated the same way unless the column says it is to the clear opening. | IBC 1030.3 (code/section-1030-emergency-escape-and-rescue.md line 45); Challenge brief (instructions/README.md line 64) | W-1, W-3, W-7, W-10, W-12, W-13, W-20 |
| `POL-E-GRADE-FLOOR` Grade-floor limit (decision 4) | Whether an opening is a grade-floor opening needs the finished ground level, which these sheets don't give. The area is decided only when the 5.0 and 5.7 sq ft limits give the same result. | IBC 1030.2 Exception (code/section-1030-emergency-escape-and-rescue.md line 37); IBC 202 GRADE FLOOR OPENING (code/section-1030-emergency-escape-and-rescue.md line 55); project decision: Plan from here: open decisions #4 | W-1, W-3, W-7, W-10, W-12, W-20 |
| `POL-E-FIXED` A fixed window is not an escape opening | A window scheduled as fixed does not open, so it can't be operated from inside and has no net clear opening by normal operation: Fail. | IBC 1030.1.1 (code/section-1030-emergency-escape-and-rescue.md line 31); IBC 1030.2.1 (code/section-1030-emergency-escape-and-rescue.md line 41) | W-13 |
| `POL-E-PARTIAL-OPENING` Single hung and slider bounds are notes only (decision 5) | A single hung opens only its bottom sash and a slider about half its width. The tool shows the half-size figure as a labelled note, never as proof of a Fail, because panel splits vary (a three-panel slider opens two thirds; sashes can be unequal). | Challenge brief (instructions/README.md line 66); project decision: Plan from here: open decisions #5 | W-12 |
| `POL-E-AT-LIMIT` A bound sitting exactly at a limit is flagged as a likely Fail | A frame sill exactly at the 44 in maximum, or a partial-opening note (bottom sash, half a slider) at or below a minimum, cannot prove a Fail from the schedule, so the verdict stays Could Not Evaluate. The window is flagged 'expect a Fail' and listed first among the items to check, because any frame deduction tips it over. | IBC 1030.3 (code/section-1030-emergency-escape-and-rescue.md line 45); IBC 1030.2.1 (code/section-1030-emergency-escape-and-rescue.md line 41); project decision: report review rounds, 2026-11-08 | W-7, W-12 |
| `POL-E-UNSEEN` Requirements no schedule shows | Operation without keys or tools, releasable screens and opening onto a public way, yard or court are each a Could Not Evaluate line on every egress window, naming the document that would settle it. They never cause a Fail; they do keep a window from a Pass. | IBC 1030.1.1 (code/section-1030-emergency-escape-and-rescue.md line 31); IBC 1030.5 (code/section-1030-emergency-escape-and-rescue.md line 49); IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13) | W-1, W-3, W-7, W-10, W-12, W-13, W-20 |
| `POL-E-ROOM-ROLLUP` Room verdict (decision 3) | A sleeping room Passes if a designated egress window Passes, and is Could Not Evaluate if one is Could Not Evaluate. If none is designated, or every designated one Fails, the room's other windows are evaluated as candidates: if any could comply the room is Could Not Evaluate, flagged 'no complying opening designated'; if none could, the room Fails. | IBC 1030.1 (code/section-1030-emergency-escape-and-rescue.md line 13); project decision: Plan from here: open decisions #3 | R-101, R-107, R-203, R-205, R-301, R-303 |
| `POL-E-EXCEPTION-2` Exit-door exception is not assumed | A room Fail says 'unless Exception 2 applies (an exit door to a public way)'. The floor plans would settle it; the tool does not assume a door it can't see. | IBC 1030.1 Exception 2 (code/section-1030-emergency-escape-and-rescue.md line 19) | R-203, R-301 |

Not needed for this project: `POL-GEN-OCR` (OCR-repaired values never decide a verdict alone), `POL-GEN-UNCOVERED` (No rule, no verdict), `POL-H-NS-NEW` (NS limits are for existing buildings), `POL-E-OPERATION-UNKNOWN` (Unrecognised window type), `POL-E-NO-EGRESS-COLUMN` (Schedule without an egress column).

### C. Inputs

| Input | File | sha256 (first 12) |
|---|---|---|
| Code analysis (CODE ANALYSIS - SHEET A0.1) | `code-analysis.html` | `a0dc18fc9c36` |
| Window schedule | `window-schedule.html` | `85de501d0b3c` |

Generated by `python -m services.planCheck code-analysis.html window-schedule.html -o REPORT.md --json findings.json`. The same findings are in `findings.json`.

# Spot check: hand-verify each ruling in REPORT.md

`index.html` is a small web app for checking each ruling in `REPORT.md` against the real sheets. It shows the steps below one finding at a time. Next to them it shows the sheet image, with the exact row or cell to look at highlighted. You mark each ruling Correct, Wrong or Unsure, and can add a note.

## Run it

From the `ichi-assignment` folder:

```bash
python -m http.server 8765
```

Then open http://localhost:8765/spotcheck/.

Served this way, the app reads the live verdicts and confidence levels from `findings.json`. It warns you if the report and this checklist disagree.

You can also open `index.html` straight from disk. It still works, but it shows the verdicts built into the page instead of the live ones.

**Keys:**
- `←` / `→`: move between findings.
- `↑` / `↓`: move between steps.
- `C`: mark Correct. `W`: mark Wrong. `U`: mark Unsure.

Your marks and notes are saved in this browser only. **Export results** downloads them as a Markdown table, and **Reset** clears them.

---

## The checklist

Open these four files from `instructions/`:

| Short name | File | What it is |
|---|---|---|
| **Code sheet** | `readme_images/code-analysis.png` | The architect's summary of the building |
| **Schedule** | `readme_images/window-schedule.png` | The list of every window |
| **Height table** | `readme_images/table-504-3.png` | The code's height limits |
| **Window rules** | `fixtures/code/section-1030-emergency-escape-and-rescue.md` | The code text for bedroom escape windows |

If an image is hard to read, the same content is in `fixtures/project/code-analysis.html` and `fixtures/project/window-schedule.html`. Row numbers below count from the top of those tables.

### Part 1: Is the building too tall?

**1. Read the building's facts.** On the code sheet:

| Row | Label | It should say |
|---|---|---|
| 4 | OCCUPANCY GROUP | R-3 (a house) |
| 5 | CONSTRUCTION TYPE | V-B |
| 6 | FIRE SPRINKLE RS | NFPA 13D (IBC 903.3.1.3) |
| 8 | BUILDING HEIGHT | 41' - 6" |
| 9 | ALLOWABLE HEIGHT | 60' - 0" PER TABLE 504.3 |

**2. Turn those facts into table labels.**
- R-3 uses the table row for **R**. Source: `instructions/README.md`, line 54.
- An NFPA 13D system is written **S13D**. Source: the legend under the height table, and `fixtures/code/table-504.3-notes.md`, lines 15 and 39.

**3. Look up the limit.** On the height table, find row **R**, then sub-row **S13D**, then column **TYPE V / B**. It should say **40**.

**4. Compare.** 41'-6" is more than 40 ft. **Fail**, over by 1'-6".

**5. Check the architect's figure.** In the same row R and column V-B, the **S13R** and **S** sub-rows say **60**. That is probably where the architect's 60 ft came from.

### Part 2: The bedroom window rules

Each rule is on one line of the window rules file:

| Rule | Line |
|---|---|
| Every bedroom below the 4th floor needs at least one escape opening | 13 |
| ...unless it has a door straight to the outside (Exception 2) | 19 |
| It must open from inside without keys or tools | 31 |
| The opening must be at least **5.7 sq ft** | 35 |
| ...or **5 sq ft** for a ground-floor window | 37 |
| It must be at least **24 in tall** and **20 in wide** | 41 |
| The bottom of the opening (the sill) must be no more than **44 in** above the floor | 45 |

Two things to know before checking the windows:
- **The schedule lists frame sizes.** The real opening is a little smaller. A size that is already too small proves a Fail, but a size that looks big enough can't prove a Pass.
- **The schedule doesn't list sill heights.** Work them out as **head height minus window height**, in inches. For example, 6'-8" is 80 in.

### Part 3: Escape windows (EGRESS = Y)

Find each window by its number in the **SYMBOL** column.

| Window | HTML row | What the schedule says | Do this math | Expected result |
|---|---|---|---|---|
| **1** | 4 | Casement 2'-6" × 4'-0", head 6'-8" | 2.5 × 4 = 10 sq ft; sill 80 − 48 = 32 in | **Could Not Evaluate**: big enough on paper, but the true opening isn't given |
| **3** | 6 | Same as window 1 | Same | **Could Not Evaluate** |
| **7** | 10 | Casement 2'-6" × 3'-0", head 6'-8" | Sill 80 − 36 = **44 in**, exactly the limit | **Could Not Evaluate**, flagged "likely Fail" |
| **10** | 12 | Casement 2'-0" × 2'-6", head 6'-8" | 2 × 2.5 = **5.0 sq ft**, so the real opening is under 5; sill 80 − 30 = **50 in** | **Fail** |
| **12** | 14 | Single hung 3'-0" × 4'-0", head 6'-8" | Only the bottom half opens: 48 ÷ 2 = **24 in**, the minimum before the frame | **Could Not Evaluate**, flagged "likely Fail" |
| **13** | 15 | **FIXED** 4'-0" × 4'-0", EGRESS Y | A fixed window doesn't open (line 31) | **Fail** |
| **20** | 17 | Casement 2'-6" × 3'-0", head **8'-0"** | Sill 96 − 36 = **60 in** | **Fail** |

### Part 4: Bedrooms

Each bedroom needs one working escape window. Code sheet row 12 gives the room numbering: 1XX is the first floor, 2XX the second and 3XX the third, so every bedroom is below the 4th floor.

| Bedroom | Windows | Reasoning | Expected result |
|---|---|---|---|
| **101** | 1, 2, 3 | 1 and 3 aren't settled; 2 is fixed and not egress | **Could Not Evaluate** |
| **107** | 7 | 7 isn't settled | **Could Not Evaluate** |
| **203** | 10, 11 | 10 fails; 11 is fixed | **Fail**, unless there's a door straight outside (line 19) |
| **205** | 12, 13 | 12 isn't settled; 13 fails. "BEDRROM" is a scanning typo. | **Could Not Evaluate** |
| **301** | 20 | Its only window fails | **Fail**, unless there's a door straight outside (line 19) |
| **303** | 21 (row 18) | EGRESS is blank (the Y is under SCREEN), but 2'-6" × 4'-0" could work | **Could Not Evaluate**: ask the architect to designate an escape window |

### Part 5: Windows that don't need checking

| Window(s) | HTML row(s) | Why | Expected result |
|---|---|---|---|
| 2, 11, 21 | 5, 13, 18 | In bedrooms but not marked egress; each bedroom only needs one escape window | **Not Applicable** |
| 4 | 7 | OFFICE 102 isn't treated as a bedroom. Its width "3' - O" (letter O) was read as 3'-0". | **Not Applicable**. Ask whether the office is used for sleeping. |
| 5, 6, 8, 14, 22, 23 | 8, 9, 11, 16, 19, 20 | Living room, kitchen, laundry, bath, hall, stair | **Not Applicable** |

### Part 6: Other claims in the report

1. **Missing window numbers.** Read down SYMBOL: there is no window 9, and none from 15 to 19.
2. **The architect's claim.** Code sheet row 13 says escape openings are "PROVIDED AT ALL SLEEPING ROOMS". Bedrooms 203 and 301 fail, and others can't be confirmed, so the claim isn't supported.
3. **Confidence levels.** These are the tool's judgement, not something printed on the sheets. Check that each reason holds.

| Level | Findings | Reason |
|---|---|---|
| **High** | Windows 10 and 13 | They fail on printed sizes |
| **Medium** | Height | Could change if a Chapter 4–5 exception applied (`table-504.3-notes.md` line 19) |
| **Medium** | Bedroom 203 | Could change if it has an outside door |
| **Medium** | Window 20 | Fails only on the worked-out sill |
| **Medium** | Bedroom 205 and window 12 | Rest on reading "BEDRROM" as BEDROOM |
| **Low** | Bedroom 301 | Two doubts: the worked-out sill and a possible outside door |
| **Low** | Window 4 | Rests on guessing that the office isn't a bedroom |

`tests/fixtures/expected/verdicts.json` holds the same expected results.

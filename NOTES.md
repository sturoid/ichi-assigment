# NOTES

## Run it

From `src/`, using Python 3.12 with the standard library only:

```
python -m services.planCheck ../tests/fixtures/code-analysis.html ../tests/fixtures/window-schedule.html -o ../REPORT.md --json ../findings.json
python -m services.planCheck.evals ../tests/fixtures/expected/verdicts.json ../findings.json --report ../REPORT.md
```

To run the tests, use `python -m unittest` in each of `tests/services/htmlParser`, `tests/services/codeStore` and `tests/services/planCheck`. That is 85 + 38 + 87 tests. Eight parser tests are known gaps and are skipped on purpose.

## How it works

There are no model calls at run time. Every step is plain, tested Python.

1. **Parse the HTML** (`services/htmlParser`).
   - Rowspans and colspans are resolved. `<sup>` marks become footnotes.
   - Header rows are found from the table's structure, not from `<th>` or bold.
   - OCR text is kept raw. A word split across lines keeps both readings (`FIRE SPRINKLE RS` / `FIRE SPRINKLERS`), and nothing is repaired silently.
2. **Code store** (`services/codeStore`).
   - Table 504.3 is parsed against an explicit spec for that table, and every cell is keyed by its printed labels.
   - The notes file supplies footnotes a–h, the legend and the sprinkler shorthand, each with its line number.
   - Each footnote reference is linked to a manifest of documents. The manifest also lists the documents we *don't* have (IBC 903, Chapters 4–5, the IEBC, floor plans, window details ...).
   - Lookups are exact and return one of `found`, `not_found`, `unavailable` or `invalid_input`. They never raise.
3. **Resolver.** Project wording becomes table values only through rules, and each rule cites its source:
   - `R-3`→`R` (the brief's rule, reported as an interpretation, because IBC 310 isn't provided);
   - `NFPA 13D` / `903.3.1.3`→`S13D` (legend line 15, shorthand line 39);
   - `NONE`→`NS`;
   - `VB` / `TYPE V-B`→`V-B`.

   Partial or unstated sprinkler coverage resolves to nothing, which gives Could Not Evaluate.
4. **Facts.**
   - Code-analysis fields and schedule columns are found by alias, never by position.
   - The two `TYPE` columns are told apart by order, then confirmed by their contents.
   - A feet-and-inches parser flags OCR damage such as `3' - O"`.
   - A sleeping-room classifier reads `BEDRROM` as a bedroom and flags it. Office, den, loft and unknown names are treated as ambiguous and listed for review.
5. **Checks.**
   - The IBC 1030 limits are constants. Each carries its file, line and word-for-word quote, and the CLI refuses to run if a quote isn't on its line.
   - Every judgement call is a named rule in `policies.py`, with an id, a statement, what it rests on, and a test. The report lists them.
   - The key rules: nominal size is an upper bound, so it can prove a Fail but never a Pass. A sill derived as head height minus window height is the *frame* sill, a lower bound on the clear opening's bottom.
6. **Report.** `REPORT.md` and `findings.json` render from one list of findings. A test checks that the committed files are byte-for-byte what the tool writes.

**Why the report is laid out this way.** It follows the plan checker's job, in order:
1. **Corrections.** These are worded like correction-letter comments and grouped by room, so Bedroom 203 and its failing window are one item. Each states the arithmetic and only the code sections that decide it.
2. **Check these before relying on the report.** This is where the tool could be wrong or the drawings could hide something: likely Fails the schedule can't prove, missing window numbers, OCR repairs, an ambiguous room, interpretations.
3. **Information to request.** The Could Not Evaluate findings, rewritten as requests to the architect.
4. **Evidence.** Compact tables follow. The egress-window table shows, for each window, what was read and each requirement's result, with the code section in the column header. Rules shared by every window, such as nominal size being an upper bound, are stated once above it.
5. **Appendix.** It holds what a reviewer needs but a plan checker doesn't: code file lines, source rows, the named rules and input hashes.

The report went from 585 lines to about 240 after three independent reviews: two from Sonnet and one from me.

**What varies and what doesn't.** The project files are inputs. Another project's code analysis and window schedule, with different values, column names, order and OCR damage, are read the same way (brief, line 92). The code files are a fixed library: IBC 2018 Table 504.3, its notes and Section 1030 (brief, lines 13, 53 and 72). They are curated once with line-cited quotes, not re-read per project. Swapping in another edition means updating `planCheck/citations.py`. If a code file changes without that update, the startup quote check stops the run rather than apply stale limits.

## How I used AI and checked it

- **Roles.** Claude Opus built the tool. Claude Sonnet did independent reviews at each design point: it got the files and the question, not Opus's conclusions. Disagreements were taken to me rather than settled silently.
- **Hand-typed checks against the printed sources.**
  - All 144 cells of Table 504.3 were typed from the printed image, and the parser is tested against them.
  - The eval set (`tests/fixtures/expected/verdicts.json`) was typed by hand, never generated from output. I spot-checked it against the sheet images.
  - Every code quote the tool cites is tested against its line.
- **What reviews caught.**
  - In fixture analysis, the AI first asserted that R / S13D / V-B was 60 ft. Checking against the image showed 40.
  - The last review found six real bugs, all fixed with regression tests:
    - footnote d applied to rows that don't carry it;
    - `41.5 FT` misread as 5 ft;
    - fixed windows getting window-level Fails when the schedule has no EGRESS column;
    - an unnumbered `BEDRROM 2` split from `BEDROOM 2`;
    - `BEDROOM BATH` read as a bedroom;
    - a bare `840` read as 840 sq ft.
  - Three reviews of the report agreed on every verdict. Two Sonnet reviews independently found something I had missed: the schedule skips window numbers 9 and 15–19. The report now flags gaps like that for any numbered schedule.

## What I couldn't verify, and what would settle it

| What | Why not | What settles it |
|---|---|---|
| Net clear opening, clear width and height | The schedule gives nominal (frame) sizes | Window type details or manufacturer data |
| Sill heights | Derived from head height minus window height; this is the frame sill, not the clear opening | Elevations or window details |
| Grade-floor openings (5.0 vs 5.7 sq ft) | Needs the finished ground level at each window | Civil sheet C1.0, elevations |
| Hardware without keys or tools; screens releasing from inside; opening onto a public way, yard or court | Never on a schedule | Window details, floor plans, site plan |
| Exception 2 (an exit door from the bedroom) | Not on either sheet | Floor plans |
| The 41'-6" height itself | It's the architect's figure | Building sections, roof plan, C1.0 |
| Footnote a exceptions (Chapters 4–5), and the 903.2.8 sprinkler requirement | Not provided | IBC Chapters 4–5, 903 |
| Local amendments | Not provided | The City of Meridian Falls amendments |
| Bedrooms with no row in the schedule | The tool only sees scheduled rooms | Floor plans |

## Judgement calls to discuss

- **A window cannot get a Pass from a schedule like this one.** Three requirements (hardware, screens, public way) never appear on a schedule, so I count them as Could Not Evaluate on every egress window (`POL-E-UNSEEN`). The Sonnet reviewer argued for a Pass on the measurable criteria, with those three listed as unverified. I kept the stricter reading, because a wrong Pass is worse than an honest Could Not Evaluate. It is one rule to change. On these fixtures it changes nothing, because no window has a net clear opening.
- **Guest Bed 303 is Could Not Evaluate, not Fail.** No window is marked egress, but 1030.1 requires a complying opening to *exist*, and window 21 could comply at nominal size. So the finding is flagged "ask the architect to designate one" instead.
- **Bedrooms 203 and 301 are Fail, although Exception 2 can't be ruled out.** Their only designated windows fail, and no other window could comply. Exception 2 (an exit door to the outside) is something the applicant claims. Here, the code analysis claims the openings are provided "per IBC 1030, see window schedule". Each Fail says "unless Exception 2 applies" and asks for the floor plans. One Sonnet review preferred Could Not Evaluate; the other agreed with Fail.
- **Window 7 is Could Not Evaluate, flagged "expect a Fail".** Its frame sill is exactly 44 in, so any bottom frame puts the clear opening over the limit. That figure rests on head height being measured to the top of the unit. Windows 10 and 20 fail on sill with 6 in and 16 in to spare, which covers that uncertainty. Window 7 has no margin, so it is listed first among the items to check, not reported as a Fail (`POL-E-AT-LIMIT`). Window 20 still gets Medium confidence (below), because its only failing ground is that derived sill. Window 12 is handled the same way: its bottom sash gives about 24 in, exactly the minimum.
- **Height is a Fail, despite footnote a's unavailable exceptions.** The code analysis claims no exception, so a Fail stands unless an exception is claimed. The architect's 60 ft equals the R / S and R / S13R cells, so they probably read the wrong sprinkler sub-row. The report says so.

## Confidence, and what to do with a low-confidence Fail

Every finding has a confidence level: High, Medium or Low (`POL-GEN-CONFIDENCE`, in `planCheck/confidence.py`). It means how likely the verdict is to survive review with the full drawing set. It is a level, not a score, and it comes only from named reasons, which are listed with the finding. It never changes a verdict.

- It starts at High.
- It drops one level for each of these:
  - a Fail whose only failing grounds are derived values, such as a sill worked out from head height minus window height;
  - a Fail that a document we don't have could reverse: an exception the code points to, such as Exception 2 or the Chapter 4–5 exceptions in footnote a;
  - a verdict resting on a repaired room name.
- A verdict decided by guessing a room's use is Low. If the guess is wrong, a required opening goes unchecked.
- A room's Fail takes on its failing window's lowered levels, because both must hold for the correction to stand.

On these fixtures, window 13 is High: it is scheduled FIXED. Window 10 is High too, because its area fails on printed values even before the derived sill. The height Fail, Bedroom 203 and window 20 are Medium. Bedroom 301 is Low: it rests on a derived sill *and* an unseen exit door.

**What a reviewer should do with a Low-confidence Fail:** don't send it as a correction yet. A wrong correction costs the applicant a redesign and the reviewer credibility. A wrong request for information costs one round trip. So:
1. Check the named reasons against the sheets you have; for Bedroom 301, those are the elevations and the floor plans.
2. If they hold, send the correction.
3. If they can't be checked, send it as a request for information, quoting the arithmetic, so the applicant can answer with one sheet.

For a Medium Fail, send the correction with the condition stated, as §1 already does for Exception 2. A review queue sorted by confidence puts the cheap checks first.

## With another day

- Read the number of exits from the code analysis, so R-2 buildings can be scoped instead of returning Could Not Evaluate.
- Build a second fixture package with the traps this one doesn't have: reordered columns, no EGRESS column, an unnumbered room, square-inch areas.
- Load IBC 1030 into the store as provisions instead of constants, if more prose sections are added.

**At 200 sheets and 40 checks**, the expensive parts are finding the right table and verifying code text. Both are built to scale here: a manifest of documents, and code tables declared once in specs. The checks also share one finding model and one policy registry. The weak point is OCR'd project tables. I would add a review queue for any value the reader repaired or chose between readings of, instead of letting it decide a verdict.

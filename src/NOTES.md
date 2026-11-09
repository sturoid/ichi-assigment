# Project notes — how the parser was built and why

A running log of phases, findings, decisions, issues and proposed fixes. It is kept short so it can be reviewed with other developers. Design detail lives in [`services/htmlParser/PLAN.md`](services/htmlParser/PLAN.md) (parser) and [`services/codeStore/DESIGN.md`](services/codeStore/DESIGN.md) (store contract). The table-shape test catalogue lives in [`../tests/fixtures/scenarios/README.md`](../tests/fixtures/scenarios/README.md).

## Goal and roadmap

We want code tables (the law) and project tables (submitted, OCR'd, messy) in reliable data structures that scripts can query. Later phases check submissions against code and report what fails or could not be evaluated. Each step has to be solid before the next one starts.

1. **Reliable HTML parser and data structure.** *Done: parser (1-1c) and store contract (1d), each reviewed independently by Sonnet.*
2. **Code notes and other code documents into the same lookup store.** This covers footnotes, legend, prose sections and cross-references, including references to documents we don't have.
3. **Analyse project files against the code data.** Flag discrepancies, missing data and missing code.
4. **Report** for the plan checker.

## Plan from here, after reading the brief (2026-11-08)

The brief (`instructions/README.md`) was read in full on 2026-11-08, with the user's permission. The user's agent-oriented outline of it was also read.

**Was the path right?** Mostly yes, though we over-invested in some places.
- **The core matches what the brief judges.** The brief's own trap is that an LLM misreads Table 504.3, and it asks "How would you know if your tool read the wrong cell?" Our answer is the 144-cell sweep against values hand-typed from the printed image. The brief's question, *I-4 / III-B / non-sprinklered*, returns **55 ft**, cited as row `I-4` / `NS` / column `III-B`, with footnotes a, d and g.
- **The design already enforces several of the brief's rules:** exact lookup, provenance on every value, a manifest of what we don't have, and Could Not Evaluate kept separate from bad input.
- **What we over-invested in:** the brief budgets 3–4 hours, says hand-built parsers earn nothing extra, and cares most about the report. The scenario suite and the store contract are good evidence of verification, but no more general infrastructure should be built. **Everything from here goes toward the deliverables:** a tool that takes the code analysis and the window schedule and writes `REPORT.md`, plus `NOTES.md`; optionally a findings JSON and an eval set.
- **Earlier advice changed.** For IBC 1030, a generic prose-limit extractor is over-engineering for five limits. Instead:
  - the 1030 requirements become cited constants in plain, tested code;
  - a test checks that each quoted phrase appears word for word at its line in the code file.
  - Code requirements are the same for any project, so this isn't "hard-coding to the fixtures". Project values never get hard-coded.

**Remaining work, in order.** Each step gets tests and hand-typed expected values.

1. **Load the 504.3 notes.**
   - Footnotes a–h get their text, and `conditions_loaded` becomes true. Their references link to manifest ids, so we can say "IBC 903.2.8, not provided".
   - Legend definitions are stored per sub-row value.
   - The sprinkler shorthand is stored with line numbers.
2. **Turn the 1030 requirements into cited constants.** Scope (1030.1), net clear area of 5.7 sq ft (5.0 for a grade-floor opening), clear height 24 in, clear width 20 in, sill 44 in, and operable from inside (1030.1.1). Each one gets its line and quote.
3. **Build the resolver** (format already in `codeStore/DESIGN.md`). Project wording becomes table values, and every rule cites its source:
   - `R-3` → `R` (the brief's rule; IBC 310 not provided);
   - `NFPA 13D` / `903.3.1.3` → `S13D`, from the legend and shorthand;
   - `NONE` → `NS`;
   - construction type normalisation.
4. **Extract project facts.**
   - Code analysis fields by label aliases, using the join candidates (`FIRE SPRINKLE RS`, `GRADE PLAN E`).
   - Window schedule column roles by alias. The two `TYPE` columns are told apart by order: operation first, type mark second. A missing role, such as `EGRESS`, gives Could Not Evaluate.
   - A feet-and-inches parser that flags OCR damage such as `3' - O"`.
   - A sleeping-room classifier: `BEDROOM`, `BED`, `BDRM` and `BEDRROM` count; den, office and loft are flagged as ambiguous.
5. **Write the checks.**
   - Check 1 produces one finding.
   - Check 2 produces a finding per egress window and a roll-up per sleeping room, and gives `Not Applicable` for windows in other rooms. Nominal size is an upper bound, so it can prove a Fail but never a Pass. Every derived value (such as the sill height) is shown with its working.
6. **Write the CLI and wire it together.**
   - `python -m <tool> <code-analysis.html> <window-schedule.html> -o REPORT.md` runs parser → store → resolver → checks → report.
   - The committed `REPORT.md` must be exactly what the tool writes, and a test checks this.
7. **Produce the report and deliverables:**
   - `REPORT.md`;
   - an eval set of expected verdicts with a scorer;
   - the deliverable `NOTES.md` for Ichi, which is separate from this log;
   - `findings.json` last, as a bonus.

**Sonnet review of this plan (independent; it decided the open questions before reading ours).** It agreed with the verdict policy. It found these gaps, all now added to the plan:
- **Missing steps:** no CLI step and no wiring step (now steps 6 and 7).
- **Requirements that need their own Could Not Evaluate line on every egress window:**
  - operable from inside without keys or tools (1030.1.1);
  - screens releasable (1030.5);
  - an exit door from the room, which would be Exception 2;
  - opening onto a public way, yard or court.
  Each line names the document that would settle it.
- **A cross-check of the architect's claim.** The code analysis says egress is "PROVIDED AT ALL SLEEPING ROOMS" (A0.1). Rooms 203, 205 (window 13), 301 and 303 contradict that, and it belongs in the report.
- **The architect's 60 ft** equals both the R / `S` and R / `S13R` cells for V-B (checked against the store). They probably read a sprinkler sub-row other than `S13D`. Say so in the height finding.
- **Bedrooms with no row in the schedule** are invisible to the tool. List this as something the plan checker should verify against the floor plans; it isn't a verdict.
- **A regression test for window 21 (GUEST BED 303).** It has `Y` under SCREEN but not under EGRESS, so a parser that shifts columns would wrongly make it egress.
- **Scope cut:** load the footnote text simply (a–h; `h` is the one Check 1 cites). Don't build general resolver citation machinery beyond what the rules need.

**Expected verdicts from nominal data.** Derived by Sonnet and re-checked by Opus against the parsed schedule. These are the seed of the eval set and still need your spot-check.

| Window / room | Data | Expected |
|---|---|---|
| Building height | R / S13D / V-B = 40 ft; claimed 41'-6"; architect says 60 | **Fail** by 1'-6", with the 60 ft mismatch flagged |
| 1, 3 (Bedroom 101) | casement 2'-6" × 4'-0" = 10 sq ft, sill 32" | Could Not Evaluate (net unknown) → room Could Not Evaluate |
| 7 (ADU Bedroom 107) | casement 2'-6" × 3'-0", head 6'-8", so sill = 44" exactly | Could Not Evaluate: the clear opening's bottom sits at or above the frame's, so it can't be shown ≤ 44 |
| 10 (Bedroom 203) | 2'-0" × 2'-6" = 5.0 sq ft nominal | **Fail** under 1030.2 even at the 5.0 grade-floor limit, since net < nominal → room **Fail** |
| 12 (`BEDRROM` 205) | single hung 3'-0" × 4'-0" | Could Not Evaluate. The typo matches as a bedroom, and the match is noted |
| 13 (Bedroom 205) | **FIXED**, marked egress | **Fail**: it doesn't open (1030.1.1 / 1030.2) → room Could Not Evaluate because of window 12 |
| 20 (Bedroom 301) | head 8'-0" − 3'-0" gives a 60" sill | **Fail** under 1030.3 → room **Fail** |
| Guest Bed 303 | window 21 not marked egress | Decision 3 below; the recommendation is Could Not Evaluate, flagged |
| 4 (Office 102) | `3' - O"` OCR damage | Not Applicable; flagged as a possibly ambiguous sleeping room, and the OCR damage is flagged |
| Living, kitchen, laundry, bath, hall, stair | — | Not Applicable |

**Decision 5 changed after the review.** Sonnet pointed out that "about half opens" is not a true upper bound: a three-panel slider opens two thirds, and single-hung sashes can be unequal. The half-bound is now shown as a labelled note only, never as the proof of a Fail. No fixture verdict changes either way.

**Image check for the eval set (2026-11-08).** The brief does not ask us to verify the HTML against the sheet images. We did a light check anyway, because the expected verdicts above should rest on what the sheet shows, not only on the HTML.
- **Method:** Opus read `instructions/readme_images/window-schedule.png` and `code-analysis.png` by eye, and compared every row against the HTML and the parsed JSON.
- **Result:** no differences.
  - All 17 window rows match cell for cell, including the OCR damage, which is also in the image: `3' - O"` (window 4), `BEDRROM` (window 12), `2'-6"` without spaces (window 7), and `SCREE N` in the header.
  - All 12 code-analysis rows match, including the split labels `FIRE SPRINKLE RS` and `GRADE PLAN E`.
- **What this does not show:** net clear opening, sill height and grade level are not on either sheet. They stay Could Not Evaluate inputs, as planned.
- **User spot-check (done):** confirmed windows 7, 10, 13, 20 and 21, and the 504.3 cells for R / V-B and I-4 / III-B, including footnotes d and g on I-4 NS and `h` on R. Table-wide footnote `a` is on the image's title, which the HTML omits; the spec declares it.
- **Decision 3 decided:** Guest Bed 303 is Could Not Evaluate, flagged.

**Run in parallel with the build** (optional): draft the deliverable `NOTES.md` for Ichi. The expected-verdict table above should be spot-checked by you rather than generated again.

**Open decisions for the user,** with recommendations. These are from the outline's section 8.

| # | Decision | Recommendation |
|---|---|---|
| 1 | Architect's allowable height (60) disagrees with the table (40) | Keep the single height finding the brief asks for, and flag the mismatch inside it. Also list it at the top of the report under "needs attention". |
| 2 | Frame-deduction assumption | Use no assumption: Could Not Evaluate, showing the nominal upper bound and what would settle it |
| 3 | Bedroom with no window marked egress (Guest Bed 303) | Could Not Evaluate, flagged prominently. It becomes Fail only if the room has no window that could comply even at nominal size. Sonnet agrees, but notes a Fail is also defensible because no opening is designated. Opus, checking the code text: 1030.1 (line 13) requires a complying opening to *exist*, not to be marked on the schedule. Window 21 (casement, 10 sq ft nominal, 32" sill) could comply, so the documents don't decide it: Could Not Evaluate, flagged "no opening designated; ask the architect". It is a Fail only if no window in the room could comply, and even then the finding says "unless Exception 2 (an exit door) applies" (line 19). **Your call.** |
| 4 | Grade-floor opening (5.0 vs 5.7 sq ft) | Decide only when both limits give the same result. Otherwise Could Not Evaluate, which needs the grade from the civil sheet or elevations. |
| 5 | Single-hung and slider upper bounds | **Revised after the Sonnet review:** show them as a labelled note, never as the proof of a Fail. A three-panel slider opens 2/3, so "half" isn't a true bound. |

**Session note.** This session's context is very long. The rest of the work should start in a fresh session from this section, `codeStore/DESIGN.md` and `htmlParser/PLAN.md`. The steps above are best done in order in one session: they share a finding model and the report layout, and splitting them risks two report formats.

## How the work is guided

- **Two independent passes on every design decision.** Opus leads and builds. Sonnet reviews independently: it gets the files and the question, not Opus's conclusions. Disagreements are surfaced to the user rather than settled silently.
- **Expected values are typed in by hand from the printed source**, the table image, never generated from parser output. Tests compare the parser against those hand-typed values.
- **Scripts first.** Deterministic, testable code is preferred over LLM calls wherever reasonable (user decision, 2026-11-08).
- **Scope control.** The session is kept to `tests/` and `src/services/htmlParser`. Files from elsewhere are copied in only with approval.
  - Process correction (2026-11-08): early on, Claude read outside `tests/` without asking. It now stays scoped.

## Phase log

### Phase 0: Fixture analysis and plan (2026-11-08)

Opus and Sonnet independently catalogued the traps in the three fixtures. They agreed on all hand-resolved Table 504.3 cells.

Key findings:

- **504.3 HTML:**
  - Every cell has `colspan=""` / `rowspan=""`, which must count as 1.
  - Headers are `<td>` inside `<tbody>`, marked only by a CSS class.
  - Footnote markers sit in `<sup>`. A naive parse produces `NSb`.
  - Rows are short because of rowspans: the H-1… `S` row has 1 cell, and the I-1 Condition 2 `S` row has 4.
  - The R group has 4 sub-rows in the order NS, S13D, S13R, S.
- **Window schedule:**
  - A 2-row header whose second row is `<td>`.
  - Empty `<th>` cells, two `TYPE` columns, and a separator row.
  - OCR errors: `3' - O"`, `BEDRROM`, and `SCREE N`.
- **Code analysis:** words split across lines, e.g. `FIRE SPRINKLE RS` and `GRADE PLAN E`.
- **Project-level finding:** R / S13D / V-B = **40 ft**. The architect claims 60 ft allowable, and the building is 41'-6".
  - The advisor model first asserted 60. Checking against the printed table image caught the error.

### Phase 1: HTML parser (2026-11-08)

Python standard library only. Three layers:

1. **grid:** spans resolved, inherited cells flagged, `<sup>` turned into footnotes, raw text kept, both readings of a line-broken word kept.
2. **layout:** title, header, separator and data rows, plus column header paths.
3. **projections:**
   - code table → keyed cell records with exact lookup;
   - schedule → one record per row;
   - code analysis → key/value pairs.

Results:

- Code tables use an explicit spec (`specs.py`) that the parser verifies against. Nothing is auto-guessed for law tables.
- All 144 cells of 504.3 match the hand-typed expected values.
  - A test assumption was wrong, not the parser: "sprinklered ≥ unsprinklered" fails for S13R and S13D, because R / NS / I-A is UL but S13R and S13D cap at 60. The invariant was narrowed to `S` vs `NS`.

### Phase 1a: Structure scenario suite (2026-11-08)

- 30+ small HTML tables, each isolating one way a real table can differ. For example: headers in plain `<td>`, transposed tables, group rows, repeated headers, `1,000` / `1/2` / `10-20` values, `<sup>` used for units, two key/value pairs per row, nested tables.
- Synthetic values are labelled **not code**.
- Sonnet review hardened the runner:
  - each known gap must fail with its own signature;
  - a gap that starts passing fails the run;
  - unknown expectation keys are rejected.
- The review confirmed two real bugs: warnings leaking across tables, and nested-table text glued together.

### Phase 1b: Structural header detection (2026-11-08)

- Headers are now found from structure, not from `<th>` or bold:
  - **start:** a row with merged cells and no values;
  - **extend:** through rowspans, then through column-group children, then through `<th>` rows.
- Fixed 5 gaps: plain-`<td>` headers, real 504.3 with bold removed, numeric header labels, the real schedule with `<th>` removed, and a bold first data row.
- Added guard scenarios so the new rules can't overreach.

### Phase 1c: HTML parsing gaps, project tables first (2026-11-08)

Scope was narrowed to parsing only; the store contract moved to 1d. Each fix had a failing scenario waiting, so "done" meant those scenarios flip to passing with nothing else breaking.

| Fix | Scenarios | What changed |
|---|---|---|
| `<p>` / `<div>` / `<li>` inside a cell are line breaks | P08 | `BED`/`ROOM 101` now reads `BED ROOM 101`, with `BEDROOM 101` kept as a join candidate instead of silently glued |
| Warnings tracked per table | P10 | A nested-table warning in table 2 no longer appears on table 1 |
| Nested-table cells separated by spaces | P11 | `outer in1 in2 in3 in4`, not `in1in2in3in4`; still warned |
| Repeated header dropped and reported | P04, M10 | Body rows that reprint the header block exactly (case and spacing aside) are removed from data, listed in `repeated_header_rows`, and warned. No fake window named "SYMBOL"; no duplicate keys in a law table |
| P15 tie-breaker + review item | P15 | A plain column already labelled in the header (no merge down) can't have a child label under it, so the row is data. The alternative reading is recorded in `review_items` with the exact override (`header_rows=2`) |
| Key/value variants | P05, P06 | `KeyValueSheet.mode` is `label_value`, `paired` (label/value/label/value) or `inline_colon` (`LABEL: VALUE` in one column; leading cells without `:` are the title) |

New in the output:
- **`review_items`** (layout, records, matrix, kv): readings the parser had to choose between. The chosen reading is used; the alternative is recorded. Separate from `warnings`, which are parser-quality notes.
- **`repeated_header_rows`** in the layout, and **`mode`** on key/value sheets.

Guard added: **P16**, a 4-column `label | value | unit | note` sheet. Even width alone must not trigger paired reading; a repeated "label" in column 2 (`FT`, `FT`) shows it is a unit column. Paired mode, when chosen, always adds a review item. A mutation check confirmed P16 fails without the rule. Advisor review then found that the P15 tie-breaker could demote an all-`<th>` child row to data. It now yields to `<th>` rows, guarded by **P17** (also mutation-checked).

The real fixtures' parsed data is unchanged; the only differences are the new empty fields.

**Sonnet review of 1c (independent, 2026-11-08).** Sonnet got the code and the questions, not Opus's conclusions. It found five real failures, all reproduced by Opus and now fixed, each with a scenario:

| Finding | Fix | Scenario |
|---|---|---|
| Paired mode accepted distinct units or references in column 2 (`SF => gross`, `IBC 304 => Business`) | Later label columns must look like word labels: no unit tokens, digits, or `SEE`/`PER`/`IBC`/`TABLE` prefixes | P18 |
| Several `LABEL: VALUE` lines in one cell became one entry (`A => 1 B: 2 C: 3`) | Each line is an entry; a wrapped line without `:` continues the previous value (warned) | P19 |
| A first data row equal to a one-row header was silently deleted | A repeat must follow real data. Dropping is now a review item, not a warning, and keeps the dropped rows' text. Footnote marks count in the match. | P20 |
| An unclosed `<table>` lost the next table's text | A `<table>` outside any cell starts a new table, with a warning | P21 |
| The P15 tie-breaker mis-keyed a units row (`(hr)` under ELEMENT) | Parenthesised or unit-token cells under a plain label don't count as conflicts | M20 |

Also from the review: **`review_items` are now structured** (`code`, `rows`, `cols`, `chosen`, `alternative`, `override`, `message`), so scripts can filter them. Codes so far: `header.row_read_as_data`, `header.repeat_dropped`, `kv.paired`.

Deferred to 1d, where the output contract is designed: structured warnings (code and scope); table identity on each object (`table_index`); one source for `review_items` (now copied from the layout to each projection); `mode_basis`. Also deferred: a 4-column key/value sheet with its own header row (`ITEM | VALUE | NOTE | REF`) is still read as pairs, and a bold or `<th>` header followed by a plain-text row stops without a review item (P14 behaviour, which is confident because the styling differs).

Where Sonnet agreed with the design: recording the chosen and alternative readings together; not guessing flat headers; the `header_rows=N` override named in the message; per-table warnings; columns keyed by id, not header text.

Known limits, recorded:
- Repeated-header matching is exact. An OCR typo in the reprinted header (e.g. `SYMBQL`) leaves it as a data row. Near-matching is a content signal for later.
- Inline-colon splitting uses the first `:`. A label containing a colon (rare) would split wrong.

### Phase 1d: Store contract, as first proposed (built below)

Sonnet reviewed the store for a scripts-first consumer. Agreed scope:

- **Lookup result with explicit status:** `found` / `not_found` / `invalid_input`.
  - Today, `None` can't distinguish "no such cell" from "typo", which is the most dangerous confusion for a code checker.
- **Exact matching only in the store.** A separate rule-based resolver will handle wording (`R-3` → `R`). Its format is decided now and it is built later.
- **Answers carry their conditions.** A lookup returns the footnotes that apply, and anything missing to evaluate them (`unevaluable: needs X`).
- **Identity and indexing:** provision IDs that include the edition (`IBC:2018:T504.3`), a nested index, and a minimal document manifest that records which documents we do not have.
- **Repeatable, lean output:**
  - no timestamps;
  - relative paths;
  - the bulky audit grid moved to a separate file;
  - the stored sentence dropped in favour of on-demand rendering.
- **Validation:** a schema and validator built on the standard library, plus tests for determinism, an exhaustive sweep, bad input, and validator mutations.
- (The parser fixes first listed here were done in 1c.)

### Phase 1d: Store contract, as built (2026-11-08)

This phase added three things:
- a new package, `src/services/codeStore` (store, lookup, validator and CLI);
- a hand-written `tests/fixtures/manifest.json`;
- a generated, committed `tests/fixtures/store/`.

The contract itself is in [`DESIGN.md`](services/codeStore/DESIGN.md).

- **Lookup never raises; the status says what happened.** Every problem is listed, not just the first.

  | Status | Error codes |
  |---|---|
  | `found` | none |
  | `not_found` | `no_cell`: each value is valid, but no cell has that combination |
  | `unavailable` | `unavailable_document` or `not_loaded` |
  | `invalid_input` | `missing_dimension`, `unknown_value` (with the allowed values), `unknown_dimension`, `invalid_type`, `unknown_provision` |
- **Citation with the printed labels.** The README's worked example is a golden test: B / NS / II-B → 55, cited as ``Table 504.3, row `A, B, E, F, M, S, U` / `NS`, column `II-B` ``. The project's own cell, R / S13D / V-B, returns **40 ft**.
- **Conditions travel with the value.** Each footnote mark is recorded where it is printed: on the table, a row label or a cell. Table-wide footnote `a` is on every cell. It is declared in the spec with its source line, because the scrape dropped the title row.
- **Incompleteness can't be missed.**
  - Footnote text isn't loaded yet, so a found value that has footnotes carries `limitations: [conditions_text_not_loaded]` and `is_complete: false`.
  - `numeric_limit` gives `inf` for UL, so a height comparison never meets `None`.
- **Manifest of missing documents.** It lists 25 documents, 21 of which we don't have. Each missing one says what needs it.
  - Code: IBC chapter 3 and 310, chapter 6, 504.1–504.2, Table 504.4, 903, 202, chapters 4–5, 1510.2.4 and 1030.4; the IEBC; IFC 1103.5; NFPA 13, 13R and 13D; the Meridian Falls amendments.
  - Project: floor plans, elevations, window details, building sections, civil sheet C1.0.
- **Deterministic, verifiable output.**
  - No timestamps, and relative paths only.
  - The audit grid goes in a separate file, named with a Windows-safe slug.
  - `Store.load(path, manifest=...)` rebuilds from the sources and refuses a store.json that differs.
- **Parser side.**
  - Warnings carry codes (`grid.ragged_row`, `records.duplicate_header` ...).
  - Every object has a `table_index`, and review items live in one place.
  - The spec id equals the manifest id (`IBC:2018:T504.3`).
  - `sentence` is rendered on demand instead of stored.
- **An advisor check before building caught four design issues:**
  - colons in sidecar filenames, which break on Windows;
  - "document unavailable" filed as invalid input;
  - footnote `a` deferred, although 1d had promised it;
  - two different ids for one table.

**Sonnet review of 1d (independent).** The lookup itself held up: all 144 cells are reachable, no lookup returns a wrong cell, matching is strict, and the output is byte-for-byte deterministic. It found these real gaps, all now fixed and tested:

| Finding | Fix |
|---|---|
| `found` with unloaded footnotes looked final | `limitations` and `is_complete` |
| `value` is `None` for UL, so `41.5 <= None` crashes (or `or 0` gives a false Fail) | `numeric_limit` (`inf` for UL) |
| Results shared data with the store, so editing a result changed later lookups | Results are deep copies |
| `lookup(P, provision_id=...)` raised an error | The id is positional-only; odd calls return `invalid_input` |
| The validator passed misleading edits: value 40→140, NaN, wrong unit, swapped keys, a false printed label, dropped footnote `a`, `conditions_loaded: true` with no text | Keys and ids re-derived from dims and labels; each value checked against its printed text, kind and unit |
| A consistent edit (value and printed text both changed) still passes any shape check | `Store.load(..., manifest=...)` rebuilds and compares bytes |
| The manifest missed 504.1–504.2, Table 504.4, chapters 3 and 6, NFPA 13, 13R and 13D, and building sections | Added. The reason 1030.4 is missing is now structured (`why_unavailable`) |
| DESIGN.md disagreed with the code about `unavailable` | Rewritten to match |

**Disagreement recorded for review.** Sonnet would load the footnote text now, in phase 1, because footnote `h` concerns sprinklering new Group R buildings, which is exactly this project. Opus kept it in phase 2 to hold the phase boundary, since the `is_complete` contract already stops anyone treating the result as final. **Resolved (user, 2026-11-08): phase 2,** as Opus recommended. When phase 2 loads the notes, footnote `h` is the first one a Check 1 result depends on.

Deferred:
- a separate status for "not loaded yet";
- `dims` always a list;
- check-level policy for incomplete results (phase 3).

### Phase 2–4: plan steps 1–7 built (2026-11-08)

New package `src/services/planCheck`; deliverables at the repo root (REPORT.md, NOTES.md for Ichi, findings.json). The user approved moving them there from `src/deliverables/` on 2026-11-08.

| Step | What was built | Where |
|---|---|---|
| 1 | Notes loaded: footnotes a–h (lines 19–33), legend per sub-row (line 15) and shorthand (37–39). `conditions_loaded: true`. Each reference is linked to a manifest id via new `covers` regexes (longest pattern wins; an unmatched reference is kept as `unlisted`) | `codeStore/table_notes.py`, manifest `covers` |
| 2 | IBC 1030 cited constants with line and quote; `verify_quotes` runs in the CLI and in tests; brief quotes are tested too | `planCheck/citations.py` |
| 3 | Resolver in the DESIGN.md format; a rule without `cites` is refused at import | `planCheck/resolver.py` |
| 4 | Code-analysis aliases using join candidates; schedule column roles by alias, with TYPE columns told apart by order and confirmed by content; feet-and-inches parser with OCR flags; room classifier | `facts.py`, `units.py`, `rooms.py` |
| 5 | Check 1 and Check 2, with 25 named policies, each tested (`test_every_policy_has_a_test`); a guard test checks that no rule names a fixture window or room | `checks.py`, `policies.py` |
| 6 | CLI; a test checks the committed REPORT.md and findings.json equal the tool output | `__main__.py`, `report.py` |
| 7 | Eval set (24 findings and 3 attention items) and scorer; 24/24 pass | `tests/fixtures/expected/verdicts.json`, `evals.py` |

**Store contract change (phase 2, as planned).** Four store tests that asserted the unloaded state were inverted:
- footnote text is now present;
- `is_complete` is true;
- the mutation cases now cover "text differs from its footnote" and "loaded but no text".

Lookup conditions now carry `source` (the notes line) and `references` (manifest id plus status). The validator checks that condition text matches the loaded footnotes.

**Verdicts match the expected-verdicts table:** H-1 Fail by 1'-6"; W-10, W-13 and W-20 Fail; R-203 and R-301 Fail; R-101, R-107, R-205 and R-303 Could Not Evaluate; everything else Not Applicable. One finding the table did not list: **W-10 also fails on sill**, since the derived frame sill is 80 − 30 = 50 in.

**Sonnet review of the checks (independent; it was given the files, and decided the verdicts before running the tool).** It agreed with every fixture verdict. It found six real bugs, all fixed, each with a regression test in `test_review_regressions.py`:

| Finding | Fix |
|---|---|
| Footnote d (NS is for existing buildings) was applied to any NS row on new work, e.g. the README's B / NS example | Applies only when the looked-up cell carries footnote d |
| `41.5 FT` was read as 5 ft | Decimal feet are supported; a match can't start inside a number |
| No EGRESS column gave window-level Fails for fixed windows | Not Applicable at window level; the room finding decides |
| An unnumbered `BEDRROM 2` became a different room from `BEDROOM 2` | The room key spells out OCR near-misses; `BED 2` and `BATH 2` stay apart |
| `BEDROOM BATH 206` was classed as a bedroom | A compound name is ambiguous and flagged |
| A bare `840` in a net-clear column was read as 840 sq ft | Square inches are converted; a bare number outside 0–50 is refused |

Also from the review: the fixture example `BEDRROM 205` was removed from the policy text.

**Disagreement, for the user:** Sonnet argued that a window meeting every *measurable* criterion should Pass, with hardware, screens and public way listed as unverified. Opus kept `POL-E-UNSEEN`, under which those always-unseen items keep a window at Could Not Evaluate, so no window can Pass from a schedule alone. It is one rule to change, and no fixture verdict depends on it.

**Not done (recorded):**
- R-2 scoping needs exits per story, which are not extracted, so it gives Could Not Evaluate.
- A blank EGRESS cell is read as "no"; the room roll-up is the safety net.
- `ONLY` in the partial-coverage guard can over-trigger, but it is safe (it gives Could Not Evaluate).
- IBC 1030 stays `not_loaded` in the store; its limits are cited constants by design.

### Phase 5: REPORT.md redesign after three reviews (2026-11-08)

The work moved to the `ichi-assignment` repo, where the phases are recorded as git commits. The report was reviewed three times:
- Sonnet, round 1;
- Opus, round 2, written down before reading Sonnet's second review (`report-review-round2-opus.md` in the session notes folder);
- a fresh Sonnet, round 2, which had seen neither earlier review.

**What all three agreed on:**
- every verdict and number is right;
- the report was 585 lines and repeated each finding four or five times;
- internal ids and file paths leaked into the body;
- Fails should read as correction items, grouped by room;
- the CNE items should become requests to the architect;
- the window blocks should collapse into one table, with the always-unseen requirements (hardware, screens, public way) stated once.

**Found by both Sonnet reviews:** the schedule skips window numbers 9 and 15–19. Opus missed this.

**Judgement calls, decided 2 to 1 for the current verdicts:**
- R-203 and R-301 stay Fail, with Exception 2 stated. Sonnet round 1 preferred Could Not Evaluate.
- W-7 stays Could Not Evaluate and is raised as "expect a Fail". Sonnet round 1 preferred Fail.

**Built. These are generic rules, not fixture-specific:**

| Change | Where |
|---|---|
| `POL-GEN-SCHEDULE-GAPS`: missing numbers in an all-numeric schedule are listed | `checks.schedule_gaps`, attention `schedule_number_gaps` |
| `POL-E-AT-LIMIT`: a frame sill exactly at 44 in, or a partial-opening note at or below a minimum, is flagged `sill_at_limit` / `partial_opening_at_minimum` and listed first as `likely_fails`. Verdicts don't change. | `checks.evaluate_window` |
| Rows are counted from 1, header rows included (they were 0-based grid rows) | `checks._row` |
| The "Opens" criterion cites 1030.2.1 (normal operation), not 1030.1.1 (keys or tools) | `evaluate_window` |
| `Criterion.brief` (a short plain statement) and `Criterion.flags` | `findings.py` |
| The architect's-height message names the sub-rows (`S` and `S13R`) instead of a garbled list of cells | `check_height` |
| The report is rewritten in this order: corrections, checks, requests, height, rooms table, egress-window table, NA table, appendix (code lines, source rows, rules, inputs). 238 lines. | `report.py` |
| The scorer reads verdicts from headings and table rows anywhere, and flags an id shown with two verdicts | `evals.report_verdicts` |

Tests: planCheck 86, adding `test_pol_e_at_limit` and `test_pol_gen_schedule_gaps`. The eval set gained the W-7 and W-12 flags and two attention items, all marked `spot_checked: false`. The scorer passes 24/24.

**Verification review (fresh Sonnet, old vs new report against the sources):** no factual errors, and every anchor resolves. Its brief-compliance gaps were fixed:
- the result line now says the 6 Fails are 4 correction items;
- the details request covers operating hardware (1030.1.1) and screen release (1030.5), which the §6 legend promises;
- §5 states the scope (occupancy in 1030.1 item 2, story from room number), gains a Story column, and notes the room whose name is spelled two ways;
- §7 is renamed "Windows: Not Applicable" and shows each window's EGRESS cell and code section;
- Appendix C lists every finding that uses each rule, untruncated;
- W-12 reads "exactly the 24 in minimum, leaving nothing for the frame" instead of "at or below";
- W-13's area cell gives its basis: "Fail (does not open)".

Status: planCheck 86, codeStore 38, htmlParser 85 (8 skipped) pass; eval 24/24; REPORT.md 241 lines.

### Phase 6: confidence levels (2026-11-08)

This is the brief's secondary objective: "a confidence level on each finding, and some thought on what a reviewer should do with a low-confidence Fail".

**Built:**
- `planCheck/confidence.py` assigns `confidence` and `confidence_reasons` to every finding after the checks run. It never changes a verdict.
- `Criterion.basis` (printed or derived) is set where the sill criterion is built, and replaces a string check on "frame sill".
- `Finding.unresolved` lists documents not provided that could reverse a Fail:
  - for the height, only footnotes that point to *exceptions*, so footnote a counts and footnote h (the 903.2.8 sprinkler requirement) does not;
  - for a room Fail, Exception 2 and the floor plans.
- The report shows confidence on each correction in §1, with its reasons, and gives one paragraph of guidance there. There is a header count, a line in §4, and a column in §5, §6 and §7.
- The eval scorer checks `confidence` where the eval set gives one. It is given for the 6 Fails and W-4, typed by hand from the rule.

**Considered and rejected:**
- A numeric score: the brief asks for a level.
- Lowering confidence for OCR on numbers: POL-GEN-OCR already turns such a Fail into CNE.
- Lowering it for the R-3 to R reading: the brief itself gives that rule.
- A margin threshold on derived sills: any number would be tuned to these fixtures. A derived-only Fail is Medium whatever its margin.

**Result on the fixtures:**
- W-10 and W-13 are High.
- H-1, R-203 and W-20 are Medium.
- R-301 is Low: a derived sill and an unseen exit door.
- W-4 is Low: an office read as not a sleeping room.
- R-205 and W-12 are Medium: BEDRROM.

Status: planCheck 87, codeStore 38, htmlParser 85 (8 skipped); eval 24/24.

### Input: Check 1 requirements, and what they change in the store contract, phase 1d (2026-11-08)

Check 1 asks for one finding for the building. It reads the project's occupancy, construction type, sprinklers and height, looks up the matching 504.3 cell, and compares the two heights. The finding cites the cell, as in this example: *row `A, B, E, F, M, S, U` / `NS` / column `II-B` = 55*.

Changes to the store contract:

1. **Printed labels in every lookup result.** Each result carries a `citation` with the labels exactly as printed: the row label, the sub-row, the column, and the column header path. The finding can then cite the cell without rebuilding labels.
2. **Two kinds of invalid input.**
   - `missing_dimension` means the project didn't supply a value, for example no construction type. Check 1 maps this to Could Not Evaluate.
   - `unknown_value` means a value was supplied but isn't in the table, for example `R-3`. That's the resolver's job.
3. **Sprinkler sub-row choice is traceable to the code.** The legend and the shorthand in the notes (S ↔ 903.3.1.1 ↔ NFPA 13, S13R ↔ 903.3.1.2 ↔ 13R, S13D ↔ 903.3.1.3 ↔ 13D) go into the store with their line numbers. The resolver's sprinkler rules cite those lines; they are not hand-typed aliases.
4. **Table-wide footnotes.** Footnote `a`, on the table title ("see Chapters 4 and 5 for exceptions"), applies to every cell. It is returned as a condition, with its references marked as documents or sections we don't have.
5. **The README's worked example becomes a golden lookup test.** B / no sprinklers / II-B returns 55 with the exact citation labels.

The architect's own "allowable height" is project data, compared in phase 3. It does not affect the store.

### Input: the glossary, and how authority is kept straight (2026-11-08)

The README's terms table is saved verbatim as `tests/fixtures/reference/glossary.md`. It is the challenge author's plain-language explanation, **not code**. Sonnet reviewed it independently, and Opus agreed with most of the review.

**Every stored record carries its source and authority.**
- The authority is one of `code_text`, `challenge_brief`, `project_submitted` or `project_decision`.
- The source also gives the file and line numbers, tagged per section where one file mixes authorities.
- Example of a mixed file: the "sprinkler shorthand" in the 504.3 notes is challenge-author text sitting in the code folder.

**Only `code_text` can be cited as code.**
- The validator rejects a citation that points at anything else.
- Rules taken from the brief are reported separately as an *interpretation*, with their authority shown. For example: "R-3 read as row R (challenge brief; IBC 310 not available)".

**Where the glossary is looser than the code, the code wins.** These differences are recorded for phase 3:

| Topic | Glossary says | Code says | Matters for |
|---|---|---|---|
| Building height | Measured from grade plane (no top end given) | Measured to the *average height of the highest roof surface* | Check 1. It matches the analysis wording "TO AVG. HT. OF HIGHEST ROOF SURFACE". |
| Sill height | Floor to the bottom of the *window* | 1030.3 measures to the bottom of the *clear opening* | A sill derived from nominal size (head height − window height) is not the code figure. Window 20's derived 60" must be labelled nominal and derived. |
| Grade-floor opening | Not defined | Defined relative to *finished ground level* | The 5 sq ft exception needs ground-level data we don't have. |
| Egress applicability | "Most residential buildings, every bedroom" | R-2 conditionally; R-3 and R-4; below the 4th story; with exceptions | Check 2 scope |
| Grade plane | "Average ground level" | Finished ground level at the walls, with slope and 6 ft rules | Background only |
| Sprinklers | "Better system → taller" | Not always: R / NS / I-A is UL, but S13R and S13D cap at 60. The legend also says "equipped *throughout*". | Partial coverage must resolve to unsure, never to S13x |

**Scope.**
- In phase 1d (store contract):
  - the source/authority field;
  - the rule that only `code_text` can be cited;
  - the shape of the interpretation field;
  - manifest entries for documents we don't have: IBC 310 (occupancy classification), IBC 903 (sprinklers), the full IBC 202 definitions, and the Meridian Falls amendments.
- Deferred:
  - loading the glossary itself (phase 2);
  - abbreviations and the sleeping-room name list (phase 3/4);
  - feet-inch and type-mark logic (phase 4).

**Opus pushback on Sonnet (recorded for review).**
- Sonnet proposed that a finding resting on brief text alone should be "unevaluable". Opus disagrees for rules the brief explicitly gives. The brief is the client's specification for this tool, and treating it as unusable would make every Check 1 a Could Not Evaluate (R-3 → R relies on IBC 310, which we don't have). Instead, a brief-based interpretation may support a verdict, but:
  - it is always disclosed in the finding;
  - the *limit value* itself must always come from `code_text`.
- Sonnet tagged the sprinkler shorthand `project_decision`. It is the challenge author's text, so it is tagged `challenge_brief`, with IBC 903.3.1 recorded as unavailable.

### Input: scope of the inputs, and what wins (2026-11-08)

The requirements say four things:

- Missing drawing sheets (floor plans, elevations, window details, the civil grade-plane sheet) mean **Could Not Evaluate**.
- **The code files are the source of truth.** Where a summary disagrees with a code file, the code file wins.
- `table-504.3-notes.md` supplies the caption, legend and footnotes that the scrape dropped.
- **"Don't build your tool around these two particular files"**: another project's tables will have different values, columns, column order and OCR mistakes.

What this changes:

1. **Authority order is `code files` > `challenge brief` > anything else.** The whole of `table-504.3-notes.md` counts as code-file content. That includes the sprinkler shorthand (903.3.1.1/2/3 ↔ NFPA 13/13R/13D).
   - This reverses the earlier `challenge_brief` tag on the shorthand. It is now cited from the code file, marked `supplementary: true` because it was appended for cross-referencing.
2. **Missing project documents are recorded just like missing code documents.** The manifest lists the project sheets we don't have: floor plans, elevations, window details and the civil sheet. A check can then say "needs window details (net clear opening)".
3. **The priority for the rest of the HTML phase shifts toward project tables.**
   - "The two files" are the project files, so robustness to *other projects'* schedules and code analyses matters most.
   - That moves P04 (repeated header), P05/P06 (key/value variants), P08 (block tags) and P09 (dropped cell) ahead of the more unusual code-table gaps (M05, M06, M11, M18).
4. **The code tables themselves are the same for every project on IBC 2018,** so the per-table spec approach is unaffected.

## Decisions

| Date | Decision | By | Why |
|---|---|---|---|
| 2026-11-08 | Python, standard library only | User | Nothing to install; runs anywhere |
| 2026-11-08 | Code in `src/services/htmlParser`, tests in `tests/services/htmlParser` | User | |
| 2026-11-08 | Explicit spec per code table, verified, not auto-detected | Opus, Sonnet agreed | Law tables are few; wrong guesses are unacceptable |
| 2026-11-08 | Keep raw OCR text; record repairs, never fix silently | Opus, Sonnet | Submitted data must be traceable |
| 2026-11-08 | Parser mechanics warnings are internal. Missing or incorrect submitted data and missing code go to the report. | User | Report is for the plan checker, not parser debugging |
| 2026-11-08 | Uncertainty that affects a value a check uses travels with that value, as data | Opus, agreed by user | Lets a check say "Could Not Evaluate" and explain itself |
| 2026-11-08 | Scripts first, LLM only where scripting can't reasonably do it | User | Testable, reliable, cheaper |
| 2026-11-08 | One code store for all code item types (cells, footnotes, legend, prose, definitions), with references and a "we don't have it" status | Sonnet proposed, user agreed | Footnotes and prose are the same kind of object; avoids a rewrite |
| 2026-11-08 | Don't classify reference meaning ("requires", "excepts") at ingest; don't split multi-occupancy cells | Opus (pushback on Sonnet) | Avoid presenting guesses as fact; one printed cell, one record |
| 2026-11-08 | A small manifest declares code documents (id, edition, files) | User | Explicit links beat filename matching |
| 2026-11-08 | Header-or-data ambiguity (P15): **treat as data and record for review** | User | A wrong extra record is visible; a lost record is invisible |
| 2026-11-08 | Every record carries source and authority; only `code_text` can be cited as code; brief rules are disclosed as interpretations | Sonnet proposed, Opus agreed | The glossary and brief are looser than the code in places (height, sill, sprinklers) |
| 2026-11-08 | Brief-stated rules (e.g. R-3 → R row) may support a verdict if disclosed; limit values must come from code text | Opus (pushback on Sonnet) | Otherwise every check is Could Not Evaluate for lack of IBC 310 |
| 2026-11-08 | Code files are the source of truth (the whole notes .md counts, including the sprinkler shorthand); missing project sheets are recorded like missing code | Requirements text | Stated in the brief; supersedes the earlier `challenge_brief` tag on the shorthand |
| 2026-11-08 | Rest of the HTML phase prioritises project-table robustness over unusual code-table shapes | Opus, from the requirements | "Don't build around these two files" refers to project tables |
| 2026-11-08 | Prose thresholds (1030): direction deferred to next phase. Recommendation is script-extracted limits marked "unreviewed" until confirmed. | User (pending) | |
| 2026-11-08 | Phase 1c = HTML parsing gaps only, project tables first; store contract moved to 1d | User | Keep each step solid before the next |
| 2026-11-08 | Parser ambiguities go in `review_items` (chosen reading used, alternative recorded), separate from `warnings` | Opus, implementing the P15 decision | A reviewer can see every choice the parser made and how to override it |
| 2026-11-08 | Review items are structured objects; dropping rows is a review item, never just a warning | Sonnet review, Opus agreed | Scripts must be able to filter them; deleted data must be visible and recoverable |
| 2026-11-08 | Store lives in a new package `src/services/codeStore`, separate from the parser | Opus (easy to reverse) | Phase 2 adds non-HTML code documents to the same store |
| 2026-11-08 | Four lookup statuses: found / not_found / unavailable / invalid_input; "we don't have the code" is never "bad input" | Opus; advisor and Sonnet agreed | Could Not Evaluate must say whether the project or the code library is missing something |
| 2026-11-08 | A found value with unloaded footnotes is marked incomplete (`is_complete: false`), not withheld | Opus; Sonnet preferred loading the text now | Keeps the phase boundary without letting a check treat the value as final |
| 2026-11-08 | Checks load the store verified against its sources (`Store.load(path, manifest)`) | Sonnet review | A shape validator can't detect a consistent edit |
| 2026-11-08 | A sleeping room with no window marked egress is Could Not Evaluate, flagged "no opening designated", when some window in it could comply at nominal size; Fail only if none could (unless Exception 2) | User, following the Opus/Sonnet recommendation | 1030.1 requires a complying opening to exist, not to be marked on the schedule |
| 2026-11-08 | Judgement calls become named policy rules in code, each with an id, a citation and a test; the tool never decides case by case | User question on repeatability | The same rules must give the same verdicts on any project |
| 2026-11-08 | Footnote text is loaded in phase 2, not now | User (went with Opus's recommendation) | Holds the phase boundary; `is_complete: false` already stops a check treating the value as final |
| 2026-11-08 | Once footnotes are loaded, `is_complete` is true; footnotes that point to unavailable documents are listed in the finding (`POL-H-FOOTNOTES`), not treated as blocking | Opus (advisor agreed) | Otherwise footnote `a` makes every cell permanently incomplete; the code analysis claims no exception |
| 2026-11-08 | Requirements that no schedule shows keep a window at Could Not Evaluate (`POL-E-UNSEEN`) | Opus; **Sonnet disagrees** (would Pass on the measurable criteria) | A wrong Pass is worse than an honest Could Not Evaluate. **User to decide.** |
| 2026-11-08 | Deliverables (REPORT.md, NOTES.md, findings.json) live at the repo root | User | First written to `src/deliverables/` because of the session scope; the user approved the move |
| 2026-11-08 | Code files are a fixed IBC 2018 library; only project files must generalise | User | Brief, line 92 ("these two particular files", "another project's tables") and line 167 (inputs are code analysis + window schedule); edition fixed at lines 53 and 72. Noted in the root NOTES.md under "How it works" |
| 2026-11-08 | Report redesign (Phase 5): corrections first, then checks, requests and evidence tables; R-203/R-301 stay Fail with Exception 2 stated; W-7 stays CNE flagged 'expect a Fail' | User | Three reviews; both calls 2-1 for the current verdicts |
| 2026-11-08 | Confidence levels (Phase 6, `POL-GEN-CONFIDENCE`): High by default; down one for a derived-only Fail, for a Fail an unprovided exception could reverse, and for a repaired room name; Low for a guessed room use; a room's Fail takes on its failing windows' drops | Opus (stretch goal); open for user review | Brief secondary objective; levels are typed by hand into the eval set, not spot-checked |

## Edge cases recorded for review

These are cases where the parser can't be certain. Each stays in the data with a review flag rather than being guessed.

| ID | Case | Handling |
|---|---|---|
| P15 | Plain-`<td>` header with a merged group and no child labels; the first data row is all text, so it looks like child labels | **Done (1c).** Read as data; `review_items` says the row could be header labels and gives the override `header_rows=2`. Tie-breaker: a plain column already labelled above, not merged down, can't have a header label under it. |
| P05 | A 4-column sheet read as two label/value pairs per row | **Done (1c).** Always recorded in `review_items`, because `label | value | unit | note` sheets look similar (guarded by P16). |
| P04 / M10 | Repeated header after a page break | **Done (1c).** Exact matches dropped and warned; a header reprinted with an OCR typo is still read as data. |
| P03 | Flat header in plain `<td>`, no merges | Not guessed; reported. The caller passes `header_rows=1`. |
| P09 | OCR dropped a middle cell, so later values shift left | Can only be flagged as a short row. Detecting the shift needs value-type checks (phase 3 or 4). |
| — | Project uses IBC "as adopted by the City of Meridian Falls"; we have no local amendments | Record as an unavailable document. Every lookup is conditional on it. |

## Open issues (known gaps), grouped by fix

1. **Body row classification:** footer and notes rows read as data; group sub-heading rows (M06, M09). Repeated headers done in 1c.
2. **Value parsing:** `1,000`, `1/2`, `10-20`, `5%`, `150 gross` (M12, M16, part of M17).
3. **`<sup>` as an exponent vs a footnote:** `FT<sup>2</sup>` silently becomes a footnote (M17). This is the riskiest gap, because it silently changes data.
4. **Label atoms:** `A-1 and A-2`, `H-1 through H-3` (M11).
5. **Spec features:** two column dimensions; group-row dimension; annotation columns (M05, M06, M18).
6. ~~Small parser bugs (P08, P10, P11)~~: done in 1c.
7. ~~Key/value variants (P05, P06)~~: done in 1c.

## Pending from the user

- Spot-check the hand-typed Table 504.3 expected values (`tests/fixtures/expected/table-504.3.expected.json`, `verified_by` is empty).
- Direction for prose thresholds (1030), at the start of phase 2.

## Status

- Parser: 85 tests pass, and 8 known gaps (M05, M06, M09, M11, M12, M16, M17, M18) are verified to fail for their recorded reason.
- Store: 38 tests pass (29 before, with 4 inverted for phase 2, plus 9 new notes tests).
- planCheck: 87 tests pass (`cd tests/services/planCheck && python -m unittest`). The eval scorer passes 24/24, now including confidence.
- Report: `cd src && python -m services.planCheck ../tests/fixtures/code-analysis.html ../tests/fixtures/window-schedule.html -o ../REPORT.md --json ../findings.json`. A test fails if the committed report is stale.
- Remaining gaps are code-table shapes and value parsing; no project-table gap is open except P09 (dropped cell), which needs value-type checks.
- Run them with `cd tests/services/htmlParser && python -m unittest` and `cd tests/services/codeStore && python -m unittest`.
- Rebuild the store after any parser or manifest change: `cd src && python -m services.codeStore build ../tests/fixtures/manifest.json -o ../tests/fixtures/store`. A test fails if the committed store is stale.

# Table-structure scenarios

Small HTML tables. Each one isolates one way a real table can differ from our three fixtures, so the parser is proven against the *shape* of a table and not against one particular file. The expectations live in [`scenarios.json`](scenarios.json), and [`test_scenarios.py`](../../services/htmlParser/test_scenarios.py) runs them.

> **Synthetic values are made up and are not code.** Only the structure is modelled on real IBC tables. Code values must only ever come from the real code fixtures.

## How it works

- **`pass`:** the scenario must pass.
- **`known_gap`:** the scenario must currently fail, **and** the failure message must contain its `gap_signature`.
  - The runner fails if a gap fails for a different reason, such as a typo, a broken fixture or a new bug.
  - It also fails if a gap starts passing. When that happens, flip its status to `pass`.
  - Verified gaps show as *skipped*, with the gap text as the reason.
- **Manifest check:** the manifest itself is validated. It must have unique ids. Every file must exist and appear in the manifest. Unknown `expect` keys are rejected, so a typo can't silently switch a check off.
- **Same data, different shapes:** M01–M07 and M09–M10 carry the same mini dataset in different shapes. Where they can, they assert `same_index_as: M01`, meaning the full key → value index is identical whatever the layout.

Run the scenarios:

```
cd tests/services/htmlParser && python -m unittest test_scenarios -v
```

## Catalogue

### Code tables (law → keyed lookup)

| ID | Shape | Why it matters for other codes | Status |
|---|---|---|---|
| M01 | `<thead>` / `<th>`, rowspanned labels | Control case | pass |
| M02 | Headers are plain `<td>` in `<tbody>`, no bold | A scrape can drop the styling that marks 504.3's headers | pass (structural detection) |
| M03 | Row labels repeated on every row instead of rowspan | The publisher's style must not change the keys | pass |
| M04 | Value columns reordered | Lookups key on header text, not position | pass |
| M05 | Transposed: two dimensions across the top | IBC 508.4-style tables | gap: one column dimension only |
| M06 | Group sub-heading rows (`GROUP R`) instead of a label column | Common in codes and schedules | gap: no group rows |
| M07 | One value merged across columns | Horizontal merges like "NP" across all types | pass |
| M08 | Footnotes on value cells; `NP` and `—` tokens | Table 601-style cells | pass |
| M09 | `<caption>`, title row, and footnote row at the bottom | The table's identity and notes live there | gap: footer read as data, caption dropped |
| M10 | Header block repeated mid-table | Page breaks | pass (1c: repeat dropped and warned) |
| M11 | Labels like `A-1 and A-2` or `H-1 through H-3` | Comma-only splitting misses these | gap |
| M12 | One value column, `150 gross` / `20 net` | Qualifiers change meaning (1004.5-style) | gap: value parsing |
| M13 | Real 504.3 with bold removed | The real-law version of M02 | pass (structural detection) |
| M14 | Values merged vertically | Covers the real 504.3 H-row contract synthetically | pass |
| M15 | Numeric column headers (5 / 10 / 30) | Guards the M02 fix from treating these headers as data | pass |
| M16 | `1,000`, `1/2`, `−5`, `10-20`, `5%`, ` NP ` | Real values aren't all integers | gap: value parsing |
| M17 | `FT<sup>2</sup>` exponent next to a `<sup>a</sup>` footnote | The unit would silently become a footnote | gap |
| M18 | Trailing NOTES column | It annotates rows; it is not a value dimension | gap |
| M19 | No header; the first data row has a merged label | Guard: a merged cell alone must not make a row a header | pass |
| M20 | Units row `(hr)` under a plain label beside a group's child labels | Guard: the P15 tie-breaker must not mis-key unit rows (Sonnet review) | pass |

### Project documents (OCR'd submissions)

| ID | Shape | Why | Status |
|---|---|---|---|
| P01 | Other column names and order, `W x H` size, `W-A` marks, no EGRESS column | Another architect's schedule. The EGRESS column must be reported absent, not guessed. | pass |
| P02 | Real window schedule with `<th>` turned into `<td>` | OCR is inconsistent about `<th>` | pass (structural detection) |
| P03 | Flat header in plain `<td>`, no spans | No signal. Contract: warn, then `header_rows=1` works. | pass |
| P04 | Header repeated after a page break | It would become a fake window named "SYMBOL" | pass (1c) |
| P05 | Two label/value pairs per row | Cover-sheet data blocks | pass (1c: `mode: paired`, with a review item) |
| P06 | `LABEL: VALUE` in one cell | Some OCR passes collapse the columns | pass (1c: `mode: inline_colon`) |
| P07 | `&nbsp;`, `<br>`, nested spans, primes and curly quotes | Keep the feet/inch characters exactly as written for the value parser | pass |
| P08 | `<p>` / `<div>` lines inside a cell | `BED`+`ROOM` silently becomes `BEDROOM` | pass (1c) |
| P09 | OCR dropped a middle cell | Only a warning is possible here; detecting the shifted values needs type checks later | pass |
| P10 | Two tables in one file | Warnings must stay with their own table | pass (1c) |
| P11 | 2×2 table nested in a cell | `in1in2in3in4` gets glued together | pass (1c) |
| P12 | First data row is bold | It must not be absorbed into the header | pass |
| P13 | Two-row `<td>` header grouped only by colspan | A column group implies child labels below it | pass |
| P14 | `<th>` colspan header with a text-only first data row | Children of a styled header must also be styled | pass |
| P15 | Same as P14, but the header is plain `<td>` | Ambiguous from structure alone | pass (1c: read as data, recorded in `review_items` with the `header_rows=2` override) |
| P16 | 4 columns: `label | value | unit | note` | Guard: even width alone must not trigger paired key/value reading | pass |
| P17 | All-`<th>` child row under a plain `<th>` label | Guard: the P15 tie-breaker must yield to explicit `<th>` | pass |
| P18 | 4 columns with distinct units or code references in column 2 | Guard: units like `SF`, `FT` and refs like `IBC 304` are not labels (Sonnet review) | pass |
| P19 | Several `LABEL: VALUE` lines in one cell | Each line is its own entry (Sonnet review) | pass |
| P20 | First data row equals a one-row header | Guard: only a repeat that follows real data is dropped (Sonnet review) | pass |
| P21 | `<table>` never closed before the next | The second table must not be lost (Sonnet review) | pass |

### Gaps grouped by fix

Fixing one item below should flip several scenarios at once:

1. ~~**Structural header detection**~~ is **done**. It fixed M02, M13, M15, P02 and P12, with M19, P13 and P14 as guards. P15 remains as the documented limit.
2. **Body row classification** fixes M09 and M06 (footer/notes rows, group rows). Repeated headers (M10, P04) were done in 1c.
3. **Value parsing** fixes M12, M16 and part of M17. This covers thousands separators, fractions, ranges, percentages and qualifiers.
4. **Label atoms** fixes M11. This covers `and` and `through` ranges.
5. **Spec features** fix M05, M06 and M18. These are `col_dims`, `group_row_dim` and `annotation_cols`.
6. ~~**Small parser bugs** (P08, P10, P11)~~ are **done** (1c).
7. ~~**Key/value variants** (P05, P06)~~ are **done** (1c), with P16 as the guard.

## Adding a scenario

1. Drop `Xnn-short-name.html` in this folder. Start it with a comment saying what it isolates. If the values are made up, mark it `SYNTHETIC`.
2. Add an entry to `scenarios.json` with `id`, `kind` (`matrix` / `records` / `kv`), `title`, `why`, `expect`, and either `status: pass` or `status: known_gap` with `gap` and `gap_signature`. When a gap is fixed, its old text moves to `was_gap` and `fixed_in` names the phase.
3. Run the tests. A new `known_gap` must fail with its signature before the runner accepts it.

**Most useful from you:** real tables from other projects or code sections that broke something, or that look different from all of the above. Copy the HTML in as-is, including any OCR mess, and give the values a few cells should have.

# codeStore: store contract (phase 1d)

The store is what checks query. The parser (`services/htmlParser`) reads HTML. The store holds what was read, says where it came from, and answers lookups with an explicit status.

It lives in its own package, not inside `htmlParser`, because phase 2 adds non-HTML code documents (the notes, IBC 1030) to the same store.

**Run:**

```
cd src
python -m services.codeStore build ../tests/fixtures/manifest.json -o ../tests/fixtures/store
python -m services.codeStore lookup ../tests/fixtures/store/store.json IBC:2018:T504.3 occupancy=B sprinkler=NS construction=II-B
python -m services.codeStore validate ../tests/fixtures/store/store.json
```

**Tests:** `cd tests/services/codeStore && python -m unittest`

## Inputs

- **A manifest** (`tests/fixtures/manifest.json` for this project).
  - It is hand-written and lists every document a check may need, **including the ones we don't have**.
  - Each missing document says what needs it (`referenced_by`), and where known, why it is missing (`why_unavailable`).
  - Paths are relative to the manifest. Nothing is found by filename matching.
- **Specs** for code tables (`htmlParser/specs.py`), named from the manifest.
  - The manifest id is the provision id. The spec's `table_id` must equal it, or the build fails.

`status` is `available` or `unavailable`. `authority` is `code_text`, `challenge_brief`, `project_submitted` or `project_decision`.

## Output

`store.json`, plus one audit grid per table in `grids/<slug>.grid.json`.

- The slug replaces `:` because Windows forbids it in filenames: `IBC-2018-T504.3`.
- Output is deterministic: no timestamps, paths relative to the manifest, one serialisation. Building twice gives identical bytes, and a test checks that the committed store is current.
- There is no stored `sentence`. `htmlParser.render_sentence()` builds it on demand.

A cell record (one per value slot):

```json
{"id": "IBC:2018:T504.3[occupancy=A, B, E, F, M, S, U;sprinkler=NS;construction=II-B]",
 "dims": {"occupancy": ["A","B","E","F","M","S","U"], "sprinkler": "NS", "construction": "II-B"},
 "value": 55, "value_kind": "number", "value_text": "55", "unit": "ft",
 "printed": {"row_labels": {"occupancy": "A, B, E, F, M, S, U", "sprinkler": "NS"},
             "column_header_path": ["TYPE OF CONSTRUCTION", "TYPE II", "B"]},
 "conditions": [{"kind": "footnote", "mark": "a", "attached_to": "table", "text": null},
                {"kind": "footnote", "mark": "b", "attached_to": "row_label:sprinkler", "text": null}],
 "authority": "code_text",
 "source": {"document": "IBC:2018:T504.3", "file": "table-504.3.html", "grid_row": 3, "grid_col": 5, "inherited": false},
 "keys": ["A|NS|II-B", "B|NS|II-B", "..."]}
```

- `dims` holds a list for multi-label rows (`A, B, E ...`) and a string otherwise. Query with one value; the citation carries the printed label.
- Labels containing `| ; = [ ]` are refused at build time, because ids and keys would become ambiguous.
- **Conditions:**
  - Footnote marks are recorded where they are printed: `table`, `row_label:<dim>` or `cell`.
  - Table-wide marks (504.3's `a`, which sits on the title row the scrape dropped) are declared in the spec, with the line in the notes file that shows them.
  - Footnote **text** (phase 2) comes from the notes file the manifest lists with `parse: {"as": "table_notes"}` (`table_notes.py`). The provision gains `notes`:
    - `footnotes`: each with mark, text, line and references;
    - `legend`: per sub-row token;
    - `sprinkler_shorthand`.

    Each condition gets its text, and `conditions_loaded` becomes true. A printed mark with no footnote fails the build.
  - **References** ("Section 903.2.8", "Chapters 4 and 5", "International Existing Building Code") are normalised (`IBC 903.2.8`, `IBC CH 4`, `IEBC`) and linked to the manifest document whose `covers` regex matches most specifically. Each reference carries that document's status. An unmatched reference is kept as `unlisted`.
  - At lookup, each condition carries `source` (the notes file and line) and `references`.

## Lookup

`store.lookup(provision_id, /, **dims) -> LookupResult`. It never raises.

Matching is exact after upper-casing and collapsing spaces, and nothing else: `R-3` is not `R`, and `VB` is not `V-B`.

| status | error code | when | Check 1 reads it as |
|---|---|---|---|
| `found` | — | the cell exists | a value; see `is_complete` |
| `not_found` | `no_cell` | every value is valid on its own, but the table has no cell for the combination (A / S13R) | Could Not Evaluate, never Pass |
| `unavailable` | `unavailable_document` | the document is in the manifest as unavailable (`referenced_by` says why it is needed) | Could Not Evaluate |
| `unavailable` | `not_loaded` | we have the document but it isn't in the store yet (IBC 1030 until phase 2) | Could Not Evaluate |
| `invalid_input` | `missing_dimension` | a dimension is absent, `None` or blank: the project didn't say | Could Not Evaluate |
| `invalid_input` | `unknown_value` | a value the table doesn't have (`R-3`); `allowed` lists the values | resolver's job, then retry |
| `invalid_input` | `unknown_dimension`, `invalid_type`, `unknown_provision` | caller error | bug in the check |

Every problem is listed, not just the first.

**A `found` result carries:**
- `value`, `value_kind`, `value_text`, `unit`;
- `numeric_limit`: a number, `inf` for unlimited, or `None` for anything non-numeric, so `actual <= limit` is never `actual <= None`. In Python it is `math.inf`. In JSON output (`to_dict`, the CLI) it is the **string** `"inf"`, because JSON has no infinity; convert it before comparing;
- `citation`, with the printed labels and a ready string: ``Table 504.3, row `A, B, E, F, M, S, U` / `NS`, column `II-B` ``;
- `conditions` and `conditions_complete`;
- `limitations` and `is_complete`;
- `authority`, `source`;
- `parser_notes`: the provision's parser warnings and review items.

**`is_complete` is false whenever `limitations` is non-empty.** Today that means every cell that has footnotes, because their text is not loaded (`conditions_text_not_loaded`). A check must not issue a bare Pass or Fail on an incomplete result. It either says what is missing, or treats the result as Could Not Evaluate. That policy belongs to phase 3.

Results are deep copies, so a caller can't alter the store through them.

## Resolver (format only; built later)

Project wording becomes table values through rules, never inside the store:

```json
{"id": "sprinkler.nfpa13d", "dimension": "sprinkler", "match": {"contains_any": ["NFPA 13D", "903.3.1.3"]},
 "maps_to": "S13D", "authority": "code_text",
 "cites": {"document": "IBC:2018:T504.3", "file": "code/table-504.3-notes.md", "lines": [15, 39]}}
```

- A rule without `cites` is refused.
- A rule citing anything other than `code_text` is reported as an interpretation, with its authority shown.

## Validation and provenance

`validate_store(store) -> list[str]` uses the standard library only. It checks:
- shape, types and enums;
- unique cell ids;
- that every index entry points at a cell carrying that key;
- that keys and ids are **re-derived** from each cell's dims and printed labels;
- that `value` agrees with `value_text`, `value_kind` and the table's `unit`, and is a finite, non-negative number;
- that table footnotes appear on every cell;
- that `conditions_loaded` agrees with condition texts;
- that every cell is `code_text` from an available document in the manifest;
- that no path is absolute and no filename contains `:`.

**Validation alone can't prove the store matches its sources.** A consistent edit, where a value and its printed text are both changed, passes it. `Store.load(path, manifest=...)` closes that gap: it rebuilds from the manifest and the source files and requires identical bytes. Checks should load the store that way.

## Deferred (recorded, not forgotten)

- ~~Footnote text~~: loaded in phase 2. `limitations` is now empty for 504.3 cells. A footnote pointing to an unavailable document is surfaced through `references` and handled by check policy, not as a store limitation.
- **A distinct status for "not loaded yet".** For now it is a code under `unavailable`.
- **Consistent `dims` types:** always lists.
- **Check-level policy** for incomplete results (phase 3).

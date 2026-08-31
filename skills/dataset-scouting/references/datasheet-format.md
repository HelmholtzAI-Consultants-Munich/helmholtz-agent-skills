# Datasheet format

Read this when creating, updating, checking, or building the datasheet. Candidate files are the sourced working record; `datasheet.xlsx` is the concise human review view.

## Layout and ownership

```text
datasheet/
├── criteria.md
├── datasheet.xlsx          generated; never hand-edit
└── candidates/
    └── <stable-id>.md
```

Use one file per candidate. Create it with:

```bash
python3 "$SKILL_DIR/scripts/datasheet.py" new datasheet/ <candidate-id>
```

The command supplies the supported headings and tables. Fill the scaffold; do not invent parallel fields or reorder its structure.

The agent owns findings, sources, gaps, and its recommendation. The user owns everything below `## Review`. Never edit, reformat, or move that block.

## Summary

Keep summary values comparable enough to scan in Excel. Put long reasoning in the relevant table, `Gaps`, or `Research notes`.

- `Download size`: total download volume of the acquisition set behind `Raw-data route`. Start with the total and its unit, then give the size basis or optional breakdown: `412 GB total compressed download [S2]`. If the listing exposes no usable byte sizes, write `unknown — <reason>`.
- `Metadata access` and `Raw-data access`: `direct`, `on request`, `off-repository`, `unavailable`, or `unknown`.
- `Metadata evidence` and `Raw-data evidence`: `claimed`, `route verified YYYY-MM-DD`, `contents inspected YYYY-MM-DD`, or `unknown`.
- `Tier`: relevance according to `criteria.md`; it is independent of the recommendation.
- `Recommendation`: `accept`, `reject`, or `unknown`, followed by the deciding reason.

Evidence levels are deliberately different:

- `claimed` means a record or document says a route or object exists.
- `route verified` means the exact route was opened and matched the candidate.
- `contents inspected` means a listing, manifest, export, or metadata object was examined closely enough to identify its contents.

Reachability is not content verification. A route may resolve while carrying only processed outputs.

## Checks

Record `pass`, `fail`, or `unknown`, a concise reason, and source IDs for each check.

1. `Metadata`: does relevant metadata exist, and can the user reach it? A pass needs a populated metadata route and evidence that the route was opened.
2. `Required fields`: are every must-have field present at the coverage threshold in `criteria.md`? A pass needs `contents inspected` metadata evidence and countable coverage.
3. `Raw data`: do the available files meet the user's definition of raw enough? A pass needs `contents inspected` raw-data evidence.

Do not recommend `accept` while any required check is `fail` or `unknown`. Access-restricted data is normally `unknown`, not `fail`: record the application route and contact.

## Fields

Use one row per field. This single table replaces separate present, absent, and observed lists.

| Column | Meaning |
|---|---|
| `Field` | Use the exact name from `criteria.md`; retain the source's name for additional observed fields. |
| `Priority` | `must-have`, `nice-to-have`, `observed`, or `ignore`. |
| `Status` | `present`, `absent`, or `not checked`. |
| `Coverage` | `n/N`, or `not determinable — <reason>`. |
| `Storage` | Where values live: structured field, record title, free text, supplement, code repository, data object, or another accurate source term. |
| `Level` | What entity the value describes: sample, participant, cell, study, or another accurate level. |
| `Sources` | Bracketed source IDs such as `[S2] [S4]`. |
| `Note` | Values observed, where absence was checked, contradictions, or other evidence needed to interpret the row. |

`present` requires storage and level. A field mentioned once at study level is not present per sample. Record source values when they establish usability, but do not normalize or map them into the user's target vocabulary.

Example:

```markdown
| sex | nice-to-have | present | 6/6 | supplement | participant | [S4] | values `F` and `M` |
```

## Technical details and research

The `Technical details` rows come from `criteria.md`. Record author-reported values, their sources, and the channels checked. If the authors never state a value, write `unknown` and name where you looked; do not infer a tool from file shapes without labelling the inference.

The `Research` table records which search-ladder channels were used and what each returned. Use the channel tokens defined by the search-channel guidance. An accepted or tier-1 candidate must address `publication` and `supplements`, including an explicit reason when either does not apply.

`Research notes` is optional narrative for material verification events or contradictions that do not fit cleanly in a row. It is not another copy of the tables.

## Sources

Use stable candidate-local IDs in append-only order: `S1`, `S2`, and so on. Never renumber an existing source.

Each source row records what was actually read, its resolvable URL or local path, and the retrieval date when applicable.

Every bracketed citation must resolve to a source row. Mark second-hand material as a claim. Cite the supplement, export, or file that carried the fact—not merely the publication or study it belongs to.

## Check and build

```bash
python3 "$SKILL_DIR/scripts/datasheet.py" check datasheet/
python3 "$SKILL_DIR/scripts/datasheet.py" build datasheet/
```

`check` enforces structure, controlled values, source integrity, evidence prerequisites, criteria coverage, acceptance rules, and Review preservation when a baseline is supplied. Research-quality judgement remains part of the verification pass; the script does not pretend to prove that a search was thorough.

`build` runs the same hard validation, creates `datasheet.xlsx`, reopens it, and verifies the review sheets and rows. It generates `Datasheet`, `Fields`, `Technical`, and `Totals`; rejected candidates remain visible. The workbook keeps concise decision values and declared criteria fields. Its `Download size` column shows only the total, while route cells contain every recorded URL separated by line breaks. Full evidence and additional observed fields remain in the candidate files.

`build` requires `openpyxl`. If it is unavailable in the skill runtime, report the dependency rather than installing packages globally.

To prove a re-run preserved human text:

```bash
python3 "$SKILL_DIR/scripts/datasheet.py" check datasheet/ --review-baseline <baseline-datasheet>/
```

---
name: dataset-scouting
description: use this whenever the user is examining public data, asking whether a study's metadata or raw data is actually usable, looking for exact raw-data download links, extracting the preprocessing or technical details a paper reports, building or updating a candidate list / shortlist / inclusion table, deciding which accessions are worth the download
---

# Dataset Scouting

Help the user curate and decide which public datasets they can actually use. Detailed scouting produces a **datasheet** — an Excel workbook plus its Markdown working files, one sourced entry per candidate, available and missing data or metadata, actionable download routes, selected technical details, and a recommendation with its reason. A **candidate** is one dataset the user might acquire (typically, a dataset coming from the same study sharing metadata schema, preprocessing pipeline, technology, etc.).

**The human decides.** You screen, propose and record. Accepting, rejecting, prioritising and emailing authors are the user's calls, and their words in the datasheet are theirs to edit, never yours. Acquiring, loading, harmonizing or mapping a dataset is not this skill. 

## Workflow

Copy this checklist and track progress.

```
Dataset scouting:
- [ ] Step 1: Quick check to understand the domain and potential criteria
- [ ] Step 2: Settle criteria together with the user
- [ ] Step 3: Collect
- [ ] Step 4: Preliminary results presentation and additional alignment
- [ ] Step 5: Double-check pass
- [ ] Step 6: Hand over
```

**Step 1: Quick check to understand the domain and potential criteria**

Reconnaissance, not screening. Do not write candidate files yet.

Look at a handful of real records so the criteria interview is about this domain, not a generic one. Note what one study / paper / accession actually looks like, which metadata fields deposits carry, where raw files live and in what form, what authors report as methods, and what access restrictions show up.

If they already have a list, skim several that span the obvious variety. If they only have a topic, do a short search — repository terms, reviews and benchmarks, datasets cited by papers already doing this work — and look at a few hits. If they already have a datasheet, skim it the same way.

Then, list what you can actually reach this session: connectors, databases, and MCP servers (list them, don't guess), browser or fetch, web search, repository APIs from code, article full text, sub-agents, the user's local files. If a channel you need is missing — blocked domain, no credential, unreachable API — say so and ask, rather than silently dropping to a weaker source.

**Step 2: Settle criteria together with the user**

Agree on scope and depth before collecting. Recommend a focused set of candidates and the fields needed for the user's decision; agree its size rather than imposing a fixed cap. If the user chooses a broad sweep, return a compact, cited discovery table in their requested format: candidate, relevance, tissue/cells, assay, source/access lead, and next check. Do not populate the detailed datasheet with unresearched fields. Move to detailed scouting only for the selected candidates.

For detailed scouting, write a concise `criteria.md` containing the candidate unit, checks, selected fields and thresholds, technical details, tiers, scope, shared terminology, and open questions. Explain that this file controls what you search for and how you judge candidates. Link it and summarize the proposed decisions in the conversation before asking for confirmation. Distinguish agreed decisions from proposals; writing the file is not confirmation. Reuse decisions already confirmed by the user.

Here are typical topics requiring alignment, but use your best judgment based on the responses: which fields are must-have and at what coverage, what "raw enough" means, what counts as reachable metadata, how they want `on request` rows triaged, which author-reported technical details they need, and how tiers are defined.

It's important that the interview questions are understandable to the user, load-bearing, and have best potential pre-defined options (suggestions) based on your research. Use plain words for plain things: "no download link found", not "acquisition route unresolvable at this time". Agree report terminology using real source labels, then use it throughout the report while retaining original terms and meaningful qualifiers in the evidence. This harmonizes report wording, not the underlying datasets.

**Step 3: Collect**

For detailed scouting, research each selected candidate until its identity, sample count, total download size, agreed fields, and recommendation are supported by authoritative evidence or an explicit searched gap. Resolve download targets and record their source and retrieval method. For viable/tier 1 candidates, pursue unresolved decision-critical fields through the applicable channels. Keep discovery/search logs outside `candidates/`; they are not datasets.

Adaptive: if the criteria don't fit what you are seeing, pause and ask. Don't finish the pool against a rule you no longer believe.

**Step 4: Preliminary results presentation and additional alignment with the user**

Very briefly present what you found: totals, surprises, high-relevance gaps, rows that need a decision, criteria that cracked. Do another round of interviews to align if criteria still hold, if something needs loosening/hardening, if priorities changed based on findings. Refine the criteria if they change their mind.

**Step 5: Double-check pass**
Independently verify candidate identity, evidence level, download targets and methods, agreed terminology, and the claims that determine each recommendation. For accepted, unknown, and Tier-1 candidates, also check unresolved must-have fields in plausible skipped sources. Dispatch verification sub-agents when you have them. For a broad sweep, verify the discovery claims without expanding into a detailed audit. The checks and workbook build below apply to detailed scouting.

If `scripts/` is not on disk, write it with `host.skills.read("dataset-scouting", path)`: `scripts/datasheet.py`, `scripts/datasheet_lib/__init__.py`, `scripts/datasheet_lib/markdown.py`, `scripts/datasheet_lib/model.py`, `scripts/datasheet_lib/validate.py`, `scripts/datasheet_lib/workbook.py`. Then:

```bash
python3 scripts/datasheet.py check datasheet/
```

**Step 6: Hand over**
For detailed scouting, generate and verify the output Excel file:
```bash
python3 scripts/datasheet.py build datasheet/
```

`datasheet.xlsx` must be a concise, readable review document covering the candidates, declared fields, criteria satisfaction, access routes, and proposed recommendations. Full evidence stays in the candidate Markdown files.

### References
Read with `host.skills.read("dataset-scouting", "<path>")`.
- Read `references/interview-guidelines.md` — step 2 and 4: question examples, tone, points users get wrong on a first pass.
- Read `references/search-channels.md` — step 1 and 3: which channels to use, in which order, when to stop, how to record the search.
- Read `references/search-guidelines.md` — steps 1, 3 and 5: fetch boundary, three checks, claim rules.
- Read `references/source-verifier.md` — step 5: verification guidance and a prompt for a checker sub-agent.
- Read `references/datasheet-format.md` — steps 3–6: candidate record semantics, hard checks, sources, Review ownership, and workbook build.

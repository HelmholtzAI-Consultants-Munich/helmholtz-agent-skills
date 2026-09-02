# Search channels

Work the ladder. Record each rung and its outcome in the candidate's `Research` table, so the next run starts where this one stopped and a gap names a real search.

## Inventory first
Before the first candidate, find out what you can actually reach in this session rather than assuming. Sessions differ enormously: one has a browser tool and three connected databases, the next has web search only.

Check for connected connectors and MCP servers (list them, don't guess), a browser or fetch tool, web search, repository APIs reachable from code, article full-text retrieval, sub-agents for parallel work, and the user's own local files. When you later record a gap, the channels you name should be ones that exist.

If a channel you need is unavailable, whether a blocked domain, a missing credential or an unreachable API, say so and ask for it rather than silently degrading to a weaker source. "I could not reach the repository API; may I have network access to it?" is a solvable problem. A gap entry hiding a permission error is not.

## The channel ladder

Roughly cheapest and most authoritative first. Skip rungs that cannot apply; don't skip a plausible rung because the answer seems unlikely or the last search was inconvenient. Use the rung tokens below in the `Research` table.

**1. `record` — the primary record.** The repository page *and* the API or structured export for the accession. Read all of it: per-sample records, structured attribute fields, record titles, the study-level summary and description text, file lists and sizes, processing fields, submitter contacts, related-record links, dates and status.

Read both representations. A structured export exposes fields the page collapses, and the page carries fields the export omits, grouping relations especially. Concluding "no parent record" from an API payload that never carries relations is a wrong answer that looks like a finding.

**2. `related-records` — related records.** Grouped series and their members, sibling accessions from the same submission, superseded and re-released versions, cross-links into other repositories. Structure is where candidates get confused with each other, and where a file you were told doesn't exist often turns out to live.

**3. `publication` — the publication.** Always read. Full text, URL, and specifically the **data-availability statement**, the **methods**, and the **supplementary index**. The data-availability statement is the highest-yield paragraph in the whole workflow. Methods is the only place author-reported technical details actually exist — inferring a tool from which files were deposited is not the same finding and must not be written as one.

If the full text is paywalled, say so and try the preprint, the PMC copy, the author's institutional repository, and the user's own access before recording it as unreachable.

**4. `supplements` — supplements.** Every one, not the first. Sample tables live in the fourth spreadsheet as often as the first, and they are frequently unlabelled. Supplementary tables and data-availability statements are ordinary screening sources and can be fetched directly. If a supplement cannot be opened, record that you tried and why it failed — that is a real finding about the candidate.

**5. `literature-search` — literature and citation search.** For a candidate with no obvious paper: search the accession itself, the exact submission title, the submitter's other work, distinctive phrases from the summary, and papers citing the dataset. A dataset released before its paper acquires one later, and a citing paper often describes the deposit better than the deposit does.

**6. `off-repository` — off-repository locations.** Code repositories, lab and institutional pages, project sites, consortium portals, data-hosting services. Metadata living in a code repository rather than the deposit is common enough to check by default, not as a last resort — search the repository host for the accession string.

**7. `web` — general web search.** Contacts, licences, consortium membership, retraction or withdrawal notices, and anything the structured sources don't carry.

**8. `user` — ask the user.** A legitimate channel, and better than a false unknown: they may have the paper, know the authors, or have institutional access you don't. It is last because their attention is the resource this skill protects, so batch these into one clearly-scoped question rather than interrupting per candidate. "Three candidates need full text I can't reach — can you drop the PDFs somewhere, or should I record them as unknown?"

Where sub-agents are available, run independent candidates in parallel; the ladder is per candidate and the rungs don't interact across candidates. Give each agent the candidate's identifiers, the user's fields of interest, the field contract and the fetch boundary, and ask back for sourced findings only.

## Chasing specific things

**An exact raw-data route.** Prefer the repository's own file-level listing or API over any link in the paper: paper links rot, repository routes usually don't. Where the route is an archive, the listing of what's inside is often available without downloading it. Watch for a working link at the wrong granularity: a processed atlas download is not a raw-data route, and recording it as one is worse than recording nothing. Check the directory as well as the manifest; large objects sitting beside a bundle frequently appear in neither the manifest nor the summary.

**A route to the metadata itself.** The repository's machine-readable export for the accession, the supplementary file's own URL or DOI, the file in the code repository. The record's landing page is where you found the metadata, not a route to it, and a route that was never recorded cannot be link-checked. Where metadata is only obtainable by application, record the application route.

**Whether a field is present.** Check the structured attribute fields, the record titles themselves, the study-level summary and description text, every supplement, and the paper's tables. Titles matter: stage, timepoint and group labels get encoded there and appear nowhere else. Record what level the value resolves to — a variable stated once in a study-level description is present in the deposit and absent per sample, and those are different answers. If the field could only be inside the data object, that is a permission question for the user, not a search.

**Author-reported technical details.** Methods and supplementary methods first, then the repository's processing fields, then the code repository, where pipeline configs and READMEs often carry versions the paper omits. Then the protocol registry if one is linked. If the authors never state it, say so; `unknown — tried: Methods, Supplementary Methods, code repository` is honest and actionable.

**Licence, ownership and access terms.** Repository record first, then the **journal article's own licence**, then the repository's general data-use policy, then the consortium or funder page. Checking only the repository record produces `unknown` almost every time by construction, which is a property of where you looked rather than a fact about the dataset.

**Owner contacts.** The corresponding author in the paper, the submitter on the record, the consortium contact page. Record a name and an address. "The contact is on the record" is not a contact, and it makes the sheet's own "worth an email" recommendation impossible to act on.

**A missing publication.** Search the accession string, the exact submission title, the submitter's other work, and citing literature before concluding none exists. If the search genuinely comes up empty, write `none found` with the queries you ran, and produce no citation. The plausible-looking paper by the same group on a similar topic is exactly the fabrication that destroys the datasheet's credibility.

## When to stop

Choose channels according to the unresolved claim. Don't give up too early if another accessible source could materially change a check, tier, or next action.

## Recording the search example

```markdown
| record | rendered page and API read; all 12 sample records inspected | [S1] [S2] |
| related-records | parent read; no other members | [S1] |
| publication | full text and data-availability statement read | [S3] |
| supplements | 4 of 4 opened; S2 carries the clinical table | [S4] |
| off-repository | no code repository found for the accession |  |
```

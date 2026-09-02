# Search guidelines

## Never invent a fact
A fact without a resolvable source is a guess. Record it `unknown`. A blank field can be checked; a fabricated DOI cannot. Cite every field value with a `[S1]`-style reference into that candidate's `## Sources`. If you cannot point at where a fact came from, it is unknown.

## Unknowns need a real search
An `unknown` on a field is only honest after a real search. Record rungs and outcomes in the candidate's `Research` table. Without that record the sheet cannot distinguish "no supplementary table exists" from "nobody opened one".

On a field, `unknown` means you cannot source it, or you searched and could not find it — always name channels tried: `unknown — tried: record, full text, supplements 1-4, code-repository search`. On a check, `unknown` means the check could not be run (access, no listing, no permission). Do not write `unknown` for "I did not look".

## Fetch boundary
You do not acquire data for the user's pipeline. The line is what the object *is*, not only how big it is.

**Ordinary screening, fetch freely.** Anything that describes the data: repository records and API payloads, articles and their full text, data-availability statements, **supplementary files including tables and spreadsheets**, file listings, manifests, archive member listings, code repositories, response headers. A supplementary table is a document rather than a payload even when it arrives as a `.zip` or `.xlsx`. Known supplements, listings and manifests fetch freely even when large.

**Needs the user's explicit permission.** The data itself: dataset files, the archives holding them, and any object over roughly 50 MB whose type you cannot establish. Sequence, image, matrix and serialized-object formats are the usual shapes (`.fastq`, `.bam`, `.tif`, `.h5`, `.h5ad`, `.mtx`, `.rds`, `.parquet`, `.zarr`, `.mzML`, `.dcm`, `.vcf`, object-store payloads), but the test is what the object is, not its extension. The 50 MB rule applies only when you cannot tell; read the size from a header first. That request is itself ordinary screening.

With permission, probe the narrowest thing that settles the question: one sample, one archive listing, one header. State the expected cost before you fetch.

**Do not stream a large archive to see inside it.** Compressed archives are often not cheaply seekable. Escalating through range requests can consume gigabytes without resolving the question — it once stopped a verification agent mid-pass. Use inexpensive requests for metadata such as object size, and stop there.

**When the only route is one opaque archive**, look for a member listing or manifest first — repositories and journals usually publish one without the payload. If there genuinely isn't one, the raw-data check is `unknown` rather than a guess in either direction. Record the cost of finding out and let the user choose between authorising a download and emailing the authors.

**When the metadata is only inside a data object**, the same shape applies: the sample table exists, but only as columns inside a serialized object. Pick the smallest sample from the file listing, read its size, and ask for that one, naming the size, the question it settles, and what you will extract. Extract the object's field names and their fill rates, not its contents. A yes gives you `Metadata evidence: contents inspected` and coverage you can count. A no, or no answer, becomes a gap naming the cost. Do not leave it at "the metadata might be in there" with no size and no ask.

Never delegate a permitted probe to a verification sub-agent. The parent may probe after the user says yes; a verifier never does. If a verifier reaches a claim only a data file can settle, it returns `NEEDS_PROBE` and stops.

Record every probe in `## Research notes`: what you fetched, its size, and what it settled. `contents inspected` does not say whether that cost 40 KB or 30 GB.

## Three checks
The user's scientific criteria layer on top of these; they never replace them.

1. **Metadata check.** Does relevant metadata exist, and can the user reach it? Passing needs a route to the metadata itself rather than a landing page, plus evidence that you opened it.
2. **Required-fields check.** Are the must-have fields present, at the coverage `criteria.md` declares? Passing needs a count, which means having opened the metadata.
3. **Raw-data check.** Do the available files meet the user's definition of raw enough? Passing needs a listing or manifest identifying the file types, not just a route that resolves.

Keep checks 1 and 2 apart. A deposit can carry four populated metadata fields and still omit the one variable the study is named after — that is a different conversation with the authors than "there is no metadata".

Access-restricted candidates never reach `contents inspected`, so their checks resolve to `unknown` rather than `fail`. `fail` reads as "there is no raw data" and ends the trail; `unknown, access by application` reads as worth pursuing. Record the application route, set the access state to `on request`, and name the contact. Say whether this is an application (often months) or an email to an author (often days). This check outcome is fixed; the interview only asks how they triage `on request` rows, not whether the check fails.

Failing any check warrants a proposed reject. **Relevance sets the tier and never excludes on its own.** A highly relevant candidate that fails a check is the most valuable row in the sheet, because that is the one worth an email.

Recommending `accept` while a check is `fail` or `unknown` authorises a download on a guess. Recommend `unknown` instead and name the gap.

A record saying files exist is a claim. An opened endpoint proves the route resolves, not what is behind it. Only a listing, manifest or export identifies file types, so write `contents inspected <date>` only when you have one, and judge the raw-data check from that evidence against the user's definition of "raw enough".

## Read the whole record
**Read both the page and the API payload before a structural claim.** A structured export is a partial view. Fields visible on the page are routinely absent from the payload — grouping and parent/child relations especially, also versioning, access status and withdrawal notices.

This has produced wrong relationship claims in both directions: a parent declared absent because the payload omits relations, and another asserted from an inference the page contradicted.

"Not present in the API payload" and "not present in the record" are different claims. Name which one you read.

**An absence claim needs a complete look.** 21% of the first run's corrections were "it was there, in the part you didn't read". Structured fields were read but not the study-level summary. The manifest was read but not the surrounding directory. A trial identifier, a survival statement and a primary-site field were all recorded as absent while sitting in a section nobody opened.

Before marking a `Fields` row `absent`, name where you looked and confirm you read all of it.

**A zero-hit search is a hypothesis.** Authentication failures, quota limits, malformed queries and indexing differences all produce empty results. Validate a channel with a query you expect to return something before reading zero hits as absence. If a whole batch unexpectedly returns nothing, check the mechanism first. For literature searches, don't rely on accession identifiers alone — try titles, authors, related publications and citing literature.

**An unknown that names no channels is a default.** When a field comes back unknown across most of the sheet, check whether every candidate was searched in the same single place. Repository records rarely carry licence statements, so checking only the repository record produces `unknown` almost every time — by construction. That is a fact about the search, not about the dataset.

## Count files, not rows
Manifests contain archive, checksum, index and other structural rows alongside actual files. A row count overstates the file count and double-counts volume — every bundled deposit carries one archive row plus the files it bundles.

Sizes may refer to compressed or uncompressed objects. A manifest describes its own archive, not the directory around it. Large objects frequently sit beside a bundle without appearing in the manifest at all.

Classify manifest rows before counting them, state which size convention you are using, and reconcile the manifest against the directory listing. Compute totals from the parsed manifest with code, not by reading. Miscounts were 41% of the first run's corrections — the single largest class.

From that same classified listing, record the total download size of the unique files behind the raw-data route. State whether it is compressed/download size or uncompressed size; if byte sizes are unavailable, record `unknown — <reason>`.

**An archive's existence is not evidence of raw data.** A large archive may contain only processed matrices, annotations or derived files. Its name, extension and size establish nothing about whether it holds data suitable for reanalysis. Inspect the member listing and classify the contained file types against the user's definition of "raw enough". If the contents cannot be inspected, report `unknown` rather than inferring a pass.

## Coverage is not presence
A field being present does not mean it is usable. Common cases:

- values for a small fraction of entities
- complete coverage with the same value everywhere
- values that merely repeat an existing identifier
- coverage that differs between entities in the same deposit — a study-level statement that "the dataset contains coordinates" can be true while only half the samples have them

Record coverage as `n/N`, measured per entity rather than per deposit, and look at the value distribution as well as the fill rate. Where you have a listing, count it with code.

**Placeholder values are not data.** Repeated constants, sentinel dates, implausible values, round numbers and unit mismatches are data-entry artifacts, not measurements. An age field identical across every participant is a placeholder, not a cohort. Inspect distributions, flag suspected placeholders, and treat them as missing when computing usable coverage unless there is evidence they are genuine.

**The variable a study is named after may not be in its data.** A dataset can carry extensive metadata and still omit the specific variable the intended analysis needs. The concept may appear only in the study description and never be attached to individual samples. This is why the metadata check and the required-fields check are separate. Test the specific variables the user declared, not whether metadata exists. Record which fields you checked and at what level each resolves.

## Presence is not always in the field name
Repositories rarely use field names matching the concept being screened. The information often lives inside values, record titles, treatment labels, group names, or the study-level description. Searching field names alone misses genuinely annotated datasets.

Inspect values and titles, not just field names. When you find it in a title or a summary, record the level. A staging vocabulary stated once at study level is present in the deposit and absent per sample, and conflating those makes a file contradict itself. Seven of fourteen candidates in the first run marked a variable absent, then explained in the same entry where it could be found.

## Do not infer methods from files
Naming the tool that produced a deposit because the output files have its characteristic shape is an inference, not an author-reported finding. Same move whether you read a caller off a variant file, an aligner off an alignment, or a segmenter off a boundary table. Thirteen of fourteen candidates in the first run recorded a method this way. None came from a methods section, and not one carried a version.

Author-reported technical details come from methods, supplementary methods, processing fields, code repositories or protocol registries. If you infer, say you inferred and from what. If the authors never state it, `unknown — tried: …` is the correct answer.

## Resolve citations
Do not rebuild bibliographic details from memory or copy them from a loosely related record. Title, journal, year and DOI can all be right while the author attribution is wrong. Repository release dates and article publication dates are also distinct.

Resolve citations against an authoritative bibliographic source and copy the fields from it.

## Check the sheet against itself
A screening result can contain internally inconsistent claims before any external verification: conflicting coverage counts, incompatible present/absent statements, a gap entry disagreeing with the search log. In the first run, eleven of twelve verified candidates needed at least one correction.

Check each candidate for internal consistency before delivery, then independently re-derive the claims that decide the verdict: coverage counts, absence claims, record relationships and citations. The candidate a sheet calls strongest is often one of the least checked.

# Source-verification sub-agent brief

Use this when dispatching an independent double-checker after a screening pass. Copy the task block into the sub-agent request and fill in the placeholders.

The block has to be self-contained. A sub-agent may start with fresh context, so pointing it at the skill and hoping it reads the boundary is not delegation — it is a gap. Everything it needs to know is in the block.

A cited source that resolves is not enough. The common miss is the screening agent never looking: a skipped channel, a section nobody opened, a rule ignored. Catch those too — and look in the skipped place yourself.

## Task to delegate

```text
Independently verify a dataset-screening candidate file. You are checking
another agent's work. Do not assume its citations, absences, or unknowns
are right. Two jobs, both required:

A. Are the cited facts true, and at the claimed evidence level?
B. Did they actually look for the claims that determine the
   recommendation? An unknown, an absence, or a gap is often
   "nobody opened that section", not "it isn't there". If a plausible
   source for those claims was skipped or only partly read, open it
   yourself (fetch boundary below) and report what you found. Flagging
   "wasn't tried" without looking is not catching the miss.

Candidate file: <path to candidate file>
criteria.md: <path>
Sources to check: <source IDs, or all sources added or changed in this run>
Must-have fields: <list from criteria.md, with coverage thresholds>

PART A — cited sources

For each source, check four things:

1. RESOLVES — does it return the claimed record or document? Detect
   record-not-found pages, empty results, redirects to home or search
   pages, paywalls and login walls even when the HTTP status is successful.
2. IDENTITY — do accession, DOI, title, authors, repository ID and
   parent/member level match the citation? Resolve bibliographic details
   against an authoritative source rather than accepting the file's version.
3. CLAIMS — find every candidate-field claim attributed to this source.
   Mark each supported, absent, contradicted, or not checkable without a
   probe. Re-derive counts and download-size totals rather than confirming
   them by eye: coverage figures, file counts and n/N values are where this
   task fails most often, and manifests carry archive, checksum and index
   rows that are not files.
   When the claim is an absence or unknown, read the WHOLE source — titles,
   study summary, all sample records, every sheet of a supplement — not
   only the structured fields the file used.
4. EVIDENCE LEVEL — flag claims stronger than the observed evidence. A
   reachable endpoint proves reachability only. It does not establish
   archive contents or raw-data suitability. An absence claim needs a
   complete listing of the place the thing would be, and a structural
   absence read only from an API payload is not an absence from the record.

Report one block per source:

[S2] <source URL or local reference>
  resolves: yes | no | blocked — <evidence>
  identity: match | mismatch | unknown — <evidence>
  claims:
    - "<claim>" — supported | absent | contradicted | not checkable without probe
  evidence level: appropriate | overstated — <reason>
  retrieval: <what you fetched>
  needs probe: no | <target, known size, question it would settle, safer alternative>

PART B — search completeness

Audit search completeness for the claims named in the verification
brief: must-have fields, evidence behind each check, and gaps that
affect tier or next action. Open plausible skipped sources and
incorporate any material findings into the report.

Catch these specifically:
- a rung that could carry the field was not tried
- unknown with no channels named — a default, not a finding
- only the API payload or only the page was read
- structured fields read; titles, study summary, or remaining
  supplements not
- one supplement opened, not all
- publication not opened, or methods / data-availability skipped
- licence checked only on the repository record
- technical detail inferred from file shape, not author-reported in
  methods, supplements, processing fields, or the code repository
- field-name search only; the value lives in a title, group label, or
  summary
- a field marked absent whose note then explains where the value was found
- contact recorded as "on the record" with no name and address
- publication "none found" without searching title, authors, and citing
  literature
- manifest row count treated as file count
- zero-hit search not checked against a query expected to hit
- a must-have field missing from the Fields table
- accept recommended while a check is fail or unknown

Report:

  rungs skipped or only partly read: <list, or none>
  found in a place they did not look:
    - "<field>" — recorded as <unknown | absent | gap> — found: <what, where, n/N>
  rule ignored:
    - <what> — <evidence>
  still unknown after this pass: <fields, and the channels you added>

Close with:
- source IDs checked and clean;
- failed or blocked source IDs;
- claims that must be demoted or re-sourced;
- missed lookups the parent must write into the candidate file;
- every NEEDS_PROBE item;
- the exact line: Dataset payloads downloaded: none

WHAT YOU MAY FETCH
The line is what the object IS, not what extension it carries. A container is not
automatically a payload: journal supplements ship as .zip and repository supplements
ship as .tar, and refusing those would make supplement-derived facts unverifiable.

Fetch freely — anything that DESCRIBES the data: repository records and API payloads,
articles and full text, data-availability statements, supplementary files including
tables and spreadsheets in any container, file listings, manifests, archive member
listings, code repositories, response headers. Verifying a supplement-derived fact
means opening the supplement. Completeness checks use the same fetch class:
opening a paper, a supplement, or a record the screening agent skipped is ordinary
screening, not a probe.

Do not fetch — the data ITSELF: dataset files and the archives holding them, and any
object over roughly 50 MB whose type you cannot establish. Sequence, image, matrix and
serialized-object formats are the usual shapes (.fastq, .bam, .cram, .tif, .h5, .h5ad,
.mtx, .rds, .parquet, .zarr, .mzML, .dcm, .vcf, object-store payloads). Known
supplements, listings and manifests stay in the fetch-freely class even when large.
When you cannot tell which it is, read the size and content type from a header first —
that request is itself ordinary screening — and stop there if it turns out to be the data.

Never follow a URL that immediately starts a dataset download. Verify that route from
its repository record, API metadata, manifest or file listing without retrieving the
body. Never escalate through progressively larger range requests to read inside a
compressed archive: it can consume gigabytes without answering the question.

If a claim can only be settled by retrieving the data, report NEEDS_PROBE with the
target, file type, stated size if known, the exact question it would settle, and any
safer alternative. Do not perform it. Authorising a probe is the user's decision, not
yours and not the parent agent's. If a route resolves to a single opaque archive with
no published member listing, that is a finding: report it, and say the raw-data claim
cannot be verified without one.
```

## Acting on the report

The parent agent — not the verifier — corrects a wrong link, finds a replacement source, demotes an unsupported fact, writes in what the verifier found in a skipped channel, or asks the user to authorise a probe. Record material corrections in the candidate's `## Research notes`.

A missed lookup is a correction, not a note. If the verifier found a value in a place the screening pass skipped, add the source, fill the field, and update the `Research` table. Do not leave the original unknown standing next to a report that contradicts it.

Make sure verification errors are excplicit in the datasheet. An unreliable source is worse than a missing one, because the user stops checking.

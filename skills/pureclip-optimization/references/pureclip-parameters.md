# PureCLIP parameters — what they do to the model

PureCLIP fits a hidden Markov model to genome-wide read-start counts and fragment coverage (Krakau, Richard & Marsico 2017, *Genome Biology* 18:240, doi:10.1186/s13059-017-1364-2; docs at https://pureclip.readthedocs.io, source at https://github.com/skrakau/PureCLIP). Read starts mark reverse-transcriptase truncation at UV crosslink sites. Most of these settings are not thresholds on the output; they are inputs to a fit, and they change what the model treats as background.

Flags, defaults and ranges below are from PureCLIP 1.3.1. Verify them against the version you run, and record that version in the report. Statements marked *in prior runs* come from the cohort in `prior-runs.md` and are observations about one objective on one set of datasets, not properties of the tool. How to design and run the search is in `optimization.md`.

## Contents

- The model and the score
- Fixed by the protocol
- Scope: learning versus calling
- The search axes
- Defaults that quietly gate the fit
- Free diagnostics
- Levers of last resort
- Post-processing, outside PureCLIP
- Failure signatures
- Version and installation

## The model and the score

**Four states.** The HMM crosses two binary dimensions: enriched versus non-enriched (gamma emissions on KDE-smoothed coverage, capturing transcript abundance) and crosslinked versus non-crosslinked (binomial emissions on read-start counts at a position, capturing truncation). State 0 is neither, 1 is crosslinked only, 2 is enriched only, and 3 is both. Only state 3 is written out, as state 3 in the BED, which is state 4 in the publication. An input control adds a CLIP-to-input enrichment covariate, which acts on the enrichment dimension rather than the truncation one, which is why it removes abundance-driven false positives that bandwidth and filtering cannot.

A low score does not mean "not a crosslink": the model could not separate state 3 from its nearest rival, which is often state 2, enriched but not crosslinked.

**Site score (`-st`, range 0–3, default 0).** The score column is a log posterior probability ratio, and `-st` selects which ratio:

- `0` log P(3) / max(P(0), P(1), P(2)) — most likely versus second most likely state. Default.
- `1` log P(3) / P(2) — crosslink-focused: given enrichment, is this position the crosslink?
- `2` log P(3) / P(1) — enrichment-focused: given a truncation, is this region enriched?
- `3` log((P2+P3)/(P0+P1)) + log((P1+P3)/(P0+P2)) — balanced; the two dimensions added.

`-st` changes the score column, and therefore every downstream score threshold and the shape of the score distribution you inspect as a diagnostic. If you vary it, it is a search axis and belongs in the report.

The HMM already acts as a filter, so post-hoc score thresholding is optional. If you do threshold, set the cut from the shape of the score distribution, at an inflection between the bulk and a high-scoring shoulder, rather than at a round number. Treat the threshold as a parameter: it belongs in the search space and the report, not applied silently afterwards.

**Region score is a sum.** With `-or`, sites within `-dm` are merged into one BED6 record: column 4 holds the individual site scores separated by semicolons, and column 5 holds their **sum**. A sum grows with the number of sites merged, so region score is confounded with region width and site density. Never rank or threshold binding regions on it without normalizing by site count, and expect anything that widens regions to raise it mechanically.

**Reported coordinates sit one nucleotide upstream of the read start by default.** `-ctr` moves them onto the truncation site instead. The default exists because the crosslinked nucleotide is upstream of where reverse transcription stops, but which convention is right depends on the RT enzyme, buffer and protein. Plus and minus strands are computed by separate code paths, so confirm the convention before computing any overlap, motif window or reference intersection: a systematic 1-nt shift degrades the single-nucleotide resolution PureCLIP exists to provide, and a strand-handling error shows up as motif enrichment collapsing toward 1. Scoring a strand-flipped copy of the call set is a cheap control for both.

## Fixed by the protocol

These have correct answers, not ranges. Getting one wrong produces symptoms that look like tuning problems. Settle them before any search rather than letting a sampler spend evaluations on them.

**Which mate carries the cDNA end (`-ur 1` or `-ur 2`; default: all reads).** The crosslink position is inferred from read starts, so selecting the wrong mate destroys the signal, typically as near-zero sites regardless of everything else. iCLIP single-end needs no selection; iCLIP paired-end uses read 1; eCLIP paired-end uses read 2. Applied to the input BAM as well, if one is given.

**Input control (`-ibam` plus `-ibai`).** Supply it when it exists. Alternatively `-is` takes a file of precomputed position-wise covariates, such as KDE-smoothed input read starts. The parser rejects `-ibam` without `-ibai` and rejects `-is` together with `-ibam`, so pick one route. *In prior runs*, using the control co-occurred with the higher-confidence, lower-yield regime, consistent with it removing abundance-driven calls.

**Replicates: repeat `-i` and `-bai`, maximum two.** PureCLIP learns emission parameters per replicate and combines them in a joint HMM, calling sites supported across replicates. You pass `-i rep1.bam -bai rep1.bai -i rep2.bam -bai rep2.bai`, and more than two is a hard error. With three or more IP replicates you must pool or choose a pair, which is a decision to state in the report.

This interacts with the objective: if you use the joint replicate mode *and* score replicate reproducibility, you are partly scoring what the caller already enforced. Pooling replicates for calling and measuring reproducibility from separate per-replicate runs keeps the metric independent of the caller. The upstream docs pool with `samtools merge`. Decide deliberately and report which you did.

**Preprocessing, upstream of PureCLIP entirely.** Adapter trimming, twice for eCLIP to catch double ligation; UMI deduplication if the library carries UMIs; unique mapping only (`--outFilterMultimapNmax 1`); end-to-end alignment rather than soft-clipped (`--alignEndsType EndToEnd`), because soft clipping shifts apparent read starts away from the true crosslink position and silently degrades resolution; then filter to the informative mate (`samtools view -f 130` for R2, `-f 66` for R1); coordinate-sorted and indexed. PureCLIP cannot distinguish PCR duplicates from real read-start enrichment, so skipped deduplication inflates scores at artefact positions and no parameter setting recovers from it. If you inherit BAMs, confirm this happened rather than assuming.

## Scope: learning versus calling

Two separate flags, easily conflated.

- **`-iv`** selects the contigs used to *learn* HMM parameters, for example `'chr1;chr2;chr3;'`. Learned parameters then apply wherever the model is run, so restricting learning to a few large chromosomes cuts memory substantially with little effect on parameter quality, while including unassembled scaffolds multiplies cost for nothing. This is the dominant memory and runtime lever.
- **`-chr`** selects the contigs the HMM is *applied* to. This is the genomic scope you call and score on, a choice driven by the objective's resolution rather than by cost. See `optimization.md`.

In both, contig names must appear in the same order as in the BAM file.

Threads: `-nt` for learning, `-nta` for applying. `-nta` above the number of learning contigs raises memory, because HMMs for several contigs are then built in parallel; it defaults to `min(nt, number of learning contigs)`.

Rough scale: a few chromosomes fits in roughly 8–16 GB and tens of minutes on several threads; all human chromosomes runs 32–64 GB and hours; adding a control BAM increases both. Expect a genome-wide run to take most of a day.

## The search axes

**Bandwidth (`-bdw`, range 1–500, default 50; `-bdwn` for the binomial *n* estimate, range 1–500, default: same as `-bdw`).** `-bdw` controls KDE smoothing of the coverage landscape the gamma emissions are fitted to. Too small fragments a coherent signal into noise; too large smears distinct crosslink events into broad regions and gives up single-nucleotide resolution. `-bdwn` smooths the estimate of *n*, the local coverage a read-start count is binomial against; the help recommends raising it, for example to 100, for proteins that slide along the RNA or produce long crosslink clusters, and keeping it at or below `4 × bdw`. Bandwidth is the parameter most directly tied to the physics of the assay, and *in prior runs* the one the composite objective was nearly blind to: median ρ ≈ −0.01 with score, ρ ≈ −0.33 with site count, so more smoothing gave fewer sites. Judge it on the call set, its width distribution and positional precision, not only on the score.

**Merge distance (`-dm`, default 8).** How close two crosslink sites must be to merge into one binding region. Affects only the `-or` output and the region score, not the HMM fit, so a post-processing sweep over `-dm` can reuse cached site calls. It interacts directly with any downstream clustering or width standardization: if both are free, the sampler can trade one against the other, so consider fixing one.

**Binding context (`-bc`, range 0–1, default 0), a macro over five other flags.** It expands to:

- `-bc 0` ≡ `-bdwn 50 -ntp 10 -ntp2 0 -b1p 0.01 -b2p 0.15`. Suits short, well-defined footprints, for example proteins with a short specific motif such as PUM2 or RBFOX2.
- `-bc 1` ≡ `-bdwn 100 -antp -b1p 0.01 -b2p 0.1`. Suits proteins producing larger crosslink clusters with lower read-start counts, for example binders of low-complexity motifs.

The source applies `-bc` first and reads the individual flags afterwards, so an explicit `-bdwn`, `-ntp`, `-ntp2`, `-b1p` or `-b2p` overrides it. **The exception is `-antp`: `-bc 1` switches it on and nothing switches it off.** So `-bc` and `-antp` are not independent, and searching both wastes half the grid. Which `-bc` fits is a question about the protein, so let what is known about it inform the prior rather than leaving it to search.

**Initial binomial probabilities (`-b1p`, default 0.01; `-b2p`, default 0.15).** Starting values for the truncation probability in the non-crosslink and crosslink states. For protocols where many read starts do not coincide with the crosslink position, lowering `-b2p` toward 0.03 stops parameter learning being pulled toward low-coverage artefacts. This applies to PAR-CLIP, where crosslinks are marked by T→C or G→A substitutions rather than truncations, and to constrained-end libraries. For PAR-CLIP specifically, pre-filtering reads carrying the diagnostic substitution improves signal-to-noise more than any PureCLIP setting will.

**n thresholds for learning (`-ntp`, default 10; `-ntp2`, default 0; `-antp` flag).** Only positions with local coverage *n* ≥ `-ntp` are used to learn `bin1.p` and `bin2.p`; only positions with *n* ≥ `-ntp2` are used to learn the state 2 → 2 and 2 → 3 transition. `-antp` chooses both automatically from the expected read-start count at crosslink sites. See "Defaults that quietly gate the fit": on a thin library the default `-ntp` can leave almost nothing to learn from, and `-antp` is the fix.

**Artefact exclusion (`-mkn`, range 0.5–1.5, default 1.0).** Maximum k/N ratio, read starts over local coverage, for a position to contribute to learning truncation probabilities. Positions where nearly all coverage comes from read starts are usually PCR duplicates or collapsed repeats that survived deduplication; excluding them, for example `-mkn 0.5`, stops them skewing the fit and can improve sensitivity at genuine low-signal sites. Reach for this when the score distribution looks pathological or the fit fails to converge.

**Minimum crosslink transition probability (`-mtp`, default 0.0001).** Floor on the state 2 → 3 transition. The help describes it as helpful for poor data where no clear distinction between enriched and non-enriched is possible. Try it before concluding the data is limiting.

**Gamma shape constraint (`-fk`).** Relaxes the constraint that the non-enriched state's shape parameter not exceed the enriched state's, which is imposed when input signal is incorporated. Helps where convergence is slow or the fit is poor; a diagnostic lever more than a tuning knob. Bounds on the shapes themselves are `-g1kmin` (default 1.0, parser minimum 1.5), `-g1kmax`, `-g2kmin`, `-g2kmax` (defaults 1.0, 10.0, 1.0, 10.0).

**Prior enrichment threshold (`-pet`, range 2–50, default 7).** The read-start count whose KDE value separates enriched from non-enriched in the *initial* classification that seeds the fit. A poor initial split can leave the HMM unable to separate its states, which presents as a monotone score distribution.

## Defaults that quietly gate the fit

Check these against your data before trusting a fit. Each one discards or caps information by default, and none of them announces itself.

**`-ntp 10` can starve parameter learning.** On a thin library very few positions reach *n* ≥ 10, and the binomial probabilities are then learned from almost nothing. One dataset in this project had **174 qualifying positions across three chromosomes**. Count how many positions clear `-ntp` before believing `bin1.p` and `bin2.p`, and enable `-antp` when the count is small.

**`-mtc 500` discards whole intervals from learning.** During learning, if *any* position in a covered interval has ≥ `-mtc` read starts, the entire interval is dropped, not just that position. Range 50–50000. Run with `-vv` to see which intervals were dropped.

**`-mtc2 65000` truncates counts.** Read-start counts above it are capped, which changes both k and n at that position. Range 5000–65000.

**Intervals with a single read start are discarded, and there is no flag for it.** In 1.3.1 this is hardcoded on; the `-dis` option that would control it is commented out in the source. On libraries where most read starts sit at singleton positions, this removes a substantial fraction of the data before the model sees it.

**Poly-A and poly-U exclusion is off by default.** `-ea1` and `-et1` exclude such intervals from learning, `-ea2` and `-et2` from analysis, with the stretch length set by `-pa` (default 10). Worth enabling when homopolymer artefacts are visible in the call set.

## Free diagnostics

Outputs the tool will produce on request, cheaper than re-running or re-deriving them.

**Extended output (`-oa`, and `-oe`).** `-oa` emits every position with at least one read start, carrying the state, the score, and a semicolon-separated field with the truncation count, the estimated *n*, the KDE value, the posterior of the called state, the input covariate value, and the log enrichment ratio. `-oe` adds all enriched sites with at least one read start. It lets you build a score distribution over everything, or an evidence-threshold curve, without re-running the HMM.

**Motif covariates (`-fis`, with `-nim` for the maximum motif ID; default uses ID 1 only).** Feeds FIMO motif scores into the model as a covariate. Beyond its intended use it is an independent check: if the fitted coefficient comes back at essentially zero, the motif carries no usable information about crosslink state in this library. The check does not touch your objective.

**Learned parameters (`-p`).** Writes what the fit actually concluded. Read it when a run's output is surprising, before changing parameters.

## Levers of last resort

Listed so you do not invent flags. Reach for them only with a specific symptom.

`-mkde` minimum KDE value for fitting the left-truncated gammas, default the value of a singleton read start · `-mrtf` fit gamma shape only at positions above a covariate value · `-mibr` / `-mibw` iteration caps for BRENT (1–1000, default 100) and Baum-Welch (0–500, default 50) · `-ts` / `-tmv` log-sum-exp lookup table size and floor, defaults 600000 and −2000 · `-upe` pseudo emission probabilities for the crosslink state, for replicate mode where a crosslink emission probability can otherwise hit zero · `-kgw` kernel gap width, range 0–20 · `-ld` long double precision; since v1.2.0 the forward-backward runs in log space so underflow is rare, and it costs memory.

## Post-processing, outside PureCLIP

Width standardization, clustering of adjacent calls, minimum crosslink-event counts and minimum region length convert raw crosslink positions into final footprints. None is part of PureCLIP, but all are usually part of the pipeline being optimized, and *in prior runs* they dominated the objective.

Treat width standardization with particular suspicion. It was the strongest single predictor of the composite score there, through a mechanism that is arithmetic rather than biological: wider intervals overlap replicates and reference regions more often. See "Width inflation" in `optimization.md`. It can stay in the search space, but read any improvement it produces against width-controlled diagnostics.

Minimum crosslink-event thresholds trade yield for confidence directly, and are worth searching. Note the interaction with the objective's yield guard: raising the threshold reduces `n`, which can trip the guard and produce a discontinuous score.

Because `-dm` and everything downstream of it act on written site calls rather than on the HMM fit, a post-processing sweep can reuse cached site calls instead of re-running the caller.

## Failure signatures

- Killed process → too many contigs in `-iv`, or `-nta` above the number of learning contigs.
- Near-zero sites regardless of settings → wrong `-ur` mate selection, or missing deduplication.
- Sites too broad, footprints losing resolution → `-bdw` too large.
- Many false positives in abundant transcripts → no input control.
- Convergence failure, pathological score distribution → artefact positions; try `-mkn`, `-fk`, `-pet`.
- Binomial probabilities look implausible or barely move → too few positions clear `-ntp`; count them, then try `-antp`.
- Motif enrichment near 1 on a protein with a known motif → check the `-ctr` convention and the strand of your windows before blaming the library.
- Region scores rising with no change in site quality → region score is a sum; normalize by site count.

## Version and installation

Available via Bioconda (`conda install -c bioconda -c conda-forge pureclip`); ships as a self-contained C++ binary with GSL statically linked. Also available as an nf-core module and on the European Galaxy server. Verify the version you are running and record it in the report: parameter behaviour has changed across releases, and forks exist.

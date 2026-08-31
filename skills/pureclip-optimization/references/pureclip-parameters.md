# PureCLIP parameters — what they do to the model

PureCLIP fits a two-state hidden Markov model (crosslinked / non-crosslinked) to
genome-wide read-start counts and fragment coverage (Krakau, Richard & Marsico 2017,
*Genome Biology* 18:240, doi:10.1186/s13059-017-1364-2;
docs at https://pureclip.readthedocs.io, source at https://github.com/skrakau/PureCLIP).
Read starts mark reverse-transcriptase truncation at UV crosslink sites; gamma and
binomial emissions separate genuine crosslink enrichment from transcript-abundance
background. Given a size-matched input control, it additionally models the
CLIP-to-input enrichment ratio.

That structure is the reason parameters behave the way they do, and it is worth keeping
in mind: most of these settings are not thresholds on the output, they are inputs to a
fit. Changing them changes what the model believes background looks like.

## What is determined by the protocol, and should be fixed

Getting these wrong produces symptoms that look like tuning problems and are not. Settle
them before any search, since a sampler exploring them is wasting evaluations on
questions that have correct answers.

**Which mate carries the cDNA end.** The crosslink position is inferred from read
starts, so using the wrong mate destroys the signal — typically presenting as
near-zero sites regardless of other settings. iCLIP single-end needs no selection;
iCLIP paired-end uses read 1; eCLIP paired-end uses read 2 (`-ur 1` / `-ur 2`).

**Input control.** Supply it when it exists (`-ic` / `-ibai`). It substantially reduces
false positives in abundant transcripts, which is a different problem from anything
bandwidth or filtering can fix. In prior runs, using the control co-occurred with the
higher-confidence, lower-yield regime — consistent with it removing
abundance-driven calls.

**Replicates.** PureCLIP ≥1.3.0 can learn emission parameters per replicate and combine
them in a joint HMM (`-i2` / `-bai2`), calling sites supported across replicates. Note
the interaction with your objective: if you use PureCLIP's joint replicate mode *and*
score replicate reproducibility, you are partly scoring what the caller already
enforced. Pooling replicates for calling and scoring reproducibility from separate
per-replicate runs keeps the metric independent of the caller. Decide deliberately and
report which you did.

**Preprocessing, upstream of PureCLIP entirely.** Adapter trimming; UMI deduplication
if the library carries UMIs; unique mapping only; end-to-end alignment rather than
soft-clipped (soft clipping shifts apparent read starts away from the true crosslink
position and silently degrades single-nucleotide resolution); coordinate-sorted and
indexed. PureCLIP cannot distinguish PCR duplicates from real read-start enrichment, so
skipped deduplication inflates scores at artefact positions — and no parameter setting
recovers from it. If you inherit BAMs, confirm this happened rather than assuming.

## The parameters worth searching

**Bandwidth (`-bdw`, and `-bdwn` for the binomial *n* estimate).** Controls KDE
smoothing of the coverage landscape used to fit the HMM. Too small fragments a coherent
signal into noise; too large smears distinct crosslink events into broad regions and
gives up the single-nucleotide resolution that motivates using PureCLIP at all. This is
the parameter most directly tied to the physics of the assay — and, in prior runs, the
one the composite objective was nearly blind to (median ρ ≈ −0.01 with score; ρ ≈ −0.33
with site count, so more smoothing yields fewer sites). Judge it on the call set — width
distribution, positional precision — not only on the score.

**Merge distance (`-dm`, default 8).** How close two sites must be to merge into one
binding region. Interacts directly with any downstream clustering or width
standardization you apply; if both are in the search space, the sampler can trade one
against the other, so consider whether both need to be free.

**Binding context (`-bc`).** Default suits compact, well-defined footprints; the
alternative suits RBPs producing broad clusters or binding low-complexity sequence.
This is a genuine question about the protein, so let what is known about it inform the
prior rather than leaving it entirely to search.

**Artefact handling (`-mkn`).** Positions where nearly all coverage comes from read
starts (k/N ≈ 1) are usually PCR duplicates or collapsed repeats that survived
deduplication. Excluding them from parameter learning (e.g. `-mkn 0.5`) stops them
skewing the fit and can improve sensitivity at genuine low-signal sites. Reach for this
when the score distribution looks pathological or the fit fails to converge.

**Gamma shape constraint (`-fk`).** Relaxes the constraint that the non-enriched state's
shape parameter not exceed the enriched state's. Helps where convergence is slow or the
fit is poor; a diagnostic lever more than a tuning knob.

**Initial binomial probability and *n* thresholding (`-b2p`, `-antp`).** For protocols
where many read starts do not coincide with the crosslink position — PAR-CLIP, where
crosslinks are marked by T→C or G→A substitutions rather than truncations, or
constrained-end libraries — lowering `-b2p` (e.g. 0.03) and enabling automatic *n*
thresholding stops parameter learning being pulled toward low-coverage artefacts.
For PAR-CLIP specifically, pre-filtering reads carrying the diagnostic substitution
improves signal-to-noise more than any PureCLIP setting will.

**Numerical precision (`-ld`).** Since v1.2.0 the forward-backward runs in log space, so
underflow is rare. Only needed if emission probabilities collapse to zero with a
control BAM containing many artefacts; it costs memory.

## Post-processing of raw calls

Whatever converts raw crosslink positions into final footprints — width
standardization, clustering of adjacent calls, minimum crosslink-event counts, minimum
region length — is not part of PureCLIP but is usually part of the pipeline being
optimized, and in prior runs it dominated the objective.

Treat width standardization with particular suspicion. It was the strongest single
predictor of the composite score there, through a mechanism that is arithmetic rather
than biological: wider intervals overlap replicates and reference regions more often.
See the width-inflation discussion in SKILL.md; hold it in the search space if you like,
but read any improvement it produces against width-controlled diagnostics.

Minimum crosslink-event thresholds are the honest way to trade yield for confidence,
and worth searching. Note the interaction with the objective's yield guard: raising the
threshold reduces `n`, which can trip the guard and produce a discontinuous score.

## Output

Crosslink sites come out as BED6 with the HMM's log-likelihood ratio in the score
column — higher meaning more confident. Binding regions (`-or`) merge sites within the
merge distance, scored by the maximum site score in the region.

The HMM already acts as a filter, so post-hoc score thresholding is optional. If you do
threshold, set it from the score distribution's shape — an inflection between the bulk
and a high-scoring shoulder — rather than a round number, and remember that thresholding
is itself a parameter: it belongs in the search space and the report, not applied
silently afterwards.

## Memory and runtime

The dominant lever is which contigs are used for *parameter learning* (`-iv`, e.g.
`'chr1;chr2;chr3;'`). Learned parameters apply genome-wide regardless, so restricting
learning to a few large chromosomes cuts memory substantially with little effect on
parameter quality, while including unassembled scaffolds multiplies cost for nothing.
Note this is distinct from restricting the genomic scope you *call and score* on — a
choice driven by the objective's resolution, discussed in SKILL.md.

Rough scale: a few chromosomes fits in ~8–16 GB and tens of minutes on several threads;
all human chromosomes runs 32–64 GB and hours; adding a control BAM increases both.
Threads via `-nt`. Expect a genome-wide run to take most of a day, which is why search
budgets have to be planned around trial cost.

Common failure signatures worth recognizing: killed process → too many contigs in
learning; near-zero sites → wrong mate selection, or missing deduplication; sites too
broad → bandwidth too large; many false positives in abundant transcripts → no input
control; convergence failure → artefact positions, try `-mkn` / `-fk`.

## Installation

Available via Bioconda (`conda install -c bioconda -c conda-forge pureclip`); ships as a
self-contained C++ binary with GSL statically linked. Also available as an nf-core
module and on the European Galaxy server. Verify the version you are running, and record
it in the report — parameter behaviour has changed across releases, and forks exist
(the prior-runs cohort used a fork, not upstream).

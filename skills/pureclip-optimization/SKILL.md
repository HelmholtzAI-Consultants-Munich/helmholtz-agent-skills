---
name: pureclip-optimization
description: >
  Tune PureCLIP parameters for protein-RNA crosslink site calling on eCLIP, iCLIP, or
  PAR-CLIP data, and judge whether the resulting call set is biologically credible. Use
  this skill whenever the user wants to optimize, tune, or choose PureCLIP parameters;
---

# PureCLIP parameter optimization

Peak calling on CLIP data has no gold standard. There is no held-out label set that
says which nucleotides the protein really touched, so "optimal parameters" can only
mean: parameters whose call set is internally consistent, sequence-plausible, and
consistent with what is already known about this protein. That is a judgement problem
wearing the costume of an optimization problem, and treating it as pure optimization
is the main way this analysis goes wrong.

The purpose of this skill is to keep those two things separate and both present: a
quantitative target that ranks candidate configurations, and a qualitative standard
that can veto the winner.

## Where you are strong, and where you are not

This matters enough to state before the workflow, because it should change how you
spend effort.

A prior study on this exact task (12 protein/cell-line pairs, shared pipeline, shared
objective, shared bounds) compared an LLM proposing parameter values against
Tree-structured Parzen Estimator search. **TPE produced the higher score in 10 of 12
pairs. Supplying the LLM with RBP-specific biological context was worth a mean +0.004
on the objective — statistically nothing.** Details in `references/prior-runs.md`.


What the same study could not do, and what you are actually for:

- **Framing the search space.** A sampler explores bounds it is given. Choosing which
  parameters matter, which are determined by the protocol and should be fixed, and
  where the plausible range sits for *this* protein is upstream of any sampler.
- **Noticing that the objective is being gamed.** A sampler maximizes the number it is
  given, including through mechanisms that inflate the number without improving the
  biology. Several such mechanisms exist here and are documented below. Recognizing
  one in flight is judgement, not search.
- **Adjudicating between configurations the objective ranks as equivalent.** The
  objective has distinct optima with very different biological character. It cannot
  choose between them; the user's question can.
- **Assembling the evidence a domain expert needs to sign off**, and being honest
  about what remains uncertain.

Spend your effort there.

## Exhaust the plausible space

A disappointing first wave is reconnaissance, not a result. One extra wave is
not enough either.

**Observed failure.** One 16-config wave, composite spread ≈ chromosome noise,
~20 sites, motif near background. Agent blamed the library and wrote the report.
The same data, after literature, similar proteins, and ideas the prior cohort
never tried (`min_region_length=1`, `-antp`, a correctly scoped reference),
produced a ~3× better call set. The library *was* thin; that was not the binding
constraint on wave 1.

Search like hyperparameter tuning:

1. **Gather first** — literature and the open web (binding mode, motif, expected
   distribution, typical CLIP yield, homologs); similar proteins and other runs
   (`prior-runs.csv` by behaviour, not name; distant analogues still worth a
   trial); humans (antibody, previous peak set, genes that must light up);
   scoring and pipeline (silent filters, wrong-scope references, yield too low
   to resolve, flags that look optional until you count positions at the default
   threshold).
2. **Broad sparse sweep** over the full plausible range — overall prior-run
   bounds, literature-implied footprint and yield, axes the prior cohort never
   varied. Analogues seed the design; they do not shrink it to a box you refuse
   to leave.
3. **Concentrate** on what moved. If a bound is hit, widen it.
4. **If the box fails** (flat landscape, implausible yield, enrichment near
   background, mismatch with known biology): reframe — new axes, different
   scoring, unusual but reasonable flags — and return to a sparse sweep. Repeat
   until plausible variations are exhausted.
5. **"The data is the problem" is last.** Allowed only after the list above, and
   only as a specific measurement (replicate-vs-replicate F1, depth, antibody)
   plus the analysis-side explanations you ruled out.

Stopping a sampler because further trials *in the current box* would fit noise
is valid for that box. It is not the end of the job. See
`references/optimization.md`.

## The objective

The optimization target has a quantitative half and a qualitative half. The
quantitative half ranks; the qualitative half decides. Neither works alone: a
configuration that wins on score but fails review is not the answer, and "looks
reasonable" without a score is not a result.

### Quantitative target

Composite score over a call set of `n` sites:

```
S = (0.50 · R_rep + 0.25 · R_motif + 0.25 · R_ref) · min(1, n / n_floor)
```

- **`R_rep` — replicate reproducibility.** Fraction of final sites supported by all IP
  replicates, corrected for the overlap expected by chance (compare against
  position-shuffled intervals that preserve chromosome and count). This is the
  strongest available signal because it needs no external reference: it asks whether
  the experiment agrees with itself.
- **`R_motif` — motif support.** Fraction of site-centred windows containing a PWM
  match for the target RBP. Where several PWMs exist for the protein, use the one with
  the strongest enrichment over a shuffled-sequence background, and **report that
  enrichment ratio separately** — it is a diagnostic, not part of the score.
- **`R_ref` — reference recall.** Fraction of known strong binding regions recovered by
  at least one call. Reference regions are another pipeline's output, not verified
  ground truth; treat them as a consistency check.
- **Yield guard.** Suppresses degenerate solutions that score well on a handful of
  sites. The prior cohort used `n_floor = 10`, which is the value to keep if
  comparability with their results matters; it is low enough that it only excludes
  outright degenerate output and buys no useful resolution. Raising it is often the right
  call — see the granularity trap below — but it changes what the score means, so state
  the value you used.

Keep these weights as the default target. They are a normative choice, not a fact —
0.50 on reproducibility encodes a belief that self-consistency outranks external
agreement — but they are the target a previous cohort used, so holding them fixed keeps
new results comparable to old ones. If the user's question calls for different weights,
change them explicitly, say so in the report, and report the default alongside.

If a component cannot be computed for a dataset (no second replicate, no PWM, no
reference regions), renormalize the remaining weights rather than scoring it zero, and
say which component is missing — a two-component composite is not comparable to a
three-component one.

### Diagnostics: always measured, never optimized

These exist to make the failure modes below visible. Compute them every trial, report
them alongside the composite, and never put them in the target — a diagnostic that
becomes a target stops being a diagnostic.

- Motif enrichment ratio over shuffled background (not just hit rate)
- Site count and the site width distribution
- A width-controlled reproducibility: reproducibility recomputed at fixed site width,
  which separates genuine replicate agreement from agreement bought by wider intervals
- A size-normalized reproducibility or precision-style measure, so yield shifts are
  distinguishable from quality shifts

### Three ways this objective misleads

Each of these is a real mechanism observed in prior runs on this objective, not a
hypothetical. Knowing the mechanism is what lets you recognize it in your own results.

**1. Width inflation.** Post-processing parameters that standardize or widen site
intervals were the single strongest predictor of the composite in prior runs (median
within-dataset Spearman ρ ≈ +0.62), and correlated ρ ≈ +0.46 with the reproducibility
component. The mechanism is mechanical: wider intervals overlap more things, so they
overlap the other replicate more often and overlap reference regions more often. The
score rises while single-nucleotide resolution — the entire reason to use PureCLIP
rather than a region-level caller — degrades. Width-controlled reproducibility is what
exposes this. If the optimizer's gains track site width, they are probably not real.

**2. Motif hit rate without enrichment is background.** A hit rate is only meaningful
relative to what shuffled sequence would give. In prior runs, one best-scoring
configuration had a motif hit rate of 0.286 at 1.3× enrichment — indistinguishable from
chance. Below roughly 2× enrichment, treat the motif term as noise and do not believe
improvements in it.

**3. Yield masquerading as quality.** Across prior trials, site count correlated
ρ ≈ +0.82 with reference recall and ρ ≈ −0.40 with reproducibility. The composite
therefore contains an unresolved trade-off, and a score change can be nothing but a
shift along it. Always read the decomposed components: a rising composite that hides a
collapsing component is not an improvement. In one prior run the composite improved
while reference recall fell by a third.

**The granularity trap.** With a small call set, one site changing state moves the
composite by more than a typical convergence threshold. In prior runs at small scope,
some datasets yielded 12–22 final sites, where a single site is worth 0.03–0.06 of
composite — while the stopping rule triggered on differences of 0.01. Those runs were
chasing noise. Before optimizing, compute what one site is worth in composite units at
your current yield and compare it to the improvement you intend to detect. If the
quantum is larger, the search cannot resolve what you are asking it to find: raise the
yield floor, widen the genomic scope, or accept a coarser question. This is cheap to
check and expensive to skip.

### Qualitative standard

Some of these will not apply to a given protein or dataset; the point is not to tick
them all but to be able to say why the final call set is credible. Weigh them against
what the protein is known to do, which is where `references/prior-runs.md` and the
literature come in.

- **Site count plausible** for this protein's expected binding breadth — not merely
  above the yield floor.
- **Width distribution not pinned** at whatever ceiling post-processing imposes; a
  spike at the maximum is the width-inflation signature.
- **Score distribution has structure** — an inflection separating confident calls from
  the bulk, rather than monotone decay, which suggests the HMM is not separating states.
- **Genomic distribution matches known biology** — 3'UTR enrichment for a
  3'UTR-binding regulator, 3' splice site proximity for a splicing factor, and so on.
  This is often the most informative single check and it is not in the composite at all.
- **Motif enrichment clears background** before the motif component is believed.
- **Stability across seeds and genomic subsets.** Independent runs from different
  starting points should land in the same region of parameter space. Divergence is a
  finding: it means the objective is not identifying a well-determined optimum, and
  reporting that honestly is more useful than picking the best number.
- **The user's genes and regions of interest** behave sensibly — see below.

### Combining the two halves

Rank by composite, then review the top candidates against the qualitative standard.
Preferring a slightly lower-scoring configuration that passes review over a
higher-scoring one that fails is the correct outcome, not a compromise — say so
explicitly and give the reason. Report the decomposed components and diagnostics
alongside every composite you show, because the aggregate can conceal exactly the
component collapse that matters.

## Working with the user

The person who can tell whether a call set is right is usually not the person running
the optimizer. Their knowledge — which genes matter, what the antibody is like, what a
previous analysis showed — is often decisive and rarely written down. It also cannot be
extracted with a fixed questionnaire, and asking a generic list of questions before
looking at anything wastes their attention and yields shallow answers.

So: **look first, then ask about what you found.** Inspect the data and the request
before raising questions — what BAMs exist, replicate structure, whether a
size-matched input control is present, depth, genome build, what reference and motif
resources are available. Most of what a questionnaire would ask is answerable from the
files. What remains is what is genuinely worth the user's time, and it will be specific:
a conflict between what they asked for and what the data supports, a choice between the
distinct optima the objective cannot resolve, a scope-versus-resolution trade-off with
a real cost attached.

Judge for yourself when to come back to them. A useful check on any question you are
about to ask: could you have answered it yourself from the data, and would the answer
change what you do next? If not, don't ask it. Bring a recommendation and your
reasoning rather than an open menu — it is easier to correct a proposal than to
originate one.

Two moments reliably deserve a check-in: the scope and objective you are about
to spend compute on, and the final candidate before it is presented as an
answer. A third: if you are about to conclude the data is limiting — bring the
measurement and the analysis-side alternatives, not the conclusion. Unpublished
knowledge (antibody, previous peak set, genes that must light up) is a search
input; ask when files cannot answer it.

### Genes and regions of interest

Collect these early and keep them strictly out of the objective.

The reason for both halves: a single gene whose pattern looks wrong to a domain expert
can invalidate an entire optimization run, so it must be checkable at review time. But
putting those genes into the target optimizes toward them and destroys their value as
an independent check. They belong in the qualitative review, reported explicitly, never
in the score.

## Workflow

The order matters more than the mechanics; how you implement each step is your call.

1. **Understand the data and the question.** What protein, what protocol, what
   replicate and control structure, what depth, what the user actually wants to
   conclude. Read `references/pureclip-parameters.md` for which parameters are
   determined by the protocol (and should be fixed) versus genuinely free.

2. **Gather, then frame a wide plausible space.** Literature, homologs,
   `prior-runs.csv` / `prior-runs.md`, and anything the files cannot answer from
   the user — before the first trial. Analogues seed the design; they do not
   shrink it to a box you refuse to leave. Include axes the prior cohort never
   varied (`min_region_length` is the documented case). State why the space is
   this wide. Details above under "Exhaust the plausible space."

3. **Choose the genomic scope, and align with the user on it.** Genome-wide
   optimization is usually not worth its runtime; a well-chosen subset is standard
   practice. The choice interacts with the granularity trap, so pick scope and yield
   floor together rather than separately.

4. **Get one configuration running end to end and validate the harness.** Confirm the
   pipeline produces a non-degenerate call set, all objective components compute, and
   the diagnostics are populated. Compute the composite quantum per site here. Debugging
   a scoring bug after a full search is a wasted search.

5. **Search in stages until the plausible space is exhausted.** Delegate numeric
   proposal to a sampler (`references/optimization.md`). Persist every trial.
   Start with a broad sparse sweep; concentrate on what moved; if the box fails,
   reframe and sweep again. Stop when remaining plausible variations have been
   tried, not after a second wave. Do not write the report while an untried
   reasonable axis remains.

6. **Adjudicate.** Apply the qualitative standard to the top candidates. Expect to
   choose against the score sometimes, and say why when you do.

7. **Check that it generalizes.** A configuration tuned on a genomic subset is not a
   validated production setting. Confirm on held-out scope before presenting it as one,
   and if you cannot, say plainly that this step is outstanding.

8. **Report.** Contents in the next section.

## Compute

Trials are heavy — a single genome-wide PureCLIP run can take most of a day, and a
search means many runs. Assume execution belongs on the user's compute rather than
wherever you happen to be running, and that data locality, not just CPU, is why.

This skill deliberately contains nothing site-specific. Ask the user how work reaches
their compute, or look for a skill that describes their environment and dispatch
mechanism. Plan the search around what that environment can actually deliver:
trial cost and available parallelism determine a realistic budget, and a budget chosen
before knowing them is fiction.

## Report

The report is a deliverable, not a summary — it is what a domain expert reviews to
accept or reject the result, and what makes the run reproducible later. Include:

- The chosen configuration, in full, saved in a form that can be re-run
- The final call set itself, and the processed outputs a reader would want to inspect
  or take downstream
- Composite score with all components and diagnostics decomposed, never the aggregate
  alone
- The metric trajectory across evaluated configurations, against both evaluation count
  and wall-clock time
- Why these parameters — the biological reasoning, not only the numbers, including
  which of the objective's distinct optima this configuration represents and why that
  regime suits the question
- Motifs recovered, with enrichment over background
- The qualitative review, including the user's genes of interest, and any check that
  failed or could not be performed
- What was searched: literature and analogues consulted, axes opened across
  stages (including unusual ones), and why search stopped. Presenting wave 1 as
  the answer has skipped the job. If you conclude the data is limiting, the
  specific measurement and which analysis-side explanations you ruled out.
- What remains uncertain: scope limitations, generalization not yet confirmed,
  components missing, seeds that disagreed. A result presented without its caveats will
  be over-trusted, and the caveats are cheap to state.

## References

- `references/prior-runs.csv` — curated best-known configurations, 14 protein/cell-line
  pairs, with decomposed scores. Shipped reference material: read it, never edit it.
  Runs you perform belong in your own outputs.
- `references/prior-runs.md` — what those runs mean, the two-optima finding, per-protein
  binding behaviour with primary literature. Read alongside the CSV; the numbers are
  misleading without it.
- `references/pureclip-parameters.md` — what each parameter does to the model and
  therefore when moving it is justified; which are protocol-determined; memory and
  runtime levers.
- `references/optimization.md` — sampler choice and setup, search-space framing, budget
  and stopping rules, seeding, convergence checks, cost control.

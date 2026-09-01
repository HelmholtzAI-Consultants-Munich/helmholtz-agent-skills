# Running the search

## Contents

- What you are for, and what the sampler is for
- Why a Bayesian sampler fits this problem
- Framing the space is the part that matters
- Budget and stopping
- One wave is not enough: a worked case
- Seeds, convergence, and what disagreement means
- Pruning and cost control
- Reporting the search

## What you are for, and what the sampler is for

Delegate numeric proposal to a sampler and spend your effort on what surrounds it: the
space, the budget, the diagnostics, and the interpretation.

A prior study on this task compared an LLM proposing parameter values against
Tree-structured Parzen Estimator search, across 12 protein/cell-line pairs sharing a
pipeline, an objective and bounds. TPE reached the higher score in 10 of 12. Supplying
the LLM with RBP-specific biological context was worth a mean +0.004 on the objective,
which is nothing. The comparison was not budget-matched, so it does not rank the two
optimizers; what it establishes is that proposing numbers is not where your effort pays.
Details in `prior-runs.md`.

Four things that study could not measure, which are yours:

- **Framing the search space.** A sampler explores the bounds it is given. Which
  parameters matter, which are fixed by the protocol, and where the plausible range sits
  for this protein are all settled before it starts.
- **Noticing the objective is being gamed.** A sampler maximizes the number it is given,
  including through mechanisms that inflate the number without improving the biology.
  Those mechanisms are listed in SKILL.md; recognizing one in a live run is judgement.
- **Adjudicating between configurations the objective ranks as equivalent.** The
  objective has two optima with different biological character. It cannot choose between
  them; the user's question can.
- **Assembling the evidence a domain expert needs to sign off**, including what remains
  uncertain.

### How the score misleads

**Width inflation.** Post-processing parameters that widen or standardize intervals were
the strongest predictor of the composite in prior runs, at ρ ≈ +0.62, and ρ ≈ +0.46 with
the reproducibility component. Wider intervals overlap more of everything, so they hit
the other replicate and the reference regions more often while single-nucleotide
resolution degrades. Reproducibility at fixed width exposes this. If gains track site
width, they are probably not real.

**Motif hit rate without enrichment.** A hit rate means nothing except against shuffled
sequence. One best-scoring prior configuration hit 0.286 at 1.3× enrichment, which is
chance. Below roughly 2× enrichment, treat the motif term as noise.

**Yield standing in for quality.** Site count correlated ρ ≈ +0.82 with reference recall
and ρ ≈ −0.40 with reproducibility across prior trials, so a change in the composite can
be nothing but movement along that trade-off. In one prior run the composite improved
while reference recall fell by a third. Read the decomposed components every time.

**Differences below the metric's resolution.** With a small call set, one site changing
state moves the composite more than a typical convergence threshold. Prior runs at small
scope yielded 12–22 sites, where one site was worth 0.03–0.06 of composite and the
stopping rule triggered on 0.01. Compute what one site is worth at your expected yield
before optimizing. If it exceeds the improvement you mean to detect, raise the yield
floor, widen the genomic scope, or accept a coarser question.

### Credibility review

Apply these to the top candidates after ranking, and keep them out of the score. Not all
apply to every protein; the test is whether you can say why this call set is credible.

- **Site count** plausible for the protein's known binding breadth, not merely above the
  yield floor.
- **Width distribution** not pinned at the ceiling post-processing imposes. A spike at
  the maximum is the width-inflation signature.
- **Score distribution** with an inflection separating confident calls from the bulk.
  Monotone decay suggests the HMM is not separating its two states.
- **Genomic distribution** matching known biology: 3'UTR enrichment for a 3'UTR-binding
  regulator, 3' splice site proximity for a splicing factor. Often the most informative
  single check, and absent from the composite.
- **Motif enrichment** clearing background before the motif component is believed.
- **Stability across seeds and genomic subsets.** Runs from different starting points
  should land in the same region of parameter space. Divergence means the objective is
  not identifying a well-determined optimum; report it as a finding.
- **The user's genes and regions of interest** behaving sensibly. Collect them early and
  keep them out of the score: a single gene that looks wrong to a domain expert can
  invalidate a run, and scoring against it destroys its value as an independent check.

Preferring a lower-scoring configuration that passes review over a higher-scoring one
that fails is the right outcome. Say which you chose and why, and show the decomposed
components and diagnostics with every composite.

The objective has two optima with comparable scores and different biological character: a
high-yield regime that recovers most reference regions at weaker per-site sequence
support, and a high-confidence regime with fewer sites, better replicate agreement and
stronger motif enrichment. The weights decide which one wins, not the protein. When
candidates split this way, put the choice to the user: a conservative set of sites they
would defend individually, or broad coverage of the regions where the protein acts. See
[prior-runs.md](./references/prior-runs.md).

## Why a Bayesian sampler fits this problem

The search space is small (a handful of integer and binary parameters), each evaluation
is expensive relative to the cost of deciding what to try next, and there are no
gradients. That is the regime sequential model-based optimization was built for. TPE
(Bergstra et al. 2011) models the parameter distributions of high- and low-scoring
trials separately and proposes candidates more likely under the high-scoring model;
Optuna (Akiba et al. 2019, doi:10.1145/3292500.3330701) provides a seeded, reproducible
implementation with pruning and persistent storage.

Optuna is the pragmatic default because the storage and trial-record machinery is
already what you need for the report. Random search over a well-chosen small box is a
legitimate baseline — with a dozen evaluations and a good prior it is not obviously
worse, and it parallelizes without coordination. Grid search is rarely justified here:
it spends its budget uniformly on a landscape that is not uniformly interesting.

## Framing the space is the part that matters

A sampler explores what it is given. Three decisions determine whether it succeeds, and
none of them are the sampler's:

**Which parameters are free.** Protocol-determined settings (mate selection, control
usage, replicate handling) have correct answers and should be fixed — see
`pureclip-parameters.md`. Every fixed parameter is budget redirected to a question that
is actually open.

**Where the bounds sit.** Prior runs give real ranges (`prior-runs.md`). Analogues
are a prior for where to look first, not a box you stay inside. Start broad enough
to cover the plausible range (overall prior-run bounds, literature-implied
footprint and yield, axes the prior cohort never varied). Bounds cap what can be
found — if the optimum sits at a bound, the box was wrong. Widen and keep going.

**Whether parameters are redundant.** Merge distance, cluster gap, and width
standardization all act on how nearby calls become footprints. With all three free, a
sampler can trade them against each other and spend its budget wandering a ridge of
equivalent configurations. Fixing one or coupling them is often better than exploring
all three.

Log every trial's parameters, all objective components, and all diagnostics as a durable
record — one row per trial, written as it completes. The trajectory is a required part of
the report, the records are what makes a run auditable, and a search whose intermediate
results were not persisted cannot be analyzed after the fact.

## Budget and stopping

Two rules, both learned from prior runs going wrong:

**A stopping threshold below the metric's resolution is meaningless.** Compute what one
site is worth in composite units at your expected yield before setting a convergence
threshold. Prior runs used a threshold of 0.01 on datasets where a single site was worth
0.03–0.06 — every stop decision there was made on noise. If the quantum exceeds the
threshold you want, fix the resolution (more scope, higher yield floor) rather than
tightening the threshold.

**Compare optimizers only at matched budget.** The prior study's headline result — TPE
ahead in 10 of 12 pairs — came with TPE using 14–16 evaluations against the LLM's 5–9,
which is why it establishes a protocol outcome and not an optimizer ranking. If you
compare approaches, fix the number of successful evaluations and report wall-clock and
cost separately. Note also that samplers with a startup phase (TPE typically draws
~10 initial trials before its model contributes) need a budget several times that phase
to be doing anything model-based at all — a 12-evaluation TPE run is mostly random
search wearing a Bayesian label.

Set the budget from trial cost and available parallelism, which means finding those out
first. A budget chosen before knowing how long a trial takes is a guess that will be
abandoned mid-run.

**Stopping the sampler is not stopping the analysis.** A flat landscape inside the
current box means further trials *in that box* will fit noise. Reframe: widen
bounds that were hit, open axes nobody varied, fix scoring if it cannot resolve
the question, then another sparse pass. Stop when plausible variations have been
exhausted — not after one extra wave, and not because wave 1 looked like a data
problem.

**Search in stages.** Broad sparse sweep over the plausible range, then
concentrate on what moved. If that region fails qualitative review or sits on a
bound, open the next plausible axis and sweep again. A single TPE run on the
first box is stage one, not the procedure.

## One wave is not enough: a worked case

One 16-configuration wave produced a composite spread comparable to chromosome-to-chromosome
noise, about 20 sites, and motif enrichment near background. The agent concluded the
library was thin and wrote the report.

The same data, after a literature search, comparison with similar proteins, and three
ideas the prior cohort had never tried, namely `min_region_length = 1`, `-antp` and a
correctly scoped reference-region file, produced a call set roughly three times better.
The library was thin. That was not what limited wave 1.

## Seeds, convergence, and what disagreement means

Seed the sampler and record the seed; an unreproducible search is not a result.

Beyond reproducibility, run the search more than once from different starting points —
different sampler seeds, and ideally different genomic subsets. If the runs converge to
similar parameter regions, the objective is identifying a well-determined optimum and
the answer is trustworthy. If they diverge, that is a genuine finding about the
objective, not a nuisance: it means the landscape is flat or noisy at the scale you are
searching, and the honest report says so rather than presenting whichever run scored
highest. Divergence is also the cheapest available evidence that a scope or yield-floor
choice was too aggressive.

## Pruning and cost control

Trials are expensive enough that early termination is worth wiring up, but the obvious
implementation is wrong here: pruning on the composite mid-trial does not work, because
the composite is only defined once the full call set exists.

What does work is failing fast on conditions that make a trial uninformative — a
degenerate call set below the yield floor, a configuration that has already been
evaluated, a run that exceeds a wall-clock ceiling. Detect those before the expensive
stage where possible. Also worth caching: identical parameter sets recur in samplers,
and re-running a completed configuration buys nothing.

If your compute allows parallel trials, use it — TPE handles concurrent trials with some
loss of sequential information, and random search loses nothing. Given trial costs
measured in hours, parallelism usually buys more than sampler sophistication.

## Reporting the search

Beyond the best configuration, the search itself is evidence:

- Best-score trajectory against **both** evaluation count and wall-clock time. These
  answer different questions (sample efficiency versus practical cost) and the first
  alone hides an expensive search.
- Which parameters the search actually moved, and which it converged on. A parameter
  the sampler explored widely without score consequence is telling you the objective is
  insensitive to it — which is information about the objective, and worth stating.
- Where the optimum sits relative to the bounds.
- Agreement or disagreement across seeds.
- The trial records themselves, so a reader can recompute anything.

# Running the search

The premise here is that numeric proposal should be delegated to a sampler and your
effort spent on what surrounds it: the space, the budget, the diagnostics, and the
interpretation. This file covers the surrounding parts.

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

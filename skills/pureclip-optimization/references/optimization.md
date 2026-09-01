# Running the search

Mechanics of individual parameters are in `pureclip-parameters.md`; report structure and tone are in `report-format.md`. This file covers how to run the search.

## What you decide, and what the sampler decides

The sampler proposes numbers. Everything that decides whether those numbers mean anything is yours: which parameters are in play, how wide the bounds are, whether the score measures what you think, and which candidate to recommend. A prior study on this task compared an LLM proposing parameter values against Tree-structured Parzen Estimator search, across 12 protein/cell-line pairs sharing a pipeline, an objective and bounds. TPE reached the higher score in 10 of 12. Supplying the LLM with RBP-specific biological context was worth a mean +0.004 on the objective, which is negligible. The comparison was not budget-matched, so it does not rank the two optimizers; it shows only that proposing numbers is not the best use of your effort. Details in `prior-runs.md`.

Four jobs that study could not measure, and that no sampler performs:

- **Framing the space.** A sampler explores the bounds it is given. Which parameters matter, which are fixed by the protocol, and where the plausible range sits for this protein are all settled before it starts.
- **Noticing the score is being gamed.** A sampler maximizes whatever number it is given, including through mechanisms that inflate it without improving the biology. Four such mechanisms are documented below.
- **Adjudicating between configurations the objective ranks as equivalent.** The objective has two optima with different biological character. It cannot choose between them; the user's question can.
- **Assembling the evidence a domain expert needs to sign off**, including what remains uncertain.

## Frame the space before you search it

**Which parameters are free.** Protocol-determined settings such as mate selection, input-control usage and replicate handling have correct answers, not ranges. Settle them from `pureclip-parameters.md` and fix them. Every parameter you fix frees budget for a question that is still open.

**Where the bounds sit.** Prior runs give real ranges: `prior-runs.csv`, read alongside `prior-runs.md`. Treat analogues as a prior for where to look first, not as a box to stay inside. Start broad enough to cover the plausible range: the overall bounds across prior runs, the footprint and yield the literature implies for this protein, and the axes the prior cohort never varied. Bounds cap what can be found, so an optimum sitting on a bound means the box was wrong. Widen it and keep going rather than reporting the edge as an answer.

**Which parameters are redundant.** Merge distance, cluster gap and width standardization all act on the same thing: how nearby calls become footprints. With all three free, a sampler can trade them against each other and spend its budget wandering a ridge of near-equivalent configurations. Fixing one, or coupling them, usually buys more than exploring all three.

## Pick the cheapest sampler that fits the problem

The space is small, a handful of integer and binary parameters. Each evaluation is expensive relative to the cost of deciding what to try next, and there are no gradients. That is the regime sequential model-based optimization was built for.

**Default: Optuna with TPE.** TPE (Bergstra et al. 2011) models the parameter distributions of high- and low-scoring trials separately and proposes candidates more likely under the high-scoring model. Optuna (Akiba et al. 2019, doi:10.1145/3292500.3330701) gives a seeded, reproducible implementation with pruning and persistent storage, and its trial-record machinery is already what the report needs.

**Random search is a legitimate baseline, not a fallback.** Over a well-chosen small box, with a dozen evaluations and a good prior, it is not clearly worse than TPE. **Grid search is rarely justified here:** it spends its budget evenly across a landscape where most regions are uninformative.

**Trap: a TPE run too short to be Bayesian.** TPE typically draws about 10 initial trials at random before its model contributes anything, so a 12-evaluation run is mostly random search. Either budget several times the startup phase, or use random search and say so.

Run trials in parallel if the compute allows. TPE handles concurrent trials with some loss of sequential information; random search loses nothing. With trial costs measured in hours, parallelism usually buys more than sampler sophistication.

## Set the budget from measured cost, the stopping rule from measured resolution

Find out what one trial costs and how many can run at once before choosing a budget; one chosen before you know the cost will not hold.

**The stopping threshold cannot be finer than the metric's resolution.** Compute what one site is worth in composite units at your expected yield, then set the convergence threshold above it. Prior runs used a threshold of 0.01 on datasets where a single site was worth 0.03–0.06, so every stop decision there was made on noise. If one site is worth more than the difference you want to detect, fix the resolution with more genomic scope or a higher yield floor, rather than tightening the threshold. The mechanism is under "Differences below the metric's resolution".

**Trap: comparing approaches at unmatched budget.** The prior study's headline result, TPE ahead in 10 of 12 pairs, came with TPE using 14–16 evaluations against the LLM's 5–9. If you compare approaches, fix the number of successful evaluations and report wall-clock time and cost separately.

## Make every trial auditable and every failure cheap

Write one row per trial as it completes: the parameters, every objective component, every diagnostic. The trajectory is a required part of the report, and a search whose intermediate results were not persisted cannot be audited or reanalysed afterwards.

**Pruning on the composite mid-trial does not work**, because the composite is only defined once the full call set exists. What does work is failing fast on conditions that make a trial uninformative: a degenerate call set below the yield floor, a configuration that has already been evaluated, a run past a wall-clock ceiling. Where possible, detect them before the expensive stage. Cache completed configurations, since identical parameter sets recur in samplers and re-running one buys nothing.

## Distrust a gain you cannot explain

A rising composite is a hypothesis, not a result. Four mechanisms raise it without improving the call set, all of them observed in prior runs on this objective.

**Width inflation.** Post-processing parameters that widen or standardize intervals were the strongest predictor of the composite in prior runs, at ρ ≈ +0.62, and correlated ρ ≈ +0.46 with the reproducibility component. Wider intervals overlap more of everything, so they coincide with the other replicate and with reference regions more often, while single-nucleotide resolution degrades. Reproducibility recomputed at fixed site width exposes this. If gains track site width, they are probably not real.

**Motif hit rate without enrichment.** A hit rate means nothing except against shuffled sequence. One best-scoring prior configuration hit 0.286 at 1.3× enrichment, which is chance. Below roughly 2× enrichment, treat the motif term as noise and do not believe improvements in it.

**Yield standing in for quality.** Site count correlated ρ ≈ +0.82 with reference recall and ρ ≈ −0.40 with reproducibility across prior trials, so a change in the composite can be nothing but movement along that trade-off. In one prior run the composite improved while reference recall fell by a third. Read the decomposed components every time; an aggregate that rises while a component collapses is not an improvement.

**Differences below the metric's resolution.** With a small call set, one site changing state moves the composite more than a typical convergence threshold. Prior runs at small scope yielded 12–22 sites, where one site was worth 0.03–0.06 of composite and the stopping rule triggered on 0.01. Compute what one site is worth at your expected yield before optimizing. If it exceeds the difference you want to detect, raise the yield floor, widen the genomic scope, or accept a coarser question.

## Search in stages; stopping the sampler is not stopping the analysis

Start with a broad sparse sweep over the plausible range, then concentrate on what moved. If that region fails the credibility review or sits on a bound, open the next plausible axis and sweep again. A single TPE run on the first box is stage one, not the procedure.

A flat landscape inside the current box means further trials *in that box* will fit noise. That is a valid reason to stop the sampler and an invalid reason to stop the analysis. Reframe instead: widen bounds that were hit, open axes nobody varied, fix the scoring if it cannot resolve the question, then run another sparse pass. Stop when plausible variations are exhausted.

**A worked case.** One 16-configuration sweep produced a composite spread comparable to chromosome-to-chromosome noise, about 20 sites, and motif enrichment near background. The agent concluded the library was thin and wrote the report. The same data produced a call set roughly three times better after a literature search, comparison with similar proteins, and three ideas the prior cohort had never tried: `min_region_length = 1`, `-antp`, and a correctly scoped reference-region file. The library was thin. That was not what limited the first sweep.

## Reproduce before you believe

Seed the sampler and record the seed; an unreproducible search is not a result. Beyond reproducibility, run the search more than once from different starting points: different sampler seeds, and ideally different genomic subsets. If the runs converge to similar parameter regions, the objective is identifying a well-determined optimum and the answer is trustworthy. If they diverge, that is a finding about the objective, not a nuisance. It means the landscape is flat or noisy at the scale you are searching, and the report should say so instead of presenting whichever run scored highest. Divergence is also the cheapest available evidence that a scope or yield-floor choice was too aggressive.

## Rank with the score, decide with the review

Apply this credibility review to the top candidates after ranking, and keep its checks out of the score. Not all apply to every protein; the test is whether you can say why this call set is credible.

- **Site count** plausible for the protein's known binding breadth, not merely above the yield floor.
- **Width distribution** not pinned at the ceiling post-processing imposes. A spike at the maximum is the width-inflation signature.
- **Score distribution** with an inflection separating confident calls from the bulk. Monotone decay suggests the HMM is not separating its two states.
- **Genomic distribution** matching known biology: 3'UTR enrichment for a 3'UTR-binding regulator, 3' splice site proximity for a splicing factor. Often the most informative single check, and absent from the composite.
- **Motif enrichment** clearing background before the motif component is believed.
- **Stability across seeds and genomic subsets**, as in "Reproduce before you believe".
- **The user's genes and regions of interest** behaving sensibly. Collect them early and keep them out of the score: a single gene that looks wrong to a domain expert can invalidate a run, and scoring against it destroys its value as an independent check.

A lower-scoring configuration that passes review beats a higher-scoring one that fails. Say which you chose and why, and show the decomposed components and diagnostics with every composite.

**The two optima.** The objective has two optima with comparable scores and different biological character: a high-yield regime that recovers most reference regions at weaker per-site sequence support, and a high-confidence regime with fewer sites, better replicate agreement and stronger motif enrichment. The weights decide which one wins, not the protein. When candidates split this way, put the choice to the user: a conservative set of sites they would defend individually, or broad coverage of the regions where the protein acts. Per-protein detail is in `prior-runs.md`.

## Report the search, not only the winner

The search itself is evidence. Beyond the best configuration, report:

- Best-score trajectory against **both** evaluation count and wall-clock time. The two answer different questions: sample efficiency and practical cost. Evaluation count alone hides an expensive search.
- Which parameters the search actually moved, and which it converged on. A parameter the sampler explored widely without score consequence shows the objective is insensitive to it, which is worth stating.
- Where the optimum sits relative to the bounds.
- Agreement or disagreement across seeds.
- The trial records themselves, so a reader can recompute anything.

---
name: pureclip-optimization
description: Tune PureCLIP parameters for protein-RNA crosslink site calling on eCLIP, iCLIP or PAR-CLIP data
---

# PureCLIP parameter optimization

Choose PureCLIP and post-processing parameters for a CLIP dataset, then judge whether the resulting call set is credible. The deliverable is a report a domain expert can review and use for further work: the configuration in a form that re-runs, the call set, the scores that ranked it, and the review that justified it.

CLIP peak calling has no gold standard. Nothing says which nucleotides the protein touched, so "optimal parameters" means parameters whose call set is internally consistent, sequence-plausible, and consistent with what is known about this protein. The composite score ranks configurations. It cannot decide between them, and it rises for changes that make the call set worse. The user decides; you assemble the evidence.

Write to the user in plain English, following ASD-STE100 Simplified Technical English and the EASE guidelines.

## The objective
Composite score over a call set of `n` sites:

```
S = (0.50 · R_rep + 0.25 · R_motif + 0.25 · R_ref) · min(1, n / n_floor)
```

- **`R_rep`, replicate reproducibility.** Fraction of final sites supported by all IP replicates, corrected against position-shuffled intervals that preserve chromosome and count.
- **`R_motif`, motif support.** Fraction of site-centred windows containing a PWM match.
- **`R_ref`, reference recall.** Fraction of known strong binding regions recovered by at least one call.
- **min(1, n / n_floor).** Suppresses configurations that score well on a handful of sites. Default `n_floor = 10`. Raise it when the search cannot resolve the difference you are after.

Keep the default weights unless the user agrees to change them.

### Additional diagnostics
Compute these every trial and report them next to the composite for sanity check. Not the optimization target.
- Motif enrichment over shuffled background, not the hit rate alone
- Site count, and the distribution of site widths
- Reproducibility recomputed at fixed site width, which separates real replicate agreement from agreement bought by wider intervals
- A size-normalized reproducibility or precision-style measure, so yield shifts can be told apart from quality shifts

## Workflow
Copy this checklist and track progress.

```
PureCLIP optimization:
- [ ] Step 1: Understand the data, the protein, and the question
- [ ] Step 2: Run one quick configuration end to end
- [ ] Step 3: Finalize the first sweep scope
- [ ] Step 4: Search until the plausible space is exhausted
- [ ] Step 5: Validate
- [ ] Step 6: Report
```

**Step 1: Understand the data, the protein, and the question**

Look at the files first: which BAMs exist, how many IP replicates, whether a size-matched input control is present, read depth, genome build, and which reference regions and PWMs are available.

Get acquainted with [pureclip-parameters](./references/pureclip-parameters.md). Then research the protein. Use the literature and the open web for binding mode, motif, expected genomic distribution, typical CLIP yield, and homologs. Use [prior-runs.md](./references/prior-runs.md) and [prior-runs.csv](./references/prior-runs.csv) for what similar proteins needed, matching on binding behaviour.

Then ask the user what the files cannot answer: which genes must light up, what the antibody is like, what a previous peak set showed, what they want to conclude, which chromosomes they care about. Before asking anything, check whether you could answer it yourself from the data and whether the answer would change what you do next. If not, do not ask it.

**Step 2: Run one quick configuration end to end**

Run one sensible configuration through the whole pipeline before searching anything. Results do not matter yet. The run is a pipeline check and a first look at how the data behaves. Confirm it produces a non-degenerate call set, that every objective component computes, and that the diagnostics are populated. Check the scoring setup: filters that silently drop sites, reference regions scoped to the wrong genome build or the wrong chromosomes, a yield too low for the composite to resolve anything.

**Step 3: Finalize the first sweep scope**

Set the scope of the first sweep from what you have learned. It need not contain the final parameters, so choose its breadth accordingly: narrower for a well-studied protein with many similar results, broader for an unusual one.

Check your own assumptions before they cost compute. Is the space too narrow or unreasonably large, framed too closely around prior runs, or ignoring what the literature and similar proteins showed? Is any protocol-determined parameter set wrong? Does the scope give enough yield for the score to resolve the difference you are asking about? Does the objective answer the user's question or a different one? Check the plan against scientific and hyperparameter-optimization best practices.

Discuss the scope with the user: the objective and its weights, the parameter space you intend to search, and what one trial costs. Bring a recommendation with your reasoning.

**Step 4: Search until the plausible space is exhausted**

A disappointing first sweep is normal and informative. A second is typically not enough either.

Delegate numeric sweep to a sampler and spend your own effort on the space, the diagnostics and the interpretation; see [optimization.md](./references/optimization.md).

Start with a broad sparse sweep over the full plausible range: the overall bounds from prior runs, the footprint and yield the literature implies, and the axes the prior cohort never varied. Adapt to the incoming information. Explore well-motivated but unusual parameter sets when results stay poor.

- Do not game or hack the metric. Parameters that score well on nonsense always exist, so check at every sweep whether the search is gaming the score rather than finding signal. A worse score with real biological support beats a better one that is a numerical artifact.
- Do not give up early. The space is large and the parameters interact, so poor results usually mean the search has not gone far enough. Use established hyperparameter-tuning practice, and stop only when reasonable parameter sets are exhausted or gains have flattened.
- "The data is the problem" comes last. After several poor sweeps this conclusion becomes tempting, and it is usually wrong: this is a hard optimization problem.

**Step 5: Validate**

Check that the winner generalizes. A configuration tuned on a genomic subset is not a validated production setting, so confirm it on held-out scope before presenting it as one. Re-run the search from different seeds and, where you can, different subsets. Report disagreement rather than the best-scoring run.

Then check that the score was not gamed. Did the gains track site width? Did the composite rise while a component collapsed? Is motif enrichment above background, or is a hit rate carrying a term that means nothing? Were the differences you acted on larger than one site's worth of composite? Finish by applying the credibility review to the top candidates.

**Step 6: Report**

Write for a domain expert who will accept or reject the result, and for whoever re-runs it later. Contents, structure and tone are in [report-format.md](./references/report-format.md).

## References
- [pureclip-parameters.md](./references/pureclip-parameters.md) — steps 1 and 4: what each parameter does to the model, which are determined by the protocol, memory and runtime levers.
- [prior-runs.md](./references/prior-runs.md) — steps 1, 4 and 5: what the curated runs mean, the two optima, per-protein binding behaviour with primary literature. Read it before the CSV; the numbers mislead on their own.
- [prior-runs.csv](./references/prior-runs.csv) — best-known configurations for 14 protein/cell-line pairs, with decomposed scores. Shipped reference material; your own runs belong in your outputs.
- [optimization.md](./references/optimization.md) — steps 3, 4 and 5: the division of labour between you and the sampler, sampler choice, framing the space, budget and stopping rules, seeds, cost control.
- [report-format.md](./references/report-format.md) — step 6: what the report and side notes contain, how they are structured, and how they are written.

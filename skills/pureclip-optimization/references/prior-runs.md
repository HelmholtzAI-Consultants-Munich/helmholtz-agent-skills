# Prior runs — what is known, and how much to trust it

Companion to `prior-runs.csv`. The CSV holds numbers; this file holds the reasons they
are or are not useful. Reading the CSV alone will mislead you.

## Provenance and the size of the grain of salt

Source: a student project (ML4rg group 08, TUM / Helmholtz Munich, July 2026) that ran
an automated optimization loop over PureCLIP and post-processing parameters on 26
registered ENCODE eCLIP datasets, of which 14 protein/cell-line pairs completed. Each
row of the CSV is the best-scoring configuration observed for that pair, recovered from
the project's per-trial records (359 trials total).

What this means for how you use it:

- **Restricted genomic scope, single run per arm.** Every number comes from one
  chromosome and one trajectory. There is no estimate of run-to-run variability, and
  none of these configurations was validated genome-wide. The project's own conclusion
  was that these should not be read as production settings.
- **These are starting points, not targets.** The composite values (0.219–0.547) are
  properties of a particular objective on a particular chromosome. A number here is not
  a bar to clear; if your run scores differently, that is not evidence of anything on
  its own.
- **The parameter names are the students' pipeline's, not PureCLIP's CLI flags.**
  `bandwidth_nt` maps to PureCLIP's KDE bandwidth, `merge_distance_nt` to its region
  merge distance, `use_input_covariate` to supplying a size-matched input control;
  `force_width`, `cluster_gap_width`, `min_region_length_nt`, and `min_crosslink_events`
  are post-processing of raw calls into footprints. Translate to whatever your pipeline
  exposes rather than assuming a flag-for-flag match.
- **Read-only.** This file and the CSV are shipped reference material, curated by
  humans. Runs you perform belong in your own outputs, not here.

## The single most useful finding: two distinct optima

Across the 14 best configurations, two clearly different parameter regimes reached
comparable composite scores:

| | narrow-bandwidth regime | wide-bandwidth regime |
|---|---|---|
| bandwidth | ≈ 20–35 | ≈ 50–98 |
| post-processing width | at or near maximum | mid-range |
| median sites called | ≈ 220 | ≈ 38 |
| median reproducibility | 0.40 | 0.46 |
| median reference recall | 0.43 | 0.15 |
| median motif enrichment | 2.8× | 3.9× |
| input control used | 1 of 4 | 8 of 10 |

The first regime is high-yield: it recovers most known reference regions, at weaker
per-site sequence support. The second is high-confidence: fewer sites, better replicate
agreement and stronger motif enrichment, but it misses most reference regions.

Both are defensible analyses. Which one the objective prefers is decided by its weights
— not by the biology of the protein. This is the clearest case in this whole task where
the score cannot answer the question and the user can: *do you want a conservative set
of sites you would defend individually, or broad coverage of the regions where this
protein acts?* Surfacing that choice is more valuable than any parameter you could pick
on their behalf.

## Example ranges across the 14 best configurations
(not exhausive, so feel free to deviate if makes sense)
- **bandwidth** 20–98, bimodally distributed (see above), median ≈ 67
- **merge distance** 4–16, clustering at 10–12
- **high-precision / stringency mode** on in 8 of 14
- **input control used** in 9 of 14 — and note it co-occurs with the wide-bandwidth,
  high-confidence regime, which is mechanistically sensible: an input control mostly
  removes abundance-driven false positives
- **post-processing width** 7–15
- **cluster gap** 6–15
- **minimum crosslink events** 2–6
- **minimum region length** 3 in every single run — never varied, so this is not
  evidence that 3 is optimal, only that nobody tested otherwise. Parameters the
  cohort never moved are the first unusual ideas to test, not defaults to inherit.

## Two cautions about the parameter–score relationship

**Bandwidth barely moved the score.** Within-dataset correlation between bandwidth and
composite had a median of ρ ≈ −0.01 across the 14 pairs, with wide spread (−0.66 to
+0.52). Bandwidth is the parameter most directly tied to the physics of the crosslink
signal, and the objective is nearly blind to it. Read this as a limitation of the
objective, not a reason to leave bandwidth alone — and as a reason to inspect what
bandwidth does to the *call set* (width, resolution, positional precision) rather than
only what it does to the score. Bandwidth did correlate with yield (ρ ≈ −0.33 with site
count: more smoothing, fewer sites).

**Post-processing width moved it a lot, for the wrong reason.** Median ρ ≈ +0.62 with
composite — the strongest of any parameter — and ρ ≈ +0.46 with the reproducibility
component. See the width-inflation mechanism in SKILL.md. When a sampler on this
objective finds a big improvement, check first whether it simply widened the sites.

## Binding classes, and why the classification disappointed

The project labelled proteins *crisp* (well-defined short motif), *degenerate*
(low-complexity or variable preference), or *positional* (binding determined more by
location in the transcript than by sequence). The labels are in the CSV.

They are useful for one thing: picking a starting region and anticipating whether the
motif component will carry information. A positional binder's sequence motif is a poor
description of what determines its binding, so a PWM-based term should not be expected
to discriminate well — and for such proteins, distance to annotated splice sites or
branch points is the feature that would actually help.

They are not a mechanism to reason from. The project pre-registered a hypothesis that
biological context would help the LLM most for proteins with harder motifs, and **the
predicted relationship did not appear** — the per-protein differences were small,
mixed in direction, and did not order by class. Treat class as a filing convention.

## Per-protein notes

Binding behaviour below is from primary literature (DOIs verified). Regime is which of
the two optima that protein's best configuration landed in.

**PUM1 / PUM2 (K562) — crisp.** PUF-family; recognize a defined UGUA-containing
element, canonically in 3'UTRs, and act on mRNA stability and translation.
PUM2's best run had 6.0× motif enrichment — the motif term is informative here.
PUM1's best run scored well on reproducibility (0.643) at 1.3× motif enrichment, which
is background: that configuration's motif component should not be believed.
Both landed in the wide-bandwidth regime. Galgano et al. 2008,
doi:10.1371/journal.pone.0003164.

**QKI (K562, HepG2) — crisp.** STAR-family KH-domain protein; binds a bipartite
element — core ACUAAY plus a nearby UAAY half-site — and regulates splicing, with the
positional rule that binding upstream versus downstream of an exon flips repression to
activation. Highest motif enrichment in the whole set (11.0× for K562), so the motif
component is trustworthy here. The K562 run is the low-yield case: 22 sites, and the
only pair where the LLM arm beat TPE. Galarneau & Richard 2005, doi:10.1038/nsmb963.

**RBFOX2 (HepG2, K562) — crisp.** Single RRM with strong specificity for (U)GCAUG,
typically in introns flanking regulated exons; crosslinks concentrate sharply within the
motif. Both runs landed firmly in the narrow-bandwidth high-yield regime — HepG2 gave
the largest call set (644 sites) and the highest reference recall (0.90) in the set, at
a motif hit rate of only 0.163. That combination is exactly the high-yield trade-off,
and a clean illustration of why the aggregate score needs its components. Note also
that RBFOX2 is recruited to some sites indirectly via protein partners, without its
canonical motif, which caps how high a motif hit rate can legitimately go.
Auweter et al. / Jangi et al. 2014, doi:10.1101/gad.235770.113.

**HNRNPK (K562, HepG2) — degenerate.** Triple KH-domain protein preferring C-rich but
variable sequence. Motif enrichment in the best runs was 4.0× (K562) and 1.6× (HepG2) —
so the motif term is marginal-to-useless depending on dataset. The K562 best run
recovered zero reference regions while scoring 0.583 on reproducibility: a stark case of
a composite that looks acceptable while one component has collapsed. Thisted et al.
2001, doi:10.1074/jbc.M010594200.

**SRSF1 (K562, HepG2) — degenerate.** SR-family splicing factor with two RRMs binding
purine-rich exonic splicing enhancers; the reported consensus varies substantially
between SELEX, CLIP, and structural studies (GA-rich, GGAGA, UGRWG have all been
reported), which is the practical meaning of "degenerate" — PWM choice matters more than
usual and catalog quality limits the motif term. Best runs show high motif enrichment
(8–10×) at very low hit rate (0.07–0.21): a small subset of sites carries strong
sequence signal while most do not. Both pairs scored lowest or near-lowest overall.
Cléry et al. 2013, doi:10.1073/pnas.1303445110.

**U2AF2 (K562, HepG2) — positional.** Binds polypyrimidine tracts at 3' splice sites;
what determines binding is position relative to the splice site, not a sequence motif
in isolation. The K562 run is the highest-scoring in the entire set (0.547: 180 sites,
0.461 reproducibility, 0.750 reference recall) — the one case where the objective's
components agree with each other. HepG2, on identical parameters as SRSF1_K562, gave
only 15 sites. For proteins like this, a splice-site-distance feature would be more
informative than a PWM. Sickmier et al. 2006, doi:10.1016/j.molcel.2006.05.025.

**SF3B4 (K562, HepG2) — positional.** SAP49; core U2 snRNP / SF3b subunit that
crosslinks to pre-mRNA just upstream of the branch point and stabilizes U2 binding
there. Binding is anchored by spliceosome assembly, and the upstream contact is
substantially sequence-independent — so a motif-based term is structurally
ill-suited, and the moderate hit rates (0.19–0.23) should be read in that light.
Both runs reached respectable composites (0.40–0.46) largely through reference recall.
Champion-Arnaud & Reed 1994, doi:10.1101/gad.8.16.1974.

## What the optimizer comparison actually showed

Worth knowing because it should shape how you allocate effort. In 12 head-to-head pairs
with a shared pipeline, objective, and bounds:

- TPE reached the higher score in 10 of 12 pairs.
- Automated search beat the shared default configuration in 9 of 12 (LLM arm) and 11 of
  12 (TPE arm) — so tuning is worth doing; the largest single gain was +0.220.
- Supplying RBP-specific biological context to the LLM was worth mean +0.004, median
  −0.002, across 6 datasets with both conditions. Effectively zero.
- **The comparison was not budget-matched** (TPE used 14–16 evaluations, the LLM 5–9),
  so it does not establish that TPE is intrinsically the better optimizer. What it does
  establish is that an LLM proposing parameter values is not a better use of the budget,
  and that biological context injected as a prior into parameter proposal did not pay
  off. Context is worth far more in framing the space and judging the output — where
  that study could not measure it.

Source: `ML4rg_project_report_group08` and its per-trial records.

# Prior runs

`prior-runs.csv` holds the best-scoring configuration for each of 14 protein/cell-line pairs, from one student cohort (ML4rg group 08, TUM / Helmholtz Munich, July 2026): 26 registered ENCODE eCLIP datasets, 14 pairs completed, 359 trials, all on chr21, one run per arm. The CSV is authoritative on every number. This file says how to use it.

Treat the CSV as a seed, not a recommendation. Every row is one trajectory on one small chromosome, with no estimate of run-to-run variability, so any single-row number is N=1. The 14 rows contain 12 distinct configurations; two of those configurations each appear twice. Per-pair search effort ranged from 16 to 53 trials, so composites are not comparable across rows. Several bests sit at the edge of the range that was searched, so those values mark a bound, not a fitted optimum. Use the table to seed a search space and to find proteins with similar binding behaviour.

## Binding mechanism, and what it implies for the objective

Match analogues on the mechanism below rather than on name. These facts apply to proteins that are not in the CSV.

- **Sequence-specified binders.** PUM1 and PUM2 are PUF-family, recognising a defined UGUA-containing element canonically in 3'UTRs, acting on mRNA stability and translation (doi:10.1371/journal.pone.0003164). RBFOX2 has a single RRM with strong specificity for (U)GCAUG, typically in introns flanking regulated exons, with crosslinks concentrated sharply within the motif (doi:10.1101/gad.235770.113). QKI is STAR-family, binding a bipartite element of core ACUAAY plus a nearby UAAY half-site, with the positional rule that binding upstream versus downstream of an exon flips repression to activation (doi:10.1038/nsmb963). For these the motif term is informative if the catalogue is good.
- **Position-specified binders.** U2AF2 binds polypyrimidine tracts at 3' splice sites, where position relative to the splice site rather than sequence determines binding (doi:10.1016/j.molcel.2006.05.025). SF3B4, also called SAP49, is a core U2 snRNP and SF3b subunit that crosslinks just upstream of the branch point and stabilises U2 binding there, a contact that is substantially sequence-independent (doi:10.1101/gad.8.16.1974). For these the motif term is a poor fit; use distance to the annotated feature instead.
- **Degenerate specificity.** HNRNPK is a triple KH-domain protein preferring C-rich but variable sequence (doi:10.1074/jbc.M010594200). SRSF1 is SR-family with two RRMs binding purine-rich exonic splicing enhancers, and its reported consensus varies substantially between SELEX, CLIP and structural studies, with GA-rich, GGAGA and UGRWG all reported (doi:10.1073/pnas.1303445110). Here PWM choice limits the motif term as much as the data does, so report which PWM you used.
- **Indirect recruitment.** RBFOX2 is recruited to some sites through protein partners, without its canonical motif. If a protein works in complexes as well as by its own motif, a motif hit rate below 1 is expected and is not a sign that parameters failed.
- **Expected genomic distribution.** 3'UTRs for PUF-family, introns flanking regulated exons for RBFOX2, 3' splice sites for U2AF2, branch points for SF3B4. This check is not in the composite, so it is independent evidence.
- **Binding class labels.** The CSV labels each protein crisp, degenerate or positional. The cohort pre-registered a hypothesis that biological context would help most for proteins with harder motifs. The predicted relationship did not appear: differences were small, mixed in direction, and not ordered by class. Use the label to pick a starting region, not as a predictor of how the search will go.

## What the cohort showed about the objective

These claims are about the metric and the search, not about biology.

- **Search beat the default.** Automated search beat the shared default configuration in 9 of 12 pairs for the LLM arm and 11 of 12 for the TPE arm, with a largest single gain of +0.220.
- **Bandwidth is nearly invisible to the composite.** Within-dataset correlation with the composite had a median of ρ ≈ −0.01 across the 14 pairs, spread −0.66 to +0.52. It correlated ρ ≈ −0.33 with site count, so more smoothing gave fewer sites. That is a limitation of the objective; judge bandwidth on the call set.
- **Post-processing width dominates the composite.** Median ρ ≈ +0.62, the strongest of any parameter, and ρ ≈ +0.46 with the reproducibility component. Mechanism in `optimization.md`.
- **Yield trades against per-site quality.** Across the 359 trials, site count correlated ρ ≈ +0.82 with reference recall and ρ ≈ −0.40 with reproducibility. Coverage versus confidence is a user choice. This trade-off is better supported than any pattern among the 14 best configurations.
- **The optimizer comparison was not budget-matched.** TPE reached the higher score in 10 of 12 pairs, using 14–16 evaluations against the LLM arm's 5–9. Supplying RBP-specific biological context to the LLM was worth mean +0.004 and median −0.002 across the 6 datasets run both ways.

## Reading the CSV

Read-only, curated by humans. Your own runs belong in your outputs.

The parameter columns carry the cohort's pipeline names, not PureCLIP flags. `bandwidth_nt` is the KDE bandwidth, `merge_distance_nt` the region merge distance, `use_input_covariate` whether a size-matched input control was supplied, and `high_precision_mode` a stringency setting. `force_width`, `cluster_gap_width`, `min_region_length_nt` and `min_crosslink_events` are post-processing of raw calls into footprints and have no PureCLIP flag at all. Translate rather than assuming a flag-for-flag match.

`proposer` records which arm produced that row's best configuration, where `llm_noprior` is the LLM arm run without biological context. `scope`, `source` and `caveats` are constant across all rows; there is no row-specific caveat. `min_region_length_nt` is 3 in every row and was never varied, so the CSV carries no information about it. `QKI_HepG2` and `RBFOX2_K562` have no ENCODE accessions; the other twelve rows let you fetch the same data.

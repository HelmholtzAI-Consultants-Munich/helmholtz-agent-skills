# Reporting the result

## Contents

- Structure
- Tone
- Alignment with the goal

Two files. `report.md` carries the recommendation and the evidence that decides it.
`side_notes.md` carries everything you checked that did not change the recommendation:
provenance, runs completed, controls, ruled-out explanations, incidental observations.

The split is the discipline. If a paragraph does not bear on the recommendation, it
belongs in the side notes. A report that includes everything you checked buries the
finding among the checks.

## Structure

Lead with the answer, then the evidence for it, then what would change it. A reader who
stops after the first paragraph should already know what you recommend and how good it
is.

A working order, to adapt rather than follow exactly:

1. **Summary.** What was selected, from how many trials, and the headline numbers of the
   call set it produces. State the main caveat here as well, not only at the end.
2. **Recommended configuration.** The full command or config, in a form that re-runs.
   The post-processing applied to its output. A table of the call set's metrics: the
   composite with every component and every diagnostic decomposed, never the aggregate
   alone. What was held fixed rather than searched, and why.
3. **What sets the operating point.** Usually one or two parameters dominate the
   trade-off. Show it across their range so the reader can choose a different point,
   and say which point you chose and on what evidence.
4. **Properties of the call set.** Genomic distribution, the width and score
   distributions, and the motifs recovered with their enrichment over background. This
   is the credibility review, written out.
5. **Whether the limit is the parameters or the data.** Only when the result
   disappoints. Independent lines of evidence, each one a measurement.
6. **What was searched.** Literature and analogues consulted, the axes opened at each
   stage, the trajectory against evaluation count and wall-clock time, and why the search
   stopped.
7. **Limitations and open questions.** Scope limits, generalization not confirmed,
   components that could not be computed, seeds that disagreed, checks that failed.

Everything the report asserts must be reachable: name the file holding the numbers behind
each table and figure, ship the call set and the processed outputs a reader would want
downstream, and ship the configuration itself.

## Tone

- Lead each section with its conclusion, then support it.
- Give numbers with their uncertainty. An enrichment resting on four sites is a different
  claim from one resting on four hundred, so say which it is.
- Let numbers carry the weight adjectives would otherwise carry. "5.9-fold enrichment",
  not "strong enrichment".
- Report what you did, not what you attempted.
- Do not hedge a conclusion you have evidence for, and do not assert one you do not.
- Plain English, one idea per sentence. Plain words for plain things: "no sites were
  reproducible across replicates", not "the reproducibility component failed to resolve".
- Use a table wherever more than two comparable values appear.
- Keep the argument in the report and the audit trail in the side notes.

## Alignment with the goal

The report answers the user's question, not the optimizer's. If they asked whether this
call set can support a downstream analysis, say whether it can.

- Say which of the two regimes the recommendation sits in, and why that regime suits
  their question.
- Where the objective could not separate two candidates, present the choice instead of
  hiding it behind a rank. Give the reader what each option costs.
- Put the genes and regions they named in the report, with what the call set does at
  each.
- State every check that failed or could not be performed. Omitting them is what makes a
  result over-trusted.
- Write so the recommendation can be rejected. A domain expert needs enough to disagree
  with you on specifics, not only to accept the summary.

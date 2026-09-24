# Reporting the result

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

You have good attention to detail, but tend to pack secondary nuances, caveats, examples, alternatives, and exploratory observations into the main document, which hurts readability and obscures the important parts. So split into two documents: `report_<protein>.md` carries the core information; `side_notes_<protein>.md` carries secondary details.

TODO: add the Methods section where for all reported metrics and values the formulas and approaches are explicitly described and stated.

## Writing Style
- Documents also often arise via an iterative process and become a frankenstein monster of patchwork, references to previous version and outdated or wrong assumptions. This can become very distracting and confusing. => Please make sure the document is a standalone, final, coherent text.
- You tend to make prose heavier than necessary through rhetorical emphasis, repeated conclusions, unnecessary qualification, parenthetical content, dramatic phrasing, cumbersome asides, and overly assertive language. => Keep the writing direct, precise, compact, scientific, and easy to follow. Remove unnecessary verbosity, repetition, rhetorical emphasis, editorializing, redundant explanation, and cumbersome asides. 
- Plain English, one idea per sentence. Plain words for plain things: "no sites were reproducible across replicates", not "the reproducibility component failed to resolve". Use ASD-STE100 Simplified Technical English and the EASE standards.
- Adhere to high scientific standards and make the argumentantion clear, don't overstate conclusions, include provenance, use excplicit values, use graphs to improve clarity (if needed), etc. After drafting, do a second review pass like a professional peer-reviewer would.

## Alignment with the goal

The report answers the user's question, not the optimizer's.
- Say where the recommendation sits on the coverage-versus-confidence trade-off, and
  why that suits their question.
- Where the objective could not separate two candidates, present the choice instead of
  hiding it behind a rank. Give the reader what each option costs.
- Put the genes and regions they named in the report, with what the call set does at
  each.
- State every check that failed or could not be performed. Omitting them is what makes a
  result over-trusted.
- Write so the recommendation can be rejected. A domain expert needs enough to disagree
  with you on specifics, not only to accept the summary.

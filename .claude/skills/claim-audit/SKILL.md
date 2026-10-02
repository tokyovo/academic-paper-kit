---
name: claim-audit
description: Audit every quantitative claim in the manuscript against the result files, and every citation against the bibliography. Use before a submission, before a camera-ready, or when the user asks whether the paper's numbers and sources hold up.
---

# Claim audit

Produce a table of mismatches. Do not fix anything until the user has seen it.

## Steps

1. **Numbers.** Extract every numeric claim from `paper/sections/*.tex`. For
   each one, find the value in `experiments/results/*.json`. Report:

   | Claim | File:line | Value in text | Value in results | Match? |

   Flag any number that appears in the text but in no result file. That is
   either a typed number, which the rules forbid, or a missing experiment.

2. **Tables and figures.** Confirm each `\input{tables/...}` and
   `\includegraphics` target exists and was regenerated after the last change
   to `experiments/results/`. Compare file times.

3. **Citations.** Run `make check-refs`. For every failure, look up the correct
   record with `make find-refs` and report the correction. Do not silently
   rewrite an entry.

4. **Cite keys.** Run `make scrub`. Every `\cite` key must exist in
   `refs.bib`.

5. **Ledger.** Run `make ledger`. Report claims with no evidence file.

6. **Overclaiming.** List every sentence with a superlative or a general claim
   that has no citation and no result file behind it.

## Output

One table per check, then a short list of what the user must decide. End with
the single most serious problem found, stated plainly. If everything passes,
say so without padding.

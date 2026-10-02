# Claim ledger

One row per claim the paper makes. A claim with no evidence file is a claim
you cannot defend in review.

Fill the columns like this:

- **Claim** — the assertion as it appears in the text, short.

- **Section** — the file it appears in, for example `paper/sections/05_results.tex`.

- **Evidence** — a path. A result file, a figure script, or `sources/<file>.pdf p.4`
  for a claim taken from the literature. A comparison lists each file it
  compares: `a.json; b.json`. `external` is allowed only with a
  cited key.

- **Status** — `verified`, `pending`, or `cut`.

Run `make ledger` to list rows whose evidence path does not exist.

| Claim | Section | Evidence | Status |
| --- | --- | --- | --- |
| Example: the baseline reaches 0.812 accuracy on example-v1 | paper/sections/05_results.tex | experiments/results/example_run.json | verified |

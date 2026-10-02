# The multi-agent workflow

The `paper-pipeline` skill runs a paper with parallel agents. This page
explains the design. It was built and tested on a trial paper on fake news
detection (October 2026); the lessons from that run are at the end.

## The idea in one line

Many agents may search, read and check at the same time. One agent owns each
file. A script checks every handoff. The human decides every claim.

## The flow

```
 H1 scope ─▶ search ─▶ H2 screening ─▶ add refs + PDFs ─▶ read (1 agent per PDF) ─┐
 (human)     (lead)    (human)          check-refs, pdfs    check-extractions       │
                                                                                     ▼
 H5 submit ◀─ H4 human parts ◀─ integration ◀─ audit ◀─ merge ◀─ draft (1 agent per ◀─ H3 outline ◀─ experiments
 make check   title, abstract,   pass (one       (fresh   make     section group)       (human)        check-results,
              contributions      agent reads     agent)   paper    check-evidence,                     make tables
                                 it all)                           scrub --draft, ledger
```

`H1` to `H5` are human gates. A Claude Code subagent cannot ask the human a
question, and a workflow cannot wait for an answer in the middle of a run.
So the lead stops at each gate, and the next stage starts after the human
answers.

## Who owns which file

| File | Written by | Checked by |
|---|---|---|
| `notes/scope.md` | human | (gate H1) |
| `notes/screening.tsv` | lead; human sets `approved` | (gate H2) |
| `paper/refs.bib` | lead only, through `find_refs.py --append` | `make check-refs` |
| `sources/<key>.pdf` | `make pdfs`, or the human | `fetch_pdfs.py` title check |
| `notes/extractions/<key>.md` | one `paper-reader` per key | `make check-extractions` |
| `notes/outline.md` | lead; human approves | (gate H3) |
| `experiments/results/<run>.json` | the experiment script | `make check-results` |
| `paper/tables/*` | `make tables` only | generated |
| `paper/sections/<file>.tex` | one `paper-writer` per file | `make check-evidence`, `make scrub` |
| `notes/claims/<name>.md` | the writer that owns it | `make ledger` |
| `notes/audit.md` | `paper-auditor` | advisory |
| `ai_use_log.md`, `main.tex`, `notes/claim_ledger.md` | lead only | `make check` |

No file has two writers at the same time. That is the whole concurrency
model: there are no locks, so ownership must be disjoint.

## What each check proves

| Check | Proves | Does not prove |
|---|---|---|
| `check-refs` | each entry is a real paper; title, authors and year agree with Crossref, DataCite/arXiv or OpenAlex | that the paper says what you cite it for |
| `fetch_pdfs.py` | the PDF shows the entry's title | that the PDF is the final version |
| `check-extractions` | each quote in the notes is on its page | that the fact matches the quote |
| `check-evidence` | each cited sentence has a quote that is on its page | that the quote supports the sentence |
| `check-results` | each result names a real commit, seed, data and environment | that the experiment is correct |
| `scrub` | no model text, placeholders, unknown keys or hand-typed numbers | that the prose is good |
| auditor | its judgement on support and wording | anything for certain |

The right column is why the auditor and the human are still needed.

## Lessons from the trial paper

These came from running the workflow end to end, and each one changed the kit.

- **Public APIs fail.** arXiv answered 429 or timed out for long periods.
  Lookups now retry, and arXiv entries are checked through DataCite, which
  registers every arXiv DOI and does not rate-limit the same way.
- **Title search misses acronym titles.** OpenAlex stores "dEFEND" with no
  subtitle, so its title search returns nothing. Crossref's search finds it.
- **Reader agents were reliable when a script checked them.** 12 readers
  wrote 120 quoted facts. One file was cut short by a shell heredoc and the
  checker caught it. Readers also reported problems in the sources, such as
  a paper that states two accuracy figures with the platforms swapped.
- **A writer used an unstored check as evidence.** It reran a model with
  other seeds in memory and wrote the result into the paper. The lead stored
  the runs as result files. The writer prompt now says a check run in memory
  is not evidence.
- **A checker had a bug that a writer found.** `check-evidence` cut lines
  at an escaped `\%`, so 5 of 56 cited sentences were never checked.
- **The gate passed an empty template.** The title "Working title: replace
  this", "Your Name" and empty sections all passed `scrub`. They now block,
  and CI uses `scrub --draft` so a draft in progress can still pass CI.
- **The auditor found what no script could, at the joins.** With every
  check green, it still found 1 unsupported and 3 overstated citations,
  and one contradiction between the two writers (label balance). Each
  half was clean; the problems were where they meet. So the pipeline now
  has an integration pass by one agent after the audit.
- **Comparison claims need both runs as evidence.** A ledger row may list
  several paths: `a.json; b.json`. `make ledger` checks each.
- **Parallel writers need a lead to merge.** The results writer could not
  cite, so it left `\todo{CITE}` for the dataset; the lead resolved it.
  Neither writer could write the AI-use log; the lead did.

## Cost and limits

- Each parallel agent reads its own context, so the token cost grows with
  the number of agents. Reading 12 papers took 12 agents of about 50 to 60
  thousand tokens each.
- Two LaTeX builds in one folder overwrite each other's files, so writers
  do not run `make paper`; the lead does.
- The checks prove that quotes exist, not that they support a claim. Only
  the auditor and the human judge that.

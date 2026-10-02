---
name: paper-pipeline
description: Run the whole paper with parallel agents - search, screening, one reader agent per PDF, experiments, parallel section writers, an independent audit, and the submission gate - with a deterministic check at every handoff and the human gates in between. Use when the user wants to take a paper from topic to submission-ready draft, or to rerun one stage of it.
---

# Paper pipeline

You are the lead. You run the stages, spawn the agents, own every shared
file, and stop at each human gate. The full rationale is in
`docs/agent-workflow.md`.

## Rules for the lead

- Only the lead writes shared files: `paper/refs.bib`, `paper/main.tex`,
  `notes/screening.tsv`, `notes/claim_ledger.md`, `ai_use_log.md`.
- Agents in parallel must own disjoint files. Never give two agents the
  same file.
- After each stage, run its check yourself. Do not trust an agent's report
  that its check passed.
- At a human gate, stop and ask. Do not continue on a guess. A subagent
  cannot ask the human, so every gate is a point where you, the lead, ask.
- Append one row to `ai_use_log.md` per stage.

## Stages

| # | Stage | Who | Parallel? | Check (must pass) |
|---|---|---|---|---|
| 1 | Scope: question, field terms, claims to test | human | no | gate H1 |
| 2 | Search | lead (find_refs) | queries, yes | candidates shown with authors, venue, DOI |
| 3 | Screening | human | no | gate H2: `notes/screening.tsv` status `approved` |
| 4 | Add references, fetch PDFs | lead | no | `make check-refs`, `make pdfs` (0 WRONG) |
| 5 | Read | `paper-reader`, one per PDF | yes | `make check-extractions` |
| 6 | Outline and contribution | lead drafts, human approves | no | gate H3: `notes/outline.md` approved |
| 7 | Experiments | lead | runs, yes | `make check-results`, `make tables` |
| 8 | Draft | `paper-writer`, one per section group | yes | `make check-evidence`, `scrub --draft`, `make ledger` |
| 9 | Merge | lead | no | `make paper` (0 undefined), cross-writer `\todo`s resolved |
| 10 | Audit | `paper-auditor` | no | advisory: `notes/audit.md`; lead fixes, human reviews |
| 11 | Human parts | human | no | gate H4: title, abstract, contributions, conclusion |
| 12 | Submit | lead + `pre-submission` skill | no | gate H5: `make check` clean |

## Stage notes

**2. Search.** Run `python3 tools/find_refs.py "<phrase>"` for each theme.
Title search uses OpenAlex, then Crossref when OpenAlex finds nothing
(acronym titles such as "dEFEND"). Look up each shortlisted paper by DOI or
`arXiv:<id>` so the human sees authors and venue. Add nothing yet.

**3. Screening.** Write `notes/screening.tsv` (key, group, status, note)
with status `agent-proposed`. The human changes it to `approved` or `cut`.
A citation means the human has read the paper.

**4. Add.** `python3 tools/find_refs.py <doi> --append` for each approved
paper, then `make check-refs` and `make pdfs`. List the papers with no
open-access PDF: the human adds them, or they are not drafted from.

**5. Read.** Spawn one `paper-reader` per PDF in a single message, so they
run at the same time. Prompt: "Your paper: bibkey `<key>`." Then run
`make check-extractions` yourself.

**7. Experiments.** Commit the code before each run: the run records the
commit, and `make check-results` fails a commit that is not in the repo. A
claim needs a stored result file; a check run in memory is not evidence.

**8. Draft.** Spawn the writers in one message. Give each its files and its
ledger file `notes/claims/<name>.md`. A good split: one writer for related
work, one for method, setup, results and discussion. Connected text by one
writer stays consistent; do not split one section between writers.

**9. Merge.** Run `make tables` and `make paper`. Resolve the `\todo`s a
writer could not (for example a citation in a section whose writer did not
own citations). Remove the template example result and its ledger row once
real runs exist. Commit.

**10. Audit.** Spawn one `paper-auditor`. Fix OVERSTATED and UNSUPPORTED
sentences and wording that does not fit the numbers. Show the human the
rest of `notes/audit.md`.

**12. Submit.** `make check` must pass with no `--draft`. Then use the
`pre-submission` skill for the venue's disclosure.

## Updating the kit inside a paper

A paper repo is a clone of the kit with its own commits. To take kit fixes:
`git pull --no-rebase` from the kit (a plain `git pull` stops on the
diverged history).

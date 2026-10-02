# How to use this repo

The idea is simple: the paper is a codebase. Every claim, number and citation
traces back to a file in the repository. The agent does the writing; the
repository makes unverified work fail a check.

## One-time setup

```
git clone <your fork> my-paper && cd my-paper
```

No dependencies to install. The tools use only the Python standard library.
`matplotlib` is optional, for figures. A LaTeX distribution with `latexmk` is
needed only for `make paper`.

Then:

1. Replace the preamble in `paper/main.tex` with your venue's style file.

2. Put your subject in the title and the abstract. Write the abstract yourself.

3. Delete `experiments/results/example_run.json` once you have a real run.

## The loop

| Stage | What you do | What the agent does | What checks it |
| --- | --- | --- | --- |
| Find sources | Approve candidates; put PDFs in `sources/` | `find-literature` skill; `make find-refs` | `make check-refs` |
| Related work | Spot-check the claims against the PDFs | `related-work` skill | `make scrub` |
| Experiments | Decide what to run | Writes and runs the code in `experiments/` | Seeds and commit hash in each result file |
| Numbers | Nothing by hand | `analysis/make_tables.py` | `make tables` |
| Body text | Own the contribution claims and abstract | `draft-section` skill | `make paper`, `make scrub` |
| Audit | Read the mismatch table | `claim-audit` skill | `make ledger` |
| Reviews | Decide tone and concessions | `reviewer-response` skill | `latexdiff` |
| Submit | Approve the disclosure | `pre-submission` skill | `make check` |

## Why these rules

Hallucinated citations are now the main way papers get desk-rejected. In
January 2026 GPTZero confirmed 100 fake citations across 51 accepted NeurIPS
2025 papers, all of which had passed three or more reviewers. ACL 2026
desk-rejected over 100 already-accepted papers at camera-ready. arXiv imposes
a one-year ban when a submission shows clear evidence that the authors did not
check their generated output.

Across 13 models asked to cite from memory, hallucination rates ran from 14%
to 95%, and models checking their own citations were right only about 38% of
the time. Retrieval-grounded pipelines cut the rate by roughly ten times. That
is why `refs.bib` may only be filled by lookup, never by recall.

## Which agent to use

Any of them. The rules live in `CLAUDE.md`, with `AGENTS.md` and `GEMINI.md`
as symlinks to the same file, so Claude Code, Codex CLI and Gemini CLI all
read the same contract. The skills in `.claude/skills/` are plain Markdown in
the portable SKILL.md format, so Codex reads them too.

Practical split, if you use more than one: Claude Code for drafting and
revision, Codex CLI for experiment code, Gemini CLI for whole-manuscript
consistency passes over a long draft.

## What this repo does not do

It does not write papers unsupervised. Fully automatic systems can produce
workshop-grade work, but at Agents4Science 2025 fully AI-driven papers were
23.3% of submissions and only 14.9% of acceptances, and the accepted ones had
more human input. The hypothesis, the contribution claims, the abstract and
the conclusions stay human.

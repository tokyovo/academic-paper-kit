# academic-paper-kit

A repository scaffold for writing an academic paper with a coding agent, on
any subject, without fabricating a single citation.

Clone it per paper. The agent does the drafting. The repository makes
unverified work fail a check.

## Why

Writing quality is no longer what stops AI-assisted papers. Verification is.
Venues now extract every reference from a submission and look it up in a
database, so a made-up citation is caught by machine:

- GPTZero confirmed 100 hallucinated citations across 51 accepted NeurIPS 2025
  papers in January 2026. All had passed three or more reviewers.

- ACL 2026 desk-rejected over 100 already-accepted papers at camera-ready for
  citations to literature that does not exist.

- arXiv has banned authors for one year since 14 May 2026 when a submission
  shows clear evidence that generated output was never checked.

Asked to cite from memory, 13 tested models produced bad references between
14% and 95% of the time, and they verified their own citations correctly only
about 38% of the time. So this repo never lets a reference come from a model's
memory. Every entry in `paper/refs.bib` must come from a real lookup, and
`make check-refs` proves it.

## What is in here

```
CLAUDE.md               the rules the agent must follow (AGENTS.md and
                        GEMINI.md are symlinks to it)
.claude/skills/         seven skills: paper-pipeline (the whole paper with
                        parallel agents), find-literature, related-work,
                        draft-section, claim-audit, reviewer-response,
                        pre-submission
.claude/agents/         paper-reader, paper-writer, paper-auditor: the agents
                        paper-pipeline runs in parallel
paper/                  main.tex, sections/, refs.bib, generated tables and figures
sources/                the PDFs you cite; an agent may only draft from these
experiments/            configs, code, and result JSON with seed and commit hash
analysis/               make_tables.py and make_figures.py: results -> paper
notes/                  claim_ledger.md and claims/ (claim -> evidence ->
                        section), extractions/ (quoted notes per PDF)
tools/                  find_refs.py, check_refs.py, fetch_pdfs.py, scrub.py,
                        check_extractions.py, check_evidence.py,
                        check_results.py, check_ledger.py
docs/                   workflow.md (the loop), agent-workflow.md (the
                        parallel-agent design), venues.md (disclosure rules
                        per venue), tools.md (other open-source tools),
                        field-review.md (the research notes behind the rules)
ai_use_log.md           what you disclose at submission
Makefile                make check is the pre-submission gate
```

## Start

```
git clone https://github.com/tokyovo/academic-paper-kit my-paper
cd my-paper
make help
```

No dependencies. The tools use the Python standard library only.
`matplotlib` is optional, for figures. `latexmk` is needed only to build the
PDF.

Then open the repo with Claude Code, Codex CLI or Gemini CLI and say what the
paper is about. The agent reads `CLAUDE.md` and works under its rules.

## The commands that matter

```
make find-refs Q=10.1145/3442188.3445922   # add a real reference by DOI
make find-refs Q="attention is all you need"   # or by title
make check-refs      # verify every entry against Crossref, arXiv, OpenAlex
make scrub           # leftover AI text, placeholders, unknown cite keys
make pdfs            # download open-access PDFs into sources/
make check-extractions   # every quote in notes/extractions/ is in its PDF
make check-evidence  # every cited sentence has a quote that is in its PDF
make tables          # results JSON -> LaTeX tables and result macros
make check-results   # every result names a real commit, seed, data, environment
make ledger          # claims with no evidence file
make check           # the whole gate, before you submit
make test            # prove the checkers work on deliberately bad fixtures
```

`make test` runs two fixtures: a bib file with two real and two fabricated
references plus one real title with invented authors, and a `.tex` file full
of the text models leave behind. Both are
expected to fail, which is how you know the checkers work.

## The rules, in short

1. Cite only what is in `refs.bib`, and `refs.bib` is filled only by lookup.
   A missing source becomes `\todo{CITE: ...}`, never a guess.

2. Every number in the text is generated from `experiments/results/*.json`.
   Nothing is typed by hand. No figure is drawn from a description.

3. Every claim goes in the claim ledger with the file that proves it.

4. The human owns the hypothesis, the contribution claims, the abstract and
   the conclusions.

5. `make check` must pass before submission, and the AI use log becomes the
   disclosure the venue asks for.

## Any subject

Nothing here is specific to a field. Reference lookup goes through Crossref,
arXiv and OpenAlex, which cover every discipline, and the skills ask you for
your field's vocabulary rather than assuming it. Only `paper/main.tex` needs
changing: swap the preamble for your venue's style file.

## What this is not

It is not an autonomous paper generator. Those exist, and at Agents4Science
2025 fully AI-driven papers were 23.3% of submissions but only 14.9% of
acceptances. Supervised beats autonomous, and this repo is built for
supervised.

## Where to read more

- `docs/workflow.md` — the stage-by-stage loop, and who checks what.

- `docs/agent-workflow.md` — the same loop with parallel agents: who owns
  which file, what each check proves, and the lessons from a trial paper.

- `docs/venues.md` — what each publisher and conference requires.

- `docs/tools.md` — the other open-source tools: Zotero MCP, PaperQA2, STORM,
  the reference checkers, the agent skill bundles, the autonomous systems.

- `docs/field-review.md` — the October 2026 research notes the rules come
  from: the five hallucination studies, the enforcement record, how good
  autonomous systems actually are, and the caveats.

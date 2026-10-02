# Open-source tools worth knowing

Reference notes, current as of October 2026. This repo does not depend on any
of them: it uses the Python standard library and public bibliographic APIs. Add
whichever of these fit your field.

Star counts are approximate snapshots and change quickly. Licenses marked
"see repo" were not individually verified — check before institutional or
commercial use, especially Sakana's custom license.

## Grounded retrieval (the ones that matter most)

| Tool | What it does | License | Strengths | Limitations |
| --- | --- | --- | --- | --- |
| **Zotero MCP** (`54yyyu/zotero-mcp`) | MCP server and CLI: search your library by title, author, tag, full text or meaning; read and annotate PDFs; add items. `install-skill` teaches Claude Code, Codex, Gemini CLI and Cursor to use it | MIT | Grounds citations in a library you verified; local mode keeps data private | Needs Zotero 7 local API and a Python stack; the semantic index needs maintenance |
| `cookjohn/zotero-mcp` | A Zotero plugin with MCP built in, read and write from inside Zotero | MIT | No external server | Smaller community |
| **PaperQA2** (`Future-House/paper-qa`) | High-accuracy RAG over your own PDFs, Office docs and source code, with cited answers and contradiction detection; benchmarked as superhuman on LitQA2 | Apache-2.0 | Best-in-class grounded answers over your own corpus | The open-source version omits some components from the paper, such as Grobid parsing and citation traversal |
| **GPT Researcher** (`assafelovic/gpt-researcher`) | Plans queries, crawls web or local docs, compiles a cited report | Apache-2.0 | Quick background dossiers | General web research, not scholarly-grade citation control |
| **STORM / Co-STORM** (`stanford-oval/storm`) | Multi-perspective questioning plus retrieval, then an outline, then a Wikipedia-style cited article. Co-STORM adds human–agent discussion | MIT | Good for background and related-work scaffolding | Produces encyclopedia prose, not papers; web sources need vetting |

## Reference verification

| Tool | What it does | Note |
| --- | --- | --- |
| **Halref** (`davidjurgens/hallucinated-reference-finder`), Hallucinator, RefChecker, AtomGPT detector | Extract references and check them against bibliographic databases and web search | Mirrors what ICLR, ACL and arXiv now run on you. Evaluated in arXiv:2607.22693. All have false positives, for example on translated titles, so a human confirms each flag |

`tools/check_refs.py` in this repo does the same job with no dependencies, and
also fails a DOI that resolves to a different title.

## Agent skill bundles for academic work

The portable `SKILL.md` format means the same bundle usually runs in Claude
Code and Codex. The community index `O0000-code/awesome-academic-skills` listed
222 skills in 14 categories as of 28 August 2026.

| Project | What it gives you | Note |
| --- | --- | --- |
| `Imbad0202/academic-research-skills` | research → write → review → revise → finalize; a 12-agent pipeline with style calibration, LaTeX hardening, citation conversion and figure checks | The most complete single install. Opinionated, APA-centric defaults, heavy token use |
| `tansuasici/claude-research-kit` | CLAUDE.md and hooks templates, 14 hooks, 23 skills, CI scenarios | Hooks enforce source-grounding mechanically. Claude-specific |
| `witold-andelie/claude-latex-paper-skill` | Claim ledger, verified citations, de-AI prose rules, verification loop | The claim-ledger idea is where `notes/claim_ledger.md` comes from |
| `appautomaton/latex-arxiv-SKILL` | Gated LaTeX workflow with verified BibTeX, bridges to a second model for review | Dual-runtime, CI-tested, MIT. Targets review papers, which arXiv CS restricts |
| `bahayonghang/academic-writing-skills` | Format validation, grammar and style, de-AI editing, reference checks, reviewer-style audits for LaTeX, Typst and PDF | Improves existing drafts rather than generating them, which is the safest use |
| `Noi1r/beamer-skill` | Create, compile and review Beamer talks; extracts figures from paper PDFs | For the talk after the paper |

## Agent runtimes

| Runtime | Note |
| --- | --- |
| **Claude Code** | Largest academic skill ecosystem. A plugin bundles skills, hooks, subagents and MCP servers into one installable unit; skills live at `skills/<name>/SKILL.md` with a `.claude-plugin/plugin.json` manifest |
| **Codex CLI** (`openai/codex`) | Apache-2.0, strong at experiment code, reads the same SKILL.md bundles. The desktop app is proprietary |
| **Gemini CLI** (`google-gemini/gemini-cli`) | Apache-2.0, 1M context, free tier of 60 requests a minute and 1,000 a day with a personal Google account. Check the free tier's data-use terms before putting an unpublished draft through it |

## End-to-end "AI scientist" systems

Treat these as idea and experiment generators, not as authors.

| System | What it does | Note |
| --- | --- | --- |
| **AI Scientist-v2** (`SakanaAI/AI-Scientist-v2`) | Hypotheses, experiments by agentic tree search, figure feedback from a vision model, then writes the manuscript | First AI-generated paper to pass workshop peer review (ICLR 2025). Custom source-code license: check the repo terms. Lower success rate than v1; citation errors |
| **Agent Laboratory** (`SamuelSchmidgall/AgentLaboratory`) | Literature review, experiments, report writing, with a human-in-the-loop co-pilot mode. AgentRxiv lets agents build on each other's output | MIT, about 5.9k stars. Designed to assist a human. ML-centric |
| **Denario** (arXiv:2510.26887) | Multi-agent research assistant | One of only five fully AI-generated papers accepted at Agents4Science 2025. The authors note it ran on a laptop with a very limited dataset |
| **Jr. AI Scientist** (arXiv:2511.04583) | Extends a baseline paper autonomously and ships a risk report | Submitted to Agents4Science |

## Survey generators

| Tool | Note |
| --- | --- |
| **AutoSurvey** (`AutoSurveys/AutoSurvey`) | Retrieval, parallel outline and subsection drafting, refinement with citation checks. Fast: 73.59 surveys an hour reported for 64k-token surveys. Its bundled paper database stops around April 2024 unless refreshed; one fork extended it to August 2026 |
| **SurveyX / SurveyForge** | Keyword expansion, attribute trees, outline heuristics, memory-driven generation. Better outlines than naive RAG |

Caution: arXiv CS no longer accepts review or position papers without proof of
prior peer review, so a generated survey has nowhere easy to go.

## Venue-side tooling

Google's Paper Assistant Tool (PAT) was offered to ICLR submitters in
September 2026. Venues are starting to provide sanctioned pre-submission AI
checks of their own.

## Prompts worth reusing

Adapt to any agent. These assume this repo's layout.

**Related work**

> Using only entries in `refs.bib` and the PDFs in `sources/`, draft section 2
> grouping the work into three or four themes. For each sentence that makes a
> claim about a paper, put the key and a page number or quote in a LaTeX
> comment. Flag any gap as `\todo{CITE: ...}`.

**Claim audit**

> List every quantitative claim in `paper/sections/*.tex`. For each, show the
> source file in `experiments/results/` and confirm the value matches to the
> reported precision. Output a table of mismatches only.

**Reviewer response**

> For each numbered reviewer comment in `reviews/round1/reviews.md`, propose a
> response and the exact manuscript edit. Do not promise experiments that are
> not already in `experiments/`. Produce `response.tex` and run `latexdiff`.

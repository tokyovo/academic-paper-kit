# State of the field, October 2026

Background notes for this repo. They explain why the rules in `CLAUDE.md` are
strict, and what the alternatives are. Nothing here is needed to use the repo.

Read `docs/tools.md` for the tool-by-tool comparison and `docs/venues.md` for
publisher policy.

## The short version

The most defensible setup is a human-led agentic workflow: a coding agent
inside a Git and LaTeX repository, grounded literature tools, and automated
reference verification. Fully autonomous "AI scientist" pipelines can now
produce workshop-grade papers, but they are not safe to submit unsupervised.

The binding constraint is no longer writing quality. It is verification.

## Citation hallucination: the evidence

A hallucinated citation is a reference that does not exist: invented title,
invented authors, or a DOI that belongs to a different paper.

| Study | Setup | Findings |
| --- | --- | --- |
| GhostCite (arXiv:2602.06718, Feb 2026) | 13 models, 40 CS domains, 375,440 citations from 22,800 API calls, memory-only | DeepSeek 14.23%, GLM-4.5 21.25%, Claude 4 21.84%, Qwen-3 23.52%, Kimi 41.86%, Llama 4 45.84%, GPT-5 50.92%, Gemini 59.47%, Grok 4 79.98%, Hunyuan 94.93%. Rates rose for recent papers: 27.61% for 2000-era work, 98.75% for 2025. Online search and chain-of-thought had no consistent effect. Models verifying their own citations averaged 38% accuracy |
| arXiv:2604.03173 (2026) | Citation URLs from search-enabled models and deep-research agents, checked against the Wayback Machine | Claude lowest at 3.0–3.2%; gpt-4o-search-preview 8.8%; gemini-2.5-pro-deepresearch highest at 13.3%. Its `urlhealth` tool cut non-resolving URLs by 6–79 times, to under 1% |
| AAAI proceedings study | Citation hallucination detection | GPT-4o about 12%, Claude 3.5 Sonnet about 16%, Llama-4 Maverick about 21% |
| Neurocritical care study (PMC13506236) | 300 references, 10 per model per topic | DeepSeek-V3 23% bad (8% fabricated) against GPT-5.3 69% and Grok-4 73%; 28.3% completely fabricated overall |
| Mental-health study (PMC12658395) | GPT-4o, 176 citations | 19.9% fabricated; 64% of fabricated DOIs resolved to real but unrelated papers |

Do not merge these into one model ranking. Task design (memory against
search), domain, and the definition of "valid" dominate the results.

Two lessons hold across all of them:

- Retrieval-grounded pipelines cut hallucination by roughly ten times.

- Models are poor at checking their own citations. Use deterministic database
  lookups instead, which is what `tools/check_refs.py` does.

## Enforcement

- **GPTZero, 21 January 2026**: scanned 4,841 of 5,290 accepted NeurIPS 2025
  papers and confirmed 100 hallucinated citations across 51 papers. A
  follow-up analysis (arXiv:2602.05930) counts 53. All had passed three or
  more reviewers. GPTZero separately found 50+ in ICLR 2026 submissions.
  Note that GPTZero sells detection tools, so it has a commercial interest in
  the finding; its counts were human-verified.

- **GhostCite survey**: 604 of 56,381 papers (1.07%) at top AI and security
  venues had invalid citations, up 80.9% in 2025. Of 97 researchers surveyed,
  41.5% copy-paste BibTeX without checking, 87.2% use AI tools in their
  workflow, and 76.7% of reviewers do not check references thoroughly.

- **ICLR 2026**: desk-rejected every paper with confirmed hallucinated
  references. 779 of 19,525 submissions desk-rejected in total.

- **ACL 2026**: program chairs desk-rejected over 100 already-accepted papers
  at camera-ready after finding citations to non-existent literature.

- **arXiv, since 14 May 2026**: a one-year ban when a submission contains, in
  CS section chair Thomas Dietterich's words, "incontrovertible evidence that
  the authors did not check the results of LLM generation". After the ban,
  future submissions must first be accepted at a peer-reviewed venue. Appeals
  are allowed.

All three now run reference extraction and lookup pipelines with human
confirmation. Expect your bibliography to be machine-checked.

## Other known failures

- **Overclaiming and fabricated results.** Agents4Science authors reported
  models that would overclaim results. The BadScientist paper showed research
  agents can write convincing but unsound papers that fool LLM reviewers.

- **Hallucinated plots.** NeurIPS 2026 warns that high-level instructions to
  draw a figure produce invented figures. This is why `analysis/make_figures.py`
  exists.

- **Prompt injection against AI reviewers.** Agents4Science detected two
  papers trying to manipulate LLM reviewers. NeurIPS 2026 prohibits it
  explicitly. Hidden-prompt incidents were widely reported in 2025.

- **AI-text detection is unreliable as evidence.** ICLR 2026 used detectors
  only as a triage signal. Its reference checker had a significant
  false-positive rate, for example on translated non-English titles, so every
  flagged paper was checked by at least three humans. The claim that about 21%
  of ICLR 2026 reviews were fully AI-generated comes from third-party
  detectors and should be read as an estimate.

- **Flooding.** arXiv CS stopped accepting review and position papers without
  proof of peer review on 31 October 2025, after receiving hundreds of review
  articles a month. This limits what survey generators are useful for.

## How good are autonomous systems?

- **Sakana AI Scientist-v2**: 1 of 3 papers cleared the threshold at the ICLR
  2025 "I Can't Believe It's Not Better" workshop, with an average reviewer
  score of 6.33 out of 10 (individual scores 6, 6, 7), where 6 means
  "marginally above acceptance threshold". The track had lower requirements,
  the paper was withdrawn before meta-review, and Sakana said none of its
  papers met its own main-conference bar.

- **Agents4Science 2025**: 315 submissions, 253 complete, 48 accepted. Fully
  AI-driven papers were 23.3% of submissions but only 14.9% of acceptances.
  Only about 44% of submissions had zero flagged references. Accepted papers
  involved more human guidance. GPT-class models were used in 62.5% of
  accepted papers.

- **LLM reviewers** are useful as a lint pass but miscalibrated. Gemini 2.5
  Pro averaged 4.23 out of 6 and differed from human reviewers by a mean
  absolute 2.73 points. GPT-5 was much stricter at 2.30 average and closest to
  humans at 0.91. Distrust praise.

## Choosing a model

For agentic repository work, use whichever frontier model is strongest in your
harness: Claude in Claude Code, GPT-5.x in Codex, Gemini in Gemini CLI. Make
citation grounding a property of the workflow, not of the model. No model is
safe for citing from memory.

Prices and context windows below come from vendor pages as of late 2026 and go
stale fast. Verify before budgeting.

| Family | Context | Price per 1M tokens (in / out) | Note for academic work |
| --- | --- | --- | --- |
| Claude (Opus 4.8; Sonnet 5 / 5.5) | 1M | Opus 4.8 $5 / $25; Sonnet 5/5.5 $2 / $10 | Largest academic skill ecosystem; lowest search-grounded hallucination rate. Newer Opus 5 / 5.5 tiers exist and this row does not cover them |
| GPT-5.5 / 5.5 Pro | 1.05M API, 400K in Codex | 5.5: $5 / $30; Pro: $30 / $180; GPT-5: $1.25 / $10 | Strongest critical reviewer at Agents4Science; Codex CLI is Apache-2.0 |
| Gemini 3.1 Pro / 3.8 Flash | 1M | 3.1 Pro $2 / $12 up to 200k, $4 / $18 above; 3.8 Flash $0.75 / $3.75 promotional to 31 Dec 2026 | Best value for whole-corpus reading; Gemini CLI free tier is 1,000 requests a day |
| Open-weight (DeepSeek, Qwen, Llama, Mistral, GLM) | typically 128K+ | self-host cost only | The only option for genuinely confidential manuscripts. DeepSeek and Qwen did comparatively well in GhostCite |

On writing quality there is no rigorous venue-independent benchmark. Every
practitioner kit adds "de-AI" style rules, which tells you that every frontier
model's default register is recognisable. Choose on harness fit and
verification behaviour, not prose style.

ICML 2026 defines a privacy-compliant tool as one that does not train on
logged data and limits retention: enterprise APIs, consumer plans with
training opt-out, and self-hosted models. That is a good working definition
for confidential drafts too.

## Recommendations

1. Make citation integrity mechanical. Cite only from a library populated by
   DOI or arXiv import. Enforce it in `CLAUDE.md` and in `make check-refs`.

2. Keep the scientific judgement human: hypothesis, contribution claims,
   abstract, conclusions.

3. Generate every number and figure from code, versioned with commit hashes.

4. Use several models as adversarial reviewers, not cheerleaders. Pair a
   strict model with another family, give them the venue rubric, ignore praise.

5. Choose tools by job, not by brand. See `docs/tools.md`.

6. Treat autonomous AI-scientist systems as idea and experiment generators.
   Re-run the experiments, rewrite the paper, verify every reference, and
   disclose the system's role.

7. Disclose precisely, per venue. Record tool, model version, dates, tasks and
   key prompts as you go, in `ai_use_log.md`.

8. Final scrub before submitting. `make scrub` looks for the exact artifacts
   that trigger an arXiv ban.

## Caveats on these notes

- Prices, versions, model names and star counts change monthly.

- Several figures come from secondary sources, including ICML's 497 desk
  rejections, the 21% AI-generated-reviews estimate, and arXiv's "1 in 277
  papers" statistic.

- GPTZero, a primary source for the NeurIPS counts, sells detection tools.

- Hallucination rates differ hugely across studies by method. Do not merge
  them into one ranking.

- Licenses marked "see repo" in `docs/tools.md` were not individually
  verified. Check them before institutional or commercial use.

- Policies are summarised. Always read your venue's current author guidelines.

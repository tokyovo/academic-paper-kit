# What each venue requires

Current as of October 2026. Always read your venue's own author guidelines
before submitting: individual journals inside a publisher can be stricter.

Three points are settled everywhere:

- AI can never be an author.

- Substantive use must be disclosed.

- The human author is fully accountable for everything in the paper.

What changed recently is enforcement. Venues now run reference extraction and
database lookup on submissions, so a fabricated citation is found by machine
and treated as fabrication even when the rest of the paper is sound.

| Venue | Where to disclose | Enforcement in force |
| --- | --- | --- |
| Springer Nature / Nature | Methods section. AI copy-editing is exempt | Generated images banned except narrow cases; reviewers may not upload manuscripts |
| Science (AAAS) | Cover letter, acknowledgments, and the full prompts in Methods | AI images need editor permission; reviewers may not use AI to write reviews |
| Elsevier | Declaration statement at submission. Grammar tools exempt | No AI alteration of research images |
| IEEE | Acknowledgments: the system used, which sections, level of involvement | Reviewers may not use public AI platforms |
| ACM | Full disclosure of generated content. Spelling and grammar exempt | Per ACM peer review policy |
| arXiv | Authors take full responsibility | Since 14 May 2026: one-year ban for clear evidence of unchecked LLM output. CS reviews and position papers need prior peer review |
| NeurIPS 2026 | Experimental setup, if the use was important, original or non-standard | Hallucinated citations breach the code of conduct |
| ICLR 2026 | Any LLM use | 779 of 19,525 submissions desk-rejected, partly for hallucinated references |
| ICML 2026 | Hallucinated references are grounds for desk rejection | Reviewer policy is dual: conservative or privacy-compliant only |
| ACL / ARR 2026 | Per ARR policy; conceptual help allowed | Over 100 accepted papers desk-rejected at camera-ready for non-existent references |

## Confidential manuscripts

Most venues forbid uploading a manuscript you are reviewing into an
unsanctioned model. ICML's working definition of a privacy-compliant tool is
one that does not train on logged data and limits retention: an enterprise
API, a consumer plan with training opt-out, or a self-hosted model.

For your own unpublished draft the same caution is sensible. If the draft is
sensitive, run a local open-weight model instead.

## Keeping disclosure cheap

Fill in `ai_use_log.md` as you go. Every format above can then be written in a
few minutes from that one file.

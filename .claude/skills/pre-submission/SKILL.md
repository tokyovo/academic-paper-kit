---
name: pre-submission
description: Run the full pre-submission gate and write the venue's AI disclosure. Use before submitting to any journal or conference, before a camera-ready, or when the user asks whether the paper is ready to send.
---

# Pre-submission check

Run everything, report plainly, fix nothing silently.

## 1. The gate

```
make check
```

That chain is: tables, figures, fresh reference verification, strict scrub, and
the PDF build. If any step fails, stop and report. Do not work around a
failure.

Then:

```
make ledger
```

## 2. Manual checks the tools cannot do

- Open the PDF. Confirm every figure renders, every table has its caption, and
  no `[TODO: ...]` in red survives.

- Confirm the abstract and the contribution list are the human's words.

- Confirm the page limit and the anonymity requirement for the venue.

- Confirm every PDF in `sources/` corresponds to a cited key, and that the user
  has read them.

## 3. The disclosure

Read `docs/venues.md` for the user's venue. Build the disclosure text from
`ai_use_log.md`:

- Springer Nature: a Methods paragraph. Copy-editing is exempt.

- Science: a cover letter note, an acknowledgments line, and the full prompts
  in Methods.

- IEEE or ACM: an acknowledgments paragraph naming the system, the sections,
  and the level of involvement.

- Elsevier: a declaration statement at submission.

- NeurIPS: a note in the experimental setup, if the use was non-standard.

- arXiv: no form to fill, but full author responsibility.

Draft the text and show it to the user. Do not paste it into the manuscript
without their approval.

## 4. Report

State, in this order: what passed, what failed, what the user must still
decide, and the disclosure text. If anything is unverified, say which part and
why. Never report the paper as ready when a reference check errored out.

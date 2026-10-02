---
name: reviewer-response
description: Draft a point-by-point response to peer reviews and the matching manuscript edits. Use when the user has reviews to answer, a rebuttal to write, or a revision to prepare for any venue.
---

# Reviewer response

## Setup

Reviews go in `reviews/round1/reviews.md`, one numbered comment per point.
Your output is `reviews/round1/response.tex` plus the actual edits.

## Steps

1. Read every comment. Group them: factual error, missing experiment, unclear
   writing, disagreement about framing, request out of scope.

2. For each comment write: the response, and the exact manuscript edit that
   backs it up. A response that promises a change without making it is how
   papers fail a second round.

3. **Never promise an experiment that is not in `experiments/`.** If a
   reviewer asks for one, tell the user; they decide whether to run it. Do not
   write "we have added this experiment" before the result file exists.

4. Make the edits, then produce the diff:

   ```
   cd paper && latexdiff main_submitted.tex main.tex > diff.tex && latexmk -pdf diff.tex
   ```

5. Verify: `make check-refs`, `make scrub`, `make paper`.

## Tone

Short, specific, and not defensive. Concede what is right. Where you disagree,
give the evidence and leave the judgement to the editor. Do not thank the
reviewer more than once.

Tone and concessions are the human author's call. Draft them, flag them, and
let the user decide.

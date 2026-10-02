---
name: related-work
description: Draft or revise the related work section from verified sources only. Use when the user asks for a related work, background, or literature review section, in any field.
---

# Related work

## Before drafting

Check three things and stop if any fails:

- `paper/refs.bib` has entries, and `make check-refs` passes.

- The PDFs of the papers you will discuss are in `sources/`.

- You know the paper's own contribution, so the section can set it up. If you
  do not, ask.

## Drafting

1. Group the cited work into three or four themes. Name each theme after what
   the work does, not after a method's brand name.

2. Write one paragraph per theme. Each paragraph ends by saying what that line
   of work does not do, which is what the paper addresses.

3. For every sentence that makes a claim about a specific paper, put the
   evidence in a LaTeX comment on the next line:

   ```
   Prior work treats zone assignment as nearest-neighbour matching \cite{key2021}.
   % sources/key2021.pdf p.4: "we assign each detection to the closest zone centroid"
   ```

4. Cite only keys that already exist in `refs.bib`. If a theme needs a source
   you do not have, write `\todo{CITE: <what is needed>}` and tell the user.

5. Write into `paper/sections/02_related_work.tex`, one sentence per line.

## After drafting

- Add each claim about prior work to `notes/claim_ledger.md` with the source
  and page.

- Run `make scrub` and `make check-refs`.

- Tell the user which claims rest on your reading of a PDF, so they can spot-check.

## Do not

- Do not describe a paper you have not opened in `sources/`.

- Do not write "to the best of our knowledge, no prior work..." unless the
  user asserts it. That is their claim to make.

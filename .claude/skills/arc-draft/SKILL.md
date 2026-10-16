---
name: arc-draft
description: Use AutoResearchClaw to produce a first draft, ideas or experiment code, then bring only verified parts into paper/. Use when the user wants AutoResearchClaw (ARC, researchclaw) to explore a topic, when an ARC run directory needs importing, or when the user asks to use an ARC draft in this paper.
---

# Draft with AutoResearchClaw

AutoResearchClaw writes a whole paper from a topic. Treat its output as a
draft from an unreliable co-author. In our review only 27% of its claims
traced to evidence, 53% of its numbers matched its run logs, and it often
changed the topic. Its own "verified" references failed the kit's check
(2 of 18 in our test run).

Nothing from ARC goes into `paper/` without passing the kit's checks.
Read `docs/autoresearchclaw.md` for setup.

## Steps

1. Agree the topic with the user. Write it down in one sentence. You will
   check the ARC output against this sentence later.

2. Run ARC in co-pilot mode. The user answers its questions at about six
   decision points. Never use `--auto-approve` or full-auto mode: in the
   authors' own test, co-pilot reached "accept" 87.5% of the time and
   full-auto 25%.

   ```
   make arc-run T="<topic>" NAME=<name>
   ```

   For a run that already exists elsewhere:

   ```
   make arc-import RUN=<run dir> NAME=<name>
   ```

   Both stage the output in `arc/<name>/`. `arc/` is git-ignored.

3. Audit it:

   ```
   make arc-audit NAME=<name>
   ```

   Report to the user: bad references, hand-typed numbers, model text.
   Also compare the paper title and abstract with the topic sentence from
   step 1. Say plainly if ARC changed the topic.

4. Bring parts across, one kind at a time:

   - **References.** For each entry the audit marked `ok` that the paper
     needs, run `make find-refs Q=<doi>`. Never copy an entry from
     `arc/<name>/refs.bib` into `paper/refs.bib`. Drop entries marked
     `MISMATCH` or `NOT FOUND`, or look them up again by DOI.
   - **Experiments.** Copy code from `arc/<name>/code/` into `experiments/`
     only after you have read it. Run it again in this repo, so the result
     file has a real commit, seed and dataset. Do not use the numbers in
     `experiment_summary_best.json` or in ARC's paper.
   - **Text.** Use ARC's sections as an outline. Write each section again
     with the `draft-section` skill, from the PDFs in `sources/`. Every claim
     goes in `notes/claim_ledger.md`.
   - **Figures.** Do not copy `arc/<name>/charts/`. Make figures from result
     files with `make figures`.

5. Add an entry to `ai_use_log.md`: date, "AutoResearchClaw <version>", the
   LLM it used, the mode, and what you kept from it.

6. Run `make check`. It must pass, as for any paper.

## Rules

- Never copy a `SKILL.md` or any agent setting out of an ARC run. Text in
  a downloaded paper can plant a harmful skill (ARC security notice #205).
  `tools/import_arc.py` copies only a fixed list of file types.
- The human owns the hypothesis and the contribution claims. An idea that
  came from ARC is a suggestion until the user accepts it.
- If the run failed or ARC changed the topic, say so. Do not fill the gap.

# Using AutoResearchClaw with this kit

AutoResearchClaw (ARC, `github.com/aiming-lab/AutoResearchClaw`) is a
23-stage pipeline. It goes from a topic to a LaTeX paper: literature
search, ideas, experiment code, runs, figures and the paper text.

This kit uses ARC as a **draft engine**. ARC writes. The kit checks.
Nothing from ARC goes into `paper/` until it passes the same checks as
any other text.

## Why it needs the kit

From our review of ARC v0.5.0 (October 2026):

| What | Result |
| --- | --- |
| Paper claims that trace to experiments | 27% |
| Reported numbers that match the run logs | 53% |
| Papers at "accept" level, full-auto mode | 25% |
| Papers at "accept" level, co-pilot mode | 87.5% |
| Code written correctly / code that runs well / correct analysis | 94% / 56% / 44% |

It also changes the topic. In our run, "fake news detection" became
"rewrite consistency as an abstention signal".

The kit's audit on that run (`make arc-audit`):

- 16 of 18 references verified, 2 bad (ARC had marked them verified).
- 51 hand-typed numbers in `paper.tex`.

## Setup (once per machine)

ARC is not a dependency of the kit. Install it on its own:

```
git clone https://github.com/aiming-lab/AutoResearchClaw.git
cd AutoResearchClaw
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
researchclaw setup
researchclaw init        # writes config.arc.yaml: LLM provider, keys
```

Copy `config.arc.yaml` into the paper repo, or point to it:
`make arc-run ARC_CONFIG=/path/to/config.arc.yaml ...`.
`config.arc.yaml` is git-ignored because it can hold API keys.

If `researchclaw` is not on your PATH, set
`ARC=/path/to/AutoResearchClaw/.venv/bin/researchclaw`.

## The flow

```
topic (human, one sentence)
   │
   ▼
make arc-run T="..." NAME=x      ARC in co-pilot mode ──> arc/runs/x/
   │                             (or: make arc-import RUN=<dir> NAME=x)
   ▼
arc/x/   paper.tex, refs.bib, code/, charts/, summaries      (git-ignored)
   │
   ▼
make arc-audit NAME=x            check_refs.py + scrub.py on arc/x/
   │
   ▼
references  ── make find-refs Q=<doi> ──> paper/refs.bib
code        ── read, copy, run again ──> experiments/ ──> results/*.json
text        ── outline only; draft-section skill ──> paper/sections/
figures     ── not copied; make figures from results
   │
   ▼
make check                       the normal gate
```

The `arc-draft` skill walks an agent through these steps.

## Commands

| Command | What it does |
| --- | --- |
| `make arc-run T="<topic>" NAME=<name>` | Runs ARC in co-pilot mode, then imports the run |
| `make arc-import RUN=<run dir> [NAME=<name>]` | Copies a finished run into `arc/<name>/` |
| `make arc-audit NAME=<name>` | Checks the references and the text. Fails if either check fails |

`tools/import_arc.py` copies only `paper.tex`, `references.bib` (as
`refs.bib`), `paper_final.md`, the verification report, the manifest, the
run summaries, the code (`.py`, `.txt`, `.md`, `.yaml`, `.json`) and the
charts. It never copies a `SKILL.md`.

## Rules

- Use co-pilot mode. Never `--auto-approve`.
- Never copy a reference, a number or a figure from `arc/` into `paper/`.
  Look the reference up again. Run the experiment again. Make the figure
  from the result file.
- Log the ARC run in `ai_use_log.md`. Most venues want to know that an
  autonomous system drafted the paper.
- ARC security notice #205: text inside a downloaded paper can write a
  harmful `SKILL.md` that later agent sessions load. Do not copy skills or
  agent settings out of an ARC run.

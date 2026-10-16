#!/usr/bin/env python3
"""Copy an AutoResearchClaw run into arc/<name>/ so the kit can audit it.

AutoResearchClaw (github.com/aiming-lab/AutoResearchClaw) writes a whole
paper from a topic. Its output is a draft, not a source of truth: in our
review only 27% of its claims traced to evidence and 53% of its numbers
matched the run logs. So nothing it writes goes into paper/ directly.
This script stages the output in arc/<name>/, where `make arc-audit` runs
the kit's checkers on it.

It copies only a fixed list of files. It never copies SKILL.md files or
agent settings: text inside a downloaded paper can plant a harmful skill
(AutoResearchClaw security notice #205).

Usage:
    python tools/import_arc.py <run dir> [--name <name>]

<run dir> is the --output directory of `researchclaw run`, the one that
holds deliverables/. The default name is the run directory's name.
"""

from __future__ import annotations

import os
import shutil
import sys

# deliverables/<file> -> arc/<name>/<file>. references.bib becomes refs.bib
# so that scrub.py can match \cite keys against it.
DELIVERABLES = {
    "paper.tex": "paper.tex",
    "references.bib": "refs.bib",
    "paper_final.md": "paper_final.md",
    "verification_report.json": "verification_report.json",
    "manifest.json": "manifest.json",
}
RUN_FILES = ["experiment_summary_best.json", "pipeline_summary.json"]
# Only these file types are copied from deliverables/code and /charts.
CODE_EXT = (".py", ".txt", ".md", ".yaml", ".yml", ".json")
CHART_EXT = (".png", ".pdf", ".svg")


def copy_dir(src: str, dst: str, exts: tuple[str, ...], copied: list[str]) -> None:
    if not os.path.isdir(src):
        return
    for root, _dirs, files in os.walk(src):
        for name in sorted(files):
            if not name.endswith(exts) or name.upper() == "SKILL.MD":
                continue
            path = os.path.join(root, name)
            out = os.path.join(dst, os.path.relpath(path, src))
            os.makedirs(os.path.dirname(out), exist_ok=True)
            shutil.copyfile(path, out)
            copied.append(out)


def main() -> int:
    args = sys.argv[1:]
    name = None
    if "--name" in args:
        i = args.index("--name")
        name = args[i + 1] if i + 1 < len(args) else None
        del args[i:i + 2]
    if len(args) != 1:
        print(__doc__.strip().split("Usage:")[1])
        return 2

    run = os.path.abspath(args[0])
    deliv = os.path.join(run, "deliverables")
    if not os.path.isdir(deliv):
        print(f"import-arc: no deliverables/ in {run}. Did the run finish?")
        return 1

    name = name or os.path.basename(run.rstrip("/"))
    dest = os.path.join("arc", name)
    if os.path.exists(dest):
        shutil.rmtree(dest)
    os.makedirs(dest)

    copied: list[str] = []
    missing: list[str] = []
    for src, out in DELIVERABLES.items():
        path = os.path.join(deliv, src)
        if os.path.isfile(path):
            shutil.copyfile(path, os.path.join(dest, out))
            copied.append(os.path.join(dest, out))
        else:
            missing.append(f"deliverables/{src}")
    for src in RUN_FILES:
        path = os.path.join(run, src)
        if os.path.isfile(path):
            shutil.copyfile(path, os.path.join(dest, src))
            copied.append(os.path.join(dest, src))
        else:
            missing.append(src)
    copy_dir(os.path.join(deliv, "code"), os.path.join(dest, "code"), CODE_EXT, copied)
    copy_dir(os.path.join(deliv, "charts"), os.path.join(dest, "charts"), CHART_EXT, copied)

    with open(os.path.join(dest, "SOURCE.txt"), "w", encoding="utf-8") as fh:
        fh.write(f"Imported from: {run}\n")
        fh.write("This is an AutoResearchClaw draft. Nothing here is verified.\n")
        fh.write("Run: make arc-audit NAME=" + name + "\n")

    print(f"import-arc: {len(copied)} files -> {dest}/")
    for path in missing:
        print(f"  missing: {path}")
    if not os.path.isfile(os.path.join(dest, "paper.tex")):
        print("import-arc: the run has no paper.tex. It did not reach the export stage.")
        return 1
    print(f"Next: make arc-audit NAME={name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

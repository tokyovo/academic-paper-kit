#!/usr/bin/env python3
r"""Check that every cited sentence carries a quote that is in the source.

CLAUDE.md asks that every cited claim be traceable to a passage, written as a
comment on the line after the sentence (one sentence per line):

    Prior work assigns each detection to the nearest zone \cite{key2021}.
    % sources/key2021.pdf p.4: "we assign each detection to the closest zone centroid"

This check makes the rule hold:
  - every line with \cite{...} is followed by at least one evidence comment
    for one of its keys;
  - every evidence comment names a PDF that exists in sources/ and a key the
    sentence cites;
  - the quote is on that page of that PDF.

Usage:
    python tools/check_evidence.py [paper/sections] [--sources sources]

Exit status is 1 on any problem. Needs pdftotext (poppler).
"""

from __future__ import annotations

import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_extractions import MIN_QUOTE, page_text, squash  # noqa: E402

CITE = re.compile(r"\\cite[a-zA-Z]*\s*(?:\[[^\]]*\])*\{([^}]*)\}")
EVIDENCE = re.compile(r'^\s*%\s*sources/([^/\s]+)\.pdf\s+p\.?\s*(\d+)\s*:\s*"(.*)"\s*$')


def check_file(path: str, sources: str, cache: dict) -> tuple[int, list[str]]:
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    problems, n_cited = [], 0
    for i, line in enumerate(lines):
        code = line.split("%", 1)[0] if not line.lstrip().startswith("%") else ""
        keys = {k.strip() for m in CITE.finditer(code) for k in m.group(1).split(",")
                if k.strip()}
        if not keys:
            continue
        n_cited += 1
        where = f"{path}:{i + 1}"
        evidence = []
        j = i + 1
        while j < len(lines) and lines[j].lstrip().startswith("%"):
            if m := EVIDENCE.match(lines[j]):
                evidence.append((j + 1, m.group(1), int(m.group(2)), m.group(3)))
            j += 1
        if not evidence:
            problems.append(f"{where}: cites {', '.join(sorted(keys))} with no evidence "
                            'comment (% sources/<key>.pdf p.N: "quote") on the next line')
            continue
        for lineno, key, page, quote in evidence:
            ewhere = f"{path}:{lineno}"
            pdf = os.path.join(sources, f"{key}.pdf")
            if key not in keys:
                problems.append(f"{ewhere}: evidence from {key}, but the sentence cites "
                                f"{', '.join(sorted(keys))}")
            elif not os.path.exists(pdf):
                problems.append(f"{ewhere}: no {pdf}; do not cite what is not in {sources}/")
            elif len(quote) < MIN_QUOTE:
                problems.append(f"{ewhere}: quote shorter than {MIN_QUOTE} characters")
            elif squash(quote) not in page_text(pdf, page, cache):
                problems.append(f'{ewhere}: not on page {page} of {key}: "{quote[:60]}"')
    return n_cited, problems


def main() -> int:
    argv = sys.argv[1:]
    sources = "sources"
    if "--sources" in argv:
        i = argv.index("--sources")
        sources = argv[i + 1]
        del argv[i:i + 2]
    target = argv[0] if argv else "paper/sections"
    if not shutil.which("pdftotext"):
        print("check-evidence: pdftotext is not installed (brew install poppler).")
        return 1
    files = [target] if target.endswith(".tex") else sorted(
        os.path.join(target, f) for f in os.listdir(target) if f.endswith(".tex"))

    cache: dict = {}
    problems, total = [], 0
    for path in files:
        n, p = check_file(path, sources, cache)
        total += n
        problems += p
    print(f"check-evidence: {total} cited sentence(s) in {len(files)} file(s)\n")
    for p in problems:
        print(f"  {p}")
    if problems:
        print(f"\n{len(problems)} problem(s). Copy the supporting quote from the PDF "
              "page, or drop the citation.")
        return 1
    print("  every cited sentence has a quote that is in its source")
    return 0


if __name__ == "__main__":
    sys.exit(main())

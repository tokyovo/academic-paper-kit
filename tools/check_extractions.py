#!/usr/bin/env python3
"""Check that every quote in notes/extractions/<bibkey>.md is in the PDF.

A reader agent turns sources/<bibkey>.pdf into notes. A writer agent drafts
from those notes, not from the PDF. So an invented "fact" in the notes would
reach the paper with a real citation on it. This check stops that: every fact
must carry a verbatim quote and a page, and the quote must be on that page.

Extraction format (one file per paper):

    # <bibkey>

    - F1: The fact, in your own words.
      - quote: "Exact words copied from the PDF."
      - page: 3

Usage:
    python tools/check_extractions.py [notes/extractions] [--sources sources]
    python tools/check_extractions.py notes/extractions/wang2017liar.md

Exit status is 1 if any quote is missing from its page, any fact has no
quote, or a file has no PDF. Needs pdftotext (poppler).
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys

FACT = re.compile(r"^\s*-\s*(F\d+):")
QUOTE = re.compile(r'^\s*-\s*quote:\s*"(.*)"\s*$')
PAGE = re.compile(r"^\s*-\s*page:\s*(\d+)\s*$")
# A quote must be long enough to pin down a passage.
MIN_QUOTE = 25


def squash(text: str) -> str:
    """Compare without spacing, case, hyphens or ligatures: PDF text breaks
    lines and words in places the reader did not copy."""
    text = text.replace("ﬁ", "fi").replace("ﬂ", "fl").replace("ﬀ", "ff")
    return re.sub(r"[^a-z0-9]", "", text.lower())


def page_text(pdf: str, page: int, cache: dict) -> str:
    if (pdf, page) not in cache:
        cache[(pdf, page)] = squash(subprocess.run(
            ["pdftotext", "-f", str(page), "-l", str(page), pdf, "-"],
            capture_output=True, text=True, errors="replace").stdout)
    return cache[(pdf, page)]


def facts(path: str) -> list[dict]:
    out, current = [], None
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            if m := FACT.match(line):
                current = {"id": m.group(1), "line": lineno, "quotes": []}
                out.append(current)
            elif current and (m := QUOTE.match(line)):
                current["quotes"].append({"text": m.group(1), "page": None})
            elif current and current["quotes"] and (m := PAGE.match(line)):
                current["quotes"][-1]["page"] = int(m.group(1))
    return out


def check_file(path: str, sources: str, cache: dict) -> list[str]:
    key = os.path.splitext(os.path.basename(path))[0]
    pdf = os.path.join(sources, f"{key}.pdf")
    if not os.path.exists(pdf):
        return [f"{path}: no {pdf}; notes must come from a PDF in {sources}/"]
    problems = []
    found = facts(path)
    if not found:
        problems.append(f"{path}: no facts (lines like '- F1: ...')")
    for fact in found:
        where = f"{path}:{fact['line']} {fact['id']}"
        if not fact["quotes"]:
            problems.append(f"{where}: no quote")
        for q in fact["quotes"]:
            if len(q["text"]) < MIN_QUOTE:
                problems.append(f"{where}: quote shorter than {MIN_QUOTE} characters")
            elif q["page"] is None:
                problems.append(f"{where}: quote has no page")
            elif squash(q["text"]) not in page_text(pdf, q["page"], cache):
                problems.append(f'{where}: not on page {q["page"]}: "{q["text"][:60]}"')
    return problems


def main() -> int:
    argv = sys.argv[1:]
    sources = "sources"
    if "--sources" in argv:
        i = argv.index("--sources")
        sources = argv[i + 1]
        del argv[i:i + 2]
    target = argv[0] if argv else "notes/extractions"
    if not shutil.which("pdftotext"):
        print("check-extractions: pdftotext is not installed (brew install poppler).")
        return 1
    files = ([target] if target.endswith(".md") else
             sorted(os.path.join(target, f) for f in os.listdir(target)
                    if f.endswith(".md"))) if os.path.exists(target) else []
    if not files:
        print(f"check-extractions: no extraction files at {target}. Nothing to check.")
        return 0

    cache: dict = {}
    problems, n_facts = [], 0
    for path in files:
        n_facts += len(facts(path))
        problems += check_file(path, sources, cache)
    print(f"check-extractions: {len(files)} file(s), {n_facts} fact(s)\n")
    for p in problems:
        print(f"  {p}")
    if problems:
        print(f"\n{len(problems)} problem(s). Copy each quote exactly from the "
              "PDF page, or delete the fact.")
        return 1
    print("  every quote is on its page")
    return 0


if __name__ == "__main__":
    sys.exit(main())

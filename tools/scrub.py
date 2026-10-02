#!/usr/bin/env python3
r"""Scan the manuscript for the things that get papers desk-rejected.

Four checks:
  1. Leftover model text ("As an AI", "Certainly!", "I hope this helps").
  2. Placeholders that were never filled (TODO, \todo{CITE}, [insert], X.XX).
  3. Every \cite key resolves to an entry in refs.bib.
  4. No hand-typed decimal or percentage: our numbers come from the result
     macros that make tables writes, and another paper's number needs its
     \cite on the same line.

arXiv's own ban policy names exactly these as evidence that the authors did
not check their generated output. Run this before every submission and every
camera-ready.

Usage:
    python tools/scrub.py [paper_dir] [--strict]

--strict also fails on unused bib entries and on hedge-free superlatives.
--draft reports unfinished work (\todo, template text, empty sections) as
warnings, for CI on a draft in progress. Signs of fabrication stay blocking:
model text, unknown cite keys and hand-typed numbers. make check runs
without --draft.
Exit status is 1 if anything blocking is found.
"""

from __future__ import annotations

import os
import re
import sys

# Phrases a model leaves behind. Matched case-insensitively.
MODEL_TEXT = [
    r"as an ai\b", r"as a large language model", r"as an? language model",
    r"\bcertainly[!,]", r"\bsure[!,] (?:here|i)", r"i hope this helps",
    r"i cannot (?:browse|access|verify)", r"\bfeel free to\b",
    r"here(?:'s| is) (?:the|a) (?:revised|updated|rewritten)",
    r"let me know if", r"based on my training data", r"i don'?t have access to",
    r"^\s*(?:note|disclaimer):\s*(?:i|as|this response)",
    r"\[your \w+ here\]", r"\bin this response\b", r"knowledge cutoff",
]

# Placeholders. These are blocking: a number like X.XX in a submitted PDF is
# indistinguishable from fabrication to a reviewer.
PLACEHOLDERS = [
    r"\\todo\{", r"\bTODO\b", r"\bFIXME\b", r"\bTBD\b", r"\bXXX\b",
    r"\[insert[^\]]*\]", r"\[fill in[^\]]*\]", r"lorem ipsum",
    r"\bX\.XX\b", r"\bN\.NN\b", r"\b\?\?\?\b", r"\bTK\b",
    r"\\cite\{\s*\}", r"\\cite\{(?:TODO|CITE|XXX|ref)\}",
    r"\\ref\{\s*\}", r"placeholder", r"[Ww]rite the caption here",
    # Leftovers of the template's own title block and abstract.
    r"Working title: replace this", r"\bYour Name\b", r"\bYour Institution\b",
    r"you@example\.edu", r"The human author writes this",
]

# A decimal number or a percentage typed into the text. Our own numbers must
# come from the result macros (\resLiar...), and a number from another paper
# needs its \cite on the same line (one sentence per line).
HAND_NUMBER = r"(?<![\w.\\])\d+\.\d+(?![\w.])|(?<![\w.\\])\d+(?:\.\d+)?\s*\\%"

# Claims that need a citation in the same sentence. Warning, not blocking.
SUPERLATIVES = [
    r"\bstate[- ]of[- ]the[- ]art\b", r"\bgroundbreaking\b", r"\bnovel\b",
    r"\bfirst (?:ever|work|paper|study) to\b", r"\bunprecedented\b",
    r"\bsignificantly outperform", r"\brevolutionar",
]


def tex_files(root: str) -> list[str]:
    found = []
    for dirpath, _dirs, files in os.walk(root):
        for name in sorted(files):
            if name.endswith(".tex"):
                found.append(os.path.join(dirpath, name))
    return sorted(found)


def strip_comments(line: str) -> str:
    """Drop a LaTeX comment, respecting \\%."""
    out = []
    i = 0
    while i < len(line):
        if line[i] == "\\" and i + 1 < len(line):
            out.append(line[i:i + 2])
            i += 2
            continue
        if line[i] == "%":
            break
        out.append(line[i])
        i += 1
    return "".join(out)


def bib_keys(bib_path: str) -> set[str]:
    if not os.path.exists(bib_path):
        return set()
    with open(bib_path, encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    return {m.group(1).strip() for m in
            re.finditer(r"@\w+\s*\{\s*([^,\s]+)\s*,", text)}


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    strict = "--strict" in sys.argv[1:]
    # Unfinished work blocks a submission, not a draft.
    draft = "--draft" in sys.argv[1:]
    paper_dir = args[0] if args else "paper"
    bib_path = os.path.join(paper_dir, "refs.bib")

    files = tex_files(paper_dir)
    if not files:
        print(f"scrub: no .tex files under {paper_dir}/")
        return 1

    keys = bib_keys(bib_path)
    blocking: list[str] = []
    warnings: list[str] = []
    cited: set[str] = set()
    unfinished = warnings if draft else blocking

    for path in files:
        # A section file with a heading and no text passes every other check.
        has_section = has_text = False
        with open(path, encoding="utf-8", errors="replace") as fh:
            for lineno, raw in enumerate(fh, 1):
                # An escape hatch for a line that must contain a trigger
                # word, such as the \todo macro definition itself.
                if "scrub:ignore" in raw:
                    continue
                line = strip_comments(raw).rstrip("\n")
                if not line.strip():
                    continue
                # A macro definition is not manuscript text.
                if re.search(r"\\(?:re|provide)?newcommand|\\DeclareRobustCommand"
                             r"|\\def\\", line):
                    continue
                where = f"{path}:{lineno}"
                if re.match(r"\s*\\section\*?\{", line):
                    has_section = True
                elif has_section:
                    has_text = True

                for pattern in MODEL_TEXT:
                    m = re.search(pattern, line, re.I)
                    if m:
                        blocking.append(f"{where}  model text: \"{m.group(0).strip()}\"")

                for pattern in PLACEHOLDERS:
                    m = re.search(pattern, line)
                    if m:
                        unfinished.append(f"{where}  placeholder: \"{m.group(0).strip()}\"")

                # Generated tables hold numbers by design.
                generated = os.sep + "tables" + os.sep in path
                m = re.search(HAND_NUMBER, line)
                if m and not generated and "\\cite" not in line:
                    blocking.append(
                        f"{where}  hand-typed number \"{m.group(0)}\": use a result "
                        "macro from make tables, or cite its source on this line")

                for m in re.finditer(r"\\cite[a-zA-Z]*\s*(?:\[[^\]]*\])*\{([^}]*)\}", line):
                    for key in m.group(1).split(","):
                        key = key.strip()
                        if not key:
                            continue
                        cited.add(key)
                        # An empty refs.bib makes every \cite unresolved.
                        if key not in keys:
                            blocking.append(
                                f"{where}  \\cite{{{key}}} is not in {bib_path}")

                if strict:
                    for pattern in SUPERLATIVES:
                        m = re.search(pattern, line, re.I)
                        if m and "\\cite" not in line:
                            warnings.append(
                                f"{where}  \"{m.group(0)}\" with no citation on the line")
        if has_section and not has_text:
            unfinished.append(f"{path}  empty section: write it, or remove its \\input")

    if strict and keys:
        for key in sorted(keys - cited):
            warnings.append(f"{bib_path}  {key} is never cited")

    print(f"scrub: checked {len(files)} file(s) under {paper_dir}/ "
          f"against {len(keys)} bib entries\n")

    if blocking:
        print(f"BLOCKING ({len(blocking)}):\n")
        for item in blocking:
            print(f"  {item}")
        print()
    if warnings:
        print(f"warnings ({len(warnings)}):\n")
        for item in warnings:
            print(f"  {item}")
        print()
    if not blocking and not warnings:
        print("  clean\n")

    if blocking:
        print("Fix every blocking item before submitting. These are the exact\n"
              "triggers arXiv names in its one-year ban policy.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

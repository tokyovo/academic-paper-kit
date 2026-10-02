#!/usr/bin/env python3
"""Check that every claim in notes/claim_ledger.md points at a real file.

A ledger row is only useful if its evidence path exists. This flags rows whose
evidence is missing, whose section file is missing, or whose status is still
pending.

Usage:
    python tools/check_ledger.py [notes/claim_ledger.md]

Exit status is 1 if any row has missing evidence.
"""

from __future__ import annotations

import glob
import os
import re
import sys

LEDGER = "notes/claim_ledger.md"
CLAIMS_DIR = "notes/claims"


def rows(path: str) -> list[list[str]]:
    out = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) < 4:
                continue
            if cells[0].lower() == "claim" or set(cells[0]) <= {"-", ":", " "}:
                continue
            out.append(cells)
    return out


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else LEDGER
    if not os.path.exists(path):
        print(f"ledger: no such file: {path}")
        return 1

    entries = rows(path)
    if len(sys.argv) == 1:
        # Parallel writers each keep their own ledger, one file per section,
        # so they never edit the same file at the same time.
        for extra in sorted(glob.glob(os.path.join(CLAIMS_DIR, "*.md"))):
            entries += rows(extra)
            path += f" + {extra}"
    if not entries:
        print(f"ledger: {path} has no claim rows yet.")
        return 0

    missing, pending, ok = [], [], 0
    for cells in entries:
        claim, section, evidence, status = cells[0], cells[1], cells[2], cells[3]
        short = (claim[:58] + "...") if len(claim) > 61 else claim
        problems = []
        if evidence.lower() != "external" and not re.match(r"^\\cite", evidence):
            file_part = evidence.split(" p.")[0].split("#")[0].strip("` ")
            if file_part and not os.path.exists(file_part):
                problems.append(f"evidence not found: {file_part}")
        if section and not os.path.exists(section.strip("` ")):
            problems.append(f"section file not found: {section}")
        if problems:
            missing.append((short, problems))
        elif status.lower() == "pending":
            pending.append(short)
        else:
            ok += 1

    print(f"ledger: {len(entries)} claim(s) in {path}\n")
    print(f"  backed by a real file : {ok}")
    print(f"  pending               : {len(pending)}")
    print(f"  broken                : {len(missing)}")

    if pending:
        print("\nStill pending:\n")
        for short in pending:
            print(f"  - {short}")
    if missing:
        print("\nBroken rows:\n")
        for short, problems in missing:
            print(f"  - {short}")
            for problem in problems:
                print(f"      {problem}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

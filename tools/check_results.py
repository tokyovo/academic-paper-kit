#!/usr/bin/env python3
"""Check that every result file can be traced to code, data and settings.

Every number in the paper comes from experiments/results/*.json. A result
file is only evidence if it says which code produced it (a real git commit),
with which seed, on which data, in which environment.

Required in each file: run_id, commit, seed, dataset, metrics, environment.
The commit must exist in this repository's history, so "0000000" or a commit
from another repository fails.

Usage:
    python tools/check_results.py [experiments/results]

Exit status is 1 if any file is missing a field or names an unknown commit.
"""

from __future__ import annotations

import glob
import json
import os
import subprocess
import sys

REQUIRED = ("run_id", "commit", "seed", "dataset", "metrics", "environment")


def commit_exists(commit: str) -> bool:
    return subprocess.run(["git", "cat-file", "-e", f"{commit}^{{commit}}"],
                          capture_output=True).returncode == 0


def main() -> int:
    results_dir = sys.argv[1] if len(sys.argv) > 1 else "experiments/results"
    paths = sorted(glob.glob(os.path.join(results_dir, "*.json")))
    if not paths:
        print(f"check-results: no result files in {results_dir}/. Nothing to check.")
        return 0

    problems = []
    for path in paths:
        try:
            with open(path) as fh:
                run = json.load(fh)
        except ValueError as exc:
            problems.append(f"{path}: not valid JSON ({exc})")
            continue
        for field in REQUIRED:
            if run.get(field) in (None, "", {}, []):
                problems.append(f"{path}: no {field}")
        commit = str(run.get("commit") or "")
        if commit and not commit_exists(commit):
            problems.append(f"{path}: commit {commit} is not in this repository")
        if run.get("run_id") and run["run_id"] != os.path.splitext(os.path.basename(path))[0]:
            problems.append(f"{path}: run_id {run['run_id']} does not match the file name")
        for name, value in (run.get("metrics") or {}).items():
            if not isinstance(value, (int, float)):
                problems.append(f"{path}: metric {name} is not a number")

    print(f"check-results: {len(paths)} result file(s) in {results_dir}/\n")
    for p in problems:
        print(f"  {p}")
    if problems:
        print(f"\n{len(problems)} problem(s). A number from an untraceable run cannot "
              "go in the paper.")
        return 1
    print("  every result names its commit, seed, data and environment")
    return 0


if __name__ == "__main__":
    sys.exit(main())

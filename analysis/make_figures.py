#!/usr/bin/env python3
"""Draw figures from experiments/results/*.json.

A figure in the paper must be drawn from a result file by this script. Asking
a model to produce a plot from a description produces an invented plot, which
NeurIPS warns about explicitly.

Usage:
    python analysis/make_figures.py
"""

from __future__ import annotations

import glob
import json
import os
import sys

RESULTS_DIR = "experiments/results"
OUT_DIR = "paper/figures"


def main() -> int:
    paths = sorted(glob.glob(os.path.join(RESULTS_DIR, "*.json")))
    if not paths:
        print(f"make_figures: no result files in {RESULTS_DIR}/. Nothing to draw.")
        return 0

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("make_figures: matplotlib is not installed, so no figures were drawn.")
        print("              pip install matplotlib, then run: make figures")
        return 0

    runs = []
    for path in paths:
        with open(path) as fh:
            try:
                runs.append(json.load(fh))
            except ValueError:
                print(f"make_figures: {path} is not valid JSON. Skipped.")

    metric = None
    for run in runs:
        for name, value in (run.get("metrics") or {}).items():
            if isinstance(value, (int, float)):
                metric = metric or name
    if metric is None:
        print("make_figures: no numeric metric found in the result files.")
        return 0

    labels = [str(r.get("run_id", "?")) for r in runs]
    values = [(r.get("metrics") or {}).get(metric, 0) for r in runs]

    os.makedirs(OUT_DIR, exist_ok=True)
    fig, ax = plt.subplots(figsize=(5.2, 3.1), dpi=200)
    ax.bar(labels, values, color="#1f6f6a", width=0.55)
    ax.set_ylabel(metric.replace("_", " "))
    ax.set_title(f"{metric.replace('_', ' ')} by run")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    fig.autofmt_xdate(rotation=20, ha="right")
    fig.tight_layout()
    out = os.path.join(OUT_DIR, "main_metric.pdf")
    fig.savefig(out)
    plt.close(fig)

    print(f"make_figures: wrote {out} from {len(runs)} run(s), metric '{metric}'")
    return 0


if __name__ == "__main__":
    sys.exit(main())

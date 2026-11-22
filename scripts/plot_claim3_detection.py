#!/usr/bin/env python3
"""Generate the Claim 3 figure from committed detection evidence."""

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "results/detect/summary.md"
CSV = ROOT / "results/detect/false_positive/summary.csv"
OUTPUT = ROOT / "results/figures/claim3_detection_matrix.png"

# Read positive detection evidence.
expected = {
    "heap_buffer_overflow": "heap-buffer-overflow",
    "stack_buffer_overflow": "stack-buffer-overflow",
    "global_buffer_overflow": "global-buffer-overflow",
    "use_after_free": "heap-use-after-free",
}

labels = {
    "heap_buffer_overflow": "Heap overflow",
    "stack_buffer_overflow": "Stack overflow",
    "global_buffer_overflow": "Global overflow",
    "use_after_free": "Heap use-after-free",
}

cases = {}

for line in SUMMARY.read_text().splitlines():
    if not line.strip().startswith("|"):
        continue

    fields = [
        s.strip().strip("`")
        for s in line.strip().strip("|").split("|")
    ]

    if len(fields) == 5 and fields[0] in expected:
        cases[fields[0]] = fields[1:]

if set(cases) != set(expected):
    raise ValueError("Missing positive detection evidence")

positive = []

for case, error_class in expected.items():
    plain, asan, reported, matched = cases[case]

    if plain != "exit 0":
        raise ValueError(f"Unexpected plain result: {case}")

    detected = (
        asan == "exit 1"
        and reported == error_class
        and matched.lower() == "yes"
    )

    positive.append(detected)

# Read clean-control evidence.
with CSV.open(newline="") as f:
    rows = list(csv.DictReader(f))

benchmarks = [
    "b1_malloc_text",
    "b2_pointer_chase",
    "b3_matmul",
    "b4_string_scan",
]

variants = ["base", "asan"]

expected_keys = {
    (b, v, str(r))
    for b in benchmarks
    for v in variants
    for r in range(1, 4)
}

actual_keys = {
    (r["benchmark"], r["variant"], r["run"])
    for r in rows
}

if len(rows) != 24 or actual_keys != expected_keys:
    raise ValueError("Incomplete or duplicate clean-control runs")

passed = np.zeros((4, 2), dtype=int)
totals = np.zeros((4, 2), dtype=int)

for i, benchmark in enumerate(benchmarks):
    for j, variant in enumerate(variants):
        group = [
            r for r in rows
            if r["benchmark"] == benchmark
            and r["variant"] == variant
        ]

        totals[i, j] = len(group)

        passed[i, j] = sum(
            r["exit_code"] == "0"
            and r["asan_reported"] == "no"
            for r in group
        )

asan_rows = [r for r in rows if r["variant"] == "asan"]

asan_reports = sum(
    r["asan_reported"] != "no"
    for r in asan_rows
)

normal_exits = sum(
    r["exit_code"] == "0"
    for r in rows
)

# Generate report figure.
fig, axes = plt.subplots(1, 2, figsize=(12, 5.5))

fig.suptitle(
    "AddressSanitizer Detection and Clean-Control Results",
    fontsize=15,
    fontweight="bold",
    y=0.96,
)

# Panel A: known memory errors.
ax = axes[0]

matrix = np.array([
    [0, int(result)]
    for result in positive
])

from matplotlib.colors import ListedColormap

ax.imshow(
    matrix,
    cmap=ListedColormap(["#E2E8F0", "#27865C"]),
    vmin=0,
    vmax=1,
    aspect="auto",
)

ax.set_xticks([0, 1], ["Plain", "ASan"])
ax.set_yticks(
    range(len(expected)),
    [labels[k] for k in expected],
)

ax.set_title("(a) Known memory errors", pad=14)

for i, result in enumerate(positive):
    ax.text(
        0, i, "Exit 0",
        ha="center", va="center"
    )

    ax.text(
        1, i,
        "Detected" if result else "Mismatch",
        ha="center", va="center",
        color="white" if result else "black",
        fontweight="bold",
    )

ax.set_xlabel(
    f"Expected classes detected: "
    f"{sum(positive)}/{len(positive)}",
    labelpad=14,
)

# Panel B: clean-control runs.
ax = axes[1]

ax.imshow(
    (passed == totals).astype(int),
    cmap=ListedColormap(["#F4A261", "#27865C"]),
    vmin=0,
    vmax=1,
    aspect="auto",
)

ax.set_xticks([0, 1], ["Base", "ASan"])
ax.set_yticks(range(4), benchmarks)
ax.set_title("(b) Clean-control runs", pad=14)

for i in range(4):
    for j in range(2):
        ax.text(
            j, i,
            f"{passed[i, j]}/{totals[i, j]} pass",
            ha="center", va="center",
            color="white",
            fontweight="bold",
        )

ax.set_xlabel(
    f"ASan reports: {asan_reports}/{len(asan_rows)}"
    f"; normal exits: {normal_exits}/{len(rows)}",
    labelpad=14,
)

for ax in axes:
    ax.tick_params(length=0)

    ax.set_xticks(
        np.arange(-0.5, 2, 1),
        minor=True
    )

    ax.set_yticks(
        np.arange(-0.5, 4, 1),
        minor=True
    )

    ax.grid(
        which="minor",
        color="white",
        linewidth=2
    )

    ax.tick_params(which="minor", length=0)

    for spine in ax.spines.values():
        spine.set_visible(False)

fig.text(
    0.5, 0.055,
    "One test per error class; three runs per "
    "benchmark and build variant.\n"
    "No error bars: categorical outcomes. "
    "No observed reports in these clean tests "
    "does not establish universal absence of false positives.",
    ha="center",
    fontsize=9,
)

fig.subplots_adjust(
    left=0.17,
    right=0.98,
    top=0.80,
    bottom=0.25,
    wspace=0.85,
)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUTPUT, dpi=200, bbox_inches="tight")
plt.close(fig)

print(f"Detected error classes: {sum(positive)}/{len(positive)}")
print(f"Clean-control runs: {len(rows)}")
print(f"Normal exits: {normal_exits}/{len(rows)}")
print(f"ASan reports: {asan_reports}/{len(asan_rows)}")
print(f"Wrote {OUTPUT.relative_to(ROOT)}")

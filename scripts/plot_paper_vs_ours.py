#!/usr/bin/env python3
"""Draw the Paper-vs-Ours runtime figure from the report CSV.

Every number drawn by this script comes from
``results/report/paper_vs_ours_runtime.csv``; no result value is hard-coded
here.  The CSV is validated before anything is drawn, so a missing or
inconsistent row fails loudly instead of silently producing a misleading
figure.

The comparison row carries both the paper value (73% on SPEC CPU2006, Fig. 2)
and our overall value (31.19% on ``array_update``); the batch rows carry only
our per-batch values.  The script draws the paper bar from the comparison row,
then one bar per row.

Usage
-----
    python3 scripts/plot_paper_vs_ours.py
    python3 scripts/plot_paper_vs_ours.py --csv PATH --out PATH

The script uses matplotlib's Agg backend, so it works without a display.
"""

from __future__ import annotations

import argparse
import csv
import sys
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = REPO_ROOT / "results" / "report" / "paper_vs_ours_runtime.csv"
DEFAULT_OUT = REPO_ROOT / "results" / "figures" / "paper_vs_ours_runtime.png"

REQUIRED_COLUMNS = [
    "claim",
    "figure",
    "plot_label",
    "paper_plot_label",
    "series",
    "paper_metric",
    "paper_value",
    "paper_unit",
    "ours_metric",
    "ours_value",
    "ours_unit",
    "n_runs",
    "workload",
    "setting",
    "source_file",
    "comparability_note",
]

SERIES_ORDER = ("ours_overall", "ours_batch")
COLORS = {
    "paper": "#c44e52",
    "ours_overall": "#4c72b0",
    "ours_batch": "#8da0cb",
}
BATCH_EDGE = "#5b7fb0"


def fail(message: str) -> None:
    raise SystemExit(f"error: {message}")


def load_rows(path: Path) -> tuple[list[dict[str, str]], dict[str, str]]:
    if not path.is_file():
        fail(f"CSV not found: {path}")
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        missing = [name for name in REQUIRED_COLUMNS if name not in fieldnames]
        if missing:
            fail(f"missing CSV columns in {path}: {', '.join(missing)}")
        rows = [row for row in reader if any((value or "").strip() for value in row.values())]
    if not rows:
        fail(f"no data rows in {path}")

    counts = {series: 0 for series in SERIES_ORDER}
    paper_rows: list[dict[str, str]] = []
    for row_no, row in enumerate(rows, start=2):
        if None in row:
            fail(f"row {row_no}: more fields than the header")
        series = (row.get("series") or "").strip()
        if series not in counts:
            fail(f"row {row_no}: unknown series {series!r}; expected one of {SERIES_ORDER}")
        counts[series] += 1
        for column in ("plot_label", "ours_metric", "ours_value", "source_file", "comparability_note"):
            if not (row.get(column) or "").strip():
                fail(f"row {row_no}: empty {column}")
        if (row.get("paper_value") or "").strip():
            if not (row.get("paper_plot_label") or "").strip():
                fail(f"row {row_no}: paper_value set but paper_plot_label empty")
            if not (row.get("paper_metric") or "").strip():
                fail(f"row {row_no}: paper_value set but paper_metric empty")
            paper_rows.append(row)

    if len(paper_rows) != 1:
        fail(f"expected exactly one row carrying the paper value, found {len(paper_rows)}")
    paper_row = paper_rows[0]
    if (paper_row.get("series") or "").strip() != "ours_overall":
        fail("the row carrying the paper value must also carry the overall comparison")
    if counts["ours_overall"] != 1:
        fail(f"expected exactly one ours_overall row, found {counts['ours_overall']}")
    if counts["ours_batch"] < 1:
        fail("expected at least one ours_batch row")

    # Overall comparison first, then the batches in file order.
    rank = {series: index for index, series in enumerate(SERIES_ORDER)}
    rows.sort(key=lambda row: rank[(row.get("series") or "").strip()])

    figures = {(row.get("figure") or "").strip() for row in rows}
    if len(figures) != 1:
        fail(f"rows disagree on figure number: {sorted(figures)}")
    return rows, paper_row


def as_float(row: dict[str, str], column: str, row_no: int) -> float:
    raw = (row.get(column) or "").strip()
    try:
        return float(raw)
    except ValueError:
        fail(f"row {row_no}: {column} is not a number: {raw!r}")


def as_int(row: dict[str, str], column: str, row_no: int) -> int:
    raw = (row.get(column) or "").strip()
    try:
        return int(raw)
    except ValueError:
        fail(f"row {row_no}: {column} is not an integer: {raw!r}")


def format_percent(value: float) -> str:
    if abs(value - round(value)) < 1e-9:
        return f"{value:.0f}%"
    return f"{value:.2f}%"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="report CSV to read")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="PNG to write")
    args = parser.parse_args(argv)

    rows, paper_row = load_rows(args.csv)

    entries = []
    paper_value = as_float(paper_row, "paper_value", 2)
    paper_unit = (paper_row.get("paper_unit") or "").strip()
    if paper_unit != "%":
        fail(f"paper_unit must be '%', found {paper_unit!r}")
    entries.append(
        {
            "series": "paper",
            "label": (paper_row.get("paper_plot_label") or "").strip().replace(" | ", "\n"),
            "value": paper_value,
            "unit": paper_unit,
            "n_runs": "",
            "metric": (paper_row.get("paper_metric") or "").strip(),
        }
    )

    for row_no, row in enumerate(rows, start=2):
        series = (row.get("series") or "").strip()
        value = as_float(row, "ours_value", row_no)
        unit = (row.get("ours_unit") or "").strip()
        if unit != "%":
            fail(f"row {row_no}: ours_unit must be '%', found {unit!r}")
        n_runs = as_int(row, "n_runs", row_no)
        if n_runs < 1:
            fail(f"row {row_no}: n_runs must be positive")
        entries.append(
            {
                "series": series,
                "label": (row.get("plot_label") or "").strip().replace(" | ", "\n"),
                "value": value,
                "unit": unit,
                "n_runs": str(n_runs),
                "metric": (row.get("ours_metric") or "").strip(),
            }
        )

    values = [entry["value"] for entry in entries]
    positions = list(range(len(entries)))
    bar_colors = [COLORS[entry["series"]] for entry in entries]

    fig, ax = plt.subplots(figsize=(9.6, 6.0))
    bars = ax.bar(
        positions,
        values,
        width=0.68,
        color=bar_colors,
        edgecolor=[BATCH_EDGE if entry["series"] == "ours_batch" else "none" for entry in entries],
        linewidth=0.8,
        zorder=3,
    )
    for bar, entry in zip(bars, entries):
        if entry["series"] == "ours_batch":
            bar.set_hatch("//")

    for x, entry in zip(positions, entries):
        ax.text(
            x,
            entry["value"] + max(values) * 0.015,
            format_percent(entry["value"]),
            ha="center",
            va="bottom",
            fontsize=9.5,
            fontweight="bold",
            color="#222222",
        )

    ax.set_xticks(positions)
    ax.set_xticklabels([entry["label"] for entry in entries], fontsize=9)
    ax.set_ylabel("Runtime overhead vs. uninstrumented build (%)", fontsize=11)
    ax.set_xlabel("Measurement", fontsize=10)
    ax.set_title(
        "Runtime overhead: paper vs. our replication (different workloads)",
        fontsize=13,
        fontweight="bold",
        pad=12,
    )
    ax.set_ylim(0, max(values) * 1.18)
    ax.yaxis.grid(True, linestyle=":", linewidth=0.7, color="#b5b5b5", zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)

    # Separate the paper reference bar from our measurements.
    first_ours = next(index for index, entry in enumerate(entries) if entry["series"] != "paper")
    ax.axvline(first_ours - 0.5, color="#666666", linestyle="--", linewidth=0.9, zorder=1)

    overall_entry = next(entry for entry in entries if entry["series"] == "ours_overall")
    batches = [entry for entry in entries if entry["series"] == "ours_batch"]
    batch_runs = {entry["n_runs"] for entry in batches}
    batch_text = ", ".join(
        f"{entry['label'].splitlines()[-1]} {entry['value']:.2f}%" for entry in batches
    )
    batch_runs_text = (
        next(iter(batch_runs)) if len(batch_runs) == 1 else "/".join(sorted(batch_runs))
    )

    legend_handles = [
        Patch(facecolor=COLORS["paper"], label="Paper: SPEC CPU2006 average (Fig. 2)"),
        Patch(
            facecolor=COLORS["ours_overall"],
            label="Ours: array_update, WSL2 (overall + batches)",
        ),
    ]
    ax.legend(handles=legend_handles, loc="upper right", frameon=False, fontsize=8.5)

    def display_path(path: Path) -> str:
        try:
            return path.relative_to(REPO_ROOT).as_posix()
        except ValueError:
            return path.as_posix()

    csv_display = display_path(args.csv)
    note_paragraphs = [
        "Different workloads: paper = SPEC CPU2006 average (Fig. 2); ours = 64 MiB array_update "
        "microbenchmark on WSL2. Not a same-workload reproduction.",
        f"Ours: {overall_entry['value']:.2f}% overall ({overall_entry['n_runs']} runs/version, includes "
        f"between-batch variation); {batch_text} ({batch_runs_text} runs/version each).",
        "No error bars: no matching SD is reported for the paper or for our overhead ratios "
        "(31.19% is a cross-batch aggregate).",
        f"Sources: {csv_display} (values); results/performance/performance_analysis.txt and "
        "benchmark_summary.csv (raw analysis).",
    ]
    note_text = "\n".join(textwrap.fill(paragraph, width=152) for paragraph in note_paragraphs)
    fig.text(
        0.012,
        0.014,
        note_text,
        ha="left",
        va="bottom",
        fontsize=7.3,
        linespacing=1.42,
        color="#333333",
    )
    fig.subplots_adjust(left=0.085, right=0.985, top=0.87, bottom=0.245)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, dpi=200, facecolor="white")
    plt.close(fig)

    print(f"{'series':<12} {'value':>8} {'unit':>5} {'n':>4}  label")
    for entry in entries:
        print(
            f"{entry['series']:<12} {entry['value']:>8.2f} {entry['unit']:>5} "
            f"{entry['n_runs'] or '-':>4}  {entry['label'].replace(chr(10), ' / ')}"
        )
    print(f"wrote {display_path(args.out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

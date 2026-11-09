#!/usr/bin/env python3
"""Parse the run matrix logs into the tables the report needs.

Reads the RESULT lines written by scripts/run_experiments.sh and produces

    results/summary/results.csv    one row per (benchmark, configuration, metric)
    results/summary/summary.md     Paper vs. Ours tables, mean +/- std, ratios
    results/summary/figures/*.png  optional, needs matplotlib

Usage:
    python3 scripts/parse_results.py
    python3 scripts/parse_results.py --log results/logs/20261105T101500Z/runs.log
    python3 scripts/parse_results.py --plot
    python3 scripts/parse_results.py --paper-slowdown 73 --paper-mem 3.37

No number in summary.md is invented: every value comes from a RESULT line and
the source log is recorded next to it, which is what the traceability criterion
asks for.
"""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

# Paper values, USENIX ATC 2012, Section 4 (SPEC CPU2006, 64-bit, clang -O2).
PAPER_SLOWDOWN_PCT = 73.0   # Figure 2, average over CPU2006
PAPER_MEMORY_RATIO = 3.37   # Table 1, average VmPeak increase


@dataclass
class Run:
    bench: str
    config: str
    run: str
    wall_ms: float
    vmpeak_kb: float
    vmhwm_kb: float
    exit_code: int


def find_log(explicit: str | None) -> Path:
    if explicit:
        path = Path(explicit)
        if not path.is_file():
            sys.exit(f"no such log: {path}")
        return path
    root = Path("results/logs")
    candidates = sorted(root.glob("*/runs.log"))
    if not candidates:
        sys.exit(
            "no results/logs/*/runs.log found -- run scripts/run_experiments.sh first"
        )
    return candidates[-1]


def parse_log(path: Path) -> list[Run]:
    runs: list[Run] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.startswith("RESULT "):
            continue
        fields: dict[str, str] = {}
        for token in line.split()[1:]:
            if "=" not in token:
                continue
            key, value = token.split("=", 1)
            fields[key] = value
        try:
            runs.append(
                Run(
                    bench=fields["bench"],
                    config=fields["config"],
                    run=fields["run"],
                    wall_ms=float(fields["wall_ms"]),
                    vmpeak_kb=float(fields["vmpeak_kb"]),
                    vmhwm_kb=float(fields["vmhwm_kb"]),
                    exit_code=int(fields.get("exit", "0")),
                )
            )
        except KeyError as exc:
            print(f"warning: {path}:{lineno}: missing field {exc}", file=sys.stderr)
    if not runs:
        sys.exit(f"{path}: no RESULT lines found")
    return runs


def mean_std(values: list[float]) -> tuple[float, float]:
    if len(values) == 1:
        return values[0], 0.0
    return statistics.mean(values), statistics.stdev(values)


def collect(runs: list[Run]) -> tuple[dict, dict]:
    grouped: dict[tuple[str, str], dict[str, list[float]]] = defaultdict(
        lambda: {"wall_ms": [], "vmpeak_kb": [], "vmhwm_kb": []}
    )
    failures: dict[tuple[str, str], list[str]] = defaultdict(list)
    for run in runs:
        key = (run.bench, run.config)
        grouped[key]["wall_ms"].append(run.wall_ms)
        grouped[key]["vmpeak_kb"].append(run.vmpeak_kb)
        grouped[key]["vmhwm_kb"].append(run.vmhwm_kb)
        if run.exit_code != 0:
            failures[key].append(f"{run.run} (exit {run.exit_code})")
    return grouped, failures


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--log", help="runs.log to parse (default: newest)")
    ap.add_argument("--out", default="results/summary", help="output directory")
    ap.add_argument("--plot", action="store_true", help="also render figures")
    ap.add_argument("--paper-slowdown", type=float, default=PAPER_SLOWDOWN_PCT)
    ap.add_argument("--paper-mem", type=float, default=PAPER_MEMORY_RATIO)
    args = ap.parse_args()

    log_path = find_log(args.log)
    runs = parse_log(log_path)
    grouped, failures = collect(runs)

    benches = sorted({b for b, _ in grouped})
    outdir = Path(args.out)
    (outdir / "figures").mkdir(parents=True, exist_ok=True)

    rows = []
    for bench in benches:
        for config in ("base", "asan"):
            data = grouped.get((bench, config))
            if not data:
                continue
            for metric, unit in (
                ("wall_ms", "ms"),
                ("vmpeak_kb", "kB"),
                ("vmhwm_kb", "kB"),
            ):
                mean, std = mean_std(data[metric])
                rows.append(
                    {
                        "benchmark": bench,
                        "config": config,
                        "metric": metric,
                        "mean": f"{mean:.3f}",
                        "std": f"{std:.3f}",
                        "n": len(data[metric]),
                        "unit": unit,
                        "source_log": str(log_path),
                    }
                )

    csv_path = outdir / "results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    # Per-benchmark overhead.
    table = []
    for bench in benches:
        base = grouped.get((bench, "base"))
        asan = grouped.get((bench, "asan"))
        if not base or not asan:
            continue
        b_wall, b_wall_sd = mean_std(base["wall_ms"])
        a_wall, a_wall_sd = mean_std(asan["wall_ms"])
        b_peak, b_peak_sd = mean_std(base["vmpeak_kb"])
        a_peak, a_peak_sd = mean_std(asan["vmpeak_kb"])
        b_rss, _ = mean_std(base["vmhwm_kb"])
        a_rss, _ = mean_std(asan["vmhwm_kb"])
        slowdown = (a_wall - b_wall) / b_wall * 100.0 if b_wall else float("nan")
        table.append(
            {
                "bench": bench,
                "n": len(asan["wall_ms"]),
                "base_wall": b_wall,
                "base_wall_sd": b_wall_sd,
                "asan_wall": a_wall,
                "asan_wall_sd": a_wall_sd,
                "slowdown_pct": slowdown,
                "base_peak": b_peak,
                "base_peak_sd": b_peak_sd,
                "asan_peak": a_peak,
                "asan_peak_sd": a_peak_sd,
                "mem_ratio": (a_peak / b_peak) if b_peak else float("nan"),
                "rss_ratio": (a_rss / b_rss) if b_rss else float("nan"),
            }
        )

    slow = [row["slowdown_pct"] for row in table if row["slowdown_pct"] == row["slowdown_pct"]]
    mem = [row["mem_ratio"] for row in table if row["mem_ratio"] == row["mem_ratio"]]
    avg_slow = statistics.mean(slow) if slow else float("nan")
    avg_mem = statistics.mean(mem) if mem else float("nan")

    md: list[str] = []
    md.append("# Parsed results")
    md.append("")
    md.append(f"- source log: `{log_path}`")
    md.append(f"- benchmarks: {len(benches)}, configurations: base / asan")
    md.append("- wall time around fork+exec, VmPeak and VmHWM read from /proc/<pid>/status")
    md.append("")
    md.append("## Per-benchmark measurements (mean +/- std)")
    md.append("")
    md.append("| Benchmark | n | base wall (ms) | asan wall (ms) | slowdown | base VmPeak (kB) | asan VmPeak (kB) | mem ratio |")
    md.append("|---|---|---|---|---|---|---|---|")
    for row in table:
        md.append(
            "| {bench} | {n} | {b:.1f} +/- {bs:.1f} | {a:.1f} +/- {asd:.1f} | {s:+.1f}% "
            "| {bp:.0f} +/- {bps:.0f} | {ap:.0f} +/- {aps:.0f} | {m:.2f}x |".format(
                bench=row["bench"],
                n=row["n"],
                b=row["base_wall"],
                bs=row["base_wall_sd"],
                a=row["asan_wall"],
                asd=row["asan_wall_sd"],
                s=row["slowdown_pct"],
                bp=row["base_peak"],
                bps=row["base_peak_sd"],
                ap=row["asan_peak"],
                aps=row["asan_peak_sd"],
                m=row["mem_ratio"],
            )
        )
    md.append("")
    md.append("## Paper vs. ours")
    md.append("")
    md.append(
        "The aggregate below is an unweighted mean over the benchmarks above. It is "
        "**not** directly comparable to the paper's average: the paper averages over "
        "SPEC CPU2006, this replication averages over four small benchmarks. Both the "
        "difference and its likely cause belong in the analysis section."
    )
    md.append("")
    md.append("| Metric | Paper (ATC 2012, SPEC CPU2006) | Ours (this run) | Absolute gap | Relative gap |")
    md.append("|---|---|---|---|---|")
    md.append(
        f"| Average slowdown | {args.paper_slowdown:.1f}% | {avg_slow:+.1f}% | "
        f"{avg_slow - args.paper_slowdown:+.1f} pp | "
        f"{(avg_slow / args.paper_slowdown - 1.0) * 100:+.1f}% |"
    )
    md.append(
        f"| Average memory increase (VmPeak) | {args.paper_mem:.2f}x | {avg_mem:.2f}x | "
        f"{avg_mem - args.paper_mem:+.2f}x | "
        f"{(avg_mem / args.paper_mem - 1.0) * 100:+.1f}% |"
    )
    md.append("")

    if failures:
        md.append("## Failed runs")
        md.append("")
        md.append("These runs exited non-zero. An asan run that aborts has detected a bug in the benchmark itself, so its timing must not be used.")
        md.append("")
        for (bench, config), items in sorted(failures.items()):
            md.append(f"- {bench} / {config}: {', '.join(items)}")
        md.append("")
    else:
        md.append("All runs exited 0.")

    md_path = outdir / "summary.md"
    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("\n".join(md))
    print(f"\nwrote {csv_path}\nwrote {md_path}")

    if args.plot:
        try:
            import matplotlib

            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
        except ImportError:
            print("matplotlib not available; skipping figures", file=sys.stderr)
            return 0
        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        names = [row["bench"] for row in table]
        axes[0].bar(names, [row["slowdown_pct"] for row in table], color="#4c72b0")
        axes[0].axhline(args.paper_slowdown, color="#c44e52", linestyle="--", label="paper average (73%)")
        axes[0].set_ylabel("slowdown (%)")
        axes[0].set_title("Runtime overhead")
        axes[0].legend()
        axes[1].bar(names, [row["mem_ratio"] for row in table], color="#55a868")
        axes[1].axhline(args.paper_mem, color="#c44e52", linestyle="--", label="paper average (3.37x)")
        axes[1].set_ylabel("VmPeak ratio (asan / base)")
        axes[1].set_title("Memory overhead")
        axes[1].legend()
        for ax in axes:
            ax.tick_params(axis="x", labelrotation=20)
        fig.tight_layout()
        fig.savefig(outdir / "figures" / "overhead.png", dpi=150)
        print(f"wrote {outdir / 'figures' / 'overhead.png'}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

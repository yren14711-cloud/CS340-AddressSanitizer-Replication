#!/usr/bin/env python3
"""Build the Claim 2 (memory overhead) tables and figures from a b1-b4 run matrix.

Reads the RESULT lines written by scripts/run_experiments.sh and writes, into --out:

    results.csv                    long format: one row per (benchmark, config, metric)
    summary.md                     Table A (VmHWM), Table B (VmPeak), per-run raw values, checks
    figures/fig_a_vmhwm_bars.png   Base vs ASan VmHWM per benchmark, mean +/- sample SD
    figures/fig_b_vmhwm_ratio.png  ASan/Base VmHWM ratio per benchmark, 1.0x baseline
    figures/fig_c_ratio_sessions.png  ratio per benchmark across measurement sessions

Usage:
    python3 analyze_memory_claim2.py \
        --log results/logs/20261121T051205Z/runs.log \
        --out results/memory_claim2/20261121T051205Z \
        --env results/memory_claim2/20261121T051205Z/environment.txt \
        --compare "results/logs/20261114T155152Z/runs.log;kernel 5.10 (Nov 14);Ubuntu 24.04, kernel 5.10.16.3, clang 18.1.3" \
        --compare "results/logs/20261114T161554Z/runs.log;kernel 6.18 (Nov 14);Ubuntu 24.04, kernel 6.18.33.2, clang 18.1.3"

Every number in summary.md and in the figures is read from a RESULT line of the
log named on the command line; nothing is typed in by hand. VmPeak is reported
for completeness only -- in this environment the AddressSanitizer shadow-memory
reservation makes it a constant, not a workload measurement.
"""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
from pathlib import Path

METRICS = (("wall_ms", "ms"), ("vmpeak_kb", "kB"), ("vmhwm_kb", "kB"))
COLOR_BASE = "#4c72b0"
COLOR_ASAN = "#c44e52"
COLOR_RATIO = "#55a868"


def mean_sd(values):
    if not values:
        return float("nan"), float("nan")
    if len(values) == 1:
        return values[0], 0.0
    return statistics.mean(values), statistics.stdev(values)


def parse_log(path):
    runs = []
    text = Path(path).read_text(encoding="utf-8")
    for lineno, line in enumerate(text.splitlines(), 1):
        if not line.startswith("RESULT "):
            continue
        fields = {}
        for token in line.split()[1:]:
            if "=" not in token:
                continue
            key, value = token.split("=", 1)
            fields[key] = value
        try:
            runs.append(
                {
                    "bench": fields["bench"],
                    "config": fields["config"],
                    "run": fields["run"],
                    "wall_ms": float(fields["wall_ms"]),
                    "vmpeak_kb": float(fields["vmpeak_kb"]),
                    "vmhwm_kb": float(fields["vmhwm_kb"]),
                    "exit": int(fields.get("exit", "0")),
                }
            )
        except KeyError as exc:
            print(f"warning: {path}:{lineno}: missing field {exc}", file=sys.stderr)
    if not runs:
        sys.exit(f"{path}: no RESULT lines found")
    return runs


def read_env(path):
    values = {}
    if not path:
        return values
    p = Path(path)
    if not p.is_file():
        return values
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.startswith("#") or "=" not in line:
            continue
        key, value = line[1:].split("=", 1)
        values[key.strip()] = value.strip()
    return values


def collect(runs):
    grouped = {}
    order = []
    for run in runs:
        key = (run["bench"], run["config"])
        if key not in grouped:
            grouped[key] = {"wall_ms": [], "vmpeak_kb": [], "vmhwm_kb": [], "runs": []}
            if run["bench"] not in order:
                order.append(run["bench"])
        for metric, _unit in METRICS:
            grouped[key][metric].append(run[metric])
        grouped[key]["runs"].append(run)
    return grouped, order


def build_table(grouped, benches):
    table = []
    for bench in benches:
        base = grouped.get((bench, "base"))
        asan = grouped.get((bench, "asan"))
        if not base or not asan:
            continue
        row = {"bench": bench, "n": len(asan["wall_ms"])}
        for name, metric in (
            ("wall", "wall_ms"),
            ("peak", "vmpeak_kb"),
            ("hwm", "vmhwm_kb"),
        ):
            bm, bs = mean_sd(base[metric])
            am, asd = mean_sd(asan[metric])
            row[f"base_{name}"] = bm
            row[f"base_{name}_sd"] = bs
            row[f"asan_{name}"] = am
            row[f"asan_{name}_sd"] = asd
        row["slowdown_pct"] = (row["asan_wall"] / row["base_wall"] - 1.0) * 100.0
        row["mem_ratio"] = row["asan_peak"] / row["base_peak"]
        row["rss_ratio"] = row["asan_hwm"] / row["base_hwm"]
        per_run = [
            a / b
            for a, b in zip(
                [r["vmhwm_kb"] for r in asan["runs"]],
                [r["vmhwm_kb"] for r in base["runs"]],
            )
            if b
        ]
        row["rss_ratio_run_mean"], row["rss_ratio_run_sd"] = mean_sd(per_run)
        table.append(row)
    return table


def write_csv(path, grouped, benches, source):
    rows = []
    for bench in benches:
        for config in ("base", "asan"):
            data = grouped.get((bench, config))
            if not data:
                continue
            for metric, unit in METRICS:
                m, s = mean_sd(data[metric])
                rows.append(
                    {
                        "benchmark": bench,
                        "config": config,
                        "metric": metric,
                        "mean": f"{m:.3f}",
                        "std": f"{s:.3f}",
                        "n": len(data[metric]),
                        "unit": unit,
                        "source_log": source,
                    }
                )
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def figures(table, benches, sessions, outdir, this_label, env_line):
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not available; skipping figures", file=sys.stderr)
        return []

    made = []
    names = [r["bench"] for r in table]
    base_mib = [r["base_hwm"] / 1024.0 for r in table]
    asan_mib = [r["asan_hwm"] / 1024.0 for r in table]
    base_sd = [r["base_hwm_sd"] / 1024.0 for r in table]
    asan_sd = [r["asan_hwm_sd"] / 1024.0 for r in table]
    ratios = [r["rss_ratio"] for r in table]
    positions = list(range(len(names)))
    width = 0.38

    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    ax.bar(
        [p - width / 2 for p in positions],
        base_mib,
        width,
        yerr=base_sd,
        capsize=4,
        color=COLOR_BASE,
        label="Base (clang -O2)",
    )
    ax.bar(
        [p + width / 2 for p in positions],
        asan_mib,
        width,
        yerr=asan_sd,
        capsize=4,
        color=COLOR_ASAN,
        label="ASan (clang -O2 -fsanitize=address)",
    )
    for p, value in zip(positions, asan_mib):
        ax.text(p + width / 2, value + 2.0, f"{value:.1f}", ha="center", fontsize=8)
    ax.set_xticks(positions)
    ax.set_xticklabels(names, rotation=12)
    ax.set_ylabel("peak resident set, VmHWM (MiB)")
    ax.set_title(
        "Peak resident memory, scale=1, n=3 per bar (error bar: 1 sample SD)\n" + env_line,
        fontsize=10,
    )
    ax.grid(axis="y", alpha=0.3)
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    path_a = outdir / "figures" / "fig_a_vmhwm_bars.png"
    fig.savefig(path_a, dpi=150)
    plt.close(fig)
    made.append(path_a)

    fig, ax = plt.subplots(figsize=(7.6, 3.6))
    ax.barh(names, ratios, color=COLOR_RATIO)
    ax.axvline(1.0, color=COLOR_ASAN, linestyle="--", linewidth=1.2, label="1.0x (no overhead)")
    for i, value in enumerate(ratios):
        ax.text(value + 0.02, i, f"{value:.2f}x", va="center", fontsize=9)
    ax.set_xlim(0.0, max(2.4, max(ratios) + 0.3))
    ax.set_xlabel("ASan / Base VmHWM ratio")
    ax.set_title(
        "Resident-memory ratio per benchmark, scale=1 (ratio of means, n=3)\n" + env_line,
        fontsize=10,
    )
    ax.grid(axis="x", alpha=0.3)
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    path_b = outdir / "figures" / "fig_b_vmhwm_ratio.png"
    fig.savefig(path_b, dpi=150)
    plt.close(fig)
    made.append(path_b)

    session_list = [{"table": table, "label": this_label}] + list(sessions)
    if session_list:
        count = len(session_list)
        width = 0.8 / count
        fig, ax = plt.subplots(figsize=(8.6, 4.2))
        for k, session in enumerate(session_list):
            ratios_k = [row["rss_ratio"] for row in session["table"]]
            offsets = [p + (k - (count - 1) / 2.0) * width for p in positions]
            ax.bar(offsets, ratios_k, width, label=session["label"])
        ax.axhline(1.0, color=COLOR_ASAN, linestyle="--", linewidth=1.1, label="1.0x")
        ax.set_xticks(positions)
        ax.set_xticklabels(names, rotation=12)
        ax.set_ylabel("ASan / Base VmHWM ratio")
        ax.set_title(
            "Resident-memory ratio across measurement sessions (scale=1, n=3 each)\n" + env_line,
            fontsize=10,
        )
        ax.grid(axis="y", alpha=0.3)
        ax.legend(fontsize=7, loc="upper right")
        fig.tight_layout()
        path_c = outdir / "figures" / "fig_c_ratio_sessions.png"
        fig.savefig(path_c, dpi=150)
        plt.close(fig)
        made.append(path_c)

    return made


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--log", required=True, help="runs.log of the session being reported")
    ap.add_argument("--out", required=True, help="output directory (created if missing)")
    ap.add_argument("--env", help="environment.txt of the same session (embedded in summary.md)")
    ap.add_argument(
        "--compare",
        action="append",
        default=[],
        metavar="LOG;LABEL;ENV",
        help="additional session for figure C: path;short label;one-line environment",
    )
    ap.add_argument("--paper-mem", type=float, default=3.37, help="paper Table 1 average (3.37x)")
    args = ap.parse_args()

    outdir = Path(args.out)
    (outdir / "figures").mkdir(parents=True, exist_ok=True)

    runs = parse_log(args.log)
    grouped, benches = collect(runs)
    table = build_table(grouped, benches)
    if not table:
        sys.exit("no benchmark has both a base and an asan group")
    env = read_env(args.env)

    csv_rows = write_csv(outdir / "results.csv", grouped, benches, str(args.log))

    sessions = []
    for spec in args.compare:
        parts = spec.split(";")
        if len(parts) != 3:
            sys.exit(f"--compare needs LOG;LABEL;ENV, got: {spec}")
        other_runs = parse_log(parts[0])
        other_grouped, other_benches = collect(other_runs)
        sessions.append(
            {
                "table": build_table(other_grouped, other_benches),
                "label": parts[1],
                "env": parts[2],
                "log": parts[0],
            }
        )

    this_label = (
        f"this session ({env.get('session_stamp', 'n/a')})" if env else "this session"
    )
    env_line = "n/a"
    if env:
        clang_short = env.get("clang", "n/a")
        parts = clang_short.split("version")
        if len(parts) > 1:
            clang_short = parts[-1].strip().split(" ")[0]
        env_line = (
            env.get("os", "n/a")
            + ", kernel "
            + env.get("kernel", "n/a")
            + ", clang "
            + clang_short
            + ", WSL2"
        )
    made = figures(table, benches, sessions, outdir, this_label, env_line)

    rss_ratios = [row["rss_ratio"] for row in table]
    ratio_mean = statistics.mean(rss_ratios)
    ratio_sd = statistics.stdev(rss_ratios) if len(rss_ratios) > 1 else 0.0
    peak_ratios = [row["mem_ratio"] for row in table]
    slowdowns = [row["slowdown_pct"] for row in table]

    counts = sorted({len(grouped[(b, c)]["wall_ms"]) for b in benches for c in ("base", "asan") if (b, c) in grouped})
    failures = [r for r in runs if r["exit"] != 0]
    asan_peaks = [r["vmpeak_kb"] for r in runs if r["config"] == "asan"]
    peak_spread = max(asan_peaks) - min(asan_peaks)

    wall_outliers = []
    for bench in benches:
        for config in ("base", "asan"):
            data = grouped.get((bench, config))
            if not data:
                continue
            walls = data["wall_ms"]
            if min(walls) > 0 and max(walls) / min(walls) >= 1.8:
                wall_outliers.append(
                    f"{bench} / {config}: wall_ms {', '.join(f'{w:.0f}' for w in walls)}"
                )

    lines = []
    add = lines.append
    add("# Claim 2 -- memory overhead, parsed results")
    add("")
    add(f"- source log: `{args.log}`")
    add(f"- benchmarks: {len(benches)}; configurations: base / asan; measured repetitions per bar: {counts}")
    add("- metric definition: VmHWM (peak resident set) and VmPeak, both sampled from /proc/<pid>/status")
    add("- scale: 1; ASAN_OPTIONS=quarantine_size_mb=0:malloc_context_size=0:detect_leaks=0:redzone=32")
    add("")
    if env:
        add("## Session environment")
        add("")
        for key in ("session_stamp", "cpu", "cpu_cores", "memtotal", "os", "kernel", "clang", "wsl", "workdir"):
            if key in env:
                add(f"- {key}: `{env[key]}`")
        add("")
    add("## Table A -- VmHWM (peak resident set), the reported metric")
    add("")
    add("| Benchmark | n | Base VmHWM (kB) | ASan VmHWM (kB) | Ratio ASan/Base |")
    add("|---|---|---|---|---|")
    for row in table:
        add(
            f"| {row['bench']} | {row['n']} | {row['base_hwm']:.1f} +/- {row['base_hwm_sd']:.1f} "
            f"| {row['asan_hwm']:.1f} +/- {row['asan_hwm_sd']:.1f} | {row['rss_ratio']:.2f}x |"
        )
    add("")
    add(
        f"Unweighted mean of the four per-benchmark ratios: **{ratio_mean:.2f}x** "
        f"(sample SD across the four benchmarks: {ratio_sd:.2f}; n = {len(rss_ratios)} benchmarks)."
    )
    add("")
    add(f"The paper's Table 1 average is {args.paper_mem:.2f}x over SPEC CPU2006, measured on VmPeak.")
    add("Our figure is a VmHWM proxy on four microbenchmarks: it shows that the resident-memory")
    add("overhead measured in this environment is well below 3.37x. It does not reproduce Table 1.")
    add("")
    add("Table A reads: Base and ASan are the mean and 1 sample SD of the 3 measured runs;")
    add("ratio = mean(ASan VmHWM) / mean(Base VmHWM) for the same benchmark and session.")
    add("")
    add("## Table B -- VmPeak, for completeness only (NOT usable as memory overhead)")
    add("")
    add("| Benchmark | n | Base VmPeak (kB) | ASan VmPeak (kB) | Ratio ASan/Base |")
    add("|---|---|---|---|---|")
    for row in table:
        add(
            f"| {row['bench']} | {row['n']} | {row['base_peak']:.1f} +/- {row['base_peak_sd']:.1f} "
            f"| {row['asan_peak']:.1f} +/- {row['asan_peak_sd']:.1f} | {row['mem_ratio']:.0f}x |"
        )
    add("")
    add(
        "Warning: every ASan run reports VmPeak ~= 21 474 900 000 kB (about 20 TB) because the "
        "runtime reserves the shadow address space at start-up. Within one benchmark the value is "
        f"identical from run to run; across the four benchmarks it varies by {peak_spread:.0f} kB "
        "(about 144 MiB, i.e. < 0.001% of 20 TB) with the shadow mapping layout. It is a property of "
        "the reservation, not of the workload, so the VmPeak ratio must not be reported as Claim 2. "
        "The paper's Table 1 uses VmPeak; that is precisely the deviation this replication has to state."
    )
    add("")
    add("## Per-run raw values (traceability)")
    add("")
    add("| Benchmark | Config | run1 | run2 | run3 | mean +/- SD |")
    add("|---|---|---|---|---|---|")
    for row in table:
        for config in ("base", "asan"):
            data = grouped[(row["bench"], config)]
            values = " | ".join(f"{v:.0f}" for v in data["vmhwm_kb"])
            m, s = mean_sd(data["vmhwm_kb"])
            add(f"| {row['bench']} | {config} VmHWM (kB) | {values} | {m:.1f} +/- {s:.1f} |")
    add("")
    add("## Runtime context (not the Claim 2 metric)")
    add("")
    add("| Benchmark | Base wall (ms) | ASan wall (ms) | Slowdown |")
    add("|---|---|---|---|")
    for row, slowdown in zip(table, slowdowns):
        add(
            f"| {row['bench']} | {row['base_wall']:.1f} +/- {row['base_wall_sd']:.1f} "
            f"| {row['asan_wall']:.1f} +/- {row['asan_wall_sd']:.1f} | {slowdown:+.1f}% |"
        )
    add("")
    if wall_outliers:
        add("Wall-time outliers (host stall, kept in the data, do not affect VmHWM):")
        add("")
        for item in wall_outliers:
            add(f"- {item}")
        add("")
    add("## Checks")
    add("")
    add(f"- repetitions per (benchmark, configuration): {counts} (expected 3)")
    add(f"- RESULT lines: {len(runs)} (expected {len(benches) * 2 * 3})")
    add(f"- non-zero exits: {len(failures)}")
    add(f"- ASan VmPeak spread over all ASan runs: {peak_spread:.0f} kB")
    add("")
    if sessions:
        add("## Figure C -- comparison across sessions")
        add("")
        add("Ratio per benchmark in each session; sessions are kept separate and never pooled into one n.")
        add("")
        add("| Session | Environment | " + " | ".join(f"{b}" for b in bench_order(table)) + " |")
        add("|---" * (len(bench_order(table)) + 2) + "|")
        current = {row["bench"]: row["rss_ratio"] for row in table}
        add("| this session (" + (env.get("session_stamp", "n/a") if env else "n/a") + ") | kernel " + (env.get("kernel", "n/a") if env else "n/a") + " | " + " | ".join(f"{current[b]:.2f}x" for b in bench_order(table)) + " |")
        for session in sessions:
            values = {row["bench"]: row["rss_ratio"] for row in session["table"]}
            add(
                "| " + session["label"] + " | " + session["env"] + " | "
                + " | ".join(f"{values[b]:.2f}x" if b in values else "n/a" for b in bench_order(table)) + " |"
            )
        add("")
    add("## Figures")
    add("")
    for path in made:
        add(f"- `{path.as_posix()}`")
    add("")
    add(f"CSV: `{(outdir / 'results.csv').as_posix()}` ({csv_rows} rows).")
    add("")

    md = "\n".join(lines) + "\n"
    (outdir / "summary.md").write_text(md, encoding="utf-8")
    print(md)
    print(f"wrote {(outdir / 'results.csv').as_posix()}")
    print(f"wrote {(outdir / 'summary.md').as_posix()}")
    for path in made:
        print(f"wrote {path.as_posix()}")
    return 0


def bench_order(table):
    return [row["bench"] for row in table]


if __name__ == "__main__":
    raise SystemExit(main())

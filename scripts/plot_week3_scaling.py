#!/usr/bin/env python3
"""Generate Week 3 AddressSanitizer scaling charts."""

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

INPUT = Path(
    "results/week3_scaling/combined/combined_results.csv"
)
OUTDIR = Path(
    "results/week3_scaling/analysis/figures"
)

SCALES = [1, 2, 3]
BENCHMARKS = [
    "b1_malloc_text",
    "b2_pointer_chase",
    "b3_matmul",
    "b4_string_scan",
]
CONFIGS = ["base", "asan"]
METRICS = ["wall_ms", "vmhwm_kb", "vmpeak_kb"]


def load_results():
    if not INPUT.is_file():
        raise SystemExit(f"Missing input: {INPUT}")

    data = {}

    with INPUT.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        required_columns = {
            "scale", "benchmark", "config",
            "metric", "mean", "std", "n"
        }

        if not required_columns.issubset(reader.fieldnames or []):
            raise SystemExit("CSV columns are incomplete")

        for row in reader:
            key = (
                int(row["scale"]),
                row["benchmark"],
                row["config"],
                row["metric"],
            )

            if key in data:
                raise SystemExit(f"Duplicate record: {key}")

            if int(row["n"]) != 3:
                raise SystemExit(f"Unexpected repetition count: {key}")

            data[key] = {
                "mean": float(row["mean"]),
                "std": float(row["std"]),
            }

    expected = {
        (scale, bench, config, metric)
        for scale in SCALES
        for bench in BENCHMARKS
        for config in CONFIGS
        for metric in METRICS
    }

    if set(data) != expected:
        raise SystemExit(
            f"Data mismatch: missing={expected - set(data)}, "
            f"unexpected={set(data) - expected}"
        )

    return data


def mean_value(data, scale, bench, config, metric):
    return data[(scale, bench, config, metric)]["mean"]


def ratio(data, scale, bench, metric):
    base = mean_value(data, scale, bench, "base", metric)
    asan = mean_value(data, scale, bench, "asan", metric)

    if base <= 0:
        raise ValueError("Base measurement must be positive")

    return asan / base


def slowdown(data, scale, bench):
    return (ratio(data, scale, bench, "wall_ms") - 1) * 100


def save(fig, filename):
    OUTDIR.mkdir(parents=True, exist_ok=True)
    path = OUTDIR / filename
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print("Wrote:", path)


def plot_runtime(data):
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))

    for ax, bench in zip(axes.flat, BENCHMARKS):
        for config in CONFIGS:
            values = [
                mean_value(data, s, bench, config, "wall_ms")
                for s in SCALES
            ]

            errors = [
                data[(s, bench, config, "wall_ms")]["std"]
                for s in SCALES
            ]

            ax.errorbar(
                SCALES,
                values,
                yerr=errors,
                marker="o",
                capsize=4,
                label=config.upper(),
            )

        ax.set_title(bench)
        ax.set_xticks(SCALES)
        ax.set_xlabel("Workload Scale")
        ax.set_ylabel("Wall Time (ms)")
        ax.grid(alpha=0.25)
        ax.legend()

    fig.suptitle("Runtime Scaling: Base vs ASan (Mean +/- SD)")
    fig.tight_layout()
    save(fig, "runtime_by_scale.png")


def plot_slowdown(data):
    fig, ax = plt.subplots(figsize=(9, 5.5))

    for bench in BENCHMARKS:
        values = [
            slowdown(data, s, bench)
            for s in SCALES
        ]
        ax.plot(
            SCALES, values,
            marker="o",
            linewidth=2,
            label=bench
        )

    ax.axhline(0, linestyle="--", color="gray")
    ax.set_xticks(SCALES)
    ax.set_xlabel("Workload Scale")
    ax.set_ylabel("Runtime Slowdown (%)")
    ax.set_title("ASan Runtime Overhead Across Scales")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()

    save(fig, "slowdown_by_scale.png")


def plot_memory(data, metric, filename, title, log_scale=False):
    fig, ax = plt.subplots(figsize=(9, 5.5))

    for bench in BENCHMARKS:
        values = [
            ratio(data, s, bench, metric)
            for s in SCALES
        ]

        ax.plot(
            SCALES, values,
            marker="o",
            linewidth=2,
            label=bench
        )

    ax.axhline(1, linestyle="--", color="gray")
    ax.set_xticks(SCALES)
    ax.set_xlabel("Workload Scale")
    ax.set_ylabel("ASan / Base Ratio")
    ax.set_title(title)

    if log_scale:
        ax.set_yscale("log")

    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()

    save(fig, filename)


def plot_average_slowdown(data):
    averages = []

    for scale in SCALES:
        values = [
            slowdown(data, scale, bench)
            for bench in BENCHMARKS
        ]
        averages.append(sum(values) / len(values))

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(SCALES, averages, marker="o", linewidth=2)

    for scale, value in zip(SCALES, averages):
        ax.annotate(
            f"{value:.1f}%",
            (scale, value),
            textcoords="offset points",
            xytext=(0, 10),
            ha="center",
        )

    ax.set_xticks(SCALES)
    ax.set_xlabel("Workload Scale")
    ax.set_ylabel("Average Slowdown (%)")
    ax.set_title("Mean of Four Benchmark Slowdowns")
    ax.grid(alpha=0.25)
    ax.margins(y=0.25)
    fig.tight_layout()

    save(fig, "average_slowdown_by_scale.png")

    print()
    for scale, value in zip(SCALES, averages):
        print(f"Scale {scale} average slowdown: {value:.2f}%")


def main():
    data = load_results()

    print("Validated records:", len(data))

    plot_runtime(data)
    plot_slowdown(data)

    plot_memory(
        data,
        "vmhwm_kb",
        "vmhwm_ratio_by_scale.png",
        "VmHWM: Resident Memory Overhead",
    )

    plot_memory(
        data,
        "vmpeak_kb",
        "vmpeak_ratio_by_scale.png",
        "VmPeak: Virtual Memory Overhead (Log Scale)",
        log_scale=True,
    )

    plot_average_slowdown(data)

    print()
    print("STATUS: PASS")


if __name__ == "__main__":
    main()

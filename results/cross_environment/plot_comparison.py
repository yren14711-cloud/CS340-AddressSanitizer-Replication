#!/usr/bin/env python3
"""Compare Scale 1 VmHWM ratios across two experimental environments."""

import csv
import math
import statistics
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent

BENCHMARKS = [
    "b1_malloc_text",
    "b2_pointer_chase",
    "b3_matmul",
    "b4_string_scan",
]

DATASETS = [
    (
        "ren_scale1",
        "AMD / Clang 21.1.8",
        "results/week3_scaling/combined/combined_results.csv",
    ),
    (
        "ye_session1",
        "Intel / Clang 18.1.3 / S1",
        "results/memory_claim2/20261121T051205Z/results.csv",
    ),
    (
        "ye_session2",
        "Intel / Clang 18.1.3 / S2",
        "results/memory_claim2/20261121T051259Z/results.csv",
    ),
]


def read_dataset(session, label, source):
    records = {}

    with (ROOT / source).open(newline="") as f:
        for row in csv.DictReader(f):
            if row.get("scale", "1") != "1":
                continue
            if row["metric"] != "vmhwm_kb":
                continue

            bench = row["benchmark"]
            config = row["config"]
            key = (bench, config)

            assert bench in BENCHMARKS, key
            assert config in ("base", "asan"), key
            assert key not in records, key
            assert row["unit"] == "kB", row
            assert int(row["n"]) == 3, row
            assert float(row["mean"]) > 0, row

            log = ROOT / row["source_log"]
            assert log.is_file(), log

            values = []
            run_ids = set()

            for line in log.read_text().splitlines():
                if not line.startswith("RESULT "):
                    continue

                fields = dict(
                    token.split("=", 1)
                    for token in line.split()[1:]
                    if "=" in token
                )

                if fields.get("bench") != bench:
                    continue
                if fields.get("config") != config:
                    continue

                assert fields["scale"] == "1", fields
                assert fields["exit"] == "0", fields
                assert fields["run"] not in run_ids, fields

                run_ids.add(fields["run"])
                values.append(int(fields["vmhwm_kb"]))

            assert run_ids == {"run1", "run2", "run3"}, key
            assert len(values) == 3, key

            mean = statistics.mean(values)
            sd = statistics.stdev(values)

            assert math.isclose(
                mean, float(row["mean"]),
                rel_tol=0, abs_tol=0.001
            ), key

            assert math.isclose(
                sd, float(row["std"]),
                rel_tol=0, abs_tol=0.001
            ), key

            records[key] = {
                "mean": mean,
                "std": sd,
                "n": len(values),
                "log": row["source_log"],
            }

    assert len(records) == 8, session

    output = []

    for bench in BENCHMARKS:
        base = records[(bench, "base")]
        asan = records[(bench, "asan")]

        assert base["log"] == asan["log"], bench

        ratio = asan["mean"] / base["mean"]

        output.append({
            "session": session,
            "environment": label,
            "scale": 1,
            "benchmark": bench,
            "base_mean_kb": base["mean"],
            "base_std_kb": base["std"],
            "base_n": base["n"],
            "asan_mean_kb": asan["mean"],
            "asan_std_kb": asan["std"],
            "asan_n": asan["n"],
            "vmhwm_ratio": ratio,
            "overhead_percent": (ratio - 1) * 100,
            "source_csv": source,
            "source_log": base["log"],
        })

    return output


def write_csv(rows):
    target = OUT / "comparison.csv"

    with target.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=list(rows[0]),
            lineterminator="\n"
        )
        writer.writeheader()

        for row in rows:
            formatted = {
                key: f"{value:.6f}"
                if isinstance(value, float) else value
                for key, value in row.items()
            }
            writer.writerow(formatted)

    print("Wrote:", target.relative_to(ROOT))


def print_summary(rows):
    print("\n===== PER-SESSION RESULTS =====")

    for session, label, _ in DATASETS:
        group = [
            row for row in rows
            if row["session"] == session
        ]

        print(f"\n{label}")

        for row in group:
            print(
                f"  {row['benchmark']:20s} "
                f"{row['vmhwm_ratio']:.6f}x"
            )

        mean = statistics.mean(
            row["vmhwm_ratio"] for row in group
        )
        print(f"  Unweighted mean: {mean:.6f}x")

    print("\n===== CROSS-SESSION SPREAD =====")

    for bench in BENCHMARKS:
        ratios = [
            row["vmhwm_ratio"]
            for row in rows
            if row["benchmark"] == bench
        ]

        spread = max(ratios) - min(ratios)
        relative = spread / min(ratios) * 100

        print(
            f"{bench:20s} "
            f"spread={spread:.6f}x, "
            f"relative spread={relative:.3f}%"
        )


def plot(rows):
    x = np.arange(len(BENCHMARKS))
    width = 0.24

    fig, ax = plt.subplots(figsize=(10, 5.8))

    colors = ["#4477AA", "#228833", "#CCBB44"]

    for i, (session, label, _) in enumerate(DATASETS):
        group = [
            row for row in rows
            if row["session"] == session
        ]

        values = [row["vmhwm_ratio"] for row in group]

        bars = ax.bar(
            x + (i - 1) * width,
            values,
            width,
            label=label,
            color=colors[i],
            edgecolor="black",
            linewidth=0.5,
        )

        ax.bar_label(
            bars,
            fmt="%.3f",
            padding=3,
            fontsize=8,
        )

    ax.axhline(
        1.0,
        color="gray",
        linestyle="--",
        linewidth=1,
        label="Native baseline (1.0x)",
    )

    ax.set_xticks(x)
    ax.set_xticklabels([
        "b1\nmalloc_text",
        "b2\npointer_chase",
        "b3\nmatmul",
        "b4\nstring_scan",
    ])

    ax.set_ylabel("VmHWM ratio (ASan / Base)")
    ax.set_xlabel("Benchmark (Scale 1)")
    ax.set_title("Cross-environment ASan resident-memory overhead")

    ax.set_ylim(
        0,
        max(row["vmhwm_ratio"] for row in rows) * 1.18,
    )

    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)
    ax.legend(fontsize=8, loc="upper right")

    fig.text(
        0.5, 0.02,
        "Each ratio uses 3 measured runs per configuration. "
        "Sessions are not pooled.\n"
        "No error bars: bars show ratios of means, "
        "not individual-run measurements.",
        ha="center",
        fontsize=9,
    )

    fig.tight_layout(rect=(0, 0.09, 1, 1))

    target = OUT / "figures" / "vmhwm_cross_environment.png"
    target.parent.mkdir(parents=True, exist_ok=True)

    fig.savefig(target, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print("\nWrote:", target.relative_to(ROOT))


def main():
    rows = []

    for session, label, source in DATASETS:
        rows.extend(read_dataset(session, label, source))
        print("Validated:", session)

    assert len(rows) == 12

    write_csv(rows)
    print_summary(rows)
    plot(rows)

    print("\nAll checks passed.")
    print("Datasets: 3")
    print("Environments: 2")
    print("Benchmark-session ratios: 12")
    print("Underlying measured executions: 72")


if __name__ == "__main__":
    main()

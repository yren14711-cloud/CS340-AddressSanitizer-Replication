#!/usr/bin/env python3
"""Audit stored ASan experiment evidence without rerunning experiments."""

import argparse
import csv
import math
import re
import statistics
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BENCHMARKS = {
    "b1_malloc_text",
    "b2_pointer_chase",
    "b3_matmul",
    "b4_string_scan",
}

METRICS = {"wall_ms", "vmpeak_kb", "vmhwm_kb"}

REPORT = []
ERRORS = []
WARNINGS = []
PASSED = []


def emit(message):
    print(message)
    REPORT.append(message)


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def passed(message):
    PASSED.append(message)
    emit("[PASS] " + message)


def warn(message):
    WARNINGS.append(message)
    emit("[WARN] " + message)


def run_check(name, function):
    emit("\n## " + name)
    try:
        function()
    except Exception as exc:
        message = f"{name}: {type(exc).__name__}: {exc}"
        ERRORS.append(message)
        emit("[FAIL] " + message)


def read_csv(relative):
    p = ROOT / relative
    check(p.is_file(), f"Missing CSV: {relative}")

    with p.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_results(relative):
    p = ROOT / relative
    check(p.is_file(), f"Missing log: {relative}")

    rows = []

    for line in p.read_text().splitlines():
        if not line.startswith("RESULT "):
            continue

        row = dict(
            token.split("=", 1)
            for token in line.split()[1:]
            if "=" in token
        )

        check(
            row.get("exit") == "0",
            f"Nonzero exit: {relative}: {line}"
        )

        check(
            re.fullmatch(r"run[123]", row["run"]),
            f"Unexpected measured run: {row}"
        )

        rows.append(row)

    return rows


def close(a, b, tolerance=0.001):
    return math.isclose(
        float(a),
        float(b),
        rel_tol=0,
        abs_tol=tolerance
    )


def validate_aggregate_csv(relative, expected_count):
    rows = read_csv(relative)

    check(
        len(rows) == expected_count,
        f"{relative}: unexpected CSV row count"
    )

    cache = {}
    keys = set()
    used_runs = set()

    for row in rows:
        scale = row.get("scale", "1")
        bench = row["benchmark"]
        config = row["config"]
        metric = row["metric"]

        key = (scale, bench, config, metric)

        check(key not in keys, f"Duplicate aggregate: {key}")
        keys.add(key)

        check(bench in BENCHMARKS, f"Unknown benchmark: {bench}")
        check(config in {"base", "asan"}, f"Unknown build: {config}")
        check(metric in METRICS, f"Unknown metric: {metric}")
        check(int(row["n"]) == 3, f"Invalid repetition count: {key}")

        source = row["source_log"]

        if source not in cache:
            cache[source] = read_results(source)

        matched = [
            raw for raw in cache[source]
            if raw["bench"] == bench
            and raw["config"] == config
            and raw.get("scale", "1") == scale
        ]

        check(len(matched) == 3, f"Expected 3 raw runs: {key}")

        check(
            {r["run"] for r in matched} == {"run1", "run2", "run3"},
            f"Incorrect run identifiers: {key}"
        )

        values = [float(r[metric]) for r in matched]

        check(
            all(math.isfinite(x) and x > 0 for x in values),
            f"Invalid measurement: {key}"
        )

        mean = statistics.mean(values)
        sd = statistics.stdev(values)

        check(close(mean, row["mean"]), f"Mean mismatch: {key}")
        check(close(sd, row["std"]), f"SD mismatch: {key}")

        for raw in matched:
            used_runs.add(
                (source, scale, bench, config, raw["run"])
            )

    expected_scales = {"1", "2", "3"} if expected_count == 72 else {"1"}

    expected_keys = {
        (scale, bench, config, metric)
        for scale in expected_scales
        for bench in BENCHMARKS
        for config in ("base", "asan")
        for metric in METRICS
    }

    check(keys == expected_keys, "Incomplete aggregate matrix")

    check(
        sum(len(values) for values in cache.values()) == len(used_runs),
        "Unexpected or unused measured records in raw logs"
    )

    passed(f"{relative}: {len(rows)} aggregates match raw data")
    emit(f"Unique measured executions: {len(used_runs)}")

    return rows, used_runs


def check_scaling():
    rows, runs = validate_aggregate_csv(
        "results/week3_scaling/combined/combined_results.csv",
        72
    )

    check(len(runs) == 72, "Scaling execution count mismatch")

    data = {
        (
            r["scale"], r["benchmark"],
            r["config"], r["metric"]
        ): float(r["mean"])
        for r in rows
    }

    for scale in ("1", "2", "3"):
        slowdowns = []
        memory = []

        for bench in sorted(BENCHMARKS):
            base = data[(scale, bench, "base", "wall_ms")]
            asan = data[(scale, bench, "asan", "wall_ms")]

            slowdown = (asan / base - 1) * 100

            ratio = (
                data[(scale, bench, "asan", "vmhwm_kb")]
                / data[(scale, bench, "base", "vmhwm_kb")]
            )

            slowdowns.append(slowdown)
            memory.append(ratio)

            emit(
                f"Scale {scale} {bench}: "
                f"slowdown={slowdown:.3f}%, "
                f"VmHWM={ratio:.6f}x"
            )

        emit(
            f"Scale {scale} aggregate: "
            f"slowdown={statistics.mean(slowdowns):.3f}%, "
            f"VmHWM={statistics.mean(memory):.6f}x"
        )

    passed("Scaling: 72 executions and 72 aggregate records")


def check_memory():
    sessions = [
        "20261121T051205Z",
        "20261121T051259Z",
    ]

    all_runs = set()

    for session in sessions:
        base = f"results/memory_claim2/{session}"

        rows, runs = validate_aggregate_csv(
            f"{base}/results.csv",
            24
        )

        check(len(runs) == 24, f"Incorrect count: {session}")

        check(not (all_runs & runs), "Overlapping session records")

        all_runs.update(runs)

        env = ROOT / base / "environment.txt"
        check(env.is_file(), f"Missing environment: {session}")

        data = {
            (r["benchmark"], r["config"], r["metric"]):
            float(r["mean"])
            for r in rows
        }

        ratios = []

        for bench in sorted(BENCHMARKS):
            ratio = (
                data[(bench, "asan", "vmhwm_kb")]
                / data[(bench, "base", "vmhwm_kb")]
            )

            ratios.append(ratio)
            emit(f"{session} {bench}: {ratio:.6f}x")

        emit(
            f"{session} unweighted mean: "
            f"{statistics.mean(ratios):.6f}x"
        )

    check(len(all_runs) == 48, "Expected 48 memory executions")

    passed("Memory: two sessions and 48 measured executions")


def check_cross_environment():
    rows = read_csv(
        "results/cross_environment/comparison.csv"
    )

    check(len(rows) == 12, "Expected 12 comparison rows")

    required_sources = {
        "ren_scale1":
        "results/week3_scaling/combined/combined_results.csv",
        "ye_session1":
        "results/memory_claim2/20261121T051205Z/results.csv",
        "ye_session2":
        "results/memory_claim2/20261121T051259Z/results.csv",
    }

    keys = set()
    reused = set()
    cache = {}
    ratios = defaultdict(list)

    for row in rows:
        session = row["session"]
        bench = row["benchmark"]

        key = (session, bench)
        check(key not in keys, f"Duplicate comparison: {key}")
        keys.add(key)

        check(row["scale"] == "1", f"Incorrect scale: {key}")

        source = row["source_csv"]

        check(
            source == required_sources[session],
            f"Incorrect source: {key}"
        )

        if source not in cache:
            cache[source] = read_csv(source)

        for config in ("base", "asan"):
            matches = [
                r for r in cache[source]
                if r.get("scale", "1") == "1"
                and r["benchmark"] == bench
                and r["config"] == config
                and r["metric"] == "vmhwm_kb"
            ]

            check(len(matches) == 1, f"Source ambiguity: {key}")

            original = matches[0]

            check(
                close(row[f"{config}_mean_kb"], original["mean"]),
                f"Source mean mismatch: {key}"
            )

            check(
                close(row[f"{config}_std_kb"], original["std"]),
                f"Source SD mismatch: {key}"
            )

            check(
                int(row[f"{config}_n"]) == int(original["n"]) == 3,
                f"Source sample count mismatch: {key}"
            )

            check(
                row["source_log"] == original["source_log"],
                f"Source log mismatch: {key}"
            )

            for run in ("run1", "run2", "run3"):
                reused.add(
                    (row["source_log"], bench, config, run)
                )

        ratio = (
            float(row["asan_mean_kb"])
            / float(row["base_mean_kb"])
        )

        check(
            close(ratio, row["vmhwm_ratio"], 0.000001),
            f"Ratio mismatch: {key}"
        )

        check(
            close(
                (ratio - 1) * 100,
                row["overhead_percent"],
                0.0001
            ),
            f"Overhead mismatch: {key}"
        )

        ratios[session].append(ratio)

    check(
        keys == {
            (s, b)
            for s in required_sources
            for b in BENCHMARKS
        },
        "Incomplete comparison matrix"
    )

    check(len(reused) == 72, "Expected 72 reused executions")

    for session, values in sorted(ratios.items()):
        emit(f"{session}: {statistics.mean(values):.6f}x")

    passed("Cross-environment: 12 ratios, 72 reused executions")


def check_week2():
    base = ROOT / "results/performance"

    required = [
        "benchmark_runs_batch1.log",
        "benchmark_runs_batch2.log",
        "benchmark_runs_batch3.log",
        "benchmark_summary.csv",
        "performance_analysis.txt",
    ]

    for name in required:
        check((base / name).is_file(), f"Missing Week 2 file: {name}")

    text = (base / "performance_analysis.txt").read_text()

    check("31.19" in text, "Missing reported overall slowdown")

    base_mean = 0.809600
    asan_mean = 1.062118

    slowdown = (asan_mean / base_mean - 1) * 100

    check(
        close(slowdown, 31.19, 0.01),
        "Week 2 published mean arithmetic mismatch"
    )

    emit(f"Published overall slowdown: {slowdown:.4f}%")

    passed("Week 2 source files and published mean arithmetic")

    warn(
        "Week 2 per-run means, SDs and checksums require "
        "the independent analyzer/raw-log review."
    )


def resolve_record_path(value):
    candidates = [
        ROOT / value,
        ROOT / "results/detect/false_positive" / value,
        ROOT / "results/detect/false_positive" / Path(value).name,
    ]

    return next((p for p in candidates if p.is_file()), None)


def check_detection():
    rows = read_csv(
        "results/detect/false_positive/summary.csv"
    )

    check(len(rows) == 24, "Expected 24 clean controls")

    groups = defaultdict(list)
    missing_stdout = []
    missing_stderr = []

    for row in rows:
        key = (row["benchmark"], row["variant"])
        groups[key].append(row)

        check(int(row["exit_code"]) == 0, f"Nonzero exit: {key}")

        check(
            row["asan_reported"].lower() == "no",
            f"Unexpected ASan report: {key}"
        )

        out = resolve_record_path(row["out_file"])
        err = resolve_record_path(row["err_file"])

        if out is None:
            missing_stdout.append(row["out_file"])

        if err is None:
            missing_stderr.append(row["err_file"])
        elif row["variant"] == "asan":
            check(
                not re.search(
                    r"(?:ERROR|SUMMARY): AddressSanitizer",
                    err.read_text(errors="replace")
                ),
                f"ASan diagnostic in clean stderr: {err}"
            )

    check(
        set(groups) == {
            (b, v)
            for b in BENCHMARKS
            for v in ("base", "asan")
        },
        "Incomplete clean-control matrix"
    )

    for key, group in groups.items():
        check(len(group) == 3, f"Incorrect repeats: {key}")

        check(
            len({r["run"] for r in group}) == 3,
            f"Duplicate runs: {key}"
        )

    passed("Clean-control CSV: 24/24 exits, 0/12 ASan reports")

    if missing_stdout:
        warn(f"Missing clean-control stdout files: {len(missing_stdout)}")

    if missing_stderr:
        warn(f"Missing clean-control stderr files: {len(missing_stderr)}")

    detect = ROOT / "results/detect"

    exit_files = list(
        (detect / "false_positive").rglob("*.exit")
    )

    if len(exit_files) == 24:
        for p in exit_files:
            check(p.read_text().strip() == "0", f"Invalid exit: {p}")

        passed("24 stored clean-control exit records")
    else:
        warn(
            f"Expected 24 clean-control exit files; "
            f"found {len(exit_files)}"
        )

    diagnoses = set()

    for p in detect.rglob("*"):
        if not p.is_file():
            continue
        if "false_positive" in p.parts:
            continue
        if p.suffix not in {".err", ".log", ".out"}:
            continue

        text = p.read_text(errors="replace")

        diagnoses.update(
            re.findall(
                r"ERROR: AddressSanitizer:\s+([\w-]+)",
                text
            )
        )

    expected = {
        "heap-buffer-overflow",
        "stack-buffer-overflow",
        "global-buffer-overflow",
        "heap-use-after-free",
    }

    for diagnosis in sorted(expected & diagnoses):
        emit(f"Stored positive diagnosis: {diagnosis}")

    check(
        expected <= diagnoses,
        f"Missing positive diagnostics: {expected - diagnoses}"
    )

    passed("All four expected positive diagnostic classes found")

    warn(
        "Positive-case file-to-exit-code pairing and stdout "
        "equivalence require separate record inspection."
    )


def check_figures():
    figures = [
        "results/figures/paper_vs_ours_runtime.png",
        "results/figures/claim3_detection_matrix.png",
        "results/cross_environment/figures/vmhwm_cross_environment.png",
        "results/performance/performance_comparison.png",
    ]

    for name in [
        "runtime_by_scale",
        "slowdown_by_scale",
        "vmhwm_ratio_by_scale",
        "vmpeak_ratio_by_scale",
        "average_slowdown_by_scale",
    ]:
        figures.append(
            f"results/week3_scaling/analysis/figures/{name}.png"
        )

    for session in (
        "20261121T051205Z",
        "20261121T051259Z",
    ):
        for name in ("fig_a_vmhwm_bars", "fig_b_vmhwm_ratio"):
            figures.append(
                f"results/memory_claim2/{session}/figures/{name}.png"
            )

    figures.append(
        "results/memory_claim2/20261121T051205Z/"
        "figures/fig_c_ratio_sessions.png"
    )

    from PIL import Image

    for relative in figures:
        p = ROOT / relative

        check(p.is_file(), f"Missing figure: {relative}")

        with Image.open(p) as im:
            check(im.format == "PNG", f"Not PNG: {relative}")
            width, height = im.size
            im.verify()

        check(width > 0 and height > 0, f"Invalid image: {relative}")

        emit(f"{relative}: {width} x {height}")

    passed(f"All {len(figures)} expected PNG files are readable")


def check_links():
    documents = (
        [ROOT / "README.md"]
        + sorted((ROOT / "docs").glob("*.md"))
        + [
            ROOT / "results/cross_environment/README.md",
            ROOT / "results/memory_claim2/README.md",
            ROOT / "results/week3_scaling/analysis/summary.md",
        ]
    )

    missing = []
    count = 0

    for p in documents:
        text = p.read_text()

        for link in re.findall(r"\]\(([^)]+)\)", text):
            if "://" in link or link.startswith(("#", "mailto:")):
                continue

            relative = link.split("#", 1)[0]

            if not relative:
                continue

            count += 1
            target = p.parent / relative

            if not target.exists():
                missing.append(
                    f"{p.relative_to(ROOT)} -> {link}"
                )

    for item in missing:
        warn("Missing local reference: " + item)

    emit(f"Local links checked: {count}")
    emit(f"Missing local links: {len(missing)}")

    if not missing:
        passed("All inspected local Markdown links resolve")


def check_source_scripts():
    required = [
        "Makefile",
        "scripts/run_experiments.sh",
        "scripts/parse_results.py",
        "scripts/merge_scaling_results.py",
        "scripts/plot_week3_scaling.py",
        "scripts/run_detection.sh",
        "scripts/run_false_positive.sh",
        "scripts/plot_claim3_detection.py",
        "scripts/plot_paper_vs_ours.py",
        "results/memory_claim2/analyze_memory_claim2.py",
        "results/cross_environment/plot_comparison.py",
        "experiments/performance/analyze_benchmarks.py",
        "experiments/performance/plot_performance.py",
    ]

    for relative in required:
        p = ROOT / relative

        check(p.is_file(), f"Missing source: {relative}")

        if p.suffix == ".py":
            compile(p.read_text(), str(p), "exec")

        if p.suffix == ".sh":
            subprocess.run(
                ["bash", "-n", str(p)],
                check=True
            )

        emit(f"Source OK: {relative}")

    passed("Required analysis scripts exist and pass syntax checks")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    emit("# ASan reproducibility audit")
    emit("Mode: stored-data verification; no new benchmark runs")

    run_check("Source and script checks", check_source_scripts)
    run_check("Week 2 runtime checks", check_week2)
    run_check("Week 3 scaling raw-to-CSV checks", check_scaling)
    run_check("Claim 2 memory raw-to-CSV checks", check_memory)
    run_check("Cross-environment provenance", check_cross_environment)
    run_check("Claim 3 detection evidence", check_detection)
    run_check("Figure integrity", check_figures)
    run_check("Documentation links", check_links)

    emit("\n## Audit summary")
    emit(f"Passed checks: {len(PASSED)}")
    emit(f"Warnings: {len(WARNINGS)}")
    emit(f"Failures: {len(ERRORS)}")

    for error in ERRORS:
        emit("FAILURE: " + error)

    for warning in WARNINGS:
        emit("LIMITATION: " + warning)

    if ERRORS:
        emit("AUDIT STATUS: FAILED")
    elif WARNINGS:
        emit("AUDIT STATUS: PASSED WITH DOCUMENTED LIMITATIONS")
    else:
        emit("AUDIT STATUS: PASSED")

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text("\n".join(REPORT) + "\n")

    return 1 if ERRORS else 0


if __name__ == "__main__":
    sys.exit(main())

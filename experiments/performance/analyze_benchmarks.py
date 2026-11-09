import csv
import re
import statistics
from pathlib import Path

logs = [
    ("Batch 1", Path("results/performance/benchmark_runs_batch1.log")),
    ("Batch 2", Path("results/performance/benchmark_runs_batch2.log")),
    ("Batch 3", Path("results/performance/benchmark_runs_batch3.log")),
]

rows = []

for batch, path in logs:
    pair = None
    variant = None
    elapsed = None

    for line in path.read_text().splitlines():
        m = re.search(r"PAIR\s+(\d+)", line)
        if m:
            pair = int(m.group(1))

        m = re.search(r"---\s+(NATIVE|ASAN)\s+RUN\s+(\d+)", line)
        if m:
            variant = m.group(1)
            pair = int(m.group(2))

        m = re.search(r"elapsed_seconds=([0-9.]+)", line)
        if m:
            elapsed = float(m.group(1))

        m = re.search(r"checksum=(\d+)", line)
        if m and elapsed is not None and variant is not None:
            rows.append({
                "batch": batch,
                "pair": pair,
                "variant": variant,
                "elapsed_seconds": elapsed,
                "checksum": m.group(1),
            })
            elapsed = None
            variant = None

# Validate the dataset
for batch, _ in logs:
    for variant in ("NATIVE", "ASAN"):
        count = sum(
            r["batch"] == batch and r["variant"] == variant
            for r in rows
        )
        if count != 5:
            raise ValueError(
                f"{batch} {variant}: expected 5 runs, got {count}"
            )

checksums = {r["checksum"] for r in rows}

if len(rows) != 30:
    raise ValueError(f"Expected 30 records, got {len(rows)}")

if len(checksums) != 1:
    raise ValueError(f"Unexpected checksum differences: {checksums}")

# Export all raw measurements
csv_path = Path("results/performance/benchmark_summary.csv")

with csv_path.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "batch", "pair", "variant",
        "elapsed_seconds", "checksum"
    ])
    writer.writeheader()
    writer.writerows(rows)

# Calculate statistics
def stats(selected):
    values = [r["elapsed_seconds"] for r in selected]
    mean = statistics.mean(values)
    sd = statistics.stdev(values)
    cv = sd / mean * 100
    return mean, sd, cv

report = []
report.append("AddressSanitizer Performance Analysis")
report.append("Workload: array_update")
report.append("Total runs: 30")
report.append(f"Unique checksum: {next(iter(checksums))}")
report.append("Standard deviation: Sample SD")
report.append("")

for batch, _ in logs:
    report.append(f"===== {batch} =====")

    results = {}

    for variant in ("NATIVE", "ASAN"):
        selected = [
            r for r in rows
            if r["batch"] == batch and r["variant"] == variant
        ]

        mean, sd, cv = stats(selected)
        results[variant] = mean

        report.append(
            f"{variant}: Mean={mean:.6f}s, "
            f"SD={sd:.6f}s, CV={cv:.2f}%"
        )

    overhead = (
        results["ASAN"] / results["NATIVE"] - 1
    ) * 100

    report.append(f"Overhead={overhead:.2f}%")
    report.append("")

report.append("===== ALL 15 RUNS PER GROUP =====")

results = {}

for variant in ("NATIVE", "ASAN"):
    selected = [r for r in rows if r["variant"] == variant]
    mean, sd, cv = stats(selected)
    results[variant] = mean

    report.append(
        f"{variant}: Mean={mean:.6f}s, "
        f"SD={sd:.6f}s, CV={cv:.2f}%"
    )

overhead = (
    results["ASAN"] / results["NATIVE"] - 1
) * 100

report.append(f"Overall Overhead={overhead:.2f}%")
report.append("")
report.append(
    "Note: Overall SD includes between-batch variation. "
    "Batch-specific results should also be reported."
)

analysis_path = Path("results/performance/performance_analysis.txt")
analysis_path.write_text("\n".join(report) + "\n")

print("Analysis completed successfully.")
print(f"CSV saved: {csv_path}")
print(f"Report saved: {analysis_path}")
print(f"Total records: {len(rows)}")
print(f"Unique checksums: {len(checksums)}")
print(f"Overall overhead: {overhead:.2f}%")

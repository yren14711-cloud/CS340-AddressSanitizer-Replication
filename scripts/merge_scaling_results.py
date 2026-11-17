#!/usr/bin/env python3

import csv
from pathlib import Path

# Three experiment result files
sources = {
    1: Path("results/week3_scaling/scale1/20261117T093819Z/parsed/results.csv"),
    2: Path("results/week3_scaling/scale2/20261117T100512Z/parsed/results.csv"),
    3: Path("results/week3_scaling/scale3/20261117T101557Z/parsed/results.csv"),
}

# Output file
output = Path("results/week3_scaling/combined/combined_results.csv")

combined_rows = []
expected_header = None

# Read and combine all three CSV files
for scale, source in sources.items():

    if not source.is_file():
        raise SystemExit(f"ERROR: Missing file: {source}")

    with source.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        if expected_header is None:
            expected_header = reader.fieldnames
        elif reader.fieldnames != expected_header:
            raise SystemExit(f"ERROR: CSV header mismatch: {source}")

        rows = list(reader)

    print(f"Scale {scale}: {len(rows)} records")

    if len(rows) != 24:
        raise SystemExit(
            f"ERROR: Scale {scale} expected 24 records, got {len(rows)}"
        )

    # Add scale information to every record
    for row in rows:
        row["scale"] = str(scale)
        combined_rows.append(row)


# Validate total record count
if len(combined_rows) != 72:
    raise SystemExit(
        f"ERROR: Expected 72 records, got {len(combined_rows)}"
    )

# Check repetition count
bad_n = [r for r in combined_rows if r["n"] != "3"]

if bad_n:
    raise SystemExit(f"ERROR: Found {len(bad_n)} records with n != 3")


# Check all expected combinations
benchmarks = [
    "b1_malloc_text",
    "b2_pointer_chase",
    "b3_matmul",
    "b4_string_scan",
]

configs = ["base", "asan"]
metrics = ["wall_ms", "vmpeak_kb", "vmhwm_kb"]

expected = {
    (str(scale), bench, config, metric)
    for scale in (1, 2, 3)
    for bench in benchmarks
    for config in configs
    for metric in metrics
}

keys = [
    (r["scale"], r["benchmark"], r["config"], r["metric"])
    for r in combined_rows
]

if len(keys) != len(set(keys)):
    raise SystemExit("ERROR: Duplicate combinations found")

if set(keys) != expected:
    raise SystemExit("ERROR: Missing or unexpected combinations")


# Write combined CSV
output.parent.mkdir(parents=True, exist_ok=True)

fieldnames = ["scale"] + expected_header

with output.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(combined_rows)


# Final report
print()
print("Total records:", len(combined_rows))
print("Scales:", len(sources))
print("Benchmarks:", len(benchmarks))
print("Configurations:", len(configs))
print("Metrics:", len(metrics))
print("Records with n != 3:", len(bad_n))
print("Duplicate combinations:", len(keys) - len(set(keys)))
print("Missing combinations:", len(expected - set(keys)))
print("STATUS: PASS")
print()
print("Wrote:", output)

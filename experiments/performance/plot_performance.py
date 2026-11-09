
import csv
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Input and output files
csv_path = Path("results/performance/benchmark_summary.csv")
output_path = Path("results/performance/performance_comparison.png")

# Read experimental data
groups = defaultdict(list)
checksums = set()

with csv_path.open(newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        key = (row["batch"], row["variant"])
        groups[key].append(float(row["elapsed_seconds"]))
        checksums.add(row["checksum"])

# Validate the dataset
batches = ["Batch 1", "Batch 2", "Batch 3"]
variants = ["NATIVE", "ASAN"]

for batch in batches:
    for variant in variants:
        count = len(groups[(batch, variant)])
        if count != 5:
            raise ValueError(
                f"{batch} {variant}: expected 5 runs, got {count}"
            )

if len(checksums) != 1:
    raise ValueError("Checksum mismatch detected.")

# Calculate means and sample standard deviations
native_means = []
native_sds = []
asan_means = []
asan_sds = []

for batch in batches:
    native = groups[(batch, "NATIVE")]
    asan = groups[(batch, "ASAN")]

    native_means.append(statistics.mean(native))
    native_sds.append(statistics.stdev(native))

    asan_means.append(statistics.mean(asan))
    asan_sds.append(statistics.stdev(asan))

# Create grouped bar chart
x = list(range(len(batches)))
width = 0.36

fig, ax = plt.subplots(figsize=(9, 5.5))

native_x = [i - width / 2 for i in x]
asan_x = [i + width / 2 for i in x]

ax.bar(
    native_x,
    native_means,
    width,
    yerr=native_sds,
    capsize=5,
    label="Native"
)

ax.bar(
    asan_x,
    asan_means,
    width,
    yerr=asan_sds,
    capsize=5,
    label="ASan"
)

ax.set_xlabel("Experimental Batch")
ax.set_ylabel("Execution Time (seconds)")
ax.set_title("Native vs. AddressSanitizer Performance")
ax.set_xticks(x)
ax.set_xticklabels(batches)
ax.legend()
ax.grid(axis="y", linestyle="--", alpha=0.35)
ax.set_axisbelow(True)

fig.tight_layout()

# Save high-resolution figure
fig.savefig(output_path, dpi=300)
plt.close(fig)

print("Performance chart generated successfully.")
print(f"Output: {output_path}")
print("Native and ASan: 5 runs per batch.")
print(f"Unique checksums: {len(checksums)}")

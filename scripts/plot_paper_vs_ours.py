#!/usr/bin/env python3
import os
import matplotlib.pyplot as plt

# Ensure the output directory exists
os.makedirs("results/figures", exist_ok=True)

# Define labels and values based on the paper and our own experimental data
labels = [
    "Paper\n(Fig. 2, SPEC)",
    "Ours overall\n(array_update)",
    "Ours batch 1",
    "Ours batch 2",
    "Ours batch 3",
]
values = [73.0, 31.19, 34.52, 29.27, 27.62]
colors = ["#c44e52", "#4c72b0", "#8da0cb", "#8da0cb", "#8da0cb"]

# Create the bar chart
fig, ax = plt.subplots(figsize=(8.5, 4.8))
bars = ax.bar(labels, values, color=colors)
ax.set_ylabel("Runtime overhead (%)")
ax.set_title("Runtime overhead: paper vs. ours")
ax.set_ylim(0, 90)

# Add value labels on top of each bar
for bar, v in zip(bars, values):
    label = f'{v:.0f}%' if v == 73.0 else f'{v:.2f}%'
    ax.text(bar.get_x() + bar.get_width() / 2, v + 1.5, label,
            ha="center", va="bottom", fontsize=9)

# Add a footnote emphasizing that the workloads are different
fig.text(
    0.5, 0.015,
    "Note: different workloads, not directly equivalent. "
    "Paper = SPEC CPU2006 average (Fig. 2); "
    "Ours = custom array_update microbenchmark "
    "(results/performance/performance_analysis.txt).",
    ha="center", va="bottom", fontsize=8,
)

# Adjust layout and save the figure
fig.tight_layout(rect=[0, 0.08, 1, 1])
out = "results/figures/paper_vs_ours_runtime.png"
fig.savefig(out, dpi=150)
print("wrote", out)
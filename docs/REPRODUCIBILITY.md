# Reproducibility and Data Integrity

## 1. Audit objective

This project is a partial replication and extension study of
AddressSanitizer (USENIX ATC 2012).

The Week 4 audit checks the relationship between source code,
experiment scripts, stored raw measurements, aggregate datasets,
figures and report-level conclusions.

The audit uses existing experiment records. It does not introduce
new benchmark executions or overwrite historical raw measurements.

## 2. Evidence chain

    Source code
        -> experiment scripts
        -> raw logs and environment records
        -> aggregate datasets
        -> analysis and plotting scripts
        -> report figures and claim conclusions

The numerical reporting conventions are defined in
[STATISTICAL_CONVENTIONS.md](STATISTICAL_CONVENTIONS.md).

## 3. Claim 1: runtime overhead

### Week 2 array-update experiment

- [Benchmark source](../experiments/performance/array_update_benchmark.c)
- [Execution script](../experiments/performance/run_benchmark.sh)
- [Analysis script](../experiments/performance/analyze_benchmarks.py)
- [Plotting script](../experiments/performance/plot_performance.py)
- [Experiment results](../results/performance/)
- [Aggregate dataset](../results/performance/benchmark_summary.csv)
- [Published statistics](../results/performance/performance_analysis.txt)
- [Runtime figure](../results/performance/performance_comparison.png)

The primary reported overall slowdown is 31.19%, based on
15 measured executions per build variant.

The workload and timing protocol differ from the original SPEC
CPU2006 evaluation.

### Report-level comparison

- [Comparison CSV](../results/report/paper_vs_ours_runtime.csv)
- [Generator](../scripts/plot_paper_vs_ours.py)
- [Figure 1](../results/figures/paper_vs_ours_runtime.png)

The original paper's 73% average is contextual evidence,
not a directly comparable same-workload target.

## 4. Claim 2: resident-memory overhead

- [Benchmark sources](../benchmarks/)
- [Build configuration](../Makefile)
- [Execution harness](../scripts/run_experiments.sh)
- [Memory analysis script](../results/memory_claim2/analyze_memory_claim2.py)
- [Memory experiment index](../results/memory_claim2/README.md)

Session records:

- [Session 1](../results/memory_claim2/20261121T051205Z/)
- [Session 2](../results/memory_claim2/20261121T051259Z/)

Each session contains four benchmarks, two build configurations
and three measured repetitions per configuration.

The combined design contains 48 measured executions.
Warm-up executions are excluded.

The reported memory metric is VmHWM. VmPeak is retained
for diagnostic completeness and must not be interpreted
as resident or physical memory usage.

## 5. Claim 3: memory-error detection

- [Detection methodology](DETECTION.md)
- [Detection execution script](../scripts/run_detection.sh)
- [Clean-control execution script](../scripts/run_false_positive.sh)
- [Detection summary](../results/detect/summary.md)
- [Clean-control records](../results/detect/false_positive/summary.csv)
- [Detection figure generator](../scripts/plot_claim3_detection.py)
- [Figure 3](../results/figures/claim3_detection_matrix.png)

The reported evidence covers four selected buggy cases
and 24 clean-control executions.

The false-positive denominator includes only the 12
ASan-enabled clean-control executions.

Missing raw stdout files, if any, are recorded in the audit
output and limit independent verification of output equivalence.

The selected cases do not establish universal detection completeness.

## 6. Workload-scaling extension

- [Execution harness](../scripts/run_experiments.sh)
- [Result parser](../scripts/parse_results.py)
- [Dataset merger](../scripts/merge_scaling_results.py)
- [Combined dataset](../results/week3_scaling/combined/combined_results.csv)
- [Figure generator](../scripts/plot_week3_scaling.py)
- [Analysis](../results/week3_scaling/analysis/summary.md)

The design includes three scales, four benchmarks,
two build variants and three measured repetitions.

The combined dataset contains 72 aggregate metric records
derived from 72 measured executions.

Audit checks recompute means and sample standard deviations
from the referenced raw logs.

## 7. Cross-environment extension

- [Analysis and provenance](../results/cross_environment/README.md)
- [Comparison dataset](../results/cross_environment/comparison.csv)
- [Generator](../results/cross_environment/plot_comparison.py)
- [Figure 9](../results/cross_environment/figures/vmhwm_cross_environment.png)

The comparison includes two environments and three sessions.

Twelve benchmark-session ratios are derived from 72 previously
measured executions. No new executions are counted.

Environment and compiler effects are not independently isolated.

## 8. Automated audit

From the repository root:

    python3 scripts/audit_reproducibility.py

To retain a machine-readable text record:

    python3 scripts/audit_reproducibility.py --report audit_report.txt

Dependencies include Python 3 and Pillow.
Figure regeneration additionally requires matplotlib and numpy.

The audit checks:

- Raw-to-aggregate means and sample standard deviations.
- Benchmark/configuration/scale/repetition coverage.
- Cross-environment source records and overhead ratios.
- Stored detection diagnostics and clean-control records.
- Figure readability and local documentation references.
- Python and shell script syntax.

The Week 2 arithmetic check uses published overall means.
Independent per-run verification requires its analyzer and raw logs.

The automated check does not prove historical execution provenance,
full stdout equivalence, or complete visual correctness of figures.

## 9. Audit result records

Actual audit outputs are stored in:

[results/audit/](../results/audit/)

The records distinguish passes, failures and limitations.

The source commit identifies the repository snapshot used
for isolated verification.

Figure-generation logs and comparison outputs document
the regeneration attempts. A readable PNG is not by itself
evidence of successful regeneration.

Differences in plotting libraries, fonts or metadata may
prevent byte-identical output even when the represented
numerical values agree.

## 10. Limitations

- The original SPEC CPU2006 and Chromium experiments
  have not been reproduced in full.
- Historical measurements use different software and hardware settings.
- Periodic memory sampling may miss final process peaks.
- Historical local modifications cannot always be reconstructed
  solely from committed source snapshots.
- Small sample sizes limit statistical inference.
- Missing records must be disclosed, not fabricated or replaced
  by unrelated new executions.

Any future experimental rerun should use a fresh timestamped
directory and retain its own environment records.

## 11. Final report references

- [Claims and verdicts](CLAIMS.md)
- [Paper vs. Ours](PAPER_VS_OURS.md)
- [Deviations](DEVIATIONS.md)
- [Figure inventory](FIGURE_INVENTORY.md)
- [Statistical conventions](STATISTICAL_CONVENTIONS.md)

The final report should cite these evidence sources and
must not claim stronger reproducibility than the audit establishes.

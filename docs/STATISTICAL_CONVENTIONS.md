# Statistical and Reporting Conventions

## 1. Study scope

This project is a **Partial Replication and Extension Study**
of AddressSanitizer: A Fast Address Sanity Checker
(USENIX ATC 2012).

We reproduce selected qualitative behaviors and investigate runtime
and memory overhead using open microbenchmarks. We do not claim
a full reproduction of SPEC CPU2006 or Chromium experiments.

The workload-scaling and cross-environment analyses are extensions
of the original evaluation.

## 2. Build terminology

- Base / Native / Plain: build without AddressSanitizer.
- ASan: AddressSanitizer-instrumented build.
- Use Base and ASan consistently in new report figures and tables.
- Preserve historical labels in existing raw experiment records.

Performance and detection experiments use different ASan settings.
Their configurations must be documented separately.

## 3. Runtime metrics

For the same benchmark, workload scale and session:

    Runtime ratio = mean(T_ASan) / mean(T_Base)

    Runtime slowdown (%) = (Runtime ratio - 1) * 100

Examples:

| Result | Runtime ratio | Slowdown |
|---|---:|---:|
| Original paper | 1.73x | 73% |
| Week 2 array_update | 1.3119x | 31.19% |
| Week 3 b1, Scale 1 | 6.612x | 561.2% |
| Week 3 b4, Scale 1 | 0.943x | -5.7% |

Negative measured slowdown does not establish a performance
improvement without adequate supporting evidence.

Week 2 uses CLOCK_MONOTONIC timing within the benchmark.
The b1-b4 harness measures wall time around process execution.
Absolute times from these protocols must not be pooled.

## 4. Memory metrics

- VmPeak: peak virtual address-space size.
- VmHWM: peak resident set size.
- These metrics describe different properties of a process.
- VmHWM is the primary memory-overhead proxy in this project.
- VmHWM is not a measure of total system memory consumption.

For the same benchmark, scale and session:

    VmHWM ratio = mean(VmHWM_ASan) / mean(VmHWM_Base)

    Memory overhead (%) = (VmHWM ratio - 1) * 100

VmPeak ratios may be retained for diagnostic completeness,
but must not be interpreted as physical-memory overhead.

The ASan virtual-address-space reservation in our measurements
is approximately 21.47 billion kB, or 20 TiB.

The Linux /proc memory fields use kB labels with 1024-byte units.
Preserve the original field names and source units in raw data.

    1 MiB = 1024 Linux-reported kB
    1 GiB = 1024 MiB
    1 TiB = 1024 GiB

The paper reports a 3.37x VmPeak ratio on SPEC CPU2006.
Our approximately 1.4x VmHWM ratios use different metrics
and different workloads.

These values neither reproduce nor contradict the paper's
numerical memory result.

Periodic /proc sampling may miss the final high-water mark,
particularly for short-lived processes. A fixed execution
duration does not guarantee complete peak capture.

## 5. Statistical aggregation

### Arithmetic mean

Calculate the arithmetic mean of measured repetitions for each
benchmark, configuration, workload scale and session.

### Sample standard deviation

Use sample standard deviation with denominator n - 1.

    s = sqrt(sum((x_i - mean(x))^2) / (n - 1))

Standard deviation describes variability among observations.
It is not a confidence interval or standard error.

### Ratio of means

Calculate overhead using the ratio of configuration means.
Do not silently replace this with the mean of individual
paired-run ratios.

### Benchmark-level aggregation

When summarizing b1-b4, use the unweighted arithmetic mean
of the four benchmark-specific ratios or slowdown percentages.

Do not pool absolute runtime or memory values across benchmarks
to construct the reported average overhead.

### Batch-level aggregation

The Week 2 overall result uses all 15 measured observations
per build configuration.

The overall 31.19% slowdown is calculated from the overall
configuration means, not from an arithmetic average of the
three batch-specific percentages.

### Session-level aggregation

Report each session separately unless a pooling method is
explicitly defined and justified.

The cross-environment extension compares three sessions
from two environments. Two sessions on one host are not
two independent hardware environments.

The standard deviation across benchmark ratios describes
between-benchmark variation, not repeated-run uncertainty.

## 6. Repetitions and execution counts

| Study | Design | Measured executions |
|---|---|---:|
| Week 2 runtime | 3 batches x 2 builds x 5 repeats | 30 |
| Week 3 scaling | 3 scales x 4 benchmarks x 2 builds x 3 repeats | 72 |
| Week 3 memory matrix | 2 sessions x 4 benchmarks x 2 builds x 3 repeats | 48 |
| Claim 3 clean controls | 4 benchmarks x 2 builds x 3 repeats | 24 |
| Cross-environment extension | 3 sessions x 4 benchmarks x 2 builds x 3 repeats | 72 reused; 0 new |

The table covers the listed experiments, not every historical
execution in the repository.

For the scaling and memory experiments, one warm-up per
configuration is excluded from the measured repetitions.

The scaling dataset contains 72 aggregate metric records.
This record count is distinct from its 72 measured executions.

The cross-environment analysis contains 12 benchmark-session
ratios derived from 72 existing measured executions.

Do not count those reused executions again in a project total.

## 7. Detection and false positives

Report the positive tests as:

    4/4 selected buggy cases produced the expected ASan diagnostics.

Report the clean controls as:

    Base normal exits: 12/12
    ASan normal exits: 12/12
    Total normal exits: 24/24
    Observed ASan false positives: 0/12

The denominator for observed ASan false positives includes
only ASan-enabled clean-control executions.

These observations do not establish universal detection
completeness or a population false-positive probability of zero.

Normal exit codes and absent ASan reports do not, by themselves,
establish complete stdout equivalence or program correctness.

## 8. Error bars and uncertainty

- Runtime bars: label the unit, sample size and sample SD.
- VmHWM bars: label the unit, sample size and sample SD.
- Ratio bars: do not substitute the SD of raw measurements
  for uncertainty of the ratio.
- No error bars on ratios when their uncertainty is not estimated.
- Do not invent uncertainty estimates for the paper's results.
- Detection outcomes are categorical counts, not continuous
  measurement means.
- Do not claim statistical significance or equivalence without
  a suitable statistical analysis.

## 9. Measurement variability and outliers

Retain measured observations unless an exclusion rule has
been explicitly defined and justified.

Report unusual observations and their possible impact.

Host scheduling, virtualization, compiler versions and
workload behavior may contribute to variability, but their
individual effects have not been isolated by this study.

Cross-environment consistency is descriptive evidence,
not proof of hardware independence or statistical equivalence.

## 10. Final claim verdicts

| Claim | Verdict |
|---|---|
| Claim 1: Runtime overhead | Partially supported |
| Claim 2: Memory overhead | Inconclusive |
| Claim 3: Detection capability | Supported for the tested cases |

Claim 1 supports workload-dependent runtime overhead,
but does not establish direct replication of the 73% average.

Claim 2 provides useful resident-memory measurements,
but does not directly reproduce the paper's VmPeak result.

Claim 3 is supported only within the selected positive
and clean-control tests.

## 11. Presentation and traceability

- Calculate statistics before rounding.
- Use consistent precision within each comparison table.
- Clearly distinguish ratios from percentage overheads.
- Preserve original raw logs, CSV files and environment records.
- Document every figure's generating script and source data.
- Label historical results separately from primary report results.
- Treat the original paper and experiment records as the
  numerical evidence; use this document for reporting conventions.

## 12. Related documents

- [Project README](../README.md)
- [Claims](CLAIMS.md)
- [Paper vs. Ours](PAPER_VS_OURS.md)
- [Deviations](DEVIATIONS.md)
- [Detection methodology](DETECTION.md)
- [Figure inventory](FIGURE_INVENTORY.md)
- [Cross-environment analysis](../results/cross_environment/README.md)
- [Memory analysis](../results/memory_claim2/README.md)
- [Workload scaling](../results/week3_scaling/analysis/summary.md)

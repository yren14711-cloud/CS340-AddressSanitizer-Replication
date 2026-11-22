# Final Report Outline

## Proposed title

AddressSanitizer: A Partial Replication and Extension Study

Subtitle:
An Empirical Evaluation of Runtime Overhead, Memory
Consumption, and Memory Error Detection

Course: CS340 Operating Systems

## Authors

- 任奕安 (1240014055)
- 葉景威 (1240004926)
- 王乐樵 (5260001105)
- 贾越凯 (1230022503)

The section assignments below are proposed writing
responsibilities, not a record of completed report authorship.

The final report format and length must follow the course
requirements.

## Abstract

Proposed lead: 任奕安

Suggested length: 200-250 words.

Include:

- Research background and motivation.
- Partial replication objective.
- Open microbenchmark methodology.
- Week 2 runtime result: 31.19% measured slowdown.
- Resident-memory results of approximately 1.4x.
- Four selected buggy cases with expected ASan diagnostics.
- Zero observed ASan false positives in 12 clean ASan runs.
- Workload-scaling and cross-environment extensions.
- Main conclusions and scope limitations.

Write the abstract after completing the main report.

## 1. Introduction

Proposed lead: 任奕安

Suggested length: 350-450 words.

Cover:

1. Memory safety problems in C and C++.
2. The motivation for AddressSanitizer.
3. The original USENIX ATC 2012 paper.
4. Why its performance and detection claims matter.
5. Why a full historical replication is not feasible here.
6. The scope of our partial replication.
7. Our two extension studies.

Research questions:

- RQ1: How does ASan affect runtime in our workloads?
- RQ2: What resident-memory overhead is observed?
- RQ3: Does ASan detect the selected memory errors?
- RQ4: How does overhead change with workload scale?
- RQ5: How consistent are the observed memory ratios
  across the available environments and sessions?

## 2. Background and AddressSanitizer Design

Proposed lead: 王乐樵

Suggested length: 450-600 words.

Explain:

- Compiler instrumentation.
- Shadow memory and the 8:1 mapping.
- Address-to-shadow translation.
- Poisoned and addressable shadow bytes.
- Heap, stack and global redzones.
- Heap quarantine and use-after-free detection.
- Runtime diagnostics.
- Detection limitations and possible false negatives.

Use the original paper as the primary source.

An original explanatory diagram may be included if needed.
Do not confuse the ASan shadow mapping scale with the
workload scales used in our experiments.

## 3. Experimental Methodology

Proposed coordinating lead: 任奕安

All members contribute their experiment-specific details.

Suggested length: 500-700 words.

### 3.1 Benchmark selection

Describe:

- Week 2 array_update benchmark.
- b1_malloc_text.
- b2_pointer_chase.
- b3_matmul.
- b4_string_scan.
- Four intentional memory-error cases.

Source:
[Benchmark documentation](../benchmarks/README.md)

### 3.2 Environment and build configuration

Document the available CPU, operating system, WSL2 or
Codespaces environment, compiler version and build flags.

Use historical environment records where available.

Separate the performance configuration from the detection
configuration. Do not imply that all experiments used
identical ASAN_OPTIONS.

Sources:

- [Build configuration](../Makefile)
- [Memory experiment records](../results/memory_claim2/)
- [Detection experiment records](../results/detect/)
- [Cross-environment methodology](../results/cross_environment/README.md)

### 3.3 Measurement protocol

Explain:

- Base and ASan builds.
- Timing protocols.
- VmPeak and VmHWM.
- Measured repetitions.
- Warm-up exclusion where applicable.
- Ratio-of-means calculation.
- Sample standard deviation.
- Unweighted benchmark-level aggregation.

Source:
[Statistical conventions](STATISTICAL_CONVENTIONS.md)

### 3.4 Replication deviations

Explain differences in workloads, hardware, software versions,
timing methods and memory measurement.

Source:
[Replication deviations](DEVIATIONS.md)

## 4. Runtime Overhead Evaluation

Proposed lead: 任奕安

Suggested length: 400-500 words.

### 4.1 Week 2 array_update experiment

Discuss:

- Three batches.
- Five measured runs per build per batch.
- Fifteen measured runs per build overall.
- Thirty measured executions across both builds.
- Overall slowdown of 31.19%.

Use the recorded mean and sample SD values.

Sources:

- [Runtime results](../results/performance/)
- [Published analysis](../results/performance/performance_analysis.txt)
- [Runtime comparison dataset](../results/report/paper_vs_ours_runtime.csv)

### 4.2 Comparison with the original paper

Use Figure 1:

[Paper vs. ours runtime figure](../results/figures/paper_vs_ours_runtime.png)

The paper reports 73% average slowdown.
The array_update result is not a direct SPEC CPU2006 replication.

Do not interpret the numerical difference as proof that
modern ASan is faster than historical ASan.

Claim 1 verdict: Partially supported.

## 5. Memory Overhead Evaluation

Proposed lead: 葉景威

Suggested length: 400-500 words.

### 5.1 Memory metric selection

Explain:

- Peak virtual address space (VmPeak).
- Peak resident set size (VmHWM).
- Large ASan virtual-address-space reservations.
- Why VmHWM is used as the primary resident-memory proxy.

### 5.2 Four-benchmark memory matrix

Describe two separately analyzed sessions:

- 20261121T051205Z.
- 20261121T051259Z.

Each session includes four benchmarks, two builds and
three measured repetitions per build.

The two sessions contain 48 measured executions in total.

Use Figure 2 and the supplementary memory figures.

Sources:

- [Memory result index](../results/memory_claim2/README.md)
- [Session 1](../results/memory_claim2/20261121T051205Z/)
- [Session 2](../results/memory_claim2/20261121T051259Z/)
- [Figure inventory](FIGURE_INVENTORY.md)

### 5.3 Interpretation

The observed unweighted mean VmHWM ratios are approximately
1.41x and 1.40x in the two sessions.

The paper reports a 3.37x VmPeak ratio.

These metrics and workloads differ. The numerical results
are not directly comparable.

Claim 2 verdict: Inconclusive.

## 6. Memory Error Detection Evaluation

Proposed lead: 王乐樵

Suggested length: 400-500 words.

### 6.1 Intentional memory-error tests

Cover:

- Heap-buffer-overflow.
- Stack-buffer-overflow.
- Global-buffer-overflow.
- Heap-use-after-free.

Explain expected ASan diagnostics and observed outcomes.

Report:
4/4 selected buggy cases produced the expected diagnostics.

### 6.2 Clean-control evaluation

Report:

- Base normal exits: 12/12.
- ASan normal exits: 12/12.
- Total normal exits: 24/24.
- Observed ASan false positives: 0/12.

Do not treat absent ASan reports as proof of universal
program correctness or a zero population false-positive rate.

### 6.3 Interpretation

Use Figure 3:

[Detection matrix](../results/figures/claim3_detection_matrix.png)

Sources:

- [Detection methodology](DETECTION.md)
- [Detection summary](../results/detect/summary.md)
- [Clean-control dataset](../results/detect/false_positive/summary.csv)

Claim 3 verdict: Supported for the tested cases.

## 7. Extension I: Workload Scaling

Proposed lead: 任奕安

Suggested length: 400-500 words.

### 7.1 Experimental design

- Four benchmarks.
- Three workload scales.
- Two build configurations.
- Three measured repetitions per configuration.
- Seventy-two measured executions.
- Seventy-two aggregate metric records.
- Warm-ups excluded.

Sources:

- [Combined dataset](../results/week3_scaling/combined/combined_results.csv)
- [Scaling analysis](../results/week3_scaling/analysis/summary.md)

### 7.2 Runtime scaling

Discuss Figure 4 and Figure 5.

Compare benchmark-specific trends rather than treating
all workloads as equally sensitive to instrumentation.

The negative measured slowdown in one b4 configuration
does not establish a stable performance improvement.

### 7.3 Memory scaling

Discuss Figure 6 and Figure 7.

Interpret resident-memory and virtual-memory metrics separately.

### 7.4 Aggregate overhead

Discuss Figure 8.

Compare the unweighted mean slowdown across scales.

Compute reported values from the combined dataset and retain
the rounding conventions defined in the statistical document.

## 8. Extension II: Cross-environment Consistency

Proposed lead: 任奕安
Supporting contributor: 葉景威

Suggested length: 300-400 words.

### 8.1 Study design

- Two reported environments.
- Three separately analyzed sessions.
- Four benchmarks at Scale 1.
- Three measured repetitions per configuration.
- Twelve benchmark-session VmHWM ratios.
- Seventy-two reused executions; zero new executions.

### 8.2 Results

Use Figure 9:

[Cross-environment comparison](../results/cross_environment/figures/vmhwm_cross_environment.png)

Compare benchmark-specific ratios and the unweighted
session means.

Discuss the relatively high b1 resident-memory ratio.

### 8.3 Interpretation

Treat this as descriptive consistency evidence.

Do not claim statistical equivalence, hardware independence
or isolated compiler effects.

Document any limits on historical environment provenance.

Sources:

- [Cross-environment analysis](../results/cross_environment/README.md)
- [Comparison dataset](../results/cross_environment/comparison.csv)

## 9. Paper vs. Ours and Discussion

Proposed lead: 贾越凯

All members review the interpretation of their experiments.

Suggested length: 500-650 words.

### 9.1 Claim-level comparison

| Claim | Original paper | Our evaluation | Verdict |
|---|---|---|---|
| Runtime | 73% average slowdown | 31.19% array_update slowdown; workload-dependent scaling | Partially supported |
| Memory | 3.37x VmPeak ratio | Approximately 1.4x VmHWM ratio | Inconclusive |
| Detection | Detection of memory errors | 4/4 selected cases; 0/12 observed clean ASan false positives | Supported for the tested cases |

### 9.2 Agreement and differences

Discuss qualitative agreement with the original paper.

Distinguish:

- Direct observations.
- Comparisons across different metrics.
- Possible explanations.
- Explanations that have not been independently tested.

### 9.3 Extension contributions

Explain how the scaling and cross-environment studies
extend the original replication objective.

The extensions do not convert this study into a full
SPEC CPU2006 or Chromium replication.

Sources:

- [Claims](CLAIMS.md)
- [Paper vs. ours](PAPER_VS_OURS.md)
- [Deviations](DEVIATIONS.md)

## 10. Threats to Validity and Reproducibility

Proposed coordinating lead: 贾越凯
Supporting reviewer: 任奕安

Suggested length: 300-400 words.

Discuss:

- Different benchmark suites.
- Modern compiler and ASan implementations.
- Hardware and virtualization differences.
- Memory metric differences.
- Periodic process-memory sampling.
- Small sample sizes.
- Limited intentional error coverage.
- Limited clean-control coverage.
- Historical environment and source provenance.
- Missing evidence documented by the Week 4 audit.
- Incomplete isolation of host and compiler effects.

Do not claim that all raw data or regenerated figures
were verified unless the recorded audit supports it.

Sources:

- [Reproducibility documentation](REPRODUCIBILITY.md)
- [Actual audit records](../results/audit/)
- [Statistical conventions](STATISTICAL_CONVENTIONS.md)

## 11. Conclusion

Proposed lead: 任奕安

Suggested length: 150-250 words.

Answer the research questions.

Summarize the three qualified claim verdicts and the two
extension studies.

State that the results support selected ASan behaviors,
while the original paper's numerical performance and
memory results have not been directly reproduced.

Avoid introducing new numerical results or new explanations.

## References

Proposed coordinating lead: 贾越凯

Include at least the primary paper:

Konstantin Serebryany, Derek Bruening, Alexander Potapenko,
and Dmitry Vyukov.
AddressSanitizer: A Fast Address Sanity Checker.
USENIX Annual Technical Conference, 2012.

Additional references may include relevant LLVM/Clang
documentation and Linux process-memory documentation.

Verify bibliographic details and actual cited versions.

Do not add references that were not consulted.

## Appendices

Subject to course requirements:

- Appendix A: Environment and compiler configurations.
- Appendix B: Benchmark and execution commands.
- Appendix C: Supplementary figures and numerical tables.
- Appendix D: Reproducibility and audit records.
- Appendix E: Individual contributions, if required.

## Figure plan

The repository figure numbers below are identifiers from
the current figure inventory. Final report numbering may
change according to the order of appearance.

| Repository figure | Topic | Report section |
|---|---|---|
| 1 | Paper vs. ours runtime | Section 4 |
| 2 | VmHWM memory bars | Section 5 |
| 3 | Detection and clean controls | Section 6 |
| 4 | Runtime by workload scale | Section 7 |
| 5 | Slowdown by workload scale | Section 7 |
| 6 | VmHWM ratio by scale | Section 7 |
| 7 | VmPeak ratio by scale | Section 7 |
| 8 | Average slowdown by scale | Section 7 |
| 9 | Cross-environment VmHWM | Section 8 |

Use supplementary figures where appropriate.

The authoritative file paths and generation scripts are
listed in [FIGURE_INVENTORY.md](FIGURE_INVENTORY.md).

## Writing workflow

1. Review this outline with all group members.
2. Draft assigned sections independently.
3. Use the repository data as the numerical source of truth.
4. Exchange sections for technical peer review.
5. Integrate terminology, references and figure numbering.
6. Write the abstract and conclusion last.
7. Complete the final report checklist.

See [CONTRIBUTIONS.md](CONTRIBUTIONS.md) and
[FINAL_REPORT_CHECKLIST.md](FINAL_REPORT_CHECKLIST.md).

See the [final report key results](../results/report/final_report_key_results.md) for a numerical evidence summary.

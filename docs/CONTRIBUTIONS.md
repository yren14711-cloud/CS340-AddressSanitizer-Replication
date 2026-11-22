# Group Contributions

## 1. Purpose

This document summarizes the principal experimental,
software, analysis and integration contributions of the
four group members.

It supplements the existing [CREDITS.md](../CREDITS.md)
rather than replacing earlier contribution records.

The contribution descriptions should be reviewed by
all members before final report submission.

Commit counts alone are not used to measure individual
effort or contribution percentages.

## 2. Group members

| Name | Student ID | Principal responsibility |
|---|---|---|
| 任奕安 | 1240014055 | Group coordination, runtime, scaling and integration |
| 葉景威 | 1240004926 | Resident-memory evaluation |
| 王乐樵 | 5260001105 | Memory-error detection and clean controls |
| 贾越凯 | 1230022503 | Paper comparison and report evidence organization |

## 3. Individual contributions

### 任奕安 (1240014055)

Principal contributions:

- Week 2 array_update runtime evaluation.
- Runtime measurement analysis.
- Week 3 workload-scaling experiment.
- Analysis across four benchmarks and three workload scales.
- Workload-scaling result organization and visualization.
- Week 4 integration of the group experiment results.
- Integration of the Claim 3 detection evidence.
- Detection matrix visualization and figure inventory update.
- Cross-environment resident-memory analysis.
- Statistical reporting convention standardization.
- Reproducibility audit and evidence-chain organization.
- Final report outline and contribution organization.

Representative evidence:

- [Runtime evaluation](../results/performance/)
- [Workload-scaling analysis](../results/week3_scaling/analysis/summary.md)
- [Cross-environment analysis](../results/cross_environment/)
- [Detection visualization script](../scripts/plot_claim3_detection.py)
- [Statistical conventions](STATISTICAL_CONVENTIONS.md)
- [Reproducibility documentation](REPRODUCIBILITY.md)

### 葉景威 (1240004926)

Principal contributions:

- Claim 2 resident-memory evaluation.
- Four-benchmark memory measurement matrix.
- Repeated memory measurement sessions.
- Experiment environment documentation.
- Memory data analysis and visualization.
- VmPeak and VmHWM interpretation.
- Claim 2 evidence and replication-deviation updates.

Representative evidence:

- [Memory experiment index](../results/memory_claim2/README.md)
- [Memory session 1](../results/memory_claim2/20261121T051205Z/)
- [Memory session 2](../results/memory_claim2/20261121T051259Z/)
- [Memory analysis script](../results/memory_claim2/analyze_memory_claim2.py)

The Week 4 cross-environment analysis reuses the two
memory sessions contributed by this member.

### 王乐樵 (5260001105)

Principal contributions:

- Memory-error detection experiment.
- Selected intentional memory-error cases.
- ASan diagnostic investigation.
- Clean-control evaluation for b1-b4.
- Repeated Base and ASan clean-control executions.
- False-positive evidence organization.
- Detection result documentation.

Representative evidence:

- [Detection methodology](DETECTION.md)
- [Detection experiment results](../results/detect/)
- [Detection runner](../scripts/run_detection.sh)
- [Clean-control runner](../scripts/run_false_positive.sh)
- [Clean-control dataset](../results/detect/false_positive/summary.csv)

The Week 4 detection matrix visualizes these experiment
outcomes. Experiment execution and integration visualization
are credited separately.

### 贾越凯 (1230022503)

Principal contributions:

- Comparison between the original paper and our results.
- Report-level runtime comparison dataset.
- Data-driven runtime comparison visualization.
- Claim-level comparison and interpretation.
- Initial report figure inventory organization.
- Evidence organization for final report preparation.

Representative evidence:

- [Paper vs. ours](PAPER_VS_OURS.md)
- [Runtime comparison dataset](../results/report/paper_vs_ours_runtime.csv)
- [Runtime comparison generator](../scripts/plot_paper_vs_ours.py)
- [Figure inventory](FIGURE_INVENTORY.md)

## 4. Collaborative contributions

The final integrated project combines the four members'
experiment records, analyses and report-level evidence.

Cross-environment analysis combines the workload-scaling
measurements with the two contributed memory sessions.

The Claim 3 detection matrix combines the original detection
results and clean-control records with Week 4 visualization.

These derived analyses do not represent new independent
experimental executions.

Shared files may contain contributions from multiple
members and subsequent integration edits.

## 5. Proposed final report writing assignments

The following assignments are planned responsibilities.
They do not imply that the final report sections have
already been written.

| Report section | Proposed lead | Supporting reviewers |
|---|---|---|
| Abstract | 任奕安 | All |
| Introduction | 任奕安 | All |
| Background and ASan design | 王乐樵 | 任奕安 |
| Experimental methodology | 任奕安 | All |
| Runtime overhead | 任奕安 | 贾越凯 |
| Memory overhead | 葉景威 | 任奕安 |
| Detection evaluation | 王乐樵 | 任奕安 |
| Workload scaling | 任奕安 | 贾越凯 |
| Cross-environment analysis | 任奕安 | 葉景威 |
| Paper vs. ours and discussion | 贾越凯 | All |
| Threats to validity | 贾越凯 | 任奕安 and experiment owners |
| Conclusion | 任奕安 | All |
| References and citation consistency | 贾越凯 | All |
| Final report integration | 任奕安 | All |

## 6. Review responsibilities

Each member should:

- Verify the numerical results from their experiments.
- Check the corresponding figures and source references.
- Document limitations relevant to their experiments.
- Review the assigned report sections.
- Confirm the accuracy of their contribution statement.

The coordinating member consolidates the final draft,
resolves terminology and cross-section consistency,
and manages the integration submission.

## 7. Contribution statement approval

Final acknowledgement of individual contributions
remains subject to member review and course requirements.

No contribution percentages or claims of completed final
report authorship are assigned by this planning document.

See [REPORT_OUTLINE.md](REPORT_OUTLINE.md).

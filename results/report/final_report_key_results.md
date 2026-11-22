# Final Report Key Results

This report is an evidence index generated from
existing experiment records. It introduces no new runs.

## 1. Week 2 runtime

- Overall reported slowdown: 31.19%.
- Runtime ratio corresponding to the reported slowdown: 1.3119x.
- Measured repetitions: 15 per build.
- Total measured executions: 30.
- Source: [published analysis](../performance/performance_analysis.txt).

## 2. Workload scaling

| Scale | Benchmark | Slowdown (%) | VmHWM ratio |
|---|---|---:|---:|
| 1 | b1_malloc_text | 561.16 | 2.0132x |
| 1 | b2_pointer_chase | 36.34 | 1.1807x |
| 1 | b3_matmul | 183.50 | 1.2510x |
| 1 | b4_string_scan | -5.67 | 1.1615x |
| 1 | **Unweighted mean** | **193.83** | **1.4016x** |
| 2 | b1_malloc_text | 576.51 | 1.9698x |
| 2 | b2_pointer_chase | 6.77 | 1.0959x |
| 2 | b3_matmul | 97.91 | 1.0704x |
| 2 | b4_string_scan | 27.70 | 1.1455x |
| 2 | **Unweighted mean** | **177.22** | **1.3204x** |
| 3 | b1_malloc_text | 591.87 | 1.9845x |
| 3 | b2_pointer_chase | 7.22 | 1.0686x |
| 3 | b3_matmul | 105.32 | 1.0326x |
| 3 | b4_string_scan | 34.41 | 1.3536x |
| 3 | **Unweighted mean** | **184.71** | **1.3598x** |

Source: [combined scaling dataset](../week3_scaling/combined/combined_results.csv).

The 72 aggregate metric records are distinct from
the 72 measured executions.

## 3. Cross-environment resident-memory results

| Benchmark | Ren Scale 1 | Ye Session 1 | Ye Session 2 |
|---|---:|---:|---:|
| b1_malloc_text | 2.0132x | 2.0503x | 2.0160x |
| b2_pointer_chase | 1.1807x | 1.1841x | 1.1837x |
| b3_matmul | 1.2510x | 1.2541x | 1.2557x |
| b4_string_scan | 1.1615x | 1.1617x | 1.1614x |
| **Unweighted mean** | **1.4016x** | **1.4126x** | **1.4042x** |

Source: [cross-environment comparison](../cross_environment/comparison.csv).

The two Ye sessions comprise the 48 measured executions
of the dedicated Claim 2 memory matrix.

The cross-environment analysis reuses 72 measured
executions, including those 48 memory executions.
No new executions are introduced.

## 4. Detection results

| Metric | Result |
|---|---:|
| Selected buggy cases detected (published summary) | 4/4 |
| Base clean normal exits | 12/12 |
| ASan clean normal exits | 12/12 |
| Total clean normal exits | 24/24 |
| Observed ASan false positives | 0/12 |

Sources:

- [Detection summary](../detect/summary.md)
- [Clean controls](../detect/false_positive/summary.csv)

## 5. Claim verdicts

| Claim | Verdict |
|---|---|
| Runtime overhead | Partially supported |
| Memory overhead | Inconclusive |
| Detection capability | Supported for the tested cases |

See [Claims](../../docs/CLAIMS.md) and
[Statistical conventions](../../docs/STATISTICAL_CONVENTIONS.md).

## 6. Reproducibility status

Interpret the results in accordance with the actual
[Week 4 audit records](../audit/).

The summary is not a replacement for the original
measurements, environment records or analysis scripts.

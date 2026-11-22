# Week 3: Workload Scaling Analysis

## 1. Objective

This extension investigates how AddressSanitizer (ASan) runtime and memory overhead changes with increasing workload size across four custom benchmarks.

The experiment is motivated by *AddressSanitizer: A Fast Address Sanity Checker* (Serebryany et al., USENIX ATC 2012), particularly its evaluation of runtime slowdown in Figure 2 and memory overhead in Table 1.

## 2. Experimental Setup

Four custom benchmarks were evaluated:

- **b1_malloc_text:** Frequent small heap allocations, deallocations, and byte-level accesses.
- **b2_pointer_chase:** Dependent random accesses over a large permuted index array.
- **b3_matmul:** Dense floating-point matrix multiplication.
- **b4_string_scan:** Repeated byte-wise text scanning with a dynamically expanding offsets array.

Each benchmark was executed at workload scales 1, 2, and 3, using both native (Base) and AddressSanitizer-instrumented binaries.

Each configuration included one discarded warm-up execution and three measured repetitions. The experiment recorded wall-clock execution time, VmPeak, and VmHWM.

The experiments were performed under Ubuntu on WSL2 using Clang 21.1.8 with `-O2`. ASan settings included a 32-byte redzone, zero quarantine size, disabled allocation stack tracing, and disabled leak detection.

## 3. Runtime Scaling Results

The runtime slowdown was calculated as:

`Slowdown (%) = (Mean ASan Wall Time / Mean Base Wall Time - 1) × 100`

| Benchmark | Scale 1 | Scale 2 | Scale 3 |
|---|---:|---:|---:|
| b1_malloc_text | +561.2% | +576.5% | +591.9% |
| b2_pointer_chase | +36.3% | +6.8% | +7.2% |
| b3_matmul | +183.5% | +97.9% | +105.3% |
| b4_string_scan | -5.7% | +27.7% | +34.4% |
| **Unweighted mean** | **+193.8%** | **+177.2%** | **+184.7%** |

**Figure 1 — Runtime Scaling:** `figures/runtime_by_scale.png`

Base and ASan execution times increased as workload sizes increased. However, the magnitude of this growth varied by benchmark. Matrix multiplication exhibited particularly strong growth because its dominant computational complexity is approximately cubic in matrix dimension.

**Figure 2 — ASan Runtime Slowdown:** `figures/slowdown_by_scale.png`

The results demonstrate substantial workload-dependent variation. The allocation-intensive b1 benchmark consistently exhibited the highest overhead, while b2 showed much lower relative overhead at larger scales.

The negative slowdown measured for b4 at Scale 1 should not be interpreted as a proven performance improvement, given the small sample size and measurement variability.

## 4. Resident Memory Analysis

Resident memory overhead was calculated using the mean VmHWM values:

`VmHWM Ratio = Mean ASan VmHWM / Mean Base VmHWM`

| Benchmark | Scale 1 | Scale 2 | Scale 3 |
|---|---:|---:|---:|
| b1_malloc_text | 2.013x | 1.970x | 1.985x |
| b2_pointer_chase | 1.181x | 1.096x | 1.069x |
| b3_matmul | 1.251x | 1.070x | 1.033x |
| b4_string_scan | 1.162x | 1.145x | 1.354x |
| **Unweighted mean** | **1.402x** | **1.320x** | **1.360x** |

**Figure 3 — Resident Memory Overhead:** `figures/vmhwm_ratio_by_scale.png`

The allocation-intensive benchmark b1 maintained approximately twice the peak resident memory of its native counterpart.

In contrast, b2 and b3 exhibited decreasing resident memory ratios as workload size increased. The b4 benchmark showed an increased memory ratio at Scale 3, requiring further investigation into allocation and memory management behavior.

Overall, the resident memory overhead did not increase monotonically with workload size across all benchmarks.

## 5. Virtual Memory Analysis

**Figure 4 — Virtual Memory Overhead:** `figures/vmpeak_ratio_by_scale.png`

The ASan-instrumented binaries exhibited extremely large VmPeak values, approximately 21.47 billion kB.

This observation is consistent with ASan reserving substantial virtual address space for shadow-memory mappings.

VmPeak must not be interpreted as physical RAM usage. Furthermore, modern 64-bit ASan virtual address-space behavior differs from the environment used in the 2012 evaluation.

Therefore, VmPeak and VmHWM are analyzed separately.

## 6. Aggregate Performance Trend

**Figure 5 — Average Runtime Slowdown:** `figures/average_slowdown_by_scale.png`

The unweighted average slowdown was 193.8%, 177.2%, and 184.7% at Scales 1, 2, and 3, respectively.

The average did not follow a monotonic trend. This observation suggests that increasing input size does not necessarily produce a corresponding increase in relative ASan slowdown.

The aggregate is strongly influenced by the allocation-intensive b1 benchmark and should always be interpreted alongside individual benchmark results.

## 7. Comparison with the Original Paper

The original AddressSanitizer paper reported an average runtime slowdown of 73% on SPEC CPU2006 and a memory increase of 3.37x using VmPeak.

Our experiment used four purpose-built microbenchmarks instead of SPEC CPU2006. Consequently, the overall slowdown values are not directly comparable.

Nevertheless, the qualitative behavior is consistent with the paper's observation that ASan overhead depends strongly on workload characteristics, particularly memory allocation patterns and instrumented memory accesses.

**Verdict:** The workload-dependence of ASan overhead is supported by this reduced-scale extension. Direct numerical reproduction of the paper's aggregate results remains inconclusive because the benchmarks, environment, and memory measurement conditions differ.

## 8. Limitations

- Only three workload sizes were tested.
- Each configuration included three measured repetitions.
- The experiment ran under WSL2, which may introduce additional scheduling variability.
- Base and ASan configurations were executed sequentially rather than fully randomized.
- Wall-clock time included process startup and execution overhead.
- Memory measurements relied on periodic `/proc` sampling, which may miss the final peak for short-running processes.
- VmPeak and VmHWM measure different aspects of memory usage.
- The custom benchmarks are not equivalent to the paper's SPEC CPU2006 workloads.
- These observations establish correlations, not definitive causal explanations for individual performance differences.

## 9. Conclusion

The Week 3 workload scaling experiment demonstrates that AddressSanitizer overhead varies substantially across different workload types and input sizes.

Allocation-intensive operations exhibited the highest runtime and resident memory overhead in the tested suite. Memory-access-intensive workloads also experienced significant runtime overhead even with relatively few allocations.

The results support the qualitative claim that ASan overhead is workload-dependent. However, they do not directly reproduce the original paper's aggregate performance or memory figures.

## References

Serebryany, K., Bruening, D., Potapenko, A., and Vyukov, D. (2012). *AddressSanitizer: A Fast Address Sanity Checker.* USENIX Annual Technical Conference.

https://www.usenix.org/system/files/conference/atc12/atc12-final39.pdf

## Week 4 reporting clarification

The 72 aggregate metric records are distinct from the
72 measured executions. Warm-ups are excluded.

The reported overhead averages use equal benchmark weights.

The approximately 21.47 billion Linux-reported kB of ASan
virtual address space corresponds to approximately 20 TiB.

See [Statistical and Reporting Conventions](../../../docs/STATISTICAL_CONVENTIONS.md).

# Claim 2 -- memory overhead, parsed results

- source log: `results/memory_claim2/20261121T051205Z/runs.log`
- benchmarks: 4; configurations: base / asan; measured repetitions per bar: [3]
- metric definition: VmHWM (peak resident set) and VmPeak, both sampled from /proc/<pid>/status
- scale: 1; ASAN_OPTIONS=quarantine_size_mb=0:malloc_context_size=0:detect_leaks=0:redzone=32

## Session environment

- session_stamp: `20261121T051205Z`
- cpu: `Intel(R) Core(TM) i5-14600KF`
- cpu_cores: `20`
- memtotal: `16265896 kB`
- os: `Ubuntu 24.04 LTS`
- kernel: `6.18.33.2-microsoft-standard-WSL2`
- clang: `Ubuntu clang version 18.1.3 (1ubuntu1)`
- wsl: `2.7.14.0`
- workdir: `/root/work/cs340-wk3-20261121 (filesystem ext4)`

## Table A -- VmHWM (peak resident set), the reported metric

| Benchmark | n | Base VmHWM (kB) | ASan VmHWM (kB) | Ratio ASan/Base |
|---|---|---|---|---|
| b1_malloc_text | 3 | 35366.7 +/- 1709.6 | 72513.3 +/- 709.5 | 2.05x |
| b2_pointer_chase | 3 | 17734.7 +/- 2.3 | 21000.0 +/- 34.2 | 1.18x |
| b3_matmul | 3 | 13501.3 +/- 2.3 | 16932.0 +/- 66.1 | 1.25x |
| b4_string_scan | 3 | 103065.3 +/- 2.3 | 119729.3 +/- 14.0 | 1.16x |

Unweighted mean of the four per-benchmark ratios: **1.41x** (sample SD across the four benchmarks: 0.43; n = 4 benchmarks).

The paper's Table 1 average is 3.37x over SPEC CPU2006, measured on VmPeak.
Our figure is a VmHWM proxy on four microbenchmarks: it shows that the resident-memory
overhead measured in this environment is well below 3.37x. It does not reproduce Table 1.

Table A reads: Base and ASan are the mean and 1 sample SD of the 3 measured runs;
ratio = mean(ASan VmHWM) / mean(Base VmHWM) for the same benchmark and session.

## Table B -- VmPeak, for completeness only (NOT usable as memory overhead)

| Benchmark | n | Base VmPeak (kB) | ASan VmPeak (kB) | Ratio ASan/Base |
|---|---|---|---|---|
| b1_malloc_text | 3 | 36572.0 +/- 1596.8 | 21474887752.0 +/- 0.0 | 587195x |
| b2_pointer_chase | 3 | 19080.0 +/- 0.0 | 21474904140.0 +/- 0.0 | 1125519x |
| b3_matmul | 3 | 14848.0 +/- 0.0 | 21474900952.0 +/- 0.0 | 1446316x |
| b4_string_scan | 3 | 117388.0 +/- 0.0 | 21475035232.0 +/- 0.0 | 182941x |

Warning: every ASan run reports VmPeak ~= 21 474 900 000 kB (about 20 TB) because the runtime reserves the shadow address space at start-up. Within one benchmark the value is identical from run to run; across the four benchmarks it varies by 147480 kB (about 144 MiB, i.e. < 0.001% of 20 TB) with the shadow mapping layout. It is a property of the reservation, not of the workload, so the VmPeak ratio must not be reported as Claim 2. The paper's Table 1 uses VmPeak; that is precisely the deviation this replication has to state.

## Per-run raw values (traceability)

| Benchmark | Config | run1 | run2 | run3 | mean +/- SD |
|---|---|---|---|---|---|
| b1_malloc_text | base VmHWM (kB) | 35892 | 36752 | 33456 | 35366.7 +/- 1709.6 |
| b1_malloc_text | asan VmHWM (kB) | 73028 | 71704 | 72808 | 72513.3 +/- 709.5 |
| b2_pointer_chase | base VmHWM (kB) | 17736 | 17736 | 17732 | 17734.7 +/- 2.3 |
| b2_pointer_chase | asan VmHWM (kB) | 20996 | 20968 | 21036 | 21000.0 +/- 34.2 |
| b3_matmul | base VmHWM (kB) | 13504 | 13500 | 13500 | 13501.3 +/- 2.3 |
| b3_matmul | asan VmHWM (kB) | 16936 | 16996 | 16864 | 16932.0 +/- 66.1 |
| b4_string_scan | base VmHWM (kB) | 103064 | 103064 | 103068 | 103065.3 +/- 2.3 |
| b4_string_scan | asan VmHWM (kB) | 119728 | 119716 | 119744 | 119729.3 +/- 14.0 |

## Runtime context (not the Claim 2 metric)

| Benchmark | Base wall (ms) | ASan wall (ms) | Slowdown |
|---|---|---|---|
| b1_malloc_text | 163.7 +/- 11.8 | 975.7 +/- 21.0 | +496.1% |
| b2_pointer_chase | 997.7 +/- 21.5 | 1787.7 +/- 1271.7 | +79.2% |
| b3_matmul | 64.7 +/- 0.6 | 150.3 +/- 0.6 | +132.5% |
| b4_string_scan | 341.0 +/- 23.5 | 390.7 +/- 12.4 | +14.6% |

Wall-time outliers (host stall, kept in the data, do not affect VmHWM):

- b2_pointer_chase / asan: wall_ms 1042, 1065, 3256

## Checks

- repetitions per (benchmark, configuration): [3] (expected 3)
- RESULT lines: 24 (expected 24)
- non-zero exits: 0
- ASan VmPeak spread over all ASan runs: 147480 kB

## Figure C -- comparison across sessions

Ratio per benchmark in each session; sessions are kept separate and never pooled into one n.

| Session | Environment | b1_malloc_text | b2_pointer_chase | b3_matmul | b4_string_scan |
|---|---|---|---|---|---|
| this session (20261121T051205Z) | kernel 6.18.33.2-microsoft-standard-WSL2 | 2.05x | 1.18x | 1.25x | 1.16x |
| kernel 5.10 (Nov 14) | Ubuntu 24.04, kernel 5.10.16.3, clang 18.1.3 | 2.10x | 1.26x | 1.42x | 1.16x |
| kernel 6.18 (Nov 14) | Ubuntu 24.04, kernel 6.18.33.2, clang 18.1.3 | 2.03x | 1.19x | 1.25x | 1.16x |

## Figures

- `results/memory_claim2/20261121T051205Z/figures/fig_a_vmhwm_bars.png`
- `results/memory_claim2/20261121T051205Z/figures/fig_b_vmhwm_ratio.png`
- `results/memory_claim2/20261121T051205Z/figures/fig_c_ratio_sessions.png`

CSV: `results/memory_claim2/20261121T051205Z/results.csv` (24 rows).

## Week 4 reporting clarification

The numerical VmHWM measurements are retained unchanged.
The paper's 3.37x VmPeak result is not directly comparable.

The virtual reservation is approximately 20 TiB.
The cause of wall-time outliers has not been established;
all measured observations are retained.

See [Statistical and Reporting Conventions](../../../docs/STATISTICAL_CONVENTIONS.md).

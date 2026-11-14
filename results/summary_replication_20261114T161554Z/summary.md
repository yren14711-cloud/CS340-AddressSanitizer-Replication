# Parsed results

- source log: `results/logs/20261114T161554Z/runs.log`
- benchmarks: 4, configurations: base / asan
- wall time around fork+exec, VmPeak and VmHWM read from /proc/<pid>/status

## Per-benchmark measurements (mean +/- std)

| Benchmark | n | base wall (ms) | asan wall (ms) | slowdown | base VmPeak (kB) | asan VmPeak (kB) | mem ratio |
|---|---|---|---|---|---|---|---|
| b1_malloc_text | 3 | 178.0 +/- 13.0 | 1057.3 +/- 12.4 | +494.0% | 37188 +/- 751 | 21474887752 +/- 0 | 577468.21x |
| b2_pointer_chase | 3 | 1144.3 +/- 47.7 | 1154.7 +/- 23.5 | +0.9% | 19080 +/- 0 | 21474904140 +/- 0 | 1125519.08x |
| b3_matmul | 3 | 65.0 +/- 1.0 | 150.3 +/- 0.6 | +131.3% | 14848 +/- 0 | 21474900952 +/- 0 | 1446316.07x |
| b4_string_scan | 3 | 318.7 +/- 1.2 | 420.3 +/- 13.3 | +31.9% | 117388 +/- 0 | 21475035232 +/- 0 | 182940.63x |

## Paper vs. ours

The aggregate below is an unweighted mean over the benchmarks above. It is **not** directly comparable to the paper's average: the paper averages over SPEC CPU2006, this replication averages over four small benchmarks. Both the difference and its likely cause belong in the analysis section.

| Metric | Paper (ATC 2012, SPEC CPU2006) | Ours (this run) | Absolute gap | Relative gap |
|---|---|---|---|---|
| Average slowdown | 73.0% | +164.5% | +91.5 pp | +125.4% |
| Average memory increase (VmPeak) | 3.37x | 833061.00x | +833057.63x | +24719810.9% |

All runs exited 0.

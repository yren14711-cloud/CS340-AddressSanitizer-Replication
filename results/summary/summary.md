# Parsed results

- source log: `results/logs/20261114T155152Z/runs.log`
- benchmarks: 4, configurations: base / asan
- wall time around fork+exec, VmPeak and VmHWM read from /proc/<pid>/status

## Per-benchmark measurements (mean +/- std)

| Benchmark | n | base wall (ms) | asan wall (ms) | slowdown | base VmPeak (kB) | asan VmPeak (kB) | mem ratio |
|---|---|---|---|---|---|---|---|
| b1_malloc_text | 3 | 176.7 +/- 12.4 | 1126.0 +/- 40.7 | +537.4% | 36560 +/- 955 | 21474887740 +/- 0 | 587387.52x |
| b2_pointer_chase | 3 | 1133.3 +/- 14.4 | 1184.0 +/- 26.1 | +4.5% | 19068 +/- 0 | 21474904128 +/- 0 | 1126227.40x |
| b3_matmul | 3 | 71.3 +/- 12.7 | 148.7 +/- 1.2 | +108.4% | 14836 +/- 0 | 21474900940 +/- 0 | 1447485.91x |
| b4_string_scan | 3 | 346.3 +/- 13.6 | 410.7 +/- 13.3 | +18.6% | 117376 +/- 0 | 21475035220 +/- 0 | 182959.34x |

## Paper vs. ours

The aggregate below is an unweighted mean over the benchmarks above. It is **not** directly comparable to the paper's average: the paper averages over SPEC CPU2006, this replication averages over four small benchmarks. Both the difference and its likely cause belong in the analysis section.

| Metric | Paper (ATC 2012, SPEC CPU2006) | Ours (this run) | Absolute gap | Relative gap |
|---|---|---|---|---|
| Average slowdown | 73.0% | +167.2% | +94.2 pp | +129.0% |
| Average memory increase (VmPeak) | 3.37x | 836015.04x | +836011.67x | +24807468.0% |

All runs exited 0.

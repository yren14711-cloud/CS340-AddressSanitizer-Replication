# Deviations from the paper's setup

Every change from the paper's methodology, with the original setting, the setting
actually used, and the reason. The rubric asks for this as a complete table in
the Reproduction Setup section; keep this file as the working source and copy the
final version into the report.

Status legend: **planned** = decided but not yet run; **done** = measured with
the setting shown; **TODO** = still needs a value.

| # | Item | Paper setting | Our setting | Reason | Impact on results | Status |
|---|---|---|---|---|---|---|
| 1 | Benchmark suite | SPEC CPU2006, C/C++ | 4 open benchmarks in `benchmarks/` (`b1_malloc_text`, `b2_pointer_chase`, `b3_matmul`, `b4_string_scan`) | SPEC requires a commercial licence and may not be redistributed; the repository must be cloneable and runnable by the TA[cite: 1] | The 73% figure is an average over a different mix; the reproduced average is indicative, not equal[cite: 1] | planned |
| 2 | CPU | HP Z600, 2x Intel Xeon E5620 (2010, 4 cores each, 2.4 GHz), 24 GB RAM[cite: 1] | x86_64 virtualized CPU via WSL2 (Windows 11 host)[cite: 1] | Only hardware available[cite: 1] | Absolute runtimes differ by a large factor; the relative slowdown is the comparable quantity, and it can shift because instrumented code is more sensitive to memory latency and branch prediction than uninstrumented code[cite: 1] | done |
| 3 | Operating system / kernel | 64-bit Linux, distribution and kernel version not stated in the paper[cite: 1] | Ubuntu 26.04 LTS under WSL2, kernel 6.18.54.1-microsoft-standard-WSL2[cite: 1] | The group's working environment[cite: 1] | WSL2 adds a virtualisation layer; scheduling and timer behaviour differ from bare metal[cite: 1] | done |
| 4 | Compiler | `clang -O2` (LLVM circa 2011-2012)[cite: 1] | `clang 21.1.8`, `-O2`[cite: 1] | The 2012 compiler is not installable on a current distribution[cite: 1] | Instrumentation code generation and the optimiser's treatment of it have changed substantially; this is one of the most likely causes of a gap versus 73%[cite: 1] | done |
| 5 | AddressSanitizer runtime options | 32-byte redzones, quarantine size 0, stack unwinding during malloc/free disabled[cite: 1] | `ASAN_OPTIONS=quarantine_size_mb=0:malloc_context_size=0:detect_leaks=0:redzone=32`[cite: 1] | Reproduce the paper's configuration deliberately rather than accepting modern defaults[cite: 1] | Matches the paper's caveat that quarantine overhead is excluded from the memory figures; `detect_leaks=0` because LeakSanitizer did not exist in 2012 and would change both time and memory[cite: 1] | done |
| 6 | Default runtime differences | Not applicable in 2012[cite: 1] | Modern ASan defaults are different (quarantine ~256 MB, larger redzones, leak detection on)[cite: 1] | Same as #5[cite: 1] | Any run that omits `ASAN_OPTIONS` is *not* comparable to the paper; every logged run records the options used[cite: 1] | done |
| 7 | Instrumentation scope | Benchmarks instrumented, system libraries not (ASan intercepts malloc/free)[cite: 1] | Same: only the benchmark translation unit is compiled with `-fsanitize=address`; libc is the distribution's uninstrumented build[cite: 1] | Matches the paper[cite: 1] | Interceptors and redzones behave the same way as in the paper's setup[cite: 1] | done |
| 8 | Stack-use-after-return checking | Not available in the 2012 implementation[cite: 1] | Left at the compiler default (off)[cite: 1] | Keeps the overhead comparable; the paper's numbers do not include it[cite: 1] | Avoids an extra overhead the paper never measured[cite: 1] | planned |
| 9 | Timing method | Wall-clock time of instrumented vs. reference binaries, repeated runs[cite: 1] | Wall clock around fork+exec, 1 discarded warm-up, then 3 measured repetitions, mean ± std, 1 s cooldown between runs[cite: 1] | Rubric requires mean ± std over at least three runs[cite: 1] | fork+exec adds about 1 ms per run; benchmarks are sized to run for ~0.5-1.5 s so this is below 0.3%[cite: 1] | done |
| 10 | Memory metric | `VmPeak` from `/proc/self/status`[cite: 1] | `VmPeak` sampled from `/proc/<pid>/status` every 20 ms while the process runs; `VmHWM` recorded as a cross-check[cite: 1] | A process cannot report its own `VmPeak` after exit without instrumenting the benchmark itself; polling keeps the measurement outside the measured program[cite: 1] | Sampling can only underestimate the peak, never overestimate it; on runs longer than 0.5 s the final sample is the true high-water mark[cite: 1] | done |
| 11 | Frequency scaling / turbo | Not addressed in the paper[cite: 1] | Not disabled (no control over the host power policy from WSL2)[cite: 1] | Not possible in the available environment[cite: 1] | Adds run-to-run variance, which is why results are reported as mean ± std and why all four benchmarks are measured back to back[cite: 1] | done |
| 12 | CPU pinning | Not stated in the paper[cite: 1] | Not used (default WSL2 scheduling; optional `taskset` available)[cite: 1] | Pinning reduces migration noise but changes the measurement conditions[cite: 1] | Report which of the two was used; do not mix[cite: 1] | done |
| 13 | Repetitions | "repeated runs", count not stated in the paper[cite: 1] | 3 measured repetitions + 1 warm-up per (benchmark, configuration)[cite: 1] | Rubric minimum is 3; the warm-up removes first-touch page-fault effects[cite: 1] | 3 is the minimum, not a comfortable sample; the std should be checked for stability before drawing conclusions[cite: 1] | done |
| 14 | Inputs / workload size | SPEC reference inputs[cite: 1] | `scale=1` default, one scale axis used in the extension experiment[cite: 1] | Keeps total matrix runtime in the minutes range on a laptop[cite: 1] | Smaller inputs are more cache-friendly, which can understate the instrumented slowdown[cite: 1] | done |
| 15 | Detection experiments | Reports on real Chromium bugs[cite: 1] | Small hand-written programs covering global, heap, stack overflows and use-after-free, verified in `results/detect/`[cite: 1] | Reproducing Chromium is out of scope for a course project[cite: 1] | Demonstrates the mechanism, not the paper's bug-finding record[cite: 1] | done |

## How to update this file

- Change a `TODO` to a concrete value as soon as the experiment runs, in the same
  commit that produces the log.
- Every row that says **done** must point to a log or to `results/env/environment.txt`
  that shows the setting, otherwise it is an assertion rather than a record.
- The report's table must not contain rows that are absent here.
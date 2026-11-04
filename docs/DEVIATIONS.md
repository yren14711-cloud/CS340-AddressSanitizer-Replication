# Deviations from the paper's setup

Every change from the paper's methodology, with the original setting, the setting
actually used, and the reason. The rubric asks for this as a complete table in
the Reproduction Setup section; keep this file as the working source and copy the
final version into the report.

Status legend: **planned** = decided but not yet run; **done** = measured with
the setting shown; **TODO** = still needs a value.

| # | Item | Paper setting | Our setting | Reason | Impact on results | Status |
|---|---|---|---|---|---|---|
| 1 | Benchmark suite | SPEC CPU2006, C/C++ | 4 open benchmarks in `benchmarks/` (`b1_malloc_text`, `b2_pointer_chase`, `b3_matmul`, `b4_string_scan`) | SPEC requires a commercial licence and may not be redistributed; the repository must be cloneable and runnable by the TA | The 73% figure is an average over a different mix; the reproduced average is indicative, not equal | planned |
| 2 | CPU | HP Z600, 2x Intel Xeon E5620 (2010, 4 cores each, 2.4 GHz), 24 GB RAM | TODO: record `lscpu` output of the machine used | Only hardware available | Absolute runtimes differ by a large factor; the relative slowdown is the comparable quantity, and it can shift because instrumented code is more sensitive to memory latency and branch prediction than uninstrumented code | TODO |
| 3 | Operating system / kernel | 64-bit Linux, distribution and kernel version not stated in the paper | Ubuntu 26.04 LTS under WSL2, kernel 6.18.54.1-microsoft-standard-WSL2 | The group's working environment | WSL2 adds a virtualisation layer; scheduling and timer behaviour differ from bare metal | done |
| 4 | Compiler | `clang -O2` (LLVM circa 2011-2012) | `clang 21.1.8`, `-O2` | The 2012 compiler is not installable on a current distribution | Instrumentation code generation and the optimiser's treatment of it have changed substantially; this is one of the most likely causes of a gap versus 73% | done |
| 5 | AddressSanitizer runtime options | 32-byte redzones, quarantine size 0, stack unwinding during malloc/free disabled | `ASAN_OPTIONS=quarantine_size_mb=0:malloc_context_size=0:detect_leaks=0:redzone=32` | Reproduce the paper's configuration deliberately rather than accepting modern defaults | Matches the paper's caveat that quarantine overhead is excluded from the memory figures; `detect_leaks=0` because LeakSanitizer did not exist in 2012 and would change both time and memory | done |
| 6 | Default runtime differences | Not applicable in 2012 | Modern ASan defaults are different (quarantine ~256 MB, larger redzones, leak detection on) | Same as #5 | Any run that omits `ASAN_OPTIONS` is *not* comparable to the paper; every logged run records the options used | done |
| 7 | Instrumentation scope | Benchmarks instrumented, system libraries not (ASan intercepts malloc/free) | Same: only the benchmark translation unit is compiled with `-fsanitize=address`; libc is the distribution's uninstrumented build | Matches the paper | Interceptors and redzones behave the same way as in the paper's setup | done |
| 8 | Stack-use-after-return checking | Not available in the 2012 implementation | Left at the compiler default (off) | Keeps the overhead comparable; the paper's numbers do not include it | Avoids an extra overhead the paper never measured | planned |
| 9 | Timing method | Wall-clock time of instrumented vs. reference binaries, repeated runs | Wall clock around fork+exec, 1 discarded warm-up, then 3 measured repetitions, mean ± std, 1 s cooldown between runs | Rubric requires mean ± std over at least three runs | fork+exec adds about 1 ms per run; benchmarks are sized to run for ~0.5-1.5 s so this is below 0.3% | done |
| 10 | Memory metric | `VmPeak` from `/proc/self/status` | `VmPeak` sampled from `/proc/<pid>/status` every 20 ms while the process runs; `VmHWM` recorded as a cross-check | A process cannot report its own `VmPeak` after exit without instrumenting the benchmark itself; polling keeps the measurement outside the measured program | Sampling can only underestimate the peak, never overestimate it; on runs longer than 0.5 s the final sample is the true high-water mark | done |
| 11 | Frequency scaling / turbo | Not addressed in the paper | Not disabled (no control over the host power policy from WSL2) | Not possible in the available environment | Adds run-to-run variance, which is why results are reported as mean ± std and why all four benchmarks are measured back to back | done |
| 12 | CPU pinning | Not stated in the paper | Optional `taskset -c N` via `scripts/run_experiments.sh -p N`; not used for the reported numbers unless stated | Pinning reduces migration noise but changes the measurement conditions | Report which of the two was used; do not mix | TODO |
| 13 | Repetitions | "repeated runs", count not stated in the paper | 3 measured repetitions + 1 warm-up per (benchmark, configuration) | Rubric minimum is 3; the warm-up removes first-touch page-fault effects | 3 is the minimum, not a comfortable sample; the std should be checked for stability before drawing conclusions | done |
| 14 | Inputs / workload size | SPEC reference inputs | `scale=1` default, one scale axis used in the extension experiment | Keeps total matrix runtime in the minutes range on a laptop | Smaller inputs are more cache-friendly, which can understate the instrumented slowdown | done |
| 15 | Detection experiments | Reports on real Chromium bugs | Small hand-written programs, one bug class each | Reproducing Chromium is out of scope for a course project | Demonstrates the mechanism, not the paper's bug-finding record | TODO |

## How to update this file

- Change a `TODO` to a concrete value as soon as the experiment runs, in the same
  commit that produces the log.
- Every row that says **done** must point to a log or to `results/env/environment.txt`
  that shows the setting, otherwise it is an assertion rather than a record.
- The report's table must not contain rows that are absent here.

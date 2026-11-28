# Methodology Comparison

This document compares the experimental methodology of the original
AddressSanitizer paper with the methodology used in this replication. It supports
Section 3.4 (Replication deviations) and Section 9.2 (Agreement and differences)
of the [report outline](REPORT_OUTLINE.md), and it introduces no new experiments.

The comparison is evidence-based. Every paper value below was read from the
USENIX PDF; every replication value is linked to a committed record. Where the
paper does not state a setting, this document says **not stated** rather than
inferring it. Where a repository record is incomplete, the limitation is named.

## Sources

### Original paper

Serebryany, K., Bruening, D., Potapenko, A., and Vyukov, D. "AddressSanitizer: A
Fast Address Sanity Checker." *USENIX Annual Technical Conference (USENIX ATC
'12)*, 2012. <https://www.usenix.org/system/files/conference/atc12/atc12-final39.pdf>

Page references are PDF pages of the 10-page USENIX copy. The relevant locations
are:

- **Section 4, "Evaluation", PDF p. 6** — SPEC CPU2006 benchmark selection, HP
  Z600 hardware, `clang -O2`, AddressSanitizer options, the 73% average slowdown,
  the 3.37x average memory result, and **Table 1**.
- **Figure 2, PDF p. 7** — per-benchmark slowdown on SPEC CPU2006 and the average
  bar.
- **Section 4.2, PDF p. 7** — Chromium deployment and the reported bug counts.
- **Section 3.6, PDF p. 5** — the qualitative "no false positives" statement,
  together with the undesirable reports that were fixed.
- **Section 4.3, PDF p. 8** — the default AddressSanitizer controls used while
  testing Chromium (stack-unwinding depth 30, quarantine 256 MB, redzone 128
  bytes).

### Replication evidence

- Claims, deviations and conventions:
  [CLAIMS.md](CLAIMS.md), [DEVIATIONS.md](DEVIATIONS.md),
  [STATISTICAL_CONVENTIONS.md](STATISTICAL_CONVENTIONS.md),
  [PAPER_VS_OURS.md](PAPER_VS_OURS.md).
- Runtime (Claim 1):
  [performance_analysis.txt](../results/performance/performance_analysis.txt),
  [benchmark_summary.csv](../results/performance/benchmark_summary.csv),
  [paper_vs_ours_runtime.csv](../results/report/paper_vs_ours_runtime.csv),
  the runner logs `results/performance/benchmark_runs_batch1.log` through
  `batch3.log`, and the report-level summary
  [final_report_key_results.md](../results/report/final_report_key_results.md).
- Memory (Claim 2):
  [session 1 summary](../results/memory_claim2/20261121T051205Z/summary.md),
  [session 1 results.csv](../results/memory_claim2/20261121T051205Z/results.csv),
  [session 2 summary](../results/memory_claim2/20261121T051259Z/summary.md),
  and [cross-environment comparison](../results/cross_environment/comparison.csv).
- Detection (Claim 3):
  [detection summary](../results/detect/summary.md),
  [clean-control summary.csv](../results/detect/false_positive/summary.csv),
  and [detection matrix](../results/figures/claim3_detection_matrix.png).
- Environment records:
  [results/env/environment.txt](../results/env/environment.txt),
  [b1–b4 environment record](../results/env/environment_b1-b4_20261114T155323Z.txt),
  [Claim 2 session environment](../results/memory_claim2/20261121T051205Z/environment.txt),
  [detection environment](../results/detect/environment.txt),
  and [false-positive environment](../results/detect/false_positive/environment.txt).
- Audit:
  [verification_report.txt](../results/audit/verification_report.txt) and
  [environment_review.txt](../results/audit/environment_review.txt).

### Recorded replication environments

| Dataset | Host and operating environment (as recorded) | Compiler and flags |
|---|---|---|
| Claim 1 runtime (`array_update`) | WSL2 x86-64. README §8 reports an AMD Ryzen 7 8845H with 7.4 GiB visible memory; the Week 2 raw logs record only the compiler. CPU model is therefore **not independently confirmed**. | Clang 21.1.8, `-O2`, `CLOCK_MONOTONIC` |
| Claim 2 memory (b1–b4) | Intel Core i5-14600KF (20 threads); Ubuntu 24.04; WSL2 kernel 6.18.33.2; MemTotal 16,265,896 kB in the 21 November sessions | Clang 18.1.3, `-O2` |
| Workload scaling, Environment A | WSL2 kernel 6.18.58.1, 16 threads; AMD Ryzen 7 8845H per the cross-environment README | Clang 21.1.8, `-O2` |
| Detection and clean controls | Ubuntu 24.04.5; Linux 6.8.0-1070-azure (Codespaces host) | Clang 18.1.3; `-O1` for the error cases, `-O2` for clean controls |

### Verification notes

- **Verified from the paper.** The 73% average, the 3.37x average, the HP Z600
  hardware, the `clang -O2` build, the 32-byte redzones/quarantine-0 settings,
  the VmPeak-at-termination protocol, and the Chromium bug counts all appear on
  the pages listed above.
- **Not stated in the paper.** The exact LLVM/Clang revision, the Linux
  distribution and kernel, the SPEC CPU2006 input set, the number of measured
  repetitions, any standard deviation or confidence interval for 73% and 3.37x,
  the aggregation rule behind those averages, and the AddressSanitizer revision.
  These are marked *not stated*; they are not inferred from later sources.
- **Table 1 aggregation is not reconstructible from the printed totals.** The
  instrumented and original column totals are 24,467 MB and 8,171 MB, whose ratio
  is approximately 2.99x, not the reported 3.37x. The 3.37x therefore appears to
  be an average computed by a rule the paper does not state. It is cited below as
  reported, not recomputed.
- **Claim 1 host is incomplete.** The Week 2 runner logs record the compiler
  (Clang 21.1.8) but no host line. The committed
  [environment record](../results/env/environment.txt) is dated 7 November 2026
  and names an Intel i7-13650HX host, while the array_update runs are dated 9
  November 2026. The CPU model in README §8 is therefore a claim without a
  per-session record; this document relies only on "WSL2 x86-64, Clang 21.1.8".
- **Memory host memory changed between sessions.** The 14 November record lists
  26,100,652 kB and the 21 November sessions list 16,265,896 kB. Ratios are
  computed within a session, so this does not invalidate them, but absolute
  memory values are not comparable across sessions.
- **Detection ran on a different host class.** The detection and clean-control
  records come from an Azure/Codespaces Linux host, not from either WSL2 host used
  for runtime and memory. Detection results therefore cannot be used to infer
  runtime overhead, and vice versa.
- **Audit status.** The stored-data audit reports 13 passed checks, 3 warnings and
  0 failures (`AUDIT STATUS: PASSED WITH DOCUMENTED LIMITATIONS`). The warnings
  are: Week 2 per-run means/SDs require the independent analyzer; 24 clean-control
  stdout files are missing; positive-case file-to-exit-code pairing and stdout
  equivalence need separate inspection. These limit, but do not invalidate, the
  use of the records.

## Comparison

The table below covers the four aspects required by the Week 4 template. The
second table adds the dimensions that determine whether the reported numbers can
be compared at all: AddressSanitizer configuration, measurement protocol,
aggregation, and detection evidence.

### Core aspects

| Aspect | Paper | Ours | Impact |
|---|---|---|---|
| **Workload** | 19 SPEC CPU2006 C/C++ benchmarks, 64-bit Linux (Section 4, p. 6; Table 1 and Figure 2); the input set is **not stated** | Claim 1: `array_update`, a 64 MiB array with 200 update passes. Claim 2: b1–b4 at scale 1. Claim 3: four crafted error cases plus b1–b4 clean controls. No SPEC binaries. | Instruction mix, allocation pattern and input size differ. ASan overhead is workload-dependent: across b1–b4 and scales 1–3 our slowdown ranges from −5.7% to 591.9%. Therefore 31.19% and the ~1.4x memory result are not same-workload values for 73% and 3.37x. |
| **Compiler** | "Regular LLVM compiler (`clang -O2`)"; revision **not stated** (Section 4, p. 6) | Clang 21.1.8 for Claim 1 and scaling Environment A; Clang 18.1.3 for Claim 2 and detection. `-O2` everywhere except the detection error cases (`-O1`). | The instrumentation pass, optimiser and ASan runtime are roughly a decade newer. Compiler and host effects are confounded, so the gap from 73% to 31.19% cannot be attributed to one factor. |
| **Environment** | HP Z600 with 2 × quad-core Intel Xeon E5620 CPUs and 24 GB RAM, bare 64-bit Linux; distribution and kernel **not stated** (Section 4, p. 6) | Several WSL2/Azure environments: Claim 1 WSL2 + Clang 21.1.8; Claim 2 Intel i5-14600KF, Ubuntu 24.04/WSL2 6.18.33.2, 16,265,896 kB; detection on Linux 6.8.0-1070-azure. See the environment table above. | Virtualisation, CPU generation, memory limits and compiler versions all differ. Absolute times and memory are not comparable. The cross-environment extension compares three sessions on two hosts and finds VmHWM means of 1.4016x, 1.4126x and 1.4042x, but it is descriptive and does not isolate hardware or compiler effects. |
| **Memory metric** | `VmPeak` read from `/proc/self/status` at process termination; average 3.37x; quarantine overhead excluded (Section 4, p. 6; Table 1) | `VmHWM` (peak resident set) is the primary metric. `VmPeak` is sampled every 20 ms but is unusable: every ASan run reserves about 21,474,900,000 kB (20 TiB) of shadow address space, giving `VmPeak` ratios of 1.8×10⁵–1.4×10⁶x that measure the reservation, not the program. Reported result: 1.41x in session 1 and 1.40x in session 2. | `VmPeak` and `VmHWM` describe different properties. 3.37x and 1.41x neither reproduce nor contradict each other. The modern ASan virtual reservation is not physical memory, and periodic sampling can miss a short-lived peak. |

### Measurement and evidence

| Aspect | Paper | Ours | Impact |
|---|---|---|---|
| **AddressSanitizer configuration** | Performance runs: 32-byte redzones, stack unwinding during `malloc`/`free` disabled, quarantine size 0 (p. 6). Chromium testing: defaults — redzone 128 bytes, quarantine 256 MB, unwinding depth 30 (p. 8). | Performance and memory runs: `ASAN_OPTIONS=quarantine_size_mb=0:malloc_context_size=0:detect_leaks=0:redzone=32`. Detection: `ASAN_OPTIONS=detect_leaks=0` with the runtime's default quarantine and redzone, plus `-O1`. | Overhead measurements are comparable to the paper only under the tuned configuration. Detection deliberately uses the default quarantine so that use-after-free is not masked. Detection evidence and overhead evidence must not be pooled, and modern defaults still differ from 2012. |
| **Measurement protocol** | Slowdown ratios of instrumented against regular binaries (Figure 2); the exact timing mechanism and repetition count are **not stated** in Section 4. `VmPeak` is read at process termination (p. 6). | Claim 1: `CLOCK_MONOTONIC` inside the benchmark, 3 batches × 5 runs per build. Claim 2: wall time around process execution, one warm-up plus three measured repetitions, `/proc` sampling every 20 ms. Claim 3: one run per crafted case; three clean-control repetitions per build. Ratios are ratios of means; the SD is the sample SD (n−1). | Harness overhead, sampling and warm-up differ. Samples are small (one to five measured runs per configuration). No paper uncertainty is available for 73% or 3.37x, so no paper error bar can be reconstructed. |
| **Aggregation and uncertainty** | 73% is an average over SPEC CPU2006 (Figure 2); 3.37x is an average over the 19 benchmarks (Table 1). The aggregation rule and SD are **not stated**; Figure 2 has no error bars. | The overall 31.19% is the ratio of overall means over 15 runs per build, not an average of the three batch percentages. The b1–b4 aggregate is the unweighted mean of four benchmark ratios. Sessions are reported separately. Ratio error bars and significance tests are not claimed. | Benchmark-level averaging is similar in spirit, but the paper's rule is unknown, and its Table 1 totals imply 2.99x rather than 3.37x. The comparison is therefore between reported aggregates, not between identically computed statistics. Our uncertainty is descriptive and based on small samples. |
| **Detection evidence** | Chromium deployment over 10 months: more than 300 previously unknown bugs, including 210 heap-use-after-free, 73 heap-buffer-overflow, 8 global-buffer-overflow, 7 stack-buffer-overflow and 1 `memcpy` parameter overlap (Section 4.2, p. 7). The paper also states that ASan has no false positives, while documenting undesirable reports that were fixed (Section 3.6, p. 5). | Four crafted cases (heap-, stack- and global-buffer-overflow, heap-use-after-free) were all detected and correctly classified (4/4). Clean controls: 4 benchmarks × 2 builds × 3 repetitions = 24 normal exits (24/24), with 0/12 observed ASan false positives. | The replication supports the detection mechanism for the selected cases. It does not reproduce the Chromium bug-finding record, universal detection completeness, or a population false-positive rate of zero. The audit also notes that the 24 clean-control stdout files are missing, so stdout equivalence is not independently established. |

## Implications for the three claims

### Runtime overhead (Claim 1)

**Verdict: partially supported.**

- The direction is reproduced: on `array_update`, ASan is slower than the base
  build, with a runtime ratio of 1.3119x (31.19% slowdown) over 15 runs per build.
  The three batches are 34.52%, 29.27% and 27.62% (n = 5 per build per batch).
- The magnitude is not replicated: 73% is a SPEC CPU2006 average on 2012-era
  hardware and compiler, while 31.19% is a 64 MiB microbenchmark on a modern WSL2
  host. The paper itself reports 26% when only writes are instrumented (p. 6),
  which reinforces that overhead depends on instrumentation scope and workload.
- The scaling extension shows slowdowns from −5.7% to 591.9% across b1–b4 and
  scales 1–3. This supports the qualitative claim that overhead is
  workload-dependent, but it also shows that no single percentage transfers
  across workloads.
- Do not describe 31.19% as a reproduction of 73%, and do not compare them as if
  they came from the same benchmark, compiler or host.

### Memory overhead (Claim 2)

**Verdict: inconclusive.**

- The paper reports 3.37x on `VmPeak` over SPEC CPU2006 (Table 1). The replication
  reports 1.41x on `VmHWM` over four microbenchmarks (session 1), with 1.40x in
  session 2 and session means of 1.4016x, 1.4126x and 1.4042x across three
  sessions and two hosts.
- The metric differs (`VmPeak` vs `VmHWM`), the workload differs (SPEC CPU2006 vs
  b1–b4), and the modern ASan shadow reservation makes `VmPeak` unusable as a
  memory-overhead measure. The two numbers must not be placed in the same column
  as equivalent values.
- The cross-environment result is descriptive evidence that the resident-memory
  ratio is stable for these benchmarks; it is not evidence of equivalence with the
  paper's 3.37x, nor a universal memory-overhead estimate.

### Detection capability (Claim 3)

**Verdict: supported for the tested cases.**

- Four intentional error cases were detected and classified correctly (4/4);
  their plain builds exited 0 and their ASan builds exited 1 with the expected
  diagnostic.
- All 24 clean-control executions exited normally, and none of the 12
  ASan-enabled runs produced an ASan report (0/12).
- This supports the detection mechanism for the tested classes. It does not
  reproduce the paper's Chromium bug-finding record, prove universal detection
  completeness, or establish a false-positive probability of zero. The audit
  warning about missing stdout files means output equivalence is not fully
  verified; normal exits and absent reports are necessary but not sufficient.

## Replication scope

This is a **partial replication and extension study**, not a full reproduction.

- **Benchmarks.** SPEC CPU2006 was replaced by five open benchmarks (`array_update`
  plus b1–b4); Chromium was replaced by four crafted error cases. SPEC requires a
  commercial licence and cannot be redistributed, and reproducing a Chromium-scale
  deployment is outside the course scope.
- **Claims.** The study addresses three claims: runtime overhead, memory overhead
  and detection capability. It does not reproduce SPEC CPU2006 or the Chromium
  bug-finding record, and it does not claim that the paper's numerical averages
  were reproduced.
- **Extensions.** Workload scaling (three scales × four benchmarks) and the
  cross-environment analysis (three sessions, two hosts) reuse existing
  executions. They add descriptive evidence about workload dependence and
  environment sensitivity; they do not convert the study into a controlled
  experiment and do not establish statistical equivalence.
- **What a full replication would require.** SPEC CPU2006 binaries, reference
  inputs and licence; a 2012-era LLVM/AddressSanitizer toolchain; bare-metal
  hardware comparable to the HP Z600; and a Chromium-scale deployment for the
  detection claim. None of these were available.
- **Generalisation.** Samples are small (one to five measured runs per
  configuration), both performance hosts use WSL2, and hardware, compiler and
  environment effects are not independently controlled. No statistical
  significance or equivalence is claimed.

## Evidence map

| Claim | Paper location | Replication evidence | Verdict |
|---|---|---|---|
| Runtime overhead | Section 4, p. 6; Figure 2, p. 7 | [performance_analysis.txt](../results/performance/performance_analysis.txt), [benchmark_summary.csv](../results/performance/benchmark_summary.csv), [paper_vs_ours_runtime.csv](../results/report/paper_vs_ours_runtime.csv) | Partially supported |
| Memory overhead | Section 4, p. 6; Table 1 | [session 1 summary](../results/memory_claim2/20261121T051205Z/summary.md), [cross-environment comparison](../results/cross_environment/comparison.csv) | Inconclusive |
| Detection capability | Sections 3.6 (p. 5) and 4.2 (p. 7) | [detection summary](../results/detect/summary.md), [clean-control summary.csv](../results/detect/false_positive/summary.csv) | Supported for the tested cases |

## Related documents

- [Claims and verdicts](CLAIMS.md)
- [Replication deviations](DEVIATIONS.md)
- [Statistical and reporting conventions](STATISTICAL_CONVENTIONS.md)
- [Paper vs. Ours](PAPER_VS_OURS.md)
- [Reproducibility and data integrity](REPRODUCIBILITY.md)
- [Report outline](REPORT_OUTLINE.md)

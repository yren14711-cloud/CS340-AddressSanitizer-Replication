# Claims tested

Three claims, each tied to a table or figure in the paper, as the report
structure requires ("one to three claims, each linked to a table or figure in the
paper"). Keep this file and Section 1 of the report consistent; if a claim is
dropped, drop it here too.

Paper: *AddressSanitizer: A Fast Address Sanity Checker*, USENIX ATC 2012.

---

## Claim 1 — runtime overhead

> AddressSanitizer slows instrumented programs down by **73% on average** across
> SPEC CPU2006 (i.e. runtime becomes 1.73x that of the uninstrumented build).

- Paper location: **Figure 2** ("average slowdown on SPEC CPU2006 on 64-bit
  Linux"), discussed in Section 4.
- Paper's measurement setting: `clang -O2`, 64-bit, 32-byte redzones, quarantine
  size 0, stack unwinding during malloc/free disabled.
- Worst cases reported: `400.perlbench` 2.60x, `483.xalancbmk` 2.67x — both
  malloc-intensive with many 1- and 2-byte accesses.
- What we measure: wall time of `build/<bench>-base` vs `build/<bench>-asan`,
  same `-O2`, same machine, 3 measured repetitions after a discarded warm-up.
- Metric: `slowdown = (T_asan - T_base) / T_base * 100%`, reported as
  mean ± std.
- Produced by: `scripts/run_experiments.sh` + `scripts/parse_results.py`
  (column `slowdown` in `summary.md`).

## Claim 2 — memory overhead

> AddressSanitizer increases memory usage by **3.37x on average**, measured as
> `VmPeak` from `/proc/self/status`.

- Paper location: **Table 1** (memory usage increase), Section 4.
- Related numbers in the same section: stack size increase is small (only 6
  benchmarks changed noticeably, 3 by more than 10% — Table 2); binary size grows
  1.5x-3.2x, 2.5x on average.
- Paper's caveat: the constant-size quarantine overhead was **not** counted.
- What we measure: `VmPeak` sampled from `/proc/<pid>/status` while the
  benchmark runs, with `VmHWM` recorded as a cross-check, using the same
  `quarantine_size_mb=0` so the caveat applies identically.
- Metric: `mem_ratio = VmPeak_asan / VmPeak_base`, mean ± std.
- Final measurement 2026-11-21 (`results/memory_claim2/20261121T051205Z/`;
  b1–b4, 1 warm-up + 3 measured runs per configuration, unmodified
  `scripts/run_experiments.sh -n 3 -s 1`): the `VmPeak` ratio is **not usable**
  in this environment. Every ASan run reports `VmPeak` ≈ 21 474 900 000 kB
  (about 20 TB) because the instrumented process reserves the ASan shadow address
  space at start-up. Within one benchmark the value is identical in all three
  runs (sample SD = 0); across the four benchmarks it varies by 147 480 kB
  (about 144 MiB, < 0.001% of 20 TB). The ratio therefore measures the
  reservation, not the benchmark.
- Reported instead: `VmHWM` (peak resident set), which a `PROT_NONE` reservation
  cannot inflate. Per benchmark: b1 2.05x, b2 1.18x, b3 1.25x, b4 1.16x;
  unweighted mean **1.41x** (sample SD 0.43 across the four benchmarks;
  n = 3 per configuration). A second independent session the same day
  (`20261121T051259Z`) gives 2.02x / 1.18x / 1.26x / 1.16x, unweighted mean
  **1.40x**; every benchmark agrees within 0.03x. Tables, figures and the
  generator script: `results/memory_claim2/`. The `mem ratio` column of
  `results/summary/summary.md` is the 14 November `VmPeak` ratio and is **not**
  the reported figure.
- The 1.41x number is a resident-memory proxy on four small benchmarks, not the
  paper's `VmPeak` over SPEC CPU2006 (Table 1, 3.37x). The two are reported side
  by side, never as a reproduction; see `docs/DEVIATIONS.md` rows 17–20.
- Produced by: `scripts/run_experiments.sh` (fields `vmpeak_kb`, `vmhwm_kb`) and
  `results/memory_claim2/analyze_memory_claim2.py` (tables A and B, figures A–C).

## Claim 3 — detection capability

> AddressSanitizer detects out-of-bounds accesses on heap, stack and global
> objects and use-after-free of heap memory, at the point of occurrence, without
> false positives.

- Paper location: Sections 1-3 and the error-report examples; the claim is
  qualitative rather than a single figure.
- What we measure: one small program per error class
  (`experiments/memory_errors/`), built with and without
  `-fsanitize=address`. We record exit codes, ASan reports and
  whether the reported error class matches the expected class.
  Clean-control runs are used to check for observed false positives.
- Positive detection results (2026-11-21): all four intentionally
  constructed error cases were detected and correctly classified:
  `heap-buffer-overflow`, `stack-buffer-overflow`,
  `global-buffer-overflow`, and `heap-use-after-free`.
  All four plain builds exited with code 0, whereas all four
  ASan builds exited with code 1 and reported the expected error.
- Clean-control results: four benchmarks (b1-b4), two configurations
  (Base and ASan), and three repetitions per configuration.
  All 24 executions exited successfully with code 0.
  No false-positive ASan reports were observed in the 12
  ASan-enabled executions (0/12).
- Verdict: **supported for the tested cases**. These experiments
  support the detection claim within the tested scope, but do not
  establish universal detection completeness or the absence of
  false positives in arbitrary programs.
- Evidence: `results/detect/summary.md` and
  `results/detect/false_positive/summary.csv`.
- Report figure: [Claim 3 detection matrix](../results/figures/claim3_detection_matrix.png).
- Produced by: `scripts/run_detection.sh` (covers all four cases). Clean controls are produced by
  `scripts/run_false_positive.sh`. Note that
  `make detect` currently builds only the heap case from `DETECT_SRC`.

---

## Verdict table (fill in after the final runs)

| Claim | Paper number | Our number | Verdict | Note |
|---|---|---|---|---|
| 1 runtime overhead | 73% average (Fig. 2) | 31.19% overall (`array_update`, 15 runs/version) | partially supported | Different workload from SPEC CPU2006; source: `results/performance/`. This is not a b1–b4 result. Batches: 34.52%, 29.27%, 27.62%. |
| 2 memory overhead | 3.37x average (Table 1) | 1.41x (VmHWM proxy; VmPeak unusable: constant 20 TB shadow reservation) | inconclusive | b1–b4, 1 warm-up + 3 runs per configuration, two independent sessions on 2026-11-21 (`results/memory_claim2/`, second session 1.40x; ratios reproduce within 0.03x). Metric (VmHWM vs VmPeak) and workload (4 microbenchmarks vs SPEC CPU2006) both differ from Table 1, so 3.37x is neither reproduced nor contradicted. See DEVIATIONS rows 17–20. |
| 3 detection | qualitative | 4/4 error cases correctly detected; 24/24 clean-control executions successful; 0/12 observed ASan false positives | supported | Supported for the tested cases only; not a proof of universal detection completeness or zero false positives. See `results/detect/summary.md` and `results/detect/false_positive/summary.csv`. |

Allowed verdicts: supported / partially supported / not supported / inconclusive.

## Week 4 extension: cross-environment VmHWM consistency

The Scale 1 workload-scaling results and the two Claim 2
memory sessions were compared across two hardware and
compiler environments.

The unweighted mean VmHWM ratios over the four benchmarks
were:

- AMD / Clang 21.1.8: 1.4016x.
- Intel / Clang 18.1.3, session 1: 1.4126x.
- Intel / Clang 18.1.3, session 2: 1.4042x.

The analysis contains 12 benchmark-session ratios derived
from 72 historical measured executions. Sessions are not
pooled.

The allocation-intensive b1 benchmark consistently has the
highest resident-memory ratio in these sessions.

These observations provide limited descriptive evidence
of cross-environment consistency and workload dependence,
not formal statistical equivalence or a universal memory
overhead estimate.

**Claim 2 verdict remains inconclusive** as a direct
replication of the paper's reported 3.37x VmPeak result:
our measurements use VmHWM and different benchmarks.

Evidence and reproduction instructions:

- [Cross-environment analysis](../results/cross_environment/README.md)
- [Comparison CSV](../results/cross_environment/comparison.csv)
- [Figure 9](../results/cross_environment/figures/vmhwm_cross_environment.png)
- [Analysis script](../results/cross_environment/plot_comparison.py)

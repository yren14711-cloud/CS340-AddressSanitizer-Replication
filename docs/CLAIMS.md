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
- Measured 2026-11-14 (`results/logs/20261114T155152Z/runs.log`; b1–b4, 1 warm-up +
  3 measured runs per configuration): the `VmPeak` ratio is **not usable** in this
  environment. Every ASan run reports `VmPeak` ≈ 21 474 860 000 kB (20.0 TB): the
  instrumented process reserves the ASan shadow address space at start-up, and
  that constant swamps the workload — the four ASan `VmPeak` values differ by less
  than 150 MB, so the ratio measures the reservation, not the benchmark.
- Reported instead: `VmHWM` (peak resident set), which a `PROT_NONE` reservation
  cannot inflate. Per benchmark: b1 2.10x, b2 1.26x, b3 1.42x, b4 1.16x;
  unweighted mean **1.48x**, sd over the 12 run-level ratios 0.37 (n = 3 per
  configuration). Source: the same log. The `mem ratio` column of
  `results/summary/summary.md` is still the `VmPeak` ratio and is **not** the
  reported figure.
- The 1.48x number is a resident-memory proxy on four small benchmarks, not the
  paper's `VmPeak` over SPEC CPU2006 (Table 1, 3.37x). The two are reported side
  by side, never as a reproduction; see `docs/DEVIATIONS.md` rows 17 and 18.
- Produced by: `scripts/run_experiments.sh` (fields `vmpeak_kb`, `vmhwm_kb`) and
  `scripts/parse_results.py` (column `mem ratio`).

## Claim 3 — detection capability

> AddressSanitizer detects out-of-bounds accesses on heap, stack and global
> objects and use-after-free of heap memory, at the point of occurrence, without
> false positives.

- Paper location: Sections 1-3 and the error-report examples; the claim is
  qualitative rather than a single figure.
- What we measure: one small program per error class (`experiments/`), built with
  and without `-fsanitize=address`. For each, record whether ASan reports it,
  which error class ASan names, and whether the uninstrumented build stays silent
  or crashes. False positives are checked with the clean benchmarks: a benchmark
  run that aborts under ASan would contradict the claim.
- Status today: four error classes have been written and tested:
  `heap-buffer-overflow`, `stack-buffer-overflow`, `global-buffer-overflow`,
  and `heap-use-after-free` (see `experiments/memory_errors/`). All four match
  the expected class in `results/detect/summary.md` (`Matches expected = yes`).
  The false-positive check on clean programs has not been run yet: there is no
  `results/detect/false_positive/` directory in this repository, and the verdict
  stays "partially supported" until one exists.
- Produced by: `scripts/run_detection.sh` (covers all four cases). Note that
  `make detect` currently builds only the heap case from `DETECT_SRC`.

---

## Verdict table (fill in after the final runs)

| Claim | Paper number | Our number | Verdict | Note |
|---|---|---|---|---|
| 1 runtime overhead | 73% average (Fig. 2) | 31.19% overall (`array_update`, 15 runs/version) | partially supported | Different workload from SPEC CPU2006; source: `results/performance/`. This is not a b1–b4 result. Batches: 34.52%, 29.27%, 27.62%. |
| 2 memory overhead | 3.37x average (Table 1) | 1.48x (VmHWM proxy; VmPeak unusable: constant 20 TB shadow reservation) | inconclusive | b1–b4, 3 + 1 runs each, `results/logs/20261114T155152Z/runs.log`. Metric and workload both differ from Table 1, so 3.37x is neither reproduced nor contradicted. See DEVIATIONS rows 17–18. |
| 3 detection | qualitative | 4/4 classes detected (`results/detect/summary.md`) | partially supported | Positive cases done; false-positive check pending this week. |

Allowed verdicts: supported / partially supported / not supported / inconclusive.

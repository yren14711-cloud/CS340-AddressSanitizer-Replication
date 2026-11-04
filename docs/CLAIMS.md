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
- Status today: only the heap-buffer-overflow case exists
  (`experiments/memory_errors/heap_buffer_overflow.c`). The stack, global and
  use-after-free cases are still missing and must be added before the claim can
  be evaluated.
- Produced by: `make detect`, run manually, output stored under `results/detect/`.

---

## Verdict table (fill in after the final runs)

| Claim | Paper number | Our number | Verdict | Note |
|---|---|---|---|---|
| 1 runtime overhead | 73% average (Fig. 2) | TODO | TODO | averaged over a different benchmark mix |
| 2 memory overhead | 3.37x average (Table 1) | TODO | TODO | |
| 3 detection | qualitative | TODO | TODO | needs the missing error classes |

Allowed verdicts: supported / partially supported / not supported / inconclusive.

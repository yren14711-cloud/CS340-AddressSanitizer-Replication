# Memory error detection cases

Working notes for **Claim 3** in `docs/CLAIMS.md`:

> AddressSanitizer detects out-of-bounds accesses on heap, stack and global
> objects and use-after-free of heap memory, at the point of occurrence, without
> false positives.

The claim is qualitative, so it is evidenced by one small program per error
class, each with an uninstrumented control build. A case counts as demonstrated
only when the instrumented build reports the expected class **and** the plain
build does not.

## Cases

| File | Error class expected | Plain build should | Why the case is written this way |
|---|---|---|---|
| `heap_buffer_overflow.c` | `heap-buffer-overflow` | stay silent or crash | allocating 5 ints and reading index 5 |
| `stack_buffer_overflow.c` | `stack-buffer-overflow` | stay silent or corrupt memory | index derived from `argc`, array `volatile`, so neither the store nor the array can be optimised away |
| `global_buffer_overflow.c` | `global-buffer-overflow` | stay silent or corrupt memory | same technique on a file-scope array, which needs no allocation |
| `use_after_free.c` | `heap-use-after-free` | stay silent, usually prints stale data | write then read through a pointer after `free()` |

## Running

```sh
scripts/run_detection.sh
```

It builds every case twice into `build/`, runs both builds, and writes:

- `results/detect/<case>_plain.log` — control build, with its exit code
- `results/detect/<case>_asan.log` — instrumented build, with the full report
- `results/detect/summary.md` — one row per case, including the class ASan named
- `results/detect/environment.txt` — compiler version and options

The script never modifies the sources; it only reads them.

## Configuration caveat

This script uses the **default** AddressSanitizer quarantine, unlike
`scripts/run_experiments.sh`, which sets `quarantine_size_mb=0` to match the
paper's performance methodology.

The reason is structural: with the quarantine disabled, a freed block can be
handed straight back to the allocator, so `use_after_free.c` may not be caught
reliably. Detection quality and overhead are measured under different
configurations, and each log records which one it used. Do not quote an
overhead number from a detection run, or a detection result from an overhead
run.

## What the report needs

1. One row per case: expected class, reported class, plain-build behaviour.
2. The full report of at least one case in an appendix, or a figure of it, since
   the paper's argument is that ASan reports *at the point of occurrence* with
   the exact line and the shadow bytes around the faulting address.
3. The false-positive check: all four benchmarks must run to completion under
   ASan with identical output to their plain builds. A benchmark that aborts
   would contradict the "no false positives" part of the claim.
4. A verdict for Claim 3. Four cases plus a clean benchmark suite supports
   "supported" for the mechanism; it does not reproduce the paper's bug-finding
   record in real software, which the report should state as a limitation.

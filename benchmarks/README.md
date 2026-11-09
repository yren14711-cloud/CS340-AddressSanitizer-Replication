# Benchmarks

Four small, self-contained C benchmarks used to measure the runtime and memory
overhead of AddressSanitizer. They were written for this replication; no SPEC
source code is included or derived from.

## Why these, and not SPEC CPU2006

The paper evaluates on SPEC CPU2006 (Section 4) and reports an average slowdown
of 73% and an average memory increase of 3.37x. SPEC CPU2006 requires a
commercial licence and its binaries and inputs may not be redistributed, so this
replication cannot ship them inside the repository. Instead the workloads below
reproduce the *classes* of behaviour that the paper singles out as decisive, and
the substitution is recorded as a deviation in `docs/DEVIATIONS.md`.

| Benchmark | Workload class | Corresponds to (paper) | Expected ASan cost |
|---|---|---|---|
| `b1_malloc_text` | many small heap objects, 1-2 byte accesses | 400.perlbench, 483.xalancbmk (2.60x / 2.67x, Fig. 2) | high, both time and memory |
| `b2_pointer_chase` | pointer chasing, cache misses, large allocations | 473.astar, 462.libquantum | high time cost, near-zero memory cost (redzones dwarfed by large blocks) |
| `b3_matmul` | dense floating-point, few allocations | 410.bwaves, 433.milc | lowest time cost, near-zero memory cost |
| `b4_string_scan` | byte-wise parsing of a large buffer, growing output | 483.xalancbmk, 447.dealII | high time cost, moderate memory cost |

The per-benchmark spread is itself a result: the paper's 73% average is an
average over very different overheads, and an average of a different benchmark
mix is not directly comparable to it. The report must say so.

## Running

All binaries take a single optional `scale` argument (default `1`); time and
memory grow roughly linearly with it.

```sh
build/b1_malloc_text-base 1     # uninstrumented
build/b1_malloc_text-asan 1     # AddressSanitizer instrumented
```

Each program prints one `checksum=` line so that the compiler cannot remove the
work and so that the two configurations can be checked to compute the same
result. They are deterministic: no random seeds from the environment, no I/O
beyond that one line.

The top-level `Makefile` builds all of them into `build/`;
`scripts/run_experiments.sh` runs the matrix and records the logs.

## Sizing

At `scale=1` on a modern x86-64 machine each benchmark runs for roughly
0.3-1.5 s uninstrumented. Check your own numbers with
`/usr/bin/time -f '%e s' build/<bench>-base 1` before starting a full run: a
repetition that finishes in under ~0.3 s is dominated by process start-up noise,
and one that takes minutes will make the 3-repetition matrix painful.

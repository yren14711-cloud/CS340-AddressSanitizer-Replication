# Claim 2 -- memory overhead, reproducible measurement set

This directory is the Week 3 deliverable for **Claim 2 (memory overhead)**:
two fresh measurement sessions of the b1-b4 matrix, the raw logs they produced,
the parsed tables, the figures and the script that turns the logs into the tables.

Every number in `summary.md`, in the figures and in `docs/CLAIMS.md` comes from a
`RESULT` line in one of the `runs.log` files under this directory. Nothing is
typed in by hand, and no run from 14 November is edited, overwritten or merged
into these sessions.

## 1. What is measured, and why VmHWM is the reported metric

The paper's Table 1 reports the memory increase as `VmPeak` (virtual address
space high-water mark) taken from `/proc/self/status`. This replication records
both `VmPeak` and `VmHWM` for every run (the sampler in
`scripts/run_experiments.sh` reads both fields from `/proc/<pid>/status` every
20 ms).

- `VmPeak` for an ASan build is **not usable** here. The ASan runtime reserves its
  shadow address space at start-up, so every ASan run reports
  `VmPeak` ~= 21 474 900 000 kB (about 20 TB). Within one benchmark the value is
  identical in all three runs (sample SD = 0); across the four benchmarks it
  varies by 147 480 kB (about 144 MiB, < 0.001% of 20 TB). A ratio built on that
  number measures the reservation, not the workload. It is reported in Table B
  only so the deviation is visible.
- `VmHWM` is the peak **resident** set. A `PROT_NONE` virtual reservation cannot
  raise it, so it is the closest available proxy for what the paper's Table 1 is
  after with `VmPeak`.

Metric definition used everywhere in this directory:

    ratio(benchmark) = mean(VmHWM_asan over 3 runs) / mean(VmHWM_base over 3 runs)
    unweighted mean  = mean of the four per-benchmark ratios
    sample SD        = standard deviation (n-1) across the four per-benchmark ratios
    error bars       = 1 sample SD of the three runs that make up that bar

## 2. Result

Final session `20261121T051205Z` (see `summary.md` for the full tables):

| Benchmark | Base VmHWM (kB) | ASan VmHWM (kB) | Ratio |
|---|---|---|---|
| b1_malloc_text | 35366.7 +/- 1709.6 | 72513.3 +/- 709.5 | 2.05x |
| b2_pointer_chase | 17734.7 +/- 2.3 | 21000.0 +/- 34.2 | 1.18x |
| b3_matmul | 13501.3 +/- 2.3 | 16932.0 +/- 66.1 | 1.25x |
| b4_string_scan | 103065.3 +/- 2.3 | 119729.3 +/- 14.0 | 1.16x |

- Unweighted mean of the four ratios: **1.41x** (sample SD 0.43 across the four
  benchmarks; n = 3 runs per configuration per benchmark).
- Second independent session `20261121T051259Z`: 2.02x / 1.18x / 1.26x / 1.16x,
  unweighted mean **1.40x**. Every benchmark reproduces within 0.03x.
- The paper's Table 1 average is 3.37x on SPEC CPU2006, measured on `VmPeak`.
  Our figure uses a different metric on four small benchmarks: it shows that the
  resident-memory overhead measured here is well below 3.37x. It does **not**
  reproduce Table 1, and it is not reported as if it did.
- The runtime columns in `summary.md` are context only; Claim 1 is a separate
  deliverable.

## 3. Environment (both sessions)

| Item | Value |
|---|---|
| CPU | Intel Core i5-14600KF, 20 threads |
| RAM | 16 265 896 kB total |
| OS | Ubuntu 24.04 LTS under WSL2 |
| Kernel | 6.18.33.2-microsoft-standard-WSL2 |
| WSL | 2.7.14.0 (Windows 10 Pro 19045) |
| Compiler | Ubuntu clang 18.1.3, `-O2` |
| Build | `make CC=clang OPT=-O2` (both binaries from the same translation unit) |
| ASan options | `quarantine_size_mb=0:malloc_context_size=0:detect_leaks=0:redzone=32` |
| Working tree | `/root/work/...` on ext4, not `/mnt/*` |
| Repetitions | 1 discarded warm-up + 3 measured runs per (benchmark, configuration), scale = 1 |
| Python | 3.12.3; matplotlib 3.6.3 for the figures |

Per-session details, read from the machine at run time, are in
`<session>/environment.txt`.

## 4. Reproduce from scratch

```sh
git clone https://github.com/yren14711-cloud/CS340-AddressSanitizer-Replication.git
cd CS340-AddressSanitizer-Replication
git switch week3/1240004926          # branch that carries this directory

make clean
make CC=clang OPT=-O2                 # base + asan, -O2, same source
bash scripts/run_experiments.sh -n 3 -s 1
# -> prints "logs: results/logs/<STAMP>/runs.log"
```

Then stage that session and build the tables:

```sh
STAMP=<STAMP printed by the runner>
mkdir -p results/memory_claim2/$STAMP
cp results/logs/$STAMP/runs.log results/memory_claim2/$STAMP/
mkdir -p results/memory_claim2/$STAMP/raw
cp -r results/logs/$STAMP/raw/. results/memory_claim2/$STAMP/raw/

SESSION_STAMP=$STAMP SOURCE_LOG=results/memory_claim2/$STAMP/runs.log \
  WSL_VERSION=2.7.14.0 \
  bash results/memory_claim2/collect_env_claim2.sh > results/memory_claim2/$STAMP/environment.txt

python3 results/memory_claim2/analyze_memory_claim2.py \
  --log results/memory_claim2/$STAMP/runs.log \
  --out results/memory_claim2/$STAMP \
  --env results/memory_claim2/$STAMP/environment.txt \
  --compare "results/logs/20261114T155152Z/runs.log;kernel 5.10 (Nov 14);Ubuntu 24.04, kernel 5.10.16.3, clang 18.1.3" \
  --compare "results/logs/20261114T161554Z/runs.log;kernel 6.18 (Nov 14);Ubuntu 24.04, kernel 6.18.33.2, clang 18.1.3"
```

`--compare` is optional; without it only figures A and B are produced. The two
14 November logs are used **only** for figure C and are never pooled with the new
sessions.

The figure step needs matplotlib (`apt-get install -y python3-matplotlib`);
if it is missing the script still writes the CSV and `summary.md` and says so.

## 5. Files

| Path | What it is |
|---|---|
| `analyze_memory_claim2.py` | Parses a `runs.log`, writes `results.csv`, `summary.md`, figures A/B/C |
| `collect_env_claim2.sh` | Records CPU/RAM/OS/kernel/clang/WSL/filesystem/git head into `environment.txt` |
| `20261121T051205Z/runs.log` | Raw RESULT lines of the primary session (24 measured runs) |
| `20261121T051205Z/raw/` | Per-run stdout/stderr of that session (64 files: warm-up + 3 runs, 2 configs, 4 benchmarks) |
| `20261121T051205Z/environment.txt` | Machine and toolchain record of that session |
| `20261121T051205Z/results.csv` | 24 rows: one per (benchmark, config, metric), mean / SD / n / unit / source log |
| `20261121T051205Z/summary.md` | Table A (VmHWM), Table B (VmPeak), per-run raw values, checks, figure C table |
| `20261121T051205Z/figures/fig_a_vmhwm_bars.png` | Base vs ASan VmHWM per benchmark, mean +/- 1 sample SD, n = 3 |
| `20261121T051205Z/figures/fig_b_vmhwm_ratio.png` | Per-benchmark VmHWM ratio, 1.0x baseline |
| `20261121T051205Z/figures/fig_c_ratio_sessions.png` | Ratio per benchmark across three sessions (this one and the two 14 Nov runs) |
| `20261121T051259Z/` | Second independent session, same structure (figures A and B) |

## 6. How to check any number

1. Pick a number in `summary.md` and its benchmark/configuration.
2. `grep 'bench=b3_matmul config=asan' 20261121T051205Z/runs.log` prints the three
   raw `wall_ms`/`vmpeak_kb`/`vmhwm_kb` values behind that row.
3. The same values are in `results.csv` (mean / std / n) and in the raw stdout
   files under `raw/` (each benchmark prints a checksum that must match between
   base and ASan).
4. Re-running `analyze_memory_claim2.py` on the same log must reproduce
   `summary.md` and the figures byte-for-byte apart from PNG metadata.

## 7. Data-quality notes

- n = 3 per bar is the rubric minimum, not a comfortable sample. The per-run
  VmHWM values are stable to a few kB except b1 (+/- 1.7 MB base, +/- 0.7 MB
  ASan), so the ratios are dominated by the allocation pattern, not by noise.
- Two wall-time outliers exist in the primary session and one in the second
  (b2 ASan run 3 at 3256 ms, b4 ASan run 3 at 2485 ms against ~1.0 s / ~0.4 s
  for their siblings). They are WSL2 host stalls: they are kept in the data and
  flagged in `summary.md`, and they do not touch the VmHWM values.
- b3_matmul runs for only ~65 ms (base) at scale = 1, so the 20 ms sampler sees
  few samples for it. Its VmHWM is the least time-resolved number in the table;
  it is consistent across sessions (1.25x / 1.26x / 1.25x), which is why it is
  kept, but a scale >= 2 run would be the way to firm it up.
- The two 21 November sessions are the same host and kernel; the two 14 November
  sessions differ in kernel (5.10.16.3 vs 6.18.33.2). Figure C therefore compares
  session-level reproducibility, not two different machines.

## 8. Where this feeds into

- `docs/CLAIMS.md` -- Claim 2 narrative and the verdict table row.
- `docs/DEVIATIONS.md` -- rows 10, 17, 18, 19, 20 (memory metric and host).
- `results/summary/summary.md` and `results/summary_replication_20261114T161554Z/`
  are the 14 November parses and are left untouched; their `mem ratio` column is
  the unusable VmPeak ratio and is **not** the Claim 2 figure.

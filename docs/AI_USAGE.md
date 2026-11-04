# AI usage statement

This file is the source of truth for the AI usage statement that the Writing
Quality criterion requires in the Final Report. The same text goes there.

## Statement

> We used an AI assistant (Chatbox) to draft the repository scaffolding: the
> `Makefile`, the experiment and detection shell scripts, the results parser, the
> four benchmark programs in `benchmarks/`, and the first drafts of the documents
> in `docs/`. Those drafts were compiled, run and reviewed before being committed.
>
> Every design decision the report depends on was made by the group: which claims
> to test and how to tie each to a figure or table, which workloads to substitute
> for SPEC CPU2006, the measurement methodology, and each deviation recorded in
> `docs/DEVIATIONS.md`.
>
> Every experimental number in this repository and in the report comes from
> running the committed code on the machine recorded in
> `results/env/environment.txt`. No measurement, log, table, figure or
> interpretation was generated or estimated by an AI system.

## What was drafted with AI assistance

| Area | Files | How it was checked before committing |
|---|---|---|
| Build system | `Makefile` | `make -n` expands the expected matrix; every benchmark builds twice, plain and with `-fsanitize=address` |
| Experiment harness | `scripts/run_experiments.sh`, `scripts/parse_results.py` | Parser validated end to end on a synthetic log; shell scripts pass `bash -n`; the `/proc` peak-memory sampling only runs on Linux and is verified by the first real matrix run |
| Detection experiment | `scripts/run_detection.sh`, `experiments/memory_errors/{stack,global}_buffer_overflow.c`, `use_after_free.c` | Each case compiles warning-free under `-Wall -Wextra` and, as the uninstrumented control, runs to completion while performing the invalid access |
| Benchmarks | `benchmarks/*.c` | Compile warning-free; each runs for 0.5-1.5 s at `scale=1` and prints a deterministic checksum |
| Documents | `docs/CLAIMS.md`, `docs/DEVIATIONS.md`, `docs/DETECTION.md`, this file | Reviewed against the paper's own text: the 73%, 3.37x and 32-byte-redzone settings are quoted from Sections 4 of the paper, not from secondary sources |

## What was not AI-generated

- All measured numbers, and every log under `results/`. They exist only as the
  output of the committed scripts, and each one traces back to a file.
- The analysis of discrepancies: claim verdicts, the explanation of each gap, and
  the extension design. Written by the group members after the runs.
- All decisions recorded in `docs/DEVIATIONS.md`.

## Pending at the time of writing

Listed here so that the report cannot accidentally claim more than was done:

- The overhead matrix (`make run`) and the detection runs
  (`scripts/run_detection.sh`) have not been executed on the final machine yet;
  no results are reported until they are, and the numbers that appear in the
  report will be the ones in `results/`.
- The extension experiment has not been designed in final form.

## Sign-off

Prepared by 葉景威 (1240004926). The Final Report carries this statement signed
by all four group members.

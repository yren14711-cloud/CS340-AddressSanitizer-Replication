# AI usage statement (draft)

The Writing Quality criterion requires an AI usage statement in the report, and
the Git History criterion requires the repository to show the group's own work.
This file is the working record; the final wording goes into the report.

Fill it in honestly and specifically. "We used AI for the report" is worth less
than a list of what was and was not machine-generated, because the grader is
checking whether the group can defend its own numbers.

## What was AI-assisted

| Area | How AI was used | Human verification done |
|---|---|---|
| Initial repository scaffolding (`Makefile`, `scripts/*.sh`, `scripts/parse_results.py`) | Drafted with AI assistance, then reviewed and run by the group | TODO: state who ran it and on which machine; state that a full `make run` reproduced the numbers reported |
| Benchmark programs in `benchmarks/` | Drafted with AI assistance from the paper's workload description | TODO: state that each benchmark was checked to be error-free under `-fsanitize=address` and that its checksum is identical for base and asan builds |
| Documentation templates (`docs/CLAIMS.md`, `docs/DEVIATIONS.md`) | Drafted with AI assistance | TODO: confirm every row matches an actual measurement |
| Report text | TODO: state whether AI was used for drafting, editing or translation | TODO |

## What was not AI-generated

- TODO: all measured numbers, all logs under `results/`, all figures. These must
  come from actual runs on the recorded machine — never from a language model.
- TODO: the analysis of discrepancies and the extension design. State which
  member wrote them.

## Declaration

> TODO (final text for the report): we used AI assistance for <...>. All
> experiments, measurements and their interpretation were performed and verified
> by the group members listed below. No experimental result in this report was
> produced or estimated by an AI system.

Group members: 任奕安 (1240014055), 葉景威 (1240005926), TODO x2.

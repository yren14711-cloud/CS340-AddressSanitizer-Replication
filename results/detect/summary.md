# Detection results (Claim 3)

- generated: 2026-11-07T06:37:59Z
- source directory: `experiments/memory_errors`
- compiler: Ubuntu clang version 21.1.8 (6ubuntu1)
- compilation: `-O1 -Wall -Wextra`, asan builds add `-fsanitize=address -fno-omit-frame-pointer -g`
- ASan options: `detect_leaks=0` (default quarantine; the overhead runs differ)

Each log records the exit code and the full program output; the
`plain` log is the control showing that the uninstrumented build does
not identify the error.

| Case | Plain build | ASan build | Reported class | Matches expected |
|---|---|---|---|---|
| global_buffer_overflow | exit 0 | exit 1 | global-buffer-overflow | yes |
| heap_buffer_overflow | exit 0 | exit 1 | heap-buffer-overflow | yes |
| stack_buffer_overflow | exit 0 | exit 1 | stack-buffer-overflow | yes |
| use_after_free | exit 0 | exit 1 | heap-use-after-free | yes |

# Detection results (Claim 3)

- generated: 2026-11-21T18:40:34Z
- source directory: `experiments/memory_errors`
- compiler: Ubuntu clang version 18.1.3 (1ubuntu1)
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

## Clean Controls & Detection Overview

| group | target | mode | runs | exit | status |
| :--- | :--- | :--- | :---: | :---: | :--- |
| bug | global_buffer_overflow | plain/asan | 1/1 | 0/1 | global-buffer-overflow |
| bug | heap_buffer_overflow | plain/asan | 1/1 | 0/1 | heap-buffer-overflow |
| bug | stack_buffer_overflow | plain/asan | 1/1 | 0/1 | stack-buffer-overflow |
| bug | use_after_free | plain/asan | 1/1 | 0/1 | heap-use-after-free |
| clean | b1_malloc_text | base/asan | 3/3 | 0/0 | 0/3 false positive |
| clean | b2_pointer_chase | base/asan | 3/3 | 0/0 | 0/3 false positive |
| clean | b3_matmul | base/asan | 3/3 | 0/0 | 0/3 false positive |
| clean | b4_string_scan | base/asan | 3/3 | 0/0 | 0/3 false positive |

```text
Buggy caught (exit 1): [##########] 4/4
Clean executions successful: [##########] 24/24
Observed ASan false positives: [----------] 0/12
```

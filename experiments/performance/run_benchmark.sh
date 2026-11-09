#!/usr/bin/env bash
set -euo pipefail

mkdir -p results/performance

LOG="results/performance/benchmark_runs.log"

{
    echo "AddressSanitizer Performance Benchmark"
    echo "Date (UTC): $(date -u)"
    echo "Compiler: $(clang --version | head -n 1)"
    echo "Native and ASan versions"
    echo "Formal runs: 5 per version"
    echo ""

    for run in 1 2 3 4 5; do
        echo "========== PAIR $run =========="

        if (( run % 2 == 1 )); then
            echo "--- NATIVE RUN $run ---"
            ./build/array_update_native

            echo "--- ASAN RUN $run ---"
            ./build/array_update_asan
        else
            echo "--- ASAN RUN $run ---"
            ./build/array_update_asan

            echo "--- NATIVE RUN $run ---"
            ./build/array_update_native
        fi
    done

} 2>&1 | tee "$LOG"

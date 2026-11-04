#!/usr/bin/env bash
#
# collect_env.sh -- record everything about the machine that can change a
# measurement, so that the setup section of the report and the "clean machine"
# check in the rubric both have a single source of truth.
#
# Usage: scripts/collect_env.sh [output-file]
#        default output: results/env/environment.txt
#
# AddressSanitizer configuration used by the experiment matrix is printed too;
# keep it in sync with ASAN_OPTIONS_DEFAULT in scripts/run_experiments.sh.

set -euo pipefail

OUT=${1:-results/env/environment.txt}
ASAN_OPTS_SHOWN=${ASAN_OPTIONS_DEFAULT:-quarantine_size_mb=0:malloc_context_size=0:detect_leaks=0:redzone=32}
CC_BIN=${CC:-clang}

mkdir -p "$(dirname "$OUT")"

have() { command -v "$1" >/dev/null 2>&1; }

{
    echo "=== CS340 AddressSanitizer replication: environment record ==="
    echo "recorded_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

    echo
    echo "=== Operating system ==="
    if [ -r /etc/os-release ]; then
        grep -E '^(PRETTY_NAME|VERSION_ID|ID)=' /etc/os-release
    else
        echo "os: unknown (no /etc/os-release)"
    fi
    if [ -r /proc/sys/kernel/osrelease ]; then
        echo "kernel_release: $(cat /proc/sys/kernel/osrelease)"
    fi
    echo "uname: $(uname -a)"

    echo
    echo "=== Hardware ==="
    echo "architecture: $(uname -m)"
    echo "nproc: $(nproc 2>/dev/null || getconf _NPROCESSORS_ONLN)"
    if have lscpu; then
        lscpu | grep -E '^(Model name|CPU\(s\)|Thread|Core|Socket|CPU max MHz|CPU min MHz|Vendor ID|L2 cache|L3 cache)' || true
    elif [ -r /proc/cpuinfo ]; then
        grep -m1 -E '^(model name|Hardware)' /proc/cpuinfo || true
    fi
    if [ -r /proc/meminfo ]; then
        grep -E '^(MemTotal|MemAvailable|SwapTotal)' /proc/meminfo
    fi
    echo "virtualisation: $(systemd-detect-virt 2>/dev/null || echo 'n/a')"
    if [ -r /proc/version ]; then
        echo "note_wsl: $(grep -qi microsoft /proc/version && echo 'running under WSL' || echo 'native kernel')"
    fi

    echo
    echo "=== Compilers and tools ==="
    if have "$CC_BIN"; then
        echo "--- $CC_BIN ---"
        "$CC_BIN" --version | head -n 2
        echo "target: $("$CC_BIN" -dumpmachine 2>/dev/null || echo n/a)"
    else
        echo "$CC_BIN: not found"
    fi
    if have gcc; then
        echo "--- gcc ---"
        gcc --version | head -n 1
    fi
    for tool in make python3 git taskset; do
        if have "$tool"; then
            printf '%s: %s\n' "$tool" "$("$tool" --version 2>/dev/null | head -n 1)"
        else
            printf '%s: not found\n' "$tool"
        fi
    done

    echo
    echo "=== AddressSanitizer configuration used for asan runs ==="
    echo "ASAN_OPTIONS=$ASAN_OPTS_SHOWN"
    echo "compile_flags=-fsanitize=address -fno-omit-frame-pointer (overridable with make ASAN=...)"
    echo "optimisation=-O2 for both base and asan binaries"

    echo
    echo "=== Repository state ==="
    if have git && git rev-parse --git-dir >/dev/null 2>&1; then
        echo "HEAD=$(git rev-parse HEAD)"
        echo "describe=$(git describe --always --tags --dirty 2>/dev/null || echo n/a)"
        echo "branch=$(git rev-parse --abbrev-ref HEAD)"
        echo "local_changes:"
        git status --porcelain || true
    else
        echo "not a git checkout"
    fi
} >"$OUT" 2>&1

echo "wrote $OUT"
cat "$OUT"

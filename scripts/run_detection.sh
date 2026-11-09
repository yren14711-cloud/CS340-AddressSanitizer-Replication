#!/usr/bin/env bash
#
# run_detection.sh -- build every memory-error case twice and record what
# AddressSanitizer reports. Covers Claim 3 (detection capability).
#
# For each case in experiments/memory_errors/ it builds
#   build/detect_<case>_plain   plain clang, no instrumentation
#   build/detect_<case>_asan    clang -fsanitize=address
# runs both, and writes
#   results/detect/<case>_plain.log   stdout+stderr and exit code
#   results/detect/<case>_asan.log    same, for the instrumented build
#   results/detect/summary.md         one row per case: exit codes and the
#                                     AddressSanitizer error class it reported
#   results/detect/environment.txt    compiler version and options used
#
# The plain build is the control: for a genuine memory error it either stays
# silent or crashes, and never names the error class. That contrast is what the
# report needs, not just "ASan printed something".
#
# Note on options: this script deliberately uses the DEFAULT AddressSanitizer
# quarantine. The overhead experiments switch quarantine_size_mb off to match
# the paper's methodology, but a use-after-free needs the quarantine to be
# detected reliably, so the two experiments use different configurations and
# each log records the one it used.
#
# Usage: scripts/run_detection.sh [-d CASES_DIR] [-o OUTDIR]
#   Requires clang on PATH; the sources are never modified.

set -euo pipefail

CASES_DIR="experiments/memory_errors"
OUT="results/detect"
CC_BIN=${CC:-clang}
OPT=${OPT:--O1}
ASAN_FLAGS=${ASAN_FLAGS:--fsanitize=address -fno-omit-frame-pointer -g}
DETECT_ASAN_OPTIONS=${DETECT_ASAN_OPTIONS:-detect_leaks=0}

while getopts ":d:o:h" opt; do
    case "$opt" in
        d) CASES_DIR=$OPTARG ;;
        o) OUT=$OPTARG ;;
        h) sed -n '2,30p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) echo "usage: $0 [-d CASES_DIR] [-o OUTDIR]" >&2; exit 2 ;;
    esac
done

if ! command -v "$CC_BIN" >/dev/null 2>&1; then
    echo "$CC_BIN not found on PATH" >&2
    exit 2
fi

if [ ! -d "$CASES_DIR" ]; then
    echo "no such directory: $CASES_DIR" >&2
    exit 2
fi

mkdir -p build "$OUT"

{
    echo "=== CS340 AddressSanitizer replication: detection environment ==="
    echo "recorded_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "host: $(uname -srm)"
    echo "compiler: $($CC_BIN --version | head -n 1)"
    echo "compile_flags_plain: $OPT -Wall -Wextra"
    echo "compile_flags_asan: $OPT -Wall -Wextra $ASAN_FLAGS"
    echo "ASAN_OPTIONS=$DETECT_ASAN_OPTIONS (default quarantine, unlike the overhead runs)"
    if git rev-parse --git-dir >/dev/null 2>&1; then
        echo "git_HEAD=$(git rev-parse HEAD)"
    fi
} >"$OUT/environment.txt"

ROWS=$(mktemp)
trap 'rm -f "$ROWS"' EXIT
printf '| Case | Plain build | ASan build | Reported class | Matches expected |\n' >"$ROWS"
printf '|---|---|---|---|---|\n' >>"$ROWS"

EXPECTED_HEAP="heap-buffer-overflow"
EXPECTED_STACK="stack-buffer-overflow"
EXPECTED_GLOBAL="global-buffer-overflow"
EXPECTED_UAF="heap-use-after-free"

expected_for() {
    case "$1" in
        heap_buffer_overflow)   echo "$EXPECTED_HEAP" ;;
        stack_buffer_overflow)  echo "$EXPECTED_STACK" ;;
        global_buffer_overflow) echo "$EXPECTED_GLOBAL" ;;
        use_after_free)         echo "$EXPECTED_UAF" ;;
        *)                      echo "" ;;
    esac
}

printf '%-24s %-10s %-10s %s\n' "case" "plain" "asan" "reported"

for src in "$CASES_DIR"/*.c; do
    [ -e "$src" ] || continue
    name=$(basename "$src" .c)

    if ! "$CC_BIN" "$OPT" -std=c99 -Wall -Wextra -o "build/detect_${name}_plain" "$src" 2>"$OUT/${name}_plain_build.log"; then
        echo "FAILED to build plain $name (see $OUT/${name}_plain_build.log)" >&2
        continue
    fi
    if ! "$CC_BIN" "$OPT" -std=c99 -Wall -Wextra $ASAN_FLAGS -o "build/detect_${name}_asan" "$src" 2>"$OUT/${name}_asan_build.log"; then
        echo "FAILED to build asan $name (see $OUT/${name}_asan_build.log)" >&2
        continue
    fi

    set +e
    {
        echo "### plain build: $src"
        echo "### command: build/detect_${name}_plain"
    } >"$OUT/${name}_plain.log"
    "./build/detect_${name}_plain" >>"$OUT/${name}_plain.log" 2>&1
    rc_plain=$?

    {
        echo "### asan build: $src"
        echo "### command: ASAN_OPTIONS=$DETECT_ASAN_OPTIONS build/detect_${name}_asan"
    } >"$OUT/${name}_asan.log"
    ASAN_OPTIONS="$DETECT_ASAN_OPTIONS" "./build/detect_${name}_asan" >>"$OUT/${name}_asan.log" 2>&1
    rc_asan=$?
    set -e

    reported="not reported"
    if grep -q '^SUMMARY: AddressSanitizer:' "$OUT/${name}_asan.log" 2>/dev/null; then
        reported=$(sed -n 's/^SUMMARY: AddressSanitizer: \([a-z-]*\).*/\1/p' "$OUT/${name}_asan.log" | head -n 1)
    fi

    expected=$(expected_for "$name")
    if [ -z "$expected" ]; then
        verdict="no expectation"
    elif [ "$reported" = "$expected" ]; then
        verdict="yes"
    else
        verdict="NO"
    fi

    printf '| %s | exit %s | exit %s | %s | %s |\n' "$name" "$rc_plain" "$rc_asan" "$reported" "$verdict" >>"$ROWS"
    printf '%-24s %-10s %-10s %s\n' "$name" "exit $rc_plain" "exit $rc_asan" "$reported"
done

{
    echo "# Detection results (Claim 3)"
    echo
    echo "- generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "- source directory: \`$CASES_DIR\`"
    echo "- compiler: $($CC_BIN --version | head -n 1)"
    echo "- compilation: \`$OPT -Wall -Wextra\`, asan builds add \`$ASAN_FLAGS\`"
    echo "- ASan options: \`$DETECT_ASAN_OPTIONS\` (default quarantine; the overhead runs differ)"
    echo
    echo "Each log records the exit code and the full program output; the"
    echo "\`plain\` log is the control showing that the uninstrumented build does"
    echo "not identify the error."
    echo
    cat "$ROWS"
} >"$OUT/summary.md"

echo
echo "wrote $OUT/summary.md"
echo "next: review the logs, then commit results/detect/ together with the sources"

#!/usr/bin/env bash
#
# run_experiments.sh -- run the base/asan matrix and write one log per run.
#
# For every benchmark and every configuration it performs one discarded warm-up
# run followed by N measured repetitions. Each measured run produces a line
#
#   RESULT bench=... config=... run=... wall_ms=... vmpeak_kb=... vmhwm_kb=... exit=... scale=...
#
# in runs.log, plus the program's own stdout/stderr under raw/. Every number in
# the report is meant to be traceable to these lines.
#
# Measurement notes
#   * wall time is read around fork/exec, so it includes ~1 ms of process
#     start-up; keep runs long enough for that to be a rounding error.
#   * VmPeak and VmHWM are taken from /proc/<pid>/status, which is the same
#     field the paper uses (Table 1 reports VmPeak). They are high-water marks,
#     so the last successful sample is the value reported; the sampling loop
#     only ever underestimates, never overestimates.
#   * AddressSanitizer's default options are deliberately overridden to match
#     the paper's methodology (Section 4): 32-byte redzones, quarantine of zero,
#     and no malloc/free stack unwinding. LeakSanitizer is switched off because
#     it did not exist in 2012.
#
# Usage: scripts/run_experiments.sh [-n RUNS] [-s SCALE] [-b "bench ..."] [-p CPU] [-o OUTDIR]
#   -n  measured repetitions per configuration (default 3, the rubric minimum)
#   -s  scale argument passed to every benchmark (default 1)
#   -b  subset of benchmarks (default: all four)
#   -p  pin both configurations to one CPU with taskset, e.g. -p 2
#   -o  output root (default results/logs)

set -euo pipefail

RUNS=3
SCALE=1
BENCHES="b1_malloc_text b2_pointer_chase b3_matmul b4_string_scan"
PIN=""
OUTROOT="results/logs"
ASAN_OPTS_DEFAULT="quarantine_size_mb=0:malloc_context_size=0:detect_leaks=0:redzone=32"
ASAN_OPTS=${ASAN_OPTIONS_DEFAULT:-$ASAN_OPTS_DEFAULT}

usage() {
    sed -n '2,32p' "$0" | sed 's/^# \{0,1\}//'
    exit "${1:-0}"
}

while getopts ":n:s:b:p:o:h" opt; do
    case "$opt" in
        n) RUNS=$OPTARG ;;
        s) SCALE=$OPTARG ;;
        b) BENCHES=$OPTARG ;;
        p) PIN=$OPTARG ;;
        o) OUTROOT=$OPTARG ;;
        h) usage 0 ;;
        *) usage 2 ;;
    esac
done

case "$RUNS" in
    ''|*[!0-9]*) echo "-n must be a positive integer" >&2; exit 2 ;;
esac
if [ "$RUNS" -lt 1 ]; then
    echo "-n must be at least 1" >&2
    exit 2
fi

if [ ! -d build ]; then
    echo "build/ is missing: run 'make' first" >&2
    exit 2
fi

STAMP=$(date -u +%Y%m%dT%H%M%SZ)
DIR="$OUTROOT/$STAMP"
mkdir -p "$DIR/raw"
LOG="$DIR/runs.log"

{
    echo "# CS340 AddressSanitizer replication -- run matrix"
    echo "# started_utc=$STAMP"
    echo "# host=$(uname -srm)"
    echo "# nproc=$(nproc 2>/dev/null || echo n/a)"
    if command -v clang >/dev/null 2>&1; then
        echo "# clang=$(clang --version | head -n 1)"
    fi
    echo "# repetitions=$RUNS scale=$SCALE pin=${PIN:-none} warmup=1"
    echo "# asan_options=$ASAN_OPTS"
    echo "# benchmarks=$BENCHES"
} >"$LOG"

COOLDOWN=${COOLDOWN:-1}

measure() {
    # $1 bench  $2 config  $3 run tag  $4 output dir  $5 emit(1/0)
    local bench=$1
    local cfg=$2
    local tag=$3
    local outdir=$4
    local emit=$5
    local bin="build/${bench}-${cfg}"
    local base="$outdir/raw/${bench}_${cfg}_${tag}"
    local -a cmd
    local pid rc t0 t1 wall_ms vmpeak vmhwm line key val state rest

    cmd=("$bin" "$SCALE")
    if [ -n "$PIN" ] && command -v taskset >/dev/null 2>&1; then
        cmd=(taskset -c "$PIN" "${cmd[@]}")
    fi

    t0=$(date +%s%N)
    if [ "$cfg" = "asan" ]; then
        ASAN_OPTIONS="$ASAN_OPTS" "${cmd[@]}" >"$base.out" 2>"$base.err" &
    else
        "${cmd[@]}" >"$base.out" 2>"$base.err" &
    fi
    pid=$!

    vmpeak=0
    vmhwm=0
    while :; do
        if [ ! -r "/proc/$pid/stat" ]; then
            break
        fi
        # VmPeak / VmHWM are the high-water marks we care about.
        while read -r key val _rest; do
            case "$key" in
                VmPeak:) vmpeak=$val ;;
                VmHWM:)  vmhwm=$val ;;
            esac
        done <"/proc/$pid/status" 2>/dev/null
        read -r line <"/proc/$pid/stat" 2>/dev/null || break
        rest=${line##*) }
        state=${rest%% *}
        if [ "$state" = "Z" ]; then
            break
        fi
        sleep 0.02
    done

    rc=0
    wait "$pid" || rc=$?
    t1=$(date +%s%N)
    wall_ms=$(( (t1 - t0) / 1000000 ))

    if [ "$emit" = "1" ]; then
        printf 'RESULT bench=%s config=%s run=%s wall_ms=%s vmpeak_kb=%s vmhwm_kb=%s exit=%s scale=%s\n' \
            "$bench" "$cfg" "$tag" "$wall_ms" "$vmpeak" "$vmhwm" "$rc" "$SCALE" |
            tee -a "$LOG"
        if [ "$vmpeak" -eq 0 ] || [ "$vmhwm" -eq 0 ]; then
            echo "  warning: peak sampling produced 0 for $bench/$cfg/$tag (run too short for /proc polling)" >&2
        fi
        if [ "$rc" -ne 0 ]; then
            echo "  warning: $bench/$cfg/$tag exited with $rc -- if this was an asan run, AddressSanitizer aborted and the number is not a valid timing (see $base.err)" >&2
        fi
    fi
}

for bench in $BENCHES; do
    if [ ! -x "build/${bench}-base" ] || [ ! -x "build/${bench}-asan" ]; then
        echo "skip $bench: missing build/${bench}-base or build/${bench}-asan (run make)" >&2
        continue
    fi
    echo "== $bench (scale=$SCALE, repetitions=$RUNS)"
    for cfg in base asan; do
        echo "  -- $cfg"
        measure "$bench" "$cfg" "warmup" "$DIR" 0
        for i in $(seq 1 "$RUNS"); do
            measure "$bench" "$cfg" "run$i" "$DIR" 1
            if [ "$i" -lt "$RUNS" ]; then
                sleep "$COOLDOWN"
            fi
        done
    done

    # Correctness sanity check: instrumentation must not change the output.
    if [ -s "$DIR/raw/${bench}_base_run1.out" ] && [ -s "$DIR/raw/${bench}_asan_run1.out" ]; then
        if ! diff -q "$DIR/raw/${bench}_base_run1.out" "$DIR/raw/${bench}_asan_run1.out" >/dev/null 2>&1; then
            echo "  warning: base and asan produced different output for $bench" >&2
            echo "           base: $(cat "$DIR/raw/${bench}_base_run1.out")" >&2
            echo "           asan: $(cat "$DIR/raw/${bench}_asan_run1.out")" >&2
        fi
    fi
done

{
    echo "# finished_utc=$(date -u +%Y%m%dT%H%M%SZ)"
} >>"$LOG"

echo
echo "logs: $LOG"
echo "next: python3 scripts/parse_results.py --log $LOG"

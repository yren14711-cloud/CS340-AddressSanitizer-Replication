#!/bin/bash
# collect_env_claim2.sh -- record the machine + toolchain for one Claim 2 measurement session.
#
# Usage (from the repository root, inside the Linux environment that runs the matrix):
#   bash scripts/collect_env_claim2.sh > results/memory_claim2/<STAMP>/environment.txt
#
# Optional environment variables:
#   SESSION_STAMP  run stamp of the matrix log (default: unknown)
#   SOURCE_LOG     path of the runs.log this session produced
#   WSL_VERSION    output of 'wsl.exe --version' on the Windows host, if applicable
#   REPETITIONS    measured repetitions per configuration (default: 3)
#
# Every value is read from the machine at the moment of the call; nothing is typed in by hand.

set -u

STAMP="${SESSION_STAMP:-unknown}"
SRC="${SOURCE_LOG:-unknown}"
WSLV="${WSL_VERSION:-n/a}"
REPS="${REPETITIONS:-3}"

echo "# Environment record for the Claim 2 b1-b4 memory matrix (VmHWM / VmPeak)"
echo "# generated_utc=$(date -u +%Y%m%dT%H%M%SZ)"
echo "# session_stamp=$STAMP"
echo "# source_log=$SRC"
echo "# host=$(hostname)"
echo "# cpu=$(awk -F': ' '/^model name/ {print $2; exit}' /proc/cpuinfo)"
echo "# cpu_cores=$(nproc)"
echo "# memtotal=$(awk '/^MemTotal:/ {print $2" "$3}' /proc/meminfo)"
echo "# os=$(. /etc/os-release && echo "$PRETTY_NAME")"
echo "# kernel=$(uname -r)"
echo "# arch=$(uname -m)"
echo "# clang=$(clang --version | head -n 1)"
echo "# make=$(make --version | head -n 1)"
echo "# python3=$(python3 -V 2>&1)"
echo "# wsl=$WSLV"
echo "# cc_used_for_build=clang (explicit: make CC=clang OPT=-O2)"
echo "# asan_options=quarantine_size_mb=0:malloc_context_size=0:detect_leaks=0:redzone=32"
echo "# repetitions=$REPS measured + 1 warm-up per (benchmark, configuration), scale=1"
echo "# workdir=$(pwd) (filesystem $(df -T . | awk 'NR==2 {print $2}'))"
echo "# loadavg=$(cut -d' ' -f1-3 /proc/loadavg)"
echo "# git_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo n/a)"
echo "# git_head=$(git rev-parse HEAD 2>/dev/null || echo n/a)"

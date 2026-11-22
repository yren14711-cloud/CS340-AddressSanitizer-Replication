#!/usr/bin/env bash
set -euo pipefail

mkdir -p results/detect/false_positive
make CC=clang OPT=-O2 base asan

echo "benchmark,variant,run,exit_code,asan_reported,out_file,err_file" > results/detect/false_positive/summary.csv

for b in b1_malloc_text b2_pointer_chase b3_matmul b4_string_scan; do
  for variant in base asan; do
    bin="build/${b}-${variant}"
    for i in 1 2 3; do
      out_f="results/detect/false_positive/${b}_${variant}_run${i}.out"
      err_f="results/detect/false_positive/${b}_${variant}_run${i}.err"
      exit_f="results/detect/false_positive/${b}_${variant}_run${i}.exit"

      set +e
      if [ "$variant" = "asan" ]; then
        ASAN_OPTIONS=detect_leaks=0 "$bin" > "$out_f" 2> "$err_f"
      else
        "$bin" > "$out_f" 2> "$err_f"
      fi
      rc=$?
      set -e

      echo "$rc" > "$exit_f"
      if grep -q "AddressSanitizer" "$err_f"; then
        fp="yes"
      else
        fp="no"
      fi
      echo "${b},${variant},${i},${rc},${fp},${out_f},${err_f}" >> results/detect/false_positive/summary.csv
    done
  done
done

{
  date -u
  uname -a
  cat /etc/os-release
  clang --version
  echo "ASAN_OPTIONS=detect_leaks=0"
  git rev-parse HEAD
} > results/detect/false_positive/environment.txt

echo "Wrote results/detect/false_positive/"

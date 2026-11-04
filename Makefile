# CS340 Operating Systems -- AddressSanitizer replication
#
# Builds every benchmark twice: once as a plain clang -O2 binary, once with
# AddressSanitizer instrumentation, so that the two can be compared under the
# same optimisation level on the same machine.
#
# Common use:
#   make            # build all base + asan binaries into build/
#   make env        # record the environment into results/env/environment.txt
#   make run        # run the experiment matrix (3 repetitions + 1 warm-up)
#   make results    # parse the logs into results/summary/
#   make clean
#
# Everything is overridable, e.g.:
#   make CC=clang OPT=-O1 RUNS=5 SCALE=2

CC      ?= clang
OPT     ?= -O2
STD     ?= -std=c99
WARN    := -Wall -Wextra
CFLAGS  ?= $(OPT) $(STD) $(WARN)
ASAN    ?= -fsanitize=address -fno-omit-frame-pointer

BUILD   := build
RUNS    ?= 3
SCALE   ?= 1

BENCHES  := b1_malloc_text b2_pointer_chase b3_matmul b4_string_scan
BASE_BIN := $(addprefix $(BUILD)/,$(addsuffix -base,$(BENCHES)))
ASAN_BIN := $(addprefix $(BUILD)/,$(addsuffix -asan,$(BENCHES)))

.PHONY: all base asan detect env run results clean help

all: base asan

base: $(BASE_BIN)

asan: $(ASAN_BIN)

$(BUILD):
	mkdir -p $(BUILD)

$(BUILD)/%-base: benchmarks/%.c | $(BUILD)
	$(CC) $(CFLAGS) -o $@ $<

$(BUILD)/%-asan: benchmarks/%.c | $(BUILD)
	$(CC) $(CFLAGS) $(ASAN) -o $@ $<

# AddressSanitizer detection experiments (memory error reports).
# The sources under experiments/ are built here but never modified.
DETECT_SRC := experiments/memory_errors/heap_buffer_overflow.c
detect: $(BUILD)/detect-base $(BUILD)/detect-asan

$(BUILD)/detect-base: $(DETECT_SRC) | $(BUILD)
	$(CC) $(OPT) $(WARN) -o $@ $<

$(BUILD)/detect-asan: $(DETECT_SRC) | $(BUILD)
	$(CC) $(OPT) $(WARN) $(ASAN) -o $@ $<

env:
	bash scripts/collect_env.sh

run: all
	bash scripts/run_experiments.sh -n $(RUNS) -s $(SCALE)

results:
	python3 scripts/parse_results.py

clean:
	rm -rf $(BUILD)

help:
	@echo "targets: all base asan detect env run results clean"
	@echo "vars:    CC=$(CC) OPT=$(OPT) ASAN='$(ASAN)' RUNS=$(RUNS) SCALE=$(SCALE)"
	@echo "bench:   $(BENCHES)"

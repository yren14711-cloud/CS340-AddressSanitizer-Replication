# Credits, attribution and licensing

## Paper reproduced

Konstantin Serebryany, Derek Bruening, Alexander Potapenko, Dmitry Vyukov.
*AddressSanitizer: A Fast Address Sanity Checker.* USENIX Annual Technical
Conference (ATC) 2012.
<https://www.usenix.org/system/files/conference/atc12/atc12-final39.pdf>

This repository contains no code from the paper or from SPEC CPU2006. It
re-implements the measurement methodology described in Section 4 and evaluates a
different, openly available set of workloads.

## Toolchain

The instrumented and reference binaries are built with **Clang**, which is
distributed under the Apache License 2.0 with the LLVM exception.
<https://llvm.org/LICENSE.txt>

AddressSanitizer's compiler instrumentation and runtime library (compiler-rt)
are part of that same project and are used here unmodified, through
`-fsanitize=address`. This repository does not vendor, patch or redistribute
LLVM sources.

Documentation used as a reference for the runtime options:
<https://clang.llvm.org/docs/AddressSanitizer.html>

## Workloads

The four benchmarks in `benchmarks/` were written for this replication. They are
not derived from SPEC, PARSEC or any other third-party suite; `benchmarks/README.md`
explains which behavioural class of the paper's workloads each one stands in for.

## Experiment code

The scripts in `scripts/` and the build in `Makefile` were written for this
replication.

## LICENSE

The original code in this repository (benchmarks, scripts, Makefile, report
sources) is the work of the group members and is released under the **MIT
LICENSE**. The full text is in the `LICENSE` file at the repository root.

Third-party components keep their own LICENSE: Clang and compiler-rt are
Apache-2.0 WITH LLVM-exception, and they are used as an installed toolchain
rather than copied into this repository.

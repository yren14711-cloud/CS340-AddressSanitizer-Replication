# CS340 Research Paper Replication

## 1. Project Information

**Course:** CS340 Operating Systems (2026–2027)

**Paper:** AddressSanitizer: A Fast Address Sanity Checker

**Authors:** Konstantin Serebryany, Derek Bruening, Alexander Potapenko, and Dmitry Vyukov

**Conference:** USENIX ATC 2012

**Paper Link:** https://www.usenix.org/system/files/conference/atc12/atc12-final39.pdf

## 2. Project Objective

The objective of this project is to reproduce selected experiments from the AddressSanitizer research paper.

AddressSanitizer (ASan) is a memory error detection tool for C and C++ programs. It can detect errors such as buffer overflows and use-after-free.

Our replication will investigate the performance overhead and memory usage of programs compiled with AddressSanitizer.

## 3. Planned Reproduction Experiments

### Experiment 1: Memory Error Detection

- Prepare small C/C++ programs containing memory errors.
- Compile the programs with and without AddressSanitizer.
- Run the programs and collect AddressSanitizer error reports.
- Compare the detected errors with the expected behavior.

### Experiment 2: Execution Time Overhead

- Select reproducible benchmark programs.
- Compile each benchmark with and without AddressSanitizer.
- Execute each configuration at least three times.
- Calculate the mean execution time and standard deviation.
- Calculate the slowdown introduced by AddressSanitizer.
- Compare the results with the original paper, noting any differences in workloads and hardware.

### Experiment 3: Memory Usage Overhead

- Measure the peak memory usage of benchmark programs with and without AddressSanitizer.
- Repeat measurements at least three times.
- Compare the results and investigate any differences from the original paper.

## 4. Reproduction Methodology

We will document:

- Hardware and operating system information.
- Compiler and tool versions.
- Benchmark programs and input workloads.
- Build and execution commands.
- Differences between our environment and the original paper.
- Raw experiment logs and processed results.

## 5. Planned Extension

We plan to investigate how different workload sizes influence the performance overhead of AddressSanitizer while keeping other experimental conditions unchanged.

## 6. Project Status

- [x] Research paper assigned.
- [x] GitHub repository created.
- [ ] Experimental environment configured.
- [ ] Memory error detection experiments completed.
- [ ] Performance experiments completed.
- [ ] Results analyzed and visualized.
- [ ] Extension experiment completed.
- [ ] Final report and presentation completed.

## 7. References

1. Serebryany, K., Bruening, D., Potapenko, A., and Vyukov, D. (2012). *AddressSanitizer: A Fast Address Sanity Checker*. USENIX Annual Technical Conference.
2. LLVM AddressSanitizer Documentation: https://clang.llvm.org/docs/AddressSanitizer.html

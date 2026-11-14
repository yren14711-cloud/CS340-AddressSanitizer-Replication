\# Paper vs. Ours



!\[Runtime overhead: paper vs. ours](../results/figures/paper\_vs\_ours\_runtime.png)



\*\*Figure note:\*\* different workloads, not directly equivalent.

The paper reports a 73% average runtime overhead on SPEC CPU2006 (Figure 2).

Our overall overhead is 31.19% on a custom `array\_update` microbenchmark

(64 MiB array, 200 update passes, Clang 21.1.8, WSL2). Batch overheads:

34.52%, 29.27%, 27.62%. Source: `results/performance/performance\_analysis.txt`

and `results/performance/benchmark\_summary.csv`.



These numbers must not be presented as a reproduction of Figure 2.

See also README section 8 and `docs/DEVIATIONS.md`.



\## Memory comparison



Paper Claim 2: 3.37x average VmPeak (Table 1).

Our memory figure: pending 叶/王 data (`results/summary/` or `results/memory/`).

Do not invent a ratio. When those files exist, add

`results/figures/paper\_vs\_ours\_memory.png` here with the same workload caveat.


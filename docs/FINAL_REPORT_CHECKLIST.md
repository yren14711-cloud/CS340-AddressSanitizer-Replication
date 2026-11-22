# Final Report Submission Checklist

This checklist is for final report preparation.
Items should be marked complete only after actual review.

## 1. Course requirements

- [ ] Required report format confirmed.
- [ ] Required length and submission deadline confirmed.
- [ ] Required submission files identified.
- [ ] All author names and student IDs verified.
- [ ] Academic integrity requirements satisfied.

## 2. Report structure

- [ ] Title reflects partial replication and extension.
- [ ] Abstract summarizes the completed study.
- [ ] Introduction states research questions.
- [ ] ASan design and background are explained.
- [ ] Experimental methodology is documented.
- [ ] Runtime results are presented.
- [ ] Memory results are presented.
- [ ] Detection results are presented.
- [ ] Workload-scaling extension is presented.
- [ ] Cross-environment extension is presented.
- [ ] Paper vs. ours comparison is included.
- [ ] Threats to validity are discussed.
- [ ] Conclusion answers the research questions.

## 3. Runtime statistics

- [ ] Week 2 uses 15 measured runs per build.
- [ ] Overall slowdown is verified against the recorded data.
- [ ] Runtime ratio and slowdown percentage are distinguished.
- [ ] Different timing protocols are not pooled.
- [ ] Negative measured slowdown is interpreted cautiously.
- [ ] The paper's 73% is not treated as a directly comparable target.

## 4. Memory statistics

- [ ] VmPeak and VmHWM are correctly distinguished.
- [ ] Virtual address space is not described as physical RAM.
- [ ] The approximate 20 TiB reservation uses the correct unit.
- [ ] Memory ratios use configuration means.
- [ ] Both memory sessions are identified correctly.
- [ ] The 3.37x VmPeak result is not directly compared with VmHWM.
- [ ] Uncertainty and sampling limitations are disclosed.

## 5. Detection evidence

- [ ] Four selected buggy cases are identified.
- [ ] The 4/4 detection result is scoped to the tested cases.
- [ ] Base clean normal exits are reported as 12/12.
- [ ] ASan clean normal exits are reported as 12/12.
- [ ] Combined clean normal exits are reported as 24/24.
- [ ] Observed ASan false positives are reported as 0/12.
- [ ] No universal detection or zero false-positive claim is made.
- [ ] Output equivalence is claimed only where verified.

## 6. Extension studies

- [ ] Three workload scales are described.
- [ ] The four benchmark workloads are explained.
- [ ] Scaling execution counts and aggregate records are distinguished.
- [ ] Cross-environment session counts are correct.
- [ ] Twelve benchmark-session ratios are identified.
- [ ] Seventy-two reused executions are not double-counted.
- [ ] Cross-environment results are interpreted descriptively.
- [ ] No unsupported statistical equivalence claim is made.

## 7. Claim verdicts

- [ ] Claim 1: Partially supported.
- [ ] Claim 2: Inconclusive.
- [ ] Claim 3: Supported for the tested cases.
- [ ] Abstract, discussion and conclusion use consistent verdicts.

## 8. Figures and tables

- [ ] Every included figure has a unique report number.
- [ ] Every included figure is cited in the report text.
- [ ] Figure captions explain the measurement and units.
- [ ] Sample sizes are documented where relevant.
- [ ] Error bars have explicit definitions.
- [ ] Ratio uncertainty is not confused with raw-measurement SD.
- [ ] Figure data matches the repository results.
- [ ] Figure labels are readable in the final document.
- [ ] Supplementary figures are placed appropriately.
- [ ] Figure ordering and references are consistent.

## 9. Reproducibility

- [ ] Report references the reproducibility documentation.
- [ ] Experiment scripts and data sources are identifiable.
- [ ] Historical environment records are used where available.
- [ ] Actual audit outcomes are reviewed.
- [ ] Audit warnings and unresolved limitations are disclosed.
- [ ] Figure regeneration coverage is described accurately.
- [ ] Missing evidence is not fabricated.
- [ ] No stronger reproducibility claim is made than verified.

## 10. References and contributions

- [ ] Original paper citation is verified.
- [ ] External technical references are verified.
- [ ] Borrowed figures or text have appropriate attribution.
- [ ] All cited references appear in the bibliography.
- [ ] Individual contribution descriptions are confirmed.
- [ ] All members have reviewed their assigned sections.
- [ ] All members approve the final report.

## 11. Final submission

- [ ] English terminology and formatting are consistent.
- [ ] Spelling and grammar are checked.
- [ ] All numeric results are checked against source records.
- [ ] All required files are present.
- [ ] The final exported PDF or required format is inspected.
- [ ] The correct repository version is referenced.
- [ ] The submission deadline and upload location are confirmed.
- [ ] Final submission is completed.

## Supporting documents

- [Report outline](REPORT_OUTLINE.md)
- [Contributions](CONTRIBUTIONS.md)
- [Claims](CLAIMS.md)
- [Paper vs. ours](PAPER_VS_OURS.md)
- [Figure inventory](FIGURE_INVENTORY.md)
- [Statistical conventions](STATISTICAL_CONVENTIONS.md)
- [Reproducibility](REPRODUCIBILITY.md)

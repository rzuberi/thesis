# BE paper plan: row count, aggregation and label (report only)

**Status of this file: PRE-SPECIFICATION VERSION**, committed before the analysis was run. Frozen release; nothing retrained; the max-over-rows convention of earlier documents is unchanged.

## 1. Header (completed at the results commit)
- Date: 27 September 2026. Commit at start: `6cafa6c`. Pre-specification commit: the commit adding this text. Script `scripts/paper_plan/pr_rowcount.py`; renderer `pr_render.py`; outputs `results/paper_final/rowcount.json`, figures `results/paper_final/figs/F_intro_forest_v2.*`, `F_table_forest_v2.*` (new files; the earlier figures are not overwritten), copies in `~/Downloads/be_paper_figs/` with `README.md`.

## Pre-specification
1. Rows per patient (strict pre-event rows in the release) by label, for LGD2+ and E-HGD, within discovery (82), validation (68) and all 150: median, IQR, Mann-Whitney p (two-sided); AUROC of the row count alone as a score (raw direction: more rows = higher score) with patient bootstrap CI, per population and endpoint.
2. Per whiteboard arm (C2, CNV RF, CNV KM, WSI, early, intermediate, late mean; co-attention and late-stack as supplementary), discovery LGD2+: AUROC under max, mean and last pre-event row (row with the latest `Date`; ties broken by sample id) within patients with 1–2 rows and with ≥ 3 rows (n / events stated), and on all 82. Spearman of row count with the patient score among discovery non-progressors, under max and under mean.
3. Mean aggregation, discovery and stratified, LGD2+ and E-HGD: paired differences with CI and one-sided permutation p for WSI − CNV(RF), WSI − CNV(KM), each of the five fusion arms − WSI (selection-adjusted p = P(max over the five permuted differences ≥ observed)), late fusion − CNV(RF), and C2 + modality − C2 where the combination is the fold-local z-mean of C2 rows and modality rows as in the follow-up (F3), then the patient **mean** over rows. Bootstrap: patients (within stratum for the stratified population); permutations: patient labels permuted within stratum for the stratified population, freely for discovery.
4. F-intro v2 and F-table v2: the existing panels reproduced from the same numbers, with a mean-aggregation panel beside each max panel (same populations, endpoints, arms, layout and styling; only the aggregation differs). Saved as new files with their JSON.
5. Copies of `F_intro_forest_v2.png`, `F_table_forest_v2.png`, `F_intro_forest.png`, `F_table_forest.png`, `F_D1_risk_groups.png` … `F_D6_false_negatives.png` to `~/Downloads/be_paper_figs/` with a `README.md` mapping each file to its whiteboard point. No tissue images.

(Results follow in the results commit.)

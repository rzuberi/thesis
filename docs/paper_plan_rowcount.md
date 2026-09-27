# BE paper plan: row count, aggregation and label (report only)

## 1. Header
- Date: 27 September 2026. Commit at start: `6cafa6c`. Pre-specification commit: `9ac8165` (verbatim in §6). Results commit: `47e9562`; this text is the next commit. Frozen release; nothing retrained; the max-over-rows convention is unchanged (report only).
- Outputs: `results/paper_final/rowcount.json`; figures `results/paper_final/figs/F_intro_forest_v2.{png,pdf,json}`, `F_table_forest_v2.{png,pdf,json}`; copies of all paper figures in `~/Downloads/be_paper_figs/` with `README.md` (laptop only, not committed).

## 2. Status table
| item | status | key number |
|---|---|---|
| 1 Rows per patient by label | DONE | discovery LGD2+: progressors median 3.0 vs non-progressors 8.0 rows, MW p <0.001; row count alone AUROC 0.201 [0.111, 0.301] |
| 2 Aggregation by row-count group | DONE | late fusion (1–2 rows, n 22/18): max 0.764, mean 0.722; (≥3 rows, n 60/22): max 0.751, mean 0.813, last 0.761 |
| 3 Mean-aggregation differences | DONE | discovery LGD2+: WSI − CNV(RF) +0.012 [-0.141, +0.174]; late − WSI +0.059 [0.010, 0.113], selection-adjusted p 0.2314 |
| 4 F-intro v2, F-table v2 | DONE | `results/paper_final/figs/F_intro_forest_v2.png`, `F_table_forest_v2.png` |
| 5 Figure copies | DONE | `~/Downloads/be_paper_figs/` (README lists whiteboard point per file) |

## 3. Items

### 1. Rows per patient by label
**Status.** DONE. **Pre-specification.** `9ac8165`.

| population | endpoint | n / events | rows, progressors median [IQR] | rows, non-progressors median [IQR] | Mann-Whitney p | AUROC of row count alone (more rows = higher) [CI] |
|---|---|---|---|---|---|---|
| discovery | LGD2plus | 82 / 40 | 3.0 [2.0, 5.0] | 8.0 [4.25, 12.0] | <0.001 | 0.201 [0.111, 0.301] |
| discovery | E_HGD | 82 / 26 | 4.0 [2.0, 6.75] | 7.0 [2.75, 10.25] | 0.085 | 0.382 [0.262, 0.504] |
| validation | LGD2plus | 68 / 10 | 3.0 [2.25, 5.75] | 2.5 [1.0, 4.0] | 0.098 | 0.662 [0.456, 0.849] |
| validation | E_HGD | 68 / 10 | 3.0 [2.25, 5.75] | 2.5 [1.0, 4.0] | 0.098 | 0.662 [0.456, 0.849] |
| all_150 | LGD2plus | 150 / 50 | 3.0 [2.0, 5.0] | 4.0 [2.0, 7.25] | 0.255 | 0.443 [0.350, 0.545] |
| all_150 | E_HGD | 150 / 36 | 4.0 [2.0, 6.25] | 3.0 [2.0, 7.0] | 0.489 | 0.538 [0.438, 0.640] |

**Sources.** `results/paper_final/rowcount.json` · `scripts/paper_plan/pr_rowcount.py` · commit 47e9562 (`item1_rows_per_patient`). **Caveats.** Row count is the number of strict pre-event release rows, which depends on surveillance history and on the event time (progressors accrue rows until the endpoint).

### 2. Aggregation rule by row-count group (discovery, LGD2+)
**Status.** DONE. **Pre-specification.** `9ac8165`. Groups: 1–2 rows n 22 / events 18; ≥ 3 rows n 60 / events 22.

| arm | all 82: max / mean / last | 1–2 rows: max / mean / last | ≥3 rows: max / mean / last | Spearman(row count, score) non-progressors: max / mean |
|---|---|---|---|---|
| Clinical (C2) | 0.625 / 0.680 / 0.720 | 0.854 / 0.854 / 0.854 | 0.546 / 0.594 / 0.654 | +0.360 / +0.317 |
| CNV (release RF) | 0.564 / 0.746 / 0.731 | 0.486 / 0.444 / 0.500 | 0.642 / 0.766 / 0.746 | +0.114 / -0.438 |
| CNV (Killcoyne method) | 0.580 / 0.664 / 0.621 | 0.375 / 0.306 / 0.361 | 0.695 / 0.762 / 0.685 | -0.065 / -0.216 |
| WSI | 0.649 / 0.759 / 0.730 | 0.750 / 0.750 / 0.708 | 0.705 / 0.767 / 0.720 | +0.212 / +0.009 |
| Early fusion | 0.704 / 0.777 / 0.804 | 0.667 / 0.667 / 0.736 | 0.821 / 0.829 / 0.833 | +0.250 / -0.006 |
| Intermediate fusion | 0.684 / 0.807 / 0.795 | 0.903 / 0.875 / 0.861 | 0.696 / 0.770 / 0.761 | +0.313 / +0.037 |
| Late fusion (mean) | 0.691 / 0.818 / 0.772 | 0.764 / 0.722 / 0.708 | 0.751 / 0.813 / 0.761 | +0.180 / -0.164 |
| Co-attention (suppl.) | 0.625 / 0.749 / 0.779 | 0.611 / 0.681 / 0.750 | 0.763 / 0.788 / 0.813 | +0.265 / -0.043 |
| Late stack (suppl.) | 0.647 / 0.767 / 0.738 | 0.764 / 0.764 / 0.708 | 0.709 / 0.766 / 0.724 | +0.189 / -0.146 |

**Sources.** `results/paper_final/rowcount.json` · `scripts/paper_plan/pr_rowcount.py` · commit 47e9562 (`item2_aggregation_by_rowcount`). **Caveats.** Within-group AUROCs rest on few events; "last" = the row with the latest date.

### 3. Paired differences under mean aggregation
**Status.** DONE. **Pre-specification.** `9ac8165`. Permutations within stratum for the stratified population.

**discovery, LGD2+** (n 82, events 40); mean-aggregated AUROCs: Clinical (C2) 0.680, CNV (release RF) 0.746, CNV (Killcoyne method) 0.664, WSI 0.759, Early fusion 0.777, Intermediate fusion 0.807, Late fusion (mean) 0.818, Co-attention (suppl.) 0.749, Late stack (suppl.) 0.767, C2 + WSI 0.803, C2 + CNV(RF) 0.837, C2 + CNV(KM) 0.784, C2 + late fusion 0.835, C2 + WSI + CNV(RF) 0.872

| difference | Δ [CI] | perm p | selection-adjusted p (fusion − WSI) |
|---|---|---|---|
| image_only − cnv_only | +0.012 [-0.141, +0.174] | 0.4318 |  |
| image_only − cnv_km | +0.095 [-0.064, +0.255] | 0.1419 |  |
| late_mean − cnv_only | +0.071 [-0.047, +0.199] | 0.1354 |  |
| C2+image − C2_grade_maxsofar | +0.123 [0.040, 0.212] | 0.0025 |  |
| C2+cnv_only − C2_grade_maxsofar | +0.157 [0.056, 0.257] | 0.001 |  |
| C2+cnv_km − C2_grade_maxsofar | +0.104 [0.008, 0.199] | 0.016 |  |
| C2+late_mean − C2_grade_maxsofar | +0.155 [0.067, 0.253] | 0.001 |  |
| C2+image+cnv_only − C2_grade_maxsofar | +0.192 [0.092, 0.297] | 0.001 |  |
| early_fusion − image_only | +0.018 [-0.070, +0.107] | 0.3628 | 0.6422 |
| intermediate_fusion − image_only | +0.048 [-0.035, +0.132] | 0.1459 | 0.3178 |
| late_mean − image_only | +0.059 [0.010, 0.113] | 0.005 | 0.2314 |
| coattention_fusion − image_only | -0.010 [-0.115, +0.100] | 0.5592 | 0.9025 |
| late_stack_logit − image_only | +0.008 [-0.045, +0.061] | 0.3683 | 0.7461 |

**discovery, E-HGD (post hoc)** (n 82, events 26); mean-aggregated AUROCs: Clinical (C2) 0.424, CNV (release RF) 0.677, CNV (Killcoyne method) 0.718, WSI 0.681, Early fusion 0.751, Intermediate fusion 0.727, Late fusion (mean) 0.718, Co-attention (suppl.) 0.712, Late stack (suppl.) 0.694, C2 + WSI 0.576, C2 + CNV(RF) 0.616, C2 + CNV(KM) 0.579, C2 + late fusion 0.607, C2 + WSI + CNV(RF) 0.679

| difference | Δ [CI] | perm p | selection-adjusted p (fusion − WSI) |
|---|---|---|---|
| image_only − cnv_only | +0.003 [-0.156, +0.178] | 0.4758 |  |
| image_only − cnv_km | -0.038 [-0.200, +0.133] | 0.6477 |  |
| late_mean − cnv_only | +0.041 [-0.084, +0.180] | 0.2744 |  |
| C2+image − C2_grade_maxsofar | +0.151 [0.055, 0.256] | 0.002 |  |
| C2+cnv_only − C2_grade_maxsofar | +0.192 [0.077, 0.323] | 0.0005 |  |
| C2+cnv_km − C2_grade_maxsofar | +0.155 [0.038, 0.278] | 0.003 |  |
| C2+late_mean − C2_grade_maxsofar | +0.183 [0.083, 0.292] | 0.0005 |  |
| C2+image+cnv_only − C2_grade_maxsofar | +0.255 [0.140, 0.377] | 0.0005 |  |
| early_fusion − image_only | +0.070 [-0.018, +0.166] | 0.082 | 0.1884 |
| intermediate_fusion − image_only | +0.046 [-0.033, +0.131] | 0.1754 | 0.3763 |
| late_mean − image_only | +0.038 [-0.016, +0.099] | 0.061 | 0.4333 |
| coattention_fusion − image_only | +0.031 [-0.069, +0.139] | 0.3123 | 0.4973 |
| late_stack_logit − image_only | +0.014 [-0.049, +0.077] | 0.3188 | 0.7011 |

**stratified, LGD2+** (n 150, events 50); mean-aggregated AUROCs: Clinical (C2) 0.637, CNV (release RF) 0.727, CNV (Killcoyne method) 0.665, WSI 0.788, Early fusion 0.805, Intermediate fusion 0.821, Late fusion (mean) 0.839, Co-attention (suppl.) 0.788, Late stack (suppl.) 0.791, C2 + WSI 0.825, C2 + CNV(RF) 0.813, C2 + CNV(KM) 0.780, C2 + late fusion 0.857, C2 + WSI + CNV(RF) 0.883

| difference | Δ [CI] | perm p | selection-adjusted p (fusion − WSI) |
|---|---|---|---|
| image_only − cnv_only | +0.062 [-0.068, +0.183] | 0.1899 |  |
| image_only − cnv_km | +0.124 [-0.006, +0.259] | 0.052 |  |
| late_mean − cnv_only | +0.113 [0.011, 0.212] | 0.0225 |  |
| C2+image − C2_grade_maxsofar | +0.188 [0.101, 0.280] | 0.0005 |  |
| C2+cnv_only − C2_grade_maxsofar | +0.176 [0.080, 0.277] | 0.0005 |  |
| C2+cnv_km − C2_grade_maxsofar | +0.144 [0.049, 0.244] | 0.0015 |  |
| C2+late_mean − C2_grade_maxsofar | +0.221 [0.135, 0.317] | 0.0005 |  |
| C2+image+cnv_only − C2_grade_maxsofar | +0.246 [0.150, 0.343] | 0.0005 |  |
| early_fusion − image_only | +0.016 [-0.051, +0.086] | 0.3393 | 0.6202 |
| intermediate_fusion − image_only | +0.033 [-0.031, +0.094] | 0.1929 | 0.4063 |
| late_mean − image_only | +0.051 [0.014, 0.093] | 0.003 | 0.2169 |
| coattention_fusion − image_only | -0.000 [-0.082, +0.083] | 0.4963 | 0.8446 |
| late_stack_logit − image_only | +0.002 [-0.038, +0.043] | 0.4543 | 0.8156 |

**stratified, E-HGD (post hoc)** (n 150, events 36); mean-aggregated AUROCs: Clinical (C2) 0.449, CNV (release RF) 0.675, CNV (Killcoyne method) 0.704, WSI 0.736, Early fusion 0.789, Intermediate fusion 0.766, Late fusion (mean) 0.771, Co-attention (suppl.) 0.765, Late stack (suppl.) 0.741, C2 + WSI 0.665, C2 + CNV(RF) 0.652, C2 + CNV(KM) 0.633, C2 + late fusion 0.696, C2 + WSI + CNV(RF) 0.746

| difference | Δ [CI] | perm p | selection-adjusted p (fusion − WSI) |
|---|---|---|---|
| image_only − cnv_only | +0.061 [-0.077, +0.195] | 0.2069 |  |
| image_only − cnv_km | +0.032 [-0.106, +0.177] | 0.3453 |  |
| late_mean − cnv_only | +0.096 [-0.013, +0.210] | 0.052 |  |
| C2+image − C2_grade_maxsofar | +0.216 [0.125, 0.317] | 0.0005 |  |
| C2+cnv_only − C2_grade_maxsofar | +0.204 [0.098, 0.323] | 0.0005 |  |
| C2+cnv_km − C2_grade_maxsofar | +0.184 [0.071, 0.304] | 0.0005 |  |
| C2+late_mean − C2_grade_maxsofar | +0.248 [0.155, 0.354] | 0.0005 |  |
| C2+image+cnv_only − C2_grade_maxsofar | +0.297 [0.193, 0.409] | 0.0005 |  |
| early_fusion − image_only | +0.054 [-0.013, +0.130] | 0.1144 | 0.2224 |
| intermediate_fusion − image_only | +0.030 [-0.035, +0.100] | 0.2134 | 0.4623 |
| late_mean − image_only | +0.035 [-0.005, +0.079] | 0.0315 | 0.3948 |
| coattention_fusion − image_only | +0.029 [-0.050, +0.113] | 0.2799 | 0.4713 |
| late_stack_logit − image_only | +0.005 [-0.041, +0.052] | 0.4053 | 0.7776 |

**Sources.** `results/paper_final/rowcount.json` · `scripts/paper_plan/pr_rowcount.py` · commit 47e9562 (`item3_mean_aggregation_differences`). **Caveats.** C2 + modality combinations use the fold-z row combination of the follow-up with mean aggregation; the arms were trained with max-over-rows evaluation in the release.

### 4. Figures v2
**Status.** DONE. `F_intro_forest_v2`: the F-intro panels (max over rows, top row) with the same panels under mean over rows (bottom row). `F_table_forest_v2`: F-table panels A–C (max, top row) and A–C under mean (bottom row). Numbers in the figure JSONs.

| population | endpoint | n / events | WSI max | WSI mean | CNV(RF) max | CNV(RF) mean | WSI − CNV(RF) max | WSI − CNV(RF) mean |
|---|---|---|---|---|---|---|---|---|
| discovery | LGD2plus | 82 / 40 | 0.649 [0.527, 0.765] | 0.759 [0.643, 0.857] | 0.564 [0.427, 0.693] | 0.746 [0.626, 0.854] | 0.086 [-0.084, +0.266] | 0.012 [-0.141, +0.174] |
| stratified | LGD2plus | 150 / 50 | 0.708 [0.612, 0.796] | 0.788 [0.696, 0.864] | 0.594 [0.488, 0.695] | 0.727 [0.630, 0.819] | 0.114 [-0.029, +0.253] | 0.062 [-0.068, +0.183] |
| pooled | LGD2plus | 150 / 50 | 0.731 [0.640, 0.814] | 0.756 [0.663, 0.837] | 0.663 [0.569, 0.754] | 0.748 [0.653, 0.830] | 0.068 [-0.065, +0.196] | 0.008 [-0.120, +0.131] |
| discovery | E_HGD | 82 / 26 | 0.658 [0.527, 0.782] | 0.681 [0.556, 0.802] | 0.639 [0.491, 0.779] | 0.677 [0.538, 0.809] | 0.019 [-0.151, +0.203] | 0.003 [-0.156, +0.178] |
| stratified | E_HGD | 150 / 36 | 0.721 [0.616, 0.816] | 0.736 [0.633, 0.826] | 0.651 [0.532, 0.771] | 0.675 [0.560, 0.779] | 0.070 [-0.082, +0.219] | 0.061 [-0.077, +0.195] |
| pooled | E_HGD | 150 / 36 | 0.746 [0.650, 0.837] | 0.737 [0.637, 0.828] | 0.676 [0.561, 0.774] | 0.696 [0.585, 0.795] | 0.070 [-0.066, +0.212] | 0.041 [-0.092, +0.179] |

| arm | A discovery LGD2+ max | A mean | B discovery E-HGD max | B mean | C stratified LGD2+ max | C mean |
|---|---|---|---|---|---|---|
| Clinical (C2) | 0.625 [0.498, 0.744] | 0.680 [0.558, 0.790] | 0.412 [0.277, 0.545] | 0.424 [0.290, 0.559] | 0.601 [0.492, 0.704] | 0.637 [0.532, 0.738] |
| CNV (release RF) | 0.564 [0.427, 0.693] | 0.746 [0.626, 0.854] | 0.639 [0.491, 0.779] | 0.677 [0.538, 0.809] | 0.594 [0.488, 0.695] | 0.727 [0.630, 0.819] |
| CNV (Killcoyne method) | 0.580 [0.443, 0.714] | 0.664 [0.537, 0.780] | 0.698 [0.556, 0.830] | 0.718 [0.587, 0.838] | 0.597 [0.486, 0.703] | 0.665 [0.555, 0.761] |
| WSI | 0.649 [0.527, 0.765] | 0.759 [0.643, 0.857] | 0.658 [0.527, 0.782] | 0.681 [0.556, 0.802] | 0.708 [0.612, 0.796] | 0.788 [0.696, 0.864] |
| Early fusion | 0.704 [0.579, 0.812] | 0.777 [0.667, 0.874] | 0.751 [0.618, 0.866] | 0.751 [0.617, 0.867] | 0.735 [0.642, 0.820] | 0.805 [0.714, 0.877] |
| Intermediate fusion | 0.684 [0.567, 0.798] | 0.807 [0.702, 0.900] | 0.687 [0.560, 0.806] | 0.727 [0.606, 0.838] | 0.717 [0.619, 0.806] | 0.821 [0.738, 0.894] |
| Late fusion (mean) | 0.691 [0.569, 0.803] | 0.818 [0.719, 0.906] | 0.701 [0.573, 0.821] | 0.718 [0.594, 0.835] | 0.745 [0.652, 0.829] | 0.839 [0.762, 0.907] |
| Co-attention (suppl.) | 0.625 [0.505, 0.743] | 0.749 [0.637, 0.854] | 0.683 [0.557, 0.806] | 0.712 [0.582, 0.827] | 0.695 [0.596, 0.792] | 0.788 [0.702, 0.865] |
| Late stack (suppl.) | 0.647 [0.524, 0.763] | 0.767 [0.656, 0.863] | 0.664 [0.536, 0.789] | 0.694 [0.566, 0.816] | 0.701 [0.602, 0.791] | 0.791 [0.698, 0.863] |

**Sources.** `results/paper_final/figs/F_intro_forest_v2.json`, `F_table_forest_v2.json` · `scripts/paper_plan/pr_rowcount.py` · commit 47e9562.

### 5. Figure copies
**Status.** DONE. `~/Downloads/be_paper_figs/` holds the PNGs of F_intro (v1 and v2), F_table (v1 and v2) and F_D1–F_D6 with `README.md`; no tissue images.

## 4. Discrepancies found
1. Row count differs by label in every population (item 1) and predicts the label by itself; the max-over-rows aggregation used throughout is therefore entangled with row count, and mean aggregation gives higher AUROCs for every arm (item 3; `docs/paper_plan_aggregation.md`). The aggregation rule was fixed in the release before any of this work and is left unchanged here.

## 5. Not done
- No change to the aggregation convention; no retraining.

## 6. Pre-specification text as committed at `9ac8165` (verbatim)

> # BE paper plan: row count, aggregation and label (report only)
>
> **Status of this file: PRE-SPECIFICATION VERSION**, committed before the analysis was run. Frozen release; nothing retrained; the max-over-rows convention of earlier documents is unchanged.
>
> ## 1. Header (completed at the results commit)
> - Date: 27 September 2026. Commit at start: `6cafa6c`. Pre-specification commit: the commit adding this text. Script `scripts/paper_plan/pr_rowcount.py`; renderer `pr_render.py`; outputs `results/paper_final/rowcount.json`, figures `results/paper_final/figs/F_intro_forest_v2.*`, `F_table_forest_v2.*` (new files; the earlier figures are not overwritten), copies in `~/Downloads/be_paper_figs/` with `README.md`.
>
> ## Pre-specification
> 1. Rows per patient (strict pre-event rows in the release) by label, for LGD2+ and E-HGD, within discovery (82), validation (68) and all 150: median, IQR, Mann-Whitney p (two-sided); AUROC of the row count alone as a score (raw direction: more rows = higher score) with patient bootstrap CI, per population and endpoint.
> 2. Per whiteboard arm (C2, CNV RF, CNV KM, WSI, early, intermediate, late mean; co-attention and late-stack as supplementary), discovery LGD2+: AUROC under max, mean and last pre-event row (row with the latest `Date`; ties broken by sample id) within patients with 1–2 rows and with ≥ 3 rows (n / events stated), and on all 82. Spearman of row count with the patient score among discovery non-progressors, under max and under mean.
> 3. Mean aggregation, discovery and stratified, LGD2+ and E-HGD: paired differences with CI and one-sided permutation p for WSI − CNV(RF), WSI − CNV(KM), each of the five fusion arms − WSI (selection-adjusted p = P(max over the five permuted differences ≥ observed)), late fusion − CNV(RF), and C2 + modality − C2 where the combination is the fold-local z-mean of C2 rows and modality rows as in the follow-up (F3), then the patient **mean** over rows. Bootstrap: patients (within stratum for the stratified population); permutations: patient labels permuted within stratum for the stratified population, freely for discovery.
> 4. F-intro v2 and F-table v2: the existing panels reproduced from the same numbers, with a mean-aggregation panel beside each max panel (same populations, endpoints, arms, layout and styling; only the aggregation differs). Saved as new files with their JSON.
> 5. Copies of `F_intro_forest_v2.png`, `F_table_forest_v2.png`, `F_intro_forest.png`, `F_table_forest.png`, `F_D1_risk_groups.png` … `F_D6_false_negatives.png` to `~/Downloads/be_paper_figs/` with a `README.md` mapping each file to its whiteboard point. No tissue images.
>
> (Results follow in the results commit.)
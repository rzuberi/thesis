# BE paper: final checks and figures (K1–K5, F-intro, F-table, F-D1–F-D6)

## 1. Header
- Date: 26 September 2026. Commit at start: `4e0cc2d`. Pre-specification commit: `e6e00c0` (verbatim in §6). Results commit: `50bd222`; this text is the next commit. Frozen release only; nothing retrained.
- Scripts: `scripts/paper_plan/pk_gpu.py` (K4 ablation), `pk_main.py` (K1–K5, all figures), `pk_render.py`, `pk_check_report.py`. Results: `results/paper_final/final_checks.json`, `results/paper_final/k4_ablation.json`; figures `results/paper_final/figs/<name>.png|pdf` with `<name>.json` holding the plotted numbers. Row-level ablation scores: `feasibility/paper_plan/pk_ablation_rows.csv` (cluster). No tissue images are committed; montages remain at `feasibility/paper_plan/figs/attention/` (cluster).
- Analysis decisions applied: primary population = 82 discovery patients (40 LGD2+ events, 26 HGD/IMC events); secondary = stratified all-150, then pooled (confounded); primary endpoint LGD2+; E-HGD labelled as added after seeing the CNV results; tissue amount an unresolved confound; arms as listed; ERIN grade head excluded.

## 2. Status table
| item | status | key number / path |
|---|---|---|
| K1 FP by stratum | DONE | late fusion later HGD+: discovery FP 3/22 vs TN 3/20 (p 1.0); validation FP 8/18 vs TN 1/40 (p <0.001) |
| K2 FN within discovery | DONE | late fusion FN 11 vs TP 29; kept_tiles MW p 0.002, cx p 0.041, reads p 0.002 |
| K3 Latent within discovery | DONE | probe AUROC discovery: image 0.783, intermediate 0.807, early 0.799 (pooled 0.784 / 0.819 / 0.822) |
| K4 CNV use and rank shift | DONE | discovery CNV-destroyed Δ: early +0.068, intermediate +0.059, co-attention +0.045; Spearman CNV vs late (discovery) 0.260, NRI [0.312, -0.016, 0.626] |
| K5 Risk groups within discovery | DONE | late fusion LGD2+ tertile rates 0.333, 0.385, 0.657; OR high vs low [3.635, 1.189, 11.108]; trend p 0.012 |
| F-intro | DONE | `results/paper_final/figs/F_intro_forest.png` |
| F-table | DONE | `results/paper_final/figs/F_table_forest.png` |
| F-D1 | DONE | `results/paper_final/figs/F_D1_risk_groups.png` |
| F-D2 | DONE | `results/paper_final/figs/F_D2_latent.png` |
| F-D3 | DONE | `results/paper_final/figs/F_D3_attention.png` |
| F-D4 | DONE | `results/paper_final/figs/F_D4_cnv_change.png` |
| F-D5 | DONE | `results/paper_final/figs/F_D5_false_positives.png` |
| F-D6 | DONE | `results/paper_final/figs/F_D6_false_negatives.png` |

## 3. Checks

### K1. False positives by stratum
**Question.** Where does the pooled FP excess of later HGD+ live?

**Status.** DONE. **Pre-specification.** `e6e00c0` §K1.

| model | stratum | FP | TN | later HGD+ FP (rate [Wilson]) | later HGD+ TN (rate [Wilson]) | Fisher p |
|---|---|---|---|---|---|---|
| Late fusion (mean) | discovery | 22 | 20 | 3 (0.136 [0.047, 0.333]) | 3 (0.150 [0.052, 0.360]) | 1.0 |
| Late fusion (mean) | validation | 18 | 40 | 8 (0.444 [0.246, 0.663]) | 1 (0.025 [0.004, 0.129]) | <0.001 |
| WSI | discovery | 25 | 17 | 3 (0.120 [0.042, 0.300]) | 3 (0.176 [0.062, 0.410]) | 0.672 |
| WSI | validation | 25 | 33 | 8 (0.320 [0.172, 0.516]) | 1 (0.030 [0.005, 0.153]) | 0.004 |
| CNV (release RF) | discovery | 35 | 7 | 6 (0.171 [0.081, 0.327]) | 0 (0.000 [0.000, 0.354]) | 0.567 |
| CNV (release RF) | validation | 20 | 38 | 7 (0.350 [0.181, 0.567]) | 2 (0.053 [0.015, 0.173]) | 0.006 |
| Clinical (C2) | discovery | 30 | 12 | 4 (0.133 [0.053, 0.297]) | 2 (0.167 [0.047, 0.448]) | 1.0 |
| Clinical (C2) | validation | 26 | 32 | 6 (0.231 [0.110, 0.421]) | 3 (0.094 [0.032, 0.242]) | 0.274 |

Validation non-progressors, logistic later HGD+ ~ FP + baseline grade + log kept_tiles:

| model | OR FP [CI] | p | OR log tiles | OR baseline grade | n / events | separated |
|---|---|---|---|---|---|---|
| Late fusion (mean) | n/a n/a | None | n/a | n/a | None / None | Singular matrix |
| WSI | n/a n/a | None | n/a | n/a | None / None | Singular matrix |
| CNV (release RF) | n/a n/a | None | n/a | n/a | None / None | Singular matrix |
| Clinical (C2) | n/a n/a | None | n/a | n/a | None / None | Singular matrix |

Spearman of kept_tiles with later HGD+ among validation non-progressors: {'rho': -0.414, 'p': 0.001, 'n': 58, 'events': 9}. Discovery non-progressors: {'n': 42, 'db_followup_days_median_iqr': [2506.5, 808.0, 3183.25], 'share_with_any_later_db_report': 0.976, 'killcoyne_sheet_controls_NP': 37, 'killcoyne_sheet_cases_P_labelled_nonprogressor_by_us': 5, 'later_HGDplus': 6, 'later_LGDplus': 8}.

**Method.** Pooled operating point (follow-up predictions). **Sources.** `results/paper_final/final_checks.json` · `scripts/paper_plan/pk_main.py` · commit 50bd222 (`K1`). **Caveats.** Validation non-progressors number None with None later-HGD+ events; logistic fits with three covariates are near separation for some models.

### K2. False negatives within discovery
**Question.** Does the FN vs TP difference survive when both groups are discovery progressors?

**Status.** DONE. **Pre-specification.** `e6e00c0` §K2.

**Late fusion (mean)** (FN 11, TP 29, discovery progressors only)

| variable | FN median (n) | TP median (n) | test | p |
|---|---|---|---|---|
| first_to_event | 898.0 (11) | 1096.0 (29) | Mann-Whitney | 0.348 |
| n_rows | 2.0 (11) | 4.0 (29) | Mann-Whitney | 0.1 |
| baseline_grade | 0.0 (11) | 0.0 (29) | Mann-Whitney | 0.359 |
| max_sofar | 2.0 (11) | 2.0 (29) | Mann-Whitney | 0.773 |
| cx | 24.0 (11) | 55.0 (29) | Mann-Whitney | 0.041 |
| noise | 0.074 (11) | 0.064 (29) | Mann-Whitney | 0.016 |
| segments | 179.5 (11) | 223.0 (29) | Mann-Whitney | 0.155 |
| frac_alt | 0.029 (11) | 0.043 (29) | Mann-Whitney | 0.13 |
| reads | 18533790.0 (11) | 23077752.375 (28) | Mann-Whitney | 0.002 |
| kept_tiles | 3194.143 (11) | 991.0 (29) | Mann-Whitney | 0.002 |
| tissue_frac | 0.111 (11) | 0.133 (29) | Mann-Whitney | 0.056 |
| endpoint_type | {'FN': {'HGD': 2, 'IMC/cancer': 3, 'second LGD': 6}, 'TP': {'HGD': 16, 'IMC/cancer': 5, 'second LGD': 8}} |  | Fisher (2×2 only) | None |
| scanner | {'FN': {'C13210': 0, 'C13239-01': 11}, 'TP': {'C13210': 12, 'C13239-01': 17}} |  | Fisher (2×2 only) | 0.017 |
| p53 | {'FN': {'aberrant': 2, 'missing': 2, 'normal': 7}, 'TP': {'aberrant': 13, 'missing': 0, 'normal': 16}} |  | Fisher (2×2 only) | None |

**WSI** (FN 13, TP 27, discovery progressors only)

| variable | FN median (n) | TP median (n) | test | p |
|---|---|---|---|---|
| first_to_event | 933.0 (13) | 1096.0 (27) | Mann-Whitney | 0.729 |
| n_rows | 2.0 (13) | 4.0 (27) | Mann-Whitney | 0.128 |
| baseline_grade | 0.0 (13) | 0.0 (27) | Mann-Whitney | 0.729 |
| max_sofar | 2.0 (13) | 2.0 (27) | Mann-Whitney | 0.897 |
| cx | 31.0 (13) | 62.0 (27) | Mann-Whitney | 0.024 |
| noise | 0.075 (13) | 0.064 (27) | Mann-Whitney | 0.004 |
| segments | 179.5 (13) | 229.7 (27) | Mann-Whitney | 0.067 |
| frac_alt | 0.029 (13) | 0.043 (27) | Mann-Whitney | 0.053 |
| reads | 18533790.0 (13) | 23077752.375 (26) | Mann-Whitney | 0.003 |
| kept_tiles | 3194.143 (13) | 969.8 (27) | Mann-Whitney | <0.001 |
| tissue_frac | 0.125 (13) | 0.136 (27) | Mann-Whitney | 0.04 |
| endpoint_type | {'FN': {'HGD': 2, 'IMC/cancer': 5, 'second LGD': 6}, 'TP': {'HGD': 16, 'IMC/cancer': 3, 'second LGD': 8}} |  | Fisher (2×2 only) | None |
| scanner | {'FN': {'C13210': 1, 'C13239-01': 12}, 'TP': {'C13210': 11, 'C13239-01': 16}} |  | Fisher (2×2 only) | 0.063 |
| p53 | {'FN': {'aberrant': 2, 'missing': 2, 'normal': 9}, 'TP': {'aberrant': 13, 'missing': 0, 'normal': 14}} |  | Fisher (2×2 only) | None |

**Sources.** `results/paper_final/final_checks.json` · `scripts/paper_plan/pk_main.py` · commit 50bd222 (`K2`). **Caveats.** Reads exist only for discovery-sheet profiles; small FN groups.

### K3. Latent space within discovery
**Question.** How much of the pooled probe performance was stratum?

**Status.** DONE. **Pre-specification.** `e6e00c0` §K3.

| representation | probe AUROC pooled (item 6) | probe AUROC discovery [CI] | kNN-10 discovery [CI] | Δ probe vs image (discovery) | Δ probe vs CNV (discovery) |
|---|---|---|---|---|---|
| image_only | 0.784 | 0.783 [0.676, 0.881] | 0.792 [0.681, 0.884] | — | — |
| cnv_only | 0.713 | 0.680 [0.557, 0.790] | 0.672 [0.554, 0.781] | — | — |
| early_fusion | 0.822 | 0.799 [0.687, 0.890] | 0.783 [0.668, 0.881] | 0.015 [-0.101, +0.121] | 0.118 [-0.012, +0.257] |
| intermediate_fusion | 0.819 | 0.807 [0.704, 0.897] | 0.793 [0.689, 0.885] | 0.024 [-0.066, +0.118] | 0.127 [-0.016, +0.274] |
| coattention_fusion | 0.736 | 0.719 [0.595, 0.833] | 0.794 [0.688, 0.889] | -0.064 [-0.193, +0.055] | 0.039 [-0.122, +0.198] |

n 82 discovery patients, 40 events. **Sources.** `results/paper_final/final_checks.json` · `scripts/paper_plan/pk_main.py` · commit 50bd222 (`K3`). **Caveats.** Probes fitted on all training-fold patients, evaluated on discovery held-out patients.

### K4. CNV use and rank shift within discovery
**Status.** DONE. **Pre-specification.** `e6e00c0` §K4.

| model | population | n / events | CNV permuted jointly Δ [CI] | CNV → training mean Δ [CI] | image bags permuted Δ [CI] | image → mean tile Δ [CI] | baseline AUROC |
|---|---|---|---|---|---|---|---|
| early_fusion | all_150 | 150 / 50 | +0.050 [-0.009, +0.111] | +0.064 [0.007, 0.123] | +0.114 [0.038, 0.191] | +0.082 [0.016, 0.154] | 0.738 |
| early_fusion | discovery_82 | 82 / 40 | +0.068 [-0.020, +0.151] | +0.091 [0.013, 0.170] | +0.139 [0.047, 0.234] | +0.085 [0.007, 0.173] | 0.704 |
| intermediate_fusion | all_150 | 150 / 50 | +0.023 [-0.030, +0.072] | +0.038 [-0.016, +0.096] | +0.167 [0.060, 0.271] | +0.125 [0.021, 0.231] | 0.741 |
| intermediate_fusion | discovery_82 | 82 / 40 | +0.059 [-0.020, +0.134] | +0.061 [-0.024, +0.140] | +0.177 [0.046, 0.315] | +0.157 [0.011, 0.299] | 0.684 |
| coattention_fusion | all_150 | 150 / 50 | +0.016 [-0.033, +0.067] | +0.025 [-0.029, +0.078] | +0.168 [0.092, 0.252] | +0.170 [0.094, 0.249] | 0.739 |
| coattention_fusion | discovery_82 | 82 / 40 | +0.045 [-0.040, +0.121] | +0.052 [-0.033, +0.129] | +0.146 [0.043, 0.256] | +0.174 [0.058, 0.292] | 0.625 |

8a within discovery (n 82, events 40): Spearman(CNV, late fusion) 0.260; progressors up > 20 points 12, down 9; non-progressors up 10, down 15; categorical NRI 0.312 [-0.016, 0.626].

**Sources.** `results/paper_final/k4_ablation.json` · `scripts/paper_plan/pk_gpu.py` · commit 50bd222; `results/paper_final/final_checks.json` · `scripts/paper_plan/pk_main.py` · commit 50bd222 (`K4`). **Caveats.** Ablated score per row = mean over 50 permutations; deltas on 82 patients have wide CIs.

### K5. Risk groups within discovery
**Status.** DONE. **Pre-specification.** `e6e00c0` §K5.

| endpoint | arm | low n / events / rate [Wilson] | moderate | high | OR high vs low [CI] | Cochran–Armitage z, p |
|---|---|---|---|---|---|---|
| LGD2plus | Clinical (C2) | 19 / 7 / 0.368 [0.191, 0.590] | 19 / 7 / 0.368 [0.191, 0.590] | 44 / 26 / 0.591 [0.444, 0.723] | 2.387 [0.809, 7.049] | [1.829, 0.067] |
| LGD2plus | CNV (release RF) | 12 / 7 / 0.583 [0.320, 0.807] | 31 / 13 / 0.419 [0.264, 0.592] | 39 / 20 / 0.513 [0.362, 0.661] | 0.771 [0.218, 2.726] | [-0.053, 0.958] |
| LGD2plus | WSI | 24 / 8 / 0.333 [0.180, 0.533] | 24 / 11 / 0.458 [0.279, 0.649] | 34 / 21 / 0.618 [0.450, 0.761] | 3.092 [1.059, 9.026] | [2.156, 0.031] |
| LGD2plus | Late fusion (mean) | 21 / 7 / 0.333 [0.172, 0.546] | 26 / 10 / 0.385 [0.224, 0.575] | 35 / 23 / 0.657 [0.492, 0.792] | 3.635 [1.189, 11.108] | [2.506, 0.012] |
| E_HGD | Clinical (C2) | 19 / 7 / 0.368 [0.191, 0.590] | 19 / 7 / 0.368 [0.191, 0.590] | 44 / 12 / 0.273 [0.163, 0.418] | 0.641 [0.210, 1.956] | [-0.845, 0.398] |
| E_HGD | CNV (release RF) | 12 / 4 / 0.333 [0.138, 0.609] | 31 / 7 / 0.226 [0.114, 0.398] | 39 / 15 / 0.385 [0.249, 0.541] | 1.195 [0.323, 4.419] | [0.808, 0.419] |
| E_HGD | WSI | 24 / 5 / 0.208 [0.092, 0.405] | 24 / 5 / 0.208 [0.092, 0.405] | 34 / 16 / 0.471 [0.315, 0.633] | 3.162 [0.995, 10.045] | [2.233, 0.026] |
| E_HGD | Late fusion (mean) | 21 / 3 / 0.143 [0.050, 0.346] | 26 / 7 / 0.269 [0.137, 0.461] | 35 / 16 / 0.457 [0.305, 0.618] | 4.473 [1.198, 16.696] | [2.513, 0.012] |

**Sources.** `results/paper_final/final_checks.json` · `scripts/paper_plan/pk_main.py` · commit 50bd222 (`K5`). **Caveats.** Tertile cut-points from all training-fold patients per fold, then restricted to discovery; tertiles are therefore unequal in size within discovery.

## 4. Figures

### F-intro. Forest plot: WSI vs CNV arms by population and endpoint
**File.** `results/paper_final/figs/F_intro_forest.png`, `.pdf`; numbers in `results/paper_final/figs/F_intro_forest.json`.

Left: AUROC [CI] for WSI, CNV (release RF), CNV (Killcoyne method) for discovery / stratified / pooled × LGD2+ / E-HGD (post hoc). Right: WSI − CNV difference [CI] for both CNV arms; dashed line = pre-specified non-inferiority margin −0.05.

| population | endpoint | n / events | WSI | CNV (RF) | CNV (KM) | WSI − CNV(RF) | WSI − CNV(KM) |
|---|---|---|---|---|---|---|---|
| discovery | LGD2plus | 82 / 40 | 0.649 [0.527, 0.765] | 0.564 [0.427, 0.693] | 0.580 [0.443, 0.714] | 0.086 [-0.084, +0.266] | 0.069 [-0.097, +0.245] |
| stratified | LGD2plus | 150 / 50 | 0.708 [0.612, 0.796] | 0.594 [0.488, 0.695] | 0.597 [0.486, 0.703] | 0.114 [-0.029, +0.253] | 0.111 [-0.025, +0.252] |
| pooled | LGD2plus | 150 / 50 | 0.731 [0.640, 0.814] | 0.663 [0.569, 0.754] | 0.640 [0.538, 0.734] | 0.068 [-0.065, +0.196] | 0.091 [-0.031, +0.215] |
| discovery | E_HGD | 82 / 26 | 0.658 [0.527, 0.782] | 0.639 [0.491, 0.779] | 0.698 [0.556, 0.830] | 0.019 [-0.151, +0.203] | -0.041 [-0.211, +0.144] |
| stratified | E_HGD | 150 / 36 | 0.721 [0.616, 0.816] | 0.651 [0.532, 0.771] | 0.684 [0.567, 0.794] | 0.070 [-0.082, +0.219] | 0.037 [-0.110, +0.180] |
| pooled | E_HGD | 150 / 36 | 0.746 [0.650, 0.837] | 0.676 [0.561, 0.774] | 0.694 [0.580, 0.789] | 0.070 [-0.066, +0.212] | 0.053 [-0.080, +0.193] |

### F-table. Forest plots of all whiteboard arms
**File.** `results/paper_final/figs/F_table_forest.png`, `.pdf`; numbers in `results/paper_final/figs/F_table_forest.json`.

A: discovery LGD2+ (n 82, events 40). B: discovery E-HGD post hoc (events 26). C: pooled (confounded) vs stratified vs discovery, LGD2+. Grey rows = supplementary arms.

| arm | A discovery LGD2+ | B discovery E-HGD | C pooled LGD2+ | C stratified LGD2+ | C discovery LGD2+ |
|---|---|---|---|---|---|
| Clinical (C2) | 0.625 [0.498, 0.744] | 0.412 [0.277, 0.545] | 0.681 [0.582, 0.776] | 0.601 [0.492, 0.704] | 0.625 [0.498, 0.744] |
| CNV (release RF) | 0.564 [0.427, 0.693] | 0.639 [0.491, 0.779] | 0.663 [0.569, 0.754] | 0.594 [0.488, 0.695] | 0.564 [0.427, 0.693] |
| CNV (Killcoyne method) | 0.580 [0.443, 0.714] | 0.698 [0.556, 0.830] | 0.640 [0.538, 0.734] | 0.597 [0.486, 0.703] | 0.580 [0.443, 0.714] |
| WSI | 0.649 [0.527, 0.765] | 0.658 [0.527, 0.782] | 0.731 [0.640, 0.814] | 0.708 [0.612, 0.796] | 0.649 [0.527, 0.765] |
| Early fusion | 0.704 [0.579, 0.812] | 0.751 [0.618, 0.866] | 0.738 [0.646, 0.818] | 0.735 [0.642, 0.820] | 0.704 [0.579, 0.812] |
| Intermediate fusion | 0.684 [0.567, 0.798] | 0.687 [0.560, 0.806] | 0.741 [0.653, 0.818] | 0.717 [0.619, 0.806] | 0.684 [0.567, 0.798] |
| Late fusion (mean) | 0.691 [0.569, 0.803] | 0.701 [0.573, 0.821] | 0.774 [0.687, 0.849] | 0.745 [0.652, 0.829] | 0.691 [0.569, 0.803] |
| Co-attention (suppl.) | 0.625 [0.505, 0.743] | 0.683 [0.557, 0.806] | 0.739 [0.652, 0.821] | 0.695 [0.596, 0.792] | 0.625 [0.505, 0.743] |
| Late stack (suppl.) | 0.647 [0.524, 0.763] | 0.664 [0.536, 0.789] | 0.737 [0.648, 0.814] | 0.701 [0.602, 0.791] | 0.647 [0.524, 0.763] |

### F-D1. Risk groups
**File.** `results/paper_final/figs/F_D1_risk_groups.png`, `.pdf`; numbers in `results/paper_final/figs/F_D1_risk_groups.json`.

Left: progression rate per training-fold tertile with Wilson CIs (discovery, LGD2+); counts events/n printed on bars. Right: Mantel–Haenszel OR high vs low across the two strata (all 150), from round 3.

| arm | low | moderate | high | MH OR two strata [CI] |
|---|---|---|---|---|
| Clinical (C2) | 7/19 = 0.368 [0.191, 0.590] | 7/19 = 0.368 [0.191, 0.590] | 26/44 = 0.591 [0.444, 0.723] | 2.663 [1.004, 7.067] |
| CNV (release RF) | 7/12 = 0.583 [0.320, 0.807] | 13/31 = 0.419 [0.264, 0.592] | 20/39 = 0.513 [0.362, 0.661] | 1.31 [0.468, 3.664] |
| WSI | 8/24 = 0.333 [0.180, 0.533] | 11/24 = 0.458 [0.279, 0.649] | 21/34 = 0.618 [0.450, 0.761] | 5.66 [2.120, 15.110] |
| Late fusion (mean) | 7/21 = 0.333 [0.172, 0.546] | 10/26 = 0.385 [0.224, 0.575] | 23/35 = 0.657 [0.492, 0.792] | 7.167 [2.587, 19.850] |

### F-D2. Latent space
**File.** `results/paper_final/figs/F_D2_latent.png`, `.pdf`; numbers in `results/paper_final/figs/F_D2_latent.json`.

A: linear-probe AUROC per representation, pooled (item 6) vs discovery-only evaluation (K3). B: UMAP of image-only and intermediate-fusion held-out patient embeddings, five folds (projection fitted on each fold's training patients), coloured by stratum. C (insets): the same projections, discovery patients only, coloured by label. Held-out counts per panel: {'image_only_fold1': {'n': 30, 'discovery': 21, 'events_discovery': 9}, 'image_only_fold2': {'n': 30, 'discovery': 18, 'events_discovery': 8}, 'image_only_fold3': {'n': 30, 'discovery': 16, 'events_discovery': 9}, 'image_only_fold4': {'n': 30, 'discovery': 16, 'events_discovery': 9}, 'image_only_fold5': {'n': 30, 'discovery': 11, 'events_discovery': 5}, 'intermediate_fusion_fold1': {'n': 30, 'discovery': 21, 'events_discovery': 9}, 'intermediate_fusion_fold2': {'n': 30, 'discovery': 18, 'events_discovery': 8}, 'intermediate_fusion_fold3': {'n': 30, 'discovery': 16, 'events_discovery': 9}, 'intermediate_fusion_fold4': {'n': 30, 'discovery': 16, 'events_discovery': 9}, 'intermediate_fusion_fold5': {'n': 30, 'discovery': 11, 'events_discovery': 5}}.

| representation | pooled probe [CI] | discovery probe [CI] |
|---|---|---|
| image_only | 0.784 [0.699, 0.862] | 0.783 [0.676, 0.881] |
| cnv_only | 0.713 [0.617, 0.797] | 0.680 [0.557, 0.790] |
| early_fusion | 0.822 [0.741, 0.893] | 0.799 [0.687, 0.890] |
| intermediate_fusion | 0.819 [0.743, 0.888] | 0.807 [0.704, 0.897] |
| coattention_fusion | 0.736 [0.640, 0.827] | 0.719 [0.595, 0.833] |

### F-D3. Attention
**File.** `results/paper_final/figs/F_D3_attention.png`, `.pdf`; numbers in `results/paper_final/figs/F_D3_attention.json`.

A: per-slide Spearman correlation of tile attention, image-only vs intermediate and vs co-attention (707 held-out rows each). B: attention mass on the top 5 % of tiles per model, uniform = 0.05. Tile montages (tissue) stay on the cluster: feasibility/paper_plan/figs/attention/M01-M20.png; manifest feasibility/paper_plan/montage_manifest_SECRET.csv.

| quantity | model | n rows | median [IQR] |
|---|---|---|---|
| Spearman vs image-only | intermediate_fusion | 707 | 0.867 [0.722, 0.934] |
| Spearman vs image-only | coattention_fusion | 707 | 0.347 [-0.048, 0.629] |
| top-5 % mass | image_only | 707 | 0.158 [0.11, 0.213] |
| top-5 % mass | intermediate_fusion | 707 | 0.173 [0.127, 0.237] |
| top-5 % mass | coattention_fusion | 707 | 0.085 [0.064, 0.128] |

### F-D4. Does CNV prediction change?
**File.** `results/paper_final/figs/F_D4_cnv_change.png`, `.pdf`; numbers in `results/paper_final/figs/F_D4_cnv_change.json`.

A: CNV-only vs late-fusion patient percentile within discovery (n 82, events 40), coloured by label, with the diagonal; Spearman 0.26. B: ΔAUROC when CNV or image input is destroyed (jointly permuted, mean of 50), per learned fusion model, discovery and pooled (K4).

Panel B numbers: see the K4 table above (`k4_ablation.json`).

### F-D5. False positives
**File.** `results/paper_final/figs/F_D5_false_positives.png`, `.pdf`; numbers in `results/paper_final/figs/F_D5_false_positives.json`.

Later-HGD+ rate for FP vs TN, per stratum, with Wilson CIs and counts on bars, for late fusion, WSI, CNV (RF), C2 (pooled operating point).

| model | stratum | FP later HGD+ / FP | TN later HGD+ / TN | Fisher p |
|---|---|---|---|---|
| Late fusion (mean) | discovery | 3 / 22 | 3 / 20 | 1.0 |
| Late fusion (mean) | validation | 8 / 18 | 1 / 40 | <0.001 |
| WSI | discovery | 3 / 25 | 3 / 17 | 0.672 |
| WSI | validation | 8 / 25 | 1 / 33 | 0.004 |
| CNV (release RF) | discovery | 6 / 35 | 0 / 7 | 0.567 |
| CNV (release RF) | validation | 7 / 20 | 2 / 38 | 0.006 |
| Clinical (C2) | discovery | 4 / 30 | 2 / 12 | 1.0 |
| Clinical (C2) | validation | 6 / 26 | 3 / 32 | 0.274 |

### F-D6. False negatives
**File.** `results/paper_final/figs/F_D6_false_negatives.png`, `.pdf`; numbers in `results/paper_final/figs/F_D6_false_negatives.json`.

Discovery progressors only; late-fusion FN (n 11) vs TP (n 29): boxplots of kept tiles, cx, interval first row → endpoint, max grade so far; bar panel of endpoint type.

| variable | FN median (n) | TP median (n) | Mann-Whitney p |
|---|---|---|---|
| kept_tiles | 3194.143 (11) | 991.0 (29) | 0.002 |
| cx | 24.0 (11) | 55.0 (29) | 0.041 |
| first_to_event | 898.0 (11) | 1096.0 (29) | 0.348 |
| max_sofar | 2.0 (11) | 2.0 (29) | 0.773 |

Endpoint type (FN / TP): {'FN': {'second LGD': 6, 'HGD': 2, 'IMC/cancer': 3}, 'TP': {'second LGD': 8, 'HGD': 16, 'IMC/cancer': 5}}

## 5. Discrepancies found
1. The pooled late-fusion FP excess of later HGD+ (OR 5.4 in F5/R5) is confined to the validation stratum: discovery FP 3/22 vs TN 3/20, validation 8/18 vs 1/40 (K1).
2. Probe AUROCs fall from pooled to discovery-only: image 0.784 → 0.783, early 0.822 → 0.799, intermediate 0.819 → 0.807 (K3).
3. Within discovery the FN vs TP tile-count difference (pooled p 0.002) becomes p 0.002 (K2).

## 6. Not done
- ACE-B (no data). Tissue montages and review pack not committed (patient tissue).

## 7. Pre-specification text as committed at `e6e00c0` (verbatim)

> # BE paper: final checks and figures (K1–K5, F-intro, F-table, F-D1–F-D6)
>
> **Status of this file: PRE-SPECIFICATION VERSION**, committed before any analysis or figure was produced. Results and
> figure descriptions are appended in a later commit; this text is not edited afterwards.
>
> ## 1. Header (completed at the results commit)
> - Date: 26 September 2026. Commit at start: `4e0cc2d`. Pre-specification commit: the commit adding this text. Frozen release only; nothing retrained.
> - Inputs: patient-level scores, labels, E-HGD labels, strata and tile counts from round 3 (`feasibility/paper_plan/round3_patient_table.csv`, commit `6976646`), operating-point predictions (`followup_patient_scores.csv`, `patient_scores_predictions.csv`), later-disease table, closeout patient/QC/slide tables, image and fusion embeddings and attention arrays from `pp_latent.py` (`feasibility/paper_plan/latent/`), results JSONs of rounds 1–3 for pooled/stratified numbers (`results/paper_plan/round3_main.json`, `discovery_main.json`, `f1_cnv_killcoyne.json`, `followup_main.json`, `main_items.json`).
> - Scripts: `scripts/paper_plan/pk_gpu.py` (K4 ablation, row-level scores), `pk_main.py` (K1–K5, all figures), `pk_render.py`, `pk_check_report.py`. Outputs: `results/paper_final/final_checks.json`, `results/paper_final/k4_ablation.json`, figures `results/paper_final/figs/<name>.png|.pdf` with `<name>.json` (plotted numbers, n / events per panel).
>
> ## Analysis decisions (fixed)
> Primary population = 82 discovery-stratum patients (40 LGD2+ events, 26 HGD/IMC events). Secondary = stratified all-150 (pair-weighted within-stratum AUROC, weights 1,680 / 580), then pooled all-150 labelled confounded. Primary endpoint LGD2+; secondary E-HGD, labelled "added after seeing the CNV results". Tissue amount reported as an unresolved confound, not adjusted for in primary results. Arms: Clinical = C2; CNV = release RF (Killcoyne-method arm as sensitivity comparator); WSI; early, intermediate, late (mean) fusion; co-attention and late-stack in supplementary tables only; ERIN grade head excluded from all figures. Conventions as before: patient = max over rows; rank AUROC; 2,000 patient bootstraps `RandomState(0)`; permutations 2,000; fold-honest quantities from the release folds. Figures PNG + PDF 300 dpi; no tissue images committed.
>
> ## Pre-specifications
>
> ### K1. False positives by stratum
> - Per model (late_mean, image_only, cnv_only, C2) at the pooled operating point already applied (follow-up predictions): FP/TN and later-HGD+ counts per stratum (discovery, validation). Within validation non-progressors: Fisher p; logistic regression later HGD+ ~ FP + baseline grade + log `kept_tiles` (statsmodels; Fisher only if the fit separates or fails). Spearman of `kept_tiles` with later HGD+ among validation non-progressors. Discovery non-progressors: follow-up after last release row (DB follow-up days; median, IQR, share with any later DB report) and the number who are Killcoyne sheet controls (NP) vs sheet cases labelled non-progressors by us.
>
> ### K2. False negatives within discovery
> - Item-10 comparison repeated for late_mean and image_only using the 40 discovery progressors only: FN vs TP on interval to endpoint, endpoint type, rows, baseline and max grade, cx, MAPD noise, segments, fraction altered, reads, `kept_tiles`, tissue fraction, scanner, p53 IHC; Mann-Whitney / Fisher (2×2 only).
>
> ### K3. Latent space within discovery
> - Same probe and kNN procedure as item 6 (fitted on all training-fold patients, standardisation and C on training patients), evaluated on discovery held-out patients only; AUROC with bootstrap over the 82; paired fused − unimodal (image, CNV) differences with CI.
>
> ### K4. CNV use and rank shift within discovery
> - `pk_gpu.py`: for each learned fusion model and fold, held-out row scores: baseline; CNV permuted jointly across held-out rows (50 repeats, `RandomState(0)`, mean permuted score per row kept); CNV replaced by the training mean (standardised zeros); image bags permuted (50 repeats); image replaced by training-mean tile. Row-level scores saved; ΔAUROC = baseline − ablated on (a) all 150, (b) discovery 82, CI from patient bootstrap of the paired patient scores (max over rows).
> - 8a within discovery: Spearman of cnv_only vs late_mean patient scores; percentile-rank change within discovery; counts moving > 20 points by label; categorical NRI (training-fold tertile groups computed on all patients, restricted to discovery) with bootstrap CI.
>
> ### K5. Risk groups within discovery
> - Training-fold tertiles (as round 3) restricted to discovery; per arm (C2, cnv_only, image_only, late_mean) and endpoint (LGD2+, E-HGD): n, events, rate with Wilson CI per tertile; OR high vs low (Haldane) with Woolf CI; Cochran–Armitage trend test (scores 0/1/2; chi-square with 1 df, no continuity correction).
>
> ### Figures
> - F-intro: forest plot, one row per population × endpoint (discovery, stratified, pooled × LGD2+, E-HGD) with AUROC [CI] for WSI, CNV (RF), CNV (Killcoyne); second panel WSI − CNV difference [CI] for both CNV arms with a dashed line at −0.05. Numbers from `discovery_main.json`, `round3_main.json` (pooled/stratified via R1/R2; stratified E-HGD from R2), stratified differences via bootstrap recomputed in `pk_main.py` where not already stored.
> - F-table: forest plots of all whiteboard arms (C2, CNV RF, CNV KM, WSI, early, intermediate, late; supplementary rows co-attention, late-stack shown greyed): A discovery LGD2+; B discovery E-HGD; C pooled vs stratified vs discovery on LGD2+ side by side. Markdown table rendered alongside.
> - F-D1: grouped bars of tertile progression rates with Wilson CIs (C2, CNV RF, WSI, late fusion; discovery, LGD2+); second panel MH OR high vs low per arm (two strata, from `round3_main.json` R4).
> - F-D2: A probe AUROC per representation, pooled (item 6) vs discovery-only (K3); B UMAP (fit on each fold's training patients, held-out shown, five folds as small multiples) of image-only and intermediate embeddings coloured by stratum; C same UMAP coloured by label, discovery patients only.
> - F-D3: A histograms of per-row Spearman (image-only vs intermediate; vs co-attention) from `attention_item7_rows.csv`; B top-5 % attention mass per model (from the attention arrays), uniform line at 0.05. Montage paths listed (cluster).
> - F-D4: A scatter of cnv_only vs late_mean patient percentile within discovery, coloured by label, diagonal; B ΔAUROC bars (CNV destroyed vs image destroyed) per learned fusion model, discovery and pooled (K4).
> - F-D5: later-HGD+ rate FP vs TN per stratum for late_mean, WSI, CNV (RF), C2, Wilson CIs, counts on bars (K1).
> - F-D6: discovery-only boxplots FN vs TP (late fusion) for `kept_tiles`, cx, interval to endpoint, max grade so far; bar panel of endpoint type (second LGD / HGD / IMC) for FN and TP.
>
> (Results follow in the results commit.)
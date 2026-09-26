# BE paper plan, round 3: confounding checks before writing (R1–R6)

## 1. Header
- Date: 26 September 2026. Commit at start: `e7ee492`. Pre-specification commit: `cf244e1` (verbatim in §5). Results commit: `6976646`; this text is the next commit. Frozen release only.
- Scripts (`scripts/paper_plan/`): `pr3_main.py`, `pr3_lopo.py`, `pr3_extra.py` (post hoc, labelled), `pr3_render.py`, `pr3_check_report.py`. Results: `results/paper_plan/round3_main.json`, `round3_lopo.json`, `round3_extra.json`, figures `results/paper_plan/figs/km_v3/`; cluster-only rows `feasibility/paper_plan/round3_patient_table.csv`.
- Strata: discovery = 82 Killcoyne 777-sheet patients (40 progressors), validation = 68 268-sheet patients (10 progressors); stratified AUROC = pair-weighted within-stratum AUROC (weights {'discovery': 1680, 'validation': 580}); stratified bootstrap resamples patients within stratum.

## 2. Status table
| item | status | key number |
|---|---|---|
| R1 Stratum as a shortcut | DONE | stratum from inputs (non-progressors): CNV features 0.891 [0.819, 0.951], image embedding 0.948 [0.887, 0.993], CNV QC 1.000; stratified AUROC late fusion 0.745 [0.652, 0.829] vs pooled 0.774 |
| R2 Endpoint sensitivity | DONE | E-HGD (36 events): late fusion pooled 0.782, CNV(RF) 0.676, WSI 0.746; LOPO retrain on sheet labels vs published: Spearman 0.414 |
| R3 Tissue amount | DONE | kept_tiles alone AUROC 0.766 [0.688, 0.837] pooled, 0.551 / 0.930 by stratum; stratum + tiles alone (fold-honest) 0.737 |
| R4 Risk groups (valid version) | DONE | validation stratum (68 / 10): late fusion log-rank p 0.344, Cox feasible False; pooled MH OR high vs low 7.167 [2.587, 19.850] |
| R5 FP: stratum and follow-up | DONE | late fusion later-HGD+ OR adjusted for stratum and follow-up 5.353 [1.392, 20.584]; 1 patient reclassified |
| R6 Headline table | DONE | §R6 |

## 3. Items

### R1. Stratum as a shortcut
**Question.** Can the inputs predict the design stratum without the label, and how much of each arm survives within-stratum comparison?

**Status.** DONE. **Pre-specification.** `cf244e1` §R1.

**Probes of stratum (discovery vs validation) among the 100 non-progressors** (fold-honest, release folds):

| input | n non-progressors (discovery / validation) | AUROC [CI] |
|---|---|---|
| cnv_features_pca20 | 100 (42 / 58) | 0.891 [0.819, 0.951] |
| cnv_arms_cx_no_pca | 100 (42 / 58) | 0.886 [0.813, 0.949] |
| cnv_qc | 100 (42 / 58) | 1.000 [1.000, 1.000] |
| image_patient_embedding_256d | 100 (42 / 58) | 0.948 [0.887, 0.993] |

**Stratified AUROC, all arms** (n 82 / 40 discovery, 68 / 10 validation; stratum alone in-sample AUROC 0.690):

| arm | pooled [CI] | stratified [CI] | within discovery | within validation |
|---|---|---|---|---|
| Clinical C1 | 0.688 [0.588, 0.785] | 0.591 [0.482, 0.699] | 0.615 | 0.521 |
| Clinical C2 (primary) | 0.681 [0.582, 0.776] | 0.601 [0.492, 0.704] | 0.625 | 0.531 |
| Clinical C3 | 0.666 [0.571, 0.758] | 0.582 [0.478, 0.688] | 0.591 | 0.553 |
| Clinical C4 (=3a) | 0.765 [0.684, 0.844] | 0.739 [0.648, 0.824] | 0.720 | 0.795 |
| CNV (release RF) | 0.663 [0.569, 0.754] | 0.594 [0.488, 0.695] | 0.564 | 0.683 |
| CNV (Killcoyne method) | 0.640 [0.538, 0.734] | 0.597 [0.486, 0.703] | 0.580 | 0.647 |
| WSI | 0.731 [0.640, 0.814] | 0.708 [0.612, 0.796] | 0.649 | 0.879 |
| Early fusion | 0.738 [0.646, 0.818] | 0.735 [0.642, 0.820] | 0.704 | 0.828 |
| Intermediate fusion | 0.741 [0.653, 0.818] | 0.717 [0.619, 0.806] | 0.684 | 0.814 |
| Late fusion (image + RF CNV) | 0.774 [0.687, 0.849] | 0.745 [0.652, 0.829] | 0.691 | 0.900 |
| Late fusion (image + KM CNV) | 0.764 [0.672, 0.843] | 0.730 [0.630, 0.819] | 0.676 | 0.888 |
| Co-attention (extra) | 0.739 [0.652, 0.821] | 0.695 [0.596, 0.792] | 0.625 | 0.897 |
| Late stack (extra) | 0.737 [0.648, 0.814] | 0.701 [0.602, 0.791] | 0.647 | 0.857 |
| C2 + WSI | 0.802 [0.727, 0.873] | 0.756 [0.663, 0.838] | 0.704 | 0.905 |
| C2 + CNV(RF) | 0.784 [0.707, 0.857] | 0.715 [0.619, 0.805] | 0.698 | 0.764 |
| C2 + CNV(KM) | 0.796 [0.713, 0.871] | 0.748 [0.647, 0.836] | 0.735 | 0.786 |
| C2 + late fusion | 0.824 [0.755, 0.888] | 0.778 [0.689, 0.856] | 0.729 | 0.922 |
| C2 + WSI + CNV(RF) | 0.843 [0.778, 0.901] | 0.791 [0.703, 0.867] | 0.749 | 0.914 |

**Paired differences** (stratified vs pooled):

| difference | stratified Δ [CI] | pooled Δ [CI] |
|---|---|---|
| image_only − cnv_only | +0.114 [-0.029, +0.253] | +0.068 [-0.065, +0.196] |
| image_only − cnv_km | +0.111 [-0.025, +0.252] | +0.091 [-0.031, +0.215] |
| late_mean − image_only | +0.036 [0.006, 0.070] | +0.043 [0.014, 0.071] |
| late_mean_km − image_only | +0.022 [-0.031, +0.069] | +0.033 [-0.009, +0.072] |
| late_mean − cnv_only | +0.150 [0.029, 0.275] | +0.111 [-0.001, +0.222] |
| C2+image − C2_grade_maxsofar | +0.155 [0.068, 0.240] | +0.120 [0.050, 0.196] |
| C2+cnv_only − C2_grade_maxsofar | +0.114 [0.021, 0.207] | +0.103 [0.027, 0.179] |
| C2+cnv_km − C2_grade_maxsofar | +0.147 [0.054, 0.246] | +0.114 [0.034, 0.193] |
| C2+late_mean − C2_grade_maxsofar | +0.177 [0.089, 0.265] | +0.143 [0.072, 0.216] |
| C2+image+cnv_only − C2_grade_maxsofar | +0.190 [0.094, 0.288] | +0.161 [0.086, 0.243] |

**Stratum-adjusted incremental value** (label ~ stratum, then + arm logit):

| arm | LR stat (1 df) | LR p | AUROC stratum alone → + arm (in-sample) | ΔAUROC fold-honest [CI] |
|---|---|---|---|---|
| Clinical C1 | 5.432 | 0.02 | 0.690 → 0.731 | +0.076 [0.014, 0.142] |
| Clinical C2 (primary) | 4.347 | 0.037 | 0.690 → 0.735 | +0.057 [-0.003, +0.119] |
| Clinical C3 | 5.626 | 0.018 | 0.690 → 0.725 | +0.060 [0.003, 0.123] |
| Clinical C4 (=3a) | 9.918 | 0.002 | 0.690 → 0.785 | +0.101 [0.035, 0.168] |
| CNV (release RF) | 2.181 | 0.14 | 0.690 → 0.733 | +0.043 [-0.002, +0.086] |
| CNV (Killcoyne method) | 7.02 | 0.008 | 0.690 → 0.735 | +0.058 [-0.009, +0.125] |
| WSI | 17.144 | <0.001 | 0.690 → 0.789 | +0.104 [0.020, 0.182] |
| Early fusion | 20.454 | <0.001 | 0.690 → 0.796 | +0.131 [0.053, 0.206] |
| Intermediate fusion | 15.663 | <0.001 | 0.690 → 0.789 | +0.100 [0.034, 0.165] |
| Late fusion (image + RF CNV) | 23.726 | <0.001 | 0.690 → 0.811 | +0.119 [0.028, 0.206] |
| Late fusion (image + KM CNV) | 22.813 | <0.001 | 0.690 → 0.798 | +0.107 [0.021, 0.187] |
| Co-attention (extra) | 14.016 | <0.001 | 0.690 → 0.770 | +0.094 [0.020, 0.162] |
| Late stack (extra) | 14.328 | <0.001 | 0.690 → 0.779 | +0.087 [0.009, 0.161] |
| C2 + WSI | 24.414 | <0.001 | 0.690 → 0.816 | +0.146 [0.072, 0.228] |
| C2 + CNV(RF) | 15.563 | <0.001 | 0.690 → 0.782 | +0.110 [0.048, 0.177] |
| C2 + CNV(KM) | 17.743 | <0.001 | 0.690 → 0.787 | +0.114 [0.052, 0.182] |
| C2 + late fusion | 31.716 | <0.001 | 0.690 → 0.837 | +0.171 [0.094, 0.256] |
| C2 + WSI + CNV(RF) | 29.954 | <0.001 | 0.690 → 0.828 | +0.154 [0.085, 0.226] |

The pre-specified CNV-QC probe reaches 1.0 because read counts exist only for discovery-sheet profiles, so the pre-specified missing-read indicator identifies the stratum by construction. Post-hoc variant (added after seeing this, `pr3_extra.py`, not pre-specified): QC probe without read count or indicator (noise, segments, fraction altered, cx) = 0.756 [0.656, 0.847]; univariate AUROCs (raw direction) {'noise_mapd': 0.278, 'n_segments': 0.244, 'frac_altered_0p15': 0.298, 'cx': 0.604}.

**Method.** `pr3_main.py` R1; post-hoc variant `pr3_extra.py`. **Sources.** `results/paper_plan/round3_main.json` · `scripts/paper_plan/pr3_main.py` · commit 6976646 (`R1`); `results/paper_plan/round3_extra.json` · `scripts/paper_plan/pr3_extra.py` · commit 6976646. **Caveats.** The image-embedding probe uses fold-k model embeddings for fold-k patients (held-out) and for training patients (in-sample for the image model); the CNV probe uses PCA-20 on 632 features; probes are among non-progressors only (100 patients).

### R2. Endpoint sensitivity (HGD/IMC vs LGD2+)
**Question.** Do the arms predict HGD/IMC progression rather than second-LGD events, and is the F1 arm a faithful reimplementation?

**Status.** DONE. **Pre-specification.** `cf244e1` §R2.

Progressor types: HGD/IMC 36, second-LGD only 14; by stratum {'discovery': {'HGD_IMC': 26, 'second_LGD_only': 14}, 'validation': {'HGD_IMC': 10, 'second_LGD_only': 0}}. Second-LGD-only progressors' median percentile among all patients: {'cnv_only': {'median_percentile_among_all_patients': 56.0}, 'cnv_km': {'median_percentile_among_all_patients': 40.333}, 'image_only': {'median_percentile_among_all_patients': 57.0}, 'late_mean': {'median_percentile_among_all_patients': 61.333}, 'C2_grade_maxsofar': {'median_percentile_among_all_patients': 87.667}}.

**E-HGD** (n 150, events 36; second-LGD progressors counted as non-events) and **E-HGD-excl** (n 136, events 36):

| arm | E-HGD pooled [CI] | E-HGD stratified [CI] | E-HGD discovery / validation | E-HGD-excl pooled [CI] | E-HGD-excl stratified [CI] |
|---|---|---|---|---|---|
| Clinical C1 | 0.542 [0.432, 0.656] | 0.441 [0.328, 0.552] | 0.410 / 0.521 | 0.597 [0.483, 0.710] | 0.504 [0.386, 0.624] |
| Clinical C2 (primary) | 0.529 [0.424, 0.640] | 0.446 [0.327, 0.553] | 0.412 / 0.531 | 0.588 [0.479, 0.696] | 0.513 [0.392, 0.630] |
| Clinical C3 | 0.510 [0.404, 0.619] | 0.422 [0.311, 0.533] | 0.370 / 0.553 | 0.566 [0.453, 0.677] | 0.487 [0.366, 0.606] |
| Clinical C4 (=3a) | 0.690 [0.591, 0.786] | 0.667 [0.561, 0.764] | 0.617 / 0.795 | 0.738 [0.636, 0.827] | 0.726 [0.626, 0.817] |
| CNV (release RF) | 0.676 [0.561, 0.774] | 0.651 [0.532, 0.771] | 0.639 / 0.683 | 0.684 [0.569, 0.794] | 0.646 [0.523, 0.760] |
| CNV (Killcoyne method) | 0.694 [0.580, 0.789] | 0.684 [0.567, 0.794] | 0.698 / 0.647 | 0.697 [0.579, 0.801] | 0.676 [0.561, 0.792] |
| WSI | 0.746 [0.650, 0.837] | 0.721 [0.616, 0.816] | 0.658 / 0.879 | 0.765 [0.668, 0.852] | 0.751 [0.647, 0.837] |
| Early fusion | 0.782 [0.680, 0.868] | 0.773 [0.673, 0.860] | 0.751 / 0.828 | 0.789 [0.694, 0.869] | 0.786 [0.691, 0.869] |
| Intermediate fusion | 0.744 [0.654, 0.829] | 0.723 [0.623, 0.817] | 0.687 / 0.814 | 0.763 [0.675, 0.838] | 0.745 [0.645, 0.827] |
| Late fusion (image + RF CNV) | 0.782 [0.688, 0.865] | 0.757 [0.662, 0.850] | 0.701 / 0.900 | 0.802 [0.716, 0.881] | 0.786 [0.690, 0.868] |
| Late fusion (image + KM CNV) | 0.785 [0.695, 0.864] | 0.757 [0.657, 0.847] | 0.705 / 0.888 | 0.802 [0.712, 0.877] | 0.781 [0.685, 0.864] |
| Co-attention (extra) | 0.778 [0.689, 0.859] | 0.744 [0.649, 0.839] | 0.683 / 0.897 | 0.787 [0.699, 0.865] | 0.757 [0.655, 0.841] |
| Late stack (extra) | 0.746 [0.657, 0.828] | 0.719 [0.620, 0.813] | 0.664 / 0.857 | 0.765 [0.674, 0.841] | 0.743 [0.640, 0.827] |
| C2 + WSI | 0.678 [0.586, 0.772] | 0.616 [0.513, 0.716] | 0.501 / 0.905 | 0.750 [0.654, 0.835] | 0.709 [0.600, 0.807] |
| C2 + CNV(RF) | 0.657 [0.565, 0.753] | 0.579 [0.470, 0.683] | 0.505 / 0.764 | 0.725 [0.627, 0.811] | 0.658 [0.541, 0.760] |
| C2 + CNV(KM) | 0.692 [0.587, 0.795] | 0.651 [0.532, 0.758] | 0.598 / 0.786 | 0.745 [0.641, 0.839] | 0.711 [0.599, 0.815] |
| C2 + late fusion | 0.701 [0.612, 0.790] | 0.637 [0.538, 0.733] | 0.523 / 0.922 | 0.778 [0.691, 0.856] | 0.737 [0.632, 0.829] |
| C2 + WSI + CNV(RF) | 0.738 [0.654, 0.821] | 0.673 [0.573, 0.770] | 0.578 / 0.914 | 0.807 [0.726, 0.878] | 0.760 [0.662, 0.849] |

**Faithfulness retrain within the 82 discovery patients on the sheet labels (39 sheet P), leave-one-patient-out** (`pr3_lopo.py`): LOPO vs sheet status row AUROC 0.786, patient AUROC 0.800; published LOPO vs sheet status on the 500 matched rows: row 0.820, patient 0.873 (ours on the same rows: 0.780 / 0.800); Spearman ours vs published 0.414 (F1 arm vs published 0.243; ours vs F1 arm 0.481); ours vs our LGD2+ endpoint 0.744 (40 events), published vs our endpoint 0.718. C chosen: {'10.0': 214, '1.0': 171, '0.1': 119}.

**Method.** OOF scores re-evaluated against the alternative labels; no retraining except the LOPO faithfulness check. **Sources.** `results/paper_plan/round3_main.json` · `scripts/paper_plan/pr3_main.py` · commit 6976646 (`R2`); `results/paper_plan/round3_lopo.json` · `scripts/paper_plan/pr3_lopo.py` · commit 6976646. **Caveats.** E-HGD has 36 events; the LOPO retrain uses sheet labels for 82 patients with in-cohort C selection and is not the glmnet pipeline.

### R3. Tissue amount as a shortcut
**Question.** Does the number of tissue tiles predict the label, and do the arms track it?

**Status.** DONE. **Pre-specification.** `cf244e1` §R3.

`kept_tiles` alone (patient mean, sign from training folds): pooled AUROC 0.766 [0.688, 0.837] (raw direction more-tiles-higher 0.234); stratified 0.648; discovery 0.551 (n 82, events 40), validation 0.930 (n 68, events 10). Tissue fraction alone: 0.548 [0.451, 0.650].

Distribution: by stratum {'discovery_case': {'n': 39, 'median': 1283.6, 'iqr': [907.875, 2964.667]}, 'discovery_control': {'n': 43, 'median': 1173.0, 'iqr': [945.854, 2178.991]}, 'validation_sheet': {'n': 68, 'median': 5504.167, 'iqr': [2802.15, 6550.875]}} (discovery vs validation Mann-Whitney p <0.001); by scanner {'C13210': {'n': 20, 'median': 1095.25, 'iqr': [781.969, 2264.315]}, 'C13239-01': {'n': 130, 'median': 2873.167, 'iqr': [1074.7, 5622.75]}}; by label {'progressors_median': 1119.5, 'nonprogressors_median': 3447.115, 'mannwhitney_p': '<0.001'}.

Spearman of arm score with `kept_tiles` among non-progressors: Clinical C1 -0.504 (p <0.001); Clinical C2 (primary) -0.403 (p <0.001); Clinical C3 -0.475 (p <0.001); Clinical C4 (=3a) -0.415 (p <0.001); CNV (release RF) -0.467 (p <0.001); CNV (Killcoyne method) -0.503 (p <0.001); WSI -0.431 (p <0.001); Early fusion -0.308 (p 0.002); Intermediate fusion -0.434 (p <0.001); Late fusion (image + RF CNV) -0.487 (p <0.001); Late fusion (image + KM CNV) -0.488 (p <0.001); Co-attention (extra) -0.446 (p <0.001); Late stack (extra) -0.473 (p <0.001); C2 + WSI -0.558 (p <0.001); C2 + CNV(RF) -0.553 (p <0.001); C2 + CNV(KM) -0.644 (p <0.001); C2 + late fusion -0.598 (p <0.001); C2 + WSI + CNV(RF) -0.615 (p <0.001).

**Label ~ stratum + log tiles, then + arm** (base AUROC in-sample 0.762, fold-honest 0.737):

| arm | LR stat | LR p | ΔAUROC in-sample | ΔAUROC fold-honest [CI] |
|---|---|---|---|---|
| Clinical C1 | 4.588 | 0.032 | +0.008 | +0.009 [-0.026, +0.044] |
| Clinical C2 (primary) | 4.143 | 0.042 | +0.008 | +0.014 [-0.026, +0.054] |
| Clinical C3 | 5.449 | 0.02 | +0.011 | +0.010 [-0.028, +0.048] |
| Clinical C4 (=3a) | 5.848 | 0.016 | +0.015 | +0.013 [-0.021, +0.048] |
| CNV (release RF) | 0.673 | 0.412 | +0.004 | -0.016 [-0.041, +0.004] |
| CNV (Killcoyne method) | 4.484 | 0.034 | +0.012 | +0.002 [-0.029, +0.035] |
| WSI | 7.295 | 0.007 | +0.034 | +0.013 [-0.030, +0.057] |
| Early fusion | 11.142 | <0.001 | +0.047 | +0.027 [-0.021, +0.076] |
| Intermediate fusion | 7.403 | 0.007 | +0.032 | +0.017 [-0.020, +0.057] |
| Late fusion (image + RF CNV) | 12.347 | <0.001 | +0.052 | +0.023 [-0.030, +0.078] |
| Late fusion (image + KM CNV) | 12.466 | <0.001 | +0.040 | +0.011 [-0.041, +0.062] |
| Co-attention (extra) | 7.093 | 0.008 | +0.024 | +0.011 [-0.032, +0.055] |
| Late stack (extra) | 5.554 | 0.018 | +0.025 | +0.006 [-0.036, +0.046] |
| C2 + WSI | 16.732 | <0.001 | +0.065 | +0.059 [0.005, 0.120] |
| C2 + CNV(RF) | 10.599 | 0.001 | +0.047 | +0.037 [-0.004, +0.082] |
| C2 + CNV(KM) | 13.433 | <0.001 | +0.059 | +0.047 [-0.000, 0.098] |
| C2 + late fusion | 23.208 | <0.001 | +0.088 | +0.081 [0.023, 0.146] |
| C2 + WSI + CNV(RF) | 20.367 | <0.001 | +0.090 | +0.069 [0.012, 0.129] |

**late_mean false negatives** (11; by stratum {'discovery': 11}): median `kept_tiles` 3194.143; median percentile within their stratum's progressors 80.0 and non-progressors 88.095. Per patient: [{'stratum': 'discovery', 'kept_tiles': 1413.667, 'percentile_among_stratum_progressors': 60.0, 'percentile_among_stratum_nonprogressors': 50.0}, {'stratum': 'discovery', 'kept_tiles': 3194.143, 'percentile_among_stratum_progressors': 80.0, 'percentile_among_stratum_nonprogressors': 88.095}, {'stratum': 'discovery', 'kept_tiles': 895.0, 'percentile_among_stratum_progressors': 27.5, 'percentile_among_stratum_nonprogressors': 19.048}, {'stratum': 'discovery', 'kept_tiles': 3687.125, 'percentile_among_stratum_progressors': 87.5, 'percentile_among_stratum_nonprogressors': 92.857}, {'stratum': 'discovery', 'kept_tiles': 3917.5, 'percentile_among_stratum_progressors': 90.0, 'percentile_among_stratum_nonprogressors': 92.857}, {'stratum': 'discovery', 'kept_tiles': 1202.0, 'percentile_among_stratum_progressors': 55.0, 'percentile_among_stratum_nonprogressors': 45.238}, {'stratum': 'discovery', 'kept_tiles': 3496.0, 'percentile_among_stratum_progressors': 85.0, 'percentile_among_stratum_nonprogressors': 90.476}, {'stratum': 'discovery', 'kept_tiles': 5637.0, 'percentile_among_stratum_progressors': 97.5, 'percentile_among_stratum_nonprogressors': 100.0}, {'stratum': 'discovery', 'kept_tiles': 1416.0, 'percentile_among_stratum_progressors': 62.5, 'percentile_among_stratum_nonprogressors': 50.0}, {'stratum': 'discovery', 'kept_tiles': 4718.0, 'percentile_among_stratum_progressors': 95.0, 'percentile_among_stratum_nonprogressors': 100.0}, {'stratum': 'discovery', 'kept_tiles': 1114.0, 'percentile_among_stratum_progressors': 47.5, 'percentile_among_stratum_nonprogressors': 35.714}].

**Sources.** `results/paper_plan/round3_main.json` · `scripts/paper_plan/pr3_main.py` · commit 6976646 (`R3`). **Caveats.** `kept_tiles` comes from the 0.44 µm/px extraction, not the release's 256-tile sample; scanner groups are unbalanced.

### R4. Risk groups: valid version only
**Question.** What do risk groups show when time-to-event is only used where it is interpretable?

**Status.** DONE. **Pre-specification.** `cf244e1` §R4. the paper-plan item-5 and follow-up F4 version-A results (censoring from MonthsBeforeLastBiopsy) are superseded by version B (biopsy-date censoring); earlier documents are not edited.

**Validation stratum, version B censoring** (n 68, events 10; training-fold tertiles):

| model | groups: n / events / median time (d) | log-rank p | Cox feasible (≥3 events low and high) | Cox HR high vs low | Cox HR moderate vs low | figure |
|---|---|---|---|---|---|---|
| Late fusion (image + RF CNV) | low: 30 / 0 / 728.5 / moderate: 20 / 2 / 736.5 / high: 18 / 8 / 901.0 | 0.344 | False | not fitted |  | `results/paper_plan/figs/km_v3/km_validation_late_mean.png` |
| CNV (release RF) | low: 40 / 3 / 731.0 / moderate: 16 / 4 / 739.0 / high: 12 / 3 / 810.5 | 0.746 | True | [0.729, 0.117, 4.549] | [1.385, 0.298, 6.429] | `results/paper_plan/figs/km_v3/km_validation_cnv_only.png` |
| CNV (Killcoyne method) | low: 35 / 4 / 722.0 / moderate: 18 / 4 / 780.5 / high: 15 / 2 / 735.0 | 0.105 | False | not fitted |  | `results/paper_plan/figs/km_v3/km_validation_cnv_km.png` |
| Clinical C2 (primary) | low: 38 / 6 / 729.0 / moderate: 25 / 2 / 742.0 / high: 5 / 2 / 1914.0 | 0.416 | False | not fitted |  | `results/paper_plan/figs/km_v3/km_validation_C2_grade_maxsofar.png` |
| WSI | low: 28 / 0 / 732.0 / moderate: 23 / 3 / 729.0 / high: 17 / 7 / 916.0 | 0.56 | False | not fitted |  | `results/paper_plan/figs/km_v3/km_validation_image_only.png` |

**Pooled cohort: rates and odds ratios only.**

| model | low: n / events / rate [Wilson] | moderate | high | OR high vs low (Haldane) | MH OR two strata [CI] | MH OR three strata [CI] |
|---|---|---|---|---|---|---|
| Late fusion (image + RF CNV) | 51 / 7 / 0.137 [0.068, 0.257] | 46 / 12 / 0.261 [0.156, 0.403] | 53 / 31 / 0.585 [0.451, 0.707] | 8.307 | 7.167 [2.587, 19.850] | 12.463 [2.708, 57.355] |
| CNV (release RF) | 52 / 10 / 0.192 [0.108, 0.319] | 47 / 17 / 0.362 [0.240, 0.505] | 51 / 23 / 0.451 [0.323, 0.586] | 3.338 | 1.31 [0.468, 3.664] | 0.926 [0.247, 3.469] |
| CNV (Killcoyne method) | 49 / 13 / 0.265 [0.162, 0.403] | 49 / 14 / 0.286 [0.178, 0.424] | 52 / 23 / 0.442 [0.316, 0.577] | 2.154 | 0.854 [0.301, 2.425] | 0.334 [0.076, 1.473] |
| Clinical C2 (primary) | 57 / 13 / 0.228 [0.138, 0.352] | 44 / 9 / 0.205 [0.112, 0.345] | 49 / 28 / 0.571 [0.433, 0.700] | 4.37 | 2.663 [1.004, 7.067] | 4.694 [1.152, 19.116] |
| WSI | 52 / 8 / 0.154 [0.080, 0.275] | 47 / 14 / 0.298 [0.187, 0.440] | 51 / 28 / 0.549 [0.414, 0.677] | 6.349 | 5.66 [2.120, 15.110] | 25.539 [3.079, 211.820] |

**Sources.** `results/paper_plan/round3_main.json` · `scripts/paper_plan/pr3_main.py` · commit 6976646 (`R4`); figures `results/paper_plan/figs/km_v3/`. **Caveats.** With 10 events in the validation stratum the log-rank test and any Cox model are low-powered; the three-stratum MH OR conditions on the Killcoyne case/control status, which is itself an outcome-derived label.

### R5. False positives: stratum and follow-up
**Question.** Does the FP excess of later disease survive adjustment for stratum and follow-up, and does the flagged mislabelled patient change it?

**Status.** DONE. **Pre-specification.** `cf244e1` §R5.

**Adjusted for baseline grade, max grade, stratum (discovery) and follow-up (years after last release row):**

| model | FP / TN | FP, TN by stratum {discovery: [FP, TN], validation: [FP, TN]} | later HGD+: OR FP [CI], p; covariate ORs; raw counts FP / TN | later LGD+ |
|---|---|---|---|---|
| Late fusion (image + RF CNV) | 40 / 60 | {'discovery': [22, 20], 'validation': [18, 40]} | 5.353 [1.392, 20.584], p 0.015; OR discovery 0.600, OR follow-up/yr 1.134; raw [11, 4] | 2.589 [0.795, 8.435], p 0.114; raw [11, 8] |
| WSI | 50 / 50 | {'discovery': [25, 17], 'validation': [25, 33]} | 3.747 [0.940, 14.936], p 0.061; OR discovery 0.685, OR follow-up/yr 1.154; raw [11, 4] | 1.878 [0.560, 6.296], p 0.307; raw [11, 8] |
| CNV (release RF) | 55 / 45 | {'discovery': [35, 7], 'validation': [20, 38]} | 9.198 [1.668, 50.730], p 0.011; OR discovery 0.260, OR follow-up/yr 1.131; raw [13, 2] | 8.704 [1.853, 40.889], p 0.006; raw [16, 3] |
| CNV (Killcoyne method) | 66 / 34 | {'discovery': [38, 4], 'validation': [28, 30]} | 12.122 [1.356, 108.322], p 0.026; OR discovery 0.282, OR follow-up/yr 1.131; raw [14, 1] | 7.228 [1.321, 39.557], p 0.023; raw [17, 2] |
| Clinical C2 (primary) | 56 / 44 | {'discovery': [30, 12], 'validation': [26, 32]} | 1.190 [0.300, 4.722], p 0.804; OR discovery 0.570, OR follow-up/yr 1.135; raw [10, 5] | 0.726 [0.203, 2.593], p 0.622; raw [11, 8] |
| clinical_3a | 38 / 62 | {'discovery': [22, 20], 'validation': [16, 42]} | 4.652 [1.151, 18.803], p 0.031; OR discovery 0.540, OR follow-up/yr 1.151; raw [10, 5] | 5.833 [1.532, 22.209], p 0.01; raw [12, 7] |
| v4_exploratory | 26 / 74 | {'discovery': [17, 25], 'validation': [9, 49]} | 7.696 [1.790, 33.095], p 0.006; OR discovery 0.410, OR follow-up/yr 1.143; raw [9, 6] | 4.200 [1.096, 16.094], p 0.036; raw [9, 10] |

**Rerun with the 1 flagged patient moved to the progressors** (late_mean pooled AUROC 0.774 → 0.769, events 51):

| model | FP / TN | by stratum | later HGD+ | later LGD+ |
|---|---|---|---|---|
| Late fusion (image + RF CNV) | 40 / 59 | {'discovery': [22, 19], 'validation': [18, 40]} | 7.425 [1.666, 33.092], p 0.009; OR discovery 0.381, OR follow-up/yr 1.154; raw [11, 3] | 3.054 [0.883, 10.560], p 0.078; raw [11, 7] |
| WSI | 49 / 50 | {'discovery': [24, 17], 'validation': [25, 33]} | 3.042 [0.736, 12.566], p 0.124; OR discovery 0.444, OR follow-up/yr 1.167; raw [10, 4] | 1.534 [0.438, 5.369], p 0.503; raw [10, 8] |
| CNV (release RF) | 54 / 45 | {'discovery': [34, 7], 'validation': [20, 38]} | 8.938 [1.586, 50.356], p 0.013; OR discovery 0.172, OR follow-up/yr 1.152; raw [12, 2] | 8.660 [1.800, 41.662], p 0.007; raw [15, 3] |
| CNV (Killcoyne method) | 65 / 34 | {'discovery': [37, 4], 'validation': [28, 30]} | 12.683 [1.366, 117.748], p 0.025; OR discovery 0.168, OR follow-up/yr 1.155; raw [13, 1] | 7.374 [1.312, 41.442], p 0.023; raw [16, 2] |
| Clinical C2 (primary) | 55 / 44 | {'discovery': [29, 12], 'validation': [26, 32]} | 0.949 [0.222, 4.068], p 0.944; OR discovery 0.373, OR follow-up/yr 1.157; raw [9, 5] | 0.572 [0.149, 2.196], p 0.416; raw [10, 8] |
| clinical_3a | 37 / 62 | {'discovery': [21, 20], 'validation': [16, 42]} | 3.816 [0.879, 16.564], p 0.074; OR discovery 0.351, OR follow-up/yr 1.170; raw [9, 5] | 4.991 [1.262, 19.742], p 0.022; raw [11, 7] |
| v4_exploratory | 26 / 73 | {'discovery': [17, 24], 'validation': [9, 49]} | 11.432 [2.275, 57.437], p 0.003; OR discovery 0.231, OR follow-up/yr 1.169; raw [9, 5] | 5.296 [1.270, 22.073], p 0.022; raw [9, 9] |

**Sources.** `results/paper_plan/round3_main.json` · `scripts/paper_plan/pr3_main.py` · commit 6976646 (`R5`). **Caveats.** 100 non-progressors and 15 later-HGD+ events with five covariates: the Wald CIs are wide and some fits may be near-separated.

### R6. Headline numbers under each view
**Status.** DONE. n / events: pooled and stratified [150, 50]; E-HGD [150, 36]; Δ over stratum + tiles is fold-honest (R3).

| arm | pooled AUROC [CI] | stratified AUROC [CI] | E-HGD pooled [CI] | E-HGD stratified [CI] | ΔAUROC over stratum + tiles [CI] |
|---|---|---|---|---|---|
| Clinical C1 | 0.688 [0.588, 0.785] | 0.591 [0.482, 0.699] | 0.542 [0.432, 0.656] | 0.441 [0.328, 0.552] | +0.009 [-0.026, +0.044] |
| Clinical C2 (primary) | 0.681 [0.582, 0.776] | 0.601 [0.492, 0.704] | 0.529 [0.424, 0.640] | 0.446 [0.327, 0.553] | +0.014 [-0.026, +0.054] |
| Clinical C3 | 0.666 [0.571, 0.758] | 0.582 [0.478, 0.688] | 0.510 [0.404, 0.619] | 0.422 [0.311, 0.533] | +0.010 [-0.028, +0.048] |
| Clinical C4 (=3a) | 0.765 [0.684, 0.844] | 0.739 [0.648, 0.824] | 0.690 [0.591, 0.786] | 0.667 [0.561, 0.764] | +0.013 [-0.021, +0.048] |
| CNV (release RF) | 0.663 [0.569, 0.754] | 0.594 [0.488, 0.695] | 0.676 [0.561, 0.774] | 0.651 [0.532, 0.771] | -0.016 [-0.041, +0.004] |
| CNV (Killcoyne method) | 0.640 [0.538, 0.734] | 0.597 [0.486, 0.703] | 0.694 [0.580, 0.789] | 0.684 [0.567, 0.794] | +0.002 [-0.029, +0.035] |
| WSI | 0.731 [0.640, 0.814] | 0.708 [0.612, 0.796] | 0.746 [0.650, 0.837] | 0.721 [0.616, 0.816] | +0.013 [-0.030, +0.057] |
| Early fusion | 0.738 [0.646, 0.818] | 0.735 [0.642, 0.820] | 0.782 [0.680, 0.868] | 0.773 [0.673, 0.860] | +0.027 [-0.021, +0.076] |
| Intermediate fusion | 0.741 [0.653, 0.818] | 0.717 [0.619, 0.806] | 0.744 [0.654, 0.829] | 0.723 [0.623, 0.817] | +0.017 [-0.020, +0.057] |
| Late fusion (image + RF CNV) | 0.774 [0.687, 0.849] | 0.745 [0.652, 0.829] | 0.782 [0.688, 0.865] | 0.757 [0.662, 0.850] | +0.023 [-0.030, +0.078] |
| Late fusion (image + KM CNV) | 0.764 [0.672, 0.843] | 0.730 [0.630, 0.819] | 0.785 [0.695, 0.864] | 0.757 [0.657, 0.847] | +0.011 [-0.041, +0.062] |
| Co-attention (extra) | 0.739 [0.652, 0.821] | 0.695 [0.596, 0.792] | 0.778 [0.689, 0.859] | 0.744 [0.649, 0.839] | +0.011 [-0.032, +0.055] |
| Late stack (extra) | 0.737 [0.648, 0.814] | 0.701 [0.602, 0.791] | 0.746 [0.657, 0.828] | 0.719 [0.620, 0.813] | +0.006 [-0.036, +0.046] |
| C2 + WSI | 0.802 [0.727, 0.873] | 0.756 [0.663, 0.838] | 0.678 [0.586, 0.772] | 0.616 [0.513, 0.716] | +0.059 [0.005, 0.120] |
| C2 + CNV(RF) | 0.784 [0.707, 0.857] | 0.715 [0.619, 0.805] | 0.657 [0.565, 0.753] | 0.579 [0.470, 0.683] | +0.037 [-0.004, +0.082] |
| C2 + CNV(KM) | 0.796 [0.713, 0.871] | 0.748 [0.647, 0.836] | 0.692 [0.587, 0.795] | 0.651 [0.532, 0.758] | +0.047 [-0.000, 0.098] |
| C2 + late fusion | 0.824 [0.755, 0.888] | 0.778 [0.689, 0.856] | 0.701 [0.612, 0.790] | 0.637 [0.538, 0.733] | +0.081 [0.023, 0.146] |
| C2 + WSI + CNV(RF) | 0.843 [0.778, 0.901] | 0.791 [0.703, 0.867] | 0.738 [0.654, 0.821] | 0.673 [0.573, 0.770] | +0.069 [0.012, 0.129] |

**Sources.** `results/paper_plan/round3_main.json` · `scripts/paper_plan/pr3_main.py` · commit 6976646 (`R6`, assembled from R1–R3).

## 4. Discrepancies found
1. Pooled vs stratified: late fusion 0.774 pooled vs 0.745 stratified; CNV (release RF) 0.663 vs 0.594; WSI 0.731 vs 0.708 (R1). The within-discovery AUROCs are 0.691 (late), 0.564 (CNV RF), 0.649 (WSI).
2. Stratum is predictable from the inputs among non-progressors: CNV features 0.891, image embedding 0.948, CNV QC without read counts 0.756 (R1); the pre-specified QC probe (1.0) was an artefact of the read-count missing indicator.
3. Tissue amount alone reaches 0.766 pooled and stratum + tiles 0.737 fold-honest (R3); the follow-up's item-5 version-A survival results are superseded (R4).
4. Under E-HGD the CNV arms move to 0.676 (RF) and 0.694 (KM) pooled (R2).

## 5. Pre-specification text as committed at `cf244e1` (verbatim)

> # BE paper plan, round 3: confounding checks before writing (R1–R6)
>
> **Status of this file: PRE-SPECIFICATION VERSION**, committed before any analysis in it was run. Results are appended in a
> later commit; the specification text is not edited afterwards.
>
> ## 1. Header (completed at the results commit)
> - Date: 26 September 2026. Commit at start: `e7ee492`. Pre-specification commit: the commit adding this text. Inputs: frozen release only; patient-level scores and strata written by the follow-up (`feasibility/paper_plan/followup_patient_scores.csv`, `f2_strata.csv`, `f1_cnv_km_oof.csv`, `later_disease_patient.csv`, `f5_later_hgd_nonprogressors.csv`; commit `fef1089`), image embeddings from `pp_latent.py` (`feasibility/paper_plan/latent/`), closeout tables (`feasibility/closeout/`).
> - Planned scripts: `scripts/paper_plan/pr3_main.py` (R1, R2 endpoints, R3, R4, R5, R6), `pr3_lopo.py` (R2 faithfulness retrain), `pr3_render.py`, `pr3_check_report.py`. Outputs `results/paper_plan/round3_main.json`, `round3_lopo.json`, figures `results/paper_plan/figs/km_v3/`.
> - Conventions as before (patient = max over rows; rank AUROC; 2,000 patient bootstraps `RandomState(0)`; permutations 2,000; fold honesty with the release outer folds and patient-keyed inner folds). Strata: discovery = Killcoyne 777-sheet patients (82: 39 sheet cases + 43 sheet controls), validation = 268-sheet patients (68), as defined in the follow-up F2 (`f2_strata.csv`).
>
> ## Pre-specifications
>
> ### R1. Stratum as a shortcut
> - Probes (discovery vs validation label) among the 100 non-progressors, fold-honest on the release outer folds (probe fitted on training-fold non-progressors, applied to held-out non-progressors; L2 logistic, C ∈ {0.01, 0.1, 1, 10} by the release inner folds restricted to the training patients; standardisation on training patients): (a) CNV features = patient mean of the release CNV matrix (632 features) → PCA to 20 components fitted on training patients then logistic (to avoid p ≫ n), and, as stated secondary, the 44 arm features + cx without PCA; (b) image patient embedding = patient mean of the image_only fold-model 256-d attention-pooled embedding (`emb_image_only_fold{k}.npy`, fold-k model for fold-k held-out patients); (c) CNV QC = patient means of MAPD noise, reads (missing → training median, plus a missing indicator), segments, fraction altered, cx. AUROC with patient bootstrap CI (2,000, seed 0).
> - Stratified AUROC = (n_pairs_disc × AUROC_disc + n_pairs_val × AUROC_val) / (n_pairs_disc + n_pairs_val), pairs = progressors × non-progressors within stratum. For every arm in the follow-up table (C1–C4, cnv_only, cnv_km, image_only, early, intermediate, late_mean, late_mean_km, co-attention, late-stack) and the C2 + modality fold-z combinations. Paired differences WSI − cnv_only, WSI − cnv_km, late_mean − WSI, late_mean_km − WSI, C2+modality − C2. CIs from a stratified patient bootstrap (patients resampled within stratum, 2,000, seed 0).
> - Stratum-adjusted incremental value: logistic regression of the patient label on stratum (two-level indicator), then stratum + logit of the arm's patient score (OOF); likelihood-ratio test (statsmodels, 1 df); ΔAUROC = AUROC(stratum + arm, in-sample fit) − AUROC(stratum alone) as the LR companion, and a fold-honest version (combination fitted on training-fold patients, applied held-out) reported alongside.
>
> ### R2. Endpoint sensitivity
> - Progressor type from the release: HGD/IMC if any positive row's `NextBiopsyLabel` ≥ 3, else second-LGD. E-HGD: label 1 for HGD/IMC progressors, 0 for everyone else; E-HGD-excl: second-LGD-only progressors removed. Every arm: pooled and stratified AUROC (as R1), n, events, CI. No retraining.
> - Faithfulness retrain (`pr3_lopo.py`): within the 82 discovery patients, label = sheet status (P/NP, patient level, mode over the patient's rows), elastic net as F1 (l1_ratio 0.9, standardisation and median imputation on the training rows), leave-one-patient-out; C ∈ {0.01, 0.1, 1, 10} chosen for each left-out patient by 5-fold patient-grouped CV on the remaining 81 (patient AUROC vs sheet status; folds from `GroupKFold` on patient id with a fixed patient order). Compare with the published LOPO probabilities on the matched rows: Spearman (rows), patient-level AUROC vs sheet status for ours and for the published values, and Spearman of ours vs our F1 arm.
>
> ### R3. Tissue amount as a shortcut
> - `kept_tiles` (0.44 µm/px h5 `kept_tiles`, patient mean; also `tissue_frac`): AUROC as a score with the sign chosen on training folds (if training-fold AUROC < 0.5 use the negative), pooled and within each stratum, with CIs. Distributions (median, IQR) by stratum and by scanner model; Mann-Whitney discovery vs validation. Among non-progressors, Spearman of each arm's patient score with `kept_tiles`.
> - Label ~ stratum + kept_tiles, then + arm logit: LR test and ΔAUROC (in-sample and fold-honest as R1).
> - The 11 late_mean FN patients: their `kept_tiles` percentile within the progressor and within the non-progressor distributions of their own stratum.
>
> ### R4. Risk groups, valid version only
> - Statement that version A in `docs/paper_plan_answers.md` item 5 (and the F4 version-A rows) is superseded by version B (biopsy-date censoring), recorded here (earlier docs are not edited). Version B KM, log-rank and Cox (high vs low, moderate vs low) restricted to the validation stratum for late_mean, cnv_only, cnv_km, C2, with the training-fold tertile groups of the follow-up; feasibility rule stated in advance: Cox reported only if each compared group has ≥ 3 events, otherwise KM and log-rank only. Pooled cohort: group rates with Wilson CI, OR high vs low (Haldane), and the Mantel–Haenszel OR across strata (primary: two strata discovery/validation; secondary: three strata case/control/validation) with its CI (statsmodels `StratifiedTable`).
>
> ### R5. False positives: stratum and follow-up
> - F5 logistic (later HGD+ and later LGD+ on FP status + baseline grade + max grade so far) refitted with stratum (discovery indicator) and follow-up length (days from last release row to the last DB report, 0 if none) as covariates, per model (late_mean, image_only, cnv_only, cnv_km, C2, clinical_3a, v4_exploratory). FP/TN counts per stratum per model. Rerun of the FP table with the one flagged patient (`f5_later_hgd_nonprogressors.csv`, `hgd_report_is_the_next_release_biopsy` = True) moved to the progressors (removed from the non-progressor set; its effect on pooled AUROC of late_mean reported as a sensitivity).
>
> ### R6. Headline numbers under each view
> - One table, rows = arms; columns = pooled AUROC [CI], stratified AUROC [CI] (R1), E-HGD pooled [CI], E-HGD stratified [CI], ΔAUROC over stratum + tiles fold-honest [CI] (R3), with n and events per column.
>
> (Results follow in the results commit.)
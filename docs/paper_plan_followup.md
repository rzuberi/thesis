# BE paper plan follow-up (F1–F9)

## 1. Header
- Date: 25–26 September 2026. Commit at start: `38a83f2`. Pre-specification commit: `0db4075` (verbatim in §6). Script commits: `a8e5311`, `367d512`, `f99bde9`, `7d62569`. Results commit (result files, figures, scripts): `fef1089`; this rendered text is the next commit. Frozen release only.
- Scripts (`scripts/paper_plan/`): `pf_cnv_killcoyne.py` (F1), `pf_main.py` (F2–F5, F6a, attention mass, F9), `pf_gpu.py` (F6b/c, F7, F8 train-vs-held-out), `pf_latent_figs.py` (F8), `pf_render.py`, `pf_check_report.py`.
- Results (`results/paper_plan/`): `f1_cnv_killcoyne.json`, `followup_main.json`, `f6_image_tiles.json`, `f7_modality_ablation.json`, `f8_train_vs_heldout.json`, `f8_probe_vs_output.json`; figures `figs/km_v2/`, `figs/latent_folds/`. Cluster-only rows: `feasibility/paper_plan/` (F1 OOF, strata, patient scores, later-HGD list, F6 draws, F6c checkpoints).
- Conventions as in `docs/paper_plan_answers.md`.

## 2. Status table
| item | status | key number |
|---|---|---|
| F1 Killcoyne-method CNV arm | DONE | all 150: 0.640 [0.538, 0.734] vs release CNV 0.663; on the 82 discovery patients 0.580 vs 0.564; Spearman with published LOPO 0.243 (rows 500) |
| F2 Cohort design heterogeneity | DONE | stratum-only score AUROC 0.752 [0.647, 0.849]; strata × overlap in §F2 |
| F3 Clinical arm | DONE | C1 0.688, C2 0.681 (primary), C3 0.666, C4 0.765; C2 + late_mean (z-mean) Δ +0.143 [0.072, 0.216] |
| F4 Survival inconsistency | DONE | version B (biopsy dates) late_mean HR high vs low [2.515, 1.099, 5.751]; version A [1.792, 0.788, 4.075] |
| F5 FP confounding | DONE | late_mean adjusted OR later HGD+ 5.29 [1.466, 19.086]; 15 later-HGD+ non-progressors, 1 flagged |
| F6 Attention and tiles | DONE | image-only top-5 % mass 0.158 (uniform 0.05); image-only 0.44 µm ≤2,048 tiles 0.675 [0.580, 0.769]; 256-tile draw SD median 0.005 |
| F7 Fusion uses CNV? | DONE | CNV jointly permuted ΔAUROC: early +0.122, intermediate +0.076, co-attention +0.081; image permuted: +0.165 / +0.205 / +0.200 |
| F8 Latent follow-ups | DONE | probe − model output: early +0.084 [0.006, 0.163], intermediate +0.077 [0.019, 0.140]; five-fold figures `results/paper_plan/figs/latent_folds/` |
| F9 Housekeeping | DONE | WSI − CNV lower CI bound vs −0.05 margin: release CNV -0.065, Killcoyne-method CNV -0.031 |

## 3. Items

### F1. Killcoyne-method CNV arm
**Question.** Does a CNV arm built with Killcoyne's method (elastic net on windows + arms) recover the CNV signal that the release's random forest loses on the overlap patients?

**Status.** DONE.

**Pre-specification.** `0db4075` §F1. As built: features {'n_total': 632, 'n_5mb_window_minus_arm': 587, 'n_arm': 44, 'cx': 1} (the release's window-minus-arm encoding; the paper reports 589 windows and 44 arms, our release table carries 587 windows and 44 arms plus cx); model sklearn LogisticRegression(penalty=elasticnet, solver=saga, l1_ratio=0.9), C by release inner folds (patient AUROC), per-feature standardisation and median imputation on outer training rows; C per fold {'1': 0.3, '2': 0.1, '3': 3.0, '4': 1.0, '5': 0.1}; non-zero coefficients per fold {'1': 55, '2': 36, '3': 125, '4': 77, '5': 45} (paper: 74). α sensitivity (patient AUROC, all 150): α 0.1: 0.623, α 0.5: 0.627.

**Result: subsets.**

| patients | n | events | CNV (Killcoyne method) | CNV (release RF) | WSI | late (image + RF CNV) | late (image + KM CNV) |
|---|---|---|---|---|---|---|---|
| all_150 | 150 | 50 | 0.640 [0.538, 0.734] | 0.663 [0.569, 0.754] | 0.731 [0.640, 0.814] | 0.774 [0.687, 0.849] | 0.764 [0.672, 0.843] |
| never_in_ERIN_96 | 96 | 36 | 0.736 [0.622, 0.835] | 0.760 [0.652, 0.858] | 0.744 [0.634, 0.850] | 0.819 [0.722, 0.907] | 0.802 [0.700, 0.888] |
| also_in_ERIN_54 | 54 | 14 | 0.405 [0.221, 0.591] | 0.454 [0.280, 0.627] | 0.704 [0.550, 0.841] | 0.679 [0.522, 0.815] | 0.671 [0.512, 0.809] |
| killcoyne_discovery_82 | 82 | 40 | 0.580 [0.443, 0.714] | 0.564 [0.427, 0.693] | 0.649 [0.527, 0.765] | 0.691 [0.569, 0.803] | 0.676 [0.551, 0.788] |
| other_68 | 68 | 10 | 0.647 [0.480, 0.812] | 0.683 [0.483, 0.865] | 0.879 [0.785, 0.955] | 0.900 [0.814, 0.968] | 0.888 [0.798, 0.960] |

**Faithfulness vs the published LOPO predictions** (500 rows / 82 patients): Spearman Killcoyne-method arm vs published 0.243; release RF vs published 0.278; KM arm vs RF 0.500. Patient AUROC for our endpoint on the matched patients (n 82, events 40): published max prob 0.718, KM arm 0.580, RF 0.562.

**Item 2 rerun (WSI vs CNV) and item 4 rerun (late fusion with the KM arm), per subset:**

| patients | WSI − CNV(KM) Δ [CI], perm p | WSI − CNV(RF) Δ [CI], perm p | late(KM) − WSI | late(KM) − CNV(KM) | late(KM) − late(RF) | late(RF) − WSI |
|---|---|---|---|---|---|---|
| all_150 | +0.091 [-0.031, +0.215], 0.0785 | +0.068 [-0.065, +0.196], 0.1434 | +0.033 [-0.009, +0.072], p 0.043 | +0.124 [0.023, 0.230] | -0.010 [-0.043, +0.019] | +0.043 [0.014, 0.071], p 0.0025 |
| never_in_ERIN_96 | +0.008 [-0.146, +0.167], 0.4538 | -0.016 [-0.172, +0.143], 0.5807 | +0.058 [0.008, 0.109], p 0.008 | +0.066 [-0.055, +0.191] | -0.018 [-0.055, +0.018] | +0.076 [0.042, 0.112], p 0.0005 |
| also_in_ERIN_54 | +0.298 [0.081, 0.514], 0.004 | +0.250 [0.040, 0.452], 0.013 | -0.032 [-0.102, +0.034], p 0.8921 | +0.266 [0.084, 0.454] | -0.007 [-0.071, +0.048] | -0.025 [-0.082, +0.031], p 0.8401 |
| killcoyne_discovery_82 | +0.069 [-0.097, +0.245], 0.2144 | +0.086 [-0.084, +0.266], 0.1564 | +0.026 [-0.041, +0.087], p 0.2204 | +0.095 [-0.042, +0.236] | -0.015 [-0.071, +0.033] | +0.042 [0.001, 0.083], p 0.027 |
| other_68 | +0.233 [0.060, 0.409], 0.0415 | +0.197 [-0.002, +0.415], 0.055 | +0.009 [-0.030, +0.054], p 0.3493 | +0.241 [0.096, 0.395] | -0.012 [-0.039, +0.012] | +0.021 [-0.019, +0.064], p 0.2274 |

**Diagnosis of the release RF on the 25 overlap-discovery patients (192 rows).**

| fold | held-out of the 25 | events | RF AUROC | KM-arm AUROC | training rows (positive) | training patients (progressors) | rows from the 25 in training (positive) |
|---|---|---|---|---|---|---|---|
| 1 | 4 | 1 | 0.000 | 0.000 | 533 (90) | 120 (40) | 159 (27) |
| 2 | 7 | 2 | 0.200 | 0.000 | 577 (94) | 120 (40) | 129 (24) |
| 3 | 3 | 2 | 0.000 | 0.000 | 569 (78) | 120 (40) | 169 (18) |
| 4 | 6 | 3 | 0.444 | 0.333 | 586 (90) | 120 (40) | 162 (24) |
| 5 | 5 | 3 | 0.833 | 0.333 | 563 (76) | 120 (40) | 149 (19) |

Feature distributions, rows of the 25 vs the rest (192 vs 515 rows): mean |z| over arm + cx features {'median_25': 0.475, 'median_rest': 0.528, 'p': 0.127}; PCA-64 score norm {'median_25': 8.285, 'median_rest': 8.905, 'p': 0.032}; raw cx {'median_25': 0.0, 'median_rest': 0.0, 'p': 0.438}. RF probability medians: 25 progressor rows {'n': 28, 'median': 0.184}, 25 non-progressor rows {'n': 164, 'median': 0.157}, rest progressor {'n': 79, 'median': 0.223}, rest non-progressor {'n': 436, 'median': 0.156}; KM-arm medians on the 25: progressor rows 0.099, non-progressor rows 0.141.

**Method.** `pf_cnv_killcoyne.py`; release outer folds and inner folds; standardisation and imputation on training rows. **Sources.** `results/paper_plan/f1_cnv_killcoyne.json` · `scripts/paper_plan/pf_cnv_killcoyne.py` · commit fef1089; OOF rows `feasibility/paper_plan/f1_cnv_km_oof.csv` (cluster); Killcoyne Methods p.1733, Ext Data Fig 9. **Caveats.** Not a re-run of glmnet: sklearn saga with l1_ratio 0.9 and C by inner CV; the paper standardised across the whole cohort, here per training fold; our endpoint differs from theirs; the published LOPO probabilities were produced with their labels, so agreement is expected to be partial.

### F2. Cohort design heterogeneity
**Question.** Do results differ by cohort design stratum, and does stratum itself predict the label?

**Status.** DONE.

**Pre-specification.** `0db4075` §F2. discovery_case/control = any row CNV id in the 777 discovery sheet, sheet Status P/NP (mode); validation_sheet = any row in the 268 validation sheet; other = neither.

Stratum × overlap (patients): {'also_in_ERIN': {'discovery_case': 10, 'discovery_control': 15, 'validation_sheet': 29}, 'never_in_ERIN': {'discovery_case': 29, 'discovery_control': 28, 'validation_sheet': 39}}. Stratum × label (patients, columns 0/1): {'0': {'discovery_case': 5, 'discovery_control': 37, 'validation_sheet': 58}, '1': {'discovery_case': 34, 'discovery_control': 6, 'validation_sheet': 10}}. Strata skipped (fewer than 20 patients or 5 events/non-events): [].

**discovery_case** (n 39, events 34)

| arm | AUROC [CI] | AUPRC [CI] | n | events |
|---|---|---|---|---|
| Clinical C1 (grade) | 0.597 [0.236, 0.895] | 0.904 [0.787, 0.991] | 39 | 34 |
| Clinical C2 (grade + max so far) [primary clinical] | 0.615 [0.386, 0.821] | 0.924 [0.832, 0.985] | 39 | 34 |
| Clinical C3 (+ LGD streak) | 0.621 [0.382, 0.843] | 0.924 [0.833, 0.985] | 39 | 34 |
| Clinical C4 (+ surveillance = 3a) | 0.618 [0.201, 0.973] | 0.896 [0.761, 0.998] | 39 | 34 |
| CNV (release, PCA64 + RF) | 0.553 [0.257, 0.816] | 0.908 [0.794, 0.989] | 39 | 34 |
| CNV (Killcoyne method, elastic net) | 0.471 [0.245, 0.685] | 0.893 [0.775, 0.979] | 39 | 34 |
| WSI | 0.588 [0.230, 0.867] | 0.876 [0.738, 0.991] | 39 | 34 |
| Early fusion | 0.565 [0.237, 0.871] | 0.908 [0.795, 0.990] | 39 | 34 |
| Intermediate fusion | 0.588 [0.162, 0.926] | 0.896 [0.765, 0.995] | 39 | 34 |
| Late fusion (mean, image + CNV release) | 0.629 [0.321, 0.869] | 0.917 [0.796, 0.992] | 39 | 34 |
| Late fusion (mean, image + CNV Killcoyne method) | 0.582 [0.278, 0.847] | 0.916 [0.810, 0.991] | 39 | 34 |
| Co-attention fusion (extra) | 0.541 [0.232, 0.865] | 0.901 [0.777, 0.991] | 39 | 34 |
| Late stack-logit (extra) | 0.612 [0.296, 0.889] | 0.913 [0.792, 0.990] | 39 | 34 |

**discovery_control** (n 43, events 6)

| arm | AUROC [CI] | AUPRC [CI] | n | events |
|---|---|---|---|---|
| Clinical C1 (grade) | 0.809 [0.676, 0.921] | 0.312 [0.148, 0.612] | 43 | 6 |
| Clinical C2 (grade + max so far) [primary clinical] | 0.818 [0.688, 0.931] | 0.321 [0.148, 0.633] | 43 | 6 |
| Clinical C3 (+ LGD streak) | 0.782 [0.644, 0.903] | 0.282 [0.134, 0.550] | 43 | 6 |
| Clinical C4 (+ surveillance = 3a) | 0.721 [0.507, 0.897] | 0.293 [0.105, 0.665] | 43 | 6 |
| CNV (release, PCA64 + RF) | 0.293 [0.096, 0.481] | 0.112 [0.050, 0.231] | 43 | 6 |
| CNV (Killcoyne method, elastic net) | 0.113 [0.012, 0.244] | 0.091 [0.041, 0.187] | 43 | 6 |
| WSI | 0.730 [0.472, 0.961] | 0.469 [0.113, 0.840] | 43 | 6 |
| Early fusion | 0.676 [0.378, 0.892] | 0.264 [0.100, 0.606] | 43 | 6 |
| Intermediate fusion | 0.761 [0.547, 0.927] | 0.311 [0.143, 0.690] | 43 | 6 |
| Late fusion (mean, image + CNV release) | 0.730 [0.481, 0.932] | 0.364 [0.113, 0.777] | 43 | 6 |
| Late fusion (mean, image + CNV Killcoyne method) | 0.653 [0.435, 0.849] | 0.217 [0.093, 0.496] | 43 | 6 |
| Co-attention fusion (extra) | 0.599 [0.341, 0.825] | 0.240 [0.076, 0.574] | 43 | 6 |
| Late stack-logit (extra) | 0.707 [0.500, 0.885] | 0.250 [0.111, 0.567] | 43 | 6 |

**validation_sheet** (n 68, events 10)

| arm | AUROC [CI] | AUPRC [CI] | n | events |
|---|---|---|---|---|
| Clinical C1 (grade) | 0.521 [0.270, 0.772] | 0.254 [0.093, 0.558] | 68 | 10 |
| Clinical C2 (grade + max so far) [primary clinical] | 0.531 [0.293, 0.764] | 0.218 [0.086, 0.503] | 68 | 10 |
| Clinical C3 (+ LGD streak) | 0.553 [0.317, 0.781] | 0.225 [0.091, 0.506] | 68 | 10 |
| Clinical C4 (+ surveillance = 3a) | 0.795 [0.668, 0.900] | 0.321 [0.165, 0.596] | 68 | 10 |
| CNV (release, PCA64 + RF) | 0.683 [0.483, 0.865] | 0.331 [0.129, 0.609] | 68 | 10 |
| CNV (Killcoyne method, elastic net) | 0.647 [0.480, 0.812] | 0.294 [0.113, 0.547] | 68 | 10 |
| WSI | 0.879 [0.785, 0.955] | 0.500 [0.247, 0.783] | 68 | 10 |
| Early fusion | 0.828 [0.705, 0.927] | 0.385 [0.207, 0.707] | 68 | 10 |
| Intermediate fusion | 0.814 [0.699, 0.912] | 0.354 [0.182, 0.655] | 68 | 10 |
| Late fusion (mean, image + CNV release) | 0.900 [0.814, 0.968] | 0.511 [0.287, 0.838] | 68 | 10 |
| Late fusion (mean, image + CNV Killcoyne method) | 0.888 [0.798, 0.960] | 0.510 [0.273, 0.796] | 68 | 10 |
| Co-attention fusion (extra) | 0.897 [0.814, 0.960] | 0.455 [0.277, 0.788] | 68 | 10 |
| Late stack-logit (extra) | 0.857 [0.765, 0.933] | 0.377 [0.218, 0.654] | 68 | 10 |

**discovery_all** (n 82, events 40)

| arm | AUROC [CI] | AUPRC [CI] | n | events |
|---|---|---|---|---|
| Clinical C1 (grade) | 0.615 [0.490, 0.737] | 0.584 [0.448, 0.746] | 82 | 40 |
| Clinical C2 (grade + max so far) [primary clinical] | 0.625 [0.498, 0.744] | 0.583 [0.441, 0.752] | 82 | 40 |
| Clinical C3 (+ LGD streak) | 0.591 [0.468, 0.711] | 0.575 [0.429, 0.739] | 82 | 40 |
| Clinical C4 (+ surveillance = 3a) | 0.720 [0.593, 0.827] | 0.709 [0.556, 0.844] | 82 | 40 |
| CNV (release, PCA64 + RF) | 0.564 [0.427, 0.693] | 0.614 [0.471, 0.757] | 82 | 40 |
| CNV (Killcoyne method, elastic net) | 0.580 [0.443, 0.714] | 0.675 [0.530, 0.804] | 82 | 40 |
| WSI | 0.649 [0.527, 0.765] | 0.645 [0.510, 0.809] | 82 | 40 |
| Early fusion | 0.704 [0.579, 0.812] | 0.715 [0.576, 0.845] | 82 | 40 |
| Intermediate fusion | 0.684 [0.567, 0.798] | 0.688 [0.547, 0.826] | 82 | 40 |
| Late fusion (mean, image + CNV release) | 0.691 [0.569, 0.803] | 0.703 [0.564, 0.835] | 82 | 40 |
| Late fusion (mean, image + CNV Killcoyne method) | 0.676 [0.551, 0.788] | 0.711 [0.578, 0.828] | 82 | 40 |
| Co-attention fusion (extra) | 0.625 [0.505, 0.743] | 0.643 [0.504, 0.789] | 82 | 40 |
| Late stack-logit (extra) | 0.647 [0.524, 0.763] | 0.632 [0.492, 0.786] | 82 | 40 |

**Matching check within the discovery stratum (our progressors vs non-progressors).** {'age': {'progressors_median_n': [63.0, 26], 'nonprogressors_median_n': [61.0, 40], 'mannwhitney_p': 0.368}, 'pragueM': {'progressors_median_n': [4.0, 19], 'nonprogressors_median_n': [4.5, 36], 'mannwhitney_p': 0.809}, 'pragueC': {'progressors_median_n': [0.0, 16], 'nonprogressors_median_n': [0.0, 36], 'mannwhitney_p': 0.434}, 'fu_months': {'progressors_median_n': [67.17, 40], 'nonprogressors_median_n': [66.99, 42], 'mannwhitney_p': 0.51}, 'sex': {'table': {'0': {'F': 11, 'M': 29, 'missing': 2}, '1': {'F': 4, 'M': 22, 'missing': 14}}, 'fisher_p': 0.369}, 'our_label_vs_sheet_status': {'0': {'false': 37, 'true': 5}, '1': {'false': 6, 'true': 34}}}. Our LGD2+ label vs the sheet's case/control status (patients): {'0': {'false': 37, 'true': 5}, '1': {'false': 6, 'true': 34}}.

**Stratum-only score** (training-fold progression rate per stratum applied to held-out patients): AUROC 0.752 [0.647, 0.849] (n 150, events 50).

**Arm scores by stratum among non-progressors** (discovery vs validation, patient max score):

| arm | discovery median (n) | validation median (n) | Mann-Whitney p |
|---|---|---|---|
| Clinical C2 (grade + max so far) [primary clinical] | 0.149 (42) | 0.116 (58) | <0.001 |
| CNV (release, PCA64 + RF) | 0.276 (42) | 0.184 (58) | <0.001 |
| CNV (Killcoyne method, elastic net) | 0.18 (42) | 0.123 (58) | <0.001 |
| WSI | 0.582 (42) | 0.38 (58) | 0.03 |
| Late fusion (mean, image + CNV release) | 0.374 (42) | 0.285 (58) | 0.007 |
| Late fusion (mean, image + CNV Killcoyne method) | 0.359 (42) | 0.264 (58) | 0.008 |

**Sources.** `results/paper_plan/followup_main.json` · `scripts/paper_plan/pf_main.py` · commit fef1089 (`F2`); strata `feasibility/paper_plan/f2_strata.csv`. **Caveats.** Demographics cover 66/150 patients; the sheet case/control status is Killcoyne's HGD/IMC endpoint, not ours; strata are post hoc.

### F3. Clinical arm without endpoint-definition features
**Question.** How much of the clinical arm is the endpoint rule or surveillance history, and does any modality add to the primary clinical arm C2?

**Status.** DONE. Primary clinical arm = **C2 (grade + MaxPathologySoFar)**; 3b (27 patients / 9 events) is in the supplement of `docs/paper_plan_answers.md` only.

**All 150 patients (50 events)**

| arm | AUROC [CI] | AUPRC [CI] | n | events |
|---|---|---|---|---|
| Clinical C1 (grade) | 0.688 [0.588, 0.785] | 0.513 [0.384, 0.660] | 150 | 50 |
| Clinical C2 (grade + max so far) [primary clinical] | 0.681 [0.582, 0.776] | 0.498 [0.373, 0.643] | 150 | 50 |
| Clinical C3 (+ LGD streak) | 0.666 [0.571, 0.758] | 0.489 [0.367, 0.634] | 150 | 50 |
| Clinical C4 (+ surveillance = 3a) | 0.765 [0.684, 0.844] | 0.547 [0.437, 0.711] | 150 | 50 |
| CNV (release, PCA64 + RF) | 0.663 [0.569, 0.754] | 0.538 [0.411, 0.671] | 150 | 50 |
| CNV (Killcoyne method, elastic net) | 0.640 [0.538, 0.734] | 0.569 [0.436, 0.694] | 150 | 50 |
| WSI | 0.731 [0.640, 0.814] | 0.557 [0.426, 0.717] | 150 | 50 |
| Early fusion | 0.738 [0.646, 0.818] | 0.590 [0.453, 0.733] | 150 | 50 |
| Intermediate fusion | 0.741 [0.653, 0.818] | 0.567 [0.435, 0.714] | 150 | 50 |
| Late fusion (mean, image + CNV release) | 0.774 [0.687, 0.849] | 0.630 [0.490, 0.772] | 150 | 50 |
| Late fusion (mean, image + CNV Killcoyne method) | 0.764 [0.672, 0.843] | 0.626 [0.489, 0.762] | 150 | 50 |
| Co-attention fusion (extra) | 0.739 [0.652, 0.821] | 0.548 [0.428, 0.703] | 150 | 50 |
| Late stack-logit (extra) | 0.737 [0.648, 0.814] | 0.530 [0.412, 0.684] | 150 | 50 |

C per fold: {'C1_grade': {'1': 0.01, '2': 0.01, '3': 0.1, '4': 0.1, '5': 0.1}, 'C2_grade_maxsofar': {'1': 0.1, '2': 0.01, '3': 0.01, '4': 0.01, '5': 0.01}, 'C3_plus_streak': {'1': 0.01, '2': 0.01, '3': 0.01, '4': 10.0, '5': 0.01}, 'C4_plus_surveillance_3a': {'1': 0.1, '2': 0.01, '3': 0.1, '4': 0.1, '5': 0.01}}.

**Does a modality add to C2?**

| combination | fold-z mean: AUROC, Δ vs C2 [CI], perm p | L2 stack on logits: AUROC, Δ vs C2 [CI], perm p |
|---|---|---|
| C2+image | 0.802, +0.120 [0.050, 0.196], 0.0005 | 0.781, +0.100 [0.023, 0.176], 0.004 |
| C2+cnv_only | 0.784, +0.103 [0.027, 0.179], 0.0075 | 0.734, +0.052 [-0.003, +0.111], 0.0385 |
| C2+cnv_km | 0.796, +0.114 [0.034, 0.193], 0.002 | 0.704, +0.022 [-0.023, +0.070], 0.1399 |
| C2+late_mean | 0.824, +0.143 [0.072, 0.216], 0.0005 | 0.792, +0.110 [0.034, 0.186], 0.002 |
| C2+image+cnv_only | 0.843, +0.161 [0.086, 0.243], 0.0005 | 0.777, +0.095 [0.022, 0.171], 0.005 |
| C2+image+cnv_km | 0.848, +0.166 [0.088, 0.244], 0.0005 | 0.761, +0.080 [0.006, 0.156], 0.0125 |

Single modality arms vs C2 (Δ = arm − C2): WSI +0.050 [-0.080, +0.176], p 0.2179; CNV (release, PCA64 + RF) -0.018 [-0.152, +0.110], p 0.6237; CNV (Killcoyne method, elastic net) -0.041 [-0.174, +0.090], p 0.7611; Late fusion (mean, image + CNV release) +0.093 [-0.032, +0.212], p 0.0605; Late fusion (mean, image + CNV Killcoyne method) +0.083 [-0.047, +0.203], p 0.09.

**Method.** Same nested logistic as 3a; combinations fitted on training rows (C by inner folds). **Sources.** `results/paper_plan/followup_main.json` · `scripts/paper_plan/pf_main.py` · commit fef1089 (`F3`). **Caveats.** C2's `MaxPathologySoFar` includes the row's own grade; the L2 stack has two to three inputs and 570 training rows per fold.

### F4. Risk-group survival inconsistency
**Question.** Why do rates/ORs and hazard ratios disagree, and how is censoring time derived?

**Status.** DONE.

**Censoring derivation.** {'MonthsBeforeLastBiopsy_first_row_vs_days_first_to_max_NextBiopsyDate_spearman': 0.691, 'median_abs_diff_days': 720.4, 'patients_with_mbl_strictly_decreasing_along_rows': 19, 'patients_with_more_than_one_row': 124, 'reading': 'MonthsBeforeLastBiopsy is not consistently measured from each row (it decreases along rows for only part of the patients) and its first-row value does not equal the interval to the last NextBiopsyDate; version A (used in the paper-plan item 5) = first row + max MonthsBeforeLastBiopsy; version B = first row -> max NextBiopsyDate from biopsy dates'}. Non-progressor time (days): version A median 0.5 IQR [0.5, 1824.399]; version B median 856.0 IQR [721.75, 2323.75]. Progressor time median 1096.0 IQR [539.5, 2080.5].

| model (tertiles) | time version | groups: n, events, rate, median time progressors / non-progressors (d) | log-rank p | Cox HR high vs low | Cox HR moderate vs low | OR high vs low (Haldane) | figure |
|---|---|---|---|---|---|---|---|
| CNV (release, PCA64 + RF) | A | low: n 52, ev 10, rate 0.192, t_prog 1027.5, t_nonprog 0.5 / moderate: n 47, ev 17, rate 0.362, t_prog 898.0, t_nonprog 1258.103 / high: n 51, ev 23, rate 0.451, t_prog 1608.0, t_nonprog 1940.66 | 0.163 | [0.487, 0.228, 1.041] | [0.561, 0.253, 1.248] | 3.338 | `results/paper_plan/figs/km_v2/km_cnv_only_A.png` |
| CNV (release, PCA64 + RF) | B | low: n 52, ev 10, rate 0.192, t_prog 1027.5, t_nonprog 736.0 / moderate: n 47, ev 17, rate 0.362, t_prog 898.0, t_nonprog 1622.0 / high: n 51, ev 23, rate 0.451, t_prog 1608.0, t_nonprog 1947.5 | 0.932 | [0.873, 0.4, 1.907] | [0.954, 0.426, 2.137] | 3.338 | `results/paper_plan/figs/km_v2/km_cnv_only_B.png` |
| CNV (Killcoyne method, elastic net) | A | low: n 49, ev 13, rate 0.265, t_prog 839.0, t_nonprog 0.5 / moderate: n 49, ev 14, rate 0.286, t_prog 1102.0, t_nonprog 1468.121 / high: n 52, ev 23, rate 0.442, t_prog 1263.0, t_nonprog 1086.09 | 0.011 | [0.56, 0.281, 1.115] | [0.313, 0.143, 0.685] | 2.154 | `results/paper_plan/figs/km_v2/km_cnv_km_A.png` |
| CNV (Killcoyne method, elastic net) | B | low: n 49, ev 13, rate 0.265, t_prog 839.0, t_nonprog 729.0 / moderate: n 49, ev 14, rate 0.286, t_prog 1102.0, t_nonprog 1979.0 / high: n 52, ev 23, rate 0.442, t_prog 1263.0, t_nonprog 1166.0 | 0.127 | [0.798, 0.397, 1.604] | [0.471, 0.216, 1.023] | 2.154 | `results/paper_plan/figs/km_v2/km_cnv_km_B.png` |
| Late fusion (mean, image + CNV release) | A | low: n 51, ev 7, rate 0.137, t_prog 396.0, t_nonprog 0.5 / moderate: n 46, ev 12, rate 0.261, t_prog 1053.5, t_nonprog 548.295 / high: n 53, ev 31, rate 0.585, t_prog 1096.0, t_nonprog 1556.629 | 0.045 | [1.792, 0.788, 4.075] | [0.808, 0.312, 2.095] | 8.307 | `results/paper_plan/figs/km_v2/km_late_mean_A.png` |
| Late fusion (mean, image + CNV release) | B | low: n 51, ev 7, rate 0.137, t_prog 396.0, t_nonprog 768.5 / moderate: n 46, ev 12, rate 0.261, t_prog 1053.5, t_nonprog 1181.0 / high: n 53, ev 31, rate 0.585, t_prog 1096.0, t_nonprog 2248.5 | 0.012 | [2.515, 1.099, 5.751] | [1.136, 0.443, 2.91] | 8.307 | `results/paper_plan/figs/km_v2/km_late_mean_B.png` |
| Late fusion (mean, image + CNV Killcoyne method) | A | low: n 51, ev 7, rate 0.137, t_prog 2083.0, t_nonprog 0.5 / moderate: n 47, ev 15, rate 0.319, t_prog 999.0, t_nonprog 0.5 / high: n 52, ev 28, rate 0.538, t_prog 1096.0, t_nonprog 1556.629 | 0.183 | [2.222, 0.918, 5.379] | [1.724, 0.668, 4.449] | 6.902 | `results/paper_plan/figs/km_v2/km_late_mean_km_A.png` |
| Late fusion (mean, image + CNV Killcoyne method) | B | low: n 51, ev 7, rate 0.137, t_prog 2083.0, t_nonprog 754.0 / moderate: n 47, ev 15, rate 0.319, t_prog 999.0, t_nonprog 1089.0 / high: n 52, ev 28, rate 0.538, t_prog 1096.0, t_nonprog 2248.5 | 0.068 | [2.534, 1.103, 5.821] | [1.77, 0.721, 4.346] | 6.902 | `results/paper_plan/figs/km_v2/km_late_mean_km_B.png` |
| Clinical C2 (grade + max so far) [primary clinical] | A | low: n 57, ev 13, rate 0.228, t_prog 1225.0, t_nonprog 0.5 / moderate: n 44, ev 9, rate 0.205, t_prog 1545.0, t_nonprog 0.5 / high: n 49, ev 28, rate 0.571, t_prog 964.0, t_nonprog 2098.171 | 0.559 | [1.246, 0.645, 2.407] | [0.835, 0.343, 2.029] | 4.37 | `results/paper_plan/figs/km_v2/km_C2_grade_maxsofar_A.png` |
| Clinical C2 (grade + max so far) [primary clinical] | B | low: n 57, ev 13, rate 0.228, t_prog 1225.0, t_nonprog 744.0 / moderate: n 44, ev 9, rate 0.205, t_prog 1545.0, t_nonprog 763.0 / high: n 49, ev 28, rate 0.571, t_prog 964.0, t_nonprog 3008.0 | 0.129 | [1.82, 0.928, 3.572] | [1.034, 0.44, 2.434] | 4.37 | `results/paper_plan/figs/km_v2/km_C2_grade_maxsofar_B.png` |

Discovery-stratum rates only (case–control design; time not interpretable): {"cnv_only": {"low": {"n": 12, "events": 7, "rate": 0.583}, "moderate": {"n": 31, "events": 13, "rate": 0.419}, "high": {"n": 39, "events": 20, "rate": 0.513}}, "cnv_km": {"low": {"n": 14, "events": 9, "rate": 0.643}, "moderate": {"n": 31, "events": 10, "rate": 0.323}, "high": {"n": 37, "events": 21, "rate": 0.568}}, "late_mean": {"low": {"n": 21, "events": 7, "rate": 0.333}, "moderate": {"n": 26, "events": 10, "rate": 0.385}, "high": {"n": 35, "events": 23, "rate": 0.657}}, "late_mean_km": {"low": {"n": 21, "events": 7, "rate": 0.333}, "moderate": {"n": 26, "events": 12, "rate": 0.462}, "high": {"n": 35, "events": 21, "rate": 0.6}}, "C2_grade_maxsofar": {"low": {"n": 19, "events": 7, "rate": 0.368}, "moderate": {"n": 19, "events": 7, "rate": 0.368}, "high": {"n": 44, "events": 26, "rate": 0.591}}}. in the Killcoyne discovery stratum controls were selected on >= 3 y follow-up (matched case-control), so censoring time is a selection criterion, not an outcome; for that stratum only rates and ORs are reported.

Probability deciles (patient max score, 0–100 % in steps of 10): {'cnv_only': [0.034, 0.134, 0.165, 0.195, 0.213, 0.237, 0.271, 0.29, 0.316, 0.352, 0.441], 'cnv_km': [0.0, 0.092, 0.111, 0.128, 0.141, 0.153, 0.182, 0.249, 0.312, 0.503, 1.0], 'late_mean': [0.058, 0.19, 0.235, 0.282, 0.328, 0.37, 0.417, 0.464, 0.502, 0.561, 0.675], 'late_mean_km': [0.087, 0.163, 0.199, 0.258, 0.307, 0.354, 0.413, 0.456, 0.491, 0.599, 0.989]}. Killcoyne fixed classes applied to the Killcoyne-method arm: {'low': {'n': 118, 'events': 31, 'rate': 0.263}, 'moderate': {'n': 16, 'events': 6, 'rate': 0.375}, 'high': {'n': 16, 'events': 13, 'rate': 0.812}}.

**Sources.** `results/paper_plan/followup_main.json` · `scripts/paper_plan/pf_main.py` · commit fef1089 (`F4`); figures `results/paper_plan/figs/km_v2/`. **Caveats.** Non-progressor follow-up ends at the last biopsy in the release tables; progressor time is to the endpoint biopsy; both versions share the progressor times.

### F5. False positives: confounding and label check
**Question.** Is the FP excess of later disease explained by baseline grade, and are any "non-progressors" with later HGD+ mislabelled?

**Status.** DONE.

**Adjusted logistic regression among non-progressors** (later outcome ~ FP + baseline grade + max grade so far; statsmodels Logit, Wald CIs).

| model | FP / TN | later HGD+: OR FP adjusted [CI], p (unadjusted OR) | later LGD+: OR FP adjusted [CI], p (unadjusted OR) |
|---|---|---|---|
| Late fusion (mean, image + CNV release) | 40 / 60 | 5.290 [1.466, 19.086], p 0.011 (5.310) | 2.569 [0.875, 7.546], p 0.086 (2.466) |
| WSI | 50 / 50 | 3.185 [0.893, 11.362], p 0.074 (3.244) | 1.499 [0.517, 4.348], p 0.456 (1.481) |
| CNV (release, PCA64 + RF) | 55 / 45 | 5.880 [1.215, 28.447], p 0.028 (6.655) | 5.570 [1.464, 21.193], p 0.012 (5.744) |
| clinical_3a | 38 / 62 | 4.211 [1.137, 15.590], p 0.031 (4.071) | 4.556 [1.411, 14.712], p 0.011 (3.626) |
| v4_exploratory | 26 / 74 | 5.588 [1.583, 19.724], p 0.007 (6.000) | 3.368 [1.067, 10.629], p 0.038 (3.388) |
| Clinical C2 (grade + max so far) [primary clinical] | 56 / 44 | 1.307 [0.345, 4.946], p 0.694 (1.696) | 0.938 [0.291, 3.027], p 0.915 (1.100) |
| CNV (Killcoyne method, elastic net) | 66 / 34 | 8.520 [1.047, 69.329], p 0.045 (8.885) | 5.757 [1.219, 27.186], p 0.027 (5.551) |
| Late fusion (mean, image + CNV Killcoyne method) | 39 / 61 | 3.680 [1.051, 12.886], p 0.042 (3.862) | 1.991 [0.662, 5.993], p 0.221 (1.992) |

**Within baseline-NDBE non-progressors.**

| model | FP | TN | later HGD+ FP / TN | Fisher p | later LGD+ FP / TN | Fisher p |
|---|---|---|---|---|---|---|
| Late fusion (mean, image + CNV release) | 31 | 57 | [10, 4] | 0.004 | [10, 8] | 0.055 |
| WSI | 39 | 49 | [10, 4] | 0.039 | [10, 8] | 0.301 |
| CNV (release, PCA64 + RF) | 47 | 41 | [12, 2] | 0.009 | [15, 3] | 0.007 |
| clinical_3a | 28 | 60 | [9, 5] | 0.01 | [11, 7] | 0.005 |
| v4_exploratory | 21 | 67 | [8, 6] | 0.004 | [8, 10] | 0.031 |
| Clinical C2 (grade + max so far) [primary clinical] | 44 | 44 | [9, 5] | 0.383 | [10, 8] | 0.792 |
| CNV (Killcoyne method, elastic net) | 55 | 33 | [13, 1] | 0.014 | [16, 2] | 0.013 |
| Late fusion (mean, image + CNV Killcoyne method) | 30 | 58 | [9, 5] | 0.014 | [9, 9] | 0.162 |

**Non-progressors with later HGD+** (n 15): days after the last release row median [IQR] [1607.5, 1196.5, 2400.25]; sources {'db_report+hgd_table': 8, 'db_report': 4, 'db_report+release_excluded_row+slide_matching+hgd_table': 1, 'db_report+slide_matching+hgd_table': 1, 'slide_matching': 1}; with release-excluded rows 3 ({'': 12, 'at_event': 2, 'endpoint_not_evaluable': 1}); **flagged as the next release biopsy (would be progressors): 1**. the endpoint is evaluated on the NEXT biopsy after each strict pre-event row; a later HGD+ report that is not that next biopsy (later surveillance, or after an endpoint-not-evaluable gap) does not enter the release label. Patient list `feasibility/paper_plan/f5_later_hgd_nonprogressors.csv` (cluster).

**LGD+/HGD+ count check.** late_mean: {'FP_later_LGDplus_n': 11, 'FP_later_HGDplus_n': 11, 'FP_max_later_grade_counts': {'0.0': 24, '4.0': 7, '3.0': 4, 'NaN': 3, '1.0': 2}, 'definition': 'LGD+ = max later grade >= 2 (LGD/HGD/IMC); HGD+ = max later grade >= 3 or an hgd_table entry; identical counts mean every FP with a later LGD+ also reached HGD+'}; image_only: {'FP_later_LGDplus_n': 11, 'FP_later_HGDplus_n': 11, 'FP_max_later_grade_counts': {'0.0': 33, '4.0': 6, '3.0': 5, 'NaN': 4, '1.0': 2}, 'definition': 'LGD+ = max later grade >= 2 (LGD/HGD/IMC); HGD+ = max later grade >= 3 or an hgd_table entry; identical counts mean every FP with a later LGD+ also reached HGD+'}.

**Sources.** `results/paper_plan/followup_main.json` · `scripts/paper_plan/pf_main.py` · commit fef1089 (`F5`). **Caveats.** Later grades are DB confirmed codes; 100 non-progressors with ~15 later HGD+ events give wide CIs; adjustment covariates are coarse ordinal grades.

### F6. Attention and tile sampling
**Question.** How concentrated is attention, does tile count drive image-only performance, and how much do 256-tile draws move patient scores?

**Status.** DONE (F6c retrained with a scale change, labelled).

**Attention mass** (held-out rows):

| model | rows | top-5 % (13 tiles) mass median [IQR] | top-10 % mass median [IQR] | uniform | max weight median (uniform 1/256 = 0.004) | rows with top-5 % mass < 0.06 |
|---|---|---|---|---|---|---|
| image_only | 707 | 0.158 [0.11, 0.213] | 0.267 [0.2, 0.342] | 0.05 / 0.10 | 0.017 | 0.001 |
| intermediate_fusion | 707 | 0.173 [0.127, 0.237] | 0.286 [0.221, 0.379] | 0.05 / 0.10 | 0.02 | 0.0 |
| coattention_fusion | 707 | 0.085 [0.064, 0.128] | 0.157 [0.124, 0.22] | 0.05 / 0.10 | 0.008 | 0.173 |

**F6a: image-only by tiles-kept tertile** (patient mean of `kept_tiles` at 0.44 µm/px):

| tertile | tiles kept range | n | events | image-only AUROC [CI] | late_mean | cnv_only |
|---|---|---|---|---|---|---|
| T1_low | [289.0, 1170.0] | 50 | 28 | 0.614 [0.443, 0.776] | 0.666 | 0.544 |
| T2 | [1173.0, 3886.0] | 50 | 18 | 0.655 [0.463, 0.832] | 0.675 | 0.601 |
| T3_high | [3917.5, 7811.0] | 50 | 4 | 0.582 [0.288, 0.816] | 0.647 | 0.652 |

**F6c: image-only retrained on 0.44 µm/px UNI2-h bags, ≤2,048 tiles** (release ABMIL config, release folds, epochs per fold {'1': 10, '2': 5, '3': 10, '4': 5, '5': 8}, seed 0): AUROC 0.675 [0.580, 0.769] (n 150, events 50); Δ vs release image-only -0.056 [-0.115, +0.004]. single seed 0; scale 0.44 um/px vs release 0.88 um/px; tiles capped at 2,048 random per slide (seed 0).

**F6b: 10 random 256-tile draws through the F6c fold models.** Patient-score SD across draws median 0.005 IQR [0.003, 0.007] max 0.028; AUROC per draw [0.676, 0.675, 0.676, 0.669, 0.671, 0.675, 0.675, 0.675, 0.669, 0.674] (full bags 0.675); patients changing class across draws 7 of 150 (threshold per fold {'1': 0.177, '2': 0.139, '3': 0.181, '4': 0.111, '5': 0.141}); the 11 late_mean FN patients were predicted positive in [0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0] of 10 draws (score SD [0.003, 0.004, 0.002, 0.003, 0.002, 0.008, 0.002, 0.006, 0.004, 0.004, 0.002]).

**Sources.** `results/paper_plan/followup_main.json` · `scripts/paper_plan/pf_main.py` · commit fef1089 (`F6_cpu`); `results/paper_plan/f6_image_tiles.json` · `scripts/paper_plan/pf_gpu.py` · commit fef1089; checkpoints `feasibility/paper_plan/f6c_image05_fold*.pt`. **Caveats.** F6c changes tile scale and tile count at once; single training seed; F6b draws are of 0.44 µm tiles through the F6c model, not of the release model.

### F7. Does fusion actually use CNV?
**Question.** How much does each learned fusion model lose when its CNV input, or its image input, is destroyed?

**Status.** DONE.

| model | baseline AUROC | CNV permuted jointly: Δ mean (SD over 50), [CI of mean-permuted] | CNV → training mean: Δ [CI] | image bags permuted: Δ mean (SD), [CI] | image → mean tile: Δ [CI] |
|---|---|---|---|---|---|
| image_only | 0.731 | — | — | +0.259 (0.041) [0.153, 0.373] | +0.231 [0.097, 0.361] |
| early_fusion | 0.738 | +0.122 (0.028) [-0.006, +0.108] | +0.064 [0.007, 0.123] | +0.165 (0.028) [0.042, 0.198] | +0.082 [0.016, 0.154] |
| intermediate_fusion | 0.741 | +0.076 (0.02) [-0.025, +0.082] | +0.038 [-0.016, +0.096] | +0.205 (0.037) [0.042, 0.246] | +0.125 [0.021, 0.231] |
| coattention_fusion | 0.739 | +0.081 (0.028) [-0.022, +0.081] | +0.025 [-0.029, +0.078] | +0.200 (0.038) [0.085, 0.250] | +0.170 [0.094, 0.249] |

**8b noise floor** (one random 5-Mb window feature permuted, 10 windows × 50 repeats × 5 folds): cnv_only: mean 0.002, SD 0.023, 95th pct 0.045, 99th 0.085; early_fusion: mean -0.0, SD 0.002, 95th pct 0.0, 99th 0.005; intermediate_fusion: mean 0.0, SD 0.003, 95th pct 0.005, 99th 0.01; coattention_fusion: mean 0.0, SD 0.004, 95th pct 0.005, 99th 0.01. Per-fold arm importances (mean of 10 repeats per fold) are in the JSON (`_8b_noise_floor.<model>.arm_features_per_fold_delta_auroc_mean_of_10_repeats`).

**Method.** held-out rows per fold; ablations: CNV rows permuted jointly (50 repeats) or replaced by the standardised training mean (zeros); image bags permuted across rows (50 repeats) or replaced by the training-fold mean tile; delta = baseline patient AUROC minus ablated; CI from patient bootstrap of (baseline, mean ablated score); noise floor = permuting one of 10 random 5-Mb window features, 50 repeats, per fold. **Sources.** `results/paper_plan/f7_modality_ablation.json` · `scripts/paper_plan/pf_gpu.py` · commit fef1089. **Caveats.** Two different quantities are shown for the permutation ablations: the mean over 50 repeats of the per-repeat ΔAUROC, and the ΔAUROC of the score averaged over the 50 permutations (whose CI is given); averaging permuted scores removes part of the damage, so the second is smaller. Replacing CNV by the training mean is a single deterministic ablation; the image ablation for early fusion replaces the mean-pooled bag.

### F8. Latent space: small follow-ups
**Question.** Are the probes really above the models' own outputs, and do the projections hold across folds?

**Status.** DONE.

| representation | probe AUROC | model OOF AUROC | Δ probe − model [CI] | n / events |
|---|---|---|---|---|
| image_only | 0.784 | 0.731 | +0.053 [-0.015, +0.121] | 150 / 50 |
| early_fusion | 0.822 | 0.738 | +0.084 [0.006, 0.163] | 150 / 50 |
| intermediate_fusion | 0.819 | 0.741 | +0.077 [0.019, 0.140] | 150 / 50 |
| coattention_fusion | 0.736 | 0.739 | -0.003 [-0.100, +0.093] | 150 / 50 |

**Training-fold vs held-out AUROC per fold (model outputs, patient level).**

| family | fold | training AUROC (n patients) | held-out AUROC (n patients) |
|---|---|---|---|
| image_only | 1 | 0.943 (120) | 0.525 (30) |
| image_only | 2 | 0.864 (120) | 0.875 (30) |
| image_only | 3 | 0.922 (120) | 0.755 (30) |
| image_only | 4 | 0.866 (120) | 0.73 (30) |
| image_only | 5 | 0.913 (120) | 0.88 (30) |
| early_fusion | 1 | 0.999 (120) | 0.67 (30) |
| early_fusion | 2 | 0.948 (120) | 0.935 (30) |
| early_fusion | 3 | 0.947 (120) | 0.77 (30) |
| early_fusion | 4 | 0.973 (120) | 0.8 (30) |
| early_fusion | 5 | 0.938 (120) | 0.795 (30) |
| intermediate_fusion | 1 | 0.978 (120) | 0.555 (30) |
| intermediate_fusion | 2 | 0.984 (120) | 0.83 (30) |
| intermediate_fusion | 3 | 0.969 (120) | 0.825 (30) |
| intermediate_fusion | 4 | 0.906 (120) | 0.815 (30) |
| intermediate_fusion | 5 | 0.899 (120) | 0.76 (30) |
| coattention_fusion | 1 | 0.962 (120) | 0.64 (30) |
| coattention_fusion | 2 | 0.934 (120) | 0.84 (30) |
| coattention_fusion | 3 | 0.936 (120) | 0.72 (30) |
| coattention_fusion | 4 | 0.934 (120) | 0.74 (30) |
| coattention_fusion | 5 | 0.89 (120) | 0.835 (30) |

Five-fold PCA/UMAP figures (projection fitted on each fold's training patients; held-out patients shown; rings = also_in_ERIN): `results/paper_plan/figs/latent_folds/image_only_pca_umap_5folds.png`, `results/paper_plan/figs/latent_folds/cnv_only_pca_umap_5folds.png`, `results/paper_plan/figs/latent_folds/early_fusion_pca_umap_5folds.png`, `results/paper_plan/figs/latent_folds/intermediate_fusion_pca_umap_5folds.png`, `results/paper_plan/figs/latent_folds/coattention_fusion_pca_umap_5folds.png`.

**Method.** probe: L2 logistic on patient-mean row embeddings, standardised and C-tuned (release inner folds) on training patients, applied to held-out patients (same procedure and seed as pp_latent.py); model output: release OOF, patient max; paired patient bootstrap; projections fitted on each fold's training patients. **Sources.** `results/paper_plan/f8_probe_vs_output.json` · `scripts/paper_plan/pf_latent_figs.py` · commit fef1089; `results/paper_plan/f8_train_vs_heldout.json` · `scripts/paper_plan/pf_gpu.py` · commit fef1089. **Caveats.** The probe is a second model fitted on top of the fusion embedding with its own inner CV; the comparison is probe-on-embedding vs the network's own head.

### F9. Housekeeping
**Status.** DONE.

**Page mapping.** `pdftotext` page N of `s41591-020-1033-y.pdf` = journal page 1725 + N for N ≤ 9 (Letters 1726–1732, Methods 1733–1734); N = 10–24 are Extended Data Figs 1–10 (online only, no journal page). Revised references for the item-1 table in `docs/paper_plan_answers.md`: abstract and Fig 1 legend → p.1726–1727; risk classes and validation paragraph → p.1727; Methods (cohorts, sequencing 0.4× HiSeq, QDNAseq 50-kb, elastic net, LOPO, endpoint) → p.1733; Ext Data Fig 2 (aggregation) and Fig 9 (bin size / penalty, AUC 0.87 / 0.84) → online Extended Data; supplementary `MOESM15` Ext Data Fig 9c → 50 kb discovery AUC 0.865 [0.839, 0.891].

**Non-inferiority (pre-specified margin −0.05 AUROC).** WSI − CNV (release RF): +0.068 [-0.065, +0.196], lower bound above margin: False. WSI − CNV (Killcoyne method): +0.091 [-0.031, +0.215], lower bound above margin: True. (n 150, 50 events.)

**Sources.** `results/paper_plan/followup_main.json` · `scripts/paper_plan/pf_main.py` · commit fef1089 (`F9_noninferiority`); `f1_cnv_killcoyne.json` (`subsets.*.item2_*`). **Caveats.** The margin was chosen for this follow-up, not in the original paper plan.

## 4. Updated filled whiteboard table (SWG)

|  | SWG progressor cohort (n 150, 50 progressors): AUROC [CI] · AUPRC [CI] | ACE-B |
|---|---|---|
| Clinical C2 (grade + max so far) [primary clinical] | 0.681 [0.582, 0.776] · 0.498 [0.373, 0.643] | NOT AVAILABLE |
| CNV (release, PCA64 + RF) | 0.663 [0.569, 0.754] · 0.538 [0.411, 0.671] | NOT AVAILABLE |
| CNV (Killcoyne method, elastic net) | 0.640 [0.538, 0.734] · 0.569 [0.436, 0.694] | NOT AVAILABLE |
| WSI | 0.731 [0.640, 0.814] · 0.557 [0.426, 0.717] | NOT AVAILABLE |
| Early fusion | 0.738 [0.646, 0.818] · 0.590 [0.453, 0.733] | NOT AVAILABLE |
| Intermediate fusion | 0.741 [0.653, 0.818] · 0.567 [0.435, 0.714] | NOT AVAILABLE |
| Late fusion (mean, image + CNV release) | 0.774 [0.687, 0.849] · 0.630 [0.490, 0.772] | NOT AVAILABLE |
| Late fusion (mean, image + CNV Killcoyne method) | 0.764 [0.672, 0.843] · 0.626 [0.489, 0.762] | NOT AVAILABLE |
| Co-attention fusion (extra) | 0.739 [0.652, 0.821] · 0.548 [0.428, 0.703] | NOT AVAILABLE |
| Late stack-logit (extra) | 0.737 [0.648, 0.814] · 0.530 [0.412, 0.684] | NOT AVAILABLE |

Source: `results/paper_plan/followup_main.json` (`F3.table_all_150`), commit fef1089.

## 5. Discrepancies found
1. The Killcoyne-method arm does not recover the CNV signal: on the 82 discovery patients it scores 0.580 against the release RF 0.564 and the published LOPO predictions 0.718, and its agreement with the published probabilities (0.243) is no higher than the RF's (0.278). Both of our CNV models are trained on our LGD2+ labels; the published predictions were trained on their HGD/IMC case–control labels, which disagree with ours for 11 of the 82 patients (paper plan item 0). The difference is therefore in labels and cohort design, not in the model class.
1b. Design stratum alone predicts our label with AUROC 0.752 [0.647, 0.849]: 34 of 39 Killcoyne discovery cases and 6 of 43 discovery controls are our progressors, while the validation-sheet stratum has 10 events in 68 patients (F2). Within the discovery-control stratum the CNV arms score below 0.5.
2. Killcoyne fixed classes place no release-RF patient in the high class because the RF probabilities never reach 0.5 (deciles in F4); the classes were designed for a logistic-regression probability scale.
3. The paper-plan item-5 censoring time (version A) does not equal the biopsy-date interval (version B) for most non-progressors (F4 censoring derivation).
4. Clinical arm 3a's advantage over C2 comes from features that encode the endpoint rule or surveillance history (F3, C1→C4).
5. Later-HGD+ non-progressors flagged as the next release biopsy: 1 (F5); if > 0 these are label discrepancies in the release.

## 6. Not done
- glmnet itself (R) was not run; the elastic net is the sklearn saga implementation.
- F6c uses 0.44 µm/px features (the only multi-tile pool available), so tile count and scale change together; a 0.88 µm/px multi-tile re-extraction was not done. F6c scored below the release image arm, so the tile-count hypothesis is not supported by this test but is not isolated by it either.
- ACE-B: no data.

## 7. Pre-specification text as committed at `0db4075` (verbatim)

> # BE paper plan follow-up (F1–F9)
>
> **Status of this file: PRE-SPECIFICATION VERSION**, committed before any analysis in it was run. Results are appended in
> later commits; the specification text below is not edited afterwards (changes, if any, are added beside it with both results).
>
> ## 1. Header (completed at the results commit)
> - Date: 25–26 September 2026. Commit at start: `38a83f2`. Pre-specification commit: the commit adding this text. Inputs: frozen release `chapter1_lgd2_final_pre_event_20260713_final` only; `docs/paper_plan_answers.md` and `results/paper_plan/*` (commit `98ed676`); `results/closeout/*` (commit `602a40e`); Killcoyne 2020 PDF and supplementary xlsx on the cluster.
> - Planned scripts (`scripts/paper_plan/`): `pf_cnv_killcoyne.py` (F1), `pf_main.py` (F2–F5, F9, F6a, F8 tables), `pf_gpu.py` (F6b/F6c image retrain and resampling, F7 ablations and 8b noise floor, F8 train-vs-held-out), `pf_latent_figs.py` (F8 five-fold figures), `pf_render.py`.
> - Conventions as before: patient = max over strict pre-event rows; rank AUROC/AUPRC to 3 decimals; 2,000 patient bootstraps `RandomState(0)`; 2,000 patient-label permutations `RandomState(0)`; every fitted quantity fitted on the four training outer folds (inner CV on the release's patient-keyed inner folds) and applied to the held-out fold.
>
> ## Pre-specifications
>
> ### F1. Killcoyne-method CNV arm
> - Their method (Nat Med 26:1733, Methods "Statistical methods"): per-sample weighted mean of segmented CN per 5-Mb window; mean-standardised per window across the cohort; arm means, and each window adjusted by window − arm difference; "589 5-Mb windows and 44 chromosome arms" plus cx; elastic-net logistic regression (glmnet), 5-fold patient-level CV repeated 10×; penalty α tuned in [0, 1] and **0.9 selected** ("limited the number of non-zero coefficients (n = 74) and was not full lasso (for example, 0.9)"); λ by cross-validation; leave-one-patient-out predictions for the discovery cohort (p.1733; Extended Data Fig 9b legend, p.1735+).
> - Our implementation: features = the release's `features_5mb_armdiff` (the window-minus-arm features, 587 windows) + `features_arms` (39 arms) + `cx` (the release's own encoding of the same construction; the release has fewer windows/arms than the paper because it drops empty/sex-chromosome columns, stated as such). Standardisation: per-feature mean/sd on the outer training rows (fold-honest version of "across the entire cohort"); median imputation on training rows. Model: `sklearn.linear_model.LogisticRegression(penalty="elasticnet", solver="saga", l1_ratio=0.9, max_iter=20000, class_weight=None)`; C ∈ {0.01, 0.03, 0.1, 0.3, 1, 3, 10} chosen per outer fold by the release inner folds (criterion: patient-level AUROC, max over rows). Trained on our endpoint `y_progressor` (rows), release outer folds `fold_id_rep01`. Sensitivity (secondary): α ∈ {0.1, 0.5, 0.9} also tuned by inner CV.
> - Report next to `cnv_only`: AUROC/AUPRC with CIs on all 150, never_in_ERIN 96, also_in_ERIN 54, Killcoyne-discovery 82, other 68. Faithfulness check: Spearman of our arm's OOF row scores vs the published LOPO probabilities on the 500 matched rows (`MOESM4` Fig 2a sheet), and vs cnv_only. Rerun item 2 (WSI vs "CNV (Killcoyne method)") and item 4 (late fusion = plain mean of image_only and the F1 arm probabilities, labelled `late_mean_km`; paired deltas vs WSI and vs each CNV arm; learned fusions not retrained).
> - Diagnosis of `cnv_only` on the 25 overlap-discovery patients: per-fold patient AUROC restricted to them (where both classes present); their outer training folds' class balance; standardised-feature distributions (mean |z| over the arm features and cx; PCA-64 score norms) for them vs the other 125 (Mann-Whitney); RF probability distribution.
>
> ### F2. Cohort design heterogeneity
> - Stratum per patient: Killcoyne-discovery case (any row's CNV id in the 777 sheet and sheet Status P), Killcoyne-discovery control (sheet Status NP), validation sheet (268 sheet), other (neither). Patients with rows in both sheets take the discovery stratum. Cross-tab vs also/never_in_ERIN.
> - Main table (all arms incl. F1 and F3 C1–C4) within each stratum with ≥ 5 events and ≥ 20 patients; n and events stated.
> - Within discovery stratum: progressors vs non-progressors on age at diagnosis, sex, Prague M/C, follow-up (months first→last biopsy) — Mann-Whitney / Fisher; coverage stated.
> - Stratum-only score (stratum progression rate from training folds, applied to held-out) AUROC with CI; per arm, Mann-Whitney of patient scores by stratum among non-progressors (discovery vs validation).
>
> ### F3. Clinical arm without endpoint-definition features
> - Nested versions, same model/folds as 3a (L2 logistic, inner-CV C, standardisation on training rows, patient max): C1 = row grade; C2 = grade + `MaxPathologySoFar` (**primary clinical arm**); C3 = C2 + `LGDStreakSoFar`; C4 = C3 + `BiopsyIndex`, `DaysSincePreviousBiopsy`, year (= 3a).
> - Does a modality add to C2: combinations C2 + image, C2 + cnv_only, C2 + F1 CNV, C2 + late_mean, C2 + image + cnv_only, via (i) fold-z mean and (ii) an L2 logistic stack on the logits of the row scores fitted on the outer training rows (C by inner CV); paired ΔAUROC vs C2 with CI and permutation p. 3b moves to the supplement.
>
> ### F4. Risk-group survival inconsistency
> - Per group and model (cnv_only, late_mean tertiles): median time-at-risk for progressors and non-progressors separately; derivation of the censoring time checked against the release columns (`MonthsBeforeLastBiopsy` measured from the row vs from the first row: compare its value at the first row with the interval first row → max `NextBiopsyDate`).
> - Version B: non-progressor time = earliest row → last known biopsy date computed from biopsy dates (max of `NextBiopsyDate` over the patient's rows; falls back to the last row date). Progressor time unchanged. KM/log-rank/Cox for both versions.
> - Interpretability statement for the matched case–control stratum (controls selected on ≥ 3 y follow-up): time-to-event not interpretable there; rates and ORs only.
> - Probability distributions (deciles) of cnv_only, F1 arm, late_mean; Killcoyne fixed classes applied to the F1 arm.
>
> ### F5. False positives: confounding and label check
> - Logistic regression of later HGD+ (and later LGD+) on FP status among non-progressors, adjusted for baseline grade (earliest row) and max grade so far (max over rows); ORs with profile-likelihood-free Wald CIs (statsmodels if available, else sklearn unpenalised + bootstrap CI); per model incl. C2. Repeat FP vs TN within baseline-NDBE non-progressors.
> - List every non-progressor with later HGD+: days from last release row, source, and why not a release progressor (endpoint rule requires the *next* biopsy after a pre-event row to be HGD+ or a second consecutive LGD; later events beyond the last release row or after a non-evaluable gap do not enter). Flag those whose later HGD+ is the *next* biopsy after a release row (would be progressors).
> - LGD+ definition check: list grades behind the later LGD+ and HGD+ counts for late_mean and image_only FPs.
>
> ### F6. Attention and tile sampling
> - Attention mass on the top 5 % (13 tiles) and 10 % (26 tiles) per model vs uniform (0.05, 0.10); co-attention vs mean pooling: Spearman of co-attention weights with uniform is undefined, so report the per-row max weight and the fraction of rows whose top-5 % mass < 0.06.
> - F6a: image_only AUROC by patient tertile of mean tiles kept (0.5 µm h5 `kept_tiles`), with CIs.
> - F6b/F6c (GPU, `pf_gpu.py`): F6c = ABMIL with the release image config (hidden 256, attn 128, dropout 0.1, Adam lr 1e-4, wd 0.01, batch 8), trained per outer fold on the 0.44 µm/px UNI2-h bags (`features_uni2h_05um`, all tiles up to 2,048 per bag, random subsample per epoch when larger, seed 0), fixed epochs = the release fold's `final_epochs`; labelled "image-only, 0.44 µm/px, ≤2,048 tiles" (a scale change from the release's 0.88 µm/px 256 tiles; stated). F6b = the F6c fold model applied to 10 random 256-tile draws (seeds 0–9) of each held-out slide: SD of patient scores across draws, and for the late_mean FN patients whether the F6c prediction (training-fold threshold at sens ≥ 0.80) changes across draws.
>
> ### F7. Does fusion use CNV?
> - Per learned fusion model, held-out rows: (a) permute all CNV features jointly across held-out rows, 50 repeats; (b) replace CNV input by the training-fold mean (standardised zero vector); image: (a) permute bags across held-out rows, 50 repeats; (b) replace the bag by a single tile equal to the training-fold mean tile embedding. ΔAUROC (patient level) with patient-bootstrap CI (bootstrap over patients of the per-patient permuted-vs-baseline scores, 2,000).
> - 8b noise floor: ΔAUROC when one randomly chosen 5-Mb window feature is permuted (10 windows × 50 repeats, seed 0), and per-fold values with SD for the arm features.
>
> ### F8. Latent space follow-ups
> - Paired difference (patient level) between the linear-probe AUROC and the model's own OOF AUROC for early and intermediate fusion, with CI; per fold training-fold vs held-out AUROC of the model outputs. PCA/UMAP figures for all five folds (projection fitted on each fold's training patients).
>
> ### F9. Housekeeping
> - Page mapping: pdftotext page N = journal page 1725 + N for N ≤ 9 (1726–1734); N ≥ 10 = Extended Data Figs 1–10 (online). Non-inferiority margin for WSI − CNV: **−0.05 AUROC**, pre-specified here; report the lower CI bound against it for both CNV arms.
>
> (Results follow in the results commit.)
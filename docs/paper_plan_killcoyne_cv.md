# Killcoyne protocol with imaging: stratified repeated CV, the LOPO artefact, grade, frozen package-feature models

Status: PRE-SPECIFICATION. Nothing below has been run. Results are appended in a later commit; this section is not edited afterwards.

Fixed as before (`docs/paper_plan_killcoyne_multimodal.md` 3904c44; `docs/paper_plan_killcoyne_checks.md` 828ebf7): set C (676 samples, 80 patients, 37 P), label = sheet Status per sample, glmnet α 0.9 with standardize = FALSE, their shipped CNV matrix and package features as the two CNV sources, UNI2 slide-mean image block, metrics (rank AUROC, 3 decimals; patient = max over samples), patient-bootstrap CI (2,000, `RandomState(0)`), paired within-patient swap permutation (2,000, seed 0, two-sided), subsets as in the checks (NDBE only; before the first HGD/IMC; both).

## 1. Stratified repeated patient-grouped CV

- Outer folds: for repeat s = 1..10, `set.seed(s)`; P patients shuffled, then NP patients shuffled, concatenated (P first) and assigned fold = 1..10 cyclically, so every fold has 8 patients and 3–4 P patients.
- For each outer fold: training = the other 9 folds. Image block z-scored on the training rows (fold-honest); CNV blocks as before (their matrix as shipped; package block as exported for set C). λ = class-error min from the same inner 10 × 5 patient-grouped CV on the training patients (`set.seed(r)`, r = 1..10). Predictions for the held-out fold.
- Each sample gets one out-of-fold prediction per repeat; the arm's score is the mean over the 10 repeats.
- Arms: L-CNV, L-IMG, L-EARLY and L-LATE (mean of L-CNV and L-IMG probabilities within each repeat), for both CNV sources (L-IMG shared).
- Reported on all of set C, NDBE only, before the first HGD/IMC, and both: per-sample and patient-max AUROC with CI; Δ vs L-CNV (same source) with paired CI and p. The LOPO values (fold-honest image scaling, from the checks) alongside.

## 2. The LOPO artefact

- For each arm (item 1 arms and the item 3 grade arms): the correlation (Pearson, point-biserial; and Spearman) across the 80 patients between the patient's label and the intercept of the model that scored the patient. Under LOPO, the intercept is recovered by refitting the LOPO training set at the λ already chosen for that patient (deterministic; no new selection). Under the stratified CV, the patient's intercept is the mean over repeats of the intercept of the fold model that scored the patient.
- Intercept-only model: the prediction for a held-out sample is the training-row prevalence (the maximum-likelihood intercept-only logistic model). Per-sample AUROC under LOPO and under the stratified CV (mean over repeats), on all four subsets.

## 3. Grade arms under the stratified CV

L-GRADE (grade + constant zero column), L-CNV+GRADE, L-EARLY+GRADE, and L-LATE with grade (mean of L-CNV+GRADE and L-IMG), both CNV sources, under the item 1 CV with fold-honest image scaling (this departs from the checks, which used whole-set image scaling for the grade arms). Raw grade (ordinal NDBE 0, ID 1, LGD 2, HGD 3, IMC 4) as a score with no model. Reported on all of set C and NDBE only: every arm's AUROC; Δ of L-EARLY+GRADE and of L-LATE with grade vs L-CNV+GRADE, with CI and p. On NDBE only, raw grade is constant (AUROC 0.5 by construction).

## 4. Frozen package-feature models and the ACE-B primary analysis

- L-CNV, L-IMG, L-EARLY on package features refitted once on all of set C; L-LATE = mean of frozen L-CNV and L-IMG probabilities. Scaling fitted on set C: package tile, arm and cx means and s.d. over set C (hg38 tiles from `kr_package.R`), image means and s.d. over set C. λ = class-error min of the inner 10 × 5 CV on all of set C. Committed under `models/killcoyne_frozen_pkg_v1/` with coefficients, all scaling constants, the tile and arm lists, the arm–tile incidence, UNI2 extraction settings, software versions, and a SHA-256 manifest.
- A one-page ACE-B primary analysis, `docs/aceb_primary_killcoyne.md`: L-LATE (package) vs L-CNV (package), per-sample AUROC, NDBE samples only, one-sided in favour of fusion, patient-bootstrap CI; everything else secondary; the bundle hash. An amendment line in `docs/aceb_analysis_plan.md` points to it.

## Status and outputs

Each item DONE / PARTIAL / NOT AVAILABLE; at most one line of interpretation. Scripts `scripts/paper_plan/kv_cv.R` (items 1, 3; sharded by model and repeat), `kv_lopo_intercepts.R` (item 2 LOPO refits), `kv_freeze.R` + `kc_freeze_manifest.py` (item 4), `kv_merge.py`, `kv_render.py`. Results `results/paper_final/killcoyne_cv.json`. Row-level outputs on the cluster under `feasibility/paper_plan/killcoyne_mm/cv/`. Small jobs raced on epyc, rocm, cuda and h200; merges as Slurm jobs.

---

## Results

Sources: `results/paper_final/killcoyne_cv.json` · scripts `scripts/paper_plan/kv_*.{py,R}` · frozen models `models/killcoyne_frozen_pkg_v1/` · ACE-B plan `docs/aceb_primary_killcoyne.md` · results commit d69de24. Row-level outputs on the cluster under `feasibility/paper_plan/killcoyne_mm/cv/`.

### Status

| Item | Status |
|---|---|
| 1 Stratified repeated CV | DONE |
| 2 LOPO artefact | DONE |
| 3 Grade arms under the stratified CV | DONE |
| 4 Frozen package models and ACE-B primary | DONE |

Fold composition (repeat 1): fold 1 8 patients / 4 P, fold 2 8 patients / 4 P, fold 3 8 patients / 4 P, fold 4 8 patients / 4 P, fold 5 8 patients / 4 P, fold 6 8 patients / 4 P, fold 7 8 patients / 4 P, fold 8 8 patients / 3 P, fold 9 8 patients / 3 P, fold 10 8 patients / 3 P.

### 1. Stratified 10-fold × 10 CV vs LOPO

**All of set C**, CNV source their (676 samples, 80 patients, 37 P).

| Arm | CV per-sample AUROC | CV Δ vs L-CNV | CV patient-max AUROC | CV Δ vs L-CNV | LOPO per sample / Δ | LOPO patient max / Δ |
|---|---|---|---|---|---|---|
| L-CNV | 0.847 [0.777, 0.910] | — | 0.883 [0.799, 0.953] | — | 0.846 / — | 0.879 / — |
| L-IMG | 0.879 [0.839, 0.917] | +0.032 [-0.039, 0.108] (p 0.3928) | 0.877 [0.794, 0.950] | -0.006 [-0.095, 0.088] (p 0.9125) | 0.876 / +0.031 [-0.038, 0.104] (p 0.3973) | 0.872 / -0.008 [-0.097, 0.089] (p 0.8856) |
| L-EARLY | 0.912 [0.860, 0.953] | +0.065 [0.030, 0.109] (p 0.0005) | 0.947 [0.890, 0.987] | +0.064 [0.015, 0.124] (p 0.0095) | 0.911 / +0.065 [0.033, 0.105] (p 0.0005) | 0.951 / +0.072 [0.018, 0.138] (p 0.0055) |
| L-LATE | 0.923 [0.876, 0.956] | +0.076 [0.033, 0.129] (p 0.002) | 0.926 [0.855, 0.975] | +0.043 [-0.006, 0.100] (p 0.1104) | 0.919 / +0.074 [0.031, 0.123] (p 0.0015) | 0.899 / +0.019 [-0.035, 0.080] (p 0.5222) |

**(a) NDBE samples only**, CNV source their (463 samples, 75 patients, 32 P).

| Arm | CV per-sample AUROC | CV Δ vs L-CNV | CV patient-max AUROC | CV Δ vs L-CNV | LOPO per sample / Δ | LOPO patient max / Δ |
|---|---|---|---|---|---|---|
| L-CNV | 0.796 [0.682, 0.880] | — | 0.781 [0.663, 0.880] | — | 0.781 / — | 0.765 / — |
| L-IMG | 0.844 [0.794, 0.892] | +0.049 [-0.037, 0.154] (p 0.3018) | 0.847 [0.750, 0.931] | +0.066 [-0.054, 0.197] (p 0.3298) | 0.836 / +0.056 [-0.034, 0.163] (p 0.2339) | 0.826 / +0.061 [-0.063, 0.191] (p 0.3793) |
| L-EARLY | 0.878 [0.798, 0.941] | +0.082 [0.034, 0.145] (p 0.003) | 0.885 [0.799, 0.953] | +0.105 [0.037, 0.181] (p 0.0045) | 0.873 / +0.093 [0.043, 0.156] (p 0.0005) | 0.891 / +0.126 [0.058, 0.206] (p 0.001) |
| L-LATE | 0.886 [0.817, 0.942] | +0.091 [0.037, 0.160] (p 0.004) | 0.884 [0.799, 0.955] | +0.104 [0.040, 0.182] (p 0.014) | 0.876 / +0.095 [0.038, 0.167] (p 0.0025) | 0.849 / +0.084 [0.012, 0.170] (p 0.052) |

**(b) before the first HGD/IMC**, CNV source their (571 samples, 75 patients, 32 P).

| Arm | CV per-sample AUROC | CV Δ vs L-CNV | CV patient-max AUROC | CV Δ vs L-CNV | LOPO per sample / Δ | LOPO patient max / Δ |
|---|---|---|---|---|---|---|
| L-CNV | 0.802 [0.706, 0.879] | — | 0.831 [0.726, 0.920] | — | 0.799 / — | 0.822 / — |
| L-IMG | 0.853 [0.800, 0.904] | +0.051 [-0.040, 0.154] (p 0.2744) | 0.835 [0.730, 0.924] | +0.004 [-0.118, 0.127] (p 0.9655) | 0.847 / +0.048 [-0.041, 0.147] (p 0.3128) | 0.820 / -0.002 [-0.123, 0.124] (p 0.9755) |
| L-EARLY | 0.883 [0.811, 0.939] | +0.081 [0.036, 0.135] (p 0.002) | 0.922 [0.852, 0.973] | +0.090 [0.025, 0.164] (p 0.01) | 0.881 / +0.082 [0.039, 0.135] (p 0.0015) | 0.929 / +0.107 [0.039, 0.185] (p 0.002) |
| L-LATE | 0.896 [0.835, 0.944] | +0.095 [0.041, 0.161] (p 0.0025) | 0.898 [0.814, 0.961] | +0.066 [0.004, 0.137] (p 0.066) | 0.891 / +0.093 [0.039, 0.157] (p 0.003) | 0.871 / +0.049 [-0.021, 0.127] (p 0.2174) |

**(c) NDBE and before the first HGD/IMC**, CNV source their (438 samples, 71 patients, 28 P).

| Arm | CV per-sample AUROC | CV Δ vs L-CNV | CV patient-max AUROC | CV Δ vs L-CNV | LOPO per sample / Δ | LOPO patient max / Δ |
|---|---|---|---|---|---|---|
| L-CNV | 0.778 [0.667, 0.879] | — | 0.786 [0.662, 0.888] | — | 0.761 / — | 0.765 / — |
| L-IMG | 0.838 [0.776, 0.896] | +0.060 [-0.040, 0.165] (p 0.2384) | 0.812 [0.698, 0.911] | +0.027 [-0.120, 0.171] (p 0.7196) | 0.826 / +0.065 [-0.036, 0.174] (p 0.1989) | 0.790 / +0.025 [-0.120, 0.171] (p 0.7456) |
| L-EARLY | 0.867 [0.777, 0.939] | +0.089 [0.031, 0.157] (p 0.007) | 0.879 [0.787, 0.949] | +0.093 [0.008, 0.183] (p 0.0165) | 0.861 / +0.101 [0.042, 0.172] (p 0.002) | 0.883 / +0.118 [0.035, 0.207] (p 0.004) |
| L-LATE | 0.876 [0.798, 0.938] | +0.098 [0.035, 0.170] (p 0.005) | 0.876 [0.785, 0.949] | +0.091 [0.009, 0.183] (p 0.053) | 0.864 / +0.104 [0.041, 0.179] (p 0.0045) | 0.841 / +0.076 [-0.011, 0.175] (p 0.1269) |

**All of set C**, CNV source pkg (676 samples, 80 patients, 37 P).

| Arm | CV per-sample AUROC | CV Δ vs L-CNV | CV patient-max AUROC | CV Δ vs L-CNV | LOPO per sample / Δ | LOPO patient max / Δ |
|---|---|---|---|---|---|---|
| L-CNV | 0.887 [0.825, 0.939] | — | 0.879 [0.795, 0.949] | — | 0.868 / — | 0.882 / — |
| L-IMG | 0.879 [0.839, 0.917] | -0.008 [-0.071, 0.067] (p 0.8301) | 0.877 [0.794, 0.950] | -0.003 [-0.095, 0.086] (p 0.958) | 0.876 / +0.008 [-0.059, 0.088] (p 0.8341) | 0.872 / -0.010 [-0.104, 0.085] (p 0.8336) |
| L-EARLY | 0.919 [0.870, 0.961] | +0.032 [0.009, 0.063] (p 0.0135) | 0.929 [0.862, 0.978] | +0.050 [0.011, 0.098] (p 0.016) | 0.908 / +0.040 [0.006, 0.081] (p 0.0405) | 0.918 / +0.036 [-0.011, 0.085] (p 0.2089) |
| L-LATE | 0.937 [0.903, 0.965] | +0.050 [0.015, 0.094] (p 0.0145) | 0.935 [0.872, 0.982] | +0.056 [0.008, 0.115] (p 0.052) | 0.925 / +0.057 [0.019, 0.103] (p 0.023) | 0.918 / +0.036 [-0.016, 0.090] (p 0.2909) |

**(a) NDBE samples only**, CNV source pkg (463 samples, 75 patients, 32 P).

| Arm | CV per-sample AUROC | CV Δ vs L-CNV | CV patient-max AUROC | CV Δ vs L-CNV | LOPO per sample / Δ | LOPO patient max / Δ |
|---|---|---|---|---|---|---|
| L-CNV | 0.842 [0.749, 0.913] | — | 0.850 [0.751, 0.932] | — | 0.815 / — | 0.837 / — |
| L-IMG | 0.844 [0.794, 0.892] | +0.002 [-0.073, 0.093] (p 0.967) | 0.847 [0.750, 0.931] | -0.003 [-0.119, 0.108] (p 0.9635) | 0.836 / +0.021 [-0.065, 0.119] (p 0.7106) | 0.826 / -0.011 [-0.136, 0.105] (p 0.8616) |
| L-EARLY | 0.875 [0.794, 0.938] | +0.033 [0.002, 0.074] (p 0.0715) | 0.902 [0.825, 0.963] | +0.052 [0.001, 0.112] (p 0.043) | 0.861 / +0.046 [-0.008, 0.111] (p 0.1869) | 0.883 / +0.046 [-0.017, 0.115] (p 0.1869) |
| L-LATE | 0.901 [0.844, 0.948] | +0.059 [0.016, 0.112] (p 0.018) | 0.925 [0.851, 0.981] | +0.076 [0.017, 0.149] (p 0.034) | 0.879 / +0.064 [0.018, 0.121] (p 0.074) | 0.905 / +0.068 [0.005, 0.138] (p 0.097) |

**(b) before the first HGD/IMC**, CNV source pkg (571 samples, 75 patients, 32 P).

| Arm | CV per-sample AUROC | CV Δ vs L-CNV | CV patient-max AUROC | CV Δ vs L-CNV | LOPO per sample / Δ | LOPO patient max / Δ |
|---|---|---|---|---|---|---|
| L-CNV | 0.853 [0.770, 0.914] | — | 0.860 [0.767, 0.939] | — | 0.827 / — | 0.846 / — |
| L-IMG | 0.853 [0.800, 0.904] | -0.001 [-0.083, 0.093] (p 0.9865) | 0.835 [0.730, 0.924] | -0.025 [-0.139, 0.088] (p 0.6742) | 0.847 / +0.019 [-0.068, 0.116] (p 0.7036) | 0.820 / -0.026 [-0.149, 0.095] (p 0.6967) |
| L-EARLY | 0.895 [0.828, 0.947] | +0.041 [0.011, 0.078] (p 0.0085) | 0.906 [0.827, 0.967] | +0.046 [-0.003, 0.105] (p 0.074) | 0.882 / +0.055 [0.009, 0.108] (p 0.043) | 0.892 / +0.046 [-0.010, 0.110] (p 0.1719) |
| L-LATE | 0.912 [0.863, 0.952] | +0.058 [0.015, 0.114] (p 0.0205) | 0.924 [0.852, 0.981] | +0.065 [0.009, 0.131] (p 0.051) | 0.892 / +0.065 [0.019, 0.119] (p 0.043) | 0.891 / +0.045 [-0.018, 0.113] (p 0.2354) |

**(c) NDBE and before the first HGD/IMC**, CNV source pkg (438 samples, 71 patients, 28 P).

| Arm | CV per-sample AUROC | CV Δ vs L-CNV | CV patient-max AUROC | CV Δ vs L-CNV | LOPO per sample / Δ | LOPO patient max / Δ |
|---|---|---|---|---|---|---|
| L-CNV | 0.826 [0.729, 0.909] | — | 0.844 [0.740, 0.934] | — | 0.791 / — | 0.828 / — |
| L-IMG | 0.838 [0.776, 0.896] | +0.012 [-0.075, 0.110] (p 0.7866) | 0.812 [0.698, 0.911] | -0.032 [-0.168, 0.093] (p 0.6292) | 0.826 / +0.035 [-0.068, 0.143] (p 0.5722) | 0.790 / -0.038 [-0.189, 0.100] (p 0.6117) |
| L-EARLY | 0.867 [0.786, 0.936] | +0.042 [0.006, 0.089] (p 0.042) | 0.874 [0.784, 0.946] | +0.030 [-0.026, 0.092] (p 0.2639) | 0.852 / +0.061 [-0.004, 0.133] (p 0.1444) | 0.866 / +0.038 [-0.026, 0.103] (p 0.2869) |
| L-LATE | 0.888 [0.823, 0.944] | +0.062 [0.014, 0.121] (p 0.0285) | 0.905 [0.816, 0.968] | +0.061 [-0.006, 0.135] (p 0.1139) | 0.858 / +0.068 [0.015, 0.135] (p 0.0985) | 0.872 / +0.044 [-0.028, 0.116] (p 0.2909) |

### 2. The LOPO artefact

LOPO intercepts recovered by refitting at the chosen λ; recomputed predictions match the stored ones to 0.0 (max absolute difference).

| Arm | LOPO: corr(label, intercept) Pearson / Spearman | Stratified CV: Pearson / Spearman |
|---|---|---|
| L-CNV their | -0.748 / -0.806 | -0.130 / -0.103 |
| L-CNV pkg | -0.262 / -0.339 | -0.079 / -0.049 |
| L-IMG fold-honest | -0.675 / -0.687 | -0.114 / -0.068 |
| L-EARLY fold-honest their | -0.714 / -0.831 | -0.113 / -0.092 |
| L-EARLY fold-honest pkg | -0.375 / -0.371 | -0.063 / -0.039 |
| L-GRADE | -0.853 / -0.864 | -0.132 / -0.097 |
| L-CNV+GRADE their | -0.584 / -0.612 | -0.105 / -0.095 |
| L-CNV+GRADE pkg | -0.003 / -0.276 | -0.078 / -0.049 |
| L-EARLY+GRADE their | -0.593 / -0.706 | -0.103 / -0.091 |
| L-EARLY+GRADE pkg | -0.194 / -0.199 | -0.072 / -0.059 |

Intercept-only model (prediction = training-row prevalence), per-sample AUROC:

| Subset | LOPO | Stratified CV |
|---|---|---|
| All of set C | 0.000 | 0.244 |
| (a) NDBE samples only | 0.000 | 0.267 |
| (b) before the first HGD/IMC | 0.000 | 0.248 |
| (c) NDBE and before the first HGD/IMC | 0.000 | 0.288 |

### 3. Grade arms under the stratified CV

Raw grade as a score: All of set C per sample 0.694 [0.626, 0.753], patient max 0.861 [0.767, 0.938]; (a) NDBE samples only per sample 0.500 [0.500, 0.500], patient max 0.500 [0.500, 0.500].

**All of set C**, CNV source their.

| Arm | Per-sample AUROC | Patient-max AUROC | Δ per sample | Δ patient max |
|---|---|---|---|---|
| L-GRADE | 0.590 [0.487, 0.684] | 0.843 [0.743, 0.927] | — | — |
| L-CNV+GRADE | 0.829 [0.751, 0.896] | 0.871 [0.776, 0.947] | -0.018 [-0.042, 0.003] (p 0.083) vs L-CNV | -0.012 [-0.041, 0.015] (p 0.2724) vs L-CNV |
| L-EARLY+GRADE | 0.907 [0.851, 0.949] | 0.944 [0.887, 0.986] | +0.078 [0.041, 0.120] (p 0.0005) vs L-CNV+GRADE | +0.073 [0.018, 0.137] (p 0.007) vs L-CNV+GRADE |
| L-LATE with grade | 0.913 [0.863, 0.948] | 0.916 [0.842, 0.971] | +0.084 [0.038, 0.136] (p 0.0005) vs L-CNV+GRADE | +0.045 [-0.008, 0.110] (p 0.1229) vs L-CNV+GRADE |
| L-CNV | 0.847 [0.777, 0.910] | 0.883 [0.799, 0.953] | — | — |

**(a) NDBE samples only**, CNV source their.

| Arm | Per-sample AUROC | Patient-max AUROC | Δ per sample | Δ patient max |
|---|---|---|---|---|
| L-GRADE | 0.246 [0.137, 0.389] | 0.395 [0.259, 0.533] | — | — |
| L-CNV+GRADE | 0.738 [0.616, 0.837] | 0.731 [0.604, 0.839] | -0.057 [-0.079, -0.037] (p 0.0005) vs L-CNV | -0.049 [-0.080, -0.021] (p 0.0115) vs L-CNV |
| L-EARLY+GRADE | 0.857 [0.771, 0.927] | 0.865 [0.774, 0.940] | +0.119 [0.061, 0.190] (p 0.0005) vs L-CNV+GRADE | +0.134 [0.061, 0.216] (p 0.002) vs L-CNV+GRADE |
| L-LATE with grade | 0.866 [0.792, 0.927] | 0.864 [0.776, 0.940] | +0.128 [0.061, 0.210] (p 0.001) vs L-CNV+GRADE | +0.133 [0.058, 0.223] (p 0.01) vs L-CNV+GRADE |
| L-CNV | 0.796 [0.682, 0.880] | 0.781 [0.663, 0.880] | — | — |

**All of set C**, CNV source pkg.

| Arm | Per-sample AUROC | Patient-max AUROC | Δ per sample | Δ patient max |
|---|---|---|---|---|
| L-GRADE | 0.590 [0.487, 0.684] | 0.843 [0.743, 0.927] | — | — |
| L-CNV+GRADE | 0.889 [0.830, 0.937] | 0.898 [0.815, 0.962] | +0.002 [-0.012, 0.016] (p 0.8311) vs L-CNV | +0.019 [-0.011, 0.049] (p 0.1969) vs L-CNV |
| L-EARLY+GRADE | 0.917 [0.866, 0.960] | 0.935 [0.868, 0.983] | +0.028 [0.005, 0.056] (p 0.04) vs L-CNV+GRADE | +0.037 [0.000, 0.084] (p 0.086) vs L-CNV+GRADE |
| L-LATE with grade | 0.934 [0.900, 0.962] | 0.934 [0.868, 0.981] | +0.045 [0.013, 0.086] (p 0.015) vs L-CNV+GRADE | +0.036 [-0.008, 0.088] (p 0.1624) vs L-CNV+GRADE |
| L-CNV | 0.887 [0.825, 0.939] | 0.879 [0.795, 0.949] | — | — |

**(a) NDBE samples only**, CNV source pkg.

| Arm | Per-sample AUROC | Patient-max AUROC | Δ per sample | Δ patient max |
|---|---|---|---|---|
| L-GRADE | 0.246 [0.137, 0.389] | 0.395 [0.259, 0.533] | — | — |
| L-CNV+GRADE | 0.824 [0.729, 0.900] | 0.824 [0.719, 0.910] | -0.018 [-0.035, -0.004] (p 0.1184) vs L-CNV | -0.025 [-0.062, 0.004] (p 0.2319) vs L-CNV |
| L-EARLY+GRADE | 0.860 [0.772, 0.928] | 0.886 [0.803, 0.956] | +0.036 [0.002, 0.079] (p 0.1019) vs L-CNV+GRADE | +0.062 [0.003, 0.132] (p 0.0475) vs L-CNV+GRADE |
| L-LATE with grade | 0.891 [0.835, 0.938] | 0.917 [0.841, 0.975] | +0.066 [0.019, 0.127] (p 0.0105) vs L-CNV+GRADE | +0.093 [0.029, 0.171] (p 0.0165) vs L-CNV+GRADE |
| L-CNV | 0.842 [0.749, 0.913] | 0.850 [0.751, 0.932] | — | — |

### 4. Frozen package-feature models

Bundle SHA-256 `bf1eddeda5083a16ada1ab2a63bb96708686bd05e12120631664541ae0c90776`. Reconstruction of the set-C package block from raw tiles with the frozen constants: max absolute difference 1.78e-15.

| Model | λ | Features | Non-zero coefficients | In-sample AUROC (not a performance estimate) |
|---|---|---|---|---|
| L-CNV | 0.01269 | 632 | 55 | 0.995 |
| L-IMG | 0.00433 | 1536 | 158 | 0.998 |
| L-EARLY | 0.00960 | 2168 | 96 | 1.000 |
| L-LATE | mean of L-CNV and L-IMG | — | — | 1.000 |

Development estimate of the ACE-B primary contrast (L-LATE (pkg) minus L-CNV (pkg), per-sample AUROC, NDBE samples, stratified CV; 463 samples, 75 patients, 32 P): Δ +0.059, one-sided 95% lower bound +0.021, two-sided 95% CI [+0.016, +0.112].

**Interpretation.** Under stratified 10-fold × 10 CV the fusion gains over L-CNV are about the same as under LOPO (L-LATE per sample +0.076 on their matrix, +0.050 on package features) while the intercept–label correlation falls from −0.26 to −0.85 under LOPO to −0.05 to −0.13; the ACE-B primary contrast has a development estimate of +0.059 (one-sided 95% lower bound +0.021).

**Caveats.** (1) The intercept-only model still scores below 0.5 under the stratified CV (0.244 per sample): folds hold 3 or 4 P patients of 8, so the held-out fold's prevalence still moves opposite to the training prevalence; stratification shrinks the artefact but cannot remove it with 37 P patients in 10 folds. (2) L-CNV on package features gains most from the change of protocol (0.868 LOPO → 0.887 CV per sample), consistent with it being the arm most exposed to the artefact after L-GRADE. (3) L-GRADE is still below 0.5 on NDBE samples (0.246), where grade is constant and only the fold intercept varies. (4) The frozen package models use hg38 package features scaled over set C; their reconstruction from raw tiles matches the training block to 1.8e-15.

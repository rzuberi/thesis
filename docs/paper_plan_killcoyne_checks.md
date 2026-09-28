# Killcoyne protocol with imaging: checks (selection-adjusted p, fold-honest image scaling, sample subsets, grade, frozen models)

Status: PRE-SPECIFICATION. Nothing below has been run. Results are appended in a later commit; this section is not edited afterwards.

Protocol fixed as in `docs/paper_plan_killcoyne_multimodal.md` (pre-spec 3904c44, results d497449 / 71e7f0a): set C (676 samples, 80 patients), label = sheet Status per sample, LOPO over patients, inner 10 × 5 patient-grouped CV (`set.seed(r)`, r = 1..10), glmnet α 0.9 with standardize = FALSE, λ = class-error min per left-out patient (primary), their shipped CNV matrix primary and package features secondary. Same metrics (rank AUROC, 3 decimals; patient = max over samples), 95% CI by patient bootstrap (2,000, `RandomState(0)`), paired permutation = swap the two arms' scores within whole patients (2,000, seed 0), two-sided.

## 1. Selection-adjusted permutation p

For each CNV source, the 8 non-CNV arms (L-IMG, L-EARLY, L-INTER, L-LATE, N-IMG, N-EARLY, N-INTER, N-LATE; with that source's CNV where the arm uses CNV) are compared with L-CNV of that source. In each of the 2,000 permutations one patient-swap mask is drawn and applied to all 8 arm-vs-L-CNV pairs; the statistic is max over the 8 arms of |Δ|. Adjusted p for arm j = (1 + #{permutations with max |Δ| ≥ |Δ_j observed|}) / 2,001 (single-step max-T). Separately for per-sample and patient-max AUROC. The unadjusted p from the same masks is reported next to it.

## 2. Fold-honest image scaling

L-IMG, L-EARLY (both CNV sources) and L-LATE rerun with the image block z-scored using the training patients of each LOPO fold only (the left-out patient is scaled with the training mean and s.d.; inner CV reuses the outer-training scaling). CNV blocks unchanged (their matrix as shipped; package block as before). L-LATE (fold-honest) = mean of L-CNV and fold-honest L-IMG. Reported next to the whole-set versions, with Δ vs L-CNV, CI and p.

## 3. Sample subsets (existing predictions, no refit)

Every arm (the primary arms of the multimodal report for both CNV sources, and the item 2 arms) scored on:
- (a) NDBE samples only (sheet Pathology BE);
- (b) samples taken before the patient's first HGD/IMC. Time axis = sheet 'Months before final' (endoscopy-level; within-patient order agrees with endoscopy year). First HGD/IMC = the earliest endoscopy at which any of the patient's 773 published samples has Pathology HGD or IMC, or the sheet's per-endoscopy class (Path_class_per_OGD) is HGD, IMC or HGD/IMC. Samples at that endoscopy or later are excluded. Progressor patients with no recorded HGD/IMC endoscopy use their final endoscopy (Months before final = 0) as the event, and their count is reported. Non-progressors keep all samples.
- (c) both (a) and (b).

Per subset: per-sample and patient-max AUROC for every arm; Δ vs L-CNV (same source) with paired bootstrap CI and paired permutation p, both computed within the subset (patients with no sample in the subset drop out).

## 4. Pathology grade

Grade = sample Pathology as ordinal (NDBE 0, ID 1, LGD 2, HGD 3, IMC 4), z-scored over set C. New arms in the same protocol (whole-set scaling, as the primary multimodal arms), both CNV sources:
- L-GRADE: grade alone (glmnet needs two columns; a constant zero column is added, which receives no coefficient);
- L-CNV+GRADE: [CNV block, grade];
- L-EARLY+GRADE: [CNV block, image block, grade];
- L-LATE with grade: mean of L-CNV+GRADE and L-IMG.
Reported: all four arms; Δ of L-EARLY+GRADE and of L-LATE with grade vs L-CNV+GRADE, with CI and p, on all of set C and on NDBE samples only (on NDBE only, grade is constant and L-GRADE is uninformative by construction).

## 5. Frozen models for ACE-B

L-EARLY and L-LATE on their CNV matrix with fold-honest standardisation, refitted once on all of set C: image block z-scored with set-C training statistics; λ = class-error min from the same 10 × 5 patient-grouped CV on all of C; α 0.9, standardize = FALSE. L-LATE = mean of the frozen L-CNV and frozen L-IMG probabilities, so those two are frozen as well. Committed under `models/killcoyne_frozen_v1/`: coefficients (intercept + every feature, zeros included), preprocessing (image mean and s.d. per dimension; UNI2 extraction settings from the embedding files; CNV construction = the package pipeline with the packaged model's tile/arm/cx means and s.d., and the tile list), λ, α, software versions, and a manifest with SHA-256 of every file. Aggregates only; no sample rows.

## Status and outputs

Each item DONE / PARTIAL / NOT AVAILABLE; at most one line of interpretation. Scripts `scripts/paper_plan/kc_linear.R` (items 2, 4; sharded), `kc_freeze.R` (item 5), `kc_merge.py` (items 1–4), `kc_render.py`. Results `results/paper_final/killcoyne_checks.json`. Row-level outputs on the cluster under `feasibility/paper_plan/killcoyne_mm/checks/`. Jobs small, each raced on epyc, rocm, cuda and h200; merges run as Slurm jobs, not on the login node.

---

## Results

Sources: `results/paper_final/killcoyne_checks.json` · scripts `scripts/paper_plan/kc_*.{py,R}` · frozen models `models/killcoyne_frozen_v1/` · results commit 90dec3e. Row-level outputs on the cluster under `feasibility/paper_plan/killcoyne_mm/checks/`.

### Status

| Item | Status |
|---|---|
| 1 Selection-adjusted p | DONE |
| 2 Fold-honest image scaling | DONE |
| 3 Sample subsets | DONE |
| 4 Pathology grade | DONE |
| 5 Frozen models | DONE |

Subsets: All of set C 676 samples, 80 patients (37 P); (a) NDBE samples only 463 samples, 75 patients (32 P); (b) before the first HGD/IMC 571 samples, 75 patients (32 P); (c) NDBE and before the first HGD/IMC 438 samples, 71 patients (28 P). First HGD/IMC dated from an HGD/IMC record for 33 of 37 P patients; 4 use the final endoscopy.

### 1. Selection-adjusted permutation p (max-T over the 8 non-CNV arms, all of set C)

CNV source: their shipped CNV matrix.

| Arm | Δ per sample | p unadjusted | p max-T | Δ patient max | p unadjusted | p max-T |
|---|---|---|---|---|---|---|
| L-IMG | +0.032 | 0.3793 | 0.8261 | -0.014 | 0.7786 | 0.9985 |
| L-EARLY | +0.065 | 0.0005 | 0.2169 | +0.070 | 0.007 | 0.2654 |
| L-INTER | +0.029 | 0.3818 | 0.8706 | +0.024 | 0.5712 | 0.973 |
| L-LATE | +0.074 | 0.001 | 0.1174 | +0.016 | 0.6097 | 0.9955 |
| N-IMG | -0.029 | 0.5032 | 0.8746 | -0.003 | 0.956 | 1.0 |
| N-EARLY | +0.020 | 0.5717 | 0.9725 | -0.012 | 0.6477 | 0.9995 |
| N-INTER | +0.025 | 0.4943 | 0.925 | -0.030 | 0.2744 | 0.9095 |
| N-LATE | +0.038 | 0.1279 | 0.7151 | +0.040 | 0.094 | 0.7526 |

CNV source: package features from our counts.

| Arm | Δ per sample | p unadjusted | p max-T | Δ patient max | p unadjusted | p max-T |
|---|---|---|---|---|---|---|
| L-IMG | +0.009 | 0.8176 | 0.997 | -0.016 | 0.7426 | 0.996 |
| L-EARLY | +0.038 | 0.059 | 0.5897 | +0.037 | 0.2169 | 0.7891 |
| L-INTER | +0.025 | 0.3923 | 0.8346 | +0.019 | 0.6647 | 0.9895 |
| L-LATE | +0.057 | 0.023 | 0.2959 | +0.038 | 0.2619 | 0.7731 |
| N-IMG | -0.052 | 0.2764 | 0.3763 | -0.006 | 0.9165 | 1.0 |
| N-EARLY | -0.004 | 0.9055 | 1.0 | +0.017 | 0.6697 | 0.9955 |
| N-INTER | -0.019 | 0.5457 | 0.9455 | -0.010 | 0.7821 | 1.0 |
| N-LATE | +0.024 | 0.3738 | 0.8481 | +0.052 | 0.1214 | 0.5357 |

### 2. Whole-set vs fold-honest image scaling (all of set C)

| CNV source | Arm | Scaling | Per-sample AUROC | Patient-max AUROC | Δ per sample vs L-CNV | Δ patient max vs L-CNV |
|---|---|---|---|---|---|---|
| their | L-IMG | whole set | 0.878 [0.837, 0.915] | 0.865 [0.776, 0.944] | +0.032 [-0.036, 0.106] (p 0.3793) | -0.014 [-0.106, 0.078] (p 0.7786) |
| their | L-IMG | fold-honest | 0.876 [0.835, 0.914] | 0.872 [0.784, 0.949] | +0.031 [-0.038, 0.104] (p 0.3973) | -0.008 [-0.097, 0.089] (p 0.8856) |
| their | L-EARLY | whole set | 0.910 [0.854, 0.953] | 0.949 [0.892, 0.988] | +0.065 [0.032, 0.105] (p 0.0005) | +0.070 [0.018, 0.135] (p 0.007) |
| their | L-EARLY | fold-honest | 0.911 [0.855, 0.954] | 0.951 [0.895, 0.989] | +0.065 [0.033, 0.105] (p 0.0005) | +0.072 [0.018, 0.138] (p 0.0055) |
| their | L-LATE | whole set | 0.920 [0.873, 0.954] | 0.895 [0.814, 0.958] | +0.074 [0.032, 0.125] (p 0.001) | +0.016 [-0.038, 0.077] (p 0.6097) |
| their | L-LATE | fold-honest | 0.919 [0.871, 0.954] | 0.899 [0.819, 0.962] | +0.074 [0.031, 0.123] (p 0.0015) | +0.019 [-0.035, 0.080] (p 0.5222) |
| pkg | L-IMG | whole set | 0.878 [0.837, 0.915] | 0.865 [0.776, 0.944] | +0.009 [-0.059, 0.091] (p 0.8176) | -0.016 [-0.110, 0.079] (p 0.7426) |
| pkg | L-IMG | fold-honest | 0.876 [0.835, 0.914] | 0.872 [0.784, 0.949] | +0.008 [-0.059, 0.088] (p 0.8341) | -0.010 [-0.104, 0.085] (p 0.8336) |
| pkg | L-EARLY | whole set | 0.907 [0.852, 0.952] | 0.919 [0.852, 0.971] | +0.038 [0.004, 0.081] (p 0.059) | +0.037 [-0.010, 0.087] (p 0.2169) |
| pkg | L-EARLY | fold-honest | 0.908 [0.853, 0.953] | 0.918 [0.853, 0.971] | +0.040 [0.006, 0.081] (p 0.0405) | +0.036 [-0.011, 0.085] (p 0.2089) |
| pkg | L-LATE | whole set | 0.925 [0.881, 0.961] | 0.920 [0.846, 0.976] | +0.057 [0.019, 0.104] (p 0.023) | +0.038 [-0.013, 0.091] (p 0.2619) |
| pkg | L-LATE | fold-honest | 0.925 [0.880, 0.960] | 0.918 [0.842, 0.975] | +0.057 [0.019, 0.103] (p 0.023) | +0.036 [-0.016, 0.090] (p 0.2909) |

### 3. Existing predictions on sample subsets (no refit)

**(a) NDBE samples only**, CNV source their (463 samples, 75 patients).

| Arm | Per-sample AUROC | Δ vs L-CNV | Patient-max AUROC | Δ vs L-CNV |
|---|---|---|---|---|
| L-CNV | 0.781 [0.664, 0.868] | — | 0.765 [0.640, 0.869] | — |
| L-IMG | 0.838 [0.788, 0.886] | +0.058 [-0.032, 0.165] (p 0.2189) | 0.826 [0.728, 0.915] | +0.061 [-0.054, 0.187] (p 0.3753) |
| L-EARLY | 0.873 [0.788, 0.941] | +0.092 [0.043, 0.156] (p 0.0005) | 0.891 [0.806, 0.958] | +0.126 [0.058, 0.206] (p 0.001) |
| L-INTER | 0.849 [0.760, 0.929] | +0.069 [-0.022, 0.161] (p 0.1434) | 0.876 [0.780, 0.951] | +0.111 [0.023, 0.211] (p 0.03) |
| L-LATE | 0.877 [0.807, 0.935] | +0.096 [0.038, 0.170] (p 0.003) | 0.844 [0.746, 0.927] | +0.078 [0.007, 0.166] (p 0.065) |
| N-IMG | 0.737 [0.651, 0.825] | -0.043 [-0.150, 0.076] (p 0.4708) | 0.769 [0.641, 0.880] | +0.004 [-0.141, 0.150] (p 0.9655) |
| N-EARLY | 0.830 [0.734, 0.915] | +0.049 [-0.048, 0.143] (p 0.4023) | 0.805 [0.694, 0.905] | +0.039 [-0.046, 0.129] (p 0.4333) |
| N-INTER | 0.829 [0.732, 0.914] | +0.049 [-0.051, 0.145] (p 0.4213) | 0.777 [0.659, 0.882] | +0.012 [-0.083, 0.109] (p 0.8366) |
| N-LATE | 0.818 [0.728, 0.897] | +0.038 [-0.018, 0.100] (p 0.3503) | 0.813 [0.703, 0.911] | +0.048 [-0.019, 0.125] (p 0.2409) |
| L-IMG (fold-honest) | 0.836 [0.785, 0.884] | +0.056 [-0.034, 0.163] (p 0.2339) | 0.826 [0.725, 0.914] | +0.061 [-0.063, 0.191] (p 0.3793) |
| L-EARLY (fold-honest) | 0.873 [0.788, 0.941] | +0.093 [0.043, 0.156] (p 0.0005) | 0.891 [0.806, 0.958] | +0.126 [0.058, 0.206] (p 0.001) |
| L-LATE (fold-honest) | 0.876 [0.805, 0.934] | +0.095 [0.038, 0.167] (p 0.0025) | 0.849 [0.751, 0.933] | +0.084 [0.012, 0.170] (p 0.052) |

**(b) before the first HGD/IMC**, CNV source their (571 samples, 75 patients).

| Arm | Per-sample AUROC | Δ vs L-CNV | Patient-max AUROC | Δ vs L-CNV |
|---|---|---|---|---|
| L-CNV | 0.799 [0.702, 0.876] | — | 0.822 [0.709, 0.918] | — |
| L-IMG | 0.849 [0.796, 0.900] | +0.050 [-0.039, 0.151] (p 0.2989) | 0.818 [0.705, 0.910] | -0.004 [-0.124, 0.120] (p 0.9535) |
| L-EARLY | 0.880 [0.802, 0.939] | +0.082 [0.038, 0.134] (p 0.0015) | 0.927 [0.860, 0.977] | +0.105 [0.038, 0.183] (p 0.002) |
| L-INTER | 0.837 [0.756, 0.907] | +0.039 [-0.051, 0.125] (p 0.3933) | 0.839 [0.731, 0.928] | +0.017 [-0.070, 0.109] (p 0.7206) |
| L-LATE | 0.893 [0.829, 0.942] | +0.094 [0.040, 0.159] (p 0.003) | 0.869 [0.774, 0.943] | +0.047 [-0.022, 0.126] (p 0.2354) |
| N-IMG | 0.770 [0.688, 0.846] | -0.029 [-0.130, 0.077] (p 0.5987) | 0.786 [0.666, 0.894] | -0.036 [-0.159, 0.091] (p 0.6092) |
| N-EARLY | 0.832 [0.743, 0.907] | +0.033 [-0.042, 0.112] (p 0.5062) | 0.820 [0.714, 0.911] | -0.001 [-0.076, 0.075] (p 0.9795) |
| N-INTER | 0.834 [0.755, 0.904] | +0.036 [-0.043, 0.112] (p 0.4768) | 0.796 [0.680, 0.899] | -0.026 [-0.101, 0.052] (p 0.5142) |
| N-LATE | 0.839 [0.761, 0.908] | +0.041 [-0.011, 0.098] (p 0.2559) | 0.848 [0.742, 0.938] | +0.026 [-0.031, 0.085] (p 0.4193) |
| L-IMG (fold-honest) | 0.847 [0.793, 0.899] | +0.048 [-0.041, 0.147] (p 0.3128) | 0.820 [0.711, 0.914] | -0.002 [-0.123, 0.124] (p 0.9755) |
| L-EARLY (fold-honest) | 0.881 [0.802, 0.940] | +0.082 [0.039, 0.135] (p 0.0015) | 0.929 [0.863, 0.977] | +0.107 [0.039, 0.185] (p 0.002) |
| L-LATE (fold-honest) | 0.891 [0.827, 0.940] | +0.093 [0.039, 0.157] (p 0.003) | 0.871 [0.774, 0.945] | +0.049 [-0.021, 0.127] (p 0.2174) |

**(c) NDBE and before the first HGD/IMC**, CNV source their (438 samples, 71 patients).

| Arm | Per-sample AUROC | Δ vs L-CNV | Patient-max AUROC | Δ vs L-CNV |
|---|---|---|---|---|
| L-CNV | 0.761 [0.646, 0.867] | — | 0.765 [0.636, 0.875] | — |
| L-IMG | 0.829 [0.766, 0.885] | +0.068 [-0.032, 0.181] (p 0.1874) | 0.791 [0.669, 0.895] | +0.026 [-0.121, 0.166] (p 0.7406) |
| L-EARLY | 0.861 [0.766, 0.937] | +0.100 [0.042, 0.171] (p 0.0025) | 0.882 [0.796, 0.952] | +0.117 [0.035, 0.206] (p 0.004) |
| L-INTER | 0.835 [0.739, 0.921] | +0.075 [-0.025, 0.177] (p 0.1409) | 0.817 [0.698, 0.920] | +0.052 [-0.054, 0.167] (p 0.3613) |
| L-LATE | 0.866 [0.784, 0.932] | +0.105 [0.041, 0.184] (p 0.0045) | 0.841 [0.738, 0.928] | +0.076 [-0.012, 0.174] (p 0.1259) |
| N-IMG | 0.729 [0.633, 0.828] | -0.032 [-0.147, 0.096] (p 0.6412) | 0.724 [0.586, 0.857] | -0.041 [-0.215, 0.127] (p 0.6452) |
| N-EARLY | 0.818 [0.721, 0.904] | +0.057 [-0.044, 0.154] (p 0.3883) | 0.787 [0.664, 0.891] | +0.022 [-0.065, 0.114] (p 0.6787) |
| N-INTER | 0.816 [0.713, 0.908] | +0.055 [-0.052, 0.155] (p 0.4303) | 0.773 [0.645, 0.886] | +0.008 [-0.071, 0.096] (p 0.8776) |
| N-LATE | 0.802 [0.704, 0.893] | +0.042 [-0.022, 0.113] (p 0.3628) | 0.806 [0.688, 0.915] | +0.042 [-0.040, 0.125] (p 0.3433) |
| L-IMG (fold-honest) | 0.826 [0.762, 0.882] | +0.065 [-0.036, 0.174] (p 0.1989) | 0.790 [0.670, 0.892] | +0.025 [-0.120, 0.171] (p 0.7456) |
| L-EARLY (fold-honest) | 0.861 [0.767, 0.937] | +0.101 [0.042, 0.172] (p 0.002) | 0.883 [0.797, 0.953] | +0.118 [0.035, 0.207] (p 0.004) |
| L-LATE (fold-honest) | 0.864 [0.783, 0.931] | +0.104 [0.041, 0.179] (p 0.0045) | 0.841 [0.739, 0.927] | +0.076 [-0.011, 0.175] (p 0.1269) |

**All of set C**, CNV source their (676 samples, 80 patients).

| Arm | Per-sample AUROC | Δ vs L-CNV | Patient-max AUROC | Δ vs L-CNV |
|---|---|---|---|---|
| L-CNV | 0.846 [0.774, 0.908] | — | 0.879 [0.790, 0.954] | — |
| L-IMG | 0.878 [0.837, 0.915] | +0.032 [-0.036, 0.106] (p 0.3793) | 0.865 [0.776, 0.944] | -0.014 [-0.106, 0.078] (p 0.7786) |
| L-EARLY | 0.910 [0.854, 0.953] | +0.065 [0.032, 0.105] (p 0.0005) | 0.949 [0.892, 0.988] | +0.070 [0.018, 0.135] (p 0.007) |
| L-INTER | 0.875 [0.811, 0.930] | +0.029 [-0.036, 0.097] (p 0.3818) | 0.903 [0.816, 0.976] | +0.024 [-0.050, 0.099] (p 0.5712) |
| L-LATE | 0.920 [0.873, 0.954] | +0.074 [0.032, 0.125] (p 0.001) | 0.895 [0.814, 0.958] | +0.016 [-0.038, 0.077] (p 0.6097) |
| N-IMG | 0.817 [0.750, 0.875] | -0.029 [-0.104, 0.053] (p 0.5032) | 0.876 [0.793, 0.946] | -0.003 [-0.088, 0.084] (p 0.956) |
| N-EARLY | 0.866 [0.793, 0.926] | +0.020 [-0.040, 0.084] (p 0.5717) | 0.867 [0.776, 0.947] | -0.012 [-0.063, 0.038] (p 0.6477) |
| N-INTER | 0.870 [0.802, 0.926] | +0.025 [-0.034, 0.084] (p 0.4943) | 0.849 [0.747, 0.938] | -0.030 [-0.087, 0.024] (p 0.2744) |
| N-LATE | 0.883 [0.820, 0.933] | +0.038 [0.001, 0.082] (p 0.1279) | 0.919 [0.849, 0.976] | +0.040 [0.004, 0.084] (p 0.094) |
| L-IMG (fold-honest) | 0.876 [0.835, 0.914] | +0.031 [-0.038, 0.104] (p 0.3973) | 0.872 [0.784, 0.949] | -0.008 [-0.097, 0.089] (p 0.8856) |
| L-EARLY (fold-honest) | 0.911 [0.855, 0.954] | +0.065 [0.033, 0.105] (p 0.0005) | 0.951 [0.895, 0.989] | +0.072 [0.018, 0.138] (p 0.0055) |
| L-LATE (fold-honest) | 0.919 [0.871, 0.954] | +0.074 [0.031, 0.123] (p 0.0015) | 0.899 [0.819, 0.962] | +0.019 [-0.035, 0.080] (p 0.5222) |

**(a) NDBE samples only**, CNV source pkg (463 samples, 75 patients).

| Arm | Per-sample AUROC | Δ vs L-CNV | Patient-max AUROC | Δ vs L-CNV |
|---|---|---|---|---|
| L-CNV | 0.815 [0.708, 0.899] | — | 0.837 [0.738, 0.920] | — |
| L-IMG | 0.838 [0.788, 0.886] | +0.023 [-0.062, 0.124] (p 0.6872) | 0.826 [0.728, 0.915] | -0.011 [-0.132, 0.105] (p 0.8581) |
| L-EARLY | 0.857 [0.771, 0.924] | +0.042 [-0.013, 0.108] (p 0.2469) | 0.882 [0.801, 0.948] | +0.045 [-0.019, 0.115] (p 0.2109) |
| L-INTER | 0.879 [0.808, 0.935] | +0.063 [-0.019, 0.150] (p 0.1569) | 0.882 [0.799, 0.948] | +0.044 [-0.060, 0.143] (p 0.3963) |
| L-LATE | 0.879 [0.806, 0.938] | +0.064 [0.018, 0.123] (p 0.0715) | 0.906 [0.824, 0.969] | +0.068 [0.007, 0.137] (p 0.0895) |
| N-IMG | 0.737 [0.651, 0.825] | -0.078 [-0.189, 0.039] (p 0.2344) | 0.769 [0.641, 0.880] | -0.068 [-0.216, 0.070] (p 0.3298) |
| N-EARLY | 0.819 [0.710, 0.914] | +0.004 [-0.082, 0.091] (p 0.938) | 0.841 [0.740, 0.927] | +0.004 [-0.078, 0.083] (p 0.93) |
| N-INTER | 0.793 [0.682, 0.888] | -0.023 [-0.098, 0.052] (p 0.6297) | 0.806 [0.690, 0.904] | -0.031 [-0.122, 0.053] (p 0.4838) |
| N-LATE | 0.830 [0.733, 0.912] | +0.015 [-0.041, 0.075] (p 0.7281) | 0.890 [0.801, 0.960] | +0.052 [-0.004, 0.113] (p 0.1764) |
| L-IMG (fold-honest) | 0.836 [0.785, 0.884] | +0.021 [-0.065, 0.119] (p 0.7106) | 0.826 [0.725, 0.914] | -0.011 [-0.136, 0.105] (p 0.8616) |
| L-EARLY (fold-honest) | 0.861 [0.774, 0.928] | +0.046 [-0.008, 0.111] (p 0.1869) | 0.883 [0.801, 0.949] | +0.046 [-0.017, 0.115] (p 0.1869) |
| L-LATE (fold-honest) | 0.879 [0.808, 0.936] | +0.064 [0.018, 0.121] (p 0.074) | 0.905 [0.822, 0.969] | +0.068 [0.005, 0.138] (p 0.097) |

**(b) before the first HGD/IMC**, CNV source pkg (571 samples, 75 patients).

| Arm | Per-sample AUROC | Δ vs L-CNV | Patient-max AUROC | Δ vs L-CNV |
|---|---|---|---|---|
| L-CNV | 0.827 [0.737, 0.901] | — | 0.846 [0.748, 0.926] | — |
| L-IMG | 0.849 [0.796, 0.900] | +0.022 [-0.066, 0.120] (p 0.6757) | 0.818 [0.705, 0.910] | -0.028 [-0.150, 0.092] (p 0.6722) |
| L-EARLY | 0.881 [0.808, 0.937] | +0.053 [0.008, 0.107] (p 0.0645) | 0.889 [0.807, 0.958] | +0.043 [-0.015, 0.109] (p 0.2264) |
| L-INTER | 0.871 [0.812, 0.920] | +0.044 [-0.029, 0.123] (p 0.2544) | 0.842 [0.740, 0.934] | -0.004 [-0.117, 0.113] (p 0.94) |
| L-LATE | 0.893 [0.830, 0.943] | +0.065 [0.020, 0.120] (p 0.0425) | 0.893 [0.807, 0.963] | +0.047 [-0.014, 0.114] (p 0.2074) |
| N-IMG | 0.770 [0.688, 0.846] | -0.058 [-0.160, 0.049] (p 0.3628) | 0.786 [0.666, 0.894] | -0.060 [-0.192, 0.076] (p 0.3978) |
| N-EARLY | 0.822 [0.731, 0.902] | -0.006 [-0.079, 0.068] (p 0.8986) | 0.847 [0.743, 0.936] | +0.001 [-0.086, 0.085] (p 0.994) |
| N-INTER | 0.800 [0.704, 0.881] | -0.028 [-0.096, 0.040] (p 0.5387) | 0.813 [0.702, 0.910] | -0.033 [-0.124, 0.052] (p 0.4718) |
| N-LATE | 0.845 [0.769, 0.913] | +0.018 [-0.035, 0.075] (p 0.6542) | 0.887 [0.797, 0.964] | +0.041 [-0.020, 0.105] (p 0.2714) |
| L-IMG (fold-honest) | 0.847 [0.793, 0.899] | +0.019 [-0.068, 0.116] (p 0.7036) | 0.820 [0.711, 0.914] | -0.026 [-0.149, 0.095] (p 0.6967) |
| L-EARLY (fold-honest) | 0.882 [0.811, 0.938] | +0.055 [0.009, 0.108] (p 0.043) | 0.892 [0.810, 0.960] | +0.046 [-0.010, 0.110] (p 0.1719) |
| L-LATE (fold-honest) | 0.892 [0.830, 0.941] | +0.065 [0.019, 0.119] (p 0.043) | 0.891 [0.802, 0.962] | +0.045 [-0.018, 0.113] (p 0.2354) |

**(c) NDBE and before the first HGD/IMC**, CNV source pkg (438 samples, 71 patients).

| Arm | Per-sample AUROC | Δ vs L-CNV | Patient-max AUROC | Δ vs L-CNV |
|---|---|---|---|---|
| L-CNV | 0.791 [0.682, 0.892] | — | 0.828 [0.722, 0.921] | — |
| L-IMG | 0.829 [0.766, 0.885] | +0.038 [-0.066, 0.148] (p 0.5407) | 0.791 [0.669, 0.895] | -0.037 [-0.184, 0.099] (p 0.6092) |
| L-EARLY | 0.847 [0.757, 0.924] | +0.057 [-0.011, 0.132] (p 0.1914) | 0.853 [0.757, 0.932] | +0.025 [-0.046, 0.097] (p 0.5287) |
| L-INTER | 0.870 [0.796, 0.933] | +0.079 [-0.015, 0.180] (p 0.1244) | 0.820 [0.709, 0.914] | -0.008 [-0.131, 0.102] (p 0.9) |
| L-LATE | 0.859 [0.775, 0.931] | +0.068 [0.015, 0.137] (p 0.096) | 0.875 [0.779, 0.951] | +0.047 [-0.025, 0.118] (p 0.2589) |
| N-IMG | 0.729 [0.633, 0.828] | -0.062 [-0.186, 0.065] (p 0.4023) | 0.724 [0.586, 0.857] | -0.104 [-0.278, 0.060] (p 0.1979) |
| N-EARLY | 0.804 [0.691, 0.903] | +0.014 [-0.085, 0.108] (p 0.8291) | 0.790 [0.668, 0.899] | -0.038 [-0.142, 0.055] (p 0.4398) |
| N-INTER | 0.771 [0.650, 0.883] | -0.020 [-0.105, 0.066] (p 0.7191) | 0.779 [0.647, 0.891] | -0.049 [-0.157, 0.043] (p 0.3333) |
| N-LATE | 0.806 [0.702, 0.904] | +0.015 [-0.049, 0.085] (p 0.7626) | 0.865 [0.766, 0.948] | +0.037 [-0.034, 0.107] (p 0.3983) |
| L-IMG (fold-honest) | 0.826 [0.762, 0.882] | +0.035 [-0.068, 0.143] (p 0.5722) | 0.790 [0.670, 0.892] | -0.038 [-0.189, 0.100] (p 0.6117) |
| L-EARLY (fold-honest) | 0.852 [0.764, 0.927] | +0.061 [-0.004, 0.133] (p 0.1444) | 0.866 [0.773, 0.943] | +0.038 [-0.026, 0.103] (p 0.2869) |
| L-LATE (fold-honest) | 0.858 [0.774, 0.930] | +0.068 [0.015, 0.135] (p 0.0985) | 0.872 [0.775, 0.950] | +0.044 [-0.028, 0.116] (p 0.2909) |

**All of set C**, CNV source pkg (676 samples, 80 patients).

| Arm | Per-sample AUROC | Δ vs L-CNV | Patient-max AUROC | Δ vs L-CNV |
|---|---|---|---|---|
| L-CNV | 0.868 [0.795, 0.928] | — | 0.882 [0.800, 0.950] | — |
| L-IMG | 0.878 [0.837, 0.915] | +0.009 [-0.059, 0.091] (p 0.8176) | 0.865 [0.776, 0.944] | -0.016 [-0.110, 0.079] (p 0.7426) |
| L-EARLY | 0.907 [0.852, 0.952] | +0.038 [0.004, 0.081] (p 0.059) | 0.919 [0.852, 0.971] | +0.037 [-0.010, 0.087] (p 0.2169) |
| L-INTER | 0.894 [0.848, 0.934] | +0.025 [-0.030, 0.089] (p 0.3923) | 0.901 [0.821, 0.967] | +0.019 [-0.064, 0.097] (p 0.6647) |
| L-LATE | 0.925 [0.881, 0.961] | +0.057 [0.019, 0.104] (p 0.023) | 0.920 [0.846, 0.976] | +0.038 [-0.013, 0.091] (p 0.2619) |
| N-IMG | 0.817 [0.750, 0.875] | -0.052 [-0.133, 0.038] (p 0.2764) | 0.876 [0.793, 0.946] | -0.006 [-0.096, 0.080] (p 0.9165) |
| N-EARLY | 0.864 [0.789, 0.928] | -0.004 [-0.058, 0.052] (p 0.9055) | 0.899 [0.815, 0.967] | +0.017 [-0.055, 0.079] (p 0.6697) |
| N-INTER | 0.849 [0.779, 0.913] | -0.019 [-0.072, 0.031] (p 0.5457) | 0.872 [0.779, 0.951] | -0.010 [-0.083, 0.050] (p 0.7821) |
| N-LATE | 0.893 [0.834, 0.940] | +0.024 [-0.013, 0.070] (p 0.3738) | 0.934 [0.870, 0.985] | +0.052 [0.018, 0.096] (p 0.1214) |
| L-IMG (fold-honest) | 0.876 [0.835, 0.914] | +0.008 [-0.059, 0.088] (p 0.8341) | 0.872 [0.784, 0.949] | -0.010 [-0.104, 0.085] (p 0.8336) |
| L-EARLY (fold-honest) | 0.908 [0.853, 0.953] | +0.040 [0.006, 0.081] (p 0.0405) | 0.918 [0.853, 0.971] | +0.036 [-0.011, 0.085] (p 0.2089) |
| L-LATE (fold-honest) | 0.925 [0.880, 0.960] | +0.057 [0.019, 0.103] (p 0.023) | 0.918 [0.842, 0.975] | +0.036 [-0.016, 0.090] (p 0.2909) |

### 4. Pathology grade

**All of set C**, CNV source their.

| Arm | Per-sample AUROC | Patient-max AUROC | Δ per sample | Δ patient max |
|---|---|---|---|---|
| L-GRADE | 0.492 [0.383, 0.585] | 0.820 [0.701, 0.918] | — | — |
| L-CNV+GRADE | 0.818 [0.735, 0.887] | 0.859 [0.766, 0.938] | -0.028 [-0.060, 0.000] (p 0.0595) vs L-CNV | -0.020 [-0.063, 0.024] (p 0.3243) vs L-CNV |
| L-EARLY+GRADE | 0.909 [0.853, 0.952] | 0.952 [0.900, 0.989] | +0.091 [0.049, 0.140] (p 0.0005) vs L-CNV+GRADE | +0.093 [0.029, 0.164] (p 0.0015) vs L-CNV+GRADE |
| L-LATE with grade | 0.906 [0.855, 0.943] | 0.891 [0.812, 0.956] | +0.089 [0.042, 0.141] (p 0.001) vs L-CNV+GRADE | +0.032 [-0.027, 0.098] (p 0.3108) vs L-CNV+GRADE |
| L-CNV | 0.846 [0.774, 0.908] | 0.879 [0.790, 0.954] | — | — |

**(a) NDBE samples only**, CNV source their.

| Arm | Per-sample AUROC | Patient-max AUROC | Δ per sample | Δ patient max |
|---|---|---|---|---|
| L-GRADE | 0.002 [0.000, 0.008] | 0.011 [0.000, 0.033] | — | — |
| L-CNV+GRADE | 0.724 [0.600, 0.825] | 0.727 [0.597, 0.837] | -0.057 [-0.097, -0.022] (p 0.0035) vs L-CNV | -0.039 [-0.081, 0.004] (p 0.1314) vs L-CNV |
| L-EARLY+GRADE | 0.862 [0.776, 0.930] | 0.873 [0.785, 0.945] | +0.138 [0.076, 0.209] (p 0.0005) vs L-CNV+GRADE | +0.146 [0.065, 0.231] (p 0.0015) vs L-CNV+GRADE |
| L-LATE with grade | 0.853 [0.774, 0.919] | 0.828 [0.725, 0.916] | +0.130 [0.065, 0.207] (p 0.001) vs L-CNV+GRADE | +0.101 [0.028, 0.191] (p 0.0385) vs L-CNV+GRADE |
| L-CNV | 0.781 [0.664, 0.868] | 0.765 [0.640, 0.869] | — | — |

**All of set C**, CNV source pkg.

| Arm | Per-sample AUROC | Patient-max AUROC | Δ per sample | Δ patient max |
|---|---|---|---|---|
| L-GRADE | 0.492 [0.383, 0.585] | 0.820 [0.701, 0.918] | — | — |
| L-CNV+GRADE | 0.845 [0.762, 0.917] | 0.878 [0.791, 0.957] | -0.023 [-0.055, 0.006] (p 0.1259) vs L-CNV | -0.004 [-0.047, 0.041] (p 0.8891) vs L-CNV |
| L-EARLY+GRADE | 0.892 [0.830, 0.945] | 0.911 [0.840, 0.966] | +0.047 [0.010, 0.095] (p 0.0165) vs L-CNV+GRADE | +0.033 [-0.033, 0.100] (p 0.3298) vs L-CNV+GRADE |
| L-LATE with grade | 0.915 [0.870, 0.951] | 0.918 [0.845, 0.975] | +0.070 [0.022, 0.127] (p 0.01) vs L-CNV+GRADE | +0.040 [-0.026, 0.114] (p 0.2864) vs L-CNV+GRADE |
| L-CNV | 0.868 [0.795, 0.928] | 0.882 [0.800, 0.950] | — | — |

**(a) NDBE samples only**, CNV source pkg.

| Arm | Per-sample AUROC | Patient-max AUROC | Δ per sample | Δ patient max |
|---|---|---|---|---|
| L-GRADE | 0.002 [0.000, 0.008] | 0.011 [0.000, 0.033] | — | — |
| L-CNV+GRADE | 0.762 [0.643, 0.864] | 0.788 [0.676, 0.884] | -0.053 [-0.098, -0.009] (p 0.02) vs L-CNV | -0.049 [-0.112, 0.012] (p 0.1594) vs L-CNV |
| L-EARLY+GRADE | 0.824 [0.728, 0.906] | 0.851 [0.758, 0.929] | +0.062 [0.003, 0.133] (p 0.053) vs L-CNV+GRADE | +0.063 [-0.000, 0.137] (p 0.081) vs L-CNV+GRADE |
| L-LATE with grade | 0.856 [0.787, 0.917] | 0.880 [0.792, 0.955] | +0.094 [0.032, 0.169] (p 0.008) vs L-CNV+GRADE | +0.092 [0.013, 0.182] (p 0.052) vs L-CNV+GRADE |
| L-CNV | 0.815 [0.708, 0.899] | 0.837 [0.738, 0.920] | — | — |

### 5. Frozen models (their CNV matrix, set-C scaling)

Bundle SHA-256 `17207de439433680a706d2e322838f18fe1ec17363ad647715e7f93acceee821` (MANIFEST.json lists each file's SHA-256).

| Model | λ | Features | Non-zero coefficients | In-sample AUROC (not a performance estimate) |
|---|---|---|---|---|
| L-CNV | 0.00924 | 634 | 68 | 0.996 |
| L-IMG | 0.00433 | 1536 | 158 | 0.998 |
| L-EARLY | 0.00226 | 2170 | 142 | 1.000 |
| L-LATE | mean of L-CNV and L-IMG | — | — | 1.000 |

Files: `cnv_scaling_packaged_model.csv`, `coef_L_CNV.csv`, `coef_L_EARLY.csv`, `coef_L_IMG.csv`, `extraction_settings.json`, `image_scaling.csv`, `model_info.json`.

**Interpretation.** The early- and late-fusion gains over L-CNV hold with fold-honest image scaling and on NDBE-only and pre-HGD/IMC samples (L-EARLY per-sample Δ +0.065 to +0.101, unadjusted p ≤ 0.0025), but none survives selection over the eight arms (smallest max-T adjusted p 0.117, L-LATE per sample, their matrix).

**Caveats.** (1) L-GRADE is dominated by a leave-one-patient-out artifact: leaving out a progressor lowers the training prevalence and so the intercept, which ranks that patient's samples lower; within NDBE samples (grade constant) its predictions correlate −0.838 with the patient label, giving per-sample AUROC 0.002 there and 0.492 on all of set C. Raw grade as a score, without a model, gives per-sample AUROC 0.694 on set C (descriptive, added post hoc). The same intercept shift acts on every LOPO arm, but its effect is small next to the informative features. (2) L-CNV+GRADE scoring below L-CNV (Δ −0.028, their matrix) is consistent with (1): the grade column mainly carries the prevalence-shifted intercept signal. (3) The event date is endoscopy-level ('Months before final'); 4 of 37 progressor patients have no recorded HGD/IMC endoscopy and use their final endoscopy. (4) Frozen CNV coefficients are on the scale of their shipped hg19 matrix; ACE-B CNV features built through the package pipeline on another build or batch are an approximation of that scale. The frozen image scaling uses set-C statistics.

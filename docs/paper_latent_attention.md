# Latent space and attention by fusion strategy, Killcoyne-protocol models

Status: PRE-SPECIFICATION (written 2026-10-07). Only Step 0, which reads code, was done before this commit; nothing has been run. Results are appended under the line at the end in a later commit, and this section is not edited afterwards.

**Ground rules** (as in `docs/paper_risk_strata.md`):
- Report only, with a status per item and at most one line of interpretation per question.
- Earlier documents are not edited, and patient lists stay on the cluster.

**Data.**
- Population: the 676 samples from 80 patients of the Killcoyne discovery cohort with a matched H&E slide.
  - Primary: all pre-event samples (571 samples, 75 patients).
  - Secondary: NDBE pre-event samples (438 samples, 71 patients).
- CNV source: their CNV matrix is primary; the package features are a sensitivity analysis.
- Folds: the stratified, patient-grouped 10-fold × 10-repeat CV of `kv_cv.R` (d69de24). "cfg 0" in the request is that stored run.
  - Its configurations share one fold assignment per repeat: cfg 0 = CNV (their matrix), cfg 1 = CNV (package), cfg 2 = WSI-only, cfg 3/4 = early fusion (their/package).
  - Inter fusion comes from `hz_fit.R` MODE=outer, with folds built identically.

## Step 0: architecture facts (from the code)

| Model | Where the CNV vector enters | Sample representation the model sees | Tile attention | Fold models saved |
|---|---|---|---|---|
| WSI-only (L-IMG; cfg 2) | Nowhere | `zs(IMraw, tr)`: the 1,536-dimensional mean UNI2-h tile embedding, z-scored on the training rows of the fold (`kv_common.R:5,7,22-23`). The embedding is the mean over the sample's tile bag: 256 sampled tiles per slide, median 256 per sample, range 256–768 (`km_prep.py:9-14,18`; `docs/paper_plan_killcoyne_multimodal.md:15`). | None. The tile embeddings are averaged before the model sees them. | No: only predictions are written (`kv_cv.R:13,15`) |
| Early fusion (L-EARLY; cfg 3 their, cfg 4 package) | Input level: concatenated with the slide-mean image vector (`kv_common.R:23`) | `cbind(CN, zs(IMraw, tr))`: CNV block (634 their / 632 package features, including `cx`) plus the 1,536 z-scored image features | None | No (`kv_cv.R:13,15`) |
| Inter fusion (L-INTER; their, package) | After a per-modality projection: 32 principal components per modality, fitted and z-scored on the training rows, then concatenated (`hz_fit.R:13,17`) | `cbind(pca_block(CN, tr), pca_block(zs(IMraw, tr), tr))`: 64 dimensions | None | No: only predictions are written (`hz_fit.R:33,43`) |
| Late fusion (L-LATE) | Score level: per-repeat mean of the L-CNV and L-IMG probabilities (`rs_strata.py:22`) | None | None | Not applicable |

- **Classifier.** Every model is an elastic-net logistic regression: glmnet, α 0.9, `standardize = FALSE`. λ is the class-error minimum of a 10 × 5 patient-grouped inner CV (`kv_common.R:10-18`).
- **No learned layer.** The representation each model sees is a fixed, fold-fitted transform of its inputs. Nothing between the input and the linear score is learned, so the "slide representation" is the model's input matrix.
- **Late fusion** has no joint representation. Its image half is the WSI-only model, which has no tile attention, so late fusion enters this analysis only at score level.
- **Tile attention.** No model in this tier has tile attention. The neural tier has attention: N-IMG is `AttentionMIL` and N-INTER is `IntermediateABMILCNV`; N-EARLY is an MLP on the mean embedding, without attention. That tier was run only as LOPO with 3 seeds and no saved models (`km_neural.py:10-29`) and is out of scope here, by decision on 2026-10-07.
- **Refit check, done before any analysis.** Fold models were not saved, so WSI-only, early fusion and inter fusion (their and package) are refitted for every repeat and fold with the stored seeds, folds and code (`kv_common.R`, unchanged).
  - The refitted out-of-fold predictions must equal the stored ones, with max |difference| ≤ 1e-5 per model.
  - If any model fails, the analysis stops and the failure is reported.
  - The refit also writes, per repeat and fold:
    - for WSI-only and early fusion, a fingerprint of the representation matrix: per-row sums over all 676 rows. The Python reconstruction must match it within 1e-6.
    - for inter fusion, the 64-dimensional representation matrix itself, which the probes then use.

## 1. Do fusion strategies separate the data better? (fold-honest)

**Representations per sample.** All are computed per repeat and outer fold, with the transform fitted on that fold's training rows (all 676-sample training rows, as in the model):

| Code | Representation | Notes |
|---|---|---|
| R0 | Mean of frozen UNI2-h tile embeddings, raw | No training |
| R1 | WSI-only representation | Z-scored R0. A probe that standardises its own inputs makes R1 nearly equivalent to R0; reported as observed. |
| R2 | Early fusion representation | Their matrix |
| R3 | Inter fusion representation | 64 dimensions, their matrix |
| R4 | CNV feature vector (their matrix) | Reference |
| R2-pkg, R3-pkg, R4-pkg | As above with package features | Sensitivity |

**Linear probe.**
- For each repeat and outer fold, the probe is trained on the training-fold rows of the population.
  - Pipeline: StandardScaler fitted on those rows, then L2 logistic regression (lbfgs, max_iter 5,000).
  - C is chosen from 10^k, k = −4, −3.5, …, 2, by the mean AUROC of an inner 5-fold patient-grouped, label-stratified CV on the training rows (`StratifiedGroupKFold`, shuffle, seed 1000·repeat + fold). Ties go to the smaller C.
  - The probe then scores the held-out fold's population rows.
- Fold-stratified AUROC for the progressor label: folds without both classes are skipped; the value is the mean over the 10 repeats.
- 95% CI from 2,000 patient-bootstrap draws (seed 0; draws without both classes redrawn). Resampled patients keep their folds, and the probes are not refitted.
- Probes are trained and scored separately in each population.

**Paired Δ probe AUROC.**
- Comparisons: R2 vs R1, R3 vs R1, R2 vs R3, and the same three with the package versions of R2 and R3.
- Each Δ gets a percentile CI, an unadjusted two-sided bootstrap p, and a max-T adjusted p over the three comparisons of its family (their / package).
- Max-T adjusted p is the share of draws in which max_k |(Δ*_k − Δ_k)/SD*_k| ≥ |Δ_j/SD*_j|.

**What else the representation encodes.** Same probe method and AUROC:
- scanner model: C13210 vs C13239-01 (`horizons/slide_desc.csv`);
- tissue tile count: above vs at-or-below the population median (`tissue_tiles`);
- pathology grade: NDBE vs ID/LGD. Primary population only; on NDBE samples grade is constant.
- CNV complexity: `cx` above vs at-or-below the population median, for R0–R3 only. R2 contains `cx` as an input feature, so its probe is expected to be near 1.
- **Patient identity:**
  - Within each held-out fold, find each population sample's nearest held-out neighbour by cosine distance on the representation as the fold model gives it, excluding the sample itself.
  - Report the share of samples whose nearest neighbour is from the same patient, against chance: (samples from the same patient in the fold − 1) / (samples in the fold − 1), averaged the same way.
  - Pooled over folds and averaged over repeats; R0–R4 and the package versions; point values only.

## 2. Figure: UMAP of the representations

- **In-sample, illustrative.** No separation claim rests on this figure, and it is labelled that way.
- **Rows:** R1, R2 and R3, with each transform (z-scoring; PCA plus z-scoring) fitted on all 571 pre-event samples. For this tier, "fitted with the cfg-0 hyperparameters" means only these transforms; λ does not enter a representation.
- **Columns, coloured by:**
  - progressor status;
  - patient: grey, with the 10 largest patients coloured (ties broken by sorted patient code; no codes shown);
  - scanner;
  - pathology grade (NDBE / ID / LGD).
- **UMAP settings, fixed:** umap-learn 0.5.7, n_neighbors 15, min_dist 0.1, cosine metric, random_state 0.
- **Silhouette per panel row**, by progressor status and by patient (patient silhouette on samples whose patient has ≥ 2 samples in the panel):
  - on the representation itself (cosine);
  - on the 2-D UMAP coordinates (Euclidean).
- **Supplementary:**
  - the same rows with n_neighbors 50;
  - the held-out samples of repeat 1, fold 1, embedded with that fold's transform.
- **Output:** `be_paper_figs/v3/11_F_latent_space.{pdf,png}` and `11_F_latent_space_supp.{pdf,png}`. They are drawn on the cluster, because the coordinates are row-level, and copied to `~/Downloads/be_paper_figs/v3/`.

## 3. Attention

Not applicable. Step 0 shows that no model in this tier has tile attention: WSI-only, early fusion and inter fusion all use the mean tile embedding, and late fusion inherits WSI-only. So no attention correlation, Jaccard, entropy or mass statistics are computed, no attention figure (`12_F_attention`) is made, and no top-attended tiles are written for pathologist review.

## Answers (one line each, in the results)

1. Does early or inter fusion separate progressors from non-progressors better than WSI-only (probe Δ, adjusted)?
2. What structure dominates the representations: progression, patient, scanner, grade or CNV complexity?
3. Does attention change with fusion, and does the change differ between progressors and non-progressors? This is answered as not applicable, per Step 0.

## Output

- **Scripts** (`scripts/paper_plan/`, run on Slurm via `scripts/cluster/campaign.sh` with prefix `la`):
  - `la_refit.R`: refit check and representation dumps;
  - `la_probe.py`: one task per population × repeat × representation;
  - `la_merge.py`: bootstrap, Δ and max-T;
  - `la_umap.py`: figures and silhouettes;
  - `la_render.py`.
- **Aggregates:** `results/paper_final/latent_attention/`.
- **Cluster only:** representation dumps, probe predictions and UMAP coordinates under `feasibility/paper_plan/killcoyne_mm/latent_attention/`.

---

## Results

Pre-specification commit dfac9ad; results commit bd992b0. Scripts `scripts/paper_plan/la_refit.R`, `la_probe.py`, `la_merge.py`, `la_umap.py` (Slurm via `scripts/cluster/campaign.sh`, prefixes la1 refit, la2 probes and UMAP, la3 merge, la4 UMAP rerun for the colour key, la5 scanner count), `la_scanner_xtab.py`, `la_render.py`. Aggregates `results/paper_final/latent_attention/{refit_check,probe_pre,probe_pre_ndbe,umap,scanner_xtab,answers}.json`; representation dumps, probe predictions and UMAP coordinates on the cluster only (`feasibility/paper_plan/killcoyne_mm/latent_attention/`).

### Status

| Item | Status |
|---|---|
| Step 0 architecture facts | DONE (pre-specification) |
| Step 0 refit check (≤ 1e-5) | PASS: 50 model × repeat refits, max |difference| 3.1e-13, folds identical in all |
| Representation reconstruction (row-sum fingerprints ≤ 1e-6) | PASS: max 1.4e-12 |
| 1 Linear probes, paired Δ, other structure, patient identity | DONE |
| 2 UMAP figure and silhouettes | DONE |
| 3 Attention | NOT APPLICABLE (no tile attention in this tier; Step 0) |

**Refit check per model** (max |refit − stored| over the 10 repeats × 676 out-of-fold predictions).

| Model | Repeats | Max abs difference |
|---|---|---|
| early_pkg | 10 | 1.1e-16 |
| early_their | 10 | 1.1e-16 |
| img | 10 | 1.1e-16 |
| inter_pkg | 10 | 2.6e-13 |
| inter_their | 10 | 3.1e-13 |

### Answers

1. **Early fusion yes, inter fusion no.** Probe Δ AUROC, early fusion (R2) vs WSI-only (R1), on all pre-event samples: +0.065 [+0.015, +0.112], max-T adjusted p 0.025; on NDBE samples +0.085 [+0.033, +0.141], p 0.008. Inter fusion (R3) vs R1: −0.005 [−0.064, +0.055], p 0.98. With package features the early-fusion gain is not significant (+0.055 [−0.002, +0.105], adjusted p 0.092).
2. **Scanner dominates the image-based representations, then patient.** A probe identifies the scanner perfectly from R0–R3 (AUROC 1.000), against 0.55 from CNV alone. A sample's nearest held-out neighbour is from the same patient 62–84% of the time (93% for CNV), against 16% by chance. Progression (0.84–0.91), grade (0.81–0.87) and tile count (0.71–0.79) come next, and the image alone does not encode CNV complexity (0.48). Scanner is not confounded with progression: 28% of pre-event samples are from progressors on either scanner, and 22% vs 24% of NDBE samples (descriptive, not pre-specified).
3. **Not applicable.** No model in this tier has tile attention (Step 0); late fusion's image half is WSI-only.

### 1. Linear probes (fold-stratified AUROC, mean over 10 repeats; 95% patient-bootstrap CI, 2,000 draws)

**All pre-event samples** (571 samples, 75 patients, 161 progressor samples).

| Representation | Progressor | Scanner (C13210 vs C13239-01) | Tissue tiles > median | Grade ID/LGD vs NDBE | cx > median | Nearest neighbour same patient (chance) |
|---|---|---|---|---|---|---|
| R0 mean UNI2-h embedding (raw) | 0.849 [0.801, 0.892] | 1.000 [1.000, 1.000] | 0.790 [0.742, 0.833] | 0.866 [0.801, 0.916] | 0.484 [0.438, 0.533] | 0.623 (0.162) |
| R1 WSI-only (z-scored mean embedding) | 0.849 [0.801, 0.892] | 1.000 [1.000, 1.000] | 0.790 [0.742, 0.833] | 0.866 [0.801, 0.916] | 0.484 [0.437, 0.533] | 0.651 (0.162) |
| R2 early fusion (their) | 0.913 [0.856, 0.957] | 1.000 [1.000, 1.000] | 0.768 [0.723, 0.814] | 0.847 [0.779, 0.903] | 0.651 [0.582, 0.714] | 0.722 (0.162) |
| R3 inter fusion (their, 64-d) | 0.844 [0.775, 0.904] | 1.000 [1.000, 1.000] | 0.711 [0.648, 0.761] | 0.805 [0.728, 0.873] | 0.608 [0.536, 0.677] | 0.841 (0.162) |
| R4 CNV (their) | 0.859 [0.788, 0.916] | 0.546 [0.425, 0.652] | 0.599 [0.531, 0.658] | 0.606 [0.528, 0.706] | — | 0.933 (0.162) |
| R2 early fusion (package) | 0.904 [0.836, 0.952] | 1.000 [1.000, 1.000] | 0.783 [0.732, 0.829] | 0.848 [0.778, 0.905] | 0.838 [0.786, 0.884] | 0.741 (0.162) |
| R3 inter fusion (package) | 0.845 [0.775, 0.902] | 1.000 [0.999, 1.000] | 0.726 [0.662, 0.776] | 0.814 [0.735, 0.881] | 0.660 [0.603, 0.719] | 0.840 (0.162) |
| R4 CNV (package) | 0.852 [0.774, 0.912] | 0.585 [0.467, 0.685] | 0.610 [0.551, 0.663] | 0.596 [0.525, 0.689] | — | 0.940 (0.162) |

**NDBE pre-event samples** (438 samples, 71 patients, 104 progressor samples).

| Representation | Progressor | Scanner (C13210 vs C13239-01) | Tissue tiles > median | cx > median | Nearest neighbour same patient (chance) |
|---|---|---|---|---|---|
| R0 mean UNI2-h embedding (raw) | 0.819 [0.762, 0.872] | 1.000 [1.000, 1.000] | 0.767 [0.708, 0.817] | 0.495 [0.430, 0.553] | 0.608 (0.169) |
| R1 WSI-only (z-scored mean embedding) | 0.819 [0.762, 0.872] | 1.000 [1.000, 1.000] | 0.767 [0.708, 0.817] | 0.495 [0.430, 0.553] | 0.629 (0.169) |
| R2 early fusion (their) | 0.903 [0.834, 0.957] | 1.000 [1.000, 1.000] | 0.758 [0.705, 0.812] | 0.646 [0.572, 0.714] | 0.690 (0.169) |
| R3 inter fusion (their, 64-d) | 0.840 [0.762, 0.911] | 1.000 [1.000, 1.000] | 0.705 [0.641, 0.760] | 0.626 [0.543, 0.697] | 0.817 (0.169) |
| R4 CNV (their) | 0.847 [0.768, 0.917] | 0.517 [0.403, 0.597] | 0.600 [0.524, 0.668] | — | 0.901 (0.169) |
| R2 early fusion (package) | 0.871 [0.792, 0.939] | 1.000 [1.000, 1.000] | 0.780 [0.726, 0.831] | 0.795 [0.731, 0.853] | 0.708 (0.169) |
| R3 inter fusion (package) | 0.854 [0.778, 0.916] | 1.000 [1.000, 1.000] | 0.725 [0.667, 0.779] | 0.668 [0.604, 0.729] | 0.815 (0.169) |
| R4 CNV (package) | 0.812 [0.715, 0.899] | 0.546 [0.441, 0.638] | 0.617 [0.549, 0.669] | — | 0.906 (0.169) |

**Scanner by progressor status** (descriptive, not pre-specified; samples, with patients who have any sample on that scanner in parentheses).

| Population | Scanner | Progressor samples (patients) | Non-progressor samples (patients) | Progressor share of samples |
|---|---|---|---|---|
| All pre-event samples | C13210 | 39 (9) | 100 (18) | 0.28 |
| All pre-event samples | C13239-01 | 122 (31) | 310 (40) | 0.28 |
| NDBE pre-event samples | C13210 | 21 (8) | 74 (16) | 0.22 |
| NDBE pre-event samples | C13239-01 | 83 (26) | 260 (40) | 0.24 |

Patients with samples on both scanners: All pre-event samples 23; NDBE pre-event samples 19.

**Paired Δ progressor-probe AUROC** (same draws; max-T adjusted p over the three comparisons of each family).

| Population | Comparison | Δ AUROC [95% CI] | p unadjusted | p max-T adjusted |
|---|---|---|---|---|
| All pre-event samples | R2 vs R1 | +0.065 [+0.015, +0.112] | 0.011 | 0.0245 |
| All pre-event samples | R3 vs R1 | -0.005 [-0.064, +0.055] | 0.921 | 0.9805 |
| All pre-event samples | R2 vs R3 | +0.069 [+0.039, +0.105] | < 0.0005 | < 0.0005 |
| All pre-event samples | R2 (package) vs R1 | +0.055 [-0.002, +0.105] | 0.056 | 0.092 |
| All pre-event samples | R3 (package) vs R1 | -0.004 [-0.070, +0.053] | 0.957 | 0.9955 |
| All pre-event samples | R2 (package) vs R3 (package) | +0.059 [+0.013, +0.108] | 0.006 | 0.041 |
| NDBE pre-event samples | R2 vs R1 | +0.085 [+0.033, +0.141] | 0.002 | 0.008 |
| NDBE pre-event samples | R3 vs R1 | +0.021 [-0.040, +0.080] | 0.403 | 0.737 |
| NDBE pre-event samples | R2 vs R3 | +0.064 [+0.028, +0.103] | < 0.0005 | 0.003 |
| NDBE pre-event samples | R2 (package) vs R1 | +0.052 [-0.016, +0.116] | 0.108 | 0.23 |
| NDBE pre-event samples | R3 (package) vs R1 | +0.035 [-0.019, +0.089] | 0.201 | 0.3765 |
| NDBE pre-event samples | R2 (package) vs R3 (package) | +0.017 [-0.026, +0.068] | 0.409 | 0.741 |

Probe C (median over folds and repeats, progressor): All pre-event samples: R0 10, R1 10, R2 20.8, R3 0.0316, R4 0.0316, R2p 31.6, R3p 0.316, R4p 100; NDBE pre-event samples: R0 1, R1 1, R2 31.6, R3 0.316, R4 31.6, R2p 100, R3p 1, R4p 100.

### 2. UMAP (in-sample, illustrative)

Figures `~/Downloads/be_paper_figs/v3/11_F_latent_space.{pdf,png}` (rows R1, R2, R3; their matrix; 571 pre-event samples) and `11_F_latent_space_supp.{pdf,png}` (n_neighbors 50; held-out pre-event samples of repeat 1, fold 1, 52 samples). umap-learn 0.5.7, n_neighbors 15, min_dist 0.1, cosine, seed 0.

| Set | Representation | Silhouette, progressor (representation, cosine) | Silhouette, progressor (UMAP) | Silhouette, patient (representation, cosine) | Silhouette, patient (UMAP) | Samples in patient silhouette |
|---|---|---|---|---|---|---|
| n_neighbors 15 | R1 | 0.020 | 0.002 | -0.166 | -0.479 | 569 |
| n_neighbors 15 | R2 | 0.022 | 0.035 | -0.087 | -0.485 | 569 |
| n_neighbors 15 | R3 | 0.027 | 0.026 | 0.166 | -0.081 | 569 |
| n_neighbors 50 | R1 | 0.020 | 0.018 | -0.166 | -0.533 | 569 |
| n_neighbors 50 | R2 | 0.022 | 0.010 | -0.087 | -0.547 | 569 |
| n_neighbors 50 | R3 | 0.027 | 0.053 | 0.166 | -0.127 | 569 |
| held-out r1 f1 | R1 | 0.085 | 0.125 | 0.111 | 0.032 | 52 |
| held-out r1 f1 | R2 | 0.086 | 0.143 | 0.159 | 0.062 | 52 |
| held-out r1 f1 | R3 | 0.094 | 0.174 | 0.206 | 0.212 | 52 |

Results with the CIs at 1.000 are saturated: every held-out fold is separated perfectly in every repeat and bootstrap draw.

### 3. Attention

Not applicable (Step 0): no model in this tier has tile attention; late fusion's image half is WSI-only. No attention statistics, no `12_F_attention` figure and no top-attended tiles for pathologist review.

### Deviations and caveats

- Not pre-specified, descriptive only: scanner by progressor status (`la_scanner_xtab.py`, `scanner_xtab.json`), added to interpret answer 2.
- The UMAP task was run twice; the second run only added the grade colour key to the column title. UMAP with random_state 0 was not bit-reproducible between the two runs, which ran on different nodes. Silhouettes on the representations are identical, but UMAP-space silhouettes changed by up to 0.09 (largest change: R3, held-out, progressor, 0.252 → 0.174). The figure and the table come from the second run; UMAP-space silhouettes are illustrative only.
- The representations are fixed, fold-fitted transforms of the inputs (Step 0), not learned embeddings; a probe on R2 or R3 is close to refitting the corresponding model with an L2 instead of an elastic-net penalty, so the probe Δ largely restates the model comparison.
- R2 contains `cx` as an input feature; the pre-specification expected its cx probe near 1, but it is 0.651 (their matrix) and 0.838 (package) on pre-event samples, because the L2 probe spreads its weight over about 2,170 standardised features. R4 was not probed for cx (pre-specified).
- Probes are not refitted within the bootstrap; the CIs reflect sampling of patients for fixed probes.
- Nearest-neighbour patient identity is a point estimate (no CI, pre-specified); chance depends on how many samples each patient contributes to the fold.
- Matched case–control design; the progressor label is patient status, shared by all samples of a patient, so patient structure and label structure are partly confounded.


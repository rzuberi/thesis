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

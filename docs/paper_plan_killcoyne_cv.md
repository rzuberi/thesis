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

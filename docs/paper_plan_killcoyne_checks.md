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

# Review round 4: analyses requested by reviewers (excluding ACE-B)

Status: PRE-SPECIFICATION (written 2026-10-15). Nothing below has been run. Results are appended under the line at the end in a later commit; this section is not edited afterwards.

Purpose: answer the objections from the third and fourth internal reviews of the manuscript. Drafts v3 and v4 were reviewed by 21 and 5 reviewers; the syntheses are kept outside the repository. Part A re-scores stored predictions and reads the sample sheet. Part B re-segments copy number per sample and refits linear models on existing features. Nothing changes the frozen bundles or the registered ACE-B analysis, and no ACE-B file is read.

**Ground rules**, as in `docs/paper_review_round2_analyses.md` (d681783):
- report only, with a status per item and at most one line of interpretation per item;
- earlier documents are not edited;
- row-level data stay on the cluster;
- the cohort is never referred to by its internal short label.

**Population, data and conventions.** Unchanged from round 2:
- Primary population: all pre-event samples of the 676 samples from 80 patients of the Killcoyne discovery cohort with a matched H&E slide (571 samples, 75 patients).
- Their copy-number matrix is primary.
- Stored outer and inner predictions, triage rules, comparators, B\* training matching and evaluation matching come from `tb_common.py` and `rv2_round2.py`.
- "Single model" means per-repeat calls, with each statistic averaged over the 10 repeats.
- Patient bootstrap: 2,000 draws, `RandomState(0)`, resampled patients keep their folds.
- One-sided 95% lower bound = 5th percentile.
- Unless stated, every triage comparison reports the single model, against (B) at its own threshold and against B\* training-matched. For each it gives Δ sensitivity (with one-sided bound), Δ specificity and the share sequenced (with pass/fail against the 70% cap).

**Decision fixed now for the next draft.** The robustness rule written into draft v4 (a claim is "not robust" if it fails two or more sensitivity analyses) was chosen after the results were known, and it is withdrawn. Instead, both headline claims are reported against the same set of sensitivity analyses (R33), as tables and forest plots without a summary rule. The text describes which analyses pass and which fail.

## Part A. Stored predictions and the sample sheet

### R31. Sequencing batch and processing variables

From Killcoyne's sample sheet (on the cluster), joined to the 676 samples and to the 571 pre-event samples. Variables: `Batch`, SLX run identifier, the pilot-library flag, number of reads, % Barrett's cellularity, and the sheet's exclusion flags (`excluded`, `remove`, `inconsistency`, `notes on label review`).

- **(a) Cross-tabulation by status.** Batch, SLX run and pilot flag against status, by patient (a patient's modal value; whether patients span several batches) and by pre-event sample. Fisher's exact test (Monte Carlo p for tables larger than 2 × 2).
- **(b) Raw-score AUROC.** Fold-stratified AUROC for progression of read count and % cellularity as raw scores.
  - For batch and SLX, use a fold-honest target encoding: for each held-out sample, the progressor-sample share of its batch among that fold's training samples. Batches unseen in training get the training share.
- **(c) Within-batch pairs.** Fold-stratified AUROC of L-CNV, L-IMG and L-LATE counting only case–control pairs whose two samples share a batch, with Δ L-IMG − L-CNV and its one-sided bound. The same for SLX run if at least 100 within-run pairs exist per repeat.
- **(d) Does the image encode batch?** A batch probe on the UNI2-h slide-mean embedding. For each batch with at least 5 patients, fit a one-vs-rest logistic regression (L2, default C), patient-grouped 5-fold cross-validation, and report the AUROC. Also report an image-only batch probe within non-progressors.
- **(e) Does the triage depend on batch?** Single-model triage − B\* within the largest batch.
- **(f) Exclusion flags.** Counts of analysed samples carrying each flag, by status.

### R32. Tissue strata and a tissue-adjusted gate

- **(a) Triage within tissue strata.** In each stratum (tissue tiles < 256 and ≥ 256, as in R5 and R18): single-model triage − (B), − B\* (training-matched) and − B\* (evaluation-matched). Report Δ sensitivity with its bound, Δ specificity and share sequenced, plus the between-stratum interaction for Δ sensitivity against B\*, with a CI.
- **(b) Tissue-adjusted gate.** Replace the L-IMG gate by L-IMG residualised on biopsy year and log tissue tiles.
  - Residualisation follows R5, done separately for each set of predictions: per repeat on the held-out scores; for each inner (repeat, fold) set on the inner scores, with coefficients fitted on that set's training rows only.
  - Then re-choose every cut-off by the primary rule.
  - The middle-band call stays L-LATE.
  - Report the single-model triage's share, sensitivity and specificity, and Δ against (B) and B\*.

### R33. One robustness table for each headline claim

**Claim T: triage versus B\* (training-matched), single model.** One row per analysis, each with Δ sensitivity [95% CI], the one-sided bound, Δ specificity, the share sequenced and whether the 70% cap is met:
1. primary;
2. NDBE pre-event;
3. package features;
4. pre-event-only training (F1);
5. never-dysplastic patients;
6. H-optimus-0 gate (F5);
7. excluding progressor samples within 1 year (single-model recomputation);
8. each of the 9 cut-off grid cells (B\* re-matched to each cell's own training specificity);
9. tissue strata (R32a);
10. tissue-adjusted gate (R32b);
11. λ by deviance (requires B5 below);
12. patient-weighted (R34);
13. earliest pre-event endoscopy per patient only (all samples of that endoscopy);
14. selection-inclusive;
15. evaluation-matched;
16. 10-model vote;
17. between-repeat variance added;
18. refit bootstrap (F3);
19. per-sample re-segmented copy number (R36).

**Claim H: L-IMG versus L-CNV, ΔAUROC.** The same rows wherever they apply, adding the existing Table 5 rows, so the two tables use the same analyses where both are defined. Rows that do not apply are marked "not applicable" with the reason.

**Monte Carlo error.** For both claims, the Monte Carlo SE of the refit bootstrap's 5th percentile (bootstrap of the 200 draws, 2,000 resamples) and the share of refit draws below −0.05.

**The pre-specified test.** For comparison 1 (triage versus (B), as registered on voted calls), the same rows as for Claim T, voted and single model.

### R34. Patient-weighted triage

Each pre-event sample is weighted by 1/nᵢ, where nᵢ is its patient's number of pre-event samples. Report weighted sensitivity and specificity of the triage, (B), (C), B\* and C\* (single model), and the weighted Δ against (B) and B\* with patient-bootstrap CIs and bounds.

### R35. The deployable object and band stability

- **(a) Copy-number-only middle band, single model.** The pre-specified variant (`triage_CNV`): Δ against (B) and against B\*, the latter re-matched to this variant's own training specificity.
- **(b) Frozen cut-offs on held-out predictions.** Apply the frozen median cut-offs (t_low, t_high, t_seq) to each repeat's held-out predictions separately, then average over repeats. Report share, sensitivity and specificity, and Δ against (B) at its frozen threshold (0.314) and against B\* (training-matched per fold). These cut-offs are medians over folds that include the evaluated fold, so this is labelled "frozen cut-offs on held-out predictions, not out of fold".
- **(c) Band stability.** Per sample, the number of repeats in its modal band. Report the distribution, by class and band, and the share of samples whose single-model call differs between repeats.

## Part B. Re-segmentation and refits (cluster; existing scripts, folds unchanged)

### R36. Per-sample segmentation of copy number

- **Rebuilding the features.** Rebuild the package features with `segmentRawData` applied to each sample on its own instead of jointly per patient. Everything else is unchanged: the same package, the same hg38 adaptations as `docs/paper_plan_killcoyne_reconcile.md`, then `tileSegments`, `subtractArms` and `scoreCX`.
- **Checks.** First confirm that the stored package features were segmented jointly, by comparing them with a re-run of the joint segmentation on one patient. Then report how much the per-sample features differ from the joint ones: per-sample correlation and the change in cx.
- **Refits.** L-CNV (package per-sample features) outer 10 × 10 and inner 5-fold, with `kv_cv.R` and `hz_fit.R` logic and identical folds. L-LATE is the mean with stored L-IMG.
- **Reported:**
  - fold-stratified AUROC of L-CNV and L-LATE;
  - Δ L-IMG − L-CNV with its bound;
  - single-model triage − (B), − B\* and − C\*, with B\* and C\* re-matched;
  - the same with the joint package features, for reference.
- **If time allows**, a "past-only" variant that segments each sample jointly with only its patient's samples from the same or earlier endoscopies, reported the same way.

### B5. Inner predictions with λ by deviance

`hz_fit.R` inner predictions for L-CNV (their matrix) and L-IMG with λ at the minimum binomial deviance (as F4), for all repeat × fold. This allows the deviance-λ row of R33 for the triage.

## Scripts and running

- **Part A:** `scripts/paper_plan/rv4_round4.py` (TASK = r31 … r35), sharing `tb_common.py`.
- **Part B:** `scripts/paper_plan/rv4_reseg.R`, `rv4_refit.R` and `rv4_refit_metrics.py`.
- **Renderer:** `rv4_render.py`.
- **Running:** on Slurm via `scripts/cluster/campaign.sh` with prefixes rv4a and rv4b. Never on the login node.
- **Outputs:** aggregates to `results/paper_final/review_round4/`. Row-level outputs stay under the cluster `killcoyne_mm/review_round4/`.

---

## Results

Rendered by `scripts/paper_plan/rv4_render.py` from `results/paper_final/review_round4/` (Part A results 9d50255, Part B results 658c9fc).

| Item | Status |
|---|---|
| R31 batch and processing variables | DONE |
| R32 tissue strata, tissue-adjusted gate | DONE |
| R33 robustness tables | DONE (all rows filled) |
| R34 patient-weighted triage | DONE |
| R35 copy-number-only middle band, frozen cut-offs, band stability | DONE |
| R36 per-sample re-segmentation | DONE (plus past-only variant) |
| B5 inner predictions with λ by deviance | DONE |

### R31. Sequencing batch and processing variables

Pre-event samples by batch (progressor / non-progressor). Fisher's exact test (Monte Carlo, 10,000): p < 0.0001.

| Batch | Progressor | Non-progressor |
|---|---|---|
| Batch 1 | 23 | 42 |
| Batch 16S | 4 | 7 |
| Batch 2 | 25 | 29 |
| Batch 3 | 22 | 35 |
| Batch 4 | 17 | 40 |
| Batch 5 | 0 | 86 |
| Batch 6 | 0 | 78 |
| Batch 8 | 49 | 0 |
| Batch 9 | 0 | 46 |
| Exome Subcohort | 17 | 34 |
| NP Pilot Study | 0 | 13 |
| Progressor Pilot Study | 4 | 0 |

Fold-stratified AUROC as raw scores (fold-honest target encoding for batch and run):

| Variable | AUROC [95% CI] |
|---|---|
| Batch | 0.759 [+0.641, +0.865] |
| SLX run | 0.772 [+0.657, +0.873] |
| Number of reads | 0.472 [+0.375, +0.568] |
| % Barrett's cellularity (111 samples) | 0.576 [+0.296, +0.786] |
| Pilot study | 0.497 [+0.469, +0.524] |

Within-batch pairs only (283 to 596 pairs per repeat):

| Pairs | L-CNV | L-IMG | L-LATE | Δ L-IMG − L-CNV [95% CI] | One-sided bound |
|---|---|---|---|---|---|
| same batch | 0.790 | 0.841 | 0.893 | +0.051 [-0.071, +0.184] | -0.059 |
| same SLX run | 0.783 | 0.846 | 0.891 | +0.062 [-0.065, +0.190] | -0.049 |

Batch probe on the UNI2-h embedding (patient-grouped 5-fold, one-vs-rest, batches with ≥ 5 patients): mean AUROC 0.639; Batch 1 0.802, Batch 16S 0.441, Batch 2 0.533, Batch 3 0.691, Batch 4 0.571, Batch 5 0.596, Batch 6 0.590, Batch 8 0.810, Exome Subcohort 0.713.

Largest batch (Batch 5, 86 samples) holds no progressor samples, so Δ sensitivity is not estimable there; triage specificity 0.778 against B\* 0.781.

Sheet flags among the 571 pre-event samples (progressor / non-progressor): excluded 36 / 21; remove 1 / 2; inconsistency 8 / 0; label-review note 54 / 26.

Batch is strongly associated with status by design (several batches are single-class), but discrimination within batch is close to the overall values, and the image embedding encodes batch only weakly.

### R32. Tissue strata and a tissue-adjusted gate

Single model. Δ = triage − comparator.

| Setting | Triage sensitivity / specificity | Share sequenced | Δ sens vs B\* [95% CI] | Bound | Δ spec vs B\* | Δ sens vs (B) | Bound |
|---|---|---|---|---|---|---|---|
| < 256 tissue tiles (293 samples) | 0.925 / 0.704 | 0.423 | -0.008 [-0.026, +0.005] | -0.022 | +0.042 | +0.025 | +0.003 |
| ≥ 256 tissue tiles (278 samples) | 0.817 / 0.689 | 0.496 | -0.022 [-0.055, +0.007] | -0.050 | +0.020 | +0.039 | +0.007 |
| tissue- and year-adjusted gate (all 571) | 0.870 / 0.669 | 0.577 | -0.012 [-0.031, +0.005] | -0.028 | +0.008 | +0.038 | +0.014 |

Interaction (< 256 minus ≥ 256): Δ sensitivity against B\* +0.014 [-0.020, +0.051]; ΔAUROC L-IMG − L-CNV +0.129 [-0.004, +0.246].

### R33. Robustness tables for both headline claims

No summary rule (decision fixed in the pre-specification). "Within" = one-sided 95% lower bound > −0.05; the 70% cap applies to the share sequenced.

**Claim T: triage versus B\* (training-matched), single model.**

| # | Analysis | Δ sensitivity [95% CI] | One-sided bound | Within | Δ specificity | Share sequenced | Cap met |
|---|---|---|---|---|---|---|---|
| 1 | primary: all pre-event samples | -0.016 [-0.036, +0.001] | -0.032 | yes | +0.032 | 0.458 | yes |
| 2 | NDBE pre-event samples | -0.014 [-0.038, +0.004] | -0.034 | yes | +0.027 | 0.491 | yes |
| 3 | package features | -0.007 [-0.023, +0.007] | -0.020 | yes | +0.024 | 0.458 | yes |
| 4 | pre-event-only training (F1) | -0.009 [-0.024, +0.005] | -0.021 | yes | +0.031 | 0.443 | yes |
| 5 | patients never dysplastic before the event | -0.014 [-0.039, +0.008] | -0.035 | yes | +0.028 | 0.441 | yes |
| 6 | H-optimus-0 gate (F5) | -0.008 [-0.024, +0.005] | -0.022 | yes | +0.002 | 0.668 | yes |
| 7 | excluding progressor samples within 1 year | -0.006 [-0.021, +0.010] | -0.019 | yes | +0.032 | 0.469 | yes |
| 8 | cut-off grid cell: t_low 90% training sensitivity, t_high 85% training specificity | -0.039 [-0.070, -0.008] | -0.064 | no | +0.044 | 0.298 | yes |
| 8 | cut-off grid cell: t_low 90% training sensitivity, t_high 90% training specificity | -0.039 [-0.068, -0.008] | -0.063 | no | +0.042 | 0.342 | yes |
| 8 | cut-off grid cell: t_low 90% training sensitivity, t_high 95% training specificity | -0.031 [-0.058, -0.004] | -0.053 | no | +0.029 | 0.401 | yes |
| 8 | cut-off grid cell: t_low 95% training sensitivity, t_high 85% training specificity | -0.016 [-0.037, +0.005] | -0.033 | yes | +0.030 | 0.414 | yes |
| 8 | cut-off grid cell: t_low 95% training sensitivity, t_high 90% training specificity (primary cell) | -0.016 [-0.036, +0.001] | -0.032 | yes | +0.032 | 0.458 | yes |
| 8 | cut-off grid cell: t_low 95% training sensitivity, t_high 95% training specificity | -0.016 [-0.033, +0.000] | -0.030 | yes | +0.033 | 0.517 | yes |
| 8 | cut-off grid cell: t_low 98% training sensitivity, t_high 85% training specificity | -0.002 [-0.014, +0.008] | -0.012 | yes | +0.016 | 0.542 | yes |
| 8 | cut-off grid cell: t_low 98% training sensitivity, t_high 90% training specificity | -0.001 [-0.012, +0.010] | -0.010 | yes | +0.015 | 0.586 | yes |
| 8 | cut-off grid cell: t_low 98% training sensitivity, t_high 95% training specificity | -0.002 [-0.013, +0.007] | -0.011 | yes | +0.016 | 0.645 | yes |
| 9 | tissue stratum: < 256 tissue tiles (R32a) | -0.008 [-0.026, +0.005] | -0.022 | yes | +0.042 | 0.423 | yes |
| 9 | tissue stratum: >= 256 tissue tiles (R32a) | -0.022 [-0.055, +0.007] | -0.050 | no | +0.020 | 0.496 | yes |
| T5 | tissue-matched pairs: same tissue tertile (Table 5) | not applicable: pair-based AUROC only | | | | | |
| 10 | tissue-adjusted gate (R32b) | -0.012 [-0.031, +0.005] | -0.028 | yes | +0.008 | 0.577 | yes |
| 11 | lambda by deviance (B5) | -0.006 [-0.024, +0.007] | -0.020 | yes | +0.012 | 0.526 | yes |
| 12 | patient-weighted (R34) | -0.015 [-0.033, +0.001] | -0.030 | yes | +0.020 | 0.432 | yes |
| 13 | earliest pre-event endoscopy per patient (all its samples) | -0.013 [-0.039, +0.009] | -0.034 | yes | +0.025 | 0.460 | yes |
| 14 | selection-inclusive (every cut-off re-chosen in each draw) | -0.016 [-0.043, +0.001] | -0.038 | yes | +0.032 | 0.458 | yes |
| 15 | evaluation-matched B* | +0.003 [-0.026, +0.035] | -0.022 | yes |  | 0.458 | yes |
| 16 | 10-model vote | -0.006 [-0.051, +0.034] | -0.044 | yes | +0.034 | 0.458 | yes |
| 17 | between-repeat variance added | -0.016 [-0.052, +0.020] | -0.046 | yes | +0.032 | 0.458 | yes |
| 18 | refit bootstrap (F3, 200 draws) | -0.018 [-0.079, +0.040] | -0.069 | no | +0.017 | 0.567 | yes |
| 19 | per-sample re-segmented copy number (R36) | -0.006 [-0.017, +0.005] | -0.016 | yes | +0.008 | 0.458 | yes |
| 19b | past-only re-segmented copy number (R36, extra row) | -0.009 [-0.021, +0.002] | -0.019 | yes | +0.029 | 0.458 | yes |
| T5 | package features, pre-event-only training (Table 5) | -0.005 [-0.015, +0.005] | -0.013 | yes | +0.033 | 0.443 | yes |
| T5 | earliest pre-event sample per patient (Table 5) | +0.003 [-0.033, +0.033] | -0.027 | yes | +0.028 | 0.475 | yes |

**Claim H: L-IMG versus L-CNV, ΔAUROC.**

| # | Analysis | Δ AUROC | One-sided bound | Within |
|---|---|---|---|---|
| 1 | primary: all pre-event samples | +0.045 | -0.025 | yes |
| 2 | NDBE pre-event samples | +0.047 | -0.030 | yes |
| 3 | package features | +0.002 | -0.062 | no |
| 4 | pre-event-only training (F1) | +0.074 | -0.000 | yes |
| 5 | patients never dysplastic before the event | +0.057 | -0.059 | no |
| 6 | H-optimus-0 gate (F5) | +0.003 | -0.074 | no |
| 7 | excluding progressor samples within 1 year | +0.057 | -0.010 | yes |
| 8 | cut-off grid cell: t_low 90% training sensitivity, t_high 85% training specificity | not applicable: AUROC does not depend on the cut-offs | | |
| 8 | cut-off grid cell: t_low 90% training sensitivity, t_high 90% training specificity | not applicable: AUROC does not depend on the cut-offs | | |
| 8 | cut-off grid cell: t_low 90% training sensitivity, t_high 95% training specificity | not applicable: AUROC does not depend on the cut-offs | | |
| 8 | cut-off grid cell: t_low 95% training sensitivity, t_high 85% training specificity | not applicable: AUROC does not depend on the cut-offs | | |
| 8 | cut-off grid cell: t_low 95% training sensitivity, t_high 90% training specificity (primary cell) | not applicable: AUROC does not depend on the cut-offs | | |
| 8 | cut-off grid cell: t_low 95% training sensitivity, t_high 95% training specificity | not applicable: AUROC does not depend on the cut-offs | | |
| 8 | cut-off grid cell: t_low 98% training sensitivity, t_high 85% training specificity | not applicable: AUROC does not depend on the cut-offs | | |
| 8 | cut-off grid cell: t_low 98% training sensitivity, t_high 90% training specificity | not applicable: AUROC does not depend on the cut-offs | | |
| 8 | cut-off grid cell: t_low 98% training sensitivity, t_high 95% training specificity | not applicable: AUROC does not depend on the cut-offs | | |
| 9 | tissue stratum: < 256 tissue tiles (R32a) | +0.113 | +0.021 | yes |
| 9 | tissue stratum: >= 256 tissue tiles (R32a) | -0.015 | -0.095 | no |
| T5 | tissue-matched pairs: same tissue tertile (Table 5) | +0.036 | -0.039 | yes |
| 10 | tissue-adjusted gate (R32b) | +0.029 | -0.043 | yes |
| 11 | lambda by deviance (B5) | +0.021 | -0.050 | no |
| 12 | patient-weighted (R34) | +0.030 | -0.034 | yes |
| 13 | earliest pre-event endoscopy per patient (all its samples) | +0.035 | -0.070 | no |
| 14 | selection-inclusive (every cut-off re-chosen in each draw) | not applicable: AUROC selects no cut-off | | |
| 15 | evaluation-matched B* | not applicable: no threshold in AUROC | | |
| 16 | 10-model vote | not applicable: AUROC is computed per repeat and averaged; the vote is a call rule | | |
| 17 | between-repeat variance added | +0.045 | -0.046 | yes |
| 18 | refit bootstrap (F3, 200 draws) | +0.070 | -0.083 | no |
| 19 | per-sample re-segmented copy number (R36) | +0.062 | +0.013 | yes |
| 19b | past-only re-segmented copy number (R36, extra row) | +0.047 | -0.013 | yes |
| T5 | package features, pre-event-only training (Table 5) | +0.042 | -0.025 | yes |
| T5 | earliest pre-event sample per patient (Table 5) | +0.029 | -0.075 | no |

Claim T: 26 of 31 analyses within the margin; the share sequenced met the cap in 31. Claim H: 12 of 20 within the margin.

Refit bootstrap (200 draws), Monte Carlo error of the 5th percentile:

| Claim | 5th percentile | MC SE | MC 95% interval | Share of draws < −0.05 |
|---|---|---|---|---|
| T: triage − B\* | -0.069 | 0.0046 | [-0.079, -0.062] | 0.145 |
| H: L-IMG − L-CNV | -0.083 | 0.0131 | [-0.114, -0.069] | 0.110 |
| Pre-specified: triage − (B) | -0.038 | 0.0069 | [-0.055, -0.031] | 0.035 |

### R34. Patient-weighted triage

Weights 1/nᵢ. Weighted sensitivity / specificity: triage 0.868 / 0.702; (B) 0.830 / 0.773; B\* 0.882 / 0.682; C\* 0.804 / 0.709. Weighted share sequenced 0.432.
Δ sensitivity vs (B) +0.037 [+0.006, +0.069], bound +0.012; vs B\* -0.015 [-0.033, +0.001], bound -0.030; vs C\* +0.063, bound +0.018.

### R35. The deployable object and band stability

**(a) Copy-number-only middle band, single model:** sensitivity 0.863, specificity 0.672; vs (B) +0.031 (bound +0.005); vs re-matched B\* -0.030 (bound -0.049).

**(b) frozen cut-offs on held-out predictions, not out of fold (medians over folds that include the evaluated fold):** share 0.454, sensitivity 0.860, specificity 0.701; vs (B) at 0.314 +0.028 (bound +0.007, Δspec -0.047); vs B\* -0.021 (bound -0.043, Δspec +0.036).

**(c) Band stability:** 35% of samples in the same band in all 10 repeats; mean 8.4 repeats in the modal band (progressors 8.9, non-progressors 8.2). The single-model call differs between repeats for 38% of samples (modal low band 22%, middle 63%, high 7%).

### R36. Per-sample segmentation of copy number

Checks: joint re-segmentation of one patient reproduced the stored package features exactly (max |Δ| 0.0), so the stored features were segmented jointly per patient; the refit path reproduced stored package predictions exactly (max |Δ| 0.0).
Per-sample versus joint features: per-sample correlation of raw 5-Mb tiles median 0.979, of the final standardised block median 0.747; cx correlation 0.754.

| Copy-number features | L-CNV | L-LATE | Δ L-IMG − L-CNV (bound) | Triage − (B) Δ sens (bound) | Triage − B\* (bound) | Triage − C\* (bound) |
|---|---|---|---|---|---|---|
| per-sample segmentation | 0.785 | 0.880 | +0.062 (+0.013) | +0.043 (+0.019) | -0.006 (-0.016) | +0.058 (+0.027) |
| past-only segmentation | 0.800 | 0.881 | +0.047 (-0.013) | +0.035 (+0.015) | -0.009 (-0.019) | +0.045 (+0.016) |
| joint (stored package features) | 0.845 | 0.903 | +0.002 (-0.062) | +0.039 (+0.014) | -0.007 (-0.020) | +0.090 (+0.054) |

Removing joint segmentation lowered copy-number discrimination; the H&E model was then non-inferior with a lower bound above zero, and the triage comparisons were unchanged.

### B5. λ by deviance for the triage

Deviance-λ outer (round-2 F4) and inner (B5) predictions, cut-offs re-chosen on them; full fields in `b5.json`. The triage row appears in the Claim T table (row 11).

### Checks

- Part A reproduced round-1 and round-2 values to three decimals (primary B\* −0.016 / −0.032; (B) +0.033; R18 0.905 / 0.799; R24 −0.014 / −0.035; R15 −0.046; F3 −0.069).
- Part B: joint segmentation, stored block, outer refit and all 200 inner class-error files reproduced exactly; the joint package reference reproduces 0.845 / 0.847 / 0.903.

### Implementation notes

- R31: target encoding uses the pre-event samples of the training folds; the sheet's pilot column is empty, so 'pilot' is the batch label containing 'Pilot'; the batch probe standardises inside training folds (L2, C = 1). The largest batch is single-class, so the largest mixed batch (Batch 1) is also reported in `r31.json`.
- R32b: inner residualisation fits on each inner set's pre-event rows.
- R33 rows 7, 13 and the earliest-sample row re-evaluate stored calls on the subset; selection-inclusive and between-repeat rows recompute R16 and R15 logic.
- R36: 'each sample on its own' = one `segmentRawData` call per sample (single-sample branch); arm subtraction and cx as the stored block's construction. Six samples hit a package edge case when no sample of a call passes QC; descriptor columns were selected by name (values unchanged). Past-only = per endoscopy, joint segmentation with the patient's samples up to that endoscopy.
- B5: deviance λ with the same clamp as round 2; no fold model with zero features.

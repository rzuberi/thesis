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

(appended after running)

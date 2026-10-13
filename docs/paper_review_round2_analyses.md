# Review round 2: analyses requested by reviewers (excluding ACE-B)

Status: PRE-SPECIFICATION (written 2026-10-13). Nothing below has been run. Results are appended under the line at the end in a later commit; this section is not edited afterwards.

Purpose: answer the objections from the second internal review of the manuscript draft (36 reviews of draft v2, blindly graded and clustered outside the repository). Part A re-scores stored predictions. Part B refits the existing linear models on existing features under the existing folds. Nothing changes a feature, an extractor, the frozen bundles or the registered ACE-B analysis. ACE-B is not touched: no ACE-B file is read.

**Ground rules**, as in `docs/paper_review_round1_analyses.md`:
- report only, with a status per item and at most one line of interpretation per item;
- earlier documents are not edited;
- row-level data stay on the cluster;
- the cohort is never referred to by its internal short label.

**Population, data and conventions.** Unchanged from round 1:
- Primary population: all pre-event samples of the 676 samples from 80 patients of the Killcoyne discovery cohort with a matched H&E slide (571 samples, 75 patients, 161 samples from 32 progressors).
- Their copy-number matrix is primary. Package features and NDBE pre-event samples are reported where stated.
- Stored outer and inner predictions, triage rules, comparators and the ≥ 6-of-10 vote come from `scripts/paper_plan/tb_common.py`.
- Fold-stratified AUROC.
- Patient bootstrap: 2,000 draws, `RandomState(0)`, resampled patients keep their folds.
- "No vote" means per-repeat calls, with each statistic averaged over the 10 repeats. Its CI comes from the patient bootstrap of that repeat-averaged statistic, with calls fixed.
- One-sided 95% lower bound = 5th percentile of the bootstrap draws.

**Decisions fixed now for the next draft** (applied whatever the results):
1. The deployable triage is a single frozen model, so the no-vote (per-repeat) results become the primary description of the triage's accuracy and cost. The voted results are reported as a 10-model ensemble together with their own sequencing cost (R14).
2. Equivalence wording ("as accurate as", "matched the accuracy") is not used. The matched comparison is reported as non-inferiority in sensitivity at matched specificity, against the −0.05 margin, using the one-sided bound.
3. Every interval in the abstract is labelled with the analysis it comes from.

## Part A. Stored predictions

### R14. What the vote costs, and the comparisons without the vote

- **(a) Sequencing needed by the voted rule.** For the primary triage:
  - the share of samples in the middle band in at least one repeat (already reported: 76%);
  - the share of **vote-pivotal** samples, whose ≥ 6-of-10 call changes between setting all of that sample's middle-band calls positive and setting them all negative. These samples need copy number for the voted call to be known.
  - Both are reported next to the per-repeat mean share sequenced (45.8%).
- **(b) No-vote paired comparisons.** In each repeat, compare the triage's calls with (A), (B) and (C), and with the fold-honest matched comparators A\*, B\* and C\* of R1 (thresholds as in R1, applied per repeat). Report:
  - Δ sensitivity and Δ specificity, averaged over repeats;
  - patient-bootstrap two-sided 95% CIs;
  - the one-sided 95% lower bound of Δ sensitivity against (B) and against B\*.
- **(c) Evaluation-matched B\* without the vote.** Per repeat, the threshold on that repeat's held-out L-LATE scores that gives the largest specificity ≥ the triage's realised specificity in that repeat. Paired Δ sensitivity with the threshold re-chosen inside each bootstrap draw; one-sided lower bound.
- **(d)** All three of (a)–(c) for: their matrix on all pre-event samples (primary), their matrix on NDBE pre-event samples, and package features on all pre-event samples.

### R15. How much refitting moves the primary estimates (cheap version)

- Per repeat: fold-stratified ΔAUROC for L-IMG − L-CNV and L-LATE − L-CNV, and the no-vote Δ sensitivity of the triage against (B) and against B\*.
- Reported for each:
  - SD and range over the 10 repeats;
  - the number of repeats whose own one-sided lower bound (2,000 draws on that repeat alone) is above −0.05;
  - a variance-inflated one-sided bound, Δ − 1.645·√(V_boot + V_rep), where V_boot is the bootstrap variance of the repeat-averaged Δ and V_rep is the between-repeat variance.
- Part B, F3 gives the full refit bootstrap.

### R16. Selection-inclusive intervals for the matched comparators

- **Selection-inclusive R1.** Repeat R1 (training-matched A\*, B\*, C\*; their matrix; all pre-event and NDBE pre-event samples) with every cut-off re-chosen in each bootstrap draw. That covers t_low, c\*, t_seq, the triage's training specificity s\* and the comparator thresholds. Training rows are weighted by their bootstrap multiplicity, as in `tb_selci.py`. Same draws and number of draws as `tb_selci.py`.
- **Also reported**, for both the voted and the no-vote versions:
  - the one-sided 95% lower bound and the 90% two-sided CI (TOST at ±0.05) for Δ sensitivity against B\*, training-matched;
  - the same for the evaluation-matched B\* of R1's secondary analysis, which v2 did not report.
- **Bias of the primary criterion.** For the primary triage criterion (Δ sensitivity against (B), +0.062), the bootstrap median and mean of the selection-inclusive draws and a bias-corrected estimate (2 × observed − bootstrap mean). Draws are recomputed if not stored.

### R17. Multiplicity across the matched comparators

Max-T adjusted p-values (from the joint bootstrap draws) and Holm-adjusted p-values across the three Δ sensitivities, triage − A\*, triage − B\* and triage − C\*. Training-matched and evaluation-matched versions are reported separately, voted and no-vote.

### R18. Tissue amount: stratified comparisons

The strata are overlapping-tile samples (tissue tiles < 256) and the rest (≥ 256), as in R5. Within each stratum:
- **AUROCs:** L-CNV, L-IMG and L-LATE.
- **Paired Δ L-IMG − L-CNV**, with the one-sided bound.
- **Interaction:** the difference between strata in Δ, with a CI.
- **Triage:** sensitivity, specificity and share sequenced (voted and no-vote).

Also reported:
- **Tissue-matched AUROC.** Fold-stratified AUROC counting only case–control pairs whose two samples are in the same tissue-tile tertile. Tertiles are cut on all pre-event samples, without labels. Reported for L-CNV, L-IMG and L-LATE, with Δ L-IMG − L-CNV.
- Counts of samples by tertile and class.

### R19. The registered scanner fallback, tested on the stored transfer predictions

- **Setting:** the C13239-01 → C13210 transfer predictions of R4(b), with the same middle-band rule.
- **Fallback:** set t_low and c\* label-free as the quantiles of the C13210 transfer L-IMG scores that reproduce the internal low and high shares (30.9% and 23.2%). Keep t_seq at the frozen 0.233.
- **Reported:** sensitivity, specificity and band shares on C13210, next to the unreset transfer result and the mixed-scanner CV result on the same samples.
- **Prevalence-dependence of the target shares.** From the internal class-wise band rates (R12), give the expected low, middle and high shares at progressor-sample prevalence 2%, 5%, 10%, 15%, 20% and the observed 28%:

  share(band) = π·r₁(band) + (1 − π)·r₀(band).

  The future rule should therefore state its target as a function of the external cohort's design prevalence.
- **A numeric trigger.** For a cohort of 234 samples from 117 patients, the 95% prediction interval of each band share under the internal model. It is computed by resampling 117 internal pre-event patients with replacement, with calls from a randomly chosen repeat, 2,000 draws. A share outside the interval would trigger the reset. This is reported only; nothing is registered here.

### R20. The 8 patients without a slide

All 8 patients of the 88 without a scanned slide are progressors. Using the published probabilities (P) and Killcoyne's sample sheet (on the cluster):
- per sample and per patient (mean): P for the 8 against the 37 included progressors, and their grade mix and number of samples;
- plain per-sample AUROC of P on pre-event samples of all 88 patients against the 80 patients analysed;
- the reason no slide exists, if recorded anywhere in the source data; otherwise "not recorded".

### R21. How large is the leave-one-patient-out bias for the published model?

- **(a)** Killcoyne-style intercept-only leave-one-patient-out predictions (`kv_lopo_intercepts.R` output), scored with the within-fold pairing used for (P).
- **(b)** If stored leave-one-patient-out L-CNV predictions from our pipeline exist (their matrix), the fold-stratified AUROC of those predictions on the 10 × 10 pairs, against our 10 × 10 L-CNV. Otherwise this is fitted in Part B (F7).
- The direction and size of the gap is reported as an estimate of the bias carried by (P).

### R22. Package-feature triage in the main tables

The package-feature equivalents of Tables 4 and 5 (sample, endoscopy and patient level; A\*, B\*, C\*), drawn from the stored `triage/pkg_pre.json` and `review_round1/r1_pkg_pre.json`. These are reporting only, plus the no-vote rows from R14.

### R23. Endoscopy and patient level

- **Endoscopy level.** An endoscopy is positive if any of its pre-event samples is positive. Endoscopy-level sensitivity and specificity for the triage, B\* and C\* (training-matched), voted and no-vote, with paired Δ and patient-bootstrap CIs.
- **Patient level.** For the triage, (A), (B), (C), B\* and C\* (voted):
  - missed progressor patients and falsely flagged non-progressor patients, with exact (Clopper–Pearson) CIs;
  - paired differences, triage − (B) and triage − (C), with patient-bootstrap CIs.
- **Burden per non-progressor.**
  - Flagged endoscopies per non-progressor patient-year, where follow-up runs from the first to the last pre-event endoscopy (patients with a single endoscopy are counted with 0 years and reported separately).
  - The distribution of flagged endoscopies per patient (0, 1, 2, ≥ 3) by status.

### R24. Current care, grade and sampling intensity

- **Comparator D (current care), from the stored grade.**
  - D1: flag if the sample's grade is ID or LGD.
  - D2: flag if the worst grade to date is ID or LGD.

  Report sample, endoscopy and patient sensitivity and specificity, next to Table 4.
- **Band × grade.** Counts of modal band × grade (NDBE, ID, LGD), by class.
- **Worst grade and sampling intensity.**
  - By status: the number of patients with any pre-event ID or LGD; pre-event endoscopies per patient; pre-event samples per patient; and the span from first to last pre-event endoscopy.
  - The fold-stratified AUROC of the endoscopy's index within the patient (1 = first) as a raw score. This is the null comparator for "more chances to accrue a worse grade".
- **Never-dysplastic patients.** Non-inferiority Δ L-IMG − L-CNV and the triage criterion on samples from patients with no pre-event ID or LGD at any endoscopy.

### R25. Negative control: the triage with an uninformative H&E gate

- **(a) Random gate.** Replace L-IMG's inner and outer scores by independent uniform random scores, 100 seeds. Apply the primary rule unchanged, including the cut-off selection on inner scores. The middle-band call stays real L-LATE.
- **Reported:** the mean and 2.5th–97.5th percentile over seeds of the share sequenced, sensitivity and specificity (no vote).
- **Comparison with the real gate.** For each random seed, the share that must be sequenced to reach the real triage's no-vote sensitivity. It is obtained by widening the middle band symmetrically in rank from the random rule's middle until the sensitivity is reached.
- **(b)** The permutation-trained gate is in Part B (F6).

### R26. Do the cut-offs transfer from the inner predictions?

- **Spread of the fold cut-offs.** The IQR and range of the 100 fold-level t_low, c\* and t_seq values (their matrix; package features).
- **Training versus held-out operating points.** Per fold, the triage's training specificity s\* (inner predictions) against its held-out specificity, summarised over folds. The same for each comparator's training and held-out specificity.
- **Frozen model, in sample.** The frozen their-matrix bundle and the frozen median cut-offs applied to the 571 pre-event samples. Report the band shares and the number of non-zero coefficients of the frozen L-CNV and L-IMG, against the range over the 100 fold models. Labelled in-sample.

### R27. Pairs and time-dependent AUROC without within-patient pairs

- **Within-fold case–control pairs per repeat**, at sample and patient level (pre-event and NDBE pre-event), and the number of fold × repeat cells lacking one class.
- **Time-dependent AUROC without within-patient pairs.** At 1, 3 and 5 years, for L-CNV, L-IMG and L-LATE, computed as in `docs/paper_horizon_foldstrat.md` but excluding pairs whose two samples come from the same patient. Paired Δ L-IMG − L-CNV with the one-sided bound.
- **Unweighted version.** Controls restricted to samples whose observed event-free follow-up is at least the horizon, without inverse-probability-of-censoring weights.

### R28. The extractor the registered switching rule chose (H-optimus-0)

- From the stored H-optimus-0 downstream predictions (`docs/paper_scanner_robustness.md`, downstream run): fold-stratified Δ L-IMG(H-optimus-0) − L-CNV, with the one-sided bound, on all pre-event and NDBE pre-event samples.
- The H-optimus-0 triage needs inner predictions; it is fitted in Part B (F5), then reported as the primary triage criterion and B\*/C\*.

### R29. Likelihood ratios and natural frequencies

- **Band likelihood ratios** with patient-bootstrap CIs, from the class-wise band rates: LR(high) = r₁(high)/r₀(high), LR(low) = r₁(low)/r₀(low), and LR(middle).
- **Natural frequencies.** Per 1,000 biopsies at 2% and 5% prevalence: sequenced, progressor biopsies caught and missed, and false flags. No vote and voted.

### R30. Lead time

- For each progressor patient caught by the triage (voted call; also no vote averaged over repeats), the time from the first positive pre-event endoscopy to the first HGD/IMC.
- Report the median and IQR for the triage, (B) and (C), and the paired difference, triage − (C), in patients caught by both.

## Part B. Refits on existing features (CPU glmnet, existing scripts and folds)

All fits use `kv_common.R`, `kv_cv.R` and `hz_fit.R` unchanged except for the training rows or the λ rule stated. Fold assignment is computed on all 80 patients exactly as now, so folds are identical to the stored ones. Outputs go to new directories; stored predictions are not overwritten.

### F1. Pre-event-only training

- **Fits.** Outer 10 × 10 (`kv_cv.R` logic) and inner 5-fold (`hz_fit.R` inner logic) for L-CNV (their matrix and package features) and L-IMG, with training rows restricted to pre-event samples of the training patients. The 105 post-event samples, and the 5 progressors without pre-event samples, are excluded from training.
- **Reported:**
  - the Table 2 rows for the primary population and NDBE pre-event samples;
  - Δ L-IMG − L-CNV with its non-inferiority bound;
  - the triage criterion against (B);
  - R1's B\* and C\* comparisons (voted and no vote).

### F2. Training-size control for the scanner-transfer drop

- **Fits.** In each repeat × outer fold of the main CV, subsample the training patients to 48, stratified by status at the main CV's training prevalence, `set.seed(100*REP+FOLD)`. Fit L-IMG and score the held-out samples.
- **Reported:**
  - fold-stratified AUROC on held-out C13210 samples and on C13239-01 samples;
  - the same next to the full-size main CV (0.835 on C13210) and the transfer model (0.726).
- **Reading:**
  - If the size-48 mixed-scanner models stay near 0.835, the drop is attributed to the scanner.
  - If they fall towards 0.726, training size explains part of it.

### F3. Refit bootstrap for the two confirmatory comparisons

- **Draws.** 200 patient-bootstrap draws (`RandomState(0)`, first 200 of the standard sequence). Copies of a patient stay together: they are assigned to the same fold as the original patient, and the fold assignment uses the original patient IDs.
- **In each draw**, one stratified 10-fold CV (seed = draw index) is run on the resampled data, with λ and all cut-offs re-chosen. That covers:
  - outer L-CNV (their matrix) and L-IMG;
  - inner 5-fold predictions for the triage cut-offs.
- **Statistics per draw:**
  - fold-stratified Δ L-IMG − L-CNV;
  - triage − (B) Δ sensitivity and Δ specificity (single repeat, no vote);
  - triage − B\* Δ sensitivity.
- **Reported:** percentile intervals and the one-sided 5th percentile, next to the conditional intervals.

### F4. λ by deviance

- **Fits.** Outer 10 × 10 L-CNV (their matrix) and L-IMG with λ at the minimum binomial deviance of the same patient-grouped inner CV curves, instead of the class-error minimum.
- **Reported:**
  - the primary Δ with its bound;
  - for both λ rules, the share of the 100 fold models with no selected feature, per arm.

### F5. H-optimus-0 inner predictions

- **Fits.** `hz_fit.R` inner predictions for L-IMG on the stored H-optimus-0 sample embeddings, for all repeat × fold.
- **Reported:** the triage criterion and B\*/C\* with the H-optimus-0 gate (R28).

### F6. Permutation-trained gate

- **Fits.** For 5 permutations: within each training set, permute progression labels at the patient level, keeping the number of progressor patients. Fit outer and inner L-IMG on the permuted labels with the same folds.
- **Reported:** the triage with this gate, with share sequenced, sensitivity and specificity, mean over permutations (no vote). This complements R25(a) with a gate whose score distribution is that of a real fitted model.

### F7. Leave-one-patient-out L-CNV (only if not stored, for R21b)

- **Fits.** Leave-one-patient-out L-CNV on their matrix, λ rule as in `kv_cv.R`, on the 80 patients.

## Scripts and running

- **Part A:** `scripts/paper_plan/rv2_round2.py` (TASK = r14_* … r30), sharing `tb_common.py`.
- **Part B:** `scripts/paper_plan/rv2_refit.R` (MODE = f1_outer, f1_inner, f2, f3, f4, f5_inner, f6_outer, f6_inner, f7), then `rv2_refit_metrics.py`.
- **Renderer:** `rv2_render.py`.
- **Running:** on Slurm via `scripts/cluster/campaign.sh` with prefix rv2. Never on the login node.
- **Outputs:** aggregates to `results/paper_final/review_round2/`. Row-level outputs stay under the cluster `killcoyne_mm/review_round2/`.

---

## Results

(appended after running)

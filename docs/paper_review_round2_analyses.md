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

Pre-specification commit d681783; results commits 41f84cb (Part B) and c8934b6 (Part A). Scripts `scripts/paper_plan/rv2_round2.py` (Part A), `rv2_refit.R` and `rv2_refit_metrics.py` (Part B), run on Slurm via `scripts/cluster/campaign.sh` (prefix rv2); renderer `rv2_render.py`. Aggregates `results/paper_final/review_round2/`.

### Status

| Item | Status |
|---|---|
| R14 cost of the vote; no-vote comparisons | DONE |
| R15 between-repeat variability | DONE |
| R16 selection-inclusive intervals | DONE |
| R17 multiplicity | DONE |
| R18 tissue amount | DONE |
| R19 scanner fallback | DONE |
| R20 patients without a slide | DONE |
| R21 leave-one-patient-out bias | DONE ((b) from stored predictions; R21b) |
| R22 package-feature tables | DONE |
| R23 endoscopy and patient level | DONE |
| R24 current care, grade, sampling | DONE |
| R25 uninformative gate | DONE ((a) random gate; (b) = F6) |
| R26 cut-off transfer | DONE (fold coefficient counts not stored) |
| R27 pairs and time-dependent AUROC | DONE |
| R28 H-optimus-0 | DONE (triage = F5) |
| R29 likelihood ratios | DONE |
| R30 lead time | DONE |
| F1 pre-event-only training | DONE |
| F2 training-size control | DONE |
| F3 refit bootstrap | DONE (200 draws) |
| F4 λ by deviance | DONE |
| F5 H-optimus-0 inner predictions | DONE |
| F6 permutation-trained gate | DONE |
| F7 leave-one-patient-out L-CNV | NOT RUN (stored predictions exist; R21b) |

### R14. Cost of the vote and the comparisons without the vote

(a) Sequencing needed (share of samples; patient-bootstrap 95% CI).

| Population | Samples (progressor) | Per-repeat mean middle band | Middle band in ≥ 1 repeat | Vote-pivotal | Progressor samples: mean / ≥ 1 repeat / pivotal | Non-progressor samples: mean / ≥ 1 repeat / pivotal |
|---|---|---|---|---|---|---|
| their, all pre-event | 571 (161) | 0.458 [0.408, 0.504] | 0.760 [0.699, 0.811] | 0.471 [0.412, 0.526] | 0.360 / 0.590 / 0.398 | 0.497 / 0.827 / 0.500 |
| their, NDBE pre-event | 438 (104) | 0.491 [0.441, 0.539] | 0.806 [0.750, 0.856] | 0.500 [0.442, 0.562] | 0.408 / 0.625 / 0.433 | 0.517 / 0.862 / 0.521 |
| package, all pre-event | 571 (161) | 0.458 [0.408, 0.504] | 0.760 [0.699, 0.811] | 0.471 [0.412, 0.526] | 0.360 / 0.590 / 0.398 | 0.497 / 0.827 / 0.500 |

Triage operating points (sensitivity / specificity).

| Population | No vote | Voted |
|---|---|---|
| their, all pre-event | 0.865 [0.791, 0.926] / 0.697 [0.633, 0.762] | 0.863 [0.774, 0.942] / 0.734 [0.667, 0.802] |
| their, NDBE pre-event | 0.846 [0.748, 0.928] / 0.680 [0.605, 0.750] | 0.856 [0.742, 0.955] / 0.728 [0.646, 0.798] |
| package, all pre-event | 0.865 [0.801, 0.926] / 0.737 [0.667, 0.796] | 0.863 [0.779, 0.945] / 0.763 [0.690, 0.824] |

(b) No-vote paired comparisons (training-matched A\*, B\*, C\* as in R1, thresholds per repeat; one-sided lower bound where pre-specified).

| Population | Comparator | Comparator sens / spec | Δ sens triage − comparator [95% CI]; lower | Δ spec [95% CI] |
|---|---|---|---|---|
| their, all pre-event | A | 0.801 [0.695, 0.885] / 0.560 [0.452, 0.672] | +0.063 [-0.003, +0.144] | +0.138 [+0.056, +0.216] |
| their, all pre-event | B | 0.832 [0.740, 0.909] / 0.762 [0.694, 0.824] | +0.033 [+0.005, +0.062]; lower 0.011 | -0.065 [-0.092, -0.034] |
| their, all pre-event | C | 0.795 [0.723, 0.870] / 0.719 [0.669, 0.769] | +0.070 [+0.021, +0.116] | -0.022 [-0.068, +0.021] |
| their, all pre-event | A* | 0.746 [0.628, 0.842] / 0.658 [0.550, 0.765] | +0.119 [+0.042, +0.210] | +0.039 [-0.040, +0.117] |
| their, all pre-event | B* | 0.881 [0.801, 0.944] / 0.665 [0.585, 0.745] | -0.016 [-0.036, +0.001]; lower -0.032 | +0.032 [-0.002, +0.071] |
| their, all pre-event | C* | 0.804 [0.729, 0.879] / 0.713 [0.663, 0.762] | +0.061 [+0.017, +0.103] | -0.016 [-0.063, +0.031] |
| their, NDBE pre-event | A | 0.808 [0.696, 0.911] / 0.532 [0.421, 0.646] | +0.038 [-0.030, +0.121] | +0.148 [+0.073, +0.228] |
| their, NDBE pre-event | B | 0.823 [0.713, 0.918] / 0.720 [0.638, 0.797] | +0.023 [-0.008, +0.052]; lower -0.003 | -0.040 [-0.066, -0.012] |
| their, NDBE pre-event | C | 0.787 [0.708, 0.868] / 0.690 [0.630, 0.748] | +0.059 [+0.004, +0.113] | -0.011 [-0.064, +0.038] |
| their, NDBE pre-event | A* | 0.723 [0.579, 0.853] / 0.654 [0.542, 0.766] | +0.123 [+0.035, +0.223] | +0.025 [-0.047, +0.101] |
| their, NDBE pre-event | B* | 0.861 [0.755, 0.944] / 0.653 [0.562, 0.739] | -0.014 [-0.038, +0.004]; lower -0.034 | +0.027 [-0.002, +0.061] |
| their, NDBE pre-event | C* | 0.790 [0.705, 0.874] / 0.693 [0.636, 0.748] | +0.056 [+0.005, +0.113] | -0.013 [-0.066, +0.036] |
| package, all pre-event | A | 0.812 [0.727, 0.885] / 0.683 [0.559, 0.784] | +0.053 [-0.013, +0.126] | +0.053 [-0.019, +0.137] |
| package, all pre-event | B | 0.827 [0.739, 0.906] / 0.793 [0.720, 0.852] | +0.039 [+0.010, +0.071]; lower 0.014 | -0.056 [-0.084, -0.027] |
| package, all pre-event | C | 0.795 [0.723, 0.870] / 0.719 [0.669, 0.769] | +0.070 [+0.030, +0.111] | +0.018 [-0.036, +0.063] |
| package, all pre-event | A* | 0.791 [0.710, 0.864] / 0.706 [0.583, 0.806] | +0.074 [+0.011, +0.143] | +0.031 [-0.039, +0.114] |
| package, all pre-event | B* | 0.872 [0.800, 0.934] / 0.713 [0.618, 0.789] | -0.007 [-0.023, +0.007]; lower -0.020 | +0.024 [-0.013, +0.071] |
| package, all pre-event | C* | 0.775 [0.696, 0.857] / 0.743 [0.692, 0.793] | +0.090 [+0.046, +0.136] | -0.006 [-0.064, +0.043] |

(c) Evaluation-matched comparators without the vote (threshold re-chosen in every bootstrap draw).

| Population | Comparator | Comparator sens at the triage's realised specificity | Δ sens [95% CI]; lower |
|---|---|---|---|
| their, all pre-event | A* | 0.720 [0.582, 0.834] | +0.145 [+0.046, +0.257]; lower 0.060 |
| their, all pre-event | B* | 0.861 [0.774, 0.933] | +0.003 [-0.026, +0.035]; lower -0.022 |
| their, all pre-event | C* | 0.803 [0.732, 0.881] | +0.061 [+0.003, +0.114]; lower 0.011 |
| their, NDBE pre-event | A* | 0.711 [0.543, 0.852] | +0.136 [+0.036, +0.257]; lower 0.052 |
| their, NDBE pre-event | B* | 0.846 [0.736, 0.933] | +0.000 [-0.034, +0.036]; lower -0.028 |
| their, NDBE pre-event | C* | 0.796 [0.708, 0.876] | +0.050 [-0.011, +0.121]; lower -0.003 |
| package, all pre-event | A* | 0.762 [0.621, 0.871] | +0.103 [-0.002, +0.222]; lower 0.011 |
| package, all pre-event | B* | 0.857 [0.777, 0.929] | +0.009 [-0.021, +0.043]; lower -0.017 |
| package, all pre-event | C* | 0.775 [0.693, 0.861] | +0.090 [+0.031, +0.149]; lower 0.040 |

One line: without the vote (their matrix, all pre-event) Δ sensitivity is +0.033 against (B) (lower 0.011, non-inferior at −0.05) and -0.016 against B\* (lower -0.032, non-inferior at −0.05); 0.471 of samples are vote-pivotal under the voted rule.

### R15. Between-repeat variability (their matrix, all pre-event)

| Statistic | Repeat mean | SD over repeats | Range | Repeats with own lower bound > −0.05 | Standard one-sided lower | Variance-inflated lower (V_boot, V_rep) |
|---|---|---|---|---|---|---|
| dAUROC LIMG minus LCNV | +0.045 | 0.033 | -0.034 to +0.070 | 6 / 10 | -0.025 | -0.046 (0.002000, 0.001063) |
| dAUROC LLATE minus LCNV | +0.087 | 0.019 | +0.039 to +0.104 | 10 / 10 | 0.044 | 0.031 (0.000789, 0.000375) |
| no vote d sens triage minus B | +0.033 | 0.025 | +0.006 to +0.075 | 10 / 10 | 0.011 | -0.014 (0.000211, 0.000601) |
| no vote d sens triage minus Bstar | -0.016 | 0.016 | -0.037 to +0.012 | 7 / 10 | -0.032 | -0.046 (0.000091, 0.000242) |

One line: with between-repeat variance added, ΔAUROC L-IMG − L-CNV has lower bound -0.046 (non-inferior at −0.05) and the no-vote Δ sensitivity against B\* has lower bound -0.046 (non-inferior at −0.05).

### R16. Selection-inclusive intervals (every cut-off re-chosen in each draw; 2,000 draws)

| Population | Mode | Comparator | Triage sens / spec | Comparator sens / spec | Δ sens [95% CI]; lower; 90% CI (TOST) | Δ spec [95% CI] |
|---|---|---|---|---|---|---|
| their, all pre-event | voted | A* (training-matched) | 0.863 [0.802, 0.895] / 0.734 [0.610, 0.830] | 0.745 [0.644, 0.833] / 0.685 [0.547, 0.792] | +0.118 [+0.005, +0.213]; lower 0.020 | +0.049 [-0.018, +0.126] |
| their, all pre-event | voted | B* (training-matched) | 0.863 [0.802, 0.895] / 0.734 [0.610, 0.830] | 0.870 [0.812, 0.916] / 0.700 [0.568, 0.804] | -0.006 [-0.057, +0.032]; lower -0.051; 90% CI [-0.051, +0.023] | +0.034 [-0.002, +0.081] |
| their, all pre-event | voted | C* (training-matched) | 0.863 [0.802, 0.895] / 0.734 [0.610, 0.830] | 0.789 [0.703, 0.868] / 0.746 [0.626, 0.824] | +0.075 [-0.010, +0.141]; lower 0.000 | -0.012 [-0.053, +0.029] |
| their, all pre-event | voted | (B) | 0.863 [0.802, 0.895] / 0.734 [0.610, 0.830] | 0.801 [0.765, 0.871] / 0.785 [0.657, 0.889] | +0.062 [-0.015, +0.093]; lower -0.007; 90% CI [-0.007, +0.084] | -0.051 [-0.109, +0.012] |
| their, all pre-event | voted | A* (evaluation-matched) | 0.863 [0.802, 0.895] / 0.734 [0.610, 0.830] | 0.727 [0.576, 0.826] / — | +0.137 [+0.011, +0.287]; lower 0.030 | — |
| their, all pre-event | voted | B* (evaluation-matched) | 0.863 [0.802, 0.895] / 0.734 [0.610, 0.830] | 0.851 [0.796, 0.909] / — | +0.012 [-0.057, +0.059]; lower -0.045; 90% CI [-0.045, +0.048] | — |
| their, all pre-event | voted | C* (evaluation-matched) | 0.863 [0.802, 0.895] / 0.734 [0.610, 0.830] | 0.807 [0.707, 0.881] / — | +0.056 [-0.039, +0.140]; lower -0.027 | — |
| their, all pre-event | no vote | A* (training-matched) | 0.865 [0.817, 0.890] / 0.697 [0.577, 0.785] | 0.746 [0.665, 0.814] / 0.658 [0.528, 0.764] | +0.119 [+0.037, +0.196]; lower 0.047 | +0.039 [-0.007, +0.090] |
| their, all pre-event | no vote | B* (training-matched) | 0.865 [0.817, 0.890] / 0.697 [0.577, 0.785] | 0.881 [0.830, 0.914] / 0.665 [0.546, 0.767] | -0.016 [-0.043, +0.001]; lower -0.038; 90% CI [-0.038, -0.001] | +0.032 [+0.006, +0.059] |
| their, all pre-event | no vote | C* (training-matched) | 0.865 [0.817, 0.890] / 0.697 [0.577, 0.785] | 0.804 [0.727, 0.859] / 0.713 [0.591, 0.786] | +0.061 [+0.008, +0.122]; lower 0.014 | -0.016 [-0.036, +0.014] |
| their, all pre-event | no vote | (B) | 0.865 [0.817, 0.890] / 0.697 [0.577, 0.785] | 0.832 [0.793, 0.862] / 0.762 [0.634, 0.861] | +0.033 [+0.001, +0.055]; lower 0.006; 90% CI [+0.006, +0.051] | -0.065 [-0.109, -0.012] |
| their, all pre-event | no vote | A* (evaluation-matched) | 0.865 [0.817, 0.890] / 0.697 [0.577, 0.785] | 0.720 [0.616, 0.806] / — | +0.145 [+0.041, +0.255]; lower 0.054 | — |
| their, all pre-event | no vote | B* (evaluation-matched) | 0.865 [0.817, 0.890] / 0.697 [0.577, 0.785] | 0.861 [0.820, 0.905] / — | +0.003 [-0.039, +0.027]; lower -0.034; 90% CI [-0.034, +0.022] | — |
| their, all pre-event | no vote | C* (evaluation-matched) | 0.865 [0.817, 0.890] / 0.697 [0.577, 0.785] | 0.803 [0.731, 0.867] / — | +0.061 [-0.007, +0.119]; lower 0.003 | — |
| their, NDBE pre-event | voted | A* (training-matched) | 0.856 [0.759, 0.903] / 0.728 [0.583, 0.832] | 0.721 [0.607, 0.825] / 0.677 [0.523, 0.800] | +0.135 [+0.008, +0.238]; lower 0.027 | +0.051 [-0.022, +0.123] |
| their, NDBE pre-event | voted | B* (training-matched) | 0.856 [0.759, 0.903] / 0.728 [0.583, 0.832] | 0.846 [0.771, 0.908] / 0.671 [0.536, 0.799] | +0.010 [-0.056, +0.048]; lower -0.048; 90% CI [-0.048, +0.038] | +0.057 [+0.002, +0.093] |
| their, NDBE pre-event | voted | C* (training-matched) | 0.856 [0.759, 0.903] / 0.728 [0.583, 0.832] | 0.779 [0.673, 0.868] / 0.734 [0.597, 0.824] | +0.077 [-0.042, +0.171]; lower -0.025 | -0.006 [-0.052, +0.045] |
| their, NDBE pre-event | voted | (B) | 0.856 [0.759, 0.903] / 0.728 [0.583, 0.832] | 0.788 [0.740, 0.868] / 0.734 [0.595, 0.873] | +0.067 [-0.026, +0.108]; lower -0.018; 90% CI [-0.018, +0.096] | -0.006 [-0.081, +0.036] |
| their, NDBE pre-event | voted | A* (evaluation-matched) | 0.856 [0.759, 0.903] / 0.728 [0.583, 0.832] | 0.683 [0.527, 0.825] / — | +0.173 [+0.000, +0.333]; lower 0.031 | — |
| their, NDBE pre-event | voted | B* (evaluation-matched) | 0.856 [0.759, 0.903] / 0.728 [0.583, 0.832] | 0.837 [0.761, 0.900] / — | +0.019 [-0.082, +0.085]; lower -0.061; 90% CI [-0.061, +0.072] | — |
| their, NDBE pre-event | voted | C* (evaluation-matched) | 0.856 [0.759, 0.903] / 0.728 [0.583, 0.832] | 0.798 [0.685, 0.884] / — | +0.058 [-0.081, +0.165]; lower -0.065 | — |
| their, NDBE pre-event | no vote | A* (training-matched) | 0.846 [0.778, 0.884] / 0.680 [0.545, 0.792] | 0.723 [0.626, 0.809] / 0.654 [0.497, 0.770] | +0.123 [+0.034, +0.215]; lower 0.045 | +0.025 [-0.012, +0.085] |
| their, NDBE pre-event | no vote | B* (training-matched) | 0.846 [0.778, 0.884] / 0.680 [0.545, 0.792] | 0.861 [0.791, 0.904] / 0.653 [0.518, 0.769] | -0.014 [-0.048, +0.006]; lower -0.043; 90% CI [-0.043, +0.003] | +0.027 [+0.003, +0.056] |
| their, NDBE pre-event | no vote | C* (training-matched) | 0.846 [0.778, 0.884] / 0.680 [0.545, 0.792] | 0.790 [0.704, 0.845] / 0.693 [0.554, 0.788] | +0.056 [-0.005, +0.135]; lower 0.004 | -0.013 [-0.037, +0.022] |
| their, NDBE pre-event | no vote | (B) | 0.846 [0.778, 0.884] / 0.680 [0.545, 0.792] | 0.823 [0.766, 0.855] / 0.720 [0.573, 0.841] | +0.023 [-0.012, +0.056]; lower -0.007; 90% CI [-0.007, +0.049] | -0.040 [-0.092, +0.006] |
| their, NDBE pre-event | no vote | A* (evaluation-matched) | 0.846 [0.778, 0.884] / 0.680 [0.545, 0.792] | 0.711 [0.599, 0.804] / — | +0.136 [+0.034, +0.256]; lower 0.047 | — |
| their, NDBE pre-event | no vote | B* (evaluation-matched) | 0.846 [0.778, 0.884] / 0.680 [0.545, 0.792] | 0.846 [0.799, 0.895] / — | +0.000 [-0.056, +0.034]; lower -0.046; 90% CI [-0.046, +0.027] | — |
| their, NDBE pre-event | no vote | C* (evaluation-matched) | 0.846 [0.778, 0.884] / 0.680 [0.545, 0.792] | 0.796 [0.707, 0.855] / — | +0.050 [-0.036, +0.136]; lower -0.022 | — |

Bias of the primary criterion (Δ sensitivity against (B)) and selection-inclusive CIs of the share sequenced.

| Population | Mode | Observed | Bootstrap median / mean | Bias-corrected (2 × observed − mean) | 95% CI; lower | Share sequenced 95% CI: per-repeat mean / ≥ 1 repeat / vote-pivotal |
|---|---|---|---|---|---|---|
| their, all pre-event | voted | +0.062 | +0.035 / +0.036 | +0.088 | [-0.015, +0.093]; -0.007 | [0.344, 0.540] / [0.662, 0.841] / [0.329, 0.555] |
| their, all pre-event | no vote | +0.033 | +0.028 / +0.028 | +0.038 | [+0.001, +0.055]; 0.006 | [0.344, 0.540] / [0.662, 0.841] / [0.329, 0.555] |
| their, NDBE pre-event | voted | +0.067 | +0.036 / +0.038 | +0.097 | [-0.026, +0.108]; -0.018 | [0.361, 0.576] / [0.708, 0.882] / [0.341, 0.591] |
| their, NDBE pre-event | no vote | +0.023 | +0.021 / +0.021 | +0.025 | [-0.012, +0.056]; -0.007 | [0.361, 0.576] / [0.708, 0.882] / [0.341, 0.591] |

One line: selection-inclusive, the no-vote Δ sensitivity against B\* has lower bound -0.038 (non-inferior at −0.05) and the voted one -0.051 (not non-inferior at −0.05); the recomputed voted draws against (B) match the stored `tb_selci` draws (max abs difference 0.0).

### R17. Multiplicity across A\*, B\*, C\* (Δ sensitivity, triage − comparator)

| Population | Mode, matching | Comparator | Δ [95% CI] | p (percentile) | p Holm | p max-T |
|---|---|---|---|---|---|---|
| their, all pre-event | voted, training-matched | A* | +0.118 [+0.025, +0.219] | 0.008 | 0.024 | 0.049 |
| their, all pre-event | voted, training-matched | B* | -0.006 [-0.051, +0.034] | 0.952 | 0.952 | 0.9825 |
| their, all pre-event | voted, training-matched | C* | +0.075 [+0.016, +0.135] | 0.015 | 0.03 | 0.0405 |
| their, all pre-event | voted, evaluation-matched | A* | +0.137 [+0.020, +0.286] | 0.021 | 0.063 | 0.1105 |
| their, all pre-event | voted, evaluation-matched | B* | +0.012 [-0.038, +0.061] | 0.745 | 0.745 | 0.934 |
| their, all pre-event | voted, evaluation-matched | C* | +0.056 [-0.035, +0.149] | 0.22 | 0.44 | 0.4795 |
| their, all pre-event | no vote, training-matched | A* | +0.119 [+0.042, +0.210] | 0.005 | 0.015 | 0.017 |
| their, all pre-event | no vote, training-matched | B* | -0.016 [-0.036, +0.001] | 0.076 | 0.076 | 0.2055 |
| their, all pre-event | no vote, training-matched | C* | +0.061 [+0.017, +0.103] | 0.005 | 0.015 | 0.014 |
| their, all pre-event | no vote, evaluation-matched | A* | +0.145 [+0.046, +0.257] | 0.005 | 0.015 | 0.024 |
| their, all pre-event | no vote, evaluation-matched | B* | +0.003 [-0.026, +0.035] | 0.899 | 0.899 | 0.996 |
| their, all pre-event | no vote, evaluation-matched | C* | +0.061 [+0.003, +0.114] | 0.039 | 0.078 | 0.078 |
| their, NDBE pre-event | voted, training-matched | A* | +0.135 [+0.038, +0.241] | 0.012 | 0.036 | 0.032 |
| their, NDBE pre-event | voted, training-matched | B* | +0.010 [-0.023, +0.044] | 0.777 | 0.777 | 0.8925 |
| their, NDBE pre-event | voted, training-matched | C* | +0.077 [-0.009, +0.165] | 0.086 | 0.172 | 0.2035 |
| their, NDBE pre-event | voted, evaluation-matched | A* | +0.173 [+0.035, +0.330] | 0.012 | 0.036 | 0.066 |
| their, NDBE pre-event | voted, evaluation-matched | B* | +0.019 [-0.020, +0.099] | 0.528 | 0.572 | 0.881 |
| their, NDBE pre-event | voted, evaluation-matched | C* | +0.058 [-0.050, +0.184] | 0.286 | 0.572 | 0.6345 |
| their, NDBE pre-event | no vote, training-matched | A* | +0.123 [+0.035, +0.223] | 0.003 | 0.009 | 0.0335 |
| their, NDBE pre-event | no vote, training-matched | B* | -0.014 [-0.038, +0.004] | 0.158 | 0.158 | 0.397 |
| their, NDBE pre-event | no vote, training-matched | C* | +0.056 [+0.005, +0.113] | 0.033 | 0.066 | 0.103 |
| their, NDBE pre-event | no vote, evaluation-matched | A* | +0.136 [+0.036, +0.257] | 0.003 | 0.009 | 0.05 |
| their, NDBE pre-event | no vote, evaluation-matched | B* | +0.000 [-0.034, +0.036] | 0.971 | 0.971 | 1.0 |
| their, NDBE pre-event | no vote, evaluation-matched | C* | +0.050 [-0.011, +0.121] | 0.121 | 0.242 | 0.3115 |
| package, all pre-event | voted, training-matched | A* | +0.068 [-0.018, +0.165] | 0.145 | 0.29 | 0.2985 |
| package, all pre-event | voted, training-matched | B* | -0.019 [-0.046, +0.000] | 0.283 | 0.29 | 0.296 |
| package, all pre-event | voted, training-matched | C* | +0.093 [+0.035, +0.160] | 0.001 | 0.003 | 0.0115 |
| package, all pre-event | voted, evaluation-matched | A* | +0.099 [-0.048, +0.264] | 0.192 | 0.384 | 0.4495 |
| package, all pre-event | voted, evaluation-matched | B* | +0.006 [-0.042, +0.045] | 1.0 | 1.0 | 0.985 |
| package, all pre-event | voted, evaluation-matched | C* | +0.093 [+0.006, +0.172] | 0.048 | 0.144 | 0.09 |
| package, all pre-event | no vote, training-matched | A* | +0.074 [+0.011, +0.143] | 0.02 | 0.04 | 0.065 |
| package, all pre-event | no vote, training-matched | B* | -0.007 [-0.023, +0.007] | 0.428 | 0.428 | 0.6825 |
| package, all pre-event | no vote, training-matched | C* | +0.090 [+0.046, +0.136] | 0.0 | 0.0 | 0.0015 |
| package, all pre-event | no vote, evaluation-matched | A* | +0.103 [-0.002, +0.222] | 0.056 | 0.112 | 0.1695 |
| package, all pre-event | no vote, evaluation-matched | B* | +0.009 [-0.021, +0.043] | 0.666 | 0.666 | 0.8955 |
| package, all pre-event | no vote, evaluation-matched | C* | +0.090 [+0.031, +0.149] | 0.001 | 0.003 | 0.0085 |

One line: their matrix, all pre-event, no vote, training-matched: max-T p 0.017 (A\*), 0.2055 (B\*), 0.014 (C\*).

### R18. Tissue amount (their matrix, all pre-event)

| Stratum | Samples (progressor) / patients | L-CNV | L-IMG | L-LATE | Δ L-IMG − L-CNV [95% CI]; lower | Triage voted sens / spec; mid in ≥ 1 repeat; pivotal | Triage no vote sens / spec; share sequenced |
|---|---|---|---|---|---|---|---|
| tissue tiles < 256 (overlapping tiles) | 293 (71) / 72 | 0.792 [0.689, 0.876] | 0.905 [0.846, 0.946] | 0.926 [0.881, 0.959] | +0.113 [+0.002, +0.223]; lower 0.021 | 0.915 [0.824, 0.980] / 0.743 [0.664, 0.813]; 0.730; 0.437 | 0.925 [0.866, 0.969] / 0.704 [0.627, 0.779]; 0.423 [0.355, 0.484] |
| tissue tiles ≥ 256 | 278 (90) / 67 | 0.814 [0.695, 0.903] | 0.799 [0.733, 0.861] | 0.865 [0.773, 0.930] | -0.015 [-0.104, +0.097]; lower -0.095 | 0.822 [0.681, 0.934] / 0.723 [0.634, 0.803]; 0.791; 0.507 | 0.817 [0.706, 0.905] / 0.689 [0.610, 0.761]; 0.496 [0.451, 0.540] |

Interaction (Δ in the < 256 stratum minus Δ in the ≥ 256 stratum): +0.129 [-0.004, +0.246] (p 0.062).

Tissue-matched AUROC (pairs within the same tissue-tile tertile; tertile edges 5.000, 200.000, 302.000, 5433.000 tiles): L-CNV 0.804 [0.713, 0.879], L-IMG 0.840 [0.786, 0.892], L-LATE 0.892 [0.830, 0.937]; Δ L-IMG − L-CNV +0.036 [-0.052, +0.135]; lower -0.039 (unstratified reference L-CNV 0.801, L-IMG 0.847, L-LATE 0.889).

Samples by tertile (progressor / non-progressor): tertile 1 49 / 143; tertile 2 39 / 149; tertile 3 73 / 118.

One line: the L-IMG advantage is confined to the overlapping-tile stratum (+0.113, lower 0.021) and absent in the ≥ 256 stratum (-0.015, lower -0.095, not non-inferior at −0.05); tissue-matched Δ +0.036, lower -0.039 (non-inferior at −0.05).

### R19. Scanner fallback on the stored transfer predictions (C13239-01 → C13210; 139 samples, 27 patients, 9 progressors; t_seq frozen at 0.233)

| Rule | t_low | c* | Sensitivity [95% CI] | Specificity [95% CI] | Bands low / mid / high |
|---|---|---|---|---|---|
| transfer, unreset cut-offs | 0.141 | 0.497 | 0.744 [0.516, 0.929] | 0.690 [0.544, 0.807] | 0.496 / 0.295 / 0.209 |
| transfer, label-free reset to the internal low / high shares (0.309 / 0.232) | 0.077 | 0.428 | 0.846 [0.629, 0.977] | 0.600 [0.449, 0.756] | 0.309 / 0.453 / 0.237 |
| mixed-scanner CV, same samples (voted) | — | — | 0.923 [0.839, 1.000] | 0.700 [0.588, 0.793] | 0.309 / 0.469 / 0.222 |

Internal class-wise band rates (low / mid / high): progressor 0.066 / 0.360 / 0.574; non-progressor 0.405 / 0.497 / 0.098.

| Progressor-sample prevalence | Expected low | Expected middle | Expected high |
|---|---|---|---|
| 0.02 | 0.398 | 0.494 | 0.107 |
| 0.05 | 0.388 | 0.490 | 0.122 |
| 0.10 | 0.371 | 0.483 | 0.145 |
| 0.15 | 0.354 | 0.477 | 0.169 |
| 0.20 | 0.337 | 0.470 | 0.193 |
| 0.282 (observed) | 0.309 | 0.458 | 0.232 |

Trigger interval for a 117-patient cohort (2000 draws of 75 internal patients, mean 890.8 samples per draw): low mean 0.311, 95% interval [0.213, 0.390]; mid mean 0.456, 95% interval [0.380, 0.568]; high mean 0.233, 95% interval [0.184, 0.291].

One line: the label-free reset moves C13210 sensitivity from 0.744 to 0.846 and specificity from 0.690 to 0.600, against 0.923 / 0.700 for the mixed-scanner CV on the same samples.

### R20. The 8 patients without a slide (all progressors; published P and the sample sheet)

| Group | Samples | Patients | P per sample: mean, median (IQR) | P per patient mean: mean, median (IQR) | Samples per patient: median (IQR) | Grade mix | Share of samples with P ≥ 0.5 |
|---|---|---|---|---|---|---|---|
| without slide, all samples | 46 | 8 | 0.718, 0.913 (0.388–0.996) | 0.709, 0.780 (0.624–0.872) | 5.000 (4.000–6.750) | NDBE 26, LGD 10, HGD 6, ID 3, IMC 1 | 0.652 |
| without slide, pre-event samples | 29 | 8 | 0.711, 0.944 (0.404–0.996) | 0.659, 0.691 (0.416–0.937) | 3.000 (2.000–4.250) | NDBE 17, LGD 10, ID 2 | 0.621 |
| included progressors, all samples | 303 | 37 | 0.700, 0.768 (0.486–0.963) | 0.678, 0.691 (0.503–0.898) | 7.000 (4.000–10.000) | NDBE 146, LGD 73, HGD 30, ID 30, IMC 24 | 0.733 |
| included progressors, pre-event samples | 187 | 33 | 0.648, 0.711 (0.435–0.930) | 0.650, 0.678 (0.477–0.840) | 5.000 (2.000–7.000) | NDBE 119, LGD 48, ID 20 | 0.658 |

| Plain per-sample AUROC of P, pre-event samples | Samples / patients (progressors) | AUROC [95% CI] |
|---|---|---|
| all 88 patients | 640 / 84 (41) | 0.836 [0.749, 0.903] |
| 80 patients all sheet pre event samples | 611 / 76 (33) | 0.834 [0.739, 0.911] |
| 80 patients 571 analysed samples | 571 / 75 (32) | 0.828 [0.730, 0.904] |

Reason no slide exists: no column of the sample sheet records one. Non-empty rows among the 46 sheet rows of these patients: Pathology notes 6 (BE (gastric type), GM, IM, LGD/focal HGD, focal); inconsistency 1 (Y); notes on label review 9 (focal HGD, no path record, outcome OGD focal HGD); excluded 46; remove 46; Replicate 0; Set 46 (Test, Training); Batch 46 (Batch 1, Batch 16S, Batch 3, Batch 4, Exome Subcohort). Slide matching: 0 matched rows, 0 with a slide file. Conclusion: not recorded.

One line: the published P of the 8 patients is of the same order as the included progressors' (pre-event per-patient mean 0.659 against 0.650), and P's plain AUROC on all 88 patients (0.836) is close to that on the analysed samples (0.828).

### R21. Leave-one-patient-out bias of the published model

(a) Intercept-only leave-one-patient-out predictions (`killcoyne_mm/cv/lopo_intercepts/arm_00.csv (train_prev of each leave-one-patient-out fit)`, 80 patients). (b) Stored leave-one-patient-out L-CNV from our pipeline (`killcoyne_mm/linear/cfg_00_chunk_*.csv (rule class_min; their matrix; 676 rows)`; λ range 0.003–0.015), so F7 was not refitted.

| Population | Score | Fold-stratified AUROC on the 10 × 10 pairs [95% CI] | Plain pooled AUROC [95% CI] |
|---|---|---|---|
| all pre-event (571 samples) | intercept only LOPO | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| all pre-event (571 samples) | P published | 0.823 [0.709, 0.908] | 0.828 [0.730, 0.904] |
| all pre-event (571 samples) | L-CNV LOPO stored | 0.794 [0.691, 0.877] | 0.799 [0.702, 0.876] |
| all pre-event (571 samples) | L-CNV 10x10 | 0.801 [0.710, 0.875] | 0.802 [0.706, 0.879] |
| NDBE pre-event (438 samples) | intercept only LOPO | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| NDBE pre-event (438 samples) | P published | 0.781 [0.647, 0.902] | 0.788 [0.667, 0.897] |
| NDBE pre-event (438 samples) | L-CNV LOPO stored | 0.758 [0.638, 0.870] | 0.761 [0.646, 0.867] |
| NDBE pre-event (438 samples) | L-CNV 10x10 | 0.780 [0.681, 0.879] | 0.778 [0.667, 0.879] |

| Population | Difference | Δ [95% CI] | p |
|---|---|---|---|
| all pre-event | (a) intercept-only LOPO − P | -0.823 [-0.908, -0.709] | 0.0 |
| all pre-event | (b) LOPO L-CNV − 10 × 10 L-CNV, fold-stratified | -0.008 [-0.036, +0.018] | 0.587 |
| all pre-event | (b) LOPO L-CNV − 10 × 10 L-CNV, plain pooled | -0.003 [-0.021, +0.016] | 0.73 |
| all pre-event | P − 10 × 10 L-CNV | +0.022 [-0.028, +0.070] | 0.359 |
| all pre-event | (a) intercept-only LOPO − 0.5 | -0.500 | — |
| NDBE pre-event | (a) intercept-only LOPO − P | -0.781 [-0.902, -0.647] | 0.0 |
| NDBE pre-event | (b) LOPO L-CNV − 10 × 10 L-CNV, fold-stratified | -0.022 [-0.053, +0.006] | 0.134 |
| NDBE pre-event | (b) LOPO L-CNV − 10 × 10 L-CNV, plain pooled | -0.017 [-0.038, +0.003] | 0.085 |
| NDBE pre-event | P − 10 × 10 L-CNV | +0.002 [-0.048, +0.056] | 0.883 |
| NDBE pre-event | (a) intercept-only LOPO − 0.5 | -0.500 | — |

R21b (`rv2_refit_metrics.py`, same stored predictions): all pre-event LOPO 0.794 [0.691, 0.877] against 10 × 10 0.801 [0.710, 0.875], Δ -0.008 [-0.036, +0.018] (p 0.587); plain LOPO 0.799 against 0.802; NDBE pre-event LOPO 0.758 [0.638, 0.870] against 10 × 10 0.780 [0.681, 0.879], Δ -0.022 [-0.053, +0.006] (p 0.134); plain LOPO 0.761 against 0.778.

One line: the intercept-only leave-one-patient-out score is perfectly anti-concordant (AUROC 0.000), and our leave-one-patient-out L-CNV differs from the 10 × 10 L-CNV on the same pairs by -0.008 [-0.036, +0.018] (all pre-event), so the leave-one-patient-out design does not account for P − L-CNV (+0.022 [-0.028, +0.070]).

### R22. Package-feature triage (all pre-event samples; reporting of stored results)

| Level | Strategy | Sensitivity [95% CI] | Specificity [95% CI] |
|---|---|---|---|
| sample, voted | triage_LATE | 0.863 [0.779, 0.945] | 0.763 [0.690, 0.824] |
| sample, voted | A | 0.839 [0.745, 0.916] | 0.700 [0.564, 0.810] |
| sample, voted | B | 0.832 [0.728, 0.924] | 0.820 [0.741, 0.885] |
| sample, voted | C | 0.789 [0.703, 0.875] | 0.754 [0.693, 0.811] |
| endoscopy, voted | triage_LATE | 0.955 [0.904, 1.000] | 0.630 [0.550, 0.709] |
| endoscopy, voted | A | 0.943 [0.890, 0.986] | 0.625 [0.487, 0.749] |
| endoscopy, voted | B | 0.920 [0.852, 0.974] | 0.725 [0.634, 0.807] |
| endoscopy, voted | C | 0.886 [0.815, 0.955] | 0.575 [0.497, 0.658] |
| sample, no vote (mean over repeats, range) | triage_LATE | 0.865 (0.826–0.907) | 0.737 (0.690–0.776) |
| sample, no vote (mean over repeats, range) | A | 0.812 (0.727–0.907) | 0.683 (0.646–0.741) |
| sample, no vote (mean over repeats, range) | B | 0.827 (0.795–0.888) | 0.793 (0.766–0.829) |
| sample, no vote (mean over repeats, range) | C | 0.795 (0.758–0.832) | 0.719 (0.688–0.746) |

| Matched comparator (voted, R1) | Comparator sens / spec | Δ sens triage − comparator [95% CI] | Δ spec [95% CI] | No-vote Δ sens [95% CI]; lower (R14) |
|---|---|---|---|---|
| A* (L-CNV) | 0.795 [0.698, 0.881] / 0.727 [0.597, 0.831] | +0.068 [-0.018, +0.165] | +0.037 [-0.043, +0.132] | +0.074 [+0.011, +0.143] |
| B* (L-LATE) | 0.882 [0.799, 0.953] / 0.729 [0.627, 0.813] | -0.019 [-0.046, +0.000] | +0.034 [-0.010, +0.087] | -0.007 [-0.023, +0.007]; lower -0.020 |
| C* (L-IMG) | 0.770 [0.678, 0.864] / 0.780 [0.725, 0.831] | +0.093 [+0.035, +0.160] | -0.017 [-0.077, +0.035] | +0.090 [+0.046, +0.136] |

Patient level (voted): triage_LATE caught 31, missed 1, non-progressors flagged 30 of 43; A caught 31, missed 1, non-progressors flagged 27 of 43; B caught 31, missed 1, non-progressors flagged 26 of 43; C caught 31, missed 1, non-progressors flagged 35 of 43.

Bands (all [95% CI] / progressor / non-progressor): low 0.309 [0.249, 0.366] / 0.066 / 0.405; mid 0.458 [0.408, 0.504] / 0.360 / 0.497; high 0.232 [0.175, 0.299] / 0.574 / 0.098. Share of samples sequenced 0.458; endoscopies with any sample sequenced 0.597; per-repeat share 0.458 (0.406–0.559), in the middle band in ≥ 1 repeat 0.760.

One line: the package-feature primary criterion (voted) is Δ sensitivity +0.031 against (B), lower -0.006, share sequenced 0.458: met; no vote, against B\* -0.007 [-0.023, +0.007]; lower -0.020 (non-inferior at −0.05).

### R23. Endoscopy and patient level (their matrix, all pre-event; 288 endoscopies, 88 from progressors)

| Mode | Strategy | Sensitivity [95% CI] | Specificity [95% CI] | Δ sens triage − strategy [95% CI] | Δ spec [95% CI] |
|---|---|---|---|---|---|
| endoscopy, voted | triage | 0.898 [0.833, 0.959] | 0.590 [0.497, 0.681] | — | — |
| endoscopy, voted | B* | 0.909 [0.833, 0.970] | 0.570 [0.464, 0.675] | -0.011 [-0.066, +0.045] | +0.020 [-0.021, +0.064] |
| endoscopy, voted | C* | 0.875 [0.806, 0.939] | 0.570 [0.484, 0.653] | +0.023 [-0.045, +0.090] | +0.020 [-0.057, +0.092] |
| endoscopy, voted | A | 0.818 [0.691, 0.925] | 0.545 [0.411, 0.671] | +0.080 [-0.020, +0.192] | +0.045 [-0.043, +0.133] |
| endoscopy, voted | B | 0.852 [0.753, 0.933] | 0.650 [0.558, 0.744] | +0.045 [-0.023, +0.118] | -0.060 [-0.107, -0.015] |
| endoscopy, voted | C | 0.886 [0.815, 0.955] | 0.575 [0.497, 0.658] | +0.011 [-0.071, +0.082] | +0.015 [-0.054, +0.084] |
| endoscopy, no vote | triage | 0.909 [0.865, 0.952] | 0.549 [0.460, 0.637] | — | — |
| endoscopy, no vote | B* | 0.923 [0.873, 0.962] | 0.530 [0.431, 0.629] | -0.014 [-0.041, +0.009] | +0.019 [-0.010, +0.053] |
| endoscopy, no vote | C* | 0.890 [0.837, 0.939] | 0.541 [0.474, 0.615] | +0.019 [-0.022, +0.059] | +0.008 [-0.053, +0.063] |
| endoscopy, no vote | A | 0.845 [0.767, 0.912] | 0.504 [0.385, 0.621] | +0.064 [+0.010, +0.122] | +0.045 [-0.022, +0.112] |
| endoscopy, no vote | B | 0.876 [0.803, 0.935] | 0.640 [0.552, 0.726] | +0.033 [-0.006, +0.076] | -0.091 [-0.121, -0.061] |
| endoscopy, no vote | C | 0.885 [0.828, 0.938] | 0.550 [0.482, 0.625] | +0.024 [-0.023, +0.068] | -0.001 [-0.057, +0.051] |

Patient level, voted (32 progressor and 43 non-progressor patients; exact Clopper–Pearson 95% CIs).

| Strategy | Progressor patients missed (share [95% CI]) | Non-progressor patients flagged (share [95% CI]) | Δ missed share, triage − strategy [95% CI] (patients) | Δ flagged share [95% CI] (patients) |
|---|---|---|---|---|
| triage | 1 (0.031 [0.001, 0.162]) | 30 (0.698 [0.539, 0.828]) | — | — |
| B* | 1 (0.031 [0.001, 0.162]) | 31 (0.721 [0.563, 0.847]) | +0.000 [+0.000, +0.000] (+0) | -0.023 [-0.075, +0.000] (-1) |
| C* | 2 (0.062 [0.008, 0.208]) | 34 (0.791 [0.640, 0.900]) | -0.031 [-0.103, +0.000] (-1) | -0.093 [-0.214, +0.026] (-4) |
| A | 4 (0.125 [0.035, 0.290]) | 29 (0.674 [0.515, 0.809]) | — | — |
| B | 2 (0.062 [0.008, 0.208]) | 28 (0.651 [0.491, 0.790]) | -0.031 [-0.103, +0.000] (-1) | +0.047 [-0.043, +0.143] (+2) |
| C | 1 (0.031 [0.001, 0.162]) | 35 (0.814 [0.666, 0.916]) | +0.000 [-0.088, +0.094] (+0) | -0.116 [-0.231, +0.000] (-5) |

Burden per non-progressor (follow-up first to last pre-event endoscopy; 43 non-progressors with > 1 endoscopy, 285.5 patient-years; 0 with a single endoscopy).

| Strategy | Flagged endoscopies per non-progressor patient-year: voted / no vote | Flagged endoscopies per non-progressor patient, voted: 0 / 1 / 2 / ≥ 3 | Per progressor patient, voted: 0 / 1 / 2 / ≥ 3 | Per non-progressor patient, no vote: 0 / 1 / 2 / ≥ 3 |
|---|---|---|---|---|
| triage | 0.287 / 0.316 | 0.302 / 0.116 / 0.209 / 0.372 | 0.031 / 0.312 / 0.219 / 0.438 | 0.256 / 0.158 / 0.195 / 0.391 |
| B | 0.245 / 0.252 | 0.349 / 0.209 / 0.140 / 0.302 | 0.062 / 0.344 / 0.188 / 0.406 | 0.337 / 0.207 / 0.172 / 0.284 |
| C | 0.298 / 0.315 | 0.186 / 0.186 / 0.302 / 0.326 | 0.031 / 0.344 / 0.156 / 0.469 | 0.186 / 0.163 / 0.267 / 0.384 |
| B* | 0.301 / 0.330 | 0.279 / 0.209 / 0.140 / 0.372 | 0.031 / 0.312 / 0.219 / 0.438 | 0.263 / 0.156 / 0.179 / 0.402 |
| C* | 0.301 / 0.322 | 0.209 / 0.163 / 0.256 / 0.372 | 0.062 / 0.312 / 0.188 / 0.438 | 0.177 / 0.167 / 0.260 / 0.395 |

One line: at patient level the voted triage misses 1 progressor and flags 30 of 43 non-progressors, with 0.287 flagged endoscopies per non-progressor patient-year against 0.245 for (B) and 0.298 for (C).

### R24. Current care, grade and sampling intensity (their matrix, all pre-event)

| Comparator | Sample sens [95% CI] / spec [95% CI]; share flagged | Endoscopy sens / spec | Patients: progressors caught / missed; non-progressors flagged / unflagged |
|---|---|---|---|
| D1 grade ID or LGD | 0.354 [0.233, 0.480] / 0.815 [0.753, 0.879]; 0.233 | 0.364 / 0.760 | 17 / 15; 25 / 18 |
| D2 worst grade to date ID or LGD | 0.534 [0.351, 0.703] / 0.407 [0.280, 0.559]; 0.576 | 0.466 / 0.445 | 17 / 15; 25 / 18 |
| Table 4 reference (voted) | triage 0.863 / 0.734; A 0.783 / 0.590; B 0.801 / 0.785; C 0.789 / 0.754 | — | — |

Modal band × grade (counts low / mid / high): progressor NDBE 6 / 48 / 50; progressor ID 0 / 6 / 9; progressor LGD 1 / 10 / 31; non-progressor NDBE 144 / 163 / 27; non-progressor ID 15 / 32 / 4; non-progressor LGD 12 / 10 / 3.

| Status | Patients | With any pre-event ID or LGD | Pre-event endoscopies per patient: mean, median (range) | Pre-event samples per patient: mean, median (range) | Span first to last pre-event endoscopy, years: mean, median (range) |
|---|---|---|---|---|---|
| progressor | 32 | 17 | 2.750, 2.500 (1.000–9.000) | 5.031, 4.500 (1.000–12.000) | 3.531, 2.750 (0.000–12.000) |
| non-progressor | 43 | 25 | 4.651, 5.000 (2.000–8.000) | 9.535, 8.000 (4.000–30.000) | 6.640, 6.000 (2.000–13.000) |

Endoscopy index within the patient (1 = earliest) as a raw score: fold-stratified AUROC 0.366 [0.279, 0.454].

Never-dysplastic patients (197 samples, 56 progressor; 33 patients, 15 progressors): AUROC L-CNV 0.756 [0.613, 0.906], L-IMG 0.814 [0.725, 0.895], L-LATE 0.837 [0.732, 0.941]; Δ L-IMG − L-CNV +0.057 [-0.079, +0.193]; lower -0.059; triage − (B) Δ sensitivity voted +0.089 [+0.029, +0.154]; lower 0.038, no vote +0.050 [+0.023, +0.072]; lower 0.028 (Δ specificity no vote -0.046 [-0.073, -0.021]); triage − B\* no vote -0.014 [-0.039, +0.008]; lower -0.035; share sequenced (no vote) 0.441.

One line: current care (D1) has sample sensitivity 0.354 at specificity 0.815; in never-dysplastic patients Δ L-IMG − L-CNV is not non-inferior at −0.05 (lower -0.059) while the triage criterion against (B) holds (no-vote lower 0.028).

### R25. Negative control: uniform random H&E gate (100 seeds; no vote; their matrix, all pre-event)

| Gate | Share sequenced | Sensitivity | Specificity |
|---|---|---|---|
| random (mean, 2.5th–97.5th percentile over seeds) | 0.846 (0.835–0.859) | 0.804 (0.791–0.817) | 0.697 (0.690–0.708) |
| real gate | 0.458 | 0.865 | 0.697 |

Share that must be sequenced for the random gate to reach the real no-vote sensitivity (0.865): not reached in 100 of 100 seeds even with the middle band widened to all samples (sensitivity at full sequencing, mean over seeds, 0.832). (b) The permutation-trained gate is in F6.

One line: a random gate sequences 0.846 of samples for sensitivity 0.804 and does not reach the real gate's 0.865 at any share.

### R26. Cut-off transfer from the inner predictions

| CNV source | Cut-off | Median | IQR | Range over the 100 folds |
|---|---|---|---|---|
| their | t_low | 0.042 | 0.027–0.059 | 0.005–0.109 |
| their | c_star | 0.589 | 0.554–0.619 | 0.489–0.725 |
| their | t_seq | 0.233 | 0.214–0.257 | 0.159–0.328 |
| their | t_B | 0.314 | 0.288–0.346 | 0.225–0.441 |
| package | t_low | 0.042 | 0.027–0.059 | 0.005–0.109 |
| package | c_star | 0.589 | 0.554–0.619 | 0.489–0.725 |
| package | t_seq | 0.237 | 0.216–0.257 | 0.167–0.306 |
| package | t_B | 0.332 | 0.307–0.356 | 0.221–0.416 |

| CNV source | Strategy | Training specificity: median (IQR) | Held-out specificity: median (IQR) | Held-out − training: median (IQR; range) |
|---|---|---|---|---|
| their | triage (s*) | 0.618 (0.562–0.674) | 0.718 (0.631–0.800) | +0.087 (-0.002 to +0.163; -0.293 to +0.385) |
| their | A | 0.478 (0.392–0.553) | 0.574 (0.440–0.735) | +0.106 (-0.058 to +0.266; -0.465 to +0.637) |
| their | B | 0.717 (0.682–0.772) | 0.783 (0.699–0.857) | +0.049 (-0.035 to +0.131; -0.294 to +0.294) |
| their | C | 0.621 (0.584–0.672) | 0.718 (0.648–0.798) | +0.094 (+0.011 to +0.165; -0.276 to +0.342) |
| package | triage (s*) | 0.666 (0.627–0.702) | 0.739 (0.658–0.816) | +0.086 (-0.034 to +0.169; -0.188 to +0.375) |
| package | A | 0.632 (0.579–0.701) | 0.686 (0.537–0.844) | +0.046 (-0.087 to +0.211; -0.492 to +0.455) |
| package | B | 0.768 (0.722–0.806) | 0.802 (0.720–0.882) | +0.036 (-0.056 to +0.130; -0.416 to +0.285) |
| package | C | 0.621 (0.584–0.672) | 0.718 (0.648–0.798) | +0.094 (+0.011 to +0.165; -0.276 to +0.342) |

Frozen their-matrix bundle on the 571 pre-event samples, IN-SAMPLE (frozen bundle fitted on all 676 samples; not a performance estimate): cut-offs t_B 0.314, t_high 0.589, t_low 0.042, t_seq 0.233; bands low / mid / high 0.356 / 0.385 / 0.259 (progressor 0.000 / 0.081 / 0.919; non-progressor 0.495 / 0.505 / 0.000); in-sample triage sensitivity 1.000, specificity 0.946; (B) in sample 1.000 / 0.980. Non-zero coefficients: frozen L-CNV 68, frozen L-IMG 158; λ frozen L-CNV 0.009 (fold range 0.002–0.029), frozen L-IMG 0.004 (fold range 0.002–0.014). Bundle reproduction: in-sample AUROC L-CNV 0.996 (model_info 0.996), L-IMG 0.998 (model_info 0.998).

One line: held-out specificity exceeds the training target s\* by a median +0.087 (their matrix), and the frozen in-sample band shares (0.356 / 0.385 / 0.259) are not a performance estimate.

### R27. Case–control pairs and time-dependent AUROC without within-patient pairs (their matrix)

| Population | Samples / patients | Sample-level within-fold pairs, mean over repeats | Patient-level within-fold pairs, mean | Fold × repeat cells lacking one class | Sample pairs without folds |
|---|---|---|---|---|---|
| all pre-event | 571 / 75 | 6495.4 | 135.4 | 0 | 66010 |
| NDBE pre-event | 438 / 71 | 3448.2 | 118.5 | 0 | 34736 |

| Population | Horizon (years) | Cases / controls | Within-patient pairs removed (repeat 1, of within-fold pairs) | Weighting, pairs | L-CNV | L-IMG | L-LATE | Δ L-IMG − L-CNV [95% CI]; lower | Δ L-LATE − L-CNV [95% CI] |
|---|---|---|---|---|---|---|---|---|---|
| all pre-event | 1 | 29 / 449 | 94 of 1313 | IPCW, excluding within-patient | 0.827 [0.718, 0.936] | 0.794 [0.689, 0.876] | 0.879 [0.826, 0.925] | -0.033 [-0.214, +0.130]; lower -0.183 | +0.052 [-0.040, +0.149] |
| all pre-event | 1 | 29 / 449 | 94 of 1313 | IPCW, all pairs (reference) | 0.811 [0.656, 0.923] | 0.771 [0.631, 0.846] | 0.854 [0.747, 0.907] | -0.039 [-0.239, +0.107]; lower -0.207 | +0.043 [-0.065, +0.119] |
| all pre-event | 1 | 29 / 449 | 94 of 1313 | unweighted, excluding within-patient | 0.827 [0.718, 0.936] | 0.794 [0.689, 0.876] | 0.879 [0.826, 0.925] | -0.033 [-0.214, +0.130]; lower -0.183 | +0.052 [-0.040, +0.149] |
| all pre-event | 1 | 29 / 449 | 94 of 1313 | unweighted, all pairs (reference) | 0.811 [0.656, 0.923] | 0.771 [0.631, 0.846] | 0.854 [0.747, 0.907] | -0.039 [-0.239, +0.107]; lower -0.207 | +0.043 [-0.065, +0.119] |
| all pre-event | 3 | 99 / 277 | 191 of 2557 | IPCW, excluding within-patient | 0.791 [0.702, 0.875] | 0.811 [0.731, 0.884] | 0.854 [0.783, 0.917] | +0.020 [-0.085, +0.128]; lower -0.067 | +0.064 [+0.003, +0.131] |
| all pre-event | 3 | 99 / 277 | 191 of 2557 | IPCW, all pairs (reference) | 0.767 [0.655, 0.841] | 0.788 [0.659, 0.866] | 0.831 [0.705, 0.898] | +0.021 [-0.086, +0.132]; lower -0.069 | +0.064 [-0.004, +0.135] |
| all pre-event | 3 | 99 / 277 | 191 of 2557 | unweighted, excluding within-patient | 0.790 [0.700, 0.876] | 0.810 [0.730, 0.882] | 0.854 [0.781, 0.918] | +0.019 [-0.087, +0.126]; lower -0.069 | +0.064 [+0.003, +0.132] |
| all pre-event | 3 | 99 / 277 | 191 of 2557 | unweighted, all pairs (reference) | 0.769 [0.657, 0.843] | 0.788 [0.662, 0.864] | 0.832 [0.709, 0.898] | +0.019 [-0.090, +0.131]; lower -0.072 | +0.064 [-0.004, +0.135] |
| all pre-event | 5 | 126 / 168 | 141 of 1886 | IPCW, excluding within-patient | 0.800 [0.711, 0.873] | 0.781 [0.716, 0.846] | 0.843 [0.777, 0.900] | -0.018 [-0.113, +0.088]; lower -0.098 | +0.043 [-0.014, +0.112] |
| all pre-event | 5 | 126 / 168 | 141 of 1886 | IPCW, all pairs (reference) | 0.779 [0.669, 0.841] | 0.760 [0.661, 0.819] | 0.821 [0.716, 0.873] | -0.018 [-0.109, +0.079]; lower -0.096 | +0.043 [-0.013, +0.105] |
| all pre-event | 5 | 126 / 168 | 141 of 1886 | unweighted, excluding within-patient | 0.801 [0.712, 0.876] | 0.788 [0.721, 0.851] | 0.849 [0.781, 0.905] | -0.013 [-0.109, +0.095]; lower -0.095 | +0.049 [-0.010, +0.120] |
| all pre-event | 5 | 126 / 168 | 141 of 1886 | unweighted, all pairs (reference) | 0.782 [0.675, 0.848] | 0.768 [0.665, 0.828] | 0.829 [0.725, 0.883] | -0.014 [-0.111, +0.083]; lower -0.094 | +0.047 [-0.011, +0.110] |
| NDBE pre-event | 1 | 12 / 334 | 27 of 393 | IPCW, excluding within-patient | 0.890 [0.774, 0.959] | 0.743 [0.603, 0.860] | 0.886 [0.811, 0.937] | -0.146 [-0.314, +0.033]; lower -0.287 | -0.003 [-0.074, +0.088] |
| NDBE pre-event | 1 | 12 / 334 | 27 of 393 | IPCW, all pairs (reference) | 0.873 [0.716, 0.951] | 0.727 [0.542, 0.844] | 0.869 [0.748, 0.927] | -0.145 [-0.355, +0.046]; lower -0.323 | -0.004 [-0.098, +0.086] |
| NDBE pre-event | 1 | 12 / 334 | 27 of 393 | unweighted, excluding within-patient | 0.890 [0.774, 0.959] | 0.743 [0.603, 0.860] | 0.886 [0.811, 0.937] | -0.146 [-0.315, +0.033]; lower -0.287 | -0.004 [-0.074, +0.088] |
| NDBE pre-event | 1 | 12 / 334 | 27 of 393 | unweighted, all pairs (reference) | 0.873 [0.717, 0.951] | 0.727 [0.542, 0.844] | 0.869 [0.748, 0.927] | -0.145 [-0.355, +0.046]; lower -0.323 | -0.004 [-0.098, +0.086] |
| NDBE pre-event | 3 | 61 / 192 | 85 of 1133 | IPCW, excluding within-patient | 0.793 [0.681, 0.898] | 0.775 [0.694, 0.870] | 0.824 [0.735, 0.917] | -0.018 [-0.112, +0.090]; lower -0.098 | +0.031 [-0.021, +0.100] |
| NDBE pre-event | 3 | 61 / 192 | 85 of 1133 | IPCW, all pairs (reference) | 0.775 [0.642, 0.875] | 0.756 [0.631, 0.846] | 0.806 [0.677, 0.900] | -0.020 [-0.127, +0.098]; lower -0.109 | +0.031 [-0.030, +0.110] |
| NDBE pre-event | 3 | 61 / 192 | 85 of 1133 | unweighted, excluding within-patient | 0.789 [0.674, 0.898] | 0.771 [0.689, 0.866] | 0.820 [0.729, 0.916] | -0.018 [-0.114, +0.091]; lower -0.100 | +0.031 [-0.022, +0.101] |
| NDBE pre-event | 3 | 61 / 192 | 85 of 1133 | unweighted, all pairs (reference) | 0.773 [0.641, 0.877] | 0.751 [0.629, 0.843] | 0.803 [0.673, 0.899] | -0.022 [-0.130, +0.095]; lower -0.112 | +0.030 [-0.031, +0.105] |
| NDBE pre-event | 5 | 79 / 111 | 72 of 833 | IPCW, excluding within-patient | 0.772 [0.673, 0.866] | 0.743 [0.663, 0.816] | 0.793 [0.714, 0.871] | -0.029 [-0.129, +0.076]; lower -0.114 | +0.021 [-0.034, +0.089] |
| NDBE pre-event | 5 | 79 / 111 | 72 of 833 | IPCW, all pairs (reference) | 0.752 [0.636, 0.839] | 0.714 [0.593, 0.778] | 0.769 [0.652, 0.840] | -0.038 [-0.152, +0.061]; lower -0.132 | +0.017 [-0.044, +0.086] |
| NDBE pre-event | 5 | 79 / 111 | 72 of 833 | unweighted, excluding within-patient | 0.774 [0.669, 0.875] | 0.746 [0.665, 0.824] | 0.797 [0.711, 0.879] | -0.028 [-0.129, +0.081]; lower -0.116 | +0.024 [-0.032, +0.091] |
| NDBE pre-event | 5 | 79 / 111 | 72 of 833 | unweighted, all pairs (reference) | 0.756 [0.632, 0.851] | 0.718 [0.588, 0.787] | 0.775 [0.651, 0.854] | -0.038 [-0.158, +0.063]; lower -0.138 | +0.020 [-0.044, +0.090] |

One line: excluding within-patient pairs (IPCW, all pre-event), Δ L-IMG − L-CNV is -0.033 at the 1-year horizon (lower -0.183, not non-inferior at −0.05); +0.020 at the 3-year horizon (lower -0.067, not non-inferior at −0.05); -0.018 at the 5-year horizon (lower -0.098, not non-inferior at −0.05).

### R28. H-optimus-0 downstream predictions (stored; folds equal to the main CV)

| Population | Model | AUROC [95% CI] |
|---|---|---|
| all pre-event (571 samples) | L-CNV | 0.801 [0.710, 0.875] |
| all pre-event (571 samples) | L-IMG UNI2h | 0.847 [0.798, 0.894] |
| all pre-event (571 samples) | L-IMG Hoptimus0 | 0.805 [0.744, 0.859] |
| all pre-event (571 samples) | L-LATE UNI2h | 0.889 [0.830, 0.934] |
| all pre-event (571 samples) | L-LATE Hoptimus0 | 0.870 [0.807, 0.922] |
| NDBE pre-event (438 samples) | L-CNV | 0.780 [0.681, 0.879] |
| NDBE pre-event (438 samples) | L-IMG UNI2h | 0.827 [0.768, 0.883] |
| NDBE pre-event (438 samples) | L-IMG Hoptimus0 | 0.784 [0.710, 0.851] |
| NDBE pre-event (438 samples) | L-LATE UNI2h | 0.867 [0.794, 0.931] |
| NDBE pre-event (438 samples) | L-LATE Hoptimus0 | 0.850 [0.771, 0.917] |

| Population | Difference | Δ [95% CI]; lower |
|---|---|---|
| all pre-event | L-IMG (H-optimus-0) − L-CNV | +0.003 [-0.089, +0.097]; lower -0.074 |
| all pre-event | L-IMG (UNI2-h) − L-CNV, reference | +0.045 [-0.036, +0.136]; lower -0.025 |
| all pre-event | L-LATE (H-optimus-0) − L-CNV | +0.069 [+0.021, +0.121] |
| all pre-event | L-IMG (H-optimus-0) − L-IMG (UNI2-h) | -0.042 [-0.082, -0.010] |
| NDBE pre-event | L-IMG (H-optimus-0) − L-CNV | +0.004 [-0.102, +0.106]; lower -0.087 |
| NDBE pre-event | L-IMG (UNI2-h) − L-CNV, reference | +0.047 [-0.040, +0.145]; lower -0.030 |
| NDBE pre-event | L-LATE (H-optimus-0) − L-CNV | +0.070 [+0.012, +0.132] |
| NDBE pre-event | L-IMG (H-optimus-0) − L-IMG (UNI2-h) | -0.044 [-0.101, +0.002] |

One line: with H-optimus-0, Δ L-IMG − L-CNV is +0.003 (lower -0.074, not non-inferior at −0.05; all pre-event) and L-IMG (H-optimus-0) − L-IMG (UNI2-h) is -0.042 [-0.082, -0.010]; the H-optimus-0 triage is in F5.

### R29. Band likelihood ratios and natural frequencies (their matrix, all pre-event)

| Band | Rate in progressor samples [95% CI] | Rate in non-progressor samples [95% CI] | Likelihood ratio [95% CI] |
|---|---|---|---|
| low | 0.066 [0.033, 0.103] | 0.405 [0.341, 0.470] | 0.163 [0.080, 0.262] |
| mid | 0.360 [0.269, 0.443] | 0.497 [0.444, 0.549] | 0.725 [0.535, 0.920] |
| high | 0.574 [0.469, 0.689] | 0.098 [0.071, 0.130] | 5.868 [4.111, 8.451] |

Per 1,000 biopsies (no vote: sequenced = middle band; voted: sequenced = vote-pivotal; 95% CIs).

| Prevalence | Mode | Sequenced | Progressor biopsies caught | Progressor biopsies missed | False flags | In the middle band in ≥ 1 repeat |
|---|---|---|---|---|---|---|
| 0.02 | no vote | 494.3 [442.0, 545.5] | 17.3 [15.8, 18.5] | 2.7 [1.5, 4.2] | 296.9 [233.3, 360.1] | 822.1 [768.5, 870.9] |
| 0.02 | voted | 498.0 [432.5, 560.4] | 17.3 [15.5, 18.8] | 2.7 [1.2, 4.5] | 260.5 [194.3, 325.9] | 822.1 [768.5, 870.9] |
| 0.05 | no vote | 490.2 [439.1, 540.0] | 43.2 [39.5, 46.3] | 6.8 [3.7, 10.5] | 287.8 [226.1, 349.0] | 815.0 [762.1, 862.4] |
| 0.05 | voted | 494.9 [431.5, 555.5] | 43.2 [38.7, 47.1] | 6.8 [2.9, 11.3] | 252.6 [188.3, 315.9] | 815.0 [762.1, 862.4] |

One line: LR(high) 5.868, LR(low) 0.163, LR(middle) 0.725; at 5% prevalence the no-vote triage sequences 490.2 of 1,000 biopsies, catches 43.2 of 50 progressor biopsies and flags 287.8 non-progressor biopsies (high-band PPV at 5%, R12 check, 0.236).

### R30. Lead time (32 progressor patients with pre-event samples; years from the first positive pre-event endoscopy to the first HGD/IMC)

| Strategy | Voted: patients caught | Voted: median (IQR), mean | No vote (mean over repeats): patients caught | No vote: median (IQR), mean |
|---|---|---|---|---|
| triage | 31 | 5.000 (2.500–7.500), 5.177 | 31.1 | 4.950 (2.425–7.175), 5.208 |
| B | 30 | 4.500 (2.000–6.750), 4.983 | 30.7 | 4.575 (2.100–6.800), 5.057 |
| C | 31 | 5.000 (2.250–7.500), 5.290 | 31.1 | 4.975 (2.250–7.350), 5.232 |
| B* | 31 | 5.000 (2.500–7.000), 5.242 | — | — |
| C* | 30 | 5.000 (2.125–7.750), 5.267 | — | — |

Paired difference in patients caught by both (voted): triage − (C) median 0.000 (IQR 0.000–0.000), mean +0.033, n 30; triage − (B) median 0.000 (IQR 0.000–0.000), mean +0.100, n 30. No vote, triage − (C): median 0.000, mean +0.092, n 30.4.

One line: lead time is the same for the triage and (C) in the patients both catch (median difference 0.000 years), with the triage's median 5.000 years against 4.500 for (B).

### F1. Pre-event-only training (outer 10 × 10 and inner 5-fold refits; training rows restricted to pre-event samples)

Training rows per outer fold: their mean 513.9 (range 479–541); package mean 513.9 (range 479–541) (stored main CV: all samples of the training patients (about 608)).

| CNV source | Population | L-CNV | L-IMG | L-LATE | Δ L-IMG − L-CNV [95% CI]; lower | Δ L-LATE − L-CNV [95% CI] | Stored reference L-CNV / L-IMG / L-LATE; stored Δ L-IMG − L-CNV lower |
|---|---|---|---|---|---|---|---|
| their | all pre-event | 0.774 [0.685, 0.853] | 0.848 [0.799, 0.895] | 0.879 [0.820, 0.926] | +0.074 [-0.015, +0.165]; lower 0.000 | +0.105 [+0.046, +0.168] | 0.801 / 0.847 / 0.889; -0.025 |
| their | NDBE pre-event | 0.749 [0.641, 0.848] | 0.828 [0.769, 0.886] | 0.857 [0.782, 0.922] | +0.079 [-0.018, +0.175]; lower -0.003 | +0.108 [+0.047, +0.175] | 0.780 / 0.827 / 0.867; -0.030 |
| package | all pre-event | 0.806 [0.714, 0.872] | 0.848 [0.799, 0.895] | 0.888 [0.836, 0.933] | +0.042 [-0.036, +0.137]; lower -0.025 | +0.082 [+0.033, +0.144] | 0.845 / 0.847 / 0.903; -0.062 |
| package | NDBE pre-event | 0.791 [0.695, 0.875] | 0.828 [0.769, 0.886] | 0.864 [0.795, 0.925] | +0.037 [-0.044, +0.121]; lower -0.033 | +0.073 [+0.027, +0.125] | 0.823 / 0.827 / 0.879; -0.061 |

| CNV source | Population | Mode | Triage sens / spec | Share sequenced (per-repeat mean [95% CI]; ≥ 1 repeat) | Criterion vs (B): Δ sens; lower; met | A\* Δ sens [95% CI]; lower | B\* Δ sens [95% CI]; lower | C\* Δ sens [95% CI]; lower |
|---|---|---|---|---|---|---|---|---|
| their | all pre-event | voted | 0.894 [0.807, 0.961] / 0.734 [0.672, 0.794] | 0.443 [0.397, 0.484]; 0.762 | +0.056; 0.032; met | +0.186 [+0.100, +0.283]; lower 0.113 | +0.000 [-0.025, +0.025]; lower -0.021 | +0.081 [+0.027, +0.136]; lower 0.035 |
| their | all pre-event | no vote | 0.873 [0.795, 0.935] / 0.696 [0.632, 0.757] | 0.443 [0.397, 0.484]; 0.762 | +0.040; 0.024; met | +0.153 [+0.074, +0.235]; lower 0.088 | -0.009 [-0.024, +0.005]; lower -0.021 | +0.059 [+0.023, +0.095]; lower 0.028 |
| their | NDBE pre-event | voted | 0.846 [0.731, 0.947] / 0.719 [0.643, 0.786] | 0.496 [0.444, 0.543]; 0.811 | +0.029; 0.000; met | +0.144 [+0.029, +0.260]; lower 0.048 | -0.019 [-0.046, +0.000]; lower -0.041 | +0.048 [-0.026, +0.136]; lower -0.016 |
| their | NDBE pre-event | no vote | 0.850 [0.750, 0.939] / 0.657 [0.586, 0.723] | 0.496 [0.444, 0.543]; 0.811 | +0.037; 0.014; met | +0.135 [+0.060, +0.219]; lower 0.073 | -0.013 [-0.033, +0.003]; lower -0.030 | +0.043 [+0.004, +0.086]; lower 0.010 |
| package | all pre-event | voted | 0.888 [0.823, 0.950] / 0.766 [0.704, 0.822] | 0.443 [0.397, 0.484]; 0.762 | +0.081; 0.039; met | +0.137 [+0.053, +0.231]; lower 0.067 | +0.006 [-0.021, +0.035]; lower -0.016 | +0.075 [+0.017, +0.134]; lower 0.025 |
| package | all pre-event | no vote | 0.863 [0.792, 0.925] / 0.718 [0.653, 0.777] | 0.443 [0.397, 0.484]; 0.762 | +0.042; 0.024; met | +0.109 [+0.045, +0.184]; lower 0.055 | -0.005 [-0.015, +0.005]; lower -0.013 | +0.065 [+0.028, +0.105]; lower 0.034 |
| package | NDBE pre-event | voted | 0.846 [0.759, 0.933] / 0.713 [0.620, 0.790] | 0.496 [0.444, 0.543]; 0.811 | +0.048; 0.000; met | +0.096 [+0.000, +0.209]; lower 0.010 | -0.010 [-0.053, +0.032]; lower -0.047 | +0.058 [+0.000, +0.131]; lower 0.009 |
| package | NDBE pre-event | no vote | 0.842 [0.761, 0.927] / 0.679 [0.598, 0.749] | 0.496 [0.444, 0.543]; 0.811 | +0.041; 0.022; met | +0.088 [+0.012, +0.174]; lower 0.023 | -0.004 [-0.018, +0.008]; lower -0.015 | +0.055 [+0.014, +0.105]; lower 0.020 |

Cut-offs (their matrix, all pre-event; median, range over folds): t_low 0.028 (0.001–0.100), c_star 0.477 (0.360–0.737), t_seq 0.190 (0.106–0.259); training specificity target s\* 0.598 (0.411–0.780); folds without a middle band 0, t_seq fallback 0.

One line: with pre-event-only training (their matrix, all pre-event) Δ L-IMG − L-CNV is +0.074 (lower 0.000, non-inferior at −0.05) and the no-vote Δ sensitivity against B\* is -0.009 [-0.024, +0.005]; lower -0.021 (non-inferior at −0.05).

### F2. Training-size control (48 training patients per fold, 22.3 progressors (range 22–23); full size 72.0 patients, 33.3 progressors)

| Held-out samples | n | L-IMG, size-48 mixed-scanner [95% CI] | L-IMG, full-size main CV [95% CI] | Δ size-48 − full [95% CI] | Reference |
|---|---|---|---|---|---|
| C13210 | 139 | 0.780 [0.652, 0.886] | 0.835 [0.717, 0.926] | -0.055 [-0.104, -0.012] | transfer model C13239-01 → C13210 0.726 |
| C13239-01 | 432 | 0.803 [0.740, 0.862] | 0.858 [0.803, 0.909] | -0.055 [-0.079, -0.034] | within-C13239-01 CV 0.841 |
| all pre-event | — | 0.783 [0.727, 0.840] | 0.847 | — | — |

One line: size-48 mixed-scanner models change by -0.055 on C13210 (0.780, between the full-size 0.835 and the transfer model's 0.726), so training size explains part of the transfer drop.

### F3. Refit bootstrap (200 draws; one stratified 10-fold CV per draw, λ and all cut-offs re-chosen; no vote; 48.0 distinct patients per draw, range 40–54; mean 566.0 pre-event evaluation rows)

| Statistic | Refit bootstrap mean / median | 95% percentile interval | One-sided 5th percentile | SD | Conditional stored: voted | Conditional stored: no vote |
|---|---|---|---|---|---|---|
| Δ AUROC L-IMG − L-CNV | +0.070 / +0.060 | [-0.114, +0.302] | -0.083 | 0.108 | +0.045 [-0.036, +0.136]; lower -0.025 | — |
| Δ sensitivity triage − (B) | +0.018 / +0.018 | [-0.055, +0.102] | -0.038 | 0.039 | +0.062 [+0.011, +0.116]; lower 0.020 | +0.033 [+0.005, +0.062]; lower 0.011 |
| Δ specificity triage − (B) | -0.041 / -0.043 | [-0.145, +0.059] | -0.122 | 0.051 | -0.051 [-0.092, -0.008]; lower -0.084 | -0.065 [-0.092, -0.034]; lower -0.088 |
| Δ sensitivity triage − B* | -0.018 / -0.016 | [-0.079, +0.040] | -0.069 | 0.033 | -0.006 [-0.051, +0.034] | -0.016 [-0.036, +0.001]; lower -0.032 |

Per-draw triage (mean / median; 95% percentile interval): sensitivity 0.828 / 0.833 [0.716, 0.915]; specificity 0.598 / 0.619 [0.379, 0.752]; share sequenced 0.567 / 0.566 [0.381, 0.779]. Draw-mean AUROC: L-CNV 0.718, L-IMG 0.788, L-LATE 0.821.

One line: under the full refit bootstrap the 5th percentile of Δ AUROC L-IMG − L-CNV is -0.083 (not non-inferior at −0.05), of Δ sensitivity against (B) -0.038 (non-inferior at −0.05) and against B\* -0.069 (not non-inferior at −0.05).

### F4. λ at the deviance minimum (outer 10 × 10 refits; their matrix)

| Arm | Share of fold models with no selected feature: class-error λ / deviance λ | Non-zero coefficients, median: class-error / deviance | λ median: class-error / deviance | Share of folds with deviance λ < class-error λ | Max abs prediction difference, class-error refit vs stored |
|---|---|---|---|---|---|
| L-CNV | 0.000 / 0.000 | 73.000 / 54.000 | 0.008 / 0.015 | 0.030 | 0.0 |
| L-IMG | 0.000 / 0.000 | 143.000 / 93.500 | 0.004 / 0.010 | 0.010 | 0.0 |

| Population | λ rule | L-CNV | L-IMG | L-LATE | Δ L-IMG − L-CNV [95% CI]; lower | Δ L-LATE − L-CNV [95% CI] |
|---|---|---|---|---|---|---|
| all pre-event | deviance | 0.809 [0.722, 0.881] | 0.830 [0.775, 0.883] | 0.882 [0.817, 0.932] | +0.021 [-0.060, +0.111]; lower -0.050 | +0.073 [+0.024, +0.130] |
| all pre-event | class error (stored) | 0.801 [0.710, 0.875] | 0.847 [0.798, 0.894] | 0.889 [0.830, 0.934] | +0.045 [-0.036, +0.136]; lower -0.025 | +0.087 [+0.037, +0.145] |
| NDBE pre-event | deviance | 0.784 [0.686, 0.880] | 0.816 [0.749, 0.880] | 0.864 [0.781, 0.932] | +0.032 [-0.059, +0.130]; lower -0.043 | +0.080 [+0.026, +0.146] |
| NDBE pre-event | class error (stored) | 0.780 [0.681, 0.879] | 0.827 [0.768, 0.883] | 0.867 [0.794, 0.931] | +0.047 [-0.040, +0.145]; lower -0.030 | +0.087 [+0.034, +0.152] |

One line: with the deviance λ (all pre-event) Δ L-IMG − L-CNV is +0.021 with lower bound -0.050 (not non-inferior at −0.05); no fold model is empty under either rule.

### F5. H-optimus-0 gate triage (L-IMG on H-optimus-0 sample embeddings (stored outer predictions of the scanner-robustness downstream run; inner predictions F5); L-CNV stored, their matrix)

| CNV source | Population | Mode | Triage sens / spec | Share sequenced (per-repeat mean [95% CI]; ≥ 1 repeat) | Criterion vs (B): Δ sens; lower; met | A\* Δ sens [95% CI]; lower | B\* Δ sens [95% CI]; lower | C\* Δ sens [95% CI]; lower |
|---|---|---|---|---|---|---|---|---|
| their, H-optimus-0 gate | all pre-event | voted | 0.863 [0.764, 0.940] / 0.646 [0.558, 0.733] | 0.668 [0.619, 0.710]; 0.874 | +0.025; 0.000; met | +0.087 [-0.005, +0.184]; lower 0.009 | -0.006 [-0.023, +0.000]; lower -0.019 | +0.062 [+0.014, +0.114]; lower 0.022 |
| their, H-optimus-0 gate | all pre-event | no vote | 0.875 [0.798, 0.935] / 0.621 [0.538, 0.704] | 0.668 [0.619, 0.710]; 0.874 | +0.040; 0.020; met | +0.114 [+0.040, +0.197]; lower 0.051 | -0.008 [-0.024, +0.005]; lower -0.022 | +0.066 [+0.027, +0.103]; lower 0.035 |
| their, H-optimus-0 gate | NDBE pre-event | voted | 0.865 [0.752, 0.961] / 0.605 [0.506, 0.706] | 0.716 [0.666, 0.761]; 0.902 | +0.058; 0.008; not met | +0.115 [+0.000, +0.219]; lower 0.017 | +0.000 [-0.044, +0.036]; lower -0.036 | +0.067 [-0.018, +0.165]; lower 0.000 |
| their, H-optimus-0 gate | NDBE pre-event | no vote | 0.864 [0.770, 0.947] / 0.587 [0.491, 0.681] | 0.716 [0.666, 0.761]; 0.902 | +0.039; 0.015; not met | +0.110 [+0.030, +0.196]; lower 0.041 | -0.010 [-0.029, +0.004]; lower -0.026 | +0.073 [+0.024, +0.128]; lower 0.032 |

Cut-offs (all pre-event; median, range over folds): t_low 0.047 (0.004–0.102), c_star 0.600 (0.490–0.735), t_seq 0.244 (0.178–0.375); s\* 0.580 (0.407–0.803). Stored UNI2-h reference (all pre-event): share sequenced 0.458, voted Δ sensitivity against (B) +0.062 [+0.011, +0.116]; lower 0.020, voted B\* -0.006 [-0.051, +0.034].

One line: the H-optimus-0 gate sequences 0.668 of samples (UNI2-h 0.458) with the criterion against (B) met (voted lower 0.000; no vote lower 0.020) and no-vote Δ sensitivity against B\* -0.008 [-0.024, +0.005]; lower -0.022.

### F6. Permutation-trained gate (5 patient-level label permutations; outer and inner L-IMG refitted; their matrix, all pre-event)

| Permutation | Gate AUROC (fold-stratified) | L-LATE AUROC with the permuted gate | No vote: share sequenced / sensitivity / specificity | Voted: sensitivity / specificity; middle band in ≥ 1 repeat |
|---|---|---|---|---|
| 1 | 0.495 | 0.753 | 0.839 / 0.775 / 0.466 | 0.807 / 0.546; 1.000 |
| 2 | 0.519 | 0.752 | 0.834 / 0.786 / 0.476 | 0.826 / 0.549; 1.000 |
| 3 | 0.504 | 0.759 | 0.852 / 0.801 / 0.457 | 0.820 / 0.524; 1.000 |
| 4 | 0.510 | 0.755 | 0.845 / 0.783 / 0.473 | 0.851 / 0.534; 1.000 |
| 5 | 0.499 | 0.755 | 0.837 / 0.774 / 0.473 | 0.807 / 0.549; 1.000 |
| mean | 0.505 | — | 0.841 / 0.784 / 0.469 | 0.822 / 0.540; — |
| real gate (no vote) | — | — | 0.458 / 0.865 / 0.697 | — |

One line: a gate fitted on permuted labels (AUROC 0.505) sequences 0.841 of samples for sensitivity 0.784 and specificity 0.469, against 0.458, 0.865 and 0.697 for the real gate.

### F7. Leave-one-patient-out L-CNV

Not refitted: stored leave-one-patient-out predictions cover all 676 samples and 80 patients (check.json), so R21(b) used them (R21b above).

### Implementation notes

- R14c/R1-style evaluation matching uses the smallest held-out specificity ≥ the triage's (ceil rule, positive if score > threshold).
- R16 draws are the tb_selci draws (20 shards × 100).
- R17 max-T is single-step over centred bootstrap-t draws; Holm from percentile p.
- R19 trigger interval resamples 117 internal patients with all their samples (mean 891 samples per draw, not 234), so it is narrower than an interval for a 2-samples-per-patient cohort would be.
- R21b used the stored LOPO L-CNV predictions (killcoyne_mm/linear), so F7 was not refitted.
- R26 fold-model coefficient counts were not stored; λ ranges are reported instead.
- R27 same-patient exclusion also removes cross-copy pairs of a bootstrapped patient.
- F1 pre-event filter applies to outer and inner training rows; inner folds re-stratified over pre-event patients.
- F2: 48 patients, progressor count matched to the fold's training share.
- F3: the first 200 boots_for draws over the 75 pre-event patients; copies share their patient's fold; each draw has about 48 distinct patients, so refit models are weaker than the stored ones (per-draw triage sens 0.83, spec 0.60, share 0.57) and the interval is likely pessimistic.
- F4: deviance with 1e-5 clamp as km_linear.R; ties → largest λ.
- F6: one patient-level permutation per (perm, rep, fold), shared by outer and inner fits; cut-offs chosen against real labels.

### Checks

- f1_outer_unfiltered_vs_cfg_00_rep_01: n 676, max abs prediction difference 0.0, folds equal True, λ max abs difference 0.0: passed.
- f1_inner_unfiltered_vs_inner_img_rep_01_fold_01: n 618, max abs prediction difference 0.0, folds equal True, λ max abs difference 0.0: passed.
- f5_inner_uni2_vs_inner_img_rep_01_fold_01: n 618, max abs prediction difference 0.0, folds equal True, λ max abs difference 0.0: passed.
- f4_class_lambda_vs_cfg_00_rep_01: n 676, max abs prediction difference 0.0, folds equal True, λ max abs difference 0.0: passed.
- H-optimus-0 stored outer AUROC (all pre-event) 0.805 against the documented 0.805, folds equal True: passed.
- Stored leave-one-patient-out L-CNV: 676 rows, 80 patients, all samples covered True (km_linear.R cfg 0 (killcoyne_mm/linear), rule class_min); F7 needed: False. All checks passed: True.
- Round-1 numbers reproduced from the stored predictions: voted Δ sensitivity against B\* -0.006, against (B) +0.062, middle band in ≥ 1 repeat 0.760, per-repeat share sequenced 0.458 (R14); R4 transfer sensitivity 0.744 (R19); R12 high-band PPV at 5% 0.236 (R29); recomputed selection-inclusive draws against the stored tb_selci draws, max abs difference 0.0 (R16).


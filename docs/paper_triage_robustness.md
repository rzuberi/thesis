# Triage robustness, scanner transfer and ACE-B preparation

Status: PRE-SPECIFICATION (written 2026-10-09). Nothing below has been run. Results are appended under the line at the end in a later commit; this section is not edited afterwards.

**Ground rules** (as in `docs/paper_triage.md`, pre-specification f5944d2, results 650701b):
- Same population and the same stored fold-honest predictions: outer held-out predictions of the stratified patient-grouped 10-fold × 10-repeat CV (`kv_cv.R`, d69de24; `hz_fit.R` outer), and inner out-of-fold predictions (`hz_fit.R` inner) for every cut-off.
- Same cut-off rules and the same ≥ 6-of-10 vote.
- Their CNV matrix is primary; package features are a sensitivity analysis.
- No refitting except in item 5.
- Report only, with a status per item and at most one line of interpretation per question. Earlier documents are not edited, and patient lists stay on the cluster.

**Population.** The 676 samples from 80 patients of the Killcoyne discovery cohort with a matched H&E slide. Primary: all pre-event samples (571 samples, 75 patients). Secondary: NDBE pre-event samples.

**Patient bootstrap.** Unless stated otherwise: 2,000 patient-bootstrap draws (`RandomState(0)`, draws without both classes redrawn, resampled patients keep their folds), with the same draws as `paper_triage.md`.

## 1. Sequencing-budget curve

For each target share sequenced s = 0%, 5%, …, 100%, and in each repeat r and outer fold k, on the inner L-IMG predictions of that fold's population training rows (n training samples):

- **Youden threshold.** τ_J is the training L-IMG value that maximises Youden's J (sensitivity + specificity − 1, with score ≥ τ positive; ties go to the smaller τ).
- **Middle band.** It holds m = round(s·n) training samples closest to τ_J in rank: ⌈m/2⌉ immediately at or above τ_J and ⌊m/2⌋ immediately below it. When one side runs out, the remainder is taken from the other side. The band's score interval [lo, hi] is set by its lowest and highest member.
- **Held-out calls.**
  - Below lo: cleared.
  - Above hi: flagged.
  - In [lo, hi]: L-LATE at t_seq, the 80%-sensitivity threshold among training middle-band cases (the `paper_triage.md` rule, with the same fallback to all training cases when fewer than 5 cases are in the band).
  - s = 0%: H&E only, positive if L-IMG ≥ τ_J.
  - s = 100%: every sample sequenced with the L-LATE threshold from all training cases. This equals (B).
- **Vote:** positive in ≥ 6 of 10 repeats.
- **Reported at each s:**
  - sensitivity and specificity with patient-bootstrap 95% CIs;
  - the realised held-out share sequenced (mean over repeats), next to the target s.
- **Reference lines:** (A) sequence everyone with L-CNV and (B) sequence everyone with L-LATE, at the operating points of `paper_triage.md` (80%-sensitivity thresholds).
- **Smallest s matching (A):** the smallest s on the grid at which triage sensitivity ≥ (A)'s and triage specificity ≥ (A)'s; the same for (B).
  - Its 95% CI comes from recomputing that smallest s in each bootstrap draw, with calls held fixed. Draws where no s qualifies are recorded as "not reached" and counted.
  - If no s qualifies in the observed data, it is reported as not reached.
- **Figure:** `be_paper_figs/v3/14_F_budget_curve.{pdf,png}`: sensitivity and specificity, with CI bands, against target share sequenced; (A) and (B) as horizontal reference lines. Their matrix, all pre-event samples.
- **Also reported:** both CNV sources and both populations.

## 2. Cut-off grid

- The triage of `paper_triage.md` (L-LATE in the middle band) is re-run for t_low at 90%, 95% and 98% training sensitivity × t_high at 85%, 90% and 95% training specificity: 9 cells.
- The 95/90 cell must reproduce `paper_triage.md` exactly: sensitivity, specificity, share sequenced and missed counts identical to `results/paper_final/triage/their_pre.json`. If it does not, the analysis stops and the difference is reported.
- **Reported per cell:**
  - sensitivity and specificity;
  - share sequenced;
  - progressor patients with all samples missed;
  - Δ sensitivity and Δ specificity vs (A) and vs (B), with patient-bootstrap CIs (calls fixed).
- No cell is selected; the primary remains 95/90.
- Their matrix and package features; all pre-event and NDBE pre-event samples.

## 3. CIs including threshold selection

For the primary triage (95/90, L-LATE in the middle band) and for (A), (B) and (C), in each of 2,000 patient-bootstrap draws:
- resample patients (same seed and redraw rule);
- in every repeat and fold, re-choose every cut-off with the same rules on the resampled inner training predictions of that fold. A patient drawn w times contributes its training samples w times (weighted quantiles, as integer replication);
- recompute the held-out calls, the vote and the metrics on the resampled rows.

**Reported**, next to the fixed-threshold CIs of `paper_triage.md`:
- sensitivity and specificity per strategy;
- Δ sensitivity (triage − B) with its one-sided 95% lower bound (5th percentile); the primary criterion holds if it is > −0.05;
- Δ specificity (triage − A);
- the share sequenced.

Their matrix, all pre-event samples (primary); NDBE pre-event and package features (secondary).

## 4. Patient and endoscopy level

Endoscopy = the `Endoscopy` field of the sample table (`set_C.csv`); calls are the final ≥ 6-of-10 sample calls.

**Endoscopy level:**
- An endoscopy is positive if any of its population samples is positive; label = patient status.
- Sensitivity and specificity per endoscopy for triage, (A), (B) and (C), with patient-bootstrap CIs.
- Share of endoscopies with at least one sample sequenced (middle band; per repeat, mean over repeats), and share of samples sequenced.

**Patient level** (descriptive, exact counts, no tests):
- A progressor patient is caught if any pre-event endoscopy is positive; otherwise missed.
- A non-progressor patient is a false positive if any endoscopy is positive.
- Reported per strategy: caught and missed progressor patients, false-positive and true-negative non-progressor patients.

**Structure:** endoscopies per patient (mean, median, range) and samples per endoscopy (mean, median, range).

All four strategies, both populations, their matrix (package features for triage, A and B as sensitivity).

## 5. Scanner transfer (refits L-IMG only)

**Scanners:** C13239-01 and C13210 (`horizons/slide_desc.csv`). Pre-event samples only. Model as L-IMG:
- glmnet α 0.9, `standardize = FALSE`;
- λ by the class-error minimum of the 10 × 5 patient-grouped inner CV (`kv_common.R` `cvcurves`, unchanged);
- slide-mean UNI2-h embedding z-scored on the training rows.

**(a) Cross-scanner, primary design.** Train on all pre-event samples from scanner X; test on the pre-event samples from scanner Y, excluding test samples from patients with any sample in the training set. Both directions.

**(b) Cross-scanner, patient-disjoint secondary design.** Fixed now because many patients have samples on both scanners. Test on all pre-event samples from scanner Y; train on the scanner-X pre-event samples of patients with no scanner-Y sample. Both directions.

**Estimability.** A direction is estimable only if its test set has ≥ 10 patients including ≥ 2 progressor patients, and its training set has ≥ 3 progressor patients. Otherwise it is reported as not estimable, with its counts.

**(c) Within-scanner reference.** The stratified patient-grouped 10-fold × 10 CV (folds as `kv_cv.R`: `set.seed(repeat)`, progressor patients then non-progressor patients shuffled, cyclic) restricted to that scanner's pre-event samples. Fold-stratified AUROC, mean over repeats.

**Reported:**
- per-sample AUROC: cross-scanner (one model per direction and design; plain AUROC) and within-scanner, each with a patient-bootstrap 95% CI (2,000 draws, predictions fixed);
- the numbers of test samples, patients and progressor patients.

**Triage bands on the test scanner.**
- The cut-offs t_low (95% training sensitivity) and c* (90% training specificity) are chosen on inner out-of-fold predictions of the training scanner: a 5-fold patient-grouped, label-stratified split (`hz_fit.R` `strat_folds`, seed 1), each inner model fitted as above with λ from a 1 × 5 CV (`hz_fit.R` `cvcurves1`).
- They are applied to the cross-scanner model's predictions on the test scanner.
- Reported: the share of test samples in each band, by progressor status, next to the shares the training scanner's own inner out-of-fold predictions give.

**Harmonisation sensitivity analysis.** The same analyses with per-scanner z-scoring: each scanner's samples are standardised with that scanner's own mean and SD over its pre-event samples, which is transductive for the test scanner and uses no labels. The usual training-row z-scoring is then applied on top.

**Script:** `scripts/paper_plan/tb_scanner.R` (fits), with metrics in `tb_scanner_metrics.py`.

## 6. Frozen cut-offs and ACE-B power

**Frozen cut-offs.** Taken from the 100 repeat × fold cut-offs of `paper_triage.md` (their matrix, all pre-event samples), recomputed with the same rules by `tb_frozen.py`. They must reproduce the medians and ranges in `their_pre.json`.

| Cut-off | Value |
|---|---|
| t_low | median of the fold t_low |
| t_high = c* | median of the fold c*; the high band is L-IMG > c* |
| t_seq (L-LATE) | median of the fold t_seq |
| t_B | median of the fold 80%-sensitivity L-LATE thresholds of (B); needed for the criterion, added here |

- Each is written with its range, rule and source to `models/killcoyne_frozen_v1/triage_cutoffs.json`.
- Its SHA-256 goes under a new `addenda` key of `models/killcoyne_frozen_v1/MANIFEST.json`. The existing `files` entries and `bundle_sha256` (`17207de4…`, cited in `docs/paper_plan_killcoyne_checks.md`) are not changed, so the frozen bundle hash stays valid.
- The package-feature equivalents are reported in the results only. They are not written into `models/killcoyne_frozen_pkg_v1/`, whose bundle SHA-256 is part of the ACE-B primary pre-registration (`docs/aceb_primary_killcoyne.md`).
- Note: these cut-offs were chosen on fold-model predictions. Applying them to the frozen models (fitted on all 676 samples) assumes similar score distributions on new data.

**ACE-B power** for the triage primary criterion: non-inferior sensitivity vs (B), margin −0.05, one-sided α 0.05.
- **Scores:** each internal pre-event sample's repeat-mean held-out L-IMG and L-LATE predictions stand in for external frozen-model scores.
  - Triage call with the frozen cut-offs: cleared if L-IMG < t_low; flagged if L-IMG > c*; otherwise positive if L-LATE ≥ t_seq.
  - (B): positive if L-LATE ≥ t_B.
- **Sizes**, from `results/paper_final/killcoyne_final.json` `aceb_size`, amended plan with prevalent HGD/IMC excluded:
  - primary S2: 15 progressor and 67 non-progressor patients;
  - secondary: the owner's split without prevalent cases, 11 progressor and 93 non-progressor patients.
- **Simulation:** 2,000 simulations, seed = simulation index.
  - Draw the progressor and non-progressor patients with replacement from the internal pre-event patients, each bringing all its pre-event samples.
  - Compute Δ sensitivity (triage − B) per sample.
  - Run the criterion test within the simulated cohort: 2,000 patient-bootstrap draws, `RandomState(simulation index)`, one-sided 95% lower bound = 5th percentile.
  - Power = share of simulations with lower bound > −0.05.
- **Effects:**
  - E1, the internal effect: Δ under the frozen cut-offs on the internal cohort, as observed.
  - E2, the effect's lower bound: the one-sided 95% patient-bootstrap lower bound of that internal Δ. It is imposed by changing to negative, with probability q, the triage calls of progressor samples that are triage-positive and (B)-negative. q is set by bisection so that the internal Δ equals E2.
- **Reported:** power with a binomial 95% CI, median simulated Δ, and median lower bound, for each size × effect.

## Output

- **Scripts:** `scripts/paper_plan/tb_budget.py` (item 1), `tb_grid.py` (2), `tb_selci.py` (3, sharded by draws), `tb_levels.py` (4), `tb_scanner.R` with `tb_scanner_metrics.py` (5), `tb_frozen.py` and `tb_power.py` (6), `tb_fig.py`, `tb_render.py`. All run on Slurm via `scripts/cluster/campaign.sh`, prefix tb.
- **Aggregates:** `results/paper_final/triage_robustness/`.
- **Cluster only:** row-level outputs under `feasibility/paper_plan/killcoyne_mm/triage_robustness/`.

## Answers (one line each, in the results)

1. What share sequenced matches sequencing everyone with CNV alone, and with late fusion?
2. Does the triage result depend on the cut-off choice?
3. Does the primary criterion still hold with threshold selection included in the CIs?
4. At patient level, how many progressors does each strategy miss?
5. Does the histology model transfer between scanners, and does per-scanner standardisation help?
6. What are the frozen cut-offs, and what is ACE-B's power for the triage criterion?

---

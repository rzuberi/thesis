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

## Results

Pre-specification commit 32653f1; results commit ef8bb5f. Scripts `scripts/paper_plan/tb_*.py`, `tb_scanner.R` (Slurm via `scripts/cluster/campaign.sh`, prefixes tbs smoke, tb1, tb2), `tb_fig.py`, `tb_render.py`. Aggregates `results/paper_final/triage_robustness/`; row-level outputs on the cluster only. Figure `~/Downloads/be_paper_figs/v3/14_F_budget_curve.{pdf,png}`. Frozen cut-offs `models/killcoyne_frozen_v1/triage_cutoffs.json`.

### Status

| Item | Status |
|---|---|
| 1 Sequencing-budget curve | DONE |
| 2 Cut-off grid (95/90 reproduces paper_triage.md exactly) | DONE |
| 3 CIs including threshold selection | DONE |
| 4 Endoscopy and patient level | DONE (endoscopy unit clarified, see deviations) |
| 5 Scanner transfer | DONE; 2 of 4 planned directions not estimable by the pre-specified rule |
| 6 Frozen cut-offs and ACE-B power | DONE; `models/killcoyne_frozen_v1/triage_cutoffs.json` written, SHA-256 under the manifest's `addenda` |

### Answers

1. **A 70% band to match CNV alone, a 90% band to match late fusion (their matrix, all pre-event samples).**
   - The symmetric, Youden-centred band matches sequencing everyone with CNV alone at a 70% target share (58% of samples actually sequenced), and sequencing everyone with late fusion at a 90% target (82% sequenced).
   - The CIs are wide: against CNV alone, 0–90%, and not reached in 655 of 2,000 draws.
   - The CNV-alone match is not reached at any share on NDBE samples (their matrix) or with package features (all pre-event); with package features on NDBE samples it is reached at 90%.
   - This symmetric band adds specificity rather than sensitivity. The primary asymmetric triage (95/90) sequences 46% with higher sensitivity than both.
2. **Yes, through t_low.**
   - Across the 9 cells, the one-sided lower bound of Δ sensitivity vs (B) runs from −0.058 (90/95) to +0.061 (98/85), and the share sequenced from 30% to 65%.
   - The criterion (> −0.05) holds in 8 of 9 cells with their matrix; it fails only at 90/95.
   - With package features it holds in 6 of 9; it fails in all three cells with t_low at 90%.
3. **Yes.** With every cut-off re-chosen in each draw:
   - Δ sensitivity vs (B) is +0.062 [−0.015, +0.093], one-sided lower bound −0.007 > −0.05 (fixed thresholds: +0.020).
   - The share sequenced is 45.8% [34.4%, 54.0%], still below 70%.
   - Δ specificity vs (A) is +0.144 [+0.022, +0.293].
   - Once selection is included, a sensitivity gain over (B) is no longer shown.
4. **Triage misses 1 of 32 progressor patients; (A) misses 4, (B) 2 and (C) 1** (their matrix, all pre-event samples).
   - The cost is false positives in 30 of 43 non-progressor patients (A 29, B 28, C 35).
   - With package features, every strategy misses 1.
5. **Only from the larger scanner, and per-scanner standardisation does not help.**
   - The model trained on C13239-01 scores 0.726 [0.56, 0.86] on C13210 patients it never saw (within-C13239-01 CV: 0.841).
   - A model trained on the 27 C13210 patients fails within its own scanner (0.456) and on C13239-01 (0.541).
   - Per-scanner z-scoring gives 0.710 and 0.544.
6. **Frozen cut-offs: t_low 0.042, t_high 0.589, t_seq 0.233 and t_B 0.314.**
   - ACE-B power for the triage criterion is ≥ 0.98 at the internal effect under frozen cut-offs (Δ +0.075) and at its lower bound (+0.033). This holds for 15 progressor / 67 non-progressor patients (1.000 / 0.999) and for 11 / 93 (0.990 / 0.976).
   - The −0.05 margin is wide relative to the triage–(B) discordance.
   - Power to show a sensitivity gain was not assessed.

### 1. Sequencing-budget curve

**their, all pre-event.** (A): sensitivity 0.783, specificity 0.590; (B): 0.801, 0.785. Smallest share matching (A): 70% (95% CI 0%–90%; not reached in 655 of 2,000 draws); matching (B): 90% (95% CI 25%–90%; not reached in 0).

| Target share | Realised share | Sensitivity [95% CI] | Specificity [95% CI] |
|---|---|---|---|
| 0% | 0% | 0.696 [0.599, 0.806] | 0.832 [0.786, 0.874] |
| 5% | 4% | 0.702 [0.605, 0.803] | 0.829 [0.781, 0.873] |
| 10% | 7% | 0.714 [0.622, 0.815] | 0.829 [0.781, 0.874] |
| 15% | 10% | 0.720 [0.628, 0.817] | 0.832 [0.783, 0.875] |
| 20% | 14% | 0.727 [0.632, 0.826] | 0.824 [0.774, 0.869] |
| 25% | 18% | 0.733 [0.640, 0.831] | 0.839 [0.788, 0.884] |
| 30% | 22% | 0.733 [0.640, 0.831] | 0.846 [0.799, 0.889] |
| 35% | 25% | 0.739 [0.648, 0.833] | 0.844 [0.796, 0.887] |
| 40% | 29% | 0.752 [0.660, 0.841] | 0.844 [0.796, 0.887] |
| 45% | 34% | 0.752 [0.657, 0.843] | 0.844 [0.794, 0.889] |
| 50% | 38% | 0.752 [0.657, 0.843] | 0.844 [0.793, 0.890] |
| 55% | 43% | 0.758 [0.667, 0.845] | 0.841 [0.788, 0.888] |
| 60% | 48% | 0.764 [0.672, 0.856] | 0.846 [0.793, 0.894] |
| 65% | 53% | 0.764 [0.672, 0.856] | 0.849 [0.797, 0.896] |
| 70% | 58% | 0.783 [0.683, 0.875] | 0.851 [0.800, 0.898] |
| 75% | 64% | 0.783 [0.683, 0.875] | 0.834 [0.778, 0.884] |
| 80% | 69% | 0.789 [0.689, 0.882] | 0.832 [0.775, 0.882] |
| 85% | 76% | 0.795 [0.693, 0.887] | 0.822 [0.762, 0.876] |
| 90% | 82% | 0.801 [0.697, 0.893] | 0.807 [0.742, 0.867] |
| 95% | 90% | 0.801 [0.697, 0.893] | 0.795 [0.728, 0.856] |
| 100% | 100% | 0.801 [0.697, 0.893] | 0.785 [0.714, 0.850] |

**their, NDBE pre-event.** (A): sensitivity 0.798, specificity 0.560; (B): 0.788, 0.734. Smallest share matching (A): not reached (95% CI 0%–95%; not reached in 1087 of 2,000 draws); matching (B): 95% (95% CI 25%–95%; not reached in 0).

**package, all pre-event.** (A): sensitivity 0.839, specificity 0.700; (B): 0.832, 0.820. Smallest share matching (A): not reached (95% CI 0%–100%; not reached in 1001 of 2,000 draws); matching (B): 100% (95% CI 45%–100%; not reached in 0).

**package, NDBE pre-event.** (A): sensitivity 0.808, specificity 0.686; (B): 0.817, 0.760. Smallest share matching (A): 90% (95% CI 5%–95%; not reached in 759 of 2,000 draws); matching (B): 95% (95% CI 75%–95%; not reached in 0).

### 2. Cut-off grid (L-LATE in the middle band; the primary is 95/90; no cell selected)

**their, all pre-event** (95/90 reproduces `paper_triage.md`: yes).

| t_low sens / t_high spec | Sensitivity | Specificity | Share sequenced | Progressor patients all missed | Δ sens vs A | Δ spec vs A | Δ sens vs B | Δ spec vs B |
|---|---|---|---|---|---|---|---|---|
| 90 / 85 | 0.820 | 0.776 | 30% | 1 | +0.037 [-0.062, +0.146] | +0.185 [+0.059, +0.305] | +0.019 [-0.033, +0.074] | -0.010 [-0.061, +0.050] |
| 90 / 90 | 0.814 | 0.798 | 34% | 1 | +0.031 [-0.071, +0.143] | +0.207 [+0.082, +0.324] | +0.012 [-0.039, +0.068] | +0.012 [-0.031, +0.069] |
| 90 / 95 | 0.776 | 0.817 | 40% | 1 | -0.006 [-0.113, +0.110] | +0.227 [+0.108, +0.342] | -0.025 [-0.065, +0.017] | +0.032 [-0.008, +0.084] |
| 95 / 85 | 0.876 | 0.715 | 41% | 1 | +0.093 [+0.005, +0.192] | +0.124 [+0.011, +0.239] | +0.075 [+0.017, +0.137] | -0.071 [-0.120, -0.023] |
| 95 / 90 | 0.863 | 0.734 | 46% | 1 | +0.081 [-0.008, +0.178] | +0.144 [+0.029, +0.256] | +0.062 [+0.011, +0.116] | -0.051 [-0.092, -0.008] |
| 95 / 95 | 0.851 | 0.766 | 52% | 1 | +0.068 [-0.025, +0.167] | +0.176 [+0.064, +0.285] | +0.050 [+0.000, +0.101] | -0.020 [-0.053, +0.019] |
| 98 / 85 | 0.913 | 0.646 | 54% | 1 | +0.130 [+0.053, +0.221] | +0.056 [-0.036, +0.145] | +0.112 [+0.052, +0.185] | -0.139 [-0.183, -0.094] |
| 98 / 90 | 0.888 | 0.673 | 59% | 1 | +0.106 [+0.029, +0.194] | +0.083 [-0.014, +0.179] | +0.087 [+0.041, +0.145] | -0.112 [-0.151, -0.073] |
| 98 / 95 | 0.876 | 0.727 | 64% | 1 | +0.093 [+0.015, +0.181] | +0.137 [+0.038, +0.239] | +0.075 [+0.034, +0.125] | -0.059 [-0.089, -0.028] |

**their, NDBE pre-event** (95/90 reproduces `paper_triage.md`: yes).

| t_low sens / t_high spec | Sensitivity | Specificity | Share sequenced | Progressor patients all missed | Δ sens vs A | Δ spec vs A | Δ sens vs B | Δ spec vs B |
|---|---|---|---|---|---|---|---|---|
| 90 / 85 | 0.827 | 0.769 | 32% | 1 | +0.029 [-0.083, +0.146] | +0.210 [+0.097, +0.329] | +0.038 [-0.023, +0.095] | +0.036 [-0.019, +0.102] |
| 90 / 90 | 0.808 | 0.787 | 37% | 1 | +0.010 [-0.104, +0.120] | +0.228 [+0.117, +0.349] | +0.019 [-0.038, +0.067] | +0.054 [+0.002, +0.118] |
| 90 / 95 | 0.769 | 0.805 | 43% | 1 | -0.029 [-0.160, +0.097] | +0.246 [+0.130, +0.368] | -0.019 [-0.073, +0.021] | +0.072 [+0.021, +0.135] |
| 95 / 85 | 0.875 | 0.704 | 45% | 1 | +0.077 [+0.000, +0.167] | +0.144 [+0.046, +0.249] | +0.087 [+0.018, +0.159] | -0.030 [-0.074, +0.015] |
| 95 / 90 | 0.856 | 0.728 | 49% | 1 | +0.058 [-0.033, +0.158] | +0.168 [+0.066, +0.278] | +0.067 [+0.013, +0.128] | -0.006 [-0.049, +0.042] |
| 95 / 95 | 0.837 | 0.743 | 55% | 1 | +0.038 [-0.052, +0.135] | +0.183 [+0.080, +0.293] | +0.048 [+0.000, +0.094] | +0.009 [-0.032, +0.057] |
| 98 / 85 | 0.894 | 0.626 | 59% | 1 | +0.096 [+0.013, +0.198] | +0.066 [-0.014, +0.151] | +0.106 [+0.043, +0.176] | -0.108 [-0.157, -0.067] |
| 98 / 90 | 0.885 | 0.650 | 63% | 1 | +0.087 [+0.010, +0.177] | +0.090 [+0.006, +0.184] | +0.096 [+0.036, +0.168] | -0.084 [-0.124, -0.048] |
| 98 / 95 | 0.856 | 0.671 | 69% | 1 | +0.058 [-0.026, +0.151] | +0.111 [+0.023, +0.208] | +0.067 [+0.022, +0.122] | -0.063 [-0.101, -0.032] |

**package, all pre-event** (95/90 reproduces `paper_triage.md`: yes).

| t_low sens / t_high spec | Sensitivity | Specificity | Share sequenced | Progressor patients all missed | Δ sens vs A | Δ spec vs A | Δ sens vs B | Δ spec vs B |
|---|---|---|---|---|---|---|---|---|
| 90 / 85 | 0.820 | 0.793 | 30% | 1 | -0.019 [-0.113, +0.085] | +0.093 [+0.000, +0.202] | -0.012 [-0.061, +0.041] | -0.027 [-0.075, +0.034] |
| 90 / 90 | 0.820 | 0.815 | 34% | 1 | -0.019 [-0.113, +0.085] | +0.115 [+0.021, +0.228] | -0.012 [-0.061, +0.041] | -0.005 [-0.052, +0.060] |
| 90 / 95 | 0.814 | 0.841 | 40% | 1 | -0.025 [-0.123, +0.078] | +0.141 [+0.048, +0.251] | -0.019 [-0.062, +0.028] | +0.022 [-0.018, +0.081] |
| 95 / 85 | 0.882 | 0.739 | 41% | 1 | +0.043 [-0.044, +0.139] | +0.039 [-0.042, +0.136] | +0.050 [+0.000, +0.109] | -0.080 [-0.125, -0.032] |
| 95 / 90 | 0.863 | 0.763 | 46% | 1 | +0.025 [-0.068, +0.124] | +0.063 [-0.021, +0.161] | +0.031 [-0.013, +0.090] | -0.056 [-0.099, -0.009] |
| 95 / 95 | 0.863 | 0.798 | 52% | 1 | +0.025 [-0.068, +0.124] | +0.098 [+0.012, +0.200] | +0.031 [-0.013, +0.090] | -0.022 [-0.064, +0.028] |
| 98 / 85 | 0.907 | 0.693 | 54% | 1 | +0.068 [-0.010, +0.153] | -0.007 [-0.074, +0.071] | +0.075 [+0.030, +0.130] | -0.127 [-0.167, -0.088] |
| 98 / 90 | 0.894 | 0.715 | 59% | 1 | +0.056 [-0.019, +0.135] | +0.015 [-0.055, +0.094] | +0.062 [+0.018, +0.120] | -0.105 [-0.141, -0.071] |
| 98 / 95 | 0.876 | 0.756 | 64% | 1 | +0.037 [-0.050, +0.128] | +0.056 [-0.017, +0.139] | +0.043 [+0.006, +0.098] | -0.063 [-0.101, -0.030] |

**package, NDBE pre-event** (95/90 reproduces `paper_triage.md`: yes).

| t_low sens / t_high spec | Sensitivity | Specificity | Share sequenced | Progressor patients all missed | Δ sens vs A | Δ spec vs A | Δ sens vs B | Δ spec vs B |
|---|---|---|---|---|---|---|---|---|
| 90 / 85 | 0.827 | 0.743 | 32% | 1 | +0.019 [-0.084, +0.131] | +0.057 [-0.036, +0.165] | +0.010 [-0.046, +0.054] | -0.018 [-0.067, +0.041] |
| 90 / 90 | 0.808 | 0.775 | 37% | 1 | +0.000 [-0.100, +0.111] | +0.090 [+0.000, +0.195] | -0.010 [-0.072, +0.043] | +0.015 [-0.030, +0.074] |
| 90 / 95 | 0.798 | 0.808 | 43% | 1 | -0.010 [-0.112, +0.104] | +0.123 [+0.032, +0.227] | -0.019 [-0.080, +0.029] | +0.048 [+0.006, +0.102] |
| 95 / 85 | 0.865 | 0.722 | 45% | 1 | +0.058 [-0.035, +0.155] | +0.036 [-0.052, +0.135] | +0.048 [+0.000, +0.096] | -0.039 [-0.080, +0.013] |
| 95 / 90 | 0.846 | 0.737 | 49% | 1 | +0.038 [-0.064, +0.139] | +0.051 [-0.037, +0.153] | +0.029 [-0.014, +0.078] | -0.024 [-0.066, +0.025] |
| 95 / 95 | 0.837 | 0.763 | 55% | 1 | +0.029 [-0.073, +0.132] | +0.078 [-0.005, +0.174] | +0.019 [-0.022, +0.067] | +0.003 [-0.033, +0.047] |
| 98 / 85 | 0.885 | 0.659 | 59% | 1 | +0.077 [-0.009, +0.168] | -0.027 [-0.092, +0.044] | +0.067 [+0.023, +0.112] | -0.102 [-0.134, -0.069] |
| 98 / 90 | 0.885 | 0.677 | 63% | 1 | +0.077 [-0.009, +0.168] | -0.009 [-0.075, +0.066] | +0.067 [+0.023, +0.112] | -0.084 [-0.112, -0.054] |
| 98 / 95 | 0.856 | 0.701 | 69% | 1 | +0.048 [-0.049, +0.147] | +0.015 [-0.054, +0.097] | +0.038 [+0.000, +0.083] | -0.060 [-0.088, -0.032] |

### 3. CIs including threshold selection (2,000 draws; cut-offs re-chosen in every draw)

| Population | Strategy | Sensitivity | CI, selection-inclusive | CI, fixed thresholds | Specificity | CI, selection-inclusive | CI, fixed thresholds |
|---|---|---|---|---|---|---|---|
| their, all pre-event | Triage (L-LATE middle band) | 0.863 | [0.802, 0.895] | [0.774, 0.942] | 0.734 | [0.610, 0.830] | [0.667, 0.802] |
| their, all pre-event | (A) sequence everyone, L-CNV | 0.783 | [0.726, 0.860] | [0.651, 0.888] | 0.590 | [0.403, 0.749] | [0.469, 0.722] |
| their, all pre-event | (B) sequence everyone, L-LATE | 0.801 | [0.765, 0.871] | [0.697, 0.893] | 0.785 | [0.657, 0.889] | [0.714, 0.850] |
| their, all pre-event | (C) H&E only, L-IMG | 0.789 | [0.741, 0.822] | [0.703, 0.875] | 0.754 | [0.651, 0.836] | [0.693, 0.811] |
| their, NDBE pre-event | Triage (L-LATE middle band) | 0.856 | [0.759, 0.903] | [0.742, 0.955] | 0.728 | [0.583, 0.832] | [0.646, 0.798] |
| their, NDBE pre-event | (A) sequence everyone, L-CNV | 0.798 | [0.704, 0.867] | [0.652, 0.931] | 0.560 | [0.369, 0.758] | [0.430, 0.688] |
| their, NDBE pre-event | (B) sequence everyone, L-LATE | 0.788 | [0.740, 0.868] | [0.667, 0.900] | 0.734 | [0.595, 0.873] | [0.644, 0.813] |
| their, NDBE pre-event | (C) H&E only, L-IMG | 0.779 | [0.723, 0.829] | [0.689, 0.873] | 0.710 | [0.616, 0.825] | [0.643, 0.768] |
| package, all pre-event | Triage (L-LATE middle band) | 0.863 | [0.806, 0.915] | [0.779, 0.945] | 0.763 | [0.681, 0.850] | [0.690, 0.824] |
| package, all pre-event | (A) sequence everyone, L-CNV | 0.839 | [0.759, 0.870] | [0.745, 0.916] | 0.700 | [0.554, 0.830] | [0.564, 0.810] |
| package, all pre-event | (B) sequence everyone, L-LATE | 0.832 | [0.776, 0.861] | [0.728, 0.924] | 0.820 | [0.693, 0.920] | [0.741, 0.885] |
| package, all pre-event | (C) H&E only, L-IMG | 0.789 | [0.741, 0.822] | [0.703, 0.875] | 0.754 | [0.651, 0.836] | [0.693, 0.811] |

| Population | Δ sensitivity triage − B [selection-inclusive CI]; one-sided 95% lower | Fixed-threshold CI; lower | Criterion (> −0.05) | Δ specificity triage − A [selection-inclusive CI] | Fixed-threshold CI | Share sequenced [selection-inclusive CI] |
|---|---|---|---|---|---|---|
| their, all pre-event | +0.062 [-0.015, +0.093]; -0.007 | [+0.011, +0.116]; 0.020 | holds | +0.144 [+0.022, +0.293] | [+0.029, +0.256] | 46% [34%, 54%] |
| their, NDBE pre-event | +0.067 [-0.026, +0.108]; -0.018 | [+0.013, +0.128]; 0.021 | holds | +0.168 [+0.025, +0.306] | [+0.066, +0.278] | 49% [36%, 58%] |
| package, all pre-event | +0.031 [-0.012, +0.096]; -0.006 | [-0.013, +0.090]; -0.006 | holds | +0.063 [-0.028, +0.178] | [-0.021, +0.161] | 46% [34%, 54%] |

### 4. Endoscopy and patient level

**their, all pre-event** (571 samples, 288 endoscopies of which 88 from progressors, 75 patients; endoscopies per patient mean 3.84, median 4, range 1–9; samples per endoscopy mean 1.983, median 2, range 1–8). Triage sequences 46% of samples and touches 60% of endoscopies (≥ 1 sample sequenced).

| Strategy | Endoscopy sensitivity [95% CI] | Endoscopy specificity [95% CI] | Progressor patients caught / missed | Non-progressor patients false positive / true negative |
|---|---|---|---|---|
| Triage (L-LATE middle band) | 0.898 [0.833, 0.959] | 0.590 [0.497, 0.681] | 31 / 1 | 30 / 13 |
| (A) sequence everyone, L-CNV | 0.818 [0.691, 0.925] | 0.545 [0.411, 0.671] | 28 / 4 | 29 / 14 |
| (B) sequence everyone, L-LATE | 0.852 [0.753, 0.933] | 0.650 [0.558, 0.744] | 30 / 2 | 28 / 15 |
| (C) H&E only, L-IMG | 0.886 [0.815, 0.955] | 0.575 [0.497, 0.658] | 31 / 1 | 35 / 8 |

**their, NDBE pre-event** (438 samples, 240 endoscopies of which 68 from progressors, 71 patients; endoscopies per patient mean 3.38, median 3, range 1–8; samples per endoscopy mean 1.825, median 1, range 1–8). Triage sequences 49% of samples and touches 60% of endoscopies (≥ 1 sample sequenced).

| Strategy | Endoscopy sensitivity [95% CI] | Endoscopy specificity [95% CI] | Progressor patients caught / missed | Non-progressor patients false positive / true negative |
|---|---|---|---|---|
| Triage (L-LATE middle band) | 0.926 [0.867, 0.983] | 0.576 [0.466, 0.681] | 27 / 1 | 27 / 16 |
| (A) sequence everyone, L-CNV | 0.838 [0.729, 0.935] | 0.512 [0.378, 0.642] | 25 / 3 | 28 / 15 |
| (B) sequence everyone, L-LATE | 0.882 [0.800, 0.955] | 0.593 [0.477, 0.703] | 27 / 1 | 28 / 15 |
| (C) H&E only, L-IMG | 0.882 [0.797, 0.955] | 0.547 [0.464, 0.628] | 27 / 1 | 35 / 8 |

**package, all pre-event** (571 samples, 288 endoscopies of which 88 from progressors, 75 patients; endoscopies per patient mean 3.84, median 4, range 1–9; samples per endoscopy mean 1.983, median 2, range 1–8). Triage sequences 46% of samples and touches 60% of endoscopies (≥ 1 sample sequenced).

| Strategy | Endoscopy sensitivity [95% CI] | Endoscopy specificity [95% CI] | Progressor patients caught / missed | Non-progressor patients false positive / true negative |
|---|---|---|---|---|
| Triage (L-LATE middle band) | 0.955 [0.904, 1.000] | 0.630 [0.550, 0.709] | 31 / 1 | 30 / 13 |
| (A) sequence everyone, L-CNV | 0.943 [0.890, 0.986] | 0.625 [0.487, 0.749] | 31 / 1 | 27 / 16 |
| (B) sequence everyone, L-LATE | 0.920 [0.852, 0.974] | 0.725 [0.634, 0.807] | 31 / 1 | 26 / 17 |
| (C) H&E only, L-IMG | 0.886 [0.815, 0.955] | 0.575 [0.497, 0.658] | 31 / 1 | 35 / 8 |

**package, NDBE pre-event** (438 samples, 240 endoscopies of which 68 from progressors, 71 patients; endoscopies per patient mean 3.38, median 3, range 1–8; samples per endoscopy mean 1.825, median 1, range 1–8). Triage sequences 49% of samples and touches 60% of endoscopies (≥ 1 sample sequenced).

| Strategy | Endoscopy sensitivity [95% CI] | Endoscopy specificity [95% CI] | Progressor patients caught / missed | Non-progressor patients false positive / true negative |
|---|---|---|---|---|
| Triage (L-LATE middle band) | 0.956 [0.899, 1.000] | 0.599 [0.508, 0.688] | 27 / 1 | 31 / 12 |
| (A) sequence everyone, L-CNV | 0.912 [0.846, 0.970] | 0.622 [0.488, 0.743] | 27 / 1 | 26 / 17 |
| (B) sequence everyone, L-LATE | 0.941 [0.868, 1.000] | 0.651 [0.541, 0.750] | 27 / 1 | 28 / 15 |
| (C) H&E only, L-IMG | 0.882 [0.797, 0.955] | 0.547 [0.464, 0.628] | 27 / 1 | 35 / 8 |

### 5. Scanner transfer (L-IMG refitted; C13239-01 = s39, C13210 = s10)

| Within-scanner CV | AUROC, fold-stratified [95% CI] | Samples | Patients (progressor) |
|---|---|---|---|
| s39 | 0.841 [0.788, 0.890] | 432 | 71 (31) |
| s10 | 0.456 [0.392, 0.532] | 139 | 27 (9) |

| Design, training → test, harmonisation | Estimable | AUROC on test scanner [95% CI] | Test samples, patients (progressor) | Training patients (progressor) | Test bands low / middle / high (training-scanner inner OOF) |
|---|---|---|---|---|---|
| (a) s10 → s39, none | yes | 0.541 [0.436, 0.634] | 312, 48 (23) | 27 (9) | 0% / 66% / 34% (4% / 88% / 9%) |
| (a) s10 → s39, per-scanner z | yes | 0.544 [0.441, 0.639] | 312, 48 (23) | 27 (9) | 0% / 94% / 5% (4% / 88% / 9%) |
| (a) s39 → s10, none | no | — | 30, 4 (1) | 71 (31) | — |
| (a) s39 → s10, per-scanner z | no | — | 30, 4 (1) | 71 (31) | — |
| (b) s10 → s39, none | no | — | 432, 71 (31) | 4 (1) | — |
| (b) s10 → s39, per-scanner z | no | — | 432, 71 (31) | 4 (1) | — |
| (b) s39 → s10, none | yes | 0.726 [0.560, 0.860] | 139, 27 (9) | 48 (23) | 50% / 30% / 21% (18% / 61% / 20%) |
| (b) s39 → s10, per-scanner z | yes | 0.710 [0.542, 0.846] | 139, 27 (9) | 48 (23) | 43% / 34% / 23% (18% / 61% / 20%) |

### 6. Frozen cut-offs and ACE-B power

| Cut-off | Their matrix: median (range) — written to `models/killcoyne_frozen_v1/triage_cutoffs.json` | Package features: median (range) — reported only |
|---|---|---|
| t_low | 0.0417 (0.0049–0.1091) | 0.0417 (0.0049–0.1091) |
| t_high | 0.5889 (0.4887–0.7249) | 0.5889 (0.4887–0.7249) |
| t_seq | 0.2334 (0.1592–0.3277) | 0.2365 (0.1672–0.3060) |
| t_B | 0.3143 (0.2250–0.4415) | 0.3315 (0.2214–0.4164) |

Frozen cut-offs on the internal repeat-mean held-out predictions (all pre-event samples): triage sensitivity 0.901 vs (B) 0.826 (E1 Δ +0.075; one-sided 95% lower bound E2 +0.033); specificity 0.673 vs 0.768; share sequenced 51%.

| ACE-B size | Effect | Target Δ | Power [95% CI] | Median simulated Δ | Median lower bound |
|---|---|---|---|---|---|
| S2 (database, prevalent excluded): 15 P / 67 NP patients | E1 | +0.075 | 1.000 [0.997, 1.000] | +0.072 | +0.018 |
| S2 (database, prevalent excluded): 15 P / 67 NP patients | E2 | +0.033 | 0.999 [0.996, 1.000] | +0.031 | +0.000 |
| owner split, prevalent excluded: 11 P / 93 NP patients | E1 | +0.075 | 0.990 [0.985, 0.994] | +0.071 | +0.006 |
| owner split, prevalent excluded: 11 P / 93 NP patients | E2 | +0.033 | 0.976 [0.968, 0.981] | +0.032 | +0.000 |

### Deviations and caveats

- Endoscopy unit: the `Endoscopy` field of the sample table numbers endoscopies within each patient (11 distinct values), so the unit used is (patient, endoscopy number): 288 endoscopies from 75 patients on pre-event samples.
- Scanner transfer: by the pre-specified estimability rule, design (a) C13239-01 → C13210 (4 test patients) and design (b) C13210 → C13239-01 (4 training patients) are not estimable, because 23 patients have slides on both scanners. The estimable directions are (a) C13210 → C13239-01 and (b) C13239-01 → C13210.
- The within-scanner CV on C13210 (139 samples, 27 patients, 9 progressors) gives AUROC 0.456, below 0.5. Cross-validation is known to be biased downwards in very small samples; this is reported, not interpreted further.
- Selection-inclusive bootstrap distributions are not centred on the point estimates (e.g. Δ sensitivity vs (B): +0.062, 95% CI [−0.015, +0.093]). Percentile intervals are reported as pre-specified.
- Selection-inclusive sensitivity CIs are narrower than the fixed-threshold ones and specificity CIs wider (e.g. (B) sensitivity [0.765, 0.871] vs [0.697, 0.893]). Re-choosing the thresholds in each draw pins training sensitivity at its target, so held-out sensitivity varies less and specificity absorbs the variation.
- Budget curve: the held-out share sequenced is lower than the target share (e.g. 70% target, 58% sequenced), because the band is the training score interval. Both are reported; the figure uses the target share, as pre-specified.
- ACE-B power: the frozen cut-offs are applied to each sample's repeat-mean held-out predictions (pre-specified), not to the ≥ 6-of-10 vote, so the internal Δ (+0.075) differs from `paper_triage.md`'s +0.062. Specificity under frozen cut-offs: triage 0.673 vs (B) 0.768; 51% of samples sequenced.
- The run was split into a smoke batch (prefix tbs, 7 tasks), the main batch (tb1, 66 tasks) and merges (tb2, 4 tasks). The smoke outputs are part of the results.


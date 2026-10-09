# H&E-first triage: who needs sequencing?

Status: PRE-SPECIFICATION (written 2026-10-09). Nothing below has been run. Results are appended under the line at the end in a later commit; this section is not edited afterwards.

**Ground rules** (as in `docs/paper_risk_strata.md`):
- No refitting: only stored fold-honest predictions are used.
- Report only, with a status per item and at most one line of interpretation per question.
- Earlier documents are not edited, and patient lists stay on the cluster.

## Data

- **Population:** the 676 samples from 80 patients of the Killcoyne discovery cohort with a matched H&E slide.
  - Primary: all pre-event samples (571 samples, 75 patients).
  - Secondary: NDBE pre-event samples (438 samples, 71 patients).
- **CNV source:** their CNV matrix is primary; package features are a sensitivity analysis.
- **Label:** ever-progression to HGD/IMC (patient status), as in all earlier per-sample analyses.
- **Held-out (outer) predictions:** the stratified, patient-grouped 10-fold × 10-repeat CV of `kv_cv.R` (d69de24):
  - L-CNV: cfg 0 their / cfg 1 package;
  - L-IMG: cfg 2;
  - L-EARLY: cfg 3 / 4;
  - L-INTER: `hz_fit.R` MODE=outer, same folds;
  - L-LATE: per-repeat mean of the L-CNV and L-IMG probabilities.
- **Training-fold predictions for choosing cut-offs:** the stored inner 5-fold out-of-fold predictions of each outer training fold (`hz_fit.R` MODE=inner, `horizons/inner/`; all 100 repeat × fold cells exist for every model). Inner L-LATE is the mean of inner L-CNV and inner L-IMG on the same inner folds, as in `ha_q2.py`.
  - The training rows used to choose any cut-off are the outer training samples that belong to the population (pre-event, or NDBE pre-event).
  - Cut-offs never see the held-out fold.

## 1. Is histology non-inferior to CNV?

- **Metric:** per-sample, fold-stratified AUROC (only case–control pairs in the same outer fold of a repeat; folds without both classes skipped), mean over the 10 repeats. This is the scoring of `docs/paper_horizon_foldstrat.md` and `rs_strata.py` `fs_auc`.
- **Non-inferiority, L-IMG vs L-CNV:** Δ = AUROC(L-IMG) − AUROC(L-CNV), margin −0.05.
  - The one-sided 95% lower bound is the 5th percentile of Δ over 2,000 patient-bootstrap draws (seed 0; draws without both classes redrawn; resampled patients keep their folds; predictions fixed).
  - L-IMG is non-inferior if the lower bound is > −0.05.
- **Reported for:** both CNV sources and both populations. The primary claim is their matrix, all pre-event samples.
- **Fusion vs histology alone:** Δ(L-EARLY − L-IMG), Δ(L-INTER − L-IMG) and Δ(L-LATE − L-IMG), each with a percentile 95% CI, an unadjusted two-sided bootstrap p, and a max-T adjusted p over these three comparisons.
  - Max-T adjusted p is the share of draws with max_k |(Δ*_k − Δ_k)/SD*_k| ≥ |Δ_j/SD*_j|.
  - Computed per CNV source and population, the same way fusion vs CNV was tested.

## 2. Triage strategy

**Bands.** Each sample's H&E score is its L-IMG probability. In each repeat r and outer fold k, two cut-offs are chosen on the inner L-IMG predictions of that fold's population training rows only, then applied to the held-out fold:

- **t_low:** the largest value keeping ≥ 95% sensitivity among training cases. Training-case scores are sorted in descending order, and t_low is the ⌈0.95·n_cases⌉-th of them.
  - Low band (cleared without sequencing): L-IMG < t_low.
- **t_high:** the smallest value keeping ≥ 90% specificity among training controls. With c* the ⌈0.9·n_controls⌉-th smallest training-control score, the high band (flagged high risk without sequencing) is L-IMG > c*. That is the smallest cut-off that leaves at least 90% of training controls below it.
- **Middle band** (sequenced): t_low ≤ L-IMG ≤ c*.
- **No middle band:** if t_low > c* in a fold, that fold has no middle band.
  - The call there is H&E-only: positive if L-IMG > c*, otherwise cleared. This favours sensitivity: both training targets are met at c*.
  - How often this happens is reported.

**Sequencing call.** For a middle-band sample, the final call uses the sequenced-band model at threshold t_seq: L-LATE (primary) or L-CNV (secondary).
- t_seq is the largest threshold keeping ≥ 80% sensitivity (the `ha_q2.py:49` rule) among the population training cases that fall in that fold's training middle band, as defined by that fold's cut-offs on the inner L-IMG predictions. It is applied to the model's inner predictions to choose it, and to its held-out predictions to call.
- If a fold's training middle band holds fewer than 5 cases, t_seq is instead the model's 80%-sensitivity threshold on all population training cases. How often this happens is reported.

**Final call.** Low band → negative; high band → positive; middle band → model score ≥ t_seq. A sample's final call is positive if it is positive in ≥ 6 of 10 repeats (as in `ha_q2.py`).

**Comparators.** Each uses its own fold-chosen 80%-sensitivity threshold on the inner predictions of all population training cases, and the same ≥ 6-of-10 vote:
- (A) sequence everyone, L-CNV;
- (B) sequence everyone, L-LATE;
- (C) H&E only, L-IMG.

## 3. What is reported

**Per strategy:** triage with L-LATE in the middle band, triage with L-CNV in the middle band, A, B and C. Each is reported for both populations; triage, A and B for both CNV sources.
- **Calls:**
  - sensitivity and specificity of the final calls, with patient-bootstrap 95% CIs;
  - the number of progressor samples missed;
  - progressor patients with at least one missed sample, and with every pre-event sample missed.
- **Triage band shares:**
  - the share of samples sequenced (middle band), and the share in each band, overall and by progressor status;
  - per repeat these are shares of samples, and the reported value is the mean over the 10 repeats, with a patient-bootstrap CI;
  - plus the cut-offs (median and range over the 100 folds), the number of folds without a middle band, and the number of t_seq fallbacks.
- **Paired differences:** triage vs (A) and vs (B) in sensitivity and specificity, with patient-bootstrap 95% CIs. The calls are fixed and the draws are those of Section 1.

**Primary success criterion, fixed now.** Triage with L-LATE in the middle band (their matrix, all pre-event samples) must meet both of:
- non-inferiority to (B) in sensitivity at margin −0.05: the 5th percentile of the bootstrap Δ sensitivity (triage − B) is > −0.05;
- a point-estimate share of samples sequenced below 70%.

**Secondary questions.**
- **Does CNV discriminate better where histology is uncertain?** In the middle band only, compare the AUROC of L-CNV and L-IMG.
  - Per repeat, the fold-stratified AUROC is computed on the held-out samples in that repeat's middle band; the mean is over repeats, skipping folds without both classes.
  - Paired Δ (L-CNV − L-IMG) with a patient-bootstrap CI and unadjusted p. L-LATE vs L-IMG in the middle band is reported alongside.
- **Characteristics of the middle band against the low and high bands:**
  - mean (SD) raw cx (package `cx`, unscaled with the frozen constants of `models/killcoyne_frozen_pkg_v1/cnv_scaling_setC.csv`);
  - mean (SD) and median tissue tile count (`horizons/slide_desc.csv`);
  - grade shares (NDBE / ID / LGD);
  - share scanned on C13210.
  - These are pooled over sample × repeat band assignments, each counted 1/10. Report only, no tests.

## 4. Prevalence

The cohort is matched case–control: 161 of 571 pre-event samples (28%) are from progressors.

- **Projection:** with m₁ and m₀ the middle-band rates among progressor and non-progressor samples (mean over repeats), the share sequenced at progressor-sample prevalence π is π·m₁ + (1 − π)·m₀. Band membership rates within each class are unchanged.
- The same projection is applied to the low and high bands.
- Reported at π = 2%, 5% and 10% (and at the observed π), with patient-bootstrap CIs.
- These are projections, not observations.

## Output

- **Script:** `scripts/paper_plan/tr_triage.py`, run on Slurm via `scripts/cluster/campaign.sh`, prefix tr. TASK = `<src>_<pop>`, with src in their | pkg and pop in pre | pre_ndbe.
- **Aggregates:** `results/paper_final/triage/<TASK>.json`.
- **Cluster only:** per-sample calls and bands (`feasibility/paper_plan/killcoyne_mm/triage/`).
- **Figure:** `be_paper_figs/v3/13_F_triage.{pdf,png}` (`scripts/paper_plan/tr_fig.py`, drawn from aggregates). Their matrix, all pre-event samples, triage with L-LATE.
  - Panel 1, sample flow: all samples → three bands → final calls, with progressor and non-progressor counts per box. The band shown is each sample's most frequent band over the 10 repeats (ties → middle); the call is the ≥ 6-of-10 final call.
  - Panel 2: share sequenced against progressor-sample prevalence (0.5–30%), marking 2%, 5%, 10% and the observed value.
- **Renderer:** `scripts/paper_plan/tr_render.py`.

## Answers (one line each, in the results)

1. Is histology non-inferior to CNV at margin −0.05? Does fusion beat histology alone?
2. Does the triage strategy meet the primary success criterion, and what share of samples does it sequence?
3. In the middle band, does CNV add discrimination over histology?
4. What share of samples would be sequenced at real-world prevalence?

---

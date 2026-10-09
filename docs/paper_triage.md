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

## Results

Pre-specification commit f5944d2; results commit 650701b. Scripts `scripts/paper_plan/tr_triage.py` (Slurm via `scripts/cluster/campaign.sh`, prefix tr), `tr_fig.py`, `tr_render.py`. Aggregates `results/paper_final/triage/{their,pkg}_{pre,pre_ndbe}.json`; per-sample bands, calls and missed-patient rows on the cluster only (`feasibility/paper_plan/killcoyne_mm/triage/`). Figure `~/Downloads/be_paper_figs/v3/13_F_triage.{pdf,png}`. All CIs: 2,000 patient-bootstrap draws; p unadjusted unless stated.

### Status

| Item | Status |
|---|---|
| 1 Non-inferiority of histology; fusion vs histology | DONE |
| 2 Triage strategy and comparators | DONE |
| 3 Strategy metrics, paired differences, middle band | DONE |
| 4 Prevalence projection | DONE |
| Primary success criterion | MET: lower bound Δ sensitivity vs (B) 0.020 (> −0.05: yes); share sequenced 45.8% (< 70%: yes) |

### Answers

1. **Histology is non-inferior to CNV with their matrix, not with package features; only late fusion beats histology, and with their matrix only borderline.** L-IMG 0.847 vs L-CNV 0.801: Δ +0.045, one-sided 95% lower bound −0.025 > −0.05 (NDBE −0.030). With package features the lower bound is −0.062 (NDBE −0.061). L-LATE − L-IMG +0.042 [+0.002, +0.078], max-T adjusted p 0.066 (package +0.056, p 0.010). Early and inter fusion do not beat L-IMG (adjusted p ≥ 0.25).
2. **Yes.** Triage with L-LATE in the middle band has sensitivity 0.863 vs 0.801 for sequencing everyone with L-LATE: Δ +0.062, one-sided lower bound +0.020 > −0.05. It sequences 45.8% [40.8%, 50.4%] of samples. Specificity is lower (0.734 vs 0.785, Δ −0.051 [−0.092, −0.008]), and it misses 22 progressor samples from 9 patients, against 32 from 15 for (B).
3. **Yes.** In the middle band, L-CNV AUROC is 0.786 vs L-IMG 0.650: Δ +0.136 [+0.011, +0.238] (their matrix, all pre-event samples). On NDBE samples it is +0.106 [−0.012, +0.226], and with package features +0.191. L-IMG's AUROC there is restricted by construction, because the band is defined by L-IMG.
4. **About half.** Projected share sequenced: 49.4% at 2%, 49.0% at 5% and 48.3% at 10% progressor-sample prevalence (45.8% observed at 28%). Half of non-progressor samples fall in the middle band, so the share barely changes with prevalence. These are projections, not observations.

### 1. Histology vs CNV (fold-stratified per-sample AUROC, mean over 10 repeats)

| CNV source, population | L-IMG | L-CNV | Δ (L-IMG − L-CNV) [95% CI] | One-sided 95% lower bound | Non-inferior at −0.05 |
|---|---|---|---|---|---|
| their, all pre-event | 0.847 [0.798, 0.894] | 0.801 [0.710, 0.875] | +0.045 [-0.036, +0.136] | -0.025 | yes |
| their, NDBE pre-event | 0.827 [0.768, 0.883] | 0.780 [0.681, 0.879] | +0.047 [-0.040, +0.145] | -0.030 | yes |
| package, all pre-event | 0.847 [0.798, 0.894] | 0.845 [0.766, 0.904] | +0.002 [-0.074, +0.090] | -0.062 | no |
| package, NDBE pre-event | 0.827 [0.768, 0.883] | 0.823 [0.733, 0.901] | +0.004 [-0.071, +0.088] | -0.061 | no |

**Fusion vs histology alone** (Δ AUROC vs L-IMG; max-T adjusted over the three).

| CNV source, population | Model | AUROC | Δ vs L-IMG [95% CI] | p unadjusted | p max-T adjusted |
|---|---|---|---|---|---|
| their, all pre-event | L-EARLY | 0.865 | +0.018 [-0.052, +0.080] | 0.582 | 0.8745 |
| their, all pre-event | L-INTER | 0.832 | -0.015 [-0.083, +0.050] | 0.686 | 0.92 |
| their, all pre-event | L-LATE | 0.889 | +0.042 [+0.002, +0.078] | 0.048 | 0.066 |
| their, NDBE pre-event | L-EARLY | 0.850 | +0.023 [-0.046, +0.091] | 0.455 | 0.808 |
| their, NDBE pre-event | L-INTER | 0.833 | +0.006 [-0.057, +0.069] | 0.796 | 0.9955 |
| their, NDBE pre-event | L-LATE | 0.867 | +0.040 [-0.002, +0.083] | 0.063 | 0.1345 |
| package, all pre-event | L-EARLY | 0.885 | +0.038 [-0.022, +0.093] | 0.194 | 0.2885 |
| package, all pre-event | L-INTER | 0.871 | +0.024 [-0.036, +0.079] | 0.449 | 0.6265 |
| package, all pre-event | L-LATE | 0.903 | +0.056 [+0.018, +0.093] | 0.003 | 0.01 |
| package, NDBE pre-event | L-EARLY | 0.863 | +0.035 [-0.023, +0.091] | 0.223 | 0.403 |
| package, NDBE pre-event | L-INTER | 0.871 | +0.043 [-0.016, +0.101] | 0.144 | 0.2505 |
| package, NDBE pre-event | L-LATE | 0.879 | +0.052 [+0.012, +0.091] | 0.009 | 0.0225 |

### 2–3. Strategies

**their, all pre-event** (571 samples, 75 patients; 161 progressor samples from 32 patients).

| Strategy | Sensitivity [95% CI] | Specificity [95% CI] | Progressor samples missed | Progressor patients with ≥ 1 / all samples missed | Δ sens vs A | Δ spec vs A | Δ sens vs B (one-sided 95% lower) | Δ spec vs B |
|---|---|---|---|---|---|---|---|---|
| Triage, L-LATE in middle band | 0.863 [0.774, 0.942] | 0.734 [0.667, 0.802] | 22 | 9 / 1 | +0.081 [-0.008, +0.178] | +0.144 [+0.029, +0.256] | +0.062 [+0.011, +0.116] (0.020) | -0.051 [-0.092, -0.008] |
| Triage, L-CNV in middle band | 0.857 [0.762, 0.940] | 0.717 [0.639, 0.795] | 23 | 9 / 2 | +0.075 [-0.011, +0.165] | +0.127 [+0.048, +0.205] | +0.056 [+0.000, +0.115] (0.012) | -0.068 [-0.118, -0.013] |
| (A) sequence everyone, L-CNV | 0.783 [0.651, 0.888] | 0.590 [0.469, 0.722] | 35 | 13 / 4 | — | — | -0.019 [-0.121, +0.079] (-0.105) | -0.195 [-0.295, -0.092] |
| (B) sequence everyone, L-LATE | 0.801 [0.697, 0.893] | 0.785 [0.714, 0.850] | 32 | 15 / 2 | +0.019 [-0.079, +0.121] | +0.195 [+0.092, +0.295] | — | — |
| (C) H&E only, L-IMG | 0.789 [0.703, 0.875] | 0.754 [0.693, 0.811] | 34 | 15 / 1 | +0.006 [-0.128, +0.150] | +0.163 [+0.021, +0.302] | -0.012 [-0.085, +0.073] (-0.073) | -0.032 [-0.093, +0.038] |

| Band | All samples [95% CI] | Progressor samples | Non-progressor samples |
|---|---|---|---|
| Low (cleared) | 30.9% [24.9%, 36.6%] | 6.6% | 40.5% |
| Middle (sequenced) | 45.8% [40.8%, 50.4%] | 36.0% | 49.7% |
| High (flagged) | 23.2% [17.5%, 29.9%] | 57.4% | 9.8% |

Folds without a middle band: 0/100; t_seq fallbacks (< 5 training middle-band cases): L-LATE 0/100, L-CNV 0/100. Cut-offs, median (range): t_low 0.042 (0.005–0.109), c* 0.589 (0.489–0.725), t_seq L-LATE 0.233, t_seq L-CNV 0.214.

**their, NDBE pre-event** (438 samples, 71 patients; 104 progressor samples from 28 patients).

| Strategy | Sensitivity [95% CI] | Specificity [95% CI] | Progressor samples missed | Progressor patients with ≥ 1 / all samples missed | Δ sens vs A | Δ spec vs A | Δ sens vs B (one-sided 95% lower) | Δ spec vs B |
|---|---|---|---|---|---|---|---|---|
| Triage, L-LATE in middle band | 0.856 [0.742, 0.955] | 0.728 [0.646, 0.798] | 15 | 7 / 1 | +0.058 [-0.033, +0.158] | +0.168 [+0.066, +0.278] | +0.067 [+0.013, +0.128] (0.021) | -0.006 [-0.049, +0.042] |
| Triage, L-CNV in middle band | 0.856 [0.735, 0.959] | 0.695 [0.603, 0.778] | 15 | 7 / 2 | +0.058 [-0.013, +0.141] | +0.135 [+0.050, +0.225] | +0.067 [+0.000, +0.141] (0.010) | -0.039 [-0.090, +0.012] |
| (A) sequence everyone, L-CNV | 0.798 [0.652, 0.931] | 0.560 [0.430, 0.688] | 21 | 8 / 3 | — | — | +0.010 [-0.111, +0.122] (-0.089) | -0.174 [-0.273, -0.082] |
| (B) sequence everyone, L-LATE | 0.788 [0.667, 0.900] | 0.734 [0.644, 0.813] | 22 | 10 / 1 | -0.010 [-0.122, +0.111] | +0.174 [+0.082, +0.273] | — | — |
| (C) H&E only, L-IMG | 0.779 [0.689, 0.873] | 0.710 [0.643, 0.768] | 23 | 13 / 1 | -0.019 [-0.165, +0.137] | +0.150 [+0.016, +0.291] | -0.010 [-0.105, +0.076] (-0.090) | -0.024 [-0.102, +0.067] |

| Band | All samples [95% CI] | Progressor samples | Non-progressor samples |
|---|---|---|---|
| Low (cleared) | 30.7% [24.5%, 36.5%] | 6.7% | 38.1% |
| Middle (sequenced) | 49.1% [44.1%, 53.9%] | 40.8% | 51.7% |
| High (flagged) | 20.2% [15.2%, 26.4%] | 52.5% | 10.2% |

Folds without a middle band: 0/100; t_seq fallbacks (< 5 training middle-band cases): L-LATE 0/100, L-CNV 0/100. Cut-offs, median (range): t_low 0.035 (0.003–0.104), c* 0.565 (0.475–0.737), t_seq L-LATE 0.219, t_seq L-CNV 0.197.

**package, all pre-event** (571 samples, 75 patients; 161 progressor samples from 32 patients).

| Strategy | Sensitivity [95% CI] | Specificity [95% CI] | Progressor samples missed | Progressor patients with ≥ 1 / all samples missed | Δ sens vs A | Δ spec vs A | Δ sens vs B (one-sided 95% lower) | Δ spec vs B |
|---|---|---|---|---|---|---|---|---|
| Triage, L-LATE in middle band | 0.863 [0.779, 0.945] | 0.763 [0.690, 0.824] | 22 | 8 / 1 | +0.025 [-0.068, +0.124] | +0.063 [-0.021, +0.161] | +0.031 [-0.013, +0.090] (-0.006) | -0.056 [-0.099, -0.009] |
| Triage, L-CNV in middle band | 0.882 [0.806, 0.949] | 0.778 [0.693, 0.846] | 19 | 8 / 1 | +0.043 [-0.034, +0.129] | +0.078 [+0.006, +0.163] | +0.050 [+0.006, +0.098] (0.012) | -0.041 [-0.083, +0.000] |
| (A) sequence everyone, L-CNV | 0.839 [0.745, 0.916] | 0.700 [0.564, 0.810] | 26 | 13 / 1 | — | — | +0.006 [-0.098, +0.111] (-0.079) | -0.120 [-0.204, -0.048] |
| (B) sequence everyone, L-LATE | 0.832 [0.728, 0.924] | 0.820 [0.741, 0.885] | 27 | 10 / 1 | -0.006 [-0.111, +0.098] | +0.120 [+0.048, +0.204] | — | — |
| (C) H&E only, L-IMG | 0.789 [0.703, 0.875] | 0.754 [0.693, 0.811] | 34 | 15 / 1 | -0.050 [-0.163, +0.078] | +0.054 [-0.063, +0.189] | -0.043 [-0.109, +0.022] (-0.099) | -0.066 [-0.131, +0.016] |

| Band | All samples [95% CI] | Progressor samples | Non-progressor samples |
|---|---|---|---|
| Low (cleared) | 30.9% [24.9%, 36.6%] | 6.6% | 40.5% |
| Middle (sequenced) | 45.8% [40.8%, 50.4%] | 36.0% | 49.7% |
| High (flagged) | 23.2% [17.5%, 29.9%] | 57.4% | 9.8% |

Folds without a middle band: 0/100; t_seq fallbacks (< 5 training middle-band cases): L-LATE 0/100, L-CNV 0/100. Cut-offs, median (range): t_low 0.042 (0.005–0.109), c* 0.589 (0.489–0.725), t_seq L-LATE 0.237, t_seq L-CNV 0.227.

**package, NDBE pre-event** (438 samples, 71 patients; 104 progressor samples from 28 patients).

| Strategy | Sensitivity [95% CI] | Specificity [95% CI] | Progressor samples missed | Progressor patients with ≥ 1 / all samples missed | Δ sens vs A | Δ spec vs A | Δ sens vs B (one-sided 95% lower) | Δ spec vs B |
|---|---|---|---|---|---|---|---|---|
| Triage, L-LATE in middle band | 0.846 [0.734, 0.950] | 0.737 [0.657, 0.810] | 16 | 7 / 1 | +0.038 [-0.064, +0.139] | +0.051 [-0.037, +0.153] | +0.029 [-0.014, +0.078] (-0.010) | -0.024 [-0.066, +0.025] |
| Triage, L-CNV in middle band | 0.856 [0.755, 0.949] | 0.751 [0.653, 0.838] | 15 | 7 / 1 | +0.048 [-0.034, +0.143] | +0.066 [-0.018, +0.153] | +0.038 [+0.000, +0.079] (0.000) | -0.009 [-0.053, +0.033] |
| (A) sequence everyone, L-CNV | 0.808 [0.700, 0.905] | 0.686 [0.557, 0.803] | 20 | 11 / 1 | — | — | -0.010 [-0.116, +0.092] (-0.094) | -0.075 [-0.148, -0.012] |
| (B) sequence everyone, L-LATE | 0.817 [0.703, 0.932] | 0.760 [0.667, 0.845] | 19 | 7 / 1 | +0.010 [-0.092, +0.116] | +0.075 [+0.012, +0.148] | — | — |
| (C) H&E only, L-IMG | 0.779 [0.689, 0.873] | 0.710 [0.643, 0.768] | 23 | 13 / 1 | -0.029 [-0.146, +0.092] | +0.024 [-0.099, +0.167] | -0.038 [-0.124, +0.035] (-0.108) | -0.051 [-0.133, +0.044] |

| Band | All samples [95% CI] | Progressor samples | Non-progressor samples |
|---|---|---|---|
| Low (cleared) | 30.7% [24.5%, 36.5%] | 6.7% | 38.1% |
| Middle (sequenced) | 49.1% [44.1%, 53.9%] | 40.8% | 51.7% |
| High (flagged) | 20.2% [15.2%, 26.4%] | 52.5% | 10.2% |

Folds without a middle band: 0/100; t_seq fallbacks (< 5 training middle-band cases): L-LATE 0/100, L-CNV 0/100. Cut-offs, median (range): t_low 0.035 (0.003–0.104), c* 0.565 (0.475–0.737), t_seq L-LATE 0.219, t_seq L-CNV 0.198.

**Middle band only: does CNV discriminate where histology is uncertain?** (fold-stratified AUROC on held-out middle-band samples, mean over repeats).

| CNV source, population | L-IMG | L-CNV | L-LATE | Δ L-CNV − L-IMG [95% CI], p | Δ L-LATE − L-IMG [95% CI], p |
|---|---|---|---|---|---|
| their, all pre-event | 0.650 [0.599, 0.710] | 0.786 [0.677, 0.872] | 0.807 | +0.136 [+0.011, +0.238], 0.036 | +0.157 [+0.062, +0.238], 0.003 |
| their, NDBE pre-event | 0.665 [0.609, 0.722] | 0.771 [0.662, 0.878] | 0.797 | +0.106 [-0.012, +0.226], 0.077 | +0.132 [+0.040, +0.225], 0.004 |
| package, all pre-event | 0.650 [0.599, 0.710] | 0.841 [0.741, 0.912] | 0.844 | +0.191 [+0.076, +0.276], 0.003 | +0.194 [+0.108, +0.267], < 0.0005 |
| package, NDBE pre-event | 0.665 [0.609, 0.722] | 0.807 [0.702, 0.903] | 0.818 | +0.141 [+0.035, +0.234], 0.012 | +0.153 [+0.076, +0.228], < 0.0005 |

**Band characteristics** (pooled over sample × repeat assignments, each 1/10; their matrix, all pre-event samples; bands depend on L-IMG only).

| Band | Samples (sum of 1/10) | Progressor share | Raw cx, mean (SD) | Tissue tiles, mean (SD); median | NDBE / ID / LGD | Scanner C13210 share |
|---|---|---|---|---|---|---|
| Low (all pre-event) | 176.7 | 0.060 | 23.7 (6.1) | 407 (663); 239 | 0.838 / 0.089 / 0.072 | 0.243 |
| Middle (all pre-event) | 261.8 | 0.222 | 24.7 (7.2) | 553 (824); 264 | 0.783 / 0.138 / 0.079 | 0.249 |
| High (all pre-event) | 132.5 | 0.697 | 27.1 (10.8) | 642 (987); 250 | 0.640 / 0.106 / 0.254 | 0.232 |
| Low (NDBE pre-event) | 134.4 | 0.052 | 23.5 (6.2) | 418 (688); 238 | 1.000 / 0.000 / 0.000 | 0.223 |
| Middle (NDBE pre-event) | 215.0 | 0.197 | 24.6 (7.2) | 550 (820); 264 | 1.000 / 0.000 / 0.000 | 0.221 |
| High (NDBE pre-event) | 88.6 | 0.616 | 27.4 (11.0) | 563 (758); 246 | 1.000 / 0.000 / 0.000 | 0.198 |

### 4. Prevalence projection (not observed)

Share of samples in each band if progressor samples made up 2%, 5% or 10% of samples, holding each class's band rates fixed (triage bands depend on L-IMG only).

| CNV source, population | Prevalence | Sequenced (middle) [95% CI] | Cleared (low) | Flagged (high) |
|---|---|---|---|---|
| their, all pre-event | 2.0% | 49.4% [44.2%, 54.6%] | 39.8% | 10.7% |
| their, all pre-event | 5.0% | 49.0% [43.9%, 54.0%] | 38.8% | 12.2% |
| their, all pre-event | 10.0% | 48.3% [43.5%, 53.1%] | 37.1% | 14.5% |
| their, all pre-event | 28.2% (observed) | 45.8% [41.3%, 50.2%] | 30.9% | 23.2% |
| their, NDBE pre-event | 2.0% | 51.5% [46.3%, 56.6%] | 37.5% | 11.0% |
| their, NDBE pre-event | 5.0% | 51.1% [46.2%, 56.2%] | 36.6% | 12.3% |
| their, NDBE pre-event | 10.0% | 50.6% [45.7%, 55.5%] | 35.0% | 14.4% |
| their, NDBE pre-event | 23.7% (observed) | 49.1% [44.3%, 53.7%] | 30.7% | 20.2% |

### Figure

`13_F_triage`: (a) sample flow for their matrix, all pre-event samples, triage with L-LATE; a sample's band is its most frequent band over the 10 repeats (ties → middle), which equals its band in all 10 repeats for 35.0% of samples; (b) projected share sequenced against prevalence.

### Deviations and caveats

- None in method. The `primary_criterion` block is computed in every task, but the criterion applies only to their matrix, all pre-event samples; the other tasks' blocks are not used.
- Middle-band AUROC of L-IMG is computed on samples selected for intermediate L-IMG scores, so it is range-restricted by construction; the comparison answers whether CNV ranks those samples better, not whether CNV is better overall.
- Matched case–control cohort (about 28% progressor samples); sensitivities and specificities are per sample, the label is patient status shared by all of a patient's samples, and absolute numbers sequenced at other prevalences are projections.
- The ≥ 6-of-10 vote and the band shares use the same stored predictions; bootstrap CIs hold calls fixed and resample patients (thresholds are not re-chosen per draw), so they do not include threshold-selection variability.
- Triage bands are set by L-IMG only, so they are the same for both CNV sources; only the middle-band call changes.


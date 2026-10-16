# Review round 6: analyses requested by reviewers (excluding ACE-B)

Status: PRE-SPECIFICATION (written 2026-10-16). Nothing below has been run. Results are appended under the line at the end in a later commit; this section is not edited afterwards.

Purpose: answer the round-6 review of manuscript v6 (Nature Medicine referee and four full-context reviewers; synthesis outside the repository). All items re-score stored predictions or read stored sample-sheet and hospital-record fields. No model is refitted, no feature changes, no frozen bundle changes, and no ACE-B file is read.

**Ground rules** as in `docs/paper_review_round4_analyses.md` (45b77bf).

**Population and conventions.** Unchanged:
- Primary population: 571 pre-event samples of the 676 samples from 80 patients of the Killcoyne discovery cohort with a matched H&E slide.
- The shipped matrix is the primary copy-number source. Per-sample re-segmented features (R36) are reported where stated.
- Single model = per-repeat calls averaged over 10 repeats. The 10-model vote is ≥ 6 of 10.
- Patient bootstrap: 2,000 draws, `RandomState(0)`, resampled patients keep their folds.
- One-sided 95% bound = 5th percentile. Two-sided 95% limits are also reported.
- Triage comparisons give Δ sensitivity (with bound), Δ specificity and share sequenced against (B) and B\* (training-matched).

## R37. p53 immunohistochemistry as a current-standard comparator

Source: the `P53 IHC` field of the analysed-sample table (0 = wild-type pattern, 1 = aberrant, blank = not done).

- **(a) Availability.** p53 available, by class, among the 571 pre-event samples. Grade distribution of samples with and without p53. Fisher test of availability against status.
- **(b) p53 alone.** On pre-event samples with p53, sensitivity and specificity of "flag if p53 aberrant", per sample, per endoscopy and per patient, with exact CIs.
- **(c) Current care with p53.** "Flag if grade ID or LGD, or p53 aberrant" (D+p53), on the same samples and levels.
- **(d) Triage with p53.**
  - "Flag if triage positive or p53 aberrant" (single model, and voted).
  - Restricted to samples with p53, the triage alone against (D), (D+p53) and p53 alone, paired, with patient-bootstrap CIs on Δ sensitivity and Δ specificity.
- **(e) Does p53 add to the triage?** Among samples the triage clears (low band), how many progressor samples are p53-aberrant, and how many non-progressor samples.
- **(f) Sensitivity analysis.** Treat missing p53 as wild-type and report (b)–(d) on all 571.

## R38. Label sensitivity analyses

All re-score stored predictions on subsets, with fold-stratified AUROC and the patient bootstrap on the subset.

- **(a) Sheet exclusion flag.** Exclude samples carrying Killcoyne's `excluded` flag. Also report it with `remove` and `inconsistency` flags excluded.
- **(b) Short follow-up.** Exclude non-progressor samples taken less than 1 year before the patient's last sequenced endoscopy; separately, less than 2 years.
- **(c) Possible later HGD.** Exclude non-progressor patients with any later HGD+ report in the stored hospital-record check (`results/paper_final/final_checks.json` K1 and the row-level source it was built from, on the cluster). Report how many of the 43 are affected; if they cannot be identified, report "not identifiable".
- **(d)** (a), (b at 1 year) and (c) together.
- **Reported for each:**
  - the triage against B\* and against (B) (single model);
  - the triage's sensitivity, specificity and share sequenced;
  - Δ L-IMG − L-CNV (shipped matrix) with its bound;
  - the number of samples and patients by class.

## R39. The 10-model ensemble as the frozen rule

The 10-model vote is a candidate stabilised rule.
- Repeat the R33 Claim T table (triage against B\*, same rows where computable from stored voted calls) using voted calls for both triage and comparator.
- Add the vote-pivotal share sequenced per row.
- Report the between-repeat stability of a voted call:
  - the share of samples whose voted call is unanimous (10/10) or near-unanimous (≥ 8/10);
  - the same by modal band.

Comparing this table with R33 shows whether the ensemble is more robust than the single model.

## R40. Paired comparison of copy-number versions

Paired patient-bootstrap ΔAUROC (fold-stratified, same draws) between L-CNV versions on pre-event samples:
- the shipped matrix;
- the joint package rebuild;
- past-only;
- per-sample.

Report all six pairwise Δ with two-sided CIs and p-values, Holm-adjusted over the six.

**Sampling intensity.** The median per-sample correlation between joint and per-sample final features, by number of the patient's samples segmented together (tertiles), and by class within tertile. This tests whether the class difference in Fig. 5c follows the number of samples per patient.

## R41. One random biopsy per endoscopy

A cheap comparator at a similar sequencing share.
- **Rule.** At each pre-event endoscopy, sequence one sample chosen at random (100 seeds) and call the endoscopy by that sample's L-LATE result at (B)'s fold threshold.
- **Reported:**
  - endoscopy- and patient-level sensitivity and specificity, mean and 2.5–97.5% range over seeds;
  - the share of samples sequenced.
- **Comparison.** Against the triage at endoscopy and patient level (single model). Paired over seeds and patient bootstrap: Δ endoscopy sensitivity and specificity.
- **Variant.** One random biopsy sequenced, and the rest called by the H&E model.

## Scripts and running

- Scripts: `scripts/paper_plan/rv6_round6.py` (TASK = r37 … r41) and `rv6_render.py`.
- Running: Slurm via `scripts/cluster/campaign.sh`, prefix rv6. Never on the login node.
- Outputs: aggregates to `results/paper_final/review_round6/`.

---

## Results

Rendered by `scripts/paper_plan/rv6_render.py` from `results/paper_final/review_round6/` (aggregate results 05d0613).

| Item | Status |
|---|---|
| R37 p53 immunohistochemistry | DONE |
| R38 label sensitivity analyses | DONE (6 subsets) |
| R39 the 10-model vote as the frozen rule | DONE (28 rows) |
| R40 paired comparison of copy-number versions | DONE |
| R41 one random biopsy per endoscopy | DONE |

### R37. p53 immunohistochemistry as a current-standard comparator

**(a) Availability.** p53 available for 450 of 571 pre-event samples (79%): progressor 111 with / 50 without, non-progressor 339 / 71 (Fisher p = 0.001). Aberrant among those with a result: 17 progressor and 1 non-progressor samples. Patients with any p53 result: 31 progressor, 40 non-progressor.

| Grade | Progressor with p53 | Progressor without | Non-progressor with p53 | Non-progressor without |
|---|---|---|---|---|
| NDBE | 72 | 32 | 270 | 64 |
| ID | 10 | 5 | 48 | 3 |
| LGD | 29 | 13 | 21 | 4 |

**(b)–(d) On the 450 pre-event samples with p53** (111 progressor; 71 patients, 220 endoscopies). Exact (Clopper–Pearson) CIs for deterministic rules, patient-bootstrap CIs for single-model rules. Triage share sequenced on these samples 0.452.

| Rule | Sample sens / spec | Endoscopy sens / spec | Patient sens / spec |
|---|---|---|---|
| p53 alone (b) | 0.153 [0.092, 0.234] / 0.997 [0.984, 1.000] | 0.210 [0.117, 0.332] / 0.994 [0.965, 1.000] | 0.387 [0.218, 0.578] / 0.975 [0.868, 0.999] |
| (D) grade ID or LGD | 0.351 [0.263, 0.448] / 0.796 [0.750, 0.838] | 0.339 [0.223, 0.470] / 0.734 [0.658, 0.801] | 0.484 [0.302, 0.669] / 0.450 [0.293, 0.615] |
| (D) + p53 (c) | 0.432 [0.339, 0.530] / 0.794 [0.746, 0.835] | 0.419 [0.295, 0.552] / 0.728 [0.651, 0.796] | 0.613 [0.422, 0.782] / 0.450 [0.293, 0.615] |
| triage, single model | 0.871 [0.809, 0.927] / 0.716 [0.651, 0.781] | 0.902 [0.842, 0.955] / 0.572 [0.487, 0.661] | 0.961 [0.896, 0.997] / 0.282 [0.167, 0.400] |
| triage or p53, single model (d) | 0.881 [0.823, 0.936] / 0.713 [0.649, 0.779] | 0.910 [0.853, 0.960] / 0.569 [0.484, 0.658] | 0.961 [0.896, 0.997] / 0.282 [0.167, 0.400] |
| triage, voted | 0.874 [0.797, 0.929] / 0.758 [0.709, 0.803] | 0.903 [0.801, 0.964] / 0.620 [0.540, 0.696] | 0.968 [0.833, 0.999] / 0.325 [0.186, 0.491] |
| triage or p53, voted (d) | 0.874 [0.797, 0.929] / 0.755 [0.706, 0.800] | 0.903 [0.801, 0.964] / 0.614 [0.533, 0.690] | 0.968 [0.833, 0.999] / 0.325 [0.186, 0.491] |
| B\* training-matched, single model | 0.882 [0.821, 0.939] / 0.683 [0.600, 0.764] | 0.898 [0.836, 0.952] / 0.558 [0.461, 0.657] | 0.965 [0.897, 1.000] / 0.295 [0.171, 0.421] |

Paired comparisons, single model unless stated:

| Paired difference (sample level) | Δ sensitivity [95% CI] | One-sided bound | Δ specificity [95% CI] |
|---|---|---|---|
| triage − (D) | +0.520 [+0.393, +0.652] | +0.413 | -0.081 [-0.163, +0.003] |
| triage − (D+p53) | +0.439 [+0.308, +0.568] | +0.328 | -0.078 [-0.163, +0.011] |
| triage − p53 alone | +0.718 [+0.633, +0.804] | +0.647 | -0.281 [-0.348, -0.215] |
| triage (voted) − (D+p53) | +0.441 [+0.299, +0.573] | +0.326 | -0.035 [-0.130, +0.067] |
| triage-or-p53 − (D+p53) | +0.449 [+0.317, +0.578] | +0.338 | -0.080 [-0.163, +0.003] |
| triage-or-p53 − triage | +0.010 [+0.001, +0.021] | +0.003 | -0.003 [-0.008, +0.000] |
| triage − B\* | -0.011 [-0.028, +0.004] | -0.025 | +0.033 [-0.006, +0.076] |

**(e) p53 among samples the triage clears.** Modal low band: 178 samples, 150 with p53; p53-aberrant 0 of 3 progressor and 1 of 147 non-progressor samples. Low band in all 10 repeats: 0 of 1 progressor, 0 of 52 non-progressor. Per-repeat mean p53-aberrant samples in the low band: progressor 0.6, non-progressor 0.7.

**(f) Missing p53 as wild-type, all 571 samples.**

| Rule | Sample sens / spec | Endoscopy sens / spec | Patient sens / spec |
|---|---|---|---|
| p53 alone (b) | 0.106 [0.063, 0.164] / 0.998 [0.986, 1.000] | 0.148 [0.081, 0.239] / 0.995 [0.972, 1.000] | 0.375 [0.211, 0.563] / 0.977 [0.877, 0.999] |
| (D) grade ID or LGD | 0.354 [0.280, 0.433] / 0.815 [0.774, 0.851] | 0.364 [0.264, 0.473] / 0.760 [0.695, 0.817] | 0.531 [0.347, 0.709] / 0.419 [0.270, 0.579] |
| (D) + p53 (c) | 0.410 [0.333, 0.490] / 0.812 [0.771, 0.849] | 0.420 [0.316, 0.530] / 0.755 [0.689, 0.813] | 0.656 [0.468, 0.814] / 0.419 [0.270, 0.579] |
| triage, single model | 0.865 [0.791, 0.926] / 0.697 [0.633, 0.762] | 0.909 [0.865, 0.952] / 0.549 [0.460, 0.637] | 0.972 [0.928, 1.000] / 0.256 [0.156, 0.368] |
| triage or p53, single model (d) | 0.871 [0.797, 0.933] / 0.695 [0.631, 0.760] | 0.915 [0.872, 0.955] / 0.546 [0.458, 0.635] | 0.972 [0.928, 1.000] / 0.256 [0.156, 0.368] |
| triage, voted | 0.863 [0.800, 0.912] / 0.734 [0.689, 0.776] | 0.898 [0.815, 0.952] / 0.590 [0.518, 0.659] | 0.969 [0.838, 0.999] / 0.302 [0.172, 0.461] |
| triage or p53, voted (d) | 0.863 [0.800, 0.912] / 0.732 [0.686, 0.774] | 0.898 [0.815, 0.952] / 0.585 [0.513, 0.654] | 0.969 [0.838, 0.999] / 0.302 [0.172, 0.461] |
| B\* training-matched, single model | 0.881 [0.801, 0.944] / 0.665 [0.585, 0.745] | 0.923 [0.873, 0.962] / 0.530 [0.431, 0.629] | 0.975 [0.929, 1.000] / 0.263 [0.152, 0.381] |

| Paired difference (sample level) | Δ sensitivity [95% CI] | One-sided bound | Δ specificity [95% CI] |
|---|---|---|---|
| triage − (D) | +0.511 [+0.396, +0.637] | +0.416 | -0.118 [-0.204, -0.039] |
| triage − (D+p53) | +0.455 [+0.346, +0.576] | +0.359 | -0.115 [-0.204, -0.034] |
| triage − p53 alone | +0.759 [+0.677, +0.833] | +0.694 | -0.300 [-0.366, -0.236] |
| triage (voted) − (D+p53) | +0.453 [+0.333, +0.585] | +0.351 | -0.078 [-0.175, +0.015] |
| triage-or-p53 − (D+p53) | +0.461 [+0.351, +0.584] | +0.366 | -0.117 [-0.204, -0.039] |
| triage-or-p53 − triage | +0.007 [+0.001, +0.015] | +0.002 | -0.002 [-0.006, +0.000] |
| triage − B\* | -0.016 [-0.036, +0.001] | -0.032 | +0.032 [-0.002, +0.071] |

p53 is available for 79% of samples and flags few; the triage keeps its sensitivity advantage over current care with p53 (+0.439, bound +0.328), and adding p53 to the triage changes sensitivity by +0.010 at a specificity cost of 0.003.

### R38. Label sensitivity analyses

Stored calls re-evaluated on each subset (single model; patient bootstrap on the subset). Later HGD+: of the 43 non-progressor patients, 43 are in the hospital-record check (0 not identifiable), 1 with a later HGD+ report and 9 with later LGD+.

| Subset | Samples (progressor) / patients | Triage sens / spec | Share | Δ sens vs B\* [95% CI] | Bound | Within | Δ spec | Δ sens vs (B) (bound) | Δ L-IMG − L-CNV (bound) | Within |
|---|---|---|---|---|---|---|---|---|---|---|
| primary (R33 row 1, for reference) | 571 (161) / 75 | 0.865 / 0.697 | 0.458 | -0.016 [-0.036, +0.001] | -0.032 | yes | +0.032 | +0.033 (+0.011) | +0.045 (-0.025) | yes |
| (a) 'excluded' flag removed | 514 (125) / 71 | 0.852 / 0.701 | 0.468 | -0.011 [-0.030, +0.007] | -0.027 | yes | +0.030 | +0.043 (+0.023) | +0.048 (-0.029) | yes |
| (a) 'excluded', 'remove' and 'inconsistency' flags removed | 507 (118) / 69 | 0.843 / 0.701 | 0.473 | -0.012 [-0.030, +0.007] | -0.027 | yes | +0.030 | +0.046 (+0.024) | +0.052 (-0.031) | yes |
| (b) non-progressor samples < 1 year before the last sequenced endoscopy removed | 478 (161) / 75 | 0.865 / 0.686 | 0.444 | -0.016 [-0.036, +0.001] | -0.032 | yes | +0.035 | +0.033 (+0.011) | +0.035 (-0.037) | yes |
| (b) non-progressor samples < 2 years before the last sequenced endoscopy removed | 456 (161) / 75 | 0.865 / 0.694 | 0.448 | -0.016 [-0.036, +0.001] | -0.032 | yes | +0.038 | +0.033 (+0.011) | +0.032 (-0.039) | yes |
| (c) non-progressor patients with a later HGD+ report removed | 564 (161) / 74 | 0.865 / 0.697 | 0.460 | -0.016 [-0.036, +0.001] | -0.033 | yes | +0.032 | +0.033 (+0.011) | +0.047 (-0.020) | yes |
| (d) (a) + (b, 1 year) + (c) | 415 (125) / 70 | 0.852 / 0.687 | 0.455 | -0.011 [-0.029, +0.007] | -0.027 | yes | +0.033 | +0.043 (+0.021) | +0.040 (-0.036) | yes |

Triage versus B\* stays within the margin in 6 of 6 label subsets and the H&E-versus-copy-number bound in 6 of 6; the direction of every difference is unchanged by the label exclusions.

### R39. The 10-model ensemble as the frozen rule

Voted (≥ 6 of 10) triage against voted B\* (training-matched), same rows as R33 Claim T. "Pivotal" = share of samples whose voted call depends on the middle-band calls (the vote's sequencing need). The single-model (R33) Δ and bound are repeated for comparison.

| # | Analysis | Δ sensitivity voted [95% CI] | Bound | Within | Δ spec | Share | Pivotal | Cap | Single-model Δ (bound) | Within |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | primary: all pre-event samples | -0.006 [-0.051, +0.034] | -0.044 | yes | +0.034 | 0.458 | 0.471 | yes | -0.016 (-0.032) | yes |
| 2 | NDBE pre-event samples | +0.010 [-0.023, +0.044] | -0.018 | yes | +0.057 | 0.491 | 0.500 | yes | -0.014 (-0.034) | yes |
| 3 | package features | -0.019 [-0.046, +0.000] | -0.040 | yes | +0.034 | 0.458 | 0.471 | yes | -0.007 (-0.020) | yes |
| 4 | pre-event-only training (F1) | +0.000 [-0.025, +0.025] | -0.021 | yes | +0.039 | 0.443 | 0.447 | yes | -0.009 (-0.021) | yes |
| 5 | patients never dysplastic before the event | +0.018 [+0.000, +0.054] | +0.000 | yes | +0.021 | 0.441 | 0.452 | yes | -0.014 (-0.035) | yes |
| 6 | H-optimus-0 gate (F5) | -0.006 [-0.023, +0.000] | -0.019 | yes | -0.010 | 0.668 | 0.683 | yes | -0.008 (-0.022) | yes |
| 7 | excluding progressor samples within 1 year | +0.000 [-0.043, +0.040] | -0.035 | yes | +0.034 | 0.469 | 0.483 | yes | -0.006 (-0.019) | yes |
| 8 | cut-off grid cell: t_low 90% training sensitivity, t_high 85% training specificity | -0.043 [-0.085, +0.000] | -0.077 | no | +0.061 | 0.298 | 0.289 | yes | -0.039 (-0.064) | no |
| 8 | cut-off grid cell: t_low 90% training sensitivity, t_high 90% training specificity | -0.037 [-0.075, +0.000] | -0.069 | no | +0.066 | 0.342 | 0.331 | yes | -0.039 (-0.063) | no |
| 8 | cut-off grid cell: t_low 90% training sensitivity, t_high 95% training specificity | -0.043 [-0.080, -0.006] | -0.075 | no | +0.051 | 0.401 | 0.385 | yes | -0.031 (-0.053) | no |
| 8 | cut-off grid cell: t_low 95% training sensitivity, t_high 85% training specificity | -0.006 [-0.051, +0.033] | -0.043 | yes | +0.044 | 0.414 | 0.429 | yes | -0.016 (-0.033) | yes |
| 8 | cut-off grid cell: t_low 95% training sensitivity, t_high 90% training specificity (primary cell) | -0.006 [-0.051, +0.034] | -0.044 | yes | +0.034 | 0.458 | 0.471 | yes | -0.016 (-0.032) | yes |
| 8 | cut-off grid cell: t_low 95% training sensitivity, t_high 95% training specificity | +0.006 [-0.027, +0.037] | -0.021 | yes | +0.041 | 0.517 | 0.525 | yes | -0.016 (-0.030) | yes |
| 8 | cut-off grid cell: t_low 98% training sensitivity, t_high 85% training specificity | +0.006 [-0.014, +0.028] | -0.011 | yes | +0.024 | 0.542 | 0.562 | yes | -0.002 (-0.012) | yes |
| 8 | cut-off grid cell: t_low 98% training sensitivity, t_high 90% training specificity | +0.000 [-0.016, +0.019] | -0.014 | yes | +0.015 | 0.586 | 0.604 | yes | -0.001 (-0.010) | yes |
| 8 | cut-off grid cell: t_low 98% training sensitivity, t_high 95% training specificity | +0.006 [-0.014, +0.027] | -0.011 | yes | +0.017 | 0.645 | 0.658 | yes | -0.002 (-0.011) | yes |
| 9 | tissue stratum: < 256 tissue tiles (R32a) | -0.014 [-0.045, +0.000] | -0.039 | yes | +0.036 | 0.423 | 0.437 | yes | -0.008 (-0.022) | yes |
| 9 | tissue stratum: >= 256 tissue tiles (R32a) | +0.000 [-0.086, +0.069] | -0.069 | no | +0.032 | 0.496 | 0.507 | yes | -0.022 (-0.050) | no |
| 10 | tissue-adjusted gate (R32b) | -0.019 [-0.050, +0.009] | -0.045 | yes | +0.005 | 0.577 | 0.595 | yes | -0.012 (-0.028) | yes |
| 11 | lambda by deviance (B5) | -0.006 [-0.032, +0.014] | -0.027 | yes | +0.000 | 0.526 | 0.552 | yes | -0.006 (-0.020) | yes |
| 12 | patient-weighted (R34) | +0.001 [-0.023, +0.025] | -0.019 | yes | +0.022 | 0.432 | 0.452 | yes | -0.015 (-0.030) | yes |
| 13 | earliest pre-event endoscopy per patient (all its samples) | -0.016 [-0.074, +0.038] | -0.064 | no | +0.013 | 0.460 | 0.486 | yes | -0.013 (-0.034) | yes |
| 14 | selection-inclusive (every cut-off re-chosen in each draw) | -0.006 [-0.057, +0.032] | -0.051 | no | +0.034 | 0.458 | 0.471 | yes | -0.016 (-0.038) | yes |
| 15 | evaluation-matched B* | +0.012 [-0.038, +0.061] | -0.030 | yes |  | 0.458 | 0.471 | yes | +0.003 (-0.022) | yes |
| 16 | 10-model vote | not applicable: this table is the voted rule; identical to row 1 | | | | | | | -0.006 (-0.044) | yes |
| 17 | between-repeat variance added | not applicable: the vote pools the repeats; no between-repeat variance | | | | | | | -0.016 (-0.046) | yes |
| 18 | refit bootstrap (F3, 200 draws) | not applicable: one model per draw; no vote | | | | | | | -0.018 (-0.069) | no |
| 19 | per-sample re-segmented copy number (R36) | +0.006 [-0.015, +0.040] | -0.012 | yes | +0.010 | 0.458 | 0.471 | yes | -0.006 (-0.016) | yes |
| 19b | past-only re-segmented copy number (R36, extra row) | +0.006 [-0.013, +0.029] | -0.011 | yes | +0.034 | 0.458 | 0.471 | yes | -0.009 (-0.019) | yes |
| T5 | package features, pre-event-only training (Table 5) | +0.006 [-0.021, +0.035] | -0.016 | yes | +0.059 | 0.443 | 0.447 | yes | -0.005 (-0.013) | yes |
| T5 | earliest pre-event sample per patient (Table 5) | +0.000 [-0.088, +0.088] | -0.069 | no | +0.023 | 0.475 | 0.520 | yes | +0.003 (-0.027) | yes |

Voted: 21 of 28 rows within the margin (single model on the same 28 rows: 24; voted: 21); mean Δ voted -0.005 versus single model -0.012; mean voted CI width 0.071.

**Between-repeat stability of the voted call** (primary): the per-repeat call equals the voted call in all 10 repeats for 62% of samples and in ≥ 8 of 10 for 82% (progressors 71% / 88%, non-progressors 58% / 80%). By modal band: low 78% / 93% (n 178), middle 37% / 67% (n 269), high 93% / 100% (n 124). B\* for reference: 65% / 84%.

The vote's point estimates stay close to the single model's (mean Δ -0.005 versus -0.012) but its intervals are wider: the 4 rows the single model fails also fail voted, and 3 further rows (earliest pre-event endoscopy per patient (all its samples); selection-inclusive (every cut-off re-chosen in each draw); earliest pre-event sample per patient (Table 5)) fall just below the margin; disagreement between repeats concentrates in the middle band (37% unanimous against 78% and 93% in the low and high bands), so the ensemble is not a more robust rule than the single model.

### R40. Paired comparison of copy-number versions

| L-CNV version | Fold-stratified AUROC [95% CI] |
|---|---|
| shipped matrix | 0.801 [+0.710, +0.875] |
| joint package rebuild | 0.845 [+0.766, +0.904] |
| past-only | 0.800 [+0.723, +0.867] |
| per-sample | 0.785 [+0.723, +0.845] |

| Pair | ΔAUROC [95% CI] | p (two-sided) | p (Holm) |
|---|---|---|---|
| shipped matrix − joint package rebuild | -0.044 [-0.115, +0.031] | 0.265 | 1.0 |
| shipped matrix − past-only | +0.002 [-0.065, +0.074] | 0.96 | 1.0 |
| shipped matrix − per-sample | +0.017 [-0.064, +0.088] | 0.671 | 1.0 |
| joint package rebuild − past-only | +0.045 [-0.012, +0.097] | 0.116 | 0.582 |
| joint package rebuild − per-sample | +0.061 [-0.010, +0.121] | 0.097 | 0.582 |
| past-only − per-sample | +0.015 [-0.042, +0.064] | 0.592 | 1.0 |

**Sampling intensity.** Samples segmented together in the joint call: median 10 (IQR 7–12) for progressor and 12 (8–15) for non-progressor pre-event samples. Per-sample correlation of joint versus per-sample final features: median 0.805 (progressor) versus 0.708 (non-progressor), difference +0.097 [+0.048, +0.166]; Spearman ρ of r against the number segmented together -0.160 (progressor -0.061, non-progressor -0.171).

| Tertile of samples segmented together | Range | Progressor n / median r | Non-progressor n / median r | Class difference [95% CI] |
|---|---|---|---|---|
| 1 | 2–8 | 56 / 0.836 | 136 / 0.716 | +0.120 [+0.065, +0.172] |
| 2 | 9–13 | 70 / 0.79 | 139 / 0.729 | +0.061 [-0.056, +0.151] |
| 3 | 14–31 | 35 / 0.769 | 135 / 0.645 | +0.124 [-0.002, +0.283] |

The joint package rebuild has the highest AUROC, but no pairwise difference survives Holm adjustment (smallest Holm p 0.582; joint − per-sample +0.061 [-0.010, +0.121]). Progressor samples are segmented with fewer companions than non-progressor samples, yet the class difference in joint-versus-per-sample agreement is present in every tertile (clearly in the lowest), so it does not follow the number of samples per patient.

### R41. One random biopsy per endoscopy

288 pre-event endoscopies (88 progressor) in 75 patients; one sample per endoscopy sequences 0.504 of samples (triage: 0.458 per repeat, 0.760 in at least one repeat). 100 seeds; single model; mean over seeds with the 2.5–97.5% range over seeds, and the patient-bootstrap CI of the seed mean.

| Level | Rule | Sensitivity, mean (range over seeds) [bootstrap CI] | Specificity, mean (range) [CI] |
|---|---|---|---|
| endoscopy | one random biopsy, L-LATE at (B)'s threshold | 0.827 (0.803 to 0.852) [0.742, 0.901] | 0.740 (0.721 to 0.762) [0.673, 0.805] |
| endoscopy | one random biopsy + the rest by the H&E model (C) | 0.879 (0.874 to 0.885) [0.807, 0.938] | 0.589 (0.575 to 0.604) [0.511, 0.669] |
| endoscopy | triage | 0.909 [0.865, 0.952] | 0.549 [0.460, 0.637] |
| endoscopy | (B), every sample sequenced | 0.876 [0.803, 0.935] | 0.640 [0.552, 0.726] |
| patient | one random biopsy, L-LATE at (B)'s threshold | 0.930 (0.889 to 0.956) [0.862, 0.985] | 0.417 (0.373 to 0.458) [0.298, 0.544] |
| patient | one random biopsy + the rest by the H&E model (C) | 0.965 (0.959 to 0.972) [0.914, 1.000] | 0.240 (0.209 to 0.276) [0.147, 0.351] |
| patient | triage | 0.972 [0.928, 1.000] | 0.256 [0.156, 0.368] |
| patient | (B), every sample sequenced | 0.959 [0.900, 1.000] | 0.337 [0.223, 0.461] |

| Level | Δ rule − triage | Δ sensitivity, mean over seeds (range) [bootstrap CI of the seed mean] | One-sided bound | Δ specificity (range) [CI] |
|---|---|---|---|---|
| endoscopy | one random biopsy | -0.082 (-0.106 to -0.057) [-0.140, -0.035] | -0.131 | +0.191 (+0.172 to +0.213) [+0.150, +0.234] |
| endoscopy | random biopsy + H&E on the rest | -0.030 (-0.035 to -0.024) [-0.073, +0.009] | -0.065 | +0.040 (+0.026 to +0.055) [+0.011, +0.066] |
| patient | one random biopsy | -0.041 (-0.083 to -0.016) [-0.086, -0.008] | -0.078 | +0.161 (+0.117 to +0.202) [+0.112, +0.209] |
| patient | random biopsy + H&E on the rest | -0.007 (-0.013 to +0.000) [-0.038, +0.015] | -0.032 | -0.016 (-0.047 to +0.020) [-0.061, +0.030] |

At a similar sequencing share, one random biopsy per endoscopy loses 0.082 endoscopy-level sensitivity against the triage (bound -0.131) while gaining +0.191 specificity; calling the remaining biopsies with the H&E model recovers 0.052 of that sensitivity (Δ -0.030, bound -0.065) and keeps a specificity gain of +0.040.

### Checks

- Stored values reproduced: single-model triage vs B\* -0.016 / -0.032; vs (B) +0.033; R33 voted row -0.006 / -0.044; R35 share in the same band in all 10 repeats 0.35.
- R23 endoscopy-level single-model triage 0.909 / 0.549; R24 (D) 0.354 / 0.815; R36 L-CNV per-sample 0.785, joint package 0.845.

### Implementation notes

- R37: p53 from the `P53 IHC` field of the analysed-sample table (0 / 1 / blank); endoscopy = (patient, endoscopy number), positive if any sample is flagged; patient positive if any sample is flagged; single-model statistics are per-repeat values averaged over the 10 repeats; the patient bootstrap tags resampled copies of a patient as distinct units (R23). 'Cleared' in (e) = modal low band over the 10 repeats (also low in all 10). B\* and the paired comparisons are on the same samples; cut-offs as stored.
- R38: calls and cut-offs as stored (R33 row 7 logic); the sheet flags are Killcoyne's `excluded` = 1, `remove` = 1 and non-empty `inconsistency`; 'less than 1 year before the last sequenced endoscopy' = the sheet's months-before-final < 12 for non-progressor samples (so the last endoscopy itself is excluded), 24 for 2 years; later HGD+ = the K1 definition of `pk_main.py` on `later_disease_patient.csv`, joined to the analysed patients by study number (every non-progressor patient matched; the stored K1 count of 6 later HGD+ among 42 refers to the ERIN-labelled discovery non-progressors, five of whom are sheet progressors); (d) uses (a) 'excluded' only.
- R39: one task per row, recomputed with the rv4 machinery; the voted comparator is the training-matched B\* voted the same way; the selection-inclusive row uses the stored round-4 draws (no pivotal CI); rows 16–18 are not applicable to a voted rule; the 'evaluation-matched' row is the voted evaluation-matched B\* of the primary analysis. Stability = agreement of the 10 per-repeat triage calls with the voted call.
- R40: four L-CNV outer prediction sets (stored shipped, stored package, round-4 past-only and per-sample refits) on identical folds; the same 2,000 patient draws score every version; Holm over the six pairs on two-sided bootstrap p-values. Samples segmented together = the patient's sample count in the joint call (all of the patient's sheet samples, `rv4_reseg.R`); tertile edges are the pre-event terciles of that count, ties kept in the lower tertile.
- R41: the random biopsy's call is its stored (B) call (L-LATE at that repeat × fold's 80%-training-sensitivity threshold); the variant adds the stored (C) call of the endoscopy's other samples; the triage endoscopy call is 'any sample positive'; the patient bootstrap resamples patients with all their endoscopies and reports the seed-averaged statistic per draw (pooled seed × draw percentiles in the JSON).

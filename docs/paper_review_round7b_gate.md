# Review round 7b: exploring the per-endoscopy gate with nested selection

Status: PRE-SPECIFICATION (written 2026-10-17). Nothing below has been run. Results are appended under the line at the end in a later commit; this section is not edited afterwards.

## Why

R49 (`docs/paper_review_round7_analyses.md`, results cd57fb6) found that a per-endoscopy gate matched the sample-level triage per endoscopy while sequencing 25.5% of samples rather than 45.8%. That variant was chosen before it was run, but further variants are now explored after seeing it.

To keep the estimate honest:
1. The variant is selected **inside cross-validation**, using only each outer fold's training patients.
2. The headline estimate is the performance of that whole selection procedure on held-out patients.
3. Apparent (non-nested) results for every variant are reported as well, labelled as optimistic.

No ACE-B file is read. Frozen bundles and stored predictions are unchanged. Conventions as in `docs/paper_review_round6_analyses.md` (5c10c27).

## Unit and comparators

- **Unit:** pre-event endoscopies (288: 88 progressor, 200 non-progressor) with their pre-event samples. An endoscopy is positive (flagged) if the rule flags it. Endoscopy status = patient status.
- **Comparators at endoscopy level** (flag the endoscopy if any sample is called positive):
  - **B\*-endo:** sequence all samples, call each by L-LATE at the B\* threshold.
  - **(B)-endo:** as B\*-endo at the (B) threshold.
  - **Sample-level triage aggregated to endoscopies.**
  - **Random-one:** one random sample per endoscopy, called by L-LATE (R41 seeds). Reported at its own threshold and at the gate's endoscopy specificity (as R46).
  - **R49 gate** (the original variant).

## Variant grid (36 variants)

1. **Aggregation of L-IMG over the endoscopy's samples:** maximum; mean; mean of the top 2 (equal to the maximum when there is one sample).
2. **Cut-offs:**
   - **sample-level:** the per-fold t_low and t_high of the triage;
   - **endoscopy-level:** t_low at 95% and t_high at 90% training endoscopy-level sensitivity and specificity, computed on inner out-of-fold endoscopy scores of the training patients with the same aggregation.
3. **Which samples are sequenced in a middle-band endoscopy:**
   - the sample with the highest L-IMG;
   - the sample whose L-IMG is closest to the middle of the band (the most uncertain);
   - all samples of the endoscopy.
4. **Call for a sequenced middle-band endoscopy:** positive if any sequenced sample is positive by L-LATE at t_seq, or by L-CNV at its triage-matched threshold (`rv4` copy-number-only middle band rule).

Low-band endoscopies: all samples are cleared. High-band endoscopies are flagged without sequencing.

## Nested selection rule (fixed)

In each outer fold of each repeat:
1. Compute every variant on the **inner out-of-fold predictions of the training patients only**, at endoscopy level.
2. **Eligible:** the inner endoscopy sensitivity is at least that of B\*-endo on the same inner predictions minus 0.02, and the inner endoscopy specificity is at least B\*-endo's minus 0.05.
3. **Choose** the eligible variant with the lowest inner share of samples sequenced. Ties go to the simpler variant, in this order:
   - maximum before top-2 before mean;
   - sample-level before endoscopy-level cut-offs;
   - highest before uncertain before all;
   - L-LATE before L-CNV.
4. If no variant is eligible, use the sample-level triage.
5. Apply the chosen variant to the outer fold's held-out endoscopies.

## Primary reporting for this exploration

**Nested gate against B\*-endo** (single model, means over 10 repeats; patient bootstrap with fitted models and selections fixed):
- Δ endoscopy sensitivity with two-sided CI and one-sided bound, against the −0.05 margin;
- Δ endoscopy specificity;
- share of samples sequenced;
- share of endoscopies with ≥ 1 sample sequenced.

**Also reported:**
- the same against the sample-level triage, (B)-endo and random-one (own threshold, and matched endoscopy specificity);
- patient columns (progressor patients missed of 32; non-progressor patients flagged of 43);
- how often each variant was chosen across the 100 outer folds;
- the apparent results of all 36 variants on the outer predictions, labelled optimistic.

## Robustness of the nested gate

Same nested rule, re-run with:
- **(a)** NDBE-only samples (endoscopies keep their NDBE samples only);
- **(b)** the earliest pre-event endoscopy per patient;
- **(c)** endoscopies with ≥ 2 samples only;
- **(d)** the R52(a) cohort with the 8 progressors' same-block samples, using the R52(a) refit predictions;
- **(e)** between-repeat variance: the share of the 10 repeats in which the nested gate's bound against B\*-endo stays within −0.05, and the bound with the between-repeat variance added (as R33).

## Trade-off curve (descriptive)

Endoscopy sensitivity and specificity against share of samples sequenced over a 3 × 3 grid of cut-off quantiles (t_low at 90/95/98% sensitivity, t_high at 85/90/95% specificity) for:
- the nested gate's most-chosen variant;
- the sample-level triage;
- random-one.

## What follows from the result (fixed now)

- **If** the nested gate is within −0.05 of B\*-endo (bound) and sequences fewer samples than the sample-level triage, it becomes:
  - the manuscript's headline development result, described as "selected by nested cross-validation, after R49";
  - the proposed primary rule for ACE-B registration.

  The sample-level triage remains reported as the original pre-specified analysis.
- **Otherwise** the sample-level triage stays the headline, and the gate is reported as exploratory.

## Scripts and running

- **Script:** `scripts/paper_plan/rv7b_gate.py`, re-scoring stored outer and inner predictions. No refit, except reading the R52(a) refit outputs.
- **Execution:** cluster jobs via `scripts/cluster/campaign.sh`, prefix `rv7b`.
- **Outputs:** aggregates to `results/paper_final/review_round7b/`; results appended below by `rv7b_render.py`.

---

## Results

Rendered by `scripts/paper_plan/rv7b_render.py` from `results/paper_final/review_round7b/` (aggregate results 139edda). Single model = per-repeat values averaged over the 10 repeats; patient bootstrap 2,000 draws (`RandomState(0)`) with fitted models, cut-offs and selections fixed; bound = one-sided 95% lower bound (5th percentile). Unit = pre-event endoscopy.

| Item | Status |
|---|---|
| nested gate against B\*-endo (primary) | DONE |
| against triage, (B)-endo, random-one, R49 | DONE |
| patient columns | DONE |
| variant choice frequencies | DONE |
| apparent results of the 36 variants (optimistic) | DONE |
| robustness (a)–(e) | DONE |
| trade-off curve | DONE |

All inner out-of-fold predictions needed (L-IMG, L-LATE and L-CNV `cnv_their`, stored under `killcoyne_mm/horizons/inner/`; R52(a) refit inner files for (d)) exist, so no variant was dropped from the nested grid.

### Nested gate (primary for this exploration)

288 pre-event endoscopies (88 progressor), 571 samples, 75 patients (32 progressor). In 96 of 100 outer folds at least one variant was eligible on the inner predictions; 4 fell back to the sample-level triage. Nested endoscopy bands (per repeat): low 0.252, middle 0.435, high 0.273, fallback 0.039.

| Rule | Endoscopy sens [95% CI] | Endoscopy spec [95% CI] | Samples sequenced | Endoscopies sequenced | Progressor patients missed (of 32) / non-progressor flagged (of 43) |
|---|---|---|---|---|---|
| **nested gate** | 0.889 [0.839, 0.939] | 0.589 [0.511, 0.674] | 0.241 | 0.460 | 1.0 / 31.0 |
| B\*-endo (sequence all, B\* threshold) | 0.923 [0.873, 0.962] | 0.530 [0.431, 0.629] | 1.000 | 1.000 | 0.8 / 31.7 |
| (B)-endo (sequence all, (B) threshold) | 0.876 [0.803, 0.935] | 0.640 [0.552, 0.726] | 1.000 | 1.000 | 1.3 / 28.5 |
| sample-level triage, aggregated | 0.909 [0.865, 0.952] | 0.549 [0.460, 0.637] | 0.458 | 0.597 | 0.9 / 32.0 |
| random-one, own threshold | 0.827 [0.742, 0.901] | 0.740 [0.673, 0.805] | 0.504 | 1.000 | 2.2 / 25.1 |
| random-one, matched to the nested gate's endoscopy specificity | 0.920 [0.854, 0.961] | 0.590 [0.513, 0.676] | 0.504 | 1.000 | 1.1 / 30.8 |
| R49 gate (max, sample-level, highest, L-LATE) | 0.907 [0.861, 0.951] | 0.560 [0.475, 0.645] | 0.255 | 0.505 | 0.9 / 31.8 |
| R49 variant (max, sample-level, all, L-LATE) | 0.914 [0.871, 0.955] | 0.543 [0.453, 0.633] | 0.501 | 0.505 | 0.9 / 32.4 |

| Nested gate − | Δ endoscopy sens [95% CI] | Bound | Within −0.05 | Δ endoscopy spec [95% CI] | Δ share of samples sequenced [95% CI] | Δ share of endoscopies sequenced |
|---|---|---|---|---|---|---|
| B\*-endo (sequence all, B\* threshold) | -0.034 [-0.073, -0.001] | -0.066 | no | +0.060 [+0.016, +0.114] | -0.759 [-0.794, -0.722] | -0.540 |
| (B)-endo (sequence all, (B) threshold) | +0.012 [-0.033, +0.056] | -0.025 | yes | -0.051 [-0.090, -0.003] | -0.759 [-0.794, -0.722] | -0.540 |
| sample-level triage, aggregated | -0.020 [-0.036, -0.005] | -0.034 | yes | +0.040 [+0.022, +0.065] | -0.218 [-0.249, -0.183] | -0.137 |
| random-one, own threshold | +0.062 [+0.009, +0.123] | +0.018 | yes | -0.150 [-0.197, -0.101] | -0.264 [-0.312, -0.224] | -0.540 |
| random-one, matched to the nested gate's endoscopy specificity | -0.031 [-0.075, +0.021] | -0.067 | no | -0.000 [-0.004, -0.001] | -0.264 [-0.312, -0.224] | -0.540 |
| R49 gate (max, sample-level, highest, L-LATE) | -0.018 [-0.034, -0.004] | -0.032 | yes | +0.029 [+0.015, +0.049] | -0.014 [-0.028, -0.001] | -0.045 |
| R49 variant (max, sample-level, all, L-LATE) | -0.025 [-0.043, -0.008] | -0.040 | yes | +0.047 [+0.025, +0.075] | -0.260 [-0.309, -0.207] | -0.045 |

### Variant choice across the 100 outer folds

| Variant (aggregation · cut-offs · sequenced · call) | Folds chosen |
|---|---|
| max · sample-level cut-offs · highest · L-LATE | 48 |
| mean · endoscopy-level cut-offs · highest · L-LATE | 37 |
| max · endoscopy-level cut-offs · highest · L-LATE | 5 |
| fallback: sample-level triage | 4 |
| top2 · endoscopy-level cut-offs · highest · L-LATE | 4 |
| max · sample-level cut-offs · all · L-LATE | 1 |
| mean · endoscopy-level cut-offs · highest · L-CNV | 1 |

By factor (folds with a variant chosen): aggregation: max 54, top2 4, mean 38; cutoffs: sample 49, endoscopy 47; sequenced: highest 95, uncertain 0, all 1; call: L-LATE 95, L-CNV 1.

Inner (training patients, inner out-of-fold predictions; medians over folds): eligible variants 19 (range 0–36) of 36; B\*-endo sensitivity / specificity 0.909 / 0.486; sample-level triage 0.920 / 0.478, share sequenced 0.576; chosen variant 0.910 / 0.514, share sequenced 0.278.

### Robustness of the nested gate

Same nested rule re-run on each population (cut-offs, comparators, inner selection and evaluation all restricted to it).

| Row | Endoscopies (progressor) / samples / patients (progressor) | Nested endo sens / spec | Δ endo sens vs B\*-endo [95% CI] | Bound | Within −0.05 | Δ endo spec vs B\*-endo | Samples sequenced: nested / triage | Endoscopies sequenced: nested / triage | Δ endo sens vs triage (bound) | Fallback folds | Most-chosen variant |
|---|---|---|---|---|---|---|---|---|---|---|---|
| primary (all pre-event samples) | 288 (88) / 571 / 75 (32) | 0.889 / 0.589 | -0.034 [-0.073, -0.001] | -0.066 | no | +0.060 | 0.241 / 0.458 | 0.460 / 0.597 | -0.020 (-0.034) | 4 | max · sample-level cut-offs · highest · L-LATE |
| (a) NDBE-only samples | 240 (68) / 438 / 71 (28) | 0.893 / 0.583 | -0.040 [-0.094, -0.005] | -0.081 | no | +0.066 | 0.260 / 0.491 | 0.462 / 0.600 | -0.028 (-0.048) | 3 | mean · endoscopy-level cut-offs · highest · L-LATE |
| (b) earliest pre-event endoscopy per patient | 75 (32) / 140 / 75 (32) | 0.856 / 0.619 | -0.034 [-0.070, -0.003] | -0.064 | no | +0.047 | 0.279 / 0.450 | 0.473 / 0.553 | -0.013 (-0.026) | 9 | max · sample-level cut-offs · highest · L-LATE |
| (c) endoscopies with ≥ 2 samples | 146 (40) / 429 / 64 (25) | 0.925 / 0.541 | -0.032 [-0.067, -0.005] | -0.061 | no | +0.089 | 0.178 / 0.450 | 0.449 / 0.702 | -0.022 (-0.040) | 2 | max · sample-level cut-offs · highest · L-LATE |
| (d) R52(a) cohort, refit predictions | 290 (90) / 577 / 77 (34) | 0.896 / 0.606 | -0.024 [-0.045, -0.007] | -0.041 | yes | +0.046 | 0.245 / 0.481 | 0.470 / 0.618 | -0.022 (-0.035) | 2 | mean · endoscopy-level cut-offs · highest · L-LATE |

**(e) Between-repeat variance** (primary, R33 / R15 logic): per-repeat Δ endoscopy sensitivity nested − B\*-endo ranges -0.057 to +0.011; the per-repeat bound stays within −0.05 in 1 of 10 repeats (10%). With the between-repeat variance added: Δ -0.034, 95% interval [-0.086, +0.018], bound -0.078 (not within −0.05).

### Trade-off curve (descriptive)

Most-chosen variant (max · sample-level cut-offs · highest · L-LATE) applied in every fold (not nested); sample-level triage; random-one matched to the gate's endoscopy specificity at each grid point (own threshold: 0.827 / 0.740, 0.504 of samples). Endoscopy sens / spec, share of samples sequenced.

| t_low sens / t_high spec | Gate variant | Triage | Random-one (matched) |
|---|---|---|---|
| 0.90 / 0.85 | 0.894 / 0.580, 0.175 | 0.894 / 0.574, 0.298 | 0.923 / 0.580, 0.504 |
| 0.90 / 0.90 | 0.887 / 0.611, 0.209 | 0.887 / 0.603, 0.342 | 0.908 / 0.611, 0.504 |
| 0.90 / 0.95 | 0.865 / 0.645, 0.249 | 0.865 / 0.638, 0.401 | 0.886 / 0.645, 0.504 |
| 0.95 / 0.85 | 0.917 / 0.526, 0.220 | 0.919 / 0.514, 0.414 | 0.944 / 0.526, 0.504 |
| 0.95 / 0.90 | 0.907 / 0.560, 0.255 | 0.909 / 0.549, 0.458 | 0.931 / 0.560, 0.504 |
| 0.95 / 0.95 | 0.895 / 0.603, 0.295 | 0.897 / 0.589, 0.517 | 0.914 / 0.603, 0.504 |
| 0.98 / 0.85 | 0.936 / 0.482, 0.266 | 0.941 / 0.470, 0.542 | 0.958 / 0.482, 0.504 |
| 0.98 / 0.90 | 0.927 / 0.514, 0.300 | 0.931 / 0.500, 0.586 | 0.950 / 0.514, 0.504 |
| 0.98 / 0.95 | 0.914 / 0.567, 0.340 | 0.917 / 0.547, 0.645 | 0.927 / 0.567, 0.504 |

### Apparent results of the 36 variants (optimistic: not nested, chosen after seeing R49)

| Variant | Endo sens | Endo spec | Samples sequenced | Endoscopies sequenced | Patients missed / flagged | Δ endo sens vs B\*-endo (bound) | Δ endo spec vs B\*-endo | Δ samples vs triage | Folds chosen (nested) |
|---|---|---|---|---|---|---|---|---|---|
| max · sample-level cut-offs · highest · L-LATE | 0.907 | 0.560 | 0.255 | 0.505 | 0.9 / 31.8 | -0.016 (-0.038) | +0.030 | -0.204 | 48 |
| max · sample-level cut-offs · highest · L-CNV | 0.894 | 0.568 | 0.255 | 0.505 | 1.1 / 32.1 | -0.028 (-0.052) | +0.038 | -0.204 | 0 |
| max · sample-level cut-offs · uncertain · L-LATE | 0.903 | 0.570 | 0.255 | 0.505 | 0.9 / 31.2 | -0.019 (-0.041) | +0.041 | -0.204 | 0 |
| max · sample-level cut-offs · uncertain · L-CNV | 0.893 | 0.568 | 0.255 | 0.505 | 1.1 / 32.1 | -0.030 (-0.053) | +0.038 | -0.204 | 0 |
| max · sample-level cut-offs · all · L-LATE | 0.914 | 0.543 | 0.501 | 0.505 | 0.9 / 32.4 | -0.009 (-0.031) | +0.013 | +0.042 | 1 |
| max · sample-level cut-offs · all · L-CNV | 0.902 | 0.530 | 0.501 | 0.505 | 1.1 / 33.4 | -0.020 (-0.045) | +0.000 | +0.042 | 0 |
| max · endoscopy-level cut-offs · highest · L-LATE | 0.889 | 0.591 | 0.241 | 0.477 | 1.0 / 31.6 | -0.034 (-0.066) | +0.061 | -0.218 | 5 |
| max · endoscopy-level cut-offs · highest · L-CNV | 0.858 | 0.654 | 0.241 | 0.477 | 1.2 / 28.3 | -0.065 (-0.098) | +0.125 | -0.218 | 0 |
| max · endoscopy-level cut-offs · uncertain · L-LATE | 0.887 | 0.597 | 0.241 | 0.477 | 1.0 / 31.3 | -0.035 (-0.067) | +0.067 | -0.218 | 0 |
| max · endoscopy-level cut-offs · uncertain · L-CNV | 0.857 | 0.654 | 0.241 | 0.477 | 1.2 / 28.3 | -0.066 (-0.099) | +0.125 | -0.218 | 0 |
| max · endoscopy-level cut-offs · all · L-LATE | 0.893 | 0.579 | 0.487 | 0.477 | 1.0 / 31.9 | -0.030 (-0.061) | +0.049 | +0.029 | 0 |
| max · endoscopy-level cut-offs · all · L-CNV | 0.866 | 0.617 | 0.487 | 0.477 | 1.2 / 30.1 | -0.057 (-0.089) | +0.087 | +0.029 | 0 |
| top2 · sample-level cut-offs · highest · L-LATE | 0.906 | 0.566 | 0.275 | 0.546 | 0.9 / 31.8 | -0.017 (-0.040) | +0.036 | -0.183 | 0 |
| top2 · sample-level cut-offs · highest · L-CNV | 0.880 | 0.601 | 0.275 | 0.546 | 1.3 / 30.8 | -0.043 (-0.074) | +0.071 | -0.183 | 0 |
| top2 · sample-level cut-offs · uncertain · L-LATE | 0.886 | 0.617 | 0.275 | 0.546 | 1.4 / 30.4 | -0.036 (-0.066) | +0.088 | -0.183 | 0 |
| top2 · sample-level cut-offs · uncertain · L-CNV | 0.882 | 0.611 | 0.275 | 0.546 | 1.3 / 30.8 | -0.041 (-0.068) | +0.081 | -0.183 | 0 |
| top2 · sample-level cut-offs · all · L-LATE | 0.911 | 0.549 | 0.572 | 0.546 | 0.9 / 32.3 | -0.011 (-0.034) | +0.020 | +0.114 | 0 |
| top2 · sample-level cut-offs · all · L-CNV | 0.891 | 0.560 | 0.572 | 0.546 | 1.3 / 32.6 | -0.032 (-0.059) | +0.031 | +0.114 | 0 |
| top2 · endoscopy-level cut-offs · highest · L-LATE | 0.887 | 0.599 | 0.236 | 0.468 | 1.1 / 31.3 | -0.035 (-0.067) | +0.069 | -0.222 | 4 |
| top2 · endoscopy-level cut-offs · highest · L-CNV | 0.852 | 0.659 | 0.236 | 0.468 | 1.7 / 28.6 | -0.070 (-0.111) | +0.129 | -0.222 | 0 |
| top2 · endoscopy-level cut-offs · uncertain · L-LATE | 0.866 | 0.644 | 0.236 | 0.468 | 1.8 / 30.1 | -0.057 (-0.098) | +0.114 | -0.222 | 0 |
| top2 · endoscopy-level cut-offs · uncertain · L-CNV | 0.856 | 0.667 | 0.236 | 0.468 | 1.7 / 28.7 | -0.067 (-0.105) | +0.138 | -0.222 | 0 |
| top2 · endoscopy-level cut-offs · all · L-LATE | 0.892 | 0.589 | 0.495 | 0.468 | 1.1 / 31.5 | -0.031 (-0.062) | +0.059 | +0.037 | 0 |
| top2 · endoscopy-level cut-offs · all · L-CNV | 0.865 | 0.625 | 0.495 | 0.468 | 1.7 / 30.1 | -0.058 (-0.093) | +0.095 | +0.037 | 0 |
| mean · sample-level cut-offs · highest · L-LATE | 0.906 | 0.571 | 0.280 | 0.554 | 0.9 / 31.7 | -0.017 (-0.040) | +0.041 | -0.179 | 0 |
| mean · sample-level cut-offs · highest · L-CNV | 0.874 | 0.623 | 0.280 | 0.554 | 1.5 / 28.9 | -0.049 (-0.083) | +0.093 | -0.179 | 0 |
| mean · sample-level cut-offs · uncertain · L-LATE | 0.881 | 0.633 | 0.280 | 0.554 | 1.5 / 29.9 | -0.042 (-0.075) | +0.104 | -0.179 | 0 |
| mean · sample-level cut-offs · uncertain · L-CNV | 0.875 | 0.632 | 0.280 | 0.554 | 1.5 / 29.1 | -0.048 (-0.079) | +0.103 | -0.179 | 0 |
| mean · sample-level cut-offs · all · L-LATE | 0.911 | 0.558 | 0.596 | 0.554 | 0.9 / 31.9 | -0.011 (-0.034) | +0.029 | +0.137 | 0 |
| mean · sample-level cut-offs · all · L-CNV | 0.886 | 0.584 | 0.596 | 0.554 | 1.5 / 31.0 | -0.036 (-0.065) | +0.054 | +0.137 | 0 |
| mean · endoscopy-level cut-offs · highest · L-LATE | 0.887 | 0.611 | 0.224 | 0.445 | 1.1 / 30.6 | -0.035 (-0.067) | +0.081 | -0.234 | 37 |
| mean · endoscopy-level cut-offs · highest · L-CNV | 0.858 | 0.675 | 0.224 | 0.445 | 1.6 / 27.5 | -0.065 (-0.106) | +0.145 | -0.234 | 1 |
| mean · endoscopy-level cut-offs · uncertain · L-LATE | 0.864 | 0.671 | 0.224 | 0.445 | 1.7 / 28.5 | -0.059 (-0.099) | +0.141 | -0.234 | 0 |
| mean · endoscopy-level cut-offs · uncertain · L-CNV | 0.860 | 0.683 | 0.224 | 0.445 | 1.6 / 27.8 | -0.062 (-0.101) | +0.153 | -0.234 | 0 |
| mean · endoscopy-level cut-offs · all · L-LATE | 0.892 | 0.603 | 0.483 | 0.445 | 1.1 / 30.6 | -0.031 (-0.062) | +0.073 | +0.025 | 0 |
| mean · endoscopy-level cut-offs · all · L-CNV | 0.870 | 0.642 | 0.483 | 0.445 | 1.6 / 29.2 | -0.052 (-0.088) | +0.112 | +0.025 | 0 |

### What follows

Nested gate against B\*-endo: bound -0.066 (not within −0.05); samples sequenced 0.241 against 0.458 for the sample-level triage (fewer).

The conditions are not both met, so by the pre-specified rule the sample-level triage stays the headline and the gate is reported as exploratory.

### Checks

- R49 gate through this code: 0.907, 0.560, 0.255, 0.505, 0.900, 31.800 (R49: 0.907, 0.560, 0.255, 0.505, 0.900, 31.800; endoscopy sens, spec, samples, endoscopies, patients missed, flagged); reproduced: yes; sensitivity CI [0.861, 0.951] (R49 [0.861, 0.951]).
- R49 all-samples variant: 0.914, 0.543, 0.501, 0.505, 0.900, 32.400 (R49: 0.914, 0.542, 0.501, 0.505, 0.900, 32.400); reproduced: yes.
- B\*-endo: 0.923, 0.530 (Table 1 endoscopy column: 0.923, 0.530); reproduced: yes.
- Sample-level triage aggregated: 0.909, 0.549, 0.458, 0.597, 0.900, 32.000 (R49: 0.909, 0.549, 0.458, 0.597, 0.900, 32.000); reproduced: yes.
- Random-one at its own threshold: 0.827, 0.740 (R46: 0.827, 0.740); reproduced: yes.
- The B\* fold threshold recomputed for the inner evaluation reproduces the stored outer B\* calls in every fold (asserted in each selection job).

### Implementation notes

- Inner evaluation: for each outer (repeat, fold), every variant is scored on the inner out-of-fold predictions of that fold's training patients (the stored inner files from which the triage's t_low, t_high and t_seq are chosen), grouped into the training patients' pre-event endoscopies. The sample-level cut-offs and t_seq are the fold's own (chosen on the same inner predictions); the endoscopy-level cut-offs are chosen on the same inner endoscopy scores. So inner performance is apparent with respect to the cut-offs, out-of-fold with respect to the models.
- Inner B\*-endo: the fold's B\* threshold (L-LATE, training-matched to the triage's inner specificity, exactly as `matched_calls`) applied to the inner L-LATE of the training samples; endoscopy flagged if any sample is positive. Eligibility uses 'at least' with a 1e-9 tolerance for floating ties. 'Share of samples sequenced' compares integer counts, so equal shares tie exactly and go to the lower variant in the pre-specified order (aggregation, then cut-off type, then sequenced sample, then call).
- Middle-band call: L-LATE at the triage's fold t_seq for every variant, including those with endoscopy-level cut-offs (t_seq is not re-chosen). L-CNV threshold = the fold t_seq of the rv4 copy-number-only middle band (`triage(..., mid='L-CNV')`, R35 a): 80% sensitivity of inner L-CNV among the middle-band training progressor samples, with the same fallback.
- 'Uncertain' sample = the sample whose L-IMG is closest to (t_low + t_high) / 2 of the cut-offs in use (sample-level or endoscopy-level); ties to the first sample in sorted order. Top-2 mean = mean of the two highest L-IMG (the maximum when there is one sample). Endoscopy bands as R49: low if score < t_low, high if score > t_high, no middle band when t_low > t_high.
- Endoscopy-level cut-offs: t_low = the largest threshold keeping ≥ 95% of training progressor endoscopies at or above it (`thr_sens`), t_high = the ⌈0.90 n⌉-th smallest training non-progressor endoscopy score (`c_star`), per aggregation.
- Fallback (no eligible variant): the held-out endoscopies of that fold are called by the sample-level triage (flagged if any sample is triage-positive; sequenced samples = middle-band samples).
- Bootstrap: the R49 draw loop (2,000 patient draws, RandomState(0), draws with only one class rejected), endoscopies of a resampled patient kept together; calls, cut-offs and chosen variants fixed. Patient columns: patient flagged if any of its pre-event endoscopies is flagged; counts averaged over repeats.
- Random-one: R41 seeds 0–99, R41 draw order over the row's endoscopies in sorted order; own threshold = the stored (B) call of the picked sample; matched = one L-LATE threshold per seed × repeat, pooled across folds, set to the nested gate's endoscopy specificity in that repeat and re-set in each draw (as R46, with a 1e-9 guard on ⌈s·n⌉).
- Robustness rows re-run the whole procedure on the restricted population: cut-offs, t_seq, B\*, (B) and inner selection are re-chosen on the training samples of that population (as R50 for NDBE). (a) NDBE pre-event samples; endoscopies with no NDBE sample drop out. (b) earliest pre-event endoscopy = the patient's pre-event endoscopy with the largest months-before-final; unlike R33 row 13, cut-offs are re-chosen on these endoscopies. (c) endoscopies with ≥ 2 pre-event samples. (d) the R52(a) set and its refit outer and inner predictions (`killcoyne_mm/review_round7/refit/r52a`), endoscopy = the set's (patient, endoscopy).
- Checks: values are compared at three decimals with a tolerance of 0.0015; the R49 all-samples variant's specificity prints 0.543 here against 0.542 in R49 because the value is exactly 0.5425 (915 of 2,000 non-progressor endoscopy-repeats flagged) and the two scripts' summation order decides the rounding; all other values are identical. The curve task ran before the scripts commit with byte-identical code.
- (e) as R15 / R33: per-repeat Δ with its own 5th-percentile bound; variance-inflated bound = mean Δ − 1.645 √(V_boot + V_rep), V_boot = variance of the bootstrap repeat-mean Δ, V_rep = variance of the 10 per-repeat Δ.
- Trade-off curve: the most-chosen variant (ties to the simpler) applied in all folds with cut-offs at each grid point (sample-level cut-offs and t_seq from the triage rule at those quantiles; endoscopy-level cut-offs at the same quantiles on inner endoscopy scores). Random-one has no cut-off quantiles, so it is shown at its own threshold and matched (evaluation-matched, per repeat) to the gate's endoscopy specificity at each grid point. No intervals.

# Review round 1: analyses requested by reviewers (excluding ACE-B)

Status: PRE-SPECIFICATION (written 2026-10-13). Nothing below has been run. Results are appended under the line at the end in a later commit; this section is not edited afterwards.

Purpose: answer the objections raised in the first internal review of the manuscript draft (11 reviews, synthesised outside the repository). Nothing here changes a model, a feature or the headline analyses; every item re-scores stored predictions, except R13, which trains attention models under the existing folds.

**Ground rules**, as in `docs/paper_triage.md` and `docs/paper_triage_robustness.md`:
- report only, with a status per item and at most one line of interpretation per item;
- earlier documents are not edited;
- row-level data stay on the cluster;
- the cohort is never referred to by its internal short label.

**Population and data.**
- Primary: all pre-event samples of the 676 samples from 80 patients of the Killcoyne discovery cohort with a matched H&E slide (571 samples, 75 patients, 161 samples from 32 progressors). Pre-event means the sample's endoscopy is strictly earlier than the first HGD/IMC endoscopy, so same-day samples are excluded (`hz_prep.py`).
- Their copy-number matrix is primary; package features are reported where stated.
- Predictions: stored outer held-out predictions of the stratified patient-grouped 10-fold × 10-repeat CV (`kv_cv.R` d69de24, `hz_fit.R` outer) and stored inner out-of-fold predictions (`hz_fit.R` inner). The CV models were trained on all samples of the training patients, including post-event samples; this is stated, not changed.
- Triage, comparators (A), (B), (C), cut-off rules and the ≥ 6-of-10 vote are those of `paper_triage.md`, as implemented in `scripts/paper_plan/tb_common.py`.

**Shared conventions.**
- Fold-stratified AUROC: only case–control pairs in the same outer fold of a repeat are compared, then averaged over repeats.
- Patient bootstrap: 2,000 draws, `RandomState(0)`, draws without both classes redrawn, resampled patients keep their folds, calls and predictions fixed unless stated.
- "Repeat-mean score": a sample's held-out prediction averaged over the 10 repeats.
- (P) is Killcoyne's published probability, scored on the same pairs.

## R1. Triage against comparators at matched specificity (primary item of this round)

Question: is the triage's sensitivity advantage over (A), (B) and (C) more than a move along the comparators' ROC curves?

- **Fold-honest matched comparators (A\*, B\*, C\*).** In each repeat r and outer fold k:
  1. Apply the primary triage rule to the population training rows' inner out-of-fold predictions: band from inner L-IMG with that fold's t_low and c\*, middle-band call L-LATE ≥ t_seq.
  2. Its training specificity s\* is the share of training controls called negative.
  3. For comparator model X (A\*: L-CNV, B\*: L-LATE, C\*: L-IMG), set the threshold to the ⌈s\*·n₀⌉-th smallest inner training-control score of X. A held-out sample is positive if X > threshold.
  4. Vote ≥ 6 of 10 as for the triage.
- **Reported:** sensitivity and specificity of A\*, B\* and C\*; paired Δ sensitivity and Δ specificity of triage minus each, with patient-bootstrap 95% CIs.
- **Secondary (test-set matching, conservative for the triage because the comparator threshold is chosen on the evaluation data):** for each X, on repeat-mean scores of the population, the comparator's sensitivity at the largest threshold whose specificity ≥ the triage's observed specificity. Paired Δ with the threshold re-chosen inside each bootstrap draw.
- **Populations:** their matrix (primary) and package features; all pre-event and NDBE pre-event samples.
- **Interpretation rule, fixed now:** if the lower bound of Δ sensitivity versus B\* and versus C\* is above 0, the triage adds sensitivity at matched specificity. If a CI contains 0, the triage is described as matching that comparator's accuracy while sequencing fewer samples (B\*) or as not shown to add to H&E alone (C\*).

## R2. Patient-level and patient-weighted discrimination

Models: L-CNV, L-IMG, L-LATE, (P); their matrix and package features.
- **(a) Patient-level, fold-stratified AUROC.** A patient's score is the mean of its pre-event held-out predictions in that repeat; patients compared only within the same outer fold; mean over repeats.
- **(b)** As (a) with the patient's earliest pre-event sample instead of the mean.
- **(c) Patient-weighted per-sample AUROC:** fold-stratified, each case–control pair weighted 1/(n_i·n_j), where n is the patient's number of pre-event samples.
- **Paired Δ:** L-IMG − L-CNV, with the non-inferiority lower bound at −0.05; L-LATE − L-CNV.
- **Also reported:** two-sided 95% CIs alongside one-sided bounds, for this and for the main-text non-inferiority results (from stored draws).

## R3. Calibration (relative, case–control caveat)

For L-CNV, L-IMG and L-LATE (their matrix, all pre-event samples), on repeat-mean scores:
- calibration slope b and intercept a from logit P(y) = a + b·logit(p);
- calibration-in-the-large: intercept with slope fixed at 1;
- observed progressor share against mean predicted probability by decile.

Patient-bootstrap CIs (refit per draw). Interpreted only as relative calibration between models, because sampling is case–control (28% progressor samples).

## R4. Scanner, like-for-like

- **(a)** Main CV (mixed-scanner training) fold-stratified AUROC of L-IMG, L-CNV and L-LATE restricted to C13210 pre-event samples, and to C13239-01 pre-event samples (pairs within fold and within that scanner subset).
- **(b) Triage under transfer to C13210** (exploratory):
  - Scores: the stored cross-scanner L-IMG predictions on C13210 from the model trained on C13239-01 patients with no C13210 sample (`triage_robustness/scanner/cross_b_s39_none.csv`).
  - Band cut-offs: t_low and c\* as already computed on that model's training-scanner inner out-of-fold predictions (0.141 and 0.497).
  - Middle band: L-LATE_transfer = (cross L-IMG + repeat-mean held-out L-CNV)/2 ≥ 0.233 (the frozen median t_seq).
  - Reported: sensitivity, specificity and band shares on C13210, next to the main triage's voted calls restricted to C13210 samples.
- **(c)** Count of folds with both classes and of within-fold pairs per repeat for the within-C13210 CV (`docs/paper_triage_robustness.md` item 5), to explain its narrow CI.

## R5. Technical confounders of the H&E score

On all pre-event samples, using `set_C.csv` `year` (biopsy year) and `horizons/slide_desc.csv` `tissue_tiles`:
- **(a)** Fold-stratified AUROC for progression of year and of tissue-tile count as raw scores (same pairs as the models), with CIs.
- **(b)** L-IMG fold-stratified AUROC in samples with tissue_tiles < 256 (overlapping tiles) and ≥ 256.
- **(c)** Spearman correlation of repeat-mean L-IMG with year and with log tissue tiles, within progressor samples and within non-progressor samples (patient-bootstrap CI).
- **(d)** L-IMG fold-stratified AUROC after residualising the score on year and log tissue tiles. Linear regression of the held-out score on the two covariates, fitted per repeat on the population without labels.

## R6. Timing of pre-event samples

- **Distribution:** time from pre-event progressor sample to first HGD/IMC (`time`): median, IQR, and the number of samples and patients within 6 and 12 months.
- **Re-run without near-event samples:** excluding progressor samples within 1 year of the event (controls unchanged):
  - fold-stratified AUROC of L-CNV, L-IMG, L-LATE and (P);
  - Δ L-IMG − L-CNV with its non-inferiority bound;
  - triage, (A), (B) and (C) sensitivity from the stored voted calls.

## R7. Clinical comparator: worst grade to date

Each sample's worst grade among its patient's samples at the same or earlier endoscopies (NDBE 0, ID 1, LGD 2; HGD/IMC do not occur pre-event).
- Fold-stratified AUROC on all pre-event samples and NDBE pre-event samples. Grade-to-date can vary there because earlier samples may be ID/LGD.
- Paired Δ against L-CNV, L-IMG and L-LATE.

## R8. Triage without the vote

Per repeat (no vote), for the triage and for (A), (B) and (C):
- sensitivity, specificity and share sequenced, as mean and range over the 10 repeats;
- per repeat, the patient-level missed progressors and false-positive non-progressor patients (mean and range);
- the share of samples in the middle band in at least one repeat.

Their matrix and package features, all pre-event samples.

## R9. How different are the image and copy-number scores?

Spearman correlation of repeat-mean L-IMG and L-CNV, within progressor samples and within non-progressor samples (patient-bootstrap CI). Their matrix and package features.

## R10. C-index without within-patient pairs

Fold-stratified Harrell's C (τ = 8 years; `docs/paper_risk_strata.md` addendum A definition) for L-CNV, L-LATE and (P), excluding pairs whose two samples come from the same patient. Paired Δ L-LATE − L-CNV and L-LATE − P, all pre-event samples, their matrix.

## R11. Proportional hazards for the risk-class Cox models

For the primary risk-class Cox models (P, L-CNV, L-LATE; Killcoyne thresholds; all pre-event samples): Schoenfeld-residual test (lifelines `proportional_hazard_test`, rank time transform) per class indicator and globally.

## R12. Band predictive values at other prevalences

From the class-wise band rates of `results/paper_final/triage/their_pre.json`: PPV of the high band and NPV of the low band, and the progressor share within the middle band, at progressor-sample prevalence 2%, 5%, 10% and observed. Arithmetic only, with patient-bootstrap CIs from the stored class-wise band rates' draws (recomputed).

## R13. Attention MIL under the stratified 10 × 10 CV

The manuscript dismissed attention MIL on leave-one-patient-out results. Here:
- N-IMG (`AttentionMIL`, release hyperparameters as in `scripts/paper_plan/km_neural.py`: hidden 256, attention 128, dropout 0.1, AdamW lr 1e-4, weight decay 0.01, batch 8, ≤ 20 epochs, patience 5, positive-class weight) is trained on the stored UNI2-h tile bags (`killcoyne_mm/bags/`).
- Training is in every repeat × fold of the `kv_cv.R` folds, on all samples of the training patients. Early stopping uses a validation group of training patients, chosen as in `km_neural.py`. One seed per repeat × fold (seed = repeat).
- **Reported:**
  - fold-stratified AUROC of N-IMG and N-LATE (= (N-IMG + L-CNV)/2) on all pre-event samples;
  - paired Δ N-IMG − L-IMG and N-LATE − L-LATE.
- GPU cap: 10 GPU-hours.
- Two-phase compute: the bags are pre-extracted embeddings, so no slide files are read.

## Output

- **Scripts** (`scripts/paper_plan/`), run on Slurm via `scripts/cluster/campaign.sh`, prefixes rv (R1–R12) and rva (R13):
  - `rv_round1.py`, TASK = r1 … r12;
  - `rv_abmil_*.py`;
  - `rv_render.py`.
- **Aggregates:** `results/paper_final/review_round1/`.
- **Manuscript:** these results feed `paper/manuscript_draft_v2.md`. v1 is frozen at `paper/frozen/manuscript_draft_v1.md`, SHA-256 6d25ba9d….

---

## Results

Pre-specification commit baa47ab; results commit 87fe74a. Script `scripts/paper_plan/rv_round1.py` (Slurm via `scripts/cluster/campaign.sh`, prefix rv; R13 prefix rva), `rv_render.py`. Aggregates `results/paper_final/review_round1/`.

### Status

| Item | Status |
|---|---|
| R1 matched-specificity comparators | DONE |
| R2 patient-level discrimination | DONE |
| R3 calibration | DONE |
| R4 scanner like-for-like and transfer triage | DONE |
| R5 confounders | DONE |
| R6 timing | DONE |
| R7 worst grade to date | DONE |
| R8 no-vote triage | DONE |
| R9 score correlation | DONE |
| R10 C-index without within-patient pairs | DONE |
| R11 proportional hazards | DONE |
| R12 band predictive values | DONE |
| R13 attention MIL under 10 × 10 CV | PENDING |

### R1. Matched specificity (fold-honest; secondary test-set matching in the last column)

| Population | Triage sens / spec | Comparator | Comparator sens / spec | Δ sens triage − comparator [95% CI] | Δ spec [95% CI] | Secondary Δ sens [95% CI] |
|---|---|---|---|---|---|---|
| their, all pre-event | 0.863 / 0.734 | A* (L-CNV) | 0.745 / 0.685 | +0.118 [+0.025, +0.219] | +0.049 [-0.055, +0.149] | +0.137 [+0.020, +0.286] |
| their, all pre-event | 0.863 / 0.734 | B* (L-LATE) | 0.870 / 0.700 | -0.006 [-0.051, +0.034] | +0.034 [-0.006, +0.083] | +0.012 [-0.038, +0.061] |
| their, all pre-event | 0.863 / 0.734 | C* (L-IMG) | 0.789 / 0.746 | +0.075 [+0.016, +0.135] | -0.012 [-0.061, +0.035] | +0.056 [-0.035, +0.149] |
| their, NDBE pre-event | 0.856 / 0.728 | A* (L-CNV) | 0.721 / 0.677 | +0.135 [+0.038, +0.241] | +0.051 [-0.040, +0.149] | +0.173 [+0.035, +0.330] |
| their, NDBE pre-event | 0.856 / 0.728 | B* (L-LATE) | 0.846 / 0.671 | +0.010 [-0.023, +0.044] | +0.057 [+0.017, +0.103] | +0.019 [-0.020, +0.099] |
| their, NDBE pre-event | 0.856 / 0.728 | C* (L-IMG) | 0.779 / 0.734 | +0.077 [-0.009, +0.165] | -0.006 [-0.068, +0.052] | +0.058 [-0.050, +0.184] |
| package, all pre-event | 0.863 / 0.763 | A* (L-CNV) | 0.795 / 0.727 | +0.068 [-0.018, +0.165] | +0.037 [-0.043, +0.132] | +0.099 [-0.048, +0.264] |
| package, all pre-event | 0.863 / 0.763 | B* (L-LATE) | 0.882 / 0.729 | -0.019 [-0.046, +0.000] | +0.034 [-0.010, +0.087] | +0.006 [-0.042, +0.045] |
| package, all pre-event | 0.863 / 0.763 | C* (L-IMG) | 0.770 / 0.780 | +0.093 [+0.035, +0.160] | -0.017 [-0.077, +0.035] | +0.093 [+0.006, +0.172] |
| package, NDBE pre-event | 0.846 / 0.737 | A* (L-CNV) | 0.798 / 0.707 | +0.048 [-0.036, +0.134] | +0.030 [-0.057, +0.129] | +0.106 [-0.048, +0.290] |
| package, NDBE pre-event | 0.846 / 0.737 | B* (L-LATE) | 0.846 / 0.713 | +0.000 [-0.027, +0.028] | +0.024 [-0.026, +0.083] | +0.010 [-0.045, +0.067] |
| package, NDBE pre-event | 0.846 / 0.737 | C* (L-IMG) | 0.769 / 0.731 | +0.077 [+0.008, +0.154] | +0.006 [-0.052, +0.059] | +0.058 [-0.034, +0.168] |

One line (pre-specified rule): against B\* the CI of Δ sensitivity contains 0 (-0.051 to +0.034), so the triage matches the accuracy of sequencing everyone with late fusion while sequencing fewer samples; against C\* the lower bound is above 0 (+0.016), so the triage adds sensitivity over H&E alone at matched specificity (their matrix, all pre-event; the secondary test-set matching CI includes 0).

### R2. Patient-level and patient-weighted discrimination (fold-stratified)

| CNV source | Measure | L-CNV | L-IMG | L-LATE | P | L-IMG − L-CNV [two-sided 95% CI]; one-sided lower | L-LATE − L-CNV [95% CI] |
|---|---|---|---|---|---|---|---|
| their | patient mean | 0.863 | 0.940 | 0.957 | 0.881 | +0.077 [-0.009, +0.170]; 0.005 | +0.094 [+0.041, +0.166] |
| their | patient earliest | 0.812 | 0.841 | 0.881 | 0.828 | +0.029 [-0.090, +0.162]; -0.075 | +0.069 [-0.006, +0.157] |
| their | patient weighted samples | 0.822 | 0.852 | 0.897 | 0.841 | +0.030 [-0.047, +0.118]; -0.034 | +0.075 [+0.028, +0.131] |
| pkg | patient mean | 0.867 | 0.940 | 0.960 | 0.881 | +0.073 [-0.009, +0.157]; 0.003 | +0.093 [+0.042, +0.153] |
| pkg | patient earliest | 0.812 | 0.841 | 0.889 | 0.828 | +0.029 [-0.087, +0.149]; -0.071 | +0.076 [+0.008, +0.156] |
| pkg | patient weighted samples | 0.832 | 0.852 | 0.899 | 0.841 | +0.020 [-0.062, +0.104]; -0.049 | +0.066 [+0.024, +0.116] |

### R3. Calibration (repeat-mean predictions; relative only, case–control)

| Model | Slope [95% CI] | Intercept [95% CI] | Calibration-in-the-large [95% CI] | Mean predicted / observed |
|---|---|---|---|---|
| L-CNV | 0.737 [0.487, 1.099] | -0.428 [-1.005, 0.233] | -0.310 [-0.959, 0.364] | 0.324 / 0.282 |
| L-IMG | 0.669 [0.527, 0.865] | -0.371 [-0.954, 0.165] | -0.194 [-0.905, 0.477] | 0.302 / 0.282 |
| L-LATE | 1.576 [1.135, 2.230] | 0.066 [-0.531, 0.715] | -0.211 [-0.727, 0.295] | 0.313 / 0.282 |

### R4. Scanner

| Main CV scored on | Samples / patients | L-IMG | L-CNV | L-LATE |
|---|---|---|---|---|
| C13210 | 139 / 27 | 0.835 [0.717, 0.926] | 0.767 [0.641, 0.904] | 0.900 [0.827, 0.958] |
| C13239-01 | 432 / 71 | 0.858 [0.803, 0.909] | 0.802 [0.698, 0.884] | 0.890 [0.825, 0.943] |

Triage on C13210 (139 samples, 27 patients, 9 progressors): under transfer (cut-offs t_low 0.141, c* 0.497, t_seq 0.233) sensitivity 0.744 [0.516, 0.929], specificity 0.690 [0.544, 0.807], bands low/mid/high {'low': 0.496, 'mid': 0.295, 'high': 0.209}; main mixed-scanner CV triage on the same samples sensitivity 0.923 [0.839, 1.000], specificity 0.700 [0.588, 0.793], bands {'low': 0.309, 'mid': 0.469, 'high': 0.222}.

Within-C13210 CV pairs: repeat 1: 9 folds, 371 pairs; repeat 2: 9 folds, 410 pairs; repeat 3: 9 folds, 423 pairs; repeat 4: 9 folds, 424 pairs; repeat 5: 9 folds, 425 pairs; repeat 6: 9 folds, 383 pairs; repeat 7: 9 folds, 423 pairs; repeat 8: 9 folds, 368 pairs; repeat 9: 9 folds, 336 pairs; repeat 10: 9 folds, 326 pairs (of 3900 case–control pairs overall).

### R5. Confounders

- a_auroc_year: 0.572 [0.457, 0.691]
- a_auroc_tissue_tiles: 0.561 [0.473, 0.633]
- b_LIMG_overlap_lt256: 0.905 [0.846, 0.946] (n 293)
- b_LIMG_no_overlap_ge256: 0.799 [0.733, 0.861] (n 278)
- c_spearman_LIMG_year_progressor: 0.171 [-0.087, 0.385]
- c_spearman_LIMG_year_nonprogressor: -0.150 [-0.278, -0.021]
- c_spearman_LIMG_log_tiles_progressor: -0.308 [-0.489, -0.101]
- c_spearman_LIMG_log_tiles_nonprogressor: 0.148 [0.045, 0.250]
- d_LIMG_residualised: 0.831 [0.774, 0.887] (unadjusted 0.847)

### R6. Timing

Progressor pre-event samples: median 2.5 years to event (IQR 1.5–5.0); 15 samples (7 patients) within 6 months, 29 (14) within 1 year.
Excluding those within 1 year (542 samples, 132 progressor, 72 patients): L-CNV 0.785 [0.688, 0.867], L-IMG 0.842 [0.790, 0.892], L-LATE 0.873 [0.802, 0.927], P 0.804 [0.681, 0.905]; L-IMG − L-CNV +0.057 [-0.021, +0.151], one-sided lower -0.010; stored-call sensitivity triage_LATE 0.841, A 0.765, B 0.765, C 0.780.

### R7. Worst grade to date

- pre: worst grade 0.507 [0.378, 0.630]; L-CNV − worst grade +0.294 [+0.169, +0.434], L-IMG − worst grade +0.340 [+0.222, +0.473], L-LATE − worst grade +0.381 [+0.268, +0.512]
- pre_ndbe: worst grade 0.397 [0.279, 0.525]; L-CNV − worst grade +0.383 [+0.236, +0.534], L-IMG − worst grade +0.430 [+0.293, +0.559], L-LATE − worst grade +0.470 [+0.335, +0.600]

### R8. Without the vote (mean over repeats, range)

| CNV source | Strategy | Sensitivity | Specificity | Progressor patients missed | Non-progressor patients with a false positive |
|---|---|---|---|---|---|
| their | triage_LATE | 0.865 (0.832–0.901) | 0.697 (0.622–0.744) | 0.9 (0–3) | 32.0 (30–33) |
| their | A | 0.801 (0.745–0.845) | 0.560 (0.488–0.639) | 2.6 (2–3) | 30.2 (29–34) |
| their | B | 0.832 (0.801–0.863) | 0.762 (0.724–0.795) | 1.3 (0–2) | 28.5 (27–32) |
| their | C | 0.795 (0.758–0.832) | 0.719 (0.688–0.746) | 0.9 (0–2) | 35.0 (31–37) |
| their | share sequenced | 0.458 (0.406–0.559); in middle band in ≥ 1 repeat 0.76 | | | |
| pkg | triage_LATE | 0.865 (0.826–0.907) | 0.737 (0.69–0.776) | 0.9 (0–2) | 33.0 (32–36) |
| pkg | A | 0.812 (0.727–0.907) | 0.683 (0.646–0.741) | 1.4 (0–3) | 28.1 (22–32) |
| pkg | B | 0.827 (0.795–0.888) | 0.793 (0.766–0.829) | 1.0 (0–2) | 28.1 (24–32) |
| pkg | C | 0.795 (0.758–0.832) | 0.719 (0.688–0.746) | 0.9 (0–2) | 35.0 (31–37) |
| pkg | share sequenced | 0.458 (0.406–0.559); in middle band in ≥ 1 repeat 0.76 | | | |

### R9. Spearman correlation of L-IMG and L-CNV (repeat-mean)

- their: progressor_samples 0.163 [-0.048, 0.390], nonprogressor_samples 0.202 [0.059, 0.337], all 0.381 [0.248, 0.500]
- pkg: progressor_samples 0.224 [0.014, 0.432], nonprogressor_samples 0.071 [-0.090, 0.221], all 0.369 [0.231, 0.497]

### R10. Harrell's C without within-patient pairs

L-CNV 0.778 [0.704, 0.854]; L-LATE 0.830 [0.772, 0.881]; P 0.802 [0.715, 0.881]; L-LATE_minus_L-CNV +0.052 [+0.001, +0.111] (p 0.041); L-LATE_minus_P +0.028 [-0.028, +0.097] (p 0.376).

### R11. Proportional hazards (Schoenfeld, rank transform)

P: moderate p 0.1, high p 0.333; L-CNV: moderate p 0.908, high p 0.532; L-LATE: moderate p 0.187, high p 0.08.

### R12. Band predictive values

| Prevalence | PPV high band | NPV low band | Progressor share in middle band |
|---|---|---|---|
| 0.020 | 0.107 [0.077, 0.147] | 0.997 [0.995, 0.998] | 0.015 [0.011, 0.018] |
| 0.050 | 0.236 [0.178, 0.308] | 0.992 [0.986, 0.996] | 0.037 [0.027, 0.046] |
| 0.100 | 0.395 [0.314, 0.484] | 0.982 [0.972, 0.991] | 0.075 [0.056, 0.093] |
| 0.282 | 0.697 [0.618, 0.768] | 0.940 [0.907, 0.969] | 0.222 [0.174, 0.265] |

### R13. Attention MIL under 10 × 10 CV

Pending (running separately; appended when complete).

### Deviations

- None in method for R1–R12. R13 is rendered separately when its run completes.


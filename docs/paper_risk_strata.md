# Risk stratification on the Killcoyne discovery cohort

Status: PRE-SPECIFICATION (written 2026-10-07). Step 0 (reading the paper) was done before writing this section; nothing else has been computed. Results are appended under the line at the end in a later commit; this section is not edited afterwards.

Ground rules as in `docs/paper_horizon_answers.md`: no refitting of any prediction model (survival models below are analysis models fitted to stored predictions); stored fold-honest out-of-fold predictions only; report only; status per item; at most one line of interpretation per question; earlier docs not edited; patient lists on the cluster only.

Population name used throughout: **the 676 samples from 80 patients of the Killcoyne discovery cohort with a matched H&E slide** (37 progressors by Killcoyne's sheet `Status`).

## Step 0. What Killcoyne et al. 2020 reported (Nat Med 26:1726, `s41591-020-1033-y.pdf`; supplementary appendix `EMS86618-supplement-Supp_Appendix.docx`; Source Data MOESM4)

Paraphrased with page and figure references (direct quotation is kept to one short phrase).

**Risk class definitions (main text, p. 1727, paragraph after Fig. 1 discussion; Fig. 2a legend).**
- Unit: the **sample** (one pooled biopsy from one level of one endoscopy), using the leave-one-patient-out probability Pr of each sample in the discovery cohort (n = 773 samples, 88 patients).
- Low: Pr ≤ 0.3. Moderate: 0.3 < Pr < 0.5 (printed in the paper as "0.3 > Pr < 0.5", read here as 0.3 < Pr < 0.5). High: Pr ≥ 0.5. Low is inclusive at 0.3; high is inclusive at 0.5.
- The thresholds were set from the enrichment of progressor vs non-progressor samples across predicted risk, to maximise sensitivity (p. 1727; Fig. 2a inset).
- **These definitions match the task's primary thresholds; no change is needed.**

**Metrics reported for the risk classes, with unit and population.**
1. Sensitivity and specificity at each class boundary, per sample, discovery cohort, label = patient status P/NP: at Pr ≤ 0.3 vs above (sensitivity 0.87, specificity 0.65) and at Pr ≥ 0.5 vs below (sensitivity 0.72, specificity 0.82) (p. 1727). Extended Data Fig. 2a,b gives AUC, sensitivity and specificity at Pr = 0.3 with 95% CIs, per sample and aggregated as mean/max per endoscopy and per patient (patient aggregation excludes the final HGD/IMC samples).
2. Proportion of samples in each class by patient status and by sample pathology (Fig. 2b, discovery, 773 samples; Fig. 2c, validation, 213 samples; Extended Data Fig. 10 for other bin sizes; 50 kb discovery: non-progressor samples 0.65 low / 0.17 moderate / 0.18 high, progressor samples 0.13 / 0.15 / 0.72). Headline figures: in NDBE samples, 60.5% (104/172) of progressor samples are high risk and 64.7% (224/346) of non-progressor samples are low risk (p. 1727). Validation: 55% (78/142) of non-progressor samples low, 77% (55/71) of progressor samples high (p. 1727).
3. Relative risk: a histogram of per-sample log(RR) (Fig. 2a), with an inset calibration plot of the observed progressor:non-progressor sample ratio against the mean predicted probability by decile, with 95% CIs (Fig. 2a inset). Relative risk is not reported per class.
4. Endoscopy-level sensitivity: for progressors, the share of endoscopies whose highest-risk sample is high risk, by months before the endpoint (> 96, 72–96, 45–72, 24–48, 12–24, 1–12 months, endpoint), with n endoscopies and samples per bar (Fig. 3b; p. 1727: 50% of endoscopies ≥ 8 years before HGD/IMC had at least one high-risk sample).
5. Patient-level management recommendations derived from the classes at the second and penultimate endoscopy (Fig. 4b; Supplementary Table 4).
- **Not reported:** no C-index, no Brier score, no Kaplan–Meier curves, no hazard ratios or Cox models, no per-class relative risk or odds ratio; calibration only as the decile inset of Fig. 2a.

## Models and data

- **(P)** Killcoyne's published probabilities: MOESM4 'Supporting data for Figure 2a' `Probability` (= `k_prob` in the sample table, identical; `docs/paper_horizon_q2_all_horizons.md`). These are their leave-one-patient-out predictions from a model trained on all 773 samples; they are **not** cross-validated within our folds and their training population differs from ours.
- **(C)** L-CNV and **(L)** L-LATE, their CNV matrix (primary); package-feature versions of C and L as sensitivity. Stored out-of-fold predictions (`feasibility/paper_plan/killcoyne_mm/cv/preds/`, `kv_cv.R`, d69de24), averaged over the 10 repeats per sample; L-LATE = per-repeat mean of L-CNV and L-IMG, then averaged.
- **Section 4 only:** L-IMG (WSI), L-EARLY, L-INTER (`hz_fit.R` outer, 4d7efa9), Pathology grade (raw score: NDBE 0, ID 1, LGD 2), and an intercept-only reference (training-fold prevalence) to show the size of the fold-prevalence artefact on the pooled metrics.
- **Populations:** primary all pre-event samples (571 samples, 75 patients, 32 progressors: samples before the first HGD/IMC; all non-progressor samples); secondary NDBE pre-event samples (438 samples, 71 patients). For Section 2's replication of Killcoyne's metrics (Step 0 items 1, 2, 4) also all 676 samples, because Killcoyne computed them on all samples including HGD/IMC.
- **Time:** years from the sample to HGD/IMC diagnosis (progressors) or censoring at the last endoscopy (non-progressors), `horizons/samples.csv` (`hz_prep.py`).

## 1. Risk classes

- Primary: Killcoyne thresholds applied unchanged to each model's probability (low ≤ 0.3, moderate 0.3–0.5 exclusive, high ≥ 0.5).
- Sensitivity, class-size matched: for C and L, cut-points at the quantiles of each model's score that reproduce the low / moderate / high proportions of (P) under the primary thresholds in the same population (computed on that population; this is a ranking comparison, not a prediction rule).
- Per model, scheme and population: samples, patients, events (progressor samples and patients) per class.

## 2. Separation (replicating Killcoyne, plus survival)

Per model (P, C, L; package versions of C and L) and class scheme:
- **Killcoyne's metrics (Step 0):** (i) sensitivity and specificity at the 0.3 and 0.5 boundaries, per sample, label = progressor status; (ii) proportion of progressor and non-progressor samples in each class, overall and in NDBE samples; (iii) decile calibration as in Fig. 2a inset (observed P:NP sample ratio and mean predicted probability per decile of predicted probability); (iv) endoscopy-level sensitivity: share of progressor endoscopies whose highest-scoring sample is high risk, by months before endpoint (> 96, 72–96, 48–72, 24–48, 12–24, 1–12 months, and the endpoint endoscopy where the population contains it). Computed on all 676 samples (as Killcoyne) and on the primary population; patient-bootstrap 95% CIs (2,000 draws, `RandomState(0)`).
- **Cox model** on class (low = reference), sample level, progression-free time, Breslow ties, robust (sandwich) variance clustered by patient: HR moderate vs low and high vs low with 95% CI; a class with no events → HR not estimable, reported as such. **Log-rank trend test** across the ordered classes (scores 0, 1, 2; samples treated as independent, so also reported: the cluster-robust Wald p of class as a single ordinal covariate).
- **Paired comparisons** L vs C and L vs P: difference in log HR (high vs low) and in the proportion of events (progressor samples with an observed event) falling in the high class; 2,000 patient-bootstrap draws (`RandomState(0)`, Cox refitted per draw without the robust variance), two-sided percentile CI, bootstrap p = 2·min(share ≤ 0, share ≥ 0). Unadjusted; labelled as such.

## 3. Kaplan–Meier figure

- Primary: sample-level KM of progression-free time by risk class (primary thresholds), one panel per model (P, C, L; their matrix), shared axes 0–10 years, numbers at risk under each panel at 0, 2, 4, 6, 8 years; pointwise 95% bands from the 2,000 patient-bootstrap draws (not Greenwood, samples are clustered). Colours as `be_paper_figs/v3` (blue low, orange moderate, red high), n / events in each panel title.
- Secondary (supplementary): patient-level KM using each patient's earliest pre-event sample (class of that sample).
- Output: `~/Downloads/be_paper_figs/v3/10_F_risk_KM.pdf` and `.png`; secondary `10_F_risk_KM_patient_supplementary.pdf` / `.png`; numbers in JSON.

## 4. Discrimination and accuracy

Per model (P, C, L, WSI, early fusion, inter fusion, pathology grade; package versions of C and L; intercept-only reference), all pre-event samples and NDBE pre-event samples:
- Per-sample AUROC on the ever-progression label: fold-stratified (same-fold pairs per repeat, mean over repeats; `kf_stats.py` `fs_auc`) for the cross-validated models; plain AUROC for (P) and grade (not cross-validated in our folds).
- Harrell's C and Uno's C, truncation at τ = 8 years, on the repeat-averaged scores; patient-bootstrap CI; paired Δ L vs C.
- IPCW Brier score at 1, 3 and 5 years and integrated Brier score over 0–5 years (Graf et al.; censoring weights from the reverse Kaplan–Meier over the evaluated samples, re-estimated per bootstrap draw), with the Kaplan–Meier null model (predicted P(event by t) = 1 − KM(t) for everyone) as reference. Each model's probability is used as its predicted P(event by t) at every t, because the models predict ever-progression, not a time-specific risk; stated as a limitation. Paired Δ L vs C for C-indices and the integrated Brier score, patient bootstrap.
- Table caveat: matched case–control cohort, so Brier values compare models with each other and do not measure real-world calibration.

## Answers (one line each, in the results)

1. Are the results good enough to split into low / moderate / high like Killcoyne? (For L: does the high class carry a clearly higher event rate than the low class, with a CI excluding no effect?)
2. Does late fusion separate better than CNV and than Killcoyne's published model? (Section 2 paired Δ, both class schemes.)
3. C-index and Brier: does L beat C?

## Output

`docs/paper_risk_strata.md`; script `scripts/paper_plan/rs_strata.py` (Slurm via `scripts/cluster/campaign.sh`, prefix rs, one task per section × population); render `scripts/paper_plan/rs_render.py`, figure `scripts/paper_plan/rs_km_fig.py`; aggregates `results/paper_final/risk_strata/`.

---

## Results

Pre-specification commit b1f788a; results commit 86be57d. Scripts `scripts/paper_plan/rs_strata.py` (Slurm via `scripts/cluster/campaign.sh`, prefixes rs, rs2), `rs_km_fig.py`, `rs_render.py`. Results `results/paper_final/risk_strata/{sep_all676,sep_pre,sep_pre_ndbe,disc_pre,disc_pre_ndbe,km}.json`; figure numbers `results/paper_final/risk_strata/figs/10_F_risk_KM.json`; figures `~/Downloads/be_paper_figs/v3/10_F_risk_KM.{pdf,png}`, `10_F_risk_KM_patient_supplementary.{pdf,png}`.

Population: the 676 samples from 80 patients of the Killcoyne discovery cohort with a matched H&E slide; primary analyses on its pre-event samples (571 samples, 75 patients, 161 samples with an observed event, 32 progressor patients).

### Status

| Item | Status |
|---|---|
| Step 0 (Killcoyne's definitions and metrics) | DONE (above; definitions match, no change) |
| 1 Risk classes (primary, class-size matched) | DONE |
| 2 Separation: Killcoyne metrics, Cox, trend, paired Δ | DONE (Cox ties deviate, see Deviations) |
| 3 Kaplan–Meier figure (sample level; patient level supplementary) | DONE |
| 4 Discrimination and accuracy | DONE (Brier not reported for grade, which is not a probability) |

### Answers

1. **Yes, for late fusion the classes separate clearly:** on pre-event samples the high class holds 107/132 samples with an observed progression against 26/332 in the low class, HR high vs low 11.64 [5.79, 23.42] (patient-clustered), and the same holds on NDBE samples (HR 8.05 [3.79, 17.13]); the moderate class is not separable from low on NDBE samples (HR 2.00 [0.89, 4.49]).
2. **Better than CNV, not clearly better than Killcoyne's published model:** L vs C, Δ log HR (high vs low) +0.635 [+0.016, +1.282] and Δ share of events in the high class +0.137 [+0.022, +0.269] (primary thresholds; class-size matched +0.843 [+0.128, +1.656] and +0.168 [+0.062, +0.253]); L vs P, Δ log HR +0.359 [-0.455, +1.060] (primary) and +0.486 [-0.325, +1.284] (matched), with only the matched-scheme event share favouring L (+0.124 [+0.026, +0.208]); all unadjusted.
3. **Yes on all pre-event samples, L beats C on C-index and Brier:** Harrell's C 0.825 vs 0.764 (Δ +0.061 [+0.008, +0.124]), Uno's C Δ +0.058 [+0.004, +0.120], integrated Brier 0–5 years 0.152 vs 0.181 (Δ -0.028 [-0.055, -0.004]); but no model's integrated Brier beats the Kaplan–Meier null (0.121), because ever-progression probabilities are used as time-specific risks; on NDBE samples the C-index differences are not significant (+0.036 [-0.012, +0.098]).

### 1. Risk classes

Samples / patients / samples with an observed event, per class. Class-size matched cut-points reproduce (P)'s proportions: pre-event 0.52, 0.18, 0.30 (low, moderate, high); NDBE 0.56, 0.18, 0.27.

**All pre-event samples (571 / 75)**

| Model | Scheme | Low | Moderate | High | Cut-points (low/moderate, moderate/high) |
|---|---|---|---|---|---|
| Killcoyne published (P) | primary | 298 / 50 / 28 | 103 / 39 / 30 | 170 / 43 / 103 | 0.30, 0.50 |
| CNV, their matrix (C) | primary | 315 / 55 / 36 | 121 / 38 / 40 | 135 / 41 / 85 | 0.30, 0.50 |
| CNV, their matrix (C) | matched | 298 / 54 / 35 | 103 / 39 / 30 | 170 / 45 / 96 | 0.27, 0.44 |
| Late fusion, their matrix (L) | primary | 332 / 56 / 26 | 107 / 46 / 28 | 132 / 43 / 107 | 0.30, 0.50 |
| Late fusion, their matrix (L) | matched | 298 / 50 / 17 | 103 / 39 / 21 | 170 / 54 / 123 | 0.26, 0.41 |
| CNV, package features | primary | 333 / 49 / 31 | 86 / 36 / 33 | 152 / 40 / 97 | 0.30, 0.50 |
| CNV, package features | matched | 298 / 46 / 22 | 103 / 42 / 34 | 170 / 45 / 105 | 0.21, 0.46 |
| Late fusion, package features | primary | 331 / 51 / 22 | 113 / 46 / 34 | 127 / 44 / 105 | 0.30, 0.50 |
| Late fusion, package features | matched | 298 / 48 / 15 | 103 / 45 / 25 | 170 / 53 / 121 | 0.24, 0.41 |

**NDBE pre-event samples (438 / 71)**

| Model | Scheme | Low | Moderate | High | Cut-points |
|---|---|---|---|---|---|
| Killcoyne published (P) | primary | 243 / 47 / 23 | 77 / 34 / 21 | 118 / 38 / 60 | 0.30, 0.50 |
| CNV, their matrix (C) | primary | 261 / 51 / 27 | 85 / 34 / 27 | 92 / 32 / 50 | 0.30, 0.50 |
| CNV, their matrix (C) | matched | 243 / 50 / 26 | 77 / 34 / 22 | 118 / 37 / 56 | 0.25, 0.44 |
| Late fusion, their matrix (L) | primary | 273 / 54 / 22 | 80 / 37 / 19 | 85 / 38 / 63 | 0.30, 0.50 |
| Late fusion, their matrix (L) | matched | 243 / 48 / 15 | 77 / 32 / 14 | 118 / 48 / 75 | 0.25, 0.40 |
| CNV, package features | primary | 267 / 47 / 25 | 64 / 30 / 20 | 107 / 35 / 59 | 0.30, 0.50 |
| CNV, package features | matched | 243 / 47 / 18 | 77 / 35 / 23 | 118 / 38 / 63 | 0.23, 0.47 |
| Late fusion, package features | primary | 268 / 48 / 18 | 89 / 41 / 25 | 81 / 39 / 61 | 0.30, 0.50 |
| Late fusion, package features | matched | 243 / 45 / 13 | 77 / 42 / 20 | 118 / 47 / 71 | 0.25, 0.40 |

### 2. Separation

**Killcoyne's metrics, recomputed** (per sample, label = progressor status; patient-bootstrap 95% CIs). Killcoyne reported, on 773 samples: sensitivity / specificity 0.87 / 0.65 at Pr ≤ 0.3 and 0.72 / 0.82 at Pr ≥ 0.5; 60.5% of progressor NDBE samples high and 64.7% of non-progressor NDBE samples low.

| Population | Model | Sens / spec, low vs above (Pr > 0.3) | Sens / spec, high (Pr ≥ 0.5) vs below | Progressor NDBE samples high | Non-progressor NDBE samples low |
|---|---|---|---|---|---|
| all 676 samples | Killcoyne published (P) | 0.876 [0.782, 0.942] / 0.659 [0.552, 0.774] | 0.726 [0.626, 0.814] / 0.837 [0.750, 0.917] | 0.612 (n 129) | 0.659 (n 334) |
| all 676 samples | CNV, their matrix (C) | 0.835 [0.736, 0.909] / 0.680 [0.569, 0.798] | 0.639 [0.527, 0.739] / 0.878 [0.801, 0.945] | 0.535 (n 129) | 0.701 (n 334) |
| all 676 samples | Late fusion, their matrix (L) | 0.887 [0.814, 0.943] / 0.746 [0.664, 0.821] | 0.737 [0.651, 0.812] / 0.939 [0.904, 0.969] | 0.628 (n 129) | 0.751 (n 334) |
| all 676 samples | CNV, package features | 0.865 [0.787, 0.928] / 0.737 [0.617, 0.848] | 0.699 [0.592, 0.807] / 0.866 [0.764, 0.948] | 0.620 (n 129) | 0.725 (n 334) |
| all 676 samples | Late fusion, package features | 0.906 [0.837, 0.962] / 0.754 [0.652, 0.842] | 0.733 [0.645, 0.817] / 0.946 [0.912, 0.972] | 0.620 (n 129) | 0.749 (n 334) |
| pre-event | Killcoyne published (P) | 0.826 [0.697, 0.925] / 0.659 [0.543, 0.775] | 0.640 [0.514, 0.752] / 0.837 [0.744, 0.916] | 0.577 (n 104) | 0.659 (n 334) |
| pre-event | CNV, their matrix (C) | 0.776 [0.645, 0.879] / 0.680 [0.569, 0.796] | 0.528 [0.399, 0.656] / 0.878 [0.799, 0.942] | 0.481 (n 104) | 0.701 (n 334) |
| pre-event | Late fusion, their matrix (L) | 0.839 [0.743, 0.918] / 0.746 [0.663, 0.820] | 0.665 [0.560, 0.766] / 0.939 [0.902, 0.969] | 0.606 (n 104) | 0.751 (n 334) |
| pre-event | CNV, package features | 0.807 [0.699, 0.901] / 0.737 [0.608, 0.840] | 0.602 [0.453, 0.744] / 0.866 [0.765, 0.948] | 0.567 (n 104) | 0.725 (n 334) |
| pre-event | Late fusion, package features | 0.863 [0.771, 0.942] / 0.754 [0.652, 0.838] | 0.652 [0.530, 0.768] / 0.946 [0.913, 0.972] | 0.587 (n 104) | 0.749 (n 334) |

**Endoscopy-level sensitivity** (Fig. 3b of Killcoyne): share of progressor endoscopies whose highest-scoring sample is high risk, by months before the endpoint, all 676 samples (endoscopies in parentheses). Killcoyne (p. 1727): 50% of endoscopies at least 8 years before HGD/IMC had at least one high-risk sample; their Fig. 3b labels the fourth bin 45–72 months, the pre-specification uses 48–72.

| Model | endpoint | 1-12 | 12-24 | 24-48 | 48-72 | 72-96 | >96 |
|---|---|---|---|---|---|---|---|
| Killcoyne published (P) | 0.92 (24) | 1.00 (12) | 0.67 (15) | 0.67 (24) | 0.65 (17) | 0.38 (8) | 0.42 (12) |
| CNV, their matrix (C) | 0.92 (24) | 1.00 (12) | 0.47 (15) | 0.62 (24) | 0.53 (17) | 0.38 (8) | 0.50 (12) |
| Late fusion, their matrix (L) | 0.88 (24) | 0.92 (12) | 0.93 (15) | 0.71 (24) | 0.65 (17) | 0.75 (8) | 0.50 (12) |

**Decile calibration** (Fig. 2a inset of Killcoyne): progressor:non-progressor samples (mean predicted probability) per decile of predicted probability, all 676 samples.

| Model | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Killcoyne published (P) | 2:66 (0.01) | 7:61 (0.05) | 11:56 (0.11) | 6:62 (0.18) | 12:55 (0.30) | 30:38 (0.42) | 30:37 (0.55) | 45:23 (0.72) | 59:8 (0.90) | 64:4 (0.99) |
| CNV, their matrix (C) | 3:65 (0.02) | 10:58 (0.06) | 4:63 (0.11) | 17:51 (0.17) | 16:51 (0.27) | 25:43 (0.38) | 34:33 (0.48) | 40:28 (0.62) | 51:16 (0.80) | 66:2 (0.96) |
| Late fusion, their matrix (L) | 0:68 (0.03) | 3:65 (0.07) | 1:66 (0.13) | 11:57 (0.20) | 15:52 (0.27) | 16:52 (0.35) | 37:30 (0.47) | 54:14 (0.60) | 61:6 (0.75) | 68:0 (0.94) |

**Cox model on class** (low = reference; sample level; patient-clustered robust variance) and **log-rank trend test** (samples treated as independent) with the cluster-robust ordinal-class Cox as the clustered counterpart.

| Population | Model | Scheme | HR moderate vs low [95% CI] | HR high vs low [95% CI] | Log-rank trend | Ordinal class HR per step (robust) [CI] |
|---|---|---|---|---|---|---|
| pre-event | Killcoyne published (P) | primary | 3.78 [1.56, 9.13] | 7.90 [3.51, 17.79] | z 11.14, p < 1e-15 | 2.70 [1.89, 3.87], p 5.6e-08 |
| pre-event | CNV, their matrix (C) | primary | 3.69 [1.87, 7.29] | 5.98 [2.91, 12.30] | z 9.93, p < 1e-15 | 2.35 [1.68, 3.28], p 4.9e-07 |
| pre-event | CNV, their matrix (C) | matched | 2.98 [1.45, 6.13] | 5.49 [2.66, 11.31] | z 9.47, p < 1e-15 | 2.29 [1.62, 3.22], p 2.2e-06 |
| pre-event | Late fusion, their matrix (L) | primary | 2.71 [1.32, 5.56] | 11.64 [5.79, 23.42] | z 13.65, p < 1e-15 | 3.54 [2.50, 5.01], p 8.9e-13 |
| pre-event | Late fusion, their matrix (L) | matched | 2.71 [1.06, 6.96] | 13.11 [5.32, 32.34] | z 12.99, p < 1e-15 | 3.86 [2.49, 5.99], p 1.6e-09 |
| pre-event | CNV, package features | primary | 4.43 [1.95, 10.07] | 8.07 [3.62, 17.98] | z 11.59, p < 1e-15 | 2.71 [1.88, 3.89], p 7.8e-08 |
| pre-event | CNV, package features | matched | 5.14 [1.98, 13.36] | 9.46 [4.06, 22.06] | z 11.45, p < 1e-15 | 2.84 [1.96, 4.11], p 3.0e-08 |
| pre-event | Late fusion, package features | primary | 3.89 [1.79, 8.47] | 13.61 [5.79, 31.99] | z 13.89, p < 1e-15 | 3.65 [2.43, 5.48], p 4.3e-10 |
| pre-event | Late fusion, package features | matched | 4.80 [2.39, 9.64] | 14.12 [5.82, 34.29] | z 12.63, p < 1e-15 | 3.56 [2.38, 5.34], p 7.8e-10 |
| NDBE pre-event | Killcoyne published (P) | primary | 3.68 [1.36, 9.97] | 5.61 [2.17, 14.48] | z 7.73, p 1.1e-14 | 2.27 [1.50, 3.44], p 1.0e-04 |
| NDBE pre-event | CNV, their matrix (C) | primary | 3.90 [1.74, 8.71] | 4.78 [1.99, 11.46] | z 7.15, p 8.9e-13 | 2.10 [1.43, 3.10], p 1.7e-04 |
| NDBE pre-event | CNV, their matrix (C) | matched | 3.38 [1.41, 8.15] | 4.42 [1.83, 10.67] | z 6.74, p 1.6e-11 | 2.03 [1.36, 3.02], p 4.7e-04 |
| NDBE pre-event | Late fusion, their matrix (L) | primary | 2.00 [0.89, 4.49] | 8.05 [3.79, 17.13] | z 9.60, p < 1e-15 | 2.96 [2.02, 4.34], p 2.6e-08 |
| NDBE pre-event | Late fusion, their matrix (L) | matched | 2.19 [0.77, 6.26] | 8.44 [3.14, 22.69] | z 9.11, p < 1e-15 | 3.04 [1.89, 4.90], p 4.4e-06 |
| NDBE pre-event | CNV, package features | primary | 3.10 [1.27, 7.59] | 6.12 [2.59, 14.46] | z 8.35, p < 1e-15 | 2.43 [1.61, 3.66], p 2.1e-05 |
| NDBE pre-event | CNV, package features | matched | 4.00 [1.46, 10.98] | 6.90 [2.87, 16.58] | z 8.24, p < 1e-15 | 2.50 [1.66, 3.75], p 1.1e-05 |
| NDBE pre-event | Late fusion, package features | primary | 3.37 [1.39, 8.19] | 9.66 [3.80, 24.58] | z 9.89, p < 1e-15 | 3.07 [1.99, 4.74], p 4.4e-07 |
| NDBE pre-event | Late fusion, package features | matched | 4.55 [2.04, 10.12] | 9.39 [3.52, 25.05] | z 8.90, p < 1e-15 | 2.85 [1.87, 4.37], p 1.3e-06 |

**Paired comparisons** (2,000 patient-bootstrap draws, Cox refitted per draw with Breslow ties; draws with no event in the low or high class dropped; unadjusted).

| Population | Comparison | Scheme | Δ log HR high vs low [CI], p | Δ share of events in the high class [CI], p |
|---|---|---|---|---|
| pre-event | L vs C | primary | +0.635 [+0.016, +1.282], p 0.0474 (1984 draws) | +0.137 [+0.022, +0.269], p 0.024 |
| pre-event | L vs P | primary | +0.359 [-0.455, +1.060], p 0.4093 (1984 draws) | +0.025 [-0.075, +0.130], p 0.665 |
| pre-event | L (package) vs C (package) | primary | +0.497 [-0.080, +1.147], p 0.0941 (1976 draws) | +0.050 [-0.057, +0.163], p 0.395 |
| pre-event | L (package) vs P | primary | +0.514 [-0.473, +1.495], p 0.3421 (1976 draws) | +0.012 [-0.113, +0.136], p 0.854 |
| pre-event | L vs C | matched | +0.843 [+0.128, +1.656], p 0.02 (2000 draws) | +0.168 [+0.062, +0.253], p 0.001 |
| pre-event | L vs P | matched | +0.486 [-0.325, +1.284], p 0.259 (2000 draws) | +0.124 [+0.026, +0.208], p 0.019 |
| pre-event | L (package) vs C (package) | matched | +0.391 [-0.355, +1.161], p 0.2431 (1999 draws) | +0.099 [+0.017, +0.203], p 0.022 |
| pre-event | L (package) vs P | matched | +0.567 [-0.524, +1.886], p 0.3452 (1999 draws) | +0.112 [+0.010, +0.225], p 0.033 |
| NDBE pre-event | L vs C | primary | +0.481 [-0.199, +1.184], p 0.1692 (1998 draws) | +0.125 [-0.009, +0.272], p 0.082 |
| NDBE pre-event | L vs P | primary | +0.324 [-0.696, +1.089], p 0.5265 (1998 draws) | +0.029 [-0.084, +0.156], p 0.749 |
| NDBE pre-event | L (package) vs C (package) | primary | +0.432 [-0.155, +1.143], p 0.1486 (1992 draws) | +0.019 [-0.097, +0.128], p 0.847 |
| NDBE pre-event | L (package) vs P | primary | +0.509 [-0.667, +1.586], p 0.4106 (1992 draws) | +0.010 [-0.146, +0.173], p 0.987 |
| NDBE pre-event | L vs C | matched | +0.616 [+0.016, +1.663], p 0.0451 (1997 draws) | +0.183 [+0.063, +0.294], p 0.003 |
| NDBE pre-event | L vs P | matched | +0.385 [-0.389, +1.390], p 0.2804 (1997 draws) | +0.144 [+0.023, +0.263], p 0.014 |
| NDBE pre-event | L (package) vs C (package) | matched | +0.300 [-0.316, +1.193], p 0.2817 (1995 draws) | +0.077 [-0.010, +0.206], p 0.093 |
| NDBE pre-event | L (package) vs P | matched | +0.496 [-0.752, +1.761], p 0.5003 (1995 draws) | +0.106 [-0.009, +0.262], p 0.084 |

### 3. Kaplan–Meier

Figure `10_F_risk_KM` (sample level, primary) and `10_F_risk_KM_patient_supplementary` (patient level: each patient's earliest pre-event sample). Primary thresholds; 95% patient-bootstrap bands.

| Level | Model | Class | n / events | At risk at 0 / 2 / 4 / 6 / 8 years | Progression-free at 2 / 4 / 6 / 8 years |
|---|---|---|---|---|---|
| sample | Killcoyne published (P) | low | 298 / 28 | 298 / 226 / 139 / 82 / 43 | 0.94 / 0.92 / 0.92 / 0.88 |
| sample | Killcoyne published (P) | moderate | 103 / 30 | 103 / 72 / 48 / 20 / 7 | 0.93 / 0.77 / 0.56 / 0.32 |
| sample | Killcoyne published (P) | high | 170 / 103 | 170 / 113 / 57 / 33 / 20 | 0.65 / 0.45 / 0.29 / 0.26 |
| sample | CNV, their matrix (C) | low | 315 / 36 | 315 / 233 / 150 / 86 / 43 | 0.93 / 0.91 / 0.87 / 0.81 |
| sample | CNV, their matrix (C) | moderate | 121 / 40 | 121 / 85 / 46 / 18 / 7 | 0.82 / 0.65 / 0.49 / 0.35 |
| sample | CNV, their matrix (C) | high | 135 / 85 | 135 / 93 / 48 / 31 / 20 | 0.69 / 0.47 / 0.32 / 0.27 |
| sample | Late fusion, their matrix (L) | low | 332 / 26 | 332 / 241 / 152 / 78 / 38 | 0.97 / 0.93 / 0.88 / 0.85 |
| sample | Late fusion, their matrix (L) | moderate | 107 / 28 | 107 / 82 / 51 / 32 / 20 | 0.89 / 0.80 / 0.68 / 0.62 |
| sample | Late fusion, their matrix (L) | high | 132 / 107 | 132 / 88 / 41 / 25 / 12 | 0.58 / 0.35 / 0.22 / 0.14 |
| patient | Killcoyne published (P) | low | 40 / 8 | 40 / 39 / 31 / 23 / 16 | 0.93 / 0.90 / 0.90 / 0.90 |
| patient | Killcoyne published (P) | moderate | 13 / 7 | 13 / 13 / 12 / 7 / 3 | 1.00 / 0.85 / 0.54 / 0.36 |
| patient | Killcoyne published (P) | high | 22 / 17 | 22 / 18 / 14 / 8 / 4 | 0.82 / 0.59 / 0.33 / 0.26 |
| patient | CNV, their matrix (C) | low | 43 / 11 | 43 / 42 / 35 / 26 / 18 | 0.93 / 0.91 / 0.84 / 0.80 |
| patient | CNV, their matrix (C) | moderate | 11 / 4 | 11 / 11 / 9 / 4 / 0 | 1.00 / 0.81 / 0.40 / 0.40 |
| patient | CNV, their matrix (C) | high | 21 / 17 | 21 / 17 / 13 / 8 / 5 | 0.81 / 0.57 / 0.37 / 0.31 |
| patient | Late fusion, their matrix (L) | low | 42 / 8 | 42 / 42 / 35 / 22 / 14 | 0.98 / 0.92 / 0.85 / 0.79 |
| patient | Late fusion, their matrix (L) | moderate | 12 / 6 | 12 / 11 / 9 / 8 / 5 | 0.83 / 0.75 / 0.66 / 0.66 |
| patient | Late fusion, their matrix (L) | high | 21 / 18 | 21 / 17 / 13 / 8 / 4 | 0.81 / 0.57 / 0.31 / 0.25 |

### 4. Discrimination and accuracy

**Caveat:** matched case–control cohort, so Brier values compare models with each other and do not measure real-world calibration; each model's ever-progression probability is used as its predicted risk at every horizon. Lower Brier is better.

**All pre-event samples** (571 samples, 75 patients, 161 samples with an event).

| Model | AUROC ever-progression [CI] (type) | Harrell's C (τ 8 y) | Uno's C (τ 8 y) | Brier 1 y | Brier 3 y | Brier 5 y | Integrated Brier 0–5 y |
|---|---|---|---|---|---|---|---|
| Killcoyne published (P) | 0.828 [0.730, 0.904] (plain) | 0.791 [0.719, 0.859] | 0.794 [0.714, 0.860] | 0.217 [0.156, 0.286] | 0.186 [0.133, 0.244] | 0.183 [0.119, 0.257] | 0.205 [0.151, 0.265] |
| CNV, their matrix (C) | 0.801 [0.710, 0.875] (fold-stratified) | 0.764 [0.686, 0.835] | 0.765 [0.686, 0.837] | 0.179 [0.129, 0.231] | 0.171 [0.128, 0.217] | 0.181 [0.131, 0.231] | 0.181 [0.137, 0.228] |
| Late fusion, their matrix (L) | 0.889 [0.830, 0.934] (fold-stratified) | 0.825 [0.766, 0.878] | 0.823 [0.765, 0.873] | 0.161 [0.123, 0.203] | 0.138 [0.107, 0.171] | 0.151 [0.119, 0.181] | 0.152 [0.122, 0.184] |
| WSI (L-IMG) | 0.847 [0.798, 0.894] (fold-stratified) | 0.779 [0.712, 0.838] | 0.770 [0.709, 0.833] | 0.204 [0.160, 0.254] | 0.171 [0.129, 0.216] | 0.195 [0.149, 0.242] | 0.188 [0.152, 0.229] |
| Early fusion | 0.865 [0.787, 0.928] (fold-stratified) | 0.804 [0.736, 0.871] | 0.809 [0.742, 0.868] | 0.189 [0.132, 0.253] | 0.164 [0.115, 0.221] | 0.182 [0.131, 0.239] | 0.183 [0.133, 0.239] |
| Inter fusion | 0.832 [0.761, 0.899] (fold-stratified) | 0.778 [0.705, 0.852] | 0.771 [0.692, 0.844] | 0.215 [0.154, 0.285] | 0.179 [0.124, 0.235] | 0.211 [0.151, 0.275] | 0.205 [0.150, 0.265] |
| Pathology grade (raw score) | 0.598 [0.525, 0.671] (plain) | 0.586 [0.511, 0.663] | 0.570 [0.501, 0.635] | n/a | n/a | n/a | n/a |
| CNV, package features | 0.845 [0.766, 0.904] (fold-stratified) | 0.765 [0.689, 0.832] | 0.776 [0.693, 0.845] | 0.190 [0.133, 0.257] | 0.190 [0.137, 0.246] | 0.195 [0.136, 0.257] | 0.195 [0.140, 0.255] |
| Late fusion, package features | 0.903 [0.856, 0.944] (fold-stratified) | 0.817 [0.752, 0.873] | 0.823 [0.758, 0.879] | 0.167 [0.126, 0.214] | 0.148 [0.112, 0.188] | 0.159 [0.120, 0.200] | 0.160 [0.123, 0.199] |
| Early fusion, package | 0.885 [0.822, 0.937] (fold-stratified) | 0.793 [0.723, 0.860] | 0.797 [0.722, 0.864] | 0.202 [0.142, 0.272] | 0.185 [0.130, 0.244] | 0.199 [0.137, 0.264] | 0.199 [0.142, 0.256] |
| Inter fusion, package | 0.871 [0.812, 0.922] (fold-stratified) | 0.787 [0.722, 0.846] | 0.786 [0.720, 0.847] | 0.230 [0.166, 0.301] | 0.193 [0.139, 0.248] | 0.210 [0.153, 0.271] | 0.216 [0.162, 0.276] |
| Intercept-only (reference) | 0.500 [0.500, 0.500] (fold-stratified) | 0.316 [0.219, 0.427] | 0.292 [0.205, 0.400] | 0.168 [0.162, 0.176] | 0.202 [0.187, 0.221] | 0.221 [0.199, 0.243] | 0.186 [0.176, 0.199] |
| Kaplan–Meier null | — | — | — | 0.057 [0.031, 0.089] | 0.176 [0.129, 0.215] | 0.215 [0.171, 0.238] | 0.121 [0.087, 0.150] |

**NDBE pre-event samples** (438 samples, 71 patients, 104 with an event).

| Model | AUROC ever-progression [CI] (type) | Harrell's C (τ 8 y) | Uno's C (τ 8 y) | Brier 1 y | Brier 3 y | Brier 5 y | Integrated Brier 0–5 y |
|---|---|---|---|---|---|---|---|
| Killcoyne published (P) | 0.788 [0.667, 0.897] (plain) | 0.773 [0.677, 0.862] | 0.777 [0.688, 0.857] | 0.203 [0.142, 0.271] | 0.188 [0.134, 0.250] | 0.200 [0.131, 0.282] | 0.202 [0.148, 0.265] |
| CNV, their matrix (C) | 0.780 [0.681, 0.879] (fold-stratified) | 0.759 [0.661, 0.849] | 0.759 [0.672, 0.842] | 0.167 [0.118, 0.223] | 0.165 [0.121, 0.212] | 0.191 [0.139, 0.247] | 0.175 [0.130, 0.223] |
| Late fusion, their matrix (L) | 0.867 [0.794, 0.931] (fold-stratified) | 0.795 [0.719, 0.869] | 0.800 [0.731, 0.862] | 0.149 [0.112, 0.194] | 0.139 [0.105, 0.176] | 0.166 [0.130, 0.207] | 0.150 [0.117, 0.185] |
| WSI (L-IMG) | 0.827 [0.768, 0.883] (fold-stratified) | 0.744 [0.671, 0.818] | 0.747 [0.672, 0.813] | 0.190 [0.145, 0.246] | 0.180 [0.133, 0.234] | 0.219 [0.162, 0.284] | 0.189 [0.146, 0.238] |
| Early fusion | 0.850 [0.753, 0.929] (fold-stratified) | 0.799 [0.718, 0.878] | 0.800 [0.729, 0.867] | 0.170 [0.121, 0.230] | 0.154 [0.109, 0.205] | 0.196 [0.144, 0.252] | 0.172 [0.128, 0.223] |
| Inter fusion | 0.833 [0.746, 0.911] (fold-stratified) | 0.779 [0.678, 0.876] | 0.766 [0.673, 0.857] | 0.190 [0.130, 0.260] | 0.169 [0.114, 0.230] | 0.219 [0.151, 0.294] | 0.189 [0.135, 0.250] |
| Pathology grade (raw score) | not estimable: grade is constant (NDBE) in this population | — | — | n/a | n/a | n/a | n/a |
| CNV, package features | 0.823 [0.733, 0.901] (fold-stratified) | 0.739 [0.648, 0.829] | 0.759 [0.665, 0.844] | 0.184 [0.128, 0.254] | 0.198 [0.141, 0.259] | 0.207 [0.144, 0.279] | 0.198 [0.141, 0.263] |
| Late fusion, package features | 0.879 [0.818, 0.935] (fold-stratified) | 0.778 [0.699, 0.853] | 0.792 [0.713, 0.864] | 0.158 [0.117, 0.212] | 0.157 [0.116, 0.202] | 0.178 [0.133, 0.230] | 0.164 [0.125, 0.208] |
| Early fusion, package | 0.863 [0.782, 0.929] (fold-stratified) | 0.757 [0.660, 0.847] | 0.766 [0.673, 0.855] | 0.189 [0.133, 0.261] | 0.193 [0.137, 0.255] | 0.224 [0.153, 0.297] | 0.201 [0.145, 0.265] |
| Inter fusion, package | 0.871 [0.798, 0.932] (fold-stratified) | 0.785 [0.704, 0.863] | 0.793 [0.714, 0.868] | 0.207 [0.146, 0.282] | 0.182 [0.129, 0.242] | 0.213 [0.148, 0.282] | 0.203 [0.147, 0.267] |
| Intercept-only (reference) | 0.500 [0.500, 0.500] (fold-stratified) | 0.329 [0.210, 0.461] | 0.310 [0.202, 0.439] | 0.163 [0.158, 0.168] | 0.196 [0.181, 0.214] | 0.215 [0.195, 0.238] | 0.180 [0.171, 0.191] |
| Kaplan–Meier null | — | — | — | 0.033 [0.014, 0.059] | 0.161 [0.113, 0.203] | 0.207 [0.161, 0.233] | 0.103 [0.071, 0.132] |

**Paired Δ** (2,000 patient-bootstrap draws, unadjusted; for Brier, negative favours the first model).

| Population | Comparison | Δ AUROC | Δ Harrell's C | Δ Uno's C | Δ integrated Brier |
|---|---|---|---|---|---|
| pre-event | L vs C | +0.087 [+0.037, +0.145], p 0.001 | +0.061 [+0.008, +0.124], p 0.022 | +0.058 [+0.004, +0.120], p 0.031 | -0.028 [-0.055, -0.004], p 0.022 |
| pre-event | L (package) vs C (package) | +0.058 [+0.016, +0.108], p 0.002 | +0.052 [+0.011, +0.100], p 0.014 | +0.047 [+0.008, +0.095], p 0.019 | -0.035 [-0.068, -0.007], p 0.01 |
| pre-event | L vs P | +0.061 [+0.005, +0.127], p 0.034 | +0.034 [-0.016, +0.091], p 0.193 | +0.029 [-0.026, +0.094], p 0.33 | -0.053 [-0.099, -0.016], p 0.001 |
| NDBE pre-event | L vs C | +0.087 [+0.034, +0.152], p < 0.0005 | +0.036 [-0.012, +0.098], p 0.177 | +0.041 [-0.014, +0.109], p 0.175 | -0.025 [-0.054, +0.003], p 0.08 |
| NDBE pre-event | L (package) vs C (package) | +0.056 [+0.014, +0.106], p 0.007 | +0.039 [-0.003, +0.085], p 0.064 | +0.033 [-0.009, +0.080], p 0.116 | -0.035 [-0.069, -0.005], p 0.02 |
| NDBE pre-event | L vs P | +0.079 [+0.008, +0.160], p 0.019 | +0.022 [-0.034, +0.091], p 0.498 | +0.024 [-0.039, +0.097], p 0.527 | -0.052 [-0.103, -0.012], p 0.005 |

The intercept-only reference scores Harrell's C 0.316 on pre-event samples: the pooled C-indices of the cross-validated models carry the stratified-CV fold-prevalence artefact (`docs/paper_horizon_answers.md`), which (P) and the raw grade do not; the AUROC column is fold-stratified for the cross-validated models and is free of it (intercept-only 0.500).

### Deviations from the pre-specification

- Cox HRs and their CIs: the pre-specified statsmodels PHReg with Breslow ties and patient-clustered robust variance returned non-finite robust standard errors (string and integer group labels), so every reported HR, CI and robust p uses the fallback built into the script: lifelines `CoxPHFitter`, Efron ties, patient-clustered sandwich variance (`cox.source` in the JSON). The paired bootstrap comparisons use statsmodels PHReg with Breslow ties as specified (point estimates only, no robust variance needed), so their point Δ log HR can differ slightly from the difference of the tabulated Efron HRs.
- The first run (prefix rs) of the two pre-event separation tasks returned NaN robust CIs and p-values; they were rerun with the fallback (prefix rs2). Class counts, Killcoyne metrics, trend tests and the paired bootstrap are identical between the two runs; the tabulated HR point estimates differ from the first run because of the Efron ties (e.g. L, high vs low, 10.85 with Breslow vs 11.64 with Efron). The all-676-samples task was not rerun: only its Killcoyne metrics are reported, and its Cox fields in `sep_all676.json` are the NaN-CI first-run values and are not used.
- Sensitivity and specificity CIs are given for the primary thresholds only; for the class-size matched scheme the cut-points are data-derived and no CI is given.

### Caveats

- (P) are Killcoyne's leave-one-patient-out predictions from a model trained on all 773 samples (their population, their features, hg19); they are not cross-validated in our folds and are not a like-for-like comparison with C and L.
- Samples are clustered within patients; sample-level KM and the log-rank trend test treat samples as independent (the bands and the ordinal Cox use patient clustering).
- Matched case–control design: event rates, KM curves and Brier values are not population risks; HRs compare classes within this cohort.


---

## Addendum A: fold-stratified C-index (pre-specification)

Status: PRE-SPECIFICATION (written 2026-10-07). Nothing below has been run. Results are appended under "### Addendum A results" in a later commit; this pre-specification and all sections above are not edited afterwards.

Ground rules as above: no refitting; the same stored fold-honest predictions; report only; at most one line of interpretation.

**Why.** The pooled C-indices in Section 4 compare samples from different outer folds, whose predictions come from different training sets; the intercept-only reference scores Harrell's C 0.316 on pre-event samples. Fold-stratified scoring removes that artefact, as fold-stratified AUROC did.

**Definition.**
- For each repeat r (1–10) and each outer fold k of that repeat, the comparable pairs are those whose two samples both sit in fold k of repeat r.
  - Comparable pair (as in Section 4): sample i has an observed event with t_i < τ = 8 years, and t_i < t_j.
  - Concordance uses repeat r's own out-of-fold predictions, not the repeat mean; tied predictions count 0.5.
- **Harrell's C** for repeat r = Σ over folds of concordant pairs / Σ over folds of comparable pairs, i.e. pooled within folds, like the fold-stratified AUROC. The reported value is the mean over the 10 repeats; folds with no comparable pair contribute nothing.
- **Uno's C:** as Harrell's, with each pair weighted by 1/G(t_i−)². G is the reverse Kaplan–Meier censoring distribution estimated on the whole population (the bootstrap draw, within the bootstrap), as in Section 4.
- **Folds:** the outer-fold assignment of the `kv_cv.R` predictions (cfg 0; d69de24). The script checks that every cross-validated model's stored fold column matches it, and reports the result.
  - If a model's folds differ, that model is scored on its own folds, and this is noted.
- **Check:** intercept-only (training-fold prevalence) must score 0.500 on both C-indices, because its predictions are constant within a fold. If it does not, the run is reported as failed and not interpreted.

**Models.**
- Cross-validated: C, L, WSI (L-IMG), early fusion, inter fusion, and the package-feature versions of C, L, early fusion and inter fusion.
- Not cross-validated: Killcoyne's published model (P) and pathology grade. These have no folds of their own.
  - For a like-for-like comparison they are scored on exactly the same within-fold pairs, i.e. with the same cfg-0 folds of each repeat, averaged over the 10 repeats. Their scores do not vary across repeats; only the pair set does.
  - Their pooled values from Section 4 stay as they are.

**Populations.** All pre-event samples (571 samples, 75 patients; primary) and NDBE pre-event samples (secondary). Grade is constant on NDBE samples, so it is reported there as not estimable.

**Inference.**
- 2,000 patient-bootstrap draws: the same draws as Section 4 (seed 0, draws without both a progressor and a non-progressor sample redrawn).
- A resampled patient keeps its fold in every repeat. The bootstrap statistic is recomputed per draw as defined above, giving percentile 95% CIs.
- **Paired Δ** on the same draws: L vs C and L vs P (main), plus L vs C on package features (as in Section 4), for both C-indices and both populations. Each Δ gets a percentile CI and an unadjusted two-sided bootstrap p.

**Reported.**
- The same table as Section 4 for the C-index columns: fold-stratified Harrell's and Uno's C with CIs per model and population, next to the pooled Section 4 values.
- The paired-Δ table.
- The fold-match check and the intercept-only check.
- One line: does the Section 4 answer to question 3 (L beats C on C-index) hold under fold-stratified scoring, and how does L compare with P?

**Output.**
- Script `scripts/paper_plan/rs_fsc.py`: TASK `fsc_pre` | `fsc_pre_ndbe`, run on Slurm via `scripts/cluster/campaign.sh`.
- Aggregates: `results/paper_final/risk_strata/fsc_pre.json` and `fsc_pre_ndbe.json`.
- Rendered by `scripts/paper_plan/rs_fsc_render.py`, which appends below this pre-specification only.

### Addendum A results

Pre-specification commit f29bd1d; results commit bcb9e72. Script `scripts/paper_plan/rs_fsc.py` (Slurm via `scripts/cluster/campaign.sh`, prefix fsc), `scripts/paper_plan/rs_fsc_render.py`. Aggregates `results/paper_final/risk_strata/fsc_pre.json`, `fsc_pre_ndbe.json`.

| Check | Result |
|---|---|
| Fold columns of every cross-validated model equal the cfg-0 folds, all 10 repeats | yes |
| Intercept-only, fold-stratified Harrell's / Uno's C (must be 0.500) | pre-event 0.500 / 0.500; NDBE 0.500 / 0.500: PASS |
| Pooled C recomputed by this script equals Section 4 (±0.001) | yes, both populations |

**All pre-event samples** (571 samples, 75 patients, 161 samples with an event; 2000 patient-bootstrap draws).

| Model | Harrell's C, fold-stratified [95% CI] | Uno's C, fold-stratified [95% CI] | Harrell's C, pooled (Section 4) | Uno's C, pooled (Section 4) |
|---|---|---|---|---|
| Killcoyne published (P) † | 0.774 [0.664, 0.839] | 0.764 [0.623, 0.833] | 0.791 | 0.794 |
| CNV, their matrix (C) | 0.752 [0.653, 0.814] | 0.744 [0.616, 0.801] | 0.764 | 0.765 |
| Late fusion, their matrix (L) | 0.805 [0.713, 0.848] | 0.803 [0.709, 0.842] | 0.825 | 0.823 |
| WSI (L-IMG) | 0.761 [0.675, 0.808] | 0.754 [0.675, 0.801] | 0.779 | 0.770 |
| Early fusion | 0.779 [0.683, 0.837] | 0.774 [0.653, 0.824] | 0.804 | 0.809 |
| Inter fusion | 0.755 [0.657, 0.819] | 0.741 [0.633, 0.801] | 0.778 | 0.771 |
| Pathology grade (raw score) † | 0.577 [0.500, 0.651] | 0.561 [0.490, 0.616] | 0.586 | 0.570 |
| CNV, package features | 0.748 [0.641, 0.804] | 0.759 [0.636, 0.816] | 0.765 | 0.776 |
| Late fusion, package features | 0.799 [0.700, 0.847] | 0.807 [0.708, 0.852] | 0.817 | 0.823 |
| Early fusion, package | 0.780 [0.676, 0.835] | 0.782 [0.679, 0.836] | 0.793 | 0.797 |
| Inter fusion, package | 0.767 [0.674, 0.815] | 0.761 [0.661, 0.812] | 0.787 | 0.786 |
| Intercept-only (reference) | 0.500 [0.500, 0.500] | 0.500 [0.500, 0.500] | 0.316 | 0.292 |

**NDBE pre-event samples** (438 samples, 71 patients, 104 samples with an event; 2000 patient-bootstrap draws).

| Model | Harrell's C, fold-stratified [95% CI] | Uno's C, fold-stratified [95% CI] | Harrell's C, pooled (Section 4) | Uno's C, pooled (Section 4) |
|---|---|---|---|---|
| Killcoyne published (P) † | 0.766 [0.647, 0.856] | 0.770 [0.667, 0.848] | 0.773 | 0.777 |
| CNV, their matrix (C) | 0.758 [0.648, 0.838] | 0.755 [0.660, 0.825] | 0.759 | 0.759 |
| Late fusion, their matrix (L) | 0.781 [0.677, 0.850] | 0.785 [0.685, 0.844] | 0.795 | 0.800 |
| WSI (L-IMG) | 0.728 [0.631, 0.792] | 0.726 [0.629, 0.777] | 0.744 | 0.747 |
| Early fusion | 0.779 [0.668, 0.856] | 0.774 [0.669, 0.847] | 0.799 | 0.800 |
| Inter fusion | 0.770 [0.639, 0.856] | 0.757 [0.647, 0.835] | 0.779 | 0.766 |
| Pathology grade (raw score) † | not estimable (grade constant) | — | — | — |
| CNV, package features | 0.733 [0.616, 0.814] | 0.760 [0.649, 0.833] | 0.739 | 0.759 |
| Late fusion, package features | 0.766 [0.661, 0.835] | 0.783 [0.684, 0.845] | 0.778 | 0.792 |
| Early fusion, package | 0.751 [0.635, 0.827] | 0.766 [0.656, 0.842] | 0.757 | 0.766 |
| Inter fusion, package | 0.768 [0.654, 0.844] | 0.774 [0.657, 0.850] | 0.785 | 0.793 |
| Intercept-only (reference) | 0.500 [0.500, 0.500] | 0.500 [0.500, 0.500] | 0.329 | 0.310 |

† Not cross-validated: scored on the same within-fold pairs as the cross-validated models (cfg-0 folds), averaged over the 10 repeats; only the pair set varies across repeats.

**Paired Δ, fold-stratified** (same 2,000 patient-bootstrap draws; unadjusted two-sided bootstrap p).

| Population | Comparison | Δ Harrell's C [95% CI], p | Δ Uno's C [95% CI], p |
|---|---|---|---|
| All pre-event samples | L vs C | +0.053 [+0.003, +0.106], p 0.032 | +0.059 [+0.010, +0.122], p 0.019 |
| All pre-event samples | L vs P | +0.031 [-0.022, +0.095], p 0.266 | +0.039 [-0.024, +0.129], p 0.276 |
| All pre-event samples | L (package) vs C (package) | +0.051 [+0.011, +0.108], p 0.012 | +0.047 [+0.008, +0.099], p 0.022 |
| NDBE pre-event samples | L vs C | +0.023 [-0.020, +0.075], p 0.333 | +0.030 [-0.017, +0.085], p 0.26 |
| NDBE pre-event samples | L vs P | +0.015 [-0.044, +0.083], p 0.693 | +0.016 [-0.049, +0.092], p 0.871 |
| NDBE pre-event samples | L (package) vs C (package) | +0.033 [-0.007, +0.082], p 0.106 | +0.024 [-0.016, +0.069], p 0.303 |

**Answer (one line).** The Section 4 answer to question 3 holds on all pre-event samples under fold-stratified scoring: L beats C on Harrell's C (+0.053 [+0.003, +0.106]) and Uno's C (+0.059 [+0.010, +0.122]), with every model's C-index lower than its pooled value; L vs P is not significant (+0.031 [-0.022, +0.095]), and on NDBE samples neither difference is significant (L vs C +0.023 [-0.020, +0.075]).

**Caveat (observed after running, not pre-specified).** For every model the fold-stratified point estimate sits near the upper end of its percentile CI (e.g. L, pre-event, 0.805 [0.713, 0.848]). A likely cause: a patient drawn more than once keeps its fold, so its copies are compared with each other inside one fold, and these within-patient pairs make up a much larger share of the within-fold pairs than of the pooled pairs; within-patient ordering is close to uninformative, which pulls the bootstrap distribution towards 0.5. The CIs of single models are therefore conservative on the low side; the paired Δ, which uses the same pairs for both models, is less affected. The method was not changed after seeing this.

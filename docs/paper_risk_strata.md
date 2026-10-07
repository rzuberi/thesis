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

(appended in a later commit)

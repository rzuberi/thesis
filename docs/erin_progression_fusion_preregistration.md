# Pre-registration — ERIN image + text fusion for future progression
Written 21 Sep 2026, 19:35 (cluster time), BEFORE any model training. Same format as `docs/nodal_probe_preregistration.md`.
Cohort build script: `scripts/erin_fusion/build_cohort.py` (run once, output `results/erin_progression_fusion/cohort_counts.json`).

## 1. Question
Does fusing the index H&E slide(s) with the index pathology report predict progression to HGD/cancer better than either alone, in ERIN? Primary comparison: late-mean fusion (d) vs the better single modality, max(b, c).

## 2. Cohort (fixed before training)
- Source: ERIN jury labels (`labeller/erin_labels_jury_final.csv`, train-eligible + adjudicated reports only).
- **Index** = each patient's first report graded NDBE or IND (v3 also admitted LGD indices; excluded here per the task text — recorded as a decision).
- **Primary label y3**: HGD or CANCER jury label within 1,095 days of the index (1); no HGD/CANCER ever AND last report ≥ 1,095 days after index (0); otherwise excluded (censored early). **Secondary y_any**: any later HGD/CANCER, censoring-ignorant.
- **Image bag**: all H&E slides of the index CaseName with all-slides UNI2 features (`features_uni_v2_all`), tiles pooled into one bag per case.
- Covariates: age at index (present for all); sex is not available in ERIN or the DB export.
- Overlap: ERIN↔SWG patient overlap via the accession/DB crosswalk of 2.40, reported per cohort.

## 3. Arms
a. baseline — logistic regression on index grade (NDBE vs IND) + age.
b. text_only — logistic regression (C=1, standardised) on the `nomic-embed-text` (768-d, local ollama) embedding of the index report's FinalDiagnosis + MicroscopicDescription.
b2. jury_structured — logistic regression on jury-v3 per-report features of the index report (n sections, fraction of sections IND, site fractions oesophagus/GOJ/stomach/duodenum/other, specimen-type fractions, grade fractions, n jurors).
c. image_only — `scripts/abmil_clf.py::train_abmil_clf_fold` on the pooled index-case bag, ERIN-grading defaults (25 epochs, lr 1e-4, mb 32, MAX_TILES cap, pos-weighted BCE). No hyper-parameter search.
d. late_mean — fold-local z-scored OOF risks of b and c averaged (fold-local per 2.46).
e. late_mean_b2c — same with b2 and c.

## 4. Evaluation (unchanged machinery)
Patient-disjoint 5-fold folds from `patient_folds` (seed 0), 3 seeds averaged into one OOF vector per arm; metrics per arm: AUROC, AUPRC with 2,000-replicate patient bootstrap CIs (`bootstrap_auc`), Brier, specificity at sensitivity 0.95 and 1.0, sensitivity at specificity 0.80; paired deltas with CIs for d−max(b,c) [primary], e−max(b2,c), b−a, c−a; 50 label-permutation shards for arms c and d (b and b2 re-fitted per permutation, c retrained per permutation, one seed); tile-count confound for c. If d beats max(b,c) with the delta CI excluding zero, the max-over-arms selection-adjusted permutation (`task_swg_selection_adjusted.py` logic) over {b, b2, c, d, e} is run before any statement is made.

## 5. Rules
- Pass rule (primary): d − max(b,c) paired 95% CI excludes 0 AND selection-adjusted p < 0.05 → "fusion adds to the best single modality in ERIN". Otherwise: "no demonstrated fusion gain", with the power map's minimum detectable delta quoted.
- Feasibility rule: if y3 positives < 30 → feasibility run, no comparison interpreted. **If either class is empty at the horizon, the experiment is infeasible and stops after the cohort report.**
- Stop rule: nothing changes in this file after the first training job; deviations go to the report's "decisions not pre-specified" list.

## 6. Cohort report (run 21 Sep 2026, 19:20) — FEASIBILITY STOP
| | patients / cases | y3 = 1 | y3 = 0 | excluded (censored < 3 y) | y_any = 1 |
|---|---|---|---|---|---|
| Report level (all index NDBE/IND patients) | 2,092 | 115 | 721 | 1,256 | 159 |
| **Index case has ≥1 H&E slide with features** | **632** | **18** | **0** | **614** | 18 |
Slides per imaged index case median 2 (1–72), 2,499 slides in total; index grade NDBE 611 / IND 21; age available 632/632; jury-v3 features 632/632; SWG-overlap patients 1 (0 among positives).
Why: **every scanned ERIN H&E slide comes from a 2022–2025 report** (59 / 4,685 / 5,765 / 1,163 slides by year). Imaged index cases date from 2022–2025 (8 / 261 / 298 / 65), 499 of 632 have no later report at all, median follow-up 0 days. Shorter horizons do not rescue it: 1 year → 18 positives / 30 negatives; 2 years → 18 / 2. Admitting LGD indices (v3 rule): 27 / 31 at 1 year, 0 negatives at 3 years. Using the earliest *imaged* NDBE/IND report as a landmark index: 14 / 44 at 1 year, 0 negatives at 3 years.
**Decision by the pre-registered feasibility rule: the experiment cannot be run tonight — the negative class is empty at the 3-year horizon and below any usable size at shorter ones.** No training job was submitted. What is missing is stated in `reports/erin_progression_fusion.md`.

# Two papers, agent P1A: Paper 1 core estimates

Paper 1 plan v2 ("New analyses" items 1, 2, 3 and 8). Rules: `paper/two_papers/RUN_RULES.md`. Population: the 571 pre-event samples (288 endoscopies, 75 patients, 32 progressors) of the 676 samples from 80 patients of the Killcoyne discovery cohort with a matched H&E slide.

## Plan (written 21 October 2026, before any new number was computed)

**Stored inputs, read-only.** Outer 10 × 10 predictions of `kv_cv.R` (L-CNV on the shipped matrix cfg 0, joint package rebuild cfg 1, L-IMG cfg 2, L-EARLY cfg 3); L-INTER (`hz_fit.R`); past-only and per-sample re-segmentations (`review_round4/r36_outer`); the published leave-one-patient-out probabilities of P (`k_prob`); the round-2 F3 refit-bootstrap predictions (`review_round2/f3`, 200 draws). L-LATE = per-repeat mean of L-CNV and L-IMG probabilities.

**1. P refitted in our folds** (`tp_p1a_prefit.R`). Killcoyne's recipe inside the same 10 × 10 outer folds (same fold assignment as `kv_cv.R`): glmnet α 0.9, `standardize = FALSE`, 1,000-value λ path, λ from 10 × 5 patient-grouped CV inside the training patients (the `kr_lopo.R` curves). Variants:
- features: their shipped 773 × 634 matrix (their segmentation, tiles, arm adjustment, arms, cx; standardised over their whole cohort), or the same pipeline on our hg38 counts through their package (standardised over the 773 published samples);
- training rows: every published sample of the training patients plus the 8 patients without a slide (P's own training population; "s773"), or only the set C rows L-CNV is trained on ("C");
- λ rule: class-error 1-s.e. (as in their leave-one-out coefficient tables), class-error minimum, deviance minimum, deviance 1-s.e.; plus the shipped model's λ (chosen on all data, so not fold-honest; optimistic, labelled).

**Primary "P refit", fixed now:** shipped matrix, s773 training rows, class-error 1-s.e. All variants are reported. Smoke: shipped matrix, set C rows, 100-value path, class-error minimum must reproduce the stored L-CNV predictions exactly (0.801), and the package-feature analogue the joint package rebuild (0.845).

**2. Units of analysis.** All estimands are fold-stratified (case–control pairs within the same outer fold of a repeat, mean over the 10 repeats); predictions are fixed and the patient bootstrap resamples patients (2,000 draws, `RandomState(0)`, the `tb_common.boots_for` sequence; resampled copies are distinct units).
- *Sample level* (existing): concordance over within-fold progressor-sample × non-progressor-sample pairs.
- *Patient-weighted* (proposed primary): the same pairs, each weighted 1/(n_i · n_j), where n_i and n_j are the two patients' numbers of pre-event samples. Every within-fold progressor-patient × non-progressor-patient pair then carries total weight 1, so the estimand is the probability that a random pre-event sample of a random progressor scores above a random pre-event sample of a random non-progressor (within fold). It does not depend on how many samples a patient contributed.
- *Endoscopy level:* per repeat, endoscopy score = max or mean of its samples' probabilities; concordance over within-fold progressor × non-progressor endoscopy pairs.
- *Patient level:* patient score = max or mean over pre-event samples (the ACE-B-style unit).
- Models: L-IMG, L-CNV (shipped matrix), L-LATE, refit P, the joint package rebuild (best segmentation), past-only and per-sample segmentations, published P.
- **Classification at P's thresholds** (low ≤ 0.3, high ≥ 0.5; endoscopy = max sample probability, as the package's per-endoscopy rule): endoscopy- and sample-level sensitivity and specificity for "high" and "not low", per repeat then averaged, for published P, refit P, L-CNV, the joint package rebuild, L-IMG and L-LATE. The L-IMG analogue is (a) the same probability cuts (fixed in advance, fold-honest) and (b) cuts that reproduce refit P's held-out share of endoscopies in each class (label-free, descriptive ranking comparison).

**3. Differences and multiplicity.** L-LATE − L-IMG, and L-IMG − each copy-number model (L-CNV, refit P, joint package, past-only, per-sample, published P): two-sided percentile 95% CI, two-sided bootstrap p, and single-step max-T adjusted p (studentised by the bootstrap SD, as `tr_triage.py`). **Family:** these 7 contrasts, separately within each estimand (sample, patient-weighted, endoscopy max, endoscopy mean, patient max, patient mean). The earlier 0.066 adjusted over a different family (L-EARLY, L-INTER and L-LATE vs L-IMG, sample level), which is reproduced as the smoke.

**4. Design checks.**
- Matching variables: from the Gregson thesis and Killcoyne Supplementary Table 1 (frequency-matched, no pair key).
- Within-stratum concordance: strata = sex × age at diagnosis (≤ / > the 75-patient median) × Prague M (≤ 4 cm, > 4 cm, missing), from `Demographics_full.csv` linked as in `hz_prep.py`. Sample-level and patient-weighted concordance over pairs in the same stratum (across folds, and within fold), with patient-bootstrap CIs; conditional logistic regression of status on the patient-mean logit (per SD) with stratum as the conditioning set, next to the unconditional fit.
- Calibration: per repeat, logistic recalibration of status on logit(probability) at sample level (slope; and calibration-in-the-large with the slope fixed at 1), unweighted and patient-weighted, averaged over repeats, patient-bootstrap CI. Case–control sampling (28% progressor samples, 43% progressor patients) fixes the intercept by design, so only the slope is interpretable.
- Bootstrap: the stored primary bootstrap keeps predictions fixed (no refit). The round-2 F3 refit bootstrap (200 draws, λ re-chosen, one stratified 10-fold CV per draw) exists for L-CNV and L-IMG; both key differences (L-LATE − L-IMG, L-IMG − L-CNV) are recomputed from it at every estimand. If refit P becomes the primary comparator, its own 200-draw refit bootstrap is run on the same draws and folds.

Scripts: `scripts/paper_plan/tp_p1a_prefit.R`, `tp_p1a_metrics.py`. Results: `results/paper_final/two_papers_P1A/`. Row-level outputs: `killcoyne_mm/two_papers_P1A/` (cluster).

---

## Results

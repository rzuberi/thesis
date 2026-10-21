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

Run 21 October 2026. Scripts `scripts/paper_plan/tp_p1a_prefit.R` (400 outer refits + 2,000 refit-bootstrap fits), `tp_p1a_metrics.py` (smoke, point, 20 bootstrap shards, merge, f3), `tp_p1a_render.py` (tables below). Aggregates `results/paper_final/two_papers_P1A/{smoke,point,main,refit_boot}.json`. Row-level outputs on the cluster under `killcoyne_mm/two_papers_P1A/`. Slurm campaigns `tpp1a*` (epyc, rocm, cuda). No deviation from the plan except where stated under "Deviations".

### Summary

- **P refitted in our folds gives 0.78–0.83, and the λ rule decides where.** The pre-specified primary (shipped matrix, P's 773-sample training population, class-error 1-s.e.) gives 0.784 [0.688, 0.862] per sample. The class-error minimum on the same rows gives 0.826, and the shipped model's λ 0.827, which reproduces the published 0.823 on the same pairs. So the published 0.83 is not inflated by its leave-one-patient-out design or by having been fitted on this cohort; it does depend on choosing the smaller λ. The 1-s.e. rule shrinks to about 46 features (median) and loses 0.04.
- **H&E is level with copy number in every unit of analysis.** Patient-weighted AUROC: L-IMG 0.852, copy-number versions 0.796–0.841, L-LATE 0.897. L-IMG − CN ranges from +0.011 (published P) to +0.056 (past-only); no CI excludes 0 and no max-T p is below 0.4. At endoscopy level the best segmentation is ahead of H&E (−0.032 [−0.107, +0.053]).
- **Weighting by patient helps copy number more than H&E** (L-CNV 0.801 → 0.822; L-IMG 0.847 → 0.852). This is because non-progressors with many samples drag sample-level copy-number AUROC down. The H&E "edge" over L-CNV shrinks from +0.045 to +0.030.
- **Fusion:** L-LATE − L-IMG is +0.042 to +0.051 at sample, patient-weighted, endoscopy and patient-max level. Patient-weighted: +0.045 [+0.006, +0.084], p 0.025, max-T 0.035 over the two primary contrasts and 0.086 over all seven. The refit bootstrap triples the SD (0.049 vs 0.020) and its interval spans 0 ([−0.032, +0.131]; 20% of draws ≤ 0). The gain is consistent but not confirmed.
- **At P's own thresholds, per endoscopy:** at "high" (≥ 0.5), L-IMG reaches sensitivity 0.691 at specificity 0.779, against 0.648 / 0.775 for published P and 0.588 / 0.796 for L-CNV. L-LATE reaches 0.701 / 0.876.
- **Design checks.** Restricting to case–control pairs in the same matching stratum (sex × age × segment length) moves AUROCs by at most 0.05. L-IMG − L-CNV lies between −0.017 and +0.041 with every CI spanning 0, and L-LATE − L-IMG stays at +0.05 to +0.07. Conditional and unconditional odds ratios agree for the copy-number models. Calibration slopes are 0.51–0.70 for the single models at the class-error-minimum λ (over-dispersed), 0.99 for the 1-s.e. refit P, and 1.29 for L-LATE, which is under-dispersed because averaging two probabilities pulls them together.

### Smoke (known numbers reproduced)

| Quantity | Expected | Reproduced |
|---|---|---|
| L-IMG | 0.847 | 0.847 |
| L-CNV | 0.801 | 0.801 |
| L-LATE | 0.889 | 0.889 |
| CN joint package | 0.845 | 0.845 |
| CN past-only | 0.8 | 0.8 |
| CN per-sample | 0.785 | 0.785 |
| P published | 0.823 | 0.823 |
| L-LATE − L-IMG, old family max-T | +0.042 [+0.002, +0.078], 0.066 | +0.042 [+0.002, +0.078], 0.066 |
| Refit anchor (their features, set C rows, 100-λ, class min) vs stored L-CNV fold predictions | identical | max abs Δ 5.6e-16, same λ |
| Refit anchor (pkg features, set C rows, 100-λ, class min) vs stored L-CNV fold predictions | identical | max abs Δ 0.0e+00, same λ |
| Refit bootstrap (F3) Δ L-IMG − L-CNV, sample level | +0.070 [−0.114, +0.302]; draw-mean AUROC 0.718 / 0.788 / 0.821 | +0.070 [-0.114, +0.302]; 0.718 / 0.788 / 0.821 |

### 1. Model P refitted in our folds (sample-level and patient-weighted fold-stratified AUROC, 571 pre-event samples)

| Features | Training rows | λ rule | Sample | Patient-weighted | Endoscopy max | λ median | Non-zero coef. median |
|---|---|---|---|---|---|---|---|
| shipped matrix | P's population (773 samples, 88 patients) | class_1se (pre-specified primary) | 0.784 | 0.809 | 0.797 | 0.021 | 46 |
| shipped matrix | P's population (773 samples, 88 patients) | class_min | 0.826 | 0.838 | 0.835 | 0.003 | 106 |
| shipped matrix | P's population (773 samples, 88 patients) | dev_min | 0.820 | 0.838 | 0.829 | 0.010 | 65 |
| shipped matrix | P's population (773 samples, 88 patients) | dev_1se | 0.736 | 0.763 | 0.754 | 0.037 | 31 |
| shipped matrix | P's population (773 samples, 88 patients) | published (not fold-honest) | 0.827 | 0.843 | 0.835 | 0.007 | 79 |
| shipped matrix | set C rows only | class_1se | 0.727 | 0.754 | 0.737 | 0.039 | 27 |
| shipped matrix | set C rows only | class_min | 0.801 | 0.821 | 0.810 | 0.008 | 72 |
| shipped matrix | set C rows only | dev_min | 0.809 | 0.831 | 0.818 | 0.015 | 54 |
| shipped matrix | set C rows only | dev_1se | 0.686 | 0.710 | 0.699 | 0.058 | 18 |
| shipped matrix | set C rows only | published (not fold-honest) | 0.806 | 0.826 | 0.816 | 0.007 | 79 |
| our counts via package | P's population (773 samples, 88 patients) | class_1se | 0.770 | 0.753 | 0.790 | 0.049 | 24 |
| our counts via package | P's population (773 samples, 88 patients) | class_min | 0.803 | 0.778 | 0.827 | 0.004 | 93 |
| our counts via package | P's population (773 samples, 88 patients) | dev_min | 0.815 | 0.787 | 0.832 | 0.019 | 50 |
| our counts via package | P's population (773 samples, 88 patients) | dev_1se | 0.770 | 0.755 | 0.794 | 0.051 | 23 |
| our counts via package | P's population (773 samples, 88 patients) | published (not fold-honest) | 0.822 | 0.799 | 0.845 | 0.007 | 77 |
| our counts via package | set C rows only | class_1se | 0.788 | 0.786 | 0.826 | 0.049 | 23 |
| our counts via package | set C rows only | class_min | 0.845 | 0.832 | 0.869 | 0.009 | 63 |
| our counts via package | set C rows only | dev_min | 0.850 | 0.840 | 0.879 | 0.016 | 48 |
| our counts via package | set C rows only | dev_1se | 0.798 | 0.797 | 0.838 | 0.047 | 25 |
| our counts via package | set C rows only | published (not fold-honest) | 0.850 | 0.837 | 0.876 | 0.007 | 70 |

### 2. AUROC by unit of analysis (fold-stratified; patient-bootstrap 95% CI, 2,000 draws)

| Model | Sample | Patient-weighted | Endoscopy max | Endoscopy mean | Patient max | Patient mean |
|---|---|---|---|---|---|---|
| L-IMG | 0.847 [0.798, 0.894] | 0.852 [0.803, 0.898] | 0.837 [0.784, 0.889] | 0.852 [0.804, 0.898] | 0.851 [0.755, 0.932] | 0.940 [0.882, 0.981] |
| L-CNV | 0.801 [0.710, 0.875] | 0.822 [0.738, 0.887] | 0.811 [0.722, 0.881] | 0.821 [0.732, 0.890] | 0.836 [0.732, 0.920] | 0.863 [0.774, 0.934] |
| L-LATE | 0.889 [0.830, 0.934] | 0.897 [0.848, 0.936] | 0.885 [0.831, 0.930] | 0.901 [0.848, 0.942] | 0.902 [0.824, 0.958] | 0.957 [0.908, 0.990] |
| CN joint package | 0.845 [0.766, 0.904] | 0.832 [0.754, 0.899] | 0.869 [0.796, 0.926] | 0.871 [0.797, 0.928] | 0.853 [0.755, 0.933] | 0.867 [0.782, 0.938] |
| CN past-only | 0.800 [0.723, 0.867] | 0.796 [0.726, 0.863] | 0.826 [0.758, 0.892] | 0.826 [0.759, 0.888] | 0.826 [0.722, 0.917] | 0.882 [0.796, 0.952] |
| CN per-sample | 0.785 [0.723, 0.845] | 0.806 [0.747, 0.857] | 0.813 [0.747, 0.880] | 0.826 [0.762, 0.888] | 0.851 [0.748, 0.935] | 0.941 [0.882, 0.983] |
| P published | 0.823 [0.709, 0.908] | 0.841 [0.750, 0.911] | 0.820 [0.716, 0.902] | 0.838 [0.735, 0.914] | 0.854 [0.745, 0.940] | 0.881 [0.781, 0.958] |
| P refit | 0.784 [0.688, 0.862] | 0.809 [0.732, 0.875] | 0.797 [0.706, 0.871] | 0.811 [0.723, 0.880] | 0.819 [0.711, 0.912] | 0.868 [0.781, 0.937] |

**Classification at P's published thresholds** (low ≤ 0.3, high ≥ 0.5; endoscopy score = max sample probability; per repeat, averaged). Sensitivity / specificity [95% CI].

| Model | Endoscopy, high (≥ 0.5) | Endoscopy, not low (> 0.3) | Sample, high | Sample, not low |
|---|---|---|---|---|
| P published | 0.648 [0.515, 0.774] / 0.775 [0.657, 0.880] | 0.852 [0.735, 0.949] / 0.615 [0.483, 0.740] | 0.640 [0.514, 0.752] / 0.837 [0.744, 0.916] | 0.826 [0.697, 0.925] / 0.659 [0.543, 0.775] |
| P refit | 0.569 [0.442, 0.693] / 0.824 [0.734, 0.904] | 0.827 [0.734, 0.912] / 0.488 [0.377, 0.595] | 0.537 [0.420, 0.644] / 0.857 [0.783, 0.925] | 0.807 [0.701, 0.891] / 0.520 [0.405, 0.641] |
| L-CNV | 0.588 [0.470, 0.703] / 0.796 [0.698, 0.881] | 0.764 [0.665, 0.852] / 0.629 [0.507, 0.743] | 0.544 [0.423, 0.659] / 0.852 [0.778, 0.917] | 0.732 [0.613, 0.830] / 0.686 [0.583, 0.792] |
| CN joint package | 0.718 [0.606, 0.825] / 0.828 [0.737, 0.903] | 0.882 [0.813, 0.941] / 0.682 [0.569, 0.782] | 0.599 [0.476, 0.717] / 0.863 [0.777, 0.934] | 0.760 [0.664, 0.847] / 0.739 [0.617, 0.837] |
| L-IMG | 0.691 [0.595, 0.789] / 0.779 [0.723, 0.831] | 0.827 [0.753, 0.901] / 0.647 [0.583, 0.712] | 0.620 [0.520, 0.731] / 0.875 [0.838, 0.906] | 0.730 [0.647, 0.820] / 0.791 [0.744, 0.834] |
| L-LATE | 0.701 [0.602, 0.802] / 0.876 [0.826, 0.921] | 0.880 [0.818, 0.934] / 0.601 [0.508, 0.693] | 0.637 [0.540, 0.738] / 0.928 [0.893, 0.956] | 0.840 [0.752, 0.913] / 0.731 [0.656, 0.800] |
| L-IMG share-matched to P refit | 0.607 [0.508, 0.721] / 0.840 [0.764, 0.917] | 0.895 [0.833, 0.949] / 0.518 [0.406, 0.620] | 0.601 [0.487, 0.718] / 0.881 [0.822, 0.939] | 0.878 [0.798, 0.941] / 0.548 [0.444, 0.658] |

### 3. Paired differences (patient bootstrap, predictions fixed)

Max-T (7) adjusts over the 7 contrasts in the table within the same unit of analysis; max-T (2) over the two primary contrasts only (L-LATE − L-IMG and L-IMG − L-CNV).

| Unit | Contrast | Δ [95% CI] | p | max-T p (7) | max-T p (2) |
|---|---|---|---|---|---|
| Sample | L-LATE - L-IMG | +0.042 [+0.002, +0.078] | 0.048 | 0.114 | 0.047 |
| Sample | L-IMG - L-CNV | +0.045 [-0.036, +0.136] | 0.295 | 0.7315 | 0.3665 |
| Sample | L-IMG - P refit | +0.062 [-0.022, +0.157] | 0.175 | 0.4905 | — |
| Sample | L-IMG - CN joint package | +0.002 [-0.074, +0.090] | 0.969 | 1.0 | — |
| Sample | L-IMG - CN past-only | +0.047 [-0.022, +0.131] | 0.214 | 0.5765 | — |
| Sample | L-IMG - CN per-sample | +0.062 [+0.003, +0.119] | 0.038 | 0.1335 | — |
| Sample | L-IMG - P published | +0.024 [-0.067, +0.127] | 0.659 | 0.9885 | — |
| Patient-weighted | L-LATE - L-IMG | +0.045 [+0.006, +0.084] | 0.025 | 0.0855 | 0.0345 |
| Patient-weighted | L-IMG - L-CNV | +0.030 [-0.047, +0.118] | 0.456 | 0.8965 | 0.5805 |
| Patient-weighted | L-IMG - P refit | +0.043 [-0.034, +0.129] | 0.307 | 0.7155 | — |
| Patient-weighted | L-IMG - CN joint package | +0.020 [-0.062, +0.104] | 0.643 | 0.9865 | — |
| Patient-weighted | L-IMG - CN past-only | +0.056 [-0.019, +0.135] | 0.16 | 0.427 | — |
| Patient-weighted | L-IMG - CN per-sample | +0.046 [-0.017, +0.107] | 0.152 | 0.4015 | — |
| Patient-weighted | L-IMG - P published | +0.011 [-0.074, +0.108] | 0.806 | 1.0 | — |
| Endoscopy max | L-LATE - L-IMG | +0.048 [+0.003, +0.093] | 0.039 | 0.125 | 0.0475 |
| Endoscopy max | L-IMG - L-CNV | +0.026 [-0.057, +0.119] | 0.53 | 0.962 | 0.665 |
| Endoscopy max | L-IMG - P refit | +0.040 [-0.045, +0.138] | 0.357 | 0.799 | — |
| Endoscopy max | L-IMG - CN joint package | -0.032 [-0.107, +0.053] | 0.429 | 0.8625 | — |
| Endoscopy max | L-IMG - CN past-only | +0.011 [-0.062, +0.093] | 0.804 | 0.999 | — |
| Endoscopy max | L-IMG - CN per-sample | +0.024 [-0.045, +0.092] | 0.486 | 0.907 | — |
| Endoscopy max | L-IMG - P published | +0.017 [-0.074, +0.125] | 0.739 | 0.9975 | — |
| Endoscopy mean | L-LATE - L-IMG | +0.048 [-0.000, +0.092] | 0.054 | 0.1265 | 0.0515 |
| Endoscopy mean | L-IMG - L-CNV | +0.031 [-0.052, +0.127] | 0.471 | 0.9235 | 0.5775 |
| Endoscopy mean | L-IMG - P refit | +0.041 [-0.041, +0.138] | 0.339 | 0.791 | — |
| Endoscopy mean | L-IMG - CN joint package | -0.019 [-0.093, +0.068] | 0.66 | 0.9875 | — |
| Endoscopy mean | L-IMG - CN past-only | +0.026 [-0.044, +0.105] | 0.504 | 0.919 | — |
| Endoscopy mean | L-IMG - CN per-sample | +0.026 [-0.036, +0.087] | 0.391 | 0.825 | — |
| Endoscopy mean | L-IMG - P published | +0.014 [-0.077, +0.124] | 0.795 | 0.999 | — |
| Patient max | L-LATE - L-IMG | +0.051 [-0.009, +0.120] | 0.105 | 0.3345 | 0.174 |
| Patient max | L-IMG - L-CNV | +0.015 [-0.095, +0.125] | 0.793 | 0.999 | 0.93 |
| Patient max | L-IMG - P refit | +0.032 [-0.082, +0.151] | 0.564 | 0.9595 | — |
| Patient max | L-IMG - CN joint package | -0.002 [-0.117, +0.104] | 1.0 | 1.0 | — |
| Patient max | L-IMG - CN past-only | +0.024 [-0.088, +0.138] | 0.691 | 0.9895 | — |
| Patient max | L-IMG - CN per-sample | -0.000 [-0.109, +0.107] | 0.972 | 1.0 | — |
| Patient max | L-IMG - P published | -0.004 [-0.120, +0.123] | 0.92 | 1.0 | — |
| Patient mean | L-LATE - L-IMG | +0.017 [-0.029, +0.074] | 0.489 | 0.9365 | 0.6595 |
| Patient mean | L-IMG - L-CNV | +0.077 [-0.009, +0.170] | 0.084 | 0.2855 | 0.141 |
| Patient mean | L-IMG - P refit | +0.072 [-0.014, +0.169] | 0.096 | 0.3255 | — |
| Patient mean | L-IMG - CN joint package | +0.073 [-0.009, +0.157] | 0.082 | 0.2615 | — |
| Patient mean | L-IMG - CN past-only | +0.058 [-0.023, +0.142] | 0.182 | 0.4815 | — |
| Patient mean | L-IMG - CN per-sample | -0.001 [-0.067, +0.062] | 0.982 | 1.0 | — |
| Patient mean | L-IMG - P published | +0.059 [-0.034, +0.167] | 0.243 | 0.6375 | — |

**Refit bootstrap** (200 draws; one stratified 10-fold CV per draw with λ re-chosen; copies share every split). Draw mean, 95% percentile interval, SD; next to the stored estimate and the fixed-prediction bootstrap SE.

| Unit | Contrast | Refit mean [95% interval] | Refit SD | Share of draws ≤ 0 | Stored Δ | Fixed-prediction SE |
|---|---|---|---|---|---|---|
| Sample | L-LATE - L-IMG | +0.032 [-0.076, +0.124] | 0.054 | 0.295 | +0.042 | 0.019 |
| Sample | L-IMG - L-CNV | +0.070 [-0.114, +0.302] | 0.108 | 0.285 | +0.045 | 0.045 |
| Sample | L-IMG - P refit | +0.091 [-0.118, +0.300] | 0.112 | 0.250 | +0.062 | 0.046 |
| Sample | L-IMG - P refit (class_min) | +0.030 [-0.150, +0.265] | 0.104 | 0.405 | — | — |
| Patient-weighted | L-LATE - L-IMG | +0.044 [-0.032, +0.131] | 0.049 | 0.200 | +0.045 | 0.020 |
| Patient-weighted | L-IMG - L-CNV | +0.047 [-0.115, +0.240] | 0.097 | 0.350 | +0.030 | 0.042 |
| Patient-weighted | L-IMG - P refit | +0.074 [-0.094, +0.264] | 0.100 | 0.250 | +0.043 | 0.043 |
| Patient-weighted | L-IMG - P refit (class_min) | +0.014 [-0.158, +0.211] | 0.092 | 0.450 | — | — |
| Endoscopy max | L-LATE - L-IMG | +0.033 [-0.057, +0.141] | 0.055 | 0.310 | +0.048 | 0.023 |
| Endoscopy max | L-IMG - L-CNV | +0.051 [-0.134, +0.269] | 0.106 | 0.350 | +0.026 | 0.045 |
| Endoscopy max | L-IMG - P refit | +0.068 [-0.136, +0.270] | 0.107 | 0.250 | +0.040 | 0.046 |
| Endoscopy max | L-IMG - P refit (class_min) | +0.013 [-0.168, +0.220] | 0.101 | 0.475 | — | — |
| Endoscopy mean | L-LATE - L-IMG | +0.036 [-0.056, +0.145] | 0.057 | 0.285 | +0.048 | 0.023 |
| Endoscopy mean | L-IMG - L-CNV | +0.063 [-0.128, +0.288] | 0.106 | 0.280 | +0.031 | 0.046 |
| Endoscopy mean | L-IMG - P refit | +0.080 [-0.118, +0.281] | 0.109 | 0.245 | +0.041 | 0.046 |
| Endoscopy mean | L-IMG - P refit (class_min) | +0.023 [-0.189, +0.219] | 0.104 | 0.450 | — | — |
| Patient max | L-LATE - L-IMG | +0.041 [-0.100, +0.216] | 0.084 | 0.365 | +0.051 | 0.033 |
| Patient max | L-IMG - L-CNV | +0.029 [-0.196, +0.273] | 0.121 | 0.425 | +0.015 | 0.058 |
| Patient max | L-IMG - P refit | +0.034 [-0.208, +0.274] | 0.126 | 0.385 | +0.032 | 0.059 |
| Patient max | L-IMG - P refit (class_min) | -0.013 [-0.263, +0.207] | 0.116 | 0.535 | — | — |
| Patient mean | L-LATE - L-IMG | +0.030 [-0.081, +0.174] | 0.070 | 0.365 | +0.017 | 0.026 |
| Patient mean | L-IMG - L-CNV | +0.081 [-0.163, +0.336] | 0.124 | 0.280 | +0.077 | 0.047 |
| Patient mean | L-IMG - P refit | +0.101 [-0.162, +0.356] | 0.129 | 0.205 | +0.072 | 0.046 |
| Patient mean | L-IMG - P refit (class_min) | +0.056 [-0.185, +0.295] | 0.118 | 0.280 | — | — |

Draw-mean AUROC (refit models, ~48 distinct patients per draw): Sample: pred_cnv 0.718, pred_img 0.788, late 0.821, prefit 0.697, prefit_min 0.758; Patient-weighted: pred_cnv 0.746, pred_img 0.793, late 0.838, prefit 0.720, prefit_min 0.780; Endoscopy max: pred_cnv 0.720, pred_img 0.772, late 0.805, prefit 0.704, prefit_min 0.759; Endoscopy mean: pred_cnv 0.725, pred_img 0.788, late 0.824, prefit 0.708, prefit_min 0.765; Patient max: pred_cnv 0.752, pred_img 0.781, late 0.822, prefit 0.747, prefit_min 0.794; Patient mean: pred_cnv 0.785, pred_img 0.866, late 0.896, prefit 0.765, prefit_min 0.810.

### 4. Design checks

**Within-stratum concordance** (strata: sex × age at diagnosis ≤ / > 61.0 y × Prague M ≤ 4 / > 4 cm / missing; Prague M missing for 11 patients; within-stratum pairs are 11.8% of all case–control sample pairs).

| Model / contrast | All pairs, across folds: sample | patient-weighted | Same stratum, across folds: sample | patient-weighted | Same stratum and fold: sample | patient-weighted |
|---|---|---|---|---|---|---|
| L-IMG | 0.837 [0.783, 0.889] | 0.842 [0.790, 0.892] | 0.829 [0.753, 0.896] | 0.840 [0.772, 0.899] | 0.825 [0.764, 0.894] | 0.836 [0.768, 0.898] |
| L-CNV | 0.783 [0.691, 0.858] | 0.803 [0.717, 0.870] | 0.788 [0.654, 0.902] | 0.820 [0.696, 0.911] | 0.819 [0.700, 0.925] | 0.852 [0.746, 0.932] |
| L-LATE | 0.880 [0.820, 0.928] | 0.887 [0.832, 0.930] | 0.879 [0.796, 0.943] | 0.896 [0.825, 0.947] | 0.880 [0.801, 0.950] | 0.903 [0.834, 0.956] |
| P refit | 0.775 [0.681, 0.854] | 0.798 [0.713, 0.869] | 0.784 [0.646, 0.896] | 0.819 [0.705, 0.906] | 0.799 [0.674, 0.912] | 0.820 [0.715, 0.913] |
| CN joint package | 0.838 [0.758, 0.898] | 0.825 [0.743, 0.892] | 0.857 [0.762, 0.927] | 0.850 [0.761, 0.920] | 0.858 [0.758, 0.931] | 0.835 [0.717, 0.928] |
| L-IMG - L-CNV | — | — | +0.041 [-0.082, +0.198] | +0.021 [-0.082, +0.143] | +0.006 [-0.103, +0.125] | -0.017 [-0.109, +0.096] |
| L-IMG - P refit | — | — | +0.045 [-0.076, +0.197] | +0.021 [-0.083, +0.139] | +0.026 [-0.092, +0.151] | +0.016 [-0.091, +0.129] |
| L-IMG - CN joint package | — | — | -0.028 [-0.127, +0.078] | -0.010 [-0.098, +0.085] | -0.033 [-0.126, +0.097] | +0.000 [-0.110, +0.125] |
| L-LATE - L-IMG | — | — | +0.051 [-0.006, +0.106] | +0.056 [+0.004, +0.111] | +0.055 [-0.008, +0.117] | +0.067 [+0.008, +0.126] |

| Model (patient-mean logit, per SD) | Conditional OR [95% CI], stratum = matching cell | Unconditional OR [95% CI] |
|---|---|---|
| L-IMG | 611.8 [7.9, 47560.0] | 745.9 [19.9, 27903.7] |
| L-CNV | 9.4 [3.0, 28.9] | 11.5 [3.7, 35.3] |
| L-LATE | 112.5 [7.9, 1598.8] | 186.3 [15.7, 2212.7] |
| P refit | 15.2 [3.7, 62.7] | 15.9 [4.3, 58.8] |
| CN joint package | 10.9 [3.2, 37.3] | 10.4 [3.4, 31.6] |

**Calibration** (logistic recalibration of status on logit(probability), sample level, per repeat and averaged; calibration-in-the-large = intercept with slope fixed at 1).

| Model | Slope | Calibration-in-the-large | Slope, patient-weighted | CITL, patient-weighted |
|---|---|---|---|---|
| L-IMG | 0.533 [0.420, 0.686] | -0.214 [-0.996, 0.529] | 0.511 [0.415, 0.639] | 0.538 [-0.245, 1.233] |
| L-CNV | 0.565 [0.373, 0.829] | -0.336 [-1.036, 0.392] | 0.582 [0.402, 0.831] | 0.446 [-0.191, 1.133] |
| L-LATE | 1.291 [0.935, 1.801] | -0.218 [-0.752, 0.307] | 1.234 [0.922, 1.711] | 0.370 [-0.130, 0.862] |
| P refit | 0.990 [0.657, 1.479] | -0.556 [-1.140, 0.003] | 1.064 [0.757, 1.507] | 0.119 [-0.370, 0.615] |
| CN joint package | 0.638 [0.461, 0.925] | -0.292 [-1.015, 0.435] | 0.574 [0.394, 0.841] | 0.324 [-0.336, 1.025] |
| P published | 0.662 [0.396, 1.125] | -0.592 [-1.311, 0.136] | 0.695 [0.455, 1.097] | 0.154 [-0.464, 0.804] |


### Primary-estimand recommendation for Paper 1

**Unit: patient-weighted, fold-stratified AUROC over pre-event samples (defined in the plan).** Every within-fold progressor–non-progressor patient pair counts once, whatever the patients' sample counts.
- It removes the dominance of non-progressors with many endoscopies (median 5 pre-event endoscopies against 2.5 in progressors), which was penalising copy number.
- It uses every sample and needs no aggregation rule (max vs mean), which is itself a choice that moves results by up to 0.09 at patient level.
- Its CIs are no wider than sample-level CIs (L-IMG 0.803–0.898 vs 0.798–0.894; L-CNV 0.738–0.887 vs 0.710–0.875).
- It equals the expected AUROC when each patient contributes one random sample, which is the closest internal analogue of a one-endoscopy cohort like ACE-B. For the ACE-B reference specifically, report endoscopy-level AUROC with the aggregation rule ACE-B registers (endoscopy mean: L-IMG 0.852, L-CNV 0.821, L-LATE 0.901).

Report sample, endoscopy (max, mean) and patient (max, mean) levels as secondary rows of one forest. Present patient-mean as descriptive only. It sits 0.09–0.14 above the other units for H&E and per-sample copy number, rests on about 15 within-fold patient pairs per fold, and depends on how many samples a patient has.

**Comparator: L-CNV on the published matrix as the single primary comparator.**
- It is the only copy-number model whose specification (matrix, learner, λ rule, folds) was fixed before the image results and is identical to L-IMG's.
- It sits mid-range among the honest refits of P's recipe (0.784–0.827 per sample, 0.809–0.843 patient-weighted).

Show refit P (pre-specified 1-s.e. and class-minimum), the three re-segmentations and published P in the same forest. State plainly that against the strongest copy-number version, L-IMG − CN ≈ 0:
- patient-weighted: +0.011 against published P, +0.020 against the joint package;
- endoscopy level: −0.032 against the joint package.

Do not lead with "H&E beats copy number". The defensible sentence is "comparable" (patient-weighted +0.030 [−0.047, +0.118] against L-CNV).

**Multiplicity.** State the family. The recommended family is the two primary contrasts (L-LATE − L-IMG and L-IMG − L-CNV) at the primary unit. There, L-LATE − L-IMG has max-T p 0.035; over all seven copy-number and fusion contrasts it is 0.086. The earlier 0.066 adjusted over L-EARLY, L-INTER and L-LATE vs L-IMG at sample level and should not be quoted without that family. Because the refit bootstrap interval spans 0, keep "highest AUROC, gain not statistically confirmed" even where the fixed-prediction p is below 0.05.

**Suggested headline numbers (patient-weighted).** H&E 0.85 [0.80, 0.90] vs copy number 0.82 [0.74, 0.89]: difference +0.03 [−0.05, +0.12]; copy-number versions range 0.80–0.84. Combined 0.90 [0.85, 0.94]: gain over H&E +0.045 [+0.006, +0.084], max-T p 0.035 over the two primary contrasts. Under a full refit bootstrap the interval is [−0.03, +0.13].

**What changes in the plan.** "P refit" cannot be one number; it is a λ-rule-dependent range (0.78–0.83). The forest should show that range rather than a single refit point. The ACE-B registration should name its aggregation rule and its Cambridge reference value (endoscopy mean). The calibration and matched-stratum checks need one Extended Data panel each and change no conclusion.

### Notes on the design checks

- **Matching variables.** Gregson thesis (pp. 52–53, 80) and Killcoyne Supplementary Table 1: frequency-matched 1:1 by patient count on age at diagnosis, sex and Barrett's segment length. The sources disagree on smoking. No pair key exists, so an exact matched-pair analysis is impossible. The stratified analysis uses 10 non-empty cells (sex × age ≤ / > 61 × Prague M ≤ 4 / > 4 / missing; Prague M missing for 11 patients). Only 11.8% of case–control sample pairs fall within a cell, hence the wide CIs.
- **Conditional logistic regression** on the patient-mean logit, per SD, conditioning on the cell. For the copy-number models the conditional and unconditional ORs agree (L-CNV 9.4 vs 11.5; refit P 15.2 vs 15.9; joint package 10.9 vs 10.4). For L-IMG and L-LATE the patient means nearly separate the classes, so their ORs (hundreds per SD) are not interpretable; the within-stratum concordance is the usable check there.
- **Calibration.** Case–control sampling (28% progressor samples, 43% progressor patients) fixes calibration-in-the-large by design: it is near 0 per sample and positive when weighted by patient, and neither says anything about absolute risk. The slopes are interpretable as dispersion:
  - the elastic-net models at the class-error-minimum λ are too extreme (L-IMG 0.53, L-CNV 0.57);
  - L-LATE is too flat (1.29), because averaging two probabilities shrinks them;
  - any absolute-risk use needs recalibration on a cohort-representative sample.
- **Bootstrap.** The stored primary bootstrap keeps the fold predictions fixed: it does not refit the cross-validation, so it omits training variability. The refit bootstrap (round-2 F3 draws, reused, plus a new 200-draw refit of P on the same draws and folds) re-chooses λ within a single 10-fold CV per draw. Two caveats:
  - Each draw has about 48 distinct patients, so the refit models are weaker (draw-mean AUROC 0.70–0.87) and the interval is pessimistic.
  - Its SD also includes the single-CV noise that the stored 10-repeat average removes.
  - Treat it as an upper bound on uncertainty, and the fixed-prediction interval as conditional on the trained models.

### Deviations

- Primary P refit chosen before the results (class-error 1-s.e.). It turned out to be the weakest fold-honest rule, so the class-minimum version is reported next to it everywhere, including the refit bootstrap. Neither is selected post hoc as "the" P.
- Max-T: the plan named one family (all seven contrasts per unit). Two-contrast families were added after the merge for the recommendation, and are labelled.
- The refit bootstrap for L-CNV and L-IMG reuses the stored round-2 F3 predictions (read-only) rather than refitting them again. Its smoke reproduced F3 exactly.


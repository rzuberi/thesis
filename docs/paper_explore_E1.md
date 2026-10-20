# Exploration E1: error analysis of non-progressor false flags (20–21 October 2026)

Status: EXPLORATORY (shared rules: `paper/reviews_round7/decisions/EXPLORE_RULES.md`). Nothing here is confirmatory; everything tried is recorded.

## Plan

**Question.** Why do non-progressor (NP) endoscopies get flagged by R49 and by H&E alone (P1 at 90%), and can a rule derived from that reduce false flags without losing progressor patients?

1. **Characterise flags (E1.1).** For each repeat, classify pre-event endoscopies as false-positive NP (flagged NP), true-negative NP, true-positive progressor (flagged P) and false-negative progressor, under R49 and under P1 90%. Compare FP-NP against TN-NP and against TP-P on every covariate available: tissue tiles, background-tile share (R55 pixels), slide age at scan, scanner, sequencing batch and batch composition, biopsy year, grade (sheet and Barrett's database), samples per endoscopy, position in the patient's series, time to last endoscopy, p53, Prague length, age, sex, later database grade group, slide notes (z levels / marker), same-block status. Endoscopy class shares are averaged over the 10 repeats (an endoscopy contributes its share of repeats in each class). Effect sizes: difference in means (and in shares) with paired patient-bootstrap 95% CIs (2,000 draws, `RandomState(0)`).
2. **Inside the H&E score (E1.2).** The H&E model is an elastic-net logistic regression on the z-scored mean of the sample's UNI2-h tile embeddings, so the logit decomposes exactly into per-tile contributions c_t = w·z(e_t)/N (N = the sample's tiles). Coefficients are not stored, so the outer fits (`kv_cv.R`, cfg 02) and the inner fits (`hz_fit.R`, img) are refitted verbatim and checked against the stored predictions. Per sample: share of the score from background and edge tiles (per-tile pixel statistics at the stored tile positions, CPU jobs), from the top-k tiles, the Gini of positive contributions, the number of strongly positive tiles. Aggregates only; no images.
3. **Fixes (E1.3).** Candidate fixes built from whatever separates FP-NP from TP-P: (a) score adjustments (e.g. remove background-tile contributions, trimmed means of tile contributions); (b) vetoes on flagged endoscopies by tissue/background/concentration features; (c) a second-stage false-positive filter (logistic) trained on training patients' flagged endoscopies. Every threshold and model is fitted on the training patients of each outer fold (inner out-of-fold scores and inner-fit tile contributions) and scored on held-out patients. Reported against R49 and P1 90% on the same patients with paired bootstrap CIs; apparent (non-nested) versions labelled optimistic.

**Space.** Scripts `scripts/paper_plan/ex_e1_*`; aggregates `results/paper_final/explore_E1/`; figures `paper/figures_explore_E1/` (local); row-level `killcoyne_mm/explore_E1/` (cluster); Slurm prefix `exe1`.

---

## Results

Scripts `scripts/paper_plan/ex_e1_coef.R`, `ex_e1_px.py`, `ex_e1_main.py`, `ex_e1_analysis.py`; this section is rendered by `ex_e1_render.py` from `results/paper_final/explore_E1/`. Exploratory: many comparisons, nothing adjusted, nothing confirmatory. Single model = per-repeat values averaged over the 10 repeats. Intervals: paired patient bootstrap, 2,000 draws (`RandomState(0)`), thresholds and calls fixed.

### Summary

**Why non-progressors get flagged.**
- **False flags sit with patients, not single endoscopies.** Under R49, an ever-flagged non-progressor (NP) patient has 2.8 flagged endoscopies on average. Only 21% of these patients are flagged exactly once, and 57% of their endoscopies are flagged. The 10 most-flagged NP patients account for 46% of all false-flagged NP endoscopies; the 20 most-flagged account for 79%. Between patients, the endoscopy H&E score of non-progressors has an ICC of 0.21. A rule that clears single endoscopies therefore rarely clears a patient: patient-level false flags fall slowly even when endoscopy specificity rises.
- **More looks, more flags.** NP endoscopies flagged by R49 carry more samples than unflagged ones (2.27 against 1.88; +0.39 [+0.05, +0.74]). Flagged NP patients have more endoscopies (4.9 against 4.0) and more samples (10.2 against 7.7) than NP patients who are never flagged. The maximum over more samples and more endoscopies inflates the chance of a false flag.
- **Biology that looks like risk.** Flagged NP patients have longer Barrett's segments (Prague M 5.1 against 3.6 cm; +1.6 [+0.5, +2.7]) and a higher highest sheet grade (+0.54 [+0.07, +0.97]; more ID/LGD). What separates false-positive NP endoscopies from true-positive progressor endoscopies is mostly what the model cannot see in this cohort: aberrant p53 (0.7% against 22%), a later HGD+ report, and the H&E and copy-number scores themselves (both lower in false positives).
- **Slide and study artefacts.** Flagged NP patients more often have slides from the C13210 scanner (25% against 9%) and a higher background-tile share (0.060 against 0.019). They are less often sequenced in batches holding only one class (41% against 82%; −0.41 [−0.62, −0.18]). The "marker on slide" note is on 7.5% of false-positive NP endoscopies and 0.3% of true negatives. Only 11 NP patients are never flagged under R49, so these patient contrasts rest on a small group.
- **Inside the H&E score, false positives are a diffuse, moderate shift, not a few odd tiles.** The logit decomposes exactly into tile contributions. In false-positive slides, 53% of tiles push the score up (true negatives 40%, true positives 63%). The positive evidence is *less* concentrated than in true negatives (top-16 tiles hold 29% of the positive contribution against 38%). Background, edge, blurred and ink tiles add almost nothing to the score (background contribution +0.05 logit). Removing them, trimming, or using the median moves false-positive and true-positive scores alike (all differences in score change cross 0).

**Fixes (nested, against R49 and P1 90%).**
- **Robust tile aggregates do not help.** Means over non-background or core tiles, trimmed means and medians leave sample AUROC unchanged or lower (0.846 / 0.804 / 0.846 / 0.837 against 0.847). Within R49 they change NP patients flagged by −0.1 to +0.4.
- **Single-feature vetoes and second-stage filters on flagged endoscopies** raise endoscopy specificity, up to about 0.64 from 0.56. But among variants losing at most 0.5 progressor patients they remove at most about 1 NP patient (typically at a cost of 0.2–0.4 progressor patients); larger reductions cost more progressors. Their held-out AUROC among flagged endoscopies is 0.68–0.75. The apparent (non-nested) versions look much better (down to 25 NP patients with clinical features), which shows how easily these filters overfit.
- **Most promising deployable change: penalise the endoscopy maximum for the number of samples** (score = max logit − c·log(samples), c chosen on training patients).
  - Within R49 (keeping training sensitivity within 0.02): NP patients flagged 30.8 against 31.8 (−1.0 [−1.8, −0.3]); progressor patients caught 30.7 against 31.1 (−0.4 [−1.3, 0.0]). It also sequences fewer samples (1.75 against 1.94 per patient).
  - Applied to H&E alone, without sequencing: caught 30.8, NP flagged 32.6, against P1's 31.1 / 36.0. That is −3.4 [−6.6, −0.4] NP against P1 at 90%, but only −2.3 [−5.7, +1.4] against P1 matched to the same endoscopy sensitivity. Endoscopy AUROC rises from 0.837 to 0.850 (+0.013 [−0.011, +0.036]).
  - None of these clears the bar of fewer NP patients with no progressor loss and an interval excluding zero.
- **Not deployable, but informative about confounding.** A filter that knows only the progressor share of the sample's sequencing batch, computed from training patients only, removes 2.9 [1.4, 4.8] NP patients from R49 with no progressor loss. Using batch shares computed from all labels, a leak, removes 12 NP patients. Slide metadata (scanner, slide age, biopsy year) removes none. Sequencing-batch structure carries label information that the H&E-driven flags partly track. This is a confounding risk for transport to ACE-B, not a fix.


Checks: refitted H&E model coefficients reproduce every stored outer and inner prediction (max |Δ prediction| 1e-16, λ identical; `ex_e1_coef.R`); the tile decomposition b0 + mean_t u_t reproduces the stored logits (max |Δ logit| outer 1.4e-06 over 6758 sample x repeat cells, inner 1.5e-06 over 60825). Tiles: 174848 stored UNI2-h tile positions re-read for pixel statistics; tile flags (share of all tiles): bg 0.057, edge 0.391, ink 0.002, blur 0.094.

### E1.1 Who gets flagged

Check against round 8: R49 caught 31.1 / NP flagged 31.8 (31.1 / 31.8); P1 90% 31.1 / 36.0 (31.1 / 36.0).

**R49.** Endoscopies per repeat (mean): false-positive NP 88.0, true-negative NP 112.0, true-positive P 79.8, false-negative P 8.2.

| Covariate | FP-NP | TN-NP | TP-P | Δ FP−TN [95% CI] (std.) | Δ FP−TP [95% CI] (std.) | AUROC TP vs FP |
|---|---|---|---|---|---|---|
| later_db_group = HGD+ | 0.022 | 0.019 | 0.649 | +0.003 [-0.005, +0.019] (+0.021) | -0.627 [-0.830, -0.417] (-1.778) | 0.814 |
| batch_progressor_share (top-H&E sample) | 0.281 | 0.211 | 0.695 | +0.069 [-0.006, +0.143] (+0.294) | -0.414 [-0.548, -0.285] (-1.679) | 0.865 |
| later_db_group = NDBE/ID | 0.617 | 0.669 | 0.177 | -0.052 [-0.201, +0.093] (-0.108) | +0.441 [+0.176, +0.686] (+1.009) | 0.280 |
| H&E score: max logit L-IMG (repeat mean) | -0.125 | -2.880 | 2.447 | +2.755 [+2.324, +3.226] (+1.688) | -2.572 [-3.567, -1.705] (-1.001) | 0.753 |
| copy number: max logit L-CNV (repeat mean) | -0.718 | -2.391 | 1.410 | +1.673 [+1.090, +2.231] (+0.973) | -2.128 [-2.976, -1.287] (-0.903) | 0.732 |
| endoscopies_of_patient | 5.268 | 5.018 | 3.867 | +0.250 [-0.212, +0.687] (+0.175) | +1.402 [+0.135, +2.563] (+0.772) | 0.255 |
| p53_aberrant (any, of tested) | 0.007 | 0.005 | 0.224 | +0.002 [-0.001, +0.007] (+0.020) | -0.217 [-0.318, -0.121] (-0.720) | 0.608 |
| later_db_group = no later report | 0.308 | 0.265 | 0.050 | +0.043 [-0.096, +0.182] (+0.094) | +0.257 [+0.080, +0.439] (+0.713) | 0.371 |
| sat_mean (top-H&E sample) | 0.267 | 0.261 | 0.241 | +0.006 [-0.005, +0.016] (+0.113) | +0.026 [+0.008, +0.044] (+0.487) | 0.355 |
| position_from_last (0 = last) | 2.203 | 1.959 | 1.413 | +0.244 [-0.054, +0.530] (+0.146) | +0.790 [+0.123, +1.404] (+0.479) | 0.353 |
| db_grade_at_endoscopy (0 NDBE .. 3 HGD) | 0.511 | 0.363 | 0.908 | +0.148 [-0.024, +0.321] (+0.200) | -0.397 [-0.738, -0.044] (-0.445) | 0.602 |
| grade_sheet_LGD | 0.133 | 0.094 | 0.306 | +0.040 [-0.030, +0.111] (+0.125) | -0.173 [-0.329, -0.018] (-0.426) | 0.587 |
| blur_share (top-H&E sample) | 0.092 | 0.095 | 0.149 | -0.002 [-0.022, +0.017] (-0.022) | -0.056 [-0.097, -0.017] (-0.407) | 0.619 |
| db_report_found | 0.923 | 0.900 | 0.786 | +0.023 [-0.047, +0.087] (+0.081) | +0.137 [-0.012, +0.317] (+0.396) | 0.431 |
| position_in_series (0 = first) | 2.066 | 2.059 | 1.453 | +0.007 [-0.291, +0.289] (+0.004) | +0.612 [-0.003, +1.187] (+0.384) | 0.382 |
| first_endoscopy | 0.190 | 0.235 | 0.349 | -0.045 [-0.125, +0.033] (-0.110) | -0.159 [-0.271, -0.071] (-0.365) | 0.580 |
| prague_M | 5.054 | 4.277 | 4.185 | +0.777 [+0.114, +1.597] (+0.322) | +0.869 [-0.466, +2.103] (+0.362) | 0.382 |
| db_grade_ID_or_worse | 0.324 | 0.245 | 0.484 | +0.079 [-0.022, +0.185] (+0.177) | -0.159 [-0.340, +0.028] (-0.329) | 0.580 |
| grade_sheet_max (0 NDBE, 1 ID, 2 LGD) | 0.421 | 0.296 | 0.686 | +0.125 [-0.016, +0.268] (+0.186) | -0.265 [-0.585, +0.048] (-0.324) | 0.565 |
| edge_share (top-H&E sample) | 0.390 | 0.396 | 0.433 | -0.006 [-0.033, +0.020] (-0.055) | -0.043 [-0.096, +0.008] (-0.321) | 0.600 |
| same_block (top-H&E sample) | 0.930 | 0.965 | 0.989 | -0.035 [-0.090, +0.016] (-0.157) | -0.058 [-0.113, -0.009] (-0.300) | 0.529 |
| samples_per_endoscopy | 2.268 | 1.879 | 1.883 | +0.389 [+0.053, +0.738] (+0.284) | +0.385 [-0.159, +0.917] (+0.289) | 0.428 |
| biopsy_year | 2005.732 | 2006.026 | 2006.787 | -0.295 [-1.041, +0.483] (-0.082) | -1.055 [-2.971, +0.763] (-0.246) | 0.580 |
| slide_age_years (top-H&E sample) | 11.283 | 11.030 | 10.269 | +0.253 [-0.523, +0.994] (+0.070) | +1.013 [-0.810, +2.943] (+0.235) | 0.423 |
| age | 66.349 | 64.592 | 64.166 | +1.757 [-1.392, +4.847] (+0.170) | +2.183 [-3.111, +7.241] (+0.221) | 0.407 |
| later_db_group = LGD | 0.053 | 0.047 | 0.112 | +0.006 [-0.033, +0.052] (+0.028) | -0.058 [-0.220, +0.076] (-0.214) | 0.529 |
| lapvar_median (top-H&E sample) | 398.961 | 371.933 | 362.204 | +27.028 [-10.171, +66.572] (+0.154) | +36.757 [-16.687, +90.555] (+0.200) | 0.440 |
| grade_sheet_ID_or_LGD | 0.288 | 0.202 | 0.380 | +0.085 [+0.000, +0.169] (+0.199) | -0.092 [-0.262, +0.080] (-0.197) | 0.546 |
| p53_tested | 0.784 | 0.795 | 0.700 | -0.011 [-0.106, +0.086] (-0.026) | +0.083 [-0.102, +0.247] (+0.191) | 0.458 |
| note_z_levels (top-H&E sample) | 0.052 | 0.058 | 0.094 | -0.007 [-0.056, +0.043] (-0.030) | -0.042 [-0.125, +0.037] (-0.164) | 0.521 |
| scanner_C13210 (top-H&E sample) | 0.275 | 0.203 | 0.207 | +0.072 [-0.030, +0.176] (+0.169) | +0.069 [-0.106, +0.241] (+0.161) | 0.466 |
| later_db_group = not linked | 0.000 | 0.000 | 0.013 | +0.000 [+0.000, +0.000] (–) | -0.013 [-0.044, +0.000] (-0.160) | 0.506 |
| note_marker (top-H&E sample) | 0.075 | 0.003 | 0.041 | +0.072 [+0.029, +0.117] (+0.377) | +0.034 [-0.023, +0.094] (+0.146) | 0.483 |
| bg_share (top-H&E sample) | 0.065 | 0.044 | 0.052 | +0.022 [-0.002, +0.048] (+0.214) | +0.014 [-0.029, +0.056] (+0.129) | 0.483 |
| tissue_tiles (top-H&E sample) | 704.696 | 608.911 | 591.389 | +95.785 [-106.635, +307.137] (+0.094) | +113.307 [-126.523, +379.048] (+0.119) | 0.499 |
| dark_share (top-H&E sample) | 0.001 | 0.000 | 0.001 | +0.001 [-0.000, +0.003] (+0.205) | +0.001 [-0.001, +0.003] (+0.114) | 0.465 |
| bg_share (endoscopy max) | 0.078 | 0.054 | 0.065 | +0.024 [-0.009, +0.055] (+0.195) | +0.013 [-0.041, +0.064] (+0.106) | 0.492 |
| log_tissue_tiles (top-H&E sample) | 5.872 | 5.776 | 5.770 | +0.096 [-0.113, +0.302] (+0.096) | +0.102 [-0.188, +0.417] (+0.097) | 0.499 |
| years_to_reference (event or last endoscopy) | 3.893 | 3.825 | 4.150 | +0.068 [-0.702, +0.774] (+0.021) | -0.257 [-1.227, +0.771] (-0.083) | 0.538 |
| sex_M | 0.712 | 0.726 | 0.737 | -0.014 [-0.197, +0.151] (-0.031) | -0.025 [-0.272, +0.220] (-0.055) | 0.512 |
| tissue_tiles (endoscopy mean) | 635.103 | 622.621 | 649.434 | +12.481 [-201.044, +207.274] (+0.013) | -14.332 [-269.246, +248.337] (-0.016) | 0.529 |
| batch_single_class (top-H&E sample) | 0.387 | 0.537 | 0.395 | -0.150 [-0.316, +0.016] (-0.304) | -0.007 [-0.278, +0.244] (-0.015) | 0.504 |
| n_slides (top-H&E sample) | 1.023 | 1.000 | 1.025 | +0.023 [+0.000, +0.058] (+0.216) | -0.002 [-0.064, +0.050] (-0.011) | 0.495 |
| ink_share (top-H&E sample) | 0.000 | 0.000 | 0.000 | +0.000 [+0.000, +0.000] (–) | -0.000 [-0.000, +0.000] (–) | 0.501 |

Patient level (R49; weighted by share of repeats flagged): NP flagged 31.8, NP never flagged 11.2, P caught 31.1, P missed 0.9.

| Patient covariate | NP flagged | NP never | P caught | Δ NP flagged − never [95% CI] (std.) |
|---|---|---|---|---|
| endoscopies | 4.896 | 3.955 | 2.785 | +0.941 [+0.102, +1.784] (+0.650) |
| years_followed (first endoscopy to reference) | 6.676 | 6.276 | 5.371 | +0.401 [-1.550, +2.339] (+0.126) |
| samples | 10.170 | 7.732 | 5.113 | +2.438 [+0.175, +4.729] (+0.567) |
| age (mean) | 66.032 | 63.226 | 64.226 | +2.805 [-2.853, +8.553] (+0.287) |
| sex_M (mean) | 0.733 | 0.777 | 0.775 | -0.044 [-0.272, +0.194] (-0.103) |
| prague_M (mean) | 5.139 | 3.562 | 4.875 | +1.577 [+0.491, +2.743] (+0.706) |
| tissue_tiles (mean) | 499.274 | 438.571 | 514.470 | +60.703 [-210.695, +282.972] (+0.162) |
| slide_age_years (mean) | 10.821 | 10.205 | 9.919 | +0.615 [-0.461, +1.734] (+0.301) |
| scanner_C13210 (mean) | 0.254 | 0.093 | 0.195 | +0.161 [+0.008, +0.304] (+0.575) |
| batch_single_class (mean) | 0.413 | 0.821 | 0.404 | -0.408 [-0.619, -0.182] (-0.950) |
| bg_share (mean) | 0.060 | 0.019 | 0.044 | +0.041 [+0.008, +0.074] (+0.637) |
| grade_sheet (max) | 1.094 | 0.554 | 0.984 | +0.541 [+0.072, +0.967] (+0.648) |
| later_db_group = no later report | 0.311 | 0.188 | 0.064 | +0.124 [-0.106, +0.345] (+0.289) |
| later_db_group = NDBE/ID | 0.588 | 0.741 | 0.129 | -0.153 [-0.389, +0.106] (-0.329) |
| later_db_group = LGD | 0.069 | 0.071 | 0.096 | -0.002 [-0.151, +0.109] (-0.009) |
| later_db_group = HGD+ | 0.031 | 0.000 | 0.678 | +0.031 [+0.000, +0.108] (+0.254) |
| later_db_group = not linked | 0.000 | 0.000 | 0.032 | +0.000 [+0.000, +0.000] (–) |

**P1 90%.** Endoscopies per repeat (mean): false-positive NP 95.1, true-negative NP 104.9, true-positive P 79.0, false-negative P 9.0.

| Covariate | FP-NP | TN-NP | TP-P | Δ FP−TN [95% CI] (std.) | Δ FP−TP [95% CI] (std.) | AUROC TP vs FP |
|---|---|---|---|---|---|---|
| later_db_group = HGD+ | 0.023 | 0.017 | 0.670 | +0.006 [+0.000, +0.025] (+0.043) | -0.646 [-0.850, -0.437] (-1.852) | 0.823 |
| batch_progressor_share (top-H&E sample) | 0.270 | 0.218 | 0.696 | +0.052 [-0.011, +0.117] (+0.219) | -0.426 [-0.562, -0.293] (-1.707) | 0.867 |
| later_db_group = NDBE/ID | 0.616 | 0.673 | 0.156 | -0.057 [-0.181, +0.069] (-0.119) | +0.461 [+0.207, +0.689] (+1.075) | 0.270 |
| copy number: max logit L-CNV (repeat mean) | -1.261 | -2.007 | 1.299 | +0.747 [+0.132, +1.356] (+0.397) | -2.559 [-3.436, -1.676] (-1.060) | 0.785 |
| H&E score: max logit L-IMG (repeat mean) | -0.044 | -3.142 | 2.548 | +3.098 [+2.717, +3.533] (+2.133) | -2.591 [-3.532, -1.805] (-1.056) | 0.772 |
| p53_aberrant (any, of tested) | 0.001 | 0.011 | 0.226 | -0.010 [-0.032, +0.000] (-0.125) | -0.225 [-0.322, -0.128] (-0.757) | 0.613 |
| endoscopies_of_patient | 5.170 | 5.095 | 3.846 | +0.075 [-0.328, +0.458] (+0.052) | +1.324 [+0.188, +2.424] (+0.745) | 0.261 |
| later_db_group = no later report | 0.294 | 0.274 | 0.051 | +0.020 [-0.105, +0.139] (+0.044) | +0.244 [+0.067, +0.422] (+0.681) | 0.378 |
| sat_mean (top-H&E sample) | 0.268 | 0.260 | 0.239 | +0.007 [-0.004, +0.018] (+0.144) | +0.028 [+0.011, +0.046] (+0.542) | 0.336 |
| position_from_last (0 = last) | 2.176 | 1.965 | 1.371 | +0.211 [-0.134, +0.554] (+0.127) | +0.805 [+0.217, +1.373] (+0.497) | 0.356 |
| db_grade_at_endoscopy (0 NDBE .. 3 HGD) | 0.520 | 0.346 | 0.931 | +0.174 [+0.028, +0.313] (+0.238) | -0.410 [-0.752, -0.066] (-0.459) | 0.605 |
| blur_share (top-H&E sample) | 0.091 | 0.096 | 0.153 | -0.005 [-0.026, +0.016] (-0.051) | -0.062 [-0.103, -0.022] (-0.442) | 0.638 |
| grade_sheet_LGD | 0.135 | 0.088 | 0.310 | +0.047 [-0.024, +0.116] (+0.150) | -0.175 [-0.333, -0.019] (-0.431) | 0.588 |
| db_report_found | 0.913 | 0.908 | 0.776 | +0.005 [-0.071, +0.076] (+0.018) | +0.137 [-0.016, +0.323] (+0.385) | 0.432 |
| prague_M | 5.052 | 4.235 | 4.191 | +0.817 [+0.261, +1.452] (+0.339) | +0.862 [-0.469, +2.035] (+0.367) | 0.381 |
| edge_share (top-H&E sample) | 0.390 | 0.397 | 0.439 | -0.006 [-0.032, +0.022] (-0.055) | -0.049 [-0.103, +0.004] (-0.364) | 0.618 |
| position_in_series (0 = first) | 1.994 | 2.130 | 1.475 | -0.136 [-0.459, +0.185] (-0.082) | +0.519 [-0.069, +1.068] (+0.328) | 0.399 |
| first_endoscopy | 0.202 | 0.227 | 0.345 | -0.025 [-0.110, +0.054] (-0.061) | -0.143 [-0.256, -0.052] (-0.326) | 0.572 |
| grade_sheet_max (0 NDBE, 1 ID, 2 LGD) | 0.435 | 0.274 | 0.699 | +0.161 [+0.031, +0.294] (+0.241) | -0.264 [-0.580, +0.050] (-0.322) | 0.565 |
| db_grade_ID_or_worse | 0.335 | 0.231 | 0.491 | +0.103 [+0.005, +0.195] (+0.231) | -0.157 [-0.343, +0.030] (-0.322) | 0.578 |
| samples_per_endoscopy | 2.284 | 1.839 | 1.888 | +0.445 [+0.090, +0.809] (+0.328) | +0.395 [-0.139, +0.913] (+0.296) | 0.426 |
| same_block (top-H&E sample) | 0.929 | 0.968 | 0.982 | -0.039 [-0.097, +0.014] (-0.178) | -0.053 [-0.113, +0.001] (-0.261) | 0.526 |
| p53_tested | 0.806 | 0.775 | 0.699 | +0.031 [-0.070, +0.131] (+0.077) | +0.107 [-0.086, +0.269] (+0.251) | 0.446 |
| lapvar_median (top-H&E sample) | 399.728 | 369.466 | 355.733 | +30.262 [-4.299, +66.560] (+0.173) | +43.995 [-8.169, +97.108] (+0.246) | 0.425 |
| biopsy_year | 2005.811 | 2005.985 | 2006.702 | -0.174 [-0.946, +0.527] (-0.048) | -0.891 [-2.834, +0.945] (-0.204) | 0.570 |
| scanner_C13210 (top-H&E sample) | 0.270 | 0.203 | 0.188 | +0.067 [-0.025, +0.156] (+0.159) | +0.082 [-0.088, +0.248] (+0.195) | 0.459 |
| slide_age_years (top-H&E sample) | 11.201 | 11.077 | 10.363 | +0.124 [-0.582, +0.886] (+0.034) | +0.838 [-1.055, +2.801] (+0.191) | 0.434 |
| grade_sheet_ID_or_LGD | 0.300 | 0.186 | 0.389 | +0.114 [+0.036, +0.187] (+0.268) | -0.089 [-0.259, +0.074] (-0.188) | 0.544 |
| bg_share (top-H&E sample) | 0.065 | 0.042 | 0.047 | +0.023 [+0.001, +0.046] (+0.227) | +0.018 [-0.024, +0.060] (+0.169) | 0.482 |
| age | 65.761 | 65.004 | 64.075 | +0.757 [-1.978, +3.901] (+0.073) | +1.686 [-3.617, +6.669] (+0.168) | 0.419 |
| later_db_group = LGD | 0.066 | 0.035 | 0.112 | +0.031 [+0.000, +0.078] (+0.142) | -0.045 [-0.211, +0.092] (-0.160) | 0.523 |
| later_db_group = not linked | 0.000 | 0.000 | 0.013 | +0.000 [+0.000, +0.000] (–) | -0.013 [-0.045, +0.000] (-0.160) | 0.506 |
| note_z_levels (top-H&E sample) | 0.050 | 0.059 | 0.090 | -0.009 [-0.063, +0.045] (-0.038) | -0.040 [-0.123, +0.039] (-0.155) | 0.520 |
| tissue_tiles (endoscopy mean) | 561.724 | 684.757 | 659.105 | -123.032 [-355.190, +91.740] (-0.130) | -97.381 [-342.186, +150.665] (-0.121) | 0.530 |
| dark_share (top-H&E sample) | 0.001 | 0.000 | 0.001 | +0.001 [+0.000, +0.003] (+0.209) | +0.001 [-0.001, +0.003] (+0.120) | 0.466 |
| bg_share (endoscopy max) | 0.075 | 0.056 | 0.061 | +0.019 [-0.007, +0.045] (+0.158) | +0.014 [-0.038, +0.063] (+0.114) | 0.498 |
| years_to_reference (event or last endoscopy) | 3.852 | 3.853 | 4.175 | -0.002 [-0.695, +0.655] (-0.001) | -0.323 [-1.211, +0.636] (-0.104) | 0.543 |
| n_slides (top-H&E sample) | 1.012 | 1.009 | 1.025 | +0.003 [-0.022, +0.030] (+0.030) | -0.014 [-0.073, +0.030] (-0.078) | 0.501 |
| note_marker (top-H&E sample) | 0.065 | 0.008 | 0.048 | +0.058 [+0.016, +0.104] (+0.312) | +0.017 [-0.042, +0.078] (+0.074) | 0.491 |
| sex_M | 0.761 | 0.682 | 0.731 | +0.079 [-0.045, +0.205] (+0.177) | +0.030 [-0.199, +0.263] (+0.069) | 0.485 |
| log_tissue_tiles (top-H&E sample) | 5.822 | 5.812 | 5.776 | +0.010 [-0.213, +0.232] (+0.010) | +0.046 [-0.235, +0.363] (+0.045) | 0.502 |
| batch_single_class (top-H&E sample) | 0.416 | 0.518 | 0.399 | -0.102 [-0.244, +0.030] (-0.206) | +0.017 [-0.252, +0.271] (+0.035) | 0.491 |
| tissue_tiles (top-H&E sample) | 609.864 | 684.539 | 600.034 | -74.675 [-302.824, +130.796] (-0.074) | +9.829 [-214.698, +242.845] (+0.012) | 0.502 |
| ink_share (top-H&E sample) | 0.000 | 0.000 | 0.000 | +0.000 [+0.000, +0.000] (–) | -0.000 [-0.000, +0.000] (–) | 0.501 |

Patient level (P1 90%; weighted by share of repeats flagged): NP flagged 36.0, NP never flagged 7.0, P caught 31.1, P missed 0.9.

| Patient covariate | NP flagged | NP never | P caught | Δ NP flagged − never [95% CI] (std.) |
|---|---|---|---|---|
| endoscopies | 4.808 | 3.843 | 2.801 | +0.965 [-0.100, +1.761] (+0.695) |
| years_followed (first endoscopy to reference) | 6.687 | 5.981 | 5.484 | +0.706 [-1.465, +2.416] (+0.236) |
| samples | 9.917 | 7.571 | 5.119 | +2.345 [-0.862, +5.248] (+0.527) |
| age (mean) | 65.900 | 62.219 | 64.063 | +3.682 [-3.546, +11.536] (+0.375) |
| sex_M (mean) | 0.747 | 0.729 | 0.775 | +0.019 [-0.252, +0.371] (+0.042) |
| prague_M (mean) | 5.060 | 3.088 | 4.781 | +1.972 [+0.601, +3.355] (+0.907) |
| tissue_tiles (mean) | 504.433 | 375.620 | 512.772 | +128.813 [-209.599, +321.254] (+0.340) |
| slide_age_years (mean) | 10.792 | 9.983 | 10.208 | +0.809 [-0.625, +2.100] (+0.407) |
| scanner_C13210 (mean) | 0.244 | 0.050 | 0.195 | +0.194 [+0.080, +0.315] (+0.762) |
| batch_single_class (mean) | 0.434 | 0.957 | 0.404 | -0.523 [-0.673, -0.367] (-1.426) |
| bg_share (mean) | 0.056 | 0.012 | 0.044 | +0.045 [+0.017, +0.074] (+0.751) |
| grade_sheet (max) | 1.006 | 0.686 | 0.997 | +0.320 [-0.352, +0.950] (+0.365) |
| later_db_group = no later report | 0.275 | 0.300 | 0.064 | -0.025 [-0.376, +0.284] (-0.055) |
| later_db_group = NDBE/ID | 0.614 | 0.700 | 0.106 | -0.086 [-0.396, +0.272] (-0.182) |
| later_db_group = LGD | 0.083 | 0.000 | 0.096 | +0.083 [+0.000, +0.181] (+0.427) |
| later_db_group = HGD+ | 0.028 | 0.000 | 0.701 | +0.028 [+0.000, +0.095] (+0.240) |
| later_db_group = not linked | 0.000 | 0.000 | 0.032 | +0.000 [+0.000, +0.000] (–) |

**Persistence of false flags.**

| Quantity | R49 | P1 90% |
|---|---|---|
| Flagged endoscopies per ever-flagged NP patient | 2.77 | 2.64 |
| Share of ever-flagged NP patients flagged exactly once | 0.214 | 0.197 |
| Share of an ever-flagged NP patient's endoscopies that are flagged | 0.574 | 0.564 |
| (Progressors: share of a caught patient's endoscopies flagged) | 0.944 | 0.927 |
| Share of all false-flagged NP endoscopies from the 10 / 20 most-flagged NP patients | 0.464 / 0.793 | 0.417 / 0.708 |

Between-patient share of variance (ICC) of the endoscopy H&E score: non-progressors 0.214 [0.087, 0.341], progressors 0.411 [0.179, 0.572] (patients with ≥ 2 pre-event endoscopies; interval from 200 patient-bootstrap draws).

NP endoscopy flags per repeat: flagged by both P1 90% and R49 72.6, by P1 only (cleared by sequencing) 22.5, by R49 only 15.4.

### E1.2 Inside the H&E score

Logit decomposition check (b0 + mean tile score = stored outer logit), max |difference| × 1000: 0.001.

**R49** (top-H&E sample of each endoscopy, outer model; per-repeat class means averaged):

| Tile summary | FP-NP | TN-NP | TP-P | Δ FP−TP [95% CI] (std.) | AUROC TP vs FP |
|---|---|---|---|---|---|
| mean | 0.782 | -2.329 | 3.309 | -2.527 [-3.543, -1.675] (-0.934) | 0.740 |
| median | 0.755 | -2.209 | 3.205 | -2.450 [-3.491, -1.572] (-0.892) | 0.727 |
| trim10 | 0.775 | -2.269 | 3.270 | -2.495 [-3.529, -1.638] (-0.920) | 0.735 |
| nonbg_mean | 0.787 | -2.328 | 3.357 | -2.570 [-3.612, -1.715] (-0.951) | 0.746 |
| core_mean | 0.581 | -2.514 | 3.054 | -2.473 [-3.663, -1.447] (-0.795) | 0.696 |
| noink_mean | 0.782 | -2.329 | 3.309 | -2.527 [-3.543, -1.676] (-0.934) | 0.740 |
| sd | 8.947 | 9.261 | 9.296 | -0.350 [-0.830, +0.161] (-0.161) | 0.556 |
| p90 | 12.111 | 9.278 | 15.202 | -3.091 [-4.186, -2.090] (-0.720) | 0.708 |
| max | 26.380 | 23.622 | 29.904 | -3.524 [-5.159, -1.815] (-0.431) | 0.626 |
| top16_mean | 18.474 | 15.605 | 21.808 | -3.334 [-4.621, -2.064] (-0.587) | 0.674 |
| rest_mean | -0.382 | -3.524 | 2.093 | -2.475 [-3.535, -1.596] (-0.920) | 0.733 |
| share_pos | 0.533 | 0.404 | 0.628 | -0.095 [-0.135, -0.061] (-0.906) | 0.719 |
| gini_pos | 0.411 | 0.423 | 0.393 | +0.018 [+0.008, +0.030] (+0.531) | 0.362 |
| n_u_gt2 | 113.997 | 81.711 | 143.323 | -29.326 [-42.903, -18.051] (-0.770) | 0.722 |
| n_u_gt5 | 79.993 | 53.709 | 109.873 | -29.880 [-42.188, -19.299] (-0.831) | 0.731 |
| frac_u_gt2 | 0.439 | 0.319 | 0.544 | -0.105 [-0.147, -0.070] (-0.947) | 0.735 |
| bg_contrib | 0.045 | -0.097 | 0.109 | -0.064 [-0.169, +0.028] (-0.160) | 0.534 |
| edge_contrib | 0.386 | -0.847 | 1.690 | -1.304 [-1.896, -0.795] (-0.819) | 0.726 |
| ink_contrib | 0.000 | 0.000 | -0.000 | +0.000 [+0.000, +0.001] (+0.143) | 0.492 |
| blur_contrib | 0.177 | -0.054 | 0.729 | -0.551 [-0.871, -0.272] (-0.592) | 0.655 |
| top16_contrib | 1.141 | 0.975 | 1.344 | -0.203 [-0.281, -0.129] (-0.583) | 0.668 |
| pos_sum | 4.007 | 2.668 | 5.789 | -1.782 [-2.469, -1.223] (-0.848) | 0.736 |
| conc_top16_of_pos | 0.294 | 0.380 | 0.252 | +0.042 [+0.024, +0.063] (+0.779) | 0.300 |
| mean_without_top16 | -0.382 | -3.524 | 2.093 | -2.475 [-3.535, -1.596] (-0.920) | 0.733 |
| score_change_if_bg_removed (nonbg_mean - mean) | 0.005 | 0.001 | 0.048 | -0.043 [-0.163, +0.066] (-0.110) | 0.500 |
| score_change_if_edge_and_bg_removed (core_mean - mean) | -0.201 | -0.185 | -0.254 | +0.054 [-0.508, +0.670] (+0.033) | 0.515 |
| score_change_trimmed10 (trim10 - mean) | -0.007 | 0.059 | -0.039 | +0.032 [-0.031, +0.090] (+0.130) | 0.482 |
| score_change_median (median - mean) | -0.027 | 0.120 | -0.103 | +0.076 [-0.058, +0.205] (+0.123) | 0.462 |
| score_change_drop_top16 (rest_mean - mean) | -1.164 | -1.196 | -1.215 | +0.051 [-0.021, +0.119] (+0.168) | 0.450 |

**P1 90%** (top-H&E sample of each endoscopy, outer model; per-repeat class means averaged):

| Tile summary | FP-NP | TN-NP | TP-P | Δ FP−TP [95% CI] (std.) | AUROC TP vs FP |
|---|---|---|---|---|---|
| mean | 0.882 | -2.637 | 3.408 | -2.525 [-3.464, -1.751] (-0.980) | 0.759 |
| median | 0.882 | -2.527 | 3.289 | -2.408 [-3.356, -1.615] (-0.916) | 0.736 |
| trim10 | 0.880 | -2.576 | 3.367 | -2.487 [-3.438, -1.702] (-0.963) | 0.752 |
| nonbg_mean | 0.882 | -2.632 | 3.446 | -2.564 [-3.542, -1.771] (-0.994) | 0.762 |
| core_mean | 0.709 | -2.846 | 3.095 | -2.386 [-3.538, -1.403] (-0.785) | 0.694 |
| noink_mean | 0.882 | -2.637 | 3.408 | -2.526 [-3.464, -1.751] (-0.980) | 0.759 |
| sd | 8.932 | 9.297 | 9.318 | -0.386 [-0.884, +0.162] (-0.174) | 0.558 |
| p90 | 12.175 | 9.019 | 15.359 | -3.184 [-4.225, -2.233] (-0.756) | 0.719 |
| max | 26.233 | 23.563 | 29.977 | -3.744 [-5.364, -1.990] (-0.456) | 0.631 |
| top16_mean | 18.497 | 15.379 | 21.943 | -3.446 [-4.701, -2.182] (-0.608) | 0.680 |
| rest_mean | -0.284 | -3.833 | 2.190 | -2.474 [-3.435, -1.675] (-0.964) | 0.750 |
| share_pos | 0.539 | 0.390 | 0.632 | -0.093 [-0.130, -0.062] (-0.953) | 0.729 |
| gini_pos | 0.410 | 0.425 | 0.392 | +0.018 [+0.009, +0.030] (+0.529) | 0.360 |
| n_u_gt2 | 114.312 | 79.196 | 144.424 | -30.112 [-42.732, -19.559] (-0.818) | 0.743 |
| n_u_gt5 | 80.234 | 51.655 | 110.893 | -30.659 [-42.289, -20.821] (-0.871) | 0.748 |
| frac_u_gt2 | 0.444 | 0.307 | 0.548 | -0.105 [-0.143, -0.071] (-0.991) | 0.747 |
| bg_contrib | 0.054 | -0.115 | 0.126 | -0.072 [-0.169, +0.014] (-0.190) | 0.541 |
| edge_contrib | 0.396 | -0.944 | 1.750 | -1.353 [-1.888, -0.862] (-0.870) | 0.746 |
| ink_contrib | 0.000 | 0.000 | -0.000 | +0.000 [+0.000, +0.001] (+0.140) | 0.492 |
| blur_contrib | 0.182 | -0.074 | 0.744 | -0.563 [-0.874, -0.286] (-0.605) | 0.662 |
| top16_contrib | 1.148 | 0.957 | 1.352 | -0.204 [-0.280, -0.133] (-0.590) | 0.671 |
| pos_sum | 4.041 | 2.545 | 5.853 | -1.812 [-2.462, -1.280] (-0.880) | 0.748 |
| conc_top16_of_pos | 0.291 | 0.389 | 0.249 | +0.042 [+0.027, +0.059] (+0.868) | 0.282 |
| mean_without_top16 | -0.284 | -3.833 | 2.190 | -2.474 [-3.435, -1.675] (-0.964) | 0.750 |
| score_change_if_bg_removed (nonbg_mean - mean) | -0.000 | 0.005 | 0.039 | -0.039 [-0.153, +0.062] (-0.102) | 0.500 |
| score_change_if_edge_and_bg_removed (core_mean - mean) | -0.173 | -0.209 | -0.313 | +0.139 [-0.434, +0.772] (+0.084) | 0.497 |
| score_change_trimmed10 (trim10 - mean) | -0.003 | 0.061 | -0.041 | +0.038 [-0.023, +0.097] (+0.158) | 0.477 |
| score_change_median (median - mean) | -0.000 | 0.110 | -0.118 | +0.118 [-0.020, +0.248] (+0.189) | 0.448 |
| score_change_drop_top16 (rest_mean - mean) | -1.166 | -1.196 | -1.218 | +0.051 [-0.022, +0.119] (+0.167) | 0.452 |

### E1.3 Fixes

226 nested rule variants were scored. Deployable variants (no batch, slide-metadata or label information) ranked by Δ non-progressor patients flagged against R49, among those with Δ progressor patients caught ≥ −0.5 (top 25; all rows in `summary.json`):

| Rank | Rule | Caught | NP flagged | Endo sens / spec | Seq / patient | Δ NP flagged vs R49 [CI] | Δ caught vs R49 [CI] | Δ NP flagged vs P1 [CI] | Δ caught vs P1 [CI] | Apparent (optimistic) caught / NP flagged |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | R49 veto auto eps 0.05 | 30.8 | 30.8 | 0.848 / 0.615 | 1.94 | -1.0 [-1.9, -0.3] | -0.3 [-0.8, +0.0] | -5.2 [-8.5, -2.3] | -0.3 [-1.9, +1.6] | – |
| 2 | R49 on max - c log(samples) eps 0.02 | 30.7 | 30.8 | 0.894 / 0.614 | 1.75 | -1.0 [-1.8, -0.3] | -0.4 [-1.3, +0.0] | -5.2 [-8.4, -2.3] | -0.4 [-1.6, +0.6] | – |
| 3 | R49 filter image quality + tile eps 0.05 | 30.7 | 30.9 | 0.859 / 0.601 | 1.94 | -0.9 [-1.8, -0.2] | -0.4 [-1.3, +0.0] | -5.1 [-8.2, -2.3] | -0.4 [-1.6, +0.6] | 30.3 / 29.8 |
| 4 | R49 veto auto eps 0.02 | 30.9 | 31.1 | 0.872 / 0.597 | 1.94 | -0.7 [-1.5, -0.1] | -0.2 [-0.5, +0.0] | -4.9 [-8.0, -2.1] | -0.2 [-1.6, +1.5] | – |
| 5 | R49 veto median eps 0.05 | 30.9 | 31.2 | 0.872 / 0.617 | 1.94 | -0.6 [-1.8, +0.0] | -0.2 [-0.7, +0.0] | -4.8 [-8.0, -2.0] | -0.2 [-1.5, +1.2] | 30.8 / 31.2 |
| 6 | R49 veto core_mean eps 0.05 | 31.1 | 31.2 | 0.855 / 0.618 | 1.94 | -0.6 [-1.3, -0.1] | +0.0 [+0.0, +0.0] | -4.8 [-7.9, -1.9] | +0.0 [-1.5, +1.9] | 31.1 / 31.5 |
| 7 | R49 veto gini_pos eps 0.05 | 30.6 | 31.2 | 0.851 / 0.596 | 1.94 | -0.6 [-1.1, -0.2] | -0.5 [-1.0, -0.1] | -4.8 [-7.9, -1.9] | -0.5 [-2.0, +1.1] | 30.9 / 31.4 |
| 8 | R49 veto conc_top16_of_pos eps 0.05 | 30.9 | 31.2 | 0.866 / 0.601 | 1.94 | -0.6 [-1.6, +0.0] | -0.2 [-0.7, +0.0] | -4.8 [-8.0, -2.1] | -0.2 [-1.5, +1.2] | 31.0 / 31.3 |
| 9 | R49 filter tile contributions eps 0.05 | 31.1 | 31.2 | 0.866 / 0.602 | 1.94 | -0.6 [-1.3, -0.1] | +0.0 [+0.0, +0.0] | -4.8 [-7.9, -2.0] | +0.0 [-1.5, +1.9] | 30.6 / 30.5 |
| 10 | R49 veto share_pos eps 0.05 | 31.0 | 31.3 | 0.881 / 0.605 | 1.94 | -0.5 [-1.5, +0.0] | -0.1 [-0.3, +0.0] | -4.7 [-7.9, -1.9] | -0.1 [-1.5, +1.6] | 30.9 / 30.8 |
| 11 | R49 on max - c log(samples) eps 0.0 | 30.8 | 31.3 | 0.900 / 0.596 | 1.83 | -0.5 [-1.2, +0.0] | -0.3 [-1.0, +0.0] | -4.7 [-7.8, -1.9] | -0.3 [-1.5, +0.9] | – |
| 12 | R49 veto auto eps 0.0 | 31.1 | 31.4 | 0.882 / 0.580 | 1.94 | -0.4 [-0.9, +0.0] | +0.0 [+0.0, +0.0] | -4.6 [-7.7, -1.7] | +0.0 [-1.5, +1.9] | – |
| 13 | R49 veto p90 eps 0.05 | 31.1 | 31.4 | 0.900 / 0.573 | 1.94 | -0.4 [-0.9, +0.0] | +0.0 [+0.0, +0.0] | -4.6 [-7.7, -1.8] | +0.0 [-1.5, +1.9] | 30.7 / 30.4 |
| 14 | R49 veto frac_u_gt2 eps 0.05 | 31.0 | 31.4 | 0.892 / 0.588 | 1.94 | -0.4 [-1.1, +0.0] | -0.1 [-0.3, +0.0] | -4.6 [-7.7, -1.8] | -0.1 [-1.5, +1.6] | 30.8 / 30.8 |
| 15 | R49 veto mean eps 0.02 | 30.7 | 31.5 | 0.880 / 0.596 | 1.94 | -0.3 [-0.7, +0.0] | -0.4 [-0.9, +0.0] | -4.5 [-7.6, -1.6] | -0.4 [-1.8, +1.3] | 30.8 / 31.3 |
| 16 | R49 veto trim10 eps 0.02 | 30.6 | 31.5 | 0.880 / 0.593 | 1.94 | -0.3 [-0.8, +0.0] | -0.5 [-1.0, -0.1] | -4.5 [-7.7, -1.6] | -0.5 [-2.0, +1.5] | 30.9 / 31.5 |
| 17 | R49 veto conc_top16_of_pos eps 0.02 | 31.0 | 31.5 | 0.892 / 0.582 | 1.94 | -0.3 [-0.7, +0.0] | -0.1 [-0.3, +0.0] | -4.5 [-7.6, -1.6] | -0.1 [-1.5, +1.6] | 31.0 / 31.6 |
| 18 | R49 veto bg_share eps 0.05 | 31.1 | 31.5 | 0.855 / 0.579 | 1.94 | -0.3 [-0.8, +0.0] | +0.0 [+0.0, +0.0] | -4.5 [-7.7, -1.4] | +0.0 [-1.5, +1.9] | 31.1 / 31.8 |
| 19 | R49 veto edge_share eps 0.05 | 30.7 | 31.5 | 0.849 / 0.587 | 1.94 | -0.3 [-0.8, +0.0] | -0.4 [-1.1, +0.0] | -4.5 [-7.7, -1.3] | -0.4 [-2.0, +1.5] | 31.1 / 31.3 |
| 20 | R49 veto bg_contrib eps 0.05 | 30.8 | 31.5 | 0.839 / 0.600 | 1.94 | -0.3 [-0.7, +0.0] | -0.3 [-0.8, +0.0] | -4.5 [-7.7, -1.4] | -0.3 [-1.9, +1.5] | 31.1 / 31.6 |
| 21 | R49 filter clinical eps 0.02 | 30.8 | 31.5 | 0.898 / 0.584 | 1.94 | -0.3 [-0.7, +0.0] | -0.3 [-1.0, +0.0] | -4.5 [-7.6, -1.5] | -0.3 [-1.5, +0.9] | 30.2 / 28.3 |
| 22 | R49 veto share_pos eps 0.0 | 30.9 | 31.6 | 0.900 / 0.570 | 1.94 | -0.2 [-0.5, +0.0] | -0.2 [-0.7, +0.0] | -4.4 [-7.6, -1.5] | -0.2 [-1.7, +1.8] | 31.1 / 31.6 |
| 23 | R49 veto max eps 0.02 | 30.7 | 31.6 | 0.895 / 0.565 | 1.94 | -0.2 [-0.5, +0.0] | -0.4 [-0.8, -0.1] | -4.4 [-7.5, -1.4] | -0.4 [-2.0, +1.6] | 31.1 / 31.5 |
| 24 | R49 veto share_pos eps 0.02 | 31.0 | 31.6 | 0.892 / 0.579 | 1.94 | -0.2 [-0.5, +0.0] | -0.1 [-0.3, +0.0] | -4.4 [-7.6, -1.5] | -0.1 [-1.6, +1.8] | 31.1 / 31.5 |
| 25 | R49 veto gini_pos eps 0.02 | 30.7 | 31.6 | 0.882 / 0.572 | 1.94 | -0.2 [-0.5, +0.0] | -0.4 [-1.0, +0.0] | -4.4 [-7.5, -1.4] | -0.4 [-2.1, +1.5] | 31.1 / 31.8 |

Not deployable (they use sequencing-batch composition or slide metadata; shown to measure confounding, not as fixes):

| Rule | Caught | NP flagged | Δ NP flagged vs R49 [CI] | Δ caught vs R49 [CI] | Apparent caught / NP flagged |
|---|---|---|---|---|---|
| R49 filter artefact incl. batch shares from all labels (LEAKS LABELS; demonstration only) eps 0.05 | 31.1 | 19.6 | -12.2 [-16.9, -7.5] | +0.0 [+0.0, +0.0] | 31.1 / 17.5 |
| R49 filter artefact incl. batch shares from all labels (LEAKS LABELS; demonstration only) eps 0.02 | 31.1 | 20.7 | -11.1 [-15.5, -6.8] | +0.0 [+0.0, +0.0] | 31.1 / 18.9 |
| P1 90% filter artefact incl. batch shares from all labels (LEAKS LABELS; demonstration only) eps 0.05 | 31.0 | 21.1 | -10.7 [-16.1, -5.1] | -0.1 [-2.0, +1.4] | 30.9 / 18.6 |
| R49 filter artefact incl. batch shares from all labels (LEAKS LABELS; demonstration only) eps 0.0 | 31.1 | 21.6 | -10.2 [-14.3, -6.1] | +0.0 [+0.0, +0.0] | 31.1 / 19.2 |
| P1 90% filter artefact incl. batch shares from all labels (LEAKS LABELS; demonstration only) eps 0.02 | 31.1 | 22.7 | -9.1 [-14.1, -3.9] | +0.0 [-1.9, +1.5] | 31.0 / 20.7 |
| P1 90% filter artefact incl. batch shares from all labels (LEAKS LABELS; demonstration only) eps 0.0 | 31.1 | 24.0 | -7.8 [-12.5, -3.1] | +0.0 [-1.9, +1.5] | 31.1 / 21.0 |
| R49 filter sequencing batch progressor share, training labels only (not deployable) eps 0.05 | 31.1 | 28.9 | -2.9 [-4.8, -1.4] | +0.0 [+0.0, +0.0] | 31.1 / 22.5 |
| R49 filter sequencing batch progressor share, training labels only (not deployable) eps 0.02 | 31.1 | 30.4 | -1.4 [-2.6, -0.5] | +0.0 [+0.0, +0.0] | 31.1 / 26.0 |
| P1 90% filter sequencing batch progressor share, training labels only (not deployable) eps 0.05 | 31.1 | 31.1 | -0.7 [-3.7, +2.3] | +0.0 [-1.9, +1.5] | 31.1 / 24.5 |
| R49 filter sequencing batch progressor share, training labels only (not deployable) eps 0.0 | 31.1 | 31.2 | -0.6 [-1.3, -0.1] | +0.0 [+0.0, +0.0] | 31.1 / 29.2 |
| R49 filter slide metadata: scanner, slide age, biopsy year (not deployable) eps 0.05 | 30.9 | 31.7 | -0.1 [-0.3, +0.0] | -0.2 [-0.7, +0.0] | 30.7 / 31.1 |
| R49 filter slide metadata: scanner, slide age, biopsy year (not deployable) eps 0.0 | 31.1 | 31.8 | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | 31.1 / 31.7 |
| R49 filter slide metadata: scanner, slide age, biopsy year (not deployable) eps 0.02 | 31.1 | 31.8 | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | 31.0 / 31.7 |
| P1 90% filter sequencing batch progressor share, training labels only (not deployable) eps 0.02 | 31.1 | 32.7 | +0.9 [-2.0, +3.7] | +0.0 [-1.9, +1.5] | 31.1 / 27.7 |
| P1 90% filter sequencing batch progressor share, training labels only (not deployable) eps 0.0 | 31.1 | 33.9 | +2.1 [-0.8, +5.1] | +0.0 [-1.9, +1.5] | 31.1 / 29.7 |
| P1 90% filter slide metadata: scanner, slide age, biopsy year (not deployable) eps 0.02 | 31.1 | 35.9 | +4.1 [+1.1, +7.2] | +0.0 [-1.9, +1.5] | 31.0 / 35.3 |
| P1 90% filter slide metadata: scanner, slide age, biopsy year (not deployable) eps 0.05 | 30.9 | 35.9 | +4.1 [+1.1, +7.2] | -0.2 [-2.1, +1.3] | 30.4 / 33.5 |
| P1 90% filter slide metadata: scanner, slide age, biopsy year (not deployable) eps 0.0 | 31.1 | 36.0 | +4.2 [+1.2, +7.4] | +0.0 [-1.9, +1.5] | 31.1 / 35.5 |

Selected variants with P1 re-matched to their realised endoscopy sensitivity (Δ = rule − matched P1):

| Rule | Endo sens | Endo spec | Δ endo spec vs matched P1 [CI] | Δ NP flagged vs matched P1 [CI] | Δ caught vs matched P1 [CI] |
|---|---|---|---|---|---|
| R49 | 0.907 | 0.560 | +0.068 [-0.038, +0.165] | -5.0 [-8.7, -1.1] | -0.1 [-1.3, +0.8] |
| P1 90% | 0.898 | 0.524 | -0.012 [-0.055, +0.010] | +0.4 [-0.3, +1.9] | +0.0 [-0.3, +0.0] |
| R49 on max - c log(samples) eps 0.02 | 0.894 | 0.614 | +0.095 [-0.012, +0.189] | -5.3 [-8.9, -1.3] | -0.5 [-1.4, +0.3] |
| R49 veto auto eps 0.05 | 0.848 | 0.615 | -0.006 [-0.062, +0.085] | -2.5 [-5.7, +0.3] | +0.2 [-1.1, +1.7] |
| R49 filter image quality + tile eps 0.05 | 0.859 | 0.601 | -0.003 [-0.056, +0.079] | -2.8 [-5.8, -0.3] | -0.1 [-0.9, +0.7] |
| R49 veto auto eps 0.02 | 0.872 | 0.597 | +0.033 [-0.044, +0.119] | -3.6 [-7.0, -0.7] | -0.1 [-1.1, +1.0] |
| R49 veto conc_top16_of_pos eps 0.05 | 0.866 | 0.601 | +0.023 [-0.042, +0.102] | -2.8 [-6.0, -0.3] | +0.1 [-0.8, +1.0] |
| R49 veto core_mean eps 0.05 | 0.855 | 0.618 | +0.023 [-0.074, +0.135] | -2.4 [-6.4, +1.2] | +0.3 [-0.8, +1.7] |
| R49 veto median eps 0.05 | 0.872 | 0.617 | +0.047 [-0.027, +0.123] | -3.2 [-6.5, -0.4] | +0.1 [-0.9, +1.0] |
| R49 veto gini_pos eps 0.05 | 0.851 | 0.596 | +0.001 [-0.095, +0.106] | -2.1 [-6.1, +1.1] | +0.0 [-1.2, +1.2] |
| R49 filter tile contributions eps 0.05 | 0.866 | 0.602 | +0.016 [-0.043, +0.099] | -2.7 [-6.0, -0.2] | +0.2 [-0.8, +1.5] |
| R49 on max - c log(samples) eps 0.0 | 0.900 | 0.596 | +0.089 [-0.012, +0.183] | -5.0 [-8.7, -1.3] | -0.4 [-1.4, +0.3] |
| R49 filter sequencing batch progressor share, training labels only (not deployable) eps 0.05 | 0.883 | 0.637 | +0.108 [+0.010, +0.195] | -6.6 [-10.3, -3.0] | -0.1 [-0.9, +1.1] |
| P1 90% filter sequencing batch progressor share, training labels only (not deployable) eps 0.05 | 0.880 | 0.628 | +0.065 [-0.002, +0.114] | -3.9 [-6.2, -1.3] | +0.2 [-0.2, +0.4] |
| R49 veto auto eps 0.0 | 0.882 | 0.580 | +0.027 [-0.054, +0.129] | -3.8 [-7.4, -0.5] | +0.1 [-1.0, +1.3] |
| P1 90% veto auto eps 0.0 | 0.866 | 0.545 | -0.049 [-0.079, -0.011] | +1.9 [+0.5, +3.5] | +0.3 [-0.4, +0.7] |
| P1 90% on max - c log(samples) | 0.876 | 0.587 | +0.015 [-0.067, +0.102] | -2.3 [-5.7, +1.4] | -0.2 [-0.5, +0.2] |
| P1 90% on max - c1 log(samples) - c2 log(1 + position) (design-sensitive) | 0.863 | 0.623 | +0.042 [-0.019, +0.097] | -1.0 [-4.0, +2.4] | +0.3 [-0.2, +0.8] |

**Score substitutions** (sample H&E score replaced by a robust aggregate of tile scores; thresholds from the new inner out-of-fold scores):

| Aggregate | Sample AUROC new / original | Δ AUROC [CI] | P1 90%: caught / NP flagged | R49: caught / NP flagged / seq |
|---|---|---|---|---|
| nonbg_mean | 0.846 / 0.847 | -0.000 [-0.005, +0.005] | 31.2 / 36.4 | 31.1 / 31.9 / 1.93 |
| core_mean | 0.804 / 0.847 | -0.043 [-0.071, -0.015] | 31.4 / 39.1 | 31.1 / 31.7 / 2.12 |
| trim10 | 0.846 / 0.847 | -0.001 [-0.005, +0.003] | 31.4 / 36.8 | 31.1 / 31.7 / 1.96 |
| median | 0.837 / 0.847 | -0.010 [-0.019, -0.001] | 31.7 / 37.4 | 31.1 / 32.1 / 1.99 |
| noink_mean | 0.847 / 0.847 | -0.000 [-0.000, +0.000] | 31.1 / 36.0 | 31.1 / 31.8 / 1.94 |
| rest_mean | 0.844 / 0.847 | -0.003 [-0.006, -0.000] | 30.7 / 35.1 | 31.1 / 32.2 / 2.00 |

**Sample-count penalty** (endoscopy score = max logit L-IMG − c·log(samples); c from the training patients of each fold):

- P1 90% on max - c1 log(samples) - c2 log(1 + position) (design-sensitive): c median [1.5, 1.0]; caught 31.1, NP flagged 33.4, endoscopy sens / spec 0.863 / 0.623, samples sequenced / patient 0.00
- P1 90% on max - c log(samples): c median 1.75; caught 30.8, NP flagged 32.6, endoscopy sens / spec 0.876 / 0.587, samples sequenced / patient 0.00
- R49 on max - c log(samples) eps 0.0: c median 1.125; caught 30.8, NP flagged 31.3, endoscopy sens / spec 0.900 / 0.596, samples sequenced / patient 1.83
- R49 on max - c log(samples) eps 0.02: c median 1.75; caught 30.7, NP flagged 30.8, endoscopy sens / spec 0.894 / 0.614, samples sequenced / patient 1.75
- Endoscopy-level fold-stratified AUROC, max - c log(samples): 0.85 vs max 0.837, Δ +0.013 [-0.011, +0.036]
- Endoscopy-level fold-stratified AUROC, max - c1 log(samples) - c2 log(1 + position): 0.855 vs max 0.837, Δ +0.018 [-0.007, +0.046]

Automatic veto (feature and direction chosen per fold on training patients) — features chosen (fold count over 100 splits):

- R49 eps 0.0: p90 12, top16_mean 12, max 10, edge_contrib 8, bg_contrib 6, mean 6, core_mean 6, log_tissue_tiles 5, median 5, nonbg_mean 5, frac_u_gt2 5, conc_top16_of_pos 4, gini_pos 4, share_pos 3, rest_mean 3, trim10 2, dark_share 1, bg_share 1, blur_contrib 1, sd 1
- R49 eps 0.02: p90 11, max 11, top16_mean 11, rest_mean 8, core_mean 8, mean 7, frac_u_gt2 7, nonbg_mean 7, median 5, edge_contrib 4, trim10 4, sd 4, bg_contrib 3, gini_pos 3, log_tissue_tiles 2, share_pos 1, bg_share 1, edge_share 1, conc_top16_of_pos 1, blur_contrib 1
- R49 eps 0.05: p90 18, max 9, nonbg_mean 9, top16_mean 9, frac_u_gt2 8, rest_mean 7, mean 7, edge_contrib 6, core_mean 6, conc_top16_of_pos 4, gini_pos 4, trim10 4, share_pos 2, blur_contrib 2, bg_share 2, log_tissue_tiles 1, median 1, sd 1
- P1 90% eps 0.0: top16_mean 17, bg_contrib 14, p90 12, max 8, conc_top16_of_pos 8, rest_mean 7, nonbg_mean 6, frac_u_gt2 6, edge_contrib 5, mean 3, share_pos 3, gini_pos 3, sd 2, trim10 2, median 1, bg_share 1, dark_share 1, core_mean 1
- P1 90% eps 0.02: top16_mean 17, p90 17, rest_mean 8, nonbg_mean 7, edge_contrib 7, mean 6, max 6, trim10 5, median 5, gini_pos 5, frac_u_gt2 4, share_pos 3, bg_contrib 3, core_mean 3, conc_top16_of_pos 3, bg_share 1
- P1 90% eps 0.05: p90 21, mean 10, rest_mean 10, frac_u_gt2 9, max 8, nonbg_mean 7, trim10 5, top16_mean 5, conc_top16_of_pos 4, edge_contrib 4, median 3, share_pos 3, gini_pos 3, core_mean 3, bg_contrib 2, sd 2, bg_share 1

**Second-stage filter**, held-out AUROC of the filter among flagged endoscopies (P vs NP, per-repeat mean):

| Rule | Feature set | AUROC | eps 0: caught / NP flagged | eps 0.05: caught / NP flagged |
|---|---|---|---|---|
| R49 | image quality | 0.716 | 31.0 / 31.8 | 30.4 / 30.9 |
| R49 | tile contributions | 0.679 | 31.1 / 31.8 | 31.1 / 31.2 |
| R49 | image quality + tile | 0.688 | 31.0 / 31.7 | 30.7 / 30.9 |
| R49 | image quality + tile + clinical | 0.700 | 31.1 / 31.7 | 30.4 / 31.2 |
| R49 | clinical | 0.723 | 31.0 / 31.8 | 30.4 / 30.9 |
| R49 | slide metadata: scanner, slide age, biopsy year (not deployable) | 0.685 | 31.1 / 31.8 | 30.9 / 31.7 |
| R49 | sequencing batch progressor share, training labels only (not deployable) | 0.818 | 31.1 / 31.2 | 31.1 / 28.9 |
| R49 | artefact incl. batch shares from all labels (LEAKS LABELS; demonstration only) | 0.883 | 31.1 / 21.6 | 31.1 / 19.6 |
| P1 90% | image quality | 0.738 | 31.0 / 35.9 | 30.8 / 35.2 |
| P1 90% | tile contributions | 0.704 | 31.1 / 35.9 | 30.8 / 35.1 |
| P1 90% | image quality + tile | 0.714 | 31.0 / 35.9 | 30.9 / 35.1 |
| P1 90% | image quality + tile + clinical | 0.732 | 31.1 / 35.8 | 30.9 / 35.1 |
| P1 90% | clinical | 0.752 | 31.1 / 35.7 | 30.7 / 34.4 |
| P1 90% | slide metadata: scanner, slide age, biopsy year (not deployable) | 0.717 | 31.1 / 36.0 | 30.9 / 35.9 |
| P1 90% | sequencing batch progressor share, training labels only (not deployable) | 0.835 | 31.1 / 33.9 | 31.1 / 31.1 |
| P1 90% | artefact incl. batch shares from all labels (LEAKS LABELS; demonstration only) | 0.889 | 31.1 / 24.0 | 31.0 / 21.1 |

### Implementation notes

- **Population and rules.** These are exactly round 8's: `rv8b_step3.py` and `rv8_landscape.py` are executed unchanged up to their dispatch. R49 = P6 t_low 95% / t_high 90%; P1 = max L-IMG at 90% training endoscopy sensitivity. The check reproduces round 8 (31.1 / 31.8 and 31.1 / 36.0).
- **Endoscopy classes and covariates.** FP-NP / TN-NP / TP-P / FN-P are counted per repeat. Means are weighted by the share of repeats in each class. Sample covariates come from the endoscopy's top-H&E sample (repeat-mean outer L-IMG). Database grade at endoscopy = highest confirmed grade in Barrett's database reports within 14 days of the sample's exact date (rv7_round7.py linkage). Later DB group = highest grade more than 14 days after the last sequenced endoscopy (R54 logic). Same-block labels come from round-7 lookup Q1. Slide notes come from `slide_matching` (`Slide Notes`). Batch composition uses the sheet `Batch`; the batch progressor share uses all labels, so it is descriptive only.
- **Tile scores.** u_t = w·(e_t − μ)/σ, with w, μ, σ from the exact refit of each outer or inner fit, so the sample logit = b0 + mean_t u_t. Tile flags come from per-tile pixel statistics at the stored positions (`ex_e1_px.py`; no pixels saved):
  - background: > 50% white pixels (R55);
  - edge: non-background with tissue-mask share < 0.8 in the 3 × 3-tile neighbourhood, or > 25% white;
  - blur: non-background below the 10th percentile of Laplacian variance;
  - ink: > 2% saturated green-blue pixels (almost none found).
- **Nesting.** Training-side quantities for each (repeat, outer fold) come from training patients only:
  - R49 / P1 flags of training endoscopies: from inner out-of-fold L-IMG / L-LATE and the fold's own cut-offs;
  - tile summaries of training samples: under the inner fits whose held-out fold contains them.
  - Vetoes choose the feature direction and threshold so that at most eps of training flagged progressor endoscopies are vetoed. The "auto" veto picks the feature per fold too.
  - Filters are L2 logistic regressions (C = 1) on standardised features plus the gate score, trained on training flagged endoscopies. Their threshold comes from patient-grouped 5-fold out-of-fold probabilities within training.
  - Score substitutions recompute P1 thresholds and the R49 cut-offs from the substituted inner scores.
  - The sample-count penalty picks c (grid 0–3) by training specificity at 90% training sensitivity (P1), or by the largest NP reduction with training R49 sensitivity within eps (R49).
- **Vetoed endoscopies keep their sequencing.** Δ for vetoes and filters therefore leaves samples sequenced unchanged.
- **Apparent (optimistic) values.** These set the threshold or fit the model on the evaluated endoscopies of each repeat.
- **Matched comparison.** P1 matched = P1's threshold re-matched in every repeat and draw to the rule's realised endoscopy sensitivity (rv8b S1 (i)).
- **Multiplicity.** 226 nested variants were scored. The selected rows in the matched table are the best of many and are optimistic as a group.
- **Privacy.** Only aggregates are committed. Row-level tile scores, pixel statistics, coefficients and calls stay on the cluster (`killcoyne_mm/explore_E1/`).
- **Figures.** Local only, in `paper/figures_explore_E1/`: e1_char_r49.png, e1_char_p1.png, e1_tiles_r49.png, e1_fixes.png.


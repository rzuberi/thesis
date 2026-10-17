# Review round 7: analyses chosen by the decision panel (excluding ACE-B)

Status: PRE-SPECIFICATION (written 2026-10-17). Nothing below has been run. Results are appended under the line at the end in a later commit; this section is not edited afterwards.

Purpose: answer the round-7 review of manuscript v7 and the decisions of a five-member panel (gastroenterologist, Nature Medicine editor, biostatistician, computational pathologist, cancer-genomics PI; brief and answers outside the repository). The primary analysis is unchanged. Every item below is a sensitivity, secondary or descriptive analysis and is reported whatever the result. No ACE-B file is read. Frozen bundles are not changed.

**Ground rules and conventions** as in `docs/paper_review_round6_analyses.md` (5c10c27):
- **Primary population:** 571 pre-event samples of the 676 samples from 80 patients of the Killcoyne discovery cohort with a matched H&E slide.
- **Copy number:** the shipped matrix.
- **Calls:** single model = per-repeat calls averaged over 10 repeats; 10-model vote = ≥ 6 of 10.
- **Bootstrap:** patient bootstrap, 2,000 draws, `RandomState(0)`; one-sided 95% bound = 5th percentile; two-sided limits also reported.
- **Triage comparisons** against B\* (training-matched) and (B).

**Refits.** Items marked [refit] rerun the existing pipeline: `kv_cv.R` outer loop, `hz_fit.R` inner loop, triage cut-offs from inner predictions (as `rv4_refit.R`).
- Existing patients keep their folds in every repeat.
- Added patients are assigned, in sorted patient order, to the fold with the fewest progressor patients (non-progressor patients for non-progressors), ties to the lowest fold index, separately in each repeat.
- Nothing else changes.

## Part A. Corrections of round-7 errors

### R42. Stability of the 10-model vote

The round-6 "62% unanimous" restated single-model agreement. Here:
- For every one of the 126 ways of splitting the 10 repeats into two sets of 5, compute the two 5-model votes (≥ 3 of 5) per pre-event sample.
- Report the share of samples on which the two votes agree (mean and 2.5–97.5% range over splits).
- Report the same for two single repeats (all 45 pairs).
- Report both overall and by modal band.

### R43. Control exclusions with training refitted [refit]

R38 (b) and (c) cannot change sensitivity when only evaluation samples are removed. Here the same non-progressor samples are removed from **training and evaluation**:
- (a) samples taken less than 1 year before the patient's last sequenced endoscopy;
- (b) less than 2 years;
- (c) the patient with a later HGD report.

Reported for each: triage against B\* and (B) (Δ sensitivity with bound, Δ specificity, share sequenced), and Δ L-IMG − L-CNV with bound. R38 (b)/(c) rows are relabelled "evaluation-only: sensitivity unchanged by construction; Δ specificity shown".

### R44. p53 among all triage-negative samples

Recompute R37 (e) over all samples the triage calls negative per repeat: low band, plus middle band called negative by L-LATE. Report counts of p53-aberrant progressor and non-progressor samples (mean over repeats), and the modal-low-band counts for comparison.

## Part B. Matched comparisons and burden

### R45. Current care with p53 at matched specificity

On the 450 pre-event samples with p53, set the threshold of L-LATE (sequence all) and of L-IMG so that per-repeat specificity on these samples equals that of grade ID/LGD or p53 aberrant (0.794; evaluation-matched).
- **Per sample:** Δ sensitivity against grade-or-p53, with patient-bootstrap CI.
- **Per patient:** the same at grade-or-p53's per-patient specificity.
- **Secondary:** the triage at its own operating point is also restated on these samples.

### R46. One random sample per endoscopy at matched endoscopy specificity

Using the R41 seeds:
- **(a) Matched specificity.** Lower or raise the random rule's L-LATE threshold so that its endoscopy-level specificity equals the triage's (per repeat, evaluation-matched). Report Δ endoscopy sensitivity (triage − random) with patient-bootstrap CI.
- **(b) Per patient.** Progressor patients missed and non-progressor patients flagged for the random rule, at its own threshold and at the matched one.
- **(c) Sequencing burden.** Share of samples sequenced and share of endoscopies with ≥ 1 sample sequenced, for the random rule, the triage, B\* and (B).

### R47. Burden, prevalence and cost (descriptive)

For triage, two-band rule (R48), B\*, (B), (C), (D) and grade-or-p53:
- **(a) Flag rate.** Flagged endoscopies per non-progressor patient-year.
- **(b) Projection per 1,000 surveillance samples** at progressor-sample prevalence 0.5%, 2% and 5%, using class-conditional rates from this cohort. Report:
  - samples sequenced;
  - flagged samples;
  - flagged endoscopies (using the cohort's samples-per-endoscopy distribution);
  - progressor samples missed;
  - cost.

  Cost = £85 per sequenced sample (Gregson 2017 thesis, 2017–18 prices) + £471 per flagged endoscopy, assuming one repeat endoscopy (NHS Payment Scheme 2024/25, FE21Z). Costs are illustrative; no threshold is set.
- **(c) Share sequenced reweighted** to each prevalence.

### R48. Two-band rule (secondary)

Clear the low band; sequence every other sample (middle and high) and call it by L-LATE. Nothing is flagged without sequencing. Same cut-offs as the triage.
- Report sensitivity, specificity and share sequenced.
- Report Δ against the triage and against B\* (with bound).
- Report endoscopy and patient columns as in Table 1, and the R47 burden.

### R49. Per-endoscopy gate (secondary, exploratory)

1. **Endoscopy score:** the maximum L-IMG over the endoscopy's pre-event samples. Same per-fold t_low and t_high.
2. **Endoscopy bands:**
   - low: all its samples are cleared;
   - high: the endoscopy is flagged;
   - middle: the sample with the highest L-IMG is sequenced, and the endoscopy is called by its L-LATE.
3. **Variant:** in the middle band, sequence all samples and flag if any is L-LATE positive.

Report endoscopy-level sensitivity and specificity, share of samples and of endoscopies sequenced, and patient columns, against the sample-level triage aggregated to endoscopies, with paired bootstrap Δ.

### R50. NDBE-only block

Restrict to pre-event samples graded NDBE (438 samples, 71 patients). Table 1 rows for triage, B\*, (B), C\* and (D)+p53 where defined: share sequenced, sensitivity, specificity, endoscopy and patient columns.

### R51. Falsely cleared progressor endoscopies (descriptive)

Progressor endoscopies the triage calls negative (all samples negative), by time to event (< 1, 1–3, > 3 years). Report counts and grade. For progressor patients missed in ≥ 1 repeat: number of pre-event endoscopies, grade, tissue tertile, and time from first sample to event. Aggregates only.

## Part C. Labels and cohort

### R52. Samples of the 8 progressors previously reported without a slide [refit]

The linkage is built in `analysis/clinical_lookup/a2_candidate_map_8pt.csv` (cluster), with no change to the analysis inputs.
- **(a)** Add the 17 samples linked on the same case and block. This gives 693 samples; pre-event 577 samples / 77 patients / 34 progressors.
- **(b)** Additionally add the 7 samples from the same case with the block unrecorded. This gives 700 samples; pre-event 582 / 79 / 36.

For each, refit and report:
- the triage against B\* and (B);
- Δ L-IMG − L-CNV;
- AUROCs of the three models;
- Table 1 patient columns.

### R53. Event dates from the Barrett's database

Define each progressor's event date as the earlier of the sample-sheet event endoscopy and the first HGD+ report in the Barrett's database. Exclude pre-event samples taken on or after it. Re-score stored predictions (no refit) and report the number removed, the triage against B\* and (B), and Δ L-IMG − L-CNV.

### R54. Later disease in non-progressors [refit]

Relabel the non-progressor with a later HGD report as a progressor, and exclude non-progressor patients with a later LGD report (Barrett's database, after the last sequenced endoscopy). Refit; report as R52.

## Part D. Image confounds

### R55. Image quality and within-class confound audit

**(a) Background tiles.** Per slide, count the share of the stored 256 tile positions that are background, recomputed from the slide at the stored coordinates. Background = more than 50% of pixels with all RGB channels > 220.
- Report by class and tissue tertile.
- Report triage against B\* and Δ L-IMG − L-CNV after excluding slides with background share > 25% (re-scoring, no refit).

**(b) Slide age.** Slide age at scan = scan date (slide header) − exact endoscopy date.
- Within each class, Spearman of L-IMG with slide age, tissue tiles and biopsy year.
- AUROC of slide age alone.

**(c) Metadata alone.** Out-of-fold AUROC of a logistic model with slide age, tissue tiles, scanner and batch-composition group (single-class / mixed) under the same folds.

**(d) Incremental value.** Δ AUROC of L-IMG + metadata over metadata alone.

### R56. Killcoyne validation cohort: audit only

No outcome-based score of the slide model is computed in this item.
- **(a) Identity.** Whether the samples or patients of `sWGS_validation_cleaned_Leanne` are the "release validation batch" previously rejected as an external test (project history), and whether any patient overlaps the 80.
- **(b) Linkage.** Patients, samples and progressors with ≥ 1 scanned slide; batches; scanners; tissue tiles, by class.
- **(c) Metadata.** Out-of-fold AUROC of metadata alone (scanner, batch, tissue tiles, biopsy year) for status.

**Gate.** It must not be the rejected batch, have ≥ 10 progressor patients with slides, and metadata-alone AUROC lower 95% bound < 0.65 with point estimate < 0.65. If it passes, a later commit pre-registers a patient-level check of the frozen slide model, with success = lower 95% bound of AUROC > 0.65. The model is not scored in this round.

## Part E. ACE-B power (no ACE-B data read)

### R57. Achievable precision

Simulate ACE-B-like samples from the discovery cohort's single-model calls: about 15 progressor and 67 non-progressor patients, 2 pre-event samples per patient drawn without replacement (all if fewer), 10,000 draws.
- **(a) Precision.** CI half-width of per-sample sensitivity and specificity.
- **(b) Pass rule.** Probability that "≥ 12 of 15 progressor patients detected" passes, at the cohort's per-patient detection rate and at true per-patient detection rates of 0.70, 0.80 and 0.90.
- **(c) Slide model.** CI half-width of the slide model's per-patient AUROC.

## Part F. Deeper sequencing (registered now, run when the data arrive)

### R58. 4× copy number of the same cohort

The 0.4× shipped matrix stays primary. When the 4× data exist, compare L-CNV, Δ L-IMG − L-CNV and the triage against B\* under:
- 0.4× (shipped);
- 4× downsampled to 0.4× (package rebuild, joint segmentation);
- full 4× (same pipeline).

**Consequence.** If L-CNV at 4× exceeds L-IMG by more than 0.05 AUROC with a lower bound above 0, the manuscript drops "the slide model discriminates about as well as copy number". The result is reported whatever it is.

## Scripts and running

- **Scripts:** `scripts/paper_plan/rv7_round7.py` (re-scoring items) and `scripts/paper_plan/rv7_refit.R` (refits, copying `rv4_refit.R`).
- **Execution:** cluster campaigns via `scripts/cluster/campaign.sh`, prefix `rv7`.
- **Outputs:** aggregates to `results/paper_final/review_round7/`; row-level outputs stay on the cluster under `killcoyne_mm/review_round7/`.
- **Results:** appended below by a render script (`rv7_render.py`).

---

## Results

Rendered by `scripts/paper_plan/rv7_render.py` from `results/paper_final/review_round7/` (aggregate results f1c04d4). Single model = per-repeat values averaged over the 10 repeats; patient bootstrap 2,000 draws (`RandomState(0)`); bound = one-sided 95% lower bound (5th percentile).

| Item | Status |
|---|---|
| R42 stability of the 10-model vote | DONE |
| R43 control exclusions with training refitted | DONE (3 refits) |
| R44 p53 among all triage-negative samples | DONE |
| R45 current care with p53 at matched specificity | DONE |
| R46 one random sample per endoscopy at matched specificity | DONE |
| R47 burden, prevalence and cost | DONE |
| R48 two-band rule | DONE |
| R49 per-endoscopy gate | DONE |
| R50 NDBE-only block | DONE |
| R51 falsely cleared progressor endoscopies | DONE |
| R52 samples of the 8 progressors previously reported without a slide | DONE (2 refits) |
| R53 event dates from the Barrett's database | DONE |
| R54 later disease in non-progressors | DONE (1 refit) |
| R55 image quality and within-class confound audit | DONE |
| R56 Killcoyne validation cohort: audit only | DONE (gate not passed) |
| R57 achievable precision (simulated, no ACE-B data) | DONE |
| R58 4x copy number of the same cohort | NOT RUN: data not yet available |

### R42. Stability of the 10-model vote

Pre-event samples (571). Two 5-model votes (≥ 3 of 5) over all 126 splits of the 10 repeats into two sets of 5, and two single repeats over all 45 pairs: share of samples on which the two calls agree, mean (2.5–97.5% range over splits or pairs).

| Samples | n | Two 5-model votes agree | Two single repeats agree |
|---|---|---|---|
| all pre-event | 571 | 0.920 (0.905–0.935) | 0.856 (0.835–0.875) |
| modal band low | 178 | 0.968 (0.955–0.983) | 0.923 (0.867–0.971) |
| modal band middle | 269 | 0.852 (0.822–0.881) | 0.753 (0.717–0.809) |
| modal band high | 124 | 1.000 (1.000–1.000) | 0.982 (0.960–1.000) |
| progressor | 161 | 0.936 (0.914–0.956) | 0.893 (0.852–0.919) |
| non-progressor | 410 | 0.914 (0.893–0.934) | 0.841 (0.808–0.870) |

Two independent 5-model votes give the same call on 92% of samples, against 86% for two single repeats; the disagreement is in the middle band (85% for votes, 75% for single repeats). The round-6 '62% unanimous' was the share of samples on which all 10 single repeats agree with the vote, not the stability of the vote itself.

### R43. Control exclusions with training refitted

The same non-progressor samples as R38 (b) and (c) are removed from training and evaluation, and the whole pipeline (outer and inner fits, cut-offs, matched comparators) is refitted. Existing patients keep their folds.

| Analysis | Pre-event samples (progressor) / patients (progressor) | Triage sens / spec | Share sequenced | Δ sens vs B\* [95% CI] | Bound | Within −0.05 | Δ spec vs B\* | Δ sens vs (B) (bound) | Δ L-IMG − L-CNV (bound) | Within |
|---|---|---|---|---|---|---|---|---|---|---|
| primary (stored, R33 row 1) | 571 (161) / 75 (32) | 0.865 / 0.697 | 0.458 | -0.016 [-0.036, +0.001] | -0.032 | yes | +0.032 | +0.033 (+0.011) | +0.045 (-0.025) | yes |
| (a) non-progressor samples < 1 year before the last sequenced endoscopy removed, refitted | 478 (161) / 75 (32) | 0.842 / 0.685 | 0.484 | -0.014 [-0.036, +0.006] | -0.032 | yes | +0.025 | +0.025 (+0.002) | +0.041 (-0.038) | yes |
| (b) < 2 years removed, refitted | 456 (161) / 75 (32) | 0.859 / 0.703 | 0.484 | -0.015 [-0.040, +0.004] | -0.035 | yes | +0.019 | +0.035 (+0.009) | +0.029 (-0.038) | yes |
| (c) the non-progressor patient with a later HGD report removed, refitted | 564 (161) / 74 (32) | 0.875 / 0.704 | 0.461 | -0.006 [-0.023, +0.012] | -0.020 | yes | +0.032 | +0.039 (+0.018) | +0.050 (-0.017) | yes |

R38 rows relabelled (stored calls, evaluation-only):

| R38 row | Triage sensitivity | Δ spec vs B\* | Note |
|---|---|---|---|
| (b) non-progressor samples < 1 year before the last sequenced endoscopy removed | 0.865 | +0.035 | evaluation-only: sensitivity unchanged by construction; Δ specificity shown |
| (b) non-progressor samples < 2 years before the last sequenced endoscopy removed | 0.865 | +0.038 | evaluation-only: sensitivity unchanged by construction; Δ specificity shown |
| (c) non-progressor patients with a later HGD+ report removed | 0.865 | +0.032 | evaluation-only: sensitivity unchanged by construction; Δ specificity shown |

With training refitted, the triage stays within −0.05 of B\* in 3 of 3 exclusions and L-IMG within −0.05 of L-CNV in 3 of 3.

### R44. p53 among all triage-negative samples

Pre-event samples called negative by the triage in a repeat (low band, or middle band negative on L-LATE); counts are means over the 10 repeats (range over repeats).

| Set | Progressor: negative / with p53 / p53-aberrant | Non-progressor: negative / with p53 / p53-aberrant |
|---|---|---|
| all triage-negative (R44) | 21.8 / 14.3 / 1.1 (0–3) | 285.8 / 242.7 / 0.9 (0–1) |
| low band only (R37 e, per repeat) | 10.6 / 6.5 / 0.6 (0–2) | 166.1 / 143.6 / 0.7 (0–1) |
| modal low band (R37 e) | — / 3 / 0 | — / 147 / <5 |

Of 17 p53-aberrant progressor samples, a mean of 1.1 per repeat are triage-negative (all negatives), against 0.6 in the low band alone.

### R45. Current care with p53 at matched specificity

On the 450 pre-event samples with p53 (111 progressor; 71 patients). Grade ID/LGD or p53 aberrant: per sample sensitivity 0.432, specificity 0.794; per patient 0.613 / 0.450. Each model's threshold is set per repeat so that its specificity on these samples equals grade-or-p53's (evaluation-matched; re-matched in each draw).

| Level | Model at grade-or-p53's specificity | Sensitivity [95% CI] | Δ sensitivity vs grade-or-p53 [95% CI] | Bound |
|---|---|---|---|---|
| sample | L-LATE (sequence all) | 0.812 [0.696, 0.911] | +0.379 [+0.225, +0.529] | +0.250 |
| sample | L-IMG (H&E only) | 0.750 [0.596, 0.853] | +0.317 [+0.136, +0.465] | +0.166 |
| patient | L-LATE (sequence all) | 0.948 [0.844, 0.996] | +0.335 [+0.147, +0.503] | +0.179 |
| patient | L-IMG (H&E only) | 0.865 [0.726, 0.963] | +0.252 [+0.059, +0.442] | +0.097 |

Secondary, triage at its own operating point on these samples (share sequenced 0.452): per sample 0.871 / 0.716 (Δ sensitivity +0.439 [+0.308, +0.568], Δ specificity -0.078 [-0.163, +0.011]); per patient 0.961 / 0.282 (Δ sensitivity +0.348, Δ specificity -0.167 [-0.312, -0.022]).

### R46. One random sample per endoscopy at matched endoscopy specificity

288 pre-event endoscopies (88 progressor); R41 seeds (100). Mean over seeds (2.5–97.5% range over seeds) [bootstrap CI of the seed mean].

| Rule | Endoscopy sensitivity | Endoscopy specificity |
|---|---|---|
| triage | 0.909 [0.865, 0.952] | 0.549 [0.460, 0.637] |
| one random sample, L-LATE threshold matched to the triage's endoscopy specificity | 0.934 (0.915–0.952) [0.883, 0.971] | 0.550 (0.550–0.550) [0.463, 0.640] |
| one random sample, (B)'s fold threshold (R41) | 0.827 (0.803–0.852) [0.742, 0.901] | 0.740 (0.721–0.762) [0.673, 0.805] |

**(a)** Δ endoscopy sensitivity, triage − random at matched specificity: -0.025 (seeds -0.043 to -0.006) [-0.060, +0.013], bound -0.055.

**(b) Per patient** (of 32 progressor / 43 non-progressor patients; means over seeds and repeats): random rule at its own threshold misses 2.2 and flags 25.1; at the matched threshold misses 1.0 and flags 32.2; triage misses 0.9 and flags 32.0.

**(c) Sequencing burden.**

| Rule | Share of samples sequenced | Share of endoscopies with ≥ 1 sample sequenced |
|---|---|---|
| one random sample per endoscopy | 0.504 | 1.000 |
| triage | 0.458 | 0.597 |
| B\* | 1.000 | 1.000 |
| (B) | 1.000 | 1.000 |

### R47. Burden, prevalence and cost (descriptive)

**(a) Flag rate.** Flagged non-progressor endoscopies per non-progressor patient-year (43 patients, 286.0 patient-years between first and last pre-event endoscopy).

| Rule | Sensitivity | False-positive rate | Share sequenced (progressor / non-progressor) | Flagged non-progressor endoscopies (mean) | Per patient-year |
|---|---|---|---|---|---|
| triage | 0.865 | 0.303 | 0.360 / 0.497 | 90.2 | 0.315 |
| two-band rule (R48) | 0.865 | 0.303 | 0.934 / 0.595 | 90.2 | 0.315 |
| B\* | 0.881 | 0.335 | 1.000 / 1.000 | 94.1 | 0.329 |
| (B) | 0.832 | 0.238 | 1.000 / 1.000 | 72.0 | 0.252 |
| (C) H&E only | 0.795 | 0.281 | 0.000 / 0.000 | 89.9 | 0.314 |
| (D) grade ID or LGD | 0.354 | 0.185 | 0.000 / 0.000 | 48.0 | 0.168 |
| grade or p53 aberrant | 0.410 | 0.188 | 0.000 / 0.000 | 49.0 | 0.171 |

**(b), (c) Projection per 1,000 surveillance samples** (class-conditional rates from this cohort; mean 1.98 samples per endoscopy; £85 per sequenced sample, £471 per flagged endoscopy; illustrative, no threshold set).

| Prevalence | Rule | Samples sequenced (share, c) | Flagged samples | Flagged endoscopies | Progressor samples missed | Cost (£) |
|---|---|---|---|---|---|---|
| 0.5% | triage | 496 (0.496) | 306 | 237 | 0.7 | 153,876 |
| 0.5% | two-band rule (R48) | 597 (0.597) | 306 | 237 | 0.7 | 162,392 |
| 0.5% | B\* | 1000 (1.000) | 337 | 256 | 0.6 | 205,368 |
| 0.5% | (B) | 1000 (1.000) | 241 | 196 | 0.8 | 177,524 |
| 0.5% | (C) H&E only | 0 (0.000) | 283 | 224 | 1.0 | 105,261 |
| 0.5% | (D) grade ID or LGD | 0 (0.000) | 186 | 158 | 3.2 | 74,676 |
| 0.5% | grade or p53 aberrant | 0 (0.000) | 189 | 160 | 3.0 | 75,595 |
| 2.0% | triage | 494 (0.494) | 314 | 242 | 2.7 | 156,056 |
| 2.0% | two-band rule (R48) | 602 (0.602) | 314 | 242 | 2.7 | 165,179 |
| 2.0% | B\* | 1000 (1.000) | 346 | 260 | 2.4 | 207,550 |
| 2.0% | (B) | 1000 (1.000) | 250 | 202 | 3.4 | 180,278 |
| 2.0% | (C) H&E only | 0 (0.000) | 291 | 228 | 4.1 | 107,495 |
| 2.0% | (D) grade ID or LGD | 0 (0.000) | 189 | 160 | 12.9 | 75,536 |
| 2.0% | grade or p53 aberrant | 0 (0.000) | 192 | 163 | 11.8 | 76,722 |
| 5.0% | triage | 490 (0.490) | 331 | 252 | 6.8 | 160,326 |
| 5.0% | two-band rule (R48) | 612 (0.612) | 331 | 252 | 6.8 | 170,663 |
| 5.0% | B\* | 1000 (1.000) | 362 | 269 | 6.0 | 211,833 |
| 5.0% | (B) | 1000 (1.000) | 268 | 214 | 8.4 | 185,669 |
| 5.0% | (C) H&E only | 0 (0.000) | 306 | 238 | 10.2 | 111,883 |
| 5.0% | (D) grade ID or LGD | 0 (0.000) | 194 | 164 | 32.3 | 77,244 |
| 5.0% | grade or p53 aberrant | 0 (0.000) | 199 | 168 | 29.5 | 78,956 |

### R48. Two-band rule (secondary)

Low band cleared; middle and high bands sequenced and called by L-LATE at the triage's fold threshold. Sensitivity 0.865 [0.791, 0.926], specificity 0.697 [0.633, 0.762], share sequenced 0.691 [0.634, 0.751]. Share of high-band samples that L-LATE calls negative: 0.000.

| Two-band − | Δ sensitivity [95% CI] | Bound | Δ specificity [95% CI] |
|---|---|---|---|
| triage | +0.000 [+0.000, +0.000] | +0.000 | +0.000 [+0.000, +0.000] |
| B\* | -0.016 [-0.036, +0.001] | -0.032 | +0.032 [-0.002, +0.071] |
| (B) | +0.033 [+0.005, +0.062] | +0.011 | -0.065 [-0.092, -0.034] |

| Strategy | Sequenced | Sensitivity | Specificity | Endoscopy sens / spec | Patients missed / flagged |
|---|---|---|---|---|---|
| two-band rule | 69.1% | 0.865 [0.791, 0.926] | 0.697 [0.633, 0.762] | 0.909 / 0.549 | 0.9 / 32.0 |
| triage | 45.8% | 0.865 [0.791, 0.926] | 0.697 [0.633, 0.762] | 0.909 / 0.549 | 0.9 / 32.0 |
| B\* | 100.0% | 0.881 [0.801, 0.944] | 0.665 [0.585, 0.745] | 0.923 / 0.530 | 0.8 / 31.7 |
| (B) | 100.0% | 0.832 [0.740, 0.909] | 0.762 [0.694, 0.824] | 0.876 / 0.640 | 1.3 / 28.5 |

Burden (R47): two-band sequences 0.691 of samples against 0.458 for the triage, at the same flag rate (0.315 vs 0.315 per non-progressor patient-year).

### R49. Per-endoscopy gate (secondary, exploratory)

288 pre-event endoscopies (88 progressor). Endoscopy bands (per repeat mean): low 0.180, middle 0.505, high 0.315.

| Rule | Endoscopy sens [95% CI] | Endoscopy spec [95% CI] | Samples sequenced | Endoscopies sequenced | Patients missed / flagged | Δ endoscopy sens vs triage [95% CI] (bound) | Δ endoscopy spec [95% CI] |
|---|---|---|---|---|---|---|---|
| gate: top-L-IMG sample sequenced | 0.907 [0.861, 0.951] | 0.560 [0.475, 0.645] | 0.255 | 0.505 | 0.9 / 31.8 | -0.002 [-0.008, +0.000] (-0.006) | +0.011 [+0.005, +0.019] |
| variant: all middle-endoscopy samples sequenced | 0.914 [0.871, 0.955] | 0.542 [0.453, 0.633] | 0.501 | 0.505 | 0.9 / 32.4 | +0.005 [+0.000, +0.011] (+0.000) | -0.006 [-0.013, -0.001] |
| sample-level triage, aggregated | 0.909 [0.865, 0.952] | 0.549 [0.460, 0.637] | 0.458 | 0.597 | 0.9 / 32.0 |  |  |

### R50. NDBE-only block

Pre-event NDBE samples: 438 (104 progressor), 71 patients (28 progressor), 240 endoscopies (68 progressor). (D) flags nothing on NDBE samples, so (D)+p53 = p53 aberrant (missing as wild-type).

| Strategy | Sequenced | Sensitivity | Specificity | Endoscopy sens / spec | Patients missed / flagged |
|---|---|---|---|---|---|
| H&E-first triage | 49.1% | 0.846 [0.748, 0.928] | 0.680 [0.605, 0.750] | 0.921 / 0.533 | 0.9 / 31.6 |
| B\* | 100.0% | 0.861 [0.755, 0.944] | 0.653 [0.562, 0.739] | 0.932 / 0.516 | 0.8 / 30.5 |
| (B) | 100.0% | 0.823 [0.713, 0.918] | 0.720 [0.638, 0.797] | 0.900 / 0.591 | 0.8 / 28.5 |
| C\* | 0.0% | 0.790 [0.705, 0.874] | 0.693 [0.636, 0.748] | 0.888 / 0.528 | 0.9 / 34.1 |
| (D)+p53 | 0.0% | 0.087 [0.029, 0.164] | 0.997 [0.990, 1.000] | 0.103 / 0.994 | 21.0 / 1.0 |

Triage − B\* -0.014 [-0.038, +0.004] (bound -0.034); triage − (B) +0.023 (bound -0.003); L-IMG − L-CNV +0.047 (bound -0.030). On the 342 NDBE samples with a p53 result, (D)+p53 = 0.125 / 0.996.

### R51. Falsely cleared progressor endoscopies (descriptive)

88 progressor pre-event endoscopies. An endoscopy is falsely cleared in a repeat when every sample is triage-negative.

| Time to event | Progressor endoscopies | Falsely cleared, mean per repeat | In ≥ 1 repeat | In ≥ 6 of 10 | Grade of those cleared in ≥ 1 repeat (NDBE / ID / LGD) |
|---|---|---|---|---|---|
| <1 year | 7 | 0.0 | 0 | 0 | 0 / 0 / 0 |
| 1-3 years | 36 | 1.8 | 6 | <5 | 6 / 0 / 0 |
| >3 years | 45 | 6.2 | 15 | 5 | 12 / <5 / <5 |

Progressor patients missed in ≥ 1 repeat: <5 of 32. Pre-event endoscopies median 2 (range 1–3); highest grade NDBE <5, LGD <5; tissue tertile T1 <5, T2 <5; years from first pre-event sample to event median 5.0 (range 2.0–10.0); repeats missed median 2 (range 1–6).

### R52. Samples of the 8 progressors previously reported without a slide

(a) adds 17 samples (6 pre-event) from <5 patients: 693 samples; pre-event 577 / 77 / 34 progressors. (b) adds 24 (11 pre-event) from 6 patients: 700 samples; pre-event 582 / 79 / 36. Every pipeline step refitted; added patients assigned to folds by the pre-specified rule.

| Analysis | Pre-event samples (progressor) / patients (progressor) | Triage sens / spec | Share sequenced | Δ sens vs B\* [95% CI] | Bound | Within −0.05 | Δ spec vs B\* | Δ sens vs (B) (bound) | Δ L-IMG − L-CNV (bound) | Within |
|---|---|---|---|---|---|---|---|---|---|---|
| primary (stored, R33 row 1) | 571 (161) / 75 (32) | 0.865 / 0.697 | 0.458 | -0.016 [-0.036, +0.001] | -0.032 | yes | +0.032 | +0.033 (+0.011) | +0.045 (-0.025) | yes |
| (a) + same case and block | 577 (167) / 77 (34) | 0.874 / 0.716 | 0.481 | -0.011 [-0.022, +0.000] | -0.020 | yes | +0.015 | +0.054 (+0.031) | +0.061 (-0.004) | yes |
| (b) + block unrecorded | 582 (172) / 79 (36) | 0.890 / 0.719 | 0.464 | +0.008 [+0.001, +0.016] | +0.002 | yes | +0.023 | +0.071 (+0.048) | +0.081 (+0.013) | yes |

| Analysis | AUROC L-CNV [95% CI] | L-IMG | L-LATE | Patients missed / flagged: triage | B\* | (B) | C\* |
|---|---|---|---|---|---|---|---|
| (a) + same case and block | 0.801 [0.709, 0.873] | 0.862 [0.814, 0.908] | 0.895 [0.833, 0.941] | 0.9 / 31.2 | 0.9 / 30.8 | 1.2 / 26.5 | 1.1 / 35.3 |
| (b) + block unrecorded | 0.789 [0.701, 0.867] | 0.870 [0.824, 0.914] | 0.898 [0.839, 0.942] | 0.6 / 32.0 | 0.7 / 31.5 | 1.3 / 26.0 | 1.4 / 35.7 |

### R53. Event dates from the Barrett's database

Progressor event date = earlier of the sheet event endoscopy and the first database HGD+ report. Progressor patients: both dates, database earlier 8; both, sheet earlier or same day 21; sheet only <5; database only 6; not linked <5. Pre-event progressor samples dated on or after the sheet event date: 6; on or after the first database HGD+ report: 6 (more than 14 days after: <5; within 14 days: <5). Stored predictions re-scored.

| Analysis | Pre-event samples (progressor) / patients (progressor) | Triage sens / spec | Share sequenced | Δ sens vs B\* [95% CI] | Bound | Within −0.05 | Δ spec vs B\* | Δ sens vs (B) (bound) | Δ L-IMG − L-CNV (bound) | Within |
|---|---|---|---|---|---|---|---|---|---|---|
| primary (stored, R33 row 1) | 571 (161) / 75 (32) | 0.865 / 0.697 | 0.458 | -0.016 [-0.036, +0.001] | -0.032 | yes | +0.032 | +0.033 (+0.011) | +0.045 (-0.025) | yes |
| pre-event samples on or after the event date removed (10 samples, <5 patients) | 561 (151) / 74 (31) | 0.860 / 0.697 | 0.461 | -0.013 [-0.036, +0.005] | -0.032 | yes | +0.032 | +0.036 (+0.013) | +0.056 (-0.015) | yes |
| same, plus samples within 14 days before a database report (10 samples) | 561 (151) / 74 (31) | 0.860 / 0.697 | 0.461 | -0.013 [-0.036, +0.005] | -0.032 | yes | +0.032 | +0.036 (+0.013) | +0.056 (-0.015) | yes |

### R54. Later disease in non-progressors

Barrett's database, confirmed grade more than 14 days after the last sequenced endoscopy (43 of 43 non-progressor patients linked): <5 relabelled progressor (later HGD+; the same patient as the stored check: <5), <5 excluded (later LGD; 45 samples). Pre-event 526 samples / 72 patients / 33 progressors. Refitted.

| Analysis | Pre-event samples (progressor) / patients (progressor) | Triage sens / spec | Share sequenced | Δ sens vs B\* [95% CI] | Bound | Within −0.05 | Δ spec vs B\* | Δ sens vs (B) (bound) | Δ L-IMG − L-CNV (bound) | Within |
|---|---|---|---|---|---|---|---|---|---|---|
| primary (stored, R33 row 1) | 571 (161) / 75 (32) | 0.865 / 0.697 | 0.458 | -0.016 [-0.036, +0.001] | -0.032 | yes | +0.032 | +0.033 (+0.011) | +0.045 (-0.025) | yes |
| later HGD relabelled, later LGD excluded | 526 (168) / 72 (33) | 0.839 / 0.621 | 0.511 | -0.021 [-0.035, -0.007] | -0.033 | yes | +0.017 | +0.023 (+0.002) | +0.081 (+0.009) | yes |

| Analysis | AUROC L-CNV [95% CI] | L-IMG | L-LATE | Patients missed / flagged: triage | B\* | (B) | C\* |
|---|---|---|---|---|---|---|---|
| later HGD relabelled, later LGD excluded | 0.731 [0.630, 0.824] | 0.812 [0.748, 0.866] | 0.838 [0.756, 0.903] | 1.0 / 32.7 | 1.1 / 32.6 | 1.7 / 30.1 | 0.7 / 34.2 |

### R55. Image quality and within-class confound audit

**(a) Background tiles.** 683 slides; slides with background share > 0.25: 36 (5.3%). Background share per pre-event sample, median (IQR):

| Stratum | Progressor | Non-progressor |
|---|---|---|
| all pre-event | 0.000 (0.000–0.066); > 0.25: 8 (n 161) | 0.000 (0.000–0.018); > 0.25: 27 (n 410) |
| tissue tertile 1 | 0.000 (0.000–0.000); > 0.25: <5 (n 49) | 0.000 (0.000–0.113); > 0.25: 12 (n 143) |
| tissue tertile 2 | 0.018 (0.000–0.169); > 0.25: <5 (n 40) | 0.000 (0.000–0.150); > 0.25: 9 (n 152) |
| tissue tertile 3 | 0.000 (0.000–0.025); > 0.25: <5 (n 72) | 0.000 (0.000–0.002); > 0.25: 6 (n 115) |

Excluding samples with background share > 0.25 (35 removed, 8 progressor), stored calls:

| Analysis | Pre-event samples (progressor) / patients (progressor) | Triage sens / spec | Share sequenced | Δ sens vs B\* [95% CI] | Bound | Within −0.05 | Δ spec vs B\* | Δ sens vs (B) (bound) | Δ L-IMG − L-CNV (bound) | Within |
|---|---|---|---|---|---|---|---|---|---|---|
| primary (stored, R33 row 1) | 571 (161) / 75 (32) | 0.865 / 0.697 | 0.458 | -0.016 [-0.036, +0.001] | -0.032 | yes | +0.032 | +0.033 (+0.011) | +0.045 (-0.025) | yes |
| background share ≤ 0.25 | 536 (153) / 75 (32) | 0.859 / 0.703 | 0.462 | -0.018 [-0.041, +0.001] | -0.036 | yes | +0.030 | +0.032 (+0.007) | +0.042 (-0.026) | yes |

**(b) Slide age at scan** (years): progressor median 9.2 (IQR 6.4–13.3), non-progressor 10.2 (7.7–12.8). AUROC of slide age alone (younger = higher): 0.568 [0.452, 0.689].

| Within class | Spearman L-IMG vs slide age | vs tissue tiles | vs biopsy year |
|---|---|---|---|
| progressor (n 161) | -0.172 | -0.308 | +0.171 |
| non-progressor (n 410) | +0.164 | +0.148 | -0.150 |

**(c) Metadata alone** (slide age, log tissue tiles, scanner, batch composition; 6 single-class and 6 mixed batches): out-of-fold AUROC 0.594 [0.462, 0.717].

**(d) Incremental value.** L-IMG + metadata 0.833 [0.774, 0.884] (L-IMG alone 0.847); Δ (L-IMG + metadata) − metadata +0.239 [+0.125, +0.362] (bound +0.143); Δ (L-IMG + metadata) − L-IMG -0.014 [-0.052, +0.017].

### R56. Killcoyne validation cohort: audit only

No outcome-based score of the slide model was computed.

**(a) Identity.** The sheet holds 268 samples from 103 patients. 199 of its samples (68 patients, 66% of its patients) are release rows; the release holds 203 rows from the validation copy-number folders (68 patients). It is therefore the same source as the release validation batch rejected as an external test. Patients overlapping the 80: 5.

**(b) Linkage.** 179 samples with ≥ 1 same-case, same-block embedded slide (180 slides): progressor 35 samples / 9 patients, non-progressor 143 / 59. Sequencing runs 30 (progressor 9, non-progressor 22; 1 with both classes). Scanner: progressor C13239-01 35; non-progressor C13239-01 142, C13210 <5. Tissue tiles median (IQR): progressor 198 (120–286), non-progressor 1441 (1114–1854).

**(c) Metadata alone** (scanner, sequencing run, tissue tiles, biopsy year) for status: out-of-fold AUROC 0.984 [0.937, 1.000], one-sided lower bound 0.948 (178 samples, 68 patients, 9 progressor).

| Gate condition | Met |
|---|---|
| not the rejected batch | no |
| ≥ 10 progressor patients with slides | no |
| metadata AUROC point estimate < 0.65 | no |
| metadata AUROC lower 95% bound < 0.65 | no |

Gate not passed: no check of the slide model on this cohort is pre-registered.

### R57. Achievable precision (simulated from the discovery cohort; no ACE-B data read)

10,000 draws of 15 progressor and 67 non-progressor patients, 2 pre-event samples each.

| Quantity | Mean | CI half-width | 2.5–97.5% over draws |
|---|---|---|---|
| per-sample sensitivity (triage) | 0.864 | 0.155 | 0.690–1.000 |
| per-sample specificity (triage) | 0.701 | 0.101 | 0.597–0.799 |
| per-patient AUROC (slide model, maximum over the 2 samples) | 0.870 | 0.101 | 0.755–0.958 |

**(b) Pass rule '≥ 12 of 15 progressor patients detected'.** Simulated probability 0.982 (per-patient detection rate with 2 samples 0.946; cohort rate with all samples 0.972). Binomial probability at a true per-patient detection rate of 0.70: 0.297; 0.80: 0.648; 0.90: 0.944.

### R58. 4× copy number of the same cohort

Not run: data not yet available. No 4× data for this cohort exist on the cluster (docs/paper_horizon_answers.md); the analysis stays registered as written above.

### Checks

- Refit pipeline with no change (`rv7_refit.R`, VAR=base, repeat 1) reproduces the stored predictions: outer L-CNV 676 rows, max |Δ prediction| 0.0e+00; outer L-IMG 676 rows, 0.0e+00; inner L-CNV 10 splits, 6084 rows, 0.0e+00; inner L-IMG 6084 rows, 0.0e+00; folds and λ identical: yes.
- Stored predictions through the round-7 scoring path reproduce R33 row 1: triage − B\* -0.016 (bound -0.032), triage − (B) +0.033, L-IMG − L-CNV +0.045 (expected −0.016 / −0.032, +0.033, +0.045).
- Added samples: (a) 17 → 693 samples, pre-event 577 / 77 / 34 (pre-specified 693; 577 / 77 / 34); (b) 24 → 700, 582 / 79 / 36 (pre-specified 700; 582 / 79 / 36). Their slide-mean image rows use the existing UNI2-h tiles; the km_prep.py construction reproduces stored rows to 4.8e-08; their copy-number rows come from the shipped matrix (stored block reproduced to 4.4e-16).
- R38 evaluation-only rows: triage sensitivity primary (R33 row 1, for reference): 0.865; (a) 'excluded' flag removed: 0.852; (a) 'excluded', 'remove' and 'inconsistency' flags removed: 0.843; (b) non-progressor samples < 1 year before the last sequenced endoscopy removed: 0.865; (b) non-progressor samples < 2 years before the last sequenced endoscopy removed: 0.865; (c) non-progressor patients with a later HGD+ report removed: 0.865; (d) (a) + (b, 1 year) + (c): 0.852 (the (b) and (c) rows equal the primary 0.865, as expected when only non-progressor samples are removed).
- R43 removals equal R38's: (a) 478, (b) 456, (c) 564 pre-event samples (R38: 478, 456, 564).
- R45 and R44 restate R37: grade-or-p53 0.432 / 0.794, triage − grade-or-p53 +0.439 (R37: 0.432 / 0.794, +0.439); low-band p53-aberrant per repeat 0.6 / 0.7 (R37 e: 0.6 / 0.7). R46 own-threshold rule 0.827 / 0.740 (R41: 0.827 / 0.740). R48 triage 0.865 / 0.697.
- R55 tissue tiles recomputed from the masks equal the stored `slide_desc.csv` values on the first pixel chunk (18 of 18 samples) and the stored tile coordinates are level coordinates (tile centres fall in the tissue mask).

### Implementation notes

- General: stored predictions and cut-offs are scored with the rv6_round6.py helpers (copied unchanged into rv7_round7.py). 'Single model' everywhere; endoscopy = (patient, endoscopy number), positive if any sample is flagged; patient positive if any sample is flagged. Patient bootstraps that need endoscopy or patient units tag resampled copies as distinct units (R23).
- Refits (R43, R52, R54): `rv7_refit.R` runs the kv_cv.R outer loop and the hz_fit.R inner loop verbatim on a variant set; only the set changes. Existing patients keep their set-C fold in every repeat, for the outer folds and also for the inner 5-fold splits (the inner split of the stored set C, 1000 × REP + FOLD); added patients get a fold by the pre-specified rule (fewest patients of their class, sorted order, ties to the lowest index), applied separately to the outer folds and to each inner split. The λ-selection shuffles (shuffle_groups, unchanged code) are drawn on the variant's patients, so they differ from the stored ones when patients are added or removed. A few refit files (base repeat 1, and one unit each of r52b and r54) were produced by the smoke test with the committed code and kept.
- R42: 126 = the 252 ordered 5/5 splits counted once (repeat 1 always in the first half); 5-model vote = ≥ 3 of 5; modal band as R39.
- R43: the R38 definitions are reused exactly (months before final < 12 / < 24 for non-progressor samples; the later-HGD patient of the stored hospital-record check, K1 logic), so (a)/(b) remove samples but no patient and (c) removes one patient.
- R44: triage-negative = band low, or band middle with L-LATE below the fold t_seq, per repeat; reported as per-repeat means with the range over repeats.
- R45: evaluation-matched threshold per repeat, pooled over folds, on the 450 samples (as the evaluation-matched B\* of R33): positive if score > the ⌈s·n⌉-th smallest non-progressor score; re-matched in each bootstrap draw to grade-or-p53's specificity in that draw. Per patient: patient score = maximum over its samples with p53; grade-or-p53 per patient = any sample flagged.
- R46: the R41 seed loop (RandomState(seed), seeds 0–99, endoscopies in sorted order) is reproduced to pick the same samples; the matched threshold is one L-LATE threshold per seed × repeat pooled across folds, set to the triage's endoscopy specificity in that repeat (and re-set in each draw). 'Triage share of endoscopies sequenced' = endoscopies with ≥ 1 middle-band sample, per repeat.
- R47: non-progressor patient-years = sum over non-progressor patients of the span between their first and last pre-event endoscopy (months before final / 12); a patient with one endoscopy contributes 0. Projections use per-sample class-conditional rates (sensitivity, false-positive rate, share sequenced by class); flagged endoscopies assume samples within an endoscopy flag independently, with the cohort's samples-per-endoscopy distribution. Grade-or-p53 treats missing p53 as wild-type on all 571 samples (R37 f). (C), (D) and grade-or-p53 sequence nothing. No uncertainty is attached (descriptive).
- R48: high-band samples are sequenced and called at the triage's middle-band threshold t_seq of their fold.
- R49: the endoscopy's fold is the patient's (all samples share it); its score is compared with that fold's t_low and c\* (high band = score > c\*, as the sample-level rule); when t_low > c\* there is no middle band. Share of samples sequenced = sequenced samples / pre-event samples, per repeat.
- R50: cut-offs and matched comparators chosen on NDBE pre-event training samples, as R33 row 2 and the R39 'ndbe' row; Table 1 columns from those calls.
- R51: endoscopy time to event = its samples' time; < 1 year, 1–3 years (inclusive), > 3 years. 'Missed patient' = no pre-event sample flagged in that repeat. Tissue tertile = tertile of the patient's median tissue tiles against pre-event sample tertile edges.
- R52: tiers T1 and T2b of `a2_candidate_map_8pt.csv`; all their samples (pre- and post-event) are added, as for every other patient in set C. Pre-event, time and NDBE flags follow hz_prep.py (event = the patient's first HGD/IMC sample in kr_samples.csv or the sheet's per-endoscopy class). Slide-mean image rows = mean over the union of the sample's stored UNI2-h tiles (km_prep.py); for T2b samples with several candidate slides of the case, all of them.
- R53: Barrett's database linkage and grade coding copied from clinical_lookup/r2_main.py; sheet event date = earliest exact date of the patient's event samples; sample dates = pre_event_cohort.Date (all 571 dated). 'On or after' is taken literally (sample date ≥ event date); a second row also removes samples dated up to 14 days before the event (the lookup's same-endoscopy convention). The database report date is the specimen-received date. Calls, cut-offs and comparators are the stored ones (no refit).
- R54: later = confirmed grade in a pathology report (or an HGD-register entry) more than 14 days after the patient's last sequenced endoscopy (latest exact date among all of the patient's sheet samples, slide-table date as fallback), as the lookup's B2. HGD+ → relabelled progressor (all its samples, all pre-event); highest later grade LGD → patient excluded.
- R55 (a): the 256 stored tile positions are read at the stored level and tile size; a sample's share is pooled over its slides; samples (not single slides) above 0.25 are excluded, because re-scoring cannot drop one slide of a sample. (b): scan date = hamamatsu.Created (earliest over the sample's slides); L-IMG = mean of the 10 outer predictions; slide-age AUROC uses the stored folds (fold-stratified, fixed score, sign chosen so younger slides score higher). (c)/(d): unpenalised logistic regression on training-standardised features; batch composition = whether the sample's sheet batch contains one class only among the 676; training rows = the stored inner rows of each outer split, where L-IMG enters as its inner out-of-fold prediction (and as its outer prediction on the held-out fold), so no fold sees its own test data.
- R56: 'the rejected batch' = the release's 268-sheet stratum (`docs/dataset_description.md`: release rows whose CNV sample is in the validation sheet); the sheet counts as that batch if any of its patients has a release row. Slide link = case + block (lookup functions ckey / vblock) with an embedded slide in uni2_npz_map.csv. The sheet has no Batch column, so 'batch' = sequencing run (SLXID1). Metadata model: L2 logistic (C = 1, because the one-hot run levels are many for the sample size), patient-grouped folds stratified by patient status; status = the sample's sheet Status (P / NP only). The gate's 'lower 95% bound' is the one-sided 5th percentile, as elsewhere.
- R57: patients drawn with replacement (67 > 43 non-progressor patients available); one random repeat per draw; CI half-width = half the 2.5–97.5% range of the estimate over draws (the spread an ACE-B-sized study would see), not a within-study interval. The pass-rule probability at a given true detection rate is binomial (15 patients).
- R58: not run; no 4× data exist.

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

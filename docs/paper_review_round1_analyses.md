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

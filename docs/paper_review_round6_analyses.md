# Review round 6: analyses requested by reviewers (excluding ACE-B)

Status: PRE-SPECIFICATION (written 2026-10-16). Nothing below has been run. Results are appended under the line at the end in a later commit; this section is not edited afterwards.

Purpose: answer the round-6 review of manuscript v6 (Nature Medicine referee and four full-context reviewers; synthesis outside the repository). All items re-score stored predictions or read stored sample-sheet and hospital-record fields. No model is refitted, no feature changes, no frozen bundle changes, and no ACE-B file is read.

**Ground rules** as in `docs/paper_review_round4_analyses.md` (45b77bf).

**Population and conventions.** Unchanged:
- Primary population: 571 pre-event samples of the 676 samples from 80 patients of the Killcoyne discovery cohort with a matched H&E slide.
- The shipped matrix is the primary copy-number source. Per-sample re-segmented features (R36) are reported where stated.
- Single model = per-repeat calls averaged over 10 repeats. The 10-model vote is ≥ 6 of 10.
- Patient bootstrap: 2,000 draws, `RandomState(0)`, resampled patients keep their folds.
- One-sided 95% bound = 5th percentile. Two-sided 95% limits are also reported.
- Triage comparisons give Δ sensitivity (with bound), Δ specificity and share sequenced against (B) and B\* (training-matched).

## R37. p53 immunohistochemistry as a current-standard comparator

Source: the `P53 IHC` field of the analysed-sample table (0 = wild-type pattern, 1 = aberrant, blank = not done).

- **(a) Availability.** p53 available, by class, among the 571 pre-event samples. Grade distribution of samples with and without p53. Fisher test of availability against status.
- **(b) p53 alone.** On pre-event samples with p53, sensitivity and specificity of "flag if p53 aberrant", per sample, per endoscopy and per patient, with exact CIs.
- **(c) Current care with p53.** "Flag if grade ID or LGD, or p53 aberrant" (D+p53), on the same samples and levels.
- **(d) Triage with p53.**
  - "Flag if triage positive or p53 aberrant" (single model, and voted).
  - Restricted to samples with p53, the triage alone against (D), (D+p53) and p53 alone, paired, with patient-bootstrap CIs on Δ sensitivity and Δ specificity.
- **(e) Does p53 add to the triage?** Among samples the triage clears (low band), how many progressor samples are p53-aberrant, and how many non-progressor samples.
- **(f) Sensitivity analysis.** Treat missing p53 as wild-type and report (b)–(d) on all 571.

## R38. Label sensitivity analyses

All re-score stored predictions on subsets, with fold-stratified AUROC and the patient bootstrap on the subset.

- **(a) Sheet exclusion flag.** Exclude samples carrying Killcoyne's `excluded` flag. Also report it with `remove` and `inconsistency` flags excluded.
- **(b) Short follow-up.** Exclude non-progressor samples taken less than 1 year before the patient's last sequenced endoscopy; separately, less than 2 years.
- **(c) Possible later HGD.** Exclude non-progressor patients with any later HGD+ report in the stored hospital-record check (`results/paper_final/final_checks.json` K1 and the row-level source it was built from, on the cluster). Report how many of the 43 are affected; if they cannot be identified, report "not identifiable".
- **(d)** (a), (b at 1 year) and (c) together.
- **Reported for each:**
  - the triage against B\* and against (B) (single model);
  - the triage's sensitivity, specificity and share sequenced;
  - Δ L-IMG − L-CNV (shipped matrix) with its bound;
  - the number of samples and patients by class.

## R39. The 10-model ensemble as the frozen rule

The 10-model vote is a candidate stabilised rule.
- Repeat the R33 Claim T table (triage against B\*, same rows where computable from stored voted calls) using voted calls for both triage and comparator.
- Add the vote-pivotal share sequenced per row.
- Report the between-repeat stability of a voted call:
  - the share of samples whose voted call is unanimous (10/10) or near-unanimous (≥ 8/10);
  - the same by modal band.

Comparing this table with R33 shows whether the ensemble is more robust than the single model.

## R40. Paired comparison of copy-number versions

Paired patient-bootstrap ΔAUROC (fold-stratified, same draws) between L-CNV versions on pre-event samples:
- the shipped matrix;
- the joint package rebuild;
- past-only;
- per-sample.

Report all six pairwise Δ with two-sided CIs and p-values, Holm-adjusted over the six.

**Sampling intensity.** The median per-sample correlation between joint and per-sample final features, by number of the patient's samples segmented together (tertiles), and by class within tertile. This tests whether the class difference in Fig. 5c follows the number of samples per patient.

## R41. One random biopsy per endoscopy

A cheap comparator at a similar sequencing share.
- **Rule.** At each pre-event endoscopy, sequence one sample chosen at random (100 seeds) and call the endoscopy by that sample's L-LATE result at (B)'s fold threshold.
- **Reported:**
  - endoscopy- and patient-level sensitivity and specificity, mean and 2.5–97.5% range over seeds;
  - the share of samples sequenced.
- **Comparison.** Against the triage at endoscopy and patient level (single model). Paired over seeds and patient bootstrap: Δ endoscopy sensitivity and specificity.
- **Variant.** One random biopsy sequenced, and the rest called by the H&E model.

## Scripts and running

- Scripts: `scripts/paper_plan/rv6_round6.py` (TASK = r37 … r41) and `rv6_render.py`.
- Running: Slurm via `scripts/cluster/campaign.sh`, prefix rv6. Never on the login node.
- Outputs: aggregates to `results/paper_final/review_round6/`.

---

## Results

(appended after running)

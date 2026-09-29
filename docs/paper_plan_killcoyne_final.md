# Killcoyne protocol with imaging: fold-stratified AUROC, selection-adjusted p, ACE-B power

Status: PRE-SPECIFICATION. Nothing below has been run. Results are appended in a later commit; this section is not edited afterwards.

Inputs: the stratified 10-fold × 10 CV predictions of `docs/paper_plan_killcoyne_cv.md` (pre-spec 76879b8, results d69de24), no refit. Set C, labels, subsets (all of set C; NDBE only; before the first HGD/IMC; both), CNV sources (their shipped matrix; package features), patient-bootstrap CI (2,000, `RandomState(0)`) and paired within-patient swap permutation (2,000, seed 0, two-sided) as before. The outer folds depend only on the repeat seed and the patient labels, so every arm shares them (checked in the script).

## 1. Fold-stratified AUROC

For repeat r: AUROC_r = Σ_folds (P–NP sample pairs within the fold ranked correctly + ½ ties) / Σ_folds (P–NP sample pairs within the fold), using that repeat's out-of-fold predictions; the metric is the mean of AUROC_r over the 10 repeats. Within a subset, only the subset's samples form pairs. Patient bootstrap: patients resampled with replacement keep their fold in every repeat; a patient drawn k times contributes its samples k times. Paired permutation: a patient's scores are swapped between the two arms in all repeats at once. Arms: L-CNV, L-IMG, L-EARLY, L-LATE (L-LATE per repeat = mean of that repeat's L-CNV and L-IMG probabilities), both CNV sources, all four subsets, with Δ vs L-CNV, CI and p. The intercept-only model (prediction = training-row prevalence) is scored the same way; it is constant within a fold, so its value is 0.5 by construction, reported as a check.

## 2. Selection-adjusted p under the stratified CV

The checks' family was 8 non-CNV arms (L-IMG, L-EARLY, L-INTER, L-LATE, N-IMG, N-EARLY, N-INTER, N-LATE). Under the stratified CV only L-IMG, L-EARLY and L-LATE exist, and "no refit" rules out producing the others, so the family here is those 3 arms (PARTIAL). Single-step max-T as in the checks: one patient-swap mask per permutation applied to all arm-vs-L-CNV pairs; adjusted p = (1 + #{max |Δ| ≥ |Δ_j|}) / 2,001. Metrics: per-sample and patient-max AUROC on the repeat-averaged scores (as in the checks), and the item 1 fold-stratified AUROC. Their matrix and package features; all of set C and NDBE only. An adjusted p over 3 arms is a lower bound on the adjusted p over the 8-arm family.

## 3. ACE-B power for the primary contrast

- ACE-B size from the sample manifest (`phd/aceb_meta/ACEB_samples_for Rehan.csv`: samples with sWGS, their case and pathology): NDBE samples = Pathology "IM"; patients = cases with at least one IM sample. Patient status from the Barrett's-database timeline (`feasibility/runs/num_aceb_db_v2/output/aceb_participant_timeline.csv`, joined through the official case list), because the owner's per-patient labels are not on the cluster; the owner's aggregate split (11 progressors, 93 non-progressors, 30 prevalent HGD/IMC) is reported beside it.
- Size scenarios: (S1) P = prevalent or progressed (the Killcoyne-protocol label of `docs/aceb_primary_killcoyne.md`), NP = neither, patients with an IM sample and a database status; (S2) as S1 with prevalent patients removed; (S3) the owner's split, P = 11 + 30, NP = 93, all assumed to contribute NDBE samples (optimistic).
- Effect scenarios on set-C NDBE samples, using the repeat-averaged CV scores of L-CNV (pkg) and L-LATE (pkg): (E1) the development effect as observed (+0.059); (E2) the lower bound (+0.021), from a blended fusion score (1 − w)·L-CNV + w·L-LATE with w chosen by bisection so that the set-C NDBE Δ equals +0.021.
- Simulation (2,000 per scenario pair, seed = simulation index): draw n_P set-C P patients and n_NP set-C NP patients with replacement from the patients with NDBE samples, each bringing all its NDBE samples; compute Δ; run the primary analysis on the simulated set (2,000-resample patient bootstrap, `RandomState(simulation index)`, 5th percentile = one-sided 95% lower bound). Power = share of simulations whose lower bound exceeds 0. Simulated sample counts are reported next to ACE-B's.

## Status and outputs

Each item DONE / PARTIAL / NOT AVAILABLE; at most one line of interpretation. Scripts `scripts/paper_plan/kf_stats.py` (items 1, 2; sharded), `kf_aceb_size.py`, `kf_power.py` (item 3; sharded by scenario and simulation block), `kf_merge.py`, `kf_render.py`. Results `results/paper_final/killcoyne_final.json` (aggregates only). Row-level outputs on the cluster under `feasibility/paper_plan/killcoyne_mm/final/`. Jobs through `scripts/cluster/campaign.sh` (every task raced on all partitions plus pull workers).

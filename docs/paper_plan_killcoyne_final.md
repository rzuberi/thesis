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

---

## Results

Sources: `results/paper_final/killcoyne_final.json` · scripts `scripts/paper_plan/kf_*.py` · results commit b04e05e. Row-level outputs on the cluster under `feasibility/paper_plan/killcoyne_mm/final/`.

### Status

| Item | Status |
|---|---|
| 1 Fold-stratified AUROC | DONE |
| 2 Selection-adjusted p | PARTIAL (3 of the 8 arms exist under the stratified CV; no refit) |
| 3 ACE-B power | DONE (patient status from the database timeline, not the owner's per-patient labels) |

### 1. Fold-stratified AUROC (within-fold P–NP pairs, mean over 10 repeats)

| CNV source | Subset | Samples / patients (P) | L-CNV | L-IMG (Δ) | L-EARLY (Δ) | L-LATE (Δ) | Intercept-only |
|---|---|---|---|---|---|---|---|
| their | All of set C | 676 / 80 (37) | 0.848 [0.777, 0.908] | 0.873 [0.833, 0.909]; Δ +0.026 [-0.039, 0.097] (p 0.4868) | 0.899 [0.841, 0.945]; Δ +0.051 [0.019, 0.088] (p 0.009) | 0.917 [0.871, 0.949]; Δ +0.069 [0.028, 0.119] (p 0.0025) | 0.500 |
| their | (a) NDBE samples only | 463 / 75 (32) | 0.799 [0.695, 0.882] | 0.835 [0.788, 0.881]; Δ +0.036 [-0.045, 0.132] (p 0.4228) | 0.865 [0.773, 0.934]; Δ +0.066 [0.021, 0.120] (p 0.0205) | 0.879 [0.811, 0.933]; Δ +0.080 [0.031, 0.140] (p 0.008) | 0.500 |
| their | (b) before the first HGD/IMC | 571 / 75 (32) | 0.801 [0.710, 0.875] | 0.847 [0.798, 0.894]; Δ +0.045 [-0.036, 0.136] (p 0.3288) | 0.865 [0.787, 0.928]; Δ +0.063 [0.021, 0.111] (p 0.0155) | 0.889 [0.830, 0.934]; Δ +0.087 [0.037, 0.145] (p 0.0055) | 0.500 |
| their | (c) NDBE and before the first HGD/IMC | 438 / 71 (28) | 0.780 [0.681, 0.879] | 0.827 [0.768, 0.883]; Δ +0.047 [-0.040, 0.145] (p 0.3248) | 0.850 [0.753, 0.929]; Δ +0.070 [0.017, 0.131] (p 0.0295) | 0.867 [0.794, 0.931]; Δ +0.087 [0.034, 0.152] (p 0.009) | 0.500 |
| pkg | All of set C | 676 / 80 (37) | 0.878 [0.813, 0.931] | 0.873 [0.833, 0.909]; Δ -0.004 [-0.067, 0.069] (p 0.8926) | 0.910 [0.861, 0.951]; Δ +0.032 [0.008, 0.066] (p 0.015) | 0.929 [0.895, 0.957]; Δ +0.051 [0.014, 0.096] (p 0.016) | 0.500 |
| pkg | (a) NDBE samples only | 463 / 75 (32) | 0.839 [0.749, 0.905] | 0.835 [0.788, 0.881]; Δ -0.004 [-0.072, 0.082] (p 0.926) | 0.870 [0.791, 0.930]; Δ +0.032 [0.002, 0.073] (p 0.086) | 0.892 [0.835, 0.938]; Δ +0.053 [0.016, 0.103] (p 0.025) | 0.500 |
| pkg | (b) before the first HGD/IMC | 571 / 75 (32) | 0.845 [0.766, 0.904] | 0.847 [0.798, 0.894]; Δ +0.002 [-0.074, 0.090] (p 0.967) | 0.885 [0.822, 0.937]; Δ +0.040 [0.011, 0.078] (p 0.0125) | 0.903 [0.856, 0.944]; Δ +0.058 [0.016, 0.108] (p 0.023) | 0.500 |
| pkg | (c) NDBE and before the first HGD/IMC | 438 / 71 (28) | 0.823 [0.733, 0.901] | 0.827 [0.768, 0.883]; Δ +0.004 [-0.071, 0.088] (p 0.9215) | 0.863 [0.782, 0.929]; Δ +0.040 [0.005, 0.083] (p 0.0435) | 0.879 [0.818, 0.935]; Δ +0.056 [0.014, 0.106] (p 0.0425) | 0.500 |

### 2. Max-T adjusted p over the 3 non-CNV arms available under the stratified CV

Adjusted p over 3 arms is a lower bound on the adjusted p over the checks' 8-arm family.

| CNV source / subset | Arm | Metric | Δ vs L-CNV | p unadjusted | p max-T |
|---|---|---|---|---|---|
| their_all_C | L-IMG | per sample auroc | +0.032 | 0.3928 | 0.4568 |
| their_all_C | L-IMG | patient max auroc | -0.006 | 0.9125 | 0.992 |
| their_all_C | L-IMG | fold stratified auroc | +0.026 | 0.4868 | 0.6077 |
| their_all_C | L-EARLY | per sample auroc | +0.065 | 0.0005 | 0.071 |
| their_all_C | L-EARLY | patient max auroc | +0.064 | 0.0095 | 0.1774 |
| their_all_C | L-EARLY | fold stratified auroc | +0.051 | 0.009 | 0.1724 |
| their_all_C | L-LATE | per sample auroc | +0.076 | 0.002 | 0.033 |
| their_all_C | L-LATE | patient max auroc | +0.043 | 0.1104 | 0.4203 |
| their_all_C | L-LATE | fold stratified auroc | +0.069 | 0.0025 | 0.0545 |
| their_a_NDBE_only | L-IMG | per sample auroc | +0.049 | 0.3018 | 0.3578 |
| their_a_NDBE_only | L-IMG | patient max auroc | +0.066 | 0.3298 | 0.3603 |
| their_a_NDBE_only | L-IMG | fold stratified auroc | +0.036 | 0.4228 | 0.5702 |
| their_a_NDBE_only | L-EARLY | per sample auroc | +0.082 | 0.003 | 0.0755 |
| their_a_NDBE_only | L-EARLY | patient max auroc | +0.105 | 0.0045 | 0.1274 |
| their_a_NDBE_only | L-EARLY | fold stratified auroc | +0.066 | 0.0205 | 0.1504 |
| their_a_NDBE_only | L-LATE | per sample auroc | +0.091 | 0.004 | 0.049 |
| their_a_NDBE_only | L-LATE | patient max auroc | +0.104 | 0.014 | 0.1314 |
| their_a_NDBE_only | L-LATE | fold stratified auroc | +0.080 | 0.008 | 0.075 |
| pkg_all_C | L-IMG | per sample auroc | -0.008 | 0.8301 | 0.96 |
| pkg_all_C | L-IMG | patient max auroc | -0.003 | 0.958 | 0.9995 |
| pkg_all_C | L-IMG | fold stratified auroc | -0.004 | 0.8926 | 0.988 |
| pkg_all_C | L-EARLY | per sample auroc | +0.032 | 0.0135 | 0.3793 |
| pkg_all_C | L-EARLY | patient max auroc | +0.050 | 0.016 | 0.3203 |
| pkg_all_C | L-EARLY | fold stratified auroc | +0.032 | 0.015 | 0.3808 |
| pkg_all_C | L-LATE | per sample auroc | +0.050 | 0.0145 | 0.1479 |
| pkg_all_C | L-LATE | patient max auroc | +0.056 | 0.052 | 0.2569 |
| pkg_all_C | L-LATE | fold stratified auroc | +0.051 | 0.016 | 0.1514 |
| pkg_a_NDBE_only | L-IMG | per sample auroc | +0.002 | 0.967 | 1.0 |
| pkg_a_NDBE_only | L-IMG | patient max auroc | -0.003 | 0.9635 | 1.0 |
| pkg_a_NDBE_only | L-IMG | fold stratified auroc | -0.004 | 0.926 | 0.9965 |
| pkg_a_NDBE_only | L-EARLY | per sample auroc | +0.033 | 0.0715 | 0.5112 |
| pkg_a_NDBE_only | L-EARLY | patient max auroc | +0.052 | 0.043 | 0.4123 |
| pkg_a_NDBE_only | L-EARLY | fold stratified auroc | +0.032 | 0.086 | 0.5392 |
| pkg_a_NDBE_only | L-LATE | per sample auroc | +0.059 | 0.018 | 0.1794 |
| pkg_a_NDBE_only | L-LATE | patient max auroc | +0.076 | 0.034 | 0.1934 |
| pkg_a_NDBE_only | L-LATE | fold stratified auroc | +0.053 | 0.025 | 0.2189 |

### 3. ACE-B power for the primary contrast (L-LATE pkg − L-CNV pkg, per-sample AUROC, NDBE samples, one-sided)

Manifest: 234 sWGS samples from 117 cases; 163 NDBE (IM) samples from 107 cases. NDBE cases by database status: {'non_progressor': 67, 'progressed': 15, 'no_database_status': 14, 'prevalent': 11}; NDBE samples by status: {'non_progressor': 101, 'no_database_status': 27, 'progressed': 20, 'prevalent': 15}. Owner's aggregate split: 11 progressors, 93 non-progressors, 30 prevalent HGD/IMC (134 patients, 294 samples).

Rows marked [post hoc] were added after the pre-specified runs showed two problems: (1) simulated patients bring set C's NDBE samples (about 6 per patient) whereas ACE-B's cases have 1–3, so the pre-specified simulation has 4–5 times ACE-B's sample count; the S1m/S2m rows keep, for each drawn patient, a number of its NDBE samples drawn from ACE-B's per-case distribution for its class. (2) The pre-specified +0.021 scenario blends 20% L-LATE into L-CNV, which makes the two arms nearly identical and the difference nearly noise-free, so its power is not a conservative figure; the last column instead shifts each full-effect simulation's lower bound down by 0.038 (the gap between +0.059 and +0.021), keeping the full-effect variance.

| Size scenario | Effect | P / NP patients | ACE-B NDBE samples | Median simulated samples | Set-C Δ (blend w) | Median simulated Δ | Median lower bound | Power (lower bound > 0) | Power at +0.021 by shift [post hoc] |
|---|---|---|---|---|---|---|---|---|---|
| S1: manifest IM samples; P = prevalent or progressed (database) | development (+0.059) | 26 / 67 | 136 | 624 | +0.059 (1.0) | +0.056 | +0.020 | 0.902 [0.889, 0.915] | 0.169 |
| S1: manifest IM samples; P = prevalent or progressed (database) | lower bound (+0.021, blend) | 26 / 67 | 136 | 624 | +0.021 (0.1993) | +0.020 | +0.012 | 1.000 [1.000, 1.000] | — |
| S2: S1 without prevalent patients | development (+0.059) | 15 / 67 | 121 | 581 | +0.059 (1.0) | +0.057 | +0.014 | 0.776 [0.758, 0.794] | 0.127 |
| S2: S1 without prevalent patients | lower bound (+0.021, blend) | 15 / 67 | 121 | 581 | +0.021 (0.1993) | +0.020 | +0.010 | 1.000 [1.000, 1.000] | — |
| S3: owner's split, P = 11 progressors + 30 prevalent, NP = 93, all assumed to contribute NDBE samples | development (+0.059) | 41 / 93 | — | 887 | +0.059 (1.0) | +0.057 | +0.027 | 0.981 [0.974, 0.987] | 0.250 |
| S3: owner's split, P = 11 progressors + 30 prevalent, NP = 93, all assumed to contribute NDBE samples | lower bound (+0.021, blend) | 41 / 93 | — | 887 | +0.021 (0.1993) | +0.020 | +0.013 | 1.000 [1.000, 1.000] | — |
| S1m: manifest IM samples; P = prevalent or progressed (database) [post hoc: ACE-B sample count per patient] | development (+0.059) | 26 / 67 | 136 | 134 | +0.059 (1.0) | +0.064 | +0.015 | 0.725 [0.705, 0.744] | 0.199 |
| S2m: S1 without prevalent patients [post hoc: ACE-B sample count per patient] | development (+0.059) | 15 / 67 | 121 | 120 | +0.059 (1.0) | +0.063 | +0.003 | 0.537 [0.516, 0.559] | 0.134 |

**Interpretation.** With every pair scored by the same fold model, L-LATE still beats L-CNV (fold-stratified Δ +0.069 on their matrix and +0.051 on package features, all of set C); over the 3 available arms only L-LATE on their matrix keeps an adjusted p below 0.05 (per sample 0.033 on all of set C, 0.049 on NDBE samples), and at ACE-B's real NDBE sample count the primary contrast has power 0.73 (S1) or 0.54 (S2) at the development effect and 0.20 or 0.13 at +0.021.

**Caveats.** (1) The intercept-only model scores exactly 0.500 under the fold-stratified metric in every subset, as it must. (2) Item 2 covers 3 of the checks' 8 arms (no refit); its adjusted p values are lower bounds for the 8-arm family, so the adjusted p for L-LATE on their matrix could exceed 0.05 over all 8 arms. (3) ACE-B patient status comes from the Barrett's-database timeline (LLM-jury grades, cross-check), not the owner's adjudicated labels; 14 of the 107 NDBE cases have no database status and are left out of S1/S2. (4) The pre-specified power rows overstate power: simulated sets carry about 4–5 times ACE-B's NDBE sample count, and the blended +0.021 scenario is nearly noise-free (power 1.000). The sample-count-matched rows (S1m, S2m) and the shifted +0.021 column were added post hoc to correct both. (5) Simulated patients are resampled from set C, so power assumes ACE-B behaves like set C (same scanner, depth and case mix), which it does not (Aperio .svs, about 7× sWGS).

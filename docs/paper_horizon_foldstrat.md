# Fold-stratified IPCW time-dependent AUROC for the 1/3/5-year table

Status: PRE-SPECIFICATION (written 2026-10-05). Nothing below has been run. Results are appended under the line at the end in a later commit; this section is not edited afterwards.

Ground rules as in `docs/paper_horizon_answers.md` (pre-specification 81473df, results afa0278): no refit; rank AUROC to 3 decimals; patient-clustered bootstrap 2,000 draws `RandomState(0)`; within-patient swap permutation 2,000 draws seed 0; status per item; at most one line of interpretation; earlier docs not edited. ACE-B not touched.

## Why

The pooled per-sample AUROC of `docs/paper_horizon_answers.md` ranks a case scored by one outer-fold model against a control scored by another. Under the stratified CV the fold models' intercepts move with their training prevalence, which is how an intercept-only prediction reaches 0.29–0.41 there (`q0_intercept_only.json`). Restricting to case–control pairs scored by the same fold model removes that between-model component; an intercept-only prediction then gives exactly 0.500 (all its within-fold pairs are ties).

## Definition

For horizon t, CNV source s and population (all pre-event samples; NDBE pre-event samples), with the cases, controls, censoring weights and samples of `docs/paper_horizon_answers.md` (event times from `hz_prep.py`; case: event within t; control: event-free with follow-up ≥ t; w_i = 1/Ĝ(T_i−), Ĝ = reverse Kaplan–Meier over the evaluated samples):

- For each repeat r = 1..10, with that repeat's out-of-fold probabilities p_r and outer fold f_r (from the `kv_cv.R` prediction files; every arm shares the same folds per repeat):
  AUC_r(t) = Σ_k Σ_{i case, j control, f_r(i) = f_r(j) = k} w_i [1(p_r(i) > p_r(j)) + ½·1(p_r(i) = p_r(j))] / Σ_k Σ_{same pairs} w_i.
- Fold-stratified IPCW AUROC = mean of AUC_r(t) over the 10 repeats. (The unweighted version, w_i = 1, is reported alongside.) This is the IPCW extension of the fold-stratified AUROC in `scripts/paper_plan/kf_stats.py` (`fs_auc`).
- Arms (no refit): L-CLIN and L-CLIN without grade (`ha_clin.py` outer predictions), L-CNV, L-IMG, L-EARLY (`kv_cv.R`), L-INTER (`hz_fit.R` outer), L-LATE (per-repeat mean of L-CNV and L-IMG probabilities). Intercept-only check: p_r = the training-fold prevalence (`train_prev` in the `kv_cv.R` files); expected 0.500 by construction.
- CI: 2,000 patient-bootstrap draws (`RandomState(0)`); a resampled patient keeps its fold label in every repeat; Ĝ re-estimated per draw.

## Q1 deltas under this metric

Paired Δ of every arm against L-LATE and against L-CNV on the same bootstrap draws; swap-permutation p (each patient's two arms' per-repeat probabilities swapped together) with single-step max-T over the 5 non-clinical arms, families as in `docs/paper_horizon_answers.md` (Δ vs L-LATE: L-CNV, L-IMG, L-EARLY, L-INTER; Δ vs L-CNV: L-IMG, L-EARLY, L-INTER, L-LATE). Best arm per horizon = highest fold-stratified IPCW AUROC among the six table rows.

## Output

`docs/paper_horizon_foldstrat.md` (results below); script `scripts/paper_plan/hf_foldstrat.py` (one Slurm task per CNV source × population × horizon via `scripts/cluster/campaign.sh`), `scripts/paper_plan/hf_render.py`; results `results/paper_final/horizon_foldstrat/*.json`; figure: fold-stratified vs pooled AUROC per arm and horizon (PNG, PDF, JSON).

---

## Results

Pre-specification commit 2d0014f; results commit d6b43ff. Script `scripts/paper_plan/hf_foldstrat.py` (Slurm via `scripts/cluster/campaign.sh`, prefix hf, one task per CNV source × population × horizon), `scripts/paper_plan/hf_render.py`. Results `results/paper_final/horizon_foldstrat/fs_{their,pkg}_{pre,pre_ndbe}_{1,3,5}.json`; figure `results/paper_final/horizon_foldstrat/figs/foldstrat_vs_pooled.{png,pdf,json}`. Pooled values from `results/paper_final/horizon_answers/q0_*.json` (afa0278).

### Status

| Item | Status |
|---|---|
| Fold-stratified IPCW AUROC, every row and horizon, both CNV sources, both populations | DONE |
| Intercept-only check (expected 0.500) | DONE: 0.500 in all 12 cells |
| Q1 deltas vs L-CNV and vs L-LATE under this metric | DONE |

Every arm's fold assignment matches `kv_cv.R` in all 10 repeats (yes). Valid bootstrap draws: 2,000 of 2,000 in every cell.

### Answer

Restricted to same-fold case–control pairs, the intercept-only prediction scores 0.500 at every horizon, so the metric removes the between-fold-model artefact. The CNV, image and fusion arms fall by 0.00–0.04 from their pooled values (the clinical arms rise slightly); L-LATE remains the best arm on all pre-event samples at 1, 3 and 5 years with either CNV source (0.854, 0.831, 0.821 on their matrix), and its gain over L-CNV (+0.043, +0.064, +0.043) is not significant after max-T adjustment (p 0.7391, 0.2574, 0.6427). Demographics-only L-CLIN stays below 0.5 under this metric (0.383, 0.364, 0.385), so its pooled shortfall is not only the intercept artefact. One line: the fusion ranking survives fold stratification; the size of its advantage over CNV remains unresolved.

### Table: their matrix, all pre-event samples

Fold-stratified IPCW time-dependent AUROC [95% patient-bootstrap CI] (pooled per-sample IPCW AUROC from `docs/paper_horizon_answers.md` in parentheses).

|  | Internal 1-year | Internal 3-year | Internal 5-year | ACE-B 1 | ACE-B 3 | ACE-B 5 |
|---|---|---|---|---|---|---|
| Clinical Only (baseline) | 0.621 [0.456, 0.768] (pooled 0.604) | 0.457 [0.349, 0.577] (pooled 0.430) | 0.490 [0.392, 0.593] (pooled 0.458) | pending | pending | pending |
| CNV (replication) | 0.811 [0.656, 0.923] (pooled 0.815) | 0.767 [0.655, 0.841] (pooled 0.775) | 0.779 [0.669, 0.841] (pooled 0.792) | pending | pending | pending |
| WSI | 0.771 [0.631, 0.846] (pooled 0.782) | 0.788 [0.659, 0.866] (pooled 0.817) | 0.760 [0.661, 0.819] (pooled 0.786) | pending | pending | pending |
| Early fusion | 0.839 [0.714, 0.918] (pooled 0.853) | 0.802 [0.691, 0.872] (pooled 0.828) | 0.792 [0.688, 0.854] (pooled 0.820) | pending | pending | pending |
| Inter fusion | 0.811 [0.658, 0.899] (pooled 0.829) | 0.793 [0.683, 0.873] (pooled 0.818) | 0.765 [0.665, 0.837] (pooled 0.787) | pending | pending | pending |
| Late fusion | 0.854 [0.747, 0.907] (pooled 0.869) | 0.831 [0.705, 0.898] (pooled 0.855) | 0.821 [0.716, 0.873] (pooled 0.844) | pending | pending | pending |
| Demographics only (L-CLIN without grade) | 0.383 [0.268, 0.528] (pooled 0.348) | 0.364 [0.278, 0.485] (pooled 0.294) | 0.385 [0.294, 0.510] (pooled 0.313) | pending | pending | pending |
| Intercept-only check | 0.500 [0.500, 0.500] | 0.500 [0.500, 0.500] | 0.500 [0.500, 0.500] | pending | pending | pending |
| n cases / n controls (samples; patients); within-fold pairs, repeat 1 | 29 / 449; 14 / 72; 1,313 of 13,021 | 99 / 277; 29 / 62; 2,557 of 27,423 | 126 / 168; 32 / 46; 1,886 of 21,168 | pending (slides being scanned) | pending (slides being scanned) | pending (slides being scanned) |

### Table: their matrix, NDBE pre-event samples

Fold-stratified IPCW time-dependent AUROC [95% patient-bootstrap CI] (pooled per-sample IPCW AUROC from `docs/paper_horizon_answers.md` in parentheses).

|  | Internal 1-year | Internal 3-year | Internal 5-year | ACE-B 1 | ACE-B 3 | ACE-B 5 |
|---|---|---|---|---|---|---|
| Clinical Only (baseline) | 0.314 [0.178, 0.499] (pooled 0.260) | 0.344 [0.249, 0.485] (pooled 0.268) | 0.433 [0.301, 0.585] (pooled 0.342) | pending | pending | pending |
| CNV (replication) | 0.873 [0.716, 0.951] (pooled 0.873) | 0.775 [0.642, 0.875] (pooled 0.772) | 0.752 [0.636, 0.839] (pooled 0.763) | pending | pending | pending |
| WSI | 0.727 [0.542, 0.844] (pooled 0.731) | 0.756 [0.631, 0.846] (pooled 0.780) | 0.714 [0.593, 0.778] (pooled 0.744) | pending | pending | pending |
| Early fusion | 0.884 [0.753, 0.942] (pooled 0.889) | 0.802 [0.673, 0.895] (pooled 0.826) | 0.752 [0.607, 0.843] (pooled 0.788) | pending | pending | pending |
| Inter fusion | 0.866 [0.657, 0.934] (pooled 0.881) | 0.801 [0.657, 0.904] (pooled 0.812) | 0.758 [0.616, 0.860] (pooled 0.770) | pending | pending | pending |
| Late fusion | 0.869 [0.748, 0.927] (pooled 0.870) | 0.806 [0.677, 0.900] (pooled 0.823) | 0.769 [0.652, 0.840] (pooled 0.792) | pending | pending | pending |
| Demographics only (L-CLIN without grade) | 0.348 [0.208, 0.530] (pooled 0.331) | 0.393 [0.297, 0.528] (pooled 0.336) | 0.441 [0.337, 0.581] (pooled 0.389) | pending | pending | pending |
| Intercept-only check | 0.500 [0.500, 0.500] | 0.500 [0.500, 0.500] | 0.500 [0.500, 0.500] | pending | pending | pending |
| n cases / n controls (samples; patients); within-fold pairs, repeat 1 | 12 / 334; 9 / 69; 393 of 4,008 | 61 / 192; 25 / 59; 1,133 of 11,712 | 79 / 111; 26 / 39; 833 of 8,769 | pending (slides being scanned) | pending (slides being scanned) | pending (slides being scanned) |

### Table: package features, all pre-event samples

Fold-stratified IPCW time-dependent AUROC [95% patient-bootstrap CI] (pooled per-sample IPCW AUROC from `docs/paper_horizon_answers.md` in parentheses).

|  | Internal 1-year | Internal 3-year | Internal 5-year | ACE-B 1 | ACE-B 3 | ACE-B 5 |
|---|---|---|---|---|---|---|
| Clinical Only (baseline) | 0.621 [0.456, 0.768] (pooled 0.604) | 0.457 [0.349, 0.577] (pooled 0.430) | 0.490 [0.392, 0.593] (pooled 0.458) | pending | pending | pending |
| CNV (replication) | 0.790 [0.663, 0.873] (pooled 0.805) | 0.757 [0.623, 0.820] (pooled 0.779) | 0.780 [0.640, 0.852] (pooled 0.796) | pending | pending | pending |
| WSI | 0.771 [0.631, 0.846] (pooled 0.782) | 0.788 [0.659, 0.866] (pooled 0.817) | 0.760 [0.661, 0.819] (pooled 0.786) | pending | pending | pending |
| Early fusion | 0.822 [0.689, 0.886] (pooled 0.836) | 0.790 [0.656, 0.855] (pooled 0.814) | 0.791 [0.664, 0.863] (pooled 0.811) | pending | pending | pending |
| Inter fusion | 0.786 [0.650, 0.857] (pooled 0.802) | 0.799 [0.683, 0.865] (pooled 0.822) | 0.787 [0.686, 0.851] (pooled 0.803) | pending | pending | pending |
| Late fusion | 0.838 [0.720, 0.893] (pooled 0.852) | 0.817 [0.685, 0.887] (pooled 0.842) | 0.818 [0.698, 0.878] (pooled 0.839) | pending | pending | pending |
| Demographics only (L-CLIN without grade) | 0.383 [0.268, 0.528] (pooled 0.348) | 0.364 [0.278, 0.485] (pooled 0.294) | 0.385 [0.294, 0.510] (pooled 0.313) | pending | pending | pending |
| Intercept-only check | 0.500 [0.500, 0.500] | 0.500 [0.500, 0.500] | 0.500 [0.500, 0.500] | pending | pending | pending |
| n cases / n controls (samples; patients); within-fold pairs, repeat 1 | 29 / 449; 14 / 72; 1,313 of 13,021 | 99 / 277; 29 / 62; 2,557 of 27,423 | 126 / 168; 32 / 46; 1,886 of 21,168 | pending (slides being scanned) | pending (slides being scanned) | pending (slides being scanned) |

### Table: package features, NDBE pre-event samples

Fold-stratified IPCW time-dependent AUROC [95% patient-bootstrap CI] (pooled per-sample IPCW AUROC from `docs/paper_horizon_answers.md` in parentheses).

|  | Internal 1-year | Internal 3-year | Internal 5-year | ACE-B 1 | ACE-B 3 | ACE-B 5 |
|---|---|---|---|---|---|---|
| Clinical Only (baseline) | 0.314 [0.178, 0.499] (pooled 0.260) | 0.344 [0.249, 0.485] (pooled 0.268) | 0.433 [0.301, 0.585] (pooled 0.342) | pending | pending | pending |
| CNV (replication) | 0.820 [0.643, 0.908] (pooled 0.826) | 0.738 [0.609, 0.827] (pooled 0.749) | 0.753 [0.624, 0.836] (pooled 0.758) | pending | pending | pending |
| WSI | 0.727 [0.542, 0.844] (pooled 0.731) | 0.756 [0.631, 0.846] (pooled 0.780) | 0.714 [0.593, 0.778] (pooled 0.744) | pending | pending | pending |
| Early fusion | 0.822 [0.653, 0.891] (pooled 0.830) | 0.761 [0.632, 0.848] (pooled 0.776) | 0.745 [0.585, 0.842] (pooled 0.756) | pending | pending | pending |
| Inter fusion | 0.775 [0.610, 0.849] (pooled 0.788) | 0.798 [0.668, 0.885] (pooled 0.819) | 0.772 [0.624, 0.864] (pooled 0.792) | pending | pending | pending |
| Late fusion | 0.830 [0.697, 0.889] (pooled 0.837) | 0.779 [0.657, 0.876] (pooled 0.798) | 0.769 [0.647, 0.837] (pooled 0.785) | pending | pending | pending |
| Demographics only (L-CLIN without grade) | 0.348 [0.208, 0.530] (pooled 0.331) | 0.393 [0.297, 0.528] (pooled 0.336) | 0.441 [0.337, 0.581] (pooled 0.389) | pending | pending | pending |
| Intercept-only check | 0.500 [0.500, 0.500] | 0.500 [0.500, 0.500] | 0.500 [0.500, 0.500] | pending | pending | pending |
| n cases / n controls (samples; patients); within-fold pairs, repeat 1 | 12 / 334; 9 / 69; 393 of 4,008 | 61 / 192; 25 / 59; 1,133 of 11,712 | 79 / 111; 26 / 39; 833 of 8,769 | pending (slides being scanned) | pending (slides being scanned) | pending (slides being scanned) |

### Q1 under this metric: their matrix, all pre-event samples

Paired Δ on the same bootstrap draws; swap-permutation p and single-step max-T over the 5 non-clinical arms (clinical rows: CI only).

| Horizon | Arm | Fold-stratified AUROC | Δ vs L-LATE [CI] (p, max-T) | Δ vs L-CNV [CI] (p, max-T) |
|---|---|---|---|---|
| 1 y | L-CLIN | 0.621 | -0.233 [-0.402, -0.037] | -0.189 [-0.431, +0.053] |
| 1 y | L-CNV | 0.811 | -0.043 [-0.119, +0.065] (p 0.5097, max-T 0.7956) | — |
| 1 y | L-IMG | 0.771 | -0.083 [-0.177, -0.002] (p 0.0895, max-T 0.1779) | -0.039 [-0.239, +0.107] (p 0.6387, max-T 0.7836) |
| 1 y | L-EARLY | 0.839 | -0.015 [-0.059, +0.048] (p 0.901, max-T 0.9965) | +0.028 [-0.043, +0.085] (p 0.3138, max-T 0.9315) |
| 1 y | L-INTER | 0.811 | -0.043 [-0.109, +0.032] (p 0.3758, max-T 0.7961) | +0.000 [-0.087, +0.060] (p 0.9985, max-T 1.0) |
| 1 y | L-LATE | 0.854 | — | +0.043 [-0.065, +0.119] (p 0.5097, max-T 0.7391) |
| 1 y | best | L-LATE | ranking: L-LATE > L-EARLY > L-INTER > L-CNV > L-IMG > L-CLIN |  |
| 3 y | L-CLIN | 0.457 | -0.374 [-0.457, -0.256] | -0.310 [-0.423, -0.156] |
| 3 y | L-CNV | 0.767 | -0.064 [-0.135, +0.004] (p 0.062, max-T 0.1149) | — |
| 3 y | L-IMG | 0.788 | -0.043 [-0.092, +0.001] (p 0.1224, max-T 0.4563) | +0.021 [-0.086, +0.132] (p 0.6832, max-T 0.9055) |
| 3 y | L-EARLY | 0.802 | -0.030 [-0.075, +0.018] (p 0.3323, max-T 0.7411) | +0.034 [-0.011, +0.085] (p 0.1924, max-T 0.6667) |
| 3 y | L-INTER | 0.793 | -0.038 [-0.105, +0.033] (p 0.2294, max-T 0.5537) | +0.026 [-0.035, +0.102] (p 0.4563, max-T 0.8191) |
| 3 y | L-LATE | 0.831 | — | +0.064 [-0.004, +0.135] (p 0.062, max-T 0.2574) |
| 3 y | best | L-LATE | ranking: L-LATE > L-EARLY > L-INTER > L-IMG > L-CNV > L-CLIN |  |
| 5 y | L-CLIN | 0.490 | -0.331 [-0.425, -0.199] | -0.289 [-0.397, -0.145] |
| 5 y | L-CNV | 0.779 | -0.043 [-0.105, +0.013] (p 0.1954, max-T 0.6217) | — |
| 5 y | L-IMG | 0.760 | -0.061 [-0.108, -0.017] (p 0.0305, max-T 0.2764) | -0.018 [-0.109, +0.079] (p 0.7286, max-T 0.9605) |
| 5 y | L-EARLY | 0.792 | -0.030 [-0.090, +0.030] (p 0.4083, max-T 0.8401) | +0.013 [-0.044, +0.077] (p 0.6492, max-T 0.99) |
| 5 y | L-INTER | 0.765 | -0.056 [-0.128, +0.039] (p 0.2484, max-T 0.3638) | -0.013 [-0.087, +0.075] (p 0.7966, max-T 0.9895) |
| 5 y | L-LATE | 0.821 | — | +0.043 [-0.013, +0.105] (p 0.1954, max-T 0.6427) |
| 5 y | best | L-LATE | ranking: L-LATE > L-EARLY > L-CNV > L-INTER > L-IMG > L-CLIN |  |

### Q1 under this metric: their matrix, NDBE pre-event samples

Paired Δ on the same bootstrap draws; swap-permutation p and single-step max-T over the 5 non-clinical arms (clinical rows: CI only).

| Horizon | Arm | Fold-stratified AUROC | Δ vs L-LATE [CI] (p, max-T) | Δ vs L-CNV [CI] (p, max-T) |
|---|---|---|---|---|
| 1 y | L-CLIN | 0.314 | -0.555 [-0.688, -0.312] | -0.558 [-0.735, -0.278] |
| 1 y | L-CNV | 0.873 | +0.004 [-0.086, +0.098] (p 0.9255, max-T 1.0) | — |
| 1 y | L-IMG | 0.727 | -0.141 [-0.267, -0.033] (p 0.0415, max-T 0.0415) | -0.145 [-0.355, +0.046] (p 0.1809, max-T 0.1809) |
| 1 y | L-EARLY | 0.884 | +0.016 [-0.037, +0.077] (p 0.6027, max-T 0.996) | +0.012 [-0.051, +0.075] (p 0.5007, max-T 0.9985) |
| 1 y | L-INTER | 0.866 | -0.003 [-0.124, +0.059] (p 0.93, max-T 1.0) | -0.007 [-0.121, +0.068] (p 0.8431, max-T 1.0) |
| 1 y | L-LATE | 0.869 | — | -0.004 [-0.098, +0.086] (p 0.9255, max-T 1.0) |
| 1 y | best | L-EARLY | ranking: L-EARLY > L-CNV > L-LATE > L-INTER > L-IMG > L-CLIN |  |
| 3 y | L-CLIN | 0.344 | -0.463 [-0.567, -0.301] | -0.432 [-0.547, -0.254] |
| 3 y | L-CNV | 0.775 | -0.031 [-0.110, +0.030] (p 0.3188, max-T 0.7691) | — |
| 3 y | L-IMG | 0.756 | -0.051 [-0.113, +0.007] (p 0.1229, max-T 0.3598) | -0.020 [-0.127, +0.098] (p 0.7236, max-T 0.945) |
| 3 y | L-EARLY | 0.802 | -0.005 [-0.056, +0.036] (p 0.8541, max-T 0.9995) | +0.027 [-0.015, +0.081] (p 0.3658, max-T 0.8676) |
| 3 y | L-INTER | 0.801 | -0.005 [-0.077, +0.070] (p 0.9155, max-T 0.9995) | +0.026 [-0.046, +0.126] (p 0.5792, max-T 0.8721) |
| 3 y | L-LATE | 0.806 | — | +0.031 [-0.030, +0.110] (p 0.3188, max-T 0.7971) |
| 3 y | best | L-LATE | ranking: L-LATE > L-EARLY > L-INTER > L-CNV > L-IMG > L-CLIN |  |
| 5 y | L-CLIN | 0.433 | -0.337 [-0.490, -0.140] | -0.320 [-0.474, -0.120] |
| 5 y | L-CNV | 0.752 | -0.017 [-0.086, +0.044] (p 0.6022, max-T 0.972) | — |
| 5 y | L-IMG | 0.714 | -0.055 [-0.125, -0.010] (p 0.093, max-T 0.4093) | -0.038 [-0.152, +0.061] (p 0.4993, max-T 0.7701) |
| 5 y | L-EARLY | 0.752 | -0.018 [-0.107, +0.064] (p 0.6557, max-T 0.967) | -0.001 [-0.089, +0.085] (p 0.987, max-T 1.0) |
| 5 y | L-INTER | 0.758 | -0.012 [-0.093, +0.092] (p 0.8121, max-T 0.9935) | +0.006 [-0.079, +0.113] (p 0.918, max-T 0.9995) |
| 5 y | L-LATE | 0.769 | — | +0.017 [-0.044, +0.086] (p 0.6022, max-T 0.9715) |
| 5 y | best | L-LATE | ranking: L-LATE > L-INTER > L-CNV > L-EARLY > L-IMG > L-CLIN |  |

### Q1 under this metric: package features, all pre-event samples

Paired Δ on the same bootstrap draws; swap-permutation p and single-step max-T over the 5 non-clinical arms (clinical rows: CI only).

| Horizon | Arm | Fold-stratified AUROC | Δ vs L-LATE [CI] (p, max-T) | Δ vs L-CNV [CI] (p, max-T) |
|---|---|---|---|---|
| 1 y | L-CLIN | 0.621 | -0.217 [-0.373, -0.024] | -0.168 [-0.363, +0.052] |
| 1 y | L-CNV | 0.790 | -0.048 [-0.113, +0.027] (p 0.2374, max-T 0.4538) | — |
| 1 y | L-IMG | 0.771 | -0.067 [-0.140, -0.002] (p 0.1039, max-T 0.1754) | -0.018 [-0.158, +0.097] (p 0.7846, max-T 0.9565) |
| 1 y | L-EARLY | 0.822 | -0.016 [-0.057, +0.021] (p 0.4758, max-T 0.974) | +0.032 [-0.037, +0.084] (p 0.2504, max-T 0.7796) |
| 1 y | L-INTER | 0.786 | -0.052 [-0.107, +0.016] (p 0.091, max-T 0.3913) | -0.004 [-0.083, +0.068] (p 0.943, max-T 1.0) |
| 1 y | L-LATE | 0.838 | — | +0.048 [-0.027, +0.113] (p 0.2374, max-T 0.5447) |
| 1 y | best | L-LATE | ranking: L-LATE > L-EARLY > L-CNV > L-INTER > L-IMG > L-CLIN |  |
| 3 y | L-CLIN | 0.457 | -0.360 [-0.439, -0.239] | -0.300 [-0.402, -0.137] |
| 3 y | L-CNV | 0.757 | -0.060 [-0.144, -0.000] (p 0.029, max-T 0.0455) | — |
| 3 y | L-IMG | 0.788 | -0.029 [-0.066, +0.013] (p 0.2114, max-T 0.6202) | +0.031 [-0.061, +0.145] (p 0.4973, max-T 0.6117) |
| 3 y | L-EARLY | 0.790 | -0.027 [-0.082, +0.010] (p 0.1899, max-T 0.6672) | +0.033 [-0.011, +0.087] (p 0.1054, max-T 0.5712) |
| 3 y | L-INTER | 0.799 | -0.018 [-0.074, +0.044] (p 0.4833, max-T 0.8846) | +0.042 [-0.018, +0.130] (p 0.1894, max-T 0.4258) |
| 3 y | L-LATE | 0.817 | — | +0.060 [+0.000, +0.144] (p 0.029, max-T 0.1844) |
| 3 y | best | L-LATE | ranking: L-LATE > L-INTER > L-EARLY > L-IMG > L-CNV > L-CLIN |  |
| 5 y | L-CLIN | 0.490 | -0.328 [-0.414, -0.205] | -0.291 [-0.384, -0.149] |
| 5 y | L-CNV | 0.780 | -0.037 [-0.097, +0.014] (p 0.2304, max-T 0.5292) | — |
| 5 y | L-IMG | 0.760 | -0.057 [-0.108, -0.000] (p 0.0315, max-T 0.1429) | -0.020 [-0.110, +0.087] (p 0.7031, max-T 0.8771) |
| 5 y | L-EARLY | 0.791 | -0.026 [-0.077, +0.021] (p 0.3713, max-T 0.7761) | +0.011 [-0.028, +0.056] (p 0.4873, max-T 0.9785) |
| 5 y | L-INTER | 0.787 | -0.030 [-0.084, +0.049] (p 0.3328, max-T 0.6912) | +0.007 [-0.054, +0.098] (p 0.8131, max-T 0.997) |
| 5 y | L-LATE | 0.818 | — | +0.037 [-0.014, +0.097] (p 0.2304, max-T 0.5872) |
| 5 y | best | L-LATE | ranking: L-LATE > L-EARLY > L-INTER > L-CNV > L-IMG > L-CLIN |  |

### Q1 under this metric: package features, NDBE pre-event samples

Paired Δ on the same bootstrap draws; swap-permutation p and single-step max-T over the 5 non-clinical arms (clinical rows: CI only).

| Horizon | Arm | Fold-stratified AUROC | Δ vs L-LATE [CI] (p, max-T) | Δ vs L-CNV [CI] (p, max-T) |
|---|---|---|---|---|
| 1 y | L-CLIN | 0.314 | -0.515 [-0.650, -0.267] | -0.505 [-0.694, -0.223] |
| 1 y | L-CNV | 0.820 | -0.010 [-0.099, +0.094] (p 0.8346, max-T 1.0) | — |
| 1 y | L-IMG | 0.727 | -0.102 [-0.219, +0.016] (p 0.1769, max-T 0.1869) | -0.092 [-0.310, +0.107] (p 0.4133, max-T 0.4633) |
| 1 y | L-EARLY | 0.822 | -0.007 [-0.078, +0.060] (p 0.8631, max-T 1.0) | +0.003 [-0.096, +0.067] (p 0.921, max-T 1.0) |
| 1 y | L-INTER | 0.775 | -0.054 [-0.141, +0.037] (p 0.3423, max-T 0.7836) | -0.044 [-0.179, +0.072] (p 0.7116, max-T 0.8941) |
| 1 y | L-LATE | 0.830 | — | +0.010 [-0.094, +0.099] (p 0.8346, max-T 0.9995) |
| 1 y | best | L-LATE | ranking: L-LATE > L-EARLY > L-CNV > L-INTER > L-IMG > L-CLIN |  |
| 3 y | L-CLIN | 0.344 | -0.435 [-0.533, -0.282] | -0.394 [-0.501, -0.219] |
| 3 y | L-CNV | 0.738 | -0.041 [-0.114, +0.008] (p 0.1144, max-T 0.4023) | — |
| 3 y | L-IMG | 0.756 | -0.023 [-0.077, +0.030] (p 0.4373, max-T 0.8436) | +0.018 [-0.071, +0.132] (p 0.7121, max-T 0.9215) |
| 3 y | L-EARLY | 0.761 | -0.018 [-0.072, +0.020] (p 0.4603, max-T 0.9195) | +0.023 [-0.025, +0.082] (p 0.3288, max-T 0.8441) |
| 3 y | L-INTER | 0.798 | +0.019 [-0.055, +0.097] (p 0.5517, max-T 0.9085) | +0.060 [-0.011, +0.162] (p 0.077, max-T 0.2474) |
| 3 y | L-LATE | 0.779 | — | +0.041 [-0.008, +0.114] (p 0.1144, max-T 0.5112) |
| 3 y | best | L-INTER | ranking: L-INTER > L-LATE > L-EARLY > L-IMG > L-CNV > L-CLIN |  |
| 5 y | L-CLIN | 0.433 | -0.337 [-0.470, -0.152] | -0.321 [-0.457, -0.152] |
| 5 y | L-CNV | 0.753 | -0.016 [-0.079, +0.050] (p 0.7006, max-T 0.965) | — |
| 5 y | L-IMG | 0.714 | -0.055 [-0.118, +0.000] (p 0.0975, max-T 0.2909) | -0.039 [-0.152, +0.067] (p 0.5007, max-T 0.6292) |
| 5 y | L-EARLY | 0.745 | -0.025 [-0.104, +0.052] (p 0.5032, max-T 0.8491) | -0.009 [-0.066, +0.045] (p 0.6872, max-T 0.9955) |
| 5 y | L-INTER | 0.772 | +0.002 [-0.073, +0.095] (p 0.946, max-T 1.0) | +0.018 [-0.054, +0.103] (p 0.5977, max-T 0.9385) |
| 5 y | L-LATE | 0.769 | — | +0.016 [-0.050, +0.079] (p 0.7006, max-T 0.958) |
| 5 y | best | L-INTER | ranking: L-INTER > L-LATE > L-CNV > L-EARLY > L-IMG > L-CLIN |  |

Unweighted fold-stratified AUROCs (w = 1) are in the JSON files (`arms.<arm>.unweighted`).

**Method.** Per repeat, IPCW-weighted concordance over case–control pairs from the same outer fold (cases weighted 1/Ĝ(T−), Ĝ the reverse Kaplan–Meier over the evaluated samples), pooled over folds, then averaged over the 10 repeats; bootstrap draws keep each resampled patient's folds and re-estimate Ĝ; permutation swaps a patient's two arms' per-repeat probabilities together.
**Sources.** `feasibility/paper_plan/killcoyne_mm/cv/preds/` (kv_cv.R, d69de24), `horizons/outer/inter_*` (hz_fit.R, 4d7efa9), `horizon_answers/clin_outer.csv` (ha_clin.py, afa0278), `horizons/samples.csv` (hz_prep.py).
**Caveats.** (1) Only about 9–10% of case–control pairs are within a fold (folds of 8 patients), so the intervals are wider than the pooled ones. (2) Within-fold pairs include pairs from the same progressor (an early control sample and a later case sample), which no between-patient ranking can separate except through the sample-level score. (3) Demographics-only stays below 0.5 under this metric: with a near-null signal, a model fitted on the other folds' patients is known to be negatively correlated with held-out patients' labels; this was not investigated further here. (4) Design caveat as before: AUROCs only; no absolute risk, calibration or PPV.


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

(appended in a later commit)

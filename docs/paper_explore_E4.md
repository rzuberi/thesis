# Exploration E4: train for time, not just class

Exploratory (round 9, 20–21 October 2026). Not confirmatory; everything tried is recorded. Rules: `paper/reviews_round7/decisions/EXPLORE_RULES.md`.

## Plan (written before any model was fitted)

**Idea.** The stored models are binary (progressor vs not). A progressor sample taken 10 years before the event and a non-progressor sample with 12 clean years of follow-up after it are both treated as certain labels, and a non-progressor sample taken a year before the last sequenced endoscopy counts the same as one with a decade of clean follow-up. Models that use time to event might rank risk better and so flag fewer non-progressors at the same catch rate.

**Population and folds.** Same as every round: models are trained on the 676 samples (80 patients) of the analysed set, exactly as the stored linear models, under the stored patient-grouped folds (`strat_folds(set C, REP, 10)`, 10 repeats × 10 folds; inner 5-fold OOF on the outer training patients, `strat_folds(..., 1000·REP + FOLD, 5)`). Evaluation on the 571 pre-event samples (288 endoscopies, 75 patients, 32 progressors). Features as stored: slide-mean UNI2-h embedding (z-scored on training rows) and the stored copy-number block (`cnv_their_C.csv`). glmnet, α = 0.9, `standardize = FALSE`, as stored.

**Time axis (row-level on the cluster only).** Exact dates (`pre_event_cohort.Date`).
- Progressor samples: time = sample date → event (first HGD/IMC endoscopy, rv8 reference date); event/post-event samples get 0.01 years.
- Non-progressor samples, censored. *Study follow-up*: to the last sequenced endoscopy (rv8 reference). *Extended follow-up* (main): to the later of that and the last Barrett's-database record (pathology report or endoscopy; linkage and tables as `paper/reviews_round7/lookup/data2.md` B), stopping before any later HGD+ report or HGD-register entry.

**Models** (each fitted inside every outer fold on training patients only, λ by patient-grouped inner CV on training patients):
1. **Cox elastic net** (`family = "cox"`) on the H&E embedding and on copy number; λ = minimum of the patient-grouped 5-fold partial-likelihood deviance averaged over 10 shuffles (outer) or 1 shuffle (inner OOF), mirroring the stored class-error rule. Main: extended follow-up (`cox_x`); sensitivity: study follow-up (`cox_s`). Score = linear predictor, z-scored on the model's own training rows.
2. **Horizon binary models**, H = 3 and 5 years: cases = progressor samples with event within H; controls = non-progressor samples with ≥ H extended follow-up; progressor samples > H before the event and non-progressors with < H follow-up are left out of training (scored like everyone else). Stored class-error λ rule.
3. **Certainty-weighted binary**: all training samples, stored labels; weights progressor samples 1 if ≤ 8 years before the event, 0.5 if > 8; non-progressor samples clip(extended follow-up / 5 years, 0.5, 1.5). Weighted class-error λ rule.
4. **Late fusion** of the time-aware H&E and copy-number scores: mean of the two z-scored Cox linear predictors; mean of probabilities for the binary variants (as L-LATE).

**Rules rebuilt on the new scores** (cut-off rules unchanged, thresholds from inner OOF predictions of training patients):
- **P1-new**: flag an endoscopy if max new H&E score ≥ t, t at 80/90/95% training endoscopy sensitivity.
- **R49-new**: the round-7 gate (t_low 95%, t_high 90%, middle band → top-H&E sample sequenced and called by the fusion at t_seq 80%) with the new H&E score for the bands and the new fusion in the middle band. Also mixed gates (stored H&E bands + new fusion; new bands + stored L-LATE).
- **P3-new**: any sample's fusion ≥ t at 90%.

**Reported against R49 and P1 (stored) on the same patients**: Δ non-progressor patients ever flagged (of 43), Δ progressor patients caught (of 32), Δ endoscopy specificity at matched endoscopy sensitivity (new rule's score thresholded per repeat to R49's / P1's realised endoscopy sensitivity), sample- and endoscopy-level fold-stratified AUROC, fold-stratified IPCW time-dependent AUROC at 1/3/5 years (`hf_foldstrat.py` method, study times) and fold-stratified Harrell's C-index. Paired patient bootstrap, 2,000 draws, `RandomState(0)` (rv8 `pdraws`). Apparent numbers (thresholds set on the evaluated patients) are labelled optimistic.

**Files.** Scripts `scripts/paper_plan/ex_e4_*`; aggregates `results/paper_final/explore_E4/`; figures `paper/figures_explore_E4/` (local); row-level `killcoyne_mm/explore_E4/` on the cluster; Slurm prefix `exe4`.

---

## Results

Rendered by `scripts/paper_plan/ex_e4_render.py` from `results/paper_final/explore_E4/`. Exploratory: about 20 score schemes × 8 rules were tried on 75 patients. Intervals are not adjusted for that search.

### Summary

- **Training for time did not reduce false flags.** No time-aware score, used on its own or inside the R49 gate, flagged fewer non-progressor patients than the same rule built on the stored binary scores without losing progressors. The best clean comparison was the stored gate bands with a stored + 3-year-horizon ensemble fusion in the middle band, at the t_low 90 / t_high 95 cell: −1.1 [−2.7, +0.5] non-progressor patients flagged and −0.2 caught against the same cell on stored scores. Against R49 that row is −3.1 [−5.1, −1.2], but −2.0 of the −3.1 is the cut-off change alone: the stored scores at that cell give 29.8 flagged.
- **Cox models discriminate worse than the binary models.** With extended follow-up, H&E sample AUROC was 0.761 against 0.847 (Δ −0.085 [−0.118, −0.052]) and the fusion was 0.806 against 0.889. The C-index was also lower (fusion, extended follow-up: 0.774 against 0.832). The R49 gate rebuilt on Cox scores flagged 38.0 non-progressors (+6.2 [+3.0, +9.7]). Censoring non-progressors at the last sequenced endoscopy (study follow-up) was worse still (H&E AUROC 0.653). Training on pre-event samples only, without the at/after-event samples, did not help (0.740). Our reading: in the partial likelihood, a progressor's early samples are controls for other progressors' earlier events. The model therefore learns "close to HGD", not "will progress". The binary label holds a stable progressor field effect, and that field effect is what catches patients years ahead.
- **Horizon models trade overall ranking for short-term ranking.** The 3-year binary fusion had a higher time-dependent AUROC at 3 and 5 years (+0.028 at both; 95% CIs [−0.004, +0.069] and [−0.004, +0.078]) but a lower overall AUROC (−0.029 [−0.061, −0.003]). Its gate flagged more non-progressors (+3.7 [+0.7, +6.9] against R49).
- **Certainty weighting barely changes the stored model** (AUROC +0.002, gate +1.4 [+0.1, +2.9] flagged, +0.5 caught). Stronger weights were slightly worse.
- **Averaging stored and horizon models helps time-dependent discrimination a little.** The stored + 3-year ensemble fusion raised time-dependent AUROC at 3 years to 0.853 (+0.021 [+0.004, +0.042]) and at 5 years to 0.844 (+0.022 [+0.003, +0.051]), and the study C-index to 0.815 (+0.015 [+0.002, +0.030]), with unchanged AUROC (−0.002). This is the only nominally positive discrimination result. At R49's cut-offs it does not translate into fewer flags (+0.8 [−0.9, +2.6]).
- **No gain at matched sensitivity.** At R49's realised endoscopy sensitivity, no time-aware H&E or fusion score had higher endoscopy specificity than the stored score (best: strongly weighted ensemble H&E +0.005 [−0.043, +0.054]).
- **Memory rule (coordinator request).** Round 9's EW memory of the R49-aligned gate score was re-run on the time-aware probability scores. With the stored + 3-year ensemble, both bands and the fusion change: 21.7 non-progressors flagged (−10.1 [−13.8, −6.5] against R49; −1.9 [−3.8, −0.3] against the same memory rule on stored scores), but 30.2 caught (−0.9 [−2.1, +0.1] against R49; −0.5 [−1.4, +0.2] against stored memory). That is a move along the trade-off curve, not a clear improvement. With only the middle-band fusion replaced: 22.8 flagged / 30.5 caught (−0.8 [−1.7, +0.1] / −0.2 against stored memory). Weighted scores inside memory are no better than stored (+0.5 to +1.3).
- **Apparent (optimistic)** numbers tell the same story: H&E alone at 90% endoscopy sensitivity set on the evaluated patients flags 36.8 (stored), 37.5 (weighted, ensemble), 40.1 (Cox) and 42.1 (3-year horizon) non-progressor patients.

### Implementation notes

- Time axis (`ex_e4_prep.py`): exact dates (`pre_event_cohort.Date`). Progressor event = round 8's reference date (first HGD/IMC endoscopy). The 105 at/after-event progressor training samples (and those of the 5 patients with no pre-event sample) get 0.01 years. Non-progressor extended follow-up uses the linkage, tables and 14-day rule of data2.md B2 (`r2_main.py`): latest pathology report or endoscopy after the last sequenced endoscopy, stopped before any later HGD+ report or HGD-register entry (<5 patients). The extension reproduces B2: 36 of 43 extended, median 7.0 years added.
- Fits (`ex_e4_fit.R`): set C (676 samples) under the stored outer folds (asserted equal) and inner folds. Cox λ = minimum of the grouped-CV partial-likelihood deviance (Verweij–van Houwelingen; Breslow ties; 10 shuffles outer, 1 inner); score = linear predictor z-scored on that model's training rows. Binary kinds use the stored class-error rule (weighted class error for the weighted kinds). Kinds `coxp` (pre-event training samples only) and `wt2` (P weight 1 / 0.5 / 0.25 at ≤ 5 / 5–8 / > 8 years; NP clip(follow-up / 5, 0.25, 2)), the ensembles (`ens_*`: mean of the stored and the time-aware model per modality) and the middle-band-only variants (`stored+*late`) were **added after the first results**.
- Combining scales (`ex_e4_eval.py` `build`): probabilities only → mean of probabilities (as the stored L-LATE). If any Cox component is present, binary components are put on the logit scale and z-scored per (repeat, fold) on that fold's inner OOF values, then averaged.
- Rules: P1-new and P3-new with round 8's `thr_arr`; R49-new = `tb_common.triage` + `r49_calls` on the new scores at four cut-off cells (the R49 cell 95/90 and 90/90, 95/95, 90/95). 'Same rule, stored scores' builds the identical cell on the stored scores, paired on the same draws. The `stored` scheme is a control: it reproduces R49 31.1 / 31.8 and P1 31.1 / 36.0 with every delta 0, and the stored discrimination values (L2 AUROCs, `horizon_foldstrat` time-dependent AUROCs).
- Discrimination bootstrap: `tb_common.boots_for` on pre-event samples (RandomState(0), 2,000). Rule bootstrap: rv8 `pdraws` (RandomState(0), 2,000).
- Memory (`ex_e4_memory.py`): `rv9_falseflags.py` executed unchanged up to its merge task. Families A1 gate-aligned EW, gate-aligned threshold-only and H&E EW, 'np' selection. The stored run reproduces round 9 (EW gate 30.7 / 23.6; threshold-only 30.7 / 29.4; H&E EW 31.2 / 32.1).
- Cluster: campaigns `exe4` (200 fits), `exe4b` (80), `exe4e3` (20 evaluations), `exe4m` (6 memory runs), epyc only. Row-level outputs (survival times, fits) stay under `killcoyne_mm/explore_E4/`. Figures (local): `paper/figures_explore_E4/e4_rules_vs_r49.png`, `e4_spec_matched.png`, `e4_discrimination.png`.

### Time axis

- Progressor pre-event samples: years to event median 2.5 (IQR 1.5–5.0); 16 samples > 8 years before the event (down-weighted in the weighted model). The 105 at/after-event progressor samples of the training set get 0.01 years.
- Non-progressor samples, study follow-up (to the last sequenced endoscopy): median 2.4 years (IQR 0.7–5.0); extended with the Barrett's database: median 10.6 (IQR 6.7–15.0).
- Non-progressor patients linked 43 of 43; follow-up extended for 36 (median 7.0 years added per patient, as data2.md B2); stopped before a later HGD+ record: <5.
- Horizon training sets: non-progressor samples with ≥ 3 / ≥ 5 years extended follow-up 352 / 326 (study follow-up only: 186 / 104); progressor samples within 3 / 5 years of the event (incl. at/after-event) 198 / 228.

Control: the evaluation code run on the stored scores reproduces R49 (31.1 caught / 31.8 non-progressors flagged) and P1 90% (31.1 / 36.0); reproduced: yes. All stored-control deltas are 0.

### Ranked results against R49 and P1 (held-out patients, thresholds from training patients)

Every rule, every scheme. Caught = progressor patients flagged at ≥ 1 pre-event endoscopy (of 32); NP flagged = non-progressor patients ever flagged (of 43). Δ = rule − reference with paired patient-bootstrap 95% CI (2,000 draws, `RandomState(0)`). Sorted: rules losing > 0.5 progressor patients against R49 last, then by Δ NP flagged against R49. R49 = 31.1 caught / 31.8 flagged, endoscopy 0.907 / 0.560, 1.94 samples sequenced per patient; P1 90% = 31.1 / 36.0, 0.898 / 0.524.

| # | Scheme | Rule | Caught | NP flagged | Endo sens / spec | Seq / patient | Δ NP flagged vs R49 | Δ caught vs R49 | Δ NP flagged vs P1 | Δ caught vs P1 | Δ NP flagged vs same rule, stored scores | Δ caught vs same rule, stored scores |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | stored bands, stored + 3-year ensemble fusion | R49-new t_low 90/t_high 95 | 30.7 | 28.7 | 0.856 / 0.666 | 1.90 | -3.1 [-5.1, -1.2] | -0.4 [-1.3, +0.2] | -7.3 [-11.0, -3.9] | -0.4 [-2.2, +1.4] | -1.1 [-2.7, +0.5] | -0.2 [-1.2, +0.5] |
| 2 | stored + 3-year ensemble | R49-new t_low 90/t_high 95 | 30.8 | 29.0 | 0.859 / 0.670 | 1.96 | -2.8 [-4.8, -1.0] | -0.3 [-1.3, +0.4] | -7.0 [-10.6, -3.7] | -0.3 [-2.1, +1.5] | -0.8 [-2.5, +0.9] | -0.1 [-1.1, +0.7] |
| 3 | weighted H&E + stored copy number | R49-new t_low 90/t_high 95 | 30.9 | 29.9 | 0.861 / 0.632 | 2.06 | -1.9 [-3.2, -0.7] | -0.2 [-0.9, +0.3] | -6.1 [-10.0, -2.3] | -0.2 [-2.0, +1.8] | +0.1 [-1.0, +1.6] | 0.0 [-0.8, +0.6] |
| 4 | stored + strongly weighted ensemble | R49-new t_low 90/t_high 95 | 31.0 | 30.2 | 0.868 / 0.645 | 1.96 | -1.6 [-2.7, -0.6] | -0.1 [-0.6, +0.3] | -5.8 [-9.3, -2.6] | -0.1 [-1.8, +1.8] | +0.4 [-0.2, +1.1] | +0.1 [-0.5, +0.6] |
| 5 | stored bands, stored + 3-year ensemble fusion | R49-new t_low 95/t_high 95 | 31.0 | 30.4 | 0.878 / 0.620 | 2.25 | -1.4 [-3.2, +0.4] | -0.1 [-0.9, +0.6] | -5.6 [-9.1, -2.5] | -0.1 [-1.7, +1.8] | -0.2 [-2.0, +1.7] | -0.1 [-0.9, +0.6] |
| 6 | certainty-weighted binary | R49-new t_low 90/t_high 95 | 31.1 | 30.5 | 0.869 / 0.629 | 2.06 | -1.3 [-2.7, -0.0] | 0.0 [-0.5, +0.4] | -5.5 [-8.9, -2.4] | 0.0 [-1.5, +1.9] | +0.7 [-0.6, +2.1] | +0.2 [-0.4, +0.9] |
| 7 | stored + 5-year ensemble | R49-new t_low 90/t_high 95 | 30.8 | 30.5 | 0.867 / 0.645 | 1.96 | -1.3 [-3.0, +0.4] | -0.3 [-1.2, +0.3] | -5.5 [-8.9, -2.4] | -0.3 [-2.2, +1.7] | +0.7 [-0.8, +2.4] | -0.1 [-1.1, +0.6] |
| 8 | stored + 3-year ensemble | R49-new t_low 95/t_high 95 | 31.0 | 30.6 | 0.881 / 0.627 | 2.31 | -1.2 [-3.3, +0.8] | -0.1 [-0.9, +0.4] | -5.4 [-8.7, -2.1] | -0.1 [-1.8, +1.8] | 0.0 [-2.1, +2.2] | -0.1 [-0.9, +0.4] |
| 9 | stored + 3-year ensemble | R49-new t_low 90/t_high 90 | 31.1 | 30.8 | 0.876 / 0.634 | 1.65 | -1.0 [-2.8, +0.9] | 0.0 [-0.6, +0.6] | -5.2 [-8.4, -2.1] | 0.0 [-1.4, +1.6] | -0.2 [-2.0, +1.8] | +0.1 [-0.5, +0.7] |
| 10 | weighted H&E + stored copy number | R49-new t_low 95/t_high 95 | 31.0 | 30.9 | 0.889 / 0.584 | 2.42 | -0.9 [-1.9, +0.1] | -0.1 [-0.6, +0.3] | -5.1 [-8.8, -1.4] | -0.1 [-1.8, +1.8] | +0.3 [-0.8, +1.6] | -0.1 [-0.6, +0.3] |
| 11 | stored + strongly weighted ensemble | R49-new t_low 90/t_high 90 | 31.5 | 31.0 | 0.887 / 0.613 | 1.64 | -0.8 [-1.7, 0.0] | +0.4 [0.0, +1.1] | -5.0 [-8.5, -1.9] | +0.4 [-0.7, +2.1] | 0.0 [-0.9, +1.0] | +0.5 [0.0, +1.3] |
| 12 | weighted H&E + stored copy number | R49-new t_low 90/t_high 90 | 31.2 | 31.1 | 0.885 / 0.596 | 1.69 | -0.7 [-1.8, +0.4] | +0.1 [-0.2, +0.5] | -4.9 [-8.4, -1.4] | +0.1 [-1.3, +1.9] | +0.1 [-1.1, +1.6] | +0.2 [-0.2, +0.6] |
| 13 | stored + strongly weighted ensemble | R49-new t_low 95/t_high 95 | 31.4 | 31.1 | 0.902 / 0.597 | 2.31 | -0.7 [-1.6, +0.2] | +0.3 [0.0, +0.8] | -4.9 [-8.4, -1.5] | +0.3 [-0.9, +2.0] | +0.5 [-0.4, +1.5] | +0.3 [0.0, +0.8] |
| 14 | stored + 5-year ensemble | R49-new t_low 95/t_high 95 | 31.0 | 31.2 | 0.889 / 0.606 | 2.27 | -0.6 [-2.1, +1.0] | -0.1 [-0.9, +0.4] | -4.8 [-8.0, -1.8] | -0.1 [-1.8, +1.8] | +0.6 [-0.9, +2.3] | -0.1 [-0.9, +0.4] |
| 15 | stored bands, stored + 3-year ensemble fusion | R49-new t_low 90/t_high 90 | 31.1 | 31.2 | 0.875 / 0.619 | 1.59 | -0.6 [-2.1, +0.9] | 0.0 [-0.7, +0.8] | -4.8 [-8.0, -1.8] | 0.0 [-1.3, +1.6] | +0.2 [-1.2, +1.8] | +0.1 [-0.5, +0.9] |
| 16 | stored H&E + Cox copy number | R49-new t_low 90/t_high 95 | 31.3 | 31.3 | 0.869 / 0.597 | 1.90 | -0.5 [-2.3, +1.4] | +0.2 [-1.0, +1.8] | -4.7 [-8.3, -1.4] | +0.2 [-1.1, +1.8] | +1.5 [-0.3, +3.4] | +0.4 [-0.9, +2.2] |
| 17 | certainty-weighted binary | R49-new t_low 95/t_high 95 | 31.4 | 31.4 | 0.899 / 0.582 | 2.42 | -0.4 [-1.4, +0.6] | +0.3 [-0.2, +1.0] | -4.6 [-7.8, -1.5] | +0.3 [-0.9, +2.0] | +0.8 [-0.3, +2.0] | +0.3 [-0.2, +1.0] |
| 18 | Cox H&E + stored copy number | R49-new t_low 90/t_high 95 | 30.8 | 31.4 | 0.868 / 0.563 | 2.71 | -0.4 [-3.6, +2.9] | -0.3 [-1.0, +0.2] | -4.6 [-8.9, -0.2] | -0.3 [-2.0, +1.6] | +1.6 [-1.9, +5.4] | -0.1 [-0.8, +0.5] |
| 19 | stored + Cox ensemble | R49-new t_low 90/t_high 95 | 30.9 | 31.4 | 0.885 / 0.601 | 2.21 | -0.4 [-2.4, +1.7] | -0.2 [-0.6, +0.2] | -4.6 [-8.4, -0.8] | -0.2 [-2.0, +1.7] | +1.6 [-0.4, +3.9] | 0.0 [-0.4, +0.4] |
| 20 | strongly weighted binary | R49-new t_low 90/t_high 95 | 31.5 | 31.5 | 0.882 / 0.607 | 2.16 | -0.3 [-2.0, +1.5] | +0.4 [-0.2, +1.4] | -4.5 [-7.5, -1.8] | +0.4 [-0.8, +2.1] | +1.7 [0.0, +3.7] | +0.6 [-0.1, +1.8] |
| 21 | certainty-weighted binary | R49-new t_low 90/t_high 90 | 31.5 | 31.6 | 0.885 / 0.591 | 1.69 | -0.2 [-1.4, +0.9] | +0.4 [0.0, +1.1] | -4.4 [-7.5, -1.5] | +0.4 [-0.7, +2.1] | +0.6 [-0.6, +1.9] | +0.5 [0.0, +1.3] |
| 22 | weighted H&E + stored copy number | P3-new 90% | 31.0 | 31.7 | 0.912 / 0.540 | 7.61 | -0.1 [-1.7, +1.8] | -0.1 [-0.6, +0.3] | -4.3 [-8.2, +0.1] | -0.1 [-1.8, +1.8] | -0.1 [-1.1, +1.1] | -0.2 [-0.7, 0.0] |
| 23 | stored + 5-year ensemble | P3-new 90% | 31.1 | 31.8 | 0.908 / 0.565 | 7.61 | 0.0 [-1.7, +1.9] | 0.0 [-0.8, +0.7] | -4.2 [-7.7, -0.5] | 0.0 [-1.6, +1.8] | 0.0 [-1.5, +1.6] | -0.1 [-0.9, +0.6] |
| 24 | stored + strongly weighted ensemble | P3-new 90% | 31.1 | 31.8 | 0.902 / 0.564 | 7.61 | 0.0 [-1.5, +1.9] | 0.0 [-0.5, +0.4] | -4.2 [-8.0, -0.3] | 0.0 [-1.5, +1.9] | 0.0 [-0.9, +1.1] | -0.1 [-0.6, +0.3] |
| 25 | stored + 5-year ensemble | R49-new t_low 90/t_high 90 | 31.2 | 32.0 | 0.887 / 0.607 | 1.62 | +0.2 [-1.4, +1.9] | +0.1 [-0.5, +0.7] | -4.0 [-7.0, -1.2] | +0.1 [-1.4, +1.9] | +1.0 [-0.6, +2.9] | +0.2 [-0.4, +0.9] |
| 26 | stored bands, 3-year fusion | R49-new t_low 90/t_high 95 | 30.7 | 32.1 | 0.847 / 0.628 | 1.90 | +0.3 [-2.0, +3.0] | -0.4 [-2.0, +1.0] | -3.9 [-6.8, -1.2] | -0.4 [-2.6, +1.5] | +2.3 [-0.1, +5.1] | -0.2 [-1.8, +1.4] |
| 27 | certainty-weighted binary | P3-new 90% | 31.5 | 32.2 | 0.908 / 0.549 | 7.61 | +0.4 [-1.2, +2.3] | +0.4 [-0.2, +1.4] | -3.8 [-7.2, -0.1] | +0.4 [-0.8, +2.1] | +0.4 [-0.8, +1.7] | +0.3 [-0.3, +1.3] |
| 28 | stored bands, 5-year fusion | R49-new t_low 90/t_high 95 | 30.7 | 32.2 | 0.863 / 0.623 | 1.90 | +0.4 [-1.9, +3.0] | -0.4 [-1.6, +0.4] | -3.8 [-6.9, -0.9] | -0.4 [-2.4, +1.4] | +2.4 [0.0, +5.2] | -0.2 [-1.4, +0.7] |
| 29 | stored bands, stored + 3-year ensemble fusion | R49-new t_low 95/t_high 90 | 31.3 | 32.3 | 0.897 / 0.575 | 1.94 | +0.5 [-0.9, +2.1] | +0.2 [-0.5, +1.2] | -3.7 [-6.7, -1.0] | +0.2 [-1.2, +2.0] | +0.5 [-0.9, +2.1] | +0.2 [-0.5, +1.2] |
| 30 | weighted H&E + stored copy number | R49-new t_low 95/t_high 90 | 31.4 | 32.4 | 0.912 / 0.543 | 2.06 | +0.6 [-0.4, +1.7] | +0.3 [0.0, +0.8] | -3.6 [-6.9, -0.2] | +0.3 [-0.9, +2.0] | +0.6 [-0.4, +1.7] | +0.3 [0.0, +0.8] |
| 31 | stored + Cox ensemble | R49-new t_low 90/t_high 90 | 31.2 | 32.4 | 0.902 / 0.574 | 1.90 | +0.6 [-1.3, +2.8] | +0.1 [0.0, +0.3] | -3.6 [-7.3, +0.3] | +0.1 [-1.4, +2.0] | +1.4 [-0.6, +3.8] | +0.2 [0.0, +0.5] |
| 32 | stored + strongly weighted ensemble | R49-new t_low 95/t_high 90 | 31.5 | 32.4 | 0.919 / 0.563 | 1.99 | +0.6 [-0.3, +1.6] | +0.4 [0.0, +1.1] | -3.6 [-6.6, -0.7] | +0.4 [-0.7, +2.1] | +0.6 [-0.3, +1.6] | +0.4 [0.0, +1.1] |
| 33 | 5-year horizon binary | R49-new t_low 90/t_high 95 | 30.6 | 32.5 | 0.870 / 0.593 | 2.17 | +0.7 [-2.3, +3.9] | -0.5 [-1.9, +0.3] | -3.5 [-6.5, -0.6] | -0.5 [-2.8, +1.6] | +2.7 [-0.4, +6.3] | -0.3 [-1.8, +0.7] |
| 34 | strongly weighted binary | R49-new t_low 95/t_high 95 | 31.4 | 32.5 | 0.902 / 0.569 | 2.46 | +0.7 [-1.0, +2.5] | +0.3 [-0.2, +1.0] | -3.5 [-6.3, -0.8] | +0.3 [-0.9, +2.0] | +1.9 [+0.1, +4.0] | +0.3 [-0.2, +1.0] |
| 35 | stored + Cox ensemble | R49-new t_low 95/t_high 95 | 31.3 | 32.5 | 0.911 / 0.544 | 2.56 | +0.7 [-1.3, +3.0] | +0.2 [0.0, +0.5] | -3.5 [-7.2, +0.4] | +0.2 [-1.3, +2.0] | +1.9 [-0.2, +4.4] | +0.2 [0.0, +0.5] |
| 36 | stored + 3-year ensemble | P3-new 90% | 31.2 | 32.6 | 0.901 / 0.557 | 7.61 | +0.8 [-1.3, +3.1] | +0.1 [-0.8, +1.0] | -3.4 [-6.8, +0.3] | +0.1 [-1.5, +1.9] | +0.8 [-1.0, +2.8] | 0.0 [-0.8, +0.9] |
| 37 | stored + 3-year ensemble | R49-new t_low 95/t_high 90 | 31.4 | 32.6 | 0.901 / 0.581 | 2.00 | +0.8 [-0.9, +2.6] | +0.3 [-0.2, +1.0] | -3.4 [-6.0, -0.6] | +0.3 [-0.9, +2.0] | +0.8 [-0.9, +2.6] | +0.3 [-0.2, +1.0] |
| 38 | stored bands, stored + 3-year ensemble fusion | P3-new 90% | 31.2 | 32.6 | 0.901 / 0.557 | 7.61 | +0.8 [-1.3, +3.1] | +0.1 [-0.8, +1.0] | -3.4 [-6.8, +0.3] | +0.1 [-1.5, +1.9] | +0.8 [-1.0, +2.8] | 0.0 [-0.8, +0.9] |
| 39 | stored + 5-year ensemble | R49-new t_low 95/t_high 90 | 31.3 | 32.7 | 0.910 / 0.566 | 1.93 | +0.9 [-0.6, +2.5] | +0.2 [-0.5, +1.0] | -3.3 [-5.9, -0.7] | +0.2 [-1.2, +1.9] | +0.9 [-0.6, +2.5] | +0.2 [-0.5, +1.0] |
| 40 | Cox H&E + stored copy number | R49-new t_low 90/t_high 90 | 30.9 | 32.8 | 0.881 / 0.538 | 2.32 | +1.0 [-2.0, +4.3] | -0.2 [-0.7, +0.2] | -3.2 [-7.2, +0.8] | -0.2 [-1.9, +1.7] | +1.8 [-1.4, +5.3] | -0.1 [-0.7, +0.4] |
| 41 | stored H&E + Cox copy number | R49-new t_low 90/t_high 90 | 31.7 | 32.8 | 0.886 / 0.558 | 1.59 | +1.0 [-0.9, +2.9] | +0.6 [-0.4, +2.1] | -3.2 [-6.5, -0.1] | +0.6 [-0.3, +2.0] | +1.8 [-0.0, +3.9] | +0.7 [-0.2, +2.2] |
| 42 | stored bands, 3-year fusion | R49-new t_low 95/t_high 95 | 30.8 | 32.8 | 0.865 / 0.595 | 2.25 | +1.0 [-1.4, +3.9] | -0.3 [-1.8, +1.1] | -3.2 [-5.8, -0.7] | -0.3 [-2.6, +1.8] | +2.2 [-0.4, +5.3] | -0.3 [-1.8, +1.1] |
| 43 | stored bands, 5-year fusion | R49-new t_low 95/t_high 95 | 30.9 | 32.8 | 0.890 / 0.584 | 2.25 | +1.0 [-1.4, +3.8] | -0.2 [-1.2, +0.4] | -3.2 [-6.2, -0.3] | -0.2 [-2.1, +1.8] | +2.2 [-0.4, +5.2] | -0.2 [-1.2, +0.4] |
| 44 | Cox H&E + stored copy number | R49-new t_low 95/t_high 95 | 31.0 | 32.9 | 0.893 / 0.511 | 3.01 | +1.1 [-1.9, +4.3] | -0.1 [-0.5, +0.2] | -3.1 [-7.3, +1.1] | -0.1 [-1.7, +1.8] | +2.3 [-0.9, +5.7] | -0.1 [-0.5, +0.2] |
| 45 | 3-year horizon binary | R49-new t_low 90/t_high 95 | 30.6 | 33.0 | 0.803 / 0.637 | 1.95 | +1.2 [-1.9, +4.5] | -0.5 [-2.5, +1.1] | -3.0 [-5.8, -0.1] | -0.5 [-3.1, +1.5] | +3.2 [-0.1, +6.7] | -0.3 [-2.4, +1.5] |
| 46 | strongly weighted binary | R49-new t_low 90/t_high 90 | 31.5 | 33.0 | 0.893 / 0.575 | 1.77 | +1.2 [-0.4, +3.0] | +0.4 [-0.2, +1.4] | -3.0 [-5.5, -0.6] | +0.4 [-0.8, +2.1] | +2.0 [+0.3, +4.0] | +0.5 [-0.1, +1.5] |
| 47 | Cox (pre-event) H&E + stored copy number | R49-new t_low 95/t_high 95 | 30.7 | 33.1 | 0.894 / 0.525 | 3.02 | +1.3 [-1.5, +4.2] | -0.4 [-1.1, +0.2] | -2.9 [-7.1, +1.4] | -0.4 [-2.3, +1.4] | +2.5 [-0.6, +5.7] | -0.4 [-1.1, +0.2] |
| 48 | certainty-weighted binary | R49-new t_low 95/t_high 90 | 31.6 | 33.2 | 0.915 / 0.538 | 2.06 | +1.4 [+0.1, +2.9] | +0.5 [0.0, +1.4] | -2.8 [-5.3, -0.4] | +0.5 [-0.6, +2.2] | +1.4 [+0.1, +2.9] | +0.5 [0.0, +1.4] |
| 49 | stored H&E + Cox copy number | R49-new t_low 95/t_high 95 | 31.7 | 33.2 | 0.901 / 0.542 | 2.25 | +1.4 [-0.6, +3.6] | +0.6 [-0.2, +2.1] | -2.8 [-6.2, +0.6] | +0.6 [-0.5, +2.3] | +2.6 [+0.4, +5.0] | +0.6 [-0.2, +2.1] |
| 50 | stored bands, 5-year fusion | R49-new t_low 90/t_high 90 | 30.9 | 33.2 | 0.881 / 0.592 | 1.59 | +1.4 [-0.8, +4.0] | -0.2 [-1.0, +0.4] | -2.8 [-5.5, 0.0] | -0.2 [-1.8, +1.5] | +2.2 [-0.2, +5.0] | -0.1 [-0.9, +0.4] |
| 51 | 5-year horizon binary | R49-new t_low 95/t_high 95 | 30.8 | 33.7 | 0.892 / 0.554 | 2.48 | +1.9 [-0.7, +4.8] | -0.3 [-1.5, +0.4] | -2.3 [-5.1, +0.6] | -0.3 [-2.4, +1.7] | +3.1 [+0.3, +6.4] | -0.3 [-1.5, +0.4] |
| 52 | stored bands, 3-year fusion | R49-new t_low 90/t_high 90 | 31.0 | 33.7 | 0.863 / 0.592 | 1.59 | +1.9 [-0.1, +4.2] | -0.1 [-1.2, +1.1] | -2.3 [-4.6, 0.0] | -0.1 [-1.9, +1.6] | +2.7 [+0.5, +5.3] | 0.0 [-1.1, +1.2] |
| 53 | stored + Cox ensemble | P3-new 90% | 31.5 | 33.9 | 0.922 / 0.492 | 7.61 | +2.1 [-0.2, +4.9] | +0.4 [0.0, +0.9] | -2.1 [-5.8, +1.6] | +0.4 [-0.7, +2.1] | +2.1 [+0.1, +4.5] | +0.3 [0.0, +0.8] |
| 54 | 3-year horizon binary | R49-new t_low 95/t_high 95 | 30.6 | 34.0 | 0.844 / 0.592 | 2.33 | +2.2 [-0.8, +5.5] | -0.5 [-2.5, +1.1] | -2.0 [-4.4, +0.7] | -0.5 [-3.1, +1.5] | +3.4 [0.0, +7.0] | -0.5 [-2.5, +1.1] |
| 55 | strongly weighted binary | P3-new 90% | 31.4 | 34.0 | 0.912 / 0.521 | 7.61 | +2.2 [+0.3, +4.5] | +0.3 [-0.5, +1.3] | -2.0 [-4.9, +1.5] | +0.3 [-1.2, +2.0] | +2.2 [+0.5, +4.3] | +0.2 [-0.5, +1.2] |
| 56 | stored + Cox ensemble | R49-new t_low 95/t_high 90 | 31.4 | 34.0 | 0.926 / 0.498 | 2.25 | +2.2 [0.0, +4.7] | +0.3 [0.0, +0.7] | -2.0 [-5.8, +1.9] | +0.3 [-1.0, +2.1] | +2.2 [0.0, +4.7] | +0.3 [0.0, +0.7] |
| 57 | Cox H&E + stored copy number | P3-new 90% | 31.3 | 34.1 | 0.924 / 0.463 | 7.61 | +2.3 [-0.4, +5.4] | +0.2 [0.0, +0.5] | -1.9 [-5.6, +2.1] | +0.2 [-1.3, +2.0] | +2.3 [-0.3, +5.1] | +0.1 [0.0, +0.3] |
| 58 | Cox (pre-event) H&E + stored copy number | P3-new 90% | 30.7 | 34.1 | 0.906 / 0.492 | 7.61 | +2.3 [-0.2, +5.0] | -0.4 [-1.2, +0.2] | -1.9 [-5.7, +1.9] | -0.4 [-2.5, +1.7] | +2.3 [-0.0, +4.8] | -0.5 [-1.3, 0.0] |
| 59 | stored H&E + Cox copy number | R49-new t_low 95/t_high 90 | 31.9 | 34.2 | 0.914 / 0.508 | 1.94 | +2.4 [+0.1, +4.8] | +0.8 [0.0, +2.3] | -1.8 [-5.1, +1.7] | +0.8 [-0.2, +2.4] | +2.4 [+0.1, +4.8] | +0.8 [0.0, +2.3] |
| 60 | 3-year horizon binary | R49-new t_low 90/t_high 90 | 30.6 | 34.3 | 0.819 / 0.598 | 1.71 | +2.5 [-0.6, +5.9] | -0.5 [-2.5, +1.1] | -1.7 [-4.2, +1.2] | -0.5 [-3.1, +1.5] | +3.3 [0.0, +6.9] | -0.4 [-2.4, +1.2] |
| 61 | 5-year horizon binary | R49-new t_low 90/t_high 90 | 30.7 | 34.3 | 0.884 / 0.549 | 1.83 | +2.5 [-0.4, +5.7] | -0.4 [-1.5, +0.3] | -1.7 [-4.4, +1.1] | -0.4 [-2.5, +1.7] | +3.3 [+0.3, +6.8] | -0.3 [-1.5, +0.4] |
| 62 | Cox H&E + stored copy number | R49-new t_low 95/t_high 90 | 31.0 | 34.3 | 0.902 / 0.479 | 2.62 | +2.5 [-0.3, +5.6] | -0.1 [-0.5, +0.2] | -1.7 [-5.5, +2.2] | -0.1 [-1.7, +1.8] | +2.5 [-0.3, +5.6] | -0.1 [-0.5, +0.2] |
| 63 | strongly weighted binary | R49-new t_low 95/t_high 90 | 31.5 | 34.4 | 0.916 / 0.525 | 2.08 | +2.6 [+0.8, +4.7] | +0.4 [-0.2, +1.4] | -1.6 [-3.9, +0.7] | +0.4 [-0.8, +2.1] | +2.6 [+0.8, +4.7] | +0.4 [-0.2, +1.4] |
| 64 | stored bands, 5-year fusion | R49-new t_low 95/t_high 90 | 31.1 | 34.5 | 0.909 / 0.540 | 1.94 | +2.7 [+0.3, +5.5] | 0.0 [-0.8, +0.7] | -1.5 [-4.1, +1.2] | 0.0 [-1.6, +1.8] | +2.7 [+0.3, +5.5] | 0.0 [-0.8, +0.7] |
| 65 | Cox (pre-event) H&E + stored copy number | R49-new t_low 95/t_high 90 | 30.8 | 34.7 | 0.908 / 0.471 | 2.69 | +2.9 [0.0, +5.9] | -0.3 [-0.9, +0.2] | -1.3 [-5.6, +3.0] | -0.3 [-2.2, +1.5] | +2.9 [0.0, +5.9] | -0.3 [-0.9, +0.2] |
| 66 | Cox, pre-event samples only | R49-new t_low 95/t_high 95 | 30.8 | 35.1 | 0.902 / 0.441 | 3.02 | +3.3 [+0.5, +6.2] | -0.3 [-1.4, +0.6] | -0.9 [-4.9, +2.8] | -0.3 [-2.0, +1.2] | +4.5 [+1.4, +7.8] | -0.3 [-1.4, +0.6] |
| 67 | Cox, pre-event samples only | R49-new t_low 90/t_high 90 | 30.7 | 35.2 | 0.894 / 0.459 | 2.40 | +3.4 [+0.3, +6.5] | -0.4 [-1.6, +0.5] | -0.8 [-4.9, +3.0] | -0.4 [-1.7, +0.7] | +4.2 [+1.0, +7.6] | -0.3 [-1.3, +0.5] |
| 68 | stored H&E + Cox copy number | P3-new 90% | 31.7 | 35.2 | 0.926 / 0.467 | 7.61 | +3.4 [+0.8, +6.2] | +0.6 [-0.2, +2.1] | -0.8 [-3.9, +2.5] | +0.6 [-0.5, +2.3] | +3.4 [+0.9, +6.0] | +0.5 [-0.4, +2.0] |
| 69 | stored bands, 3-year fusion | R49-new t_low 95/t_high 90 | 31.1 | 35.2 | 0.880 / 0.546 | 1.94 | +3.4 [+1.0, +6.3] | 0.0 [-1.1, +1.2] | -0.8 [-3.0, +1.3] | 0.0 [-1.9, +1.9] | +3.4 [+1.0, +6.3] | 0.0 [-1.1, +1.2] |
| 70 | 5-year horizon binary | P3-new 90% | 31.0 | 35.4 | 0.914 / 0.500 | 7.61 | +3.6 [+1.0, +6.5] | -0.1 [-1.4, +1.0] | -0.6 [-3.3, +2.5] | -0.1 [-2.2, +1.9] | +3.6 [+1.1, +6.5] | -0.2 [-1.5, +0.8] |
| 71 | stored bands, 5-year fusion | P3-new 90% | 31.0 | 35.4 | 0.914 / 0.500 | 7.61 | +3.6 [+1.0, +6.5] | -0.1 [-1.4, +1.0] | -0.6 [-3.3, +2.5] | -0.1 [-2.2, +1.9] | +3.6 [+1.1, +6.5] | -0.2 [-1.5, +0.8] |
| 72 | 3-year horizon binary | R49-new t_low 95/t_high 90 | 30.7 | 35.5 | 0.861 / 0.545 | 2.08 | +3.7 [+0.7, +6.9] | -0.4 [-2.4, +1.2] | -0.5 [-2.8, +2.2] | -0.4 [-3.1, +1.8] | +3.7 [+0.7, +6.9] | -0.4 [-2.4, +1.2] |
| 73 | 5-year horizon binary | R49-new t_low 95/t_high 90 | 31.0 | 35.5 | 0.903 / 0.509 | 2.14 | +3.7 [+1.0, +6.8] | -0.1 [-0.9, +0.4] | -0.5 [-2.9, +2.2] | -0.1 [-1.8, +1.8] | +3.7 [+1.0, +6.8] | -0.1 [-0.9, +0.4] |
| 74 | Cox, pre-event samples only | P3-new 90% | 31.3 | 35.6 | 0.910 / 0.415 | 7.61 | +3.8 [+1.1, +6.7] | +0.2 [-0.6, +1.2] | -0.4 [-3.8, +3.1] | +0.2 [-1.2, +1.7] | +3.8 [+1.2, +6.5] | +0.1 [-0.7, +1.1] |
| 75 | Cox, pre-event samples only | R49-new t_low 95/t_high 90 | 31.1 | 35.7 | 0.916 / 0.411 | 2.69 | +3.9 [+1.0, +7.0] | 0.0 [-0.6, +0.6] | -0.3 [-4.4, +3.5] | 0.0 [-1.1, +1.4] | +3.9 [+1.0, +7.0] | 0.0 [-0.6, +0.6] |
| 76 | 5-year H&E + stored copy number | P3-new 90% | 30.6 | 35.7 | 0.914 / 0.493 | 7.61 | +3.9 [+1.1, +7.0] | -0.5 [-1.9, +0.3] | -0.3 [-3.2, +3.0] | -0.5 [-2.8, +1.6] | +3.9 [+1.2, +7.1] | -0.6 [-2.0, 0.0] |
| 77 | Cox, extended follow-up | R49-new t_low 90/t_high 95 | 31.5 | 35.9 | 0.857 / 0.483 | 2.71 | +4.1 [+0.9, +7.5] | +0.4 [-0.2, +1.4] | -0.1 [-3.5, +3.5] | +0.4 [-0.7, +2.1] | +6.1 [+2.6, +9.9] | +0.6 [-0.1, +1.8] |
| 78 | stored H&E + Cox copy number | P1-new 90% | 31.1 | 36.0 | 0.898 / 0.524 | 0.00 | +4.2 [+1.2, +7.4] | 0.0 [-1.9, +1.5] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| 79 | stored bands, 3-year fusion | P1-new 90% | 31.1 | 36.0 | 0.898 / 0.524 | 0.00 | +4.2 [+1.2, +7.4] | 0.0 [-1.9, +1.5] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| 80 | stored bands, 5-year fusion | P1-new 90% | 31.1 | 36.0 | 0.898 / 0.524 | 0.00 | +4.2 [+1.2, +7.4] | 0.0 [-1.9, +1.5] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| 81 | stored bands, stored + 3-year ensemble fusion | P1-new 90% | 31.1 | 36.0 | 0.898 / 0.524 | 0.00 | +4.2 [+1.2, +7.4] | 0.0 [-1.9, +1.5] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| 82 | Cox, extended follow-up | R49-new t_low 90/t_high 90 | 31.6 | 36.8 | 0.875 / 0.455 | 2.32 | +5.0 [+2.1, +8.3] | +0.5 [0.0, +1.4] | +0.8 [-2.4, +4.3] | +0.5 [-0.6, +2.2] | +5.8 [+2.7, +9.4] | +0.6 [0.0, +1.6] |
| 83 | stored + 3-year ensemble | P1-new 90% | 31.4 | 36.8 | 0.893 / 0.514 | 0.00 | +5.0 [+1.8, +8.5] | +0.3 [-1.0, +1.7] | +0.8 [-0.1, +1.9] | +0.3 [-0.2, +1.0] | +0.8 [-0.1, +1.9] | +0.3 [-0.2, +1.0] |
| 84 | stored + strongly weighted ensemble | P1-new 90% | 31.1 | 37.0 | 0.903 / 0.503 | 0.00 | +5.2 [+1.8, +8.8] | 0.0 [-2.2, +1.8] | +1.0 [+0.1, +2.1] | 0.0 [-0.3, +0.3] | +1.0 [+0.1, +2.1] | 0.0 [-0.3, +0.3] |
| 85 | Cox, extended follow-up | R49-new t_low 95/t_high 95 | 31.6 | 37.2 | 0.875 / 0.430 | 3.01 | +5.4 [+2.3, +8.8] | +0.5 [0.0, +1.4] | +1.2 [-2.2, +4.8] | +0.5 [-0.6, +2.2] | +6.6 [+3.2, +10.2] | +0.5 [0.0, +1.4] |
| 86 | 3-year horizon binary | P3-new 90% | 30.8 | 37.2 | 0.891 / 0.483 | 7.61 | +5.4 [+2.3, +8.8] | -0.3 [-2.4, +1.5] | +1.2 [-1.4, +4.6] | -0.3 [-2.9, +1.9] | +5.4 [+2.3, +8.8] | -0.4 [-2.5, +1.3] |
| 87 | stored bands, 3-year fusion | P3-new 90% | 30.8 | 37.2 | 0.891 / 0.483 | 7.61 | +5.4 [+2.3, +8.8] | -0.3 [-2.4, +1.5] | +1.2 [-1.4, +4.6] | -0.3 [-2.9, +1.9] | +5.4 [+2.3, +8.8] | -0.4 [-2.5, +1.3] |
| 88 | stored + 5-year ensemble | P1-new 90% | 30.9 | 37.4 | 0.898 / 0.497 | 0.00 | +5.6 [+2.4, +9.1] | -0.2 [-1.7, +0.8] | +1.4 [+0.4, +2.7] | -0.2 [-0.7, +0.2] | +1.4 [+0.4, +2.7] | -0.2 [-0.7, +0.2] |
| 89 | certainty-weighted binary | P1-new 90% | 31.2 | 37.7 | 0.906 / 0.482 | 0.00 | +5.9 [+2.8, +9.5] | +0.1 [-1.9, +2.1] | +1.7 [+0.4, +3.3] | +0.1 [-0.3, +0.6] | +1.7 [+0.4, +3.3] | +0.1 [-0.3, +0.6] |
| 90 | weighted H&E + stored copy number | P1-new 90% | 31.2 | 37.7 | 0.906 / 0.482 | 0.00 | +5.9 [+2.8, +9.5] | +0.1 [-1.9, +2.1] | +1.7 [+0.4, +3.3] | +0.1 [-0.3, +0.6] | +1.7 [+0.4, +3.3] | +0.1 [-0.3, +0.6] |
| 91 | Cox, extended follow-up | R49-new t_low 95/t_high 90 | 31.6 | 38.0 | 0.895 / 0.390 | 2.62 | +6.2 [+3.0, +9.7] | +0.5 [0.0, +1.4] | +2.0 [-1.5, +5.7] | +0.5 [-0.6, +2.2] | +6.2 [+3.0, +9.7] | +0.5 [0.0, +1.4] |
| 92 | stored + Cox ensemble | P1-new 90% | 30.7 | 38.9 | 0.900 / 0.449 | 0.00 | +7.1 [+3.7, +10.9] | -0.4 [-2.1, +0.7] | +2.9 [+0.8, +5.5] | -0.4 [-1.1, 0.0] | +2.9 [+0.8, +5.5] | -0.4 [-1.1, 0.0] |
| 93 | stored + 3-year ensemble | P1-new 95% | 31.8 | 39.0 | 0.943 / 0.403 | 0.00 | +7.2 [+3.9, +10.8] | +0.7 [-0.1, +1.9] | +3.0 [+1.3, +5.2] | +0.7 [0.0, +2.1] | -0.3 [-1.8, +1.0] | -0.1 [-0.3, 0.0] |
| 94 | Cox, extended follow-up | P3-new 90% | 31.8 | 39.1 | 0.909 / 0.326 | 7.61 | +7.3 [+4.1, +10.8] | +0.7 [0.0, +1.9] | +3.1 [-0.1, +6.7] | +0.7 [-0.2, +2.3] | +7.3 [+4.1, +10.7] | +0.6 [0.0, +1.8] |
| 95 | 3-year horizon binary | P1-new 90% | 31.2 | 39.3 | 0.830 / 0.421 | 0.00 | +7.5 [+3.9, +11.3] | +0.1 [-1.4, +1.7] | +3.3 [+1.2, +6.1] | +0.1 [-1.9, +1.9] | +3.3 [+1.2, +6.1] | +0.1 [-1.9, +1.9] |
| 96 | strongly weighted binary | P1-new 90% | 31.7 | 39.3 | 0.910 / 0.442 | 0.00 | +7.5 [+4.2, +11.3] | +0.6 [-0.6, +2.2] | +3.3 [+1.4, +5.8] | +0.6 [0.0, +1.6] | +3.3 [+1.4, +5.8] | +0.6 [0.0, +1.6] |
| 97 | stored H&E + Cox copy number | P1-new 95% | 31.9 | 39.3 | 0.942 / 0.370 | 0.00 | +7.5 [+4.1, +11.2] | +0.8 [-0.1, +2.3] | +3.3 [+1.4, +5.5] | +0.8 [0.0, +2.2] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| 98 | stored bands, 3-year fusion | P1-new 95% | 31.9 | 39.3 | 0.942 / 0.370 | 0.00 | +7.5 [+4.1, +11.2] | +0.8 [-0.1, +2.3] | +3.3 [+1.4, +5.5] | +0.8 [0.0, +2.2] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| 99 | stored bands, 5-year fusion | P1-new 95% | 31.9 | 39.3 | 0.942 / 0.370 | 0.00 | +7.5 [+4.1, +11.2] | +0.8 [-0.1, +2.3] | +3.3 [+1.4, +5.5] | +0.8 [0.0, +2.2] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| 100 | stored bands, stored + 3-year ensemble fusion | P1-new 95% | 31.9 | 39.3 | 0.942 / 0.370 | 0.00 | +7.5 [+4.1, +11.2] | +0.8 [-0.1, +2.3] | +3.3 [+1.4, +5.5] | +0.8 [0.0, +2.2] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| 101 | stored + strongly weighted ensemble | P1-new 95% | 31.9 | 39.6 | 0.944 / 0.382 | 0.00 | +7.8 [+4.4, +11.7] | +0.8 [-0.1, +2.3] | +3.6 [+1.7, +6.0] | +0.8 [0.0, +2.2] | +0.3 [-0.7, +1.3] | 0.0 [0.0, 0.0] |
| 102 | 5-year horizon binary | P1-new 90% | 31.0 | 40.2 | 0.883 / 0.406 | 0.00 | +8.4 [+4.9, +12.1] | -0.1 [-0.6, +0.3] | +4.2 [+1.8, +7.3] | -0.1 [-1.3, +1.3] | +4.2 [+1.8, +7.3] | -0.1 [-1.3, +1.3] |
| 103 | 5-year H&E + stored copy number | P1-new 90% | 31.0 | 40.2 | 0.883 / 0.406 | 0.00 | +8.4 [+4.9, +12.1] | -0.1 [-0.6, +0.3] | +4.2 [+1.8, +7.3] | -0.1 [-1.3, +1.3] | +4.2 [+1.8, +7.3] | -0.1 [-1.3, +1.3] |
| 104 | stored + 5-year ensemble | P1-new 95% | 31.7 | 40.3 | 0.948 / 0.372 | 0.00 | +8.5 [+5.1, +12.3] | +0.6 [-0.1, +1.6] | +4.3 [+2.0, +7.3] | +0.6 [0.0, +2.0] | +1.0 [-0.0, +2.3] | -0.2 [-0.7, 0.0] |
| 105 | Cox, extended follow-up | P1-new 90% | 31.0 | 40.4 | 0.918 / 0.316 | 0.00 | +8.6 [+4.6, +12.9] | -0.1 [-2.6, +2.0] | +4.4 [+1.6, +7.9] | -0.1 [-0.7, +0.5] | +4.4 [+1.6, +7.9] | -0.1 [-0.7, +0.5] |
| 106 | Cox, study follow-up | R49-new t_low 90/t_high 95 | 31.6 | 40.4 | 0.806 / 0.383 | 2.93 | +8.6 [+4.5, +13.2] | +0.5 [-0.1, +1.3] | +4.4 [+0.9, +8.7] | +0.5 [-0.4, +2.1] | +10.6 [+6.2, +15.6] | +0.7 [-0.1, +1.7] |
| 107 | Cox H&E + stored copy number | P1-new 90% | 31.0 | 40.4 | 0.918 / 0.316 | 0.00 | +8.6 [+4.6, +12.9] | -0.1 [-2.6, +2.0] | +4.4 [+1.6, +7.9] | -0.1 [-0.7, +0.5] | +4.4 [+1.6, +7.9] | -0.1 [-0.7, +0.5] |
| 108 | certainty-weighted binary | P1-new 95% | 31.9 | 40.5 | 0.951 / 0.343 | 0.00 | +8.7 [+5.1, +12.7] | +0.8 [-0.1, +2.2] | +4.5 [+2.2, +7.4] | +0.8 [-0.2, +2.5] | +1.2 [+0.1, +2.6] | 0.0 [-0.3, +0.3] |
| 109 | weighted H&E + stored copy number | P1-new 95% | 31.9 | 40.5 | 0.951 / 0.343 | 0.00 | +8.7 [+5.1, +12.7] | +0.8 [-0.1, +2.2] | +4.5 [+2.2, +7.4] | +0.8 [-0.2, +2.5] | +1.2 [+0.1, +2.6] | 0.0 [-0.3, +0.3] |
| 110 | stored + Cox ensemble | P1-new 95% | 31.8 | 40.5 | 0.959 / 0.320 | 0.00 | +8.7 [+4.9, +12.9] | +0.7 [0.0, +1.7] | +4.5 [+1.9, +7.8] | +0.7 [0.0, +2.3] | +1.2 [-0.3, +2.9] | -0.1 [-0.6, +0.3] |
| 111 | Cox, study follow-up | R49-new t_low 90/t_high 90 | 31.7 | 40.7 | 0.826 / 0.367 | 2.66 | +8.9 [+4.8, +13.4] | +0.6 [0.0, +1.4] | +4.7 [+1.2, +9.0] | +0.6 [-0.3, +2.2] | +9.7 [+5.4, +14.5] | +0.7 [+0.1, +1.5] |
| 112 | 3-year horizon binary | P1-new 95% | 31.6 | 40.8 | 0.893 / 0.312 | 0.00 | +9.0 [+5.3, +13.0] | +0.5 [-0.5, +2.0] | +4.8 [+2.1, +8.2] | +0.5 [-1.0, +2.3] | +1.5 [-0.2, +3.7] | -0.3 [-1.2, +0.3] |
| 113 | strongly weighted binary | P1-new 95% | 31.9 | 40.8 | 0.958 / 0.312 | 0.00 | +9.0 [+5.2, +13.2] | +0.8 [-0.1, +2.3] | +4.8 [+2.1, +8.0] | +0.8 [0.0, +2.2] | +1.5 [+0.3, +3.0] | 0.0 [0.0, 0.0] |
| 114 | Cox, study follow-up | R49-new t_low 95/t_high 95 | 31.7 | 41.1 | 0.834 / 0.354 | 3.10 | +9.3 [+5.3, +13.8] | +0.6 [0.0, +1.4] | +5.1 [+1.7, +9.3] | +0.6 [-0.3, +2.2] | +10.5 [+6.2, +15.3] | +0.6 [0.0, +1.4] |
| 115 | Cox, study follow-up | R49-new t_low 95/t_high 90 | 31.7 | 41.2 | 0.852 / 0.341 | 2.83 | +9.4 [+5.3, +13.9] | +0.6 [0.0, +1.4] | +5.2 [+1.8, +9.5] | +0.6 [-0.3, +2.2] | +9.4 [+5.3, +13.9] | +0.6 [0.0, +1.4] |
| 116 | Cox, extended follow-up | P1-new 95% | 32.0 | 41.4 | 0.972 / 0.201 | 0.00 | +9.6 [+5.6, +13.9] | +0.9 [0.0, +2.3] | +5.4 [+2.4, +9.3] | +0.9 [0.0, +2.5] | +2.1 [+0.1, +4.5] | +0.1 [0.0, +0.3] |
| 117 | Cox, pre-event samples only | P1-new 95% | 31.5 | 41.4 | 0.948 / 0.186 | 0.00 | +9.6 [+5.5, +14.0] | +0.4 [-0.9, +1.8] | +5.4 [+2.3, +9.4] | +0.4 [0.0, +1.1] | +2.1 [+0.1, +4.5] | -0.4 [-1.1, 0.0] |
| 118 | Cox H&E + stored copy number | P1-new 95% | 32.0 | 41.4 | 0.972 / 0.201 | 0.00 | +9.6 [+5.6, +13.9] | +0.9 [0.0, +2.3] | +5.4 [+2.4, +9.3] | +0.9 [0.0, +2.5] | +2.1 [+0.1, +4.5] | +0.1 [0.0, +0.3] |
| 119 | Cox (pre-event) H&E + stored copy number | P1-new 95% | 31.5 | 41.4 | 0.948 / 0.186 | 0.00 | +9.6 [+5.5, +14.0] | +0.4 [-0.9, +1.8] | +5.4 [+2.3, +9.4] | +0.4 [0.0, +1.1] | +2.1 [+0.1, +4.5] | -0.4 [-1.1, 0.0] |
| 120 | Cox, study follow-up | P1-new 80% | 31.6 | 41.5 | 0.802 / 0.324 | 0.00 | +9.7 [+5.7, +14.0] | +0.5 [-0.6, +2.0] | +5.5 [+2.5, +9.3] | +0.5 [-0.7, +2.3] | +9.9 [+5.9, +14.1] | +1.5 [-0.2, +4.0] |
| 121 | 5-year horizon binary | P1-new 95% | 31.7 | 41.7 | 0.941 / 0.289 | 0.00 | +9.9 [+6.0, +14.1] | +0.6 [0.0, +1.8] | +5.7 [+2.6, +9.6] | +0.6 [-0.4, +2.2] | +2.4 [+0.7, +4.7] | -0.2 [-0.6, +0.2] |
| 122 | 5-year H&E + stored copy number | P1-new 95% | 31.7 | 41.7 | 0.941 / 0.289 | 0.00 | +9.9 [+6.0, +14.1] | +0.6 [0.0, +1.8] | +5.7 [+2.6, +9.6] | +0.6 [-0.4, +2.2] | +2.4 [+0.7, +4.7] | -0.2 [-0.6, +0.2] |
| 123 | Cox, study follow-up | P3-new 90% | 31.9 | 42.5 | 0.901 / 0.225 | 7.61 | +10.7 [+6.4, +15.2] | +0.8 [0.0, +2.0] | +6.5 [+3.1, +10.9] | +0.8 [0.0, +2.4] | +10.7 [+6.2, +15.4] | +0.7 [0.0, +1.9] |
| 124 | Cox, study follow-up | P1-new 90% | 32.0 | 42.6 | 0.903 / 0.192 | 0.00 | +10.8 [+6.5, +15.3] | +0.9 [0.0, +2.3] | +6.6 [+3.1, +11.0] | +0.9 [0.0, +2.5] | +6.6 [+3.1, +11.0] | +0.9 [0.0, +2.5] |
| 125 | Cox, study follow-up | P1-new 95% | 32.0 | 43.0 | 0.950 / 0.125 | 0.00 | +11.2 [+6.8, +16.0] | +0.9 [0.0, +2.3] | +7.0 [+3.3, +11.6] | +0.9 [0.0, +2.5] | +3.7 [+1.3, +7.0] | +0.1 [0.0, +0.3] |
| 126 | stored H&E + Cox copy number | P1-new 80% | 30.1 | 31.6 | 0.820 / 0.659 | 0.00 | -0.2 [-2.4, +1.6] | -1.0 [-3.1, +0.1] | -4.4 [-6.6, -2.4] | -1.0 [-2.0, -0.2] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| 127 | stored bands, 3-year fusion | P1-new 80% | 30.1 | 31.6 | 0.820 / 0.659 | 0.00 | -0.2 [-2.4, +1.6] | -1.0 [-3.1, +0.1] | -4.4 [-6.6, -2.4] | -1.0 [-2.0, -0.2] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| 128 | stored bands, 5-year fusion | P1-new 80% | 30.1 | 31.6 | 0.820 / 0.659 | 0.00 | -0.2 [-2.4, +1.6] | -1.0 [-3.1, +0.1] | -4.4 [-6.6, -2.4] | -1.0 [-2.0, -0.2] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| 129 | stored bands, stored + 3-year ensemble fusion | P1-new 80% | 30.1 | 31.6 | 0.820 / 0.659 | 0.00 | -0.2 [-2.4, +1.6] | -1.0 [-3.1, +0.1] | -4.4 [-6.6, -2.4] | -1.0 [-2.0, -0.2] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| 130 | Cox (pre-event) H&E + stored copy number | R49-new t_low 90/t_high 95 | 30.3 | 31.9 | 0.868 / 0.571 | 2.73 | +0.1 [-2.9, +3.0] | -0.8 [-2.0, +0.1] | -4.1 [-8.6, +0.4] | -0.8 [-2.8, +0.8] | +2.1 [-1.1, +5.5] | -0.6 [-1.6, +0.1] |
| 131 | stored + strongly weighted ensemble | P1-new 80% | 29.8 | 32.9 | 0.824 / 0.649 | 0.00 | +1.1 [-1.3, +3.3] | -1.3 [-3.5, +0.1] | -3.1 [-4.6, -1.7] | -1.3 [-2.5, -0.3] | +1.3 [+0.2, +2.6] | -0.3 [-0.8, 0.0] |
| 132 | Cox (pre-event) H&E + stored copy number | R49-new t_low 90/t_high 90 | 30.3 | 33.3 | 0.882 / 0.535 | 2.40 | +1.5 [-1.6, +4.6] | -0.8 [-2.0, +0.1] | -2.7 [-7.3, +1.8] | -0.8 [-2.8, +0.8] | +2.3 [-1.0, +5.8] | -0.7 [-1.8, +0.1] |
| 133 | 5-year H&E + stored copy number | R49-new t_low 90/t_high 95 | 30.5 | 33.4 | 0.868 / 0.588 | 2.17 | +1.6 [-1.2, +4.7] | -0.6 [-2.0, 0.0] | -2.6 [-5.6, +0.5] | -0.6 [-2.9, +1.5] | +3.6 [+0.7, +7.0] | -0.4 [-1.8, +0.4] |
| 134 | certainty-weighted binary | P1-new 80% | 30.1 | 33.7 | 0.832 / 0.624 | 0.00 | +1.9 [-0.7, +4.5] | -1.0 [-3.2, +0.4] | -2.3 [-3.5, -1.2] | -1.0 [-1.9, -0.2] | +2.1 [+0.6, +3.7] | 0.0 [-0.4, +0.6] |
| 135 | weighted H&E + stored copy number | P1-new 80% | 30.1 | 33.7 | 0.832 / 0.624 | 0.00 | +1.9 [-0.7, +4.5] | -1.0 [-3.2, +0.4] | -2.3 [-3.5, -1.2] | -1.0 [-1.9, -0.2] | +2.1 [+0.6, +3.7] | 0.0 [-0.4, +0.6] |
| 136 | stored + 3-year ensemble | P1-new 80% | 29.8 | 34.0 | 0.791 / 0.622 | 0.00 | +2.2 [-0.8, +5.2] | -1.3 [-3.6, +0.3] | -2.0 [-3.1, -1.0] | -1.3 [-2.7, -0.3] | +2.4 [+0.6, +4.4] | -0.3 [-1.2, +0.4] |
| 137 | Cox, pre-event samples only | R49-new t_low 90/t_high 95 | 30.4 | 34.4 | 0.878 / 0.492 | 2.73 | +2.6 [-0.2, +5.5] | -0.7 [-2.0, +0.2] | -1.6 [-5.7, +2.2] | -0.7 [-2.4, +0.6] | +4.6 [+1.4, +7.9] | -0.5 [-1.6, +0.3] |
| 138 | stored + 5-year ensemble | P1-new 80% | 29.5 | 34.4 | 0.808 / 0.626 | 0.00 | +2.6 [-0.4, +5.8] | -1.6 [-3.7, -0.1] | -1.6 [-2.8, -0.5] | -1.6 [-3.2, -0.3] | +2.8 [+0.8, +4.9] | -0.6 [-1.6, +0.1] |
| 139 | 5-year H&E + stored copy number | R49-new t_low 95/t_high 95 | 30.5 | 34.5 | 0.894 / 0.555 | 2.48 | +2.7 [0.0, +5.6] | -0.6 [-2.0, 0.0] | -1.5 [-4.2, +1.4] | -0.6 [-2.9, +1.5] | +3.9 [+1.0, +7.2] | -0.6 [-2.0, 0.0] |
| 140 | 5-year H&E + stored copy number | R49-new t_low 90/t_high 90 | 30.5 | 34.7 | 0.883 / 0.555 | 1.83 | +2.9 [+0.1, +6.0] | -0.6 [-2.0, 0.0] | -1.3 [-4.3, +1.8] | -0.6 [-2.9, +1.5] | +3.7 [+0.7, +7.1] | -0.5 [-1.9, +0.3] |
| 141 | stored + Cox ensemble | P1-new 80% | 29.5 | 35.5 | 0.816 / 0.591 | 0.00 | +3.7 [+0.6, +6.7] | -1.6 [-4.0, 0.0] | -0.5 [-1.8, +0.8] | -1.6 [-3.2, -0.4] | +3.9 [+1.8, +6.0] | -0.6 [-1.3, -0.1] |
| 142 | 5-year H&E + stored copy number | R49-new t_low 95/t_high 90 | 30.5 | 35.6 | 0.907 / 0.517 | 2.14 | +3.8 [+1.1, +6.8] | -0.6 [-2.0, 0.0] | -0.4 [-3.0, +2.5] | -0.6 [-2.9, +1.5] | +3.8 [+1.1, +6.8] | -0.6 [-2.0, 0.0] |
| 143 | strongly weighted binary | P1-new 80% | 29.5 | 36.1 | 0.812 / 0.587 | 0.00 | +4.3 [+1.1, +7.9] | -1.6 [-3.9, +0.1] | +0.1 [-1.1, +1.4] | -1.6 [-3.2, -0.4] | +4.5 [+2.1, +7.1] | -0.6 [-1.6, +0.1] |
| 144 | 3-year horizon binary | P1-new 80% | 30.2 | 36.6 | 0.749 / 0.558 | 0.00 | +4.8 [+1.4, +8.5] | -0.9 [-2.9, +1.0] | +0.6 [-0.9, +2.3] | -0.9 [-3.3, +0.8] | +5.0 [+2.2, +8.0] | +0.1 [-2.1, +2.2] |
| 145 | Cox, pre-event samples only | P1-new 80% | 28.7 | 36.7 | 0.797 / 0.498 | 0.00 | +4.9 [+1.5, +8.6] | -2.4 [-5.1, -0.4] | +0.7 [-2.6, +3.9] | -2.4 [-4.7, -0.6] | +5.1 [+1.4, +8.7] | -1.4 [-2.8, -0.3] |
| 146 | Cox (pre-event) H&E + stored copy number | P1-new 80% | 28.7 | 36.7 | 0.797 / 0.498 | 0.00 | +4.9 [+1.5, +8.6] | -2.4 [-5.1, -0.4] | +0.7 [-2.6, +3.9] | -2.4 [-4.7, -0.6] | +5.1 [+1.4, +8.7] | -1.4 [-2.8, -0.3] |
| 147 | 5-year horizon binary | P1-new 80% | 29.3 | 36.8 | 0.799 / 0.564 | 0.00 | +5.0 [+1.6, +8.7] | -1.8 [-3.7, -0.4] | +0.8 [-1.0, +3.0] | -1.8 [-3.6, -0.4] | +5.2 [+2.3, +8.3] | -0.8 [-1.9, +0.1] |
| 148 | 5-year H&E + stored copy number | P1-new 80% | 29.3 | 36.8 | 0.799 / 0.564 | 0.00 | +5.0 [+1.6, +8.7] | -1.8 [-3.7, -0.4] | +0.8 [-1.0, +3.0] | -1.8 [-3.6, -0.4] | +5.2 [+2.3, +8.3] | -0.8 [-1.9, +0.1] |
| 149 | Cox, extended follow-up | P1-new 80% | 29.5 | 38.9 | 0.806 / 0.472 | 0.00 | +7.1 [+3.3, +11.2] | -1.6 [-4.4, +0.5] | +2.9 [+0.7, +5.8] | -1.6 [-3.3, -0.4] | +7.3 [+3.9, +10.8] | -0.6 [-2.1, +0.6] |
| 150 | Cox H&E + stored copy number | P1-new 80% | 29.5 | 38.9 | 0.806 / 0.472 | 0.00 | +7.1 [+3.3, +11.2] | -1.6 [-4.4, +0.5] | +2.9 [+0.7, +5.8] | -1.6 [-3.3, -0.4] | +7.3 [+3.9, +10.8] | -0.6 [-2.1, +0.6] |
| 151 | Cox, pre-event samples only | P1-new 90% | 30.5 | 40.3 | 0.889 / 0.312 | 0.00 | +8.5 [+4.7, +12.6] | -0.6 [-2.8, +0.8] | +4.3 [+1.5, +7.9] | -0.6 [-1.2, -0.1] | +4.3 [+1.5, +7.9] | -0.6 [-1.2, -0.1] |
| 152 | Cox (pre-event) H&E + stored copy number | P1-new 90% | 30.5 | 40.3 | 0.889 / 0.312 | 0.00 | +8.5 [+4.7, +12.6] | -0.6 [-2.8, +0.8] | +4.3 [+1.5, +7.9] | -0.6 [-1.2, -0.1] | +4.3 [+1.5, +7.9] | -0.6 [-1.2, -0.1] |

Reference: the same rules built on the stored scores (the 'same rule, stored scores' comparator; R49 is the t_low 95 / t_high 90 gate, P1 is P1-new 90% here):

| Rule | Caught | NP flagged | Endo sens / spec | Seq / patient |
|---|---|---|---|---|
| P1-new 80% | 30.1 | 31.6 | 0.820 / 0.659 | 0.00 |
| P1-new 90% | 31.1 | 36.0 | 0.898 / 0.524 | 0.00 |
| P1-new 95% | 31.9 | 39.3 | 0.942 / 0.370 | 0.00 |
| P3-new 90% | 31.2 | 31.8 | 0.912 / 0.551 | 7.61 |
| R49-new t_low 95/t_high 90 | 31.1 | 31.8 | 0.907 / 0.560 | 1.94 |
| R49-new t_low 90/t_high 90 | 31.0 | 31.0 | 0.887 / 0.611 | 1.59 |
| R49-new t_low 95/t_high 95 | 31.1 | 30.6 | 0.895 / 0.603 | 2.25 |
| R49-new t_low 90/t_high 95 | 30.9 | 29.8 | 0.865 / 0.645 | 1.90 |

### Endoscopy specificity at matched endoscopy sensitivity

Each endoscopy score is thresholded per repeat to the reference rule's realised endoscopy sensitivity (re-matched in every bootstrap draw; evaluation-matched, so this isolates ranking quality, not a deployable threshold). 'vs stored score' = the same matching applied to the stored score (max L-IMG for H&E, max L-LATE for the fusion), i.e. the gain from the time-aware training alone.

| Scheme | Score | Matched to | Spec at matched sens | Δ spec vs reference [CI] | Δ spec vs stored score [CI] | NP flagged | Δ NP flagged vs reference [CI] | Δ caught vs reference |
|---|---|---|---|---|---|---|---|---|
| stored (control) | H&E max | R49 (0.907) | 0.493 | -0.068 [-0.165, +0.038] | 0.000 [0.000, 0.000] | 36.8 | +5.0 [+1.1, +8.7] | +0.1 |
| stored (control) | fusion max (sequence all) | R49 (0.907) | 0.591 | +0.030 [-0.046, +0.118] | 0.000 [0.000, 0.000] | 30.7 | -1.1 [-5.4, +1.6] | 0.0 |
| stored (control) | H&E max | P1 90% (0.898) | 0.537 | +0.012 [-0.010, +0.055] | 0.000 [0.000, 0.000] | 35.6 | -0.4 [-1.9, +0.3] | 0.0 |
| stored (control) | fusion max (sequence all) | P1 90% (0.898) | 0.626 | +0.102 [-0.053, +0.217] | 0.000 [0.000, 0.000] | 28.6 | -7.4 [-13.2, -1.2] | +0.1 |
| Cox, extended follow-up | H&E max | R49 (0.907) | 0.344 | -0.216 [-0.331, -0.106] | -0.149 [-0.257, -0.042] | 39.9 | +8.1 [+4.2, +12.6] | +0.1 |
| Cox, extended follow-up | fusion max (sequence all) | R49 (0.907) | 0.365 | -0.195 [-0.325, -0.013] | -0.226 [-0.352, -0.064] | 38.1 | +6.3 [+0.7, +10.9] | +0.9 |
| Cox, extended follow-up | H&E max | P1 90% (0.898) | 0.366 | -0.158 [-0.261, -0.072] | -0.171 [-0.288, -0.077] | 40.0 | +4.0 [+1.2, +7.5] | +0.2 |
| Cox, extended follow-up | fusion max (sequence all) | P1 90% (0.898) | 0.404 | -0.120 [-0.303, +0.086] | -0.222 [-0.345, -0.059] | 37.5 | +1.5 [-6.0, +6.8] | +0.8 |
| Cox, study follow-up | H&E max | R49 (0.907) | 0.199 | -0.362 [-0.463, -0.238] | -0.294 [-0.388, -0.177] | 42.5 | +10.7 [+6.5, +15.2] | +0.9 |
| Cox, study follow-up | fusion max (sequence all) | R49 (0.907) | 0.237 | -0.323 [-0.413, -0.210] | -0.353 [-0.442, -0.248] | 42.3 | +10.5 [+6.1, +15.0] | +0.9 |
| Cox, study follow-up | H&E max | P1 90% (0.898) | 0.203 | -0.322 [-0.397, -0.203] | -0.334 [-0.423, -0.216] | 42.5 | +6.5 [+3.0, +10.8] | +0.9 |
| Cox, study follow-up | fusion max (sequence all) | P1 90% (0.898) | 0.244 | -0.280 [-0.380, -0.123] | -0.382 [-0.455, -0.258] | 42.3 | +6.3 [+2.0, +10.5] | +0.9 |
| Cox, pre-event samples only | H&E max | R49 (0.907) | 0.291 | -0.269 [-0.399, -0.096] | -0.201 [-0.337, -0.021] | 40.2 | +8.4 [+4.0, +12.6] | -0.1 |
| Cox, pre-event samples only | fusion max (sequence all) | R49 (0.907) | 0.428 | -0.133 [-0.264, +0.019] | -0.163 [-0.279, -0.044] | 35.5 | +3.7 [-1.8, +7.7] | +0.2 |
| Cox, pre-event samples only | H&E max | P1 90% (0.898) | 0.338 | -0.187 [-0.345, -0.046] | -0.199 [-0.367, -0.060] | 39.6 | +3.6 [-0.2, +7.6] | -0.2 |
| Cox, pre-event samples only | fusion max (sequence all) | P1 90% (0.898) | 0.449 | -0.076 [-0.249, +0.105] | -0.178 [-0.280, -0.045] | 34.8 | -1.2 [-8.0, +4.1] | +0.1 |
| 3-year horizon binary | H&E max | R49 (0.907) | 0.309 | -0.251 [-0.345, -0.144] | -0.183 [-0.310, -0.068] | 41.7 | +9.9 [+5.6, +14.2] | +0.6 |
| 3-year horizon binary | fusion max (sequence all) | R49 (0.907) | 0.488 | -0.072 [-0.242, +0.040] | -0.103 [-0.245, +0.007] | 36.8 | +5.0 [-0.1, +10.2] | +0.2 |
| 3-year horizon binary | H&E max | P1 90% (0.898) | 0.321 | -0.204 [-0.323, -0.083] | -0.216 [-0.347, -0.102] | 41.4 | +5.4 [+1.7, +9.2] | +0.5 |
| 3-year horizon binary | fusion max (sequence all) | P1 90% (0.898) | 0.512 | -0.012 [-0.271, +0.131] | -0.114 [-0.263, -0.006] | 35.6 | -0.4 [-6.8, +6.4] | +0.2 |
| 5-year horizon binary | H&E max | R49 (0.907) | 0.399 | -0.161 [-0.252, -0.054] | -0.094 [-0.218, +0.013] | 40.3 | +8.5 [+4.7, +12.3] | 0.0 |
| 5-year horizon binary | fusion max (sequence all) | R49 (0.907) | 0.533 | -0.027 [-0.145, +0.085] | -0.057 [-0.143, +0.039] | 34.6 | +2.8 [-2.6, +6.7] | -0.3 |
| 5-year horizon binary | H&E max | P1 90% (0.898) | 0.412 | -0.112 [-0.242, -0.005] | -0.124 [-0.261, -0.025] | 40.1 | +4.1 [+1.1, +7.6] | -0.1 |
| 5-year horizon binary | fusion max (sequence all) | P1 90% (0.898) | 0.545 | +0.021 [-0.188, +0.202] | -0.081 [-0.176, +0.034] | 33.5 | -2.5 [-11.0, +3.7] | 0.0 |
| certainty-weighted binary | H&E max | R49 (0.907) | 0.491 | -0.069 [-0.177, +0.027] | -0.002 [-0.061, +0.043] | 37.1 | +5.3 [+1.7, +9.6] | +0.4 |
| certainty-weighted binary | fusion max (sequence all) | R49 (0.907) | 0.575 | +0.014 [-0.058, +0.103] | -0.016 [-0.049, +0.028] | 31.1 | -0.7 [-4.7, +2.3] | +0.4 |
| certainty-weighted binary | H&E max | P1 90% (0.898) | 0.508 | -0.016 [-0.068, +0.041] | -0.028 [-0.084, +0.011] | 37.0 | +1.0 [-0.8, +3.1] | 0.0 |
| certainty-weighted binary | fusion max (sequence all) | P1 90% (0.898) | 0.601 | +0.077 [-0.086, +0.211] | -0.025 [-0.059, +0.021] | 29.7 | -6.3 [-12.6, -0.2] | +0.2 |
| strongly weighted binary | H&E max | R49 (0.907) | 0.469 | -0.091 [-0.200, -0.008] | -0.024 [-0.127, +0.044] | 38.3 | +6.5 [+3.1, +10.5] | +0.6 |
| strongly weighted binary | fusion max (sequence all) | R49 (0.907) | 0.543 | -0.017 [-0.121, +0.092] | -0.048 [-0.122, +0.025] | 32.5 | +0.7 [-3.3, +5.1] | +0.4 |
| strongly weighted binary | H&E max | P1 90% (0.898) | 0.486 | -0.038 [-0.147, +0.026] | -0.051 [-0.167, +0.008] | 38.4 | +2.4 [+0.1, +4.9] | +0.3 |
| strongly weighted binary | fusion max (sequence all) | P1 90% (0.898) | 0.560 | +0.035 [-0.138, +0.197] | -0.067 [-0.131, +0.017] | 31.6 | -4.4 [-11.5, +2.3] | +0.4 |
| Cox H&E + stored copy number | H&E max | R49 (0.907) | 0.344 | -0.216 [-0.331, -0.106] | -0.149 [-0.257, -0.042] | 39.9 | +8.1 [+4.2, +12.6] | +0.1 |
| Cox H&E + stored copy number | fusion max (sequence all) | R49 (0.907) | 0.522 | -0.038 [-0.132, +0.065] | -0.068 [-0.145, +0.006] | 32.4 | +0.6 [-4.0, +4.5] | +0.1 |
| Cox H&E + stored copy number | H&E max | P1 90% (0.898) | 0.366 | -0.158 [-0.261, -0.072] | -0.171 [-0.288, -0.077] | 40.0 | +4.0 [+1.2, +7.5] | +0.2 |
| Cox H&E + stored copy number | fusion max (sequence all) | P1 90% (0.898) | 0.540 | +0.016 [-0.138, +0.180] | -0.086 [-0.147, +0.001] | 31.5 | -4.5 [-11.9, +1.5] | -0.2 |
| Cox (pre-event) H&E + stored copy number | H&E max | R49 (0.907) | 0.291 | -0.269 [-0.399, -0.096] | -0.201 [-0.337, -0.021] | 40.2 | +8.4 [+4.0, +12.6] | -0.1 |
| Cox (pre-event) H&E + stored copy number | fusion max (sequence all) | R49 (0.907) | 0.520 | -0.040 [-0.170, +0.086] | -0.070 [-0.163, +0.012] | 33.7 | +1.9 [-3.7, +6.2] | -0.1 |
| Cox (pre-event) H&E + stored copy number | H&E max | P1 90% (0.898) | 0.338 | -0.187 [-0.345, -0.046] | -0.199 [-0.367, -0.060] | 39.6 | +3.6 [-0.2, +7.6] | -0.2 |
| Cox (pre-event) H&E + stored copy number | fusion max (sequence all) | P1 90% (0.898) | 0.541 | +0.017 [-0.197, +0.200] | -0.085 [-0.182, +0.020] | 31.8 | -4.2 [-11.9, +3.1] | -0.2 |
| stored H&E + Cox copy number | H&E max | R49 (0.907) | 0.493 | -0.068 [-0.165, +0.038] | 0.000 [0.000, 0.000] | 36.8 | +5.0 [+1.1, +8.7] | +0.1 |
| stored H&E + Cox copy number | fusion max (sequence all) | R49 (0.907) | 0.508 | -0.052 [-0.158, +0.081] | -0.083 [-0.184, +0.045] | 33.5 | +1.7 [-3.5, +5.6] | +0.8 |
| stored H&E + Cox copy number | H&E max | P1 90% (0.898) | 0.537 | +0.012 [-0.010, +0.055] | 0.000 [0.000, 0.000] | 35.6 | -0.4 [-1.9, +0.3] | 0.0 |
| stored H&E + Cox copy number | fusion max (sequence all) | P1 90% (0.898) | 0.567 | +0.043 [-0.149, +0.180] | -0.059 [-0.166, +0.038] | 31.0 | -5.0 [-11.1, +2.2] | +0.5 |
| weighted H&E + stored copy number | H&E max | R49 (0.907) | 0.491 | -0.069 [-0.177, +0.027] | -0.002 [-0.061, +0.043] | 37.1 | +5.3 [+1.7, +9.6] | +0.4 |
| weighted H&E + stored copy number | fusion max (sequence all) | R49 (0.907) | 0.558 | -0.002 [-0.062, +0.104] | -0.032 [-0.050, +0.015] | 30.7 | -1.1 [-5.4, +1.6] | +0.2 |
| weighted H&E + stored copy number | H&E max | P1 90% (0.898) | 0.508 | -0.016 [-0.068, +0.041] | -0.028 [-0.084, +0.011] | 37.0 | +1.0 [-0.8, +3.1] | 0.0 |
| weighted H&E + stored copy number | fusion max (sequence all) | P1 90% (0.898) | 0.595 | +0.070 [-0.093, +0.216] | -0.032 [-0.060, +0.010] | 29.3 | -6.7 [-13.6, -0.1] | +0.1 |
| 5-year H&E + stored copy number | H&E max | R49 (0.907) | 0.399 | -0.161 [-0.252, -0.054] | -0.094 [-0.218, +0.013] | 40.3 | +8.5 [+4.7, +12.3] | 0.0 |
| 5-year H&E + stored copy number | fusion max (sequence all) | R49 (0.907) | 0.513 | -0.047 [-0.141, +0.081] | -0.078 [-0.149, +0.016] | 35.4 | +3.6 [-3.0, +7.0] | -0.5 |
| 5-year H&E + stored copy number | H&E max | P1 90% (0.898) | 0.412 | -0.112 [-0.242, -0.005] | -0.124 [-0.261, -0.025] | 40.1 | +4.1 [+1.1, +7.6] | -0.1 |
| 5-year H&E + stored copy number | fusion max (sequence all) | P1 90% (0.898) | 0.538 | +0.014 [-0.183, +0.193] | -0.088 [-0.179, +0.013] | 34.4 | -1.6 [-11.0, +3.6] | -0.4 |
| stored + Cox ensemble | H&E max | R49 (0.907) | 0.468 | -0.092 [-0.212, -0.001] | -0.025 [-0.110, +0.039] | 38.4 | +6.6 [+2.9, +10.5] | -0.1 |
| stored + Cox ensemble | fusion max (sequence all) | R49 (0.907) | 0.568 | +0.008 [-0.112, +0.143] | -0.023 [-0.124, +0.068] | 31.1 | -0.7 [-6.4, +3.8] | +0.3 |
| stored + Cox ensemble | H&E max | P1 90% (0.898) | 0.479 | -0.045 [-0.096, +0.013] | -0.057 [-0.116, 0.000] | 38.1 | +2.1 [0.0, +4.6] | -0.2 |
| stored + Cox ensemble | fusion max (sequence all) | P1 90% (0.898) | 0.605 | +0.080 [-0.127, +0.250] | -0.022 [-0.122, +0.062] | 29.1 | -6.9 [-14.7, +0.8] | -0.1 |
| stored + 3-year ensemble | H&E max | R49 (0.907) | 0.479 | -0.082 [-0.164, +0.029] | -0.014 [-0.058, +0.054] | 37.7 | +5.9 [+1.7, +9.1] | +0.6 |
| stored + 3-year ensemble | fusion max (sequence all) | R49 (0.907) | 0.579 | +0.018 [-0.079, +0.111] | -0.012 [-0.075, +0.058] | 31.5 | -0.3 [-4.4, +3.4] | +0.3 |
| stored + 3-year ensemble | H&E max | P1 90% (0.898) | 0.505 | -0.019 [-0.065, +0.045] | -0.031 [-0.080, +0.018] | 36.8 | +0.8 [-0.8, +2.5] | +0.6 |
| stored + 3-year ensemble | fusion max (sequence all) | P1 90% (0.898) | 0.599 | +0.074 [-0.092, +0.217] | -0.027 [-0.090, +0.056] | 29.9 | -6.1 [-12.2, +0.6] | +0.1 |
| stored + 5-year ensemble | H&E max | R49 (0.907) | 0.474 | -0.087 [-0.169, +0.013] | -0.019 [-0.066, +0.040] | 38.5 | +6.7 [+2.4, +10.1] | +0.2 |
| stored + 5-year ensemble | fusion max (sequence all) | R49 (0.907) | 0.569 | +0.008 [-0.076, +0.126] | -0.022 [-0.064, +0.048] | 31.4 | -0.4 [-4.9, +2.5] | 0.0 |
| stored + 5-year ensemble | H&E max | P1 90% (0.898) | 0.509 | -0.016 [-0.083, +0.035] | -0.028 [-0.098, +0.008] | 37.6 | +1.6 [-0.2, +4.3] | 0.0 |
| stored + 5-year ensemble | fusion max (sequence all) | P1 90% (0.898) | 0.594 | +0.070 [-0.100, +0.233] | -0.032 [-0.081, +0.048] | 30.1 | -5.9 [-13.4, +0.3] | 0.0 |
| stored + strongly weighted ensemble | H&E max | R49 (0.907) | 0.497 | -0.063 [-0.155, +0.034] | +0.005 [-0.043, +0.054] | 36.9 | +5.1 [+1.3, +9.1] | +0.1 |
| stored + strongly weighted ensemble | fusion max (sequence all) | R49 (0.907) | 0.588 | +0.028 [-0.057, +0.116] | -0.002 [-0.039, +0.039] | 30.2 | -1.6 [-5.3, +1.7] | +0.3 |
| stored + strongly weighted ensemble | H&E max | P1 90% (0.898) | 0.527 | +0.002 [-0.049, +0.063] | -0.010 [-0.067, +0.032] | 36.2 | +0.2 [-1.7, +2.0] | +0.2 |
| stored + strongly weighted ensemble | fusion max (sequence all) | P1 90% (0.898) | 0.613 | +0.088 [-0.074, +0.219] | -0.014 [-0.042, +0.031] | 29.0 | -7.0 [-13.3, -0.7] | +0.3 |
| stored bands, 3-year fusion | H&E max | R49 (0.907) | 0.493 | -0.068 [-0.165, +0.038] | 0.000 [0.000, 0.000] | 36.8 | +5.0 [+1.1, +8.7] | +0.1 |
| stored bands, 3-year fusion | fusion max (sequence all) | R49 (0.907) | 0.488 | -0.072 [-0.242, +0.040] | -0.103 [-0.245, +0.007] | 36.8 | +5.0 [-0.1, +10.2] | +0.2 |
| stored bands, 3-year fusion | H&E max | P1 90% (0.898) | 0.537 | +0.012 [-0.010, +0.055] | 0.000 [0.000, 0.000] | 35.6 | -0.4 [-1.9, +0.3] | 0.0 |
| stored bands, 3-year fusion | fusion max (sequence all) | P1 90% (0.898) | 0.512 | -0.012 [-0.271, +0.131] | -0.114 [-0.263, -0.006] | 35.6 | -0.4 [-6.8, +6.4] | +0.2 |
| stored bands, 5-year fusion | H&E max | R49 (0.907) | 0.493 | -0.068 [-0.165, +0.038] | 0.000 [0.000, 0.000] | 36.8 | +5.0 [+1.1, +8.7] | +0.1 |
| stored bands, 5-year fusion | fusion max (sequence all) | R49 (0.907) | 0.533 | -0.027 [-0.145, +0.085] | -0.057 [-0.143, +0.039] | 34.6 | +2.8 [-2.6, +6.7] | -0.3 |
| stored bands, 5-year fusion | H&E max | P1 90% (0.898) | 0.537 | +0.012 [-0.010, +0.055] | 0.000 [0.000, 0.000] | 35.6 | -0.4 [-1.9, +0.3] | 0.0 |
| stored bands, 5-year fusion | fusion max (sequence all) | P1 90% (0.898) | 0.545 | +0.021 [-0.188, +0.202] | -0.081 [-0.176, +0.034] | 33.5 | -2.5 [-11.0, +3.7] | 0.0 |
| stored bands, stored + 3-year ensemble fusion | H&E max | R49 (0.907) | 0.493 | -0.068 [-0.165, +0.038] | 0.000 [0.000, 0.000] | 36.8 | +5.0 [+1.1, +8.7] | +0.1 |
| stored bands, stored + 3-year ensemble fusion | fusion max (sequence all) | R49 (0.907) | 0.579 | +0.018 [-0.079, +0.111] | -0.012 [-0.075, +0.058] | 31.5 | -0.3 [-4.4, +3.4] | +0.3 |
| stored bands, stored + 3-year ensemble fusion | H&E max | P1 90% (0.898) | 0.537 | +0.012 [-0.010, +0.055] | 0.000 [0.000, 0.000] | 35.6 | -0.4 [-1.9, +0.3] | 0.0 |
| stored bands, stored + 3-year ensemble fusion | fusion max (sequence all) | P1 90% (0.898) | 0.599 | +0.074 [-0.092, +0.217] | -0.027 [-0.090, +0.056] | 29.9 | -6.1 [-12.2, +0.6] | +0.1 |

New gates against H&E alone matched to the gate's own realised endoscopy sensitivity (round 8b S1 (a)(i) form; Δ = gate − P1):

| Scheme | Gate | Δ spec [CI] | Δ NP flagged [CI] | Δ caught [CI] |
|---|---|---|---|---|
| stored (control) | R49-new t_low 95/t_high 90 | +0.068 [-0.038, +0.165] | -5.0 [-8.7, -1.1] | -0.1 [-1.3, +0.8] |
| stored (control) | R49-new t_low 90/t_high 90 | +0.070 [-0.011, +0.164] | -4.7 [-8.2, -1.2] | -0.2 [-1.0, +0.9] |
| stored (control) | R49-new t_low 95/t_high 95 | +0.079 [-0.033, +0.188] | -5.1 [-9.5, -1.5] | -0.1 [-1.2, +1.0] |
| stored (control) | R49-new t_low 90/t_high 95 | +0.062 [-0.023, +0.158] | -4.6 [-8.2, -1.0] | -0.1 [-1.2, +1.3] |
| Cox, extended follow-up | R49-new t_low 95/t_high 90 | -0.131 [-0.289, +0.107] | +2.1 [-3.2, +7.9] | +0.5 [-0.5, +1.8] |
| Cox, extended follow-up | R49-new t_low 90/t_high 90 | -0.110 [-0.251, +0.114] | +1.9 [-3.5, +8.0] | +0.6 [-0.5, +2.2] |
| Cox, extended follow-up | R49-new t_low 95/t_high 95 | -0.135 [-0.282, +0.090] | +2.4 [-3.4, +8.6] | +0.6 [-0.5, +2.3] |
| Cox, extended follow-up | R49-new t_low 90/t_high 95 | -0.118 [-0.253, +0.100] | +2.3 [-4.0, +8.2] | +0.8 [-0.5, +2.6] |
| Cox, study follow-up | R49-new t_low 95/t_high 90 | -0.249 [-0.378, -0.082] | +7.4 [+2.2, +13.5] | +1.0 [-0.1, +2.6] |
| Cox, study follow-up | R49-new t_low 90/t_high 90 | -0.258 [-0.378, -0.120] | +7.7 [+2.8, +14.1] | +1.1 [0.0, +3.1] |
| Cox, study follow-up | R49-new t_low 95/t_high 95 | -0.266 [-0.398, -0.105] | +7.9 [+2.7, +15.0] | +1.0 [-0.1, +3.0] |
| Cox, study follow-up | R49-new t_low 90/t_high 95 | -0.280 [-0.400, -0.127] | +8.8 [+3.0, +15.9] | +1.1 [-0.1, +3.6] |
| Cox, pre-event samples only | R49-new t_low 95/t_high 90 | -0.042 [-0.213, +0.158] | -1.5 [-6.3, +4.0] | -0.3 [-1.2, +0.4] |
| Cox, pre-event samples only | R49-new t_low 90/t_high 90 | -0.043 [-0.200, +0.154] | -0.8 [-6.3, +4.7] | -0.5 [-1.6, +0.3] |
| Cox, pre-event samples only | R49-new t_low 95/t_high 95 | -0.039 [-0.210, +0.166] | -1.6 [-6.4, +4.2] | -0.5 [-1.8, +0.5] |
| Cox, pre-event samples only | R49-new t_low 90/t_high 95 | -0.033 [-0.201, +0.161] | -1.3 [-6.5, +5.2] | -0.8 [-2.1, +0.4] |
| 3-year horizon binary | R49-new t_low 95/t_high 90 | -0.042 [-0.155, +0.144] | +1.2 [-3.2, +6.5] | -0.2 [-2.5, +1.4] |
| 3-year horizon binary | R49-new t_low 90/t_high 90 | -0.052 [-0.146, +0.083] | +1.8 [-2.2, +7.5] | +0.3 [-1.8, +2.0] |
| 3-year horizon binary | R49-new t_low 95/t_high 95 | -0.021 [-0.129, +0.158] | +0.6 [-3.9, +5.8] | 0.0 [-2.2, +1.6] |
| 3-year horizon binary | R49-new t_low 90/t_high 95 | -0.033 [-0.122, +0.085] | +1.7 [-2.8, +6.9] | +0.6 [-1.6, +2.4] |
| 5-year horizon binary | R49-new t_low 95/t_high 90 | +0.024 [-0.132, +0.204] | -1.1 [-5.4, +3.8] | -0.3 [-1.5, +1.0] |
| 5-year horizon binary | R49-new t_low 90/t_high 90 | +0.022 [-0.114, +0.191] | -1.6 [-5.4, +3.7] | -0.2 [-1.9, +0.9] |
| 5-year horizon binary | R49-new t_low 95/t_high 95 | +0.044 [-0.110, +0.228] | -2.3 [-6.9, +2.8] | -0.3 [-1.9, +1.0] |
| 5-year horizon binary | R49-new t_low 90/t_high 95 | +0.029 [-0.091, +0.206] | -2.4 [-6.7, +2.6] | -0.2 [-2.1, +1.2] |
| certainty-weighted binary | R49-new t_low 95/t_high 90 | +0.069 [-0.065, +0.203] | -4.1 [-7.4, -0.2] | +0.4 [-0.5, +1.1] |
| certainty-weighted binary | R49-new t_low 90/t_high 90 | +0.052 [-0.052, +0.148] | -4.3 [-7.3, -0.1] | +0.4 [-0.5, +1.5] |
| certainty-weighted binary | R49-new t_low 95/t_high 95 | +0.071 [-0.061, +0.222] | -4.4 [-9.0, -0.5] | +0.2 [-0.9, +1.3] |
| certainty-weighted binary | R49-new t_low 90/t_high 95 | +0.058 [-0.039, +0.163] | -4.3 [-7.8, -0.3] | +0.1 [-1.1, +1.5] |
| strongly weighted binary | R49-new t_low 95/t_high 90 | +0.044 [-0.099, +0.223] | -2.6 [-6.9, +1.7] | +0.2 [-0.8, +1.0] |
| strongly weighted binary | R49-new t_low 90/t_high 90 | +0.048 [-0.078, +0.206] | -2.9 [-6.9, +1.4] | +0.4 [-0.7, +1.5] |
| strongly weighted binary | R49-new t_low 95/t_high 95 | +0.070 [-0.077, +0.243] | -3.7 [-8.4, +0.6] | +0.2 [-0.8, +1.3] |
| strongly weighted binary | R49-new t_low 90/t_high 95 | +0.053 [-0.058, +0.204] | -3.9 [-7.8, +0.3] | +0.5 [-0.7, +1.7] |
| Cox H&E + stored copy number | R49-new t_low 95/t_high 90 | -0.016 [-0.169, +0.186] | -2.0 [-7.3, +3.1] | -0.1 [-1.5, +1.0] |
| Cox H&E + stored copy number | R49-new t_low 90/t_high 90 | +0.002 [-0.152, +0.202] | -2.5 [-8.0, +3.5] | -0.1 [-1.5, +1.2] |
| Cox H&E + stored copy number | R49-new t_low 95/t_high 95 | -0.010 [-0.162, +0.205] | -2.8 [-8.7, +2.8] | 0.0 [-1.5, +1.1] |
| Cox H&E + stored copy number | R49-new t_low 90/t_high 95 | -0.002 [-0.151, +0.204] | -3.3 [-9.3, +3.3] | -0.2 [-1.5, +1.4] |
| Cox (pre-event) H&E + stored copy number | R49-new t_low 95/t_high 90 | -0.023 [-0.175, +0.203] | -1.9 [-7.5, +4.0] | -0.5 [-2.0, +0.7] |
| Cox (pre-event) H&E + stored copy number | R49-new t_low 90/t_high 90 | -0.020 [-0.151, +0.208] | -1.6 [-8.0, +4.3] | -0.7 [-2.4, +0.4] |
| Cox (pre-event) H&E + stored copy number | R49-new t_low 95/t_high 95 | +0.004 [-0.149, +0.234] | -2.7 [-8.5, +3.2] | -0.4 [-2.0, +0.8] |
| Cox (pre-event) H&E + stored copy number | R49-new t_low 90/t_high 95 | -0.015 [-0.142, +0.216] | -2.4 [-8.8, +3.5] | -0.6 [-2.2, +0.8] |
| stored H&E + Cox copy number | R49-new t_low 95/t_high 90 | +0.028 [-0.091, +0.130] | -2.9 [-6.4, +1.7] | +0.6 [-0.2, +1.4] |
| stored H&E + Cox copy number | R49-new t_low 90/t_high 90 | +0.016 [-0.077, +0.106] | -2.5 [-6.2, +1.3] | +0.6 [-0.3, +1.6] |
| stored H&E + Cox copy number | R49-new t_low 95/t_high 95 | +0.042 [-0.087, +0.143] | -2.9 [-6.9, +1.5] | +0.5 [-0.5, +1.5] |
| stored H&E + Cox copy number | R49-new t_low 90/t_high 95 | +0.028 [-0.070, +0.125] | -3.3 [-7.1, +0.8] | +0.3 [-1.0, +1.8] |
| weighted H&E + stored copy number | R49-new t_low 95/t_high 90 | +0.060 [-0.068, +0.199] | -4.4 [-8.5, -0.3] | 0.0 [-1.1, +0.9] |
| weighted H&E + stored copy number | R49-new t_low 90/t_high 90 | +0.061 [-0.046, +0.152] | -4.8 [-8.0, -0.3] | 0.0 [-1.0, +1.2] |
| weighted H&E + stored copy number | R49-new t_low 95/t_high 95 | +0.057 [-0.069, +0.191] | -4.8 [-9.1, 0.0] | -0.1 [-1.5, +1.2] |
| weighted H&E + stored copy number | R49-new t_low 90/t_high 95 | +0.041 [-0.046, +0.150] | -4.4 [-8.3, 0.0] | +0.1 [-1.4, +1.5] |
| 5-year H&E + stored copy number | R49-new t_low 95/t_high 90 | +0.031 [-0.135, +0.240] | -1.2 [-5.8, +4.2] | -0.8 [-2.7, +0.6] |
| 5-year H&E + stored copy number | R49-new t_low 90/t_high 90 | +0.018 [-0.118, +0.205] | -0.7 [-5.4, +4.4] | -0.5 [-2.3, +0.9] |
| 5-year H&E + stored copy number | R49-new t_low 95/t_high 95 | +0.053 [-0.110, +0.243] | -1.5 [-6.2, +3.8] | -0.7 [-2.5, +0.7] |
| 5-year H&E + stored copy number | R49-new t_low 90/t_high 95 | +0.018 [-0.107, +0.207] | -1.2 [-5.9, +4.0] | -0.3 [-2.1, +1.1] |
| stored + Cox ensemble | R49-new t_low 95/t_high 90 | +0.054 [-0.102, +0.234] | -4.2 [-8.6, +1.4] | -0.1 [-1.2, +0.9] |
| stored + Cox ensemble | R49-new t_low 90/t_high 90 | +0.065 [-0.057, +0.222] | -3.8 [-8.7, +0.8] | -0.1 [-1.3, +1.1] |
| stored + Cox ensemble | R49-new t_low 95/t_high 95 | +0.064 [-0.088, +0.253] | -4.2 [-9.5, +0.7] | 0.0 [-1.3, +1.1] |
| stored + Cox ensemble | R49-new t_low 90/t_high 95 | +0.057 [-0.063, +0.220] | -4.1 [-8.9, +0.8] | -0.2 [-1.6, +1.1] |
| stored + 3-year ensemble | R49-new t_low 95/t_high 90 | +0.081 [-0.051, +0.218] | -3.6 [-7.8, +0.4] | +0.2 [-0.8, +1.1] |
| stored + 3-year ensemble | R49-new t_low 90/t_high 90 | +0.071 [-0.019, +0.189] | -3.8 [-8.0, -0.3] | +0.2 [-1.1, +1.1] |
| stored + 3-year ensemble | R49-new t_low 95/t_high 95 | +0.072 [-0.032, +0.214] | -4.7 [-8.6, -0.5] | -0.1 [-1.5, +1.2] |
| stored + 3-year ensemble | R49-new t_low 90/t_high 95 | +0.081 [-0.005, +0.183] | -5.3 [-8.9, -1.3] | -0.1 [-1.6, +1.0] |
| stored + 5-year ensemble | R49-new t_low 95/t_high 90 | +0.088 [-0.051, +0.215] | -4.4 [-8.0, -0.3] | +0.1 [-1.1, +0.8] |
| stored + 5-year ensemble | R49-new t_low 90/t_high 90 | +0.085 [-0.035, +0.180] | -4.2 [-7.1, +0.1] | +0.1 [-1.1, +1.1] |
| stored + 5-year ensemble | R49-new t_low 95/t_high 95 | +0.089 [-0.043, +0.217] | -4.7 [-8.6, -0.6] | -0.1 [-1.4, +1.0] |
| stored + 5-year ensemble | R49-new t_low 90/t_high 95 | +0.089 [-0.030, +0.180] | -4.5 [-7.9, -0.0] | -0.2 [-1.6, +1.3] |
| stored + strongly weighted ensemble | R49-new t_low 95/t_high 90 | +0.108 [-0.035, +0.265] | -5.1 [-9.3, -0.9] | +0.3 [-0.8, +1.0] |
| stored + strongly weighted ensemble | R49-new t_low 90/t_high 90 | +0.095 [-0.023, +0.191] | -5.1 [-8.6, -1.0] | +0.3 [-0.4, +1.5] |
| stored + strongly weighted ensemble | R49-new t_low 95/t_high 95 | +0.113 [-0.029, +0.244] | -5.4 [-9.8, -1.2] | +0.2 [-0.7, +1.3] |
| stored + strongly weighted ensemble | R49-new t_low 90/t_high 95 | +0.077 [-0.022, +0.194] | -4.5 [-8.3, -0.7] | 0.0 [-1.2, +1.4] |
| stored bands, 3-year fusion | R49-new t_low 95/t_high 90 | -0.009 [-0.092, +0.102] | +0.1 [-3.1, +3.4] | +0.2 [-1.5, +1.2] |
| stored bands, 3-year fusion | R49-new t_low 90/t_high 90 | +0.015 [-0.062, +0.105] | -0.7 [-3.7, +2.7] | +0.1 [-1.4, +1.3] |
| stored bands, 3-year fusion | R49-new t_low 95/t_high 95 | +0.023 [-0.075, +0.133] | -1.8 [-5.1, +2.0] | -0.1 [-2.0, +1.4] |
| stored bands, 3-year fusion | R49-new t_low 90/t_high 95 | +0.027 [-0.062, +0.124] | -1.8 [-5.0, +2.4] | -0.1 [-1.9, +1.4] |
| stored bands, 5-year fusion | R49-new t_low 95/t_high 90 | +0.058 [-0.064, +0.158] | -2.2 [-5.6, +1.6] | -0.2 [-1.5, +0.6] |
| stored bands, 5-year fusion | R49-new t_low 90/t_high 90 | +0.045 [-0.048, +0.136] | -2.4 [-5.4, +1.5] | -0.2 [-1.5, +0.8] |
| stored bands, 5-year fusion | R49-new t_low 95/t_high 95 | +0.059 [-0.060, +0.167] | -2.8 [-6.6, +1.2] | -0.3 [-1.8, +0.9] |
| stored bands, 5-year fusion | R49-new t_low 90/t_high 95 | +0.038 [-0.055, +0.150] | -2.3 [-5.9, +2.0] | -0.3 [-1.9, +1.1] |
| stored bands, stored + 3-year ensemble fusion | R49-new t_low 95/t_high 90 | +0.068 [-0.052, +0.166] | -3.8 [-7.3, -0.2] | +0.1 [-1.1, +1.1] |
| stored bands, stored + 3-year ensemble fusion | R49-new t_low 90/t_high 90 | +0.057 [-0.030, +0.157] | -3.8 [-7.4, -0.2] | 0.0 [-1.1, +1.1] |
| stored bands, stored + 3-year ensemble fusion | R49-new t_low 95/t_high 95 | +0.064 [-0.042, +0.175] | -4.9 [-8.6, -0.7] | -0.1 [-1.4, +1.3] |
| stored bands, stored + 3-year ensemble fusion | R49-new t_low 90/t_high 95 | +0.074 [-0.014, +0.181] | -5.5 [-9.2, -1.5] | -0.1 [-1.6, +1.2] |

### Discrimination

Fold-stratified (pairs within the same outer fold), mean over 10 repeats, pre-event samples; Δ vs the stored score of the same modality with paired patient-bootstrap CI. Time-dependent AUROC: IPCW, sheet times, as `hf_foldstrat.py`. C-index: Harrell, fold-stratified, study or extended follow-up for non-progressors.

**H&E** (stored: AUROC sample 0.847, AUROC endoscopy (max) 0.837, td-AUROC 1 y 0.771, td-AUROC 3 y 0.788, td-AUROC 5 y 0.760, C study FU 0.755, C extended FU 0.792)

| Scheme | AUROC sample | AUROC endoscopy (max) | td-AUROC 1 y | td-AUROC 3 y | td-AUROC 5 y | C study FU | C extended FU |
|---|---|---|---|---|---|---|---|
| Cox, extended follow-up | 0.761 (-0.085 [-0.118, -0.052]) | 0.755 (-0.083 [-0.124, -0.043]) | 0.721 (-0.051 [-0.087, +0.008]) | 0.712 (-0.077 [-0.105, -0.037]) | 0.677 (-0.083 [-0.129, -0.022]) | 0.686 (-0.069 [-0.099, -0.033]) | 0.724 (-0.068 [-0.095, -0.037]) |
| Cox, study follow-up | 0.653 (-0.194 [-0.252, -0.132]) | 0.657 (-0.181 [-0.252, -0.120]) | 0.681 (-0.091 [-0.159, +0.009]) | 0.725 (-0.063 [-0.113, +0.009]) | 0.685 (-0.075 [-0.136, +0.017]) | 0.670 (-0.085 [-0.132, -0.018]) | 0.648 (-0.144 [-0.192, -0.076]) |
| Cox, pre-event samples only | 0.740 (-0.107 [-0.146, -0.069]) | 0.752 (-0.085 [-0.132, -0.041]) | 0.680 (-0.091 [-0.152, -0.005]) | 0.670 (-0.119 [-0.158, -0.064]) | 0.632 (-0.129 [-0.191, -0.051]) | 0.646 (-0.110 [-0.144, -0.067]) | 0.698 (-0.094 [-0.125, -0.059]) |
| 3-year horizon binary | 0.784 (-0.063 [-0.105, -0.022]) | 0.776 (-0.062 [-0.104, -0.023]) | 0.777 (+0.006 [-0.030, +0.058]) | 0.801 (+0.013 [-0.012, +0.051]) | 0.771 (+0.011 [-0.028, +0.080]) | 0.759 (+0.004 [-0.018, +0.040]) | 0.760 (-0.032 [-0.061, +0.005]) |
| 5-year horizon binary | 0.809 (-0.038 [-0.070, -0.011]) | 0.792 (-0.045 [-0.080, -0.013]) | 0.755 (-0.017 [-0.036, +0.018]) | 0.787 (-0.001 [-0.022, +0.031]) | 0.746 (-0.014 [-0.044, +0.038]) | 0.742 (-0.013 [-0.030, +0.016]) | 0.769 (-0.023 [-0.046, +0.003]) |
| certainty-weighted binary | 0.848 (+0.002 [-0.008, +0.011]) | 0.834 (-0.004 [-0.017, +0.007]) | 0.772 (+0.001 [-0.020, +0.021]) | 0.791 (+0.002 [-0.006, +0.012]) | 0.761 (+0.001 [-0.013, +0.020]) | 0.755 (-0.001 [-0.009, +0.009]) | 0.793 (+0.001 [-0.007, +0.009]) |
| strongly weighted binary | 0.829 (-0.018 [-0.036, -0.002]) | 0.816 (-0.022 [-0.047, -0.002]) | 0.761 (-0.010 [-0.032, +0.024]) | 0.783 (-0.006 [-0.019, +0.013]) | 0.747 (-0.013 [-0.043, +0.022]) | 0.744 (-0.011 [-0.027, +0.007]) | 0.781 (-0.011 [-0.025, +0.004]) |
| Cox H&E + stored copy number | 0.761 (-0.085 [-0.118, -0.052]) | 0.755 (-0.083 [-0.124, -0.043]) | 0.721 (-0.051 [-0.087, +0.008]) | 0.712 (-0.077 [-0.105, -0.037]) | 0.677 (-0.083 [-0.129, -0.022]) | 0.686 (-0.069 [-0.099, -0.033]) | 0.724 (-0.068 [-0.095, -0.037]) |
| Cox (pre-event) H&E + stored copy number | 0.740 (-0.107 [-0.146, -0.069]) | 0.752 (-0.085 [-0.132, -0.041]) | 0.680 (-0.091 [-0.152, -0.005]) | 0.670 (-0.119 [-0.158, -0.064]) | 0.632 (-0.129 [-0.191, -0.051]) | 0.646 (-0.110 [-0.144, -0.067]) | 0.698 (-0.094 [-0.125, -0.059]) |
| stored H&E + Cox copy number | 0.847 (0.000 [0.000, 0.000]) | 0.837 (0.000 [0.000, 0.000]) | 0.771 (0.000 [0.000, 0.000]) | 0.788 (0.000 [0.000, 0.000]) | 0.760 (0.000 [0.000, 0.000]) | 0.755 (0.000 [0.000, 0.000]) | 0.792 (0.000 [0.000, 0.000]) |
| weighted H&E + stored copy number | 0.848 (+0.002 [-0.008, +0.011]) | 0.834 (-0.004 [-0.017, +0.007]) | 0.772 (+0.001 [-0.020, +0.021]) | 0.791 (+0.002 [-0.006, +0.012]) | 0.761 (+0.001 [-0.013, +0.020]) | 0.755 (-0.001 [-0.009, +0.009]) | 0.793 (+0.001 [-0.007, +0.009]) |
| 5-year H&E + stored copy number | 0.809 (-0.038 [-0.070, -0.011]) | 0.792 (-0.045 [-0.080, -0.013]) | 0.755 (-0.017 [-0.036, +0.018]) | 0.787 (-0.001 [-0.022, +0.031]) | 0.746 (-0.014 [-0.044, +0.038]) | 0.742 (-0.013 [-0.030, +0.016]) | 0.769 (-0.023 [-0.046, +0.003]) |
| stored + Cox ensemble | 0.824 (-0.023 [-0.037, -0.009]) | 0.817 (-0.021 [-0.043, -0.007]) | 0.762 (-0.010 [-0.029, +0.017]) | 0.767 (-0.022 [-0.036, -0.003]) | 0.736 (-0.024 [-0.046, +0.005]) | 0.737 (-0.019 [-0.032, -0.001]) | 0.774 (-0.018 [-0.030, -0.003]) |
| stored + 3-year ensemble | 0.837 (-0.010 [-0.026, +0.007]) | 0.831 (-0.006 [-0.029, +0.007]) | 0.782 (+0.011 [-0.007, +0.040]) | 0.803 (+0.015 [+0.002, +0.035]) | 0.776 (+0.015 [-0.004, +0.054]) | 0.767 (+0.011 [+0.001, +0.033]) | 0.792 (-0.000 [-0.012, +0.018]) |
| stored + 5-year ensemble | 0.840 (-0.007 [-0.022, +0.006]) | 0.828 (-0.009 [-0.029, +0.003]) | 0.768 (-0.003 [-0.014, +0.017]) | 0.796 (+0.007 [-0.003, +0.024]) | 0.761 (+0.001 [-0.016, +0.028]) | 0.756 (0.000 [-0.009, +0.016]) | 0.789 (-0.003 [-0.014, +0.011]) |
| stored + strongly weighted ensemble | 0.845 (-0.002 [-0.009, +0.006]) | 0.836 (-0.001 [-0.013, +0.007]) | 0.771 (-0.000 [-0.014, +0.020]) | 0.792 (+0.004 [-0.003, +0.013]) | 0.758 (-0.002 [-0.016, +0.013]) | 0.755 (-0.000 [-0.007, +0.009]) | 0.792 (0.000 [-0.006, +0.008]) |
| stored bands, 3-year fusion | 0.847 (0.000 [0.000, 0.000]) | 0.837 (0.000 [0.000, 0.000]) | 0.771 (0.000 [0.000, 0.000]) | 0.788 (0.000 [0.000, 0.000]) | 0.760 (0.000 [0.000, 0.000]) | 0.755 (0.000 [0.000, 0.000]) | 0.792 (0.000 [0.000, 0.000]) |
| stored bands, 5-year fusion | 0.847 (0.000 [0.000, 0.000]) | 0.837 (0.000 [0.000, 0.000]) | 0.771 (0.000 [0.000, 0.000]) | 0.788 (0.000 [0.000, 0.000]) | 0.760 (0.000 [0.000, 0.000]) | 0.755 (0.000 [0.000, 0.000]) | 0.792 (0.000 [0.000, 0.000]) |
| stored bands, stored + 3-year ensemble fusion | 0.847 (0.000 [0.000, 0.000]) | 0.837 (0.000 [0.000, 0.000]) | 0.771 (0.000 [0.000, 0.000]) | 0.788 (0.000 [0.000, 0.000]) | 0.760 (0.000 [0.000, 0.000]) | 0.755 (0.000 [0.000, 0.000]) | 0.792 (0.000 [0.000, 0.000]) |

**Copy number** (stored: AUROC sample 0.801, AUROC endoscopy (max) 0.811, td-AUROC 1 y 0.811, td-AUROC 3 y 0.767, td-AUROC 5 y 0.779, C study FU 0.748, C extended FU 0.767)

| Scheme | AUROC sample | AUROC endoscopy (max) | td-AUROC 1 y | td-AUROC 3 y | td-AUROC 5 y | C study FU | C extended FU |
|---|---|---|---|---|---|---|---|
| Cox, extended follow-up | 0.722 (-0.079 [-0.150, -0.022]) | 0.725 (-0.086 [-0.153, -0.025]) | 0.753 (-0.057 [-0.152, +0.034]) | 0.746 (-0.022 [-0.080, +0.041]) | 0.757 (-0.021 [-0.081, +0.043]) | 0.723 (-0.024 [-0.074, +0.027]) | 0.710 (-0.057 [-0.110, -0.004]) |
| Cox, study follow-up | 0.657 (-0.145 [-0.230, -0.075]) | 0.660 (-0.151 [-0.248, -0.077]) | 0.687 (-0.124 [-0.296, +0.023]) | 0.737 (-0.030 [-0.110, +0.052]) | 0.753 (-0.026 [-0.092, +0.057]) | 0.699 (-0.049 [-0.112, +0.020]) | 0.654 (-0.113 [-0.183, -0.041]) |
| Cox, pre-event samples only | 0.721 (-0.080 [-0.136, -0.029]) | 0.742 (-0.069 [-0.123, -0.025]) | 0.731 (-0.080 [-0.128, -0.024]) | 0.726 (-0.042 [-0.091, +0.023]) | 0.726 (-0.052 [-0.105, -0.002]) | 0.692 (-0.055 [-0.095, -0.006]) | 0.702 (-0.066 [-0.107, -0.020]) |
| 3-year horizon binary | 0.790 (-0.011 [-0.060, +0.033]) | 0.789 (-0.022 [-0.069, +0.023]) | 0.826 (+0.016 [-0.053, +0.073]) | 0.801 (+0.033 [-0.008, +0.081]) | 0.803 (+0.024 [-0.022, +0.065]) | 0.769 (+0.022 [-0.015, +0.061]) | 0.768 (+0.001 [-0.035, +0.042]) |
| 5-year horizon binary | 0.797 (-0.005 [-0.035, +0.026]) | 0.812 (+0.001 [-0.027, +0.030]) | 0.810 (-0.000 [-0.019, +0.022]) | 0.779 (+0.011 [-0.021, +0.053]) | 0.798 (+0.019 [-0.008, +0.050]) | 0.755 (+0.008 [-0.021, +0.038]) | 0.772 (+0.005 [-0.018, +0.033]) |
| certainty-weighted binary | 0.804 (+0.003 [-0.009, +0.015]) | 0.816 (+0.005 [-0.009, +0.018]) | 0.817 (+0.007 [-0.004, +0.018]) | 0.776 (+0.009 [-0.004, +0.024]) | 0.789 (+0.010 [-0.002, +0.024]) | 0.754 (+0.007 [-0.005, +0.018]) | 0.772 (+0.005 [-0.004, +0.016]) |
| strongly weighted binary | 0.810 (+0.009 [-0.009, +0.028]) | 0.822 (+0.011 [-0.012, +0.027]) | 0.824 (+0.013 [-0.003, +0.027]) | 0.786 (+0.019 [+0.003, +0.041]) | 0.801 (+0.022 [+0.002, +0.047]) | 0.764 (+0.017 [+0.003, +0.032]) | 0.779 (+0.012 [0.000, +0.027]) |
| Cox H&E + stored copy number | 0.801 (0.000 [0.000, 0.000]) | 0.811 (0.000 [0.000, 0.000]) | 0.811 (0.000 [0.000, 0.000]) | 0.767 (0.000 [0.000, 0.000]) | 0.779 (0.000 [0.000, 0.000]) | 0.748 (0.000 [0.000, 0.000]) | 0.767 (0.000 [0.000, 0.000]) |
| Cox (pre-event) H&E + stored copy number | 0.801 (0.000 [0.000, 0.000]) | 0.811 (0.000 [0.000, 0.000]) | 0.811 (0.000 [0.000, 0.000]) | 0.767 (0.000 [0.000, 0.000]) | 0.779 (0.000 [0.000, 0.000]) | 0.748 (0.000 [0.000, 0.000]) | 0.767 (0.000 [0.000, 0.000]) |
| stored H&E + Cox copy number | 0.722 (-0.079 [-0.150, -0.022]) | 0.725 (-0.086 [-0.153, -0.025]) | 0.753 (-0.057 [-0.152, +0.034]) | 0.746 (-0.022 [-0.080, +0.041]) | 0.757 (-0.021 [-0.081, +0.043]) | 0.723 (-0.024 [-0.074, +0.027]) | 0.710 (-0.057 [-0.110, -0.004]) |
| weighted H&E + stored copy number | 0.801 (0.000 [0.000, 0.000]) | 0.811 (0.000 [0.000, 0.000]) | 0.811 (0.000 [0.000, 0.000]) | 0.767 (0.000 [0.000, 0.000]) | 0.779 (0.000 [0.000, 0.000]) | 0.748 (0.000 [0.000, 0.000]) | 0.767 (0.000 [0.000, 0.000]) |
| 5-year H&E + stored copy number | 0.801 (0.000 [0.000, 0.000]) | 0.811 (0.000 [0.000, 0.000]) | 0.811 (0.000 [0.000, 0.000]) | 0.767 (0.000 [0.000, 0.000]) | 0.779 (0.000 [0.000, 0.000]) | 0.748 (0.000 [0.000, 0.000]) | 0.767 (0.000 [0.000, 0.000]) |
| stored + Cox ensemble | 0.782 (-0.020 [-0.056, +0.010]) | 0.785 (-0.026 [-0.063, +0.002]) | 0.812 (+0.001 [-0.028, +0.038]) | 0.780 (+0.012 [-0.013, +0.042]) | 0.784 (+0.005 [-0.025, +0.034]) | 0.755 (+0.007 [-0.014, +0.029]) | 0.756 (-0.011 [-0.036, +0.014]) |
| stored + 3-year ensemble | 0.810 (+0.009 [-0.013, +0.031]) | 0.816 (+0.005 [-0.020, +0.025]) | 0.826 (+0.015 [-0.015, +0.042]) | 0.794 (+0.027 [+0.002, +0.053]) | 0.804 (+0.025 [-0.003, +0.050]) | 0.768 (+0.021 [+0.001, +0.042]) | 0.780 (+0.013 [-0.005, +0.033]) |
| stored + 5-year ensemble | 0.806 (+0.004 [-0.011, +0.020]) | 0.818 (+0.007 [-0.009, +0.020]) | 0.815 (+0.004 [-0.007, +0.018]) | 0.778 (+0.010 [-0.005, +0.030]) | 0.794 (+0.016 [0.000, +0.031]) | 0.756 (+0.008 [-0.006, +0.023]) | 0.776 (+0.008 [-0.003, +0.022]) |
| stored + strongly weighted ensemble | 0.808 (+0.007 [-0.001, +0.016]) | 0.819 (+0.008 [-0.004, +0.015]) | 0.819 (+0.008 [0.000, +0.016]) | 0.778 (+0.011 [+0.003, +0.020]) | 0.793 (+0.015 [+0.004, +0.026]) | 0.758 (+0.010 [+0.003, +0.018]) | 0.776 (+0.008 [+0.002, +0.015]) |
| stored bands, 3-year fusion | 0.801 (0.000 [0.000, 0.000]) | 0.811 (0.000 [0.000, 0.000]) | 0.811 (0.000 [0.000, 0.000]) | 0.767 (0.000 [0.000, 0.000]) | 0.779 (0.000 [0.000, 0.000]) | 0.748 (0.000 [0.000, 0.000]) | 0.767 (0.000 [0.000, 0.000]) |
| stored bands, 5-year fusion | 0.801 (0.000 [0.000, 0.000]) | 0.811 (0.000 [0.000, 0.000]) | 0.811 (0.000 [0.000, 0.000]) | 0.767 (0.000 [0.000, 0.000]) | 0.779 (0.000 [0.000, 0.000]) | 0.748 (0.000 [0.000, 0.000]) | 0.767 (0.000 [0.000, 0.000]) |
| stored bands, stored + 3-year ensemble fusion | 0.801 (0.000 [0.000, 0.000]) | 0.811 (0.000 [0.000, 0.000]) | 0.811 (0.000 [0.000, 0.000]) | 0.767 (0.000 [0.000, 0.000]) | 0.779 (0.000 [0.000, 0.000]) | 0.748 (0.000 [0.000, 0.000]) | 0.767 (0.000 [0.000, 0.000]) |

**Fusion** (stored: AUROC sample 0.889, AUROC endoscopy (max) 0.885, td-AUROC 1 y 0.854, td-AUROC 3 y 0.831, td-AUROC 5 y 0.821, C study FU 0.800, C extended FU 0.832)

| Scheme | AUROC sample | AUROC endoscopy (max) | td-AUROC 1 y | td-AUROC 3 y | td-AUROC 5 y | C study FU | C extended FU |
|---|---|---|---|---|---|---|---|
| Cox, extended follow-up | 0.806 (-0.082 [-0.138, -0.037]) | 0.801 (-0.084 [-0.134, -0.032]) | 0.813 (-0.041 [-0.104, +0.046]) | 0.786 (-0.045 [-0.092, +0.004]) | 0.772 (-0.049 [-0.111, +0.014]) | 0.756 (-0.043 [-0.089, +0.004]) | 0.774 (-0.058 [-0.100, -0.018]) |
| Cox, study follow-up | 0.699 (-0.189 [-0.251, -0.133]) | 0.698 (-0.188 [-0.264, -0.125]) | 0.749 (-0.105 [-0.193, +0.017]) | 0.794 (-0.038 [-0.085, +0.033]) | 0.782 (-0.039 [-0.090, +0.027]) | 0.741 (-0.059 [-0.106, +0.003]) | 0.697 (-0.134 [-0.182, -0.071]) |
| Cox, pre-event samples only | 0.801 (-0.088 [-0.131, -0.049]) | 0.814 (-0.071 [-0.119, -0.029]) | 0.765 (-0.089 [-0.158, +0.013]) | 0.746 (-0.085 [-0.136, -0.029]) | 0.724 (-0.098 [-0.159, -0.034]) | 0.713 (-0.087 [-0.134, -0.040]) | 0.756 (-0.075 [-0.114, -0.039]) |
| 3-year horizon binary | 0.859 (-0.029 [-0.061, -0.003]) | 0.848 (-0.037 [-0.074, -0.008]) | 0.860 (+0.006 [-0.031, +0.048]) | 0.859 (+0.028 [-0.004, +0.069]) | 0.850 (+0.028 [-0.004, +0.078]) | 0.814 (+0.014 [-0.006, +0.042]) | 0.824 (-0.007 [-0.029, +0.020]) |
| 5-year horizon binary | 0.870 (-0.018 [-0.042, +0.004]) | 0.871 (-0.015 [-0.043, +0.010]) | 0.839 (-0.015 [-0.040, +0.019]) | 0.836 (+0.004 [-0.021, +0.034]) | 0.824 (+0.003 [-0.030, +0.043]) | 0.797 (-0.003 [-0.025, +0.022]) | 0.826 (-0.006 [-0.023, +0.014]) |
| certainty-weighted binary | 0.891 (+0.002 [-0.005, +0.010]) | 0.888 (+0.003 [-0.004, +0.015]) | 0.859 (+0.005 [-0.011, +0.018]) | 0.835 (+0.003 [-0.007, +0.013]) | 0.827 (+0.006 [-0.008, +0.021]) | 0.802 (+0.002 [-0.006, +0.010]) | 0.835 (+0.004 [-0.003, +0.010]) |
| strongly weighted binary | 0.882 (-0.007 [-0.024, +0.010]) | 0.877 (-0.009 [-0.026, +0.015]) | 0.856 (+0.002 [-0.024, +0.033]) | 0.833 (+0.002 [-0.017, +0.022]) | 0.821 (-0.001 [-0.031, +0.033]) | 0.798 (-0.001 [-0.017, +0.016]) | 0.832 (0.000 [-0.012, +0.014]) |
| Cox H&E + stored copy number | 0.852 (-0.036 [-0.064, -0.012]) | 0.850 (-0.036 [-0.078, -0.005]) | 0.846 (-0.008 [-0.041, +0.042]) | 0.791 (-0.041 [-0.071, -0.011]) | 0.783 (-0.038 [-0.080, +0.003]) | 0.767 (-0.033 [-0.062, -0.007]) | 0.803 (-0.029 [-0.052, -0.008]) |
| Cox (pre-event) H&E + stored copy number | 0.834 (-0.054 [-0.084, -0.026]) | 0.851 (-0.035 [-0.081, -0.006]) | 0.817 (-0.037 [-0.077, +0.028]) | 0.763 (-0.069 [-0.105, -0.027]) | 0.756 (-0.065 [-0.119, -0.014]) | 0.741 (-0.059 [-0.090, -0.027]) | 0.784 (-0.048 [-0.074, -0.023]) |
| stored H&E + Cox copy number | 0.867 (-0.022 [-0.054, +0.006]) | 0.860 (-0.025 [-0.049, +0.009]) | 0.839 (-0.015 [-0.065, +0.045]) | 0.837 (+0.006 [-0.025, +0.038]) | 0.823 (+0.001 [-0.033, +0.034]) | 0.803 (+0.003 [-0.024, +0.030]) | 0.821 (-0.011 [-0.036, +0.013]) |
| weighted H&E + stored copy number | 0.887 (-0.001 [-0.010, +0.006]) | 0.884 (-0.002 [-0.009, +0.010]) | 0.854 (0.000 [-0.010, +0.012]) | 0.829 (-0.002 [-0.010, +0.006]) | 0.821 (-0.000 [-0.013, +0.014]) | 0.798 (-0.002 [-0.009, +0.004]) | 0.832 (-0.000 [-0.006, +0.005]) |
| 5-year H&E + stored copy number | 0.869 (-0.020 [-0.040, -0.005]) | 0.863 (-0.023 [-0.045, -0.002]) | 0.842 (-0.012 [-0.029, +0.013]) | 0.828 (-0.004 [-0.022, +0.020]) | 0.812 (-0.009 [-0.039, +0.031]) | 0.792 (-0.008 [-0.024, +0.011]) | 0.821 (-0.011 [-0.024, +0.003]) |
| stored + Cox ensemble | 0.878 (-0.011 [-0.032, +0.007]) | 0.875 (-0.010 [-0.031, +0.011]) | 0.864 (+0.010 [-0.017, +0.057]) | 0.833 (+0.002 [-0.020, +0.024]) | 0.824 (+0.002 [-0.024, +0.024]) | 0.802 (+0.002 [-0.018, +0.024]) | 0.829 (-0.003 [-0.021, +0.014]) |
| stored + 3-year ensemble | 0.887 (-0.002 [-0.016, +0.012]) | 0.884 (-0.001 [-0.022, +0.010]) | 0.865 (+0.012 [-0.011, +0.037]) | 0.853 (+0.021 [+0.004, +0.042]) | 0.844 (+0.022 [+0.003, +0.051]) | 0.815 (+0.015 [+0.002, +0.030]) | 0.839 (+0.007 [-0.004, +0.021]) |
| stored + 5-year ensemble | 0.888 (-0.000 [-0.011, +0.010]) | 0.888 (+0.003 [-0.011, +0.016]) | 0.853 (-0.001 [-0.014, +0.014]) | 0.839 (+0.007 [-0.006, +0.022]) | 0.828 (+0.007 [-0.009, +0.026]) | 0.804 (+0.004 [-0.006, +0.016]) | 0.836 (+0.004 [-0.004, +0.013]) |
| stored + strongly weighted ensemble | 0.889 (+0.001 [-0.007, +0.009]) | 0.888 (+0.002 [-0.007, +0.014]) | 0.860 (+0.006 [-0.010, +0.025]) | 0.835 (+0.004 [-0.007, +0.014]) | 0.824 (+0.003 [-0.012, +0.017]) | 0.803 (+0.003 [-0.005, +0.011]) | 0.835 (+0.004 [-0.003, +0.010]) |
| stored bands, 3-year fusion | 0.859 (-0.029 [-0.061, -0.003]) | 0.848 (-0.037 [-0.074, -0.008]) | 0.860 (+0.006 [-0.031, +0.048]) | 0.859 (+0.028 [-0.004, +0.069]) | 0.850 (+0.028 [-0.004, +0.078]) | 0.814 (+0.014 [-0.006, +0.042]) | 0.824 (-0.007 [-0.029, +0.020]) |
| stored bands, 5-year fusion | 0.870 (-0.018 [-0.042, +0.004]) | 0.871 (-0.015 [-0.043, +0.010]) | 0.839 (-0.015 [-0.040, +0.019]) | 0.836 (+0.004 [-0.021, +0.034]) | 0.824 (+0.003 [-0.030, +0.043]) | 0.797 (-0.003 [-0.025, +0.022]) | 0.826 (-0.006 [-0.023, +0.014]) |
| stored bands, stored + 3-year ensemble fusion | 0.887 (-0.002 [-0.016, +0.012]) | 0.884 (-0.001 [-0.022, +0.010]) | 0.865 (+0.012 [-0.011, +0.037]) | 0.853 (+0.021 [+0.004, +0.042]) | 0.844 (+0.022 [+0.003, +0.051]) | 0.815 (+0.015 [+0.002, +0.030]) | 0.839 (+0.007 [-0.004, +0.021]) |

### Time-aware scores inside the round-9 memory rule

Round 9's nested engine (`rv9_falseflags.py` `run_families`, executed unchanged) with the scheme's scores swapped in: exponentially weighted mean of the patient's endoscopy scores so far (half-life 1, 2 or 4 years chosen on training patients), operating threshold = training progressor-patient detection ≥ R49's in the fold. Only probability-scale (binary) schemes, because the engine works on logits. 'Same rule, stored scores' = the identical rule on the stored predictions (reproduces round 9: EW gate 23.6 NP flagged / 30.7 caught).

| Scheme | Rule | Caught | NP flagged | Seq / patient | Δ NP flagged vs R49 | Δ caught vs R49 | Δ NP flagged vs same rule, stored | Δ caught vs same rule, stored |
|---|---|---|---|---|---|---|---|---|
| stored (control) | EW memory of the R49-aligned gate score | 30.7 | 23.6 | 1.94 | -8.2 [-11.4, -5.1] | -0.4 [-1.3, +0.4] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| stored (control) | gate score, threshold only (no memory) | 30.7 | 29.4 | 1.94 | -2.4 [-3.7, -1.3] | -0.4 [-1.2, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| stored (control) | EW memory of H&E alone | 31.2 | 32.1 | 0.00 | +0.3 [-2.7, +3.4] | +0.1 [-1.2, +1.7] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| stored + 3-year ensemble | EW memory of the R49-aligned gate score | 30.2 | 21.7 | 2.00 | -10.1 [-13.8, -6.5] | -0.9 [-2.1, +0.1] | -1.9 [-3.8, -0.3] | -0.5 [-1.4, +0.2] |
| stored + 3-year ensemble | gate score, threshold only (no memory) | 30.4 | 29.0 | 2.00 | -2.8 [-4.9, -1.0] | -0.7 [-1.9, +0.2] | -0.4 [-2.2, +1.4] | -0.3 [-1.7, +0.9] |
| stored + 3-year ensemble | EW memory of H&E alone | 30.7 | 31.6 | 0.00 | -0.2 [-3.1, +2.8] | -0.4 [-1.9, +1.1] | -0.5 [-2.1, +1.2] | -0.5 [-0.9, -0.1] |
| stored + strongly weighted ensemble | EW memory of the R49-aligned gate score | 30.7 | 24.2 | 1.99 | -7.6 [-10.7, -4.7] | -0.4 [-1.6, +0.7] | +0.6 [-1.0, +2.1] | 0.0 [-0.7, +0.7] |
| stored + strongly weighted ensemble | gate score, threshold only (no memory) | 30.7 | 28.6 | 1.99 | -3.2 [-4.9, -1.7] | -0.4 [-1.4, +0.3] | -0.8 [-2.3, +0.7] | 0.0 [-0.5, +0.6] |
| stored + strongly weighted ensemble | EW memory of H&E alone | 31.4 | 33.9 | 0.00 | +2.1 [-1.1, +5.4] | +0.3 [-1.1, +2.0] | +1.8 [+0.6, +3.3] | +0.2 [-0.2, +0.6] |
| stored bands, stored + 3-year ensemble fusion | EW memory of the R49-aligned gate score | 30.5 | 22.8 | 1.94 | -9.0 [-12.1, -5.9] | -0.6 [-1.7, +0.4] | -0.8 [-1.7, +0.1] | -0.2 [-0.9, +0.4] |
| stored bands, stored + 3-year ensemble fusion | gate score, threshold only (no memory) | 30.4 | 28.8 | 1.94 | -3.0 [-4.9, -1.2] | -0.7 [-1.8, 0.0] | -0.6 [-2.1, +1.0] | -0.3 [-1.2, +0.3] |
| stored bands, stored + 3-year ensemble fusion | EW memory of H&E alone | 30.9 | 31.7 | 0.00 | -0.1 [-3.3, +2.9] | -0.2 [-1.6, +1.2] | -0.4 [-1.3, +0.4] | -0.3 [-0.7, 0.0] |
| certainty-weighted binary | EW memory of the R49-aligned gate score | 30.6 | 24.9 | 2.06 | -6.9 [-10.0, -4.0] | -0.5 [-1.5, +0.5] | +1.3 [-0.5, +3.0] | -0.1 [-0.8, +0.6] |
| certainty-weighted binary | gate score, threshold only (no memory) | 30.7 | 28.8 | 2.06 | -3.0 [-4.6, -1.4] | -0.4 [-1.7, +0.7] | -0.6 [-2.2, +1.1] | 0.0 [-0.9, +1.1] |
| certainty-weighted binary | EW memory of H&E alone | 31.4 | 34.1 | 0.00 | +2.3 [-0.7, +5.7] | +0.3 [-1.1, +2.0] | +2.0 [+0.6, +3.7] | +0.2 [-0.2, +0.6] |
| weighted H&E + stored copy number | EW memory of the R49-aligned gate score | 30.5 | 24.1 | 2.06 | -7.7 [-10.8, -4.8] | -0.6 [-1.5, +0.2] | +0.5 [-0.9, +1.8] | -0.2 [-1.0, +0.7] |
| weighted H&E + stored copy number | gate score, threshold only (no memory) | 30.3 | 28.6 | 2.06 | -3.2 [-5.0, -1.6] | -0.8 [-1.9, 0.0] | -0.8 [-2.4, +0.9] | -0.4 [-1.1, +0.2] |
| weighted H&E + stored copy number | EW memory of H&E alone | 31.2 | 34.2 | 0.00 | +2.4 [-0.6, +5.8] | +0.1 [-1.5, +1.9] | +2.1 [+0.7, +3.7] | 0.0 [-0.5, +0.4] |

### Apparent (non-nested) numbers: OPTIMISTIC

P1-new with the 90% endoscopy-sensitivity threshold set on the evaluated (held-out) endoscopies themselves, per repeat. Optimistic by construction; not a deployable rule.

| Scheme | Caught | NP flagged | Endo sens / spec |
|---|---|---|---|
| stored (control) | 31.4 | 36.8 | 0.909 / 0.482 |
| Cox, extended follow-up | 31.2 | 40.1 | 0.909 / 0.346 |
| Cox, study follow-up | 32.0 | 42.5 | 0.909 / 0.196 |
| Cox, pre-event samples only | 31.1 | 40.3 | 0.909 / 0.306 |
| 3-year horizon binary | 31.7 | 42.1 | 0.909 / 0.297 |
| 5-year horizon binary | 31.2 | 40.3 | 0.909 / 0.390 |
| certainty-weighted binary | 31.5 | 37.5 | 0.909 / 0.494 |
| strongly weighted binary | 31.8 | 38.4 | 0.909 / 0.477 |
| Cox H&E + stored copy number | 31.2 | 40.1 | 0.909 / 0.346 |
| Cox (pre-event) H&E + stored copy number | 31.1 | 40.3 | 0.909 / 0.306 |
| stored H&E + Cox copy number | 31.4 | 36.8 | 0.909 / 0.482 |
| weighted H&E + stored copy number | 31.5 | 37.5 | 0.909 / 0.494 |
| 5-year H&E + stored copy number | 31.2 | 40.3 | 0.909 / 0.390 |
| stored + Cox ensemble | 31.1 | 38.8 | 0.909 / 0.448 |
| stored + 3-year ensemble | 31.8 | 37.5 | 0.909 / 0.478 |
| stored + 5-year ensemble | 31.4 | 38.5 | 0.909 / 0.479 |
| stored + strongly weighted ensemble | 31.4 | 36.9 | 0.909 / 0.506 |
| stored bands, 3-year fusion | 31.4 | 36.8 | 0.909 / 0.482 |
| stored bands, 5-year fusion | 31.4 | 36.8 | 0.909 / 0.482 |
| stored bands, stored + 3-year ensemble fusion | 31.4 | 36.8 | 0.909 / 0.482 |

Fitted models (outer fits, median over 100 repeat × fold): λ, non-zero coefficients, training samples used.

| Fit | λ | Non-zero coefficients | Training samples |
|---|---|---|---|
| coxp_cnv | 0.046 | 28.0 | 512.0 |
| coxp_img | 0.052 | 33.0 | 512.0 |
| coxs_cnv | 0.061 | 29.0 | 608.0 |
| coxs_img | 0.04 | 54.0 | 608.0 |
| coxx_cnv | 0.044 | 39.0 | 608.0 |
| coxx_img | 0.036 | 60.0 | 608.0 |
| h3_cnv | 0.005 | 84.0 | 493.0 |
| h3_img | 0.003 | 120.0 | 493.0 |
| h5_cnv | 0.007 | 83.0 | 497.0 |
| h5_img | 0.005 | 120.0 | 497.0 |
| wt2_cnv | 0.008 | 72.0 | 608.0 |
| wt2_img | 0.007 | 100.0 | 608.0 |
| wt_cnv | 0.008 | 71.0 | 608.0 |
| wt_img | 0.005 | 121.0 | 608.0 |

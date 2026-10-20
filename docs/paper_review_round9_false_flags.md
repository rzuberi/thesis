# Round 9: methods to reduce false flags in non-progressors

Status: EXPLORATORY PLAN (written 2026-10-20). The authors' instruction is to search widely for anything that reduces false flags. Nothing is confirmatory, and the plan may be extended while running; every extension is listed under "Implementation notes". Every method is still evaluated on held-out patients (outer folds), so that findings reflect performance on new patients. Results are appended under the line at the end.

## Why

**The problem.** The R49 gate is the main rule (`docs/paper_review_round8b_step3.md`, c39fd82). It catches 31.1 of 32 progressor patients but flags 31.8 of 43 non-progressor patients at least once. Every endoscopy is judged without memory of the patient's earlier endoscopies, and non-progressors have about twice as many endoscopies, so false flags accumulate.

**What this round does.** It tests methods that reduce non-progressor patients ever flagged without losing progressors:
- **Group A:** re-scoring the stored predictions;
- **Group B:** small models fitted on stored out-of-fold predictions, plus two refits.

The main rule is not changed by this round. A method that succeeds becomes a candidate to register for external testing in a cohort with repeat endoscopies, and it is reported as post hoc. ACE-B (mostly one endoscopy per patient) cannot test the longitudinal methods.

No ACE-B file is read. Frozen bundles and stored predictions are unchanged. Population and conventions as in round 8: 571 pre-event samples, 288 endoscopies, 75 patients (32 progressors); patient bootstrap, 2,000 draws, `RandomState(0)`; single model averaged over 10 repeats; exact dates from `pre_event_cohort.Date`.

## F0. Are flagged non-progressors more likely to show later dysplasia? (descriptive)

**Later disease** = the highest Barrett's database confirmed grade after the last sequenced endoscopy (as round-7 lookup B2): IND, LGD or HGD.

**Rules:** R49, P1 at 90% and P3 at 90%.

**Analysis.** For each rule, cross-tabulate non-progressor patients by ever flagged (in at least 5 of 10 repeats) against later IND+ and LGD+. Report the counts, Fisher p and the share with any later record. Also flags per patient-year by later-grade group.

The 7 non-progressors with no later record are a separate row.

## Common evaluation for every method

1. **Patient-level primary outcome:** non-progressor patients ever flagged (of 43) at matched progressor patients caught.
2. **The method's operating threshold:** chosen per outer fold on the training patients' inner out-of-fold predictions by a fixed rule: the highest threshold at which training progressor-patient detection ≥ the R49 gate's own training-patient detection in that fold.
3. **Contrasts against R49,** with paired patient-bootstrap 95% CIs:
   - Δ non-progressor patients ever flagged;
   - Δ progressor patients caught;
   - Δ flagged non-progressor endoscopies per patient-year;
   - Δ endoscopy specificity;
   - Δ samples sequenced per patient.

   The same contrasts against P1 at 90% are also reported.
4. **Evaluation-matched version:** the threshold set on the evaluation patients so that progressor patients caught equals R49's.
5. **Ranking, not a gate.** Methods are ranked by Δ non-progressor patients flagged at Δ progressor patients caught ≥ −0.5 (point estimate). 95% CIs are reported, and Bonferroni-adjusted 99.2% CIs alongside for reference. Anything promising is kept, whatever its interval.
6. **Hyper-parameters** within a method family are chosen inside the inner cross-validation by the same rule (lowest training non-progressor patients flagged subject to the detection constraint). Every grid point's apparent result is also reported, labelled optimistic.

## Group A: decision rules on stored predictions

**A1. Memory (patient running score).** At each endoscopy, the patient's score combines all their pre-event endoscopies so far:
- (a) mean of endoscopy-max logit L-IMG;
- (b) exponentially weighted, half-life 1, 2 or 4 years;
- (c) persistence: flag if the current and previous endoscopies are both ≥ t, or the current one is ≥ t_high (first endoscopy: t_high only).

These are applied to H&E alone and to the gate (memory over the gate's endoscopy score, with the middle band's sequenced logit L-LATE replacing L-IMG for that endoscopy).

**A2. Copy-number low-risk certificate.** After an endoscopy whose sequenced sample has L-CNV below `t_quiet`, raise that patient's H&E threshold by Δ for Y years. Built on the gate.

| Parameter | Grid |
|---|---|
| `t_quiet` | training non-progressor 50th or 75th percentile |
| Δ | to the 85% or 95% training-specificity threshold |
| Y | 2 or 4 years |

**A3. Agreement within an endoscopy.** A high-band (gate) or H&E-alone flag requires the second-highest sample of the endoscopy to be ≥ t_mid as well. Otherwise the top sample is sequenced and the flag stands only if its L-CNV ≥ the copy-number-only threshold. Endoscopies with one sample follow the gate.

## Group B: models on stored out-of-fold predictions, and two refits

**B1. Stacked endoscopy score (no refit).** A logistic regression fitted per outer fold on the training patients' inner out-of-fold predictions. It is applied as a gate replacement (same structure: low / sequence top sample / high).
- **Inputs:** endoscopy-max logit L-IMG, grade at the endoscopy (ID/LGD indicator), age, sex.
- **In the middle band:** also the top sample's logit L-CNV.
- **Excluded:** the number of prior endoscopies and time in surveillance, which are artefacts of this cohort's sampling design and would not transfer.

**B2. B1 combined with memory.** The A1(b) weighting applied to the B1 score.

**B3. Abstention.** In the middle band, if the sequenced call's L-LATE lies within ±ε of `t_seq`, the endoscopy is "indeterminate, usual interval" (not flagged). ε is set so that 10% or 20% of training middle-band endoscopies are indeterminate. Reported with the number of indeterminate endoscopies; progressor endoscopies made indeterminate count as missed.

**B4. Refits of the H&E model (refit pipeline as `rv4_refit.R` and `rv7_refit.R`, same folds and λ rule).**
- (a) Class-weighted training: non-progressor weight 2.
- (b) Training on NDBE samples only.

The gate is then rebuilt from the refitted L-IMG with the same cut-off rules. These are the only refits in this round.

Deeper (4×) copy number is registered separately (R58) and is not part of this round.

## Robustness of the most promising methods (top 3 by the ranking)

The R49 robustness rows that are re-scorable for that method:
- NDBE endoscopies;
- endoscopies with ≥ 2 samples;
- tissue strata;
- R52(a);
- between-repeat variance;
- refit bootstrap where the arrays exist.

## Scripts and running

- **Scripts:** `scripts/paper_plan/rv9_falseflags.py` (A, B1–B3, F0) and `scripts/paper_plan/rv9_refit.R` (B4), reusing round 7–8 helpers.
- **Execution:** cluster jobs via `campaign.sh`, prefix `rv9`.
- **Outputs:** aggregates to `results/paper_final/review_round9/`; results appended below by `rv9_render.py`. Figures go to `paper/figures_r9/` (not committed).

---

## Results

Rendered by `scripts/paper_plan/rv9_render.py` from `results/paper_final/review_round9/` (aggregate results 940f28f); scripts `rv9_falseflags.py` (everything except B4 fitting), `rv9_later.py` (F0 input), `rv9_refit.R` (B4 refits); figures by `rv9_figs.py` (local, not committed). **This round is exploratory: every number is a post hoc finding, nothing is adjusted for the many methods tried, and no method replaces R49.** Single model = per-repeat values averaged over the 10 repeats. Intervals: paired patient bootstrap, 2,000 draws (`RandomState(0)`); the 99.2% interval (Bonferroni over 6 method families) is shown for reference. No ACE-B file was read; frozen bundles and stored predictions are unchanged; only B4 refits the H&E model (`rv9_refit.R`).

Check (round-8 settings, observed): R49 31.1 caught / 31.8 NP flagged; P1 90% 31.1 / 36.0 (expected 31.1 / 31.8 and 31.1 / 36.0); reproduced: yes. Refit reproduction (`rv9_refit.R` with weight 1 and all rows against the stored predictions): outer repeat 1 max |difference| 0.0e+00, inner repeat 1 fold 1 0.0e+00; passed: yes.

### F0. Are flagged non-progressors more likely to show later dysplasia? (descriptive)

Later disease = highest Barrett's database confirmed grade after the last sequenced endoscopy (round-7 lookup B2: records > 14 days after the latest exact sample date); IND, LGD, HGD+. 'ever flagged' = flagged at >= 1 pre-event endoscopy in >= 5 of 10 repeats (stored held-out predictions); rates = flagged non-progressor endoscopies (mean over repeats) per patient-year (first sequenced endoscopy to last sequenced endoscopy); groups < 5 patients shown as '<5'. Non-progressor patients: 43. Group sizes: later HGD or worse <5; later IND <5; later LGD <5; later NDBE only 24; no later database record 7; records after, none with a confirmed grade 5.

| Rule | NP ever flagged (≥ 5 of 10 repeats) | Population | Outcome | Flagged: later / not | Not flagged: later / not | Share later: flagged vs not flagged | Fisher p |
|---|---|---|---|---|---|---|---|
| R49 | 31 | all 43 | later IND or worse | 5 / 26 | <5 / 10 | 0.161 vs <5 | 1.0 |
| R49 | 31 | all 43 | later LGD or worse | <5 / 28 | <5 / 11 | <5 vs <5 | 1.0 |
| R49 | 31 | with any later record | later IND or worse | 5 / 20 | <5 / 9 | 0.2 vs <5 | 1.0 |
| R49 | 31 | with any later record | later LGD or worse | <5 / 22 | <5 / 10 | <5 vs <5 | 1.0 |
| R49 | 31 | all 43 | any later database record | 25 / 6 | 11 / <5 | 0.806 vs 0.917 | 0.652 |
| P1 90% | 36 | all 43 | later IND or worse | 6 / 30 | <5 / 6 | 0.167 vs <5 | 1.0 |
| P1 90% | 36 | all 43 | later LGD or worse | <5 / 32 | 0 / 7 | <5 vs 0.0 | 1.0 |
| P1 90% | 36 | with any later record | later IND or worse | 6 / 23 | <5 / 6 | 0.207 vs <5 | 1.0 |
| P1 90% | 36 | with any later record | later LGD or worse | <5 / 25 | 0 / 7 | <5 vs 0.0 | 0.566 |
| P1 90% | 36 | all 43 | any later database record | 29 / 7 | 7 / 0 | 0.806 vs 1.0 | 0.577 |
| P3 90% | 31 | all 43 | later IND or worse | 6 / 25 | <5 / 11 | 0.194 vs <5 | 0.652 |
| P3 90% | 31 | all 43 | later LGD or worse | <5 / 28 | <5 / 11 | <5 vs <5 | 1.0 |
| P3 90% | 31 | with any later record | later IND or worse | 6 / 19 | <5 / 10 | 0.24 vs <5 | 0.4 |
| P3 90% | 31 | with any later record | later LGD or worse | <5 / 22 | <5 / 10 | <5 vs <5 | 1.0 |
| P3 90% | 31 | all 43 | any later database record | 25 / 6 | 11 / <5 | 0.806 vs 0.917 | 0.652 |

Flagged non-progressor endoscopies per patient-year by later-grade group (groups below 5 patients: '<5'):

| Rule | no later database record | records after, none with a confirmed grade | later NDBE only | later IND or worse | later LGD or worse |
|---|---|---|---|---|---|
| R49 | 0.506 (n = 7) | 0.273 (n = 5) | 0.284 (n = 24) | 0.291 (n = 7) | <5 (n = <5) |
| P1 90% | 0.501 (n = 7) | 0.305 (n = 5) | 0.302 (n = 24) | 0.369 (n = 7) | <5 (n = <5) |
| P3 90% | 0.565 (n = 7) | 0.234 (n = 5) | 0.284 (n = 24) | 0.315 (n = 7) | <5 (n = <5) |

### Per-patient intraclass correlation of endoscopy scores (before the memory rules)

| Score | Class | ICC(1) [95% CI] | Between-patient MS | Within-patient MS | Patients / endoscopies |
|---|---|---|---|---|---|
| logit max L-IMG | non-progressor | 0.22 [0.16, 0.26] | 9.57 | 4.16 | 43 / 200 |
| logit max L-IMG | progressor | 0.59 [0.52, 0.64] | 25.75 | 5.17 | 32 / 88 |
| gate score, literal | non-progressor | 0.28 [0.22, 0.31] | 10.43 | 3.78 | 43 / 200 |
| gate score, literal | progressor | 0.60 [0.52, 0.64] | 23.84 | 4.70 | 32 / 88 |
| gate score, R49-aligned (0 = R49 flag boundary) | non-progressor | 0.29 [0.23, 0.32] | 12.79 | 4.45 | 43 / 200 |
| gate score, R49-aligned (0 = R49 flag boundary) | progressor | 0.60 [0.52, 0.65] | 19.00 | 3.69 | 32 / 88 |

one-way random-effects ICC(1) for unequal group sizes (ANOVA), per repeat on the held-out endoscopy scores, averaged over the 10 repeats; patient bootstrap of the repeat-mean ICC (2,000 draws, RandomState(0), resampled patients as separate clusters). ICC near 1: a patient's score is nearly fixed, so averaging or persistence rules cannot separate non-progressors; near 0: independent errors, so they can.

Persistence ceiling: non-progressor patients (mean over repeats) flagged at exactly 1, 2 and ≥ 3 endoscopies. A patient flagged once only is the most a persistence rule can remove.

| Rule | NP ever flagged | Flagged once only | Twice | ≥ 3 times | Flagged ≥ 2 times | Share of flagged NP with one flag only |
|---|---|---|---|---|---|---|
| R49 | 31.8 | 6.8 | 8.8 | 16.2 | 25.0 | 0.213 |
| P1 90% | 36.0 | 7.1 | 11.2 | 17.7 | 28.9 | 0.197 |

### Ranking: nested (held-out) results, all families

Every row: operating threshold (and, within a family, the hyper-parameter) chosen on the training patients' inner out-of-fold predictions of each outer fold by the plan's rule; performance on the held-out patients. Δ against R49 and against P1 at 90% on the same bootstrap draws. Ranked by Δ NP flagged among rows with Δ caught ≥ -0.5 (point estimate); the other rows follow. 'Control' rows are threshold-only dials and re-tuned R49 (they show what the training-side tuning rule alone does). '(pAUC selection)' rows choose the hyper-parameter by patient-level partial AUC (FPR ≤ 0.2) instead.

| # | Method | Caught | NP flagged | Δ NP flagged vs R49 [95% CI] | 99.2% CI | Δ caught [95% CI] | Flags / NP py (Δ) | Δ endoscopy spec. | Samples seq. / patient (Δ) | Δ NP flagged vs P1 90% [95% CI] | Δ caught vs P1 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | A4 confirm-by-sequencing · gate with the high band also sequenced (score 0 = flag boundary) · exponentially weighted mean | 30.8 | 23.1 | **-8.7** [-12.1, -5.6] | [-13.5, -4.8] | -0.3 [-0.8, +0.0] | 0.240 (-0.071) | +0.101 | 3.15 (+1.21) | -12.9 [-17.6, -8.3] | -0.3 |
| 2 | A1 · gate score, R49-aligned · exponentially weighted mean | 30.7 | 23.6 | **-8.2** [-11.4, -5.1] | [-12.8, -4.3] | -0.4 [-1.3, +0.4] | 0.244 (-0.068) | +0.096 | 1.94 (+0.00) | -12.4 [-16.9, -7.9] | -0.4 |
| 3 | A4 confirm-by-sequencing · gate with the high band also sequenced (score 0 = flag boundary) · exponentially weighted mean (pAUC selection) | 31.3 | 23.9 | **-7.9** [-11.4, -4.7] | [-12.7, -3.9] | +0.2 [-0.2, +0.7] | 0.264 (-0.048) | +0.067 | 3.15 (+1.21) | -12.1 [-16.8, -7.4] | +0.2 |
| 4 | A4 confirm-by-sequencing · gate with the high band also sequenced (score 0 = flag boundary) · running mean | 31.4 | 24.0 | **-7.8** [-11.1, -4.7] | [-12.4, -3.7] | +0.3 [-0.3, +1.1] | 0.325 (+0.013) | -0.019 | 3.15 (+1.21) | -12.0 [-16.3, -7.7] | +0.3 |
| 5 | A1+A2: EW memory of gate score + copy-number certificate (pAUC selection) | 30.8 | 24.3 | **-7.5** [-11.0, -4.1] | [-12.7, -3.1] | -0.3 [-1.1, +0.4] | 0.239 (-0.073) | +0.102 | 1.94 (+0.00) | -11.7 [-16.2, -7.1] | -0.3 |
| 6 | A1 · gate score, literal · running mean | 31.1 | 24.6 | **-7.2** [-10.2, -4.3] | [-11.4, -3.6] | +0.0 [-0.7, +0.8] | 0.327 (+0.016) | -0.022 | 1.94 (+0.00) | -11.4 [-15.6, -7.3] | +0.0 |
| 7 | Sample aggregation · max L-LATE (sequence all samples) · exponentially weighted mean | 31.0 | 24.6 | **-7.2** [-10.7, -3.8] | [-12.1, -2.6] | -0.1 [-0.6, +0.3] | 0.278 (-0.033) | +0.047 | 7.61 (+5.67) | -11.4 [-16.2, -6.2] | -0.1 |
| 8 | A1 · gate score, literal · exponentially weighted mean | 30.8 | 24.7 | **-7.1** [-9.8, -4.5] | [-10.9, -3.6] | -0.3 [-0.8, +0.0] | 0.258 (-0.053) | +0.075 | 1.94 (+0.00) | -11.3 [-15.5, -7.0] | -0.3 |
| 9 | Sample aggregation · max L-LATE (sequence all samples) · exponentially weighted mean (pAUC selection) | 31.2 | 24.8 | **-7.0** [-10.6, -3.5] | [-11.8, -2.5] | +0.1 [+0.0, +0.3] | 0.292 (-0.019) | +0.027 | 7.61 (+5.67) | -11.2 [-16.2, -5.9] | +0.1 |
| 10 | Sample aggregation · max L-LATE (sequence all samples) · running mean | 31.1 | 25.2 | **-6.6** [-10.2, -3.2] | [-11.8, -2.3] | +0.0 [-0.4, +0.6] | 0.357 (+0.046) | -0.065 | 7.61 (+5.67) | -10.8 [-15.7, -5.7] | +0.0 |
| 11 | A1 · gate score, R49-aligned · exponentially weighted mean (pAUC selection) | 31.0 | 25.2 | **-6.6** [-10.0, -3.2] | [-11.4, -2.3] | -0.1 [-1.1, +0.9] | 0.275 (-0.036) | +0.051 | 1.94 (+0.00) | -10.8 [-15.0, -6.6] | -0.1 |
| 12 | A1 · gate score, R49-aligned · running mean | 31.2 | 25.3 | **-6.5** [-10.4, -2.8] | [-11.7, -1.7] | +0.1 [-1.0, +1.2] | 0.325 (+0.013) | -0.019 | 1.94 (+0.00) | -10.7 [-14.8, -6.7] | +0.1 |
| 13 | A1 · gate score, literal · exponentially weighted mean (pAUC selection) | 31.0 | 25.3 | **-6.5** [-8.9, -4.2] | [-9.7, -3.4] | -0.1 [-0.3, +0.0] | 0.271 (-0.041) | +0.057 | 1.94 (+0.00) | -10.7 [-14.7, -6.8] | -0.1 |
| 14 | A1+A2': EW memory of gate score + p53-normal certificate (pAUC selection) | 30.9 | 25.3 | **-6.5** [-9.9, -3.2] | [-11.5, -2.4] | -0.2 [-1.1, +0.7] | 0.214 (-0.097) | +0.137 | 1.94 (+0.00) | -10.7 [-14.9, -6.5] | -0.2 |
| 15 | A1 · gate score, R49-aligned · exponentially weighted, longer half-lives (0.5, 8, 16 y) (pAUC selection) | 31.2 | 25.6 | **-6.2** [-9.6, -2.9] | [-10.9, -1.9] | +0.1 [-0.6, +0.9] | 0.300 (-0.011) | +0.016 | 1.94 (+0.00) | -10.4 [-14.4, -6.4] | +0.1 |
| 16 | Sample aggregation · H&E mean over samples · running mean | 31.4 | 27.2 | **-4.6** [-8.3, -1.2] | [-9.9, +0.0] | +0.3 [-0.6, +1.5] | 0.353 (+0.042) | -0.059 | 0.00 (-1.94) | -8.8 [-12.8, -5.0] | +0.3 |
| 17 | A1 · gate score, literal · mean of last 2 | 31.1 | 27.9 | **-3.9** [-6.0, -2.1] | [-6.8, -1.4] | +0.0 [-0.7, +0.8] | 0.308 (-0.004) | +0.005 | 1.94 (+0.00) | -8.1 [-12.0, -4.4] | +0.0 |
| 18 | A2 copy-number certificate (gate) | 31.0 | 28.1 | **-3.7** [-5.6, -2.1] | [-6.3, -1.7] | -0.1 [-0.3, +0.0] | 0.239 (-0.073) | +0.103 | 1.36 (-0.58) | -7.9 [-11.8, -4.1] | -0.1 |
| 19 | A2' p53-normal certificate (gate) | 30.9 | 28.2 | **-3.6** [-5.3, -2.1] | [-5.9, -1.6] | -0.2 [-0.5, +0.0] | 0.200 (-0.111) | +0.157 | 1.17 (-0.77) | -7.8 [-11.6, -4.3] | -0.2 |
| 20 | A4 confirm-by-sequencing · gate with the high band also sequenced (score 0 = flag boundary) · threshold only | 30.8 | 28.2 | **-3.6** [-5.0, -2.3] | [-5.6, -1.8] | -0.3 [-0.8, +0.0] | 0.233 (-0.078) | +0.110 | 3.15 (+1.21) | -7.8 [-11.6, -4.2] | -0.3 |
| 21 | Sample aggregation · H&E mean over samples · exponentially weighted mean | 30.8 | 28.4 | **-3.4** [-6.3, -0.6] | [-7.5, +0.4] | -0.3 [-1.6, +0.9] | 0.315 (+0.004) | -0.005 | 0.00 (-1.94) | -7.6 [-11.1, -4.2] | -0.3 |
| 22 | B4(a) refit, non-progressor weight 2, cut-offs re-tuned by the round-9 rule | 30.8 | 28.6 | **-3.2** [-4.6, -1.8] | [-5.2, -1.4] | -0.3 [-1.1, +0.2] | 0.234 (-0.078) | +0.110 | 1.92 (-0.02) | -7.4 [-11.6, -3.6] | -0.3 |
| 23 | B1-img control: stacked gate on L-IMG only (endoscopy-level cut-offs) | 30.7 | 28.7 | **-3.1** [-4.6, -1.6] | [-5.2, -1.1] | -0.4 [-1.2, +0.2] | 0.243 (-0.068) | +0.097 | 1.84 (-0.10) | -7.3 [-11.2, -3.7] | -0.4 |
| 24 | A1 · gate score, literal · threshold only | 30.6 | 28.8 | **-3.0** [-4.4, -1.8] | [-5.0, -1.4] | -0.5 [-1.0, -0.1] | 0.231 (-0.081) | +0.114 | 1.94 (+0.00) | -7.2 [-10.9, -3.8] | -0.5 |
| 25 | Sample aggregation · max L-LATE (sequence all samples) · threshold only | 30.9 | 29.1 | **-2.7** [-4.4, -0.8] | [-5.0, +0.0] | -0.2 [-0.7, +0.2] | 0.260 (-0.051) | +0.072 | 7.61 (+5.67) | -6.9 [-11.2, -2.7] | -0.2 |
| 26 | Sample aggregation · H&E mean of top-2 samples · running mean | 31.4 | 29.2 | **-2.6** [-6.2, +0.7] | [-8.2, +2.1] | +0.3 [-0.6, +1.5] | 0.399 (+0.087) | -0.124 | 0.00 (-1.94) | -6.8 [-10.3, -3.3] | +0.3 |
| 27 | Sample aggregation · H&E mean over samples · exponentially weighted mean (pAUC selection) | 31.0 | 29.3 | **-2.5** [-5.4, +0.5] | [-6.6, +1.5] | -0.1 [-1.2, +1.0] | 0.309 (-0.003) | +0.004 | 0.00 (-1.94) | -6.7 [-10.2, -3.2] | -0.1 |
| 28 | A1 · gate score, R49-aligned · threshold only | 30.7 | 29.4 | **-2.4** [-3.7, -1.3] | [-4.1, -1.0] | -0.4 [-1.2, +0.0] | 0.249 (-0.063) | +0.089 | 1.94 (+0.00) | -6.6 [-10.3, -3.3] | -0.4 |
| 29 | control: R49 with cut-offs re-tuned by the round-9 rule | 30.6 | 29.4 | **-2.4** [-3.6, -1.3] | [-4.2, -1.0] | -0.5 [-1.2, +0.0] | 0.243 (-0.068) | +0.096 | 1.87 (-0.07) | -6.6 [-10.3, -3.2] | -0.5 |
| 30 | B1+A1+A2: stacked gate + EW memory + copy-number certificate | 31.0 | 29.8 | **-2.0** [-4.6, +0.8] | [-5.9, +1.8] | -0.1 [-0.8, +0.6] | 0.312 (+0.000) | -0.001 | 2.27 (+0.33) | -6.2 [-9.2, -3.1] | -0.1 |
| 31 | A3 agreement within endoscopy | 30.6 | 29.8 | **-2.0** [-3.5, -0.6] | [-4.0, -0.1] | -0.5 [-1.1, -0.1] | 0.248 (-0.063) | +0.089 | 1.51 (-0.43) | -6.2 [-10.1, -2.7] | -0.5 |
| 32 | A1 · gate score, R49-aligned · mean of last 2 | 31.1 | 29.9 | **-1.9** [-4.2, +0.3] | [-5.1, +1.1] | +0.0 [-1.1, +1.2] | 0.327 (+0.015) | -0.022 | 1.94 (+0.00) | -6.1 [-9.4, -2.9] | +0.0 |
| 33 | A4 confirm the high band by sequencing (no outright slide-only flag) | 30.9 | 30.5 | **-1.3** [-2.1, -0.6] | [-2.5, -0.4] | -0.2 [-0.5, +0.0] | 0.256 (-0.056) | +0.078 | 2.96 (+1.01) | -5.5 [-9.1, -2.3] | -0.2 |
| 34 | B3 abstention in middle band | 31.1 | 30.8 | **-1.0** [-1.7, -0.4] | [-1.8, -0.3] | +0.0 [+0.0, +0.0] | 0.281 (-0.031) | +0.043 | 1.94 (+0.00) | -5.2 [-8.8, -2.0] | +0.0 |
| 35 | Sample aggregation · H&E mean of top-2 samples · exponentially weighted mean | 30.8 | 31.1 | **-0.7** [-3.4, +2.0] | [-4.4, +2.9] | -0.3 [-1.6, +0.9] | 0.362 (+0.051) | -0.072 | 0.00 (-1.94) | -4.9 [-7.6, -2.4] | -0.3 |
| 36 | B4(b) refit, NDBE samples only, cut-offs re-tuned by the round-9 rule | 30.7 | 31.1 | **-0.7** [-3.6, +2.4] | [-4.7, +4.0] | -0.4 [-1.4, +0.2] | 0.291 (-0.021) | +0.029 | 2.33 (+0.39) | -4.9 [-9.1, -0.3] | -0.4 |
| 37 | A1 · H&E alone (max L-IMG) · running mean | 31.5 | 31.2 | **-0.6** [-4.4, +3.2] | [-5.8, +4.7] | +0.4 [-0.8, +2.0] | 0.419 (+0.108) | -0.153 | 0.00 (-1.94) | -4.8 [-7.8, -1.9] | +0.4 |
| 38 | Sample aggregation · H&E mean of top-2 samples · exponentially weighted mean (pAUC selection) | 30.7 | 31.7 | **-0.1** [-2.5, +2.5] | [-3.2, +3.5] | -0.4 [-1.9, +0.9] | 0.352 (+0.040) | -0.057 | 0.00 (-1.94) | -4.3 [-6.9, -1.9] | -0.4 |
| 39 | A1 · stacked B1 gate score, aligned · exponentially weighted mean | 31.1 | 31.9 | **+0.1** [-2.0, +2.5] | [-2.9, +3.4] | +0.0 [-0.6, +0.6] | 0.387 (+0.076) | -0.107 | 2.27 (+0.33) | -4.1 [-6.8, -1.3] | +0.0 |
| 40 | B4(a) refit, non-progressor weight 2, R49 rules rebuilt | 31.3 | 32.1 | **+0.3** [-0.4, +1.0] | [-0.7, +1.2] | +0.2 [+0.0, +0.5] | 0.307 (-0.004) | +0.006 | 1.98 (+0.04) | -3.9 [-7.3, -0.5] | +0.2 |
| 41 | A1 · H&E alone (max L-IMG) · exponentially weighted mean | 31.2 | 32.1 | **+0.3** [-2.7, +3.4] | [-3.6, +4.5] | +0.1 [-1.2, +1.7] | 0.371 (+0.060) | -0.085 | 0.00 (-1.94) | -3.9 [-6.4, -1.7] | +0.1 |
| 42 | B1+A1+A2: stacked gate + EW memory + copy-number certificate (pAUC selection) | 31.2 | 32.2 | **+0.4** [-2.1, +3.0] | [-3.4, +4.0] | +0.1 [-0.6, +0.8] | 0.373 (+0.062) | -0.087 | 2.27 (+0.33) | -3.8 [-6.7, -0.9] | +0.1 |
| 43 | B1 stacked gate (L-IMG, grade, age, sex; + L-CNV in middle band) | 30.9 | 32.2 | **+0.4** [-0.6, +1.4] | [-0.9, +2.0] | -0.2 [-0.7, +0.0] | 0.317 (+0.006) | -0.009 | 2.33 (+0.39) | -3.8 [-7.0, -0.7] | -0.2 |
| 44 | A1 · stacked B1 gate score, aligned · running mean | 31.3 | 32.4 | **+0.6** [-2.1, +3.4] | [-2.9, +4.4] | +0.2 [-0.7, +1.1] | 0.453 (+0.142) | -0.201 | 2.27 (+0.33) | -3.6 [-6.6, -0.2] | +0.2 |
| 45 | A1 · stacked B1 gate score, aligned · exponentially weighted mean (pAUC selection) | 31.1 | 32.5 | **+0.7** [-1.5, +3.1] | [-2.4, +4.0] | +0.0 [-0.6, +0.6] | 0.401 (+0.089) | -0.126 | 2.27 (+0.33) | -3.5 [-6.2, -0.6] | +0.0 |
| 46 | Sample aggregation · H&E mean over samples · threshold only | 30.7 | 32.7 | **+0.9** [-2.0, +3.9] | [-3.2, +5.1] | -0.4 [-2.0, +1.0] | 0.285 (-0.027) | +0.037 | 0.00 (-1.94) | -3.3 [-6.2, -0.7] | -0.4 |
| 47 | A1 · H&E alone (max L-IMG) · exponentially weighted mean (pAUC selection) | 31.5 | 33.1 | **+1.3** [-1.6, +4.4] | [-2.6, +5.5] | +0.4 [-0.9, +2.1] | 0.373 (+0.061) | -0.087 | 0.00 (-1.94) | -2.9 [-5.2, -0.9] | +0.4 |
| 48 | B1 + p53 (aberrant, missing) | 30.9 | 33.4 | **+1.6** [+0.1, +3.3] | [-0.3, +4.0] | -0.2 [-0.7, +0.0] | 0.344 (+0.032) | -0.046 | 2.34 (+0.40) | -2.6 [-5.5, +0.4] | -0.2 |
| 49 | A1 · stacked B1 gate score, aligned · mean of last 2 | 31.3 | 33.8 | **+2.0** [+0.0, +4.2] | [-0.9, +5.0] | +0.2 [-0.7, +1.1] | 0.422 (+0.110) | -0.156 | 2.27 (+0.33) | -2.2 [-5.1, +0.8] | +0.2 |
| 50 | A1 · H&E alone (max L-IMG) · mean of last 2 | 31.4 | 34.2 | **+2.4** [-0.4, +5.2] | [-1.2, +6.1] | +0.3 [-1.0, +1.9] | 0.391 (+0.080) | -0.113 | 0.00 (-1.94) | -1.8 [-3.3, -0.4] | +0.3 |
| 51 | A1 · stacked B1 gate score, aligned · threshold only | 31.2 | 34.8 | **+3.0** [+1.4, +4.7] | [+1.0, +5.3] | +0.1 [-0.5, +0.7] | 0.373 (+0.061) | -0.087 | 2.27 (+0.33) | -1.2 [-3.9, +1.6] | +0.1 |
| 52 | B4(b) refit, NDBE samples only, R49 rules rebuilt | 31.1 | 34.9 | **+3.1** [-0.1, +6.5] | [-1.0, +7.9] | +0.0 [-0.3, +0.3] | 0.363 (+0.052) | -0.074 | 2.31 (+0.38) | -1.1 [-5.2, +3.2] | +0.0 |
| 53 | Sample aggregation · H&E mean of top-2 samples · threshold only | 30.6 | 35.4 | **+3.6** [+0.9, +6.4] | [+0.0, +7.4] | -0.5 [-2.3, +1.0] | 0.333 (+0.021) | -0.030 | 0.00 (-1.94) | -0.6 [-2.3, +1.0] | -0.5 |
| 54 | A1 · H&E alone (max L-IMG) · threshold only | 31.5 | 36.0 | **+4.2** [+1.8, +6.8] | [+0.9, +7.8] | +0.4 [-0.7, +1.8] | 0.338 (+0.026) | -0.037 | 0.00 (-1.94) | +0.0 [-1.0, +1.1] | +0.4 |
| 55 | A1 · gate score, R49-aligned · change from own mean (pAUC selection) | 30.6 | 37.3 | **+5.5** [+2.3, +9.1] | [+1.3, +10.4] | -0.5 [-1.3, +0.0] | 0.264 (-0.048) | +0.068 | 1.94 (+0.00) | +1.3 [-2.2, +5.3] | -0.5 |
| 56 | A1 · gate score, R49-aligned · change from own mean | 30.6 | 37.6 | **+5.8** [+2.4, +9.6] | [+1.3, +11.0] | -0.5 [-1.3, +0.0] | 0.261 (-0.051) | +0.072 | 1.94 (+0.00) | +1.6 [-2.1, +5.7] | -0.5 |
| 57 | A1 · stacked B1 gate score, aligned · change from own mean (pAUC selection) | 30.8 | 38.4 | **+6.6** [+3.6, +10.0] | [+2.5, +11.3] | -0.3 [-1.0, +0.4] | 0.358 (+0.047) | -0.067 | 2.27 (+0.33) | +2.4 [-0.7, +5.9] | -0.3 |
| 58 | A1 · H&E alone (max L-IMG) · change from own mean (pAUC selection) | 31.2 | 39.1 | **+7.3** [+4.2, +10.6] | [+3.2, +11.6] | +0.1 [-1.6, +1.7] | 0.333 (+0.022) | -0.031 | 0.00 (-1.94) | +3.1 [+0.9, +6.2] | +0.1 |
| 59 | A1 · H&E alone (max L-IMG) · change from own mean | 30.9 | 39.6 | **+7.8** [+4.5, +11.3] | [+3.5, +12.6] | -0.2 [-2.1, +1.3] | 0.331 (+0.020) | -0.028 | 0.00 (-1.94) | +3.6 [+1.0, +7.0] | -0.2 |
| 60 | A1+A2: EW memory of gate score + copy-number certificate | 30.5 | 21.5 | **-10.3** [-13.9, -6.9] | [-15.6, -5.8] | -0.6 [-1.6, +0.2] | 0.189 (-0.122) | +0.173 | 1.94 (+0.00) | -14.5 [-19.0, -9.6] | -0.6 |
| 61 | A1+A2': EW memory of gate score + p53-normal certificate | 30.5 | 22.2 | **-9.6** [-12.9, -6.5] | [-14.1, -5.5] | -0.6 [-1.6, +0.2] | 0.164 (-0.148) | +0.209 | 1.94 (+0.00) | -13.8 [-18.1, -9.2] | -0.6 |
| 62 | A1 · gate score, R49-aligned · exponentially weighted, longer half-lives (0.5, 8, 16 y) | 30.4 | 23.6 | **-8.2** [-11.1, -5.4] | [-12.1, -4.6] | -0.7 [-1.5, -0.1] | 0.236 (-0.075) | +0.107 | 1.94 (+0.00) | -12.4 [-16.7, -8.1] | -0.7 |
| 63 | A1 · gate score, R49-aligned · consecutive-2 or t_high | 29.4 | 29.4 | **-2.4** [-5.1, +0.2] | [-5.9, +1.2] | -1.7 [-4.0, -0.1] | 0.287 (-0.024) | +0.034 | 1.94 (+0.00) | -6.6 [-10.3, -3.0] | -1.7 |
| 64 | A1 · gate score, literal · consecutive-2 or t_high | 28.3 | 30.7 | **-1.1** [-3.7, +1.3] | [-4.5, +2.1] | -2.8 [-5.9, -0.4] | 0.304 (-0.007) | +0.010 | 1.94 (+0.00) | -5.3 [-8.5, -2.2] | -2.8 |
| 65 | A1 · gate score, literal · 2-of-last-3 or t_high | 28.7 | 31.0 | **-0.8** [-2.9, +1.4] | [-3.7, +2.2] | -2.4 [-5.5, -0.2] | 0.350 (+0.039) | -0.055 | 1.94 (+0.00) | -5.0 [-8.1, -1.9] | -2.4 |
| 66 | A1 · gate score, R49-aligned · 2-of-last-3 or t_high | 29.4 | 31.2 | **-0.6** [-3.0, +1.8] | [-3.7, +2.6] | -1.7 [-4.0, -0.1] | 0.347 (+0.035) | -0.050 | 1.94 (+0.00) | -4.8 [-8.4, -1.2] | -1.7 |
| 67 | A1 · gate score, literal · 2-of-n anywhere or t_high | 28.6 | 31.3 | **-0.5** [-2.7, +1.8] | [-3.5, +2.6] | -2.5 [-5.5, -0.3] | 0.380 (+0.068) | -0.096 | 1.94 (+0.00) | -4.7 [-7.8, -1.4] | -2.5 |
| 68 | A1 · gate score, R49-aligned · 2-of-n anywhere or t_high | 29.3 | 31.6 | **-0.2** [-2.7, +2.2] | [-3.6, +3.1] | -1.8 [-4.0, -0.2] | 0.375 (+0.064) | -0.090 | 1.94 (+0.00) | -4.4 [-7.9, -0.9] | -1.8 |
| 69 | A1 · gate score, R49-aligned · consecutive-2 or t_high (pAUC selection) | 28.4 | 32.7 | **+0.9** [-1.8, +3.7] | [-3.0, +4.8] | -2.7 [-5.9, -0.4] | 0.327 (+0.016) | -0.023 | 1.94 (+0.00) | -3.3 [-6.3, -0.2] | -2.7 |
| 70 | A1 · gate score, literal · consecutive-2 or t_high (pAUC selection) | 28.1 | 32.9 | **+1.1** [-1.7, +3.9] | [-2.9, +5.0] | -3.0 [-6.3, -0.6] | 0.336 (+0.025) | -0.035 | 1.94 (+0.00) | -3.1 [-6.0, +0.0] | -3.0 |
| 71 | A1 · gate score, literal · consecutive-2 | 21.2 | 33.2 | **+1.4** [-1.7, +4.4] | [-3.0, +5.4] | -9.9 [-15.0, -5.4] | 0.333 (+0.022) | -0.031 | 1.94 (+0.00) | -2.8 [-5.8, +0.4] | -9.9 |
| 72 | A1 · gate score, R49-aligned · consecutive-2 | 21.2 | 33.3 | **+1.5** [-1.5, +4.4] | [-2.8, +5.5] | -9.9 [-15.0, -5.4] | 0.331 (+0.020) | -0.028 | 1.94 (+0.00) | -2.7 [-5.6, +0.5] | -9.9 |
| 73 | A1 · H&E alone (max L-IMG) · consecutive-2 or t_high | 27.8 | 33.4 | **+1.6** [-1.3, +4.8] | [-2.3, +5.8] | -3.3 [-6.6, -0.8] | 0.327 (+0.016) | -0.022 | 0.00 (-1.94) | -2.6 [-5.0, -0.4] | -3.3 |
| 74 | A1 · stacked B1 gate score, aligned · consecutive-2 or t_high | 29.6 | 33.6 | **+1.8** [-1.4, +5.3] | [-2.7, +6.3] | -1.5 [-3.2, -0.2] | 0.352 (+0.041) | -0.057 | 2.27 (+0.33) | -2.4 [-5.2, +0.8] | -1.5 |
| 75 | A1 · gate score, literal · change from own mean (pAUC selection) | 30.4 | 34.1 | **+2.3** [-0.1, +4.9] | [-0.9, +5.8] | -0.7 [-1.4, -0.1] | 0.229 (-0.082) | +0.117 | 1.94 (+0.00) | -1.9 [-5.5, +1.8] | -0.7 |
| 76 | A1 · stacked B1 gate score, aligned · consecutive-2 or t_high (pAUC selection) | 29.1 | 34.2 | **+2.4** [-0.9, +6.0] | [-2.2, +7.3] | -2.0 [-4.1, -0.4] | 0.360 (+0.048) | -0.068 | 2.27 (+0.33) | -1.8 [-4.8, +1.6] | -2.0 |
| 77 | A1 · gate score, literal · 2-of-last-3 or t_high (pAUC selection) | 28.3 | 34.2 | **+2.4** [-0.1, +5.1] | [-1.1, +6.0] | -2.8 [-6.1, -0.4] | 0.390 (+0.079) | -0.112 | 1.94 (+0.00) | -1.8 [-4.7, +1.3] | -2.8 |
| 78 | A1 · gate score, R49-aligned · 2-of-last-3 or t_high (pAUC selection) | 28.5 | 34.3 | **+2.5** [+0.1, +5.1] | [-0.8, +6.0] | -2.6 [-5.8, -0.3] | 0.384 (+0.073) | -0.103 | 1.94 (+0.00) | -1.7 [-4.6, +1.5] | -2.6 |
| 79 | A1 · gate score, literal · 2-of-n anywhere or t_high (pAUC selection) | 28.2 | 34.3 | **+2.5** [+0.0, +5.2] | [-1.1, +6.3] | -2.9 [-6.3, -0.4] | 0.415 (+0.104) | -0.147 | 1.94 (+0.00) | -1.7 [-4.7, +1.6] | -2.9 |
| 80 | A1 · gate score, literal · change from own mean | 30.4 | 34.5 | **+2.7** [+0.1, +5.5] | [-0.7, +6.6] | -0.7 [-1.4, -0.1] | 0.231 (-0.080) | +0.113 | 1.94 (+0.00) | -1.5 [-5.2, +2.3] | -0.7 |
| 81 | A1 · gate score, R49-aligned · 2-of-n anywhere or t_high (pAUC selection) | 28.4 | 34.5 | **+2.7** [+0.2, +5.4] | [-0.8, +6.3] | -2.7 [-5.9, -0.4] | 0.411 (+0.099) | -0.141 | 1.94 (+0.00) | -1.5 [-4.5, +1.8] | -2.7 |
| 82 | A1 · gate score, literal · 2-of-n anywhere | 21.2 | 34.9 | **+3.1** [+0.4, +6.0] | [-0.8, +7.1] | -9.9 [-14.9, -5.4] | 0.418 (+0.107) | -0.150 | 1.94 (+0.00) | -1.1 [-4.0, +2.1] | -9.9 |
| 83 | A1 · gate score, literal · 2-of-last-3 | 21.2 | 35.0 | **+3.2** [+0.6, +6.0] | [-0.6, +6.9] | -9.9 [-14.9, -5.4] | 0.391 (+0.080) | -0.113 | 1.94 (+0.00) | -1.0 [-3.8, +2.1] | -9.9 |
| 84 | A1 · stacked B1 gate score, aligned · 2-of-last-3 or t_high | 29.6 | 35.1 | **+3.3** [+0.3, +6.4] | [-0.7, +7.5] | -1.5 [-3.2, -0.2] | 0.402 (+0.090) | -0.128 | 2.27 (+0.33) | -0.9 [-3.5, +2.0] | -1.5 |
| 85 | A1 · H&E alone (max L-IMG) · consecutive-2 or t_high (pAUC selection) | 28.1 | 35.2 | **+3.4** [+0.0, +7.0] | [-1.2, +8.2] | -3.0 [-6.3, -0.5] | 0.351 (+0.040) | -0.056 | 0.00 (-1.94) | -0.8 [-3.2, +1.8] | -3.0 |
| 86 | A1 · H&E alone (max L-IMG) · consecutive-2 | 21.1 | 35.2 | **+3.4** [-0.0, +7.2] | [-1.4, +8.3] | -10.0 [-15.0, -5.5] | 0.344 (+0.033) | -0.047 | 0.00 (-1.94) | -0.8 [-3.3, +1.8] | -10.0 |
| 87 | A1 · gate score, R49-aligned · 2-of-n anywhere | 21.3 | 35.3 | **+3.5** [+0.9, +6.3] | [-0.3, +7.4] | -9.8 [-14.7, -5.3] | 0.422 (+0.110) | -0.156 | 1.94 (+0.00) | -0.7 [-3.5, +2.4] | -9.8 |
| 88 | A1 · gate score, R49-aligned · 2-of-last-3 | 21.3 | 35.3 | **+3.5** [+1.0, +6.2] | [-0.0, +7.1] | -9.8 [-14.7, -5.3] | 0.394 (+0.082) | -0.116 | 1.94 (+0.00) | -0.7 [-3.5, +2.3] | -9.8 |
| 89 | A1 · stacked B1 gate score, aligned · 2-of-n anywhere or t_high | 29.6 | 35.6 | **+3.8** [+0.7, +7.0] | [-0.3, +8.1] | -1.5 [-3.2, -0.2] | 0.433 (+0.121) | -0.172 | 2.27 (+0.33) | -0.4 [-3.0, +2.6] | -1.5 |
| 90 | A1 · stacked B1 gate score, aligned · 2-of-last-3 or t_high (pAUC selection) | 29.1 | 35.6 | **+3.8** [+0.7, +7.0] | [-0.3, +8.1] | -2.0 [-4.1, -0.4] | 0.410 (+0.099) | -0.140 | 2.27 (+0.33) | -0.4 [-3.1, +2.7] | -2.0 |
| 91 | A1 · H&E alone (max L-IMG) · 2-of-last-3 or t_high | 28.1 | 35.7 | **+3.9** [+1.2, +6.6] | [+0.2, +7.4] | -3.0 [-6.1, -0.6] | 0.403 (+0.091) | -0.129 | 0.00 (-1.94) | -0.3 [-2.1, +1.7] | -3.0 |
| 92 | A1 · stacked B1 gate score, aligned · consecutive-2 | 21.2 | 35.8 | **+4.0** [+0.6, +7.6] | [-0.7, +8.9] | -9.9 [-15.0, -5.3] | 0.374 (+0.063) | -0.089 | 2.27 (+0.33) | -0.2 [-3.4, +3.4] | -9.9 |
| 93 | A1 · stacked B1 gate score, aligned · 2-of-n anywhere or t_high (pAUC selection) | 29.1 | 36.2 | **+4.4** [+1.3, +7.8] | [+0.2, +8.9] | -2.0 [-4.1, -0.4] | 0.439 (+0.128) | -0.181 | 2.27 (+0.33) | +0.2 [-2.5, +3.4] | -2.0 |
| 94 | A1 · H&E alone (max L-IMG) · 2-of-n anywhere or t_high | 28.1 | 36.2 | **+4.4** [+1.8, +7.2] | [+0.8, +8.0] | -3.0 [-6.1, -0.6] | 0.435 (+0.124) | -0.175 | 0.00 (-1.94) | +0.2 [-1.6, +2.2] | -3.0 |
| 95 | A1 · stacked B1 gate score, aligned · 2-of-last-3 | 21.4 | 37.0 | **+5.2** [+2.1, +8.6] | [+1.0, +10.1] | -9.7 [-14.7, -5.1] | 0.424 (+0.113) | -0.160 | 2.27 (+0.33) | +1.0 [-2.0, +4.4] | -9.7 |
| 96 | A1 · stacked B1 gate score, aligned · 2-of-n anywhere | 21.4 | 37.4 | **+5.6** [+2.4, +9.1] | [+1.2, +10.5] | -9.7 [-14.7, -5.1] | 0.453 (+0.142) | -0.200 | 2.27 (+0.33) | +1.4 [-1.6, +4.8] | -9.7 |
| 97 | A1 · H&E alone (max L-IMG) · 2-of-last-3 or t_high (pAUC selection) | 28.2 | 38.0 | **+6.2** [+3.0, +9.6] | [+2.1, +10.4] | -2.9 [-6.2, -0.5] | 0.430 (+0.119) | -0.168 | 0.00 (-1.94) | +2.0 [-0.0, +4.4] | -2.9 |
| 98 | A1 · H&E alone (max L-IMG) · 2-of-last-3 | 21.1 | 38.0 | **+6.2** [+3.0, +9.5] | [+2.0, +10.6] | -10.0 [-14.9, -5.5] | 0.424 (+0.112) | -0.159 | 0.00 (-1.94) | +2.0 [-0.1, +4.5] | -10.0 |
| 99 | A1 · H&E alone (max L-IMG) · 2-of-n anywhere or t_high (pAUC selection) | 28.1 | 38.4 | **+6.6** [+3.4, +10.0] | [+2.3, +11.3] | -3.0 [-6.3, -0.5] | 0.461 (+0.149) | -0.211 | 0.00 (-1.94) | +2.4 [+0.2, +5.0] | -3.0 |
| 100 | A1 · H&E alone (max L-IMG) · 2-of-n anywhere | 21.1 | 38.5 | **+6.7** [+3.4, +10.2] | [+2.4, +11.5] | -10.0 [-14.9, -5.5] | 0.455 (+0.144) | -0.204 | 0.00 (-1.94) | +2.5 [+0.2, +5.2] | -10.0 |
| 101 | A1 · stacked B1 gate score, aligned · change from own mean | 30.5 | 38.8 | **+7.0** [+3.8, +10.6] | [+2.6, +12.0] | -0.6 [-1.4, +0.2] | 0.344 (+0.033) | -0.047 | 2.27 (+0.33) | +2.8 [-0.5, +6.8] | -0.6 |

**Top 3 (excluding controls and pAUC variants): 1. A4 confirm-by-sequencing · gate with the high band also sequenced (score 0 = flag boundary) · exponentially weighted mean; 2. A1 · gate score, R49-aligned · exponentially weighted mean; 3. A4 confirm-by-sequencing · gate with the high band also sequenced (score 0 = flag boundary) · running mean.**

### k-of-n persistence and progressors with a single pre-event endoscopy

A 2-of-n rule cannot flag a progressor with one pre-event endoscopy unless an override threshold (t_high) flags it outright.

| Method (nested) | Progressors with 1 endoscopy: caught (of n) | R49 | Δ caught overall | Δ NP flagged [95% CI] |
|---|---|---|---|---|
| A1 · gate score, R49-aligned · consecutive-2 or t_high | 7.9 (of 10) | 9.4 | -1.7 | -2.4 [-5.1, +0.2] |
| A1 · gate score, literal · consecutive-2 or t_high | 7.3 (of 10) | 9.4 | -2.8 | -1.1 [-3.7, +1.3] |
| A1 · gate score, literal · 2-of-last-3 or t_high | 7.3 (of 10) | 9.4 | -2.4 | -0.8 [-2.9, +1.4] |
| A1 · gate score, R49-aligned · 2-of-last-3 or t_high | 7.9 (of 10) | 9.4 | -1.7 | -0.6 [-3.0, +1.8] |
| A1 · gate score, literal · 2-of-n anywhere or t_high | 7.3 (of 10) | 9.4 | -2.5 | -0.5 [-2.7, +1.8] |
| A1 · gate score, R49-aligned · 2-of-n anywhere or t_high | 7.9 (of 10) | 9.4 | -1.8 | -0.2 [-2.7, +2.2] |
| A1 · gate score, literal · consecutive-2 | 0.0 (of 10) | 9.4 | -9.9 | +1.4 [-1.7, +4.4] |
| A1 · gate score, R49-aligned · consecutive-2 | 0.0 (of 10) | 9.4 | -9.9 | +1.5 [-1.5, +4.4] |
| A1 · H&E alone (max L-IMG) · consecutive-2 or t_high | 7.2 (of 10) | 9.4 | -3.3 | +1.6 [-1.3, +4.8] |
| A1 · stacked B1 gate score, aligned · consecutive-2 or t_high | 7.9 (of 10) | 9.4 | -1.5 | +1.8 [-1.4, +5.3] |
| A1 · gate score, literal · 2-of-n anywhere | 0.0 (of 10) | 9.4 | -9.9 | +3.1 [+0.4, +6.0] |
| A1 · gate score, literal · 2-of-last-3 | 0.0 (of 10) | 9.4 | -9.9 | +3.2 [+0.6, +6.0] |
| A1 · stacked B1 gate score, aligned · 2-of-last-3 or t_high | 7.9 (of 10) | 9.4 | -1.5 | +3.3 [+0.3, +6.4] |
| A1 · H&E alone (max L-IMG) · consecutive-2 | 0.0 (of 10) | 9.4 | -10.0 | +3.4 [-0.0, +7.2] |
| A1 · gate score, R49-aligned · 2-of-n anywhere | 0.0 (of 10) | 9.4 | -9.8 | +3.5 [+0.9, +6.3] |
| A1 · gate score, R49-aligned · 2-of-last-3 | 0.0 (of 10) | 9.4 | -9.8 | +3.5 [+1.0, +6.2] |
| A1 · stacked B1 gate score, aligned · 2-of-n anywhere or t_high | 7.9 (of 10) | 9.4 | -1.5 | +3.8 [+0.7, +7.0] |
| A1 · H&E alone (max L-IMG) · 2-of-last-3 or t_high | 7.3 (of 10) | 9.4 | -3.0 | +3.9 [+1.2, +6.6] |
| A1 · stacked B1 gate score, aligned · consecutive-2 | 0.0 (of 10) | 9.4 | -9.9 | +4.0 [+0.6, +7.6] |
| A1 · H&E alone (max L-IMG) · 2-of-n anywhere or t_high | 7.3 (of 10) | 9.4 | -3.0 | +4.4 [+1.8, +7.2] |
| A1 · stacked B1 gate score, aligned · 2-of-last-3 | 0.0 (of 10) | 9.4 | -9.7 | +5.2 [+2.1, +8.6] |
| A1 · stacked B1 gate score, aligned · 2-of-n anywhere | 0.0 (of 10) | 9.4 | -9.7 | +5.6 [+2.4, +9.1] |
| A1 · H&E alone (max L-IMG) · 2-of-last-3 | 0.0 (of 10) | 9.4 | -10.0 | +6.2 [+3.0, +9.5] |
| A1 · H&E alone (max L-IMG) · 2-of-n anywhere | 0.0 (of 10) | 9.4 | -10.0 | +6.7 [+3.4, +10.2] |

### Grid points (apparent, labelled optimistic)

#### A1 memory rules

Fixed hyper-parameter picked after seeing the evaluation (optimistic); the threshold is still the training-chosen one.

| # | Method | Caught | NP flagged | Δ NP flagged vs R49 [95% CI] | 99.2% CI | Δ caught [95% CI] | Flags / NP py (Δ) | Δ endoscopy spec. | Samples seq. / patient (Δ) | Δ NP flagged vs P1 90% [95% CI] | Δ caught vs P1 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | A1 · gate score, literal · exponentially weighted mean · ew h=4y | 31.3 | 24.6 | **-7.2** [-10.1, -4.3] | [-11.3, -3.7] | +0.2 [+0.0, +0.7] | 0.293 (-0.018) | +0.026 | 1.94 (+0.00) | -11.4 [-15.7, -7.2] | +0.2 |
| 2 | A1 · gate score, literal · exponentially weighted mean · ew h=2y | 31.3 | 25.0 | **-6.8** [-9.4, -4.2] | [-10.2, -3.4] | +0.2 [+0.0, +0.7] | 0.268 (-0.044) | +0.062 | 1.94 (+0.00) | -11.0 [-15.1, -6.8] | +0.2 |
| 3 | A1 · gate score, R49-aligned · exponentially weighted, longer half-lives (0.5, 8, 16 y) · ew h=8y | 31.1 | 25.2 | **-6.6** [-10.3, -3.0] | [-11.8, -1.9] | +0.0 [-1.1, +1.2] | 0.306 (-0.005) | +0.007 | 1.94 (+0.00) | -10.8 [-14.9, -6.7] | +0.0 |
| 4 | A1 · gate score, R49-aligned · exponentially weighted, longer half-lives (0.5, 8, 16 y) · ew h=16y | 31.2 | 25.3 | **-6.5** [-10.2, -2.8] | [-11.8, -1.8] | +0.1 [-1.0, +1.2] | 0.315 (+0.004) | -0.005 | 1.94 (+0.00) | -10.7 [-14.8, -6.7] | +0.1 |
| 5 | A1 · gate score, R49-aligned · exponentially weighted mean · ew h=4y | 31.1 | 25.4 | **-6.4** [-10.2, -2.8] | [-11.7, -1.7] | +0.0 [-1.1, +1.2] | 0.294 (-0.018) | +0.025 | 1.94 (+0.00) | -10.6 [-14.8, -6.5] | +0.0 |
| 6 | A1 · gate score, R49-aligned · exponentially weighted mean · ew h=1y | 30.9 | 25.7 | **-6.1** [-8.7, -3.6] | [-9.9, -3.0] | -0.2 [-0.8, +0.3] | 0.250 (-0.062) | +0.087 | 1.94 (+0.00) | -10.3 [-14.5, -6.0] | -0.2 |
| 7 | A1 · gate score, R49-aligned · exponentially weighted mean · ew h=2y | 30.9 | 25.8 | **-6.0** [-9.2, -2.9] | [-10.3, -2.0] | -0.2 [-1.2, +0.7] | 0.276 (-0.036) | +0.050 | 1.94 (+0.00) | -10.2 [-14.3, -6.2] | -0.2 |
| 8 | A1 · gate score, literal · exponentially weighted mean · ew h=1y | 30.8 | 26.4 | **-5.4** [-7.5, -3.5] | [-8.3, -2.8] | -0.3 [-0.8, +0.0] | 0.249 (-0.063) | +0.089 | 1.94 (+0.00) | -9.6 [-13.6, -5.8] | -0.3 |
| 9 | A1 · gate score, R49-aligned · exponentially weighted, longer half-lives (0.5, 8, 16 y) · ew h=0.5y | 30.7 | 26.9 | **-4.9** [-7.1, -2.9] | [-7.9, -2.4] | -0.4 [-1.0, +0.0] | 0.232 (-0.079) | +0.111 | 1.94 (+0.00) | -9.1 [-13.1, -5.2] | -0.4 |
| 10 | A1 · H&E alone (max L-IMG) · exponentially weighted mean · ew h=4y | 31.5 | 31.8 | **+0.0** [-3.5, +3.5] | [-4.6, +4.8] | +0.4 [-0.9, +2.0] | 0.397 (+0.086) | -0.121 | 0.00 (-1.94) | -4.2 [-7.0, -1.7] | +0.4 |
| 11 | A1 · stacked B1 gate score, aligned · exponentially weighted mean · ew h=4y | 31.3 | 31.9 | **+0.1** [-2.3, +2.6] | [-3.1, +3.3] | +0.2 [-0.7, +1.1] | 0.420 (+0.109) | -0.154 | 2.27 (+0.33) | -4.1 [-7.0, -1.1] | +0.2 |
| 12 | A1 · stacked B1 gate score, aligned · exponentially weighted mean · ew h=2y | 31.2 | 32.3 | **+0.5** [-1.7, +2.9] | [-2.6, +3.8] | +0.1 [-0.6, +0.8] | 0.401 (+0.089) | -0.126 | 2.27 (+0.33) | -3.7 [-6.6, -0.7] | +0.1 |
| 13 | A1 · H&E alone (max L-IMG) · exponentially weighted mean · ew h=2y | 31.3 | 32.5 | **+0.7** [-2.5, +4.0] | [-3.5, +5.0] | +0.2 [-1.0, +1.7] | 0.378 (+0.067) | -0.095 | 0.00 (-1.94) | -3.5 [-6.0, -1.3] | +0.2 |
| 14 | A1 · stacked B1 gate score, aligned · exponentially weighted mean · ew h=1y | 31.1 | 32.7 | **+0.9** [-1.2, +3.2] | [-1.9, +4.1] | +0.0 [-0.6, +0.6] | 0.385 (+0.074) | -0.104 | 2.27 (+0.33) | -3.3 [-6.0, -0.4] | +0.0 |
| 15 | A1 · H&E alone (max L-IMG) · exponentially weighted mean · ew h=1y | 31.3 | 33.8 | **+2.0** [-0.6, +4.8] | [-1.5, +5.8] | +0.2 [-1.0, +1.7] | 0.354 (+0.043) | -0.061 | 0.00 (-1.94) | -2.2 [-4.1, -0.6] | +0.2 |
| 16 | A1 · gate score, R49-aligned · change from own mean · change from own mean, lambda=0.5 | 30.6 | 37.3 | **+5.5** [+2.3, +9.1] | [+1.3, +10.4] | -0.5 [-1.3, +0.0] | 0.264 (-0.048) | +0.068 | 1.94 (+0.00) | +1.3 [-2.2, +5.3] | -0.5 |
| 17 | A1 · stacked B1 gate score, aligned · change from own mean · change from own mean, lambda=0.5 | 30.8 | 38.4 | **+6.6** [+3.6, +10.0] | [+2.5, +11.3] | -0.3 [-1.0, +0.4] | 0.357 (+0.046) | -0.065 | 2.27 (+0.33) | +2.4 [-0.7, +5.9] | -0.3 |
| 18 | A1 · H&E alone (max L-IMG) · change from own mean · change from own mean, lambda=0.5 | 31.2 | 39.1 | **+7.3** [+4.2, +10.6] | [+3.2, +11.6] | +0.1 [-1.6, +1.7] | 0.333 (+0.022) | -0.031 | 0.00 (-1.94) | +3.1 [+0.9, +6.2] | +0.1 |
| 19 | A1 · gate score, R49-aligned · change from own mean · change from own mean, lambda=1.0 | 30.6 | 39.1 | **+7.3** [+3.3, +11.9] | [+1.9, +13.6] | -0.5 [-1.2, +0.0] | 0.273 (-0.039) | +0.054 | 1.94 (+0.00) | +3.1 [-0.8, +7.7] | -0.5 |
| 20 | A1 · H&E alone (max L-IMG) · change from own mean · change from own mean, lambda=1.0 | 30.8 | 41.1 | **+9.3** [+5.4, +13.6] | [+4.0, +15.3] | -0.3 [-2.4, +1.3] | 0.340 (+0.028) | -0.040 | 0.00 (-1.94) | +5.1 [+1.8, +9.3] | -0.3 |
| 21 | A1 · gate score, R49-aligned · consecutive-2 or t_high · consecutive-2 or t_high=q90 | 29.7 | 29.7 | **-2.1** [-4.6, +0.3] | [-5.4, +1.3] | -1.4 [-3.5, +0.0] | 0.291 (-0.020) | +0.028 | 1.94 (+0.00) | -6.3 [-9.9, -2.8] | -1.4 |
| 22 | A1 · gate score, R49-aligned · consecutive-2 or t_high · consecutive-2 or t_high=q95 | 29.0 | 31.2 | **-0.6** [-3.2, +1.9] | [-4.0, +2.8] | -2.1 [-4.8, -0.2] | 0.306 (-0.005) | +0.007 | 1.94 (+0.00) | -4.8 [-8.1, -1.5] | -2.1 |
| 23 | A1 · gate score, R49-aligned · 2-of-last-3 or t_high · 2-of-last-3 or t_high=q90 | 29.7 | 31.3 | **-0.5** [-2.8, +1.8] | [-3.5, +2.6] | -1.4 [-3.5, +0.0] | 0.350 (+0.039) | -0.055 | 1.94 (+0.00) | -4.7 [-8.2, -1.1] | -1.4 |
| 24 | A1 · gate score, literal · consecutive-2 or t_high · consecutive-2 or t_high=q90 | 28.5 | 31.4 | **-0.4** [-2.6, +1.8] | [-3.3, +2.6] | -2.6 [-5.6, -0.3] | 0.314 (+0.002) | -0.003 | 1.94 (+0.00) | -4.6 [-7.7, -1.7] | -2.6 |
| 25 | A1 · gate score, R49-aligned · 2-of-n anywhere or t_high · 2-of-n anywhere or t_high=q90 | 29.6 | 31.7 | **-0.1** [-2.6, +2.3] | [-3.3, +3.1] | -1.5 [-3.6, -0.1] | 0.378 (+0.067) | -0.095 | 1.94 (+0.00) | -4.3 [-7.8, -0.8] | -1.5 |
| 26 | A1 · gate score, literal · 2-of-last-3 or t_high · 2-of-last-3 or t_high=q90 | 28.9 | 31.7 | **-0.1** [-2.0, +1.9] | [-2.7, +2.6] | -2.2 [-5.1, -0.2] | 0.359 (+0.048) | -0.068 | 1.94 (+0.00) | -4.3 [-7.4, -1.3] | -2.2 |
| 27 | A1 · gate score, literal · 2-of-n anywhere or t_high · 2-of-n anywhere or t_high=q90 | 28.9 | 32.1 | **+0.3** [-1.6, +2.4] | [-2.3, +3.1] | -2.2 [-5.1, -0.2] | 0.388 (+0.076) | -0.108 | 1.94 (+0.00) | -3.9 [-7.0, -0.9] | -2.2 |
| 28 | A1 · gate score, literal · consecutive-2 or t_high · consecutive-2 or t_high=q95 | 28.1 | 32.6 | **+0.8** [-1.8, +3.6] | [-2.7, +4.6] | -3.0 [-6.3, -0.5] | 0.331 (+0.019) | -0.028 | 1.94 (+0.00) | -3.4 [-6.3, -0.5] | -3.0 |
| 29 | A1 · gate score, R49-aligned · consecutive-2 or t_high · consecutive-2 or t_high=q975 | 28.4 | 32.7 | **+0.9** [-1.8, +3.7] | [-3.0, +4.8] | -2.7 [-5.9, -0.4] | 0.327 (+0.016) | -0.022 | 1.94 (+0.00) | -3.3 [-6.3, -0.2] | -2.7 |
| 30 | A1 · gate score, R49-aligned · 2-of-last-3 or t_high · 2-of-last-3 or t_high=q95 | 29.0 | 32.9 | **+1.1** [-1.3, +3.6] | [-2.3, +4.5] | -2.1 [-4.8, -0.2] | 0.368 (+0.056) | -0.080 | 1.94 (+0.00) | -3.1 [-6.3, +0.1] | -2.1 |
| 31 | A1 · gate score, literal · consecutive-2 or t_high · consecutive-2 or t_high=q975 | 28.1 | 32.9 | **+1.1** [-1.7, +3.9] | [-2.9, +5.0] | -3.0 [-6.3, -0.6] | 0.335 (+0.024) | -0.034 | 1.94 (+0.00) | -3.1 [-6.0, +0.0] | -3.0 |
| 32 | A1 · gate score, R49-aligned · 2-of-n anywhere or t_high · 2-of-n anywhere or t_high=q95 | 28.9 | 33.3 | **+1.5** [-1.1, +4.1] | [-2.1, +5.0] | -2.2 [-4.8, -0.3] | 0.397 (+0.085) | -0.121 | 1.94 (+0.00) | -2.7 [-6.0, +0.7] | -2.2 |
| 33 | A1 · gate score, literal · 2-of-last-3 or t_high · 2-of-last-3 or t_high=q95 | 28.4 | 33.6 | **+1.8** [-0.6, +4.4] | [-1.6, +5.3] | -2.7 [-6.0, -0.3] | 0.386 (+0.075) | -0.106 | 1.94 (+0.00) | -2.4 [-5.3, +0.7] | -2.7 |
| 34 | A1 · gate score, literal · 2-of-n anywhere or t_high · 2-of-n anywhere or t_high=q95 | 28.3 | 33.7 | **+1.9** [-0.5, +4.6] | [-1.5, +5.5] | -2.8 [-6.1, -0.4] | 0.410 (+0.099) | -0.140 | 1.94 (+0.00) | -2.3 [-5.3, +0.8] | -2.8 |
| 35 | A1 · stacked B1 gate score, aligned · consecutive-2 or t_high · consecutive-2 or t_high=q90 | 29.9 | 33.8 | **+2.0** [-1.2, +5.4] | [-2.4, +6.5] | -1.2 [-2.9, +0.1] | 0.358 (+0.047) | -0.067 | 2.27 (+0.33) | -2.2 [-5.1, +1.0] | -1.2 |
| 36 | A1 · gate score, literal · change from own mean · change from own mean, lambda=0.5 | 30.4 | 34.1 | **+2.3** [-0.1, +4.9] | [-0.9, +5.8] | -0.7 [-1.4, -0.1] | 0.229 (-0.082) | +0.116 | 1.94 (+0.00) | -1.9 [-5.5, +1.8] | -0.7 |
| 37 | A1 · stacked B1 gate score, aligned · consecutive-2 or t_high · consecutive-2 or t_high=q95 | 29.6 | 34.1 | **+2.3** [-0.9, +5.8] | [-2.0, +6.8] | -1.5 [-3.4, +0.0] | 0.358 (+0.047) | -0.066 | 2.27 (+0.33) | -1.9 [-4.8, +1.4] | -1.5 |
| 38 | A1 · H&E alone (max L-IMG) · consecutive-2 or t_high · consecutive-2 or t_high=q90 | 28.1 | 34.1 | **+2.3** [-0.4, +5.4] | [-1.4, +6.5] | -3.0 [-6.1, -0.6] | 0.339 (+0.027) | -0.039 | 0.00 (-1.94) | -1.9 [-4.1, +0.2] | -3.0 |
| 39 | A1 · gate score, literal · 2-of-last-3 or t_high · 2-of-last-3 or t_high=q975 | 28.3 | 34.2 | **+2.4** [-0.1, +5.1] | [-1.1, +6.0] | -2.8 [-6.1, -0.4] | 0.390 (+0.078) | -0.111 | 1.94 (+0.00) | -1.8 [-4.7, +1.3] | -2.8 |
| 40 | A1 · gate score, R49-aligned · 2-of-last-3 or t_high · 2-of-last-3 or t_high=q975 | 28.5 | 34.3 | **+2.5** [+0.1, +5.1] | [-0.8, +6.0] | -2.6 [-5.8, -0.3] | 0.384 (+0.073) | -0.103 | 1.94 (+0.00) | -1.7 [-4.6, +1.5] | -2.6 |

#### A2 / A2' certificates

Fixed hyper-parameter picked after seeing the evaluation (optimistic); the threshold is still the training-chosen one.

| # | Method | Caught | NP flagged | Δ NP flagged vs R49 [95% CI] | 99.2% CI | Δ caught [95% CI] | Flags / NP py (Δ) | Δ endoscopy spec. | Samples seq. / patient (Δ) | Δ NP flagged vs P1 90% [95% CI] | Δ caught vs P1 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | A2 copy-number certificate (gate) · t_quiet=p75, raise to 95%-spec, Y=4y | 30.8 | 26.9 | **-4.9** [-7.2, -2.9] | [-7.9, -2.5] | -0.3 [-0.8, +0.0] | 0.218 (-0.093) | +0.131 | 1.24 (-0.70) | -9.1 [-13.2, -5.1] | -0.3 |
| 2 | A2' p53-normal certificate (gate) · raise to 95%-spec, Y=4y | 30.6 | 26.9 | **-4.9** [-7.1, -2.9] | [-7.9, -2.2] | -0.5 [-1.1, +0.0] | 0.173 (-0.138) | +0.195 | 0.94 (-1.00) | -9.1 [-13.3, -5.2] | -0.5 |
| 3 | A2 copy-number certificate (gate) · t_quiet=p50, raise to 95%-spec, Y=4y | 30.9 | 27.7 | **-4.1** [-6.3, -2.1] | [-7.2, -1.7] | -0.2 [-0.7, +0.0] | 0.249 (-0.062) | +0.088 | 1.40 (-0.54) | -8.3 [-12.4, -4.3] | -0.2 |
| 4 | A2' p53-normal certificate (gate) · raise to 95%-spec, Y=2y | 31.1 | 29.1 | **-2.7** [-4.4, -1.3] | [-5.0, -0.8] | +0.0 [+0.0, +0.0] | 0.213 (-0.098) | +0.139 | 1.35 (-0.58) | -6.9 [-10.4, -3.6] | +0.0 |
| 5 | A2 copy-number certificate (gate) · t_quiet=p75, raise to 95%-spec, Y=2y | 31.1 | 29.7 | **-2.1** [-4.1, -0.6] | [-4.9, -0.4] | +0.0 [+0.0, +0.0] | 0.252 (-0.059) | +0.084 | 1.57 (-0.37) | -6.3 [-9.8, -2.8] | +0.0 |
| 6 | A2' p53-normal certificate (gate) · raise to 85%-spec, Y=4y | 31.0 | 29.7 | **-2.1** [-3.3, -1.1] | [-3.8, -0.8] | -0.1 [-0.3, +0.0] | 0.225 (-0.086) | +0.122 | 1.05 (-0.89) | -6.3 [-10.1, -2.9] | -0.1 |
| 7 | A2 copy-number certificate (gate) · t_quiet=p50, raise to 95%-spec, Y=2y | 31.1 | 30.1 | **-1.7** [-3.2, -0.5] | [-3.8, -0.3] | +0.0 [+0.0, +0.0] | 0.272 (-0.039) | +0.055 | 1.67 (-0.28) | -5.9 [-9.2, -2.5] | +0.0 |
| 8 | A2 copy-number certificate (gate) · t_quiet=p75, raise to 85%-spec, Y=4y | 31.0 | 30.2 | **-1.6** [-2.7, -0.7] | [-3.0, -0.4] | -0.1 [-0.3, +0.0] | 0.261 (-0.051) | +0.072 | 1.32 (-0.61) | -5.8 [-9.6, -2.3] | -0.1 |
| 9 | A2 copy-number certificate (gate) · t_quiet=p50, raise to 85%-spec, Y=4y | 31.0 | 30.5 | **-1.3** [-2.3, -0.4] | [-2.7, -0.2] | -0.1 [-0.3, +0.0] | 0.280 (-0.031) | +0.044 | 1.46 (-0.48) | -5.5 [-9.2, -2.0] | -0.1 |
| 10 | A2' p53-normal certificate (gate) · raise to 85%-spec, Y=2y | 31.1 | 30.6 | **-1.2** [-2.2, -0.4] | [-2.5, -0.2] | +0.0 [+0.0, +0.0] | 0.253 (-0.058) | +0.083 | 1.43 (-0.51) | -5.4 [-8.7, -2.4] | +0.0 |
| 11 | A2 copy-number certificate (gate) · t_quiet=p50, raise to 85%-spec, Y=2y | 31.1 | 31.4 | **-0.4** [-0.8, -0.1] | [-0.9, +0.0] | +0.0 [+0.0, +0.0] | 0.293 (-0.019) | +0.026 | 1.70 (-0.24) | -4.6 [-7.9, -1.5] | +0.0 |
| 12 | A2 copy-number certificate (gate) · t_quiet=p75, raise to 85%-spec, Y=2y | 31.1 | 31.4 | **-0.4** [-0.8, -0.1] | [-0.9, +0.0] | +0.0 [+0.0, +0.0] | 0.282 (-0.030) | +0.042 | 1.63 (-0.31) | -4.6 [-7.9, -1.5] | +0.0 |
| 13 | A2 copy-number certificate (gate) · no certificate (= R49) | 31.1 | 31.8 | **+0.0** [+0.0, +0.0] | [+0.0, +0.0] | +0.0 [+0.0, +0.0] | 0.311 (+0.000) | +0.000 | 1.94 (+0.00) | -4.2 [-7.4, -1.2] | +0.0 |
| 14 | A2' p53-normal certificate (gate) · no certificate (= R49) | 31.1 | 31.8 | **+0.0** [+0.0, +0.0] | [+0.0, +0.0] | +0.0 [+0.0, +0.0] | 0.311 (+0.000) | +0.000 | 1.94 (+0.00) | -4.2 [-7.4, -1.2] | +0.0 |

#### A3 agreement

Fixed hyper-parameter picked after seeing the evaluation (optimistic); the threshold is still the training-chosen one.

| # | Method | Caught | NP flagged | Δ NP flagged vs R49 [95% CI] | 99.2% CI | Δ caught [95% CI] | Flags / NP py (Δ) | Δ endoscopy spec. | Samples seq. / patient (Δ) | Δ NP flagged vs P1 90% [95% CI] | Δ caught vs P1 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | A3 agreement within endoscopy · gate: t_mid=50% sens, t_cnv=80% sens | 30.7 | 31.1 | **-0.7** [-1.4, -0.1] | [-1.8, +0.0] | -0.4 [-1.1, +0.0] | 0.294 (-0.017) | +0.024 | 2.23 (+0.29) | -4.9 [-8.4, -1.6] | -0.4 |
| 2 | A3 agreement within endoscopy · gate: t_mid=50% sens, t_cnv=90% sens | 30.9 | 31.2 | **-0.6** [-1.1, -0.1] | [-1.4, +0.0] | -0.2 [-0.5, +0.0] | 0.299 (-0.012) | +0.017 | 2.23 (+0.29) | -4.8 [-8.2, -1.6] | -0.2 |
| 3 | A3 agreement within endoscopy · gate: t_mid=80% sens, t_cnv=80% sens | 31.0 | 31.5 | **-0.3** [-0.7, +0.0] | [-0.8, +0.0] | -0.1 [-0.3, +0.0] | 0.304 (-0.007) | +0.010 | 2.08 (+0.14) | -4.5 [-7.9, -1.4] | -0.1 |
| 4 | A3 agreement within endoscopy · gate: t_mid=80% sens, t_cnv=90% sens | 31.0 | 31.5 | **-0.3** [-0.7, +0.0] | [-0.8, +0.0] | -0.1 [-0.3, +0.0] | 0.305 (-0.006) | +0.008 | 2.08 (+0.14) | -4.5 [-7.9, -1.4] | -0.1 |
| 5 | A3 agreement within endoscopy · no agreement rule (= R49) | 31.1 | 31.8 | **+0.0** [+0.0, +0.0] | [+0.0, +0.0] | +0.0 [+0.0, +0.0] | 0.311 (+0.000) | +0.000 | 1.94 (+0.00) | -4.2 [-7.4, -1.2] | +0.0 |
| 6 | A3 agreement within endoscopy · H&E alone: t_mid=50% sens, t_cnv=90% sens | 30.9 | 31.8 | **+0.0** [-1.8, +2.0] | [-2.4, +2.8] | -0.2 [-1.6, +0.9] | 0.262 (-0.049) | +0.069 | 0.85 (-1.09) | -4.2 [-7.3, -1.4] | -0.2 |
| 7 | A3 agreement within endoscopy · H&E alone: t_mid=80% sens, t_cnv=80% sens | 30.7 | 31.9 | **+0.1** [-1.8, +2.1] | [-2.4, +2.9] | -0.4 [-1.7, +0.5] | 0.266 (-0.045) | +0.064 | 0.47 (-1.47) | -4.1 [-7.1, -1.5] | -0.4 |
| 8 | A3 agreement within endoscopy · H&E alone: t_mid=80% sens, t_cnv=90% sens | 31.0 | 33.2 | **+1.4** [-0.4, +3.3] | [-1.0, +4.0] | -0.1 [-1.4, +0.9] | 0.281 (-0.031) | +0.043 | 0.47 (-1.47) | -2.8 [-5.0, -0.8] | -0.1 |
| 9 | A3 agreement within endoscopy · H&E alone: t_mid=50% sens, t_cnv=80% sens | 30.5 | 29.9 | **-1.9** [-4.3, +0.6] | [-5.0, +1.5] | -0.6 [-2.0, +0.4] | 0.240 (-0.071) | +0.101 | 0.87 (-1.07) | -6.1 [-10.1, -2.5] | -0.6 |

#### B3 abstention

Fixed hyper-parameter picked after seeing the evaluation (optimistic); the threshold is still the training-chosen one.

| # | Method | Caught | NP flagged | Δ NP flagged vs R49 [95% CI] | 99.2% CI | Δ caught [95% CI] | Flags / NP py (Δ) | Δ endoscopy spec. | Samples seq. / patient (Δ) | Δ NP flagged vs P1 90% [95% CI] | Δ caught vs P1 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | B3 abstention in middle band · indeterminate share 20% | 31.1 | 30.1 | **-1.7** [-2.6, -0.9] | [-2.9, -0.7] | +0.0 [+0.0, +0.0] | 0.272 (-0.040) | +0.056 | 1.94 (+0.00) | -5.9 [-9.6, -2.6] | +0.0 |
| 2 | B3 abstention in middle band · indeterminate share 10% | 31.1 | 30.6 | **-1.2** [-2.0, -0.5] | [-2.3, -0.3] | +0.0 [+0.0, +0.0] | 0.290 (-0.022) | +0.030 | 1.94 (+0.00) | -5.4 [-9.0, -2.1] | +0.0 |
| 3 | B3 abstention in middle band · no abstention (= R49) | 31.1 | 31.8 | **+0.0** [+0.0, +0.0] | [+0.0, +0.0] | +0.0 [+0.0, +0.0] | 0.311 (+0.000) | +0.000 | 1.94 (+0.00) | -4.2 [-7.4, -1.2] | +0.0 |

#### A1+A2 and B1+A1+A2 combined

Fixed hyper-parameter picked after seeing the evaluation (optimistic); the threshold is still the training-chosen one.

| # | Method | Caught | NP flagged | Δ NP flagged vs R49 [95% CI] | 99.2% CI | Δ caught [95% CI] | Flags / NP py (Δ) | Δ endoscopy spec. | Samples seq. / patient (Δ) | Δ NP flagged vs P1 90% [95% CI] | Δ caught vs P1 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | A1+A2: EW memory of gate score + copy-number certificate · ew h=1y, t_quiet=p75, +1.0 logit, Y=2y | 31.0 | 23.9 | **-7.9** [-11.0, -5.1] | [-12.4, -4.0] | -0.1 [-0.8, +0.6] | 0.205 (-0.107) | +0.150 | 1.94 (+0.00) | -12.1 [-16.5, -7.7] | -0.1 |
| 2 | A1+A2: EW memory of gate score + copy-number certificate · ew h=1y, t_quiet=p50, +0.5 logit, Y=4y | 31.0 | 24.0 | **-7.8** [-10.9, -4.9] | [-12.3, -4.1] | -0.1 [-0.6, +0.5] | 0.228 (-0.083) | +0.117 | 1.94 (+0.00) | -12.0 [-16.4, -7.6] | -0.1 |
| 3 | A1+A2: EW memory of gate score + copy-number certificate · ew h=1y, t_quiet=p50, +1.0 logit, Y=4y | 31.1 | 24.1 | **-7.7** [-10.9, -4.7] | [-12.4, -3.8] | +0.0 [-0.4, +0.5] | 0.225 (-0.087) | +0.122 | 1.94 (+0.00) | -11.9 [-16.1, -7.6] | +0.0 |
| 4 | A1+A2: EW memory of gate score + copy-number certificate · ew h=1y, t_quiet=p75, +0.5 logit, Y=4y | 31.1 | 24.2 | **-7.6** [-10.8, -4.6] | [-12.3, -3.9] | +0.0 [-0.5, +0.5] | 0.222 (-0.089) | +0.126 | 1.94 (+0.00) | -11.8 [-16.1, -7.5] | +0.0 |
| 5 | A1+A2: EW memory of gate score + copy-number certificate · ew h=1y, t_quiet=p75, +0.5 logit, Y=2y | 30.9 | 24.2 | **-7.6** [-10.6, -4.8] | [-12.0, -3.9] | -0.2 [-0.8, +0.3] | 0.218 (-0.093) | +0.131 | 1.94 (+0.00) | -11.8 [-16.2, -7.4] | -0.2 |
| 6 | A1+A2: EW memory of gate score + copy-number certificate · ew h=1y, t_quiet=p75, +1.0 logit, Y=4y | 31.1 | 24.4 | **-7.4** [-10.6, -4.4] | [-12.0, -3.5] | +0.0 [-0.6, +0.8] | 0.209 (-0.102) | +0.144 | 1.94 (+0.00) | -11.6 [-15.7, -7.4] | +0.0 |
| 7 | A1+A2: EW memory of gate score + copy-number certificate · ew h=2y, t_quiet=p50, +1.0 logit, Y=4y | 31.2 | 24.6 | **-7.2** [-10.7, -3.8] | [-11.9, -2.7] | +0.1 [-0.9, +1.2] | 0.238 (-0.073) | +0.103 | 1.94 (+0.00) | -11.4 [-15.6, -7.1] | +0.1 |
| 8 | A1+A2: EW memory of gate score + copy-number certificate · ew h=2y, t_quiet=p50, +0.5 logit, Y=4y | 31.1 | 24.6 | **-7.2** [-10.8, -3.8] | [-12.1, -2.6] | +0.0 [-1.0, +1.0] | 0.253 (-0.059) | +0.083 | 1.94 (+0.00) | -11.4 [-15.7, -7.1] | +0.0 |
| 9 | A1+A2: EW memory of gate score + copy-number certificate · ew h=4y, t_quiet=p50, +0.5 logit, Y=4y | 31.2 | 24.7 | **-7.1** [-11.0, -3.4] | [-12.6, -2.3] | +0.1 [-1.0, +1.2] | 0.271 (-0.041) | +0.057 | 1.94 (+0.00) | -11.3 [-15.6, -7.1] | +0.1 |
| 10 | A1+A2: EW memory of gate score + copy-number certificate · ew h=4y, t_quiet=p75, +1.0 logit, Y=2y | 31.2 | 24.7 | **-7.1** [-11.1, -3.3] | [-12.7, -2.0] | +0.1 [-1.1, +1.5] | 0.244 (-0.068) | +0.095 | 1.94 (+0.00) | -11.3 [-15.6, -7.0] | +0.1 |
| 11 | A1+A2: EW memory of gate score + copy-number certificate · ew h=2y, t_quiet=p75, +0.5 logit, Y=4y | 31.0 | 24.7 | **-7.1** [-10.8, -3.7] | [-12.3, -2.7] | -0.1 [-1.2, +0.9] | 0.247 (-0.064) | +0.091 | 1.94 (+0.00) | -11.3 [-15.5, -6.9] | -0.1 |
| 12 | A1+A2: EW memory of gate score + copy-number certificate · ew h=1y, t_quiet=p50, +1.0 logit, Y=2y | 30.9 | 24.7 | **-7.1** [-10.1, -4.3] | [-11.7, -3.4] | -0.2 [-0.8, +0.3] | 0.221 (-0.090) | +0.128 | 1.94 (+0.00) | -11.3 [-15.7, -6.9] | -0.2 |
| 13 | A1+A2: EW memory of gate score + copy-number certificate · ew h=2y, t_quiet=p75, +0.5 logit, Y=2y | 30.9 | 24.7 | **-7.1** [-10.6, -3.8] | [-11.8, -2.7] | -0.2 [-1.2, +0.7] | 0.245 (-0.066) | +0.093 | 1.94 (+0.00) | -11.3 [-15.5, -7.0] | -0.2 |
| 14 | A1+A2: EW memory of gate score + copy-number certificate · ew h=4y, t_quiet=p50, +1.0 logit, Y=4y | 31.3 | 24.8 | **-7.0** [-10.8, -3.3] | [-12.3, -2.2] | +0.2 [-0.9, +1.5] | 0.253 (-0.058) | +0.082 | 1.94 (+0.00) | -11.2 [-15.5, -6.9] | +0.2 |
| 15 | A1+A2: EW memory of gate score + copy-number certificate · ew h=4y, t_quiet=p75, +0.5 logit, Y=4y | 31.1 | 24.8 | **-7.0** [-10.9, -3.4] | [-12.2, -2.0] | +0.0 [-1.1, +1.2] | 0.265 (-0.046) | +0.065 | 1.94 (+0.00) | -11.2 [-15.4, -7.0] | +0.0 |
| 16 | A1+A2: EW memory of gate score + copy-number certificate · ew h=2y, t_quiet=p75, +1.0 logit, Y=2y | 31.0 | 24.8 | **-7.0** [-10.6, -3.7] | [-11.7, -2.4] | -0.1 [-1.2, +1.0] | 0.225 (-0.086) | +0.122 | 1.94 (+0.00) | -11.2 [-15.4, -6.9] | -0.1 |
| 17 | A1+A2: EW memory of gate score + copy-number certificate · ew h=4y, t_quiet=p50, +1.0 logit, Y=2y | 31.1 | 24.9 | **-6.9** [-10.8, -3.2] | [-12.5, -1.9] | +0.0 [-1.1, +1.2] | 0.260 (-0.052) | +0.073 | 1.94 (+0.00) | -11.1 [-15.5, -6.8] | +0.0 |
| 18 | A1+A2: EW memory of gate score + copy-number certificate · ew h=4y, t_quiet=p75, +0.5 logit, Y=2y | 31.1 | 24.9 | **-6.9** [-10.8, -3.2] | [-12.6, -2.0] | +0.0 [-1.1, +1.2] | 0.266 (-0.045) | +0.064 | 1.94 (+0.00) | -11.1 [-15.4, -6.8] | +0.0 |
| 19 | A1+A2: EW memory of gate score + copy-number certificate · ew h=4y, t_quiet=p50, +0.5 logit, Y=2y | 31.1 | 25.0 | **-6.8** [-10.7, -3.1] | [-12.4, -1.9] | +0.0 [-1.1, +1.2] | 0.272 (-0.039) | +0.055 | 1.94 (+0.00) | -11.0 [-15.3, -6.7] | +0.0 |
| 20 | A1+A2: EW memory of gate score + copy-number certificate · ew h=1y, t_quiet=p50, +0.5 logit, Y=2y | 30.9 | 25.0 | **-6.8** [-9.8, -4.1] | [-11.2, -3.2] | -0.2 [-0.8, +0.3] | 0.229 (-0.082) | +0.116 | 1.94 (+0.00) | -11.0 [-15.4, -6.6] | -0.2 |

#### B1 stacked gate and controls (cut-off cells)

Fixed hyper-parameter picked after seeing the evaluation (optimistic); the threshold is still the training-chosen one.

| # | Method | Caught | NP flagged | Δ NP flagged vs R49 [95% CI] | 99.2% CI | Δ caught [95% CI] | Flags / NP py (Δ) | Δ endoscopy spec. | Samples seq. / patient (Δ) | Δ NP flagged vs P1 90% [95% CI] | Δ caught vs P1 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | B1-img control: stacked gate on L-IMG only (endoscopy-level cut-offs) · cut-offs 95/95/70 | 30.6 | 24.4 | **-7.4** [-9.9, -5.0] | [-11.1, -4.2] | -0.5 [-1.2, +0.0] | 0.176 (-0.136) | +0.192 | 2.17 (+0.23) | -11.6 [-16.1, -7.3] | -0.5 |
| 2 | B1-img control: stacked gate on L-IMG only (endoscopy-level cut-offs) · cut-offs 98/95/70 | 30.7 | 25.5 | **-6.3** [-8.7, -4.1] | [-9.7, -3.4] | -0.4 [-1.1, +0.0] | 0.196 (-0.115) | +0.162 | 2.57 (+0.63) | -10.5 [-14.9, -6.3] | -0.4 |
| 3 | B1-img control: stacked gate on L-IMG only (endoscopy-level cut-offs) · cut-offs 95/90/70 | 30.6 | 26.3 | **-5.5** [-7.5, -3.6] | [-8.4, -2.8] | -0.5 [-1.2, +0.0] | 0.201 (-0.110) | +0.156 | 1.91 (-0.03) | -9.7 [-13.8, -5.9] | -0.5 |
| 4 | control: R49 with cut-offs re-tuned by the round-9 rule · cut-offs 90/95/70 | 30.6 | 26.9 | **-4.9** [-6.7, -3.2] | [-7.3, -2.6] | -0.5 [-1.2, +0.0] | 0.200 (-0.111) | +0.157 | 1.90 (-0.04) | -9.1 [-13.2, -5.1] | -0.5 |
| 5 | B1-img control: stacked gate on L-IMG only (endoscopy-level cut-offs) · cut-offs 98/90/70 | 30.8 | 27.2 | **-4.6** [-6.4, -2.9] | [-7.2, -2.3] | -0.3 [-1.0, +0.0] | 0.224 (-0.087) | +0.123 | 2.30 (+0.36) | -8.8 [-12.8, -5.1] | -0.3 |
| 6 | B1-img control: stacked gate on L-IMG only (endoscopy-level cut-offs) · cut-offs 95/95/80 | 30.7 | 27.7 | **-4.1** [-6.0, -2.4] | [-6.8, -1.9] | -0.4 [-1.1, +0.0] | 0.230 (-0.081) | +0.115 | 2.17 (+0.23) | -8.3 [-12.3, -4.6] | -0.4 |
| 7 | control: R49 with cut-offs re-tuned by the round-9 rule · cut-offs 95/95/70 | 30.8 | 27.8 | **-4.0** [-5.5, -2.6] | [-5.9, -2.2] | -0.3 [-0.8, +0.0] | 0.230 (-0.082) | +0.116 | 2.25 (+0.30) | -8.2 [-12.1, -4.5] | -0.3 |
| 8 | control: R49 with cut-offs re-tuned by the round-9 rule · cut-offs 98/95/70 | 30.8 | 28.3 | **-3.5** [-4.9, -2.2] | [-5.4, -1.8] | -0.3 [-0.8, +0.0] | 0.245 (-0.066) | +0.093 | 2.59 (+0.65) | -7.7 [-11.6, -3.9] | -0.3 |
| 9 | B1-img control: stacked gate on L-IMG only (endoscopy-level cut-offs) · cut-offs 95/85/70 | 30.6 | 28.3 | **-3.5** [-5.1, -2.0] | [-5.8, -1.7] | -0.5 [-1.2, +0.0] | 0.224 (-0.088) | +0.124 | 1.75 (-0.20) | -7.7 [-11.6, -4.1] | -0.5 |
| 10 | B1-img control: stacked gate on L-IMG only (endoscopy-level cut-offs) · cut-offs 98/95/80 | 31.0 | 28.4 | **-3.4** [-5.0, -2.0] | [-5.5, -1.7] | -0.1 [-0.3, +0.0] | 0.258 (-0.054) | +0.076 | 2.57 (+0.63) | -7.6 [-11.4, -4.1] | -0.1 |
| 11 | B1 + p53 (aberrant, missing) · cut-offs 98/95/70 | 30.6 | 28.7 | **-3.1** [-4.7, -1.5] | [-5.2, -1.1] | -0.5 [-1.0, -0.1] | 0.255 (-0.056) | +0.080 | 2.82 (+0.88) | -7.3 [-11.1, -3.7] | -0.5 |
| 12 | B1-img control: stacked gate on L-IMG only (endoscopy-level cut-offs) · cut-offs 95/90/80 | 30.9 | 28.9 | **-2.9** [-4.3, -1.7] | [-4.9, -1.4] | -0.2 [-0.5, +0.0] | 0.257 (-0.055) | +0.077 | 1.91 (-0.03) | -7.1 [-10.9, -3.7] | -0.2 |
| 13 | B1-img control: stacked gate on L-IMG only (endoscopy-level cut-offs) · cut-offs 98/85/70 | 30.9 | 29.0 | **-2.8** [-4.2, -1.5] | [-4.9, -1.2] | -0.2 [-0.7, +0.0] | 0.247 (-0.065) | +0.091 | 2.14 (+0.20) | -7.0 [-11.0, -3.4] | -0.2 |
| 14 | B1 stacked gate (L-IMG, grade, age, sex; + L-CNV in middle band) · cut-offs 98/95/70 | 30.7 | 29.0 | **-2.8** [-4.1, -1.5] | [-4.6, -1.0] | -0.4 [-0.9, +0.0] | 0.241 (-0.070) | +0.099 | 2.87 (+0.93) | -7.0 [-10.7, -3.4] | -0.4 |
| 15 | control: R49 with cut-offs re-tuned by the round-9 rule · cut-offs 90/90/70 | 30.8 | 29.1 | **-2.7** [-4.0, -1.6] | [-4.4, -1.3] | -0.3 [-0.6, +0.0] | 0.231 (-0.081) | +0.114 | 1.59 (-0.35) | -6.9 [-10.7, -3.4] | -0.3 |
| 16 | B1 stacked gate (L-IMG, grade, age, sex; + L-CNV in middle band) · cut-offs 95/90/70 | 30.6 | 29.1 | **-2.7** [-4.1, -1.3] | [-4.5, -0.8] | -0.5 [-1.2, +0.0] | 0.246 (-0.065) | +0.092 | 2.27 (+0.33) | -6.9 [-10.6, -3.4] | -0.5 |
| 17 | control: R49 with cut-offs re-tuned by the round-9 rule · cut-offs 95/90/70 | 30.9 | 29.6 | **-2.2** [-3.5, -1.2] | [-4.0, -0.9] | -0.2 [-0.5, +0.0] | 0.262 (-0.050) | +0.070 | 1.94 (+0.00) | -6.4 [-10.1, -3.0] | -0.2 |
| 18 | control: R49 with cut-offs re-tuned by the round-9 rule · cut-offs 90/95/80 | 30.9 | 29.8 | **-2.0** [-3.0, -1.1] | [-3.6, -0.9] | -0.2 [-0.5, +0.0] | 0.251 (-0.061) | +0.085 | 1.90 (-0.04) | -6.2 [-9.7, -3.0] | -0.2 |
| 19 | B1 + p53 (aberrant, missing) · cut-offs 98/90/70 | 30.8 | 29.8 | **-2.0** [-3.4, -0.6] | [-3.9, -0.1] | -0.3 [-0.7, +0.0] | 0.277 (-0.034) | +0.048 | 2.60 (+0.66) | -6.2 [-9.7, -2.8] | -0.3 |
| 20 | B1 stacked gate (L-IMG, grade, age, sex; + L-CNV in middle band) · cut-offs 98/90/70 | 30.9 | 30.1 | **-1.7** [-3.0, -0.3] | [-3.5, +0.0] | -0.2 [-0.5, +0.0] | 0.266 (-0.045) | +0.064 | 2.61 (+0.67) | -5.9 [-9.6, -2.3] | -0.2 |
| 21 | B1 + p53 (aberrant, missing) · cut-offs 95/85/70 | 30.7 | 30.2 | **-1.6** [-3.0, -0.2] | [-3.5, +0.2] | -0.4 [-0.9, +0.0] | 0.280 (-0.032) | +0.045 | 2.08 (+0.14) | -5.8 [-9.2, -2.6] | -0.4 |
| 22 | control: R49 with cut-offs re-tuned by the round-9 rule · cut-offs 98/90/70 | 31.0 | 30.3 | **-1.5** [-2.5, -0.7] | [-2.9, -0.5] | -0.1 [-0.3, +0.0] | 0.284 (-0.028) | +0.039 | 2.29 (+0.35) | -5.7 [-9.5, -2.1] | -0.1 |
| 23 | B1 stacked gate (L-IMG, grade, age, sex; + L-CNV in middle band) · cut-offs 95/85/70 | 30.7 | 30.3 | **-1.5** [-2.8, -0.2] | [-3.3, +0.2] | -0.4 [-1.1, +0.0] | 0.265 (-0.046) | +0.065 | 2.07 (+0.13) | -5.7 [-9.3, -2.2] | -0.4 |
| 24 | B1-img control: stacked gate on L-IMG only (endoscopy-level cut-offs) · cut-offs 98/90/80 | 31.1 | 30.4 | **-1.4** [-2.6, -0.3] | [-3.1, -0.0] | +0.0 [-0.3, +0.3] | 0.284 (-0.028) | +0.039 | 2.30 (+0.36) | -5.6 [-9.0, -2.3] | +0.0 |
| 25 | control: R49 with cut-offs re-tuned by the round-9 rule · cut-offs 90/85/70 | 30.9 | 30.5 | **-1.3** [-2.1, -0.6] | [-2.5, -0.3] | -0.2 [-0.5, +0.0] | 0.259 (-0.053) | +0.075 | 1.33 (-0.61) | -5.5 [-9.2, -2.2] | -0.2 |
| 26 | control: R49 with cut-offs re-tuned by the round-9 rule · cut-offs 95/95/80 | 31.1 | 30.6 | **-1.2** [-1.9, -0.6] | [-2.2, -0.3] | +0.0 [+0.0, +0.0] | 0.281 (-0.030) | +0.042 | 2.25 (+0.30) | -5.4 [-8.9, -2.2] | +0.0 |
| 27 | B1-img control: stacked gate on L-IMG only (endoscopy-level cut-offs) · cut-offs 95/85/80 | 31.0 | 30.6 | **-1.2** [-2.0, -0.5] | [-2.3, -0.3] | -0.1 [-0.4, +0.2] | 0.273 (-0.038) | +0.054 | 1.75 (-0.20) | -5.4 [-8.9, -2.2] | -0.1 |
| 28 | control: R49 with cut-offs re-tuned by the round-9 rule · cut-offs 95/85/70 | 31.1 | 30.9 | **-0.9** [-1.7, -0.3] | [-2.0, -0.2] | +0.0 [+0.0, +0.0] | 0.286 (-0.026) | +0.036 | 1.68 (-0.26) | -5.1 [-8.8, -1.8] | +0.0 |
| 29 | B1 + p53 (aberrant, missing) · cut-offs 98/85/70 | 31.0 | 31.0 | **-0.8** [-2.2, +0.7] | [-2.7, +1.1] | -0.1 [-0.4, +0.2] | 0.304 (-0.008) | +0.011 | 2.39 (+0.45) | -5.0 [-8.4, -1.8] | -0.1 |
| 30 | control: R49 with cut-offs re-tuned by the round-9 rule · cut-offs 90/90/80 | 31.0 | 31.0 | **-0.8** [-1.6, -0.2] | [-1.8, +0.0] | -0.1 [-0.3, +0.0] | 0.275 (-0.036) | +0.051 | 1.59 (-0.35) | -5.0 [-8.3, -1.9] | -0.1 |

#### B4 refits (re-tuned cut-off cells)

Fixed hyper-parameter picked after seeing the evaluation (optimistic); the threshold is still the training-chosen one.

| # | Method | Caught | NP flagged | Δ NP flagged vs R49 [95% CI] | 99.2% CI | Δ caught [95% CI] | Flags / NP py (Δ) | Δ endoscopy spec. | Samples seq. / patient (Δ) | Δ NP flagged vs P1 90% [95% CI] | Δ caught vs P1 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | B4(a) refit, non-progressor weight 2, cut-offs re-tuned by the round-9 rule · cut-offs 90/95/70 | 30.8 | 26.9 | **-4.9** [-6.8, -3.1] | [-7.6, -2.5] | -0.3 [-1.1, +0.2] | 0.194 (-0.117) | +0.166 | 1.96 (+0.02) | -9.1 [-13.3, -5.1] | -0.3 |
| 2 | B4(a) refit, non-progressor weight 2, cut-offs re-tuned by the round-9 rule · cut-offs 95/95/70 | 30.9 | 27.2 | **-4.6** [-6.3, -2.9] | [-6.9, -2.4] | -0.2 [-0.7, +0.2] | 0.219 (-0.092) | +0.130 | 2.31 (+0.37) | -8.8 [-13.0, -4.8] | -0.2 |
| 3 | B4(a) refit, non-progressor weight 2, cut-offs re-tuned by the round-9 rule · cut-offs 98/95/70 | 30.9 | 27.7 | **-4.1** [-5.8, -2.5] | [-6.3, -2.0] | -0.2 [-0.7, +0.2] | 0.243 (-0.069) | +0.097 | 2.63 (+0.69) | -8.3 [-12.5, -4.2] | -0.2 |
| 4 | B4(a) refit, non-progressor weight 2, cut-offs re-tuned by the round-9 rule · cut-offs 90/90/70 | 31.0 | 28.6 | **-3.2** [-4.6, -1.9] | [-5.3, -1.4] | -0.1 [-0.5, +0.2] | 0.230 (-0.082) | +0.116 | 1.63 (-0.31) | -7.4 [-11.4, -3.6] | -0.1 |
| 5 | B4(a) refit, non-progressor weight 2, cut-offs re-tuned by the round-9 rule · cut-offs 90/95/80 | 31.1 | 28.8 | **-3.0** [-4.3, -1.8] | [-4.8, -1.4] | +0.0 [-0.3, +0.3] | 0.246 (-0.065) | +0.093 | 1.96 (+0.02) | -7.2 [-11.1, -3.6] | +0.0 |
| 6 | B4(a) refit, non-progressor weight 2, cut-offs re-tuned by the round-9 rule · cut-offs 95/90/70 | 31.1 | 28.9 | **-2.9** [-4.2, -1.7] | [-4.9, -1.2] | +0.0 [-0.3, +0.3] | 0.253 (-0.058) | +0.082 | 1.98 (+0.04) | -7.1 [-11.0, -3.4] | +0.0 |
| 7 | B4(a) refit, non-progressor weight 2, cut-offs re-tuned by the round-9 rule · cut-offs 95/95/80 | 31.1 | 29.8 | **-2.0** [-3.1, -1.1] | [-3.5, -0.8] | +0.0 [-0.3, +0.3] | 0.278 (-0.034) | +0.047 | 2.31 (+0.37) | -6.2 [-10.0, -2.6] | +0.0 |
| 8 | B4(a) refit, non-progressor weight 2, cut-offs re-tuned by the round-9 rule · cut-offs 98/90/70 | 31.1 | 29.9 | **-1.9** [-3.3, -0.6] | [-3.8, -0.2] | +0.0 [-0.3, +0.3] | 0.286 (-0.026) | +0.036 | 2.29 (+0.35) | -6.1 [-10.2, -2.1] | +0.0 |
| 9 | B4(a) refit, non-progressor weight 2, cut-offs re-tuned by the round-9 rule · cut-offs 90/85/70 | 31.1 | 30.0 | **-1.8** [-2.8, -0.9] | [-3.2, -0.6] | +0.0 [-0.3, +0.3] | 0.259 (-0.052) | +0.074 | 1.35 (-0.59) | -6.0 [-9.6, -2.6] | +0.0 |
| 10 | B4(a) refit, non-progressor weight 2, cut-offs re-tuned by the round-9 rule · cut-offs 90/90/80 | 31.2 | 30.2 | **-1.6** [-2.6, -0.7] | [-2.9, -0.5] | +0.1 [+0.0, +0.3] | 0.271 (-0.040) | +0.056 | 1.63 (-0.31) | -5.8 [-9.5, -2.3] | +0.1 |
| 11 | B4(b) refit, NDBE samples only, cut-offs re-tuned by the round-9 rule · cut-offs 98/95/70 | 30.6 | 30.4 | **-1.4** [-4.4, +1.8] | [-5.5, +3.3] | -0.5 [-1.5, +0.2] | 0.289 (-0.023) | +0.032 | 2.90 (+0.96) | -5.6 [-9.8, -1.2] | -0.5 |
| 12 | B4(a) refit, non-progressor weight 2, cut-offs re-tuned by the round-9 rule · cut-offs 95/85/70 | 31.1 | 30.7 | **-1.1** [-1.9, -0.3] | [-2.1, -0.2] | +0.0 [-0.3, +0.3] | 0.285 (-0.026) | +0.037 | 1.70 (-0.24) | -5.3 [-8.8, -2.0] | +0.0 |
| 13 | B4(a) refit, non-progressor weight 2, cut-offs re-tuned by the round-9 rule · cut-offs 98/95/80 | 31.3 | 31.4 | **-0.4** [-1.5, +0.8] | [-1.9, +1.1] | +0.2 [+0.0, +0.5] | 0.312 (+0.001) | -0.002 | 2.63 (+0.69) | -4.6 [-8.5, -0.8] | +0.2 |
| 14 | B4(a) refit, non-progressor weight 2, cut-offs re-tuned by the round-9 rule · cut-offs 98/85/70 | 31.2 | 31.8 | **+0.0** [-1.0, +1.2] | [-1.3, +1.6] | +0.1 [+0.0, +0.3] | 0.314 (+0.003) | -0.004 | 2.02 (+0.08) | -4.2 [-7.9, -0.6] | +0.1 |
| 15 | B4(b) refit, NDBE samples only, cut-offs re-tuned by the round-9 rule · cut-offs 95/90/70 | 30.6 | 31.8 | **+0.0** [-3.0, +3.0] | [-3.9, +4.5] | -0.5 [-1.5, +0.2] | 0.304 (-0.007) | +0.010 | 2.31 (+0.38) | -4.2 [-8.4, +0.2] | -0.5 |

### Evaluation-matched versions (optimistic)

Threshold set on the evaluation patients, per repeat, so that progressor patients caught equals R49's (re-matched in every bootstrap draw). Score-type methods only (candidates: the progressor patients' own scores); the number shown is the 30 best.

| # | Method | Caught | NP flagged | Δ NP flagged vs R49 [95% CI] | 99.2% CI | Δ caught [95% CI] | Flags / NP py (Δ) | Δ endoscopy spec. | Samples seq. / patient (Δ) | Δ NP flagged vs P1 90% [95% CI] | Δ caught vs P1 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | A4 confirm-by-sequencing · gate with the high band also sequenced (score 0 = flag boundary) · exponentially weighted mean · ew h=1y [evaluation-matched] | 31.1 | 18.4 | **-13.4** [-21.2, -11.1] | [-22.9, -10.2] | +0.0 [+0.0, +0.0] | 0.161 (-0.150) | +0.212 | 3.15 (+1.21) | -17.6 [-25.5, -14.0] | +0.0 |
| 2 | A4 confirm-by-sequencing · gate with the high band also sequenced (score 0 = flag boundary) · exponentially weighted mean · ew h=2y [evaluation-matched] | 31.1 | 18.7 | **-13.1** [-21.1, -10.5] | [-23.0, -9.5] | +0.0 [+0.0, +0.0] | 0.180 (-0.131) | +0.185 | 3.15 (+1.21) | -17.3 [-25.7, -13.5] | +0.0 |
| 3 | Sample aggregation · max L-LATE (sequence all samples) · exponentially weighted mean · ew h=2y [evaluation-matched] | 31.1 | 18.9 | **-12.9** [-21.5, -10.4] | [-24.0, -8.6] | +0.0 [+0.0, +0.0] | 0.200 (-0.112) | +0.158 | 7.61 (+5.67) | -17.1 [-26.0, -13.2] | +0.0 |
| 4 | Sample aggregation · max L-LATE (sequence all samples) · exponentially weighted mean · ew h=4y [evaluation-matched] | 31.1 | 19.0 | **-12.8** [-20.9, -10.0] | [-23.6, -8.8] | +0.0 [+0.0, +0.0] | 0.216 (-0.096) | +0.136 | 7.61 (+5.67) | -17.0 [-25.5, -13.0] | +0.0 |
| 5 | A4 confirm-by-sequencing · gate with the high band also sequenced (score 0 = flag boundary) · exponentially weighted mean · ew h=4y [evaluation-matched] | 31.1 | 19.0 | **-12.8** [-20.4, -10.4] | [-22.5, -9.1] | +0.0 [+0.0, +0.0] | 0.198 (-0.114) | +0.160 | 3.15 (+1.21) | -17.0 [-24.8, -13.6] | +0.0 |
| 6 | Sample aggregation · max L-LATE (sequence all samples) · exponentially weighted mean · ew h=1y [evaluation-matched] | 31.1 | 19.4 | **-12.4** [-20.9, -9.9] | [-23.3, -8.5] | +0.0 [+0.0, +0.0] | 0.178 (-0.133) | +0.188 | 7.61 (+5.67) | -16.6 [-25.6, -12.8] | +0.0 |
| 7 | A4 confirm-by-sequencing · gate with the high band also sequenced (score 0 = flag boundary) · running mean [evaluation-matched] | 31.1 | 19.4 | **-12.4** [-19.3, -9.7] | [-22.2, -8.4] | +0.0 [+0.0, +0.0] | 0.233 (-0.078) | +0.110 | 3.15 (+1.21) | -16.6 [-23.9, -13.0] | +0.0 |
| 8 | Sample aggregation · max L-LATE (sequence all samples) · running mean [evaluation-matched] | 31.1 | 20.0 | **-11.8** [-19.5, -9.0] | [-22.5, -7.8] | +0.0 [+0.0, +0.0] | 0.252 (-0.059) | +0.084 | 7.61 (+5.67) | -16.0 [-24.3, -12.1] | +0.0 |
| 9 | A1+A2: EW memory of gate score + copy-number certificate · ew h=4y, t_quiet=p75, +1.0 logit, Y=2y [evaluation-matched] | 31.1 | 20.9 | **-10.9** [-18.6, -7.9] | [-20.4, -6.2] | +0.0 [+0.0, +0.4] | 0.211 (-0.100) | +0.141 | 1.94 (+0.00) | -15.1 [-22.9, -11.4] | +0.0 |
| 10 | A1+A2: EW memory of gate score + copy-number certificate · ew h=4y, t_quiet=p50, +0.5 logit, Y=4y [evaluation-matched] | 31.1 | 21.0 | **-10.8** [-18.8, -7.4] | [-20.8, -6.1] | +0.0 [+0.0, +0.4] | 0.226 (-0.086) | +0.121 | 1.94 (+0.00) | -15.0 [-23.1, -11.1] | +0.0 |
| 11 | A1+A2: EW memory of gate score + copy-number certificate · ew h=4y, t_quiet=p50, +1.0 logit, Y=4y [evaluation-matched] | 31.1 | 21.0 | **-10.8** [-18.9, -7.8] | [-20.9, -6.1] | +0.0 [+0.0, +0.4] | 0.214 (-0.097) | +0.137 | 1.94 (+0.00) | -15.0 [-23.3, -11.4] | +0.0 |
| 12 | A1+A2: EW memory of gate score + copy-number certificate · ew h=4y, t_quiet=p75, +0.5 logit, Y=4y [evaluation-matched] | 31.1 | 21.0 | **-10.8** [-18.3, -7.5] | [-20.4, -6.0] | +0.0 [+0.0, +0.5] | 0.218 (-0.094) | +0.133 | 1.94 (+0.00) | -15.0 [-22.8, -11.0] | +0.0 |
| 13 | A1+A2: EW memory of gate score + copy-number certificate · ew h=4y, t_quiet=p75, +0.5 logit, Y=2y [evaluation-matched] | 31.1 | 21.1 | **-10.7** [-18.5, -7.6] | [-20.6, -6.1] | +0.0 [+0.0, +0.4] | 0.227 (-0.085) | +0.120 | 1.94 (+0.00) | -14.9 [-22.9, -11.1] | +0.0 |
| 14 | A1+A2: EW memory of gate score + copy-number certificate · ew h=4y, t_quiet=p50, +1.0 logit, Y=2y [evaluation-matched] | 31.1 | 21.2 | **-10.6** [-18.1, -7.4] | [-20.5, -6.0] | +0.0 [+0.0, +0.4] | 0.225 (-0.086) | +0.121 | 1.94 (+0.00) | -14.8 [-22.6, -10.9] | +0.0 |
| 15 | A1+A2: EW memory of gate score + copy-number certificate · ew h=4y, t_quiet=p50, +0.5 logit, Y=2y [evaluation-matched] | 31.1 | 21.3 | **-10.5** [-18.3, -7.3] | [-20.4, -5.9] | +0.0 [+0.0, +0.4] | 0.234 (-0.077) | +0.110 | 1.94 (+0.00) | -14.7 [-22.7, -10.9] | +0.0 |
| 16 | A1+A2: EW memory of gate score + copy-number certificate · ew h=4y, t_quiet=p75, +1.0 logit, Y=4y [evaluation-matched] | 31.1 | 21.3 | **-10.5** [-18.1, -7.3] | [-20.0, -5.6] | +0.0 [+0.0, +0.5] | 0.198 (-0.113) | +0.160 | 1.94 (+0.00) | -14.7 [-22.4, -10.8] | +0.0 |
| 17 | A1+A2': EW memory of gate score + p53-normal certificate · ew h=2y, p53-normal certificate, +1.0 logit, Y=2y [evaluation-matched] | 31.1 | 21.3 | **-10.5** [-18.4, -8.0] | [-20.5, -6.5] | +0.0 [+0.0, +0.4] | 0.176 (-0.136) | +0.191 | 1.94 (+0.00) | -14.7 [-22.8, -11.4] | +0.0 |
| 18 | A1+A2': EW memory of gate score + p53-normal certificate · ew h=4y, p53-normal certificate, +0.5 logit, Y=2y [evaluation-matched] | 31.1 | 21.3 | **-10.5** [-18.6, -7.6] | [-20.8, -6.2] | +0.0 [+0.0, +0.4] | 0.212 (-0.099) | +0.140 | 1.94 (+0.00) | -14.7 [-23.0, -11.0] | +0.0 |
| 19 | A1+A2': EW memory of gate score + p53-normal certificate · ew h=4y, p53-normal certificate, +1.0 logit, Y=2y [evaluation-matched] | 31.1 | 21.3 | **-10.5** [-18.6, -7.6] | [-21.1, -6.3] | +0.0 [+0.0, +0.4] | 0.186 (-0.125) | +0.176 | 1.94 (+0.00) | -14.7 [-23.0, -11.1] | +0.0 |
| 20 | A1+A2: EW memory of gate score + copy-number certificate · ew h=2y, t_quiet=p75, +1.0 logit, Y=2y [evaluation-matched] | 31.1 | 21.4 | **-10.4** [-18.4, -7.9] | [-20.7, -6.5] | +0.0 [+0.0, +0.4] | 0.199 (-0.113) | +0.159 | 1.94 (+0.00) | -14.6 [-22.9, -11.1] | +0.0 |
| 21 | A1+A2: EW memory of gate score + copy-number certificate · ew h=2y, t_quiet=p50, +1.0 logit, Y=2y [evaluation-matched] | 31.1 | 21.5 | **-10.3** [-18.1, -7.6] | [-20.6, -6.3] | +0.0 [+0.0, +0.4] | 0.213 (-0.098) | +0.138 | 1.94 (+0.00) | -14.5 [-22.7, -10.9] | +0.0 |
| 22 | A1+A2: EW memory of gate score + copy-number certificate · ew h=2y, t_quiet=p75, +0.5 logit, Y=2y [evaluation-matched] | 31.1 | 21.5 | **-10.3** [-18.4, -7.9] | [-21.0, -6.4] | +0.0 [+0.0, +0.4] | 0.213 (-0.098) | +0.139 | 1.94 (+0.00) | -14.5 [-23.0, -11.1] | +0.0 |
| 23 | A1 · gate score, literal · exponentially weighted mean · ew h=4y [evaluation-matched] | 31.1 | 21.5 | **-10.3** [-18.1, -8.1] | [-21.2, -7.1] | +0.0 [+0.0, +0.0] | 0.227 (-0.084) | +0.119 | 1.94 (+0.00) | -14.5 [-22.7, -11.2] | +0.0 |
| 24 | A1+A2: EW memory of gate score + copy-number certificate · ew h=2y, t_quiet=p50, +0.5 logit, Y=2y [evaluation-matched] | 31.1 | 21.6 | **-10.2** [-18.2, -7.6] | [-20.6, -6.3] | +0.0 [+0.0, +0.4] | 0.221 (-0.091) | +0.128 | 1.94 (+0.00) | -14.4 [-22.7, -10.8] | +0.0 |
| 25 | A1+A2': EW memory of gate score + p53-normal certificate · ew h=2y, p53-normal certificate, +0.5 logit, Y=2y [evaluation-matched] | 31.1 | 21.6 | **-10.2** [-18.4, -7.6] | [-20.8, -6.2] | +0.0 [+0.0, +0.4] | 0.200 (-0.111) | +0.157 | 1.94 (+0.00) | -14.4 [-22.9, -11.0] | +0.0 |
| 26 | A1+A2: EW memory of gate score + copy-number certificate · ew h=2y, t_quiet=p75, +0.5 logit, Y=4y [evaluation-matched] | 31.1 | 21.7 | **-10.1** [-18.2, -7.3] | [-20.2, -5.7] | +0.0 [+0.0, +0.4] | 0.218 (-0.094) | +0.132 | 1.94 (+0.00) | -14.3 [-22.7, -10.7] | +0.0 |
| 27 | A1+A2: EW memory of gate score + copy-number certificate · ew h=2y, t_quiet=p50, +1.0 logit, Y=4y [evaluation-matched] | 31.1 | 21.9 | **-9.9** [-18.6, -7.3] | [-20.4, -5.7] | +0.0 [+0.0, +0.4] | 0.211 (-0.100) | +0.141 | 1.94 (+0.00) | -14.1 [-23.0, -10.6] | +0.0 |
| 28 | A1+A2': EW memory of gate score + p53-normal certificate · ew h=1y, p53-normal certificate, +1.0 logit, Y=2y [evaluation-matched] | 31.1 | 21.9 | **-9.9** [-18.2, -7.8] | [-20.1, -6.9] | +0.0 [+0.0, +0.2] | 0.167 (-0.145) | +0.204 | 1.94 (+0.00) | -14.1 [-22.7, -11.0] | +0.0 |
| 29 | A1+A2: EW memory of gate score + copy-number certificate · ew h=1y, t_quiet=p75, +1.0 logit, Y=2y [evaluation-matched] | 31.1 | 22.0 | **-9.8** [-18.3, -7.7] | [-20.2, -6.6] | +0.0 [+0.0, +0.2] | 0.188 (-0.124) | +0.175 | 1.94 (+0.00) | -14.0 [-22.7, -10.8] | +0.0 |
| 30 | A1+A2: EW memory of gate score + copy-number certificate · ew h=2y, t_quiet=p50, +0.5 logit, Y=4y [evaluation-matched] | 31.1 | 22.0 | **-9.8** [-18.3, -7.0] | [-20.6, -5.5] | +0.0 [+0.0, +0.4] | 0.228 (-0.084) | +0.118 | 1.94 (+0.00) | -14.0 [-22.9, -10.3] | +0.0 |

### B3. Abstention: indeterminate endoscopies

Nested row: mean per repeat 21.4 indeterminate endoscopies, of which 2.7 progressor endoscopies (counted as missed, 288 pre-event endoscopies in all). Selected share over the 100 folds: {'no abstention (= R49)': 20, 'indeterminate share 10%': 11, 'indeterminate share 20%': 69}.

### Choices made inside training (selection frequencies over the 100 outer folds)

| Family | Chosen candidate: folds | Infeasible folds (training detection target unreachable) | Mean training detection target / reached |
|---|---|---|---|
| A4 confirm-by-sequencing · gate with the high band also sequenced (score 0 = flag boundary) · exponentially weighted mean | ew h=1y: 48; ew h=2y: 24; ew h=4y: 28 | 0 | 28.33 / 28.33 |
| A1 · gate score, R49-aligned · exponentially weighted mean | ew h=1y: 41; ew h=2y: 17; ew h=4y: 42 | 0 | 28.33 / 28.33 |
| A4 confirm-by-sequencing · gate with the high band also sequenced (score 0 = flag boundary) · running mean | mean: 100 | 0 | 28.33 / 28.33 |
| A1 · gate score, literal · running mean | mean: 100 | 0 | 28.33 / 28.33 |
| Sample aggregation · max L-LATE (sequence all samples) · exponentially weighted mean | ew h=1y: 41; ew h=2y: 27; ew h=4y: 32 | 0 | 28.33 / 28.33 |
| A1 · gate score, literal · exponentially weighted mean | ew h=1y: 40; ew h=2y: 19; ew h=4y: 41 | 0 | 28.33 / 28.33 |
| Sample aggregation · max L-LATE (sequence all samples) · running mean | mean: 100 | 0 | 28.33 / 28.33 |
| A1 · gate score, R49-aligned · running mean | mean: 100 | 0 | 28.33 / 28.33 |
| Sample aggregation · H&E mean over samples · running mean | mean: 100 | 0 | 28.33 / 28.33 |
| A1 · gate score, literal · mean of last 2 | mean of last 2: 100 | 0 | 28.33 / 28.33 |
| A2 copy-number certificate (gate) | no certificate (= R49): 2; t_quiet=p50, raise to 85%-spec, Y=4y: 1; t_quiet=p50, raise to 95%-spec, Y=2y: 1; t_quiet=p50, raise to 95%-spec, Y=4y: 10; t_quiet=p75, raise to 85%-spec, Y=2y: 1; t_quiet=p75, raise to 85%-spec, Y=4y: 8; t_quiet=p75, raise to 95%-spec, Y=2y: 22; t_quiet=p75, raise to 95%-spec, Y=4y: 55 | 0 | 28.33 / 28.33 |
| A2' p53-normal certificate (gate) | no certificate (= R49): 1; raise to 85%-spec, Y=4y: 13; raise to 95%-spec, Y=2y: 50; raise to 95%-spec, Y=4y: 36 | 0 | 28.33 / 28.33 |
| A4 confirm-by-sequencing · gate with the high band also sequenced (score 0 = flag boundary) · threshold only | none: 100 | 0 | 28.33 / 28.33 |
| Sample aggregation · H&E mean over samples · exponentially weighted mean | ew h=1y: 25; ew h=2y: 24; ew h=4y: 51 | 0 | 28.33 / 28.33 |
| B4(a) refit, non-progressor weight 2, cut-offs re-tuned by the round-9 rule | cut-offs 90/85/70: 4; cut-offs 90/85/80: 1; cut-offs 90/85/90: 1; cut-offs 90/90/70: 17; cut-offs 90/90/80: 4; cut-offs 90/95/70: 29; cut-offs 90/95/80: 10; cut-offs 90/95/90: 2; cut-offs 95/85/70: 6; cut-offs 95/90/70: 3; cut-offs 95/90/80: 3; cut-offs 95/95/70: 7; cut-offs 95/95/80: 2; cut-offs 98/85/70: 1; cut-offs 98/90/70: 3; cut-offs 98/95/70: 4; cut-offs 98/95/80: 3 | 0 | 28.38 / 28.39 |
| B1-img control: stacked gate on L-IMG only (endoscopy-level cut-offs) | cut-offs 90/85/70: 3; cut-offs 90/85/80: 8; cut-offs 90/85/90: 3; cut-offs 90/90/70: 3; cut-offs 90/90/80: 4; cut-offs 90/90/90: 6; cut-offs 90/95/70: 11; cut-offs 90/95/80: 1; cut-offs 90/95/90: 5; cut-offs 95/85/70: 10; cut-offs 95/85/80: 2; cut-offs 95/90/70: 5; cut-offs 95/90/80: 2; cut-offs 95/90/90: 1; cut-offs 95/95/70: 6; cut-offs 95/95/80: 4; cut-offs 95/95/90: 3; cut-offs 98/85/70: 1; cut-offs 98/85/80: 4; cut-offs 98/85/90: 4; cut-offs 98/90/70: 1; cut-offs 98/90/80: 1; cut-offs 98/90/90: 2; cut-offs 98/95/70: 5; cut-offs 98/95/80: 2; cut-offs 98/95/90: 3 | 5 | 28.33 / 28.29 |
| A1 · gate score, literal · threshold only | none: 100 | 0 | 28.33 / 28.33 |
| Sample aggregation · max L-LATE (sequence all samples) · threshold only | none: 100 | 0 | 28.33 / 28.33 |
| Sample aggregation · H&E mean of top-2 samples · running mean | mean: 100 | 0 | 28.33 / 28.33 |
| A1 · gate score, R49-aligned · threshold only | none: 100 | 0 | 28.33 / 28.33 |
| control: R49 with cut-offs re-tuned by the round-9 rule | cut-offs 90/85/70: 4; cut-offs 90/85/80: 5; cut-offs 90/90/70: 11; cut-offs 90/90/80: 7; cut-offs 90/95/70: 31; cut-offs 90/95/80: 8; cut-offs 95/85/70: 2; cut-offs 95/90/70: 5; cut-offs 95/90/80: 4; cut-offs 95/95/70: 10; cut-offs 95/95/80: 4; cut-offs 98/85/70: 3; cut-offs 98/90/70: 2; cut-offs 98/95/70: 4 | 0 | 28.33 / 28.33 |
| B1+A1+A2: stacked gate + EW memory + copy-number certificate | B1 + ew h=1y, t_quiet=p50, +0.5 logit, Y=4y: 2; B1 + ew h=1y, t_quiet=p50, +1.0 logit, Y=2y: 2; B1 + ew h=1y, t_quiet=p50, +1.0 logit, Y=4y: 6; B1 + ew h=1y, t_quiet=p75, +0.5 logit, Y=2y: 1; B1 + ew h=1y, t_quiet=p75, +0.5 logit, Y=4y: 5; B1 + ew h=1y, t_quiet=p75, +1.0 logit, Y=2y: 14; B1 + ew h=1y, t_quiet=p75, +1.0 logit, Y=4y: 21; B1 + ew h=2y, t_quiet=p50, +1.0 logit, Y=2y: 3; B1 + ew h=2y, t_quiet=p50, +1.0 logit, Y=4y: 2; B1 + ew h=2y, t_quiet=p75, +0.5 logit, Y=4y: 2; B1 + ew h=2y, t_quiet=p75, +1.0 logit, Y=4y: 14; B1 + ew h=4y, t_quiet=p50, +1.0 logit, Y=2y: 1; B1 + ew h=4y, t_quiet=p50, +1.0 logit, Y=4y: 5; B1 + ew h=4y, t_quiet=p75, +0.5 logit, Y=4y: 1; B1 + ew h=4y, t_quiet=p75, +1.0 logit, Y=2y: 6; B1 + ew h=4y, t_quiet=p75, +1.0 logit, Y=4y: 15 | 0 | 28.33 / 28.33 |
| A3 agreement within endoscopy | no agreement rule (= R49): 4; gate: t_mid=50% sens, t_cnv=80% sens: 29; gate: t_mid=50% sens, t_cnv=90% sens: 5; gate: t_mid=80% sens, t_cnv=80% sens: 17; H&E alone: t_mid=50% sens, t_cnv=80% sens: 32; H&E alone: t_mid=50% sens, t_cnv=90% sens: 5; H&E alone: t_mid=80% sens, t_cnv=80% sens: 8 | 0 | 28.33 / 28.33 |
| A1 · gate score, R49-aligned · mean of last 2 | mean of last 2: 100 | 0 | 28.33 / 28.33 |
| A4 confirm the high band by sequencing (no outright slide-only flag) | t_low 90%, t_seq 70%: 48; t_low 90%, t_seq 80%: 14; t_low 90%, t_seq 90%: 1; t_low 95%, t_seq 70%: 18; t_low 95%, t_seq 80%: 14; t_low 98%, t_seq 70%: 5 | 0 | 28.33 / 28.33 |
| B3 abstention in middle band | no abstention (= R49): 20; indeterminate share 10%: 11; indeterminate share 20%: 69 | 0 | 28.33 / 28.33 |
| Sample aggregation · H&E mean of top-2 samples · exponentially weighted mean | ew h=1y: 24; ew h=2y: 30; ew h=4y: 46 | 0 | 28.33 / 28.33 |
| B4(b) refit, NDBE samples only, cut-offs re-tuned by the round-9 rule | cut-offs 90/85/70: 7; cut-offs 90/85/80: 4; cut-offs 90/90/70: 4; cut-offs 90/90/80: 10; cut-offs 90/95/70: 28; cut-offs 90/95/80: 7; cut-offs 95/85/70: 3; cut-offs 95/90/70: 9; cut-offs 95/90/80: 4; cut-offs 95/95/70: 11; cut-offs 95/95/80: 3; cut-offs 98/85/70: 2; cut-offs 98/90/70: 3; cut-offs 98/95/70: 4; cut-offs 98/95/80: 1 | 0 | 27.71 / 27.72 |
| A1 · H&E alone (max L-IMG) · running mean | mean: 100 | 0 | 28.33 / 28.33 |
| A1 · stacked B1 gate score, aligned · exponentially weighted mean | ew h=1y: 51; ew h=2y: 25; ew h=4y: 24 | 0 | 28.33 / 28.33 |
| B4(a) refit, non-progressor weight 2, R49 rules rebuilt | R49 gate rebuilt on this L-IMG (nominal cut-off rules): 100 | 0 | 28.38 / 28.38 |
| A1 · H&E alone (max L-IMG) · exponentially weighted mean | ew h=1y: 31; ew h=2y: 22; ew h=4y: 47 | 0 | 28.33 / 28.33 |
| B1 stacked gate (L-IMG, grade, age, sex; + L-CNV in middle band) | cut-offs 90/85/70: 4; cut-offs 90/85/80: 2; cut-offs 90/85/90: 3; cut-offs 90/90/70: 1; cut-offs 90/90/80: 3; cut-offs 90/90/90: 4; cut-offs 90/95/70: 4; cut-offs 90/95/80: 3; cut-offs 90/95/90: 6; cut-offs 95/85/70: 1; cut-offs 95/85/80: 3; cut-offs 95/85/90: 6; cut-offs 95/90/70: 1; cut-offs 95/90/80: 3; cut-offs 95/90/90: 3; cut-offs 95/95/70: 5; cut-offs 95/95/80: 5; cut-offs 95/95/90: 4; cut-offs 98/85/70: 2; cut-offs 98/85/80: 4; cut-offs 98/85/90: 4; cut-offs 98/90/70: 3; cut-offs 98/90/80: 3; cut-offs 98/90/90: 3; cut-offs 98/95/70: 10; cut-offs 98/95/80: 4; cut-offs 98/95/90: 6 | 13 | 28.33 / 28.19 |
| A1 · stacked B1 gate score, aligned · running mean | mean: 100 | 0 | 28.33 / 28.33 |
| Sample aggregation · H&E mean over samples · threshold only | none: 100 | 0 | 28.33 / 28.33 |
| B1 + p53 (aberrant, missing) | cut-offs 90/85/80: 6; cut-offs 90/85/90: 5; cut-offs 90/90/70: 3; cut-offs 90/90/80: 1; cut-offs 90/90/90: 2; cut-offs 90/95/70: 3; cut-offs 90/95/80: 2; cut-offs 90/95/90: 2; cut-offs 95/85/70: 2; cut-offs 95/85/80: 6; cut-offs 95/85/90: 7; cut-offs 95/90/70: 1; cut-offs 95/90/80: 3; cut-offs 95/90/90: 3; cut-offs 95/95/70: 4; cut-offs 95/95/80: 7; cut-offs 95/95/90: 6; cut-offs 98/85/70: 3; cut-offs 98/85/80: 1; cut-offs 98/85/90: 6; cut-offs 98/90/70: 3; cut-offs 98/90/80: 4; cut-offs 98/90/90: 5; cut-offs 98/95/70: 2; cut-offs 98/95/80: 8; cut-offs 98/95/90: 5 | 14 | 28.33 / 28.19 |
| A1 · stacked B1 gate score, aligned · mean of last 2 | mean of last 2: 100 | 0 | 28.33 / 28.33 |
| A1 · H&E alone (max L-IMG) · mean of last 2 | mean of last 2: 100 | 0 | 28.33 / 28.33 |
| A1 · stacked B1 gate score, aligned · threshold only | none: 100 | 0 | 28.33 / 28.33 |
| B4(b) refit, NDBE samples only, R49 rules rebuilt | R49 gate rebuilt on this L-IMG (nominal cut-off rules): 100 | 0 | 27.71 / 27.71 |
| Sample aggregation · H&E mean of top-2 samples · threshold only | none: 100 | 0 | 28.33 / 28.33 |
| A1 · H&E alone (max L-IMG) · threshold only | none: 100 | 0 | 28.33 / 28.33 |
| A1 · gate score, R49-aligned · change from own mean | change from own mean, lambda=0.5: 75; change from own mean, lambda=1.0: 25 | 0 | 28.33 / 28.33 |
| A1 · H&E alone (max L-IMG) · change from own mean | change from own mean, lambda=0.5: 69; change from own mean, lambda=1.0: 31 | 0 | 28.33 / 28.33 |
| A1+A2: EW memory of gate score + copy-number certificate | ew h=1y, t_quiet=p50, +0.5 logit, Y=4y: 1; ew h=1y, t_quiet=p50, +1.0 logit, Y=4y: 1; ew h=1y, t_quiet=p75, +0.5 logit, Y=2y: 3; ew h=1y, t_quiet=p75, +0.5 logit, Y=4y: 3; ew h=1y, t_quiet=p75, +1.0 logit, Y=2y: 14; ew h=1y, t_quiet=p75, +1.0 logit, Y=4y: 24; ew h=2y, t_quiet=p50, +0.5 logit, Y=4y: 1; ew h=2y, t_quiet=p50, +1.0 logit, Y=2y: 1; ew h=2y, t_quiet=p50, +1.0 logit, Y=4y: 1; ew h=2y, t_quiet=p75, +0.5 logit, Y=4y: 2; ew h=2y, t_quiet=p75, +1.0 logit, Y=2y: 6; ew h=2y, t_quiet=p75, +1.0 logit, Y=4y: 8; ew h=4y, t_quiet=p50, +1.0 logit, Y=4y: 6; ew h=4y, t_quiet=p75, +0.5 logit, Y=4y: 3; ew h=4y, t_quiet=p75, +1.0 logit, Y=2y: 11; ew h=4y, t_quiet=p75, +1.0 logit, Y=4y: 15 | 0 | 28.33 / 28.33 |
| A1+A2': EW memory of gate score + p53-normal certificate | ew h=1y, p53-normal certificate, +0.5 logit, Y=2y: 2; ew h=1y, p53-normal certificate, +0.5 logit, Y=4y: 3; ew h=1y, p53-normal certificate, +1.0 logit, Y=2y: 37; ew h=1y, p53-normal certificate, +1.0 logit, Y=4y: 5; ew h=2y, p53-normal certificate, +0.5 logit, Y=2y: 1; ew h=2y, p53-normal certificate, +0.5 logit, Y=4y: 1; ew h=2y, p53-normal certificate, +1.0 logit, Y=2y: 10; ew h=2y, p53-normal certificate, +1.0 logit, Y=4y: 7; ew h=4y, p53-normal certificate, +0.5 logit, Y=4y: 3; ew h=4y, p53-normal certificate, +1.0 logit, Y=2y: 20; ew h=4y, p53-normal certificate, +1.0 logit, Y=4y: 11 | 0 | 28.33 / 28.33 |
| A1 · gate score, R49-aligned · exponentially weighted, longer half-lives (0.5, 8, 16 y) | ew h=0.5y: 43; ew h=8y: 38; ew h=16y: 19 | 0 | 28.33 / 28.33 |
| A1 · gate score, R49-aligned · consecutive-2 or t_high | consecutive-2 or t_high=q90: 61; consecutive-2 or t_high=q95: 29; consecutive-2 or t_high=q975: 10 | 77 | 28.33 / 26.97 |
| A1 · gate score, literal · consecutive-2 or t_high | consecutive-2 or t_high=q90: 44; consecutive-2 or t_high=q95: 27; consecutive-2 or t_high=q975: 29 | 98 | 28.33 / 26.28 |
| A1 · gate score, literal · 2-of-last-3 or t_high | 2-of-last-3 or t_high=q90: 46; 2-of-last-3 or t_high=q95: 27; 2-of-last-3 or t_high=q975: 27 | 98 | 28.33 / 26.28 |
| A1 · gate score, R49-aligned · 2-of-last-3 or t_high | 2-of-last-3 or t_high=q90: 60; 2-of-last-3 or t_high=q95: 30; 2-of-last-3 or t_high=q975: 10 | 77 | 28.33 / 26.97 |
| A1 · gate score, literal · 2-of-n anywhere or t_high | 2-of-n anywhere or t_high=q90: 46; 2-of-n anywhere or t_high=q95: 26; 2-of-n anywhere or t_high=q975: 28 | 98 | 28.33 / 26.28 |
| A1 · gate score, R49-aligned · 2-of-n anywhere or t_high | 2-of-n anywhere or t_high=q90: 60; 2-of-n anywhere or t_high=q95: 30; 2-of-n anywhere or t_high=q975: 10 | 77 | 28.33 / 26.97 |
| A1 · gate score, literal · consecutive-2 | consecutive-2: 100 | 100 | 28.33 / 19.8 |
| A1 · gate score, R49-aligned · consecutive-2 | consecutive-2: 100 | 100 | 28.33 / 19.8 |
| A1 · H&E alone (max L-IMG) · consecutive-2 or t_high | consecutive-2 or t_high=q90: 36; consecutive-2 or t_high=q95: 30; consecutive-2 or t_high=q975: 34 | 98 | 28.33 / 26.21 |
| A1 · stacked B1 gate score, aligned · consecutive-2 or t_high | consecutive-2 or t_high=q90: 40; consecutive-2 or t_high=q95: 45; consecutive-2 or t_high=q975: 15 | 96 | 28.33 / 25.89 |
| A1 · gate score, literal · change from own mean | change from own mean, lambda=0.5: 89; change from own mean, lambda=1.0: 11 | 0 | 28.33 / 28.33 |
| A1 · gate score, literal · 2-of-n anywhere | 2-of-n anywhere: 100 | 100 | 28.33 / 19.8 |
| A1 · gate score, literal · 2-of-last-3 | 2-of-last-3: 100 | 100 | 28.33 / 19.8 |
| A1 · stacked B1 gate score, aligned · 2-of-last-3 or t_high | 2-of-last-3 or t_high=q90: 39; 2-of-last-3 or t_high=q95: 47; 2-of-last-3 or t_high=q975: 14 | 96 | 28.33 / 25.89 |
| A1 · H&E alone (max L-IMG) · consecutive-2 | consecutive-2: 100 | 100 | 28.33 / 19.8 |
| A1 · gate score, R49-aligned · 2-of-n anywhere | 2-of-n anywhere: 100 | 100 | 28.33 / 19.8 |
| A1 · gate score, R49-aligned · 2-of-last-3 | 2-of-last-3: 100 | 100 | 28.33 / 19.8 |
| A1 · stacked B1 gate score, aligned · 2-of-n anywhere or t_high | 2-of-n anywhere or t_high=q90: 39; 2-of-n anywhere or t_high=q95: 48; 2-of-n anywhere or t_high=q975: 13 | 96 | 28.33 / 25.89 |
| A1 · H&E alone (max L-IMG) · 2-of-last-3 or t_high | 2-of-last-3 or t_high=q90: 38; 2-of-last-3 or t_high=q95: 33; 2-of-last-3 or t_high=q975: 29 | 98 | 28.33 / 26.21 |
| A1 · stacked B1 gate score, aligned · consecutive-2 | consecutive-2: 100 | 100 | 28.33 / 19.8 |
| A1 · H&E alone (max L-IMG) · 2-of-n anywhere or t_high | 2-of-n anywhere or t_high=q90: 37; 2-of-n anywhere or t_high=q95: 33; 2-of-n anywhere or t_high=q975: 30 | 98 | 28.33 / 26.21 |
| A1 · stacked B1 gate score, aligned · 2-of-last-3 | 2-of-last-3: 100 | 100 | 28.33 / 19.8 |
| A1 · stacked B1 gate score, aligned · 2-of-n anywhere | 2-of-n anywhere: 100 | 100 | 28.33 / 19.8 |
| A1 · H&E alone (max L-IMG) · 2-of-last-3 | 2-of-last-3: 100 | 100 | 28.33 / 19.8 |
| A1 · H&E alone (max L-IMG) · 2-of-n anywhere | 2-of-n anywhere: 100 | 100 | 28.33 / 19.8 |
| A1 · stacked B1 gate score, aligned · change from own mean | change from own mean, lambda=0.5: 80; change from own mean, lambda=1.0: 20 | 0 | 28.33 / 28.33 |

### Cumulative false-flag curves by endoscopy index

Best memory rule in the ranking: **A1 · gate score, R49-aligned · exponentially weighted mean**. share of patients flagged at >= 1 of their first k pre-event endoscopies (patients with fewer than k endoscopies contribute all of theirs; 'restricted' keeps only patients with >= k endoscopies, the matched first-k window); held-out predictions, 10-repeat mean; patient bootstrap CIs; groups < 5 patients '<5'.

| k | Rule | NP flagged: all patients [95% CI] | NP flagged: patients with ≥ k endoscopies (n) | Progressors caught: all | Progressors caught: ≥ k (n) | Δ NP vs R49 [95% CI] (all) |
|---|---|---|---|---|---|---|
| 1 | R49 | 0.388 [0.27, 0.51] | 0.388 (n = 43) | 0.872 | 0.872 (n = 32) |  |
| 1 | P1 90% | 0.447 [0.32, 0.57] | 0.447 (n = 43) | 0.853 | 0.853 (n = 32) | +0.058 [-0.008, +0.124] |
| 1 | A1 · gate score, R49-aligned · exponentially weighted mean | 0.363 [0.26, 0.47] | 0.363 (n = 43) | 0.869 | 0.869 (n = 32) | -0.026 [-0.053, +0.002] |
| 2 | R49 | 0.644 [0.52, 0.76] | 0.644 (n = 43) | 0.972 | 0.986 (n = 22) |  |
| 2 | P1 90% | 0.73 [0.60, 0.84] | 0.73 (n = 43) | 0.969 | 0.995 (n = 22) | +0.086 [+0.009, +0.164] |
| 2 | A1 · gate score, R49-aligned · exponentially weighted mean | 0.458 [0.34, 0.58] | 0.458 (n = 43) | 0.947 | 0.95 (n = 22) | -0.186 [-0.263, -0.115] |
| 3 | R49 | 0.684 [0.56, 0.80] | 0.695 (n = 40) | 0.972 | 0.988 (n = 16) |  |
| 3 | P1 90% | 0.779 [0.66, 0.89] | 0.762 (n = 40) | 0.972 | 1.0 (n = 16) | +0.095 [+0.026, +0.170] |
| 3 | A1 · gate score, R49-aligned · exponentially weighted mean | 0.498 [0.38, 0.62] | 0.508 (n = 40) | 0.959 | 0.988 (n = 16) | -0.186 [-0.260, -0.118] |
| 4 | R49 | 0.728 [0.61, 0.83] | 0.819 (n = 32) | 0.972 | 1.0 (n = 9) |  |
| 4 | P1 90% | 0.833 [0.72, 0.92] | 0.916 (n = 32) | 0.972 | 1.0 (n = 9) | +0.105 [+0.031, +0.179] |
| 4 | A1 · gate score, R49-aligned · exponentially weighted mean | 0.523 [0.41, 0.65] | 0.591 (n = 32) | 0.959 | 1.0 (n = 9) | -0.205 [-0.281, -0.131] |
| 5 | R49 | 0.735 [0.62, 0.84] | 0.822 (n = 23) | 0.972 | <5 (n = <5) |  |
| 5 | P1 90% | 0.833 [0.72, 0.92] | 0.904 (n = 23) | 0.972 | <5 (n = <5) | +0.098 [+0.025, +0.172] |
| 5 | A1 · gate score, R49-aligned · exponentially weighted mean | 0.535 [0.41, 0.66] | 0.604 (n = 23) | 0.959 | <5 (n = <5) | -0.200 [-0.274, -0.126] |
| 6 | R49 | 0.74 [0.63, 0.84] | 0.846 (n = 13) | 0.972 | <5 (n = <5) |  |
| 6 | P1 90% | 0.837 [0.73, 0.92] | 0.938 (n = 13) | 0.972 | <5 (n = <5) | +0.098 [+0.028, +0.171] |
| 6 | A1 · gate score, R49-aligned · exponentially weighted mean | 0.547 [0.42, 0.68] | 0.677 (n = 13) | 0.959 | <5 (n = <5) | -0.193 [-0.267, -0.122] |

### Robustness of the top 3 methods

Rows as the R49 robustness rows (`docs/paper_review_round7c_gate_robustness.md`) that can be re-scored: the same nested procedure is repeated inside the row's population (NDBE-only, ≥ 2 samples, R52(a) refit set: every training-side choice is redone; tissue strata: held-out calls of the main run, evaluation restricted). Between-repeat variance and the refit bootstrap are below.

| Row | Population (endoscopies; progressor / non-progressor patients) | Rule | Caught | NP flagged | Δ NP flagged vs R49 [95% CI] | Δ caught vs R49 [95% CI] | Δ NP flagged vs P1 90% [95% CI] |
|---|---|---|---|---|---|---|---|
| ndbe | 240; 28 / 43 | R49 | 27.1 | 31.3 | | | |
| ndbe | 240; 28 / 43 | P1 90% | 27.4 | 34.7 | | | |
| ndbe | 240; 28 / 43 | A4 confirm-by-sequencing · gate with the high band also sequenced (score 0 = flag boundary) · exponentially weighted mean | 26.7 | 23.0 | -8.3 [-11.3, -5.4] | -0.4 [-0.9, +0.0] | -11.7 [-15.8, -7.7] |
| ndbe | 240; 28 / 43 | A1 · gate score, R49-aligned · exponentially weighted mean | 27.1 | 22.9 | -8.4 [-11.5, -5.4] | +0.0 [-0.7, +0.6] | -11.8 [-15.9, -7.6] |
| ndbe | 240; 28 / 43 | A4 confirm-by-sequencing · gate with the high band also sequenced (score 0 = flag boundary) · running mean | 27.1 | 22.7 | -8.6 [-12.2, -5.3] | -0.0 [-0.6, +0.6] | -12.0 [-16.2, -7.6] |
| ge2 | 146; 25 / 39 | R49 | 24.3 | 27.2 | | | |
| ge2 | 146; 25 / 39 | P1 90% | 23.4 | 27.7 | | | |
| ge2 | 146; 25 / 39 | A4 confirm-by-sequencing · gate with the high band also sequenced (score 0 = flag boundary) · exponentially weighted mean | 23.9 | 20.0 | -7.2 [-9.5, -5.1] | -0.4 [-1.0, +0.0] | -7.7 [-11.4, -4.1] |
| ge2 | 146; 25 / 39 | A1 · gate score, R49-aligned · exponentially weighted mean | 23.4 | 22.3 | -4.9 [-6.8, -3.2] | -0.9 [-1.7, -0.2] | -5.4 [-8.9, -2.2] |
| ge2 | 146; 25 / 39 | A4 confirm-by-sequencing · gate with the high band also sequenced (score 0 = flag boundary) · running mean | 23.5 | 20.9 | -6.3 [-8.6, -4.3] | -0.8 [-1.9, -0.1] | -6.8 [-10.4, -3.4] |
| tis_lt256 | 142; 32 / 43 | R49 | 29.6 | 26.8 | | | |
| tis_lt256 | 142; 32 / 43 | P1 90% | 29.6 | 29.9 | | | |
| tis_lt256 | 142; 32 / 43 | A4 confirm-by-sequencing · gate with the high band also sequenced (score 0 = flag boundary) · exponentially weighted mean | 28.5 | 20.5 | -6.3 [-9.7, -3.4] | -1.0 [-2.2, -0.1] | -9.4 [-13.6, -5.5] |
| tis_lt256 | 142; 32 / 43 | A1 · gate score, R49-aligned · exponentially weighted mean | 29.3 | 20.7 | -6.1 [-9.2, -3.3] | -0.3 [-1.1, +0.6] | -9.2 [-13.1, -5.6] |
| tis_lt256 | 142; 32 / 43 | A4 confirm-by-sequencing · gate with the high band also sequenced (score 0 = flag boundary) · running mean | 30.7 | 22.5 | -4.3 [-7.8, -1.1] | +1.2 [-0.1, +3.0] | -7.4 [-11.3, -3.7] |
| tis_ge256 | 146; 32 / 43 | R49 | 31.0 | 28.4 | | | |
| tis_ge256 | 146; 32 / 43 | P1 90% | 30.2 | 32.2 | | | |
| tis_ge256 | 146; 32 / 43 | A4 confirm-by-sequencing · gate with the high band also sequenced (score 0 = flag boundary) · exponentially weighted mean | 30.7 | 20.4 | -8.0 [-11.0, -5.3] | -0.3 [-0.8, +0.0] | -11.9 [-16.3, -7.4] |
| tis_ge256 | 146; 32 / 43 | A1 · gate score, R49-aligned · exponentially weighted mean | 30.3 | 20.4 | -8.0 [-11.3, -5.1] | -0.6 [-2.2, +0.7] | -11.9 [-16.4, -7.4] |
| tis_ge256 | 146; 32 / 43 | A4 confirm-by-sequencing · gate with the high band also sequenced (score 0 = flag boundary) · running mean | 31.5 | 22.5 | -5.9 [-9.3, -2.8] | +0.5 [-0.6, +2.4] | -9.7 [-14.2, -5.5] |
| tis_lt256pure | 98; 32 / 43 | R49 | 30.1 | 24.4 | | | |
| tis_lt256pure | 98; 32 / 43 | P1 90% | 29.0 | 23.2 | | | |
| tis_lt256pure | 98; 32 / 43 | A4 confirm-by-sequencing · gate with the high band also sequenced (score 0 = flag boundary) · exponentially weighted mean | 28.5 | 19.0 | -5.4 [-9.5, -1.6] | -1.6 [-3.0, -0.4] | -4.2 [-9.5, +1.5] |
| tis_lt256pure | 98; 32 / 43 | A1 · gate score, R49-aligned · exponentially weighted mean | 29.6 | 18.6 | -5.9 [-9.6, -2.4] | -0.5 [-1.1, +0.0] | -4.6 [-9.5, +0.3] |
| tis_lt256pure | 98; 32 / 43 | A4 confirm-by-sequencing · gate with the high band also sequenced (score 0 = flag boundary) · running mean | 31.0 | 22.1 | -2.4 [-6.7, +1.9] | +1.0 [-0.3, +2.9] | -1.1 [-6.8, +5.2] |
| tis_ge256pure | 117; 32 / 43 | R49 | 30.8 | 26.2 | | | |
| tis_ge256pure | 117; 32 / 43 | P1 90% | 29.6 | 30.4 | | | |
| tis_ge256pure | 117; 32 / 43 | A4 confirm-by-sequencing · gate with the high band also sequenced (score 0 = flag boundary) · exponentially weighted mean | 30.3 | 19.3 | -6.9 [-9.9, -4.3] | -0.5 [-1.2, +0.0] | -11.1 [-16.2, -6.1] |
| tis_ge256pure | 117; 32 / 43 | A1 · gate score, R49-aligned · exponentially weighted mean | 29.9 | 19.3 | -6.9 [-9.7, -4.4] | -0.9 [-2.7, +0.8] | -11.1 [-16.0, -6.6] |
| tis_ge256pure | 117; 32 / 43 | A4 confirm-by-sequencing · gate with the high band also sequenced (score 0 = flag boundary) · running mean | 31.4 | 21.6 | -4.6 [-7.8, -1.8] | +0.6 [-0.6, +2.8] | -8.7 [-13.8, -4.0] |
| r52a | 290; 34 / 43 | R49 | 33.1 | 31.2 | | | |
| r52a | 290; 34 / 43 | P1 90% | 33.0 | 36.6 | | | |
| r52a | 290; 34 / 43 | A4 confirm-by-sequencing · gate with the high band also sequenced (score 0 = flag boundary) · exponentially weighted mean | 32.9 | 21.4 | -9.8 [-13.4, -6.4] | -0.2 [-0.7, +0.0] | -15.2 [-19.7, -10.5] |
| r52a | 290; 34 / 43 | A1 · gate score, R49-aligned · exponentially weighted mean | 32.8 | 22.0 | -9.2 [-12.7, -5.9] | -0.3 [-0.7, +0.0] | -14.6 [-18.8, -10.0] |
| r52a | 290; 34 / 43 | A4 confirm-by-sequencing · gate with the high band also sequenced (score 0 = flag boundary) · running mean | 33.3 | 22.9 | -8.3 [-11.9, -4.9] | +0.2 [-0.3, +1.0] | -13.7 [-18.0, -9.1] |

Row definitions: **ndbe**: pre-event NDBE samples only (cut-offs and comparators re-chosen on NDBE training samples; round-7c row); **ge2**: endoscopies with >= 2 pre-event samples (cut-offs re-chosen on them; round-7c row); **tis_lt256**: < 256 tissue tiles (endoscopy by its top-L-IMG sample); **tis_ge256**: >= 256 tissue tiles (endoscopy by its top-L-IMG sample); **tis_lt256pure**: < 256 tissue tiles (all samples of the endoscopy in the stratum); **tis_ge256pure**: >= 256 tissue tiles (all samples of the endoscopy in the stratum); **r52a**: R52(a): + 17 same-block samples, refit (round-7 refit predictions, all cut-offs and rules re-derived).

Between-repeat variance of the main-run result (Δ against R49 per repeat, 10 repeats):

| Method | Δ NP flagged: mean (SD; min, max) | Δ caught: mean (SD; min, max) |
|---|---|---|
| A4 confirm-by-sequencing · gate with the high band also sequenced (score 0 = flag boundary) · exponentially weighted mean | -8.70 (1.83; -12.0, -5.0) | -0.30 (0.68; -1.0, +1.0) |
| A1 · gate score, R49-aligned · exponentially weighted mean | -8.20 (2.15; -12.0, -5.0) | -0.40 (0.52; -1.0, +0.0) |
| A4 confirm-by-sequencing · gate with the high band also sequenced (score 0 = flag boundary) · running mean | -7.80 (2.53; -11.0, -3.0) | +0.30 (0.95; -1.0, +2.0) |

Refit bootstrap (F3, 200 draws): not re-scored; see Implementation notes.

### Figures (local, not committed)

`paper/figures_r9/`: `r9_forest.png` (ranked Δ NP patients flagged against R49, Δ caught annotated), `r9_scatter.png` (caught against NP flagged for every method with R49, P1 90%, P3 90% and grade marked), `r9_f0.png` (F0), `r9_icc.png` (ICC), `r9_curves.png` (cumulative false-flag curves).

### What the round shows (exploratory; every statement post hoc)

- **Memory over the gate score is the main lever.** EW memory of the R49-aligned gate score (hyper-parameter chosen in training): 23.6 NP flagged (-8.2 [-11.4, -5.1]), 30.7 caught (-0.4), 1.94 samples per patient; running mean of the literal gate score: 24.6 NP flagged (-7.2 [-10.2, -4.3]), 31.1 caught (+0.0), 1.94 samples per patient. The same pattern appears with L-LATE over all samples and, without copy number, with sample-mean H&E (smaller). Against R49: 31.8 NP flagged, 31.1 caught, 1.94 samples per patient.
- **How much is just re-tuning.** R49 with cut-offs re-tuned by the round-9 rule: 29.4 NP flagged (-2.4 [-3.6, -1.3]), 30.6 caught (-0.5), 1.87 samples per patient; the gate score with a single re-tuned threshold: 29.4 NP flagged (-2.4 [-3.7, -1.3]), 30.7 caught (-0.4), 1.94 samples per patient. Memory adds about 5.8 fewer flagged non-progressors beyond that.
- **A4 (confirm every above-low endoscopy by sequencing)** with memory is nominally first: A4 + EW: 23.1 NP flagged (-8.7 [-12.1, -5.6]), 30.8 caught (-0.3), 3.15 samples per patient, at the price of about one more sample per patient; without memory A4 alone: 30.5 NP flagged (-1.3 [-2.1, -0.6]), 30.9 caught (-0.2), 2.96 samples per patient.
- **Pure k-of-n persistence loses progressors:** a progressor with one pre-event endoscopy (10 of 32) cannot be flagged by 2-of-n or consecutive-2; they catch about 21 of 32. With a t_high override the loss is 1.7 progressors (consecutive-2 or t_high on the aligned gate score) for -2.4 non-progressors flagged, far less than EW memory gives at a fraction of that loss.
- **Other levers are small:** A2 copy-number certificate: 28.1 NP flagged (-3.7 [-5.6, -2.1]), 31.0 caught (-0.1), 1.36 samples per patient; A2' p53 certificate: 28.2 NP flagged (-3.6 [-5.3, -2.1]), 30.9 caught (-0.2), 1.17 samples per patient; A3: 29.8 NP flagged (-2.0 [-3.5, -0.6]), 30.6 caught (-0.5), 1.51 samples per patient; B3 abstention: 30.8 NP flagged (-1.0 [-1.7, -0.4]), 31.1 caught (+0.0), 1.94 samples per patient; B1 stacked gate: 32.2 NP flagged (+0.4 [-0.6, +1.4]), 30.9 caught (-0.2), 2.33 samples per patient (no gain from grade, age and sex); B4 refits: weight 2, re-tuned: 28.6 NP flagged (-3.2 [-4.6, -1.8]), 30.8 caught (-0.3), 1.92 samples per patient and NDBE only, re-tuned: 31.1 NP flagged (-0.7 [-3.6, +2.4]), 30.7 caught (-0.4), 2.33 samples per patient; with R49's own cut-off rules rebuilt they change +0.3 and +3.1. 'Change from own mean' recalibration is worse than no memory.
- **Combining** the EW memory with a copy-number or p53 certificate lowers flags further (A1+A2: 21.5 NP flagged (-10.3 [-13.9, -6.9]), 30.5 caught (-0.6), 1.94 samples per patient) but costs a little progressor detection (the point estimate falls just below the −0.5 line).
- **Why memory works here:** non-progressors' scores are only weakly correlated within a patient (ICC about 0.2 to 0.3) while progressors' are strongly correlated (about 0.6); averaging shrinks the non-progressors' noise and leaves progressors' consistent signal. Almost all of the reduction appears from the second endoscopy on (first-endoscopy false-flag share unchanged).
- **F0:** flagged non-progressors were not more likely than unflagged ones to show a later IND, LGD or HGD record (counts 5 or 6 of 31 or 36 flagged against fewer than 5 unflagged; all Fisher p ≥ 0.4), but only 7 non-progressors have any later IND or worse, so the comparison cannot detect a moderate difference.
- **Caveats.** About 70 families and several hundred grid points were tried on 75 patients; the top rows are the winners of that search and their intervals do not account for it (the 99.2% intervals cover 6 families only). The nested design protects against tuning on the evaluation patients, not against the choice of which families to report. Results are post hoc on a cohort with repeat endoscopies; ACE-B (mostly one endoscopy per patient) cannot test them. A method worth registering must be fixed (family, half-life rule, cut-offs) before any external look.

### Implementation notes

**Conventions reused.** Setup, endoscopy units (571 pre-event samples, 288 endoscopies, 75 patients, 32 progressors), exact endoscopy dates, patient outcomes (`patient_arrays`), bootstrap draws (`pdraws`, `RandomState(0)`, 2,000, one-class draws rejected), weighted-sum metrics (`parts`, `per_rep`, `met`) and `dstat` are executed unchanged from `rv8_landscape.py` / `rv8b_step3.py`; R49 is `r49_calls`, P1 90% is `thr_arr(img, 0.90)`. Counts are shares × 32 or × 43 in every draw. Check run first in a smoke run (50 draws) and repeated in the full run: R49 31.1 / 31.8, P1 90% 31.1 / 36.0; the engine's per-fold R49 equals `r49_calls` on every held-out endoscopy and its sample-level cut-off re-derivation equals `tb_common.triage` in all 100 folds.

**Nested evaluation (the non-negotiable).** For each outer (repeat, fold) every method is built from the training patients only: training endoscopies carry the stored inner out-of-fold predictions of that fold, held-out endoscopies the stored outer predictions. A patient's memory score uses only that patient's own endoscopies up to the current one (time order by exact date), so no held-out label or other held-out patient enters. The operating threshold is the D-th largest training progressor-patient maximum score, D = the number of training progressor patients the R49 gate itself detects in that fold (28.33 of 28.33 on average; mean reached by the method is in the selection-frequency table); gate-structured methods choose among their candidate cut-off cells the one with the lowest training non-progressor patients flagged subject to detection ≥ D (ties: fewer flagged endoscopies, fewer samples sequenced, grid order). If no candidate reaches D (the pure k-of-n rules, 77 to 100 folds) the candidate with the highest training detection is taken and the fold is counted as infeasible; that is where their progressor losses come from. Hyper-parameters within a family are chosen by the same rule (rows 'nested'); '(pAUC selection)' picks the score-type candidate with the highest patient-level partial AUC (FPR ≤ 0.2, normalised) of the training patients' maximum scores and then applies the same threshold rule. Logistic stackers (B1 family) are 5-fold patient-grouped cross-validated inside the training patients: cut-offs and thresholds use the out-of-fold stacked scores, held-out endoscopies the all-training fit.

**Apparent results (optimistic).** 'Grid point' rows fix one hyper-parameter value for all folds (threshold still training-chosen) and are picked after seeing the evaluation; 'evaluation-matched' rows set the threshold on the evaluation patients, per repeat, so that progressor patients caught equals R49's (re-matched in every bootstrap draw; candidates are the progressor patients' own maximum scores). Both are labelled optimistic in the tables; evaluation-matched is available for score-type methods (a continuous dial) only.

**Interpretation choices where the plan was open.**
- A1(a) running mean, A1(b) exponentially weighted (half-life 1, 2, 4 years, weights 0.5^(Δt/h), Δt from exact dates), A1(c) persistence = 'consecutive-2 or score ≥ t_high' (first endoscopy: t_high only; t_high at the 90, 95 or 97.5th percentile of training non-progressor endoscopy scores, t from the detection rule). Scores are logits of the endoscopy-maximum L-IMG; the gate score is the literal reading of the plan (L-IMG logit, replaced in the middle band by the sequenced top sample's L-LATE logit) and, as an addition, a R49-aligned version in which the middle-band logit is shifted so that the gate's own decision (L-LATE ≥ t_seq) is 'score ≥ logit c*' (R49 is then exactly 'score ≥ logit c*', verified on every held-out endoscopy). Sequencing for the gate-score memory rules is R49's (1.94 samples per patient).
- A2: certificate issued after a sequenced (middle-band) endoscopy whose top sample's L-CNV logit is below t_quiet (training non-progressor sequenced endoscopies, 50th or 75th percentile); for Y = 2 or 4 years afterwards both gate cut-offs are raised to at least the training H&E threshold at 85% or 95% non-progressor specificity (so the low band widens, and at 95% the certified patient is judged by H&E alone). 'No certificate' (= R49) is a candidate.
- A3: second-highest sample's L-IMG against t_mid (80% or 50% sensitivity among training progressor endoscopies with ≥ 2 samples); otherwise the top sample is sequenced and the flag stands only if its L-CNV ≥ the copy-number threshold (80% or 90% sensitivity among training progressor endoscopies, top sample). Both the gate and an H&E-alone version (threshold by the detection rule) are candidates; single-sample endoscopies follow the base rule.
- B1: logistic regression (L2, C = 1, standardised inputs) on endoscopy-maximum L-IMG logit, ID/LGD indicator, age and sex (age at the endoscopy from the stored age at sample), fitted on endoscopy labels; middle band: second regression that adds the top sample's L-CNV logit; endoscopy-level cut-offs (t_low at 90, 95 or 98% training progressor-endoscopy sensitivity, c* at 85, 90 or 95% training non-progressor-endoscopy specificity, t_seq at 70, 80 or 90% sensitivity) form the 27-cell candidate grid. B2 = EW memory over the B1 gate score aligned as above.
- B3: indeterminate when the sequenced call's L-LATE logit is within ±ε of logit t_seq; ε = the 10% or 20% quantile of training middle-band |distance|; indeterminate endoscopies are not flagged (progressor ones count as missed).
- B4: `rv9_refit.R` refits the H&E elastic net with the stored folds and λ rule (outer 10 repeats × 10 folds, inner 10 × 10 × 5), only the observation weights (non-progressor weight 2) or the training rows (NDBE samples only, image block scaled on them; predictions for all held-out samples) changed; L-CNV is the stored one. Reproduction check (weight 1, all rows): exactly the stored predictions. The gate is rebuilt from the refitted L-IMG with the same cut-off rules ('R49 rules rebuilt') and, additionally, with the round-9 grid ('cut-offs re-tuned'); for these rows the detection target is the refitted R49's own training detection.

**Additions (not in the plan).**
- Controls: C1 (R49 with its 27 cut-off cells re-tuned by the round-9 rule), threshold-only dials ('threshold only' rows) on H&E, the gate score, the stacked score and max L-LATE (sequence all samples), and B1-img (stacked gate on L-IMG alone): they show what the training-side tuning rule gives without any memory.
- R49-aligned gate score (above); max L-LATE over all samples as a sequence-everything reference; H&E sample aggregation variants (mean over samples, mean of the top 2) with threshold-only, running-mean and EW rules.
- More memory functions: mean of the last 2; k-of-n variants (coordinator addition: 2-of-n anywhere, 2-of-last-3, consecutive-2, each pure and with a t_high override); 'change from own mean' (per-patient recalibration: score minus λ × the mean of the patient's earlier scores, λ = 0.5 or 1, first endoscopy minus the training non-progressor mean); EW with longer half-lives (0.5, 8, 16 years).
- p53 where available: B1 + p53 (aberrant at the endoscopy, result missing) and A2' (a p53-normal result certifies, same raise as A2); A1+A2' (EW memory with the p53 certificate).
- Combinations: A1+A2 (EW memory of the aligned gate score with the copy-number certificate lowering the score by 0.5 or 1 logit for Y years), B1+A1+A2 (same on the stacked gate score), A1+A2'.
- A4 (literature idea 3): the high band is no longer flagged on the slide alone; every endoscopy at or above t_low has its top sample sequenced and is flagged if L-LATE ≥ t_seq (t_low 90, 95, 98%; t_seq 70, 80, 90%); and memory rules on its aligned score. It sequences about 3 samples per patient (R49 1.94).
- Coordinator items: (1) per-patient ICC of non-progressor (and progressor) endoscopy scores before the memory rules, with the persistence ceiling (non-progressor patients flagged once only, twice, ≥ 3 times); (2) k-of-n variants with the loss from progressors with a single pre-event endoscopy (10 of 32); (3) cumulative false-flag curves by endoscopy index (first-k windows, all patients and patients with ≥ k endoscopies) for R49, P1 90% and the best memory rule; (4) pAUC (FPR ≤ 0.2) selection of the hyper-parameters as the alternative criterion.

**Robustness rows.** NDBE and ≥ 2 samples re-run the whole nested procedure in the row's population (the round-7c definitions, with `PRE` restricted before `setup`); R52(a) uses the round-7 refit predictions of the 693-sample set (4 added progressor patients, 17 samples; their age and sex are cohort means, used only by stacked rows, and their event is the endoscopy at 0 months before final) with R49 and P1 re-derived in that set; tissue strata (< / ≥ 256 tiles, endoscopy by its top-L-IMG sample or all its samples) restrict the evaluation of the main run's held-out calls. Between-repeat variance is read from the 10 per-repeat results. **Refit bootstrap (F3): not re-scored.** The 200 stored draws carry one prediction set per resampled population with copy identifiers and no per-copy patient timelines or repeats, so the longitudinal rules and the nested fold structure cannot be rebuilt from them without a new pipeline; the top-3 methods have no F3 row.

**Not done.** No ACE-B file was read. No deeper (4×) copy number (R58). The round-8 policy P7 to P9 (sequence once, then H&E) were not combined with memory.

**Privacy.** Only aggregates are committed (`results/paper_final/review_round9/`); row-level arrays, the later-grade table, refit predictions and per-fold candidate files stay on the cluster (`killcoyne_mm/review_round9/`). No identifiers or dates; patient cells below 5 are shown as '<5' in F0, in the curves and in the progressor-with-one-endoscopy columns where applicable.

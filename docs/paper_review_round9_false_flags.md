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

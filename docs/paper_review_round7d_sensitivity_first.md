# Review round 7d: sensitivity first: can a little sequencing remove false positives?

Status: PRE-SPECIFICATION (written 2026-10-20). The draft was reviewed by a biostatistician, a gastroenterologist and an ML methodologist; their must-change items are incorporated (reviews outside the repository). Nothing below has been run. Results are appended under the line at the end in a later commit; this section is not edited afterwards.

## Why, and status of this round

The authors reframe the question:
1. Fix sensitivity as high as possible, so that no progressor is missed.
2. Ask whether sequencing a few samples removes false positives that the H&E slide alone would raise.

So far every analysis fixed specificity and compared sensitivity, and no rule let sequencing overturn a slide-based flag.

This round is post hoc: the reframing follows the round-7 results (`docs/paper_review_round7_analyses.md`, `..._7b_gate.md`, `..._7c_gate_robustness.md`). Its primary contrast is pre-specified but hypothesis-generating. The key secondary contrast is tested only if the primary succeeds (fixed sequence). Rule V0 and its threshold procedure are frozen at this commit for external testing.

No model is refitted; stored outer and inner predictions are re-scored. No ACE-B file is read. Frozen bundles are unchanged. Conventions as in `docs/paper_review_round6_analyses.md` (5c10c27).

## Prerequisites (checked before anything is scored)

Confirm that sample-level inner and outer out-of-fold predictions exist for L-IMG, L-CNV, L-LATE and package L-CNV for every repeat and fold. Do the same for the R52(a) refit predictions (round 7) and for the refit-bootstrap draws if used.
- Any row whose arrays are missing is reported "not available"; nothing is refitted.
- In training, the endoscopy score, top sample and cleared status come from inner out-of-fold L-IMG. Copy-number calls come from inner out-of-fold L-CNV / L-LATE.

## Units

- **Primary:** pre-event endoscopies (288; 88 progressor).
- **Key secondary 1:** NDBE endoscopies only, i.e. those whose samples are all graded NDBE. This is where a rule would act clinically.
- **Key secondary 2:** patients (75; 32 progressor), with the bias corrections below. All patient-level comparisons are unmatched and descriptive.
- **Secondary:** samples.

## Rule V0 (primary): "clear on the slide, confirm by sequencing"

Endoscopy score `s_E` = maximum L-IMG over the endoscopy's pre-event samples. The top sample is the sample attaining it.

**Step 1: clear.** If `s_E` < `t_low`, clear the endoscopy without sequencing.
- `t_low` is the 2nd percentile of the training progressor endoscopies' inner out-of-fold `s_E` (98% training endoscopy sensitivity at this step).
- It is estimated with the Harrell–Davis quantile estimator.

**Step 2: confirm.** Otherwise, sequence the top sample and flag the endoscopy only if its L-CNV ≥ `t_cnv`.
- `t_cnv` is the highest threshold at which the **two-stage rule as a whole** flags ≥ 95% of training progressor endoscopies, given `t_low`.
- It is computed on inner out-of-fold predictions.

**Step 3.** Nothing is flagged without sequencing.

**V0+override** (reported alongside V0 at every unit). Endoscopies with any sample graded ID or LGD, or any p53-aberrant sample, follow guideline management (flagged by pathology). The rule acts only on the remaining endoscopies.

## Variants (all reported; none is promoted afterwards)

| Variant | Change from V0 |
|---|---|
| V1 | Confirm by L-LATE (H&E + copy number) instead of L-CNV; threshold set the same way |
| V2 | Sequence all samples of a non-cleared endoscopy; flag if any L-CNV ≥ `t_cnv2`, set the same way with the "any" rule |
| V4 | Keep a high band (`s_E` ≥ `t_high`, 90% training specificity) flagged without sequencing; only the middle band is confirmed by L-CNV (isolates the value of vetoing high-band flags) |
| V-p53 | On the 450 samples with p53: same step 1, then confirm with aberrant p53 on the top sample instead of copy number. Compared with V0 on the same subset at matched sensitivity |
| R49 gate | As specified in round 7, for reference |

The trade-off curve replaces separate cut-off variants.

## Comparators at matched sensitivity

For each repeat, each comparator's specificity is read at V0's realised endoscopy sensitivity from its empirical ROC, by linear interpolation between adjacent operating points. Values are averaged over repeats and re-matched in each bootstrap draw. This matching is evaluation-matched, which favours the comparators.

- **(H) H&E alone:** `s_E` thresholded.
- **(S-LATE) Sequence everything:** flag if any sample's L-LATE ≥ threshold.
- **(S-CNV) Sequence everything, copy number only:** flag if any sample's L-CNV ≥ threshold.
- **(R1) One random sample per endoscopy,** L-LATE (R41 seeds).

**Current care** (grade ID/LGD; grade ID/LGD or p53 aberrant on the p53 subset) is deterministic. It is reported as it is, shown as points on the trade-off curve. Also reported: the V0 family's sensitivity at current care's specificity, and its specificity at current care's sensitivity.

## Primary and secondary contrasts (fixed sequence)

1. **Primary.** Δ endoscopy specificity, V0 − (H), with two-sided 95% CI.
   - **Success:** lower 95% limit > 0 **and** realised V0 endoscopy sensitivity ≥ 0.90.
   - **Clinically relevant:** Δ ≥ 0.05, about 50 fewer repeat endoscopies per 1,000 endoscopies.
   - **Failure:** if the lower limit is ≤ 0 or the sensitivity condition fails, the manuscript reports that limited sequencing did not remove more false positives than raising the H&E threshold. No variant or curve point is then promoted, and the reframing is reported as tested and not supported.
2. **Key secondary (only if 1 succeeds).** Δ endoscopy specificity, V0 − (S-LATE), one-sided 95% bound against −0.05.
   - The margin of −0.05 is about 50 extra flagged non-progressor endoscopies per 1,000, about £23.6k at £471 each.
   - It is fixed before any 7d result.

## Uncertainty

- **Primary interval: patient bootstrap with threshold re-derivation.** 2,000 draws, `RandomState(0)`. In each draw, each fold's `t_low`, `t_cnv` and comparator matching are re-derived from the resampled training patients' inner out-of-fold predictions. Fitted models are held fixed. Success is judged on this interval.
- **Secondary interval:** the fixed-threshold bootstrap (as rounds 4–7).
- **Threshold stability:** for each fold, report `t_low`, `t_cnv`, the number of training progressor endoscopies and patients below `t_low`, and target against realised outer sensitivity.
- **Patient-level sensitivity:** detected progressor patients per repeat (median and range), an exact 95% interval on the median repeat, and a patient-bootstrap interval for the averaged proportion. With 32 progressors, detecting all 32 still has a lower limit of about 0.89.

## Patient level (bias-corrected, descriptive)

Non-progressors have about twice as many endoscopies, so they have more chances to be flagged. Reported:
- non-progressor patients ever flagged (of 43);
- the per-patient share of endoscopies flagged, averaged with each patient weighted equally;
- "ever flagged" within an equal window: each patient's last 2 pre-event endoscopies, with the last sequenced endoscopy as the reference point for non-progressors;
- flagged non-progressor endoscopies per patient-year.

## Timing (descriptive)

- Endoscopy sensitivity by time to event: < 2, 2–5 and > 5 years.
- For each progressor patient: time from first flag to event.
- The number of progressor patients first flagged only at their last pre-event endoscopy.
- For progressor endoscopies cleared by copy number at step 2: whether a later pre-event endoscopy of the same patient is flagged.
- A missed progressor is a patient never flagged before the event.

## Clinical output: per 1,000 NDBE surveillance endoscopies

A table for V0, V0+override, (H), (S-LATE), R49 and grade+p53, giving:
- endoscopies with sequencing;
- endoscopies flagged (each assumed to trigger expert review, p53 and a 6-month repeat endoscopy);
- progressor endoscopies missed;
- cost.

Costs are counted per 1,000 endoscopies at a 2% progressor-endoscopy prevalence, projected from class-conditional rates:

| Cost item | Value |
|---|---|
| Sequencing | £85 per sample, with sensitivity rows at £150 and £250 |
| Sequencing failures | 3%, treated as flags |
| Flag | £471 (repeat endoscopy) + £44 (expert pathology review, NHS histopathology proxy) + £20 (p53) |
| Slide scanning and AI | £5 per slide, all rules except grade |

Also reported: the extra cost per additional progressor patient detected compared with grade+p53. The cost of misses is not modelled; this is stated.

## Assumed clinical pathway (stated in the manuscript)

- The scored slide is the diagnostic H&E. Whether the scanned slides are diagnostic or the research sections cut beneath the DNA is unconfirmed (limitation).
- The sequenced DNA comes from the same FFPE block. Report how many V0-sequenced samples are not same-block pairs.
- Turnaround ≤ 4 weeks from endoscopy to decision.

## Trade-off curve (descriptive)

The V0 family over `t_low` at 90, 95 and 98% training step-1 sensitivity × overall two-stage target at 90, 95 and 98%. For each point:
- realised endoscopy sensitivity and specificity;
- share of samples sequenced;
- (H) and (S-LATE) specificity at the same realised sensitivity;
- current care as fixed points.

## Robustness of V0 (primary contrast)

- NDBE endoscopies (also key secondary)
- Earliest pre-event endoscopy per patient
- Endoscopies with ≥ 2 samples
- Tissue strata (< 256 / ≥ 256 tiles, by top sample)
- R52(a) cohort (refit predictions)
- Package copy-number features
- Between-repeat variance added
- Refit bootstrap if the prerequisites hold; otherwise "not available"

## Scripts and running

- **Script:** `scripts/paper_plan/rv7d_sensfirst.py`, reusing `rv7b_gate.py` and `rv7c_gate_rob.py`.
- **Execution:** cluster jobs via `campaign.sh`, prefix `rv7d`.
- **Outputs:** aggregates to `results/paper_final/review_round7d/`; results appended below by `rv7d_render.py`.

---

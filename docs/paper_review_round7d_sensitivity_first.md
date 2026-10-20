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

## Results

Rendered by `scripts/paper_plan/rv7d_render.py` from `results/paper_final/review_round7d/` (aggregate results 42df29f); script `scripts/paper_plan/rv7d_sensfirst.py`. No model was refitted; stored outer and inner out-of-fold predictions were re-scored. Unit = pre-event endoscopy unless stated. Single model = per-repeat values averaged over the 10 repeats. Intervals: **re-derived** = patient bootstrap, 2,000 draws (`RandomState(0)`), every threshold re-derived in each draw from the resampled training patients' inner predictions (the primary interval); **fixed** = the same draws with thresholds and calls fixed (rounds 4–7). Comparators are evaluation-matched: specificity read at the rule's per-repeat endoscopy sensitivity on the comparator's empirical ROC (linear interpolation), re-matched in each draw.

### Prerequisites

| Stored arrays | Outer (10 repeats, finite) | Inner (repeat × fold sets, img / cnv) | Repeat-folds with missing inner values | Inner rows in their own outer fold | Status |
|---|---|---|---|---|---|
| L-IMG / L-CNV / L-LATE (stored, cfg_00 / cfg_02 outer; horizons/inner img and cnv_their) | yes | 100 / 100 | 0 | 0 | available |
| package L-CNV (cfg_01 outer; horizons/inner cnv_pkg) | yes | 100 / 100 | 0 | 0 | available |
| R52(a) refit (review_round7/refit/r52a) | yes | 100 / 100 | 0 | 0 | available |
| refit bootstrap draws (review_round2/f3) | 200 of 200 draws with outer and inner L-CNV and L-IMG | | | | available |
| R41 random-one seeds | regenerated (seeds 0-99, R41 draw order) | | | | available |

In training, the endoscopy score, top sample and cleared status come from inner out-of-fold L-IMG and the copy-number confirmation from inner out-of-fold L-CNV (L-LATE for V1). p53 (analysed-sample table, `P53 IHC`, as R37): available for 450 pre-event samples, aberrant in 18; identical to the field of the endoscopy table: yes. Nothing was 'not available'; nothing was refitted.

### Primary contrast (fixed sequence, step 1)

288 pre-event endoscopies (88 progressor), 571 samples, 75 patients (32 progressor).

| Rule | Endoscopy sens [re-derived] [fixed] | Endoscopy spec [re-derived] [fixed] | Samples sequenced | Endoscopies sequenced |
|---|---|---|---|---|
| **V0** (clear on the slide, confirm top sample by L-CNV) | 0.949 [0.907, 0.961] [0.923, 0.973] | 0.358 [0.282, 0.496] [0.282, 0.440] | 40.8% | 80.9% |
| (H) H&E alone at V0's sensitivity | (matched) | 0.374 [0.281, 0.574] [0.286, 0.516] | 0.0% | 0.0% |

**Δ endoscopy specificity, V0 − (H): -0.016**, 95% CI [-0.133, +0.061] (re-derived, primary interval); [-0.140, +0.054] (fixed). Realised V0 endoscopy sensitivity 0.949. Per repeat: +0.070, +0.040, -0.080, +0.040, -0.055, -0.075, -0.205, +0.010, +0.025, +0.075.

- Lower 95% limit > 0: no. Sensitivity ≥ 0.90: yes. Clinically relevant (Δ ≥ 0.05): no.

**Verdict: failure.** Limited sequencing did not remove more false positives than raising the H&E threshold. No variant or curve point is promoted, and the reframing is reported as tested and not supported.

### Key secondary contrast (fixed sequence, step 2): V0 − (S-LATE)

Status: **not tested (primary failed)**.

Δ endoscopy specificity V0 − (S-LATE) -0.121; one-sided 95% lower bound -0.254 (re-derived), -0.229 (fixed); two-sided 95% CI [-0.280, -0.018] (re-derived), [-0.251, -0.030] (fixed). Margin −0.05 (about 50 extra flagged non-progressor endoscopies per 1,000; about £23.6k at £471 each).

Computed for completeness only; because the primary contrast failed, it is not tested and supports no claim.

### Comparators at V0's sensitivity (all evaluation-matched)

| Comparator | Endoscopy spec at V0's sensitivity [re-derived] | Samples sequenced | V0 − comparator, Δ spec [re-derived] | [fixed] |
|---|---|---|---|---|
| (H) H&E alone | 0.374 [0.281, 0.574] | 0.0% | -0.016 [-0.133, +0.061] | [-0.140, +0.054] |
| (S-LATE) sequence everything, L-LATE | 0.479 [0.388, 0.681] | 100% | -0.121 [-0.280, -0.018] | [-0.251, -0.030] |
| (S-CNV) sequence everything, L-CNV | 0.336 [0.231, 0.529] | 100% | +0.023 [-0.117, +0.148] | [-0.106, +0.119] |
| (R1) one random sample, L-LATE (seeds 0-99) | 0.532 [0.373, 0.693] | 50.4% | -0.173 [-0.303, +0.017] | [-0.294, +0.019] |

Current care (deterministic; exact intervals): grade ID/LGD, endoscopy sensitivity 0.364 [0.264, 0.473], specificity 0.760 [0.695, 0.817]; grade ID/LGD or p53 aberrant on the p53 subset (220 endoscopies, 62 progressor): 0.419 / 0.728. The V0 family at grade's specificity reaches sensitivity n/a, and at grade's sensitivity specificity n/a; on the p53 subset against grade + p53: n/a and n/a (n/a = outside the family's range: the nine V0 grid points span sensitivity 0.893–0.970 and specificity 0.270–0.534; on the p53 subset 0.869–0.971 and 0.278–0.539).

### V0+override

- all pre-event endoscopies: sensitivity 0.963 [0.926, 0.973], specificity 0.288 [0.220, 0.404], samples sequenced 27.3%, endoscopies sequenced 54.2%; Δ spec vs (H) at its sensitivity -0.035 [-0.161, +0.022] (fixed [-0.146, +0.029]); vs (S-LATE) -0.171 [-0.331, -0.062].
- NDBE endoscopies: sensitivity 0.941 [0.873, 0.959], specificity 0.379 [0.297, 0.523], samples sequenced 39.9%, endoscopies sequenced 75.0%; Δ spec vs (H) at its sensitivity +0.011 [-0.122, +0.072] (fixed [-0.115, +0.083]); vs (S-LATE) -0.132 [-0.286, -0.012].

Override endoscopies (any ID / LGD / p53-aberrant sample): 86 of 288 (37 progressor). The rule acts on the rest with V0's thresholds; p53 missing counts as wild-type.

### NDBE endoscopies (key secondary unit 1)

208 endoscopies whose samples are all NDBE (56 progressor; 68 patients, 25 progressor). V0 (thresholds as the primary) sensitivity 0.930 [0.857, 0.955], specificity 0.381 [0.300, 0.526]; samples sequenced 41.4%, endoscopies 77.7%.

- Δ spec V0 − (H): -0.027 [-0.152, +0.052] (re-derived), [-0.147, +0.042] (fixed); (H) spec 0.408.
- Δ spec V0 − (S-LATE): -0.153 [-0.300, -0.021]; one-sided bound -0.276 (re-derived), -0.263 (fixed).

### Variants (all reported; none promoted)

| Rule | Endo sens [re-derived] | Endo spec [re-derived] | Samples / endoscopies sequenced | (H) spec at its sens | Δ spec vs (H) [re-derived] [fixed] | Δ spec vs (S-LATE) [re-derived] |
|---|---|---|---|---|---|---|
| **V0** (clear on the slide, confirm top sample by L-CNV) | 0.949 [0.907, 0.961] | 0.358 [0.282, 0.496] | 40.8% / 80.9% | 0.374 | -0.016 [-0.133, +0.061] [-0.140, +0.054] | -0.121 [-0.280, -0.018] |
| V1 (confirm by L-LATE) | 0.942 [0.904, 0.954] | 0.469 [0.358, 0.588] | 40.8% / 80.9% | 0.384 | +0.085 [-0.057, +0.154] [-0.025, +0.150] | -0.032 [-0.180, +0.033] |
| V2 (sequence all samples of an uncleared endoscopy) | 0.948 [0.903, 0.959] | 0.370 [0.286, 0.503] | 84.0% / 80.9% | 0.379 | -0.008 [-0.140, +0.072] [-0.128, +0.065] | -0.098 [-0.266, -0.015] |
| V4 (high band flagged unsequenced) | 0.947 [0.906, 0.960] | 0.410 [0.319, 0.562] | 28.3% / 56.1% | 0.385 | +0.025 [-0.097, +0.138] [-0.079, +0.101] | -0.064 [-0.208, +0.024] |
| V0+override (ID / LGD / p53-aberrant → guideline) | 0.963 [0.926, 0.973] | 0.288 [0.220, 0.404] | 27.3% / 54.2% | 0.323 | -0.035 [-0.161, +0.022] [-0.146, +0.029] | -0.171 [-0.331, -0.062] |
| R49 gate (round 7, reference) | 0.907 [0.863, 0.940] | 0.560 [0.424, 0.671] | 25.5% / 50.5% | 0.493 | +0.067 [-0.060, +0.180] [-0.038, +0.165] | -0.030 [-0.115, +0.041] |

V-p53 on the p53 subset (220 endoscopies, 62 progressor, 450 samples): sensitivity 0.148 [0.070, 0.229], specificity 1.000 [1.000, 1.000]; p53 read on 79.9% of these endoscopies. V0 on the same subset at its own thresholds: 0.944 / 0.365; V0 at V-p53's sensitivity (t_cnv evaluation-matched, step 1 fixed): specificity 1.000. Δ spec V-p53 − V0 +0.000 [+0.000, +0.004] (re-derived), [+0.000, +0.004] (fixed).

### Patient level (key secondary unit 2; bias-corrected, unmatched, descriptive)

75 patients (32 progressor, 43 non-progressor); pre-event endoscopies per patient: progressor 2.75, non-progressor 4.65; non-progressor follow-up 285.5 patient-years. (H) and (S-LATE) here use the threshold reaching V0's per-repeat endoscopy sensitivity (binary calls).

| Rule | Progressor patients detected per repeat: median (range) of 32 [exact 95% CI, median repeat] | Non-progressor patients ever flagged (of 43) | Per-patient share of endoscopies flagged, equal weights: progressor / non-progressor | Last 2 endoscopies: progressor detected share / non-progressor patients flagged (of 43) | Flagged non-progressor endoscopies per patient-year |
|---|---|---|---|---|---|
| V0 | 32.0 (31–32) [0.891, 1.000] | 39.1 | 0.961 / 0.635 | 0.991 / 35.7 | 0.449 |
| V0+override | 32.0 (31–32) [0.891, 1.000] | 40.5 | 0.971 / 0.700 | 0.997 / 35.9 | 0.499 |
| (H) H&E alone | 32.0 (31–32) [0.891, 1.000] | 39.8 | 0.962 / 0.622 | 0.997 / 35.8 | 0.439 |
| (S-LATE) sequence everything | 31.5 (30–32) [0.838, 0.999] | 33.4 | 0.948 / 0.510 | 0.981 / 28.4 | 0.365 |
| R49 gate | 31.0 (29–32) [0.838, 0.999] | 31.8 | 0.917 / 0.424 | 0.972 / 25.9 | 0.308 |
| grade + p53 (current care) | 21.0 (21–21) [0.468, 0.814] | 25.0 | 0.439 / 0.228 | 0.656 / 5.0 | 0.172 |

V0 progressor-patient detection averaged over repeats 0.997, patient bootstrap 95% CI [0.965, 1.000] (re-derived), [0.989, 1.000] (fixed). With 32 progressors, detecting all still has an exact lower limit of about 0.89.

### Timing (descriptive)

| Rule | Endo sens, < 2 y | 2–5 y | > 5 y | Years first flag → event: median of repeat medians (pooled IQR) | Progressor patients first flagged only at last pre-event endoscopy (of whom ≥ 2 endoscopies) | Missed progressor patients (range over repeats) |
|---|---|---|---|---|---|---|
| V0 | 0.928 | 0.955 | 0.954 | 5.00 (2.50–7.00) | 10.5 (0.6) | 0.1 (0–<5) |
| V0+override | 0.944 | 0.974 | 0.957 | 5.00 (2.50–7.00) | 10.4 (0.5) | 0.1 (0–<5) |
| (H) H&E alone | 0.933 | 0.969 | 0.929 | 5.00 (2.50–7.50) | 10.8 (0.9) | 0.1 (0–<5) |
| (S-LATE) sequence everything | 1.000 | 0.952 | 0.911 | 4.95 (2.50–7.00) | 10.0 (0.5) | 0.6 (0–<5) |
| R49 gate | 0.944 | 0.924 | 0.857 | 4.95 (2.50–7.00) | 10.0 (0.6) | 0.9 (0–<5) |
| grade + p53 (current care) | 0.722 | 0.381 | 0.286 | 3.00 (1.50–5.00) | 12.0 (6.0) | 11.0 (11–11) |

Progressor endoscopies per band: < 2 y 18, 2–5 y 42, > 5 y 28. Counts per patient are means over the 10 repeats.

V0, progressor endoscopies cleared by copy number at step 2: 2.0 per repeat; a later pre-event endoscopy of the same patient is flagged for 0.8, a later one exists but is not flagged for 0.2, and there is no later pre-event endoscopy for 1.0. A missed progressor is a patient never flagged before the event.

### Samples (secondary unit)

| Rule | Sample sens | Sample spec |
|---|---|---|
| V0 | 0.957 | 0.319 |
| V0+override | 0.971 | 0.260 |
| (H) H&E alone | 0.965 | 0.316 |
| (S-LATE) sequence everything | 0.963 | 0.420 |
| R49 gate | 0.933 | 0.514 |
| grade + p53 (current care) | 0.509 | 0.727 |

Each sample takes its endoscopy's call.

### Clinical output: per 1,000 NDBE surveillance endoscopies

Class-conditional rates on the 208 NDBE endoscopies (56 progressor), projected to a 2% progressor-endoscopy prevalence. **Costs are the pre-specification's assumptions**, not measured: sequencing £85 per sample (sensitivity £150, £250); 3% sequencing failures, treated as flags; each flag £535 (repeat endoscopy £471 + expert pathology review £44, an NHS histopathology proxy, + p53 £20); slide scanning and AI £5 per slide for every rule except grade + p53. The cost of misses is not modelled. (H) and (S-LATE) use the threshold reaching V0's per-repeat sensitivity on the NDBE endoscopies.

| Rule | Endoscopies with sequencing | Endoscopies flagged | Progressor endoscopies missed | Cost at £85 | at £150 | at £250 | Extra cost per additional progressor patient detected vs grade + p53 (£85) |
|---|---|---|---|---|---|---|---|
| V0 | 716.1 | 628.0 | 1.38 | £406,821 | £453,368 | £524,978 | £56,622 |
| V0+override | 709.8 | 630.2 | 1.17 | £407,432 | £453,569 | £524,550 | £56,708 |
| (H) H&E alone | 0.0 | 598.9 | 1.39 | £330,353 | £330,353 | £330,353 | £45,863 |
| (S-LATE) sequence everything | 1000.0 | 504.6 | 1.34 | £448,661 | £577,684 | £776,183 | £63,793 |
| R49 gate | 572.5 | 431.5 | 2.28 | £289,466 | £326,679 | £383,929 | £41,792 |
| grade + p53 (current care) | 0.0 | 8.2 | 18.21 | £4,405 | £4,405 | £4,405 | (reference) |

Additional progressor patients per 1,000 endoscopies are projected as (20 progressor endoscopies ÷ 2.24 progressor NDBE endoscopies per progressor patient) × the rule's patient detection on the NDBE endoscopies. Extra cost per additional progressor endoscopy detected (£85): V0 £23,900; V0+override £23,644; (H) H&E alone £19,377; (S-LATE) sequence everything £26,327; R49 gate £17,888.

### Assumed clinical pathway

V0 sequences 232.9 samples per repeat; 11.0 per repeat are not labelled same-block pairs. Over the 10 repeats 342 distinct samples are sequenced at least once, 13 of them not same-block (different block, block not recorded, or case unparseable; round-7 lookup Q1 labels). Whether the scanned slides are the diagnostic H&E or research sections is unconfirmed (limitation); turnaround ≤ 4 weeks is assumed.

### Trade-off curve (descriptive)

| t_low: training step-1 sensitivity | Two-stage target | Endo sens | Endo spec | Samples sequenced | Endoscopies sequenced | (H) spec at same sens | (S-LATE) spec at same sens | Folds where the target was unreachable |
|---|---|---|---|---|---|---|---|---|
| 90% | 90% | 0.893 | 0.534 | 30.8% | 61.0% | 0.528 | 0.636 | 40 |
| 90% | 95% | 0.900 | 0.518 | 30.8% | 61.0% | 0.521 | 0.626 | 100 |
| 90% | 98% | 0.900 | 0.518 | 30.8% | 61.0% | 0.521 | 0.626 | 100 |
| 95% | 90% | 0.902 | 0.491 | 36.4% | 72.3% | 0.506 | 0.605 | 0 |
| 95% | 95% | 0.940 | 0.384 | 36.4% | 72.3% | 0.396 | 0.516 | 51 |
| 95% | 98% | 0.941 | 0.373 | 36.4% | 72.3% | 0.395 | 0.515 | 100 |
| 98% | 90% | 0.900 | 0.478 | 40.8% | 80.9% | 0.514 | 0.577 | 0 |
| 98% | 95% | 0.949 | 0.358 | 40.8% | 80.9% | 0.374 | 0.479 | 0 |
| 98% | 98% | 0.970 | 0.270 | 40.8% | 80.9% | 0.271 | 0.446 | 63 |
| current care: grade ID/LGD | — | 0.364 | 0.760 | 0.0% | 0.0% | | | |
| current care: grade or p53 (p53 subset) | — | 0.419 | 0.728 | 0.0% | 0.0% | | | |

The primary V0 is the 98% / 95% cell. Where the two-stage target exceeds what step 1 leaves in training, no copy-number threshold reaches it and every uncleared endoscopy is flagged (last column; such points coincide). Because the primary contrast failed, no curve point is promoted.

### Threshold stability (100 folds)

- t_low: 0.042 (IQR 0.033–0.060; range 0.007–0.164); t_cnv: 0.016 (IQR 0.008–0.035; range 0.000–0.162); folds where no copy-number threshold met the target (all uncleared flagged): 0.
- Training progressor endoscopies per fold: 80 (range 68–87). Folds by training progressor endoscopies below t_low: none 0, 1–4 100, ≥ 5 0; by training progressor patients below t_low: none 0, 1–4 100, ≥ 5 0.
- Targets against realised: step 1 target 0.98, training 0.976 (IQR 0.975–0.987; range 0.971–0.988), outer per fold 1.000 (IQR 1.000–1.000; range 0.800–1.000); two-stage target 0.95, training 0.954 (IQR 0.951–0.961; range 0.950–0.962), outer per fold 1.000 (IQR 0.909–1.000; range 0.571–1.000); outer per repeat 0.966, 0.966, 0.932, 0.932, 0.966, 0.966, 0.943, 0.955, 0.943, 0.920.

### Robustness of V0 (primary contrast)

| Row | Endoscopies (progressor) / samples / patients (progressor) | V0 endo sens / spec | (H) spec at V0's sens | Δ spec V0 − (H) [re-derived] | [fixed] | Lower limit > 0 | Samples / endoscopies sequenced | Δ spec V0 − (S-LATE) (bound) |
|---|---|---|---|---|---|---|---|---|
| all pre-event endoscopies (reference) | 288 (88) / 571 / 75 (32) | 0.949 / 0.358 | 0.374 | -0.016 [-0.133, +0.061] | [-0.140, +0.054] | no | 40.8% / 80.9% | -0.121 (-0.254) |
| NDBE endoscopies (all samples graded NDBE) | 208 (56) / 391 / 68 (25) | 0.930 / 0.381 | 0.408 | -0.027 [-0.152, +0.052] | [-0.147, +0.042] | no | 41.4% / 77.7% | -0.153 (-0.276) |
| earliest pre-event endoscopy per patient | 75 (32) / 140 / 75 (32) | 0.956 / 0.407 | 0.374 | +0.033 [-0.145, +0.097] | [-0.128, +0.082] | no | 43.7% / 81.6% | -0.081 (-0.252) |
| endoscopies with ≥ 2 samples | 146 (40) / 429 / 64 (25) | 0.962 / 0.310 | 0.371 | -0.060 [-0.303, +0.008] | [-0.304, -0.006] | no | 29.0% / 85.1% | -0.220 (-0.429) |
| < 256 tissue tiles (by top sample) | 142 (39) / 309 / 67 (25) | 0.959 / 0.349 | 0.450 | -0.102 [-0.210, +0.001] | [-0.237, -0.012] | no | 37.2% / 80.8% | -0.109 (-0.265) |
| ≥ 256 tissue tiles (by top sample) | 146 (49) / 262 / 63 (25) | 0.941 / 0.369 | 0.361 | +0.008 [-0.187, +0.070] | [-0.180, +0.068] | no | 45.1% / 80.9% | -0.153 (-0.306) |
| R52(a) cohort (refit predictions) | 290 (90) / 577 / 77 (34) | 0.938 / 0.367 | 0.435 | -0.068 [-0.183, +0.040] | [-0.200, +0.028] | no | 41.1% / 81.8% | -0.153 (-0.255) |
| package copy-number features | 288 (88) / 571 / 75 (32) | 0.948 / 0.486 | 0.360 | +0.126 [-0.069, +0.208] | [-0.042, +0.225] | no | 40.8% / 80.9% | -0.107 (-0.225) |
| between-repeat variance added (as R33) |  |  |  | -0.016 [-0.213, +0.182] (variance-inflated CI) |  | no |  |  |
| refit bootstrap (F3, 200 draws) |  | 0.907 / 0.266 | 0.353 | -0.087 [-0.369, +0.163] (percentile over draws) |  | no | 44.0% | -0.159 |

Of 9 robustness rows, the lower 95% limit of Δ spec V0 − (H) is above 0 in 0 and not above 0 in 9; none was not available. Reporting only; the verdict rests on the primary row.

Refit bootstrap: V0 − (H) Δ spec positive in 0.250 of the 200 draws; held-out pre-event endoscopies per draw median 286 (range 244–330).

### Checks

- R49 through this code: sens, spec, samples, endoscopies 0.907, 0.560, 0.255, 0.505, sensitivity CI (fixed) [0.861, 0.951] (round 7: 0.907, 0.560, 0.255, 0.505, [0.861, 0.951]); reproduced: yes. Pre-specification: 0.907 / 0.560, 25.5% of samples.
- (H) at R49's sensitivity (0.907): specificity 0.493 (evaluation-matched); C\*-endo (training-matched, round 7c) 0.890, 0.541; (H) at C\*-endo's own sensitivity: specificity 0.550 (evaluation matching favours (H)).
- (S-LATE) at B\*-endo's sensitivity: specificity 0.534; B\*-endo 0.923, 0.530 (expected 0.923 / 0.530, reproduced: yes); difference in specificity +0.005 (evaluation matching favours the comparator).
- Refit bootstrap: R49 re-scored on the 200 stored F3 draws, mean sens / spec 0.874, 0.478 (round 7c: 0.874, 0.478); reproduced: yes.
- Same-block labels of the 571 pre-event samples (round-7 lookup Q1: same / different / unknown = 556 / 6 / 9): same case, block not recorded on one side 9, same case, different block 6, same case, same block 556.

### Implementation notes

- Endoscopy = (patient, endoscopy number) over its pre-event samples; `s_E` = maximum L-IMG, top sample = the sample attaining it. In each (repeat, fold) the training endoscopies are the fold's training pre-event samples grouped the same way, scored by inner out-of-fold L-IMG (score, top sample, cleared) and inner L-CNV / L-LATE of the top sample (confirmation).
- `t_low` = Harrell–Davis 0.02 quantile (`scipy.stats.mstats.hdquantiles`) of the training progressor endoscopies' `s_E`; cleared if `s_E` < `t_low`. `t_cnv` = the largest threshold at which the two-stage rule flags ≥ 95% of training progressor endoscopies (cleared ones count as not flagged; the ⌈0.95 n⌉-th largest confirmation score among them). If no threshold reaches the target, every uncleared endoscopy is flagged (counted under threshold stability).
- V1 confirms by the top sample's L-LATE; V2 by the maximum L-CNV over all samples of an uncleared endoscopy (all its samples sequenced); V4 keeps a high band `s_E` > `t_high` (the training non-progressor endoscopies' 90% specificity point, the c\* convention of the triage, which guarantees ≥ 90% training specificity) flagged unsequenced, with `t_cnv` set for the rule as a whole. Each variant's thresholds are derived the same way.
- V0+override uses V0's thresholds unchanged: endoscopies with any ID / LGD or p53-aberrant sample are flagged by pathology and not sequenced; p53 missing counts as wild-type (as R47). V-p53: endoscopies restricted to their samples with p53; step 1 with V0's `t_low`; flag if the top sample (by L-IMG among them) is p53-aberrant. 'V0 on the same subset at matched sensitivity' varies `t_cnv` with step 1 fixed (evaluation-matched to V-p53's per-repeat sensitivity).
- Comparators: (H) = `s_E`, (S-LATE) / (S-CNV) = maximum sample L-LATE / L-CNV, (R1) = L-LATE of one random sample per endoscopy (seeds 0–99, R41 draw order, specificity averaged over seeds). For each repeat the empirical ROC is pooled across folds, and specificity is read at the rule's realised endoscopy sensitivity in that repeat by linear interpolation between adjacent operating points; values are averaged over repeats and re-matched in each draw. The pre-specification's 'comparator matching re-derived from the training patients' is read as this evaluation-set re-matching, since no comparator threshold is set on training data.
- Bootstrap: patients of the analysed population drawn with replacement (`RandomState(0)`, the R49 loop; draws whose evaluated endoscopies are one-class are rejected), multiplicities used as integer weights. Re-derived: in each draw every fold's `t_low` (Harrell–Davis on the replicated training progressor endoscopies), `t_cnv`, the variants' thresholds and R49's triage cut-offs (tb_common.triage with weights) are recomputed; fitted models fixed. Fixed: the same draws, observed calls. The primary row's draws coincide with R49's, so R49's fixed interval reproduces round 7.
- Units: subsets (NDBE endoscopies, earliest endoscopy, ≥ 2 samples, tissue strata) evaluate the frozen V0 (thresholds from all training pre-event endoscopies) on that subset of endoscopies; draws resample all patients and evaluate the subset. The R52(a) and package rows use their own stored predictions with every threshold re-derived. Earliest = the endoscopy with the largest months-before-final per patient; tissue strata by the tissue tiles of the sample with the highest L-IMG averaged over repeats (as round 7c).
- Patient level: a patient is flagged if any of its pre-event endoscopies is. (H) and (S-LATE) use the binary threshold reaching V0's per-repeat sensitivity (`thr_sens`), which can give them slightly higher sensitivity than V0. Equal window: each patient's last 2 pre-event endoscopies (smallest months-before-final; for non-progressors the last sequenced endoscopy is the reference). Patient-years: span from first to last pre-event endoscopy (R47). Exact interval = Clopper–Pearson on the median repeat's count (lower median for an even split).
- Timing: endoscopy time to event = the samples' years to event; first flag = the earliest flagged pre-event endoscopy; 'first flagged only at the last pre-event endoscopy' = only the last endoscopy flagged. 'Cleared by copy number' = progressor endoscopies sequenced and not flagged in that repeat.
- Clinical table: rates from the NDBE endoscopies, means over repeats; a sequencing failure (3% per sequenced sample, independent) turns an unflagged endoscopy into a flag; samples sequenced, flags and slides are projected to 1,000 endoscopies at 2% prevalence as π·(progressor rate) + (1 − π)·(non-progressor rate). Extra cost per additional progressor patient is a projection through the cohort's progressor NDBE endoscopies per progressor patient (stated above); grade + p53 uses grade or p53-aberrant with missing p53 as wild-type and costs no scanning.
- Same-block status: the round-7 lookup Q1 labels (clinical_lookup/q6_q1fix.py logic copied, read-only); only aggregate counts are reported.
- Refit bootstrap: the 200 stored F3 draws (one 10-fold CV per patient-bootstrap draw); V0's thresholds re-derived per draw and fold from the draw's inner predictions; units = resampled patient copy × endoscopy; (H) and (S-LATE) evaluation-matched to V0's sensitivity in the draw.
- Between-repeat variance: mean of the 10 per-repeat Δ ± 1.96 √(V_boot + V_rep), V_boot from the re-derived draws (R33 / R15 rule).
- Costs are the pre-specification's values, labelled as assumptions. Checks compare values at three decimals with a tolerance of 0.0015.

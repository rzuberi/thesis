# Two papers, agent P2S: Paper 2 safety and design analyses

Status: EXPLORATORY (21 October 2026). Shared rules: `paper/two_papers/RUN_RULES.md`. Tasks: `paper/two_papers/PAPER2_plan_v2.md` items 2–8, plus the brief's items (memory audit, per-1,000 patient-years, the 4 failing robustness rows). Reviews read: `review_P2_gastro.md`, `review_P2_editor.md`, `review_strategy_sceptic.md`.

## Plan

**Tiers under test (frozen per-fold rules, no re-implementation).**
- **No sequencing:** mean-logit endoscopy score + EW memory (E3 / E9 family `A1:img:ew` on the mean-logit variant): 31.0 caught / 26.6 NP flagged.
- **Confirmatory:** final rule (A12 memory + certificate + quiet-genome check, cn90 bar): 30.5 / 17.2; fold-internal bar: 30.4 / 16.4.
- **Comparators:** per-endoscopy gate R49 (this study), H&E alone (P1 90%), sequencing everything (P3 90%), grade IND/LGD, grade IND/LGD or p53 aberrant; single-endoscopy counterparts of each memory rule (mean-logit single endoscopy; gate score single endoscopy); Prague M and a Parasa-style score, with and without memory.

**Code.** `scripts/paper_plan/tp_p2s_main.py` executes `ex_e7_stress.py` up to its dispatch (which executes `ex_e2_veto.py` and `rv9_falseflags.py`) and the helper section of `ex_e3_score.py` (mean-logit variant as `ex_e9_frontier.py` `state('ml')`). The only new engine piece is `engine2` = `ex_e7_stress.engine` plus the chosen candidate's held-out margin (score − fold threshold). Smoke first (50 draws), reproducing R49 31.1/31.8, P1 31.1/36.0, grade 17.0/25.0, A1 30.7/23.6, A12 30.5/21.5, final 30.5/17.2, fold-internal bar 30.4/16.4, mean-logit + memory 31.0/26.6, and E7's equal-exposure A1 −6.1.

**Analyses.**
1. **Memory audit:** code reading, unit tests (future scores replaced by noise; memory and certificate at or before the cut unchanged), an end-to-end test (held-out predictions of every later endoscopy replaced by noise, whole nested pipeline rerun, flags up to the cut compared) and a cross-patient test.
2. **Landmark analysis:** every pre-event endoscopy is a landmark scored on history to date; outcome = progression within 1, 3, 5 years or ever. Sensitivity, specificity, PPV, NPV at the operating point, and landmark AUROC of the margin, memory vs single-endoscopy scoring, patient-bootstrap CIs. Equal exposure as a primary row: (a) patient level, E7 truncation (non-progressors cut to progressor endoscopy counts, 200 draws, frozen rules); (b) landmark level with the same truncation weights. Patient-weighted landmarks as a secondary row.
3. **Two-consecutive-lows rule:** de-escalate only after ≥ 2 consecutive low endoscopies; NP cleared lost and progressors de-escalated, against single-look de-escalation.
4. **Safety block:** missed (never flagged) and "cleared at the last pre-event endoscopy" progressors per tier: HGD vs IMC, focal HGD, time from the last cleared endoscopy to the event, Prague M, whether a 5-year (or 3-year) interval from that endoscopy would have postponed detection past the event date. Aggregate only (<5 suppressed). NPV among cleared patients; integer counts per repeat and majority-vote counts with exact CIs.
5. **Lead time:** evaluation restricted to endoscopies > 2 y and > 4 y before the event (NP all endoscopies, or symmetric).
6. **Clinical comparators:** Prague M and a Parasa-style score (9 × male + 5 × smoker + 1 per cm + 11 × LGD), single endoscopy and with memory, training-chosen thresholds and fixed published cut-offs; missingness reported.
7. **Subgroups:** segment length (< / ≥ 3 cm), age (< / ≥ 65), sex, samples per endoscopy.
8. **The 4 of 34 failing R49 robustness rows** (round 7c), named with the reason.
9. **Per 1,000 patient-years** in the de-escalated group at 0.3–0.6 %/yr incidence, model-based, with CIs.

**Space.** Aggregates `results/paper_final/two_papers_P2S/`; row-level `killcoyne_mm/two_papers_P2S/`; Slurm prefix `tpp2s`.

## Summary (what the numbers say)

- **Memory is causal (item 1).** Code reading, a unit test, an end-to-end test with every later endoscopy's held-out predictions replaced by noise, and a cross-patient test all pass with 0 mismatches. Nothing needed fixing.
- **Landmark analysis (item 2).** Scored on history to date, memory ranks later progression better than single-endoscopy scoring at every horizon: mean-logit Δ landmark AUROC +0.026 [0.010, 0.042] (ever), +0.027 [0.006, 0.050] (≤ 5 y), +0.030 [0.002, 0.064] (≤ 3 y); ≤ 1 y has 10 positive landmarks and is inconclusive. It survives equal exposure (ever +0.020 [0.003, 0.036]; ≤ 5 y +0.020 [−0.002, 0.045]) and patient weighting (ever +0.019 [0.004, 0.034]). At the operating points memory raises landmark sensitivity (+4.6 points at ≤ 5 y) and slightly lowers landmark specificity (−2.6): the patient-level gain comes from fewer patients ever crossing the line, not from fewer flagged endoscopies. The final rule's landmark sensitivity is lower than R49's (0.815 vs 0.929 at ≤ 5 y): it clears about 1 in 5 progressor endoscopies, and its patient-level catch depends on the next look.
- **Equal exposure, patient level (primary row).** No-sequencing tier 22.3 vs R49 25.9 NP flagged, −3.6 [−6.7, −0.6]; its own memory gain −2.3 [−3.7, −1.0] (−4.4 without truncation). Final −11.3 [−14.7, −8.1]; fold-internal −12.4 [−15.8, −9.2]; progressors caught −0.1 to −0.7, CIs include 0.
- **Two consecutive lows (item 3).** With the recommended reading (never flagged to date and two consecutive lows), non-progressors de-escalated at their last endoscopy are unchanged (no-sequencing 16.4, final 25.8, fold-internal 26.6 of 43: every never-flagged non-progressor has ≥ 2 endoscopies); non-progressors ever de-escalated fall by 3.7–6.2. Progressors whose interval would have been lengthened at the last look before the event: no-sequencing 1.0 → 0.1 [0.0, 0.3] (integer 0–1 over repeats), final 1.5 → 1.0 [0.2, 1.9] (0–3), fold-internal 1.6 → 1.1 [0.2, 2.1]. Without 'never flagged to date' (de-escalating on the current score after an earlier flag), 3.9 (final) and 5.8 (fold-internal) progressors are de-escalated at the last look: a flag must be sticky.
- **Safety (item 4).** Missed (never flagged) progressors: 1.0 per repeat (no sequencing; integer 0–2), 1.5 (final; 0–3), 1.6 (fold-internal; 0–3); no progressor is missed in ≥ 5 of 10 repeats under any tier (exact 95% upper limit 10.9% of 32). The final rule's misses include no IMC; the no-sequencing tier's do (in some repeats), but most of its misses have a single pre-event endoscopy, which the two-lows rule never de-escalates. For most misses the event came < 5 years after the last cleared endoscopy, so a 5-year interval would have put the next look after the event date. Cohort (case–control) NPV among never-flagged patients 0.944–0.947 for the tiers, 0.62 for grade + p53.
- **Lead time (item 5).** Endoscopies > 2 y before the event: no sequencing 23.5 / 24, final 22.7 / 24, grade + p53 14.0 / 24. > 4 y: 18.4, 17.7 and 6.0 of 20; the fold-internal bar loses 2.0 [0.6, 3.6] progressors against R49 there.
- **Clinical comparators (item 6).** Prague M and a Parasa-style score cannot reach the tiers' sensitivity: at R49's training detection they flag 41–42 of 43 non-progressors; fixed cut-offs give Prague M ≥ 3 cm 19 / 35, Parasa > 10 25 / 34, Parasa > 20 12 / 17 (caught / NP flagged). Even with thresholds set on the evaluated patients, at the no-sequencing tier's 26.6 NP flagged Parasa catches 20–22 and Prague 13 of 32. Memory adds nothing to them (both are essentially one value per patient). Smoking is missing for 33 of 75 patients and Prague M for 7 progressors.
- **Subgroups (item 7).** The tiers' gains against R49 hold across sex, age and segment-length groups (all small). The no-sequencing tier's gain sits in endoscopies with ≥ 2 samples (−4.4 NP vs R49) and is absent with < 2 (−0.8), as expected: with one sample the mean logit is the max.
- **The 4 failing R49 robustness rows (item 8):** ≥ 256 tiles (two definitions), between-repeat variance added, refit bootstrap; all fail by width, none by a shift.
- **Per 1,000 patient-years (item 9, model-based), λ = 0.45%/yr:** no sequencing 0.37 [0.04, 0.93], exact upper 1.9; final 0.35 [0.12, 0.66], exact upper 1.6; fold-internal 0.37, exact upper 1.5; R49 0.49, exact upper 2.8; grade + p53 3.7 [1.8, 6.4]; grade 5.0 (no triage 4.5). At λ = 0.6%/yr the exact upper limits of the tiers reach 2.0–2.6, at the 2 per 1,000 bar.

**What changes in the paper plan.** The clinical rule needs two parts, not one: no de-escalation on a single look, and no de-escalation after any flag (a flag returns the patient to guideline care); with both, the no-sequencing tier de-escalates essentially no progressor before the event at no cost in non-progressors cleared. The abstract's equal-exposure number should be the tier's own (−2.3 memory gain, −3.6 vs R49 for no sequencing; −11.3 for the final rule), not the gate-memory −6.1, and the safety bar for the ERIN test should be judged with exact limits, which sit near 2 per 1,000 patient-years at the top of the incidence range.

---

## Results

Rendered by `scripts/paper_plan/tp_p2s_render.py` from `results/paper_final/two_papers_P2S/` (analysis `scripts/paper_plan/tp_p2s_main.py`). Exploratory: every rule here came out of the ~650-variant search, and these analyses describe it; nothing is confirmatory. Held-out patients throughout; every threshold, half-life, certificate setting and check bar chosen on training patients (inner out-of-fold predictions of each outer fold). Counts are means over the 10 repeats unless they are labelled integer; intervals are paired patient-bootstrap 95% CIs (2,000 draws, `RandomState(0)`, the round-8 draws). Patient cells below 5 are shown as <5. No ACE-B file was read; stored predictions and frozen bundles were not touched.

### Reproduction (smoke and full run)

| Rule | Caught / 32 | NP flagged / 43 | Samples sequenced / patient | Expected |
|---|---|---|---|---|
| Per-endoscopy gate R49 (this study) | 31.1 | 31.8 | 1.94 | 31.1/31.8 |
| H&E alone (P1 90%) | 31.1 | 36.0 | 0.00 | 31.1/36.0 |
| Grade IND/LGD | 17.0 | 25.0 | 0.00 | 17.0/25.0 |
| Memory (gate score) | 30.7 | 23.6 | 1.94 | 30.7/23.6 |
| Memory + certificate | 30.5 | 21.5 | 1.94 | 30.5/21.5 |
| Confirmatory (final rule, cn90 bar) | 30.5 | 17.2 | 3.82 | 30.5/17.2 |
| Confirmatory, fold-internal bar | 30.4 | 16.4 | 3.82 | 30.4/16.4 |
| No sequencing (mean-logit + memory) | 31.0 | 26.6 | 0.00 | 31.0/26.6 |
| Mean-logit, single endoscopy | 30.9 | 31.0 | 0.00 |  |
| Gate score, single endoscopy | 30.7 | 29.4 | 1.94 |  |
| Grade IND/LGD or p53 aberrant | 21.0 | 25.0 | 0.00 |  |
| Sequence everything (P3 90%) | 31.2 | 31.8 | 7.61 |  |

Every expected number reproduced (`reproduced: True`), and the rebuilt held-out flags equal the stored ones exactly: 0 mismatches against `explore_E7/base_flags.npz` for R49, P1, grade, A1, A12, final and fold-internal final, and 0 against the E9 sweep for mean-logit + memory. E7's equal-exposure memory gain (A1 −6.1) reproduced as -6.1. The smoke run used 50 draws; the tables use 2,000.

### 1. Memory uses visits up to k only (audit)

**Verdict: pass.** Nothing needed fixing.

- **Code reading.** Rv9 memory(): EW weights ST['EW'][h] are lower-triangular in the patient's time order (np.tril, column <= row) and masked to valid slots; 'mean' is a cumulative sum; so the score at slot k uses slots <= k. Time order ORD (rv8 setup): exact endoscopy date (pre_event_cohort.Date), ties broken by months-before-final; weights use max(dt, 0) only for the diagonal. Rv9 cert_flags(): strictly earlier endoscopies (np.tril(..., -1)) within Y years. Quiet-genome check (ex_e2 vs_test / ex_e7 apply_check): the current endoscopy's own top-2 samples only; a cancelled flag is not fed back into the memory. Thresholds, half-life, certificate and check bar: training patients' inner out-of-fold predictions only (make_ctx / thr_for / infold_bar); held-out patients' outer predictions enter only their own memory. Patient-level outcomes use the maximum over a patient's endoscopies (ever flagged); this is an evaluation summary, not an input to any score.
- **Time order.** Patients whose order is not by exact date: 0; consecutive endoscopies on the same date: 0. 19 endoscopy units have samples dated on more than one day (the unit takes its earliest date, as in all earlier rounds).
- **Unit test.** Per patient a random cut; every score after the cut replaced by noise (×10 scale). Mismatches at or before the cut, for running mean, EW (h = 0.5–16 y), last-2, consecutive-2, 2-of-n, 2-of-3 and the certificate (Y = 2, 4): all 0. The current endoscopy does enter its own memory (sanity check: True).
- **End to end.** The held-out (outer) L-IMG and L-CNV predictions of every sample in a later endoscopy replaced by noise and the whole nested pipeline rerun (thresholds, half-life, certificate, check bar, fold-internal bar). Flag mismatches at or before the cut: A1 0, A12 0, final 0, fold-internal final 0, mean-logit + memory 0. Sanity: flags after the cut did change (210 and 416 endoscopy-repeats).
- **Other patients.** Whole histories of a random half of patients replaced by noise: final-rule flags of the untouched half changed at 0 endoscopy-repeats.

### Tiers and comparators (all 75 patients)

| Rule | Caught / 32 [CI] | NP flagged / 43 [CI] | Caught, integer range over repeats | NP flagged, integer range | Missed in ≥ 5 of 10 repeats (exact 95% CI of share) | NPV among never-flagged (case–control) [CI] | Seq. / patient | Δ NP vs grade + p53 | Δ caught vs grade + p53 |
|---|---|---|---|---|---|---|---|---|---|
| No sequencing (mean-logit + memory) | 31.0 [29.8, 31.9] | 26.6 [21.3, 31.7] | 30–32 | 23–30 | 0 (0.000–0.109) | 0.944 [0.868, 0.995] | 0.00 | +1.6 [−5.3, 9.3] | +10.0 [5.1, 14.9] |
| Confirmatory (final rule, cn90 bar) | 30.5 [29.3, 31.5] | 17.2 [12.1, 22.7] | 29–32 | 14–20 | 0 (0.000–0.109) | 0.947 [0.894, 0.985] | 3.82 | −7.8 [−14.7, −0.2] | +9.5 [4.4, 14.7] |
| Confirmatory, fold-internal bar | 30.4 [29.1, 31.5] | 16.4 [11.4, 21.8] | 29–32 | 11–19 | 0 (0.000–0.109) | 0.945 [0.888, 0.984] | 3.82 | −8.6 [−15.6, −1.1] | +9.4 [4.3, 14.6] |
| Mean-logit, single endoscopy | 30.9 [29.4, 32.0] | 31.0 [25.9, 35.6] | 30–32 | 27–34 | 0 (0.000–0.109) | 0.922 [0.815, 1.000] | 0.00 | +6.0 [−0.7, 13.6] | +9.9 [4.9, 14.8] |
| Memory (gate score) | 30.7 [29.5, 31.6] | 23.6 [18.3, 29.2] | 29–32 | 21–26 | 0 (0.000–0.109) | 0.938 [0.868, 0.985] | 1.94 | −1.4 [−8.4, 5.8] | +9.7 [4.7, 14.9] |
| Memory + certificate | 30.5 [29.3, 31.5] | 21.5 [16.3, 26.8] | 29–32 | 18–24 | 0 (0.000–0.109) | 0.938 [0.877, 0.982] | 1.94 | −3.5 [−10.3, 3.7] | +9.5 [4.4, 14.7] |
| Per-endoscopy gate R49 (this study) | 31.1 [29.7, 32.0] | 31.8 [27.0, 36.2] | 29–32 | 30–33 | <5 (0.001–0.162) | 0.930 [0.819, 1.000] | 1.94 | +6.8 [0.5, 13.3] | +10.1 [5.1, 15.2] |
| H&E alone (P1 90%) | 31.1 [29.5, 32.0] | 36.0 [31.4, 39.7] | 30–32 | 35–37 | <5 (0.001–0.162) | 0.892 [0.715, 1.000] | 0.00 | +11.0 [4.3, 17.9] | +10.1 [5.1, 15.0] |
| Sequence everything (P3 90%) | 31.2 [29.7, 32.0] | 31.8 [26.9, 36.4] | 30–32 | 29–34 | <5 (0.001–0.162) | 0.935 [0.825, 1.000] | 7.61 | +6.8 [0.3, 13.6] | +10.2 [5.1, 15.3] |
| Grade IND/LGD | 17.0 [11.6, 22.9] | 25.0 [18.6, 31.0] | 17–17 | 25–25 | 15 (0.291–0.653) | 0.545 [0.378, 0.722] | 0.00 | 0.0 [0.0, 0.0] | −4.0 [−8.0, −0.9] |
| Grade IND/LGD or p53 aberrant | 21.0 [15.5, 26.4] | 25.0 [18.6, 31.0] | 21–21 | 25–25 | 11 (0.186–0.532) | 0.621 [0.437, 0.800] | 0.00 | — | — |

NPV here is the cohort's 1:1 case–control value and is not a population NPV; item 9 gives the model-based population version. Integer counts per repeat are in `design.json` (`integer_counts.per_repeat`).

### 2. Landmark analysis (history to date only)

Every pre-event endoscopy is a landmark scored on the patient's history up to and including it. Positive at horizon h: progressor endoscopy with the event ≤ h years later. Negative: non-progressor endoscopy with known event-free follow-up ≥ h (to the last sequenced endoscopy, extended by later Barrett's database records, median 6.7 more years), or progressor endoscopy with the event > h years later. Operating points are each rule's own (training-chosen) thresholds. AUROC = landmark AUROC of the held-out score minus its fold threshold, pooled over folds, repeat mean; memory and single-endoscopy versions of the same base, each with its own training threshold.

**All landmarks (primary).**

| Horizon | Positive (patients) / negative landmarks | No-seq tier sens / spec | Mean-logit single sens / spec | Δ sens, memory − single | Δ spec, memory − single | AUROC memory vs single (mean-logit) | Δ AUROC (mean-logit) | Final sens / spec | Fold-internal sens / spec | R49 sens / spec | Δ AUROC, memory + certificate − single gate | Grade + p53 sens / spec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1y | 10 (10 P) / 267 | 0.950 / 0.443 | 0.850 / 0.476 | +0.100 [0.000, 0.257] | −0.033 [−0.062, −0.006] | 0.809 vs 0.765 | +0.044 [−0.004, 0.116] | 0.900 / 0.658 | 0.830 / 0.688 | 0.920 / 0.428 | +0.052 [0.011, 0.096] | 0.800 / 0.719 |
| 3y | 38 (27 P) / 224 | 0.953 / 0.481 | 0.895 / 0.506 | +0.058 [0.012, 0.116] | −0.025 [−0.054, 0.003] | 0.842 vs 0.812 | +0.030 [0.002, 0.064] | 0.853 / 0.702 | 0.782 / 0.728 | 0.963 / 0.471 | +0.006 [−0.012, 0.023] | 0.579 / 0.741 |
| 5y | 59 (32 P) / 187 | 0.937 / 0.529 | 0.892 / 0.556 | +0.046 [0.012, 0.086] | −0.026 [−0.061, 0.007] | 0.855 vs 0.828 | +0.027 [0.006, 0.050] | 0.815 / 0.741 | 0.753 / 0.767 | 0.929 / 0.508 | +0.017 [−0.003, 0.038] | 0.508 / 0.759 |
| ever | 88 (32 P) / 200 | 0.924 / 0.587 | 0.882 / 0.625 | +0.042 [0.015, 0.071] | −0.038 [−0.077, 0.000] | 0.877 vs 0.851 | +0.026 [0.010, 0.042] | 0.793 / 0.829 | 0.730 / 0.845 | 0.907 / 0.560 | +0.038 [0.020, 0.057] | 0.420 / 0.755 |

**Equal exposure (primary): non-progressor landmarks weighted by the share of the 200 E7 truncation draws that keep them.**

| Horizon | Positive (patients) / negative landmarks | No-seq tier sens / spec | Mean-logit single sens / spec | Δ sens, memory − single | Δ spec, memory − single | AUROC memory vs single (mean-logit) | Δ AUROC (mean-logit) | Final sens / spec | Fold-internal sens / spec | R49 sens / spec | Δ AUROC, memory + certificate − single gate | Grade + p53 sens / spec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1y | 10 (10 P) / 267 | 0.950 / 0.374 | 0.850 / 0.403 | +0.100 [0.000, 0.257] | −0.030 [−0.050, −0.011] | 0.762 vs 0.724 | +0.038 [−0.011, 0.104] | 0.900 / 0.550 | 0.830 / 0.589 | 0.920 / 0.365 | +0.047 [0.007, 0.092] | 0.800 / 0.660 |
| 3y | 38 (27 P) / 224 | 0.953 / 0.427 | 0.895 / 0.452 | +0.058 [0.012, 0.116] | −0.025 [−0.047, −0.005] | 0.804 vs 0.782 | +0.022 [−0.008, 0.057] | 0.853 / 0.612 | 0.782 / 0.646 | 0.963 / 0.425 | −0.003 [−0.022, 0.016] | 0.579 / 0.687 |
| 5y | 59 (32 P) / 187 | 0.937 / 0.492 | 0.892 / 0.515 | +0.046 [0.012, 0.086] | −0.023 [−0.048, 0.001] | 0.825 vs 0.805 | +0.020 [−0.002, 0.045] | 0.815 / 0.661 | 0.753 / 0.696 | 0.929 / 0.471 | +0.008 [−0.015, 0.030] | 0.508 / 0.705 |
| ever | 88 (32 P) / 200 | 0.924 / 0.591 | 0.882 / 0.620 | +0.042 [0.015, 0.071] | −0.029 [−0.059, 0.002] | 0.866 vs 0.847 | +0.020 [0.003, 0.036] | 0.793 / 0.791 | 0.730 / 0.812 | 0.907 / 0.563 | +0.028 [0.010, 0.047] | 0.420 / 0.677 |

**Patient-weighted (secondary): each patient's landmarks share weight 1.**

| Horizon | Positive (patients) / negative landmarks | No-seq tier sens / spec | Mean-logit single sens / spec | Δ sens, memory − single | Δ spec, memory − single | AUROC memory vs single (mean-logit) | Δ AUROC (mean-logit) | Final sens / spec | Fold-internal sens / spec | R49 sens / spec | Δ AUROC, memory + certificate − single gate | Grade + p53 sens / spec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1y | 10 (10 P) / 267 | 0.954 / 0.406 | 0.895 / 0.431 | +0.059 [0.000, 0.134] | −0.025 [−0.049, −0.004] | 0.748 vs 0.731 | +0.017 [−0.008, 0.053] | 0.952 / 0.572 | 0.924 / 0.603 | 0.979 / 0.384 | +0.037 [0.005, 0.078] | 0.893 / 0.719 |
| 3y | 38 (27 P) / 224 | 0.947 / 0.482 | 0.908 / 0.501 | +0.039 [0.011, 0.075] | −0.019 [−0.045, 0.006] | 0.835 vs 0.822 | +0.013 [−0.002, 0.031] | 0.892 / 0.666 | 0.845 / 0.693 | 0.980 / 0.468 | +0.002 [−0.014, 0.019] | 0.559 / 0.757 |
| 5y | 59 (32 P) / 187 | 0.921 / 0.548 | 0.889 / 0.567 | +0.032 [0.011, 0.059] | −0.019 [−0.051, 0.011] | 0.854 vs 0.838 | +0.015 [0.001, 0.030] | 0.858 / 0.729 | 0.810 / 0.756 | 0.934 / 0.519 | +0.015 [−0.002, 0.033] | 0.516 / 0.790 |
| ever | 88 (32 P) / 200 | 0.920 / 0.616 | 0.886 / 0.646 | +0.034 [0.014, 0.058] | −0.030 [−0.068, 0.006] | 0.888 vs 0.869 | +0.019 [0.004, 0.034] | 0.837 / 0.828 | 0.786 / 0.843 | 0.917 / 0.576 | +0.033 [0.018, 0.051] | 0.439 / 0.772 |

NPV at the landmark (event within 5 years; case–control mix of landmarks): no-sequencing tier 0.964 [0.933, 0.986], final 0.927 [0.864, 0.973], R49 0.958 [0.919, 0.985], grade + p53 0.830 [0.748, 0.899].

**Equal exposure at patient level (E7 test 1(a): each non-progressor truncated to its first m endoscopies, m drawn from the progressors' counts, 200 draws; frozen rules).**

| Rule | Caught | NP flagged (of 43) | Δ NP vs R49 | Δ caught vs R49 |
|---|---|---|---|---|
| No sequencing (mean-logit + memory) | 31.0 [29.8, 31.9] | 22.3 [17.2, 27.2] | −3.6 [−6.7, −0.6] | −0.1 [−1.2, 0.9] |
| Mean-logit, single endoscopy | 30.9 [29.4, 32.0] | 24.6 [19.9, 29.1] | −1.3 [−4.3, 1.7] | −0.2 [−1.5, 0.9] |
| Confirmatory (final rule, cn90 bar) | 30.5 [29.3, 31.5] | 14.6 [9.9, 19.5] | −11.3 [−14.7, −8.1] | −0.6 [−1.6, 0.2] |
| Confirmatory, fold-internal bar | 30.4 [29.1, 31.5] | 13.5 [9.1, 18.1] | −12.4 [−15.8, −9.2] | −0.7 [−1.8, 0.2] |
| Memory (gate score) | 30.7 [29.5, 31.6] | 19.8 [14.9, 24.7] | −6.1 [−8.3, −4.0] | −0.4 [−1.3, 0.4] |
| Memory + certificate | 30.5 [29.3, 31.5] | 18.5 [13.6, 23.6] | −7.3 [−10.0, −4.9] | −0.6 [−1.6, 0.2] |
| Per-endoscopy gate R49 (this study) | 31.1 [29.7, 32.0] | 25.9 [21.3, 30.3] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| H&E alone (P1 90%) | 31.1 [29.5, 32.0] | 29.5 [24.9, 33.5] | +3.6 [0.9, 6.5] | 0.0 [−1.9, 1.5] |
| Grade IND/LGD or p53 aberrant | 21.0 [15.5, 26.4] | 20.6 [14.8, 26.4] | −5.2 [−11.7, 0.9] | −10.1 [−15.2, −5.1] |

Memory gain at equal exposure (memory minus the same base without memory): mean-logit −2.3 [−3.7, −1.0] NP (caught +0.1 [−0.2, 0.5]); gate score −3.0 [−5.2, −0.9]; gate + certificate −4.2 [−6.8, −1.9]. Without truncation the mean-logit memory gain is -4.4 (26.6 vs 31.0).

### 3. Two-consecutive-lows rule

De-escalation = the interval would be lengthened after that endoscopy. Four readings: (a) single look: low at this endoscopy; (b) two consecutive lows; (c) never flagged to date, single look (the 'never flagged' headline metric); (d) never flagged to date and two consecutive lows (the gastro review's recommendation: no de-escalation on one look, a flag returns the patient to guideline care). 'Progressors de-escalated at the last pre-event endoscopy' are progressors whose interval would have been lengthened at the look before the event.

| Rule | De-escalation reading | NP de-escalated at last endoscopy | NP ever de-escalated | Share of NP endoscopies followed by a longer interval | Progressors de-escalated at the last pre-event endoscopy | Same, integer range over repeats | Progressors ever de-escalated before the event |
|---|---|---|---|---|---|---|---|
| No sequencing (mean-logit + memory) | (a) single look | 28.0 [23.5, 32.5] | 36.5 [32.9, 39.5] | 0.59 | 2.1 [0.8, 3.9] | 1–4 | 6.0 [3.3, 9.2] |
| No sequencing (mean-logit + memory) | (b) two lows | 24.7 [19.7, 29.7] | 29.3 [24.6, 33.6] | 0.37 | 0.2 [0.0, 0.5] | 0–1 | 0.2 [0.0, 0.5] |
| No sequencing (mean-logit + memory) | (c) never flagged, single look | 16.4 [11.3, 21.7] | 26.6 [21.5, 31.4] | 0.42 | 1.0 [0.1, 2.2] | 0–2 | 4.0 [1.5, 6.9] |
| No sequencing (mean-logit + memory) | (d) never flagged, two lows | 16.4 [11.3, 21.7] | 20.4 [15.0, 25.9] | 0.29 | 0.1 [0.0, 0.3] | 0–1 | 0.1 [0.0, 0.3] |
| Confirmatory (final rule, cn90 bar) | (a) single look | 39.0 [36.4, 41.3] | 41.4 [39.9, 42.7] | 0.83 | 3.9 [1.2, 7.1] | 2–7 | 10.6 [6.3, 15.0] |
| Confirmatory (final rule, cn90 bar) | (b) two lows | 36.2 [32.2, 39.6] | 38.5 [35.1, 41.3] | 0.59 | 1.6 [0.4, 3.0] | 0–3 | 4.0 [1.3, 7.3] |
| Confirmatory (final rule, cn90 bar) | (c) never flagged, single look | 25.8 [20.3, 30.9] | 31.6 [27.0, 35.9] | 0.63 | 1.5 [0.5, 2.7] | 0–3 | 6.0 [3.0, 9.5] |
| Confirmatory (final rule, cn90 bar) | (d) never flagged, two lows | 25.8 [20.3, 30.9] | 27.9 [22.8, 32.8] | 0.47 | 1.0 [0.2, 1.9] | 0–3 | 2.7 [0.8, 5.2] |
| Confirmatory, fold-internal bar | (a) single look | 39.4 [37.0, 41.6] | 41.9 [40.6, 43.0] | 0.84 | 5.8 [2.7, 9.3] | 3–10 | 13.5 [9.1, 18.1] |
| Confirmatory, fold-internal bar | (b) two lows | 36.4 [32.4, 39.8] | 38.8 [35.5, 41.5] | 0.60 | 2.1 [0.8, 3.6] | 0–4 | 4.9 [2.5, 7.5] |
| Confirmatory, fold-internal bar | (c) never flagged, single look | 26.6 [21.2, 31.6] | 32.8 [28.6, 36.7] | 0.66 | 1.6 [0.5, 2.9] | 0–3 | 7.6 [4.1, 11.6] |
| Confirmatory, fold-internal bar | (d) never flagged, two lows | 26.6 [21.2, 31.6] | 29.1 [24.2, 33.9] | 0.49 | 1.1 [0.2, 2.1] | 0–3 | 3.0 [1.3, 5.0] |
| Per-endoscopy gate R49 (this study) | (a) single look | 26.6 [22.0, 30.7] | 39.0 [36.5, 41.2] | 0.56 | 2.7 [0.7, 5.3] | 1–5 | 6.6 [3.4, 10.0] |
| Per-endoscopy gate R49 (this study) | (b) two lows | 17.1 [12.3, 22.0] | 24.2 [19.1, 28.9] | 0.27 | 0.3 [0.0, 0.8] | 0–2 | 0.3 [0.0, 0.8] |
| Per-endoscopy gate R49 (this study) | (c) never flagged, single look | 11.2 [6.8, 16.0] | 26.3 [21.1, 31.3] | 0.33 | 0.9 [0.0, 2.3] | 0–3 | 4.1 [1.7, 6.8] |
| Per-endoscopy gate R49 (this study) | (d) never flagged, two lows | 11.2 [6.8, 16.0] | 15.3 [10.3, 20.5] | 0.20 | 0.3 [0.0, 0.8] | 0–2 | 0.3 [0.0, 0.8] |
| Grade IND/LGD or p53 aberrant | (a) single look | 42.0 [39.5, 43.0] | 43.0 [43.0, 43.0] | 0.76 | 14.0 [8.0, 19.4] | 14–14 | 24.0 [19.0, 28.4] |
| Grade IND/LGD or p53 aberrant | (b) two lows | 38.0 [33.2, 41.9] | 39.0 [34.8, 42.1] | 0.48 | 7.0 [2.7, 11.9] | 7–7 | 13.0 [7.7, 18.4] |
| Grade IND/LGD or p53 aberrant | (c) never flagged, single look | 18.0 [12.0, 24.4] | 27.0 [20.9, 32.8] | 0.45 | 11.0 [5.6, 16.5] | 11–11 | 20.0 [14.5, 25.1] |
| Grade IND/LGD or p53 aberrant | (d) never flagged, two lows | 18.0 [12.0, 24.4] | 22.0 [15.8, 28.7] | 0.31 | 7.0 [2.7, 11.9] | 7–7 | 12.0 [6.9, 17.4] |

### 4. Safety block

Reference: 32 progressors; first event HGD 21, IMC 7, no HGD/IMC sample sequenced (event = final endoscopy) <5; focal HGD noted at the event endoscopy 7; 10 progressors have one pre-event endoscopy; median 1.5 years from the last pre-event endoscopy to the event. Stage: the event is the first HGD/IMC endoscopy on the sheet; the Barrett's database gives OAC as the first HGD-or-worse report for <5 progressors and as the later worst grade for 5 (round-7 lookup B2), and records no TNM stage. Row-level line lists stay on the cluster.

| Rule | Group | Expected count (integer range over repeats) | Distinct patients in any repeat | Patients in ≥ 5 of 10 repeats | Any IMC | Expected IMC | Expected focal HGD | Expected: 5-y interval from the last cleared endoscopy postpones detection past the event | Most postponed by a 5-y interval | Most have a single pre-event endoscopy | Median years, last cleared endoscopy → event |
|---|---|---|---|---|---|---|---|---|---|---|---|
| No sequencing (mean-logit + memory) | missed (never flagged) | 1.0 (0–2) | <5 | 0 | yes | <5 patients | 0 | <5 patients | yes | yes | <5 patients |
| No sequencing (mean-logit + memory) | cleared at last pre-event endoscopy | 2.1 (1–4) | 8 | <5 | yes | <5 patients | 0 | 1.7 | yes | no | 1.08 |
| Confirmatory (final rule, cn90 bar) | missed (never flagged) | 1.5 (0–3) | 7 | 0 | no | 0 | <5 patients | 1.1 | yes | no | 2.69 |
| Confirmatory (final rule, cn90 bar) | cleared at last pre-event endoscopy | 3.9 (2–7) | 9 | <5 | yes | <5 patients | <5 patients | 3.5 | yes | no | 1.48 |
| Confirmatory, fold-internal bar | missed (never flagged) | 1.6 (0–3) | 7 | 0 | no | 0 | <5 patients | 1.2 | yes | no | 2.69 |
| Confirmatory, fold-internal bar | cleared at last pre-event endoscopy | 5.8 (3–10) | 12 | 6 | yes | <5 patients | <5 patients | 5.4 | yes | no | 1.48 |
| Per-endoscopy gate R49 (this study) | missed (never flagged) | 0.9 (0–3) | <5 | <5 | no | 0 | 0 | <5 patients | no | yes | <5 patients |
| Per-endoscopy gate R49 (this study) | cleared at last pre-event endoscopy | 2.7 (1–5) | 6 | <5 | yes | <5 patients | <5 patients | 2.1 | yes | no | 3.09 |
| H&E alone (P1 90%) | missed (never flagged) | 0.9 (0–2) | <5 | <5 | yes | <5 patients | 0 | <5 patients | yes | yes | <5 patients |
| H&E alone (P1 90%) | cleared at last pre-event endoscopy | 2.2 (1–4) | 5 | <5 | yes | <5 patients | 0 | <5 patients | yes | no | 1.05 |
| Grade IND/LGD or p53 aberrant | missed (never flagged) | 11.0 (11–11) | 11 | 11 | yes | <5 patients | 0 | 10.0 | yes | no | 2.12 |
| Grade IND/LGD or p53 aberrant | cleared at last pre-event endoscopy | 14.0 (14–14) | 14 | 14 | yes | <5 patients | <5 patients | 13.0 | yes | no | 2.0 |

'5-y interval postpones detection past the event' = the event came less than 5 years after the last cleared endoscopy, so a 5-year interval would have put the next look after the event date (detection delayed by 5 − t years). Whether that delay would have passed beyond endoscopic cure cannot be judged from these records: most treated progressors had EMR or ablation at or after the event (round-7 lookup), but what a further 2–4 years would have done is not observed.

### 5. Lead time

| Window | P / NP with an endoscopy in it | Rule | Caught | NP flagged | Δ caught vs R49 | Δ NP vs R49 | Δ caught vs grade + p53 | Δ NP vs single-endoscopy counterpart |
|---|---|---|---|---|---|---|---|---|
| > 2 y (NP: all) | 24 / 43 | No sequencing (mean-logit + memory) | 23.5 [22.5, 24.0] | 26.6 [21.3, 31.7] | +0.3 [−0.2, 1.0] | −5.2 [−8.2, −2.4] | +9.5 [4.9, 14.2] | −4.4 [−7.0, −2.2] |
| > 2 y (NP: all) | 24 / 43 | Mean-logit, single endoscopy | 23.5 [22.5, 24.0] | 31.0 [25.9, 35.6] | +0.3 [−0.2, 0.9] | −0.8 [−3.8, 2.3] | +9.5 [4.9, 14.3] | — |
| > 2 y (NP: all) | 24 / 43 | Confirmatory (final rule, cn90 bar) | 22.7 [21.6, 23.7] | 17.2 [12.1, 22.7] | −0.5 [−1.5, 0.3] | −14.6 [−18.9, −10.3] | +8.7 [4.1, 13.5] | −14.6 [−18.9, −10.3] |
| > 2 y (NP: all) | 24 / 43 | Confirmatory, fold-internal bar | 22.6 [21.4, 23.7] | 16.4 [11.4, 21.8] | −0.6 [−1.7, 0.3] | −15.4 [−19.8, −11.1] | +8.6 [4.0, 13.4] | −15.4 [−19.8, −11.1] |
| > 2 y (NP: all) | 24 / 43 | Per-endoscopy gate R49 (this study) | 23.2 [21.8, 24.0] | 31.8 [27.0, 36.2] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | +9.2 [4.5, 14.0] | — |
| > 2 y (NP: all) | 24 / 43 | H&E alone (P1 90%) | 23.7 [23.2, 24.0] | 36.0 [31.4, 39.7] | +0.5 [−0.2, 1.5] | +4.2 [1.2, 7.4] | +9.7 [5.0, 14.4] | — |
| > 2 y (NP: all) | 24 / 43 | Grade IND/LGD or p53 aberrant | 14.0 [9.1, 18.9] | 25.0 [18.6, 31.0] | −9.2 [−14.0, −4.5] | −6.8 [−13.3, −0.5] | 0.0 [0.0, 0.0] | — |
| > 2 y (NP: > 2 y before last) | 24 / 42 | No sequencing (mean-logit + memory) | 23.5 [22.5, 24.0] | 24.0 [18.5, 29.4] | +0.3 [−0.2, 1.0] | −4.1 [−7.8, −0.8] | +9.5 [4.9, 14.2] | −3.3 [−5.6, −1.3] |
| > 2 y (NP: > 2 y before last) | 24 / 42 | Mean-logit, single endoscopy | 23.5 [22.5, 24.0] | 27.3 [21.8, 32.4] | +0.3 [−0.2, 0.9] | −0.8 [−4.5, 2.6] | +9.5 [4.9, 14.3] | — |
| > 2 y (NP: > 2 y before last) | 24 / 42 | Confirmatory (final rule, cn90 bar) | 22.7 [21.6, 23.7] | 14.2 [9.4, 19.2] | −0.5 [−1.5, 0.3] | −13.9 [−19.0, −9.2] | +8.7 [4.1, 13.5] | −13.9 [−19.0, −9.2] |
| > 2 y (NP: > 2 y before last) | 24 / 42 | Confirmatory, fold-internal bar | 22.6 [21.4, 23.7] | 12.9 [8.5, 17.7] | −0.6 [−1.7, 0.3] | −15.2 [−20.5, −10.4] | +8.6 [4.0, 13.4] | −15.2 [−20.5, −10.4] |
| > 2 y (NP: > 2 y before last) | 24 / 42 | Per-endoscopy gate R49 (this study) | 23.2 [21.8, 24.0] | 28.1 [22.6, 33.1] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | +9.2 [4.5, 14.0] | — |
| > 2 y (NP: > 2 y before last) | 24 / 42 | H&E alone (P1 90%) | 23.7 [23.2, 24.0] | 31.4 [26.1, 35.8] | +0.5 [−0.2, 1.5] | +3.3 [0.8, 5.9] | +9.7 [5.0, 14.4] | — |
| > 2 y (NP: > 2 y before last) | 24 / 42 | Grade IND/LGD or p53 aberrant | 14.0 [9.1, 18.9] | 22.0 [15.5, 28.0] | −9.2 [−14.0, −4.5] | −6.1 [−13.3, 0.8] | 0.0 [0.0, 0.0] | — |
| > 4 y (NP: all) | 20 / 43 | No sequencing (mean-logit + memory) | 18.4 [16.7, 19.8] | 26.6 [21.3, 31.7] | −0.3 [−1.3, 0.7] | −5.2 [−8.2, −2.4] | +12.4 [8.2, 16.4] | −4.4 [−7.0, −2.2] |
| > 4 y (NP: all) | 20 / 43 | Mean-logit, single endoscopy | 18.2 [16.4, 19.6] | 31.0 [25.9, 35.6] | −0.5 [−1.6, 0.6] | −0.8 [−3.8, 2.3] | +12.2 [7.9, 16.2] | — |
| > 4 y (NP: all) | 20 / 43 | Confirmatory (final rule, cn90 bar) | 17.7 [16.2, 19.1] | 17.2 [12.1, 22.7] | −1.0 [−2.0, 0.0] | −14.6 [−18.9, −10.3] | +11.7 [7.3, 15.9] | −14.6 [−18.9, −10.3] |
| > 4 y (NP: all) | 20 / 43 | Confirmatory, fold-internal bar | 16.7 [14.6, 18.5] | 16.4 [11.4, 21.8] | −2.0 [−3.6, −0.6] | −15.4 [−19.8, −11.1] | +10.7 [6.3, 14.8] | −15.4 [−19.8, −11.1] |
| > 4 y (NP: all) | 20 / 43 | Per-endoscopy gate R49 (this study) | 18.7 [17.2, 19.8] | 31.8 [27.0, 36.2] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | +12.7 [8.7, 16.6] | — |
| > 4 y (NP: all) | 20 / 43 | H&E alone (P1 90%) | 18.3 [16.0, 19.9] | 36.0 [31.4, 39.7] | −0.4 [−2.1, 1.1] | +4.2 [1.2, 7.4] | +12.3 [8.2, 16.2] | — |
| > 4 y (NP: all) | 20 / 43 | Grade IND/LGD or p53 aberrant | 6.0 [2.1, 10.0] | 25.0 [18.6, 31.0] | −12.7 [−16.6, −8.7] | −6.8 [−13.3, −0.5] | 0.0 [0.0, 0.0] | — |
| > 4 y (NP: > 4 y before last) | 20 / 33 | No sequencing (mean-logit + memory) | 18.4 [16.7, 19.8] | 18.7 [14.2, 23.2] | −0.3 [−1.3, 0.7] | −2.4 [−6.4, 1.1] | +12.4 [8.2, 16.4] | −2.1 [−4.4, −0.3] |
| > 4 y (NP: > 4 y before last) | 20 / 33 | Mean-logit, single endoscopy | 18.2 [16.4, 19.6] | 20.8 [16.3, 25.1] | −0.5 [−1.6, 0.6] | −0.3 [−4.2, 3.4] | +12.2 [7.9, 16.2] | — |
| > 4 y (NP: > 4 y before last) | 20 / 33 | Confirmatory (final rule, cn90 bar) | 17.7 [16.2, 19.1] | 12.0 [7.8, 16.6] | −1.0 [−2.0, 0.0] | −9.1 [−12.9, −5.6] | +11.7 [7.3, 15.9] | −9.1 [−12.9, −5.6] |
| > 4 y (NP: > 4 y before last) | 20 / 33 | Confirmatory, fold-internal bar | 16.7 [14.6, 18.5] | 10.9 [6.7, 15.4] | −2.0 [−3.6, −0.6] | −10.2 [−14.2, −6.5] | +10.7 [6.3, 14.8] | −10.2 [−14.2, −6.5] |
| > 4 y (NP: > 4 y before last) | 20 / 33 | Per-endoscopy gate R49 (this study) | 18.7 [17.2, 19.8] | 21.1 [16.4, 25.6] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | +12.7 [8.7, 16.6] | — |
| > 4 y (NP: > 4 y before last) | 20 / 33 | H&E alone (P1 90%) | 18.3 [16.0, 19.9] | 23.2 [18.6, 27.5] | −0.4 [−2.1, 1.1] | +2.1 [−0.9, 5.0] | +12.3 [8.2, 16.2] | — |
| > 4 y (NP: > 4 y before last) | 20 / 33 | Grade IND/LGD or p53 aberrant | 6.0 [2.1, 10.0] | 20.0 [14.3, 25.0] | −12.7 [−16.6, −8.7] | −1.1 [−8.1, 5.3] | 0.0 [0.0, 0.0] | — |

### 6. Clinical comparators

Sources: Prague M per endoscopy from the Barrett's database within ±60 days (4 of 288 endoscopies), else `Demographics_full` Maximal (256), else the patient's database median (13); missing 15 endoscopies (7 patients, all progressors: segment-length rows are biased by differential missingness). Smoking known for 20 of 32 progressors and 22 of 43 non-progressors (`Demographics_full`; the database's smoking code is undocumented and unused). Sex from the sample table; LGD from the sheet grade at the endoscopy. Parasa-style score = 9 × male + 5 × smoker + 1 per cm + 11 × LGD (Parasa et al., Gastroenterology 2018). Because Prague M is essentially one value per patient, memory cannot change it.

| Comparator | Caught | NP flagged | Δ caught vs no-seq tier | Δ NP vs no-seq tier | Δ caught vs grade + p53 | Δ NP vs grade + p53 |
|---|---|---|---|---|---|---|
| Prague M ≥ 3 cm | 19.0 [13.5, 24.5] | 35.0 [29.7, 39.8] | −12.0 [−17.6, −6.5] | +8.4 [1.3, 14.9] | −2.0 [−8.2, 4.3] | +10.0 [2.9, 17.8] |
| EW-mean Prague M ≥ 3 cm | 19.0 [13.5, 24.5] | 35.0 [29.7, 39.8] | −12.0 [−17.6, −6.5] | +8.4 [1.3, 14.9] | −2.0 [−8.2, 4.3] | +10.0 [2.9, 17.8] |
| Parasa > 10 | 25.0 [20.3, 29.4] | 34.0 [28.7, 39.1] | −6.0 [−10.7, −1.6] | +7.4 [0.0, 14.4] | +4.0 [−2.9, 11.0] | +9.0 [2.1, 16.1] |
| EW-mean Parasa > 10 | 25.0 [20.3, 29.4] | 34.0 [28.7, 39.1] | −6.0 [−10.7, −1.6] | +7.4 [0.0, 14.4] | +4.0 [−2.9, 11.0] | +9.0 [2.1, 16.1] |
| Parasa > 20 | 12.0 [6.6, 17.9] | 17.0 [11.0, 23.1] | −19.0 [−24.3, −13.4] | −9.6 [−16.9, −2.6] | −9.0 [−15.1, −2.7] | −8.0 [−14.3, −2.0] |
| EW-mean Parasa > 20 | 11.0 [5.5, 16.6] | 15.0 [9.3, 21.1] | −20.0 [−25.3, −14.4] | −11.6 [−18.9, −4.0] | −10.0 [−16.7, −3.3] | −10.0 [−16.7, −3.5] |
| Prague M, training threshold | 31.0 [28.8, 32.0] | 41.8 [40.3, 43.0] | 0.0 [−2.4, 1.9] | +15.2 [10.1, 20.5] | +10.0 [4.0, 15.6] | +16.8 [10.7, 23.3] |
| Prague M + memory, training threshold | 31.0 [28.8, 32.0] | 41.8 [40.3, 43.0] | 0.0 [−2.4, 1.9] | +15.2 [10.1, 20.5] | +10.0 [4.0, 15.6] | +16.8 [10.7, 23.3] |
| Parasa-style, training threshold | 30.2 [27.5, 32.0] | 41.9 [40.2, 42.9] | −0.8 [−3.7, 1.5] | +15.3 [9.7, 20.6] | +9.2 [3.1, 15.3] | +16.9 [11.0, 23.2] |
| Parasa-style + memory, training threshold | 30.2 [27.5, 32.0] | 41.7 [39.9, 42.9] | −0.8 [−3.7, 1.5] | +15.1 [9.5, 20.5] | +9.2 [3.1, 15.3] | +16.7 [10.9, 23.2] |

Evaluation-matched (OPTIMISTIC for the comparator: its threshold set on the evaluated patients, per repeat):

| Comparator | Tier | Tier caught / NP flagged | Comparator NP flagged at the tier's caught | Comparator caught at the tier's NP flagged |
|---|---|---|---|---|
| prague_single | No sequencing (mean-logit + memory) | 31.0 / 26.6 | 41.4 | 13.1 |
| prague_single | Confirmatory (final rule, cn90 bar) | 30.5 / 17.2 | 40.1 | 8.7 |
| prague_single | Confirmatory, fold-internal bar | 30.4 / 16.4 | 40.1 | 8.3 |
| prague_mem | No sequencing (mean-logit + memory) | 31.0 / 26.6 | 41.4 | 13.7 |
| prague_mem | Confirmatory (final rule, cn90 bar) | 30.5 / 17.2 | 40.1 | 9.0 |
| prague_mem | Confirmatory, fold-internal bar | 30.4 / 16.4 | 40.1 | 8.7 |
| parasa_single | No sequencing (mean-logit + memory) | 31.0 / 26.6 | 41.2 | 20.1 |
| parasa_single | Confirmatory (final rule, cn90 bar) | 30.5 / 17.2 | 39.2 | 12.9 |
| parasa_single | Confirmatory, fold-internal bar | 30.4 / 16.4 | 39.2 | 12.0 |
| parasa_mem | No sequencing (mean-logit + memory) | 31.0 / 26.6 | 41.1 | 21.6 |
| parasa_mem | Confirmatory (final rule, cn90 bar) | 30.5 / 17.2 | 39.2 | 12.2 |
| parasa_mem | Confirmatory, fold-internal bar | 30.4 / 16.4 | 39.2 | 11.6 |

### 7. Subgroups

| Subgroup | P / NP | Rule | Caught | NP flagged | Δ NP vs R49 | Δ NP vs grade + p53 |
|---|---|---|---|---|---|---|
| segment <3 cm | 6 / 8 | No sequencing (mean-logit + memory) | 5.9 [5.7, 6.0] | 4.5 [1.9, 7.0] | −0.3 [−1.6, 0.5] | +0.5 [−4.3, 5.4] |
| segment <3 cm | 6 / 8 | Confirmatory (final rule, cn90 bar) | 5.5 [4.8, 6.0] | 1.1 [0.0, 3.2] | −3.7 [−6.2, −1.3] | −2.9 [−6.9, 1.6] |
| segment <3 cm | 6 / 8 | Confirmatory, fold-internal bar | 5.4 [4.6, 6.0] | 1.2 [0.0, 3.2] | −3.6 [−6.0, −1.3] | −2.8 [−6.8, 1.7] |
| segment <3 cm | 6 / 8 | Per-endoscopy gate R49 (this study) | 6.0 [6.0, 6.0] | 4.8 [2.2, 7.4] | 0.0 [0.0, 0.0] | +0.8 [−3.6, 5.3] |
| segment <3 cm | 6 / 8 | Grade IND/LGD or p53 aberrant | 2.0 [0.0, 4.5] | 4.0 [1.0, 7.0] | −0.8 [−5.3, 3.6] | 0.0 [0.0, 0.0] |
| segment >=3 cm | 19 / 35 | No sequencing (mean-logit + memory) | 18.5 [17.6, 19.0] | 22.1 [17.7, 26.4] | −4.9 [−7.5, −2.2] | +1.1 [−4.5, 7.5] |
| segment >=3 cm | 19 / 35 | Confirmatory (final rule, cn90 bar) | 18.7 [18.2, 19.0] | 16.1 [11.5, 20.6] | −10.9 [−14.7, −7.4] | −4.9 [−11.0, 1.7] |
| segment >=3 cm | 19 / 35 | Confirmatory, fold-internal bar | 18.7 [18.2, 19.0] | 15.2 [10.7, 19.8] | −11.8 [−15.7, −8.1] | −5.8 [−11.8, 0.8] |
| segment >=3 cm | 19 / 35 | Per-endoscopy gate R49 (this study) | 19.0 [19.0, 19.0] | 27.0 [23.1, 30.6] | 0.0 [0.0, 0.0] | +6.0 [1.3, 11.2] |
| segment >=3 cm | 19 / 35 | Grade IND/LGD or p53 aberrant | 15.0 [11.2, 18.1] | 21.0 [15.2, 26.2] | −6.0 [−11.2, −1.3] | 0.0 [0.0, 0.0] |
| segment unknown | 7 / 0 | not estimable |  |  |  |  |
| age <65 at first endoscopy | 21 / 20 | No sequencing (mean-logit + memory) | 20.8 [20.5, 21.0] | 10.4 [7.1, 13.9] | −2.4 [−4.3, −0.7] | +1.4 [−3.9, 7.1] |
| age <65 at first endoscopy | 21 / 20 | Confirmatory (final rule, cn90 bar) | 20.2 [19.3, 20.9] | 4.9 [2.1, 8.0] | −7.9 [−10.9, −5.0] | −4.1 [−9.0, 1.3] |
| age <65 at first endoscopy | 21 / 20 | Confirmatory, fold-internal bar | 20.1 [19.1, 20.9] | 4.5 [1.9, 7.6] | −8.3 [−11.2, −5.4] | −4.5 [−9.4, 1.0] |
| age <65 at first endoscopy | 21 / 20 | Per-endoscopy gate R49 (this study) | 20.8 [20.3, 21.0] | 12.8 [9.2, 16.2] | 0.0 [0.0, 0.0] | +3.8 [−1.2, 9.3] |
| age <65 at first endoscopy | 21 / 20 | Grade IND/LGD or p53 aberrant | 15.0 [10.5, 18.9] | 9.0 [4.4, 13.1] | −3.8 [−9.3, 1.2] | 0.0 [0.0, 0.0] |
| age >=65 | 11 / 23 | No sequencing (mean-logit + memory) | 10.2 [9.0, 11.0] | 16.2 [12.3, 19.8] | −2.8 [−5.0, −0.6] | +0.2 [−4.8, 5.2] |
| age >=65 | 11 / 23 | Confirmatory (final rule, cn90 bar) | 10.3 [9.4, 11.0] | 12.3 [8.4, 16.1] | −6.7 [−9.9, −3.8] | −3.7 [−9.0, 1.8] |
| age >=65 | 11 / 23 | Confirmatory, fold-internal bar | 10.3 [9.4, 11.0] | 11.9 [8.1, 15.7] | −7.1 [−10.3, −4.0] | −4.1 [−9.3, 1.5] |
| age >=65 | 11 / 23 | Per-endoscopy gate R49 (this study) | 10.3 [9.0, 11.0] | 19.0 [15.9, 21.7] | 0.0 [0.0, 0.0] | +3.0 [−1.0, 7.1] |
| age >=65 | 11 / 23 | Grade IND/LGD or p53 aberrant | 6.0 [2.4, 9.3] | 16.0 [11.5, 20.1] | −3.0 [−7.1, 1.0] | 0.0 [0.0, 0.0] |
| male | 25 / 32 | No sequencing (mean-logit + memory) | 24.0 [22.8, 24.9] | 20.1 [15.5, 24.4] | −3.2 [−5.7, −0.9] | +1.1 [−5.1, 7.3] |
| male | 25 / 32 | Confirmatory (final rule, cn90 bar) | 23.7 [22.5, 24.6] | 10.6 [6.5, 15.0] | −12.7 [−16.8, −8.9] | −8.4 [−14.3, −2.6] |
| male | 25 / 32 | Confirmatory, fold-internal bar | 23.6 [22.4, 24.6] | 9.8 [5.9, 14.2] | −13.5 [−17.5, −9.6] | −9.2 [−15.0, −3.5] |
| male | 25 / 32 | Per-endoscopy gate R49 (this study) | 24.1 [22.7, 25.0] | 23.3 [19.0, 27.2] | 0.0 [0.0, 0.0] | +4.3 [−0.9, 9.9] |
| male | 25 / 32 | Grade IND/LGD or p53 aberrant | 15.0 [10.2, 19.8] | 19.0 [13.4, 24.2] | −4.3 [−9.9, 0.9] | 0.0 [0.0, 0.0] |
| female | 7 / 11 | No sequencing (mean-logit + memory) | 7.0 [7.0, 7.0] | 6.5 [3.8, 9.2] | −2.0 [−3.9, −0.6] | +0.5 [−3.9, 5.1] |
| female | 7 / 11 | Confirmatory (final rule, cn90 bar) | 6.8 [6.3, 7.0] | 6.6 [3.9, 9.3] | −1.9 [−3.5, −0.5] | +0.6 [−4.2, 5.3] |
| female | 7 / 11 | Confirmatory, fold-internal bar | 6.8 [6.3, 7.0] | 6.6 [3.9, 9.3] | −1.9 [−3.5, −0.5] | +0.6 [−4.2, 5.3] |
| female | 7 / 11 | Per-endoscopy gate R49 (this study) | 7.0 [7.0, 7.0] | 8.5 [6.2, 10.6] | 0.0 [0.0, 0.0] | +2.5 [−1.4, 6.6] |
| female | 7 / 11 | Grade IND/LGD or p53 aberrant | 6.0 [3.5, 7.0] | 6.0 [2.4, 9.4] | −2.5 [−6.6, 1.4] | 0.0 [0.0, 0.0] |
| mean samples per endoscopy <2 | 17 / 24 | No sequencing (mean-logit + memory) | 16.9 [16.7, 17.0] | 16.4 [12.4, 19.9] | −0.8 [−2.5, 0.7] | +3.4 [−2.5, 9.3] |
| mean samples per endoscopy <2 | 17 / 24 | Confirmatory (final rule, cn90 bar) | 16.0 [15.2, 16.8] | 9.0 [5.1, 13.1] | −8.2 [−11.6, −4.9] | −4.0 [−9.9, 2.2] |
| mean samples per endoscopy <2 | 17 / 24 | Confirmatory, fold-internal bar | 15.9 [14.9, 16.7] | 8.8 [4.9, 12.8] | −8.4 [−11.9, −5.1] | −4.2 [−10.2, 2.0] |
| mean samples per endoscopy <2 | 17 / 24 | Per-endoscopy gate R49 (this study) | 16.7 [16.2, 17.0] | 17.2 [13.2, 20.8] | 0.0 [0.0, 0.0] | +4.2 [−1.6, 10.2] |
| mean samples per endoscopy <2 | 17 / 24 | Grade IND/LGD or p53 aberrant | 11.0 [7.0, 14.9] | 13.0 [8.0, 17.5] | −4.2 [−10.2, 1.6] | 0.0 [0.0, 0.0] |
| mean samples per endoscopy >=2 | 15 / 19 | No sequencing (mean-logit + memory) | 14.1 [12.9, 15.0] | 10.2 [6.7, 13.5] | −4.4 [−6.5, −2.5] | −1.8 [−5.8, 2.6] |
| mean samples per endoscopy >=2 | 15 / 19 | Confirmatory (final rule, cn90 bar) | 14.5 [13.5, 15.0] | 8.2 [4.8, 11.4] | −6.4 [−9.6, −3.7] | −3.8 [−8.2, 0.5] |
| mean samples per endoscopy >=2 | 15 / 19 | Confirmatory, fold-internal bar | 14.5 [13.5, 15.0] | 7.6 [4.3, 10.7] | −7.0 [−10.3, −4.2] | −4.4 [−8.8, −0.2] |
| mean samples per endoscopy >=2 | 15 / 19 | Per-endoscopy gate R49 (this study) | 14.4 [12.9, 15.0] | 14.6 [11.7, 17.2] | 0.0 [0.0, 0.0] | +2.6 [−0.1, 5.8] |
| mean samples per endoscopy >=2 | 15 / 19 | Grade IND/LGD or p53 aberrant | 10.0 [6.2, 13.6] | 12.0 [7.6, 16.1] | −2.6 [−5.8, 0.1] | 0.0 [0.0, 0.0] |
| endoscopies with 1 sample | 21 / 31 | No sequencing (mean-logit + memory) | 20.3 / 21 | 18.9 / 31 | −0.6 [−2.8, 1.7] | — |
| endoscopies with 1 sample | 21 / 31 | Confirmatory (final rule, cn90 bar) | 18.7 / 21 | 10.5 / 31 | −9.0 [−13.0, −5.5] | — |
| endoscopies with 1 sample | 21 / 31 | Per-endoscopy gate R49 (this study) | 19.8 / 21 | 19.5 / 31 | 0.0 [0.0, 0.0] | — |
| endoscopies with 1 sample | 21 / 31 | Grade IND/LGD or p53 aberrant | 8.0 / 21 | 13.0 / 31 | −6.5 [−13.8, 0.7] | — |
| endoscopies with >=2 samples | 25 / 39 | No sequencing (mean-logit + memory) | 23.9 / 25 | 18.9 / 39 | −7.0 [−10.4, −3.8] | — |
| endoscopies with >=2 samples | 25 / 39 | Confirmatory (final rule, cn90 bar) | 22.3 / 25 | 11.8 / 39 | −14.1 [−18.0, −10.2] | — |
| endoscopies with >=2 samples | 25 / 39 | Per-endoscopy gate R49 (this study) | 24.3 / 25 | 25.9 / 39 | 0.0 [0.0, 0.0] | — |
| endoscopies with >=2 samples | 25 / 39 | Grade IND/LGD or p53 aberrant | 16.0 / 25 | 19.0 / 39 | −6.9 [−12.4, −2.1] | — |

patient-level subgroups: frozen held-out calls, bootstrap restricted to the subgroup's patients; segment = median Prague M over the patient's endoscopies (database at the endoscopy, else Demographics_full); endoscopy-level rows restrict the evaluated endoscopies (memory still from the full history). Segment and age cut-offs are the guideline split (3 cm) and 65 years; no subgroup test is powered.

### 8. The 4 of 34 R49 robustness rows that fail (round 7c)

Round 7c (`docs/paper_review_round7c_gate_robustness.md`) tests R49's endoscopy sensitivity against sequencing everything (B*-endo) with a −0.05 non-inferiority bound in 34 rows. 30 are within; none fails by a shift; four fail by width (the CI includes 0, the lower bound is below −0.05):

| Row | Population | Δ endoscopy sensitivity [95% CI] | Lower bound | Why |
|---|---|---|---|---|
| 7: ≥ 256 tissue tiles, endoscopy by its top-L-IMG sample | 146 endoscopies (49 P), 63 patients (25 P) | −0.024 [−0.072, +0.018] | −0.063 | half the endoscopies; larger biopsies, where H&E is weaker relative to copy number (the H&E advantage sits in small biopsies) |
| 7: ≥ 256 tissue tiles, all samples of the endoscopy in the stratum | 117 endoscopies (40 P), 54 patients (21 P) | −0.013 [−0.071, +0.031] | −0.060 | same stratum, even smaller |
| 15: between-repeat variance added (as R33) | all | −0.016 [−0.061, +0.029] | −0.054 | the interval is inflated by the spread of the 10 CV repeats; same point estimate as the primary row |
| 15: refit bootstrap (F3, 200 draws) | all, refitted per draw | −0.012 [−0.080, +0.054] | −0.072 | models refitted on each bootstrap population add fitting variance (10% of draws below −0.05) |

All four are width failures with point estimates between −0.012 and −0.024 (primary −0.016): no row shows R49 losing sensitivity; the intervals are too wide to rule out a 5-point loss in large biopsies or once fitting and repeat variance are counted.

### 9. Progressions per 1,000 patient-years in the de-escalated group (MODEL-BASED)

A case–control cohort cannot estimate absolute risk. Assumption: the rule's patient-level sensitivity (progressors flagged at ≥ 1 pre-event endoscopy) and specificity (non-progressors never flagged) transport to an NDBE population with annual progression incidence λ. Then progressions per 1,000 patient-years in the de-escalated (never-flagged) group = 1000 · λ(1 − sens) / (λ(1 − sens) + (1 − λ) spec). Bootstrap CIs cannot exceed the cohort's observed misses, so an exact (Clopper–Pearson) upper limit on the miss count (mean misses rounded up) is given. Bar (gastro review): ≤ 2 per 1,000 patient-years (short-segment NDBE, ~0.2%/yr).

| Rule | De-escalated per 1,000 patients | λ = 0.30%/yr: per 1,000 py [CI]; exact upper | λ = 0.45%/yr | λ = 0.60%/yr | Rate relative to no triage (λ = 0.45%) |
|---|---|---|---|---|---|
| No sequencing (mean-logit + memory) | 379.8 | 0.25 [0.03, 0.62]; exact ≤ 1.28 | 0.37 [0.04, 0.93]; exact ≤ 1.92 | 0.49 [0.05, 1.24]; exact ≤ 2.56 | 0.08 [0.01, 0.21] |
| Confirmatory (final rule, cn90 bar) | 597.5 | 0.23 [0.08, 0.44]; exact ≤ 1.04 | 0.35 [0.12, 0.66]; exact ≤ 1.56 | 0.47 [0.16, 0.89]; exact ≤ 2.09 | 0.08 [0.03, 0.15] |
| Confirmatory, fold-internal bar | 616.0 | 0.24 [0.08, 0.46]; exact ≤ 1.01 | 0.36 [0.12, 0.69]; exact ≤ 1.52 | 0.49 [0.16, 0.93]; exact ≤ 2.03 | 0.08 [0.03, 0.15] |
| Memory (gate score) | 449.3 | 0.27 [0.08, 0.57]; exact ≤ 1.39 | 0.41 [0.12, 0.86]; exact ≤ 2.08 | 0.54 [0.15, 1.15]; exact ≤ 2.77 | 0.09 [0.03, 0.19] |
| Memory + certificate | 498.0 | 0.28 [0.09, 0.54]; exact ≤ 1.25 | 0.42 [0.14, 0.81]; exact ≤ 1.88 | 0.57 [0.19, 1.08]; exact ≤ 2.50 | 0.09 [0.03, 0.18] |
| Mean-logit, single endoscopy | 278.0 | 0.37 [0.00, 0.99]; exact ≤ 2.24 | 0.56 [0.00, 1.49]; exact ≤ 3.36 | 0.74 [0.00, 1.99]; exact ≤ 4.48 | 0.12 [0.00, 0.33] |
| Per-endoscopy gate R49 (this study) | 259.4 | 0.33 [0.00, 0.96]; exact ≤ 1.87 | 0.49 [0.00, 1.45]; exact ≤ 2.80 | 0.65 [0.00, 1.93]; exact ≤ 3.74 | 0.11 [0.00, 0.32] |
| H&E alone (P1 90%) | 162.2 | 0.52 [0.00, 1.84]; exact ≤ 2.98 | 0.78 [0.00, 2.77]; exact ≤ 4.48 | 1.04 [0.00, 3.69]; exact ≤ 5.97 | 0.17 [0.00, 0.61] |
| Sequence everything (P3 90%) | 259.4 | 0.29 [0.00, 0.94]; exact ≤ 1.87 | 0.43 [0.00, 1.40]; exact ≤ 2.80 | 0.58 [0.00, 1.87]; exact ≤ 3.74 | 0.10 [0.00, 0.31] |
| Grade IND/LGD | 418.8 | 3.36 [1.87, 5.60]; exact ≤ 4.67 | 5.04 [2.81, 8.39]; exact ≤ 7.00 | 6.71 [3.75, 11.17]; exact ≤ 9.33 | 1.12 [0.62, 1.86] |
| Grade IND/LGD or p53 aberrant | 418.3 | 2.46 [1.19, 4.29]; exact ≤ 3.81 | 3.70 [1.79, 6.43]; exact ≤ 5.71 | 4.93 [2.39, 8.57]; exact ≤ 7.61 | 0.82 [0.40, 1.43] |
| Parasa > 10 | 209.3 | 3.13 [1.07, 8.10]; exact ≤ 5.72 | 4.70 [1.60, 12.12]; exact ≤ 8.56 | 6.27 [2.14, 16.12]; exact ≤ 11.40 | 1.04 [0.36, 2.69] |

Without triage the rate is 3.0, 4.5 and 6.0 per 1,000 patient-years.


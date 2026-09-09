# Gap review wave 4 — GPT-6 Astra (2026-09-09)

3 adversarial passes (statistics / missing computation / claim–evidence audit)
+ synthesis over the full dossier (claims register C1–C25, EXECUTION_PLAN,
all 53 results JSONs). Script: `scripts/openai_gapreview.py`; raw outputs in
`review/astra/` (gitignored, local + cluster). Actual cost: $1.93
(113k in / 16k out). 15 findings; triage below.

## Verified and already fixed (same day)

- **A2 — Holm monotonicity bug (CONFIRMED).** `task_closure_cpu.py` computed
  step-down Holm without the cumulative-max constraint: largest raw p 0.94517
  reported as p_holm 0.94517 instead of 1.0. Fixed in code +
  `results/closure_cpu.json` regenerated. **No significance call changes**
  (the only survivor, SWG p_holm=0.0096, is unaffected).
- **A7 — count conservation (CONFIRMED, benign).** `label_dist_train_eligible`
  in the jury summary actually counted train_eligible + adjudicated (6,945 vs
  6,867 — excess exactly the 78 adjudications). Export-key bug only:
  regenerated all label CSVs to scratch and `cmp`-verified byte-identical to
  canonical — **no training-set contamination**. Summary now reports both
  strict and usable-incl-adjudicated distributions. Remaining A7 subclaims
  (unsure label totals, audit-matrix orientation) still to be checked.

## Accepted — wording/framing fixes for the writing phase (no compute)

- **A3 — null ≠ equivalence.** Never write "closes the escape hatch" /
  "loses nothing"; write observed delta + CI + "no demonstrated improvement".
  PORPOISE CI permits +0.035; 2.38 CI permits a 0.028 loss. MDT is 77 vs 76
  correct on 78 development cases — one decision, not superiority.
- **A4 — WGD claim overreach.** Neither cohort measures true WGD; C9 becomes
  "predicted-WGD score associates inversely with progression (ERIN) and
  weakly negatively with CNV complexity (SWG)" — not "ranking inversion".
- **A5 — EoE wording.** "Classified as diagnosed/suspected by the LLM", not
  "found cases"; the 0/100 control result is on keyword-negative sampled
  controls without independent status.
- **A11 — Brier ≠ calibration.** Call C1's Brier delta a Brier improvement;
  add calibration intercept/slope analysis (already on the P2 strengthener
  list, cheap from saved OOF).

## Accepted — recomputation queue (all from saved artefacts)

- **A6 (the substantive one): patient-clustered uncertainty.** Our paired
  bootstraps resample slides/rows, not patients. Recompute headline CIs
  (2.38, 2.38b, grade AUC, SWG correlations) resampling whole patients;
  patient-aware permutation for the trajectory rho. CPU-hours.
- **A1 (labelled blocker): selection history for C1.** Reconstruct the
  timestamped arm-selection history from git (fully reconstructable — every
  promotion is a dated commit/amendment); pair with selection-aware
  permutation (rerun full arm-selection inside each permutation) so the SWG
  headline carries a selection-adjusted p. Partially overlaps the quantified
  winner's curse (+0.027), but the pre-registration-status point is fair.
- **A8:** pooled-vs-within-fold C-index check on survival cohorts. CPU.
- **A9:** power map recalibration — fair catch that baseline 0.926 + delta
  0.10 exceeds 1.0; redo on a bounded/realistic effect scale with MC error
  bars and a type-I check at zero effect. CPU.
- **A10:** SWG trajectory needs the current-CNV-persistence + elapsed-time
  baseline before "anticipates future CNV" survives. CPU.
- **A12:** visibility curves with prevalence-matched sampling (TP53 ~83% OAC
  vs ~46% STAD) + cohort-identity-only baseline. CPU/GPU-light.
- **A13:** pan-cancer jury — add confusion matrices, macro-F1,
  majority-class baseline, tier-mapping audit for BLCA, and replay the
  5-juror rule on saved ERIN votes vs the deployed 8. CPU (saved votes).
- **A14:** cross-cohort identity crosswalk (ERIN↔SWG via Barrett's DB) —
  audit patient/report overlap across every train/eval set incl.
  adjudication samples; document the VLM single-split exception. CPU.
- **A15:** repeated patient-level permutations through the FINAL OCCAMS
  pipelines (current controls cover ERIN + TCGA; OCCAMS has single-shuffle
  only). GPU-hours (the one non-trivial item).

## Assessment

No finding overturns a result; two were real bugs (both fixed, neither
changed a conclusion); the rest split into wording discipline for the
writing phase and a recomputation queue that is almost entirely
saved-artefact CPU work. The most consequential items are A6
(patient-clustered CIs — could widen headline intervals) and A1/A15
(selection-adjusted inference for the single surviving confirmatory claim).

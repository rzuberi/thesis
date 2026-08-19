# ERIN Ch3 analysis: pre-registered design (EXECUTION_PLAN 1.6)

Written 2026-08-19, before any ERIN model has been trained. Same discipline as
docs/occams_v2_decision_tree.md: criteria fixed before results exist.

## Cohort

ERIN imaged cases with report linkage (2,280 cases; 100% linkage verified in the
feasibility report). Labels: report-derived grade (pathladder barretts_ladder,
post-audit patterns) and, for the progression endpoint, the feasibility cohort's
`progressed_to_HGDplus` with follow-up time. Patients overlapping SWGCohort
(n=6) are excluded from every experiment.

## Endpoints (fixed)

- **Primary: current-biopsy grade classification** — NDBE vs {LGD, HGD, CANCER}
  (IND excluded from the primary contrast; reported separately). Chosen as primary
  because every imaged case contributes, giving the largest test of the
  histology+clinical pairing.
- **Secondary: future progression** — non-dysplastic/LGD index cases with >=2
  timepoints, progressed_to_HGDplus as event. Smaller n, closer to SWGCohort's
  question; reported with the same machinery, powered or not.

## Arms (fixed)

1. Histology only: ABMIL over UNI2 tile features.
2. Clinical only: report-derived structured variables (age, surveillance interval,
   prior-grade history, cancer-pathway flag) — no image.
3. Late fusion of 1+2 (z-scored OOF combination).
4. Early fusion (concatenation) as the taxonomy's contrast arm.

## Protocol and criteria (inherited from Ch1)

Patient-disjoint 5-fold CV, folds frozen before comparison; 3 seeds; shuffled-label
controls per arm. Primary metric AUROC (grade), Harrell's C (progression).
"Signal": lower 95% bootstrap CI above 0.55. "Fusion benefit": paired
fusion-minus-histology delta CI excluding zero. Calibration (Brier) and
surveillance-framed net benefit reported alongside.

## Pre-registered interpretations

- Fusion benefit on primary -> Ch3's claim replicates externally at 16x scale.
- Signal without fusion benefit -> report as informative negative; Ch3's positive
  claim rests on SWGCohort, and the discussion addresses why report-derived
  clinical adds nothing over histology (probable label leakage: grade is itself
  report-derived — this is the known circularity risk, mitigated by using only
  PRIOR-timepoint clinical variables in arm 2; any deviation is reported).
- No signal in histology at n≈2,280 -> pipeline bug until proven otherwise
  (SWGCohort and published Barrett's models say this task is learnable).

## Not allowed post hoc

New arms, endpoint swaps, threshold moves, or quietly dropping the progression
endpoint if it disappoints. Deviations are reported as deviations.

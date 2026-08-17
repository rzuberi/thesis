# OCCAMS v2: pre-registered interpretation

Written 2026-08-15, before the v2 results have been read (the job ran or will run
during the cluster maintenance window; its output was unread at the time of
writing). Purpose: fix the interpretation criteria before seeing the numbers, so
Chapter 2's treatment of the OCCAMS arm is decided by rules set in advance.

## The analysis being interpreted

OCCAMS H&E + genomics fusion for overall survival, n≈141 patients with both
modalities. Design changes from the failed first pass (2026-08-14, AUC deltas null
or negative): ABMIL aggregation instead of mean pooling, a censoring-aware endpoint
(Harrell's C on out-of-fold risk instead of a 2-year binary cut with unmodelled
censoring), and clinical-only and stage-only reference arms alongside the
histology/genomics/fusion arms.

## Pre-registered criteria

"Signal" for an arm means the lower bound of its bootstrap 95% CI for
out-of-fold C-index is above 0.55. "Fusion benefit" means the paired
fusion-minus-best-unimodal delta CI excludes zero. Both computed under the Ch1
protocol (patient-disjoint folds, inner-only selection, 2,000 bootstrap resamples).

## Outcomes and their consequences

**A. Fusion benefit present.** The OCCAMS arm stands as designed. Chapter 2 claims
the H&E+genomics pairing helps for survival in established OAC, and the TCGA arm
(n=78 complete labels, now built) attempts replication of the same contrast.

**B. Unimodal signal, no fusion benefit.** The OCCAMS arm is reported as a
negative fusion result with working inputs — the most informative negative
available, because it rules out the excuse that the inputs were broken. Chapter 2's
positive fusion claim then rests on SWGCohort (progression) and on TCGA if it
independently shows a fusion benefit. The discussion addresses the likely cause:
six coarse genomic features carry little prognostic information at this sample
size, consistent with genomics-only performance.

**C. No signal in any arm (including clinical-only).** The cohort, at this size
and with these labels, does not support survival modelling; no fusion conclusion
of either sign can be drawn from it. The OCCAMS arm moves to a short negative
section, Chapter 2 becomes SWGCohort (primary) plus TCGA (replication), and the
weeks-survival label quality in the OCCAMS export becomes an explicit data-quality
finding — clinical-only baselines from May 2026 suggested stage should predict
survival, so a null there points at the labels, not the models.

**D. Signal but implausible (e.g. shuffled-label control away from 0.5, or
clinical-only far above published stage-based benchmarks).** Pipeline bug until
proven otherwise. Fix, rerun, reinterpret under the same rules.

## What is not allowed after the results are read

Adding new model arms because the pre-registered ones disappointed; moving the
0.55 threshold; swapping the primary metric; or reporting the first-pass binary
endpoint as if it were the planned analysis. Any of these, if ever justified,
must be reported as a post-hoc deviation in the thesis text.

# Multiplicity correction plan (EXECUTION_PLAN 1.18)

Written 2026-08-25 in response to the converged review finding (severity 4):
many paired contrasts are reported, none corrected, and the SWG family-winner
selection carries winner's-curse exposure.

## Status honesty (added 2026-08-25 after wave-2 review)

This plan was written AFTER the results existed. It is a reporting discipline —
one honest headline per chapter, everything else labelled exploratory — not a
pre-registration, and it must never be cited as if it were one. The only truly
pre-registered contrasts are those in the original pre-reg documents.

## Principle

One confirmatory contrast per chapter, declared here; everything else is
exploratory and labelled as such. Correction applies within the confirmatory
set only — correcting exploratory analyses would launder them into
confirmatory ones.

## Confirmatory set (4 contrasts, Holm-corrected as one family)

1. **Ch2 / SWG:** late-mean fusion vs histology-only (UNI2 + ABMIL), paired
   bootstrap ΔAUC. Released CI [0.015, 0.071]; Holm-adjusted significance to be
   recomputed from the bootstrap sign probabilities.
2. **Ch2 / OCCAMS:** fusion vs histology-only C-index delta under the v3
   pre-registered decision tree (Outcome C: null — stands as reported).
3. **Ch3 / ERIN:** histology + report-derived clinical vs histology-only on
   progression (primary estimand post-reframe; grade classification is Ch4's).
4. **Ch4 / ERIN:** jury-label-trained vs pathladder-trained model on the
   human-truth evaluation sample (blocked on R.4 pathologist grades).

Method: Holm-Bonferroni over the four bootstrap sign probabilities (two-sided),
alpha 0.05. Each chapter reports its raw CI plus the Holm-adjusted verdict.

## Winner's-curse handling (SWG)

The seven-family comparison is reported as a league table with the
pre-registered primary (late-mean vs CNV) and the hypothesis-named contrast
(late-mean vs histology) called out. The selection event — late-mean chosen as
best family on the same data used for the contrast — is disclosed wherever the
contrast is cited. No optimism correction is attempted at n=150; instead the
external arms (OCCAMS, TCGA, ERIN) are the check, and their nulls are part of
the thesis's central claim, not a caveat to it.

## Everything else

Encoder sweeps, pooling/heterogeneity splits, attention-shift metrics,
necessity probes, sensitivity analyses: exploratory, uncorrected, reported with
CIs and labelled "exploratory" in table captions. Their role is mechanism and
robustness, not hypothesis confirmation.

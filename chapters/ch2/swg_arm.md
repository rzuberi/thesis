# Chapter 2, SWGCohort arm: histology + copy number for Barrett's progression

Draft. Numbers marked [TO FILL] live in the final-release tables on the cluster
(`reports/thesis_ch1/` in the barretts_training tree) and should be transcribed,
not recomputed.

## Cohort and endpoint

The cohort is 150 Barrett's oesophagus surveillance patients contributing 707
matched biopsy samples (693 unique shallow-WGS copy-number profiles) with paired
H&E slides. The endpoint is progression to LGD2+ at the next biopsy: high-grade
dysplasia, intramucosal carcinoma, or adenocarcinoma, or two consecutive
low-grade-dysplasia calls — the composite that UK surveillance guidance treats as
the intervention trigger. This is prediction of a future state, not recognition of
the current one: samples taken at or after the qualifying event are excluded
before any split is made, so a model can only score biopsies that preceded the
diagnosis it is asked to anticipate.

## Models

Seven model families run under the Chapter 1 protocol on identical frozen
patient-disjoint folds. The copy-number baseline follows the published sWGS
approach for this cohort: imputation, scaling, 64-component PCA, random forest.
Alongside the families below, a co-attention fusion variant was evaluated and is
reported with the others.
The histology model is attention-based multiple-instance learning (ABMIL) over
UNI2-h tile features. Early fusion concatenates the modalities before a single
classifier; intermediate fusion merges learned representations; late fusion
combines the two unimodal out-of-fold probabilities, by averaging or by a
logistic stacker fitted on inner folds. Late-fusion results are reported for
three histology encoders (UNI2-h, Virchow2, GigaPath) as an encoder-sensitivity
check.

## Results

Late-mean fusion is the best family: AUPRC 0.630, ROC AUC 0.774, Brier 0.184,
against 0.538 / 0.663 / 0.216 for copy number alone. The paired bootstrap puts
the late-mean advantage over copy number at +0.111 AUC (95% CI 0.002 to 0.219)
and −0.032 Brier (−0.062 to −0.004); the AUPRC difference, +0.091, has an
interval crossing zero (−0.036 to 0.219). The discrimination and calibration
gains are therefore individually supported, and the AUPRC gain is directionally
consistent but not resolved at n=150 — the claim this chapter makes is a likely
multimodal benefit, not a definitive one, and the external arms exist to test it.

Histology alone (ABMIL over UNI2) reaches AUPRC 0.557, ROC AUC 0.731, Brier
0.245 — both unimodal arms rank below every fusion family on AUPRC (histology 4th
and copy number 6th of seven families). The histology-anchored contrast (late-mean
fusion minus histology-only) — the delta the thesis hypothesis names — is
supported on all three metrics by the released paired bootstrap
(`lgd2_final_pre_event_paired_differences.csv`, 150 patients, 5,000 resamples):
+0.073 AUPRC (95% CI 0.006 to 0.125), +0.043 AUC (0.015 to 0.071), −0.061 Brier
(−0.095 to −0.027). None of the three intervals crosses zero, making this the
strongest fusion contrast in the release — stronger than the copy-number-anchored
one above, whose AUPRC interval crosses zero. Two caveats bound the claim. First,
late-mean was selected as the best of seven families on this same data, so the
contrast carries winner's-curse exposure; it is reported alongside the
pre-registered fusion-vs-CNV primary, not in place of it. Second, in the encoder
sensitivity check GigaPath histology-alone is the best unimodal arm by point
estimate (AUPRC 0.609 vs UNI2's 0.557), and against it the fusion advantage
narrows: the paired bootstrap (`latemean_vs_gigapath_paired.json`, same
methodology, reproduction-gated) gives ΔAUPRC +0.020 (95% CI −0.064 to 0.104)
and ΔAUC +0.041 (−0.020 to 0.103), both crossing zero, with only the
calibration gain surviving (ΔBrier −0.048, CI −0.085 to −0.011). The honest
statement is therefore encoder-conditional: fusion beats histology-only
decisively under the pre-registered primary encoder, but against the strongest
swept encoder the discrimination advantage is directionally consistent and
unresolved at n=150, and only calibration is decisively better.

Early fusion (AUPRC 0.590, AUC 0.738) and intermediate fusion (0.567, 0.741)
did not overtake late-mean fusion on AUPRC, and neither did a co-attention
variant (0.548, 0.739) — consistent with the small-cohort expectation set out in
the Chapter 1 taxonomy. The shuffled-label controls sat at chance for all
families. One provenance note: an earlier, less strict evaluation round (155
patients, before the pre-event hardening) produced substantially higher absolute
numbers across all families; only the strict pre-event release reported here is
citable, and the earlier table is retained solely as an illustration of how much
evaluation leakage inflates this task.

## Interpretation available

Attention maps exist for eight selected cases (true positives, false negatives,
and one copy-number-rescue case where histology missed and CNV caught the
progressor), regenerated from the final fold checkpoints [TO CHECK: regeneration
from final checkpoints was listed as pending in PROJECT_STATE]. Per-fold
copy-number feature importances are exported and aggregated, and the
window-to-gene annotation map exists in the release
(`data/lgd2_cnv_feature_gene_annotation.csv`, 633 features): the top-ranked
importance regions annotate to canonical oesophageal drivers — chr20p
(CDC25B, FOXA2), chr11q (CCND1, ATM, FGF3/4/19), chr7p (EGFR), and chr17p
(TP53) — so regional importance is reportable in gene terms.

## Limitations

Single cohort, 150 patients, internal cross-validation only — external validation
for this endpoint is structurally unavailable (Chapter 1, replication ceiling),
which is why the chapter's other arms change cohort and endpoint rather than
re-testing this one. The AUPRC interval crossing zero is reported as such
wherever this result is cited.

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

Six model families run under the Chapter 1 protocol on identical frozen
patient-disjoint folds. The copy-number baseline follows the published sWGS
approach for this cohort: imputation, scaling, 64-component PCA, random forest.
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

Histology alone reaches [TO FILL: ABMIL-only AUPRC/AUC/Brier], placing the
unimodal arms [TO FILL: ordering]. The histology-anchored contrast (fusion minus
histology-only) is [TO FILL: delta and CI] — this is the delta the thesis
hypothesis names, and the copy-number-anchored contrast above is its complement.

Early and intermediate fusion [TO FILL: their metrics] did not overtake late
fusion, consistent with the small-cohort expectation set out in the Chapter 1
taxonomy. The shuffled-label controls sat at chance for all families.

## Interpretation available

Attention maps exist for eight selected cases (true positives, false negatives,
and one copy-number-rescue case where histology missed and CNV caught the
progressor), regenerated from the final fold checkpoints [TO CHECK: regeneration
from final checkpoints was listed as pending in PROJECT_STATE]. Per-fold
copy-number feature importances are exported and aggregated; the window-to-gene
annotation map is still to be built, so regional importance is currently reported
in genomic coordinates rather than gene names.

## Limitations

Single cohort, 150 patients, internal cross-validation only — external validation
for this endpoint is structurally unavailable (Chapter 1, replication ceiling),
which is why the chapter's other arms change cohort and endpoint rather than
re-testing this one. The AUPRC interval crossing zero is reported as such
wherever this result is cited.

# Evaluation protocol

Draft for Ch1. Defined once here; Chapters 2–4 inherit it unchanged. Deviations,
where a dataset forces one, are stated in the chapter that makes them.

**Unit of analysis.** All primary metrics are computed at patient level. Slide- and
sample-level results appear only as supplementary tables. Where a patient
contributes multiple samples, predictions are aggregated before scoring, and the
aggregation rule is fixed before the final run.

**Cross-validation.** Five-fold cross-validation with patient-disjoint folds:
no patient appears in both the training and evaluation side of any split. Folds are
frozen before model comparison begins and shared by every model in a chapter, so
paired comparisons see identical evaluation rows. Model selection — hyperparameters,
operating thresholds, calibration, epoch choice — uses inner validation splits only.
Out-of-fold predictions therefore reflect a model that never saw the evaluated
patient at any stage.

**Comparisons.** The question in every chapter is whether fusion beats the
histology-only baseline, so the primary statistic is the paired difference in
discrimination between fusion and histology-only, estimated on out-of-fold
predictions with a patient-level bootstrap (2,000 resamples, 95% percentile
interval). An improvement is claimed only when the interval excludes zero.
Secondary comparisons against the second modality alone establish that fusion
inputs carry independent signal.

**Metrics.** Discrimination: ROC AUC, and AUPRC where the positive class is rare
(Barrett's progression). Survival endpoints use Harrell's concordance index with
censoring handled by the estimator, never by discarding censored patients.
Calibration: Brier score and calibration curves. Clinical utility: decision-curve
net benefit at pre-declared threshold ranges. A model that improves AUC but
degrades calibration is reported as exactly that.

**Controls and negatives.** Every prediction task is accompanied by a
shuffled-label control run through the identical pipeline; a control AUC away from
0.5 invalidates the pipeline, not the hypothesis. Negative results are retained and
reported with the same detail as positive ones — including when later work
complicates them. The genotype-visibility question is the worked example: the
first OCCAMS probe found TP53 and whole-genome doubling not predictable from H&E
(AUC 0.48 and 0.41 at n=141), but a larger pooled analysis (n=446, adding TCGA
gastric/GEJ cases) reached AUC 0.703 and 0.771 for the same targets. The
reversal was resolved by a matched-n learning curve across population strata
(2026-08-26): oesophageal adenocarcinoma stays at chance at every tested n in
two independent cohorts, while the gastric/GEJ stratum shows real signal that
grows with n — the pooled "visibility" was a population effect, not a
sample-size effect. Chapter 2 therefore reports genotype visibility as
population-specific: absent in OAC (a clean two-cohort negative), present in
gastric/GEJ; the first-pass OCCAMS fusion null with its pre-registered
interpretation is described there.

**Reproducibility.** Splits, seeds, and model configurations are versioned
artefacts. Each final run writes an out-of-fold contract (row count, patient count,
fold assignment) that later analyses assert against, so a metric can never silently
be computed on different rows than its comparator.

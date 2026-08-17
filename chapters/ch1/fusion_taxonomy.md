# Fusion taxonomy

Draft for Ch1. Terms used throughout the thesis for how a second modality joins a
histology model. The taxonomy matters because "multimodal helps" is only a useful
claim if it says which integration point helped.

Histology enters every model the same way: tile-level features from a pathology
foundation model (UNI2-h, 1,536 dimensions; Virchow2 in sensitivity analyses),
aggregated to a patient representation either by mean pooling or by attention-based
multiple-instance learning (ABMIL). The second modality — copy-number features,
clinical variables, or report-derived labels — joins at one of three points:

**Late fusion.** Each modality trains its own predictor; their out-of-fold
probabilities are combined, either by averaging or by a logistic stacker fitted on
inner folds. Nothing about either representation changes. This is the weakest form
of integration and the strongest baseline: it cannot exploit interactions between
modalities, but it also cannot be destabilised by them, and it tolerates missing
modalities at prediction time.

**Early fusion.** The modalities are concatenated into one feature vector before a
single predictor is trained. Interactions are available in principle, but a
low-dimensional modality can drown next to a 1,536-dimensional histology embedding,
and regularisation choices decide whether that happens. The first-pass OCCAMS
result — early fusion scoring below histology alone — is the canonical failure mode.

**Intermediate fusion.** Modality-specific encoders learn representations that are
merged inside the network and trained end to end against the target. The most
expressive option and the hungriest for data; at the cohort sizes in this thesis
(141–2,446 patients) it competes with late fusion only when the histology encoder
stays frozen.

Chapter 2's SWGCohort analysis instantiates all three under the shared protocol
(six model families: CNV-only, histology ABMIL, early, intermediate, late-mean,
late-stacked), and late-mean fusion won. The other chapters test whether that
ordering is a property of the pairing or of the dataset.

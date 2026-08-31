
## HisToSpatialCNV (Garmire lab, Nat BME 2026) — added 2026-08-31, from Rehan
https://www.nature.com/articles/s41551-026-01754-z
Spot-level CNV (amp/del/neutral) from H&E; labels = inferCNV from spatial
transcriptomics; CellProfiler+GNN+MHSA architecture.
Use in thesis:
- Ch2 Part A discussion: their WES-validated AUC 0.651 (vs 0.825 on
  transcriptomics-derived labels, partly circular) lands in our gastric/GEJ
  visibility range (0.64-0.74) — cite as independent support for "genome
  partially visible from H&E, modest and tissue-dependent". Contrast with our
  OAC-at-chance finding as population-dependence evidence.
- Ch5 transfer discussion: their cross-platform drop (0.825 -> 0.65-0.73)
  parallels our resection->biopsy inversion; cite as independent fragility
  evidence for morphology->genome predictors under domain shift.
- Encoder conditionality: CellProfiler ~= ResNet50 > UNI (0.785) in their
  ablations — published foundation-model-not-best instance beside our sweep.
NOT actionable as an experiment: requires spatial transcriptomics we lack.

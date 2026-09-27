# BE paper plan: slide→patient aggregation sensitivity (mean over rows vs max over rows)

**Status of this file: PRE-SPECIFICATION VERSION**, committed before the analysis was run. Report only; the max-over-rows
convention of all earlier documents is unchanged.

## 1. Header (completed at the results commit)
- Date: 27 September 2026. Commit at start: `e421783`. Pre-specification commit: the commit adding this text. Frozen release only; nothing retrained. Script `scripts/paper_plan/pa_aggregation.py`; renderer `pa_render.py`; output `results/paper_final/aggregation_sensitivity.json`.

## Pre-specification
- Row scores: release OOF probabilities for cnv_only, image_only, early_fusion, intermediate_fusion, late_mean, coattention_fusion, late_stack_logit; the F1 Killcoyne-method CNV rows (`feasibility/paper_plan/f1_cnv_km_oof.csv`); clinical C2 rows recomputed with the identical nested logistic of `pf_main.py` (grade + MaxPathologySoFar, release folds and inner folds; deterministic). Patient label = max of `y_progressor` over rows (unchanged); E-HGD label as in round 3.
- Aggregations: current = max over the patient's rows; alternative = mean over rows. Populations: discovery (82) and stratified all-150 (pair-weighted within-stratum AUROC). Endpoints: LGD2+ and E-HGD. Per arm, population and endpoint: AUROC for max and for mean, paired difference mean − max with CI (patient bootstrap 2,000 `RandomState(0)`; within-stratum resampling for the stratified population).
- K3 probes with max aggregation: (i) patient representation = element-wise max over the patient's row embeddings (instead of the mean), same probe procedure (standardisation and C on training-fold patients, release inner folds), evaluated on discovery held-out patients and on all held-out patients; (ii) row-level probe fitted on training-fold rows, patient score = max over rows of the row probe. Paired difference vs the mean-representation probe of K3 with CI.

(Results follow in the results commit.)

# BE paper plan: slide→patient aggregation sensitivity (mean over rows vs max over rows)

## 1. Header
- Date: 27 September 2026. Commit at start: `e421783`. Pre-specification commit: `d1958ea` (verbatim in §5). Results commit: `b5a6f35`; this text is the next commit. Frozen release only; nothing retrained. Report only: the max-over-rows convention is unchanged.
- Check that the recomputed max-over-rows scores equal the round-3 patient table (max |difference| per arm): {'cnv_only': 0.0, 'image_only': 0.0, 'early_fusion': 0.0, 'intermediate_fusion': 0.0, 'late_mean': 0.0, 'coattention_fusion': 0.0, 'late_stack_logit': 0.0, 'cnv_km': 0.0, 'C2_grade_maxsofar': 0.0}.

## 2. Status table
| item | status | key number |
|---|---|---|
| A1 Arms, mean vs max, discovery LGD2+ | DONE | late fusion max 0.691 vs mean 0.818, Δ +0.127 [0.046, 0.213]; WSI Δ +0.110 [0.038, 0.186] |
| A2 Arms, mean vs max, stratified LGD2+ | DONE | late fusion Δ +0.095 [0.028, 0.166]; CNV(RF) Δ +0.132 [0.055, 0.215] |
| A3 Arms, E-HGD (both populations) | DONE | late fusion discovery Δ +0.018 [-0.062, +0.094] |
| A4 K3 probes with max aggregation | DONE | image: mean-repr 0.783, max-repr 0.770, row-probe max 0.643 (discovery) |

## 3. Items

### A1–A3. Arms under mean-over-rows aggregation
**Question.** Does the slide→patient aggregation rule change the AUROCs?

**Status.** DONE. **Pre-specification.** `d1958ea`.

**discovery, LGD2+** (n 82, events 40)

| arm | AUROC max (convention) | AUROC mean | Δ mean − max [CI] |
|---|---|---|---|
| Clinical (C2) | 0.625 | 0.680 | +0.055 [0.015, 0.100] |
| CNV (release RF) | 0.564 | 0.746 | +0.183 [0.086, 0.288] |
| CNV (Killcoyne method) | 0.580 | 0.664 | +0.083 [0.028, 0.145] |
| WSI | 0.649 | 0.759 | +0.110 [0.038, 0.186] |
| Early fusion | 0.704 | 0.777 | +0.073 [0.015, 0.137] |
| Intermediate fusion | 0.684 | 0.807 | +0.123 [0.050, 0.199] |
| Late fusion (mean) | 0.691 | 0.818 | +0.127 [0.046, 0.213] |
| Co-attention (suppl.) | 0.625 | 0.749 | +0.124 [0.043, 0.205] |
| Late stack (suppl.) | 0.647 | 0.767 | +0.120 [0.040, 0.199] |

**discovery, E-HGD (post hoc)** (n 82, events 26)

| arm | AUROC max (convention) | AUROC mean | Δ mean − max [CI] |
|---|---|---|---|
| Clinical (C2) | 0.412 | 0.424 | +0.013 [-0.033, +0.056] |
| CNV (release RF) | 0.639 | 0.677 | +0.038 [-0.058, +0.138] |
| CNV (Killcoyne method) | 0.698 | 0.718 | +0.020 [-0.028, +0.070] |
| WSI | 0.658 | 0.681 | +0.023 [-0.053, +0.092] |
| Early fusion | 0.751 | 0.751 | +0.000 [-0.065, +0.063] |
| Intermediate fusion | 0.687 | 0.727 | +0.040 [-0.038, +0.115] |
| Late fusion (mean) | 0.701 | 0.718 | +0.018 [-0.062, +0.094] |
| Co-attention (suppl.) | 0.683 | 0.712 | +0.029 [-0.065, +0.115] |
| Late stack (suppl.) | 0.664 | 0.694 | +0.030 [-0.049, +0.107] |

**stratified, LGD2+** (n 150, events 50)

| arm | AUROC max (convention) | AUROC mean | Δ mean − max [CI] |
|---|---|---|---|
| Clinical (C2) | 0.601 | 0.637 | +0.036 [0.002, 0.074] |
| CNV (release RF) | 0.594 | 0.727 | +0.132 [0.055, 0.215] |
| CNV (Killcoyne method) | 0.597 | 0.665 | +0.067 [0.019, 0.116] |
| WSI | 0.708 | 0.788 | +0.080 [0.022, 0.143] |
| Early fusion | 0.735 | 0.805 | +0.069 [0.023, 0.119] |
| Intermediate fusion | 0.717 | 0.821 | +0.104 [0.046, 0.167] |
| Late fusion (mean) | 0.745 | 0.839 | +0.095 [0.028, 0.166] |
| Co-attention (suppl.) | 0.695 | 0.788 | +0.093 [0.029, 0.157] |
| Late stack (suppl.) | 0.701 | 0.791 | +0.090 [0.025, 0.155] |

**stratified, E-HGD (post hoc)** (n 150, events 36)

| arm | AUROC max (convention) | AUROC mean | Δ mean − max [CI] |
|---|---|---|---|
| Clinical (C2) | 0.446 | 0.449 | +0.003 [-0.032, +0.037] |
| CNV (release RF) | 0.651 | 0.675 | +0.024 [-0.053, +0.099] |
| CNV (Killcoyne method) | 0.684 | 0.704 | +0.020 [-0.023, +0.062] |
| WSI | 0.721 | 0.736 | +0.015 [-0.044, +0.068] |
| Early fusion | 0.773 | 0.789 | +0.017 [-0.033, +0.065] |
| Intermediate fusion | 0.723 | 0.766 | +0.043 [-0.018, +0.100] |
| Late fusion (mean) | 0.757 | 0.771 | +0.013 [-0.049, +0.073] |
| Co-attention (suppl.) | 0.744 | 0.765 | +0.022 [-0.048, +0.086] |
| Late stack (suppl.) | 0.719 | 0.741 | +0.022 [-0.041, +0.080] |

**Method.** Row scores as released (C2 rows recomputed deterministically); patient score = max or mean over rows; label = max; bootstrap over patients (within stratum for the stratified population). **Sources.** `results/paper_final/aggregation_sensitivity.json` · `scripts/paper_plan/pa_aggregation.py` · commit b5a6f35 (`arms`). **Caveats.** Patients with one row (26 of 150) are identical under both rules; the stratified AUROC weights discovery pairs 1,680 : 580.

### A4. K3 probes with max aggregation
**Status.** DONE. **Pre-specification.** `d1958ea`.

| representation | population | n / events | probe on mean embedding (K3) | probe on element-wise max embedding | Δ [CI] | row probe, max over rows | Δ [CI] |
|---|---|---|---|---|---|---|---|
| image_only | discovery | 82 / 40 | 0.783 | 0.770 | -0.014 [-0.095, +0.071] | 0.643 | -0.140 [-0.232, -0.032] |
| image_only | all_150 | 150 / 50 | 0.784 | 0.800 | +0.016 [-0.037, +0.075] | 0.719 | -0.065 [-0.137, +0.003] |
| cnv_only | discovery | 82 / 40 | 0.680 | 0.587 | -0.094 [-0.212, +0.018] | 0.495 | -0.186 [-0.338, -0.024] |
| cnv_only | all_150 | 150 / 50 | 0.713 | 0.662 | -0.051 [-0.152, +0.056] | 0.608 | -0.105 [-0.210, +0.005] |
| early_fusion | discovery | 82 / 40 | 0.799 | 0.826 | +0.027 [-0.039, +0.096] | 0.690 | -0.108 [-0.211, -0.009] |
| early_fusion | all_150 | 150 / 50 | 0.822 | 0.832 | +0.010 [-0.040, +0.060] | 0.762 | -0.060 [-0.128, +0.011] |
| intermediate_fusion | discovery | 82 / 40 | 0.807 | 0.781 | -0.026 [-0.093, +0.038] | 0.659 | -0.148 [-0.240, -0.056] |
| intermediate_fusion | all_150 | 150 / 50 | 0.819 | 0.798 | -0.021 [-0.069, +0.025] | 0.741 | -0.078 [-0.140, -0.019] |
| coattention_fusion | discovery | 82 / 40 | 0.719 | 0.707 | -0.012 [-0.074, +0.054] | 0.639 | -0.080 [-0.195, +0.054] |
| coattention_fusion | all_150 | 150 / 50 | 0.736 | 0.756 | +0.020 [-0.026, +0.070] | 0.752 | +0.016 [-0.075, +0.107] |

**Sources.** `results/paper_final/aggregation_sensitivity.json` · `scripts/paper_plan/pa_aggregation.py` · commit b5a6f35 (`k3_probes`). **Caveats.** The row probe is trained on rows (several per patient) with patient-keyed inner folds; the element-wise max representation changes the feature distribution, not only the aggregation.

## 4. Discrepancies found
None affecting earlier documents; the max-over-rows scores reproduce the round-3 table exactly (max |difference| in §1).

## 5. Pre-specification text as committed at `d1958ea` (verbatim)

> # BE paper plan: slide→patient aggregation sensitivity (mean over rows vs max over rows)
>
> **Status of this file: PRE-SPECIFICATION VERSION**, committed before the analysis was run. Report only; the max-over-rows
> convention of all earlier documents is unchanged.
>
> ## 1. Header (completed at the results commit)
> - Date: 27 September 2026. Commit at start: `e421783`. Pre-specification commit: the commit adding this text. Frozen release only; nothing retrained. Script `scripts/paper_plan/pa_aggregation.py`; renderer `pa_render.py`; output `results/paper_final/aggregation_sensitivity.json`.
>
> ## Pre-specification
> - Row scores: release OOF probabilities for cnv_only, image_only, early_fusion, intermediate_fusion, late_mean, coattention_fusion, late_stack_logit; the F1 Killcoyne-method CNV rows (`feasibility/paper_plan/f1_cnv_km_oof.csv`); clinical C2 rows recomputed with the identical nested logistic of `pf_main.py` (grade + MaxPathologySoFar, release folds and inner folds; deterministic). Patient label = max of `y_progressor` over rows (unchanged); E-HGD label as in round 3.
> - Aggregations: current = max over the patient's rows; alternative = mean over rows. Populations: discovery (82) and stratified all-150 (pair-weighted within-stratum AUROC). Endpoints: LGD2+ and E-HGD. Per arm, population and endpoint: AUROC for max and for mean, paired difference mean − max with CI (patient bootstrap 2,000 `RandomState(0)`; within-stratum resampling for the stratified population).
> - K3 probes with max aggregation: (i) patient representation = element-wise max over the patient's row embeddings (instead of the mean), same probe procedure (standardisation and C on training-fold patients, release inner folds), evaluated on discovery held-out patients and on all held-out patients; (ii) row-level probe fitted on training-fold rows, patient score = max over rows of the row probe. Paired difference vs the mean-representation probe of K3 with CI.
>
> (Results follow in the results commit.)
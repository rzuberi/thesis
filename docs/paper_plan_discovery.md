# BE paper plan: discovery-stratum analysis (82 Killcoyne-discovery patients)

## 1. Header
- Date: 26 September 2026. Commit at start: `c93ca01`. Pre-specification commit: `30b2317` (verbatim in §5). Results commit: `c66d1bc`; this text is the next commit. Frozen release only. Script `scripts/paper_plan/pd_discovery.py`; result `results/paper_plan/discovery_main.json`.
- Cohort: the 82 discovery-stratum patients; LGD2+ 40 events; E-HGD 26 events. Patient scores as computed in earlier rounds (max over rows, fold-honest); nothing refitted except the discovery-refit operating thresholds in the FP analysis.

## 2. Status table
| item | status | key number |
|---|---|---|
| D1 Arms within discovery, LGD2+ | DONE | WSI 0.649 [0.527, 0.765]; late fusion 0.691; CNV(RF) 0.564; C2 0.625 |
| D2 Arms within discovery, E-HGD | DONE | WSI 0.658; late fusion 0.701; CNV(RF) 0.639; CNV(KM) 0.698 |
| D3 Paired differences and selection-adjusted p | DONE | LGD2+: late − WSI +0.042 [0.001, 0.083], selection-adjusted p 0.3898; WSI − CNV(RF) +0.086 [-0.084, +0.266] |
| D4 FP analysis within discovery non-progressors | DONE | 42 non-progressors, 6 with later HGD+; late fusion (pooled thresholds) FP/TN 22/20, later HGD+ [3, 22] vs [3, 20], Fisher p 1.0 |

## 3. Items

### D1. LGD2+ endpoint within discovery
**Question.** How do the arms perform when progressors and non-progressors come from the same design stratum?

**Status.** DONE. **Pre-specification.** `30b2317`.

n 82, events 40.

| arm | AUROC [CI] | AUPRC [CI] |
|---|---|---|
| Clinical C1 | 0.615 [0.490, 0.737] | 0.584 [0.448, 0.746] |
| Clinical C2 (primary) | 0.625 [0.498, 0.744] | 0.583 [0.441, 0.752] |
| Clinical C3 | 0.591 [0.468, 0.711] | 0.575 [0.429, 0.739] |
| Clinical C4 (=3a) | 0.720 [0.593, 0.827] | 0.709 [0.556, 0.844] |
| CNV (release RF) | 0.564 [0.427, 0.693] | 0.614 [0.471, 0.757] |
| CNV (Killcoyne method) | 0.580 [0.443, 0.714] | 0.675 [0.530, 0.804] |
| WSI | 0.649 [0.527, 0.765] | 0.645 [0.510, 0.809] |
| Early fusion | 0.704 [0.579, 0.812] | 0.715 [0.576, 0.845] |
| Intermediate fusion | 0.684 [0.567, 0.798] | 0.688 [0.547, 0.826] |
| Late fusion (image + RF CNV) | 0.691 [0.569, 0.803] | 0.703 [0.564, 0.835] |
| Late fusion (image + KM CNV) | 0.676 [0.551, 0.788] | 0.711 [0.578, 0.828] |
| Co-attention (extra) | 0.625 [0.505, 0.743] | 0.643 [0.504, 0.789] |
| Late stack (extra) | 0.647 [0.524, 0.763] | 0.632 [0.492, 0.786] |
| C2 + WSI | 0.704 [0.592, 0.812] | 0.699 [0.552, 0.840] |
| C2 + CNV(RF) | 0.698 [0.581, 0.805] | 0.713 [0.571, 0.842] |
| C2 + CNV(KM) | 0.735 [0.617, 0.842] | 0.750 [0.596, 0.879] |
| C2 + late fusion | 0.729 [0.617, 0.833] | 0.719 [0.575, 0.851] |
| C2 + WSI + CNV(RF) | 0.749 [0.637, 0.848] | 0.734 [0.590, 0.865] |

**Paired differences** (one-sided permutation p that the first arm is higher):

| difference | Δ AUROC [CI] | perm p | selection-adjusted p (max over 5 fusion arms, fusion − WSI only) |
|---|---|---|---|
| image_only − cnv_only | +0.086 [-0.084, +0.266] | 0.1564 |  |
| image_only − cnv_km | +0.069 [-0.097, +0.245] | 0.2144 |  |
| late_mean − cnv_only | +0.127 [-0.021, +0.284] | 0.045 |  |
| late_mean_km − cnv_km | +0.095 [-0.042, +0.236] | 0.0755 |  |
| C2+image − C2_grade_maxsofar | +0.079 [-0.003, +0.165] | 0.0365 |  |
| C2+cnv_only − C2_grade_maxsofar | +0.073 [-0.031, +0.171] | 0.086 |  |
| C2+cnv_km − C2_grade_maxsofar | +0.110 [0.007, 0.207] | 0.0155 |  |
| C2+late_mean − C2_grade_maxsofar | +0.104 [0.019, 0.194] | 0.0105 |  |
| C2+image+cnv_only − C2_grade_maxsofar | +0.124 [0.020, 0.233] | 0.013 |  |
| early_fusion − image_only | +0.054 [-0.048, +0.148] | 0.1549 | 0.3003 |
| intermediate_fusion − image_only | +0.035 [-0.059, +0.126] | 0.2289 | 0.4558 |
| late_mean − image_only | +0.042 [0.001, 0.083] | 0.027 | 0.3898 |
| coattention_fusion − image_only | -0.024 [-0.149, +0.103] | 0.6537 | 0.974 |
| late_stack_logit − image_only | -0.002 [-0.054, +0.052] | 0.5397 | 0.8521 |

**Method.** Patient bootstrap (2,000, seed 0) over the 82; label permutations (2,000, seed 0). **Sources.** `results/paper_plan/discovery_main.json` · `scripts/paper_plan/pd_discovery.py` · commit c66d1bc (`endpoints.LGD2plus`). **Caveats.** The discovery stratum is a matched case–control design with our LGD2+ label disagreeing with the sheet status for 11 patients; E-HGD has 26 events.

### D2. E-HGD endpoint within discovery
**Question.** How do the arms perform when progressors and non-progressors come from the same design stratum?

**Status.** DONE. **Pre-specification.** `30b2317`.

n 82, events 26.

| arm | AUROC [CI] | AUPRC [CI] |
|---|---|---|
| Clinical C1 | 0.410 [0.282, 0.547] | 0.273 [0.189, 0.410] |
| Clinical C2 (primary) | 0.412 [0.277, 0.545] | 0.283 [0.191, 0.427] |
| Clinical C3 | 0.370 [0.239, 0.502] | 0.261 [0.180, 0.391] |
| Clinical C4 (=3a) | 0.617 [0.476, 0.746] | 0.459 [0.305, 0.660] |
| CNV (release RF) | 0.639 [0.491, 0.779] | 0.573 [0.399, 0.739] |
| CNV (Killcoyne method) | 0.698 [0.556, 0.830] | 0.609 [0.415, 0.785] |
| WSI | 0.658 [0.527, 0.782] | 0.475 [0.320, 0.689] |
| Early fusion | 0.751 [0.618, 0.866] | 0.644 [0.474, 0.814] |
| Intermediate fusion | 0.687 [0.560, 0.806] | 0.583 [0.411, 0.752] |
| Late fusion (image + RF CNV) | 0.701 [0.573, 0.821] | 0.595 [0.409, 0.764] |
| Late fusion (image + KM CNV) | 0.705 [0.573, 0.823] | 0.613 [0.440, 0.771] |
| Co-attention (extra) | 0.683 [0.557, 0.806] | 0.568 [0.392, 0.746] |
| Late stack (extra) | 0.664 [0.536, 0.789] | 0.519 [0.356, 0.701] |
| C2 + WSI | 0.501 [0.366, 0.638] | 0.315 [0.219, 0.485] |
| C2 + CNV(RF) | 0.505 [0.368, 0.642] | 0.330 [0.225, 0.512] |
| C2 + CNV(KM) | 0.598 [0.449, 0.747] | 0.447 [0.294, 0.664] |
| C2 + late fusion | 0.523 [0.390, 0.658] | 0.327 [0.228, 0.502] |
| C2 + WSI + CNV(RF) | 0.578 [0.444, 0.712] | 0.370 [0.252, 0.572] |

**Paired differences** (one-sided permutation p that the first arm is higher):

| difference | Δ AUROC [CI] | perm p | selection-adjusted p (max over 5 fusion arms, fusion − WSI only) |
|---|---|---|---|
| image_only − cnv_only | +0.019 [-0.151, +0.203] | 0.4203 |  |
| image_only − cnv_km | -0.041 [-0.211, +0.144] | 0.6702 |  |
| late_mean − cnv_only | +0.062 [-0.088, +0.225] | 0.2264 |  |
| late_mean_km − cnv_km | +0.007 [-0.129, +0.147] | 0.4643 |  |
| C2+image − C2_grade_maxsofar | +0.089 [-0.001, +0.180] | 0.0295 |  |
| C2+cnv_only − C2_grade_maxsofar | +0.094 [-0.025, +0.205] | 0.05 |  |
| C2+cnv_km − C2_grade_maxsofar | +0.186 [0.054, 0.318] | 0.001 |  |
| C2+late_mean − C2_grade_maxsofar | +0.111 [0.018, 0.204] | 0.0105 |  |
| C2+image+cnv_only − C2_grade_maxsofar | +0.166 [0.043, 0.282] | 0.005 |  |
| early_fusion − image_only | +0.093 [0.001, 0.181] | 0.0465 | 0.1339 |
| intermediate_fusion − image_only | +0.029 [-0.058, +0.115] | 0.2859 | 0.5322 |
| late_mean − image_only | +0.043 [-0.003, +0.091] | 0.034 | 0.4063 |
| coattention_fusion − image_only | +0.025 [-0.090, +0.147] | 0.3478 | 0.5742 |
| late_stack_logit − image_only | +0.006 [-0.047, +0.064] | 0.4093 | 0.7546 |

**Method.** Patient bootstrap (2,000, seed 0) over the 82; label permutations (2,000, seed 0). **Sources.** `results/paper_plan/discovery_main.json` · `scripts/paper_plan/pd_discovery.py` · commit c66d1bc (`endpoints.E_HGD`). **Caveats.** The discovery stratum is a matched case–control design with our LGD2+ label disagreeing with the sheet status for 11 patients; E-HGD has 26 events.

### D3. Paired differences and selection adjustment
**Status.** DONE. Reported inside D1 and D2 (both endpoints). **Sources.** `results/paper_plan/discovery_main.json` · `scripts/paper_plan/pd_discovery.py` · commit c66d1bc (`endpoints.*.differences`).

### D4. False positives within discovery non-progressors
**Question.** Does the FP excess of later disease hold when only discovery non-progressors are compared?

**Status.** DONE. **Pre-specification.** `30b2317`. 42 discovery non-progressors; later HGD+ in 6, later LGD+ in 8.

| model | thresholds | FP / TN | later HGD+ FP vs TN [k/n] | OR FP adjusted for baseline and max grade [CI], p | later LGD+ FP vs TN | OR adjusted |
|---|---|---|---|---|---|---|
| Late fusion (image + RF CNV) | pooled thresholds | 22 / 20 | [3, 22] vs [3, 20], Fisher p 1.0 | 0.981 [0.160, 6.007], p 0.983 | [3, 22] vs [5, 20], Fisher p 0.445 | 0.564 [0.107, 2.970], p 0.499 |
| Late fusion (image + RF CNV) | discovery refit thresholds | 26 / 16 | [4, 26] vs [2, 16], Fisher p 1.0 | 1.459 [0.214, 9.958], p 0.7 | [4, 26] vs [4, 16], Fisher p 0.454 | 0.658 [0.126, 3.441], p 0.62 |
| WSI | pooled thresholds | 25 / 17 | [3, 25] vs [3, 17], Fisher p 0.672 | 0.675 [0.104, 4.367], p 0.68 | [3, 25] vs [5, 17], Fisher p 0.235 | 0.375 [0.067, 2.087], p 0.263 |
| WSI | discovery refit thresholds | 27 / 15 | [4, 27] vs [2, 15], Fisher p 1.0 | 1.255 [0.186, 8.463], p 0.816 | [4, 27] vs [4, 15], Fisher p 0.425 | 0.552 [0.106, 2.864], p 0.48 |
| CNV (release RF) | pooled thresholds | 35 / 7 | [6, 35] vs [0, 7], Fisher p 0.567 | 48712554397.327 [0.000, inf], p 1.0 (near-separation: CI unreliable) | [8, 35] vs [0, 7], Fisher p 0.312 | 57899449504.306 [0.000, inf], p 1.0 |
| CNV (release RF) | discovery refit thresholds | 32 / 10 | [5, 32] vs [1, 10], Fisher p 1.0 | 1.628 [0.163, 16.213], p 0.678 | [7, 32] vs [1, 10], Fisher p 0.655 | 2.434 [0.254, 23.362], p 0.441 |
| CNV (Killcoyne method) | pooled thresholds | 38 / 4 | [6, 38] vs [0, 4], Fisher p 1.0 | 26583668509.823 [0.000, inf], p 1.0 (near-separation: CI unreliable) | [8, 38] vs [0, 4], Fisher p 0.572 | 40931464761.616 [0.000, inf], p 1.0 |
| CNV (Killcoyne method) | discovery refit thresholds | 38 / 4 | [6, 38] vs [0, 4], Fisher p 1.0 | 26583668509.823 [0.000, inf], p 1.0 (near-separation: CI unreliable) | [8, 38] vs [0, 4], Fisher p 0.572 | 40931464761.616 [0.000, inf], p 1.0 |
| Clinical C2 (primary) | pooled thresholds | 30 / 12 | [4, 30] vs [2, 12], Fisher p 1.0 | 0.918 [0.097, 8.704], p 0.941 | [5, 30] vs [3, 12], Fisher p 0.668 | 1.005 [0.147, 6.868], p 0.996 |
| Clinical C2 (primary) | discovery refit thresholds | 30 / 12 | [4, 30] vs [2, 12], Fisher p 1.0 | 0.918 [0.097, 8.704], p 0.941 | [5, 30] vs [3, 12], Fisher p 0.668 | 1.005 [0.147, 6.868], p 0.996 |
| clinical_3a | pooled thresholds | 22 / 20 | [3, 22] vs [3, 20], Fisher p 1.0 | 1.128 [0.140, 9.073], p 0.91 | [4, 22] vs [4, 20], Fisher p 1.0 | 1.656 [0.272, 10.082], p 0.584 |
| clinical_3a | discovery refit thresholds | 22 / 20 | [3, 22] vs [3, 20], Fisher p 1.0 | 1.128 [0.140, 9.073], p 0.91 | [4, 22] vs [4, 20], Fisher p 1.0 | 1.656 [0.272, 10.082], p 0.584 |
| v4_exploratory | pooled thresholds | 17 / 25 | [4, 17] vs [2, 25], Fisher p 0.202 | 3.849 [0.600, 24.707], p 0.155 | [4, 17] vs [4, 25], Fisher p 0.694 | 1.853 [0.377, 9.122], p 0.448 |
| v4_exploratory | discovery refit thresholds | 17 / 25 | [4, 17] vs [2, 25], Fisher p 0.202 | 3.849 [0.600, 24.707], p 0.155 | [4, 17] vs [4, 25], Fisher p 0.694 | 1.853 [0.377, 9.122], p 0.448 |

**Method.** F5 model without a stratum term; two threshold versions as pre-specified. **Sources.** `results/paper_plan/discovery_main.json` · `scripts/paper_plan/pd_discovery.py` · commit c66d1bc (`fp_analysis_discovery_nonprogressors`). **Caveats.** 42 non-progressors and 6 later-HGD+ events: Wald CIs are wide and several fits are near separation.

## 4. Discrepancies found
1. Compare with the pooled figures in `docs/paper_plan_round3.md` R6: within discovery, WSI 0.649 (pooled 0.731), late fusion 0.691 (0.774), CNV(RF) 0.564 (0.663), C2 0.625 (0.681).

## 5. Pre-specification text as committed at `30b2317` (verbatim)

> # BE paper plan: discovery-stratum analysis (82 Killcoyne-discovery patients)
>
> **Status of this file: PRE-SPECIFICATION VERSION**, committed before the analysis was run.
>
> ## 1. Header (completed at the results commit)
> - Date: 26 September 2026. Commit at start: `c93ca01`. Pre-specification commit: the commit adding this text. Frozen release only. Inputs: patient-level arm scores, labels, E-HGD labels and strata from round 3 (`feasibility/paper_plan/round3_patient_table.csv`, commit `6976646`), operating-point predictions from the follow-up (`followup_patient_scores.csv`), later-disease table and closeout patient table.
> - Script: `scripts/paper_plan/pd_discovery.py`; renderer `pd_render.py`; output `results/paper_plan/discovery_main.json`.
>
> ## Pre-specification
> - Cohort: the 82 discovery-stratum patients (Killcoyne 777-sheet), 40 LGD2+ progressors, 26 HGD/IMC progressors. Endpoints: LGD2+ (release label) and E-HGD (HGD/IMC progressors = 1, second-LGD progressors = 0, as round 3 R2).
> - Arms: every arm in the round-3 R6 table (C1–C4, cnv_only, cnv_km, image_only, early, intermediate, late_mean, late_mean_km, co-attention, late-stack, C2 + WSI, C2 + CNV(RF), C2 + CNV(KM), C2 + late fusion, C2 + WSI + CNV(RF)); patient scores as already computed (max over rows; fold-honest; nothing refitted).
> - Per endpoint: AUROC and AUPRC with patient bootstrap CI (2,000, `RandomState(0)`, resamples of the 82). Paired differences with CI and one-sided permutation p (2,000 patient-label permutations, seed 0): WSI − cnv_only, WSI − cnv_km, each of the five fusion arms − WSI, late_mean − cnv_only, late_mean_km − cnv_km, each C2 + modality − C2. Selection-adjusted p for each fusion arm − WSI = P(max over the five fusion arms of the permuted difference ≥ observed).
> - FP analysis (F5 model, no stratum term) within the 42 discovery non-progressors: per model (late_mean, image_only, cnv_only, cnv_km, C2, clinical_3a, v4_exploratory), FP/TN at the primary operating point with two threshold versions: (a) the pooled thresholds already applied (follow-up predictions), (b) thresholds refitted on discovery training-fold patients (sensitivity ≥ 0.80 per fold); later HGD+ and later LGD+ counts, Fisher p, and logistic regression of the later outcome on FP + baseline grade + max grade so far (statsmodels Logit; if separation prevents a fit, report the Fisher result only).
>
> (Results follow in the results commit.)
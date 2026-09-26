# BE paper plan: discovery-stratum analysis (82 Killcoyne-discovery patients)

**Status of this file: PRE-SPECIFICATION VERSION**, committed before the analysis was run.

## 1. Header (completed at the results commit)
- Date: 26 September 2026. Commit at start: `c93ca01`. Pre-specification commit: the commit adding this text. Frozen release only. Inputs: patient-level arm scores, labels, E-HGD labels and strata from round 3 (`feasibility/paper_plan/round3_patient_table.csv`, commit `6976646`), operating-point predictions from the follow-up (`followup_patient_scores.csv`), later-disease table and closeout patient table.
- Script: `scripts/paper_plan/pd_discovery.py`; renderer `pd_render.py`; output `results/paper_plan/discovery_main.json`.

## Pre-specification
- Cohort: the 82 discovery-stratum patients (Killcoyne 777-sheet), 40 LGD2+ progressors, 26 HGD/IMC progressors. Endpoints: LGD2+ (release label) and E-HGD (HGD/IMC progressors = 1, second-LGD progressors = 0, as round 3 R2).
- Arms: every arm in the round-3 R6 table (C1–C4, cnv_only, cnv_km, image_only, early, intermediate, late_mean, late_mean_km, co-attention, late-stack, C2 + WSI, C2 + CNV(RF), C2 + CNV(KM), C2 + late fusion, C2 + WSI + CNV(RF)); patient scores as already computed (max over rows; fold-honest; nothing refitted).
- Per endpoint: AUROC and AUPRC with patient bootstrap CI (2,000, `RandomState(0)`, resamples of the 82). Paired differences with CI and one-sided permutation p (2,000 patient-label permutations, seed 0): WSI − cnv_only, WSI − cnv_km, each of the five fusion arms − WSI, late_mean − cnv_only, late_mean_km − cnv_km, each C2 + modality − C2. Selection-adjusted p for each fusion arm − WSI = P(max over the five fusion arms of the permuted difference ≥ observed).
- FP analysis (F5 model, no stratum term) within the 42 discovery non-progressors: per model (late_mean, image_only, cnv_only, cnv_km, C2, clinical_3a, v4_exploratory), FP/TN at the primary operating point with two threshold versions: (a) the pooled thresholds already applied (follow-up predictions), (b) thresholds refitted on discovery training-fold patients (sensitivity ≥ 0.80 per fold); later HGD+ and later LGD+ counts, Fisher p, and logistic regression of the later outcome on FP + baseline grade + max grade so far (statsmodels Logit; if separation prevents a fit, report the Fisher result only).

(Results follow in the results commit.)

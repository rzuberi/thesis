# BE paper plan, round 3: confounding checks before writing (R1–R6)

**Status of this file: PRE-SPECIFICATION VERSION**, committed before any analysis in it was run. Results are appended in a
later commit; the specification text is not edited afterwards.

## 1. Header (completed at the results commit)
- Date: 26 September 2026. Commit at start: `e7ee492`. Pre-specification commit: the commit adding this text. Inputs: frozen release only; patient-level scores and strata written by the follow-up (`feasibility/paper_plan/followup_patient_scores.csv`, `f2_strata.csv`, `f1_cnv_km_oof.csv`, `later_disease_patient.csv`, `f5_later_hgd_nonprogressors.csv`; commit `fef1089`), image embeddings from `pp_latent.py` (`feasibility/paper_plan/latent/`), closeout tables (`feasibility/closeout/`).
- Planned scripts: `scripts/paper_plan/pr3_main.py` (R1, R2 endpoints, R3, R4, R5, R6), `pr3_lopo.py` (R2 faithfulness retrain), `pr3_render.py`, `pr3_check_report.py`. Outputs `results/paper_plan/round3_main.json`, `round3_lopo.json`, figures `results/paper_plan/figs/km_v3/`.
- Conventions as before (patient = max over rows; rank AUROC; 2,000 patient bootstraps `RandomState(0)`; permutations 2,000; fold honesty with the release outer folds and patient-keyed inner folds). Strata: discovery = Killcoyne 777-sheet patients (82: 39 sheet cases + 43 sheet controls), validation = 268-sheet patients (68), as defined in the follow-up F2 (`f2_strata.csv`).

## Pre-specifications

### R1. Stratum as a shortcut
- Probes (discovery vs validation label) among the 100 non-progressors, fold-honest on the release outer folds (probe fitted on training-fold non-progressors, applied to held-out non-progressors; L2 logistic, C ∈ {0.01, 0.1, 1, 10} by the release inner folds restricted to the training patients; standardisation on training patients): (a) CNV features = patient mean of the release CNV matrix (632 features) → PCA to 20 components fitted on training patients then logistic (to avoid p ≫ n), and, as stated secondary, the 44 arm features + cx without PCA; (b) image patient embedding = patient mean of the image_only fold-model 256-d attention-pooled embedding (`emb_image_only_fold{k}.npy`, fold-k model for fold-k held-out patients); (c) CNV QC = patient means of MAPD noise, reads (missing → training median, plus a missing indicator), segments, fraction altered, cx. AUROC with patient bootstrap CI (2,000, seed 0).
- Stratified AUROC = (n_pairs_disc × AUROC_disc + n_pairs_val × AUROC_val) / (n_pairs_disc + n_pairs_val), pairs = progressors × non-progressors within stratum. For every arm in the follow-up table (C1–C4, cnv_only, cnv_km, image_only, early, intermediate, late_mean, late_mean_km, co-attention, late-stack) and the C2 + modality fold-z combinations. Paired differences WSI − cnv_only, WSI − cnv_km, late_mean − WSI, late_mean_km − WSI, C2+modality − C2. CIs from a stratified patient bootstrap (patients resampled within stratum, 2,000, seed 0).
- Stratum-adjusted incremental value: logistic regression of the patient label on stratum (two-level indicator), then stratum + logit of the arm's patient score (OOF); likelihood-ratio test (statsmodels, 1 df); ΔAUROC = AUROC(stratum + arm, in-sample fit) − AUROC(stratum alone) as the LR companion, and a fold-honest version (combination fitted on training-fold patients, applied held-out) reported alongside.

### R2. Endpoint sensitivity
- Progressor type from the release: HGD/IMC if any positive row's `NextBiopsyLabel` ≥ 3, else second-LGD. E-HGD: label 1 for HGD/IMC progressors, 0 for everyone else; E-HGD-excl: second-LGD-only progressors removed. Every arm: pooled and stratified AUROC (as R1), n, events, CI. No retraining.
- Faithfulness retrain (`pr3_lopo.py`): within the 82 discovery patients, label = sheet status (P/NP, patient level, mode over the patient's rows), elastic net as F1 (l1_ratio 0.9, standardisation and median imputation on the training rows), leave-one-patient-out; C ∈ {0.01, 0.1, 1, 10} chosen for each left-out patient by 5-fold patient-grouped CV on the remaining 81 (patient AUROC vs sheet status; folds from `GroupKFold` on patient id with a fixed patient order). Compare with the published LOPO probabilities on the matched rows: Spearman (rows), patient-level AUROC vs sheet status for ours and for the published values, and Spearman of ours vs our F1 arm.

### R3. Tissue amount as a shortcut
- `kept_tiles` (0.44 µm/px h5 `kept_tiles`, patient mean; also `tissue_frac`): AUROC as a score with the sign chosen on training folds (if training-fold AUROC < 0.5 use the negative), pooled and within each stratum, with CIs. Distributions (median, IQR) by stratum and by scanner model; Mann-Whitney discovery vs validation. Among non-progressors, Spearman of each arm's patient score with `kept_tiles`.
- Label ~ stratum + kept_tiles, then + arm logit: LR test and ΔAUROC (in-sample and fold-honest as R1).
- The 11 late_mean FN patients: their `kept_tiles` percentile within the progressor and within the non-progressor distributions of their own stratum.

### R4. Risk groups, valid version only
- Statement that version A in `docs/paper_plan_answers.md` item 5 (and the F4 version-A rows) is superseded by version B (biopsy-date censoring), recorded here (earlier docs are not edited). Version B KM, log-rank and Cox (high vs low, moderate vs low) restricted to the validation stratum for late_mean, cnv_only, cnv_km, C2, with the training-fold tertile groups of the follow-up; feasibility rule stated in advance: Cox reported only if each compared group has ≥ 3 events, otherwise KM and log-rank only. Pooled cohort: group rates with Wilson CI, OR high vs low (Haldane), and the Mantel–Haenszel OR across strata (primary: two strata discovery/validation; secondary: three strata case/control/validation) with its CI (statsmodels `StratifiedTable`).

### R5. False positives: stratum and follow-up
- F5 logistic (later HGD+ and later LGD+ on FP status + baseline grade + max grade so far) refitted with stratum (discovery indicator) and follow-up length (days from last release row to the last DB report, 0 if none) as covariates, per model (late_mean, image_only, cnv_only, cnv_km, C2, clinical_3a, v4_exploratory). FP/TN counts per stratum per model. Rerun of the FP table with the one flagged patient (`f5_later_hgd_nonprogressors.csv`, `hgd_report_is_the_next_release_biopsy` = True) moved to the progressors (removed from the non-progressor set; its effect on pooled AUROC of late_mean reported as a sensitivity).

### R6. Headline numbers under each view
- One table, rows = arms; columns = pooled AUROC [CI], stratified AUROC [CI] (R1), E-HGD pooled [CI], E-HGD stratified [CI], ΔAUROC over stratum + tiles fold-honest [CI] (R3), with n and events per column.

(Results follow in the results commit.)

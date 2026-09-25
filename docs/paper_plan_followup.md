# BE paper plan follow-up (F1–F9)

**Status of this file: PRE-SPECIFICATION VERSION**, committed before any analysis in it was run. Results are appended in
later commits; the specification text below is not edited afterwards (changes, if any, are added beside it with both results).

## 1. Header (completed at the results commit)
- Date: 25–26 September 2026. Commit at start: `38a83f2`. Pre-specification commit: the commit adding this text. Inputs: frozen release `chapter1_lgd2_final_pre_event_20260713_final` only; `docs/paper_plan_answers.md` and `results/paper_plan/*` (commit `98ed676`); `results/closeout/*` (commit `602a40e`); Killcoyne 2020 PDF and supplementary xlsx on the cluster.
- Planned scripts (`scripts/paper_plan/`): `pf_cnv_killcoyne.py` (F1), `pf_main.py` (F2–F5, F9, F6a, F8 tables), `pf_gpu.py` (F6b/F6c image retrain and resampling, F7 ablations and 8b noise floor, F8 train-vs-held-out), `pf_latent_figs.py` (F8 five-fold figures), `pf_render.py`.
- Conventions as before: patient = max over strict pre-event rows; rank AUROC/AUPRC to 3 decimals; 2,000 patient bootstraps `RandomState(0)`; 2,000 patient-label permutations `RandomState(0)`; every fitted quantity fitted on the four training outer folds (inner CV on the release's patient-keyed inner folds) and applied to the held-out fold.

## Pre-specifications

### F1. Killcoyne-method CNV arm
- Their method (Nat Med 26:1733, Methods "Statistical methods"): per-sample weighted mean of segmented CN per 5-Mb window; mean-standardised per window across the cohort; arm means, and each window adjusted by window − arm difference; "589 5-Mb windows and 44 chromosome arms" plus cx; elastic-net logistic regression (glmnet), 5-fold patient-level CV repeated 10×; penalty α tuned in [0, 1] and **0.9 selected** ("limited the number of non-zero coefficients (n = 74) and was not full lasso (for example, 0.9)"); λ by cross-validation; leave-one-patient-out predictions for the discovery cohort (p.1733; Extended Data Fig 9b legend, p.1735+).
- Our implementation: features = the release's `features_5mb_armdiff` (the window-minus-arm features, 587 windows) + `features_arms` (39 arms) + `cx` (the release's own encoding of the same construction; the release has fewer windows/arms than the paper because it drops empty/sex-chromosome columns, stated as such). Standardisation: per-feature mean/sd on the outer training rows (fold-honest version of "across the entire cohort"); median imputation on training rows. Model: `sklearn.linear_model.LogisticRegression(penalty="elasticnet", solver="saga", l1_ratio=0.9, max_iter=20000, class_weight=None)`; C ∈ {0.01, 0.03, 0.1, 0.3, 1, 3, 10} chosen per outer fold by the release inner folds (criterion: patient-level AUROC, max over rows). Trained on our endpoint `y_progressor` (rows), release outer folds `fold_id_rep01`. Sensitivity (secondary): α ∈ {0.1, 0.5, 0.9} also tuned by inner CV.
- Report next to `cnv_only`: AUROC/AUPRC with CIs on all 150, never_in_ERIN 96, also_in_ERIN 54, Killcoyne-discovery 82, other 68. Faithfulness check: Spearman of our arm's OOF row scores vs the published LOPO probabilities on the 500 matched rows (`MOESM4` Fig 2a sheet), and vs cnv_only. Rerun item 2 (WSI vs "CNV (Killcoyne method)") and item 4 (late fusion = plain mean of image_only and the F1 arm probabilities, labelled `late_mean_km`; paired deltas vs WSI and vs each CNV arm; learned fusions not retrained).
- Diagnosis of `cnv_only` on the 25 overlap-discovery patients: per-fold patient AUROC restricted to them (where both classes present); their outer training folds' class balance; standardised-feature distributions (mean |z| over the arm features and cx; PCA-64 score norms) for them vs the other 125 (Mann-Whitney); RF probability distribution.

### F2. Cohort design heterogeneity
- Stratum per patient: Killcoyne-discovery case (any row's CNV id in the 777 sheet and sheet Status P), Killcoyne-discovery control (sheet Status NP), validation sheet (268 sheet), other (neither). Patients with rows in both sheets take the discovery stratum. Cross-tab vs also/never_in_ERIN.
- Main table (all arms incl. F1 and F3 C1–C4) within each stratum with ≥ 5 events and ≥ 20 patients; n and events stated.
- Within discovery stratum: progressors vs non-progressors on age at diagnosis, sex, Prague M/C, follow-up (months first→last biopsy) — Mann-Whitney / Fisher; coverage stated.
- Stratum-only score (stratum progression rate from training folds, applied to held-out) AUROC with CI; per arm, Mann-Whitney of patient scores by stratum among non-progressors (discovery vs validation).

### F3. Clinical arm without endpoint-definition features
- Nested versions, same model/folds as 3a (L2 logistic, inner-CV C, standardisation on training rows, patient max): C1 = row grade; C2 = grade + `MaxPathologySoFar` (**primary clinical arm**); C3 = C2 + `LGDStreakSoFar`; C4 = C3 + `BiopsyIndex`, `DaysSincePreviousBiopsy`, year (= 3a).
- Does a modality add to C2: combinations C2 + image, C2 + cnv_only, C2 + F1 CNV, C2 + late_mean, C2 + image + cnv_only, via (i) fold-z mean and (ii) an L2 logistic stack on the logits of the row scores fitted on the outer training rows (C by inner CV); paired ΔAUROC vs C2 with CI and permutation p. 3b moves to the supplement.

### F4. Risk-group survival inconsistency
- Per group and model (cnv_only, late_mean tertiles): median time-at-risk for progressors and non-progressors separately; derivation of the censoring time checked against the release columns (`MonthsBeforeLastBiopsy` measured from the row vs from the first row: compare its value at the first row with the interval first row → max `NextBiopsyDate`).
- Version B: non-progressor time = earliest row → last known biopsy date computed from biopsy dates (max of `NextBiopsyDate` over the patient's rows; falls back to the last row date). Progressor time unchanged. KM/log-rank/Cox for both versions.
- Interpretability statement for the matched case–control stratum (controls selected on ≥ 3 y follow-up): time-to-event not interpretable there; rates and ORs only.
- Probability distributions (deciles) of cnv_only, F1 arm, late_mean; Killcoyne fixed classes applied to the F1 arm.

### F5. False positives: confounding and label check
- Logistic regression of later HGD+ (and later LGD+) on FP status among non-progressors, adjusted for baseline grade (earliest row) and max grade so far (max over rows); ORs with profile-likelihood-free Wald CIs (statsmodels if available, else sklearn unpenalised + bootstrap CI); per model incl. C2. Repeat FP vs TN within baseline-NDBE non-progressors.
- List every non-progressor with later HGD+: days from last release row, source, and why not a release progressor (endpoint rule requires the *next* biopsy after a pre-event row to be HGD+ or a second consecutive LGD; later events beyond the last release row or after a non-evaluable gap do not enter). Flag those whose later HGD+ is the *next* biopsy after a release row (would be progressors).
- LGD+ definition check: list grades behind the later LGD+ and HGD+ counts for late_mean and image_only FPs.

### F6. Attention and tile sampling
- Attention mass on the top 5 % (13 tiles) and 10 % (26 tiles) per model vs uniform (0.05, 0.10); co-attention vs mean pooling: Spearman of co-attention weights with uniform is undefined, so report the per-row max weight and the fraction of rows whose top-5 % mass < 0.06.
- F6a: image_only AUROC by patient tertile of mean tiles kept (0.5 µm h5 `kept_tiles`), with CIs.
- F6b/F6c (GPU, `pf_gpu.py`): F6c = ABMIL with the release image config (hidden 256, attn 128, dropout 0.1, Adam lr 1e-4, wd 0.01, batch 8), trained per outer fold on the 0.44 µm/px UNI2-h bags (`features_uni2h_05um`, all tiles up to 2,048 per bag, random subsample per epoch when larger, seed 0), fixed epochs = the release fold's `final_epochs`; labelled "image-only, 0.44 µm/px, ≤2,048 tiles" (a scale change from the release's 0.88 µm/px 256 tiles; stated). F6b = the F6c fold model applied to 10 random 256-tile draws (seeds 0–9) of each held-out slide: SD of patient scores across draws, and for the late_mean FN patients whether the F6c prediction (training-fold threshold at sens ≥ 0.80) changes across draws.

### F7. Does fusion use CNV?
- Per learned fusion model, held-out rows: (a) permute all CNV features jointly across held-out rows, 50 repeats; (b) replace CNV input by the training-fold mean (standardised zero vector); image: (a) permute bags across held-out rows, 50 repeats; (b) replace the bag by a single tile equal to the training-fold mean tile embedding. ΔAUROC (patient level) with patient-bootstrap CI (bootstrap over patients of the per-patient permuted-vs-baseline scores, 2,000).
- 8b noise floor: ΔAUROC when one randomly chosen 5-Mb window feature is permuted (10 windows × 50 repeats, seed 0), and per-fold values with SD for the arm features.

### F8. Latent space follow-ups
- Paired difference (patient level) between the linear-probe AUROC and the model's own OOF AUROC for early and intermediate fusion, with CI; per fold training-fold vs held-out AUROC of the model outputs. PCA/UMAP figures for all five folds (projection fitted on each fold's training patients).

### F9. Housekeeping
- Page mapping: pdftotext page N = journal page 1725 + N for N ≤ 9 (1726–1734); N ≥ 10 = Extended Data Figs 1–10 (online). Non-inferiority margin for WSI − CNV: **−0.05 AUROC**, pre-specified here; report the lower CI bound against it for both CNV arms.

(Results follow in the results commit.)

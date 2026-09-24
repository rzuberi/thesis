# P32 — Predicting report fields from the H&E image

Started 24 Sep 2026. Depends on P31 (its fields are the targets). Pre-registered before the first result.

## Question
Which of the things a pathologist writes are visible to a slide model, and does an image-derived "report"
give a cohort without text (SWG) a usable third modality?

## Design
Unit = imaged ERIN case (one UNI2 slide bag, ≤ 1,500 tiles). For each binary target with ≥ 30 positives
and ≥ 30 negatives: gated-attention ABMIL (`scripts/abmil_clf.ABMIL`), patient-disjoint 5-fold (seed 0),
3 seeds averaged, 25 epochs, Adam 1e-4, 800-tile per-epoch subsample, class-weighted BCE. No tuning.
Targets from P31: grade LGD+ and HGD+ (references), IM present, goblet present, inflammation any /
moderate-severe, ulceration, squamous-only, gastric mucosa present, treatment effect, p53 abnormal,
certainty not definite, site GOJ/stomach, specimen resection. Script `scripts/projects/p32_fields_from_image.py`,
four field groups as separate jobs (cuda + h200 twins), chained on P31's validate job.

## Payoff test (the reason for the project), `scripts/projects/p32_swg_fuse.py`
The seed-0 fold models are applied to all 707 SWG release slides (UNI2 npz) to impute every field. Then, on
the release folds and endpoint, patient level, 150 patients: a CV logistic on the imputed-field vector
("fields" arm); 3-way fold-local z-mean fusion (image OOF + CNV OOF + fields) vs the 2-way (image + CNV)
on the same 150 patients; paired 2,000-boot CI. Sanity check first: imputed grade LGD+ vs the SWG
pathologist grade (if this is < 0.7 the imputation has not transferred and the fusion result is moot).

## Predictions written down before results
- Visible (AUROC > 0.8): grade, squamous-only, gastric mucosa, IM/goblet, specimen resection, treatment
  effect (neosquamous epithelium is morphological).
- Partly visible (0.65–0.8): inflammation, ulceration.
- Not visible (≈ 0.5–0.6): p53 status, diagnostic certainty, site (GOJ vs oesophagus is endoscopic, not
  histological).
- SWG payoff: imputed grade tracks the pathologist grade at 0.7–0.8 despite the scale shift; the 3-way
  fusion does NOT beat 2-way with a CI excluding zero at n = 150. If it does, that is the Chapter 1–2 bridge.

## Known caveats
- SWG tiles are the release's 256 stored level-2 tiles (~0.88 µm/px) against ERIN's 0.5 µm/px: a scale shift
  in the imputation. If the sanity check fails, re-extract SWG at 0.5 µm/px (the CONCH scale scripts already
  read the raw slides) before concluding anything.
- Circularity: a field predicted from the image and fused with the image adds only what the field encodes
  of pathologist knowledge beyond the encoder. A null fusion result is informative, not a failure.
- Labels are LLM-derived (P31), so "visible" means "predictable from the image as the LLM read the report".

## Outputs
`feasibility/runs/p32_fields_g*/output/{results.json, oof_<field>.csv, swg_imputed_fields.csv}`;
`feasibility/runs/p32_swg_fuse/output/results.json`; committed copies under `results/numbers/p32_*.json`.

## Status log
- 2026-09-24 evening: scripts written; 8 field-group jobs + fusion job submitted, chained on P31.
- 2026-09-25 02:00: FIRST PASS DONE (`results/numbers/p32_fields.json`; P31 v1 fields as targets, 2,293 cases, ABMIL,
  patient folds, 3 seeds). Image → field AUROC [patient-clustered 95 % CI]:

  | field | n / pos | AUROC | predicted band | verdict |
  |---|---|---|---|---|
  | specimen_resection | 2,293 / 91 | 1.000 | visible | trivially (resection tissue) |
  | squamous_only | 2,291 / 127 | 0.920 [0.892, 0.945] | visible | held |
  | grade HGD+ | 1,642 / 482 | 0.911 [0.893, 0.931] | visible | held |
  | im_present | 2,192 / 1,406 | 0.897 [0.884, 0.910] | visible | held |
  | grade LGD+ | 1,642 / 644 | 0.861 [0.840, 0.882] | visible | held (jury-label reference 0.926 on 2,153 slides) |
  | ulceration | 2,154 / 320 | 0.847 [0.818, 0.875] | partly | above band |
  | treatment_effect | 2,293 / 522 | 0.821 [0.797, 0.842] | visible | held |
  | gastric_present | 1,182 / 831 | 0.781 [0.749, 0.811] | visible | just below band |
  | p53_abnormal | 473 / 193 | 0.749 [0.703, 0.795] | not visible | **above band**: rides on grade (p53 is stained when dysplasia is suspected) |
  | inflammation_mod_severe | 1,846 / 373 | 0.742 [0.709, 0.771] | partly | held |
  | site_goj_or_stomach | 2,293 / 612 | 0.723 [0.698, 0.749] | not visible | above band: cardia-type mucosa is morphological |
  | inflammation_any | 1,846 / 1,517 | 0.607 [0.574, 0.643] | partly | below band (85 % prevalence; "mild" is the default phrase) |
  | certainty_not_definite | 2,289 / 78 | 0.538 [0.467, 0.611] | not visible | held |
  | goblet_present | skipped (21 positives) | | | |

  Reading: what the pathologist SEES is predictable from UNI2 bags (tissue type, IM, ulceration, treatment change,
  grade); what they INFER or ORDER (certainty) is not; p53 and site are visible only through their correlation with
  grade and mucosa type. Eleven of thirteen tested fields fall in or above the predicted band.
  **SWG payoff test: MOOT in pass 1.** Imputed grade LGD+ vs the SWG pathologist grade = **0.540**: the fold models
  did not transfer to the release's 256 level-2 tiles (~0.88 µm/px), exactly the pre-registered failure condition
  (< 0.7). The 3-way fusion result from `p32_swg_fuse` is therefore reported but not interpreted.
  Action (pass 2, launched): re-extract all 707 SWG release slides with the ERIN UNI2-h pipeline at 0.5 µm/px
  (`feasibility/swg_manifest_05um.txt` → `SWGCohort/features_uni2h_05um/`, 6 cuda pull-workers + 2 h200), then
  re-run six informative fields with `SWG_FEATS` pointing at the new bags and the fold models saved
  (`p32b_fields`), then the fusion test (`p32b_swg_fuse`). Targets now come from P31 v2.
- 2026-09-25 late: PASS 2 DONE (`results/numbers/p32b_fields.json`, `p32b_swg_fuse.json`, `p32_fuse_controls.json`).
  All 707 SWG release slides re-extracted with the ERIN UNI2-h pipeline at 0.5 µm/px (`SWGCohort/features_uni2h_05um/`,
  8,000-tile cap). Six ERIN field heads (P31 v2 targets) retrained with fold models saved, applied to the new bags:
  ERIN OOF AUROCs grade LGD+ 0.887, IM 0.891, squamous-only 0.881, ulceration 0.858, treatment 0.819, inflammation
  mod/severe 0.738 (v2 labels; all within 0.04 of pass 1).
  **Sanity gate:** imputed grade vs the SWG spreadsheet grade **0.619** (pass 1: 0.540). Still below the pre-registered
  0.7, so by the letter of the pre-registration the transfer is "not established"; but see the DB-code result (C27):
  the spreadsheet grade itself agrees with the database's coded grade at only 0.907 two-tier, so 0.7 against the
  spreadsheet may have been the wrong bar. Reported as-is.
  **Payoff test, all 150 SWG patients (50 progressors), release folds, patient level:**

  | arm | AUROC [95 % CI] |
  |---|---|
  | image_only (release) | 0.731 [0.640, 0.814] |
  | cnv_only (release) | 0.663 [0.569, 0.754] |
  | imputed fields (CV logistic on 6 fields) | 0.738 [0.652, 0.817] |
  | fuse2: image + CNV | 0.783 [0.700, 0.854] |
  | **fuse3: image + CNV + imputed fields** | **0.832 [0.762, 0.894]** |
  | Δ fuse3 − fuse2 | **+0.050 [+0.015, +0.089]**, label-permutation p 0.002 |
  | Δ fuse3 − image | +0.101 [+0.040, +0.168] |

  **Controls (`p32_fuse_controls.json`):**
  - Ensemble control: the same 3-way fusion with a SECOND SWG-trained image model (rep02 image_only OOF, 0.745)
    as the third arm gives 0.800, Δ vs fuse2 +0.018 [−0.018, +0.058], p 0.17. Fields beat this control by +0.032
    [−0.010, +0.078]: **the gain over plain ensembling is not established at n = 150.**
  - The gain is carried by ONE field: the imputed grade LGD+ head. Alone it predicts SWG progression at **0.756**,
    above the SWG-trained image arm (0.731); fuse3 with grade only 0.851 (Δ vs fuse2 +0.069 [+0.024, +0.119]);
    leave-grade-out drops fuse3 to 0.809. Imputed inflammation mod/severe also carries signal alone (0.739);
    IM, ulceration, squamous-only and treatment effect are at or below chance for progression (0.37–0.56), as expected.
  - Pass-1 (0.88 µm/px) fusion for the record: fields 0.692, fuse3 0.803, Δ +0.020 [−0.020, +0.062] — scale mattered.

  **Reading (honest version).** An ERIN-trained dysplasia-grade head, trained on 2,291 report-labelled slides and
  transferred to SWG at matched scale, is a better progression predictor on SWG than the arm trained on SWG's own
  707 slides, and adding it to image + CNV raises the fusion to 0.83. Whether that is "report-derived fields as a
  third modality" or "report-supervised pre-training on a 3× larger cohort" cannot be separated here: the control
  says the gain over a second same-cohort image model is +0.03 with an interval that includes zero. Both readings are
  useful for the thesis; the second is the more defensible claim. Prediction check: "3-way does NOT beat 2-way with a
  CI excluding zero" — FALSIFIED (it does), but the pre-registered mechanism claim needs the ensemble control to clear
  zero, which it does not. This is the first positive multimodal result on SWG that does not depend on arm selection:
  the arm and the rule were fixed before the SWG numbers existed.
  **Next (not run):** (1) selection-adjusted permutation over the six fields; (2) a stronger ensemble control (an
  ERIN-trained image head on a NON-grade target, e.g. treatment effect, which is at chance for progression, as the
  third arm — already available: fuse3 with treatment_effect only vs fuse2 is the cheap version); (3) second CV
  repeat of the fold models; (4) apply the same heads to ACE-B when scanned.
- 2026-09-24 23:50: OVERNIGHT fluke checks launched — repeat-split grade head, permuted-label head (random-head control), SWG image arm on 0.5 µm features, selection-adjusted permutation over fields, rep02-split replication, imputed grade vs DB confirmed code, calibration; real-vs-imputed fields on the 65 DB-matched patients. See `docs/projects/overnight_2026-09-25.md`.

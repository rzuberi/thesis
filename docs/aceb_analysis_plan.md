# ACE-B analysis plan (frozen before any ACE-B slide is processed)

Written 25 Sep 2026 as item N of `docs/closeout_for_review.md`. No ACE-B slide, feature file or CNV table exists on the
cluster at the time of writing (checked: `/mnt/scratche/fast/fmlab/datasets/imaging/` has no ACE-B directory;
`/mnt/scratche/slow/fmlab/zuberi01/phd/aceb_meta/` holds metadata only). This plan is fixed at the commit that adds it;
any later change is recorded as an amendment below the line, never by editing the frozen text.

## 1. Frozen models (sha256 in `results/closeout/aceb_checkpoint_hashes.json`, computed by `scripts/closeout/co_checkpoint_hashes.py`)

| Model | Files | sha256 (first 16 hex) |
|---|---|---|
| SWG image_only, 5 outer-fold ABMIL checkpoints | `<release>/training_final_nested_cv_v1/image_only/fold{1..5}/model.pt` | 105c29f411ff2db9, 39b89ec2101aceb5, f6e9d595f2b78f3d, 41ebf0f149792b76, 62eb26957b7fb9bf |
| SWG cnv_only, 5 outer-fold sklearn models | `<release>/training_final_nested_cv_v1/cnv_only/fold{1..5}/model.joblib` (+ `resolved_config.yaml`) | 8122113fd4cb9fb1, cdfbcafa7c6eb558, 9c8d678714c801a9, 13d5761d0881cf62, a2320516e9031d26 |
| SWG late_mean | no file: plain mean of the image_only and cnv_only probabilities (release construction) | n/a |
| ERIN grade head, leak-free (P32), 5 fold checkpoints | `feasibility/runs/p32_head_noov/output/model_grade_LGDplus_f{0..4}.pt` (cluster) | ed7b7822d2797561, 044517fae4c64dda, 9772929edce9fc12, 0f8d27aab5fd93ee, a6b4ba88944e6ad7 |
| CNV arm-feature table used to define the CNV input schema | `<release>/feature_views/cnv/features_arms.csv` | 22651db98586bf96 |
| Fixed thresholds | `results/numbers/swg_operating_points_patient.json` | 08611ad5e9cf4043 |
| Feature extraction code | `campaigns/allslides/extract_worker.py` | eede37e79a087429 |

`<release>` = `/mnt/scratche/slow/fmlab/zuberi01/phd/barretts_retraining/barretts_training/analysis/chapter1_lgd2_final_pre_event_20260713_final`.
Scoring uses the average of the five fold models' outputs per slide (image, grade head) or per CNV profile (cnv_only). No ACE-B data is used for training, tuning, thresholding or calibration.

## 2. Preprocessing
- H&E: UNI2-h features at 0.5 µm/px, 224 px tiles, 8,000-tile cap, tissue mask and banded thumbnail exactly as `extract_worker.py` (the pipeline that produced `SWGCohort/features_uni2h_05um/`, on which the ERIN grade head was applied to SWG). For the SWG image_only arm, which was trained on the release's 0.88 µm/px level-2 tiles (256 per slide), ACE-B tiles are additionally extracted at the release scale with the release's tile sampler; both feature sets are produced before any scoring. Scanner (.svs, Aperio) differs from SWG (.ndpi, Hamamatsu C13210); this is declared as a shift, not corrected.
- CNV: ACE-B sWGS (~7× per the cohort owner) is down-sampled to the SWG read depth (target: the median read count of the SWG release samples reported in `closeout_for_review.md` item C) before QDNAseq 50 kb binning, then arm-level features are built with the same columns as `features_arms.csv`. If read-level data are not provided, the arm table from the owner's pipeline is used and this is stated as a depth shift.
- Sample unit: one biopsy slide + one CNV profile per row, as in SWG.

## 3. Endpoint and inclusion
- Endpoint: progression to HGD or IMC/OAC as adjudicated by the cohort owner (Leanne / Dr di Pietro's trial adjudication), patient level. SWG's LGD2+ endpoint cannot be reproduced in ACE-B because the trial adjudication is HGD/IMC; this difference is declared.
- Included rows: pre-event rows only (biopsy date before the event biopsy for progressors; all rows for non-progressors), from patients whose baseline Seattle-protocol histology is NDBE, IND or LGD.
- The 30 prevalent HGD/IMC patients (owner's count) are EXCLUDED from the primary progression analysis: they have the outcome at baseline and are not at risk of the modelled transition. They form a separate, secondary "prevalent dysplasia detection" set: the grade head and image_only score are reported as AUROC for prevalent HGD/IMC vs non-progressor NDBE, with its own n and CI, and are not pooled with the progression analysis.
- Patient score = max over that patient's included rows.

## 4. Primary metric and comparison
- Primary: patient-level AUROC of late_mean (image_only + cnv_only) for progression, with a 2,000-resample patient bootstrap CI (seed 0). Reported alongside: image_only alone, cnv_only alone, ERIN grade head alone, and image + CNV + grade head (fold-local z-mean is not defined without folds; on ACE-B the three arms are z-scored over the ACE-B cohort and averaged, declared as such).
- Primary comparison: late_mean vs image_only, paired bootstrap CI on the difference. Power note carried from `docs/NUMBERS.md` §25: with ~11 progressors the CI on an AUROC near 0.75 is about ±0.15; ACE-B can show transfer (AUROC above 0.5) but cannot resolve a 0.04 fusion gain. This is stated in advance and will not be re-framed after the fact.
- Fixed operating points: specificity at the SWG-fixed thresholds for sensitivity 0.95 and 1.0 (`swg_operating_points_patient.json`, item-19 rule), and the other-fold thresholds in `swg_robustness.json` item 14, applied unchanged; ACE-B sensitivity and specificity at those thresholds are reported with n and events.
- Calibration: calibration-in-the-large and slope of the release probabilities in the ACE-B prevalence; Brier.
- Every number is reported with n patients and n progressors. No tuning, no threshold re-selection, no model selection on ACE-B.

## 5. Order of operations (to be logged with timestamps)
1. Receive slides and CNV; record scanner, dates, depth. 2. Extract features (both scales). 3. Build the CNV arm table. 4. Score with the frozen models. 5. Compute the pre-specified metrics once. 6. Write results to `results/aceb/` and a status entry to this file's amendment section.

---
Amendments: none.

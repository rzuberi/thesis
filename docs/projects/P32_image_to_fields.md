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

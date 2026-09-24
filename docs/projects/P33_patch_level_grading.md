# P33 — Patch-level grading as an interpretable modality

Started 24 Sep 2026. Builds on 2.47 (tile-level training within 0.02–0.03 of ABMIL; better on six-class
under section labels) and the 12 tile grade maps. Pre-registered before the first result.

## Question
If every tile of every ERIN slide carries a six-class grade probability, does a 13-number summary of a slide
(fraction of tiles per grade, mean probability per grade, log tile count) carry the imminent-dysplasia
signal that ABMIL found (T2b 0.86, T3a 0.82, T3b 0.87)? If yes, the field-effect result becomes
inspectable ("x % of tiles look LGD-like on a slide the pathologist called benign") instead of a bag score.

## Design, `scripts/projects/p33_tilefeat.py`
Tile MLP 1536→512→6 trained on SECTION labels of the 1,538 dual-labelled slides (2.47 recipe: 4 epochs,
2,000 tiles per slide, sqrt-inverse-frequency class weights), the 2.47 patient folds, seed 0: five fold
models plus one final model on all 1,538. Every UNI2 feature file referenced by the ERIN task tables and
every all-slides feature file (~11,000) is scored; a slide that is one of the 1,538 is scored by the fold
model that never saw it (matched by uuid), all others by the final model. Output: one row per slide with
6 argmax fractions, 6 mean probabilities, log tile count; the models are saved for tile maps.

## Payoff test, `scripts/projects/p33_tasks.py`
On T2a, T2b (case bags: tile-weighted mean of slide summaries), T3a, T3b, T3a_bio, T3b_bio (one slide):
logistic on the 13-d summary + age + grade flag, queue folds (`patient_folds` seed 0), vs the queue's saved
ABMIL image OOF; paired patient-clustered 2,000-boot deltas; plus a z-mean fusion of the two. Top five
coefficients reported so the signal is readable.

## Predictions written down before results
- T3a/T3b: the summary reaches within 0.05 of ABMIL (field effect shows as raised IND/LGD tile fractions
  on benign slides); the top coefficient is frac_IND or mean_LGD.
- T2b (HGD within a year, 30 positives): the summary is ≥ 0.05 below ABMIL; the attention model uses
  something the grade-fraction summary throws away.
- Fusion of summary and ABMIL does not beat ABMIL.

## Caveats
- Leakage guard: the tile model saw section labels of the 1,538 slides; fold-wise scoring removes direct
  leakage for those slides. Case bags in T2 may contain slides from the same patients as training slides;
  the T2 label (future dysplasia) is not the section label, so the leak is indirect, and it is stated.
- The summary is a slide-level compression; spatial statistics (clustering of LGD-like tiles) are a second pass.

## Outputs
`feasibility/runs/p33_tilefeat/output/{tile_summary_all.parquet, tile_mlp_models.pt, results.json}`,
`feasibility/runs/p33_tasks/output/results.json`; committed copy `results/numbers/p33_tasks.json`.

## Status log
- 2026-09-24 evening: scripts written; tilefeat (cuda + h200 twin) and tasks (chained) submitted.
- 2026-09-24 22:30: tilefeat DONE on cuda (h200 twin cancelled). 13,319 slides summarised, 1,538 fold-scored; OOF slide-level LGD+ AUROC from mean tile probability 0.837 (2.47 reported 0.836 for the same recipe: reproduced). `feasibility/runs/p33_tilefeat/output/`. p33_tasks released.

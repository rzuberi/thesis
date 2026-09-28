# Killcoyne protocol with imaging: CNV-only vs imaging-only vs early / intermediate / late fusion

Status: PRE-SPECIFICATION. Nothing below has been run. Results are appended in a later commit; this section is not edited afterwards.

## Question

`docs/paper_plan_killcoyne_reconcile.md` (commits a655e08, 73c1d48, 3a1b5f7) reproduced the Killcoyne 2020 CNV model: on their shipped 773 × 634 feature matrix, glmnet (α 0.9, standardize = FALSE) left-one-patient-out (LOPO) regenerates the published probabilities (Spearman 0.991; per-sample AUROC 0.870 vs published 0.865). Here the protocol is held fixed (same samples, same labels, same LOPO folds, same inner CV, same λ rules, same evaluation) and only the input changes: CNV only, imaging only, and CNV + imaging by early, intermediate and late fusion.

## Fixed protocol (identical for every arm)

- **Samples.** The Killcoyne discovery samples (773 published, 88 patients) that also have a UNI2 slide embedding: 676 samples, 80 patients (UNI2 bags mapped via the embedding file's stored slide path and the SWG image inventory; 97 samples without an image, 8 patients with none). This common set C is the primary population for every arm. A sample with several slides uses the union of their tiles (7 samples).
- **Label.** Per sample, the patient's sheet Status (P = 1, NP = 0), as in the paper. HGD/IMC and post-event samples stay in, as in the paper.
- **Folds.** LOPO over the 80 patients of C. Inner CV (λ selection, and the neural validation split): the training patients shuffled with `set.seed(r)` and split into 5 groups, r = 1..10 (linear), r = 1 group 1 as the validation set (neural).
- **CNV input.** Primary: their shipped matrix (rows aligned to our samples in the reconciliation; used as shipped). Secondary: package features from our own counts (reconciliation plan B construction).
- **Image input.** UNI2 (tile 224, level 2) embeddings, 256 tiles per slide, 1,536 features: the same bags the release image model used. Linear tier uses the slide mean embedding; neural tier uses the tile bags.
- **Evaluation.** Per-sample AUROC (the paper's unit, primary), patient-mean and patient-max AUROC, per-sample and patient-max AUPRC; on C, and on the release rows within C (secondary). Rank AUROC, 3 decimals. 95% CI by patient bootstrap (2,000, `RandomState(0)`).
- **Comparisons.** Each arm minus CNV-only of the same tier and CNV source, on the same samples: ΔAUROC per sample and patient max with paired patient-bootstrap 95% CI, and a paired permutation p (swap the two models' scores within each patient, 2,000, seed 0).

## Arms

**Anchors (already computed, reported for reference).** CNV-only on all 773 samples: their matrix, class-error λ min (0.860) and global λ (0.869); package features plan B (0.852).

**Linear tier (the reproduced machinery).** glmnet α 0.9, standardize = FALSE; image and PCA blocks z-scored over the whole set C (the paper's whole-cohort standardisation; their CNV matrix used as shipped); for each left-out patient λ by 10 × 5 patient-grouped CV. Primary λ rule: class-error min (fold-honest). Secondary: 'global' (one λ by the same CV on all of C, reused for every left-out patient; the rule that matched the published outputs, not fold-honest), deviance min.
- L-CNV: CNV block only.
- L-IMG: image mean embedding only.
- L-EARLY: [CNV block, image block] concatenated.
- L-INTER: per modality a PCA fitted on the training patients only (32 components each), components z-scored on the training rows, concatenated (64) into the same glmnet.
- L-LATE: mean of the L-CNV and L-IMG LOPO probabilities (equal weights, no fitting).

**Neural tier (release architectures, fixed release hyperparameters, no search).** Classes imported unchanged from the release code; training loop = release `fit_neural` (AdamW, lr 1e-4, weight decay 0.01, batch 8, ≤ 20 epochs, patience 5, positive-class weight, early stopping on validation patient-max AUPRC, release CNV standardisation on training rows). Three seeds (0, 1, 2); the arm's score is the mean probability over seeds.
- N-IMG: `AttentionMIL` (hidden 256, attention 128, dropout 0.1) on the tile bag.
- N-EARLY: `EarlyFusionMLP` (hidden 512, dropout 0.2) on [mean tile embedding, CNV block].
- N-INTER: `IntermediateABMILCNV` (image 256, CNV 128, attention 128, fusion 256, dropout 0.2).
- N-LATE: mean of the N-IMG probability and the L-CNV probability (release late_mean pairs the image model with the CNV model).

CNV source: primary their matrix; secondary package features (L-CNV, L-EARLY, L-INTER, N-EARLY, N-INTER, N-LATE rerun with them).

## Status reporting

Each arm DONE / PARTIAL / NOT AVAILABLE. One line of interpretation at most.

## Outputs

- Scripts `scripts/paper_plan/`: `km_prep.py` (set C, bags, image matrices), `km_linear.R` (linear tier, sharded by `CFG_ID` / `CHUNK_ID`), `km_neural.py` (neural tier, sharded by model / seed / chunk), `km_merge.py`, `km_render.py`.
- Results `results/paper_final/killcoyne_multimodal.json` (aggregates only). Row-level outputs on the cluster under `feasibility/paper_plan/killcoyne_mm/`.
- Jobs: small chunks, each submitted to every partition (epyc, rocm, cuda, h200); the first copy to start takes the task lock and the others exit.

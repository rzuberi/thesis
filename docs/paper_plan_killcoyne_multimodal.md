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

---

## Results

Sources: `results/paper_final/killcoyne_multimodal.json` · scripts `scripts/paper_plan/km_*.{py,R}` · results commit d497449. Row-level outputs on the cluster under `feasibility/paper_plan/killcoyne_mm/`.

### Status

| Arm | Status |
|---|---|
| L-CNV (their) | DONE |
| L-IMG | DONE |
| L-EARLY (their) | DONE |
| L-INTER (their) | DONE |
| L-LATE (their) | DONE |
| N-IMG | DONE |
| N-EARLY (their) | DONE |
| N-INTER (their) | DONE |
| N-LATE (their) | DONE |
| L-CNV (pkg) | DONE |
| L-EARLY (pkg) | DONE |
| L-INTER (pkg) | DONE |
| L-LATE (pkg) | DONE |
| N-EARLY (pkg) | DONE |
| N-INTER (pkg) | DONE |
| N-LATE (pkg) | DONE |

### Set C

676 samples, 80 patients (37 P patients, 266 P samples); pathology {'NDBE': 463, 'LGD': 91, 'ID': 75, 'HGD': 26, 'IMC': 21}; 5 samples with more than one slide (the pre-specification said 7); 97 published samples without a UNI2 bag, patients 74, 75, 76, 77, 78, 79, 82, 83 have none; 461 of the samples are release rows.

CNV-only anchors on all 773 samples (reconciliation): their matrix, class min (cfg 32) 0.860; their matrix, global (cfg 32) 0.869; package features, plan B 0.852; published 0.865.

### Primary rule (class-error λ min per left-out patient; neural = mean of 3 seeds), CNV source: their shipped matrix

| Arm | Per-sample AUROC | Patient-mean AUROC | Patient-max AUROC | Per-sample AUPRC | Patient-max AUPRC | Release rows: per sample / patient max | Δ per sample vs L-CNV (p) | Δ patient max vs L-CNV (p) |
|---|---|---|---|---|---|---|---|---|
| L-CNV (their) | 0.846 [0.774, 0.908] | 0.881 | 0.879 [0.790, 0.954] | 0.811 | 0.904 | 0.789 / 0.824 | — | — |
| L-IMG | 0.878 [0.837, 0.915] | 0.947 | 0.865 [0.776, 0.944] | 0.850 | 0.896 | 0.840 / 0.804 | +0.032 [-0.036, 0.106] (0.3793) | -0.014 [-0.106, 0.078] (0.7786) |
| L-EARLY (their) | 0.910 [0.854, 0.953] | 0.969 | 0.949 [0.892, 0.988] | 0.892 | 0.955 | 0.867 / 0.929 | +0.065 [0.032, 0.105] (0.0005) | +0.070 [0.018, 0.135] (0.007) |
| L-INTER (their) | 0.875 [0.811, 0.930] | 0.941 | 0.903 [0.816, 0.976] | 0.826 | 0.856 | 0.821 / 0.845 | +0.029 [-0.036, 0.097] (0.3818) | +0.024 [-0.050, 0.099] (0.5712) |
| L-LATE (their) | 0.920 [0.873, 0.954] | 0.955 | 0.895 [0.814, 0.958] | 0.895 | 0.910 | 0.870 / 0.867 | +0.074 [0.032, 0.125] (0.001) | +0.016 [-0.038, 0.077] (0.6097) |
| N-IMG | 0.817 [0.750, 0.875] | 0.907 | 0.876 [0.793, 0.946] | 0.822 | 0.894 | 0.738 / 0.756 | -0.029 [-0.104, 0.053] (0.5032) | -0.003 [-0.088, 0.084] (0.956) |
| N-EARLY (their) | 0.866 [0.793, 0.926] | 0.911 | 0.867 [0.776, 0.947] | 0.843 | 0.888 | 0.825 / 0.827 | +0.020 [-0.040, 0.084] (0.5717) | -0.012 [-0.063, 0.038] (0.6477) |
| N-INTER (their) | 0.870 [0.802, 0.926] | 0.908 | 0.849 [0.747, 0.938] | 0.837 | 0.871 | 0.820 / 0.814 | +0.025 [-0.034, 0.084] (0.4943) | -0.030 [-0.087, 0.024] (0.2744) |
| N-LATE (their) | 0.883 [0.820, 0.933] | 0.940 | 0.919 [0.849, 0.976] | 0.873 | 0.929 | 0.813 / 0.852 | +0.038 [0.001, 0.082] (0.1279) | +0.040 [0.004, 0.084] (0.094) |

### Primary rule (class-error λ min per left-out patient; neural = mean of 3 seeds), CNV source: package features from our counts

| Arm | Per-sample AUROC | Patient-mean AUROC | Patient-max AUROC | Per-sample AUPRC | Patient-max AUPRC | Release rows: per sample / patient max | Δ per sample vs L-CNV (p) | Δ patient max vs L-CNV (p) |
|---|---|---|---|---|---|---|---|---|
| L-IMG | 0.878 [0.837, 0.915] | 0.947 | 0.865 [0.776, 0.944] | 0.850 | 0.896 | 0.840 / 0.804 | (see their-source table) | (see their-source table) |
| N-IMG | 0.817 [0.750, 0.875] | 0.907 | 0.876 [0.793, 0.946] | 0.822 | 0.894 | 0.738 / 0.756 | (see their-source table) | (see their-source table) |
| L-CNV (pkg) | 0.868 [0.795, 0.928] | 0.875 | 0.882 [0.800, 0.950] | 0.825 | 0.891 | 0.803 / 0.857 | — | — |
| L-EARLY (pkg) | 0.907 [0.852, 0.952] | 0.938 | 0.919 [0.852, 0.971] | 0.870 | 0.927 | 0.856 / 0.890 | +0.038 [0.004, 0.081] (0.059) | +0.037 [-0.010, 0.087] (0.2169) |
| L-INTER (pkg) | 0.894 [0.848, 0.934] | 0.947 | 0.901 [0.821, 0.967] | 0.830 | 0.882 | 0.856 / 0.829 | +0.025 [-0.030, 0.089] (0.3923) | +0.019 [-0.064, 0.097] (0.6647) |
| L-LATE (pkg) | 0.925 [0.881, 0.961] | 0.955 | 0.920 [0.846, 0.976] | 0.906 | 0.935 | 0.870 / 0.894 | +0.057 [0.019, 0.104] (0.023) | +0.038 [-0.013, 0.091] (0.2619) |
| N-EARLY (pkg) | 0.864 [0.789, 0.928] | 0.924 | 0.899 [0.815, 0.967] | 0.837 | 0.917 | 0.811 / 0.853 | -0.004 [-0.058, 0.052] (0.9055) | +0.017 [-0.055, 0.079] (0.6697) |
| N-INTER (pkg) | 0.849 [0.779, 0.913] | 0.917 | 0.872 [0.779, 0.951] | 0.829 | 0.889 | 0.773 / 0.816 | -0.019 [-0.072, 0.031] (0.5457) | -0.010 [-0.083, 0.050] (0.7821) |
| N-LATE (pkg) | 0.893 [0.834, 0.940] | 0.941 | 0.934 [0.870, 0.985] | 0.881 | 0.946 | 0.819 / 0.881 | +0.024 [-0.013, 0.070] (0.3738) | +0.052 [0.018, 0.096] (0.1214) |

### Post hoc: same predictions scored without the HGD/IMC samples

Added after the pre-specification: under the paper's label the HGD/IMC diagnostic samples are progressor samples, and their slides show the diagnosis itself. No model is refitted.

| Arm | Samples | Per-sample AUROC | Patient-max AUROC |
|---|---|---|---|
| L-CNV (their) | 629 | 0.822 | 0.837 |
| L-IMG | 629 | 0.859 | 0.844 |
| L-EARLY (their) | 629 | 0.896 | 0.927 |
| L-INTER (their) | 629 | 0.858 | 0.882 |
| L-LATE (their) | 629 | 0.907 | 0.876 |
| N-IMG | 629 | 0.789 | 0.819 |
| N-EARLY (their) | 629 | 0.847 | 0.845 |
| N-INTER (their) | 629 | 0.853 | 0.818 |
| N-LATE (their) | 629 | 0.863 | 0.864 |
| L-CNV (pkg) | 629 | 0.849 | 0.843 |
| L-EARLY (pkg) | 629 | 0.892 | 0.892 |
| L-INTER (pkg) | 629 | 0.881 | 0.877 |
| L-LATE (pkg) | 629 | 0.913 | 0.902 |
| N-EARLY (pkg) | 629 | 0.844 | 0.882 |
| N-INTER (pkg) | 629 | 0.825 | 0.843 |
| N-LATE (pkg) | 629 | 0.873 | 0.900 |

### Secondary λ rules (linear tier)

| Arm | Per-sample AUROC | Patient-max AUROC |
|---|---|---|
| L-CNV (their) [global] | 0.845 | 0.883 |
| L-IMG [global] | 0.872 | 0.866 |
| L-EARLY (their) [global] | 0.912 | 0.948 |
| L-INTER (their) [global] | 0.883 | 0.918 |
| L-LATE (their) [global] | 0.918 | 0.908 |
| L-CNV (their) [dev_min] | 0.845 | 0.872 |
| L-IMG [dev_min] | 0.865 | 0.871 |
| L-EARLY (their) [dev_min] | 0.888 | 0.914 |
| L-INTER (their) [dev_min] | 0.880 | 0.915 |
| L-LATE (their) [dev_min] | 0.913 | 0.920 |
| L-CNV (pkg) [global] | 0.888 | 0.891 |
| L-EARLY (pkg) [global] | 0.916 | 0.926 |
| L-INTER (pkg) [global] | 0.889 | 0.921 |
| L-LATE (pkg) [global] | 0.931 | 0.915 |
| L-CNV (pkg) [dev_min] | 0.883 | 0.887 |
| L-EARLY (pkg) [dev_min] | 0.909 | 0.922 |
| L-INTER (pkg) [dev_min] | 0.886 | 0.909 |
| L-LATE (pkg) [dev_min] | 0.927 | 0.927 |

### Neural seeds

Per-sample AUROC by seed: img {'0': 0.797, '1': 0.804, '2': 0.825}; early_their {'0': 0.854, '1': 0.836, '2': 0.865}; inter_their {'0': 0.853, '1': 0.865, '2': 0.858}; early_pkg {'0': 0.85, '1': 0.842, '2': 0.857}; inter_pkg {'0': 0.823, '1': 0.834, '2': 0.852}.

Best epoch (early stopping) by model: early_pkg mean 2.2 (min 1.0, max 7.0); early_their mean 2.33 (min 1.0, max 8.0); img mean 7.03 (min 1.0, max 15.0); inter_pkg mean 3.46 (min 2.0, max 8.0); inter_their mean 2.97 (min 1.0, max 7.0).

**Interpretation.** With the paper's samples, labels, folds and λ rule held fixed, adding UNI2 imaging to the reproduced CNV model raised per-sample AUROC from 0.846 to 0.910 (linear early fusion, Δ +0.065 [0.032, 0.105], p 0.0005) and 0.920 (linear late fusion, Δ +0.074 [0.032, 0.125], p 0.001); imaging alone and the neural fusion arms were not distinguishable from CNV alone.

**Deviations and caveats.** (1) 5 samples have more than one slide (the pre-specification said 7). (2) The common set drops 97 of the 773 samples (14 HGD/IMC) and 8 patients, so L-CNV here (0.846, their matrix) is not the 773-sample anchor (0.860). (3) Neural early stopping chose epochs 1–8 for the fusion models (mean 2–3.5) and 1–15 for N-IMG (mean 7); hyperparameters were fixed at the release values, not tuned for this label. (4) The HGD/IMC-excluded scoring was added post hoc. (5) The permutation p swaps whole patients' scores between two arms and can disagree with the bootstrap interval when the effect is concentrated in a few patients.

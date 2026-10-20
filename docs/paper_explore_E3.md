# Exploration E3: a better H&E model from features that already exist

Status: exploratory, not confirmatory (rules: `paper/reviews_round7/decisions/EXPLORE_RULES.md`). Written 20 October 2026.

## Plan

**Question.** Can a better slide model, built only from tile embeddings already on disk, flag fewer non-progressor patients without missing progressors, either alone (P1) or inside the R49 gate?

**Current L-IMG.** Elastic net (α 0.9) on the mean UNI2-h embedding of 256 tiles per slide (level 2, about 0.88 µm/px). Samples with several slides pool the union of their tiles.

**Inventory first.** List what is stored for the 676 set-C samples (683 slides), by extractor, scale and number of tiles. No slide pixels are read.

**Fitting.** Every variant is refitted inside the stored patient-grouped folds (10 repeats × 10 folds) with the stored λ rules:
- outer: `kv_cv.R` (`cvcurves`, 10 × 5 inner reshuffles, class-error minimum);
- inner out-of-fold predictions: `hz_fit.R` (`cvcurves1`, 5 inner folds).

`ex_e3_refit.R` copies `rv4_refit.R`. Only the feature block changes. Check: the refit on the stored `img_mean.csv` must reproduce the stored L-IMG outer and inner predictions.

**Variants.**
1. Pooling on the current tiles: max, mean+SD, quantiles (10/50/90%), top-k mean by tile norm (k = 8, 16, 32), and top-k mean of tile scores. Tile scores come from the fitted slide-mean model applied to each tile; the top-k uses k = 8, 16, 32 and the maximum.
2. Scale: UNI2-h level 1 (about 0.44 µm/px); multi-scale concatenations.
3. Extractors:
   - Prov-GigaPath at levels 1, 2 and 3;
   - Virchow2 at level 2 (256 tiles);
   - TRIDENT 20× all-tissue tiles (0.5 µm/px): H-optimus-0, Virchow2, CONCH v1.5, CTransPath, MUSK.
   
   Also an extractor ensemble (the mean of per-extractor probabilities, outer and inner alike).
4. Endoscopy-level pooling:
   - the current rule (max of sample scores);
   - the mean sample logit;
   - the model applied to the embedding pooled over all the endoscopy's tiles.
5. A nested choice among variants: per outer fold, pick the variant with the best inner out-of-fold AUROC on training patients. This is the honest version of "pick the best variant".
6. Attention-MIL is not run: it scored 0.778 before, below the linear model.

**Scoring.** `ex_e3_score.py` runs the round-8 code (`rv8_landscape.py` / `rv8b_step3.py` module bodies, unchanged) with L-IMG replaced. L-LATE = (L-CNV + new L-IMG) / 2, and the copy-number arm is unchanged. P1 and R49 use the same cut-off rules on inner out-of-fold predictions. Reported per variant:
- fold-stratified AUROC (sample, endoscopy, patient), with paired Δ against the current L-IMG;
- Δ non-progressor patients ever flagged and Δ progressor patients caught, against R49 and P1;
- Δ endoscopy specificity at matched endoscopy sensitivity (new P1 matched per draw to R49's, and to the current P1 at 90%);
- paired patient bootstrap (2,000 draws, `RandomState(0)`);
- apparent numbers (threshold set on the evaluated endoscopies), labelled optimistic.

**Data stay on the cluster.** Features, predictions and fits stay under `killcoyne_mm/explore_E3/`. Only aggregate JSON goes to `results/paper_final/explore_E3/`.

## Results

Exploratory. More than 50 variants were scored on the same 75 patients, so any single "best" row is selected after seeing the results and is optimistic. Every threshold, λ and fitted model still comes from training patients only. Intervals are paired patient-bootstrap 95% CIs (2,000 draws, `RandomState(0)`), and counts are repeat means.

Aggregates are in `results/paper_final/explore_E3/`:
- `v_*.json`: one variant under P1 and R49;
- `mem_*.json`: one variant inside the round-9 memory rules;
- `inventory.json`: the stored features;
- `diag_endoscopy_size.json`: the samples-per-endoscopy diagnostic.

Tables are printed by `scripts/paper_plan/ex_e3_render.py`. The figure is `paper/figures_explore_E3/e3_np_flagged_vs_R49.png` (local, not committed).

### Checks

- **Refit reproduces the stored model.** `ex_e3_refit.R` on the stored `img_mean.csv` matches the stored L-IMG exactly: maximum absolute difference 0.0 for the outer predictions and 0.0 for the inner out-of-fold predictions.
- **Rebuilt mean embedding matches.** The mean embedding rebuilt from the npz tiles matches `img_mean.csv` to 5.9e-8.
- **Round 8 reproduces.** The scoring code gives R49 31.1 caught / 31.8 non-progressors (NP) flagged and P1 90% 31.1 / 36.0.
- **Round 9 reproduces.** The memory engine gives the R49-aligned gate score with exponentially weighted (EW) memory at 30.7 / 23.6, and H&E-alone EW memory at 31.2 / 32.1.
- **Tile-score pooling.** The mean of tile logits equals the slide-mean model (relative difference 1.4e-6).
- **Tile-score fix.** The first tile-score run was degenerate: 95% of max-tile probabilities were 1.0, so most scores tied. Pooled tile logits are now mapped onto the slide-mean logit scale by an affine map fitted on each fit's training samples. Ranks are unchanged.

### Inventory (stored features for the 683 slides of the 676 samples)

| Source | Scale | Tiles per sample (median) | Dim | Coverage |
|---|---|---|---|---|
| UNI2-h level 2 (current) | ~0.88 µm/px | 256 sampled per slide | 1536 | 676 / 676 |
| UNI2-h level 1 | ~0.44 µm/px | 256 | 1536 | 676 |
| Prov-GigaPath levels 1 / 2 / 3 | 0.44 / 0.88 / 1.77 µm/px | 256 (level 2 = same tiles as UNI2-h) | 1536 | 676 |
| Virchow2 level 2 | ~0.88 µm/px | 256 (other tile draw) | 2560 | 676 |
| H-optimus-0, Virchow2, CTransPath (TRIDENT) | 20×, 0.5 µm/px, all tissue | 1,039 (50 to 17,475) | 1536 / 2560 / 768 | 675 (1 slide missing; imputed) |
| CONCH v1.5 (TRIDENT, 448 px) | 20× | 302 | 768 | 675 |
| MUSK (TRIDENT, 384 px) | 20× | 394 | 1024 | 675 |

Not used:
- UNI2-h level 3: only 58% of slides.
- `SWGCohort/features_uni2h_05um`: 465 of 683 slides.
- CONCH runs on the SWG slides: zero-shot outputs, not embeddings.

Stored npz coordinates are tile centres; they were not needed, because only pooling was done.

### 1. A better sample-level model? No.

None of the following beat the current UNI2-h level-2 mean, on sample AUROC (0.847) or on P1 non-progressors flagged:
- other poolings;
- other scales;
- other extractors;
- concatenations;
- ensembles;
- the nested per-fold choice.

| Variant | Sample AUROC | P1 90%: caught / NP flagged | R49 rebuilt: caught / NP |
|---|---|---|---|
| Current (UNI2-h L2 mean) | 0.847 | 31.1 / 36.0 | 31.1 / 31.8 |
| Pooling: mean+SD / quantiles / max / top-k by norm | 0.784 / 0.837 / 0.678 / 0.64 to 0.72 | 39.7 / 37.6 / 42.2 / 40.3 to 42.7 NP | 35.9 / 32.8 / 36.6 / 35.3 to 38.6 NP |
| Tile-score pooling (max, top 8 / 16 / 32) | 0.742 to 0.835 | 38.4 to 41.4 NP | 34.5 to 38.8 NP |
| UNI2-h level 1 / concat L1+L2 | 0.819 / 0.828 | 37.6 / 37.7 NP | 31.3 / 32.0 NP |
| Other extractors (GigaPath, Virchow2, H-optimus-0, CONCH, CTransPath, MUSK) | 0.744 to 0.838 | 37.4 to 42.2 NP | 32.1 to 35.3 NP |
| Probability ensembles (2 to 6 extractors) | 0.839 to 0.855 | 36.3 to 37.2 NP | 31.1 to 32.2 NP |
| Nested choice per fold (inner OOF AUROC, 9 or 11 candidates) | 0.816 / 0.819 | 37.4 / 37.2 NP | 32.3 / 32.4 NP |

Attention-MIL was not run, by the brief's own priority: it scored 0.778 before.

The nested choice is the honest version of "pick the best extractor", and it is worse than the current model. Inner-fold AUROC differences between extractors are mostly noise at 75 patients.

### 2. Endoscopy aggregation matters more than the extractor

The current rule scores an endoscopy by the **maximum** over its samples. Using the **mean sample logit** instead needs no refit, and the threshold rule is unchanged (90% training endoscopy sensitivity, inner out-of-fold predictions):
- endoscopy AUROC 0.837 → **0.863** (Δ +0.026 [+0.000, +0.054]);
- P1 90%: **31.2 caught / 32.2 NP flagged**, against 31.1 / 36.0. Δ NP −3.8 [−7.3, −0.7]; Δ caught +0.1 [−0.6, +0.9]; endoscopy specificity +0.078 [+0.029, +0.127].

Against R49:
- H&E alone with the mean logit, matched to R49's endoscopy sensitivity, flags +1.1 [−3.0, +5.1] more NP patients than R49.
- With the current score the same contrast is +5.0 [+1.1, +8.7] (round 8b S1).
- So most of R49's false-flag advantage over P1 comes from the max-over-samples rule, not from sequencing.

Rebuilding R49 on the mean logit, with the same cut-off rules, gives 30.9 / 31.2:
- Δ NP −0.6 [−2.1, +1.0];
- Δ caught −0.2 [−0.7, +0.0];
- **1.43 samples sequenced per patient instead of 1.94 (−26%)**.

Other aggregations behave similarly; the mean logit is the simplest and among the best:

| Aggregation | P1 90%: caught / NP | R49 rebuilt: caught / NP |
|---|---|---|
| Model applied to the endoscopy-pooled embedding | 31.2 / 32.2 | 30.9 / 31.3 |
| Median logit | 31.3 / 33.1 | 30.9 / 31.1 |
| Mean probability | 31.2 / 33.5 | 30.8 / 31.5 |
| Mean of top-2 logits | 31.2 / 34.0 | 30.8 / 30.6 |

**Why.** Non-progressor endoscopies have more samples (2.05 against 1.83 per endoscopy). Under the max rule, P1 specificity falls with the number of samples: 0.59 with 1 sample, 0.56 with 2, 0.43 with 3 and 0.32 with 4 or more. Under the mean logit it is 0.51, 0.66, 0.73 and 0.66. More biopsies should not make a non-progressor look riskier.

With mean-logit aggregation, ensembles reach the highest endoscopy AUROC: UNI2-h + H-optimus-0 + Virchow2 20× + GigaPath reaches 0.873 (+0.035 [+0.002, +0.069]). Its flag counts are no better than the UNI2-h mean logit alone (P1 31.0 / 32.8).

Apparent (optimistic; P1 threshold set on the evaluated endoscopies at 90% sensitivity): NP flagged 33.4 with the mean logit, against 36.8 with the current score.

### 3. Inside the round-9 memory rule

The round-9 nested engine was used unchanged, with the new score. It selects the half-life (1, 2 or 4 years) by the lowest training NP flagged, at the threshold that matches R49's training progressor-patient detection.

| Rule | Score | Caught | NP flagged | Samples seq. / patient | Δ NP vs R49 | Δ caught vs R49 | Δ NP vs same rule, current score |
|---|---|---|---|---|---|---|---|
| H&E alone, EW memory | current (round 9) | 31.2 | 32.1 | 0 | +0.3 [−2.7, +3.4] | +0.1 [−1.2, +1.7] | reference |
| **H&E alone, EW memory** | **mean logit** | **31.0** | **26.6** | **0** | **−5.2 [−8.2, −2.4]** | **−0.1 [−1.2, +0.9]** | **−5.5 [−8.7, −2.7]** |
| Gate score (R49-aligned), EW memory | current (round 9) | 30.7 | 23.6 | 1.94 | −8.2 [−11.4, −5.1] | −0.4 [−1.3, +0.4] | reference |
| Gate score (R49-aligned), EW memory | mean logit | 30.5 | 22.6 | 1.43 | −9.2 [−12.4, −6.0] | −0.6 [−1.5, +0.0] | −1.0 [−3.4, +1.2] |
| Gate score, EW memory (post hoc best of 14) | mean logit, concat UNI2-h + GigaPath L2 | 30.3 | 19.8 | 1.41 | −12.0 [−15.5, −8.5] | −0.8 [−1.6, −0.1] | −3.8 [−6.5, −1.3] |

Reading the table:
- **H&E alone + mean logit + EW memory** catches as many progressors as R49 and flags about 5 fewer non-progressors, **without any sequencing**.
- **Inside the gate**, the mean logit keeps round 9's gain (−1.0 NP, not significant) with 26% less sequencing.
- **The post hoc concat row** is the best of 14 scores tried in the memory rule and should not be quoted as a result without new data.

### Ranked summary (against R49 31.1 / 31.8 and P1 31.1 / 36.0; nested unless stated)

| Rank | Rule (E3 change) | Caught | NP flagged | Δ NP vs R49 | Δ NP vs P1 90% | Samples seq. / patient |
|---|---|---|---|---|---|---|
| 1 | Gate memory + mean logit, concat UNI2-h + GigaPath (post hoc, optimistic) | 30.3 | 19.8 | −12.0 [−15.5, −8.5] | −16.2 | 1.41 |
| 2 | Gate memory + mean logit (UNI2-h, current model) | 30.5 | 22.6 | −9.2 [−12.4, −6.0] | −13.4 | 1.43 |
| 3 | **H&E alone + mean logit + EW memory** | 31.0 | 26.6 | −5.2 [−8.2, −2.4] | −9.4 | **0** |
| 4 | R49 rebuilt on the mean logit | 30.9 | 31.2 | −0.6 [−2.1, +1.0] | −4.8 | 1.43 |
| 5 | P1 90% on the mean logit | 31.2 | 32.2 | +0.4 | −3.8 [−7.3, −0.7] | 0 |
| — | Best new extractor or pooling alone (P1 90%) | 30.7 to 31.5 | ≥ 35.8 | ≥ +4.0 | ≥ −0.2 | 0 |

### All variants (P1 and R49, nested)

| Variant | AUROC sample / endoscopy / patient | Δ endoscopy AUROC [95% CI] | P1 90%: caught / NP flagged | Δ NP vs P1 (current) | P1 matched to R49 sens.: Δ NP vs R49 | Δ spec. vs R49 (matched) | R49 rebuilt: caught / NP / seq. per patient | Δ NP vs R49 | Δ caught vs R49 | Apparent P1 NP (optimistic) |
|---|---|---|---|---|---|---|---|---|---|---|
| [mean logit] concat UNI2-h + GigaPath L2 | 0.878 / 0.844 / 0.832 | +0.006 [-0.032, +0.048] | 31.0 / 30.4 | -5.6 [-9.1, -2.4] | +0.6 [-4.2, +4.8] | -0.003 [-0.109, +0.115] | 31.2 / 29.3 / 1.41 | -2.5 [-4.5, -0.4] | +0.1 [-0.4, +0.7] | 32.6 |
| [mean logit] ensemble UNI2-h L2 + GigaPath L2 | 0.885 / 0.858 / 0.836 | +0.021 [-0.013, +0.056] | 30.9 / 31.6 | -4.4 [-7.8, -1.4] | -0.1 [-3.7, +3.8] | +0.026 [-0.069, +0.121] | 31.1 / 29.6 / 1.44 | -2.2 [-4.5, +0.0] | +0.0 [-0.4, +0.4] | 32.0 |
| [mean logit] UNI2-h L2 | 0.890 / 0.863 / 0.854 | +0.026 [+0.000, +0.054] | 31.2 / 32.2 | -3.8 [-7.3, -0.7] | +1.1 [-3.0, +5.1] | +0.019 [-0.079, +0.130] | 30.9 / 31.2 / 1.43 | -0.6 [-2.1, +1.0] | -0.2 [-0.7, +0.0] | 33.4 |
| [pooled-embedding endoscopy] UNI2-h L2 | 0.890 / 0.863 / 0.854 | +0.026 [+0.001, +0.054] | 31.2 / 32.2 | -3.8 [-7.3, -0.7] | +1.2 [-2.9, +5.1] | +0.019 [-0.080, +0.130] | 30.9 / 31.3 / 1.44 | -0.5 [-2.1, +1.1] | -0.2 [-0.7, +0.0] | 33.4 |
| [mean logit] concat UNI2-h L1 + L2 | 0.874 / 0.843 / 0.835 | +0.005 [-0.029, +0.042] | 30.5 / 32.5 | -3.5 [-7.2, +0.1] | +2.6 [-2.0, +7.0] | -0.049 [-0.166, +0.074] | 30.8 / 30.5 / 1.52 | -1.3 [-3.8, +1.6] | -0.3 [-1.8, +0.6] | 34.7 |
| [mean logit] ensemble UNI2-h L2 + UNI2-h L1 | 0.890 / 0.866 / 0.857 | +0.029 [-0.002, +0.063] | 30.7 / 32.7 | -3.3 [-7.1, +0.3] | +1.3 [-3.0, +5.6] | +0.024 [-0.097, +0.135] | 30.9 / 30.5 / 1.35 | -1.3 [-4.1, +1.8] | -0.2 [-1.4, +0.7] | 33.5 |
| [mean logit] ensemble UNI2-h L2 + H-optimus-0 20x + Virchow2 20x + GigaPath L2 | 0.902 / 0.873 / 0.853 | +0.035 [+0.002, +0.069] | 31.0 / 32.8 | -3.2 [-6.6, +0.0] | +1.7 [-4.0, +6.1] | +0.044 [-0.078, +0.155] | 31.2 / 30.7 / 1.31 | -1.1 [-4.1, +1.9] | +0.1 [-1.0, +1.1] | 33.3 |
| [median logit] UNI2-h L2 | 0.875 / 0.855 / 0.846 | +0.018 [-0.013, +0.049] | 31.3 / 33.1 | -2.9 [-5.7, -0.3] | +1.7 [-2.2, +5.9] | -0.006 [-0.109, +0.098] | 30.9 / 31.1 / 1.56 | -0.7 [-2.3, +0.9] | -0.2 [-0.7, +0.0] | 34.7 |
| [mean logit] nested choice among UNI2-h L2 + UNI2-h L1 + GigaPath L1 + GigaPath L2 + GigaPath L3 + Virchow2 L2 + CONCH 20x + MUSK 20x + concat UNI2-h L1 + L2 + concat GigaPath L1 + L2 + L3 + concat UNI2-h + GigaPath L2 | 0.861 / 0.825 / 0.830 | -0.012 [-0.043, +0.021] | 30.8 / 33.3 | -2.7 [-6.2, +0.4] | +3.3 [-0.5, +7.0] | -0.078 [-0.158, +0.026] | 30.9 / 31.6 / 1.49 | -0.2 [-2.0, +1.7] | -0.2 [-0.9, +0.3] | 35.1 |
| [mean prob.] UNI2-h L2 | 0.879 / 0.852 / 0.828 | +0.015 [-0.008, +0.037] | 31.2 / 33.5 | -2.5 [-4.5, -0.7] | +1.2 [-2.5, +5.9] | +0.001 [-0.113, +0.111] | 30.8 / 31.5 / 1.42 | -0.3 [-2.0, +1.3] | -0.3 [-1.3, +0.3] | 34.1 |
| [mean logit] ensemble UNI2-h L2 + UNI2-h L1 + GigaPath L2 + Virchow2 L2 + CONCH 20x + MUSK 20x | 0.889 / 0.854 / 0.826 | +0.017 [-0.022, +0.054] | 30.9 / 33.8 | -2.2 [-5.9, +1.3] | +1.1 [-4.3, +6.3] | +0.028 [-0.136, +0.139] | 31.1 / 29.9 / 1.45 | -1.9 [-5.1, +1.4] | +0.0 [-1.4, +1.1] | 32.2 |
| [top-2 logit] UNI2-h L2 | 0.871 / 0.850 / 0.853 | +0.013 [-0.003, +0.030] | 31.2 / 34.0 | -2.0 [-4.0, -0.3] | +1.9 [-1.7, +6.6] | -0.018 [-0.125, +0.097] | 30.8 / 30.6 / 1.60 | -1.2 [-2.6, -0.2] | -0.3 [-1.0, +0.0] | 34.7 |
| [pooled-embedding endoscopy] UNI2-h L1 | 0.859 / 0.832 / 0.838 | -0.006 [-0.047, +0.041] | 30.8 / 34.4 | -1.6 [-5.7, +2.3] | +4.0 [-1.0, +8.9] | -0.082 [-0.237, +0.055] | 30.6 / 30.9 / 1.62 | -0.9 [-4.0, +2.7] | -0.5 [-2.5, +0.7] | 35.8 |
| [mean logit] ensemble UNI2-h L2 + H-optimus-0 20x | 0.886 / 0.861 / 0.837 | +0.023 [-0.004, +0.051] | 31.2 / 34.4 | -1.6 [-4.1, +0.6] | +3.0 [-2.1, +7.2] | -0.004 [-0.109, +0.110] | 31.3 / 31.3 / 1.50 | -0.5 [-2.9, +2.0] | +0.2 [-0.5, +1.0] | 34.9 |
| [mean logit] UNI2-h L1 | 0.860 / 0.832 / 0.838 | -0.005 [-0.047, +0.041] | 30.8 / 34.4 | -1.6 [-5.7, +2.3] | +4.0 [-1.0, +8.9] | -0.080 [-0.235, +0.058] | 30.6 / 30.9 / 1.61 | -0.9 [-4.1, +2.7] | -0.5 [-2.5, +0.7] | 35.8 |
| [mean logit] Virchow2 20x | 0.879 / 0.850 / 0.833 | +0.013 [-0.033, +0.057] | 30.7 / 34.9 | -1.1 [-5.1, +2.9] | +4.3 [-2.2, +10.2] | -0.063 [-0.248, +0.116] | 31.5 / 31.9 / 1.51 | +0.1 [-4.6, +5.1] | +0.4 [-1.2, +2.1] | 37.1 |
| [pooled-embedding endoscopy] Virchow2 L2 | 0.868 / 0.825 / 0.804 | -0.013 [-0.068, +0.038] | 31.4 / 35.4 | -0.6 [-3.8, +2.5] | +4.1 [-3.2, +10.5] | -0.054 [-0.329, +0.123] | 31.2 / 33.1 / 1.74 | +1.3 [-2.6, +5.3] | +0.1 [-0.6, +0.9] | 36.4 |
| [mean logit] Virchow2 L2 | 0.868 / 0.825 / 0.803 | -0.013 [-0.068, +0.038] | 31.4 / 35.4 | -0.6 [-3.8, +2.5] | +4.1 [-3.2, +10.5] | -0.055 [-0.329, +0.123] | 31.2 / 33.2 / 1.74 | +1.4 [-2.5, +5.4] | +0.1 [-0.6, +0.9] | 36.4 |
| [mean logit] GigaPath L2 | 0.839 / 0.805 / 0.801 | -0.033 [-0.084, +0.015] | 31.0 / 35.5 | -0.5 [-3.6, +2.4] | +5.1 [+1.0, +9.2] | -0.104 [-0.232, -0.005] | 30.9 / 31.9 / 1.71 | +0.1 [-2.4, +2.9] | -0.2 [-1.0, +0.4] | 37.2 |
| concat UNI2-h + GigaPath L2 | 0.832 / 0.824 / 0.843 | -0.013 [-0.042, +0.018] | 31.5 / 35.8 | -0.2 [-1.9, +1.6] | +5.0 [-0.6, +9.0] | -0.085 [-0.208, +0.070] | 31.4 / 31.7 / 1.96 | -0.1 [-2.1, +1.9] | +0.3 [+0.0, +0.8] | 36.6 |
| current L-IMG (stored) | 0.847 / 0.837 / 0.851 | +0.000 [+0.000, +0.000] | 31.1 / 36.0 | +0.0 [+0.0, +0.0] | +5.0 [+1.1, +8.7] | -0.068 [-0.165, +0.038] | 31.1 / 31.8 / 1.94 | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | 36.8 |
| ensemble UNI2-h L2 + UNI2-h L1 + GigaPath L2 + Virchow2 L2 + CONCH 20x + MUSK 20x | 0.843 / 0.828 / 0.829 | -0.010 [-0.041, +0.018] | 30.7 / 36.3 | +0.3 [-2.1, +2.3] | +4.4 [+0.3, +9.1] | -0.065 [-0.197, +0.033] | 31.5 / 31.1 / 2.03 | -0.7 [-3.3, +1.8] | +0.4 [+0.0, +0.9] | 36.1 |
| ensemble UNI2-h L2 + UNI2-h L1 | 0.845 / 0.836 / 0.860 | -0.001 [-0.020, +0.018] | 31.0 / 36.4 | +0.4 [-0.9, +1.9] | +4.6 [+0.2, +8.3] | -0.068 [-0.179, +0.042] | 31.3 / 31.4 / 1.93 | -0.4 [-2.7, +2.2] | +0.2 [-0.2, +0.7] | 36.6 |
| ensemble UNI2-h L2 + H-optimus-0 20x + Virchow2 20x + GigaPath L2 | 0.855 / 0.844 / 0.824 | +0.007 [-0.024, +0.034] | 31.0 / 36.6 | +0.6 [-1.2, +2.3] | +4.9 [+1.0, +9.4] | -0.062 [-0.199, +0.049] | 31.5 / 32.2 / 1.94 | +0.4 [-1.5, +2.5] | +0.4 [+0.0, +0.9] | 36.9 |
| ensemble UNI2-h L2 + GigaPath L2 | 0.840 / 0.833 / 0.819 | -0.005 [-0.031, +0.021] | 31.1 / 36.8 | +0.8 [-1.1, +2.9] | +5.0 [+1.3, +8.6] | -0.065 [-0.170, +0.036] | 31.2 / 32.0 / 1.98 | +0.2 [-1.6, +2.1] | +0.1 [-0.2, +0.5] | 36.9 |
| ensemble UNI2-h L2 + H-optimus-0 20x | 0.839 / 0.837 / 0.826 | -0.001 [-0.027, +0.024] | 30.9 / 37.2 | +1.2 [-0.0, +2.7] | +5.4 [+1.4, +9.5] | -0.083 [-0.190, +0.032] | 31.3 / 32.1 / 2.08 | +0.3 [-1.3, +2.0] | +0.2 [+0.0, +0.5] | 37.2 |
| nested choice among UNI2-h L2 + UNI2-h L1 + GigaPath L1 + GigaPath L2 + GigaPath L3 + Virchow2 L2 + CONCH 20x + MUSK 20x + concat UNI2-h L1 + L2 + concat GigaPath L1 + L2 + L3 + concat UNI2-h + GigaPath L2 | 0.819 / 0.799 / 0.823 | -0.039 [-0.066, -0.015] | 31.2 / 37.2 | +1.2 [+0.2, +2.3] | +6.6 [+2.8, +10.4] | -0.150 [-0.243, -0.042] | 31.3 / 32.4 / 1.96 | +0.6 [-0.7, +2.0] | +0.2 [+0.0, +0.5] | 38.6 |
| [mean logit] GigaPath L1 | 0.863 / 0.810 / 0.807 | -0.028 [-0.069, +0.014] | 31.3 / 37.3 | +1.3 [-3.0, +5.5] | +6.2 [+1.4, +10.7] | -0.148 [-0.264, -0.036] | 31.2 / 33.0 / 1.90 | +1.2 [-2.1, +4.8] | +0.1 [-1.0, +1.5] | 38.2 |
| nested choice among UNI2-h L2 + UNI2-h L1 + GigaPath L2 + Virchow2 L2 + H-optimus-0 20x + Virchow2 20x + CONCH 20x + CTransPath 20x + MUSK 20x | 0.816 / 0.800 / 0.824 | -0.037 [-0.067, -0.010] | 31.2 / 37.4 | +1.4 [-0.1, +3.2] | +6.7 [+2.3, +10.6] | -0.137 [-0.248, -0.024] | 31.3 / 32.3 / 1.97 | +0.5 [-1.8, +2.9] | +0.2 [+0.0, +0.5] | 38.4 |
| Virchow2 20x | 0.838 / 0.817 / 0.812 | -0.020 [-0.069, +0.026] | 30.8 / 37.4 | +1.4 [-1.3, +4.5] | +6.6 [+1.4, +11.2] | -0.114 [-0.269, +0.017] | 32.0 / 32.1 / 1.89 | +0.3 [-4.2, +5.0] | +0.9 [+0.0, +2.3] | 38.1 |
| UNI2-h L1 | 0.819 / 0.807 / 0.843 | -0.030 [-0.064, +0.007] | 31.1 / 37.6 | +1.6 [-0.2, +4.0] | +6.6 [+1.9, +10.6] | -0.141 [-0.281, -0.012] | 31.3 / 31.3 / 2.01 | -0.5 [-3.7, +3.0] | +0.2 [-0.4, +0.8] | 37.9 |
| UNI2-h L2 pooled q3 | 0.837 / 0.844 / 0.848 | +0.007 [-0.022, +0.037] | 31.0 / 37.6 | +1.6 [-0.1, +3.6] | +4.2 [+0.7, +9.1] | -0.039 [-0.216, +0.054] | 31.4 / 32.8 / 2.25 | +1.0 [-0.4, +2.4] | +0.3 [+0.0, +0.8] | 36.6 |
| concat UNI2-h L1 + L2 | 0.828 / 0.816 / 0.846 | -0.022 [-0.045, +0.001] | 30.7 / 37.7 | +1.7 [+0.0, +3.6] | +5.5 [+1.6, +9.8] | -0.130 [-0.245, -0.004] | 31.4 / 32.0 / 1.96 | +0.2 [-2.1, +2.7] | +0.3 [-0.1, +0.9] | 37.4 |
| [mean logit] H-optimus-0 20x | 0.834 / 0.812 / 0.774 | -0.026 [-0.080, +0.024] | 30.5 / 38.3 | +2.3 [+0.2, +4.6] | +7.0 [+0.7, +11.6] | -0.160 [-0.338, +0.038] | 30.5 / 34.7 / 2.04 | +2.9 [-0.9, +6.8] | -0.6 [-2.5, +1.1] | 38.7 |
| tile-score pooling of the current model: top32 | 0.835 / 0.806 / 0.780 | -0.031 [-0.067, +0.003] | 30.6 / 38.4 | +2.4 [-0.3, +5.6] | +7.5 [+3.0, +11.8] | -0.160 [-0.303, -0.001] | 31.0 / 34.5 / 1.94 | +2.7 [-0.1, +5.7] | -0.1 [-0.7, +0.5] | 39.1 |
| [mean logit] MUSK 20x | 0.778 / 0.741 / 0.743 | -0.096 [-0.158, -0.039] | 30.8 / 38.7 | +2.7 [+0.2, +5.5] | +8.7 [+3.8, +13.0] | -0.272 [-0.412, -0.097] | 30.6 / 34.3 / 2.07 | +2.5 [-0.9, +6.1] | -0.5 [-2.1, +0.8] | 40.6 |
| tile-score pooling of the current model: top16 | 0.822 / 0.788 / 0.758 | -0.050 [-0.088, -0.011] | 30.6 / 38.9 | +2.9 [+0.4, +6.0] | +7.8 [+3.5, +12.2] | -0.182 [-0.333, -0.027] | 31.0 / 36.0 / 1.97 | +4.2 [+1.1, +7.5] | -0.1 [-0.9, +0.6] | 39.5 |
| GigaPath L2 | 0.796 / 0.777 / 0.785 | -0.061 [-0.110, -0.012] | 31.2 / 39.3 | +3.3 [+0.9, +6.1] | +7.3 [+3.9, +11.9] | -0.181 [-0.301, -0.097] | 31.0 / 33.9 / 2.10 | +2.1 [-0.8, +5.3] | -0.1 [-0.9, +0.4] | 39.5 |
| H-optimus-0 20x | 0.784 / 0.790 / 0.758 | -0.047 [-0.109, +0.008] | 31.2 / 39.3 | +3.3 [+1.1, +6.1] | +7.2 [+2.4, +12.5] | -0.193 [-0.384, +0.008] | 31.5 / 35.2 / 2.36 | +3.4 [-0.5, +7.3] | +0.4 [-0.5, +1.7] | 39.1 |
| Virchow2 L2 | 0.805 / 0.786 / 0.772 | -0.052 [-0.108, -0.005] | 31.4 / 39.5 | +3.5 [+1.1, +6.4] | +8.4 [+1.9, +12.9] | -0.170 [-0.391, +0.029] | 31.5 / 34.9 / 2.19 | +3.1 [-0.9, +7.0] | +0.4 [-0.1, +1.0] | 40.2 |
| tile-score pooling of the current model: top8 | 0.804 / 0.771 / 0.747 | -0.067 [-0.108, -0.026] | 31.2 / 39.6 | +3.6 [+1.0, +6.8] | +8.2 [+4.4, +12.9] | -0.188 [-0.358, -0.063] | 30.9 / 37.4 / 1.98 | +5.6 [+2.6, +8.9] | -0.2 [-1.2, +0.5] | 40.1 |
| UNI2-h L2 pooled meansd | 0.784 / 0.783 / 0.796 | -0.055 [-0.098, -0.014] | 31.3 / 39.7 | +3.7 [+1.2, +6.8] | +8.3 [+3.8, +12.3] | -0.199 [-0.325, -0.049] | 31.2 / 35.9 / 2.33 | +4.1 [+1.2, +7.0] | +0.1 [-0.2, +0.5] | 40.0 |
| UNI2-h L2 pooled top32n | 0.721 / 0.689 / 0.682 | -0.148 [-0.212, -0.089] | 31.3 / 40.3 | +4.3 [+1.3, +7.8] | +9.2 [+4.8, +13.6] | -0.322 [-0.427, -0.186] | 31.4 / 35.3 / 2.13 | +3.5 [-1.1, +7.9] | +0.3 [-0.9, +1.8] | 41.1 |
| concat GigaPath L1 + L2 + L3 | 0.801 / 0.772 / 0.803 | -0.065 [-0.111, -0.025] | 31.3 / 40.5 | +4.5 [+1.5, +8.1] | +9.5 [+4.4, +13.4] | -0.258 [-0.351, -0.104] | 31.5 / 32.5 / 2.27 | +0.7 [-2.3, +3.9] | +0.4 [+0.0, +0.9] | 41.6 |
| GigaPath L1 | 0.812 / 0.778 / 0.810 | -0.059 [-0.107, -0.014] | 31.9 / 40.5 | +4.5 [+1.7, +7.8] | +9.1 [+4.4, +13.2] | -0.228 [-0.339, -0.102] | 31.8 / 34.3 / 2.21 | +2.5 [-1.0, +6.2] | +0.7 [-0.1, +2.1] | 41.2 |
| [mean logit] CONCH 20x | 0.795 / 0.774 / 0.747 | -0.064 [-0.122, -0.007] | 31.4 / 40.7 | +4.7 [+0.6, +9.5] | +8.6 [+3.7, +13.6] | -0.217 [-0.357, -0.081] | 31.7 / 35.4 / 2.18 | +3.6 [-1.1, +8.1] | +0.6 [-0.6, +2.2] | 40.5 |
| MUSK 20x | 0.744 / 0.711 / 0.705 | -0.126 [-0.189, -0.068] | 30.7 / 40.9 | +4.9 [+2.3, +8.2] | +10.2 [+5.7, +14.5] | -0.333 [-0.452, -0.168] | 31.1 / 35.3 / 2.25 | +3.5 [+0.2, +6.8] | +0.0 [-1.0, +1.1] | 42.0 |
| [mean logit] CTransPath 20x | 0.830 / 0.813 / 0.758 | -0.024 [-0.090, +0.037] | 30.8 / 41.2 | +5.2 [+1.9, +9.3] | +9.3 [+0.5, +13.8] | -0.168 [-0.357, +0.091] | 31.2 / 33.1 / 2.09 | +1.3 [-2.9, +5.2] | +0.1 [-1.4, +1.7] | 41.6 |
| tile-score pooling of the current model: max | 0.742 / 0.703 / 0.675 | -0.134 [-0.181, -0.084] | 31.6 / 41.4 | +5.4 [+2.5, +8.9] | +10.3 [+6.0, +14.7] | -0.321 [-0.431, -0.183] | 31.6 / 38.8 / 2.18 | +7.0 [+3.6, +10.9] | +0.5 [-0.7, +2.1] | 42.2 |
| CTransPath 20x | 0.785 / 0.789 / 0.747 | -0.048 [-0.111, +0.009] | 31.3 / 41.7 | +5.7 [+2.5, +9.7] | +9.4 [+2.4, +13.8] | -0.194 [-0.412, +0.045] | 31.9 / 33.7 / 2.45 | +1.9 [-1.9, +5.7] | +0.8 [+0.0, +2.0] | 41.6 |
| GigaPath L3 | 0.776 / 0.769 / 0.790 | -0.068 [-0.122, -0.015] | 31.7 / 41.9 | +5.9 [+2.5, +10.3] | +9.4 [+3.7, +13.7] | -0.183 [-0.333, -0.031] | 32.0 / 34.5 / 2.35 | +2.7 [+0.1, +5.3] | +0.9 [+0.0, +2.3] | 41.3 |
| UNI2-h L2 pooled max | 0.678 / 0.683 / 0.712 | -0.154 [-0.216, -0.091] | 31.1 / 42.2 | +6.2 [+3.0, +10.2] | +10.7 [+6.1, +15.1] | -0.400 [-0.502, -0.228] | 30.8 / 36.6 / 2.83 | +4.8 [+1.4, +8.3] | -0.3 [-2.0, +0.9] | 42.6 |
| CONCH 20x | 0.767 / 0.761 / 0.735 | -0.076 [-0.137, -0.016] | 31.5 / 42.2 | +6.2 [+2.1, +11.0] | +10.7 [+5.0, +15.4] | -0.252 [-0.380, -0.104] | 32.0 / 34.6 / 2.35 | +2.8 [-2.0, +7.2] | +0.9 [+0.0, +2.3] | 42.7 |
| UNI2-h L2 pooled top8n | 0.664 / 0.637 / 0.599 | -0.201 [-0.265, -0.135] | 30.9 / 42.5 | +6.5 [+2.9, +11.2] | +11.1 [+6.6, +15.7] | -0.421 [-0.516, -0.299] | 31.1 / 38.6 / 2.58 | +6.8 [+2.7, +11.3] | +0.0 [-1.3, +1.6] | 42.9 |
| UNI2-h L2 pooled top16n | 0.642 / 0.628 / 0.626 | -0.209 [-0.271, -0.145] | 30.8 / 42.7 | +6.7 [+3.2, +11.2] | +10.8 [+6.4, +15.3] | -0.446 [-0.535, -0.320] | 30.4 / 36.6 / 2.93 | +4.8 [+0.9, +9.0] | -0.7 [-1.6, +0.0] | 42.6 |

### All memory-rule runs (nested round-9 engine)

| Variant | Memory rule | Caught | NP flagged | Seq. / patient | Δ NP vs R49 | Δ caught vs R49 | Δ NP vs same rule, current L-IMG | Δ caught vs same rule | Δ endoscopy spec. vs R49 |
|---|---|---|---|---|---|---|---|---|---|
| [mean logit] concat UNI2-h + GigaPath L2 | gate score (R49-aligned), EW memory | 30.3 | 19.8 | 1.41 | -12.0 [-15.5, -8.5] | -0.8 [-1.6, -0.1] | -3.8 [-6.5, -1.3] | -0.4 [-1.4, +0.5] | +0.196 [+0.138, +0.257] |
| [mean logit] ensemble UNI2-h L2 + GigaPath L2 | gate score (R49-aligned), EW memory | 30.6 | 21.5 | 1.44 | -10.3 [-13.5, -7.3] | -0.5 [-1.3, +0.2] | -2.1 [-5.1, +0.7] | -0.1 [-1.0, +0.7] | +0.175 [+0.124, +0.229] |
| [median logit] UNI2-h L2 | gate score (R49-aligned), EW memory | 30.4 | 21.6 | 1.56 | -10.2 [-13.4, -6.9] | -0.7 [-1.6, +0.0] | -2.0 [-4.3, +0.1] | -0.3 [-1.0, +0.3] | +0.156 [+0.110, +0.204] |
| [mean logit] ensemble UNI2-h L2 + UNI2-h L1 | gate score (R49-aligned), EW memory | 30.0 | 21.8 | 1.35 | -10.0 [-13.8, -6.2] | -1.1 [-2.4, -0.2] | -1.8 [-4.8, +1.2] | -0.7 [-2.2, +0.6] | +0.193 [+0.142, +0.242] |
| [mean logit] concat UNI2-h L1 + L2 | gate score (R49-aligned), EW memory | 30.0 | 21.9 | 1.52 | -9.9 [-13.2, -6.5] | -1.1 [-2.6, +0.1] | -1.7 [-4.9, +1.6] | -0.7 [-2.3, +0.7] | +0.148 [+0.088, +0.210] |
| [mean logit] ensemble UNI2-h L2 + UNI2-h L1 + GigaPath L2 + Virchow2 L2 + CONCH 20x + MUSK 20x | gate score (R49-aligned), EW memory | 30.8 | 22.2 | 1.45 | -9.6 [-13.3, -5.9] | -0.3 [-1.5, +0.5] | -1.4 [-4.9, +2.1] | +0.1 [-1.3, +1.3] | +0.177 [+0.117, +0.242] |
| [mean logit] UNI2-h L2 | gate score (R49-aligned), EW memory | 30.5 | 22.6 | 1.43 | -9.2 [-12.4, -6.0] | -0.6 [-1.5, +0.0] | -1.0 [-3.4, +1.2] | -0.2 [-0.8, +0.4] | +0.144 [+0.106, +0.187] |
| [pooled-embedding endoscopy] UNI2-h L2 | gate score (R49-aligned), EW memory | 30.5 | 22.6 | 1.44 | -9.2 [-12.5, -6.1] | -0.6 [-1.5, +0.0] | -1.0 [-3.5, +1.3] | -0.2 [-0.8, +0.4] | +0.144 [+0.104, +0.187] |
| [mean logit] nested choice among UNI2-h L2 + UNI2-h L1 + GigaPath L1 + GigaPath L2 + GigaPath L3 + Virchow2 L2 + CONCH 20x + MUSK 20x + concat UNI2-h L1 + L2 + concat GigaPath L1 + L2 + L3 + concat UNI2-h + GigaPath L2 | gate score (R49-aligned), EW memory | 29.5 | 22.7 | 1.49 | -9.1 [-12.3, -5.9] | -1.6 [-2.8, -0.6] | -0.9 [-3.6, +1.6] | -1.2 [-2.3, -0.3] | +0.132 [+0.083, +0.180] |
| [top-2 logit] UNI2-h L2 | gate score (R49-aligned), EW memory | 30.4 | 23.2 | 1.60 | -8.6 [-11.8, -5.4] | -0.7 [-1.8, +0.2] | -0.4 [-2.2, +1.3] | -0.3 [-1.2, +0.5] | +0.149 [+0.110, +0.191] |
| ensemble UNI2-h L2 + UNI2-h L1 | gate score (R49-aligned), EW memory | 30.9 | 23.2 | 1.93 | -8.6 [-12.4, -4.9] | -0.2 [-0.8, +0.3] | -0.4 [-2.8, +2.1] | +0.2 [-0.5, +1.1] | +0.119 [+0.073, +0.165] |
| current L-IMG (stored) | gate score (R49-aligned), EW memory | 30.7 | 23.6 | 1.94 | -8.2 [-11.4, -5.1] | -0.4 [-1.3, +0.4] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | +0.096 [+0.058, +0.133] |
| [mean logit] ensemble UNI2-h L2 + H-optimus-0 20x + Virchow2 20x + GigaPath L2 | gate score (R49-aligned), EW memory | 29.7 | 24.0 | 1.31 | -7.8 [-11.1, -4.3] | -1.4 [-3.6, +0.0] | +0.4 [-2.5, +3.6] | -1.0 [-3.1, +0.6] | +0.157 [+0.099, +0.211] |
| [mean prob.] UNI2-h L2 | gate score (R49-aligned), EW memory | 30.1 | 24.1 | 1.42 | -7.7 [-10.8, -4.7] | -1.0 [-2.3, +0.0] | +0.5 [-1.6, +2.6] | -0.6 [-1.7, +0.3] | +0.126 [+0.090, +0.167] |
| [mean logit] ensemble UNI2-h L2 + UNI2-h L1 + GigaPath L2 + Virchow2 L2 + CONCH 20x + MUSK 20x | gate score, no memory | 30.7 | 26.1 | 1.45 | -5.7 [-9.0, -2.5] | -0.4 [-1.6, +0.4] | -3.3 [-6.4, -0.3] | +0.0 [-1.3, +1.1] | +0.155 [+0.105, +0.207] |
| [mean logit] ensemble UNI2-h L2 + H-optimus-0 20x + Virchow2 20x + GigaPath L2 | gate score, no memory | 30.0 | 26.5 | 1.31 | -5.3 [-8.1, -2.6] | -1.1 [-2.2, -0.2] | -2.9 [-5.2, -0.6] | -0.7 [-1.9, +0.3] | +0.161 [+0.116, +0.209] |
| [mean logit] ensemble UNI2-h L2 + GigaPath L2 | gate score, no memory | 30.4 | 26.7 | 1.44 | -5.1 [-7.2, -3.0] | -0.7 [-1.4, -0.1] | -2.7 [-4.3, -1.2] | -0.3 [-1.1, +0.7] | +0.156 [+0.116, +0.195] |
| ensemble UNI2-h L2 + UNI2-h L1 | gate score, no memory | 30.9 | 26.7 | 1.93 | -5.1 [-7.7, -2.5] | -0.2 [-0.6, +0.2] | -2.7 [-5.0, -0.5] | +0.2 [-0.3, +0.8] | +0.115 [+0.080, +0.151] |
| [mean logit] concat UNI2-h + GigaPath L2 | gate score, no memory | 30.9 | 26.7 | 1.41 | -5.1 [-7.2, -2.9] | -0.2 [-0.9, +0.5] | -2.7 [-4.3, -1.0] | +0.2 [-0.6, +1.1] | +0.135 [+0.096, +0.175] |
| [mean logit] ensemble UNI2-h L2 + UNI2-h L1 | gate score, no memory | 29.9 | 26.8 | 1.35 | -5.0 [-7.9, -1.8] | -1.2 [-2.5, -0.2] | -2.6 [-4.9, +0.2] | -0.8 [-2.1, +0.1] | +0.160 [+0.117, +0.204] |
| [top-2 logit] UNI2-h L2 | gate score, no memory | 30.0 | 27.4 | 1.60 | -4.4 [-6.4, -2.7] | -1.1 [-2.3, -0.2] | -2.0 [-3.6, -0.6] | -0.7 [-2.0, +0.5] | +0.151 [+0.117, +0.188] |
| [mean logit] concat UNI2-h L1 + L2 | gate score, no memory | 30.2 | 27.4 | 1.52 | -4.4 [-7.1, -1.4] | -0.9 [-2.3, +0.1] | -2.0 [-4.3, +0.8] | -0.5 [-2.0, +0.8] | +0.125 [+0.076, +0.174] |
| [mean logit] UNI2-h L2 | gate score, no memory | 30.4 | 28.2 | 1.43 | -3.6 [-5.3, -2.0] | -0.7 [-1.4, -0.2] | -1.2 [-2.6, +0.0] | -0.3 [-1.1, +0.6] | +0.135 [+0.105, +0.168] |
| [median logit] UNI2-h L2 | gate score, no memory | 30.4 | 28.2 | 1.56 | -3.6 [-5.4, -2.0] | -0.7 [-1.5, -0.1] | -1.2 [-2.5, +0.0] | -0.3 [-1.1, +0.6] | +0.139 [+0.106, +0.175] |
| [mean logit] nested choice among UNI2-h L2 + UNI2-h L1 + GigaPath L1 + GigaPath L2 + GigaPath L3 + Virchow2 L2 + CONCH 20x + MUSK 20x + concat UNI2-h L1 + L2 + concat GigaPath L1 + L2 + L3 + concat UNI2-h + GigaPath L2 | gate score, no memory | 29.9 | 28.2 | 1.49 | -3.6 [-5.6, -1.6] | -1.2 [-2.2, -0.3] | -1.2 [-2.9, +0.5] | -0.8 [-1.9, +0.1] | +0.119 [+0.085, +0.158] |
| [pooled-embedding endoscopy] UNI2-h L2 | gate score, no memory | 30.5 | 28.3 | 1.44 | -3.5 [-5.2, -1.9] | -0.6 [-1.2, -0.1] | -1.1 [-2.6, +0.2] | -0.2 [-0.9, +0.7] | +0.134 [+0.104, +0.167] |
| [mean prob.] UNI2-h L2 | gate score, no memory | 30.1 | 28.9 | 1.42 | -2.9 [-4.8, -1.3] | -1.0 [-2.0, -0.2] | -0.5 [-2.5, +1.1] | -0.6 [-1.8, +0.5] | +0.109 [+0.079, +0.147] |
| current L-IMG (stored) | gate score, no memory | 30.7 | 29.4 | 1.94 | -2.4 [-3.7, -1.3] | -0.4 [-1.2, +0.0] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | +0.089 [+0.069, +0.107] |
| [mean logit] concat UNI2-h + GigaPath L2 | H&E alone, EW memory | 30.4 | 25.2 | 0.00 | -6.6 [-9.9, -3.3] | -0.7 [-1.5, +0.1] | -6.9 [-10.4, -3.5] | -0.8 [-2.4, +0.3] | +0.059 [-0.008, +0.133] |
| [mean logit] ensemble UNI2-h L2 + H-optimus-0 20x + Virchow2 20x + GigaPath L2 | H&E alone, EW memory | 30.3 | 25.5 | 0.00 | -6.3 [-10.4, -2.0] | -0.8 [-3.1, +0.9] | -6.6 [-10.6, -2.4] | -0.9 [-2.5, +0.4] | +0.113 [+0.037, +0.196] |
| [mean logit] ensemble UNI2-h L2 + UNI2-h L1 | H&E alone, EW memory | 30.4 | 26.5 | 0.00 | -5.3 [-9.4, -0.8] | -0.7 [-3.2, +0.9] | -5.6 [-9.6, -1.8] | -0.8 [-2.6, +0.4] | +0.069 [-0.005, +0.140] |
| [mean logit] UNI2-h L2 | H&E alone, EW memory | 31.0 | 26.6 | 0.00 | -5.2 [-8.2, -2.4] | -0.1 [-1.2, +0.9] | -5.5 [-8.7, -2.7] | -0.2 [-1.1, +0.5] | +0.027 [-0.042, +0.102] |
| [pooled-embedding endoscopy] UNI2-h L2 | H&E alone, EW memory | 31.0 | 26.6 | 0.00 | -5.2 [-8.2, -2.4] | -0.1 [-1.2, +0.9] | -5.5 [-8.7, -2.7] | -0.2 [-1.1, +0.5] | +0.024 [-0.045, +0.100] |
| [mean logit] concat UNI2-h L1 + L2 | H&E alone, EW memory | 30.4 | 26.6 | 0.00 | -5.2 [-8.8, -1.3] | -0.7 [-2.7, +0.6] | -5.5 [-9.1, -1.8] | -0.8 [-2.4, +0.4] | +0.043 [-0.031, +0.116] |
| [mean prob.] UNI2-h L2 | H&E alone, EW memory | 30.5 | 26.8 | 0.00 | -5.0 [-7.8, -2.2] | -0.6 [-2.4, +0.7] | -5.3 [-7.6, -3.1] | -0.7 [-1.9, +0.3] | +0.057 [-0.000, +0.120] |
| [mean logit] nested choice among UNI2-h L2 + UNI2-h L1 + GigaPath L1 + GigaPath L2 + GigaPath L3 + Virchow2 L2 + CONCH 20x + MUSK 20x + concat UNI2-h L1 + L2 + concat GigaPath L1 + L2 + L3 + concat UNI2-h + GigaPath L2 | H&E alone, EW memory | 30.5 | 27.1 | 0.00 | -4.7 [-7.8, -1.4] | -0.6 [-1.8, +0.4] | -5.0 [-8.2, -2.1] | -0.7 [-1.8, +0.2] | +0.013 [-0.055, +0.088] |
| [median logit] UNI2-h L2 | H&E alone, EW memory | 30.9 | 27.2 | 0.00 | -4.6 [-7.5, -1.9] | -0.2 [-1.1, +0.7] | -4.9 [-7.7, -2.3] | -0.3 [-1.3, +0.5] | +0.010 [-0.056, +0.084] |
| [mean logit] ensemble UNI2-h L2 + UNI2-h L1 + GigaPath L2 + Virchow2 L2 + CONCH 20x + MUSK 20x | H&E alone, EW memory | 30.2 | 27.5 | 0.00 | -4.3 [-8.4, +0.2] | -0.9 [-3.5, +1.3] | -4.6 [-8.6, -0.4] | -1.0 [-2.7, +0.0] | +0.037 [-0.043, +0.119] |
| [top-2 logit] UNI2-h L2 | H&E alone, EW memory | 30.5 | 27.8 | 0.00 | -4.0 [-6.9, -1.3] | -0.6 [-1.8, +0.4] | -4.3 [-6.5, -2.3] | -0.7 [-2.0, +0.2] | +0.009 [-0.053, +0.075] |
| [mean logit] ensemble UNI2-h L2 + GigaPath L2 | H&E alone, EW memory | 30.1 | 28.2 | 0.00 | -3.6 [-6.9, -0.3] | -1.0 [-2.5, +0.2] | -3.9 [-6.8, -1.1] | -1.1 [-3.0, +0.0] | +0.028 [-0.042, +0.103] |
| current L-IMG (stored) | H&E alone, EW memory | 31.2 | 32.1 | 0.00 | +0.3 [-2.7, +3.4] | +0.1 [-1.2, +1.7] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | -0.085 [-0.144, -0.019] |
| ensemble UNI2-h L2 + UNI2-h L1 | H&E alone, EW memory | 30.9 | 32.4 | 0.00 | +0.6 [-2.7, +4.4] | -0.2 [-2.6, +1.7] | +0.3 [-2.2, +2.9] | -0.3 [-1.7, +0.7] | -0.080 [-0.139, -0.022] |
| [mean logit] concat UNI2-h + GigaPath L2 | H&E alone, no memory | 30.5 | 28.6 | 0.00 | -3.2 [-6.4, +0.0] | -0.6 [-1.7, +0.3] | -7.4 [-10.8, -4.2] | -1.0 [-2.8, +0.2] | +0.084 [+0.026, +0.152] |
| [mean logit] ensemble UNI2-h L2 + H-optimus-0 20x + Virchow2 20x + GigaPath L2 | H&E alone, no memory | 30.4 | 29.8 | 0.00 | -2.0 [-5.9, +2.0] | -0.7 [-3.0, +0.9] | -6.2 [-9.7, -2.7] | -1.1 [-2.5, -0.1] | +0.128 [+0.065, +0.202] |
| [mean logit] concat UNI2-h L1 + L2 | H&E alone, no memory | 30.4 | 30.1 | 0.00 | -1.7 [-5.5, +2.3] | -0.7 [-2.9, +0.6] | -5.9 [-9.6, -2.2] | -1.1 [-2.8, +0.1] | +0.072 [+0.005, +0.146] |
| [mean prob.] UNI2-h L2 | H&E alone, no memory | 30.8 | 30.9 | 0.00 | -0.9 [-3.5, +1.6] | -0.3 [-2.1, +0.9] | -5.1 [-7.3, -2.9] | -0.7 [-1.8, +0.1] | +0.080 [+0.028, +0.142] |
| [mean logit] UNI2-h L2 | H&E alone, no memory | 30.9 | 31.0 | 0.00 | -0.8 [-3.8, +2.3] | -0.2 [-1.5, +0.9] | -5.0 [-7.9, -2.1] | -0.6 [-1.5, +0.1] | +0.065 [+0.005, +0.133] |
| [mean logit] ensemble UNI2-h L2 + UNI2-h L1 | H&E alone, no memory | 30.5 | 31.1 | 0.00 | -0.7 [-4.2, +3.0] | -0.6 [-3.0, +0.9] | -4.9 [-8.5, -1.3] | -1.0 [-2.7, +0.1] | +0.085 [+0.024, +0.151] |
| [pooled-embedding endoscopy] UNI2-h L2 | H&E alone, no memory | 30.9 | 31.1 | 0.00 | -0.7 [-3.8, +2.4] | -0.2 [-1.5, +0.9] | -4.9 [-7.8, -2.0] | -0.6 [-1.5, +0.1] | +0.063 [+0.004, +0.130] |
| [mean logit] nested choice among UNI2-h L2 + UNI2-h L1 + GigaPath L1 + GigaPath L2 + GigaPath L3 + Virchow2 L2 + CONCH 20x + MUSK 20x + concat UNI2-h L1 + L2 + concat GigaPath L1 + L2 + L3 + concat UNI2-h + GigaPath L2 | H&E alone, no memory | 30.8 | 31.3 | 0.00 | -0.5 [-3.4, +2.7] | -0.3 [-1.8, +0.7] | -4.7 [-7.6, -1.9] | -0.7 [-1.8, +0.1] | +0.040 [-0.021, +0.110] |
| [mean logit] ensemble UNI2-h L2 + GigaPath L2 | H&E alone, no memory | 30.3 | 31.4 | 0.00 | -0.4 [-3.6, +2.9] | -0.8 [-2.3, +0.3] | -4.6 [-7.9, -1.6] | -1.2 [-3.1, +0.0] | +0.053 [-0.008, +0.122] |
| [mean logit] ensemble UNI2-h L2 + UNI2-h L1 + GigaPath L2 + Virchow2 L2 + CONCH 20x + MUSK 20x | H&E alone, no memory | 30.3 | 31.5 | 0.00 | -0.3 [-4.1, +3.7] | -0.8 [-3.4, +1.3] | -4.5 [-8.1, -0.9] | -1.2 [-3.0, +0.0] | +0.060 [-0.008, +0.135] |
| [top-2 logit] UNI2-h L2 | H&E alone, no memory | 30.5 | 32.1 | 0.00 | +0.3 [-2.4, +2.9] | -0.6 [-2.2, +0.6] | -3.9 [-5.9, -2.0] | -1.0 [-2.5, +0.0] | +0.041 [-0.010, +0.101] |
| [median logit] UNI2-h L2 | H&E alone, no memory | 30.9 | 32.1 | 0.00 | +0.3 [-2.5, +3.2] | -0.2 [-1.5, +0.9] | -3.9 [-6.2, -1.8] | -0.6 [-1.6, +0.1] | +0.044 [-0.014, +0.110] |
| ensemble UNI2-h L2 + UNI2-h L1 | H&E alone, no memory | 30.9 | 35.6 | 0.00 | +3.8 [+0.8, +7.0] | -0.2 [-2.6, +1.7] | -0.4 [-2.3, +1.5] | -0.6 [-2.0, +0.2] | -0.056 [-0.112, -0.002] |
| current L-IMG (stored) | H&E alone, no memory | 31.5 | 36.0 | 0.00 | +4.2 [+1.8, +6.8] | +0.4 [-0.7, +1.8] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | -0.037 [-0.090, +0.020] |

### What next

1. **Pre-specify the endoscopy aggregation.** Make mean sample logit the endoscopy score, both for H&E alone with EW memory and inside the gate, and register it before any external test. It is a one-line change that needs no refit.
2. **Find a cohort with repeat endoscopies.** ACE-B cannot test memory; it has mostly one endoscopy per patient. It can still test the aggregation within an endoscopy wherever 2 samples exist.
3. **Check sample-count robustness.** Repeat the samples-per-endoscopy diagnostic under R49 and the memory rule. Check that the mean-logit gain does not hinge on the few endoscopies with 4 or more samples.
4. **Stop chasing extractors.** At this cohort size, no extractor, scale or pooling beats the UNI2-h level-2 mean.

### Implementation notes

- **Scripts** (`scripts/paper_plan/`):
  - `ex_e3_feats.py`: feature blocks from stored tiles; union of a sample's slides; endoscopy-pooled block per endoscopy and pre/post status;
  - `ex_e3_refit.R`: the `rv4_refit.R` / `kv_cv.R` / `hz_fit.R` loops on any block; training-mean imputation; raw-scale coefficients;
  - `ex_e3_tilepool.py`;
  - `ex_e3_score.py`: runs `rv8b_step3.py` / `rv8_landscape.py` unchanged with L-IMG replaced; variants, AUROC, contrasts, diag;
  - `ex_e3_memory.py`: runs `rv9_falseflags.py` unchanged with L-IMG replaced;
  - `ex_e3_render.py`, `ex_e3_figs.py`.
- **L-LATE** is always (stored L-CNV + the variant's sample-level L-IMG) / 2. When L-IMG is an endoscopy score, the top-H&E sample sequenced by R49 is still chosen by the sample-level model.
  - In `ex_e3_score.py`, through a separate pick.
  - In `ex_e3_memory.py`, through a 1e-6 logit tie-break.
  - R49's cut-offs (`t_low`, `c*`, `t_seq`) are derived as in `tb_common.triage` on training samples, each sample carrying its endoscopy's score.
- **Ensembles** average probabilities in the outer and inner predictions alike.
- **The nested choice** picks, per (repeat, outer fold), the candidate with the best fold-stratified AUROC of inner out-of-fold predictions on the fold's pre-event training samples (inner folds as strata).
- **AUROC** is fold-stratified (the `fsa` convention): sample level on pre-event samples, endoscopy level on max/aggregated scores, patient level on the maximum endoscopy score. Each is a repeat mean, with paired bootstrap Δ against the stored L-IMG.
- **Matched contrasts** re-match the variant's P1 threshold per draw and per repeat to the reference rule's realised endoscopy sensitivity (the round-8b S1(i) rule).
- **Apparent** = P1 threshold set on the evaluated endoscopies themselves at 90% endoscopy sensitivity, per repeat.
- **Compute.** Cluster campaigns `exe3f`, `exe3r1` to `exe3r4`, `exe3tp`, `exe3s1` to `exe3s5`, `exe3m1` to `exe3m3`, all on epyc. Row-level outputs stay in `killcoyne_mm/explore_E3/`.

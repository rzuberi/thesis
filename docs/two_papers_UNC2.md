# Two papers, agent UNC2: disagreement between genuinely different H&E models

3 November 2026. Rules: `paper/two_papers/RUN_RULES.md`. Follow-up to `docs/two_papers_UNC.md`. UNC found that disagreement between the 10 CV repeats of the clean L-IMG carries no signal beyond the score. Those 10 models share the features and the recipe. This test asks the same question of models that differ in what they see: other foundation models, other scales, other poolings, other training targets, ERIN transfer, and the same recipe on different tile subsets.

## Plan

- **Population, folds, errors.** As UNC: 571 pre-event samples, 288 endoscopies, 75 patients (32 progressors); stored 10 × 10 patient-grouped folds (`killcoyne_mm`). An H&E error is a clean L-IMG call on the wrong side of the fold's training 90%-sensitivity cut-off (inner out-of-fold predictions). "Confident" means outside the R49 mean-logit gate's middle band. All thresholds come from training patients.
- **Members.** Only models with stored held-out predictions in the same folds (asserted fold by fold). The lists were fixed before any disagreement was computed. The one exception is a pooling filter, explained next.
  - **Set FM (13; primary for "different models").** Clean L-IMG; stored L-IMG (all tiles); UNI2-h L1; Prov-GigaPath L1, L2, L3; Virchow2 L2; H-optimus-0 L2 (scanner-robustness run); TRIDENT 20× H-optimus-0, Virchow2, CONCH v1.5, CTransPath, MUSK (E3).
  - **Set ALL (22).** FM plus:
    - five poolings: quantile; mean+SD; tile-score top-32, top-16 and top-8. The filter kept E3 poolings whose stored sample AUROC was at least 0.75, so it dropped max pooling, top-k by norm and tile-score max. This is a filter on held-out results, so I label it.
    - three E4 time-aware image models: Cox on extended follow-up, a 5-year horizon model and a certainty-weighted model. I took one per model class. Cox gives a linear predictor, not a probability.
    - ERIN LGD+ transfer (E5). It is a fixed model never trained on these labels.
  - **Set TILES (10; new).** The clean-tile L-IMG recipe refitted on 10 random 32-tile subsets of each sample's clean tiles. Each subset is drawn without replacement and independently of the others; samples with several slides pool their slides' tiles. The fit is the same elastic net, the same folds and the same nested λ (`tp_unc2_refit.R`, a copy of ART's refit), and it runs on CPU only.
  - **Not usable.** The attention-MIL N-IMG and the neural fusion models are patient-level and use other folds and seeds. Concatenations and probability ensembles are combinations of members. ART's `clean_noblur` and `rand` are near-duplicates of clean and stored.
- **Disagreement D**, per endoscopy (or sample) and per repeat, is the SD across a set's members of their held-out scores in that repeat. Each member is first put on a common scale within each (repeat, held-out fold): z = z-score of the log-odds, and the endoscopy score is the mean sample logit, as in UNC. Two sensitivity scales: rank = within-fold percentile rank; prob = raw probability with no rescaling (Cox excluded). All scales are label-free.
- **Analyses (UNC's, reused).** `tp_unc_main.py` is executed up to its bootstrap. That gives the state, the R49 smoke, the cut-offs, M, the band, the copy-number and L-LATE fixes, and the budget rule. On top of it:
  - correlations of D with M, with entropy and with the ensemble mean;
  - AUROC of D for an error;
  - error ~ M (+ D);
  - error ~ a flexible model of the score (+ D). The flexible model is UNC's piecewise quadratic in (log-odds − cut-off) plus the cell-level entropy of the clean L-IMG probability. A stricter version also adds the z-scale ensemble mean and its square.
  - Outputs: held-out AUROC gain (5-fold patient-grouped), apparent gain, and the cluster-robust Wald p for D;
  - confident but top-quartile-D endoscopies versus the other confident ones. The quartile cut is the fold's training endoscopies' D. Reported: wrong rate, copy-number and L-LATE fixes, and flips;
  - equal budget: choose by highest D the same number of endoscopies per repeat as the middle band. Reported: non-progressor endoscopies corrected, progressor endoscopies lost, and final flags.
  - Patient bootstrap: 2,000 draws, RandomState(0), UNC's construction.
- **Ensemble mean (exploratory; adds to the image-model search count).** Fold-stratified sample AUROC (`tp_p1b_main.py` `fsa`, `hblock`) for two scores: the mean member probability, and the mean within-fold z log-odds. Paired against clean L-IMG and stored L-IMG on the same 2,000 draws.
- **Smoke.** Member AUROCs must reproduce clean L-IMG 0.811, stored L-IMG 0.847 and H-optimus-0 L2 0.805. The UNC engine must reproduce R49 31.1 / 32.3 (asserted). The clean member's endoscopy mean logit must equal UNC's state. The tile features must rebuild ART's clean block exactly. The refit of ART's clean block (repeat 1) must equal ART's refit.
- **Files.** Scripts: `scripts/paper_plan/tp_unc2_{feats,main}.py` and `tp_unc2_refit.R`. Aggregates: `results/paper_final/two_papers_UNC2/`. Row-level outputs stay in `killcoyne_mm/two_papers_UNC2/` on the cluster. Slurm prefix: `tpunc2`.

## Results

**No signal. Disagreement between genuinely different H&E models adds nothing to the H&E score for predicting H&E errors. This holds for 13 foundation-model and scale variants, for 22 variants that add poolings, time-aware targets and ERIN transfer, and for 10 tile-subset refits. Once the score is modelled flexibly, the held-out AUROC gain is −0.004 to +0.005 in all 18 set × scale × level analyses, and every 95% CI includes 0. At the gate's budget, choosing whom to sequence by disagreement corrects 8 to 14 fewer non-progressor endoscopies than the middle band. The ensemble's mean score, though, beats clean L-IMG: 0.864 against 0.811, Δ +0.052 [+0.020, +0.085]. This is exploratory. It does not beat the stored all-tile L-IMG (+0.017 [−0.002, +0.035]).**

Aggregates are in `results/paper_final/two_papers_UNC2/`: `auc.json` (member and ensemble AUROCs) and `dis_<set>_<scale>.json` (9 files).

### Smoke checks (all passed, asserted in the code)

- Member AUROCs (fold-stratified, sample level): clean L-IMG 0.811, stored L-IMG 0.847, H-optimus-0 L2 0.805. All three match the documented values.
- UNC engine: R49 mean-logit gate (clean) gives 31.1 caught / 32.3 non-progressors flagged / 1.701 samples per patient (= ART `gate.json`), in all 12 runs. The middle band holds 127.6 endoscopies and corrects 23.6 non-progressor endoscopies (= UNC).
- Clean member's endoscopy mean logit against UNC's state: max |Δ| 1.4e-5, which is the 1e-6 tie-break of `state_v`.
- Tile features: the all-clean-tile mean rebuilt by `tp_unc2_feats.py` equals ART's `clean.csv.gz` (max |Δ| 5e-8, the write precision).
- Refit: `tp_unc2_refit.R` on ART's clean block (repeat 1) equals ART's clean refit exactly (max |Δ| 0.0, outer and inner).
- Every member's folds equal the stored folds (asserted for each of the 32 models).

### Members and their own AUROCs (held-out, sample level, fsa)

| Group | Model (sample AUROC) |
|---|---|
| FM set (13) | clean L-IMG 0.811; UNI2-h L2 all tiles (stored L-IMG) 0.847; UNI2-h L1 0.819; Prov-GigaPath L1 0.812, L2 0.796, L3 0.776; Virchow2 L2 0.805; H-optimus-0 L2 0.805; H-optimus-0 20× 0.784; Virchow2 20× 0.838; CONCH v1.5 20× 0.767; CTransPath 20× 0.785; MUSK 20× 0.744 |
| Added in ALL (9) | quantile pooling 0.837; mean+SD pooling 0.784; tile-score top-32 0.835, top-16 0.822, top-8 0.804; E4 Cox extended follow-up 0.761, 5-year horizon 0.809, certainty-weighted 0.848; ERIN LGD+ 0.758 |
| TILES set (10) | 32-clean-tile subsets: 0.744 to 0.804 (median 0.766) |

- Tile subsets: median 248 clean tiles per pre-event sample. The median expected share of tiles that two subsets have in common is 13%. Fewer than 5 pre-event samples have only 32 clean tiles, and they get the same tiles in every subset.
- The members really are different. The mean pairwise Spearman correlation between members' z-scaled endoscopy scores within a repeat is 0.69 for FM, 0.67 for ALL and 0.75 for TILES. I did not compute the same figure for UNC's 10 repeats, so I cannot say exactly how much more different these members are.
- The new D is a different quantity from UNC's. The Spearman correlation between FM z-scale D and UNC's repeat SD is +0.33 at endoscopy level and +0.30 at sample level. For TILES z-scale D it is +0.19.

### 1–3. Disagreement, the score and H&E errors

Endoscopy × repeat cells: H&E error rate 36.0% [28.9, 43.1]. The flexible score model alone has held-out AUROC 0.824 [0.754, 0.901] for an error, and 0.834–0.844 once the ensemble mean is added. This is slightly above UNC's 0.817, because the entropy is now per cell rather than averaged over the 10 repeats.

**Endoscopy level**

| Set, scale | Spearman D vs M | Spearman D vs entropy | AUROC of D for an error | Held-out AUROC gain over flexible score | Gain over flexible score + ensemble mean | D coefficient given flexible score (per SD), p | Same, given + ensemble mean, p |
|---|---|---|---|---|---|---|---|
| FM (13), z | +0.23 [+0.15, +0.30] | −0.02 [−0.11, +0.06] | 0.46 [0.41, 0.51] | +0.000 [−0.005, +0.010] | +0.000 [−0.005, +0.009] | −0.05 [−0.33, +0.20], p 0.74 | p 0.77 |
| FM (13), rank | −0.25 [−0.36, −0.13] | +0.16 [+0.06, +0.26] | 0.57 [0.52, 0.63] | −0.001 [−0.007, +0.012] | +0.001 [−0.005, +0.009] | +0.20 [−0.09, +0.50], p 0.16 | p 0.69 |
| FM (13), prob | +0.07 [−0.04, +0.18] | +0.46 [+0.36, +0.54] | 0.63 [0.57, 0.69] | −0.004 [−0.006, +0.010] | −0.004 [−0.006, +0.006] | +0.10 [−0.22, +0.40], p 0.55 | p 0.74 |
| ALL (22), z | +0.23 [+0.15, +0.31] | −0.01 [−0.10, +0.07] | 0.47 [0.42, 0.52] | −0.000 [−0.006, +0.011] | −0.002 [−0.007, +0.006] | −0.04 [−0.34, +0.20], p 0.78 | p 0.89 |
| ALL (22), rank | −0.27 [−0.38, −0.15] | +0.15 [+0.04, +0.26] | 0.60 [0.54, 0.66] | +0.002 [−0.007, +0.022] | −0.003 [−0.007, +0.006] | +0.35 [+0.06, +0.69], p 0.02 | p 0.55 |
| ALL (22), prob | +0.06 [−0.04, +0.17] | +0.47 [+0.38, +0.55] | 0.63 [0.57, 0.69] | −0.004 [−0.008, +0.013] | −0.004 [−0.007, +0.006] | +0.07 [−0.28, +0.39], p 0.67 | p 0.78 |
| TILES (10), z | +0.07 [−0.00, +0.14] | +0.09 [+0.01, +0.17] | 0.55 [0.50, 0.59] | −0.003 [−0.006, +0.007] | −0.004 [−0.006, +0.008] | +0.13 [−0.08, +0.34], p 0.25 | p 0.21 |
| TILES (10), rank | −0.39 [−0.49, −0.30] | +0.28 [+0.17, +0.38] | 0.62 [0.56, 0.68] | −0.004 [−0.008, +0.010] | −0.004 [−0.006, +0.006] | +0.16 [−0.10, +0.46], p 0.24 | p 0.62 |
| TILES (10), prob | −0.03 [−0.14, +0.08] | +0.64 [+0.56, +0.69] | 0.71 [0.64, 0.78] | −0.003 [−0.006, +0.011] | −0.003 [−0.007, +0.011] | +0.24 [−0.06, +0.53], p 0.10 | p 0.16 |

**Sample level**

| Set, scale | Spearman D vs M | Spearman D vs entropy | AUROC of D for an error | Held-out AUROC gain over flexible score | Gain over flexible score + ensemble mean | D coefficient given flexible score (per SD), p | Same, given + ensemble mean, p |
|---|---|---|---|---|---|---|---|
| FM (13), z | +0.17 [+0.12, +0.24] | −0.10 [−0.15, −0.04] | 0.44 [0.41, 0.48] | −0.000 [−0.003, +0.006] | −0.001 [−0.004, +0.004] | −0.01 [−0.25, +0.21], p 0.92 | p 0.55 |
| FM (13), rank | −0.28 [−0.38, −0.19] | +0.13 [+0.05, +0.22] | 0.58 [0.54, 0.63] | +0.003 [−0.002, +0.015] | −0.001 [−0.004, +0.005] | +0.28 [+0.03, +0.52], p 0.02 | p 0.39 |
| FM (13), prob | +0.12 [+0.01, +0.22] | +0.48 [+0.41, +0.55] | 0.62 [0.57, 0.68] | −0.002 [−0.004, +0.005] | −0.002 [−0.003, +0.003] | +0.08 [−0.14, +0.27], p 0.43 | p 0.57 |
| ALL (22), z | +0.21 [+0.16, +0.27] | −0.08 [−0.14, −0.02] | 0.44 [0.41, 0.47] | +0.001 [−0.002, +0.008] | −0.001 [−0.003, +0.003] | −0.07 [−0.28, +0.12], p 0.49 | p 0.53 |
| ALL (22), rank | −0.28 [−0.38, −0.19] | +0.14 [+0.06, +0.23] | 0.60 [0.56, 0.65] | +0.005 [−0.002, +0.016] | −0.001 [−0.003, +0.005] | +0.38 [+0.18, +0.60], p < 0.001 | p 0.06 |
| ALL (22), prob | +0.11 [+0.01, +0.21] | +0.50 [+0.42, +0.57] | 0.63 [0.57, 0.68] | −0.002 [−0.005, +0.005] | −0.001 [−0.004, +0.004] | +0.06 [−0.17, +0.28], p 0.56 | p 0.77 |
| TILES (10), z | +0.00 [−0.05, +0.06] | +0.02 [−0.04, +0.09] | 0.52 [0.48, 0.55] | −0.001 [−0.003, +0.007] | −0.001 [−0.003, +0.007] | +0.16 [−0.04, +0.34], p 0.10 | p 0.05 |
| TILES (10), rank | −0.45 [−0.53, −0.37] | +0.25 [+0.16, +0.35] | 0.62 [0.58, 0.67] | −0.001 [−0.003, +0.007] | −0.001 [−0.003, +0.004] | +0.20 [−0.02, +0.43], p 0.07 | p 0.34 |
| TILES (10), prob | +0.02 [−0.07, +0.11] | +0.67 [+0.61, +0.71] | 0.71 [0.65, 0.76] | −0.001 [−0.003, +0.010] | −0.001 [−0.003, +0.008] | +0.30 [+0.06, +0.54], p 0.01 | p 0.03 |

- **z scale (the primary scale).** On the z scale, D on its own does not point to errors. Its AUROC for an error is 0.44 to 0.55, so its ranking of errors is close to chance. Like UNC's D, it grows slightly with distance from the cut-off (Spearman +0.17 to +0.23 for the model sets).
- **Probability scale.** On the probability scale, D does pick out errors on its own (AUROC 0.62–0.71). But it is mostly entropy (Spearman +0.46 to +0.67), and the held-out gain once the score is controlled is ≤ 0.
- **Rank scale.** On the rank scale, D is largest in the middle of the score range (Spearman with M −0.25 to −0.45), so it partly re-expresses closeness to the cut-off.
- **Coefficients that reach p < 0.05.** Given the flexible score, a few D coefficients reach p < 0.05: ALL rank at both levels, FM rank at sample level, and TILES prob at sample level. None of them gives a held-out AUROC gain whose CI excludes 0. Three of the four fall to p ≥ 0.06 once the ensemble mean is added to the control. The exception is TILES prob at sample level, with p 0.03 and a held-out gain of −0.001 [−0.003, +0.008]. There are 36 such p-values (9 set × scale, 2 levels, 2 controls), and 5 of them fall below 0.05. My reading is that these are small in-sample effects of the scale, not usable information. This is my inference.

### 4. Confident but disagreeing (endoscopy level; repeat-mean counts per 288 endoscopies)

| Set, scale | Confident, top-quartile D: endoscopies | Wrong | Confident, rest: wrong | Difference (points) | Copy number net per 100 (top-D) | L-LATE net per 100 (top-D) | Copy number net per 100 (rest) |
|---|---|---|---|---|---|---|---|
| FM (13), z | 47.7 [36.3, 59.3] | 24.3% [14.9, 34.2] | 17.9% [11.5, 25.5] | +6.4 [−2.4, +15.0] | −10.1 [−21.3, +0.2] | −3.6 [−10.8, +3.4] | −21.1 [−31.9, −10.4] |
| FM (13), rank | 38.0 [27.6, 49.2] | 26.8% [16.0, 37.8] | 17.6% [11.6, 25.1] | +9.2 [−0.9, +19.1] | −11.3 [−26.6, +2.1] | −6.6 [−18.0, +3.3] | −19.9 [−29.8, −10.1] |
| FM (13), prob | 45.1 [34.0, 57.4] | 38.6% [25.5, 52.4] | 12.5% [7.7, 18.9] | +26.1 [+13.5, +38.6] | +5.8 [−5.2, +16.6] | −2.9 [−10.2, +3.1] | −27.1 [−38.0, −16.1] |
| ALL (22), z | 48.0 [37.1, 59.3] | 27.3% [16.9, 37.9] | 16.6% [10.8, 23.7] | +10.7 [+2.2, +18.8] | −9.4 [−20.5, +1.9] | −3.3 [−10.5, +3.6] | −21.4 [−32.1, −11.0] |
| ALL (22), rank | 35.9 [26.0, 46.5] | 30.4% [18.3, 43.1] | 16.8% [11.2, 23.7] | +13.6 [+2.2, +24.5] | −10.6 [−28.2, +4.5] | −5.6 [−17.8, +5.0] | −19.9 [−29.3, −10.5] |
| ALL (22), prob | 42.6 [31.6, 54.7] | 42.0% [28.8, 56.0] | 11.8% [7.3, 18.0] | +30.2 [+18.5, +42.8] | +6.8 [−5.3, +18.1] | −1.4 [−9.6, +6.1] | −26.7 [−37.0, −16.8] |
| TILES (10), z | 42.6 [32.6, 53.7] | 31.9% [22.4, 41.6] | 15.4% [9.5, 22.6] | +16.5 [+8.7, +23.9] | −9.6 [−23.4, +2.9] | −3.8 [−11.0, +3.4] | −20.8 [−31.1, −10.6] |
| TILES (10), rank | 29.1 [21.3, 37.6] | 29.9% [19.0, 41.1] | 17.6% [11.3, 25.2] | +12.3 [+1.4, +22.7] | −15.8 [−33.6, +1.0] | −7.6 [−19.6, +3.4] | −18.3 [−28.0, −8.7] |
| TILES (10), prob | 37.7 [27.4, 49.2] | 47.5% [31.8, 64.2] | 11.3% [7.0, 17.0] | +36.2 [+20.9, +51.6] | +7.7 [−2.2, +17.3] | −1.1 [−6.0, +2.8] | −25.7 [−36.3, −14.9] |

- **The wrong-rate difference.** Unlike UNC, confident endoscopies with high disagreement are wrong more often than the other confident ones. The difference is +6 to +36 points, and its CI excludes 0 in 7 of 9 rows. Sections 1–3 show this is score-level information: those endoscopies sit near the band edges or at moderate probabilities, and the flexible score model already captures that.
- **Copy number does not rescue them.** Its net effect in the top-D group is −15.8 to +7.7 per 100, and every CI includes 0. L-LATE's net effect is −7.6 to −1.1 per 100, again with every CI including 0. Copy number is clearly harmful in the rest (−18 to −27 per 100). So letting copy number overrule a confident H&E call is at best neutral even where the models disagree.

### 5. Equal budget (endoscopy level; same number sequenced per repeat as the middle band, 127.6)

| Selection | Overlap with the band | NP endoscopies corrected | Highest D − band: NP corrected | Highest D − band: progressor endoscopies lost | Highest D − band: NP flagged, final | Highest D − band: progressor flagged, final |
|---|---|---|---|---|---|---|
| Middle band (R49) | 127.6 [105.3, 150.7] | 23.6 [15.2, 32.4] | — | — | — | — |
| Highest D, FM (13), z | 47.3 [34.7, 62.5] | 9.4 [5.2, 15.6] | −14.2 [−18.8, −9.0] | −1.8 [−3.8, −0.3] | +12.8 [+5.6, +19.4] | +2.0 [−0.6, +5.0] |
| Highest D, FM (13), rank | 66.1 [51.5, 81.8] | 13.7 [8.3, 19.8] | −9.9 [−14.2, −6.1] | −1.7 [−3.5, −0.3] | +13.6 [+7.8, +20.3] | +2.1 [−0.2, +5.0] |
| Highest D, FM (13), prob | 56.3 [41.1, 73.4] | 10.9 [5.6, 16.5] | −12.7 [−17.6, −8.6] | −0.2 [−0.8, +0.1] | +7.8 [+1.9, +14.7] | +0.2 [−1.8, +2.6] |
| Highest D, ALL (22), z | 48.0 [34.7, 64.7] | 9.3 [5.0, 14.6] | −14.3 [−19.3, −9.5] | −1.4 [−3.0, −0.2] | +11.9 [+5.6, +19.0] | +1.6 [−0.5, +4.3] |
| Highest D, ALL (22), rank | 66.5 [51.7, 83.3] | 13.5 [7.9, 19.9] | −10.1 [−14.5, −6.3] | −1.4 [−3.0, +0.0] | +14.5 [+7.9, +20.8] | +2.2 [−0.3, +5.1] |
| Highest D, ALL (22), prob | 58.1 [42.4, 75.7] | 10.4 [5.1, 16.5] | −13.2 [−17.8, −8.6] | −0.4 [−0.9, +0.2] | +8.9 [+3.0, +15.2] | +1.0 [−1.2, +3.0] |
| Highest D, TILES (10), z | 56.7 [43.4, 72.3] | 12.8 [7.2, 18.3] | −10.8 [−15.9, −6.7] | −0.9 [−2.2, +0.0] | +7.9 [+2.9, +14.4] | +1.5 [−0.3, +3.9] |
| Highest D, TILES (10), rank | 75.1 [59.5, 92.6] | 15.6 [9.2, 22.8] | −8.0 [−11.5, −4.7] | −0.4 [−1.4, +0.1] | +9.0 [+4.8, +14.1] | +1.7 [−0.1, +4.4] |
| Highest D, TILES (10), prob | 67.2 [50.7, 84.8] | 13.1 [7.1, 20.2] | −10.5 [−14.4, −6.8] | −0.6 [−1.3, +0.1] | +4.0 [−0.4, +9.2] | +0.3 [−1.4, +1.8] |

Every disagreement-based selection is worse than the middle band.
- It corrects 8.0 to 14.3 fewer non-progressor endoscopies.
- It ends with 4.0 to 14.5 more non-progressor endoscopies flagged.
- Progressor endoscopies flagged: no gain whose CI excludes 0 (−0.3 to +5.1 at the CI bounds).

### Ensemble mean against clean L-IMG (exploratory; adds to the image-model search count)

Fold-stratified sample AUROC, 571 pre-event samples, 2,000 paired patient-bootstrap draws:

| Score | AUROC | − clean L-IMG | − stored L-IMG |
|---|---|---|---|
| Clean L-IMG | 0.811 [0.753, 0.872] | — | −0.036 [−0.062, −0.011] |
| Stored L-IMG (all tiles) | 0.847 [0.798, 0.894] | +0.036 [+0.011, +0.062] | — |
| FM ensemble, mean probability | 0.851 [0.803, 0.897] | **+0.040 [+0.003, +0.079]**, p 0.033 | +0.004 [−0.024, +0.031] |
| FM ensemble, mean z log-odds | 0.848 [0.799, 0.896] | +0.036 [+0.001, +0.073], p 0.046 | +0.001 [−0.027, +0.026] |
| ALL ensemble, mean probability | 0.864 [0.818, 0.906] | **+0.052 [+0.020, +0.085]**, p < 0.001 | +0.017 [−0.002, +0.035], p 0.069 |
| ALL ensemble, mean z log-odds | 0.859 [0.812, 0.903] | +0.047 [+0.018, +0.080], p 0.001 | +0.012 [−0.006, +0.029] |
| TILES ensemble, mean probability | 0.805 [0.750, 0.862] | −0.006 [−0.026, +0.016] | −0.041 [−0.066, −0.016] |
| TILES ensemble, mean z log-odds | 0.799 [0.741, 0.858] | −0.012 [−0.030, +0.007] | −0.047 [−0.072, −0.022] |

- The diverse ensembles beat clean L-IMG by about as much as the stored all-tile L-IMG does, and they do not beat the stored L-IMG.
- All FM and ALL members other than clean L-IMG are all-tile models. ART showed that part of the all-tile L-IMG's advantage comes from artefact tiles. So the ensemble's gain over clean L-IMG may be partly that same artefact signal (my inference; not tested). A clean-tile version of each extractor would be needed to separate the two.
- Averaging 10 models that each see only 32 clean tiles recovers clean L-IMG's AUROC (0.805 against 0.811) but does not exceed it.
- The ALL row is the best of 6 ensemble rows and comes after E3's more than 50 variants and P1B's 30-candidate nested choice. It is therefore optimistic, and it is not a confirmatory result.

### Verdict

No signal. Disagreement across genuinely different H&E models re-expresses the score, as UNC's repeat disagreement did, and gives no held-out gain over a flexible model of the score.
- The models do differ (pairwise Spearman 0.67–0.75).
- On the probability scale, disagreement tracks entropy. On the rank scale, it tracks closeness to the cut-off. On the z scale, it carries nothing.
- At equal budget, it does worse than the middle band. Copy number does not fix the confident-but-disagreeing endoscopies.
- The gate's middle band remains the uncertainty signal for choosing whom to sequence.
- The only positive finding is the ensemble mean's AUROC. It matches the stored all-tile L-IMG and does not exceed it.

Not checked:
- clean-tile refits of the other extractors;
- disagreement as a predictor of copy-number errors;
- tile-level spread within a slide.

### Implementation notes

- `tp_unc2_main.py TASK=dis` executes `tp_unc_main.py` (UNC's committed script, byte-identical copy in `killcoyne_mm/two_papers_UNC2/code/`) up to its bootstrap section. This reuses UNC's state, smoke, cut-offs, M, band, CNV/LATE fixes and budget rule unchanged.
- `analyse2` and `step45_2` are UNC's `analyse` and `step45`, changed in four ways:
  - D varies by repeat (rows × 10), because each repeat has its own held-out predictions;
  - Spearman correlations are computed over the stacked cells;
  - entropy is per cell (the clean L-IMG probability in that repeat);
  - a second control adds the z-scale ensemble mean and its square.
- The common scale is computed within each (repeat, held-out fold), over that fold's held-out pre-event endoscopies (or samples). It is label-free. The top-quartile cut is the 75th percentile of the fold's training endoscopies' D, which is their own held-out D in the same repeat.
- The ERIN LGD+ score is the max over a sample's slides of the slide logit (E5 convention). It is the same in every fold because ERIN never saw these labels. The E4 Cox model gives a linear predictor: it enters the z and rank scales and is left out of the probability scale and the mean-probability ensemble.
- `TASK=auc` executes `tp_p1b_main.py` for definitions only (`fsa`, `hblock`, `boots`, `dstat`). Ensembles: the mean of member probabilities (E3 convention), or the mean of within-fold z log-odds.
- Compute, all CPU, all through Slurm:
  - `tpunc2f`: tile features, 1 job;
  - `tpunc2c`, `tpunc2k`: refit smoke and comparison;
  - `tpunc2r`: 100 refits (10 subsets × 10 repeats), about 9 min wall;
  - `tpunc2s`: three 5-draw smokes;
  - `tpunc2d`, `tpunc2t`: 9 disagreement jobs of 466–540 s each and one AUROC job of 140 s.
- Wall time was about 65 min (3 Nov, 21:50–22:56). No GPU was used and no slide pixels were read. Row-level features and refits stay in `killcoyne_mm/two_papers_UNC2/`.

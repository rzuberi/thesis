# Two papers, agent P1B: Paper 1 confound and robustness analyses

21 October 2026. Brief: `paper/two_papers/PAPER1_plan_v2.md`, "New analyses" items 4, 5, 6, 7, 9 and 10. Rules: `paper/two_papers/RUN_RULES.md`.

## Plan

Population: the 571 pre-event samples (288 endoscopies, 75 patients, 32 progressors). Models: the stored L-CNV (their matrix, `cv/preds/cfg_00`), L-IMG (`cfg_02`) and L-LATE (their mean), 10 repeats × 10 patient-grouped folds. Metric: fold-stratified AUROC (`fsa` of `rv4_round4.py`: within-fold case–control pairs, mean over repeats), sample-level as in every earlier round, plus the patient-weighted version (pair weight 1/n_i × 1/n_j). CIs: 2,000 patient-bootstrap draws (`tb_common.boots_for`, `RandomState(0)`); p = two-sided bootstrap sign p. Every Δ is paired on the same draws. Smoke check first: 0.801 / 0.847 / 0.889 and the round-4 within-batch values 0.790 / 0.841 / 0.893.

1. **Batch (item 4).** Within-batch AUROC (pairs in the same fold and the same sequencing batch) for the three models, Δ L-IMG − L-CNV and Δ L-LATE − L-IMG, sample-level and patient-weighted. Same within scanner (the H&E scan campaign) and within batch × scanner. Batch × scanner cross-table with Cramér's V. Is copy number batch-associated: (a) within-class batch probes from the CN matrix and from the slide-mean embedding (patient-grouped 5-fold, one-vs-rest, batches with ≥ 3 patients in that class); (b) between-batch variance of each model's held-out score within each class (patient-level, permutation p).
2. **Depth (item 5).** Realised depth per sample (total reads × read length / genome length, as `dd_describe.py`; sheet read count × 50 bp as the second definition). Distribution overall, by class and by batch. AUROC of the three models within depth tertiles (cuts on all pre-event samples, label-free), within package QC pass/fail and within varMAD tertiles. Biopsy size (tissue tiles, < 256 vs ≥ 256 as R32; and tertiles): Δ L-IMG − L-CNV in small minus large (difference-in-differences) with bootstrap CI; the same for depth (low minus high tertile). Are small biopsies low depth: Spearman correlation, cross-table, and the tissue DiD restricted to depth-matched pairs.
3. **Image-model selection (item 6).** Dated record from git history. Then the nested choice: per (repeat, outer fold), pick the candidate with the best inner out-of-fold AUROC on that fold's training patients (`ex_e3_score.py` `sel:` logic), on candidate sets of growing size from the E3 refits (extractors, scales, poolings, ensembles). Report nested AUROC, Δ against L-IMG, the apparent best (max over candidates of held-out AUROC) and the optimism, and L-LATE with the nested image score.
4. **Grade and p53 (item 7).** Per outer fold, logistic models fitted on training pre-event samples: grade; grade + L-IMG (inner out-of-fold logit); grade + p53; grade + p53 + L-IMG; also with L-CNV and L-LATE. Held-out AUROC and paired Δ. L-IMG within NDBE (0.827) and within grade strata (pairs sharing grade), with CIs. Apparent (non-nested) refits labelled optimistic.
5. **Sensitivity (item 9).** Labels: sheet status (the published Killcoyne labels; checked against the published Fig 2a table) against the Barrett's-database update (R54 refit) and database event dates (R53, re-scored); added linkable samples (R52 refits). Same-block only: drop the 15 samples whose slide is from a different or unrecorded block (evaluation-only). Selection: the 97 published samples without a slide against the 676 with one, on class, grade, pre-event status, batch, reads, p53, year, the published model P probability and copy-number burden, within class, with P's AUROC on each.
6. **Pathologist panel (item 10).** Per-tile L-IMG contributions u_t (E1 `u/` files, held-out fit of each sample, mean over repeats) on pre-event samples; non-background, non-edge, non-ink, non-blurred tiles; top and bottom tiles across the cohort, at most 2 per patient. Crops read in a CPU job at level 1 (≈ 0.44 µm/px, the same field as the 224-px level-2 tile). Mixed and shuffled into numbered montages in `paper/two_papers/figs_P1B/`; the answer key stays on the cluster.

Scripts `scripts/paper_plan/tp_p1b_*.py`; aggregates `results/paper_final/two_papers_P1B/`; row-level `killcoyne_mm/two_papers_P1B/`; Slurm prefix `tpp1b`.

---

## Results

Aggregates: `results/paper_final/two_papers_P1B/*.json`. Tables below are printed by `scripts/paper_plan/tp_p1b_render.py`; the figure is `paper/two_papers/figs_P1B/p1b_robustness_forest.png` (local). Scripts: `tp_p1b_main.py` (items 4–9), `tp_p1b_panel.py` (item 10), `tp_p1b_render.py`, `tp_p1b_figs.py`. Cluster campaigns `tpp1bs` (smoke, 20 draws), `tpp1b` (full, 2,000 draws), `tpp1bp` (tile crops); all on epyc.

**Smoke checks.** The new `fsa` reproduces L-CNV / L-IMG / L-LATE 0.801 / 0.847 / 0.889, the round-4 within-batch values 0.790 / 0.841 / 0.893, and the NDBE values 0.780 / 0.827 / 0.867. The nested image choice reproduces E3 (0.819 on 11 candidates, 0.816 on 9). The E3 `base` refit equals the stored L-IMG exactly; the round-7 `base` refit equals the stored repeat 1 exactly (max |Δ| 0.0). Published model P on our 571 samples gives 0.828 (the 0.83 quoted).

### Summary

- **Batch.** Within sequencing batch (412 within-fold pairs per repeat): L-CNV 0.790, L-IMG 0.841, L-LATE 0.893; Δ IMG − CNV +0.051 [−0.071, +0.184], Δ LATE − IMG +0.052 [−0.006, +0.109]. Within scanner and within batch × scanner the picture is the same. Sequencing batch and scan campaign are strongly but not fully aligned (Cramér's V 0.70; 9 of 12 batches span both scanners). Copy number is about as batch-encodable as the image (batch probe 0.648 vs 0.664 over all samples; within non-progressors 0.615 vs 0.566). Within class, only the L-IMG score varies more between batches than chance, and only among non-progressors (η² 0.37, permutation p 0.03; L-CNV 0.17, p 0.53).
- **Depth.** Realised depth median 0.287× (IQR 0.229–0.348; 33 samples < 0.1×). L-CNV is lowest in the shallowest tertile (0.710 vs 0.831 in the deepest; Δ −0.121 [−0.286, +0.048]), but L-IMG also drops there (−0.089 [−0.193, +0.004]), so the IMG − CNV gap does not change with depth (+0.032 [−0.156, +0.198]). sWGS QC failed in only 8 pre-event samples (not reported separately).
- **Small biopsies.** The H&E advantage in small biopsies is an interaction of +0.129 [−0.004, +0.246] (p 0.06) for < 256 vs ≥ 256 tiles and +0.195 [+0.022, +0.351] for the lowest vs highest tissue tertile. It comes from **L-IMG being better on small biopsies** (+0.106 [+0.030, +0.180]), not from copy number being worse (−0.022 [−0.135, +0.095]). Small biopsies are **not** low depth: median 0.298× vs 0.274× in large ones (Spearman of tissue tiles with depth −0.13). With pairs matched on depth tertile the interaction is unchanged (+0.146 [−0.010, +0.279]).
- **Image-model selection.** See the dated record below. Choosing the image model inside the CV among the variants with stored inner predictions gives 0.816–0.827 instead of 0.847 (optimism of the reported L-IMG over an honest choice: +0.020 to +0.031). The nested image model against L-CNV is +0.014 to +0.026, and L-LATE built on it is 0.873–0.883 (+0.072 to +0.081 over L-CNV).
- **Grade and p53.** Grade alone (nested logistic) 0.564; grade + L-IMG 0.852, Δ +0.288 [+0.235, +0.346]. Grade + p53 0.674; adding L-IMG +0.191 [+0.132, +0.261]. Grade adds nothing to L-IMG (+0.005 [−0.012, +0.021]). L-IMG within NDBE 0.827 [0.771, 0.885]; among pairs sharing grade 0.830 [0.776, 0.886]; within p53-normal samples 0.848 [0.786, 0.903].
- **Sensitivity.** No row changes the picture: same-block only 0.807 / 0.854 / 0.895; database event dates 0.791 / 0.847 / 0.884; database-updated labels (refit) 0.731 / 0.812 / 0.838, which moves copy number more than H&E (Δ IMG − CNV +0.081). The sheet Status equals the sheet's original P/NP column for all 571 samples, so "original labels" are the primary analysis.
- **Samples without a slide.** 97 of 773 published samples (83 progressor; 8 progressor patients with none). Excluded progressor samples are later (SMD +0.55) and somewhat more copy-number-abnormal (SMD +0.38 [+0.02, +0.73]); published P scores them no better (AUROC 0.752 [0.552, 0.980] on the 97 vs 0.868 on the 676). Adding the linkable ones (R52) raises L-IMG to 0.862–0.870 and leaves L-CNV at 0.789–0.801.
- **Pathologist panel.** Ready, not sent: 80 tiles (40 top-weighted, 40 bottom-weighted, ≤ 2 per patient, 47 patients), five numbered montages and `PANEL_README.txt` in `paper/two_papers/figs_P1B/`; the answer key is only at `killcoyne_mm/two_papers_P1B/panel/ANSWER_KEY_SECRET.csv`. Among the 40 highest-ranked positive tiles, 22.5% were glass, coverslip-edge or out-of-focus artefact (tissue share < 0.15), against 0% of the 40 most negative. These were left out of the panel and replaced by the next-ranked tissue tiles.

### Image-model selection: the dated record

| Date (git) | What was fixed or tried |
|---|---|
| 26 Feb 2026 (file dates) | UNI2-h tile embeddings: 224 px at level 2 (≈ 0.88 µm/px), 256 tiles per slide, seed 20260226 (`barretts_retraining/.../uni2_tile224_lvl2`). Fixed months before any analysis here. |
| Aug – 25 Sep 2026 | Release models on the same bags: attention-MIL "WSI", co-attention and intermediate fusion. |
| 26 Sep 2026 (25f7a55) | Linear probes on patient-mean embeddings seen in the K3 pooling checks. |
| 28 Sep 2026 15:14 (1fe1c8a) | Pre-specification "Killcoyne protocol with imaging": L-IMG = glmnet α 0.9, standardize FALSE, class-error λ on the slide-mean embedding, **hyper-parameters copied from Killcoyne's copy-number model**, alongside N-IMG (attention-MIL). Results 15:43 (026b0a2): L-IMG per-sample 0.878 vs N-IMG 0.817 (patient max 0.865 vs 0.876). |
| 29 Sep 2026 (d238871) | 10 × 10 CV pre-specification carries L-IMG only. |
| 12 Oct – 20 Oct 2026 | Scanner robustness and H-optimus (12 Oct), scales (12 Oct), ABMIL retrain (13 Oct), E3 extractors, poolings and ensembles, E4 time-aware models, E5 ERIN transfer (20 Oct). |

So the specification was fixed and dated before every alternative in the reviewers' list, but not before all image models: L-IMG was preferred to the pre-specified attention-MIL after both were seen (on the per-sample metric; patient-max favoured N-IMG slightly). N-IMG has no inner out-of-fold predictions in these folds, so it cannot enter the nested choice; the nested analysis covers the 30 variants that do.

**Asymmetric tuning effort.** Copy number: 4 segmentation versions plus the package and shipped feature sets. Image: 2 pre-specified models, then about 30 extractor, scale, pooling and ensemble variants (E3), time-aware models (E4), ERIN transfer (E5) and an ABMIL retrain. L-IMG itself took no image-specific tuning.

### 1. Batch

| Rows | Samples / patients (P) | L-CNV | L-IMG | L-LATE | Δ IMG − CNV | Δ LATE − IMG |
|---|---|---|---|---|---|---|
| All pairs | 6495 pairs; 571 / 75 (32) | 0.801 [0.710, 0.875] | 0.847 [0.798, 0.894] | 0.889 [0.830, 0.934] | +0.045 [-0.036, 0.136] | +0.042 [0.002, 0.078] |
| All pairs, patient-weighted | 6495 pairs; 571 / 75 (32) | 0.822 [0.738, 0.887] | 0.852 [0.803, 0.898] | 0.897 [0.848, 0.936] | +0.030 [-0.047, 0.118] | +0.045 [0.006, 0.084] |
| Within sequencing batch | 412 pairs; 571 / 75 (32) | 0.790 [0.675, 0.916] | 0.841 [0.755, 0.925] | 0.893 [0.796, 0.967] | +0.051 [-0.071, 0.184] | +0.052 [-0.006, 0.109] |
| Within sequencing batch, patient-weighted | 412 pairs; 571 / 75 (32) | 0.814 [0.689, 0.929] | 0.850 [0.764, 0.926] | 0.898 [0.803, 0.969] | +0.035 [-0.081, 0.165] | +0.049 [-0.007, 0.110] |
| Within scanner (H&E batch) | 4070 pairs; 571 / 75 (32) | 0.799 [0.701, 0.874] | 0.856 [0.806, 0.902] | 0.891 [0.828, 0.939] | +0.058 [-0.021, 0.149] | +0.035 [-0.005, 0.072] |
| Within scanner (H&E batch), patient-weighted | 4070 pairs; 571 / 75 (32) | 0.815 [0.729, 0.885] | 0.862 [0.809, 0.908] | 0.898 [0.845, 0.940] | +0.046 [-0.034, 0.135] | +0.037 [-0.004, 0.079] |
| Within batch and scanner | 295 pairs; 571 / 75 (32) | 0.779 [0.663, 0.912] | 0.844 [0.755, 0.926] | 0.884 [0.789, 0.962] | +0.065 [-0.060, 0.202] | +0.040 [-0.011, 0.103] |
| Within batch and scanner, patient-weighted | 295 pairs; 571 / 75 (32) | 0.810 [0.675, 0.926] | 0.851 [0.761, 0.926] | 0.892 [0.797, 0.965] | +0.042 [-0.071, 0.183] | +0.040 [-0.012, 0.104] |

Batch × scanner: Cramér's V 0.7; 9 of 12 batches hold slides from both scanners; patients with slides from both scanners 23, with samples in several batches 15.
One-variable AUROC (fold-honest target encoding): batch 0.759 [0.641, 0.865]; scanner 0.387 [0.343, 0.435]; batch × scanner 0.742 [0.624, 0.849].

| Batch probe (mean one-vs-rest AUROC over batches) | Copy-number matrix | UNI2-h slide mean |
|---|---|---|
| All pre-event samples (≥ 5 patients per batch) | 0.648 (9 batches) | 0.664 (9) |
| Non-progressors only (≥ 3) | 0.615 (10 batches) | 0.566 (10) |
| Progressors only (≥ 3) | 0.486 (7 batches) | 0.538 (7) |

| Held-out score vs batch, within class (patient level) | η² non-progressors (perm p) | η² progressors (perm p) |
|---|---|---|
| L-CNV | 0.174 (0.5343; null 0.192) | 0.045 (0.948; null 0.168) |
| L-IMG | 0.372 (0.0302; null 0.19) | 0.123 (0.6339; null 0.168) |

### 2. Depth, sWGS QC and biopsy size

Realised depth, pre-event samples: median 0.287× (IQR 0.229–0.348; 10th–90th centile 0.154–0.404; range 0.043–1.715); 33 samples below 0.1×, <5 above 1×. Sheet read count × 50 bp: median 0.344× (IQR 0.289–0.417). Progressors 0.298×, non-progressors 0.284× (Δ median +0.015 [-0.023, 0.053]).

| Rows | Samples / patients (P) | L-CNV | L-IMG | L-LATE | Δ IMG − CNV | Δ LATE − IMG |
|---|---|---|---|---|---|---|
| Depth low tertile (< 0.254×) | 190 / 52 (20) | 0.710 [0.545, 0.862] | 0.797 [0.709, 0.873] | 0.805 [0.675, 0.914] | +0.088 [-0.063, 0.233] | +0.007 [-0.081, 0.088] |
| Depth middle (0.254–0.324×) | 190 / 65 (26) | 0.871 [0.775, 0.936] | 0.838 [0.772, 0.907] | 0.910 [0.854, 0.958] | -0.034 [-0.122, 0.082] | +0.073 [0.016, 0.124] |
| Depth high (> 0.324×) | 191 / 51 (20) | 0.831 [0.739, 0.909] | 0.887 [0.825, 0.942] | 0.936 [0.889, 0.974] | +0.056 [-0.053, 0.172] | +0.050 [0.005, 0.099] |
| Pairs within the same depth tertile | 571 / 75 (32) | 0.803 [0.702, 0.880] | 0.842 [0.793, 0.893] | 0.884 [0.816, 0.937] | +0.039 [-0.046, 0.134] | +0.043 [-0.007, 0.086] |
| sWGS QC pass | 563 / 75 (32) | 0.805 [0.712, 0.877] | 0.844 [0.795, 0.892] | 0.889 [0.831, 0.935] | +0.039 [-0.044, 0.133] | +0.045 [0.005, 0.082] |
| sWGS QC fail | 8 samples; not reported: fewer than 5 samples or patients in a class | | | | | |
| varMAD low tertile (least noisy) | 67 / 32 (10) | 0.789 [0.577, 0.957] | 0.908 [0.786, 0.982] | 0.951 [0.894, 0.993] | +0.119 [-0.118, 0.369] | +0.043 [-0.046, 0.175] |
| varMAD middle | 303 / 71 (28) | 0.828 [0.734, 0.897] | 0.821 [0.757, 0.889] | 0.876 [0.801, 0.933] | -0.006 [-0.091, 0.084] | +0.055 [0.013, 0.097] |
| varMAD high (noisiest) | 201 / 59 (23) | 0.758 [0.630, 0.877] | 0.868 [0.792, 0.928] | 0.890 [0.818, 0.944] | +0.110 [-0.044, 0.264] | +0.022 [-0.049, 0.094] |
| Small biopsy (< 256 tissue tiles) | 293 / 72 (29) | 0.792 [0.689, 0.876] | 0.905 [0.846, 0.946] | 0.926 [0.881, 0.959] | +0.113 [0.002, 0.223] | +0.021 [-0.017, 0.058] |
| Large biopsy (≥ 256) | 278 / 67 (26) | 0.814 [0.695, 0.903] | 0.799 [0.733, 0.861] | 0.865 [0.773, 0.930] | -0.015 [-0.104, 0.097] | +0.067 [0.006, 0.116] |
| Tissue low tertile (< 200 tiles) | 189 / 62 (23) | 0.770 [0.653, 0.866] | 0.909 [0.847, 0.955] | 0.927 [0.876, 0.962] | +0.139 [0.021, 0.269] | +0.018 [-0.029, 0.065] |
| Tissue middle (200–302) | 195 / 59 (19) | 0.850 [0.776, 0.912] | 0.897 [0.825, 0.949] | 0.937 [0.889, 0.969] | +0.048 [-0.047, 0.136] | +0.040 [0.008, 0.081] |
| Tissue high (> 302) | 187 / 61 (23) | 0.802 [0.662, 0.905] | 0.746 [0.664, 0.826] | 0.837 [0.722, 0.918] | -0.056 [-0.162, 0.080] | +0.091 [0.019, 0.154] |
| Small biopsy, depth-matched pairs | 293 / 72 (29) | 0.802 [0.705, 0.887] | 0.921 [0.869, 0.958] | 0.935 [0.887, 0.968] | +0.119 [0.012, 0.225] | +0.014 [-0.022, 0.047] |
| Large biopsy, depth-matched pairs | 278 / 67 (26) | 0.811 [0.672, 0.911] | 0.784 [0.712, 0.861] | 0.855 [0.741, 0.932] | -0.027 [-0.130, 0.104] | +0.071 [-0.011, 0.138] |

| Interaction (difference in differences) | Estimate [95% CI] | p |
|---|---|---|
| Small − large biopsy: Δ IMG − CNV | +0.129 [-0.004, 0.246] | 0.062 |
| Small − large: L-CNV AUROC | -0.022 [-0.135, 0.095] | 0.76 |
| Small − large: L-IMG AUROC | +0.106 [0.030, 0.180] | 0.004 |
| Small − large: Δ LATE − IMG | -0.045 [-0.101, 0.019] | 0.151 |
| Small − large, depth-matched pairs: Δ IMG − CNV | +0.146 [-0.010, 0.279] | 0.068 |
| Small − large, depth-matched pairs: L-CNV | -0.008 [-0.130, 0.126] | 0.889 |
| Low − high depth tertile: Δ IMG − CNV | +0.032 [-0.156, 0.198] | 0.875 |
| Low − high depth: L-CNV | -0.121 [-0.286, 0.048] | 0.207 |
| Low − high depth: L-IMG | -0.089 [-0.193, 0.004] | 0.061 |
| Low − high tissue tertile: Δ IMG − CNV | +0.195 [0.022, 0.351] | 0.027 |
| Least − most noisy varMAD tertile: L-CNV | +0.031 [-0.206, 0.242] | 0.738 |

Small biopsies are not low depth: Spearman (tissue tiles, depth) -0.132 [-0.227, -0.036]; median depth small 0.298× vs large 0.274× (Δ +0.024 [0.003, 0.039]). Small-biopsy samples by depth tertile (low / mid / high): {'0': 80, '1': 104, '2': 109}; large: {'0': 110, '1': 86, '2': 82}.

### 3. Image-model selection

| Candidate set | n | Nested AUROC | Nested − L-IMG | L-IMG chosen (of 100 folds) | Rank of L-IMG | Apparent best (held-out, optimistic) | Optimism: apparent best − nested | Nested IMG − L-CNV | Nested LATE | Nested LATE − L-CNV |
|---|---|---|---|---|---|---|---|---|---|---|
| E3 extractors (9) | 9 | 0.816 [0.762, 0.868] | -0.031 [-0.055, -0.012] | 47 | 1 | 0.847 (base) | +0.031 [0.018, 0.059] | +0.014 [-0.076, 0.114] | 0.877 [0.815, 0.924] | +0.075 [0.023, 0.134] |
| E3 scales and concatenations (11) | 11 | 0.819 [0.766, 0.871] | -0.028 [-0.047, -0.013] | 51 | 1 | 0.847 (base) | +0.028 [0.014, 0.048] | +0.017 [-0.070, 0.108] | 0.873 [0.812, 0.923] | +0.072 [0.021, 0.129] |
| Poolings (11) | 11 | 0.825 [0.775, 0.873] | -0.021 [-0.034, -0.011] | 37 | 1 | 0.847 (base) | +0.021 [0.014, 0.041] | +0.024 [-0.058, 0.110] | 0.875 [0.813, 0.921] | +0.073 [0.026, 0.128] |
| Everything with inner predictions | 30 | 0.827 [0.774, 0.876] | -0.020 [-0.042, -0.001] | 8 | 2 | 0.855 (ens:base+ho20_mean+v220_mean+gpl2_mean) | +0.028 [0.018, 0.054] | +0.026 [-0.062, 0.123] | 0.883 [0.824, 0.929] | +0.081 [0.032, 0.136] |

### 4. Grade and p53

| Model (held-out, nested) | AUROC [95% CI] |
|---|---|
| GRADE | 0.564 [0.504, 0.628] |
| GRADE+IMG | 0.852 [0.799, 0.902] |
| GRADE+CNV | 0.805 [0.722, 0.874] |
| GRADE+LATE | 0.887 [0.827, 0.936] |
| GRADE+P53 | 0.674 [0.594, 0.746] |
| GRADE+P53+IMG | 0.865 [0.813, 0.911] |
| GRADE+P53+LATE | 0.888 [0.831, 0.935] |
| GRADE+P53+CNV | 0.809 [0.729, 0.875] |
| GRADE+P53AB | 0.606 [0.545, 0.673] |
| GRADE+P53AB+IMG | 0.861 [0.809, 0.910] |
| GRADE+P53AB+LATE | 0.892 [0.832, 0.939] |
| L-IMG | 0.847 [0.798, 0.894] |
| L-CNV | 0.801 [0.710, 0.875] |
| L-LATE | 0.889 [0.830, 0.934] |
| raw_grade | 0.595 [0.523, 0.668] |

| Difference | Δ [95% CI] | p |
|---|---|---|
| GRADE+IMG − GRADE | +0.288 [0.235, 0.346] | 0.0 |
| GRADE+CNV − GRADE | +0.241 [0.155, 0.318] | 0.0 |
| GRADE+LATE − GRADE | +0.323 [0.257, 0.387] | 0.0 |
| GRADE+P53+IMG − GRADE+P53 | +0.191 [0.132, 0.261] | 0.0 |
| GRADE+P53+CNV − GRADE+P53 | +0.136 [0.056, 0.212] | 0.002 |
| GRADE+P53+LATE − GRADE+P53 | +0.215 [0.141, 0.293] | 0.0 |
| GRADE+P53 − GRADE | +0.109 [0.043, 0.171] | 0.001 |
| GRADE+P53AB+IMG − GRADE+P53AB | +0.255 [0.201, 0.311] | 0.0 |
| GRADE+P53AB+LATE − GRADE+P53AB | +0.286 [0.221, 0.346] | 0.0 |
| GRADE+P53AB − GRADE | +0.041 [0.016, 0.074] | 0.0 |
| GRADE+IMG − L-IMG | +0.005 [-0.012, 0.021] | 0.54 |
| GRADE+LATE − L-LATE | -0.001 [-0.012, 0.008] | 0.852 |
| GRADE+IMG − GRADE+CNV | +0.047 [-0.021, 0.124] | 0.196 |
| L-IMG − raw_grade | +0.252 [0.182, 0.329] | 0.0 |

| Rows | Samples / patients (P) | L-CNV | L-IMG | L-LATE | Δ IMG − CNV | Δ LATE − IMG |
|---|---|---|---|---|---|---|
| NDBE samples only | 438 / 71 (28) | 0.780 [0.673, 0.869] | 0.827 [0.771, 0.885] | 0.867 [0.790, 0.928] | +0.047 [-0.041, 0.147] | +0.040 [-0.005, 0.081] |
| NDBE only, patient-weighted | 438 / 71 (28) | 0.811 [0.720, 0.882] | 0.838 [0.786, 0.888] | 0.886 [0.831, 0.930] | +0.027 [-0.057, 0.120] | +0.047 [0.006, 0.088] |
| Pairs sharing grade | 571 / 75 (32) | 0.782 [0.676, 0.869] | 0.830 [0.776, 0.886] | 0.870 [0.797, 0.929] | +0.048 [-0.040, 0.144] | +0.040 [-0.004, 0.080] |
| p53-normal samples only | 432 / 70 (30) | 0.767 [0.671, 0.853] | 0.848 [0.786, 0.903] | 0.884 [0.834, 0.930] | +0.081 [-0.028, 0.192] | +0.036 [-0.005, 0.078] |
| NDBE and p53-normal | 332 / 65 (25) | 0.757 [0.646, 0.853] | 0.837 [0.769, 0.897] | 0.874 [0.817, 0.925] | +0.080 [-0.040, 0.217] | +0.037 [-0.008, 0.081] |

Apparent (non-nested, optimistic): GRADE 0.601; GRADE+IMG 0.863; GRADE+CNV 0.818; GRADE+LATE 0.896; GRADE+P53 0.69; GRADE+P53+IMG 0.878; GRADE+P53+LATE 0.902; GRADE+P53+CNV 0.832; GRADE+P53AB 0.64; GRADE+P53AB+IMG 0.872; GRADE+P53AB+LATE 0.9.

### 5. Sensitivity rows

| Rows | Samples / patients (P) | L-CNV | L-IMG | L-LATE | Δ IMG − CNV | Δ LATE − IMG |
|---|---|---|---|---|---|---|
| Primary: original (Killcoyne sheet) labels | 571 / 75 (32) | 0.801 [0.710, 0.875] | 0.847 [0.798, 0.894] | 0.889 [0.830, 0.934] | +0.045 [-0.036, 0.136] | +0.042 [0.002, 0.078] |
| Database event dates (R53; eval-only) (−10) | 561 / 74 (31) | 0.791 [0.697, 0.869] | 0.847 [0.795, 0.897] | 0.884 [0.823, 0.931] | +0.056 [-0.029, 0.151] | +0.037 [-0.005, 0.074] |
| Sheet review 'inconsistent' removed (eval-only) (−25) | 546 / 75 (32) | 0.791 [0.698, 0.868] | 0.849 [0.799, 0.897] | 0.884 [0.824, 0.933] | +0.059 [-0.026, 0.150] | +0.035 [-0.004, 0.071] |
| Sheet 'excluded' flag removed (eval-only) (−57) | 514 / 71 (28) | 0.795 [0.692, 0.877] | 0.843 [0.789, 0.895] | 0.881 [0.810, 0.934] | +0.048 [-0.040, 0.146] | +0.038 [-0.005, 0.077] |
| Same block only (eval-only) (−15) | 556 / 75 (32) | 0.807 [0.715, 0.880] | 0.854 [0.806, 0.900] | 0.895 [0.836, 0.939] | +0.047 [-0.034, 0.138] | +0.042 [0.001, 0.078] |
| Refit r54: Barrett's database follow-up: later HGD relabelled progressor, later LGD patients excluded | 526 / 72 (33) | 0.731 [0.630, 0.824] | 0.812 [0.748, 0.866] | 0.838 [0.756, 0.903] | +0.081 [-0.004, 0.171] | +0.026 [-0.015, 0.065] |
| Refit r43c: the non-progressor with later HGD removed | 564 / 74 (32) | 0.798 [0.705, 0.874] | 0.848 [0.800, 0.894] | 0.887 [0.826, 0.935] | +0.050 [-0.027, 0.141] | +0.039 [0.001, 0.076] |
| Refit r43a: non-progressor samples < 12 months before the final endoscopy removed | 478 / 75 (32) | 0.783 [0.684, 0.862] | 0.824 [0.771, 0.876] | 0.867 [0.801, 0.920] | +0.041 [-0.048, 0.139] | +0.044 [-0.005, 0.086] |
| Refit r43b: non-progressor samples < 24 months before the final endoscopy removed | 456 / 75 (32) | 0.806 [0.712, 0.878] | 0.835 [0.779, 0.886] | 0.882 [0.813, 0.932] | +0.029 [-0.052, 0.121] | +0.047 [-0.002, 0.087] |
| Refit r52a: 8 progressors' linkable samples added: same case and block | 577 / 77 (34) | 0.801 [0.709, 0.873] | 0.862 [0.814, 0.908] | 0.895 [0.833, 0.941] | +0.061 [-0.019, 0.148] | +0.033 [-0.007, 0.066] |
| Refit r52b: 8 progressors' linkable samples added: also block unrecorded | 582 / 79 (36) | 0.789 [0.701, 0.867] | 0.870 [0.824, 0.914] | 0.898 [0.839, 0.942] | +0.081 [-0.000, 0.174] | +0.028 [-0.010, 0.063] |

Label check: sheet Status equals the sheet's original P/NP column for 571 of 571 pre-event samples. Refit reproduction (repeat 1, max |Δ| vs stored): {'L-CNV': 0.0, 'L-IMG': 0.0}. Same-block labels: {'same case, same block': 556, 'same case, block not recorded on one side': 9, 'same case, different block': 6}.

**Samples without a slide.** 97 of 773 published samples (progressor 83, non-progressor 14; pre-event {'progressor': 55, 'non_progressor': 14}); 8 patients have none, 51 samples come from patients who do.

| Published model P AUROC | Samples (P) | AUROC [95% CI] |
|---|---|---|
| all_773 | 773 (349) | 0.865 [0.796, 0.923] |
| with_slide | 676 (266) | 0.868 [0.794, 0.928] |
| without_slide | 97 (83) | 0.752 [0.552, 0.980] |
| pre_event_all | 640 (216) | 0.836 [0.747, 0.906] |
| pre_event_with_slide | 571 (161) | 0.828 [0.729, 0.907] |
| pre_event_without_slide | 69 (55) | 0.749 [0.503, 0.988] |

| Within class: without − with slide | P probability | CN burden | Reads | Grade | p53 aberrant | Year |
|---|---|---|---|---|---|---|
| progressor_all | 0.725 vs 0.695; SMD +0.097 [-0.376, 0.594] | 0.674 vs 0.556; SMD +0.379 [0.020, 0.732] | 24744920.012 vs 23685354.778; SMD +0.083 [-0.153, 0.534] | 1.072 vs 1.195; SMD -0.094 [-0.391, 0.235] | 0.258 vs 0.242; SMD +0.038 [-0.244, 0.336] | 2010.434 vs 2008.004; SMD +0.548 [0.056, 1.157] |
| progressor_pre_event | 0.724 vs 0.633; SMD +0.300 [-0.271, 0.903] | 0.661 vs 0.537; SMD +0.432 [-0.003, 0.806] | 24355316.611 vs 23886179.045; SMD +0.032 [-0.215, 0.595] | 0.709 vs 0.615; SMD +0.107 [-0.389, 0.587] | 0.211 vs 0.153; SMD +0.149 [-0.163, 0.539] | 2009.218 vs 2006.863; SMD +0.513 [-0.047, 1.214] |
| non_progressor_all | 0.455 vs 0.247; SMD +0.740 [-0.998, 1.725] | 0.464 vs 0.404; SMD +0.276 [-0.271, 1.130] | 22621076.929 vs 22244686.185; SMD +0.057 [-0.935, 0.631] | 0.214 vs 0.246; SMD -0.058 [-0.657, 0.642] | 0.0 vs 0.003; SMD -0.077 [-0.137, -0.069] | 2002.429 vs 2006.117; SMD -1.118 [-2.383, -0.745] |
| non_progressor_pre_event | 0.455 vs 0.247; SMD +0.740 [-0.998, 1.725] | 0.464 vs 0.404; SMD +0.276 [-0.271, 1.130] | 22621076.929 vs 22244686.185; SMD +0.057 [-0.935, 0.631] | 0.214 vs 0.246; SMD -0.058 [-0.657, 0.642] | 0.0 vs 0.003; SMD -0.077 [-0.137, -0.069] | 2002.429 vs 2006.117; SMD -1.118 [-2.383, -0.745] |

### What this changes in the plan

- The plan's line "copy number in small, low-yield biopsies is depth-limited" is not supported: small biopsies are not shallower, and copy number does not lose discrimination in them; the H&E model gains. Say instead that H&E discriminates better on small samples, and keep depth as a separate, unconfirmed limitation (CN is weakest in the shallowest tertile, but so is H&E).
- Report L-IMG with its selection-inclusive companion: the nested choice costs 0.02–0.03 AUROC, which turns the H&E − CN gap from +0.045 into about +0.02, consistent with "comparable".

### Implementation notes

- `fsa` is `rv4_round4.fsa` with the set's folds and labels passed in; patient weights 1/n_i per sample (pair weight 1/(n_i n_j)).
- Strata are evaluation subsets (pairs where both samples are in the stratum). DiD draws are paired on the same patient-bootstrap draw.
- Depth: total reads of the 50-kb readCountSummary × modal BAM read length / genome length (`dd_describe.py`).
- Grade models: per (repeat, outer fold), unpenalised logistic on pre-event training samples, image and copy-number scores entering as inner out-of-fold logits. 0 of 1,100 fits failed to converge.
- Selection: `ex_e3_score.py` `sel:` logic on the E3 refits; ensembles average probabilities in outer and inner predictions alike.
- R53 event dates use `rv7_round7.db_link`; same-block labels use `rv7d_sensfirst.same_block_labels` (both executed in their own namespaces).
- Panel: u_t from `explore_E1/u` (held-out fit, repeat mean); single-slide pre-event samples only; crops at level 1 with the extraction rule (coords are tile centres, top-left = centre − 112 at level 2, clamped). Tissue QC: share of pixels with saturation > 0.15 and not white ≥ 0.15, white < 0.30, ink < 0.02, dark < 0.30.
- **Found in passing:** `ex_e1_px.py` reads `coords_level` as top-left corners, so the E1 tile pixel flags are offset by half a tile (112 px), and its background flag (> 50% white) misses grey glass and coverslip-edge tiles. E1's "background tiles add almost nothing" may therefore understate artefact tiles; the panel shows them among the most positive tiles.

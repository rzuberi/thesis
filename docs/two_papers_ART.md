# Two papers, agent ART: does L-IMG read slide artefact?

21 October 2026. Rules: `paper/two_papers/RUN_RULES.md`. Trigger: P1B's pathologist panel (`docs/two_papers_P1B.md`) found that 22.5% of the 40 tiles pushing L-IMG most towards progression were glass, coverslip edge or out-of-focus artefact (none of the 40 most negative), and that `ex_e1_px.py` read tile centres as top-left corners and missed grey glass and coverslip edges, so E1's "background tiles barely affect the score" may be wrong.

## Plan

Population: the 571 pre-event samples (288 endoscopies, 75 patients, 32 progressors); models trained on set C (676 samples) as always. L-IMG tiles: 256 UNI2-h tiles per slide, 224 px at level 2 (about 0.88 µm/px), positions = tile centres (`extract_foundation_from_masks.py`: top-left = centre − 112, clamped).

1. **Per-tile QC flag (CPU only).** `tp_art_qc.py` re-reads every L-IMG tile at the correct position and stores pixel statistics only: stained-tissue share, white and grey glass, dark unstained pixels, straight unstained bands (coverslip edge), green/blue marker, Laplacian variance over tissue pixels (focus), tissue-mask share in the tile and its neighbourhood. Smoke: with E1's top-left reading the statistics must equal E1's stored values exactly. Flag = glass/background (tissue share < 0.25) or edge band or pen or blur (lowest 5% of tissue-pixel Laplacian variance); thresholds set by eye on calibration montages, then checked on random flagged vs unflagged montages and on P1B's top/bottom-40 tiles (`paper/two_papers/figs_ART/`, numbers only).
2. **Artefact fraction** per sample by class, scanner and sequencing batch (anonymised), with patient-bootstrap differences and permutation η²; artefact-only probe AUROC: each fraction alone (direction fixed: more artefact = progressor) and a nested logistic probe on all artefact features, overall and within batch.
3. **Clean-tile L-IMG.** Sample mean embedding over clean tiles; a sample with < 32 clean tiles is topped up to 32 with its least-artefactual flagged tiles (highest tissue share, then sharpest); also reported excluding those samples. Same recipe, folds and nested λ (`tp_art_refit.R` = `ex_e3_refit.R` with ART paths). Control: a random tile subset of the same size per sample. Smoke: the all-tile refit must reproduce the stored L-IMG exactly (0.847). Metrics: L-IMG, L-LATE, L-IMG − L-CNV, L-LATE − L-IMG, clean − stored, 2,000-draw patient bootstrap (`tp_p1b_main.py` `hblock`), overall, patient-weighted, within batch, within scanner. Paper 2: R49, memory, light tier and tier 0 (mean-logit + EW memory) rerun with the clean L-IMG through the E9 engine (`tp_art_gate.py`); smoke = the stored L-IMG reproduces E9 (31.1 / 31.8, 30.7 / 23.6, 30.5 / 21.5, 31.0 / 26.6).
4. **E1 recheck.** E1's flags at old and corrected positions; contribution of flagged tiles to the held-out logit (E1 tile scores u_t), score change when they are dropped (same fitted model), by class, and the AUROC of the substituted scores.

Scripts `scripts/paper_plan/tp_art_*.py` / `.R`; aggregates `results/paper_final/two_papers_ART/`; row-level `killcoyne_mm/two_papers_ART/`; figures `paper/two_papers/figs_ART/` (local); Slurm prefix `tpart`.

---

## Results

Aggregates: `results/paper_final/two_papers_ART/*.json` (`feats`, `frac`, `score`, `gate`, `e1`, `flag_validation`). Figures (local, numbers only): `paper/two_papers/figs_ART/` — `art_clean_tile_forest.png`, flag montages `art_flag_*.png`, calibration montages in `calib/`. Cluster campaigns `tpartq` (QC, 60 chunks), `tpartrb` (all-tile refit), `tpartrc` (clean / random / clean-without-blur refits), plus single epyc jobs for merge, montages, feats, frac, e1, score and gate. All CPU; no GPU job.

**L-IMG's performance partly survives removing artefact tiles: its AUROC falls from 0.847 to 0.811 (Δ −0.036 [−0.062, −0.011]), about nine times the loss from removing the same number of random tiles, which wipes out most of its lead over copy number (L-IMG − L-CNV +0.045 → +0.010 [−0.086, +0.114]), while L-LATE keeps most of its value (0.889 → 0.875).**

### Smoke checks

- Reading: with E1's top-left convention, `tp_art_qc.py` reproduces E1's stored white share and Laplacian variance exactly (max |Δ| 1e-16, 64 tiles); with the correct centre rule the white share differs by 0.14 on average, and by > 0.05 in 47% of tiles.
- Bags: 174,848 tiles, 683 slides, 676 samples; per-sample tile counts equal `bag_index`; the all-tile mean of the re-read bags equals `img_mean.csv` (max |Δ| 1.8e-7).
- Refit: the all-tile refit with `tp_art_refit.R` equals the stored L-IMG exactly (max |Δ prediction| 0.0, all 10 repeats). Metrics reproduce L-CNV / L-IMG / L-LATE 0.801 / 0.847 / 0.889 and the within-batch 0.790 / 0.841 / 0.893.
- Paper 2 engine: with the stored L-IMG, `tp_art_gate.py` reproduces E9: R49 31.1 / 31.8, memory 30.7 / 23.6, light tier 30.5 / 21.5, tier 0 31.0 / 26.6.
- E1 tile scores: b0 + mean u_t equals the stored logit (max |Δ| 1.4e-6 over 5,700 sample × repeat cells).

### 1. The artefact flag

Per tile (level 2, 224 px, centre rule), a tile is **artefact** if any of:
- **glass / background:** stained-tissue share (HSV saturation > 0.15, not white) < 0.15 — white or grey glass, coverslip edges and bubbles over glass, empty tiles;
- **edge:** a straight band (3-line running mean over rows or columns) with ≥ 50% dark unstained pixels over tissue (coverslip edge, bubble rim, fold);
- **pen / dye:** > 2% blue-green pixels (mostly margin dye or marker);
- **blur:** Laplacian variance over tissue pixels below the 5th percentile of non-background tiles (132.5).

Calibration montages (viewed before fixing the rule): tiles with tissue share 0.15–0.25 were mostly genuine tissue edges, so the glass cut is P1B's 0.15; a straight band of *any* unstained pixels flagged ordinary tissue borders and was dropped; the lowest 5% of tissue focus was visibly out of focus, the 5–10% band mostly sharp.

| Share of all 174,848 tiles | Glass / background | Edge | Pen / dye | Blur | Any artefact |
|---|---|---|---|---|---|
| All | 5.7% | 0.02% | 0.18% | 4.7% | 10.6% |
| Scanner C13239-01 | 6.1% | 0.02% | 0.06% | 5.8% | 11.9% |
| Scanner C13210 | 4.7% | 0.0% | 0.53% | 1.6% | 6.8% |

Validation:
- **Blind check** (40 flagged + 40 unflagged pre-event tiles, shuffled, called by eye before reading the key): agreement 69/80 (86%). Of the 35 tiles I called artefact, the rule flagged 32 (sensitivity 91%); of the 40 it flagged, 32 were artefact by eye (precision 80%). The 8 rule-only tiles were nearly all blur-flagged tiles that looked soft but readable; the blur component is the least precise, so a "blur kept" variant is reported too.
- **Random 96 unflagged tiles:** no clear artefact. **Random 96 flagged tiles:** glass, coverslip edges and bubbles all correct; blur tiles mixed (clearly out of focus to soft).
- **P1B's panel tiles:** of the 40 tiles pushing L-IMG most towards progression, 13 are flagged (9 glass / coverslip edge, 4 blur; P1B's 9 artefacts are all caught); of the 40 most negative, 1 (a dust blob). Over the top and bottom 120: 21 vs 6. Six of the top-40 tiles are coverslip edges over glass.

Clean tiles per sample: median 96.9%. Six slides (5 pre-event samples; < 5 progressor samples) keep < 32 clean tiles; rule: those samples are topped up to 32 with their least-artefactual flagged tiles (highest tissue share, then sharpest), and every result is also given excluding them (no change).

### 2. Artefact fraction by class, scanner and batch; artefact-only probe

Pre-event samples (`frac.json`; differences with 2,000-draw patient bootstrap):

| Artefact share of a sample's L-IMG tiles | Progressor (161) | Non-progressor (410) | P − NP [95% CI] |
|---|---|---|---|
| Any artefact, mean (median) | 15.4% (6.3%) | 8.6% (2.3%) | +6.8 points [+3.0, +10.4] |
| Glass / background | 8.9% | 4.5% | +4.4 [+1.5, +7.3] |
| Blur | 6.5% | 4.1% | +2.4 [−0.5, +5.2] |
| Edge, pen / dye | < 0.1% | < 0.1% | ≈ 0 |

- **By scanner:** the progressor excess is entirely on scanner C13239-01 (progressors 17.9%, non-progressors 9.1%); on C13210 the classes are equal (7.5% vs 7.1%). C13239-01 slides carry more blur (5.8% vs 1.8% of tiles; Δ +3.9 [+2.3, +5.6]).
- **By sequencing batch** (12 batches, anonymised by size): batch means range 4.9%–17.6%; the highest is the all-progressor batch. η² 0.047 (permutation p 0.011); within non-progressors η² 0.041 (p 0.053), within progressors 0.027 (p 0.75). Glass share alone: η² 0.076 (p 0.003), within non-progressors 0.060 (p 0.012).
- **Artefact-only probes** (fold-stratified AUROC, repeat mean):

| Probe | AUROC [95% CI] | Within batch [95% CI] |
|---|---|---|
| Any-artefact fraction (no fitting; more = progressor) | 0.649 [0.580, 0.711] | 0.587 [0.456, 0.702] |
| Glass / background fraction | 0.664 [0.589, 0.736] | 0.591 [0.462, 0.729] |
| Blur fraction | 0.535 [0.455, 0.599] | 0.496 [0.348, 0.601] |
| Nested logistic on all artefact features | 0.662 [0.589, 0.732] | 0.620 [0.489, 0.785] |

So slide quality alone predicts progression at about 0.65, mostly through glass on one scanner and in some batches; within batch the signal shrinks and its interval includes 0.5. The artefact fraction correlates weakly with the held-out L-IMG logit within class (Spearman 0.10 in progressors, 0.16 in non-progressors).

### 3. Clean-tile L-IMG (same recipe, folds and nested λ)

`score.json`; fold-stratified AUROC, 571 pre-event samples, 2,000-draw patient bootstrap, paired Δ:

| Rows | L-CNV | L-IMG clean | L-LATE clean | L-IMG published | L-IMG random-removal control | Clean − published L-IMG | L-IMG − L-CNV (clean) | L-LATE − L-IMG (clean) |
|---|---|---|---|---|---|---|---|---|
| All pairs | 0.801 [0.710, 0.875] | **0.811** [0.753, 0.872] | 0.875 [0.812, 0.925] | 0.847 [0.798, 0.894] | 0.843 [0.793, 0.893] | **−0.036** [−0.062, −0.011] | +0.010 [−0.086, +0.114] | +0.063 [+0.013, +0.111] |
| Patient-weighted | 0.822 | 0.832 [0.775, 0.884] | 0.891 | 0.852 | 0.848 | −0.020 [−0.042, +0.001] | +0.010 [−0.072, +0.102] | +0.059 [+0.016, +0.102] |
| Within sequencing batch | 0.790 [0.675, 0.916] | 0.813 [0.706, 0.915] | 0.879 [0.757, 0.969] | 0.841 | 0.834 | −0.028 [−0.071, +0.009] | +0.023 [−0.100, +0.160] | +0.066 [+0.004, +0.119] |
| Within batch, patient-weighted | 0.814 | 0.825 | 0.886 | 0.850 | 0.840 | −0.025 [−0.066, +0.011] | +0.010 [−0.109, +0.147] | +0.062 [+0.001, +0.122] |
| Within scanner | 0.799 | 0.821 [0.760, 0.881] | 0.877 | 0.856 | 0.851 | −0.036 [−0.065, −0.007] | +0.022 [−0.072, +0.130] | +0.056 [+0.004, +0.104] |
| NDBE only | 0.780 | 0.802 [0.739, 0.866] | 0.856 | 0.827 | 0.821 | −0.025 [−0.048, −0.003] | +0.022 [−0.070, +0.127] | +0.054 [−0.000, +0.100] |
| Excluding the 5 samples with < 32 clean tiles | 0.799 | 0.812 | 0.874 | 0.845 | 0.842 | −0.034 [−0.060, −0.010] | +0.013 [−0.083, +0.117] | +0.062 [+0.011, +0.111] |

- **Control:** dropping the same number of random tiles costs −0.004 [−0.012, +0.004]; clean minus random −0.032 [−0.057, −0.007]. The loss is specific to artefact tiles, not to having fewer tiles.
- **Which artefact:** removing glass, edge and pen tiles but keeping blur gives 0.829 (−0.018 [−0.038, −0.000]); blur removal accounts for the other half.
- **L-LATE** clean 0.875 vs 0.889 published (−0.014 [−0.024, −0.003]); still +0.073 [+0.021, +0.133] over L-CNV.
- **Before, for comparison:** published L-IMG − L-CNV +0.045 [−0.036, +0.136], within batch +0.051.

**Paper 2 rules with the clean L-IMG** (`gate.json`; nested, held-out, repeat mean; caught of 32 progressor patients / non-progressor patients flagged of 43 / samples sequenced per patient; Δ paired):

| Rule | Published L-IMG | Clean L-IMG | Δ caught | Δ NP flagged | Random-removal control Δ NP flagged |
|---|---|---|---|---|---|
| R49 gate | 31.1 / 31.8 / 1.94 | 31.3 / 32.8 / 2.16 | +0.2 [0.0, +0.5] | +1.0 [−0.8, +3.1] | +1.5 [+0.3, +3.0] |
| Memory (gate score, EW) | 30.7 / 23.6 | 30.7 / 25.1 | 0.0 [−0.8, +0.9] | +1.5 [−0.7, +3.9] | +1.6 [+0.1, +3.1] |
| Light tier (A12) | 30.5 / 21.5 | 30.5 / 23.5 | 0.0 [−0.7, +0.8] | +2.0 [−0.3, +4.3] | +1.1 [−0.4, +2.6] |
| Tier 0 (mean-logit + memory, no sequencing) | 31.0 / 26.6 / 0 | 31.1 / 29.7 / 0 | +0.1 [−0.7, +1.0] | **+3.1 [+0.4, +6.0]** | +0.3 [−1.4, +2.0] |

R49 sequences more with the clean score (2.16 vs 1.94 samples per patient; +0.22 [+0.10, +0.35]) because more endoscopies fall in its middle band. Tier 0, the recommended no-sequencing rule, flags about 3 more non-progressor patients (26.6 → 29.7), beyond what random tile removal does. The confirmatory tier was not rerun (its quiet-genome check arrays are built on the published R49 bands).

### 4. E1's background conclusion, rechecked

`e1.json`; E1 tile scores u_t (held-out fit), pre-event samples:

- **Positions:** at the corrected centres, E1's own background rule (> 50% white) flags 4.3% of tiles instead of 5.7%, and the tile-level overlap is poor (4,655 tiles flagged at both positions, 5,249 only at the old, 2,934 only at the new). E1's flag also misses most artefact: only 11% of ART-flagged tiles were E1 background tiles.
- **E1's narrow claim holds:** dropping E1-background tiles (old or corrected positions) leaves the AUROC at 0.846–0.847 (Δ 0.000 [−0.007, +0.006]).
- **The broad reading does not:** artefact tiles push the score up in both classes (mean tile score u: artefact 5.3 in progressors and 3.3 in non-progressors, against 1.8 and −2.2 for clean tiles). They add 0.59 [0.32, 0.88] logit more to progressor than to non-progressor samples. Dropping them from the same fitted model costs −0.016 [−0.031, −0.001] AUROC (glass alone −0.012 [−0.028, +0.002]); refitting without them costs −0.036 (section 3).
- E1's "core" result (dropping its edge tiles costs −0.043) is about tissue-border tiles, which are mostly genuine tissue (E1's background + edge rule covers 45% of tiles); corrected positions give −0.049 [−0.082, −0.018].

So E1's statement that "background tiles add almost nothing to the score" is true only for its white-pixel background definition. Correcting the coordinates alone does not change it. With grey glass, coverslip edges and blur counted, artefact tiles carry a progression-like signal worth about 0.02–0.04 AUROC.

### What this changes in the plan

- Paper 1: report L-IMG on clean tiles (0.811) as the primary H&E number, or at least alongside 0.847, with the artefact-only probe (0.65) as a named confound. "H&E beats copy number" becomes "comparable" (+0.010), which agrees with P1B's selection-inclusive +0.014 to +0.026. L-LATE's gain over each modality holds (+0.063 over clean L-IMG, +0.073 over L-CNV).
- Paper 2: the R49 gate barely moves, but tier 0's saving over R49 shrinks from 5.2 to 3.1 non-progressor patients (26.6 → 29.7 flagged). Retest the frozen tiers with tile QC applied (and decide whether the frozen bundle should be rebuilt on clean tiles) before registration. Tile QC also has to run in the ERIN and 4× pipelines, because scanner C13239-01 carries most of the blur.

### Implementation notes

- `tp_art_qc.py` (CPU, the only script reading pixels): bag order = `km_prep.py` (slides sorted by npz, stored tile order); top-left = centre − 112, clamped (`extract_foundation_from_masks.py`); statistics only, no pixels saved.
- `tp_art_main.py`: tasks merge / describe / montage_* (CPU, reads tiles for montages only) / feats / frac / score / e1; metric helpers from `tp_p1b_main.py` (module body executed, no branch run).
- `tp_art_refit.R` = `ex_e3_refit.R` with the ART input and output directories (coefficients not written).
- `tp_art_gate.py`: E9 engine executed unchanged; L-IMG swapped through E3 `variant()` with `RD` pointed at the ART refits; tier 0 uses E3's mean-logit construction with the 1e-6 sample tie-break; `pick()` copied from `tp_reg_freeze.py`.
- Artefact-probe fits: L2 logistic (C = 1) on standardised per-sample fractions + log median tissue focus, trained on each outer fold's set C training rows.
- Batch labels are anonymised (B1 = largest). Cells < 5 shown as "<5".

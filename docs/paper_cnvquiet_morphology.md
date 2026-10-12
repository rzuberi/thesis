# What the image sees in CNV-quiet progressors: a fixed nuclear feature panel

Status: PRE-SPECIFICATION (written 2026-10-12). No feature has been measured on any group sample. Before this commit only the following was done: the segmentation environment was installed, and an end-to-end smoke test (tile extraction, segmentation, overlay check) was run on two slides from post-event progressor samples, which belong to none of the groups below; no feature was computed from them. Results are appended under the line at the end in a later commit, and this section is not edited afterwards.

**Ground rules** (as in `docs/paper_horizon_q2_all_horizons.md`, pre-specification e645dcf, results aa7cfe2):
- No prediction model is fitted or refitted. The groups come from stored predictions; nothing measured here feeds back into any predictor.
- Report only, with a status per item and at most one line of interpretation per question.
- Earlier documents are not edited. Patient lists, per-sample rows and per-nucleus tables stay on the cluster; only aggregates enter the repo.
- Source data and slides are read-only.

**Why.** At 3 and 5 years, the progressor samples newly caught by late fusion (L-LATE) but missed by CNV alone (L-CNV) are CNV-quiet (mean raw cx 21 vs 30 for cases both catch; `docs/paper_horizon_q2_all_horizons.md`). This asks whether their tissue differs from non-progressor tissue of the same CNV complexity in a few interpretable nuclear features taken from the oral-dysplasia and nuclear-morphology literature (Bashir 2023, Shephard 2024, Mahmood 2023, Abel 2024). It is supportive evidence for the discussion, not a test that can carry the paper.

## Population and groups

Population: the 676 samples from 80 patients of the Killcoyne discovery cohort with a matched H&E slide. All groups are pre-event samples.

**Source of (a) and (b).** The Q2 per-sample list of `scripts/paper_plan/ha_q2.py` (commit afa0278), cluster-only `killcoyne_mm/horizon_answers/q2_patient_list.csv`, rows with `src == "their"` and `comparison == "L-LATE vs L-CNV"`: their CNV matrix, 80%-sensitivity operating point per horizon, ≥ 6-of-10 vote, all pre-event samples. The per-horizon counts must reproduce `docs/paper_horizon_q2_all_horizons.md` (newly caught 11 samples / 6 patients at 3 years, 13 / 8 at 5 years; caught by both 73 / 26 and 91 / 28). If they do not, the analysis stops.

| Group | Definition | Expected size |
|---|---|---|
| (a) CNV-quiet newly caught progressor samples | Union over the 3- and 5-year horizons of `captured_cases_CNVneg_bestpos` (horizon case, negative under L-CNV, positive under L-LATE) | 13 samples / 8 patients (the 3-year set lies inside the 5-year set, checked when the counts were verified) |
| (b) Progressor samples caught by both | Union over 3 and 5 years of `cases_both_pos`, excluding any sample in (a) | 91 samples / 28 patients (no overlap with (a) at sample level; 6 of the 8 (a) patients also have (b) samples) |
| (c) CNV-matched non-progressor samples | Matched to (a) by the rule below | 39 samples (3 per (a) sample) |

- Union, not per horizon, is primary because the groups are small and the 3-year set is nested in the 5-year set. The 3-year-only (a) (11 / 6) is a secondary, descriptive comparison against the (c) samples matched to those 11.
- **Matching rule for (c)**, written before any feature is measured:
  - Candidates: non-progressor (`y == 0`) pre-event samples (410 samples, 43 patients).
  - Exact match on scanner (`horizons/slide_desc.csv`: C13210 / C13239-01) and on grade class (NDBE vs ID/LGD, `Pathology`). Scanner, because the image representation identifies the scanner perfectly (`docs/paper_latent_attention.md`); grade, because dysplasia changes nuclear morphology by definition.
  - Nearest raw cx: the package `cx` of `cnv_pkg_C.csv`, de-scaled with the frozen constants of `models/killcoyne_frozen_pkg_v1/cnv_scaling_setC.csv` (row `kind == "cx"`); this is the cx of `docs/paper_horizon_q2_all_horizons.md`.
  - 3 controls per (a) sample, without replacement. Three round-robin rounds: in each round every (a) sample, in one fixed order drawn with `numpy.random.default_rng(20261012)`, takes its nearest unused candidate; ties in |Δcx| are broken by a random key per candidate drawn from the same generator.
  - Balance reported: raw cx, grade, scanner, tissue tiles, |Δcx| (mean, maximum, number exact), samples per patient.
- Slides per sample: every `uni2_npz_map.csv` row of the sample (union of the sample's slides, as `km_prep.py`).

## Image regions

- **Tiles.** The stored UNI2 tiles that the image model averaged: the 256 `coords_level` per slide in the sample's npz (pyramid level 2, 224 px, about 198 µm square). Using these tiles, not all tissue, measures what the image model saw and bounds the cost.
- **Re-read** at level 0 (about 0.22 µm/px, `openslide.mpp-x`): a square of round(224 × level-2 downsample) px at (x, y) × downsample, resampled with Lanczos to 0.25 µm/px (the PanNuke training resolution; about 790 px), saved as JPEG quality 95. CPU jobs read slides; GPU jobs read only these files.
- **Coordinate check:** for the first 4 tiles of every slide, the level-0 read downsampled to 224 px must correlate (Pearson, grey) ≥ 0.95 with the level-2 read the embedding used. Slides that fail are reported and excluded. (Smoke: 0.992–0.998.)

## Segmentation model

- **HoVer-Net, fast mode, PanNuke weights**, as distributed by TIAToolbox 2.1.3 (`hovernet_fast-pannuke`, HF repo `TIACentre/TIAToolbox_pretrained_weights`, file SHA-256 `789b2be8bdaf532627f584a009f83b3ba06e04c0e55c1635252ff12785ef57e8`), torch 2.9.1+cu128, env `/mnt/scratche/slow/fmlab/zuberi01/envs/cq_tia`.
- Inference: each tile reflect-padded by 46 px (plus padding to a multiple of 164), 256-px input / 164-px output sliding window with stride 164, maps assembled and cropped to the tile, then TIAToolbox's own HoVer-Net post-processing (`HoVerNet._proc_np_hv` and `get_instance_info`). No stain normalisation (Bashir 2023 normalised; this is a stated difference).
- **Classes** (PanNuke): 1 neoplastic, 2 inflammatory, 3 connective, 4 dead, 5 non-neoplastic epithelial. **Epithelial = classes 1 and 5** (PanNuke's neoplastic/non-neoplastic split is not trusted for Barrett's; the share called neoplastic is reported per group as QC, not tested).
- **Inflammatory** (class 2) includes lymphocytes, plasma cells, neutrophils and macrophages; PanNuke has no lymphocyte-only class. **Plasma-cell density is not measurable** with this model (no plasma-cell class) and is dropped from the panel.
- **Per nucleus:** tile, centroid, area = instance pixel count × 0.0625 µm², perimeter = closed contour length (`cv2.arcLength`) × 0.25 µm, type, type probability, edge flag (bounding box within 2 px of the tile edge).

## Feature panel (fixed)

Nuclei < 5 µm² are dropped everywhere. Edge nuclei are dropped from F1–F3 only. All neighbourhoods are computed within a tile (tiles are separate images). Per sample, nuclei are pooled over all tiles of all its slides.

| Code | Feature | Definition | Source |
|---|---|---|---|
| F1 | Epithelial nuclear area, mean | Mean area (µm²) of non-edge epithelial nuclei | Abel 2024 |
| F2 | Epithelial nuclear area, variability | SD (µm², ddof 1) of the same areas | Abel 2024 (SD of cancer nuclear area), Yu 2023 |
| F3 | Epithelial nuclear circularity | Mean of 4πA/P², clipped to [0, 1], over the same nuclei | Mahmood 2023 |
| F4 | Basal-layer nuclear density | Basal-layer nuclei = epithelial nuclei with a connective-tissue (class 3) nucleus centroid within 25 µm. F4 = mean, over basal-layer nuclei, of the number of other epithelial nuclei with a centroid within 20 µm | Bashir 2023 (basal-layer nuclei count) |
| F5 | Peri-epithelial lymphocyte density | Inflammatory nuclei with an epithelial centroid within 50 µm, per 100 epithelial nuclei (pooled counts) | Bashir 2023, Shephard 2024 |

- **Why F4 and F5 are proxies.** Bashir and Shephard use HoVer-Net+ layer segmentation of oral squamous epithelium (basal, epithelial, keratin layers). Barrett's mucosa is glandular and columnar, there is no Barrett's gland or layer segmenter available, and HoVer-Net+ was not trained on it. So "basal layer" is operationalised as the stroma-facing epithelial nuclei, and density as local crowding among them (stratification and crowding are the dysplastic changes); "peri-epithelial" is a 50 µm centroid distance, which also counts intra-epithelial inflammatory cells.
- **Eligibility:** a sample needs ≥ 200 non-edge epithelial nuclei for F1–F3 and F5, and ≥ 50 basal-layer nuclei for F4; otherwise that feature is missing for the sample. Counts of ineligible samples are reported.

## Tests

- **Unit of analysis: the patient.** Samples are clustered in patients (13 (a) samples from 8 patients). For each group and feature, a patient's value is the mean over that patient's eligible samples in the group. A patient with samples in both (a) and (b) contributes to each group separately; (a) and (c) share no patient by construction.
- **Primary: (a) vs (c), per feature.** Two-sided Mann–Whitney U on patient values (`scipy.stats.mannwhitneyu`, exact when there are no ties, otherwise asymptotic), two-sided because the direction of an immune difference is not known in advance (Pennycuick 2020 vs Bashir 2023 / Ercan 2025). **Holm** adjustment over the five features (over the features actually estimable if any is not; a feature needs ≥ 3 patients with a value in each group). α 0.05 on Holm-adjusted p.
- **Effect sizes:** difference in patient-level means (a − c) with a 95% patient-bootstrap CI (2,000 draws, `RandomState(0)`, patients resampled within each group); AUC = U / (n_a n_c), the probability that an (a) patient's value exceeds a (c) patient's.
- **(b), descriptive only:** patient-level mean and SD; (b − c) and (b − a) differences with the same bootstrap CIs and AUC; no p-values.
- **Secondary, descriptive:** 3-year-only (a) vs its matched (c) samples (unadjusted Mann–Whitney p); sample-level means and SDs per group; matched-set differences (each (a) sample minus the mean of its 3 matches: mean, and how many are above).
- **QC per group:** nuclei total, epithelial nuclei, share of epithelial nuclei called neoplastic, inflammatory per 100 epithelial (all distances), median epithelial nuclei per sample, share of tiles with any epithelial nucleus, ineligible samples.

## Compute

- Phase 1 (CPU, env `erin`): `scripts/paper_plan/cq_extract.py`, one task per slide shard. Phase 2 (GPU, env `cq_tia`): `cq_segment.py`, never reads slides, cuda (L40S) paired with h200. Both through `scripts/cluster/campaign.sh`, prefixes cq3 (groups, then extract), cq4 (segment) and cq5 (features, statistics, figure); cq0–cq2 were the environment and the smoke test.
- Budget cap 15 GPU-hours. Smoke test: 141–180 s per slide (256 tiles, one L40S, 7 post-processing CPU workers, including 6 overlays), so about 150 slides of (a) + (b) + (c) project to roughly 6–8 GPU-hours. If the projected total exceeds the cap, the run stops before phase 2 and this is reported; (b) is not silently subsampled.
- Overlays of 6 tiles per smoke slide were inspected before this commit: gland nuclei are outlined and called epithelial or neoplastic, stromal nuclei connective; some small round stromal cells that look like lymphocytes are called connective, so F5 may undercount inflammatory cells (the same model is applied to every group). One overlay from a slide outside all groups is used in the figure (no identifiers).

## Outputs

- **Scripts** (`scripts/paper_plan/`): `cq_groups.py` (groups, matching, count check), `cq_extract.py`, `cq_segment.py`, `cq_features.py`, `cq_stats.py`, `cq_fig.py`, `cq_render.py`.
- **Aggregates:** `results/paper_final/cnvquiet_morphology/` (`groups.json`, `stats.json`, `segmentation_qc.json`).
- **Cluster only:** under `feasibility/paper_plan/killcoyne_mm/cnvquiet_morphology/`: `groups.csv`, `slides.csv`, `tiles/`, `nuclei/`, `features_sample.csv`, `fig_patient_values.csv`, overlays.
- **Figure:** `be_paper_figs/v3/16_F_cnvquiet_morphology.{pdf,png}`: per feature, patient values for (a), (b) and (c) with means; one segmentation overlay. Drawn on the cluster and copied.

## Questions (one line each, in the results)

1. Do CNV-quiet newly caught progressor samples differ from CNV-, grade- and scanner-matched non-progressor samples in epithelial nuclear area (mean or SD)?
2. Do they differ in epithelial nuclear circularity?
3. Do they differ in basal-layer nuclear density (crowding proxy)?
4. Do they differ in peri-epithelial lymphocyte density, and in which direction?
5. Where do the progressor samples caught by both models sit on the same features (descriptive)?
6. Is plasma-cell density measurable with the chosen model? (Expected: no.)

---

## Results

Pre-specification commit a50ce7b; results commit ed31053. Scripts `scripts/paper_plan/cq_groups.py`, `cq_extract.py`, `cq_segment.py`, `cq_features.py`, `cq_stats.py`, `cq_fig.py`, `cq_render.py` (Slurm via `scripts/cluster/campaign.sh`, prefixes cq0, cq0b (environment), cq1, cq2 (smoke), cq3a (groups), cq3, cq3b, cq4, cq4d, cq5, cq5b (first run, offset tiles), cq6, cq7, cq8 (corrected run, (a) and (c))). Aggregates `results/paper_final/cnvquiet_morphology/`. Row-level outputs on the cluster only.

**Two runs.** The first run (results commit 889f080, rendered in 15ac82b) read the npz `coords_level` as tile top-left corners. They are tile centres (`barretts_training/scripts/extract_foundation_from_masks.py`, `extract_tiles`: top-left = centre − 112 px, clamped), so every tile was shifted half a tile (about 99 µm) right and down and overlapped the tile the image model saw by a quarter. (a) and (c) were re-extracted and re-segmented with the centre rule; those results are primary. (b) was not re-run, because re-segmenting its 94 slides would take the total over the 15 GPU-hour cap, so (b) is reported from the offset run only, against (a) and (c) from the same run.

### Status

| Item | Status |
|---|---|
| Groups from stored outputs; per-horizon counts equal docs/paper_horizon_q2_all_horizons.md | DONE; all four counts match (11/6, 13/8, 73/26, 91/28) |
| (c) matching | DONE; 39 samples / 23 patients, mean absolute Δcx 0.46 |
| Tile re-read at tile centres, (a) and (c) | DONE; 52 slides, none excluded by the coordinate check on tissue tiles |
| Segmentation (HoVer-Net fast, PanNuke, TIAToolbox 2.1.3), corrected tiles | DONE; 52 slides, 13,312 tiles, 2.30 M nuclei |
| Features F1–F5, primary tests (a) vs (c), Holm | DONE; no feature significant after Holm |
| Plasma-cell density | NOT MEASURABLE (no plasma-cell class in PanNuke) |
| (b) descriptive | PARTIAL: offset tiles only (not re-run within the GPU cap) |
| Figure 16_F_cnvquiet_morphology | DONE ((a) and (c), corrected tiles) |

### Groups

Patient counts are distinct patients; (a) and (b) share patients (6 of the 8 (a) patients also have (b) samples). Raw cx = package block.

| Group | Samples | Patients | Slides | Raw cx, mean (SD) | Raw cx, median | Grade | Scanner | Tissue tiles, median | Max samples per patient |
|---|---|---|---|---|---|---|---|---|---|
| (a) CNV-quiet newly caught | 13 | 8 | 13 | 21.2 (5.7) | 19 | ID 1, LGD 5, NDBE 7 | C13210 5, C13239-01 8 | 211 | 3 |
| (b) caught by both | 91 | 28 | 94 | 29.5 (12.6) | 26 | ID 9, LGD 28, NDBE 54 | C13210 20, C13239-01 71 | 278 | 9 |
| (c) matched non-progressors | 39 | 23 | 39 | 21.3 (5.6) | 20 | ID 14, LGD 4, NDBE 21 | C13210 15, C13239-01 24 | 228 | 4 |

Count check against `docs/paper_horizon_q2_all_horizons.md`: 3y captured_cases_CNVneg_bestpos 11 / 6 (ok); 5y captured_cases_CNVneg_bestpos 13 / 8 (ok); 3y cases_both_pos 73 / 26 (ok); 5y cases_both_pos 91 / 28 (ok).
Matching: mean absolute Δcx 0.46, maximum 3, exact 26 of 39. (a) samples also newly caught at 3 years: 11.

### Segmentation

- **Corrected tiles ((a) and (c)):** slides 52, tiles 13,312; coordinate check on tissue tiles: minimum r 0.964, slides failing 0 (pre-specified all-tile rule: 3 would fail, minimum r 0.884); level-0 mpp 0.2204–0.2209, tiles 790, 792 px at about 0.25 µm/px; nuclei kept (≥ 5 µm²) 2,301,135.
- **Offset tiles (first run, all groups):** slides 146, tiles 37,376; coordinate check on tissue tiles: minimum r 0.967, slides failing 0 (pre-specified all-tile rule: 25 would fail, minimum r 0.533); level-0 mpp 0.2204–0.2209, tiles 790, 792 px at about 0.25 µm/px; nuclei kept (≥ 5 µm²) 5,708,539.
- GPU: 10.2 GPU-hours allocated over 57 L40S jobs in total (first run 8.2 including the smoke test, start-up and duplicate twins; corrected run 2.0), under the 15-hour cap; about 150 s per slide.

| Run | Group | Nuclei | Epithelial nuclei | Share of epithelial called neoplastic | Inflammatory per 100 epithelial (any distance) | Median epithelial nuclei per sample | Tiles with epithelium | Samples ineligible F1–F3, F5 / F4 |
|---|---|---|---|---|---|---|---|---|
| corrected | (a) CNV-quiet newly caught | 569,924 | 176,173 | 0.531 | 39.7 | 12345 | 0.897 | 0 / 0 |
| corrected | (c) matched non-progressors | 1,731,211 | 573,838 | 0.533 | 36.4 | 14365 | 0.877 | 0 / 0 |
| offset | (a) CNV-quiet newly caught | 533,151 | 163,420 | 0.527 | 41.0 | 11366 | 0.828 | 0 / 0 |
| offset | (b) caught by both | 3,540,529 | 1,288,864 | 0.522 | 30.3 | 14206 | 0.788 | 2 / 1 |
| offset | (c) matched non-progressors | 1,634,859 | 535,083 | 0.528 | 37.3 | 13138 | 0.827 | 0 / 0 |

### Primary: (a) vs (c), patient level, corrected tiles

Patient value = mean over the patient's eligible samples in the group. Δ = (a) − (c) patient-level means, 95% patient-bootstrap CI. AUC = P((a) patient > (c) patient). Two-sided Mann–Whitney U; Holm over the five features.

| Feature | Patients a / c | (a) mean (SD) | (c) mean (SD) | Δ (a − c) [95% CI] | AUC | p | Holm p |
|---|---|---|---|---|---|---|---|
| F1 epithelial nuclear area, mean (µm²) | 8 / 23 | 28.3 (2.148) | 31.2 (2.787) | -2.876 [-4.619, -1.228] | 0.212 | 0.016 | 0.078 |
| F2 epithelial nuclear area, SD (µm²) | 8 / 23 | 15.2 (1.507) | 16.6 (2.548) | -1.328 [-2.755, 0.018] | 0.348 | 0.219 | 0.877 |
| F3 epithelial nuclear circularity, mean | 8 / 23 | 0.843 (0.009) | 0.843 (0.016) | 0.000 [-0.008, 0.009] | 0.451 | 0.707 | 1.000 |
| F4 basal-layer crowding (epithelial nuclei within 20 µm) | 8 / 23 | 6.625 (0.907) | 6.722 (0.991) | -0.097 [-0.803, 0.633] | 0.478 | 0.877 | 1.000 |
| F5 peri-epithelial inflammatory nuclei per 100 epithelial nuclei | 8 / 23 | 29.4 (21.0) | 27.9 (14.4) | 1.508 [-11.7, 17.4] | 0.495 | 0.982 | 1.000 |

### (b) progressor samples caught by both, descriptive (no tests), offset tiles

(b) was measured only in the first run, whose tiles are offset by half a tile; (b) is compared with (a) and (c) from the same run, so all three share the offset.

| Feature | Patients | (b) mean (SD) | Δ (b − c) [95% CI] | AUC (b > c) | Δ (b − a) [95% CI] |
|---|---|---|---|---|---|
| F1 epithelial nuclear area, mean (µm²) | 27 | 30.7 (2.409) | -0.385 [-1.798, 1.051] | 0.436 | 2.401 [0.740, 4.213] |
| F2 epithelial nuclear area, SD (µm²) | 27 | 16.3 (1.588) | -0.187 [-1.311, 0.851] | 0.494 | 1.170 [0.063, 2.511] |
| F3 epithelial nuclear circularity, mean | 27 | 0.843 (0.011) | -0.000 [-0.007, 0.007] | 0.452 | 0.000 [-0.008, 0.007] |
| F4 basal-layer crowding (epithelial nuclei within 20 µm) | 27 | 6.545 (0.994) | -0.168 [-0.769, 0.390] | 0.481 | -0.028 [-0.667, 0.617] |
| F5 peri-epithelial inflammatory nuclei per 100 epithelial nuclei | 27 | 25.4 (13.6) | -3.232 [-11.2, 4.546] | 0.440 | -6.282 [-24.8, 9.051] |

### Record: (a) vs (c) on the offset tiles (first run, superseded)

Same tests on tiles shifted by half a tile (about 99 µm right and down; a quarter of each true tile). Kept because it measures nearby tissue of the same biopsies and is the only run that includes (b).

| Feature | Patients a / c | (a) mean (SD) | (c) mean (SD) | Δ (a − c) [95% CI] | AUC | p | Holm p |
|---|---|---|---|---|---|---|---|
| F1 epithelial nuclear area, mean (µm²) | 8 / 23 | 28.3 (2.361) | 31.0 (2.774) | -2.786 [-4.704, -0.965] | 0.223 | 0.020 | 0.102 |
| F2 epithelial nuclear area, SD (µm²) | 8 / 23 | 15.1 (1.642) | 16.5 (2.302) | -1.357 [-2.757, -0.065] | 0.337 | 0.187 | 0.747 |
| F3 epithelial nuclear circularity, mean | 8 / 23 | 0.842 (0.010) | 0.843 (0.015) | -0.001 [-0.009, 0.008] | 0.435 | 0.611 | 1.000 |
| F4 basal-layer crowding (epithelial nuclei within 20 µm) | 8 / 23 | 6.573 (0.817) | 6.713 (1.064) | -0.140 [-0.841, 0.527] | 0.478 | 0.877 | 1.000 |
| F5 peri-epithelial inflammatory nuclei per 100 epithelial nuclei | 8 / 23 | 31.7 (25.4) | 28.6 (15.3) | 3.050 [-12.2, 22.3] | 0.489 | 0.947 | 1.000 |

### Secondary, descriptive, corrected tiles

| Feature | 3-year (a) vs its matches: patients, Δ, unadjusted p | Sample-level means a / c | Matched sets: mean (a − matches), (a) above |
|---|---|---|---|
| F1 | 6 / 18, -2.768, 0.033 | 29.0 / 31.3 | -2.289, 3 of 13 |
| F2 | 6 / 18, -1.596, 0.156 | 15.3 / 16.6 | -1.253, 4 of 13 |
| F3 | 6 / 18, 0.000, 0.673 | 0.845 / 0.842 | 0.002, 6 of 13 |
| F4 | 6 / 18, 0.119, 0.673 | 6.617 / 6.688 | -0.071, 4 of 13 |
| F5 | 6 / 18, -4.253, 0.581 | 31.1 / 28.3 | 2.834, 6 of 13 |

### Answers

1. Nuclear area: CNV-quiet newly caught patients had a smaller mean epithelial nuclear area than matched non-progressors (28.3 vs 31.2 µm², Δ −2.9 [−4.6, −1.2], AUC 0.21, p 0.016), not significant after Holm (p 0.078); the SD did not differ (Δ −1.3 µm², Holm p 0.88). If anything the nuclei are smaller, not the enlarged nuclei that track aneuploidy (Abel 2024).
2. Circularity: no difference (0.843 vs 0.843, Holm p 1.00).
3. Basal-layer crowding: no difference (6.63 vs 6.72 epithelial nuclei within 20 µm, Holm p 1.00).
4. Peri-epithelial inflammatory density: no difference and no direction (29.4 vs 27.9 per 100 epithelial nuclei, Δ +1.5 [−11.7, +17.4], Holm p 1.00).
5. Caught by both (offset tiles only): close to the matched non-progressors on every feature (nuclear area 30.7 vs 31.0 µm², Δ −0.4 [−1.8, +1.1]) and above (a) in nuclear area (Δ +2.4 [+0.7, +4.2]); the small-nucleus tendency appears only in the CNV-quiet newly caught samples.
6. No: PanNuke's inflammatory class pools lymphocytes, plasma cells, neutrophils and macrophages, so plasma-cell density was not measured.

### Deviations from the pre-specification

- Tile positions: the pre-specification read tiles at (x, y) × downsample, treating `coords_level` as top-left corners; they are tile centres. The first run therefore measured tiles offset by half a tile. Primary results come from a corrected run of (a) and (c) (cq6–cq8, commit 8465796); the offset run is kept as a record (`stats_offset.json`, `segmentation_qc_offset.json`) and is the only source for (b). Offset and corrected (a) vs (c) results agree (nuclear area Δ −2.8 vs −2.9 µm², Holm p 0.10 vs 0.078; all other features null in both).
- (b) not re-measured on corrected tiles: doing so (about 5 GPU-hours) would exceed the 15 GPU-hour cap.
- Coordinate check applied to tissue tiles only (grey SD ≥ 10 on the saved tile), changed in commit de6f70b before any feature was computed. Every tile with r < 0.95 was blank glass (grey SD about 2), where the correlation is noise. Under the pre-specified all-tile rule, 25 of 146 offset slides and 3 of 52 corrected slides would have been excluded; on tissue tiles the minimum r was 0.967 (offset) and 0.964 (corrected), and no slide was excluded.
- Operational, no effect on outputs (each step writes per-slide outputs and skips finished slides): in the first run, 4 extraction tasks hit the 1-hour limit and were finished as cq3b, and 13 slides orphaned by an h200 preemption and requeue were re-run on cuda as cq4d.
- Figure: the overlay is a quarter of a tile region from a smoke-test slide outside all groups, enlarged for legibility; (b) is not plotted because it exists only on offset tiles.

**Figure.** `be_paper_figs/v3/16_F_cnvquiet_morphology.{pdf,png}` (corrected tiles, (a) and (c)).
**Caveats.** (1) (a) has 8 patients, so power is low; the nulls do not exclude moderate differences, and the nuclear-area result is unadjusted-only. (2) Grade was matched at class level (NDBE vs ID/LGD) as pre-specified; within the dysplastic class (a) is mostly LGD (5 LGD, 1 ID) and its matches mostly ID (14 ID, 4 LGD). (3) F4 and F5 are proxies: there is no Barrett's layer segmenter, PanNuke's inflammatory class is not lymphocyte-specific, and in the smoke overlays some lymphocyte-like stromal cells were called connective. (4) Only the 256 stored tiles per slide (about 10 mm²) were measured, i.e. what the image model saw, not all tissue; no stain normalisation (scanner matched exactly). (5) PanNuke's neoplastic/non-neoplastic split is uninformative here (52–53% of epithelial nuclei called neoplastic in every group, both runs). (6) Matched case–control cohort; results are descriptive and do not feed any predictor.

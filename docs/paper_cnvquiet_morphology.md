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

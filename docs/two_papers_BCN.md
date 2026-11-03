# Two papers, agent BCN: preparing BEACON (Ercan et al.) as a competitor benchmark on the Killcoyne discovery slides

## Plan

Rehan approved: install BEACON's code, work out the input it expects against our Hamamatsu slides, and prepare tiles. He has not approved downloading the Zenodo weights (models.zip 7.7 GB, annotations.zip 0.43 GB, CC BY-NC-ND 4.0), and the REMEDIS base model needs PhysioNet credentials (Rehan is applying). Neither was downloaded, and no BEACON model was run.

1. Clone the repository on the cluster, record the commit, and build an env for the DACOR path.
2. Read their code, the preprint and its supplementary tables, and write down the exact input each model needs.
3. Map that input onto our slides: the 683 slides of the 676 discovery-cohort samples with an H&E (set C, the L-IMG bags).
4. Write a CPU tiling script, smoke it on 3 slides, check montages, estimate storage, then run all slides if the total is 1.5 TB or less.
5. Write down what is ready, what is blocked, and the commands for when the weights arrive.

Where things are:
- Code: `/mnt/scratche/slow/fmlab/zuberi01/phd/beacon/code`, commit `b2007a83f024c3ca5d4a82721ad8c32e328113b0` (21 Aug 2026, "Add revision analyses and experiments"). GPL-3.0; the vendored CellViT-plus-plus keeps its own Apache-2.0 + Commons Clause licence.
- Env: `phd/beacon/env`, built by `tp_bcn_build_env.sh`.
- Scripts: `scripts/paper_plan/tp_bcn_tiles.py` (CPU, the only BCN script that reads slide pixels), `tp_bcn_embed.py` (GPU embedding and DACOR scoring; run only with dummy weights), `tp_bcn_dummy_check.sh`, `tp_bcn_build_env.sh`.
- Row-level data, on the cluster only: `killcoyne_mm/two_papers_BCN/` (chmod 700). This holds `slide_key.csv` (600), `tiles/{A,B}/s<k>.npy`, `coords/s<k>.npz`, `meta/s<k>.json`, plus the smoke archives `smoke_theirs/` and `smoke_mask/`.
- Aggregates: `results/paper_final/two_papers_BCN/` (`storage_estimate.json`, `tiling_summary.json`).
- Figures, local only: `paper/two_papers/figs_BCN/`.
- Slurm prefixes: `tpbcn*`.

## 1. What BEACON expects

How each item is known: **[code]** = read in their repository at the commit above (file named); **[pre]** = medRxiv 10.1101/2025.11.11.25339952 v1 (13 Nov 2025) and its supplementary tables; **[zen]** = the Zenodo record 17583572 metadata page (no file downloaded); **[inf]** = my inference.

### DACOR (DNA content abnormality, CLAM MIL)

| Item | What they use | Source |
|---|---|---|
| Training slides | 20× scans: MDACC Hamamatsu NanoZoomer **0.4548 µm/px** (discovery, 422 slides), NU Aperio AT2 0.5013 µm/px (test, 355 slides). The slides were ROI crops (`roi_pyramid`, `.tif`; `sample_list_roi.csv`), one flow-cytometry biopsy each | [pre] Methods; [code] `heatmaps/configs/*.yaml`, `3.integration/ecology/1.2.cell_attn.Rmd` (`nonorm224_roi1`) |
| Label | flow-cytometry DNA content: aneuploid / tetraploid or G2/M > 6% = "abnormal" | [pre] |
| Tissue detection | `WholeSlideImage.segmentTissue`, preset `barrett.csv` / `barrett_gaus.csv`, at the level nearest downsample 64. In the released code only the `gaus_otsu` branch runs (the other branches leave `mask_foreground` undefined and crash): grey, then 7×7 Gaussian blur, then inverted Otsu, minus a dilated ink mask (grey < 50), then closing 2 px. Contours are kept if their area minus holes is more than 1 × (512 px)² at level 0; at most 2 holes are kept, each larger than 1 × (512 px)². `barrett.csv` has no `gaus_otsu` column and would raise a KeyError in `create_patches_fp.py`; the two presets differ only in `sthresh`, which Otsu ignores | [code] `wsi_core/WholeSlideImage.py`, `create_patches_fp.py`, `presets/` |
| Tiles | **224 × 224 px at level 0 (20×, so 101.9 µm), step 224 (no overlap)**, `four_pt` contour check (any of 4 points at ±56 px from the centre inside tissue, centre not in a hole), padding on. CLAM drops any contour with only 1 tile. `white_thresh`/`black_thresh` are in the preset but unused by the fp patcher | [code] `create_patches_fp.py`, `process_contour`; 224 from `collect_probabilities_df(patch_size=(224,224))` and the run name `nonorm224`, and 112-px heatmap cells in the ecology code (= 224 at 50% overlap). [inf] for the exact `--patch_size 224 --step_size 224` call, which is not in the repo |
| Stain normalisation | **none**. The tile goes to the encoder as float **0–255** (`--normalisation none`; the default `custom_transforms` path is a no-op) | [code] `datasets/dataset_h5.py`, `extract_features_fp.py`; "nonorm" in the run name |
| Encoder | REMEDIS **`path-152x2-remedis-m`** (preprint), SimCLR fine-tuned on their MDA tiles, loaded from `FOUNDATION_MODEL_ROOT/finetuned/448_ds2/<arch>/saved_backbone_model`. Backbone = hub layer → AvgPool 7×7 → Flatten → Dense 1024 (no bias), **1024-d features**, input 224×224×3. The fine-tune notebook named in the README as "the exact run" uses `arch = 'path-50x1-remedis-s'` and **random 448 crops of 1024 regions, resized to 224** (so the encoder was trained at 2× the pixel size, about 0.91 µm/px). The preprint says "two non-overlapping 224×224 tiles" | [pre]; [code] `models/model_foundation.py`, `notebooks/simclr/finetune_250207_albm_448_ds2.ipynb`, `finetuning/config.py` |
| **Fine-tuned encoder availability** | **not released**: "intentionally not included" in Zenodo; only the base model is pointed to (PhysioNet) | [zen]; README "Data availability" |
| Aggregation | CLAM_MB, size "big" (1024→512, gated attention 512→384, 2 attention branches, 2 bag classifiers), dropout 0.25; one bag = one slide (all its tiles); checkpoint `s_16_checkpoint.pt` (split 16) | [pre] Supp. Tables 2–3; [code] `models/model_clam.py`, `utils/eval_utils.py`, README |
| Output | per slide: `Y_prob[0,1]` = probability of DNA content abnormality, `Y_hat` = argmax; per tile: attention (raw and percentile). Heatmaps: sliding window at 50% overlap, averaged into **112 × 112 px** cells (level 0, 20×). Patient = abnormal if any biopsy is predicted abnormal | [code] `inference_aggregate_heatmap_250316.py`; [pre] |
| Reported performance | AUC 0.988 (validation), 0.825 (NU test) for flow-cytometry abnormality | [pre] |

Two readings fit their materials, and the code does not settle which one produced DACOR's bags:
- **A**, 224 px at 0.4548 µm/px (code defaults, `nonorm224`, 112-px heatmap cells).
- **B**, 448 px resized to 224, 0.91 µm/px (the encoder's fine-tune geometry, `448_ds2`).

I prepared both. A is the primary reading because three separate code paths point to it; B covers 4× the area per tile and costs a quarter of the storage. To choose between them without looking at outcome, use the outcome-free copy-number check in section 5.

### Immune ecology and the LASSO risk model

| Model | Input | Source |
|---|---|---|
| CellViT-plus-plus nucleus segmenter + 5-class cell classifier (lymphocyte, plasma cell, other immune, epithelial, stromal) | their WSI pipeline (`inference_disk.py`): **1024 × 1024 px patches, 64 px overlap, at 0.25 µm/px** (for slides between 0.20 and 0.30 µm/px it uses the native resolution, so ours run at 0.2204 / 0.2209 µm/px, level 0). The model was trained on 256 × 256 tiles with stain normalisation; the classifier normalises with mean/std 0.5. Backbone: Virchow per the preprint; `train_config.yaml` names CellViT-256 | [code] `cellvit/inference/{inference_disk,wsi_meta,cli}.py`, `train_config.yaml`; [pre] Supp. Tables 5, 9 |
| SegFormer MiT-B0, 4 classes (background, columnar, stroma, squamous) | **1024 × 1024 px tiles at 0.5 µm/px** exported from QuPath as PNG (`1024px_05mpp`), resized to **512 × 512**, /255, no other normalisation; edge tiles padded white | [code] `2.2.segmentation/code/{config,wsi_inference}.py` |
| QuPath integration (manual GUI step) | cells from CellViT, tissue masks from SegFormer and DACOR attention merged per cell; per-slide TSVs exported; QuPath nuclear features (intensity 5, Haralick 13, shape 6) | README step 2.3; [pre] |
| Ecology metrics (R) | density, Ripley's L, Getis-Ord Gi*, kNN, Moran's I, Morisita-Horn, G-function, each for DNA-abnormal regions, normal regions and whole tissue, across cell-type pairs | `3.integration/ecology/*.Rmd`; [pre] Supp. Table 11 |
| LASSO risk model | **1,538 standardised features (928 ecology + 610 nuclear morphology)**, 27 non-zero coefficients, λ1se = 0.0464, applied **only to DACOR-positive slides**; patient score = max slide score; threshold 0.6103 | [code] `3.integration/risk_model/README.md`, `00_config.R` |

### Inputs we cannot provide or cannot reproduce exactly

- **The fine-tuned REMEDIS backbone.** DACOR's checkpoint was trained on its features, and the fine-tune ends in a randomly initialised Dense(1024) projection. The base REMEDIS model plus their recipe would give a different 1024-d basis, so the released checkpoint would be meaningless on it. Their fine-tuning tiles (MDA ROI patches) are not released either. **Without this backbone, the published DACOR cannot be run, even with the Zenodo weights and PhysioNet access.** [inf, from the code path and the Zenodo note]
- Flow cytometry is only DACOR's training label; inference does not need it. We have no flow data. Our nearest equivalent is sWGS copy number (aneuploidy burden), useful as an outcome-free check.
- The LASSO model needs, on top of DACOR (attention for abnormal regions, positive-slide gating), CellViT + SegFormer outputs, the **manual QuPath merge and nuclear-feature export**, the ecology R pipeline, and **their standardisation** of the 1,538 features. The standardisation parameters are not stated as released; standardising on our cohort is a deviation.
- Slide unit: their bags are ROI crops of one biopsy. Ours are whole slides, which often carry several levels or sections of the same biopsies (smoke slides 1 and 2 hold 18 and 16 tissue pieces). DACOR is applied per slide; a sample with 2 slides takes the max (their "any positive" rule).

## 2. Our slides and the mapping

- Slide set: the L-IMG bags (`tp_art_qc.bag_slides`: set C samples × `uni2_npz_map.csv`, slides sorted by npz). That gives **683 slides of 676 samples**, matching ART's count (683 slides, 676 samples). All 683 slide files and all 683 Killcoyne tissue masks exist.
- Scanner (openslide properties, ART `qc_slides.csv`): Hamamatsu NDPI, two products: C13239-01 (509 slides, **0.22089 µm/px**) and C13210 (174 slides, **0.22040 µm/px**). This matches `two_papers_ERL.md` (0.2204 at level 0). Pyramid downsamples are 1, 2, 4, … (level 1 = 0.441 µm/px, level 2 = 0.882 µm/px; asserted per slide).
- Scale factor r = 0.4548 / mpp0 = 2.059 (C13239-01) or 2.064 (C13210). Every pixel size in their code is multiplied by r so the physical size stays the same:

| | theirs (20×, 0.4548 µm/px) | ours (40×) |
|---|---|---|
| Segmentation level | downsample 64 (29 µm/px) | level nearest downsample 64 r = level 7 (downsample 128, 28 µm/px) |
| Area unit for contour / hole filters | (512 px)² at level 0 | (512 r px)² at level 0 (0.054 mm²) |
| **Tile A** | 224 px at level 0, step 224 | **461/462 px at level 0, step the same; read 230/231 px at level 1, bicubic to 224 → 0.4536 / 0.4546 µm/px** |
| Tile B | 448 px at level 0, resized to 224 | 922/924 px at level 0; read 230/231 px at level 2, bicubic to 224 → 0.9072 / 0.9092 µm/px |
| SegFormer | 1024 px at 0.5 µm/px | 2318/2323 px at level 0 (coordinates only) |
| CellViT | 1024 px, 64 overlap, at about 0.25 µm/px | 1024 px at level 0 (0.22 µm/px), step 960 (coordinates only) |

- **Tissue detection: deviation.** Their detector, scaled as above and run on our whole NDPI slides, failed on 2 of 3 smoke slides (`figs_BCN/tissue_smoke_their_detector.png`, `montage_smoke_their_detector.png`). On slide 1 it took both coverslip edges as tissue. On slide 2 it took only the pen-marker rings around the sections and none of the faint tissue: the tiles are grey and black glass. It was built for tight ROI crops. The tiling therefore uses **the Killcoyne tissue masks that L-IMG used**, with their contour-area and hole filters in the same physical units, their 4-point rule and their grid (`TISSUE=mask`, the default; `TISSUE=theirs` reproduces their detector).
- **Glass tiles.** The masks are looser than a tight Otsu contour, so about 1 in 4 grid tiles is mostly glass. CLAM's `isWhitePatch` rule (mean saturation < 5) removes none of them, because glass on our scans has saturation 9–14. All tiles are stored. Per-tile statistics are also stored (mean saturation, mean RGB, tissue share = share of pixels with saturation > 0.15 and not white, the `tp_art_qc` definition). The tiles DACOR scores are those with **tissue share ≥ 0.15**, a threshold set by eye on `figs_BCN/smoke_tissue_bins.png` (< 0.15 is glass with slivers; 0.15–0.25 is real tissue edges). No outcome or score was looked at. Bags with all tiles, or with ≥ 0.25, are one environment variable away (`KEEP_TIS`).

## 3. Smoke (3 slides: k = 0, 300, 600)

Measured from `meta/s{000,300,600}.json` and the smoke stats job.

| | slide 1 | slide 2 | slide 3 |
|---|---|---|---|
| scanner | C13239-01 | C13239-01 | C13210 |
| tissue (mask contours) | 105.1 mm² | 91.5 mm² | 10.0 mm² |
| A tiles / B tiles | 10,761 / 2,858 | 9,475 / 2,530 | 1,049 / 280 |
| SegFormer / CellViT grid tiles | 520 / 2,651 | 468 / 2,373 | 54 / 262 |
| A + B storage (uint8 .npy) | 2.05 GB | 1.81 GB | 0.20 GB |
| CPU time (4 cores) | 260 s | 187 s | 32 s |

- Of 21,285 A tiles, tissue share was < 0.05 for 4,531, 0.05–0.15 for 953, 0.15–0.25 for 773, 0.25–0.4 for 1,154 and ≥ 0.4 for 13,874. So **15,801 (74%) pass the ≥ 0.15 rule**. None has saturation < 5 or mean RGB < 50.
- Montages (`figs_BCN/montage_smoke.png`: random A and B tiles; `tissue_smoke.png`: A grid over the tissue) show H&E tissue at the expected scale, with the remaining glass tiles caught by the tissue-share rule. The A tiles are 102 µm across with nuclei clearly resolved; the B tiles are 204 µm across.
- The smoke slides sit in the upper tail of tissue area: slides 1 and 2 are above the 75th percentile of 13.8 mm².
- Known-number check: the slide set reproduces ART's 683 slides / 676 samples. No model number can be reproduced until weights exist.

## 4. Storage and the campaign

- Estimate before launching (`storage_estimate.json`, mask area only): 13,589 mm² of tissue mask over 683 slides (median 9.9 mm², max 212 mm²), so about 1.31 M A tiles and **about 197 GB (A) + 49 GB (B) as uint8**. Grid edge effects added 6% (A) and 13% (B) on the smoke slides. This is far under 1.5 TB, so all slides were tiled.
- Campaign `tpbcnt`: 683 per-slide CPU tasks through `scripts/cluster/campaign.sh` (workers only: 15 per partition on epyc, rocm, cuda, h200, the h200 ones with `--qos=h200_preempt`; 4 CPUs, 16 GB). Env `pathology` (openslide + cv2); `phd/beacon/env` is for the GPU step.
- Result: all 683 slides done (11:38–12:26, 3 Nov 2026), 0 failures; see section 6.

## 5. Blockers and the next commands

**Blockers**
1. **Fine-tuned REMEDIS backbone (`finetuned/448_ds2/<arch>/saved_backbone_model`)**: not on Zenodo. It has to come from the authors (Caner Ercan, MD Anderson; corresponding author). Their PhysioNet data-use agreement probably governs redistribution, so Rehan's PhysioNet credential is likely a precondition [inf]. Ask them also: which arch (152x2-m in the preprint, 50x1-s in the notebook), the exact `create_patches_fp.py` call (patch size, level; settles A vs B), and the LASSO feature standardisation.
2. Zenodo `models.zip` (DACOR `s_16_checkpoint.pt`, CellViT segmenter + classifier, SegFormer, LASSO): Rehan's approval to download (7.7 GB, CC BY-NC-ND 4.0: non-commercial, no derivatives distributed).
3. REMEDIS base (PhysioNet, credentialed): Rehan applying. It is needed only to re-fine-tune, and re-fine-tuning cannot reproduce their backbone (blocker 1).
4. LASSO risk model: also needs CellViT on our slides (about 1,700 grid tiles per large slide, 3 MB each raw; not extracted), SegFormer, and a scripted replacement for their manual QuPath merge. This is a separate project; DACOR comes first.

**Env.** `phd/beacon/env` (Python 3.11): torch 2.10.0 cu126, TF 2.20 `[and-cuda]` + tf-keras, tensorflow_hub 0.16.1, their pins for numpy, pandas, h5py, albumentations, Pillow, scipy, scikit-learn, timm, transformers, plus openslide and opencv. Their full `requirements.txt` does not install: `ctypes_snappy==1.03` is not on PyPI and `fastapi==0.128.0` conflicts with `starlette==0.52.1`. `tensorflow_addons` (EOL) is dropped; it is used only by the fine-tune. CellViT will need its own env from `2.1.cell/CellViT-plus-plus/environment.yaml`.

**Once the backbone and the checkpoint are in place** (`FOUNDATION_MODEL_ROOT=/mnt/scratche/slow/fmlab/zuberi01/phd/beacon/weights/remedis`, `DACOR_CKPT=/mnt/scratche/slow/fmlab/zuberi01/phd/beacon/weights/zenodo/models/dacor_mil/s_16_checkpoint.pt`):

```bash
# on the cluster, repo root /mnt/scratche/slow/fmlab/zuberi01/phd/thesis
E=/mnt/scratche/slow/fmlab/zuberi01/phd/beacon/env; W=/mnt/scratche/slow/fmlab/zuberi01/phd/beacon/weights
X="FOUNDATION_MODEL_ROOT=$W/remedis DACOR_CKPT=$W/zenodo/models/dacor_mil/s_16_checkpoint.pt ARCH=path-152x2-remedis-m"
# 0. smoke: 3 slides on one GPU; check feature shape (n x 1024), finite values, and that A and B both run
printf "e000\t$E\t$X TASK=embed_A_0 python scripts/paper_plan/tp_bcn_embed.py\n" > /tmp/tpbcng0.tsv   # + embed_A_300, embed_A_600
bash scripts/cluster/campaign.sh tpbcng0 /tmp/tpbcng0.tsv --partitions "cuda" --gres gpu:1 --workers 1 --cpus 8 --mem 48G --time 1:00:00
# 1. embedding: 683 tasks per variant (A first), GPU pull workers on cuda (L40S; TF 2.20 does not run on our H200 driver); each task reads only tiles/<V>/s<k>.npy
for k in $(seq 0 682); do printf "eA%03d\t$E\t$X TASK=embed_A_%d python scripts/paper_plan/tp_bcn_embed.py\n" $k $k; done > /tmp/tpbcnga.tsv
bash scripts/cluster/campaign.sh tpbcnga /tmp/tpbcnga.tsv --partitions "cuda" --gres gpu:1 --workers 12 --per-task no --cpus 8 --mem 48G --worker-time 6:00:00
# 2. DACOR scoring (one small GPU or CPU job; 683 bags of <= ~10k x 1024)
printf "sA\t$E\t$X TASK=score_A python scripts/paper_plan/tp_bcn_embed.py\n" > /tmp/tpbcnsa.tsv
bash scripts/cluster/campaign.sh tpbcnsa /tmp/tpbcnsa.tsv --partitions "epyc cuda h200" --workers 0 --cpus 4 --mem 32G --time 1:00:00
```

Env checks (measured; logs in `phd/beacon/`):
- torch 2.10.0+cu126 runs on L40S (cuda, driver 545.23) and H200 (h200, driver 535.274).
- **TF 2.20 runs on L40S only.** On H200 its elementwise kernels fail with `CUDA_ERROR_UNSUPPORTED_PTX_VERSION`: driver 535 (CUDA 12.2) is too old for the PTX in the TF 2.20 wheels, which carry no sm_90 machine code [inf; a plain `tf.matmul` did pass on H200, probably because it goes through cuBLAS]. The REMEDIS embedding therefore goes on **cuda (6 nodes × 4 L40S) only**. If h200 capacity is needed, a separate env with a TF built for CUDA ≤ 12.2 (TF 2.15) would have to be tested there first. DACOR scoring is torch and runs anywhere.
- Plumbing check with **dummy weights** (`tp_bcn_dummy_check.sh`: a random TF encoder with the same interface, 224×224×3 float 0–255 → 1024, and a random CLAM_MB state dict), on one L40S for slide k = 600. Embedding A gave 965 × 1024 (965 of 1,049 tiles pass the keep rule) and B gave 255 × 1024. Scoring loaded the state dict with `strict=True` and wrote `slide_scores.csv`. This proves the reading, keep mask, output layout and CLAM path only, not any BEACON number. Real REMEDIS has not been loaded.

**Evaluation (to script once `dacor/A/slide_scores.csv` exists; nothing outcome-related has been done yet)**
1. Outcome-free validity, which also decides A vs B. DACOR p(abnormal) against sWGS aneuploidy burden on the same samples: Spearman with genome fraction altered, and AUROC for "CN-abnormal". The CN-abnormal definition must be fixed before scores are read, e.g. the CNC/ACE ploidy-deviation call. Pick the variant with the higher Spearman; outcome is not looked at.
2. Progression benchmark on the 571 pre-event samples (288 endoscopies, 75 patients, 32 progressors). Sample score = max over its slides. DACOR is not trained on our data, so its score is already held-out for every patient. Report its AUROC with the 2,000-draw patient bootstrap (`tp_p1b_main.py` `hblock`), paired against the stored out-of-fold L-IMG (0.847, and clean-tile 0.811 per ART) and L-CNV (0.801) in the same 10 × 10 folds. Also report their patient rule (any sample with `Y_hat` = 1).
3. Does DACOR add to copy number? Logistic stack of DACOR + L-CNV refit inside the stored 10 × 10 patient-grouped folds (training patients only, as `tp_art_refit.R`), scored on held-out patients; apparent numbers labelled optimistic.

## 6. Campaign result (measured, `tiling_summary.json`)

| | value |
|---|---|
| Slides tiled | 683 of 683 (509 C13239-01 at 0.22089 µm/px, 174 C13210 at 0.22040 µm/px); segmentation level 7 for all |
| Tissue (mask contours) | 13,245 mm² in total; median 9.7 mm² per slide (min 0.18, max 203.7) |
| **A tiles** (224 px at 0.4536–0.4546 µm/px) | **1,383,239** (median 1,032 per slide, min 26, max 21,070); **1,097,246 (79%) pass tissue share ≥ 0.15** |
| **B tiles** (224 px at 0.9072–0.9092 µm/px) | **369,990** (median 278, min 7, max 5,609); 298,665 (81%) pass |
| Storage, uint8 `.npy` | **A 208 GB + B 56 GB = 264 GB** |
| Not extracted (coordinates stored) | SegFormer 68,944 tiles (217 GB raw at 1024 px); CellViT 345,867 tiles (1,088 GB raw at 1024 px) |
| Completeness | every array matches its coordinate and statistics counts, shape (n, 224, 224, 3) uint8; no slide with 0 tiles; no temporary files left |
| CPU time | median 99 s per slide (max 1,673 s), 35 CPU-hours in total, 48 min wall-clock on about 56 workers |

What is ready: tiles A and B for every slide, their level-0 coordinates and per-tile statistics, the keep rule, the env (cuda partition), and the embedding and scoring script with its plumbing checked on dummy weights.

What is missing:
1. The fine-tuned REMEDIS backbone, from the authors.
2. Zenodo `models.zip`, which needs Rehan's approval.
3. PhysioNet access, only for re-fine-tuning.
4. The outcome-free choice between A and B.

GPU time once the weights are in (inference, not measured): about 1.1 M kept A tiles through an R152x2 at 224 px plus one model load per slide task. That is likely 5–15 GPU-hours, so 1–2 h on 8–12 L40S.

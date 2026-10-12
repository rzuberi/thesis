# Scanner robustness of the image extractor: a label-free choice between UNI2-h and alternatives

Status: PRE-SPECIFICATION (written 2026-10-12). Only Step 0, which reads code, model cards and sample counts, was done before this commit; no embedding has been computed or compared. Results are appended under the line at the end in a later commit, and this section is not edited afterwards.

**Ground rules** (as in `docs/paper_triage_robustness.md`, pre-specification 32653f1):
- Report only, with a status per item and at most one line of interpretation per question.
- Earlier documents are not edited. Patient lists and row-level data stay on the cluster; only aggregates go in the repository.
- **No progression labels are used to choose the extractor.** The index scripts read only sample, patient, endoscopy and scanner. Labels enter only the conditional downstream run (item 4), which is done once and reported whatever the outcome.
- The frozen model bundles in `models/` are not changed by this analysis.

**Why.** The histology model is scanner-sensitive: L-IMG scores 0.841 within C13239-01 and 0.726 when moved to C13210 patients, and the scanner is identified with AUROC 1.000 from every image representation (`docs/paper_triage_robustness.md` item 5, `docs/paper_latent_attention.md`). If ACE-B is scanned on another scanner, the image arm can fail for a technical reason. This analysis asks, without labels, whether a different extractor puts patient before scanner in its embedding space more than UNI2-h does.

## Step 0: facts established before this commit

- **Extraction code.** The stored UNI2-h embeddings come from `barretts_training/scripts/extract_foundation_from_masks.py` (seed 20260226, 24 chunks). `coords_level` holds tile **centres** at level 2. A tile is read with its top-left corner at centre − 112 px, clamped to the level bounds, via `read_region` at level 2, size 224 × 224, converted to RGB. Level 2 is about 0.88 µm/px. UNI2-h features are the CLS token (1,536-d), computed under fp16 autocast and stored as fp16.
- **Prov-GigaPath embeddings** exist from the same script (`gigapath_tile224_lvl2`, same chunking and seed). On the two slides checked, `coords_level` is identical to UNI2-h's. Item 1 checks this on every slide.
- **H0-mini is not available.** `bioptimus/H0-mini` is gated, and the cached token was refused on 2026-10-12 (HTTP 403, "not in the authorized list"). It is replaced by H-optimus-0, as below.
- **Cached weights** (`hf_cache`): H-optimus-0, Virchow2, Prov-GigaPath and Phikon-v2. H-optimus-1 is incomplete (metadata only). UNI2-h weights are not cached.
- **Dual-scanner patients.** The scanner is recorded per sample (`horizons/slide_desc.csv`; a sample's slides share one scanner):
  - Across all 676 samples, 25 patients have samples on both scanners: 283 samples, 146 on C13210 and 137 on C13239-01.
  - Per patient: 1–15 samples on C13210 and 1–17 on C13239-01; mean 11.3 samples per patient.
  - Status: 10 progressor and 15 non-progressor patients. This is reported, not used.
  - Earlier documents give 23 patients because they count pre-event samples only.
  - 12 of 315 endoscopies have samples on both scanners.
  - Paired samples are different biopsies, often from different endoscopies, not rescans of one slide. Same-patient, other-scanner neighbours therefore differ in biology as well as scanner. This lowers the index for every extractor alike.
- Software: conda env `virchow2` (torch 2.9.1+cu128, timm 1.0.24, openslide) for tiles and embeddings; `/mnt/scratche/slow/fmlab/zuberi01/envs/killcoyne_r` for R.

## 1. Extractors and embeddings

**Shortlist**, justified by the PathoROB robustness index (Kömen 2025, Sup. Tables 8–10). The value given is the mean of the default-processing index over its three datasets (TCGA 2×2, Camelyon, Tolkach ESCA):

| Code | Extractor | Role | PathoROB mean index | Tile feature |
|---|---|---|---|---|
| E0 | UNI2-h | Incumbent; stored embeddings | 0.768 | CLS, 1,536-d |
| E1 | Virchow2 (`paige-ai/Virchow2`) | Eligible candidate. Highest of the 20 models and the only public, cached model near the top (CONCHv1.5 0.859 and Atlas 0.856 are next; neither is cached or public) | 0.870 | Model card: CLS ⊕ mean of patch tokens 5+, 2,560-d |
| E2 | H-optimus-0 (`bioptimus/H-optimus-0`) | Eligible candidate, **replacing H0-mini** (0.822, not accessible). It is H0-mini's teacher and the best-ranked cached model after Virchow2 | 0.820 | CLS, 1,536-d |
| GP | Prov-GigaPath | Reference only, never eligible (ranked below UNI2-h); stored embeddings | 0.640 | CLS, 1,536-d |

- **Same tiles for every extractor.** The new extractors embed exactly the 256 stored tiles of each of the 683 slides: the same slide, level and centres, read with the original code's rule above. Only the extractor changes.
- **Two phases.**
  - CPU jobs read the tiles and save them as uint8 arrays on scratch. These are the only jobs that open slide files.
  - GPU jobs embed the saved tiles: model-card preprocessing, fp16 autocast, features stored as fp16.
  - Virchow2 uses `create_transform(resolve_data_config(...))` with `SwiGLUPacked` / `SiLU`.
  - H-optimus-0 uses ToTensor and its own mean/std, with `init_values 1e-5` and `dynamic_img_size False`.
- **Prov-GigaPath check.** It is used only if its `coords_level` equals UNI2-h's on all 683 slides; otherwise it is dropped and reported.
- **Validation before the full run (smoke).**
  - Run end to end on 2 slides, the first slide of each scanner in map order.
  - Prov-GigaPath is re-embedded from the saved tiles with its original transform: Resize 256 bicubic, CenterCrop 224, ImageNet mean/std, fp16.
  - Per-tile cosine similarity with the stored Prov-GigaPath embeddings must have median ≥ 0.99 and minimum ≥ 0.95. Otherwise the analysis stops and the difference is reported.
- **Sample representation**, as `km_prep.py`:
  - The tile embeddings of a sample's slides are concatenated in map order (sorted by sample, then npz) and averaged in float32.
  - For UNI2-h this must reproduce `killcoyne_mm/img_mean.csv` (max |difference| ≤ 1e-4). Otherwise the analysis stops.

## 2. Robustness index (primary)

**Pool P.** The 283 samples of the 25 dual-scanner patients. These are both the queries and the neighbour candidates.
- Pre- and post-event samples are both included, because no label is involved.
- Restricting the pool keeps the design balanced, as PathoROB requires: every patient in the pool can have neighbours of the same patient on the other scanner, and the scanners are about equally represented (146 / 137).
- The 393 samples of single-scanner patients cannot have such neighbours, and they would make C13239-01 the majority. They enter secondary S2.

**Definition** (Kömen 2025, Methods 4.4, the same group's refinement of de Jong 2025, eq. 1), with patient as the biological class and scanner as the confounding class:
- For each query i in P, take its k nearest neighbours in P \ {i} by cosine distance on the sample representation (stable sort).
- Each neighbour falls into one of four classes:
  - SS: same patient, same scanner;
  - SO: same patient, other scanner;
  - OS: other patient, same scanner;
  - OO: other patient, other scanner.
- R_k = Σ_i |SO_k(i)| / (Σ_i |SO_k(i)| + Σ_i |OS_k(i)|).
- SS and OO neighbours are excluded. A same-patient, same-scanner neighbour is often from the same endoscopy, and it cannot tell patient from scanner.
- **Primary k = 10**, about the mean number of samples per dual-scanner patient (11.3). It is fixed now.
- **Chance level:** R_chance = Σ_i n_SO(i) / (Σ_i n_SO(i) + Σ_i n_OS(i)), where n_SO(i) and n_OS(i) are the numbers of SO and OS candidates for query i in the pool. It is the same for every extractor.

**Uncertainty.** 2,000 patient-bootstrap draws (`RandomState(0)`):
- Resample the 25 patients with replacement. A patient drawn w times contributes its queries w times.
- Neighbour lists are computed once on the full pool and kept fixed (Kömen 2025, Sup. Note B.5).
- The same draws are used for every extractor. ΔR = R(E) − R(UNI2-h) gets a paired percentile 95% CI.

## 3. Decision rule (fixed before any embedding is compared)

- Eligible: Virchow2 (E1) and H-optimus-0 (E2).
- An eligible extractor E is **clearly more robust** than UNI2-h if **both** hold:
  1. the lower bound of the paired 95% patient-bootstrap CI of ΔR_10 = R_10(E) − R_10(UNI2-h) is > 0; and
  2. R_10(E) ≥ 1.25 × R_10(UNI2-h).
- With two candidates, each two-sided 95% CI is a one-sided 2.5% test, so the family-wise one-sided error is at most 5%.
- **Outcome:**
  - **No extractor qualifies:** keep UNI2-h, report the index, and do not run item 4. The label-free band-share recalibration (match the internal triage band shares) stays the ACE-B fallback for scanner shift.
  - **One qualifies:** it is the switch candidate.
  - **Both qualify:** the one with the larger R_10.
- Only the primary index enters the rule. The secondary analyses are reported and not used. Prov-GigaPath is never eligible.
- A switch is a recommendation for the image arm in ACE-B, subject to Rehan's decision. It is not applied to the frozen bundles here.

## Secondary analyses (report only; every extractor including Prov-GigaPath)

- **S1. Curve:** R_k for k = 1, …, 50 on P.
- **S2. All-sample pool:** queries are the 283 samples of P; neighbour candidates are all 676 samples; k = 10.
- **S3. Z-scored representation:** each feature is z-scored over all 676 samples (label-free; close to what L-IMG sees), then the primary is recomputed (P, cosine, k = 10).
- **S4. Tile level:**
  - Tiles: the first 32 stored tiles of every slide of the 283 samples. Stored tiles are already a random sample, so this subset is deterministic.
  - Neighbours: all tiles of P, excluding tiles of the query's own sample.
  - k = 50, de Jong's k. Same patient bootstrap.
- **S5. de Jong 2025, eq. (1) form:** R_dJ,10 = Σ same-patient neighbours / Σ same-scanner neighbours, with SS counted in both; P, k = 10.
- **S6. Other-endoscopy neighbours only:** as the primary, but neighbours from the query's own endoscopy (patient × `Endoscopy`) are removed before the k nearest are taken.
- **S7. Scanner probe** on all 676 samples:
  - StandardScaler, then L2 logistic regression (C = 1, lbfgs, max_iter 5,000).
  - 5-fold `StratifiedGroupKFold`: grouped by patient, stratified by scanner, shuffle, seed 0.
  - Pooled out-of-fold AUROC.
- **Agreement summary:** for each secondary, whether the ordering of E1 and E2 relative to UNI2-h matches the primary.

## 4. Downstream run (only if item 3 says switch; one run, reported whatever the outcome)

**D0. Reproduction check.**
- The R code for D1, run with the UNI2-h matrix (`img_mean.csv`) for repeat 1, must reproduce the stored `cv/preds/cfg_02_rep_01.csv` predictions (max |difference| ≤ 1e-5).
- If it does not, D1 and D2 stop and the failure is reported.

**D1. L-IMG and L-LATE with the new extractor.**
- L-IMG is refitted with the new sample representation under the stored stratified patient-grouped 10-fold × 10-repeat CV (`kv_cv.R`, d69de24).
- Everything else is unchanged:
  - the same folds (`set.seed(repeat)`; progressor then non-progressor patients shuffled; cyclic);
  - all 676 samples in training;
  - z-scoring on the training rows;
  - glmnet α 0.9, `standardize = FALSE`;
  - λ by the class-error minimum of the 10 × 5 inner CV (`kv_common.R`).
- L-LATE is the per-repeat mean of the new L-IMG and the stored L-CNV (their matrix; package features as sensitivity).
- **Reported:**
  - fold-stratified AUROC (mean over 10 repeats) on all pre-event samples (571) and on NDBE pre-event samples (438), next to the stored UNI2-h values;
  - paired Δ (new − UNI2-h) for L-IMG and L-LATE, with patient-bootstrap 95% CIs: 2,000 draws, `RandomState(0)`, draws without both classes redrawn, resampled patients keep their folds.

**D2. Scanner transfer with the new extractor**, as `docs/paper_triage_robustness.md` item 5 (`tb_scanner.R` logic, image matrix swapped, no harmonisation):
- design (b) C13239-01 → C13210: test on all C13210 pre-event samples; train on the C13239-01 pre-event samples of patients with no C13210 sample;
- within-C13239-01 CV, 10 repeats.
- **Reported:** AUROC with patient-bootstrap CI, and test-scanner band shares (low / middle / high), next to 0.726 and 0.841.

No other configuration is run and nothing is tuned.

## Output

- **Scripts** (`scripts/paper_plan/`; Slurm via `scripts/cluster/campaign.sh`, prefixes `sr0` smoke, `sr1`, `sr2`, …):
  - `sr_tiles.py`: CPU tile reading and the Prov-GigaPath coordinate check;
  - `sr_embed.py`: GPU embedding;
  - `sr_validate.py`: smoke validation;
  - `sr_index.py`: sample representations, index, bootstrap, secondaries, decision;
  - `sr_cv.R` and `sr_cv_metrics.py`: item 4, only if run;
  - `sr_fig.py`, `sr_render.py`.
- **Aggregates:** `results/paper_final/scanner_robustness/`.
- **Cluster only:** tiles, tile and sample embeddings, neighbour lists and predictions under `feasibility/paper_plan/killcoyne_mm/scanner_robustness/`.
- **Figure:** `be_paper_figs/v3/15_F_scanner_robustness.{pdf,png}`: R_k against k per extractor with the chance level, and the primary R_10 with CIs.
- **GPU budget cap:** 30 GPU-hours (expected under 3). If the plan would exceed it, the run stops and this is reported.

## Answers (one line each, in the results)

1. How robust is UNI2-h to scanner on our slides (R_10 against chance)?
2. Is Virchow2 or H-optimus-0 clearly more robust by the pre-specified rule, and what is the decision?
3. Do the secondary forms (curve, all-sample pool, z-scored, tile level, de Jong form, other-endoscopy) agree with the primary ordering?
4. Does any extractor remove the scanner signal (scanner probe)?
5. If an extractor was switched in: how do L-IMG, L-LATE and cross-scanner transfer change? Otherwise: not run, per the rule.

---

## Results

Pre-specification commit abe96e9; results commit e8309b9. Scripts `scripts/paper_plan/sr_*.py` (Slurm via `scripts/cluster/campaign.sh`, prefixes sr0 smoke tiles, sr1 smoke embeddings, sr2 smoke validation, sr3 tiles, sr4 embeddings, sr5 index, sr6 refits, sr7 refit metrics). GPU use: 0.71 GPU-hours allocated (sr1 0.06, sr4 0.65; L40S; cap 30). CPU: about 7.2 job-hours, 6.6 of them reading tiles. Aggregates `results/paper_final/scanner_robustness/`; row-level outputs (tiles, embeddings, neighbour lists) on the cluster only. Figure `~/Downloads/be_paper_figs/v3/15_F_scanner_robustness.{pdf,png}`.

### Status

| Item | Status |
|---|---|
| 1 Extractors and embeddings | DONE. H0-mini was not accessible and is replaced by H-optimus-0, as pre-specified. Prov-GigaPath is included: coordinates equal on 683 of 683 slides. Smoke validation passed (cosine 1.000). |
| 2 Robustness index (primary) | DONE |
| 3 Decision rule | DONE: switch to H-optimus-0. Both criteria are met, narrowly. |
| Secondary S1–S7 | DONE |
| 4 Downstream run (H-optimus-0) | DONE. D0 reproduction passed (max difference 0). |

### Answers

1. **Barely: UNI2-h's neighbourhoods are organised by scanner far more than by patient.**
   - R_10 is 0.077 [0.034, 0.132], against a chance level of 0.040.
   - Among the 10 nearest neighbours of the 283 samples, 1,538 are other patients on the same scanner and 128 are the same patient on the other scanner.
2. **H-optimus-0 meets the rule, only just; Virchow2 does not. Decision: switch to H-optimus-0, which triggered the one downstream run.**
   - H-optimus-0: R_10 0.097 [0.041, 0.168]; ΔR +0.020 [+0.001, +0.040]; 1.26 × UNI2-h, against a threshold of 1.25.
   - Virchow2: R_10 0.068; ΔR −0.009 [−0.024, +0.004].
   - Prov-GigaPath (reference): R_10 0.028, below chance.
3. **The direction holds; the size is not robust.**
   - H-optimus-0 is above UNI2-h at every k from 1 to 50 and in all five secondary forms.
   - Its CI excludes 0 only with all 676 samples as neighbours (+0.026) and in the de Jong form (+0.037). It includes 0 with z-scored features, at tile level and with other-endoscopy neighbours only.
   - Virchow2 is below UNI2-h at 48 of 50 k values and in 4 of 5 secondary forms.
4. **No.** The scanner probe AUROC is 1.000 for UNI2-h, Virchow2 and H-optimus-0, and 0.9995 for Prov-GigaPath.
5. **No gain from switching: H-optimus-0 is worse for histology alone and transfers worse between scanners.**
   - L-IMG: 0.805 vs 0.847 (Δ −0.042 [−0.082, −0.010]) on all pre-event samples; NDBE pre-event samples −0.043 [−0.101, +0.002].
   - L-LATE (their matrix): 0.870 vs 0.889 (Δ −0.019 [−0.040, +0.001]); package features −0.013 [−0.029, +0.001].
   - Cross-scanner (C13239-01 → C13210): 0.676 [0.516, 0.827] vs 0.726. Within C13239-01: 0.779 vs 0.841.
   - The score shift on C13210 changes direction rather than going away: 0% / 91% / 9% low / middle / high, against 50% / 30% / 21% with UNI2-h.
   - The small neighbourhood-robustness gain did not carry over to accuracy or transfer. Keeping UNI2-h is the decision to confirm with Rehan.

### Checks

- Smoke validation: Prov-GigaPath re-embedded from the saved tiles of 2 slides vs the stored embeddings, per-tile cosine median 1.00000, minimum 1.00000 (required ≥ 0.99 / ≥ 0.95): passed.
- Prov-GigaPath `coords_level` equal to UNI2-h's on 683 of 683 slides: included as reference.
- UNI2-h sample representation vs `img_mean.csv`: max |difference| 5.85e-08 (≤ 1e-4 required).
- Pool: 283 samples from 25 patients (C13210 146, C13239-01 137); 113 endoscopies, 12 with samples on both scanners; 9,152 tiles for S4.
- Feature dimensions: UNI2-h 1536, Virchow2 2560, H-optimus-0 1536, Prov-GigaPath 1536.

### 2–3. Primary robustness index (pool of dual-scanner patients, cosine, k = 10) and decision

| Extractor | R_10 [95% CI] | Chance | SO / OS / SS neighbours | ΔR vs UNI2-h [95% CI] | Ratio to UNI2-h | CI above 0 | Ratio ≥ 1.25 | Qualifies |
|---|---|---|---|---|---|---|---|---|
| UNI2-h | 0.077 [0.034, 0.132] | 0.040 | 128 / 1538 / 641 | — | — | — | — | — (incumbent) |
| Virchow2 | 0.068 [0.032, 0.113] | 0.040 | 116 / 1596 / 556 | -0.009 [-0.024, +0.004] | 0.88 | no | no | no |
| H-optimus-0 | 0.097 [0.041, 0.168] | 0.040 | 152 / 1413 / 653 | +0.020 [+0.001, +0.040] | 1.26 | yes | yes | yes |
| Prov-GigaPath | 0.028 [0.010, 0.048] | 0.040 | 51 / 1779 / 645 | -0.049 [-0.088, -0.019] | 0.36 | no | no | not eligible (reference) |

**Decision: switch to H-optimus-0.**

### Secondary analyses (report only)

**S1. R_k at selected k** (pool of dual-scanner patients).

| Extractor | k = 1 | k = 5 | k = 10 | k = 20 | k = 50 |
|---|---|---|---|---|---|
| UNI2-h | 0.115 [0.046, 0.189] | 0.069 [0.030, 0.117] | 0.077 [0.034, 0.132] | 0.073 [0.032, 0.127] | 0.064 [0.032, 0.107] |
| Virchow2 | 0.080 [0.025, 0.151] | 0.064 [0.030, 0.103] | 0.068 [0.032, 0.113] | 0.066 [0.028, 0.118] | 0.054 [0.024, 0.095] |
| H-optimus-0 | 0.164 [0.054, 0.285] | 0.120 [0.054, 0.195] | 0.097 [0.041, 0.168] | 0.085 [0.034, 0.153] | 0.068 [0.031, 0.117] |
| Prov-GigaPath | 0.016 [0.000, 0.039] | 0.025 [0.011, 0.041] | 0.028 [0.010, 0.048] | 0.030 [0.010, 0.058] | 0.035 [0.011, 0.070] |

| Analysis | UNI2-h | Virchow2 | H-optimus-0 | Prov-GigaPath | Chance |
|---|---|---|---|---|---|
| S2 all 676 samples as neighbours, k = 10 | 0.043 [0.015, 0.077] | 0.037 [0.017, 0.059] | 0.069 [0.028, 0.117] | 0.017 [0.004, 0.032] | 0.017 |
| S3 z-scored features, k = 10 | 0.061 [0.029, 0.098] | 0.070 [0.033, 0.111] | 0.078 [0.033, 0.132] | 0.029 [0.016, 0.043] | 0.040 |
| S4 tile level, k = 50 | 0.060 [0.036, 0.091] | 0.056 [0.032, 0.087] | 0.067 [0.036, 0.111] | 0.041 [0.019, 0.072] | 0.041 |
| S5 de Jong form (same patient / same scanner), k = 10 | 0.353 [0.230, 0.485] | 0.312 [0.211, 0.421] | 0.390 [0.263, 0.529] | 0.287 [0.194, 0.384] | 0.096 |
| S6 other-endoscopy neighbours only, k = 10 | 0.077 [0.029, 0.136] | 0.070 [0.025, 0.127] | 0.096 [0.033, 0.176] | 0.029 [0.006, 0.058] | 0.038 |

| Analysis | Δ Virchow2 − UNI2-h [95% CI] | Δ H-optimus-0 − UNI2-h [95% CI] | Same direction as primary |
|---|---|---|---|
| S2 all 676 samples as neighbours, k = 10 | -0.006 [-0.022, +0.008] | +0.025 [+0.009, +0.044] | Virchow2: yes, H-optimus-0: yes |
| S3 z-scored features, k = 10 | +0.008 [-0.006, +0.021] | +0.017 [-0.002, +0.037] | Virchow2: no, H-optimus-0: yes |
| S4 tile level, k = 50 | -0.004 [-0.010, +0.000] | +0.007 [-0.003, +0.021] | Virchow2: yes, H-optimus-0: yes |
| S5 de Jong form (same patient / same scanner), k = 10 | -0.041 [-0.072, -0.010] | +0.037 [+0.011, +0.062] | Virchow2: yes, H-optimus-0: yes |
| S6 other-endoscopy neighbours only, k = 10 | -0.007 [-0.024, +0.006] | +0.019 [-0.008, +0.044] | Virchow2: yes, H-optimus-0: yes |

**S7. Scanner probe** (all 676 samples, 5-fold patient-grouped, pooled out-of-fold AUROC): UNI2-h 1.0000; Virchow2 1.0000; H-optimus-0 1.0000; Prov-GigaPath 0.9995.

### 4. Downstream run

D0: `sr_cv.R` with the UNI2-h matrix reproduces stored `cfg_02_rep_01` predictions: max |difference| 0.0e+00, folds equal: yes (passed).

**D1. Fold-stratified per-sample AUROC, stratified patient-grouped 10-fold × 10 CV (stored folds), H-optimus-0 vs UNI2-h.**

| Population | Arm | UNI2-h [95% CI] | H-optimus-0 [95% CI] | Δ [95% CI] | p (two-sided) |
|---|---|---|---|---|---|
| all pre-event (571 samples, 75 patients) | L-IMG | 0.847 [0.798, 0.894] | 0.805 [0.744, 0.859] | -0.042 [-0.082, -0.010] | 0.009 |
| all pre-event (571 samples, 75 patients) | L-LATE their | 0.889 [0.830, 0.934] | 0.870 [0.807, 0.922] | -0.019 [-0.040, +0.001] | 0.06 |
| all pre-event (571 samples, 75 patients) | L-LATE package | 0.903 [0.856, 0.944] | 0.890 [0.837, 0.934] | -0.013 [-0.029, +0.001] | 0.076 |
| NDBE pre-event (438 samples, 71 patients) | L-IMG | 0.827 [0.768, 0.883] | 0.784 [0.710, 0.851] | -0.043 [-0.101, +0.002] | 0.064 |
| NDBE pre-event (438 samples, 71 patients) | L-LATE their | 0.867 [0.794, 0.931] | 0.850 [0.771, 0.917] | -0.017 [-0.046, +0.006] | 0.154 |
| NDBE pre-event (438 samples, 71 patients) | L-LATE package | 0.879 [0.818, 0.935] | 0.866 [0.798, 0.929] | -0.013 [-0.031, +0.004] | 0.141 |

**D2. Scanner transfer with H-optimus-0** (L-IMG refitted; pre-event samples).

| Design | AUROC [95% CI] | UNI2-h reference | Test bands low / middle / high (training-scanner inner OOF) |
|---|---|---|---|
| Within C13239-01, fold-stratified, 432 samples, 71 patients | 0.779 [0.710, 0.839] | 0.841 | — |
| (b) C13239-01 → C13210, 139 test samples, 27 patients; 48 training patients | 0.676 [0.516, 0.827] | 0.726; bands 50% / 30% / 21% (18% / 61% / 20%) | 0% / 91% / 9% (14% / 67% / 20%) |

### Deviations and caveats

- H0-mini, the README's main candidate, was not used. `bioptimus/H0-mini` is gated and the cached token was refused (HTTP 403) on 2026-10-12. H-optimus-0, its teacher and the next-ranked cached model in PathoROB, replaced it. This was stated in the pre-specification before any embedding was computed.
- Dual-scanner patients: 25 patients and 283 samples across all 676 samples. Earlier documents give 23 because they count pre-event samples only.
- The decision rule was met by a narrow margin: ratio 1.264 against the 1.25 threshold, and a CI lower bound of +0.0009. The pre-specified downstream run followed, and its result points the other way (answer 5). Under the pre-specification a switch is a recommendation subject to Rehan's decision; the frozen bundles in `models/` were not changed.
- Every index is close to chance (chance R_10 0.040), because a pool of 283 samples offers few same-patient, other-scanner candidates per query (about 5). The index ranks extractors on identical data; its absolute values are not comparable with PathoROB's balanced datasets.
- Tiles are about 0.88 µm/px (level 2), while Virchow2 and H-optimus-0 were trained at about 0.5 µm/px. This matches the stored UNI2-h pipeline and applies to every extractor.
- Found in passing, not part of this analysis: `coords_level` in the stored npz files are tile centres. `scripts/paper_plan/pp_montage.py` and `scripts/task_conch_swg.py` read them as top-left corners, so their tiles are offset by half a tile (112 px at level 2).
- The run was split into a smoke batch (sr0–sr2) and main batches (sr3–sr7). The smoke tiles and embeddings are part of the results.

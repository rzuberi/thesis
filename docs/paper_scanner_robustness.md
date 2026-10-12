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

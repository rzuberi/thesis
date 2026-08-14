# Open gates and next steps (dependency-ordered) — updated 2026-08-14 (PM)

## Gate results (feasibility jobs, 2026-08-14 — scripts in `feasibility/`, outputs in `feasibility/runs/`)

1. **OCCAMS H&E+genomics fusion first-pass** — ⚠️ RAN, WEAK. n=140, 2-yr binary
   survival: hist-only AUC 0.567, gen-only 0.518, late fusion 0.583 (ΔAUC vs hist
   −0.005 [−0.031,+0.022]), early fusion WORSE (−0.079, CI excl. 0). Caveats that
   gate a REDESIGN, not abandonment: mean-pooled features (SWG benefit came from
   ABMIL), crude endpoint (no vital-status column in the genomics TSV → censoring
   unmodelled), only 6 scalar genomic features.
2. **TCGA-Reports join (Ch4)** — ✅ PASSED. Report+slide: ESCA 146 (88 OAC),
   ESCA+STAD 507 (417 adeno), pan-cancer 9,517.
3. **TCGA-ESCA download (Ch2)** — ✅ PASSED. 65 OAC diagnostic (-DX) slides,
   83.9 GB, ~4 MB/s single-stream (~6 h; minutes as 65 parallel jobs).
   NOTE: only 65/87 complete-modality OAC cases have DX slides.
4. **ERIN UNI2 extraction (Ch3/Ch4)** — ✅ PASSED on L40S (`erin` env — the
   `pathology` env torch is CPU-only). 6/6 slides, 0 errors, mean 84 s/slide
   (512-tile cap) → ~25 GPU-h capped for 1,045 slides; run as per-slide jobs.
   Production note: precompute low-mag tissue masks (background scanning dominates
   sparse slides: 163 s for 324 tiles vs 20 s for 512).

## Next steps
1. **OCCAMS second pass (redesigned):** find vital status in
   `~/occams_work/occams_master_20260511.csv` (or master OCCAMS export) → proper
   censored endpoint; ABMIL over tile-level h5 features
   (`occams/wsi_data/slides/features/20x_224px/features_uni_v2/`); richer CN
   features (segments/signatures, not 6 scalars).
2. **Launch ERIN full extraction:** 1,045 per-slide race-to-run jobs on
   `cuda,h200`, `CONDA_ENV=erin`, tissue-mask preflight.
3. **Launch TCGA-ESCA acquisition:** 65 per-slide download jobs (epyc) + 65
   per-slide extraction jobs (GPU) keyed off download done-markers.
4. **TCGA TP53/WGD probe** (Ch2 Part A replication) — minutes, after step 3.
5. **ERIN report-label vs expert-grade validation** (Ch4) — CPU, after step 2.

## Standing cautions
- `pathology` conda env torch is CPU-only; GPU tasks need `CONDA_ENV=erin` (torch 2.0.1+cu117, timm 1.0.3, openslide).
- Report SWG fusion benefit as AUC+Brier-backed "likely benefit" (AUPRC CI includes zero).
- Never use ICGC ESAD as external validation (≡ OCCAMS).
- Ch2 endpoints: SWG=progression; OCCAMS+TCGA=survival (matched replication pair).
- barretts_training Phase 8 rerun still blocked on CNV feature dir + UNI2 index (commands in docs/).

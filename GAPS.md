# Open gates and next steps (dependency-ordered) — 2026-08-14

## Gates (decide chapter commitment)
1. **OCCAMS H&E+genomics fusion first-pass** (Ch2 Part B, n=141) — ❌ NOT RUN.
   The single most load-bearing untested item. Inputs exist: UNI2/Virchow2 features
   precomputed; WGS labels in `~/occams_work/`. Clinical-only baselines already in
   `phd/occams_multimodal/` (use as comparison arm).
2. **TCGA-Reports join first-pass** (Ch4) — ❌. Laptop job: download Mendeley
   hyg5xkznpx, join to `manifests/TCGA_multimodal_manifest.csv` on case ID, count
   oesophageal/GEJ cases with report+slide.
3. ~~ERIN feasibility~~ — ✅ PASSED 2026-08-10 (see feasibility report).

## Compute campaign (batch as ONE GPU allocation)
- ERIN UNI2/Virchow2 extraction: 1,045 oeso slides (serves Ch3 + Ch4)
- TCGA-ESCA extraction: 87 OAC diagnostic WSIs (serves Ch2 Parts A+B)
  — FIRST check for public TCGA foundation-model embedding releases; may halve the job.

## Cheap follow-ons once features exist
- TCGA TP53/WGD linear probe (Ch2 Part A replication) — minutes of compute; do same day.
- ERIN report-label vs expert-grade validation (Ch4) — CPU only.

## Known blockers recorded elsewhere
- barretts_training Phase 8 GPU rerun never launched: needs correct CNV feature-source
  dir + UNI2 feature index for the frozen cohort (existing CSVs belong to a different
  killcoyne cohort). Commands ready: `docs/final_analysis_foundation_launch_commands.md`.
- LGD2+ CNV window→gene map missing (importances exist per fold since 07-13 release).
- Interpretation cases must be reselected from FINAL strict pre-event OOF predictions.

## Standing cautions
- Report SWG fusion benefit as AUC+Brier-backed "likely benefit" (AUPRC CI includes zero).
- Never use ICGC ESAD as external validation (≡ OCCAMS).
- Ch2 endpoints: SWG=progression; OCCAMS+TCGA=survival (matched replication pair).

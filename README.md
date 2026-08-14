# Thesis — working index

Working title: **Histology-anchored multimodal deep learning for oesophageal cancer:
does adding a second modality help, and does it replicate across cohorts?**

This folder is the single place to see the whole thesis at once. It is a **thin
index**: plans, status, dataset matrix, and small manifests only.

## Rules
1. **No heavy data and no copied results here.** Canonical work stays where it is;
   this folder points to it (same principle as the clean repo's PROJECT_STATE).
2. **PLAN.md is the thesis-level state.** Update its status markers when a gate is
   passed or an arm completes. Chapter-internal detail stays in each project's own
   state file (e.g. `barretts_training/multimodal-barretts-progression/PROJECT_STATE.md`).
3. Date-stamp substantive updates in the changelog at the bottom of PLAN.md.

## Contents
- `PLAN.md` — chapter-by-chapter plan with done/not-done status and gates
- `DATASETS.md` — cohort/modality matrix, canonical paths, independence audit
- `GAPS.md` — open gates and dependency-ordered next steps
- `manifests/` — small case-level manifests (TCGA multimodal flags, built 2026-08-14
  from live GDC/TCIA APIs)

## Canonical work locations (pointers, not contents)
- **Ch2/Ch3 SWGCohort arm (done):** `/mnt/scratche/slow/fmlab/zuberi01/phd/barretts_retraining/barretts_training/`
  — canonical repo `multimodal-barretts-progression/` (PROJECT_STATE.md is source of truth)
- **ERIN data:** `/mnt/scratche/slow/fmlab/datasets/imaging/ERIN`
  — feasibility first-pass: `/mnt/scratche/slow/fmlab/zuberi01/phd/erin_multimodal_feasibility/` (PASSED 2026-08-10)
- **OCCAMS inputs:** `~/occams_work/` (master CSV + slide↔WGS inventory);
  TP53/WGD probe: `~/occams_scan/`; clinical survival baselines:
  `/mnt/scratche/slow/fmlab/zuberi01/phd/occams_multimodal/`
- **TCGA:** manifests here in `manifests/`; legacy explorations in `phd/tcga_exp/`

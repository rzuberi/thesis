# Dataset matrix and canonical paths (2026-08-14)

## Cohorts

| Cohort | Histology | Genomics | Clinical/EHR | Text | Endpoint | Scale | Access |
|---|---|---|---|---|---|---|---|
| SWGCohort (Barrett's) | H&E WSI | sWGS CNV | grade + surveillance | — | LGD2+ progression | 150 pt / 707 rows | local |
| ERIN | H&E WSI (2,280 imaged cases; 1,045 oeso slides) | none | report-derived | free-text reports (7,149) | dysplasia grade / progression | 2,537 pt; 1,454 with ≥2 timepoints | local |
| OCCAMS | H&E WSI (635 slides; UNI2+Virchow2 precomputed) | WGS (TP53, ploidy, WGD, CN) | survival, TNM, treatment | — | OAC outcome | 384 WGS; 141 features+labels | local |
| TCGA-ESCA (OAC) | diagnostic WSI | RNA+WXS+CNV+meth (open); TP53 via MC3, WGD via ABSOLUTE | survival (use TCGA-CDR), TNM, treatment | TCGA-Reports | OAC survival | 88 OAC (87 complete-modality) | open |
| TCGA-STAD GEJ pool | diagnostic WSI | same | same | TCGA-Reports | survival | 382 complete-modality | open |
| TCGA-Reports | — | — | — | 9,523 cleaned reports, joinable by case ID | Ch4 replication | pan-cancer | open (Mendeley hyg5xkznpx) |

## Independence audit
- ERIN ∩ SWGCohort = 6 / 1,992 patients → genuinely independent. ✅ verified
- **ICGC ESAD-UK ≡ OCCAMS** (same patients) → EXCLUDED from any external-validation role.
- TCGA is US-based, independent of all local cohorts.
- DFCI/Broad OAC (Dulak 2013, n=151, cBioPortal `esca_broad`): likely independent; genomics-only sanity checks (no usable WSIs).

## Raw data locations on cluster (verified 2026-08-14)

| Dataset | Fast pool (GPU working copy) | Slow pool | Size (fast) |
|---|---|---|---|
| ERIN | `/mnt/scratche/fast/fmlab/datasets/imaging/ERIN` | `/mnt/scratche/slow/fmlab/datasets/imaging/ERIN` | 5.4 TB |
| OCCAMS | `/mnt/scratche/fast/fmlab/datasets/imaging/occams` | `/mnt/scratche/slow/fmlab/datasets/imaging/occams` | 1.6 TB |
| SWGCohort | `/mnt/scratche/fast/fmlab/datasets/imaging/SWGCohort` | `/mnt/scratche/slow/fmlab/datasets/imaging/SWGCohort` | 794 GB |
| TCGA | — (not on cluster) | `~/reference/tcga` (2.5 GB: liver + colon only, SurvPGC leftovers — **no ESCA**) | — |

Also in `fmlab/datasets/imaging` (both pools): best2/best3/best4, delta, SEARCH,
ExVision, TissueSegmentation. Prefer the **fast** copies for GPU feature-extraction
jobs; slow copies are the archival source.

**TCGA-ESCA WSIs are NOT on the cluster yet** — the 87 complete-modality OAC
diagnostic slides (see `manifests/TCGA_multimodal_manifest.csv`, filter
`project=TCGA-ESCA`) must be downloaded from the GDC before the Ch2 TCGA arm runs.

## Canonical paths
- SWGCohort work: `/mnt/scratche/slow/fmlab/zuberi01/phd/barretts_retraining/barretts_training/`
  (clean repo `multimodal-barretts-progression/`; PROJECT_STATE.md = source of truth)
- ERIN data: `/mnt/scratche/slow/fmlab/datasets/imaging/ERIN`
  (reports: `data/PathologyReport_AnonIds.csv`; linkage: `WSIExport_Result_*.csv`;
  feasibility report: `phd/erin_multimodal_feasibility/ERIN_feasibility_report.md`)
- OCCAMS: `~/occams_work/occams_master_20260511.csv`, `OCCAMS slides linked to WGS.xlsx`,
  `slide_inventory.csv`; probe: `~/occams_scan/`; clinical baselines: `phd/occams_multimodal/`
- TCGA manifests: `manifests/TCGA_multimodal_manifest.csv`, `manifests/CPTAC_multimodal_manifest.csv`
  (one row per GDC case; flags: rna_seq, wxs_wgs, slide_image, methylation, mirna_seq,
  tcia_radiology; built 2026-08-14 from live GDC + TCIA NBIA APIs)

## Open-data facts worth keeping (checked 2026-08-14)
- TCGA-ESCA: 185 cases = 88 adenocarcinoma (87 complete RNA+WXS+slide) + 96 ESCC (95 complete).
- TCGA pan: 10,300 cases with RNA+WXS/WGS+slide; 1,061 also with TCIA radiology.
- No open Barrett's progression cohort with WSIs exists (TCGA ✗, HTAN Phase 1 ✗, TCIA ✗) → Ch3 replication ceiling is ERIN.
- CPTAC has no oesophageal cohort. MSK-CHORD lacks oesophagus + has no images.
- HANCOCK (head&neck, 763 pt, WSI+clinical+TMA, CC BY): optional out-of-organ methods check only.
- Genomics England 100kGP: managed access, no export; future-work only.

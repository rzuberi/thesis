# Thesis plan v2 — status-annotated (2026-08-14)

**Central question (reframed 2026-08-25, joint — see EXECUTION_PLAN amendment):**
where and why does adding a second modality to a histology model fail to replicate
across cohorts in oesophageal cancer — and how should the report-derived
supervision such studies depend on be validated?
**Secondary claim:** genomic state is not recoverable from H&E alone, so fusion is
necessary, not a convenience.

Modality sweep anchored on H&E: **+ genomics (Ch2), + structured clinical (Ch3),
+ free text (Ch4)** — each on ≥2 cohorts, at least one external.

Status key: ✅ done · 🟡 partial/exists-needs-work · ❌ not started · **[GATE]** feasibility check that decides commitment.

---

## Ch1 — Introduction, datasets, evaluation protocol
- 🟡 Modality-availability matrix (5 cohorts; TCGA columns from `manifests/`: 87 OAC complete-modality, 382 GEJ/gastric)
- ✅ Independence audit: ERIN∩SWGCohort = 6/1,992
- 🟡 Independence audit: ICGC ESAD ≡ OCCAMS exclusion — known, needs writing
- 🟡 Fusion taxonomy (late/early/intermediate) — defined; must map onto the ablations Ch2–4 actually run
- 🟡 Honest evaluation protocol (patient-disjoint nested CV, paired bootstrap on fusion delta, calibration, net benefit, negatives retained) — used in SWG work; freeze + write once, inherit everywhere

## Ch2 — Histology + Genomics
**Part A — necessity (promoted negative: genotype-from-H&E):**
- ✅ OCCAMS probe: H&E→TP53 AUC 0.48, H&E→WGD AUC 0.41 (`~/occams_scan/`)
- ❌ TCGA-OAC replication of same probe (labels: open MC3 TP53 + PanCanAtlas ABSOLUTE WGD/ploidy; needs TCGA WSI features — shared job with Part B)

**Part B — fusion:**
- ✅ SWGCohort H&E+CNV → LGD2+ progression — COMPLETE (final release 2026-07-13 + hardening 07-27..31).
  707 rows / 150 patients, frozen 5-fold patient-disjoint split, six model families.
  Best: late mean AUPRC 0.630 / AUC 0.774 / Brier 0.184 vs CNV-only 0.538 / 0.663 / 0.216.
  Paired deltas: AUC +0.111 (CI 0.002–0.219, excl. zero), Brier −0.032 (excl. zero),
  AUPRC +0.091 (CI −0.036–0.219, **includes zero** → report "likely benefit").
  Endpoint is LGD2+ neoplastic progression, NOT cancer/OAC.
- ❌ **[GATE]** OCCAMS H&E+WGS-features → survival/stage fusion first-pass (n=141).
  Note: `phd/occams_multimodal/` (May 2026) = clinical-only 5-yr survival baselines — useful baseline, not the fusion.
- ❌ TCGA-OAC same pairing, same survival endpoint (n=87; case list ✅ in `manifests/`; slides+features ❌ — check public embedding releases first)
- ❌ GEJ/gastric pooling sensitivity analysis (n≈382) — optional, decide after n=87 result
- 🟡 Depth layer: ABMIL attention ✅ (8 cases) + 3 case packs ✅ but need regenerating from final checkpoints; model-internal fusion attribution ❌; CNV window→gene map ❌ (per-fold importances now exist); fusion-strategy ablation ran (6 families ✅) — needs framing against Ch1 taxonomy

## Ch3 — Histology + Clinical/EHR
- ✅ SWGCohort H&E + grade/surveillance → progression (largely done; rerun under frozen Ch1 protocol to finalise)
- ✅ **[GATE PASSED 2026-08-10]** ERIN feasibility (`phd/erin_multimodal_feasibility/ERIN_feasibility_report.md`):
  2,280 imaged cases, 100% image→report linkage, 1,454/2,537 patients ≥2 timepoints
  (median span ~3.75 yr), full benign→carcinoma grade ladder. Labels previously extracted:
  2,446 graded patients (NDBE 4,804 / cancer 843 / HGD 528 / LGD 291 / IND 201).
- ❌ **[GATE]** ERIN UNI2/Virchow2 feature extraction (1,045 oeso slides, GPU)
- ❌ ERIN H&E + report-derived clinical → dysplasia/progression fusion (blocked by features)
- 🟡 Replication-ceiling statement (no open Barrett's WSI cohort: TCGA ✗, HTAN Ph1 ✗, TCIA ✗) — evidence gathered, needs a paragraph
- ❌ Depth layer: annotation-effort analysis, surveillance-framed calibration/net benefit, failure analysis

## Ch4 — Histology + Report Text (NEW)
Question: can free-text pathology reports substitute for expert labels in training and
evaluating histology models, and does report-supervision replicate across cohorts?
- ✅ ERIN report→label extraction working end-to-end (seed of the chapter)
- 🟡 Labeller built + NAMED: **pathladder** (`labeller/`, schema-driven, negation-aware,
  10 unit tests). Validated on TCGA reports 2026-08-15: histologic type 98% coverage /
  100% accuracy vs GDC (n=464); grade 77% coverage / 96.5% accuracy vs cBioPortal
  (n=375). Remaining: ERIN schema application + packaging/release.
- ❌ Validate report-derived labels vs expert grades (ERIN manual grades = ground truth; inputs all exist)
- ❌ Report-weak-supervision vs gold-label supervision on same H&E task (needs ERIN features — same GPU job as Ch3)
- ❌ **[GATE]** TCGA arm: download TCGA-Reports (9,523 machine-readable reports,
  Kefeli & Tatonetti, Patterns 2024; Mendeley hyg5xkznpx), join to WSI manifest,
  count usable oesophageal/GEJ cases with report+slide. Laptop job, no GPU.
- ❌ TCGA replication of the weak-supervision framework
- ❌ Depth layer: report–slide disagreement analysis

## Ch5 — Discussion
- ❌ Where fusion helped (3 pairings × cohorts)
- 🟡 Two-cohort necessity negative + clinical-collection implication (OCCAMS arm ✅)
- 🟡 Cohort effects; open-data landscape as replication-limit evidence; Genomics England = future work
- 🟡 Publications map (lab norm): SWG hardening → paper-bound ✅; Ch4 artifact = natural second manuscript ❌

---

## Changelog
- 2026-08-15: cluster in maintenance until Wed 19th ~17:00 — offline work session.
  Built + validated **pathladder** (Ch4 named artifact) on TCGA reports; built
  Ch2 TCGA-OAC label table (`data/tcga_oac_labels.csv`: 88 cases with CDR survival
  + TP53 (69 mut), 78 with ABSOLUTE ploidy/WGD (47 WGD+)); drafted four Ch1
  sections (`chapters/ch1/`); pre-registered OCCAMS v2 interpretation
  (`docs/occams_v2_decision_tree.md`).
- 2026-08-14 (PM): four feasibility gates run as cluster jobs (see GAPS.md + feasibility/):
  Ch4 TCGA-Reports PASSED (146 ESCA / 507 ESCA+STAD / 9,517 pan-cancer report+slide);
  Ch2 TCGA download PASSED (65 OAC DX slides, 84 GB — note 65/87, not 87);
  Ch3/Ch4 ERIN extraction PASSED on L40S (~84 s/slide, ~25 GPU-h campaign);
  Ch2 OCCAMS fusion first-pass WEAK (no fusion benefit with mean-pool + crude
  endpoint) → redesigned second pass required (ABMIL, vital status, richer CN).
- 2026-08-14: v2 created. Added Ch4 (histology+text). Statuses reconciled against
  cluster state: SWG final numbers from PROJECT_STATE; ERIN feasibility gate marked
  PASSED (2026-08-10 report); occams_multimodal noted as clinical-only baselines.

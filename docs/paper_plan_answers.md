# BE paper plan: answers (SWG progressor cohort)

## 1. Header
- Date: 25 September 2026. Commit at start: `1d27002`. Pre-specification commit: `db236a0` (text reproduced verbatim in §8). Script commits before results: `187dda8`, `5bf5419`, `529cccc`, `b4bc409`. Results commit (all result files, figures and scripts): `98ed676`; this rendered text is the next commit.
- Release used for every number: the frozen `chapter1_lgd2_final_pre_event_20260713_final` only (item 0: no confirmed errors: all items run on the frozen release only).
- New scripts (`scripts/paper_plan/`): `pp_audit.py`, `pp_latent.py`, `pp_main.py`, `pp_montage.py`, `pp_review_pack.py`, `pp_render.py`.
- New results (`results/paper_plan/`): `audit_item0.json` (v1), `audit_item0_v2.json`, `main_items.json`, `latent_item6.json`, `attention_item7_rows.csv`, `perm_importance_item8b.json`; figures `figs/km/*.png`, `figs/latent/*.png`, `figs/attention/M*.png`. Cluster-only (identifiable or row-level): `feasibility/paper_plan/` (audit rows, patient scores, later-disease table, embeddings, montage and review-pack manifests, review pack thumbnails).
- Conventions: patient level, patient score = max over strict pre-event rows; rank AUROC and AUPRC to 3 decimals; CIs = 2,000 patient bootstraps `RandomState(0)`; permutations = 2,000 patient-label permutations `RandomState(0)`. Fold honesty: every fitted quantity (clinical arms, operating thresholds, tertile cut-points, probes, kNN, scalers, PCA/UMAP) is fitted on the four training outer folds (inner CV on the release's patient-keyed inner folds) and applied to the held-out fold.

## 2. Plan status table
| whiteboard element | status | key number / figure |
|---|---|---|
| Intro: Killcoyne 2020 comparison (item 1) | DONE | their column filled from the paper PDF with page refs; 82 of our patients / 500 rows have Killcoyne per-sample predictions |
| Intro: histology as good as CNV? (item 2) | DONE | WSI − CNV ΔAUROC +0.068 [-0.065, +0.196], perm p 0.1434 (n 150, 50 events) |
| Table row Clinical only × SWG (item 3) | DONE | 3a AUROC 0.765 [0.684, 0.844]; 3b on 27 complete-case patients |
| Table row CNV × SWG | DONE | 0.663 [0.569, 0.754] |
| Table row WSI × SWG | DONE | 0.731 [0.640, 0.814] |
| Table row Early fusion × SWG | DONE | 0.738 [0.646, 0.818] |
| Table row Intermediate fusion × SWG | DONE | 0.741 [0.653, 0.818] |
| Table row Late fusion × SWG | DONE | 0.774 [0.687, 0.849]; vs WSI +0.043 [0.014, 0.071], selection-adjusted p 0.2649 |
| Every table row × ACE-B | NOT AVAILABLE | no ACE-B slides, features or CNV on the cluster (closeout item N); nothing run |
| Discussion 1: risk groups (item 5) | DONE | late_mean tertiles: high-group rate 0.585 vs low 0.137; Cox HR high vs low [1.792, 0.788, 4.075]; `results/paper_plan/figs/km/km_late_mean_tertile.png` |
| Discussion 2: latent space (item 6) | DONE | probe AUROC image 0.784, intermediate 0.819, co-attention 0.736; figs `results/paper_plan/figs/latent/` |
| Discussion 3: attention patches (item 7) | DONE | Spearman image-only vs intermediate median 0.867, vs co-attention 0.347; montages cluster-only `feasibility/paper_plan/figs/attention/` |
| Discussion 4: CNV prediction change (item 8) | DONE | 8a Spearman CNV vs late 0.387, NRI [0.17, -0.082, 0.418]; 8b top feature cnv_only chr17p |
| Discussion 5: false positives (item 9) | DONE | late_mean FP 40 / TN 60; later LGD+ [11, 40, 0.275] vs [8, 60, 0.133], Fisher p 0.117 |
| Discussion 6: false negatives (item 10) | DONE | late_mean FN 11 / TP 39; review pack 31 FN + 31 TP + 31 TN slides (cluster) |

## 3. Item 0: CNV audit of the overlap subgroup
**Status.** DONE. **Decision: no confirmed errors: all items run on the frozen release only** (confirmed-error rows 0, patients 0). Every later number uses the frozen release.

**Pre-specification.** `db236a0` §"Item 0". Two versions of the audit script were run: v1 (commit `187dda8`, `audit_item0.json`) had a slide-filename parser that failed on `PS00 4239 …` names and mapped the discovery sheet's numeric patient id through `slide_matching.PatientID`, which is a different numbering; v2 (commit `529cccc`, `audit_item0_v2.json`) parses those names and maps the sheet id to the release patient owning the majority of its CNV ids. Both are kept; the decision is identical under both (0 confirmed errors). v1 flag counts (artefacts): patient-sheet 48 / 26 rows, slide-filename 35 / 27 rows (overlap / comparator).

**Result (v2): discrepancy counts per subgroup** (rows, patients). Overlap = 54 patients / 279 rows ({'discovery': 192, 'validation': 87}); comparator = 25 `never_in_ERIN` patients drawn with `RandomState(0)` / 126 rows ({'discovery': 95, 'validation': 31}); the remaining 71 patients / 302 rows are shown for completeness.

| check | also_in_ERIN (54 pts) | comparator (25 pts) | other 71 pts |
|---|---|---|---|
| patient: slide_matching ≠ release | 0 rows / 0 pts | 0 rows / 0 pts | 0 rows / 0 pts |
| patient: sequencing sheet (majority-mapped id) ≠ release | 1 rows / 1 pts | 2 rows / 1 pts | 3 rows / 1 pts |
| accession: slide_matching ≠ release | 0 rows / 0 pts | 0 rows / 0 pts | 0 rows / 0 pts |
| accession: sequencing sheet ≠ release | 0 rows / 0 pts | 0 rows / 0 pts | 0 rows / 0 pts |
| accession: slide filename ≠ release | 0 rows / 0 pts | 7 rows / 1 pts | 8 rows / 4 pts |
| CNV sheet accession ≠ slide accession (same row) | 0 rows / 0 pts | 7 rows / 1 pts | 8 rows / 4 pts |
| date: sheet endoscopy year ≠ release year | 0 rows / 0 pts | 0 rows / 0 pts | 6 rows / 2 pts |
| date: slide_matching date ≠ release (> 366 d, non-placeholder) | 0 rows / 0 pts | 0 rows / 0 pts | 0 rows / 0 pts |
| date: DB report date ≠ release (> 366 d) | 0 rows / 0 pts | 0 rows / 0 pts | 0 rows / 0 pts |
| grade two-tier: sheet ≠ release | 27 rows / 9 pts | 12 rows / 6 pts | 15 rows / 12 pts |
| grade two-tier: slide_matching ≠ release | 24 rows / 8 pts | 12 rows / 6 pts | 15 rows / 12 pts |
| grade two-tier: DB confirmed code ≠ release | 0 rows / 0 pts | 0 rows / 0 pts | 0 rows / 0 pts |
| next-biopsy label: master ≠ DB scrape | 17 rows / 5 pts | 4 rows / 4 pts | 7 rows / 7 pts |
| next-biopsy label: release ≠ next DB report | 21 rows / 5 pts | 3 rows / 3 pts | 6 rows / 6 pts |

Rows with a slide_matching entry: 279 / 126 / 302; with a DB report matched by accession: 256 / 92 / 199. Sheet numeric ids mapping to more than one release patient: 0.

**CNV attached to a different endoscopy than sequenced.** The row's CNV sheet accession equals the slide accession in every row of every subgroup where both exist (0 flags in v2); the only residual flags are in 'other' (slide filename year differs from the accession year in the filename for 8 rows / 4 patients, where slide_matching agrees with the release) and the comparator (7 rows / 1 patient, same pattern).

**Label-source disagreements (not chain errors).** Release grade LGD where both the sequencing sheet and slide_matching say NDBE/IND: 42 rows; the reverse: 9 rows. The release grade comes from the DB confirmed code for most rows (`GradeSource` scraped_confirmed), so grade-vs-DB disagreement is 0 by construction. Next-biopsy label: 381 rows carry both a master and a DB-scrape label; 28 disagree at two-tier level. Recomputing the LGD2+ patient status with the alternative source: DB-scrape-preferred changes 2 overlap patients (0 to progressor, 2 to non-progressor) and 4 never-in-ERIN patients (2 / 2); master-preferred changes 0 + 0 (the release already prefers master). Grade-source mix per subgroup: {'master_label_fallback': {'also_in_ERIN': 19, 'comparator_25': 34, 'other': 102}, 'scraped_confirmed': {'also_in_ERIN': 256, 'comparator_25': 92, 'other': 199}, 'scraped_research': {'also_in_ERIN': 4, 'comparator_25': 0, 'other': 1}}.

**Killcoyne 2020 per-sample predictions vs ours** (`41591_2020_1033_MOESM4_ESM.xlsx` sheet "Supporting data for Figure 2a": leave-one-patient-out probability and risk class for 773 discovery samples; join on CNV sample id).

| quantity | value |
|---|---|
| matched rows / patients | 500 / 82 (rows by subgroup {'never_in_ERIN': 308, 'also_in_ERIN': 192}) |
| Killcoyne patient status vs our LGD2+ label (patients) | {'0': {'Non-Progressor': 37, 'Progressor': 5}, '1': {'Non-Progressor': 6, 'Progressor': 34}} |
| Spearman, Killcoyne probability vs our cnv_only OOF (rows) | 0.278 (n 500) |
| Killcoyne class by our row label (rows) | {'0': {'High': 110, 'Low': 234, 'Moderate': 80}, '1': {'High': 41, 'Low': 24, 'Moderate': 11}} |
| patients | n | events | AUROC Killcoyne max prob (their LOPO model, our endpoint) | AUROC our cnv_only (release OOF) |
|---|---|---|---|---|
| all | 82 | 40 | 0.718 | 0.562 |
| also_in_ERIN | 25 | 11 | 0.792 | 0.253 |
| never_in_ERIN | 57 | 29 | 0.688 | 0.702 |

**Count reconciliation.** Rows whose CNV id is in the 777-sample discovery sheet: 504; in the Killcoyne prediction table: 500. Patients with any such row: 82 / 82; with all rows: 82 / 81; modal sheet: 82. **82 is correct** under every definition computed here; the pipeline document's 69 matches none of them and its derivation is not recorded (the document is undated and cites no file).

**Method.** `pp_audit.py` (v2). **Sources.** `results/paper_plan/audit_item0_v2.json` · `scripts/paper_plan/pp_audit.py` · commit 98ed676; v1 `audit_item0.json` (commit 187dda8). Row table `feasibility/paper_plan/audit_rows.csv` (cluster).

**Caveats.** The sequencing sheet and slide_matching both originate from the Fitzgerald-lab sample records and may not be independent of each other; the confirmed-error rule required agreement of two non-release sources on patient, accession or date, and none occurred. Grade and next-label disagreements are between label sources, not chain errors, and were outside the pre-specified corrected-release trigger; their effect on patient status is quantified above (≤ 6 patients). The Killcoyne comparison uses their in-cohort LOPO predictions against our LGD2+ endpoint, not their HGD/IMC endpoint.

## 4. Items 1–10

### Item 1. Killcoyne 2020 comparison
**Question.** How do our cohort, unit, endpoint, eligibility, CNV representation, depth and evaluation compare with Killcoyne 2020, and how much do the cohorts overlap?

**Status.** DONE (their column from the PDF and supplementary xlsx on the cluster; page numbers refer to the `pdftotext` page index of `s41591-020-1033-y.pdf`, Nat Med 26:1726–1732).

| field | ours (frozen release; closeout item L) | Killcoyne 2020 (source) |
|---|---|---|
| cohort | 150 patients, 707 rows, 50 progressor patients (LGD2+), 107 positive rows | discovery 88 patients / 777 biopsies sequenced, 773 passing QC; 45 progressors NDBE→HGD/IMC, 43 non-progressors; validation 76 patients / 213 samples passing QC (219 sequenced) (PDF p.1 abstract; p.4 Fig 2 legend; p.8 Methods) |
| design | retrospective surveillance cohort; no case-control matching documented in the release | retrospective, demographically matched case–control; cases and controls matched for age, gender and BE segment length; NP min follow-up 3 y (6.7 ± 3.2), P min 1 y (6.1 ± 3.4) (p.1; p.2 Fig 1 legend; p.8 Methods) |
| unit | one biopsy slide + one CNV profile per row; patient = max over rows | one pooled per-level biopsy sample per row; per-sample predictions; per-endoscopy/patient aggregation did not change accuracy (p.2; p.8; p.13 Ext Data Fig 2b) |
| endpoint | `NextBiopsyProgression_LGD2plus`: next biopsy HGD+ or second consecutive LGD (code `src/barrett/labels/lgd2.py`) | a single biopsy graded HGD or IMC (p.8 Methods) |
| eligibility | strict pre-event rows only (at-event, post-event and non-evaluable rows excluded) | all samples incl. diagnostic HGD/IMC in the main model; models excluding HGD/IMC reported (p.2; p.13 Ext Data Fig 2a) |
| CNV representation | QDNAseq 50 kb → 5-Mb window features + 39 arm features + complexity cx (features_5mb_armdiff, features_arms, cx) | QDNAseq 50-kb bins, genome-wide standardised, elastic-net logistic regression over bins/arms; bin size tuned 15–500 kb (p.8; p.23 Ext Data Fig 9) |
| depth | 0.4× as stated in project documents (not verified from BAMs); median reads per profile in closeout item C | sWGS average depth 0.4× on Illumina HiSeq (p.1; p.8) |
| evaluation | 5-fold patient-level nested CV (split seed 20260713); AUPRC primary in the release, AUROC here | leave-one-patient-out on discovery; independent validation cohort; 50 kb LOPO AUC 0.87 discovery, 0.84 validation (p.23–24 Ext Data Fig 9); supplementary `MOESM15` Ext Data Fig 9c: 50 kb discovery AUC 0.865 [0.839, 0.891]; combined discovery + validation (n = 164) cross-validated AUC 0.89, spec 0.83, sens 0.82 (p.2) |
| risk classes | tertiles of training-fold scores (item 5); Killcoyne fixed classes also applied | low Pr ≤ 0.3 (sens 0.87, spec 0.65), moderate 0.3–0.5, high Pr ≥ 0.5 (sens 0.72, spec 0.82) (p.2) |
| overlap | 504 of 707 rows / 82 of 150 patients have a CNV id in the discovery sheet; 500 rows / 82 patients appear in the published per-sample prediction table; 203 rows / 68 patients are from the validation sheet (closeout item C) | — |

**CNV-only AUROC, Killcoyne-overlap patients vs the rest** (patient level, release OOF):

| patients | n | events | rows | cnv_only | image_only | late_mean |
|---|---|---|---|---|---|---|
| in_killcoyne_discovery_table | 82 | 40 | 504 | 0.564 [0.427, 0.693] | 0.649 [0.527, 0.765] | 0.691 [0.569, 0.803] |
| not_in_table | 68 | 10 | 203 | 0.683 [0.483, 0.865] | 0.879 [0.785, 0.955] | 0.900 [0.814, 0.968] |

**Sources.** `results/paper_plan/main_items.json` · `scripts/paper_plan/pp_main.py` · commit 98ed676 (key `item1_overlap`); `audit_item0_v2.json`; `docs/closeout_for_review.md` item L (commit 1d27002); Killcoyne PDF and `MOESM4/7/15` xlsx (cluster `phd/`). **Caveats.** Their AUCs are for an HGD/IMC endpoint in their cohort; not comparable one-to-one with our LGD2+ endpoint. Our CNV-only arm on the Killcoyne-overlap patients is compared with their published LOPO predictions in item 0.

### Item 2. Histology vs CNV
**Question.** Is image-only as good as CNV-only on the same patients?

**Status.** DONE.

| patients | n | events | WSI AUROC | CNV AUROC | ΔAUROC WSI − CNV [CI] | paired perm p | WSI AUPRC | CNV AUPRC | ΔAUPRC [CI] |
|---|---|---|---|---|---|---|---|---|---|
| all_150 | 150 | 50 | 0.731 | 0.663 | +0.068 [-0.065, +0.196] | 0.1434 | 0.557 | 0.538 | +0.019 [-0.119, +0.184] |
| never_in_ERIN_96 | 96 | 36 | 0.744 | 0.760 | -0.016 [-0.172, +0.143] | 0.5807 | 0.641 | 0.718 | -0.077 [-0.237, +0.124] |
| also_in_ERIN_54 | 54 | 14 | 0.704 | 0.454 | +0.250 [0.040, 0.452] | 0.013 | 0.408 | 0.242 | +0.165 [0.026, 0.388] |

**Method.** Release OOF probabilities, patient max; paired bootstrap and paired label permutation as in the conventions. No corrected release exists (item 0). **Sources.** `results/paper_plan/main_items.json` · `scripts/paper_plan/pp_main.py` · commit 98ed676 (`item4_tables.*.item2_image_vs_cnv`). **Caveats.** Same patients, different feature pipelines; the subgroups are post hoc (closeout item D).

### Item 3. Clinical-only arm (new)
**Question.** What does a clinical-only arm achieve, on all patients (3a) and with demographics (3b)?

**Status.** DONE.

**Pre-specification.** `db236a0` §"Item 3". Covariates considered for 3a: ['grade', 'maxsofar', 'streak', 'bidx', 'dsp', 'year']; patient coverage {'grade': 1.0, 'maxsofar': 1.0, 'streak': 1.0, 'bidx': 1.0, 'dsp': 1.0, 'year': 1.0}; used (coverage ≥ 0.9): ['grade', 'maxsofar', 'streak', 'bidx', 'dsp', 'year']. C chosen per outer fold: {'1': 0.1, '2': 0.01, '3': 0.1, '4': 0.1, '5': 0.01}. 3b covariates: ['grade', 'maxsofar', 'streak', 'bidx', 'dsp', 'year', 'age', 'sex_m', 'pragueC', 'pragueM', 'smoke']; patients in the demographics sheet 66; complete cases 27 patients / 204 rows; C per fold {'1': 0.1, '2': 0.01, '3': 10.0, '4': 0.01, '5': 0.01}.

3a on all 150: AUROC 0.765 [0.684, 0.844], AUPRC 0.547 [0.437, 0.711] (n 150, 50 events).
**3b subset, all arms re-evaluated on the same patients** (n 27, events 9):

| arm | AUROC [CI] | AUPRC [CI] |
|---|---|---|
| Clinical + demographics (3b) | 0.568 [0.272, 0.841] | 0.575 [0.256, 0.840] |
| Clinical only (3a) | 0.741 [0.477, 0.954] | 0.731 [0.431, 0.938] |
| CNV | 0.488 [0.228, 0.764] | 0.396 [0.190, 0.713] |
| WSI | 0.617 [0.349, 0.864] | 0.626 [0.338, 0.861] |
| Early fusion | 0.623 [0.381, 0.849] | 0.473 [0.244, 0.807] |
| Intermediate fusion | 0.648 [0.421, 0.853] | 0.555 [0.242, 0.809] |
| Late fusion (mean) | 0.636 [0.376, 0.865] | 0.560 [0.252, 0.844] |
| Co-attention fusion (extra) | 0.593 [0.368, 0.827] | 0.408 [0.218, 0.756] |
| Late stack-logit fusion (extra) | 0.623 [0.375, 0.841] | 0.494 [0.247, 0.818] |

Δ 3b − 3a on the subset: [-0.456, +0.095].

**Method.** L2 logistic, C by inner CV (release inner folds, patient-level AUROC), standardisation on outer training rows, patient = max over rows. **Sources.** `results/paper_plan/main_items.json` · `scripts/paper_plan/pp_main.py` · commit 98ed676 (`item3`). **Caveats.** `BiopsyIndex`, `DaysSincePreviousBiopsy` and the row year encode surveillance history, not biology; 3b is a complete-case subset of 27 patients / 9 events with CIs spanning most of the range; it cannot rank arms.

### Item 4. Main results table
**Question.** All arms on SWG with paired fusion differences; ACE-B column.

**Status.** DONE for SWG; ACE-B NOT AVAILABLE (no ACE-B slides, features or CNV exist on the cluster; closeout item N; nothing was run).

**All 150 patients**

| arm | AUROC [CI] | AUPRC [CI] | n | events |
|---|---|---|---|---|
| Clinical only (3a) | 0.765 [0.684, 0.844] | 0.547 [0.437, 0.711] | 150 | 50 |
| CNV | 0.663 [0.569, 0.754] | 0.538 [0.411, 0.671] | 150 | 50 |
| WSI | 0.731 [0.640, 0.814] | 0.557 [0.426, 0.717] | 150 | 50 |
| Early fusion | 0.738 [0.646, 0.818] | 0.590 [0.453, 0.733] | 150 | 50 |
| Intermediate fusion | 0.741 [0.653, 0.818] | 0.567 [0.435, 0.714] | 150 | 50 |
| Late fusion (mean) | 0.774 [0.687, 0.849] | 0.630 [0.490, 0.772] | 150 | 50 |
| Co-attention fusion (extra) | 0.739 [0.652, 0.821] | 0.548 [0.428, 0.703] | 150 | 50 |
| Late stack-logit fusion (extra) | 0.737 [0.648, 0.814] | 0.530 [0.412, 0.684] | 150 | 50 |

Paired differences (fusion arm minus reference):

| fusion arm | vs | ΔAUROC [CI] | ΔAUPRC [CI] | naive perm p | selection-adjusted p (max over 5 fusion arms) |
|---|---|---|---|---|---|
| Early fusion | WSI | +0.007 [-0.056, +0.067] | +0.033 [-0.080, +0.125] | 0.4418 | 0.7421 |
| Intermediate fusion | WSI | +0.010 [-0.053, +0.067] | +0.010 [-0.086, +0.090] | 0.3878 | 0.6907 |
| Late fusion (mean) | WSI | +0.043 [0.014, 0.071] | +0.073 [0.006, 0.123] | 0.0025 | 0.2649 |
| Co-attention fusion (extra) | WSI | +0.008 [-0.071, +0.093] | -0.009 [-0.125, +0.100] | 0.4253 | 0.7266 |
| Late stack-logit fusion (extra) | WSI | +0.005 [-0.029, +0.037] | -0.027 [-0.104, +0.039] | 0.3583 | 0.7631 |
| Early fusion | CNV | +0.075 [-0.038, +0.183] | +0.051 [-0.055, +0.166] | 0.089 | 0.1674 |
| Intermediate fusion | CNV | +0.078 [-0.035, +0.193] | +0.029 [-0.084, +0.162] | 0.0825 | 0.1534 |
| Late fusion (mean) | CNV | +0.111 [-0.001, +0.222] | +0.091 [-0.032, +0.226] | 0.018 | 0.053 |
| Co-attention fusion (extra) | CNV | +0.076 [-0.032, +0.184] | +0.010 [-0.100, +0.142] | 0.065 | 0.1639 |
| Late stack-logit fusion (extra) | CNV | +0.074 [-0.044, +0.188] | -0.008 [-0.120, +0.127] | 0.1009 | 0.1779 |

**Exploratory block (not merged): ERIN grade-head fusion, closeout canonical v4.** From `results/closeout/closeout_main.json` (commit 602a40e): head alone 0.753 [0.659, 0.840]; image + CNV + head 0.850 [0.779, 0.909]; gain vs fold-z image + CNV +0.067 [+0.022, +0.114]; selection-adjusted permutation p 0.069 (maximum over 28 evaluated third arms) and 0.078 (canonical gain against the same null); the pre-registered sanity gate (imputed grade vs pathologist grade ≥ 0.7) failed for every head (canonical 0.597). Reported here as exploratory only.

**never_in_ERIN (96)**

| arm | AUROC [CI] | AUPRC [CI] | n | events |
|---|---|---|---|---|
| Clinical only (3a) | 0.768 [0.662, 0.859] | 0.619 [0.470, 0.791] | 96 | 36 |
| CNV | 0.760 [0.652, 0.858] | 0.718 [0.574, 0.840] | 96 | 36 |
| WSI | 0.744 [0.634, 0.850] | 0.641 [0.492, 0.818] | 96 | 36 |
| Early fusion | 0.812 [0.710, 0.896] | 0.776 [0.651, 0.883] | 96 | 36 |
| Intermediate fusion | 0.827 [0.738, 0.909] | 0.773 [0.643, 0.891] | 96 | 36 |
| Late fusion (mean) | 0.819 [0.722, 0.907] | 0.757 [0.615, 0.883] | 96 | 36 |
| Co-attention fusion (extra) | 0.824 [0.728, 0.909] | 0.764 [0.628, 0.881] | 96 | 36 |
| Late stack-logit fusion (extra) | 0.772 [0.668, 0.867] | 0.662 [0.511, 0.816] | 96 | 36 |

| fusion arm | vs | ΔAUROC [CI] | ΔAUPRC [CI] | naive perm p | selection-adjusted p (max over 5 fusion arms) |
|---|---|---|---|---|---|
| Early fusion | WSI | +0.068 [-0.007, +0.144] | +0.134 [0.015, 0.218] | 0.0615 | 0.1499 |
| Intermediate fusion | WSI | +0.084 [0.020, 0.158] | +0.132 [0.017, 0.212] | 0.0145 | 0.084 |
| Late fusion (mean) | WSI | +0.076 [0.042, 0.112] | +0.116 [0.038, 0.165] | 0.0005 | 0.1169 |
| Co-attention fusion (extra) | WSI | +0.080 [-0.020, +0.187] | +0.123 [-0.025, +0.240] | 0.0755 | 0.1014 |
| Late stack-logit fusion (extra) | WSI | +0.029 [-0.015, +0.073] | +0.021 [-0.094, +0.100] | 0.072 | 0.4628 |
| Early fusion | CNV | +0.052 [-0.081, +0.189] | +0.057 [-0.075, +0.186] | 0.2314 | 0.3778 |
| Intermediate fusion | CNV | +0.068 [-0.066, +0.205] | +0.055 [-0.086, +0.211] | 0.1714 | 0.2854 |
| Late fusion (mean) | CNV | +0.060 [-0.076, +0.194] | +0.039 [-0.100, +0.191] | 0.1964 | 0.3348 |
| Co-attention fusion (extra) | CNV | +0.064 [-0.065, +0.194] | +0.046 [-0.089, +0.190] | 0.1549 | 0.3073 |
| Late stack-logit fusion (extra) | CNV | +0.013 [-0.125, +0.149] | -0.056 [-0.199, +0.101] | 0.4198 | 0.6137 |

**also_in_ERIN (54)**

| arm | AUROC [CI] | AUPRC [CI] | n | events |
|---|---|---|---|---|
| Clinical only (3a) | 0.809 [0.681, 0.907] | 0.491 [0.300, 0.763] | 54 | 14 |
| CNV | 0.454 [0.280, 0.627] | 0.242 [0.142, 0.406] | 54 | 14 |
| WSI | 0.704 [0.550, 0.841] | 0.408 [0.240, 0.682] | 54 | 14 |
| Early fusion | 0.586 [0.423, 0.742] | 0.307 [0.179, 0.530] | 54 | 14 |
| Intermediate fusion | 0.577 [0.424, 0.716] | 0.304 [0.177, 0.521] | 54 | 14 |
| Late fusion (mean) | 0.679 [0.522, 0.815] | 0.382 [0.224, 0.636] | 54 | 14 |
| Co-attention fusion (extra) | 0.559 [0.390, 0.717] | 0.285 [0.170, 0.482] | 54 | 14 |
| Late stack-logit fusion (extra) | 0.668 [0.522, 0.802] | 0.350 [0.208, 0.576] | 54 | 14 |

| fusion arm | vs | ΔAUROC [CI] | ΔAUPRC [CI] | naive perm p | selection-adjusted p (max over 5 fusion arms) |
|---|---|---|---|---|---|
| Early fusion | WSI | -0.118 [-0.235, -0.007] | -0.101 [-0.259, -0.004] | 0.943 | 1.0 |
| Intermediate fusion | WSI | -0.127 [-0.250, -0.014] | -0.103 [-0.263, -0.008] | 0.9785 | 1.0 |
| Late fusion (mean) | WSI | -0.025 [-0.082, +0.031] | -0.026 [-0.121, +0.062] | 0.8401 | 0.9615 |
| Co-attention fusion (extra) | WSI | -0.145 [-0.286, -0.009] | -0.123 [-0.297, -0.023] | 0.97 | 1.0 |
| Late stack-logit fusion (extra) | WSI | -0.036 [-0.101, +0.024] | -0.058 [-0.171, +0.002] | 0.922 | 0.9835 |
| Early fusion | CNV | +0.132 [-0.066, +0.317] | +0.065 [-0.026, +0.209] | 0.078 | 0.1579 |
| Intermediate fusion | CNV | +0.123 [-0.070, +0.314] | +0.062 [-0.036, +0.215] | 0.085 | 0.1924 |
| Late fusion (mean) | CNV | +0.225 [0.034, 0.405] | +0.140 [0.020, 0.334] | 0.012 | 0.0205 |
| Co-attention fusion (extra) | CNV | +0.105 [-0.105, +0.294] | +0.043 [-0.048, +0.153] | 0.1069 | 0.2594 |
| Late stack-logit fusion (extra) | CNV | +0.214 [0.018, 0.405] | +0.107 [0.000, 0.264] | 0.018 | 0.0275 |

**Arms.** Clinical 3a: L2 logistic on row covariates (item 3), this repo. CNV: `cnv_only` = impute(median) → standardise → PCA(64) → random forest (500 trees, depth 20, balanced), on 5-Mb + arm + cx CNV features; `<release>/training_final_nested_cv_v1/cnv_only/fold*/model.joblib`. WSI: `image_only` = gated-attention MIL (hidden 256, attn 128) on 256 UNI2 tile embeddings (1536-d, release level-2 tiles); `image_only/fold*/model.pt`. Early: `early_fusion` = MLP (512) on [mean tile embedding ‖ standardised CNV]; Intermediate: `intermediate_fusion` = ABMIL image branch (256) ‖ CNV MLP (128) → fusion MLP; Co-attention: `coattention_fusion` = CNV-embedding query over tile keys, pooled values ‖ CNV embedding → fusion MLP; Late (mean): `late_mean` = plain mean of image_only and cnv_only probabilities; Late stack: `late_stack_logit` = logistic regression on the two probabilities. Code: `multimodal-barretts-progression/src/barrett/models/*.py`, trainer `scripts/24_run_lgd2_final_outer_fold.py` (pipeline commit 98ba8682), configs `fold*/resolved_config.yaml`.

**Sources.** `results/paper_plan/main_items.json` · `scripts/paper_plan/pp_main.py` · commit 98ed676 (`item4_tables`). **Caveats.** The five fusion arms share the same image and CNV inputs; the selection-adjusted p treats the choice among them as post hoc and maximises over the five fusion rows of this table (early, intermediate, late-mean, co-attention, late-stack); the digest's 0.225 (`results/numbers/swg_rep02_selection.json`) maximised over a different five-arm set that included the fold-z late mean instead of late-stack, so the two values are not the same statistic. Subgroup tables are post hoc.

### Primary operating point (items 5–10)
**Threshold** fitted on the four training folds' patient scores for sensitivity ≥ 0.80, applied to the held-out fold.

| model | fold | threshold | n test | events | sensitivity | specificity |
|---|---|---|---|---|---|---|
| late_mean | 1 | 0.395 | 30 | 10 | 0.6 | 0.5 |
| late_mean | 2 | 0.361 | 30 | 10 | 0.8 | 0.75 |
| late_mean | 3 | 0.356 | 30 | 10 | 0.9 | 0.4 |
| late_mean | 4 | 0.395 | 30 | 10 | 0.6 | 0.9 |
| late_mean | 5 | 0.301 | 30 | 10 | 1.0 | 0.45 |
| image_only | 1 | 0.556 | 30 | 10 | 0.4 | 0.45 |
| image_only | 2 | 0.486 | 30 | 10 | 0.7 | 0.75 |
| image_only | 3 | 0.406 | 30 | 10 | 0.9 | 0.3 |
| image_only | 4 | 0.512 | 30 | 10 | 0.6 | 0.7 |
| image_only | 5 | 0.387 | 30 | 10 | 1.0 | 0.3 |
| cnv_only | 1 | 0.207 | 30 | 10 | 0.8 | 0.1 |
| cnv_only | 2 | 0.206 | 30 | 10 | 1.0 | 0.35 |
| cnv_only | 3 | 0.207 | 30 | 10 | 0.8 | 0.45 |
| cnv_only | 4 | 0.206 | 30 | 10 | 0.9 | 0.5 |
| cnv_only | 5 | 0.234 | 30 | 10 | 0.5 | 0.85 |
| clinical_3a | 1 | 0.125 | 30 | 10 | 1.0 | 0.5 |
| clinical_3a | 2 | 0.125 | 30 | 10 | 1.0 | 0.5 |
| clinical_3a | 3 | 0.135 | 30 | 10 | 0.8 | 0.5 |
| clinical_3a | 4 | 0.145 | 30 | 10 | 0.6 | 0.75 |
| clinical_3a | 5 | 0.145 | 30 | 10 | 0.6 | 0.85 |
| v4_exploratory | 1 | 0.49 | 30 | 10 | 0.7 | 0.45 |
| v4_exploratory | 2 | 0.477 | 30 | 10 | 0.8 | 0.75 |
| v4_exploratory | 3 | 0.477 | 30 | 10 | 0.8 | 0.8 |
| v4_exploratory | 4 | 0.458 | 30 | 10 | 0.9 | 0.95 |
| v4_exploratory | 5 | 0.49 | 30 | 10 | 0.7 | 0.75 |

| model | pooled sensitivity | pooled specificity | flagged | n | events |
|---|---|---|---|---|---|
| late_mean | 0.78 | 0.6 | 79 | 150 | 50 |
| image_only | 0.72 | 0.5 | 86 | 150 | 50 |
| cnv_only | 0.8 | 0.45 | 95 | 150 | 50 |
| clinical_3a | 0.8 | 0.62 | 78 | 150 | 50 |
| v4_exploratory | 0.78 | 0.74 | 65 | 150 | 50 |

`v4_exploratory` = fold-z mean of image_only, cnv_only and the leak-free ERIN grade head (closeout v4). **Sources.** `results/paper_plan/main_items.json` · `scripts/paper_plan/pp_main.py` · commit 98ed676 (`operating_point`).

### Item 5. Risk stratification groups
**Question.** Do training-fold tertiles (and Killcoyne's fixed classes) separate progression risk, per model?

**Status.** DONE. No Killcoyne-style thresholds are documented in the release metadata (closeout: none found); the alternative applied is the paper's fixed classes (Killcoyne et al. 2020 Nat Med, results text: low Pr <= 0.3, moderate 0.3-0.5, high Pr >= 0.5 (p. 1727)).

| model / rule | group | n | events | progression rate | Wilson 95 % CI |
|---|---|---|---|---|---|
| clinical_3a__tertile_trainfold | low | 51 | 5 | 0.098 | [0.043, 0.210] |
| clinical_3a__tertile_trainfold | moderate | 49 | 16 | 0.327 | [0.212, 0.466] |
| clinical_3a__tertile_trainfold | high | 50 | 29 | 0.580 | [0.442, 0.706] |
| cnv_only__tertile_trainfold | low | 52 | 10 | 0.192 | [0.108, 0.319] |
| cnv_only__tertile_trainfold | moderate | 47 | 17 | 0.362 | [0.240, 0.505] |
| cnv_only__tertile_trainfold | high | 51 | 23 | 0.451 | [0.323, 0.586] |
| image_only__tertile_trainfold | low | 52 | 8 | 0.154 | [0.080, 0.275] |
| image_only__tertile_trainfold | moderate | 47 | 14 | 0.298 | [0.187, 0.440] |
| image_only__tertile_trainfold | high | 51 | 28 | 0.549 | [0.414, 0.677] |
| late_mean__tertile_trainfold | low | 51 | 7 | 0.137 | [0.068, 0.257] |
| late_mean__tertile_trainfold | moderate | 46 | 12 | 0.261 | [0.156, 0.403] |
| late_mean__tertile_trainfold | high | 53 | 31 | 0.585 | [0.451, 0.707] |
| cnv_only__killcoyne_fixed_0.3_0.5 | low | 112 | 30 | 0.268 | [0.195, 0.357] |
| cnv_only__killcoyne_fixed_0.3_0.5 | moderate | 38 | 20 | 0.526 | [0.373, 0.675] |
| cnv_only__killcoyne_fixed_0.3_0.5 | high | 0 | 0 | n/a | n/a |
| late_mean__killcoyne_fixed_0.3_0.5 | low | 54 | 7 | 0.130 | [0.064, 0.244] |
| late_mean__killcoyne_fixed_0.3_0.5 | moderate | 64 | 23 | 0.359 | [0.253, 0.482] |
| late_mean__killcoyne_fixed_0.3_0.5 | high | 32 | 20 | 0.625 | [0.453, 0.771] |

| model / rule | OR high vs low (Haldane) | log-OR SE | log-rank p (3 groups) | Cox HR high vs low [CI] | Cox HR moderate vs low [CI] | KM figure |
|---|---|---|---|---|---|---|
| clinical_3a__tertile_trainfold | 11.6 | 0.533 | 0.09 | [2.733, 1.056, 7.072] | [2.031, 0.738, 5.593] | `results/paper_plan/figs/km/km_clinical_3a_tertile.png` |
| cnv_only__tertile_trainfold | 3.338 | 0.443 | 0.163 | [0.487, 0.228, 1.041] | [0.561, 0.253, 1.248] | `results/paper_plan/figs/km/km_cnv_only_tertile.png` |
| image_only__tertile_trainfold | 6.349 | 0.467 | 0.192 | [2.117, 0.923, 4.854] | [1.692, 0.682, 4.198] | `results/paper_plan/figs/km/km_image_only_tertile.png` |
| late_mean__tertile_trainfold | 8.307 | 0.482 | 0.045 | [1.792, 0.788, 4.075] | [0.808, 0.312, 2.095] | `results/paper_plan/figs/km/km_late_mean_tertile.png` |
| cnv_only__killcoyne_fixed_0.3_0.5 | 2.705 | 2.011 | 0.616 | None | None | `results/paper_plan/figs/km/km_cnv_only_killcoyne.png` |
| late_mean__killcoyne_fixed_0.3_0.5 | 10.387 | 0.532 | 0.239 | [1.776, 0.749, 4.21] | [1.128, 0.481, 2.646] | `results/paper_plan/figs/km/km_late_mean_killcoyne.png` |

Time definition: progressors: earliest release row -> endpoint biopsy (closeout item E); non-progressors: earliest row -> last biopsy (max MonthsBeforeLastBiopsy x 30.44 d), censored. Cross-tab CNV tertile (rows) × late_mean tertile (columns): [[26, 15, 11], [10, 17, 20], [15, 14, 22]]; movers 85 patients with progression rate 0.329 vs stayers 0.338; moved up [46, 0.391] (n, rate), moved down [39, 0.256].

**Method.** `pp_main.py` item 5; lifelines KaplanMeierFitter / multivariate log-rank / CoxPHFitter with moderate and high indicators. **Sources.** `results/paper_plan/main_items.json` · `scripts/paper_plan/pp_main.py` · commit 98ed676 (`item5`); figures `results/paper_plan/figs/km/`. **Caveats.** Time is measured from the earliest release row, which is not a clinical baseline; censoring at the last biopsy uses `MonthsBeforeLastBiopsy`; tertile cut-points differ per fold.

### Item 6. Latent space under fusion
**Question.** Does a learned fusion representation separate progressors better than the unimodal representations?

**Status.** DONE. Late fusion excluded (no shared representation). CNV-only representation = the fold pipeline's 64-d PCA scores (the random forest has no penultimate layer; the PCA is fitted on training folds inside the pipeline).

| representation | dim | linear-probe AUROC [CI] | kNN-10 AUROC [CI] | silhouette (held-out, mean of 5 folds) | Δ probe vs image | Δ probe vs CNV | Δ kNN vs image | Δ kNN vs CNV |
|---|---|---|---|---|---|---|---|---|
| image_only | 256 | 0.784 [0.699, 0.862] | 0.786 [0.697, 0.861] | 0.118 | — | — | — | — |
| cnv_only | 64 | 0.713 [0.617, 0.797] | 0.662 [0.575, 0.746] | 0.085 | — | — | — | — |
| early_fusion | 512 | 0.822 [0.741, 0.893] | 0.793 [0.704, 0.868] | 0.085 | +0.038 [-0.040, +0.123] | +0.110 [0.005, 0.215] | +0.007 [-0.059, +0.070] | +0.131 [0.019, 0.233] |
| intermediate_fusion | 384 | 0.819 [0.743, 0.888] | 0.797 [0.713, 0.871] | 0.092 | +0.034 [-0.033, +0.107] | +0.106 [0.001, 0.220] | +0.011 [-0.036, +0.056] | +0.135 [0.028, 0.240] |
| coattention_fusion | 384 | 0.736 [0.640, 0.827] | 0.786 [0.698, 0.859] | 0.115 | -0.048 [-0.140, +0.045] | +0.023 [-0.098, +0.151] | -0.000 [-0.075, +0.078] | +0.124 [0.012, 0.229] |

n = 150 patients, 50 events in every row. Figures (PCA and UMAP fitted on fold-1 training patients, held-out fold-1 patients shown, coloured by status and by subgroup): `results/paper_plan/figs/latent/image_only_pca_fold1.png`, `results/paper_plan/figs/latent/image_only_umap_fold1.png`, `results/paper_plan/figs/latent/cnv_only_pca_fold1.png`, `results/paper_plan/figs/latent/cnv_only_umap_fold1.png`, `results/paper_plan/figs/latent/early_fusion_pca_fold1.png`, `results/paper_plan/figs/latent/early_fusion_umap_fold1.png`, `results/paper_plan/figs/latent/intermediate_fusion_pca_fold1.png`, `results/paper_plan/figs/latent/intermediate_fusion_umap_fold1.png`, `results/paper_plan/figs/latent/coattention_fusion_pca_fold1.png`, `results/paper_plan/figs/latent/coattention_fusion_umap_fold1.png`.

**Method.** row vectors from each fold model (held-out rows = out-of-sample); patient = mean of rows; probe/kNN/scaler fitted on training-fold patients (C by release inner folds); silhouette on held-out standardised patients; PCA/UMAP fitted on fold-1 training patients, held-out fold-1 patients shown; late_mean excluded (no shared representation). Recomputed model outputs vs release OOF (sanity): {'image_only': {'max_abs_diff_vs_release_oof': 0.0, 'spearman': 1.0}, 'early_fusion': {'max_abs_diff_vs_release_oof': 0.0, 'spearman': 1.0}, 'intermediate_fusion': {'max_abs_diff_vs_release_oof': 0.0, 'spearman': 1.0}, 'coattention_fusion': {'max_abs_diff_vs_release_oof': 0.0, 'spearman': 1.0}, 'cnv_only': {'max_abs_diff_vs_release_oof': 0.021, 'spearman': 0.999}}. **Sources.** `results/paper_plan/latent_item6.json` · `scripts/paper_plan/pp_latent.py` · commit 98ed676. **Caveats.** Training-fold rows' representations come from a model that saw them; only held-out patients are scored. UMAP is a secondary visual with a fixed seed; held-out fold 1 only (projections are not comparable across folds).

### Item 7. Attention patches under fusion
**Question.** Do the tiles the model attends to change under fusion?

**Status.** DONE. Models with an image attention module: intermediate (own gated attention) and co-attention (CNV-conditioned); early fusion has none (mean pooling).

| fusion model | rows | n rows | Spearman vs image-only, median [IQR] | Jaccard top-5 % (13 tiles), median | Jaccard top-50, median | entropy image-only, median | entropy fusion, median |
|---|---|---|---|---|---|---|---|
| intermediate_fusion | overall | 707 | 0.867 [0.722, 0.934] | 0.444 | 0.587 | 5.326 | 5.286 |
| intermediate_fusion | progressor_rows | 107 | 0.884 [0.688, 0.942] | 0.444 | 0.587 | 5.293 | 5.299 |
| intermediate_fusion | nonprogressor_rows | 600 | 0.865 [0.727, 0.932] | 0.444 | 0.587 | 5.333 | 5.284 |
| intermediate_fusion | image_only_correct_patient | 306 | 0.867 [0.735, 0.938] | 0.444 | 0.587 | 5.348 | 5.268 |
| intermediate_fusion | image_only_incorrect_patient | 401 | 0.869 [0.715, 0.932] | 0.444 | 0.587 | 5.304 | 5.308 |
| coattention_fusion | overall | 707 | 0.347 [-0.048, +0.629] | 0.040 | 0.190 | 5.326 | 5.512 |
| coattention_fusion | progressor_rows | 107 | 0.352 [-0.163, +0.641] | 0.040 | 0.176 | 5.293 | 5.507 |
| coattention_fusion | nonprogressor_rows | 600 | 0.343 [-0.022, +0.616] | 0.040 | 0.198 | 5.333 | 5.513 |
| coattention_fusion | image_only_correct_patient | 306 | 0.319 [-0.077, +0.615] | 0.040 | 0.176 | 5.348 | 5.508 |
| coattention_fusion | image_only_incorrect_patient | 401 | 0.386 [-0.018, +0.642] | 0.040 | 0.205 | 5.304 | 5.513 |

Max entropy ln(256) = 5.545. Correct/incorrect = image_only patient prediction at the primary operating point. Montages of the top-16 tiles per model for 20 pre-drawn rows: `M01–M20.png`, 20 files. Deviation from the pre-specified path: they are patient tissue images, so they stay on the cluster at `feasibility/paper_plan/figs/attention/` (moved from `results/paper_plan/figs/attention/`) and are not committed to the public repository; manifest with outcomes `feasibility/paper_plan/montage_manifest_SECRET.csv` (cluster).

**Method.** Held-out-fold attention over the 256 release tiles per row (`pp_latent.py`), summarised in `pp_main.py`. **Sources.** `results/paper_plan/attention_item7_rows.csv` · `scripts/paper_plan/pp_latent.py` · commit 98ed676; `main_items.json` (`item7`). **Caveats.** Attention weights are not importance; 256 tiles per slide are the release's fixed sample.

### Item 8. Does CNV prediction change?
**Question.** 8a: how do patient rankings move from CNV-only to late fusion; 8b: which CNV features drive each model?

**Status.** DONE.

**8a (patient ranking, n 150, events 50).** Spearman(cnv_only, late_mean) = 0.387; median |percentile change| 20.333 points; progressors moving up > 20 points 16, down 10; non-progressors up 23, down 28. Categorical NRI (late vs CNV, item-5 tertile groups) 0.17 [-0.082, 0.418] (event NRI 0.16, non-event NRI 0.01).

**8b (permutation importance, ΔAUROC when one arm-level feature is permuted on held-out rows; top 10 per model).**

| rank | cnv_only | early_fusion | intermediate_fusion | coattention_fusion |
|---|---|---|---|---|
| 1 | chr17p (+0.027) | chr21q (+0.008) | chr1p (+0.006) | chr20p (+0.005) |
| 2 | chr5q (+0.022) | chr1p (+0.006) | chr17q (+0.006) | cx (+0.005) |
| 3 | chr5p (+0.022) | chr17p (+0.005) | chr21q (+0.005) | chr17p (+0.005) |
| 4 | chr11q (+0.021) | chr12q (+0.004) | chr7p (+0.003) | chr21q (+0.004) |
| 5 | chr16p (+0.017) | cx (+0.003) | chr16p (+0.002) | chr8p (+0.004) |
| 6 | chr2q (+0.016) | chr13q (+0.003) | chr6p (+0.002) | chr7p (+0.003) |
| 7 | chr14p (+0.016) | chr5q (+0.002) | chr17p (+0.002) | chr18q (+0.002) |
| 8 | chr21q (+0.015) | chr10p (+0.002) | chr20q (+0.002) | chr9q (+0.002) |
| 9 | chr21p (+0.015) | chr12p (+0.001) | cx (+0.001) | chr22q (+0.002) |
| 10 | chr18q (+0.015) | chr5p (+0.001) | chr3q (+0.001) | chr2q (+0.002) |

Spearman of the importance vectors vs cnv_only: early 0.241, intermediate 0.176, co-attention 0.122. Method: held-out rows per fold; one of 45 arm-level features (39 arms + cx) permuted across the held-out rows, 50 repeats, RandomState(0); delta = baseline patient-level AUROC (max over rows) minus permuted, averaged over the 5 folds; 5-Mb features held fixed; fusion models: image parts precomputed, CNV branch re-run. late_mean has no CNV branch of its own (its CNV component is cnv_only).

**Sources.** `results/paper_plan/main_items.json` · `scripts/paper_plan/pp_main.py` · commit 98ed676 (`item8a`); `results/paper_plan/perm_importance_item8b.json` · `scripts/paper_plan/pp_latent.py` · commit 98ed676. **Caveats.** ΔAUROC importances on ~140 held-out rows per fold are noisy; a feature can matter through the 5-Mb windows, which were held fixed.

### Item 9. Do false positives show risk of progression?
**Question.** At the primary operating point, do non-progressors flagged positive show later disease?

**Status.** DONE (later-disease sources exist; coverage stated).

Sources checked: Barrett's-DB pathology reports of the linked participant after the last release row (149 of 150 patients linked; report dates ['1995-07-28', '2026-08-04']); release rows excluded as at-event / post-event / endpoint-not-evaluable; `hgd_pathology_table` (798 rows, ['1998-12-18', '2020-04-07']); slide_matching rows dated after the last release row. Later LGD+ = any of these with grade LGD or worse; later HGD+ = HGD/IMC or an hgd_table entry.

| model | FP | TN | later LGD+ FP (k/n, rate) | later LGD+ TN | Fisher p | later HGD+ FP | later HGD+ TN | Fisher p | DB follow-up d, median FP / TN (MW p) | any DB report after, FP / TN | baseline grade mean FP / TN (p) | cx median FP / TN (p) | p53 aberrant / with IHC, FP ; TN | KM |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| late_mean | 40 | 60 | [11, 40, 0.275] | [8, 60, 0.133] | 0.117 | [11, 40, 0.275] | [4, 60, 0.067] | 0.008 | [2447.0, 2811.0, 0.986] | [39, 60] | [0.325, 0.067, 0.008] | [6.5, 2.5, 0.687] | [[1, 19], [0, 18]] | results/paper_plan/figs/km/later_lgd_FP_TN_late_mean.png |
| image_only | 50 | 50 | [11, 50, 0.22] | [8, 50, 0.16] | 0.611 | [11, 50, 0.22] | [4, 50, 0.08] | 0.091 | [2506.5, 2943.5, 0.679] | [49, 50] | [0.3, 0.04, 0.003] | [2.0, 6.0, 0.766] | [[1, 21], [0, 16]] | results/paper_plan/figs/km/later_lgd_FP_TN_image_only.png |
| cnv_only | 55 | 45 | [16, 55, 0.291] | [3, 45, 0.067] | 0.005 | [13, 55, 0.236] | [2, 45, 0.044] | 0.01 | [2587.0, 2079.0, 0.901] | [54, 45] | [0.2, 0.133, 0.407] | [14.0, 0.0, '<0.001'] | [[1, 30], [0, 7]] | results/paper_plan/figs/km/later_lgd_FP_TN_cnv_only.png |
| clinical_3a | 38 | 62 | [12, 38, 0.316] | [7, 62, 0.113] | 0.018 | [10, 38, 0.263] | [5, 62, 0.081] | 0.02 | [2549.0, 2715.5, 0.587] | [37, 62] | [0.395, 0.032, '<0.001'] | [14.0, 0.5, 0.028] | [[1, 17], [0, 20]] | results/paper_plan/figs/km/later_lgd_FP_TN_clinical_3a.png |
| v4_exploratory | 26 | 74 | [9, 26, 0.346] | [10, 74, 0.135] | 0.038 | [9, 26, 0.346] | [6, 74, 0.081] | 0.003 | [2447.0, 2811.0, 0.36] | [25, 74] | [0.269, 0.135, 0.195] | [17.0, 0.5, 0.014] | [[1, 14], [0, 23]] | results/paper_plan/figs/km/later_lgd_FP_TN_v4_exploratory.png |

**Sources.** `results/paper_plan/main_items.json` · `scripts/paper_plan/pp_main.py` · commit 98ed676 (`item9`); patient table `feasibility/paper_plan/later_disease_patient.csv` (cluster). **Caveats.** DB linkage covers most but not all patients; later grades are DB confirmed codes (not re-read); release-excluded rows are by construction absent for non-progressors except non-evaluable ones; no cancer-registry linkage exists.

### Item 10. What is missing from false negatives?
**Question.** At the primary operating point, how do missed progressors differ from detected ones?

**Status.** DONE (tables; review pack built on the cluster, review itself out of scope).

**late_mean** (FN 11, TP 39)

| variable | FN median / counts | TP median / counts | test | p |
|---|---|---|---|---|
| first_to_event | 898.0 (n 11) | 1108.0 (n 39) | Mann-Whitney | 0.337 |
| n_rows | 2.0 (n 11) | 4.0 (n 39) | Mann-Whitney | 0.07 |
| baseline_grade | 0.0 (n 11) | 0.0 (n 39) | Mann-Whitney | 0.198 |
| max_sofar | 2.0 (n 11) | 1.0 (n 39) | Mann-Whitney | 0.431 |
| cx | 24.0 (n 11) | 52.0 (n 39) | Mann-Whitney | 0.072 |
| noise | 0.074 (n 11) | 0.066 (n 39) | Mann-Whitney | 0.019 |
| segments | 179.5 (n 11) | 229.7 (n 39) | Mann-Whitney | 0.153 |
| frac_alt | 0.029 (n 11) | 0.042 (n 39) | Mann-Whitney | 0.242 |
| reads | 18533790.0 (n 11) | 23077752.375 (n 28) | Mann-Whitney | 0.002 |
| tiles_kept | 3194.143 (n 11) | 991.0 (n 39) | Mann-Whitney | 0.002 |
| tissue_frac | 0.111 (n 11) | 0.143 (n 39) | Mann-Whitney | 0.019 |
| endpoint_label | {'FN': {'2.0': 6, '3.0': 2, '4.0': 3}, 'TP': {'2.0': 8, '3.0': 24, '4.0': 7}} |  | Fisher (2×2 only) | None |
| scanner | {'FN': {'C13210': 0, 'C13239-01': 11}, 'TP': {'C13210': 12, 'C13239-01': 27}} |  | Fisher (2×2 only) | 0.046 |
| subgroup | {'FN': {'also_in_ERIN': 4, 'never_in_ERIN': 7}, 'TP': {'also_in_ERIN': 10, 'never_in_ERIN': 29}} |  | Fisher (2×2 only) | 0.476 |
| p53 | {'FN': {'aberrant': 2, 'missing': 2, 'normal': 7}, 'TP': {'aberrant': 13, 'missing': 10, 'normal': 16}} |  | Fisher (2×2 only) | None |

**image_only** (FN 14, TP 36)

| variable | FN median / counts | TP median / counts | test | p |
|---|---|---|---|---|
| first_to_event | 1020.5 (n 14) | 1096.0 (n 36) | Mann-Whitney | 0.754 |
| n_rows | 2.0 (n 14) | 4.0 (n 36) | Mann-Whitney | 0.034 |
| baseline_grade | 0.0 (n 14) | 0.0 (n 36) | Mann-Whitney | 0.597 |
| max_sofar | 2.0 (n 14) | 1.0 (n 36) | Mann-Whitney | 0.748 |
| cx | 27.5 (n 14) | 54.0 (n 36) | Mann-Whitney | 0.018 |
| noise | 0.075 (n 14) | 0.065 (n 36) | Mann-Whitney | 0.004 |
| segments | 175.5 (n 14) | 247.438 (n 36) | Mann-Whitney | 0.029 |
| frac_alt | 0.028 (n 14) | 0.043 (n 36) | Mann-Whitney | 0.048 |
| reads | 18533790.0 (n 13) | 23077752.375 (n 26) | Mann-Whitney | 0.003 |
| tiles_kept | 2825.571 (n 14) | 960.2 (n 36) | Mann-Whitney | <0.001 |
| tissue_frac | 0.127 (n 14) | 0.145 (n 36) | Mann-Whitney | 0.041 |
| endpoint_label | {'FN': {'2.0': 6, '3.0': 3, '4.0': 5}, 'TP': {'2.0': 8, '3.0': 23, '4.0': 5}} |  | Fisher (2×2 only) | None |
| scanner | {'FN': {'C13210': 1, 'C13239-01': 13}, 'TP': {'C13210': 11, 'C13239-01': 25}} |  | Fisher (2×2 only) | 0.14 |
| subgroup | {'FN': {'also_in_ERIN': 4, 'never_in_ERIN': 10}, 'TP': {'also_in_ERIN': 10, 'never_in_ERIN': 26}} |  | Fisher (2×2 only) | 1.0 |
| p53 | {'FN': {'aberrant': 2, 'missing': 3, 'normal': 9}, 'TP': {'aberrant': 13, 'missing': 9, 'normal': 14}} |  | Fisher (2×2 only) | None |

**cnv_only** (FN 10, TP 40)

| variable | FN median / counts | TP median / counts | test | p |
|---|---|---|---|---|
| first_to_event | 1027.5 (n 10) | 1102.0 (n 40) | Mann-Whitney | 0.497 |
| n_rows | 2.5 (n 10) | 3.0 (n 40) | Mann-Whitney | 0.411 |
| baseline_grade | 0.0 (n 10) | 0.0 (n 40) | Mann-Whitney | 0.602 |
| max_sofar | 1.5 (n 10) | 1.0 (n 40) | Mann-Whitney | 0.679 |
| cx | 0.0 (n 10) | 51.0 (n 40) | Mann-Whitney | 0.002 |
| noise | 0.065 (n 10) | 0.071 (n 40) | Mann-Whitney | 0.221 |
| segments | 206.625 (n 10) | 214.262 (n 40) | Mann-Whitney | 0.913 |
| frac_alt | 0.028 (n 10) | 0.043 (n 40) | Mann-Whitney | 0.083 |
| reads | 21471850.0 (n 6) | 21573962.667 (n 33) | Mann-Whitney | 0.635 |
| tiles_kept | 1329.75 (n 10) | 1089.75 (n 40) | Mann-Whitney | 0.707 |
| tissue_frac | 0.166 (n 10) | 0.134 (n 40) | Mann-Whitney | 0.186 |
| endpoint_label | {'FN': {'2.0': 3, '3.0': 6, '4.0': 1}, 'TP': {'2.0': 11, '3.0': 20, '4.0': 9}} |  | Fisher (2×2 only) | None |
| scanner | {'FN': {'C13210': 2, 'C13239-01': 8}, 'TP': {'C13210': 10, 'C13239-01': 30}} |  | Fisher (2×2 only) | 1.0 |
| subgroup | {'FN': {'also_in_ERIN': 5, 'never_in_ERIN': 5}, 'TP': {'also_in_ERIN': 9, 'never_in_ERIN': 31}} |  | Fisher (2×2 only) | 0.118 |
| p53 | {'FN': {'aberrant': 2, 'missing': 3, 'normal': 5}, 'TP': {'aberrant': 13, 'missing': 9, 'normal': 18}} |  | Fisher (2×2 only) | None |

**clinical_3a** (FN 10, TP 40)

| variable | FN median / counts | TP median / counts | test | p |
|---|---|---|---|---|
| first_to_event | 1097.0 (n 10) | 1096.0 (n 40) | Mann-Whitney | 0.762 |
| n_rows | 3.5 (n 10) | 3.0 (n 40) | Mann-Whitney | 0.971 |
| baseline_grade | 0.0 (n 10) | 0.0 (n 40) | Mann-Whitney | 0.284 |
| max_sofar | 0.0 (n 10) | 2.0 (n 40) | Mann-Whitney | 0.004 |
| cx | 63.5 (n 10) | 44.0 (n 40) | Mann-Whitney | 0.415 |
| noise | 0.065 (n 10) | 0.07 (n 40) | Mann-Whitney | 0.536 |
| segments | 211.5 (n 10) | 213.929 (n 40) | Mann-Whitney | 0.913 |
| frac_alt | 0.054 (n 10) | 0.041 (n 40) | Mann-Whitney | 0.431 |
| reads | 21607096.5 (n 7) | 21339403.119 (n 32) | Mann-Whitney | 0.9 |
| tiles_kept | 970.8 (n 10) | 1139.833 (n 40) | Mann-Whitney | 0.203 |
| tissue_frac | 0.15 (n 10) | 0.134 (n 40) | Mann-Whitney | 0.52 |
| endpoint_label | {'FN': {'2.0': 1, '3.0': 8, '4.0': 1}, 'TP': {'2.0': 13, '3.0': 18, '4.0': 9}} |  | Fisher (2×2 only) | None |
| scanner | {'FN': {'C13210': 2, 'C13239-01': 8}, 'TP': {'C13210': 10, 'C13239-01': 30}} |  | Fisher (2×2 only) | 1.0 |
| subgroup | {'FN': {'also_in_ERIN': 1, 'never_in_ERIN': 9}, 'TP': {'also_in_ERIN': 13, 'never_in_ERIN': 27}} |  | Fisher (2×2 only) | 0.246 |
| p53 | {'FN': {'aberrant': 2, 'missing': 3, 'normal': 5}, 'TP': {'aberrant': 13, 'missing': 9, 'normal': 18}} |  | Fisher (2×2 only) | None |

**v4_exploratory** (FN 11, TP 39)

| variable | FN median / counts | TP median / counts | test | p |
|---|---|---|---|---|
| first_to_event | 898.0 (n 11) | 1096.0 (n 39) | Mann-Whitney | 0.623 |
| n_rows | 2.0 (n 11) | 4.0 (n 39) | Mann-Whitney | 0.297 |
| baseline_grade | 0.0 (n 11) | 0.0 (n 39) | Mann-Whitney | 0.614 |
| max_sofar | 2.0 (n 11) | 1.0 (n 39) | Mann-Whitney | 0.431 |
| cx | 5.0 (n 11) | 53.0 (n 39) | Mann-Whitney | <0.001 |
| noise | 0.071 (n 11) | 0.069 (n 39) | Mann-Whitney | 0.482 |
| segments | 219.667 (n 11) | 208.857 (n 39) | Mann-Whitney | 1.0 |
| frac_alt | 0.029 (n 11) | 0.043 (n 39) | Mann-Whitney | 0.146 |
| reads | 20800968.0 (n 9) | 21772675.625 (n 30) | Mann-Whitney | 0.494 |
| tiles_kept | 1413.667 (n 11) | 1065.5 (n 39) | Mann-Whitney | 0.558 |
| tissue_frac | 0.13 (n 11) | 0.136 (n 39) | Mann-Whitney | 0.888 |
| endpoint_label | {'FN': {'2.0': 5, '3.0': 3, '4.0': 3}, 'TP': {'2.0': 9, '3.0': 23, '4.0': 7}} |  | Fisher (2×2 only) | None |
| scanner | {'FN': {'C13210': 2, 'C13239-01': 9}, 'TP': {'C13210': 10, 'C13239-01': 29}} |  | Fisher (2×2 only) | 1.0 |
| subgroup | {'FN': {'also_in_ERIN': 4, 'never_in_ERIN': 7}, 'TP': {'also_in_ERIN': 10, 'never_in_ERIN': 29}} |  | Fisher (2×2 only) | 0.476 |
| p53 | {'FN': {'aberrant': 0, 'missing': 3, 'normal': 8}, 'TP': {'aberrant': 15, 'missing': 9, 'normal': 15}} |  | Fisher (2×2 only) | None |

no blur/focus QC exists for SWG slides; tiles_kept and tissue fraction (kept/grid) from the 0.5 um h5 attributes are the available slide-level metrics. Review pack: 31 FN slides (all rows of the 11 late_mean FN patients) + 31 TP + 31 TN slides, shuffled, opaque names, thumbnails in `feasibility/paper_plan/review_pack/` (cluster); manifest feasibility/paper_plan/review_pack_manifest_SECRET.csv (cluster only).

**Sources.** `results/paper_plan/main_items.json` · `scripts/paper_plan/pp_main.py` · commit 98ed676 (`item10`); QC and slide tables from the closeout (`feasibility/closeout/`, commit 602a40e). **Caveats.** Small FN groups; endpoint-type and scanner tables have more than two levels (no Fisher p); read counts exist only for discovery-sheet profiles.

## 5. Filled whiteboard table (SWG; no corrected release exists)

|  | SWG progressor cohort (n 150, 50 progressors): AUROC [CI] · AUPRC [CI] | ACE-B external validation |
|---|---|---|
| Clinical only (3a) | 0.765 [0.684, 0.844] · 0.547 [0.437, 0.711] | NOT AVAILABLE |
| CNV | 0.663 [0.569, 0.754] · 0.538 [0.411, 0.671] | NOT AVAILABLE |
| WSI | 0.731 [0.640, 0.814] · 0.557 [0.426, 0.717] | NOT AVAILABLE |
| Early fusion | 0.738 [0.646, 0.818] · 0.590 [0.453, 0.733] | NOT AVAILABLE |
| Intermediate fusion | 0.741 [0.653, 0.818] · 0.567 [0.435, 0.714] | NOT AVAILABLE |
| Late fusion (mean) | 0.774 [0.687, 0.849] · 0.630 [0.490, 0.772] | NOT AVAILABLE |
| Co-attention fusion (extra) | 0.739 [0.652, 0.821] · 0.548 [0.428, 0.703] | NOT AVAILABLE |
| Late stack-logit fusion (extra) | 0.737 [0.648, 0.814] · 0.530 [0.412, 0.684] | NOT AVAILABLE |

Source: `results/paper_plan/main_items.json` (`item4_tables.all_150`), commit 98ed676.

## 6. Discrepancies found
1. Pipeline document `killcoyne_protocol_comparison.md` says 69/150 patients overlap the Killcoyne discovery cohort; every definition computed here gives 82 (item 0).
2. Our CNV-only arm scores the 25 discovery-sheet overlap patients at 0.253 while Killcoyne's published per-sample predictions on the same profiles give 0.792 for our endpoint: the CNV data are not corrupted; the release's CNV model is what fails on these patients (item 0).
3. Release grade LGD contradicted by both lab tables in 42 rows, and 28 rows where the master and DB-scrape next-biopsy labels disagree; changes patient status for ≤ 6 patients under the alternative source (item 0). Not a chain error under the pre-specified rule.
4. Recomputing `cnv_only` probabilities from the saved pipelines reproduces the release OOF only to 0.021 max abs difference (Spearman 0.999); the four torch families reproduce exactly. Feeding float32 instead of the release's float64 input shifts RF probabilities by up to 0.14 (fixed in commit 5bf5419).
5. Audit v1 flagged 48 overlap rows for patient mismatch and 35 for accession mismatch; both were parser/mapping artefacts corrected in v2 (item 0).

## 7. Not done
- ACE-B column (no data; nothing run).
- Killcoyne-style thresholds from release metadata (none documented; paper's fixed classes used instead).
- Sequencing depth in ×, slide blur/focus QC, cancer-registry linkage: not available (closeout item C; item 10 note).
- The pathologist review of the pack (out of scope by instruction).
- A corrected release (not triggered: no confirmed errors).

## 8. Pre-specification text as committed at `db236a0` (verbatim)

> # BE paper plan: answers (SWG progressor cohort)
>
> **Status of this file: PRE-SPECIFICATION VERSION**, committed before any analysis in it was run (ground rule 5). Results
> are appended in later commits; specification text below is never edited after this commit. If a specification has to
> change after seeing data, the original stays and the change is added beside it with both results.
>
> ## 1. Header (to be completed at the results commit)
> - Date: 25 September 2026. Commit at start: `1d27002`. Pre-specification commit: the commit that adds this text.
> - Inputs: frozen release `chapter1_lgd2_final_pre_event_20260713_final` (707 rows, 150 patients, 50 progressor patients, 107 positive rows); `docs/closeout_for_review.md` and `results/closeout/*` (commit `602a40e`); SWG source tables on the cluster (`SWGCohort/`), the Barrett's-DB export, the Killcoyne 2020 paper PDF (`phd/s41591-020-1033-y.pdf`) and its supplementary tables (`phd/killcoyne_data_from_paper/41591_2020_1033_MOESM*.xlsx`).
> - Planned scripts (`scripts/paper_plan/`): `pp_audit.py` (item 0), `pp_main.py` (items 1–5, 8a, 9, 10 tables), `pp_latent.py` (items 6, 7 attention arrays, 8b; GPU), `pp_montage.py` (item 7 montages), `pp_review_pack.py` (item 10 pack), `pp_render.py` (writes this file from the JSONs).
> - Planned outputs: `results/paper_plan/*.json`, `results/paper_plan/figs/**`. Row-level and identifiable material (per-patient audit table, montages, review pack, embeddings) stays on the cluster under `feasibility/paper_plan/` and is never committed.
>
> ## Conventions (every item)
> As in the closeout: patient level; patient score = max over the patient's strict pre-event rows; rank AUROC and AUPRC (average precision) to 3 decimals; 95 % CI = percentile bootstrap over patients, 2,000 resamples, `numpy.random.RandomState(0)`, one-class resamples redrawn; permutation tests = 2,000 permutations of patient labels, `RandomState(0)`, p = (1 + #null ≥ obs)/2,001; paired differences use the same resamples for both arms. Every table carries n patients and n events. Arm scores are the release out-of-fold probabilities (`training_final_nested_cv_v1/<family>/fold*/outer_test_predictions.csv`, outer folds `fold_id_rep01`); late_mean is the release's plain mean of the image_only and cnv_only probabilities. Fold honesty: anything fitted for evaluation (thresholds, quantiles, scalers, probes, projections, logistic combinations) is fitted on the four training outer folds and applied to the held-out fold; inner CV for hyper-parameters uses the release's `inner_fold_assignments.csv` (patient-keyed).
>
> ## Pre-specifications
>
> ### Item 0. CNV audit of the overlap subgroup (blocking)
> - Patients: the 54 `also_in_ERIN` patients (crosswalk recomputed as in the closeout, `feasibility/closeout/erin_swg_pairs.csv`) and 25 `never_in_ERIN` patients drawn with `RandomState(0)` from the sorted list of the 96.
> - Chain per release row: `cnv_id` → sequencing sheet entry (discovery 777-sheet `combined_name` or validation 268-sheet `sample_id`: PatientID, Path ID/Block accession, Endoscopy Year, Pathology, Status) → release accession `BiopsyID_real` and `Date` (`DateSource`, `BiopsyIDMatchType`) → slide file (`ImageAbsPath` basename; `slide_matching.csv`: PatientID/AlternateID, PathCaseID, EndoscopyDate, Block, Pathology) → row grade `Label` (`GradeSource`) → `NextBiopsyLabel` (`NextBiopsyLabel_source`, `_orig`, `_scrape`) → DB report (accession match to `swg_matched_reports_v2` / `pathology_text_normalised_full`: participant, date, `highestgradedysconf`).
> - Flags (one per row, each source pair): patient mismatch (sheet PatientID or slide_matching AlternateID ≠ release patient_id, after mapping the sheet's numeric PatientID through `slide_matching.PatientID` → `AlternateID`); accession mismatch (sheet Path ID/Block stem ≠ release accession stem ≠ slide_matching PathCaseID stem ≠ DB specimennumber stem); date mismatch (sheet Endoscopy Year ≠ year of release Date; slide_matching EndoscopyDate ≠ release Date by > 366 d when the slide_matching date is not a 1 January placeholder); CNV-from-different-endoscopy (sheet accession stem ≠ slide accession stem for the same row); grade disagreement (sheet Pathology vs release grade vs slide_matching Pathology vs DB confirmed code, two-tier NDBE/IND vs LGD+); next-label disagreement (`NextBiopsyLabel_orig` vs `_scrape` where both present, and vs DB code of the next report).
> - Summary table: counts of each flag type per subgroup (overlap 54 vs comparator 25), rows and patients; the per-patient table stays on the cluster (`feasibility/paper_plan/audit_rows.csv`).
> - Killcoyne per-sample predictions: `41591_2020_1033_MOESM4_ESM.xlsx`, sheet "Supporting data for Figure 2a" (Samplename, Probability, Risk class; 773 discovery samples) and `MOESM7` Ext Data Fig 1a-b (Samplename, Status, Complexity). Join on `cnv_id` = Samplename. Report: n matched rows and patients; Killcoyne Status vs our patient label (agreement table); Spearman of Killcoyne probability vs our cnv_only OOF on matched rows; patient-level AUROC of Killcoyne max probability for our endpoint on matched patients, by subgroup.
> - Count reconciliation: "69/150" (pipeline doc, undated method) vs "82/150" (closeout, modal sheet per patient). Recompute: patients with ≥ 1 row whose cnv_id is in the discovery sheet; patients with ≥ 1 row whose Samplename appears in the Killcoyne per-sample table; patients all of whose rows are discovery. State which definition each earlier count matches.
> - Decision rule (pre-specified): a row is a **confirmed error** only if two independent sources (independent = not derived from one another: the sequencing sheet, slide_matching, the DB report, and the Killcoyne supplementary table count as independent of the release; `NextBiopsyLabel_scrape` and the DB code are the same source) agree on a patient, accession or date that contradicts the release. If ≥ 1 confirmed error: build a corrected release as a new versioned directory (frozen one untouched), retrain the affected arms with `scripts/24_run_lgd2_final_outer_fold.py` unchanged, and run every item on both releases side by side. If none: state so and run on the frozen release only.
>
> ### Item 1. Killcoyne 2020 comparison
> - Our column from the release metadata and code as in closeout item L. Their column only from the PDF text (`pdftotext` of `s41591-020-1033-y.pdf`) and the supplementary xlsx, each cell with page/figure/sheet. Overlap from item 0. CNV-only AUROC (patient level, CI) for patients with ≥ 1 Killcoyne-discovery row vs the rest.
>
> ### Item 2. Histology vs CNV
> - image_only vs cnv_only: AUROC, AUPRC, paired difference with CI and paired permutation p (labels permuted, difference of AUROCs); on all 150, the 96, the 54, and the corrected release if any.
>
> ### Item 3. Clinical-only arm (new)
> - 3a (150 patients): features = row grade code (0/1/2), `MaxPathologySoFar`, `LGDStreakSoFar`, `BiopsyIndex`, `DaysSincePreviousBiopsy` (0 for first row), row year. Coverage is listed; only covariates present for ≥ 90 % of patients enter. Model: L2 logistic regression, C ∈ {0.01, 0.1, 1, 10} chosen by inner CV (release `inner_fold_assignments.csv` of the same outer fold, patient-keyed; criterion = patient-level AUROC on inner validation, max over rows), standardisation fitted on the outer training rows; predictions on the held-out outer fold; patient = max over rows.
> - 3b (patients in `Demographics_full.csv`): 3a features + age at the row (row year − birth year), sex, Prague C, Prague M, smoking (Y/N). Complete cases only; n stated. Same model and folds (release folds restricted to the subset). image, CNV, late_mean, early, intermediate, co-attention re-evaluated on the same patients.
>
> ### Item 4. Main results table
> - Rows: Clinical 3a, CNV (`cnv_only`), WSI (`image_only`), Early (`early_fusion`), Intermediate (`intermediate_fusion`), Late (`late_mean`), plus Co-attention (`coattention_fusion`) and Late-stack (`late_stack_logit`) labelled extra. Columns: AUROC [CI], AUPRC [CI], n, events. Difference block: each fusion arm vs WSI and vs CNV, CI, naive permutation p, selection-adjusted p = P(max over the five fusion arms of the permuted difference ≥ observed). Repeated on the 96 and the 54. Exploratory block: closeout v4 (leak-free grade head fusion) read from `results/closeout/closeout_main.json` with its selection-adjusted p and the failed gate. ACE-B column NOT AVAILABLE. Architecture, inputs, code path and model directory per arm from the release configs.
>
> ### Primary model and operating point (items 5–10)
> - Primary = `late_mean`; comparators `image_only`, `cnv_only`, clinical 3a; exploratory = closeout v4. Operating point: for each outer fold, the threshold on patient-level scores of the four training folds giving sensitivity ≥ 0.80 (largest threshold meeting it), applied to the held-out fold; realised sensitivity/specificity per fold and pooled.
>
> ### Item 5. Risk groups
> - Thresholds = 1/3 and 2/3 quantiles of training-fold patient scores per outer fold. Alternative: Killcoyne classes low Pr ≤ 0.3, moderate 0.3–0.5, high ≥ 0.5 (paper, results paragraph on risk classes) applied to the arm's probability (reported for cnv_only and late_mean, whose scores are probabilities; not for 3a beyond its logistic probability). Per model: n, events, progression rate per group with Wilson 95 % CI, OR high vs low (Haldane correction if a zero cell). Time to endpoint biopsy from the earliest release row (closeout item E definition); non-progressors censored at earliest row + max `MonthsBeforeLastBiopsy`; Kaplan–Meier per group, log-rank p, Cox HR high vs low and moderate vs low (lifelines). Cross-tab CNV group × late_mean group with progression rates of movers.
>
> ### Item 6. Latent space
> - Representations (row level, from the fold model that did not see the row; training-fold rows from the same fold model): image_only = attention-pooled 256-d embedding before the classifier; cnv_only = 64-d PCA scores of the fold pipeline (RF is not linear and has no penultimate layer; stated); early = 512-d first hidden layer; intermediate = 384-d concat of attended image (256) and CNV branch (128); co-attention = 384-d concat of CNV-attended image (256) and CNV embedding (128). Patient representation = mean of the patient's row vectors. Per outer fold: linear probe (L2 logistic, C by inner CV on training patients), kNN k = 10 (fitted on training patients, distance-weighted no; uniform), evaluated on held-out patients; pooled held-out AUROC with patient bootstrap; silhouette by progressor status on held-out patients (standardised with training-fold mean/sd). Paired fused − unimodal differences. PCA (2-d) and UMAP (n_neighbors 15, min_dist 0.1, random_state 0) fitted on training patients of fold 1, held-out fold-1 patients plotted, coloured by status and by subgroup; also a pooled plot of all held-out patients using each fold's own projection is NOT made (projections are not comparable across folds). Late fusion excluded (no shared space).
>
> ### Item 7. Attention
> - Tile attention (256 tiles per row) from image_only and intermediate (image attention module) and co-attention (CNV-conditioned attention) fold models on held-out rows; early fusion has no attention (mean pooling). Per row: Spearman(image_only, fusion), Jaccard of top-5 % (13 tiles) and top-50 tiles, Shannon entropy per model. Summary per model overall, by progressor status and by correct/incorrect prediction of the respective model at the primary operating point. Montages: 20 patients (10 progressors, 10 non-progressors, `RandomState(0)` from sorted ids), the row with the highest image_only score per patient, top-16 tiles per model read from the .ndpi at the release tile level (level-2 coords in the npz); files named by an opaque index; manifest separate.
>
> ### Item 8. Does CNV prediction change?
> - 8a: Spearman(cnv_only, late_mean) patient scores; percentile rank change per patient; counts of progressors/non-progressors moving > 20 percentile points up/down; categorical NRI using item-5 groups (late vs CNV) with patient bootstrap CI.
> - 8b: permutation importance on held-out rows, ΔAUROC (patient level) when one CNV feature is permuted across held-out rows, 50 repeats, `RandomState(0)`; features = the 39 arm columns + `cx` (5-Mb features held fixed); models = cnv_only pipeline and the CNV input of early, intermediate, co-attention. Top 10 per model; Spearman of importance vectors between cnv_only and each fusion model.
>
> ### Item 9. False positives
> - Non-progressors at the primary operating point → FP/TN per model. Later disease: (a) DB pathology reports of the patient's participant after the last release row (`highestgradedysconf` mapped to grade; coverage to 2026-08); (b) release rows excluded as `post_event`/`endpoint_not_evaluable`/`at_event` for the patient (should be none for non-progressors; reported); (c) `hgd_pathology_table` (participant, grading_sequence, date); (d) slide_matching rows after the last release row (Pathology). Sources listed with coverage. FP vs TN: n; follow-up after last release row; any later LGD+/HGD+/cancer (Fisher); time to first later dysplasia (KM, log-rank) where events ≥ 5; baseline grade; cx; p53 IHC.
>
> ### Item 10. False negatives
> - Progressors at the primary operating point → FN/TP per model. FN vs TP: interval first row → endpoint biopsy; endpoint type (next label 2/3/4+); n rows; baseline and max grade so far; cx, MAPD noise, segments, fraction altered, reads (closeout QC tables); tiles kept and tissue fraction (0.5 µm h5 attrs `kept_tiles`/`grid_tiles`); scanner model; subgroup; p53 IHC. Mann-Whitney / Fisher. Review pack: thumbnails (2,048 px, level chosen by openslide) of every FN slide (late_mean) plus equal numbers of TP and TN slides (`RandomState(0)`), shuffled, opaque names; manifest separate on the cluster.
>
> (Results follow in the results commit.)
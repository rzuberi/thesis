# Closeout for review: SWG fusion and the ERIN-transfer result

## 1. Header
- Date: 25 September 2026.
- Commit at start: `a23b483`. Pre-specification commit (this file's specification text, the ACE-B plan and all closeout scripts, before any run): `0aaa824`. Script fixes after failed first runs (markdown writer, CNV path, one labelling correction stated in item E): `1148318`, `4af24d5`. Results commit (all result files and scripts): `602a40e`. Commit at end = the commit that adds this rendered text (the next commit after `602a40e`; see `git log -- docs/closeout_for_review.md`).
- New scripts: `scripts/closeout/co_checkpoint_hashes.py`, `co_swg_slide_meta.py`, `co_swg_cnv_qc.py`, `co_main.py`, `co_h_assemble.py`, `co_render_report.py` (writes this file from the JSONs; no number here is typed by hand).
- New result files (`results/closeout/`): `aceb_checkpoint_hashes.json`, `swg_slide_meta_summary.json`, `closeout_main.json`, `tables.md`, `h_nongrade_controls.json`, `tables_h.md`. Row-level tables (slide filenames, per-patient rows, per-profile QC) stay on the cluster under `feasibility/closeout/` and are not committed.
- New plan: `docs/aceb_analysis_plan.md` (frozen at `0aaa824`).
- Conventions for every number: SWG frozen release `chapter1_lgd2_final_pre_event_20260713_final`, 707 rows / 150 patients / 50 progressor patients; patient score = max over the patient's rows; AUROC rank-based; CI = percentile bootstrap over patients, 2,000 resamples, `RandomState(0)`; permutation = 2,000 permutations of patient labels, `RandomState(0)`. Fused arms = mean of fold-local z-scores (release outer folds). "Head" = ERIN-trained ABMIL grade head applied to the SWG slide at 0.5 µm/px, leak-free unless stated.

## 2. Summary table
| Item | Status | One-line answer |
|---|---|---|
| A | DONE | Four versions reproduce exactly from their files; canonical = leak-free grade head as third arm: head 0.753, fusion 0.850 vs 0.783, gain +0.067 [0.022, 0.114], perm p 0.003 (n 150, 50 events). |
| B | DONE | 54 SWG patients link to 55 ERIN identities; only 43 imaged ERIN cases exist for them, from 33 SWG patients; the other 21 have no imaged ERIN case and were never in any training table; the leak-free head excluded all 55 identities. No rerun needed. |
| C | PARTIAL | Groups differ in age (56.5 vs 65.0, p 0.006), slide age at scan (p 0.044) and grade-label provenance (p <0.001); CNV-only 0.454 [0.280, 0.627] vs 0.760 [0.652, 0.858]; collapse persists within the discovery sequencing sheet (0.253, n 25 / 11). Staining batch, depth in ×, 4× data NOT AVAILABLE. |
| D | DONE | Gain difference +0.176 [0.065, 0.303]; membership-permutation p 0.001 (sizes) / 0.0015 (sizes + events). Post-hoc split. |
| E | DONE | Progressor interval first row → endpoint biopsy median 1096 d, IQR [540, 2080]; excluding ≤6 m / ≤12 m progressors the gain is +0.070 [0.030, 0.113] (n 144/44) and +0.068 [0.026, 0.112] (n 142/42). |
| F | DONE | No clinical arm exists in the release (7 families listed). Row grade alone 0.682; grade + head 0.797; head within first-row-NDBE patients 0.740 [0.625, 0.845] (n 121/33). |
| G | DONE | Pre-registered gate "< 0.7 → moot" quoted; observed slide-level AUROC vs Label: pass-1 0.540, pass-2 0.619, leak-free 0.597; vs DB code 0.629 / 0.606 (n 418). No independent second pathologist read exists. Gate failed for every head. |
| H | DONE | treatment-effect head: alone 0.55, gain -0.029 [-0.075, +0.014]; IM head: alone 0.389, gain -0.004 [-0.053, +0.039]; leak-free permuted head: gain -0.001. |
| I | DONE | 28 third arms were ever evaluated; selection-adjusted permutation p for the maximum (grade, +0.069) = **0.069** (unadjusted 0.0055); same null applied to the canonical gain: 0.078. |
| J | DONE | All digest CIs are patient-level or patient-clustered, seed 0; all use 2,000 resamples except the 13 P32 ERIN field CIs (1,000) — recomputed at 2,000, max change 0.002. |
| K | DONE | Every SWG patient in exactly one outer fold (rep01 and rep02, 0 violations); inner folds keyed by patient; all 9 ERIN task tables and the P32 head table: 0 patients in two folds. Baseline = no single row; all strict pre-event rows are units; patient = max. |
| L | PARTIAL | 4× data NOT AVAILABLE (locations searched listed). Our endpoint/cohort definitions tabulated from code and release metadata; the Killcoyne column is left blank. |
| M | DONE | Calibration slope image 0.616, late_mean 1.780, fuse3+head (Platt-CV) 1.720; Brier 0.245 / 0.184 / 0.168; net benefit at 0.3: 0.100 / 0.135 / 0.160 (treat-all 0.048). p53 IHC on 75 patients: AUROC 0.684; head adds [-0.044, +0.156]. |
| N | DONE | No ACE-B slides, features or CNV on the cluster; depth SWG 0.4× (stated, not verified), ACE-B ~7× (owner's statement). Prevalent HGD/IMC excluded from the primary analysis, secondary detection set. Plan frozen in `docs/aceb_analysis_plan.md` at `0aaa824` with checkpoint hashes. |

## 3. Items

### A. Canonical number reconciliation
**Question.** Which of the reported values (0.83 / 0.850; +0.050 / +0.063 / +0.067; 0.756 / 0.753) is which, and which is canonical?

**Status.** DONE.

**Result.** All four versions recomputed from the out-of-fold and imputed tables (n 150 patients, 50 progressors in every row). Each reproduces the value in its source file to 3 decimals.

| version | third arm | ERIN training set | head alone | fuse2 (image + CNV) | fuse3 | gain | gain CI | perm p | source file of the original report |
|---|---|---|---|---|---|---|---|---|---|
| v1_p32b_fields6_logistic | CV logistic on 6 imputed fields (incl-overlap heads) | 2,293 cases incl. 43 cases of 33 SWG-linked patients | 0.738 [0.652, 0.817] | 0.783 | 0.832 [0.762, 0.894] | +0.050 | [0.015, 0.089] | 0.0025 | `results/numbers/p32b_swg_fuse.json` (`scripts/projects/p32_swg_fuse.py`, commit 926fc93) |
| v2_p32b_grade_only | imputed grade LGD+ (incl-overlap head) | 2,293 cases incl. 43 cases of 33 SWG-linked patients | 0.756 [0.661, 0.842] | 0.783 | 0.851 [0.781, 0.909] | +0.069 | [0.024, 0.119] | 0.0055 | `results/numbers/p32_fuse_controls.json` (`scripts/projects/p32_fuse_controls.py`, 926fc93) |
| v3_noov_fields2_logistic | CV logistic on 2 leak-free imputed fields (grade, inflammation) | 2,249 cases, 55 SWG-linked ERIN ids excluded | 0.754 [0.664, 0.834] | 0.783 | 0.846 [0.774, 0.908] | +0.063 | [0.020, 0.107] | 0.0025 | `results/numbers/p32_fuse_noov.json` (`p32_swg_fuse.py` on `p32_head_noov`, ec07155) |
| v4_noov_grade_only_CANONICAL | imputed grade LGD+ (leak-free head, 55 ERIN ids / 54 SWG patients excluded) | 2,249 cases, 55 SWG-linked ERIN ids excluded | 0.753 [0.659, 0.840] | 0.783 | 0.850 [0.779, 0.909] | +0.067 | [0.022, 0.114] | 0.003 | `results/numbers/p32_noov_subgroups.json` (25 Sep session, ec07155) |

What differs between versions: (i) **training set** of the ERIN head: v1/v2 include the 43 ERIN cases of 33 SWG-linked patients, v3/v4 exclude all 55 linked ERIN identities; (ii) **third arm**: v1/v3 = a CV logistic fitted on SWG labels within the release folds over the imputed field vector (6 fields in v1, 2 in v3), v2/v4 = the imputed grade probability alone, no fitted component; (iii) fold models, feature set (0.5 µm/px UNI2-h bags), aggregation (max over rows), fusion rule (fold-local z-mean), folds (`fold_id_rep01`) and bootstrap seed are identical across versions. "0.83" is v1 rounded; "0.850" is v4 (v2 gives 0.851). "0.756" is the incl-overlap grade head, "0.753" the leak-free one; "+0.063" is v3, "+0.067" v4.

**Canonical: v4** (leak-free grade head as the third arm), because (a) it uses no ERIN case from a SWG patient, (b) its third arm has no component fitted on SWG labels, (c) grade was the field named as the reference target in the P32 pre-registration. Its selection among the evaluated arms is accounted for in item I, where the selection-adjusted p is reported.

**Method.** `co_main.py` block A: release OOF `image_only`/`cnv_only`, imputed tables from `feasibility/runs/{p32b_fields,p32_head_noov}/output/swg_imputed_fields.csv`; z within outer fold; mean; max over rows; rank AUROC; 2,000 patient bootstraps seed 0; 2,000 label permutations seed 0.

**Sources.** `results/closeout/closeout_main.json` · `scripts/closeout/co_main.py` · commit 602a40e; arm AUROCs image 0.731 [0.640, 0.814], CNV 0.663 [0.569, 0.754], fuse2 0.783 [0.700, 0.854].

**Caveats.** The choice of grade as the single third arm was made after the pass-2 results (item I). Item A does not by itself show that the gain survives selection.

### B. Overlap count discrepancy (33 vs 54)
**Question.** Why were 33 patients excluded when 54 SWG patients are also in ERIN, and were any of the other 21 in any head's training set?

**Status.** DONE.

**Result.**

| quantity | value |
|---|---|
| SWG patients linked to an ERIN identity | 54 |
| ERIN anon_ids linked | 55 (62 pairs: 10 by shared accession, 52 via a Barrett's-DB participant) |
| imaged ERIN cases (slides) belonging to those 55 identities, any label status | 43 ({'train_eligible': 42, 'unsure_held_out': 1}) |
| SWG patients with ≥1 such case in any incl-overlap P32 training table (pass-1 groups g0–g3, pass-2, repeat-fold, permuted-label) | 33 (the "33") |
| cases from linked identities in the pass-2 training table | 43 |
| SWG patients with ≥1 such case in the leak-free head's training | 0 |
| identities in the exclusion file used for the leak-free head | 55 (all 55) |

The difference is not a matching error: 54 SWG patients have an ERIN **report** identity, but only 33 of them have an **imaged** ERIN case (43 slides), because ERIN slides were scanned for a subset of reports. The other 21 SWG patients have zero imaged ERIN cases, so they were in no training split of any head in any SWG result. ERIN "train/val/test membership" does not apply: the heads are 5-fold CV over all cases, so every included case trains four of the five fold models whose average is applied to SWG; "in training" therefore means "in the table". The leak-free head nonetheless excluded all 55 identities (all 54 patients), so no rerun is required.

**Method.** Recomputation of the crosswalk (`scripts/task_overlap_audit.py` logic: accession normalisation `PSyy-nnnnn`/`psyy.nnnnn`; DB bridge via `pathology_text_normalised_full.specimennumber` → `participant_id`), then for each linked SWG patient the count of its ERIN cases (`labeller/erin_master.csv` CaseName → anon_id) in every `oof_*.csv` of every P32 run. Row-level table `feasibility/closeout/swg_overlap_training_membership.csv` (cluster).

**Sources.** `results/closeout/closeout_main.json` key `B_overlap`; `results/overlap_audit.json` (`scripts/task_overlap_audit.py`); `results/closeout/closeout_main.json` · `scripts/closeout/co_main.py` · commit 602a40e.

**Caveats.** The bridge depends on DB accession parsing; a SWG patient whose reports carry no parseable accession cannot be linked (SWG DB match rate 0.78 in `overlap_audit.json`), so "never in ERIN" may contain unlinked shared patients. ERIN heads are 5-fold CV over all training cases; every included case trains 4 of the 5 fold models whose average is applied to SWG, so any included case is in training for the imputation. The 21 linked patients without a case in the tables have no imaged ERIN case at all (their ERIN link is report-only).

### C. Characterise the overlap subgroup (54 vs 96)
**Question.** How do the 54 SWG patients also in ERIN differ from the 96 who are not, and does the CNV collapse persist within sequencing strata?

**Status.** PARTIAL (staining batch, depth in ×, referral pathway beyond the DB hospital field, and 4× data are NOT AVAILABLE; see below).

**Result: patient-level comparison.** Patient value = mean (continuous) or mode (categorical) over the patient's release rows. Continuous cells are median [IQR] (n with a value).

| variable | also_in_ERIN (n 54, 14 events) | never_in_ERIN (n 96, 36 events) | test | p |
|---|---|---|---|---|
| n_rows | 4 [2, 7] (n=54) | 3 [2, 6] (n=96) | Mann-Whitney | 0.25 |
| first_year | 2008 [2005, 2012] (n=54) | 2008 [2002, 2010] (n=96) | Mann-Whitney | 0.068 |
| span_days | 119 [0, 1548] (n=54) | 360 [0, 1536] (n=96) | Mann-Whitney | 0.954 |
| biopsies_total | 2 [1, 5] (n=54) | 3 [1, 5] (n=96) | Mann-Whitney | 0.484 |
| followup_months_first_to_last_biopsy | 24.6 [0, 69.6] (n=54) | 36.0 [0, 75.1] (n=96) | Mann-Whitney | 0.609 |
| days_first_to_event | 942 [434, 1894] (n=14) | 1102 [812, 2308] (n=36) | Mann-Whitney | 0.483 |
| age_at_diagnosis | 56.5 [51.2, 63.8] (n=22) | 65.0 [58.8, 68.2] (n=44) | Mann-Whitney | 0.006 |
| prague_C | 0 [0, 2.5] (n=20) | 0 [0, 2] (n=32) | Mann-Whitney | 0.76 |
| prague_M | 4.5 [4, 5.75] (n=22) | 4 [2, 6] (n=33) | Mann-Whitney | 0.27 |
| n_reads_mean | 22197935 [20800968, 25242923] (n=25) | 20981523 [18806932, 23508466] (n=56) | Mann-Whitney | 0.054 |
| cellularity_mean | 29.3 [23.9, 50.0] (n=5) | 47.5 [44.6, 50.0] (n=13) | Mann-Whitney | 0.34 |
| cx_max | 14.5 [0, 45.0] (n=54) | 11.5 [0, 46.5] (n=96) | Mann-Whitney | 0.911 |
| noise_mapd_mean | 0.0715 [0.0633, 0.0783] (n=54) | 0.074 [0.0645, 0.0821] (n=96) | Mann-Whitney | 0.246 |
| n_segments_mean | 218 [174, 291] (n=54) | 201 [162, 283] (n=96) | Mann-Whitney | 0.499 |
| frac_altered_0p15_mean | 0.0316 [0.0231, 0.0463] (n=54) | 0.031 [0.0208, 0.0531] (n=96) | Mann-Whitney | 0.92 |
| frac_altered_0p30_mean | 0.0151 [0.0146, 0.0158] (n=54) | 0.0152 [0.0148, 0.0169] (n=96) | Mann-Whitney | 0.078 |
| slide_age_at_scan_days_mean | 2823 [1424, 3650] (n=54) | 3057 [2237, 4031] (n=96) | Mann-Whitney | 0.044 |
| scan_year_first | 2017 [2017, 2017] (n=54) | 2017 [2017, 2017] (n=96) | Mann-Whitney | 0.45 |
| mpp_mean | 0.221 [0.221, 0.221] (n=54) | 0.221 [0.221, 0.221] (n=96) | Mann-Whitney | 0.194 |
| y | 0: 40, 1: 14 | 0: 60, 1: 36 | Fisher exact | 0.206 |
| baseline_grade | 0: 41, 1: 7, 2: 6 | 0: 80, 1: 6, 2: 10 | chi-square (3 levels; Fisher only defined for 2x2) | 0.359 |
| max_grade | 0: 36, 1: 6, 2: 12 | 0: 61, 1: 9, 2: 26 | chi-square (3 levels; Fisher only defined for 2x2) | 0.787 |
| endpoint_label_name | HGD: 8, IMC/cancer: 2, LGD (second consecutive): 4, missing: 40 | HGD: 18, IMC/cancer: 8, LGD (second consecutive): 10, missing: 60 | chi-square (4 levels; Fisher only defined for 2x2) | 0.484 |
| sex_demographics | F: 5, M: 17, missing: 32 | F: 10, M: 34, missing: 52 | chi-square (3 levels; Fisher only defined for 2x2) | 0.834 |
| gender_id_code | 1: 40, 2: 14, missing: 0 | 1: 74, 2: 21, missing: 1 | chi-square (3 levels; Fisher only defined for 2x2) | 0.655 |
| smoking | N: 4, Y: 10, missing: 40 | N: 4, Y: 17, missing: 75 | chi-square (3 levels; Fisher only defined for 2x2) | 0.681 |
| referral_hospital_db | Addenbrookes: 3, Bedford: 0, Hinchingbrooke: 0, None: 33, Not Specified: 18, West Suffolk: 0, not in DB: 0 | Addenbrookes: 2, Bedford: 1, Hinchingbrooke: 3, None: 55, Not Specified: 30, West Suffolk: 1, not in DB: 4 | chi-square (7 levels; Fisher only defined for 2x2) | 0.375 |
| seq_sheet_mode | discovery_777: 25, validation_268: 29 | discovery_777: 57, validation_268: 39 | Fisher exact | 0.129 |
| scanner_model_mode | C13210: 6, C13239-01: 48 | C13210: 14, C13239-01: 82 | Fisher exact | 0.624 |
| scanner_serial_mode | 000023: 6, 000058: 48 | 000023: 14, 000058: 82 | Fisher exact | 0.624 |
| source_lens_mode | 40: 54 | 40: 96 | constant | None |
| p53_ihc_any_aberrant | aberrant: 4, missing: 31, normal: 19 | aberrant: 12, missing: 44, normal: 40 | chi-square (3 levels; Fisher only defined for 2x2) | 0.344 |
| p53_seqsheet_any | 0: 19, 1: 4, missing: 31 | 0: 40, 1: 11, missing: 45 | chi-square (3 levels; Fisher only defined for 2x2) | 0.429 |
| grade_source_mode | master_label_fallback: 4, scraped_confirmed: 49, scraped_research: 1 | master_label_fallback: 36, scraped_confirmed: 60, scraped_research: 0 | chi-square (3 levels; Fisher only defined for 2x2) | <0.001 |
| next_label_source_mode | master: 27, scrape_exact: 27 | master: 57, scrape_exact: 39 | Fisher exact | 0.306 |

Sequencing batch (Leanne batch, 12 levels, p 0.565) and SLX run (43 levels, p 0.51) are in the JSON (`C_characterisation`) and not tabulated here. Variable notes: `first_year` = year of the earliest release row; `span_days` = first to last release row; `followup_months_first_to_last_biopsy` = max `MonthsBeforeLastBiopsy`; `days_first_to_event` = progressors only (item E definition); `age_at_diagnosis`, `prague_C/M`, `sex_demographics`, `smoking` from `SWGCohort/Demographics_full.csv` (66 of 150 patients); `gender_id_code` from `SWGCohort/barretts_database_230809.csv` (code mapping not documented; reported as code); `referral_hospital_db` = referral hospital of the first DB endoscopy (Barrett's-DB export, participant id); `seq_sheet_mode` = discovery (777-sample sheet) vs validation (268-sample sheet) membership of the patient's CNV profiles; `n_reads_mean` from the discovery sheet only (validation sheet has no read count); `cellularity_mean` from the sheet (18 patients); `cx_max` = release complexity score; `noise_mapd_mean`, `n_segments_mean`, `frac_altered_*` from the QDNAseq 50 kb profiles (`co_swg_cnv_qc.py`; values are relative copy-number ratios centred at 1, altered = |ratio − median| > 0.15 / 0.30); `scanner_model_mode`/`scanner_serial_mode`/`source_lens_mode`/`mpp_mean`/`scan_year_first`/`slide_age_at_scan_days_mean` from the .ndpi headers (`co_swg_slide_meta.py`: 707/707 slides read; models {'C13239-01': 585, 'C13210': 122}; scan years {'2016': 122, '2017': 585}; NDP.scan versions {'NDP.scan 3.2.15': 374, 'NDP.scan 3.3.0': 333}); `p53_ihc_any_aberrant` from `SWGCohort/slide_matching.csv`; `p53_seqsheet_any` from the sequencing sheet; `grade_source_mode` / `next_label_source_mode` = provenance of the row grade and of the next-biopsy label in the release (`GradeSource`, `NextBiopsyLabel_source`). "Who ascertained progression" is not recorded as a person; the provenance columns are the closest available proxy.

**Result: arm AUROCs per subgroup** (canonical leak-free head; CIs from within-subgroup bootstrap).

| subgroup | n | events | CNV-only | image-only | head-only | image + CNV | with head | gain |
|---|---|---|---|---|---|---|---|---|
| all | 150 | 50 | 0.663 [0.569, 0.754] | 0.731 [0.640, 0.814] | 0.753 [0.659, 0.840] | 0.783 [0.700, 0.854] | 0.850 [0.779, 0.909] | +0.067 [0.022, 0.114] |
| also_in_ERIN | 54 | 14 | 0.454 [0.280, 0.627] | 0.704 [0.550, 0.841] | 0.745 [0.562, 0.899] | 0.580 [0.395, 0.754] | 0.779 [0.625, 0.909] | +0.198 [0.096, 0.317] |
| never_in_ERIN | 96 | 36 | 0.760 [0.652, 0.858] | 0.744 [0.634, 0.850] | 0.758 [0.638, 0.863] | 0.863 [0.785, 0.932] | 0.885 [0.816, 0.945] | +0.022 [-0.027, +0.070] |

**Result: CNV-only within sequencing strata × subgroup** (rows with n ≥ 10 shown; all strata in the JSON key `C_cnv_by_stratum`; CI when events ≥ 3).

| stratum | subgroup | n | events | CNV-only AUROC |
|---|---|---|---|---|
| sequencing sheet (discovery vs validation)=discovery_777 | also_in_ERIN | 25 | 11 | 0.253 [0.081, 0.487] |
| sequencing sheet (discovery vs validation)=discovery_777 | never_in_ERIN | 57 | 29 | 0.703 [0.556, 0.835] |
| sequencing sheet (discovery vs validation)=validation_268 | also_in_ERIN | 29 | 3 | 0.538 [0.143, 0.846] |
| sequencing sheet (discovery vs validation)=validation_268 | never_in_ERIN | 39 | 7 | 0.750 [0.500, 0.938] |
| SLX run=SLX-12455 | never_in_ERIN | 12 | 6 | 0.417 [0.029, 0.806] |
| Leanne batch (discovery only)=Batch 4 | never_in_ERIN | 12 | 6 | 0.417 [0.029, 0.806] |
| Leanne batch (discovery only)=missing | also_in_ERIN | 29 | 3 | 0.538 [0.143, 0.846] |
| Leanne batch (discovery only)=missing | never_in_ERIN | 39 | 7 | 0.750 [0.500, 0.938] |
| read-count tertile=reads_T1_low | never_in_ERIN | 21 | 10 | 0.682 [0.436, 0.904] |
| read-count tertile=reads_T2 | never_in_ERIN | 19 | 8 | 0.682 [0.393, 0.923] |
| read-count tertile=reads_T3_high | also_in_ERIN | 11 | 4 | 0.250 [0.000, 0.607] |
| read-count tertile=reads_T3_high | never_in_ERIN | 16 | 10 | 0.817 [0.545, 1.000] |

CNV-only at 4× resequencing: NOT AVAILABLE: no resequenced data exists; see item L.

**Method.** `co_main.py` block C; tests: `scipy.stats.mannwhitneyu` (two-sided), `fisher_exact` for 2×2, `chi2_contingency` for more than two levels (labelled). Missing values form their own level in categorical tests where present.

**Sources.** `results/closeout/closeout_main.json` · `scripts/closeout/co_main.py` · commit 602a40e; `results/closeout/swg_slide_meta_summary.json` (`scripts/closeout/co_swg_slide_meta.py`); QC rows `feasibility/closeout/swg_cnv_qc.csv` (cluster, `scripts/closeout/co_swg_cnv_qc.py`); `SWGCohort/Demographics_full.csv`, `sWGS_777_samples_cleaned_202401_Leanne_fullDetails (3) (1).csv`, `sWGS_validation_cleaned_Leanne (4) (1).csv`, `slide_matching.csv`, `barretts_database_230809.csv` (cluster data, not in the repo).

**Caveats.** NOT AVAILABLE: staining batch (no record in any SWG table); referral pathway beyond DB referral_hospital of first endoscopy; sequencing depth in x (reads only; read length not recorded in the sheet); sex for patients absent from Demographics_full.csv (gender_id code from barretts_database_230809.csv reported as code, mapping not documented); p53 IHC for slides with blank p53IHC in slide_matching.csv; 4x resequencing (none exists; see L). The grade-provenance difference (p <0.001) is structural: the overlap was found through the Barrett's DB, so linked patients are those whose grades were scraped from the DB. Demographics cover 66/150 patients and read counts 81/150, so those tests are on subsets. The two subgroups have 14 and 36 events; per-stratum CIs are wide.

### D. Interaction test
**Question.** Is the fusion gain different between the 54 and the 96, beyond chance?

**Status.** DONE. **This split was defined for the leakage check on 25 Sep 2026 and is a post-hoc subgroup analysis.**

**Pre-specification.** Commit `0aaa824` (section "D. Interaction test" of the pre-specification, reproduced verbatim in §6).

**Result.**

| quantity | value |
|---|---|
| gain also_in_ERIN (n 54, events 14) | +0.198 |
| gain never_in_ERIN (n 96, events 36) | +0.022 |
| difference (also − never) | +0.176 |
| bootstrap CI, patients resampled within each subgroup, 2000 resamples, seed 0 | [0.065, 0.303] |
| permutation of membership, sizes preserved: two-sided p / one-sided p / null 2.5–97.5 % | 0.001 / 0.001 / [-0.098, +0.095] (2000 valid) |
| permutation preserving sizes and progressor counts per group | 0.0015 / 0.0015 / [-0.103, +0.098] (2000 valid) |

**Method.** As pre-specified; `co_main.py` block D.

**Sources.** `results/closeout/closeout_main.json` · `scripts/closeout/co_main.py` · commit 602a40e.

**Caveats.** Post-hoc split; the subgroup with the large gain has 14 events; the interaction is driven by the CNV arm (item C), which is one of the two fused arms, not by the head, whose AUROC is similar in both subgroups.

### E. Prevalent vs future disease
**Question.** How far from the baseline sample is the endpoint biopsy, and does the result survive dropping near-baseline progressors?

**Status.** DONE.

**Result: interval distribution** (50 progressor patients; interval = earliest release row → endpoint biopsy, the biopsy that completes the LGD2+ rule; 9 progressors have a single row).

| statistic | value |
|---|---|
| n with interval | 50 |
| median (days) | 1096 |
| IQR (days) | [540, 2080] |
| min, max (days) | 118, 5262 |
| histogram | 0-6m: 6, 6-12m: 2, 12-24m: 6, 24-36m: 10, 36-60m: 10, >60m: 16 |
| secondary: min `DaysFromCurrentToEvent` per progressor (release column, non-null for 30 progressors) | median 728 d |

**Result: exclusion runs** (canonical arms).

| exclusion | n | events | head | image + CNV | with head | gain |
|---|---|---|---|---|---|---|
| none | 150 | 50 | 0.753 [0.659, 0.840] | 0.783 [0.700, 0.854] | 0.850 [0.779, 0.909] | +0.067 [0.022, 0.114] |
| exclude progressors with event <= 6 m from first row | 144 | 44 | 0.776 [0.680, 0.861] | 0.794 [0.715, 0.866] | 0.864 [0.797, 0.920] | +0.070 [0.030, 0.113] |
| exclude progressors with event <= 12 m from first row | 142 | 42 | 0.767 [0.672, 0.856] | 0.791 [0.711, 0.871] | 0.859 [0.793, 0.918] | +0.068 [0.026, 0.112] |
| SECONDARY: drop positive ROWS with DaysToNextBiopsy <= 183 (patient keeps other rows) (rows kept 675) | 144 | 44 | 0.772 [0.677, 0.857] | 0.775 [0.693, 0.850] | 0.856 [0.786, 0.915] | +0.081 [0.038, 0.126] |
| SECONDARY: drop positive ROWS with DaysToNextBiopsy <= 365 (rows kept 660) | 142 | 42 | 0.727 [0.624, 0.824] | 0.740 [0.647, 0.829] | 0.801 [0.717, 0.879] | +0.062 [0.013, 0.111] |

**Method.** As pre-specified. One correction after the first run (commit `4af24d5`, stated per rule 8): in the SECONDARY row-dropping analysis the first run re-derived the patient label from the remaining rows, which turned 11 progressors into non-progressors (events 33/25); the corrected version keeps each patient's original progressor label and drops rows only. Both versions are in git history (`feasibility/runs/co_main` outputs of jobs 57654406 and 57654440 on the cluster); the corrected one is reported.

**Sources.** `results/closeout/closeout_main.json` · `scripts/closeout/co_main.py` · commit 602a40e.

**Caveats.** The release has no single baseline sample: evaluation uses all strict pre-event rows with max aggregation, so "interval from baseline" is measured from the earliest row. Rows at or after the event were already excluded by the release (183 at-event, 31 post-event rows).

### F. Baseline grade
**Question.** Is the baseline pathologist grade in the clinical-only arm, and what do grade-based arms give?

**Status.** DONE.

**Result.** The release has **no clinical arm**. Model families with out-of-fold predictions: `cnv_only`, `coattention_fusion`, `early_fusion`, `image_only`, `intermediate_fusion`, `late_mean`, `late_stack_logit`. No family takes clinical covariates; there is therefore no feature list to quote. Grade coding: pre_event_cohort.Label per row: 0 NDBE, 1 IND, 2 LGD (no HGD+ rows in the 707); MaxPathologySoFar = max grade up to the row.

| arm (all 150 patients, 50 events) | AUROC |
|---|---|
| grade_arm | 0.682 [0.585, 0.778] |
| grade_plus_head | 0.797 [0.713, 0.873] |
| grade_maxsofar_arm | 0.671 [0.574, 0.770] |
| grade_maxsofar_plus_head | 0.796 [0.711, 0.872] |
| fuse2_plus_grade | 0.843 [0.776, 0.901] |
| fuse3_plus_grade | 0.885 [0.830, 0.934] |
| head | 0.753 [0.659, 0.840] |
| fuse2 | 0.783 [0.700, 0.854] |
| fuse3 | 0.850 [0.779, 0.909] |
| grade_raw_max | 0.687 [0.601, 0.768] |

`grade_arm` = CV logistic (release folds) on the row grade; `grade_maxsofar_arm` adds `MaxPathologySoFar`; `_plus_head` = fold-z mean with the leak-free head; `grade_raw_max` = the raw grade code, max over rows, no fitting. Age and sex are available for 66 patients only (item C) and were not used.

**Within baseline-NDBE patients.**

| definition | n | events | head | image | CNV | image + CNV | with head | gain |
|---|---|---|---|---|---|---|---|---|
| first release row NDBE (Label 0) | 121 | 33 | 0.740 [0.625, 0.845] | 0.777 [0.674, 0.866] | 0.710 [0.595, 0.816] | 0.832 [0.749, 0.904] | 0.881 [0.815, 0.938] | +0.049 [0.009, 0.091] |
| all release rows NDBE | 97 | 21 | 0.724 [0.573, 0.853] | 0.781 [0.654, 0.893] | 0.758 [0.636, 0.866] | 0.867 [0.773, 0.943] | 0.916 [0.846, 0.969] | +0.049 [0.004, 0.101] |

**Method.** `co_main.py` block F; logistic C = 1, features standardised on the training folds.

**Sources.** `results/closeout/closeout_main.json` · `scripts/closeout/co_main.py` · commit 602a40e; release families from `<release>/training_final_nested_cv_v1/`.

**Caveats.** "Clinical + baseline grade" reduces to grade alone because no other clinical covariate is in the release for all patients.

### G. The failed pre-registered sanity check
**Question.** What was pre-registered, what was observed, and is there a second read?

**Status.** DONE.

**Pre-registration (verbatim).** `docs/projects/P32_image_to_fields.md` at commit `128760e`, committed 2026-09-24 17:50:13 +0100:

> The seed-0 fold models are applied to all 707 SWG release slides (UNI2 npz) to impute every field. Then, on the release folds and endpoint, patient level, 150 patients: a CV logistic on the imputed-field vector ("fields" arm); 3-way fold-local z-mean fusion (image OOF + CNV OOF + fields) vs the 2-way (image + CNV) on the same 150 patients; paired 2,000-boot CI. Sanity check first: imputed grade LGD+ vs the SWG pathologist grade (if this is < 0.7 the imputation has not transferred and the fusion result is moot).

and, under "Predictions written down before results": "SWG payoff: imputed grade tracks the pathologist grade at 0.7–0.8 despite the scale shift; the 3-way fusion does NOT beat 2-way with a CI excluding zero at n = 150. If it does, that is the Chapter 1–2 bridge."

**Result.** Metric: slide-level AUROC of the head's imputed P(LGD+) against the binary pathologist grade LGD+ (Label >= 2) on the 707 release rows; the 707 rows contain no HGD+ so LGD+ = LGD. n rows 707, LGD rows 87. Source of the pathologist grade (`GradeSource` on the 707 rows): {'scraped_confirmed': 547, 'master_label_fallback': 155, 'scraped_research': 5}.

| head | AUROC vs release Label (707 rows) | AUROC vs DB confirmed code (418 rows, 62 LGD+) | AUROC vs Label on the same 418 rows |
|---|---|---|---|
| pass-1 (0.88 µm/px imputation, incl-overlap) | 0.540 | n/a | n/a |
| pass-2 `p32b_fields` (0.5 µm/px, incl-overlap) | 0.619 | 0.629 | 0.640 |
| repeat-fold head (`p32_head_repeat`) | 0.602 | n/a | n/a |
| permuted-label head (`p32_head_perm`) | 0.566 | n/a | n/a |
| leak-free head `p32_head_noov` (canonical) | 0.597 | 0.606 | 0.621 |

"0.619" is the pass-2 head vs the release Label; "0.63" is the same head vs the DB confirmed code (0.629). Every head is below the pre-registered 0.7, including the canonical one (0.597). The permuted-label head scores 0.566 on the same check.

**Second read.** NONE: highestgradedysresearch is 7 (not done) on 325/327 matched reports; no other pathologist re-read table exists in the release, the SWGCohort folder or the DB export. Release Label vs DB confirmed code on the 418 coded rows: two-tier agreement 0.993, kappa 0.972, AUROC of Label as a score for the code 0.996. GradeSource shows Label is itself 'scraped_confirmed' (the DB code) for most rows, so this is not an independent second pathologist read.

**Method.** `co_main.py` block G; DB code mapping 2→NDBE, 3→IND, 4→LGD, 5→HGD, 6/8→cancer (`query_dysplasia_types`); rows matched by accession stem to `swg_matched_reports_v2.parquet`.

**Sources.** `results/closeout/closeout_main.json` · `scripts/closeout/co_main.py` · commit 602a40e; pre-registration `docs/projects/P32_image_to_fields.md` @ `128760e`; earlier values `results/numbers/p32_checks.json` (`scripts/projects/p32_checks.py`), `results/numbers/p32b_fields.json`, `p32_head_noov.json`.

**Caveats.** The pre-registration set the gate on "the SWG pathologist grade" without naming the column; the release Label is for 547/707 rows the DB confirmed code itself, so the two anchors are not independent. The 707 rows contain no HGD+, so the check is NDBE/IND vs LGD only. By the letter of the pre-registration the fusion result is "moot"; the project log re-read the gate after the fact (digest §5), which is a post-hoc decision.

### H. Non-grade ensemble control (new training)
**Question.** Does an ERIN head trained on a non-grade field give the same fusion gain?

**Status.** DONE.

**Pre-specification.** Commit `0aaa824` (section "H" of the pre-specification, verbatim in §6). Run names `co_h_treat_noov`, `co_h_im_noov`, `co_h_perm_noov` (cluster jobs 57654104–57654106).

**Result** (all 150 patients, 50 events; fuse2 = image + CNV = 0.783).

| head | ERIN training cases | ERIN OOF AUROC (n / pos) | head alone on SWG | with head (fuse3) | gain vs fuse2 | perm p |
|---|---|---|---|---|---|---|
| grade_LGDplus_leakfree_CANONICAL | 2249 | 0.890 (2247 / 620) | 0.753 [0.659, 0.840] | 0.850 [0.779, 0.909] | +0.067 [0.022, 0.114] | 0.0025 |
| inflammation_mod_severe_leakfree | 2249 | 0.747 (1712 / 342) | 0.738 [0.647, 0.815] | 0.820 [0.741, 0.886] | +0.038 [-0.004, +0.080] | 0.0575 |
| treatment_effect_leakfree_NEW | 2249 | 0.834 (2249 / 433) | 0.550 [0.448, 0.649] | 0.754 [0.671, 0.831] | -0.029 [-0.075, +0.014] | 0.8671 |
| im_present_leakfree_NEW | 2249 | 0.893 (2180 / 1411) | 0.389 [0.299, 0.487] | 0.779 [0.699, 0.854] | -0.004 [-0.053, +0.039] | 0.5887 |
| grade_permuted_labels_leakfree_NEW | 2249 | 0.491 (2247 / 620) | 0.583 [0.486, 0.681] | 0.782 [0.694, 0.858] | -0.001 [-0.043, +0.045] | 0.5252 |
| grade_permuted_labels_incl_overlap | 2293 | 0.487 (2291 / 622) | 0.449 [0.354, 0.552] | 0.677 [0.589, 0.768] | -0.105 [-0.170, -0.037] | 1.0 |
| treatment_effect_incl_overlap_pass2 | 2293 | 0.819 (2293 / 445) | 0.556 [0.462, 0.652] | 0.778 [0.698, 0.851] | -0.005 [-0.049, +0.038] | 0.5802 |
| im_present_incl_overlap_pass2 | 2293 | 0.891 (2224 / 1436) | 0.385 [0.293, 0.483] | 0.775 [0.695, 0.853] | -0.007 [-0.059, +0.036] | 0.6367 |

**Method.** fold-local z-mean of image_only OOF, cnv_only OOF and the head's imputed probability; patient = max over rows; 2000 bootstraps, 2000 permutations, seed 0; heads trained by `scripts/projects/p32_fields_from_image.py` with the leak-free exclusion file (2,249 cases), P31 v2 labels, 0.5 µm/px SWG bags; `scripts/closeout/co_h_assemble.py`.

**Sources.** `results/closeout/h_nongrade_controls.json` · `scripts/closeout/co_h_assemble.py` · commit 602a40e; head runs `feasibility/runs/co_h_*_noov/output/` (cluster).

Reading rule outcome (stated before training, §6): no non-grade head's gain has a CI excluding zero on the positive side; the condition under which the gain would be attributed to representation rather than grade content is not met.

**Caveats.** The reading rule was stated before training (§6). ERIN OOF AUROCs of the new heads are reported so a weak head can be told apart from a non-transferring one.

### I. Selection across P32 fields
**Question.** Which imputed fields were ever evaluated on SWG, and what is the selection-adjusted p for the grade head's gain?

**Status.** DONE.

**Result: candidates and when first evaluated** (dates from result-file commits: pass-1 fields 2026-09-24 19:51 `0dd5df8`; pass-1 fusion and pass-2 fusion + controls 2026-09-24 23:20 `926fc93`; leak-free 2026-09-25 11:33 `ec07155`). Observed gain (fuse3 − fuse2) per candidate third arm, all 150 patients:

| candidate third arm | gain |
|---|---|
| pass1_0.88um:grade_LGDplus | +0.007 |
| pass1_0.88um:grade_HGDplus | -0.012 |
| pass1_0.88um:im_present | +0.001 |
| pass1_0.88um:inflammation_mod_severe | +0.011 |
| pass1_0.88um:inflammation_any | +0.032 |
| pass1_0.88um:ulceration | -0.046 |
| pass1_0.88um:squamous_only | -0.046 |
| pass1_0.88um:gastric_present | -0.030 |
| pass1_0.88um:treatment_effect | -0.059 |
| pass1_0.88um:p53_abnormal | -0.001 |
| pass1_0.88um:certainty_not_definite | -0.051 |
| pass1_0.88um:site_goj_or_stomach | -0.009 |
| pass1_0.88um:specimen_resection | -0.008 |
| pass1_0.88um:logistic_all13 | +0.020 |
| pass2_0.5um:grade_LGDplus | +0.069 |
| pass2_0.5um:im_present | -0.007 |
| pass2_0.5um:treatment_effect | -0.005 |
| pass2_0.5um:ulceration | -0.078 |
| pass2_0.5um:squamous_only | -0.042 |
| pass2_0.5um:inflammation_mod_severe | +0.037 |
| pass2_0.5um:logistic_all6 | +0.050 |
| pass2_0.5um:logistic_without_grade_LGDplus | +0.027 |
| pass2_0.5um:logistic_without_im_present | +0.053 |
| pass2_0.5um:logistic_without_treatment_effect | +0.058 |
| pass2_0.5um:logistic_without_ulceration | +0.048 |
| pass2_0.5um:logistic_without_squamous_only | +0.050 |
| pass2_0.5um:logistic_without_inflammation_mod_severe | +0.043 |
| pass2_0.5um:img2_rep02_ensemble_control | +0.018 |

| quantity | value |
|---|---|
| candidates maximised over | 28: every third arm ever fused with image + CNV on SWG: 13 pass-1 single fields (0.88 um imputation), pass-1 all-13 logistic, 6 pass-2 single fields (0.5 um), pass-2 all-6 logistic, 6 pass-2 leave-one-field-out logistics, the rep02 image ensemble control; fusion rule fixed (fold-local z-mean) so not maximised over |
| selected maximum | pass2_0.5um:grade_LGDplus (+0.069) |
| unadjusted permutation p for the selected arm | 0.0055 |
| **selection-adjusted p (max over all candidates under 2000 label permutations, seed 0)** | **0.069** |
| canonical leak-free grade gain against the same max-null | +0.067 → p 0.078 |

For comparison, `results/numbers/p32_checks.json` (`scripts/projects/p32_checks.py`) adjusted over the 6 pass-2 fields only and reported p 0.022; adjusting over everything that was evaluated gives 0.069.

**Method.** `co_main.py` block I. The fusion rule (fold-local z-mean) was fixed in the P32 pre-registration and is not maximised over; the choice "single field vs logistic over fields" was not fixed and is included.

**Sources.** `results/closeout/closeout_main.json` · `scripts/closeout/co_main.py` · commit 602a40e; pass-1 imputations `feasibility/runs/p32_fields_g0..g3/output/swg_imputed_fields.csv`, pass-2 `p32b_fields`, rep02 image `<release>_rep02/training_rep02_nested_cv/image_only`.

**Caveats.** Pass-1 arms were imputed at 0.88 µm/px and pass-2 at 0.5 µm/px; both are included because both were evaluated. The retrained leak-free head is a re-estimate of the selected arm, not a new candidate.

### J. CI method audit
**Question.** For every CI in `docs/results_digest_2026-09-24_25.md`: resampling unit, n, seed; recompute any that are not patient-clustered.

**Status.** DONE.

**Result.** Read from the generating scripts (grep of `RandomState`, `choice`, `groupby("patient_id")`, cluster index construction):

| digest location | CI(s) | generating script | resampling unit | n resamples | seed |
|---|---|---|---|---|---|
| summary row 2, §1 table (rep01/rep02 deltas vs image) | e.g. +0.043 [+0.014, +0.071], +0.042 [+0.019, +0.069] | `scripts/numbers/num_swg_rep02.py` | patient (max over rows; `groupby("patient_id")`) | 2,000 | 0 |
| §1 permutation / selection-adjusted p | 0.0025 / 0.001; 0.225 / 0.024 | `scripts/numbers/num_swg_rep02_selection.py` | patient labels permuted | 2,000 | 0 |
| summary row 3, §2 table (spec at sens 0.95, Brier deltas), recalibration Brier CI | e.g. −0.061 [−0.095, −0.027]; [−0.079, −0.007] | `scripts/numbers/num_swg_robustness.py` | patient (items 14–16); item 17 windows: rows resampled by patient cluster | 2,000 | 0 |
| summary row 4 | 0.750 / 0.756 / 0.748 (CIs in JSON) | `scripts/numbers/num_cnvtext_cis.py` | patient (max risk over rows) | 2,000 | 0 |
| §3 T4 rows | 0.874 [0.850, 0.896]; 0.686 [0.610, 0.767] | `scripts/numbers/num_t4_treatment_split.py` | ERIN case rows resampled by patient cluster (`anon_id`) | 2,000 | 0 |
| §3 T3a/T3b biopsy-only | 0.801 [0.751, 0.848]; Δ 0.228 [0.156, 0.298]; 0.822 [0.764, 0.874]; Δ 0.226 [0.138, 0.317] | `scripts/erin_fusion/assemble_bio.py` | ERIN units resampled by patient cluster (`anon_id`) | 2,000 | 0 |
| §3 grade model rows | 0.871 [0.842, 0.897]; 0.865 [0.831, 0.896] | `scripts/numbers/num_grade_within_biopsy.py` | slides resampled by patient cluster (`anon_id`) | 2,000 | 0 |
| §5 P32 ERIN field table (13 CIs) | e.g. grade LGD+ 0.861 [0.840, 0.882] | `scripts/projects/p32_fields_from_image.py` | cases resampled by patient cluster (`anon_id`) | **1,000** (deviates from the 2,000 convention) | 0 |
| §5 P32 SWG arm table, controls table, overlap tables | e.g. +0.050 [+0.015, +0.089]; +0.063 [+0.020, +0.107] | `scripts/projects/p32_swg_fuse.py`, `p32_fuse_controls.py`, `p32_checks.py`, subgroup split in the 25 Sep session | patient-level vectors (max over rows) resampled | 2,000 | 0 |
| §5 P33 table | e.g. T3a 0.800 [0.753, 0.847] | `scripts/projects/p33_tasks.py` | units resampled by patient cluster (`anon_id`) | 2,000 | 0 |
| §4 anchors, §5 P31 kappas, row 20 intervals | no CIs (agreement statistics, Mann-Whitney p) | `task_anchor_eval.py`, `p31_agreement.py`, `fig_db_interval_first_lgd.py` | n/a | n/a | n/a |


The only deviation is the 13 P32 ERIN field CIs (1,000 patient-clustered resamples). Recomputed at 2,000 from the saved out-of-fold files:

| run | field | n cases | n patients | pos | AUROC | CI (2,000, patient-clustered, seed 0) |
|---|---|---|---|---|---|---|
| p32b_fields | grade_LGDplus | 2291 | 1613 | 622 | 0.887 | [0.868, 0.905] |
| p32b_fields | im_present | 2224 | 1564 | 1436 | 0.891 | [0.877, 0.904] |
| p32b_fields | inflammation_mod_severe | 1745 | 1292 | 343 | 0.738 | [0.707, 0.770] |
| p32b_fields | squamous_only | 2291 | 1614 | 116 | 0.881 | [0.854, 0.908] |
| p32b_fields | treatment_effect | 2293 | 1614 | 445 | 0.819 | [0.796, 0.843] |
| p32b_fields | ulceration | 2114 | 1505 | 318 | 0.858 | [0.831, 0.883] |
| p32_head_noov | grade_LGDplus | 2247 | 1580 | 620 | 0.890 | [0.872, 0.907] |
| p32_head_noov | inflammation_mod_severe | 1712 | 1269 | 342 | 0.747 | [0.715, 0.778] |
| p32_fields_g0 | grade_HGDplus | 1642 | 1213 | 482 | 0.911 | [0.892, 0.931] |
| p32_fields_g0 | grade_LGDplus | 1642 | 1213 | 644 | 0.861 | [0.839, 0.882] |
| p32_fields_g0 | im_present | 2192 | 1542 | 1406 | 0.897 | [0.884, 0.910] |
| p32_fields_g1 | inflammation_any | 1846 | 1352 | 1517 | 0.607 | [0.570, 0.643] |
| p32_fields_g1 | inflammation_mod_severe | 1846 | 1352 | 373 | 0.742 | [0.709, 0.770] |
| p32_fields_g1 | squamous_only | 2291 | 1614 | 127 | 0.920 | [0.893, 0.944] |
| p32_fields_g1 | ulceration | 2154 | 1527 | 320 | 0.847 | [0.817, 0.875] |
| p32_fields_g2 | gastric_present | 1182 | 958 | 831 | 0.781 | [0.749, 0.812] |
| p32_fields_g2 | p53_abnormal | 473 | 368 | 193 | 0.749 | [0.701, 0.795] |
| p32_fields_g2 | treatment_effect | 2293 | 1614 | 522 | 0.821 | [0.799, 0.842] |
| p32_fields_g3 | certainty_not_definite | 2289 | 1613 | 78 | 0.538 | [0.464, 0.612] |
| p32_fields_g3 | site_goj_or_stomach | 2293 | 1614 | 612 | 0.723 | [0.697, 0.749] |
| p32_fields_g3 | specimen_resection | 2293 | 1614 | 91 | 1.000 | [1.000, 1.000] |

**Method.** `co_main.py` block J; digest-side sources: `results/numbers/p32_fields.json`, `p32b_fields.json` (1,000-resample CIs).

**Sources.** `results/closeout/closeout_main.json` · `scripts/closeout/co_main.py` · commit 602a40e.

**Caveats.** None of the digest CIs is slide-level i.i.d.; no conclusion changes. The digest's SWG fusion CIs are "patient-level" by construction (the unit is the patient vector), which is the same as patient-clustered here.

### K. Aggregation and baseline definition
**Question.** What is a patient's baseline, how do slides aggregate, are folds grouped by patient everywhere?

**Status.** DONE.

**Result.** release row = one slide + one CNV profile (707 rows; 26 rows share a CNV profile with another row). the release has no single baseline row: every strict pre-event row of a patient is a unit in training and in evaluation; 'baseline' in items C/E means the earliest release row. Patient score: max over the patient's rows of the arm score (after fold-local z for fused arms); patient label: max of y_progressor over rows. rows of one patient always share an outer fold (assertion above) so no patient is split across train/test.

Assertions run in `co_main.py` block K:

| check | code path | result |
|---|---|---|
| SWG rep01: patients in more than one outer fold | `training_manifest.fold_id_rep01` grouped by `patient_id` | 0 |
| SWG rep02: patients in more than one outer fold | `_rep02/training_manifest_v2.csv` | 0 |
| SWG inner folds, image_only / cnv_only | `fold*/inner_fold_assignments.csv` (keyed by patient_id) | 0 / 0 |
| ERIN task T1 (n units 48, patients 48): patients in more than one fold | `scripts/abmil_clf.patient_folds(keys, anon_id, y, 5, seed=0)` as called by `scripts/erin_fusion/worker.py` | 0 |
| ERIN task T2a (n units 185, patients 156): patients in more than one fold | `scripts/abmil_clf.patient_folds(keys, anon_id, y, 5, seed=0)` as called by `scripts/erin_fusion/worker.py` | 0 |
| ERIN task T2b (n units 183, patients 155): patients in more than one fold | `scripts/abmil_clf.patient_folds(keys, anon_id, y, 5, seed=0)` as called by `scripts/erin_fusion/worker.py` | 0 |
| ERIN task T2c (n units 389, patients 289): patients in more than one fold | `scripts/abmil_clf.patient_folds(keys, anon_id, y, 5, seed=0)` as called by `scripts/erin_fusion/worker.py` | 0 |
| ERIN task T3a (n units 1274, patients 1056): patients in more than one fold | `scripts/abmil_clf.patient_folds(keys, anon_id, y, 5, seed=0)` as called by `scripts/erin_fusion/worker.py` | 0 |
| ERIN task T3a_bio (n units 1203, patients 1001): patients in more than one fold | `scripts/abmil_clf.patient_folds(keys, anon_id, y, 5, seed=0)` as called by `scripts/erin_fusion/worker.py` | 0 |
| ERIN task T3b (n units 1274, patients 1056): patients in more than one fold | `scripts/abmil_clf.patient_folds(keys, anon_id, y, 5, seed=0)` as called by `scripts/erin_fusion/worker.py` | 0 |
| ERIN task T3b_bio (n units 1203, patients 1001): patients in more than one fold | `scripts/abmil_clf.patient_folds(keys, anon_id, y, 5, seed=0)` as called by `scripts/erin_fusion/worker.py` | 0 |
| ERIN task T4 (n units 1147, patients 874): patients in more than one fold | `scripts/abmil_clf.patient_folds(keys, anon_id, y, 5, seed=0)` as called by `scripts/erin_fusion/worker.py` | 0 |
| P32 ERIN heads (n cases 2293, patients 1614) | `patient_folds` in `scripts/projects/p32_fields_from_image.py` | 0 |

`patient_folds` (`scripts/abmil_clf.py` lines 72–82) assigns whole patients to folds, event-stratified, so a patient cannot be split by construction; the assertions confirm it on the tables actually used, including the C26 field-effect tasks T3a/T3b (and their biopsy-only variants), T2a/T2b/T2c, T4 and T1.

**Sources.** `results/closeout/closeout_main.json` · `scripts/closeout/co_main.py` · commit 602a40e; `scripts/abmil_clf.py`; `scripts/erin_fusion/worker.py`; `feasibility/erin_fusion/tasks/*.csv` (cluster).

**Caveats.** Multiple rows per patient enter training as separate units within the same fold; the release trainer does not weight patients equally.

### L. CNV comparison to Killcoyne 2020
**Question.** CNV-only at 0.4× vs 4× on the same patients; side-by-side definitions.

**Status.** PARTIAL (4× NOT AVAILABLE).

**Result: 4× data.** NOT AVAILABLE. Locations searched: /mnt/scratche/fast/fmlab/datasets/imaging/SWGCohort (50kb, copy_number_hg38/train, dna_seq_bam: 1,035 BAMs, validation_genomics: id lists only); barretts_training/leanne_files_25_03_2026 (777 discovery + 268 validation sample sheets, no depth column); docs/NUMBERS.md, docs/status_ledger_2026-09-24.md item 2, questions_for_people Q2 (question to Leanne, unanswered).

**Result: definitions** (ours filled from code and release metadata; the Killcoyne 2020 column is left for the author).

| field | ours | Killcoyne 2020 |
|---|---|---|
| modality | H&E (UNI2 ABMIL) + sWGS CNV; CNV-only arm = `cnv_only` | |
| cohort | 150 patients, 707 rows; 50 progressor patients; 107 positive rows | |
| unit | one biopsy slide + one CNV profile per row; patient = max | |
| endpoint | `NextBiopsyProgression_LGD2plus`: src/barrett/labels/lgd2.py derive_next_biopsy_lgd2plus: positive if next biopsy label >= HGD, or next biopsy = LGD and current LGD streak >= 1 (two consecutive LGD) | |
| eligibility | strict pre-event rows only: exclusion_counts {"": 707, "at_event": 183, "endpoint_not_evaluable": 38, "post_event": 31} | |
| evaluation | 5-fold patient-level, split_seed 20260713; nested inner CV per outer fold | |
| primary metric in the release | auprc_mean (AUROC used here) | |
| CNV representation | QDNAseq 50 kb bins -> arm-level features (features_arms.csv, 39 arm columns) + complexity cx | |
| depth | 0.4x stated in docs/NUMBERS.md (Leanne's slide, 6 Mar 2026); not verifiable from data here; read counts from the sequencing sheet summarised in item C; median reads per profile 21512922 (n 500 rows with a value) | |
| overlap with the discovery sample sheet | 504 of 707 rows' CNV ids are in the 777-sample discovery sheet; 203 in the 268-sample validation sheet | |
| code identity | release built at pipeline commit `5cfbf0cd8f6c`; fold models at `98ba86820b3a` | |

**Sources.** `results/closeout/closeout_main.json` · `scripts/closeout/co_main.py` · commit 602a40e; `<release>/cohort_release_metadata.json`, `split_release_metadata.json`, `tasks_chapter1_lgd2_final.json`; `multimodal-barretts-progression/src/barrett/labels/lgd2.py` (cluster).

**Caveats.** The depth of 0.4× is a statement in the project's documents, not a value computed from the BAMs; read counts are from the sequencing sheet and read length is not recorded.

### M. Calibration and clinical comparators
**Question.** Calibration, Brier and net benefit for image-only, image + CNV and with head; is p53 IHC available and does the head add to it?

**Status.** DONE.

**Result: calibration and Brier** (150 patients, 50 events; prevalence 0.333).

| arm | AUROC | mean predicted | calibration slope | intercept (at fitted slope) | calibration-in-the-large | Brier |
|---|---|---|---|---|---|---|
| image_only_prob | 0.731 | 0.549 | 0.616 | -0.992 | -0.888 | 0.245 [0.206, 0.287] |
| late_mean_prob_release | 0.774 | 0.375 | 1.780 | +0.104 | -0.180 | 0.184 [0.162, 0.207] |
| fuse2_z_plattCV | 0.777 | 0.239 | 1.292 | +0.872 | +0.464 | 0.189 [0.152, 0.225] |
| fuse3_head_z_plattCV | 0.845 | 0.246 | 1.720 | +1.338 | +0.428 | 0.168 [0.132, 0.204] |
| head_prob | 0.753 | 0.749 | 1.060 | -2.187 | -1.785 | 0.360 [0.319, 0.401] |

**Result: decision-curve net benefit** (per patient; treat-none = 0).

| threshold | image_only_prob | late_mean_prob_release | fuse2_z_plattCV | fuse3_head_z_plattCV | head_prob | treat all |
|---|---|---|---|---|---|---|
| 0.1 | +0.262 | +0.260 | +0.271 | +0.277 | +0.259 | +0.259 |
| 0.15 | +0.227 | +0.220 | +0.242 | +0.250 | +0.216 | +0.216 |
| 0.2 | +0.183 | +0.197 | +0.190 | +0.215 | +0.167 | +0.167 |
| 0.25 | +0.144 | +0.156 | +0.124 | +0.178 | +0.111 | +0.111 |
| 0.3 | +0.100 | +0.135 | +0.135 | +0.160 | +0.048 | +0.048 |
| 0.35 | +0.074 | +0.119 | +0.111 | +0.125 | -0.026 | -0.026 |
| 0.4 | +0.033 | +0.109 | +0.104 | +0.091 | -0.109 | -0.111 |
| 0.45 | -0.007 | +0.098 | +0.077 | +0.089 | -0.202 | -0.212 |
| 0.5 | -0.040 | +0.053 | +0.053 | +0.080 | -0.320 | -0.333 |

fused arms are z-score means with no probability scale; fuse2/fuse3 are put on a probability scale by a Platt logistic fitted on the other four outer folds (CV), then max over rows; image_only and late_mean are release probabilities.

**Result: p53 IHC.** Available for a subset: slide_matching.csv p53IHC per slide (normal/aberrant/blank); patient = aberrant if any release slide aberrant, normal if any normal and none aberrant. n patients with IHC 75, events 38, aberrant 16.

| arm (same 75 patients) | AUROC |
|---|---|
| p53 aberrant (binary) | 0.684 [0.602, 0.764] |
| head | 0.734 [0.607, 0.851] |
| p53 + head (rank mean) | 0.738 [0.610, 0.855]; Δ vs p53 [-0.044, +0.156] |
| image + CNV | 0.699 [0.574, 0.820] |
| image + CNV + p53 (rank mean) | 0.772 [0.663, 0.877]; Δ vs image + CNV [0.022, 0.143] |

**Method.** `co_main.py` block M: slope/intercept from a logistic regression of outcome on logit(p); calibration-in-the-large = logit(observed rate) − logit(mean p); Brier with patient bootstrap; net benefit = TP/n − FP/n × t/(1−t). rank-mean combination (no fitted weights) because a fitted combination on 150 patients would need its own CV.

**Sources.** `results/closeout/closeout_main.json` · `scripts/closeout/co_main.py` · commit 602a40e; p53 from `SWGCohort/slide_matching.csv` (cluster).

**Caveats.** The fused arms have no native probability; their calibration is that of a CV Platt map and is not comparable one-to-one with the release probabilities. The head's own probability is severely miscalibrated on SWG (mean predicted 0.749 against prevalence 0.333), consistent with item G. p53 IHC covers half the patients and is a research staining from the matching sheet, not a clinical result.

### N. ACE-B readiness
**Question.** Status of slides and CNV, plan for the 30 prevalent cases, frozen plan with checkpoint hashes.

**Status.** DONE (plan frozen); data NOT AVAILABLE.

**Result.**

| item | status |
|---|---|
| ACE-B slides on the cluster | none (`/mnt/scratche/fast/fmlab/datasets/imaging/` has no ACE-B directory; only `phd/aceb_meta/` metadata from May 2026) |
| ACE-B features | none |
| ACE-B CNV tables or BAMs | none on the cluster |
| depth, SWG | 0.4× as stated in project documents (not verified from data; sheet read counts in item C) |
| depth, ACE-B | ~7× per the cohort owner (docs/NUMBERS.md §25); no file to verify |
| the 30 prevalent HGD/IMC cases | excluded from the primary progression analysis; analysed as a separate secondary "prevalent detection" set (plan §3). Previously the plan in `docs/NUMBERS.md` §25 said "optionally 5–10 prevalent HGD/IMC" for imaging without stating how they enter the analysis; this is now written down. |
| frozen plan | `docs/aceb_analysis_plan.md`, committed at `0aaa824` before any ACE-B slide exists; checkpoint hashes in `results/closeout/aceb_checkpoint_hashes.json` (`scripts/closeout/co_checkpoint_hashes.py`), e.g. image_only fold1 `105c29f411ff2db9…`, 68 files hashed |

**Sources.** `docs/aceb_analysis_plan.md`; `results/closeout/aceb_checkpoint_hashes.json`; `docs/NUMBERS.md` §25; `docs/status_ledger_2026-09-24.md` items 2, 11, 12, 21.

**Caveats.** The plan's CNV step assumes read-level data can be down-sampled; if only the owner's arm table arrives, the depth shift is declared, not corrected. With ~11 progressors the plan states in advance that the fusion-vs-image comparison is under-powered.

## 4. Discrepancies found
1. **Selection-adjusted p.** `results/numbers/p32_checks.json` and the digest report 0.022, adjusting over the 6 pass-2 fields only. Adjusting over every third arm that was evaluated (28) gives 0.069 (item I). The 0.022 is correct for what it adjusts over; it is not the fully adjusted value.
2. **Digest row 16 wording.** The digest attributes "+0.063 [+0.020, +0.107]" to the leak-free head "alone"; that value is the 2-field CV-logistic fusion (v3). The leak-free grade-head fusion is +0.067 [0.022, 0.114] (v4). Both numbers are correct; the label was wrong.
3. **"33 overlap patients excluded".** The digest and project log say 33 patients were excluded; the exclusion file lists all 55 linked ERIN identities (all 54 SWG patients). 33 is the number of SWG patients that had a case in training; the exclusion was wider (item B).
4. **P32 ERIN field CIs** used 1,000 resamples, not the 2,000 stated as the convention elsewhere; recomputed values differ by ≤ 0.002 (item J).
5. **Sanity gate.** The digest (§5, "Mechanism check") reports 0.619 and 0.629 for the pass-2 head; the canonical leak-free head scores 0.597 / 0.606, lower, and this was not previously reported (item G).
6. **Killcoyne comparison doc** in the pipeline repository (`reports/scientific_hardening/killcoyne_protocol_comparison.md`) states "69/150 local patients are Killcoyne-discovery PSIDs"; by CNV id, 504 of 707 rows are in the discovery sheet, i.e. 82 of 150 patients by modal sheet (item C). Not reconciled here; both counts are reported.
7. **First-run labelling error in item E secondary analysis** (own error, corrected at `4af24d5` before reporting; see item E).
8. **Digest "nothing pending"** (§6): item H (non-grade control) had been listed in the P32 log as "Next (not run)" and was not run until this closeout.

## 5. Not done
- Sequencing depth in × (read length not recorded; BAM-based depth not computed: no samtools/pysam in the environment, 1,035 BAMs unindexed).
- Staining batch (no record exists).
- 4× CNV (no data exists; question to the cohort owner open since 24 Sep).
- Killcoyne 2020 column of item L (left to the author by instruction).
- A second pathologist read for item G (none exists).
- Referral pathway beyond the DB referral-hospital field; sex for the 84 patients absent from the demographics sheet (gender code reported instead).
- ACE-B itself (no data).

## 6. Pre-specification text as committed at `0aaa824` (verbatim)

> # Closeout for review: SWG fusion and the ERIN-transfer result
>
> **Status of this file: PRE-SPECIFICATION VERSION.** Written and committed before any new analysis in it was run (rule 8).
> Results are appended in a later commit without changing the text below the "Pre-specification" headings; if a specification
> had to change after seeing data, both versions are kept.
>
> ## 1. Header
> - Date: 25 September 2026.
> - Commit at start: `a23b483` (laptop and cluster clones identical).
> - Pre-specification commit: filled in on the results commit (the hash of the commit that adds this text).
> - Commit at end: pending.
> - New scripts: `scripts/closeout/co_checkpoint_hashes.py`, `scripts/closeout/co_swg_slide_meta.py`, `scripts/closeout/co_swg_cnv_qc.py`, `scripts/closeout/co_main.py`, `scripts/closeout/co_h_assemble.py`.
> - New result files (all under `results/closeout/`): `aceb_checkpoint_hashes.json`, `swg_slide_meta_summary.json`, `closeout_main.json`, `tables.md`, `h_nongrade_controls.json`, `tables_h.md`. Row-level tables (slide filenames, per-patient rows) stay on the cluster under `feasibility/closeout/` and are not committed.
> - New plan: `docs/aceb_analysis_plan.md`.
>
> ## Conventions applied to every item (rules 3 to 6)
> - Cohort: SWG frozen release `chapter1_lgd2_final_pre_event_20260713_final`: 707 rows (one slide + one CNV profile each), 150 patients, 50 progressor patients, 107 positive rows. Row label `y_progressor` = the next biopsy after this row is HGD+ or completes two consecutive LGD (code in item L).
> - Arm scores: release out-of-fold probabilities (`image_only`, `cnv_only`, outer folds `fold_id_rep01`), or an ERIN head's imputed probability per slide. Fused arms: mean of fold-local z-scores (z within each outer fold). Slide→patient aggregation: **max over the patient's rows**, for scores and for the label.
> - AUROC: rank-based, 3 decimals. CI: percentile bootstrap over patients, 2,000 resamples, `numpy.random.RandomState(0)`, resamples with one class skipped and redrawn. Permutation tests: 2,000 permutations of patient-level labels, `RandomState(0)`, p = (1 + #null ≥ observed)/(2,001).
> - Every table carries n patients and n events.
>
> ## Pre-specifications (written before running; scripts committed in the same commit)
>
> ### D. Interaction test
> - Subgroups: `also_in_ERIN` = SWG patients linked to an ERIN identity by the accession crosswalk and Barrett's-DB participant bridge (the set recomputed by `co_main.py` from `feasibility/closeout/erin_swg_pairs.csv`, expected 54); `never_in_ERIN` = the rest (expected 96). **This split was defined for the leakage check on 25 Sep 2026 and is a post-hoc subgroup analysis.**
> - Arms: canonical fusion (item A): image_only + cnv_only + leak-free ERIN grade head (`p32_head_noov`), fold-local z-mean; comparator image_only + cnv_only.
> - Statistic: gain_g = AUROC(fuse3) − AUROC(fuse2) within subgroup g; difference = gain_also − gain_never.
> - Bootstrap CI: 2,000 resamples of patients drawn **within each subgroup** (sizes preserved), seed 0, percentile 2.5/97.5.
> - Permutation (a): reassign subgroup membership at random preserving the two sizes; (b): reassign preserving sizes and the progressor count in each subgroup (permute within progressors and within non-progressors separately). 2,000 each, seed 0. Report two-sided p = (1 + #|null| ≥ |obs|)/(n_valid + 1) as primary and one-sided (null ≥ obs) as secondary. Permutations where a subgroup has one class are dropped and counted.
>
> ### G. Failed pre-registered sanity check
> - Pre-registration text is quoted verbatim from `docs/projects/P32_image_to_fields.md` at commit `128760e` (2026-09-24 17:50:13 +0100).
> - Observed value: recomputed as the slide-level AUROC of each head's imputed P(LGD+) on the 707 release rows against `pre_event_cohort.Label ≥ 2` (0 NDBE, 1 IND, 2 LGD; the 707 rows contain no HGD+), for the pass-1 (0.88 µm), pass-2 (`p32b_fields`), repeat-fold, permuted-label and leak-free (`p32_head_noov`) heads. Also against the Barrett's-DB confirmed code (`highestgradedysconf` mapped 2→NDBE, 3→IND, 4→LGD, 5→HGD, 6/8→cancer) on rows whose accession matches a DB report.
> - Source of the pathologist grade: `pre_event_cohort.GradeSource` distribution on the 707 rows is reported.
> - Second read: if any independent second pathologist read exists (release, SWGCohort folder, DB export `highestgradedysresearch`, `specimen_pairs.swg_grade_code`), inter-read agreement (two-tier accuracy, Cohen's kappa, AUROC of read A as a score for read B) and head vs each read on the same rows are computed; if not, this is stated. The LLM jury grade of the clinical report is reported separately and labelled as not a pathologist read.
>
> ### H. Non-grade ensemble control (new training)
> - Heads: ERIN ABMIL heads for `treatment_effect` (P31 v2 field, yes/no) and `im_present` (intestinal metaplasia present vs absent), the two non-grade fields with the highest ERIN visibility in P32 that are at or near chance for SWG progression alone (pass-2 single-field AUROCs 0.556 and 0.385). A third head: `grade_LGDplus` with labels permuted (PERM_SEED 7) on the same leak-free set, the shuffled-label control on equal footing.
> - Training set: identical to the leak-free grade head: `scripts/projects/p32_fields_from_image.py` with `EXCLUDE_PATIENTS=feasibility/erin_fusion/erin_swg_overlap_anon_ids.txt` (55 ERIN ids → 2,249 cases), `P31DIR=feasibility/runs/p31_validate_v2/output`, `SWG_FEATS=SWGCohort/features_uni2h_05um` (0.5 µm/px), `FOLD_SEED 0`, seeds 0–2, 25 epochs, Adam 1e-4, 800-tile subsample, class-weighted BCE, ≤1,500 tiles per bag. Nothing tuned. Run names `co_h_treat_noov`, `co_h_im_noov`, `co_h_perm_noov`.
> - Transfer: seed-0 fold models averaged per SWG slide (as for the grade head). Report per head: ERIN OOF AUROC, head alone on SWG progression, fuse2 (image + CNV), fuse3 (image + CNV + head), gain with CI and permutation p; side by side with the leak-free grade head and both permuted-label heads (`p32_head_perm`, incl-overlap; the new leak-free one). Script `scripts/closeout/co_h_assemble.py`.
> - Pre-stated reading rule (not a prediction of outcome): if a non-grade head's gain has a CI excluding zero of similar size to the grade head's, the gain is attributable to ERIN-supervised image representation rather than to grade content.
>
> ### C. Subgroup characterisation
> - Per-patient variables from: release cohort table (rows, first year, span, baseline grade = grade of the earliest row, max grade, biopsies total, endpoint label reached, follow-up to last biopsy, days first row → endpoint biopsy), `SWGCohort/Demographics_full.csv` (sex, age at diagnosis, Prague C/M, smoking; 66 of 150 patients), `barretts_database_230809.csv` gender code (149), DB export first-endoscopy referral hospital, sequencing sheets (discovery 777 / validation 268 membership, Leanne batch, SLX run, read count, cellularity, sheet p53), QDNAseq 50 kb QC per profile (`co_swg_cnv_qc.py`: bins, MAPD noise, sd, segments, fraction altered), release `cx`, slide scanner properties (`co_swg_slide_meta.py`: model, serial, source lens, mpp, scan date; slide age at scan = scan date − biopsy date), `slide_matching.csv` p53 IHC. Patient value = mean (continuous) or mode (categorical) over the patient's rows.
> - Tests: Mann-Whitney U (continuous), Fisher exact (2×2), chi-square where a categorical has more than two levels (labelled). Per-subgroup AUROCs with within-subgroup bootstrap CIs for cnv, image, head, fuse2, fuse3. CNV-only within strata (sequencing sheet, SLX run, Leanne batch, read-count tertile) × subgroup where n ≥ 10 and events ≥ 1 (CI when events ≥ 3).
>
> ### E. Prevalent vs future disease
> - Interval per progressor patient = earliest release row date → endpoint biopsy date, where the endpoint biopsy date = date of the earliest positive row + its `DaysToNextBiopsy`. Secondary: `DaysFromCurrentToEvent` minimum. Histogram bins 0–6, 6–12, 12–24, 24–36, 36–60, >60 months.
> - Exclusion runs: drop progressor patients with interval ≤ 183 d, then ≤ 365 d; recompute head, fuse2, fuse3 and gain. Secondary (labelled): drop positive rows with `DaysToNextBiopsy` ≤ 183 / 365 while keeping the patient's other rows.
>
> ### F. Baseline grade
> - List the release model families; state whether any clinical arm exists. Grade arms: CV logistic (release folds) on the row grade (0/1/2) alone, and with `MaxPathologySoFar`; each fused with the head; plus fuse2 + grade and fuse3 + grade. Within baseline-NDBE patients (two definitions: earliest row NDBE; all rows NDBE): head, fuse2, fuse3, image, cnv, gain.
>
> ### I. Selection across P32 fields
> - Candidate third arms = every arm ever fused with image + CNV on SWG (pass-1 13 single fields at 0.88 µm and their all-field logistic; pass-2 6 single fields at 0.5 µm, their all-field logistic and 6 leave-one-out logistics; rep02 image ensemble control). Null: max over candidates of (AUROC fuse3 − AUROC fuse2) under patient-label permutation (2,000, seed 0). Report p for the observed maximum and the same null applied to the canonical gain. Fusion rule fixed before results (P32 pre-registration), so not maximised over.
>
> ### M. Calibration and clinical comparators
> - Patient-level probabilities: image_only (release), late_mean (release, mean of probabilities); fuse2 and fuse3 z-means mapped to probabilities by a Platt logistic fitted on the other four outer folds (CV), then max over rows. Calibration slope and intercept (logistic of outcome on logit p), calibration-in-the-large (logit observed − logit mean predicted), Brier with CI, net benefit at thresholds 0.10–0.50 step 0.05 with treat-all and treat-none.
> - p53 IHC: `slide_matching.csv` p53IHC (normal/aberrant/blank); patient aberrant if any release slide aberrant. AUROC of p53, of the head, and of their rank-mean, on patients with IHC; paired deltas.
>
> ### K, L, J, B, A
> - K: assertions run in `co_main.py` (each SWG patient in exactly one outer fold for rep01 and rep02; inner folds keyed by patient; `patient_folds` for every ERIN task table and for the P32 head table gives no patient in two folds).
> - L: our definitions from `cohort_release_metadata.json`, `split_release_metadata.json`, `tasks_chapter1_lgd2_final.json`, `src/barrett/labels/lgd2.py`; the other column left blank. 4× data: searched locations listed.
> - J: resampling unit, n and seed for each CI in the digest read from the generating scripts; P32 ERIN field CIs recomputed at 2,000 (source used 1,000).
> - B: membership of each linked SWG patient's ERIN cases in every P32 training table (`feasibility/closeout/swg_overlap_training_membership.csv`).
> - A: the four reported versions recomputed from the OOF and imputed tables; canonical declared in the results section with the reason.
>
> (Results sections follow in the results commit.)
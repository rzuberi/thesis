# Closeout for review: SWG fusion and the ERIN-transfer result

**Status of this file: PRE-SPECIFICATION VERSION.** Written and committed before any new analysis in it was run (rule 8).
Results are appended in a later commit without changing the text below the "Pre-specification" headings; if a specification
had to change after seeing data, both versions are kept.

## 1. Header
- Date: 25 September 2026.
- Commit at start: `a23b483` (laptop and cluster clones identical).
- Pre-specification commit: filled in on the results commit (the hash of the commit that adds this text).
- Commit at end: pending.
- New scripts: `scripts/closeout/co_checkpoint_hashes.py`, `scripts/closeout/co_swg_slide_meta.py`, `scripts/closeout/co_swg_cnv_qc.py`, `scripts/closeout/co_main.py`, `scripts/closeout/co_h_assemble.py`.
- New result files (all under `results/closeout/`): `aceb_checkpoint_hashes.json`, `swg_slide_meta_summary.json`, `closeout_main.json`, `tables.md`, `h_nongrade_controls.json`, `tables_h.md`. Row-level tables (slide filenames, per-patient rows) stay on the cluster under `feasibility/closeout/` and are not committed.
- New plan: `docs/aceb_analysis_plan.md`.

## Conventions applied to every item (rules 3 to 6)
- Cohort: SWG frozen release `chapter1_lgd2_final_pre_event_20260713_final`: 707 rows (one slide + one CNV profile each), 150 patients, 50 progressor patients, 107 positive rows. Row label `y_progressor` = the next biopsy after this row is HGD+ or completes two consecutive LGD (code in item L).
- Arm scores: release out-of-fold probabilities (`image_only`, `cnv_only`, outer folds `fold_id_rep01`), or an ERIN head's imputed probability per slide. Fused arms: mean of fold-local z-scores (z within each outer fold). Slide→patient aggregation: **max over the patient's rows**, for scores and for the label.
- AUROC: rank-based, 3 decimals. CI: percentile bootstrap over patients, 2,000 resamples, `numpy.random.RandomState(0)`, resamples with one class skipped and redrawn. Permutation tests: 2,000 permutations of patient-level labels, `RandomState(0)`, p = (1 + #null ≥ observed)/(2,001).
- Every table carries n patients and n events.

## Pre-specifications (written before running; scripts committed in the same commit)

### D. Interaction test
- Subgroups: `also_in_ERIN` = SWG patients linked to an ERIN identity by the accession crosswalk and Barrett's-DB participant bridge (the set recomputed by `co_main.py` from `feasibility/closeout/erin_swg_pairs.csv`, expected 54); `never_in_ERIN` = the rest (expected 96). **This split was defined for the leakage check on 25 Sep 2026 and is a post-hoc subgroup analysis.**
- Arms: canonical fusion (item A): image_only + cnv_only + leak-free ERIN grade head (`p32_head_noov`), fold-local z-mean; comparator image_only + cnv_only.
- Statistic: gain_g = AUROC(fuse3) − AUROC(fuse2) within subgroup g; difference = gain_also − gain_never.
- Bootstrap CI: 2,000 resamples of patients drawn **within each subgroup** (sizes preserved), seed 0, percentile 2.5/97.5.
- Permutation (a): reassign subgroup membership at random preserving the two sizes; (b): reassign preserving sizes and the progressor count in each subgroup (permute within progressors and within non-progressors separately). 2,000 each, seed 0. Report two-sided p = (1 + #|null| ≥ |obs|)/(n_valid + 1) as primary and one-sided (null ≥ obs) as secondary. Permutations where a subgroup has one class are dropped and counted.

### G. Failed pre-registered sanity check
- Pre-registration text is quoted verbatim from `docs/projects/P32_image_to_fields.md` at commit `128760e` (2026-09-24 17:50:13 +0100).
- Observed value: recomputed as the slide-level AUROC of each head's imputed P(LGD+) on the 707 release rows against `pre_event_cohort.Label ≥ 2` (0 NDBE, 1 IND, 2 LGD; the 707 rows contain no HGD+), for the pass-1 (0.88 µm), pass-2 (`p32b_fields`), repeat-fold, permuted-label and leak-free (`p32_head_noov`) heads. Also against the Barrett's-DB confirmed code (`highestgradedysconf` mapped 2→NDBE, 3→IND, 4→LGD, 5→HGD, 6/8→cancer) on rows whose accession matches a DB report.
- Source of the pathologist grade: `pre_event_cohort.GradeSource` distribution on the 707 rows is reported.
- Second read: if any independent second pathologist read exists (release, SWGCohort folder, DB export `highestgradedysresearch`, `specimen_pairs.swg_grade_code`), inter-read agreement (two-tier accuracy, Cohen's kappa, AUROC of read A as a score for read B) and head vs each read on the same rows are computed; if not, this is stated. The LLM jury grade of the clinical report is reported separately and labelled as not a pathologist read.

### H. Non-grade ensemble control (new training)
- Heads: ERIN ABMIL heads for `treatment_effect` (P31 v2 field, yes/no) and `im_present` (intestinal metaplasia present vs absent), the two non-grade fields with the highest ERIN visibility in P32 that are at or near chance for SWG progression alone (pass-2 single-field AUROCs 0.556 and 0.385). A third head: `grade_LGDplus` with labels permuted (PERM_SEED 7) on the same leak-free set, the shuffled-label control on equal footing.
- Training set: identical to the leak-free grade head: `scripts/projects/p32_fields_from_image.py` with `EXCLUDE_PATIENTS=feasibility/erin_fusion/erin_swg_overlap_anon_ids.txt` (55 ERIN ids → 2,249 cases), `P31DIR=feasibility/runs/p31_validate_v2/output`, `SWG_FEATS=SWGCohort/features_uni2h_05um` (0.5 µm/px), `FOLD_SEED 0`, seeds 0–2, 25 epochs, Adam 1e-4, 800-tile subsample, class-weighted BCE, ≤1,500 tiles per bag. Nothing tuned. Run names `co_h_treat_noov`, `co_h_im_noov`, `co_h_perm_noov`.
- Transfer: seed-0 fold models averaged per SWG slide (as for the grade head). Report per head: ERIN OOF AUROC, head alone on SWG progression, fuse2 (image + CNV), fuse3 (image + CNV + head), gain with CI and permutation p; side by side with the leak-free grade head and both permuted-label heads (`p32_head_perm`, incl-overlap; the new leak-free one). Script `scripts/closeout/co_h_assemble.py`.
- Pre-stated reading rule (not a prediction of outcome): if a non-grade head's gain has a CI excluding zero of similar size to the grade head's, the gain is attributable to ERIN-supervised image representation rather than to grade content.

### C. Subgroup characterisation
- Per-patient variables from: release cohort table (rows, first year, span, baseline grade = grade of the earliest row, max grade, biopsies total, endpoint label reached, follow-up to last biopsy, days first row → endpoint biopsy), `SWGCohort/Demographics_full.csv` (sex, age at diagnosis, Prague C/M, smoking; 66 of 150 patients), `barretts_database_230809.csv` gender code (149), DB export first-endoscopy referral hospital, sequencing sheets (discovery 777 / validation 268 membership, Leanne batch, SLX run, read count, cellularity, sheet p53), QDNAseq 50 kb QC per profile (`co_swg_cnv_qc.py`: bins, MAPD noise, sd, segments, fraction altered), release `cx`, slide scanner properties (`co_swg_slide_meta.py`: model, serial, source lens, mpp, scan date; slide age at scan = scan date − biopsy date), `slide_matching.csv` p53 IHC. Patient value = mean (continuous) or mode (categorical) over the patient's rows.
- Tests: Mann-Whitney U (continuous), Fisher exact (2×2), chi-square where a categorical has more than two levels (labelled). Per-subgroup AUROCs with within-subgroup bootstrap CIs for cnv, image, head, fuse2, fuse3. CNV-only within strata (sequencing sheet, SLX run, Leanne batch, read-count tertile) × subgroup where n ≥ 10 and events ≥ 1 (CI when events ≥ 3).

### E. Prevalent vs future disease
- Interval per progressor patient = earliest release row date → endpoint biopsy date, where the endpoint biopsy date = date of the earliest positive row + its `DaysToNextBiopsy`. Secondary: `DaysFromCurrentToEvent` minimum. Histogram bins 0–6, 6–12, 12–24, 24–36, 36–60, >60 months.
- Exclusion runs: drop progressor patients with interval ≤ 183 d, then ≤ 365 d; recompute head, fuse2, fuse3 and gain. Secondary (labelled): drop positive rows with `DaysToNextBiopsy` ≤ 183 / 365 while keeping the patient's other rows.

### F. Baseline grade
- List the release model families; state whether any clinical arm exists. Grade arms: CV logistic (release folds) on the row grade (0/1/2) alone, and with `MaxPathologySoFar`; each fused with the head; plus fuse2 + grade and fuse3 + grade. Within baseline-NDBE patients (two definitions: earliest row NDBE; all rows NDBE): head, fuse2, fuse3, image, cnv, gain.

### I. Selection across P32 fields
- Candidate third arms = every arm ever fused with image + CNV on SWG (pass-1 13 single fields at 0.88 µm and their all-field logistic; pass-2 6 single fields at 0.5 µm, their all-field logistic and 6 leave-one-out logistics; rep02 image ensemble control). Null: max over candidates of (AUROC fuse3 − AUROC fuse2) under patient-label permutation (2,000, seed 0). Report p for the observed maximum and the same null applied to the canonical gain. Fusion rule fixed before results (P32 pre-registration), so not maximised over.

### M. Calibration and clinical comparators
- Patient-level probabilities: image_only (release), late_mean (release, mean of probabilities); fuse2 and fuse3 z-means mapped to probabilities by a Platt logistic fitted on the other four outer folds (CV), then max over rows. Calibration slope and intercept (logistic of outcome on logit p), calibration-in-the-large (logit observed − logit mean predicted), Brier with CI, net benefit at thresholds 0.10–0.50 step 0.05 with treat-all and treat-none.
- p53 IHC: `slide_matching.csv` p53IHC (normal/aberrant/blank); patient aberrant if any release slide aberrant. AUROC of p53, of the head, and of their rank-mean, on patients with IHC; paired deltas.

### K, L, J, B, A
- K: assertions run in `co_main.py` (each SWG patient in exactly one outer fold for rep01 and rep02; inner folds keyed by patient; `patient_folds` for every ERIN task table and for the P32 head table gives no patient in two folds).
- L: our definitions from `cohort_release_metadata.json`, `split_release_metadata.json`, `tasks_chapter1_lgd2_final.json`, `src/barrett/labels/lgd2.py`; the other column left blank. 4× data: searched locations listed.
- J: resampling unit, n and seed for each CI in the digest read from the generating scripts; P32 ERIN field CIs recomputed at 2,000 (source used 1,000).
- B: membership of each linked SWG patient's ERIN cases in every P32 training table (`feasibility/closeout/swg_overlap_training_membership.csv`).
- A: the four reported versions recomputed from the OOF and imputed tables; canonical declared in the results section with the reason.

(Results sections follow in the results commit.)

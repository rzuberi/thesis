# Status ledger for the 38-item post-talk list (24 September 2026)

One line per item: what was done, the number if there is one, the source file, and what is still open.
"RUNNING" items have jobs on the cluster; their numbers are appended in §Results when they land.
Questions for people are drafted, ready to paste, in `docs/questions_for_people_2026-09-24.md`.

## 1. Facts to confirm

| # | Item | Status | Answer / where |
|---|---|---|---|
| 1 (T) | LGD2+ definition | **Answered from code** | Two consecutive LGD **biopsies** in the patient's timeline, not two reads of one biopsy. `src/barrett/labels/lgd2.py`: event when `CurrentGradeInt >= 3` (HGD/IMC/OAC) or `CurrentGradeInt == 2 and LGDStreakSoFar >= 2`; next-biopsy endpoint positive when the next biopsy is HGD+ or is LGD with the current streak already >= 1. `configs/chapter1_lgd2_final_analysis.yaml` locks `event_rule: two_consecutive_lgd`. Note: the database's canonical EventDate uses an LGDx3 rule and is explicitly *not* used for eligibility (`17_build_lgd2_pre_event_cohort.py`). |
| 2 (T) | SWG 4x resequencing | **No record** | Only depth statements anywhere: SWG 0.4x / 50 kb (NUMBERS item 15; 6 March slides lines 174–176) and ACE-B ~7x (Rehan, 21 Sep). Searched repo markdown, LaTeX, plan, DATASETS.md, slides text. Question to Leanne drafted. |
| 3 (T) | Multi-slide biopsies in the release | **Answered from code** | One **slide = one modelling unit** (`SampleID`; `matched_cohort.py`: "one slide/sample = one modelling unit"). 707 units = 707 distinct slides from 359 distinct biopsies (180 biopsies with 1 slide, 77 with 2, 102 with >= 3). CNV is per biopsy, so 26 of 707 units share a CNV profile with another slide of the same biopsy (`matched_manifest.csv`, `cnv_shared_with_other_sample`), flagged not dropped. Patient-level numbers take max over all a patient's slides. |
| 4 (T) | Who produced SWG grades | Question drafted (Leanne) | The spreadsheet column `Pathology` in `sWGS_777_samples_cleaned_202401_Leanne_fullDetails.xlsx`; provenance unknown to us. |
| 5 (T) | Permission to show a report | Question drafted (data owner) | File exists at `review/erin_example_report_item11.md`, laptop and cluster only. |
| 6 (T) | MedGemma 0.50 slide set | **Answered from code** | `scripts/task_patch_vlm_pilot.py`: 100 dual-labelled ERIN slides from `erin_slide_labels_v2.csv`, stratified 16 per section grade (NORMAL_OTHER, NDBE, IND, LGD, HGD, CANCER), `random_state = 7`; 96 scored; 8 highest-attention tiles each from the section-trained ABMIL. A subset of the 1,538 CONCH slides, truth = section grade. |
| 7 | Non-progressor matching | Question drafted (Leanne) | |
| 8 | Overlap with Killcoyne 2020 | Question drafted (Leanne / Fitzgerald lab) | |
| 9 | ERIN selection and acronym | Question drafted (data exporter) | Nothing in any file states the selection rule or the acronym. |
| 10 | Published progression rate | **Done** | NDBE → adenocarcinoma 0.33 per 100 person-years (Desai 2012, Gut, meta-analysis); confirmed LGD 9.1 %/yr vs 0.6 %/yr after downstaging (Duits 2015, Gut). Links in the questions doc. |
| 11 | ACE-B 294 vs 234 | Reconciled as far as our files allow; question drafted | 134 = official cases with Seattle histology and a trial date (of 153 study numbers); the workbook we hold has 234 sample rows (233 names, 101 PS accession bases); 294 is Leanne's count and no 294-row list exists here. |
| 12 | ACE-B scanning | Question drafted (histopathology core) | Includes the 7 unreadable ERIN files for re-export. |

## 2. Barrett's robustness checks

| # | Item | Status | Result / where |
|---|---|---|---|
| 13 | Second CV repeat | **Done, replicates** (see §Results 13) | New patient-stratified split (seed 20260924; only 22.6 % of rows keep their rep01 fold id) in a sibling release dir `..._rep02`; the release trainer `24_run_lgd2_final_outer_fold.py` run unchanged. cnv_only 5/5 folds done; image_only, early_fusion, intermediate_fusion, coattention_fusion 5 folds each queued as cuda/h200 twins. Late fusion afterwards via `14_run_lgd2_late_fusion.py`. |
| 14 | Thresholds fixed on training folds | **Done** | `results/numbers/swg_robustness.json` item14. Threshold chosen on the other four folds' OOF, applied to the held-out fold. At target sens 0.95: image_only achieves sens 0.94 / spec 0.18 [0.11, 0.26], 129/150 flagged; late_mean 0.92 / 0.28 [0.19, 0.37], 118 flagged; late_stack 0.92 / 0.30 [0.21, 0.39]; intermediate 0.92 / 0.40 [0.30, 0.50], 106 flagged. At target spec 0.86: image_only sens 0.42 [0.28, 0.56] (spec 0.86 achieved), late_mean 0.48 [0.33, 0.62] at spec 0.85. Honest version is within a few points of the post-hoc table, slightly lower sensitivities. |
| 15 | Paired Brier CI, late_mean vs image_only | **Done** | Brier image_only 0.245 [0.206, 0.287]; late_mean 0.184 [0.162, 0.207]; **delta −0.061 [−0.095, −0.027]**, CI excludes zero. Late-stack −0.043 [−0.093, +0.008]; other fusions cross zero. `swg_robustness.json` item15. |
| 16 | Recalibration | **Done, partly negative** | Calibration slope before: image_only 0.62 (over-confident), late_mean 1.78 (under-confident), late_stack 1.63. Platt scaling fitted on the other folds and applied within CV: image_only Brier 0.245 → 0.202 (delta CI [−0.079, −0.007], real gain) but slope only 0.71 and AUROC falls 0.731 → 0.699 because the fold-wise fits disagree; late_mean Brier 0.184 → 0.191 (no gain, [−0.008, +0.022]), slope 0.71. Simple Platt fixes the over-confident arm's Brier and does not fix under-confidence; with 30 training positives per fold the recalibrator is itself noisy. Quote absolute risks only for late_mean, and with the under-confidence stated. |
| 17 | Detection-intensity confound | **Done, negative** | Excluding the 64 samples taken <= 183 d after the previous biopsy (685 of 707 kept) changes nothing: image_only 0–12 m 0.830 → 0.831, 12–36 m 0.516 → 0.490, > 36 m 0.804 → 0.806; horizons move by <= 0.014. The near-event advantage is not explained by repeat-biopsy sampling. `swg_robustness.json` item17. |
| 18 | 12–36 month window | **Done** | 29 progressor samples from 13 patients. They are not obviously different in grade (mean grade code 0.72 vs 0.67 in 0–12 m and 1.58 in > 36 m) but the > 36 m window is dominated by LGD samples (19 of 24 grade 2) with 63 % first biopsies, which is why it scores high: the model is seeing prevalent dysplasia. The 12–36 m samples are mostly NDBE (18/29), median 438 d since previous biopsy, image_only median prob 0.34 vs 0.69 (0–12 m) and 0.64 (> 36 m). Reading: the "U-shape" is a grade-composition artefact of the windows, not a temporal property of the model. |
| 19 | CNV-as-text CIs and repeats | **Done** (see §Results 19) | CIs: `num_cnvtext_cis.py` running as a job (login-node run exceeded 500 s). Repeats: MedGemma-27B, temperature 0.7, seeds 1 and 2, with and without grade, 4 tasks as cuda/h200 twins. |
| 20 | Interpretability | Checklist written; needs a pathologist | `docs/interpretability_checklist_2026-09-24.md`, 11 maps in `review/swg_heatmaps/`. |

## 3. Pending runs

| # | Item | Status |
|---|---|---|
| 21 | ACE-B validation | Scaffold `scripts/aceb_validate.py` (fails closed until `ACEB_SLIDES`, `ACEB_CNV`, `ACEB_LABELS` exist); thresholds will come from `swg_operating_points_patient.json` and `swg_robustness.json` item14. |
| 22 | Deeper sequencing | Blocked on item 2: no deeper SWG data is known to exist. |

## 4. ERIN checks

| # | Item | Status | Result / where |
|---|---|---|---|
| 23 (T) | 79 cancer-boundary re-reads | Needs Rehan | Until spot-checked, all text says "LLM re-reads" (adjudicator column reads `claude_pending_rehan_spotcheck`). The 29 "yes" cases are in `labeller/adjudications.csv`. |
| 24 | Grade model within biopsies | **Done, small effect** | `results/numbers/grade_within_biopsy.json`. Case-max-trained ABMIL on the 1,538 dual-labelled slides, section truth: all 0.871 [0.842, 0.897]; **biopsy-only (1,429 slides) 0.865 [0.831, 0.896]**; resection-only (109 slides) 0.756; specimen type alone 0.558; delta all − biopsy-only [−0.002, +0.013]. Section-trained: 0.860 → 0.853. The grade model is not riding on specimen type. (The corpus-wide 2,153-slide figure 0.926 has no saved per-slide predictions to re-read; the dual-labelled subset is the check we can do.) |
| 25 | Over-grading audit, 30 reports | Pack ready for Rehan | `review/audit_item25_swg_overcalls.md` + `.csv`: 10 IND, 10 LGD, 10 HGD/cancer over-calls on pathologist-NDBE specimens, with the specimen-scoped report text and a verdict column (jury_right / pathologist_right / mapping_error / ambiguous). Of 184 over-calls in total: 113 IND, 43 LGD, 20 HGD, 8 cancer. |
| 26 | ACE-B HGD under-calls | Pack ready; **cause confirmed and re-scored** (see §Results 26) | `review/audit_item26_aceb_hgd_missed.md`. All 4 missed cases have gap 0 days and a **second report in the 120-day window that the jury graded HGD** (ACE-B/C/019, /078, /096, /109). The anchor matched the *closest* report, which was a benign one from the same visit; the HGD sits in the other report. This is a matching rule error, not a jury error: use the max grade over reports in the window, or the trial-tagged report. Re-running the anchor with max-over-window is a one-line change and would move HGD recall from 6/11 toward 10/11. |
| 27 | Pathologist grades | Needs Rehan | App relaunched 24 Sep, passphrase rotated; 0 grades. |
| 28 | Keep raw jury JSON | **Done** | `labeller/llm_grade_shard.py` now appends `{CaseName, model, raw, parsed_grade, ts}` to `<output>_raw_responses.jsonl` for every report. Committed. |
| 29 | CONCH on SWG: scale check | **Done: chance at every scale; not a scale artefact** (see §Results 29) | `scripts/task_conch_swg_scale.py`: same slides and tissue points at level 2 (~0.88 µm/px, what was used), level 1 (~0.44) and level 0 (~0.22); 128 tiles; all HGD+ and IND/LGD slides plus 40 NDBE. AUROC vs pathologist grade per scale. |
| 30a | T3 biopsy-only re-run | **Done, field effect survives** (see §Results 30a) | T3a_bio n 1,203 (116 pos), T3b_bio n 1,203 (62 pos); 30 image units + 2 tabular in the pull-worker queue; assembler `scripts/erin_fusion/assemble_bio.py`. |
| 30b | T4 confound with prior RFA/EMR | **Done, confound confirmed** | `results/numbers/t4_treatment_split.json`. Of 1,147 T4 units, 510 have an earlier report mentioning RFA/EMR/ablation, and 87 % of those are positive against 12 % of the rest. **The prior-therapy flag alone scores 0.874 [0.850, 0.896], above the image arm's 0.780.** Within units with no prior therapy (637, 75 positives) the image arm falls to 0.686 [0.610, 0.767]; with no therapy mentioned anywhere (612, 62 positives) to 0.645. The index report itself mentions therapy in 437 units (post-ablation neosquamous epithelium etc.), flag alone 0.813. **C26's T4 component should be withdrawn as "prior dysplasia leaves a trace"; what the image recognises is treated mucosa.** A residual 0.65–0.69 remains in untreated patients and is the honest number. |

## 5. New directions

| # | Item | Status | Result / where |
|---|---|---|---|
| 31 | Multi-field extraction | Not started; design note below | The v3 per-section jury already emits `site` and `specimen_type`; extending the schema to IM extent, inflammation and the pathologist's hedging is a prompt change plus a 50-report hand-checked set per field. Cost ≈ one jury campaign (≈ 110 GPU-h for sections v3). |
| 32 | Predict fields from image | Not started | Depends on 31. |
| 33 | Patch-level grading | Partly in hand | Tile-level classifiers exist (within 0.02–0.03 of ABMIL, better on six-class under section labels) and the tile grade maps for 12 slides; extending to all 1,538 slides is a queue job. |
| 34 | Fix the jury's over-grading | **Done, mostly negative** | `results/numbers/jury_recalibration.json`, 5-fold CV by report on 625 SWG specimens. Majority: two-tier 0.821, over-call rate on pathologist-NDBE 0.375, LGD+ sensitivity 0.96. Dropping the 3 worst jurors (llama3.1-8B, deepseek-r1-14B, gemma3-27B): two-tier 0.822, over-call 0.294, sensitivity 0.93. Vote-threshold rules: best two-tier 0.827 at "LGD+ needs 7/8", sensitivity 0.86. Multinomial logistic on votes: over-call 0.17 but sensitivity 0.66. **No rule improves two-tier agreement by more than 0.006; over-calling can only be bought with sensitivity.** Applied to ACE-B the chosen rule gives 0.909 vs 0.900. The over-grading is in the text-versus-re-read gap, not in the aggregation. |
| 35 | Do image models over-grade the same specimens? | **Done, no evidence** | `results/numbers/image_vs_jury_overgrading.json`. 129 release slides link uniquely to a DB specimen pair. Among 82 pathologist-NDBE specimens, CONCH P(LGD+) median 0.078 where the jury over-called vs 0.051 where it agreed, Mann-Whitney p 0.57, AUROC 0.54; Spearman between image residual and jury over-call 0.08 (p 0.38). No sign the label bias has passed into the image score, with the caveat that CONCH is a weak grader on SWG (item 29). |
| 36 | MedGemma-27B alone vs anchors | **Already computed** | `results/numbers/anchor_eval.json`: vs SWG pathologist exact 0.632 / two-tier 0.775 / QWK 0.591 (n 623); vs ACE-B 0.865 / 0.910 / 0.752 (n 111). Slightly higher exact agreement than the jury on SWG, lower two-tier; equal-or-better on ACE-B. |
| 37 | Image + text on a non-report label | **Done, fusion not shown** (see §Results 37–38) | `scripts/task_swg_text_arm.py`: pathologist grade (release `Label >= 2`) as target; text arm = nomic embedding of the matched clinical report, image arm = ABMIL on release UNI2 tiles, late fusion; release folds. |
| 38 | Report text as SWG's third modality | **Done: embedding null, jury grade ≈ pathologist grade** (see §Results 37–38) | 428 of 707 release samples (65 of 150 patients, 96 of 127 progressor samples) match a Barrett's-DB report by accession stem. Text arm for progression + 3-way late fusion vs 2-way on the same subset. |

## Results appended when jobs landed (24 Sep, 15:00–19:30)

### 13. Second CV repeat — `results/numbers/swg_rep02.json`, `swg_rep02_selection.json`
New patient-stratified split (seed 20260924; 22.6 % of rows keep their rep01 fold), the release trainer run unchanged for
cnv_only, image_only, early_fusion, intermediate_fusion, coattention_fusion (25 folds, 0 failures). The release's
`late_mean` is the plain mean of the image and CNV probabilities (verified: correlation 1.000 with its OOF).

| arm | rep01 AUROC | rep01 Δ vs image | rep02 AUROC | rep02 Δ vs image |
|---|---|---|---|---|
| image_only | 0.731 [0.640, 0.814] | — | 0.745 [0.660, 0.827] | — |
| cnv_only | 0.663 | −0.068 [−0.197, +0.065] | 0.708 | −0.037 [−0.151, +0.073] |
| early_fusion | 0.738 | +0.007 [−0.056, +0.067] | 0.788 | +0.043 [−0.029, +0.119] |
| intermediate_fusion | 0.741 | +0.010 [−0.053, +0.067] | 0.767 | +0.022 [−0.036, +0.079] |
| coattention_fusion | 0.739 | +0.008 [−0.072, +0.094] | 0.768 | +0.023 [−0.036, +0.086] |
| **late_mean (release construction)** | 0.774 | **+0.043 [+0.014, +0.071]** | 0.787 | **+0.042 [+0.019, +0.069]** |
| late_mean, fold-local z (ours) | 0.783 | +0.051 [−0.022, +0.118] | 0.830 | +0.085 [+0.034, +0.137] |

Label-permutation p for the release late_mean vs image: rep01 0.0025, rep02 0.001. Selection-adjusted (max over the five
fusion arms): rep01 0.225, rep02 0.024. **Reading:** the arm chosen on rep01 was fixed before rep02 existed, so rep02 is a
pre-specified replication and needs no selection adjustment: the +0.04 late-fusion advantage replicates in size and sign
on a second split. The single-model fusions stay at +0.01 to +0.04 on both splits. Split-to-split movement is +0.01 to
+0.05 per arm, the same size as the effect, which is the case for more than one repeat. Caveat: both repeats re-partition
the same 150 patients; this is replication of the procedure, not new data. C1 can move from "exploratory" to
"replicated across two CV repeats, selection-adjusted on the first only".

### 19. CNV-as-text CIs and repeats — `results/numbers/cnvtext_cis.json`
| run | patient AUROC [CI] | Δ vs grade-as-score (0.687) | Δ vs trained CNV model (0.663) |
|---|---|---|---|
| MedGemma-27B, grade in prompt, T=0 | 0.750 [0.662, 0.832] | +0.06 [−0.040, +0.161] | +0.09 [−0.006, +0.187] |
| … seed 1, T=0.7 | 0.756 [0.669, 0.837] | [−0.035, +0.169] | [−0.003, +0.195] |
| … seed 2, T=0.7 | 0.748 [0.657, 0.829] | [−0.044, +0.160] | [−0.013, +0.190] |
| MedGemma-27B, CNV only, T=0 | 0.645 [0.548, 0.738] | [−0.168, +0.078] | [−0.112, +0.075] |
| … seed 1 / seed 2 | 0.647 / 0.642 | | |
| qwen3-32B, grade in prompt | 0.725 [0.640, 0.802] | [−0.078, +0.153] | [−0.028, +0.155] |

Stable to 0.01 across seeds. Grade+CNV text sits 0.09 above the trained CNV model with an interval that just touches zero
on all three seeds; CNV-only text is indistinguishable from the trained model. The qwen CNV-only run (109 rows) is skipped
as degenerate.

### 29. CONCH tile scale — FINAL, `results/numbers/conch_swg_scale.json`
80 SWG release slides (40 NDBE, 20 IND, 20 LGD; the pre-event cohort has no HGD), 128 tiles each, same tissue points read
at three scales. AUROC for pathologist LGD vs the rest, mean P(LGD+): 0.22 µm/px **0.559**, 0.44 µm/px **0.468**,
0.88 µm/px (the scale used before) **0.442**. Chance at every scale; the level-0 minus level-2 difference is +0.10 with a
bootstrap interval spanning zero. CONCH never emits "LGD" as a tile argmax on LGD slides at any scale (0 %); it spreads them
over NDBE, IND, cancer and normal. **Scale is not the explanation for the weak SWG result.** CONCH's prompt vocabulary has no
working low-grade-dysplasia concept on this material, and its ERIN 0.78 rests on separating cancer/HGD from benign, not
LGD. Do not use CONCH anywhere LGD is the target without a supervised head.

### 30a. T3 biopsy-only — `results/numbers/erin_t3_biopsy_only.json`
| task | n / pos | image AUROC [CI] | baseline | Δ image − baseline [CI] | original (all specimens) |
|---|---|---|---|---|---|
| T3a_bio field effect (LGD+) | 1,203 / 116 | 0.801 [0.751, 0.848] | 0.573 | +0.228 [+0.156, +0.298] | 0.821 vs 0.577, +0.244 |
| T3b_bio (HGD+) | 1,203 / 62 | 0.822 [0.764, 0.874] | 0.596 | +0.226 [+0.138, +0.317] | 0.869 vs 0.608, +0.261 |

**The field-effect signal survives removing resections**, losing 0.02–0.05 AUROC. Combined with 30b, C26 should now read:
field effect (T3) and HGD-within-a-year (T2b) stand; T4 "prior dysplasia" is withdrawn as treatment recognition.

### 37–38. SWG report text as a third modality — `results/numbers/swg_text_arm.json`, `swg_text_arm_jurygrade.json`
Matched subset: 428 slides, 65 patients (24 progressors). Embedding text arm (nomic) for progression: **0.43** [0.28, 0.58],
null; 3-way fusion 0.55 vs 2-way 0.59 on the same subset (image alone 0.61 here: the matched subset is harder than the
cohort). Jury *grade* of the same report as the text score: **0.669 [0.530, 0.800]**, against the pathologist's grade code
0.677, delta [−0.046, +0.029]; 3-way fusion with the jury grade 0.668 vs 2-way 0.593, [−0.037, +0.186]. Pathologist grade as
target (item 37): text 0.755 [0.686, 0.818], image ABMIL 0.670 [0.595, 0.741], fusion 0.731, fusion − best single
[−0.071, +0.023]. **Reading:** the LLM's structured read of a clinical report carries the same prognostic information as
the pathologist's code on a cohort with outcomes, and a raw text embedding carries none; fusion gains are not shown at
n = 65. The subset is too small to be a Chapter 1–2 bridge; the image-to-fields route (see the 24 Sep discussion) is how
to give all 150 patients a text modality.

### 26 follow-up. ACE-B anchor with max-over-window matching — `results/numbers/anchor_eval.json`, block `aceb_seattle_grade_maxwindow`
Closest-report rule (as before): two-tier 0.900, HGD recall 6/11. Max jury grade over every report within 120 d of trial
entry (the Seattle protocol's own logic; 66 cases have 2 reports in the window, 32 have 3–5): two-tier **0.856**, exact 0.811,
QWK 0.717; HGD recall **11/11** (8 HGD + 3 called cancer), LGD 8/9, cancer 3/3, but 15 of 83 NDBE cases over-called (7 LGD,
7 HGD). MedGemma-27B max-window: 0.865 / 0.820 / 0.737. Report both: the closest-report rule under-calls, the max rule
exposes the same over-calling seen on SWG (18 % of benign cases).

### Evening addition (Rehan: "have we fully extracted what we needed from the Barrett's database?") — `results/numbers/db_confirmed_grade_anchor.json`
The database report table carries a coded confirmed grade on 99.8 % of reports (lookup `query_dysplasia_types.csv`). Jury vs
DB confirmed code, 8,221 Barrett's-coded reports: exact 0.961, two-tier 0.986, QWK 0.974; over-call on NDBE 2.9 %, under-call
on LGD+ 1.6 %. Including non-Barrett's mucosa codes (11,613 reports): 0.966 / 0.988. DB confirmed code vs SWG spreadsheet
code on the same 313 reports: 0.847 / 0.907 (the spreadsheet under-calls 22 % of DB-coded LGD+). Provisional code vs
confirmed code: exact 0.49, the provisional entry over-calls 81 % of confirmed-NDBE reports, so "prov" is a first-pass
field, not a grade. New claim C27; provenance question Q13 added.

## Commits
`384987a` scripts + first results; `c998de8` questions and checklist; results of the batch in the commit after
`c998de8` on `main` (see `git log`). Plan amendment 2.50 records the whole day.

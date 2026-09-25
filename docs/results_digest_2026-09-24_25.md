# Results digest — everything run 24–25 September 2026

Compiled 25 Sep 2026, 10:40; updated 11:20 with the leak-free P32 retrain. Companion to `results_digest_2026-09-21_22.md`.
Every number is transcribed from a committed JSON named in its section; tables are CSV-shaped so they can be plotted directly.
Nothing is pending.

Classes: **USE** solid, goes in the thesis · **BOUNDARY** a null worth stating · **DIG** real but needs one more step ·
**WITHDRAWN** an earlier claim retracted · **INFRA** data/pipeline fact.

| # | Task (Rehan's request) | Class | One-line result | Source |
|---|---|---|---|---|
| 1 | 38-item post-talk list: facts from code | INFRA | LGD2+ = two consecutive LGD *biopsies*; one slide = one unit (26/707 share a CNV); MedGemma 0.50 was on 96 of the 1,538 slides; no record of SWG resequencing | `docs/status_ledger_2026-09-24.md` §1 |
| 2 | SWG second CV repeat | **USE** | release late-mean beats histology +0.043 [+0.014, +0.071] on rep01 and +0.042 [+0.019, +0.069] on rep02; perm p 0.0025 / 0.001 | `results/numbers/swg_rep02.json`, `swg_rep02_selection.json` |
| 3 | Operating points, Brier, recalibration, detection-intensity, 12–36 m window | USE / BOUNDARY | train-fold thresholds within a few points of post hoc; Brier late-mean − image −0.061 [−0.095, −0.027]; Platt fixes over-confidence not under-confidence; repeat-biopsy exclusion changes nothing; the 12–36 m dip is grade composition | `results/numbers/swg_robustness.json` |
| 4 | CNV-as-text CIs and repeats | USE | 0.750 / 0.756 / 0.748 with grade, 0.645 / 0.647 / 0.642 without, across 3 seeds | `results/numbers/cnvtext_cis.json` |
| 5 | T4 "prior dysplasia" | **WITHDRAWN** | prior-therapy flag alone 0.874 > image 0.780; image within untreated 0.686 | `results/numbers/t4_treatment_split.json` |
| 6 | T3 field effect without resections | USE | 0.801 / 0.822 vs baselines 0.573 / 0.596, Δ +0.23, CIs > 0 | `results/numbers/erin_t3_biopsy_only.json` |
| 7 | Grade model within biopsies | USE | 0.865 biopsy-only vs 0.871 all; specimen type alone 0.558 | `results/numbers/grade_within_biopsy.json` |
| 8 | ACE-B HGD under-calls | USE | matching error: HGD in the other report of the same visit; max-over-window HGD 11/11 but two-tier 0.856 (15/83 NDBE over-called) | `results/numbers/anchor_eval.json` |
| 9 | Jury recalibration | BOUNDARY | no weighting or vote threshold gains > 0.006 two-tier; over-calling trades 1:1 with sensitivity | `results/numbers/jury_recalibration.json` |
| 10 | Image models vs jury over-grading | BOUNDARY | no association (p 0.57, n 82) | `results/numbers/image_vs_jury_overgrading.json` |
| 11 | SWG report text as third modality | BOUNDARY / DIG | text embedding 0.43 (null); jury grade of the report 0.669 vs pathologist code 0.677 | `results/numbers/swg_text_arm*.json` |
| 12 | CONCH tile-scale check | BOUNDARY | chance at 0.22 / 0.44 / 0.88 µm/px; never emits "LGD" | `results/numbers/conch_swg_scale.json` |
| 13 | Barrett's-DB confirmed grade as anchor (C27) | **USE** | jury vs DB code on 8,221 reports: exact 0.961, two-tier 0.986, QWK 0.974 | `results/numbers/db_confirmed_grade_anchor.json` |
| 14 | P31 multi-field extraction | USE | 12 fields, ≤ 3 % parse fail; grade needs its full definition (0.949 vs 0.477 exact); 6 fields two-juror robust, 4 not | `results/numbers/p31_validation_v2.json`, `p31_agreement.json` |
| 15 | P32 image → fields (ERIN) | USE | 11/13 fields in predicted band; visible: squamous 0.92, HGD+ 0.91, IM 0.90, LGD+ 0.86, treatment 0.82; not: certainty 0.54 | `results/numbers/p32_fields.json`, `p32b_fields.json` |
| 16 | P32 ERIN head → SWG fusion | **USE (heterogeneous)** | leak-free head (33 overlap patients excluded): alone 0.753; fusion +0.063 [+0.020, +0.107] on all 150; survives selection, permuted-label, feature and leakage controls; gain is +0.02 (n.s.) in the 96 never-in-ERIN patients and +0.20 in the 54 whose CNV arm fails | `results/numbers/p32b_swg_fuse.json`, `p32_fuse_controls.json`, `p32_checks.json` |
| 17 | P33 patch-level grading | USE | 13-d tile summary within 0.02–0.04 of ABMIL on T3 (no leak); T2b 0.14 below ABMIL after patient-level scoring | `results/numbers/p33_tasks_v2.json` |
| 18 | Local-LLM review panel | INFRA | 6 models agree on ACE-B validation, spatial statistics, human label audit; none found a numerical error | `docs/projects/llm_review_2026-09-25.md` |
| 19 | Grading app | INFRA | relaunched, passphrase rotated; 0 grades | `hand_grading/README.txt` (cluster) |
| 20 | Barrett's DB surveillance interval | USE | after a first LGD the next biopsy comes at median 199 d vs 374 d before; effect is post-2010 | `results/numbers/db_interval_first_lgd.json` |

---

## 1. SWG: second CV repeat (item 13 of the list)

Release trainer unchanged; new patient-stratified split, seed 20260924 (22.6 % of rows keep their rep01 fold).
`late_mean` in the release is the plain mean of the image and CNV probabilities (verified, corr 1.000).

```csv
arm,rep01_auroc,rep01_delta_vs_image,rep01_lo,rep01_hi,rep02_auroc,rep02_delta_vs_image,rep02_lo,rep02_hi
image_only,0.731,0,,,0.745,0,,
cnv_only,0.663,-0.068,-0.197,0.065,0.708,-0.037,-0.151,0.073
early_fusion,0.738,0.007,-0.056,0.067,0.788,0.043,-0.029,0.119
intermediate_fusion,0.741,0.010,-0.053,0.067,0.767,0.022,-0.036,0.079
coattention_fusion,0.739,0.008,-0.072,0.094,0.768,0.023,-0.036,0.086
late_mean_release,0.774,0.043,0.014,0.071,0.787,0.042,0.019,0.069
late_mean_foldz,0.783,0.051,-0.022,0.118,0.830,0.085,0.034,0.137
```

Permutation p (late_mean_release vs image): 0.0025 / 0.001. Selection-adjusted over five fusion arms: 0.225 / 0.024.
The arm was fixed after rep01, so rep02 is a pre-specified replication. Both repeats re-partition the same 150 patients.

## 2. SWG robustness (items 14–18)

```csv
arm,spec_at_sens95_trainfold,spec_ci_lo,spec_ci_hi,flagged,sens_at_spec86_trainfold,brier,brier_delta_vs_image_lo,brier_delta_vs_image_hi
image_only,0.18,0.11,0.26,129/150,0.42,0.245,0,0
cnv_only,0.06,0.02,0.11,141/150,0.34,0.216,-0.091,0.031
early_fusion,0.25,0.16,0.34,120/150,0.46,0.213,-0.070,0.006
intermediate_fusion,0.40,0.30,0.50,106/150,0.38,0.224,-0.049,0.009
coattention_fusion,0.25,0.16,0.34,121/150,0.36,0.230,-0.052,0.023
late_mean,0.28,0.19,0.37,118/150,0.48,0.184,-0.095,-0.027
late_stack_logit,0.30,0.21,0.39,116/150,0.32,0.203,-0.093,0.008
```

Recalibration (Platt within CV): image slope 0.62 → 0.71, Brier 0.245 → 0.202 [−0.079, −0.007], AUROC 0.731 → 0.699;
late_mean slope 1.78 → 0.71, Brier 0.184 → 0.191 (no gain). Detection-intensity exclusion (≤ 183 d repeats, 64
samples): every window and horizon moves by ≤ 0.026. The 12–36 m window: 29 samples from 13 patients, mostly NDBE
(18/29), image median probability 0.34; the > 36 m window is 19/24 LGD samples with 63 % first biopsies.

## 3. ERIN checks (items 24–30)

```csv
check,quantity,value,ci_lo,ci_hi
T4 prior-therapy flag alone,AUROC,0.874,0.850,0.896
T4 image arm all,AUROC,0.780,,
T4 image within no prior therapy (637/75),AUROC,0.686,0.610,0.767
T4 image within no therapy anywhere (612/62),AUROC,0.645,,
T3a biopsy-only image (1203/116),AUROC,0.801,0.751,0.848
T3a biopsy-only delta vs baseline,delta,0.228,0.156,0.298
T3b biopsy-only image (1203/62),AUROC,0.822,0.764,0.874
T3b biopsy-only delta vs baseline,delta,0.226,0.138,0.317
grade model case-max-trained all 1538,AUROC,0.871,0.842,0.897
grade model biopsy-only 1429,AUROC,0.865,0.831,0.896
specimen type alone,AUROC,0.558,,
```

## 4. Anchors and the jury (items 25, 26, 34, 35 + C27)

```csv
comparison,n,exact,two_tier,qwk
jury vs Barrett's-DB confirmed code (Barrett's codes),8221,0.961,0.986,0.974
jury vs DB code incl. non-Barrett's mucosa codes,11613,0.966,0.988,0.973
jury vs DB code on SWG-matched reports,298,0.940,0.983,0.976
DB code vs SWG spreadsheet code,313,0.847,0.907,0.886
jury vs SWG spreadsheet (previous anchor),627,0.590,0.821,0.611
jury vs ACE-B Seattle closest report,110,0.845,0.900,0.725
jury vs ACE-B Seattle max over 120-d window,111,0.811,0.856,0.717
```

Recalibration of the jury (5-fold CV by report, 625 pairs): majority two-tier 0.821; best rule (LGD+ needs 7/8) 0.827
with LGD+ sensitivity 0.96 → 0.86; dropping the 3 worst jurors 0.822. CONCH on 82 pathologist-NDBE SWG specimens: no
association between image score and jury over-call (Mann-Whitney p 0.57, AUROC 0.54).

## 5. The three new projects

### P31 — multi-field extraction (`p31_validation_v2.json`, `p31_agreement.json`)

```csv
field,parse_fail_v2,medgemma_vs_gemma_exact,kappa,keyword_or_reference_check,verdict
grade,0.000,0.946,0.892,vs jury exact 0.949 two-tier 0.969 (v1 prompt: 0.477),robust after full-ladder prompt
specimen_type,0.000,0.996,0.974,vs protocol 0.964,robust
intestinal_metaplasia,0.000,0.926,0.850,vs keyword 0.72,robust
p53,0.000,0.901,0.767,vs keyword 0.98,robust
inflammation,0.003,0.815,0.710,vs keyword 0.92,robust (moderate/severe)
treatment_effect,0.000,0.861,0.649,vs keyword 0.84,robust
site,0.000,0.741,0.554,,weak
gastric_mucosa_present,0.010,0.735,0.562,,weak
squamous_only,0.001,0.958,0.560,,rare class
ulceration_or_erosion,0.000,0.318,0.188,vs keyword 0.95,NOT robust
goblet_cells,0.000,0.665,0.073,,NOT robust
diagnostic_certainty,0.000,0.954,0.234,,NOT robust (19–78 non-definite)
```

Side effect: sharpening the grade definition shrank certainty from 78 to 19 non-definite calls; fields interact
through the prompt.

### P32 — fields from the image, ERIN (`p32_fields.json`; v2-label re-run in `p32b_fields.json`)

```csv
field,n,pos,auroc,ci_lo,ci_hi,predicted_band,verdict
specimen_resection,2293,91,1.000,1.000,1.000,visible,trivial
squamous_only,2291,127,0.920,0.892,0.945,visible,held
grade_HGDplus,1642,482,0.911,0.893,0.931,visible,held
im_present,2192,1406,0.897,0.884,0.910,visible,held
grade_LGDplus,1642,644,0.861,0.840,0.882,visible,held
ulceration,2154,320,0.847,0.818,0.875,partly,above band but juror kappa 0.19 -> fragile
treatment_effect,2293,522,0.821,0.797,0.842,visible,held
gastric_present,1182,831,0.781,0.749,0.811,visible,just below
p53_abnormal,473,193,0.749,0.703,0.795,not visible,above band (rides on grade)
inflammation_mod_severe,1846,373,0.742,0.709,0.771,partly,held
site_goj_or_stomach,2293,612,0.723,0.698,0.749,not visible,above band (cardia mucosa)
inflammation_any,1846,1517,0.607,0.574,0.643,partly,below band
certainty_not_definite,2289,78,0.538,0.467,0.611,not visible,held
```

### P32 — ERIN head transferred to SWG (`p32b_swg_fuse.json`, `p32_fuse_controls.json`, `p32_checks.json`)

All 150 SWG patients, release folds, patient level:

```csv
arm,auroc,ci_lo,ci_hi
image_only,0.731,0.640,0.814
cnv_only,0.663,0.569,0.754
imputed_fields_6,0.738,0.652,0.817
ERIN_grade_head_alone,0.756,,
fuse2_image_cnv,0.783,0.700,0.854
fuse3_plus_fields,0.832,0.762,0.894
fuse3_plus_grade_head_only,0.851,,
```

Controls (delta vs fuse2):

```csv
control,delta,ci_lo,ci_hi,perm_p
fields (6) as third arm,0.050,0.015,0.089,0.002
selection-adjusted over the 6 fields (max),0.069,,,0.022
second SWG image model as third arm (ensemble control),0.018,-0.018,0.058,0.170
ERIN grade head retrained on other ERIN split,0.071,0.028,0.122,
ERIN head trained on PERMUTED labels,-0.106,-0.170,-0.037,
SWG image arm retrained on 0.5um feats (alone 0.693); fuse3 vs fuse2 on it,0.050,0.002,0.098,
rep02 SWG split (grade head),0.035,-0.008,0.079,
rep02 SWG split (6 fields),0.015,-0.018,0.048,
```

Mechanism check: imputed grade vs SWG spreadsheet 0.619, vs DB confirmed code 0.629 (n 418); the head calls 85 % of
SWG slides p > 0.5 against a 12 % LGD+ rate (calibration slope 0.58). It is not a grade read-out on SWG.

**Patient overlap (found 25 Sep 10:30).** 54/150 SWG patients are also ERIN patients; 44 ERIN cases from 33 of them
were in P32 training. Split by overlap status (existing scores):

```csv
swg_subgroup,n,pos,image,cnv,erin_head,fuse2,fuse3,delta,ci_lo,ci_hi
all,150,50,0.731,0.663,0.756,0.783,0.851,0.069,0.024,0.119
never_in_ERIN,96,36,0.744,0.760,0.758,0.863,0.884,0.020,-0.025,0.066
also_in_ERIN,54,14,0.704,0.454,0.739,0.580,0.784,0.204,0.087,0.336
```

The head's own AUROC is not higher on patients it could have seen; the gain concentrates where the CNV arm collapses.
Leak-free retrain with the 33 patients excluded (`p32_head_noov.json`, `p32_fuse_noov.json`, `p32_noov_subgroups.json`):

```csv
swg_subgroup,n,pos,image,cnv,erin_head_leakfree,fuse2,fuse3,delta,ci_lo,ci_hi
all,150,50,0.731,0.663,0.753,0.783,0.850,0.067,0.022,0.114
never_in_ERIN,96,36,0.744,0.760,0.758,0.863,0.885,0.022,-0.027,0.070
also_in_ERIN,54,14,0.704,0.454,0.745,0.580,0.779,0.198,0.096,0.317
```

Excluding the shared patients changed nothing (head 0.756 → 0.753): training leakage was not the driver. The gain is
real on the full cohort and concentrated where the CNV arm collapses; report both numbers.

### P33 — patch-level grading (`p33_tasks_v2.json`, 3 seeds, patient-level fold scoring)

```csv
task,n,pos,tile_summary,tile_lo,tile_hi,abmil,delta_lo,delta_hi,fused,v1_tile_summary
T2a,185,44,0.758,0.669,0.837,0.817,-0.150,0.036,0.820,0.792
T2b,183,30,0.720,0.602,0.821,0.862,-0.242,-0.058,0.837,0.782
T3a,1274,146,0.800,0.753,0.847,0.821,-0.060,0.017,0.835,0.798
T3b,1274,90,0.828,0.762,0.885,0.869,-0.089,0.000,0.861,0.827
T3a_bio,1203,116,0.765,0.712,0.818,0.801,-0.078,0.010,0.808,0.765
T3b_bio,1203,62,0.802,0.729,0.872,0.822,-0.090,0.052,0.844,0.804
```

T3 unchanged from v1 (no leak); T2 fell 0.03–0.06 (v1 had indirect leakage). Top coefficient on every T3 task:
mean cancer-class probability, then LGD tile fraction. Tile maps for 12 slides in `review/p33_tilemaps/`; the top
benign-called positives carry 5–66 % LGD-class tiles; two top-scoring negatives look dysplastic too.

## 6. Pending
Nothing. The leak-free retrain landed at 11:10 on 25 Sep (see §5).

## 7. People and decisions still needed
Questions drafted in `docs/questions_for_people_2026-09-24.md` (Leanne ×5 incl. DB-code provenance, data owner ×2,
histopathology core ×1, pathologist ×2). Audit packs in `review/`: 30 SWG over-calls, 4 ACE-B HGD cases, 50 P31
reports, 12 P33 tile maps. Your own spot-check of the 29 cancer re-reads.

# Results digest — everything run 21–22 September 2026

Compiled 23 Sep 2026 from the results JSONs (paths given per section; the JSON is
ground truth, this file is a transcription for the Thursday 24 Sep lab talk).
Every table is written so it can be pasted into a plotting script; CSV blocks
are given where a chart is the natural presentation.

Classification used throughout:

- **USE** — solid, pre-registered or gated, goes in the thesis as a claim.
- **BOUNDARY** — a negative or null worth stating as a limit of the method.
- **DIG** — real but needs one more experiment before it can carry weight.
- **INFRA** — data or compute fact, no scientific claim.

| # | Run | Class | One-line result | Source |
|---|---|---|---|---|
| 1 | ERIN 3-year progression fusion (2.48) | BOUNDARY / INFRA | Infeasible: 18 positives, 0 negatives; every scanned slide is 2022–2025 | `reports/erin_progression_fusion.md` |
| 2 | ERIN imminent-dysplasia task set (2.49), 7 tasks | USE + DIG | Image beats grade+age by +0.23 to +0.26 AUROC on T2b/T3a/T3b/T4 (CI > 0); fusion never beats image. Review: 5 % of T3 slides are resection tissue and specimen type alone scores 0.59/0.64 on T3a/T3b (§13) | `results/erin_progression_fusion/results.json` |
| 3 | Human-grade anchors: jury vs SWG pathologist, vs ACE-B Seattle | USE | Two-tier 0.82 (κ 0.61) vs SWG pathologist with systematic over-grading; 0.90 vs ACE-B | `results/numbers/anchor_eval.json` |
| 4 | MedGemma-27B as ERIN juror | USE | 99.7 % exact agreement with the 8-model jury; sensitivity 1.0 on 79 adjudicated cancers | `results/numbers/num_medgemma.json` |
| 5 | Zero-shot 5-year risk from report text (3 LLMs) | BOUNDARY | 0.59–0.63 vs index-grade baseline 0.62; LLM ≈ grade, as predicted | `results/numbers/prognosis_eval.json` |
| 6 | CNV-as-text (MedGemma-27B, qwen3-32B) | USE | CNV-only prompt 0.645 vs trained CNV model 0.663; grade+CNV 0.751 > grade 0.687 | `results/numbers/cnvtext_*.json` |
| 7 | MedGemma image pilots (4B, 27B) | BOUNDARY | AUROC 0.50–0.51, half the tiles unparseable; gate failed | `results/numbers/patchvlm_*.json` |
| 8 | CONCH zero-shot (pilot → 1,538 slides) | USE | 0.784 LGD+ zero-shot on the 1,538 dual-labelled slides (section truth). Fair supervised reference on the SAME slides and truth is ABMIL 0.871 (case-max-trained) / 0.860 (section-trained), not 0.926 (see §13.3 item 9) | `results/numbers/conch_zeroshot*.json` |
| 9 | CONCH zero-shot on SWG release | DIG | 0.53–0.59 vs pathologist grade; 0.58–0.67 progression; scale/subsample suspected | `results/numbers/conch_swg.json` |
| 10 | Tile-level training vs ABMIL | USE | Within 0.02–0.03 of ABMIL; tile-level wins six-class under section labels | `results/numbers/tile_level.json` |
| 11 | Nodal status from OGD biopsy (OCCAMS) | BOUNDARY | cN null (0.49–0.57, perm p 0.67); ypN weak (0.58–0.67), below clinical 0.66 | `results/numbers/nodal_probe.json` |
| 12 | Attention heat-maps (SWG) and tile grade maps (ERIN) | INFRA | Qualitative figures produced; 12 ERIN slides, SWG prior/progressor samples | `results/numbers/{swg_heatmaps,erin_tilemaps}.json`, `review/` |
| 13 | ERIN all-slides UNI2-h extraction close-out | INFRA | 9,544 biopsy-scale slides in use of 9,562; 11 valid resection megaslides parked; 7 corrupt files need rescan (§11, §13) | `results/numbers/extraction_coverage.json` |

---

## 1. ERIN 3-year progression fusion — feasibility stop (2.48)

Pre-registered 21 Sep 19:40 (`docs/erin_progression_fusion_preregistration.md`); stopped at the
cohort stage by its own rule (empty negative class). GPU-hours: 0.

### 1.1 Cohort funnel (chart: funnel or waterfall)

```csv
stage,n,y3_pos,y3_neg,censored
Index NDBE/IND patients (report level),2092,115,721,1256
...with H&E slides + UNI2 features on the index case,632,18,0,614
Analysis set at 3 years,18,18,0,0
```

- Imaged index cases: 632 patients, 2,499 slides, median 2 per case (range 1–72). Index grade NDBE 611 / IND 21.
- Follow-up among imaged index cases: median 0 days; 499 of 632 have no later report.
- Horizon sweep (pos / neg): 180 d 9/69 · 1 y 18/30 · 1.5 y 18/11 · 2 y 18/2 · 3 y 18/0.
- The 18 "positives" progressed a median 180 days after index: prevalent disease found within months, not 3-year prediction.

### 1.2 Where the 3-year cohort actually is (chart: stacked bars by index year)

```csv
index_year,y3_defined_cases,progressors,scanned
2014,31,2,0
2015,177,9,0
2016,163,8,0
2017,105,14,0
2018,117,13,0
2019,101,12,0
2020,55,9,0
2021,50,12,0
2022,19,18,0
2023,9,9,9
2024,9,9,9
```

Total 836 three-year-defined index cases, 115 progressors, 18 scanned. The 2014–2021 index blocks
(818 cases, 97 progressors, ~721 clean negatives) are in the archive, unscanned. Cost estimate for a
targeted retrieval (all 97 progressor index cases + ~200 matched negatives ≈ 600 slides at ~£10 each)
≈ £6k, two weeks per batch. This is the single decision that would give ERIN a real progression cohort.

### 1.3 Consequence for existing claims
C3 reworded: the earlier ERIN "progression" number (153 index slides / 28 progressors, histology 0.819,
fusion null) is imminent-dysplasia detection in a censored 2022–2025 window, not progression prediction.

---

## 2. ERIN imminent-dysplasia task set (2.49) — 7 tasks, 364 queue tasks, 0 failures

Pre-registered 21 Sep 20:15 (`docs/erin_imminent_tasks_preregistration.md`, commit 48ab0c5) before launch.
Machinery: patient-disjoint 5-fold (seed 0), 3 seeds averaged, patient-clustered 2,000-replicate bootstrap,
fold-local z-scored late-mean fusion, no tuning. Arms: **a** baseline logistic on grade+age;
**b** text logistic on `nomic-embed-text` (768-d) of FinalDiagnosis+Microscopic; **c** image ABMIL on UNI2-h
tiles (case bag = all H&E slides of the report's case, ≤1,500 tiles/slide); **d** late-mean of z(b), z(c).
Text arm omitted for T3/T4 because the label is derived from text/history (would leak).

### 2.1 Task definitions and counts

```csv
task,unit,label,n,pos,neg,patients,slides,status
T1,first NDBE/IND report per patient,HGD/cancer within 365 d,48,18,30,48,181,feasibility only (<30 pos)
T2a,every imaged NDBE/IND report with follow-up (landmark),LGD+ within 365 d,185,44,141,156,564,PRIMARY
T2b,landmark,HGD+ within 365 d,183,30,153,155,535,interpretable (borderline)
T2c,landmark,next report is LGD+ (any gap),389,45,344,289,1212,interpretable
T3a,benign-section slide (NDBE or NORMAL_OTHER; section labels v2),case has LGD+ elsewhere (field effect),1274,146,1128,1056,1274,image-only
T3b,benign-section slide,case has HGD+ elsewhere,1274,90,1184,1056,1274,image-only
T4,imaged NDBE/IND report with earlier reports,prior LGD+ anywhere in history,1147,518,629,874,3886,image-only
```

Negative definition for the 365-day labels: no event AND last report ≥ 365 d after the landmark.
Grade distribution of inputs: T2a NDBE 171 / IND 14; T3 NORMAL_OTHER 685 / NDBE 589; T4 NDBE 1,093 / IND 54.

### 2.2 AUROC per arm (chart: grouped bars, one group per task, error bars = 95 % CI)

```csv
task,arm,auroc,ci_lo,ci_hi,auprc,auprc_lo,auprc_hi,brier
T1,baseline,0.6222,0.4541,0.7813,0.4566,0.3005,0.6950,0.2473
T1,text,0.7278,0.5535,0.8803,0.6622,0.4647,0.8835,0.2039
T1,image,0.8481,0.7241,0.9535,0.8426,0.6939,0.9510,0.1400
T1,fusion,0.9093,0.7983,0.9877,0.8991,0.7737,0.9831,0.1549
T2a,baseline,0.7086,0.6198,0.7978,0.3987,0.2840,0.5672,0.2168
T2a,text,0.6139,0.5054,0.7115,0.3330,0.2072,0.5070,0.2621
T2a,image,0.8174,0.7250,0.8920,0.6202,0.4473,0.7945,0.1612
T2a,fusion,0.7747,0.6867,0.8499,0.5226,0.3528,0.6867,0.2161
T2b,baseline,0.6294,0.5193,0.7307,0.2302,0.1361,0.3739,0.2354
T2b,text,0.6597,0.5500,0.7740,0.3193,0.1698,0.5101,0.1829
T2b,image,0.8619,0.7885,0.9199,0.5424,0.3473,0.7520,0.1379
T2b,fusion,0.8257,0.7514,0.8896,0.4617,0.2853,0.6588,0.2192
T2c,baseline,0.6488,0.5634,0.7270,0.1689,0.1174,0.2477,0.2351
T2c,text,0.6522,0.5709,0.7293,0.1874,0.1263,0.2869,0.1733
T2c,image,0.6608,0.5686,0.7450,0.2595,0.1630,0.4088,0.1832
T2c,fusion,0.7049,0.6276,0.7794,0.2500,0.1618,0.3866,0.2478
T3a,baseline,0.5771,0.5297,0.6254,0.1452,0.1161,0.1844,0.2454
T3a,image,0.8210,0.7791,0.8608,0.5288,0.4483,0.6157,0.1166
T3b,baseline,0.6078,0.5450,0.6648,0.0968,0.0744,0.1339,0.2360
T3b,image,0.8692,0.8237,0.9105,0.4967,0.3931,0.6115,0.0737
T4,baseline,0.5499,0.5088,0.5925,0.4832,0.4347,0.5351,0.2465
T4,image,0.7802,0.7470,0.8089,0.7271,0.6738,0.7779,0.1953
```

### 2.3 Paired deltas (chart: forest plot; already drawn as `results/erin_progression_fusion/figures/fig2_forest_deltas.png`)

```csv
task,contrast,delta,ci_lo,ci_hi,verdict
T1,image - baseline,0.2259,0.0569,0.3980,feasibility only
T1,text - baseline,0.1056,-0.1250,0.3072,feasibility only
T1,fusion - best single (image),0.0611,-0.0388,0.1807,feasibility only
T2a,image - baseline,0.1088,-0.0283,0.2341,CI includes 0
T2a,text - baseline,-0.0947,-0.2353,0.0348,CI includes 0
T2a,fusion - best single (image),-0.0427,-0.0965,0.0163,no demonstrated fusion gain (PRIMARY)
T2b,image - baseline,0.2325,0.1227,0.3493,CI excludes 0
T2b,text - baseline,0.0303,-0.0952,0.1681,CI includes 0
T2b,fusion - best single (image),-0.0362,-0.0824,0.0104,CI includes 0
T2c,image - baseline,0.0120,-0.0912,0.1176,CI includes 0
T2c,text - baseline,0.0033,-0.1096,0.1248,CI includes 0
T2c,fusion - best single (image),0.0441,-0.0232,0.1254,CI includes 0
T3a,image - baseline,0.2438,0.1820,0.3077,CI excludes 0
T3b,image - baseline,0.2614,0.1926,0.3286,CI excludes 0
T4,image - baseline,0.2303,0.1754,0.2811,CI excludes 0
```

### 2.4 Permutation nulls, T2a (chart: null histogram with the real value as a vertical line)

```csv
arm,n_perm,null_mean,null_p95,real_auroc,p_empirical
image (c),50,0.5088,0.6228,0.8174,0.0196
fusion (d),50,0.5188,0.6097,0.7747,0.0196
```

Image retrained per permutation, one seed. p = 1/(50+1): no permutation reached the real value.

### 2.5 Operating points, image arm (chart: table or dot plot; sensitivity locked at 0.95 and 1.0 per Rehan)

```csv
task,arm,spec_at_sens_0.95,spec_at_sens_1.0,sens_at_spec_0.80
T2a,baseline,0.305,0.106,0.432
T2a,image,0.277,0.099,0.659
T2a,fusion,0.369,0.099,0.568
T2b,baseline,0.268,0.065,0.333
T2b,image,0.641,0.549,0.667
T2b,fusion,0.503,0.464,0.733
T2c,image,0.180,0.157,0.422
T3a,baseline,0.078,0.009,0.253
T3a,image,0.122,0.004,0.706
T3b,baseline,0.043,0.018,0.300
T3b,image,0.404,0.015,0.778
T4,baseline,0.140,0.011,0.243
T4,image,0.191,0.019,0.641
```

The clinically striking one is T2b: at 95 % sensitivity for HGD+ within a year the image arm keeps
64 % specificity, against 27 % for grade+age. It rests on 30 positives.

### 2.6 Tile-count confound (AUROC of tile count alone)

```csv
task,tilecount_auroc
T1,0.425
T2a,0.568
T2b,0.536
T2c,0.533
T3a,0.516
T3b,0.534
T4,0.402
```

No task's label is predictable from biopsy size.

### 2.7 What the pre-registered rules say
- **Primary (T2a fusion vs best single):** −0.043 [−0.097, +0.016] → "no demonstrated fusion gain"; the selection-adjusted permutation was not triggered.
- T2a image − baseline: CI includes 0 → not demonstrated, though the permutation null puts the image arm's 0.817 well above any of 50 permutations.
- T2b, T3a, T3b, T4 image − baseline: CI excludes 0 → "the image carries information beyond grade + age".
- T2c null. T1 feasibility only.
- All tasks live in the 2022–2025 window with ≤ 3 years follow-up: none is progression prediction in the SWG sense.

### 2.8 Decisions not pre-specified (defend or change)
1. ≤1,500 tiles kept per slide when pooling case bags (memory); ABMIL's MAX_TILES=800 per-epoch subsample then applies.
2. Landmark tasks allow several reports per patient; a one-per-patient variant was not run.
3. Negative = no event and last report ≥ 365 d after landmark.
4. Text arm = FinalDiagnosis + MicroscopicDescription only, truncated at 6,000 characters.
5. Late fusion uses fold-local z-scoring (2.46 lesson), not pooled.
6. T3 baseline uses section grade (NORMAL_OTHER vs NDBE) + age; others index grade (NDBE vs IND) + age.

### 2.9 Compute
20.7 GPU-hours (cuda 14.99, h200 5.74, epyc 0), allocated GPUs × wall time including worker idle.
364 queue tasks: 1 embedding, 7 tabular, 105 image units (7 tasks × 5 folds × 3 seeds), 250 T2a permutation
image units, tabular permutations. Figures: `fig1_roc_T2a.png`, `fig2_forest_deltas.png`, `fig3_reliability_T2a_d.png` + CSVs.

### 2.10 What still needs doing before C26 carries weight (DIG)
- **Specimen-type confound, quantified in review (§13.3, item 1).** ERIN is not biopsy-only: 490 of 7,149 reports are oesophagectomy resections and they contribute ~34 % of all slide rows. In the T3 tables 68 of 1,274 "benign-section" slides come from resection cases, where the positive rate is 0.44 (T3a) / 0.41 (T3b) against 0.10 / 0.05 for biopsies; specimen type alone scores AUROC 0.586 / 0.639. It cannot explain 0.82 / 0.87, but it inflates them. The fix is a biopsy-only re-run of the T3 image arm (n = 1,206; 116 / 62 positives; 30 image units, ~1 GPU-hour). T2 and T4 are unaffected (≤ 3 resection units, specimen-type AUROC ≤ 0.51).
- **Other metadata confounds.** Scanner/block/date alone for T3/T4; if that reaches 0.7 the field-effect reading collapses.
- **Section-label noise check for T3.** "Benign-section slide" comes from the v2 section jury, which disagrees with case-max on 32 % of slides (C17). Some T3 positives may be dysplastic slides mislabelled benign; the model would then be detecting dysplasia present, not field effect. Look at the tile grade maps of the top-scoring T3 positives.
- **Treatment history for T4.** Patients with prior dysplasia have usually had RFA/EMR; the image may be recognising post-ablation neosquamous epithelium and scarring rather than a "trace" of dysplasia. Split T4 by treatment mention in the earlier reports.
- **T2b power.** 30 positives. The 818 unscanned pre-2022 blocks or ACE-B are the only routes to more.

---

## 3. Human-grade anchors for the LLM jury (project A)

`results/numbers/anchor_eval.json`. Confusion matrices are truth rows × predicted columns in ordinal order
**NDBE, IND, LGD, HGD, CANCER**.

### 3.1 vs SWG research-pathologist grade (658 specimen-level Barrett's-DB reports)

```csv
grader,n,exact,two_tier_LGDplus,qwk,within_one_rung
jury consensus,627,0.590,0.821,0.611,0.864
jury consensus (confident only frac>=0.75),437,0.597,0.771,0.606,0.828
MedGemma-27B,623,0.632,0.775,0.591,0.822
qwen3_32b,523,0.530,0.822,0.592,0.864
deepseek-r1_14b,516,0.430,0.769,0.505,0.810
gemma3_12b,581,0.535,0.806,0.577,0.852
mistral-small3.2,562,0.696,0.822,0.666,0.863
phi4_14b,620,0.689,0.826,0.658,0.886
qwen3_14b,615,0.621,0.836,0.643,0.886
llama3.1_8b,625,0.370,0.797,0.492,0.845
gemma3_27b,626,0.500,0.824,0.576,0.867
```

Jury-consensus confusion (truth rows NDBE/IND/LGD/HGD/CANCER; columns same order) — chart: heat-map:

```csv
truth,NDBE,IND,LGD,HGD,CANCER
NDBE,246,113,43,20,8
IND,0,34,26,11,0
LGD,0,4,56,21,2
HGD,0,0,0,18,5
CANCER,0,0,1,3,16
```

Reading: the jury never under-calls (lower triangle is almost empty) and over-calls heavily — of 430
pathologist-NDBE specimens it calls 113 IND, 43 LGD, 20 HGD, 8 cancer (184 = 43 %). Caveats recorded:
the SWG grade is a research re-read, the text is the original clinical report, and the section↔specimen
mapping is itself noisy. The 20 HGD + 8 cancer calls on pathologist-NDBE tissue are the cells to audit first.

### 3.2 vs ACE-B Seattle-protocol grades (report within 120 d of trial entry; gap median 0 d)

```csv
grader,n,exact,two_tier_LGDplus,qwk,within_one_rung
jury,110,0.836,0.900,0.716,0.909
MedGemma-27B,111,0.865,0.910,0.752,0.919
```

Jury confusion (truth rows NDBE 83 / IND 5 / LGD 9 / HGD 11 / CANCER 3):

```csv
truth,NDBE,IND,LGD,HGD,CANCER
NDBE,77,1,2,2,0
IND,3,2,0,0,0
LGD,2,1,6,0,0
HGD,4,0,0,6,1
CANCER,0,0,0,2,1
```

Note for the talk: two-tier 0.90 hides that 4 of 11 Seattle-HGD cases were called NDBE by the jury
(HGD recall 6/11; MedGemma the same 4). With n = 11 that is a flag, not a finding.

### 3.3 Reference points
TCGA registry two-tier agreement 0.96–0.97 (C14). ERIN jury vs 78 adjudications 98.7 % (C15).

---

## 4. MedGemma-27B as a ninth ERIN juror

`results/numbers/num_medgemma.json`, 7,101 reports.

```csv
model,parse_rate,exact_vs_jury,binary_LGDplus_vs_jury,n_compared,adjudicated_cancer_n,adj_acc,adj_sens,adj_spec
medgemma_27b,0.9965,0.9974,0.9993,6804,79,0.987,1.000,0.980
medgemma_4b,0.7458,0.9397,0.9881,5128,58,0.862,0.600,1.000
```

Pairwise agreement of MedGemma-27B with each juror: qwen3_14b 0.973, gemma3_27b 0.973, phi4_14b 0.973,
gemma3_12b 0.969, qwen3_32b 0.964, deepseek-r1_14b 0.961, mistral-small3.2 0.952, llama3.1_8b 0.880.
Disagreements with a confident jury: 12 of 6,621 (4 of them jury=HGD → MedGemma=CANCER).
MedGemma-4B is unusable: 1,789 parse failures and it under-calls cancer as HGD 160 times.

---

## 5. Zero-shot 5-year HGD/cancer risk from report text (project C1)

`results/numbers/prognosis_eval.json`. ERIN v3 cohort, 1,266 patients, 181 progressors; input = pre-index
report history (median 1 report shown, because the index is the first NDBE report by construction).

```csv
model,auroc,ci_lo,ci_hi,auroc_within_NDBE_index,parse_fail
index-grade baseline,0.623,0.588,0.659,,
medgemma_27b,0.593,0.546,0.637,0.524,0
qwen3_32b,0.625,0.577,0.671,0.551,0
gemma3_27b,0.632,0.586,0.677,0.561,0
trained text model (DB corpus; reference),0.696,,,,
```

Pre-registered prediction "LLM ≈ grade" holds. Median risk given to progressors vs non-progressors is
identical for two of three models (15 vs 15, 10 vs 10), i.e. the models are not separating at all beyond
the grade word.

---

## 6. Copy-number as text (project C2; SWG, 707 samples)

`results/numbers/cnvtext_*.json`. Prompt = chromosome-arm gains/losses as text, with or without the current grade.

```csv
arm,model,patient_auroc,sample_auroc,parsed
CNV-only prompt,medgemma_27b,0.645,0.597,707/707
grade+CNV prompt,medgemma_27b,0.751,0.676,707/707
grade+CNV prompt,qwen3_32b,0.725,0.691,707/707
trained CNV-only linear model (reference),,0.663,0.620,
pathologist grade as score (reference),,0.687,,
```

qwen3-32B CNV-only arm cancelled (1.2 prompts/min on an L40S; would not finish in walltime).
Reading: a zero-shot LLM reading CNV text matches a trained linear model within noise, and grade+CNV
exceeds either alone — the same complementarity the LRT found (p 0.007), reproduced without training.

---

## 7. Zero-shot histology: general medical VLM vs pathology VLM

### 7.1 MedGemma image pilots (project B; 96 slides × 8 tiles, 16 per class) — gate 0.70 FAILED

```csv
model,tiles_parsed,tiles_unparseable,tile_grades_emitted,auroc_LGDplus_max,auroc_frac,auroc_mean
medgemma_4b,330,438,NDBE 293 / HGD 37,0.510,0.514,0.514
medgemma_27b,386,382,NDBE 386,0.500,0.500,0.500
```

### 7.2 CONCH zero-shot (project E; 64 highest-attention tiles per slide, Barrett's prompt ensemble)

```csv
run,n_slides,auroc_LGDplus_mean,auroc_LGDplus_max,auroc_LGDplus_top10,macro_auroc_6class,gate_0.70
pilot,96,0.710,0.755,0.723,0.709,pass
full,1538,0.770,0.784,0.778,0.733,pass
```

Reference points, corrected 24 Sep: the pre-registration quoted "trained VLM 0.889, supervised MIL 0.926 on identical slides", but those three numbers come from three different slide sets. 0.926 is `results/erin_encoder_sweep.json` uni2/hist_abmil on 2,153 slides against case-max labels; 0.889 is `results/vlm_pretrain.json` on a 423-slide VLM test split; CONCH's 0.784 is on the 1,538 dual-labelled slides against section truth. On those 1,538 slides and that truth the supervised ABMIL reference is 0.871 (case-max-trained) or 0.860 (section-trained), `results/slide_vs_casemax.json`. The zero-shot gap is therefore 0.08–0.09, not 0.14. MedGemma 0.50 was on a 96-slide subset of the same 1,538.

Tile-level argmax fractions by true slide grade, full run (chart: stacked bars or heat-map):

```csv
truth,frac_NORMAL_OTHER,frac_NDBE,frac_IND,frac_LGD,frac_HGD,frac_CANCER
NORMAL_OTHER,0.655,0.248,0.055,0.015,0.018,0.009
NDBE,0.378,0.486,0.068,0.045,0.019,0.003
IND,0.245,0.572,0.092,0.036,0.042,0.013
LGD,0.326,0.367,0.106,0.057,0.122,0.022
HGD,0.378,0.220,0.089,0.024,0.206,0.082
CANCER,0.383,0.118,0.021,0.020,0.245,0.214
```

Anatomically sensible: cancer slides get 46 % HGD/cancer tiles vs 1–3 % on benign slides; LGD is the
class CONCH cannot name (5.7 % of LGD-slide tiles).

### 7.3 CONCH on the SWG release (707 slides, the stored 256 level-2 tiles each) — DIG

```csv
target,score,auroc
pathologist LGD+ (slide),mean P(LGD),0.534
pathologist LGD+ (slide),max P(LGD),0.566
pathologist LGD+ (slide),top10 P(LGD),0.546
pathologist LGD+ (slide),mean P(HGD),0.586
progression (sample),mean P(LGD),0.543
progression (patient max),mean P(LGD),0.583
progression (patient max),max P(LGD),0.656
progression (patient max),mean P(HGD),0.667
trained image_only (reference; sample / patient),,0.739 / 0.731
pathologist grade as score (reference; patient),,0.687
```

Same model that scores 0.78 on ERIN scores 0.53–0.59 on SWG grade. Suspected: the stored tiles are level 2
(~0.9 µm/px) against CONCH's 20× training scale, and only 256 tiles per slide. Test: re-extract 20 SWG slides at 20× from the raw files.

---

## 8. Tile-level training vs ABMIL (project D; 1,538 slides, frozen folds, 3 seeds)

`results/numbers/tile_level.json`. MLP tile classifier 1536→512→6, 4 epochs, 2,000 tiles/slide cap;
slide score = mean / max / top-10 % of tile probabilities.

```csv
label_scheme,model,binary_auc,binary_lo,binary_hi,macro_auc,d_binary_lo,d_binary_hi,d_macro_lo,d_macro_hi
case_max,ABMIL (reference),0.8705,,,0.7639,,,,
case_max,tile mean,0.8447,0.8142,0.8734,0.7347,-0.0499,-0.0034,-0.0515,-0.0070
case_max,tile max,0.7780,0.7351,0.8144,0.7255,-0.1332,-0.0592,-0.0622,-0.0150
case_max,tile top10,0.8424,0.8117,0.8700,0.7392,-0.0510,-0.0049,-0.0477,-0.0014
section,ABMIL (reference),0.8604,,,0.7216,,,,
section,tile mean,0.8360,0.8023,0.8664,0.7550,-0.0497,-0.0005,0.0102,0.0565
section,tile max,0.8062,0.7695,0.8387,0.7314,-0.0879,-0.0236,-0.0126,0.0322
section,tile top10,0.8419,0.8096,0.8707,0.7523,-0.0418,0.0034,0.0083,0.0540
```

Reading: for binary screening tile-level is 0.02–0.03 below ABMIL (CIs mostly exclude 0); for six-class
under section labels tile-level wins (+0.010 to +0.057). Prediction was half right. Tile-level gives real
per-tile grade maps for free and is the model of choice once section-resolved labels exist.

---

## 9. Nodal status from the pre-treatment OGD biopsy (OCCAMS)

`results/numbers/nodal_probe.json`; design `docs/nodal_probe_preregistration.md`. Gate: histology lower CI > 0.5 and point ≥ 0.60.

```csv
label,n,node_pos,node_neg,encoder,hist_auc,hist_lo,hist_hi,clin_auc,clin_lo,clin_hi
ypN (resection; after neoadjuvant),133,82,51,uni_v2,0.607,0.503,0.704,0.655,0.549,0.759
ypN,133,82,51,virchow2,0.669,0.575,0.753,0.655,0.549,0.759
ypN,133,82,51,hoptimus0,0.634,0.536,0.733,0.655,0.549,0.759
ypN,133,82,51,gigapath,0.604,0.503,0.703,0.655,0.549,0.759
ypN,133,82,51,phikon2,0.578,0.469,0.683,0.655,0.549,0.759
cN (clinical pre-treatment),139,96,43,uni_v2,0.487,0.383,0.599,0.672,0.560,0.776
cN,139,96,43,hoptimus0,0.539,0.440,0.658,0.672,0.560,0.776
cN,139,96,43,phikon2,0.567,0.466,0.678,0.672,0.560,0.776
cN,139,96,43,gigapath,0.498,0.398,0.612,0.672,0.560,0.776
```

Permutation nulls (UNI2, 50 perms): ypN null mean 0.481, max 0.606, p 0.0196 (gate passed, barely);
cN null mean 0.514, max 0.648, p 0.667 (null). Tile-count confound 0.551 / 0.487.
Interpretation rule → ypN "weak signal, not clinically useful" (histology < clinical-with-cN 0.655);
cN "not visible in the primary". Clinical baseline for ypN includes cN.

---

## 10. Qualitative outputs produced (no numbers to claim)

- **SWG attention heat-maps** (`results/numbers/swg_heatmaps.json`, PNGs in `review/swg_heatmaps/`): per sample, top-10 % attention share for the image, intermediate, co-attention and early-fusion models, with OOF probabilities. Sample ids are pseudonymous DB ids.
- **ERIN tile grade maps** (`results/numbers/erin_tilemaps.json`, PNGs in `review/tilemaps/`): 12 held-out slides (fold 4), model trained on 1,229 slides, case-max and section-label models side by side, per-tile argmax distributions. Example: a NORMAL_OTHER section slide in an NDBE case → case-max model 76 % NDBE tiles, section model 54 % NORMAL tiles.

---

## 11. ERIN all-slides UNI2-h extraction — close-out (INFRA) and data-quality register

`results/numbers/extraction_coverage.json`. Manifest 9,562 H&E slides; feature directory also holds ~2,230 files from earlier manifests (11,781 in the main directory after parking).

```csv
category,slides,cases,status
extracted at 0.5 um/px and in use,9544,,in use
large-format resection megaslides (classic TIFF capped at exactly 4 GiB; no mpp tag; 1-2 pyramid levels),11,9,valid features extracted (level 1 fully readable; 4 single-level ones resized 448->224) but PARKED pending scope decision
unreadable source TIFF (openslide and PIL both fail; 24 KB - 105 MB),7,1,EXCLUDED - needs rescan (case 58beb6fd)
```

The 9 megaslide cases all carry SpecimenProtocol "OESOPHAGUS, PART/TOT RESECTION" (labels 6 CANCER, 1 HGD, 1 NDBE, 1 unsure). Their tiles are full-thickness oesophageal wall (muscularis propria, ganglia, vessels, submucosa) at the normal scan resolution; the physical size (~54 × 44 mm at 0.25 µm/px) fits a 2 × 3 inch slide, which is why these files alone hit the cap. Parked because a biopsy-cohort model should not silently ingest resection tissue; restore with a single `mv` if resections are in scope.

**Corpus composition, found in the same check (chart: pie or bar):**

```csv
specimen_protocol_class,reports_all,reports_imaged,slide_rows_all_stains
OESOPHAGUS (biopsy protocol),6654,2132,8085
OESOPHAGUS PART/TOT RESECTION,490,161,4192
other (polyp / stomach biopsy / nodes / adipose / diverticulum),5,0,~70 unmatched
```

Resections are 6.9 % of reports but ~34 % of slide rows (30–70 blocks per oesophagectomy; the cohort table's "max 72 slides per case" is one of these). This belongs in the thesis cohort description and is the source of the T3 confound in §2.10.

Compute burned on the failure loop: 1,093 OOM-killed worker jobs over ~24 h (740 cuda, 353 h200) chasing the same 18 slides, because the keepalive sweeper only stopped at zero remaining. Fixes now in place: banded thumbnail path for non-pyramidal slides, sweeper stall floor (3 cycles), file-based slide lists (Slurm `--export` splits on commas). Also confirmed: **no ERIN slide carries an mpp tag**; the pipeline assumes 0.25 µm/px at level 0 for every slide (normal slides' dimensions, e.g. 152,064 × 54,784 px → 38 × 14 mm, are consistent with that). State it in methods.

---

## 12. Job and compute tally, 21 Sep 09:00 → 22 Sep 13:00

```csv
state,jobs,of_which
FAILED,1211,1093 extraction workers (OOM kill) + ~112 nodal race-loser twins + 5 one-off bugs fixed on re-run + 1 gated MedGemma HF download
COMPLETED,326,
CANCELLED,74,idle workers and redundant race twins
```

Project-level GPU-hours since 14 Aug (`results/numbers/compute.json`, 32,011 jobs, 1,010.9 GPU-h, 36,763 CPU-h):
ERIN other-encoder extraction 495.7 · ERIN all-slides extraction 201.4 · LLM jury sections v3 109.4 ·
TCGA-STAD extraction 56.6 · misc analysis 41.0 · UNI2 one-per-case 38.1 · whole-report jury 31.8 ·
sections v2 19.8 (+13,101 CPU-h of CPU-only LLM garbage) · SWG 5.4 · EoE/MDT/phenotype 3.4 (+5,377 CPU-h garbage) ·
OCCAMS fusion 0.7 · OCCAMS extraction 0.5 · VLM 0.1. Imminent-task set: 20.7 GPU-h.

---

## 13. Review of the 21–22 Sep work (Fable 5.1 reviewing Opus 5)

Method: every number above re-read from its JSON; code paths for task construction, the image arm,
fold-local fusion and the extraction fix re-read; the "rescued" slides checked against the corpus.

### 13.1 Confirmed correct
- All transcribed numbers in the 22 Sep summary match the JSONs (anchors, CNV-text, CONCH, nodal, tile-level, imminent tasks).
- Pre-registration discipline held: 2.48 and 2.49 committed before launch; rules applied as written; six unregistered decisions listed.
- Folds are patient-disjoint in every task (`patient_folds`, seed 0); fusion z-scoring is fold-local (`zfold` per test fold); T3/T4 correctly drop the text arm to avoid label leakage.
- Nodal probe complete (50/50 permutations both labels); the FAILED nodal jobs were race-losers, not lost work.
- The tile-scale audit and the 0.5 µm/px re-extraction of 4 single-level slides were the right call, and the corpus is now homogeneous.
- Git attribution and repo hygiene (aggregate JSON only; slide UUIDs already had precedent in `erin_tilemaps.json`).

### 13.2 Found and acted on (two passes — the first conclusion was wrong and is kept here on purpose)
- **Pass 1 (quantitative).** The 11 "rescued" 4-GiB TIFFs have UNI2 features far outside the corpus: slide-mean cosine to the corpus centroid 0.19–0.43 (reference slides median 0.62, 5th percentile 0.41, minimum 0.30); per-tile cosine median 0.09–0.19 with 92–100 % of tiles below 0.3 (reference 0.29–0.42, 15–63 %). I provisionally called them corrupt and parked them.
- **Pass 2 (look at the tiles, read the metadata).** Rendered thumbnails and 36 random tiles from three of them (`review/bigcheck/`): well-preserved full-thickness oesophageal wall at the normal scale, next to a normal biopsy slide for comparison. All 9 cases are oesophagectomy resections by SpecimenProtocol. The features are valid; the distance from the centroid is tissue type. Parking stands, for the scope reason given in §11, with the reason relabelled `large_format_resection_specimen_parked` and the files restorable. Coverage register, plan entry and memory corrected. Lesson recorded: an out-of-distribution check is a flag, not a verdict.
- **Consequence that matters more than the 11 slides:** the check exposed that ~34 % of ERIN slide rows are resection material, and that 68 T3 slides come from resection cases (§2.10). That is the review's main finding.
- No analysis ever used the 11 slides (no features existed before 22 Sep; no task table, cohort or label file references their ids). The 22 Sep summary's numbers and the commit `3ca5f11` description remain accurate except for the word "rescued".

### 13.3 Flags for Rehan (not acted on)
1. **Specimen type is a partial confound for the T3 field-effect result.** 68 of 1,274 T3 slides are from resection cases (positive rate 0.44 / 0.41 vs 0.10 / 0.05); specimen type alone gives AUROC 0.586 (T3a) / 0.639 (T3b). A biopsy-only re-run (n = 1,206) is ~1 GPU-hour and should precede any presentation of C26 as biology. T2 and T4 are clean on this axis (≤ 0.51).
2. **T3 positives may also be section-label noise** (section-jury vs case-max disagreement is 32 %). Check the tile grade maps of the highest-scoring T3 positives.
3. **T4 "prior dysplasia" is confounded with prior treatment.** The image may be recognising post-RFA/EMR tissue. Split by treatment mention in the earlier reports.
4. **Grade models may exploit specimen type corpus-wide.** 490 resection reports (mostly CANCER) and ~34 % of slides: the six-class and cancer-vs-rest numbers (C20 0.921/0.960, VLM 0.889, CONCH 0.784) should be re-read within biopsies only, or with specimen type as a covariate, before P1 goes out.
5. **ACE-B two-tier 0.90 hides HGD recall of 6/11.** State both.
6. **The jury over-grades pathologist-NDBE tissue 43 % of the time** (incl. 20 HGD and 8 cancer calls). Needs a 30-report manual audit to separate mapping error from genuine over-call before P1.
7. **Downstream tile-map code assumes 224 px tiles at the stored level**; the 4 re-extracted single-level slides store 448 px tiles at level 0 (attribute `tile_px_at_level`). Harmless now; would mis-draw a map if displayed.
8. **No mpp tag anywhere in ERIN**: 0.25 µm/px at level 0 is an assumption; state it in methods.
9. **The CONCH comparison's supervised reference was on a different slide set.** 0.926 (2,153 slides, case-max truth) vs CONCH on 1,538 slides with section truth, where ABMIL scores 0.871. Wording in the pre-registration, plan entries and claims text should say 0.871/0.860; the qualitative conclusion (pathology VLM zero-shot ≈ 0.08 below supervised) stands.

---

## 14. Suggested figures for Thursday (data → chart)

1. §1.2 → stacked bars by index year: "the 3-year cohort exists on paper, none of it is scanned".
2. §2.2 + §2.3 → grouped bars (baseline / text / image / fusion) per task with the forest of deltas underneath; T2b operating point (64 % vs 27 % specificity at 95 % sensitivity) as a callout.
3. §2.4 → T2a permutation null histogram with the real 0.817.
4. §3.1 → jury-vs-pathologist confusion heat-map, with the "never under-calls, often over-calls" reading; ACE-B beside it.
5. §7 → one bar chart: MedGemma 0.50 · CONCH 0.78 · trained VLM 0.89 · supervised MIL 0.93, same 1,538 slides.
6. §6 → dots: grade 0.687 · CNV linear 0.663 · CNV-as-text 0.645 · grade+CNV text 0.751.
7. §8 → paired bars ABMIL vs tile-level, binary and six-class, both label schemes.
8. §11–12 → the failure-loop story as a one-slide "what 1,093 failed jobs taught us", if lessons are on the agenda.

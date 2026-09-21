# ERIN imminent-dysplasia task set — results (assembled 2026-09-21 22:41)

Pre-registration: `docs/erin_imminent_tasks_preregistration.md` (committed before the first job). Machinery: `scripts/abmil_clf.py` trainer, `patient_folds` (seed 0), 3 seeds, patient-clustered 2,000-replicate bootstraps, fold-local z-scored late fusion. No hyper-parameter tuning. Numbers only; the pre-registered rules say what they mean.

## Why these tasks
The 3-year progression experiment was infeasible (all scanned ERIN slides are 2022–2025; 0 negatives at 3 years — `reports/erin_progression_fusion.md`). These are the tasks the same window CAN support: imminent dysplasia within a year, next-report upgrade, synchronous dysplasia elsewhere in the case (field effect), and prior dysplasia in the patient's history.

## Cohort counts
| task | definition | n | pos | neg | patients | slides | status |
|---|---|---|---|---|---|---|---|
| T1 | first NDBE/IND report → HGD/cancer ≤ 1 y (FEASIBILITY ONLY) | 48 | 18 | 30 | 48 | 181 | feasibility only |
| T2a | benign report (landmark) → LGD+ ≤ 1 y — PRIMARY | 185 | 44 | 141 | 156 | 564 | interpretable |
| T2b | benign report → HGD+ ≤ 1 y | 183 | 30 | 153 | 155 | 535 | interpretable |
| T2c | benign report → next report LGD+ | 389 | 45 | 344 | 289 | 1212 | interpretable |
| T4 | benign report → prior LGD+ in history | 1147 | 518 | 629 | 874 | 3886 | interpretable |
| T3a | benign-section slide → case has LGD+ elsewhere (field effect) | 1274 | 146 | 1128 | 1056 | 1274 | interpretable |
| T3b | benign-section slide → case has HGD+ elsewhere | 1274 | 90 | 1184 | 1056 | 1274 | interpretable |

## Per-arm metrics (patient-level where one sample per patient; landmark tasks have several samples per patient — bootstraps resample patients)
| task | arm | AUROC [95% CI] | AUPRC [95% CI] | Brier | spec@sens0.95 | spec@sens1.0 | sens@spec0.80 | image units |
|---|---|---|---|---|---|---|---|---|
| T1 | baseline (grade+age) | 0.6222 [0.4541, 0.7813] | 0.4566 [0.3005, 0.695] | 0.2473 | 0.0333 | 0.0333 | 0.1667 | 15/15 |
| T1 | text (nomic embedding) | 0.7278 [0.5535, 0.8803] | 0.6622 [0.4647, 0.8835] | 0.2039 | 0.0667 | 0.0667 | 0.6111 | 15/15 |
| T1 | image (ABMIL, UNI2) | 0.8481 [0.7241, 0.9535] | 0.8426 [0.6939, 0.951] | 0.14 | 0.4 | 0.4 | 0.7222 | 15/15 |
| T1 | late-mean fusion b+c | 0.9093 [0.7983, 0.9877] | 0.8991 [0.7737, 0.9831] | 0.1549 | 0.2 | 0.2 | 0.8333 | 15/15 |
| T2a | baseline (grade+age) | 0.7086 [0.6198, 0.7978] | 0.3987 [0.284, 0.5672] | 0.2168 | 0.305 | 0.1064 | 0.4318 | 15/15 |
| T2a | text (nomic embedding) | 0.6139 [0.5054, 0.7115] | 0.333 [0.2072, 0.507] | 0.2621 | 0.1489 | 0.0851 | 0.2727 | 15/15 |
| T2a | image (ABMIL, UNI2) | 0.8174 [0.725, 0.892] | 0.6202 [0.4473, 0.7945] | 0.1612 | 0.2766 | 0.0993 | 0.6591 | 15/15 |
| T2a | late-mean fusion b+c | 0.7747 [0.6867, 0.8499] | 0.5226 [0.3528, 0.6867] | 0.2161 | 0.3688 | 0.0993 | 0.5682 | 15/15 |
| T2b | baseline (grade+age) | 0.6294 [0.5193, 0.7307] | 0.2302 [0.1361, 0.3739] | 0.2354 | 0.268 | 0.0654 | 0.3333 | 15/15 |
| T2b | text (nomic embedding) | 0.6597 [0.55, 0.774] | 0.3193 [0.1698, 0.5101] | 0.1829 | 0.183 | 0.1046 | 0.3667 | 15/15 |
| T2b | image (ABMIL, UNI2) | 0.8619 [0.7885, 0.9199] | 0.5424 [0.3473, 0.752] | 0.1379 | 0.6405 | 0.549 | 0.6667 | 15/15 |
| T2b | late-mean fusion b+c | 0.8257 [0.7514, 0.8896] | 0.4617 [0.2853, 0.6588] | 0.2192 | 0.5033 | 0.4641 | 0.7333 | 15/15 |
| T2c | baseline (grade+age) | 0.6488 [0.5634, 0.727] | 0.1689 [0.1174, 0.2477] | 0.2351 | 0.125 | 0.0756 | 0.4222 | 15/15 |
| T2c | text (nomic embedding) | 0.6522 [0.5709, 0.7293] | 0.1874 [0.1263, 0.2869] | 0.1733 | 0.1977 | 0.0552 | 0.3111 | 15/15 |
| T2c | image (ABMIL, UNI2) | 0.6608 [0.5686, 0.745] | 0.2595 [0.163, 0.4088] | 0.1832 | 0.1802 | 0.157 | 0.4222 | 15/15 |
| T2c | late-mean fusion b+c | 0.7049 [0.6276, 0.7794] | 0.25 [0.1618, 0.3866] | 0.2478 | 0.2645 | 0.1453 | 0.4444 | 15/15 |
| T3a | baseline (grade+age) | 0.5771 [0.5297, 0.6254] | 0.1452 [0.1161, 0.1844] | 0.2454 | 0.078 | 0.0089 | 0.2534 | 15/15 |
| T3a | image (ABMIL, UNI2) | 0.821 [0.7791, 0.8608] | 0.5288 [0.4483, 0.6157] | 0.1166 | 0.1223 | 0.0044 | 0.7055 | 15/15 |
| T3b | baseline (grade+age) | 0.6078 [0.545, 0.6648] | 0.0968 [0.0744, 0.1339] | 0.236 | 0.0431 | 0.0177 | 0.3 | 15/15 |
| T3b | image (ABMIL, UNI2) | 0.8692 [0.8237, 0.9105] | 0.4967 [0.3931, 0.6115] | 0.0737 | 0.4037 | 0.0152 | 0.7778 | 15/15 |
| T4 | baseline (grade+age) | 0.5499 [0.5088, 0.5925] | 0.4832 [0.4347, 0.5351] | 0.2465 | 0.1399 | 0.0111 | 0.2432 | 15/15 |
| T4 | image (ABMIL, UNI2) | 0.7802 [0.747, 0.8089] | 0.7271 [0.6738, 0.7779] | 0.1953 | 0.1908 | 0.0191 | 0.6409 | 15/15 |

## Paired deltas (AUROC, patient-clustered 95% CI)
| task | contrast | delta | CI | rule |
|---|---|---|---|---|
| T1 | image - baseline | 0.2259 | [0.0569, 0.398] | feasibility only — not interpreted |
| T1 | text - baseline | 0.1056 | [-0.125, 0.3072] | feasibility only — not interpreted |
| T1 | late_mean - best single (c) | 0.0611 | [-0.0388, 0.1807] | feasibility only — not interpreted |
| T2a | image - baseline | 0.1088 | [-0.0283, 0.2341] | CI includes 0 |
| T2a | text - baseline | -0.0947 | [-0.2353, 0.0348] | CI includes 0 |
| T2a | late_mean - best single (c) | -0.0427 | [-0.0965, 0.0163] | CI includes 0 |
| T2b | image - baseline | 0.2325 | [0.1227, 0.3493] | CI excludes 0 (positive) |
| T2b | text - baseline | 0.0303 | [-0.0952, 0.1681] | CI includes 0 |
| T2b | late_mean - best single (c) | -0.0362 | [-0.0824, 0.0104] | CI includes 0 |
| T2c | image - baseline | 0.012 | [-0.0912, 0.1176] | CI includes 0 |
| T2c | text - baseline | 0.0033 | [-0.1096, 0.1248] | CI includes 0 |
| T2c | late_mean - best single (c) | 0.0441 | [-0.0232, 0.1254] | CI includes 0 |
| T3a | image - baseline | 0.2438 | [0.182, 0.3077] | CI excludes 0 (positive) |
| T3b | image - baseline | 0.2614 | [0.1926, 0.3286] | CI excludes 0 (positive) |
| T4 | image - baseline | 0.2303 | [0.1754, 0.2811] | CI excludes 0 (positive) |

## Permutation null (T2a)
- perm_null_c: 50 permutations, null mean 0.5088, 95th pct 0.6228, empirical p = 0.0196
- perm_null_d: 50 permutations, null mean 0.5188, 95th pct 0.6097, empirical p = 0.0196

## Tile-count confound (AUROC of tile count alone for the image task label)
- T1: 0.425
- T2a: 0.568
- T2b: 0.5363
- T2c: 0.5334
- T3a: 0.5157
- T3b: 0.5344
- T4: 0.4017

## What the pre-registered rules say

- **T2a primary (fusion vs best single modality):** delta -0.0427 [-0.0965, 0.0163] → no demonstrated fusion gain (rule: CI must exclude 0).
- T2a image − baseline: 0.1088 [-0.0283, 0.2341] → not demonstrated (benign report (landmark) → LGD+ ≤ 1 y — PRIMARY).
- T2b image − baseline: 0.2325 [0.1227, 0.3493] → the image carries information beyond grade + age (benign report → HGD+ ≤ 1 y).
- T2c image − baseline: 0.012 [-0.0912, 0.1176] → not demonstrated (benign report → next report LGD+).
- T3a image − baseline: 0.2438 [0.182, 0.3077] → the image carries information beyond grade + age (benign-section slide → case has LGD+ elsewhere (field effect)).
- T3b image − baseline: 0.2614 [0.1926, 0.3286] → the image carries information beyond grade + age (benign-section slide → case has HGD+ elsewhere).
- T4 image − baseline: 0.2303 [0.1754, 0.2811] → the image carries information beyond grade + age (benign report → prior LGD+ in history).
- T1 is a feasibility run (18 positives): reported, not interpreted.
- All tasks live in the 2022–2025 imaging window with ≤ 3 years follow-up; none is 'progression prediction' in the SWG sense.

## Not finished / caveats
- Image units per task are listed above; any task below 15/15 has an incomplete image arm.
- The text arm depends on the `nomic-embed-text` embedding task; if absent, arms b and d are missing.
- T2 landmark samples share patients (several benign reports per patient); folds are patient-disjoint but the effective n is the patient count.

## Decisions not pre-specified (to defend or change)
1. Slides capped at 1,500 tiles each when pooling a case bag (memory); ABMIL's own MAX_TILES=800 per-epoch subsample then applies.
2. Landmark tasks allow multiple reports per patient; a one-per-patient variant was not run.
3. Negative definition for the 1-year label: no LGD+/HGD+ event AND last report ≥ 365 days after the landmark.
4. Text arm embeds FinalDiagnosis + MicroscopicDescription only (no addenda), truncated at 6,000 characters.
5. Late fusion uses fold-local z-scoring (per 2.46), not the SWG release's pooled z-scoring.
6. Baseline for T3 uses section grade (NORMAL_OTHER vs NDBE) + age; for others index grade (NDBE vs IND) + age.

## Compute
GPU-hours by partition for the worker jobs (allocated GPUs × wall time, idle included): {'cuda': 14.99, 'h200': 5.74, 'epyc': 0.0}. Task→job log in `results/erin_progression_fusion/results.json` (`task_partition_log`).

## Figures
`results/erin_progression_fusion/figures/`: fig1_roc_T2a.png (+ roc_T2a_*.csv), fig2_forest_deltas.png (+ .csv), fig3_reliability_T2a_d.png (+ .csv).

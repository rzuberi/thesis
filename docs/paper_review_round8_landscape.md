# Round 8: mapping the strategy space (descriptive, step 1 of 3)

Status: PRE-SPECIFICATION (written 2026-10-20). Nothing below has been run. Results are appended under the line at the end in a later commit; this section is not edited afterwards.

## Why

The authors want to know what the cohort can say about **when sequencing is worth it**. Every sample has both an H&E slide and copy number, and most patients have several time points.

This round maps the whole space of reasonable surveillance strategies and modality questions in one descriptive pass. It is **hypothesis-generating only**: no result in this round is confirmatory. Multiple comparisons are many and are not adjusted; patterns are reported with intervals and labelled descriptive.

The plan has three steps:
1. **This document:** map the space.
2. **A panel of agents** (gastroenterologist, health economist, statistician, Nature Medicine editor, sceptic) reads the map and proposes one strategy.
3. **A separate pre-specification** fixes that strategy by a stated rule, runs its robustness checks and registers it for ACE-B.

No model is refitted; stored patient-grouped outer predictions and inner out-of-fold predictions are re-scored. No ACE-B file is read. Frozen bundles are unchanged. Population: the 571 pre-event samples (288 endoscopies, 75 patients, 32 progressors) of the 676 samples from 80 patients of the Killcoyne discovery cohort with a matched H&E slide. Conventions as in `docs/paper_review_round6_analyses.md`.

Single model = per-repeat values averaged over 10 repeats. Patient bootstrap: 2,000 draws, `RandomState(0)`, thresholds fixed. All thresholds come from training patients only: inner out-of-fold predictions within each outer fold.

## L1. Policy map (patient-level, longitudinal)

A policy is applied to each patient's pre-event endoscopies in time order. Each endoscopy's samples carry stored outer-fold predictions.

### Outcomes per policy

| Outcome | Definition |
|---|---|
| Progressor patients caught | of 32; flagged at ≥ 1 pre-event endoscopy |
| Time from first flag to event | median, progressors |
| Non-progressor patients ever flagged | of 43 |
| Flags per non-progressor patient-year | flagged non-progressor endoscopies ÷ patient-years |
| Equal-window measures | caught / flagged within each patient's last 2 pre-event endoscopies (reference: last sequenced endoscopy for non-progressors) |
| Sequencing | samples sequenced per patient, and per 100 patient-years |
| Cost per patient | £85 per sequenced sample + £535 per flagged endoscopy (£471 endoscopy + £44 review + £20 p53, as round 7d) |
| Endoscopy-level | sensitivity and specificity |

### Policies

Thresholds are set per fold on training patients, at the stated training endoscopy-sensitivity targets (grid shown).

| Policy | Rule | Grid |
|---|---|---|
| P1. H&E only | flag an endoscopy if max L-IMG ≥ t | t at 80/90/95% |
| P2. Copy number only, sequence all | flag if any sample's L-CNV ≥ t | same |
| P3. Sequence all, H&E + copy number | flag if any sample's L-LATE ≥ t | same |
| P4. One random sample per endoscopy | L-LATE, R41 seeds | same |
| P5. Sample-level triage | stored primary | the 9 cut-off cells |
| P6. R49 gate | as round 7 | the 9 cut-off cells |
| P7. Sequence once, then H&E | at the first pre-event endoscopy, sequence k samples and flag if max L-LATE over them ≥ t_b (always flag: the patient becomes "high risk"); at later endoscopies flag if max L-IMG ≥ t_s | k ∈ {1 top-H&E, 1 random, 2 top-H&E, all}; t_b and t_s at 80/90/95% |
| P8. Sequence once, re-sequence when H&E rises | as P7, but a later endoscopy with max L-IMG ≥ t_mid is sequenced (top sample) and flagged only if its L-LATE ≥ t_c | k = 1 top-H&E; t_mid at 80/90%; t_c at 90% |
| P9. Sequence every N years | at the first endoscopy and whenever ≥ N years have passed since the last sequencing, sequence the top-H&E sample and flag if L-LATE ≥ t; other endoscopies flag if max L-IMG ≥ t_s | N ∈ {2, 3, 5}; t, t_s at 90% |
| P10. Current care | grade ID/LGD; and grade ID/LGD or p53 aberrant on the 450-sample subset | none |

### Display

1. **Plot (a):** progressor patients caught against non-progressor patients ever flagged, one point per policy and grid cell, marker size = samples sequenced per patient.
2. **Plot (b):** the same with flags per non-progressor patient-year on the x-axis.
3. **Plot (c):** cost per patient against progressor patients caught.
4. **Frontier:** list the Pareto-efficient points, those not dominated on caught, false flags and sequencing.
5. **Table:** all points.

Policies whose thresholds cannot be met in a fold are reported as such.

## L2. Where copy number adds value

Δ = L-LATE − L-IMG in fold-stratified AUROC, with patient-bootstrap CI. Also the share of endoscopies whose call changes when copy number is added (P1 against P3 at matched training sensitivity 90%).

Strata:
- **H&E score:** quintiles of the repeat-mean L-IMG, both classes within the stratum.
- **Grade:** NDBE / ID / LGD.
- **Tissue:** tertile.
- **Time to event:** < 1, 1–3 and > 3 years; progressor samples of the stratum against all non-progressor samples.
- **Position:** first pre-event endoscopy against later ones.
- **Samples:** endoscopies with 1 against ≥ 2 samples.

Same strata for Δ = L-CNV − L-IMG.

## L3. Change over time within a patient

For patients with ≥ 2 pre-event endoscopies:
- **Slopes.** Per-patient slope of endoscopy max logit L-IMG, and of max logit L-CNV, against time to event (years; non-progressors against time to their last sequenced endoscopy). Compared between classes by the difference in mean slope with a patient-bootstrap CI.
- **Mixed models.** Linear mixed model logit-score ~ time × class with a patient random intercept, for each modality. Report the interaction.
- **Progressors.** Score at the last against the first pre-event endoscopy.
- **Time-dependent AUROC.** Re-tabulate the stored values next to these.

## L4. Disagreement within an endoscopy as a signal

For endoscopies with ≥ 2 samples:
- **Disagreement alone:** fold-stratified AUROC of the within-endoscopy SD of logit L-IMG, and of logit L-CNV.
- **Over the maximum:** of the max plus the SD (rank-sum combination, fixed equal weights).

Compared with the max alone. Also at patient level: the SD over all pre-event samples.

## L5. Who each modality misses

P1 (H&E only) and P2 (copy number only) are set to the same non-progressor ever-flagged rate (interpolated along each grid, per repeat). The analysis then:
- **cross-tabulates** the progressor patients caught by each (mean over repeats: both / H&E only / copy number only / neither);
- **describes discordant patients** in aggregate: grade history, number of endoscopies, time from first sample to event, tissue tertile, batch type and scanner.

Cells below 5 are shown as "< 5".

## Scripts and running

- **Script:** `scripts/paper_plan/rv8_landscape.py`, reusing the round-7 / 7b / 7c / 7d loaders and endoscopy helpers.
- **Figures:** `scripts/paper_plan/rv8_figs.py`, writing to `paper/figures_r8/` (not committed) from aggregate JSONs.
- **Execution:** cluster jobs via `campaign.sh`, prefix `rv8`.
- **Outputs:** aggregates to `results/paper_final/review_round8/`; results appended below by `rv8_render.py`.

---

## Results

Rendered by `scripts/paper_plan/rv8_render.py` from `results/paper_final/review_round8/` (aggregate results 63b3fe8); script `scripts/paper_plan/rv8_landscape.py`; figures by `scripts/paper_plan/rv8_figs.py` (local, not committed). **Everything below is descriptive and hypothesis-generating; no comparison is confirmatory and nothing is adjusted for multiplicity.** No model was refitted; stored patient-grouped outer and inner out-of-fold predictions were re-scored. Single model = per-repeat values averaged over the 10 repeats. Intervals: patient bootstrap, 2,000 draws (`RandomState(0)`), thresholds and calls fixed.

### Population, dates and availability

288 pre-event endoscopies (88 progressor), 571 samples, 75 patients (32 progressor, 43 non-progressor). Endoscopies per patient: progressors 2.75 (≥ 2 in 22), non-progressors 4.65 (≥ 2 in 43).

- Exact dates (`pre_event_cohort.Date`) for 676 of 676 analysed samples. Event date (progressors) = exact date of the sheet event endoscopy (first HGD/IMC endoscopy): 27 patients; 5 had no exact date on that endoscopy's samples and use the date implied by their analysed samples' exact dates and months before final. Last sequenced endoscopy (non-progressors) = latest exact date over the patient's sequenced samples on the sheet: 43 patients.
- Exact reference dates against those implied by months before final: progressors median 91 days (90th percentile 163, max 208; > 90 days in 15); non-progressors median 56 days (90th percentile 147, max 1458; > 90 days in 13). Progressor pre-event samples, years to event from exact dates against months before final: median absolute difference 0.27 years (max 1.14).
- Endoscopy units (patient, endoscopy number, as rounds 6–7d) whose samples carry more than one exact date: 19 (spread median 197 days, max 333; all dates in one calendar year in 19); the unit's date is its earliest sample date. Endoscopies dated after the reference date: 0; progressor pre-event endoscopies dated on the event date: <5. Exact-date order equals months-before-final order in 75 of 75 patients.
- Patient-years: progressors 172.3 (first pre-event endoscopy to event), non-progressors 282.6 (first pre-event endoscopy to last sequenced endoscopy; round 7d, months-before-final span: 285.5), all 454.9.
- Arrays: outer predictions finite in 10 repeats: yes; inner repeat × fold sets 100 (L-IMG) / 100 (L-CNV); stored time-dependent AUROC at 1 / 3 / 5 years: yes / yes / yes. Nothing was 'not available'.

### L1. Policy map

Per policy and grid cell (single model). Caught = progressor patients (of 32) flagged at ≥ 1 pre-event endoscopy; NP flagged = non-progressor patients (of 43) ever flagged; shares with 95% CI in brackets. Flags / NP py = flagged non-progressor endoscopies per non-progressor patient-year. First flag → event = median years over caught progressors. Last 2 = caught / NP flagged within each patient's last 2 pre-event endoscopies. Sequenced = samples per patient (per 100 patient-years). Cost = £85 per sequenced sample + £535 per flagged endoscopy, per patient (all 75). F = on the Pareto frontier (caught, NP flagged, samples sequenced); C = on the cost / caught frontier.

| Policy | Cell | Caught [share CI] | NP flagged [share CI] | Flags / NP py [CI] | First flag → event (y) | Last 2: caught / NP flagged | Sequenced / patient (/100 py) | Cost / patient [CI] | Endo sens / spec | Frontier |
|---|---|---|---|---|---|---|---|---|---|---|
| P1 | 80% | 30.1 / 32 [0.865, 0.994] | 31.6 / 43 [0.621, 0.838] | 0.241 [0.188, 0.304] | 4.37 | 30.0 / 22.2 | 0.00 (0.0) | £1,002 [£846, £1,170] | 0.820 / 0.659 | F C |
| P1 | 90% | 31.1 / 32 [0.921, 1.000] | 36.0 / 43 [0.729, 0.923] | 0.337 [0.271, 0.409] | 4.70 | 31.1 / 29.9 | 0.00 (0.0) | £1,242 [£1,075, £1,412] | 0.898 / 0.524 | F C |
| P1 | 95% | 31.9 / 32 [0.990, 1.000] | 39.3 / 43 [0.837, 0.970] | 0.446 [0.373, 0.530] | 4.76 | 31.9 / 35.6 | 0.00 (0.0) | £1,489 [£1,305, £1,678] | 0.942 / 0.370 | F C |
| P2 | 80% | 28.8 / 32 [0.803, 0.976] | 28.0 / 43 [0.532, 0.767] | 0.316 [0.229, 0.419] | 4.16 | 28.5 / 23.7 | 7.61 (125.5) | £1,796 [£1,524, £2,080] | 0.814 / 0.553 |  |
| P2 | 90% | 31.0 / 32 [0.933, 0.997] | 35.0 / 43 [0.724, 0.893] | 0.427 [0.336, 0.526] | 4.63 | 30.8 / 32.2 | 7.61 (125.5) | £2,082 [£1,808, £2,366] | 0.915 / 0.397 |  |
| P2 | 95% | 31.7 / 32 [0.974, 1.000] | 39.6 / 43 [0.867, 0.965] | 0.524 [0.444, 0.614] | 4.76 | 31.5 / 37.2 | 7.61 (125.5) | £2,306 [£2,044, £2,589] | 0.960 / 0.259 |  |
| P3 | 80% | 30.5 / 32 [0.888, 1.000] | 26.4 / 43 [0.485, 0.734] | 0.200 [0.144, 0.262] | 4.17 | 30.4 / 17.4 | 7.61 (125.5) | £1,579 [£1,359, £1,812] | 0.843 / 0.718 | F |
| P3 | 90% | 31.2 / 32 [0.929, 1.000] | 31.8 / 43 [0.626, 0.846] | 0.317 [0.239, 0.404] | 4.61 | 31.2 / 25.3 | 7.61 (125.5) | £1,860 [£1,606, £2,127] | 0.912 / 0.551 |  |
| P3 | 95% | 31.4 / 32 [0.950, 1.000] | 34.7 / 43 [0.708, 0.895] | 0.399 [0.312, 0.491] | 4.74 | 31.4 / 30.7 | 7.61 (125.5) | £2,055 [£1,786, £2,338] | 0.961 / 0.436 |  |
| P4 | 80% | 29.8 / 32 [0.867, 0.983] | 25.5 / 43 [0.465, 0.710] | 0.188 [0.137, 0.245] | 4.35 | 29.4 / 16.0 | 3.84 (63.3) | £1,225 [£1,032, £1,433] | 0.827 / 0.734 | F |
| P4 | 90% | 30.7 / 32 [0.909, 0.993] | 30.8 / 43 [0.605, 0.821] | 0.288 [0.218, 0.362] | 4.66 | 30.5 / 22.9 | 3.84 (63.3) | £1,478 [£1,262, £1,708] | 0.911 / 0.594 |  |
| P4 | 95% | 31.2 / 32 [0.938, 0.997] | 34.7 / 43 [0.716, 0.889] | 0.368 [0.290, 0.452] | 4.73 | 31.0 / 28.3 | 3.84 (63.3) | £1,667 [£1,442, £1,907] | 0.955 / 0.480 |  |
| P5 | t_low 90% / t_high 85% | 31.0 / 32 [0.924, 0.997] | 32.1 / 43 [0.633, 0.846] | 0.301 [0.232, 0.376] | 4.67 | 31.0 / 25.6 | 2.27 (37.4) | £1,362 [£1,165, £1,571] | 0.894 / 0.574 |  |
| P5 | t_low 90% / t_high 90% | 31.0 / 32 [0.924, 0.997] | 31.0 / 43 [0.602, 0.828] | 0.281 [0.214, 0.354] | 4.66 | 31.0 / 23.9 | 2.61 (43.0) | £1,344 [£1,143, £1,556] | 0.887 / 0.604 |  |
| P5 | t_low 90% / t_high 95% | 30.9 / 32 [0.915, 0.997] | 29.8 / 43 [0.567, 0.804] | 0.256 [0.193, 0.328] | 4.51 | 30.9 / 21.8 | 3.05 (50.3) | £1,319 [£1,114, £1,535] | 0.865 / 0.638 |  |
| P5 | t_low 95% / t_high 85% | 31.1 / 32 [0.928, 1.000] | 33.9 / 43 [0.685, 0.876] | 0.344 [0.268, 0.427] | 4.74 | 31.1 / 28.8 | 3.15 (52.0) | £1,539 [£1,325, £1,768] | 0.919 / 0.514 |  |
| P5 | t_low 95% / t_high 90% | 31.1 / 32 [0.928, 1.000] | 32.0 / 43 [0.632, 0.844] | 0.319 [0.244, 0.402] | 4.70 | 31.1 / 26.4 | 3.49 (57.5) | £1,511 [£1,293, £1,744] | 0.909 / 0.549 |  |
| P5 | t_low 95% / t_high 95% | 31.1 / 32 [0.928, 1.000] | 30.8 / 43 [0.597, 0.823] | 0.291 [0.219, 0.371] | 4.67 | 31.1 / 24.0 | 3.94 (64.9) | £1,484 [£1,263, £1,720] | 0.897 / 0.589 |  |
| P5 | t_low 98% / t_high 85% | 31.2 / 32 [0.938, 1.000] | 35.1 / 43 [0.721, 0.898] | 0.375 [0.293, 0.463] | 4.74 | 31.2 / 30.5 | 4.12 (68.0) | £1,698 [£1,462, £1,946] | 0.941 / 0.470 |  |
| P5 | t_low 98% / t_high 90% | 31.1 / 32 [0.928, 1.000] | 33.7 / 43 [0.680, 0.876] | 0.354 [0.273, 0.441] | 4.70 | 31.1 / 28.6 | 4.46 (73.6) | £1,677 [£1,441, £1,931] | 0.931 / 0.500 |  |
| P5 | t_low 98% / t_high 95% | 31.1 / 32 [0.928, 1.000] | 31.8 / 43 [0.627, 0.844] | 0.321 [0.242, 0.405] | 4.67 | 31.1 / 25.4 | 4.91 (80.9) | £1,639 [£1,403, £1,893] | 0.917 / 0.547 |  |
| P6 | t_low 90% / t_high 85% | 31.0 / 32 [0.924, 0.997] | 32.1 / 43 [0.633, 0.846] | 0.297 [0.229, 0.371] | 4.67 | 31.0 / 25.3 | 1.33 (21.9) | £1,274 [£1,088, £1,470] | 0.894 / 0.580 | F |
| P6 | t_low 90% / t_high 90% | 31.0 / 32 [0.924, 0.997] | 31.0 / 43 [0.602, 0.828] | 0.275 [0.210, 0.348] | 4.66 | 31.0 / 23.7 | 1.59 (26.2) | £1,247 [£1,058, £1,443] | 0.887 / 0.611 |  |
| P6 | t_low 90% / t_high 95% | 30.9 / 32 [0.915, 0.997] | 29.8 / 43 [0.567, 0.804] | 0.251 [0.188, 0.319] | 4.51 | 30.9 / 21.5 | 1.90 (31.3) | £1,210 [£1,022, £1,404] | 0.865 / 0.645 | C |
| P6 | t_low 95% / t_high 85% | 31.1 / 32 [0.928, 1.000] | 33.6 / 43 [0.676, 0.870] | 0.336 [0.261, 0.418] | 4.74 | 31.1 / 28.1 | 1.68 (27.6) | £1,395 [£1,203, £1,605] | 0.917 / 0.525 |  |
| P6 | t_low 95% / t_high 90% | 31.1 / 32 [0.928, 1.000] | 31.8 / 43 [0.627, 0.842] | 0.311 [0.238, 0.393] | 4.70 | 31.1 / 25.9 | 1.94 (32.0) | £1,362 [£1,167, £1,573] | 0.907 / 0.560 |  |
| P6 | t_low 95% / t_high 95% | 31.1 / 32 [0.928, 1.000] | 30.6 / 43 [0.591, 0.819] | 0.281 [0.212, 0.359] | 4.67 | 31.1 / 23.5 | 2.25 (37.0) | £1,320 [£1,123, £1,530] | 0.895 / 0.603 |  |
| P6 | t_low 98% / t_high 85% | 31.2 / 32 [0.938, 1.000] | 34.9 / 43 [0.714, 0.895] | 0.367 [0.288, 0.452] | 4.74 | 31.2 / 29.9 | 2.02 (33.4) | £1,499 [£1,294, £1,719] | 0.936 / 0.482 |  |
| P6 | t_low 98% / t_high 90% | 31.1 / 32 [0.928, 1.000] | 33.5 / 43 [0.674, 0.873] | 0.344 [0.266, 0.428] | 4.70 | 31.1 / 27.9 | 2.29 (37.7) | £1,469 [£1,265, £1,691] | 0.927 / 0.514 |  |
| P6 | t_low 98% / t_high 95% | 31.1 / 32 [0.928, 1.000] | 31.6 / 43 [0.619, 0.840] | 0.306 [0.232, 0.387] | 4.67 | 31.1 / 24.7 | 2.59 (42.7) | £1,412 [£1,210, £1,628] | 0.914 / 0.567 |  |
| P7 | k = 1 top-H&E; t_b 80%, t_s 80% | 30.9 / 32 [0.914, 0.997] | 31.2 / 43 [0.608, 0.830] | 0.312 [0.242, 0.388] | 4.30 | 30.9 / 25.9 | 1.00 (16.5) | £1,276 [£1,092, £1,475] | 0.897 / 0.560 | F |
| P7 | k = 1 top-H&E; t_b 80%, t_s 90% | 31.2 / 32 [0.922, 1.000] | 35.4 / 43 [0.713, 0.909] | 0.367 [0.294, 0.445] | 4.30 | 31.2 / 31.6 | 1.00 (16.5) | £1,398 [£1,209, £1,594] | 0.915 / 0.482 |  |
| P7 | k = 1 top-H&E; t_b 80%, t_s 95% | 31.2 / 32 [0.922, 1.000] | 39.0 / 43 [0.829, 0.965] | 0.433 [0.360, 0.513] | 4.32 | 31.2 / 36.5 | 1.00 (16.5) | £1,534 [£1,340, £1,740] | 0.918 / 0.388 |  |
| P7 | k = 1 top-H&E; t_b 90%, t_s 80% | 31.0 / 32 [0.924, 0.997] | 32.5 / 43 [0.641, 0.854] | 0.388 [0.301, 0.485] | 4.68 | 31.0 / 28.0 | 1.00 (16.5) | £1,457 [£1,248, £1,680] | 0.941 / 0.452 | F |
| P7 | k = 1 top-H&E; t_b 90%, t_s 90% | 31.3 / 32 [0.933, 1.000] | 36.1 / 43 [0.737, 0.922] | 0.430 [0.344, 0.524] | 4.67 | 31.3 / 32.7 | 1.00 (16.5) | £1,549 [£1,343, £1,771] | 0.952 / 0.393 |  |
| P7 | k = 1 top-H&E; t_b 90%, t_s 95% | 31.3 / 32 [0.933, 1.000] | 39.1 / 43 [0.832, 0.967] | 0.477 [0.395, 0.565] | 4.67 | 31.3 / 36.8 | 1.00 (16.5) | £1,646 [£1,434, £1,872] | 0.955 / 0.326 |  |
| P7 | k = 1 top-H&E; t_b 95%, t_s 80% | 31.4 / 32 [0.950, 1.000] | 33.5 / 43 [0.671, 0.871] | 0.439 [0.342, 0.545] | 4.74 | 31.4 / 30.2 | 1.00 (16.5) | £1,578 [£1,353, £1,817] | 0.967 / 0.379 | F |
| P7 | k = 1 top-H&E; t_b 95%, t_s 90% | 31.6 / 32 [0.957, 1.000] | 36.9 / 43 [0.760, 0.933] | 0.472 [0.378, 0.575] | 4.77 | 31.6 / 33.9 | 1.00 (16.5) | £1,649 [£1,427, £1,882] | 0.975 / 0.332 | F |
| P7 | k = 1 top-H&E; t_b 95%, t_s 95% | 31.6 / 32 [0.957, 1.000] | 39.5 / 43 [0.843, 0.973] | 0.511 [0.422, 0.606] | 4.77 | 31.6 / 37.6 | 1.00 (16.5) | £1,728 [£1,514, £1,959] | 0.977 / 0.279 |  |
| P7 | k = 1 random; t_b 80%, t_s 80% | 30.5 / 32 [0.896, 0.989] | 31.4 / 43 [0.616, 0.834] | 0.324 [0.250, 0.405] | 4.51 | 30.5 / 26.1 | 1.00 (16.5) | £1,311 [£1,114, £1,512] | 0.911 / 0.542 |  |
| P7 | k = 1 random; t_b 80%, t_s 90% | 30.8 / 32 [0.905, 0.996] | 35.6 / 43 [0.718, 0.911] | 0.375 [0.299, 0.457] | 4.52 | 30.8 / 31.7 | 1.00 (16.5) | £1,422 [£1,224, £1,623] | 0.925 / 0.470 |  |
| P7 | k = 1 random; t_b 80%, t_s 95% | 30.8 / 32 [0.905, 0.996] | 39.0 / 43 [0.829, 0.965] | 0.436 [0.361, 0.517] | 4.53 | 30.8 / 36.4 | 1.00 (16.5) | £1,547 [£1,350, £1,755] | 0.928 / 0.384 |  |
| P7 | k = 1 random; t_b 90%, t_s 80% | 30.9 / 32 [0.915, 0.995] | 32.6 / 43 [0.647, 0.855] | 0.390 [0.303, 0.486] | 4.73 | 30.9 / 28.4 | 1.00 (16.5) | £1,468 [£1,249, £1,696] | 0.951 / 0.449 |  |
| P7 | k = 1 random; t_b 90%, t_s 90% | 31.1 / 32 [0.922, 0.999] | 36.2 / 43 [0.743, 0.924] | 0.430 [0.345, 0.526] | 4.75 | 31.1 / 33.0 | 1.00 (16.5) | £1,555 [£1,341, £1,778] | 0.960 / 0.392 |  |
| P7 | k = 1 random; t_b 90%, t_s 95% | 31.1 / 32 [0.922, 0.999] | 39.2 / 43 [0.834, 0.968] | 0.478 [0.394, 0.569] | 4.75 | 31.1 / 37.2 | 1.00 (16.5) | £1,653 [£1,441, £1,875] | 0.962 / 0.325 |  |
| P7 | k = 1 random; t_b 95%, t_s 80% | 31.2 / 32 [0.939, 1.000] | 33.9 / 43 [0.681, 0.875] | 0.442 [0.347, 0.548] | 4.75 | 31.2 / 30.5 | 1.00 (16.5) | £1,590 [£1,367, £1,826] | 0.977 / 0.375 |  |
| P7 | k = 1 random; t_b 95%, t_s 90% | 31.4 / 32 [0.945, 1.000] | 36.9 / 43 [0.765, 0.932] | 0.474 [0.382, 0.576] | 4.78 | 31.4 / 34.1 | 1.00 (16.5) | £1,657 [£1,440, £1,889] | 0.982 / 0.330 |  |
| P7 | k = 1 random; t_b 95%, t_s 95% | 31.4 / 32 [0.945, 1.000] | 39.5 / 43 [0.843, 0.973] | 0.511 [0.424, 0.606] | 4.78 | 31.4 / 37.8 | 1.00 (16.5) | £1,733 [£1,521, £1,963] | 0.984 / 0.278 |  |
| P7 | k = 2 top-H&E; t_b 80%, t_s 80% | 30.9 / 32 [0.914, 0.997] | 31.2 / 43 [0.608, 0.830] | 0.312 [0.240, 0.389] | 4.30 | 30.9 / 26.0 | 1.39 (22.9) | £1,311 [£1,125, £1,511] | 0.899 / 0.559 |  |
| P7 | k = 2 top-H&E; t_b 80%, t_s 90% | 31.2 / 32 [0.922, 1.000] | 35.4 / 43 [0.713, 0.909] | 0.367 [0.295, 0.445] | 4.30 | 31.2 / 31.6 | 1.39 (22.9) | £1,433 [£1,244, £1,632] | 0.917 / 0.482 |  |
| P7 | k = 2 top-H&E; t_b 80%, t_s 95% | 31.2 / 32 [0.922, 1.000] | 39.0 / 43 [0.829, 0.965] | 0.434 [0.361, 0.513] | 4.32 | 31.2 / 36.5 | 1.39 (22.9) | £1,571 [£1,375, £1,775] | 0.920 / 0.387 |  |
| P7 | k = 2 top-H&E; t_b 90%, t_s 80% | 31.0 / 32 [0.924, 0.997] | 32.6 / 43 [0.643, 0.856] | 0.393 [0.303, 0.491] | 4.67 | 31.0 / 28.2 | 1.39 (22.9) | £1,502 [£1,291, £1,729] | 0.941 / 0.444 |  |
| P7 | k = 2 top-H&E; t_b 90%, t_s 90% | 31.3 / 32 [0.933, 1.000] | 36.2 / 43 [0.740, 0.923] | 0.435 [0.347, 0.528] | 4.66 | 31.3 / 32.8 | 1.39 (22.9) | £1,592 [£1,378, £1,820] | 0.952 / 0.386 |  |
| P7 | k = 2 top-H&E; t_b 90%, t_s 95% | 31.3 / 32 [0.933, 1.000] | 39.1 / 43 [0.832, 0.967] | 0.480 [0.397, 0.569] | 4.66 | 31.3 / 36.8 | 1.39 (22.9) | £1,685 [£1,476, £1,909] | 0.955 / 0.322 |  |
| P7 | k = 2 top-H&E; t_b 95%, t_s 80% | 31.3 / 32 [0.948, 1.000] | 33.6 / 43 [0.673, 0.873] | 0.445 [0.346, 0.555] | 4.75 | 31.3 / 30.3 | 1.39 (22.9) | £1,622 [£1,395, £1,863] | 0.967 / 0.371 |  |
| P7 | k = 2 top-H&E; t_b 95%, t_s 90% | 31.5 / 32 [0.955, 1.000] | 37.0 / 43 [0.763, 0.936] | 0.477 [0.382, 0.580] | 4.78 | 31.5 / 34.0 | 1.39 (22.9) | £1,692 [£1,467, £1,927] | 0.975 / 0.326 |  |
| P7 | k = 2 top-H&E; t_b 95%, t_s 95% | 31.5 / 32 [0.955, 1.000] | 39.5 / 43 [0.843, 0.973] | 0.515 [0.426, 0.611] | 4.78 | 31.5 / 37.6 | 1.39 (22.9) | £1,769 [£1,554, £2,000] | 0.977 / 0.273 |  |
| P7 | k = all; t_b 80%, t_s 80% | 30.9 / 32 [0.914, 0.997] | 31.2 / 43 [0.608, 0.830] | 0.312 [0.240, 0.389] | 4.30 | 30.9 / 26.0 | 1.87 (30.8) | £1,353 [£1,166, £1,553] | 0.899 / 0.558 |  |
| P7 | k = all; t_b 80%, t_s 90% | 31.2 / 32 [0.922, 1.000] | 35.4 / 43 [0.713, 0.909] | 0.367 [0.295, 0.445] | 4.30 | 31.2 / 31.6 | 1.87 (30.8) | £1,475 [£1,281, £1,679] | 0.917 / 0.481 |  |
| P7 | k = all; t_b 80%, t_s 95% | 31.2 / 32 [0.922, 1.000] | 39.0 / 43 [0.829, 0.965] | 0.435 [0.362, 0.513] | 4.32 | 31.2 / 36.5 | 1.87 (30.8) | £1,612 [£1,418, £1,818] | 0.920 / 0.386 |  |
| P7 | k = all; t_b 90%, t_s 80% | 31.0 / 32 [0.924, 0.997] | 32.6 / 43 [0.643, 0.856] | 0.395 [0.305, 0.493] | 4.67 | 31.0 / 28.3 | 1.87 (30.8) | £1,545 [£1,331, £1,777] | 0.940 / 0.442 |  |
| P7 | k = all; t_b 90%, t_s 90% | 31.3 / 32 [0.933, 1.000] | 36.2 / 43 [0.740, 0.923] | 0.436 [0.348, 0.531] | 4.66 | 31.3 / 32.8 | 1.87 (30.8) | £1,635 [£1,419, £1,860] | 0.951 / 0.384 |  |
| P7 | k = all; t_b 90%, t_s 95% | 31.3 / 32 [0.933, 1.000] | 39.1 / 43 [0.832, 0.967] | 0.481 [0.397, 0.570] | 4.66 | 31.3 / 36.8 | 1.87 (30.8) | £1,727 [£1,514, £1,951] | 0.953 / 0.320 |  |
| P7 | k = all; t_b 95%, t_s 80% | 31.3 / 32 [0.948, 1.000] | 33.6 / 43 [0.673, 0.873] | 0.446 [0.346, 0.555] | 4.75 | 31.3 / 30.3 | 1.87 (30.8) | £1,664 [£1,433, £1,909] | 0.967 / 0.370 |  |
| P7 | k = all; t_b 95%, t_s 90% | 31.5 / 32 [0.955, 1.000] | 37.0 / 43 [0.763, 0.936] | 0.478 [0.383, 0.581] | 4.78 | 31.5 / 34.0 | 1.87 (30.8) | £1,734 [£1,509, £1,973] | 0.975 / 0.325 |  |
| P7 | k = all; t_b 95%, t_s 95% | 31.5 / 32 [0.955, 1.000] | 39.5 / 43 [0.843, 0.973] | 0.515 [0.427, 0.612] | 4.78 | 31.5 / 37.6 | 1.87 (30.8) | £1,811 [£1,591, £2,043] | 0.977 / 0.272 |  |
| P8 | t_b 80%, t_mid 80%, t_c 90% | 30.9 / 32 [0.914, 0.997] | 28.7 / 43 [0.538, 0.786] | 0.289 [0.217, 0.362] | 4.30 | 30.9 / 23.0 | 1.70 (28.1) | £1,289 [£1,096, £1,495] | 0.895 / 0.592 | F |
| P8 | t_b 80%, t_mid 90%, t_c 90% | 31.0 / 32 [0.917, 1.000] | 29.3 / 43 [0.553, 0.797] | 0.302 [0.228, 0.380] | 4.29 | 31.0 / 24.5 | 1.93 (31.8) | £1,343 [£1,140, £1,556] | 0.907 / 0.573 | F |
| P8 | t_b 90%, t_mid 80%, t_c 90% | 31.0 / 32 [0.924, 0.997] | 30.2 / 43 [0.578, 0.813] | 0.369 [0.282, 0.467] | 4.68 | 31.0 / 25.4 | 1.47 (24.2) | £1,459 [£1,243, £1,685] | 0.940 / 0.479 | F |
| P8 | t_b 90%, t_mid 90%, t_c 90% | 31.1 / 32 [0.928, 1.000] | 30.4 / 43 [0.584, 0.816] | 0.378 [0.288, 0.475] | 4.65 | 31.1 / 26.3 | 1.64 (27.1) | £1,493 [£1,274, £1,727] | 0.944 / 0.466 | F |
| P8 | t_b 95%, t_mid 80%, t_c 90% | 31.4 / 32 [0.950, 1.000] | 31.4 / 43 [0.611, 0.836] | 0.423 [0.325, 0.530] | 4.74 | 31.4 / 27.7 | 1.33 (22.0) | £1,572 [£1,345, £1,813] | 0.966 / 0.402 | F |
| P8 | t_b 95%, t_mid 90%, t_c 90% | 31.4 / 32 [0.950, 1.000] | 31.6 / 43 [0.620, 0.840] | 0.428 [0.330, 0.535] | 4.74 | 31.4 / 28.2 | 1.47 (24.2) | £1,595 [£1,369, £1,840] | 0.967 / 0.395 |  |
| P9 | N = 2 years; t, t_s 90% | 31.1 / 32 [0.928, 1.000] | 33.4 / 43 [0.663, 0.874] | 0.312 [0.245, 0.385] | 4.65 | 31.1 / 26.7 | 2.53 (41.8) | £1,416 [£1,215, £1,625] | 0.909 / 0.558 |  |
| P9 | N = 3 years; t, t_s 90% | 31.3 / 32 [0.933, 1.000] | 34.2 / 43 [0.684, 0.888] | 0.320 [0.254, 0.395] | 4.67 | 31.3 / 27.6 | 2.07 (34.1) | £1,395 [£1,202, £1,600] | 0.915 / 0.548 |  |
| P9 | N = 5 years; t, t_s 90% | 31.3 / 32 [0.933, 1.000] | 35.4 / 43 [0.713, 0.912] | 0.317 [0.252, 0.389] | 4.67 | 31.3 / 29.3 | 1.60 (26.4) | £1,348 [£1,162, £1,539] | 0.912 / 0.552 | C |
| P10 | grade ID/LGD (all pre-event endoscopies) | 17.0 / 32 [0.364, 0.714] | 25.0 / 43 [0.432, 0.720] | 0.170 [0.117, 0.234] | 3.28 | 17.0 / 4.0 | 0.00 (0.0) | £571 [£428, £728] | 0.364 / 0.760 | F C |
| P10 | grade ID/LGD or p53 aberrant (samples with p53) | 19.0 / 31 [0.437, 0.788] | 22.0 / 40 [0.400, 0.692] | 0.161 [0.105, 0.228] | 2.20 | 19.0 / 4.0 | 0.00 (0.0) | £520 [£391, £654] | 0.419 / 0.728 |  |

Folds in which a training sensitivity target could not be met: 0 (over all policies and cells). P5 / P6 folds without a middle band, summed over the 9 cells: P5 0, P6 0. The P10 grade-or-p53 row uses only samples with a p53 result (its own patients; counts of its own denominators) and is excluded from both frontiers.

**Pareto frontier** (not dominated on caught, non-progressor patients ever flagged and samples sequenced per patient):

| Policy | Cell | Caught | NP flagged | Sequenced / patient | Flags / NP py | Cost / patient | Endo sens / spec |
|---|---|---|---|---|---|---|---|
| P1 | 80% | 30.1 | 31.6 | 0.00 | 0.241 | £1,002 | 0.820 / 0.659 |
| P1 | 90% | 31.1 | 36.0 | 0.00 | 0.337 | £1,242 | 0.898 / 0.524 |
| P1 | 95% | 31.9 | 39.3 | 0.00 | 0.446 | £1,489 | 0.942 / 0.370 |
| P3 | 80% | 30.5 | 26.4 | 7.61 | 0.200 | £1,579 | 0.843 / 0.718 |
| P4 | 80% | 29.8 | 25.5 | 3.84 | 0.188 | £1,225 | 0.827 / 0.734 |
| P6 | t_low 90% / t_high 85% | 31.0 | 32.1 | 1.33 | 0.297 | £1,274 | 0.894 / 0.580 |
| P7 | k = 1 top-H&E; t_b 80%, t_s 80% | 30.9 | 31.2 | 1.00 | 0.312 | £1,276 | 0.897 / 0.560 |
| P7 | k = 1 top-H&E; t_b 90%, t_s 80% | 31.0 | 32.5 | 1.00 | 0.388 | £1,457 | 0.941 / 0.452 |
| P7 | k = 1 top-H&E; t_b 95%, t_s 80% | 31.4 | 33.5 | 1.00 | 0.439 | £1,578 | 0.967 / 0.379 |
| P7 | k = 1 top-H&E; t_b 95%, t_s 90% | 31.6 | 36.9 | 1.00 | 0.472 | £1,649 | 0.975 / 0.332 |
| P8 | t_b 80%, t_mid 80%, t_c 90% | 30.9 | 28.7 | 1.70 | 0.289 | £1,289 | 0.895 / 0.592 |
| P8 | t_b 80%, t_mid 90%, t_c 90% | 31.0 | 29.3 | 1.93 | 0.302 | £1,343 | 0.907 / 0.573 |
| P8 | t_b 90%, t_mid 80%, t_c 90% | 31.0 | 30.2 | 1.47 | 0.369 | £1,459 | 0.940 / 0.479 |
| P8 | t_b 90%, t_mid 90%, t_c 90% | 31.1 | 30.4 | 1.64 | 0.378 | £1,493 | 0.944 / 0.466 |
| P8 | t_b 95%, t_mid 80%, t_c 90% | 31.4 | 31.4 | 1.33 | 0.423 | £1,572 | 0.966 / 0.402 |
| P10 | grade ID/LGD (all pre-event endoscopies) | 17.0 | 25.0 | 0.00 | 0.170 | £571 | 0.364 / 0.760 |

**Cost / caught frontier:** P10 grade ID/LGD (all pre-event endoscopies) (17.0 caught, £571); P1 80% (30.1 caught, £1,002); P6 t_low 90% / t_high 95% (30.9 caught, £1,210); P1 90% (31.1 caught, £1,242); P9 N = 5 years; t, t_s 90% (31.3 caught, £1,348); P1 95% (31.9 caught, £1,489).

**Checks**

- P6 primary cell (t_low 95% / t_high 90%) against R49: endoscopy sens / spec 0.907 / 0.560, samples sequenced 25.5%, progressor patients missed 0.9, non-progressor patients flagged 31.8 (R49: 0.907 / 0.560, 25.5%, 0.9, 31.8); reproduced: yes.
- P5 primary cell against the round-7 triage aggregated to endoscopies: 0.909 / 0.549, 45.8%, missed 0.9, flagged 32.0 (expected 0.909 / 0.549, 45.8%, 0.9, 32.0); reproduced: yes.
- P3 at the B\* operating point (round-7 B\* sample threshold, endoscopy flagged if any sample is): 0.923 / 0.530 (B\*-endo 0.923 / 0.530); reproduced: yes. Nearest P3 grid cell: 90% (0.912 / 0.551).
- P10 grade ID/LGD per patient: 15 missed / 25 flagged (Table 1 (D): 15 / 25); reproduced: yes.

### L2. Where copy number adds value

Fold-stratified AUROC on pre-event samples within each stratum (single model), Δ with 95% patient-bootstrap CI. Call change = share of endoscopy × repeat cells whose P1 and P3 calls at 90% training endoscopy sensitivity differ (progressor / non-progressor endoscopies); gained / lost = P3 flags and P1 does not / P1 flags and P3 does not.

| Stratum | Samples (progressor) / patients (progressor) | AUROC L-IMG / L-CNV / L-LATE | Δ L-LATE − L-IMG [CI] | Δ L-CNV − L-IMG [CI] | Endoscopies (progressor) | Call change P / NP | Progressor gained / lost | NP gained / lost |
|---|---|---|---|---|---|---|---|---|
| all pre-event samples | 571 (161) / 75 (32) | 0.847 / 0.801 / 0.889 | +0.042 [+0.002, +0.078] | -0.045 [-0.136, +0.036] | 288 (88) | 0.108 / 0.238 | 0.061 / 0.047 | 0.105 / 0.133 |
| H&E score quintile 1 | 114 (<5) / 35 (<5) | 0.582 / 0.665 / 0.676 | +0.094 [-0.109, +0.366] | +0.083 [-0.117, +0.366] | 28 (0) | n/a / 0.132 | n/a / n/a | 0.132 / 0.000 |
| H&E score quintile 2 | 114 (13) / 51 (10) | 0.635 / 0.824 / 0.831 | +0.196 [-0.019, +0.361] | +0.189 [-0.028, +0.352] | 44 (<5) | 0.675 / 0.247 | 0.650 / 0.025 | 0.225 / 0.022 |
| H&E score quintile 3 | 114 (18) / 51 (12) | 0.592 / 0.826 / 0.816 | +0.224 [+0.104, +0.329] | +0.234 [+0.095, +0.354] | 52 (6) | 0.400 / 0.337 | 0.333 / 0.067 | 0.135 / 0.202 |
| H&E score quintile 4 | 114 (41) / 54 (22) | 0.571 / 0.774 / 0.743 | +0.172 [+0.069, +0.274] | +0.203 [+0.070, +0.324] | 88 (28) | 0.146 / 0.303 | 0.029 / 0.118 | 0.037 / 0.267 |
| H&E score quintile 5 | 115 (86) / 43 (26) | 0.752 / 0.712 / 0.756 | +0.004 [-0.137, +0.153] | -0.040 [-0.205, +0.136] | 76 (50) | 0.006 / 0.012 | 0.000 / 0.006 | 0.000 / 0.012 |
| NDBE | 438 (104) / 71 (28) | 0.827 / 0.780 / 0.867 | +0.040 [-0.005, +0.081] | -0.047 [-0.147, +0.041] | 208 (56) | 0.141 / 0.235 | 0.084 / 0.057 | 0.112 / 0.123 |
| ID | 66 (15) / 30 (9) | 0.851 / 0.861 / 0.920 | +0.069 [-0.009, +0.157] | +0.011 [-0.221, +0.172] | 33 (7) | 0.114 / 0.288 | 0.057 / 0.057 | 0.108 / 0.181 |
| LGD | 67 (42) / 30 (14) | 0.892 / 0.789 / 0.925 | +0.033 [-0.034, +0.103] | -0.103 [-0.291, +0.056] | 47 (25) | 0.032 / 0.200 | 0.012 / 0.020 | 0.059 / 0.141 |
| tissue tertile 1 | 192 (49) / 62 (23) | 0.910 / 0.760 / 0.925 | +0.016 [-0.031, +0.062] | -0.149 [-0.283, -0.022] | 96 (28) | 0.071 / 0.231 | 0.018 / 0.054 | 0.103 / 0.128 |
| tissue tertile 2 | 192 (40) / 59 (19) | 0.894 / 0.864 / 0.936 | +0.042 [+0.010, +0.081] | -0.031 [-0.120, +0.054] | 85 (24) | 0.125 / 0.254 | 0.092 / 0.033 | 0.095 / 0.159 |
| tissue tertile 3 | 187 (72) / 61 (23) | 0.746 / 0.802 / 0.837 | +0.091 [+0.019, +0.154] | +0.056 [-0.080, +0.162] | 107 (36) | 0.125 / 0.231 | 0.075 / 0.050 | 0.117 / 0.114 |
| < 1 year | 430 (20) / 53 (10) | 0.870 / 0.882 / 0.962 | +0.092 [+0.012, +0.199] | +0.012 [-0.168, +0.209] | 210 (10) | 0.090 / 0.238 | 0.090 / 0.000 | 0.105 / 0.133 |
| 1-3 years | 480 (70) / 65 (22) | 0.845 / 0.822 / 0.887 | +0.042 [+0.001, +0.088] | -0.023 [-0.120, +0.071] | 228 (28) | 0.054 / 0.238 | 0.043 / 0.011 | 0.105 / 0.133 |
| > 3 years | 481 (71) / 65 (22) | 0.842 / 0.758 / 0.869 | +0.027 [-0.025, +0.075] | -0.084 [-0.208, +0.032] | 250 (50) | 0.142 / 0.238 | 0.066 / 0.076 | 0.105 / 0.133 |
| first pre-event endoscopy | 140 (61) / 75 (32) | 0.847 / 0.812 / 0.908 | +0.061 [-0.004, +0.130] | -0.035 [-0.175, +0.098] | 75 (32) | 0.159 / 0.200 | 0.091 / 0.069 | 0.079 / 0.121 |
| later endoscopies | 431 (100) / 65 (22) | 0.841 / 0.803 / 0.880 | +0.039 [-0.004, +0.080] | -0.037 [-0.135, +0.051] | 213 (56) | 0.079 / 0.248 | 0.045 / 0.034 | 0.113 / 0.136 |
| endoscopies with 1 sample | 142 (48) / 52 (21) | 0.808 / 0.810 / 0.869 | +0.061 [-0.016, +0.130] | +0.002 [-0.152, +0.119] | 142 (48) | 0.146 / 0.210 | 0.077 / 0.069 | 0.093 / 0.117 |
| endoscopies with >= 2 samples | 429 (113) / 64 (25) | 0.854 / 0.799 / 0.891 | +0.038 [-0.006, +0.081] | -0.055 [-0.159, +0.046] | 146 (40) | 0.062 / 0.263 | 0.043 / 0.020 | 0.117 / 0.146 |

Time-to-event strata compare the stratum's progressor samples with all non-progressor samples (so the non-progressor call-change columns repeat). Strata with few progressor patients have wide intervals; no stratum contrast is tested.

### L3. Change over time within a patient

Patients with ≥ 2 pre-event endoscopies: 65 (22 progressor, 43 non-progressor), 278 endoscopies. Endoscopy score = mean over repeats of the maximum logit outer prediction. Time = years before the event (progressors) or before the last sequenced endoscopy (non-progressors); a **negative** slope against time to event means the score **rises** towards the event.

| Modality | Mean slope / year: progressors (median) | non-progressors (median) | Δ mean slope P − NP [CI] | Mixed model time × class [95% CI], p | Time (NP) | Class | Last − first: progressors [CI] (share up) | non-progressors [CI] (share up) |
|---|---|---|---|---|---|---|---|---|
| L-IMG | -0.807 (-0.214) | -0.018 (-0.000) | -0.790 [-1.868, -0.113] | -0.234 [-0.410, -0.058], p = 0.009 | +0.010 [-0.080, +0.100] | +4.387 [+3.292, +5.482] | +1.702 [+0.809, +2.667] (0.77) | +0.012 [-0.684, +0.680] (0.56) |
| L-CNV | -0.646 (-0.007) | -0.109 (-0.050) | -0.537 [-1.453, +0.082] | -0.161 [-0.303, -0.019], p = 0.027 | -0.079 [-0.151, -0.007] | +3.336 [+2.290, +4.382] | +1.294 [-0.096, +2.981] (0.46) | +0.625 [+0.160, +1.085] (0.60) |

- L-IMG mixed model: random-intercept variance 1.403, residual variance 3.781, converged yes, 278 endoscopies / 65 patients.
- L-CNV mixed model: random-intercept variance 2.156, residual variance 2.314, converged yes, 278 endoscopies / 65 patients.

Time-dependent AUROC (stored, fold-stratified IPCW, `results/paper_final/horizon_foldstrat`; re-tabulated, not recomputed):

| Horizon | Cases / controls (samples) | L-CNV [CI] | L-IMG [CI] | L-LATE [CI] |
|---|---|---|---|---|
| 1 year | 29 / 449 | 0.811 [0.656, 0.923] | 0.771 [0.631, 0.846] | 0.854 [0.747, 0.907] |
| 3 years | 99 / 277 | 0.767 [0.655, 0.841] | 0.788 [0.659, 0.866] | 0.831 [0.705, 0.898] |
| 5 years | 126 / 168 | 0.779 [0.669, 0.841] | 0.760 [0.661, 0.819] | 0.821 [0.716, 0.873] |

### L4. Disagreement within an endoscopy as a signal

| Unit | Modality | AUROC max [CI] | AUROC SD [CI] | AUROC max + SD [CI] | Δ (max + SD) − max [CI] |
|---|---|---|---|---|---|
| endoscopy (n = 146, 40 progressor) | L-IMG | 0.882 [0.813, 0.938] | 0.575 [0.482, 0.669] | 0.757 [0.676, 0.829] | -0.125 [-0.171, -0.084] |
| endoscopy (n = 146, 40 progressor) | L-CNV | 0.846 [0.752, 0.927] | 0.635 [0.526, 0.734] | 0.764 [0.671, 0.843] | -0.082 [-0.146, -0.021] |
| patient (n = 73, 30 progressor) | L-IMG | 0.841 [0.735, 0.928] | 0.558 [0.432, 0.685] | 0.733 [0.612, 0.847] | -0.107 [-0.164, -0.055] |
| patient (n = 73, 30 progressor) | L-CNV | 0.827 [0.722, 0.917] | 0.668 [0.537, 0.794] | 0.767 [0.640, 0.877] | -0.060 [-0.137, +0.014] |

Endoscopy level: endoscopies with ≥ 2 pre-event samples; patient level: SD over all of a patient's pre-event samples (patients with ≥ 2).

### L5. Who each modality misses

P1 (H&E only) and P2 (copy number only) set to the same non-progressor ever-flagged count per repeat: target 35.5 of 43 (mean over repeats; the mean of the two policies' 90% cells). Mean grid position (0 = 80%, 1 = 90%, 2 = 95%): H&E 0.99, copy number 1.14; repeats clamped to a grid end: H&E 0, copy number 0. Progressor patients caught: H&E 31.0, copy number 31.1 of 32.

| Progressor patients (mean over repeats) | Copy number caught | Copy number missed |
|---|---|---|
| H&E caught | 30.2 (both) | <5 (H&E only) |
| H&E missed | <5 (copy number only) | <5 (neither) |

Non-progressor patients at the same operating point: both 30.1, H&E only 5.4, copy number only 5.4, neither <5.

Progressor patients by modal category (highest mean probability over repeats) and the patients discordant in at least one repeat, described in aggregate:

| Group | Patients | Highest pre-event grade | Pre-event endoscopies, median [IQR] | Years first sample → event, median [IQR] | Tissue tertile 1 / 2 / 3 | Batch type | Scanner |
|---|---|---|---|---|---|---|---|
| both | 31 | LGD 14, NDBE 14, ID <5 | 3.0 [1.0, 4.0] | 4.9 [2.9, 7.3] | 9 / 12 / 10 | all samples in mixed batches 16, any sample in a single-class batch 15 | C13239-01 22, both scanners 8, C13210 <5 |
| H&E only | 0 |  | | | | | |
| copy number only | <5 | fewer than 5 patients: not described | | | | | |
| neither | 0 |  | | | | | |
| discordant in at least one repeat (H&E only or copy number only) | 6 | NDBE 5, LGD <5 | 1.5 [1.0, 2.8] | 5.5 [2.8, 8.8] | <5 / <5 / <5 | any sample in a single-class batch <5, all samples in mixed batches <5 | C13239-01 5, both scanners <5 |

Discordant-in-≥ 1-repeat group: mean per repeat 0.78 caught by H&E only and 0.90 by copy number only; modal category 'both' for 5 of them.

### Figures (local, not committed)

`paper/figures_r8/`: `r8_a_caught_vs_np_flagged.png` (plot a; marker size = samples sequenced per patient), `r8_b_caught_vs_flags_per_py.png` (plot b), `r8_c_cost_vs_caught.png` (plot c, cost / caught frontier joined), `r8_l2_forest.png` (Δ by stratum), `r8_l3_trajectory.png` (mean endoscopy logit by years to reference, both modalities), `r8_l4_auroc.png`, `r8_l5_2x2.png`. Frontier points are numbered in plots a–c with a key beside each plot.

### Implementation notes

- Units and population: pre-event samples of the analysed cohort (571 samples, 288 endoscopies, 75 patients); endoscopy = (patient, endoscopy number) as rounds 6–7d, so the checks against R49, B\*-endo and Table 1 (D) use the same units. A patient is in one outer fold per repeat, so every threshold applied to a patient's history comes from that fold.
- Thresholds (all policies): per (repeat, fold), on the fold's training patients' pre-event endoscopies scored by inner out-of-fold predictions, the largest threshold flagging ≥ the target share of training progressor endoscopies (`thr_sens`; endoscopy level). No policy uses a patient-level threshold: P7–P9 apply endoscopy-level thresholds along each patient's history. P5 and P6 use the stored sample-level triage cut-offs (`tb_common.triage`) at the 9 cells (t_low 90/95/98% sample sensitivity × t_high 85/90/95% specificity), as round 7b/7c.
- Endoscopy scores: P1 max L-IMG; P2 max L-CNV; P3 max L-LATE; P4 L-LATE of one random sample (R41 seeds 0–99; the same pick for an endoscopy whether it is in training or evaluation; one threshold per seed; outcomes averaged over seeds). Top-H&E sample = the sample with the highest L-IMG (inner in training, outer in evaluation).
- P7: the first pre-event endoscopy (earliest exact date) is sequenced (k = 1 top-H&E, 1 random, 2 top-H&E, all) and flagged if the max L-LATE over the sequenced samples ≥ t_b; 'always flag' is read as: a patient flagged there becomes high risk and **every later endoscopy is flagged** without further sequencing. Otherwise later endoscopies are flagged if max L-IMG ≥ t_s (the P1 threshold). t_b is set on all training endoscopies with the same k-sample score (for k = all it equals P3's threshold).
- P8: as P7 with k = 1 top-H&E; t_b keeps P7's grid (80/90/95%), so 3 × 2 cells; for a patient not high risk, a later endoscopy with max L-IMG ≥ t_mid (the P1 threshold at 80/90%) has its top-H&E sample sequenced and is flagged if that L-LATE ≥ t_c (the top-H&E L-LATE threshold at 90% training endoscopy sensitivity, unconditional on t_mid). Endoscopies below t_mid are not flagged.
- P9: the top-H&E sample is sequenced at the first endoscopy and at any endoscopy ≥ N years (exact dates, 365.25-day years) after the last sequenced one, flagged if its L-LATE ≥ t (90%); other endoscopies flagged if max L-IMG ≥ t_s (90%). A positive sequencing result does not change later rules.
- P10: grade ID/LGD at any sample of the endoscopy; grade ID/LGD or p53 aberrant on the samples with a p53 result (endoscopies and patients formed from those samples only), so its counts have their own denominators.
- Outcomes: patient caught / ever flagged = flagged at ≥ 1 pre-event endoscopy; time first flag → event = from the earliest flagged endoscopy's exact date to the event, median over caught progressors per repeat, then averaged; last-2 window = each patient's two latest pre-event endoscopies by exact date (for non-progressors the last sequenced endoscopy is the reference of the time axis); sequencing counts samples; cost = £85 × samples sequenced + £535 × flagged endoscopies (£471 + £44 + £20, round 7d), divided by all 75 patients.
- Dates: exact sample dates from `pre_event_cohort.Date` (CNV folder name), never the year-only slide-table date. Event = earliest exact date among the samples of the sheet event endoscopy (largest months before final among HGD/IMC samples, hz_prep.py); if none of its samples has an exact date, the date implied by the patient's analysed samples (exact date + (months before final − event months) × 30.44 days, midrange). Last sequenced endoscopy (non-progressors) = latest exact date over the patient's sequenced samples on the sheet. The endoscopy unit's date is its earliest sample date. Pre-event status keeps the study's months-before-final definition.
- Frontier: computed on observed single-model means (no intervals); dominance requires ≥ on all three criteria and > on one. P1 cells sequence nothing, so they are on the three-way frontier by construction whenever no other zero-sequencing point dominates them.
- L2: strata at the sample level for AUROC (H&E quintile edges from the repeat-mean L-IMG of all pre-event samples; tissue tertiles of tissue tiles; time to event from exact dates; position = the patient's first pre-event endoscopy). Folds lacking one class within a stratum are skipped (fsa). Call-change strata at the endoscopy level (quintile of the endoscopy's max repeat-mean L-IMG, highest grade, tissue tertile of the top-H&E sample, progressor endoscopy time to event with all non-progressor endoscopies).
- L3: endoscopy score = mean over the 10 repeats of the endoscopy's maximum logit (outer prediction, clipped at 1e-6); slopes by least squares per patient; Δ mean slope with a patient bootstrap of the 65 patients; mixed model `score ~ time × class + (1 | patient)` (statsmodels MixedLM, REML) on the same endoscopies; last − first by exact date. The trajectory plot bins endoscopies by years to the reference date; bins with < 5 patients are not plotted.
- L4: within-unit SD (ddof 1) of logit predictions per repeat; max + SD = sum of the two ranks among the units in that repeat (fixed equal weights), ranks held fixed in the bootstrap; fold-stratified AUROC with the unit's patient fold.
- L5: the common non-progressor ever-flagged target per repeat is the mean of P1's and P2's counts at their 90% cells; each policy is interpolated linearly in that count between adjacent grid cells, a patient's catch probability being the same mix of its two cells' calls; cross-tab cells are expected counts with the two mixes independent. Groups of fewer than 5 patients are not described.
- Privacy: only aggregates are committed; counts of 1–4 patients in patient cells are shown as '<5'; the row-level endoscopy date table stays on the cluster (killcoyne_mm/review_round8/).

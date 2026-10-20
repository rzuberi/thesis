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

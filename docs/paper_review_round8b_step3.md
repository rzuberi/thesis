# Round 8b: step 3: fixing the main rule and the checks the panel asked for

Status: PRE-SPECIFICATION (written 2026-10-20). Nothing below has been run. Results are appended under the line at the end in a later commit; this section is not edited afterwards.

## The decision fixed now

A five-member panel read the round-8 strategy map (`docs/paper_review_round8_landscape.md`, results 1a77818). The panel was a gastroenterologist, a health economist, a biostatistician, a Nature Medicine editor and a sceptic; their reviews are outside the repository.

**Main rule.** The main rule of the manuscript and of the ACE-B registration is the **R49 per-endoscopy gate exactly as pre-specified in round 7** (P6, t_low 95% / t_high 90%). The comparator is **H&E alone (P1)**.

**Selection rule written now.** R49 is the only rule that meets all three conditions:
1. it was fixed before the strategy map was seen;
2. it stays within −0.05 of sequencing every sample per endoscopy (round 7c);
3. it can be applied in ACE-B's design (about 2 samples, mostly one endoscopy per patient).

Four of the five panellists chose it. The health economist preferred H&E alone, and that view is reported.

**Not promoted.** Strategies that appeared on the map's frontier (P8, P9, P6 at other cells) are not promoted. The panel judged their ranking to be within noise.

**Exploration ends here.** This round's analyses only quantify uncertainty and transportability. They cannot change the main rule. Whatever they show is reported, and the manuscript states the claims accordingly.

No model is refitted; stored predictions and calls are re-scored. No ACE-B file is read. Conventions: patient bootstrap, 2,000 draws, `RandomState(0)`; single model averaged over 10 repeats; thresholds fixed as in each policy's round-8 definition.

## S1. Does sequencing reduce false flags compared with H&E alone? (paired)

Contrasts:
- (a) R49 against P1;
- (b) P3 (sequence everything, H&E + copy number) against P1.

Each contrast is computed at two operating points:
- (i) P1's threshold set so that its endoscopy sensitivity equals the other rule's realised endoscopy sensitivity (evaluation-matched, re-matched per draw);
- (ii) P1 at its 90% training cell, with no matching.

Reported for each, with paired patient-bootstrap two-sided 95% CIs:
- Δ endoscopy specificity;
- Δ non-progressor patients ever flagged (of 43);
- Δ flagged non-progressor endoscopies per patient-year;
- Δ progressor patients caught (of 32);
- Δ samples sequenced per patient.

The manuscript states "sequencing reduces false flags compared with the slide alone" only if Δ non-progressor patients flagged in (a)(i) has an upper 95% limit below 0. Otherwise it states that the reduction was not demonstrated.

## S2. How stable is the frontier?

In each bootstrap draw:
1. recompute every round-8 policy cell's outcomes, using progressor patients caught, non-progressor patients ever flagged and samples sequenced per patient;
2. find the Pareto set;
3. find the cost frontier at the round-8 unit costs.

Report, for each policy cell, the share of draws in which it is on each frontier. Also report the share of draws in which R49 (P6 95/90) and P1 at 90% are each dominated.

## S3. Cost sensitivity (descriptive)

For P1 (80/90/95%), R49, P3 at 90%, P8 at 90/80 and grade, recompute cost per patient and the cost frontier over this grid:

| Parameter | Values |
|---|---|
| Sequencing price | £85, £150, £250, £400 |
| Cost per flagged endoscopy | £535; also £1,605 (a high-risk pathway costing about three endoscopy-equivalents) |
| Unit | per patient; per non-progressor patient-year |
| Progressor weight | as in the cohort; reweighted to 10% progressor patients |

Report, at each grid point, which rules are on the cost frontier and the paired Δ cost (R49 − P1 at 90%) with its CI.

## S4. ACE-B-shaped precision (no ACE-B data)

Draw 10,000 discovery subsamples shaped like ACE-B:
- 15 progressor and 67 non-progressor patients, sampled without replacement;
- one pre-event endoscopy per patient, chosen at random;
- at most 2 of its samples, chosen at random.

Report the 2.5–97.5% range and the median of:
- H&E model patient-level AUROC (score = max L-IMG);
- R49 endoscopy sensitivity and specificity;
- Δ specificity, R49 − P1 at matched sensitivity;
- the share of draws in which "≥ 12 of 15 progressor patients detected by R49" passes.

From these, propose pass bounds for the ACE-B registration. The primary endpoint is H&E model transfer: patient-level AUROC with a lower 95% bound above 0.70. The secondary endpoint is the R49 gate, with endoscopy sensitivity and the share sequenced. The bounds go in the registration draft, not in the manuscript's results.

## Scripts and running

- **Script:** `scripts/paper_plan/rv8b_step3.py`, reusing `rv8_landscape.py`.
- **Execution:** cluster jobs via `campaign.sh`, prefix `rv8b`.
- **Outputs:** aggregates to `results/paper_final/review_round8b/`; results appended below by `rv8b_render.py`.

---

## Results

Rendered by `scripts/paper_plan/rv8b_render.py` from `results/paper_final/review_round8b/` (aggregate results 402e00f); script `scripts/paper_plan/rv8b_step3.py` (policy definitions, thresholds and outcomes executed unchanged from `rv8_landscape.py`); figures by `scripts/paper_plan/rv8b_figs.py` (local, not committed). No model was refitted and no ACE-B file was read. Single model = per-repeat values averaged over the 10 repeats. Intervals: paired patient bootstrap, 2,000 draws (`RandomState(0)`), thresholds and calls fixed unless stated. These analyses do not change the main rule (R49).

### S1. Does sequencing reduce false flags compared with H&E alone? (paired)

Δ = rule − P1 (H&E alone). (i) P1's threshold set per repeat so that its endoscopy sensitivity equals the rule's realised endoscopy sensitivity (re-matched in every draw); (ii) P1 at its 90% training cell. Values: rule / P1, then Δ [95% CI].

| Contrast | Operating point | Δ NP patients flagged (of 43) | Δ endoscopy specificity | Δ flagged NP endoscopies / NP patient-year | Δ progressor patients caught (of 32) | Δ samples sequenced / patient |
|---|---|---|---|---|---|---|
| (a) R49 − P1 | (i) evaluation-matched | 31.8 / 36.8; **-5.0** [-8.7, -1.1] | 0.560 / 0.493; **+0.068** [-0.038, +0.165] | 0.311 / 0.359; **-0.048** [-0.118, +0.027] | 31.1 / 31.2; **-0.1** [-1.3, +0.8] | 1.94 / 0.00; **+1.94** [+1.61, +2.27] |
| (a) R49 − P1 | (ii) P1 at 90% | 31.8 / 36.0; **-4.2** [-7.4, -1.2] | 0.560 / 0.524; **+0.036** [-0.018, +0.085] | 0.311 / 0.337; **-0.025** [-0.060, +0.013] | 31.1 / 31.1; **+0.0** [-1.5, +1.9] | 1.94 / 0.00; **+1.94** [+1.61, +2.27] |
| (b) P3 90% − P1 | (i) evaluation-matched | 31.8 / 37.4; **-5.6** [-10.3, -0.6] | 0.551 / 0.466; **+0.085** [-0.067, +0.263] | 0.317 / 0.378; **-0.061** [-0.185, +0.046] | 31.2 / 31.2; **+0.0** [-1.2, +0.9] | 7.61 / 0.00; **+7.61** [+6.59, +8.71] |
| (b) P3 90% − P1 | (ii) P1 at 90% | 31.8 / 36.0; **-4.2** [-8.1, -0.1] | 0.551 / 0.524; **+0.027** [-0.052, +0.097] | 0.317 / 0.337; **-0.019** [-0.069, +0.037] | 31.2 / 31.1; **+0.1** [-1.4, +2.0] | 7.61 / 0.00; **+7.61** [+6.59, +8.71] |

- (a)(i) matching: endoscopy sensitivity rule 0.907, P1 0.907 (P1 − rule observed +0.000; over draws median +0.005, max +0.026).
- (b)(i) matching: endoscopy sensitivity rule 0.912, P1 0.912 (P1 − rule observed +0.000; over draws median +0.005, max +0.038).

**Binding manuscript statement (pre-specified rule):** Δ non-progressor patients flagged in (a)(i) = -5.0 [-8.7, -1.1]; upper 95% limit -1.097 < 0. The manuscript states: **"Sequencing reduces false flags compared with the slide alone."**

Check (round-8 settings, observed): R49 31.1 caught / 31.8 NP flagged; P1 90% 31.1 / 36.0; P3 90% 31.2 / 31.8 (round 8: 31.1 / 31.8, 31.1 / 36.0, 31.2 / 31.8); reproduced: yes.

### S2. How stable is the frontier?

76 round-8 policy cells (the p53-subset current-care cell excluded, as in round 8), 2,000 draws. Pareto = not dominated on progressor patients caught, non-progressor patients ever flagged and samples sequenced per patient; cost = not dominated on caught and cost per patient (£85 per sample, £535 per flagged endoscopy). Observed = round-8 single-model frontier membership.

Points on the frontier per draw, median [IQR]: Pareto 15 [13, 17], cost 5 [4, 7].

- **R49 (P6 t_low 95% / t_high 90%)**: dominated in 99.8% of draws on the Pareto criteria (most often by P8 t_b 90%, t_mid 90%, t_c 90% (97.9%); P8 t_b 95%, t_mid 80%, t_c 90% (78.2%); P8 t_b 95%, t_mid 90%, t_c 90% (70.1%)) and in 100.0% on cost (most often by P6 t_low 95% / t_high 95% (100.0%); P9 N = 5 years; t, t_s 90% (69.7%); P1 90% (56.6%)).
- **P1 at 90%**: dominated in 0.2% of draws on the Pareto criteria (most often by P1 80% (0.3%)) and in 33.2% on cost (most often by P6 t_low 90% / t_high 95% (30.9%); P6 t_low 90% / t_high 90% (15.0%); P7 k = 1 top-H&E; t_b 80%, t_s 80% (6.4%)).

Cells on either frontier in ≥ 5% of draws or in the observed data, plus R49:

| Policy | Cell | Caught | NP flagged | Sequenced / patient | Cost / patient | Observed: Pareto / cost | Share of draws on Pareto | on cost frontier |
|---|---|---|---|---|---|---|---|---|
| P1 | 80% | 30.1 | 31.6 | 0.00 | £1,002 | yes / yes | 100.0% | 100.0% |
| P1 | 90% | 31.1 | 36.0 | 0.00 | £1,242 | yes / yes | 99.8% | 66.8% |
| P1 | 95% | 31.9 | 39.3 | 0.00 | £1,489 | yes / yes | 86.7% | 67.9% |
| P2 | 80% | 28.8 | 28.0 | 7.61 | £1,796 | no / no | 14.7% | 0.0% |
| P2 | 90% | 31.0 | 35.0 | 7.61 | £2,082 | no / no | 9.2% | 0.0% |
| P2 | 95% | 31.7 | 39.6 | 7.61 | £2,306 | no / no | 16.1% | 1.2% |
| P3 | 80% | 30.5 | 26.4 | 7.61 | £1,579 | yes / no | 86.0% | 0.0% |
| P3 | 90% | 31.2 | 31.8 | 7.61 | £1,860 | no / no | 12.9% | 0.0% |
| P4 | 80% | 29.8 | 25.5 | 3.84 | £1,225 | yes / no | 99.9% | 10.6% |
| P4 | 90% | 30.7 | 30.8 | 3.84 | £1,478 | no / no | 10.4% | 1.1% |
| P6 | t_low 90% / t_high 85% | 31.0 | 32.1 | 1.33 | £1,274 | yes / no | 28.8% | 0.0% |
| P6 | t_low 90% / t_high 90% | 31.0 | 31.0 | 1.59 | £1,247 | no / no | 21.2% | 28.8% |
| P6 | t_low 90% / t_high 95% | 30.9 | 29.8 | 1.90 | £1,210 | no / yes | 25.3% | 68.7% |
| P6 | t_low 95% / t_high 90% | 31.1 | 31.8 | 1.94 | £1,362 | no / no | 0.2% | 0.0% |
| P6 | t_low 95% / t_high 95% | 31.1 | 30.6 | 2.25 | £1,320 | no / no | 9.6% | 28.8% |
| P6 | t_low 98% / t_high 85% | 31.2 | 34.9 | 2.02 | £1,499 | no / no | 0.0% | 5.1% |
| P7 | k = 1 top-H&E; t_b 80%, t_s 80% | 30.9 | 31.2 | 1.00 | £1,276 | yes / no | 94.4% | 17.5% |
| P7 | k = 1 top-H&E; t_b 80%, t_s 90% | 31.2 | 35.4 | 1.00 | £1,398 | no / no | 28.3% | 1.1% |
| P7 | k = 1 top-H&E; t_b 90%, t_s 80% | 31.0 | 32.5 | 1.00 | £1,457 | yes / no | 44.6% | 0.0% |
| P7 | k = 1 top-H&E; t_b 90%, t_s 90% | 31.3 | 36.1 | 1.00 | £1,549 | no / no | 5.8% | 0.0% |
| P7 | k = 1 top-H&E; t_b 95%, t_s 80% | 31.4 | 33.5 | 1.00 | £1,578 | yes / no | 91.2% | 1.3% |
| P7 | k = 1 top-H&E; t_b 95%, t_s 90% | 31.6 | 36.9 | 1.00 | £1,649 | yes / no | 34.1% | 9.1% |
| P7 | k = 1 random; t_b 80%, t_s 80% | 30.5 | 31.4 | 1.00 | £1,311 | no / no | 8.5% | 0.1% |
| P7 | k = 1 random; t_b 90%, t_s 80% | 30.9 | 32.6 | 1.00 | £1,468 | no / no | 24.7% | 0.0% |
| P7 | k = 1 random; t_b 95%, t_s 80% | 31.2 | 33.9 | 1.00 | £1,590 | no / no | 20.4% | 1.0% |
| P7 | k = 1 random; t_b 95%, t_s 90% | 31.4 | 36.9 | 1.00 | £1,657 | no / no | 8.6% | 1.4% |
| P8 | t_b 80%, t_mid 80%, t_c 90% | 30.9 | 28.7 | 1.70 | £1,289 | yes / no | 100.0% | 1.7% |
| P8 | t_b 80%, t_mid 90%, t_c 90% | 31.0 | 29.3 | 1.93 | £1,343 | yes / no | 61.5% | 5.0% |
| P8 | t_b 90%, t_mid 80%, t_c 90% | 31.0 | 30.2 | 1.47 | £1,459 | yes / no | 93.3% | 0.0% |
| P8 | t_b 90%, t_mid 90%, t_c 90% | 31.1 | 30.4 | 1.64 | £1,493 | yes / no | 61.3% | 0.0% |
| P8 | t_b 95%, t_mid 80%, t_c 90% | 31.4 | 31.4 | 1.33 | £1,572 | yes / no | 96.4% | 5.6% |
| P9 | N = 3 years; t, t_s 90% | 31.3 | 34.2 | 2.07 | £1,395 | no / no | 27.7% | 0.4% |
| P9 | N = 5 years; t, t_s 90% | 31.3 | 35.4 | 1.60 | £1,348 | no / yes | 15.8% | 33.2% |
| P10 | grade ID/LGD (all pre-event endoscopies) | 17.0 | 25.0 | 0.00 | £571 | yes / yes | 97.2% | 100.0% |

The other 42 cells were on neither frontier in the observed data and on each in < 5% of draws (all shares in `s2.json`). Check: observed frontier membership equals round 8 for 76 of 76 cells; reproduced: yes.

### S3. Cost sensitivity (descriptive)

Progressor patients caught (of 32, fixed across the grid): P1 80 30.1; P1 90 31.1; P1 95 31.9; R49 31.1; P3 90 31.2; P8 90/80 31.0; grade 17.0. Cost per patient or per non-progressor patient-year (NP py); '10%' = progressor and non-progressor patient means mixed 10% / 90% (applies to the per-patient unit only). Frontier = rules not dominated on caught and cost.

| Sequencing £ | Flag £ | Unit | Weight | P1 80 | P1 90 | P1 95 | R49 | P3 90 | P8 90/80 | grade | Cost frontier | Δ R49 − P1 90 [CI] |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| £85 | £535 | patient | cohort | £1,002 | £1,242 | £1,489 | £1,362 | £1,860 | £1,459 | £571 | P1 80, P1 90, P1 95, grade | +£120 [£41, £206] |
| £85 | £535 | patient | 10% progressors | £884 | £1,197 | £1,548 | £1,333 | £1,911 | £1,444 | £591 | P1 80, P1 90, P1 95, grade | +£136 [£28, £261] |
| £85 | £535 | NP py | – | £129 | £180 | £238 | £201 | £293 | £219 | £91 | P1 80, P1 90, P1 95, grade | +£21 [£4, £42] |
| £85 | £1,605 | patient | cohort | £3,005 | £3,726 | £4,468 | £3,756 | £4,285 | £4,127 | £1,712 | P1 80, P1 90, P1 95, P3 90, grade | +£30 [−£200, £274] |
| £85 | £1,605 | patient | 10% progressors | £2,653 | £3,591 | £4,645 | £3,570 | £4,188 | £4,056 | £1,773 | P1 80, P1 95, R49, P3 90, grade | −£20 [−£347, £342] |
| £85 | £1,605 | NP py | – | £387 | £540 | £715 | £535 | £633 | £614 | £273 | P1 80, P1 95, R49, P3 90, grade | −£5 [−£60, £55] |
| £150 | £535 | patient | cohort | £1,002 | £1,242 | £1,489 | £1,488 | £2,355 | £1,554 | £571 | P1 80, P1 90, P1 95, grade | +£246 [£161, £339] |
| £150 | £535 | patient | 10% progressors | £884 | £1,197 | £1,548 | £1,497 | £2,501 | £1,549 | £591 | P1 80, P1 90, P1 95, grade | +£300 [£186, £434] |
| £150 | £535 | NP py | – | £129 | £180 | £238 | £228 | £387 | £236 | £91 | P1 80, P1 90, P1 95, grade | +£48 [£29, £69] |
| £150 | £1,605 | patient | cohort | £3,005 | £3,726 | £4,468 | £3,882 | £4,780 | £4,222 | £1,712 | P1 80, P1 90, P1 95, grade | +£156 [−£78, £405] |
| £150 | £1,605 | patient | 10% progressors | £2,653 | £3,591 | £4,645 | £3,734 | £4,779 | £4,162 | £1,773 | P1 80, P1 90, P1 95, grade | +£143 [−£180, £503] |
| £150 | £1,605 | NP py | – | £387 | £540 | £715 | £561 | £727 | £630 | £273 | P1 80, P1 90, P1 95, grade | +£21 [−£33, £82] |
| £250 | £535 | patient | cohort | £1,002 | £1,242 | £1,489 | £1,682 | £3,116 | £1,701 | £571 | P1 80, P1 90, P1 95, grade | +£440 [£337, £551] |
| £250 | £535 | patient | 10% progressors | £884 | £1,197 | £1,548 | £1,748 | £3,410 | £1,711 | £591 | P1 80, P1 90, P1 95, grade | +£551 [£422, £697] |
| £250 | £535 | NP py | – | £129 | £180 | £238 | £269 | £533 | £261 | £91 | P1 80, P1 90, P1 95, grade | +£89 [£68, £113] |
| £250 | £1,605 | patient | cohort | £3,005 | £3,726 | £4,468 | £4,076 | £5,541 | £4,369 | £1,712 | P1 80, P1 90, P1 95, grade | +£350 [£111, £609] |
| £250 | £1,605 | patient | 10% progressors | £2,653 | £3,591 | £4,645 | £3,986 | £5,687 | £4,324 | £1,773 | P1 80, P1 90, P1 95, grade | +£395 [£71, £769] |
| £250 | £1,605 | NP py | – | £387 | £540 | £715 | £602 | £872 | £656 | £273 | P1 80, P1 90, P1 95, grade | +£62 [£8, £125] |
| £400 | £535 | patient | cohort | £1,002 | £1,242 | £1,489 | £1,973 | £4,258 | £1,922 | £571 | P1 80, P1 90, P1 95, grade | +£731 [£589, £879] |
| £400 | £535 | patient | 10% progressors | £884 | £1,197 | £1,548 | £2,126 | £4,772 | £1,955 | £591 | P1 80, P1 90, P1 95, grade | +£929 [£765, £1,107] |
| £400 | £535 | NP py | – | £129 | £180 | £238 | £331 | £750 | £299 | £91 | P1 80, P1 90, P1 95, grade | +£151 [£125, £180] |
| £400 | £1,605 | patient | cohort | £3,005 | £3,726 | £4,468 | £4,367 | £6,683 | £4,590 | £1,712 | P1 80, P1 90, P1 95, grade | +£641 [£392, £911] |
| £400 | £1,605 | patient | 10% progressors | £2,653 | £3,591 | £4,645 | £4,364 | £7,050 | £4,567 | £1,773 | P1 80, P1 90, P1 95, grade | +£773 [£441, £1,164] |
| £400 | £1,605 | NP py | – | £387 | £540 | £715 | £664 | £1,090 | £694 | £273 | P1 80, P1 90, P1 95, grade | +£124 [£69, £187] |

Per-NP-patient-year rows do not depend on the progressor weighting (their duplicates are omitted; all 32 grid points are in `s3.json`). Times on the cost frontier over the 32 grid points: P1 80 32; P1 90 29; P1 95 32; R49 3; P3 90 4; P8 90/80 0; grade 32.
Δ cost R49 − P1 90%: interval entirely below 0 at 0 and entirely above 0 at 24 of 32 grid points.

Check (£85 / £535, per patient, cohort weights): caught and cost equal the round-8 cells: yes (R49 £1,361.87 vs £1,361.87; P1 90% £1,241.91 vs £1,241.91).

### S4. ACE-B-shaped precision (no ACE-B data)

10,000 discovery subsamples: 15 progressor patients (without replacement, of 32) and 67 non-progressor patients (**with replacement**: only 43 exist); one random pre-event endoscopy per drawn patient, at most 2 of its samples at random. Stored outer predictions and R49's round-7 fold cut-offs fixed.

| Quantity | Median | 2.5–97.5% range |
|---|---|---|
| H&E model patient-level AUROC (max L-IMG) | 0.855 | 0.756 – 0.930 |
| R49 endoscopy sensitivity | 0.913 | 0.813 – 0.987 |
| R49 endoscopy specificity | 0.615 | 0.519 – 0.707 |
| P1 specificity at R49's sensitivity | 0.587 | 0.422 – 0.770 |
| Δ specificity, R49 − P1 at matched sensitivity | 0.027 | -0.140 – 0.178 |
| R49 share of samples sequenced | 0.334 | 0.284 – 0.384 |
| R49 progressor patients detected (of 15) | 13.7 | 12.2 – 14.8 |
| AUROC lower 95% bound (Hanley–McNeil) | 0.730 | 0.606 – 0.838 |

Share of draws in which "≥ 12 of 15 progressor patients detected by R49" passes: 98.9% (detected count averaged over the 10 repeats); 96.6% averaged per repeat.

**Proposed pass bounds for the ACE-B registration draft** (not manuscript results):

- Primary (H&E model transfer): patient-level AUROC with a lower 95% bound above 0.70, as pre-specified. Expected AUROC in an ACE-B-shaped sample: median 0.855; the lower bound exceeded 0.70 in 69.0% of draws (Hanley–McNeil), the point estimate in 99.9%.
- Secondary (R49 gate), sensitivity: ≥ 12 of 15 progressor patients detected (floor(15 x 2.5th percentile of the ACE-B-shaped sensitivity); passed in 98.9% of draws). The pre-specified check '≥ 12 of 15' passed in 98.9%.
- Secondary (R49 gate), share of samples sequenced: ≤ 0.39 (97.5th percentile of the ACE-B-shaped share, rounded up to 0.01; passed in 98.7% of draws).

### Figures (local, not committed)

`paper/figures_r8/`: `r8b_s1_forest.png` (S1 paired differences), `r8b_s2_frontier_share.png` (S2 frontier membership), `r8b_s3_cost_grid.png` (S3 cost-frontier membership across the grid), `r8b_s4_distributions.png` (S4 distributions with the proposed bounds).

### Implementation notes

- Reuse: `rv8b_step3.py` executes `rv8_landscape.py` unchanged up to its task dispatch, so setup, endoscopy units, thresholds (`thr_arr`), policies (`family`, `r49_calls`, `p8_calls`), outcomes (`patient_arrays`) and bootstrap draws (`pdraws`, `RandomState(0)`, one-class draws rejected) are round 8's. Outcomes are recomputed from the same weighted sums as round 8's `lstats`.
- S1 contrast (b) uses P3 at its 90% cell (the round-8 check cell). Counts are shares × 32 or × 43 in every draw, as round 8. Δ samples sequenced equals the rule's own value because P1 sequences nothing.
- S1 (i) matching: per repeat, P1's threshold is the largest value of max L-IMG reaching at least the rule's realised endoscopy sensitivity over the evaluated endoscopies (bootstrap multiplicities as integer weights; round 7d's binary-call matching); with continuous scores the realised P1 sensitivity can exceed the rule's slightly (gap reported).
- S1 statement: the binding rule is applied to the 95% percentile interval of Δ non-progressor patients flagged (count of 43) in (a)(i).
- S2: every round-8 cell's outcomes are recomputed per draw with thresholds and calls fixed and rounded as round 8 (counts 2 dp, samples sequenced 3 dp, cost 2 dp) before the dominance test; ties are not dominance. 'Dominated' = not on that frontier in the draw.
- S3: P8 at 90/80 = t_b 90%, t_mid 80% (t_c 90%); grade = P10 grade ID/LGD on all pre-event endoscopies. Cost per non-progressor patient-year = sequencing and flagged-endoscopy costs incurred in non-progressor patients divided by their patient-years (round 8's flags-per-NP-patient-year analogue), so progressor reweighting does not apply to it. Reweighting to 10% progressors mixes the progressor and non-progressor per-patient mean costs 10% / 90%. The cost frontier is observed (single-model means), among the seven rules only; Δ cost has a paired bootstrap interval.
- S4: the pre-specification asks for 67 non-progressor patients without replacement, but the cohort has 43; non-progressors are therefore drawn with replacement (each copy picks its own endoscopy and samples), progressors without replacement. One RandomState(0) stream for all 10,000 draws.
- S4: AUROC is pooled over folds within each repeat (an external test set is scored by one model; fold-stratified AUROC is unstable with 15 progressors) and averaged over repeats; R49 uses the stored round-7 cut-offs (t_low 95%, c* 90%, t_seq) of the drawn patient's outer fold, applied to the max L-IMG of the chosen ≤ 2 samples, the top one sequenced in the middle band. '≥ 12 of 15 detected' is judged on the repeat-mean count (also reported per repeat). The Hanley–McNeil lower bound and the proposal rules (2.5th percentile of sensitivity, floored to a count of 15; 97.5th percentile of the share sequenced, rounded up) were added to turn the distributions into bounds; they are proposals for the registration draft only.
- Checks were run first in a 20-draw smoke campaign (aggregates written aside, not committed) and repeated in the full run: S1 point estimates at round-8 settings, S2 observed frontier membership (76 of 76 cells) and S3 base costs all equal round 8.
- Privacy: only aggregates are committed; per-draw arrays stay on the cluster (killcoyne_mm/review_round8b/); no identifiers or dates.

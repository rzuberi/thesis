# Exploration E9: the clinical and economic picture

Status: exploratory, not confirmatory (rules: `paper/reviews_round7/decisions/EXPLORE_RULES.md`). Written 20 October 2026.

## Plan

**Question.** How do the rules look as full operating curves rather than single points? What do they mean in a real surveillance population? When do they save money?

Every threshold and hyper-parameter is chosen on training patients (inner out-of-fold predictions inside the stored 10 × 10 patient-grouped folds). Every number below is on held-out patients unless it is labelled optimistic.

**Code reuse.** No rule is re-implemented. `scripts/paper_plan/ex_e9_frontier.py` executes, unchanged:
- the module body of `rv9_falseflags.py`, which brings in `statics`, `memory`, `cert_flags`, `make_ctx`, `base`, `f_A12` and the nested engine's selection logic;
- the helper section of `ex_e3_score.py`, for the mean-logit endoscopy score (`variant("mlogit:stored")`, which E3 showed is identical to its `mlogit:base` refit);
- `ex_e2_veto.py` up to its dispatch, as `story_deck/cluster/story_aggs_v2.py` does, for the quiet-genome check (`vs_test`, `vs_train`, `veto_V` with the `cn90` bar on `ps_oac`, top-2 samples).

The only new piece is the sweep. For every outer fold, the round-9 operating rule ("highest threshold whose training progressor-patient detection is at least the target; among candidates, fewest training non-progressor patients flagged") runs at a series of targets instead of only R49's own training detection D. The targets are D itself and nTP − k for k = 0…24, where nTP is the fold's number of training progressor patients.

**Rules on the curves.**

| Curve | Score | Sequencing |
|---|---|---|
| H&E max (single endoscopy) | `A1:img:none` | 0 |
| H&E mean-logit (single endoscopy) | `A1:img:none` on mean logit | 0 |
| Today's gate | `A1:gate_al:none` (R49-aligned gate score) | gate band |
| Memory | `A1:gate_al:ew` | gate band |
| Memory + certificate | `A12` | gate band |
| Final rule | `A12` + quiet check (cn90, top-2) | + check |
| Mean-logit + memory | `A1:img:ew` on mean logit | 0 |
| Mean-logit full stack | `A12` on the mean-logit gate + check | gate band + check |
| Grade with memory | EW / running mean of endoscopy grade (0 NDBE, 1 IND, 2 LGD) | 0 |
| Grade + p53 with memory | as above, p53 aberrant counted as LGD | 0 |

Fixed points: pathologist grade (IND/LGD ever), LGD ever, p53 aberrant ever, grade + p53, R49 and P1 at 90%. "Running worst grade" is the same as "ever flagged" per patient, so the grade memory comparator is the averaged grade.

**Outputs.**
1. Trade-off figure (x = non-progressor patients ever flagged of 43, y = progressor patients caught of 32), with patient-bootstrap 95% bands (vertical averaging on a common x grid, 2,000 draws, `RandomState(0)`). Matched comparisons: non-progressors flagged at 31.1 / 30.5 caught, and caught at 17.2 / 23.6 / 31.8 non-progressors flagged, paired against today's gate.
2. Full stack on the mean-logit base, plus a tiered menu: no sequencing, about 1.4–1.9 samples per patient, about 3.8 samples per patient. For each tier: caught, non-progressors flagged, samples, cost, and extra cost per false flag avoided and per progressor lost.
3. Reweighting to 1.5%, 3%, 5% and 10% progressing, per 1,000 patients over the cohort's follow-up. For each rule: flags, extra endoscopies, samples sequenced, PPV, NPV, progressors missed, and non-progressors never flagged (de-escalation candidates).
4. Break-even analysis:
   - the sequencing price at which each rule stops saving, against today's gate and against standard care (grade + p53);
   - the flag-cost threshold;
   - the flag costed once per flagged patient or per flagged endoscopy;
   - a missed-progressor cost of £0, £20k or £40k.

Costs as round 8: £85 per sample sequenced, £535 per flagged endoscopy.

## Results

All numbers are on held-out patients. Every threshold, half-life, certificate setting and check bar was chosen on training patients. Counts are means over the 10 repeats; intervals are paired patient-bootstrap 95% CIs (2,000 draws, `RandomState(0)`). Aggregates: `results/paper_final/explore_E9/frontier.json`. Figures (local only): `paper/figures_explore_E9/fig_e9_tradeoff.png` and `fig_e9_prevalence.png`.

### 0. Reproduction

The sweep engine at target D reproduces every stored rule exactly:

| Rule | Caught | NP flagged | Samples/patient |
|---|---|---|---|
| R49 | 31.1 | 31.8 | 1.94 |
| P1 90% | 31.1 | 36.0 | 0 |
| Memory | 30.7 | 23.6 | 1.94 |
| Memory + certificate | 30.5 | 21.5 | 1.94 |
| Final rule | 30.5 | 17.2 | 3.82 |
| Mean-logit + memory | 31.0 | 26.6 | 0 |
| Mean-logit gate + memory | 30.5 | 22.6 | 1.43 |

The engine's gate bands also equal `r49_calls`.

### 1. Trade-off curves (the missing figure)

![trade-off](../paper/figures_explore_E9/fig_e9_tradeoff.png)

Each curve sweeps the round-9 operating rule over 32 training targets:
- R49's own training detection D;
- "catch all training progressors but k", for k = 0…24;
- "flag at least a share r of training non-progressors", for r = 0.5…1.0.

The large dot on each curve is the reported operating point (target D).

**Panels A and B (H&E rules).** Memory moves the curve up and to the left almost everywhere. The certificate and then the check move it further. Single-endoscopy H&E (max or mean-logit) is the worst curve. At the high-sensitivity end, the gap between rules is wider than at any single point:

| Rule | NP flagged at 30.5 caught | Δ vs gate curve | NP flagged at R49's own caught, minus R49 | Caught at 23.6 NP | Δ vs gate | Caught at 17.2 NP | Δ vs gate |
|---|---|---|---|---|---|---|---|
| Today's gate (swept) | 26.6 [13.9, 35.4] | 0 | −0.7 [−10.2, +8.7] | 29.9 | 0 | 28.5 | 0 |
| H&E max, single endoscopy | 33.8 | +7.3 [−1.3, +17.2] | +3.3 [−1.9, +10.1] | 27.3 | −2.6 [−5.6, +0.1] | 26.3 | −2.2 [−5.5, +0.3] |
| H&E mean-logit, single endoscopy | 29.1 | +2.6 [−4.6, +13.7] | +3.1 [−6.2, +8.6] | 28.3 | −1.6 [−4.7, +0.5] | 26.0 | −2.5 [−5.8, +0.5] |
| Memory | 22.9 | −3.7 [−8.9, +2.1] | **−5.3 [−10.7, −0.7]** | 30.7 | +0.8 [−0.4, +2.1] | 29.4 | +0.9 [−0.2, +2.1] |
| Memory + certificate | 21.5 | −5.0 [−11.0, +2.5] | **−6.6 [−12.6, −2.3]** | 30.9 | +1.0 [−0.5, +2.8] | 29.6 | +1.1 [−0.4, +2.6] |
| Final rule | 17.2 | **−9.3 [−16.7, −0.2]** | **−11.2 [−18.0, −6.9]** | 31.8 | **+1.9 [+0.1, +4.1]** | 30.5 | +2.0 [−0.2, +4.6] |
| Memory + check (no certificate) | 19.1 | **−7.4 [−13.4, −0.9]** | **−8.7 [−15.1, −4.4]** | 31.2 | +1.3 [−0.1, +3.3] | 30.1 | **+1.6 [+0.1, +3.6]** |
| Mean-logit + memory | 24.7 | −1.9 [−9.3, +8.8] | −4.5 [−10.8, +7.9] | 30.1 | +0.2 [−2.6, +2.1] | 27.6 | −0.9 [−4.0, +1.7] |
| Mean-logit gate + memory + certificate | 21.9 | −4.6 [−12.1, +3.9] | −6.5 [−11.3, +7.4] | 30.8 | +0.9 [−0.7, +2.7] | 29.4 | +0.9 [−0.9, +3.2] |
| Mean-logit full stack | 17.6 | −9.0 [−16.2, +0.9] | −11.2 [−16.4, +1.2] | 31.4 | +1.5 [−0.2, +3.8] | 30.4 | +1.9 [−0.4, +4.3] |

How to read the table:
- "NP flagged at c caught" is the fewest non-progressors flagged at which the curve's monotone envelope reaches c progressors caught.
- The intervals are wide because the curves are flat near the top: one progressor more or less costs 5–10 non-progressor flags.
- The cleanest single comparison is the "R49's own caught" column. In each bootstrap draw, it reads each curve at R49's caught count. The final rule flags 11.2 [6.9, 18.0] fewer non-progressors there.

**Does memory help every base? (paired, memory minus the same base without memory)**

| Base | Δ caught at 23.6 NP | Δ caught at 17.2 NP | Δ NP flagged at 30.5 caught |
|---|---|---|---|
| Gate score | +0.8 [−0.4, +2.1] | +0.9 [−0.2, +2.1] | −3.7 [−8.9, +2.1] |
| Mean-logit | **+1.8 [+0.3, +3.7]** | **+1.6 [+0.2, +3.2]** | **−4.4 [−8.3, −1.7]** |
| H&E max (no gate) | +1.0 [−0.2, +2.1] | +0.9 [−0.3, +2.4] | −3.4 [−6.0, +0.1] |
| Mean-logit gate | +0.6 [−0.2, +1.8] | +1.1 [−0.1, +2.1] | −4.2 [−8.4, +0.8] |
| Grade (EW) | +1.0 [−0.7, +3.3] | not estimable | — |
| Grade + p53 (EW) | +0.4 [−0.8, +2.5] | not estimable | — |
| Grade, running mean | −0.1 [−3.3, +2.2] | — | — |

**Panel C (pathology, fair comparator).**
- Averaging grade or grade + p53 over a patient's endoscopies does not reproduce the H&E memory gain. The EW curves lie on or near the single-endoscopy curves, and a running mean is slightly worse.
- "Running worst grade" is identical to "ever flagged", so it gives the fixed points.
- Pathology is coarse: on the grade curves, going from 17 to 21 caught costs 8–9 more non-progressors. No pathology threshold reaches 30 caught without flagging about 40 of 43 non-progressors.
- At the same 25 non-progressors flagged:

| Rule | Progressors caught (of 32) |
|---|---|
| Grade IND/LGD | 17 |
| Grade IND/LGD or p53 aberrant | 21 |
| The H&E curves | 30–31 |

So memory is not a generic smoothing benefit. It needs a continuous score whose within-patient noise is larger in non-progressors (the ICC finding).

**Fixed points (no threshold, held-out):**

| Rule | Caught | NP flagged |
|---|---|---|
| Grade IND/LGD ever | 17.0 | 25.0 |
| LGD ever | 14.0 | 16.0 |
| p53 aberrant ever | 12.0 | 1.0 |
| Grade or p53 (p53 missing = normal) | 21.0 | 25.0 |
| LGD or p53 | 19.0 | 17.0 |
| Grade or p53, restricted to endoscopies with p53 (round-8 P10, scaled to 32 / 43) | 19.6 | 23.6 |

p53 is available for 220 of 288 endoscopies.

**Apparent (OPTIMISTIC: threshold swept on the evaluated patients, per repeat).** Caught at 17 / 23.5 non-progressors flagged:

| Rule | Caught at 17 NP | Caught at 23.5 NP |
|---|---|---|
| Gate | 28.4 | 29.6 |
| Memory | 29.4 | 30.9 |
| Memory + certificate | 29.2 | 30.3 |
| Mean-logit + memory | 28.4 | 30.1 |
| H&E max | 26.1 | 27.9 |
| Grade EW | 14.6 | 17.0 |
| Grade + p53 EW | 19.1 | 21.0 |

The nested curves are close to these, so the curves are not mainly selection artefacts. That holds for the threshold step only; the families themselves were chosen post hoc in round 9.

### 2. Full stack on the mean-logit base and the tiered menu

Operating points at target D, ranked by non-progressors flagged among rules within about one progressor of R49:

| Rule | Caught | NP flagged | Samples/patient | ΔNP vs R49 | Δcaught vs R49 | ΔNP vs P1 | Δcaught vs P1 | Cost/patient |
|---|---|---|---|---|---|---|---|---|
| **Mean-logit full stack** (mean-logit gate + memory + certificate + check) | 30.3 | **16.2** | 3.12 | **−15.6 [−20.1, −11.2]** | −0.8 [−1.7, −0.1] | −19.8 [−24.8, −14.6] | −0.8 [−2.3, +0.7] | £947 |
| Final rule | 30.5 | 17.2 | 3.82 | −14.6 [−18.9, −10.3] | −0.6 [−1.6, +0.2] | −18.8 [−23.9, −13.7] | −0.6 [−2.1, +1.3] | £1,067 |
| Mean-logit gate + memory + certificate | 30.3 | 20.1 | 1.43 | −11.7 [−15.1, −8.3] | −0.8 [−1.7, −0.1] | −15.9 [−20.3, −11.4] | −0.8 [−2.3, +0.7] | £974 |
| Memory + check (no certificate) | 30.7 | 20.4 | 4.05 | −11.4 [−15.6, −7.4] | −0.4 [−1.3, +0.4] | −15.6 [−20.7, −10.4] | −0.4 [−1.9, +1.4] | £1,173 |
| Memory + certificate | 30.5 | 21.5 | 1.94 | −10.3 [−13.9, −6.9] | −0.6 [−1.6, +0.2] | −14.5 [−19.0, −9.6] | −0.6 [−2.1, +1.3] | £1,096 |
| Mean-logit gate + memory | 30.5 | 22.6 | 1.43 | −9.2 [−12.4, −6.0] | −0.6 [−1.5, +0.0] | −13.4 [−17.7, −9.1] | −0.6 [−1.9, +0.8] | £1,088 |
| Mean-logit + memory + check (no gate) | 31.0 | 22.9 | 3.14 | −8.9 [−13.2, −5.2] | −0.1 [−1.2, +0.9] | −13.1 [−18.1, −8.5] | −0.1 [−0.9, +0.7] | £1,145 |
| … + check-derived certificate (threshold chosen with the check in the loop) | 31.0 | 23.0 | 2.93 | −8.8 [−13.1, −5.1] | −0.1 [−1.2, +0.9] | −13.0 [−17.9, −8.5] | −0.1 [−0.9, +0.7] | £1,098 |
| Memory | 30.7 | 23.6 | 1.94 | −8.2 [−11.4, −5.1] | −0.4 [−1.3, +0.4] | −12.4 [−16.9, −7.9] | −0.4 [−1.9, +1.4] | £1,224 |
| Mean-logit + memory | 31.0 | 26.6 | 0 | −5.2 [−8.2, −2.4] | −0.1 [−1.2, +0.9] | −9.4 [−13.4, −5.6] | −0.1 [−0.9, +0.7] | £1,169 |
| H&E max + memory (no gate) | 31.2 | 32.1 | 0 | +0.3 [−2.7, +3.4] | +0.1 [−1.2, +1.7] | −3.9 [−6.4, −1.7] | +0.1 [−0.9, +1.2] | £1,324 |
| R49 | 31.1 | 31.8 | 1.94 | 0 | 0 | −4.2 [−7.4, −1.2] | 0.0 [−1.5, +1.9] | £1,362 |
| P1 90% | 31.1 | 36.0 | 0 | +4.2 [+1.2, +7.4] | 0.0 [−1.9, +1.5] | 0 | 0 | £1,242 |
| Grade or p53 | 21.0 | 25.0 | 0 | −6.8 [−13.3, −0.5] | **−10.1 [−15.2, −5.1]** | −11.0 [−17.9, −4.3] | −10.1 [−15.0, −5.1] | £613 |

Notes:
- **The mean-logit full stack** is the best point found, and the least sequencing among the check rules. It removes one more non-progressor than the final rule (16.2 vs 17.2) with 0.7 fewer samples per patient (3.12 vs 3.82). It is cheaper by £120 per patient. The cost is 0.2 more progressors lost; its Δcaught CI against R49 excludes 0, at −0.8 [−1.7, −0.1].
- On the curve the two stacks are indistinguishable: 17.6 vs 17.2 non-progressors at 30.5 caught.
- **Without the gate** (mean-logit + memory + check), no progressor is lost against mean-logit + memory: 31.0 caught, 22.9 flagged. The check-in-the-loop threshold and the check-derived certificate change almost nothing (23.0–23.2) and save 0.2 samples per patient.
- **The check needs the gate's certificate to shine.** On H&E max without the gate, memory + check gives 31.2 caught / 27.1 flagged at 3.75 samples per patient, a poor return.

**Tiered menu.** Net £ per non-progressor flag avoided = 75 × Δcost per patient / −ΔNP; negative means the step saves money. Costs are at £85 per sample and £535 per flagged endoscopy, in the case-control mix.

| Tier | Rule | Caught | NP flagged | Samples/patient | Cost/patient | vs tier 0: ΔNP | Δcaught | Δcost/patient | Net £ per NP flag avoided | Net £ per progressor lost |
|---|---|---|---|---|---|---|---|---|---|---|
| 0: no sequencing | Mean-logit + memory | 31.0 | 26.6 | 0 | £1,169 | — | — | — | — | — |
| 1: ~1.4 samples | Mean-logit gate + memory + certificate | 30.3 | 20.1 | 1.43 | £974 | −6.5 [−9.7, −3.6] | −0.7 [−1.7, +0.2] | −£196 [−306, −92] | −£2,257 (saves) | −£20,957 (saves) |
| 1′: ~1.9 samples | Memory + certificate | 30.5 | 21.5 | 1.94 | £1,096 | −5.1 [−9.2, −1.1] | −0.5 [−1.6, +0.7] | −£73 [−197, +47] | −£1,079 | −£11,003 |
| 2 (no loss): ~3.1 samples | Mean-logit + memory + check (no gate) | 31.0 | 22.9 | 3.14 | £1,145 | −3.7 [−7.1, −1.1] | 0.0 | −£24 [−135, +79] | −£492 | — |
| 3: ~3.1 samples | Mean-logit full stack | 30.3 | 16.2 | 3.12 | £947 | −10.4 [−15.2, −6.2] | −0.7 [−1.7, +0.2] | −£222 [−374, −83] | −£1,599 | −£23,759 |
| 3′: ~3.8 samples | Final rule | 30.5 | 17.2 | 3.82 | £1,067 | −9.4 [−14.1, −5.0] | −0.5 [−1.6, +0.7] | −£102 [−260, +53] | −£816 | −£15,332 |
| ref | R49 | 31.1 | 31.8 | 1.94 | £1,362 | +5.2 | +0.1 | +£193 | — | — |

Against R49, every tier saves money: £193 (tier 0), £388 (tier 1), £414 (tier 3) and £295 (tier 3′) per patient. Moving up the tiers costs about 0.7 progressors for about 10 fewer non-progressor flags. In this cost model each step also saves money, because a flag costs more than the sequencing that removes it. The trade is clinical, not financial.

### 3. Real-world reweighting (per 1,000 patients over the cohort's follow-up)

Method: class-specific held-out rates reweighted to the progression share. Over the follow-up, non-progressors have a median of 5 pre-event endoscopies (mean 4.65) and progressors 2.75. "Extra endoscopies" assumes every flagged endoscopy triggers one.

**3% progressing (30 of 1,000):**

| Rule | Patients flagged | Extra endoscopies | Samples sequenced | PPV | NPV | Progressors missed (of 30) | NP never flagged (de-escalation candidates, of 970) | Flagged per progressor caught |
|---|---|---|---|---|---|---|---|---|
| Grade or p53 | 584 [439, 718] | 1,140 | 0 | 0.034 | 0.975 | 10.3 [5.3, 15.5] | 406 | 29.6 |
| R49 | 747 [637, 844] | 2,060 | 2,642 | 0.039 | 0.997 | 0.8 [0.0, 2.2] | 253 | 25.6 |
| Memory | 561 [442, 687] | 1,629 | 2,642 | 0.051 | 0.997 | 1.2 [0.4, 2.3] | 438 | 19.5 |
| Final rule | 417 [303, 542] | 839 | 3,872 | 0.069 [0.053, 0.096] | 0.998 | 1.4 [0.5, 2.5] | **582 [457, 696]** | 14.6 |
| Mean-logit + memory | 629 [509, 743] | 1,940 | 0 | 0.046 | 0.997 | 0.9 [0.1, 2.1] | 370 | 21.6 |
| Mean-logit full stack | 394 [277, 512] | 728 | 2,803 | 0.072 [0.055, 0.104] | 0.997 | 1.6 [0.5, 3.1] | **605 [487, 722]** | 13.9 |
| Final rule OR grade/p53 | 722 | 1,684 | 3,872 | 0.040 | 0.997 | 0.9 | 277 | 24.8 |

PPV and non-progressors never flagged at the other prevalences:

| Rule | PPV 1.5% | PPV 5% | PPV 10% | NP never flagged 1.5% / 5% / 10% |
|---|---|---|---|---|
| Grade or p53 | 0.017 | 0.056 | 0.111 | 412 / 398 / 377 |
| R49 | 0.020 | 0.065 | 0.127 | 257 / 247 / 234 |
| Memory | 0.026 | 0.084 | 0.163 | 444 / 429 / 406 |
| Final rule | 0.035 | 0.111 | 0.209 | 591 / 570 / 540 |
| Mean-logit + memory | 0.023 | 0.076 | 0.148 | 376 / 362 / 343 |
| Mean-logit full stack | 0.037 | 0.117 | 0.218 | 614 / 592 / 561 |

Progressors missed per 1,000:

| Rule | 1.5% | 5% | 10% |
|---|---|---|---|
| Grade or p53 | 5.2 | 17.2 | 34.4 |
| R49 | 0.4 | 1.4 | 2.8 |
| Final rule | 0.7 | 2.3 | 4.7 |
| Mean-logit full stack | 0.8 | 2.7 | 5.3 |
| Mean-logit + memory | 0.5 | 1.6 | 3.1 |

![prevalence](../paper/figures_explore_E9/fig_e9_prevalence.png)

Reading, consistent with the gastroenterologist's critique:
- **As an escalation tool, the PPV is too low.** It is at most 7% at 3% progression and about 11–12% at 5%. The ≥ 15% bar is reached only at 10% progression.
- **As a de-escalation tool, the numbers are strong.** At 3%, the final rule never flags 582 of 1,000 patients and the mean-logit full stack 605. In that group 1.4–1.6 of 30 progressors are missed over the whole follow-up (NPV 0.997–0.998).
- **Today's practice:**

| Rule (3%) | Patients never flagged | Progressors missed |
|---|---|---|
| Grade or p53 | 406 | 10.3 |
| Today's gate | 253 | 0.8 |

- **Against grade or p53**, the final rule clears 176 more patients and misses about 9 fewer progressors per 1,000.

### 4. Break-even

Per 1,000 patients: rule minus comparator. The break-even sequencing price is the highest £ per sample at which the rule costs no more than the comparator. "Saves at any price" means it sequences no more and flags less. A negative value means it costs more at any price. The break-even flag cost is the lowest £ per flag at which the rule saves.

**Against today's gate (R49):**

| Rule | Break-even £/sample, 43% mix, per flagged endoscopy | Same, flag once per patient | 3%, per flagged endoscopy | 3%, flag once per patient | Flag-cost threshold at £85/sample, 3%, per endoscopy |
|---|---|---|---|---|---|
| Memory, memory + certificate | saves at any price | saves at any price | saves at any price | saves at any price | any flag cost |
| Mean-logit + memory, mean-logit gate + memory (+ certificate) | saves at any price (less sequencing) | saves at any price | saves at any price | saves at any price | any flag cost |
| Final rule | £242 [171, 336] | £58 [36, 91] | £531 [398, 751] | £143 [86, 242] | £86 [61, 114] |
| Mean-logit full stack | £438 [281, 775] | £100 [55, 201] | £4,443 (sequences only +160 samples per 1,000) | £1,176 | £10 [−24, +40] |
| Mean-logit + memory + check (no gate) | £266 [146, 501] | £54 [24, 115] | £3,731 | £888 | £12 [−64, +74] |
| Final rule OR grade/p53 | £86 [27, 152] | £5 [−14, 25] | £163 [24, 326] | £11 [−38, 65] | £278 [139, 1,265] |

Missed-progressor cost barely matters against R49, because the rules lose at most about 0.6 progressors per 1,000 at 3%. At the 43% mix and £20k per miss, the final rule's break-even falls from £242 to £157 per sample (£72 at £40k).

**Against standard care (grade or p53, no sequencing).** Here the missed-progressor cost dominates. Break-even £/sample at miss cost £0 / £20k / £40k:

| Rule | 3%, per flagged endoscopy | 3%, flag once per patient | 10%, flag once per patient |
|---|---|---|---|
| Memory | −£99 / −£30 / £39 | £5 / £73 / £142 | £0 / £241 / £481 |
| Final rule | £42 / £88 / £134 | £23 / £69 / £115 | £18 / £172 / £326 |
| Mean-logit full stack | £79 / £141 / £203 | £36 / £98 / £161 | £29 / £232 / £436 |
| Final rule OR grade/p53 | −£75 / −£27 / £22 | −£19 / £29 / £78 | −£21 / £141 / £303 |

Mean-logit + memory sequences nothing, so it has no break-even price. Per 1,000 at 3%, it costs £427,724 more than standard care at a £0 miss cost (flags once per endoscopy) and £240,224 more at £20k. With the flag costed once per patient, it costs £24,325 more at £0 and saves £163,175 at £20k.

Reading the break-even results:
- **Against today's gate**, every memory rule saves at £85 per sample. The final rule keeps saving up to about £240 per sample in the cohort mix and about £530 at 3% prevalence, when every flagged endoscopy costs a £535 action.
- **If a flag is a once-per-patient pathway change**, the final rule's break-even falls to about £58 (cohort) or £143 (3%) per sample. An NHS sWGS price of £150–300 would then erase the saving.
- **The mean-logit full stack** sequences barely more than R49 in a non-progressor-dominated population. It saves at any realistic price.
- **Against grade or p53**, the AI rules cost more unless a missed progressor is valued:
  - at £20–40k per miss and 3% progression, the final rule breaks even at about £70–135 per sample;
  - at 10% progression, about £170–340 per sample.
- **The realistic deployment is "rule OR grade/p53"**, because pathologist dysplasia calls will not be ignored. It needs a miss cost of about £40k to break even near £80 per sample at 3%.

### 5. What this adds, and caveats

- **Every point is post hoc.** All of it is about 650 variants deep. The curves remove the "convenient operating point" objection for the threshold, but not for the family choice.
- **Undercounted costs.** The cost model is round 8's (£85, £535), with no discounting, scanning, AI licence or failed samples. A £15-per-sample AI scoring cost is reported in the JSON for the comparison with standard care.
- **The per-1,000 numbers assume transportability.** They assume the cohort's class-specific per-patient rates carry over over the same follow-up. Non-progressors here have about twice the endoscopies of progressors, so per-patient flag rates are follow-up-dependent.
- **No endoscopy-level matched specificity.** Δ endoscopy specificity at matched endoscopy sensitivity was not recomputed here; the patient-level curves replace it for this angle.


### 6. Most promising finding, and next steps

**Finding.** At 3% progression the memory rules work as de-escalation tools:

| Rule | Patients never flagged (of 1,000) | Progressors missed (of 30) |
|---|---|---|
| Final rule | 582 | 1.4 |
| Mean-logit full stack | 605 | 1.6 |
| Today's gate | 253 | 0.8 |
| Grade or p53 | 406 | 10.3 |

Memory does not transfer to pathology grade, so the gain is specific to the continuous H&E score.

**Next.**
1. Recompute the trade-off and prevalence tables on the exposure-matched endpoint (first 2–3 endoscopies per patient). This answers the follow-up confound in the per-1,000 numbers.
2. Rebuild the de-escalation table in time: years from the last "never flagged" endoscopy to the event for the 1–2 missed progressors, and whether grade or p53 would have caught them (the `OR grade/p53` rows suggest about 0.5 per 1,000 are recovered).
3. Pre-specify one rule per tier (tier 0: mean-logit + memory; tier 1: mean-logit gate + memory + certificate; tier 3: mean-logit full stack), freeze and hash them, then score ACE-B for the within-endoscopy parts.
4. Replace the per-flag cost with a pathway model (flag means a 6-month repeat with Seattle biopsies) and use NHS sWGS prices (£150–300). The break-even then hinges on the flag-once-per-patient column: the final rule loses its saving above about £60–140 per sample, while the mean-logit full stack keeps it.

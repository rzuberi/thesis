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

(pending)

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

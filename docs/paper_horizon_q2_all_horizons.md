# Q2 sample-level breakdown at 1, 3 and 5 years (late fusion vs CNV, their matrix)

Status: PRE-SPECIFICATION (written 2026-10-05). Nothing below has been run. Results are appended under the line at the end in a later commit; this section is not edited afterwards.

Ground rules as in `docs/paper_horizon_answers.md` (pre-specification 81473df, results afa0278): no refit; report only; status per item; at most one line of interpretation; earlier docs not edited; row-level patient lists on the cluster only.

## Source and definitions (unchanged from Q2 of `docs/paper_horizon_answers.md`)

- Same run, same predictions, same operating point: `scripts/paper_plan/ha_q2.py` (commit afa0278). Per horizon t, model, repeat and outer fold, the threshold is the largest value with ≥ 80% sensitivity among that horizon's pre-event training cases on the inner out-of-fold predictions; applied to the held-out outer predictions of the same repeat; a sample is positive if positive in ≥ 6 of 10 repeats. L-LATE vs L-CNV, their matrix, all pre-event samples of the discovery subset (571 samples, 75 patients). Cases and controls per horizon as in `docs/paper_horizon_answers.md` (case: event within t; control: event-free with follow-up ≥ t).
- Groups per horizon: **newly caught cases** = horizon cases negative under L-CNV and positive under L-LATE; **cases caught by both** = positive under both; **newly cleared controls** = horizon controls positive under L-CNV and negative under L-LATE.

## What is reported per horizon (1, 3, 5 years)

- Newly caught cases: samples and patients; newly cleared controls: samples and patients.
- For newly caught cases vs cases caught by both: mean (and SD) raw cx (package block, recovered with the frozen scaling constants of `models/killcoyne_frozen_pkg_v1/cnv_scaling_setC.csv`), mean (and SD) tissue tiles available (`horizons/slide_desc.csv`).
- Newly caught cases scored low risk by Killcoyne's published model: number with published probability Pr ≤ 0.3 (MOESM4 'Supporting data for Figure 2a' `Probability`; cross-checked against `k_prob` in `set_C.csv`).
- A check that the group counts equal `results/paper_final/horizon_answers/q2.json`.
- Whether 3 years was designated a primary horizon in any pre-specification commit, with hashes and quoted text.

## Output

`docs/paper_horizon_q2_all_horizons.md`; script `scripts/paper_plan/hq_all.py` (Slurm via `scripts/cluster/campaign.sh`); aggregates `results/paper_final/horizon_q2_all/q2_all.json`; per-horizon patient lists (study numbers) only on the cluster: `feasibility/paper_plan/killcoyne_mm/horizon_answers/q2_all_horizons_patients.csv`.

---

## Results

Pre-specification commit e645dcf; results commit aa7cfe2. Script `scripts/paper_plan/hq_all.py` (Slurm, prefix hq), `scripts/paper_plan/hq_render.py`. Aggregates `results/paper_final/horizon_q2_all/q2_all.json`. Source rows: the Q2 per-sample list from `ha_q2.py` (afa0278), cluster-only; patient lists for this document: `feasibility/paper_plan/killcoyne_mm/horizon_answers/q2_all_horizons_patients.csv` (cluster only).

### Status

| Item | Status |
|---|---|
| Breakdown at 1, 3 and 5 years | DONE |
| Counts equal `q2.json` (afa0278) | yes, every horizon |
| Published probability: MOESM4 vs `set_C.csv` k_prob | identical (max |difference| 0.0) |
| Was 3 years a pre-specified primary horizon? | No (details below) |

### Late fusion vs CNV (their matrix), all pre-event samples

Newly caught = cases negative under L-CNV and positive under L-LATE; newly cleared = controls positive under L-CNV and negative under L-LATE. Samples / patients. Means of raw cx (package block) and tissue tiles; published Pr ≤ 0.3 = Killcoyne's published probability (MOESM4).

| Horizon | Cases newly caught | Controls newly cleared | cx, newly caught | cx, caught by both | Tiles, newly caught | Tiles, caught by both | Newly caught with published Pr ≤ 0.3 | Caught by both with Pr ≤ 0.3 | Cases caught by both |
|---|---|---|---|---|---|---|---|---|---|
| 1 year | 6 / 3 | 70 / 30 | 25.8 (SD 7.3) | 23.4 (SD 9.2) | 206.3 (SD 109.5) | 386.6 (SD 416.0) | 3 / 6 | 0 / 21 | 21 / 13 |
| 3 years | 11 / 6 | 58 / 26 | 21.3 (SD 5.6) | 30.0 (SD 13.6) | 324.1 (SD 367.2) | 412.7 (SD 756.1) | 8 / 11 | 1 / 73 | 73 / 26 |
| 5 years | 13 / 8 | 31 / 14 | 21.2 (SD 5.7) | 29.5 (SD 12.6) | 307.5 (SD 340.1) | 650.2 (SD 1019.4) | 8 / 13 | 1 / 91 | 91 / 28 |

### Answer

At every horizon late fusion clears more control samples than it newly catches case samples: 6 caught vs 70 cleared at 1 year, 11 vs 58 at 3 years and 13 vs 31 at 5 years. The newly caught cases are mostly ones Killcoyne's published model scored low risk at 3 and 5 years (8/11 and 8/13 with Pr ≤ 0.3) and have lower CNV complexity than cases both models catch (mean cx 21.3 vs 30.0, 21.2 vs 29.5); at 1 year the 6 newly caught samples (3 patients) do not follow that pattern (cx 25.8 vs 23.4; 3/6 low risk). Newly caught cases have fewer tissue tiles on average at every horizon, with wide spread. One line: the 3-year pattern holds at 5 years but rests on 3 patients at 1 year.

### Was 3 years a pre-specified primary horizon?

No. No pre-specification commit designates a primary horizon for the AUROCs or for Q2:
- `81473df` (2026-10-05, pre-specification of `docs/paper_horizon_answers.md`, whose Q2 produced these numbers): horizons 1, 3 and 5 years are treated alike; Q2 asks for every comparison "at each horizon" and for the newly captured / cleared groups without naming a horizon. The 3-year emphasis in that document's Q2 answer was a reporting choice made after the results, not pre-specified.
- `ee51db8` (2026-10-01, pre-specification of `docs/paper_survival_horizons.md`) is the only commit that names 3 years, and only for the descriptive breakdown of H2, which used a different operating point (80% sensitivity for the ever-progression label): "Operating point (a), 3-year horizon, their matrix, best model and L-LATE; the other cells' counts reported."
- `2d0014f` (fold-stratified AUROC) and `487b2a7` (grade row) do not designate a primary horizon.

**Method.** No new predictions or thresholds: the groups are those of `ha_q2.py` (afa0278) at each horizon; this script only adds means, SDs and the published-probability count. **Sources.** `q2_patient_list.csv` (cluster), `killcoyne_data_from_paper/41591_2020_1033_MOESM4_ESM.xlsx` ('Supporting data for Figure 2a' `Probability`), `models/killcoyne_frozen_pkg_v1/cnv_scaling_setC.csv` (raw cx), `horizons/slide_desc.csv` (tiles).
**Caveats.** (1) The operating point is fitted for each horizon's cases, so the three horizons use different thresholds; the groups are not nested. (2) Samples, not patients, are the unit of the means; several samples come from the same patient. (3) Tile counts are highly skewed (SDs exceed the means), so the mean difference in tiles is not robust to a few large slides; the medians were reported in `docs/paper_horizon_answers.md`. (4) Design caveat: matched case–control cohort; no absolute risks or PPVs.


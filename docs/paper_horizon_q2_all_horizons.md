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

(appended in a later commit)

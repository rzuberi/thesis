# calib strand — PLAN (20 Oct 2026, written before any run)

Question: can one model's confidence, recalibrated or combined with other signals, match or beat ten-model jury vote-fraction triage?

## Fixed before running
- Models: project-1 RL model (`rl_grader/runs/p1_best_merged`) and D2 (`rl_followups/D/runs/d2/checkpoint-150`, LoRA on p1_best_merged, confidence prompt).
- New scoring (GPU): greedy generation (as before), then for every section score each of the six grade strings by
  log P(GRADE + '"' | prompt + generated text up to `"grade": "`). Six log-scores per section = the full grade distribution.
  Sets: val, test, test485, pop, all_lowconf. Also keep the old first-token `p_grade` for comparability.
- Calibration (fit on **val only**, jury labels): temperature over the six log-scores (NLL), isotonic on p_max as a check.
  Report ECE (10 bins, weighted, as Task A) and AUROC on the 479 before/after, plus on the jury test fold.
- Combination: logistic regression fit on **val** (target: model grade != jury consensus); features = logit p_max(cal), entropy,
  margin, section letter index, WHOLE flag, report length, and (combo variant) jury vote fraction + model==jury flag.
  Caveat known in advance: val has jury_vf >= 0.75 only; pop has 429 sections below. A second combo fit on val + all_lowconf
  (p1 only; those patients overlap training patients) is reported as secondary.
- Triage: the existing tie-aware estimator (copied from p2_metrics.py, unchanged logic) at 5/10/17/20/30% of reports,
  each method minus jury vote-fraction triage, paired patient bootstrap (2,000, seed 20261016). Primary operating point 20% (as Task D).
- Conformal: split conformal on val (score 1 - p_cal(jury label)), alpha = 0.10 and 0.05; on the 479 report coverage vs human and
  vs jury, mean set size, and the rule "review if set size > 1" (fraction of sections and reports sent, accuracy after review).
- The 479 are never used for fitting, thresholds or selection. Nothing is tuned on them.
- Smoke test on N=5 sections per set before the full runs. Two GPU jobs (one per model), <= 1 h each.

## Outputs
- `analysis/rl_explore/calib/preds/<tag>__<set>.jsonl` (cluster only), `results.json`, `reliability_calib.png`, `triage_calib.png`.
- Local: `~/Documents/job-search/rl-projects/explore/RESULTS_calib.md`.

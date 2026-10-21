# Explore / grader: closing the 4B-vs-jury gap (PLAN, written 20 Oct 2026 14:45 before any run)

Gap to close: one MedGemma-4B SFT→GRPO model = 89.1–90.6% (3 seeds) vs ten-model jury 93.0%, weighted exact grade on the 479
hand-graded sections. Budget ~11 h wall clock, ≤4 GPUs, deadline 02:30 21 Oct.

## Chosen
1. **(a) Soft-label reward from the jury** — GRPO from the project-1 SFT model (seed 0, `rl_grader/runs/sft_merged`), 300 steps,
   everything as project 1 except the reward: `r = max(share(pred), 0.3·same_side)`, `−0.5` invalid JSON, where share(pred) = fraction
   of jurors who listed the predicted grade for that section (from `erin_sections_v3_consensus.csv` grade_votes / n_jurors). On
   unanimous sections this reduces exactly to the project-1 reward, so it is a strict generalisation.
   - **a1 soft+all:** training prompts = class-capped train (vf ≥ 0.75) **plus all 1,028 low-agreement train-patient sections**
     (the point of soft labels: use sections the hard-label recipe had to throw away).
   - **a2 soft only:** same reward, project-1 training set only (isolates reward change from data change).
2. **Control: (a3) longer GRPO** — resume the seed-0 project-1 GRPO run from checkpoint-300 to 600 steps, unchanged reward. Two of three
   seeds picked their last checkpoint on validation, so the recipe may simply be under-trained; without this control a gain from a1/a2
   could be a steps effect.
3. **(d) Ensembles (CPU):** majority vote of the 3 seed RL models (tie → worst grade / seed-0 / most-severe rules, fixed below); 3 seeds +
   MedGemma-27B zero-shot (4 voters); and, after training, the new models added. Also 3-seed majority on the jury-test fold.

## Amendment 15:05 (before any full run; smoke test still running)
Checked `frac_reward_zero_std` in the existing GRPO logs: seed-0 SFT→GRPO 0.78 (steps ≤50) → 0.94 (last 50); seeds 1–2 0.73→0.90/0.92;
GRPO-from-base 0.51→0.66. So most groups give no gradient, and the soft reward cannot change that for a unanimous group (identical shares).
Therefore **a2 (soft reward, P1 data) is dropped** and replaced by **a4: P1 reward, P1 data, but only prompts whose 8 SFT samples (T = 1,
mined once from `sft_merged`) are mixed (0 < acc < 1)**; same 300 steps, so compute is matched. a1 keeps the soft reward because the
low-agreement sections are where mixed groups are likeliest. GPU use stays at 3 training jobs. Report zero-std fractions for every run.

## Not chosen
- (b) reason-then-answer: the SFT model emits `{"grade"}` only and there are no reasoning targets; GRPO-from-base with reasoning reached
  84% in project 1, well below SFT→GRPO. Would need a reasoning-SFT stage we cannot build in the time.
- (c) bigger base: neither Qwen3-14B nor MedGemma-27B is in the offline HF cache (only Qwen3-4B/8B, MedGemma-4B); 27B GRPO with a colocated
  vLLM copy would not fit the 141 GB/step-time budget anyway (~12 h for 300 steps).

## Evaluation (identical to project 1)
- Checkpoints every 50 steps scored on the jury-labelled **validation** fold only; best checkpoint then run on test (jury fold) and test485.
- test485: population-weighted exact and dysplasia yes/no vs human; paired patient bootstrap (2,000, seed 20261016) vs the seed-0 RL model
  (`grpo_sft__checkpoint-300`) and vs the jury. Jury-test fold agreement reported.
- Ensemble tie rule fixed now: majority of valid votes; ties broken by the seed-0 model's prediction (it is the published model).

## Jobs (all `x_grader_*`, race3 on cuda/h200)
smoke (20 steps, 50 items, eval 50) → a1, a2, a3 in parallel (3 GPUs, ~3 h each on H200) → val evals of checkpoints → best on test/test485 → CPU report.

## Amendment 23:10 (coordinator): deadline mode
The smoke job was preempted at 15:00 and, on requeue, exited on its own stale lock (`run_task.sh` treats the requeued job id as a live
owner). Its first attempt had trained 10 soft-reward steps (checkpoint-10 saved), which is taken as the smoke pass for training; the
evaluation path is the unchanged project-1 `evaluate.py`. a1/a3/a4 (300 steps each) no longer fit before 02:30. Replaced by ONE arm,
**short**: 100 GRPO steps from the P1 RL model (`p1_best_merged`), soft jury reward + the 1,028 low-agreement sections, checkpoints 50/100
selected on validation, then test/test485 — all in one job, H200 twins only (an L40S twin cannot finish by 02:00). Reported only if it finishes.

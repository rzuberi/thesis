# Explore/agent plan (20 Oct 2026, 15:00)

Starting point (Task E): the tool-using SQL agent after GRPO answers 59.1% of held-out answerable questions (per-template 42.6%),
versus 47.1% / 40.9% for single-shot SFT; it falsely refuses 22.7% of answerable questions (all on templates it cannot solve:
older_hgd 30/30, avg_age 12/15, patients_per_organ 13/18), and its gain is concentrated in per-year questions. Only 12 answerable
training templates (289 questions) remain.

## Arms (all share one change set so that arm A isolates it)
- **A — shaped reward + schema doc.** GRPO from the SFT model (same recipe as Task E: 150 steps, B=8 x G=8, lr 1e-5, beta 0.04)
  with the SCHEMA.md doc appended to the system prompt and a shaped outcome reward: refusing an answerable question −0.5 (was 0),
  executed-but-wrong final query +0.1 (was 0), +0.05 if at least one `run_sql` probe executed successfully; unanswerable unchanged
  (refuse +1, answer −0.5).
- **B — expert iteration, then A.** Sample 8 episodes per training question from the Task-E GRPO agent and 4 from the untrained SFT
  agent (temperature 1, new prompt), keep correct trajectories (correct answer or correct refusal), de-duplicate, cap 2 per answerable
  question (fewest tool calls first) and 1 per unanswerable question. SFT the merged SFT model on them (LoRA r=16, loss on assistant
  tokens only, 2 epochs, lr 1e-4), merge, evaluate as an agent, then GRPO as in A from that model.
- **C — training diversity, then A.** New parameter values for the 12 answerable training templates (same gold SQL; ~70 new base
  questions) plus 2 fresh Qwen3-4B paraphrases of every training base question; GRPO as in A on the enlarged training set.
- **D (if time) — B + C.**
Justification: B attacks the "few kinds of question" problem by distilling the agent's own successful behaviour before RL (cheap and
the usual first step when RL plateaus); A is the direct fix for false refusals and for wasted `describe` calls; C is the only way to
widen the training distribution without touching held-out templates.

## Evaluation
Same held-out split (20 answerable + 8 unanswerable templates), greedy decoding, `report2.py` = e_report metrics plus per-template
accuracy (primary), paired 2,000-resample template bootstrap vs single-shot SFT (`agsplit_sft__final`) and the Task-E GRPO agent
(`checkpoint-150`). Checkpoints chosen on the 7 validation templates only (mean per-template correctness). Extra baselines: the
Task-E agent and the untrained SFT agent re-run with the schema prompt (no training), to separate the prompt change from training.

## Compute plan
Smoke test (1 GPU, ~20 min), then jobs A, B, C in parallel (≤3 GPUs; each ~1.5–2 h), then D. Deadline 02:30.

## Change of scope (23:05, 20 Oct)
The session was interrupted at ~15:00 (API spend limit) right after the smoke test passed; jobs A/B/C were never submitted. With
~3 h left and contended GPUs, only **arm B** (expert iteration + shaped reward + schema prompt) is run, plus the no-training
baseline evaluation (Task-E agent and untrained SFT agent under the new prompt). Arms A, C and D are not run; their isolating
comparisons are therefore unavailable and the result attributes any change to the bundle (prompt + reward + expert iteration).

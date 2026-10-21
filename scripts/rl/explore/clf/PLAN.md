# clf strand — PLAN (written 20 Oct 2026 ~15:00, before any training)

Question: does a cheap encoder classifier trained on the same jury labels match the 4B RL grader?

Data (unchanged, read-only): analysis/rl_grader/data/{train,val,test,test485,pop}.jsonl. Train = 14,380 sections (vf >= 0.75),
val 1,771, jury-test 1,808, test485 = 479 human-graded sections (TEST ONLY), pop = 4,929 population sections for triage.

Input text: "[SECTION X]\n" + report (GROSS / FINAL DIAGNOSIS / MICROSCOPIC as in common.report_text). For 512-token models the
report is reduced to lines that mention the section letter first, then other lines in document order until the budget fits.

Models (all 6-way heads, plain cross-entropy, bf16, select on validation exact agreement with the jury, per half-epoch):
1. TF-IDF (word 1-2 grams + char 3-5 grams) + logistic regression, CPU — the floor.
2. BioClinical-ModernBERT-base (150M, 8k ctx; we use max 2,048 tokens), seeds 0/1/2, lr 3e-5, bs 16, 3 epochs.
3. BioClinical-ModernBERT-large (396M), seed 0, lr 2e-5, bs 16, 3 epochs.
4. Bio_ClinicalBERT (110M, 512 ctx, section-focused truncation), seed 0, lr 3e-5, bs 32, 3 epochs.

Evaluation = project 1's metrics.py logic (copied, not edited): weighted exact + dysplasia yes/no on the 479 with hand-label
weights, n=50 random slice, unweighted, paired patient bootstrap (2,000, RandomState(0)) vs RL seed 0 (grpo_sft checkpoint-300),
vs SFT seed 0 (sft__final), vs jury, vs MedGemma-27B. Inference seconds per report on test485 (GPU, batched) and parameter counts.
Triage: p2_metrics.py fed with PDIR pointing at our preds (score = max softmax prob), PRIMARY_FRAC 0.20; error AUROC on the 479.

Decision rule fixed in advance: "matches the RL model" = paired CI of (clf − RL) on weighted exact includes 0 AND point within 2.
Compute budget: <= 3 GPUs at once, L40S fine. Smoke test (N=64, 20 steps) before full runs.

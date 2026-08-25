# Red-team review: converged findings (2026-08-25)

Five independent reviewers — a fresh-context Claude agent, GPT-5.6 Terra Pro,
Grok-4.6, DeepSeek-V3.2 (frontier, via OpenRouter), plus four local models —
reviewed the plan, pre-registrations, drafts, and full results digest. Findings
ranked by cross-family convergence (a flaw found independently by 3+ model
families is treated as established).

## Converged, severity 5 (all or nearly all reviewers)

1. **LLM self-validation loop.** Claude adjudicated the truth set; the LLM jury is
   validated against it; jury labels train Ch3/Ch4 models; LLM reviewers reviewed
   the result. Only human anchor: a pending 10-case spot check.
   FIX: independent pathologist grading of a stratified ~200-300 report sample
   (including the unsure stratum), blind to machine labels. -> R.4
2. **Central claim unsupported as stated.** No cohort shows fusion beating the
   best unimodal arm; the pooled +0.061 is against a collapsed histology arm and
   loses to clinical-alone; the SWG fusion-vs-HISTOLOGY CI (the hypothesis-named
   contrast) was never computed. FIX: compute it (top priority); adopt
   fusion-vs-best-unimodal as the decisive contrast everywhere; reframe (done —
   see amendment).
   **RESOLUTION (2026-08-25): the SWG CI existed all along.** The strict
   pre-event release table `lgd2_final_pre_event_paired_differences.csv`
   (barretts_training, 150 patients, 5,000 paired bootstraps) carries
   late_mean − image_only: ΔAUPRC +0.073 [0.006, 0.125], ΔAUC +0.043
   [0.015, 0.071], ΔBrier −0.061 [−0.095, −0.027] — all three exclude zero.
   It was computed in the 2026-07-13 release but never transcribed into the
   chapter, so no reviewer saw it. This softens the finding: SWG does show
   fusion beating histology (and UNI2 histology is the stronger unimodal arm
   there), internally, on the pre-registered protocol. It does not overturn the
   reframe — the win is single-cohort, internal-CV, winner's-curse-exposed
   (late-mean chosen among 7 families), and every external arm is null — which
   is exactly the "where and why fusion fails to replicate" story. Residual
   RESOLVED (1.13b, reproduction-gated recomputation, `results/
   latemean_vs_gigapath_paired.json`): against GigaPath histology — the
   strongest unimodal arm by point — ΔAUPRC +0.020 [−0.064, 0.104] and ΔAUC
   +0.041 [−0.020, 0.103] cross zero; only ΔBrier −0.048 [−0.085, −0.011]
   excludes it. Net verdict: fusion > histology is decisive under the
   pre-registered primary encoder, encoder-conditional under the sweep (the
   amended sign-flip rule applies — claim downgraded to encoder-conditional),
   and unreplicated externally. Transcribed into swg_arm.md.
3. **Ch3 primary endpoint circularity.** Current-grade classification reconstructs
   the pathologist's reading of the same slide — recognition, not prediction.
   FIX: progression becomes Ch3's primary estimand; grade classification moves to
   Ch4 as an annotation-replacement result.
4. **Ch4 label-quality experiment circularly evaluated** (scored against jury
   labels). FIX: full cross-evaluation matrix + human-truth evaluation.

## Converged, severity 4

5. OCCAMS deviations: n=141->87 unexplained; shuffled controls omitted from the
   decisive run. FIX: controls job + attrition flow diagram.
6. Genotype-visibility reversal inconsistently handled: Ch1 text stale; Grok's
   sharpening — the n=446 "visibility" came from adding STAD/GEJ (population
   change), OAC-only TP53 was anti-predictive with a failing shuffled control.
   FIX: rewrite Part A around the learning-curve + population story; debug the
   failed probe control.
   PROBE DEBUG DONE (2026-08-25, results/tcga_probe.json): a 50-permutation
   empirical null shows the earlier "failing control" (0.557 from 5 shuffles)
   was sampling noise — null is 0.474±0.13 (TP53) / 0.517±0.08 (WGD) at
   n=65/58. Real AUCs sit at the 20th/14th null percentile: no signal, pipeline
   valid, the TCGA-OAC negative stands and replicates the OCCAMS n=141 probe.
   Ch1 text rewritten (evaluation_protocol.md) to the conditional
   size-and-population story.
7. PORPOISE (published baseline) never run — in-house nulls can't be attributed.
8. Jury kappa 0.90 inflated by NDBE base rate; specimen-level collapse (0.60)
   shows fragility; correlated-LLM-errors caveat mandatory.
9. 96.5% accuracy is tcga_gi/TCGA-scoped; cannot vouch for ERIN barretts_ladder.
10. Multiplicity: many paired contrasts, no correction; SWG winner selection
    (7 families) has winner's-curse exposure; SWG lower bound 0.002 fragile.

## Notable singletons worth acting on

- (Grok) pathladder's negation fix was derived from the same error sample used to
  declare the competing grader wrong — label-function leakage; revalidate the
  widened window on a fresh sample.
  DONE 2026-08-25 (results/negation_revalidation.json): on 6,867 fresh
  confident-jury reports, pathladder-vs-jury agreement is 0.817 (audit sample:
  0.821 — no optimism gap, so the 80-case audit was not flattering), but the
  CANCER over-call persists: 321 fresh plad=CANCER vs jury=NDBE confusions,
  300 of them negation-bearing. The widened window generalises only partially;
  Grok's concern was material. Consequence for Ch4: pathladder is a strong
  cheap baseline (~82% vs jury), not a substitute — which the label-source
  experiment already showed at the model level (jury-trained = pathladder-
  trained downstream AUC).
- (DeepSeek) the encoder-sweep pre-reg's "headline stays the primary config" rule
  insulates claims from falsification — amend: a sign flip in the sweep DOWNGRADES
  the claim.
- (GPT-5.6) bootstrap CIs at 58/36 events omit split/seed/model uncertainty —
  temper language; report seed-variance alongside.

## Verdict adopted

All reviewers independently converge with the fresh-context agent's verdict: the
scaffolding is strong, the positive-replication claim is not supported, and the
honest, stronger thesis is the reframe recorded in the amendment log.


---

# Wave 2 addendum (2026-08-25, evening)

Five additional frontier families reviewed the CURRENT repo state (post-reframe,
post-fixes), BLIND to this findings document: DeepSeek-V4-Pro, Kimi-K3, GLM-5.3,
Qwen3.8-Max, Gemini-3.7-Flash. With wave 1 that makes 8 independent model
families + 4 local models.

## Blind convergence with wave 1 (validates the original findings)

- Self-validation loop / Claude-as-adjudicator: 5/5 wave-2 families, most as
  severity 5. R.4 (pathologist sample) is confirmed as THE critical unblock.
- SWG winner's curse + GigaPath collapse of the headline contrast: 4/5.
- Pooled-visibility population confound (n=446 mixes OAC/GEJ/STAD): 4/5.
- Grade-endpoint circularity: 4/5 (now addressed by the reframe swap).
- Jury homogeneity (agreement among similar LLMs ≠ truth): 3/5.
- PORPOISE still missing: 2/5.

## New findings unique to wave 2

1. **The reframe itself is flagged as post-hoc hypothesis revision (HARKing)**
   (Kimi sev-5, GLM sev-5, DeepSeek sev-5). Response adopted: the thesis must
   present the reframe as hypothesis-GENERATING, defended by the dated amendment
   trail (results known, reasons stated, nothing hidden), and the reframed claim
   must not be presented as confirmed by the same data that motivated it.
   External confirmation = the pre-registered OCCAMS/TCGA arms and R.4.
2. **ERIN pre-reg endpoint swap was silent** (DeepSeek sev-5, GLM/Gemini sev-4,
   Qwen sev-5). FIXED same day: explicit dated deviation note added to
   erin_ch3_preregistration.md; the swap demotes the flattering endpoint.
3. **multiplicity_plan.md is itself post hoc** (Kimi sev-4, GLM sev-4, Qwen
   sev-3): "confirmatory" contrasts chosen after CIs were known. Amended: the
   plan now states it is a reporting discipline, not pre-registration.
4. **Own Outcome-D rule ignored for off-0.5 shuffled controls** in OCCAMS v2
   (gen 0.58), TCGA first-pass (0.54), and probes (5/5 families flag some form).
   FIX: apply the 1.17 lesson (5-shuffle controls are noise) — recompute proper
   50-permutation nulls for every flagged control, or formally annotate
   Outcome D. Queued as 1.20.
5. **Progression cohort v2-vs-v3 unreconciled** (Kimi sev-3, Qwen sev-3): the
   two "final" cohorts differ by 48 patients / −16 progressors with no recorded
   reconciliation, and the direction (fewer events after removing false
   CANCERs) needs explaining. Queued as 1.21.
6. **Encoder-sweep grid extended twice post-freeze** (Kimi/GLM sev-3):
   H-Optimus-0 was pre-declared conditional on access, but Phikon-v2 was not in
   the frozen grid. Deviation now recorded in the pre-reg.
7. **Ceiling effect** (DeepSeek sev-5): ERIN grade histology is at 0.91-0.93,
   so CI-positive fusion deltas of +0.01 ride a ceiling; claims must be framed
   as "measurable at ceiling", clinical relevance unargued.
8. **Unsure-holdout selection bias** (Gemini sev-4): excluding the 206 hardest
   reports makes the reported population easier than deployment. FIX: sensitivity
   analysis scoring held-out unsure cases. Queued as 1.22.
9. **Clinical-arm label leakage risk** (Qwen sev-3/4): prior-grade-history
   features and grade labels derive from the same report stream. FIX: ablation
   dropping prior-grade from the clinical arm. Queued as 1.23.

## Wave-2 verdict

No wave-2 reviewer found a NEW thesis-threatening flaw outside the wave-1 set —
the severity-5 mass concentrates on the same two structural issues (human
anchor R.4; post-hoc claims must be labelled as such). The reframe survives
blind review as the honest reading of the results, PROVIDED it is presented as
hypothesis-generating with the amendment trail as its provenance.

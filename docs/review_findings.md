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
- (DeepSeek) the encoder-sweep pre-reg's "headline stays the primary config" rule
  insulates claims from falsification — amend: a sign flip in the sweep DOWNGRADES
  the claim.
- (GPT-5.6) bootstrap CIs at 58/36 events omit split/seed/model uncertainty —
  temper language; report seed-variance alongside.

## Verdict adopted

All reviewers independently converge with the fresh-context agent's verdict: the
scaffolding is strong, the positive-replication claim is not supported, and the
honest, stronger thesis is the reframe recorded in the amendment log.

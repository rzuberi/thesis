# Two papers, agent P2N: selection-aware permutation null for Paper 2

Status: PLAN written 21 October 2026 before any null was run; results are appended below the line. Brief: `paper/two_papers/PAPER2_plan_v2.md`, new analysis 1. Reviews: `review_strategy_integrity.md` (item 8), `review_P2_editor.md`, `review_strategy_sceptic.md` (risk 1). Rules: `paper/two_papers/RUN_RULES.md`.

## Plan

**The objection.** The E7 null (`docs/paper_explore_E7.md`, test 7) used 50 + 50 label shuffles, kept the stored predictions (models trained on the true labels) and re-scored only the frozen path (R49 cut-offs, memory threshold and half-life, certificate, check bar) plus an optimistic best of 243 cells. It did not rerun the choice among the families, which was made after seeing held-out results. With 100 shuffles p cannot go below about 0.01.

**1. Variant log (supplement).** Count every held-out rule cell that was scored, by stage and family, from the committed aggregates (`scripts/paper_plan/tp_p2n_varlog.py` -> `results/paper_final/two_papers_P2N/variant_log.json`), with each family's best cell and the order of discovery.

**2. Selection criterion (fixed now).** Across every searched cell: the fewest held-out non-progressor (NP) patients flagged, among cells that catch at least as many progressor patients as the R49 gate minus a tolerance, both computed under the same labels. **Primary tolerance 1.0 progressor patient**: the smallest round tolerance that admits every rule actually promoted (memory + certificate −0.6, final rule −0.6, mean-logit full stack −0.8 against R49). Also 0, 0.5 (the round-9 ranking rule as written) and 2.0, and the unconstrained "excess" statistic of E7 (Δ share NP flagged − Δ share caught). Statistic = best cell's NP flagged − R49's NP flagged (more negative = bigger gain).

**3. The null.** Patient-level permutation of the progressor label among the 75 evaluated patients (32 progressors kept; the 5 training-only patients, all progressors with event samples only, keep their label). For each label set the whole search is rerun with its own code:
- **(a) Full refit:** L-IMG and L-CNV elastic nets refitted inside the folds under the permuted labels (kv_cv.R outer loop and hz_fit.R inner out-of-fold loop, same λ rules; outer and inner folds re-stratified on the permuted labels as the pipeline does), L-LATE = their mean; then every label-using rule step: R49 cut-offs, memory thresholds and hyper-parameters, certificates, veto thresholds and bars, stackers, per-fold selections. Target 1,000 permutations (at least 200).
- **(b) Fixed scores:** stored predictions, rule search rerun (E7's approach, extended to the whole search). 1,000 free permutations and 1,000 within endoscopy-count strata (E7's 'strat', which keeps the progressors' shorter histories).
- **Families rerun:** all round-9 families (every candidate and the per-fold 'np' and 'pAUC' selections) on the max-logit gate; E2 fixed vetoes (25 features + L-CNV + L-LATE × k × 4 rules × 3 bases), double vetoes, grade-gated, AND, batch/noise-adjusted, stability and per-fold-selected vetoes; E2 vetoes on the memory bases (A1, A1 longer half-lives, A12); E7 check-bar sweep and in-fold bar; E8 arm-set checks; E3 endoscopy aggregations (mean / median logit, mean probability, top-2 logit) with P1, R49 rebuilt and the memory families; E9 mean-logit full stack and mean-logit memory + check. In (b) also the E3 extractor, pooling and ensemble variants from their stored refits.
- **Not rerun** (say so in Methods): E1 (tile-level fixes), E2 elastic-net vetoes, E4 time-aware refits, E5 ERIN rules, round-9 B4 refits, E3 extractor refits in (a). None came within 3 NP of the selected rules on real labels.
- **p-value** = (1 + #{null ≤ real}) / (B + 1).

**Smoke checks before the full run.** SHUF 0 must reproduce R49 31.1 / 31.8, P1 31.1 / 36.0, memory 30.7 / 23.6, A12 30.5 / 21.5, final 30.5 / 17.2, in-fold bar 30.4 / 16.4, mean-logit memory 31.0 / 26.6, mean-logit full stack 30.3 / 16.2; the SHUF 0 refit must reproduce the stored L-IMG and L-CNV predictions exactly (so L-IMG 0.847 and L-CNV 0.801 follow).

**Files.** Scripts `scripts/paper_plan/tp_p2n_{refit.R,search.py,merge.py,varlog.py,task.sh,figs.py}`; aggregates `results/paper_final/two_papers_P2N/`; figures `paper/two_papers/figs_P2N/`; row-level `killcoyne_mm/two_papers_P2N/`; Slurm prefix `tpp2n`.

---

## Results

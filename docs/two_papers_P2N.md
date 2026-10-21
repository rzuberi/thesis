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
- **Not rerun** (say so in Methods): E1 (tile-level fixes), E2 elastic-net vetoes, E4 time-aware refits, E5 ERIN rules, round-9 B4 refits, E3 extractor refits in (a), minor E8 check variants.
- **p-value** = (1 + #{null ≤ real}) / (B + 1).

**Smoke checks before the full run.** SHUF 0 must reproduce R49 31.1 / 31.8, P1 31.1 / 36.0, memory 30.7 / 23.6, A12 30.5 / 21.5, final 30.5 / 17.2, in-fold bar 30.4 / 16.4, mean-logit memory 31.0 / 26.6, mean-logit full stack 30.3 / 16.2; the SHUF 0 refit must reproduce the stored L-IMG and L-CNV predictions exactly (so L-IMG 0.847 and L-CNV 0.801 follow).

**Files.** Scripts `scripts/paper_plan/tp_p2n_{refit.R,search.py,merge.py,varlog.py,task.sh,figs.py}`; aggregates `results/paper_final/two_papers_P2N/`; figures `paper/two_papers/figs_P2N/`; row-level `killcoyne_mm/two_papers_P2N/`; Slurm prefix `tpp2n`.

---

## Results

Written 21 October 2026 (evening). Scripts as in the plan; aggregates `results/paper_final/two_papers_P2N/` (`variant_log.json`, `check0.json`, `merge.json`); figures `paper/two_papers/figs_P2N/` (local). Every number is on held-out patients (mean over the 10 repeats) unless marked; counts of 32 progressor and 43 non-progressor (NP) patients.

### 1. Variant log (supplementary table)

Built by `tp_p2n_varlog.py` from the committed aggregates only. A *cell* is one rule scored on held-out patients with its thresholds set on training patients (per-fold selected rows and fixed hyper-parameter grid points both count). Cells whose threshold was set on the evaluation patients ("matched", "apparent") are listed separately and never ranked; label-leaking demonstrations (E1 batch shares from all labels) are counted but never ranked. Best cell = fewest NP flagged with caught ≥ 30.1 (R49 31.1 − 1).

| Stage (date, 2026) | Family | Cells | Best cell within one progressor of R49: caught / NP flagged / samples per patient |
|---|---|---|---|
| 0. Round 7 (pre-specified) | R49 gate (t_low 95%, t_high 90%) fixed as the main rule; sample-level triage pre-specified | – | 31.1 / 31.8 / 1.94 (reference) |
| 0. Round 8 map (20 Oct, descriptive; R49 already fixed) | Policies P1–P10 | 77 | P3 80% 30.5 / 26.4 / 7.61 |
| 1. Round 9 (20 Oct) | Memory functions on the R49-aligned gate score (running, EW half-lives 0.5–16 y, last-2, k-of-n, recalibration) | 35 | EW memory 30.7 / 23.6 / 1.94 |
| | Memory functions on the literal gate score | 30 | 31.3 / 24.6 / 1.94 |
| | Memory functions on H&E alone (max L-IMG) | 30 | 31.5 / 31.2 / 0 |
| | Memory functions on the stacked B1 gate score | 30 | 31.3 / 31.9 / 2.27 |
| | Sample aggregation (mean, top-2, max L-LATE) × memory | 21 | 31.2 / 24.5 / 7.61 |
| | Confirm-by-sequencing (A4) ± memory | 17 | 30.8 / 23.1 / 3.15 |
| | Certificates (copy-number A2, p53 A2') | 16 | 30.8 / 26.9 / 1.24 |
| | **Memory + copy-number certificate (A12)** | 26 | **30.5 / 21.5 / 1.94** |
| | Memory + p53 certificate | 14 | 30.5 / 22.2 / 1.94 |
| | Stacked gate (grade, age, sex, p53) and controls | 84 | 30.1 / 23.1 / 1.73 |
| | Stacked gate + memory + certificate | 26 | 31.0 / 29.8 / 2.27 |
| | Agreement within endoscopy (A3) | 10 | 30.6 / 29.8 / 1.51 |
| | Abstention (B3) | 4 | 31.1 / 30.1 / 1.94 |
| | R49 cut-offs re-tuned (control) | 28 | 30.6 / 26.9 / 1.90 |
| | Refits: NP weight 2; NDBE samples only | 58 | 30.8 / 26.9 / 1.96 |
| 2. E1 (20–21 Oct) | Tile-score substitutions, single-feature vetoes, second-stage filters, sample-count penalty | 220 | 30.8 / 30.8 / 1.94 |
| 3. E2 (20 Oct) | Fixed copy-number and trained-score vetoes on P1, R49 high band, all R49 flags (25 features + L-CNV + L-LATE × k 1/2 × 4 bar rules × 3 bases; the "about 650") | 648 | 30.5 / 24.2 / 4.35 |
| | Double vetoes (trained score low AND quiet) | 192 | 31.0 / 23.9 / 4.35 |
| | Elastic-net vetoes trained on H&E-flagged samples | 144 | 30.3 / 27.0 / 4.35 |
| | Grade-gated vetoes; H&E AND copy number; batch / noise-adjusted; stability | 151 | 30.4 / 24.4 / 2.80 |
| | Veto chosen per outer fold | 42 | 30.2 / 22.7 / 3.16 |
| | **Vetoes on the memory bases (A1, A1 longer half-lives, A12): the quiet-genome check joins A12 here** | 54 | 30.5 / 16.9 / 3.82 (final rule: 30.5 / 17.2 / 3.82) |
| 4. E3 (20 Oct) | 57 H&E score variants (extractors, scales, poolings, ensembles, endoscopy aggregations) × P1 80/90/95%, R49 rebuilt | 228 | 30.2 / 28.1 / 0 |
| | 14 score variants inside the memory engine (**mean-logit + memory found here**) | 56 | 30.3 / 19.8 / 1.41 (mean-logit + memory, no sequencing: 31.0 / 26.6 / 0) |
| 5. E4 (20–21 Oct) | Time-aware refits (Cox, horizons, certainty weights) × 8 rules; inside memory | 178 | 30.2 / 21.7 / 2.00 |
| 6. E5 (20 Oct) | ERIN dysplasia score alone, stacked, as veto or rescue, inside memory | 105 | 30.6 / 22.9 / 1.94 |
| 7. E7 (20 Oct) | Check bar sweep 70–97.5% and in-fold bar (the other E7 tests are robustness checks) | 10 | in-fold bar 30.4 / 16.4 / 3.82 |
| 8. E8 (21 Oct) | Check variants on A12 (arm subsets, QC gates, noise scaling, agreement, flattening, soft veto) | 90 | 30.5 / 17.2 / 3.82 |
| 9. E9 (21 Oct) | Mean-logit full stack, check-in-the-loop, tier combinations | 10 | **mean-logit full stack 30.3 / 16.2 / 3.12** |
| **Total** | | **2,634** (2,557 from round 9 on; plus 646 optimistic cells not ranked) | |

**Order of discovery.** R49 gate (round 7, pre-specified) → round-8 map (R49 kept by a panel) → round 9: memory (A1) and the copy-number certificate (A12) → E2: the quiet-genome check, first picked as the no-loss cell among the 648 R49-base cells, then applied unchanged to the memory bases the same evening (final rule) → E3: mean-logit endoscopy score (no-sequencing tier) → E7/E8: bar sweep, in-fold bar, arm and noise variants → E9: mean-logit full stack and tiers.

**Selection criterion actually used.** Round 9, E1, E3 and E5 ranked by Δ NP flagged against R49 among rows with Δ caught ≥ −0.5 (point estimate). The promoted rules broke that line slightly: A12 and the final rule (−0.6) and the mean-logit full stack (−0.8). E2 picked the check as the "no progressor lost" cell with the largest NP reduction. A tolerance of one progressor is the smallest round tolerance that reproduces every promotion, so it is the primary criterion of the null.

**"About 650" understates the search.** 648 is the E2 R49-base grid alone. Counting every held-out cell, the false-flag search scored 2,557 cells in 34 families (2,634 with the round-8 map), on 75 patients. The paper should say "about 2,600 held-out rule cells in 34 families (supplementary table)", not "about 650 variants".

### 2. Smoke checks (reproduced)

- **SHUF 0, both modes** (`check0.json`): R49 31.1 / 31.8 / 1.94; P1 31.1 / 36.0; memory 30.7 / 23.6; A12 30.5 / 21.5; final rule 30.5 / 17.2 / 3.82; in-fold bar 30.4 / 16.4; mean-logit + memory 31.0 / 26.6 / 0; mean-logit gate + memory 30.5 / 22.6 / 1.43; mean-logit full stack 30.3 / 16.2 / 3.11 (E9: 3.115); R49 + check 31.1 / 26.6; memory + check 30.7 / 20.4; R49 re-tuned 30.6 / 29.4; 17p-only check 30.5 / 19.7. One expected difference: R49 rebuilt on the mean logit gives 30.9 / 30.8 here against E3's 30.9 / 31.2, because the top-H&E sample is picked by E3's 1e-6 logit tie-break (as in E3's memory runs and E9) rather than by E3's separate pick.
- **Full refit at SHUF 0** reproduces every stored outer and inner L-IMG and L-CNV prediction exactly (max |difference| 0.0, folds identical), so L-IMG 0.847, L-CNV 0.801 and L-LATE 0.889 follow.
- Mode (a) searches 1,664 cells per label set; mode (b) 2,096 (the extra 432 are the E3 extractor, pooling and ensemble variants, tagged `e3x`).

### 3. The real best-of-search (same code, true labels)

| Tolerance (caught ≥ R49 − tol) | Selected cell | Δ NP vs R49 | Δ caught |
|---|---|---|---|
| 0 | A4 confirm-by-sequencing + EW memory, h = 4 y (grid point) | −8.2 | +0.3 |
| 0.5 | (a) memory + double veto (L-LATE low and OAC quiet < 90%); (b) EW memory of the mean-logit concat UNI2-h + GigaPath gate score (grid point) | −11.4 / −11.7 | −0.4 / −0.5 |
| **1.0 (primary)** | **mean-logit full stack (gate + memory + certificate + check)** | **−15.6** | **−0.8** |
| 2.0 | A12 + check at the 75% bar | −16.7 | −1.2 |
| none ("excess") | A12 + check at the 75% bar | excess −0.351 | |

The primary criterion picks the rule the project actually promoted last (E9), so the null tests the real path.

### 4. Selection-aware null: best of the whole search (B = 1,000 permutations each)

Statistic: Δ NP flagged (of 43) of the best cell against R49 under the same labels. Null mean [2.5–97.5%]; n = null searches at or below the real value; p = (1 + n) / 1,001 (floor 0.001).

| Null | Real | tol 0 | tol 0.5 | **tol 1.0 (primary)** | tol 2.0 | Excess (real −0.351) |
|---|---|---|---|---|---|---|
| **(a) full refit + whole search** | −8.2 / −11.4 / **−15.6** / −16.7 | −3.6 [−8.0, −1.0]; n 24; p 0.025 | −4.6 [−9.1, −1.9]; n 6; p 0.007 | **−5.5 [−10.0, −2.7]; n 1; p 0.002** | −7.0 [−11.9, −3.7]; n 1; p 0.002 | −0.135 [−0.249, −0.056]; n 0; p 0.001 |
| (b) stored predictions + whole search incl. E3 extractors | −8.2 / −11.7 / −15.6 / −16.7 | −4.0 [−9.0, −1.4]; n 44; p 0.045 | −5.2 [−10.3, −2.2]; n 11; p 0.012 | −6.2 [−11.2, −2.9]; n 4; p 0.005 | −7.8 [−12.6, −4.2]; n 5; p 0.006 | −0.147 [−0.273, −0.063]; n 3; p 0.004 |
| (b) same family set as (a) | −8.2 / −11.4 / −15.6 / −16.7 | n 43; p 0.044 | n 13; p 0.014 | −6.2 [−11.2, −2.9]; n 4; p 0.005 | n 5; p 0.006 | n 3; p 0.004 |
| (b′) as (b), permuted within endoscopy-count strata | −8.2 / −11.7 / −15.6 / −16.7 | −2.8 [−7.6, −0.9]; n 15; p 0.016 | −4.3 [−9.3, −1.5]; n 5; p 0.006 | −5.6 [−11.0, −2.5]; n 0; p 0.001 | −7.6 [−13.5, −3.8]; n 2; p 0.003 | −0.148 [−0.282, −0.050]; n 1; p 0.002 |

- **What the search alone buys.** Under permuted labels the best of about 1,700–2,100 cells already "clears" 5.5–6.2 NP patients (95th–97.5th percentile about 10–11) while staying within one progressor of R49; the selected null cell's Δ caught is −0.6 to −0.8 (real −0.8). That is the selection optimism E7 did not measure. The real search clears 15.6, about 10 more than the typical null search, and 1 (a), 4 (b) and 0 (b′) of 1,000 null searches reach it.
- **Which families win under the null** (tol 1.0, mode a): the E2 R49-base veto grid (579 of 1,000), round-9 families (179), grade-gated (64) and batch-adjusted (61) vetoes. Large grids, not the memory or check families, generate the chance gains.
- **The exposure imbalance contributes little to the null.** Permuting within endoscopy-count strata (keeps progressors' shorter histories) gives the same null centre (−5.6) as free permutation.
- **Strict tolerance (tol 0) is the weak spot.** Without any allowance for lost progressors the best real cell is only −8.2 (A4 + memory, sequencing 3.15 per patient), and p = 0.016–0.045: much of the gain of the promoted rules is bought with 0.5–0.8 progressor patients.

**No-sequencing tier, selection rerun among no-sequencing cells only** (statistic: best cell that sequences nothing):

| Null | Real | tol 0.5 | tol 1.0 |
|---|---|---|---|
| (a) full refit | −5.5 (mean-logit + EW memory, h = 4 y; Δ caught 0.0) | null −1.0 [−5.7, +3.2]; n 29; **p 0.030** | null −1.7 [−7.0, +2.7]; n 68; **p 0.069** |
| (b) stored, incl. E3 extractors | −6.5 / −6.6 (concat UNI2-h + GigaPath mean-logit memory) | p 0.026 | p 0.057 |
| (b′) strata | −6.5 / −6.6 | p 0.010 | p 0.020 |

**Frozen path (E7's statistic, now with 1,000 permutations and the full refit)**: Δ NP vs R49 of each named rule rebuilt under permuted labels (every label-using step rerun, the rule's structure fixed). p (a / b / b′): memory −8.2: 0.001 / 0.001 / 0.004; memory + certificate −10.3: 0.001 / 0.001 / 0.001; final rule −14.6: 0.001 / 0.001 / 0.002 (null mean −2.8 / −3.7 / −6.6); in-fold bar −15.4: 0.001 / 0.001 / 0.002; mean-logit gate + memory −9.2: 0.001 / 0.001 / 0.006; mean-logit full stack −15.6: 0.001 / 0.001 / 0.001; **mean-logit + memory (no sequencing) −5.2: 0.020 / 0.060 / 0.022** (excess statistic 0.005 / 0.014 / 0.007); R49 re-tuned (control) −2.4: 0.009 / 0.070 / 0.167.

Figures (local): `paper/two_papers/figs_P2N/fig_p2n_null.png` (primary null, three panels), `fig_p2n_null_tier0.png` (no-sequencing tier), `fig_p2n_null_scatter.png` (Δ caught against Δ NP of the selected null cells).

### 5. What it means for Paper 2

- **The confirmatory-tier result survives its own search.** Rerunning the whole search on 1,000 permuted label sets, with both models refitted, the best rule found clears 15.6 NP patients against a null of 5.5 [2.7–10.0]; p = 0.002. The reviewers' main objection to the selection is answered for the copy-number tiers.
- **The no-sequencing tier does not, on its own.** Mean-logit + memory clears 5.2 NP patients; the best no-sequencing cell of a permuted search clears 1.7 on average and up to 7.0 (97.5%), so p = 0.03–0.07 depending on tolerance. Its internal evidence is suggestive, not conclusive: the ERIN-archive test is needed before it can be the headline recommendation, and the abstract should not lean on it as an established finding.
- **Report the size of the search correctly**: about 2,600 held-out cells in 34 families, not "about 650".

### 6. Methods paragraph (draft for Paper 2)

> *Selection-aware permutation test.* The rules were chosen from 2,557 held-out rule cells in 34 families (Supplementary Table X) after held-out results had been seen. To estimate how much of the gain this search could produce by chance, we permuted the progressor label among the 75 evaluated patients (32 progressors kept; the five patients contributing only event-time training samples kept their label) 1,000 times. For each permutation we refitted the H&E and copy-number elastic-net models inside the same cross-validation pipeline (10 repeats × 10 outer folds, re-stratified on the permuted labels; inner five-fold out-of-fold predictions for training-patient thresholds; the original λ rules), rebuilt every label-dependent step of every searched rule (gate cut-offs, memory thresholds and half-lives, certificates, veto thresholds and check bars, stackers and per-fold selections), scored all 1,664 rule cells on held-out patients, and applied the selection criterion used in development: the cell with the fewest non-progressor patients flagged among cells catching at least as many progressor patients as the per-endoscopy gate minus one. The test statistic was that cell's difference from the gate in non-progressor patients flagged; the p-value is (1 + number of permutations at or below the observed value)/(1,001). Two sensitivity versions kept the stored predictions and reran only the rule search (2,096 cells including the alternative H&E feature extractors), with labels permuted freely or within strata of endoscopy count. Families that needed other refitted models or features (tile-level filters, elastic-net vetoes, alternative H&E feature extractors, time-aware and external dysplasia models, and minor variants of the copy-number check; about 40% of logged cells) were not rerun; apart from check variants that reproduce the final rule's decisions, none came within three non-progressor patients of the selected rule.

### Implementation notes

- **Permutations** (`TASK=perms`): `perms.csv` (free, 1,000) and `perms_strat.csv` (within strata of 1, 2, 3, 4, 5–6, ≥ 7 pre-event endoscopies, 1,000), `RandomState(20261021 + b)` (+100,000 for strata), column s0000 = true labels; row-level, cluster only.
- **Refit** (`tp_p2n_refit.R`): `kv_common.R` unchanged; y replaced by the permuted patient label; outer folds `strat_folds(pat, y, REP, 10)`, inner `strat_folds(pat[otr], y[otr], 1000·REP + k, 5)`, λ by `cvcurves` (outer, 10 × 5) and `cvcurves1` (inner), image block z-scored on the training rows, copy-number block (`cnv_their_C.csv`) as stored. One task per permutation ran four Rscript processes (img / cnv × reps 1–5 / 6–10) then the search.
- **Search** (`tp_p2n_search.py`): executes `ex_e2_veto.py` and `rv9_falseflags.py` up to their dispatch; labels replaced in `tb_common`, the rv8, E2 and rv9 namespaces before `build()`; reference dates cached from the true labels (they feed only lead-time and patient-year summaries). Cells: R49, P1 80/90/95%; all 69 round-9 families (each candidate plus 'np' and 'pAUC' per-fold selections); E2 fixed (648), per-fold selected without elastic-net candidates (36), double (192), grade-gated (64), AND (9), batch/noise-adjusted (60), stability (18); E2 memory-base vetoes (17 vetoes × A1, A1 longer half-lives, A12; threshold set against the R49hm base as in E2); E7 bar sweep (8) and in-fold bar (slack 0, 1; training flags of the chosen A12 candidate from a copy of E7's engine, asserted equal to `run_families`); E8 arm sets (17 OAC-derived sets incl. single arms; OAC k1; fraction altered) with the cn90 bar; E3 aggregations (mean / median logit, mean probability, top-2 logit) with P1, R49 rebuilt and the four memory families, plus A12 and the check on the mean logit (E9 full stack, mean-logit memory + check, mean-logit gate memory + check); mode b only: the 56 stored E3 variants (P1 80/90/95%, R49 rebuilt; memory families for the 14 E3 memory variants), built with E3's own `variant()` reader.
- **Not rerun**: E1 (220 cells: tile contributions need the refitted coefficients), E2 elastic-net vetoes (144), E4 (178), E5 (105), round-9 B4 refits (58), E8 QC/noise/agreement/flattening/soft-veto rows and random-arm controls, E9 check-in-the-loop (4); in (a) also the E3 extractor variants. Together about 780 of 2,557 logged cells (about 30%) in (b) and about 1,030 (about 40%) in (a). Their best real cells are at least 3 NP patients worse than the selected rule (16.2), except E8 check variants that make the final rule's decisions (17.2, i.e. not better than it).
- **Compute**: campaigns `tpp2n0`–`tpp2n5`, `tpp2na` (1,000 tasks, 4 CPUs, ~6 min each: refit ~4 min, search ~2 min) and `tpp2nb` (1,000 tasks of two permutations, ~7.5 min per permutation with the E3 extension), 18:08–21:07 on epyc, cuda and rocm. Row-level outputs (`refit/sXXXX/`, `search/*.npz`, permutations) stay in `killcoyne_mm/two_papers_P2N/`; committed JSON holds only cell-level counts and null summaries.
- **Not done**: a null for the variant families not rerun; a bootstrap of the selected cell's own CI (the paired-bootstrap CIs elsewhere remain conditional on the selection).

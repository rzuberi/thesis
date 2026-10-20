# Exploration E7: is the memory / quiet-genome result an artefact?

Status: EXPLORATORY, COMPLETE (20 October 2026; plan 23:15, results the same night). Rules in `paper/reviews_round7/decisions/EXPLORE_RULES.md`. Nothing here is confirmatory.

## Plan

**Rules under test** (reproduced with the round-9 engine `rv9_falseflags.py`, the E2 veto helpers `ex_e2_veto.py` and the story-deck reconstruction `story_aggs_v2.py`):
- **A1 memory:** EW memory of the R49-aligned gate score, per-fold selected (30.7 caught / 23.6 NP flagged);
- **A12:** memory + copy-number certificate (30.5 / 21.5);
- **Final:** A12 + quiet-genome check (ps_oac, top 2 samples, cn90 bar) (30.5 / 17.2 / 3.82 samples per patient).

Every test is against today's gate (R49), with paired patient-bootstrap 95% CIs (2,000 draws, `RandomState(0)`). Thresholds and hyper-parameters stay on training patients.

1. **Exposure equalised.** Truncate each non-progressor to its first m pre-event endoscopies, m drawn from the progressors' endoscopy-count distribution (200 draws); also first 2 / first 3 endoscopies for everyone. Primary: the frozen per-fold rules evaluated on the truncated histories (memory is causal, so its scores on kept endoscopies are unchanged). Secondary: the whole selection rerun on the truncated cohort (training patients truncated too). Also flags per NP patient-year.
2. **Order shuffle** within patient (100 draws): (a) whole pipeline rerun on shuffled histories; (b) rules selected on true order, applied to shuffled held-out histories.
3. **Prevalent-disease exclusion.** Drop progressor endoscopies within 1 or 2 years of the event; progressors caught by gate / memory / final against pathologist grade (17/32). Also a symmetric version (NP endoscopies within 1 or 2 years of the last endoscopy dropped).
4. **One look per patient.** The check applied only at each patient's first flagged endoscopy; a cancelled flag is final (no later rescue). Fixed cn90 bar and the bar re-chosen inside each fold. Also the first-endoscopy-only (ACE-B-like) projection.
5. **Bar sweep** of the check, 70–97.5% of training progressor endoscopies, plus the in-fold re-chosen bar (headline).
6. **Missing records.** 20% / 40% of past endoscopies missing from the memory (100 draws), rules selected on full histories (deployment) and rerun on the damaged cohort.
7. **Optimism of the search.** 50 patient-level label permutations (free) and 50 permuted within endoscopy-count strata (keeps the exposure imbalance, removes the signal); rerun the selection of half-life / certificate / check bar; distribution of the nested gain and of the best-of-grid apparent gain against the real ones.
8. **Batch.** Does the within-patient score bounce of non-progressors track scanner or sequencing-batch changes between consecutive endoscopies?

**Space.** Script `scripts/paper_plan/ex_e7_stress.py`; aggregates `results/paper_final/explore_E7/`; row-level `killcoyne_mm/explore_E7/`; Slurm prefix `exe7`.

---

## Results

Aggregates: `results/paper_final/explore_E7/base.json` (reproduction, tests 1a, 3, 4, 5, 8, real-label reference for 7) and `merge.json` (tests 1b, 2, 6, 7). Rendered by `scripts/paper_plan/ex_e7_render.py`. Figures (local): `paper/figures_explore_E7/e7_forest.png`, `e7_bar_sweep.png`, `e7_null.png`. All numbers are held-out patients, mean over the 10 repeats; CIs are paired patient bootstraps (2,000 draws, `RandomState(0)`). Every test here is post hoc, on the same 75 patients.

### Verdicts (one line per test)

| # | Test | Verdict | Key number (final rule unless stated; Δ vs R49) |
|---|---|---|---|
| 1 | Exposure equalised | **holds** (about a quarter of the memory gain is exposure) | NP truncated to progressor endoscopy counts: A1 −6.1 [−8.3, −4.0] (was −8.2), final −11.3 [−14.7, −8.1] (was −14.6), caught −0.6; selection rerun on the truncated cohort −6.2 / −11.7; flags per NP patient-year −0.145 [−0.199, −0.102] |
| 2 | Order shuffled within patient | **holds as averaging; "recency memory" breaks** | shuffled and re-selected: A1 −7.7 [−9.9, −5.5], final −14.8 [−18.6, −11.4]; time order adds about 0.5 |
| 3 | Endoscopies within 1 / 2 years of the event dropped | **holds** | ≥ 1 y before the event: final 28.6 / 32 caught (R49 29.1, grade 12.0); ≥ 2 y: 23.7 (25 progressors left; grade 10.0) |
| 4 | Quiet-genome check, one look per patient | **breaks** (as a single-look veto) | fixed bar: −2.6 [−5.7, 0.0] progressors against A12; first endoscopy only −2.1 [−4.7, 0.0]; a bar chosen for one look keeps −0.9 but clears only −0.4 NP |
| 5 | Check bar sweep, in-fold bar | **holds** | 80–97.5% bars lose 0 progressors against A12; in-fold bar 30.4 caught / 16.4 NP flagged, −15.4 [−19.8, −11.1], caught −0.1 [−0.3, 0.0] against A12; 75% loses 0.6, 70% loses 2.4 |
| 6 | 20% / 40% of past records missing | **holds** (degrades gracefully) | at deployment: 20% −12.7 [−16.6, −8.9], 40% −10.9 [−14.7, −7.3]; A1 −6.8 / −5.3 |
| 7 | Optimism of the search (label permutation) | **holds** | real excess (Δ share NP flagged − Δ share caught) −0.32; free null mean +0.005 (2.5–97.5%: −0.115 to +0.074), count-stratified null −0.064 (−0.164 to +0.017); 0 of 50 nulls reach the real value in either; even the optimistic best of 243 cells under the stratified null reaches only −0.125 |
| 8 | Batch / scanner | **holds** (small technical part of the bounce) | scanner change: larger NP H&E swing (+0.90 logit [+0.01, +1.80]) but gate-score swing and flips not clearly; NP ICC unchanged by scanner adjustment (0.214 → 0.216); memory gain present in patients scanned on one scanner (A1 −4.8 of 28 NP, final −7.9) |

### What it means

- **Memory is not an exposure artefact.** With non-progressors cut to the progressors' endoscopy counts (2.5 per patient), memory still removes 6.1 of 25.9 flagged non-progressors at no progressor cost, and the final rule 11.3. It holds with only the first 2 or 3 endoscopies of everyone (−8.0 for A1). When progressors are cut to 2 endoscopies too, the final rule starts losing progressors (−2.3 [−4.7, −0.5] frozen, −1.8 rerun): the same dependence on repeat looks as test 4. The stratified permutation null, which keeps the exposure imbalance and removes the signal, gives about −0.06 excess (about 3 non-progressors at fixed caught): that is the size of the exposure part, against −0.32 real.
- **It is averaging, not recency.** Shuffling the order of a patient's scores (dates kept) barely changes anything (A1 −7.7 vs −8.2). The editor's "persistence" framing is right; "recency-weighted" should be described as patient-level averaging.
- **It is prognostic, not missed prevalent dysplasia.** Dropping the endoscopies within 1 year of the event leaves 28.6 of 32 progressors caught by the final rule (grade: 12). Without the last 2 years the ceiling is 25 (7 progressors have no endoscopy 2 or more years before the event) and the rules catch 23.7–24.2 of them.
- **The in-fold check bar does not lose progressors here.** Re-choosing the check bar on training patients (fewest training NP flagged with no training progressor lost) gives 30.4 / 16.4, Δ caught −0.1 [−0.3, 0.0] against A12. The "loses 1–2" caveat in `WHAT_WE_TRIED.md` came from E2's strict-threshold family on the R49 base, not from this bar family. The safe region is 80–97.5% (four grid steps); below 75% it starts losing progressors.
- **But the check depends on progressors' second chances.** Applied only once per patient, the same check loses 2.6 progressors (2.1 on first endoscopies only, the ACE-B-like setting). Chosen for one look it is nearly useless (−0.4 NP). The check should not be described or tested on ACE-B as a single-endoscopy veto; its claimed safety is a property of repeat surveillance.
- **The search was not the source of the gain.** Under 50 + 50 label permutations with every label-using step re-run, no permutation came near the real excess, and picking the best of 243 cells on the evaluation patients added only 0.02 to the real result (−0.343 vs −0.321).

### Reproduction

Engine re-implementation against the stored round-9 flags: {'A1_flag_mismatches': 0, 'A1_ns_mismatches': 0, 'A12_flag_mismatches': 0, 'A12_ns_mismatches': 0}. Observed (all patients): R49 31.1 caught / 31.8 NP flagged / 1.94 samples per patient; P1 H&E alone 90% 31.1 caught / 36.0 NP flagged / 0.0 samples per patient; A1 memory 30.7 caught / 23.6 NP flagged / 1.94 samples per patient; A12 memory + certificate 30.5 caught / 21.5 NP flagged / 1.94 samples per patient; final (A12 + check, cn90 bar) 30.5 caught / 17.2 NP flagged / 3.816 samples per patient; final, check bar re-chosen in fold 30.4 caught / 16.4 NP flagged / 3.816 samples per patient; pathologist grade ID/LGD 17.0 caught / 25.0 NP flagged / 0.0 samples per patient.

### 1. Exposure equalised

**(a) Frozen rules, truncated held-out histories** (memory is causal, so the scores on kept endoscopies are those of the full rule; frozen per-fold rules (thresholds and hyper-parameters chosen on training patients with full histories) evaluated on truncated held-out histories; non-progressor follow-up for flags per patient-year = first endoscopy to the first dropped endoscopy; draws averaged as fractional patient outcomes, then the paired patient bootstrap).

| Truncation | NP endoscopies per NP patient | R49 NP flagged / caught | Rule | NP flagged | caught | Δ NP vs R49 [95% CI] | Δ caught vs R49 | Δ NP vs P1 | Δ flags per NP patient-year vs R49 | spread of Δ NP over draws |
|---|---|---|---|---|---|---|---|---|---|---|
| np_matched_to_progressor_counts (200 draws) | 2.46 | 25.9 / 31.1 | A1 memory | 19.8 | 30.7 | -6.1 [-8.3, -4.0] | -0.4 [-1.3, +0.4] | -9.7 [-13.1, -6.4] | -0.053 [-0.076, -0.030] | -6.1 (-7.8 to -4.2) |
| np_matched_to_progressor_counts (200 draws) | 2.46 | 25.9 / 31.1 | A12 memory + certificate | 18.5 | 30.5 | -7.3 [-10.0, -4.9] | -0.6 [-1.6, +0.2] | -11.0 [-14.5, -7.5] | -0.089 [-0.121, -0.062] | -7.34 (-9.3 to -5.1) |
| np_matched_to_progressor_counts (200 draws) | 2.46 | 25.9 / 31.1 | final (A12 + check, cn90 bar) | 14.6 | 30.5 | -11.3 [-14.7, -8.1] | -0.6 [-1.6, +0.2] | -14.9 [-18.8, -11.1] | -0.145 [-0.199, -0.102] | -11.3 (-13.6 to -8.69) |
| np_matched_to_progressor_counts (200 draws) | 2.46 | 25.9 / 31.1 | P1 H&E alone 90% | 29.5 | 31.1 | +3.6 [+0.9, +6.5] | +0.0 [-1.9, +1.5] |  | +0.029 [-0.006, +0.063] | 3.63 (2.3 to 4.9) |
| first_2_everyone (1 draw) | 2.0 | 27.7 / 31.1 | A1 memory | 19.7 | 30.3 | -8.0 [-11.3, -4.9] | -0.8 [-2.1, +0.2] | -11.7 [-16.2, -7.3] | -0.057 [-0.087, -0.030] | -8.0 (-8.0 to -8.0) |
| first_2_everyone (1 draw) | 2.0 | 27.7 / 31.1 | A12 memory + certificate | 18.0 | 29.8 | -9.7 [-13.7, -6.0] | -1.3 [-2.5, -0.2] | -13.4 [-18.4, -8.6] | -0.084 [-0.124, -0.050] | -9.7 (-9.7 to -9.7) |
| first_2_everyone (1 draw) | 2.0 | 27.7 / 31.1 | final (A12 + check, cn90 bar) | 15.1 | 28.8 | -12.6 [-17.2, -8.3] | -2.3 [-4.7, -0.5] | -16.3 [-21.5, -11.2] | -0.135 [-0.197, -0.086] | -12.6 (-12.6 to -12.6) |
| first_2_everyone (1 draw) | 2.0 | 27.7 / 31.1 | P1 H&E alone 90% | 31.4 | 31.0 | +3.7 [+0.4, +7.1] | -0.1 [-2.0, +1.4] |  | +0.041 [+0.002, +0.083] | 3.7 (3.7 to 3.7) |
| first_3_everyone (1 draw) | 2.93 | 29.4 / 31.1 | A1 memory | 21.4 | 30.7 | -8.0 [-11.2, -5.1] | -0.4 [-1.3, +0.4] | -12.1 [-16.3, -7.9] | -0.052 [-0.082, -0.025] | -8.0 (-8.0 to -8.0) |
| first_3_everyone (1 draw) | 2.93 | 29.4 / 31.1 | A12 memory + certificate | 19.3 | 30.5 | -10.1 [-14.0, -6.7] | -0.6 [-1.6, +0.2] | -14.2 [-18.8, -9.6] | -0.095 [-0.133, -0.063] | -10.1 (-10.1 to -10.1) |
| first_3_everyone (1 draw) | 2.93 | 29.4 / 31.1 | final (A12 + check, cn90 bar) | 15.7 | 30.3 | -13.7 [-18.3, -9.6] | -0.8 [-1.8, +0.1] | -17.8 [-22.7, -12.9] | -0.146 [-0.200, -0.102] | -13.7 (-13.7 to -13.7) |
| first_3_everyone (1 draw) | 2.93 | 29.4 / 31.1 | P1 H&E alone 90% | 33.5 | 31.1 | +4.1 [+1.1, +7.3] | +0.0 [-1.9, +1.5] |  | +0.025 [-0.010, +0.058] | 4.1 (4.1 to 4.1) |
| first_2_non_progressors_only (1 draw) | 2.0 | 27.7 / 31.1 | A1 memory | 19.7 | 30.7 | -8.0 [-11.3, -4.9] | -0.4 [-1.3, +0.4] | -11.7 [-16.2, -7.3] | -0.057 [-0.087, -0.030] | -8.0 (-8.0 to -8.0) |
| first_2_non_progressors_only (1 draw) | 2.0 | 27.7 / 31.1 | A12 memory + certificate | 18.0 | 30.5 | -9.7 [-13.7, -6.0] | -0.6 [-1.6, +0.2] | -13.4 [-18.4, -8.6] | -0.084 [-0.124, -0.050] | -9.7 (-9.7 to -9.7) |
| first_2_non_progressors_only (1 draw) | 2.0 | 27.7 / 31.1 | final (A12 + check, cn90 bar) | 15.1 | 30.5 | -12.6 [-17.2, -8.3] | -0.6 [-1.6, +0.2] | -16.3 [-21.5, -11.2] | -0.135 [-0.197, -0.086] | -12.6 (-12.6 to -12.6) |
| first_2_non_progressors_only (1 draw) | 2.0 | 27.7 / 31.1 | P1 H&E alone 90% | 31.4 | 31.1 | +3.7 [+0.4, +7.1] | +0.0 [-1.9, +1.5] |  | +0.041 [+0.002, +0.083] | 3.7 (3.7 to 3.7) |
| first_3_non_progressors_only (1 draw) | 2.93 | 29.4 / 31.1 | A1 memory | 21.4 | 30.7 | -8.0 [-11.2, -5.1] | -0.4 [-1.3, +0.4] | -12.1 [-16.3, -7.9] | -0.052 [-0.082, -0.025] | -8.0 (-8.0 to -8.0) |
| first_3_non_progressors_only (1 draw) | 2.93 | 29.4 / 31.1 | A12 memory + certificate | 19.3 | 30.5 | -10.1 [-14.0, -6.7] | -0.6 [-1.6, +0.2] | -14.2 [-18.8, -9.6] | -0.095 [-0.133, -0.063] | -10.1 (-10.1 to -10.1) |
| first_3_non_progressors_only (1 draw) | 2.93 | 29.4 / 31.1 | final (A12 + check, cn90 bar) | 15.7 | 30.5 | -13.7 [-18.3, -9.6] | -0.6 [-1.6, +0.2] | -17.8 [-22.7, -12.9] | -0.146 [-0.200, -0.102] | -13.7 (-13.7 to -13.7) |
| first_3_non_progressors_only (1 draw) | 2.93 | 29.4 / 31.1 | P1 H&E alone 90% | 33.5 | 31.1 | +4.1 [+1.1, +7.3] | +0.0 [-1.9, +1.5] |  | +0.025 [-0.010, +0.058] | 4.1 (4.1 to 4.1) |

**(b) Whole selection rerun on the truncated cohort** (whole nested selection (R49 cut-offs, memory threshold and hyper-parameters, certificate, check bar) rerun with training AND held-out non-progressors truncated; models not refitted).

| Truncation | draws | R49 NP flagged / caught | Rule | NP flagged | caught | Δ NP vs R49 [95% CI] | Δ caught vs R49 |
|---|---|---|---|---|---|---|---|
| first_2_everyone | 1 | 27.5 / 31.1 | A1 memory | 20.6 | 30.7 | -6.9 [-10.3, -3.8] | -0.4 [-1.0, +0.2] |
| first_2_everyone | 1 | 27.5 / 31.1 | A12 memory + certificate | 19.9 | 30.3 | -7.6 [-11.2, -4.4] | -0.8 [-1.9, +0.2] |
| first_2_everyone | 1 | 27.5 / 31.1 | final (A12 + check, cn90 bar) | 16.6 | 29.3 | -10.9 [-15.6, -6.8] | -1.8 [-4.2, +0.0] |
| first_2_everyone | 1 | 27.5 / 31.1 | final, check bar re-chosen in fold | 17.2 | 29.1 | -10.3 [-14.6, -6.5] | -2.0 [-4.3, -0.2] |
| first_3_everyone | 1 | 30.4 / 31.1 | A1 memory | 21.8 | 30.7 | -8.6 [-11.7, -5.6] | -0.4 [-1.3, +0.3] |
| first_3_everyone | 1 | 30.4 / 31.1 | A12 memory + certificate | 19.8 | 30.7 | -10.6 [-14.3, -7.3] | -0.4 [-1.2, +0.2] |
| first_3_everyone | 1 | 30.4 / 31.1 | final (A12 + check, cn90 bar) | 15.9 | 30.5 | -14.5 [-19.0, -10.3] | -0.6 [-1.5, +0.1] |
| first_3_everyone | 1 | 30.4 / 31.1 | final, check bar re-chosen in fold | 15.1 | 30.1 | -15.3 [-19.7, -11.1] | -1.0 [-2.3, +0.0] |
| matched | 20 | 25.9 / 31.1 | A1 memory | 19.6 | 30.7 | -6.2 [-8.2, -4.4] | -0.4 [-1.2, +0.2] |
| matched | 20 | 25.9 / 31.1 | A12 memory + certificate | 18.2 | 30.5 | -7.6 [-9.9, -5.5] | -0.6 [-1.5, +0.1] |
| matched | 20 | 25.9 / 31.1 | final (A12 + check, cn90 bar) | 14.2 | 30.5 | -11.7 [-15.2, -8.6] | -0.6 [-1.5, +0.1] |
| matched | 20 | 25.9 / 31.1 | final, check bar re-chosen in fold | 13.2 | 30.2 | -12.7 [-16.1, -9.6] | -0.9 [-2.0, -0.1] |

### 2. Order shuffled within patient

both = the whole nested selection rerun on shuffled histories (dates kept, scores permuted across a patient's date slots); deploy = rules selected on true order, held-out histories shuffled. Unshuffled: A1 −8.2, A12 −10.3, final −14.6 NP flagged against R49.

| Variant | Rule | NP flagged | caught | Δ NP vs R49 [95% CI] | Δ caught vs R49 [95% CI] | Δ NP vs P1 | Δ NP over draws (2.5–97.5%) |
|---|---|---|---|---|---|---|---|
| both (100 draws) | A1 memory | 24.1 | 30.7 | -7.7 [-9.9, -5.5] | -0.4 [-1.0, +0.1] | -11.9 [-15.5, -8.2] | -7.72 (-10.56 to -5.3) |
| both (100 draws) | A12 memory + certificate | 22.1 | 30.6 | -9.7 [-12.2, -7.2] | -0.5 [-1.1, +0.0] | -13.9 [-17.4, -10.0] | -9.68 (-12.5 to -6.75) |
| both (100 draws) | final (A12 + check, cn90 bar) | 17.0 | 30.6 | -14.8 [-18.6, -11.4] | -0.5 [-1.1, -0.0] | -19.0 [-23.2, -14.5] | -14.79 (-17.95 to -11.74) |
| both (100 draws) | final, check bar re-chosen in fold | 16.4 | 30.2 | -15.4 [-19.0, -12.0] | -0.9 [-1.7, -0.2] | -19.6 [-23.6, -15.3] | -15.38 (-18.61 to -12.59) |
| deploy (100 draws) | A1 memory | 25.0 | 30.9 | -6.8 [-9.1, -4.7] | -0.2 [-0.9, +0.5] | -11.0 [-14.8, -7.2] | -6.84 (-8.96 to -5.3) |
| deploy (100 draws) | A12 memory + certificate | 23.3 | 30.9 | -8.5 [-10.9, -6.1] | -0.2 [-0.8, +0.4] | -12.7 [-16.4, -8.7] | -8.49 (-10.65 to -6.45) |
| deploy (100 draws) | final (A12 + check, cn90 bar) | 18.0 | 30.8 | -13.8 [-17.5, -10.4] | -0.3 [-0.9, +0.4] | -18.0 [-22.4, -13.5] | -13.83 (-16.1 to -11.44) |
| deploy (100 draws) | final, check bar re-chosen in fold | 16.6 | 30.7 | -15.2 [-19.0, -11.6] | -0.4 [-1.1, +0.3] | -19.4 [-23.7, -14.8] | -15.18 (-16.9 to -13.19) |

### 3. Endoscopies close to the event excluded

Caught counted out of all 32 (a progressor with no endoscopy left counts as missed). Rules frozen (thresholds from full training histories).

| Exclusion | progressors with an endoscopy left | R49 | A1 | A12 | final | P1 | grade ID/LGD | Δ final vs R49 | Δ final vs grade | Δ NP vs R49 (symmetric version): A1 / final |
|---|---|---|---|---|---|---|---|---|---|---|
| drop_within_1y_of_event_progressors_only | 30 | 29.1 | 28.9 | 28.6 | 28.6 | 29.0 | 12.0 | -0.5 [-1.5, +0.3] | +16.6 |  |
| drop_within_1y_of_event_and_np_within_1y_of_last | 30 | 29.1 | 28.9 | 28.6 | 28.6 | 29.0 | 12.0 | -0.5 [-1.5, +0.3] | +16.6 | -8.0 [-11.5, -4.7] / -14.3 [-19.1, -9.8] |
| drop_within_2y_of_event_progressors_only | 25 | 24.2 | 24.0 | 23.7 | 23.7 | 24.7 | 10.0 | -0.5 [-1.5, +0.3] | +13.7 |  |
| drop_within_2y_of_event_and_np_within_2y_of_last | 25 | 24.2 | 24.0 | 23.7 | 23.7 | 24.7 | 10.0 | -0.5 [-1.5, +0.3] | +13.7 | -7.6 [-11.3, -4.2] / -13.9 [-19.0, -9.2] |

### 4. One look per patient

| Variant | caught | NP flagged | samples per patient | Δ caught vs A12 [95% CI] | Δ NP vs A12 | Δ caught vs R49 | Δ NP vs R49 |
|---|---|---|---|---|---|---|---|
| fixed_cn90 | 27.9 | 14.4 | 1.825 | -2.6 [-5.7, +0.0] | -7.1 [-11.4, -3.2] | -3.2 [-6.5, -0.7] | -17.4 [-22.2, -13.0] |
| infold_bar | 29.6 | 21.1 | 1.825 | -0.9 [-2.3, +0.0] | -0.4 [-0.8, -0.1] | -1.5 [-3.1, -0.2] | -10.7 [-14.2, -7.3] |
| infold_bar_chosen_multi_look | 26.4 | 13.2 | 1.825 | -4.1 [-7.3, -1.4] | -8.3 [-12.6, -4.4] | -4.7 [-8.1, -1.8] | -18.6 [-23.2, -14.1] |

First endoscopy only (ACE-B-like; only each patient's first pre-event endoscopy is evaluated (memory = that endoscopy alone; ACE-B-like); the certificate cannot act): R49 27.9 caught / 16.7 NP flagged; A12 28.1 / 16.1; A12 + check 26.0 / 11.4 (check vs A12: Δ caught -2.1 [-4.7, +0.0], Δ NP -4.7 [-8.5, -1.7]).

### 5. Check bar sweep

| Bar (share of training progressor endoscopies above it) | caught | NP flagged | Δ NP vs R49 [95% CI] | Δ caught vs R49 [95% CI] | Δ caught vs A12 [95% CI] | Δ NP vs A12 |
|---|---|---|---|---|---|---|
| bar_0.7 | 28.1 | 13.5 | -18.3 [-23.1, -13.6] | -3.0 [-6.1, -0.6] | -2.4 [-5.3, -0.2] | -8.0 [-12.0, -4.5] |
| bar_0.75 | 29.9 | 15.1 | -16.7 [-21.4, -12.0] | -1.2 [-2.6, -0.1] | -0.6 [-1.4, +0.0] | -6.4 [-10.2, -3.0] |
| bar_0.8 | 30.5 | 16.5 | -15.3 [-19.8, -10.9] | -0.6 [-1.6, +0.2] | +0.0 [+0.0, +0.0] | -5.0 [-8.7, -2.0] |
| bar_0.85 | 30.5 | 16.8 | -15.0 [-19.5, -10.6] | -0.6 [-1.6, +0.2] | +0.0 [+0.0, +0.0] | -4.7 [-8.3, -1.9] |
| bar_0.9 | 30.5 | 17.2 | -14.6 [-18.9, -10.3] | -0.6 [-1.6, +0.2] | +0.0 [+0.0, +0.0] | -4.3 [-7.7, -1.7] |
| bar_0.925 | 30.5 | 17.9 | -13.9 [-18.1, -9.6] | -0.6 [-1.6, +0.2] | +0.0 [+0.0, +0.0] | -3.6 [-6.9, -1.2] |
| bar_0.95 | 30.5 | 19.2 | -12.6 [-16.8, -8.5] | -0.6 [-1.6, +0.2] | +0.0 [+0.0, +0.0] | -2.3 [-4.6, -0.6] |
| bar_0.975 | 30.5 | 21.0 | -10.8 [-14.4, -7.3] | -0.6 [-1.6, +0.2] | +0.0 [+0.0, +0.0] | -0.5 [-1.0, -0.1] |
| infold_bar_slack0 (picks: 0.7: 8, 0.75: 23, 0.8: 35, 0.85: 12, 0.9: 3, 0.925: 8, 0.95: 9, 0.975: 2) | 30.4 | 16.4 | -15.4 [-19.8, -11.1] | -0.7 [-1.8, +0.2] | -0.1 [-0.3, +0.0] | -5.1 [-8.6, -2.3] |
| infold_bar_slack1 (picks: 0.7: 25, 0.75: 51, 0.8: 10, 0.85: 8, 0.9: 1, 0.925: 5) | 29.8 | 15.3 | -16.5 [-21.2, -11.8] | -1.3 [-2.7, -0.1] | -0.7 [-1.7, +0.0] | -6.2 [-10.1, -2.9] |

### 6. Missing records

each endoscopy independently missing from later histories (memory and certificate) with probability p; it is still judged on its own score when it happens; deploy = selection on full histories.


**20pct missing**

| Variant | Rule | NP flagged | caught | Δ NP vs R49 [95% CI] | Δ caught vs R49 [95% CI] | Δ NP vs P1 | Δ NP over draws (2.5–97.5%) |
|---|---|---|---|---|---|---|---|
| deploy (100 draws) | A1 memory | 25.0 | 30.8 | -6.8 [-9.5, -4.2] | -0.3 [-1.1, +0.4] | -11.0 [-15.2, -6.8] | -6.81 (-8.0 to -5.35) |
| deploy (100 draws) | A12 memory + certificate | 23.5 | 30.7 | -8.3 [-11.1, -5.5] | -0.4 [-1.2, +0.3] | -12.5 [-16.7, -8.2] | -8.31 (-9.7 to -6.54) |
| deploy (100 draws) | final (A12 + check, cn90 bar) | 19.1 | 30.6 | -12.7 [-16.6, -8.9] | -0.5 [-1.3, +0.3] | -16.9 [-21.7, -12.2] | -12.72 (-14.15 to -11.35) |
| deploy (100 draws) | final, check bar re-chosen in fold | 17.9 | 30.5 | -13.9 [-18.0, -9.9] | -0.6 [-1.5, +0.2] | -18.1 [-22.8, -13.4] | -13.94 (-15.15 to -12.44) |
| both (100 draws) | A1 memory | 24.5 | 30.7 | -7.3 [-9.9, -4.7] | -0.4 [-1.2, +0.1] | -11.5 [-15.5, -7.3] | -7.26 (-9.55 to -5.49) |
| both (100 draws) | A12 memory + certificate | 22.7 | 30.5 | -9.1 [-12.0, -6.3] | -0.6 [-1.4, -0.0] | -13.3 [-17.4, -9.0] | -9.11 (-11.56 to -7.1) |
| both (100 draws) | final (A12 + check, cn90 bar) | 18.5 | 30.4 | -13.3 [-17.2, -9.4] | -0.7 [-1.4, -0.0] | -17.5 [-22.2, -12.7] | -13.25 (-14.9 to -11.5) |
| both (100 draws) | final, check bar re-chosen in fold | 17.6 | 30.1 | -14.2 [-18.1, -10.2] | -1.0 [-2.0, -0.1] | -18.4 [-22.9, -13.7] | -14.15 (-16.4 to -12.09) |

**40pct missing**

| Variant | Rule | NP flagged | caught | Δ NP vs R49 [95% CI] | Δ caught vs R49 [95% CI] | Δ NP vs P1 | Δ NP over draws (2.5–97.5%) |
|---|---|---|---|---|---|---|---|
| deploy (100 draws) | A1 memory | 26.5 | 30.9 | -5.3 [-7.5, -3.2] | -0.2 [-1.0, +0.4] | -9.5 [-13.4, -5.7] | -5.34 (-7.15 to -3.99) |
| deploy (100 draws) | A12 memory + certificate | 25.5 | 30.8 | -6.3 [-8.5, -4.0] | -0.3 [-1.0, +0.3] | -10.5 [-14.4, -6.5] | -6.26 (-8.3 to -4.29) |
| deploy (100 draws) | final (A12 + check, cn90 bar) | 20.9 | 30.8 | -10.9 [-14.7, -7.3] | -0.3 [-1.0, +0.3] | -15.1 [-19.9, -10.5] | -10.91 (-13.0 to -9.15) |
| deploy (100 draws) | final, check bar re-chosen in fold | 19.4 | 30.6 | -12.4 [-16.3, -8.7] | -0.5 [-1.4, +0.2] | -16.6 [-21.2, -11.8] | -12.39 (-13.95 to -10.75) |
| both (100 draws) | A1 memory | 25.5 | 30.6 | -6.3 [-8.5, -4.2] | -0.5 [-1.2, +0.0] | -10.5 [-14.3, -6.7] | -6.32 (-9.2 to -4.4) |
| both (100 draws) | A12 memory + certificate | 24.1 | 30.4 | -7.7 [-10.0, -5.3] | -0.7 [-1.4, -0.1] | -11.9 [-15.7, -7.9] | -7.65 (-10.4 to -5.4) |
| both (100 draws) | final (A12 + check, cn90 bar) | 19.8 | 30.4 | -12.0 [-15.8, -8.4] | -0.7 [-1.5, -0.2] | -16.2 [-20.9, -11.6] | -11.98 (-14.25 to -9.9) |
| both (100 draws) | final, check bar re-chosen in fold | 18.9 | 29.9 | -12.9 [-16.5, -9.3] | -1.2 [-2.3, -0.3] | -17.1 [-21.5, -12.6] | -12.87 (-15.45 to -10.74) |

### 7. Optimism of the search (label permutation)

labels permuted at patient level (free) or within endoscopy-count strata 1/2/3/4/5-6/7+ (strat: keeps the progressors' shorter histories, removes the signal); everything that uses labels is rerun: R49 cut-offs, memory threshold rule, half-life / certificate selection, check bars; models' stored predictions unchanged; excess = change in the share of NP flagged minus change in the share of progressors caught (0 expected when the rule only moves a threshold); best_of_grid_excess = OPTIMISTIC pick on the evaluation patients, among the A1 / A12 candidates x check bars (243 cells), of the lowest excess.

Real labels: R49 31.1 / 31.8; nested A1 memory 30.7 / 23.6; A12 memory + certificate 30.5 / 21.5; final (A12 + check, cn90 bar) 30.5 / 17.2; final, check bar re-chosen in fold 30.4 / 16.4; best of grid (optimistic, 243 cells) {'caught': 30.6, 'np_flagged': 16.8, 'seq_per_patient': 3.945, 'flags_per_np_py': 0.115, 'endo_spec': 0.838, 'endo_sens': 0.672, 'rule': 'A12', 'cand': 15, 'bar': 0.75}; best of grid by excess {'caught': 30.4, 'np_flagged': 16.1, 'seq_per_patient': 3.907, 'flags_per_np_py': 0.108, 'endo_spec': 0.848, 'endo_sens': 0.656, 'rule': 'A12', 'cand': 7, 'bar': 0.75, 'excess': -0.3432}.

| Null | permutations | Rule | null Δ NP vs R49: mean (2.5–97.5%) | null Δ caught mean | null excess Δ share (NP − progressor): mean (2.5–97.5%) | real Δ NP | real excess | share of null at or below real excess |
|---|---|---|---|---|---|---|---|---|
| free | 50 | A1 memory | -2.45 (-5.73 to -0.5) | -2.0 | 0.006 (-0.095 to 0.064) | -8.2 | -0.178 | 0.0 |
| free | 50 | A12 memory + certificate | -3.0 (-7.42 to -0.7) | -2.31 | 0.002 (-0.116 to 0.062) | -10.3 | -0.221 | 0.0 |
| free | 50 | final (A12 + check, cn90 bar) | -3.6 (-8.24 to -0.75) | -2.85 | 0.005 (-0.115 to 0.074) | -14.6 | -0.321 | 0.0 |
| free | 50 | final, check bar re-chosen in fold | -3.63 (-7.98 to -0.92) | -2.87 | 0.005 (-0.123 to 0.083) | -15.4 | -0.336 | 0.0 |
| free | 50 | best_of_grid_excess (OPTIMISTIC) | -4.74 (-10.38 to -0.67) | -2.16 | -0.043 (-0.168 to 0.032) | -15.7 | -0.343 | 0.0 |
| strat | 50 | A1 memory | -4.0 (-5.88 to -1.37) | -1.77 | -0.038 (-0.105 to 0.014) | -8.2 | -0.178 | 0.0 |
| strat | 50 | A12 memory + certificate | -4.93 (-7.69 to -2.05) | -2.06 | -0.05 (-0.14 to 0.018) | -10.3 | -0.221 | 0.0 |
| strat | 50 | final (A12 + check, cn90 bar) | -6.65 (-10.43 to -4.17) | -2.89 | -0.064 (-0.164 to 0.017) | -14.6 | -0.321 | 0.0 |
| strat | 50 | final, check bar re-chosen in fold | -6.08 (-9.55 to -3.47) | -2.67 | -0.058 (-0.155 to 0.022) | -15.4 | -0.336 | 0.0 |
| strat | 50 | best_of_grid_excess (OPTIMISTIC) | -8.95 (-13.53 to -4.12) | -2.65 | -0.125 (-0.238 to -0.035) | -15.7 | -0.343 | 0.0 |

### 8. Batch and scanner

consecutive pre-event endoscopies within patient; |change| of the repeat-mean logit max L-IMG and of the median R49-aligned gate score (0 = flag boundary); flip = gate flag differs; endoscopy scanner / sequencing batch = commonest over its samples; OLS with patient-clustered SEs; ICC(1) on repeat-mean scores, adjusted = residuals on scanner (and batch) fixed effects.

| Class | pairs | pairs with scanner change | with batch change | |Δ H&E logit|: scanner change coef [CI] | batch change coef | |Δ gate score|: scanner coef | flip: scanner coef | flip: batch coef | mean flip rate no change / change |
|---|---|---|---|---|---|---|---|---|---|
| non_progressor | 157 | 24 | 11 | +0.90 [+0.01, +1.80] | +0.55 [-0.32, +1.42] | +0.30 [-0.70, +1.30] | +0.16 [-0.03, +0.34] | +0.40 [+0.07, +0.74] | 0.414 / 0.583 |
| progressor | 56 | 11 | 8 | +0.13 [-0.72, +0.99] | -0.78 [-1.23, -0.32] | -0.31 [-0.96, +0.35] | +0.06 [-0.20, +0.31] | -0.06 [-0.31, +0.18] | 0.178 / 0.182 |

ICC(1) of repeat-mean endoscopy scores: non_progressor logit max L-IMG: 0.214 unadjusted, 0.216 scanner-adjusted, 0.121 scanner+batch-adjusted; non_progressor R49-aligned gate score: 0.315 unadjusted, 0.311 scanner-adjusted, 0.204 scanner+batch-adjusted; progressor logit max L-IMG: 0.624 unadjusted, 0.621 scanner-adjusted, 0.532 scanner+batch-adjusted; progressor R49-aligned gate score: 0.646 unadjusted, 0.647 scanner-adjusted, 0.588 scanner+batch-adjusted.

- **all_endoscopies_one_scanner** (28 NP, 26 P): A1 vs R49 Δ NP -4.8 [-7.1, -2.7]; final vs R49 Δ NP -7.9 [-11.3, -4.9].
- **scanner_changes_within_patient** (15 NP, 6 P): A1 vs R49 Δ NP -3.4 [-6.0, -1.2]; final vs R49 Δ NP -6.7 [-9.8, -3.7].


### Implementation notes

- **Code reused.** `ex_e7_stress.py` executes the E2 module body (`ex_e2_veto.py`, up to its dispatch: `build`, `vs_test`, `vs_train`, round-8 helpers) and the rv9 module body (`rv9_falseflags.py`: `statics`, `memory`, `cert_flags`, `make_ctx`, `pat_scores`, `thr_for`, family builders `A1:gate_al:ew` and `A12`). The rv9 engine loop is re-implemented for criterion "np" only so that it returns the chosen candidate's training-patient flags and can score held-out patients on a different history matrix. Reproduction: 0 flag and 0 sequencing mismatches against `grp_A1ga.npz` / `grp_A12.npz` over all 288 × 10 endoscopy-repeats; final rule 30.5 / 17.2 / 3.816 as `story_aggs_v2.py`.
- **Check.** ps_oac of the top two H&E samples (E2 `vs_test`/`vs_train`, k = 2); bar = `thr_sens` at share q of the fold's training progressor endoscopies (q = 0.90 is E2's cn90). Sequencing: k top samples at every memory flag (k − 1 in R49's middle band), as E2 `mem`.
- **In-fold bar.** Per outer fold, among q ∈ {70, 75, 80, 85, 90, 92.5, 95, 97.5%} and "no check", the bar with the fewest training non-progressor patients flagged by A12 + check, subject to training progressor-patient detection ≥ A12's own training detection (slack 0; slack 1 also shown); ties to the higher q. Training flags are A12's training-patient flags from inner out-of-fold predictions (resubstitution of the memory threshold, as in rv9).
- **Test 1.** (a) Frozen: memory scores at a kept endoscopy depend only on earlier endoscopies, so the stored rules are evaluated with later endoscopies masked (`patient_arrays(em=keep)`). m per non-progressor ~ the empirical distribution of the 32 progressors' pre-event endoscopy counts, capped at the patient's own count (200 draws, `RandomState(7001)`); draws are averaged as fractional patient outcomes before the bootstrap. Flags per NP patient-year use the follow-up from the first endoscopy to the first dropped endoscopy. (b) Rerun: removed endoscopies are deleted from the history matrices, the patient incidence matrix and the training-endoscopy masks; R49 cut-offs are re-derived on the remaining training samples (`tb_common.triage` with the reduced population mask); the check bar uses the remaining training progressor endoscopies; 20 matched draws. Models are not refitted.
- **Test 2.** Within each patient the endoscopy scores are permuted across the patient's date slots (dates, and so the EW weights and certificate windows, kept); 100 draws (`RandomState(7100 + d)`). "both" re-runs the selection on shuffled histories; "deploy" selects on true order and scores held-out patients on shuffled ones.
- **Test 3.** Frozen rules; progressor endoscopies with years-to-event < 1 (or 2) removed; caught counted out of 32. Symmetric version also removes non-progressor endoscopies within 1 (2) years of the last sequenced endoscopy. Grade = any ID/LGD sample at an evaluated endoscopy (round-8 P10).
- **Test 4.** One look: at each patient's first A12-flagged endoscopy (time order) the check is applied; if it cancels, the patient is never flagged afterwards. Sequencing counted up to that endoscopy. First endoscopy only: every patient evaluated at the first pre-event endoscopy alone.
- **Test 6.** Each endoscopy is missing from all later histories with probability p (EW weights to it set to 0 for later endoscopies; its certificate never issued); it is still judged on its own score. 100 draws per p.
- **Test 7.** 50 free permutations of the 75 patient labels and 50 within endoscopy-count strata (1, 2, 3, 4, 5–6, ≥ 7). Every label-using step is re-run: R49 cut-offs (`tb_common.triage` with permuted sample labels), the memory threshold rule, half-life and certificate selection, the check bars and the in-fold bar. Stored predictions (trained on the true labels) are unchanged, so the null keeps their structure but removes their link to the permuted labels. Because the null rules lose detection, the comparison statistic is the excess Δ share NP flagged − Δ share progressors caught (0 for a pure threshold move).
- **Test 8.** Endoscopy scanner = commonest `slide_desc.csv` scanner over its samples (8 endoscopies have mixed-scanner samples); sequencing batch from E2 `features.csv`. Sequencing batch is largely patient-level, so the scanner-and-batch-adjusted ICC falls in both classes; it does not isolate within-patient technical noise.
- **Not done.** No refit of the H&E / copy-number models under truncation or permutation (stored predictions throughout). The "last m endoscopies" exposure variant and the null-arm control for the check (random non-OAC arms) were not run.

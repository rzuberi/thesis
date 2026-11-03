# Two papers, agent UNC: is ensemble disagreement a sequencing signal?

3 November 2026. Rules: `paper/two_papers/RUN_RULES.md`. Quick signal test (about 45 min), no model trained. Question: does disagreement between the 10 held-out H&E predictions of each endoscopy (one per repeat of the 10 × 10 patient-grouped CV) tell us whom to sequence, beyond the H&E score itself?

## Plan

- **Inputs (read-only).** ART's clean-tile L-IMG refit (`killcoyne_mm/two_papers_ART/refit/clean`), the stored L-CNV, and L-LATE = (L-CNV + clean L-IMG) / 2. Population: 571 pre-event samples, 288 endoscopies, 75 patients (32 progressors).
- **State.** `tp_art_gate.py` is executed for its definitions only, with its `state_v("ml", "clean")`: the endoscopy score is the mean sample logit, and the R49 mean-logit gate cut-offs (t_low, c\*, t_seq) are re-derived in each outer fold on training patients (inner out-of-fold predictions).
- **Definitions.**
  - D = SD of the 10 held-out log-odds. At endoscopy level this is the mean sample logit; at sample level, the sample's own logit.
  - Cut-off = each fold's training 90%-sensitivity cut-off (training endoscopies or training pre-event samples). I used this rather than the band edges because it is a single cut. Outside the middle band it gives the same call as the band in all 2,880 endoscopy × repeat cells.
  - M = |held-out log-odds − that cut-off|.
  - Entropy = binary entropy of the mean held-out probability.
  - H&E error = a non-progressor at or above the cut-off, or a progressor below it.
  - Confident = outside the R49 mean-logit gate's middle band.
  - Top-quartile D = D at or above the 75th percentile of the fold's training endoscopies. D uses no labels.
  - A copy-number or combined "fix" = that score's own endoscopy mean logit lands on the correct side of its own training 90%-sensitivity cut-off.
- **Units and uncertainty.** Units are endoscopy (or sample) × repeat. Metrics are computed per repeat and then averaged over the 10 repeats. Intervals come from a patient bootstrap: 2,000 draws, rv8 `pdraws` construction, RandomState(0), with each drawn patient's rows resampled together.
- **Fitted models.** Logistic models for error are unpenalised and fitted on rows stacked over repeats. p-values are cluster-robust Wald tests with patients as clusters. The naive likelihood-ratio p is also stored, but it ignores clustering. Held-out AUROC uses 5-fold patient-grouped CV.
- **Added beyond the brief.** The brief controls for the score only through M. I added a flexible control for the score: a piecewise quadratic in (log-odds − cut-off), fitted separately on each side, plus entropy. I also ran D on the probability scale (SD of the 10 probabilities) as a sensitivity analysis.
- **Files.** Script `scripts/paper_plan/tp_unc_main.py`. Aggregates in `results/paper_final/two_papers_UNC/unc.json`. One epyc job (Slurm prefix `tpunc`). Row-level arrays stayed in memory on the cluster, and nothing row-level was written.

## Results

**No signal. D's apparent association with H&E errors comes entirely from the score level. Once the score itself is controlled for, D adds nothing at either level or on either scale (held-out AUROC gain −0.001 to +0.001). On the logit scale, the "confident but disagreeing" endoscopies are wrong less often than the other confident ones (9.3% vs 25.6%). Choosing whom to sequence by D, at the gate's budget, flags 17.8 more non-progressor endoscopies.**

### Smoke

With the clean L-IMG, the engine reproduces ART's `gate.json` R49 mean-logit gate: 31.1 caught / 32.3 non-progressors flagged / 1.701 samples per patient (`unc.json` → `smoke_R49_mean_logit_gate_clean`). The run asserts this before any analysis.

### 1–3. Disagreement, distance to the cut-off, and errors (logit-scale D)

Endoscopy-level D: median 0.77 log-odds (IQR 0.56–1.10). M: median 1.55 (IQR 0.71–2.70). Errors at the 90%-sensitivity cut-off: 36.0% of endoscopy × repeat cells [28.9, 43.1] and 43.9% of sample × repeat cells [36.9, 50.1]. Most are non-progressors above the cut.

| | Endoscopy | Sample |
|---|---|---|
| Spearman D vs M | **+0.47 [0.35, 0.58]** | +0.33 [0.23, 0.42] |
| Spearman D vs entropy | −0.55 [−0.64, −0.43] | −0.54 [−0.61, −0.45] |
| AUROC of D for an H&E error | **0.33 [0.27, 0.41]** (inverse: high D = fewer errors) | 0.31 [0.26, 0.37] |
| AUROC of closeness to the cut-off (−M) for an error | 0.63 [0.58, 0.69] | 0.62 [0.57, 0.67] |
| AUROC of entropy for an error | 0.77 [0.68, 0.84] | 0.75 [0.67, 0.81] |
| Error ~ M vs M + D: held-out AUROC | 0.613 → 0.654, gain +0.040 [−0.007, +0.117] | 0.609 → 0.685, +0.076 [+0.017, +0.136] |
| Same, apparent (optimistic) | +0.045 [+0.004, +0.113] | +0.073 [+0.025, +0.136] |
| D coefficient given M (per SD) | −0.47 [−0.89, −0.12], cluster Wald p = 0.019 | −0.62 [−0.94, −0.32], p < 0.001 |
| Error ~ flexible score vs + D: held-out AUROC | 0.817 → 0.817, **gain −0.001 [−0.006, +0.006]** | 0.835 → 0.836, **+0.001 [−0.004, +0.007]** |
| D coefficient given the flexible score | +0.13 [−0.26, +0.42], p = 0.40 | −0.09 [−0.43, +0.21], p = 0.58 |

- On the log-odds scale, D is not a "near the cut-off" signal. It is larger for endoscopies far from the cut-off (Spearman +0.47), because the 10 models spread more at extreme log-odds.
- D's "gain" over M is therefore in the wrong direction (high D means fewer errors). It is a stand-in for how far the score sits from the cut-off, which M (a symmetric V) does not capture. With a flexible function of the score, the gain is zero.
- Probability scale (sensitivity; `unc.json` → `sensitivity_D_probability_scale`). D now points the expected way: AUROC for an error is 0.71 [0.63, 0.78] at endoscopy level and 0.70 [0.63, 0.77] at sample level. But it is mostly entropy (Spearman +0.84 and +0.89). Given the flexible score, the gain is −0.002 [−0.012, +0.015] at endoscopy level (p = 0.79) and 0.000 [−0.008, +0.013] at sample level (p = 0.60).

### 4. Confident but disagreeing (endoscopy level; repeat-mean counts per 288 endoscopies)

| Group | Endoscopies | H&E call wrong | Wrong rate | Copy number fixes a wrong call | L-LATE fixes a wrong call | Copy number flips a correct call |
|---|---|---|---|---|---|---|
| Confident, top-quartile D | 57.0 [41.9, 73.7] | 5.3 [1.8, 9.6] | **9.3% [3.3, 17.1]** | <5 | <5 | 15.7 [9.3, 23.1] |
| Confident, bottom 75% D | 103.4 [85.2, 122.1] | 26.5 [17.2, 36.8] | **25.6% [17.7, 35.0]** | 11.6 [6.3, 17.8] | <5 | 27.1 [18.5, 36.7] |

- Difference in wrong rate (top-D − rest): −16.3 points [−25.6, −6.7]. Confident endoscopies with high logit-scale disagreement are *more* often right.
- Net effect of letting copy number decide, per 100 endoscopies (fixes − flips): −23.0 [−35.1, −11.4] in top-D and −15.0 [−26.8, −3.8] in the rest. L-LATE: −9.6 [−19.2, −2.3] and −2.4 [−8.7, +2.3].
- Probability-scale D, for comparison: confident top-D endoscopies are wrong 39.6% [25.0, 56.0] of the time, against 13.6% [7.3, 21.5]. Copy-number net there is +8.1 per 100 [−1.9, +19.6]. These are the high-band endoscopies with only moderate probabilities, so the same score-level effect explains the difference (section 1–3, flexible control).

### 5. Equal budget (endoscopy level, not the full patient pathway)

Same number of endoscopies sequenced per repeat as the R49 middle band: 127.6 [105.3, 150.7]. Sequenced endoscopies are called by top-sample L-LATE ≥ t_seq (R49's rule); the others by H&E at the 90%-sensitivity cut-off. Counts are repeat means.

| Selection | Overlap with the band | NP endoscopies corrected | Progressor endoscopies lost | Progressor endoscopies rescued | NP endoscopies newly flagged | NP endoscopies flagged, final | Progressor endoscopies flagged, final |
|---|---|---|---|---|---|---|---|
| Middle band (R49) | 127.6 | 23.6 [15.2, 32.4] | <5 | <5 | 12.9 [8.1, 18.6] | 84.8 [60.7, 110.8] | 79.7 [53.8, 108.7] |
| Highest D (logit) | 35.6 [21.9, 53.0] | 8.2 [3.9, 14.0] | <5 | <5 | 15.3 [6.7, 25.5] | 102.6 [73.3, 134.1] | 81.4 [55.0, 111.9] |
| Highest D (probability, sensitivity) | 69.0 [51.8, 87.2] | 14.2 [7.2, 22.0] | <5 | <5 | <5 | 85.3 [61.7, 111.1] | 79.3 [53.8, 108.0] |

- D (logit) − band: **+17.8 [+8.9, +27.0] non-progressor endoscopies flagged**, +1.7 [−1.3, +5.2] progressor endoscopies flagged.
- D (probability) − band: +0.5 [−4.7, +5.9] and −0.4 [−2.0, +0.7]. This is no better than the band, and it picks 59 of the same 128 endoscopies.

### Verdict

No signal worth a full analysis. Ensemble disagreement of the 10 CV models re-expresses the H&E score level. Logit-scale SD grows with distance from the cut-off, and probability-scale SD tracks entropy. With the score modelled flexibly, it carries no extra information about H&E errors. At equal budget it does not beat the middle band. The gate's middle band already holds the uncertainty that matters for choosing whom to sequence.

What this does *not* test (not checked):
- disagreement between genuinely different models, such as different foundation models or tile subsets;
- tile-level spread within a slide;
- whether D predicts errors of the copy-number score.

The 10 CV repeats share the recipe and the features, and any two of them train on about 90% of the same patients (my inference from 9-of-10-fold training sets), so they may simply be too alike to disagree informatively.

### Implementation notes

- `tp_unc_main.py` executes `tp_art_gate.py` with a TASK other than `gate`, which gives definitions only. It then calls `state_v("ml", "clean")` and `make_ctx` per (repeat, fold), and `read_refit("clean")` for the sample-level model. No rule is re-implemented. The R49 band, flag and t_seq come from the engine.
- Copy-number and L-LATE endoscopy scores are the mean sample logit of each fold's inner out-of-fold (training) or held-out predictions, the same construction as E3's `mlogit`.
- Bootstrap patients get distinct cluster ids, so duplicated patients stay in the same CV fold.
- Repeat-mean counts < 5 are shown as "<5" (in the JSON too).
- Runtime: one epyc job (2 CPUs) of 417–603 s for 2,000 draws; about 28 min wall time for the whole test (19:13–19:41), including three 5–10-draw smokes and a rerun that only masked small cells (all other values identical).

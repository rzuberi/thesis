# Exploration E5: borrowing knowledge from ERIN

Started 20 October 2026 (exploration, not confirmatory; rules in `paper/reviews_round7/decisions/EXPLORE_RULES.md`).

## Plan (written before any result)

**Idea.** ERIN is a separate archive of about 7,900 routine oesophageal H&E slides (2022–2025) with section-level dysplasia grades from an LLM jury. A dysplasia model trained there knows what dysplasia looks like from far more slides than our cohort has. Its "dysplasia-likeness" score on our slides may help separate progressors from non-progressors, or tell which H&E flags are real.

**Prior evidence.**
- ISBI rerun, part 3: the ERIN arm-B LGD+ models scored SWG LGD-versus-NDBE at only 0.57.
- P32: an ERIN report-label grade head predicted SWG progression at 0.75 at patient level on the release cohort.
- So transfer is uncertain.

**Steps.**
1. **ERIN models.** Arm B of the ISBI rerun (own-section jury-v3 grade, ABMIL on UNI2-h tiles at 0.5 µm/px, GPU-resident, `train_fold.py` settings).
   - Retrained with every slide of the 70 ERIN patients also in the SWG cohort removed: the 55-ID list, the ISBI part-3 accession and Barrett's-DB bridges, and the closeout pairs file.
   - Tasks: LGD+ (primary), HGD+ and six-class.
   - 5 ERIN patient folds × 3 seeds; the 130 hand-labelled patients are never trained on (validation).
   - The existing leak-free P32 report-label grade head is scored alongside.
2. **Scoring our cohort.**
   - 460 of the 578 pre-event slides already have UNI2-h features from the same pipeline (`SWGCohort/features_uni2h_05um`; Hamamatsu level 1, 0.44 µm/px).
   - The other 118 are extracted with the same tiling in two phases: CPU tile crops, then GPU embedding.
   - Slide score = mean over models of the logit; sample score = max over its slides; endoscopy score = max over its samples.
3. **Uses**, all nested in the stored 10 × 10 patient-grouped folds (`killcoyne_mm`). ERIN models never see SWG labels, so only thresholds and stackers need nesting.
   - **(a) Alone:**
     - AUROC (sample-level fold-stratified, endoscopy and patient max);
     - P1-like rule "flag if max ERIN score ≥ t", with t at 80/90/95% training endoscopy sensitivity.
   - **(b) Stacked with L-IMG:**
     - per outer fold, a logistic regression of y on logit inner-OOF L-IMG and the ERIN logit, fitted on training patients' pre-event samples;
     - training-patient scores for thresholds are cross-fitted (5 patient-grouped folds inside training patients);
     - used (i) P1-style at 80/90/95%, (ii) in the R49 gate in place of L-IMG for banding (L-LATE unchanged), (iii) also in L-LATE = (L-CNV + stack) / 2.
   - **(c) Veto or confirmation inside R49:**
     - τ_q = the threshold keeping ≥ q of training progressor endoscopies' max ERIN score (q = 90/95/98%; **primary q = 95%**, fixed now);
     - c1: every R49 flag requires ERIN ≥ τ;
     - c2: only high-band (H&E-only) flags require it;
     - c3: high-band flags below τ are sent to the middle band (sequenced, CNV decides) instead of being dropped;
     - c4: low-band endoscopies whose ERIN score exceeds the 90%-specificity training cut-off are rescued into the middle band;
     - c5: P1 at 90% with the veto.
4. **Reporting.**
   - Against R49 and P1 at 90% on the same 571 samples / 75 patients: Δ NP patients flagged, Δ caught, Δ endoscopy specificity (matched where the rule is score-based), samples sequenced and AUROC.
   - Paired patient bootstrap, 2,000 draws, `RandomState(0)`.
   - Apparent (non-nested) versions are labelled optimistic.

**Primary per use:**
- (a) ERIN LGD+ max at 90%;
- (b) stack(L-IMG, ERIN LGD+) in P1 at 90%;
- (c) c1 at q = 95%.

Everything else is descriptive.

Scripts: `scripts/paper_plan/ex_e5_{prep,tiles,embed,train,score,eval}.py`, `ex_e5_gpu_submit.sh`. Slurm prefix `exe5`. Row-level outputs: `killcoyne_mm/explore_E5/` (cluster). Aggregates: `results/paper_final/explore_E5/`.

---

## Results

Run 20 October 2026. Scripts: `scripts/paper_plan/ex_e5_*.py`. Aggregates: `results/paper_final/explore_E5/` (`e5_auc`, `e5_a`, `e5_b`, `e5_c`, `e5_mem`, `e5_erin_validation`, `e5_prep_info`). Tables: `ex_e5_render.py`. Figure (local only): `paper/figures_explore_E5/e5_forest.png`.

All comparisons use the same 571 pre-event samples, 288 endoscopies and 75 patients (32 progressors). R49 and P1 at 90% reproduce round 8: 31.1 caught / 31.8 NP flagged, and 31.1 / 36.0. Intervals come from a paired patient bootstrap (2,000 draws, `RandomState(0)`). "Nested" means every threshold, stacker and half-life was chosen on the outer fold's training patients only.

### What was built

- **ERIN models.**
  - Arm-B ABMIL (`train_fold.py` settings): LGD+, HGD+ and six-class; 5 ERIN patient folds × 3 seeds, so 45 models.
  - Excluded: every slide of the 70 listed SWG-overlap ERIN patients. 42 of them have oesophageal slides in the ISBI table, 166 slides in all.
  - 7,599 slides remained.
  - Validation is unchanged from the ISBI rerun.
    - LGD+: held-out fold T1 0.949, human-labelled holdout T2 0.894.
    - HGD+: T1 0.961, T2 0.939.
  - Also scored: the existing leak-free P32 report-label grade head ("P32 head", 5 fold models).
- **Our slides.**
  - 460 of the 578 pre-event slides already had UNI2-h features from the ERIN pipeline.
  - The other 118 were extracted in two phases: 30 CPU tile-crop jobs, then 4 GPU embedding jobs. No slide was read in a GPU job.
  - All 578 slides were scored at 0.44 µm/px, with a median of about 1,060 tiles per slide.
- **Transfer check against our recorded grade** (no SWG label used in training):
  - ERIN LGD+ separates LGD from NDBE samples at 0.76, and ID/LGD from NDBE at 0.70;
  - six-class P(LGD) does so at 0.79;
  - Spearman correlation with L-IMG is 0.41.
  - This is far better than the ISBI part-3 transfer (0.57). The likely reasons are full-tile 0.44 µm features and this cohort's grades; the cause was not tested.

### AUROC for progression (ERIN score alone, no SWG training)

| Score | Sample AUROC (fold-stratified) [95% CI] | Δ vs L-IMG | Endoscopy max | Patient max | Δ patient vs L-IMG |
|---|---|---|---|---|---|
| L-IMG (reference) | 0.847 [0.798, 0.894] | – | 0.824 | 0.831 | – |
| ERIN LGD+ (primary) | 0.758 [0.686, 0.827] | −0.089 [−0.148, −0.033] | 0.788 | 0.781 | −0.050 [−0.156, +0.046] |
| ERIN six-class LGD+ | 0.744 | −0.103 | 0.765 | 0.742 | −0.089 |
| ERIN six-class P(LGD) | 0.748 | −0.099 | 0.772 | 0.717 | −0.114 |
| P32 report-label head | 0.700 | −0.147 | 0.733 | 0.749 | −0.081 |
| ERIN HGD+ | 0.661 | −0.185 | 0.678 | 0.698 | −0.132 |
| ERIN top-16 tile logit | 0.716 | −0.131 | 0.721 | 0.645 | −0.186 |

A model that never saw a SWG progression label ranks progressor patients at 0.78. That is close to, but below, our own H&E model. The LGD-type scores carry the signal; the HGD+ score is weaker, because ERIN's positives are mostly HGD or cancer.

### Ranked results (nested unless marked; Δ = rule − comparator, 95% CI)

Ranked by Δ NP patients flagged against R49, among rules with Δ caught ≥ −0.5 first.

| # | Rule | Caught / 32 | NP flagged / 43 | Δ NP flagged vs R49 | Δ caught vs R49 | Δ NP flagged vs P1 90% | Δ caught vs P1 90% | Endo sens / spec | Seq / patient |
|---|---|---|---|---|---|---|---|---|---|
| 1 | (m) round-9 EW memory + P32-head veto (q95) | 30.6 | 22.9 | **−8.9** [−12.3, −5.6] | −0.5 [−1.6, +0.3] | −13.1 [−17.8, −8.3] | −0.5 [−2.1, +1.3] | 0.866 / 0.696 | 1.94 |
| – | (m) round-9 EW memory alone (reference, reproduced) | 30.7 | 23.6 | −8.2 [−11.4, −5.1] | −0.4 [−1.3, +0.4] | −12.4 [−16.9, −7.9] | −0.4 [−1.9, +1.4] | 0.905 / 0.656 | 1.94 |
| 2 | (m) EW memory over stack(gate score, P32 head) | 31.0 | 25.7 | −6.1 [−9.6, −2.9] | −0.1 [−1.5, +1.5] | −10.3 [−14.7, −6.0] | −0.1 [−1.8, +1.9] | 0.889 / 0.618 | 1.94 |
| 3 | (c1) R49, flags need P32 head ≥ τ95 | 30.8 | 29.3 | −2.5 [−5.2, −0.4] | −0.3 [−1.0, +0.0] | −6.7 [−10.6, −3.0] | −0.3 [−2.0, +1.6] | 0.858 / 0.629 | 1.94 |
| 4 | (c2) R49, high-band flags need ERIN LGD+ ≥ τ90 | 30.8 | 30.2 | −1.6 [−3.3, −0.3] | −0.3 [−0.8, +0.0] | −5.8 [−9.2, −2.5] | −0.3 [−1.9, +1.5] | 0.889 / 0.624 | 1.94 |
| 5 | (b)(iii) R49 with stack(L-IMG, ERIN HGD+) for banding and L-LATE | 31.2 | 30.8 | −1.0 [−2.7, +0.8] | +0.1 [+0.0, +0.3] | −5.2 [−9.2, −1.0] | +0.1 [−1.3, +1.9] | 0.915 / 0.554 | 2.16 |
| 6 | (b)(iii) the same with ERIN LGD+ | 31.2 | 31.2 | −0.6 [−3.2, +1.9] | +0.1 [+0.0, +0.3] | −4.8 [−9.2, −0.2] | +0.1 [−1.4, +2.0] | 0.927 / 0.526 | 2.11 |
| 7 | (c3) weak-ERIN high-band flags sequenced instead | 31.1 | 31.8 | 0.0 | 0.0 | −4.2 [−7.4, −1.2] | 0.0 [−1.5, +1.9] | 0.907 / 0.560 | 1.99 |
| 8 | (c4) strong-ERIN low-band endoscopies sequenced | 31.2 | 31.8 | 0.0 | +0.1 [+0.0, +0.3] | −4.2 [−7.4, −1.2] | +0.1 [−1.4, +2.0] | 0.924 / 0.555 | 1.99 |
| 9 | (b)(ii) R49 banded by stack(L-IMG, ERIN LGD+) | 31.1 | 32.7 | +0.9 [+0.3, +1.6] | 0.0 [−0.3, +0.3] | −3.3 [−6.5, −0.1] | 0.0 [−1.7, +1.9] | 0.926 / 0.520 | 2.11 |
| 10 | **(c) primary**: c1, R49 flags need ERIN LGD+ ≥ τ95 | 30.1 | 30.5 | −1.3 [−2.7, −0.2] | −1.0 [−3.4, +0.0] | −5.5 [−8.9, −2.3] | −1.0 [−3.8, +1.4] | 0.868 / 0.608 | 1.94 |
| 11 | (m) EW memory + ERIN LGD+ veto (q95) | 30.0 | 23.7 | −8.1 [−11.1, −5.2] | −1.1 [−3.5, +0.2] | −12.3 [−16.5, −8.1] | −1.1 [−3.8, +1.2] | 0.877 / 0.672 | 1.94 |
| 12 | (c1) ERIN LGD+ ≥ τ90 | 29.3 | 26.3 | −5.5 [−9.3, −2.4] | −1.8 [−4.6, +0.0] | −9.7 [−14.4, −5.4] | −1.8 [−5.0, +1.0] | 0.824 / 0.742 | 1.94 |
| 13 | **(b) primary**: stack(L-IMG, ERIN LGD+), P1-style 90% | 30.2 | 35.1 | +3.3 [−0.7, +7.2] | −0.9 [−3.3, +0.8] | −0.9 [−3.8, +1.8] | −0.9 [−2.2, +0.0] | 0.899 / 0.497 | 0 |
| 14 | **(a) primary**: ERIN LGD+ alone, 90% | 30.2 | 39.1 | +7.3 [+0.9, +13.5] | −0.9 [−3.9, +1.5] | +3.1 [−2.6, +9.1] | −0.9 [−4.1, +1.7] | 0.890 / 0.424 | 0 |
| 15 | (m) EW memory over ERIN LGD+ alone | 30.6 | 40.8 | +9.0 [+4.1, +14.4] | −0.5 [−3.2, +1.7] | +4.8 [+0.5, +10.0] | −0.5 [−3.3, +1.9] | 0.940 / 0.164 | 0 |

**Against the memory rule itself** (paired):
- adding the P32-head veto: Δ NP flagged −0.7 [−2.6, +0.4], Δ caught −0.1 [−0.3, 0.0];
- adding the ERIN LGD+ veto: Δ NP +0.1 [−1.1, +1.3], Δ caught −0.7 [−2.4, +0.2]. 33 of 100 folds could not keep R49's training detection with this veto.

**Specificity at matched sensitivity.**
- Against P1 matched to each rule's own endoscopy sensitivity:
  - c1 P32 head: +0.033 [−0.075, +0.152];
  - memory + P32 veto: +0.136 [+0.004, +0.232];
  - memory alone: +0.158 [+0.069, +0.252].
- Score rules matched to R49's sensitivity, specificity minus R49's:
  - ERIN LGD+ alone −0.177;
  - stack(L-IMG, ERIN LGD+) −0.066;
  - stack with the P32 head −0.060.
  - No score rule reaches R49's specificity.

**Apparent (optimistic) versions** (stacker or threshold fitted on all patients) were close to the nested ones:
- ERIN LGD+ 90%: 31.0 / 39.0;
- stack(L-IMG, ERIN LGD+) 90%: 31.1 / 35.1;
- c1 q95: 30.1 / 30.9.

**Stacker.**
- The ERIN LGD+ coefficient was positive in 100 of 100 folds: standardised 0.84 (range 0.71–0.98), against 1.20 for L-IMG.
- The stacked score's sample AUROC was 0.853, against 0.847 for L-IMG.
- The 6-score ERIN profile stack was no better (0.850).

**What the veto touches** (c1 q95, per repeat): of 168 R49-flagged endoscopies, it removes 9.6 non-progressor and 3.4 progressor endoscopies.

### Reading

1. **ERIN transfers.**
   - A dysplasia model trained only on ERIN predicts progression in our cohort: patient AUROC 0.78 for LGD+ and 0.75 for the P32 head.
   - It also agrees with our recorded grade (LGD vs NDBE 0.76).
   - It is positively weighted in every stacking fold.
2. **But it is largely redundant with L-IMG.**
   - The stack moves AUROC by +0.006.
   - No stacked or score rule beats P1 or R49 on false flags at the same detection.
3. **As a veto on R49**, ERIN removes some non-progressor flags, but at about the same rate as it removes progressor endoscopies.
   - The primary c1 (q95) trades −1.3 NP flagged for −1.0 caught.
   - Only the P32 head at q95 stays within half a progressor: −2.5 [−5.2, −0.4] NP, −0.3 caught. It is descriptive, one of about 14 veto variants.
4. **Sequencing-based uses change nothing.** Sending weak-ERIN high-band flags to sequencing (c3) or rescuing strong-ERIN low-band endoscopies (c4) leaves patient outcomes unchanged: copy number confirms every re-routed high-band endoscopy, and the rescued ones were already caught elsewhere.
5. **Inside the round-9 EW memory rule**, the P32-head veto lowers NP flagged from 23.6 to 22.9, with an interval spanning zero. Memory over a gate-plus-ERIN stack is worse than memory over the gate alone (25.7).
6. **Caveats.**
   - About 70 rule variants were tried on 75 patients; the headline rows are search winners.
   - The P32 head was trained on ERIN case-level report labels and saw the 0.5 µm SWG bags only at inference.
   - SWG slides are Hamamatsu at 0.44 µm/px, ERIN's are 0.5 µm/px.

### Implementation notes

- **ERIN overlap exclusion.** The union of four sources:
  - the 55-ID file;
  - accession bridges from the release, sheet and slide_matching accessions;
  - the Barrett's-DB participant bridge (70 patients);
  - the closeout pairs file.
  15 patients are beyond the 55-ID file. Excluded patients' slides were dropped from both ERIN training and ERIN test.
- **Scores.** Slide score = mean over the 15 fold models of the bag logit, using all tiles (up to 8,000). Six-class scores are the logit of the mean class probabilities. The tile score is the mean over models of the instance head applied to each tile embedding. Sample = max over slides (7 samples have 2 slides); endoscopy = max over samples.
- **(a) and (c) thresholds** are thr_sens over the fold's training progressor endoscopies (the R49 / round-8 convention). The c4 cut-off is the 90th percentile of training non-progressor endoscopies (c*).
- **(b) stacker.** L2 logistic regression (C = 1, standardised) on the sample-level logit of inner-OOF L-IMG and ERIN, fitted on the training patients' pre-event samples. Training-patient scores for thresholds and R49 cut-offs are 5-fold GroupKFold out-of-fold; held-out samples use the all-training fit.
- **(m) memory rules** use the round-9 engine (`rv9_falseflags.py`, executed unchanged up to its task dispatch):
  - EW memory of the R49-aligned gate score, half-life 1/2/4 years;
  - half-life and threshold chosen per fold by the round-9 rule: detection ≥ R49's training detection, then fewest training NP flagged;
  - the veto sets an endoscopy's score to −∞ when its ERIN score is below τ95 (training progressor endoscopies);
  - the stack is the rv9 endoscopy-level `lr_scores` on (gate score, ERIN logit).
  The reference row reproduces round 9 (30.7 / 23.6).
- **Computational deviation.** ERIN scoring of SWG slides ran on CPU (epyc), because the GPU queue was saturated; it reads features only. The 118 new slides were embedded on GPU from tile arrays written by CPU jobs.
- **Privacy.** Row-level scores, manifests and tiles stay in `killcoyne_mm/explore_E5/` on the cluster. The committed JSONs hold counts, AUROCs and deltas only.

# Exploration E2: copy number as a veto on H&E flags

Status: EXPLORATORY (20–21 October 2026), rules in `paper/reviews_round7/decisions/EXPLORE_RULES.md`. Nothing here is confirmatory; every rule tried is recorded.

## Plan

**Idea.** The L-CNV elastic net was trained to separate progressors from non-progressors over all samples. It was not trained to clear the H&E false positives. Here copy number is used only as a **veto**: H&E flags an endoscopy, its top-H&E sample (or top two) is sequenced, and the flag is kept only if the copy-number veto score says "not quiet".

**Bases.** P1 at 90% training endoscopy sensitivity (H&E only), and the R49 gate (veto on the high band only, or on the high and middle bands).

**Steps.**
1. **Descriptive.** Among endoscopies that H&E flags, compare copy-number features of the top-H&E sample between progressor and non-progressor endoscopies:
   - complexity cx (shipped block and package raw);
   - fraction of genome altered;
   - number of altered arms;
   - signed values of arms often altered early in OAC (17p, 9p, 18q, 5q, 4q, 13q, 3p losses; 8q, 7p, 20q gains);
   - focal against broad events;
   - per-sample noise (50-kb MAPD).
   
   Features are built from the shipped matrix (`cnv_their_C.csv`) and from the package tiles (joint segmentation as stored, and per-sample segmentation, R36). Fold-stratified AUROC within the flagged population, with patient-bootstrap CIs. Also the cross-tab of H&E and copy-number false positives among non-progressor endoscopies (are the errors independent?).
2. **Nested veto rules** (thresholds and models from training patients only, using inner out-of-fold predictions for the H&E flags of training endoscopies):
   - (a) fixed scores (cx, fraction altered, altered-arm count, OAC-arm score, stored L-CNV as comparator), with the threshold set on training patients by three rules:
     - strict: no loss of training progressor patients;
     - loss of at most 1 training progressor patient;
     - ≥ 95% of training flagged progressor endoscopies kept;
   - (b) an elastic net (α 0.9, C by inner patient-grouped CV) trained only on samples of H&E-flagged training endoscopies, either on the full shipped block or on a compact block of interpretable features, with nested inner out-of-fold scores for its threshold;
   - (c) top-1 against top-2 samples sequenced (veto score = maximum over the sequenced samples).
3. **Drift over time.** Is the non-progressor L-CNV rise from first to last endoscopy (+0.63 logit, round 8 L3) explained by sequencing batch or run, depth or noise? Then test a batch- or noise-aware veto if relevant.
4. **Coordinator additions.**
   - Within-patient copy-number stability veto: profile change since the patient's earliest or previous sequenced endoscopy. There is no history at the first endoscopy.
   - The H&E AND copy-number rule, after the independence check.

**Evaluation.** Every rule is evaluated on held-out patients against R49 and P1 on the same patients:
- Δ non-progressor patients ever flagged;
- Δ progressor patients caught;
- Δ samples sequenced per patient;
- Δ endoscopy specificity (also against P1 at matched endoscopy sensitivity);
- paired patient-bootstrap 95% CIs (2,000 draws, `RandomState(0)`).

Apparent (non-nested) numbers are labelled optimistic.

**Files.**
- **Scripts:** `scripts/paper_plan/ex_e2_veto.py`.
- **Aggregates:** `results/paper_final/explore_E2/`.
- **Row-level files:** `killcoyne_mm/explore_E2/` (cluster only).
- **Slurm prefix:** `exe2`.

---

## Results

Written 20 October 2026. All numbers are on held-out patients: the mean over the 10 repeats of the single model, with paired patient-bootstrap 95% CIs (2,000 draws, `RandomState(0)`). The checks reproduce R49 (31.1 caught, 31.8 non-progressors flagged, 1.94 samples sequenced per patient, endoscopy sensitivity / specificity 0.907 / 0.560) and P1 at 90% (31.1, 36.0, 0, 0.898 / 0.524).

**Notation.**
- **Bases.**
  - P1 = H&E at 90%.
  - R49h = veto applied only to R49's high band (flags R49 makes without sequencing).
  - R49hm = veto applied to every R49 flag (high band and called middle band).
- **k** = top-H&E samples sequenced for the veto (1 or 2; with 2, the veto score is the maximum over the two).
- **Threshold rules** (all set on the outer fold's training patients, with H&E flags of training endoscopies from inner out-of-fold scores):
  - strict = no training progressor patient lost;
  - loss1 = at most one lost;
  - endo95 = ≥ 95% of vetoable training progressor endoscopies kept;
  - cn90 = the copy-number-alone threshold (90% of all training progressor endoscopies).
- **Features.**
  - ps_ = per-sample segmentation (R36);
  - jt_ = joint per-patient segmentation as stored;
  - th_ = shipped block `cnv_their_C.csv`;
  - oac = summed loss on 17p, 9p, 18q, 5q, 4q, 13q, 3p plus gain on 8q, 7p, 20q;
  - fga10 = share of 5-Mb tiles deviating > 10% from the sample median;
  - narm05 = arms deviating > 5%;
  - ntilez2 = tiles with |z| > 2 in the shipped block.

Aggregates are in `results/paper_final/explore_E2/` (`desc`, `fixed_*`, `sel_*`, `en_eval`, `drift`, `stab`, `combo`, `and`, `decomp`). The full table of 1,000+ cells is printed by `scripts/paper_plan/ex_e2_render.py`.

### 1. What separates progressor from non-progressor endoscopies among those H&E flags (descriptive)

H&E (P1 90%) flags a mean of 79.0 progressor and 95.1 non-progressor endoscopies per repeat. AUROC is for the top-H&E sample's feature, progressor vs non-progressor endoscopy, among the held-out flagged endoscopies, with a patient-bootstrap CI. The training-fold column is the same AUROC among each fold's training endoscopies flagged by inner scores (mean over 100 folds).

| Feature (top-H&E sample) | AUROC held-out [CI] | AUROC training folds | Median P / NP |
|---|---|---|---|
| L-LATE (logit) | 0.821 [0.747, 0.884] | 0.787 | 0.59 / −0.56 |
| L-CNV (logit) | 0.769 [0.684, 0.844] | 0.717 | 0.26 / −1.44 |
| L-IMG (logit) | 0.751 [0.675, 0.825] | 0.727 | 1.83 / −0.07 |
| th_ntilez2 (tiles with \|z\| > 2) | 0.749 [0.678, 0.819] | 0.731 | 5 / 0 |
| 7p (per-sample arm value) | 0.728 [0.640, 0.802] | 0.724 | |
| 17p loss (sign reversed) | 0.657 [0.566, 0.747] | 0.663 | −3.3% / −2.6% |
| oac arm score (joint / per-sample / shipped) | 0.694 / 0.678 / 0.691 | 0.70 / 0.69 / 0.70 | |
| th_armzabs (summed \|arm z\|) | 0.690 | 0.684 | |
| fraction of genome altered (fga15 / fga10 / fga05, per sample) | 0.639 / 0.612 / 0.600 | 0.63 / 0.61 / 0.59 | |
| altered arms (narm05, joint / per sample) | 0.632 / 0.593 | | |
| 9p, 13q, 5q loss (sign reversed, per sample) | 0.59, 0.56, 0.59 | | |
| complexity cx (shipped / package raw) | 0.509 / 0.48–0.52 | ≈ 0.50 | |
| sample noise (50-kb MAPD) / read count | 0.524 / 0.518 | | |

- **Quietness alone discriminates poorly where the veto acts.** Complexity cx carries no signal among flagged endoscopies (AUROC 0.51). Fraction altered and altered-arm counts reach about 0.60–0.64. The canonical OAC arms (17p, 9p, 13q losses; 7p, 8q gains) do better, at 0.68–0.69 combined. The trained L-CNV (0.77) and L-LATE (0.82) are better than every simple feature. In the R49 high band (55.8 progressor, 34.9 non-progressor endoscopies), the AUROCs are L-CNV 0.739, oac 0.696 and fga10 0.62.
- **Noise contaminates "altered".** In non-progressor samples, fraction altered correlates with 50-kb noise: Spearman 0.46 per-sample segmentation, 0.46 joint. Noisy non-progressor samples look altered, which blunts any quietness veto.
- **H&E and copy-number false positives are nearly independent per endoscopy** (P1 90% vs P2 90%, non-progressor endoscopies, means over repeats):
  - observed counts: both 64.4, H&E only 30.7, copy number only 56.2, neither 48.7;
  - expected "both" under independence 57.4; φ = 0.14;
  - correlation of the max logits 0.24.
  
  **At the patient level they are not.** 30.0 of 43 non-progressors are flagged at some endoscopy by both, 6.0 by H&E only, 5.0 by copy number only, and 2.0 by neither. An AND rule therefore helps per endoscopy, but many non-progressors still meet both modalities at some point in their history.

### 2. Veto rules, nested

**Where R49's false flags come from** (`decomp`). Of the 31.8 non-progressors R49 flags:
- 6.1 are flagged only through the high band;
- 9.0 only through the called middle band;
- 16.7 through both.

A high-band-only veto (R49h) can therefore clear at most about 6 patients. Vetoing every flag (R49hm) can reach all of them.

**(a) Fixed scores** (`fixed_*`, 25 quietness features + stored L-CNV and L-LATE × k 1/2 × 4 rules × 3 bases = 648 cells). Every cell is nested, but picking the best cell afterwards is not. Selected cells are below; the full list is in the JSON.

| Rule | Caught / 32 | NP flagged / 43 | Seq / patient | Endo sens / spec | Δ NP flagged vs R49 [CI] | Δ caught vs R49 [CI] | Δ NP flagged vs P1 [CI] | Δ caught vs P1 [CI] | Δ endo spec vs P1 at matched sens [CI] |
|---|---|---|---|---|---|---|---|---|---|
| R49hm veto ps_oac k2 cn90 | 31.1 | 26.6 | 4.35 | 0.812 / 0.706 | -5.2 [-9.1, -2.1] | +0.0 [+0.0, +0.0] | -9.4 [-14.3, -4.9] | +0.0 [-1.5, +1.9] | +0.049 [-0.068, +0.196] |
| R49hm veto ps_oac k2 strict | 29.7 | 23.0 | 4.35 | 0.690 / 0.759 | -8.8 [-13.1, -4.9] | -1.4 [-3.7, +0.0] | -13.0 [-18.1, -8.1] | -1.4 [-4.3, +1.1] | -0.014 [-0.141, +0.105] |
| R49h veto L-LATE k1 endo95 | 31.1 | 29.9 | 3.15 | 0.892 / 0.606 | -1.9 [-3.7, -0.6] | +0.0 [+0.0, +0.0] | -6.1 [-9.7, -2.5] | +0.0 [-1.5, +1.9] | +0.084 [-0.037, +0.195] |
| R49hm veto L-LATE k1 strict | 30.8 | 28.2 | 3.15 | 0.848 / 0.670 | -3.6 [-5.0, -2.3] | -0.3 [-0.8, +0.0] | -7.8 [-11.6, -4.2] | -0.3 [-2.1, +1.7] | +0.068 [-0.034, +0.162] |
| R49hm veto L-LATE k1 loss1 | 30.5 | 24.3 | 3.15 | 0.806 / 0.754 | -7.5 [-9.7, -5.3] | -0.6 [-1.5, +0.0] | -11.7 [-15.8, -7.6] | -0.6 [-2.6, +1.3] | +0.094 [+0.013, +0.174] |
| R49hm veto L-CNV k1 strict | 30.6 | 28.2 | 3.15 | 0.868 / 0.614 | -3.6 [-5.5, -1.9] | -0.5 [-1.4, +0.0] | -7.8 [-11.8, -3.8] | -0.5 [-2.3, +1.4] | +0.062 [-0.071, +0.166] |
| P1 veto L-LATE k1 strict | 30.1 | 29.4 | 2.32 | 0.840 / 0.676 | -2.4 [-3.7, -1.2] | -1.0 [-2.6, +0.0] | -6.6 [-10.0, -3.6] | -1.0 [-2.4, +0.0] | +0.046 [-0.004, +0.094] |
| P1 veto L-CNV k1 cn90 (H&E AND copy number, top sample) | 30.1 | 28.2 | 2.32 | 0.812 / 0.676 | -3.6 [-6.1, -1.1] | -1.0 [-2.9, +0.5] | -7.8 [-11.3, -4.6] | -1.0 [-2.2, -0.1] | +0.016 [-0.083, +0.089] |
| R49hm veto ps_fga10 k1 strict | 30.0 | 31.7 | 3.15 | 0.880 / 0.564 | -0.1 [-0.3, +0.0] | -1.1 [-3.4, +0.0] | -4.3 [-7.5, -1.3] | -1.1 [-3.8, +1.3] | +0.032 [-0.105, +0.129] |
| R49hm veto th_cx k1 strict | 30.3 | 31.8 | 3.15 | 0.889 / 0.564 | +0.0 [+0.0, +0.0] | -0.8 [-1.7, +0.0] | -4.2 [-7.4, -1.2] | -0.8 [-2.4, +0.6] | +0.036 [-0.084, +0.143] |

- **Apparent (optimistic)** = one threshold per repeat set on the evaluation patients at no progressor loss. Non-progressors flagged: R49hm L-LATE k1 22.7; R49hm ps_oac k2 22.3; R49hm L-CNV k2 26.5; P1 L-CNV k2 27.8.

  The gap between these and the nested numbers is the cost of setting the threshold on 29 training progressors: the "no training loss" threshold loses 0.3–1.4 progressor patients on new patients.
- **cx, fraction altered and arm counts do almost nothing** as vetoes once the threshold must protect training progressors. The few patients they clear come with progressor losses. Batch- and noise-adjusted versions (section 3) do not change this.
- **The no-loss ps_oac k2 cn90 cell is a post-hoc pick** among about 650 cells. Neighbouring cells of the same score (strict, loss1, k1) all lose progressors. The fold-level selection below tests it properly.

**(a′) Selected per outer fold on training patients** (`sel_*`). This is the honest version of "pick the best rule". In each outer fold, among a family's candidates, take the one with the fewest training non-progressor patients flagged, among those whose training progressor detection is ≥ the base's (training loss ≤ 0) or ≥ the base's − 1.

| Rule | Caught / 32 | NP flagged / 43 | Seq / patient | Endo sens / spec | Δ NP flagged vs R49 [CI] | Δ caught vs R49 [CI] | Δ NP flagged vs P1 [CI] | Δ caught vs P1 [CI] | Δ endo spec vs P1 at matched sens [CI] |
|---|---|---|---|---|---|---|---|---|---|
| R49hm, trained models (L-CNV / L-LATE), loss ≤ 0 | 30.3 | 26.4 | 3.36 | 0.822 / 0.685 | -5.4 [-7.5, -3.4] | -0.8 [-1.6, -0.2] | -9.6 [-13.8, -5.6] | -0.8 [-2.7, +1.3] | +0.039 [-0.057, +0.154] |
| R49hm, trained models, loss ≤ 1 | 30.2 | 22.9 | 3.36 | 0.778 / 0.753 | -8.9 [-11.7, -6.0] | -0.9 [-1.9, -0.2] | -13.1 [-17.6, -8.5] | -0.9 [-3.0, +1.2] | +0.063 [-0.028, +0.156] |
| R49hm, quiet features, loss ≤ 0 (picks ps_oac k2 strict in 83 of 100 folds) | 29.1 | 22.9 | 4.29 | 0.688 / 0.759 | -8.9 [-12.9, -5.3] | -2.0 [-4.4, -0.5] | -13.1 [-17.9, -8.4] | -2.0 [-4.9, +0.6] | -0.014 [-0.140, +0.098] |
| R49hm, all candidates (fixed, trained, gated, elastic net, double), loss ≤ 0 | 29.5 | 23.0 | 4.01 | 0.707 / 0.768 | -8.8 [-11.9, -5.8] | -1.6 [-3.6, -0.4] | -13.0 [-17.2, -8.9] | -1.6 [-4.2, +0.8] | +0.009 [-0.093, +0.102] |
| R49hm, trained models with NDBE/ID gate, loss ≤ 0 | 30.5 | 26.6 | 2.95 | 0.809 / 0.690 | -5.2 [-7.4, -3.1] | -0.6 [-1.4, -0.1] | -9.4 [-13.5, -5.4] | -0.6 [-2.5, +1.4] | +0.033 [-0.059, +0.129] |
| R49hm, double vetoes, loss ≤ 0 | 29.9 | 24.1 | 4.35 | 0.755 / 0.743 | -7.7 [-11.3, -4.5] | -1.2 [-3.3, +0.0] | -11.9 [-16.3, -7.6] | -1.2 [-3.9, +1.2] | +0.025 [-0.085, +0.147] |
| R49h, trained models, loss ≤ 0 | 30.3 | 28.8 | 3.24 | 0.840 / 0.620 | -3.0 [-5.1, -1.4] | -0.8 [-2.1, +0.0] | -7.2 [-10.8, -3.4] | -0.8 [-2.9, +1.3] | +0.008 [-0.118, +0.134] |
| P1, trained models, loss ≤ 0 | 29.9 | 28.5 | 2.57 | 0.820 / 0.690 | -3.3 [-4.9, -1.8] | -1.2 [-2.9, +0.0] | -7.5 [-10.7, -4.5] | -1.2 [-2.5, -0.3] | +0.037 [-0.027, +0.098] |
| P1, quiet features, loss ≤ 0 | 29.7 | 25.9 | 3.56 | 0.680 / 0.762 | -5.9 [-11.3, -1.0] | -1.4 [-4.1, +0.7] | -10.1 [-14.7, -6.0] | -1.4 [-3.5, -0.1] | -0.023 [-0.142, +0.089] |
| R49hm, elastic-net vetoes (compact block), loss ≤ 0 | 29.7 | 29.6 | 3.65 | 0.811 / 0.650 | -2.2 [-3.5, -1.1] | -1.4 [-2.7, -0.4] | -6.4 [-9.9, -2.9] | -1.4 [-3.5, +0.6] | +0.002 [-0.100, +0.123] |

**When the rule is chosen on training patients, every copy-number veto loses progressor patients.**
- **Trained-model vetoes:** the loss is about 0.8 (CI excludes 0). They clear 5.4 non-progressors (loss ≤ 0) or 8.9 (loss ≤ 1) relative to R49.
- **Quietness vetoes:** the loss is about 2, so they are worse.
- **Exchange rate:** for comparison, moving H&E alone from 90% to 80% (round 8) costs 1.0 progressor and clears 4.4 non-progressors. The trained-model veto on all R49 flags clears about 6–10 per progressor lost, a better rate than H&E thresholds. It is not free.

**(b) Elastic net trained only on H&E-flagged training endoscopies** (`en_*`, `en_eval`):
- **Specification:** α 0.9, C by patient-grouped inner CV, nested inner out-of-fold scores for the threshold. Populations: P1-90% flagged, the wider 95% flagged, and all training samples.
- **Compact block** (44 per-sample arm deviations + 11 summary features): held-out AUROC of the top sample among P1-flagged endoscopies 0.719 (flagged population), 0.718 (wide) and 0.723 (all). Training on the flagged population does not help, and the compact model is below L-CNV (0.769).
- **As a veto:** no cell reduces non-progressors flagged by more than about 1.5 without losing progressors. The best no-loss cell is R49h EN[compact, all] k1 cn90: −0.7 [−1.4, −0.2], caught 31.1.
- **Full shipped block (633 features):** STILL RUNNING at the time of writing; see the status line at the end.

**(c) One against two samples.** A second sample helps only the quietness scores (ps_oac R49hm: k1 cn90 −3.3 non-progressors at −1.2 caught; k2 cn90 −5.2 at 0.0). For the trained models it adds sequencing (3.15 → 4.35 samples per patient on R49hm) with no gain.

**(d) Double veto** (`combo`, 192 cells). A flag is vetoed only if both conditions hold:
- the OAC-arm profile of the top two samples is quiet, below its copy-number-alone training threshold at 90% or 80%;
- the top sample's L-LATE or L-CNV is below the rule's threshold.

| Cell | Caught | Non-progressors flagged | Δ vs R49 | Samples per patient |
|---|---|---|---|---|
| quiet < 80%, L-LATE strict | 31.0 (Δ −0.1 [−0.3, 0.0]) | 24.3 | −7.5 [−11.5, −4.1] | 4.35 |
| quiet < 80%, L-CNV strict | 31.0 | 24.6 | −7.2 | 4.35 |
| quiet < 90% | 31.1 | 26.6 | −5.2 | 4.35 |

At 90% this reproduces the ps_oac k2 cn90 cell. These are the best single cells of the exploration. **Selected per fold on training patients** (`sel_R49hm`, double-veto family, loss ≤ 0), they give 29.9 caught (Δ −1.2 [−3.3, 0.0]) and 24.1 non-progressors flagged (Δ −7.7 [−11.3, −4.5]). The no-loss single cells are therefore partly selection luck.

**Why "no training loss" does not transfer.** The strict threshold is the minimum, over about 29 training progressor patients, of each patient's best veto score. A new progressor falls below that minimum with probability about 1/(n + 1) ≈ 1/30, so about 1 of 32 new progressors is expected to be lost. That is what the strict rules show (0.3–1.4 lost). No veto tuned on this cohort can be shown to lose nobody, and R49 itself misses 0.9.

**(e) H&E AND copy number, every sample of an H&E-flagged endoscopy sequenced** (`and`). Max L-IMG ≥ P1 threshold AND max L-CNV ≥ P2 threshold:
- 90% / 90%: 30.1 caught, 27.7 non-progressors flagged, 4.88 samples sequenced per patient; Δ vs R49 −4.1 [−7.3, −1.1] non-progressors, −1.0 [−2.8, +0.3] caught.
- 80% / 95%: 30.0, 27.9, 3.99.

These are the same trade-off as the top-sample vetoes, at more sequencing.

**(f) Within-patient stability veto** (coordinator idea; `stab`):
- **Scores:** change of the top sample's per-sample arm profile since the patient's first pre-event endoscopy:
  - change = mean |Δ arm|;
  - new = arms altered now but not at baseline;
  - cur_plus_change = current burden + change.
- **Rules:** the first endoscopy keeps its flag. The baseline sample counts as sequenced once if not already sequenced.
- **Results:** R49hm change strict 30.4 caught, 27.0 flagged (Δ vs R49 −4.8 [−7.6, −2.5] non-progressors, −0.7 [−1.4, −0.1] caught), 2.92 samples sequenced per patient. "New arms" strict: 30.7 / 28.6 (−3.2 / −0.4). cur_plus_change strict: 30.0 / 24.8 (−7.0 / −1.1).
- **Interpretation:** stable non-progressor profiles exist, but no stability rule avoids progressor losses. The loss1 versions reach 19–21 non-progressors flagged at 29.3–29.6 caught, which is the lowest false-flag region seen, at a cost of about 1.5–2 progressors.

**(g) Grade gate** (`grade`, added while running). Only endoscopies whose highest sample grade is NDBE (or NDBE/ID) can be vetoed and sequenced; dysplastic endoscopies keep the base call.
- **Single cells.** R49hm L-LATE k1 strict, NDBE/ID only: 30.9 caught (Δ −0.2 [−0.5, 0.0]), 27.7 non-progressors flagged (Δ −4.1 [−5.8, −2.5]), 2.80 samples sequenced per patient. Ungated it is 30.8 / 28.2 / 3.15. With loss1: 30.4 / 24.4 / 2.80.
- **Selected per fold** (trained models, NDBE/ID gate, loss ≤ 0): R49hm 30.5 caught (Δ −0.6 [−1.4, −0.1]), 26.6 flagged (Δ −5.2 [−7.4, −3.1]), 2.95 per patient. Gated or not, loss ≤ 0: 30.4 / 26.1 / 3.11 (Δ −5.7 [−7.9, −3.6], caught −0.7 [−1.5, −0.1]).
- **Interpretation.** The gate saves sequencing and a little progressor loss. It does not remove the loss.

### 3. Copy-number drift in non-progressors: not batch, partly sample noise

For non-progressors with ≥ 2 endoscopies (43), the endoscopy L-CNV score (mean over repeats of the max logit, as round 8 L3) rises from first to last endoscopy by +0.625.

- **Batch.** First and last endoscopy were sequenced in the same sheet batch for 38 of 43 non-progressors (same-batch mean rise +0.50; the 5 different-batch patients +1.56). Mixed model among non-progressor endoscopies (slope per year before the reference, negative = rising):
  - time only −0.077 [−0.127, −0.026];
  - + batch −0.082 [−0.133, −0.030].
  
  **Batch does not explain the drift.**
- **Noise and depth.** Sample noise (50-kb MAPD) falls with later endoscopies (log MAPD slope +0.031 per year before the reference [0.025, 0.037]; the older archival samples are noisier). Adding log MAPD and log reads attenuates the slope to −0.049 [−0.112, +0.013] (−0.051 with batch too).

  Noise therefore explains about a third of the drift. Noisier samples receive a lower L-CNV (MAPD coefficient −0.8 logit per log unit, not significant).
- **Genome burden does not rise.** Non-progressors' fraction altered actually falls towards the reference (+0.003 per year before it [0.001, 0.005]). The drift is in the model score, not in the number of alterations.
- **Progressors.** The rise survives every adjustment (−0.322 time only, −0.242 with batch, MAPD and reads).
- **Batch- and noise-aware vetoes** (feature minus the training non-progressor median of its batch, or residual on log MAPD, refitted per fold) change nothing material. For example, R49hm L-CNV batch-adjusted strict gives −3.8 non-progressors / −0.7 caught against −3.6 / −0.5 unadjusted; fraction altered batch-adjusted gives −2.3 / −1.0.

### 4. Where the vetoes sit against round 8

Joint frontier on caught, non-progressors flagged and samples sequenced, over the E2 cells and all round-8 policy cells:
- **The E2 cells on it** are the R49hm trained-model and stability vetoes listed above, from 31.1 caught / 26.6 flagged (ps_oac k2 cn90, post hoc) and 30.5 / 24.3 (L-LATE loss1) down to 29.1–29.3 / 19–21 (stability loss1).
- **They displace** P3 80% (30.5 / 26.4 at 7.6 samples per patient) and P4 80%.
- **Round-8 points that stay** are the P1 grid, P6 90/85, P7 and P8. P8 (t_b 80%, t_mid 80%) at 30.9 / 28.7 / 1.70 is close to the strict trained-model veto (30.8 / 28.2 / 3.15) with half the sequencing. These two are the same idea: sequence the top sample of an H&E-elevated endoscopy and call it by L-LATE.

**Lead time.** Vetoes remove the earliest flags. R49hm L-LATE strict moves the median first flag → event from 4.7 to 4.4 years (loss1: 4.2). Vetoed progressor endoscopies lie a median 4.8–5.5 years before the event, against 3.0 for kept ones.

Figure (local): `paper/figures_explore_E2/e2_veto_scatter.png`.

### Implementation notes

- Round-8 helpers are run unchanged by executing `rv8_landscape.py` into a namespace (`setup`, `patient_arrays`, `lstats`, `cell_result`, `thr_arr`, `r49_calls`).
- **Training-side R49 for threshold selection:** the fold's stored t_low, c\* and t_seq applied to training endoscopies' inner out-of-fold max L-IMG, with the inner top sample's L-LATE for the middle band.
- **Top-H&E sample:** outer L-IMG on held-out patients, inner L-IMG on training.
- **Sequencing counts:** k samples at every vetoable flagged endoscopy (the middle band's top sample is already sequenced, so k − 1 extra there).
- **Raw tile tables:** `review_round4/reseg/tiles_{joint_stored,persample}_analysed.csv` (relative copy number, 587 tiles + 44 arms); deviations relative to the sample's median tile. 50-kb MAPD from QDNAseq `50.copy_number.txt` (log2), consecutive bins within chromosomes.
- **Elastic net:** scikit-learn `LogisticRegression(penalty="elasticnet", l1_ratio=0.9, solver="saga")`, C grid 10^−2.5…10^1 (8 values) by patient-grouped inner CV on binomial deviance, features standardised on the training rows. Inner out-of-fold veto scores use the stored inner fold assignment, with C re-chosen inside each inner split.
- **Per-fold selection (`sel_*`):** candidates are the fixed-score, trained-model and compact elastic-net cells. Training outcomes are resubstitution (the threshold was set on the same patients), which is one reason the selected rules lose progressors on new patients.
- **Bootstrap:** patient multiplicities, 2,000 draws, `RandomState(0)` (round-8 `pdraws`). Δ endoscopy specificity at matched sensitivity: P1's pooled-fold ROC per repeat at the rule's endoscopy sensitivity.
- **Privacy:** patient counts < 5 are shown as "<5"; feature tables and elastic-net predictions stay on the cluster (`killcoyne_mm/explore_E2/`).

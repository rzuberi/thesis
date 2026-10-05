# The 1/3/5-year table and four questions (discovery subset)

Status: PRE-SPECIFICATION (written 2026-10-05). Nothing new below has been run. Results are appended under the line at the end in a later commit; this section is not edited afterwards. Where this specification reuses outputs computed earlier under an identical specification, that is stated item by item.

Ground rules as in the earlier paper tasks (`docs/paper_plan_killcoyne_cv.md`, `docs/paper_survival_horizons.md`): rank AUROC to 3 decimals; patient-clustered bootstrap 2,000 draws `RandomState(0)`; within-patient swap permutation 2,000 draws seed 0; status per item; at most one line of interpretation per answer; earlier docs not edited. ACE-B columns stay "pending (slides being scanned)"; no ACE-B outcome, pathology or follow-up is read.

## Cohort, labels, predictions

- **The discovery subset** = set C (`feasibility/paper_plan/killcoyne_mm/set_C.csv`): 676 samples, 80 patients, 37 progressors.
- **Labels**: Killcoyne 2020 only (sheet `Status`: P = NDBE → HGD/IMC, NP = never beyond LGD).
- **Predictions**: the stratified, patient-grouped 10-fold × 10 CV out-of-fold predictions of `docs/paper_plan_killcoyne_cv.md` (`kv_cv.R`, results commit d69de24; fold-honest image scaling); arm score = mean of the 10 repeats; L-LATE = per-repeat mean of L-CNV and L-IMG, then averaged. CNV source: their matrix (primary), package features (secondary). L-INTER under the stratified CV (32 + 32 PCA components per modality fitted on training rows, `paper_plan_killcoyne_multimodal.md` specification) was fitted for `docs/paper_survival_horizons.md` (`hz_fit.R` MODE=outer, commit 4d7efa9) and is reused here, not refitted again.

## Time, samples, horizons (identical to `docs/paper_survival_horizons.md` H0)

- Time per sample = years from the sample to the endpoint from the 777 sheet's `Months before final` (`mbf`). Progressors: endpoint = first HGD/IMC endoscopy among the published samples (`tev` = largest `mbf` among HGD/IMC samples, `kc_merge.py:30-32`); the 4 progressors with no HGD/IMC sample use the final endoscopy (`tev` = 0), flagged, and the table is also reported without them. Non-progressors: censored at their last endoscopy (`mbf`/12). Cross-check: `mbf` against the Source Data `Months before final` (MOESM4 'Supporting data for Figure 2d', MOESM11) per sample; agreement reported, the sheet value used.
- Samples: only those before the event (progressor samples with `mbf` > `tev`; all non-progressor samples); samples on or after the first HGD/IMC, including the diagnostic samples, are excluded.
- Horizon t = 1, 3, 5 years. Case: event within t. Control: event-free with follow-up ≥ t (event = 0 and time ≥ t, or event = 1 and time > t). Censored before t without event: dropped at t. n cases and n controls reported as samples and as patients.

## Metrics

- Primary: IPCW time-dependent AUROC (cumulative/dynamic, Uno-type; censoring Kaplan–Meier on the reverse outcome, re-estimated in every bootstrap draw), per sample, patient-clustered bootstrap CI.
- Secondary: unweighted AUROC on the same cases and controls; per patient on each patient's earliest pre-event NDBE sample; Harrell's C over all follow-up.

## Rows

- **Clinical only: L-CLIN (new fit).** L2-penalised logistic regression (scikit-learn, C = 1, the default; no tuning) on [sample pathology grade (ordinal NDBE 0, ID 1, LGD 2, HGD 3, IMC 4), age at BE diagnosis (`Demographics_full.csv` 'Age at diagnosis'), sex (M = 1), Prague M (`Maximal`) with missing values filled by the training-fold median plus a missing indicator]; features z-scored on the training rows; label = ever-progression (sheet `Status`, as every other arm); fitted in the same stratified outer folds (the fold of each sample per repeat read from the `kv_cv.R` prediction files), mean over the 10 repeats. **L-CLIN without grade** (demographics only) the same, as a sanity check (expected near 0.5 because the cohort was matched on age, sex and segment length).
- CNV (replication): L-CNV. WSI: L-IMG. Early fusion: L-EARLY. Inter fusion: L-INTER (refitted under the stratified CV for the earlier task, reused). Late fusion: L-LATE.

## Best model and tests

- Pre-registered primary: L-LATE. "Best" at a horizon = highest primary (IPCW, per sample) AUROC among the six table rows.
- Paired Δ of every arm against L-LATE and against L-CNV, patient-bootstrap CI.
- Selection-adjusted p: single-step max-T over the 5 non-clinical arms within each horizon, by within-patient swap permutation with one mask per permutation shared across pairs: (i) for Δ vs L-LATE, the family is the other 4 non-clinical arms; (ii) for Δ vs L-CNV, the other 4 non-clinical arms. Adjusted p = (1 + #{max |Δ*| ≥ |Δ_j|}) / 2,001.

## Q0. The table

Rows as above, cells AUROC [95% CI], ACE-B cells "pending"; a row of n cases / n controls (samples; patients) per horizon. Supplements: package features; NDBE pre-event samples only; and the table without the 4 fallback-endpoint progressors.

## Q1. Best model by horizon

Best arm per horizon, its AUROC, Δ vs L-CNV and vs L-LATE with CI and adjusted p; whether the ranking of arms changes across horizons (rank order per horizon reported).

## Q2. False positives and newly captured patients

- Operating point per horizon and model: within each outer training fold, the largest threshold whose sensitivity among that horizon's training cases (pre-event samples, horizon-t case definition) on the **inner out-of-fold** predictions is ≥ 0.80; applied to the held-out fold's outer prediction of the same repeat. Inner out-of-fold predictions: `hz_fit.R` MODE=inner (commit 4d7efa9) for L-CNV, L-IMG, L-EARLY, L-INTER (L-LATE = their L-CNV/L-IMG mean); for L-CLIN, the same inner folds (the `inner_fold` recorded in those files) with the L-CLIN recipe. Sample call = positive in ≥ 6 of 10 repeats.
- Compare L-CNV against the Q1 best arm and, if different, against L-LATE: FPR and TPR of each, paired ΔFPR (and ΔTPR) with patient-bootstrap CI; 2 × 2 reclassification (CNV−/best+, CNV+/best−) for cases and controls, as samples and as patients (patient unit: earliest pre-event NDBE sample); categorical NRI with CI. Their matrix (primary), package features (secondary); all pre-event samples.
- Newly captured cases (CNV−/best+) vs cases positive under both, and newly cleared controls (CNV+/best−) vs controls positive under both: study number, sample pathology, time to event, CNV complexity (raw cx of the package block, from the frozen scaling constants) and noise (package QC `varMAD_median`), tissue tiles available, scanner, p53 IHC where present, Killcoyne's published risk class of that sample (MOESM4 'Supporting data for Figure 2a', `Risk class`). **The per-patient list (study numbers with these fields) is row-level patient data, so under the standing rule that row-level tables stay off the public repository it is written to the cluster only (`feasibility/paper_plan/killcoyne_mm/horizon_answers/q2_patient_list.csv`); the document gives the group summaries, counts and that path.**

## Q3. WSI vs CNV weighting (exploratory)

Identical to `docs/paper_survival_horizons.md` H3 (pre-specified in ee51db8, run in 4d7efa9): within each outer training fold and horizon, logistic stack label_t ~ a + b·z(logit CNV) + c·z(logit IMG) on inner out-of-fold predictions (L2 1e-4 on slopes), 100 fits per horizon; WSI share c/(b + c) mean over fits with patient-bootstrap CI (2,000 refits with patient-multiplicity weights); paired 1-year minus 5-year difference; held-out stack AUROC vs fixed 50/50 L-LATE. Because the specification is identical, the H3 outputs (`results/paper_final/horizons/h3_{their,pkg}.json`) are reused, not recomputed. **Expectation stated before running H3 and restated here: the WSI share is higher at 1 year than at 5 years.**

## Q4. 4× CNV and depth transfer

- Search the cluster again (sharded `lfs find`, same roots and patterns as `hz_search_shard.py`) for 4× resequenced discovery data and for ACE-B reads (SLX pools in the manifest); list the paths checked. No 4× discovery data → "4× → external: NOT AVAILABLE (no 4× training data)".
- If ACE-B reads exist: the label-blind depth check pre-specified in `docs/paper_survival_horizons.md` H4 (0.3×, 0.4×, 1×, 4× nominal, 5 seeds, `samtools view -s`; package features hg38 50 kb frozen parameters with the discovery hg38 bin annotation; frozen L-CNV package; ICC across seeds and vs native, median |Δ probability|, share changing Killcoyne risk class, cx by depth vs the discovery subset). If not: NOT AVAILABLE with the paths checked.

## Design caveat (to appear in the output)

The discovery cohort is a matched case–control design (non-progressors ≥ 3 years of follow-up, progressors ≥ 1 year): AUROCs are valid; absolute risks, calibration and positive predictive values are not.

## Output

`docs/paper_horizon_answers.md` (this file, results below); scripts `scripts/paper_plan/ha_*`; results `results/paper_final/horizon_answers/*.json`; figures (PNG, PDF, numbers in JSON): AUROC by horizon per arm, Q2 reclassification, Q3 WSI share by horizon, Q4 probability stability by depth (if run). All cluster work through `scripts/cluster/campaign.sh`.

---

## Results

Pre-specification commit 81473df; results commit afa0278. Scripts `scripts/paper_plan/ha_clin.py` (L-CLIN), `ha_metrics.py` (Q0/Q1), `ha_intercept.py` (added sanity check), `ha_q2.py` (Q2), `ha_search_shard.py` (Q4), `ha_figs.py`, `ha_render.py`; reused: `kv_cv.R` (d69de24), `hz_fit.R`, `hz_prep.py`, `hz_stack.py` (4d7efa9). All run through `scripts/cluster/campaign.sh` (prefixes hac, ham, hai, haq2, has, has2).
Results: `results/paper_final/horizon_answers/q0_{their,pkg}_{pre,pre_ndbe,pre_nofallback}.json`, `q0_check.json`, `q0_intercept_only.json`, `q2.json`, `q4_search.json`; Q3 from `results/paper_final/horizons/h3_{their,pkg}.json` (4d7efa9). Figures `results/paper_final/horizon_answers/figs/*.{png,pdf,json}`. Row-level files on the cluster only, under `feasibility/paper_plan/killcoyne_mm/horizon_answers/` (L-CLIN predictions, Q2 patient list).

### Status

| Item | Status |
|---|---|
| Q0 table (internal) | DONE; ACE-B pending (slides being scanned) |
| Q1 best model by horizon | DONE |
| Q2 false positives and newly captured patients | DONE (patient list by study number on the cluster only) |
| Q3 WSI vs CNV weighting (exploratory) | DONE (outputs of the identical H3 specification reused) |
| Q4 4× CNV and depth transfer | 4× → external: NOT AVAILABLE (no 4× training data); ACE-B depth check NOT AVAILABLE |

### Q0. The table

Discovery subset, all pre-event samples, CNV source their matrix. IPCW time-dependent AUROC [95% patient-bootstrap CI], per sample. Clinical Only = L-CLIN.

|  | Internal 1-year | Internal 3-year | Internal 5-year | ACE-B 1 | ACE-B 3 | ACE-B 5 |
|---|---|---|---|---|---|---|
| Clinical Only (baseline) | 0.604 [0.436, 0.754] | 0.430 [0.313, 0.553] | 0.458 [0.362, 0.565] | pending | pending | pending |
| CNV (replication) | 0.815 [0.698, 0.923] | 0.775 [0.683, 0.860] | 0.792 [0.698, 0.871] | pending | pending | pending |
| WSI | 0.782 [0.668, 0.869] | 0.817 [0.731, 0.894] | 0.786 [0.714, 0.856] | pending | pending | pending |
| Early fusion | 0.853 [0.756, 0.931] | 0.828 [0.747, 0.902] | 0.820 [0.745, 0.886] | pending | pending | pending |
| Inter fusion | 0.829 [0.737, 0.915] | 0.818 [0.734, 0.898] | 0.787 [0.697, 0.872] | pending | pending | pending |
| Late fusion | 0.869 [0.806, 0.921] | 0.855 [0.778, 0.922] | 0.844 [0.777, 0.902] | pending | pending | pending |
| n cases / n controls (samples; patients) | 29 / 449; 14 / 72 | 99 / 277; 29 / 62 | 126 / 168; 32 / 46 | pending (slides being scanned) | pending (slides being scanned) | pending (slides being scanned) |

L-CLIN without grade (demographics only, sanity check): 1 y 0.348 [0.205, 0.519], 3 y 0.294 [0.181, 0.435], 5 y 0.313 [0.192, 0.464]. It sits below 0.5, not near it; the intercept-only prediction (each sample's training-fold prevalence; check added after the pre-specification) scores 1 y 0.412 [0.258, 0.573], 3 y 0.289 [0.186, 0.410], 5 y 0.290 [0.175, 0.429], so the shortfall is the stratified-CV fold-prevalence artefact of `docs/paper_plan_killcoyne_cv.md` (folds of 3–4 P patients in 8), which a near-constant score inherits, not a reversed demographic signal.

**Supplement: package features** (all pre-event samples).

|  | Internal 1-year | Internal 3-year | Internal 5-year | ACE-B 1 | ACE-B 3 | ACE-B 5 |
|---|---|---|---|---|---|---|
| Clinical Only (baseline) | 0.604 [0.436, 0.754] | 0.430 [0.313, 0.553] | 0.458 [0.362, 0.565] | pending | pending | pending |
| CNV (replication) | 0.805 [0.714, 0.895] | 0.779 [0.692, 0.850] | 0.796 [0.693, 0.878] | pending | pending | pending |
| WSI | 0.782 [0.668, 0.869] | 0.817 [0.731, 0.894] | 0.786 [0.714, 0.856] | pending | pending | pending |
| Early fusion | 0.836 [0.760, 0.900] | 0.814 [0.724, 0.887] | 0.811 [0.712, 0.890] | pending | pending | pending |
| Inter fusion | 0.802 [0.719, 0.877] | 0.822 [0.749, 0.890] | 0.803 [0.720, 0.871] | pending | pending | pending |
| Late fusion | 0.852 [0.782, 0.909] | 0.842 [0.760, 0.912] | 0.839 [0.760, 0.906] | pending | pending | pending |
| n cases / n controls (samples; patients) | 29 / 449; 14 / 72 | 99 / 277; 29 / 62 | 126 / 168; 32 / 46 | pending (slides being scanned) | pending (slides being scanned) | pending (slides being scanned) |

**Supplement: NDBE pre-event samples only**, their matrix.

|  | Internal 1-year | Internal 3-year | Internal 5-year | ACE-B 1 | ACE-B 3 | ACE-B 5 |
|---|---|---|---|---|---|---|
| Clinical Only (baseline) | 0.260 [0.099, 0.462] | 0.268 [0.154, 0.427] | 0.342 [0.197, 0.515] | pending | pending | pending |
| CNV (replication) | 0.873 [0.761, 0.948] | 0.772 [0.659, 0.878] | 0.763 [0.654, 0.859] | pending | pending | pending |
| WSI | 0.731 [0.575, 0.865] | 0.780 [0.684, 0.876] | 0.744 [0.651, 0.824] | pending | pending | pending |
| Early fusion | 0.889 [0.802, 0.952] | 0.826 [0.727, 0.918] | 0.788 [0.700, 0.871] | pending | pending | pending |
| Inter fusion | 0.881 [0.783, 0.943] | 0.812 [0.692, 0.924] | 0.770 [0.654, 0.873] | pending | pending | pending |
| Late fusion | 0.870 [0.782, 0.932] | 0.823 [0.728, 0.920] | 0.792 [0.707, 0.865] | pending | pending | pending |
| n cases / n controls (samples; patients) | 12 / 334; 9 / 69 | 61 / 192; 25 / 59 | 79 / 111; 26 / 39 | pending (slides being scanned) | pending (slides being scanned) | pending (slides being scanned) |

**Supplement: NDBE pre-event samples only**, package features.

|  | Internal 1-year | Internal 3-year | Internal 5-year | ACE-B 1 | ACE-B 3 | ACE-B 5 |
|---|---|---|---|---|---|---|
| Clinical Only (baseline) | 0.260 [0.099, 0.462] | 0.268 [0.154, 0.427] | 0.342 [0.197, 0.515] | pending | pending | pending |
| CNV (replication) | 0.826 [0.700, 0.913] | 0.749 [0.646, 0.851] | 0.758 [0.636, 0.859] | pending | pending | pending |
| WSI | 0.731 [0.575, 0.865] | 0.780 [0.684, 0.876] | 0.744 [0.651, 0.824] | pending | pending | pending |
| Early fusion | 0.830 [0.734, 0.902] | 0.776 [0.663, 0.883] | 0.756 [0.631, 0.860] | pending | pending | pending |
| Inter fusion | 0.788 [0.683, 0.885] | 0.819 [0.729, 0.904] | 0.792 [0.692, 0.877] | pending | pending | pending |
| Late fusion | 0.837 [0.745, 0.902] | 0.798 [0.702, 0.895] | 0.785 [0.690, 0.868] | pending | pending | pending |
| n cases / n controls (samples; patients) | 12 / 334; 9 / 69 | 61 / 192; 25 / 59 | 79 / 111; 26 / 39 | pending (slides being scanned) | pending (slides being scanned) | pending (slides being scanned) |

**Supplement: without the 4 fallback-endpoint progressors**, their matrix.

|  | Internal 1-year | Internal 3-year | Internal 5-year | ACE-B 1 | ACE-B 3 | ACE-B 5 |
|---|---|---|---|---|---|---|
| Clinical Only (baseline) | 0.597 [0.412, 0.763] | 0.429 [0.304, 0.556] | 0.441 [0.332, 0.547] | pending | pending | pending |
| CNV (replication) | 0.811 [0.690, 0.925] | 0.777 [0.684, 0.866] | 0.803 [0.710, 0.884] | pending | pending | pending |
| WSI | 0.785 [0.664, 0.873] | 0.817 [0.727, 0.893] | 0.796 [0.720, 0.866] | pending | pending | pending |
| Early fusion | 0.850 [0.752, 0.934] | 0.825 [0.746, 0.905] | 0.823 [0.749, 0.893] | pending | pending | pending |
| Inter fusion | 0.827 [0.730, 0.919] | 0.814 [0.727, 0.901] | 0.793 [0.702, 0.882] | pending | pending | pending |
| Late fusion | 0.868 [0.803, 0.920] | 0.854 [0.772, 0.924] | 0.860 [0.794, 0.916] | pending | pending | pending |
| n cases / n controls (samples; patients) | 28 / 441; 13 / 68 | 96 / 271; 27 / 59 | 120 / 165; 28 / 44 | pending (slides being scanned) | pending (slides being scanned) | pending (slides being scanned) |

**Secondary metrics** (all pre-event samples; patient unit = earliest pre-event NDBE sample).

| CNV source | Metric | L-CLIN | L-CNV | L-IMG | L-EARLY | L-INTER | L-LATE |
|---|---|---|---|---|---|---|---|
| their | per sample, Harrell's C | 0.485 [0.384, 0.590] | 0.762 [0.684, 0.834] | 0.778 [0.712, 0.838] | 0.802 [0.734, 0.869] | 0.777 [0.705, 0.851] | 0.824 [0.764, 0.877] |
| their | per patient 1 y (2/69) | 0.130 [0.000, 0.319] | 0.935 [0.857, 0.986] | 0.565 [0.371, 0.754] | 0.906 [0.797, 0.986] | 0.891 [0.814, 0.957] | 0.841 [0.700, 0.957] |
| their | per patient 3 y (9/59) | 0.430 [0.127, 0.734] | 0.767 [0.548, 0.934] | 0.802 [0.657, 0.913] | 0.831 [0.661, 0.963] | 0.885 [0.779, 0.962] | 0.820 [0.675, 0.933] |
| their | per patient 5 y (15/39) | 0.446 [0.240, 0.660] | 0.725 [0.573, 0.864] | 0.749 [0.598, 0.880] | 0.730 [0.577, 0.857] | 0.784 [0.655, 0.901] | 0.764 [0.613, 0.889] |
| their | unweighted 1 y | 0.604 [0.436, 0.754] | 0.815 [0.698, 0.923] | 0.782 [0.668, 0.869] | 0.853 [0.756, 0.931] | 0.829 [0.736, 0.915] | 0.869 [0.806, 0.921] |
| their | unweighted 3 y | 0.435 [0.318, 0.558] | 0.775 [0.683, 0.863] | 0.816 [0.730, 0.892] | 0.828 [0.747, 0.902] | 0.817 [0.734, 0.897] | 0.855 [0.778, 0.923] |
| their | unweighted 5 y | 0.456 [0.357, 0.566] | 0.792 [0.696, 0.873] | 0.795 [0.722, 0.864] | 0.823 [0.745, 0.891] | 0.793 [0.704, 0.875] | 0.851 [0.784, 0.908] |
| pkg | per sample, Harrell's C | 0.485 [0.384, 0.590] | 0.764 [0.690, 0.832] | 0.778 [0.712, 0.838] | 0.794 [0.724, 0.860] | 0.787 [0.723, 0.846] | 0.817 [0.751, 0.873] |
| pkg | per patient 1 y (2/69) | 0.130 [0.000, 0.319] | 0.877 [0.765, 0.971] | 0.565 [0.371, 0.754] | 0.841 [0.714, 0.943] | 0.609 [0.321, 0.871] | 0.775 [0.671, 0.870] |
| pkg | per patient 3 y (9/59) | 0.430 [0.127, 0.734] | 0.708 [0.513, 0.880] | 0.802 [0.657, 0.913] | 0.783 [0.630, 0.910] | 0.787 [0.631, 0.912] | 0.794 [0.652, 0.905] |
| pkg | per patient 5 y (15/39) | 0.446 [0.240, 0.660] | 0.672 [0.505, 0.826] | 0.749 [0.598, 0.880] | 0.684 [0.530, 0.821] | 0.717 [0.585, 0.847] | 0.753 [0.601, 0.879] |
| pkg | unweighted 1 y | 0.604 [0.436, 0.754] | 0.805 [0.714, 0.895] | 0.782 [0.668, 0.869] | 0.836 [0.760, 0.900] | 0.802 [0.719, 0.877] | 0.852 [0.782, 0.909] |
| pkg | unweighted 3 y | 0.435 [0.318, 0.558] | 0.779 [0.692, 0.850] | 0.816 [0.730, 0.892] | 0.815 [0.727, 0.887] | 0.821 [0.747, 0.888] | 0.842 [0.761, 0.911] |
| pkg | unweighted 5 y | 0.456 [0.357, 0.566] | 0.796 [0.694, 0.874] | 0.795 [0.722, 0.864] | 0.813 [0.715, 0.892] | 0.804 [0.722, 0.872] | 0.843 [0.765, 0.908] |

Time check: the 777 sheet's `Months before final` (used) agrees with the Source Data for every patient (MOESM4 'Supporting data for Figure 2d': each patient's set of sample months is contained in the published set for 80/80 patients; MOESM11: 80/80; the Source Data have no sample identifiers, so the check is per patient; `q0_check.json`).

## Which is best model? 1/3/5 year?

**Answer.** On their CNV matrix the best arm is L-LATE at all three horizons: AUROC 0.869, 0.855, 0.844, with L-EARLY second at every horizon. Its gain over L-CNV is +0.054, +0.080, +0.053 (max-T p 0.6387, 0.1639, 0.5152); after selection adjustment no arm differs from L-LATE except L-CNV at 3 years (max-T p 0.033). The order of the middle arms changes across horizons (rank orders below), but the top two do not; on NDBE samples only, L-EARLY is first at 1 and 3 years and L-LATE at 5 years. One line: late fusion is the best arm at every horizon, by margins that adjustment mostly cannot separate from early or intermediate fusion.

**Best arm per horizon**, their matrix, all pre-event samples.

| Horizon | Best | AUROC [CI] | Δ vs L-CNV [CI] (p, max-T) | Δ vs L-LATE [CI] (p, max-T) | Ranking (IPCW AUROC) |
|---|---|---|---|---|---|
| 1 y | L-LATE | 0.869 [0.806, 0.921] | +0.054 [-0.043, +0.151] (p 0.3738, max-T 0.6387) | — | L-LATE > L-EARLY > L-INTER > L-CNV > L-IMG > L-CLIN |
| 3 y | L-LATE | 0.855 [0.778, 0.922] | +0.080 [+0.015, +0.157] (p 0.027, max-T 0.1639) | — | L-LATE > L-EARLY > L-INTER > L-IMG > L-CNV > L-CLIN |
| 5 y | L-LATE | 0.844 [0.777, 0.902] | +0.053 [-0.011, +0.131] (p 0.1384, max-T 0.5152) | — | L-LATE > L-EARLY > L-CNV > L-INTER > L-IMG > L-CLIN |

Package features:

| Horizon | Best | AUROC [CI] | Δ vs L-CNV [CI] (p, max-T) | Δ vs L-LATE [CI] (p, max-T) | Ranking (IPCW AUROC) |
|---|---|---|---|---|---|
| 1 y | L-LATE | 0.852 [0.782, 0.909] | +0.048 [-0.031, +0.123] (p 0.2784, max-T 0.5712) | — | L-LATE > L-EARLY > L-CNV > L-INTER > L-IMG > L-CLIN |
| 3 y | L-LATE | 0.842 [0.760, 0.912] | +0.062 [+0.011, +0.121] (p 0.011, max-T 0.1474) | — | L-LATE > L-INTER > L-IMG > L-EARLY > L-CNV > L-CLIN |
| 5 y | L-LATE | 0.839 [0.760, 0.906] | +0.043 [-0.006, +0.103] (p 0.1524, max-T 0.4878) | — | L-LATE > L-EARLY > L-INTER > L-CNV > L-IMG > L-CLIN |

NDBE pre-event samples, their matrix:

| Horizon | Best | AUROC [CI] | Δ vs L-CNV [CI] (p, max-T) | Δ vs L-LATE [CI] (p, max-T) | Ranking (IPCW AUROC) |
|---|---|---|---|---|---|
| 1 y | L-EARLY | 0.889 [0.802, 0.952] | +0.015 [-0.023, +0.067] (p 0.3718, max-T 0.9865) | +0.019 [-0.044, +0.091] (p 0.6282, max-T 0.9735) | L-EARLY > L-INTER > L-CNV > L-LATE > L-IMG > L-CLIN |
| 3 y | L-EARLY | 0.826 [0.727, 0.918] | +0.054 [+0.002, +0.120] (p 0.08, max-T 0.5377) | +0.002 [-0.032, +0.034] (p 0.9255, max-T 1.0) | L-EARLY > L-LATE > L-INTER > L-IMG > L-CNV > L-CLIN |
| 5 y | L-LATE | 0.792 [0.707, 0.865] | +0.029 [-0.037, +0.107] (p 0.4693, max-T 0.8726) | — | L-LATE > L-EARLY > L-INTER > L-CNV > L-IMG > L-CLIN |

**All arms, paired deltas**, their matrix, all pre-event samples (max-T over the 5 non-clinical arms; clinical arms have unadjusted CIs only).

| Horizon | Arm | AUROC | Δ vs L-LATE [CI] | Δ vs L-CNV [CI] |
|---|---|---|---|---|
| 1 y | L-CLIN | 0.604 | -0.266 [-0.445, -0.099] | -0.212 [-0.451, +0.002] |
| 1 y | L-CNV | 0.815 | -0.054 [-0.151, +0.043] (p 0.3738, max-T 0.5972) | — |
| 1 y | L-IMG | 0.782 | -0.087 [-0.182, -0.009] (p 0.066, max-T 0.1664) | -0.033 [-0.217, +0.136] (p 0.6952, max-T 0.8741) |
| 1 y | L-EARLY | 0.853 | -0.017 [-0.078, +0.042] (p 0.8416, max-T 0.9925) | +0.037 [-0.030, +0.105] (p 0.2794, max-T 0.8376) |
| 1 y | L-INTER | 0.829 | -0.041 [-0.102, +0.026] (p 0.3638, max-T 0.8096) | +0.013 [-0.067, +0.091] (p 0.7226, max-T 0.996) |
| 1 y | L-LATE | 0.869 | — | +0.054 [-0.043, +0.151] (p 0.3738, max-T 0.6387) |
| 3 y | L-CLIN | 0.430 | -0.425 [-0.535, -0.323] | -0.345 [-0.485, -0.201] |
| 3 y | L-CNV | 0.775 | -0.080 [-0.157, -0.015] (p 0.027, max-T 0.033) | — |
| 3 y | L-IMG | 0.817 | -0.038 [-0.084, +0.001] (p 0.1444, max-T 0.5717) | +0.041 [-0.061, +0.147] (p 0.4458, max-T 0.5907) |
| 3 y | L-EARLY | 0.828 | -0.027 [-0.067, +0.010] (p 0.3268, max-T 0.7926) | +0.052 [+0.002, +0.113] (p 0.067, max-T 0.4368) |
| 3 y | L-INTER | 0.818 | -0.037 [-0.083, +0.012] (p 0.2584, max-T 0.6032) | +0.043 [-0.033, +0.127] (p 0.3093, max-T 0.5722) |
| 3 y | L-LATE | 0.855 | — | +0.080 [+0.015, +0.157] (p 0.027, max-T 0.1639) |
| 5 y | L-CLIN | 0.458 | -0.387 [-0.491, -0.273] | -0.334 [-0.459, -0.198] |
| 5 y | L-CNV | 0.792 | -0.053 [-0.131, +0.011] (p 0.1384, max-T 0.4128) | — |
| 5 y | L-IMG | 0.786 | -0.058 [-0.109, -0.004] (p 0.056, max-T 0.3263) | -0.005 [-0.111, +0.115] (p 0.926, max-T 1.0) |
| 5 y | L-EARLY | 0.820 | -0.024 [-0.076, +0.026] (p 0.4588, max-T 0.9225) | +0.029 [-0.027, +0.095] (p 0.3378, max-T 0.8681) |
| 5 y | L-INTER | 0.787 | -0.057 [-0.123, +0.006] (p 0.2069, max-T 0.3433) | -0.004 [-0.086, +0.081] (p 0.932, max-T 1.0) |
| 5 y | L-LATE | 0.844 | — | +0.053 [-0.011, +0.131] (p 0.1384, max-T 0.5152) |

Package features, all pre-event samples:

| Horizon | Arm | AUROC | Δ vs L-LATE [CI] | Δ vs L-CNV [CI] |
|---|---|---|---|---|
| 1 y | L-CLIN | 0.604 | -0.249 [-0.425, -0.080] | -0.201 [-0.415, -0.005] |
| 1 y | L-CNV | 0.805 | -0.048 [-0.123, +0.031] (p 0.2784, max-T 0.4738) | — |
| 1 y | L-IMG | 0.782 | -0.070 [-0.152, -0.007] (p 0.0915, max-T 0.1644) | -0.022 [-0.176, +0.109] (p 0.7521, max-T 0.921) |
| 1 y | L-EARLY | 0.836 | -0.016 [-0.049, +0.018] (p 0.4478, max-T 0.97) | +0.031 [-0.032, +0.092] (p 0.3383, max-T 0.7996) |
| 1 y | L-INTER | 0.802 | -0.051 [-0.104, +0.005] (p 0.079, max-T 0.4208) | -0.003 [-0.085, +0.073] (p 0.943, max-T 1.0) |
| 1 y | L-LATE | 0.852 | — | +0.048 [-0.031, +0.123] (p 0.2784, max-T 0.5712) |
| 3 y | L-CLIN | 0.430 | -0.412 [-0.516, -0.312] | -0.349 [-0.480, -0.221] |
| 3 y | L-CNV | 0.779 | -0.062 [-0.121, -0.011] (p 0.011, max-T 0.019) | — |
| 3 y | L-IMG | 0.817 | -0.025 [-0.065, +0.011] (p 0.2474, max-T 0.6742) | +0.037 [-0.048, +0.125] (p 0.3783, max-T 0.4718) |
| 3 y | L-EARLY | 0.814 | -0.028 [-0.060, +0.001] (p 0.1544, max-T 0.5882) | +0.035 [-0.005, +0.076] (p 0.1159, max-T 0.5277) |
| 3 y | L-INTER | 0.822 | -0.020 [-0.064, +0.023] (p 0.4228, max-T 0.8176) | +0.042 [-0.012, +0.104] (p 0.1664, max-T 0.3863) |
| 3 y | L-LATE | 0.842 | — | +0.062 [+0.011, +0.121] (p 0.011, max-T 0.1474) |
| 5 y | L-CLIN | 0.458 | -0.382 [-0.483, -0.274] | -0.339 [-0.457, -0.206] |
| 5 y | L-CNV | 0.796 | -0.043 [-0.103, +0.006] (p 0.1524, max-T 0.3803) | — |
| 5 y | L-IMG | 0.786 | -0.053 [-0.107, +0.004] (p 0.079, max-T 0.2054) | -0.010 [-0.109, +0.100] (p 0.8651, max-T 0.9865) |
| 5 y | L-EARLY | 0.811 | -0.029 [-0.074, +0.007] (p 0.3333, max-T 0.7086) | +0.014 [-0.019, +0.048] (p 0.3918, max-T 0.945) |
| 5 y | L-INTER | 0.803 | -0.037 [-0.085, +0.012] (p 0.2089, max-T 0.5172) | +0.006 [-0.051, +0.070] (p 0.8161, max-T 0.997) |
| 5 y | L-LATE | 0.839 | — | +0.043 [-0.006, +0.103] (p 0.1524, max-T 0.4878) |

**Method.** `ha_metrics.py`: IPCW cumulative/dynamic AUROC (reverse Kaplan–Meier weights re-estimated per draw), 2,000 patient-bootstrap draws `RandomState(0)`, paired deltas on the same draws, within-patient swap permutation (2,000, seed 0) with single-step max-T (families in the pre-specification). Scores: mean over 10 repeats of out-of-fold probabilities. **Sources.** `cv/preds/` (kv_cv.R), `horizons/outer/inter_*` (hz_fit.R), `horizon_answers/clin_outer.csv` (ha_clin.py), `horizons/samples.csv` (hz_prep.py); `q0_*.json`.
**Caveats.** The models were trained on ever-progression, so these are ever-progression scores ranked against near-term and later events. The 1-year cells rest on 29 case samples from 14 patients.

## Change in false positive rate: what patients does the best model capture that was previously missing?

**Answer.** The best arm is L-LATE at every horizon, so the comparison is L-LATE against L-CNV (their matrix). At each model's 80%-sensitivity threshold for that horizon, L-LATE has fewer false positives: ΔFPR -0.089 [-0.156, -0.019] at 1 year, -0.141 [-0.242, -0.040] at 3 years and -0.089 [-0.216, +0.040] at 5 years, with NRI +0.227, +0.171 and +0.089. At 3 years it newly captures 11 case samples from 6 patients that L-CNV missed; most were low risk in Killcoyne's published classes (Low 8, High 2, Moderate 1), with lower CNV complexity (median cx 19 vs 25) and fewer tissue tiles (211 vs 258) than cases positive under both. It clears 58 control samples from 26 patients. One line: late fusion mainly removes false positives; the cases it adds are CNV-quiet ones that the published model also called low risk.

**FPR, TPR and NRI**, their matrix (patient unit: earliest pre-event NDBE sample).

| Horizon | Unit | Cases/controls | Best | L-CNV TPR / FPR | Best TPR / FPR | ΔFPR [CI] | ΔTPR [CI] | NRI [CI] |
|---|---|---|---|---|---|---|---|---|
| 1 y | sample | 29/449 | L-LATE | 0.793 / 0.370 | 0.931 / 0.281 | -0.089 [-0.156, -0.019] | +0.138 [-0.133, +0.412] | +0.227 [-0.041, +0.500] |
| 1 y | patient | 2/69 | L-LATE | 1.000 / 0.319 | 1.000 / 0.333 | +0.014 [-0.103, +0.130] | +0.000 [+0.000, +0.000] | -0.014 [-0.130, +0.103] |
| 3 y | sample | 99/277 | L-LATE | 0.818 / 0.444 | 0.848 / 0.303 | -0.141 [-0.242, -0.040] | +0.030 [-0.090, +0.153] | +0.171 [+0.004, +0.343] |
| 3 y | patient | 9/59 | L-LATE | 0.778 / 0.373 | 0.889 / 0.322 | -0.051 [-0.179, +0.070] | +0.111 [+0.000, +0.364] | +0.162 [-0.036, +0.446] |
| 5 y | sample | 126/168 | L-LATE | 0.825 / 0.417 | 0.825 / 0.327 | -0.089 [-0.216, +0.040] | +0.000 [-0.102, +0.116] | +0.089 [-0.079, +0.261] |
| 5 y | patient | 15/39 | L-LATE | 0.733 / 0.359 | 0.733 / 0.385 | +0.026 [-0.133, +0.179] | +0.000 [-0.273, +0.263] | -0.026 [-0.336, +0.275] |

Package features:

| Horizon | Unit | Cases/controls | Best | L-CNV TPR / FPR | Best TPR / FPR | ΔFPR [CI] | ΔTPR [CI] | NRI [CI] |
|---|---|---|---|---|---|---|---|---|
| 1 y | sample | 29/449 | L-LATE | 0.828 / 0.365 | 0.897 / 0.281 | -0.085 [-0.158, -0.021] | +0.069 [-0.125, +0.250] | +0.154 [-0.048, +0.343] |
| 1 y | patient | 2/69 | L-LATE | 1.000 / 0.435 | 1.000 / 0.333 | -0.101 [-0.221, +0.015] | +0.000 [+0.000, +0.000] | +0.101 [-0.015, +0.224] |
| 3 y | sample | 99/277 | L-LATE | 0.838 / 0.404 | 0.838 / 0.343 | -0.061 [-0.147, +0.011] | +0.000 [-0.114, +0.097] | +0.061 [-0.061, +0.189] |
| 3 y | patient | 9/59 | L-LATE | 0.778 / 0.508 | 0.889 / 0.373 | -0.136 [-0.250, -0.034] | +0.111 [+0.000, +0.364] | +0.247 [+0.063, +0.514] |
| 5 y | sample | 126/168 | L-LATE | 0.841 / 0.369 | 0.833 / 0.321 | -0.048 [-0.139, +0.038] | -0.008 [-0.115, +0.082] | +0.040 [-0.097, +0.167] |
| 5 y | patient | 15/39 | L-LATE | 0.800 / 0.462 | 0.800 / 0.410 | -0.051 [-0.189, +0.057] | +0.000 [-0.182, +0.200] | +0.051 [-0.167, +0.283] |

**Reclassification**, their matrix: samples (patients with ≥ 1 such sample) / patient unit.

| Horizon | Group | CNV− / best+ | CNV+ / best− | both + | both − |
|---|---|---|---|---|---|
| 1 y | cases | 6 (3) / 0 | 2 (2) / 0 | 21 (13) / 2 | 0 (0) / 0 |
| 1 y | controls | 30 (20) / 9 | 70 (30) / 8 | 96 (34) / 14 | 253 (51) / 38 |
| 3 y | cases | 11 (6) / 1 | 8 (6) / 0 | 73 (26) / 7 | 7 (4) / 1 |
| 3 y | controls | 19 (14) / 6 | 58 (26) / 9 | 65 (25) / 13 | 135 (39) / 31 |
| 5 y | cases | 13 (8) / 2 | 13 (9) / 2 | 91 (28) / 9 | 9 (5) / 2 |
| 5 y | controls | 16 (11) / 5 | 31 (14) / 4 | 39 (20) / 10 | 82 (27) / 20 |

Package features:

| Horizon | Group | CNV− / best+ | CNV+ / best− | both + | both − |
|---|---|---|---|---|---|
| 1 y | cases | 4 (3) / 0 | 2 (2) / 0 | 22 (13) / 2 | 1 (1) / 0 |
| 1 y | controls | 25 (16) / 6 | 63 (27) / 13 | 101 (38) / 17 | 260 (46) / 33 |
| 3 y | cases | 8 (7) / 1 | 8 (4) / 0 | 75 (28) / 7 | 8 (5) / 1 |
| 3 y | controls | 21 (14) / 2 | 38 (21) / 10 | 74 (31) / 20 | 144 (32) / 27 |
| 5 y | cases | 11 (7) / 1 | 12 (8) / 1 | 94 (31) / 11 | 9 (5) / 2 |
| 5 y | controls | 10 (7) / 2 | 18 (11) / 4 | 44 (21) / 14 | 96 (25) / 19 |

**Newly captured and newly cleared**, their matrix, per sample (medians; counts).

| Horizon | Group | Samples / patients | Pathology | Years to event or censoring | cx (raw) | Noise (varMAD) | Tissue tiles | Scanner | p53 IHC | Killcoyne risk class (MOESM4) |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 y | captured cases CNVneg bestpos | 6 / 3 | LGD 5, NDBE 1 | 0.8 | 25 | 0.002 | 196 | C13210 5, C13239-01 1 | 0.0 5, 1.0 1 | Low 3, High 2, Moderate 1 |
| 1 y | cases both pos | 21 / 13 | NDBE 10, LGD 9, ID 2 | 0.5 | 21 | 0.003 | 268 | C13239-01 18, C13210 3 | 0.0 11, nan 5, 1.0 5 | High 21 |
| 1 y | cleared controls CNVpos bestneg | 70 / 30 | NDBE 52, ID 12, LGD 6 | 4.0 | 24 | 0.003 | 277 | C13239-01 46, C13210 24 | 0.0 54, nan 15, 1.0 1 | High 39, Moderate 26, Low 5 |
| 1 y | controls both pos | 96 / 34 | NDBE 63, LGD 23, ID 10 | 3.0 | 28 | 0.003 | 257 | C13239-01 74, C13210 22 | 0.0 48, nan 40, 1.0 8 | High 82, Moderate 13, Low 1 |
| 3 y | captured cases CNVneg bestpos | 11 / 6 | NDBE 5, LGD 5, ID 1 | 2.0 | 19 | 0.002 | 211 | C13239-01 6, C13210 5 | 0.0 9, nan 2 | Low 8, High 2, Moderate 1 |
| 3 y | cases both pos | 73 / 26 | NDBE 44, LGD 21, ID 8 | 1.5 | 25 | 0.002 | 258 | C13239-01 54, C13210 19 | 0.0 42, nan 16, 1.0 15 | High 65, Moderate 7, Low 1 |
| 3 y | cleared controls CNVpos bestneg | 58 / 26 | NDBE 36, ID 19, LGD 3 | 5.0 | 24 | 0.003 | 237 | C13239-01 44, C13210 14 | 0.0 48, nan 10 | Moderate 25, High 17, Low 16 |
| 3 y | controls both pos | 65 / 25 | NDBE 44, LGD 16, ID 5 | 5.5 | 26 | 0.003 | 332 | C13239-01 49, C13210 16 | nan 35, 0.0 29, 1.0 1 | High 51, Moderate 11, Low 3 |
| 5 y | captured cases CNVneg bestpos | 13 / 8 | NDBE 7, LGD 5, ID 1 | 2.0 | 19 | 0.002 | 211 | C13239-01 8, C13210 5 | 0.0 11, nan 2 | Low 8, High 3, Moderate 2 |
| 5 y | cases both pos | 91 / 28 | NDBE 54, LGD 28, ID 9 | 2.0 | 26 | 0.002 | 278 | C13239-01 71, C13210 20 | 0.0 47, nan 29, 1.0 15 | High 81, Moderate 9, Low 1 |
| 5 y | cleared controls CNVpos bestneg | 31 / 14 | NDBE 16, ID 13, LGD 2 | 6.0 | 23 | 0.003 | 223 | C13239-01 21, C13210 10 | 0.0 26, nan 5 | Moderate 14, High 9, Low 8 |
| 5 y | controls both pos | 39 / 20 | NDBE 29, LGD 7, ID 3 | 8.0 | 26 | 0.004 | 319 | C13239-01 26, C13210 13 | nan 20, 0.0 18, 1.0 1 | High 28, Moderate 9, Low 2 |

Study numbers: the per-patient list (1126 rows: study number, sample, pathology, time, cx, noise, tissue tiles, scanner, p53, published risk class, for every group, horizon and CNV source) is row-level patient data and stays on the cluster: `/mnt/scratche/slow/fmlab/zuberi01/phd/thesis/feasibility/paper_plan/killcoyne_mm/horizon_answers/q2_patient_list.csv`. Published risk class matched for 676/676 samples.

Thresholds (median over the 100 fold × repeat fits): 1 y L-CNV 0.327, L-LATE 0.429; 3 y L-CNV 0.232, L-LATE 0.358; 5 y L-CNV 0.23, L-LATE 0.334 (their matrix).

**Method.** `ha_q2.py`: per model, horizon, repeat and outer fold, the threshold is the largest value with ≥ 80% sensitivity among that horizon's pre-event training cases on the inner out-of-fold predictions (`hz_fit.R` inner; L-CLIN inner from `ha_clin.py`); held-out calls, positive in ≥ 6 of 10 repeats; ΔFPR, ΔTPR and categorical NRI with 2,000 patient-bootstrap draws. **Sources.** As above, plus `horizons/slide_desc.csv`, `horizons/pkg_qc.csv`, `models/killcoyne_frozen_pkg_v1/cnv_scaling_setC.csv` (raw cx), `killcoyne_data_from_paper/41591_2020_1033_MOESM4_ESM.xlsx` (risk class); `q2.json`.
**Caveats.** FPR and TPR describe this matched case–control sample, not a screening population (design caveat). The patient unit has 2 cases at 1 year. The group comparison is descriptive, with no test.

## What's the weighting between WSI and CNV? Does this change between 1-year and 5-year?

**Answer (exploratory).** The WSI share c/(b+c) of the horizon-specific stack is about one half at every horizon: 0.496 [0.015, 0.811], 0.575 [0.385, 0.730], 0.495 [0.319, 0.661] at 1, 3 and 5 years on their matrix (package features 0.503, 0.596, 0.484). The 1-year minus 5-year difference is +0.001 [-0.411, +0.291] (package +0.019 [-0.354, +0.280]), so the pre-stated expectation of a higher WSI share at 1 year is not supported. Held out, no horizon-specific stack beats the fixed 50/50 L-LATE (Δ -0.033, -0.008, -0.005). One line: equal weighting is as good as fitted weighting at every horizon.

| CNV source | Horizon | Fits | b (CNV) [CI] | c (WSI) [CI] | WSI share c/(b+c) [CI] | Held-out stack vs L-LATE IPCW AUROC, Δ [CI] |
|---|---|---|---|---|---|---|
| their matrix | 1 y | 100 | 0.542 [0.207, 1.159] | 0.511 [0.025, 1.015] | 0.496 [0.015, 0.811] | 0.836 vs 0.869: -0.033 [-0.060, -0.008] |
| their matrix | 3 y | 100 | 0.820 [0.494, 1.378] | 1.082 [0.636, 1.699] | 0.575 [0.385, 0.730] | 0.847 vs 0.855: -0.008 [-0.021, +0.004] |
| their matrix | 5 y | 100 | 1.060 [0.663, 1.701] | 1.011 [0.606, 1.580] | 0.495 [0.319, 0.661] | 0.840 vs 0.844: -0.005 [-0.019, +0.010] |
| package features | 1 y | 100 | 0.547 [0.238, 1.011] | 0.541 [0.097, 1.022] | 0.503 [0.083, 0.785] | 0.824 vs 0.852: -0.028 [-0.051, -0.011] |
| package features | 3 y | 100 | 0.714 [0.447, 1.102] | 1.052 [0.610, 1.639] | 0.596 [0.414, 0.741] | 0.834 vs 0.842: -0.008 [-0.025, +0.010] |
| package features | 5 y | 100 | 1.022 [0.641, 1.544] | 0.951 [0.542, 1.491] | 0.484 [0.311, 0.639] | 0.836 vs 0.839: -0.003 [-0.019, +0.011] |

**Method.** Identical specification to `docs/paper_survival_horizons.md` H3 (pre-specified ee51db8, run 4d7efa9 with `hz_stack.py` TASK=h3_<src>); outputs reused, not recomputed. **Sources.** `results/paper_final/horizons/h3_their.json`, `h3_pkg.json`.
**Caveats.** Exploratory; the 1-year stacks rest on few cases, which is why the 1-year interval is wide (0.02–0.81).

## Does 4x CNV transfer to 7x external downsampled?

**Answer.** 4× → external: NOT AVAILABLE (no 4× training data). The re-run search (466 `lfs find` shards over `/mnt/scratche/fast/fmlab` and `/mnt/scratche/slow/fmlab`, 15,950,519 entries, 64,078 read files) finds no resequenced discovery data: the discovery-SLX read files outside `dna_seq_bam` are `/mnt/scratche/slow/fmlab/datasets/imaging/SWGCohort/validation_genomics` (780), `/mnt/scratche/slow/fmlab/zuberi01/phd/barretts_retraining/barretts_training` (780), `/mnt/scratche/slow/fmlab/zuberi01/phd/barretts_retraining/paper` (1565), i.e. the older hg19 alignment of the same runs (probed nominal depth at most 1.02×, `results/paper_final/horizons/h4_bam_probe.json`) and broken symlinks to it. No ACE-B reads (SLX pools SLX-26195, SLX-26196, SLX-26851, SLX-27125, SLX-27128) are on the cluster, so the label-blind depth check is NOT AVAILABLE.

**Paths checked.** Roots `/mnt/scratche/fast/fmlab`, `/mnt/scratche/slow/fmlab`, every depth-2 directory as its own shard plus each depth-1 directory at `-maxdepth 1` (shard list `feasibility/closeout/ha_search.tsv`, `ha_search2.tsv`); patterns: read-file extensions `bam`, `cram`, `fastq[.gz]`, `fq[.gz]`, `sra`; discovery SLX ids from the 777 sheet (15); ACE-B SLX pools from the manifest; directory names with 4x/deep/reseq/high-depth (125 hits, all software or slide folders). Unreadable-path messages: 1,975.

**Method.** `ha_search_shard.py` (same code as `hz_search_shard.py`, fresh output folder). **Sources.** `q4_search.json`.
**Caveats.** Only the mounted lab scratch is visible; data held by the sequencing core or the cohort owner off-cluster cannot be seen.

### Design caveat

The discovery cohort is a matched case–control design: non-progressors had at least 3 years of follow-up and progressors at least 1. AUROCs are valid; absolute risks, calibration and positive predictive values are not, and none is reported.

### Discrepancies found

- L-CLIN without grade is not near 0.5 (0.29–0.35); the intercept-only prediction scores the same, so the stratified-CV fold-prevalence artefact, not the demographics, sets it. The same artefact pulls L-CLIN below 0.5 at 3 and 5 years.
- The question heading says '7x external'; the ACE-B manifest gives median 5.3× (range 3.3–14.9×), as found in `docs/dataset_description.md` item 7.
- The Source Data carry no sample identifiers for `Months before final`, so the time check is per patient (all 80 agree).

### Not done

- ACE-B columns: pending (slides being scanned); L-CLIN and L-INTER have no frozen model for ACE-B.
- Q4 depth check (no ACE-B reads on the cluster).
- The per-patient study-number list is not in this document (cluster-only, as above).
- Q4 figure (probability stability by depth): not produced, no depth check.


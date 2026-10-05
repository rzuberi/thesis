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

(appended in a later commit)

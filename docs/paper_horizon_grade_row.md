# Pathology grade (raw score) row for the 1/3/5-year table

Status: PRE-SPECIFICATION (written 2026-10-05). Nothing below has been run. Results are appended under the line at the end in a later commit; this section is not edited afterwards.

Ground rules as in `docs/paper_horizon_answers.md` (81473df / afa0278) and `docs/paper_horizon_foldstrat.md` (2d0014f / d6b43ff): no refit; rank AUROC to 3 decimals; patient-clustered bootstrap 2,000 draws `RandomState(0)`; within-patient swap permutation 2,000 draws seed 0; status per item; at most one line of interpretation; earlier docs not edited. ACE-B columns stay "pending (slides being scanned)".

## The row

- **Pathology grade (raw score):** score = the sample's ordinal grade from `set_C.csv` `Pathology` (NDBE 0, ID 1, LGD 2; pre-event samples contain no HGD/IMC by construction), no model fitted, identical in every repeat. Higher grade = higher predicted risk; ties count ½.
- Same discovery subset, pre-event samples, event times, horizons (1/3/5 years), case/control definitions and IPCW weights as `docs/paper_horizon_answers.md`.
- **Metrics:** (i) pooled per-sample IPCW time-dependent AUROC; (ii) fold-stratified IPCW AUROC (`docs/paper_horizon_foldstrat.md`: same-fold case–control pairs per repeat, using each repeat's outer folds from `kv_cv.R`, averaged over repeats). For a score that does not depend on the fold, (ii) differs from (i) only through the restriction to same-fold pairs.
- **CIs and paired Δ:** patient bootstrap (2,000 draws, `RandomState(0)`, Ĝ re-estimated per draw); paired Δ of the raw-grade row vs L-CNV and vs L-LATE on the same draws, for each metric, with an unadjusted swap-permutation p (the raw-grade row is outside the max-T family of the 5 non-clinical arms). The row's AUROC is the same for both CNV sources; the Δs differ by source.
- **NDBE pre-event samples only:** the grade is constant (all 0), so the row is reported as **not estimable** (the AUROC would be 0.5 by ties); the number of distinct grades in that population is checked and reported.

## Tables

- Main 1/3/5-year table: the Clinical Only row is replaced by Pathology grade (raw score); the other rows (CNV, WSI, Early, Inter, Late fusion) are copied from the existing results (pooled: `results/paper_final/horizon_answers/q0_*.json`; fold-stratified: `results/paper_final/horizon_foldstrat/fs_*.json`), both metrics shown, for their matrix and package features, all pre-event samples and NDBE only.
- Supplement: L-CLIN and L-CLIN without grade (demographics only), from the same files, with the note that the discovery cohort was matched on age, sex and Barrett's segment length, so demographic predictors are not expected to discriminate.
- Design caveat as before: AUROCs only; no absolute risk, calibration or PPV.

## Output

`docs/paper_horizon_grade_row.md` (results below); script `scripts/paper_plan/hg_grade.py` (Slurm via `scripts/cluster/campaign.sh`, one task per CNV source × horizon, plus the NDBE constancy check), `scripts/paper_plan/hg_render.py`; results `results/paper_final/horizon_grade_row/*.json`.

---

## Results

(appended in a later commit)

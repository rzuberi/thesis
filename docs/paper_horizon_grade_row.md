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

Pre-specification commit 487b2a7; results commit 0ceb0a3. Script `scripts/paper_plan/hg_grade.py` (Slurm via `scripts/cluster/campaign.sh`, prefix hg), `scripts/paper_plan/hg_render.py`. Results `results/paper_final/horizon_grade_row/hg_{their,pkg}_{1,3,5}.json`, `hg_ndbecheck.json`. Other rows: pooled from `results/paper_final/horizon_answers/q0_*.json` (afa0278), fold-stratified from `results/paper_final/horizon_foldstrat/fs_*.json` (d6b43ff).

### Status

| Item | Status |
|---|---|
| Pathology grade (raw score) row, pooled and fold-stratified, all pre-event samples | DONE |
| NDBE pre-event samples only | NOT ESTIMABLE (distinct grades: [0.0], n = 438) |
| Paired Δ vs L-CNV and vs L-LATE | DONE |
| Supplement: L-CLIN and demographics only | DONE (copied, no new computation) |

Check: L-CNV and L-LATE recomputed on the same draws reproduce the stored pooled and fold-stratified AUROCs exactly (yes). Pre-event grades: NDBE 438, LGD 67, ID 66 samples.

### Answer

Raw pathology grade ranks samples above chance only at 1 year (fold-stratified 0.694 [0.566, 0.797], pooled 0.697) and close to chance at 3 and 5 years (0.543, 0.524). It is below L-CNV at every horizon (fold-stratified Δ -0.116, -0.225, -0.254) and below L-LATE (-0.160, -0.288, -0.297); the 1-year Δ vs L-CNV has a CI crossing zero. On NDBE samples the grade is constant and the row is not estimable. One line: grade carries near-term information only, which the CNV and image models exceed.

### Table: their matrix, all pre-event samples

Each cell: fold-stratified IPCW AUROC [95% patient-bootstrap CI]; pooled IPCW AUROC [CI]. The Pathology grade row is identical for both CNV sources.

|  | Internal 1-year | Internal 3-year | Internal 5-year | ACE-B 1 | ACE-B 3 | ACE-B 5 |
|---|---|---|---|---|---|---|
| Pathology grade (raw score) | 0.694 [0.566, 0.797]; pooled 0.697 [0.578, 0.808] | 0.543 [0.445, 0.634]; pooled 0.554 [0.461, 0.650] | 0.524 [0.434, 0.613]; pooled 0.535 [0.449, 0.623] | pending | pending | pending |
| CNV (replication) | 0.811 [0.656, 0.923]; pooled 0.815 [0.698, 0.923] | 0.767 [0.655, 0.841]; pooled 0.775 [0.683, 0.860] | 0.779 [0.669, 0.841]; pooled 0.792 [0.698, 0.871] | pending | pending | pending |
| WSI | 0.771 [0.631, 0.846]; pooled 0.782 [0.668, 0.869] | 0.788 [0.659, 0.866]; pooled 0.817 [0.731, 0.894] | 0.760 [0.661, 0.819]; pooled 0.786 [0.714, 0.856] | pending | pending | pending |
| Early fusion | 0.839 [0.714, 0.918]; pooled 0.853 [0.756, 0.931] | 0.802 [0.691, 0.872]; pooled 0.828 [0.747, 0.902] | 0.792 [0.688, 0.854]; pooled 0.820 [0.745, 0.886] | pending | pending | pending |
| Inter fusion | 0.811 [0.658, 0.899]; pooled 0.829 [0.737, 0.915] | 0.793 [0.683, 0.873]; pooled 0.818 [0.734, 0.898] | 0.765 [0.665, 0.837]; pooled 0.787 [0.697, 0.872] | pending | pending | pending |
| Late fusion | 0.854 [0.747, 0.907]; pooled 0.869 [0.806, 0.921] | 0.831 [0.705, 0.898]; pooled 0.855 [0.778, 0.922] | 0.821 [0.716, 0.873]; pooled 0.844 [0.777, 0.902] | pending | pending | pending |
| n cases / n controls (samples; patients) | 29 / 449; 14 / 72 | 99 / 277; 29 / 62 | 126 / 168; 32 / 46 | pending (slides being scanned) | pending (slides being scanned) | pending (slides being scanned) |

### Table: their matrix, NDBE pre-event samples

Each cell: fold-stratified IPCW AUROC [95% patient-bootstrap CI]; pooled IPCW AUROC [CI]. The Pathology grade row is identical for both CNV sources.

|  | Internal 1-year | Internal 3-year | Internal 5-year | ACE-B 1 | ACE-B 3 | ACE-B 5 |
|---|---|---|---|---|---|---|
| Pathology grade (raw score) | not estimable (grade constant: all NDBE) | not estimable (grade constant: all NDBE) | not estimable (grade constant: all NDBE) | pending | pending | pending |
| CNV (replication) | 0.873 [0.716, 0.951]; pooled 0.873 [0.761, 0.948] | 0.775 [0.642, 0.875]; pooled 0.772 [0.659, 0.878] | 0.752 [0.636, 0.839]; pooled 0.763 [0.654, 0.859] | pending | pending | pending |
| WSI | 0.727 [0.542, 0.844]; pooled 0.731 [0.575, 0.865] | 0.756 [0.631, 0.846]; pooled 0.780 [0.684, 0.876] | 0.714 [0.593, 0.778]; pooled 0.744 [0.651, 0.824] | pending | pending | pending |
| Early fusion | 0.884 [0.753, 0.942]; pooled 0.889 [0.802, 0.952] | 0.802 [0.673, 0.895]; pooled 0.826 [0.727, 0.918] | 0.752 [0.607, 0.843]; pooled 0.788 [0.700, 0.871] | pending | pending | pending |
| Inter fusion | 0.866 [0.657, 0.934]; pooled 0.881 [0.783, 0.943] | 0.801 [0.657, 0.904]; pooled 0.812 [0.692, 0.924] | 0.758 [0.616, 0.860]; pooled 0.770 [0.654, 0.873] | pending | pending | pending |
| Late fusion | 0.869 [0.748, 0.927]; pooled 0.870 [0.782, 0.932] | 0.806 [0.677, 0.900]; pooled 0.823 [0.728, 0.920] | 0.769 [0.652, 0.840]; pooled 0.792 [0.707, 0.865] | pending | pending | pending |
| n cases / n controls (samples; patients) | 12 / 334; 9 / 69 | 61 / 192; 25 / 59 | 79 / 111; 26 / 39 | pending (slides being scanned) | pending (slides being scanned) | pending (slides being scanned) |

### Table: package features, all pre-event samples

Each cell: fold-stratified IPCW AUROC [95% patient-bootstrap CI]; pooled IPCW AUROC [CI]. The Pathology grade row is identical for both CNV sources.

|  | Internal 1-year | Internal 3-year | Internal 5-year | ACE-B 1 | ACE-B 3 | ACE-B 5 |
|---|---|---|---|---|---|---|
| Pathology grade (raw score) | 0.694 [0.566, 0.797]; pooled 0.697 [0.578, 0.808] | 0.543 [0.445, 0.634]; pooled 0.554 [0.461, 0.650] | 0.524 [0.434, 0.613]; pooled 0.535 [0.449, 0.623] | pending | pending | pending |
| CNV (replication) | 0.790 [0.663, 0.873]; pooled 0.805 [0.714, 0.895] | 0.757 [0.623, 0.820]; pooled 0.779 [0.692, 0.850] | 0.780 [0.640, 0.852]; pooled 0.796 [0.693, 0.878] | pending | pending | pending |
| WSI | 0.771 [0.631, 0.846]; pooled 0.782 [0.668, 0.869] | 0.788 [0.659, 0.866]; pooled 0.817 [0.731, 0.894] | 0.760 [0.661, 0.819]; pooled 0.786 [0.714, 0.856] | pending | pending | pending |
| Early fusion | 0.822 [0.689, 0.886]; pooled 0.836 [0.760, 0.900] | 0.790 [0.656, 0.855]; pooled 0.814 [0.724, 0.887] | 0.791 [0.664, 0.863]; pooled 0.811 [0.712, 0.890] | pending | pending | pending |
| Inter fusion | 0.786 [0.650, 0.857]; pooled 0.802 [0.719, 0.877] | 0.799 [0.683, 0.865]; pooled 0.822 [0.749, 0.890] | 0.787 [0.686, 0.851]; pooled 0.803 [0.720, 0.871] | pending | pending | pending |
| Late fusion | 0.838 [0.720, 0.893]; pooled 0.852 [0.782, 0.909] | 0.817 [0.685, 0.887]; pooled 0.842 [0.760, 0.912] | 0.818 [0.698, 0.878]; pooled 0.839 [0.760, 0.906] | pending | pending | pending |
| n cases / n controls (samples; patients) | 29 / 449; 14 / 72 | 99 / 277; 29 / 62 | 126 / 168; 32 / 46 | pending (slides being scanned) | pending (slides being scanned) | pending (slides being scanned) |

### Table: package features, NDBE pre-event samples

Each cell: fold-stratified IPCW AUROC [95% patient-bootstrap CI]; pooled IPCW AUROC [CI]. The Pathology grade row is identical for both CNV sources.

|  | Internal 1-year | Internal 3-year | Internal 5-year | ACE-B 1 | ACE-B 3 | ACE-B 5 |
|---|---|---|---|---|---|---|
| Pathology grade (raw score) | not estimable (grade constant: all NDBE) | not estimable (grade constant: all NDBE) | not estimable (grade constant: all NDBE) | pending | pending | pending |
| CNV (replication) | 0.820 [0.643, 0.908]; pooled 0.826 [0.700, 0.913] | 0.738 [0.609, 0.827]; pooled 0.749 [0.646, 0.851] | 0.753 [0.624, 0.836]; pooled 0.758 [0.636, 0.859] | pending | pending | pending |
| WSI | 0.727 [0.542, 0.844]; pooled 0.731 [0.575, 0.865] | 0.756 [0.631, 0.846]; pooled 0.780 [0.684, 0.876] | 0.714 [0.593, 0.778]; pooled 0.744 [0.651, 0.824] | pending | pending | pending |
| Early fusion | 0.822 [0.653, 0.891]; pooled 0.830 [0.734, 0.902] | 0.761 [0.632, 0.848]; pooled 0.776 [0.663, 0.883] | 0.745 [0.585, 0.842]; pooled 0.756 [0.631, 0.860] | pending | pending | pending |
| Inter fusion | 0.775 [0.610, 0.849]; pooled 0.788 [0.683, 0.885] | 0.798 [0.668, 0.885]; pooled 0.819 [0.729, 0.904] | 0.772 [0.624, 0.864]; pooled 0.792 [0.692, 0.877] | pending | pending | pending |
| Late fusion | 0.830 [0.697, 0.889]; pooled 0.837 [0.745, 0.902] | 0.779 [0.657, 0.876]; pooled 0.798 [0.702, 0.895] | 0.769 [0.647, 0.837]; pooled 0.785 [0.690, 0.868] | pending | pending | pending |
| n cases / n controls (samples; patients) | 12 / 334; 9 / 69 | 61 / 192; 25 / 59 | 79 / 111; 26 / 39 | pending (slides being scanned) | pending (slides being scanned) | pending (slides being scanned) |

### Paired Δ of the Pathology grade row

All pre-event samples; same bootstrap draws; unadjusted swap-permutation p (the row is outside the max-T family). NDBE only: not estimable.

| CNV source | Horizon | Metric | Grade AUROC [CI] | Δ vs L-CNV [CI] (p) | Δ vs L-LATE [CI] (p) |
|---|---|---|---|---|---|
| their matrix | 1 y | fold-stratified | 0.694 [0.566, 0.797] | -0.116 [-0.326, +0.084] (p 0.2409) | -0.160 [-0.296, -0.006] (p 0.0695) |
| their matrix | 1 y | pooled | 0.697 [0.578, 0.808] | -0.118 [-0.314, +0.064] (p 0.2219) | -0.172 [-0.311, -0.047] (p 0.0525) |
| their matrix | 3 y | fold-stratified | 0.543 [0.445, 0.634] | -0.225 [-0.344, -0.081] (p 0.005) | -0.288 [-0.374, -0.181] (p 0.001) |
| their matrix | 3 y | pooled | 0.554 [0.461, 0.650] | -0.222 [-0.353, -0.082] (p 0.0075) | -0.301 [-0.402, -0.210] (p 0.001) |
| their matrix | 5 y | fold-stratified | 0.524 [0.434, 0.613] | -0.254 [-0.354, -0.128] (p 0.0035) | -0.297 [-0.382, -0.188] (p 0.0015) |
| their matrix | 5 y | pooled | 0.535 [0.449, 0.623] | -0.256 [-0.372, -0.129] (p 0.004) | -0.309 [-0.400, -0.218] (p 0.001) |
| package features | 1 y | fold-stratified | 0.694 [0.566, 0.797] | -0.095 [-0.251, +0.078] (p 0.2934) | -0.144 [-0.267, +0.008] (p 0.0975) |
| package features | 1 y | pooled | 0.697 [0.578, 0.808] | -0.108 [-0.280, +0.051] (p 0.2424) | -0.155 [-0.291, -0.027] (p 0.0745) |
| package features | 3 y | fold-stratified | 0.543 [0.445, 0.634] | -0.214 [-0.320, -0.065] (p 0.006) | -0.274 [-0.355, -0.171] (p 0.001) |
| package features | 3 y | pooled | 0.554 [0.461, 0.650] | -0.226 [-0.340, -0.102] (p 0.005) | -0.288 [-0.384, -0.200] (p 0.001) |
| package features | 5 y | fold-stratified | 0.524 [0.434, 0.613] | -0.256 [-0.355, -0.119] (p 0.003) | -0.293 [-0.378, -0.179] (p 0.001) |
| package features | 5 y | pooled | 0.535 [0.449, 0.623] | -0.261 [-0.381, -0.135] (p 0.004) | -0.304 [-0.402, -0.211] (p 0.001) |

### Supplement: L-CLIN and demographics only

**Note.** The discovery cohort was matched on age, sex and Barrett's segment length (Killcoyne 2020, Supplementary Table 1), so demographic predictors are not expected to discriminate; the values below sit at or under 0.5, and under the pooled metric they also carry the stratified-CV fold-prevalence artefact (`docs/paper_horizon_answers.md`). L-CLIN = L2 logistic on grade, age at BE diagnosis, sex and Prague M; demographics only = the same without grade (`scripts/paper_plan/ha_clin.py`).

all pre-event samples (identical for both CNV sources):

|  | Internal 1-year | Internal 3-year | Internal 5-year | ACE-B 1 | ACE-B 3 | ACE-B 5 |
|---|---|---|---|---|---|---|
| L-CLIN | 0.621 [0.456, 0.768]; pooled 0.604 [0.436, 0.754] | 0.457 [0.349, 0.577]; pooled 0.430 [0.313, 0.553] | 0.490 [0.392, 0.593]; pooled 0.458 [0.362, 0.565] | pending | pending | pending |
| Demographics only | 0.383 [0.268, 0.528]; pooled 0.348 [0.205, 0.519] | 0.364 [0.278, 0.485]; pooled 0.294 [0.181, 0.435] | 0.385 [0.294, 0.510]; pooled 0.313 [0.192, 0.464] | pending | pending | pending |
| n cases / n controls (samples; patients) | 29 / 449; 14 / 72 | 99 / 277; 29 / 62 | 126 / 168; 32 / 46 | pending (slides being scanned) | pending (slides being scanned) | pending (slides being scanned) |

NDBE pre-event samples (identical for both CNV sources):

|  | Internal 1-year | Internal 3-year | Internal 5-year | ACE-B 1 | ACE-B 3 | ACE-B 5 |
|---|---|---|---|---|---|---|
| L-CLIN | 0.314 [0.178, 0.499]; pooled 0.260 [0.099, 0.462] | 0.344 [0.249, 0.485]; pooled 0.268 [0.154, 0.427] | 0.433 [0.301, 0.585]; pooled 0.342 [0.197, 0.515] | pending | pending | pending |
| Demographics only | 0.348 [0.208, 0.530]; pooled 0.331 [0.148, 0.547] | 0.393 [0.297, 0.528]; pooled 0.336 [0.208, 0.495] | 0.441 [0.337, 0.581]; pooled 0.389 [0.252, 0.555] | pending | pending | pending |
| n cases / n controls (samples; patients) | 12 / 334; 9 / 69 | 61 / 192; 25 / 59 | 79 / 111; 26 / 39 | pending (slides being scanned) | pending (slides being scanned) | pending (slides being scanned) |

**Method.** Score = ordinal grade (NDBE 0, ID 1, LGD 2), constant across repeats; pooled metric over all case–control pairs; fold-stratified metric over same-fold pairs in each repeat's outer folds, averaged over 10 repeats; IPCW weights from the reverse Kaplan–Meier, re-estimated per bootstrap draw. **Sources.** `feasibility/paper_plan/killcoyne_mm/set_C.csv` (grade), `horizons/samples.csv` (times, events), `cv/preds/` (folds, L-CNV, L-IMG).
**Caveats.** (1) Ties: with three grade levels most case–control pairs are tied and count ½, which pulls the row toward 0.5. (2) Design caveat: AUROCs only; no absolute risk, calibration or PPV. (3) Pre-event samples contain no HGD/IMC (they are excluded by the endpoint definition), so the grade spans only NDBE, ID and LGD.


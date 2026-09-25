| digest location | CI(s) | generating script | resampling unit | n resamples | seed |
|---|---|---|---|---|---|
| summary row 2, §1 table (rep01/rep02 deltas vs image) | e.g. +0.043 [+0.014, +0.071], +0.042 [+0.019, +0.069] | `scripts/numbers/num_swg_rep02.py` | patient (max over rows; `groupby("patient_id")`) | 2,000 | 0 |
| §1 permutation / selection-adjusted p | 0.0025 / 0.001; 0.225 / 0.024 | `scripts/numbers/num_swg_rep02_selection.py` | patient labels permuted | 2,000 | 0 |
| summary row 3, §2 table (spec at sens 0.95, Brier deltas), recalibration Brier CI | e.g. −0.061 [−0.095, −0.027]; [−0.079, −0.007] | `scripts/numbers/num_swg_robustness.py` | patient (items 14–16); item 17 windows: rows resampled by patient cluster | 2,000 | 0 |
| summary row 4 | 0.750 / 0.756 / 0.748 (CIs in JSON) | `scripts/numbers/num_cnvtext_cis.py` | patient (max risk over rows) | 2,000 | 0 |
| §3 T4 rows | 0.874 [0.850, 0.896]; 0.686 [0.610, 0.767] | `scripts/numbers/num_t4_treatment_split.py` | ERIN case rows resampled by patient cluster (`anon_id`) | 2,000 | 0 |
| §3 T3a/T3b biopsy-only | 0.801 [0.751, 0.848]; Δ 0.228 [0.156, 0.298]; 0.822 [0.764, 0.874]; Δ 0.226 [0.138, 0.317] | `scripts/erin_fusion/assemble_bio.py` | ERIN units resampled by patient cluster (`anon_id`) | 2,000 | 0 |
| §3 grade model rows | 0.871 [0.842, 0.897]; 0.865 [0.831, 0.896] | `scripts/numbers/num_grade_within_biopsy.py` | slides resampled by patient cluster (`anon_id`) | 2,000 | 0 |
| §5 P32 ERIN field table (13 CIs) | e.g. grade LGD+ 0.861 [0.840, 0.882] | `scripts/projects/p32_fields_from_image.py` | cases resampled by patient cluster (`anon_id`) | **1,000** (deviates from the 2,000 convention) | 0 |
| §5 P32 SWG arm table, controls table, overlap tables | e.g. +0.050 [+0.015, +0.089]; +0.063 [+0.020, +0.107] | `scripts/projects/p32_swg_fuse.py`, `p32_fuse_controls.py`, `p32_checks.py`, subgroup split in the 25 Sep session | patient-level vectors (max over rows) resampled | 2,000 | 0 |
| §5 P33 table | e.g. T3a 0.800 [0.753, 0.847] | `scripts/projects/p33_tasks.py` | units resampled by patient cluster (`anon_id`) | 2,000 | 0 |
| §4 anchors, §5 P31 kappas, row 20 intervals | no CIs (agreement statistics, Mann-Whitney p) | `task_anchor_eval.py`, `p31_agreement.py`, `fig_db_interval_first_lgd.py` | n/a | n/a | n/a |

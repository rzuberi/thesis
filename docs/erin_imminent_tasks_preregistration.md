# Pre-registration — ERIN "imminent dysplasia" task set (image + text), 21 Sep 2026, 20:15
Follows the feasibility stop of `docs/erin_progression_fusion_preregistration.md`: 3-year progression is impossible from ERIN images (all scanned slides are 2022–2025). This file pre-registers every task the metadata CAN support in that window. Task tables: `scripts/erin_fusion/build_tasks.py` → `feasibility/erin_fusion/tasks/*.csv` (counts below, computed before any training). Nothing here changes after the first job is submitted.

## Tasks (input = an imaged report graded NDBE or IND unless stated; bag = all H&E slides of that report's case, tiles pooled)
| Task | Unit | Label | n | pos | neg | patients | status |
|---|---|---|---|---|---|---|---|
| T1 | first NDBE/IND report per patient | HGD/CANCER within 365 d; neg needs ≥365 d clean follow-up | 48 | 18 | 30 | 48 | feasibility only (<30 pos) |
| **T2a (primary)** | every imaged NDBE/IND report with follow-up (landmark) | **LGD or worse within 365 d**; neg needs ≥365 d clean follow-up | 185 | 44 | 141 | 156 | interpretable |
| T2b | landmark | HGD or worse within 365 d | 183 | 30 | 153 | 155 | interpretable (borderline) |
| T2c | landmark | next report is LGD or worse (any gap) | 389 | 45 | 344 | 289 | interpretable |
| T3a | benign-section SLIDE (section NDBE/NORMAL, v2 labels) | case-max LGD+ elsewhere in the same case (field effect) | 1,274 | 146 | 1,128 | 1,056 | interpretable; image-only |
| T3b | benign-section slide | case-max HGD+ elsewhere | 1,274 | 90 | 1,184 | 1,056 | interpretable; image-only |
| T4 | imaged NDBE/IND report with earlier reports | prior LGD+ anywhere in the patient's history | 1,147 | 518 | 629 | 874 | interpretable; image-only |
Landmark tasks have several samples per patient; folds are patient-disjoint and bootstraps resample patients.

## Arms
a. baseline: logistic regression on grade (NDBE vs IND; for T3 section NORMAL vs NDBE) + age. b. text: logistic regression on `nomic-embed-text` embedding (768-d) of the report (T1, T2 only — for T3/T4 the label is derived from report text or history, so text would leak). c. image: `abmil_clf.train_abmil_clf_fold`, ERIN-grading defaults (25 epochs, lr 1e-4, mb 32, MAX_TILES cap; ≤1,500 tiles kept per slide at load), no tuning. d. late_mean: fold-local z-scored OOF of b and c averaged (T1, T2 only).

## Evaluation
`patient_folds` (5 folds, seed 0), seeds 0/1/2 averaged, patient-clustered 2,000-replicate bootstrap; per arm AUROC, AUPRC, Brier, spec@sens 0.95, spec@sens 1.0, sens@spec 0.80; paired deltas d−max(b,c), b−a, c−a (T1/T2) and c−a (T3/T4); 50 label permutations of arm c AND arm d on T2a (image retrained per permutation, one seed); tile-count confound for c on every task; selection-adjusted permutation over {b, c, d} only if d beats max(b, c) with CI excluding zero.

## Rules
- T1 is reported as feasibility only; no comparison interpreted.
- T2a primary claim requires d − max(b,c) CI > 0 AND selection-adjusted p < 0.05; otherwise "no demonstrated fusion gain".
- c − a with CI > 0 on T3 = "benign-looking tissue in a case with dysplasia is distinguishable" (field effect); on T4 = "prior dysplasia leaves a visible trace"; on T2 = "imminent dysplasia is visible before it is diagnosed". Any of these is reported with the caveat that ERIN follow-up is ≤ 3 years and index reports are 2022–2025.
- Stop rule: nothing changes after submission; deviations go to the report.

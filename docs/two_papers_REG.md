# Two papers, agent REG: frozen bundle and registration draft

Agent REG under `paper/two_papers/RUN_RULES.md` (21 October 2026). No ACE-B file is opened at any point.

## Plan

1. **Freeze.** Bundle on the cluster at `feasibility/paper_plan/killcoyne_mm/two_papers_REG/frozen/`:
   - **Models.** L-IMG, L-CNV and L-LATE refitted on all of set C (676 samples, 80 patients; the 571 pre-event samples of 75 patients are the evaluation population) with the existing recipe: glmnet α 0.9, `standardize = FALSE`, λ = class-error minimum of the 10 × 5 patient-grouped CV on all training patients (the same inner CV that picks λ inside each outer fold). Two copy-number flavours: their shipped matrix (`kc_freeze.R`, the Paper 1 L-CNV) and package features from reads (`kv_freeze.R`, needed wherever copy number has to be computed from new reads: ACE-B and 4×). Both scripts are rerun unchanged into the bundle; the refit must be byte-identical to the committed `models/killcoyne_frozen_v1` and `models/killcoyne_frozen_pkg_v1`.
   - **Rules.** R49 gate; no-sequencing tier (mean-logit + EW memory, E9 `ml_mem`); light tier (EW memory of the R49-aligned gate score + copy-number certificate, round-9 A12); confirmatory tier (light + quiet-genome check, ps_oac of the two top-H&E samples at the cn90 bar, E9 `final`); R49 with package-feature L-LATE for ACE-B and 4×.
   - **How thresholds are chosen on all 75 patients.** The round-9 operating rule and candidate families are run unchanged (the E9 module body is executed), with all 75 patients as training patients and the outer out-of-fold predictions of one repeat in the role inner out-of-fold predictions play inside a fold. Done for each of the 10 repeats, then frozen in sequence: gate cut-offs (median), hyper-parameters (mode), quiet cut (median), thresholds (median), check bar (median).
   - **Also in the bundle:** label-free scanner reset (class-wise quantiles of the out-of-fold L-IMG for quantile mapping at a registered progressor share), the Paper 1 patient-score aggregation, a standalone scorer (`tp_reg_score.py`), code copies with the commit, and a MANIFEST with the sha256 of every file. Only the MANIFEST is committed (`results/paper_final/two_papers_REG/frozen_MANIFEST.json`).
   - **Checks.** Smoke: the selection code on the 100 stored folds must reproduce E9 (R49 31.1 / 31.8, memory 30.7 / 23.6, A12 30.5 / 21.5, final 30.5 / 17.2, mean-logit + memory 31.0 / 26.6) and pick the same candidates in every fold. Verify: refit files identical to the committed bundles; in-sample AUROC recomputed from the frozen coefficients equals `model_info.json`; the standalone scorer reproduces the engine flag for flag on all 10 repeats; apparent (non-nested, optimistic) numbers of the frozen rules reported next to the nested ones.
2. **Registration draft** `paper/two_papers/REGISTRATION_draft.md` (one document, a section per paper and per dataset), for Rehan to post on OSF.
3. **Email draft** `paper/two_papers/EMAIL_killcoyne_draft.md` to Sarah Killcoyne and Rebecca Fitzgerald. Nothing is sent.

Scripts: `scripts/paper_plan/tp_reg_freeze.py` (TASK = nested | freeze | verify | manifest), `scripts/paper_plan/tp_reg_score.py`. Slurm prefix `tpreg`. Aggregates: `results/paper_final/two_papers_REG/`.

## Results

(below, after the runs)

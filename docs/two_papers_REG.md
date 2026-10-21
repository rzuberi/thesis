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



### Smoke (selection code on the 100 stored folds)

`results/paper_final/two_papers_REG/nested_smoke.json`. The selection function used for the freeze, run in fold mode, reproduces E9 exactly and picks the same candidate as E9 in all 100 folds for every family.

| Rule | Caught / 32 | NP flagged / 43 | Samples per patient | E9 |
|---|---|---|---|---|
| R49 | 31.1 | 31.8 | 1.94 | 31.1 / 31.8 / 1.94 |
| Memory (gate score, EW) | 30.7 | 23.6 | 1.94 | 30.7 / 23.6 / 1.94 |
| Light tier (A12) | 30.5 | 21.5 | 1.94 | 30.5 / 21.5 / 1.94 |
| Confirmatory (A12 + check, cn90) | 30.5 | 17.2 | 3.82 | 30.5 / 17.2 / 3.82 |
| Tier 0 (mean-logit + memory) | 31.0 | 26.6 | 0 | 31.0 / 26.6 / 0 |
| Mean-logit gate + memory + certificate | 30.3 | 20.1 | 1.43 | 30.3 / 20.1 / 1.43 |

### Frozen bundle

Bundle `feasibility/paper_plan/killcoyne_mm/two_papers_REG/frozen/` (cluster), 29 files, **bundle SHA-256 `17828c1a5fddceb4e1825c81b4295a49b798b9bd2f670c7a2f13f87304c1105f`**, frozen 2026-10-21T17:56:47; freeze code commit 7e9dc92, code copies at cd60032. Per-file hashes: `results/paper_final/two_papers_REG/frozen_MANIFEST.json`.

**Models.** The refit of `kc_freeze.R` and `kv_freeze.R` into the bundle is byte-identical to the committed `models/killcoyne_frozen_v1` (their matrix) and `models/killcoyne_frozen_pkg_v1` (package features), coefficient and scaling files alike. They are trained on set C (676 samples, 80 patients), because that is the recipe used inside every outer fold (training rows include post-event samples and the 5 patients without pre-event samples); the 571 pre-event samples of 75 patients are the evaluation population. In-sample AUROC recomputed from the frozen coefficients equals `model_info.json` (L-IMG 0.998, L-CNV 0.996, L-LATE 1.000; optimistic by construction).

**Rules** (all 75 patients as training patients; per repeat, then median / mode in sequence; `rules.json`, values rounded):

| Rule | Frozen values | Stability over the 10 repeats |
|---|---|---|
| R49 gate | t_low 0.0322, c\* 0.5775, t_seq 0.2330 (package flavour t_seq 0.2346) | t_low 0.016–0.058, c\* 0.527–0.647, t_seq 0.193–0.269; tb_frozen medians 0.042 / 0.589 / 0.233 |
| Tier 0, no sequencing | mean-logit endoscopy score, EW half-life 4 y, threshold −1.737 (logit) | h = 4 in 10/10 repeats; threshold −2.54 to −1.37 |
| Light tier | EW of the R49-aligned gate score, h 4 y; certificate: quiet cut = p75 of training NP middle-band top-sample logit L-CNV = −0.561, −1.0 logit for 4 y; threshold −0.018 | modal tuple (4, p75, 1.0, 4 y) in 4/10 repeats (5 tuples seen); threshold −1.10 to +0.54 |
| Confirmatory tier | light tier + quiet-genome check, bar ps_oac 0.0599 | bar 0.0599 in 8/10, 0.0609 in 2/10 |

R49's detection target D was 29–32 progressor patients across repeats.

**Apparent (OPTIMISTIC) numbers of the frozen rules** on the same out-of-fold predictions (all patients, repeat mean), next to the nested ones:

| Rule | Apparent caught / NP flagged / samples per patient | Nested (held-out) |
|---|---|---|
| R49 | 31.2 / 31.5 / 1.99 | 31.1 / 31.8 / 1.94 |
| R49, package flavour | 31.1 / 33.0 / 1.99 | — |
| Tier 0 | 30.6 / 24.5 / 0 | 31.0 / 26.6 / 0 |
| Light | 30.9 / 22.9 / 1.99 | 30.5 / 21.5 / 1.94 |
| Confirmatory | 30.9 / 19.1 / 3.94 | 30.5 / 17.2 / 3.82 |

The frozen single thresholds give apparent numbers close to the nested ones, with no sign that the frozen versions are better than the nested estimates (the apparent non-progressor counts are slightly higher, because a median threshold is not tuned to any one repeat).

**Standalone scorer.** `tp_reg_score.py` was written without the engine. On all 10 repeats it reproduces the engine's flags for R49, R49 package, tier 0, light and confirmatory (0 mismatches), the samples sequenced (0 mismatches) and the tier-0 and light scores (max |Δ| < 1e-9).

**Development estimates of the registered Paper 1 patient score** (sample logit → endoscopy mean → patient max; nested out-of-fold, fold-stratified, repeat mean; context only): L-IMG 0.854 (equal to E3's mean-logit patient AUROC), L-CNV their 0.826, L-CNV package 0.852, L-LATE their 0.893, L-LATE package 0.914.

**Scanner reset.** Class-wise quantiles (1,001) of the pooled out-of-fold L-IMG; quantile mapping at a registered π = 15/117; monotone (checked).

### Choices made here that Rehan may want to change before posting

1. **Light tier = memory + certificate on the R49 gate score (A12, 1.94 samples per patient)**, so the tiers nest: confirmatory = light + check. E9 had suggested the mean-logit gate + memory + certificate (1.43 samples per patient, 30.3 / 20.1) as tier 1. Swapping it needs a refreeze (about 10 minutes).
2. **Confirmatory tier = the final rule on the R49 gate score at the fixed cn90 bar** (as briefed), not the mean-logit full stack (30.3 / 16.2) or the in-fold bar (30.4 / 16.4).
3. **ACE-B copy number = package features** (`models_pkg`), the only flavour computable from new reads; the R49 gate on ACE-B uses the package t_seq.
4. **Patient score for the Paper 1 ACE-B primary = max over endoscopies of the endoscopy mean logit** (mean logit when one endoscopy); max sample probability as sensitivity.
5. **Scanner reset π = 15/117**, fixed from the cohort description.
6. The light-tier choice is unstable across repeats (modal tuple 4/10) and its threshold spans −1.1 to +0.5 logit: the frozen light and confirmatory tiers are less settled than tier 0 (h = 4 in 10/10). This is reported in the registration.

### Drafts

- `paper/two_papers/REGISTRATION_draft.md` (local, not committed; `paper/` is never committed).
- `paper/two_papers/EMAIL_killcoyne_draft.md` (not sent).

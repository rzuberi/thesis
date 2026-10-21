# Two papers, agent CLN: Paper 2 tiers on the clean-tile L-IMG, and frozen bundle v2

21 October 2026. Rules: `paper/two_papers/RUN_RULES.md`. Trigger: agent ART (`docs/two_papers_ART.md`) showed that L-IMG partly reads artefact tiles (glass, coverslip edge, pen, blur); the clean-tile L-IMG (same recipe, folds and nested λ) falls from 0.847 to 0.811 and will likely become the primary image model. Paper 2's tiers must be re-established on it before the registration is posted. Inputs (read-only): ART's refits (`killcoyne_mm/two_papers_ART/refit/{clean,rand}`), ART's per-tile QC (`qc_all.parquet`) and features, P2S's clinical table (`killcoyne_mm/two_papers_P2S/clin.npz`), REG's bundle v1 (untouched). No ACE-B file is opened.

## Plan

**Models.** Three L-IMG versions run through the same code: *published* (stored L-IMG), *clean* (ART clean-tile refit; L-LATE = (L-CNV + clean L-IMG) / 2) and *random-removal control* (ART `rand`: the same number of tiles removed at random). Swapping is done at the loader only: `load("their")` inside the round-8 setup (E2 `build`, so R49 gate cut-offs, middle band, top-H&E samples, certificate quiet cut and check bars are all re-derived on the swapped model in the training folds), and E3 `variant("mlogit:<model>")` for the mean-logit tiers, exactly as ART's `tp_art_gate.py` and P2S's `state_ml`.

**Code reuse.** `scripts/paper_plan/tp_cln_main.py` executes `tp_p2s_main.py` up to its dispatch (which executes `ex_e7_stress.py`, `ex_e2_veto.py`, `rv9_falseflags.py` and the E3 helper section), swaps the model, and then runs P2S's own task branches (`rules`, `landmark`, `design`, `per1000`) with row-level and aggregate paths redirected to the CLN space. The only additions: the mean-logit full stack (E9 `ml_final`: A12 on the mean-logit gate + quiet-genome check, cn90 bar; plus its fold-internal bar via E7 `infold_bar`) and a cross-model `compare` task (paired patient bootstrap, RandomState(0), 2,000 draws; E7 truncation draws RandomState(7001) for equal exposure).

1. **Every Paper 2 rule held out, per model:** R49 gate, H&E alone (P1 90%), memory (A1), memory + certificate (A12, light), final rule (A12 + check, cn90 bar) and its fold-internal bar, mean-logit + memory (tier 0), mean-logit full stack (and its fold-internal bar). Caught / 32, NP flagged / 43, samples sequenced per patient; paired CIs for clean − published, clean − random control, and each tier − R49 on the same model.
2. **Equal exposure** (E7 truncation, frozen per-fold rules) per tier and model; **landmark** AUROC gain of memory (mean-logit memory − single endoscopy, gate memory − single); **safety** (never flagged to date + two consecutive lows: progressors de-escalated before the event and at the last pre-event endoscopy); **per 1,000 patient-years** in the de-escalated group at 0.45%/yr with exact limits; **lead time** > 2 y / > 4 y. Compared with P2S.
3. **Random-tile-removal control** for every tier (in particular the confirmatory tier): clean − random isolates the artefact effect from the tile count.
4. **Bundle v2** at `killcoyne_mm/two_papers_REG/frozen_v2_clean/` with REG's freeze procedure (`tp_reg_freeze.py` executed with only the model loader and output paths changed): tile QC (ART's flag with fixed thresholds, including the blur cut 132.54 as a constant) as the first pipeline step; clean-tile L-IMG / L-CNV / L-LATE refitted on all of set C (`kc_freeze.R` / `kv_freeze.R` copies with the image input switched; smoke: the copies reproduce v1 byte for byte on the old input); scanner reset; one rule per tier. Verification as REG: REG's independent scorer reproduces the engine flag for flag (0 mismatches), an independent QC + embedding function reproduces ART's clean features, in-sample AUROC equals `model_info.json`. MANIFEST with sha256 committed as `results/paper_final/two_papers_CLN/frozen_v2_MANIFEST.json`. v1 untouched.
5. **Summary table:** strongest tier on raw counts, equal exposure and safety, and what Paper 2 should lead with.

**Smoke first:** with the published L-IMG the pipeline must reproduce P2S / E9 exactly (R49 31.1 / 31.8, P1 31.1 / 36.0, A1 30.7 / 23.6, A12 30.5 / 21.5, final 30.5 / 17.2, fold-internal 30.4 / 16.4, tier 0 31.0 / 26.6, mean-logit full stack 30.3 / 16.2) and, with the clean L-IMG, ART's clean numbers (R49 31.3 / 32.8, A1 30.7 / 25.1, A12 30.5 / 23.5, tier 0 31.1 / 29.7).

Scripts `scripts/paper_plan/tp_cln_*.py` / `.R`; aggregates `results/paper_final/two_papers_CLN/`; row-level `killcoyne_mm/two_papers_CLN/`; Slurm prefix `tpcln`. The cluster checkout cannot be pulled (P2N's untracked scripts block it; they are not touched), so CLN's scripts run from copies in `killcoyne_mm/two_papers_CLN/code/` with absolute paths, as ART's did.

---

## Results

(pending)

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

Aggregates: `results/paper_final/two_papers_CLN/` (`<model>/{rules,landmark,design,per1000}.json` for model = stored (published L-IMG), clean, rand; `compare.json`; `freeze_v2/`; `frozen_v2_MANIFEST.json`). Tables rendered by `scripts/paper_plan/tp_cln_render.py`. Cluster campaigns `tpclnr` (rules), `tpclne` + `tpclnc` (P2S analyses per model, cross-model compare), `tpclnm` (frozen models), `tpclnf` / `tpclnv` / `tpclnx` (freeze, verify, manifest); all CPU, no slide pixels read. Held-out patients throughout; every threshold, half-life, certificate setting, gate cut-off and check bar chosen on training patients of each outer fold, using that model's own inner out-of-fold predictions. Intervals are paired patient-bootstrap 95% CIs (2,000 draws, RandomState(0)), the same draws for all three models. EXPLORATORY: the rule families come from the ~650-variant search.

**The tiers survive artefact removal, but not equally. The sequencing tiers keep almost all of their advantage over the per-endoscopy gate (mean-logit full stack −14.9 non-progressors vs R49 on the clean model, −12.2 at equal exposure). The no-sequencing tier does not: its saving over the gate falls from 5.2 to 3.1 non-progressors [−6.8, +0.4], and at equal exposure to −2.0 [−5.7, +1.6]. The random-tile control shows that this loss is specific to artefact tiles (clean − random +2.8 [+0.4, +5.3]).**

### Summary

- **Raw counts (clean model).** R49 31.3 / 32.8 / 2.16 (caught / NP flagged / samples per patient). Tier 0 (mean-logit + memory) 31.1 / 29.7 / 0. Light tier: R49-gate version 30.5 / 23.5 / 2.16, mean-logit version 30.3 / 21.9 / 1.70. Confirmatory: final rule 30.3 / 19.8 / 4.06 (fold-internal bar 30.2 / 18.6); mean-logit full stack 30.2 / 17.9 / 3.41 (fold-internal 30.0 / 16.4).
  - Against the published L-IMG, every tier flags 1.5–3.1 more non-progressors. The CI excludes 0 for tier 0 (+3.1), the final rule (+2.6) and its fold-internal bar (+2.2); the mean-logit full stack moves +1.7 [−0.2, +3.9].
  - Progressors caught do not change (|Δ| ≤ 0.3).
  - Samples sequenced rise by 0.2–0.3 per patient, because more endoscopies fall in the gate's middle band.
- **Artefact versus tile count (random-removal control).** Clean − random, NP flagged:
  - tier 0: +2.8 [+0.4, +5.3];
  - final rule: +1.8 [−0.3, +4.0];
  - mean-logit full stack: +0.5 [−1.4, +2.7];
  - R49: −0.5.

  Artefact tiles were helping mainly the no-sequencing tier: its saving over R49 shrinks by 3.3 [0.5, 6.1] relative to the random control. Copy number (gate, certificate, check) makes the sequencing tiers largely immune.
- **Equal exposure (E7 truncation), clean model.**
  - Rule − R49, NP flagged: tier 0 −2.0 [−5.7, +1.6] (published −3.6 [−6.7, −0.6]); final rule −10.8 [−14.4, −7.7] (−11.3); mean-logit full stack −12.2 [−15.8, −9.0] (−12.0); mean-logit light −8.6 [−11.4, −6.0].
  - Tier 0's own memory gain (mean-logit memory − mean-logit single endoscopy) is −1.5 [−2.4, −0.7] (published −2.3 [−3.7, −1.0]). It holds, at about two thirds of its size.
- **Landmark (history to date).**
  - The memory gain in landmark AUROC holds at "ever": +0.029 [0.010, 0.048] (published +0.026), equal exposure +0.025 [0.005, 0.044], patient-weighted +0.019 [0.003, 0.036]; ≤ 5 y +0.022 [0.004, 0.040].
  - At ≤ 5 y with equal exposure the gain is +0.014 [−0.004, 0.032]; the published version had +0.020 [−0.002, 0.045], so its CI also included 0.
- **Safety (two lows + no de-escalation after a flag), clean model.**
  - Progressors de-escalated at the last pre-event endoscopy: tier 0 0.3 (integer 0–1 per repeat; published 0.1, 0–1); final rule 1.0 (0–2); mean-logit full stack 1.0 (0–3); R49 0.2.
  - Missed (never flagged): tier 0 0.9 (0–2), final 1.7, mean-logit full stack 1.8; no progressor is missed in ≥ 5 of 10 repeats under any tier.
  - Per 1,000 patient-years in the de-escalated group at 0.45%/yr: tier 0 0.41 [0.10, 0.92], exact upper 2.36 (published 1.92); final 0.45, exact upper 1.74; mean-logit full stack 0.43 [0.15, 0.82], exact upper 1.61; R49 exact upper 3.08; grade + p53 3.70 [1.79, 6.43].
  - Only the confirmatory tiers keep the exact upper limit under the 2 per 1,000 bar.
- **Lead time, clean model.**
  - Endoscopies > 2 y before the event (24 progressors): tier 0 23.4 caught, mean-logit full stack 22.4, R49 23.3, grade + p53 14.0.
  - Endoscopies > 4 y before the event (20 progressors): tier 0 17.9, final 17.4, mean-logit full stack 17.6, R49 18.2, grade + p53 6.0.
  - The fold-internal-bar versions lose 1.7–1.9 progressors against R49 in the > 4 y window.
- **Mean-logit stack vs R49-gate stack.** Same model, clean:
  - confirmatory: −1.9 [−3.6, −0.4] non-progressors and −0.65 [−0.83, −0.46] samples per patient, for −0.1 caught;
  - light: −1.6 [−3.4, 0.0] non-progressors and −0.46 samples per patient.

  The mean-logit stack is never worse in any model, so bundle v2 freezes it for the light and confirmatory tiers.
- **Bundle v2.** It is at `killcoyne_mm/two_papers_REG/frozen_v2_clean/` and v1 is untouched. Verification:
  - the scorer reproduces the engine flag for flag (0 mismatches);
  - the independent QC / embedding function reproduces ART's clean features (max |Δ| 5e-8, the CSV rounding);
  - the model R scripts reproduce v1 byte for byte on the v1 input.

### Smoke checks

- **Published L-IMG through the CLN wrapper** reproduces P2S / E9 / REG exactly:
  - R49 31.1 / 31.8, P1 31.1 / 36.0, memory 30.7 / 23.6, light 30.5 / 21.5, final 30.5 / 17.2, fold-internal 30.4 / 16.4, tier 0 31.0 / 26.6, mean-logit light 30.3 / 20.1 / 1.43, mean-logit full stack 30.3 / 16.2 / 3.12;
  - 0 flag mismatches against E7's stored flags and E9's tier-0 sweep;
  - P2S's design and per1000 JSONs identical value for value (12,594 and 689 leaves);
  - landmark identical except 15 bootstrap leaves (third decimal of p-values, and the CI ends of the clinical comparators' patient-weighted NPV, which are unstable near empty cells); no tier estimate differs. The cause is not established; floating-point summation order on a different node type is the likely one;
  - equal exposure: tier 0 vs R49 −3.566 (P2S −3.6), final −11.299 (−11.3).
- **Clean L-IMG** reproduces ART's `gate.json`: R49 31.3 / 32.8, memory 30.7 / 25.1, light 30.5 / 23.5, tier 0 31.1 / 29.7.
- **Freeze wrapper on the published L-IMG** (`CLN_MODEL=stored`) reproduces bundle v1's rules.json:
  - R49, R49 package flavour and confirmatory values: identical;
  - tier 0 threshold and light threshold: equal to the last floating-point digit (|Δ| ≤ 6e-16).
- **Frozen-model R scripts** on the v1 input: all 13 model files byte-identical to `models/killcoyne_frozen_v1` and `killcoyne_frozen_pkg_v1`.

### 1. Every rule held out, three L-IMG versions

Caught of 32 / non-progressor patients flagged of 43 / samples sequenced per patient (repeat mean); Δ = paired patient-bootstrap difference in non-progressors flagged [95% CI] (caught Δ in the next column); bold = CI excludes 0.

| Rule | Published L-IMG | Clean-tile L-IMG | Random-removal control | Clean − published, NP | Clean − published, caught | Clean − random, NP | Clean: rule − R49, NP | Clean: rule − R49, caught |
|---|---|---|---|---|---|---|---|---|
| Per-endoscopy gate R49 | 31.1 / 31.8 / 1.94 | 31.3 / 32.8 / 2.16 | 31.3 / 33.3 / 2.01 | +1.0 [−0.8, 3.1] | +0.2 [0.0, 0.5] | −0.5 [−2.5, 1.7] | — | — |
| H&E alone (P1 90%) | 31.1 / 36.0 / 0.00 | 31.3 / 37.8 / 0.00 | 31.4 / 37.3 / 0.00 | +1.8 [0.0, 3.9] | +0.2 [−0.3, 0.9] | +0.5 [−1.6, 2.6] | **+5.0 [1.9, 8.5]** | +0.0 [−1.1, 1.1] |
| Memory (gate score) | 30.7 / 23.6 / 1.94 | 30.7 / 25.1 / 2.16 | 30.8 / 25.2 / 2.01 | +1.5 [−0.7, 3.9] | +0.0 [−0.8, 0.9] | −0.1 [−2.4, 2.4] | **−7.7 [−11.1, −4.5]** | **−0.6 [−1.2, −0.1]** |
| Memory + certificate (light, R49 gate) | 30.5 / 21.5 / 1.94 | 30.5 / 23.5 / 2.16 | 30.3 / 22.6 / 2.01 | +2.0 [−0.3, 4.3] | +0.0 [−0.7, 0.8] | +0.9 [−1.4, 3.3] | **−9.3 [−12.9, −5.9]** | **−0.8 [−1.6, −0.2]** |
| Confirmatory: final rule, cn90 bar | 30.5 / 17.2 / 3.82 | 30.3 / 19.8 / 4.06 | 30.3 / 18.0 / 3.88 | **+2.6 [0.6, 4.8]** | −0.2 [−1.0, 0.7] | +1.8 [−0.3, 4.0] | **−13.0 [−17.5, −8.7]** | **−1.0 [−2.1, −0.2]** |
| Confirmatory: final rule, fold-internal bar | 30.4 / 16.4 / 3.82 | 30.2 / 18.6 / 4.06 | 30.0 / 16.6 / 3.88 | **+2.2 [0.4, 4.3]** | −0.2 [−1.0, 0.7] | +2.0 [−0.3, 4.5] | **−14.2 [−18.8, −9.6]** | **−1.1 [−2.2, −0.3]** |
| Tier 0: mean-logit + memory | 31.0 / 26.6 / 0.00 | 31.1 / 29.7 / 0.00 | 30.8 / 26.9 / 0.00 | **+3.1 [0.4, 6.0]** | +0.1 [−0.7, 1.0] | **+2.8 [0.4, 5.3]** | −3.1 [−6.8, 0.4] | −0.2 [−1.3, 0.9] |
| Mean-logit gate + memory + certificate (light) | 30.3 / 20.1 / 1.43 | 30.3 / 21.9 / 1.70 | 30.3 / 21.5 / 1.48 | +1.8 [−0.4, 4.2] | +0.0 [−1.0, 1.0] | +0.4 [−2.4, 3.1] | **−10.9 [−14.4, −7.4]** | **−1.0 [−1.8, −0.3]** |
| Mean-logit full stack, cn90 bar | 30.3 / 16.2 / 3.12 | 30.2 / 17.9 / 3.41 | 30.2 / 17.4 / 3.17 | +1.7 [−0.2, 3.9] | −0.1 [−1.2, 1.0] | +0.5 [−1.4, 2.7] | **−14.9 [−19.5, −10.6]** | **−1.1 [−2.0, −0.3]** |
| Mean-logit full stack, fold-internal bar | 29.7 / 14.8 / 3.12 | 30.0 / 16.4 / 3.41 | 29.5 / 16.1 / 3.17 | +1.6 [−0.3, 3.7] | +0.3 [−0.7, 1.4] | +0.3 [−1.6, 2.5] | **−16.4 [−21.0, −12.0]** | **−1.3 [−2.6, −0.3]** |

CIs of the clean-model counts: Per-endoscopy gate R49 caught [30.1, 32.0], NP [28.3, 37.1]; Tier 0: mean-logit + memory caught [30.2, 31.8], NP [25.5, 34.0]; Mean-logit gate + memory + certificate (light) caught [29.0, 31.4], NP [16.6, 27.5]; Confirmatory: final rule, cn90 bar caught [28.7, 31.6], NP [14.4, 25.3]; Mean-logit full stack, cn90 bar caught [28.8, 31.4], NP [12.4, 23.5].

Saving against the same model's R49 (NP flagged by the rule minus by R49), clean minus published / clean minus random: Tier 0: mean-logit + memory +2.1 [−0.6, 4.8] / **+3.3 [0.5, 6.1]**; Memory (gate score) +0.5 [−1.3, 2.5] / +0.4 [−1.8, 2.8]; Memory + certificate (light, R49 gate) +1.0 [−1.2, 3.0] / +1.4 [−0.9, 3.9]; Confirmatory: final rule, cn90 bar +1.6 [−0.3, 3.6] / +2.3 [0.0, 4.6]; Mean-logit gate + memory + certificate (light) +0.8 [−1.3, 2.9] / +0.9 [−1.6, 3.4]; Mean-logit full stack, cn90 bar +0.7 [−1.2, 2.6] / +1.0 [−0.9, 2.9].


**Mean-logit stack minus R49-gate stack, same model** (NP flagged Δ; caught Δ; samples per patient Δ):

| Contrast | Model | Raw: NP | Raw: caught | Raw: samples / patient | Equal exposure: NP |
|---|---|---|---|---|---|
| ml_A12 - A12 | stored | −1.4 [−3.7, 0.8] | −0.2 [−1.1, 0.7] | **−0.51 [−0.67, −0.35]** | −1.2 [−3.1, 0.5] |
| ml_A12 - A12 | clean | −1.6 [−3.4, 0.0] | −0.2 [−0.6, 0.2] | **−0.46 [−0.64, −0.27]** | −1.3 [−3.1, 0.1] |
| ml_A12 - A12 | rand | −1.1 [−3.2, 1.0] | +0.0 [−0.8, 0.7] | **−0.53 [−0.70, −0.35]** | −1.2 [−3.4, 0.7] |
| ml_final - final | stored | −1.0 [−2.7, 0.6] | −0.2 [−1.1, 0.7] | **−0.70 [−0.88, −0.53]** | −0.7 [−2.3, 0.7] |
| ml_final - final | clean | **−1.9 [−3.6, −0.4]** | −0.1 [−0.5, 0.3] | **−0.65 [−0.83, −0.46]** | −1.4 [−3.1, 0.0] |
| ml_final - final | rand | −0.6 [−2.3, 1.0] | −0.1 [−1.2, 0.7] | **−0.70 [−0.91, −0.51]** | −0.9 [−2.7, 0.7] |
| ml_final_infold - final_infold | stored | **−1.6 [−3.2, −0.1]** | −0.7 [−1.8, 0.3] | **−0.70 [−0.88, −0.53]** | −1.1 [−2.6, 0.4] |
| ml_final_infold - final_infold | clean | **−2.2 [−4.0, −0.5]** | −0.2 [−0.9, 0.4] | **−0.65 [−0.83, −0.46]** | **−1.6 [−3.3, −0.2]** |
| ml_final_infold - final_infold | rand | −0.5 [−2.4, 1.3] | −0.5 [−1.7, 0.5] | **−0.70 [−0.91, −0.51]** | −0.6 [−2.5, 1.1] |
| ml_final - final_infold | stored | −0.2 [−2.1, 1.8] | −0.1 [−1.0, 0.8] | **−0.70 [−0.88, −0.53]** | +0.4 [−1.4, 2.1] |
| ml_final - final_infold | clean | −0.7 [−2.9, 1.5] | +0.0 [−0.5, 0.5] | **−0.65 [−0.83, −0.46]** | −0.5 [−2.6, 1.6] |
| ml_final - final_infold | rand | +0.8 [−1.5, 3.1] | +0.2 [−1.0, 1.3] | **−0.70 [−0.91, −0.51]** | +0.3 [−1.9, 2.3] |

### 2a. Equal exposure (E7 truncation, 200 draws; frozen per-fold rules)

| Rule | NP flagged: published | clean | random | Rule − R49, published | Rule − R49, clean | Clean − published | Clean − random | Caught, clean |
|---|---|---|---|---|---|---|---|---|
| Per-endoscopy gate R49 | 25.9 | 27.5 [23.0, 32.0] | 27.0 | — | — | +1.7 [−0.1, 3.8] | +0.6 [−1.0, 2.5] | 31.3 |
| H&E alone (P1 90%) | 29.5 | 31.9 [27.8, 35.6] | 30.2 | **+3.6 [0.9, 6.5]** | **+4.4 [1.2, 7.9]** | **+2.5 [0.6, 4.8]** | **+1.8 [0.0, 3.7]** | 31.3 |
| Memory (gate score) | 19.8 | 21.4 [16.2, 26.5] | 21.0 | **−6.1 [−8.3, −4.0]** | **−6.2 [−8.5, −4.0]** | +1.6 [−0.2, 3.7] | +0.4 [−1.4, 2.4] | 30.7 |
| Memory + certificate (light, R49 gate) | 18.5 | 20.3 [15.1, 25.7] | 19.1 | **−7.3 [−10.0, −4.9]** | **−7.3 [−10.0, −4.7]** | +1.8 [−0.1, 3.9] | +1.2 [−0.9, 3.3] | 30.5 |
| Confirmatory: final rule, cn90 bar | 14.6 | 16.7 [11.8, 21.9] | 15.1 | **−11.3 [−14.7, −8.1]** | **−10.8 [−14.4, −7.7]** | **+2.2 [0.4, 4.3]** | +1.7 [−0.1, 3.8] | 30.3 |
| Confirmatory: final rule, fold-internal bar | 13.5 | 15.9 [11.0, 20.9] | 13.9 | **−12.4 [−15.8, −9.2]** | **−11.7 [−15.2, −8.4]** | **+2.4 [0.7, 4.5]** | +2.0 [−0.1, 4.3] | 30.2 |
| Tier 0: mean-logit + memory | 22.3 | 25.6 [21.3, 29.8] | 22.4 | **−3.6 [−6.7, −0.6]** | −2.0 [−5.7, 1.6] | **+3.3 [0.7, 6.0]** | **+3.2 [1.0, 5.5]** | 31.1 |
| Mean-logit gate + memory + certificate (light) | 17.3 | 18.9 [13.9, 24.5] | 17.9 | **−8.5 [−11.2, −6.0]** | **−8.6 [−11.4, −6.0]** | +1.6 [−0.4, 3.9] | +1.1 [−1.1, 3.4] | 30.3 |
| Mean-logit full stack, cn90 bar | 13.8 | 15.4 [10.4, 20.6] | 14.1 | **−12.0 [−15.5, −9.0]** | **−12.2 [−15.8, −9.0]** | +1.5 [−0.3, 3.6] | +1.2 [−0.4, 3.2] | 30.2 |
| Mean-logit full stack, fold-internal bar | 12.4 | 14.3 [9.6, 19.3] | 13.2 | **−13.5 [−17.0, −10.3]** | **−13.3 [−16.9, −10.1]** | **+1.9 [0.0, 3.9]** | +1.0 [−0.6, 3.0] | 30.0 |

Memory gain at equal exposure (memory minus the same base without memory, NP flagged): ml_mem - ml_single: published **−2.3 [−3.7, −1.0]**, clean **−1.5 [−2.4, −0.7]**, random **−2.5 [−4.0, −1.2]**; A1 - gate_single: published **−3.0 [−5.2, −0.9]**, clean −1.8 [−3.9, 0.1], random −1.5 [−3.9, 0.8]; A12 - gate_single: published **−4.2 [−6.8, −1.9]**, clean **−2.9 [−5.3, −0.7]**, random **−3.3 [−5.9, −0.9]**.


### 2b. Landmark AUROC gain of memory (history to date; margin AUROC, memory minus single endoscopy)

| Pair | Horizon | Published, all landmarks | Clean, all landmarks | Clean, equal exposure | Clean, patient-weighted | Random, all |
|---|---|---|---|---|---|---|
| ml_mem - ml_single | 3y | **+0.030 [0.002, 0.064]** | +0.024 [−0.001, 0.053] | +0.015 [−0.011, 0.042] | +0.010 [−0.007, 0.028] | **+0.027 [0.001, 0.059]** |
| ml_mem - ml_single | 5y | **+0.027 [0.006, 0.050]** | **+0.022 [0.004, 0.040]** | +0.014 [−0.004, 0.032] | +0.011 [−0.002, 0.025] | **+0.027 [0.007, 0.048]** |
| ml_mem - ml_single | ever | **+0.026 [0.010, 0.042]** | **+0.029 [0.010, 0.048]** | **+0.025 [0.005, 0.044]** | **+0.019 [0.003, 0.036]** | **+0.028 [0.012, 0.042]** |
| A1 - gate_single | 3y | +0.011 [−0.007, 0.028] | +0.006 [−0.011, 0.023] | +0.001 [−0.017, 0.019] | +0.000 [−0.013, 0.013] | +0.011 [−0.010, 0.032] |
| A1 - gate_single | 5y | **+0.020 [0.002, 0.038]** | +0.010 [−0.004, 0.025] | +0.005 [−0.009, 0.020] | +0.005 [−0.006, 0.017] | +0.018 [0.000, 0.036] |
| A1 - gate_single | ever | **+0.032 [0.015, 0.050]** | **+0.024 [0.009, 0.040]** | **+0.020 [0.004, 0.037]** | **+0.017 [0.004, 0.032]** | **+0.025 [0.009, 0.043]** |
| A12 - gate_single | 3y | +0.006 [−0.012, 0.023] | +0.002 [−0.017, 0.020] | −0.006 [−0.027, 0.012] | −0.001 [−0.016, 0.013] | +0.005 [−0.015, 0.022] |
| A12 - gate_single | 5y | +0.017 [−0.003, 0.038] | +0.010 [−0.009, 0.031] | +0.001 [−0.020, 0.023] | +0.010 [−0.006, 0.026] | **+0.017 [0.001, 0.034]** |
| A12 - gate_single | ever | **+0.038 [0.020, 0.057]** | **+0.033 [0.015, 0.054]** | **+0.023 [0.004, 0.043]** | **+0.027 [0.011, 0.045]** | **+0.034 [0.017, 0.053]** |

Landmark sensitivity / specificity at the operating points, ≤ 5 y, clean (published): Tier 0: mean-logit + memory 0.922 / 0.481 (0.937 / 0.529); Confirmatory: final rule, cn90 bar 0.822 / 0.719 (0.815 / 0.741); Mean-logit full stack, cn90 bar 0.822 / 0.743 (0.812 / 0.775); Per-endoscopy gate R49 0.941 / 0.481 (0.929 / 0.508).


### 2c. Safety (never flagged to date + two consecutive lows) and per 1,000 patient-years (λ = 0.45%/yr, model-based)

| Rule | Model | Progressors de-escalated at the last pre-event endoscopy (integer range) | Progressors ever de-escalated before the event | NP de-escalated at last endoscopy | Missed (never flagged), mean (range) | Per 1,000 py in de-escalated [CI] | Exact upper |
|---|---|---|---|---|---|---|---|
| Tier 0: mean-logit + memory | stored | 0.1 [0.0, 0.3] (0–1) | 0.1 | 16.4 | 1.0 (0–2) | 0.37 [0.04, 0.93] | 1.92 |
| Tier 0: mean-logit + memory | clean | 0.3 [0.0, 0.8] (0–1) | 0.6 | 13.3 | 0.9 (0–2) | 0.41 [0.10, 0.92] | 2.36 |
| Tier 0: mean-logit + memory | rand | 0.2 [0.0, 0.5] (0–1) | 0.5 | 16.1 | 1.2 (0–3) | 0.45 [0.07, 1.10] | 2.50 |
| Memory + certificate (light, R49 gate) | stored | 1.0 [0.2, 1.9] (0–3) | 1.7 | 21.5 | 1.5 (0–3) | 0.42 [0.14, 0.81] | 1.88 |
| Memory + certificate (light, R49 gate) | clean | 0.8 [0.0, 1.8] (0–2) | 1.5 | 19.5 | 1.5 (0–3) | 0.47 [0.12, 0.97] | 2.07 |
| Memory + certificate (light, R49 gate) | rand | 1.3 [0.3, 2.6] (0–3) | 2.3 | 20.4 | 1.7 (0–4) | 0.51 [0.14, 0.98] | 1.98 |
| Confirmatory: final rule, cn90 bar | stored | 1.0 [0.2, 1.9] (0–3) | 2.7 | 25.8 | 1.5 (0–3) | 0.35 [0.12, 0.66] | 1.56 |
| Confirmatory: final rule, cn90 bar | clean | 1.0 [0.0, 2.2] (0–2) | 2.5 | 23.2 | 1.7 (0–3) | 0.45 [0.11, 0.91] | 1.74 |
| Confirmatory: final rule, cn90 bar | rand | 1.3 [0.3, 2.6] (0–3) | 3.3 | 25.0 | 1.7 (0–4) | 0.41 [0.12, 0.79] | 1.61 |
| Confirmatory: final rule, fold-internal bar | stored | 1.1 [0.2, 2.1] (0–3) | 3.0 | 26.6 | 1.6 (0–3) | 0.36 [0.12, 0.69] | 1.52 |
| Confirmatory: final rule, fold-internal bar | clean | 1.1 [0.1, 2.3] (0–3) | 2.9 | 24.4 | 1.8 (0–3) | 0.45 [0.13, 0.88] | 1.65 |
| Confirmatory: final rule, fold-internal bar | rand | 1.5 [0.3, 3.1] (0–3) | 3.5 | 26.4 | 2.0 (0–4) | 0.46 [0.13, 0.89] | 1.53 |
| Mean-logit full stack, cn90 bar | stored | 0.9 [0.2, 1.8] (0–3) | 3.4 | 26.8 | 1.7 (0–5) | 0.39 [0.11, 0.77] | 1.51 |
| Mean-logit full stack, cn90 bar | clean | 1.0 [0.1, 2.1] (0–3) | 2.4 | 25.1 | 1.8 (0–3) | 0.43 [0.15, 0.82] | 1.61 |
| Mean-logit full stack, cn90 bar | rand | 1.3 [0.3, 2.6] (0–2) | 3.4 | 25.6 | 1.8 (1–3) | 0.43 [0.10, 0.84] | 1.58 |
| Mean-logit full stack, fold-internal bar | stored | 1.3 [0.3, 2.6] (0–3) | 3.9 | 28.2 | 2.3 (0–5) | 0.49 [0.18, 0.91] | 1.72 |
| Mean-logit full stack, fold-internal bar | clean | 1.2 [0.1, 2.6] (0–3) | 3.3 | 26.6 | 2.0 (1–3) | 0.46 [0.14, 0.86] | 1.52 |
| Mean-logit full stack, fold-internal bar | rand | 1.9 [0.4, 3.7] (1–3) | 4.0 | 26.9 | 2.5 (2–4) | 0.56 [0.17, 1.06] | 1.80 |
| Per-endoscopy gate R49 | stored | 0.3 [0.0, 0.8] (0–2) | 0.3 | 11.2 | 0.9 (0–3) | 0.49 [0.00, 1.45] | 2.80 |
| Per-endoscopy gate R49 | clean | 0.2 [0.0, 0.7] (0–1) | 0.9 | 10.2 | 0.7 (0–2) | 0.42 [0.00, 1.33] | 3.08 |
| Per-endoscopy gate R49 | rand | 0.1 [0.0, 0.3] (0–1) | 0.2 | 9.7 | 0.7 (0–2) | 0.44 [0.00, 1.52] | 3.24 |
| H&E alone (P1 90%) | stored | 0.0 [0.0, 0.0] (0–0) | 0.1 | 7.0 | 0.9 (0–2) | 0.78 [0.00, 2.77] | 4.48 |
| H&E alone (P1 90%) | clean | 0.0 [0.0, 0.0] (0–0) | 0.3 | 5.2 | 0.7 (0–2) | 0.82 [0.00, 2.95] | 6.02 |
| H&E alone (P1 90%) | rand | 0.1 [0.0, 0.3] (0–1) | 0.4 | 5.7 | 0.6 (0–2) | 0.64 [0.00, 2.17] | 5.49 |
| Grade IND/LGD or p53 aberrant | stored | 7.0 [2.7, 11.9] (7–7) | 12.0 | 18.0 | 11.0 (11–11) | 3.70 [1.79, 6.43] | 5.71 |
| Grade IND/LGD or p53 aberrant | clean | 7.0 [2.7, 11.9] (7–7) | 12.0 | 18.0 | 11.0 (11–11) | 3.70 [1.79, 6.43] | 5.71 |
| Grade IND/LGD or p53 aberrant | rand | 7.0 [2.7, 11.9] (7–7) | 12.0 | 18.0 | 11.0 (11–11) | 3.70 [1.79, 6.43] | 5.71 |

### 2d. Lead time

| Window | Rule | Published caught / NP | Clean caught / NP | Clean: Δ caught vs R49 | Clean: Δ NP vs R49 |
|---|---|---|---|---|---|
| > 2 y (NP: all) (24 P) | Tier 0: mean-logit + memory | 23.5 / 26.6 | 23.4 / 29.7 | +0.1 [−0.7, 1.0] | −3.1 [−6.8, 0.4] |
| > 2 y (NP: all) (24 P) | Confirmatory: final rule, cn90 bar | 22.7 / 17.2 | 22.4 / 19.8 | **−0.9 [−1.9, −0.1]** | **−13.0 [−17.5, −8.7]** |
| > 2 y (NP: all) (24 P) | Confirmatory: final rule, fold-internal bar | 22.6 / 16.4 | 22.2 / 18.6 | **−1.1 [−2.2, −0.2]** | **−14.2 [−18.8, −9.6]** |
| > 2 y (NP: all) (24 P) | Mean-logit full stack, cn90 bar | 22.2 / 16.2 | 22.4 / 17.9 | **−0.9 [−1.8, −0.2]** | **−14.9 [−19.5, −10.6]** |
| > 2 y (NP: all) (24 P) | Mean-logit full stack, fold-internal bar | 21.8 / 14.8 | 22.2 / 16.4 | **−1.1 [−2.4, −0.2]** | **−16.4 [−21.0, −12.0]** |
| > 2 y (NP: all) (24 P) | Per-endoscopy gate R49 | 23.2 / 31.8 | 23.3 / 32.8 | — | — |
| > 2 y (NP: all) (24 P) | Grade IND/LGD or p53 aberrant | 14.0 / 25.0 | 14.0 / 25.0 | **−9.3 [−14.1, −4.6]** | **−7.8 [−14.4, −1.5]** |
| > 4 y (NP: all) (20 P) | Tier 0: mean-logit + memory | 18.4 / 26.6 | 17.9 / 29.7 | −0.3 [−2.3, 1.8] | −3.1 [−6.8, 0.4] |
| > 4 y (NP: all) (20 P) | Confirmatory: final rule, cn90 bar | 17.7 / 17.2 | 17.4 / 19.8 | −0.8 [−1.9, 0.1] | **−13.0 [−17.5, −8.7]** |
| > 4 y (NP: all) (20 P) | Confirmatory: final rule, fold-internal bar | 16.7 / 16.4 | 16.5 / 18.6 | **−1.7 [−3.0, −0.6]** | **−14.2 [−18.8, −9.6]** |
| > 4 y (NP: all) (20 P) | Mean-logit full stack, cn90 bar | 17.1 / 16.2 | 17.6 / 17.9 | −0.6 [−1.6, 0.5] | **−14.9 [−19.5, −10.6]** |
| > 4 y (NP: all) (20 P) | Mean-logit full stack, fold-internal bar | 16.3 / 14.8 | 16.3 / 16.4 | **−1.9 [−3.2, −0.8]** | **−16.4 [−21.0, −12.0]** |
| > 4 y (NP: all) (20 P) | Per-endoscopy gate R49 | 18.7 / 31.8 | 18.2 / 32.8 | — | — |
| > 4 y (NP: all) (20 P) | Grade IND/LGD or p53 aberrant | 6.0 / 25.0 | 6.0 / 25.0 | **−12.2 [−16.1, −8.3]** | **−7.8 [−14.4, −1.5]** |
| > 4 y (NP: > 4 y before last) (20 P) | Tier 0: mean-logit + memory | 18.4 / 18.7 | 17.9 / 21.4 | −0.3 [−2.3, 1.8] | −1.1 [−5.3, 2.7] |
| > 4 y (NP: > 4 y before last) (20 P) | Confirmatory: final rule, cn90 bar | 17.7 / 12.0 | 17.4 / 13.8 | −0.8 [−1.9, 0.1] | **−8.7 [−12.5, −5.2]** |
| > 4 y (NP: > 4 y before last) (20 P) | Confirmatory: final rule, fold-internal bar | 16.7 / 10.9 | 16.5 / 12.6 | **−1.7 [−3.0, −0.6]** | **−9.9 [−14.0, −6.1]** |
| > 4 y (NP: > 4 y before last) (20 P) | Mean-logit full stack, cn90 bar | 17.1 / 11.7 | 17.6 / 13.0 | −0.6 [−1.6, 0.5] | **−9.5 [−13.7, −5.9]** |
| > 4 y (NP: > 4 y before last) (20 P) | Mean-logit full stack, fold-internal bar | 16.3 / 10.0 | 16.3 / 11.5 | **−1.9 [−3.2, −0.8]** | **−11.0 [−15.3, −7.1]** |
| > 4 y (NP: > 4 y before last) (20 P) | Per-endoscopy gate R49 | 18.7 / 21.1 | 18.2 / 22.5 | — | — |
| > 4 y (NP: > 4 y before last) (20 P) | Grade IND/LGD or p53 aberrant | 6.0 / 20.0 | 6.0 / 20.0 | **−12.2 [−16.1, −8.3]** | −2.5 [−9.4, 3.9] |

### 3. Random-tile-removal control (artefact versus tile count)

ART's control removes the same number of tiles per sample at random and refits with the same recipe. It is run through every tier above (column "Random-removal control" and the "Clean − random" contrasts).

- **Confirmatory tier.**
  - Final rule: clean − random +1.8 [−0.3, +4.0] non-progressors flagged raw, +1.7 [−0.1, +3.8] at equal exposure.
  - Mean-logit full stack: +0.5 [−1.4, +2.7] raw, +1.2 [−0.4, +3.2] at equal exposure.
  - The confirmatory tiers' movement is therefore mostly a tile-count / refit effect, not an artefact effect. Their saving over R49 is unchanged against the control (final +2.3 [0.0, +4.6], mean-logit full stack +1.0 [−0.9, +2.9]).
- **No-sequencing tier.** The effect is specific to artefact tiles: clean − random +2.8 [+0.4, +5.3] raw, +3.2 [+1.0, +5.5] at equal exposure; saving over R49 +3.3 [+0.5, +6.1].

### 4. Frozen bundle v2 (clean-tile pipeline)

Bundle `killcoyne_mm/two_papers_REG/frozen_v2_clean/` (cluster), **bundle SHA-256 `c186e7895d295d561bc714cc9371eacd453428dbc7c4dc41358e8fd7c22055be`**, 40 files, frozen 2026-10-21T23:39:09. Freeze code: REG's `tp_reg_freeze.py` (commit 7e9dc92), executed by `tp_cln_freeze.py` (commit 1efed0f) with only the loader, the output paths and the scorer import substituted. Per-file hashes: `results/paper_final/two_papers_CLN/frozen_v2_MANIFEST.json`. Bundle v1 (`frozen/`, SHA-256 17828c1a…) was re-hashed after the work: 29 files, 0 mismatches.

**Pipeline (rules.json `pipeline`).**
1. **Tile QC** (`qc/qc_spec.json`). ART's flag with fixed thresholds:
   - tissue share < 0.15 (glass / background);
   - dark-unstained straight band ≥ 0.5 (edge);
   - ink > 0.02 (pen / dye);
   - tissue-pixel Laplacian variance < 132.544 (blur), the set-C 5th percentile stored as a constant.

   A sample with fewer than 32 clean tiles is topped up with its least-artefactual flagged tiles. Statistics come from `code/tp_art_qc.py`; the flag and the embedding from `code/tp_cln_pipeline.py`.
2. **Clean-tile mean UNI2-h embedding → L-IMG.** Models are refitted on all of set C with the unchanged kc / kv recipes: `models_their` uses their copy-number matrix, `models_pkg` uses package features for ACE-B and 4×.
   - L-CNV coefficients and copy-number scaling are byte-identical to v1.
   - L-IMG, L-EARLY and the image scaling are new.
   - In-sample AUROC (optimistic): L-IMG 1.000, L-CNV 0.996, L-LATE 1.000, recomputed equal to `model_info.json`.
3. **Scanner reset.** Class-wise quantiles of the clean out-of-fold L-IMG; π = 15/117; monotone.
4. **L-LATE** = (L-CNV + L-IMG) / 2.
5. **Rules**, one per tier, chosen on all 75 patients with REG's sequence: median gate cut-offs → modal hyper-parameters → median quiet cut → median threshold; median cn90 bar.

| Tier | Frozen rule | Values (v2) | Stability over the 10 repeats | Apparent (OPTIMISTIC) caught / NP / samples per patient | Nested held-out (clean) |
|---|---|---|---|---|---|
| Gate (ACE-B / 4×) | R49 | t_low 0.0392, c\* 0.6169, t_seq 0.2610 (package t_seq 0.2585) | — | 31.2 / 32.9 / 2.20 | 31.3 / 32.8 / 2.16 |
| 0: no sequencing | mean-logit + EW memory | h 4 y, threshold −1.604 | h = 4 in 8/10 | 30.6 / 26.1 / 0 | 31.1 / 29.7 / 0 |
| Light | mean-logit gate + EW memory + copy-number certificate | mean-logit gate cuts 0.0800 / 0.4826 / 0.2516; h 1 y, quiet p75 (logit L-CNV −0.337), −1.0 logit for 4 y; threshold +0.007 | modal tuple in 5/10 (5 tuples seen) | 30.6 / 20.9 / 1.60 | 30.3 / 21.9 / 1.70 |
| Confirmatory | light + quiet-genome check (ps_oac, two top-L-IMG samples) | cn90 bar 0.0609 | — | 30.5 / 17.5 / 3.24 | 30.2 / 17.9 / 3.41 |

Changes from v1:
- **The image model.** Tile QC and clean-tile L-IMG; the gate cut-offs move up (c\* 0.577 → 0.617).
- **The light and confirmatory tiers now sit on the mean-logit gate,** so the three tiers nest on one endoscopy score: tier 0 = mean-logit memory; light adds the gate and the certificate; confirmatory adds the check.
  - Held out, this stack beats the R49-gate stack in every model (section 1); REG's choice notes 1–2 had listed it as an option.
  - The R49-gate versions (light h 4 y, p75 (logit L-CNV −0.618), −1.0 logit for 2 y, threshold +0.620, modal tuple in only 3/10 repeats; confirmatory bar 0.0609) are recorded in `freeze_v2/freeze.json` as the alternative not chosen. On apparent numbers that alternative looks better (30.2 / 15.7 / 3.98), but the choice follows the nested held-out results, as REG's did.
- **The light tier is the least settled,** as in v1 (modal tuple 5/10).

**Verification** (`freeze_v2/verify.json`):
- REG's standalone scorer, extended by `tp_cln_score.py` for the mean-logit light / confirmatory tiers (written from the rule text, not the engine), reproduces the engine on all 10 repeats: flags for R49, R49 package, tier 0, light and confirmatory 0 mismatches; samples sequenced 0 mismatches; tier-0 and light scores max |Δ| < 1e-9.
- The independent QC + embedding function reproduces ART's clean-tile features for all 676 samples (max |Δ| 5.0e-8, the 8-digit CSV rounding); 10.6% of tiles flagged; 6 samples topped up.
- Development patient AUROC of the registered Paper 1 aggregation (nested, context only): L-IMG 0.828 (v1 0.854), L-LATE their 0.887 (0.893), package 0.914 (0.914).

### 5. Which tier is strongest now (clean-tile L-IMG)

| Criterion | Strongest | Runner-up | No-sequencing tier (tier 0) | Note |
|---|---|---|---|---|
| (a) Raw counts: NP flagged at ~equal caught | **Mean-logit full stack** 30.2 / 17.9 / 3.41; −14.9 [−19.5, −10.6] NP vs R49 | Final rule 30.3 / 19.8 / 4.06 (−13.0) | 31.1 / 29.7 / 0; −3.1 [−6.8, +0.4] vs R49 | Every confirmatory version catches about one progressor fewer than R49 (−1.0 to −1.3); the fold-internal bars flag fewer (16.4, 18.6) |
| (b) Equal exposure | **Mean-logit full stack** −12.2 [−15.8, −9.0] vs R49 | Final rule −10.8 [−14.4, −7.7] | −2.0 [−5.7, +1.6] vs R49; its own memory gain −1.5 [−2.4, −0.7] | Tier 0's lead over the gate does not survive both corrections together |
| (c) Safety: progressors de-escalated before the event (two lows + sticky flag) | **Tier 0** 0.3 at the last look (0–1), 0.6 ever | R49 0.2 at the last look, but it clears only 10 of 43 NP | — | Confirmatory tiers de-escalate 1.0 at the last look (0–3); none misses a progressor in ≥ 5 of 10 repeats |
| (c′) Safety: progressions per 1,000 py in the de-escalated group, exact upper (λ 0.45%/yr) | **Mean-logit full stack** 1.61 (point 0.43) | Final rule 1.74 | 2.36: above the 2 per 1,000 bar | The bar is met only by the confirmatory tiers |

**What Paper 2 should lead with.** Lead with the confirmatory tier on the mean-logit score: H&E memory + copy-number certificate + quiet-genome check. On the artefact-cleaned image model it is the only tier that is clearly better than the per-endoscopy gate on every count:
- 15 fewer non-progressors flagged in the raw data and 12 fewer at equal exposure;
- about one progressor fewer than R49 (−1.1 [−2.0, −0.3]);
- an exact upper limit under 2 progressions per 1,000 patient-years among the patients it de-escalates;
- 3.4 samples sequenced per patient.

Its advantage barely depends on the artefact tiles (clean − random +0.5). Memory stays the mechanism and the reason the stack works, and it is still measurable on clean tiles (landmark AUROC +0.029 [0.010, 0.048]; equal-exposure gain of 1.5 non-progressors). But the no-sequencing tier on its own is no longer a stronger rule than the gate: its saving over R49 is 3.1 [−6.8, +0.4] raw and 2.0 [−5.7, +1.6] at equal exposure, about half of it was artefact, and its exact safety limit is above the 2 per 1,000 bar. The plan v2 line "memory (no sequencing) leads" should therefore become "memory is the mechanism; the sequencing stack is the headline rule". Tier 0 should be presented as the externally testable rule (ERIN archive, H&E only), described as non-inferior to the gate without sequencing, with no claim that it flags fewer patients. Against current care (grade or p53), tier 0 still catches 10.1 [5.0, 15.4] more progressors for +4.7 [−1.7, +12.1] non-progressors flagged; the mean-logit full stack catches 9.2 [4.0, 14.3] more with −7.1 [−14.4, +0.4].

### What this changes in the plan

- Re-register with bundle v2, not v1: tile QC first, clean-tile models, and the mean-logit light / confirmatory tiers. The tier 0 definition is unchanged; its threshold moves from −1.737 to −1.604.
- The abstract's numbers move:
  - tier 0 vs R49: 31.8 → 26.6 becomes 32.8 → 29.7;
  - equal exposure: −3.6 becomes −2.0, CI including 0;
  - the confirmatory headline: 17.2 becomes 17.9 (mean-logit full stack).
- Tile QC must run in the ERIN and 4× pipelines before the frozen L-IMG is applied.

### Not done / caveats

- The light tier on the mean-logit gate was not added to the P2S safety, per-1,000 or lead-time tasks (those run P2S's rule list plus the two full stacks); its counts and equal-exposure numbers are in section 1 and 2a.
- All three models share the stored L-CNV and folds, so the comparisons isolate the image model.
- The ART flag's blur component is the least precise part (ART's blind check, precision 80%).

### Implementation notes

- **`tp_cln_main.py`** executes `tp_p2s_main.py`'s definitions, swaps `load("their")` in the E2 / round-8 namespace (`g8`) and P2S's `state_ml`, then executes P2S's dispatch unchanged with `XD` / `OUT` redirected.
  - The mean-logit full stack is E9's construction: E7 `engine` selection on the mean-logit state's A12 family; `apply_check` with the mean-logit gate band from `r49_calls`, so k2 − 1 samples in the middle band; the check arrays come from the same model's `build`.
  - `compare` reuses P2S's truncation code and E7's `avgA` / `full` / `delta`.
- **`tp_cln_freeze.py`** executes `tp_reg_freeze.py` with asserted single-occurrence substitutions. The model swap also patches `tb_common.load`, so every later `from tb_common import *` (the check arrays; `TC.load('pkg')`) sees the clean L-IMG.
  - The mean-logit light / confirmatory freeze uses REG's own functions (`full_ctx`, `pick`, `f_A12`, `a12_cand`, `mode_first`, `med`, `with_check`) on the mean-logit full context.
- **`tp_cln_freeze.R`** evaluates `kc_freeze.R` / `kv_freeze.R` with the image input line swapped.
- **The cluster checkout was not pulled.** P2N's untracked scripts block the rebase; they were not touched. CLN code ran from `killcoyne_mm/two_papers_CLN/code/` (identical to the committed files), as ART's did.
- **Row-level outputs** (cluster): `killcoyne_mm/two_papers_CLN/<model>/rules.npz`, `bands.npz`, `clin.npz` (copy of P2S's), `freeze/apparent_flags.npz`.

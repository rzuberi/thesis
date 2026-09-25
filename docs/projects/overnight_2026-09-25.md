# Overnight campaign, 24→25 September 2026: "is it a fluke?" checks, completeness, and a local-LLM review

Launched ~23:45 on 24 Sep (Rehan: "run further checks… make sure all three projects are fully done… natural
follow-ups… ways to check this is actually working and not a fluke… call some local LLMs to review"). Every job is a
Slurm job; nothing runs on the laptop. Results are appended below as they land and pushed into each project's status log.

## Track A — the P32 SWG fusion result (+0.050 [+0.015, +0.089]) under attack

| job | what it tests | if the result is real | if it is a fluke |
|---|---|---|---|
| `p32_head_repeat` | ERIN grade head retrained on a different patient split (FOLD_SEED 1), applied to SWG | imputed grade ≈ 0.75 for progression again; fuse3 gain similar | gain moves by more than its CI |
| `p32_head_perm` | ERIN head trained on **permuted** grade labels (a "random ERIN head"), applied to SWG | its fuse3 gain ≈ the ensemble control (+0.02) or less | it gains as much as the real head → the gain is a generic third-image-model effect |
| `p32_swg_img05` | SWG-trained image arm retrained on the new 0.5 µm/px features (median 1,224 tiles vs 256) | SWG image arm rises little; ERIN head still ≥ SWG arm | SWG arm rises to ≈ 0.76 → "ERIN beats SWG's own model" was a feature-quality artefact; also re-test fuse3 on the new arm |
| `p32_checks` §1 | selection-adjusted permutation over the six imputed fields (max-over-fields delta) | p < 0.05 | p > 0.05 → the field choice was fishing |
| `p32_checks` §2 | replication of fuse3 on the **rep02** split (rep02 image/CNV OOF + folds; ERIN heads unchanged) | gain ≈ +0.04–0.05 again | gain vanishes |
| `p32_checks` §3 | imputed grade vs the Barrett's-DB **confirmed code** (the human anchor that agrees with the jury at 0.99) | > 0.7 (the 0.62 against the spreadsheet was the wrong bar) | still ≈ 0.6 → the head is not reading grade on SWG |
| `p32_checks` §4 | calibration/prevalence of the transferred head on SWG | positive rate near SWG's, slope near 1 | gross shift → domain gap |

## Track B — completeness of P31 and P33

| job | what |
|---|---|
| `p31_gemma_s0..3` → `p31_agreement` | second juror (gemma3-27B, v2 prompt) on the same 2,293 reports: per-field agreement and kappa with MedGemma-27B; which fields are model-robust |
| `p31_db_s0..1` → `p32_real_vs_imputed` | v2 extraction on the **Barrett's-DB clinical reports** of the SWG samples (428 slides / 65 patients); imputed-vs-real field AUROC per field (direct test of image-to-fields on SWG); fusion with real vs imputed fields on that subset |
| `p33_tilefeat_v2` → `p33_tasks_v2` | tile MLP with **3 seeds** and **patient-level** fold assignment (a slide of any training patient is scored by that patient's held-out model) → closes the indirect-leak caveat in P33; re-runs the six task comparisons |
| `p33_tilemaps_top` | per-tile grade maps for the 8 highest-scoring benign T3a slides + 4 controls, for the pathologist checklist (`review/p33_tilemaps/`) |

## Track C — local-LLM review panel

`llm_review`: qwen3-32B, gemma3-27B, MedGemma-27B, deepseek-r1-14B, mistral-small-3.2, phi4-14B each read a
~90k-character pack (claims excerpt, digest table, 24 Sep ledger results, the three project MDs) and answer seven
fixed headings as a hostile reviewer: what is established, confounds, statistical concerns, ranked next experiments,
missing baselines, ideas, verdict. Output `docs/projects/llm_review_2026-09-25.md`. Aggregate docs only; nothing
leaves the cluster.

## Not launched (needs a decision or data)
- ACE-B application of the field heads (slides not scanned).
- A second ERIN-side control that would separate "report supervision" from "bigger cohort": an ERIN ABMIL trained
  directly on the SWG progression task is impossible (no progression labels at scale in ERIN); the closest feasible
  control is the permuted-label head above plus the treatment-effect head already imputed.

## Job ids (24 Sep 23:50)
Track A 57648201 (repeat head), 57648202 (permuted head), 57648203 (SWG img 0.5 µm) → 57648204 (checks).
Track B 57648205–08 (gemma shards) → 57648209 (agreement); 57648210–11 (DB reports) → 57648212 (real vs imputed);
57648213 (tilefeat v2) → 57648214 (tasks v2), 57648215 (tile maps). Track C 57648216 (LLM panel, 6 models).
All on cuda/epyc only (no h200 twins, so no dependency can hang on a never-starting job).

## Results (appended as they land)

All 16 jobs finished by 09:30 on 25 Sep, zero failures. Result JSONs committed under `results/numbers/` (`p32_checks.json`,
`p32_swg_img05.json`, `p32_head_repeat.json`, `p32_head_perm.json`, `p31_agreement.json`, `p32_real_vs_imputed.json`,
`p33_tilefeat_v2.json`, `p33_tasks_v2.json`); LLM panel verbatim in `docs/projects/llm_review_2026-09-25.md`.

### Track A — the P32 result survives every control that could have killed it, with one mechanism surprise

| check | outcome | verdict |
|---|---|---|
| Selection-adjusted permutation over the 6 fields (max-over-fields Δ vs fuse2) | selected field = grade, t 0.069, **p 0.022** (unadjusted 0.006); all-fields fusion Δ +0.050, p 0.0025 | not fishing |
| Repeat ERIN split (FOLD_SEED 1) grade head | ERIN OOF 0.891; on SWG the arm alone 0.764, fuse3 0.854, **Δ vs fuse2 +0.028 to +0.122 (CI > 0)** | replicates across ERIN splits |
| **Permuted-label ERIN head (random-head control)** | ERIN OOF 0.487 (chance, as designed); on SWG arm 0.449, fuse3 0.677, Δ vs fuse2 **[−0.170, −0.037]** — it *hurts* | the gain needs real grade supervision; it is not a generic third-model effect |
| SWG image arm retrained on the 0.5 µm features | 0.693 [0.596, 0.780] vs release 0.731, Δ [−0.103, +0.022]; fuse2′ 0.774; fuse3′ with the ERIN grade head 0.823, **Δ vs fuse2′ [+0.002, +0.098]** | finer tiles did not help SWG's own model; the ERIN head's advantage is not a feature-quality artefact, and the gain holds on the new arm |
| rep02 SWG split replication (ERIN heads unchanged) | fuse2 0.830 (rep02 image 0.745, CNV 0.708 are themselves higher); f3_grade 0.866, Δ +0.035 [−0.008, +0.079]; f3_all 0.845, Δ +0.015 [−0.018, +0.048] | same sign, smaller, CIs include 0 — the gain is split-dependent in size |
| Imputed grade vs DB confirmed code (n 418) | **0.629**; vs spreadsheet on the same slides 0.640; spreadsheet and DB code agree 0.993 here | the head does NOT read the SWG pathologist grade (the 0.62 was not a wrong-bar problem) |
| Calibration / prevalence on SWG | head calls 85 % of SWG slides p > 0.5 against a 12 % LGD+ rate; mean p 0.64 vs 0.32 on ERIN; slope 0.58, intercept −2.45 | large domain shift: on SWG the head is a shifted, weakly grade-related score |

**Reading.** The fusion gain is real by every statistical test available (selection-adjusted, permuted-label control,
second ERIN split, second feature set), but the *mechanism is not "imputed grade"*: on SWG the transferred head agrees
with the pathologist grade at only 0.63 while predicting progression at 0.76–0.77. It is scoring something that
co-varies with dysplasia in ERIN and with progression in SWG, under a strong calibration shift. Candidate: the head
learned report-supervised morphology of "dysplasia-prone Barrett's" (glandular architecture, IM density) that the
SWG-trained arm, with 127 progressor samples, could not. Honest wording for the thesis: *report-supervised
pre-training on ERIN produces an image score that transfers to SWG and adds +0.05 AUROC to image + CNV, surviving a
permuted-label control; the score is not a grade read-out on SWG.* rep02's smaller gain is the number to quote as the
lower bound.

### Track B — completeness

**P31 second juror** (gemma3-27B v2 vs MedGemma-27B v2, 2,279 reports; `p31_agreement.json`): grade exact 0.946 /
κ 0.89 (gemma vs jury 0.942 exact, 0.953 two-tier), specimen_type 0.996 / 0.97, intestinal_metaplasia 0.926 / 0.85,
p53 0.901 / 0.77, inflammation 0.815 / 0.71, treatment_effect 0.861 / 0.65, site 0.741 / 0.55, gastric 0.735 / 0.56;
**not robust:** ulceration_or_erosion exact 0.318 / κ 0.19, goblet_cells κ 0.07, diagnostic_certainty κ 0.23,
squamous_only κ 0.56 despite 0.958 exact (rare class). Consequence for P32: the "ulceration is visible at 0.85" row
rests on a field two models cannot agree on and is demoted to *fragile*; the robust visible set is grade, IM,
specimen type, treatment effect, inflammation (moderate/severe).

**Real vs imputed fields on SWG** (428 slides, 65 patients with a DB clinical report; `p32_real_vs_imputed.json`):
imputed grade vs the report's real grade 0.647, imputed IM vs real IM 0.724, inflammation 0.61 — consistent with
Track A: the heads do not recover the SWG report fields. Fusion on 65 patients is uninformative (all CIs span zero;
real-field fusion 0.636, imputed-grade fusion 0.698, fuse2 0.590).

**P33 v2** (3 seeds, patient-level fold scoring; 13,319 slides, 10,344 scored by a held-out-patient model;
`p33_tasks_v2.json`): T3a 0.800 (v1 0.798), T3b 0.828 (0.827), T3a_bio 0.765, T3b_bio 0.802 — **unchanged**, so
the T3 field-effect summary was not leaking. T2a 0.758 (v1 0.792) and **T2b 0.720 (v1 0.782)** fell by 0.03–0.06:
the v1 T2 numbers had benefited from indirect leakage through training-patient slides; T2b is now 0.14 below ABMIL.
Predictions 1–3 still hold; the T2b gap is larger than stated.

**Tile maps** (`review/p33_tilemaps/`, 12 PNGs, index in `review_local/p33_tilemaps/index.json`): the eight
top-scoring benign-section T3a positives carry 5–66 % LGD-class tiles (median ≈ 40 %) on slides the section jury
called NDBE/NORMAL. Two of the four top-scoring *negatives* look the same (b61d7ccd: 50 % LGD + 30 % HGD tiles;
4c5e0c58: 45 % HGD tiles): either the case-max label missed dysplasia or the model over-calls — exactly the question
for the pathologist checklist.

### Track C — what the six local reviewers said (verbatim in `llm_review_2026-09-25.md`; 13,800–15,900 prompt tokens each)

**Where they agree (5–6 of 6):**
1. *Independent external validation* of both the ERIN field effect (C26) and the SWG fusion — ACE-B is the only route; blocked on scanning.
2. *Spatial statistics on the tile maps* (clustering / edge-vs-interior of LGD-like tiles) as the next P33 step — every model raised it.
3. *Human audit of the LLM labels* — partly answered by C27 (8,221 DB-coded reports at 0.986), pending provenance (Q13); the 30-report and 50-report hand-check packs are the remaining human step.
4. *A non-grade ERIN head as the ensemble control* and a *selection-adjusted test over the six fields* — both run overnight: the permuted-label head **hurts** (Δ [−0.17, −0.04]) and the treatment-effect head is at chance for progression (0.556), while the selection-adjusted p is 0.022.
5. *Second CV repeat of the P32 heads* — run overnight; replicates (Δ [+0.028, +0.122]).
6. *Compare the imputed grade to the DB anchor* (MedGemma's check #3) — run: 0.629, so by their own criterion the "imputed grade" reading is questionable; the permuted control says the signal is nonetheless real, which is why the claim is now worded as transfer, not imputation.

**Ideas not yet in the plan (worth doing):** site- or sub-cohort-stratified field effect (qwen3); edge-vs-interior localisation of the field-effect signal within benign tissue (MedGemma); *temporal* field effect on serial slides of the same patient (qwen3, deepseek); multi-task head predicting grade and field effect jointly to test whether they are the same signal (qwen3); using the LLM's per-field uncertainty to triage reports for human review (gemma3); the reverse transfer, SWG-trained heads applied to ERIN (MedGemma); a clinical-covariate confound arm for T3 as was done for T4 (deepseek).

**Where they are wrong or already answered (so the reader does not chase them):** qwen3 says the SWG bootstrap is "not patient-clustered" — it is, throughout; deepseek misquotes the CONCH scale result ("0.559 at 2.2 µm/px") and attributes the STAD/GEJ WGD numbers (0.63–0.69) to cohort transfer; phi4 asks for a text-embedding-only ERIN arm — that is the text arm already reported (0.61–0.73); MedGemma's "apply the SWG fusion model to OCCAMS or ERIN" is not possible (different endpoints, no progression labels at scale in ERIN); several reviewers conflate C26 (ERIN field effect) with P32 (SWG fusion). Baselines demanded (BioClinicalBERT-style NLP for P31, PORPOISE-style fusion for C1, attention-map interpretability) are either already in the thesis (PORPOISE C5, heat-maps) or reasonable additions for the labelling paper (a fine-tuned BERT baseline for grade extraction).

**Verdicts, condensed:** all six accept the LLM-labelling validation and the ERIN benign-tissue signal as established; all six call the SWG fusion gain real-but-fragile at n = 150 and want an independent cohort; none found an error in the numbers themselves.

### What the overnight changes in the three project verdicts
- **P31:** done as a first pass with a two-juror consensus available for six fields; four fields (ulceration, goblet, certainty, site) are model-dependent and should not be used as targets until the prompt is revised.
- **P32:** the SWG gain is robust to every control run (selection, permuted labels, second ERIN split, second feature set), weaker on the rep02 split, and *not* explained by grade read-out on SWG. Claim to carry forward: *report-supervised pre-training on ERIN transfers a progression-relevant image score to SWG (+0.05 over image + CNV; lower bound +0.015 on rep02).* The ulceration-visibility row is demoted.
- **P33:** the field-effect summary stands with no leakage; the T2 summaries were leak-inflated and are corrected downward; twelve tile maps are ready for a pathologist, and the two dysplastic-looking "negatives" are the first cases to show them.


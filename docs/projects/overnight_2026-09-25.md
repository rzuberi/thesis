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

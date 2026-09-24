# P31 — Multi-field structured extraction from ERIN pathology reports

Started 24 Sep 2026 (Rehan: "start the new projects; one MD per project; launch first passes to see which
directions work"). Pre-registered here before the first job returned. Status log at the bottom.

## Question
A report says more than a grade. Can one local LLM extract, per report, a fixed set of fields that
(a) describe what the pathologist saw and (b) are candidates for image prediction (P32)? Which fields
parse reliably, and which agree with simple text evidence?

## Fields (whole-report level, fixed vocabulary)
grade (NDBE/IND/LGD/HGD/CANCER/NA) · site (oesophagus/goj/stomach/other/mixed) · specimen_type
(biopsy/emr_esd/resection/other) · intestinal_metaplasia (present/absent/not_stated) · goblet_cells ·
inflammation (none/mild/moderate/severe/not_stated) · ulceration_or_erosion · squamous_only (yes/no) ·
gastric_mucosa_present · treatment_effect (yes/no: post-ablation, neosquamous, scarring, prior EMR site,
buried glands) · p53 (abnormal/normal/not_done/not_stated) · diagnostic_certainty
(definite/probable/uncertain) · n_specimens (integer).

## Data and model
Input: the 2,280 imaged ERIN cases (one UNI2 slide per case, `labeller/erin_master.csv`), report text =
clinical information + gross + microscopic + final diagnosis + first addendum, truncated at 7,000 chars.
Model: MedGemma-27B via local ollama (the most reliable single juror: 99.7 % parse, 99.7 % agreement with
the 8-model jury), temperature 0, JSON mode, 300 output tokens. Raw JSON kept for every report.
Script `scripts/projects/p31_fields_shard.py` (4 shards, cuda + h200 race twins).

## First-pass validation (no human labels yet), `scripts/projects/p31_validate.py`
1. Parse-fail rate per field (gate: < 5 % for a field to go forward to P32).
2. Field vs keyword regex on the same text: treatment_effect vs /RFA|ablat|EMR|ESD|neosquam|buried/,
   p53 stated vs /p53/, inflammation stated vs /inflamm|oesophagitis/, IM present vs /intestinal
   metaplasia|goblet|barrett/, ulceration vs /ulcer|erosion/. Expected: agreement > 0.85 where the field is
   lexical (p53, treatment); lower for IM (negations) — the gap is what the LLM adds over regex.
3. grade vs the 8-model jury final label on train-eligible reports (expected exact > 0.95).
4. specimen_type vs SpecimenProtocol RESECTION flag (expected > 0.95).
5. A 50-report hand-check pack, stratified by grade, written to `review_local/` (cluster) for Rehan.

## Predictions written down before results
- grade, specimen_type, p53, treatment_effect: reliable (> 0.9 by the checks above).
- inflammation grade and diagnostic_certainty: reliable parse, but low agreement between models if we
  later add a second juror; they are the fields where pathologists themselves vary.
- intestinal_metaplasia "absent" will be rare: UK reports state IM when present and rarely negate it.

## Outputs
`feasibility/runs/p31_fields_s*/output/fields_medgemma_27b_shard*.jsonl` (per report, incl. raw),
`feasibility/runs/p31_validate/output/{p31_validation.json, p31_fields.csv}`; committed copy of the
validation JSON in `results/numbers/p31_validation.json`.

## Not done in the first pass
Second juror (qwen3-32B) for agreement; per-section extraction; extension to all 7,149 reports;
the Barrett's-DB reports for SWG patients (a copy of this script with `INPUT` pointed at the DB export).

## Status log
- 2026-09-24 evening: scripts written, 8 shard jobs + validate submitted (validate chained on the shards).
- 2026-09-24 22:30: all 4 shards DONE on cuda in ~17 min each (570 reports per shard, 2,279 total; h200 twins cancelled). Validation job released.
- 2026-09-24 22:50: VALIDATION (`results/numbers/p31_validation.json`, 2,293 reports). Parse failures ≤ 1 % on every
  field (max 1.0 % gastric_mucosa_present). Keyword checks: p53 stated 0.99, ulceration 0.95, inflammation stated 0.89,
  treatment_effect 0.87 (220 keyword mentions without "yes" are mostly RFA/EMR in the clinical-history line, i.e. the
  field is stricter than the regex, as intended; 75 "yes" without keyword to hand-check), IM present 0.71 (regex includes
  "Barrett" from the clinical line; 786 "absent" are squamous/gastric/neosquamous specimens). specimen_type vs
  protocol 0.96, with 127 EMR/ESD split off correctly. Marginals: treatment_effect yes 522 (23 %), p53 stated 475,
  certainty non-definite 78 (3.4 %), squamous_only 127, gastric present 831.
  **FINDING: the grade field DEGRADED under the multi-field prompt.** vs the 8-model jury on 1,579 train-eligible
  reports: two-tier 0.936 but exact 0.477; the model called IND on 651 jury-NDBE reports (749 IND in total vs the
  jury's ≈ 300 corpus-wide) and NA on 650 reports. The same model with the dedicated single-field prompt agreed
  99.7 % exact. Cause (hypothesis): the one-line grade definition in the multi-field prompt lets "IND" absorb
  inflammation/reactive change and "NA" absorb GOJ/gastric specimens. Prediction 1 (grade reliable) is therefore
  FALSE for this prompt; predictions on p53/treatment/specimen hold.
  Action: v2 prompt with the explicit ladder text (IND only if the pathologist writes it; NA only if no
  oesophageal/GOJ tissue) launched on 400 reports (`p31_v2check`) to test whether the fix restores agreement.
  For P32 the grade targets use the P31 v1 grade binarised (two-tier 0.936 is adequate); the jury grade result
  (0.926) remains the reference. Hand-check pack (50 reports) copied to `review/p31_handcheck_pack.md` on the laptop.
- 2026-09-24 23:15: v2 PROMPT CHECK, first 96 overlapping train-eligible reports (400-report check still running):
  grade vs jury exact **0.927** (v1 on the same reports 0.500), two-tier 0.948 (0.917), NA calls 0 (24), IND calls 1
  (26; jury 1). The other fields barely move between v1 and v2 (treatment 0.96, IM 0.97, certainty 0.97,
  inflammation 0.88 agreement), so the fix is specific to the grade definition. Cause confirmed: the one-line
  ladder let IND absorb reactive change and NA absorb GOJ specimens. v2 is now the P31 prompt. FULL v2 extraction
  (4 shards, `p31_fields_v2_s*`) + chained validation launched; P32's first pass continues on v1 fields (grade
  binarised, two-tier ≥ 0.92; non-grade fields ≥ 0.88 identical), and P32 pass 2 will use v2.
- 2026-09-24 23:45: v2 CHECK COMPLETE, 386 train-eligible reports with both prompts: v2 grade vs jury exact **0.948**
  (v1 0.491), two-tier 0.966 (0.950), NA 0 (107), IND 9 vs jury 10 (v1 123). Residual v2 errors: 7 jury-NDBE → HGD
  and 4 → LGD (3.8 % over-call on benign), 6 jury-CANCER → HGD, 1 HGD → NDBE. Conclusion: multi-field extraction
  works when each field carries its full definition in the prompt; a one-line vocabulary is not enough for the
  clinically loaded field. Full v2 run in progress.
- 2026-09-25 00:10: FULL v2 RUN VALIDATED (`results/numbers/p31_validation_v2.json`, 2,293 reports; the v2 field
  table `feasibility/runs/p31_validate_v2/output/p31_fields.csv` is now the canonical P31 output). Grade vs jury on
  2,215 train-eligible reports: exact **0.949**, two-tier 0.969, NA 2. Residual pattern: 60 of 1,590 jury-NDBE
  reports over-called (29 HGD, 31 LGD; 3.8 %), 27 of 310 jury-cancer under-called as HGD. Parse failure ≤ 3.1 %
  (inflammation). Keyword checks unchanged (p53 0.98, ulceration 0.95, inflammation 0.92, treatment 0.84, IM 0.72).
  Side effect worth knowing: sharpening the grade definition collapsed diagnostic_certainty (78 non-definite in v1
  → 19 in v2): fields interact through the prompt, so every field needs its own definition and its own check.
  Marginals v2: treatment_effect yes 445 (19 %), p53 stated 484, IM present 1,436 / absent 788.
  First pass verdict: **extraction works** for grade (with the full ladder), specimen type, p53, ulceration,
  treatment effect and IM; inflammation grade and certainty are the fields that will need a second juror and a
  human check before use.


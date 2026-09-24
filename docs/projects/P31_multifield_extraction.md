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

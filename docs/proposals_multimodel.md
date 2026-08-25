# Multi-model proposal consultation (2026-08-25)

Ten models (6 frontier: GPT-5.6-Terra-Pro, Grok-4.6, Kimi-K3, DeepSeek-V4-Pro,
GLM-5.3, Qwen3.8-Max; 4 small: GPT-5.6-Luna, Gemini-3.7-Flash,
DeepSeek-V4-Flash, Qwen3.7-Flash) each proposed 8 campaigns given the full
current pack INCLUDING the red-team findings. 80 proposals total; raw answers
logged in `review/proposals_*.json`. Clustered below by cross-model recurrence.
Status: CANDIDATES — per the plan contract these are PARKED until jointly
promoted; items already in the plan are marked.

## Tier 1 — proposed by 5+ of 10 models

1. **PORPOISE published baseline** (8/10) — already plan item 1.4. Consensus
   design: build ESCA/STAD omics via their Preprocessing.ipynb + signatures.csv,
   reuse our frozen patient-disjoint folds, run on TCGA pool (n=399) + OCCAMS
   (n=87). Decisive: if PORPOISE also nulls externally, "fusion fails to
   replicate" stops being attributable to bespoke architecture.
2. **Genotype-visibility learning curve, n × population disentangled** (7/10) —
   subsample OAC-only / GEJ-only / STAD-only / mixed at matched n
   (65/100/150/250/350/446), TP53+WGD probes, 50-perm nulls, one figure.
   Decisive: if OAC-only stays null at n=350+ while mixed rises, the "adequate
   n" claim dies and population-visibility replaces it. CHEAP (features exist,
   CPU). The single highest insight-per-hour item on the board.
3. **Unsure-holdout scoring / deployment sensitivity** (7/10) — already item
   1.22. Extensions worth adopting: entropy-as-sample-weight retraining arm
   (Grok, Qwen3.7) and abstention/triage framing (Qwen3.8's entropy quality
   gate).
4. **R.4 pathologist sample — build the pack NOW** (6/10) — the grading is
   Rehan's, but every model converges on the same prep: stratified 250-report
   export (confident / unsure / pathladder-vs-jury disagreements enriched for
   negation + the 321 CANCER-vs-NDBE confusions), blind, two graders if
   possible, Terra-Pro adds: a nested ~80-case arm where the pathologist reads
   the WSI itself, testing report-vs-slide truth. Design doc + export can be
   ready before Rehan returns.
5. **Clinical-arm leakage ablation** (5/10) — already item 1.23. Terra-Pro's
   stricter version adopted as the design: landmarked index-biopsy build where
   only pre-index information enters the clinical arm.
6. **Conditional-attention shift, replicated on TCGA pool with controls**
   (6/10) — extends done item 2.20 to a second cohort with permuted-genomics
   AND random-vector controls (Terra-Pro), plus tile-level readouts.

## Tier 2 — proposed by 2-4 models, high value

7. **Power map / minimum-detectable-delta simulation** (4/10; GLM's version
   sharpest) — for each cohort's n and event count, inject known fusion deltas
   into semi-synthetic OOF risks, measure detection probability. Decisive:
   shows which cohorts could NEVER have detected a plausible delta — turns
   "fusion failed to replicate" into "fusion was undetectable below X at n=87",
   the quantitative core of Ch5. CHEAP (CPU, saved OOF).
8. **Winner's-curse quantification by bootstrap selection stability** (GLM) —
   re-run the 7-family SWG comparison on ~200 patient bootstraps of saved OOF;
   report how often late-mean actually wins. CHEAP; directly answers a wave-1/2
   convergent criticism with a number.
9. **Leave-one-family-out jury** (GLM; answers the correlated-LLM-error
   criticism) — recompute majorities dropping each model family; report label
   flip rate + downstream AUC stability. CHEAP (CPU, votes exist).
10. **Residual-complementarity meta-model** (Terra-Pro) — nested Cox on saved
    OOF risks: does genomics add after histology risk is in the model?
    Reframes fusion as conditional information gain. CHEAP.
11. **Cross-cohort transfer matrix** (4/10) — train each arm in each cohort,
    evaluate in every other (SWG->ERIN progression the key cell). Decisive for
    the replication story; moderate GPU.
12. **Pan-cancer jury/pathladder validation on TCGA-Reports** (Kimi, Grok) —
    extends 2.19: 3 cancer types with structured ground truth; tests whether
    report-derived supervision transports beyond oesophagus. Makes Ch4 a
    method chapter with external validity.

## Notable singletons

- Label-noise phase diagram via controlled corruption (Luna) — quantifies how
  much label error the grade task can absorb; explains jury==pathladder
  equivalence.
- Specimen-vs-report-vs-patient-level supervision comparison (Luna) — folds the
  parked specimen-suffix question into an experiment.
- Time-dependent AUC + decision curves for surveillance (Qwen3.7) — clinical
  utility framing for Ch3.
- Calibration-first cross-cohort analysis (Qwen3.8) — ECE/reliability as the
  replication metric instead of discrimination.
- Fusion failure-mode simulator as a new chapter (DeepSeek-Flash) — overlaps
  with the power map (7); merge if promoted.

## Small-vs-big model observation

Small models proposed the same top clusters as frontier ones (PORPOISE,
learning curve, leakage ablation) — the differentiator was design sharpness,
not idea novelty. Terra-Pro's leakage/landmark design and GLM's power map were
the two proposals no small model matched.

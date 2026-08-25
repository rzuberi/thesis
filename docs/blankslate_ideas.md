# Blank-slate ideation: data + compute only (2026-08-25)

Ten models (same six frontier + four small as the primed consultation) were
given ONLY the dataset/compute inventory — no thesis question, no results, no
prior framing (temperature 0.9). 80 ideas; raw answers in
`review/blankslate_*.json`. LOG ONLY — nothing here is promoted.

## Unprimed convergence (what this data 'obviously' supports)

1. **Longitudinal trajectory modelling of Barrett's surveillance** (9/10
   models) — treat each patient's SERIAL biopsy sequence as a trajectory
   (sequence-to-event, embedding drift, change-point detection, 'morphological
   velocity') predicting future progression, exploiting ERIN's multi-timepoint
   span and SWG's serial samples. THE largest unprimed cluster — and something
   the thesis currently does not do at all (we use index biopsies as
   snapshots). Notable variants: Terra-Pro's 'digital twin' predicting the
   next documented disease state from slide+report+timing history; Qwen3.7's
   temporal embedding-drift change-points as clonal-expansion markers.
2. **Morphology-to-genome prediction** (9/10) — predicting CNV burden, TP53,
   WGD, ploidy from H&E. Validates our Part A/visibility framing as natural to
   the data. Sharpest variants: Grok's OCCAMS-teacher -> surveillance-biopsy
   transfer (does PREDICTED genome-doubling in non-dysplastic Barrett's mark
   future progressors?); Kimi's 'does baseline morphology predict the FUTURE
   copy-number landscape at progression?'; Gemini's spatial clonal-
   heterogeneity index mapped onto tiles.
3. **LLM-jury report-derived supervision** (8/10) — our Ch4, independently
   reinvented by nearly every model. Extension we don't do: run the jury over
   the 13,645-report Barrett's specialist database to build a NATURAL-HISTORY
   dataset — real-world transition rates between dysplasia states (Terra-Pro),
   a text-only progression-risk baseline (Qwen3.8), active-learning triage of
   which unimaged patients to scan (Qwen3.7).
4. **Cross-foundation-model disagreement as an uncertainty biomarker** (7/10)
   — we hold five encoders' embeddings for every slide; per-slide inter-model
   disagreement as a signal for ambiguous histology, label noise, biopsy
   adequacy, even progression risk. Cheap (features exist) and connects
   directly to our unsure-holdout finding that model confidence fails on
   ambiguous cases.
5. **Report-slide vision-language alignment** (7/10) — contrastive pretraining
   on the 9,517 pan-cancer report+slide pairs, then zero-shot grading /
   semantic slide retrieval / 'virtual re-review' on ERIN. Chapter-scale, H200-
   suited. Grok's bold variant: a local 120B LLM as slide-report consistency
   auditor flagging possible missed dysplasia.
6. **Encoder benchmark / domain-shift harmonisation** (6/10) — our encoder
   sweep, plus batch-effect characterisation across cohorts we haven't done.

## The meta-finding

Only 2/10 unprimed models proposed the fusion question ('does adding modality
X to histology beat histology alone?') as a central framing. The blank-slate
consensus instead treats modality pairs as TEACHER AND STUDENT — cross-modal
prediction, distillation, weak supervision — not as fusion inputs. Given this
data, 'does fusion help?' is a choice, not the obvious question; the obvious
questions are the ones our thesis drifted toward anyway (visibility, report
supervision, replication). This independently corroborates the reframe: the
thesis's post-reframe shape matches what unprimed models say this data is FOR.

## Strongest ideas we currently have no plan item for

- Longitudinal trajectory modelling (cluster 1) — biggest gap; ERIN is
  uniquely suited and it is the clinically deployable framing of surveillance.
- Predicted-WGD-in-Barrett's as a progression marker (Grok, cluster 2) —
  bridges Ch2's visibility result to SWG's progression endpoint.
- Barrett's-database natural-history extraction (cluster 3) — CPU-only,
  13,645 reports already exported, jury already built.
- Cross-FM disagreement biomarker (cluster 4) — near-free given extracted
  features.

## Small-vs-big observation

Same as the primed round: small models found the same clusters; the frontier
premium was in twist quality (Terra-Pro's digital twin, Grok's teacher-student
transfer and consistency auditor, Kimi's future-CNA-landscape question).

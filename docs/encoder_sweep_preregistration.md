# Encoder sweep: pre-registered design (EXECUTION_PLAN 1.7)

Written 2026-08-19, before any multi-encoder result exists.

## Question

Are this thesis's multimodal conclusions encoder-invariant? Published benchmarks
(PathBench, eva) report no consistently winning pathology foundation model; the
sweep tests whether our *fusion deltas* — not just absolute performance — survive
changing the histology representation.

## Fixed grid

- Encoders: UNI2-h, Virchow2, GigaPath (weights pending R.1 HF login); H-Optimus-0
  added if access granted. No further additions mid-sweep.
- Aggregators: mean-pool and ABMIL.
- Tasks: exactly the chapters' pre-registered tasks (SWG progression; OCCAMS v3
  survival; TCGA-OAC survival; ERIN grade primary). No new tasks.
- Extraction via Trident where the encoder is supported; our extract_one.py
  otherwise; identical tile grid per slide across encoders.

## Analysis rules

- The headline result of every chapter remains its pre-registered primary config
  (UNI2 + ABMIL). The sweep contextualises; it never replaces.
- AMENDED 2026-08-25 (review finding, DeepSeek; joint reframe session): the rule
  above insulated headline claims from falsification. New rule: if any swept
  encoder's fusion delta flips sign relative to the primary config's, the
  chapter's claim is DOWNGRADED to encoder-conditional and must say so wherever
  the headline number is cited. The headline number itself still does not change.
- Report the FULL distribution of per-encoder fusion deltas (table + dot plot),
  never a best-of. No per-encoder significance claims; the estimand is the range.
- Encoder mixes: after single-encoder results only, top-2 concat + ensemble; four
  runs maximum.
- "Encoder-invariant" claim requires all encoders' fusion deltas to agree in sign
  with the primary config's.

## Budget

Extraction is the only real cost: ~25 GPU-h per encoder per 1,000-slide cohort
(measured, UNI2/L40S, 512-tile cap). Grid ceiling ~200 GPU-h across cuda+h200 as
per-slide race-to-run jobs. Downstream heads are CPU.

## Deviations recorded

- 2026-08-25 (wave-2 review): the grid gained H-Optimus-0 (pre-declared,
  conditional on access — arguably compliant) and Phikon-v2 (NOT pre-declared —
  a deviation). Both additions were made before their results existed, for
  coverage, not because results disappointed; but the freeze rule was violated
  and the sweep must be described as "extended grid" wherever cited.

## Not allowed post hoc

Adding encoders because results disappoint; promoting a non-primary encoder to
headline; dropping a cohort from the sweep without recording it here as a deviation.

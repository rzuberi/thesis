# Review round 7c: robustness of the R49 per-endoscopy gate

Status: PRE-SPECIFICATION (written 2026-10-17). Nothing below has been run. Results are appended under the line at the end in a later commit; this section is not edited afterwards.

## Why

The authors propose making the R49 gate the manuscript's headline. R49 is specified in `docs/paper_review_round7_analyses.md` (724ff97; results cd57fb6):
- endoscopy score = maximum L-IMG over the endoscopy's pre-event samples;
- per-fold sample-level t_low and t_high;
- in the middle band, the highest-scoring sample is sequenced and the endoscopy is called by its L-LATE at t_seq.

R49 was proposed after the sample-level triage's results were seen, and specified before it was run. A wider nested search (`docs/paper_review_round7b_gate.md`, 16d6902) did not hold up. This document fixes R49 exactly as it is and gives it the same robustness scrutiny the triage received (R33 Claim T rows).

## Primary comparison

- **Endpoint.** R49 against B\*-endo (sequence all samples; flag the endoscopy if any sample's L-LATE is positive at the B\* threshold).
- **Population.** All 288 pre-event endoscopies.
- **Reported:** Δ endoscopy sensitivity with two-sided CI and one-sided bound against −0.05; Δ endoscopy specificity; share of samples sequenced; share of endoscopies with ≥ 1 sample sequenced; patient columns.

Also against (B)-endo, the sample-level triage aggregated to endoscopies, C\*-endo (H&E alone at matched specificity, flag if any sample positive), and random-one at matched endoscopy specificity (as R46).

## Robustness table (same rows as R33 Claim T where stored predictions allow)

For each row, R49 is recomputed on that row's predictions, cut-offs and population. Comparators are recomputed the same way. Each row reports the primary comparison.

1. NDBE-only samples.
2. Never-dysplastic patients.
3. Earliest pre-event endoscopy per patient.
4. Endoscopies with ≥ 2 samples.
5. Excluding progressor samples within 1 year of the event.
6. Cut-off grid: t_low at 90/95/98% × t_high at 85/90/95% (9 cells, primary 95/90).
7. Slides with < 256 tissue tiles, and with ≥ 256 (an endoscopy is assigned by its highest-scoring sample's stratum; also reported restricting to endoscopies whose samples are all in one stratum).
8. Package copy-number features (joint rebuild).
9. Per-sample segmentation (R36).
10. H-optimus-0 extractor (stored predictions).
11. λ by deviance (B5).
12. Tissue- and year-adjusted gate scores (R32 rule).
13. Label rows: R38(a) sheet-flagged samples excluded; R53 database event dates; R43(a), (b) and (c) refits; R54 relabel; R55 background > 25% excluded.
14. Cohort rows: R52(a) and R52(b).
15. Inference rows:
    - between-repeat variance added (as R33);
    - per-repeat bounds (how many of the 10 within −0.05);
    - the refit bootstrap if stored refit outer/inner predictions and cut-offs exist for every draw. If they do not exist, this row is reported as "not available" and is not run.

Rows whose stored predictions do not exist are reported as "not available", not refitted.

## Summary rule (reporting only)

Report how many rows are within −0.05, how many fail by a shift (two-sided CI entirely below 0) and how many fail by width. No pass/fail threshold is set for promoting R49. That decision is the authors', and the full table is reported whatever it shows.

## Scripts and running

- **Script:** `scripts/paper_plan/rv7c_gate_rob.py`, reusing `rv7b_gate.py` (the R49 variant and the endoscopy comparators) and the R33 row loaders of `rv4_round4.py` / `rv6_round6.py`.
- **Execution:** cluster jobs via `scripts/cluster/campaign.sh`, prefix `rv7c`.
- **Outputs:** aggregates to `results/paper_final/review_round7c/`; results appended below by `rv7c_render.py`.

---

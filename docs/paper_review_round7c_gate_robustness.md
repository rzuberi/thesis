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

## Results

Rendered by `scripts/paper_plan/rv7c_render.py` from `results/paper_final/review_round7c/` (aggregate results ced4088). R49 exactly as in round 7 (max L-IMG endoscopy score, the triage's per-fold t_low / t_high / t_seq, top-L-IMG sample sequenced in the middle band). Single model = per-repeat values averaged over the 10 repeats; patient bootstrap 2,000 draws (`RandomState(0)`) with fitted models and cut-offs fixed; bound = one-sided 95% lower bound (5th percentile). Unit = pre-event endoscopy. No model was refitted for this item (refit rows read stored round-2 / round-4 / round-7 refit predictions).

| Item | Status |
|---|---|
| primary comparison (R49 against B\*-endo) and the other comparators | DONE |
| 1. NDBE-only samples | DONE |
| 2. never-dysplastic patients | DONE |
| 3. earliest pre-event endoscopy per patient | DONE |
| 4. endoscopies with ≥ 2 samples | DONE |
| 5. excluding progressor samples within 1 year of the event | DONE |
| 6. cut-off grid: t_low 90% / t_high 85% | DONE |
| 6. cut-off grid: t_low 90% / t_high 90% | DONE |
| 6. cut-off grid: t_low 90% / t_high 95% | DONE |
| 6. cut-off grid: t_low 95% / t_high 85% | DONE |
| 6. cut-off grid: t_low 95% / t_high 90% (primary cell) | DONE |
| 6. cut-off grid: t_low 95% / t_high 95% | DONE |
| 6. cut-off grid: t_low 98% / t_high 85% | DONE |
| 6. cut-off grid: t_low 98% / t_high 90% | DONE |
| 6. cut-off grid: t_low 98% / t_high 95% | DONE |
| 7. < 256 tissue tiles (endoscopy by its top-L-IMG sample) | DONE |
| 7. ≥ 256 tissue tiles (endoscopy by its top-L-IMG sample) | DONE |
| 7. < 256 tissue tiles (all samples of the endoscopy in the stratum) | DONE |
| 7. ≥ 256 tissue tiles (all samples of the endoscopy in the stratum) | DONE |
| 8. package copy-number features (joint rebuild) | DONE |
| 9. per-sample segmentation (R36) | DONE |
| 10. H-optimus-0 extractor (F5, stored predictions) | DONE |
| 11. λ by deviance (B5) | DONE |
| 12. tissue- and year-adjusted gate scores (R32b rule) | DONE |
| 13. R38(a): sheet 'excluded' flag removed | DONE |
| 13. R53: database event dates | DONE |
| 13. R43(a): non-progressor samples < 1 year before last endoscopy, refit | DONE |
| 13. R43(b): < 2 years, refit | DONE |
| 13. R43(c): later-HGD non-progressor patient, refit | DONE |
| 13. R54: later-disease relabel, refit | DONE |
| 13. R55: background share > 25% excluded | DONE |
| 14. R52(a): + 17 same-block samples, refit | DONE |
| 14. R52(b): + 24 samples, refit | DONE |
| 15. between-repeat variance added (as R33) | DONE |
| 15. per-repeat bounds (repeats within −0.05 of 10) | DONE |
| 15. refit bootstrap (F3, 200 draws) | DONE |

### Primary comparison

288 pre-event endoscopies (88 progressor), 571 samples, 75 patients (32 progressor). R49 endoscopy bands (per repeat): low 0.180, middle 0.505, high 0.315.

| Rule | Endoscopy sens [95% CI] | Endoscopy spec [95% CI] | Samples sequenced | Endoscopies sequenced | Progressor patients missed (of 32) / non-progressor flagged (of 43) |
|---|---|---|---|---|---|
| **R49 gate** | 0.907 [0.861, 0.951] | 0.560 [0.475, 0.645] | 0.255 | 0.505 | 0.9 / 31.8 |
| B\*-endo (sequence all, B\* threshold) | 0.923 [0.873, 0.962] | 0.530 [0.431, 0.629] | 1.000 | 1.000 | 0.8 / 31.7 |
| (B)-endo (sequence all, (B) threshold) | 0.876 [0.803, 0.935] | 0.640 [0.552, 0.726] | 1.000 | 1.000 | 1.3 / 28.5 |
| sample-level triage, aggregated | 0.909 [0.865, 0.952] | 0.549 [0.460, 0.637] | 0.458 | 0.597 | 0.9 / 32.0 |
| C\*-endo (H&E alone, training-matched) | 0.890 [0.837, 0.939] | 0.541 [0.474, 0.615] | 0.000 | 0.000 | 1.0 / 35.4 |
| random-one, matched to R49's endoscopy specificity | 0.931 [0.878, 0.968] | 0.560 [0.477, 0.648] | 0.504 | 1.000 | 1.0 / 31.8 |
| random-one, own threshold | 0.827 [0.742, 0.901] | 0.740 [0.673, 0.805] | 0.504 | 1.000 | 2.2 / 25.1 |

| R49 − | Δ endoscopy sens [95% CI] | Bound | Within −0.05 | Δ endoscopy spec [95% CI] | Δ share of samples sequenced [95% CI] | Δ share of endoscopies sequenced | Δ patients missed / flagged |
|---|---|---|---|---|---|---|---|
| B\*-endo (sequence all, B\* threshold) | -0.016 [-0.044, +0.008] | -0.038 | yes | +0.030 [-0.001, +0.068] | -0.745 [-0.783, -0.705] | -0.495 | +0.1 / +0.1 |
| (B)-endo (sequence all, (B) threshold) | +0.031 [-0.008, +0.074] | -0.001 | yes | -0.080 [-0.112, -0.048] | -0.745 [-0.783, -0.705] | -0.495 | -0.4 / +3.3 |
| sample-level triage, aggregated | -0.002 [-0.008, +0.000] | -0.006 | yes | +0.011 [+0.005, +0.019] | -0.204 [-0.239, -0.164] | -0.092 | +0.0 / -0.2 |
| C\*-endo (H&E alone, training-matched) | +0.017 [-0.025, +0.056] | -0.017 | yes | +0.019 [-0.038, +0.070] | +0.255 [+0.217, +0.295] | +0.505 | -0.1 / -3.6 |
| random-one, matched to R49's endoscopy specificity | -0.024 [-0.058, +0.016] | -0.052 | no | +0.000 [-0.004, -0.001] | -0.250 [-0.295, -0.212] | -0.495 | -0.1 / -0.0 |
| random-one, own threshold | +0.080 [+0.033, +0.138] | +0.039 | yes | -0.180 [-0.222, -0.140] | -0.250 [-0.295, -0.212] | -0.495 | -1.3 / +6.7 |

### Robustness table

Each row recomputes R49 and B\*-endo on that row's predictions, cut-offs and population (the R33 Claim T definition of the row; see the implementation notes). Fails by: shift = two-sided 95% CI entirely below 0; width = CI includes 0 but the bound is below −0.05.

| Item | Row | Endoscopies (progressor) / samples / patients (progressor) | R49 endo sens / spec | Δ endo sens vs B\*-endo [95% CI] | Bound | Within −0.05 | Verdict | Δ endo spec vs B\*-endo | Samples sequenced: R49 / triage | Endoscopies sequenced (R49) | Δ endo sens vs triage (bound) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| — | primary: all pre-event endoscopies (reference) | 288 (88) / 571 / 75 (32) | 0.907 / 0.560 | -0.016 [-0.044, +0.008] | -0.038 | yes | (reference) within | +0.030 | 0.255 / 0.458 | 0.505 | -0.002 (-0.006) |
| 1 | NDBE-only samples | 240 (68) / 438 / 71 (28) | 0.918 / 0.544 | -0.015 [-0.046, +0.006] | -0.039 | yes | within | +0.028 | 0.288 / 0.491 | 0.526 | -0.003 (-0.007) |
| 2 | never-dysplastic patients | 105 (33) / 197 / 33 (15) | 0.873 / 0.631 | -0.006 [-0.026, +0.015] | -0.023 | yes | within | +0.050 | 0.277 / 0.441 | 0.519 | +0.000 (+0.000) |
| 3 | earliest pre-event endoscopy per patient | 75 (32) / 140 / 75 (32) | 0.872 / 0.612 | -0.009 [-0.050, +0.023] | -0.043 | yes | within | +0.049 | 0.261 / 0.460 | 0.487 | -0.006 (-0.018) |
| 4 | endoscopies with ≥ 2 samples | 146 (40) / 429 / 64 (25) | 0.940 / 0.484 | -0.017 [-0.045, +0.003] | -0.040 | yes | within | +0.032 | 0.172 / 0.450 | 0.505 | -0.007 (-0.022) |
| 5 | excluding progressor samples within 1 year of the event | 276 (76) / 542 / 72 (29) | 0.905 / 0.560 | -0.005 [-0.021, +0.012] | -0.019 | yes | within | +0.030 | 0.264 / 0.469 | 0.518 | -0.003 (-0.007) |
| 6 | cut-off grid: t_low 90% / t_high 85% | 288 (88) / 571 / 75 (32) | 0.894 / 0.580 | -0.017 [-0.056, +0.014] | -0.048 | yes | within | +0.030 | 0.175 / 0.298 | 0.346 | +0.000 (+0.000) |
| 6 | cut-off grid: t_low 90% / t_high 90% | 288 (88) / 571 / 75 (32) | 0.887 / 0.611 | -0.014 [-0.052, +0.020] | -0.045 | yes | within | +0.031 | 0.209 / 0.342 | 0.415 | +0.000 (+0.000) |
| 6 | cut-off grid: t_low 90% / t_high 95% | 288 (88) / 571 / 75 (32) | 0.865 / 0.645 | -0.009 [-0.038, +0.016] | -0.033 | yes | within | +0.023 | 0.249 / 0.401 | 0.494 | +0.000 (+0.000) |
| 6 | cut-off grid: t_low 95% / t_high 85% | 288 (88) / 571 / 75 (32) | 0.917 / 0.525 | -0.016 [-0.045, +0.012] | -0.040 | yes | within | +0.024 | 0.220 / 0.414 | 0.437 | -0.002 (-0.006) |
| 6 | cut-off grid: t_low 95% / t_high 90% (primary cell) | 288 (88) / 571 / 75 (32) | 0.907 / 0.560 | -0.016 [-0.044, +0.008] | -0.038 | yes | within | +0.030 | 0.255 / 0.458 | 0.505 | -0.002 (-0.006) |
| 6 | cut-off grid: t_low 95% / t_high 95% | 288 (88) / 571 / 75 (32) | 0.895 / 0.603 | -0.015 [-0.043, +0.012] | -0.038 | yes | within | +0.036 | 0.295 / 0.517 | 0.585 | -0.001 (-0.003) |
| 6 | cut-off grid: t_low 98% / t_high 85% | 288 (88) / 571 / 75 (32) | 0.936 / 0.482 | -0.011 [-0.026, +0.005] | -0.024 | yes | within | +0.020 | 0.266 / 0.542 | 0.527 | -0.005 (-0.013) |
| 6 | cut-off grid: t_low 98% / t_high 90% | 288 (88) / 571 / 75 (32) | 0.927 / 0.514 | -0.008 [-0.021, +0.005] | -0.019 | yes | within | +0.023 | 0.300 / 0.586 | 0.595 | -0.003 (-0.010) |
| 6 | cut-off grid: t_low 98% / t_high 95% | 288 (88) / 571 / 75 (32) | 0.914 / 0.567 | -0.009 [-0.023, +0.005] | -0.021 | yes | within | +0.030 | 0.340 / 0.645 | 0.675 | -0.003 (-0.010) |
| 7 | < 256 tissue tiles (endoscopy by its top-L-IMG sample) | 142 (39) / 309 / 67 (25) | 0.926 / 0.544 | -0.005 [-0.018, +0.006] | -0.016 | yes | within | +0.034 | 0.233 / 0.454 | 0.508 | +0.000 (+0.000) |
| 7 | ≥ 256 tissue tiles (endoscopy by its top-L-IMG sample) | 146 (49) / 262 / 63 (25) | 0.892 / 0.577 | -0.024 [-0.072, +0.018] | -0.063 | no | fails: width | +0.027 | 0.280 / 0.463 | 0.503 | -0.004 (-0.012) |
| 7 | < 256 tissue tiles (all samples of the endoscopy in the stratum) | 98 (27) / 165 / 58 (20) | 0.926 / 0.569 | -0.004 [-0.022, +0.010] | -0.019 | yes | within | +0.038 | 0.296 / 0.430 | 0.499 | +0.000 (+0.000) |
| 7 | ≥ 256 tissue tiles (all samples of the endoscopy in the stratum) | 117 (40) / 173 / 54 (21) | 0.905 / 0.599 | -0.013 [-0.071, +0.031] | -0.060 | no | fails: width | +0.022 | 0.332 / 0.495 | 0.491 | +0.000 (+0.000) |
| 8 | package copy-number features (joint rebuild) | 288 (88) / 571 / 75 (32) | 0.939 / 0.594 | -0.013 [-0.035, +0.008] | -0.032 | yes | within | +0.010 | 0.255 / 0.458 | 0.505 | -0.005 (-0.009) |
| 9 | per-sample segmentation (R36) | 288 (88) / 571 / 75 (32) | 0.917 / 0.508 | -0.008 [-0.026, +0.007] | -0.023 | yes | within | +0.036 | 0.255 / 0.458 | 0.505 | -0.005 (-0.011) |
| 10 | H-optimus-0 extractor (F5, stored predictions) | 288 (88) / 571 / 75 (32) | 0.918 / 0.497 | -0.011 [-0.031, +0.005] | -0.028 | yes | within | +0.004 | 0.324 / 0.668 | 0.642 | +0.000 (+0.000) |
| 11 | λ by deviance (B5) | 288 (88) / 571 / 75 (32) | 0.919 / 0.533 | -0.005 [-0.018, +0.009] | -0.016 | yes | within | +0.021 | 0.280 / 0.526 | 0.555 | -0.003 (-0.010) |
| 12 | tissue- and year-adjusted gate scores (R32b rule) | 288 (88) / 571 / 75 (32) | 0.916 / 0.546 | -0.009 [-0.031, +0.013] | -0.027 | yes | within | +0.018 | 0.291 / 0.577 | 0.577 | -0.003 (-0.009) |
| 13 | R38(a): sheet 'excluded' flag removed | 263 (70) / 514 / 71 (28) | 0.909 / 0.569 | -0.006 [-0.021, +0.010] | -0.019 | yes | within | +0.032 | 0.267 / 0.468 | 0.522 | +0.000 (+0.000) |
| 13 | R53: database event dates | 284 (84) / 561 / 74 (31) | 0.902 / 0.560 | -0.017 [-0.046, +0.008] | -0.041 | yes | within | +0.030 | 0.257 / 0.461 | 0.508 | -0.002 (-0.007) |
| 13 | R43(a): non-progressor samples < 1 year before last endoscopy, refit | 247 (88) / 478 / 75 (32) | 0.892 / 0.553 | +0.000 [-0.010, +0.011] | -0.009 | yes | within | +0.019 | 0.269 / 0.484 | 0.520 | +0.000 (+0.000) |
| 13 | R43(b): < 2 years, refit | 238 (88) / 456 / 75 (32) | 0.902 / 0.574 | -0.001 [-0.011, +0.009] | -0.009 | yes | within | +0.019 | 0.268 / 0.484 | 0.514 | -0.001 (-0.003) |
| 13 | R43(c): later-HGD non-progressor patient, refit | 284 (88) / 564 / 74 (32) | 0.922 / 0.563 | -0.000 [-0.018, +0.019] | -0.015 | yes | within | +0.027 | 0.258 / 0.461 | 0.512 | -0.001 (-0.003) |
| 13 | R54: later-disease relabel, refit | 278 (92) / 526 / 72 (33) | 0.908 / 0.489 | +0.000 [-0.012, +0.011] | -0.009 | yes | within | +0.017 | 0.289 / 0.511 | 0.547 | +0.000 (+0.000) |
| 13 | R55: background share > 25% excluded | 277 (84) / 536 / 75 (32) | 0.902 / 0.566 | -0.017 [-0.048, +0.008] | -0.041 | yes | within | +0.033 | 0.263 / 0.462 | 0.509 | -0.002 (-0.007) |
| 14 | R52(a): + 17 same-block samples, refit | 290 (90) / 577 / 77 (34) | 0.917 / 0.578 | -0.003 [-0.015, +0.009] | -0.014 | yes | within | +0.018 | 0.264 / 0.481 | 0.525 | -0.001 (-0.003) |
| 14 | R52(b): + 24 samples, refit | 294 (94) / 582 / 79 (36) | 0.924 / 0.585 | +0.009 [-0.004, +0.022] | -0.002 | yes | within | +0.023 | 0.257 / 0.464 | 0.508 | -0.002 (-0.006) |
| 15 | between-repeat variance added (as R33) |  |  | -0.016 [-0.061, +0.029] | -0.054 | no | fails: width | +0.031 | 0.255 | 0.505 |  |
| 15 | per-repeat bounds (repeats within −0.05 of 10) | | | per repeat -0.034 to +0.023 | -0.075 to +0.000 | 3 of 10 | (count) | | | | |
| 15 | refit bootstrap (F3, 200 draws) |  |  | -0.012 [-0.080, +0.054] | -0.072 | no | fails: width | +0.012 | 0.293 | 0.578 |  |

Refit bootstrap: Monte Carlo SE of the 5th percentile 0.0073; share of the 200 draws with Δ below −0.05: 0.100; held-out pre-event endoscopies per draw median 286 (range 244–330).

Tissue strata: for 0.083 of the 288 endoscopies the stratum of R49's per-repeat top sample differs from that of the repeat-averaged top sample (the assignment used) in at least one repeat.

### Summary (reporting only)

Of 34 robustness rows (items 1–15; the primary row and the per-repeat count row are not counted): **30 within −0.05**, **0 fail by a shift** (CI entirely below 0), **4 fail by width**, **0 not available**. R49 sequences fewer samples than the sample-level triage in 32 of the rows where both are reported. No pass/fail threshold is set; whether R49 is promoted is the authors' decision.

### Checks

- R49 through this code: 0.907, 0.560, 0.255, 0.505, 0.900, 31.800 (R49: 0.907, 0.560, 0.255, 0.505, 0.900, 31.800; endoscopy sens, spec, samples, endoscopies, patients missed, flagged); reproduced: yes; sensitivity CI [0.861, 0.951] (R49 [0.861, 0.951]). Against the pre-specification's 0.907 / 0.560, 25.5% of samples, 50.5% of endoscopies: reproduced: yes.
- B\*-endo: 0.923, 0.530 (expected 0.923, 0.530); reproduced: yes.
- Sample-level triage aggregated: 0.909, 0.549, 0.458, 0.597, 0.900, 32.000 (R49: 0.909, 0.549, 0.458, 0.597, 0.900, 32.000); reproduced: yes. Random-one at its own threshold: 0.827, 0.740 (R46: 0.827, 0.740); reproduced: yes.
- Cut-off grid primary cell (95 / 90) equals the primary row (rules, deltas, between-repeat block and counts identical): yes.
- Primary against round 7b's apparent R49-variant row (same population and bootstrap): 0.907, 0.560, 0.255, 0.505, 0.900, 31.800, -0.016, -0.038 (7b: 0.907, 0.560, 0.255, 0.505, 0.900, 31.800, -0.016, -0.038; the last two = Δ endoscopy sens vs B\*-endo and bound); reproduced: yes.
- Row 'NDBE-only' against round 7b's apparent R49-variant row on the same population: 0.918, 0.544, 0.288, 0.526, 0.900, 31.300, -0.015, -0.039 (7b: 0.918, 0.544, 0.288, 0.526, 0.900, 31.300, -0.015, -0.039); reproduced: yes.
- Row '≥ 2 samples' against round 7b's apparent R49-variant row on the same population: 0.940, 0.484, 0.172, 0.505, 0.700, 27.200, -0.017, -0.040 (7b: 0.940, 0.484, 0.172, 0.505, 0.700, 27.200, -0.017, -0.040); reproduced: yes.
- Row 'R52(a)' against round 7b's apparent R49-variant row on the same population: 0.917, 0.578, 0.264, 0.525, 0.900, 31.200, -0.003, -0.014 (7b: 0.917, 0.578, 0.264, 0.525, 0.900, 31.200, -0.003, -0.014); reproduced: yes.
- Refit bootstrap: the sample-level triage − B\* Δ sensitivity re-derived from the stored F3 draws, mean and 5th percentile -0.018, -0.069 (R33 row 18: -0.018, -0.069).

### Implementation notes

- R49, B\*-endo, (B)-endo, the aggregated triage, the random-one rules and the bootstrap are the rv7_round7.py r49 / rv7b_gate.py merge code, unchanged; C\*-endo = the training-matched C\* call (L-IMG at the triage's training specificity, `matched_calls`) with the endoscopy flagged if any sample is positive, sequencing nothing. Random-one matched = one L-LATE threshold per seed × repeat, pooled across folds, giving R49's endoscopy specificity in that repeat (re-set in each draw, as R46).
- Row cut-offs follow the R33 Claim T implementation of each row. Rows that R33 scored on stored calls (never-dysplastic, earliest endoscopy, excluding progressor samples within 1 year, tissue strata, R38(a), R53, R55) keep the primary cut-offs, B\* and calls and change only the evaluated samples; R49 is then recomputed on the remaining samples of each endoscopy (endoscopy score = max over its remaining pre-event samples; endoscopies left with no sample drop out). Rows with their own predictions or population (NDBE, package features, R36, F5, deviance λ, tissue- and year-adjusted gate, the refits) re-choose every cut-off and B\* on that row's training samples, as in R33.
- Earliest pre-event endoscopy (row 3) uses R33 row 13 (stored cut-offs; earliest = largest months-before-final), not round 7b (b), which re-chose cut-offs. Endoscopies with ≥ 2 samples (row 4) is not an R33 row; it follows round 7b (c) (cut-offs re-chosen on endoscopies with ≥ 2 pre-event samples).
- Tissue strata (row 7): the endoscopy keeps all its pre-event samples and is assigned by the tissue tiles of its top sample, taken as the sample with the highest L-IMG averaged over the 10 repeats (a fixed assignment; R49 sequences the per-repeat top sample, and the share of endoscopies where the two differ in stratum in some repeat is reported above). The 'pure' rows keep endoscopies whose samples all fall in one stratum.
- Tissue- and year-adjusted gate (row 12): the R32b residualised L-IMG (year and log tissue tiles, outer per repeat, inner per (repeat, fold)) replaces L-IMG everywhere in the gate (endoscopy score, bands, sequenced sample, C\*); the middle-band call stays the stored L-LATE, as in R32b.
- Label rows (13): R38(a) = the sheet's 'excluded' flag only (the R38 'also report' variant with 'remove' and 'inconsistency' is not a separate row); R53 = its primary 'on or after' row (the 14-day variant is not run); R43(a)–(c), R54 and R52(a)/(b) use the round-7 refit outer and inner predictions with all cut-offs re-chosen (the refit sets' own endoscopies).
- Inference rows (15): between-repeat variance = the R33 / R15 rule on the primary row (mean of the 10 per-repeat Δ ± z √(V_boot + V_rep)); per-repeat bounds = each repeat's own 5th-percentile bound (a count, so it is listed but not counted in the summary). The refit bootstrap is run because stored outer and inner predictions exist for all 200 F3 draws; the per-draw cut-offs are not stored files but are re-derived from each draw's stored inner predictions by the fixed R33 F3 rule (rv4_round4.py r33_f3, unchanged), which reproduces R33 row 18. Endoscopy units in a draw = (resampled patient copy, endoscopy).
- Summary verdicts: within = bound > −0.05; shift = not within and the two-sided 95% CI (percentile interval for the refit bootstrap, variance-inflated interval for the between-repeat row) entirely below 0; width = not within and the CI includes 0. No row was refitted and every needed stored prediction set existed, so nothing is 'not available'.
- Checks compare values at three decimals with a tolerance of 0.0015.

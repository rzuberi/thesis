# Review round 7b: exploring the per-endoscopy gate with nested selection

Status: PRE-SPECIFICATION (written 2026-10-17). Nothing below has been run. Results are appended under the line at the end in a later commit; this section is not edited afterwards.

## Why

R49 (`docs/paper_review_round7_analyses.md`, results cd57fb6) found that a per-endoscopy gate matched the sample-level triage per endoscopy while sequencing 25.5% of samples rather than 45.8%. That variant was chosen before it was run, but further variants are now explored after seeing it.

To keep the estimate honest:
1. The variant is selected **inside cross-validation**, using only each outer fold's training patients.
2. The headline estimate is the performance of that whole selection procedure on held-out patients.
3. Apparent (non-nested) results for every variant are reported as well, labelled as optimistic.

No ACE-B file is read. Frozen bundles and stored predictions are unchanged. Conventions as in `docs/paper_review_round6_analyses.md` (5c10c27).

## Unit and comparators

- **Unit:** pre-event endoscopies (288: 88 progressor, 200 non-progressor) with their pre-event samples. An endoscopy is positive (flagged) if the rule flags it. Endoscopy status = patient status.
- **Comparators at endoscopy level** (flag the endoscopy if any sample is called positive):
  - **B\*-endo:** sequence all samples, call each by L-LATE at the B\* threshold.
  - **(B)-endo:** as B\*-endo at the (B) threshold.
  - **Sample-level triage aggregated to endoscopies.**
  - **Random-one:** one random sample per endoscopy, called by L-LATE (R41 seeds). Reported at its own threshold and at the gate's endoscopy specificity (as R46).
  - **R49 gate** (the original variant).

## Variant grid (36 variants)

1. **Aggregation of L-IMG over the endoscopy's samples:** maximum; mean; mean of the top 2 (equal to the maximum when there is one sample).
2. **Cut-offs:**
   - **sample-level:** the per-fold t_low and t_high of the triage;
   - **endoscopy-level:** t_low at 95% and t_high at 90% training endoscopy-level sensitivity and specificity, computed on inner out-of-fold endoscopy scores of the training patients with the same aggregation.
3. **Which samples are sequenced in a middle-band endoscopy:**
   - the sample with the highest L-IMG;
   - the sample whose L-IMG is closest to the middle of the band (the most uncertain);
   - all samples of the endoscopy.
4. **Call for a sequenced middle-band endoscopy:** positive if any sequenced sample is positive by L-LATE at t_seq, or by L-CNV at its triage-matched threshold (`rv4` copy-number-only middle band rule).

Low-band endoscopies: all samples are cleared. High-band endoscopies are flagged without sequencing.

## Nested selection rule (fixed)

In each outer fold of each repeat:
1. Compute every variant on the **inner out-of-fold predictions of the training patients only**, at endoscopy level.
2. **Eligible:** the inner endoscopy sensitivity is at least that of B\*-endo on the same inner predictions minus 0.02, and the inner endoscopy specificity is at least B\*-endo's minus 0.05.
3. **Choose** the eligible variant with the lowest inner share of samples sequenced. Ties go to the simpler variant, in this order:
   - maximum before top-2 before mean;
   - sample-level before endoscopy-level cut-offs;
   - highest before uncertain before all;
   - L-LATE before L-CNV.
4. If no variant is eligible, use the sample-level triage.
5. Apply the chosen variant to the outer fold's held-out endoscopies.

## Primary reporting for this exploration

**Nested gate against B\*-endo** (single model, means over 10 repeats; patient bootstrap with fitted models and selections fixed):
- Δ endoscopy sensitivity with two-sided CI and one-sided bound, against the −0.05 margin;
- Δ endoscopy specificity;
- share of samples sequenced;
- share of endoscopies with ≥ 1 sample sequenced.

**Also reported:**
- the same against the sample-level triage, (B)-endo and random-one (own threshold, and matched endoscopy specificity);
- patient columns (progressor patients missed of 32; non-progressor patients flagged of 43);
- how often each variant was chosen across the 100 outer folds;
- the apparent results of all 36 variants on the outer predictions, labelled optimistic.

## Robustness of the nested gate

Same nested rule, re-run with:
- **(a)** NDBE-only samples (endoscopies keep their NDBE samples only);
- **(b)** the earliest pre-event endoscopy per patient;
- **(c)** endoscopies with ≥ 2 samples only;
- **(d)** the R52(a) cohort with the 8 progressors' same-block samples, using the R52(a) refit predictions;
- **(e)** between-repeat variance: the share of the 10 repeats in which the nested gate's bound against B\*-endo stays within −0.05, and the bound with the between-repeat variance added (as R33).

## Trade-off curve (descriptive)

Endoscopy sensitivity and specificity against share of samples sequenced over a 3 × 3 grid of cut-off quantiles (t_low at 90/95/98% sensitivity, t_high at 85/90/95% specificity) for:
- the nested gate's most-chosen variant;
- the sample-level triage;
- random-one.

## What follows from the result (fixed now)

- **If** the nested gate is within −0.05 of B\*-endo (bound) and sequences fewer samples than the sample-level triage, it becomes:
  - the manuscript's headline development result, described as "selected by nested cross-validation, after R49";
  - the proposed primary rule for ACE-B registration.

  The sample-level triage remains reported as the original pre-specified analysis.
- **Otherwise** the sample-level triage stays the headline, and the gate is reported as exploratory.

## Scripts and running

- **Script:** `scripts/paper_plan/rv7b_gate.py`, re-scoring stored outer and inner predictions. No refit, except reading the R52(a) refit outputs.
- **Execution:** cluster jobs via `scripts/cluster/campaign.sh`, prefix `rv7b`.
- **Outputs:** aggregates to `results/paper_final/review_round7b/`; results appended below by `rv7b_render.py`.

---

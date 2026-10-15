# Manuscript figures (draft v6): specification

Status: SPECIFICATION (written 2026-10-16), committed before any figure is drawn. Figures are descriptive displays of results already estimated and committed. No new estimand is introduced; where a panel needs a quantity not yet stored (e.g. a pooled ROC curve), it is computed from the stored held-out predictions with the stated rule, and the figure legend says so.

The display plan follows the round-5 internal review (Nature Medicine referee standard): six main figures and eight Extended Data figures. A pathologist-annotated tile figure is planned but not drawn here, because it needs pathologist review.

**Ground rules:**
- Row-level data stay on the cluster. Figures that need per-sample data are drawn there, and only image files (PNG 300 dpi and PDF) plus an aggregate source-data JSON per figure come back.
- No patient or sample identifiers appear in any figure; patients in Figure 4 are anonymous rows.
- Estimates shown are those in the committed results. Fold-stratified AUROCs label curves. Pooled ROC curves are drawn from repeat-mean held-out predictions and labelled as such.
- The cohort is never referred to by its internal short label.

**Style:**
- One consistent colour per model: L-IMG, L-CNV (shipped; per-sample; past-only; joint package), L-LATE, P, grade.
- One consistent colour per band: low, middle, high.
- 95% CIs shown wherever stored.

## Main figures

**Figure 1. Study design.**
- (a) CONSORT-style flow: 88 patients and 777 samples → 80 with slides (676) → 571 pre-event (75 patients, 32 progressors) → 438 NDBE pre-event, with exclusions at each step, including the 8 slide-less progressors.
- (b) Pipeline schematic: biopsy → H&E slide → 256 tiles → UNI2-h → L-IMG; DNA → sWGS → copy number (joint, per-sample or past-only segmentation) → L-CNV; L-LATE = mean.
- (c) The three-band rule on the H&E score axis: t_low, t_high, sequenced middle band and L-LATE call.
- (d) Timeline: distribution of pre-event biopsy times before the event (progressors) and before last follow-up (non-progressors).

**Figure 2. Discrimination.**
- (a) ROC curves (pooled repeat-mean held-out predictions) for L-IMG, L-CNV (shipped matrix), L-CNV (per-sample), L-LATE, P and raw grade. The legend gives the committed fold-stratified AUROCs with CIs. The triage single-model operating point and comparators (A), (B), (C), B\*, C\* and (D) are marked.
- (b) L-IMG score distributions by class (pre-event samples), with the median frozen t_low and t_high.
- (c) L-IMG versus L-CNV repeat-mean scores by class, with the within-class Spearman correlations.
- (d) Precision–recall curves for L-IMG, L-CNV and L-LATE at the cohort prevalence.

**Figure 3. H&E-first triage.**
- (a) Flow of pre-event samples by class into the low, middle and high bands (modal band) and final calls, with absolute counts.
- (b) Share sequenced against sensitivity for the H&E gate (single model), the H-optimus-0 gate, the permuted-label gate and the random gate (mean and 95% range over seeds). Points for (A), (B), (C), A\*, B\*, C\*, (D), and the 9 grid cells.
- (c) Per-patient outcomes by strategy: progressor patients missed and non-progressor patients flagged (means over repeats; range).
- (d) Predictive values against progressor-sample prevalence (0.5% to 30%): high-band PPV, low-band NPV and share sequenced, with CI ribbons.
- (e) Band stability: for each modal band and class, the distribution of repeats in the modal band.

**Figure 4. Patients over time.**
- (a) Swimmer plot, one anonymous row per patient (75), ordered by class and then time span. Pre-event biopsies are placed by time before the event or last follow-up, coloured by modal band, with grade shown by marker shape. Progressors' events are marked.
- (b) Time-dependent AUROC at 1, 3 and 5 years for grade, L-CNV, L-IMG and L-LATE, with CIs (stored).

**Figure 5. Copy-number segmentation.**
- (a) Genome-wide 5-Mb profiles of one progressor's earliest pre-event biopsy under joint, per-sample and past-only segmentation, with the patient's later HGD/IMC biopsy shown for reference. Choose the patient with the largest joint-versus-per-sample difference among progressors with a post-event sample; the patient is anonymous.
- (b) L-CNV AUROC with CIs by copy-number version (shipped matrix, joint package, past-only, per-sample) against L-IMG, with Δ and the one-sided bound.
- (c) Per-sample correlation between joint and per-sample features (raw 5-Mb tiles and final block), by class and by whether the patient has a later HGD/IMC sample.

**Figure 6. Robustness.**
- Forest plots of the two robustness tables (R33, plus R36 rows): triage − B\* Δ sensitivity and L-IMG − L-CNV ΔAUROC.
- Two-sided 95% CIs.
- The −0.05 margin drawn.
- Rows grouped by type: population, features, training, tissue, cut-offs, inference.
- Analyses specified before they were run, in rounds 2 and 4, are marked distinctly from the primary.

## Extended Data figures

| ED | Content | Source |
|---|---|---|
| 1 | Tissue amount: tile-count distributions by class; L-IMG score against log tiles by class (Spearman); AUROC by tissue stratum and tertile; tissue and year alone | R5, R18, R32 |
| 2 | Batch: batch × class composition (12 labels, single-class highlighted); within-batch AUROCs; embedding batch probe per batch | R31 |
| 3 | Scanner transfer: band shares and triage sensitivity and specificity before and after the label-free reset; AUROC per setting with CIs; training-size control | R4, F2, R19 |
| 4 | Calibration: decile plots of observed against predicted for L-CNV, L-IMG and L-LATE, with slopes; case–control caveat in the legend | R3 |
| 5 | Negative controls: distributions over 100 random seeds and 5 permutations of share sequenced, sensitivity and specificity, with the H&E gate marked | R25, F6 |
| 6 | Foundation models: UNI2-h, Virchow2, H-optimus-0 and Prov-GigaPath; robustness index, L-IMG AUROC and cross-scanner AUROC where run; triage share for UNI2-h and H-optimus-0 | scanner_robustness, F5 |
| 7 | Kaplan–Meier by Killcoyne risk class for P, L-CNV and L-LATE, with hazard ratios and CIs | risk_strata |
| 8 | Performance by time to event (< 1, 1–3, > 3 years) and by sample grade (NDBE, ID, LGD), from stored held-out predictions; descriptive, fold-stratified AUROC where both classes exist | stored predictions |

## Output

- Images: `paper/figures_v6/Fig{1..6}.{png,pdf}` and `paper/figures_v6/ED{1..8}.{png,pdf}`.
- Source data: `results/paper_final/figures_v6/<figure>.json`, aggregate values only.
- Scripts: `scripts/paper_plan/fig6_*.py`.

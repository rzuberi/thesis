# Project summaries (2026-08-26)

One paragraph per project; key numbers inline. Written at compute-closure time
(wave-3 gap review pending; R.4/R.5 human anchors pending).

## 1. Evaluation protocol & infrastructure (Ch1)
Frozen rules: patient-disjoint folds, paired bootstrap on every fusion delta,
shuffled-label controls with a pipeline-invalidation rule, negatives retained,
OOF contracts. Machinery: ABMIL clf/Cox trainers, race-to-run Slurm pattern,
five FM encoders extracted over every slide. Meta-lesson turned finding:
5-shuffle controls are noise; 50-perm nulls resolved two false alarms
(results/tcga_probe.json, occams_v3_shuffle.json).

## 2. SWG Barrett's fusion (Ch2 flagship)
150 pts / 707 biopsies, H&E + sWGS, strict pre-event LGD2+ endpoint, 7 families,
frozen folds. Late-mean fusion best (AUPRC 0.630 / AUC 0.774); beats
histology-alone on all three metrics, CIs excluding zero
(lgd2_final_pre_event_paired_differences.csv). Bounds: encoder-conditional
(vs GigaPath histology only calibration survives,
results/latemean_vs_gigapath_paired.json); winner's curse measured and small
(73% win rate, +0.027 optimism, results/swg_oof_analyses.json);
complementarity: CNV adds information (LRT p=0.007) but discrimination
unresolved at n=150. CNV importances map to TP53/EGFR/CCND1 arms
(data/lgd2_cnv_feature_gene_annotation.csv).

## 3. Genotype visibility from H&E (Ch2 Part A)
Matched-n learning curve across population strata
(results/visibility_curve.json): OAC at chance at every n (two cohorts;
combining them worsens it); gastric/GEJ real and growing (TP53 0.64, WGD 0.74).
"Adequate n" reading falsified — population effect. Companions: attention-shift
pair (conditioning redirects attention only where genomics is visible: TCGA
pool yes, OCCAMS no — results/attn_shift_occams.json) and WGD transfer
(resection-validated teacher INVERTS on surveillance biopsies,
results/wgd_transfer.json; SWG measured-CNV diagnosis in flight).

## 4. External replication & power map (Ch2/Ch5)
OCCAMS n=87 (attrition explained: 276 slides -> 145 survival -> 87 genomics)
and TCGA-OAC n=65: fusion null; pooled TCGA gain dissolves into population
heterogeneity. Power map (results/power_map.json): those cohorts cannot detect
deltas < ~0.075-0.10 at 80% power; real fusion effects run +0.01-0.04.
"Failure to replicate is largely failure to power" = Ch5 spine. PORPOISE
published baseline + transfer matrix in flight.

## 5. ERIN histology + clinical (Ch3)
2,280 imaged cases, all supervision from reports. Grade: hist 0.926
(near-ceiling); encoder sweep: fusion +0.011-0.015 CI-excluding-zero on 4/5
encoders (null on primary UNI2), early fusion consistently hurts
(results/erin_encoder_sweep.json). Progression (reframed primary): hist 0.819
(153/28); landmarked leakage ablation shows the clinical arm's signal was
index-date leakage — strictly-pre-index it is chance and fusion adds nothing
(results/erin_prog_ablation.json).

## 6. Report-derived supervision (Ch4 methodological core)
pathladder (rules; 96.5% TCGA grade accuracy; ~82% vs jury on ERIN, CANCER
over-call persists on negations — results/negation_revalidation.json) + 8-LLM
jury (kappa 0.90). Validations: jury- and pathladder-trained models
interchangeable downstream, feas-grader noise localized
(results/ch4_labelsource_xeval.json); no single LLM family load-bearing
(max 0.5% flips, results/lofo_jury.json); unsure quarantine justified — on the
206 ambiguous reports performance drops to ~0.70 and model confidence fails to
flag it (results/unsure_scoring.json + unsure_characterization.json). Scaled
to 13,645 DB reports (12,780 labelled). Pan-cancer external check in flight;
R.4 pathologist anchor pending.

## 7. Vision-language alignment (Ch4-adjacent method)
CLIP-style ERIN slide-report model: zero-shot grading 0.889 (supervised 0.926)
with no labels; TCGA transfer: semantics carry (site zero-shot 0.782) though
literal retrieval collapses under report-style shift
(results/vlm_pretrain.json, signal test results/vlm_alignment.json).

## 8. Longitudinal trajectories (appendix negative + seed)
Tested twice: ERIN (acquisition-limited) and SWG (dense serial data) — the
latest biopsy beats or matches every trajectory arm (results/swg_trajectory.json,
erin_trajectory.json). Snapshot sufficiency is real at these scales. Seed:
current H&E weakly predicts next-biopsy CNV complexity (rho 0.16, p=1.3e-4).

## 9. Barrett's natural history (paper-grade side product)
Transition matrix over 2,092 patients from jury-labelled reports (incl.
post-treatment CANCER->NDBE reversions), dwell times, text-only prognosis
0.696 at n=8,830 (results/barretts_history.json). Structured-truth validation
blocked on R.5 (grade-code map from Leanne).

## 10. Review meta-project
8 frontier families + 4 local models, two blind red-team waves (96 criticisms),
10-model improvement consultation + 10-model blank-slate ideation (160
proposals, ~27 distinct, 14 implemented). Produced the reframe, the fix-list
(all severity-5s addressed or human-blocked), pre-registration deviation
records, and the amendment-log discipline. Wave-3 compute-gap review is the
gate before writing.

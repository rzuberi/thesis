# Blank-slate implementation plan (2026-08-25, joint — Rehan approved all
# clusters except the Ch4 vision-language rebuild)

Destination honesty: these are appendix/paper candidates unless results earn
chapter status. Each item: design, data, script, jobs, decisive readout.
The report-slide contrastive/VLM cluster stays PARKED (excluded by Rehan).
Selection rule (Rehan, same day): implement NOVEL ideas as signal/feasibility
tests; skip reinventions of completed work unless they HARDEN it — 2.26 is
retained under the hardening clause (jury validated against structured truth
at 13k scale), all other retained items are novel; fusion re-runs, basic
probes, and encoder benchmarks were excluded as reinventions.

## 2.24 Longitudinal trajectory modelling (9/10 unprimed convergence)

Design: for every ERIN progression-cohort patient, build the sequence of
pooled UNI2 slide embeddings for all imaged timepoints up to the index date
(pooled cache exists: erin_pooled_uni2.npz). Three arms on identical
patient-disjoint folds: (a) index-slide-only logistic (snapshot baseline),
(b) trajectory-features logistic (index embedding + per-year embedding drift
+ last-step delta + n timepoints + span), (c) GRU over the padded sequence.
Endpoint: progressed_to_HGDplus. Paired bootstrap trajectory-vs-snapshot.
Secondary: next-timepoint upgrade prediction (grade >=LGD at t+1 from data
<=t) on the wider >=2-timepoint imaged cohort — larger n than progression.
Script: scripts/task_erin_trajectory.py. Jobs: epyc (CPU arms) + cuda (GRU).
Decisive: trajectory delta CI over snapshot excluding zero = the thesis gains
a genuinely new, clinically-framed result; null = snapshot sufficiency is
itself a finding for the surveillance-imaging discussion.

## 2.25 Predicted-WGD transfer: resection teachers -> surveillance biopsies

Design: train ABMIL WGD + TP53 teachers on the pooled TCGA(OAC+GEJ/STAD)
+ OCCAMS labelled resections (the visibility-ceiling machinery), sanity-check
by 5-fold CV (must reproduce ~0.77/0.70 ceiling), then retrain on all and run
inference on ERIN progression-cohort index slides. Readout: does predicted-WGD
stratify future progression (AUC + KM-style separation), and does it add to
histology risk (paired bootstrap over the hist-only progression model)?
Script: scripts/task_wgd_transfer.py. Jobs: cuda+h200 race pair.
Phase 2 (needs SWG per-sample feature+CNV table locations confirmed): same
inference on SWG biopsies where measured sWGS exists — direct validation of
predicted vs measured genomic state, plus Kimi's future-CNA-landscape
question. Recorded here as 2.25b, submitted after path confirmation.
Decisive: predicted-WGD marking progressors in biopsies would bridge Ch2's
visibility result to the surveillance question — strongest possible outcome
of this batch.

## 2.26 Barrett's-DB natural history + jury-at-scale validation

Design: run the pre-registered 8-model jury over the 13,645-report normalised
corpus (pathology_text_normalised_full.csv; llm_grade_shard.py already
supports this input), sharded per model x 4 shards = 32 GPU jobs. Analysis
job (submitted with afterany dependency): (i) VALIDATE jury grades against
the database's own structured dysplasiagradehistory table at 13k scale — the
largest jury-vs-structured-truth comparison available anywhere in the thesis;
(ii) per-patient longitudinal state sequences -> empirical transition rates
between NDBE/IND/LGD/HGD/CANCER (real-world natural history); (iii) text-only
progression risk baseline from grade trajectories.
Scripts: labeller/llm_grade_shard.py (reused) + scripts/task_barretts_history.py.
Decisive: (i) is a direct, human-independent external check on the jury that
partially answers the self-validation-loop criticism at scale; (ii) is a
paper-grade epidemiology table.

## 2.27 Cross-foundation-model disagreement biomarker

Design: pool each of the five encoders' tile features per ERIN slide, train
identical PCA64+logistic grade probes per encoder on shared folds, define
per-slide disagreement = std of the five OOF probabilities. Readouts:
correlation with jury entropy (label ambiguity), AUC for predicting
unsure-holdout membership, IND enrichment, and association with progression.
Script: scripts/task_fm_disagreement.py. Jobs: epyc (features exist; CPU).
Decisive: if FM disagreement flags the ambiguous stratum that model
confidence missed (unsure_scoring showed confidence fails there), we gain a
deployable triage signal and a novel methods contribution.

## Deferred within this batch

- 2.25b SWG-side transfer + future-CNA (path confirmation first).
- Cross-cohort batch-effect atlas: folded into the encoder-sweep write-up.
- Ch4 VLM rebuild: PARKED (Rehan exclusion).

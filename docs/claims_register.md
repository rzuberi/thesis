# Claims register

Every headline claim of the thesis as a numbered, falsifiable statement with
its evidence file. Written 2026-09-09 for the Astra gap review; maintained as
the writing-phase checklist. Numbers here are transcriptions — the attached
results JSONs are ground truth; any mismatch is a finding.

## Chapter 2 — multimodal fusion in Barrett's/OAC (replication)

- **C1.** In the SWG Barrett's cohort (image+CNV), late-mean fusion beats
  histology alone for progression (pre-registered confirmatory test;
  p_holm=0.0096, the ONLY confirmatory test surviving Holm).
  [results/closure_cpu.json, results/latemean_vs_gigapath_paired.json]
- **C2.** In OCCAMS (survival), fusion does not beat histology alone
  (p_holm=0.69). [results/closure_cpu.json, results/occams_v3.json]
- **C3.** In ERIN progression, fusion does not beat histology alone
  (p_holm=1.0). [results/closure_cpu.json]
- **C4.** The fusion nulls are not an artefact of encoder choice: under all 4
  tile encoders the fusion delta CIs cross zero on all survival cohorts.
  [results/encoder_sweep_surv.json]
- **C5.** Not an artefact of architecture: the published PORPOISE MMF
  underperforms its own AMIL baseline on our data (0.545 vs 0.566, delta
  −0.021) — the published-architecture escape hatch is closed.
  [results/porpoise_baselines.json]
- **C6.** Failure to replicate is largely failure to power: minimum detectable
  deltas are 0.075–0.10 while observed real deltas are +0.01–0.04.
  [results/power_map.json]
- **C7.** The pipeline is sound: permutation nulls land at 0.502/0.487 while
  real labels give 0.819 (p<0.014) and 0.679 (p<0.02).
  [results/perm_controls.json]
- **C8.** Winner's curse in arm selection is quantified: late_mean wins 72.8%
  of resamples with optimism +0.027. [results/swg_oof_analyses.json]
- **C9.** A WGD teacher transfers with INVERTED ranking to ERIN (AUC 0.315)
  and its predictions anti-correlate with measured CNV in SWG (rho −0.10,
  p=0.005): cross-cohort molecular distillation fails at the ranking level.
  [results/wgd_transfer.json]
- **C10.** SWG trajectory: image embeddings weakly predict FUTURE CNV state
  (rho 0.161, p=1.3e-4) — signal exists but is small.
  [results/swg_trajectory.json]

## Chapter 3/4 — LLM report labelling (P1 paper)

- **C11.** An 8-model local-LLM jury labels 7,149 reports: 6,867
  train-eligible, 204 unsure held out, 78 adjudicated; near-100% parse rates.
  [results/erin_jury_labels_summary.json, results/jury_corpus_analysis.json]
- **C12.** The jury is not hostage to any single model: leave-one-family-out
  flips ≤0.5% of labels (eligible-set Jaccard ≥0.979).
  [results/lofo_jury.json]
- **C13.** Jury uncertainty tracks genuine textual ambiguity: unsure reports
  have 3.3× the hedging rate (0.52 vs 0.16). [results/unsure_characterization.json]
- **C14.** External validity: the same jury pipeline agrees with human
  registry grades at 0.97–0.99 (two-tier) across TCGA ESCA/STAD/KIRC/BLCA.
  [results/pancancer_jury.json]
- **C15.** MDT-style deliberation ≥ independent voting: chair 98.7% vs 97.4%
  on adjudicated cases, zero conformity losses; caveat — chair confidence is
  uncalibrated on unsure cases (200/201 "confident"). [results/mdt_erin.json]
- **C16.** A deterministic keyword ladder (pathladder) trains models
  indistinguishable from jury-label-trained models downstream (p_holm=0.945).
  [results/closure_cpu.json]
- **C17.** Per-section jury: 32.0% of slides carry a different grade than
  their report's case-max — quantified label noise of the standard shortcut.
  [results/slide_labels_v2.json]
- **C18.** That noise is FREE at binary screening: case-max-trained 0.871 vs
  slide-label-trained 0.860 on slide truth (delta −0.010 [−0.028, +0.009]).
  [results/slide_vs_casemax.json]
- **C19.** At six-class grading, case-max is significantly BETTER (macro-AUC
  0.764 vs 0.722, delta −0.042 [−0.066, −0.019]; QWK null): with 35–82 slides
  per rare class, noisy-but-plentiful beats clean-but-scarce. Scaling
  reversal left as testable prediction. [results/svc_5class.json]
- **C20.** Jury labels support strong image models: grade classification AUC
  0.921 slide-level, 0.960 patient-level. [results/closure_cpu.json]
- **C21.** Label-generation change v2→v3 flips 103 patients' progression
  status — label provenance materially affects cohort composition and is
  reported, not hidden. [results/closure_cpu.json]

## Chapter 4/5 — VLM and discovery

- **C22.** CLIP-style report-slide alignment trains: retrieval R@1 16× chance;
  zero-shot grading 0.889 on ERIN test. [results/vlm_pretrain.json]
- **C23.** VLM transfer: TCGA site classification 0.782 but retrieval fails;
  SWG zero-shot vs pathologist grades 0.614 with retrieval 3× chance —
  transfer is partial and honest. [results/vlm_swg.json]
- **C24.** LLM case-finding works: EoE finder returns 26 diagnosed reports
  (17 patients) + 77 suspected (66 patients), 0 false EoE in 100
  keyword-negative controls. [results/eoe_finder.json]
- **C25.** Open-vocabulary phenotype extraction is viable: 844 distinct terms
  from 1,000 reports (pilot; full-corpus atlas not yet run).
  [results/phenotype_pilot.json]

## Methods (how every number above was produced)

- Patient-disjoint 5-fold CV throughout; folds frozen per cohort (hash/perm
  seed 0); identical folds shared by contrasted arms.
- Uncertainty: 1000-rep paired bootstrap on the SAME resample indices for
  deltas; percentile 95% CIs.
- Multiplicity: 4 pre-registered confirmatory tests under Holm (C1–C3 + C16);
  everything else labelled exploratory.
- Jury vote: majority accepted; near-splits → unsure held-out; hardest 78
  adjudicated manually (Claude, full text, on-cluster).
- Per-section consensus: grade needs ≥3/5 jurors; a section counts only if
  seen by ≥max(3, n−2) jurors; slide join via Shiv Sakthivel's
  section↔slide table + uuid.
- MIL: gated-attention ABMIL (512-d embed), Adam 1e-4, class-weighted CE
  (sqrt inverse frequency) for the 6-class run; 2000-tile subsampling.
- Survival: ABMIL-Cox / linear-Cox, Harrell's C, stratified folds.
- All LLM labelling is LOCAL (ollama on cluster GPUs); no patient text ever
  left the institutional network.

## Known limitations (already recorded — repeating these scores zero)

1. No pathologist ground-truth arm yet (human grading app live, uptake pending).
2. Rare-class slide counts tiny (IND 35, HGD 66, LGD 82) — 6-class contrasts
   are data-starved by construction.
3. Jury labels and slide labels share LLM provenance — circularity where one
   evaluates the other (external anchors: TCGA registry grades; adjudications).
4. ERIN is single-site; SWG small (n≈345/614 slide-rows P/NP; 171 patients);
   OCCAMS attrition 276→87 for the fusion set.
5. MDT chair confidence uncalibrated on unsure cases.
6. VLM trained and mostly evaluated on ERIN; transfer is partial.
7. 2.38b conclusion may invert at larger per-class n (stated as prediction).
8. Winner's curse on arm selection quantified but nonzero (+0.027 optimism).

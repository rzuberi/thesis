# EXECUTION PLAN — frozen 2026-08-19

**Rules.** This is the contract. Work is checked against it. Items may move to DONE
with evidence (a result file, a commit, a section of prose). The plan itself changes
only by joint decision between Rehan and Claude, recorded in the amendment log at the
bottom. Finishing an item ≠ permission to invent a replacement; new ideas go to the
PARKED list until jointly promoted.

**Phases are dependency classes, not dates.**
- Phase 0 — in flight: submitted and running; we wait, we don't touch.
- Phase 1 — unblocked: doable/submittable right now.
- Phase 2 — blocked on Phase 0/1 outputs.
- Phase 3 — blocked on Phase 2 results (writing that needs numbers).
- Phase 4 — end-game: needs everything.
- R — requires Rehan personally.

---

## Phase 0 — in flight (wait, monitor, don't touch)

- [~] 0.1 ERIN UNI2 extraction — 2,276/2,281 (2026-08-20 morning); 5 stragglers
      resubmitted on both GPU partitions (elements 619, 865, 1260, 1870, 1990)
- [ ] 0.2 SWG paper hardening work (Rehan's own track; Claude only assists on request)

## Phase 1 — unblocked now

### Experiments (submit)
- [x] 1.1 **OCCAMS v3** *(done 2026-08-19, results/occams_v3.json; deviation: shuffled controls omitted — noted for write-up; n=87 vs planned 141 needs explanation under 1.12)* — the pre-registered decisive Ch2 run: Cox-loss ABMIL over
      tile features, linear-Cox genomics arm, clinical-only arm (stage/age/treatment),
      late fusion; Harrell's C primary, patient-disjoint folds, bootstrap CIs; read
      strictly against docs/occams_v2_decision_tree.md. Done = results/occams_v3.json.
- [x] 1.2 **TCGA ABMIL fusion** *(done 2026-08-19, results/tcga_abmil.json)* — same machinery on TCGA-OAC (65 cases, CDR
      endpoints, native censoring). Done = results/tcga_fusion_abmil.json.
- [x] 1.3 **pathladder ERIN failure audit** *(DONE 2026-08-20: 80 cases adjudicated by Claude — 29 yes/50 no/1 unsure; pathladder negation window widened 60->130 (10 false CANCERs fixed, TCGA validation unchanged, 12 tests pass); feasibility grader 40/40 wrong on its side. Rehan spot-check of 10 flagged cases pending)* — explain CANCER over-call (1,304 vs 843):
      sample + categorise disagreeing reports, fix patterns, re-run corpus, re-validate
      on TCGA (accuracy must not regress). Done = audit note + updated distribution.
- [~] 1.4 **PORPOISE baseline** on OCCAMS + TCGA-OAC *(2026-08-25: repo cloned to
      phd/mahmood_lab/PORPOISE; ships splits for 5 cancer types only — no ESCA/
      STAD — so omics tables must be built via their Preprocessing.ipynb +
      signatures.csv; loader adaptation is a full-session task, next up)*.
      Done = results/porpoise_baselines.json.
- [x] 1.5 **CNV window→gene map** *(RESOLVED 2026-08-25: found already computed
      in release — lgd2_cnv_feature_gene_annotation.csv, 633 features with
      cancer-gene annotation; copied to data/, transcribed into swg_arm.md)*

### Writing (no dependencies)
- [x] 1.6 **ERIN Ch3 pre-registration** *(docs/erin_ch3_preregistration.md, 2026-08-19; amended by consensus-label decision)* — primary endpoint (grade vs progressed_to_HGDplus),
      arms, metrics, thresholds; same discipline as the OCCAMS decision tree.
- [x] 1.7 **Encoder-sweep pre-registration** *(docs/encoder_sweep_preregistration.md, 2026-08-19)* — grid (UNI2/Virchow2/GigaPath + gated
      additions), invariance question, full-distribution reporting rule, GPU budget.
- [ ] 1.8 **Ch2 Part A prose** — the two-cohort genotype-from-H&E negative (all numbers exist).
- [ ] 1.9 **Ch1 main introduction** — motivation, hypothesis, contributions, outline.
- [ ] 1.10 **Ch1 per-cohort dataset descriptions** with final verified numbers.
- [ ] 1.11 **Thesis skeleton** (LaTeX, Cambridge format) with all drafted sections placed.
- [~] 1.12 **SWG [TO FILL] slots** *(filled 2026-08-20 from lgd2_final_pre_event_model_comparison.md; remaining: paired fusion-vs-histology bootstrap CI from saved OOF preds)* — pull histology-only baseline + fusion-vs-hist delta
      from cluster tables into chapters/ch2/swg_arm.md (compute from saved OOF if absent).

### Requires Rehan (R)
- [x] R.1 `huggingface-cli login` *(done 2026-08-19; token relocated to modern path; Virchow2+GigaPath downloaded)* on cluster + accept Virchow2/GigaPath gated terms
      → unblocks encoder sweep extraction.
- [x] R.2 APPROVED 2026-08-19 (Rehan): acquire TCGA-STAD/GEJ pool as pre-registered
      extension (primary claim stays OAC-only).
- [x] R.3 RESOLVED 2026-08-19 (Rehan): no expert-graded subset exists. Adopted
      instead: consensus soft labels (graders agree -> confident label; disagree ->
      intermediate/uncertain class, flagged to the model), plus Rehan adjudicating
      the exported disagreement samples via document + transcribed yes/no.

## Phase 2 — blocked on Phase 0/1

- [ ] 2.1 ERIN slide↔label join for imaged subset (needs 0.1). 
- [ ] 2.2 **ERIN Ch3 arm**: histology vs histology+report-clinical under protocol
      (needs 0.1 + 1.6).
- [ ] 2.3 **Ch4 core experiment**: pathladder-label vs gold-label training on ERIN
      (needs 0.1 + 1.3 + R.3), replicated on TCGA (features ready).
- [ ] 2.4 Report–slide disagreement analysis (needs 2.3).
- [ ] 2.5 Encoder sweep execution (needs R.1 + 1.7; Trident for extraction).
- [ ] 2.6 SWG clinical arm rerun under final protocol (needs SWG repo Phase-8 unblock
      or fresh feature index — investigate as part of 1.12).
- [ ] 2.7 LLM-vs-pathladder comparison — EXTENDED by joint decision 2026-08-20:
      local-LLM grading of ERIN report text on-cluster (ollama, site-scoped ladder
      prompt), as (a) third grader for agreement analysis, (b) Ch4 rules-vs-LLM
      numbers, (c) candidate disagreement-resolver. Smoke on the 80 adjudicated
      cases first (adjudicated truth available), then full corpus + TCGA replication.
      *JURY SMOKE COMPLETE 2026-08-20: 9/10 scored (llama3.3:70b pending). Five models
      at 100% vs adjudicated truth (qwen3 14b/32b, gemma3 12b/27b, phi4); deepseek +
      mistral 98.7%; llama3.1:8b 84.4% (retained — gate is parse-only); granite3.3:8b
      EXCLUDED by pre-registered parse gate (93.7% < 95%). Unanimity 72% on hard cases;
      disagreement concentrates in the 8B tier. qwen3:14b full corpus 8/8 shards done;
      CORPUS COMPLETE 2026-08-20 evening: 8 jurors x 7,149 reports. Fleiss kappa 0.900;
      unanimity 85.5%; jury >=6/8 majority on 6,899/7,101 (97.2%) — only ~200 reports
      remain genuinely uncertain (vs 2,860 under 2-grader consensus). Results in
      results/jury_corpus_analysis.json + jury_votes.csv. OPEN JOINT DECISION:
      adopt jury-vote + entropy as Ch3/Ch4 label source. TCGA-side prompt still to design.*

### Added by 2026-08-20 joint amendment (Rehan-directed, Barretts database)
- [x] 2.13 Barretts-database free-text acquisition (READ-ONLY): all 13,645 pathology
      reports exported to secured cluster dir; SWG matching via specimen numbers ->
      643/771 Path IDs (83%), 74/88 patients, 327 report rows *(2026-08-20)*
- [~] 2.14 LLM jury on matched SWG reports (rerun on clean parquet after CR-corruption fix) -> label audit + Ch4 third cohort
- [ ] 2.16 Final ERIN jury labels (majority >=6/8 = train-eligible; below bar = "unsure",
      excluded from training, retained in a held-aside file) + progression cohort v3
- [~] 2.15 OCCAMS-side pull (approved, running): same DB exposes view_masterpath_patient (2,754 OC/AH
      patients) — candidate source for OCCAMS report text / n=87-vs-141 investigation

### Added by 2026-08-19 joint amendment
- [x] 2.8 TCGA-STAD/GEJ acquisition *(COMPLETE 2026-08-20: 381/381 slides, 381/381 features, overnight)*
- [ ] 2.9 STAD labels table (CDR + TP53 + ABSOLUTE), mirroring tcga_oac_labels.
- [x] 2.10 ERIN consensus soft labels *(FINAL 2026-08-20: 3,350 confident / 2,860 uncertain / 706 single-grader / 79 adjudicated; false confident-CANCERs correctly demoted to uncertain)*
- [x] 2.11 Adjudication pack (80 cases) delivered to Rehan + parse_adjudication.py ready *(2026-08-19)*
- [x] 2.12 progression cohort FINAL *(2026-08-20: 1,218 patients, 197 progressors — the old grader had inflated progression events ~30% via false CANCER calls)*

## Phase 3 — writing blocked on results

- [ ] 3.1 Ch2 OCCAMS + TCGA sections (needs 1.1, 1.2, 1.4; decision-tree outcome stated).
- [ ] 3.2 Ch3 chapter prose (needs 2.2).
- [ ] 3.3 Ch4 chapter prose incl. validation + core experiment (needs 2.3, 2.4).
- [ ] 3.4 Encoder-sensitivity sections per chapter (needs 2.5).
- [ ] 3.5 pathladder release with DOI + short methods paper draft (needs 1.3, 2.3).

## Phase 4 — end-game

- [ ] 4.1 Ch5 discussion (two seeds writable early: two-cohort negative; TCGA-vs-OCCAMS
      signal contrast as data-quality case study — may draft under 3.x if time allows).
- [ ] 4.2 Ch1 final pass so promises match what chapters deliver.
- [ ] 4.3 Abstract, conclusions, full assembly, reference sweep.
- [ ] 4.4 Publications map final (SWG paper, pathladder paper, thesis).

## PARKED

- 2026-08-25 (blank-slate round): 80 further ideas from the same 10 models
  given ONLY the data+compute inventory (no thesis framing) — synthesis in
  docs/blankslate_ideas.md, raw in review/blankslate_*.json. Headline: 9/10
  unprimed models converge on longitudinal trajectory modelling (which we do
  not do); only 2/10 pose the fusion question at all — independent
  corroboration of the reframe. Top unplanned candidates: trajectory
  modelling, predicted-WGD-in-Barrett's as progression marker, Barrett's-DB
  natural-history extraction, cross-FM disagreement biomarker. ALL PARKED.
- 2026-08-25: 80 proposals from a 10-model consultation logged in
  docs/proposals_multimodel.md (raw: review/proposals_*.json). All are PARKED
  candidates pending joint promotion; top clusters: visibility learning curve
  (7/10 models), power map, winner's-curse bootstrap, leave-one-family-out
  jury, R.4 sample-pack prep, TCGA-pool attention-shift replication.
 (not in plan; promote only jointly)

- TCGA pan-cancer pathladder extension beyond ESCA/STAD
- HANCOCK out-of-organ methods check
- Genomics England application
- Multitask MoE thread (multitask_moe_20260721)

## Leave-week campaign (launched 2026-08-21, Rehan away until ~2026-09-01)

All results land in feasibility/runs/<task>/output/results.json unless noted.
1. Specimen jury completion: h200 shards + cuda insurance (12+12 jobs) ->
   barretts_db_export/jury_specimen/ + swg_label_audit_specimen.csv
2. STAD labels (2.9) -> data/tcga_stad_labels.csv, then POOLED OAC+GEJ fusion
   (the R.2 powered Ch2 test, n~446) + necessity probes (2.17) on the pool
3. ERIN join (2.1) -> labeller/erin_master.csv, then Ch3 arm (2.2) and Ch4
   label-source experiment (2.3), each duplicated cuda+h200
4. Encoder sweep extraction (2.5): Virchow2 (cuda) + GigaPath (h200) over
   ERIN 2,281 + ESCA 65 + STAD 381 -> features_virchow2/ features_gigapath/
On return: read results against pre-registrations; deviations to log: none yet.

## Amendment log

- 2026-08-21 (FINDING, flagged for joint discussion on return): necessity probes
  at n=446 (pooled OAC+GEJ) show TP53 AUC 0.678 and WGD 0.703 from H&E (shuffled
  ~0.50) — genomics IS partially visible at adequate n. The earlier two-cohort
  negatives (n=65-140, AUC 0.36-0.48) stand as honest small-n results, but Ch2
  Part A's claim must be revised from "not recoverable" to "partially recoverable
  at scale; the fusion question becomes complementarity beyond what is visible."
  Stage from H&E: 0.644. Age: 0.569.
- 2026-09-02 evening (joint, Rehan; Shiv left the lab — credit, don't ask):
  2.37 per-section jury over the FULL 7,149-report corpus (top-5 jurors,
  multi-grade + subtype per section; labeller/llm_grade_sections.py) — via
  Shiv's slide<->section table this regenerates ERIN supervision at SLIDE
  level. 2.38 the payoff: retrain grade classifier slide-level vs case-max on
  identical folds — quantifies the label noise of the standard case-level
  shortcut (planned once 2.37 lands). Human per-section comparison joins the
  app labels to the same structure.
- 2026-09-02 later (joint, Rehan): label-space CORRECTION — reports contain
  lettered specimen sections with potentially different/multiple grades each,
  and cancer subtype matters (adenocarcinoma / squamous / signet ring /
  post-neoadjuvant treatment effect). Grading app rebuilt as v2: per-section
  multi-grade + subtype tags (scripts/grading_app.py; DB reset pre-launch, no
  labels lost). KEY FIND (Rehan pointer): Shiv Sakthivel's
  fmlab/sakthi01/erin/data/matched_image_pathology.csv (12,468 rows) maps each
  SLIDE to its report Section + tissue type — joining per-section human/LLM
  labels through it upgrades ERIN supervision from case-max to SLIDE-LEVEL.
  Rehan's earlier case-level local tool is superseded; he grades in the app.
  Follow-on (planned, not yet run): per-section LLM extraction prompt so the
  jury emits section-wise grades for the human comparison; slide-level label
  regeneration through Shiv's table.
- 2026-09-02 (joint, Rehan): the ERIN LLM-labelling work is to become an
  ARXIV PAPER. Missing piece = human hand labels; Rehan will grade 100 blinded
  reports himself via a local self-contained HTML tool (delivered; report text
  kept off external services per governance — no artifact publish). Sample:
  60 random train-eligible + 20 unsure-holdout + 20 pathladder-vs-jury
  disagreements, all distinct patients, shuffled, stratum key held back at
  labeller/handlabel_sample_key.csv (cluster only). On return of the CSV:
  human-vs-jury / human-vs-pathladder agreement overall and per stratum, and
  whether the unsure quarantine is where humans also struggle. Honesty note
  for the paper: Rehan is a computational researcher, not a pathologist —
  labels are a domain-expert human anchor; the pathologist sample (R.4)
  remains the gold anchor if ever available.
- 2026-09-02 (Rehan-directed side quests): SQ.1 EoE finder — keyword screen
  found 796/7,149 reports (640 patients) mentioning eosinophils, 116 with
  explicit EoE phrases; 3-juror LLM adjudication over all 791 keyword-positives
  + 100 random keyword-negative controls running (labeller/llm_eoe_shard.py).
  SQ.2 ERIN MDT — published-pattern panel deliberation (MDTeamGPT/MDAT shape:
  independent reads -> rebuttal round -> chair synthesis; 3 consultants +
  qwen3:32b chair) over the 80 adjudicated (binary truth) + 201 unsure
  reports; measures deliberation-vs-voting accuracy AND conformity flips
  (labeller/llm_mdt.py). Both are Ch4-extension candidates.
- 2026-08-26 PM (joint, Rehan): final compute closure before writing —
  2.25b WGD teacher scored on SWG biopsies with MEASURED CNV complexity as
  ground truth (diagnoses whether the ERIN transfer inversion is ranking or
  calibration failure); 2.32 cross-cohort transfer matrix (SWG<->ERIN
  progression, OCCAMS<->TCGA survival landmark, ERIN->SWG grade); 2.33
  pan-cancer jury validation on TCGA-Reports vs cBioPortal structured grades
  (ESCA/STAD + KIRC + BLCA; the top-5 pre-registered jurors) — the
  human-independent Ch4 external check.
  2.32 DONE 2026-08-26 (results/transfer_matrix.json): asymmetric — the one
  real generalisation is SWG->ERIN progression (0.744 within -> 0.640 across,
  research cohort to routine NHS cohort, the direction that matters); all
  other cells collapse (ERIN->SWG prog 0.54, grade 0.56, TCGA->OCCAMS 0.49) or
  carry no signal to transfer (OCCAMS->TCGA 0.60->0.60).
  CLOSURE OUTCOMES 2026-08-27: 1.4 DONE (results/porpoise_baselines.json) —
  published PORPOISE fusion FAILS to beat its own unimodal arm on our pool
  (MMF 0.545 vs AMIL 0.566, delta -0.021 [-0.081, +0.035]); the architecture
  escape hatch is closed. 2.25b DONE (results/wgd_swg.json) — the transfer
  inversion is a RANKING failure, replicated: predicted-WGD vs measured cx
  rho=-0.10 (p=0.005, n=707), progression AUC 0.397; virtual genomic
  biomarkers do not survive resection->biopsy shift, two cohorts. 2.33 DONE
  (results/pancancer_jury.json) — jury vs HUMAN-RECORDED structured grades:
  ESCA 98.0%, STAD 96.4%, KIRC 95.2% exact; BLCA 98.6% two-tier (two-tier is
  its clinical system); ~1,280 reports, four cancer types, fully outside the
  self-validation loop — the strongest available answer to the sev-5
  criticism short of R.4 itself.
  WAVE-3 VERDICT 2026-08-27 (docs/gap_review_wave3.md): gate NOT passed —
  finite closure list: 1.21 reconciliation, encoder sweep on OCCAMS/TCGA
  (extraction + downstream = 2.34), 1.20 remaining perm controls + final-
  pipeline controls (= 2.35), Holm computation (1.18 execution), patient-level
  ERIN grade aggregation (= 2.36, Terra sev-5). All submitted same day;
  writing gate re-evaluates when they land.
  CLOSURE PROGRESS 2026-08-27 (results/closure_cpu.json): 1.18 Holm DONE —
  only the SWG fusion win survives correction (p_holm=0.0096); OCCAMS, ERIN-
  prog fusion, Ch4 label-source all null after Holm; the corrected table
  matches the thesis narrative exactly. 2.36 DONE — patient-level ERIN grade
  0.960 vs slide-level 0.921; protocol-correct metric is STRONGER (Terra
  sev-5 resolved favourably). 1.21 DONE — v2 (1,218/197) vs v3 (1,266/181):
  75 gained (jury labels reports consensus could not), 27 lost (unsure
  exclusions), 103 event flips, 61 pos->neg consistent with the documented
  consensus-era CANCER over-call. Remaining gate compute: perm controls
  (queued) + OCCAMS extraction (~2,540 h5s) -> downstream encoder sweep.
  GATE: once these + PORPOISE land,
  a wave-3 multi-LLM GAP REVIEW of the complete results corpus decides
  whether compute is done; writing starts only after that gate.
- 2026-08-26 (joint, Rehan: full VLM pretraining + PORPOISE build + the four
  cheap analyses approved; R.4 pack deferred, no pathologist on hand):
  2.28b VLM full build = CLIP-style ERIN training with zero-shot TCGA transfer
  (446 pairs; the 9,517-pan-cancer version is infeasible without terabyte-
  scale slide downloads — recorded honestly); 1.4 step 1 = cBioPortal omics
  build + feature conversion + frozen splits (task_porpoise_data.py), step 2 =
  training run after data lands; 2.29 winner's-curse bootstrap + residual
  complementarity on release OOF (task_swg_oof_analyses.py); 2.30 leave-one-
  family-out jury (task_lofo_jury.py); 2.31 attention-shift OCCAMS replication
  (COHORT=occams branch added to task_attention_shift.py).
  2.31 DONE 2026-08-26 (results/attn_shift_occams.json): attention shift does
  NOT replicate on OCCAMS — A-vs-B Spearman 0.984 = A-vs-C 0.984 (noise
  floor), C-index B<=A. COHERENT with the visibility story: conditioning
  shifts attention only where genomics carries signal (TCGA pool) and not
  where it is invisible (OCCAMS OAC). Report the pair as one finding.
  2.28b DONE (results/vlm_pretrain.json): ERIN zero-shot grading 0.889 —
  within 4 points of supervised (0.926) with NO labels; retrieval 12x chance.
  TCGA transfer: verbatim slide-report retrieval FAILS (report style shift)
  but prompt-based zero-shot site classification transfers at 0.782. The
  semantics transfer; the literal pairing does not. Ch4-adjacent method
  contribution.
  1.4 STEP 1 DONE (results/porpoise_data.json): 439 slides / 414 cases /
  8,827 omics columns over 3,047 signature genes + pt features + frozen
  splits. Step 2 (patched training run) is the remaining piece of 1.4.
  2.29 DONE 2026-08-26 (results/swg_oof_analyses.json): winner's-curse DEFUSED
  with a number — late-mean wins 72.8% of 500 bootstrap replays, winner
  optimism only +0.027 AUPRC; the family selection is stable. Complementarity:
  hist adds to CNV decisively (LRT p=2.6e-5, dAUC +0.095 [0.009, 0.187]); CNV
  adds information beyond hist by LRT (p=0.007) but dAUC crosses zero at n=150
  — a real-but-underpowered effect, exactly as the power map predicts.
  2.30 DONE (results/lofo_jury.json): no single LLM family is load-bearing —
  max label flip 0.5% (gemma3), eligible-set Jaccard >=0.98 across all six
  drops. Caveat kept: rules out single-family dependence, not all-LLM shared
  bias (that remains R.4).
- 2026-08-25 night (joint, Rehan: "apart from the chapter 4 rebuild I think we
  could implement all of this"): PROMOTED from the blank-slate parked list —
  2.24 longitudinal trajectory modelling; 2.25 predicted-WGD teacher transfer
  (2.25b SWG side deferred pending paths); 2.26 Barrett's-DB natural history +
  jury-at-scale validation vs structured grades; 2.27 cross-FM disagreement
  biomarker. Implementation designs frozen in
  docs/blankslate_implementation_plan.md BEFORE execution. VLM/contrastive
  Ch4 rebuild stays PARKED per Rehan. Destination: appendix/papers unless
  results earn chapter status.
  OUTCOMES same night: 2.24 NO SIGNAL (results/erin_trajectory.json — naive
  trajectory features significantly WORSE than snapshot, -0.070 [-0.123,
  -0.018]; GRU merely matches; root cause: only 32/153 progression patients
  have >=2 imaged timepoints — an acquisition gap, not a modelling verdict;
  appendix negative + data-collection recommendation). 2.27 NULL
  (results/fm_disagreement.json — disagreement ~uncorrelated with jury entropy
  (rho 0.04), flags unsure at 0.52 AUC, progression 0.52; appendix negative).
  Both were cheap signal tests; correctly killed.
  2.28 promoted 2026-08-26 (joint, Rehan: "Maybe you should still implement
  the VLM rebuild then"): report-slide vision-language alignment, un-parked.
  Signal test first per the standing rule: lightweight projection from pooled
  slide embeddings into a text-embedding space trained contrastively on ERIN
  slide-report pairs; readouts = slide->report retrieval vs chance and
  zero-shot grading vs the supervised probe. Full contrastive pretraining on
  the 9,517 TCGA pairs only if the signal test passes.
  2.24b promoted same night (joint, Rehan: "The Barrett's (image+cnv) dataset
  is a good candidate for the trajectory idea"): SWG joint morphology+CNV
  trajectories on the strict pre-event cohort with FROZEN release folds —
  snapshot vs trajectory vs GRU, plus Kimi's future-CNV-from-current-H&E
  secondary. scripts/task_swg_trajectory.py.
  2.24b OUTCOME 2026-08-26 (results/swg_trajectory.json, 124/150 multi-sample,
  frozen folds): snapshot sufficiency CONFIRMED on suitable data — latest
  biopsy 0.786, trajectory features -0.058 (trend worse), GRU matches
  snapshot, CNV adds nothing at snapshot (+0.002). Twice-replicated negative.
  POSITIVE secondary: current H&E predicts NEXT biopsy CNV complexity,
  Spearman 0.161, p=1.3e-4, n=557 — morphology weakly anticipates genomic
  evolution (appendix/paper seed).
  2.26 STATUS: natural history + text-only baseline (0.696, n=8,830) DONE;
  jury-vs-structured validation BLOCKED by the database export (structured
  grade columns empty; dysplasiagradehistory 0x0; grading_sequence codes
  unmapped) -> NEW R.5: ask Leanne for the code map or a re-export.
  2.25 OUTCOME (results/wgd_transfer.json): teachers PASSED in-domain gates
  (WGD CV 0.730, TP53 0.764, n=544-562 resections) but transfer to ERIN
  surveillance biopsies INVERTED — predicted-WGD scores progression at AUC
  0.315 (progressors score LOWER). Verdict: specimen-type domain shift defeats
  in-domain-validated genotype predictors; 'virtual biomarker' claims do not
  survive resection->biopsy transfer. Strong cautionary negative for Ch2/Ch5;
  2.25b (SWG side with measured CNV as ground truth) still worthwhile to test
  whether the inversion is a calibration or a ranking failure.
- 2026-08-25 late (joint, Rehan): PROMOTED from the consultation's parked list:
  2.22 genotype-visibility learning curve, n x population disentangled
  (TCGA-OAC / OCCAMS-OAC / OAC-combined / STAD-GEJ / mixed strata, matched-n
  subsampling, permutation nulls) — scripts/task_visibility_curve.py;
  2.22 DONE 2026-08-26 (results/visibility_curve.json): DECISIVE — visibility
  is a POPULATION property, not a sample-size effect. OAC at chance at every n
  (TCGA-OAC 0.36-0.45; OCCAMS flat ~0.50 to n=141; combined DECLINES to 0.42
  at n=206) while STAD/GEJ rises with n (TP53 0.54->0.64, WGD 0.62->0.74,
  clean nulls). Matched-n cell: at n=65, STAD 0.57/0.65 vs OAC 0.36/0.45. The
  2026-08-21 amendment's "partially recoverable at adequate n" claim is
  FALSIFIED and replaced: recoverable in gastric/GEJ, not in OAC. Ch2 Part A
  reverts to a clean two-cohort OAC negative plus a population contrast.
  2.23 power map, minimum detectable fusion delta per cohort (semi-synthetic
  injection, paired-bootstrap detection probability, MDD at 80% power) —
  scripts/task_power_map.py. Both submitted to epyc same day.
  2.23 DONE 2026-08-25 (v2 after survival-arm fix; results/power_map.json):
  MDD80 at rho 0.8 — SWG 0.075, OCCAMS 0.10, TCGA-OAC 0.10, TCGA-pool 0.05,
  ERIN-grade 0.02, ERIN-prog 0.075. Since measured fusion deltas where power
  exists are +0.01..0.04, every external null (OCCAMS, TCGA-OAC) sat in a
  cohort structurally unable to detect a plausible effect — the Ch5
  quantitative core: 'failure to replicate' is largely 'failure to power'.
- 2026-08-25 evening (wave-2 review, 5 blind frontier families — see
  docs/review_findings.md addendum): reframe survives blind review but must be
  presented as hypothesis-generating (HARKing defence = amendment trail). New
  items: 1.20 50-perm nulls for every off-0.5 shuffled control (OCCAMS v2,
  TCGA first-pass, probes); 1.21 progression cohort v2-vs-v3 reconciliation;
  1.22 unsure-holdout sensitivity analysis; 1.23 clinical-arm leakage ablation
  (drop prior-grade). ERIN pre-reg deviation note added; multiplicity plan
  relabelled post-hoc; encoder-sweep grid extension recorded as deviation.
- 2026-08-25 (JOINT REFRAME, Rehan's conditional approval executed on convergence
  evidence): central claim REVISED. Old: "adding a second modality improves
  prediction and the benefit replicates." New working framing: "WHERE AND WHY
  multimodal fusion fails to replicate in oesophageal cancer, and how to validate
  report-derived supervision." Basis: docs/review_findings.md — five independent
  reviewers across four model families converged that no cohort shows fusion
  beating the best unimodal arm, while the negatives, the label-quality
  infrastructure, and the visibility/attention analyses are the defensible
  contributions. Chapters keep their experiments; their QUESTIONS are recast:
  Ch2 = when does genomics help histology and when not (SWG vs OCCAMS/TCGA);
  Ch3 = progression as primary estimand (grade-classification moves to Ch4);
  Ch4 = validating report-derived supervision (now the methodological core);
  Ch5 = why fusion fails to replicate: labels, power, population, comparators.
  New fix items from the review: R.4 pathologist ground-truth sample (~250
  reports) — REQUIRED; 1.13 SWG fusion-vs-histology CI (TOP PRIORITY —
  RESOLVED 2026-08-25: found already computed in the strict release table
  lgd2_final_pre_event_paired_differences.csv; all three CIs exclude zero;
  transcribed into swg_arm.md + review_findings.md; 1.13b DONE 2026-08-25:
  latemean vs gigapath ΔAUPRC/ΔAUC cross zero, ΔBrier excludes; claim is
  encoder-conditional — results/latemean_vs_gigapath_paired.json); 1.14
  OCCAMS shuffled controls + attrition flow (DONE 2026-08-25,
  results/occams_v3_shuffle.json: attrition explained — 276 h5 bags, 145 with
  survival, 141 with genomics, 87 with all three; single-perm controls show no
  systematic inflation but proper 50-perm nulls folded into 1.20); 1.15 Ch4 cross-evaluation matrix (DONE 2026-08-25,
  results/ch4_labelsource_xeval.json: jury-trained and pathladder-trained models
  interchangeable — 0.921 both on jury eval, 0.877/0.882 on pathladder eval;
  feas-grader-trained worse everywhere, 0.848; and NO model predicts feas-grader
  labels well, not even its own, 0.668 — label noise is asymmetric and localised
  in the old grader, answering the circularity critique from the models' side);
  1.16 Ch1/Part A rewrite around learning-curve + population story; 1.17 TCGA
  probe control-failure debug; 1.18 multiplicity plan (Holm over one confirmatory
  contrast per chapter); 1.19 pathladder negation-fix revalidation on fresh
  sample; encoder-sweep pre-reg amended: a sign flip downgrades the claim.
- 2026-08-25 (joint, Rehan proposal): added 2.21 thesis red-team review — local
  model jury (4 models) + one fresh-context Claude agent critique the plan, drafts,
  pre-registrations and results digest; criticisms must cite specific claims;
  cross-model convergence ranks severity. Complements, never replaces, human review.
- 2026-08-23 (joint, Rehan proposal): added 2.20 attention-shift study — does
  conditioning histologic attention on genomics change where the model looks?
  Conditional-ABMIL vs plain vs permuted-genomics control on the TCGA pool;
  note recorded that late fusion cannot shift attention by construction.
  Also: attribution work package (pathladder explain mode DONE, ABMIL attention
  export DONE, coefficient export pending) under existing items.
- 2026-08-21 (joint, Rehan proposals, pre-leave): added 2.18 jury expansion —
  (a) big-model axis (llama3.3:70b retry, gpt-oss:120b) + domain-tuned axis
  (medgemma if pullable), self-gating smoke->corpus jobs; (b) disagreement-driver
  analysis on existing votes (report length/negation/addenda/specimens);
  (c) placement decision: jury work stays INSIDE Ch4; standalone methods paper
  post-thesis. Added 2.19 pan-cancer jury validation on TCGA-Reports (3-4 cancer
  types vs structured grade truth; zero new data). Encoder grid extended per its
  own pre-reg clause: +H-Optimus-0, +Phikon-v2; grid now closed at 5.
- 2026-08-21 (joint, Rehan): grid extended once more to SIX with H-Optimus-1 (the
  current SOTA generation, Mar 2025) — rationale: keep older models as benchmarks,
  always include latest. Access awaiting Bioptimus manual review; self-healing
  retry + chained extraction installed. Grid FINAL at 6.
  PARKED: external-domain datasets (radiology notes etc.), HANCOCK (reaffirmed).
- 2026-08-21 (joint, Rehan proposal): added 2.17 necessity-triangle probes —
  for each chapter's modality X, report (i) hist-only, (ii) hist+X fusion,
  (iii) X-predicted-from-histology, as one repeated figure. First instance
  launched on the TCGA pool (tp53/wgd/stage/age from H&E).
- 2026-08-19: plan frozen (Rehan + Claude).
- 2026-08-19 (late): 1.1, 1.2, R.1 done with evidence; 1.3 mostly done. No scope changes.
- 2026-08-20 (Rehan decisions): (a) ADOPTED jury-vote + entropy as Ch3/Ch4 label
  source, with the conservative rule that any report below the confidence bar
  (jury majority < 6/8) or otherwise ambiguous is labelled "unsure", HELD OUT of
  all training, and reported as such — deliberate caution, shown not hidden.
  -> new item 2.16 (final ERIN jury labels + progression cohort v3).
  (b) OCCAMS-side text pull from the Barretts DB approved (2.15 -> active).
- 2026-08-20 (late, Rehan-directed): Barretts database (Fitzgerald group) accessed
  read-only with Rehan's viewer token -> items 2.13-2.15. Token expires 2026-08-21
  ~18:00 UTC; all report text stored in chmod-700 cluster dir, never in git.
- 2026-08-20: 2.7 extended to on-cluster local-LLM grading of ERIN (Rehan proposal).
- 2026-08-20 (joint, Rehan proposal): 2.7 further extended to an LLM JURY — ~10
  diverse local models grade the corpus with an identical prompt; jury majority ->
  candidate labels, jury entropy -> per-report uncertainty, inter-model agreement
  (Fleiss kappa, pairwise) studied as Ch4 content. Membership gated on parse
  viability (>=95% on adjudicated-80 smoke) ONLY — never on agreement, to avoid
  homogenising the jury. Human anchor remains the adjudicated 80 + Rehan spot-check.
- 2026-08-20: adjudication performed by Claude per Rehan's delegation, with Rehan
  spot-check to follow (10 flagged cases); independence caveat recorded for write-up.
- 2026-08-19 (joint amendments, Rehan decisions): (a) R.2 approved -> new items 2.8
  STAD acquisition + 2.9 STAD labels table; (b) ERIN label source changed to
  pathladder+feasibility CONSENSUS soft labels with Rehan adjudication of
  disagreements -> new items 2.10 consensus labels, 2.11 adjudication pack/ingest;
  (c) ERIN progression labels to be REBUILT from consensus grades before any Ch3
  model trains (amends erin_ch3_preregistration.md; reason: audit v2 showed the
  feasibility grader over-calls CANCER 4,029 vs 1,314).

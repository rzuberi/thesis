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
- [ ] 1.4 **PORPOISE baseline** on OCCAMS + TCGA-OAC (clone, env, adapt loaders).
      Done = results/porpoise_baselines.json.
- [ ] 1.5 **CNV window→gene map** for SWG Fig 1.5 (commands referenced in
      barretts_training docs). Done = annotated importance table.

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
      7 further jurors x 8 shards (56 jobs) launched. TCGA-side prompt still to design.*

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

## PARKED (not in plan; promote only jointly)

- TCGA pan-cancer pathladder extension beyond ESCA/STAD
- HANCOCK out-of-organ methods check
- Genomics England application
- Multitask MoE thread (multitask_moe_20260721)

## Amendment log

- 2026-08-19: plan frozen (Rehan + Claude).
- 2026-08-19 (late): 1.1, 1.2, R.1 done with evidence; 1.3 mostly done. No scope changes.
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

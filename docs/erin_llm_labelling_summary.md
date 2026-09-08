# ERIN automatic classification (LLM labelling) — full record

Everything done to derive labels for the ERIN pathology-report corpus with local
LLMs: the decisions, the models, the validation, and where each piece lives.
Written 2026-09-08. This is the source document for the P1 arXiv paper
("LLM jury labelling of GI pathology reports").

**Privacy rule that shaped everything:** report text and patient data never
leave the cluster. This repo is public, so it holds code + aggregate JSONs
only; every CSV containing report text or per-case labels lives at
`/mnt/scratche/slow/fmlab/zuberi01/phd/thesis/` (cluster) and is gitignored.
Paths below with `T/` mean that cluster root.

---

## 1. The corpus

- **Source:** `/mnt/scratche/fast/fmlab/datasets/imaging/ERIN/data/PathologyReport_AnonIds.csv`
  — 7,149 reports, pre-redacted by the data provider. The text fields we use
  are `FinalDiagnosis_redacted` and `MicroscopicDescription_redacted`; the case
  key is `CaseName`.
- **Slide features:** `/mnt/scratche/fast/fmlab/datasets/imaging/ERIN/features/20x_224px/features_uni_v2/*.h5`
  (UNI-v2, 1536-d; h5 attrs `slide_path`/`level`/`mpp`, keys `coords`/`features`).
- **Master join table:** `T/labeller/erin_master.csv`
  (columns `h5, uuid, anon_id, CaseName, CollectedOrOrdered, final_label, label_status, jury_frac`)
  — the one table linking slides ↔ reports ↔ patients ↔ labels.

## 2. Label-scheme evolution (three generations)

### v1 — pathladder (keyword ladder, no LLM)
Deterministic weak labeller: sentence splitting, windowed negation,
worst-finding-wins on the ordinal ladder NDBE < IND < LGD < HGD < CANCER.
- Code: `labeller/pathladder/` (pip-installable, schema-driven; schemas
  `barretts_ladder` and `tcga_gi`), tests in `labeller/tests/`.
- Validated on TCGA ESCA+STAD reports (n=507): histologic_type 98% coverage /
  100% accuracy vs GDC coding; grade 77% coverage / 96.5% accuracy vs
  cBioPortal (`labeller/README.md`, `labeller/tcga_validation_results.json`).
- Full-corpus run on ERIN: `results/erin_pathladder_fullcorpus.json`
  (NDBE 4,194 / CANCER 1,304 / None 797 / HGD 363 / LGD 290 / IND 201).
- Kept as the *baseline comparator*, not the label source — the wave-3 Holm
  test `ch4_pathladder_vs_jury_trained_auc` (p_holm=0.945,
  `results/closure_cpu.json`) shows models trained on pathladder vs jury
  labels are statistically indistinguishable downstream, which is itself a
  finding (cheap keyword labels ≈ jury labels for this coarse task).

### v2 — two-grader consensus (first LLM pass)
Two ollama models graded every report; agreement = label, disagreement =
uncertain. Produced `feasibility/runs/consensus2/output/erin_progression_cohort_v2.csv`
(1,218 patients, 197 progressors). Superseded because "uncertain" swallowed
2,860 reports (`results/erin_consensus_final.json`). Kept for the v2↔v3
reconciliation (below).

### v3 — the 8-model jury (current canonical whole-report labels)
**Decision:** replace pairwise consensus with a jury of eight local models,
majority vote, explicit unsure class. All inference is local ollama on cluster
GPUs — nothing leaves the network.

- **Jurors (8):** `qwen3:14b`, `qwen3:32b`, `gemma3:12b`, `gemma3:27b`,
  `phi4:14b`, `mistral-small3.2`, `deepseek-r1:14b`, `llama3.1:8b`.
  Models stored at `OLLAMA_MODELS=/mnt/scratche/slow/fmlab/zuberi01/ollama-models`.
- **Prompting:** one report per request, `/api/generate` with `format:json`,
  `think:false` + `/no_think` for qwen; strict JSON schema with the 5-grade
  ladder; resume-by-CaseName; sharded via `SHARD`/`N_SHARDS`; unique ollama
  port per job (`20000 + SLURM_JOB_ID % 20000`). Worker:
  `labeller/llm_grade_shard.py`.
- **Vote rule:** label accepted when a clear majority agrees →
  `label_status=train_eligible`; near-splits → `unsure_held_out` (204 reports,
  `T/labeller/erin_labels_unsure_heldout.csv`); the hardest disagreements
  (78–80 cases) manually **adjudicated by Claude** with full report text on
  cluster → `adjudicated` (`T/labeller/adjudications.csv`,
  `labeller/make_adjudication_pack.py` / `parse_adjudication.py`).
- **Aggregation code:** `labeller/build_erin_jury_labels.py`; final table
  `T/labeller/erin_labels_jury_final.csv`.
- **Outcome** (`results/erin_jury_labels_summary.json`): 7,149 reports →
  6,867 train-eligible (NDBE 5,151 / CANCER 863 / HGD 405 / LGD 269 / IND 257),
  204 unsure held out, 78 adjudicated. Per-juror parse rates ≈100% except
  llama3.1:8b at 98.3% (`results/jury_corpus_analysis.json`).
- **Progression cohort v3** built from these labels:
  `T/labeller/erin_progression_cohort_v3.csv` — 1,266 patients, 181
  progressors (definition: any later report of the same patient reaching
  LGD+ after an NDBE index).

**Jury robustness checks:**
- *Leave-one-family-out* (`scripts/task_lofo_jury.py`,
  `results/lofo_jury.json`): dropping any juror family flips ≤0.5% of labels
  (eligible-set Jaccard ≥0.979); gemma3 is the most load-bearing family. The
  jury is not hostage to any single model.
- *Unsure characterization* (`labeller/characterize_unsure.py`,
  `results/unsure_characterization.json`): unsure reports have 3.3× the
  hedging-language rate (0.52 vs 0.16) and higher addendum rates — the jury's
  uncertainty tracks genuine textual ambiguity, not model noise.
- *Negation revalidation* (`labeller/revalidate_negation.py`,
  `results/negation_revalidation.json`).
- *v2↔v3 reconciliation* (`results/closure_cpu.json`): 103 patient label
  flips between generations, documented rather than hidden.

## 3. External validation — pan-cancer TCGA jury

**Decision:** validate the same jury pipeline against *human registry grades*
where they exist, in cancer types we never tuned on.
- Worker `labeller/llm_grade_tcga.py` (G1–G4/HIGH/LOW/GX schema), 5 jurors
  (gemma3 12b/27b, phi4, qwen3 14b/32b), reports from cBioPortal
  (`data/pancancer/{st}_pan_can_atlas_2018_reports.csv`; provisional studies
  `esca_tcga`, `stad_tcga`, `kirc_tcga`, `blca_tcga` because pan_can_atlas
  clinical lacks GRADE).
- Analysis `scripts/task_pancancer_jury_analysis.py` →
  `results/pancancer_jury.json`: two-tier agreement with registry grade
  **0.98 (ESCA), 0.97 (STAD), 0.97 (KIRC), 0.99 (BLCA)**; on
  jury-confident cases 0.97–0.99. (BLCA exact agreement is 0.58 only because
  registry uses high/low while the jury outputs G1–G4 — two-tier is the fair
  metric.) This is the paper's headline external validity result.

## 4. MDT deliberation (does debate beat voting?)

**Decision (Rehan):** run an LLM multidisciplinary-team meeting on the hard
cases, following published MDT-LLM frameworks (MDTeamGPT arXiv:2503.13856,
MDAT gyn-onc medRxiv, GI-oncology multi-agent MDT arXiv:2512.08674,
consensus-matrix OpenReview — filed in `docs/reading_notes.md`).
- Design: 3 consultant models give independent Round-1 opinions with quoted
  evidence → Round 2 each sees the others' opinions and may rebut → a
  `qwen3:32b` **chair** issues the final verdict. Full transcripts saved.
  Code: `labeller/llm_mdt.py`; ran on the 280 hardest cases (adjudicated + unsure).
- Results (`results/mdt_erin.json`): on the 78 adjudicated cases, chair
  accuracy **98.7% vs 97.4%** for Round-1 independent majority, with **zero
  conformity losses** (no case where deliberation talked a correct majority
  out of the right answer). 85/124 R1-disagreement cases converged to
  unanimity by R2. Caveat recorded: on the 201 unsure cases the chair claimed
  confidence ≥0.7 on 200/201 — treat chair confidence as uncalibrated there.

## 5. The label-space correction — per-section grading (the big rebuild)

**Rehan's correction (2026-09):** reports contain lettered specimen sections
(A, B, C…), each with potentially *multiple* grades, and cancer subtype matters
(adenocarcinoma / squamous / signet-ring / post-neoadjuvant treatment effect).
A single whole-report label is the wrong unit. Also: check Shiv Sakthivel's
prior ERIN work (Shiv left the lab — credited, not consulted).

- **New worker:** `labeller/llm_grade_sections.py` — per-section output
  (`sections_json`), grades incl. `NORMAL_OTHER`, subtypes
  `ADENOCARCINOMA / SQUAMOUS / SIGNET_RING / POST_NEOADJUVANT_TX_EFFECT / OTHER_CANCER`.
  Full-corpus run with a 5-juror GPU jury: parse-fail 0.3%, mean 2.36
  sections/report, 18,691 consensus section rows over 7,031 reports.
- **Section→slide join:** Shiv's matched table
  `/mnt/scratche/slow/fmlab/sakthi01/erin/data/matched_image_pathology.csv`
  (12,467 rows; `CaseName, Section, Filepath, SlideIdentifier, TissueName`)
  joined via slide uuid regex on Filepath + normalized section letter.
  Builder: `scripts/build_slide_labels.py` (majority = grade listed by ≥3/5
  jurors; section must be seen by ≥max(3, n−2) jurors) →
  `T/labeller/erin_slide_labels_v2.csv` (1,538 dual-labelled slides;
  `results/slide_labels_v2.json`).
- **Key stat:** **32.0% of slides get a different label from their own section
  than from the report's worst grade (case-max)** — the quantified cost of
  the standard weak-labelling shortcut.
- **2.38 binary contrast** (`scripts/task_slide_vs_casemax.py` +
  `task_svc_aggregate.py`, `results/slide_vs_casemax.json`): identical ABMIL,
  same patient folds, trained under case-max vs slide-level labels, evaluated
  on slide truth → **NULL**: case-max 0.871 vs slide 0.860, paired delta
  −0.010 [−0.028, +0.009]. Case-max is *robust for binary screening*.
- **2.38b five/six-class contrast** (`scripts/task_svc_5class.py`, classes
  NORMAL_OTHER<NDBE<IND<LGD<HGD<CANCER, macro-AUC + quadratic-weighted kappa,
  60 units, aggregator job 57370480): submitted 2026-09-08, **results pending**
  → will land as `results/svc_5class.json`. Tests whether section resolution
  pays off where the 32% disagreement actually lives.

## 6. Human grading (the comparison arm for the paper)

**Constraint that decided the architecture:** reports are redacted but still
NHS-sensitive → **no Vercel/Supabase/claude.ai hosting**. Two tools built:
1. Local single-user tool for Rehan: `/Users/zuberi01/Documents/erin_grading_tool.html`
   + `erin_grading_sample.json` (100 blinded cases; answer key
   `T/labeller/handlabel_sample_key.csv`, cluster only). **Never publish this
   HTML — it embeds report text.** Superseded by:
2. **Cluster-internal multi-grader web app v2:** `scripts/grading_app.py`
   (stdlib ThreadingHTTPServer + SQLite; data at
   `/mnt/scratche/slow/fmlab/zuberi01/hand_grading/{cases.json,grading.db}`).
   Per-section rows with grade + conditional subtype checkboxes, mirroring the
   LLM schema exactly so human vs jury comparison is like-for-like.
   **Overlap design:** every grader gets a common core of 20 cases (inter-rater
   agreement) + 20 unique cases (coverage), for 4–5 lab graders.
   URL `http://clust1-sub-1.cri.camres.org:8471` (CRI network only);
   passphrase + relaunch instructions in
   `/mnt/scratche/slow/fmlab/zuberi01/hand_grading/README.txt` (deliberately
   not written here — public repo). Status: live, awaiting lab uptake.
   A "verification mode" (pre-filled jury sections, accept/fix) is designed
   but not built.

## 7. Side quests riding the same pipeline

- **EoE case finder** (`labeller/llm_eoe_shard.py`,
  `results/eoe_finder.json`): DIAGNOSED/SUSPECTED/NEGATED/ABSENT + eos-per-hpf
  extraction → 26 diagnosed reports (17 patients), 77 suspected (66 patients),
  0 false EoE in 100 keyword-negative controls.
- **Phenotype discovery pilot** (`labeller/llm_phenotype_pilot.py`,
  `results/phenotype_pilot.json`): open-vocabulary findings extraction — 844
  distinct terms from 1,000 reports; full-corpus atlas (P3 paper) not yet run.
- **VLM supervision:** jury labels are the text side of the CLIP-style
  pretraining (`scripts/task_vlm_pretrain.py`; ERIN zero-shot 0.889,
  `results/vlm_pretrain*.json`).

## 8. Hard-won operational decisions (cost real time)

- **LLM inference is GPU-only.** ollama on epyc CPUs timed out on
  report-length prompts for ≥12B models and wrote PARSE_FAIL rows at exactly
  the timeout cadence — fake progress. ~2 days and 8,983 rows scrubbed
  (resume-by-CaseName redid them on GPU). Standing rule: content-check the
  first ~20 rows of any new LLM campaign.
- **h200 is preemptible** (QoS `h200_preempt`) — every h200 job gets a cuda
  twin; `clust1-h200-1` excluded (ECC faults). Race-to-run pattern in
  `feasibility/run_task.sh` (atomic mkdir lock + done.json).
- Small sharded jobs + short walltimes (backfill) beat monolithic arrays;
  campaign-scale rules in `COMPUTE.md`.

## 9. Where everything lives (quick map)

| Thing | Path |
|---|---|
| Raw redacted reports | `/mnt/scratche/fast/fmlab/datasets/imaging/ERIN/data/PathologyReport_AnonIds.csv` (cluster) |
| Master slide↔report↔label table | `T/labeller/erin_master.csv` (cluster) |
| Jury whole-report labels | `T/labeller/erin_labels_jury_final.csv` (cluster) |
| Per-section slide labels | `T/labeller/erin_slide_labels_v2.csv` (cluster) |
| Unsure held-out / adjudications | `T/labeller/erin_labels_unsure_heldout.csv`, `T/labeller/adjudications.csv` (cluster) |
| Progression cohort v3 | `T/labeller/erin_progression_cohort_v3.csv` (cluster) |
| Jury / section / MDT / EoE / TCGA workers | `labeller/llm_grade_shard.py`, `llm_grade_sections.py`, `llm_mdt.py`, `llm_eoe_shard.py`, `llm_grade_tcga.py` (repo) |
| Label builders | `labeller/build_erin_jury_labels.py`, `scripts/build_slide_labels.py` (repo) |
| Keyword baseline | `labeller/pathladder/` (repo) |
| Aggregate results | `results/erin_jury_labels_summary.json`, `lofo_jury.json`, `unsure_characterization.json`, `pancancer_jury.json`, `mdt_erin.json`, `slide_labels_v2.json`, `slide_vs_casemax.json`, `closure_cpu.json`, `eoe_finder.json`, `phenotype_pilot.json` (repo) |
| Decision log / pre-registrations | `EXECUTION_PLAN.md` (amendments 2.34–2.38b, SQ.1–2, P1), `docs/erin_ch3_preregistration.md` (repo) |
| Human grading app + data | `scripts/grading_app.py` (repo); data + passphrase on cluster under `hand_grading/` |

## 10. Open items

- 2.38b five-class results (aggregator 57370480) → commit + interpret.
- Lab grader uptake on the app; verification mode if wanted.
- P1 paper skeleton: jury design → robustness (LOFO, unsure) → external
  validation (pan-cancer) → MDT ≥ voting → section rebuild → 32% disagreement
  → binary null + five-class result → human comparison arm.
- Credit: Shiv Sakthivel (section↔slide matching table).

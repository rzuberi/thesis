# OCCAMS in this thesis — full reference (written 2026-09-01)

## 1. What OCCAMS is

OCCAMS (Oesophageal Cancer Clinical and Molecular Stratification consortium) is
a UK multi-centre oesophageal adenocarcinoma (OAC) study. Our slice of it is a
**resection cohort**: surgical specimens from primary OAC, not surveillance
biopsies. Per case the cluster holds:

- **H&E whole-slide images** — 635 slides across cases (RES resection blocks,
  some OGD endoscopy slides), under
  `/mnt/scratche/slow/fmlab/datasets/imaging/occams/wsi_data/slides/OCCAMS/`,
  with UNI2 tile features (`features_uni_v2`, 20x/224px) and — as of the
  encoder-sweep campaign — Virchow2/GigaPath/Phikon-v2/H-Optimus-0 features
  being extracted alongside.
- **Full WGS-derived genomics** (per-case TSV): TP53 status decomposed into
  SNV / indel / deletion / knockout flags (we use the composite max), ploidy,
  and whole-genome-doubling (WGD) status.
- **Clinical + outcome** (occams master CSV): survival
  (deceased/last-known-survival days), TNM staging (TNM7), age, performance
  status, Charlson comorbidity index, treatment fields.

ID space quirk: genomics uses OCCAMS/OC-AH style IDs with inconsistent
separators; every join goes through the `norm_occ()` normaliser
(OC-AH-013 → AH0013).

## 2. The n=87 attrition (fully audited)

The pre-registered fusion run used n=87, versus 276 slides on disk — a gap
reviewers flagged. The audited pipeline (recorded in
`results/occams_v3_shuffle.json` `_meta.attrition`):

| Stage | n |
|---|---|
| Slide feature bags on disk | 276 |
| Master rows with usable survival | 2,247 |
| Genomics TSV cases | 383 |
| Bags ∩ survival | 145 |
| Bags ∩ genomics | 141 |
| Survival ∩ genomics | 225 |
| **All three (analysis cohort)** | **87** (58 events) |

The binding constraint is genomics∩imaging: most imaged cases lack WGS and
most WGS cases lack digitised slides. This is a data-availability fact, not a
selection choice; the thesis states it as such.

## 3. Everything we did with OCCAMS, with results

### 3.1 Pre-registered external fusion test (plan item 1.1; Ch2)
`results/occams_v3.json` — ABMIL-Cox histology arm, linear-Cox genomics arm,
linear-Cox clinical arm (7 pre-registered columns), late fusion; Harrell's C,
patient-disjoint 5-fold, 3 seeds, paired bootstrap.

| Arm | C | 95% CI |
|---|---|---|
| Histology (ABMIL) | **0.627** | 0.539–0.711 |
| Genomics (TP53/ploidy/WGD) | 0.521 | 0.434–0.602 |
| Clinical | 0.536 | 0.458–0.624 |
| Late fusion hist+gen | 0.589 | delta vs hist **−0.040** [−0.104, +0.026] |
| Late fusion hist+clin | 0.613 | delta vs hist −0.015 [−0.070, +0.038] |

Verdict: histology carries what signal there is; adding WGS-derived genomics
or clinical **does not help and trends harmful**. One of the two external
fusion nulls that triggered the thesis reframe.

Controls: the original single-shuffle control (hist 0.574) sat off 0.5 and was
flagged; the 50-permutation follow-up (item 1.20) showed it sits inside the
legitimate null spread — resolved as shuffle-count noise, and the thesis's
"5 shuffles are not a control" methods lesson comes partly from here.

### 3.2 Genotype visibility, Part A negative (Ch2)
TP53/WGD-from-H&E ABMIL probes on OCCAMS: at chance. The matched-n learning
curve (`results/visibility_curve.json`, `occams_oac` stratum, n=141, 117
TP53-positive) is flat at every subsample size (AUC 0.50→0.53 from n=50→141,
never beyond its permutation null), while gastric/GEJ at the same n climbs to
0.61–0.69. Impact: OAC genotype-invisibility is a **population property, not a
sample-size artifact** — the load-bearing evidence that killed the earlier
"visible at adequate n" reading.

### 3.3 Teacher pool for the WGD-transfer studies (2.25/2.25b)
OCCAMS WGS-labelled resections contribute to the 562-case teacher pool
(with TCGA) for WGD/TP53 ABMIL teachers (`results/wgd_transfer.json`):
teacher CV passes its gates (WGD 0.730 [0.689–0.773], TP53 0.764
[0.722–0.803]) **in-domain on resections**, then inverts on surveillance
biopsies (ERIN progression AUC 0.315; SWG predicted-vs-measured CNV
complexity ρ=−0.10). Impact: OCCAMS helps prove that a resection-validated
"virtual biomarker" does not survive specimen-type shift — a Ch5 pillar.

### 3.4 Attention-shift replication (2.31)
`results/attn_shift_occams.json` — CondABMIL A (plain) / B (genomics-
conditioned) / C (permuted-genomics control), n=87: A-vs-B attention Spearman
0.984 = A-vs-C 0.984 (noise floor), Jaccard@10 0.709 vs 0.699, C-index B
(0.569) ≤ A (0.576). No shift. Paired with the TCGA-pool positive, the story
is coherent: genomic conditioning only redirects attention where genomics is
actually visible in the tissue — OCCAMS is the negative control that makes the
pair interpretable.

### 3.5 Power map stratum (2.23; Ch5 spine)
`results/power_map.json`: OCCAMS minimum detectable fusion delta at 80% power
is **~0.075–0.10 C-index** (by injected-signal correlation). Measured fusion
effects, where measurable at scale, run +0.01–0.04. Impact: the OCCAMS fusion
null (3.1) is re-read as **structurally underpowered for the plausible effect
size** — the quantitative core of "failure to replicate is largely failure to
power".

### 3.6 Cross-cohort transfer matrix cells (2.32)
`results/transfer_matrix.json`, 24-month landmark mortality, pooled-UNI2 +
identical linear machinery: OCCAMS→TCGA transfers what little it has
(within 0.598 → across 0.603); TCGA→OCCAMS collapses (0.621 → 0.489). Impact:
survival signal at these scales is weak and directionally fragile — supports
the generalisation-pessimism section.

### 3.7 Encoder sweep target (2.34; wave-3 gate item, in flight)
The pre-registered encoder grid was only ever run on ERIN grade; the wave-3
gap review (4/6 families) demanded it on the survival tasks. The current
extraction campaign is building Virchow2/GigaPath/Phikon-v2/H-Optimus-0
features for all 635 OCCAMS slides; `scripts/task_encoder_sweep_surv.py`
(auto-chained) then reruns the histology and late-fusion arms per encoder on
the same folds. Open question it answers: is the OCCAMS fusion null
encoder-conditional the way the SWG fusion win is?

### 3.8 Report-text side pull (2.15; supporting)
The Barrett's database exposes `view_masterpath_patient` (2,754 OC/AH
patients); used to investigate the attrition question above. OCCAMS free-text
reports are otherwise NOT used in Ch4 (no OCCAMS reports in the jury corpus).

### 3.9 PORPOISE deviation (1.4; honesty note)
Original plan wording said PORPOISE "on OCCAMS + TCGA-OAC". PORPOISE's omics
format requires per-gene RNA-seq, which OCCAMS lacks (WGS only) — so the
published-baseline test ran on the TCGA ESCA+STAD pool alone (its fusion also
failed to beat its own unimodal arm: −0.021 [−0.081, +0.035]). The thesis must
state this substitution explicitly.

## 4. Net impact on the thesis

OCCAMS is the thesis's **hardest external test and its most instructive
negative**. Every one of its results is a null or an inversion — fusion null,
genotype invisibility, no attention shift, weak transfer — and each acquired
an explanation with a number attached: the fusion null is power-bounded
(MDD ~0.075–0.10 vs real effects +0.01–0.04), the invisibility is
population-level (flat learning curve), the teacher inversion is specimen-type
domain shift. Without OCCAMS the thesis would be a single-cohort success
story; with it, the central claims — fusion gains are small, conditional, and
only measurable at scale; morphology-genome links are population-dependent;
virtual biomarkers don't transfer — have an external cohort behind each one.

## 5. Result-file index

occams_v3.json · occams_v3_shuffle.json (incl. attrition audit) ·
visibility_curve.json (occams_oac) · wgd_transfer.json · wgd_swg.json ·
attn_shift_occams.json · power_map.json (occams_v3 stratum) ·
transfer_matrix.json (surv24 cells) · closure_cpu.json (Holm: OCCAMS contrast
p_holm=0.69) · encoder_sweep_surv (pending).

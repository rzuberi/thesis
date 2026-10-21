# Two papers, agent ERL: fastest route to an external longitudinal H&E test (ERIN)

Written 21 October 2026. Paper 2, "External validation: ERIN archive". Counts only; cells < 5 are "<5". ERIN report text, identifiers and dates stay on the cluster (`feasibility/paper_plan/killcoyne_mm/two_papers_ERL/`).

## Plan (written before any count)

1. **Already-scanned ERIN slides.** From the jury report labels (`labeller/erin_labels_jury_final.csv`), the report table and the slide table (`campaigns/allslides/erin_slides_all.csv`, oesophageal H&E from the ISBI table `analysis/isbi_rerun/slides.csv` plus the v3 section sites), build one row per patient-endoscopy (patient + collection date). Event = first report graded HGD or CANCER (IMC included). Pre-event endoscopy = before the event, before any EMR/RFA/resection evidence, not itself HGD+. Count Barrett's patients with ≥ 2 and ≥ 3 pre-event endoscopies that have a scanned oesophageal H&E, split into progressors and non-progressors (with follow-up after the last scanned endoscopy: ≥ 1, ≥ 2, ≥ 3, ≥ 5 years). Exclude the Killcoyne-overlap patients (closeout pairs file ∪ the 70-patient union built for E5). Sensitivity rows: pre-event endoscopies non-dysplastic only (NDBE/IND); "unsure" reports treated as possible events.
2. **Feature scale.** Compare the ERIN all-slides features (20×, 224 px) with L-IMG's input (UNI2-h, level 2 ≈ 0.88 µm/px, 256 mask-sampled tiles, mean). Read the scanner model and pyramid from the TIFF headers. If they differ, cost re-extraction of the candidate slides at 0.88 µm/px (CPU tiles → GPU embed).
3. **Unscanned archive.** Trace the "~97 progressors, ~£6k" estimate (`docs/results_digest_2026-09-21_22.md` §1.2) and refine it for a memory test: progressors and matched non-progressors with ≥ 3 pre-event endoscopies (NP ≥ 5 years' follow-up), endoscopies and slides needed. Scan-request list stays on the cluster; a one-page plain request for the pathology lab goes at the end of this doc.
4. **Power.** Exact binomial CIs for NP cleared and progressors missed at the counts from (1) and (1)+(3); the person-years needed for the gastro safety bar (upper 95% CI of progression in the de-escalated group ≤ 0.2%/yr) and whether a case–control scan can assess it.
5. **If (1) is feasible:** extract features and build the patient–endoscopy table, but do not score the model against outcomes (needs the frozen rule hash from agent REG). Stop and report.

No ACE-B file is opened.

## Results

Run 21 October 2026. Scripts `scripts/paper_plan/tp_erl_{cohort,scanner,archive,checks,request}.py` (copies run from `killcoyne_mm/two_papers_ERL/code/`), Slurm campaigns `tperl1`–`tperl4` (CPU only, epyc/rocm/cuda). Aggregates in `results/paper_final/two_papers_ERL/`: `cohort_counts.json`, `scanner_and_scale.json`, `archive_designs.json`, `checks.json`, `scan_request_counts.json`. Row-level tables, the scan-request lists and their study-code keys are in `killcoyne_mm/two_papers_ERL/` on the cluster (chmod 600/700). No model was scored and no outcome was looked at against any score. No ACE-B file was opened.

### Smoke

The digest's ERIN 3-year funnel reproduces exactly with the same label file and rule: 2,092 index patients, 836 three-year-defined index cases, 115 progressors (`checks.json`).

It also shows where "~97 progressors" came from. The digest says "2014–2021 index blocks (818 cases, 97 progressors)", but 818/97 is 836/115 minus the 2023 and 2024 index years only. So it includes 2022 (19 cases, 18 progressors). For 2014–2021 the numbers are 799 cases and 79 progressors. The "£6k" was 97 progressor index cases plus ~200 matched negatives, about 600 slides at ~£10 each. That design scans **one** endoscopy per patient (the index), so it cannot test memory.

### 1. Already-scanned ERIN slides: not feasible

Every scanned ERIN H&E slide comes from a 2022–2025 case (1,086 scanned pre-event endoscopies: 2022 5, 2023 437, 2024 551, 2025 93), and the reports stop in March 2025. After excluding the 70 Killcoyne-overlap patients (pairs file ∪ E5 union) and post-treatment endoscopies (RFA/EMR/ESD/ablation/APC/cryo/neosquamous text, EMR or resection specimens):

| Scanned oesophageal H&E before any HGD/IMC/cancer | Progressors | Non-progressors | NP with ≥ 1 y follow-up after last scanned |
|---|---|---|---|
| ≥ 1 endoscopy | 15 | 944 | 5 |
| ≥ 2 endoscopies | <5 | 108 | 0 |
| ≥ 3 endoscopies | 0 | 16 | 0 |

Sensitivity rows (event = report label only; event = oesophageal v3 section only; "unsure" reports as events; non-dysplastic pre-event endoscopies only; clinical-history mention of prior HGD/cancer as a stop) move these by at most a few patients and never above 5 progressors with ≥ 2 scanned endoscopies (`cohort_counts.json`). None of the non-progressors reaches ≥ 5 years (or even 1 year) after their last scanned endoscopy. **So step 5 was not triggered: no features were extracted.** The patient–endoscopy tables were still built, for the archive designs below.

### 2. Feature scale and scanner

| | L-IMG input (Killcoyne slides) | ERIN all-slides features |
|---|---|---|
| Scanner | Hamamatsu (NDPI), 0.2204 µm/px at level 0 | **Philips UFS B300** (1,487 of 1,500 sampled `.fic` sidecars; 13 "Objective Imaging"; 6 devices), 0.248 µm/px at level 0 (0.2476–0.2484; a few 0.263) |
| Level used | 2 → 0.88 µm/px | 1 → ~0.50 µm/px (pipeline assumed 0.25 at level 0; the TIFFs carry no mpp tag, the `.fic` does) |
| Tiles | 256 tile centres sampled at random from a tissue-detector mask, 224 px | all tissue tiles, 224 px (median 2,319 per slide) |
| Pooling for L-IMG | mean embedding | — |

They do not match: scale (0.50 vs 0.88 µm/px), tile selection and scanner all differ. ERIN slides were scanned in the same year as the case for 1,465 of 1,486 (prospective digital reporting), so there is no back-scanned archive on disk.

**Re-extraction recipe and cost.** Read level 1 (0.495 µm/px) regions of 398 × 398 px (= 197 µm, the field of a 224 px tile at 0.882 µm/px), resize to 224, at 256 random tissue centres from a thumbnail mask; CPU jobs write uint8 tiles, GPU jobs embed (`ex_e5_tiles.py` / `ex_e5_embed.py` pattern). Measured UNI2-h throughput in E5 was 117 tiles/s per GPU, so ~2.2 GPU-s per slide. For the request lists below: ~565 slides (ERIN list) ≈ 0.4 GPU-h, ~1,950 slides (Barrett's-DB list) ≈ 1.2 GPU-h, plus model loading (≤ 2 GPU-h in all) and ~10–20 CPU-s per slide for tiling (≤ 11 CPU-h, sharded). Compute is not the constraint. Deviation to report: our mask would be a thumbnail threshold, not the tissue-detector masks used for the Killcoyne slides.

### 3. Unscanned archive: refined counts

Two ways to define who to scan. Both use the same Addenbrooke's pathology archive (PS accession numbers).

- **(A) ERIN report history** (2014-10 to 2025-03; 2,537 patients but only 2.8 reports per patient).
- **(B) The Cambridge Barrett's database** (`barretts_db_export`, coded confirmed grade per report, 1995–2026, an HGD register, endoscopy records with Prague M). 1,476 eligible Barrett's participants after excluding 162 SWG/Killcoyne-linked participants. Much longer histories. It overlaps ERIN: 590 of the 2,752 endoscopies in the DB k ≥ 2 design have an ERIN report.

Patients with k pre-event Barrett's endoscopies (before HGD/IMC/OAC and before any treatment); NP need h years of follow-up after the k-th (`archive_designs.json`):

| Design | Progressors | NP eligible | Endoscopies to scan | Slides (≤ 2 per endoscopy) | Endoscopies before 2016 | NP person-years after k-th (all NP with ≥ k) | Crude incidence after k-th |
|---|---|---|---|---|---|---|---|
| ERIN k ≥ 2, h ≥ 3 | 36 | 313 | 941 | 1,690 | 145 | 1,773 | 1.9 /100 py |
| ERIN k ≥ 3, h ≥ 5 (gastro criteria) | 14 | 62 | 267 | 493 | 56 | 828 | 1.6 /100 py |
| DB k ≥ 2, h ≥ 3 | 74 | 541 | 2,752 | ~5,500 | 2,176 | 5,261 | 1.3 /100 py |
| DB k ≥ 3, h ≥ 5 (gastro criteria) | 48 | 309 | 1,905 | ~3,810 | 1,625 | 3,759 | 1.2 /100 py |

DB designs restricted to recent endoscopies (`checks.json`): from 2005, k ≥ 2 → 68 P / 453 NP; from 2010 → 59 / 329; from 2014 → 39 / 219. With k ≥ 3, h ≥ 5: 43 / 242 (2005+), 34 / 160 (2010+), 14 / 74 (2014+).

So the real limit is progressors with repeat pre-event endoscopies, not money: the ERIN reports give 36 with ≥ 2 and 14 with ≥ 3; the Barrett's database gives 74 and 48. In both, incidence after the k-th endoscopy (1.2–1.9 per 100 person-years) is 3–6 times the guideline NDBE rate (0.3–0.6%/yr), as expected for a referral surveillance centre.

**Scan-request lists (cluster only).** `tp_erl_request.py`: all progressors with ≥ 2 pre-event endoscopies (all pre-event endoscopies requested); NP by the gastro criteria (≥ 3 endoscopies, ≥ 5 y after the third), 2 per progressor, matched on the year of the second endoscopy and on 2–3 vs 4+ endoscopies (seed 0; median year difference 0, 85% within 3 years); NP endoscopies with ≥ 5 y follow-up after them. The NP sampling fraction is stored so cohort person-years can be reweighted.

| List | Progressors (≥ 3 endoscopies) | NP sampled / pool | Endoscopies to scan | Slides, ≤ 2 per endoscopy | of which before 2016 | Slides if every oesophageal block |
|---|---|---|---|---|---|---|
| `scan_request_ERIN_final.csv` | 36 (14) | 62 / 62 | 305 (8 already scanned) | 565 | 110 | 1,063 |
| `scan_request_DB_final.csv` | 74 (48) | 148 / 309 | 977 (5 already scanned) | ~1,954 | ~1,456 | unknown (DB has no block count; 2 assumed) |

The lists hold study codes, role, order, accessions and (ERIN) oesophageal section letters; the `_KEY` files hold the patient IDs and dates.

### 4. Power

Assumed tier performance from the Killcoyne cohort: 16.4/43 NP cleared (0.381), 1/32 progressors missed (0.031). Exact (Clopper–Pearson / Poisson) 95% CIs. Person-years in the de-escalated group = 0.381 × all NP person-years of the sampling frame (reweighted, so they do not depend on how many NP are scanned). The safety bar needs ≥ 1,844 de-escalated person-years with 0 misses, 2,786 with 1, 3,612 with 2.

| Counts | NP cleared, CI (width) | Progressors missed: CI if 0 / if 1 | De-escalated person-years | Upper 95% progression in de-escalated, 0 missed / expected missed | Safety bar (≤ 0.2%/yr) |
|---|---|---|---|---|---|
| (1) scanned only | — | — | ~0 | — | not assessable |
| ERIN list (36 P, 62 NP) | 0.27–0.52 (0.25) | 0–9.7% / 0.1–14.5% | 316–676 | 0.55–1.17 / 0.82–1.17 %/yr | not assessable |
| DB list (74 P, 148 NP) | 0.30–0.46 (0.16) | 0–4.9% / 0.0–7.3% | 1,434–2,007 | 0.18–0.26 / 0.36–0.50 %/yr | only if no progressor is missed (k ≥ 2 frame); not at expected misses (1.5–2.3) |
| DB, all eligible NP (k ≥ 2, 541) | 0.34–0.42 (0.08) | as above | 2,007 | 0.18 / 0.36 %/yr | as above |

Reading: the DB list measures the two quantities memory changes (NP cleared to ±8 points; missed progressors to an upper bound of 5–7%). The absolute safety bar cannot be shown to pass at the expected miss rate in any Cambridge archive: it would need about 3,600 de-escalated person-years, about 9,500 NP person-years. Unless that is pooled across centres, pre-specify the bar as an upper bound to report, and add a relative bar (progression rate in the de-escalated group vs all eligible patients), which carries over to centres with lower incidence.

### What changes in the paper plan

The ERIN archive in its current form (scanned since 2022) cannot test memory. The fastest real test is a targeted retrieval defined by the Cambridge Barrett's database rather than by ERIN reports: 74 progressors with ≥ 2 pre-event endoscopies and 148 matched non-progressors, about 1,950 slides. The gastro safety bar cannot be passed in this cohort at the expected miss rate, so state it as an upper bound plus a relative bar.

### Caveats

- Event and treatment flags in ERIN come from jury labels and text regexes; the DB grade is the database's coded confirmed grade (a coding of the report, not a slide re-read).
- "Pre-event" includes LGD endoscopies; the non-dysplastic-only sensitivity row cuts ERIN progressors with ≥ 3 from 14 to 11.
- Slide counts for DB endoscopies assume 2 per endoscopy; ERIN cases average ~3.5 oesophageal blocks per endoscopy, so the uncapped count could be about 1.7× higher.
- Slides older than about 10 years may no longer exist as glass (the usual minimum retention is 10 years for slides, 30 for blocks), so most of the DB list may need new H&E sections cut from blocks. A recut is a different level from the diagnostic slide.
- The scanner (Philips UFS) differs from the Killcoyne slides (Hamamatsu); this is a transport test of scanner as well as of patients.
- The `np_fu_ge_*` columns in the step-3 block of `cohort_counts.json` are follow-up after the third pre-event endoscopy for every row; `archive_designs.json` supersedes them.

## Request to the pathology lab (one page, plain text, ready to send)

Subject: Request to retrieve and scan archived Barrett's surveillance biopsies (research, no new patient contact)

We would like to test a slide-based risk score for Barrett's oesophagus on patients' earlier surveillance biopsies. Most of these biopsies were reported before digital scanning started, so the slides are only in the archive.

What we are asking for: H&E slides from earlier oesophageal biopsies of 222 patients in the Cambridge Barrett's surveillance programme. Of these, 74 later developed high-grade dysplasia or early cancer and 148 did not over at least five years of follow-up. Together they had 977 surveillance endoscopies. We would like up to two H&E slides of the oesophageal biopsies from each endoscopy, about 1,950 slides in all. We can send a list of accession numbers (and block letters where known) on request through the usual secure route; no patient names or hospital numbers are needed in the list.

Who is included: patients with Barrett's oesophagus who had at least two surveillance endoscopies with biopsies before any high-grade dysplasia, cancer or endoscopic treatment. For patients who did not progress, we need at least three such endoscopies and at least five years of follow-up after the third. Patients already in our earlier sequencing study are excluded.

About 1,450 of the slides come from endoscopies before 2016. If the glass slides from those years are no longer kept, we would ask for one new H&E section from each block instead. A smaller alternative, limited to endoscopies from 2011 onwards: 98 patients (36 who progressed, 62 who did not), 305 endoscopies, about 565 slides, of which about 110 are from before 2016.

Cost: our planning figure is £10 per slide for retrieval and scanning, so about £19,500 for the full list or about £5,700 for the smaller one, plus the cost of any new sections. Could you give us a quote, including recuts, and an estimate of time per batch?

Slides would be scanned on the department's routine scanner and returned to the archive. Images stay on the CRUK Cambridge Institute secure cluster and no report text leaves it.

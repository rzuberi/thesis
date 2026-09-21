# Numbers dossier — every count and result in one place

Generated 2026-09-21 by `scripts/numbers/assemble_numbers_md.py` from committed result JSONs. Each item: the number, one sentence, the source file. Items I could not compute are marked **MISSING** with what is needed.

Cohort key: **SWG** = Cambridge Barrett's progression cohort (H&E + sWGS); **ERIN** = Cambridge Barrett's surveillance reports + slides; **OCCAMS** = OAC resection/biopsy consortium slice; **ACE-B** = Dr di Pietro's Barrett's cohort (134 patients, 7× sWGS; slides being scanned) used only as an external validation set; **Hannah Coles set** = 221 OCCAMS OGD staging biopsies, not yet linked to patients.


# A. Dataset descriptions


## 1. Patients, cases/biopsy events, slides; slides per patient

- **SWG:** 150 patients, 707 biopsy samples in the frozen pre-event release; samples per patient median 3 (range 1–19, n=150). Slides on disk: 1028 `.ndpi` across 173 patients (1005 attributable); slides per patient median 4 (range 1–30, n=173). *(num_swg_cohort; docs/swg_barretts_slides.csv)*
- **ERIN:** 2537 patients, 7149 reports; 12347 slide files in 2280 cases from 1614 patients, of which 11672 are H&E; H&E slides per case median 3 (range 1–88, n=2268), per patient median 3 (range 1–138, n=1608). Total 6.35 TB. *(num_erin_cohort)*
- **OCCAMS:** 276 cases with slides (635 slide feature files); slides per case median 2 (range 1–11, n=276); 145 of these cases have a clinical master row. *(num_occams)*
- **ACE-B:** 153 official study cases (list from Fitzgerald lab); 111 patient codes with 269 endoscopy records in the Barrett's database view (per patient median 2 (range 1–7)). No slides or features on the cluster yet. *(num_aceb; phd/aceb_meta, May 2026)*

## 2. Source hospital(s), years of collection

- **SWG:** Cambridge (Addenbrooke's) surveillance; biopsy dates 1994–2017.
- **ERIN:** Cambridge University Hospitals histopathology; report dates 2014–2025 (busiest years [('2024', 1168), ('2022', 989), ('2023', 941)]).
- **OCCAMS:** UK multi-centre consortium; diagnosis years for the imaged cases 2010–2019. Contributing centres per case are not in our master extract.
- **ACE-B:** Addenbrooke's (Rehan); trial endoscopies (AFI/WLE dates on the official case list) 2017-05-18 to 2020-02-18, by year {'2017.0': 17, '2018.0': 60, '2019.0': 51, '2020.0': 6}; in the Barrett's database the same participants have endoscopies from 2009-08-20 to 2026-08-17 (surveillance before and after the trial). *(num_aceb_db)*

## 3. Tissue and cancer type breakdown

- **SWG:** all Barrett's oesophagus surveillance biopsies (oesophageal); grade breakdown in item 8.
- **ERIN:** organ metadata is known for 58% of slide files: {'(blank)': 5169, 'OESOPHAGUS': 5140, 'LYMPH NODE': 1099, 'STOMACH': 479, 'DUODENUM': 165, 'SOFT TIS NOT TUM/MAS/LIP/DEB': 131, 'COLORECTAL': 86, 'POLYP': 57, 'MISCELLANEOUS / UNSPECIFIED': 14, 'SOFT TIS TUMOR EXTENSIVE RES': 3, 'STOMACH-SUB/TOT RES FOR TUMOR': 1, 'OMENTUM': 1, 'SOFT TIS MASS BX SIMP EXCISION': 1, 'PERITONEUM': 1}. Stain types: {'Haematoxylin and eosin stain (H&E)': 11672, 'Special stain': 282, '(blank)': 281, 'Immunohistochemistry (IHC)': 112}. Report specimen protocols (top): {'OESOPHAGUS': 6654, 'OESOPHAGUS, PART/TOT RESECTION': 490, 'POLYP, STOMACH/SMALL INTESTINE': 1, 'ADIPOSE TISSUE': 1, 'DIVERTICULUM-OESOPHAGUS/SM INT': 1, 'STOMACH, BIOPSY': 1, 'LYMPH NODES, REGIONAL RESECT': 1}. The remaining organs come from the report gross description via jury v3 `site` (consensus builder not yet written).
- **OCCAMS:** oesophageal adenocarcinoma by design; slide specimen mix {'RES': 322, 'OGD': 286, 'NOT-HE': 25, 'OTHER': 2} (RES = resection block, OGD = endoscopic biopsy, NOT-HE = IHC/special stain).
- **ACE-B:** Seattle-protocol histology on the official case list: {'IM': 101, 'LGD': 12, 'HGD': 12, 'ID': 6, 'IMC': 3} (IM = intestinal metaplasia/NDBE, ID = indefinite).

## 4. Disease status at entry and treatment status

- **SWG:** grade of each patient's first release sample (codes 0=NDBE,1=IND,2=LGD,3=HGD,4=IMC): {'0': 121, '2': 16, '1': 13}. All samples are pre-event by construction (taken before the first confirmed LGD+); no treatment fields in the release.
- **ERIN:** first-report jury grade per patient: {'NDBE': 1701, 'CANCER': 468, 'HGD': 124, 'unsure': 95, 'IND': 81, 'LGD': 68}. Treatment status is not a structured field; post-treatment surveillance appears as CANCER→NDBE transitions in the natural-history matrix (238 such transitions in the database export).
- **OCCAMS:** established cancer at entry; pre-treatment T {'t3': 115, 't2': 22, 'tx': 4, 't4a': 2, 't4': 1, 't1b': 1}, N {'n1': 65, 'n0': 46, 'n2': 26, 'n3': 7, 'nx': 1}. Neoadjuvant regimen (grouped): {'ECF/ECX/EOF/EOX': 118, 'CRT-CF/CX': 9, 'CF/CX/XELOX/FOLFOX/CAPOX': 8, 'FLOT': 3, 'CF/CX/XELOX/FOLFOX/CAPOX-lapatinib': 2, 'CRT-CROSS': 2, 'CRT-unknown': 1, 'CRT-CX': 1, 'Other-Singleagent': 1}.
- **ACE-B:** {'IM': 101, 'LGD': 12, 'HGD': 12, 'ID': 6, 'IMC': 3} at trial entry; treatment status unknown to us.

## 5. Modalities available and the all-modality intersection

- **SWG:** H&E (UNI2 features on 707 slides) + sWGS copy-number (707 samples, 150 patients). Both modalities: 707 samples / 150 patients (missing UNI2: 0, missing CNV: 0).
- **ERIN:** reports (all 7149) + H&E slides (11672) + report-derived clinical fields; no genomics. Reports with an H&E slide on disk: 2282; H&E slides with UNI2 features: 11654 (without: 18).
- **OCCAMS:** H&E (276 cases) + WGS genomics (383 cases, 141 with slides) + clinical/survival (145 slide cases with a master row). All three with usable survival: **87 cases (58 deaths)** — attrition 276→145→141→87 (docs/occams_reference.md).
- **ACE-B:** metadata only; {'yes': 125, 'no': 28} of the official cases were found in the Barrett's database.

## 6. Label definition, source, positives

- **SWG progression:** per-sample endpoint — the *next* biopsy after this sample shows LGD confirmed on two reads or worse (`NextBiopsyProgression_LGD2plus`); source = pathology follow-up in the Barrett's database. Positive samples 107/707 (15.1%); progressor patients (any positive sample) **50/150** (33%). The database's own `Progressor_label` flag marks 35 patients — a stricter, different definition; the models use the former.
- **ERIN grade:** NDBE vs LGD+ from the report; source = 8-model LLM jury. Train-eligible reports 6867, LGD+ 1506 (21.9%); at slide level 528/2,153 positive (24.5%).
- **ERIN progression:** index NDBE/IND report → any later HGD or cancer report (jury labels); 181/1266 patients (14.3%). Slide-level progression cohort 28/153.
- **OCCAMS survival:** overall survival from the master table (vital_status/deceased_survival_days); 58 deaths / 87 in the fusion cohort. **TRG response:** Mandard TRG on the resection, 41 responders (TRG1–3) / 131 with an OGD slide (31%).
- **ACE-B (derived from the Barrett's-database scrape, LLM-jury grades on every report from trial entry onward):** of 115 participants with graded reports, baseline grade {'NDBE': 85, 'HGD': 13, 'LGD': 10, 'IND': 4, 'CANCER': 3}; **prevalent HGD/cancer at entry 16, progressed to HGD/cancer 18, non-progressors 81** — close to Leanne's 30 / 11 / 93 (our progressor count is higher because DB follow-up runs to 2026 and grades are LLM-derived, not trial-adjudicated). Leanne's split is the label to use; ours is the cross-check.

## 7. Time structure: time points, follow-up, censoring

- **SWG:** samples per patient median 3 (range 1–19, n=150); gap between consecutive biopsies median 708 days (range 1–1981 days, n=707); first-to-last sample span, progressors median 24.343 months (range 0–135.742 months, n=50), non-progressors median 0 months (range 0–157.654 months, n=100). Non-progressors are censored at their last biopsy.
- **ERIN:** reports per patient median 2 (range 1–21, n=2537); 1459 patients have ≥2 reports; follow-up span for them median 3.77002 y (range 0–10.308 y, n=1459). Progression cohort v3: time to HGD+ in progressors median 245 days (range 9–3227 days, n=181), follow-up in non-progressors median 1530 days (range 4–3765 days, n=1085) (censored at last report).
- **OCCAMS:** single time point per case (diagnostic biopsy and/or resection); survival: vital_status present for 145 slide cases, death dates 94, last-known-alive days 50.
- **ACE-B (DB-derived):** 120 participants with endoscopies in the database, median 8 (range 1–24, n=120) per participant; pathology reports from trial entry median 4 (range 1–17, n=115) per participant; time to progression median 402 days (range 56–1657 days, n=18); follow-up of non-progressors median 1925 days (range 0–2997 days, n=81) (≈5.3 y median).

## 8. Grade distribution where a grade exists

- **SWG slide level** (release samples, codes 0–4): {'0': 560, '2': 87, '1': 60}; **patient level (max grade):** {'0': 97, '1': 15, '2': 38}. Slide-CSV grades on disk: {'NDBE': 629, 'LGD': 162, 'HGD': 77, 'IND': 67, 'NaN': 48, 'CANCER_IMC': 37, 'LGD (DB jury, specimen-level)': 3, 'normal': 3, 'GM': 2}.
- **ERIN report level (train-eligible):** {'NDBE': 5105, 'CANCER': 834, 'HGD': 404, 'LGD': 268, 'IND': 256}; **patient level (max grade):** {'NDBE': 1561, 'CANCER': 622, 'HGD': 141, 'LGD': 92, 'IND': 91}; **slide level, section-resolved (1,538 dual-labelled):** {'NORMAL_OTHER': 685, 'NDBE': 589, 'LGD': 82, 'CANCER': 81, 'HGD': 66, 'IND': 35}; **section level (7099 reports):** {'NORMAL_OTHER': 8101, 'IND': 478, 'NDBE': 7306, 'HGD': 888, 'CANCER': 1186, 'LGD': 732}.
- **OCCAMS:** TRG {'4': 72, '3': 24, '5': 21, '1': 11, '2': 8}; resection pT {'t3': 80, 't2': 19, 't1b': 11, 't0': 11, 't4a': 10, 'tx': 6, 't1a': 5, 't4': 2, 't1': 1}, pN {'n0': 53, 'n1': 41, 'n3': 24, 'n2': 20, 'nx': 7}.
- **ACE-B:** {'IM': 101, 'LGD': 12, 'HGD': 12, 'ID': 6, 'IMC': 3}.

## 9. Missingness per modality

- **SWG:** 0 release samples lack UNI2 features and 0 lack a CNV complexity value; UNI2 index status {'ok': 707}; 26 of 1028 slides on disk are unattributable to a patient.
- **ERIN:** organ metadata missing for 42% of slide files; 18 H&E slides still lack features (1189 logged extraction failures); jury label unsure/held-out for 204 reports; no genomics at all.
- **OCCAMS:** imaging∩genomics is the binding constraint (141 of 276 imaged cases have WGS; 87 also have survival). Recurrence date present for only 21 of 145 slide cases (and 540 of 2,393 master rows overall) — recurrence is under-recorded, not rare.
- **ACE-B:** everything except the case list and endoscopy metadata is missing.

## 10. Access status and what is pending

- **SWG:** on cluster, canonical copy at `/mnt/scratche/slow/fmlab/datasets/imaging/SWGCohort/slides/` (567 GB, pseudonymised: accession numbers in filenames). Pending: 26 unattributable slides need Leanne's scanning log; grade-code map (R.5).
- **ERIN:** on cluster; all-slides UNI2 extraction 11781 h5 done; jury v3 (site + specimen type per section) full corpus complete (80/80 shards), consensus builder pending. Pathologist re-grading pending (grading app live).
- **OCCAMS:** on cluster; master CSV of 11 May 2026; genomics TSV 383 cases. Pending: nothing for the thesis; recurrence completeness limits any recurrence model.
- **ACE-B:** metadata matched May 2026 ({'yes': 125, 'no': 28} found in DB); slide access and governance path (Fitzgerald lab / Tim Somerset) pending; no compute yet.

# B. Barrett's-specific (SWG)


## 11. Progressors vs non-progressors

- **50 progressors / 100 non-progressors** (150 patients) under the model endpoint (any sample whose next biopsy is LGD2+); 107 positive samples of 707. Under the database `Progressor_label` flag: 35 progressor patients.

## 12. Time to progression / follow-up

- Progressors: time from sample to progression median 1095 days (range 50–5262 days, n=121) (≈3 years median); their samples sit median 29.4374 months (range 0–172.879 months, n=201) before the last biopsy; first-to-last biopsy span median 24.343 months (range 0–135.742 months, n=50). Non-progressors: span median 0 months (range 0–157.654 months, n=100), samples median 22.5709 months (range 0–157.667 months, n=506) before last biopsy. Biopsies per patient in the database median 4 (range 1–11, n=707). Samples with progression within k years: {'Progress_in_1': 11, 'Progress_in_2': 35, 'Progress_in_3': 64, 'Progress_in_4': 86, 'Progress_in_5': 95}.

## 13. How progression was defined

- Endpoint is LGD confirmed on two independent reads (the release name `lgd2`) or any higher grade, using the strict pre-event design: only samples before the first qualifying diagnosis enter. Source: PROJECT_STATE lines below. Who confirmed the reads (pathologist review vs database grade) is stated in the release documentation, not re-verified here.
  > - Primary endpoint: `NextBiopsyProgression_LGD2plus`.
  > - Primary LGD2+ strict next-biopsy master: `data/derived_nextbiopsy_lgd2_strict_nextbiopsy_CANONICAL_ONLY_20260319/derived_master.csv`
  > - Primary LGD2+ 5-fold campaign: `data/foundation_grid_runs/campaign_lgd2_nextbiopsy_lgd2_refresh_cuda_20260319_142251/`
  > - Primary LGD2+ patient aggregation: `data/foundation_grid_runs/campaign_lgd2_nextbiopsy_lgd2_refresh_cuda_20260319_142251/core_lvl2/patient_aggregation/`
  > - LGD2+ modality shuffle/ablation support: `data/foundation_grid_runs/campaign_lgd2_h200_patient_signal_lgd2_20260319/`
  > - Patient-level LGD2+ metrics (AUPRC, ROC AUC, Brier/calibration, PPV/NPV, FP/TN, fixed operating points, bootstrap CIs) are computed in `reports/thesis_ch1/lgd2_patient_level_metrics_all_samples.csv`.
  > - Early-prediction-only sensitivity analysis (excludes `DaysFromCurrentToEvent == 0`) is complete: `reports/thesis_ch1/lgd2_patient_level_metrics_early_prediction_only.csv`.
  > - Late fusion (`mean`, `stack_logit`) integrated at patient level for uni2/virchow2/gigapath; see manifest rows `lgd2_late_fusion_*`.
  > - ABMIL histology interpretation complete for all eight selected LGD2+ cases (external outputs, `pathology` env); no environment blocker remains.
  > - Frozen strict pre-event cohort release: 707 matched rows, 150 patients, 693 unique CNV profiles; at-event and post-event rows excluded before splitting.
  > - Final five-fold patient-disjoint nested-CV rerun complete for CNV-only, UNI2 ABMIL, early fusion, intermediate fusion, late mean, and late stack-logit on identical rows/patients.
  > - LGD2+ CNV feature-importance interpretation is now AVAILABLE. The July 13 final

## 14. Case-control matching

- Two different things are called 'matching' here. (a) **Slide↔sWGS file matching** (Rehan's Dec 2025–Feb 2026 work, `slide_matching.xlsx`, `matched_manifest.csv`): every one of the 707 release rows has a paired image and CNV sample; `matching_sensitivity.csv` shows the effect of match strictness — restricting to exact matches leaves 532 rows / 111 patients / 24 positives and late-mean AUC 0.723 (image 0.672, CNV 0.645), i.e. the fusion pattern holds but with fewer positives. (b) **Case-control matching in the epidemiological sense** — were non-progressors *selected* to resemble progressors on age/sex/segment length? PROJECT_STATE calls SWG an 'internal matched cohort' and Killcoyne 2020's discovery set was 45 progressors vs 43 non-progressors by design, which suggests selection rather than a consecutive series.
- **MISSING** — (b) only: whether SWG non-progressors were selected to match progressors, and on what — ask Leanne; matters for how the 33% progressor rate (vs <1%/yr in practice) is described.

## 15. CNV: platform, resolution, samples, timing

- Platform: shallow whole-genome sequencing (sWGS) of the same biopsy as the slide; 707 samples with a copy-number complexity value from 150 patients (693 unique CNV profiles; release notes 693). Per sample, i.e. per biopsy, time-matched to the slide by construction (same specimen).
- Depth 0.4× (Rehan, 21 Sep 2026); bin size 50 kb, the Killcoyne 2020 pipeline (6 March 2026 slides: 'Sequencing depth 0.4x, Bin size 50kb'). ACE-B, by contrast, is sequenced at ~7× (item 25), so its CNV must be re-called at matched resolution/depth before the SWG CNV arm is applied.

## 16. UNI2 embeddings

- 707 slides with UNI2 embeddings, 1536-d; patches per slide median 256 (range 256–256, n=707) — the release stores a fixed 256-tile subsample per slide, not all tissue tiles; 224-px tiles at 20× (release folder `uni2_tile224_lvl2`). ERIN for comparison: patches per slide median 2226 (range 21–8000, n=11781) at 0.5 mpp/224 px.

# C. Barrett's results (current)


## 17. Split strategy

- Patient-level, 5 outer folds (`fold_id_rep01`), nested CV inside each fold for hyper-parameters; folds seen per family [1, 2, 3, 4, 5]; seeds present [20261713, 20262713, 20263713, 20264713, 20265713] → **one repeat**; seeds differ per fold (one seed each), not per repeat. single nested-CV run, 5 outer folds, patient-disjoint (fold_id_rep01); one seed per family in release

## 18. Per-arm AUROC / AUPRC with CIs

| arm | patient-level AUROC [95% CI] | AUPRC [95% CI] | sample-level AUROC |
|---|---|---|---|
| image_only | 0.7312 [0.6403, 0.8142] | 0.557 [0.4263, 0.7168] | 0.739 [0.6456, 0.8147] |
| cnv_only | 0.663 [0.5687, 0.7542] | 0.5385 [0.4107, 0.6712] | 0.6195 [0.5319, 0.7132] |
| late_mean | 0.7742 [0.6872, 0.8494] | 0.6296 [0.4897, 0.7724] | 0.7584 [0.6691, 0.8333] |
| early_fusion | 0.7384 [0.6455, 0.8182] | 0.5896 [0.4529, 0.7331] | 0.7296 [0.6369, 0.813] |
| intermediate_fusion | 0.7414 [0.6534, 0.8179] | 0.5675 [0.4352, 0.7142] | 0.7049 [0.6059, 0.7997] |
| coattention_fusion | 0.7392 [0.6519, 0.8207] | 0.5482 [0.4278, 0.7027] | 0.6825 [0.5956, 0.7691] |
| late_stack_logit | 0.7366 [0.6478, 0.8138] | 0.5303 [0.412, 0.6842] | 0.7309 [0.641, 0.8087] |
- **Clinical baseline** (no clinical variables exist in the release; the pathologist grade of the biopsy used as the score): sample-level AUROC 0.6514, patient-level (max grade) 0.687.
- CIs are 2,000-replicate patient-resampled bootstraps. Positives: 50 of 150 patients. *(num_swg_metrics)*

## 19. Sensitivity and specificity at a stated threshold

- **Chosen operating rule (Rehan, 21 Sep 2026): lock sensitivity at 0.95 (and, as the no-miss standard, 1.0) and report the specificity that buys.** This is a rule-out framing: we refuse to miss progressors and ask how many non-progressors we can safely de-escalate. (Youden's J is just the threshold maximising sensitivity+specificity−1 — a symmetric default with no clinical weighting; kept below for reference only.) The March slides used the same family of convention, Spec@Sen90 and Sen@95.
| arm (patient level) | spec @ sens 0.95 | flagged/n | NPV @ cohort prev (33%) | NPV @ 0.5%/yr | spec @ sens 1.0 | Youden sens/spec |
|---|---|---|---|---|---|---|
| late_mean | 0.28 | 120/150 | 0.933 | 0.9993 | 0.21 | 0.60/0.85 |
| image_only | 0.16 | 132/150 | 0.889 | 0.9987 | 0.12 | 0.64/0.77 |
| cnv_only | 0.07 | 141/150 | 0.778 | 0.9971 | 0.05 | 0.74/0.58 |
| early_fusion | 0.18 | 130/150 | 0.900 | 0.9989 | 0.05 | 0.80/0.60 |
- Read: at sensitivity 0.95, specificity is the fraction of non-progressors the model would release from intensified surveillance; NPV at 0.5%/yr shows what that means at real-world progression rates (where almost any test has NPV > 0.99, so specificity, not NPV, is the discriminating number). Thresholds are set post hoc on out-of-fold predictions; in a deployment they would be fixed on training folds.
- **What the field reports (checked 21 Sep 2026):** TissueCypher's independent blinded validation (Davison et al. 2020) gives sensitivity 29% / specificity 86% for its 3-tier risk class and 40% / 86% for 2-tier at 5 years; its clinical-utility study (Diehl et al. 2021) reports sensitivity 62.3%, specificity 79.8%, prevalence-adjusted NPV 97.4%. Killcoyne 2020 reports low/moderate/high risk classes rather than a single operating point. So the field's convention is **rule-in** (high specificity ~0.80–0.86, sensitivity 0.3–0.6). Our late-mean model at specificity 0.80 has sensitivity 0.62 — the same operating region as TissueCypher's 62%/80%. Recommendation: report both — spec at sens 0.95 (our rule-out standard) and sens at spec 0.80/0.86 (comparable to TissueCypher).

## 20. Calibration

- **late_mean:** Brier 0.184; calibration slope 1.78, intercept 0.10; reliability (decile mean-pred → observed): [(0.152, 0.0), (0.213, 0.133), (0.254, 0.2), (0.3, 0.267), (0.351, 0.133), (0.397, 0.4), (0.441, 0.2), (0.479, 0.733), (0.537, 0.467), (0.622, 0.8)].
- **image_only:** Brier 0.245; calibration slope 0.62, intercept -0.99; reliability (decile mean-pred → observed): [(0.125, 0.067), (0.237, 0.133), (0.316, 0.2), (0.388, 0.267), (0.503, 0.333), (0.614, 0.133), (0.707, 0.467), (0.795, 0.333), (0.865, 0.733), (0.936, 0.667)].
- Also on file: late-mean minus GigaPath-histology Brier delta −0.048 [−0.085, −0.011] (results/latemean_vs_gigapath_paired.json). No reliability curve existed before this dossier.

## 21. Headline configuration and alternatives

- Headline was **late-mean fusion** (UNI2 ABMIL risk averaged with CNV risk): naive AUROC gain over image-only +0.043, Holm p 0.0096. Alternatives (AUC minus image-only): {'cnv_only': -0.0682, 'coattention_fusion': 0.008, 'early_fusion': 0.0072, 'image_only': 0.0, 'intermediate_fusion': 0.0102, 'late_mean': 0.043, 'late_stack_logit': 0.0054}.
- **Current state:** selection-adjusted p = 0.25329 (best-of-5 arms null 95th pct 0.0788); out-of-bag gain of the selected arm +0.016 [-0.1063, 0.0799]. Winner's curse: late-mean wins 73% of re-selections, optimism +0.0272 AUPRC. **The fusion gain is not claimed; the honest effect is +0.016 AUC with a CI spanning zero.**

## 22. Performance by time point

- **late_mean:** progressor samples 0–12 m before the event vs all non-progressor samples AUROC 0.8445 (n_pos 54); 12–36 m 0.5556 (n_pos 29); >36 m 0.8098 (n_pos 24). Progression-within-k-years horizons: Progress_in_1 AUROC 0.816 (pos 11/707); Progress_in_2 AUROC 0.7193 (pos 35/707); Progress_in_3 AUROC 0.6711 (pos 64/707); Progress_in_4 AUROC 0.6577 (pos 86/707); Progress_in_5 AUROC 0.6525 (pos 95/707)
- **image_only:** progressor samples 0–12 m before the event vs all non-progressor samples AUROC 0.8297 (n_pos 54); 12–36 m 0.516 (n_pos 29); >36 m 0.8044 (n_pos 24). Progression-within-k-years horizons: Progress_in_1 AUROC 0.8306 (pos 11/707); Progress_in_2 AUROC 0.6864 (pos 35/707); Progress_in_3 AUROC 0.6444 (pos 64/707); Progress_in_4 AUROC 0.6327 (pos 86/707); Progress_in_5 AUROC 0.6246 (pos 95/707)
- **cnv_only:** progressor samples 0–12 m before the event vs all non-progressor samples AUROC 0.6403 (n_pos 54); 12–36 m 0.6163 (n_pos 29); >36 m 0.5766 (n_pos 24). Progression-within-k-years horizons: Progress_in_1 AUROC 0.6283 (pos 11/707); Progress_in_2 AUROC 0.7125 (pos 35/707); Progress_in_3 AUROC 0.6462 (pos 64/707); Progress_in_4 AUROC 0.6219 (pos 86/707); Progress_in_5 AUROC 0.6275 (pos 95/707)
- Longitudinal models (drift features, GRU) did not beat the last-sample snapshot (results/swg_trajectory.json); histology adds nothing over current-CNV persistence for predicting the next biopsy's CNV (results/swg_trajectory_baselines.json).

## 23. Interpretability outputs

- CNV: per-arm importances mapped to genes exist (`data/lgd2_cnv_feature_gene_annotation.csv`; TP53/EGFR/CCND1 arms).
- **Exists:** 5 attention overlays for the image-only ABMIL from the July hardening analysis (`chapter1_scientific_hardening_20260727/attention_overlays/`: cases AD0496, PR1_HIN_043, AHM1146, AD0425, PR1_ADH_069; 256 tiles each; top-10% attention share 0.11–0.45). The release stores 256-tile subsamples with level-2 coordinates and `model.pt` state-dicts for every family, so re-inference is cheap.
- **DONE 21 Sep — SWG same-slide, cross-model maps** (`feasibility/runs/swg_heatmaps/output/maps/`, 11 slides: the 5 prior cases + 3 top-scored progressors + 1 missed progressor + 2 false-positive non-progressors; each panel = tissue thumbnail, image-only attention, image-only per-tile risk, intermediate-fusion attention, CNV-conditioned co-attention, early-fusion per-tile risk). Tile-ranking agreement (mean Spearman over slides): image-only vs early-fusion **per-tile risk 0.903** (the two models see the same tiles as risky); attention image-only vs intermediate 0.613, vs co-attention 0.41; **attention vs per-tile risk 0.023** — attention weight and tile risk are unrelated, i.e. 'where the model looks' is not 'what the model calls dangerous', which is the argument for tile-level grade maps rather than attention maps. Caveat: the release holds only 256 tiles per slide, so maps are sparse.
- **Running (submitted 21 Sep):** (i) ERIN tile-level grade maps — six-class MIL trained under case-max and under section labels, then every tile scored individually (per-tile grade, expected grade on a 0–5 sliding scale, attention) on the same 12 held-out slides for both models (`scripts/task_erin_tilemaps.py`); (ii) SWG same-slide comparison across release families (image-only attention, co-attention CNV-conditioned attention, per-tile risk for early fusion) on the 5 existing cases plus additional progressors — being written.

## 24. What changed since the last lab presentation

- **Two audiences.** Markowetz lab: last update ~a year ago → everything in this dossier is new to them (the Barrett's fusion work AND ERIN/OCCAMS/TCGA/LLM-labelling, which did not exist then). Fitzgerald lab: last update **6 March 2026**, Barrett's chapter only. Changes since 6 March, from those slides to now:
| | 6 March 2026 (Fitzgerald slides) | Now (Sept 2026) |
|---|---|---|
| Cohort | 160 patients / 470 visits / 959 samples / 941 sWGS; grades NDBE 609, ID 74, LGD 155, HGD 84, IMC 36, OAC 1 | **Frozen strict pre-event release: 150 patients / 707 samples**; at-event and post-event rows removed; patient-level max grade NDBE 97 / IND 15 / LGD 38 |
| Tasks | Six tasks (ever-progress, at-risk 1–5 y, next-biopsy progression, next-biopsy grade, days-to-progression) | **One pre-registered primary: next biopsy is LGD2+**; horizons kept only as descriptive time-point analyses (item 22) |
| Validation | Repeated CV (5–50 folds), best model per task reported, no CIs | 5 patient-disjoint frozen folds, nested CV, **paired bootstrap CIs**, Holm family, permutation controls |
| Headline numbers | Ever-progress: MM early-mean AUC 0.844, image 0.823, CNV 0.737, MoE 0.853; next-biopsy progression MoE 0.880 (Exclude LGD/HGD/IMC) | Late-mean **0.774** [0.687–0.849], image 0.731, CNV 0.663 (patient level, strict pre-event). Lower because at-event rows and post-hoc model selection are gone |
| Fusion claim | 'Image performs well, CNV confirms, combination is better' | Naive gain +0.043 (Holm p 0.0096) **does not survive selection adjustment** (p 0.25; out-of-bag gain +0.016 [−0.106, +0.080]); winner's curse quantified (+0.027); **claim demoted** |
| Fusion architecture | Early fusion > attention fusion; Mixture-of-Experts routing | Late-mean > early/intermediate/co-attention/stack-logit in the release; MoE not carried into the frozen release |
| Encoders | UNI2 only | UNI2 vs GigaPath histology: only the Brier difference survives (encoder-conditional gain) |
| Longitudinal ('next step 2' in March) | Planned | **Done, negative**: drift features and GRU do not beat the last sample; histology adds nothing over CNV persistence for next-CNV prediction |
| Attention-guided patch selection ('next step 1') | Planned | Not pursued as such; attention analysis limited to the 8 interpreted LGD2+ cases; heat-maps not regenerated |
| Power | Not addressed | Power map: minimum detectable fusion gain 0.075–0.10 at n=150 |
| Operating points / calibration | Spec@Sen90, Sen@95 in tables; no calibration | Spec at sens 0.95/1.0 with NPV (item 19); Brier + calibration slope and reliability deciles (item 20) |
| Complementarity | Routing analysis (image early / CNV late) | Likelihood-ratio tests: CNV adds to histology (p 0.007) and vice versa (p 3e-5) — information is complementary even though discrimination gain is unproven |
| External validation | None | **ACE-B agreed** (item 25); ERIN↔SWG overlap audit found 36% shared patients, so ERIN is not an external cohort for SWG |
| Beyond Barrett's | — | OCCAMS/TCGA fusion (null), PORPOISE baseline, LLM report jury (7,149 reports, validated on TCGA), section-level labels, VLM, OAC response (null) |

## 25. ACE-B: what will be run and when

- **What ACE-B is (Rehan, 21 Sep 2026):** Dr Massimiliano di Pietro's cohort (he owns it; we collaborate to validate the SWG multimodal model). Per Leanne: **134 patients, 294 samples, sWGS at ~7× depth** (SWG is 0.4×), CNV complete or near-complete. Groups: **11 progressors** (NDBE/LGD → HGD/IMC), **93 non-progressors**, **30 prevalent HGD/IMC** at baseline. Blocks: 44 at the ECI (Nottingham blocks), 250 in the Cambridge Tissue Bank store in Wales (pre-2023). Histopathology did not exist — **slides are being scanned now** (Histopathology Core; ~£369 for the 44 ECI blocks, ~£2,094 for the 250 Wales blocks; .svs output; 2-week turnaround; magnification and full-QC options still to choose).
- Our May 2026 metadata match found 153 study cases / 111 patient codes in the Barrett's database (Seattle histology {'IM': 101, 'LGD': 12, 'HGD': 12, 'ID': 6, 'IMC': 3}) — these counts differ from Leanne's 134/294 and need reconciling once her sample list arrives.
- **Plan (validation only, no training):** (1) featurise the scanned H&E with the identical UNI2 pipeline (20×/224 px; ~48 s/slide ⇒ under 1 GPU-h for the ~36–46 minimum slides, ~4 GPU-h for all 294); (2) obtain CNV from Dr di Pietro and **re-derive the SWG CNV representation at matched resolution** — 7× reads must be down-sampled or re-binned to the 0.4×/50 kb pipeline, otherwise the CNV arm sees a depth shift; (3) apply the frozen SWG image-only, CNV-only and late-mean models zero-shot; report AUROC/AUPRC and specificity at the SWG-fixed sensitivity-0.95 threshold (item 19). Minimum imaging plan from the proposal: 11 progressors (pre-cancer time point) + 20–25 matched non-progressors + optionally 5–10 prevalent HGD/IMC ≈ 36–46 slides.
- **What 11 progressors can and cannot show:** with 11 positives and ~25–93 negatives the 95% CI on an AUROC near 0.75 is roughly ±0.15, so ACE-B can confirm that the model transfers (AUROC clearly above 0.5) but **cannot** decide whether fusion beats image-only (a 0.04 difference is far below detectability). The pre-registration should say so. Two further shifts to declare up front: scanner/format (Aperio .svs vs the SWG Hamamatsu .ndpi) and sequencing depth.
- **From the database scrape (num_aceb_db):** 125 of the 153 official cases resolve to a DB participant; 120 have endoscopy records (median 8), 123 have pathology reports (1,024 in total, 977 jury-graded). Anchored at trial entry: 16 prevalent HGD/cancer, 18 progressors (median 402.0 days to progression), 81 non-progressors with median 1925.0 days follow-up — so the DB can supply dates, grades and follow-up for the validation set even before Dr di Pietro's tables arrive; per-participant timeline in `feasibility/runs/num_aceb_db_v2/output/aceb_participant_timeline.csv` (cluster).
- **MISSING** — timing — depends on scanning completion and Dr di Pietro releasing the CNV; nothing else to compute until slides arrive.

# D. ERIN labelling (LLM jury)


## 26. Reports total, oesophageal subset, matched slide

- 7149 reports from 2537 patients; 2294 reports have any slide file and 2282 an H&E slide; the original one-slide-per-case imaging set covered 2279 cases.
- Oesophageal subset: slide-file organ metadata says {'(blank)': 5169, 'OESOPHAGUS': 5140, 'LYMPH NODE': 1099, 'STOMACH': 479, 'DUODENUM': 165, 'SOFT TIS NOT TUM/MAS/LIP/DEB': 131, 'COLORECTAL': 86, 'POLYP': 57, 'MISCELLANEOUS / UNSPECIFIED': 14, 'SOFT TIS TUMOR EXTENSIVE RES': 3, 'STOMACH-SUB/TOT RES FOR TUMOR': 1, 'OMENTUM': 1, 'SOFT TIS MASS BX SIMP EXCISION': 1, 'PERITONEUM': 1}; report specimen protocols {'OESOPHAGUS': 6654, 'OESOPHAGUS, PART/TOT RESECTION': 490, 'POLYP, STOMACH/SMALL INTESTINE': 1, 'ADIPOSE TISSUE': 1, 'DIVERTICULUM-OESOPHAGUS/SM INT': 1, 'STOMACH, BIOPSY': 1, 'LYMPH NODES, REGIONAL RESECT': 1}. An exact oesophagus-only report count needs the jury v3 `site` consensus (pending).

## 27. Jury composition

- Whole-report jury: 8 open-weight models via local ollama — ['deepseek-r1_14b', 'gemma3_12b', 'gemma3_27b', 'llama3.1_8b', 'mistral-small3.2', 'phi4_14b', 'qwen3_14b', 'qwen3_32b']. Prompt: one report per request, strict JSON, five-rung ladder NDBE<IND<LGD<HGD<CANCER. Aggregation: majority label; jury_frac ≥ 0.75 → train-eligible, else unsure held out; 78 hardest disagreements adjudicated by hand. Per-section jury (v2): 5 jurors, grade accepted with ≥3/5, section kept if seen by ≥max(3, n−2) jurors; v3 adds `site` and `specimen_type`.

## 28. Agreement

- Inter-model (full corpus, 6657 reports graded by all 8): mean pairwise agreement 0.9555 (range 0.8965–0.9866), Fleiss' kappa 0.9002, unanimous on 86.4% of reports. Leave-one-family-out flips ≤ 0.5% of labels.
- External human anchor: TCGA registry grade, two-tier agreement ESCA 0.971 (n=102), STAD 0.964 (335), KIRC 0.964 (477) vs majority baselines 0.64/0.60/0.56 (results/pancancer_hardening.json).
- **Pathologist-labelled ERIN subset: none exists.** The 78 adjudications were text re-reads by the research engineer, not a pathologist; 100-case hand-label key prepared, grading app live, no grades yet.

## 29. Label distribution produced by the jury

- Whole-report: {'NDBE': 5105, 'CANCER': 834, 'HGD': 404, 'LGD': 268, 'IND': 256} (train-eligible 6867; unsure 204; adjudicated 78).
- Per-section (7099 reports, sections per report median 2 (range 0–17, n=7099)): section worst-grade {'NORMAL_OTHER': 8101, 'IND': 478, 'NDBE': 7306, 'HGD': 888, 'CANCER': 1186, 'LGD': 732}; cancer subtypes {'ADENOCARCINOMA': 1131, 'SQUAMOUS': 139, 'OTHER_CANCER': 11, 'SIGNET_RING': 78, 'POST_NEOADJUVANT_TX_EFFECT': 14}. Slide level: {'NORMAL_OTHER': 685, 'NDBE': 589, 'LGD': 82, 'CANCER': 81, 'HGD': 66, 'IND': 35} vs case-max {'NDBE': 778, 'NORMAL_OTHER': 311, 'CANCER': 168, 'LGD': 116, 'HGD': 96, 'IND': 69} — 32.0% differ.

## 30. Fine-tuned MedGemma vs zero-shot

- **DONE 21 Sep (zero-shot, both sizes, via the ollama library — no Hugging Face gating needed).** Both MedGemma models graded all 7,149 ERIN reports with the identical whole-report prompt (`labeller/llm_grade_shard.py`, 8 shards × cuda/h200 twins; the 27B finished in under an hour).
- **MedGemma-27B (text):** parse rate 0.9965 (0 parse failures, 0 NA); label distribution {'NDBE': 5209, 'CANCER': 889, 'HGD': 420, 'IND': 285, 'LGD': 273}. Agreement with the 8-model jury on train-eligible reports (n=6804): exact 0.9974, binary NDBE/IND vs LGD+ 0.9993. Versus the human adjudications (cancer yes/no, n=79): accuracy 0.9873, sensitivity 1.0, specificity 0.9804. Disagrees with a near-unanimous jury (≥7/8) on 12/6621 reports; commonest patterns ['jury=HGD|medgemma=CANCER: 4', 'jury=NDBE|medgemma=IND: 3', 'jury=LGD|medgemma=HGD: 1']. Pairwise agreement with individual jurors {'deepseek-r1_14b': 0.9613, 'gemma3_12b': 0.9688, 'gemma3_27b': 0.973, 'llama3.1_8b': 0.8803, 'mistral-small3.2': 0.952, 'phi4_14b': 0.9726, 'qwen3_14b': 0.9733, 'qwen3_32b': 0.9635}.
- **MedGemma-4B:** parse rate 0.7458 (1789 parse failures, 0 NA); label distribution {'NDBE': 4049, 'CANCER': 385, 'HGD': 382, 'LGD': 264, 'IND': 216}. Agreement with the 8-model jury on train-eligible reports (n=5128): exact 0.9397, binary NDBE/IND vs LGD+ 0.9881. Versus the human adjudications (cancer yes/no, n=58): accuracy 0.8621, sensitivity 0.6, specificity 1.0. Disagrees with a near-unanimous jury (≥7/8) on 270/5053 reports; commonest patterns ['jury=CANCER|medgemma=HGD: 160', 'jury=NDBE|medgemma=LGD: 43', 'jury=NDBE|medgemma=IND: 43']. Pairwise agreement with individual jurors {'deepseek-r1_14b': 0.9228, 'gemma3_12b': 0.913, 'gemma3_27b': 0.9131, 'llama3.1_8b': 0.9075, 'mistral-small3.2': 0.8852, 'phi4_14b': 0.9154, 'qwen3_14b': 0.9213, 'qwen3_32b': 0.9101}.
- **Reading:** **MedGemma-27B is the best single juror we have tested**: 99.7% exact agreement with the 8-model consensus, 99.9% on the binary screening split, and on the 79 human-adjudicated cancer decisions it is 98.7% accurate with sensitivity 1.0 (it misses no cancer the adjudicators confirmed) and specificity 0.98. It disagrees with a near-unanimous jury on only 12 of 6,621 reports, and 4 of those are the jury saying HGD where MedGemma says CANCER — plausibly the *jury* under-calling. Its pairwise agreement with the strongest general jurors (qwen3-14B, phi4, gemma3-27B) is 0.97, i.e. the medical tuning buys agreement, not a different opinion. **MedGemma-4B is not usable as a juror**: a quarter of reports fail JSON parsing, and on the rest it systematically under-calls carcinoma as HGD (160 of its 270 confident-jury disagreements) with adjudicated-cancer sensitivity 0.60. Conclusion for Thursday: a medically-tuned 27B matches a general 8-model jury; it does not beat it, and the small general models beat the small medical one. Fine-tuning (LoRA on the 4B, ~3–4 GPU-h) remains optional and is not needed for this point.
- **Original plan/estimate (kept for the record).** MedGemma (Google, Gemma-3-based, medically tuned; 4B multimodal and 27B text-only instruction-tuned) is gated on Hugging Face: the API sees the repos but the download was refused ('not in the authorized list') — **the HF account behind the cluster token must accept the Health AI Developer Foundations terms**; not available in the ollama library either. Once access is granted: zero-shot 27B as a 9th juror with the identical JSON prompt over 7,149 reports ≈ 3–4 GPU-h on one H200 (weights 54 GB bf16), sharded 8 ways ≈ 1 h wall; 4B ≈ 1 GPU-h. Deliverable: agreement with the 8-model jury and with the 78 adjudications, added to items 27–28. LoRA fine-tune of the 4B on the 6,867 jury-labelled reports (held-out = the 78 adjudicated + a jury-labelled fold) ≈ 3–4 GPU-h more. Both fit before Thursday IF access is granted by Tuesday.

## 31. Throughput and cost

- GPU-hours by campaign (allocated GPUs × wall time, incl. race-twin duplicates): whole-report jury 31.8 GPU-h for 7,149 reports × 8 models (≈1798 report-gradings per GPU-h); per-section v2 19.8 GPU-h; v3 109.4 GPU-h (9 jurors). Hardware: L40S (cuda partition) and H200 (preemptible). CPU inference was abandoned: 13259.2 CPU-h produced parse failures only.

# E. ERIN image side


## 32. Slides with UNI2 features vs remaining; patches total

- 11781 feature files; 11654 of 11672 H&E slides done, 18 remaining (1189 logged failures). Total kept tissue patches **38,138,909**; per slide median 2226 (range 21–8000, n=11781); grid tiles per slide median 72960 (range 594–210504, n=9540). 224 px at 0.5 mpp (20x), UNI2-h 1536-d.

## 33. Task definition (per-section vs case-max)

- NDBE/IND/normal vs LGD+ (LGD, HGD, CANCER) on the slide's OWN section grade (truth) ; models trained on case-max vs section label. Six-class: NORMAL_OTHER<NDBE<IND<LGD<HGD<CANCER, same truth. The label under test is the *training* label (report worst grade vs the slide's own section grade); the evaluation truth is always the section grade.

## 34. Split, folds, metrics for both schemes

- 5-fold patient-disjoint, frozen (patient hash seed 0), 3 seeds averaged, 1,538 slides / 1,155 patients. CIs are patient-clustered bootstraps (2,000).
| scheme | AUROC [CI] | AUPRC [CI] | F1@0.5 | F1@Youden (sens/spec) | spec @ sens 0.95 | spec @ sens 1.0 |
|---|---|---|---|---|---|---|
| trained_on_case_labels | 0.8705 [0.8419, 0.8973] | 0.6238 [0.5555, 0.6894] | 0.5769 | 0.6385 (0.7598/0.8915) | 0.314 | 0.0351 |
| trained_on_slide_labels | 0.8604 [0.8291, 0.8886] | 0.6292 [0.559, 0.7027] | 0.6004 | 0.6018 (0.7293/0.8785) | 0.2949 | 0.0084 |

| scheme (6-class) | macro AUROC [CI] | macro AUPRC | macro F1 [CI] | balanced acc |
|---|---|---|---|---|
| trained_on_case_labels | 0.7639 [0.7409, 0.7866] | 0.3645 | 0.3455 [0.3182, 0.3745] | 0.3968 |
| trained_on_slide_labels | 0.7216 [0.6957, 0.7462] | 0.3296 | 0.3408 [0.3094, 0.3703] | 0.3407 |
- Paired deltas (slide-label-trained minus case-max-trained): binary AUROC -0.0102 [-0.0284, 0.0093]; six-class macro-AUROC -0.0423 [-0.066, -0.0193]; weighted kappa -0.0093 [-0.0655, 0.0467]. Case-max is no worse for binary and better for six-class at this n.

## 35. Cases with follow-up for a progression/outcome label

- 1459 patients have ≥2 reports; progression cohort v3 1266 patients / 181 progressors (report level); 2279 imaged cases give 153 index slides / 28 progressors at slide level. With all-slides features the slide-level cohort can be rebuilt from every imaged index case.

# F. OCCAMS


## 36. Patients behind the slides

- **Main OCCAMS tree:** 276 cases (one patient each) behind 635 featurised slides ({'RES': 322, 'OGD': 286, 'NOT-HE': 25, 'OTHER': 2}); 221 have a biopsy slide, 141 a resection slide, 86 both.
- **The '227' is the Hannah Coles batch: 221 .svs slides** scanned Mar–Jun 2026 (batches B8126 27+36, B8134 82+51, B8167 25), at `occams/wsi_data/occams_hannah_coles/`, **additional** to the 635 above and not yet featurised. 131 H&E + 90 IHC (HER2, MMR panel, p53, CK); all OGD staging biopsies per Will. Identifiers: 196 carry a PS (block) number, 16 an OCCAMS patient ID, 16 (B8167) neither. **Patients behind them: only 25 slides → 12 patients are resolvable** (OC-AH-001/003/005/596/609/610/611/613, OC-RS-007/027, OC-SH-051 + 1); the other 196 slides are unlinkable until Will supplies a PS→patient mapping (0 of the 78 PS numbers appear in his WGS-linked xlsx). Source: `hannah_coles_integration_summary.md` (28 Jul 2026) and your Slack thread with Will, 27 Jul.

## 37. The genomic values and coverage

- TP53 status (composite of ['TP53_SNV', 'TP53_indel', 'TP53_deletion', 'TP53_knockout']), ploidy, and whole-genome doubling; from WGS; 383 cases in the TSV, 141 with slides, complete for all of them. Among slide cases: WGD {'yes': 85, 'no': 56}, TP53-altered 117/141.

## 38. Treatment and outcome fields

- Neoadjuvant (slide cases): {'ECF/ECX/EOF/EOX': 118, 'CRT-CF/CX': 9, 'CF/CX/XELOX/FOLFOX/CAPOX': 8, 'FLOT': 3, 'CF/CX/XELOX/FOLFOX/CAPOX-lapatinib': 2, 'CRT-CROSS': 2, 'CRT-unknown': 1, 'CRT-CX': 1, 'Other-Singleagent': 1}; broad category {'Anthra-Plat-Fluoro': 117, 'CRT-Plat-Fluoro': 10, 'Plat-Fluoro': 8, 'Plat-Fluoro-Microtubule inh': 3, 'Plat-Fluoro-TKI': 2, 'CRT-Unknown': 1, 'CRT-Carbo-Taxol': 1, 'Plat-Taxol': 1, 'CRT-Plat-Taxol': 1, 'Other-Taxol': 1}. Adjuvant regimen recorded for 145.
- Outcomes: TRG {'4': 72, '3': 24, '5': 21, '1': 11, '2': 8} (n=136); tumour_response {'not_recorded': 51, 'greater_than_or_equals_to_50pc': 51, 'less_than_50pc': 16, '0pc_remaining': 10, 'greater_than_or_equals_to_20pc': 6, 'less_than_20pc': 3}; recurrence date 21/145; survival fields {'smoker_status': 139, 'diagnostic_tumour_grading_differentiation_status': 117, 'pre_treatment_performance_status': 130, 'resection_path_tumour_grading_differentiation_status': 133, 'vital_status': 145, 'date_death': 94, 'deceased_survival_days': 95, 'last_known_survival_days': 50}.

## 39. Trainable labels (≥ ~30 positives)

- Death: 58/87 ✔. TRG1–3 response: 41/131 ✔ (run: null, UNI2 AUC 0.5407 [0.4295, 0.6495]). TRG1–2: 18 ✘. Node-positive at resection (pN1–3): 85/145 ✔ (not yet modelled). WGD: 85/141 ✔ (probes at chance). Recurrence: 21 recorded ✘ (under-recorded).

# G. OGD staging


## 40. Slides, patients, stage/nodal labels, results

- **Reading of 'OGD staging' (Rehan: probably TNM staging):** predicting the cancer's stage from the pre-treatment endoscopic (OGD) biopsy slide. Two slide pools exist: (a) the 221 Hannah Coles OGD staging biopsies (item 36) — **stage labels reachable for only 12 patients** until the PS→patient mapping arrives; (b) the 140 OGD-biopsy cases in the main tree that have a clinical master row, which already carry TNM.
- **Stage labels on the 140 main-tree OGD cases** — clinical (pre-treatment) cT {'t3': 111, 't2': 21, 'tx': 4, 't4a': 2, 't4': 1, 't1b': 1}, cN {'n1': 63, 'n0': 43, 'n2': 26, 'n3': 7, 'nx': 1}, cM {'m0': 131, 'mx': 7, 'm1': 2}; approximate AJCC7 stage group {'IIIA': 55, 'IIA': 27, 'IIIB': 22, 'IB': 13, 'IIIC': 8, 'IIB': 7, 'unknown': 6, 'IV': 2}; **clinically node-positive 96/140**. Pathological (post-neoadjuvant resection) ypT {'t3': 76, 't2': 19, 't1b': 11, 't0': 11, 't4a': 10, 'tx': 6, 't1a': 4, 't4': 2, 't1': 1}, ypN {'n0': 51, 'n1': 40, 'n3': 23, 'n2': 19, 'nx': 7}; **node-positive at resection 82/140**; approximate stage group {'IIIA': 32, 'IIIC': 24, 'IIA': 17, 'IIIB': 14, 'IA': 12, 'IB': 11, '0': 10, 'unknown': 10, 'IIB': 7, 'IV': 2, 'II+': 1}. Differentiation grade at diagnosis {'moderate': 56, 'poor': 29, 'NaN': 26, 'unknown': 14, 'moderate_to_poor': 9, 'moderate_to_well': 4, 'well': 2}. *(num_occams_tnm; stage groups from T/N/M only)*
- **Trainability:** node-positive (cN1–3: 96 vs 43 cN0; ypN1–3: 82 vs 51) and cT3 vs cT1–2 (111 vs 22) both clear the ~30-positive bar; full stage-group classification does not (most groups < 30). **No staging model has been run.** Nearest existing result on the same slides: pre-treatment biopsy → TRG response, NULL (UNI2 AUC 0.54; results/oac_response.json, which is local/uncommitted at your request).
- **MISSING** — your confirmation that this reading is right; if so, a nodal-status (cN0 vs cN+) probe from the OGD biopsy is a one-script job on existing features.

# H. Cross-project


## 41. Shared code

- Tiling + feature extraction: `scripts/extract_one_hf.py` (all encoders, all cohorts) and `campaigns/allslides/extract_worker.py` (pull-worker variant). MIL trainers: `scripts/abmil_clf.py`, `scripts/abmil_cox.py` (gated attention, Cox/CE heads, `bootstrap_auc`/`bootstrap_c`, `patient_folds`). Fusion: late fusion by z-scored risk averaging inside each task script; SWG release fusion families live in the Barrett's project. Evaluation: paired bootstrap, Holm, selection-adjusted permutation (`task_swg_selection_adjusted.py`), clustered CIs (`task_clustered_cis.py`), power map (`task_power_map.py`). Job pattern: `feasibility/run_task.sh` race-to-run. LLM jury: `labeller/llm_grade_shard.py`, `llm_grade_sections*.py`.

## 42. Compute used per project

- Window 2026-08-14 to 2026-09-21: 32,011 jobs, **1,010.9 GPU-h**, 36,762.6 CPU-h (GPU-h = allocated GPUs × wall time; race-twin duplicates that exited early are included, so real work is somewhat lower).
| project | jobs | GPU-h | CPU-h |
|---|---|---|---|
| erin_extraction_other_encoders | 12097 | 495.7 | 3582.7 |
| erin_allslides_extraction | 2577 | 201.4 | 817.3 |
| llm_jury_sections_v3 | 212 | 109.4 | 728.6 |
| tcga_stad_extraction | 2342 | 56.6 | 452.8 |
| other_analysis_and_misc | 9757 | 41.0 | 11675.2 |
| erin_extraction_uni2_one_per_case | 4558 | 38.1 | 304.5 |
| llm_jury_whole_report | 141 | 31.8 | 270.5 |
| llm_jury_sections_v2 | 80 | 19.8 | 13259.2 |
| scifi_video_nonthesis | 6 | 7.0 | 84.3 |
| swg_barretts | 157 | 5.4 | 61.7 |
| llm_eoe_mdt_pheno | 34 | 3.4 | 5403.9 |
| occams_fusion_models | 20 | 0.7 | 53.7 |
| occams_extraction | 18 | 0.5 | 12.4 |
| vlm | 8 | 0.1 | 55.9 |
| llm_pancancer_tcga | 4 | 0.0 | 0.0 |
- Scaling rules of thumb: UNI2 extraction ≈ 48 s/slide on an L40S (all-ERIN 9,562 slides ≈ 130 GPU-h planned, 201.4 GPU-h used incl. twins); whole-report jury ≈ 31.8 GPU-h per 7k reports × 8 models; a 150-slide cohort like ACE-B is ~2 GPU-h to featurise and minutes to score.

# ERIN image + text fusion for progression — cohort report and feasibility stop (21 Sep 2026)

## Outcome in one line
The pre-registered experiment (`docs/erin_progression_fusion_preregistration.md`) stopped at the cohort stage: with the slides that exist, the 3-year progression label has **18 positives and 0 negatives**, because ERIN's scanned slides all come from 2022–2025 reports and almost no imaged index patient has three years of follow-up. No model was trained; nothing about Chapter 2's fusion story changes tonight.

## Cohort counts
| Stage | n | y3 = 1 (HGD/cancer ≤ 3 y) | y3 = 0 (≥ 3 y clean follow-up) | excluded (censored) | y_any = 1 |
|---|---|---|---|---|---|
| Index NDBE/IND patients, report level | 2,092 | 115 | 721 | 1,256 | 159 |
| …whose index case has H&E slides with UNI2 features | 632 | 18 | **0** | 614 | 18 |
| Analysis set at 3 years | 18 | 18 | 0 | — | — |

- Imaged index cases: 632 patients, 2,499 slides (median 2 per case, range 1–72; pooled per case). Index grade NDBE 611 / IND 21. Age present for all; sex not recorded anywhere we hold. Jury-v3 structured fields present for all 632. SWG-overlap patients: 1 (none among positives).
- Follow-up among imaged index cases: median **0 days**; 499 of 632 have no later report. Index years: 2022: 8, 2023: 261, 2024: 298, 2025: 65.
- Horizon sweep (imaged index cases, pos / neg): 180 d 9 / 69 · 1 y 18 / 30 · 1.5 y 18 / 11 · 2 y 18 / 2 · 3 y 18 / 0.
- Alternative index definitions do not help: v3 rule (LGD index allowed) 27 / 31 at 1 y and 27 / 0 at 3 y; earliest *imaged* NDBE/IND report as landmark 14 / 44 at 1 y and 14 / 0 at 3 y.
- The 18 "positives" progressed a median 180 days after index — these are patients whose dysplasia was found within months, i.e. largely prevalent disease, not the 3-year prediction target.

## Why: the imaging window
All 11,672 scanned H&E slides belong to reports from 2022 (59), 2023 (4,685), 2024 (5,765) and 2025 (1,163). The 3-year-defined index cases exist — 836 patients (115 progressors) at report level — but their index reports date from 2014–2022 and **none of those cases is scanned** (0 of 818 pre-2023 index cases; see `results/erin_progression_fusion/missing_slides_by_year.json`).

| Index year | y3-defined index cases | of which progressors | scanned |
|---|---|---|---|
| 2014 | 31 | 2 | 0 |
| 2015 | 177 | 9 | 0 |
| 2016 | 163 | 8 | 0 |
| 2017 | 105 | 14 | 0 |
| 2018 | 117 | 13 | 0 |
| 2019 | 101 | 12 | 0 |
| 2020 | 55 | 9 | 0 |
| 2021 | 50 | 12 | 0 |
| 2022 | 19 | 18 | 0 |
| 2023–24 | 18 | 18 | 18 |

## Exactly what is missing
Scanned H&E slides for the **index cases of 2014–2021 (818 cases, ~97 progressors, ~721 clean 3-year negatives)**. Their reports and labels are in hand; the blocks are in the hospital archive. A targeted retrieval — all 97 pre-2022 progressor index cases plus ~200 matched negatives (≈300 cases, ~2 slides each ≈ 600 slides; at the Histopathology Core's ~£10/slide for sectioning + H&E + scanning ≈ £6k, two weeks per batch) — would give a 3-year cohort of ~300 patients / ~97 positives, well above the 30-positive floor and about twice SWG's positive count. Without that, ERIN cannot support a future-progression model at any horizon; it remains a grading cohort.

## What the pre-registered rules say
Feasibility rule triggered (empty negative class). No arm was run, so no comparison is interpretable; the previously reported ERIN "progression" numbers (153 index slides / 28 progressors, AUROC 0.819 for histology, fusion null) used a censoring-ignorant any-time label on the 2022–2025 window and should be described as **detection of imminent dysplasia in a censored cohort**, not progression prediction.

## Decisions that were not pre-specified (for you to defend or change)
1. Index restricted to NDBE or IND (v3 also allowed LGD) — followed the task text.
2. Negative definition requires the *last report* ≥ 1,095 days after index (no HGD/cancer ever); a stricter alternative would require a clean report at ≥ 3 years.
3. The 18 positives with ≤ 3-year events were counted regardless of whether the event report itself is imaged.
4. Sex could not be included (not in ERIN or the DB export); age used alone with grade in arm a.
5. Text arm embedding model fixed to `nomic-embed-text` (the only embedding model cached offline).
6. Late fusion pre-specified with fold-local z-scoring (lesson of 2.46), not the SWG release's pooled z-scoring.

## Compute used
Cohort build only: ~4 CPU-minutes. GPU-hours: 0.

# Dataset description: frozen SWG release, Killcoyne-protocol set C, ACE-B manifest

Report only: nothing is fitted or retrained. All numbers are computed by `scripts/paper_plan/dd_describe.py` (commit c402740), run through Slurm (`scripts/cluster/campaign.sh`, prefixes dd1, dd2, dd3), and written as aggregates to `results/paper_final/dataset_description/{core,wsi_release,wsi_setc,swgs}.json`; this file is rendered by `scripts/paper_plan/dd_render.py`. Every row names its input file and the JSON key that holds the number. No row-level data are in this repository.

Path aliases (cluster):

- `[REL]` = `/mnt/scratche/slow/fmlab/zuberi01/phd/barretts_retraining/barretts_training/analysis/chapter1_lgd2_final_pre_event_20260713_final` (frozen release)
- `[BT]` = `/mnt/scratche/slow/fmlab/zuberi01/phd/barretts_retraining/barretts_training`
- `[SWG]` = `/mnt/scratche/fast/fmlab/datasets/imaging/SWGCohort`
- `[UNI]` = `/mnt/scratche/slow/fmlab/zuberi01/phd/barretts_retraining/data/foundation_outputs/uni2_tile224_lvl2`
- `[KC]` = `/mnt/scratche/slow/fmlab/zuberi01/phd/thesis/feasibility/paper_plan/killcoyne` (and `[KC]_mm`, set C)
- `[DB]` = `/mnt/scratche/slow/fmlab/zuberi01/barretts_db_export` (Barrett's database export)
- `[ACEB]` = `/mnt/scratche/slow/fmlab/zuberi01/phd/aceb_meta/ACEB_samples_for Rehan.csv`
- `[777]` = `[SWG]/sWGS_777_samples_cleaned_202401_Leanne_fullDetails (3) (1).csv`; `[268]` = `[SWG]/sWGS_validation_cleaned_Leanne (4) (1).csv`

Definitions used throughout:

- Release rows = the 707 strict pre-event rows of `[REL]/training_manifest.csv`, joined to `[REL]/pre_event_cohort.csv` (SampleID) and `[REL]/matched_manifest.csv` (biopsy_id, slide_id, cnv_id). Progressor = patient max of `training_manifest.y_progressor` (LGD2+ endpoint of the release).
- Sheet of a release sequencing sample: 777-sheet if its cnv_id is a `combined_name` in `[777]`, 268-sheet if it is in `[SWG]/copy_number_hg38/val/`; a patient takes the sheet of its samples (no patient is mixed).
- Set C = `[KC]_mm/set_C.csv`: the published Killcoyne samples with a UNI2 bag; progressor = sheet `Status` P.
- Statistics are over patients unless the row says samples or slides; IQR = 25th–75th percentile; n = patients (or samples/slides) with a value.

Status: items 1–4 DONE; item 5 DONE; item 6 DONE; item 7 PARTIAL (the manifest has coverage, batch and pool only; WSI, read length, build, bins and pipeline NOT AVAILABLE).

## 1. Patients

| Cohort | Sheet | Patients (n) | Progressors (n) | Non-progressors (n) | Source |
|---|---|---|---|---|---|
| release | both sheets | 150 | 50 | 100 | `[REL]/training_manifest.csv`, `[777]`, `[SWG]/copy_number_hg38/val/`; `core.json:item1.release` |
| release | 777-sheet | 82 | 40 | 42 | `[REL]/training_manifest.csv`, `[777]`, `[SWG]/copy_number_hg38/val/`; `core.json:item1.release` |
| release | 268-sheet | 68 | 10 | 58 | `[REL]/training_manifest.csv`, `[777]`, `[SWG]/copy_number_hg38/val/`; `core.json:item1.release` |
| set C | 777-sheet (all samples) | 80 | 37 | 43 | `[KC]_mm/set_C.csv` (Status); `core.json:item1.setC` |

Release samples by sheet: 777: 504, 268: 203 (n = 707; `core.json:item1.release_samples_by_sheet`). The sheet assignment agrees with `feasibility/paper_plan/f2_strata.csv` for 150 of 150 patients; matching on patient ID instead would give 777: 76, 268: 67, both: 5, none: 2. The master column `Progressor_label` gives 35 progressors of 150 (the 35 in `[REL]/table1_cohort.json`); the release label used by the models is `y_progressor` (50). All 676 of 676 set C samples are 777-sheet rows; 73 of the 80 set C patients also have release rows.

## 2. Timepoints per patient

| Cohort | Unit | Sheet | Label | Patients (n) | Mean | Median | IQR | Range | Patients with one | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| release | release rows (slide + sWGS pairs) | both sheets | all | 150 | 4.7 | 3.0 | 2.0–7.0 | 1.0–19.0 | 26 | `[REL]/matched_manifest.csv`; `core.json:item2.release.rows` |
| release | release rows (slide + sWGS pairs) | both sheets | progressors | 50 | 4.0 | 3.0 | 2.0–5.0 | 1.0–13.0 | 9 | `[REL]/matched_manifest.csv`; `core.json:item2.release.rows` |
| release | release rows (slide + sWGS pairs) | both sheets | non-progressors | 100 | 5.1 | 4.0 | 2.0–7.2 | 1.0–19.0 | 17 | `[REL]/matched_manifest.csv`; `core.json:item2.release.rows` |
| release | release rows (slide + sWGS pairs) | 777-sheet | all | 82 | 6.1 | 5.0 | 2.0–8.8 | 1.0–19.0 | 9 | `[REL]/matched_manifest.csv`; `core.json:item2.release.rows` |
| release | release rows (slide + sWGS pairs) | 777-sheet | progressors | 40 | 3.9 | 3.0 | 2.0–5.0 | 1.0–13.0 | 8 | `[REL]/matched_manifest.csv`; `core.json:item2.release.rows` |
| release | release rows (slide + sWGS pairs) | 777-sheet | non-progressors | 42 | 8.3 | 8.0 | 4.2–12.0 | 1.0–19.0 | 1 | `[REL]/matched_manifest.csv`; `core.json:item2.release.rows` |
| release | release rows (slide + sWGS pairs) | 268-sheet | all | 68 | 3.0 | 3.0 | 1.8–4.0 | 1.0–11.0 | 17 | `[REL]/matched_manifest.csv`; `core.json:item2.release.rows` |
| release | release rows (slide + sWGS pairs) | 268-sheet | progressors | 10 | 4.5 | 3.0 | 2.2–5.8 | 1.0–11.0 | 1 | `[REL]/matched_manifest.csv`; `core.json:item2.release.rows` |
| release | release rows (slide + sWGS pairs) | 268-sheet | non-progressors | 58 | 2.7 | 2.5 | 1.0–4.0 | 1.0–8.0 | 16 | `[REL]/matched_manifest.csv`; `core.json:item2.release.rows` |
| release | distinct biopsies | both sheets | all | 150 | 2.4 | 2.0 | 1.0–3.0 | 1.0–8.0 | 72 | `[REL]/matched_manifest.csv`; `core.json:item2.release.biopsies` |
| release | distinct biopsies | both sheets | progressors | 50 | 2.3 | 2.0 | 1.0–3.0 | 1.0–6.0 | 16 | `[REL]/matched_manifest.csv`; `core.json:item2.release.biopsies` |
| release | distinct biopsies | both sheets | non-progressors | 100 | 2.4 | 1.0 | 1.0–4.0 | 1.0–8.0 | 56 | `[REL]/matched_manifest.csv`; `core.json:item2.release.biopsies` |
| release | distinct biopsies | 777-sheet | all | 82 | 3.4 | 3.0 | 2.0–5.0 | 1.0–8.0 | 14 | `[REL]/matched_manifest.csv`; `core.json:item2.release.biopsies` |
| release | distinct biopsies | 777-sheet | progressors | 40 | 2.4 | 2.0 | 1.0–3.0 | 1.0–6.0 | 11 | `[REL]/matched_manifest.csv`; `core.json:item2.release.biopsies` |
| release | distinct biopsies | 777-sheet | non-progressors | 42 | 4.3 | 4.0 | 3.0–5.8 | 1.0–8.0 | 3 | `[REL]/matched_manifest.csv`; `core.json:item2.release.biopsies` |
| release | distinct biopsies | 268-sheet | all | 68 | 1.2 | 1.0 | 1.0–1.0 | 1.0–4.0 | 58 | `[REL]/matched_manifest.csv`; `core.json:item2.release.biopsies` |
| release | distinct biopsies | 268-sheet | progressors | 10 | 2.0 | 1.5 | 1.0–3.0 | 1.0–4.0 | 5 | `[REL]/matched_manifest.csv`; `core.json:item2.release.biopsies` |
| release | distinct biopsies | 268-sheet | non-progressors | 58 | 1.1 | 1.0 | 1.0–1.0 | 1.0–3.0 | 53 | `[REL]/matched_manifest.csv`; `core.json:item2.release.biopsies` |
| release | distinct slides | both sheets | all | 150 | 4.7 | 3.0 | 2.0–7.0 | 1.0–19.0 | 26 | `[REL]/matched_manifest.csv`; `core.json:item2.release.slides` |
| release | distinct slides | both sheets | progressors | 50 | 4.0 | 3.0 | 2.0–5.0 | 1.0–13.0 | 9 | `[REL]/matched_manifest.csv`; `core.json:item2.release.slides` |
| release | distinct slides | both sheets | non-progressors | 100 | 5.1 | 4.0 | 2.0–7.2 | 1.0–19.0 | 17 | `[REL]/matched_manifest.csv`; `core.json:item2.release.slides` |
| release | distinct slides | 777-sheet | all | 82 | 6.1 | 5.0 | 2.0–8.8 | 1.0–19.0 | 9 | `[REL]/matched_manifest.csv`; `core.json:item2.release.slides` |
| release | distinct slides | 777-sheet | progressors | 40 | 3.9 | 3.0 | 2.0–5.0 | 1.0–13.0 | 8 | `[REL]/matched_manifest.csv`; `core.json:item2.release.slides` |
| release | distinct slides | 777-sheet | non-progressors | 42 | 8.3 | 8.0 | 4.2–12.0 | 1.0–19.0 | 1 | `[REL]/matched_manifest.csv`; `core.json:item2.release.slides` |
| release | distinct slides | 268-sheet | all | 68 | 3.0 | 3.0 | 1.8–4.0 | 1.0–11.0 | 17 | `[REL]/matched_manifest.csv`; `core.json:item2.release.slides` |
| release | distinct slides | 268-sheet | progressors | 10 | 4.5 | 3.0 | 2.2–5.8 | 1.0–11.0 | 1 | `[REL]/matched_manifest.csv`; `core.json:item2.release.slides` |
| release | distinct slides | 268-sheet | non-progressors | 58 | 2.7 | 2.5 | 1.0–4.0 | 1.0–8.0 | 16 | `[REL]/matched_manifest.csv`; `core.json:item2.release.slides` |
| release | distinct sWGS profiles | both sheets | all | 150 | 4.6 | 3.0 | 2.0–7.0 | 1.0–19.0 | 26 | `[REL]/matched_manifest.csv`; `core.json:item2.release.swgs` |
| release | distinct sWGS profiles | both sheets | progressors | 50 | 3.9 | 3.0 | 2.0–5.0 | 1.0–12.0 | 9 | `[REL]/matched_manifest.csv`; `core.json:item2.release.swgs` |
| release | distinct sWGS profiles | both sheets | non-progressors | 100 | 5.0 | 3.5 | 2.0–7.0 | 1.0–19.0 | 17 | `[REL]/matched_manifest.csv`; `core.json:item2.release.swgs` |
| release | distinct sWGS profiles | 777-sheet | all | 82 | 6.0 | 5.0 | 2.0–8.8 | 1.0–19.0 | 9 | `[REL]/matched_manifest.csv`; `core.json:item2.release.swgs` |
| release | distinct sWGS profiles | 777-sheet | progressors | 40 | 3.8 | 3.0 | 2.0–5.0 | 1.0–12.0 | 8 | `[REL]/matched_manifest.csv`; `core.json:item2.release.swgs` |
| release | distinct sWGS profiles | 777-sheet | non-progressors | 42 | 8.1 | 8.0 | 4.2–11.0 | 1.0–19.0 | 1 | `[REL]/matched_manifest.csv`; `core.json:item2.release.swgs` |
| release | distinct sWGS profiles | 268-sheet | all | 68 | 2.9 | 3.0 | 1.8–4.0 | 1.0–11.0 | 17 | `[REL]/matched_manifest.csv`; `core.json:item2.release.swgs` |
| release | distinct sWGS profiles | 268-sheet | progressors | 10 | 4.5 | 3.0 | 2.2–5.8 | 1.0–11.0 | 1 | `[REL]/matched_manifest.csv`; `core.json:item2.release.swgs` |
| release | distinct sWGS profiles | 268-sheet | non-progressors | 58 | 2.7 | 2.5 | 1.0–3.8 | 1.0–8.0 | 16 | `[REL]/matched_manifest.csv`; `core.json:item2.release.swgs` |
| set C | sWGS samples | 777-sheet | all | 80 | 8.4 | 7.5 | 5.0–11.0 | 1.0–30.0 | 3 | `[KC]_mm/set_C.csv`; `core.json:item2.setC.swgs` |
| set C | sWGS samples | 777-sheet | progressors | 37 | 7.2 | 6.0 | 3.0–10.0 | 1.0–20.0 | 3 | `[KC]_mm/set_C.csv`; `core.json:item2.setC.swgs` |
| set C | sWGS samples | 777-sheet | non-progressors | 43 | 9.5 | 8.0 | 7.0–12.0 | 4.0–30.0 | 0 | `[KC]_mm/set_C.csv`; `core.json:item2.setC.swgs` |
| set C | distinct slides | 777-sheet | all | 80 | 8.5 | 8.0 | 5.0–11.2 | 1.0–30.0 | 3 | `[KC]/uni2_npz_map.csv`; `core.json:item2.setC.slides` |
| set C | distinct slides | 777-sheet | progressors | 37 | 7.3 | 6.0 | 3.0–10.0 | 1.0–20.0 | 3 | `[KC]/uni2_npz_map.csv`; `core.json:item2.setC.slides` |
| set C | distinct slides | 777-sheet | non-progressors | 43 | 9.6 | 8.0 | 7.0–12.0 | 4.0–30.0 | 0 | `[KC]/uni2_npz_map.csv`; `core.json:item2.setC.slides` |

In the release each row is one slide paired with one sWGS profile; 707 rows hold 707 distinct slides and 693 distinct sWGS profiles (`[REL]/feature_views/feature_view_metadata.json`). The field `biopsies_per_patient` of `[REL]/table1_cohort.json` (median 3, IQR 2–7, range 1–19) counts rows, not distinct biopsies.

## 3. Follow-up (years)

| Cohort | Measure | Sheet | Label | Patients (n) | Mean | Median | IQR | Source |
|---|---|---|---|---|---|---|---|---|
| release | first to last sample | both sheets | all | 150 | 2.67 | 0.82 | 0.00–4.24 | `[REL]/pre_event_cohort.csv` (Date); `core.json:item3.release.first_to_last` |
| release | first to last sample | both sheets | progressors | 50 | 2.73 | 2.03 | 0.00–4.14 | `[REL]/pre_event_cohort.csv` (Date); `core.json:item3.release.first_to_last` |
| release | first to last sample | both sheets | non-progressors | 100 | 2.65 | 0.00 | 0.00–4.39 | `[REL]/pre_event_cohort.csv` (Date); `core.json:item3.release.first_to_last` |
| release | first to last sample | 777-sheet | all | 82 | 4.25 | 3.49 | 1.01–6.87 | `[REL]/pre_event_cohort.csv` (Date); `core.json:item3.release.first_to_last` |
| release | first to last sample | 777-sheet | progressors | 40 | 2.84 | 2.04 | 0.00–4.18 | `[REL]/pre_event_cohort.csv` (Date); `core.json:item3.release.first_to_last` |
| release | first to last sample | 777-sheet | non-progressors | 42 | 5.59 | 4.83 | 2.63–7.81 | `[REL]/pre_event_cohort.csv` (Date); `core.json:item3.release.first_to_last` |
| release | first to last sample | 268-sheet | all | 68 | 0.77 | 0.00 | 0.00–0.00 | `[REL]/pre_event_cohort.csv` (Date); `core.json:item3.release.first_to_last` |
| release | first to last sample | 268-sheet | progressors | 10 | 2.26 | 1.02 | 0.00–2.54 | `[REL]/pre_event_cohort.csv` (Date); `core.json:item3.release.first_to_last` |
| release | first to last sample | 268-sheet | non-progressors | 58 | 0.51 | 0.00 | 0.00–0.00 | `[REL]/pre_event_cohort.csv` (Date); `core.json:item3.release.first_to_last` |
| release | first sample to endpoint | both sheets | progressors | 50 | 4.05 | 3.00 | 1.48–5.70 | `[REL]/pre_event_cohort.csv` (Date, is_lgd2_event_at_current, NextBiopsyDate, NextBiopsyProgression_LGD2plus); `core.json:item3.release.first_to_endpoint` |
| release | first sample to endpoint | 777-sheet | progressors | 40 | 4.03 | 2.91 | 1.20–6.05 | `[REL]/pre_event_cohort.csv` (Date, is_lgd2_event_at_current, NextBiopsyDate, NextBiopsyProgression_LGD2plus); `core.json:item3.release.first_to_endpoint` |
| release | first sample to endpoint | 268-sheet | progressors | 10 | 4.15 | 3.19 | 2.45–4.69 | `[REL]/pre_event_cohort.csv` (Date, is_lgd2_event_at_current, NextBiopsyDate, NextBiopsyProgression_LGD2plus); `core.json:item3.release.first_to_endpoint` |
| set C | first to last sample | 777-sheet | all | 80 | 5.59 | 5.25 | 3.50–7.25 | `[777]` (Months before final), `[KC]/kr_samples.csv` (Pathology); `core.json:item3.setC.first_to_last` |
| set C | first to last sample | 777-sheet | progressors | 37 | 4.37 | 4.00 | 1.00–6.00 | `[777]` (Months before final), `[KC]/kr_samples.csv` (Pathology); `core.json:item3.setC.first_to_last` |
| set C | first to last sample | 777-sheet | non-progressors | 43 | 6.65 | 6.00 | 4.25–8.00 | `[777]` (Months before final), `[KC]/kr_samples.csv` (Pathology); `core.json:item3.setC.first_to_last` |
| set C | first sample to endpoint | 777-sheet | progressors | 37 | 4.62 | 4.00 | 1.50–6.00 | `[777]` (Months before final), `[KC]/kr_samples.csv` (Pathology); `core.json:item3.setC.first_to_endpoint` |

Release: sample dates are `pre_event_cohort.Date` for the release rows (707 of 707 dated). The endpoint date is the earliest of the date of a row flagged `is_lgd2_event_at_current` and the `NextBiopsyDate` of a row with `NextBiopsyProgression_LGD2plus` = 1, over all 959 cohort rows of the patient; available for 50 of 50 progressors. Set C: times are differences of the sheet's `Months before final` (676 of 676 samples have it) divided by 12. The endpoint is the first HGD/IMC sample of the patient among the published samples (`kr_samples.csv` Pathology or sheet `Path_class_per_OGD`), as in `scripts/paper_plan/kc_merge.py:31-32`, for 33 progressors; for the other 4 the final endoscopy (same fallback). 1 progressor has its endpoint before its first set C sample (negative time; set C contains post-event samples).

## 4. Demographics at first sample

Release-only = the cohort's demographic sheet `[SWG]/Demographics_full.csv` (Study Number or Alternate Study Number = release patient ID); the release itself carries no demographic columns. Database-completed = release-only value, else the Barrett's database through `pre_event_cohort.participant_id`: date of birth from `[DB]/initial_history.parquet`; Prague C/M from `[DB]/endoscopy.parquet` (`barretts_circumference`, `barretts_maximum`, the endoscopy closest in date to the first sample), else `initial_history` `praguec`/`praguem`. The database has no sex field outside the OCCAMS tables. Its smoking field is coded 0/1/2/3 with no codebook in the export, so it cannot be merged with the Y/N sheet; the codes are listed for the patients the sheet lacks. Baseline grade = grade of the patient's first release row (`pre_event_cohort.Label`: 0 NDBE, 1 IND, 2 LGD); for set C, the `Pathology` of the earliest set C sample.

| Cohort | Label | Variable | Version | n available / N | Summary | Source |
|---|---|---|---|---|---|---|
| release | all | age at first sample (years) | release-only | 82 / 150 | mean 62.56; median 63.59 [56.68–69.89]; range 37.86–82.50 | `Demographics_full.csv` (Date of birth / Circumference / Maximal), `pre_event_cohort.Date`; `core.json:item4.release.all.age_release` |
| release | all | age at first sample (years) | database-completed | 113 / 150 | mean 62.67; median 63.96 [56.55–70.69]; range 25.17–82.50 | by source: demographics: 82, initial_history: 31; `Demographics_full.csv`, `[DB]/initial_history.parquet`, `[DB]/endoscopy.parquet`; `core.json:item4.release.all.age_completed` |
| release | all | Prague C (cm) | release-only | 66 / 150 | mean 1.32; median 0.00 [0.00–2.00]; range 0.00–11.00 | `Demographics_full.csv` (Date of birth / Circumference / Maximal), `pre_event_cohort.Date`; `core.json:item4.release.all.C_release` |
| release | all | Prague C (cm) | database-completed | 121 / 150 | mean 2.01; median 0.00 [0.00–4.00]; range 0.00–11.00 | by source: demographics: 66, endoscopy: 39, initial_history: 16; endoscopy-to-first-sample gap median 2,807 days (range 839–6,341); `Demographics_full.csv`, `[DB]/initial_history.parquet`, `[DB]/endoscopy.parquet`; `core.json:item4.release.all.C_completed` |
| release | all | Prague M (cm) | release-only | 69 / 150 | mean 4.62; median 4.00 [3.00–5.00]; range 1.00–13.00 | `Demographics_full.csv` (Date of birth / Circumference / Maximal), `pre_event_cohort.Date`; `core.json:item4.release.all.M_release` |
| release | all | Prague M (cm) | database-completed | 122 / 150 | mean 4.73; median 4.50 [3.00–7.00]; range 0.00–13.00 | by source: demographics: 69, endoscopy: 39, initial_history: 14; `Demographics_full.csv`, `[DB]/initial_history.parquet`, `[DB]/endoscopy.parquet`; `core.json:item4.release.all.M_completed` |
| release | all | sex | release-only (database: NOT AVAILABLE) | 82 / 150 | M: 64, F: 18 | `Demographics_full.csv` (Sex); `core.json:item4.release.all.sex_release` |
| release | all | smoking | release-only | 44 / 150 | Y: 33, N: 11 | `Demographics_full.csv` (Smoking Status); `core.json:item4.release.all.smoking_release` |
| release | all | smoking | database code, patients missing above (not harmonised) | 94 / 106 | code 0: 85, code 2: 7, code 3: 1, code 1: 1 | `[DB]/initial_history.parquet` (smoking); `core.json:item4.release.all.smoking_db_raw_codes_for_missing` |
| release | all | baseline grade | release | 150 / 150 | NDBE: 121, LGD: 16, IND: 13 | `[REL]/pre_event_cohort.csv` (Label, Date); `core.json:item4.release.all.baseline_grade` |
| release | progressors | age at first sample (years) | release-only | 40 / 50 | mean 64.00; median 64.69 [57.08–70.53]; range 39.36–82.50 | `Demographics_full.csv` (Date of birth / Circumference / Maximal), `pre_event_cohort.Date`; `core.json:item4.release.P.age_release` |
| release | progressors | age at first sample (years) | database-completed | 40 / 50 | mean 64.00; median 64.69 [57.08–70.53]; range 39.36–82.50 | by source: demographics: 40; `Demographics_full.csv`, `[DB]/initial_history.parquet`, `[DB]/endoscopy.parquet`; `core.json:item4.release.P.age_completed` |
| release | progressors | Prague C (cm) | release-only | 28 / 50 | mean 1.54; median 0.00 [0.00–2.00]; range 0.00–11.00 | `Demographics_full.csv` (Date of birth / Circumference / Maximal), `pre_event_cohort.Date`; `core.json:item4.release.P.C_release` |
| release | progressors | Prague C (cm) | database-completed | 40 / 50 | mean 1.48; median 0.00 [0.00–2.00]; range 0.00–11.00 | by source: demographics: 28, endoscopy: 10, initial_history: 2; endoscopy-to-first-sample gap median 1,827 days (range 839–5,370); `Demographics_full.csv`, `[DB]/initial_history.parquet`, `[DB]/endoscopy.parquet`; `core.json:item4.release.P.C_completed` |
| release | progressors | Prague M (cm) | release-only | 31 / 50 | mean 4.58; median 4.00 [2.50–5.00]; range 1.00–13.00 | `Demographics_full.csv` (Date of birth / Circumference / Maximal), `pre_event_cohort.Date`; `core.json:item4.release.P.M_release` |
| release | progressors | Prague M (cm) | database-completed | 41 / 50 | mean 4.34; median 4.00 [2.00–5.00]; range 0.00–13.00 | by source: demographics: 31, endoscopy: 10; `Demographics_full.csv`, `[DB]/initial_history.parquet`, `[DB]/endoscopy.parquet`; `core.json:item4.release.P.M_completed` |
| release | progressors | sex | release-only (database: NOT AVAILABLE) | 40 / 50 | M: 33, F: 7 | `Demographics_full.csv` (Sex); `core.json:item4.release.P.sex_release` |
| release | progressors | smoking | release-only | 21 / 50 | Y: 18, N: 3 | `Demographics_full.csv` (Smoking Status); `core.json:item4.release.P.smoking_release` |
| release | progressors | smoking | database code, patients missing above (not harmonised) | 26 / 29 | code 0: 26 | `[DB]/initial_history.parquet` (smoking); `core.json:item4.release.P.smoking_db_raw_codes_for_missing` |
| release | progressors | baseline grade | release | 50 / 50 | NDBE: 33, LGD: 11, IND: 6 | `[REL]/pre_event_cohort.csv` (Label, Date); `core.json:item4.release.P.baseline_grade` |
| release | non-progressors | age at first sample (years) | release-only | 42 / 100 | mean 61.18; median 62.52 [55.71–69.05]; range 37.86–77.36 | `Demographics_full.csv` (Date of birth / Circumference / Maximal), `pre_event_cohort.Date`; `core.json:item4.release.NP.age_release` |
| release | non-progressors | age at first sample (years) | database-completed | 73 / 100 | mean 61.94; median 63.22 [55.78–70.69]; range 25.17–81.94 | by source: demographics: 42, initial_history: 31; `Demographics_full.csv`, `[DB]/initial_history.parquet`, `[DB]/endoscopy.parquet`; `core.json:item4.release.NP.age_completed` |
| release | non-progressors | Prague C (cm) | release-only | 38 / 100 | mean 1.16; median 0.00 [0.00–1.75]; range 0.00–8.00 | `Demographics_full.csv` (Date of birth / Circumference / Maximal), `pre_event_cohort.Date`; `core.json:item4.release.NP.C_release` |
| release | non-progressors | Prague C (cm) | database-completed | 81 / 100 | mean 2.27; median 1.00 [0.00–5.00]; range 0.00–10.00 | by source: demographics: 38, endoscopy: 29, initial_history: 14; endoscopy-to-first-sample gap median 3,220 days (range 1,116–6,341); `Demographics_full.csv`, `[DB]/initial_history.parquet`, `[DB]/endoscopy.parquet`; `core.json:item4.release.NP.C_completed` |
| release | non-progressors | Prague M (cm) | release-only | 38 / 100 | mean 4.66; median 4.50 [3.00–5.75]; range 1.00–10.00 | `Demographics_full.csv` (Date of birth / Circumference / Maximal), `pre_event_cohort.Date`; `core.json:item4.release.NP.M_release` |
| release | non-progressors | Prague M (cm) | database-completed | 81 / 100 | mean 4.93; median 5.00 [3.00–7.00]; range 0.00–11.00 | by source: demographics: 38, endoscopy: 29, initial_history: 14; `Demographics_full.csv`, `[DB]/initial_history.parquet`, `[DB]/endoscopy.parquet`; `core.json:item4.release.NP.M_completed` |
| release | non-progressors | sex | release-only (database: NOT AVAILABLE) | 42 / 100 | M: 31, F: 11 | `Demographics_full.csv` (Sex); `core.json:item4.release.NP.sex_release` |
| release | non-progressors | smoking | release-only | 23 / 100 | Y: 15, N: 8 | `Demographics_full.csv` (Smoking Status); `core.json:item4.release.NP.smoking_release` |
| release | non-progressors | smoking | database code, patients missing above (not harmonised) | 68 / 77 | code 0: 59, code 2: 7, code 3: 1, code 1: 1 | `[DB]/initial_history.parquet` (smoking); `core.json:item4.release.NP.smoking_db_raw_codes_for_missing` |
| release | non-progressors | baseline grade | release | 100 / 100 | NDBE: 88, IND: 7, LGD: 5 | `[REL]/pre_event_cohort.csv` (Label, Date); `core.json:item4.release.NP.baseline_grade` |
| set C | all | age at first sample (years) | release-only | 80 / 80 | mean 62.46; median 63.42 [57.20–69.45]; range 37.86–82.55 | `Demographics_full.csv` (Date of birth / Circumference / Maximal), `pre_event_cohort.Date`; `core.json:item4.setC.all.age_release` |
| set C | all | age at first sample (years) | database-completed | 80 / 80 | mean 62.46; median 63.42 [57.20–69.45]; range 37.86–82.55 | by source: demographics: 80; `Demographics_full.csv`, `[DB]/initial_history.parquet`, `[DB]/endoscopy.parquet`; `core.json:item4.setC.all.age_completed` |
| set C | all | Prague C (cm) | release-only | 64 / 80 | mean 1.28; median 0.00 [0.00–2.00]; range 0.00–11.00 | `Demographics_full.csv` (Date of birth / Circumference / Maximal), `pre_event_cohort.Date`; `core.json:item4.setC.all.C_release` |
| set C | all | Prague C (cm) | database-completed | 71 / 80 | mean 1.39; median 0.00 [0.00–2.00]; range 0.00–11.00 | by source: demographics: 64, endoscopy: 4, initial_history: 3; endoscopy-to-first-sample gap median 1,728 days (range 1,165–2,545); `Demographics_full.csv`, `[DB]/initial_history.parquet`, `[DB]/endoscopy.parquet`; `core.json:item4.setC.all.C_completed` |
| set C | all | Prague M (cm) | release-only | 67 / 80 | mean 4.73; median 4.00 [3.00–6.00]; range 1.00–13.00 | `Demographics_full.csv` (Date of birth / Circumference / Maximal), `pre_event_cohort.Date`; `core.json:item4.setC.all.M_release` |
| set C | all | Prague M (cm) | database-completed | 72 / 80 | mean 4.75; median 4.00 [3.00–6.00]; range 1.00–13.00 | by source: demographics: 67, endoscopy: 4, initial_history: 1; `Demographics_full.csv`, `[DB]/initial_history.parquet`, `[DB]/endoscopy.parquet`; `core.json:item4.setC.all.M_completed` |
| set C | all | sex | release-only (database: NOT AVAILABLE) | 80 / 80 | M: 61, F: 19 | `Demographics_full.csv` (Sex); `core.json:item4.setC.all.sex_release` |
| set C | all | smoking | release-only | 43 / 80 | Y: 33, N: 10 | `Demographics_full.csv` (Smoking Status); `core.json:item4.setC.all.smoking_release` |
| set C | all | smoking | database code, patients missing above (not harmonised) | 27 / 37 | code 0: 24, code 2: 2, code 3: 1 | `[DB]/initial_history.parquet` (smoking); `core.json:item4.setC.all.smoking_db_raw_codes_for_missing` |
| set C | all | baseline grade | release | 80 / 80 | NDBE: 55, LGD: 12, ID: 11, HGD: 2 | `[KC]_mm/set_C.csv` (Pathology), `[777]` (Months before final); `core.json:item4.setC.all.baseline_grade` |
| set C | progressors | age at first sample (years) | release-only | 37 / 37 | mean 63.14; median 61.23 [56.55–69.22]; range 42.23–82.55 | `Demographics_full.csv` (Date of birth / Circumference / Maximal), `pre_event_cohort.Date`; `core.json:item4.setC.P.age_release` |
| set C | progressors | age at first sample (years) | database-completed | 37 / 37 | mean 63.14; median 61.23 [56.55–69.22]; range 42.23–82.55 | by source: demographics: 37; `Demographics_full.csv`, `[DB]/initial_history.parquet`, `[DB]/endoscopy.parquet`; `core.json:item4.setC.P.age_completed` |
| set C | progressors | Prague C (cm) | release-only | 24 / 37 | mean 1.29; median 0.00 [0.00–1.25]; range 0.00–9.00 | `Demographics_full.csv` (Date of birth / Circumference / Maximal), `pre_event_cohort.Date`; `core.json:item4.setC.P.C_release` |
| set C | progressors | Prague C (cm) | database-completed | 28 / 37 | mean 1.39; median 0.00 [0.00–1.25]; range 0.00–9.00 | by source: demographics: 24, initial_history: 3, endoscopy: 1; endoscopy-to-first-sample gap median 2,545 days (range 2,545–2,545); `Demographics_full.csv`, `[DB]/initial_history.parquet`, `[DB]/endoscopy.parquet`; `core.json:item4.setC.P.C_completed` |
| set C | progressors | Prague M (cm) | release-only | 27 / 37 | mean 4.74; median 4.00 [3.00–6.50]; range 1.00–10.00 | `Demographics_full.csv` (Date of birth / Circumference / Maximal), `pre_event_cohort.Date`; `core.json:item4.setC.P.M_release` |
| set C | progressors | Prague M (cm) | database-completed | 29 / 37 | mean 4.86; median 4.00 [3.00–7.00]; range 1.00–10.00 | by source: demographics: 27, endoscopy: 1, initial_history: 1; `Demographics_full.csv`, `[DB]/initial_history.parquet`, `[DB]/endoscopy.parquet`; `core.json:item4.setC.P.M_completed` |
| set C | progressors | sex | release-only (database: NOT AVAILABLE) | 37 / 37 | M: 29, F: 8 | `Demographics_full.csv` (Sex); `core.json:item4.setC.P.sex_release` |
| set C | progressors | smoking | release-only | 21 / 37 | Y: 17, N: 4 | `Demographics_full.csv` (Smoking Status); `core.json:item4.setC.P.smoking_release` |
| set C | progressors | smoking | database code, patients missing above (not harmonised) | 10 / 16 | code 0: 10 | `[DB]/initial_history.parquet` (smoking); `core.json:item4.setC.P.smoking_db_raw_codes_for_missing` |
| set C | progressors | baseline grade | release | 37 / 37 | NDBE: 24, LGD: 7, ID: 4, HGD: 2 | `[KC]_mm/set_C.csv` (Pathology), `[777]` (Months before final); `core.json:item4.setC.P.baseline_grade` |
| set C | non-progressors | age at first sample (years) | release-only | 43 / 43 | mean 61.89; median 65.54 [57.27–69.61]; range 37.86–76.82 | `Demographics_full.csv` (Date of birth / Circumference / Maximal), `pre_event_cohort.Date`; `core.json:item4.setC.NP.age_release` |
| set C | non-progressors | age at first sample (years) | database-completed | 43 / 43 | mean 61.89; median 65.54 [57.27–69.61]; range 37.86–76.82 | by source: demographics: 43; `Demographics_full.csv`, `[DB]/initial_history.parquet`, `[DB]/endoscopy.parquet`; `core.json:item4.setC.NP.age_completed` |
| set C | non-progressors | Prague C (cm) | release-only | 40 / 43 | mean 1.27; median 0.00 [0.00–2.00]; range 0.00–11.00 | `Demographics_full.csv` (Date of birth / Circumference / Maximal), `pre_event_cohort.Date`; `core.json:item4.setC.NP.C_release` |
| set C | non-progressors | Prague C (cm) | database-completed | 43 / 43 | mean 1.40; median 0.00 [0.00–2.00]; range 0.00–11.00 | by source: demographics: 40, endoscopy: 3; endoscopy-to-first-sample gap median 1,467 days (range 1,165–1,988); `Demographics_full.csv`, `[DB]/initial_history.parquet`, `[DB]/endoscopy.parquet`; `core.json:item4.setC.NP.C_completed` |
| set C | non-progressors | Prague M (cm) | release-only | 40 / 43 | mean 4.72; median 4.50 [3.00–5.25]; range 1.00–13.00 | `Demographics_full.csv` (Date of birth / Circumference / Maximal), `pre_event_cohort.Date`; `core.json:item4.setC.NP.M_release` |
| set C | non-progressors | Prague M (cm) | database-completed | 43 / 43 | mean 4.67; median 4.00 [3.00–5.00]; range 1.00–13.00 | by source: demographics: 40, endoscopy: 3; `Demographics_full.csv`, `[DB]/initial_history.parquet`, `[DB]/endoscopy.parquet`; `core.json:item4.setC.NP.M_completed` |
| set C | non-progressors | sex | release-only (database: NOT AVAILABLE) | 43 / 43 | M: 32, F: 11 | `Demographics_full.csv` (Sex); `core.json:item4.setC.NP.sex_release` |
| set C | non-progressors | smoking | release-only | 22 / 43 | Y: 16, N: 6 | `Demographics_full.csv` (Smoking Status); `core.json:item4.setC.NP.smoking_release` |
| set C | non-progressors | smoking | database code, patients missing above (not harmonised) | 17 / 21 | code 0: 14, code 2: 2, code 3: 1 | `[DB]/initial_history.parquet` (smoking); `core.json:item4.setC.NP.smoking_db_raw_codes_for_missing` |
| set C | non-progressors | baseline grade | release | 43 / 43 | NDBE: 31, ID: 7, LGD: 5 | `[KC]_mm/set_C.csv` (Pathology), `[777]` (Months before final); `core.json:item4.setC.NP.baseline_grade` |

Coverage: release 82 of 150 patients are in the demographic sheet and 149 have a database participant_id; set C 80 of 80 and 78 (`core.json:item4`). Set C first-sample dates: pre_event_cohort.Date for 80 patients (the cohort date of the same sequencing sample).

## 5. Whole-slide images

| Cohort | Quantity | n | Value | Source |
|---|---|---|---|---|
| release | slides | 707 | 707 (read errors 0) | `[REL]/pre_event_cohort.csv` ImageAbsPath, `[REL]/feature_views/uni2/uni2_index.csv`; `wsi_release.json:n_slides` |
| release | scanner C13239-01 (Hamamatsu, `hamamatsu.Product`) | 585 | 585 slides, 141 patients; native 0.2209 µm/px (range 0.2209–0.2209); at the tiling level 0.8835 µm/px | slide properties (openslide); `wsi_release.json:scanners, mpp_native_by_scanner, level_mpp_by_scanner` |
| release | scanner C13210 (Hamamatsu, `hamamatsu.Product`) | 122 | 122 slides, 27 patients; native 0.2204 µm/px (range 0.2204–0.2204); at the tiling level 0.8816 µm/px | slide properties (openslide); `wsi_release.json:scanners, mpp_native_by_scanner, level_mpp_by_scanner` |
| release | objective power (openslide) | 707 | 40× (707 slides) | slide properties; `wsi_release.json:objective` |
| release | native resolution, all slides (µm/px, level 0) | 707 | median 0.2209; range 0.2204–0.2209 | `openslide.mpp-x`; `wsi_release.json:mpp_native` |
| release | tiling level / tile size (px) | 707 | level 2 / 224 px (all slides) | npz keys `level`, `tile_size`; `wsi_release.json:level, tile_size` |
| release | resolution at tiling level (µm/px) and tile field (µm) | 707 | median 0.8835 µm/px (range 0.8816–0.8835); 224 px = 197.9 µm | mpp × `level_downsamples[2]`; `wsi_release.json:level_mpp` |
| release | tissue tiles available (kept: non-overlapping level-2 224-px cells whose centre is in the tissue mask) | 707 | mean 683.8; median 277 [181.5–933.5]; range 5.0–9,348 | `[SWG]/unannotated/masks/*_tissuetector.png`; `wsi_release.json:tissue_grid_tiles` |
| release | tiles sampled (requested) | 707 | mean 256; median 256 [256–256]; range 256–256 | npz `tiles_requested`/`tiles_ok`/`coords_level`; `wsi_release.json:tiles_requested` |
| release | tiles embedded | 707 | mean 256; median 256 [256–256]; range 256–256 | npz `tiles_requested`/`tiles_ok`/`coords_level`; `wsi_release.json:tiles_ok` |
| release | distinct sampled tile positions | 707 | mean 256; median 256 [256–256]; range 256–256 | npz `tiles_requested`/`tiles_ok`/`coords_level`; `wsi_release.json:distinct_sampled` |
| release | slides with fewer tissue tiles than the 256 sampled (sampled tiles overlap) | 707 | 315 | `wsi_release.json:slides_tissue_tiles_lt_requested` |
| release | slides sampled with replacement (mask pixels < 256) | 707 | 0 | `wsi_release.json:with_replacement` |
| release | feature extractor | 707 | UNI2-h (`timm` `hf-hub:MahmoodLab/UNI2-h`), embedding dim 1536 (all slides); 256 tile centres drawn uniformly at random from tissue-mask pixels (seed 20260226 + chunk) | `[BT]/scripts/extract_foundation_from_masks.py` (lines 66-72, 156, 234-238); `wsi_release.json:emb_dim` |
| set C | slides | 683 | 683 (read errors 0) | `[KC]/uni2_npz_map.csv`; `wsi_setc.json:n_slides` |
| set C | scanner C13239-01 (Hamamatsu, `hamamatsu.Product`) | 509 | 509 slides; native 0.2209 µm/px (range 0.2209–0.2209); at the tiling level 0.8835 µm/px | slide properties (openslide); `wsi_setc.json:scanners, mpp_native_by_scanner, level_mpp_by_scanner` |
| set C | scanner C13210 (Hamamatsu, `hamamatsu.Product`) | 174 | 174 slides; native 0.2204 µm/px (range 0.2204–0.2204); at the tiling level 0.8816 µm/px | slide properties (openslide); `wsi_setc.json:scanners, mpp_native_by_scanner, level_mpp_by_scanner` |
| set C | objective power (openslide) | 683 | 40× (683 slides) | slide properties; `wsi_setc.json:objective` |
| set C | native resolution, all slides (µm/px, level 0) | 683 | median 0.2209; range 0.2204–0.2209 | `openslide.mpp-x`; `wsi_setc.json:mpp_native` |
| set C | tiling level / tile size (px) | 683 | level 2 / 224 px (all slides) | npz keys `level`, `tile_size`; `wsi_setc.json:level, tile_size` |
| set C | resolution at tiling level (µm/px) and tile field (µm) | 683 | median 0.8835 µm/px (range 0.8816–0.8835); 224 px = 197.9 µm | mpp × `level_downsamples[2]`; `wsi_setc.json:level_mpp` |
| set C | tissue tiles available (kept: non-overlapping level-2 224-px cells whose centre is in the tissue mask) | 683 | mean 508.4; median 253 [173–353]; range 5.0–5,433 | `[SWG]/unannotated/masks/*_tissuetector.png`; `wsi_setc.json:tissue_grid_tiles` |
| set C | tiles sampled (requested) | 683 | mean 256; median 256 [256–256]; range 256–256 | npz `tiles_requested`/`tiles_ok`/`coords_level`; `wsi_setc.json:tiles_requested` |
| set C | tiles embedded | 683 | mean 256; median 256 [256–256]; range 256–256 | npz `tiles_requested`/`tiles_ok`/`coords_level`; `wsi_setc.json:tiles_ok` |
| set C | distinct sampled tile positions | 683 | mean 256; median 256 [256–256]; range 256–256 | npz `tiles_requested`/`tiles_ok`/`coords_level`; `wsi_setc.json:distinct_sampled` |
| set C | slides with fewer tissue tiles than the 256 sampled (sampled tiles overlap) | 683 | 348 | `wsi_setc.json:slides_tissue_tiles_lt_requested` |
| set C | slides sampled with replacement (mask pixels < 256) | 683 | 0 | `wsi_setc.json:with_replacement` |
| set C | feature extractor | 683 | UNI2-h (`timm` `hf-hub:MahmoodLab/UNI2-h`), embedding dim 1536 (all slides); 256 tile centres drawn uniformly at random from tissue-mask pixels (seed 20260226 + chunk) | `[BT]/scripts/extract_foundation_from_masks.py` (lines 66-72, 156, 234-238); `wsi_setc.json:emb_dim` |
| set C | tiles per sample bag (union of the sample's slides) | 676 | median 256; range 256–768; slides per sample 1: 671, 2: 3, 3: 2 | `[KC]_mm/bag_index.csv`; `wsi_setc.json:bag_tiles_per_sample` |
| release | frozen feature views in the release (the image model uses uni2) | 707 | uni2: 707 rows, dim 1536; virchow2: 707 rows, dim 2560; gigapath: 707 rows, dim 1536 | `[REL]/feature_views/*/*_index.csv`; `wsi_release.json:feature_views` |

Tiles come from the UNI2 extraction of 2026-02-26 (`[UNI]/manifest/manifest_dedup.csv`), which the release indexes. The tissue mask is the `tissuetector` PNG of each slide.

## 6. Shallow whole-genome sequencing

| Cohort | Quantity | n | Value | Source |
|---|---|---|---|---|
| release, both sheets | sWGS samples (with read counts / with BAM) | 693 | 693 / 693 | `swgs.json:release.all.samples` |
| release, both sheets | total reads per sample | 693 | mean 19,915,893; median 19,963,683; range 97,407–77,449,748 | `[SWG]/copy_number_hg38/{train/perPatient,val}/500kb/<id>/500.readCountSummary.txt`; `swgs.json:release.all.total_reads` |
| release, both sheets | reads used by QDNAseq | 693 | mean 19,226,759; median 19,278,010; range 93,918–75,308,765 | `[SWG]/copy_number_hg38/{train/perPatient,val}/500kb/<id>/500.readCountSummary.txt`; `swgs.json:release.all.used_reads` |
| release, both sheets | depth per sample (× = total reads × read length / 3,088,269,832) | 693 | mean 0.3224; median 0.3232; range 0.0016–1.2539 | `[SWG]/copy_number_hg38/{train/perPatient,val}/500kb/<id>/500.readCountSummary.txt`; `swgs.json:release.all.depth_total` |
| release, both sheets | read length (bp; first 2,000 reads per BAM) | 693 | modal length 50 bp (693 samples); range 39–50 (trimmed) | `[SWG]/dna_seq_bam/*.bam`; `swgs.json:release.all.read_length_mode` |
| release, both sheets | alignment | 693 | bwa 0.7.18-r1243-dirty `samse` (all 693 BAMs) to hg38 (hg38.fa: 437, Pipeline/hg38.fa: 256); chr1–22, X, Y length 3,088,269,832 bp (693 BAMs) | BAM `@PG`/`@SQ` headers; `swgs.json:release.all.bwa, reference` |
| release, 777-sheet | sWGS samples (with read counts / with BAM) | 494 | 494 / 494 | `swgs.json:release.777.samples` |
| release, 777-sheet | total reads per sample | 494 | mean 18,550,476; median 18,413,348; range 2,534,277–77,449,748 | `[SWG]/copy_number_hg38/{train/perPatient,val}/500kb/<id>/500.readCountSummary.txt`; `swgs.json:release.777.total_reads` |
| release, 777-sheet | reads used by QDNAseq | 494 | mean 17,913,799; median 17,669,189; range 2,462,428–75,308,765 | `[SWG]/copy_number_hg38/{train/perPatient,val}/500kb/<id>/500.readCountSummary.txt`; `swgs.json:release.777.used_reads` |
| release, 777-sheet | depth per sample (× = total reads × read length / 3,088,269,832) | 494 | mean 0.3003; median 0.2981; range 0.0410–1.2539 | `[SWG]/copy_number_hg38/{train/perPatient,val}/500kb/<id>/500.readCountSummary.txt`; `swgs.json:release.777.depth_total` |
| release, 777-sheet | read length (bp; first 2,000 reads per BAM) | 494 | modal length 50 bp (494 samples); range 39–50 (trimmed) | `[SWG]/dna_seq_bam/*.bam`; `swgs.json:release.777.read_length_mode` |
| release, 777-sheet | alignment | 494 | bwa 0.7.18-r1243-dirty `samse` (all 494 BAMs) to hg38 (Pipeline/hg38.fa: 248, hg38.fa: 246); chr1–22, X, Y length 3,088,269,832 bp (494 BAMs) | BAM `@PG`/`@SQ` headers; `swgs.json:release.777.bwa, reference` |
| release, 268-sheet | sWGS samples (with read counts / with BAM) | 199 | 199 / 199 | `swgs.json:release.268.samples` |
| release, 268-sheet | total reads per sample | 199 | mean 23,305,421; median 23,952,923; range 97,407–39,558,553 | `[SWG]/copy_number_hg38/{train/perPatient,val}/500kb/<id>/500.readCountSummary.txt`; `swgs.json:release.268.total_reads` |
| release, 268-sheet | reads used by QDNAseq | 199 | mean 22,486,067; median 23,007,669; range 93,918–38,437,798 | `[SWG]/copy_number_hg38/{train/perPatient,val}/500kb/<id>/500.readCountSummary.txt`; `swgs.json:release.268.used_reads` |
| release, 268-sheet | depth per sample (× = total reads × read length / 3,088,269,832) | 199 | mean 0.3773; median 0.3878; range 0.0016–0.6405 | `[SWG]/copy_number_hg38/{train/perPatient,val}/500kb/<id>/500.readCountSummary.txt`; `swgs.json:release.268.depth_total` |
| release, 268-sheet | read length (bp; first 2,000 reads per BAM) | 199 | modal length 50 bp (199 samples); range 39–50 (trimmed) | `[SWG]/dna_seq_bam/*.bam`; `swgs.json:release.268.read_length_mode` |
| release, 268-sheet | alignment | 199 | bwa 0.7.18-r1243-dirty `samse` (all 199 BAMs) to hg38 (hg38.fa: 191, Pipeline/hg38.fa: 8); chr1–22, X, Y length 3,088,269,832 bp (199 BAMs) | BAM `@PG`/`@SQ` headers; `swgs.json:release.268.bwa, reference` |
| set C | sWGS samples (with read counts / with BAM) | 676 | 676 / 676 | `swgs.json:setC.samples` |
| set C | total reads per sample | 676 | mean 18,292,917; median 18,033,248; range 2,330,403–105,904,745 | `[SWG]/copy_number_hg38/train/perPatient/50kb/<id>/50.readCountSummary.txt`; `swgs.json:setC.total_reads` |
| set C | reads used by QDNAseq | 676 | mean 17,664,763; median 17,432,422; range 2,263,712–100,764,245 | `[SWG]/copy_number_hg38/train/perPatient/50kb/<id>/50.readCountSummary.txt`; `swgs.json:setC.used_reads` |
| set C | depth per sample (× = total reads × read length / 3,088,269,832) | 676 | mean 0.2962; median 0.2920; range 0.0377–1.7146 | `[SWG]/copy_number_hg38/train/perPatient/50kb/<id>/50.readCountSummary.txt`; `swgs.json:setC.depth_total` |
| set C | read length (bp; first 2,000 reads per BAM) | 676 | modal length 50 bp (676 samples); range 38–50 (trimmed) | `[SWG]/dna_seq_bam/*.bam`; `swgs.json:setC.read_length_mode` |
| set C | alignment | 676 | bwa 0.7.18-r1243-dirty `samse` (all 676 BAMs) to hg38 (hg38.fa: 345, Pipeline/hg38.fa: 331); chr1–22, X, Y length 3,088,269,832 bp (676 BAMs) | BAM `@PG`/`@SQ` headers; `swgs.json:setC.bwa, reference` |
| set C | reads per sample, sheet column `Number of reads` | 671 | mean 22,805,065; median 21,515,146; range 3,872,011–220,095,445 | `[777]`; `swgs.json:setC_sheet_number_of_reads` |
| release | CNV source: build / bins | 693 | hg38 / QDNAseq 500 kb (`500.copy_number.txt`) | `[BT]/scripts/killcoyne_reproduce_from_500kb.R` (lines 28, 294-332: `bin_kb` default 500, maps the 50 kb path to the 500 kb folder); `[BT]/slurm/submit_stage1_segment.sh` line 45 (no `--bin_kb`, so 500) |
| release | CNV pipeline | 707 | QDNAseq 500 kb copy number → copynumber::pcf(assembly=hg38) (copynumber 1.15.0), gamma 40, kmin 5, QC none → 587 5-Mb windows (arm-adjusted) + 44 arm means + cx = 632 features | `[BT]/data/killcoyne_repro_strict_500kb_slurm_v2/run_config.json` (args); `[REL]/feature_views/cnv/*.csv` (column counts); `swgs.json:release_cnv_build` |
| release | producer of the 500 kb QDNAseq folders | 693 | NOT AVAILABLE: no generating script in `[BT]` (its QDNAseq generator `scripts/swg_generate_qdnaseq_one_sample.R` accepts only 10 or 50 kb) | `[BT]/scripts/swg_generate_qdnaseq_one_sample.R` line 165 |
| set C | CNV source 'pkg' (ours): build / bins / pipeline | 676 | hg38 / QDNAseq 50 kb raw + fitted counts / BarrettsProgressionRisk `segmentRawData` (gamma2 250, cutoff 0.008) with hg38 adaptations → 632 features | `[KC]_mm/cnv_pkg_C.csv` (632 feature columns); `docs/paper_plan_killcoyne_reconcile.md` lines 16-17, 368 |
| set C | CNV source 'their' (Killcoyne shipped matrix): build / bins / pipeline | 676 | hg19 / 50 kb / the package's shipped training matrix (773 × 634), rows aligned to our samples → 634 features | `[KC]_mm/cnv_their_C.csv` (634 feature columns); `docs/paper_plan_killcoyne_reconcile.md` lines 11, 366, 368 |

Depth is nominal: reads × modal read length over the hg38 chr1–22, X, Y length, with no correction for duplicates or mapping quality. The 'their' source has no read-level data of its own; it comes from the same sequencing runs.

## 7. ACE-B (manifest only; no outcome data read)

| Quantity | n | Value | Source |
|---|---|---|---|
| samples / patients | 234 | 234 samples (234 distinct SampleID), 117 PatientID | `[ACEB]`; `core.json:item7.samples, patients` |
| samples per patient | 117 | mean 2.00; median 2; range 1–6 | `[ACEB]`; `core.json:item7.samples_per_patient` |
| WSI (slides, scanner, resolution, tiling, extractor) | 0 | NOT AVAILABLE: the manifest has no slide fields and no ACE-B slides are on the cluster | `[ACEB]` columns Batch, Name, Index, PatientID, Date of extraction, DNA conc (ng/µl), DNA amount (ng), SLX, SampleID, Mean_Coverage (+ Pathology, not read); `/mnt/scratche/fast/fmlab/datasets/imaging` has no ACE-B directory; `core.json:item7.imaging_dirs_matching_ace` |
| sequencing batches | 234 | batch 2: 96, batch 1: 96, batch 3: 42 | `[ACEB]` Batch; `core.json:item7.batches` |
| sequencing pools (SLX) | 234 | SLX-26851_SLX-27128: 96, SLX-26195_SLX-26196: 95, SLX-27125: 42, SLX-26195: 1 | `[ACEB]` SLX; `core.json:item7.slx_pools` |
| depth per sample (`Mean_Coverage`, ×) | 191 | mean 5.76; median 5.30; range 3.29–14.91 | `[ACEB]` Mean_Coverage; `core.json:item7.mean_coverage` |
| depth, batch 1 | 96 | mean 6.42; median 6.20; range 3.55–11.41 | `[ACEB]`; `core.json:item7.mean_coverage_by_batch` |
| depth, batch 2 | 95 | mean 5.09; median 4.61; range 3.29–14.91 | `[ACEB]`; `core.json:item7.mean_coverage_by_batch` |
| depth, batch 3 | 0 | — | `[ACEB]`; `core.json:item7.mean_coverage_by_batch` |
| read length, genome build, bin size, CNV pipeline | 0 | NOT AVAILABLE in the manifest | `[ACEB]` columns |

The ACE-B cases file and the cohort owner's outcome split were not read. The manifest's `Pathology` column was not read.

# Demographics completion: database smoking code, Killcoyne supplementary data, database-filled demographics, updated Table 1

Status: PRE-SPECIFICATION (written 2026-10-02). Nothing below has been computed except the structure probe that lists table and column names (`scripts/paper_plan/dm_probe.py`, no values of any cross-tab). Results are appended under the line at the end in a later commit; this section is not edited afterwards.

Ground rules: report only, no fitting; every number with file, script and commit; status per item (DONE / PARTIAL / NOT AVAILABLE / NOT RESOLVED); no imputation; earlier docs not edited. For ACE-B patients only demographic fields are read; no pathology, outcome or follow-up field is read for them. Row-level outputs stay on the cluster under `feasibility/paper_plan/demographics/`; the repository gets aggregates only.

Cohorts: the discovery subset (set C: 80 patients, 37 P by the 777-sheet `Status`), the frozen SWG release (150 patients, 50 P by `training_manifest.y_progressor`), ACE-B (117 PatientID in `ACEB_samples_for Rehan.csv`; no labels). Paths and aliases as in `docs/dataset_description.md`.

## D1. Database smoking field

1. Search the Barrett's DB export (`/mnt/scratche/slow/fmlab/zuberi01/barretts_db_export/`), its report JSONs, any column-dictionary table, any scraping or export code under `/mnt/scratche/slow/fmlab/zuberi01` and `/home/zuberi01`, and dictionary-like file names (dictionary, codebook, lookup, schema, enum, form, `.sql`, `.mdb`, `.accdb`), for a definition of `smoking` and of any other smoking field (pack-years, ex-smoker, quit date). Every path checked is listed.
2. Cross-tab: database code (0, 1, 2, 3, blank) against `Demographics_full.csv` Smoking Status (Y/N), for every patient who has both. Demographics_full is the only Y/N reference and covers the Killcoyne discovery cohort only (90 rows), so "all cohorts" = every Demographics_full patient that links to the database, whether or not in our subsets. Linkage: Study Number or Alternate Study Number → `pre_event_cohort.participant_id` (release patients), or any database identifier column whose values equal the study number (named in the output). Counts per cell and n.
3. Default-value test: number of non-null fields per `initial_history` record (null = NaN, None, '' or 'None'); records split into terciles of that count; share of smoking = 0 in the lowest vs the highest tercile, with n. **0 is called a default (missing) value if its share in the lowest tercile exceeds its share in the highest by ≥ 20 percentage points.** For every other numeric-coded column of `initial_history`, the same two shares, and whether 0 is that column's most common value.
4. **Decision rule (fixed here, before the cross-tab).**
   - Overlap set O = patients with a Y/N value and a non-blank database code; if 3 calls 0 a default, code 0 is treated as blank and removed from O.
   - Candidate mapping: each remaining code is assigned Y or N by the majority of O's Y/N values for that code (a tie leaves the code unassigned, and the mapping fails).
   - Accept the mapping only if |O| ≥ 20 **and** the mapping agrees with Y/N for ≥ 90% of O. Otherwise the field is NOT RESOLVED and smoking stays at the sheet values.
   - Stated in advance: the mapping is chosen and scored on the same patients, so the agreement is optimistic; the rule is applied as written.

## D2. Killcoyne 2020 supplementary data

Search the repository, the lab scratch (sharded `lfs find` over `/mnt/scratche/fast/fmlab` and `/mnt/scratche/slow/fmlab`, `scripts/paper_plan/dm_namesearch.py`) and the installed `BarrettsProgressionRisk` package (all files, including `data/` and `extdata/`) for the supplementary tables or any per-patient demographic or metadata file. List every column of the 777-sample sheet holding demographics (age, sex, BE length, smoking, age at diagnosis). If Supplementary Table 1 is found, compare its summaries with the 80 patients of the discovery subset (sheet values).

## D3. Database-filled demographics (discovery subset, release, ACE-B)

- **Linkage.** Discovery subset and release: `pre_event_cohort.participant_id` (".0" removed). ACE-B: an ACE-B-to-database identifier mapping in `aceb_meta/`, reading identifier columns only; if none links without reading other fields, NOT AVAILABLE.
- **Age at BE diagnosis** = (date of first BE diagnosis in the database − date of birth)/365.25, alongside **age at first sample** (first sample = first release row for the release, first set C sample for the discovery subset, as in `docs/dataset_description.md`; for ACE-B no biopsy date is read, so NOT AVAILABLE). Sheet `Age at diagnosis` reported alongside for the discovery subset.
- **Prague C/M** from the database endoscopy closest in date to the first sample (`endoscopy.parquet` `barretts_circumference`, `barretts_maximum`, `endoscopydate`), with the gap in days; values more than 365 days away are flagged. For ACE-B (no sample date), the `initial_history` `praguec`/`praguem` value is reported instead, labelled as such.
- **Sex** from any database table holding it (table named); else NOT AVAILABLE from the database.
- **If present:** BMI (height and weight from the database, record closest to the first sample), alcohol, hiatal hernia, PPI use, family history of BE/OAC, ethnicity.
- For each variable: coverage n/N by cohort and by label (discovery subset and release; no labels for ACE-B), source table and column, and how missing values are represented (counts of NaN, None, '', 'None', 0 where relevant). No imputation.

## D4. Updated Table 1

Discovery subset by label and ACE-B (no labels): every variable from D1–D3 with coverage; each value marked as sheet or database.

## Output

`docs/demographics_completion.md` (this file, results below), `results/paper_final/demographics/*.json` (aggregates), scripts `scripts/paper_plan/dm_*.py`, run through `scripts/cluster/campaign.sh`.

---

## Results

Pre-specification commit 24b2972; results commit 1256b0e. Scripts `scripts/paper_plan/dm_probe.py`, `dm_probe2.py`, `dm_probe3.R`, `dm_probe4.py`, `dm_namesearch.py`, `dm_supp.py`, `dm_st1.py`, `dm_analyse.py`, `dm_agree.py`, `dm_render.py`, all run through `scripts/cluster/campaign.sh` (prefixes dmp, dmc, dms, dmn, dmnx, dmp34, dmsu, dmst, dma, dmag, dmm). Results `results/paper_final/demographics/{d1,d1_search,d1_search_uncovered,d2_name_search,d2_supp,d2_st_compare,d3,d3_agree}.json`. Row-level tables on the cluster only: `feasibility/paper_plan/demographics/d1_crosstab_rows.csv`, `d3_patient_rows.csv`.

Sources added by the search (both read for demographic columns only): `BE_Progression_Project.db` (SQLite, in `/mnt/scratche/slow/fmlab/zuberi01/phd/aceb_meta/`, a Django database of the BE progression project: 165 patients; table `Patient` columns Gender, AgeAtDiagnosis, SmokingStatus, Height, Weight, DateInitialDiagnosis, Circumference, Maximal, linked to study numbers through `AlternatePatientID`; its `Status` and `DateProgressed` columns were not read) and, for ACE-B, `aceb_sample_counts_per_patient_20260527_121448.csv` (a scrape of the Barrett's participant table: participant_id, gender, date_of_birth read; date_of_death not read).

### Status

| Item | Status |
|---|---|
| D1 database smoking field | NOT RESOLVED (no codebook found; rule failed on agreement) |
| D2 Killcoyne supplementary data | DONE: supplementary appendix and all 14 Source Data files found on the cluster; Supplementary Table 1 compared |
| D3 database-filled demographics | DONE (with NOT AVAILABLE cells: database sex, ethnicity, family history; ACE-B age at first sample and dated Prague) |
| D4 updated Table 1 | DONE |

### D1. Database smoking field

**Question.** What do the `initial_history.smoking` codes 0/1/2/3 mean? **Status.** NOT RESOLVED. **Pre-specification.** Above (D1), decision rule committed in 24b2972 before the cross-tab.

**1. Definitions searched.** Database export tables and the report JSONs (`extras_report.json`, `match_report.json`, `match_report_v2.json`): no codebook. `occams_table_column.parquet` (660 rows, the OCCAMS column dictionary) defines `EX_IsSmoker` (current / former / never / unknown) and `EX_SmokingDurationYears` for the OCCAMS exposure form `ex_exposures_z1_0_0`, not the Barrett's `initial_history` table. Other smoking fields in `initial_history`: `packyears` (free text). No ex-smoker or quit-date column. Code and text files referencing the database (`initial_history`/`initialhistory`/`barretts_db_export`) under `/mnt/scratche/slow/fmlab/zuberi01`, `/mnt/scratche/fast/fmlab/zuberi01`, `/home/zuberi01`: 50 files in 47,965 candidate files (< 5 MB, code/text extensions; software folders excluded: conda/pixi environments, site-packages, R libraries, `.git`, and the two Python virtual environments `personal/scifi_video/env` and `env_tts`; 461 shards); lines in them mentioning smoking: 168 (`/mnt/scratche/slow/fmlab/zuberi01/phd/thesis/EXECUTION_PLAN.md:82: numbers, (c) candidate disagreement-resolver. Smoke on the 80 adjudicated`; `/mnt/scratche/slow/fmlab/zuberi01/phd/thesis/EXECUTION_PLAN.md:839: (medgemma if pullable), self-gating smoke->corpus jobs; (b) disagreement-driver`; `/mnt/scratche/slow/fmlab/zuberi01/phd/thesis/EXECUTION_PLAN.md:84: *JURY SMOKE COMPLETE 2026-08-20: 9/10 scored (llama3.3:70b pending). Five models`; `/mnt/scratche/slow/fmlab/zuberi01/phd/thesis/EXECUTION_PLAN.md:870: viability (>=95% on adjudicated-80 smoke) ONLY — never on agreement, to avoid`; `/mnt/scratche/slow/fmlab/zuberi01/phd/thesis/docs/dataset_description.md:110: Release-only = the cohort's demographic sheet `[SWG]/Demographics_full.csv` (Study`; `/mnt/scratche/slow/fmlab/zuberi01/phd/thesis/docs/dataset_description.md:121: | release | all | smoking | release-only | 44 / 150 | Y: 33, N: 11 | `Demographics`). Dictionary-like file names (dictionary, codebook, lookup, schema, enum, form, `.sql`, `.mdb`, `.bak`): 562 paths, all library headers, backups of ID maps or SQL query templates; none defines the field. Not searched (listing did not finish after two re-splits; cancelled): `/mnt/scratche/slow/fmlab/zuberi01/phd/barretts_retraining/barretts_training/analysis`, `/mnt/scratche/slow/fmlab/zuberi01/phd/barretts_retraining/barretts_training/data`, `/mnt/scratche/slow/fmlab/zuberi01/phd/barretts_progressor/scripts/unimodal`, `/mnt/scratche/slow/fmlab/zuberi01/phd/barretts_progressor_broken/scripts/unimodal`; searched with code and document extensions only: `/mnt/scratche/slow/fmlab/zuberi01/phd/barretts_progressor_broken/scripts/multimodal`, `/mnt/scratche/slow/fmlab/zuberi01/phd/barretts_progressor/scripts/multimodal`, `/mnt/scratche/slow/fmlab/zuberi01/phd/barretts_retraining/paper/hg19_relative_copy_number_qc_exact_20260330`. The export code itself (`scripts/export_barretts_db.py`, `scripts/export_barretts_occams.py`) pulls whole tables from the database REST API (`api.barrettsdatabase.org.uk`) and defines no fields. The full path lists are in `d1_search.json`.

**2. Cross-tab** (Demographics_full rows 90; linked to the database: pre_event_cohort.participant_id 87, not linked 3).

| Database code | Sheet Y | Sheet N | Sheet missing |
|---|---|---|---|
| 0 | 25 | 7 | 30 |
| 2 | 1 | 0 | 1 |
| 3 | 0 | 0 | 1 |
| conflict:0/2 | 2 | 0 | 1 |
| conflict:0/3 | 1 | 2 | 0 |
| no_initial_history_row | 5 | 2 | 9 |
| no_participant_id | 1 | 0 | 2 |

Patients with a single database code and a Y/N value: n = 33. 'conflict:a/b' = the participant's records disagree; 'no_initial_history_row' = linked but no record.

Secondary, not pre-specified: database code against `BE_Progression_Project.db` Patient.SmokingStatus for the same rows.

| Database code | never | former | current | None |
|---|---|---|---|---|
| 0 | 7 | 22 | 3 | 30 |
| 2 | 0 | 1 | 0 | 1 |
| 3 | 0 | 0 | 0 | 1 |
| conflict:0/2 | 0 | 2 | 0 | 1 |
| conflict:0/3 | 2 | 1 | 0 | 0 |
| no_initial_history_row | 2 | 5 | 0 | 9 |
| no_participant_id | 0 | 1 | 0 | 0 |

**3. Default-value test.** Pre-specified: non-null fields per `initial_history` record median 25.0 (range 4.0–105.0, n 6155); share of smoking = 0 in the lowest tercile 0.0% (n 2052) vs the highest 95.42% (n 2052): difference -95.42 points, so by the rule 0 is **not** called a default. The lowest tercile is made of records with every field null (3,024 records whose fields are all the string 'None'), so smoking is null there, not 0; the test is degenerate. Sensitivity (not pre-specified), records with any smoking value (n 3130): 0 is 100.0% / 100.0% / 91.09% across terciles (difference 8.91 points, below 20).

Other numeric-coded `initial_history` columns where 0 is the mode and ≥ 90% of non-null values: `referredby`, `occupation`, `highesteducation`, `dysto`, `heartfrequency`, `regurgitationfrequency`, `nauseafrequency`, `vomitingfrequency`, `dyspepsiafrequency`, `abdnature`, `fundoopen`, `ppiduration`, `exercise`, `currentbmi`, `bmi`, `waisthipratio`, `waisthipcalc`, `selectedpatient` (for example `occupation` 100.0%, `highesteducation` 100.0%, `currentbmi` 99.97%, `bmi` 92.85%): the table stores 0 for 'not entered' in many fields. Columns with 0 rare: `diabetescontrol` 4.18%, `ppi` 0.0%, `ppidose` 7.45%, `ppifreq` 7.98%, `praguem` 1.52%, `heightm` 0.0%, `weightkg` 0.0%, `waist` 0.0%, `hip` 0.0%.

**4. Decision.** Overlap |O| = 33 (≥ 20); 0 not treated as blank (by the pre-specified test); majority mapping 0 → Y, 2 → Y; agreement 78.79% (< 90%). **NOT RESOLVED**: smoking stays at the sheet values.

**Method.** `dm_analyse.py` PART=d1: Demographics_full Study / Alternate Study Number → `pre_event_cohort.participant_id`, else `initial_history.hospitalnumber` / `patient_anonref`; database code = the single distinct non-null `smoking` value across the participant's records. **Sources.** `[DB]/initial_history.parquet`, `[DB]/occams_table_column.parquet`, `[SWG]/Demographics_full.csv`, `[REL]/pre_event_cohort.csv`, `aceb_meta/BE_Progression_Project.db`; `d1.json`, `d1_search.json`.
**Caveats.** (1) Code 0 occurs among never, former and current smokers alike (secondary table), and the other columns' zeros point to 0 = not entered, but the pre-specified test did not establish it. (2) Codes 1–3 have too few overlapping patients (≤ 3 each) to map. (3) Only the Killcoyne discovery cohort has a Y/N reference, so 'all cohorts' reduces to 87 linked patients.

### D2. Killcoyne 2020 supplementary data

**Question.** Are the supplementary tables (especially Supplementary Table 1) available locally, and what do they add? **Status.** DONE (Supplementary Information PDF and Reporting Summary not on the cluster). **Pre-specification.** Above (D2).

**Search.** Lab scratch filenames (467 `lfs find` shards, 14,853,322 files listed): 367 hits on the pre-specified pattern, most of them false positives on the digits '1033' in slide and case names; 19 are Killcoyne 2020 files (`d2_name_search.json`): the main-text PDF (`s41591-020-1033-y.pdf`, 4 copies), the PMC supplementary appendix `EMS86618-supplement-Supp_Appendix.docx` (in `/mnt/scratche/fast/fmlab/zuberi01/personal/temp_hdd/Rehan/Downloads/Admin & Travel/`), and all 14 Nature Source Data files `41591_2020_1033_MOESM3`–`MOESM16_ESM.xlsx` in `/mnt/scratche/slow/fmlab/zuberi01/phd/killcoyne_data_from_paper/` (sizes identical to the files on nature.com). The Supplementary Information PDF (`MOESM1`) and Reporting Summary (`MOESM2`) are not on the cluster; the PMC appendix carries the same Supplementary Tables 1–4.
`BarrettsProgressionRisk` (installed in `envs/killcoyne_r` and two clones, `phd/BarrettsProgressionRisk` and `paper/qc_historical_replay_plan_20260330/BarrettsProgressionRisk_repo`): `data/` holds only `ExampleQDNAseqData` (example `raw.data`, `fit.data`, `info`); `inst/extdata/` holds chromosome info files, the QDNAseq blacklist and an example `endoscopy.xlsx` with example QDNAseq counts; `R/sysdata` holds the fitted `be_model` and `rxRules`. No per-patient demographic or metadata file is shipped (`feasibility/paper_plan/demographics/probe3_pkg.txt`).
The 777-sample sheet has no demographic column: of its 43 columns none holds age, sex, BE length, smoking or age at diagnosis (the only regex hit, 'Esophageal location', is a false positive).

**What the files hold** (`d2_supp.json`): supplementary appendix tables: Supplementary Table 1: UK Discovery Cohort Demographics; Supplementary Table 2: UK Validation Cohort Demographics; Supplementary Table 3 Model coefficients; Supplementary Table 4 Model recommendations.. Source Data sheets: per-sample published probability, relative risk and risk class (MOESM4, Fig. 2a), per-sample status, oesophageal location, risk class and months before final (MOESM4 Fig. 2d, MOESM11), per-patient max probability and recommendations (MOESM5, MOESM6), complexity scores and copy-number values (MOESM3, MOESM7), validation probabilities, purity and ASCAT ratios (MOESM9), model tuning and bin-size results (MOESM10, MOESM12, MOESM15, MOESM16), p53 counts (MOESM13), QC example profiles (MOESM14). None holds per-patient demographics; the demographics exist only as the summaries of Supplementary Tables 1 and 2.

**Supplementary Table 1 against our data** (NP / P; our values from `Demographics_full.csv`, `Maximal` as BE segment length, `Total Followup (years)` as follow-up; `d2_st_compare.json`):

| Row | Supplementary Table 1 (published) | Demographics_full.csv, all rows (P/NP column) | Discovery subset, 80 (sheet Status) |
|---|---|---|---|
| Patients (NP / P) | 43 / 45 | 45 / 45 | 43 / 37 |
| Mean age at diagnosis ± SD | 59.7 ± 10 / 62.4 ± 9.7 | 59.0 ± 10.7 / 62.4 ± 9.7 | 59.7 ± 10.0 / 61.5 ± 9.6 |
| BE segment length cm ± SD (not recorded) | 4.7 ± 2.6 (3) / 4.6 ± 2.4 (12) | 4.9 ± 2.8 (4) / 4.6 ± 2.4 (12) | 4.7 ± 2.6 (3) / 4.7 ± 2.6 (10) |
| Female : male | 11:32 / 8:37 | 12:33 / 8:37 | 11:32 / 8:29 |
| Smoking yes : no (not recorded) | 16:6 (21) / 19:5 (21) | 16:6 (23) / 19:5 (21) | 16:6 (21) / 17:4 (16) |
| Follow-up years, range (mean ± SD) | 3–13 (6.7 ± 3.2) / 1–15 (4.6 ± 3.7) | 3–14 (8.2 ± 3.0) / 1–15 (5.9 ± 3.5) | 3–14 (8.4 ± 2.9) / 1–15 (6.1 ± 3.7) |

Supplementary Table 2 (validation, 58 NP / 18 P): age at diagnosis 67.1 ± 13 / 62.8 ± 9.7, F:M 14:42 / 4:14, BE length 6.3 ± 3.1 / 5.4 ± 2.9, smoking 14:16 (27) / 11:4 (3). The release's 268-sheet patients with validation-sheet Status, from `BE_Progression_Project.db`: 63 NP / 18 P; age 66.2 ± 12.8 / 62.8 ± 9.7; F:M 17:46 / 4:14; BE length 6.2 ± 3.1 / 5.4 ± 2.9; smoking (former or current) : never (not recorded) 16:17 (30) / 11:4 (3).

**Result.** Our 43 discovery non-progressors reproduce Supplementary Table 1's non-progressor column exactly, and all 45 progressors in `Demographics_full.csv` reproduce its progressor column exactly; our discovery subset holds 37 of those 45 (the 8 without a UNI2 slide are missing), so its progressor column differs. The 18 validation progressors reproduce Supplementary Table 2 exactly; our validation-sheet non-progressors are 63 against the published 58. Follow-up does not reproduce: `Total Followup (years)` is longer than the published follow-up (NP 8.2 vs 6.7 years), so the paper used another follow-up definition (the sheet also has 'Length of Followup with Sequencing', not compared).
**Method.** `dm_namesearch.py` (search), `dm_supp.py` (appendix tables parsed from the docx XML; Source Data sheet headers), `dm_st1.py` (summaries). **Sources.** As named; `d2_name_search.json`, `d2_supp.json`, `d2_st_compare.json`.
**Caveats.** Supplementary Table 1 reports 'BE segment length' without defining it; Prague M (`Maximal`) reproduces it exactly, so it is taken as M.

### D3. Database-filled demographics

**Question.** What can the database add, for the discovery subset (80), the release (150) and ACE-B (117)? **Status.** DONE, with NOT AVAILABLE cells. **Pre-specification.** Above (D3).

**Linkage.** Discovery subset: 78/80 with a database participant_id, 80/80 in `BE_Progression_Project.db`. Release: 149/150 and 150/150. ACE-B: PatientID → participant_id through `aceb_rehan_study_number_match_table_20260527_1323.csv` (study_number and participant-id columns only): one 91, none 26 of 117.

| Variable | Discovery all | Discovery P | Discovery NP | Release all | Release P | Release NP | ACE-B | Source |
|---|---|---|---|---|---|---|---|---|
| Age at first sample, sheet DOB (years) | 63.42 [57.2–69.45] (80/80) | 61.23 [56.55–69.22] (37/37) | 65.54 [57.27–69.61] (43/43) | 63.59 [56.68–69.89] (82/150) | 64.69 [57.08–70.53] (40/50) | 62.52 [55.71–69.05] (42/100) | — (0/117) | `Demographics_full.csv` Date of birth; first-sample date |
| Age at first sample, database DOB | 62.39 [55.69–69.01] (36/80) | 59.51 [55.69–68.96] (16/37) | 65.52 [56.0–69.01] (20/43) | 63.2 [55.11–70.76] (64/150) | 61.55 [54.83–69.77] (15/50) | 63.22 [55.78–70.69] (49/100) | — (0/117) | `initial_history.dob` (ACE-B: participant table) |
| Age at BE diagnosis, sheet | 61.5 [55.0–67.0] (80/80) | 60.0 [55.0–67.0] (37/37) | 63.0 [55.0–66.0] (43/43) | 62.0 [55.0–67.75] (82/150) | 63.5 [55.75–68.25] (40/50) | 60.5 [52.75–66.0] (42/100) | — (0/117) | `Demographics_full.csv` Age at diagnosis |
| Age at BE diagnosis, BE progression DB | 61.5 [55.0–67.0] (80/80) | 60.0 [55.0–67.0] (37/37) | 63.0 [55.0–66.0] (43/43) | 65.0 [56.0–70.0] (150/150) | 64.5 [57.25–68.75] (50/50) | 65.0 [55.75–73.0] (100/100) | — (0/117) | `BE_Progression_Project.db` Patient.AgeAtDiagnosis |
| Age at BE diagnosis, database | 63.18 [58.51–68.0] (24/80) | 61.59 [59.49–67.27] (10/37) | 64.89 [57.23–68.41] (14/43) | 61.78 [52.87–68.02] (45/150) | 61.55 [52.87–67.67] (9/50) | 62.37 [53.93–68.08] (36/100) | 59.67 [55.88–64.06] (7/117) | `initial_history.datediagnosed` − `dob` |
| Sex, sheet | M 61, F 19 (80/80) | M 29, F 8 (37/37) | M 32, F 11 (43/43) | M 64, F 18 (82/150) | M 33, F 7 (40/50) | M 31, F 11 (42/100) | — (0/117) | `Demographics_full.csv` Sex |
| Sex, BE progression DB | male 61, female 19 (80/80) | male 29, female 8 (37/37) | male 32, female 11 (43/43) | male 114, female 36 (150/150) | male 40, female 10 (50/50) | male 74, female 26 (100/100) | — (0/117) | Patient.Gender |
| Sex, participant table (ACE-B) | — (0/80) | — (0/37) | — (0/43) | — (0/150) | — (0/50) | — (0/100) | Male 38, Female 14 (52/117) | `aceb_sample_counts_per_patient` gender |
| Prague C, sheet (cm) | 0.0 [0.0–2.0] (64/80) | 0.0 [0.0–1.25] (24/37) | 0.0 [0.0–2.0] (40/43) | 0.0 [0.0–2.0] (66/150) | 0.0 [0.0–2.0] (28/50) | 0.0 [0.0–1.75] (38/100) | — (0/117) | `Demographics_full.csv` Circumference |
| Prague C, BE progression DB | 0.0 [0.0–2.0] (64/80) | 0.0 [0.0–1.25] (24/37) | 0.0 [0.0–2.0] (40/43) | 1.0 [0.0–5.0] (134/150) | 0.5 [0.0–3.0] (38/50) | 2.0 [0.0–5.0] (96/100) | — (0/117) | Patient.Circumference |
| Prague C, database closest endoscopy | 0.0 [0.0–2.25] (24/80) | 0.0 [0.0–0.0] (12/37) | 2.5 [0.75–4.0] (12/43) | 0.0 [0.0–4.0] (62/150) | 0.0 [0.0–0.0] (25/50) | 3.0 [0.0–6.0] (37/100) | — (0/117) | `endoscopy.barretts_circumference` |
|   gap to first sample (days) | 4581.5 [2923.25–5824.75] (24/80) | 4143.5 [2923.25–4630.75] (12/37) | 5430.5 [3903.5–6077.0] (12/43) | 3471.0 [2264.5–4865.25] (62/150) | 3035.0 [1988.0–4621.0] (25/50) | 3834.0 [2502.0–4916.0] (37/100) | — (0/117) | `endoscopy.endoscopydate` |
| Prague C, database baseline | 0.0 [0.0–5.0] (21/80) | 0.0 [0.0–0.0] (10/37) | 4.0 [0.5–5.5] (11/43) | 1.5 [0.0–5.0] (38/150) | 0.0 [0.0–1.5] (8/50) | 3.0 [0.25–5.0] (30/100) | 4.5 [4.0–6.5] (6/117) | `initial_history.praguec` |
| Prague M, sheet (cm) | 4.0 [3.0–6.0] (67/80) | 4.0 [3.0–6.5] (27/37) | 4.5 [3.0–5.25] (40/43) | 4.0 [3.0–5.0] (69/150) | 4.0 [2.5–5.0] (31/50) | 4.5 [3.0–5.75] (38/100) | — (0/117) | `Demographics_full.csv` Maximal |
| Prague M, BE progression DB | 4.0 [3.0–6.0] (67/80) | 4.0 [3.0–6.5] (27/37) | 4.5 [3.0–5.25] (40/43) | 5.0 [3.0–7.0] (137/150) | 4.0 [3.0–6.0] (41/50) | 5.0 [3.0–7.0] (96/100) | — (0/117) | Patient.Maximal |
| Prague M, database closest endoscopy | 3.0 [0.0–4.0] (24/80) | 0.0 [0.0–0.75] (12/37) | 4.0 [3.0–5.0] (12/43) | 3.5 [0.0–6.0] (62/150) | 0.0 [0.0–3.0] (25/50) | 5.0 [3.0–7.0] (37/100) | — (0/117) | `endoscopy.barretts_maximum` |
|   gap to first sample (days) | 4581.5 [2923.25–5824.75] (24/80) | 4143.5 [2923.25–4630.75] (12/37) | 5430.5 [3903.5–6077.0] (12/43) | 3471.0 [2164.0–4865.25] (62/150) | 3035.0 [1988.0–4621.0] (25/50) | 3819.0 [2502.0–4916.0] (37/100) | — (0/117) | `endoscopy.endoscopydate` |
| Prague M, database baseline | 5.0 [3.25–6.75] (22/80) | 5.0 [2.5–7.5] (11/37) | 5.0 [4.0–6.0] (11/43) | 5.0 [2.0–7.0] (39/150) | 5.0 [3.0–7.0] (9/50) | 5.0 [2.0–6.75] (30/100) | 6.0 [5.25–7.5] (6/117) | `initial_history.praguem` |
| Smoking, sheet | Y 33, N 10 (43/80) | Y 17, N 4 (21/37) | Y 16, N 6 (22/43) | Y 33, N 11 (44/150) | Y 18, N 3 (21/50) | Y 15, N 8 (23/100) | — (0/117) | `Demographics_full.csv` Smoking Status |
| Smoking, BE progression DB | former 30, never 10, current 3 (43/80) | former 15, never 4, current 2 (21/37) | former 15, never 6, current 1 (22/43) | former 53, never 28, current 3 (84/150) | former 23, never 5, current 2 (30/50) | former 30, never 23, current 1 (54/100) | — (0/117) | Patient.SmokingStatus |
| Smoking, database code (NOT RESOLVED) | 0 53, conflict 6, 2 2, 3 1 (62/80) | 0 24, conflict 4 (28/37) | 0 29, 2 2, conflict 2, 3 1 (34/43) | 0 117, conflict 7, 2 5, 3 1, 1 1 (131/150) | 0 42, conflict 3 (45/50) | 0 75, 2 5, conflict 4, 3 1, 1 1 (86/100) | 0 50, conflict 2 (52/117) | `initial_history.smoking` |
| Pack-years, database | 2003 1, 40 1 (2/80) | 40 1 (1/37) | 2003 1 (1/43) | 20 1, 2003 1, 40 1 (3/150) | 40 1 (1/50) | 20 1, 2003 1 (2/100) | — (0/117) | `initial_history.packyears` |
| BMI, database (10–80 only) | 28.47 [26.85–28.64] (3/80) | — (0/37) | 28.47 [26.85–28.64] (3/43) | 25.51 [24.76–28.47] (9/150) | — (0/50) | 25.51 [24.76–28.47] (9/100) | — (0/117) | `initial_history.bmi` |
| BMI, BE progression DB | 27.74 [26.2–30.75] (32/80) | 29.27 [25.47–32.21] (18/37) | 27.66 [26.72–28.29] (14/43) | 27.73 [25.85–31.17] (35/150) | 27.72 [24.56–32.45] (20/50) | 27.73 [26.82–29.24] (15/100) | — (0/117) | Patient.Weight / Height² |
| Hiatal hernia, database closest endoscopy | yes 21 (21/80) | yes 12 (12/37) | yes 9 (9/43) | yes 59 (59/150) | yes 23 (23/50) | yes 36 (36/100) | — (0/117) | `endoscopy.hiatusherniapresent` |
|   gap (days) | 5254.0 [3649.0–5849.0] (21/80) | 4529.5 [3339.5–5017.25] (12/37) | 5842.0 [5264.0–6761.0] (9/43) | 3649.0 [2723.0–5006.0] (59/150) | 3471.0 [2654.0–4640.5] (23/50) | 3841.5 [2786.75–5339.75] (36/100) | — (0/117) | `endoscopy.endoscopydate` |
| PPI, database code (no codebook) | conflict 25, 1 10, 2 7, 3 6, 6 1 (49/80) | conflict 15, 1 5, 3 3, 2 2 (25/37) | conflict 10, 1 5, 2 5, 3 3, 6 1 (24/43) | conflict 46, 1 41, 2 13, 3 8, 4 3, 6 1 (112/150) | conflict 20, 1 13, 3 6, 4 2, 2 1 (42/50) | 1 28, conflict 26, 2 12, 3 2, 6 1, 4 1 (70/100) | 1 35, conflict 29, 2 14, 3 8, 4 2 (88/117) | `initial_history.ppi` |
| Family history of BE, database | — (0/80) | — (0/37) | — (0/43) | — (0/150) | — (0/50) | — (0/100) | — (0/117) | `initial_history.fambarretts` |
| Family history of OAC, database | — (0/80) | — (0/37) | — (0/43) | — (0/150) | — (0/50) | — (0/100) | — (0/117) | `initial_history.famoescancer` |

Alcohol (`initial_history.alcoholcurrent`, free text, not categorised) recorded for 7/80 discovery, 13/150 release and 2/117 ACE-B patients. Ethnicity: NOT AVAILABLE (only the OCCAMS lookup `occams_ethnic_category`, no Barrett's participant link). Sex in the Barrett's database export: NOT AVAILABLE (no sex/gender column in any Barrett's DB export table except OCCAMS masterlist _131_gender (OCCAMS cohort, no participant_id link); sex from BE_Progression_Project.db Patient.Gender (SWG) and aceb_sample_counts_per_patient.gender (participant table scrape, ACE-B)).

Database Prague values at the closest endoscopy are more than 365 days from the first sample for 24/24 discovery and 62/62 release patients (all flagged). Database BMI values outside 10–80 (0 or negative): 47 discovery, 101 release, 46 ACE-B. Database age at first sample below 18 years (implausible date of birth): 2 discovery, 2 release.

**Agreement between sources** (patients with both):

| Cohort | Comparison | Agree / both |
|---|---|---|
| discovery | sex, sheet vs BE progression DB | 80/80 |
| discovery | age at diagnosis, sheet vs BE progression DB (±0.5 y) | 80/80 |
| discovery | Prague C / M, sheet vs BE progression DB | 64/64 / 67/67 |
| discovery | smoking, sheet Y/N vs DB never ↔ N, former/current ↔ Y | 43/43 |
| discovery | age at diagnosis, database vs sheet: within 1 y (median |Δ|) | 13/24 (0.8 y) |
| discovery | age at first sample, database vs sheet DOB: within 1 y (median |Δ|) | 34/36 (0.0 y) |
| discovery | patients with sex / smoking only in the BE progression DB | 0 / 0 |
| release | sex, sheet vs BE progression DB | 82/82 |
| release | age at diagnosis, sheet vs BE progression DB (±0.5 y) | 82/82 |
| release | Prague C / M, sheet vs BE progression DB | 66/66 / 69/69 |
| release | smoking, sheet Y/N vs DB never ↔ N, former/current ↔ Y | 44/44 |
| release | age at diagnosis, database vs sheet: within 1 y (median |Δ|) | 12/23 (0.82 y) |
| release | age at first sample, database vs sheet DOB: within 1 y (median |Δ|) | 31/33 (0.0 y) |
| release | patients with sex / smoking only in the BE progression DB | 68 / 40 |

**How missing values are represented** (`initial_history` records of the cohorts' participants; `endoscopy` all rows; `BE_Progression_Project.db` Patient):

| Table.column | NaN/None object | '' | 'None' | 0 | Rows |
|---|---|---|---|---|---|
| initial_history.dob | 0 | 503 | 473 | 0 | 1051 |
| initial_history.datediagnosed | 0 | 526 | 473 | 0 | 1051 |
| initial_history.smoking | 0 | 0 | 473 | 562 | 1051 |
| initial_history.packyears | 0 | 575 | 473 | 0 | 1051 |
| initial_history.praguec | 0 | 532 | 473 | 17 | 1051 |
| initial_history.praguem | 0 | 531 | 473 | 1 | 1051 |
| initial_history.bmi | 0 | 2 | 473 | 536 | 1051 |
| initial_history.heightm | 0 | 536 | 473 | 0 | 1051 |
| initial_history.weightkg | 0 | 534 | 473 | 0 | 1051 |
| initial_history.currentbmi | 0 | 0 | 473 | 578 | 1051 |
| initial_history.alcoholcurrent | 0 | 564 | 473 | 0 | 1051 |
| initial_history.ppi | 0 | 99 | 3 | 0 | 1051 |
| initial_history.fambarretts | 0 | 578 | 473 | 0 | 1051 |
| initial_history.famoescancer | 0 | 578 | 473 | 0 | 1051 |
| endoscopy.barretts_circumference | 0 | 1626 | 691 | 1973 | 14302 |
| endoscopy.barretts_maximum | 0 | 1443 | 698 | 623 | 14302 |
| endoscopy.hiatusherniapresent | 0 | 1916 | 1968 | 4362 | 14302 |
| Patient.Gender | 0 | 0 | 0 | 0 | 165 |
| Patient.AgeAtDiagnosis | 0 | 0 | 0 | 0 | 165 |
| Patient.SmokingStatus | 73 | 0 | 73 | 0 | 165 |
| Patient.Height | 128 | 0 | 0 | 0 | 165 |
| Patient.Weight | 124 | 0 | 0 | 0 | 165 |
| Patient.Circumference | 18 | 0 | 0 | 59 | 165 |
| Patient.Maximal | 15 | 0 | 0 | 0 | 165 |

**Method.** `dm_analyse.py` PART=d3 and `dm_agree.py`. A participant's `initial_history` value is used only when all its records agree; otherwise it is counted as a conflict and left missing. No imputation.
**Sources.** As in the table; `d3.json`, `d3_agree.json`.
**Caveats.** (1) The database endoscopy records start years after the discovery samples (closest gap median about 12 years), so their Prague values describe a later Barrett's segment, not the one at sampling. (2) Every linked patient's closest endoscopy has `hiatusherniapresent` = 1, against 5,581 '1' and 4,362 '0' in the whole table; this may be a form default, as with the zeros in `initial_history`. (3) `BE_Progression_Project.db` reproduces the sheet exactly where both exist and extends it to the validation-sheet patients; it is a project database, not the Barrett's clinical database. (4) ACE-B: age at first sample and endoscopy-dated variables need biopsy dates, which were not read.

### D4. Updated Table 1

Discovery subset by label (37 P, 43 NP) and ACE-B (117, no labels). Median [IQR] (n/N) for numbers; counts (n/N) for categories. Source: sheet = `Demographics_full.csv`; BE progression DB = `BE_Progression_Project.db` (identical to the sheet where both exist); database = Barrett's DB export or its participant-table scrape.

| Variable | Source | Discovery all (80) | Discovery P (37) | Discovery NP (43) | ACE-B (117) |
|---|---|---|---|---|---|
| Age at first sample (years) | sheet | 63.42 [57.2–69.45] (80/80) | 61.23 [56.55–69.22] (37/37) | 65.54 [57.27–69.61] (43/43) | — (0/117) |
| Age at BE diagnosis (years) | sheet | 61.5 [55.0–67.0] (80/80) | 60.0 [55.0–67.0] (37/37) | 63.0 [55.0–66.0] (43/43) | — (0/117) |
| Age at BE diagnosis (years) | database | 63.18 [58.51–68.0] (24/80) | 61.59 [59.49–67.27] (10/37) | 64.89 [57.23–68.41] (14/43) | 59.67 [55.88–64.06] (7/117) |
| Sex | sheet | M 61, F 19 (80/80) | M 29, F 8 (37/37) | M 32, F 11 (43/43) | — (0/117) |
| Sex | database (participant table) | — (0/80) | — (0/37) | — (0/43) | Male 38, Female 14 (52/117) |
| Prague C (cm) | sheet | 0.0 [0.0–2.0] (64/80) | 0.0 [0.0–1.25] (24/37) | 0.0 [0.0–2.0] (40/43) | — (0/117) |
| Prague C (cm), baseline | database | 0.0 [0.0–5.0] (21/80) | 0.0 [0.0–0.0] (10/37) | 4.0 [0.5–5.5] (11/43) | 4.5 [4.0–6.5] (6/117) |
| Prague M (cm) | sheet | 4.0 [3.0–6.0] (67/80) | 4.0 [3.0–6.5] (27/37) | 4.5 [3.0–5.25] (40/43) | — (0/117) |
| Prague M (cm), baseline | database | 5.0 [3.25–6.75] (22/80) | 5.0 [2.5–7.5] (11/37) | 5.0 [4.0–6.0] (11/43) | 6.0 [5.25–7.5] (6/117) |
| Smoking | sheet | Y 33, N 10 (43/80) | Y 17, N 4 (21/37) | Y 16, N 6 (22/43) | — (0/117) |
| Smoking | BE progression DB | former 30, never 10, current 3 (43/80) | former 15, never 4, current 2 (21/37) | former 15, never 6, current 1 (22/43) | — (0/117) |
| Smoking code (not resolved) | database | 0 53, conflict 6, 2 2, 3 1 (62/80) | 0 24, conflict 4 (28/37) | 0 29, 2 2, conflict 2, 3 1 (34/43) | 0 50, conflict 2 (52/117) |
| BMI (10–80) | database | 28.47 [26.85–28.64] (3/80) | — (0/37) | 28.47 [26.85–28.64] (3/43) | — (0/117) |
| BMI | BE progression DB | 27.74 [26.2–30.75] (32/80) | 29.27 [25.47–32.21] (18/37) | 27.66 [26.72–28.29] (14/43) | — (0/117) |
| Hiatal hernia (closest endoscopy, all > 1 y away) | database | yes 21 (21/80) | yes 12 (12/37) | yes 9 (9/43) | — (0/117) |
| PPI code (no codebook) | database | conflict 25, 1 10, 2 7, 3 6, 6 1 (49/80) | conflict 15, 1 5, 3 3, 2 2 (25/37) | conflict 10, 1 5, 2 5, 3 3, 6 1 (24/43) | 1 35, conflict 29, 2 14, 3 8, 4 2 (88/117) |
| Baseline grade (first set C sample) | sheet (`docs/dataset_description.md` item 4) | NDBE 55, LGD 12, ID 11, HGD 2 (80/80) | NDBE 24, LGD 7, ID 4, HGD 2 (37/37) | NDBE 31, ID 7, LGD 5 (43/43) | not read (pathology) |
| Ethnicity, family history | — | NOT AVAILABLE | NOT AVAILABLE | NOT AVAILABLE | NOT AVAILABLE |

### Discrepancies found

- The pre-specified default-value test for code 0 is degenerate: the lowest tercile of record completeness is the 3,024 all-'None' records, where smoking is null rather than 0.
- `BE_Progression_Project.db` sits in the ACE-B metadata folder but holds the SWG / Killcoyne progression project (165 patients); it is read here for SWG patients only, demographic columns only.
- Database dates of birth disagree with the sheet for a few patients (age at first sample below 18 in 2 discovery patients).
- `packyears` holds a year ('2003') for one patient.

### Not done

- The Supplementary Information PDF (`MOESM1`) and Reporting Summary (`MOESM2`) are not on the cluster and were not downloaded; the PMC appendix carries the same supplementary tables.
- The Barrett's database REST API (`api.barrettsdatabase.org.uk`, used by `scripts/export_barretts_db.py`) was not queried for a schema or field definitions; the export code holds none.
- Any mapping of the smoking codes (NOT RESOLVED by the rule) and of the PPI codes (no codebook).
- ACE-B age at first sample, dated Prague and hiatal hernia (biopsy dates not read).

**Interpretation.** The database cannot decode smoking or add dated Prague values for these cohorts; the project database fills sex, age at diagnosis, Prague and smoking for the validation-sheet patients, and ACE-B gains sex for 52 of 117 patients.


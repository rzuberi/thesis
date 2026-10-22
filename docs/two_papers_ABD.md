# Two papers, agent ABD: are the ACE-B patients in the Cambridge Barrett's database?

22 October 2026. Rules: `paper/two_papers/RUN_RULES.md`, with one authorised, outcome-blind exception to "never open ACE-B files": identifier and date columns only. Aggregates only; cells of 1–4 are "<5".

## Plan

1. List the Barrett's database extracts on the cluster with their dates.
2. Link ACE-B patients to database participants in several independent ways, using identifier columns only, and check that the routes agree.
3. For linked patients, count endoscopy episodes from dates only: in total, and before and after the ACE-B procedure dates.
4. Check whether ACE-B material appeared in the database after June 2026.
5. Count overlap with the Killcoyne discovery cohort, the SWG release and agent ERL's scan-request lists.

No pathology, grade, report text, progression, treatment or death field was read for any patient.

## How it was run

Scripts: `scripts/paper_plan/tp_abd_headers.py` (column names only; tokens with digit runs masked), `tp_abd_probe.py` (key formats and date ranges), `tp_abd_link.py` (linkage and counts), `tp_abd_qc.py` (parse check). Each ran as a single `srun -p epyc` job (`tpabd_*`). The row-level link and history tables are at `killcoyne_mm/two_papers_ABD/` on the cluster (chmod 600). The aggregate JSON is at `results/paper_final/two_papers_ABD/aceb_db_linkage.json` on the cluster and is not committed.

**Smoke checks (known numbers reproduced).** 79 of the 80 discovery patients have a database participant ID (data2.md: 79 of 80 link). 25 of the 80 are in `erin_swg_pairs` (data.md: 25). ERL's final scan-request lists have 222 database patients (74 + 148) and 98 ERIN patients (36 + 62), matching `docs/two_papers_ERL.md`. The May-2026 study-number route links 91 of 117 ACE-B patients (`docs/demographics_completion.md`: 91).

## 1. Database extracts and linkage keys

| Extract | Made | Content (ID and date columns used) | Latest date |
|---|---|---|---|
| `SWGCohort/barretts_database_230809.csv` | Aug 2023 (file Nov 2023) | per-patient summary | 2022; not used |
| `barretts_retraining/.../barretts_scrape_20260220_172725/` | REST API, 20 Feb 2026 | pathology (13,400 well-formed rows*, 3,522 participants), endoscopy view (14,087), participant study lists, sample table | report received 10 Feb 2026 |
| `aceb_meta/` May-2026 ID files | 27–28 May 2026, by earlier assistant sessions | study number → participant; PS number → participant | — |
| `barretts_db_export/` (`scripts/export_barretts_db.py`, b211413) | REST API, 21 Aug 2026 | pathology (13,645 reports, 3,581 participants), `endoscopy` and `mat_endoscopy_full` | report received 4 Aug 2026; row update 20 Aug 2026; endoscopy 18 Aug 2026 |

\*The February pathology CSV has unquoted multi-line text. Only rows with numeric report and participant IDs were kept (13,400 of 23,455 lines). The report IDs are then a subset of August's: 248 August-only, 0 February-only. Older 2024 extracts are in `personal/temp_hdd/Archive 02092026/BarrettsDatabase/` (BEST2, endoscopies after 2020); they are superseded and were not used. No extract newer than 21 August 2026 exists. The API token is still on the cluster, so a fresh export could be pulled (not done).

**Keys that work.** The database's own ACE-B enrolment field works best. In the February participant table, 127 participants have a study label of the form "<ACE-B study number> (ACE-B)". So the ACE-B study number (sheet `PatientID`) is stored in the database. The sample's PS accession (sheet `Name`, trailing letter removed) also works: it matches the pathology `specimennumber` or the endoscopy `related_specimennumber`. Sample names in the second format (`99A999999A9`, 41 samples) never match.

| Route (ACE-B patient → participant) | Patients linked (of 117) |
|---|---|
| R1 study number, May-2026 match table (from the database study field) | 91 |
| R2 sample PS accession → Aug-2026 export | 95 |
| R3 sample PS accession → Feb-2026 scrape | 95 |
| R4 May-2026 PS → participant map | 85 |
| **Any route** | **99** (99 distinct participants) |

R1 and the specimen routes agree for all 87 patients that both reach (0 disagreements). <5 patients have more than one candidate participant; each was resolved to the participant supported by the most routes. <5 patients link through R1 only.

## 2. Coverage

117 ACE-B patients and 234 samples are in the sheet; the case list has 153 study numbers, and all 117 sheet patients are on it with dates. **99 of 117 (85%) are found in the database; 18 are not.** All 99 carry the ACE-B study label in the database. At sample level, 185 of 234 sample accessions are present as pathology specimen numbers. The 49 absent are the 41 second-format names and 8 PS names.

## 3. Longitudinal history of the 99 linked patients (dates only)

An episode is a union of endoscopy dates and report-received dates from both extracts, with dates within 14 days merged. The ACE-B date window is from the earlier to the later of the case-list `Date AFI` and `Date WLE`, widened by 14 days on each side. These dates fall in 2017–2020; the AFI–WLE gap has a median of 64 days and is 14 days or less in only <5 of 134 dated cases. Episodes inside the window are the ACE-B procedures themselves.

| Episodes on record | 1 | 2 | 3 | ≥4 | median (IQR) |
|---|---|---|---|---|---|
| Database episodes | 0 | <5 | <5 | 93 | 8 (5–13) |
| Endoscopy-table dates only | <5 | <5 | 9 | 84 | 7 (4–11.5) |
| Report dates only | 0 | <5 | 6 | 91 | 7 (5–12) |
| Database + ERIN episodes (85 patients link to ERIN by accession) | 0 | <5 | <5 | 96 | 9 (6–14) |

Span from first to last database episode: median 7.8 years (IQR 5.2–12.0). By band: 0–5 y 25, 5–10 y 37, >10 y 37. First episode 1996–2019; last 2018–2026.

| Episodes outside the ACE-B window (n = 99) | Database only | Database + ERIN |
|---|---|---|
| ≥1 before | 67 | 75 |
| ≥2 before | 46 | 50 |
| ≥3 before | 38 | 39 |
| ≥1 after | 94 | 95 |
| ≥2 after | 82 | 86 |
| ≥3 after | 60 | 63 |
| ≥1 before and ≥1 after | 64 | 73 |
| ≥3 episodes in total, counting the ACE-B one | 93 | 96 |

## 4. Does the extract post-date June 2026?

Yes. The August export was pulled on 21 August 2026; its latest report was received on 4 August and its latest row update was on 20 August. **But no ACE-B material was added between February and August.** The same 185 ACE-B sample accessions are present in the February 2026 scrape and the August export: 0 August-only, 0 February-only. The ACE-B labels and accessions were already in the database before the PI's June 2026 message. For the 99 linked patients, 10 report rows are new since February; their received or row-update dates put <5 received and 5 updated on or after 1 June 2026. These are routine new rows, not a batch import of 2017–2020 ACE-B reports. Whether the import the PI described went into a research field (for example a research grade) could only be checked by reading pathology fields, which was not done. An export pulled now might show a later import.

## 5. Overlap with other cohorts

| Overlap | ACE-B patients |
|---|---|
| ACE-B `PatientID` string in the discovery IDs or `erin_swg_pairs` | 0 |
| Killcoyne discovery cohort (80) by participant ID or through `erin_swg_pairs` | <5 |
| SWG release (150) by participant ID or through `erin_swg_pairs` | 8 |
| ERL final database scan-request list (222 patients) | 41 |
| ERL final ERIN scan-request list (98 patients) | 31 |

ERL list membership is counted over the whole list. The `role` column was not read.

## 6. Statement for the registration (fields read)

On 22 October 2026, an outcome-blind check linked ACE-B patients to the Cambridge Barrett's database. It read only these columns:
- ACE-B sample sheet: `Batch`, `Name`, `PatientID`.
- ACE-B case list: `Study Number`, `Date AFI`, `Date WLE`.
- Two May-2026 identifier maps: study number → participant ID, and PS number → participant ID.
- Database extracts of February and August 2026: participant ID, pathology report ID, specimen number, report received date and row-update date; endoscopy date and related specimen number; study-enrolment labels.
- ERIN archive: `anon_id`, `CaseName`, collection date.
- Patient-ID columns of the discovery, release and ERL scan-request files.

No pathology, histology, grade, report text, progression, treatment or death field was read for any patient, and only counts were reported.

## What this changes

ACE-B is a longitudinal cohort in the database, not a one-endoscopy cohort. 99 of the 117 patients are linked. 93 of them have at least 3 episodes on record, 46 have at least 2 episodes before the ACE-B procedures, and 82 have at least 2 after. This makes a longitudinal "memory" test on ACE-B feasible, but it needs pre-ACE-B slides, and only the ACE-B blocks are in hand. Two points for the registration:

1. **Overlap with ERL's validation list.** 41 of ERL's 222 database scan-request patients and 31 of its 98 ERIN patients are ACE-B patients. ERL assigned their progressor/non-progressor roles from database grades. The registration must therefore say how ACE-B and the archive test are kept separate, for example by excluding ACE-B patients from the archive list. It must also disclose that ERL's database-wide outcome derivation covered these patients, though not as ACE-B patients.
2. **Earlier lookups and wording.** The `aceb_meta/` folder holds May-2026 assistant outputs that looked ACE-B patients up in the database. Their column headers include `highestgradedysconf_dysplasia_grade`, `reporttext_excerpt`, `progressor` and endoscopy `report`. Only the column names were read here. The draft's sentence that Rehan "has not looked up any ACE-B patient there" should be reworded to disclose these files. Also, during this run, the ACE-B study numbers (database study labels) were shown once in the assistant session. They were identifiers only; no pathology or outcome value was shown.

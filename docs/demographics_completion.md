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

(appended in a later commit)

# Killcoyne 2020 reconciliation: our 0.800 vs their 0.87 (copy number only)

Status: PRE-SPECIFICATION. Nothing below has been run. Results are appended in a later commit; this section is not edited afterwards.

## Question

Our R2 faithfulness retrain gave patient AUROC 0.800 against sheet status (82 discovery patients, 504 rows; `results/paper_plan/round3_lopo.json`, `scripts/paper_plan/pr3_lopo.py`, commit 6976646). Killcoyne et al. 2020 (Nat Med 26:1726) report a leave-one-patient-out (LOPO) AUC of 0.87 at 50 kb. The user quotes 0.8713. We have the same sequencing data. The aim is to find which analysis choices take one number to the other, using copy number only.

## Facts fixed before running (from the paper, the package and the data)

- Paper, Methods: 777 samples sequenced, 773 pass QC, 88 patients (45 progressors); QDNAseq 50 kb; per-sample weighted mean of segmented values per 5-Mb window; windows mean-standardised "across the entire cohort"; arm means; each window adjusted by window minus arm; 589 windows + 44 arms; cx = count of windows beyond 2 s.d.; glmnet elastic net, α = 0.9 chosen; 5-fold patient-grouped CV repeated 10×; LOPO "to generate predictions for all samples"; AUC with pROC.
- Paper, Extended Data Fig. 2: per-sample AUC 0.87; patient mean 0.87; patient max 0.84; a model without HGD/IMC samples (n = 711) gives similar AUC.
- Paper, Extended Data Fig. 9: 50 kb LOPO AUC 0.87, validation 0.84.
- The unit of the published 0.87 is the sample (773 samples, HGD/IMC included, label = the patient's P/NP status). Our 0.800 is a patient-level max over 504 strict pre-event rows. The two numbers therefore differ in unit and in population before they differ in method.
- Supplementary MOESM4, sheet "Supporting data for Figure 2a": 773 rows with Samplename, Probability, log(Relative Risk), Risk class (published LOPO outputs).
- Package gerstung-lab/BarrettsProgressionRisk (cloned on the cluster): `segmentRawData` (default gamma2 250, 50 kb, cutoff 0.008), `tileSegments`, `subtractArms`, `scoreCX`, `predictRiskFromSegments`, internal fitted glmnet `be_model` with its tile/arm/cx means and s.d.
- Our data: per-sample QDNAseq raw and fitted 50 kb read counts (hg38, 61,776 bins) for all 777 sheet samples under `SWGCohort/copy_number_hg38/train/perPatient/50kb/`; sheet `sWGS_777_samples_cleaned_202401_Leanne_fullDetails (3) (1).csv` gives Status P/NP and the columns Set (Training 619 / Test 158), excluded (119 flagged), remove (17 flagged), Pathology.

## Plans

**A0. Their claim from their own outputs.** Rank AUROC of the published Probability against sheet Status: per sample on the 773 rows (3 and 4 decimals, to locate 0.8713); patient mean and patient max over the 88 patients; the same restricted to 711 non-HGD/IMC samples; and on the 82 patients / 504 release rows (known 0.873, as a check). Patient bootstrap 95% CI (2,000, `RandomState(0)`), label-permutation p (2,000, seed 0) on fixed scores.

**A. Their frozen model on our counts.** Run the package end to end on our raw and fitted counts for the 773 published samples, segmenting per patient as the package does, package defaults except `build='hg38'`, then `predictRiskFromSegments` with the internal `be_model`. Report the per-sample probability against the published probability (Spearman, n matched), and per-sample / patient-mean / patient-max AUROC against sheet status. This model was trained on these samples, so A is a pipeline-fidelity check, not a performance estimate. If tile counts differ between hg38 and the model's hg19 tiles, report the count and use the tiles present in both; state it.

**B. Faithful LOPO retrain.** R glmnet on the package features (tiles, arm-adjusted tiles, arms, cx) computed from our counts in A; all 773 samples; label = patient Status; standardisation over the whole cohort as in the paper; α = 0.9; for each left-out patient, λ by `cv.glmnet(type.measure='class')` with 5 patient-grouped folds repeated 10× (fold patients assigned with `set.seed(r)`, r = 1..10), averaging the CV curves and taking λ at the minimum. Report per-sample, patient-mean and patient-max AUROC against sheet status, and Spearman with the published probability.

**C. Brute-force grid.** All combinations of:

1. Sample set: 773 (all published); 711 (773 minus HGD/IMC); release discovery rows (504, strict pre-event).
2. Features: package features from our counts (B); the release 632-feature table (`load_cnv_matrix`).
3. Standardisation: whole cohort (paper); training patients only.
4. α ∈ {0.5, 0.7, 0.9, 1.0}.
5. λ rule: class-error min; class-error 1-s.e.; deviance min; a single λ chosen once by CV on the full cohort and reused for every left-out patient (not fold-honest); the published `be_model` λ.

Each configuration is scored in every evaluation unit: per sample, patient mean, patient max; on all its patients, and on the 82 discovery patients. The whole grid is reported. The configuration closest to the published outputs is identified by per-sample AUROC and by Spearman with the published probability. Choosing it from the grid is a post hoc selection and is labelled as such.

Pre-specified criterion: a configuration "reproduces" the published result if its per-sample AUROC on the 773 samples is within ±0.010 of the A0 per-sample value and its row Spearman with the published probability is ≥ 0.80.

**D. Reconciliation statement.** A step table from our 0.800 to the published value, moving one factor at a time along the path closest to the paper (unit and population, then features, then standardisation, then λ rule, then α), with the AUROC after each step. One line of interpretation at most.

## Conventions

Rank AUROC to 3 decimals (A0 also 4). Patient bootstrap CIs (2,000, `RandomState(0)`) for A0, A, B and the D steps. Label-permutation p on fixed scores (2,000, seed 0) for A0, A and B; permutation with retraining is NOT AVAILABLE (cost). Nothing in the frozen release is retrained or overwritten; the new fits exist only for this reconciliation.

## Outputs

- Scripts `scripts/paper_plan/`: `kr_published.py` (A0), `kr_package.R` (A and package features), `kr_lopo.R` (B, C; sharded by `SHARD_ID`/`N_SHARDS`), `kr_merge.py`, `kr_render.py`, `kr_check_report.py`.
- Results `results/paper_final/killcoyne_reconcile.json` (aggregates only).
- Row-level outputs stay on the cluster under `feasibility/paper_plan/killcoyne/`.

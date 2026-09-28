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

---

## Results

Sources: `results/paper_final/killcoyne_reconcile.json` · scripts `scripts/paper_plan/kr_*.{py,R}` · results commit 73c1d48. Row-level outputs on the cluster under `feasibility/paper_plan/killcoyne/`.

### Status

| Item | Status |
|---|---|
| A0 | DONE |
| A | DONE |
| B | DONE |
| C | PARTIAL (release features exist for release rows only; release features x 773 / 711 NOT AVAILABLE) |
| D | DONE |

### A0. Published probabilities against sheet status

| Population | Samples | Patients (P) | Per sample | Patient mean | Patient max |
|---|---|---|---|---|---|
| All 773 published | 773 | 88 (45) | 0.8651 [0.801, 0.925] | 0.912 [0.854, 0.964] | 0.919 [0.854, 0.970] |
| Without HGD/IMC samples | 712 | 87 (44) | 0.8474 [0.769, 0.915] | 0.888 [0.815, 0.951] | 0.859 [0.777, 0.934] |
| Our 500 release rows (82 patients) | 500 | 82 (39) | 0.8205 [0.724, 0.904] | 0.900 [0.828, 0.959] | 0.873 [0.797, 0.941] |
| Sheet Set = Training | 615 | 68 (35) | 0.8704 [0.790, 0.935] | 0.928 [0.861, 0.978] | 0.949 [0.891, 0.990] |
| Sheet excluded = 0 | 654 | 83 (40) | 0.8645 [0.785, 0.927] | 0.911 [0.846, 0.963] | 0.912 [0.842, 0.968] |
| Sheet remove = 0 | 756 | 88 (45) | 0.8609 [0.794, 0.922] | 0.912 [0.855, 0.964] | 0.919 [0.854, 0.970] |

Label-permutation p is 0.0005 for every row above. No population gives 0.8713; the value closest to the quoted 0.8713 is the patient-max AUROC on our 82 patients, 0.873.

### A. Their frozen model on our counts

Segmented 773 of 773 samples; 759 pass the package QC (varMAD ≤ 0.008). The model was trained on these samples, so this is a fidelity check.

| Input | Samples | Per sample | Patient mean | Patient max | Spearman vs published |
|---|---|---|---|---|---|
| Our counts, all segmented | 773 | 0.920 [0.883, 0.949] | 0.933 | 0.936 [0.879, 0.980] | 0.642 |
| Our counts, QC pass | 759 | 0.923 | 0.934 | 0.944 | 0.649 |
| Our counts, release rows | 490 | 0.928 [0.886, 0.960] | 0.940 | 0.932 [0.877, 0.975] | 0.522 |
| Their shipped training matrix (in sample) | 773 | 0.998 | 1.000 | 0.996 | 0.860 |

Row alignment of the shipped matrix to our samples [post hoc]: method hungarian; mean row correlation of the aligned pairs 0.7503 (random pairing 0.0118); candidate orders {'sheet_order': 0.0192, 'published_table_order': 0.0424, 'patient_numeric_then_sheet': 0.0908, 'patient_string_then_sheet': 0.0429, 'sample_name_sorted': 0.0456}; aligned rows form 98 patient runs over 88 patients.

### B. Faithful LOPO retrain (package features from our counts, 773 samples, α 0.9, class-error λ min)

| Evaluation | Samples | Per sample | Patient mean | Patient max | Spearman vs published |
|---|---|---|---|---|---|
| All 773 | 773 | 0.852 [0.778, 0.911] | 0.841 [0.749, 0.913] | 0.886 [0.817, 0.951] | 0.721 |
| Release rows | 490 | 0.772 [0.669, 0.868] | 0.813 [0.709, 0.898] | 0.824 [0.729, 0.906] | 0.657 |

Permutation p (all 773, per sample / patient max): 0.0005 / 0.0005.

### C. Grid (every configuration and λ rule)

per-sample AUROC on 773 within +/-0.010 of 0.8651 and Spearman with published >= 0.80. Rows tagged post hoc were added after the pre-specification, from the shipped model object. Picking a best row from this grid is a post hoc selection.

| cfg | tag | set | features | standardisation | glmnet standardize | nλ | α | λ rule | own per sample | own patient max | 82 patients max | release rows per sample | release rows max | Spearman vs published | reproduces |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | prespec | s773 | pkg | cohort | True | 100 | 0.9 | class_1se | 0.820 | 0.882 | 0.903 | 0.712 | 0.823 | 0.710 | False |
| 0 | prespec | s773 | pkg | cohort | True | 100 | 0.9 | class_min | 0.852 | 0.886 | 0.914 | 0.772 | 0.824 | 0.721 | False |
| 0 | prespec | s773 | pkg | cohort | True | 100 | 0.9 | dev_1se | 0.806 | 0.877 | 0.899 | 0.696 | 0.819 | 0.700 | False |
| 0 | prespec | s773 | pkg | cohort | True | 100 | 0.9 | dev_min | 0.861 | 0.921 | 0.951 | 0.782 | 0.862 | 0.743 | False |
| 0 | prespec | s773 | pkg | cohort | True | 100 | 0.9 | global | 0.858 | 0.888 | 0.912 | 0.779 | 0.847 | 0.727 | False |
| 0 | prespec | s773 | pkg | cohort | True | 100 | 0.9 | published | 0.856 | 0.885 | 0.912 | 0.777 | 0.843 | 0.726 | False |
| 1 | prespec | s773 | pkg | cohort | True | 100 | 0.5 | class_1se | 0.823 | 0.888 | 0.910 | 0.715 | 0.822 | 0.723 | False |
| 1 | prespec | s773 | pkg | cohort | True | 100 | 0.5 | class_min | 0.864 | 0.904 | 0.927 | 0.781 | 0.849 | 0.747 | False |
| 1 | prespec | s773 | pkg | cohort | True | 100 | 0.5 | dev_1se | 0.826 | 0.895 | 0.918 | 0.733 | 0.832 | 0.739 | False |
| 1 | prespec | s773 | pkg | cohort | True | 100 | 0.5 | dev_min | 0.865 | 0.925 | 0.949 | 0.788 | 0.866 | 0.752 | False |
| 1 | prespec | s773 | pkg | cohort | True | 100 | 0.5 | global | 0.874 | 0.928 | 0.955 | 0.801 | 0.877 | 0.756 | False |
| 1 | prespec | s773 | pkg | cohort | True | 100 | 0.5 | published | 0.858 | 0.898 | 0.917 | 0.781 | 0.857 | 0.750 | False |
| 2 | prespec | s773 | pkg | cohort | True | 100 | 0.7 | class_1se | 0.823 | 0.888 | 0.911 | 0.717 | 0.829 | 0.716 | False |
| 2 | prespec | s773 | pkg | cohort | True | 100 | 0.7 | class_min | 0.855 | 0.897 | 0.924 | 0.775 | 0.839 | 0.735 | False |
| 2 | prespec | s773 | pkg | cohort | True | 100 | 0.7 | dev_1se | 0.815 | 0.885 | 0.911 | 0.711 | 0.826 | 0.719 | False |
| 2 | prespec | s773 | pkg | cohort | True | 100 | 0.7 | dev_min | 0.860 | 0.917 | 0.946 | 0.781 | 0.864 | 0.744 | False |
| 2 | prespec | s773 | pkg | cohort | True | 100 | 0.7 | global | 0.861 | 0.896 | 0.920 | 0.782 | 0.853 | 0.738 | False |
| 2 | prespec | s773 | pkg | cohort | True | 100 | 0.7 | published | 0.860 | 0.891 | 0.915 | 0.781 | 0.849 | 0.738 | False |
| 3 | prespec | s773 | pkg | cohort | True | 100 | 1.0 | class_1se | 0.820 | 0.881 | 0.903 | 0.715 | 0.826 | 0.701 | False |
| 3 | prespec | s773 | pkg | cohort | True | 100 | 1.0 | class_min | 0.855 | 0.875 | 0.905 | 0.775 | 0.815 | 0.721 | False |
| 3 | prespec | s773 | pkg | cohort | True | 100 | 1.0 | dev_1se | 0.804 | 0.876 | 0.899 | 0.692 | 0.822 | 0.691 | False |
| 3 | prespec | s773 | pkg | cohort | True | 100 | 1.0 | dev_min | 0.863 | 0.922 | 0.953 | 0.784 | 0.868 | 0.745 | False |
| 3 | prespec | s773 | pkg | cohort | True | 100 | 1.0 | global | 0.858 | 0.885 | 0.909 | 0.781 | 0.845 | 0.725 | False |
| 3 | prespec | s773 | pkg | cohort | True | 100 | 1.0 | published | 0.854 | 0.885 | 0.914 | 0.774 | 0.835 | 0.722 | False |
| 4 | prespec | s773 | pkg | train | True | 100 | 0.9 | class_1se | 0.820 | 0.890 | 0.914 | 0.712 | 0.831 | 0.705 | False |
| 4 | prespec | s773 | pkg | train | True | 100 | 0.9 | class_min | 0.849 | 0.882 | 0.911 | 0.772 | 0.819 | 0.720 | False |
| 4 | prespec | s773 | pkg | train | True | 100 | 0.9 | dev_1se | 0.809 | 0.883 | 0.907 | 0.698 | 0.826 | 0.700 | False |
| 4 | prespec | s773 | pkg | train | True | 100 | 0.9 | dev_min | 0.860 | 0.922 | 0.952 | 0.782 | 0.867 | 0.738 | False |
| 4 | prespec | s773 | pkg | train | True | 100 | 0.9 | global | 0.855 | 0.886 | 0.913 | 0.782 | 0.847 | 0.723 | False |
| 4 | prespec | s773 | pkg | train | True | 100 | 0.9 | published | 0.853 | 0.886 | 0.914 | 0.781 | 0.844 | 0.722 | False |
| 5 | prespec | s773 | pkg | train | True | 100 | 0.5 | class_1se | 0.826 | 0.898 | 0.922 | 0.717 | 0.834 | 0.723 | False |
| 5 | prespec | s773 | pkg | train | True | 100 | 0.5 | class_min | 0.863 | 0.906 | 0.931 | 0.783 | 0.849 | 0.747 | False |
| 5 | prespec | s773 | pkg | train | True | 100 | 0.5 | dev_1se | 0.830 | 0.901 | 0.925 | 0.735 | 0.838 | 0.740 | False |
| 5 | prespec | s773 | pkg | train | True | 100 | 0.5 | dev_min | 0.863 | 0.921 | 0.946 | 0.787 | 0.863 | 0.746 | False |
| 5 | prespec | s773 | pkg | train | True | 100 | 0.5 | global | 0.873 | 0.928 | 0.955 | 0.802 | 0.873 | 0.751 | False |
| 5 | prespec | s773 | pkg | train | True | 100 | 0.5 | published | 0.855 | 0.900 | 0.919 | 0.783 | 0.856 | 0.744 | False |
| 6 | prespec | s773 | pkg | train | True | 100 | 0.7 | class_1se | 0.824 | 0.894 | 0.917 | 0.714 | 0.837 | 0.717 | False |
| 6 | prespec | s773 | pkg | train | True | 100 | 0.7 | class_min | 0.850 | 0.896 | 0.924 | 0.770 | 0.844 | 0.730 | False |
| 6 | prespec | s773 | pkg | train | True | 100 | 0.7 | dev_1se | 0.819 | 0.894 | 0.920 | 0.715 | 0.833 | 0.720 | False |
| 6 | prespec | s773 | pkg | train | True | 100 | 0.7 | dev_min | 0.859 | 0.918 | 0.948 | 0.782 | 0.863 | 0.740 | False |
| 6 | prespec | s773 | pkg | train | True | 100 | 0.7 | global | 0.857 | 0.895 | 0.920 | 0.784 | 0.853 | 0.732 | False |
| 6 | prespec | s773 | pkg | train | True | 100 | 0.7 | published | 0.856 | 0.894 | 0.918 | 0.783 | 0.850 | 0.733 | False |
| 7 | prespec | s773 | pkg | train | True | 100 | 1.0 | class_1se | 0.819 | 0.888 | 0.911 | 0.711 | 0.829 | 0.700 | False |
| 7 | prespec | s773 | pkg | train | True | 100 | 1.0 | class_min | 0.850 | 0.879 | 0.909 | 0.771 | 0.821 | 0.715 | False |
| 7 | prespec | s773 | pkg | train | True | 100 | 1.0 | dev_1se | 0.806 | 0.884 | 0.909 | 0.693 | 0.831 | 0.692 | False |
| 7 | prespec | s773 | pkg | train | True | 100 | 1.0 | dev_min | 0.860 | 0.921 | 0.953 | 0.785 | 0.870 | 0.739 | False |
| 7 | prespec | s773 | pkg | train | True | 100 | 1.0 | global | 0.855 | 0.885 | 0.909 | 0.784 | 0.846 | 0.722 | False |
| 7 | prespec | s773 | pkg | train | True | 100 | 1.0 | published | 0.852 | 0.884 | 0.914 | 0.779 | 0.839 | 0.719 | False |
| 8 | prespec | s711 | pkg | cohort | True | 100 | 0.9 | class_1se | 0.780 | 0.814 | 0.842 | 0.699 | 0.793 | 0.632 | — |
| 8 | prespec | s711 | pkg | cohort | True | 100 | 0.9 | class_min | 0.812 | 0.855 | 0.871 | 0.737 | 0.850 | 0.629 | — |
| 8 | prespec | s711 | pkg | cohort | True | 100 | 0.9 | dev_1se | 0.780 | 0.821 | 0.849 | 0.699 | 0.795 | 0.628 | — |
| 8 | prespec | s711 | pkg | cohort | True | 100 | 0.9 | dev_min | 0.819 | 0.860 | 0.887 | 0.746 | 0.843 | 0.682 | — |
| 8 | prespec | s711 | pkg | cohort | True | 100 | 0.9 | global | 0.842 | 0.851 | 0.866 | 0.793 | 0.844 | 0.696 | — |
| 8 | prespec | s711 | pkg | cohort | True | 100 | 0.9 | published | 0.832 | 0.848 | 0.871 | 0.765 | 0.848 | 0.700 | — |
| 9 | prespec | s711 | pkg | cohort | True | 100 | 0.5 | class_1se | 0.793 | 0.835 | 0.863 | 0.713 | 0.812 | 0.656 | — |
| 9 | prespec | s711 | pkg | cohort | True | 100 | 0.5 | class_min | 0.806 | 0.855 | 0.873 | 0.733 | 0.840 | 0.633 | — |
| 9 | prespec | s711 | pkg | cohort | True | 100 | 0.5 | dev_1se | 0.802 | 0.837 | 0.865 | 0.732 | 0.825 | 0.671 | — |
| 9 | prespec | s711 | pkg | cohort | True | 100 | 0.5 | dev_min | 0.847 | 0.877 | 0.900 | 0.785 | 0.877 | 0.706 | — |
| 9 | prespec | s711 | pkg | cohort | True | 100 | 0.5 | global | 0.842 | 0.868 | 0.883 | 0.788 | 0.862 | 0.713 | — |
| 9 | prespec | s711 | pkg | cohort | True | 100 | 0.5 | published | 0.834 | 0.860 | 0.877 | 0.770 | 0.853 | 0.717 | — |
| 10 | prespec | s711 | pkg | cohort | True | 100 | 0.7 | class_1se | 0.791 | 0.822 | 0.853 | 0.713 | 0.805 | 0.644 | — |
| 10 | prespec | s711 | pkg | cohort | True | 100 | 0.7 | class_min | 0.808 | 0.847 | 0.865 | 0.740 | 0.841 | 0.620 | — |
| 10 | prespec | s711 | pkg | cohort | True | 100 | 0.7 | dev_1se | 0.789 | 0.826 | 0.855 | 0.715 | 0.811 | 0.650 | — |
| 10 | prespec | s711 | pkg | cohort | True | 100 | 0.7 | dev_min | 0.836 | 0.873 | 0.899 | 0.766 | 0.863 | 0.697 | — |
| 10 | prespec | s711 | pkg | cohort | True | 100 | 0.7 | global | 0.844 | 0.864 | 0.879 | 0.793 | 0.853 | 0.707 | — |
| 10 | prespec | s711 | pkg | cohort | True | 100 | 0.7 | published | 0.828 | 0.850 | 0.868 | 0.760 | 0.844 | 0.705 | — |
| 11 | prespec | s711 | pkg | cohort | True | 100 | 1.0 | class_1se | 0.769 | 0.805 | 0.832 | 0.685 | 0.782 | 0.610 | — |
| 11 | prespec | s711 | pkg | cohort | True | 100 | 1.0 | class_min | 0.814 | 0.841 | 0.862 | 0.742 | 0.834 | 0.654 | — |
| 11 | prespec | s711 | pkg | cohort | True | 100 | 1.0 | dev_1se | 0.774 | 0.817 | 0.845 | 0.691 | 0.788 | 0.616 | — |
| 11 | prespec | s711 | pkg | cohort | True | 100 | 1.0 | dev_min | 0.814 | 0.857 | 0.884 | 0.740 | 0.841 | 0.676 | — |
| 11 | prespec | s711 | pkg | cohort | True | 100 | 1.0 | global | 0.831 | 0.841 | 0.864 | 0.765 | 0.844 | 0.697 | — |
| 11 | prespec | s711 | pkg | cohort | True | 100 | 1.0 | published | 0.833 | 0.854 | 0.876 | 0.766 | 0.852 | 0.697 | — |
| 12 | prespec | s711 | pkg | train | True | 100 | 0.9 | class_1se | 0.783 | 0.816 | 0.843 | 0.702 | 0.792 | 0.633 | — |
| 12 | prespec | s711 | pkg | train | True | 100 | 0.9 | class_min | 0.816 | 0.850 | 0.868 | 0.748 | 0.848 | 0.636 | — |
| 12 | prespec | s711 | pkg | train | True | 100 | 0.9 | dev_1se | 0.783 | 0.820 | 0.847 | 0.703 | 0.799 | 0.631 | — |
| 12 | prespec | s711 | pkg | train | True | 100 | 0.9 | dev_min | 0.820 | 0.863 | 0.890 | 0.747 | 0.849 | 0.683 | — |
| 12 | prespec | s711 | pkg | train | True | 100 | 0.9 | global | 0.839 | 0.853 | 0.869 | 0.795 | 0.844 | 0.692 | — |
| 12 | prespec | s711 | pkg | train | True | 100 | 0.9 | published | 0.828 | 0.849 | 0.872 | 0.767 | 0.850 | 0.697 | — |
| 13 | prespec | s711 | pkg | train | True | 100 | 0.5 | class_1se | 0.797 | 0.840 | 0.871 | 0.719 | 0.822 | 0.658 | — |
| 13 | prespec | s711 | pkg | train | True | 100 | 0.5 | class_min | 0.814 | 0.854 | 0.872 | 0.753 | 0.841 | 0.629 | — |
| 13 | prespec | s711 | pkg | train | True | 100 | 0.5 | dev_1se | 0.804 | 0.842 | 0.871 | 0.732 | 0.834 | 0.673 | — |
| 13 | prespec | s711 | pkg | train | True | 100 | 0.5 | dev_min | 0.846 | 0.876 | 0.900 | 0.785 | 0.877 | 0.706 | — |
| 13 | prespec | s711 | pkg | train | True | 100 | 0.5 | global | 0.841 | 0.868 | 0.883 | 0.789 | 0.863 | 0.710 | — |
| 13 | prespec | s711 | pkg | train | True | 100 | 0.5 | published | 0.832 | 0.860 | 0.877 | 0.772 | 0.857 | 0.712 | — |
| 14 | prespec | s711 | pkg | train | True | 100 | 0.7 | class_1se | 0.793 | 0.827 | 0.857 | 0.713 | 0.801 | 0.646 | — |
| 14 | prespec | s711 | pkg | train | True | 100 | 0.7 | class_min | 0.801 | 0.847 | 0.863 | 0.742 | 0.846 | 0.617 | — |
| 14 | prespec | s711 | pkg | train | True | 100 | 0.7 | dev_1se | 0.793 | 0.831 | 0.860 | 0.718 | 0.814 | 0.654 | — |
| 14 | prespec | s711 | pkg | train | True | 100 | 0.7 | dev_min | 0.832 | 0.873 | 0.899 | 0.765 | 0.865 | 0.691 | — |
| 14 | prespec | s711 | pkg | train | True | 100 | 0.7 | global | 0.842 | 0.862 | 0.877 | 0.794 | 0.853 | 0.702 | — |
| 14 | prespec | s711 | pkg | train | True | 100 | 0.7 | published | 0.826 | 0.853 | 0.872 | 0.763 | 0.847 | 0.702 | — |
| 15 | prespec | s711 | pkg | train | True | 100 | 1.0 | class_1se | 0.771 | 0.806 | 0.834 | 0.685 | 0.781 | 0.615 | — |
| 15 | prespec | s711 | pkg | train | True | 100 | 1.0 | class_min | 0.810 | 0.842 | 0.863 | 0.740 | 0.836 | 0.649 | — |
| 15 | prespec | s711 | pkg | train | True | 100 | 1.0 | dev_1se | 0.777 | 0.816 | 0.844 | 0.695 | 0.791 | 0.622 | — |
| 15 | prespec | s711 | pkg | train | True | 100 | 1.0 | dev_min | 0.814 | 0.859 | 0.887 | 0.740 | 0.846 | 0.679 | — |
| 15 | prespec | s711 | pkg | train | True | 100 | 1.0 | global | 0.827 | 0.844 | 0.868 | 0.767 | 0.847 | 0.694 | — |
| 15 | prespec | s711 | pkg | train | True | 100 | 1.0 | published | 0.829 | 0.849 | 0.874 | 0.768 | 0.851 | 0.696 | — |
| 16 | prespec | rel504 | pkg | cohort | True | 100 | 0.9 | class_1se | 0.493 | 0.633 | 0.633 | 0.493 | 0.633 | 0.117 | — |
| 16 | prespec | rel504 | pkg | cohort | True | 100 | 0.9 | class_min | 0.681 | 0.792 | 0.792 | 0.681 | 0.792 | 0.538 | — |
| 16 | prespec | rel504 | pkg | cohort | True | 100 | 0.9 | dev_1se | 0.512 | 0.634 | 0.634 | 0.512 | 0.634 | 0.120 | — |
| 16 | prespec | rel504 | pkg | cohort | True | 100 | 0.9 | dev_min | 0.717 | 0.810 | 0.810 | 0.717 | 0.810 | 0.586 | — |
| 16 | prespec | rel504 | pkg | cohort | True | 100 | 0.9 | global | 0.728 | 0.806 | 0.806 | 0.728 | 0.806 | 0.574 | — |
| 16 | prespec | rel504 | pkg | cohort | True | 100 | 0.9 | published | 0.725 | 0.818 | 0.818 | 0.725 | 0.818 | 0.619 | — |
| 17 | prespec | rel504 | pkg | cohort | True | 100 | 0.5 | class_1se | 0.558 | 0.681 | 0.681 | 0.558 | 0.681 | 0.190 | — |
| 17 | prespec | rel504 | pkg | cohort | True | 100 | 0.5 | class_min | 0.667 | 0.813 | 0.813 | 0.667 | 0.813 | 0.572 | — |
| 17 | prespec | rel504 | pkg | cohort | True | 100 | 0.5 | dev_1se | 0.570 | 0.678 | 0.678 | 0.570 | 0.678 | 0.224 | — |
| 17 | prespec | rel504 | pkg | cohort | True | 100 | 0.5 | dev_min | 0.700 | 0.810 | 0.810 | 0.700 | 0.810 | 0.632 | — |
| 17 | prespec | rel504 | pkg | cohort | True | 100 | 0.5 | global | 0.738 | 0.823 | 0.823 | 0.738 | 0.823 | 0.596 | — |
| 17 | prespec | rel504 | pkg | cohort | True | 100 | 0.5 | published | 0.764 | 0.873 | 0.873 | 0.764 | 0.873 | 0.666 | — |
| 18 | prespec | rel504 | pkg | cohort | True | 100 | 0.7 | class_1se | 0.525 | 0.655 | 0.655 | 0.525 | 0.655 | 0.158 | — |
| 18 | prespec | rel504 | pkg | cohort | True | 100 | 0.7 | class_min | 0.689 | 0.784 | 0.784 | 0.689 | 0.784 | 0.560 | — |
| 18 | prespec | rel504 | pkg | cohort | True | 100 | 0.7 | dev_1se | 0.549 | 0.662 | 0.662 | 0.549 | 0.662 | 0.182 | — |
| 18 | prespec | rel504 | pkg | cohort | True | 100 | 0.7 | dev_min | 0.713 | 0.809 | 0.809 | 0.713 | 0.809 | 0.619 | — |
| 18 | prespec | rel504 | pkg | cohort | True | 100 | 0.7 | global | 0.738 | 0.820 | 0.820 | 0.738 | 0.820 | 0.599 | — |
| 18 | prespec | rel504 | pkg | cohort | True | 100 | 0.7 | published | 0.743 | 0.844 | 0.844 | 0.743 | 0.844 | 0.640 | — |
| 19 | prespec | rel504 | pkg | cohort | True | 100 | 1.0 | class_1se | 0.469 | 0.619 | 0.619 | 0.469 | 0.619 | 0.108 | — |
| 19 | prespec | rel504 | pkg | cohort | True | 100 | 1.0 | class_min | 0.679 | 0.790 | 0.790 | 0.679 | 0.790 | 0.523 | — |
| 19 | prespec | rel504 | pkg | cohort | True | 100 | 1.0 | dev_1se | 0.488 | 0.615 | 0.615 | 0.488 | 0.615 | 0.091 | — |
| 19 | prespec | rel504 | pkg | cohort | True | 100 | 1.0 | dev_min | 0.713 | 0.803 | 0.803 | 0.713 | 0.803 | 0.575 | — |
| 19 | prespec | rel504 | pkg | cohort | True | 100 | 1.0 | global | 0.733 | 0.809 | 0.809 | 0.733 | 0.809 | 0.580 | — |
| 19 | prespec | rel504 | pkg | cohort | True | 100 | 1.0 | published | 0.721 | 0.808 | 0.808 | 0.721 | 0.808 | 0.613 | — |
| 20 | prespec | rel504 | pkg | train | True | 100 | 0.9 | class_1se | 0.496 | 0.633 | 0.633 | 0.496 | 0.633 | 0.131 | — |
| 20 | prespec | rel504 | pkg | train | True | 100 | 0.9 | class_min | 0.682 | 0.798 | 0.798 | 0.682 | 0.798 | 0.539 | — |
| 20 | prespec | rel504 | pkg | train | True | 100 | 0.9 | dev_1se | 0.511 | 0.628 | 0.628 | 0.511 | 0.628 | 0.129 | — |
| 20 | prespec | rel504 | pkg | train | True | 100 | 0.9 | dev_min | 0.717 | 0.806 | 0.806 | 0.717 | 0.806 | 0.580 | — |
| 20 | prespec | rel504 | pkg | train | True | 100 | 0.9 | global | 0.727 | 0.807 | 0.807 | 0.727 | 0.807 | 0.569 | — |
| 20 | prespec | rel504 | pkg | train | True | 100 | 0.9 | published | 0.724 | 0.819 | 0.819 | 0.724 | 0.819 | 0.614 | — |
| 21 | prespec | rel504 | pkg | train | True | 100 | 0.5 | class_1se | 0.556 | 0.678 | 0.678 | 0.556 | 0.678 | 0.185 | — |
| 21 | prespec | rel504 | pkg | train | True | 100 | 0.5 | class_min | 0.663 | 0.805 | 0.805 | 0.663 | 0.805 | 0.576 | — |
| 21 | prespec | rel504 | pkg | train | True | 100 | 0.5 | dev_1se | 0.568 | 0.680 | 0.680 | 0.568 | 0.680 | 0.225 | — |
| 21 | prespec | rel504 | pkg | train | True | 100 | 0.5 | dev_min | 0.694 | 0.800 | 0.800 | 0.694 | 0.800 | 0.627 | — |
| 21 | prespec | rel504 | pkg | train | True | 100 | 0.5 | global | 0.733 | 0.819 | 0.819 | 0.733 | 0.819 | 0.590 | — |
| 21 | prespec | rel504 | pkg | train | True | 100 | 0.5 | published | 0.764 | 0.868 | 0.868 | 0.764 | 0.868 | 0.661 | — |
| 22 | prespec | rel504 | pkg | train | True | 100 | 0.7 | class_1se | 0.523 | 0.661 | 0.661 | 0.523 | 0.661 | 0.149 | — |
| 22 | prespec | rel504 | pkg | train | True | 100 | 0.7 | class_min | 0.671 | 0.787 | 0.787 | 0.671 | 0.787 | 0.520 | — |
| 22 | prespec | rel504 | pkg | train | True | 100 | 0.7 | dev_1se | 0.548 | 0.664 | 0.664 | 0.548 | 0.664 | 0.181 | — |
| 22 | prespec | rel504 | pkg | train | True | 100 | 0.7 | dev_min | 0.712 | 0.808 | 0.808 | 0.712 | 0.808 | 0.611 | — |
| 22 | prespec | rel504 | pkg | train | True | 100 | 0.7 | global | 0.735 | 0.815 | 0.815 | 0.735 | 0.815 | 0.591 | — |
| 22 | prespec | rel504 | pkg | train | True | 100 | 0.7 | published | 0.742 | 0.845 | 0.845 | 0.742 | 0.845 | 0.633 | — |
| 23 | prespec | rel504 | pkg | train | True | 100 | 1.0 | class_1se | 0.473 | 0.621 | 0.621 | 0.473 | 0.621 | 0.122 | — |
| 23 | prespec | rel504 | pkg | train | True | 100 | 1.0 | class_min | 0.681 | 0.792 | 0.792 | 0.681 | 0.792 | 0.522 | — |
| 23 | prespec | rel504 | pkg | train | True | 100 | 1.0 | dev_1se | 0.488 | 0.613 | 0.613 | 0.488 | 0.613 | 0.095 | — |
| 23 | prespec | rel504 | pkg | train | True | 100 | 1.0 | dev_min | 0.713 | 0.799 | 0.799 | 0.713 | 0.799 | 0.569 | — |
| 23 | prespec | rel504 | pkg | train | True | 100 | 1.0 | global | 0.732 | 0.807 | 0.807 | 0.732 | 0.807 | 0.576 | — |
| 23 | prespec | rel504 | pkg | train | True | 100 | 1.0 | published | 0.718 | 0.808 | 0.808 | 0.718 | 0.808 | 0.606 | — |
| 24 | prespec | rel504 | rel | cohort | True | 100 | 0.9 | class_1se | 0.721 | 0.835 | 0.835 | 0.721 | 0.835 | 0.264 | — |
| 24 | prespec | rel504 | rel | cohort | True | 100 | 0.9 | class_min | 0.783 | 0.849 | 0.849 | 0.783 | 0.849 | 0.384 | — |
| 24 | prespec | rel504 | rel | cohort | True | 100 | 0.9 | dev_1se | 0.715 | 0.837 | 0.837 | 0.715 | 0.837 | 0.257 | — |
| 24 | prespec | rel504 | rel | cohort | True | 100 | 0.9 | dev_min | 0.777 | 0.855 | 0.855 | 0.777 | 0.855 | 0.371 | — |
| 24 | prespec | rel504 | rel | cohort | True | 100 | 0.9 | global | 0.785 | 0.857 | 0.857 | 0.785 | 0.857 | 0.391 | — |
| 24 | prespec | rel504 | rel | cohort | True | 100 | 0.9 | published | 0.784 | 0.849 | 0.849 | 0.784 | 0.849 | 0.389 | — |
| 25 | prespec | rel504 | rel | cohort | True | 100 | 0.5 | class_1se | 0.722 | 0.832 | 0.832 | 0.722 | 0.832 | 0.254 | — |
| 25 | prespec | rel504 | rel | cohort | True | 100 | 0.5 | class_min | 0.781 | 0.843 | 0.843 | 0.781 | 0.843 | 0.377 | — |
| 25 | prespec | rel504 | rel | cohort | True | 100 | 0.5 | dev_1se | 0.720 | 0.835 | 0.835 | 0.720 | 0.835 | 0.255 | — |
| 25 | prespec | rel504 | rel | cohort | True | 100 | 0.5 | dev_min | 0.774 | 0.859 | 0.859 | 0.774 | 0.859 | 0.365 | — |
| 25 | prespec | rel504 | rel | cohort | True | 100 | 0.5 | global | 0.783 | 0.856 | 0.856 | 0.783 | 0.856 | 0.376 | — |
| 25 | prespec | rel504 | rel | cohort | True | 100 | 0.5 | published | 0.790 | 0.856 | 0.856 | 0.790 | 0.856 | 0.381 | — |
| 26 | prespec | rel504 | rel | cohort | True | 100 | 0.7 | class_1se | 0.719 | 0.834 | 0.834 | 0.719 | 0.834 | 0.254 | — |
| 26 | prespec | rel504 | rel | cohort | True | 100 | 0.7 | class_min | 0.778 | 0.847 | 0.847 | 0.778 | 0.847 | 0.379 | — |
| 26 | prespec | rel504 | rel | cohort | True | 100 | 0.7 | dev_1se | 0.717 | 0.837 | 0.837 | 0.717 | 0.837 | 0.258 | — |
| 26 | prespec | rel504 | rel | cohort | True | 100 | 0.7 | dev_min | 0.775 | 0.859 | 0.859 | 0.775 | 0.859 | 0.366 | — |
| 26 | prespec | rel504 | rel | cohort | True | 100 | 0.7 | global | 0.783 | 0.868 | 0.868 | 0.783 | 0.868 | 0.378 | — |
| 26 | prespec | rel504 | rel | cohort | True | 100 | 0.7 | published | 0.786 | 0.853 | 0.853 | 0.786 | 0.853 | 0.385 | — |
| 27 | prespec | rel504 | rel | cohort | True | 100 | 1.0 | class_1se | 0.717 | 0.837 | 0.837 | 0.717 | 0.837 | 0.263 | — |
| 27 | prespec | rel504 | rel | cohort | True | 100 | 1.0 | class_min | 0.777 | 0.846 | 0.846 | 0.777 | 0.846 | 0.388 | — |
| 27 | prespec | rel504 | rel | cohort | True | 100 | 1.0 | dev_1se | 0.710 | 0.834 | 0.834 | 0.710 | 0.834 | 0.258 | — |
| 27 | prespec | rel504 | rel | cohort | True | 100 | 1.0 | dev_min | 0.772 | 0.855 | 0.855 | 0.772 | 0.855 | 0.368 | — |
| 27 | prespec | rel504 | rel | cohort | True | 100 | 1.0 | global | 0.784 | 0.861 | 0.861 | 0.784 | 0.861 | 0.393 | — |
| 27 | prespec | rel504 | rel | cohort | True | 100 | 1.0 | published | 0.783 | 0.852 | 0.852 | 0.783 | 0.852 | 0.395 | — |
| 28 | prespec | rel504 | rel | train | True | 100 | 0.9 | class_1se | 0.721 | 0.835 | 0.835 | 0.721 | 0.835 | 0.264 | — |
| 28 | prespec | rel504 | rel | train | True | 100 | 0.9 | class_min | 0.782 | 0.849 | 0.849 | 0.782 | 0.849 | 0.387 | — |
| 28 | prespec | rel504 | rel | train | True | 100 | 0.9 | dev_1se | 0.715 | 0.837 | 0.837 | 0.715 | 0.837 | 0.258 | — |
| 28 | prespec | rel504 | rel | train | True | 100 | 0.9 | dev_min | 0.777 | 0.855 | 0.855 | 0.777 | 0.855 | 0.371 | — |
| 28 | prespec | rel504 | rel | train | True | 100 | 0.9 | global | 0.785 | 0.857 | 0.857 | 0.785 | 0.857 | 0.391 | — |
| 28 | prespec | rel504 | rel | train | True | 100 | 0.9 | published | 0.784 | 0.849 | 0.849 | 0.784 | 0.849 | 0.389 | — |
| 29 | prespec | rel504 | rel | train | True | 100 | 0.5 | class_1se | 0.722 | 0.832 | 0.832 | 0.722 | 0.832 | 0.254 | — |
| 29 | prespec | rel504 | rel | train | True | 100 | 0.5 | class_min | 0.781 | 0.843 | 0.843 | 0.781 | 0.843 | 0.377 | — |
| 29 | prespec | rel504 | rel | train | True | 100 | 0.5 | dev_1se | 0.720 | 0.835 | 0.835 | 0.720 | 0.835 | 0.255 | — |
| 29 | prespec | rel504 | rel | train | True | 100 | 0.5 | dev_min | 0.774 | 0.859 | 0.859 | 0.774 | 0.859 | 0.365 | — |
| 29 | prespec | rel504 | rel | train | True | 100 | 0.5 | global | 0.783 | 0.856 | 0.856 | 0.783 | 0.856 | 0.376 | — |
| 29 | prespec | rel504 | rel | train | True | 100 | 0.5 | published | 0.790 | 0.856 | 0.856 | 0.790 | 0.856 | 0.381 | — |
| 30 | prespec | rel504 | rel | train | True | 100 | 0.7 | class_1se | 0.719 | 0.834 | 0.834 | 0.719 | 0.834 | 0.254 | — |
| 30 | prespec | rel504 | rel | train | True | 100 | 0.7 | class_min | 0.780 | 0.847 | 0.847 | 0.780 | 0.847 | 0.381 | — |
| 30 | prespec | rel504 | rel | train | True | 100 | 0.7 | dev_1se | 0.717 | 0.837 | 0.837 | 0.717 | 0.837 | 0.258 | — |
| 30 | prespec | rel504 | rel | train | True | 100 | 0.7 | dev_min | 0.775 | 0.859 | 0.859 | 0.775 | 0.859 | 0.366 | — |
| 30 | prespec | rel504 | rel | train | True | 100 | 0.7 | global | 0.783 | 0.868 | 0.868 | 0.783 | 0.868 | 0.378 | — |
| 30 | prespec | rel504 | rel | train | True | 100 | 0.7 | published | 0.786 | 0.853 | 0.853 | 0.786 | 0.853 | 0.385 | — |
| 31 | prespec | rel504 | rel | train | True | 100 | 1.0 | class_1se | 0.716 | 0.835 | 0.835 | 0.716 | 0.835 | 0.263 | — |
| 31 | prespec | rel504 | rel | train | True | 100 | 1.0 | class_min | 0.777 | 0.846 | 0.846 | 0.777 | 0.846 | 0.388 | — |
| 31 | prespec | rel504 | rel | train | True | 100 | 1.0 | dev_1se | 0.710 | 0.834 | 0.834 | 0.710 | 0.834 | 0.258 | — |
| 31 | prespec | rel504 | rel | train | True | 100 | 1.0 | dev_min | 0.772 | 0.855 | 0.855 | 0.772 | 0.855 | 0.368 | — |
| 31 | prespec | rel504 | rel | train | True | 100 | 1.0 | global | 0.784 | 0.861 | 0.861 | 0.784 | 0.861 | 0.393 | — |
| 31 | prespec | rel504 | rel | train | True | 100 | 1.0 | published | 0.783 | 0.852 | 0.852 | 0.783 | 0.852 | 0.395 | — |
| 32 | post_hoc | s773 | their | cohort | False | 100 | 0.9 | class_1se | 0.817 | 0.910 | 0.916 | 0.771 | 0.838 | 0.909 | False |
| 32 | post_hoc | s773 | their | cohort | False | 100 | 0.9 | class_min | 0.860 | 0.905 | 0.912 | 0.809 | 0.860 | 0.975 | True |
| 32 | post_hoc | s773 | their | cohort | False | 100 | 0.9 | dev_1se | 0.763 | 0.895 | 0.905 | 0.714 | 0.790 | 0.832 | False |
| 32 | post_hoc | s773 | their | cohort | False | 100 | 0.9 | dev_min | 0.867 | 0.925 | 0.934 | 0.824 | 0.886 | 0.986 | True |
| 32 | post_hoc | s773 | their | cohort | False | 100 | 0.9 | global | 0.869 | 0.926 | 0.932 | 0.827 | 0.881 | 0.990 | True |
| 32 | post_hoc | s773 | their | cohort | False | 100 | 0.9 | published | 0.870 | 0.925 | 0.933 | 0.828 | 0.883 | 0.991 | True |
| 33 | post_hoc | s773 | their | cohort | True | 100 | 0.9 | class_1se | 0.823 | 0.883 | 0.893 | 0.787 | 0.825 | 0.833 | False |
| 33 | post_hoc | s773 | their | cohort | True | 100 | 0.9 | class_min | 0.907 | 0.930 | 0.934 | 0.897 | 0.905 | 0.866 | False |
| 33 | post_hoc | s773 | their | cohort | True | 100 | 0.9 | dev_1se | 0.758 | 0.836 | 0.856 | 0.709 | 0.736 | 0.718 | False |
| 33 | post_hoc | s773 | their | cohort | True | 100 | 0.9 | dev_min | 0.849 | 0.893 | 0.895 | 0.827 | 0.848 | 0.876 | False |
| 33 | post_hoc | s773 | their | cohort | True | 100 | 0.9 | global | 0.918 | 0.949 | 0.947 | 0.913 | 0.924 | 0.858 | False |
| 33 | post_hoc | s773 | their | cohort | True | 100 | 0.9 | published | 0.888 | 0.920 | 0.921 | 0.877 | 0.892 | 0.881 | False |
| 34 | post_hoc | s711 | their | cohort | False | 100 | 0.9 | class_1se | 0.798 | 0.842 | 0.870 | 0.784 | 0.828 | 0.945 | — |
| 34 | post_hoc | s711 | their | cohort | False | 100 | 0.9 | class_min | 0.846 | 0.860 | 0.884 | 0.811 | 0.865 | 0.965 | — |
| 34 | post_hoc | s711 | their | cohort | False | 100 | 0.9 | dev_1se | 0.706 | 0.794 | 0.822 | 0.699 | 0.762 | 0.819 | — |
| 34 | post_hoc | s711 | their | cohort | False | 100 | 0.9 | dev_min | 0.827 | 0.845 | 0.877 | 0.794 | 0.848 | 0.982 | — |
| 34 | post_hoc | s711 | their | cohort | False | 100 | 0.9 | global | 0.843 | 0.856 | 0.884 | 0.813 | 0.860 | 0.980 | — |
| 34 | post_hoc | s711 | their | cohort | False | 100 | 0.9 | published | 0.841 | 0.860 | 0.888 | 0.810 | 0.860 | 0.986 | — |
| 35 | post_hoc | rel504 | their | cohort | False | 100 | 0.9 | class_1se | 0.711 | 0.794 | 0.794 | 0.711 | 0.794 | 0.597 | — |
| 35 | post_hoc | rel504 | their | cohort | False | 100 | 0.9 | class_min | 0.775 | 0.849 | 0.849 | 0.775 | 0.849 | 0.859 | — |
| 35 | post_hoc | rel504 | their | cohort | False | 100 | 0.9 | dev_1se | 0.727 | 0.801 | 0.801 | 0.727 | 0.801 | 0.632 | — |
| 35 | post_hoc | rel504 | their | cohort | False | 100 | 0.9 | dev_min | 0.798 | 0.880 | 0.880 | 0.798 | 0.880 | 0.864 | — |
| 35 | post_hoc | rel504 | their | cohort | False | 100 | 0.9 | global | 0.807 | 0.887 | 0.887 | 0.807 | 0.887 | 0.863 | — |
| 35 | post_hoc | rel504 | their | cohort | False | 100 | 0.9 | published | 0.798 | 0.868 | 0.868 | 0.798 | 0.868 | 0.888 | — |
| 36 | post_hoc | s773 | their | cohort | False | 1000 | 0.9 | class_1se | 0.813 | 0.911 | 0.917 | 0.767 | 0.831 | 0.905 | False |
| 36 | post_hoc | s773 | their | cohort | False | 1000 | 0.9 | class_min | 0.861 | 0.910 | 0.914 | 0.810 | 0.862 | 0.974 | True |
| 36 | post_hoc | s773 | their | cohort | False | 1000 | 0.9 | dev_1se | 0.757 | 0.894 | 0.900 | 0.705 | 0.785 | 0.822 | False |
| 36 | post_hoc | s773 | their | cohort | False | 1000 | 0.9 | dev_min | 0.867 | 0.925 | 0.934 | 0.825 | 0.887 | 0.986 | True |
| 36 | post_hoc | s773 | their | cohort | False | 1000 | 0.9 | global | 0.869 | 0.925 | 0.931 | 0.827 | 0.877 | 0.990 | True |
| 36 | post_hoc | s773 | their | cohort | False | 1000 | 0.9 | published | 0.870 | 0.925 | 0.933 | 0.828 | 0.883 | 0.991 | True |
| 37 | post_hoc | s773 | pkg | cohort | False | 100 | 0.9 | class_1se | 0.798 | 0.883 | 0.902 | 0.700 | 0.803 | 0.602 | False |
| 37 | post_hoc | s773 | pkg | cohort | False | 100 | 0.9 | class_min | 0.799 | 0.811 | 0.825 | 0.735 | 0.754 | 0.669 | False |
| 37 | post_hoc | s773 | pkg | cohort | False | 100 | 0.9 | dev_1se | 0.806 | 0.880 | 0.900 | 0.719 | 0.827 | 0.618 | False |
| 37 | post_hoc | s773 | pkg | cohort | False | 100 | 0.9 | dev_min | 0.831 | 0.875 | 0.897 | 0.758 | 0.813 | 0.713 | False |
| 37 | post_hoc | s773 | pkg | cohort | False | 100 | 0.9 | global | 0.868 | 0.907 | 0.919 | 0.817 | 0.866 | 0.768 | False |
| 37 | post_hoc | s773 | pkg | cohort | False | 100 | 0.9 | published | 0.849 | 0.894 | 0.914 | 0.781 | 0.850 | 0.751 | False |
| 38 | post_hoc | rel504 | pkg | cohort | False | 100 | 0.9 | class_1se | 0.577 | 0.561 | 0.561 | 0.577 | 0.561 | 0.062 | — |
| 38 | post_hoc | rel504 | pkg | cohort | False | 100 | 0.9 | class_min | 0.692 | 0.725 | 0.725 | 0.692 | 0.725 | 0.507 | — |
| 38 | post_hoc | rel504 | pkg | cohort | False | 100 | 0.9 | dev_1se | 0.626 | 0.646 | 0.646 | 0.626 | 0.646 | 0.203 | — |
| 38 | post_hoc | rel504 | pkg | cohort | False | 100 | 0.9 | dev_min | 0.749 | 0.778 | 0.778 | 0.749 | 0.778 | 0.607 | — |
| 38 | post_hoc | rel504 | pkg | cohort | False | 100 | 0.9 | global | 0.764 | 0.792 | 0.792 | 0.764 | 0.792 | 0.555 | — |
| 38 | post_hoc | rel504 | pkg | cohort | False | 100 | 0.9 | published | 0.765 | 0.832 | 0.832 | 0.765 | 0.832 | 0.617 | — |
| 39 | post_hoc | rel504 | rel | cohort | False | 100 | 0.9 | class_1se | 0.717 | 0.837 | 0.837 | 0.717 | 0.837 | 0.265 | — |
| 39 | post_hoc | rel504 | rel | cohort | False | 100 | 0.9 | class_min | 0.771 | 0.850 | 0.850 | 0.771 | 0.850 | 0.383 | — |
| 39 | post_hoc | rel504 | rel | cohort | False | 100 | 0.9 | dev_1se | 0.713 | 0.831 | 0.831 | 0.713 | 0.831 | 0.262 | — |
| 39 | post_hoc | rel504 | rel | cohort | False | 100 | 0.9 | dev_min | 0.775 | 0.857 | 0.857 | 0.775 | 0.857 | 0.379 | — |
| 39 | post_hoc | rel504 | rel | cohort | False | 100 | 0.9 | global | 0.789 | 0.850 | 0.850 | 0.789 | 0.850 | 0.389 | — |
| 39 | post_hoc | rel504 | rel | cohort | False | 100 | 0.9 | published | 0.781 | 0.850 | 0.850 | 0.781 | 0.850 | 0.387 | — |

### D. Step table from our 0.800 to the published value

| Step | Release rows patient max | Release rows per sample | 773 per sample | Spearman vs published |
|---|---|---|---|---|
| 0 our R2 retrain (sklearn elastic net, release features, 504 release rows, C by patient AUROC) | 0.800 | 0.780 | — | 0.414 |
| 1 R glmnet, release features, release rows, whole-set standardisation, alpha 0.9, class min | 0.849 [0.754, 0.932] | 0.783 | — | 0.384 |
| 2 package features from our counts (same rows) | 0.792 [0.694, 0.887] | 0.681 | — | 0.538 |
| 3 train on all 773 published samples (HGD/IMC and post-event included) | 0.824 [0.729, 0.906] | 0.772 | 0.852 | 0.721 |
| 4 their shipped training matrix instead of our features [post hoc] | 0.905 [0.835, 0.960] | 0.897 | 0.907 | 0.866 |
| 5 glmnet standardize = FALSE, as in their fit call [post hoc] | 0.860 [0.777, 0.936] | 0.809 | 0.860 | 0.975 |
| 6 lambda.1se (class), as in their LOO coefficient tables [post hoc] | 0.838 [0.748, 0.916] | 0.771 | 0.817 | 0.909 |
| 7 1,000-value lambda path [post hoc] | 0.831 [0.742, 0.911] | 0.767 | 0.813 | 0.905 |
| 8 one fixed lambda for every left-out patient = the published model's lambda (not fold-honest) [post hoc] | 0.883 [0.809, 0.947] | 0.828 | 0.870 | 0.991 |
| 9 as 8 but trained on the release rows only (their matrix) [post hoc] | 0.868 [0.784, 0.940] | 0.798 | — | 0.888 |
| 10 as 8 with our counts through the package (pkg features) [post hoc] | 0.850 [0.759, 0.928] | 0.781 | 0.849 | 0.751 |
| published LOPO probabilities (MOESM4) | 0.873 | 0.820 | 0.865 | 1.000 |

**Reconciliation.** The published 0.87 is a per-sample AUROC over all 773 samples (HGD/IMC and post-event samples included), from glmnet on their hg19 feature matrix with standardize = FALSE and one λ shared by every left-out patient; that recipe on their shipped matrix reproduces the published probabilities (Spearman 0.991, per sample 0.870 vs 0.865, release-row patient max 0.883 vs 0.873), while the same recipe on our hg38 counts gives 0.849 per sample and 0.850 release-row patient max, so the gap from our 0.800 is mostly the feature pipeline and the training population.

**Deviations from the pre-specification.** (1) Release features exist for 490 of the 773 samples, so release features × 773 / 711 samples were not run. (2) hg38 adaptations needed to run the package: blacklist lifted from hg19 (881 of 956 regions), autosomes only, explicit hg38 arms for copynumber segmentation, and the package's bundled hg38 chromosome file read directly (its loader downloads UCSC files when verbose = FALSE, which no longer parse); model tiles matched to our hg38 tiles by nearest midpoint (589 model tiles to 586 distinct hg38 tiles). (3) Post hoc, from the shipped model object: feature source 'their' (the shipped 773 × 634 training matrix, rows aligned to our samples by correlation), glmnet standardize = FALSE, a 1,000-value λ path, and a deviance 1-s.e. rule; all tagged post hoc in the grid. (4) The 500 release rows share 490 sequencing samples; retrained scores are per sequencing sample, so 'release rows' means 490 samples for retrained arms and 500 rows for the published probabilities (A0, D last row). (5) The sheet marks 712 samples as non-HGD/IMC (the paper says 711).

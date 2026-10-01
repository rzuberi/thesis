# Horizon (1/3/5-year) analysis, false-positive change, WSI–CNV weighting by horizon, depth transfer

Status: PRE-SPECIFICATION (written 2026-10-01). Nothing below has been run. Results are appended in a later commit under the line at the end; this section is not edited afterwards. Any change of specification after this commit is reported as a deviation, with both versions.

Ground rules carried from `docs/paper_plan_killcoyne_cv.md` (commit 76879b8 pre-specification, d69de24 results): rank AUROC to 3 decimals, patient-clustered bootstrap (2,000, `RandomState(0)`), within-patient swap permutation (2,000, seed 0), status per item, at most one line of interpretation. No ACE-B outcome or pathology field is read anywhere in this task.

## Cohort, labels, folds

- **The discovery subset** = set C in the code: `feasibility/paper_plan/killcoyne_mm/set_C.csv`, 676 samples, 80 patients, 37 progressors (P). The imaging subset of the Killcoyne 2020 discovery cohort.
- **Labels: Killcoyne 2020 definitions only.** P = the sheet `Status` P (NDBE → HGD/IMC); NP = never beyond LGD. No LGD2+ anywhere.
- **Cross-validation:** the stratified, patient-grouped 10-fold × 10 CV of `docs/paper_plan_killcoyne_cv.md` item 1 (`scripts/paper_plan/kv_cv.R`: for repeat s = 1..10, `set.seed(s)`, P patients shuffled then NP, concatenated, folds assigned cyclically; image block z-scored on the training rows; λ = class-error min of the inner 10 × 5 patient-grouped CV). Out-of-fold (OOF) predictions are on the cluster under `feasibility/paper_plan/killcoyne_mm/cv/preds/`. Arm score = mean of the 10 repeats' OOF probabilities; L-LATE = mean of L-CNV and L-IMG probabilities within each repeat, then averaged over repeats (as in `kv_merge.py`).
- **CNV sources:** their shipped matrix (`cnv_their_C.csv`, primary) and package features (`cnv_pkg_C.csv`).

## H0. Time origin, event, horizon labels, metrics

**Event time per sample.** Let `mbf` be the 777 sheet's `Months before final` of a sample.
- Progressors: the endpoint is the patient's first HGD/IMC endoscopy among the 773 published samples (`kr_samples.csv` Pathology HGD/IMC, or sheet `Path_class_per_OGD` HGD/IMC/HGD-IMC), at `tev` = the largest `mbf` among those samples, exactly as `scripts/paper_plan/kc_merge.py:30-32`. Time = (`mbf` − `tev`)/12 years, event = 1.
- The 4 progressors with no HGD/IMC sample among the published samples: endpoint = the final endoscopy (`tev` = 0), as in `kc_merge.py`; flagged, and every H1 headline cell is also reported with these 4 patients removed.
- Non-progressors: censored at their last endoscopy in the sheet (the 'final' of `Months before final`): time = `mbf`/12, event = 0.

**Samples used for prediction.** Only samples taken before the event: progressor samples with `mbf` > `tev` (samples on or after the first HGD/IMC, including the diagnostic samples, are excluded); all non-progressor samples. This is the `b_before_first_HGD_IMC` subset of `kv_merge.py`. Second population: those samples that are NDBE (`c_NDBE_and_before`). n samples, patients and events are reported per horizon.

**Horizon labels at t = 1, 3, 5 years (cumulative/dynamic).**
- Case: event = 1 and time ≤ t.
- Control: event-free with follow-up ≥ t, i.e. event = 0 and time ≥ t, or event = 1 and time > t (later progressors are controls at t).
- Excluded at t: event = 0 and time < t.

**Metrics.**
- Primary: IPCW time-dependent AUROC (Uno-type cumulative/dynamic): Σ_i Σ_j 1(case_i) 1(control_j) [1(M_i > M_j) + ½ 1(M_i = M_j)] w_i / Σ_i Σ_j 1(case_i) 1(control_j) w_i, with w_i = 1/Ĝ(T_i−); Ĝ = Kaplan–Meier of the censoring distribution (reverse outcome, event indicator 1 − δ) over the evaluated samples; control weights 1/Ĝ(t) are constant and cancel. Ĝ is re-estimated inside every bootstrap draw.
- Secondary: the same AUROC unweighted (plain rank AUROC of cases vs controls).
- Also: Harrell's C (lifelines `concordance_index`, higher score = shorter time) and Uno's C (IPCW weights Ĝ(T_i)⁻², τ = the largest event time) over all follow-up.

**Unit and uncertainty.** Primary unit per sample (Killcoyne's unit); 95% CI by patient-clustered bootstrap (2,000 draws of the patients, `RandomState(0)`; one set of draws per population, shared by every arm, horizon and metric so differences are paired; a draw with no case or no control at a horizon is dropped for that horizon and the count of valid draws reported). Secondary unit per patient: each patient's earliest pre-event NDBE sample (largest `mbf` among its NDBE pre-event samples); patients without one are excluded.

**Design caveat (to be stated in the output).** The discovery cohort is a matched case–control design (non-progressors needed ≥ 3 years of follow-up, progressors ≥ 1 year), so AUROCs are interpretable but absolute risks, calibration and positive predictive values are not; no absolute risk is reported.

**Primary model for "which model is best": L-LATE** (late fusion, as pre-registered for ACE-B). Every other arm is compared to it by the paired Δ IPCW AUROC with bootstrap CI, an unadjusted within-patient swap permutation p, and a single-step max-T selection-adjusted p over the arms within each horizon (one swap mask per permutation applied to every arm-vs-L-LATE pair, adjusted p = (1 + #{max_k |Δ*_k| ≥ |Δ_j|})/2,001, as `scripts/paper_plan/kf_stats.py`). Family per (CNV source, population, horizon): L-GRADE, L-GRADE+age+sex, L-CNV, L-IMG, L-EARLY, L-INTER (6 arms).

## H1. Horizon table (internal columns)

**Arms.**
- Clinical only: L-GRADE (existing stratified-CV OOF, `kv_cv.R` cfg 5); L-GRADE+age+sex (new, see below).
- CNV (replication): L-CNV, their matrix (primary, cfg 0) and package features (cfg 1).
- WSI: L-IMG (cfg 2). Early fusion: L-EARLY (cfg 3, 4). Late fusion: L-LATE (from cfg 0/1 + 2).
- Intermediate fusion: L-INTER does not exist under the stratified CV. It is rerun under the same stratified CV with the `docs/paper_plan_killcoyne_multimodal.md` specification (per modality a PCA with 32 components fitted on the training rows, components z-scored on the training rows, concatenated (64) into glmnet α 0.9, standardize = FALSE, λ class-error min of the inner 10 × 5 CV), with the image block z-scored on the training rows before its PCA (fold-honest, as every stratified-CV arm). Their matrix and package features.
- L-GRADE+age+sex: the same stratified CV and glmnet machinery on [grade (ordinal, standardised over C as in `kv_common.R`), age at sample, sex (M = 1)], age and sex z-scored on the training rows. Age at sample = (first set C sample date in `pre_event_cohort.Date` − `Demographics_full.csv` Date of birth)/365.25 + (`mbf` of the first set C sample − `mbf` of the sample)/12; sex = `Demographics_full.csv` Sex (both complete for the 80 patients, `docs/dataset_description.md` item 4). Prague and smoking are excluded (incomplete).

Both new arms are refits (the task asks for them); no other arm is refitted. Existing OOF predictions (trained on ever-progression) are scored against each horizon label, so the table measures how well an ever-progression score ranks near-term against later events.

**Cells.** For each arm × horizon × CNV source × population (all pre-event samples; NDBE pre-event samples): IPCW AUROC [CI]; n cases, n controls; unweighted AUROC [CI]; paired Δ vs L-CNV (same source) and vs L-LATE with CI; unadjusted and max-T adjusted p. Harrell's and Uno's C per arm. Secondary unit (patient) the same, without max-T.

**Rendered table.** Rows Clinical only = L-GRADE, CNV (replication) = L-CNV their, WSI = L-IMG, Early = L-EARLY their, Intermediate = L-INTER their, Late = L-LATE their; per-sample IPCW AUROC [CI] (n cases / n controls) on all pre-event samples. ACE-B columns NOT AVAILABLE (no slides, outcomes blinded).

**ACE-B code path.** `scripts/paper_plan/hz_aceb_fill.py`: inputs (i) per-sample scores from the frozen package bundle `models/killcoyne_frozen_pkg_v1` (L-CNV, L-IMG, L-EARLY, L-LATE; L-GRADE, L-GRADE+age+sex and L-INTER have no frozen model and stay NOT AVAILABLE), (ii) a label file with patient, time, event per sample. It computes exactly the H0/H1 metrics. Its end-to-end check uses the frozen models applied to the set C feature blocks as stand-in inputs and a dummy label vector (random times and events, `RandomState(0)`); no real ACE-B label is touched.

## H2. Change in false positives

**Operating points (each fitted on training folds, applied to held-out folds).**
- (a) 80% sensitivity for the ever-progression label: within each outer training fold, the largest threshold whose sensitivity on the training samples' **inner OOF** predictions (H3 nested job, below) is ≥ 0.80; applied to that fold's outer held-out predictions.
- (b) Killcoyne's high-risk threshold Pr ≥ 0.5 on the held-out probability (fixed; for L-LATE the mean of the two probabilities).
- A sample's call is the majority over the 10 repeats (positive in ≥ 6 of 10; 5/5 is negative). Per-repeat mean FPR/TPR are reported alongside.

**Comparisons.** L-CNV vs the best model from H1 and vs L-LATE (same CNV source). Best model = the arm with the highest mean per-sample IPCW AUROC over the three horizons on all pre-event samples, their matrix, among L-IMG, L-EARLY, L-INTER, L-LATE (the same arm is used for the package source). At each operating point and horizon, on that horizon's cases and controls: FPR and TPR of each model and the paired difference with patient-bootstrap CI; 2 × 2 reclassification (CNV-negative → fusion-positive and the reverse, by case and control) on samples and on patients (secondary unit); categorical NRI = [P(up | case) − P(down | case)] + [P(down | control) − P(up | control)] with CI. Populations: all pre-event samples (primary) and NDBE pre-event samples.

**Who fusion catches / clears.** Cases CNV-negative & fusion-positive vs cases positive under both; controls CNV-positive & fusion-negative vs controls positive under both. Compared on: sample pathology; time to event; CNV complexity (the raw cx count of the package block; and the cx column of each source) and noise (the package QC residual statistic from `segmentRawData`, `feasibility/paper_plan/killcoyne/pkg/pat_*.rds`); tissue tiles available (as `docs/dataset_description.md` item 5); scanner (`hamamatsu.Product`); p53 IHC where present (`set_C.csv` `P53 IHC`). Operating point (a), 3-year horizon, their matrix, best model and L-LATE; the other cells' counts reported. The patient list by study number (Hospital Research ID) with Killcoyne's published risk class per sample (from the published probability `k_prob`: low < 0.3, moderate 0.3 to < 0.5, high ≥ 0.5) is row-level, so it is written only on the cluster (`feasibility/paper_plan/killcoyne_mm/horizons/h2_patient_list.csv`); the public document gives aggregates and that path.

## H3. WSI vs CNV weighting by horizon

**Nested job (also feeds H2 (a)).** For every repeat s and outer fold k: inner 5-fold patient-grouped CV on the outer training patients, stratified as the outer CV (`set.seed(1000 s + k)`, P shuffled then NP, cyclic); each inner fit is the outer arm's model (L-CNV their, L-CNV pkg, L-IMG, L-EARLY their/pkg, L-INTER their/pkg) with λ = class-error min of a 1 × 5 patient-grouped CV on the inner training patients (`set.seed(1)`; one repeat instead of ten to bound cost); image scaling and PCA fitted on the inner training rows. Output: inner OOF probabilities for all outer training samples.

**Stack.** For each (s, k) and horizon t: logits of the inner OOF L-CNV and L-IMG probabilities (clipped to [1e-6, 1 − 1e-6]), each z-scored over the outer training samples that are horizon-t cases or controls; logistic regression label_t ~ a + b·CNV + c·IMG on those samples (L2 penalty with C = 10⁴, effectively unpenalised, to keep separable folds finite). A fold with no case or no control at t is skipped and counted.
- Report the mean b, c and c/(b + c) over the 100 fits; 95% CI by patient bootstrap (2,000 draws, `RandomState(0)`; each draw refits all fold stacks with patient-multiplicity weights); the paired difference in c/(b + c) between 1 and 5 years with CI. Their matrix (primary) and package features.
- Exploratory (fitted after H1 is seen): the held-out per-sample IPCW AUROC of the horizon-specific stack (applied to the outer OOF L-CNV and L-IMG predictions of the same (s, k), standardised with the training constants, averaged over repeats) vs the fixed 50/50 L-LATE, paired Δ with CI.
- **Expected direction, stated in advance:** the WSI weight c/(b + c) is higher at 1 year than at 5 years.

## H4. Depth transfer

**What exists (searched, paths listed in the output).** (i) Any 4× resequenced discovery data: BAM/CRAM/FASTQ under `/mnt/scratche/fast/fmlab`, `/mnt/scratche/slow/fmlab` and the other mounted lab scratch areas whose name matches a discovery SLX id from the 777 sheet outside `SWGCohort/dna_seq_bam`, or a directory named for resequencing/depth. (ii) ACE-B BAM or FASTQ: files matching the ACE-B SLX pools in the manifest (SLX-26195, SLX-26196, SLX-26851, SLX-27125, SLX-27128); their depth. The manifest gives `Mean_Coverage` median 5.3×, range 3.29–14.91× (191 samples; `docs/dataset_description.md` item 7), not 7×.

**If no 4× discovery data exists:** "4× → external" is NOT AVAILABLE, and the label-blind depth check runs instead.

**Label-blind depth check on ACE-B (no outcome, no pathology).**
- For every ACE-B sample with reads: nominal depth = reads × modal read length / 3,088,269,832 (as `docs/dataset_description.md` item 6). Downsample with `samtools view -s <seed>.<fraction>` to 0.3×, 0.4×, 1× and 4× nominal, seeds 1–5; a sample whose native depth is below a target is skipped at that target and counted. If only FASTQ exists, reads are aligned to hg38 with `bwa aln` + `bwa samse` as the SWG BAMs were (R1 only), before downsampling.
- QDNAseq 50 kb hg38 raw and fitted counts with the generator that produced the discovery 50 kb counts (`[BT]/scripts/swg_generate_qdnaseq_one_sample.R`); then the package pipeline exactly as `scripts/paper_plan/kr_package.R` (hg38, multipcf per patient across that patient's samples at the same depth and seed, `segmentRawData` frozen parameters, blacklist lifted to hg38); the package's sample sheet gets a constant placeholder pathology so no ACE-B pathology is read. Features built with the frozen constants of `models/killcoyne_frozen_pkg_v1` (tile/arm/cx scaling over set C, arm–tile incidence) and scored with the frozen L-CNV (package) coefficients; native depth likewise.
- Report: ICC of the probability across the 5 seeds at each depth (one-way random, ICC(1,1)); ICC between each depth's seed-mean probability and native (two-way agreement, ICC(A,1)); median |Δ probability| vs native; fraction of samples changing Killcoyne risk class (low < 0.3, moderate 0.3 to < 0.5, high ≥ 0.5) vs native; raw cx count distribution at each depth against the discovery subset.

**Pre-specified rule for the ACE-B primary analysis.** Downsample ACE-B to 0.4× nominal (closest to the discovery training depth, median about 0.3×, and matching Killcoyne's reported depth); native depth secondary. Committed in this same commit as amendment 2 of `docs/aceb_analysis_plan.md`, before any ACE-B outcome is read (none is read in this task).

## Outputs

Scripts `scripts/paper_plan/hz_*` (R for model fits, Python for metrics), run through `scripts/cluster/campaign.sh` (raced on epyc, rocm, cuda, h200; one task per model × repeat for fits, per cell group for metrics). Results `results/paper_final/horizons/*.json` (aggregates only); row-level outputs on the cluster under `feasibility/paper_plan/killcoyne_mm/horizons/`. Figures in `results/paper_final/horizons/figs/` as PNG and PDF with their numbers in JSON: time-dependent AUROC per arm at 1/3/5 years; H2 reclassification; H3 weights by horizon with CIs; H4 probability stability by depth.

---

## Results

Pre-specification commit ee51db8 (this file above the line, and amendment 2 of `docs/aceb_analysis_plan.md`); results commit 4d7efa9.
Scripts: `scripts/paper_plan/hz_prep.py` (H0 event times), `hz_fit.R` (new outer-CV arms and the nested inner CV), `hz_metrics.py` (H1), `hz_stack.py` (H2, H3), `hz_qc.R` and `hz_slides.py` (H2 descriptors), `hz_aceb_fill.py` (ACE-B code path), `hz_search.py` and `hz_search_shard.py` (H4), `hz_figs.py`, `hz_render.py`. All run through `scripts/cluster/campaign.sh` (prefixes hzp, hzf, hzd, hzm, hz2, hzs, hzss).
Results: `results/paper_final/horizons/h1_{their,pkg}_{pre,pre_ndbe,pre_nofallback}.json`, `h2.json`, `h3_{their,pkg}.json`, `h1_aceb_dummy_check.json`, `h4_search.json`; figures `results/paper_final/horizons/figs/*.{png,pdf,json}`. Row-level outputs on the cluster only, under `feasibility/paper_plan/killcoyne_mm/horizons/` (including the H2 patient list `h2_patient_list.csv`).

### Status

| Item | Status |
|---|---|
| H0 pre-specification, event times, horizon labels | DONE |
| H1 horizon table (internal); ACE-B columns | DONE; ACE-B NOT AVAILABLE (code path checked on dummy labels) |
| H2 change in false positives | DONE |
| H3 WSI vs CNV weighting by horizon | DONE |
| H4 depth transfer | 4× → external NOT AVAILABLE; ACE-B depth check NOT AVAILABLE |

**Design caveat.** The discovery cohort is a matched case–control design (non-progressors needed ≥ 3 years of follow-up, progressors ≥ 1 year). AUROCs are interpretable; absolute risks, calibration and positive predictive values are not, and none is reported.

### H1 table

Per-sample IPCW time-dependent AUROC [95% patient-bootstrap CI] (n cases / n controls), all pre-event samples of the discovery subset, CNV source their matrix. Clinical only = L-GRADE; L-GRADE+age+sex and the package-feature source are in H1 below. ACE-B: no slides, outcomes blinded.

|  | Internal 1-y | 3-y | 5-y | ACE-B 1-y | 3-y | 5-y |
|---|---|---|---|---|---|---|
| Clinical only | 0.682 [0.543, 0.801] (29/449) | 0.460 [0.334, 0.597] (99/277) | 0.439 [0.337, 0.554] (126/168) | NOT AVAILABLE | NOT AVAILABLE | NOT AVAILABLE |
| CNV (replication) | 0.815 [0.698, 0.923] (29/449) | 0.775 [0.683, 0.860] (99/277) | 0.792 [0.698, 0.871] (126/168) | NOT AVAILABLE | NOT AVAILABLE | NOT AVAILABLE |
| WSI | 0.782 [0.668, 0.869] (29/449) | 0.817 [0.731, 0.894] (99/277) | 0.786 [0.714, 0.856] (126/168) | NOT AVAILABLE | NOT AVAILABLE | NOT AVAILABLE |
| Early fusion | 0.853 [0.756, 0.931] (29/449) | 0.828 [0.747, 0.902] (99/277) | 0.820 [0.745, 0.886] (126/168) | NOT AVAILABLE | NOT AVAILABLE | NOT AVAILABLE |
| Intermediate fusion | 0.829 [0.737, 0.915] (29/449) | 0.818 [0.734, 0.898] (99/277) | 0.787 [0.697, 0.872] (126/168) | NOT AVAILABLE | NOT AVAILABLE | NOT AVAILABLE |
| Late fusion | 0.869 [0.806, 0.921] (29/449) | 0.855 [0.778, 0.922] (99/277) | 0.844 [0.777, 0.902] (126/168) | NOT AVAILABLE | NOT AVAILABLE | NOT AVAILABLE |

### H0. Time origin, event, horizon labels

**Question.** Which samples and labels enter each horizon? **Status.** DONE. **Pre-specification.** Above (H0).

**Result.** n per horizon (samples are the prediction unit; the patient unit is each patient's earliest pre-event NDBE sample):

| Population | Unit | Horizon | Rows | Patients | Event rows / patients | Cases | Controls | Excluded (censored before t) |
|---|---|---|---|---|---|---|---|---|
| all pre-event samples | sample | 1 y | 571 | 75 | 161 / 32 | 29 (14 patients) | 449 (72 patients) | 93 |
| all pre-event samples | sample | 3 y | 571 | 75 | 161 / 32 | 99 (29 patients) | 277 (62 patients) | 195 |
| all pre-event samples | sample | 5 y | 571 | 75 | 161 / 32 | 126 (32 patients) | 168 (46 patients) | 277 |
| all pre-event samples | patient | 1 y | 71 | 71 | 28 / 28 | 2 (2 patients) | 69 (69 patients) | 0 |
| all pre-event samples | patient | 3 y | 71 | 71 | 28 / 28 | 9 (9 patients) | 59 (59 patients) | 3 |
| all pre-event samples | patient | 5 y | 71 | 71 | 28 / 28 | 15 (15 patients) | 39 (39 patients) | 17 |
| NDBE pre-event samples | sample | 1 y | 438 | 71 | 104 / 28 | 12 (9 patients) | 334 (69 patients) | 92 |
| NDBE pre-event samples | sample | 3 y | 438 | 71 | 104 / 28 | 61 (25 patients) | 192 (59 patients) | 185 |
| NDBE pre-event samples | sample | 5 y | 438 | 71 | 104 / 28 | 79 (26 patients) | 111 (39 patients) | 248 |
| all pre-event samples, without the 4 fallback-endpoint progressors | sample | 1 y | 562 | 71 | 152 / 28 | 28 (13 patients) | 441 (68 patients) | 93 |
| all pre-event samples, without the 4 fallback-endpoint progressors | sample | 3 y | 562 | 71 | 152 / 28 | 96 (27 patients) | 271 (59 patients) | 195 |
| all pre-event samples, without the 4 fallback-endpoint progressors | sample | 5 y | 562 | 71 | 152 / 28 | 120 (28 patients) | 165 (44 patients) | 277 |

The patient unit is the same in both populations (an earliest NDBE pre-event sample is by definition in both), so it is reported once. The 4 progressors without an HGD/IMC sample among the published samples have their endpoint at the final endoscopy (`kc_merge.py` fallback), flagged in `samples.csv`; the H1 cells without them are under H1.
**Method.** `hz_prep.py`: `mbf` = `Months before final` of the 777 sheet; progressor time = (`mbf` − `tev`)/12 with `tev` the largest `mbf` among the patient's HGD/IMC samples (`kc_merge.py:30-32`); non-progressor time = `mbf`/12, censored. Pre-event = `mbf` > `tev` for progressors, all non-progressor samples (571 samples, 75 patients, 32 P, the `b_before_first_HGD_IMC` subset of `kv_merge.py`).
**Sources.** `feasibility/paper_plan/killcoyne_mm/set_C.csv`, `feasibility/paper_plan/killcoyne/kr_samples.csv`, `[SWG]/sWGS_777_samples_cleaned_202401_Leanne_fullDetails (3) (1).csv`, `[SWG]/Demographics_full.csv`; `h1_*.json:units.*.horizons.*.n_*`.
**Caveats.** `Months before final` is the only time scale available for every sample; it is in whole months. Controls at t include progressor samples whose event is later than t.

### H1. Horizon table, all arms

**Question.** How well do the ever-progression scores rank near-term against later events? **Status.** DONE (internal); ACE-B NOT AVAILABLE. **Pre-specification.** Above (H1). L-INTER and L-GRADE+age+sex were fitted under the stratified CV for this task (`hz_fit.R` MODE=outer); their folds match `kv_cv.R` for 6760 of 6760 sample × repeat rows. Every other arm is the existing out-of-fold prediction, not refitted.

**their matrix, all pre-event samples** (571 samples, 75 patients, 32 progressors), per sample.

| Horizon | Arm | Cases/controls | IPCW AUROC [CI] | Unweighted AUROC [CI] | Δ vs L-CNV [CI] | Δ vs L-LATE [CI] | p (swap) | p max-T |
|---|---|---|---|---|---|---|---|---|
| 1 y | L-GRADE | 29/449 | 0.682 [0.543, 0.801] | 0.682 [0.543, 0.801] | -0.134 [-0.343, +0.056] | -0.188 [-0.341, -0.055] | 0.002 | 0.0025 |
| 1 y | L-GRADE+age+sex | 29/449 | 0.680 [0.541, 0.802] | 0.680 [0.541, 0.802] | -0.135 [-0.347, +0.052] | -0.189 [-0.350, -0.049] | 0.0015 | 0.0015 |
| 1 y | L-CNV | 29/449 | 0.815 [0.698, 0.923] | 0.815 [0.698, 0.923] | — | -0.054 [-0.151, +0.043] | 0.3738 | 0.7776 |
| 1 y | L-IMG | 29/449 | 0.782 [0.668, 0.869] | 0.782 [0.668, 0.869] | -0.033 [-0.217, +0.136] | -0.087 [-0.182, -0.009] | 0.066 | 0.3513 |
| 1 y | L-EARLY | 29/449 | 0.853 [0.756, 0.931] | 0.853 [0.756, 0.931] | +0.037 [-0.030, +0.105] | -0.017 [-0.078, +0.042] | 0.8416 | 0.999 |
| 1 y | L-INTER | 29/449 | 0.829 [0.737, 0.915] | 0.829 [0.736, 0.915] | +0.013 [-0.067, +0.091] | -0.041 [-0.102, +0.026] | 0.3638 | 0.915 |
| 1 y | L-LATE | 29/449 | 0.869 [0.806, 0.921] | 0.869 [0.806, 0.921] | +0.054 [-0.043, +0.151] | — | — | — |
| 3 y | L-GRADE | 99/277 | 0.460 [0.334, 0.597] | 0.471 [0.345, 0.603] | -0.315 [-0.470, -0.149] | -0.395 [-0.510, -0.277] | 0.0005 | 0.0005 |
| 3 y | L-GRADE+age+sex | 99/277 | 0.445 [0.321, 0.577] | 0.456 [0.333, 0.585] | -0.330 [-0.489, -0.161] | -0.409 [-0.531, -0.288] | 0.0005 | 0.0005 |
| 3 y | L-CNV | 99/277 | 0.775 [0.683, 0.860] | 0.775 [0.683, 0.863] | — | -0.080 [-0.157, -0.015] | 0.027 | 0.3188 |
| 3 y | L-IMG | 99/277 | 0.817 [0.731, 0.894] | 0.816 [0.730, 0.892] | +0.041 [-0.061, +0.147] | -0.038 [-0.084, +0.001] | 0.1444 | 0.8386 |
| 3 y | L-EARLY | 99/277 | 0.828 [0.747, 0.902] | 0.828 [0.747, 0.902] | +0.052 [+0.002, +0.113] | -0.027 [-0.067, +0.010] | 0.3268 | 0.943 |
| 3 y | L-INTER | 99/277 | 0.818 [0.734, 0.898] | 0.817 [0.734, 0.897] | +0.043 [-0.033, +0.127] | -0.037 [-0.083, +0.012] | 0.2584 | 0.8521 |
| 3 y | L-LATE | 99/277 | 0.855 [0.778, 0.922] | 0.855 [0.778, 0.923] | +0.080 [+0.015, +0.157] | — | — | — |
| 5 y | L-GRADE | 126/168 | 0.439 [0.337, 0.554] | 0.453 [0.350, 0.572] | -0.353 [-0.485, -0.203] | -0.406 [-0.508, -0.295] | 0.0005 | 0.0005 |
| 5 y | L-GRADE+age+sex | 126/168 | 0.430 [0.330, 0.545] | 0.444 [0.342, 0.562] | -0.362 [-0.494, -0.211] | -0.414 [-0.520, -0.302] | 0.0005 | 0.0005 |
| 5 y | L-CNV | 126/168 | 0.792 [0.698, 0.871] | 0.792 [0.696, 0.873] | — | -0.053 [-0.131, +0.011] | 0.1384 | 0.7021 |
| 5 y | L-IMG | 126/168 | 0.786 [0.714, 0.856] | 0.795 [0.722, 0.864] | -0.005 [-0.111, +0.115] | -0.058 [-0.109, -0.004] | 0.056 | 0.6297 |
| 5 y | L-EARLY | 126/168 | 0.820 [0.745, 0.886] | 0.823 [0.745, 0.891] | +0.029 [-0.027, +0.095] | -0.024 [-0.076, +0.026] | 0.4588 | 0.9805 |
| 5 y | L-INTER | 126/168 | 0.787 [0.697, 0.872] | 0.793 [0.704, 0.875] | -0.004 [-0.086, +0.081] | -0.057 [-0.123, +0.006] | 0.2069 | 0.6432 |
| 5 y | L-LATE | 126/168 | 0.844 [0.777, 0.902] | 0.851 [0.784, 0.908] | +0.053 [-0.011, +0.131] | — | — | — |

**their matrix, NDBE pre-event samples** (438 samples, 71 patients, 28 progressors), per sample.

| Horizon | Arm | Cases/controls | IPCW AUROC [CI] | Unweighted AUROC [CI] | Δ vs L-CNV [CI] | Δ vs L-LATE [CI] | p (swap) | p max-T |
|---|---|---|---|---|---|---|---|---|
| 1 y | L-GRADE | 12/334 | 0.459 [0.224, 0.656] | 0.459 [0.225, 0.656] | -0.414 [-0.633, -0.228] | -0.411 [-0.620, -0.240] | 0.0015 | 0.0015 |
| 1 y | L-GRADE+age+sex | 12/334 | 0.454 [0.211, 0.647] | 0.454 [0.211, 0.647] | -0.420 [-0.652, -0.232] | -0.416 [-0.643, -0.234] | 0.001 | 0.001 |
| 1 y | L-CNV | 12/334 | 0.873 [0.761, 0.948] | 0.873 [0.761, 0.948] | — | +0.003 [-0.088, +0.076] | 0.943 | 1.0 |
| 1 y | L-IMG | 12/334 | 0.731 [0.575, 0.865] | 0.731 [0.575, 0.865] | -0.143 [-0.321, +0.039] | -0.139 [-0.254, -0.037] | 0.033 | 0.3618 |
| 1 y | L-EARLY | 12/334 | 0.889 [0.802, 0.952] | 0.889 [0.802, 0.952] | +0.015 [-0.023, +0.067] | +0.019 [-0.044, +0.091] | 0.6282 | 1.0 |
| 1 y | L-INTER | 12/334 | 0.881 [0.783, 0.943] | 0.881 [0.783, 0.943] | +0.008 [-0.056, +0.089] | +0.011 [-0.063, +0.082] | 0.7826 | 1.0 |
| 1 y | L-LATE | 12/334 | 0.870 [0.782, 0.932] | 0.870 [0.782, 0.932] | -0.003 [-0.076, +0.088] | — | — | — |
| 3 y | L-GRADE | 61/192 | 0.282 [0.172, 0.416] | 0.293 [0.178, 0.433] | -0.490 [-0.634, -0.323] | -0.541 [-0.677, -0.391] | 0.0005 | 0.0005 |
| 3 y | L-GRADE+age+sex | 61/192 | 0.264 [0.159, 0.395] | 0.274 [0.165, 0.406] | -0.508 [-0.655, -0.333] | -0.560 [-0.695, -0.407] | 0.0005 | 0.0005 |
| 3 y | L-CNV | 61/192 | 0.772 [0.659, 0.878] | 0.769 [0.648, 0.878] | — | -0.051 [-0.133, +0.010] | 0.1589 | 0.8221 |
| 3 y | L-IMG | 61/192 | 0.780 [0.684, 0.876] | 0.776 [0.684, 0.872] | +0.008 [-0.092, +0.125] | -0.044 [-0.092, +0.001] | 0.1634 | 0.8866 |
| 3 y | L-EARLY | 61/192 | 0.826 [0.727, 0.918] | 0.825 [0.723, 0.920] | +0.054 [+0.002, +0.120] | +0.002 [-0.032, +0.034] | 0.9255 | 1.0 |
| 3 y | L-INTER | 61/192 | 0.812 [0.692, 0.924] | 0.812 [0.692, 0.923] | +0.040 [-0.057, +0.150] | -0.012 [-0.082, +0.053] | 0.8401 | 0.999 |
| 3 y | L-LATE | 61/192 | 0.823 [0.728, 0.920] | 0.820 [0.723, 0.919] | +0.051 [-0.010, +0.133] | — | — | — |
| 5 y | L-GRADE | 79/111 | 0.269 [0.154, 0.409] | 0.278 [0.159, 0.421] | -0.494 [-0.657, -0.296] | -0.524 [-0.672, -0.351] | 0.0005 | 0.0005 |
| 5 y | L-GRADE+age+sex | 79/111 | 0.260 [0.150, 0.395] | 0.269 [0.153, 0.408] | -0.503 [-0.660, -0.308] | -0.532 [-0.678, -0.357] | 0.0005 | 0.0005 |
| 5 y | L-CNV | 79/111 | 0.763 [0.654, 0.859] | 0.763 [0.654, 0.863] | — | -0.029 [-0.107, +0.037] | 0.4693 | 0.973 |
| 5 y | L-IMG | 79/111 | 0.744 [0.651, 0.824] | 0.749 [0.655, 0.833] | -0.019 [-0.139, +0.106] | -0.048 [-0.108, +0.013] | 0.1609 | 0.8596 |
| 5 y | L-EARLY | 79/111 | 0.788 [0.700, 0.871] | 0.794 [0.701, 0.880] | +0.025 [-0.044, +0.109] | -0.004 [-0.064, +0.057] | 0.8936 | 1.0 |
| 5 y | L-INTER | 79/111 | 0.770 [0.654, 0.873] | 0.778 [0.660, 0.883] | +0.008 [-0.085, +0.108] | -0.022 [-0.105, +0.056] | 0.6582 | 0.9925 |
| 5 y | L-LATE | 79/111 | 0.792 [0.707, 0.865] | 0.798 [0.711, 0.875] | +0.029 [-0.037, +0.107] | — | — | — |

**their matrix, all pre-event samples, without the 4 fallback-endpoint progressors** (562 samples, 71 patients, 28 progressors), per sample.

| Horizon | Arm | Cases/controls | IPCW AUROC [CI] | Unweighted AUROC [CI] | Δ vs L-CNV [CI] | Δ vs L-LATE [CI] | p (swap) | p max-T |
|---|---|---|---|---|---|---|---|---|
| 1 y | L-GRADE | 28/441 | 0.694 [0.545, 0.816] | 0.694 [0.545, 0.816] | -0.117 [-0.339, +0.075] | -0.175 [-0.332, -0.040] | 0.004 | 0.0045 |
| 1 y | L-GRADE+age+sex | 28/441 | 0.698 [0.557, 0.828] | 0.699 [0.557, 0.827] | -0.113 [-0.327, +0.086] | -0.170 [-0.330, -0.028] | 0.006 | 0.006 |
| 1 y | L-CNV | 28/441 | 0.811 [0.690, 0.925] | 0.811 [0.690, 0.925] | — | -0.057 [-0.154, +0.045] | 0.3293 | 0.7441 |
| 1 y | L-IMG | 28/441 | 0.785 [0.664, 0.873] | 0.785 [0.664, 0.873] | -0.026 [-0.222, +0.140] | -0.083 [-0.182, -0.006] | 0.0825 | 0.3663 |
| 1 y | L-EARLY | 28/441 | 0.850 [0.752, 0.934] | 0.850 [0.752, 0.934] | +0.039 [-0.030, +0.114] | -0.018 [-0.083, +0.043] | 0.8286 | 0.999 |
| 1 y | L-INTER | 28/441 | 0.827 [0.730, 0.919] | 0.826 [0.730, 0.919] | +0.015 [-0.070, +0.100] | -0.042 [-0.107, +0.027] | 0.3523 | 0.9155 |
| 1 y | L-LATE | 28/441 | 0.868 [0.803, 0.920] | 0.868 [0.803, 0.920] | +0.057 [-0.045, +0.154] | — | — | — |
| 3 y | L-GRADE | 96/271 | 0.462 [0.324, 0.600] | 0.474 [0.337, 0.611] | -0.315 [-0.482, -0.147] | -0.392 [-0.523, -0.277] | 0.0005 | 0.0005 |
| 3 y | L-GRADE+age+sex | 96/271 | 0.451 [0.317, 0.586] | 0.462 [0.330, 0.594] | -0.326 [-0.494, -0.160] | -0.404 [-0.536, -0.287] | 0.0005 | 0.0005 |
| 3 y | L-CNV | 96/271 | 0.777 [0.684, 0.866] | 0.777 [0.685, 0.867] | — | -0.077 [-0.152, -0.013] | 0.034 | 0.3413 |
| 3 y | L-IMG | 96/271 | 0.817 [0.727, 0.893] | 0.817 [0.727, 0.891] | +0.040 [-0.065, +0.147] | -0.037 [-0.086, +0.005] | 0.1574 | 0.8531 |
| 3 y | L-EARLY | 96/271 | 0.825 [0.746, 0.905] | 0.825 [0.744, 0.907] | +0.049 [+0.000, +0.112] | -0.029 [-0.066, +0.011] | 0.2959 | 0.9375 |
| 3 y | L-INTER | 96/271 | 0.814 [0.727, 0.901] | 0.813 [0.727, 0.900] | +0.037 [-0.038, +0.123] | -0.041 [-0.087, +0.009] | 0.2139 | 0.8001 |
| 3 y | L-LATE | 96/271 | 0.854 [0.772, 0.924] | 0.855 [0.774, 0.923] | +0.077 [+0.013, +0.152] | — | — | — |
| 5 y | L-GRADE | 120/165 | 0.438 [0.318, 0.550] | 0.454 [0.332, 0.568] | -0.365 [-0.505, -0.215] | -0.422 [-0.538, -0.317] | 0.0005 | 0.0005 |
| 5 y | L-GRADE+age+sex | 120/165 | 0.432 [0.314, 0.542] | 0.448 [0.331, 0.562] | -0.371 [-0.514, -0.221] | -0.427 [-0.547, -0.318] | 0.0005 | 0.0005 |
| 5 y | L-CNV | 120/165 | 0.803 [0.710, 0.884] | 0.800 [0.708, 0.885] | — | -0.057 [-0.138, +0.006] | 0.1229 | 0.6857 |
| 5 y | L-IMG | 120/165 | 0.796 [0.720, 0.866] | 0.803 [0.726, 0.872] | -0.007 [-0.115, +0.117] | -0.064 [-0.114, -0.013] | 0.0385 | 0.5922 |
| 5 y | L-EARLY | 120/165 | 0.823 [0.749, 0.893] | 0.824 [0.748, 0.897] | +0.020 [-0.032, +0.086] | -0.036 [-0.086, +0.012] | 0.2534 | 0.9195 |
| 5 y | L-INTER | 120/165 | 0.793 [0.702, 0.882] | 0.795 [0.705, 0.885] | -0.010 [-0.092, +0.073] | -0.067 [-0.137, -0.002] | 0.1409 | 0.5437 |
| 5 y | L-LATE | 120/165 | 0.860 [0.794, 0.916] | 0.862 [0.796, 0.920] | +0.057 [-0.006, +0.138] | — | — | — |

**their matrix, patient unit** (earliest pre-event NDBE sample; 71 patients, 28 progressors).

| Horizon | Arm | Cases/controls | IPCW AUROC [CI] | Δ vs L-CNV [CI] | Δ vs L-LATE [CI] |
|---|---|---|---|---|---|
| 1 y | L-GRADE | 2/69 | 0.754 [0.471, 0.986] | -0.181 [-0.456, +0.043] | -0.087 [-0.319, +0.100] |
| 1 y | L-GRADE+age+sex | 2/69 | 0.826 [0.637, 0.971] | -0.109 [-0.292, +0.029] | -0.014 [-0.171, +0.100] |
| 1 y | L-CNV | 2/69 | 0.935 [0.857, 0.986] | — | +0.094 [+0.000, +0.203] |
| 1 y | L-IMG | 2/69 | 0.565 [0.371, 0.754] | -0.370 [-0.543, -0.200] | -0.275 [-0.398, -0.164] |
| 1 y | L-EARLY | 2/69 | 0.906 [0.797, 0.986] | -0.029 [-0.157, +0.087] | +0.065 [-0.103, +0.257] |
| 1 y | L-INTER | 2/69 | 0.891 [0.814, 0.957] | -0.043 [-0.116, +0.014] | +0.051 [-0.071, +0.200] |
| 1 y | L-LATE | 2/69 | 0.841 [0.700, 0.957] | -0.094 [-0.203, +0.000] | — |
| 3 y | L-GRADE | 9/59 | 0.393 [0.149, 0.642] | -0.375 [-0.605, -0.160] | -0.427 [-0.642, -0.211] |
| 3 y | L-GRADE+age+sex | 9/59 | 0.369 [0.121, 0.640] | -0.398 [-0.617, -0.180] | -0.451 [-0.678, -0.214] |
| 3 y | L-CNV | 9/59 | 0.767 [0.548, 0.934] | — | -0.053 [-0.169, +0.054] |
| 3 y | L-IMG | 9/59 | 0.802 [0.657, 0.913] | +0.035 [-0.179, +0.251] | -0.018 [-0.139, +0.093] |
| 3 y | L-EARLY | 9/59 | 0.831 [0.661, 0.963] | +0.064 [-0.044, +0.181] | +0.012 [-0.094, +0.127] |
| 3 y | L-INTER | 9/59 | 0.885 [0.779, 0.962] | +0.118 [-0.017, +0.290] | +0.065 [-0.026, +0.176] |
| 3 y | L-LATE | 9/59 | 0.820 [0.675, 0.933] | +0.053 [-0.054, +0.169] | — |
| 5 y | L-GRADE | 15/39 | 0.434 [0.248, 0.615] | -0.291 [-0.511, -0.072] | -0.330 [-0.554, -0.088] |
| 5 y | L-GRADE+age+sex | 15/39 | 0.406 [0.231, 0.591] | -0.319 [-0.527, -0.105] | -0.358 [-0.570, -0.117] |
| 5 y | L-CNV | 15/39 | 0.725 [0.573, 0.864] | — | -0.039 [-0.149, +0.069] |
| 5 y | L-IMG | 15/39 | 0.749 [0.598, 0.880] | +0.024 [-0.169, +0.196] | -0.016 [-0.121, +0.081] |
| 5 y | L-EARLY | 15/39 | 0.730 [0.577, 0.857] | +0.005 [-0.121, +0.120] | -0.034 [-0.156, +0.080] |
| 5 y | L-INTER | 15/39 | 0.784 [0.655, 0.901] | +0.059 [-0.069, +0.192] | +0.020 [-0.091, +0.136] |
| 5 y | L-LATE | 15/39 | 0.764 [0.613, 0.889] | +0.039 [-0.069, +0.149] | — |

**package features, all pre-event samples** (571 samples, 75 patients, 32 progressors), per sample.

| Horizon | Arm | Cases/controls | IPCW AUROC [CI] | Unweighted AUROC [CI] | Δ vs L-CNV [CI] | Δ vs L-LATE [CI] | p (swap) | p max-T |
|---|---|---|---|---|---|---|---|---|
| 1 y | L-GRADE | 29/449 | 0.682 [0.543, 0.801] | 0.682 [0.543, 0.801] | -0.123 [-0.314, +0.041] | -0.171 [-0.320, -0.040] | 0.005 | 0.0065 |
| 1 y | L-GRADE+age+sex | 29/449 | 0.680 [0.541, 0.802] | 0.680 [0.541, 0.802] | -0.125 [-0.321, +0.041] | -0.172 [-0.331, -0.034] | 0.0045 | 0.0045 |
| 1 y | L-CNV | 29/449 | 0.805 [0.714, 0.895] | 0.805 [0.714, 0.895] | — | -0.048 [-0.123, +0.031] | 0.2784 | 0.7451 |
| 1 y | L-IMG | 29/449 | 0.782 [0.668, 0.869] | 0.782 [0.668, 0.869] | -0.022 [-0.176, +0.109] | -0.070 [-0.152, -0.007] | 0.0915 | 0.4278 |
| 1 y | L-EARLY | 29/449 | 0.836 [0.760, 0.900] | 0.836 [0.760, 0.900] | +0.031 [-0.032, +0.092] | -0.016 [-0.049, +0.018] | 0.4478 | 0.9955 |
| 1 y | L-INTER | 29/449 | 0.802 [0.719, 0.877] | 0.802 [0.719, 0.877] | -0.003 [-0.085, +0.073] | -0.051 [-0.104, +0.005] | 0.079 | 0.6972 |
| 1 y | L-LATE | 29/449 | 0.852 [0.782, 0.909] | 0.852 [0.782, 0.909] | +0.048 [-0.031, +0.123] | — | — | — |
| 3 y | L-GRADE | 99/277 | 0.460 [0.334, 0.597] | 0.471 [0.345, 0.603] | -0.320 [-0.461, -0.164] | -0.382 [-0.496, -0.265] | 0.0005 | 0.0005 |
| 3 y | L-GRADE+age+sex | 99/277 | 0.445 [0.321, 0.577] | 0.456 [0.333, 0.585] | -0.334 [-0.477, -0.175] | -0.396 [-0.516, -0.276] | 0.0005 | 0.0005 |
| 3 y | L-CNV | 99/277 | 0.779 [0.692, 0.850] | 0.779 [0.692, 0.850] | — | -0.062 [-0.121, -0.011] | 0.011 | 0.4378 |
| 3 y | L-IMG | 99/277 | 0.817 [0.731, 0.894] | 0.816 [0.730, 0.892] | +0.037 [-0.048, +0.125] | -0.025 [-0.065, +0.011] | 0.2474 | 0.9185 |
| 3 y | L-EARLY | 99/277 | 0.814 [0.724, 0.887] | 0.815 [0.727, 0.887] | +0.035 [-0.005, +0.076] | -0.028 [-0.060, +0.001] | 0.1544 | 0.8871 |
| 3 y | L-INTER | 99/277 | 0.822 [0.749, 0.890] | 0.821 [0.747, 0.888] | +0.042 [-0.012, +0.104] | -0.020 [-0.064, +0.023] | 0.4228 | 0.9675 |
| 3 y | L-LATE | 99/277 | 0.842 [0.760, 0.912] | 0.842 [0.761, 0.911] | +0.062 [+0.011, +0.121] | — | — | — |
| 5 y | L-GRADE | 126/168 | 0.439 [0.337, 0.554] | 0.453 [0.350, 0.572] | -0.358 [-0.490, -0.202] | -0.401 [-0.513, -0.281] | 0.0005 | 0.0005 |
| 5 y | L-GRADE+age+sex | 126/168 | 0.430 [0.330, 0.545] | 0.444 [0.342, 0.562] | -0.366 [-0.501, -0.215] | -0.409 [-0.522, -0.289] | 0.0005 | 0.0005 |
| 5 y | L-CNV | 126/168 | 0.796 [0.693, 0.878] | 0.796 [0.694, 0.874] | — | -0.043 [-0.103, +0.006] | 0.1524 | 0.7526 |
| 5 y | L-IMG | 126/168 | 0.786 [0.714, 0.856] | 0.795 [0.722, 0.864] | -0.010 [-0.109, +0.100] | -0.053 [-0.107, +0.004] | 0.079 | 0.6197 |
| 5 y | L-EARLY | 126/168 | 0.811 [0.712, 0.890] | 0.813 [0.715, 0.892] | +0.014 [-0.019, +0.048] | -0.029 [-0.074, +0.007] | 0.3333 | 0.9235 |
| 5 y | L-INTER | 126/168 | 0.803 [0.720, 0.871] | 0.804 [0.722, 0.872] | +0.006 [-0.051, +0.070] | -0.037 [-0.085, +0.012] | 0.2089 | 0.8386 |
| 5 y | L-LATE | 126/168 | 0.839 [0.760, 0.906] | 0.843 [0.765, 0.908] | +0.043 [-0.006, +0.103] | — | — | — |

**package features, NDBE pre-event samples** (438 samples, 71 patients, 28 progressors), per sample.

| Horizon | Arm | Cases/controls | IPCW AUROC [CI] | Unweighted AUROC [CI] | Δ vs L-CNV [CI] | Δ vs L-LATE [CI] | p (swap) | p max-T |
|---|---|---|---|---|---|---|---|---|
| 1 y | L-GRADE | 12/334 | 0.459 [0.224, 0.656] | 0.459 [0.225, 0.656] | -0.367 [-0.597, -0.168] | -0.378 [-0.580, -0.198] | 0.0025 | 0.004 |
| 1 y | L-GRADE+age+sex | 12/334 | 0.454 [0.211, 0.647] | 0.454 [0.211, 0.647] | -0.372 [-0.610, -0.170] | -0.383 [-0.610, -0.197] | 0.0025 | 0.0035 |
| 1 y | L-CNV | 12/334 | 0.826 [0.700, 0.913] | 0.826 [0.700, 0.913] | — | -0.011 [-0.105, +0.070] | 0.8091 | 1.0 |
| 1 y | L-IMG | 12/334 | 0.731 [0.575, 0.865] | 0.731 [0.575, 0.865] | -0.095 [-0.289, +0.093] | -0.106 [-0.225, +0.002] | 0.1544 | 0.5587 |
| 1 y | L-EARLY | 12/334 | 0.830 [0.734, 0.902] | 0.831 [0.734, 0.902] | +0.005 [-0.051, +0.074] | -0.007 [-0.064, +0.053] | 0.8516 | 1.0 |
| 1 y | L-INTER | 12/334 | 0.788 [0.683, 0.885] | 0.788 [0.683, 0.885] | -0.038 [-0.164, +0.098] | -0.049 [-0.138, +0.054] | 0.3943 | 0.962 |
| 1 y | L-LATE | 12/334 | 0.837 [0.745, 0.902] | 0.837 [0.745, 0.902] | +0.011 [-0.070, +0.105] | — | — | — |
| 3 y | L-GRADE | 61/192 | 0.282 [0.172, 0.416] | 0.293 [0.178, 0.433] | -0.467 [-0.613, -0.290] | -0.516 [-0.659, -0.356] | 0.0005 | 0.0005 |
| 3 y | L-GRADE+age+sex | 61/192 | 0.264 [0.159, 0.395] | 0.274 [0.165, 0.406] | -0.485 [-0.633, -0.315] | -0.534 [-0.676, -0.378] | 0.0005 | 0.0005 |
| 3 y | L-CNV | 61/192 | 0.749 [0.646, 0.851] | 0.745 [0.642, 0.848] | — | -0.049 [-0.108, -0.001] | 0.0545 | 0.7496 |
| 3 y | L-IMG | 61/192 | 0.780 [0.684, 0.876] | 0.776 [0.684, 0.872] | +0.031 [-0.059, +0.126] | -0.018 [-0.066, +0.028] | 0.5137 | 0.9915 |
| 3 y | L-EARLY | 61/192 | 0.776 [0.663, 0.883] | 0.774 [0.665, 0.879] | +0.027 [-0.014, +0.074] | -0.022 [-0.063, +0.010] | 0.4103 | 0.9795 |
| 3 y | L-INTER | 61/192 | 0.819 [0.729, 0.904] | 0.817 [0.729, 0.900] | +0.070 [+0.010, +0.147] | +0.021 [-0.033, +0.075] | 0.4943 | 0.984 |
| 3 y | L-LATE | 61/192 | 0.798 [0.702, 0.895] | 0.795 [0.700, 0.893] | +0.049 [+0.001, +0.108] | — | — | — |
| 5 y | L-GRADE | 79/111 | 0.269 [0.154, 0.409] | 0.278 [0.159, 0.421] | -0.490 [-0.667, -0.269] | -0.517 [-0.683, -0.334] | 0.0005 | 0.0005 |
| 5 y | L-GRADE+age+sex | 79/111 | 0.260 [0.150, 0.395] | 0.269 [0.153, 0.408] | -0.498 [-0.667, -0.280] | -0.525 [-0.683, -0.342] | 0.0005 | 0.0005 |
| 5 y | L-CNV | 79/111 | 0.758 [0.636, 0.859] | 0.757 [0.636, 0.858] | — | -0.027 [-0.093, +0.032] | 0.4568 | 0.975 |
| 5 y | L-IMG | 79/111 | 0.744 [0.651, 0.824] | 0.749 [0.655, 0.833] | -0.015 [-0.129, +0.112] | -0.042 [-0.102, +0.027] | 0.2424 | 0.8721 |
| 5 y | L-EARLY | 79/111 | 0.756 [0.631, 0.860] | 0.758 [0.634, 0.864] | -0.002 [-0.046, +0.046] | -0.029 [-0.089, +0.021] | 0.4338 | 0.963 |
| 5 y | L-INTER | 79/111 | 0.792 [0.692, 0.877] | 0.793 [0.693, 0.881] | +0.034 [-0.040, +0.119] | +0.007 [-0.058, +0.073] | 0.8556 | 1.0 |
| 5 y | L-LATE | 79/111 | 0.785 [0.690, 0.868] | 0.787 [0.691, 0.871] | +0.027 [-0.032, +0.093] | — | — | — |

**package features, all pre-event samples, without the 4 fallback-endpoint progressors** (562 samples, 71 patients, 28 progressors), per sample.

| Horizon | Arm | Cases/controls | IPCW AUROC [CI] | Unweighted AUROC [CI] | Δ vs L-CNV [CI] | Δ vs L-LATE [CI] | p (swap) | p max-T |
|---|---|---|---|---|---|---|---|---|
| 1 y | L-GRADE | 28/441 | 0.694 [0.545, 0.816] | 0.694 [0.545, 0.816] | -0.114 [-0.316, +0.062] | -0.162 [-0.314, -0.030] | 0.013 | 0.016 |
| 1 y | L-GRADE+age+sex | 28/441 | 0.698 [0.557, 0.828] | 0.699 [0.557, 0.827] | -0.109 [-0.303, +0.070] | -0.158 [-0.312, -0.016] | 0.018 | 0.019 |
| 1 y | L-CNV | 28/441 | 0.808 [0.711, 0.899] | 0.808 [0.711, 0.899] | — | -0.049 [-0.126, +0.031] | 0.2569 | 0.7431 |
| 1 y | L-IMG | 28/441 | 0.785 [0.664, 0.873] | 0.785 [0.664, 0.873] | -0.022 [-0.180, +0.113] | -0.071 [-0.158, -0.006] | 0.083 | 0.4148 |
| 1 y | L-EARLY | 28/441 | 0.837 [0.759, 0.903] | 0.837 [0.759, 0.903] | +0.030 [-0.031, +0.091] | -0.019 [-0.052, +0.016] | 0.3723 | 0.995 |
| 1 y | L-INTER | 28/441 | 0.805 [0.722, 0.879] | 0.805 [0.722, 0.879] | -0.003 [-0.090, +0.075] | -0.052 [-0.107, +0.003] | 0.093 | 0.7026 |
| 1 y | L-LATE | 28/441 | 0.856 [0.780, 0.917] | 0.856 [0.780, 0.917] | +0.049 [-0.031, +0.126] | — | — | — |
| 3 y | L-GRADE | 96/271 | 0.462 [0.324, 0.600] | 0.474 [0.337, 0.611] | -0.323 [-0.480, -0.160] | -0.382 [-0.514, -0.265] | 0.0005 | 0.0005 |
| 3 y | L-GRADE+age+sex | 96/271 | 0.451 [0.317, 0.586] | 0.462 [0.330, 0.594] | -0.335 [-0.491, -0.173] | -0.394 [-0.526, -0.274] | 0.0005 | 0.0005 |
| 3 y | L-CNV | 96/271 | 0.786 [0.691, 0.864] | 0.786 [0.692, 0.866] | — | -0.059 [-0.120, -0.006] | 0.0155 | 0.4783 |
| 3 y | L-IMG | 96/271 | 0.817 [0.727, 0.893] | 0.817 [0.727, 0.891] | +0.032 [-0.059, +0.121] | -0.027 [-0.068, +0.010] | 0.2259 | 0.9025 |
| 3 y | L-EARLY | 96/271 | 0.817 [0.725, 0.895] | 0.818 [0.729, 0.894] | +0.032 [-0.006, +0.075] | -0.027 [-0.060, +0.004] | 0.1864 | 0.9015 |
| 3 y | L-INTER | 96/271 | 0.821 [0.744, 0.889] | 0.820 [0.745, 0.887] | +0.035 [-0.021, +0.098] | -0.024 [-0.068, +0.020] | 0.3593 | 0.9395 |
| 3 y | L-LATE | 96/271 | 0.844 [0.759, 0.913] | 0.845 [0.760, 0.912] | +0.059 [+0.006, +0.120] | — | — | — |
| 5 y | L-GRADE | 120/165 | 0.438 [0.318, 0.550] | 0.454 [0.332, 0.568] | -0.381 [-0.533, -0.230] | -0.420 [-0.548, -0.302] | 0.0005 | 0.0005 |
| 5 y | L-GRADE+age+sex | 120/165 | 0.432 [0.314, 0.542] | 0.448 [0.331, 0.562] | -0.387 [-0.539, -0.238] | -0.426 [-0.555, -0.309] | 0.0005 | 0.0005 |
| 5 y | L-CNV | 120/165 | 0.819 [0.713, 0.902] | 0.814 [0.709, 0.900] | — | -0.039 [-0.106, +0.012] | 0.1919 | 0.8026 |
| 5 y | L-IMG | 120/165 | 0.796 [0.720, 0.866] | 0.803 [0.726, 0.872] | -0.023 [-0.123, +0.092] | -0.062 [-0.116, -0.007] | 0.0335 | 0.5087 |
| 5 y | L-EARLY | 120/165 | 0.827 [0.730, 0.908] | 0.826 [0.730, 0.907] | +0.008 [-0.024, +0.044] | -0.031 [-0.079, +0.006] | 0.2884 | 0.8986 |
| 5 y | L-INTER | 120/165 | 0.813 [0.730, 0.884] | 0.812 [0.732, 0.882] | -0.006 [-0.061, +0.059] | -0.045 [-0.096, +0.002] | 0.1344 | 0.7186 |
| 5 y | L-LATE | 120/165 | 0.858 [0.782, 0.921] | 0.857 [0.780, 0.921] | +0.039 [-0.012, +0.106] | — | — | — |

**package features, patient unit** (earliest pre-event NDBE sample; 71 patients, 28 progressors).

| Horizon | Arm | Cases/controls | IPCW AUROC [CI] | Δ vs L-CNV [CI] | Δ vs L-LATE [CI] |
|---|---|---|---|---|---|
| 1 y | L-GRADE | 2/69 | 0.754 [0.471, 0.986] | -0.123 [-0.471, +0.200] | -0.022 [-0.319, +0.257] |
| 1 y | L-GRADE+age+sex | 2/69 | 0.826 [0.637, 0.971] | -0.051 [-0.304, +0.186] | +0.051 [-0.171, +0.243] |
| 1 y | L-CNV | 2/69 | 0.877 [0.765, 0.971] | — | +0.101 [-0.014, +0.217] |
| 1 y | L-IMG | 2/69 | 0.565 [0.371, 0.754] | -0.312 [-0.557, -0.058] | -0.210 [-0.397, -0.029] |
| 1 y | L-EARLY | 2/69 | 0.841 [0.714, 0.943] | -0.036 [-0.100, +0.014] | +0.065 [-0.058, +0.186] |
| 1 y | L-INTER | 2/69 | 0.609 [0.321, 0.871] | -0.268 [-0.609, +0.029] | -0.167 [-0.443, +0.086] |
| 1 y | L-LATE | 2/69 | 0.775 [0.671, 0.870] | -0.101 [-0.217, +0.014] | — |
| 3 y | L-GRADE | 9/59 | 0.393 [0.149, 0.642] | -0.316 [-0.559, -0.058] | -0.401 [-0.629, -0.164] |
| 3 y | L-GRADE+age+sex | 9/59 | 0.369 [0.121, 0.640] | -0.339 [-0.560, -0.115] | -0.424 [-0.654, -0.173] |
| 3 y | L-CNV | 9/59 | 0.708 [0.513, 0.880] | — | -0.085 [-0.215, +0.033] |
| 3 y | L-IMG | 9/59 | 0.802 [0.657, 0.913] | +0.094 [-0.124, +0.300] | +0.008 [-0.108, +0.112] |
| 3 y | L-EARLY | 9/59 | 0.783 [0.630, 0.910] | +0.074 [-0.010, +0.173] | -0.011 [-0.104, +0.085] |
| 3 y | L-INTER | 9/59 | 0.787 [0.631, 0.912] | +0.078 [-0.129, +0.268] | -0.007 [-0.144, +0.118] |
| 3 y | L-LATE | 9/59 | 0.794 [0.652, 0.905] | +0.085 [-0.033, +0.215] | — |
| 5 y | L-GRADE | 15/39 | 0.434 [0.248, 0.615] | -0.238 [-0.468, +0.011] | -0.319 [-0.547, -0.077] |
| 5 y | L-GRADE+age+sex | 15/39 | 0.406 [0.231, 0.591] | -0.266 [-0.473, -0.038] | -0.347 [-0.559, -0.113] |
| 5 y | L-CNV | 15/39 | 0.672 [0.505, 0.826] | — | -0.081 [-0.177, +0.029] |
| 5 y | L-IMG | 15/39 | 0.749 [0.598, 0.880] | +0.077 [-0.119, +0.245] | -0.004 [-0.113, +0.089] |
| 5 y | L-EARLY | 15/39 | 0.684 [0.530, 0.821] | +0.012 [-0.094, +0.109] | -0.069 [-0.179, +0.033] |
| 5 y | L-INTER | 15/39 | 0.717 [0.585, 0.847] | +0.045 [-0.099, +0.198] | -0.035 [-0.157, +0.090] |
| 5 y | L-LATE | 15/39 | 0.753 [0.601, 0.879] | +0.081 [-0.029, +0.177] | — |

**C-index over all follow-up**, per sample.

| CNV source | Population | Arm | Harrell's C [CI] | Uno's C [CI] |
|---|---|---|---|---|
| their matrix | all pre-event samples | L-GRADE | 0.510 [0.411, 0.613] | 0.479 [0.382, 0.572] |
| their matrix | all pre-event samples | L-GRADE+age+sex | 0.499 [0.402, 0.601] | 0.474 [0.373, 0.568] |
| their matrix | all pre-event samples | L-CNV | 0.762 [0.684, 0.834] | 0.738 [0.650, 0.823] |
| their matrix | all pre-event samples | L-IMG | 0.778 [0.712, 0.838] | 0.752 [0.695, 0.820] |
| their matrix | all pre-event samples | L-EARLY | 0.802 [0.734, 0.869] | 0.793 [0.718, 0.862] |
| their matrix | all pre-event samples | L-INTER | 0.777 [0.705, 0.851] | 0.773 [0.698, 0.842] |
| their matrix | all pre-event samples | L-LATE | 0.824 [0.764, 0.877] | 0.802 [0.740, 0.862] |
| their matrix | NDBE pre-event samples | L-GRADE | 0.322 [0.210, 0.447] | 0.318 [0.206, 0.447] |
| their matrix | NDBE pre-event samples | L-GRADE+age+sex | 0.308 [0.199, 0.429] | 0.308 [0.191, 0.440] |
| their matrix | NDBE pre-event samples | L-CNV | 0.755 [0.657, 0.846] | 0.716 [0.614, 0.827] |
| their matrix | NDBE pre-event samples | L-IMG | 0.744 [0.671, 0.817] | 0.733 [0.666, 0.806] |
| their matrix | NDBE pre-event samples | L-EARLY | 0.796 [0.713, 0.876] | 0.769 [0.680, 0.856] |
| their matrix | NDBE pre-event samples | L-INTER | 0.778 [0.679, 0.874] | 0.761 [0.669, 0.846] |
| their matrix | NDBE pre-event samples | L-LATE | 0.793 [0.716, 0.867] | 0.772 [0.694, 0.853] |
| package features | all pre-event samples | L-GRADE | 0.510 [0.411, 0.613] | 0.479 [0.382, 0.572] |
| package features | all pre-event samples | L-GRADE+age+sex | 0.499 [0.402, 0.601] | 0.474 [0.373, 0.568] |
| package features | all pre-event samples | L-CNV | 0.764 [0.690, 0.832] | 0.775 [0.695, 0.844] |
| package features | all pre-event samples | L-IMG | 0.778 [0.712, 0.838] | 0.752 [0.695, 0.820] |
| package features | all pre-event samples | L-EARLY | 0.794 [0.724, 0.860] | 0.801 [0.725, 0.870] |
| package features | all pre-event samples | L-INTER | 0.787 [0.723, 0.846] | 0.796 [0.726, 0.854] |
| package features | all pre-event samples | L-LATE | 0.817 [0.751, 0.873] | 0.822 [0.756, 0.882] |
| package features | NDBE pre-event samples | L-GRADE | 0.322 [0.210, 0.447] | 0.318 [0.206, 0.447] |
| package features | NDBE pre-event samples | L-GRADE+age+sex | 0.308 [0.199, 0.429] | 0.308 [0.191, 0.440] |
| package features | NDBE pre-event samples | L-CNV | 0.738 [0.648, 0.829] | 0.754 [0.665, 0.840] |
| package features | NDBE pre-event samples | L-IMG | 0.744 [0.671, 0.817] | 0.733 [0.666, 0.806] |
| package features | NDBE pre-event samples | L-EARLY | 0.757 [0.661, 0.847] | 0.772 [0.677, 0.863] |
| package features | NDBE pre-event samples | L-INTER | 0.785 [0.705, 0.862] | 0.796 [0.715, 0.869] |
| package features | NDBE pre-event samples | L-LATE | 0.778 [0.700, 0.854] | 0.795 [0.711, 0.872] |

**ACE-B columns.** NOT AVAILABLE: no ACE-B slides on the cluster and outcomes blinded. Code path: `scripts/paper_plan/hz_aceb_fill.py --cnv-tiles TILES.csv --cnv-arms ARMS.csv --img IMG.csv --labels LABELS.csv --out results/aceb/horizons.json` builds the package CNV block from raw tiles with the frozen constants of `models/killcoyne_frozen_pkg_v1` (model_info.json preprocessing), scores L-CNV, L-IMG, L-EARLY and L-LATE with the frozen coefficients, and computes the H1 metrics (IPCW and unweighted AUROC at 1/3/5 years, deltas, max-T over the three arms vs L-LATE, C-indices; all ACE-B samples and NDBE if an `ndbe` column is supplied). L-GRADE, L-GRADE+age+sex and L-INTER have no frozen model, so those ACE-B cells stay NOT AVAILABLE even after unblinding. End-to-end check (`--dummy`, `h1_aceb_dummy_check.json`): set C feature blocks as stand-in inputs, dummy labels (uniform times, 20% events, `RandomState(0)`), 200 bootstrap draws: it ran; the frozen L-CNV in-sample AUROC on set C is 0.995 (bundle `model_info.json`: 0.995); dummy 3-year L-LATE IPCW AUROC 0.510 (chance, as expected). No ACE-B label was read.

**Method.** `hz_metrics.py`: IPCW cumulative/dynamic AUROC with Ĝ the reverse Kaplan–Meier over the evaluated samples, re-estimated in each of 2,000 patient-bootstrap draws (`RandomState(0)`); paired deltas on the same draws; within-patient swap permutation (2,000, seed 0) with one mask per permutation shared by the 6 arm-vs-L-LATE pairs (single-step max-T). Scores = mean of the 10 repeats' out-of-fold probabilities.
**Sources.** `feasibility/paper_plan/killcoyne_mm/cv/preds/cfg_0{0..5}_rep_*.csv` (kv_cv.R, results commit d69de24), `feasibility/paper_plan/killcoyne_mm/horizons/outer/*.csv` (hz_fit.R); `h1_*.json`.
**Caveats.** (1) The models were trained on ever-progression with all of a progressor's samples labelled 1, so a near-term vs later contrast is a re-use of those scores, not a horizon-trained model. (2) Censoring is light before 3 years by design (non-progressors were selected for ≥ 3 years of follow-up), so IPCW and unweighted AUROCs are close. (3) L-GRADE and L-GRADE+age+sex fall below 0.5 at 3 and 5 years: the stratified-CV fold-prevalence artefact documented in `docs/paper_plan_killcoyne_cv.md` (intercept-only model 0.244–0.288) acts on a near-constant score. (4) The patient unit has 2 cases at 1 year; its 1-year cells are not informative.

### H2. Change in false positives

**Question.** At fixed operating points, does fusion change false positives against L-CNV? **Status.** DONE. **Pre-specification.** Above (H2). **Best model from H1** (highest mean per-sample IPCW AUROC over 1/3/5 years, all pre-event samples, their matrix): L-LATE (L-IMG 0.795, L-EARLY 0.834, L-INTER 0.811, L-LATE 0.856); the best model and L-LATE are therefore the same comparison.

Operating point (a) thresholds (80% sensitivity on the inner out-of-fold predictions of each outer training fold; 100 fold × repeat thresholds): their L-CNV median 0.270 (range 0.131–0.443); their L-LATE median 0.370 (range 0.278–0.471); pkg L-CNV median 0.303 (range 0.180–0.473); pkg L-LATE median 0.397 (range 0.321–0.475).

| CNV source | Operating point | Population | Horizon | Cases/controls | L-CNV TPR / FPR | L-LATE TPR / FPR | ΔTPR [CI] | ΔFPR [CI] | Categorical NRI [CI] |
|---|---|---|---|---|---|---|---|---|---|
| their matrix | (a) 80% sens. | all pre-event samples | 1 y | 29/449 | 0.828 / 0.450 | 0.966 / 0.334 | +0.138 [-0.067, +0.333] | -0.116 [-0.191, -0.038] | +0.254 [+0.040, +0.461] |
| their matrix | (a) 80% sens. | all pre-event samples | 3 y | 99/277 | 0.798 / 0.408 | 0.838 / 0.292 | +0.040 [-0.096, +0.180] | -0.116 [-0.200, -0.028] | +0.156 [-0.012, +0.327] |
| their matrix | (a) 80% sens. | all pre-event samples | 5 y | 126/168 | 0.802 / 0.363 | 0.817 / 0.298 | +0.016 [-0.092, +0.137] | -0.065 [-0.160, +0.042] | +0.081 [-0.064, +0.232] |
| their matrix | (a) 80% sens. | patient unit | 1 y | 2/69 | 1.000 / 0.348 | 1.000 / 0.377 | +0.000 [+0.000, +0.000] | +0.029 [-0.086, +0.143] | -0.029 [-0.144, +0.086] |
| their matrix | (a) 80% sens. | patient unit | 3 y | 9/59 | 0.778 / 0.322 | 0.889 / 0.322 | +0.111 [+0.000, +0.364] | +0.000 [-0.125, +0.121] | +0.111 [-0.088, +0.398] |
| their matrix | (a) 80% sens. | patient unit | 5 y | 15/39 | 0.733 / 0.308 | 0.733 / 0.385 | +0.000 [-0.273, +0.263] | +0.077 [-0.075, +0.231] | -0.077 [-0.391, +0.223] |
| their matrix | (a) 80% sens. | NDBE pre-event samples | 1 y | 12/334 | 0.917 / 0.416 | 1.000 / 0.314 | +0.083 [+0.000, +0.300] | -0.102 [-0.178, -0.027] | +0.185 [+0.048, +0.411] |
| their matrix | (a) 80% sens. | NDBE pre-event samples | 3 y | 61/192 | 0.787 / 0.391 | 0.787 / 0.302 | +0.000 [-0.141, +0.152] | -0.089 [-0.172, +0.000] | +0.089 [-0.073, +0.271] |
| their matrix | (a) 80% sens. | NDBE pre-event samples | 5 y | 79/111 | 0.785 / 0.369 | 0.759 / 0.333 | -0.025 [-0.139, +0.100] | -0.036 [-0.134, +0.074] | +0.011 [-0.139, +0.158] |
| their matrix | (b) Pr ≥ 0.5 | all pre-event samples | 1 y | 29/449 | 0.690 / 0.227 | 0.862 / 0.214 | +0.172 [-0.143, +0.467] | -0.013 [-0.085, +0.054] | +0.186 [-0.114, +0.470] |
| their matrix | (b) Pr ≥ 0.5 | all pre-event samples | 3 y | 99/277 | 0.525 / 0.199 | 0.717 / 0.162 | +0.192 [+0.015, +0.389] | -0.036 [-0.117, +0.037] | +0.228 [+0.038, +0.428] |
| their matrix | (b) Pr ≥ 0.5 | all pre-event samples | 5 y | 126/168 | 0.540 / 0.196 | 0.675 / 0.143 | +0.135 [-0.013, +0.297] | -0.054 [-0.185, +0.068] | +0.188 [+0.009, +0.388] |
| their matrix | (b) Pr ≥ 0.5 | patient unit | 1 y | 2/69 | 1.000 / 0.203 | 1.000 / 0.261 | +0.000 [+0.000, +0.000] | +0.058 [-0.044, +0.169] | -0.058 [-0.159, +0.044] |
| their matrix | (b) Pr ≥ 0.5 | patient unit | 3 y | 9/59 | 0.444 / 0.203 | 0.667 / 0.237 | +0.222 [+0.000, +0.500] | +0.034 [-0.082, +0.148] | +0.188 [-0.083, +0.503] |
| their matrix | (b) Pr ≥ 0.5 | patient unit | 5 y | 15/39 | 0.467 / 0.231 | 0.600 / 0.256 | +0.133 [-0.133, +0.400] | +0.026 [-0.121, +0.176] | +0.108 [-0.200, +0.400] |
| their matrix | (b) Pr ≥ 0.5 | NDBE pre-event samples | 1 y | 12/334 | 0.750 / 0.216 | 0.833 / 0.192 | +0.083 [-0.214, +0.429] | -0.024 [-0.097, +0.051] | +0.107 [-0.192, +0.422] |
| their matrix | (b) Pr ≥ 0.5 | NDBE pre-event samples | 3 y | 61/192 | 0.492 / 0.203 | 0.623 / 0.167 | +0.131 [-0.050, +0.344] | -0.036 [-0.129, +0.053] | +0.168 [-0.038, +0.383] |
| their matrix | (b) Pr ≥ 0.5 | NDBE pre-event samples | 5 y | 79/111 | 0.494 / 0.234 | 0.570 / 0.171 | +0.076 [-0.082, +0.246] | -0.063 [-0.220, +0.096] | +0.139 [-0.073, +0.352] |
| package features | (a) 80% sens. | all pre-event samples | 1 y | 29/449 | 0.862 / 0.372 | 0.931 / 0.296 | +0.069 [-0.083, +0.222] | -0.076 [-0.149, -0.010] | +0.145 [-0.025, +0.312] |
| package features | (a) 80% sens. | all pre-event samples | 3 y | 99/277 | 0.717 / 0.350 | 0.778 / 0.260 | +0.061 [-0.040, +0.165] | -0.090 [-0.169, -0.021] | +0.151 [+0.029, +0.279] |
| package features | (a) 80% sens. | all pre-event samples | 5 y | 126/168 | 0.730 / 0.327 | 0.778 / 0.244 | +0.048 [-0.058, +0.152] | -0.083 [-0.173, +0.006] | +0.131 [-0.006, +0.265] |
| package features | (a) 80% sens. | patient unit | 1 y | 2/69 | 1.000 / 0.449 | 1.000 / 0.362 | +0.000 [+0.000, +0.000] | -0.087 [-0.214, +0.030] | +0.087 [-0.030, +0.216] |
| package features | (a) 80% sens. | patient unit | 3 y | 9/59 | 0.667 / 0.441 | 0.778 / 0.322 | +0.111 [-0.286, +0.500] | -0.119 [-0.241, +0.000] | +0.230 [-0.191, +0.661] |
| package features | (a) 80% sens. | patient unit | 5 y | 15/39 | 0.667 / 0.410 | 0.733 / 0.333 | +0.067 [-0.222, +0.357] | -0.077 [-0.229, +0.071] | +0.144 [-0.180, +0.475] |
| package features | (a) 80% sens. | NDBE pre-event samples | 1 y | 12/334 | 0.917 / 0.368 | 0.917 / 0.278 | +0.000 [-0.250, +0.250] | -0.090 [-0.175, -0.016] | +0.090 [-0.179, +0.359] |
| package features | (a) 80% sens. | NDBE pre-event samples | 3 y | 61/192 | 0.656 / 0.385 | 0.705 / 0.271 | +0.049 [-0.079, +0.186] | -0.115 [-0.211, -0.026] | +0.164 [+0.006, +0.326] |
| package features | (a) 80% sens. | NDBE pre-event samples | 5 y | 79/111 | 0.696 / 0.369 | 0.709 / 0.270 | +0.013 [-0.106, +0.128] | -0.099 [-0.234, +0.026] | +0.112 [-0.063, +0.279] |
| package features | (b) Pr ≥ 0.5 | all pre-event samples | 1 y | 29/449 | 0.690 / 0.241 | 0.759 / 0.216 | +0.069 [-0.182, +0.320] | -0.024 [-0.102, +0.038] | +0.093 [-0.158, +0.353] |
| package features | (b) Pr ≥ 0.5 | all pre-event samples | 3 y | 99/277 | 0.556 / 0.224 | 0.677 / 0.166 | +0.121 [+0.010, +0.239] | -0.058 [-0.147, +0.015] | +0.179 [+0.042, +0.320] |
| package features | (b) Pr ≥ 0.5 | all pre-event samples | 5 y | 126/168 | 0.571 / 0.220 | 0.659 / 0.155 | +0.087 [-0.028, +0.196] | -0.065 [-0.203, +0.032] | +0.153 [-0.003, +0.318] |
| package features | (b) Pr ≥ 0.5 | patient unit | 1 y | 2/69 | 1.000 / 0.261 | 0.500 / 0.261 | -0.500 [-1.000, +0.000] | +0.000 [-0.106, +0.101] | -0.500 [-1.071, +0.072] |
| package features | (b) Pr ≥ 0.5 | patient unit | 3 y | 9/59 | 0.556 / 0.254 | 0.556 / 0.237 | +0.000 [-0.333, +0.333] | -0.017 [-0.136, +0.098] | +0.017 [-0.334, +0.360] |
| package features | (b) Pr ≥ 0.5 | patient unit | 5 y | 15/39 | 0.467 / 0.282 | 0.533 / 0.256 | +0.067 [-0.235, +0.357] | -0.026 [-0.162, +0.108] | +0.092 [-0.248, +0.405] |
| package features | (b) Pr ≥ 0.5 | NDBE pre-event samples | 1 y | 12/334 | 0.667 / 0.228 | 0.667 / 0.195 | +0.000 [-0.333, +0.400] | -0.033 [-0.119, +0.033] | +0.033 [-0.296, +0.430] |
| package features | (b) Pr ≥ 0.5 | NDBE pre-event samples | 3 y | 61/192 | 0.492 / 0.229 | 0.590 / 0.167 | +0.098 [-0.018, +0.225] | -0.062 [-0.164, +0.016] | +0.161 [+0.014, +0.322] |
| package features | (b) Pr ≥ 0.5 | NDBE pre-event samples | 5 y | 79/111 | 0.519 / 0.243 | 0.570 / 0.171 | +0.051 [-0.067, +0.175] | -0.072 [-0.234, +0.048] | +0.123 [-0.039, +0.314] |

**Reclassification**, all pre-event samples (patient unit: earliest pre-event NDBE sample). Fusion = L-LATE.

| CNV source | Op. | Unit | Horizon | Cases CNV− → fusion+ | Cases CNV+ → fusion− | Cases both + | Cases both − | Controls CNV− → fusion+ | Controls CNV+ → fusion− | Controls both + | Controls both − |
|---|---|---|---|---|---|---|---|---|---|---|---|
| their matrix | (a) | sample | 1 y | 5 | 1 | 23 | 0 | 30 | 82 | 120 | 217 |
| their matrix | (a) | sample | 3 y | 13 | 9 | 70 | 7 | 18 | 50 | 63 | 146 |
| their matrix | (a) | sample | 5 y | 15 | 13 | 88 | 10 | 14 | 25 | 36 | 93 |
| their matrix | (a) | patient | 1 y | 0 | 0 | 2 | 0 | 9 | 7 | 17 | 36 |
| their matrix | (a) | patient | 3 y | 1 | 0 | 7 | 1 | 7 | 7 | 12 | 33 |
| their matrix | (a) | patient | 5 y | 2 | 2 | 9 | 2 | 6 | 3 | 9 | 21 |
| their matrix | (b) | sample | 1 y | 8 | 3 | 17 | 1 | 37 | 43 | 59 | 310 |
| their matrix | (b) | sample | 3 y | 28 | 9 | 43 | 19 | 16 | 26 | 29 | 206 |
| their matrix | (b) | sample | 5 y | 30 | 13 | 55 | 28 | 12 | 21 | 12 | 123 |
| their matrix | (b) | patient | 1 y | 0 | 0 | 2 | 0 | 9 | 5 | 9 | 46 |
| their matrix | (b) | patient | 3 y | 2 | 0 | 4 | 3 | 7 | 5 | 7 | 40 |
| their matrix | (b) | patient | 5 y | 3 | 1 | 6 | 5 | 5 | 4 | 5 | 25 |
| package features | (a) | sample | 1 y | 3 | 1 | 24 | 1 | 30 | 64 | 103 | 252 |
| package features | (a) | sample | 3 y | 14 | 8 | 63 | 14 | 15 | 40 | 57 | 165 |
| package features | (a) | sample | 5 y | 18 | 12 | 80 | 16 | 8 | 22 | 33 | 105 |
| package features | (a) | patient | 1 y | 0 | 0 | 2 | 0 | 7 | 13 | 18 | 31 |
| package features | (a) | patient | 3 y | 2 | 1 | 5 | 1 | 4 | 11 | 15 | 29 |
| package features | (a) | patient | 5 y | 3 | 2 | 8 | 2 | 3 | 6 | 10 | 20 |
| package features | (b) | sample | 1 y | 5 | 3 | 17 | 4 | 28 | 39 | 69 | 313 |
| package features | (b) | sample | 3 y | 17 | 5 | 50 | 27 | 13 | 29 | 33 | 202 |
| package features | (b) | sample | 5 y | 21 | 10 | 62 | 33 | 8 | 19 | 18 | 123 |
| package features | (b) | patient | 1 y | 0 | 1 | 1 | 0 | 7 | 7 | 11 | 44 |
| package features | (b) | patient | 3 y | 1 | 1 | 4 | 3 | 6 | 7 | 8 | 38 |
| package features | (b) | patient | 5 y | 3 | 2 | 5 | 5 | 3 | 4 | 7 | 25 |

**Who fusion catches and clears** (operating point (a), 3 years, all pre-event samples, per sample; medians).

| CNV source | Group | Samples / patients | Pathology | Years to event or censoring | cx (raw, package) | cx (z, their) | Noise (varMAD_median) | Tissue tiles | Scanner | p53 IHC | Killcoyne risk class (published) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| their matrix | cases CNVneg fusionpos | 13 / 7 | NDBE 6, LGD 6, ID 1 | 2.000 | 21.000 | -0.643 | 0.002 | 250.000 | C13239-01 7, C13210 6 | 0.0 10, nan 2, 1.0 1 | low 8, high 3, moderate 2 |
| their matrix | cases both pos | 70 / 25 | NDBE 42, LGD 20, ID 8 | 1.500 | 25.000 | 0.068 | 0.002 | 251.000 | C13239-01 53, C13210 17 | 0.0 41, nan 16, 1.0 13 | high 63, moderate 6, low 1 |
| their matrix | controls CNVpos fusionneg | 50 / 23 | NDBE 32, ID 16, LGD 2 | 5.000 | 24.000 | -0.169 | 0.003 | 232.000 | C13239-01 40, C13210 10 | 0.0 41, nan 9 | moderate 25, high 16, low 9 |
| their matrix | controls both pos | 63 / 24 | NDBE 43, LGD 15, ID 5 | 5.500 | 26.000 | -0.050 | 0.003 | 341.000 | C13239-01 47, C13210 16 | nan 35, 0.0 27, 1.0 1 | high 50, moderate 10, low 3 |
| package features | cases CNVneg fusionpos | 14 / 10 | NDBE 9, LGD 4, ID 1 | 2.000 | 21.000 | -0.347 | 0.002 | 202.500 | C13239-01 10, C13210 4 | 0.0 11, nan 3 | low 8, moderate 3, high 3 |
| package features | cases both pos | 63 / 25 | NDBE 34, LGD 22, ID 7 | 1.500 | 25.000 | 0.068 | 0.002 | 260.000 | C13239-01 46, C13210 17 | 0.0 36, nan 14, 1.0 13 | high 58, moderate 4, low 1 |
| package features | controls CNVpos fusionneg | 40 / 22 | NDBE 33, ID 4, LGD 3 | 5.500 | 23.000 | -0.406 | 0.004 | 274.500 | C13239-01 27, C13210 13 | 0.0 32, nan 8 | low 18, high 12, moderate 10 |
| package features | controls both pos | 57 / 29 | NDBE 41, LGD 13, ID 3 | 5.500 | 26.000 | -0.050 | 0.003 | 277.000 | C13239-01 43, C13210 14 | nan 30, 0.0 26, 1.0 1 | high 35, low 11, moderate 11 |

The list of these patients by study number, with each sample's published risk class, is row-level and stays on the cluster: `/mnt/scratche/slow/fmlab/zuberi01/phd/thesis/feasibility/paper_plan/killcoyne_mm/horizons/h2_patient_list.csv` (370 rows).

**Method.** `hz_stack.py` TASK=h2. Calls per repeat, majority over the 10 repeats (≥ 6 of 10); ΔTPR, ΔFPR and NRI CIs from 2,000 patient-bootstrap draws (`RandomState(0)`). Per-repeat mean TPR/FPR are in `h2.json`.
**Sources.** `cv/preds/` (kv_cv.R), `horizons/inner/` and `horizons/outer/` (hz_fit.R), `horizons/pkg_qc.csv` (hz_qc.R from `killcoyne/pkg/pat_*.rds`), `horizons/slide_desc.csv` (hz_slides.py), `models/killcoyne_frozen_pkg_v1/cnv_scaling_setC.csv` (cx mean 25.256, s.d. 8.416, to recover raw cx); `h2.json`.
**Caveats.** (1) Operating point (b) applies a fixed 0.5 to probabilities from models whose intercept moves with the fold's training prevalence; it is not a calibrated risk threshold here (design caveat). (2) Thresholds and calls are per sample; patients contribute several samples. (3) The 'who' comparison is descriptive, with no test.

### H3. WSI vs CNV weighting by horizon

**Question.** Does the image weight in a CNV + WSI stack change with horizon? **Status.** DONE. **Pre-specification.** Above (H3); expected direction stated in advance: WSI weight higher at 1 year than at 5 years.

| CNV source | Horizon | Fits | b (CNV) [CI] | c (WSI) [CI] | c/(b+c), mean over fits [CI] | c/(b+c) of mean coefficients [CI] | Fits with b < 0 / c < 0 | Exploratory: stack vs L-LATE IPCW AUROC, Δ [CI] |
|---|---|---|---|---|---|---|---|---|
| their matrix | 1 y | 100 | 0.542 [0.207, 1.159] | 0.511 [0.025, 1.015] | 0.496 [0.015, 0.811] | 0.485 [0.024, 0.785] | 1 / 3 | 0.836 vs 0.869: -0.033 [-0.060, -0.008] |
| their matrix | 3 y | 100 | 0.820 [0.494, 1.378] | 1.082 [0.636, 1.699] | 0.575 [0.385, 0.730] | 0.569 [0.377, 0.717] | 0 / 0 | 0.847 vs 0.855: -0.008 [-0.021, +0.004] |
| their matrix | 5 y | 100 | 1.060 [0.663, 1.701] | 1.011 [0.606, 1.580] | 0.495 [0.319, 0.661] | 0.488 [0.309, 0.644] | 0 / 0 | 0.840 vs 0.844: -0.005 [-0.019, +0.010] |
| package features | 1 y | 100 | 0.547 [0.238, 1.011] | 0.541 [0.097, 1.022] | 0.503 [0.083, 0.785] | 0.498 [0.104, 0.765] | 0 / 0 | 0.824 vs 0.852: -0.028 [-0.051, -0.011] |
| package features | 3 y | 100 | 0.714 [0.447, 1.102] | 1.052 [0.610, 1.639] | 0.596 [0.414, 0.741] | 0.596 [0.410, 0.739] | 0 / 0 | 0.834 vs 0.842: -0.008 [-0.025, +0.010] |
| package features | 5 y | 100 | 1.022 [0.641, 1.544] | 0.951 [0.542, 1.491] | 0.484 [0.311, 0.639] | 0.482 [0.309, 0.636] | 0 / 0 | 0.836 vs 0.839: -0.003 [-0.019, +0.011] |

1 year minus 5 years, c/(b+c): their matrix +0.001 [-0.411, +0.291] (of mean coefficients -0.003 [-0.391, +0.280]); package features +0.019 [-0.354, +0.280] (of mean coefficients +0.016 [-0.335, +0.269]).

**Method.** `hz_stack.py` TASK=h3_<src>: inner 5-fold out-of-fold L-CNV and L-IMG probabilities (`hz_fit.R` MODE=inner) → logits, z-scored over the outer training horizon cases and controls (pre-event samples) → logistic stack with an L2 penalty of 1e-4 on the slopes (IRLS); 100 fits per horizon; CIs from 2,000 patient-bootstrap draws (`RandomState(0)`) that refit every fold stack with patient-multiplicity weights; the held-out stack is applied to the outer out-of-fold L-CNV and L-IMG predictions and averaged over repeats.
**Sources.** `horizons/inner/{cnv,img}_*`, `cv/preds/cfg_0{0,1,2}_*`; `h3_their.json`, `h3_pkg.json`.
**Caveats.** (1) Exploratory held-out AUROCs: the stack was specified before but is reported after H1 was seen. (2) The ratio c/(b+c) is unstable when b + c is small (the 1-year fits have the fewest cases); the ratio of mean coefficients is given alongside.

### H4. Depth transfer

**Question.** Is there 4× discovery data, and are CNV features stable across depth on ACE-B? **Status.** 4× → external NOT AVAILABLE; ACE-B label-blind depth check NOT AVAILABLE. **Pre-specification.** Above (H4) and amendment 2 of `docs/aceb_analysis_plan.md` (0.4× primary depth rule, committed in ee51db8 before any ACE-B outcome was read).

**What exists.** Roots searched: `/mnt/scratche/fast/fmlab`, `/mnt/scratche/slow/fmlab` (`lfs find` in 345 shards, 12,779,259 entries listed, 1,975 unreadable-path messages; read files `*.bam`, `*.cram`, `*.fastq[.gz]`, `*.fq[.gz]`, `*.sra`: 64,078 found).
- 4× resequenced discovery data: read files carrying one of the 15 discovery SLX ids outside `SWGCohort/dna_seq_bam`: 3,125 files in 2,358 directories, grouped:
  - `/mnt/scratche/slow/fmlab/datasets/imaging/SWGCohort/validation_genomics`: 780 files (0 symlinks, 0 broken; link targets under none (the pre-migration path of `validation_genomics`); 1166.6 GB in real files); 20 real BAMs probed (`RandomState(0)`): nominal depth median 0.600× (range 0.286–1.021), read length 50 bp (20), build hg19 (20).
  - `/mnt/scratche/slow/fmlab/zuberi01/phd/barretts_retraining/barretts_training`: 780 files (780 symlinks, 780 broken; link targets under `/scratchc/fmlab/datasets/imaging/SWGCohort/` (the pre-migration path of `validation_genomics`); 0.0 GB in real files).
  - `/mnt/scratche/slow/fmlab/zuberi01/phd/barretts_retraining/paper`: 1565 files (1557 symlinks, 1557 broken; link targets under `/scratchc/fmlab/datasets/imaging/SWGCohort/` (the pre-migration path of `validation_genomics`); 0.0 GB in real files).

- Directories named for depth or resequencing: 125, all software or slide-prediction folders matched by the word 'deep' (for example Python packages `deepseek_*`, `deepzoom`, `deeplabv3`, `deeptools`, and H&E 'DEEPER' levels); none holds sequencing data.
- ACE-B reads (SLX pools SLX-26195, SLX-26196, SLX-26851, SLX-27125, SLX-27128): none on the cluster.

**Result.** No 4× discovery data: the only discovery-SLX read files outside `dna_seq_bam` are an older hg19 alignment of the same runs (`SWGCohort/validation_genomics`, probed nominal depth at most 1.02×) and broken symlinks to it. No ACE-B reads exist on the cluster, so the label-blind depth check could not run; the ACE-B manifest's `Mean_Coverage` (median 5.30×, range 3.29–14.91×, 191 of 234 samples; `docs/dataset_description.md` item 7) is the only depth information, and it is not 7×.
**Method.** `hz_search.py` (one `find` over both roots, Slurm) ran > 3.5 h without finishing and was replaced by `hz_search_shard.py` (`lfs find` per depth-2 directory, plus each depth-1 directory at `-maxdepth 1`, as parallel Slurm tasks; merged with duplicates removed). The depth-check pipeline is specified above; the QDNAseq 50 kb bins for it must be the discovery hg38 annotation (61,775 bins in `50.raw_read_counts.txt`), which is stored in each discovery `50.QDNAseq.RData`: the generator in `[BT]/scripts/swg_generate_qdnaseq_one_sample.R` calls `getBinAnnotations(binSize = 50)` with QDNAseq's default genome (hg19) and no hg38 annotation package is installed, so it is not the producer of the discovery counts (made 2025-03-12 by another user).
**Sources.** `h4_search.json`, `h4_bam_probe.json` (`scripts/paper_plan/hz_bam_probe.py`: symlink targets; for 20 real BAMs per directory, `samtools view -c -F 0x900` reads, modal length of the first 2,000 reads, `@SQ` chr1 length for the build, nominal depth = reads × length / 3,088,269,832); `feasibility/paper_plan/killcoyne_mm/horizons/h4_read_files_all.csv` (cluster).
**Caveats.** (1) The search covers the mounted lab scratch areas only; reads held by the sequencing core or the cohort owner off-cluster are not visible. (2) The probe counts every primary read including unmapped ones, whereas `docs/dataset_description.md` item 6 used the QDNAseq read-count totals of the hg38 BAMs (set C median 0.29×), so the two depths are not on the same counting basis.

### Discrepancies found

- The task gives ACE-B depth as 7× ('7× external'); the manifest gives median 5.30× (range 3.29–14.91×), and 43 of 234 samples (batch 3) have no coverage value.
- The task's 'set C' is called the discovery subset here; it is 676 of the 773 published discovery samples (80 of 88 patients).
- L-INTER did not exist under the stratified CV; it was fitted for this task, so its cells are new fits, unlike the other arms.
- The H1-best model is L-LATE, so H2's 'best model' and 'L-LATE' comparisons coincide; each is reported once.
- The patient unit (earliest pre-event NDBE sample) is identical in the 'all pre-event' and 'NDBE pre-event' populations.
- The discovery 50 kb QDNAseq counts were not produced by the repository's QDNAseq generator (hg19 default bins); a depth check would have to reuse the hg38 bin annotation stored in the discovery `50.QDNAseq.RData` files.

### Deviations from the pre-specification

- The ACE-B code-path check used 200 bootstrap and permutation draws on the dummy labels (the real run uses 2,000); it checks that the path runs, not its numbers.
- H4's search was run sharded with `lfs find` instead of one `find` (same roots, same file patterns), because the single search did not finish in 3.5 h.
- No other change: every H1–H3 number above follows the pre-specified definitions.

### Not done

- ACE-B columns of the H1 table (no slides, outcomes blinded); ACE-B L-GRADE, L-GRADE+age+sex and L-INTER cells cannot be filled even after unblinding (no frozen models).
- 4× → external transfer (no 4× discovery data on the cluster). ACE-B label-blind depth check (no ACE-B reads on the cluster); its pipeline is specified but was not run.
- H4 stability figure (needs the depth check).
- No absolute risk, calibration or PPV (design caveat).

**Interpretation.** On all pre-event samples late fusion has the highest per-sample IPCW AUROC at 1, 3 and 5 years with either CNV source, but only the grade arms differ from it after max-T adjustment, and the WSI weight in the stack does not rise at 1 year.


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

(appended in a later commit)

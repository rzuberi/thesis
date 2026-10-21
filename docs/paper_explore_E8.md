# Exploration E8: is the quiet-genome check real biology, and can it be sharper or cheaper?

Status: EXPLORATORY, COMPLETE (21 October 2026). Rules in `paper/reviews_round7/decisions/EXPLORE_RULES.md`. Nothing here is confirmatory; every variant tried is recorded.

## Plan

**Baselines (reproduced with the exact E2 code).**
- **A12:** round-9 memory + copy-number certificate (stored `grp_A12.npz`, per-fold selected): 21.5 non-progressors (NP) flagged.
- **Final rule:** A12 + quiet-genome check (sequence the two top-H&E samples of each A12-flagged endoscopy; cancel the flag if both are below the bar on the 10 OAC arms; bar = 90% of the fold's training progressor endoscopies, `ps_oac k2 cn90`): 30.5 caught / 17.2 NP flagged / 3.82 samples per patient.

Every variant is reported against A12 and the final rule (and R49, P1) on the same held-out patients: Δ NP flagged, Δ progressors caught, samples per patient, paired patient-bootstrap 95% CIs (2,000 draws, `RandomState(0)`). Bars and step sizes are set on the fold's training patients only; apparent (bar on evaluation patients) numbers are labelled optimistic.

**Tests.**
1. **Technical confounding.** Read depth, 50-kb noise (MAPD; MAD of copy number minus segmented value; QDNAseq expected variance), arm-level noise (robust SD of the sample's 39 arm deviations) and an abnormal-cell proxy (pathologist % Barrett's cellularity) compared between quiet and non-quiet flagged endoscopies, by class; logistic model of "quiet" on class + QC covariates. Noise-scaled quietness (OAC score divided by each noise measure; count of OAC arms beyond 3 arm-level SDs). QC-gated cancel (cancel only if both samples pass QC: stored tile QC flag; MAPD below the training 90th percentile; reads above the training 10th percentile).
2. **Arm specificity.** 17p only; 17p + 9p; all 10 arms minus 17p; each single arm; 1,000 random 10-arm sets of non-OAC arms (7 losses, 3 gains, total length within ±15% of the OAC set); GC-rich non-OAC arms (19p, 19q, 22q, 16p; any change); fragile-site focal deletions (FHIT 3p14.2, WWOX 16q23.1; 50-kb bins vs ±10 Mb flank). Percentile of the real check among the random sets.
3. **Concordance of the two samples.** Arm calls shared vs private by class; quiet-call agreement; an agreement-required score (arm counts only if altered in both samples) and a "cancel if either is quiet" rule.
4. **Flattened / genome-doubling proxy.** Segment counts, small-amplitude segments (0.03–0.10 log2 from the genome median), distinct segment levels: quiet progressor vs quiet non-progressor samples; a check that cancels only if quiet AND not flattened.
5. **Sequential check.** Sequence the top-H&E sample; sequence the second only if the first is quiet (identical decisions); samples per patient.
6. **Soft veto.** The A12 engine is rebuilt in-fold (verified equal to the stored flags); a quiet result lowers the running score by δ (chosen on training patients) instead of cancelling; compared with the hard veto with the bar re-chosen in-fold.
7. **Timing.** Years to event of quiet vs non-quiet progressor endoscopies; quiet rate by time-to-event band; persistence of quietness in non-progressors.

**Files.** Scripts `scripts/paper_plan/ex_e8_*.py`; aggregates `results/paper_final/explore_E8/`; figures `paper/figures_explore_E8/` (local); row-level `killcoyne_mm/explore_E8/` on the cluster; Slurm prefix `exe8`.

## Results

All numbers are held-out patients, mean over the 10 repeats, paired patient-bootstrap 95% CIs (2,000 draws, `RandomState(0)`). Baselines reproduce exactly: A12 30.5 caught / 21.5 non-progressors (NP) flagged / 1.94 samples per patient; final rule 30.5 / 17.2 / 3.82 (`base.json`, `reproduced: true`). The rebuilt A12 engine matches the stored per-fold choice, flags and cn90 bar in 100/100 folds (`soft.json`). R49: 31.1 / 31.8 / 1.94; P1: 31.1 / 36.0 / 0.

Per repeat, A12 flags 53.4 NP and 77.1 progressor endoscopies; the check calls 19.1 and 7.3 of them quiet.

### Ranked summary (selected rows; the full table of 87 rows is printed by `scripts/paper_plan/ex_e8_render.py`)

| Rule | Caught | NP flagged | Samples / patient | ΔNP vs final | Δcaught vs final | ΔNP vs R49 | Δcaught vs R49 | ΔNP vs P1 | Δcaught vs P1 |
|---|---|---|---|---|---|---|---|---|---|
| Final rule (A12 + quiet check, cn90 bar) | 30.5 | 17.2 | 3.82 | 0 | 0 | −14.6 [−18.9, −10.3] | −0.6 [−1.6, +0.2] | −18.8 [−23.9, −13.7] | −0.6 [−2.1, +1.3] |
| **Sequential check** (2nd sample only if the 1st is quiet) | 30.5 | 17.2 | **3.23** | 0 | 0 | −14.6 [−18.9, −10.3] | −0.6 [−1.6, +0.2] | −18.8 [−23.9, −13.7] | −0.6 [−2.1, +1.3] |
| Band check δ = 5 + sequential (post hoc grid point) | 30.5 | 17.2 | 3.04 | 0 | 0 | −14.6 [−18.9, −10.3] | −0.6 [−1.6, +0.2] | −18.8 [−23.9, −13.7] | −0.6 [−2.1, +1.3] |
| Band check, δ nested + sequential | 30.5 | 18.2 | 2.63 | +1.0 [+0.0, +3.2] | 0 | −13.6 [−17.8, −9.6] | −0.6 [−1.6, +0.2] | −17.8 [−22.7, −12.8] | −0.6 [−2.1, +1.3] |
| Soft veto, bar q and δ nested | 30.5 | 17.4 | 3.82 | +0.2 [−1.0, +2.1] | 0 | −14.4 [−18.7, −10.3] | −0.6 [−1.6, +0.2] | −18.6 [−23.6, −13.6] | −0.6 [−2.1, +1.3] |
| Soft veto, δ nested (cn90 bar) | 30.5 | 18.5 | 3.82 | +1.3 [+0.1, +3.5] | 0 | −13.3 [−17.4, −9.3] | −0.6 [−1.6, +0.2] | −17.5 [−22.3, −12.6] | −0.6 [−2.1, +1.3] |
| Hard veto, bar re-chosen in-fold (strict) | 29.7 | 15.9 | 3.82 | −1.3 [−2.5, −0.3] | −0.8 [−1.9, +0.0] | −15.9 [−20.4, −11.6] | −1.4 [−3.0, −0.1] | −20.1 [−25.0, −15.1] | −1.4 [−3.5, +0.7] |
| QC-gated cancel (tile QC + MAPD + reads) | 30.5 | 17.3 | 3.82 | +0.1 [+0.0, +0.3] | 0 | −14.5 [−18.8, −10.2] | −0.6 [−1.6, +0.2] | −18.7 [−23.6, −13.7] | −0.6 [−2.1, +1.3] |
| Noise-residualised score (reads, only lowered) | 30.5 | 17.3 | 3.82 | +0.1 [−0.2, +0.4] | 0 | −14.5 [−18.8, −10.2] | −0.6 [−1.6, +0.2] | −18.7 [−23.7, −13.7] | −0.6 [−2.1, +1.3] |
| Mean of the two samples | 30.4 | 18.1 | 3.82 | +0.9 [+0.1, +1.9] | −0.1 [−0.3, +0.0] | −13.7 [−18.0, −9.4] | −0.7 [−1.7, +0.1] | −17.9 [−23.0, −12.7] | −0.7 [−2.2, +1.2] |
| 17p + 9p losses only | 30.5 | 18.6 | 3.82 | +1.4 [−1.1, +4.4] | 0 | −13.2 [−17.4, −9.2] | −0.6 [−1.6, +0.2] | −17.4 [−22.1, −12.5] | −0.6 [−2.1, +1.3] |
| 10 OAC arms minus 17p | 29.7 | 18.4 | 3.82 | +1.2 [+0.0, +2.6] | −0.8 [−2.0, +0.0] | −13.4 [−17.7, −9.3] | −1.4 [−2.9, −0.2] | −17.6 [−22.5, −12.6] | −1.4 [−3.3, +0.7] |
| Noise-scaled (÷ segment-residual MAD) | 29.4 | 18.8 | 3.82 | +1.6 [−0.9, +5.0] | −1.1 [−3.3, +0.0] | −13.0 [−17.5, −8.8] | −1.7 [−4.0, −0.1] | −17.2 [−22.2, −12.1] | −1.7 [−4.4, +0.7] |
| GC-rich arms 19p/19q/22q/16p, any change (control) | 29.6 | 18.8 | 3.82 | +1.6 [−1.7, +5.2] | −0.9 [−3.1, +0.0] | −13.0 [−17.1, −9.1] | −1.5 [−3.8, +0.1] | −17.2 [−21.7, −12.2] | −1.5 [−4.1, +0.8] |
| Top-H&E sample only (k1) | 29.4 | 19.1 | 2.92 | +1.9 [+0.5, +3.5] | −1.1 [−3.3, +0.0] | −12.7 [−16.8, −8.7] | −1.7 [−4.1, +0.0] | −16.9 [−21.8, −11.9] | −1.7 [−4.4, +0.8] |
| Quiet AND not flattened (small segments, 50% bar) | 30.5 | 19.5 | 3.82 | +2.3 [+0.5, +4.8] | 0 | −12.3 [−16.5, −8.5] | −0.6 [−1.6, +0.2] | −16.5 [−21.2, −11.7] | −0.6 [−2.1, +1.3] |
| Fraction genome altered (global measure) | 29.3 | 19.5 | 3.82 | +2.3 [−0.4, +5.7] | −1.2 [−3.5, +0.0] | −12.3 [−16.4, −8.3] | −1.8 [−4.1, −0.1] | −16.5 [−21.3, −11.5] | −1.8 [−4.5, +0.6] |
| 17p loss only | 30.5 | 19.7 | 3.82 | +2.5 [−0.4, +5.9] | 0 | −12.1 [−16.0, −8.3] | −0.6 [−1.6, +0.2] | −16.3 [−21.1, −11.4] | −0.6 [−2.1, +1.3] |
| Arm must change in both samples | 29.1 | 20.3 | 3.82 | +3.1 [+1.2, +5.6] | −1.4 [−3.6, +0.0] | −11.5 [−15.4, −7.8] | −2.0 [−4.2, −0.3] | −15.7 [−20.3, −10.9] | −2.0 [−4.5, +0.4] |
| FHIT + WWOX fragile sites (control) | 29.6 | 21.2 | 3.82 | +4.0 [+1.4, +7.3] | −0.9 [−3.1, +0.0] | −10.6 [−14.2, −7.1] | −1.5 [−4.0, +0.1] | −14.8 [−19.4, −10.0] | −1.5 [−4.4, +1.0] |
| A12 (memory + certificate) | 30.5 | 21.5 | 1.94 | +4.3 [+1.7, +7.7] | 0 | −10.3 [−13.9, −6.9] | −0.6 [−1.6, +0.2] | −14.5 [−19.0, −9.6] | −0.6 [−2.1, +1.3] |

Endoscopy specificity at matched sensitivity against P1: +0.162 [+0.049, +0.291] for the final rule and every decision-identical variant (sequential, band δ = 5). Cost per patient (round-8 costs): final £1,067, sequential £1,017, band δ = 5 + sequential £1,001.

### 1. Technical confounding — verdict: biology (noise works against the check, not for it; purity untested)

- **Quiet calls come from cleaner, deeper samples.** Among A12-flagged endoscopies, quiet NP endoscopies have lower 50-kb MAPD (AUROC for "higher in quiet" 0.21 [0.11, 0.33]), lower segment-residual noise (0.20), lower arm-level noise (0.29) and more reads (0.75 [0.61, 0.86]). Progressors show the same direction, more weakly. Noisy samples look *altered*: in NP samples, ps_oac correlates with MAPD (Spearman 0.40) and arm-level noise (0.40); in progressor samples it is unrelated to MAPD (−0.01) but still tracks arm-level noise (0.50).
- **The class effect survives QC adjustment.** Endoscopy-level logistic model of "quiet" (139 A12-flagged endoscopies, 27 quiet): progressor OR 0.20 [0.07, 0.59] unadjusted, 0.15 [0.05, 0.50] after MAPD, reads and segment noise, 0.15 [0.05, 0.51] adding cellularity. QC terms alone are not significant.
- **Purity proxy:** pathologist % Barrett's cellularity is missing for 460 of 676 samples, so purity is not properly tested (quiet NP 35% vs non-quiet 39%; progressors 50% vs 50%). An ichorCNA/ACE-style purity needs the 4× data.
- **Noise-scaled quietness is worse**: ÷ segment noise loses 1.1 progressors; ÷ arm-level SD loses 1.6; z-thresholded arm counts are 0 for ≥ 10% of training progressor endoscopies, so their bar degenerates to 0 and nothing is cancelled. **Noise-residualised** scores (slope on noise fitted on training NP samples) change nothing useful (best: reads, +0.1 NP).
- **QC-gated cancel** blocks almost no vetoes (all three gates together: 1.0 NP and 0.9 progressor endoscopy vetoes blocked per repeat; +0.1 NP patients net).

### 2. Arm specificity — verdict: biology

- **Random arm sets** (1,000 non-OAC 10-arm sets, 7 losses + 3 gains, length ±15%): median −0.7 NP and −0.65 progressors vs A12; **none** clears as many NPs as the OAC check (percentile 100), none matches it on both axes, and none clears ≥ 3 NPs with no progressor lost. From any arms (OAC arms allowed, set ≠ OAC): 0.2% clear as many, 0.1% match on both. Random 2 samples instead of the 2 top-H&E samples (200 draws): −3.9 [p5–p95 −5.1, −3.1] NP, 0 progressors lost — the arms carry the check; the H&E choice of samples adds little.
- **17p carries about 40% of it**: 17p alone −1.8 NP vs A12 with no progressor lost; 17p + 9p −2.9; the 10 arms −4.3. Removing 17p keeps −3.1 NP but loses 0.8 progressors: 17p is what protects progressors, the other arms add NP clearing. Removing 20q (more common in NPs) is slightly worse (−3.4), so the equal-weight sum is not hurt by 20q.
- 17p loss > 5%: 27.3% of progressor vs 1.7% of NP samples. 17p correlates with the GC-rich arms equally in both classes (Spearman 0.23 / 0.21), so GC co-movement exists but is not class-specific.
- **Controls:** GC-rich non-OAC arms (any change) −2.7 NP but −0.9 progressors (a global-instability signal, not GC artefact, since GC-rich *losses* alone clear 0.7 and *gains* 0). **Fragile sites** FHIT/WWOX: focal loss in 35% / 27% (FHIT, progressors / NPs), −0.3 NP and −0.9 progressors: useless. The OAC arms beat both.
- Single-arm checks other than 17p, 9p and 13q are inert: the arm is unaltered in ≥ 10% of training progressor endoscopies, so the 90% bar is 0.

### 3. Agreement between the two samples — verdict: mixed (biology, with sampling limits)

- Altered OAC-arm instances (> 5%) shared by both samples: 20% in NPs, 24% in progressors. **17p loss is never shared in NPs** (0.0 shared vs 0.8 private per repeat) but is shared in 44% of progressor instances (7.4 vs 9.3): progressors' 17p losses are clonal across the two levels.
- Quiet-call agreement (flagged, two samples, per repeat): NP both quiet 12.3, one 5.5, neither 12.7; progressors 3.0 / 12.4 / 21.3.
- **Requiring agreement hurts**: arm must change in both samples −1.2 NP, −1.4 progressors; cancel if either is quiet −1.6 / −1.5; top sample only (k1) −2.4 / −1.1. Both samples are needed because many progressor changes are private to one level.

### 4. Flattened / genome-doubling proxy — verdict: biology (quiet progressor samples are genuinely quiet, not flattened)

- Quiet progressor samples have *fewer* segments and small-amplitude shifts than quiet NP samples (AUROC progressor vs NP among quiet flagged endoscopies: segments ≥ 1 Mb 0.40, small-amplitude segments 0.32, distinct levels 0.39, fraction altered 0.37). No sign of compressed, many-small-shift profiles; 0.4× cannot exclude CN-LOH or doubling without allelic data.
- A "quiet AND not flattened" check only blocks NP vetoes (+2.3 NP at the 50% bar, more at 75–90%). Global measures as the check (fraction altered, segment counts, distinct levels, amplitude SD) all clear fewer NPs and most lose progressors.

### 5. Sequential check — verdict: cheaper, same decisions

- Sequencing the second sample only when the first is quiet gives **identical decisions** (asserted) and **3.23 instead of 3.82 samples per patient (−0.59 [−0.76, −0.43])**. The second sample is needed at 48% of checked NP endoscopies and 23% of progressor endoscopies.
- **Band check** (no check when the running score is already ≥ δ logits above the line, where a quiet result cannot cancel it under the soft rule): δ = 5 + sequential keeps identical decisions in this cohort at **3.04 samples per patient (−0.78 [−1.01, −0.57])**, but δ = 5 is a post hoc grid point (apparent: δ ≥ 5 gives 17.2, δ = 3 gives 17.4). With δ chosen on training patients (cheapest band matching the hard veto's training result; δ mostly 1.5–3): 18.2 NP (+1.0 [0.0, +3.2]), 30.5 caught, 2.63 samples (−1.18).

### 6. Soft veto — verdict: technical safeguard, no extra benefit

- With the bar re-chosen in-fold as a hard veto (strict: no training progressor lost), the check loses 0.8 [−1.9, 0.0] progressors (the known 1–2 loss) while clearing 1.3 more NPs.
- **The soft veto never loses a progressor** (Δcaught 0.0 in all four nested variants) but gives back NP clearing: δ nested with the cn90 bar 18.5 NP (+1.3 vs final); bar quantile and δ both nested (bar mostly 80%, δ mostly 1.5–3) 17.4 NP (+0.2 [−1.0, +2.1]). Carrying the quiet result forward 2 years: 18.6 NP, −0.2 progressors.
- E7's finding (in-fold bar from 80–97.5% loses about 0.1 progressor; one-look veto loses about 2.6) fits: what keeps the check safe in this cohort is memory, which rescues quiet progressors at another endoscopy. Here the projection "check only at each patient's first A12 flag, no rescue" makes < 5 progressors' first flag quiet, none of them with a single pre-event endoscopy, against 7.1 NPs cleared. The soft veto's advantage should show in a one-look setting (it cannot cancel a flag far above the line); that was not tested here.

### 7. Timing — verdict: biology (early field)

- **No progressor endoscopy within 1 year of the event is quiet** (0 of 10 per repeat). Quiet share 10% [0, 20%] at 1–3 years and 13.6% [3.4, 24.3%] at ≥ 3 years, against 35% of NP endoscopies. Median years to event: quiet 4.6, not quiet 3.3 (difference +1.2 [−1.0, +3.9]). Spearman of years to event with the OAC score: −0.31.
- In progressors with ≥ 2 endoscopies (22), the first endoscopy is quiet in 12.7%, the last in 4.5%.
- NP quietness persists: P(quiet next | quiet now) 0.69 vs 0.22 after a non-quiet endoscopy.

### Figures (local, `paper/figures_explore_E8/`)

- `e8_arm_specificity.png`: 1,000 random arm sets vs the OAC check and named controls.
- `e8_quiet_timing.png`: quiet share of progressor endoscopies by years before the event.
- `e8_qc_confounding.png`: AUROC of QC metrics for quiet vs non-quiet flagged endoscopies, by class.
- `e8_sequencing_cost.png`: NP flagged vs samples per patient for the staged checks.

### Implementation notes

- **Code reuse:** `ex_e8_eval.py` executes `ex_e2_veto.py` unchanged up to its dispatch (as `story_aggs_v2.py`), so A12 (stored `grp_A12.npz`) and the final rule (`vs_test`/`vs_train`, `ps_oac`, k = 2, cn90 bar from `veto_V`) are the E2 objects; the OAC-arm score rebuilt from the per-sample arm deviations equals `ps_oac` (asserted). TASK = soft also executes `rv9_falseflags.py` unchanged and re-runs the A12 per-fold selection to get running scores u and thresholds t for training endoscopies.
- **New features** (`ex_e8_feat.py`, QDNAseq 50-kb hg38 outputs, autosomes): reads and expected variance (`readCountSummary`); MAPD; segment-residual MAD (1.4826 × median |copy number − segmented|); segment counts (runs ≥ 1 Mb), small (0.03–0.10 log2) and tiny (0.02–0.06) amplitude segments relative to the genome median, distinct levels (0.05 log2 steps); FHIT (chr3:59.75–61.25 Mb) and WWOX (chr16:78.10–79.21 Mb) median log2 minus the ±10 Mb flank. Arm-level noise = robust SD (1.4826 × MAD) of the sample's 39 non-acrocentric arm deviations.
- **Bars:** every check uses the same rule as the final rule (share q = 90% of the fold's training progressor endoscopies' top-2 score), unless stated. Soft veto: a flagged endoscopy with a quiet check is cancelled only if u − δ < t; δ from {0.25, 0.5, 0.75, 1, 1.5, 2, 3, 5, ∞} (and bar q from {0.80, 0.85, 0.90, 0.95}) chosen on the fold's training patients: no training progressor patient lost relative to A12's own training detection, then fewest training NPs flagged ("target", detection ≥ R49's training detection, gave identical choices). Band sequencing counts samples only at flags with u < t + δ.
- **Sequencing:** 1 sample (0 in R49's middle band, whose top sample is already sequenced) + the second only if the first is quiet (sequential), against 2 (1) for the final rule.
- **Optimistic rows:** each fixed-bar cell also carries `apparent` (bar at 90% of the evaluation patients' progressor endoscopies); they differ from the nested values by ≤ 0.3 NP and up to 0.7 progressors (e.g. 17p only 19.8 vs 19.7 NP; agreement-required score 29.8 vs 29.1 caught). Soft veto with δ chosen on the evaluation patients: δ ≥ 5 → 17.2.
- **Compute:** Slurm prefixes `exe8f`, `exe8fb` (features), `exe8m`, `exe8r2` (evaluation). Row-level files in `killcoyne_mm/explore_E8/` on the cluster only.

## What I would do next

1. Adopt the sequential check now (no decision changes, −0.59 samples per patient); pre-specify a band δ on a new cohort before using it.
2. Test the soft veto as a one-look rule (ACE-B projection: each patient's first endoscopy only, no memory), where its protection of high-score progressors should matter.
3. With the 4× data: purity/ploidy and 17p allelic imbalance in 0.4×-quiet progressor samples (the remaining biological objection), and a depth-robustness check of the quiet call.

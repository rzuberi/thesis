# Two papers, agent KCF: every Killcoyne 2020 figure on our cohort, with H&E next to copy number

3 November 2026. Rules: `paper/two_papers/RUN_RULES.md`. Paper: Killcoyne et al., "Genomic copy number predicts esophageal cancer years before transformation", Nat Med 26:1726–1732 (2020), doi 10.1038/s41591-020-1033-y. Sources read: `paper/reviews_round7/lookup/sources/natmed_article.txt`, `pmc_PMC7116403.txt`, the source-data workbooks `MOESM4`–`MOESM16.xlsx`, the package `BarrettsProgressionRisk` (`R/risk_prediction.R`, `rxRules`), and the publisher PDF held locally (`~/Downloads/s41591-020-1033-y.pdf`, all 4 main and 10 Extended Data figures; nothing was downloaded).

## Plan (written before any number was computed)

**Population.** The 571 pre-event samples (288 endoscopies, 75 patients, 32 progressors) for every performance number; the 676 samples / 80 patients with a matched slide (set C, which includes the HGD/IMC endpoint samples) wherever Killcoyne plotted all samples (Fig. 2a, 2b, 2d, 3a, 3b endpoint bar, Extended Data 1, 5, 7a, 10). Their 773 samples are not available with H&E; their published probabilities restricted to our samples are shown as a reference.

**Scores (stored held-out predictions, no new model).** Copy number = L-CNV (Killcoyne's shipped matrix, our 10 × 10 patient-grouped folds, nested λ; 0.801). H&E = clean-tile L-IMG (agent ART refit; 0.811; the planned primary image model after `two_papers_ART.md`). Combined = per-repeat mean of the two probabilities (clean L-LATE; 0.875). Published P = Killcoyne's leave-one-patient-out probability (reference). Grade (NDBE / ID / LGD) and p53 IHC as the grey comparator where a panel has one. Only Extended Data Fig. 6 (accuracy vs number of patients) needs refits: L-CNV and clean L-IMG refitted inside the same outer folds with the training patients subsampled to 20–60 (`tp_kcf_lc.R`).

**Risk classes.** Killcoyne: low Pr ≤ 0.3, moderate, high Pr ≥ 0.5, set to reach sample sensitivity 0.87 (low cut) and specificity 0.82 (high cut) on their cohort. Ours: in each outer fold, the two cuts are chosen on the training patients' inner out-of-fold predictions to hit those same operating points (87% of training progressor samples above the low cut; 82% of training non-progressor samples below the high cut), then applied to the held-out patients. Fixed 0.3 / 0.5 cuts are reported as a sensitivity check. Displayed classes are the median over the 10 repeats; rates are averaged over repeats.

**Inference.** Patient bootstrap, 2,000 draws, `RandomState(0)`, predictions fixed; paired differences H&E − CN and combined − CN on the same draws. "Comparable" = CIs overlap; "better" only when the paired-difference CI excludes 0. AUROC = fold-stratified concordance averaged over repeats (P1A convention).

**Smoke.** The loader must reproduce L-CNV 0.801, stored L-IMG 0.847, clean L-IMG 0.811, clean L-LATE 0.875, stored L-LATE 0.889, published P 0.823; the learning-curve refit with K above the training size must equal the stored outer predictions.

**Outputs.** Scripts `scripts/paper_plan/tp_kcf_figs.py` (cluster: smoke, bootstrap, panels, learning-curve merge), `tp_kcf_lc.R` (cluster refits), `tp_kcf_compose.py` (local: four-way pages and PDF). Aggregates `results/paper_final/two_papers_KCF/`. Row-level outputs `killcoyne_mm/two_papers_KCF/`. Figures `paper/one_paper/killcoyne_repro/` (local, not committed): `original/` (cropped published panels, internal comparison only), `panels/`, `kcf_<key>_4way.png`, `killcoyne_4way.pdf`, `INDEX.md`. Slurm prefix `tpkcf`.

## Inventory of Killcoyne 2020 figures (4 main, 10 Extended Data; 43 lettered panels)

Decision codes: **A** reproducible on our cohort; **B** reproducible with H&E added (four-way page); **C** not reproducible (reason given).

| Figure | Panel | Content (theirs) | Decision |
|---|---|---|---|
| Fig. 1 | a | Cohort design schematic: 45 P / 43 NP, follow-up 1–15 / 3–13 years, all endoscopies and levels sampled | A (our cohort timeline; no H&E analogue) |
| Fig. 1 | b | Per-sample 5-Mb CN profiles of one NP and one P patient, grouped by endoscopy year and level | A, with the three model classes printed per sample |
| Fig. 1 | c | Genome-wide relative CN distribution, all samples, NP (n = 424) vs P (n = 349) | B (CN split by outcome; H&E and combined: same plot split by H&E-high vs H&E-low samples) |
| Fig. 1 | d | Same, NDBE samples only (NP 346, P 172) | B (as 1c) |
| Fig. 2 | a | Histogram of per-sample log relative risk (= logit Pr) coloured by risk class; inset decile calibration | B |
| Fig. 2 | b | Risk-class shares by pathology, NP vs P, discovery 773 samples (NDBE P high 60.5%, NP low 64.7%) | B |
| Fig. 2 | c | Same, validation cohort (76 patients, 213 samples) | C: validation cohort not available to us |
| Fig. 2 | d | Mini heatmaps of risk class per sample (endoscopy × oesophageal level) for all 88 patients | B |
| Fig. 3 | a | Per-endoscopy maximum risk over months since first endoscopy, per patient, NP and P; marker = maximum pathology | B |
| Fig. 3 | b | Share of progressor endoscopies with ≥ 1 high-risk sample by months before endpoint (50% > 96 months; 78% at 12–24) | B (grade comparator added in grey) |
| Fig. 4 | a | Schematic of surveillance rules from risk classes (package `rxRules`) | Used as the rule in 4b; schematic not redrawn |
| Fig. 4 | b | Recommendation at the second endoscopy, P vs NP (P RFA 19/35; NP 3–5-year 21/41) | B (grade/p53 mapped into the same rule as comparator) |
| Fig. 4 | c–e | Three example patients: samples by time and level coloured by risk class, with BSG 2014 vs CN-model recommendation | B (three patients chosen by rule, anonymised) |
| ED 1 | a | Per-sample cx score, NP vs P (Wilcoxon p 2.4e-06) | B (cx; H&E and combined log odds) |
| ED 1 | b | ROC of cx alone (AUC 0.6) | B (ROC of each score, cx and published P overlaid) |
| ED 1 | c | CN-altered 5-Mb windows and arms at the first endoscopy, NP vs P (p 6e-08, 5.5e-11) | B (H&E and combined probability at the first endoscopy) |
| ED 1 | d | Altered arms at first vs final endoscopy per patient (difference P vs NP p 7e-04) | B |
| ED 2 | a | AUC / sensitivity / specificity at Pr = 0.3, model on all samples vs model without HGD/IMC | B in part: we evaluate all samples vs pre-event samples; we do not retrain without HGD/IMC |
| ED 2 | b | Same metrics per sample, endoscopy mean/max, patient mean/max | B |
| ED 3 | a–d | External validation on Seattle Barrett's Study SNP arrays | C: no SNP-array data |
| ED 4 | a–b | Model trained on SNP-array data only | C: no SNP-array data |
| ED 5 | a–b | Per-patient risk heatmaps with axis labels and pathology, P and NP | B (merged with Fig. 2d) |
| ED 6 | a | Cross-validated classification accuracy vs number of training patients | B in part (AUROC only; accuracy at 0.5 not computed) |
| ED 6 | b | Number of non-zero coefficients vs number of patients | B (copy number and H&E coefficient counts, in `lc.json`; not drawn) |
| ED 6 | c | LOO AUC vs number of patients (0.70 at 28 → 0.87 at 88; 0.89 with validation; SNP data no gain) | B (learning curve; validation and SNP bars C) |
| ED 6 | d | Class shares by pathology for a model trained on discovery + validation (164 patients) | C: validation cohort not available |
| ED 7 | a | Share of aberrant p53 IHC by pathology in progressor samples | B (p53 in grey next to each score's high-risk share) |
| ED 7 | b | Chromosome 17 CN distribution, NP vs P, with model features (17p loss, 17q gain) | A (CN only) |
| ED 8 | a–c | Raw QDNAseq QC plots of a cell line, a fresh-frozen tumour and an FFPE technical replicate | C: those samples are not in our data and the panel is a QC illustration |
| ED 9 | a–c | Bin-size tuning (15, 50, 100, 500 kb): CV accuracy, LOPO AUC, discovery vs validation | C: needs re-segmentation and retraining at three more bin sizes (we hold 50 kb only), and the validation cohort; no H&E analogue |
| ED 10 | a | Risk-class shares NP vs P, discovery, per bin size (50 kb: NP 0.65/0.17/0.18, P 0.13/0.15/0.72) | B (50 kb only) |
| ED 10 | b | Same, validation cohort | C: validation cohort not available |

Count: 4 main and 10 Extended Data figures, 43 lettered panels (main 15, Extended Data 28). By panel: A 3 (Fig. 1a, 1b, ED7b); B 24 (Fig. 1c–d, 2a, 2b, 2d, 3a–b, 4b–e, ED1a–d, ED2a–b, ED5a–b, ED6a–c, ED7a, ED10a; ED2a and ED6a–b only in part); rule only 1 (Fig. 4a); C 15 (Fig. 2c, ED3a–d, ED4a–b, ED6d, ED8a–c, ED9a–c, ED10b). Built: 20 comparison pages (17 four-way, 3 two-way).

---

## Results

Run 3 November 2026. Cluster campaigns `tpkcfs` (learning-curve smoke), `tpkcfl` (100 learning-curve refits: 5 sizes x 10 repeats x 2 feature sets, ~3 min each), `tpkcfm`/`tpkcfc` (smoke, bootstrap), `tpkcff` (panels), `tpkcflm2` (learning-curve merge); all CPU. Aggregates `results/paper_final/two_papers_KCF/{smoke,stats,figs,lc}.json`. Panel-by-panel results, file names and paper use: `paper/one_paper/killcoyne_repro/INDEX.md` (local); all pages in `killcoyne_4way.pdf`.

### Smoke (known numbers reproduced)

| Quantity | Expected | Reproduced |
|---|---|---|
| L-CNV, fold-stratified sample AUROC, 571 pre-event | 0.801 | 0.801 |
| stored L-IMG | 0.847 | 0.847 |
| clean-tile L-IMG | 0.811 | 0.811 |
| clean L-LATE | 0.875 | 0.875 |
| stored L-LATE | 0.889 | 0.889 |
| published P | 0.823 | 0.823 |
| `tp_kcf_lc.R` with K above the training size vs stored outer predictions (repeat 1) | identical | max abs difference 0.0 (copy number and H&E) |
| inner predictions cover every training row of every outer fold | yes | yes |

Deviation from the plan: endoscopy units are patient x months-before-final (308 pre-event time points, 347 in set C) rather than the `Endoscopy` field, because 28 of its groups contain samples taken in different months; Killcoyne's time axes need one time per unit.

### Key results (95% patient-bootstrap CI; paired difference vs copy number)

| Killcoyne panel | Killcoyne | Copy number (ours) | H&E | H&E + copy number |
|---|---|---|---|---|
| ED1b sample AUROC (571 pre-event; theirs 773 LOPO) | 0.87 | 0.80 [0.72, 0.88] | 0.81 [0.75, 0.87]; +0.01 [-0.08, +0.11] | 0.875 [0.81, 0.93]; +0.07 [+0.02, +0.13] |
| Fig. 2b NDBE progressor samples high | 60.5% | 60% [46, 72] | 59% [50, 69]; -1 [-15, +15] | 70% [58, 82]; +10 [+2, +22] |
| Fig. 2b NDBE non-progressor samples low | 64.7% | 54% [43, 66] | 59% [53, 66]; +5 [-7, +17] | 72% [64, 80]; +18 [+11, +25] |
| Fig. 3b progressor endoscopies with a high sample, > 96 months | 50% (n = 16) | 53% [11, 84] (n = 12) | 62% [36, 82]; +8 [-16, +50] | 66% [29, 98]; +13 [-2, +45] |
| Fig. 3b, 12-24 months | 78% (n = 23) | 62% [43, 81] (n = 17) | 89% [75, 99]; +27 [+1, +50] | 92% [81, 99]; +30 [+9, +50] |
| Fig. 4b progressors to RFA after 2nd endoscopy | 19 / 35 | 12 / 25 | 15 / 25; +3 [-3, +9] | 16 / 25; +4 [-1, +9] |
| Fig. 4b non-progressors to 3-5-year surveillance | 21 / 41 | 19 / 43 | 10 / 43; -9 [-17, -1] | 16 / 43; -3 [-10, +4] |
| ED1c AUROC at the first endoscopy (patient level) | p 6e-08 (windows) | 0.82 [0.72, 0.91] | 0.84 [0.75, 0.92]; +0.02 [-0.10, +0.15] | 0.90 [0.83, 0.96]; +0.08 [+0.005, +0.17] |
| ED6c AUROC, smallest -> all training patients | 0.70 (28) -> 0.87 (88) | 0.60 (20) -> 0.80 (~72) | 0.67 -> 0.81 | 0.69 -> 0.88 |

Grade and p53 put into the same Fig. 4b rule send 3 of 25 progressors to RFA and 13 of 25 to 3-5-year surveillance; no score sends more than 1. p53 aberrant rates by grade in progressor samples reproduce Killcoyne's (NDBE 12% vs 11%, HGD 70% vs 64%).

### What this means for the paper plan

Every reproducible Killcoyne figure type also works with H&E: H&E alone is comparable to copy number on every panel except two (it de-escalates fewer non-progressors in Fig. 4b and catches fewer endpoint endoscopies in Fig. 3b), and the combined score is better than copy number on the class and AUROC panels. The strongest additions for Paper 1 are Fig. 2b (combined classes), Fig. 3b (lead time), Fig. 1d (H&E-high NDBE samples carry no extra copy-number change) and, for Paper 2, Fig. 4b (grade and p53 would leave 13 of 25 progressors on 3-5-year surveillance).

# Two papers, agent CNC: does copy number get the same effort as H&E?

28 October 2026. Rules: `paper/two_papers/RUN_RULES.md`. Trigger: reviewers flagged asymmetric effort (about 30 image variants against 4 copy-number versions). Population: the 571 pre-event samples (288 endoscopies, 75 patients, 32 progressors) of the 676 samples from 80 patients of the Killcoyne discovery cohort with a matched H&E slide; models trained on set C (676 samples) as always.

## Plan (written before any new number was computed)

**1. Survey.** Copy-number callers, feature methods and foundation models that could apply to 0.3–0.4× FFPE sWGS (50 bp single-end, QDNAseq hg38 50 kb bins): input needs, whether they work at our depth, availability. Sources cited; untested statements marked as inference.

**2. New copy-number representations** (all from the stored per-sample QDNAseq outputs of the discovery cohort in `SWGCohort/copy_number_hg38/train/perPatient/50kb/`, read-only; no BAM re-counting needed because ACQ reproduced those counts exactly):
- *QDNAseq CBS*: the stored per-sample QDNAseq CBS segmentation (`50.copy_number_segmented.rds`; another segmenter than the package's multipcf), tiled to the package's 5-Mb tiles and arms, arm-subtracted tiles + arms + cx (the `km_linear.R` construction).
- *ACE absolute*: ACE (Poell et al. 2019) on the same QDNAseq object, ploidy 2, best-fit cellularity; absolute copies tiled the same way, plus cellularity and fit error.
- *ichorCNA*: raw 50 kb counts summed to the 1 Mb ichorCNA hg38 bins, ichorCNA HMM without a panel of normals; log2 ratio tiled the same way plus tumour fraction and ploidy.
- *CIN signatures*: Drews et al. 2022 (17 CX exposures) and Macintyre et al. 2018 (7 exposures) via `CINSignatureQuantification` on ACE absolute segments.
- *Genome-instability scores*: fraction genome altered, wGII, segment and breakpoint counts, LST-like count, chromothripsis-like oscillation count, from the CBS and ACE segments; ACE cellularity, ichorCNA tumour fraction.
- *TESSERA embeddings* (if weights are public): CNA-only per-segment embeddings of the CBS log2 segments (GRCh38 lifted to GRCh37 by the package), mean + max pooled + log segment count.
- Combined block: package joint features + genome-instability scores.

**3. Fitting and evaluation (same as L-CNV).** `tp_cnc_refit.R` = `tp_art_refit.R` (`ex_e3_refit.R`) with CNC paths: the `kv_cv.R` outer 10 × 10 patient-grouped folds, glmnet α 0.9, class-error-minimum λ from 10 × 5 patient-grouped CV on the training patients, and the `hz_fit.R` inner loop (5 inner folds per outer fold) for nested selection. New blocks are z-scaled on training rows only. Metrics: fold-stratified AUROC (sample level and patient-weighted), 2,000-draw patient bootstrap (`tp_p1b_main.py` `hblock`, `RandomState(0)`), Δ vs L-CNV (shipped matrix), Δ vs clean-tile L-IMG (ART `refit/clean`), and L-LATE = mean of the new CN probability and clean L-IMG.

**4. Nested CN selection.** Per (repeat, outer fold) pick the CN representation with the best inner out-of-fold AUROC on that fold's pre-event training samples (`tp_p1b_main.py` `select_` logic, unchanged), use its held-out predictions for that fold. Candidate sets: (a) the four existing versions (shipped, joint package, past-only, per-sample); (b) everything. Report nested AUROC, the apparent best (optimistic) and the optimism, nested CN − clean L-IMG and nested L-LATE.

**Smoke.** (i) refit script with FEAT = shipped matrix and no rescaling must reproduce stored L-CNV outer and inner predictions exactly (0.801); (ii) the stored raw counts inside the QDNAseq objects equal the `50.raw_read_counts.txt` that ACQ matched to the BAMs; (iii) each new pipeline is run on 5 samples first and inspected (segment counts, cellularity, tumour fraction range); (iv) metrics reproduce L-CNV 0.801, clean L-IMG 0.811, clean L-LATE 0.875.

Scripts `scripts/paper_plan/tp_cnc_*`; aggregates `results/paper_final/two_papers_CNC/`; row-level `killcoyne_mm/two_papers_CNC/`; Slurm prefix `tpcnc`.

---
## 1. Survey: copy-number methods for 0.3–0.4× FFPE sWGS

Our data: 50 bp single-end reads, 13.8–21.0 M counted reads per BAM (ACQ), QDNAseq hg38 50 kb bins, no matched normals, no SNP allele fractions (about 0.4 reads per SNP locus). "Run" = tested here (section 3). Statements about depth are from the cited source unless marked *inference*.

| Method | What it gives | Input needs | Works at our depth? | Availability | Here |
|---|---|---|---|---|---|
| QDNAseq (Scheinin et al. 2014, Genome Res, 10.1101/gr.175141.114) | binned, GC/mappability-corrected ratios; CBS segments; CGHcall gain/loss calls | BAM, bin annotation | yes: built for sWGS of FFPE (0.1× and up) | Bioconductor | current pipeline; its stored CBS segments run as a new representation |
| BarrettsProgressionRisk (Killcoyne et al. 2020, Nat Med) | multipcf segments, 5-Mb and arm tiles, P | QDNAseq raw + fitted counts | yes (the discovery cohort itself) | GitHub | existing (shipped matrix, joint, per-sample, past-only) |
| ACE (Poell et al. 2019, Bioinformatics, 10.1093/bioinformatics/bty1055) | cellularity fit, absolute copies per segment | QDNAseq segmented object | yes in principle (designed for sWGS); needs clonal CNAs to anchor the fit (*inference*: near-diploid NDBE gives arbitrary fits) | Bioconductor 1.24 | run |
| ichorCNA (Adalsteinsson et al. 2017, Nat Commun, 10.1038/s41467-017-00965-y) | HMM segments and states, tumour fraction, ploidy | 1 Mb read-count wig (HMMcopy readCounter), GC/map wigs; panel of normals optional | yes: designed for 0.1× cfDNA; tumour-fraction floor about 3% | GitHub broadinstitute, GPL-3 | run (no panel of normals) |
| HMMcopy (Ha et al. 2012, Genome Res, 10.1101/gr.137570.112) | GC/map correction + HMM segmentation | wig counts | yes (is ichorCNA's front end) | Bioconductor | covered through ichorCNA |
| WisecondorX (Raman et al. 2019, NAR, 10.1093/nar/gky1263) | within-sample reference-bin z-scores and segments | a reference set of normal samples sequenced the same way (NIPT design) | yes for depth (0.1× NIPT); we have no normal samples, and a non-progressor reference would have to be rebuilt inside every fold | GitHub (licence not checked) | not run |
| CNVkit, WGS mode (Talevich et al. 2016, PLoS Comput Biol, 10.1371/journal.pcbi.1004873) | binned log2 and CBS/HMM segments | BAM; a pooled normal reference recommended | only with large bins (*inference*); adds nothing over QDNAseq + CBS without normals | PyPI/bioconda (licence not checked) | not run |
| ASCAT.sc (VanLoo-lab GitHub; paper not checked) | total copy number, purity/ploidy grid fit | binned counts (shallow coverage) | yes (stated for shallow coverage) | GitHub, GPL-3 | not run: same idea as ACE |
| araCNA (Visscher and Yau 2025, NAR Genom Bioinform, 10.1093/nargab/lqaf124) | Mamba/Hyena model: allele-specific CN, purity, ploidy | tumour BAM, read depth **and BAF** at about 650k SNP loci (repo README) | no: BAF needs SNP coverage we do not have at 0.4× (*inference* from the README) | GitHub e-vissch, Apache-2.0 | not run |
| CNAclinic (Chandrananda, GitHub sdchandra) | QDNAseq bins + CBS, LACBS, HMM, PLS segmenters and their consensus | BAM or log ratios | yes: written for sWGS < 0.5× | GitHub | not run as a package; its CBS and HMM arms are covered by QDNAseq CBS and ichorCNA |
| CIN signatures (Drews et al. 2022, Nature, 10.1038/s41586-022-04789-9) | 17 CX signature activities from 6 CN features | absolute copy-number segments | partly: built on SNP6/WGS absolute CN; our absolute CN comes from ACE fits on mostly near-diploid samples | GitHub markowetzlab/CINSignatureQuantification | run (on ACE segments) |
| CN signatures, ovarian (Macintyre et al. 2018, Nat Genet, 10.1038/s41588-018-0179-8) | 7 signature exposures | absolute CN from sWGS (their discovery data were sWGS) | yes in design; same ACE caveat | same package (`method = "mac"`) | run |
| Pan-cancer CN signatures (Steele et al. 2022, Nature, 10.1038/s41586-022-04738-6) | 21 signatures over 48 classes (CN × LOH × segment size) | **allele-specific** CN (heterozygosity / LOH) | no: no allele-specific CN from 0.4× sWGS | SigProfilerExtractor | not run |
| Genome-instability scores: fraction genome altered, wGII (Burrell et al. 2013, Nature; Endesfelder et al. 2014, Cancer Res), LST (Popova et al. 2012, Cancer Res), chromothripsis criteria (Korbel and Campbell 2013, Cell) | single numbers per sample | segments (LST and HRD scores properly need allele-specific CN and ploidy; chromothripsis properly needs SVs) | FGA, wGII, segment and breakpoint counts: yes; LST and chromothripsis only as total-CN proxies (*inference*) | simple code | run (proxies named as such) |

**Copy-number foundation and embedding models.**

| Model | Copy-number input | Training data | Code / weights / licence | Usable here? |
|---|---|---|---|---|
| TESSERA (Sidhom, Baras, Elemento, Shah; bioRxiv 10.64898/2026.05.27.728319, posted 1 June 2026) | genome-wide **segments**: chromosome, start, end, log2 segment mean, optional LOH; self-attention over a sample's segments (up to 1,000), masked segment-mean reconstruction; joint SNV + CNA model with a contrastive objective | TCGA Pan-Cancer Atlas, about 10,000 tumours (WES; ABSOLUTE segments, GRCh37); external checks on MSK-CHORD and GENIE panels | code github.com/JW-Sidhom-Lab/tessera (PolyForm Noncommercial 1.0.0); `pip install tessera-foundation` (0.1.7); weights huggingface.co/JW-Sidhom-Lab/tessera-foundation (CC-BY-NC-4.0), with and without the LOH head; precomputed TCGA features on Zenodo 10.5281/zenodo.20419467 | **yes**: CNA-only inference works (tested on the package demo, 344 segments to 344 × 688 embeddings); academic use allowed by both licences |
| MutationProjector (Ideker lab; bioRxiv 10.1101/2025.09.08.674723; press reports a Cancer Discovery paper, not checked) | **gene-level** amplification / deletion calls in 468 panel genes, plus TMB, aneuploidy and mutational signatures | > 30,000 clinical panel tumours | not checked | no genome-wide segment input; would need gene-level calls in panel genes, which 0.4× sWGS gives only as broad arm-level states (*inference*) |
| CanBART (Chebanov and Morris; medRxiv 10.1101/2025.11.04.25339512) | tokenised somatic alterations of a clinical panel (whether CNAs are tokens: not checked) | 144,000 MSK-IMPACT profiles | not checked | no genome-wide segment input (*inference*) |

No other published or preprinted copy-number foundation model with genome-wide segment input was found (two web searches, 28 October 2026).

---

## Results

Run 28 October 2026. Scripts (`scripts/paper_plan/`): `tp_cnc_seg.R` (per-sample CBS / ACE / ichorCNA, 676 Slurm tasks, campaign `tpcncseg`), `tp_cnc_feats.R` (feature blocks, CIN signatures), `tp_cnc_tessera.py` (TESSERA embeddings), `tp_cnc_refit.R` (L-CNV recipe, campaigns `tpcncrt`, `tpcncrf`, `tpcncrf2`), `tp_cnc_main.py` (smoke_refit, score, select), `tp_cnc_render.py` (tables below); `tp_cnc_install.R` (library setup), `tp_cnc_probe.R` (object probe). Aggregates `results/paper_final/two_papers_CNC/{smoke_refit,feats_info,score,select}.json`. Row-level outputs on the cluster under `killcoyne_mm/two_papers_CNC/`. All CPU (epyc, rocm, cuda, h200 partitions as CPU workers).

**Headline: no new copy-number representation beats the best existing one. The best honest copy-number model is 0.81, level with clean-tile H&E (0.811), and the copy-number side carries the same selection optimism as the image side (+0.034 against +0.020 to +0.031).**

### Smoke checks (known numbers reproduced)

| Check | Expected | Reproduced |
|---|---|---|
| `tp_cnc_refit.R` on the shipped matrix vs stored L-CNV (cv/preds cfg_00 + horizons/inner), 10 repeats | identical | max abs Δ prediction 0.0 outer and inner, same λ in all 10 repeats |
| L-CNV, clean L-IMG, clean L-LATE, published L-IMG (fold-stratified, sample level) | 0.801 / 0.811 / 0.875 / 0.847 | 0.801 / 0.811 / 0.875 / 0.847 |
| joint package, per-sample, past-only (stored predictions, same metric code) | 0.845 / 0.785 / 0.800 | 0.845 / 0.785 / 0.800 |
| raw counts in the stored QDNAseq objects = `50.raw_read_counts.txt` (the file ACQ matched bin by bin to the BAMs) | equal | equal in 676 / 676 samples |
| CBS arm values vs stored package arm values, per-sample Spearman | high | median 0.84 (5-Mb tiles 0.53) |
| 5-sample pipeline smoke (CBS, ACE, ichorCNA), then TESSERA on the package demo and on 5 of our samples | runs, plausible ranges | runs; see fits below |

**What the new pipelines produced** (`feats_info.json`):
- CBS: median 151 segments per sample (113.5 with ≥ 10 bins). 21 of 632 tile columns had no segment in > 50% of samples (unmappable or centromeric tiles) and were dropped.
- ACE: fitted in 676 / 676; best-fit cellularity 0.05 (min), 0.11 (10th centile), 0.725 (median), 1.0 (90th centile and max). Most samples have no clonal CNA to anchor the fit, so cellularity, and therefore absolute copies, are close to arbitrary in near-diploid samples (*inference* from the spread).
- ichorCNA: fitted in 667 / 676 (9 failures imputed with training-row means); tumour fraction 0 (min), 0.011 (10th centile), 0.045 (median), 0.12 (90th centile), 0.70 (max). Half the samples sit near ichorCNA's stated 3% floor.
- CIN signatures: Drews and Macintyre activities for 676 / 676.
- TESSERA: 95,557 segments in, 88,633 embedded (6,924, 7%, dropped by the GRCh38 → GRCh37 liftover); 676 × 1,377 features.

### Each copy-number representation, same folds and recipe as L-CNV

Fold-stratified AUROC over the 571 pre-event samples (161 progressor samples; 75 patients, 32 progressors); 2,000-draw patient bootstrap, predictions fixed, paired Δ on the same draws. "Fused" = mean of the CN probability and clean-tile L-IMG (as L-LATE).

**Sample level** (reference: L-CNV 0.801 [0.710, 0.875]; clean L-IMG 0.811 [0.753, 0.872]; L-LATE = L-CNV + clean L-IMG 0.875 [0.812, 0.925]; published L-IMG 0.847)

| CN representation | AUROC [95% CI] | Δ vs L-CNV | Δ vs clean L-IMG | Fused with clean L-IMG | Fused − clean L-IMG | Fused − L-LATE |
|---|---|---|---|---|---|---|
| L-CNV (shipped matrix) | 0.801 [0.710, 0.875] | — | -0.010 [-0.114, +0.086] | 0.875 [0.812, 0.925] | +0.063 [+0.013, +0.111] | — |
| joint package rebuild | 0.845 [0.766, 0.904] | +0.044 [-0.031, +0.115] | +0.034 [-0.062, +0.119] | 0.890 [0.836, 0.937] | +0.079 [+0.031, +0.129] | +0.015 [-0.021, +0.053] |
| per-sample package segmentation | 0.785 [0.723, 0.845] | -0.017 [-0.088, +0.064] | -0.027 [-0.095, +0.047] | 0.863 [0.804, 0.916] | +0.052 [+0.016, +0.088] | -0.011 [-0.048, +0.025] |
| past-only package segmentation | 0.800 [0.723, 0.867] | -0.002 [-0.074, +0.065] | -0.012 [-0.106, +0.070] | 0.868 [0.812, 0.919] | +0.057 [+0.013, +0.101] | -0.006 [-0.040, +0.025] |
| QDNAseq CBS segments | 0.777 [0.707, 0.839] | -0.025 [-0.102, +0.054] | -0.035 [-0.118, +0.041] | 0.863 [0.807, 0.913] | +0.052 [+0.012, +0.093] | -0.012 [-0.046, +0.022] |
| ACE absolute copy number | 0.731 [0.661, 0.794] | -0.071 [-0.159, +0.016] | -0.081 [-0.172, +0.000] | 0.840 [0.784, 0.886] | +0.028 [-0.015, +0.069] | -0.035 [-0.077, +0.007] |
| ichorCNA (1 Mb HMM) | 0.755 [0.686, 0.816] | -0.046 [-0.118, +0.029] | -0.056 [-0.136, +0.026] | 0.867 [0.807, 0.918] | +0.055 [+0.015, +0.095] | -0.008 [-0.040, +0.025] |
| genome-instability scores | 0.639 [0.558, 0.713] | -0.162 [-0.259, -0.063] | -0.172 [-0.271, -0.088] | 0.813 [0.755, 0.869] | +0.002 [-0.024, +0.026] | -0.061 [-0.101, -0.019] |
| CIN signatures (Drews 2022) | 0.652 [0.573, 0.719] | -0.150 [-0.242, -0.056] | -0.160 [-0.250, -0.078] | 0.810 [0.751, 0.866] | -0.001 [-0.030, +0.026] | -0.064 [-0.106, -0.019] |
| CN signatures (Macintyre 2018) | 0.594 [0.503, 0.670] | -0.207 [-0.310, -0.105] | -0.217 [-0.327, -0.120] | 0.805 [0.746, 0.861] | -0.007 [-0.031, +0.014] | -0.070 [-0.111, -0.027] |
| joint package + instability scores | 0.848 [0.772, 0.908] | +0.046 [-0.033, +0.124] | +0.036 [-0.056, +0.124] | 0.893 [0.838, 0.941] | +0.082 [+0.033, +0.132] | +0.019 [-0.022, +0.058] |
| TESSERA embeddings (TCGA rank-mapped) | 0.769 [0.694, 0.828] | -0.033 [-0.099, +0.031] | -0.043 [-0.128, +0.037] | 0.858 [0.797, 0.910] | +0.046 [+0.007, +0.085] | -0.017 [-0.052, +0.017] |
| TESSERA embeddings (raw log2) | 0.682 [0.606, 0.749] | -0.120 [-0.204, -0.038] | -0.130 [-0.226, -0.043] | 0.821 [0.758, 0.876] | +0.009 [-0.029, +0.048] | -0.054 [-0.098, -0.009] |

**Patient-weighted** (reference: L-CNV 0.822 [0.738, 0.887]; clean L-IMG 0.832 [0.775, 0.884]; L-LATE = L-CNV + clean L-IMG 0.891 [0.839, 0.934]; published L-IMG 0.852)

| CN representation | AUROC [95% CI] | Δ vs L-CNV | Δ vs clean L-IMG | Fused with clean L-IMG | Fused − clean L-IMG | Fused − L-LATE |
|---|---|---|---|---|---|---|
| L-CNV (shipped matrix) | 0.822 [0.738, 0.887] | — | -0.010 [-0.102, +0.072] | 0.891 [0.839, 0.934] | +0.059 [+0.016, +0.102] | — |
| joint package rebuild | 0.832 [0.754, 0.899] | +0.010 [-0.061, +0.084] | +0.000 [-0.092, +0.090] | 0.893 [0.841, 0.938] | +0.061 [+0.014, +0.111] | +0.002 [-0.030, +0.035] |
| per-sample package segmentation | 0.806 [0.747, 0.857] | -0.016 [-0.075, +0.057] | -0.026 [-0.092, +0.044] | 0.881 [0.830, 0.924] | +0.049 [+0.018, +0.084] | -0.010 [-0.037, +0.020] |
| past-only package segmentation | 0.796 [0.726, 0.863] | -0.026 [-0.092, +0.046] | -0.036 [-0.124, +0.048] | 0.877 [0.826, 0.922] | +0.045 [+0.006, +0.087] | -0.014 [-0.045, +0.016] |
| QDNAseq CBS segments | 0.765 [0.697, 0.832] | -0.057 [-0.133, +0.022] | -0.067 [-0.149, +0.014] | 0.868 [0.818, 0.913] | +0.036 [+0.002, +0.072] | -0.023 [-0.056, +0.009] |
| ACE absolute copy number | 0.711 [0.635, 0.783] | -0.111 [-0.202, -0.017] | -0.121 [-0.211, -0.036] | 0.839 [0.784, 0.887] | +0.007 [-0.030, +0.047] | -0.052 [-0.095, -0.014] |
| ichorCNA (1 Mb HMM) | 0.773 [0.704, 0.837] | -0.049 [-0.122, +0.035] | -0.059 [-0.141, +0.022] | 0.884 [0.835, 0.925] | +0.052 [+0.017, +0.090] | -0.007 [-0.038, +0.029] |
| genome-instability scores | 0.631 [0.541, 0.716] | -0.191 [-0.293, -0.094] | -0.201 [-0.303, -0.103] | 0.824 [0.765, 0.878] | -0.008 [-0.037, +0.019] | -0.067 [-0.103, -0.032] |
| CIN signatures (Drews 2022) | 0.636 [0.554, 0.713] | -0.186 [-0.286, -0.084] | -0.196 [-0.295, -0.101] | 0.823 [0.769, 0.874] | -0.009 [-0.037, +0.020] | -0.068 [-0.107, -0.026] |
| CN signatures (Macintyre 2018) | 0.557 [0.470, 0.642] | -0.265 [-0.365, -0.151] | -0.275 [-0.382, -0.168] | 0.815 [0.759, 0.869] | -0.017 [-0.041, +0.005] | -0.076 [-0.113, -0.037] |
| joint package + instability scores | 0.839 [0.762, 0.901] | +0.017 [-0.062, +0.094] | +0.007 [-0.080, +0.090] | 0.895 [0.843, 0.940] | +0.063 [+0.016, +0.111] | +0.004 [-0.034, +0.041] |
| TESSERA embeddings (TCGA rank-mapped) | 0.751 [0.668, 0.823] | -0.072 [-0.163, +0.018] | -0.082 [-0.166, -0.001] | 0.854 [0.785, 0.911] | +0.022 [-0.022, +0.066] | -0.037 [-0.091, +0.005] |
| TESSERA embeddings (raw log2) | 0.652 [0.561, 0.737] | -0.170 [-0.273, -0.074] | -0.181 [-0.278, -0.086] | 0.819 [0.750, 0.879] | -0.013 [-0.057, +0.029] | -0.072 [-0.127, -0.027] |

### Nested choice of the copy-number representation (same treatment as the image side)

Per (repeat, outer fold) the representation with the best inner out-of-fold AUROC on that fold's pre-event training samples; its held-out predictions are used for that fold. Selection criterion unweighted (as in P1B); evaluated at both units.

| Candidate set | Unit | Nested CN AUROC | Nested − L-CNV | Nested CN − clean L-IMG | Nested L-LATE | Nested L-LATE − clean L-IMG | Apparent best (optimistic) | Optimism: best − nested | Chosen most often |
|---|---|---|---|---|---|---|---|---|---|
| existing_4 (4) | sample | 0.811 [0.734, 0.872] | +0.010 [-0.056, +0.071] | -0.000 [-0.092, +0.083] | 0.876 [0.818, 0.926] | +0.064 [+0.020, +0.112] | 0.845 (pkg) | +0.034 [+0.015, +0.068] | pkg 70, pkgpast 13, their 12 |
| existing_4 (4) | patient-weighted | 0.801 [0.724, 0.868] | -0.021 [-0.083, +0.039] | -0.031 [-0.121, +0.058] | 0.883 [0.829, 0.928] | +0.051 [+0.007, +0.095] | 0.832 (pkg) | +0.031 [+0.017, +0.085] | pkg 70, pkgpast 13, their 12 |
| all (13) | sample | 0.813 [0.737, 0.876] | +0.012 [-0.056, +0.075] | +0.002 [-0.087, +0.083] | 0.876 [0.818, 0.927] | +0.065 [+0.019, +0.112] | 0.848 (pkg_gis) | +0.034 [+0.019, +0.073] | pkg 41, pkg_gis 40, their 9 |
| all (13) | patient-weighted | 0.805 [0.731, 0.870] | -0.017 [-0.082, +0.048] | -0.027 [-0.117, +0.057] | 0.881 [0.828, 0.927] | +0.049 [+0.006, +0.094] | 0.839 (pkg_gis) | +0.033 [+0.020, +0.085] | pkg 41, pkg_gis 40, their 9 |

For comparison, P1B's nested image choice: 0.816–0.827 (optimism of the reported L-IMG +0.020 to +0.031).

### What this says

- **Effort.** Copy number now has 13 representations (4 existing + 9 new: 3 callers or segmenters, 2 signature sets, 1 instability-score block, 1 combined block, 2 TESSERA variants). None of the 9 new ones beats the joint package rebuild (0.845). Adding instability scores to it gives 0.848 (+0.003 over the package alone; measured, sample level).
- **Callers.** Per-sample callers all land at or below L-CNV: QDNAseq CBS 0.777, ichorCNA 0.755, ACE 0.731 (sample level). CBS per sample (0.777) is close to the package run per sample (0.785). My inference: the joint package's lead comes from segmenting a patient's samples together, not from the segmenter.
- **Summary scores** (instability 0.639, Drews 0.652, Macintyre 0.594) carry weak signal. Fused with clean L-IMG they add nothing (+0.002, −0.001, −0.007) and fall below L-LATE by 0.06–0.07 (CIs exclude 0).
- **TESSERA** (CNA-only, rank-mapped to TCGA) gives 0.769 [0.694, 0.828], −0.033 vs L-CNV [−0.099, +0.031]; without rank-mapping 0.682. Fused with clean L-IMG it reaches 0.858, +0.046 over clean L-IMG [+0.007, +0.085], −0.017 vs L-LATE. The model was trained on TCGA tumour WES ABSOLUTE segments; ours are low-purity, mostly near-diploid sWGS segments (*inference*: out of distribution).
- **Selection optimism is symmetric.** Choosing the CN representation inside the CV gives 0.811–0.813 (sample) and 0.801–0.805 (patient-weighted). The apparent best (joint package, 0.845; with scores 0.848) is optimistic by +0.034 [+0.015, +0.068] at sample level, similar to the image side's +0.020 to +0.031. Nested CN − clean L-IMG: +0.002 [−0.087, +0.083] (all 13), −0.000 [−0.092, +0.083] (existing 4).
- **Fusion holds.** Nested L-LATE 0.876 [0.818, 0.927], +0.065 [+0.019, +0.112] over clean L-IMG; equal to L-LATE on L-CNV (0.875). Every representation with AUROC ≥ 0.75 adds +0.046 to +0.082 to clean L-IMG (sample level).

### What changes for Paper 1

- The asymmetric-effort criticism is answered with numbers: 13 CN representations against about 30 image variants, and after nested selection on both sides copy number (0.81) and clean H&E (0.81–0.83 nested, 0.811 clean) are level. Keep "comparable", not "H&E beats copy number".
- Report the joint package (0.845) the way L-IMG 0.847 is reported: as a best-of-many value with its selection-inclusive companion (0.811). Keep L-CNV on the shipped matrix as the single pre-specified comparator.
- One Extended Data forest of the 13 CN representations (with the fused column) and one sentence on TESSERA: a public CN foundation model, run, below L-CNV on this data. No new CN method needs to enter the main text.

### Deviations from the plan

- The planned "combined block" is the joint package + instability scores (`pkg_gis`).
- cx for the new tiled blocks is a sample-internal count (tiles beyond the sample's own mean ± 2 SD), not the cohort-standardised count of `km_linear.R`; a tile spanning a centromere subtracts its first covering arm only; tile columns missing in > 50% of samples are dropped (21 CBS / ACE, 25 ichorCNA). Before this fix the CBS, ACE and ichorCNA refits failed on all-missing columns and were rerun (`tpcncrf2`); the other blocks were byte-identical and kept.
- ACE absolute copies were clamped to [0, 10] for tiling and to ≥ 0 for the signatures; CBS ratios floored at 1/8 before log2.
- TESSERA run CNA-only (the package feeds a placeholder SNV per sample; the published variants have no cross-modal attention, so CNA embeddings do not depend on it, per the package code). Two variants (rank-mapped and raw) are reported; neither was chosen after seeing the result.
- Not run: WisecondorX (needs normal references), CNVkit (no gain over QDNAseq + CBS without normals), ASCAT.sc (same idea as ACE), araCNA (needs BAF), Steele 2022 signatures (need allele-specific CN), MutationProjector and CanBART (no genome-wide segment input).

### Implementation notes

- Libraries: ACE 1.24.0, HMMcopy 1.48.0, ichorCNA 0.3.2 (GitHub master + `scripts/runIchorCNA.R`), CINSignatureQuantification 1.2.0, installed into `envs/cnc_rlib` and used with the `killcoyne_r` R 4.4.1 (its own library untouched). TESSERA 0.1.7 + tensorflow-cpu 2.21 in `envs/cnc_py`; weights snapshot ff02ded, GRCh37 reference and hg38ToHg19 chain cached under `envs/cnc_tools/cache` (offline at run time).
- ichorCNA wig: raw 50 kb counts summed into ichorCNA's 1 Mb hg38 bins (QDNAseq bins start at 1 and are contiguous, so 20 bins = 1 Mb exactly); options in the `tp_cnc_seg.R` header.
- Refits: `tp_cnc_refit.R` = `tp_art_refit.R` plus a `SCALE` switch (stored blocks used as is; new blocks z-scaled on training rows). Inner predictions of the four stored versions come from `horizons/inner` and `review_round4/r36_inner`.

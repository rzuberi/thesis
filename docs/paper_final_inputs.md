# BE paper: final checks and figures (K1–K5, F-intro, F-table, F-D1–F-D6)

**Status of this file: PRE-SPECIFICATION VERSION**, committed before any analysis or figure was produced. Results and
figure descriptions are appended in a later commit; this text is not edited afterwards.

## 1. Header (completed at the results commit)
- Date: 26 September 2026. Commit at start: `4e0cc2d`. Pre-specification commit: the commit adding this text. Frozen release only; nothing retrained.
- Inputs: patient-level scores, labels, E-HGD labels, strata and tile counts from round 3 (`feasibility/paper_plan/round3_patient_table.csv`, commit `6976646`), operating-point predictions (`followup_patient_scores.csv`, `patient_scores_predictions.csv`), later-disease table, closeout patient/QC/slide tables, image and fusion embeddings and attention arrays from `pp_latent.py` (`feasibility/paper_plan/latent/`), results JSONs of rounds 1–3 for pooled/stratified numbers (`results/paper_plan/round3_main.json`, `discovery_main.json`, `f1_cnv_killcoyne.json`, `followup_main.json`, `main_items.json`).
- Scripts: `scripts/paper_plan/pk_gpu.py` (K4 ablation, row-level scores), `pk_main.py` (K1–K5, all figures), `pk_render.py`, `pk_check_report.py`. Outputs: `results/paper_final/final_checks.json`, `results/paper_final/k4_ablation.json`, figures `results/paper_final/figs/<name>.png|.pdf` with `<name>.json` (plotted numbers, n / events per panel).

## Analysis decisions (fixed)
Primary population = 82 discovery-stratum patients (40 LGD2+ events, 26 HGD/IMC events). Secondary = stratified all-150 (pair-weighted within-stratum AUROC, weights 1,680 / 580), then pooled all-150 labelled confounded. Primary endpoint LGD2+; secondary E-HGD, labelled "added after seeing the CNV results". Tissue amount reported as an unresolved confound, not adjusted for in primary results. Arms: Clinical = C2; CNV = release RF (Killcoyne-method arm as sensitivity comparator); WSI; early, intermediate, late (mean) fusion; co-attention and late-stack in supplementary tables only; ERIN grade head excluded from all figures. Conventions as before: patient = max over rows; rank AUROC; 2,000 patient bootstraps `RandomState(0)`; permutations 2,000; fold-honest quantities from the release folds. Figures PNG + PDF 300 dpi; no tissue images committed.

## Pre-specifications

### K1. False positives by stratum
- Per model (late_mean, image_only, cnv_only, C2) at the pooled operating point already applied (follow-up predictions): FP/TN and later-HGD+ counts per stratum (discovery, validation). Within validation non-progressors: Fisher p; logistic regression later HGD+ ~ FP + baseline grade + log `kept_tiles` (statsmodels; Fisher only if the fit separates or fails). Spearman of `kept_tiles` with later HGD+ among validation non-progressors. Discovery non-progressors: follow-up after last release row (DB follow-up days; median, IQR, share with any later DB report) and the number who are Killcoyne sheet controls (NP) vs sheet cases labelled non-progressors by us.

### K2. False negatives within discovery
- Item-10 comparison repeated for late_mean and image_only using the 40 discovery progressors only: FN vs TP on interval to endpoint, endpoint type, rows, baseline and max grade, cx, MAPD noise, segments, fraction altered, reads, `kept_tiles`, tissue fraction, scanner, p53 IHC; Mann-Whitney / Fisher (2×2 only).

### K3. Latent space within discovery
- Same probe and kNN procedure as item 6 (fitted on all training-fold patients, standardisation and C on training patients), evaluated on discovery held-out patients only; AUROC with bootstrap over the 82; paired fused − unimodal (image, CNV) differences with CI.

### K4. CNV use and rank shift within discovery
- `pk_gpu.py`: for each learned fusion model and fold, held-out row scores: baseline; CNV permuted jointly across held-out rows (50 repeats, `RandomState(0)`, mean permuted score per row kept); CNV replaced by the training mean (standardised zeros); image bags permuted (50 repeats); image replaced by training-mean tile. Row-level scores saved; ΔAUROC = baseline − ablated on (a) all 150, (b) discovery 82, CI from patient bootstrap of the paired patient scores (max over rows).
- 8a within discovery: Spearman of cnv_only vs late_mean patient scores; percentile-rank change within discovery; counts moving > 20 points by label; categorical NRI (training-fold tertile groups computed on all patients, restricted to discovery) with bootstrap CI.

### K5. Risk groups within discovery
- Training-fold tertiles (as round 3) restricted to discovery; per arm (C2, cnv_only, image_only, late_mean) and endpoint (LGD2+, E-HGD): n, events, rate with Wilson CI per tertile; OR high vs low (Haldane) with Woolf CI; Cochran–Armitage trend test (scores 0/1/2; chi-square with 1 df, no continuity correction).

### Figures
- F-intro: forest plot, one row per population × endpoint (discovery, stratified, pooled × LGD2+, E-HGD) with AUROC [CI] for WSI, CNV (RF), CNV (Killcoyne); second panel WSI − CNV difference [CI] for both CNV arms with a dashed line at −0.05. Numbers from `discovery_main.json`, `round3_main.json` (pooled/stratified via R1/R2; stratified E-HGD from R2), stratified differences via bootstrap recomputed in `pk_main.py` where not already stored.
- F-table: forest plots of all whiteboard arms (C2, CNV RF, CNV KM, WSI, early, intermediate, late; supplementary rows co-attention, late-stack shown greyed): A discovery LGD2+; B discovery E-HGD; C pooled vs stratified vs discovery on LGD2+ side by side. Markdown table rendered alongside.
- F-D1: grouped bars of tertile progression rates with Wilson CIs (C2, CNV RF, WSI, late fusion; discovery, LGD2+); second panel MH OR high vs low per arm (two strata, from `round3_main.json` R4).
- F-D2: A probe AUROC per representation, pooled (item 6) vs discovery-only (K3); B UMAP (fit on each fold's training patients, held-out shown, five folds as small multiples) of image-only and intermediate embeddings coloured by stratum; C same UMAP coloured by label, discovery patients only.
- F-D3: A histograms of per-row Spearman (image-only vs intermediate; vs co-attention) from `attention_item7_rows.csv`; B top-5 % attention mass per model (from the attention arrays), uniform line at 0.05. Montage paths listed (cluster).
- F-D4: A scatter of cnv_only vs late_mean patient percentile within discovery, coloured by label, diagonal; B ΔAUROC bars (CNV destroyed vs image destroyed) per learned fusion model, discovery and pooled (K4).
- F-D5: later-HGD+ rate FP vs TN per stratum for late_mean, WSI, CNV (RF), C2, Wilson CIs, counts on bars (K1).
- F-D6: discovery-only boxplots FN vs TP (late fusion) for `kept_tiles`, cx, interval to endpoint, max grade so far; bar panel of endpoint type (second LGD / HGD / IMC) for FN and TP.

(Results follow in the results commit.)

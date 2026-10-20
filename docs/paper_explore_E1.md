# Exploration E1: error analysis of non-progressor false flags (20–21 October 2026)

Status: EXPLORATORY (shared rules: `paper/reviews_round7/decisions/EXPLORE_RULES.md`). Nothing here is confirmatory; everything tried is recorded.

## Plan

**Question.** Why do non-progressor (NP) endoscopies get flagged by R49 and by H&E alone (P1 at 90%), and can a rule derived from that reduce false flags without losing progressor patients?

1. **Characterise flags (E1.1).** For each repeat, classify pre-event endoscopies as false-positive NP (flagged NP), true-negative NP, true-positive progressor (flagged P) and false-negative progressor, under R49 and under P1 90%. Compare FP-NP against TN-NP and against TP-P on every covariate available: tissue tiles, background-tile share (R55 pixels), slide age at scan, scanner, sequencing batch and batch composition, biopsy year, grade (sheet and Barrett's database), samples per endoscopy, position in the patient's series, time to last endoscopy, p53, Prague length, age, sex, later database grade group, slide notes (z levels / marker), same-block status. Endoscopy class shares are averaged over the 10 repeats (an endoscopy contributes its share of repeats in each class). Effect sizes: difference in means (and in shares) with paired patient-bootstrap 95% CIs (2,000 draws, `RandomState(0)`).
2. **Inside the H&E score (E1.2).** The H&E model is an elastic-net logistic regression on the z-scored mean of the sample's UNI2-h tile embeddings, so the logit decomposes exactly into per-tile contributions c_t = w·z(e_t)/N (N = the sample's tiles). Coefficients are not stored, so the outer fits (`kv_cv.R`, cfg 02) and the inner fits (`hz_fit.R`, img) are refitted verbatim and checked against the stored predictions. Per sample: share of the score from background and edge tiles (per-tile pixel statistics at the stored tile positions, CPU jobs), from the top-k tiles, the Gini of positive contributions, the number of strongly positive tiles. Aggregates only; no images.
3. **Fixes (E1.3).** Candidate fixes built from whatever separates FP-NP from TP-P: (a) score adjustments (e.g. remove background-tile contributions, trimmed means of tile contributions); (b) vetoes on flagged endoscopies by tissue/background/concentration features; (c) a second-stage false-positive filter (logistic) trained on training patients' flagged endoscopies. Every threshold and model is fitted on the training patients of each outer fold (inner out-of-fold scores and inner-fit tile contributions) and scored on held-out patients. Reported against R49 and P1 90% on the same patients with paired bootstrap CIs; apparent (non-nested) versions labelled optimistic.

**Space.** Scripts `scripts/paper_plan/ex_e1_*`; aggregates `results/paper_final/explore_E1/`; figures `paper/figures_explore_E1/` (local); row-level `killcoyne_mm/explore_E1/` (cluster); Slurm prefix `exe1`.

---

## Results

(appended below as they come in)

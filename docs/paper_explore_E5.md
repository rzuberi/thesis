# Exploration E5: borrowing knowledge from ERIN

Started 20 October 2026 (exploration, not confirmatory; rules in `paper/reviews_round7/decisions/EXPLORE_RULES.md`).

## Plan (written before any result)

**Idea.** ERIN is a separate archive of about 7,900 routine oesophageal H&E slides (2022–2025) with section-level dysplasia grades from an LLM jury. A dysplasia model trained there knows what dysplasia looks like from far more slides than our cohort has. Its "dysplasia-likeness" score on our slides may help separate progressors from non-progressors, or tell which H&E flags are real.

**Prior evidence.**
- ISBI rerun, part 3: the ERIN arm-B LGD+ models scored SWG LGD-versus-NDBE at only 0.57.
- P32: an ERIN report-label grade head predicted SWG progression at 0.75 at patient level on the release cohort.
- So transfer is uncertain.

**Steps.**
1. **ERIN models.** Arm B of the ISBI rerun (own-section jury-v3 grade, ABMIL on UNI2-h tiles at 0.5 µm/px, GPU-resident, `train_fold.py` settings).
   - Retrained with every slide of the 70 ERIN patients also in the SWG cohort removed: the 55-ID list, the ISBI part-3 accession and Barrett's-DB bridges, and the closeout pairs file.
   - Tasks: LGD+ (primary), HGD+ and six-class.
   - 5 ERIN patient folds × 3 seeds; the 130 hand-labelled patients are never trained on (validation).
   - The existing leak-free P32 report-label grade head is scored alongside.
2. **Scoring our cohort.**
   - 460 of the 578 pre-event slides already have UNI2-h features from the same pipeline (`SWGCohort/features_uni2h_05um`; Hamamatsu level 1, 0.44 µm/px).
   - The other 118 are extracted with the same tiling in two phases: CPU tile crops, then GPU embedding.
   - Slide score = mean over models of the logit; sample score = max over its slides; endoscopy score = max over its samples.
3. **Uses**, all nested in the stored 10 × 10 patient-grouped folds (`killcoyne_mm`). ERIN models never see SWG labels, so only thresholds and stackers need nesting.
   - **(a) Alone:**
     - AUROC (sample-level fold-stratified, endoscopy and patient max);
     - P1-like rule "flag if max ERIN score ≥ t", with t at 80/90/95% training endoscopy sensitivity.
   - **(b) Stacked with L-IMG:**
     - per outer fold, a logistic regression of y on logit inner-OOF L-IMG and the ERIN logit, fitted on training patients' pre-event samples;
     - training-patient scores for thresholds are cross-fitted (5 patient-grouped folds inside training patients);
     - used (i) P1-style at 80/90/95%, (ii) in the R49 gate in place of L-IMG for banding (L-LATE unchanged), (iii) also in L-LATE = (L-CNV + stack) / 2.
   - **(c) Veto or confirmation inside R49:**
     - τ_q = the threshold keeping ≥ q of training progressor endoscopies' max ERIN score (q = 90/95/98%; **primary q = 95%**, fixed now);
     - c1: every R49 flag requires ERIN ≥ τ;
     - c2: only high-band (H&E-only) flags require it;
     - c3: high-band flags below τ are sent to the middle band (sequenced, CNV decides) instead of being dropped;
     - c4: low-band endoscopies whose ERIN score exceeds the 90%-specificity training cut-off are rescued into the middle band;
     - c5: P1 at 90% with the veto.
4. **Reporting.**
   - Against R49 and P1 at 90% on the same 571 samples / 75 patients: Δ NP patients flagged, Δ caught, Δ endoscopy specificity (matched where the rule is score-based), samples sequenced and AUROC.
   - Paired patient bootstrap, 2,000 draws, `RandomState(0)`.
   - Apparent (non-nested) versions are labelled optimistic.

**Primary per use:**
- (a) ERIN LGD+ max at 90%;
- (b) stack(L-IMG, ERIN LGD+) in P1 at 90%;
- (c) c1 at q = 95%.

Everything else is descriptive.

Scripts: `scripts/paper_plan/ex_e5_{prep,tiles,embed,train,score,eval}.py`, `ex_e5_gpu_submit.sh`. Slurm prefix `exe5`. Row-level outputs: `killcoyne_mm/explore_E5/` (cluster). Aggregates: `results/paper_final/explore_E5/`.

---

## Results

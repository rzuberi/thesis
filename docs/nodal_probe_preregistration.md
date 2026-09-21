# Pre-registration — nodal status from the pre-treatment OGD biopsy (OCCAMS)
Written 21 Sep 2026, before any result. Derived from `docs/oac_response_preregistration.md`; same cohort machinery.

**Question.** Does the diagnostic OGD biopsy slide carry information about lymph-node involvement?
**Primary label:** pathological node status at resection (`resection_path_nstage_rp_tnm7`), ypN1–3 vs ypN0, nx/missing excluded (≈82 vs 51 among OGD-slide cases). This is the ground truth but is measured after neoadjuvant therapy.
**Secondary label:** clinical pre-treatment node status (`nstage_..._pretreatment_staging_tnm7`), cN1–3 vs cN0 (≈96 vs 43) — the clinician's imaging estimate.
**Arms.** Histology: ABMIL on OGD tiles only (UNI2 primary; 4 other encoders exploratory). Clinical baseline: linear model on age, performance status, pre-treatment T/N/M — for ypN this INCLUDES cN, so the question becomes "does the biopsy add to what the clinician already estimates"; for cN the N column is removed (it is the label).
**Design.** Patient-disjoint 5-fold, 3 seeds, 1,000-bootstrap CI; 50 label-permutation shards for the UNI2 primary; tile-count confound reported. Leakage rule: no `_RES` and no non-H&E slide in any bag (asserted).
**Gate (primary).** AUC lower CI > 0.5 and point ≥ 0.60 for histology; otherwise NULL and no attention analysis.
**Interpretation rules.** Histology ≈ clinical-with-cN ⇒ biopsy adds nothing over staging; histology > chance but < clinical ⇒ weak signal, not clinically useful; both null ⇒ consistent with the response null (future course not visible in the biopsy).

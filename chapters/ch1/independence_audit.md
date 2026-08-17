# Cohort independence audit

Draft for Ch1. Every replication claim in this thesis depends on the cohorts being
genuinely independent, so the overlaps are quantified here rather than assumed.

The thesis uses three local cohorts (SWGCohort, ERIN, OCCAMS) and one public cohort
(TCGA). I checked each pair that could plausibly share patients.

**ERIN and SWGCohort.** Both are Barrett's surveillance populations from overlapping
catchment areas, so patient overlap was a real risk. Matching anonymised patient
identifiers across the two cohorts found 6 shared patients out of 1,992 checked
(0.3%). The six are excluded from any experiment in which one cohort validates a
model trained on the other. ERIN is therefore treated as an external cohort for
Chapter 3, with the caveat that both cohorts sit in the same national surveillance
pathway and share grading conventions; transfer between them tests new patients and
new laboratories, not a new healthcare system.

**OCCAMS and ICGC ESAD-UK.** These are the same patients. OCCAMS contributed the UK
oesophageal adenocarcinoma cohort to ICGC under the ESAD label, and several public
resources (including cBioPortal studies derived from ICGC releases) repackage it.
No ICGC ESAD data or derivative is used for external validation anywhere in this
thesis. This exclusion is recorded here because the overlap is not obvious from the
dataset names, and a validation built on it would be circular.

**TCGA.** TCGA-ESCA patients were recruited at North American and Eastern European
sites and cannot overlap with the UK cohorts. TCGA is the only cohort in the thesis
collected outside the UK, which makes it the strongest external test and also the
most confounded one: scanner hardware, fixation protocols, staging era, and
treatment patterns all differ from the local cohorts at once. Chapter 2 uses it as
a replication cohort with those caveats stated.

**DFCI/Broad OAC (Dulak et al., 2013).** Considered as an additional genomics-only
sanity check. It is a US cohort and presumed independent of OCCAMS, but it has no
usable whole-slide images, so it plays no role in the histology-anchored analyses.

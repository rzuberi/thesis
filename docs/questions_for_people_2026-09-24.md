# Questions that need a person, 24 September 2026

Items from the post-talk list that no file or computation can answer. Each is written so it can be
pasted into an email. Items marked (T) were flagged as needed before the talk is reused.

## For Leanne (SWG / ACE-B cohort owner)

**Q4 (T). Who produced the SWG grades used as our pathologist anchor?**
The spreadsheet `sWGS_777_samples_cleaned_202401_Leanne_fullDetails.xlsx` carries a `Pathology` code
(BE / ID / LGD / HGD / IMC) per Path ID. We have compared our LLM jury against it as a "pathologist anchor"
(two-tier agreement 0.82, weighted kappa 0.61 on 627 specimens). Was that code (a) a research
pathologist's re-read of the block, (b) transcribed from the clinical report, or (c) your own coding?
If (b), our anchor is partly circular and we must say so; if (a), please tell us who read them and
whether a second reader was involved.

**Q7. Were SWG non-progressors selected to match progressors?**
The release has 50 progressor and 100 non-progressor patients. Were the 100 chosen by any matching rule
(age, segment length, surveillance duration, biopsy count) or are they a consecutive/available sample?
This decides whether our case-control AUROCs can be quoted as population figures.

**Q8. Does SWG overlap with the Killcoyne et al. 2020 (Nature Medicine) cohort?**
Our CNV pipeline is the Killcoyne 2020 one (0.4x, 50 kb). Are the 150 patients (or any of them) the same
patients as in that paper's discovery or validation sets? If yes, which, so we can state that our CNV arm
is not an independent replication of that work.

**Q11. ACE-B samples: 294 versus 234.**
You quoted 134 patients and 294 sWGS samples. The workbook we hold (`ACEB_samples_for Rehan.xlsx`) has
234 sample rows (233 distinct names, 101 distinct PS accession bases). Is 294 the sequenced total and 234
the DNA-extraction sheet that was shared, or are 60 samples missing from what we received? A one-line
reconciliation is enough; we will quote your numbers as the cohort and ours as the linkage-limited subset.

**Q2 (T). Sequencing depth and any resequencing of SWG.**
Our records say SWG is 0.4x / 50 kb (your 6 March 2026 slide "Sequencing depth 0.4x, Bin size 50kb")
and ACE-B about 7x. We have no record of any SWG resequencing at 4x or any other depth. Does deeper
SWG data exist anywhere? If yes, where, and at what depth, because item 22 of our list (rerun the CNV
arm and all fusions on deeper data) depends on it.

## For the data owner of the ERIN reports

**Q5 (T). Permission to show one de-identified report on screen.**
For a lab talk we would like to show one oesophageal biopsy report with dates, lab numbers, years and
clinician names replaced by tokens, alongside the eight LLM grades it received. The file exists only on
the CRUK CI cluster and Rehan's institute laptop. Is this permitted within the current data agreement,
and does it need any further redaction (e.g. free-text macroscopic measurements)?

**Q9. How were the ERIN reports selected, and what does ERIN stand for?**
The export holds 7,149 histopathology reports from 2,537 patients (2014 to 2025) with 6,654 reports under
the "OESOPHAGUS" specimen protocol, 490 under "OESOPHAGUS, PART/TOT RESECTION" and 5 others. We need,
for the thesis methods: (a) the selection criterion used for the pull (specimen site code, diagnosis
text, patient list, or other), (b) whether resections were intended to be included, (c) the expansion
of the acronym ERIN, and (d) the export date and the system it came from.

## For the CRUK CI histopathology core

**Q12. ACE-B scanning: completion date and scanner.**
Which scanner (model and objective) is being used for the ACE-B blocks, is it the same for the 44 ECI
and the 250 Wales blocks, at what nominal magnification and pixel size, and when do you expect the last
slide to be scanned? Also: do the exported files carry a pixel-size (mpp) tag, because none of the ERIN
files do and our pipeline currently assumes 0.25 um/px.

Second request, same team: **7 ERIN slide files in case `58beb6fd-5838-4f57-b923-c6278bd37f15` are
unreadable** (24 KB to 105 MB, not decodable by OpenSlide or PIL) and need re-exporting or rescanning.

## For a pathologist (any of the lab's clinical collaborators)

**Q20. Interpretability sanity check.** Eleven SWG attention/risk maps are in `review/swg_heatmaps/`
(pseudonymous IDs in filenames). We need a pathologist to look at each and answer two questions per
slide: does the high-attention region sit on epithelium rather than stroma or artefact, and does the
tile-risk pattern make sense for the recorded grade? A checklist is in
`docs/interpretability_checklist_2026-09-24.md`.

**Q27. Pathologist time for the 100-case grading key.** The grading app is live again at
`http://clust1-sub-1.cri.camres.org:8471` (CRI network); the passphrase is in `hand_grading/README.txt`
on the cluster. A grader takes 20 common cases plus 20 unique cases; about 90 minutes per grader.

## Literature figure to quote (Q10)

- Non-dysplastic Barrett's, adenocarcinoma incidence: **0.33 per 100 person-years** (95% CI 0.28 to 0.38),
  Desai et al., Gut 2012, meta-analysis of 57 studies.
  Source: https://pubmed.ncbi.nlm.nih.gov/21997553/
- Confirmed low-grade dysplasia after expert panel review: **9.1% per year** to HGD or adenocarcinoma,
  against **0.6% per year** for LGD downstaged to non-dysplastic; 73% of community LGD diagnoses were
  downstaged. Duits et al., Gut 2015. Source: https://pubmed.ncbi.nlm.nih.gov/25034523/
- Use: our ERIN "first LGD" downgrade rate at the next visit is 64%, in the same range as the 73%
  downstaging figure, which supports treating a single LGD call as a noisy label.

# The replication ceiling for Barrett's progression

Draft for Ch1 (also cited in Ch3). States why Chapter 3's replication uses two
cohorts rather than three, with evidence that two is the current maximum.

Chapter 2 can replicate on public data because established oesophageal
adenocarcinoma is represented in TCGA: 88 adenocarcinomas with whole-slide images,
matched genomics, and survival endpoints. No equivalent exists for Barrett's
progression. I audited the open-access landscape in August 2026 to establish this
rather than assert it:

- TCGA contains no Barrett's oesophagus cases. Its ESCA cohort is resected
  carcinoma only.
- The Human Tumor Atlas Network's first-phase release (2,042 participants, 8,425
  biospecimens) includes pre-cancer atlases for colorectal, breast, and lung
  lesions, but no Barrett's atlas, and its assays are single-cell and spatial
  rather than diagnostic H&E.
- The Cancer Imaging Archive hosts no Barrett's histopathology collection. Its
  oesophageal holdings are radiology.
- Public capsule-sponge datasets from the Cambridge trials (BEST2/BEST3, DELTA)
  sample a different specimen type — pan-oesophageal cytology sponges, not targeted
  endoscopic biopsies — and so test a different clinical question.

The consequence: any histology model for Barrett's progression can currently be
externally validated only on privately held biopsy cohorts. Within that constraint,
ERIN is a strong external test for SWGCohort-trained models: 16 times more patients
(2,446 graded versus 150), a different laboratory, six patients of overlap (see the
independence audit), and the full grade spectrum from non-dysplastic Barrett's to
adenocarcinoma. Two cohorts is not a design compromise; it is the ceiling the field
imposes, and this section documents that the ceiling was checked.

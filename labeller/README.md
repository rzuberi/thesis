# pathladder

Schema-driven weak labels from GI pathology report free text. One extraction
engine (sentence splitting, windowed negation, worst-finding-wins for ordinal
fields); each cohort is a schema, not a fork.

Built for this thesis's Chapter 4: can free-text reports substitute for expert
labels when training and evaluating histology models?

## Install and use

```bash
pip install -e .
pathladder --schema tcga_gi --input reports.csv --text-col text --id-col barcode --out labels.csv
```

Or in python: `from pathladder import label_report, BARRETTS_LADDER`.

## Schemas

- `barretts_ladder` — Barrett's surveillance grade: NDBE < IND < LGD < HGD < CANCER
  (highest matched rung wins, negation-aware).
- `tcga_gi` — GI resection reports: histologic_type, grade (G1–G3), site.

## Validation (TCGA ESCA+STAD reports, n=507, August 2026)

| Field | Coverage | Accuracy | Truth source | n compared |
|---|---|---|---|---|
| histologic_type | 98% | 100% | GDC disease coding | 464 |
| grade | 77% | 96.5% | cBioPortal clinical record | 375 |

Prognostic check: report-derived G3 vs G1/G2 gives Cox HR 1.50 (95% CI 1.09–2.05,
log-rank p=0.011) for overall survival, versus HR 1.48 (1.11–1.98, p=0.007) using
the clinically recorded grade on the same patients (`run_tcga_grade_prognosis.py`).

Reproduce: `run_tcga_validation.py` (needs `data/TCGA_Reports.csv.zip` +
`manifests/TCGA_multimodal_manifest.csv`), then `run_tcga_grade_prognosis.py`
(needs `data/TCGA-CDR.xlsx`).

## ERIN application (cluster)

`run_erin_validation.py` applies `barretts_ladder` to the ERIN pathology reports
and scores them against the manually graded subset. Paths are cluster-side; see
the script header.

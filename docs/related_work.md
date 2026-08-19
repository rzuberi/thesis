# Related work and reuse decisions (2026-08-18)

What exists, what we reuse, what we position against. Links checked August 2026.

## Reuse directly

| Project | What it is | How we use it |
|---|---|---|
| [Trident + Patho-Bench](https://github.com/mahmoodlab/patho-bench) | WSI processing with most FMs supported; benchmark harness (linear probe, Cox, finetune) with GPU load-balancing | Adopt Trident for remaining/extra-encoder feature extraction; pattern the encoder sweep on Patho-Bench task specs |
| [PORPOISE](https://github.com/mahmoodlab/PORPOISE) (Cancer Cell 2022) | Pan-cancer WSI+molecular fusion, 14 TCGA types, code | Run as comparison arm on OCCAMS + TCGA-OAC (Ch2); cite their TCGA numbers |
| [SurvPath](https://faisal.ai/research/) (CVPR 2024), [PathOmics](https://github.com/Cassie07/PathOmics) (MICCAI 2023) | Newer pathway/genomics x histology transformers, code | Candidate intermediate-fusion arms instead of bespoke architecture |

## Findings we build on (cite, don't re-derive)

- [PathBench](https://arxiv.org/abs/2505.20202), [eva](https://openreview.net/pdf?id=FNBQOPj18N): no encoder wins consistently across tasks
  -> justifies the encoder-sensitivity axis in the sweep pre-registration.
- [FMs unrobust to medical-centre differences](https://arxiv.org/pdf/2501.18055)
  -> published support for the cross-cohort transfer framing; reusable robustness metrics.
- [Campanella, Nat Med 2019](https://www.nature.com/articles/s41591-019-0508-1): 44,732 WSIs
  trained on report-derived diagnoses only, AUC>0.98 -> the precedent for Ch4;
  our delta = validated auditable extractor + cross-cohort replication.
- [TCGA-Reports](https://www.cell.com/patterns/fulltext/S2666-3899(24)00024-2) ships LLM
  extraction benchmarks on the same corpus -> ready-made pathladder-vs-LLM comparison.

## Position against

- [TissueCypher](https://pmc.ncbi.nlm.nih.gov/articles/PMC10684217/) (Castle Biosciences;
  [meta-analysis](https://clpmag.com/diagnostic-technologies/anatomic-pathology/meta-analysis-validates-tissuecypher-test-barretts-esophagus-risk-assessment/)):
  commercial, AGA-endorsed BE progression test (multiplex IF + classifier; 5-yr risk
  tiers 8.1%/15.3% in an 8,000-patient real-world cohort). The clinical benchmark for
  Ch2/Ch3 framing: bespoke assay vs our routine-H&E + second-modality question.
- [Weakly supervised BE screening, Nat Comms 2024](https://www.nature.com/articles/s41467-024-46174-2):
  closest neighbour to Ch3xCh4 — read before freezing the ERIN design; reuse their MIL
  setup where it fits, state the differences (progression vs screening; report-labels
  validated against expert grades; two-cohort replication).
- [Killcoyne et al. 2020]: sWGS CNV progression baseline — already reproduced; SWG arm
  extends it with histology fusion.

## Watch-outs

- PORPOISE/SurvPath validated at TCGA scale; transfer to n=141 OCCAMS is itself a
  finding either way — fits the replication frame.
- TissueCypher uses a different specimen workflow (multiplex IF); comparisons are
  positioning, not head-to-head benchmarks.

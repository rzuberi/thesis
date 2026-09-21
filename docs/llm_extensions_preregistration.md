# Pre-registration — three LLM extensions (21 Sep 2026, before any result)

## A. Human-grade anchors for the jury and MedGemma
Two human grade sets exist inside the Barrett's database scrape. (1) 658 specimen-level report/biopsy pairs matched to the SWG release **pathologist grade** (`specimen_pairs.parquet`; BE 449, LGD 88, ID 76, HGD 23, IMC 22). (2) 153 ACE-B cases with a Seattle-protocol histology grade at trial entry, linked to 125 DB participants.
Runs: MedGemma-27B with the per-specimen prompt on the 658 (jurors already run); MedGemma-27B on the full 13,645-report corpus (jurors already run). Analysis (`scripts/task_anchor_eval.py`): exact and two-tier (NDBE/IND vs LGD+) agreement and quadratic-weighted kappa against the pathologist grade for the jury consensus, each juror and MedGemma; for ACE-B, the grade of the report nearest the trial date vs the Seattle grade.
Interpretation rule: the paper reports whatever these give; a two-tier agreement below the TCGA level (0.96) is expected because specimen-level text is harder, and will be stated as such.

## B. Image-only zero-shot grading pilot (100 ERIN slides)
Slides: 100 dual-labelled ERIN slides stratified by section grade. Tiles: 8 per slide with highest attention under the section-trained six-class MIL (`erin_tilemaps/output/mcmil_section.pt`), extracted at 20x/224 px and upscaled. Models: MedGemma-4B and MedGemma-27B (both vision-capable via ollama) with a fixed prompt returning one of NDBE/IND/LGD/HGD/CANCER per tile; CONCH zero-shot with class prompts if the package installs. Slide score = max tile grade (ordinal) and mean P(LGD+). Truth = the slide's section grade.
Gate: binary AUROC (LGD+) ≥ 0.70 on the pilot to justify a full run; below that the result is reported as a negative and no further image-LLM work is done. Reference points: trained slide–report VLM 0.889, supervised MIL 0.926.

## C. Zero-shot prognosis from text and from CNV-as-text
C1 text: ERIN progression cohort v3 (1,266 patients, 181 progressors). Input = all reports dated on/before the index date (NOTHING later), concatenated with dates; prompt asks for probability (0–100) of HGD/cancer within 5 years. Models: MedGemma-27B, qwen3-32B, gemma3-27B. Metric: AUROC vs `progressed_to_HGDplus`, bootstrap CI; baseline = index grade alone. Prediction (stated in advance): LLM AUROC ≈ grade-only baseline (~0.65–0.70).
C2 CNV-as-text: SWG release, 707 samples. Input = chromosome-arm relative copy-number values serialised as gains/losses (|z| > 1 listed with magnitude) plus complexity score; prompt asks for progression risk 0–100. Models: MedGemma-27B, qwen3-32B. Metric: patient-level (max) and sample-level AUROC vs the release endpoint; reference CNV-only model 0.663 (patient), 0.620 (sample). Prediction: LLM below the trained linear model; the interesting outcome is if it is not.
All runs zero-shot, no fine-tuning, on-cluster only; report text never leaves the institute.

# Interpretability sanity check, SWG heat-maps (item 20)

Files: `review/swg_heatmaps/*.png` on Rehan's laptop (11 slides, pseudonymous DB sample ids in the
filename, `_y1` = progressor sample, `_y0` = non-progressor). Numbers behind each panel are in
`results/numbers/swg_heatmaps.json` (attention share of the top 10% tiles, tile-risk share, slide
probability per model: image-only, intermediate, co-attention, early fusion).

Cases selected (see `scripts/task_swg_heatmaps.py`): the five progressor samples already interpreted in the
Chapter 1 case packs (`why = prior`), the three progressor samples the late-mean model scored highest,
the two it scored lowest (missed), and the top false positives among non-progressors.

| file | y | what to check |
|---|---|---|
| 96_AHM0363_y1.png | progressor | |
| 153_PR1-WSH-030_y0.png | non-progressor | |
| 196_PR1-ADH-069_y1.png | progressor | |
| 396_AD0496_y1.png | progressor | |
| 423_AD0496_y1.png | progressor (same patient as 396) | |
| 533_AD0425_y1.png | progressor | |
| 552_AHM1146_y1.png | progressor | |
| 557_PR1-WSH-081_y1.png | progressor | |
| 702_PR1-HIN-044_y1.png | progressor | |
| 712_PR1-HIN-043_y1.png | progressor | |
| 746_AHM1807_y0.png | non-progressor | |

For each slide, answer:

1. **Tissue targeting.** Is the high-attention region on Barrett's glandular epithelium? (yes / partly /
   no: stroma, squamous, fold artefact, ink, out-of-focus)
2. **Grade plausibility.** Given the recorded grade, does the tile-risk pattern make sense (risk
   concentrated on the most atypical glands)? (yes / no / cannot tell at this resolution)
3. **Model agreement.** Where image-only and co-attention disagree on the slide probability, which map
   looks more like where a pathologist would look?
4. **Anything the model should not be using.** Cautery, crush, tangential sectioning, pen marks.

Return the table with one line per slide. Twenty minutes is enough; this is a plausibility check, not a
grading exercise.

# Two papers, agent P2C: early cost-consequence analysis for Paper 2

Written 21 October 2026. Replaces the "£1,362 → £1,067" line (round-8 cost model: £85 per sample, £535 per flagged endoscopy, no comparator, no horizon, no H&E costs).

## Plan

1. Reuse E9. Pull **paired** patient-bootstrap draws of each rule's class-specific per-patient rates at operating target D from the cluster: sens, fpr, samples sequenced, flagged endoscopies, endoscopies. Add the unions with the pathologist read and the sequence-everything comparator (`tp_p2c_draws.py`). No rule is re-implemented. E9 is executed unchanged and its stored sweeps are read.
2. Build a 10-year, per-1,000, prevalence-reweighted cost-consequence model locally from these aggregates (`tp_p2c_cost.py`). Cost every band action with 2023/24 NHS unit costs and add the de-escalation arm. Propagate uncertainty by pairing each bootstrap draw with one PSA draw of every cost, transition and utility.
3. Break-even sequencing price, break-even flag cost and missed-progressor threshold per tier; two-way plot; efficiency frontier; budget impact; the allowed cost sentence.

Files:
- scripts: `scripts/paper_plan/tp_p2c_draws.py` (cluster), `scripts/paper_plan/tp_p2c_cost.py` (local)
- aggregates: `results/paper_final/two_papers_P2C/rate_draws.json` (2,000 paired draws of cohort-level rates, no identifiers) and `cost_consequence.json`
- figures (local only): `paper/two_papers/figs_P2C/fig_p2c_twoway.png`, `fig_p2c_frontier.png`

## Smoke and reproduction

The first draws run (20 draws) reproduced every E9 stored rate exactly:

| Rule | Reproduced |
|---|---|
| Grade or p53 | sens 0.656, fpr 0.581 |
| Mean-logit + memory | 31.0 caught / 26.6 NP |
| Mean-logit full stack | 30.3 / 16.2, 3.12 samples per patient |
| Final rule | 30.5 / 17.2 |
| R49 | 31.1 / 31.8 |
| R49 or grade/p53 | sens 0.978, fpr 0.835 |
| Final rule or grade/p53 | sens 0.969, fpr 0.714 |

The new sequence-everything sweep reproduced round 9's nested rows:
- max L-LATE, threshold only: 30.9 / 29.1 (row 25);
- with EW memory: 31.0 / 24.6 (row 7);
- 7.61 samples per patient.

LGD-or-p53 ever (the override) gave 19/32 and 17/43, as E9's `g53_lgd`. The full run used 2,000 draws, `RandomState(0)`, so it is paired with E9.

## Model (CHEERS 2022 items in brief)

| Item | Choice |
|---|---|
| Design | Early cost-consequence model with threshold analyses (NICE early value assessment style). Decision tree over a 10-year horizon; patients' flag status is taken from the cohort's held-out "ever flagged" rates. |
| Population | 1,000 patients non-dysplastic on expert read, already in surveillance. 10-year progression to HGD/OAC of 1.5%, 3% (base), 5% and 10%, by reweighting class-specific held-out rates. The cohort's non-progressors had 4.65 endoscopies over 6.6 years, close to the 4 guideline endoscopies in 10 years, so ever-flagged rates are used as 10-year rates. |
| Perspective, currency | NHS England; GBP 2023/24 |
| Discounting | 3.5% for costs and QALYs |
| Comparators | **Current care**: grade ± p53, guideline interval of 3 years for everyone (endoscopies at 0, 3, 6, 9). **No-sequencing tier**: mean-logit + memory. **Light tier**: mean-logit gate + memory + certificate, 1.43 samples per patient. **Confirmatory tier**: mean-logit full stack, 3.12. **Sequence everything**: max L-LATE of every sample. Supplement rows: the stored-score variants of light and confirmatory, sequence-everything with memory, and pathology-guided de-escalation without AI (not guideline practice; a reference point only). |
| Band actions (PAPER2_plan_v2) | See the band table below. |
| Archive back-scan | Base case: the prior endoscopy's slides are retrieved and scanned at entry, so two consecutive looks exist at year 0. Scenario: no archive, so de-escalation starts after the second prospective low (endoscopies at 0, 3, 8). |
| Harm of a missed progressor | A de-escalated progressor has HGD onset uniform within the interval. The two-step chain HGD → early OAC → late OAC uses 0.119/y and 0.8/y (Swart 2021 via HTW EAR069). P(late at detection) is 0.115 at 3 years and 0.207 at 5 years, an excess of 0.092. Late vs early: +£7,082 cost (late £17,499, early endotherapy £10,416) and −7.24 QALYs. Value per de-escalated progressor at £20k/QALY, discounted: **£11,827** (PSA 95% £8,773–£14,967). The flag work-up is given no clinical benefit in the base case (conservative for the AI tiers); scenario: it halves late-stage risk in AI-flagged progressors. |
| Uncertainty | 2,000 iterations. Each pairs one patient-bootstrap draw of all rules' rates with one draw of every parameter: gamma with SE 10% for NHS unit costs; log-normal or uniform ranges for assumptions; beta for probabilities and utilities. |

Band actions:

| Band | Action and cost |
|---|---|
| Never flagged by the AI rule's pre-check, and no LGD or p53 aberrant ever | De-escalated one step (3 → 5 y; endoscopies at 0, 5) |
| AI flag on an endoscopy not already IND/LGD/p53 | Expert pathology review + p53 + specialist outpatient review + expert-centre endoscopy at the guideline interval (premium 25% of FE21Z). £492 per flagged endoscopy (base). |
| IND/LGD/p53 aberrant (current care, same in every arm) | Expert review + 6-month repeat endoscopy (£845) |
| Middle band (light, confirmatory tiers) | The top sample(s) are sequenced at the price per sample × (1 + 5% failure repeat) |
| Flag cancelled by the quiet-genome check | Guideline interval, never extended. The confirmatory tier therefore de-escalates exactly the light tier's patients; its only gain is fewer work-ups. |

AI read cost for every AI arm:
- £5 per slide (scan, storage, QA) at 2.05 slides per endoscopy;
- £10 per endoscopy for the licence and sign-off;
- £10 per archived slide back-scanned.

Sequencing is scaled to guideline endoscopies, which is conservative. Sequence-everything is scaled to the endoscopies actually performed.

## Sources (unit costs and inputs)

| Input | Value | Source |
|---|---|---|
| Upper GI endoscopy with biopsy (FE21Z), day case | £745 | National Cost Collection 2023/24 (NHS England 2024), as tabulated in Health Technology Wales EAR069 *Capsule sponge devices…*, Oct 2025, table A10 |
| FE21Z/FE22Z weighted (scenario) | £713 | same, scenario 6 |
| EMR (FE02A–C, day case) | £1,219 | NCC 2023/24 via HTW EAR069 |
| RFA (FE01Z, day case), 3.5 sessions per patient | £1,493 | NCC 2023/24 via HTW EAR069; sessions from Shaheen 2009 |
| Post-endotherapy surveillance | 4 + 2 endoscopies over 2 years | HTW EAR069 (expert opinion) |
| Oesophagectomy (FF02A–C) | £6,363 | NCC 2023/24 via HTW EAR069. The HTW text quotes £11,224; the table value is used. |
| Outpatient follow-up (WF01A) | £181 | NCC 2023/24 via HTW EAR069 |
| Chemotherapy (1 y) | £3,966 | Swart 2021 / NICE NG83, inflated (HTW EAR069) |
| Palliative RFA | £4,506 | same |
| Palliative stent (FE10A–D) | £4,808 | same |
| Palliative care, final year | £8,760 | same |
| Late OAC: 50% suitable for surgery; post-surgery 5-y survival 25% | as stated | Sami 2021; Øvrebø 2012 (HTW EAR069) |
| Utilities | NDBE 0.91; late OAC 0.675; surgery year 0.731; after surgery 0.836 | Benaglia 2013, Sami 2021 (HTW EAR069) |
| Age-related utility multiplier | 0.80 | Hernández Alava 2022, NICE DSU |
| Remaining life expectancy at about age 70 | 15.5 y | ONS national life tables, approximate |
| Histopathology per biopsy (context only; included in FE21Z here) | £82 (2017 GBP) | NBI vs HD-WLE cost-consequence model, PMC6415878 (UCLH / Plymouth / South Devon trust data) |
| Expert second pathology review | £100 (range £44–200) | assumption; £44 = round-7d NHS histopathology proxy |
| p53 IHC per block | £25 (£15–50) | assumption |
| Expert-centre endoscopy premium | 25% of FE21Z (0–50%) | assumption |
| Scan + storage + QA per slide | £5 (£1–15) | Ardon 2023 *J Pathol Inform* 14:100318 (MSKCC): $0.55–19.53 per scan, $0.79–0.92 staff per slide; storage about 1–1.2 GB per slide (NHS Scotland digital pathology presentation; cloud $0.01–0.07 per GB-year) |
| AI licence and sign-off per endoscopy | £10 (£2–30) | assumption. A vendor figure of about £1 per slide plus about £15,000 integration for Paige Prostate is unverified. |
| Scanner capital (services without one) | over £100,000 | vendor guidance (NHS Scotland digital pathology material). Budget-impact note only. |
| sWGS price per sample | £85 / £250 / £400 | £85 = research marginal price (round 8). sWGS for Barrett's is not in the National Genomic Test Directory. £250–400 is the reviewer's accredited-GLH range (extraction, QC failures, bioinformatics, reporting). Method: QDNAseq (Scheinin 2014 *Genome Res*). |
| sWGS failure → repeat | 5% (2–15%) | assumption |
| Surveillance interval | 3 y (BSG 2014 / NICE NG231: 2–3 y long segment, 3–5 y short); de-escalation one step to 5 y | BSG 2014; NICE NG231 (2023); HTW EAR069 base case |
| Context on the value of surveillance | 2-yearly surveillance vs at-need: no stage or survival difference; ICER about $115,563 per QALY | BOSS: Old et al., *Gastroenterology* 2025; Deidda et al., *Gastroenterology* 2025;169:1244–1252 |
| Barrett's surveillance population | about 2,500 per million (range 1,500–4,000) | UK primary-care incidence of diagnosed BO 15.6–85.6 per 100,000 PY at ages 40–74 (Masclee et al. 2014, UK and Netherlands databases), × about 11–12 years in surveillance. This is an assumption, and the doc flags it as the weakest input. |
| England population, ICBs, Cancer Alliances | 57.7 m; 42 ICBs (about 1.37 m each); 21 Cancer Alliances (about 2.75 m each) | ONS mid-2023; NHS England |

## Results (3% 10-year progression, sequencing £250 per sample, base case)

Per 1,000 patients over 10 years. Value is at the observed held-out rates; brackets are 95% PSA intervals. Costs are discounted. "Missed" = progressors de-escalated to a longer interval. For current care, "not flagged" (10.3) is shown separately: those patients stay on guideline surveillance.

| | Current care | No sequencing | Light | Confirmatory | Sequence everything |
|---|---|---|---|---|---|
| Slides scanned | 0 | 9,220 | 8,774 | 8,774 | 9,276 |
| Samples sequenced | 0 | 0 | 1,615 [1,364, 1,846] | 2,474 [2,031, 2,954] | 7,200 [6,143, 8,390] |
| Surveillance endoscopies | 4,000 | 3,498 [3,269, 3,700] | 3,280 [3,035, 3,517] | 3,280 [3,035, 3,517] | 3,525 [3,293, 3,734] |
| NP flagged by the strategy (of 970) | 564 [419, 698] (grade/p53) | 600 [480, 715] | 453 [337, 570] | 365 [248, 483] | 656 [537, 765] |
| AI work-ups (flagged endoscopies not already IND/LGD/p53) | 0 | 1,201 | 650 | 403 | 1,095 |
| NP de-escalated | 0 | 250 [149, 364] | 359 [240, 480] | 359 [240, 480] | 237 [132, 353] |
| Progressors flagged (rule or grade/p53, of 30) | 19.7 [14.5, 24.7] | 29.2 [28.0, 30.0] | 28.6 [27.1, 29.7] | 28.6 [27.1, 29.7] | 29.3 [27.8, 30.0] |
| Progressors missed (de-escalated) | 0 (10.3 not flagged) | 0.8 [0.0, 2.0] | 1.4 [0.3, 2.9] | 1.4 [0.3, 2.9] | 0.7 [0.0, 2.2] |
| Excess late-stage OAC | 0 | 0.08 | 0.13 | 0.13 | 0.06 |
| Incremental cost vs current care | — | **+£302k** [−13k, +636k] | **+£300k** [+44k, +600k] | **+£389k** [+138k, +699k] | **+£1.92m** [+1.51m, +2.47m] |
| at £85 per sample | — | +£302k | +£59k [−196k, +333k] | +£20k [−208k, +269k] | +£833k |
| at £400 per sample | — | +£302k | +£519k | +£725k | +£2.90m |
| P(saves) at £250 | — | 0.04 | 0.02 | <0.01 | 0 |
| Incremental QALYs | — | −0.5 | −0.8 | −0.8 | −0.4 |

Per patient, the confirmatory tier at £250 per sample costs about £389 more than current care over 10 years. The no-sequencing tier costs about £302 more.

**Why every AI tier costs more than current care.** The money is in de-escalation, but under the agreed actions two things cap it:
1. The pathologist read overrides the rule, so only patients never flagged by the AI pre-check and never LGD/p53-aberrant are de-escalated: 250–359 of 970 non-progressors.
2. Every high-band AI flag triggers an expert work-up. That costs more than the endoscopies saved: £510k of work-ups for the no-sequencing tier against about 500 endoscopies avoided.

Sequencing earns its keep by cancelling work-ups, not by de-escalating more patients. The quiet-genome check cannot extend intervals under the band table. That is why the confirmatory tier beats the no-sequencing tier only below about £210 per sample.

**Across prevalence (incremental cost vs current care at £250 per sample; misses per 1,000):**

| Progression | No sequencing | Light | Confirmatory | Sequence everything | Missed (no seq / light, conf / seq all) |
|---|---|---|---|---|---|
| 1.5% | +£292k | +£287k | +£366k | +£1.91m | 0.4 / 0.7 / 0.3 |
| 3% | +£302k | +£300k | +£389k | +£1.92m | 0.8 / 1.4 / 0.7 |
| 5% | +£316k | +£317k | +£420k | +£1.93m | 1.4 / 2.3 / 1.1 |
| 10% | +£350k | +£358k | +£498k | +£1.96m | 2.8 / 4.7 / 2.2 |

Non-progressors de-escalated barely move with prevalence (no sequencing 254 → 232; light and confirmatory 364 → 333).

### Break-even (3%; 95% PSA intervals)

| Strategy | vs | Break-even £ per sample (cost only) | Same, NMB at £20k/QALY | Same, flag once per patient | Break-even flag cost at £85 per sample | at £250 | at £400 |
|---|---|---|---|---|---|---|---|
| No sequencing | current care | no sequencing | — | saves at any price (−£97k) | **≤ £201** [40, 425] per flagged endoscopy | same | same |
| Light | current care | **≤ £45** [−131, 218] | ≤ £34 | ≤ £178 [41, 322] | ≤ £388 [52, 910] | not cost-neutral at any flag cost | not cost-neutral |
| Confirmatory | current care | **≤ £76** [−27, 185] | ≤ £69 | ≤ £127 [37, 230] | ≤ £435 [−125, 1,284] | not cost-neutral at any flag cost | not cost-neutral |
| Sequence everything | current care | never (< £0) | never | ≤ £11 | never | never | never |
| Light | no sequencing | **≤ £251** [142, 374] | ≤ £247 | ≤ £112 | — | **≥ £488** [277, 928] | ≥ £949 |
| Confirmatory | no sequencing | **≤ £211** [120, 315] | ≤ £208 | ≤ £84 | ≥ £83 | **≥ £619** [414, 1,004] | ≥ £1,107 |
| Sequence everything | no sequencing | ≤ £4 | ≤ £5 | never | — | about £18,000 (never in practice) | — |

How to read the flag-cost columns:
- Versus current care, AI flags are added on top of the pathologist read, so a tier is cost-neutral when a work-up costs **at most** the stated amount.
- Versus the no-sequencing tier, sequencing removes work-ups, so the sequencing tier pays off when a work-up costs **at least** the stated amount.

The break-even prices change little with prevalence:
- confirmatory vs current care: £84 at 1.5%, £67 at 5%, £44 at 10%;
- confirmatory vs no sequencing: £216 at 1.5%, £204 at 5%, £189 at 10%.

### Cost of a missed progressor

At the base flag cost and £250 per sample, **no AI tier is preferred to current care at any value of a missed progressor ≥ £0**: each costs more before any harm is counted.
- The modelled value per de-escalated progressor is £11.8k (£8.8–15.0k). It moves incremental costs by under £20k per 1,000, so it never decides the comparison.
- Against the no-sequencing tier:
  - The light tier is preferred only while a de-escalated progressor is valued below about £4,200. At the modelled £11.8k, it is preferred in 39% of iterations: the two are equivalent.
  - The confirmatory tier is preferred in 17% of iterations.
- **Pathology-guided de-escalation without AI** (extend everyone never LGD/p53-aberrant) is a reference point, not a recommendation:
  - It saves £710k [497k, 938k] per 1,000.
  - It de-escalates 12.2 [7.0, 17.3] progressors (1.1 excess late cancers).
  - It stays preferred to current care until a de-escalated progressor is worth £58.8k [35k, 109k].
- Relative to that reference, the AI tiers avoid about 1 late cancer per 1,000 at about £158k (no sequencing; 95% £87k–321k) to £181k (confirmatory) per QALY. That is above NICE's £20–30k threshold.
- This is the honest economic picture: once intervals may be lengthened, the AI's value is safety (keeping 11 of 12 progressors on surveillance), and the model prices that safety above NICE thresholds. BOSS (2025) points the same way for surveillance in general.

### Scenarios (3%, £250 per sample; incremental cost vs current care, £k per 1,000)

| Scenario | No sequencing | Light | Confirmatory | Pathology-only de-escalation |
|---|---|---|---|---|
| Base | +302 [−13, 636] | +300 [44, 600] | +389 [138, 699] | −710 |
| **Flag costed once per patient** | **−97 [−289, 96]** | +105 [−102, 326] | +276 [41, 548] | −710 |
| **Flag = review + p53 only** | **−79 [−276, 118]** | +94 [−118, 320] | +262 [30, 528] | −711 |
| Flag = extra endoscopy | +881 | +613 | +583 | −710 |
| Sequencing £85 | +302 | +59 | +20 | −710 |
| Sequencing £400 | +302 | +519 | +725 | −710 |
| Override = any IND/LGD or p53 | +377 | +433 | +523 | −493 |
| No archive back-scan | +429 | +495 | +584 | −345 |
| Guideline 2 → 3 y | +588 | +678 | +792 | −411 |
| Guideline 5 → 10 y | +179 | +180 | +228 | −363 |
| AI £30 per endoscopy, slide £15 | +446 | +437 | +526 | −710 |
| Endoscopy £500 | +338 | +407 | +510 | −473 |
| Work-up halves late-stage risk in AI-flagged progressors | +299 | +297 | +386 | −710 |
| Early → late OAC 0.5/y | +302 | +300 | +389 | −711 |

"3 → 6 y" equals the base case within a 10-year horizon (two endoscopies either way). The decisive input is **what an AI flag triggers**. If a high band means a one-off expert review rather than a repeat work-up at every flagged endoscopy, the no-sequencing tier becomes cost-saving: −£97k to −£79k per 1,000, with P(saves) about 0.8.

### Budget impact

Assumptions:
- about 2,500 patients in surveillance per million (range 1,500–4,000);
- a typical ICB of 1.37 m has about 3,400 patients (2,100–5,500);
- a Cancer Alliance of 2.75 m has about 6,900 (4,100–11,000);
- 3% progression; annualised from the discounted 10-year cost.

Steady-state annual incremental spend:

| Strategy | ICB, £85 per sample | ICB, £250 | ICB, £400 | Cancer Alliance, £250 |
|---|---|---|---|---|
| No sequencing | £104k [−4k, 218k] | £104k | £104k | £207k |
| Light | £20k [−67k, 114k] | £103k [15k, 206k] | £178k | £206k |
| Confirmatory | £7k [−71k, 93k] | £134k [47k, 240k] | £249k | £267k |
| Sequence everything | £286k | £659k | £998k | £1.32m |

5-year rollout at 20/40/60/80/100% uptake, £250 per sample:
- ICB: £311k (no sequencing), £309k (light), £401k (confirmatory);
- Cancer Alliance: about twice that.

One-off set-up applies only where there is no digital pathology: a scanner from £100k plus integration of about £15k.

## The allowed cost claim (filled in)

> "In an illustrative, prevalence-reweighted cost-consequence analysis, the confirmatory rule required about two-thirds fewer copy-number assays than sequencing every sample (2,500 vs 7,200 per 1,000 patients over 10 years). Compared with grade + p53, it flagged fewer non-progressors (365 vs 564 per 1,000) and left fewer progressors unflagged (1.6 vs 10.3). Whether it saves money relative to current care depends on the sequencing price and the downstream cost of a flag. Against current care it is cost-neutral only at ≤ £76 per sample (95% interval −£27 to £185) when each flag triggers a £492 expert work-up, or when a flag costs ≤ £435 at £85 per sample. Against the no-sequencing tier, sequencing pays for itself at ≤ £211 per sample, or when a flag costs ≥ £619."

So **X = £76 per sample** (vs current care, base flag pathway) and **Y = £619 per flag** (vs the no-sequencing tier, at £250 per sample).

Two things change from the reviewer's template:
- Against current care no flag cost makes the rule cost-neutral at £250 per sample, because AI flags add to the pathologist's work-ups rather than replacing them.
- The "≥ £Y" form therefore holds only against the no-sequencing tier.

Within the 10-year horizon the rule's tiers are not cost-saving versus current care in the base case. "Cheaper" stays out of the title and abstract; "sequences less" is factual. The one route to saving is a flag pathway costed once per patient, or limited to an expert review. Under that pathway the no-sequencing tier saves about £80–100k per 1,000.

## What changes in the paper plan

- The supplement's cost section becomes this model, and the main text carries one sentence: the tiers add £0.30–0.39m per 1,000 patients over 10 years against current care unless an AI flag costs no more than about £200 per flagged endoscopy, or is a once-per-patient review.
- Present the tiers by capacity, not by cost:
  - sequencing is worth adding to the H&E tier only below about £210–250 per sample;
  - sequence-everything is never worth it.
- The band table needs one clinical decision before submission: does a persistent high band trigger a work-up at every flagged endoscopy, or once? It is the single input that flips the sign.

## Limitations and evidence-generation plan (EVA style)

- Rates come from a 75-patient case–control cohort. Non-progressors here had grade/p53 flags in 58% (39.5% LGD/p53), which caps de-escalation; a cohort-sampled archive (ERIN) will give real-world rates.
- A static decision tree with "ever flagged" status. The landmark analysis (another agent) should confirm that de-escalation decided at year 0 holds over 10 years.
- AI licence, back-scan and work-up costs are assumptions. Locally costed pathways, sWGS failure rates and turnaround from a GLH are needed.
- The harm model counts only late-stage diagnosis from a longer interval. Symptomatic presentation, endoscopy disutility and patient preference are not modelled.
- Implementation evidence still missing:
  - digital-pathology coverage and access to prior slides;
  - adherence to de-escalated intervals;
  - acceptability to patients;
  - SaMD/DTAC route;
  - equity for services without scanners.

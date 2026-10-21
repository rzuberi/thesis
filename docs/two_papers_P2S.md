# Two papers, agent P2S: Paper 2 safety and design analyses

Status: EXPLORATORY (21 October 2026). Shared rules: `paper/two_papers/RUN_RULES.md`. Tasks: `paper/two_papers/PAPER2_plan_v2.md` items 2–8, plus the brief's items (memory audit, per-1,000 patient-years, the 4 failing robustness rows). Reviews read: `review_P2_gastro.md`, `review_P2_editor.md`, `review_strategy_sceptic.md`.

## Plan

**Tiers under test (frozen per-fold rules, no re-implementation).**
- **No sequencing:** mean-logit endoscopy score + EW memory (E3 / E9 family `A1:img:ew` on the mean-logit variant): 31.0 caught / 26.6 NP flagged.
- **Confirmatory:** final rule (A12 memory + certificate + quiet-genome check, cn90 bar): 30.5 / 17.2; fold-internal bar: 30.4 / 16.4.
- **Comparators:** per-endoscopy gate R49 (this study), H&E alone (P1 90%), sequencing everything (P3 90%), grade IND/LGD, grade IND/LGD or p53 aberrant; single-endoscopy counterparts of each memory rule (mean-logit single endoscopy; gate score single endoscopy); Prague M and a Parasa-style score, with and without memory.

**Code.** `scripts/paper_plan/tp_p2s_main.py` executes `ex_e7_stress.py` up to its dispatch (which executes `ex_e2_veto.py` and `rv9_falseflags.py`) and the helper section of `ex_e3_score.py` (mean-logit variant as `ex_e9_frontier.py` `state('ml')`). The only new engine piece is `engine2` = `ex_e7_stress.engine` plus the chosen candidate's held-out margin (score − fold threshold). Smoke first (50 draws), reproducing R49 31.1/31.8, P1 31.1/36.0, grade 17.0/25.0, A1 30.7/23.6, A12 30.5/21.5, final 30.5/17.2, fold-internal bar 30.4/16.4, mean-logit + memory 31.0/26.6, and E7's equal-exposure A1 −6.1.

**Analyses.**
1. **Memory audit:** code reading, unit tests (future scores replaced by noise; memory and certificate at or before the cut unchanged), an end-to-end test (held-out predictions of every later endoscopy replaced by noise, whole nested pipeline rerun, flags up to the cut compared) and a cross-patient test.
2. **Landmark analysis:** every pre-event endoscopy is a landmark scored on history to date; outcome = progression within 1, 3, 5 years or ever. Sensitivity, specificity, PPV, NPV at the operating point, and landmark AUROC of the margin, memory vs single-endoscopy scoring, patient-bootstrap CIs. Equal exposure as a primary row: (a) patient level, E7 truncation (non-progressors cut to progressor endoscopy counts, 200 draws, frozen rules); (b) landmark level with the same truncation weights. Patient-weighted landmarks as a secondary row.
3. **Two-consecutive-lows rule:** de-escalate only after ≥ 2 consecutive low endoscopies; NP cleared lost and progressors de-escalated, against single-look de-escalation.
4. **Safety block:** missed (never flagged) and "cleared at the last pre-event endoscopy" progressors per tier: HGD vs IMC, focal HGD, time from the last cleared endoscopy to the event, Prague M, whether a 5-year (or 3-year) interval from that endoscopy would have postponed detection past the event date. Aggregate only (<5 suppressed). NPV among cleared patients; integer counts per repeat and majority-vote counts with exact CIs.
5. **Lead time:** evaluation restricted to endoscopies > 2 y and > 4 y before the event (NP all endoscopies, or symmetric).
6. **Clinical comparators:** Prague M and a Parasa-style score (9 × male + 5 × smoker + 1 per cm + 11 × LGD), single endoscopy and with memory, training-chosen thresholds and fixed published cut-offs; missingness reported.
7. **Subgroups:** segment length (< / ≥ 3 cm), age (< / ≥ 65), sex, samples per endoscopy.
8. **The 4 of 34 failing R49 robustness rows** (round 7c), named with the reason.
9. **Per 1,000 patient-years** in the de-escalated group at 0.3–0.6 %/yr incidence, model-based, with CIs.

**Space.** Aggregates `results/paper_final/two_papers_P2S/`; row-level `killcoyne_mm/two_papers_P2S/`; Slurm prefix `tpp2s`.

---

## Results

(appended after the runs)

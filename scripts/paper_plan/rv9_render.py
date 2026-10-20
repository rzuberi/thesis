"""Render the round-9 results (appended below the final '---' of docs/paper_review_round9_false_flags.md) from results/paper_final/review_round9/*.json.
Idempotent: everything after the plan's last '---' line is replaced. Usage: python3 scripts/paper_plan/rv9_render.py"""
import os, json, subprocess, re
T = "/Users/zuberi01/Documents/thesis"; RES = T + "/results/paper_final/review_round9"; DOC = T + "/docs/paper_review_round9_false_flags.md"
J = lambda n: json.load(open(f"{RES}/{n}.json")) if os.path.exists(f"{RES}/{n}.json") else None
def sg(x, d=1): return "n/a" if x is None else (x if isinstance(x, str) else f"{x:+.{d}f}")
def f1(x, d=1): return "n/a" if x is None else (x if isinstance(x, str) else f"{x:.{d}f}")
def ci(c, d=1): return "n/a" if not c or c[0] is None else f"[{c[0]:+.{d}f}, {c[1]:+.{d}f}]"
def dl(d, k, dd=1): x = d[k]; return f"{sg(x['delta'], dd)} {ci(x['ci95'], dd)}"
def row_main(i, m):
    v = m["values"]; r = m["vs_R49"]; p = m["vs_P1_90"]; c99 = r["np_flagged"]["ci99_bonferroni"]
    return (f"| {i} | {m['name'].replace('[nested]', '').replace('[nested, pAUC selection]', '(pAUC selection)').strip()} | {f1(v['caught'])} | {f1(v['np_flagged'])} | **{sg(r['np_flagged']['delta'])}** {ci(r['np_flagged']['ci95'])} | {ci(c99)} | "
            f"{sg(r['caught']['delta'])} {ci(r['caught']['ci95'])} | {f1(v['flags_py'], 3)} ({sg(r['flags_py']['delta'], 3)}) | {sg(r['endo_spec']['delta'], 3)} | {f1(v['seq'], 2)} ({sg(r['seq']['delta'], 2)}) | "
            f"{sg(p['np_flagged']['delta'])} {ci(p['np_flagged']['ci95'])} | {sg(p['caught']['delta'])} |")
HDR = ("| # | Method | Caught | NP flagged | Δ NP flagged vs R49 [95% CI] | 99.2% CI | Δ caught [95% CI] | Flags / NP py (Δ) | Δ endoscopy spec. | Samples seq. / patient (Δ) | Δ NP flagged vs P1 90% [95% CI] | Δ caught vs P1 |\n"
       "|---|---|---|---|---|---|---|---|---|---|---|---|")
def rank_key(m): d = m["vs_R49"]; return (0 if d["caught"]["delta"] >= -0.5 else 1, d["np_flagged"]["delta"], -d["caught"]["delta"])
def render():
    M = J("merge")["merge"]; F0 = J("f0"); ICC = J("icc"); CU = J("curves"); RC = J("refit_check"); L = []; A = L.append
    h = subprocess.run(["git", "-C", T, "log", "-1", "--format=%h", "--", "results/paper_final/review_round9"], capture_output=True, text=True).stdout.strip() or "pending"
    meths = M["methods"]; nest = sorted([m for m in meths if m["kind"] in ("nested", "nested_pauc")], key=rank_key); byname = {m["name"]: m for m in meths}
    A("## Results\n")
    A(f"Rendered by `scripts/paper_plan/rv9_render.py` from `results/paper_final/review_round9/` (aggregate results {h}); scripts `rv9_falseflags.py` (everything except B4 fitting), `rv9_later.py` (F0 input), `rv9_refit.R` (B4 refits); figures by `rv9_figs.py` (local, not committed). "
      "**This round is exploratory: every number is a post hoc finding, nothing is adjusted for the many methods tried, and no method replaces R49.** Single model = per-repeat values averaged over the 10 repeats. "
      f"Intervals: paired patient bootstrap, {M['draws']:,} draws (`RandomState(0)`); the 99.2% interval (Bonferroni over 6 method families) is shown for reference. No ACE-B file was read; frozen bundles and stored predictions are unchanged; only B4 refits the H&E model (`rv9_refit.R`).\n")
    chk = M["check_round8"]; A(f"Check (round-8 settings, observed): R49 {chk['R49']['caught']:.1f} caught / {chk['R49']['np_flagged']:.1f} NP flagged; P1 90% {chk['P1_90']['caught']:.1f} / {chk['P1_90']['np_flagged']:.1f} (expected 31.1 / 31.8 and 31.1 / 36.0); reproduced: {'yes' if chk['reproduced'] else 'NO'}. "
      f"Refit reproduction (`rv9_refit.R` with weight 1 and all rows against the stored predictions): outer repeat 1 max |difference| {RC['refit_check']['outer_rep_01']['max_abs_pred_diff']:.1e}, inner repeat 1 fold 1 {RC['refit_check']['inner_rep_01_fold_01']['max_abs_pred_diff']:.1e}; passed: {'yes' if RC['refit_check']['passed'] else 'NO'}.\n" if RC else f"Check (round-8 settings, observed): R49 {chk['R49']['caught']:.1f} / {chk['R49']['np_flagged']:.1f}; P1 90% {chk['P1_90']['caught']:.1f} / {chk['P1_90']['np_flagged']:.1f}; reproduced: {'yes' if chk['reproduced'] else 'NO'}.\n")
    # ---------------------------------------------------------------- F0
    if F0:
        F = F0["F0"]; A("### F0. Are flagged non-progressors more likely to show later dysplasia? (descriptive)\n")
        A(f"{F['definition']}. Non-progressor patients: {F['n_non_progressor_patients']}. Group sizes: " + "; ".join(f"{k} {v}" for k, v in F["group_sizes"].items()) + ".\n")
        A("| Rule | NP ever flagged (≥ 5 of 10 repeats) | Population | Outcome | Flagged: later / not | Not flagged: later / not | Share later: flagged vs not flagged | Fisher p |\n|---|---|---|---|---|---|---|---|")
        for r, o in F["rules"].items():
            for tn, t in o["tables"].items():
                pop, out = tn.split(":"); A(f"| {r} | {o['ever_flagged_in_ge5_of_10_repeats']} | {pop.replace('_', ' ')} | {out.replace('_', ' ')} | {t['flagged_later']} / {t['flagged_not_later']} | {t['not_flagged_later']} / {t['not_flagged_not_later']} | {t['share_later_among_flagged']} vs {t['share_later_among_not_flagged']} | {t['fisher_p_two_sided']} |")
            a = o["any_later_record"]; A(f"| {r} | {o['ever_flagged_in_ge5_of_10_repeats']} | all 43 | any later database record | {a['flagged_with_record']} / {a['flagged_without']} | {a['not_flagged_with']} / {a['not_flagged_without']} | {a['share_flagged']} vs {a['share_not_flagged']} | {a['fisher_p_two_sided']} |")
        A("\nFlagged non-progressor endoscopies per patient-year by later-grade group (groups below 5 patients: '<5'):\n")
        gs = list(next(iter(F["rules"].values()))["flags_per_patient_year_by_later_group"]); A("| Rule | " + " | ".join(gs) + " |\n|---|" + "---|" * len(gs))
        for r, o in F["rules"].items(): A(f"| {r} | " + " | ".join(f"{o['flags_per_patient_year_by_later_group'][g]['flagged_endoscopies_per_patient_year']} (n = {o['flags_per_patient_year_by_later_group'][g]['patients']})" for g in gs) + " |")
        A("")
    # ---------------------------------------------------------------- ICC
    if ICC:
        I = ICC["ICC"]; A("### Per-patient intraclass correlation of endoscopy scores (before the memory rules)\n")
        A("| Score | Class | ICC(1) [95% CI] | Between-patient MS | Within-patient MS | Patients / endoscopies |\n|---|---|---|---|---|---|")
        for sc_, v in I["scores"].items():
            for cl, x in v.items(): A(f"| {sc_} | {cl.replace('_', '-')} | {x['icc1_mean_over_repeats']:.2f} [{x['ci95'][0]:.2f}, {x['ci95'][1]:.2f}] | {x['between_patient_mean_square']:.2f} | {x['within_patient_mean_square']:.2f} | {x['patients']} / {x['endoscopies']} |")
        A(f"\n{I['estimator']}. {I['reading']}.\n")
        A("Persistence ceiling: non-progressor patients (mean over repeats) flagged at exactly 1, 2 and ≥ 3 endoscopies. A patient flagged once only is the most a persistence rule can remove.\n")
        A("| Rule | NP ever flagged | Flagged once only | Twice | ≥ 3 times | Flagged ≥ 2 times | Share of flagged NP with one flag only |\n|---|---|---|---|---|---|---|")
        for r, c in I["persistence_ceiling_np_patients"].items(): A(f"| {r} | {c['np_patients_ever_flagged']} | {c['np_flagged_once_only']} | {c['np_flagged_twice']} | {c['np_flagged_3_or_more']} | {c['np_flagged_at_least_twice']} | {c['share_of_flagged_np_with_only_one_flagged_endoscopy']} |")
        A("")
    # ---------------------------------------------------------------- ranking
    A("### Ranking: nested (held-out) results, all families\n")
    A("Every row: operating threshold (and, within a family, the hyper-parameter) chosen on the training patients' inner out-of-fold predictions of each outer fold by the plan's rule; performance on the held-out patients. "
      "Δ against R49 and against P1 at 90% on the same bootstrap draws. Ranked by Δ NP flagged among rows with Δ caught ≥ -0.5 (point estimate); the other rows follow. 'Control' rows are threshold-only dials and re-tuned R49 (they show what the training-side tuning rule alone does). "
      "'(pAUC selection)' rows choose the hyper-parameter by patient-level partial AUC (FPR ≤ 0.2) instead.\n")
    A(HDR)
    for i, m in enumerate(nest, 1): A(row_main(i, m))
    A("")
    top3 = M["top3_names"]; A("**Top 3 (excluding controls and pAUC variants): " + "; ".join(f"{i}. {n.replace(' [nested]', '')}" for i, n in enumerate(top3, 1)) + ".**\n")
    # ---------------------------------------------------------------- progressors with one endoscopy / k-of-n
    A("### k-of-n persistence and progressors with a single pre-event endoscopy\n")
    A("A 2-of-n rule cannot flag a progressor with one pre-event endoscopy unless an override threshold (t_high) flags it outright.\n")
    A("| Method (nested) | Progressors with 1 endoscopy: caught (of n) | R49 | Δ caught overall | Δ NP flagged [95% CI] |\n|---|---|---|---|---|")
    for m in nest:
        if m["kind"] == "nested" and m["family"].split(":")[-1] in ("k2any", "k2of3", "cons2", "k2any_o", "k2of3_o", "pers") and "caught_progressors_with_one_endoscopy" in m:
            q = m["caught_progressors_with_one_endoscopy"]; A(f"| {m['name'].replace(' [nested]', '')} | {q['caught']} (of {q['n']}) | {q['R49']} | {sg(m['vs_R49']['caught']['delta'])} | {dl(m['vs_R49'], 'np_flagged')} |")
    A("")
    # ---------------------------------------------------------------- group tables: grid points and extras
    def grid_table(title, fam_pred, maxrows=40):
        rows = [m for m in meths if m["kind"] == "grid_point" and fam_pred(m["family"])]; rows = sorted(rows, key=rank_key)[:maxrows]
        if not rows: return
        A(f"#### {title}\n"); A("Fixed hyper-parameter picked after seeing the evaluation (optimistic); the threshold is still the training-chosen one.\n"); A(HDR)
        for i, m in enumerate(rows, 1): A(row_main(i, m))
        A("")
    A("### Grid points (apparent, labelled optimistic)\n")
    grid_table("A1 memory rules", lambda f: f.startswith("A1:") and not f.endswith(":none"), 40); grid_table("A2 / A2' certificates", lambda f: f.startswith("A2:")); grid_table("A3 agreement", lambda f: f == "A3"); grid_table("B3 abstention", lambda f: f == "B3")
    grid_table("A1+A2 and B1+A1+A2 combined", lambda f: f in ("A12", "B2A2"), 20); grid_table("B1 stacked gate and controls (cut-off cells)", lambda f: f.startswith("B1:") or f == "C1", 30); grid_table("B4 refits (re-tuned cut-off cells)", lambda f: f.startswith("B4"), 15)
    ev = sorted([m for m in meths if m["kind"] == "matched"], key=rank_key)[:30]
    A("### Evaluation-matched versions (optimistic)\n"); A("Threshold set on the evaluation patients, per repeat, so that progressor patients caught equals R49's (re-matched in every bootstrap draw). Score-type methods only (candidates: the progressor patients' own scores); the number shown is the 30 best.\n"); A(HDR)
    for i, m in enumerate(ev, 1): A(row_main(i, m))
    A("")
    # ---------------------------------------------------------------- B3, A2 details, selection frequencies
    b3 = [m for m in nest if m["family"] == "B3" and m["kind"] == "nested"]
    if b3: m = b3[0]; A(f"### B3. Abstention: indeterminate endoscopies\n\nNested row: mean per repeat {m['indeterminate_endoscopies_per_repeat_mean']} indeterminate endoscopies, of which {m['indeterminate_progressor_endoscopies_per_repeat_mean']} progressor endoscopies (counted as missed, 288 pre-event endoscopies in all). Selected share over the 100 folds: {m['selected_candidate_counts_over_100_folds']}.\n")
    A("### Choices made inside training (selection frequencies over the 100 outer folds)\n"); A("| Family | Chosen candidate: folds | Infeasible folds (training detection target unreachable) | Mean training detection target / reached |\n|---|---|---|---|")
    for m in nest:
        if m["kind"] == "nested" and "selected_candidate_counts_over_100_folds" in m: A(f"| {m['name'].replace(' [nested]', '')} | {'; '.join(f'{k}: {v}' for k, v in m['selected_candidate_counts_over_100_folds'].items() if v)} | {m['infeasible_folds_np']} | {m['mean_training_detection_target']} / {m['mean_training_detection_method']} |")
    A("")
    # ---------------------------------------------------------------- curves
    if CU:
        C = CU["curves"]; A("### Cumulative false-flag curves by endoscopy index\n"); A(f"Best memory rule in the ranking: **{C['best_memory_rule'].replace(' [nested]', '')}**. {C['note']}.\n")
        A("| k | Rule | NP flagged: all patients [95% CI] | NP flagged: patients with ≥ k endoscopies (n) | Progressors caught: all | Progressors caught: ≥ k (n) | Δ NP vs R49 [95% CI] (all) |\n|---|---|---|---|---|---|---|")
        for k in range(1, 7):
            for r, o in C["curves"].items():
                a = o[f"k={k}"]["all_patients_first_k_endoscopies"]; b = o[f"k={k}"]["restricted_to_patients_with_ge_k_endoscopies"]; d = C["delta_np_share_vs_R49_all_patients"].get(r, {}).get(f"k={k}")
                A(f"| {k} | {r.replace(' [nested]', '')} | {a['np']['share']} {a['np']['ci95'] if isinstance(a['np']['ci95'], str) else ci(a['np']['ci95'], 2).replace('+', '')} | {b['np']['share']} (n = {b['np']['patients']}) | {a['prog']['share']} | {b['prog']['share']} (n = {b['prog']['patients']}) | "
                  f"{'' if d is None else sg(d['delta'], 3) + ' ' + ci(d['ci95'], 3)} |")
        A("")
    # ---------------------------------------------------------------- robustness
    rob = {}
    for r in ("ndbe", "ge2", "tis_lt256", "tis_ge256", "tis_lt256pure", "tis_ge256pure", "r52a"):
        x = J("rob_" + r)
        if x: rob[r] = x["ROB"]
    if rob:
        A("### Robustness of the top 3 methods\n"); A("Rows as the R49 robustness rows (`docs/paper_review_round7c_gate_robustness.md`) that can be re-scored: the same nested procedure is repeated inside the row's population (NDBE-only, ≥ 2 samples, R52(a) refit set: every training-side choice is redone; tissue strata: held-out calls of the main run, evaluation restricted). "
          "Between-repeat variance and the refit bootstrap are below.\n")
        A("| Row | Population (endoscopies; progressor / non-progressor patients) | Rule | Caught | NP flagged | Δ NP flagged vs R49 [95% CI] | Δ caught vs R49 [95% CI] | Δ NP flagged vs P1 90% [95% CI] |\n|---|---|---|---|---|---|---|---|")
        for r, o in rob.items():
            p = o["population"]; popt = f"{p['endoscopies']}; {p['progressor_patients']} / {p['non_progressor_patients']}"
            for nm, v in o["results"].items():
                if nm in ("R49", "P1 90%"): A(f"| {o['row']} | {popt} | {nm} | {f1(v['caught'])} | {f1(v['np_flagged'])} | | | |")
                else: A(f"| {o['row']} | {popt} | {nm} | {f1(v['values']['caught'])} | {f1(v['values']['np_flagged'])} | {dl(v['vs_R49'], 'np_flagged')} | {dl(v['vs_R49'], 'caught')} | {dl(v['vs_P1_90'], 'np_flagged')} |")
        A("\nRow definitions: " + "; ".join(f"**{r}**: {o['definition']}" for r, o in rob.items()) + ".\n")
        A("Between-repeat variance of the main-run result (Δ against R49 per repeat, 10 repeats):\n"); A("| Method | Δ NP flagged: mean (SD; min, max) | Δ caught: mean (SD; min, max) |\n|---|---|---|")
        for n in top3:
            m = byname[n]; a = m["between_repeat_delta_np_flagged_vs_R49"]; b = m["between_repeat_delta_caught_vs_R49"]; A(f"| {n.replace(' [nested]', '')} | {a['mean']:+.2f} ({a['sd']:.2f}; {a['min']:+.1f}, {a['max']:+.1f}) | {b['mean']:+.2f} ({b['sd']:.2f}; {b['min']:+.1f}, {b['max']:+.1f}) |")
        A("\nRefit bootstrap (F3, 200 draws): not re-scored; see Implementation notes.\n")
    A("### Figures (local, not committed)\n"); A("`paper/figures_r9/`: `r9_forest.png` (ranked Δ NP patients flagged against R49, Δ caught annotated), `r9_scatter.png` (caught against NP flagged for every method with R49, P1 90%, P3 90% and grade marked), `r9_f0.png` (F0), `r9_icc.png` (ICC), `r9_curves.png` (cumulative false-flag curves).\n")
    return "\n".join(L)
if __name__ == "__main__":
    body = render(); notes = open(T + "/scripts/paper_plan/rv9_notes.md").read() if os.path.exists(T + "/scripts/paper_plan/rv9_notes.md") else ""
    doc = open(DOC).read(); i = doc.rindex("\n---\n"); head = doc[:i + 5]; open(DOC, "w").write(head + "\n" + body + "\n" + notes); print("rendered", len(body), "chars")

"""Two papers, agent CNC: markdown tables for docs/two_papers_CNC.md from results/paper_final/two_papers_CNC/{score,select}.json (aggregates only)."""
import json, sys, os
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../results/paper_final/two_papers_CNC")
f3 = lambda v: "—" if v is None else f"{v:.3f}"
s3 = lambda v: "—" if v is None else f"{v:+.3f}"
ci = lambda c: f"[{f3(c[0])}, {f3(c[1])}]" if c and c[0] is not None else ""
dci = lambda d: "—" if d["ci95"][0] == d["ci95"][1] == 0 else f"{s3(d['delta'])} [{s3(d['ci95'][0])}, {s3(d['ci95'][1])}]"
S = json.load(open(f"{R}/score.json")); out = []
for unit in ("sample", "patient_weighted"):
    U = S["score"][unit]; ref = U["reference"]
    out.append(f"\n**{'Sample level' if unit == 'sample' else 'Patient-weighted'}** (reference: L-CNV {f3(ref['L-CNV']['value'])} {ci(ref['L-CNV']['ci95'])}; clean L-IMG {f3(ref['L-IMG']['value'])} {ci(ref['L-IMG']['ci95'])}; "
               f"L-LATE = L-CNV + clean L-IMG {f3(ref['L-LATE']['value'])} {ci(ref['L-LATE']['ci95'])}; published L-IMG {f3(ref['L-IMG stored']['value'])})\n")
    out.append("| CN representation | AUROC [95% CI] | Δ vs L-CNV | Δ vs clean L-IMG | Fused with clean L-IMG | Fused − clean L-IMG | Fused − L-LATE |")
    out.append("|---|---|---|---|---|---|---|")
    for t, v in U["representations"].items():
        out.append(f"| {v['label']} | {f3(v['auroc']['value'])} {ci(v['auroc']['ci95'])} | {dci(v['delta_vs_L_CNV'])} | {dci(v['delta_vs_clean_L_IMG'])} | {f3(v['late_auroc']['value'])} {ci(v['late_auroc']['ci95'])} | {dci(v['late_minus_clean_L_IMG'])} | {dci(v['late_minus_clean_L_LATE'])} |")
if os.path.exists(f"{R}/select.json"):
    L = json.load(open(f"{R}/select.json"))["select"]
    out.append("\n| Candidate set | Unit | Nested CN AUROC | Nested − L-CNV | Nested CN − clean L-IMG | Nested L-LATE | Nested L-LATE − clean L-IMG | Apparent best (optimistic) | Optimism: best − nested | Chosen most often |")
    out.append("|---|---|---|---|---|---|---|---|---|---|")
    for nm, R_ in L.items():
        top = sorted(R_["times_chosen_of_100_folds"].items(), key=lambda kv: -kv[1])[:3]
        for unit in ("sample", "patient_weighted"):
            u = R_[unit]; a = u["auroc"]
            out.append(f"| {nm} ({len(R_['candidates'])}) | {unit.replace('_', '-')} | {f3(a['CN-nested']['value'])} {ci(a['CN-nested']['ci95'])} | {dci(u['nested_minus_L_CNV'])} | {dci(u['nested_CN_minus_clean_L_IMG'])} | "
                       f"{f3(a['LATE-nested']['value'])} {ci(a['LATE-nested']['ci95'])} | {dci(u['nested_LATE_minus_clean_L_IMG'])} | {f3(u['apparent_best_candidate']['auroc'])} ({u['apparent_best_candidate']['name']}) | "
                       f"{dci(u['optimism_apparent_best_minus_nested'])} | {', '.join(f'{k} {v}' for k, v in top)} |")
print("\n".join(out))

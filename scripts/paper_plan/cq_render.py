"""Render the Results section of docs/paper_cnvquiet_morphology.md from the aggregates in results/paper_final/cnvquiet_morphology/
(groups.json, segmentation_qc.json, stats.json, answers.json). Everything above the final '---' line is kept byte for byte.
usage (local, from the repo root): python scripts/paper_plan/cq_render.py PRESPEC_COMMIT RESULTS_COMMIT"""
import json, sys
P = "docs/paper_cnvquiet_morphology.md"; R = "results/paper_final/cnvquiet_morphology"
GJ, QJ, SJ, AJ = (json.load(open(f"{R}/{f}.json")) for f in ("groups", "segmentation_qc", "stats", "answers"))
pre, res = sys.argv[1], sys.argv[2]; doc = open(P).read(); head = doc[: doc.rindex("\n---\n") + 5]
f3 = lambda v: "n/a" if v is None or v != v else (f"{v:.3f}" if abs(v) < 10 else f"{v:.1f}")
fp = lambda p: "n/a" if p is None or p != p else (f"{p:.3f}" if p >= 0.001 else "< 0.001")
ci = lambda c: f"[{f3(c[0])}, {f3(c[1])}]"
L = ["", "## Results", "", f"Pre-specification commit {pre}; results commit {res}. Scripts `scripts/paper_plan/cq_groups.py`, `cq_extract.py`, `cq_segment.py`, `cq_features.py`, `cq_stats.py`, `cq_fig.py`, `cq_render.py` "
     f"(Slurm via `scripts/cluster/campaign.sh`, prefixes {AJ['prefixes']}). Aggregates `{R}/`. Row-level outputs on the cluster only.", "", "### Status", "", "| Item | Status |", "|---|---|"]
for k, v in AJ["status"].items(): L.append(f"| {k} | {v} |")
L += ["", "### Groups", "", "Patient counts are distinct patients; (a) and (b) share patients (6 of the 8 (a) patients also have (b) samples). Raw cx = package block.", "",
      "| Group | Samples | Patients | Slides | Raw cx, mean (SD) | Raw cx, median | Grade | Scanner | Tissue tiles, median | Max samples per patient |", "|---|---|---|---|---|---|---|---|---|---|"]
NAME = {"a": "(a) CNV-quiet newly caught", "b": "(b) caught by both", "c": "(c) matched non-progressors"}
for g in "abc":
    s = GJ["groups"][g]; L.append(f"| {NAME[g]} | {s['samples']} | {s['patients']} | {s['slides']} | {s['cx_raw_mean']:.1f} ({s['cx_raw_sd']:.1f}) | {s['cx_raw_median']:.0f} | "
                                  + ", ".join(f"{k} {v}" for k, v in sorted(s['grade'].items())) + " | " + ", ".join(f"{k} {v}" for k, v in sorted(s['scanner'].items())) + f" | {s['tissue_tiles_median']:.0f} | {s['samples_per_patient_max']} |")
c = GJ["c_abs_dcx"]; L += ["", f"Count check against `docs/paper_horizon_q2_all_horizons.md`: " + "; ".join(f"{k} {v['got'][0]} / {v['got'][1]} ({'ok' if v['ok'] else 'MISMATCH'})" for k, v in GJ["count_checks"].items()) + ".",
      f"Matching: |Δcx| mean {c['mean']:.2f}, maximum {c['max']:.0f}, exact {c['n_exact']} of {GJ['groups']['c']['samples']}. (a) samples also newly caught at 3 years: {GJ['a_in_3y_newly_caught']}.", "",
      "### Segmentation", "", f"Slides {QJ['slides']}, tiles {QJ['tiles_total']}; coordinate check on tissue tiles: minimum r {QJ['coord_corr_min_tissue_tiles']:.3f}, slides failing {QJ['slides_failing_coord_check']} (pre-specified all-tile rule: {QJ['slides_failing_prespecified_all_tile_rule']} slides would fail, minimum r {QJ['coord_corr_min']:.3f}, all on blank-glass tiles; see deviations); level-0 mpp {QJ['mpp0_range'][0]:.4f}–{QJ['mpp0_range'][1]:.4f}, "
      f"resampled tiles {', '.join(map(str, QJ['out_px_values']))} px at {QJ['out_mpp_range'][0]:.4f}–{QJ['out_mpp_range'][1]:.4f} µm/px; nuclei kept (≥ 5 µm²) {QJ['nuclei_kept_total']:,}. {AJ['compute']}", "",
      "| Group | Nuclei | Epithelial nuclei | Share of epithelial called neoplastic | Inflammatory per 100 epithelial (any distance) | Median epithelial nuclei per sample | Tiles with epithelium | Samples ineligible F1–F3, F5 / F4 |", "|---|---|---|---|---|---|---|---|"]
for g in "abc":
    q = SJ["qc"][g]; L.append(f"| {NAME[g]} | {q['nuclei_total']:,} | {q['epithelial_nuclei']:,} | {q['share_epithelial_called_neoplastic']:.3f} | {q['inflammatory_per_100_epithelial_all']:.1f} | {q['median_epithelial_nuclei_per_sample']:.0f} | {q['share_tiles_with_epithelium']:.3f} | {q['samples_ineligible_F1_F3_F5']} / {q['samples_ineligible_F4']} |")
L += ["", "### Primary: (a) vs (c), patient level", "", "Patient value = mean over the patient's eligible samples in the group. Δ = (a) − (c) patient-level means, 95% patient-bootstrap CI. AUC = P((a) patient > (c) patient). Two-sided Mann–Whitney U; Holm over the features.", "",
      "| Feature | Patients a / c | (a) mean (SD) | (c) mean (SD) | Δ (a − c) [95% CI] | AUC | p | Holm p |", "|---|---|---|---|---|---|---|---|"]
for i, (f, name) in enumerate(SJ["features"].items()):
    r = SJ["primary"][f]; L.append(f"| F{i + 1} {name} | {r['n_patients']['a']} / {r['n_patients']['c']} | {f3(r['patient_mean']['a'])} ({f3(r['patient_sd']['a'])}) | {f3(r['patient_mean']['c'])} ({f3(r['patient_sd']['c'])}) | "
                                  f"{f3(r.get('diff_a_minus_c'))} {ci(r['diff_ci95']) if 'diff_ci95' in r else ''} | {f3(r.get('auc_a_gt_c'))} | {fp(r['p_raw'])} | {fp(r['p_holm'])} |")
L += ["", "### (b) progressor samples caught by both, descriptive (no tests)", "", "| Feature | Patients | (b) mean (SD) | Δ (b − c) [95% CI] | AUC (b > c) | Δ (b − a) [95% CI] |", "|---|---|---|---|---|---|"]
for i, (f, name) in enumerate(SJ["features"].items()):
    r, d = SJ["primary"][f], SJ["descriptive"][f]; L.append(f"| F{i + 1} {name} | {r['n_patients']['b']} | {f3(r['patient_mean']['b'])} ({f3(r['patient_sd']['b'])}) | {f3(d['diff_b_minus_c'])} {ci(d['diff_b_minus_c_ci95'])} | {f3(d['auc_b_gt_c'])} | {f3(d['diff_b_minus_a'])} {ci(d['diff_b_minus_a_ci95'])} |")
L += ["", "### Secondary, descriptive", "", "| Feature | 3-year (a) vs its matches: patients, Δ, unadjusted p | Sample-level means a / b / c | Matched sets: mean (a − matches), (a) above |", "|---|---|---|---|"]
for i, (f, name) in enumerate(SJ["features"].items()):
    s3, r, m = SJ["secondary_3y"][f], SJ["primary"][f], SJ["matched_sets"][f]
    L.append(f"| F{i + 1} | {s3['n_patients'][0]} / {s3['n_patients'][1]}, {f3(s3['diff'])}, {fp(s3['p_unadjusted'])} | {' / '.join(f3(r['sample_mean'][g]) for g in 'abc')} | {f3(m['mean_diff'])}, {m['n_a_above_matches']} of {m['n_sets']} |")
L += ["", "### Answers", ""] + [f"{i + 1}. {a}" for i, a in enumerate(AJ["answers"])]
L += ["", "### Deviations from the pre-specification", ""] + [f"- {d}" for d in AJ["deviations"]]
L += ["", "**Figure.** `be_paper_figs/v3/16_F_cnvquiet_morphology.{pdf,png}`.", f"**Caveats.** " + " ".join(f"({i + 1}) {c}" for i, c in enumerate(AJ["caveats"])), ""]
open(P, "w").write(head + "\n".join(L)); print("CQ RENDER DONE")

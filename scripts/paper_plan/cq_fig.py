"""Figure 16_F_cnvquiet_morphology (docs/paper_cnvquiet_morphology.md): per feature, patient values for (a) CNV-quiet newly caught progressors,
(b) progressors caught by both, (c) CNV/grade/scanner-matched non-progressors, with patient-level means; primary (a) vs (c) Holm p in the title;
plus one HoVer-Net overlay from a smoke-test slide outside all groups (no identifiers). Runs on the cluster (patient values are cluster-only);
the PNG/PDF are copied to ~/Downloads/be_paper_figs/v3/."""
import json, sys, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from PIL import Image
T = "/mnt/scratche/slow/fmlab/zuberi01/phd/thesis"; W = T + "/feasibility/paper_plan/killcoyne_mm/cnvquiet_morphology"
S = json.load(open(T + "/results/paper_final/cnvquiet_morphology/stats.json")); P = pd.read_csv(W + "/fig_patient_values.csv"); OV = sys.argv[1]
plt.rcParams.update({"font.size": 8.5, "axes.spines.top": False, "axes.spines.right": False})
COL = {"a": "#d62728", "b": "#ff7f0e", "c": "#1f77b4"}; LAB = {"a": "(a) CNV-quiet,\nnewly caught", "b": "(b) caught\nby both", "c": "(c) matched\nnon-progressors"}
fig = plt.figure(figsize=(11, 6.4)); gs = fig.add_gridspec(2, 4); rs = np.random.RandomState(0)
for i, (f, name) in enumerate(S["features"].items()):
    ax = fig.add_subplot(gs[0, i]) if i < 4 else fig.add_subplot(gs[1, 0]); r = S["primary"][f]
    for j, g in enumerate("abc"):
        v = P[(P.feature == f) & (P.group == g)].value.values; ax.scatter(j + rs.uniform(-0.12, 0.12, len(v)), v, s=14, color=COL[g], alpha=0.75, lw=0)
        ax.hlines(v.mean(), j - 0.25, j + 0.25, color="k", lw=1.6)
    ax.set_xticks(range(3)); ax.set_xticklabels([LAB[g] for g in "abc"], fontsize=7); ax.set_xlim(-0.6, 2.6)
    ph = r.get("p_holm"); ax.set_title(f"F{i + 1} {name}\n(a) vs (c): Δ {r.get('diff_a_minus_c', float('nan')):+.3g}, Holm p {ph:.2f}" if ph == ph else f"F{i + 1} {name}\nnot estimable", fontsize=7.5, loc="left")
ax = fig.add_subplot(gs[1, 1:]); im = np.asarray(Image.open(OV).convert("RGB")); ax.imshow(im); ax.set_xticks([]); ax.set_yticks([])
ax.set_title("HoVer-Net (PanNuke) on one stored tile, 0.25 µm/px, slide outside all groups\nleft: tile; right: contours (red neoplastic, cyan epithelial, green inflammatory, blue connective, yellow dead)", fontsize=7, loc="left")
n = S["qc"]; fig.suptitle(f"Nuclear features in CNV-quiet progressor samples: patients (a) {n['a']['patients']}, (b) {n['b']['patients']}, (c) {n['c']['patients']}; "
                          f"samples {n['a']['samples']} / {n['b']['samples']} / {n['c']['samples']}. Dots = patient means; bar = group mean. (b) descriptive only.", fontsize=8.5, x=0.01, ha="left")
fig.tight_layout(rect=(0, 0, 1, 0.96))
for ext in ("pdf", "png"): fig.savefig(f"{W}/16_F_cnvquiet_morphology.{ext}", dpi=200)
print("CQ FIG DONE")

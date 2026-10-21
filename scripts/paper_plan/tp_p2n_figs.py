"""Two papers, agent P2N: figures of the selection-aware null from the aggregate results/paper_final/two_papers_P2N/merge.json (local; PNG 200 dpi, not committed).
fig_p2n_null.png: null distribution of the best-of-search gain (NP flagged vs R49, tolerance 1 progressor) for the three nulls, real value marked.
fig_p2n_null_scatter.png: the selected cell of every null label set (Δ caught, Δ NP flagged) against the real selection."""
import json, os, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
H = os.path.dirname(os.path.abspath(__file__)); R = json.load(open(H + "/../../results/paper_final/two_papers_P2N/merge.json")); OD = H + "/../../paper/two_papers/figs_P2N"; os.makedirs(OD, exist_ok=True)
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#52514e", "axes.labelcolor": "#0b0b0b", "xtick.color": "#52514e", "ytick.color": "#52514e"})
BLUE, INK, MUTED = "#2a78d6", "#0b0b0b", "#8a8984"
PAN = [("a_free", "(a) Full refit of L-IMG and L-CNV\n+ whole rule search"), ("b_free", "(b) Stored predictions\n+ whole rule search"), ("b_strat", "(b') As (b), labels permuted within\nendoscopy-count strata")]
PAN = [(k, t) for k, t in PAN if k in R]
fig, axes = plt.subplots(1, len(PAN), figsize=(3.6 * len(PAN), 3.4), sharey=False)
axes = np.atleast_1d(axes); lo = min(min(R[k]["tol1.0"]["null_dNP_values"]) for k, _ in PAN); real = R[PAN[0][0]]["tol1.0"]["dNP"]["real"]; lo = min(lo, real) - 1.5
for ax, (k, t) in zip(axes, PAN):
    o = R[k]["tol1.0"]; v = np.array(o["null_dNP_values"], float); bins = np.arange(np.floor(lo), 0.75, 0.5)
    ax.hist(v, bins=bins, color=BLUE, edgecolor="white", linewidth=0.8)
    ax.axvline(o["dNP"]["real"], color=INK, lw=2); ymax = ax.get_ylim()[1]
    ax.text(o["dNP"]["real"] + 0.3, ymax * 0.93, f"real search\n{o['dNP']['real']:+.1f}", color=INK, fontsize=9, va="top")
    p = o["dNP"]["p"]; B = R[k]["B"]; ptxt = f"p < {1 / (B + 1) + 1e-9:.4f}" if o["dNP"]["n_null_at_or_below_real"] == 0 else f"p = {p:.4f}"
    ax.text(0.98, 0.62, f"B = {B}\nnull median {np.median(v):+.1f}\nnull min {v.min():+.1f}\n{ptxt}", transform=ax.transAxes, ha="right", va="top", fontsize=9, color="#52514e")
    ax.set_title(t, fontsize=10, loc="left"); ax.set_xlabel("Best cell: Δ NP patients flagged vs R49\n(of 43; caught ≥ R49 − 1)")
axes[0].set_ylabel("Label permutations")
fig.tight_layout(); fig.savefig(OD + "/fig_p2n_null.png", dpi=200); plt.close(fig)
fig, axes = plt.subplots(1, len(PAN), figsize=(3.6 * len(PAN), 3.4), sharex=True, sharey=True); axes = np.atleast_1d(axes)
for ax, (k, t) in zip(axes, PAN):
    o = R[k]["tol1.0"]; x = np.array(o["null_dC_values"], float); y = np.array(o["null_dNP_values"], float); rng = np.random.RandomState(0)
    ax.scatter(x + rng.uniform(-0.04, 0.04, len(x)), y, s=10, color=BLUE, alpha=0.35, linewidths=0)
    ax.scatter([o["real_dC"]], [o["dNP"]["real"]], s=60, color=INK, zorder=3); ax.annotate("real", (o["real_dC"], o["dNP"]["real"]), xytext=(6, 4), textcoords="offset points", fontsize=9, color=INK)
    ax.set_title(t, fontsize=10, loc="left"); ax.set_xlabel("Δ progressor patients caught vs R49 (of 32)")
axes[0].set_ylabel("Δ NP patients flagged vs R49 (of 43)")
fig.tight_layout(); fig.savefig(OD + "/fig_p2n_null_scatter.png", dpi=200); plt.close(fig); print("figs written", OD)

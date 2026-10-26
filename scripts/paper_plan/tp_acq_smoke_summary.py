"""ACQ smoke summary: per smoke BAM (no identifiers; keyed by batch) the wall time, sacct memory, output size, reads used at native,
0.4x and 0.29x nominal, and a bin-noise index (robust s.d. of count/median over the discovery 'use' bins, autosomes) beside a discovery
sample; genome-wide binned-count figure for one smoke sample. Aggregate JSON -> results/paper_final/two_papers_ACQ/smoke.json."""
import os, glob, json, subprocess, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
A = "/mnt/scratche/slow/fmlab/zuberi01/phd/thesis/feasibility/paper_plan/killcoyne_mm/two_papers_ACQ"; RES = "/mnt/scratche/slow/fmlab/zuberi01/phd/thesis/results/paper_final/two_papers_ACQ"
os.makedirs(RES, exist_ok=True); os.makedirs(f"{A}/figs", exist_ok=True)
B = pd.read_csv(f"{A}/disc_bins_hg38_50kb.tsv", sep="\t"); use = (B.use.astype(str) == "True") & B.chromosome.astype(str).isin([str(i) for i in range(1, 23)])
def noise(c):
    x = c[use.values]; m = np.median(x); r = x / m; return float(1.4826 * np.median(np.abs(r - np.median(r))))
def jobinfo(key):
    logs = glob.glob(f"{A}/logs/smoke_{key}_*.log"); j = logs[0].rsplit("_", 1)[1].split(".")[0] if logs else None
    if not j: return {}
    s = subprocess.run(["sacct", "-j", j, "-P", "-n", "--format=JobID,Elapsed,MaxRSS,TotalCPU,AllocCPUS"], capture_output=True, text=True).stdout.strip().split("\n")
    out = {}
    for l in s:
        f = l.split("|")
        if f[0].endswith(".batch"): out = {"elapsed": f[1], "maxrss": f[2], "totalcpu": f[3], "alloc_cpus": f[4]}
    return out
res = {}; prof = {}
for d in sorted(glob.glob(f"{A}/smoke/smoke_*")):
    key = os.path.basename(d); st = dict(l.rstrip("\n").split("\t", 1) for l in open(f"{d}/stats.tsv")); o = {"batch": key.replace("smoke_", "")}
    for k in ("bam_bytes", "read_groups", "read_len_mode", "primary_reads", "nominal_depth", "seed", "native_secs", "d0p40_fraction", "d0p40_realised_depth", "d0p40_secs", "d0p29_fraction",
              "d0p29_realised_depth", "d0p29_secs", "native_counted", "d0p40_counted", "d0p29_counted", "native_offbin", "total_secs", "out_bytes"):
        o[k] = st.get(k)
    for t in ("native", "d0p40", "d0p29"):
        f = f"{d}/50.raw_read_counts.{t}.txt.gz"
        if os.path.exists(f): c = pd.read_csv(f, sep="\t").iloc[:, 4].values; o[f"{t}_noise"] = noise(c); o[f"{t}_median_bin"] = float(np.median(c[use.values])); prof[(key, t)] = c
    o.update(jobinfo(key)); res[key] = o; print(key, o)
# discovery reference (validated recount, native ~0.5x by the same nominal rule) and its 0.4x/0.29x
disc = {}
for d in sorted(glob.glob(f"{A}/disc_val/*"))[:6]:
    for t in ("native", "d0p40", "d0p29"):
        f = f"{d}/50.raw_read_counts.{t}.txt.gz"
        if os.path.exists(f): disc.setdefault(t, []).append(noise(pd.read_csv(f, sep="\t").iloc[:, 4].values))
    st = dict(l.rstrip("\n").split("\t", 1) for l in open(f"{d}/stats.tsv")); disc.setdefault("nominal", []).append(float(st["nominal_depth"])); disc.setdefault("counted", []).append(int(st["native_counted"]))
res["discovery_reference"] = {k: [round(x, 4) for x in v] for k, v in disc.items()}
json.dump(res, open(f"{RES}/smoke.json", "w"), indent=1)
# figure: one smoke sample (Batch2), native / 0.4x / 0.29x, counts per used bin, chromosomes shaded alternately
key = "smoke_Batch2" if ("smoke_Batch2", "native") in prof else sorted(k for k, _ in prof)[0]
chrom = B.chromosome.astype(str).values; x = np.arange(len(B)); ok = use.values
fig, ax = plt.subplots(3, 1, figsize=(11, 7.2), sharex=True, dpi=200)
for a, (t, lab) in zip(ax, [("native", "native depth"), ("d0p40", "downsampled to 0.4× nominal"), ("d0p29", "downsampled to 0.29× nominal")]):
    c = prof[(key, t)]; med = np.median(c[ok])
    for i, ch in enumerate([str(i) for i in range(1, 23)]):
        w = np.where(chrom == ch)[0]
        if i % 2 == 0: a.axvspan(w[0], w[-1], color="#EEEEEE", lw=0)
    a.scatter(x[ok], c[ok] / med, s=0.3, color="#2F6DB5", rasterized=True, lw=0)
    aut = np.where(np.isin(chrom, [str(i) for i in range(1, 23)]))[0]; a.set_xlim(aut[0], aut[-1]); a.set_ylim(0, 2.5); a.set_ylabel("count / median", fontsize=9); a.tick_params(labelsize=9)
    a.set_title(f"{lab}: {int(c[ok].sum()):,} reads in {ok.sum():,} bins, median {med:.0f} per bin", fontsize=10, loc="left")
mids = [np.where(chrom == str(i))[0].mean() for i in range(1, 23)]; ax[-1].set_xticks(mids); ax[-1].set_xticklabels([str(i) for i in range(1, 23)], fontsize=8)
ax[-1].set_xlabel("chromosome (hg38 50 kb discovery bins, QDNAseq 'use' bins, autosomes)", fontsize=9)
fig.suptitle("ACE-B smoke sample: binned read counts at three depths", fontsize=11); fig.tight_layout()
fig.savefig(f"{A}/figs/acq_smoke_binned_counts.png"); print("SMOKE SUMMARY DONE", key)

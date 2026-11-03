"""One-paper Fig. 1b example images (CPU only; the only step that reads slide pixels). Inputs, read-only: ART per-tile QC (killcoyne_mm/two_papers_ART/
qc_all.parquet, correct tile-centre positions) and the ART artefact flag (tp_art_main.flags, same thresholds), the L-IMG bags' npz (slide path, level,
tile size), horizons/samples.csv (pre-event, class, grade), QDNAseq 50 kb hg38 outputs next to set_C.csv 'raw'.
Outputs (OD = killcoyne_mm/one_paper_fig1/out): no sample ID, patient ID or date in any file name or file. The chosen sample's ID is written only to
OD/../selection_SECRET.txt (cluster only, never copied back).
  TASK=list  candidates.csv (cluster only; has IDs) + candidates_noid.txt (stats only) ranked by the rule below
  TASK=make  RANK=k (default 0): thumb.png (tile region of the slide, label area never included), tiles.csv (tile squares in thumbnail pixels + flags),
             kept_<i>.png (6 kept tiles, 224 px at level 2), cn.csv (genome-wide profile, 1 Mb medians of the 50 kb bins + segment values), meta.json
Rule (fixed before looking at any image): pre-event sample, one slide with 256 tiles; artefact share 5-20% (pre-event class means 8.6% and 15.4%: an ordinary
slide with visible artefact); at least 3 glass/background and 3 blur tiles; ranked by number of artefact types present (desc), then
progressor first, then share of the genome in segments with |log2 ratio| >= 0.15 (desc, so the profile shows changes)."""
import os, sys, json, glob, numpy as np, pandas as pd
T = "/mnt/scratche/slow/fmlab/zuberi01/phd/thesis"; M = T + "/feasibility/paper_plan/killcoyne_mm"; A = M + "/two_papers_ART"
W0 = M + "/one_paper_fig1"; OD = W0 + "/out"; os.makedirs(OD, exist_ok=True)
FLAG = dict(tis_min=0.15, line_d=0.50, ink=0.02, blur_q=0.05)          # = tp_art_main.FLAG (asserted below against its source)
src = open(T + "/scripts/paper_plan/tp_art_main.py").read(); assert "FLAG = dict(tis_min=0.15, line_d=0.50, ink=0.02, blur_q=0.05)" in src
def flags(Q):
    F = pd.DataFrame(index=Q.index); F["bg"] = Q.tissue.values < FLAG["tis_min"]; F["edge"] = ~F.bg & (Q.line_d.values >= FLAG["line_d"])
    F["pen"] = Q.ink.values > FLAG["ink"]; ok = ~F.bg & np.isfinite(Q.lapvar_t.values); lt = float(np.nanquantile(Q.lapvar_t.values[ok], FLAG["blur_q"]))
    F["blur"] = ~F.bg & (np.nan_to_num(Q.lapvar_t.values, nan=0.0) < lt); F["art"] = F.bg | F.edge | F.pen | F.blur; return F, lt
remap = lambda p: p.replace("/scratchc/", "/mnt/scratche/fast/") if isinstance(p, str) and p.startswith("/scratchc/") else p
def cn_table(raw):
    d = os.path.dirname(raw); cn = pd.read_csv(d + "/50.copy_number.txt", sep="\t"); sg = pd.read_csv(d + "/50.copy_number_segmented.txt", sep="\t")
    assert len(cn) == len(sg) and (cn.feature.values == sg.feature.values).all()
    D = pd.DataFrame({"chrom": cn.chromosome.astype(str).values, "start": cn.start.values.astype(float), "v": cn.iloc[:, 4].values.astype(float),
                      "s": sg.iloc[:, 4].values.astype(float)})
    return D[D.chrom.isin([str(i) for i in range(1, 23)]) & np.isfinite(D.v) & np.isfinite(D.s)].reset_index(drop=True)
TASK = os.environ["TASK"]
Q = pd.read_parquet(A + "/qc_all.parquet"); F, LT = flags(Q); Q = pd.concat([Q, F], axis=1)
S = pd.read_csv(M + "/horizons/samples.csv", dtype={"Sample": str}).set_index("Sample"); C = pd.read_csv(M + "/set_C.csv", dtype=str).set_index("Sample")
BI = pd.read_csv(M + "/bag_index.csv", dtype={"sample_id": str}).set_index("sample_id")
if TASK == "list":
    g = Q.groupby("sample"); T_ = pd.DataFrame({"n": g.size(), "nslides": g.npz.nunique(), **{c: g[c].sum() for c in ("art", "bg", "edge", "pen", "blur")}})
    T_ = T_.join(S[["pre", "y", "Pathology"]]); T_["share"] = T_.art / T_.n
    c = T_[(T_.pre.astype(bool)) & (T_.nslides == 1) & (T_.n == 256) & T_.share.between(0.05, 0.20) & (T_.bg >= 3) & (T_.blur >= 3)].copy()
    c["types"] = (c[["bg", "edge", "pen", "blur"]] > 0).sum(1)
    def gfrac(s):
        D = cn_table(C.loc[s, "raw"]); return float((D.s.abs() >= 0.15).mean()), float(np.median(D.v))
    c[["cn_changed", "cn_median"]] = [gfrac(s) for s in c.index]
    c = c.sort_values(["types", "y", "cn_changed"], ascending=False)
    c.to_csv(W0 + "/candidates.csv")
    pre = T_[T_.pre.astype(bool)]
    with open(OD + "/candidates_noid.txt", "w") as fh:
        fh.write(f"pre-event samples {len(pre)}; artefact share median {pre.share.median():.4f}, mean {pre.share.mean():.4f}; blur threshold {LT:.1f}\n")
        fh.write(c.reset_index(drop=True)[["y", "Pathology", "n", "share", "bg", "edge", "pen", "blur", "types", "cn_changed", "cn_median"]].to_string())
    print(open(OD + "/candidates_noid.txt").read())
elif TASK == "make":
    import openslide
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    c = pd.read_csv(W0 + "/candidates.csv", index_col=0, dtype={0: str}); k = int(os.environ.get("RANK", 0)); s = str(c.index[k])
    open(W0 + "/selection_SECRET.txt", "w").write(f"rank {k}: {s}\n")
    q = Q[Q["sample"] == s].sort_values("tile"); npz = q.npz.iloc[0]
    with np.load(npz, allow_pickle=True) as z: sp = remap(str(z["slide_path"])); lv = int(z["level"]); ts = int(z["tile_size"])
    sl = openslide.OpenSlide(sp); ds = float(sl.level_downsamples[lv]); mpp = float(sl.properties.get("openslide.mpp-x", "nan"))
    # tile region at level lv, one tile of margin; read at a coarser level so the thumbnail is about 2,400 px wide
    x0, y0 = q.x0.min() - ts, q.y0.min() - ts; x1, y1 = q.x0.max() + 2 * ts, q.y0.max() + 2 * ts
    Wl, Hl = sl.level_dimensions[lv]; x0, y0, x1, y1 = max(0, x0), max(0, y0), min(Wl, x1), min(Hl, y1)
    target = 2400.0; want = (x1 - x0) * ds / target; L2 = sl.get_best_level_for_downsample(want); d2 = float(sl.level_downsamples[L2])
    w2, h2 = int((x1 - x0) * ds / d2), int((y1 - y0) * ds / d2)
    im = sl.read_region((int(x0 * ds), int(y0 * ds)), L2, (w2, h2)).convert("RGB")
    sc = target / w2 if w2 > target else 1.0; im = im.resize((int(w2 * sc), int(h2 * sc)), Image.LANCZOS); im.save(OD + "/thumb.png")
    f = ds / d2 * sc                                                     # level-lv px -> thumbnail px
    tt = pd.DataFrame({"x": (q.x0.values - x0) * f, "y": (q.y0.values - y0) * f, "w": ts * f, "art": q.art.values, "bg": q.bg.values,
                       "edge": q.edge.values, "pen": q.pen.values, "blur": q.blur.values, "tissue": q.tissue.values.round(3)})
    tt.to_csv(OD + "/tiles.csv", index=False)
    rng = np.random.RandomState(20261103); kept = q[(~q.art) & (q.tissue > 0.6)]; pick = kept.iloc[rng.choice(len(kept), 6, replace=False)]
    for i, r in enumerate(pick.itertuples()):
        sl.read_region((int(r.x0 * ds), int(r.y0 * ds)), lv, (ts, ts)).convert("RGB").save(f"{OD}/kept_{i}.png")
    ex = {}
    for comp in ("bg", "edge", "pen", "blur"):                          # one removed example per type present (for checking by eye)
        m = q[q[comp]]
        if len(m): r = m.iloc[rng.randint(len(m))]; sl.read_region((int(r.x0 * ds), int(r.y0 * ds)), lv, (ts, ts)).convert("RGB").save(f"{OD}/removed_{comp}.png"); ex[comp] = int(len(m))
    sl.close()
    D = cn_table(C.loc[s, "raw"]); D["mb"] = (D.start // 1e6).astype(int)
    G = D.groupby(["chrom", "mb"], sort=False).agg(v=("v", "median"), s=("s", "median"), n=("v", "size")).reset_index()
    G["chrom"] = G.chrom.astype(int); G = G.sort_values(["chrom", "mb"]); G.to_csv(OD + "/cn.csv", index=False)
    meta = {"class": "progressor" if int(S.loc[s, "y"]) == 1 else "non-progressor", "grade": str(S.loc[s, "Pathology"]), "pre_event": bool(S.loc[s, "pre"]),
            "tiles": int(len(q)), "artefact_tiles": int(q.art.sum()), "by_type": {c_: int(q[c_].sum()) for c_ in ("bg", "edge", "pen", "blur")},
            "tile_size_px": ts, "level": lv, "level_um_per_px": round(mpp * ds, 3), "tile_um": round(mpp * ds * ts, 1), "thumb_um_per_px": round(mpp * d2 / sc, 2),
            "thumb_size": list(im.size), "blur_threshold": round(LT, 1), "cn_bins_50kb": int(len(D)), "cn_value": "QDNAseq copy_number (log2 ratio), 1 Mb medians",
            "cn_genome_changed_015": round(float((D.s.abs() >= 0.15).mean()), 3), "rank": k, "rule": __doc__.split("Rule")[1].strip()}
    json.dump(meta, open(OD + "/meta.json", "w"), indent=1); print(json.dumps(meta, indent=1))

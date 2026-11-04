"""Two papers, agent UNC2 (docs/two_papers_UNC2.md): tile-subset feature blocks for the tile-subset ensemble.
The clean tile set of each sample is ART's (tp_art_main.py flags(); < 32 clean tiles topped up to 32 by ART's stated rule; all of a sample's slides pooled).
K = 10 subsets of 32 tiles each, drawn at random without replacement from the sample's clean tiles, independently per subset (RandomState(20261103));
a sample with exactly 32 clean tiles gets the same 32 tiles in every subset. Block = mean UNI2-h embedding of the subset.
Smoke (asserted): the all-clean-tile mean rebuilt here equals ART's feats/clean.csv.gz.
Row-level output (cluster only): killcoyne_mm/two_papers_UNC2/feats/sub00..sub09.csv.gz and clean.csv.gz (copy of ART's block, for the refit smoke)."""
import os, sys, json, numpy as np, pandas as pd
PP = "/mnt/scratche/slow/fmlab/zuberi01/phd/thesis/scripts/paper_plan"; sys.path.insert(0, PP)
os.environ["TASK"] = "art_none"; _f = __file__; __file__ = PP + "/tp_art_main.py"; exec(compile(open(__file__).read(), __file__, "exec")); __file__ = _f   # definitions only
U2 = M + "/two_papers_UNC2"; os.makedirs(U2 + "/feats", exist_ok=True); K, NT, MINC = 10, 32, 32
def keep_of(bad, q):   # copied from tp_art_main.py TASK=feats
    clean = ~bad; nc = int(clean.sum()); keep = clean.copy()
    if nc < MINC:
        order = np.lexsort((-np.nan_to_num(q.lapvar_t.values), -q.tissue.values)); add = [i for i in order if not keep[i]][:MINC - nc]; keep[add] = True
    return keep
Q = qc_table(); F, lt = flags(Q); BI = pd.read_csv(M + "/bag_index.csv", dtype={"sample_id": str}).set_index("sample_id"); QI = Q.groupby("sample").indices
rng = np.random.RandomState(20261103); rows = {f"sub{i:02d}": [] for i in range(K)}; rows["clean"] = []; nkeep = []
for s in ids:
    ii = np.sort(QI[s]); q = Q.iloc[ii]; f = F.iloc[ii]; E_ = np.load(BI.loc[s, "npz_path"])["embeddings"].astype(np.float64); assert len(E_) == len(q) and (q.bag_pos.values == np.arange(len(q))).all()
    keep = np.where(keep_of(f.art.values, q))[0]; nkeep.append(len(keep)); rows["clean"].append(E_[keep].mean(0))
    for i in range(K): rows[f"sub{i:02d}"].append(E_[rng.choice(keep, NT, replace=False)].mean(0))
ART = pd.read_csv(M + "/two_papers_ART/feats/clean.csv.gz", dtype={"Sample": str}).set_index("Sample").reindex(ids).values
dmax = float(np.abs(np.vstack(rows["clean"]) - ART).max()); print("smoke clean rebuild max |d| vs ART clean.csv.gz", dmax, flush=True); assert dmax < 1e-6, dmax
for k, v in rows.items():
    X = pd.DataFrame(np.vstack(v), columns=[f"u{i}" for i in range(1536)]); X.insert(0, "Sample", ids); X.to_csv(f"{U2}/feats/{k}.csv.gz", index=False, float_format="%.8g")
nk = np.array(nkeep); PRE_ = PRE
info = {"smoke_clean_rebuild_max_abs_vs_ART": dmax, "K": K, "tiles_per_subset": NT, "seed": 20261103,
        "pre_event_clean_tiles_median": float(np.median(nk[PRE_])), "pre_event_samples_with_32_clean_tiles_or_fewer": int((nk[PRE_] <= NT).sum()),
        "expected_pairwise_tile_overlap_median": float(np.median(NT / nk[PRE_]))}
json.dump(info, open(U2 + "/feats/feats_info.json", "w"), indent=1); print("UNC2 FEATS DONE", json.dumps(info), flush=True)

"""OCCAMS fusion SECOND PASS (redesigned after weak first-pass 2026-08-14).

Fixes vs v1: (1) properly censored endpoint from master CSV (vital_status /
deceased_survival_days / last_known_survival_days; early-censored excluded);
(2) tile-level aggregation mean+max+std over per-tile UNI2 features (not plain
mean-pool); (3) richer genomics: TP53 flags + ploidy + WGD + HER2/CCNE1 amp.
Same harness: 5x5 patient-level CV, shuffled controls, paired bootstrap.
"""
import os, glob, json, warnings, numpy as np, pandas as pd
warnings.filterwarnings("ignore")
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, brier_score_loss
import h5py

BASE = "/mnt/scratche/slow/fmlab/datasets/imaging/occams/wsi_data"
FEAT = BASE + "/slides/features/20x_224px/features_uni_v2"
TSV = BASE + "/genomics/clinical_data_wgs_cases_therapy_tp53status_ploidy_wgd_status.tsv"
AMP = BASE + "/genomics/allcases_her2_and_ccne1_amplification_status.tsv"
MASTER = "/home/zuberi01/occams_work/occams_master_20260511.csv"
OUT = os.environ.get("OUTDIR", ".")
CUT_DAYS = 730

def norm_id(s): return str(s).strip().upper().replace("/", "-")

# --- endpoint from master (proper censoring) ---
mast = pd.read_csv(MASTER, dtype=str, low_memory=False)
mast["cid"] = mast["occams_id"].map(norm_id)
dsd = pd.to_numeric(mast["deceased_survival_days"], errors="coerce")
lkd = pd.to_numeric(mast["last_known_survival_days"], errors="coerce")
dead = mast["date_death"].notna() & (mast["date_death"].astype(str).str.strip() != "") | dsd.notna()
surv = dsd.where(dead, lkd)
y_map, excluded = {}, 0
for cid, is_dead, s in zip(mast["cid"], dead, surv):
    if pd.isna(s): continue
    if s >= CUT_DAYS: y_map[cid] = 1
    elif is_dead: y_map[cid] = 0
    else: excluded += 1  # censored alive before cutoff -> exclude
print(f"master rows={len(mast)} labelled={len(y_map)} early-censored-excluded={excluded}")

# --- histology: mean+max+std over tile features, RES slide preferred ---
files = glob.glob(FEAT + "/*.h5")
bycase = {}
for f in files:
    c = norm_id(os.path.basename(f).split("_")[0])
    bycase.setdefault(c, []).append(f)
H_map = {}
for c, fs in bycase.items():
    pick = sorted([f for f in fs if "_RES" in f] or fs)[0]
    try:
        with h5py.File(pick, "r") as h: F = np.asarray(h["features"])
        if len(F) < 5: continue
        H_map[c] = np.concatenate([F.mean(0), F.max(0), F.std(0)])
    except Exception as e:
        print("skip", pick, e)
print(f"histology cases: {len(H_map)}")

# --- genomics ---
th = pd.read_csv(TSV, sep="\t", dtype=str)
th["cid"] = th["OCCAMS_ID"].map(norm_id)
th = th.drop_duplicates("cid").set_index("cid")
amp = pd.read_csv(AMP, sep="\t", dtype=str)
amp["cid"] = amp["CASE_ID"].map(norm_id)
amp = amp.drop_duplicates("cid").set_index("cid")
def fl(series): return series.astype(str).str.strip().str.lower().isin(("1","true","yes","y")).astype(float)
def amp_fl(series): return series.astype(str).str.strip().str.lower().eq("yes").astype(float)

cases = sorted(set(H_map) & set(y_map) & set(th.index))
sub = th.loc[cases]
her2 = amp["HER2_FMlab_amplification_status"].reindex(cases).astype(str).str.lower().eq("yes").astype(float)
ccne1 = amp["CCNE1_FMlab_amplification_status"].reindex(cases).astype(str).str.lower().eq("yes").astype(float)
G = np.column_stack([
    fl(sub["TP53_SNV"]), fl(sub["TP53_indel"]), fl(sub["TP53_deletion"]), fl(sub["TP53_knockout"]),
    pd.to_numeric(sub["ploidy"], errors="coerce").fillna(2.0), fl(sub["WGD"]),
    her2.values, ccne1.values,
])
G = np.nan_to_num(G, nan=0.0)
H = np.vstack([H_map[c] for c in cases])
y = np.array([y_map[c] for c in cases])
print(f"final n={len(cases)} pos={int(y.sum())} H={H.shape} G={G.shape}")

def oof(Xi, yy, seed, pca=None):
    o = np.zeros(len(yy))
    steps = [("s", StandardScaler())]
    if pca: steps.append(("p", PCA(min(pca, Xi.shape[1], len(yy) - 1))))
    steps.append(("l", LogisticRegression(C=0.5, class_weight="balanced", max_iter=4000)))
    for tr, te in StratifiedKFold(5, shuffle=True, random_state=seed).split(Xi, yy):
        p = Pipeline(steps); p.fit(Xi[tr], yy[tr]); o[te] = p.predict_proba(Xi[te])[:, 1]
    return o

Hp = PCA(64).fit_transform(StandardScaler().fit_transform(H))
arms = {"hist_only": (H, 64), "gen_only": (G, None),
        "early_fusion": (np.column_stack([Hp, StandardScaler().fit_transform(G)]), None)}
res, oofs = {}, {}
for name, (Xi, pca) in arms.items():
    os_ = [oof(Xi, y, s, pca) for s in range(5)]
    oofs[name] = np.mean(os_, 0)
    sh = []
    for s in range(5):
        yp = np.random.RandomState(s).permutation(y)
        sh.append(roc_auc_score(yp, oof(Xi, yp, s, pca)))
    res[name] = {"auc": float(np.mean([roc_auc_score(y, o) for o in os_])),
                 "auc_sd": float(np.std([roc_auc_score(y, o) for o in os_])),
                 "brier": float(np.mean([brier_score_loss(y, o) for o in os_])),
                 "shuffled_auc": float(np.mean(sh))}
    print(name, res[name])
oofs["late_fusion"] = (oofs["hist_only"] + oofs["gen_only"]) / 2
res["late_fusion"] = {"auc": float(roc_auc_score(y, oofs["late_fusion"])),
                      "brier": float(brier_score_loss(y, oofs["late_fusion"]))}
print("late_fusion", res["late_fusion"])
rng = np.random.RandomState(0)
for fus in ("late_fusion", "early_fusion"):
    dl = []
    for _ in range(2000):
        b = rng.randint(0, len(y), len(y))
        if len(set(y[b])) < 2: continue
        dl.append(roc_auc_score(y[b], oofs[fus][b]) - roc_auc_score(y[b], oofs["hist_only"][b]))
    res[fus]["delta_auc_vs_hist"] = {"mean": float(np.mean(dl)),
                                     "ci": [float(np.percentile(dl, 2.5)), float(np.percentile(dl, 97.5))]}
    print(fus, "delta:", res[fus]["delta_auc_vs_hist"])
res["_meta"] = {"n": len(cases), "pos": int(y.sum()), "endpoint": f"OS>={CUT_DAYS}d censored-aware",
                "early_censored_excluded": int(excluded), "pooling": "mean+max+std tile-level",
                "genomics": "TP53x4+ploidy+WGD+HER2amp+CCNE1amp"}
json.dump(res, open(os.path.join(OUT, "results.json"), "w"), indent=2)
print("wrote results.json")

"""Two papers, agent UNC2 (docs/two_papers_UNC2.md): follow-up to UNC. Is disagreement across GENUINELY DIFFERENT H&E models (other foundation models,
scales, poolings, objectives, ERIN transfer; or the same recipe on different tile subsets) an uncertainty signal for choosing whom to sequence, beyond
the H&E score itself? Every member is a stored (or new, tp_unc2_refit.R) held-out prediction in the stored 10 x 10 patient-grouped folds (asserted).
TASK = auc            member AUROCs (smoke: clean L-IMG 0.811, stored L-IMG 0.847, H-optimus-0 L2 0.805) + ensemble-mean AUROC vs clean L-IMG
                      (tp_p1b_main.py fsa / hblock, 2,000-draw patient bootstrap, paired)
TASK = dis SET=fm|all|tiles SCALE=z|rank|prob
                      UNC's analyses (tp_unc_main.py executed up to its bootstrap: state, R49 smoke, cut-offs, helpers) with D = SD across the SET's
                      members of the held-out score in the same repeat; members put on a common scale within each (repeat, held-out fold):
                      z = z-score of the log-odds (endoscopy: mean sample logit), rank = within-fold percentile rank, prob = raw probability (no rescaling;
                      Cox linear predictors excluded). Error = clean L-IMG call at the fold's training 90%-sensitivity cut-off (as UNC).
UNC2_NB=k: smoke (k draws, JSON aside). Aggregates only -> results/paper_final/two_papers_UNC2/."""
import os, sys, json, glob, time, numpy as np, pandas as pd
from scipy.stats import rankdata, spearmanr
THESIS = "/mnt/scratche/slow/fmlab/zuberi01/phd/thesis"; PP = THESIS + "/scripts/paper_plan"; sys.path.insert(0, PP)
KM = THESIS + "/feasibility/paper_plan/killcoyne_mm"; U2 = KM + "/two_papers_UNC2"; CODE = os.path.dirname(os.path.abspath(__file__))
t0 = time.time(); TASK2 = os.environ["TASK"]; NB2 = int(os.environ.get("UNC2_NB", "2000"))
OUT2 = U2 + "/smoke_json" if os.environ.get("UNC2_NB") else THESIS + "/results/paper_final/two_papers_UNC2"; os.makedirs(OUT2, exist_ok=True)
# ------------------------------------------------------------------ members (fixed before any result was seen, except the pooling AUROC >= 0.75 filter: see doc)
A_FM = [("clean L-IMG: UNI2-h L2, clean tiles", "art:clean"), ("UNI2-h L2, all tiles (stored L-IMG)", "e3:base"), ("UNI2-h L1", "e3:u2l1_mean"),
        ("Prov-GigaPath L1", "e3:gpl1_mean"), ("Prov-GigaPath L2", "e3:gpl2_mean"), ("Prov-GigaPath L3", "e3:gpl3_mean"), ("Virchow2 L2", "e3:v2l2_mean"),
        ("H-optimus-0 L2", "sr:hoptimus0"), ("H-optimus-0 20x", "e3:ho20_mean"), ("Virchow2 20x", "e3:v220_mean"), ("CONCH v1.5 20x", "e3:co20_mean"),
        ("CTransPath 20x", "e3:ct20_mean"), ("MUSK 20x", "e3:mu20_mean")]
A_EXTRA = [("UNI2-h L2, quantile pooling", "e3:u2l2_q3"), ("UNI2-h L2, mean+SD pooling", "e3:u2l2_meansd"), ("tile-score pooling top-32", "e3:base_tptop32"),
           ("tile-score pooling top-16", "e3:base_tptop16"), ("tile-score pooling top-8", "e3:base_tptop8"), ("Cox, extended follow-up (E4)", "e4:coxx_img"),
           ("5-year horizon (E4)", "e4:h5_img"), ("certainty-weighted (E4)", "e4:wt_img"), ("ERIN LGD+ transfer (E5)", "erin:logit_lgd")]
SUB = [(f"tile subset {i + 1} (32 clean tiles)", f"u2:sub{i:02d}") for i in range(10)]
SETS = {"fm": A_FM, "all": A_FM + A_EXTRA, "tiles": SUB}
lgc = lambda p: np.log(np.clip(p, 1e-6, 1 - 1e-6) / (1 - np.clip(p, 1e-6, 1 - 1e-6))); sgm = lambda z: 1 / (1 + np.exp(-z))
def member(key, ids_, FO_):
    """-> (Z: n x 10 held-out log-odds or linear predictor, P: n x 10 probability or None). Folds asserted equal to the stored folds."""
    src, nm = key.split(":"); R = list(range(1, 11))
    if src == "erin":
        SS = pd.read_csv(KM + "/explore_E5/sample_slides.csv", dtype=str); SC = pd.read_csv(KM + "/explore_E5/erin_scores_slides.csv").set_index("h5")
        v = SS.assign(v=SS.h5.map(SC[nm])).groupby("cnv").v.max(); z = pd.Series(ids_).map(v).values.astype(float); Z = np.repeat(z[:, None], 10, 1); return Z, sgm(Z)
    if src == "sr": fo = [f"{KM}/scanner_robustness/cv/cv_{r}_{nm}.csv" for r in R]
    else: fo = sorted(glob.glob({"e3": f"{KM}/explore_E3/refit/{nm}", "art": f"{KM}/two_papers_ART/refit/{nm}", "u2": f"{U2}/refit/{nm}", "e4": f"{KM}/explore_E4/fits/{nm}"}[src] + "/outer_rep_*.csv"))
    assert len(fo) == 10, (key, len(fo)); D = pd.concat([pd.read_csv(f, dtype={"Sample": str}) for f in fo]); assert not D.duplicated(["Sample", "rep"]).any(), key
    pv = lambda c: D.pivot_table(index="Sample", columns="rep", values=c, dropna=False).reindex(ids_)[R].values
    assert (pv("fold").astype(int) == FO_).all(), ("folds differ from the stored folds", key); X = pv("pred")
    if nm.startswith("cox"): return X, None   # E4 Cox: linear predictor z-scored on the model's training rows (no probability)
    return lgc(X), X
# ================================================================== TASK = auc
if TASK2 == "auc":
    os.environ["TASK"] = "unc2_none"; _f = __file__; __file__ = PP + "/tp_p1b_main.py"; exec(compile(open(__file__).read(), __file__, "exec")); __file__ = _f   # definitions only
    ALL = {k: (lab, ) + member(k, ids, FO0) for lab, k in A_FM + A_EXTRA + SUB}
    rows = ROWS; ev = EV0
    single = {k: {"label": v[0], "auroc_sample_fsa": r3(fsa(v[2] if v[2] is not None else v[1], rows, ev))} for k, v in ALL.items()}
    sm = {"clean L-IMG 0.811": single["art:clean"]["auroc_sample_fsa"], "stored L-IMG 0.847": single["e3:base"]["auroc_sample_fsa"], "H-optimus-0 L2 0.805": single["sr:hoptimus0"]["auroc_sample_fsa"]}
    chk = bool(abs(sm["clean L-IMG 0.811"] - 0.811) < 0.0006 and abs(sm["stored L-IMG 0.847"] - 0.847) < 0.0006 and abs(sm["H-optimus-0 L2 0.805"] - 0.805) < 0.0006)
    print("smoke", sm, chk, flush=True); assert chk, sm
    def zfold(Z):   # within (repeat, held-out fold) z-score over the fold's held-out pre-event samples (label-free)
        out = np.full_like(Z, np.nan)
        for j in range(10):
            for k in range(1, 11):
                m = (FO0[:, j] == k) & PRE; v = Z[m, j]; out[m, j] = (v - v.mean()) / v.std()
        return out
    O = {"clean L-IMG": ALL["art:clean"][2]}
    for s, mem in SETS.items():
        ks = [k for _, k in mem]; O[f"ensemble {s}: mean probability"] = np.mean([ALL[k][2] for k in ks if ALL[k][2] is not None], 0)
        O[f"ensemble {s}: mean within-fold z log-odds"] = np.mean([zfold(ALL[k][1]) for k in ks], 0)
    O["stored L-IMG (all tiles)"] = ALL["e3:base"][2]
    bb = boots(rows, nb=NB2); R_, obs, B = hblock(O, rows, bb, keep=True)
    R_["minus_clean_L_IMG"] = {m: dstat(obs[m] - obs["clean L-IMG"], B[m] - B["clean L-IMG"]) for m in O if m != "clean L-IMG"}
    R_["minus_stored_L_IMG"] = {m: dstat(obs[m] - obs["stored L-IMG (all tiles)"], B[m] - B["stored L-IMG (all tiles)"]) for m in O if m.startswith("ensemble")}
    res = {"task": "auc", "agent": "UNC2", "smoke": sm, "smoke_ok": chk, "members": single, "sets": {s: [k for _, k in m] for s, m in SETS.items()}, "ensemble_auroc": R_, "draws": len(bb),
           "note": "fold-stratified sample AUROC (fsa) on the 571 pre-event samples, repeat mean; paired patient bootstrap (tp_p1b_main boots, RandomState(0)); ensembles: mean of member "
                   "probabilities (Cox members excluded) or mean of within-fold z-scored log-odds; exploratory (adds to the image-model search count)", "runtime_s": round(time.time() - t0)}
    json.dump(res, open(f"{OUT2}/auc.json", "w"), indent=1, default=lambda x: x.item() if hasattr(x, "item") else str(x)); print("UNC2 DONE auc", res["runtime_s"], flush=True); sys.exit(0)
# ================================================================== TASK = dis: UNC's state and helpers (tp_unc_main.py up to its bootstrap section, unchanged)
SET, SCALE = os.environ["SET"], os.environ["SCALE"]
_s = open(CODE + "/tp_unc_main.py").read(); _s = _s[:_s.index("# ------------------------------------------------------------------ observed + patient bootstrap")]
os.environ["TASK"] = "unc"; _f = __file__; __file__ = CODE + "/tp_unc_main.py"; exec(compile(_s, __file__, "exec")); __file__ = _f
EF = S["EF"]; MEM = [(lab, k) for lab, k in SETS[SET]]; ZM = {}; PM = {}
for lab, k in MEM: ZM[k], PM[k] = member(k, ids, S["FO"])
if SCALE == "prob": MEM = [(lab, k) for lab, k in MEM if PM[k] is not None]
def emean(Zc): return np.nanmean(np.where(MSK, Zc[np.where(MSK, IDX, 0)], np.nan), 1)   # endoscopy mean of a per-sample column (pre-event samples)
EZ = {k: np.stack([emean(ZM[k][:, j]) for j in range(10)], 1) for _, k in MEM}        # endoscopy mean log-odds per member (NEND x 10)
if "art:clean" in EZ:   # smoke: the clean member's endoscopy mean logit equals UNC's state ZI (up to the 1e-6 tie-break of state_v)
    d0 = float(np.abs(EZ["art:clean"] - ZI).max()); print("smoke clean member vs state ZI max |d|", d0, flush=True); assert d0 < 1e-3, d0
else: d0 = None
FOs = S["FO"][sidx]
def common(X, groups):
    """X: rows x 10 for one member; groups(j) -> list of row masks (held-out folds of repeat j); returns the member on the common scale"""
    out = np.full_like(X, np.nan, dtype=float)
    for j in range(10):
        for m in groups(j):
            v = X[m, j]
            out[m, j] = (v - v.mean()) / v.std() if SCALE == "z" else (rankdata(v) / len(v) if SCALE == "rank" else v)
    return out
ge = lambda j: [EF[:, j] == k for k in range(1, 11)]; gs = lambda j: [FOs[:, j] == k for k in range(1, 11)]
src_e = {k: (sgm(EZ[k]) if SCALE == "prob" else EZ[k]) for _, k in MEM}; src_s = {k: (sgm(ZM[k][sidx]) if SCALE == "prob" else ZM[k][sidx]) for _, k in MEM}
CE = np.stack([common(src_e[k], ge) for _, k in MEM], 2); CSm = np.stack([common(src_s[k], gs) for _, k in MEM], 2)   # rows x 10 x members
DE2 = CE.std(2, ddof=1); DS2 = CSm.std(2, ddof=1)
# ensemble mean on the z scale (always z, whatever SCALE): extra score control
def zc(X, groups):
    out = np.full_like(X, np.nan, dtype=float)
    for j in range(10):
        for m in groups(j): v = X[m, j]; out[m, j] = (v - v.mean()) / v.std()
    return out
EME = np.mean([zc(EZ[k], ge) for _, k in MEM], 0); EMS = np.mean([zc(ZM[k][sidx], gs) for _, k in MEM], 0)
HEc = -(sg(ZI) * np.log(sg(ZI)) + (1 - sg(ZI)) * np.log(1 - sg(ZI))); pS = sg(ZS[sidx]); HSc = -(pS * np.log(pS) + (1 - pS) * np.log(1 - pS))   # cell-level entropy (clean L-IMG)
DQ2 = np.full((NEND, 10), np.nan)
for j in range(10):   # label-free: 75th percentile of D over the fold's training endoscopies (their own held-out D in the same repeat)
    for k in range(1, 11): te = EF[:, j] == k; DQ2[te, j] = np.percentile(DE2[~te, j], 75)
# ------------------------------------------------------------------ UNC's analyse / step45 with D varying by repeat (rows x 10) and a second, stricter score control
def analyse2(Dv, Mv, Hv, Ev, SGv, EMv, cl, rows, full=True):
    G_ = SGv[rows].ravel(); D_ = Dv[rows]; M_ = Mv[rows]; H_ = Hv[rows]; E_ = Ev[rows].astype(int); c_ = cl[rows]; o = {}
    o["spearman_D_M"] = spearmanr(D_.ravel(), M_.ravel())[0]; o["spearman_D_entropy"] = spearmanr(D_.ravel(), H_.ravel())[0]
    o["spearman_D_abs_ensemble_mean"] = spearmanr(D_.ravel(), np.abs(EMv[rows]).ravel())[0]; o["error_rate"] = E_.mean()
    o["auroc_D_for_error"] = auc_rep(D_, E_); o["auroc_negM_for_error"] = auc_rep(-M_, E_); o["auroc_entropy_for_error"] = auc_rep(H_, E_)
    yv = E_.ravel().astype(float); Ms = stdz(M_.ravel()); Ds = stdz(D_.ravel()); cc = np.repeat(c_, 10)
    b1, ll1, Xd1, _ = logit_fit(Ms[:, None], yv); b2, ll2, Xd2, _ = logit_fit(np.column_stack([Ms, Ds]), yv)
    o["apparent_auroc_gain_over_M"] = roc_auc_score(yv, Xd2 @ b2) - roc_auc_score(yv, Xd1 @ b1); o["beta_D_per_sd_given_M"] = b2[2]
    if full: o["beta_D_given_M_cluster_wald_p"] = cluster_wald(np.column_stack([Ms, Ds]), yv, cc, 2)[1]
    o["cv_auroc_M"] = cv_auc(Ms[:, None], yv, cc); o["cv_auroc_M_plus_D"] = cv_auc(np.column_stack([Ms, Ds]), yv, cc); o["cv_auroc_gain_over_M"] = o["cv_auroc_M_plus_D"] - o["cv_auroc_M"]
    sd_ = (G_ >= 0).astype(float); Gs = G_ / G_.std(); X0 = np.column_stack([Gs, Gs ** 2, sd_, sd_ * Gs, sd_ * Gs ** 2, stdz(H_.ravel())])   # UNC's flexible control (cell entropy)
    Em = stdz(EMv[rows].ravel()); X1 = np.column_stack([X0, Em, Em ** 2])                                                               # + ensemble mean (quadratic)
    for nm, X in (("flex", X0), ("flex_plus_ensemble_mean", X1)):
        o[f"cv_auroc_{nm}"] = cv_auc(X, yv, cc); o[f"cv_auroc_{nm}_plus_D"] = cv_auc(np.column_stack([X, Ds]), yv, cc); o[f"cv_auroc_gain_over_{nm}"] = o[f"cv_auroc_{nm}_plus_D"] - o[f"cv_auroc_{nm}"]
        bb_, llA = logit_fit(X, yv)[:2]; bB, llB = logit_fit(np.column_stack([X, Ds]), yv)[:2]; o[f"beta_D_per_sd_given_{nm}"] = bB[-1]
        o[f"apparent_auroc_gain_over_{nm}"] = roc_auc_score(yv, np.column_stack([np.ones(len(yv)), X, Ds]) @ bB) - roc_auc_score(yv, np.column_stack([np.ones(len(yv)), X]) @ bb_)
        if full: o[f"beta_D_given_{nm}_cluster_wald_p"] = cluster_wald(np.column_stack([X, Ds]), yv, cc, X.shape[1] + 1)[1]
    return o
def step45_2(rows, DV, DQV):
    lab = (elab[rows] == 1)[:, None]; B = BAND[rows]; conf = B != 1; call = B == 2; wrong = conf & (call != lab); hiD = DV[rows] >= DQV[rows]; o = {}
    cnv_ok = (ZC[rows] >= CC[rows]) == lab; late_ok = (ZL[rows] >= CL[rows]) == lab
    for nm, g in (("confident_topD", conf & hiD), ("confident_restD", conf & ~hiD)):
        o[nm] = {"n": g.sum(0).mean(), "wrong": (g & wrong).sum(0).mean(), "wrong_rate": (g & wrong).sum() / max(g.sum(), 1),
                 "cnv_fixes": (g & wrong & cnv_ok).sum(0).mean(), "late_fixes": (g & wrong & late_ok).sum(0).mean(),
                 "cnv_breaks_correct": (g & ~wrong & ~cnv_ok).sum(0).mean(), "late_breaks_correct": (g & ~wrong & ~late_ok).sum(0).mean()}
        for m in ("cnv", "late"): o[nm][f"{m}_net_per_100"] = 100 * (o[nm][f"{m}_fixes"] - o[nm][f"{m}_breaks_correct"]) / max(o[nm]["n"], 1e-9)
    o["wrong_rate_topD_minus_rest"] = o["confident_topD"]["wrong_rate"] - o["confident_restD"]["wrong_rate"]
    he = ZI[rows] >= CI[rows]; bud = (B == 1).sum(0); Dr = DV[rows]; selD = np.zeros_like(he)
    for j in range(10): selD[np.argsort(-Dr[:, j], kind="stable")[:bud[j]], j] = True
    for nm, sel in (("band", B == 1), ("D", selD)):
        fin = np.where(sel, SEQC[rows], he)
        o[f"budget_{nm}"] = {"sequenced": sel.sum(0).mean(), "np_corrected": (sel & he & ~SEQC[rows] & ~lab).sum(0).mean(), "progressor_lost": (sel & he & ~SEQC[rows] & lab).sum(0).mean(),
                             "progressor_rescued": (sel & ~he & SEQC[rows] & lab).sum(0).mean(), "np_newly_flagged": (sel & ~he & SEQC[rows] & ~lab).sum(0).mean(),
                             "np_flagged_final": (fin & ~lab).sum(0).mean(), "progressor_flagged_final": (fin & lab).sum(0).mean(), "overlap_with_band": (sel & (B == 1)).sum(0).mean()}
    o["budget_D_minus_band_np_flagged"] = o["budget_D"]["np_flagged_final"] - o["budget_band"]["np_flagged_final"]
    o["budget_D_minus_band_progressor_flagged"] = o["budget_D"]["progressor_flagged_final"] - o["budget_band"]["progressor_flagged_final"]
    o["budget_D_minus_band_np_corrected"] = o["budget_D"]["np_corrected"] - o["budget_band"]["np_corrected"]
    o["budget_D_minus_band_progressor_lost"] = o["budget_D"]["progressor_lost"] - o["budget_band"]["progressor_lost"]
    return o
# ------------------------------------------------------------------ observed + patient bootstrap (UNC's construction)
eall = np.arange(NEND); sall = np.arange(len(sidx))
ob_e = analyse2(DE2, ME, HEc, ERR, SGE, EME, pidx, eall); ob_s = analyse2(DS2, MS, HSc, ERRS, SGS, EMS, spat, sall); ob_45 = step45_2(eall, DE2, DQ2)
extra = {"spearman_D_vs_UNC_repeat_SD_endoscopy": rr(spearmanr(DE2.mean(1), DE)[0]), "spearman_D_vs_UNC_repeat_SD_sample": rr(spearmanr(DS2.mean(1), DS)[0]),
         "D_endoscopy_median": rr(np.median(DE2)), "D_endoscopy_iqr": [rr(np.percentile(DE2, 25)), rr(np.percentile(DE2, 75))],
         "mean_pairwise_spearman_between_members_endoscopy": rr(np.nanmean([np.mean([spearmanr(CE[:, j, a], CE[:, j, b])[0] for j in range(10)]) for a in range(len(MEM)) for b in range(a + 1, len(MEM))]))}
rng_ = np.random.RandomState(0); Dd = []
while len(Dd) < NB2:
    mm = np.bincount(rng_.choice(P_, P_), minlength=P_)
    if (mm * plab).sum() > 0 and (mm * (1 - plab)).sum() > 0: Dd.append(mm)
EP = [np.where(pidx == p)[0] for p in range(P_)]; SP = [np.where(spat == p)[0] for p in range(P_)]; BE, BS, B45 = [], [], []
for b, mm in enumerate(Dd):
    pr = np.repeat(np.arange(P_), mm); re_ = np.concatenate([EP[p] for p in pr]); rs_ = np.concatenate([SP[p] for p in pr])
    cid_e = np.concatenate([np.full(len(EP[p]), i) for i, p in enumerate(pr)]); cid_s = np.concatenate([np.full(len(SP[p]), i) for i, p in enumerate(pr)])
    BE.append(flat(analyse2(DE2[re_], ME[re_], HEc[re_], ERR[re_], SGE[re_], EME[re_], cid_e, np.arange(len(re_)), full=False)))
    BS.append(flat(analyse2(DS2[rs_], MS[rs_], HSc[rs_], ERRS[rs_], SGS[rs_], EMS[rs_], cid_s, np.arange(len(rs_)), full=False)))
    B45.append(flat(step45_2(re_, DE2, DQ2)))
    if b % 200 == 0: print("draw", b, round(time.time() - t0), "s", flush=True)
def summ(ob, BB):   # copied from tp_unc_main.py
    o = {}
    for k, v in flat(ob).items():
        bv = np.array([x[k] for x in BB if k in x], float); bv = bv[np.isfinite(bv)]
        o[k] = {"value": rr(v), "ci95": [rr(np.percentile(bv, 2.5)), rr(np.percentile(bv, 97.5))]} if len(bv) else {"value": rr(v)}
    return o
CNT = ("n", "wrong", "cnv_fixes", "late_fixes", "cnv_breaks_correct", "late_breaks_correct", "np_corrected", "progressor_lost", "progressor_rescued", "np_newly_flagged")
def mask5(d):
    for k, v in d.items():
        if k.split(".")[-1] in CNT and isinstance(v.get("value"), float) and v["value"] < 5: d[k] = {"value": "<5"}
    return d
res = {"task": "dis", "agent": "UNC2", "set": SET, "scale": SCALE, "members": [lab for lab, _ in MEM], "n_members": len(MEM), "draws": len(Dd),
       "smoke_R49_mean_logit_gate_clean": smoke, "smoke_clean_member_vs_state_max_abs": d0, "extra": extra,
       "endoscopy_steps1to3": summ(ob_e, BE), "sample_steps1to3": summ(ob_s, BS), "endoscopy_steps4to5": mask5(summ(ob_45, B45)), "runtime_s": round(time.time() - t0),
       "note": ("D = SD across the set's members of the held-out score in the same repeat, after putting each member on a common scale within each (repeat, held-out fold): "
                "z = z-score of log-odds (endoscopy: mean sample logit), rank = within-fold percentile rank, prob = raw probability. Errors, M, cut-offs, band, CNV/LATE fixes, "
                "budget rule exactly as UNC (clean L-IMG, fold training 90%-sensitivity cut-off, R49 mean-logit gate). Flexible control = UNC's piecewise quadratic in "
                "(log-odds - cut-off) + cell entropy of the clean L-IMG probability; stricter control adds the ensemble mean (z scale) and its square. "
                "Repeat-mean counts; patient bootstrap RandomState(0); cluster Wald p with patient clusters; CV AUROC = 5-fold patient-grouped held-out")}
json.dump(res, open(f"{OUT2}/dis_{SET}_{SCALE}.json", "w"), indent=1, default=lambda x: x.item() if hasattr(x, "item") else str(x)); print("UNC2 DONE dis", SET, SCALE, res["runtime_s"], flush=True)

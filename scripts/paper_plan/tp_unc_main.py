"""Two papers, agent UNC (docs/two_papers_UNC.md): quick signal test. Is ensemble disagreement (SD of the 10 held-out clean-tile L-IMG log-odds,
one per repeat of the 10x10 patient-grouped CV) an uncertainty signal for choosing whom to sequence, beyond the H&E score itself?
No model is trained. The state is built by executing tp_art_gate.py (definitions only: ex_e9_frontier.py -> rv9_falseflags.py, E3 helpers) and its
state_v("ml", "clean"): endoscopy score = mean sample logit of the ART clean-tile refit, R49 mean-logit gate cut-offs (t_low, c*, t_seq) re-derived
on each outer fold's training patients (inner out-of-fold predictions). Smoke: R49 (mean-logit gate, clean) must reproduce ART gate.json 31.1 / 32.3.
Cut-off for "H&E call" and for M: each fold's training 90%-sensitivity cut-off (training endoscopies / training pre-event samples, inner OOF),
the same rule for L-CNV and L-LATE (their own cut-offs). Units: endoscopy (or sample) x repeat, metrics per repeat then repeat-mean.
Patient bootstrap: rv8 pdraws construction, RandomState(0), 2,000 draws (rows physically resampled per patient).
Aggregates only -> results/paper_final/two_papers_UNC/unc.json. UNC_NB=k: smoke (k draws, JSON aside)."""
import os, sys, json, time, numpy as np, pandas as pd
from sklearn.metrics import roc_auc_score
from scipy.stats import spearmanr, chi2, norm
THESIS = "/mnt/scratche/slow/fmlab/zuberi01/phd/thesis"; PP = THESIS + "/scripts/paper_plan"; sys.path.insert(0, PP)
t00 = time.time(); RTASK = os.environ.get("TASK", "unc"); os.environ["TASK"] = "tpunc_import"
_fs = __file__; __file__ = PP + "/tp_art_gate.py"; exec(compile(open(__file__).read(), __file__, "exec")); __file__ = _fs   # TASK != gate: definitions only
OUTU = T + "/results/paper_final/two_papers_UNC"; NBU = 2000
if os.environ.get("UNC_NB"): NBU = int(os.environ["UNC_NB"]); OUTU = M + "/two_papers_UNC/smoke_json"
os.makedirs(OUTU, exist_ok=True)
rr = lambda v, d=3: None if v is None or not np.isfinite(v) else round(float(v), d)
def cut90(pos): s = np.sort(pos)[::-1]; return s[int(np.ceil(0.9 * len(s))) - 1]   # largest threshold keeping >= 90% sensitivity (score >= cut positive)
# ------------------------------------------------------------------ state (clean L-IMG, mean-logit endoscopy score)
S, ST, INFO = state_v("ml", "clean"); NEND = S["E"]; elab = S["elab"].astype(int); pidx = S["pidx"]; P_ = S["P_"]; plab = S["plab"]; es = S["es"]
RFC = read_refit("clean"); popm = S["popm"]
IDX, MSK = ST["IDX"], ST["MSK"]
def emean_logit(x): Z = np.where(MSK, lg_(x[np.where(MSK, IDX, 0)]), np.nan); return np.nanmean(Z, 1)
def build():
    ZI = np.full((NEND, 10), np.nan); ZC = ZI.copy(); ZL = ZI.copy(); BAND = np.zeros((NEND, 10), int); FL49 = np.zeros((NEND, 10), bool); NS49 = np.zeros((NEND, 10), int)
    CI = ZI.copy(); CC = ZI.copy(); CL = ZI.copy(); SEQC = np.zeros((NEND, 10), bool)   # per-fold cut-offs broadcast to that fold's held-out endoscopies; SEQC = top-sample L-LATE >= t_seq
    DQ = np.full((NEND, 10), np.nan)
    zs_all = lg_(RFC["O"]); ZS = zs_all.copy(); CS = np.full((n, 10), np.nan)
    for j in range(10):
        r = REPS[j]
        for k in range(1, 11):
            c = make_ctx(S, ST, j, k, INFO); te = c.te_e; tr = c.tr_e; te_s = S["FO"][:, j] == k; xs = {}
            for m in ("L-CNV", "L-LATE"):
                x = np.full(n, np.nan); s_ = S["I"][m][(r, k)]; x[s_.index.values] = s_.values; x[te_s] = S["O"][m][te_s, j]; xs[m] = emean_logit(x)
            zi = c.ef["zi"]; ZI[te, j] = zi[te]; ZC[te, j] = xs["L-CNV"][te]; ZL[te, j] = xs["L-LATE"][te]
            BAND[te, j] = c.r49_band[te]; FL49[te, j] = c.r49_flag[te]; NS49[te, j] = c.r49_ns[te]; SEQC[te, j] = (c.ef["pl_top"] >= c.cuts[2])[te]
            Pm = tr & (elab == 1); CI[te, j] = cut90(zi[Pm]); CC[te, j] = cut90(xs["L-CNV"][Pm]); CL[te, j] = cut90(xs["L-LATE"][Pm])
            si = RFC["I"][(r, k)]; tri = si.index.values[popm[si.index.values]]; CS[te_s, j] = cut90(lg_(si.reindex(tri).values)[y[tri] == 1])
    return ZI, ZC, ZL, BAND, FL49, NS49, CI, CC, CL, SEQC, DQ, ZS, CS
ZI, ZC, ZL, BAND, FL49, NS49, CI, CC, CL, SEQC, DQ, ZS, CS = build()
# ------------------------------------------------------------------ smoke: R49 mean-logit gate (clean) = ART gate.json
Ap = patient_arrays(S, FL49, NS49); p1 = parts(S, Ap, np.ones((1, P_)))
nP = int((plab == 1).sum()); nN = int((plab == 0).sum())
smoke = {"caught": rr(nP * met(p1, "caught_share")[0], 2), "np_flagged": rr(nN * met(p1, "np_flagged_share")[0], 2), "seq_per_patient": rr(met(p1, "seq_per_patient")[0])}
smoke["reproduces_ART_gate_json"] = bool(abs(smoke["caught"] - 31.1) < 0.051 and abs(smoke["np_flagged"] - 32.3) < 0.051 and abs(smoke["seq_per_patient"] - 1.701) < 0.0006)
print("smoke", smoke, flush=True); assert smoke["reproduces_ART_gate_json"], smoke
# ------------------------------------------------------------------ per-endoscopy quantities
DE = ZI.std(1, ddof=1)                                   # disagreement
DEp = sg(ZI).std(1, ddof=1)                              # sensitivity: disagreement on the probability scale
ME = np.abs(ZI - CI)                                     # distance to the fold's 90%-sensitivity cut-off (per repeat)
pbar = sg(ZI).mean(1); HE = -(pbar * np.log(pbar) + (1 - pbar) * np.log(1 - pbar))
ERR = (ZI >= CI) != (elab[:, None] == 1)                 # H&E error at the fold's cut-off
SGE = ZI - CI
DQp = np.full((NEND, 10), np.nan)
for j in range(10):                                      # fold training quartile of D (label-free; training endoscopies of that fold)
    for k in range(1, 11):
        te = S["EF"][:, j] == k; DQ[te, j] = np.percentile(DE[~te], 75); DQp[te, j] = np.percentile(DEp[~te], 75)
cutcheck = {"outside_band_calls_disagreeing_with_cut90": int((((BAND == 2) != (ZI >= CI)) & (BAND != 1)).sum()), "endoscopy_repeat_cells": int(NEND * 10)}
# samples (pre-event)
sidx = np.where(popm)[0]; spat = np.full(n, -1)
for e, s_ in enumerate(es): spat[s_] = pidx[e]
assert (spat[sidx] >= 0).all()
DS = ZS[sidx].std(1, ddof=1); MS = np.abs(ZS[sidx] - CS[sidx]); ps_ = sg(ZS[sidx]).mean(1); HS = -(ps_ * np.log(ps_) + (1 - ps_) * np.log(1 - ps_))
ERRS = (ZS[sidx] >= CS[sidx]) != (y[sidx][:, None] == 1); spat = spat[sidx]; SGS = ZS[sidx] - CS[sidx]; DSp = sg(ZS[sidx]).std(1, ddof=1)
# ------------------------------------------------------------------ helpers
def logit_fit(X, yv, it=50):
    """unpenalised logistic regression by Newton; returns beta (with intercept), log-likelihood"""
    Xd = np.column_stack([np.ones(len(X)), X]); b = np.zeros(Xd.shape[1])
    for _ in range(it):
        p = sg(Xd @ b); W = p * (1 - p) + 1e-12; g = Xd.T @ (yv - p); H = (Xd * W[:, None]).T @ Xd; st = np.linalg.solve(H, g); b += st
        if np.abs(st).max() < 1e-10: break
    p = np.clip(sg(Xd @ b), 1e-12, 1 - 1e-12); return b, float((yv * np.log(p) + (1 - yv) * np.log(1 - p)).sum()), Xd, p
def cluster_wald(X, yv, cl, which):
    b, ll, Xd, p = logit_fit(X, yv); W = p * (1 - p); Hinv = np.linalg.inv((Xd * W[:, None]).T @ Xd); sc = Xd * (yv - p)[:, None]
    G = np.zeros((Xd.shape[1], Xd.shape[1]))
    for u in np.unique(cl): v = sc[cl == u].sum(0); G += np.outer(v, v)
    nc = len(np.unique(cl)); V = Hinv @ G @ Hinv * nc / (nc - 1); z = b[which] / np.sqrt(V[which, which]); return float(b[which]), float(2 * norm.sf(abs(z)))
def cv_auc(X, yv, cl, nf=5, seed=0):
    """patient-grouped 5-fold held-out linear predictor (duplicates of a patient stay together)"""
    u = np.unique(cl); f = {p: i % nf for i, p in enumerate(np.random.RandomState(seed).permutation(u))}; fo = np.array([f[p] for p in cl]); out = np.zeros(len(yv))
    for q in range(nf):
        t = fo != q; b = logit_fit(X[t], yv[t])[0]; out[~t] = np.column_stack([np.ones((~t).sum()), X[~t]]) @ b
    return roc_auc_score(yv, out)
def stdz(v): return (v - v.mean()) / v.std()
def auc_rep(score, lab):   # repeat-mean AUROC; score / lab (rows x 10)
    a = [roc_auc_score(lab[:, j], score[:, j]) for j in range(lab.shape[1]) if 0 < lab[:, j].sum() < len(lab)]; return float(np.mean(a))
def analyse(Dv, Mv, Hv, Ev, SGv, cl, rows, full=True):
    """steps 1-3 on the given rows (row indices into the unit arrays; repeats stacked as columns)"""
    G_ = SGv[rows].ravel(); D_ = Dv[rows]; M_ = Mv[rows]; H_ = Hv[rows]; E_ = Ev[rows].astype(int); c_ = cl[rows]; o = {}
    o["spearman_D_M"] = spearmanr(D_, M_.mean(1))[0]; o["spearman_D_entropy"] = spearmanr(D_, H_)[0]; o["spearman_M_entropy"] = spearmanr(M_.mean(1), H_)[0]
    Db = np.repeat(D_[:, None], 10, 1); o["error_rate"] = E_.mean()
    o["auroc_D_for_error"] = auc_rep(Db, E_); o["auroc_negM_for_error"] = auc_rep(-M_, E_); o["auroc_entropy_for_error"] = auc_rep(np.repeat(H_[:, None], 10, 1), E_)
    yv = E_.ravel().astype(float); Ms = stdz(M_.ravel()); Ds = stdz(Db.ravel()); cc = np.repeat(c_, 10)
    b1, ll1, Xd1, p1_ = logit_fit(Ms[:, None], yv); b2, ll2, Xd2, p2_ = logit_fit(np.column_stack([Ms, Ds]), yv)
    o["apparent_auroc_M"] = roc_auc_score(yv, Xd1 @ b1); o["apparent_auroc_M_plus_D"] = roc_auc_score(yv, Xd2 @ b2); o["apparent_auroc_gain"] = o["apparent_auroc_M_plus_D"] - o["apparent_auroc_M"]
    o["beta_D_per_sd"] = b2[2]
    if full:
        o["lr_stat_naive"] = 2 * (ll2 - ll1); o["lr_p_naive_ignores_clustering"] = float(chi2.sf(2 * (ll2 - ll1), 1))
        o["beta_D_cluster_wald_p"] = cluster_wald(np.column_stack([Ms, Ds]), yv, cc, 2)[1]
    # flexible control for the score itself: piecewise quadratic in the signed distance to the cut-off (separate on each side) + entropy of the mean probability
    sd_ = (G_ >= 0).astype(float); Gs = G_ / G_.std(); X0 = np.column_stack([Gs, Gs ** 2, sd_, sd_ * Gs, sd_ * Gs ** 2, stdz(np.repeat(H_, 10))])
    o["cv_auroc_score_flex"] = cv_auc(X0, yv, cc); o["cv_auroc_score_flex_plus_D"] = cv_auc(np.column_stack([X0, Ds]), yv, cc); o["cv_auroc_gain_over_flex"] = o["cv_auroc_score_flex_plus_D"] - o["cv_auroc_score_flex"]
    o["beta_D_per_sd_given_flex"] = logit_fit(np.column_stack([X0, Ds]), yv)[0][-1]
    if full: o["beta_D_given_flex_cluster_wald_p"] = cluster_wald(np.column_stack([X0, Ds]), yv, cc, X0.shape[1] + 1)[1]
    o["cv_auroc_M"] = cv_auc(Ms[:, None], yv, cc); o["cv_auroc_M_plus_D"] = cv_auc(np.column_stack([Ms, Ds]), yv, cc); o["cv_auroc_gain"] = o["cv_auroc_M_plus_D"] - o["cv_auroc_M"]
    return o
def step45(rows, DV, DQV):
    """steps 4-5 on endoscopy rows (repeats as columns); counts are repeat means"""
    lab = (elab[rows] == 1)[:, None]; B = BAND[rows]; conf = B != 1; call = B == 2; wrong = conf & (call != lab)
    hiD = (DV[rows][:, None] >= DQV[rows]); o = {}
    cnv_ok = (ZC[rows] >= CC[rows]) == lab; late_ok = (ZL[rows] >= CL[rows]) == lab
    for nm, g in (("confident_topD", conf & hiD), ("confident_restD", conf & ~hiD)):
        o[nm] = {"n": g.sum(0).mean(), "wrong": (g & wrong).sum(0).mean(), "wrong_rate": (g & wrong).sum() / max(g.sum(), 1),
                 "wrong_progressor_low_band": (g & wrong & lab).sum(0).mean(), "wrong_np_high_band": (g & wrong & ~lab).sum(0).mean(),
                 "cnv_fixes": (g & wrong & cnv_ok).sum(0).mean(), "late_fixes": (g & wrong & late_ok).sum(0).mean(),
                 "cnv_breaks_correct": (g & ~wrong & ~cnv_ok).sum(0).mean(), "late_breaks_correct": (g & ~wrong & ~late_ok).sum(0).mean()}
        for m in ("cnv", "late"): o[nm][f"{m}_net_per_100"] = 100 * (o[nm][f"{m}_fixes"] - o[nm][f"{m}_breaks_correct"]) / max(o[nm]["n"], 1e-9)
    o["wrong_rate_topD_minus_rest"] = o["confident_topD"]["wrong_rate"] - o["confident_restD"]["wrong_rate"]
    # step 5: equal budget, endoscopy level. H&E-only call = cut90; sequenced endoscopies called by top-sample L-LATE >= t_seq (R49's sequencing rule)
    he = ZI[rows] >= CI[rows]; bud = (B == 1).sum(0); Dr = DV[rows]; selD = np.zeros_like(he)
    for j in range(10): selD[np.argsort(-Dr, kind="stable")[:bud[j]], j] = True
    for nm, sel in (("band", B == 1), ("D", selD)):
        fin = np.where(sel, SEQC[rows], he)
        o[f"budget_{nm}"] = {"sequenced": sel.sum(0).mean(), "np_corrected": (sel & he & ~SEQC[rows] & ~lab).sum(0).mean(), "progressor_lost": (sel & he & ~SEQC[rows] & lab).sum(0).mean(),
                             "progressor_rescued": (sel & ~he & SEQC[rows] & lab).sum(0).mean(), "np_newly_flagged": (sel & ~he & SEQC[rows] & ~lab).sum(0).mean(),
                             "np_flagged_final": (fin & ~lab).sum(0).mean(), "progressor_flagged_final": (fin & lab).sum(0).mean(), "overlap_with_band": (sel & (B == 1)).sum(0).mean()}
    o["budget_D_minus_band_np_flagged"] = o["budget_D"]["np_flagged_final"] - o["budget_band"]["np_flagged_final"]
    o["budget_D_minus_band_progressor_flagged"] = o["budget_D"]["progressor_flagged_final"] - o["budget_band"]["progressor_flagged_final"]
    return o
def flat(d, pre=""):
    out = {}
    for k, v in d.items():
        if isinstance(v, dict): out.update(flat(v, pre + k + "."))
        else: out[pre + k] = v
    return out
# ------------------------------------------------------------------ observed + patient bootstrap
eall = np.arange(NEND); sall = np.arange(len(sidx))
ob_e = analyse(DE, ME, HE, ERR, SGE, pidx, eall); ob_s = analyse(DS, MS, HS, ERRS, SGS, spat, sall); ob_45 = step45(eall, DE, DQ); ob_45p = step45(eall, DEp, DQp)
ob_ep = analyse(DEp, ME, HE, ERR, SGE, pidx, eall); ob_sp = analyse(DSp, MS, HS, ERRS, SGS, spat, sall)
rng_ = np.random.RandomState(0); Dd = []
while len(Dd) < NBU:
    mm = np.bincount(rng_.choice(P_, P_), minlength=P_)
    if (mm * plab).sum() > 0 and (mm * (1 - plab)).sum() > 0: Dd.append(mm)
EP = [np.where(pidx == p)[0] for p in range(P_)]; SP = [np.where(spat == p)[0] for p in range(P_)]
BE, BS, B45, BEp, BSp, B45p = [], [], [], [], [], []
for b, mm in enumerate(Dd):
    pr = np.repeat(np.arange(P_), mm); re_ = np.concatenate([EP[p] for p in pr]); rs_ = np.concatenate([SP[p] for p in pr])
    # bootstrap patients get distinct cluster ids (duplicates kept together in CV folds)
    cid_e = np.concatenate([np.full(len(EP[p]), i) for i, p in enumerate(pr)]); cid_s = np.concatenate([np.full(len(SP[p]), i) for i, p in enumerate(pr)])
    BE.append(flat(analyse(DE[re_], ME[re_], HE[re_], ERR[re_], SGE[re_], cid_e, np.arange(len(re_)), full=False)))
    BS.append(flat(analyse(DS[rs_], MS[rs_], HS[rs_], ERRS[rs_], SGS[rs_], cid_s, np.arange(len(rs_)), full=False)))
    B45.append(flat(step45(re_, DE, DQ))); B45p.append(flat(step45(re_, DEp, DQp)))
    BEp.append(flat(analyse(DEp[re_], ME[re_], HE[re_], ERR[re_], SGE[re_], cid_e, np.arange(len(re_)), full=False)))
    BSp.append(flat(analyse(DSp[rs_], MS[rs_], HS[rs_], ERRS[rs_], SGS[rs_], cid_s, np.arange(len(rs_)), full=False)))
    if b % 200 == 0: print("draw", b, round(time.time() - t00), "s", flush=True)
def summ(ob, BB):
    o = {}
    for k, v in flat(ob).items():
        bv = np.array([x[k] for x in BB if k in x], float); bv = bv[np.isfinite(bv)]
        o[k] = {"value": rr(v), "ci95": [rr(np.percentile(bv, 2.5)), rr(np.percentile(bv, 97.5))]} if len(bv) else {"value": rr(v)}
    return o
CNT = ("n", "wrong", "wrong_progressor_low_band", "wrong_np_high_band", "cnv_fixes", "late_fixes", "cnv_breaks_correct", "late_breaks_correct", "np_corrected", "progressor_lost", "progressor_rescued", "np_newly_flagged")
def mask5(d):
    """repeat-mean counts < 5 -> '<5' (no interval), per RUN_RULES"""
    for k, v in d.items():
        if k.split(".")[-1] in CNT and isinstance(v.get("value"), float) and v["value"] < 5: d[k] = {"value": "<5"}
    return d
res = {"task": "unc", "agent": "UNC", "smoke_R49_mean_logit_gate_clean": smoke, "cut_check": cutcheck, "draws": len(Dd),
       "n": {"endoscopies": int(NEND), "pre_event_samples": int(len(sidx)), "patients": int(P_), "progressor_patients": nP},
       "endoscopy_steps1to3": summ(ob_e, BE), "sample_steps1to3": summ(ob_s, BS), "endoscopy_steps4to5": mask5(summ(ob_45, B45)),
       "sensitivity_D_probability_scale": {"endoscopy": summ(ob_ep, BEp), "sample": summ(ob_sp, BSp), "endoscopy_steps4to5": mask5(summ(ob_45p, B45p))},
       "D_distribution_endoscopy": {"median": rr(np.median(DE)), "iqr": [rr(np.percentile(DE, 25)), rr(np.percentile(DE, 75))]},
       "M_distribution_endoscopy": {"median": rr(np.median(ME)), "iqr": [rr(np.percentile(ME, 25)), rr(np.percentile(ME, 75))]},
       "runtime_s": round(time.time() - t00),
       "note": ("D = SD over the 10 repeats of the held-out clean L-IMG log-odds (endoscopy: mean sample logit); M = |held-out log-odds - fold's training 90%-sensitivity cut-off|; "
                "H&E error at that cut-off; confident = outside the R49 mean-logit gate middle band; top-quartile D = D >= 75th percentile of the fold's training endoscopies; "
                "CNV / LATE fix = their own endoscopy mean-logit on the correct side of their own training 90%-sensitivity cut-off; budget: same number of endoscopies per repeat "
                "as the middle band, chosen by highest D; sequenced endoscopies called by top-sample L-LATE >= t_seq (R49), others by H&E at the 90%-sensitivity cut. "
                "Flexible score control = piecewise quadratic in (log-odds - cut-off), separate on each side, + entropy of the mean probability. Sensitivity: D on the probability scale (SD of the 10 probabilities). "
                "Counts are repeat means over 10 repeats; patient bootstrap 2,000 draws (RandomState(0)); cluster Wald p uses patient clusters; CV AUROC = 5-fold patient-grouped held-out")}
json.dump(res, open(f"{OUTU}/unc.json", "w"), indent=1, default=lambda x: x.item() if hasattr(x, "item") else str(x)); print("UNC DONE", res["runtime_s"], "s", flush=True)

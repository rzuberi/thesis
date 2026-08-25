"""2.23 (joint, Rehan 2026-08-25): power map — minimum detectable fusion delta
per cohort (GLM-5.3's proposal, wave-2 consultation).

For each cohort's (n, positives/events) and observed unimodal performance,
simulate paired arm predictions: a base risk score achieving the observed
AUC/C, and a fusion score = base signal + injected delta, correlated at rho.
Detection = paired bootstrap 95% CI on the delta excludes zero. 200 replicates
per (cohort, delta, rho). Readout: detection probability surface + the minimum
delta detectable with 80% power — 'a fusion benefit below X was structurally
undetectable in cohort Y'.

Binary-endpoint cohorts use the biGaussian AUC model. Survival cohorts use
exponential event times with risk-proportional hazard and censoring matched to
the observed event fraction, scored by Harrell's C.
"""
import json, os
import numpy as np
from scipy.stats import norm

OUT = os.environ.get("OUTDIR", ".")
REPS, N_BOOT = 200, 500
DELTAS = [0.01, 0.02, 0.03, 0.05, 0.075, 0.10]
RHOS = [0.6, 0.8, 0.9]

COHORTS = {
    "swg":        {"kind": "binary",   "n": 150,  "pos": 50,  "base": 0.731},
    "occams_v3":  {"kind": "survival", "n": 87,   "events": 58,  "base": 0.55},
    "tcga_oac":   {"kind": "survival", "n": 65,   "events": 36,  "base": 0.55},
    "tcga_pool":  {"kind": "survival", "n": 399,  "events": 176, "base": 0.615},
    "erin_grade": {"kind": "binary",   "n": 1574, "pos": 528, "base": 0.926},
    "erin_prog":  {"kind": "binary",   "n": 153,  "pos": 28,  "base": 0.819},
}

def cindex(risk, time, event):
    order = np.argsort(time)
    risk, time, event = risk[order], time[order], event[order]
    num = den = 0
    for i in range(len(time)):
        if not event[i]: continue
        later = time > time[i]
        den += later.sum()
        num += (risk[later] < risk[i]).sum() + 0.5 * (risk[later] == risk[i]).sum()
    return num / den if den else 0.5

def auc_fast(y, s):
    r = np.argsort(np.argsort(s))
    return (r[y == 1].sum() - (y == 1).sum() * ((y == 1).sum() + 1) / 2) / ((y == 1).sum() * (y == 0).sum())

def make_binary(rng, n, pos, base_auc, delta_auc, rho):
    """Two correlated scores whose true AUCs are base and base+delta."""
    y = np.zeros(n, int); y[rng.choice(n, pos, replace=False)] = 1
    mu_a = norm.ppf(base_auc) * np.sqrt(2)          # biGaussian separation for AUC
    mu_b = norm.ppf(min(base_auc + delta_auc, 0.999)) * np.sqrt(2)
    z1 = rng.normal(size=n); z2 = rho * z1 + np.sqrt(1 - rho**2) * rng.normal(size=n)
    a = z1 + mu_a * y
    b = z2 + mu_b * y
    return y, a, b

def make_survival(rng, n, events, base_c, delta_c, rho):
    """Exponential times; hazard = exp(beta*score); beta tuned so C≈target."""
    z1 = rng.normal(size=n); z2 = rho * z1 + np.sqrt(1 - rho**2) * rng.normal(size=n)
    def beta_for(c):  # empirical monotone map, tuned per draw
        lo, hi = 0.0, 3.0
        for _ in range(12):
            mid = (lo + hi) / 2
            t = rng.exponential(1 / np.exp(mid * z1[:200] if n >= 200 else mid * z1))
            lo, hi = (mid, hi) if cindex(z1[:len(t)], t, np.ones(len(t), bool)) < c else (lo, mid)
        return (lo + hi) / 2
    ba, bb = beta_for(base_c), beta_for(min(base_c + delta_c, 0.99))
    t_lat = rng.exponential(np.exp(-(ba * z1)))
    cens = np.quantile(t_lat, events / n)
    time = np.minimum(t_lat, cens); event = t_lat <= cens
    # risk scores: a = true risk driver z1; b = z2 blended toward z1's signal more strongly
    return time, event, z1, (bb / max(ba, 1e-6)) * (rho * z1) + np.sqrt(1 - rho**2) * z2 + (bb - ba) * z1

res = {"_meta": {"reps": REPS, "n_boot": N_BOOT, "deltas": DELTAS, "rhos": RHOS,
                 "cohorts": COHORTS}}
for cname, c in COHORTS.items():
    res[cname] = {}
    for rho in RHOS:
        for d in DELTAS:
            detect = 0; runs = 0
            for rep in range(REPS):
                rng = np.random.RandomState(rep * 7919 + int(d * 1000) + int(rho * 100))
                if c["kind"] == "binary":
                    y, a, b = make_binary(rng, c["n"], c["pos"], c["base"], d, rho)
                    stats = []
                    for _ in range(N_BOOT):
                        idx = rng.randint(0, c["n"], c["n"])
                        if y[idx].sum() in (0, c["n"]): continue
                        stats.append(auc_fast(y[idx], b[idx]) - auc_fast(y[idx], a[idx]))
                else:
                    time, event, a, b = make_survival(rng, c["n"], c["events"], c["base"], d, rho)
                    stats = []
                    for _ in range(N_BOOT // 5):   # C-index bootstrap is costlier
                        idx = rng.randint(0, c["n"], c["n"])
                        if event[idx].sum() < 5: continue
                        stats.append(cindex(b[idx], time[idx], event[idx])
                                     - cindex(a[idx], time[idx], event[idx]))
                if len(stats) < 50: continue
                lo = np.percentile(stats, 2.5)
                runs += 1; detect += int(lo > 0)
            if runs:
                res[cname][f"rho{rho}_d{d}"] = {"power": round(detect / runs, 3), "runs": runs}
        # minimum detectable delta at 80% power for this rho
        mdd = next((d for d in DELTAS
                    if res[cname].get(f"rho{rho}_d{d}", {}).get("power", 0) >= 0.8), None)
        res[cname][f"rho{rho}_min_detectable_80"] = mdd
        print(cname, "rho", rho, "MDD80:", mdd, flush=True)
json.dump(res, open(os.path.join(OUT, "results.json"), "w"), indent=2)
print("wrote results.json")

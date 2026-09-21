"""ACE-B timeline from the Barrett's-database scrape: for the 125 ACE-B participants matched in May 2026,
pull endoscopy dates, pathology reports, the 8-juror DB-corpus grade per report (jury_full_* outputs,
keyed by pathology_text_id), and derive baseline grade, max grade, HGD/IMC progression and follow-up."""
import glob, json, os
from collections import Counter
import numpy as np, pandas as pd
E = "/mnt/scratche/slow/fmlab/zuberi01/barretts_db_export"; A = "/mnt/scratche/slow/fmlab/zuberi01/phd/aceb_meta"
T = "/mnt/scratche/slow/fmlab/zuberi01/phd/thesis"; OUT = os.environ.get("OUTDIR", ".")
ORD = {"NDBE": 0, "IND": 1, "LGD": 2, "HGD": 3, "CANCER": 4}; INV = {v: k for k, v in ORD.items()}
def mr(s): s = pd.Series(s).dropna(); return {"median": float(s.median()), "min": float(s.min()), "max": float(s.max()), "n": int(len(s))} if len(s) else None
ac = pd.read_csv(A + "/aceb_official_case_presence_in_barretts_db_20260527_150857.csv", dtype=str)
case2pid = {}
for _, r in ac.iterrows():
    for x in str(r.participant_ids).replace(";", ",").split(","):
        if x.strip() and x.strip().lower() != "nan": case2pid.setdefault(r.study_number_normalized, set()).add(x.strip())
pids = sorted({p for s in case2pid.values() for p in s})
seattle = dict(zip(ac.study_number_normalized, ac.Histology_Seattle_Protocol))
afi = pd.to_datetime(ac["Date AFI"], dayfirst=True, errors="coerce"); wle = pd.to_datetime(ac["Date WLE"], dayfirst=True, errors="coerce")
res = {"official_cases": len(ac), "found_in_db": int((ac.found_in_barretts_db == "yes").sum()), "participants": len(pids),
       "official_case_dates": {"AFI_min": str(afi.min().date()) if afi.notna().any() else None, "AFI_max": str(afi.max().date()) if afi.notna().any() else None,
                               "WLE_min": str(wle.min().date()) if wle.notna().any() else None, "WLE_max": str(wle.max().date()) if wle.notna().any() else None,
                               "AFI_by_year": afi.dt.year.value_counts().sort_index().to_dict()},
       "seattle_histology_official": ac.Histology_Seattle_Protocol.value_counts().to_dict()}
# endoscopies
en = pd.read_parquet(E + "/endoscopy.parquet"); en["d"] = pd.to_datetime(en.endoscopydate, dayfirst=True, errors="coerce"); en["pid"] = en.participant_id.astype(str)
ea = en[en.pid.isin(pids)]; per = ea.groupby("pid").size()
res["endoscopies_db"] = {"participants_with_endoscopy": int(ea.pid.nunique()), "records": len(ea), "per_participant": mr(per),
                         "date_min": str(ea.d.min().date()) if ea.d.notna().any() else None, "date_max": str(ea.d.max().date()) if ea.d.notna().any() else None,
                         "ACE-B_tagged_records": int(ea.endoscopyref.astype(str).str.contains("ACE", case=False).sum()),
                         "span_years_per_participant": mr((ea.groupby("pid").d.max() - ea.groupby("pid").d.min()).dt.days / 365.25)}
# pathology reports + DB jury labels
pt = pd.read_csv(E + "/pathology_text_normalised_full.csv", dtype=str, usecols=["pathology_text_id", "participant_id", "receiveddatetime", "specimennumber"])
pt["d"] = pd.to_datetime(pt.receiveddatetime, dayfirst=True, errors="coerce"); pt["pid"] = pt.participant_id.astype(str)
votes = {}
for f in glob.glob(T + "/feasibility/runs/jury_full_*/output/llm_grades_*.csv"):
    d = pd.read_csv(f, dtype=str); d = d[d.llm_grade.isin(ORD)]
    for c, g in zip(d.CaseName, d.llm_grade): votes.setdefault(str(c), []).append(g)
lab = {}
for c, vs in votes.items():
    top, n = Counter(vs).most_common(1)[0]
    if len(vs) >= 4 and n / len(vs) >= 0.5: lab[c] = top
pt["grade"] = pt.pathology_text_id.astype(str).map(lab)
pa = pt[pt.pid.isin(pids)].sort_values("d")
res["pathology_db"] = {"participants_with_reports": int(pa.pid.nunique()), "reports": len(pa), "reports_with_jury_grade": int(pa.grade.notna().sum()),
                       "reports_per_participant": mr(pa.groupby("pid").size()), "date_min": str(pa.d.min().date()) if pa.d.notna().any() else None, "date_max": str(pa.d.max().date()) if pa.d.notna().any() else None,
                       "grade_dist_all_reports": pa.grade.value_counts().to_dict()}
rows = []
for pid, g in pa[pa.grade.notna()].groupby("pid"):
    g = g.sort_values("d"); seq = g.grade.map(ORD).values; dates = g.d.values
    base = int(seq[0]); mx = int(seq.max()); hg = np.where(seq >= 3)[0]
    first_hgd = dates[hg[0]] if len(hg) else None
    prevalent = base >= 3; progressed = (not prevalent) and len(hg) > 0
    tte = (pd.Timestamp(first_hgd) - pd.Timestamp(dates[0])).days if progressed else None
    fu = (pd.Timestamp(dates[-1]) - pd.Timestamp(dates[0])).days
    rows.append({"pid": pid, "n_reports": len(g), "baseline": INV[base], "max": INV[mx], "prevalent_HGD_plus": prevalent, "progressed_to_HGD_plus": progressed, "tte_days": tte, "followup_days": fu})
tl = pd.DataFrame(rows)
res["derived_timeline"] = {"participants_with_graded_reports": len(tl), "baseline_grade": tl.baseline.value_counts().to_dict(), "max_grade": tl["max"].value_counts().to_dict(),
                           "prevalent_HGD_or_cancer_at_first_report": int(tl.prevalent_HGD_plus.sum()), "progressed_to_HGD_or_cancer": int(tl.progressed_to_HGD_plus.sum()),
                           "non_progressors": int((~tl.prevalent_HGD_plus & ~tl.progressed_to_HGD_plus).sum()),
                           "time_to_progression_days": mr(tl[tl.progressed_to_HGD_plus].tte_days), "followup_days_nonprogressors": mr(tl[~tl.prevalent_HGD_plus & ~tl.progressed_to_HGD_plus].followup_days),
                           "reports_per_participant": mr(tl.n_reports),
                           "note": "grades are DB-corpus LLM-jury labels (majority of >=4 jurors); 'progression' = first HGD/CANCER report after a non-HGD baseline; compare with Leanne's 11/93/30 split"}
# hgd table / surveillance study membership
h = pd.read_parquet(E + "/hgd_pathology_table.parquet"); h["pid"] = h.participant_id.astype(str)
res["hgd_pathology_table_rows_for_aceb"] = int(h.pid.isin(pids).sum())
s = pd.read_parquet(E + "/studypatientbarrettssurv.parquet"); s["pid"] = s.participant_id.astype(str)
res["barretts_surveillance_study_rows_for_aceb"] = int(s.pid.isin(pids).sum())
tl.to_csv(os.path.join(OUT, "aceb_participant_timeline.csv"), index=False)
json.dump(res, open(os.path.join(OUT, "results.json"), "w"), indent=2, default=str); print(json.dumps(res, indent=1, default=str))

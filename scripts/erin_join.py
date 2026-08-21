"""EXECUTION_PLAN 2.1: ERIN slide<->label join.

Chain: feature h5 (named by slide-dir UUID) -> WSIExport manifest (Case Folder Name
-> Case Identifier) -> report CaseName -> jury label + patient. Output: erin_master.csv
(one row per slide with features + train-eligible label + patient id + date).
"""
import glob, os, re
import pandas as pd

ERIN = "/mnt/scratche/fast/fmlab/datasets/imaging/ERIN"
FEAT = ERIN + "/features/20x_224px/features_uni_v2"
LBL = "/mnt/scratche/slow/fmlab/zuberi01/phd/thesis/labeller/erin_labels_jury_final.csv"
OUT = os.environ.get("OUTDIR", os.path.dirname(LBL))

mans = glob.glob(ERIN + "/slides/WSIExport_Result*.csv") + glob.glob(ERIN + "/raw/WSIExport_Result*.csv")
wx = pd.concat([pd.read_csv(f, dtype=str) for f in mans], ignore_index=True)
wx.columns = [c.strip() for c in wx.columns]
folder_col = next(c for c in wx.columns if "Folder" in c)
case_col = next(c for c in wx.columns if "Identifier" in c)
wx = wx[[folder_col, case_col]].dropna().drop_duplicates()
wx.columns = ["uuid", "case_id"]
wx["uuid"] = wx["uuid"].str.strip().str.lower()
print(f"manifest rows: {len(wx)}")

feats = pd.DataFrame({"h5": sorted(glob.glob(os.path.join(FEAT, "*.h5")))})
feats["uuid"] = feats["h5"].map(lambda p: os.path.basename(p)[:-3].lower())

lab = pd.read_csv(LBL, dtype=str)
def norm_case(s):  # PS18-06758 / PS18.06758 / ps1806758 -> PS18-6758 canonical
    m = re.search(r"PS\s?(\d{2})[.\-/ ]?0*(\d{3,6})", str(s).upper())
    return f"PS{m.group(1)}-{int(m.group(2))}" if m else str(s).strip().upper()
lab["case_key"] = lab["CaseName"].map(norm_case)
wx["case_key"] = wx["case_id"].map(norm_case)

m = feats.merge(wx, on="uuid", how="left").merge(
    lab[["case_key", "anon_id", "CaseName", "CollectedOrOrdered",
         "final_label", "label_status", "jury_frac"]], on="case_key", how="left")
m.to_csv(os.path.join(OUT, "erin_master.csv"), index=False)
print(f"slides: {len(feats)} | with case link: {m['case_id'].notna().sum()} | "
      f"with label: {m['final_label'].notna().sum()} | "
      f"train-eligible: {(m['label_status'].isin(['train_eligible','adjudicated'])).sum()} | "
      f"patients: {m['anon_id'].nunique()}")
print(m["final_label"].value_counts(dropna=False).to_dict())

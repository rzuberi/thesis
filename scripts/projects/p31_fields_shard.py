"""P31 first pass: multi-field structured extraction from ERIN reports with one strong local LLM.
One shard of the imaged ERIN cases (erin_master CaseName, one UNI2 slide per case) -> one JSON per report with the
fields below. Runs entirely on-cluster (ollama on the job GPU). Raw JSON string is kept for every report.
Env: SHARD, N_SHARDS, MODEL (medgemma:27b), OUTDIR, INPUT (csv with CaseName column; default = erin_master cases)."""
import json, os, re, subprocess, sys, time, urllib.request, threading, csv
import pandas as pd
ERIN = "/mnt/scratche/fast/fmlab/datasets/imaging/ERIN/data/PathologyReport_AnonIds.csv"; T = "/mnt/scratche/slow/fmlab/zuberi01/phd/thesis"
OUT = os.environ.get("OUTDIR", "."); MODEL = os.environ.get("MODEL", "medgemma:27b"); SHARD = int(os.environ.get("SHARD", "0")); N = int(os.environ.get("N_SHARDS", "1")); CONC = int(os.environ.get("CONC", "4"))
INPUT = os.environ.get("INPUT", T + "/labeller/erin_master.csv")
os.environ.setdefault("OLLAMA_MODELS", "/mnt/scratche/slow/fmlab/zuberi01/ollama-models"); os.environ.setdefault("OLLAMA_NUM_PARALLEL", str(CONC))
PORT = 20000 + int(os.environ.get("SLURM_JOB_ID", "0")) % 20000; os.environ["OLLAMA_HOST"] = f"127.0.0.1:{PORT}"; BASE = f"http://127.0.0.1:{PORT}"
srv = subprocess.Popen([os.path.expanduser("~/.local/bin/ollama"), "serve"], stdout=open(os.path.join(OUT, f"ollama_{SHARD}.log"), "w"), stderr=subprocess.STDOUT)
for _ in range(60):
    try: urllib.request.urlopen(BASE + "/api/tags", timeout=3); break
    except Exception: time.sleep(2)
FIELDS = {"grade": ["NDBE", "IND", "LGD", "HGD", "CANCER", "NA"], "site": ["oesophagus", "goj", "stomach", "other", "mixed"], "specimen_type": ["biopsy", "emr_esd", "resection", "other"],
          "intestinal_metaplasia": ["present", "absent", "not_stated"], "goblet_cells": ["present", "absent", "not_stated"], "inflammation": ["none", "mild", "moderate", "severe", "not_stated"],
          "ulceration_or_erosion": ["yes", "no", "not_stated"], "squamous_only": ["yes", "no"], "gastric_mucosa_present": ["yes", "no", "not_stated"], "treatment_effect": ["yes", "no"],
          "p53": ["abnormal", "normal", "not_done", "not_stated"], "diagnostic_certainty": ["definite", "probable", "uncertain"]}
PROMPT = """You extract structured fields from UK oesophageal surveillance histopathology reports.
Consider ONLY the oesophagus / gastro-oesophageal junction findings for grade; other fields describe the whole report.
Ignore historical mentions and negated findings when deciding what is CURRENTLY present.
Return ONLY a JSON object with exactly these keys and allowed values:
"grade": worst current oesophageal/GOJ finding: NDBE | IND | LGD | HGD | CANCER | NA
"site": oesophagus | goj | stomach | other | mixed
"specimen_type": biopsy | emr_esd | resection | other
"intestinal_metaplasia": present | absent | not_stated
"goblet_cells": present | absent | not_stated
"inflammation": none | mild | moderate | severe | not_stated   (worst active or chronic inflammation described)
"ulceration_or_erosion": yes | no | not_stated
"squamous_only": yes | no   (yes if the specimens contain squamous mucosa only, no columnar/glandular epithelium)
"gastric_mucosa_present": yes | no | not_stated
"treatment_effect": yes | no   (post-ablation change, neosquamous epithelium, scarring, prior EMR/RFA site, buried glands)
"p53": abnormal | normal | not_done | not_stated
"diagnostic_certainty": definite | probable | uncertain   (how confident the pathologist sounds about the main diagnosis)
"n_specimens": integer count of lettered specimens (A, B, C ...) or null
REPORT:
"""
rep = pd.read_csv(ERIN, dtype=str).fillna(""); rep["text"] = (rep.ClinicalInformation_redacted + "\n" + rep.GrossDescription_redacted + "\n" + rep.MicroscopicDescription_redacted + "\n" + rep.FinalDiagnosis_redacted + "\n" + rep.Addendum1_redacted).str.slice(0, 7000)
cases = pd.read_csv(INPUT, dtype=str).CaseName.dropna().unique(); cases = sorted(set(cases) & set(rep.CaseName)); mine = cases[SHARD::N]
text_of = dict(zip(rep.CaseName, rep.text))
out = os.path.join(OUT, f"fields_{MODEL.replace(':', '_')}_shard{SHARD}.jsonl"); done = set()
if os.path.exists(out):
    for l in open(out):
        try: done.add(json.loads(l)["CaseName"])
        except Exception: pass
todo = [c for c in mine if c not in done]; print(f"shard {SHARD}/{N}: {len(mine)} cases, {len(todo)} to do", flush=True)
lock = threading.Lock(); t0 = time.time(); cnt = [0]
def ask(text):
    body = json.dumps({"model": MODEL, "prompt": PROMPT + text, "stream": False, "format": "json", "think": False, "options": {"temperature": 0, "num_predict": 300}}).encode()
    r = urllib.request.Request(BASE + "/api/generate", data=body, headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(r, timeout=600).read())["response"]
def parse(raw):
    try: d = json.loads(raw)
    except Exception:
        m = re.search(r"\{.*\}", raw, re.S); d = json.loads(m.group(0)) if m else {}
    o = {}
    for k, allowed in FIELDS.items():
        v = str(d.get(k, "")).strip().lower(); v = v.upper() if k == "grade" else v; o[k] = v if v in allowed else "PARSE_FAIL"
    try: o["n_specimens"] = int(d.get("n_specimens")) if d.get("n_specimens") not in (None, "", "null") else None
    except Exception: o["n_specimens"] = None
    return o
def work(c):
    raw = ""
    for _ in range(3):
        try: raw = ask(text_of[c]); break
        except Exception as e: time.sleep(3)
    rec = {"CaseName": c, "model": MODEL, **parse(raw), "raw": raw[:2000], "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
    with lock:
        with open(out, "a") as fh: fh.write(json.dumps(rec) + "\n")
        cnt[0] += 1
        if cnt[0] <= 2: print("RAW:", raw[:300], flush=True)
        if cnt[0] % 50 == 0: print(f"{cnt[0]}/{len(todo)} {time.time()-t0:.0f}s", flush=True)
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(CONC) as ex: list(ex.map(work, todo))
srv.terminate(); print(f"[exit] shard {SHARD} done {cnt[0]} in {time.time()-t0:.0f}s", flush=True)

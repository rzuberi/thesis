"""EXECUTION_PLAN 2.7 (extended 2026-08-20): local-LLM grading of ERIN report text.

Runs entirely on-cluster (report text never leaves). Starts an ollama server on the
job's GPU, grades a shard of reports onto the oesophageal ladder with a strict JSON
prompt (site-scoped: oesophagus/GOJ findings only — the site-mismatch lesson from
the adjudication audit), writes a per-report CSV shard.

Env: SHARD (0-based), N_SHARDS, MODEL (default qwen3:14b), SMOKE=adjudicated|all
"""
import json, os, subprocess, sys, time, urllib.request
import pandas as pd

ERIN = "/mnt/scratche/fast/fmlab/datasets/imaging/ERIN/data/PathologyReport_AnonIds.csv"
IDX = "/mnt/scratche/slow/fmlab/zuberi01/phd/thesis/feasibility/runs/adjpack/output/adjudication_index.csv"
OUT = os.environ.get("OUTDIR", ".")
MODEL = os.environ.get("MODEL", "qwen3:14b")
SHARD = int(os.environ.get("SHARD", "0")); N_SHARDS = int(os.environ.get("N_SHARDS", "1"))
SMOKE = os.environ.get("SMOKE", "")
TEXT = ["FinalDiagnosis_redacted", "MicroscopicDescription_redacted",
        "Addendum1_redacted", "Addendum2_redacted", "Addendum3_redacted"]

os.environ.setdefault("OLLAMA_MODELS", "/mnt/scratche/slow/fmlab/zuberi01/ollama-models")
srv = subprocess.Popen([os.path.expanduser("~/.local/bin/ollama"), "serve"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for _ in range(60):
    try:
        urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=3); break
    except Exception: time.sleep(2)
subprocess.run([os.path.expanduser("~/.local/bin/ollama"), "pull", MODEL], check=True)

PROMPT = """You grade UK oesophageal surveillance pathology reports.
Consider ONLY findings in the oesophagus or gastro-oesophageal junction (GOJ/cardia).
Ignore stomach-body, duodenal, colorectal or other-site findings entirely.
Ignore historical mentions ("known/previous/history of carcinoma") — grade only what
is diagnosed as CURRENTLY PRESENT in this specimen. Negated findings ("no dysplasia",
"no evidence of malignancy") do not count.

Grade on this ladder, choosing the WORST current oesophageal/GOJ finding:
NDBE (Barrett's/intestinal metaplasia without dysplasia, or benign/normal),
IND (indefinite for dysplasia), LGD (low-grade dysplasia),
HGD (high-grade dysplasia), CANCER (carcinoma of any type, incl. intramucosal),
NA (report not gradeable on this ladder).

Reply with ONLY a JSON object: {"grade":"NDBE|IND|LGD|HGD|CANCER|NA"}

REPORT:
"""

def grade(text):
    body = json.dumps({"model": MODEL, "prompt": PROMPT + text[:6000],
                       "stream": False, "format": "json",
                       "options": {"temperature": 0}}).encode()
    r = urllib.request.Request("http://127.0.0.1:11434/api/generate", data=body,
                               headers={"Content-Type": "application/json"})
    resp = json.loads(urllib.request.urlopen(r, timeout=300).read())["response"]
    try:
        g = json.loads(resp).get("grade", "PARSE_FAIL")
        return g if g in ("NDBE", "IND", "LGD", "HGD", "CANCER", "NA") else "PARSE_FAIL"
    except Exception:
        return "PARSE_FAIL"

rep = pd.read_csv(ERIN, dtype=str, low_memory=False).fillna("")
rep["_text"] = rep[TEXT].agg(" ".join, axis=1)
if SMOKE == "adjudicated":
    idx = pd.read_csv(IDX)
    rep = rep[rep["CaseName"].isin(idx["CaseName"])]
rep = rep.reset_index(drop=True)
rep = rep[rep.index % N_SHARDS == SHARD]
print(f"model={MODEL} shard={SHARD}/{N_SHARDS} reports={len(rep)}", flush=True)

rows, t0 = [], time.time()
for i, (_, r) in enumerate(rep.iterrows()):
    rows.append({"CaseName": r["CaseName"], "llm_grade": grade(r["_text"])})
    if i % 25 == 0:
        print(f"{i}/{len(rep)} elapsed={time.time()-t0:.0f}s", flush=True)
out = os.path.join(OUT, f"llm_grades_{MODEL.replace(':','_').replace('/','_')}_shard{SHARD}.csv")
pd.DataFrame(rows).to_csv(out, index=False)
print("wrote", out, f"({(time.time()-t0)/max(len(rep),1):.1f}s/report)")
srv.terminate()

"""Multi-grader ERIN hand-labelling app — cluster-internal only (NHS IG: report
text never leaves the institutional network). Stdlib-only HTTP server + SQLite.

Design: every grader labels the 20-case COMMON CORE (inter-rater kappa), then
unique 20-case blocks assigned from the 200-case pool on demand. Every click is
saved server-side immediately; sessions resume by name. Shared passphrase.

Run:  env GRADING_PASS=... python grading_app.py [port]
Data: /mnt/scratche/slow/fmlab/zuberi01/hand_grading/{cases.json,grading.db}
Export: sqlite3 grading.db "select * from labels" or /export?pw=...
"""
import json, os, sqlite3, sys, threading, urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

H = "/mnt/scratche/slow/fmlab/zuberi01/hand_grading"
PASS = os.environ.get("GRADING_PASS", "change-me")
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8471
CASES = json.load(open(H + "/cases.json"))
CORE = [c for c in CASES if c["block"] == "core"]
POOL = [c for c in CASES if c["block"] == "pool"]
BY_CASE = {c["case"]: c for c in CASES}
GRADES = ["NDBE", "IND", "LGD", "HGD", "CANCER", "CANT_GRADE"]

db = sqlite3.connect(H + "/grading.db", check_same_thread=False)
db.execute("""CREATE TABLE IF NOT EXISTS labels
  (grader TEXT, case_name TEXT, grade TEXT, note TEXT,
   ts DATETIME DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (grader, case_name))""")
db.execute("""CREATE TABLE IF NOT EXISTS assignments
  (grader TEXT, case_name TEXT, ord INTEGER, PRIMARY KEY (grader, case_name))""")
db.commit()
lock = threading.Lock()

def assign(grader):
    with lock:
        rows = db.execute("SELECT case_name FROM assignments WHERE grader=? ORDER BY ord",
                          (grader,)).fetchall()
        if rows:
            return [r[0] for r in rows]
        used = {r[0] for r in db.execute("SELECT DISTINCT case_name FROM assignments")}
        fresh = [c["case"] for c in POOL if c["case"] not in used][:20]
        order = [c["case"] for c in CORE] + fresh
        db.executemany("INSERT OR IGNORE INTO assignments VALUES (?,?,?)",
                       [(grader, c, i) for i, c in enumerate(order)])
        db.commit()
        return order

PAGE = """<!doctype html><meta charset="utf-8"><title>ERIN Lab Grading</title>
<style>
body{font-family:-apple-system,sans-serif;background:#f7f7f8;margin:0;padding:24px;display:flex;justify-content:center;color:#1a1a1a}
.wrap{max-width:860px;width:100%}
.card{background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:22px}
pre{white-space:pre-wrap;font-family:Georgia,serif;font-size:15px;line-height:1.55;max-height:50vh;overflow-y:auto}
button{font-size:14px;padding:10px 16px;border-radius:8px;border:1px solid #d1d5db;background:#fff;cursor:pointer;margin:3px}
button.sel{background:#2563eb;color:#fff}
input,textarea{padding:8px;border:1px solid #d1d5db;border-radius:8px;font-size:14px}
.bar{height:8px;background:#e5e7eb;border-radius:4px;margin:12px 0}.fill{height:100%;background:#2563eb;border-radius:4px}
.mut{color:#666;font-size:13px}
</style>
<div class="wrap" id="app"></div>
<script>
const GRADES=["NDBE","IND","LGD","HGD","CANCER","CANT_GRADE"];
const KEY={"1":0,"2":1,"3":2,"4":3,"5":4,"0":5};
let S={name:localStorage.getItem("g_name")||"",pw:localStorage.getItem("g_pw")||"",cases:[],labels:{},idx:0};
const app=document.getElementById("app");
function login(){app.innerHTML=`<div class="card"><h2>ERIN report grading</h2>
<p class="mut">Grade the worst finding in each report. Your progress saves on every click and you can stop and resume any time.</p>
<p><input id="nm" placeholder="Your name" value="${S.name}"> <input id="pw" type="password" placeholder="Lab passphrase" value="${S.pw}"> <button onclick="start()">Start / Resume</button></p>
<p class="mut" id="err"></p></div>`}
async function start(){
  S.name=document.getElementById("nm").value.trim().toLowerCase();S.pw=document.getElementById("pw").value;
  if(!S.name)return;
  const r=await fetch(`/session?name=${encodeURIComponent(S.name)}&pw=${encodeURIComponent(S.pw)}`);
  if(!r.ok){document.getElementById("err").textContent="Wrong passphrase";return}
  localStorage.setItem("g_name",S.name);localStorage.setItem("g_pw",S.pw);
  const d=await r.json();S.cases=d.cases;S.labels=d.labels;
  S.idx=S.cases.findIndex(c=>!(c.case in S.labels));if(S.idx<0)S.idx=0;render()}
function render(){
  const c=S.cases[S.idx],done=Object.keys(S.labels).length;
  app.innerHTML=`<div class="card">
  <div class="mut">${S.name} &middot; report ${S.idx+1}/${S.cases.length} (${c.case}) &middot; keys 1-5, 0=can't grade</div>
  <div class="bar"><div class="fill" style="width:${100*done/S.cases.length}%"></div></div>
  <pre>${c.text.replace(/</g,"&lt;")}</pre>
  <div>${GRADES.map((g,j)=>`<button class="${S.labels[c.case]===g?"sel":""}" onclick="grade('${g}')">${j<5?j+1:0} ${g.replace("_"," ")}</button>`).join("")}</div>
  <textarea id="note" placeholder="optional note" style="width:100%;box-sizing:border-box;margin-top:8px"></textarea>
  <p><button onclick="move(-1)">&larr; Prev</button> <button onclick="move(1)">Next &rarr;</button>
  <span class="mut">${done}/${S.cases.length} graded${done>=S.cases.length?" — all done, thank you!":""}</span></p></div>`}
async function grade(g){
  const c=S.cases[S.idx],note=document.getElementById("note").value;
  S.labels[c.case]=g;
  await fetch("/label",{method:"POST",headers:{"Content-Type":"application/json"},
    body:JSON.stringify({name:S.name,pw:S.pw,case:c.case,grade:g,note:note})});
  if(S.idx<S.cases.length-1)S.idx++;render()}
function move(d){S.idx=Math.min(S.cases.length-1,Math.max(0,S.idx+d));render()}
document.addEventListener("keydown",e=>{
  if(e.target.tagName==="TEXTAREA"||e.target.tagName==="INPUT")return;
  if(e.key in KEY)grade(GRADES[KEY[e.key]]);
  else if(e.key==="ArrowLeft")move(-1);else if(e.key==="ArrowRight")move(1)});
login();
</script>"""

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _json(self, obj, code=200):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        q = dict(urllib.parse.parse_qsl(u.query))
        if u.path == "/":
            b = PAGE.encode()
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
        elif u.path == "/session":
            if q.get("pw") != PASS: return self._json({"err": "bad pw"}, 403)
            name = q.get("name", "").strip().lower()
            if not name: return self._json({"err": "no name"}, 400)
            order = assign(name)
            labels = dict(db.execute(
                "SELECT case_name, grade FROM labels WHERE grader=?", (name,)).fetchall())
            self._json({"cases": [{"case": c, "text": BY_CASE[c]["text"]} for c in order],
                        "labels": labels})
        elif u.path == "/export":
            if q.get("pw") != PASS: return self._json({"err": "bad pw"}, 403)
            rows = db.execute("SELECT grader, case_name, grade, note, ts FROM labels").fetchall()
            self._json({"n": len(rows), "labels": rows})
        else:
            self._json({"err": "not found"}, 404)
    def do_POST(self):
        if self.path != "/label": return self._json({"err": "not found"}, 404)
        n = int(self.headers.get("Content-Length", 0))
        d = json.loads(self.rfile.read(n))
        if d.get("pw") != PASS: return self._json({"err": "bad pw"}, 403)
        g = d.get("grade")
        if g not in GRADES or d.get("case") not in BY_CASE: return self._json({"err": "bad"}, 400)
        with lock:
            db.execute("INSERT OR REPLACE INTO labels (grader, case_name, grade, note) VALUES (?,?,?,?)",
                       (d["name"].strip().lower(), d["case"], g, str(d.get("note", ""))[:500]))
            db.commit()
        self._json({"ok": True})

print(f"grading app on port {PORT}", flush=True)
ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()

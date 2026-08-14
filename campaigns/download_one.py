"""Per-file GDC download (one array element = one slide). Idempotent by size check."""
import os, sys, time, urllib.request, pandas as pd

CSV = sys.argv[1]; OUTDIR = sys.argv[2]
IDX = int(os.environ["SLURM_ARRAY_TASK_ID"])
df = pd.read_csv(CSV)
if IDX >= len(df): print("[skip] beyond manifest"); sys.exit(0)
r = df.iloc[IDX]
os.makedirs(OUTDIR, exist_ok=True)
dest = os.path.join(OUTDIR, r["file_name"])
if os.path.exists(dest) and os.path.getsize(dest) == int(r["size"]):
    print("[skip] exists", dest); sys.exit(0)
lock = dest + ".lock"
try: os.mkdir(lock)
except FileExistsError:
    if time.time() - os.path.getmtime(lock) < 2 * 3600: print("[skip] locked"); sys.exit(0)
    os.rmdir(lock); os.mkdir(lock)
try:
    t0 = time.time()
    with urllib.request.urlopen(f"https://api.gdc.cancer.gov/data/{r['file_id']}", timeout=3600) as resp, \
         open(dest + ".part", "wb") as fh:
        while True:
            chunk = resp.read(1 << 22)
            if not chunk: break
            fh.write(chunk)
    assert os.path.getsize(dest + ".part") == int(r["size"]), "size mismatch"
    os.replace(dest + ".part", dest)
    print(f"[done] {dest} {int(r['size'])/1e6:.0f}MB in {time.time()-t0:.0f}s")
finally:
    try: os.rmdir(lock)
    except OSError: pass

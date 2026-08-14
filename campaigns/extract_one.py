"""Per-slide UNI2-h feature extraction (one Slurm array element = one slide).

Usage: extract_one.py --manifest FILE --outdir DIR [--name-from dir|file]
Index = OFFSET + SLURM_ARRAY_TASK_ID. Idempotent: skips if output h5 exists;
atomic lock dir guards against cross-partition duplicates (stale >3h reclaimed).
Tissue mask from a 2048px thumbnail before any full-res reads.
"""
import os, sys, time, argparse, numpy as np, h5py

ap = argparse.ArgumentParser()
ap.add_argument("--manifest", required=True)
ap.add_argument("--outdir", required=True)
ap.add_argument("--name-from", default="dir", choices=["dir", "file"])
a = ap.parse_args()

IDX = int(os.environ.get("OFFSET", "0")) + int(os.environ["SLURM_ARRAY_TASK_ID"])
paths = [l.strip() for l in open(a.manifest) if l.strip()]
if IDX >= len(paths):
    print(f"[skip] index {IDX} beyond manifest ({len(paths)})"); sys.exit(0)
path = paths[IDX]
base = os.path.basename(os.path.dirname(path)) if a.name_from == "dir" \
    else os.path.splitext(os.path.basename(path))[0]
out = os.path.join(a.outdir, base + ".h5")
lock = out + ".lock"
os.makedirs(a.outdir, exist_ok=True)

if os.path.exists(out):
    print(f"[skip] exists {out}"); sys.exit(0)
try:
    os.mkdir(lock)
except FileExistsError:
    if time.time() - os.path.getmtime(lock) < 3 * 3600:
        print(f"[skip] locked {lock}"); sys.exit(0)
    os.rmdir(lock)
    try: os.mkdir(lock)
    except FileExistsError: print("[skip] lock race lost"); sys.exit(0)

try:
    import torch, timm, openslide
    TILE, BATCH, MAX_TILES = 224, 128, 8000
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"idx={IDX} slide={path} dev={dev}")

    m = timm.create_model("vit_giant_patch14_224", pretrained=False,
                          img_size=224, patch_size=14, depth=24, num_heads=24,
                          init_values=1e-5, embed_dim=1536, mlp_ratio=2.66667 * 2,
                          num_classes=0, no_embed_class=True,
                          mlp_layer=timm.layers.SwiGLUPacked, act_layer=torch.nn.SiLU,
                          reg_tokens=8, dynamic_img_size=True)
    sd = torch.load("/mnt/scratche/slow/fmlab/zuberi01/phd/UNI2-h/pytorch_model.bin",
                    map_location="cpu")
    m.load_state_dict(sd, strict=True)
    m.eval().to(dev)
    MEAN = np.array([0.485, 0.456, 0.406]); STD = np.array([0.229, 0.224, 0.225])

    sl = openslide.OpenSlide(path)
    try: mpp0 = float(sl.properties.get("openslide.mpp-x", "0.25"))
    except Exception: mpp0 = 0.25
    lvl = min(range(sl.level_count), key=lambda l: abs(mpp0 * sl.level_downsamples[l] - 0.5))
    ds = sl.level_downsamples[lvl]
    W, H = sl.level_dimensions[lvl]

    thumb = np.asarray(sl.get_thumbnail((2048, 2048)).convert("L"), dtype=np.float32)
    ty, tx = thumb.shape
    sy, sx = ty / (H * ds / ds), tx / W  # thumb px per level-lvl px
    sy = ty / H
    coords = []
    for yy in range(0, H - TILE, TILE):
        for xx in range(0, W - TILE, TILE):
            p = thumb[int(yy * sy):max(int(yy * sy) + 1, int((yy + TILE) * sy)),
                      int(xx * sx):max(int(xx * sx) + 1, int((xx + TILE) * sx))]
            if p.size and p.mean() < 220 and p.std() > 4:
                coords.append((xx, yy))
    if len(coords) > MAX_TILES:
        coords = [coords[i] for i in np.linspace(0, len(coords) - 1, MAX_TILES).astype(int)]
    print(f"tissue tiles: {len(coords)} of grid {(H//TILE)*(W//TILE)}")

    feats, batch, kept = [], [], []
    t0 = time.time()
    with torch.inference_mode():
        for (xx, yy) in coords:
            t = np.asarray(sl.read_region((int(xx * ds), int(yy * ds)), lvl,
                                          (TILE, TILE)).convert("RGB"))
            if t.mean() > 235 or t.std() < 8: continue
            batch.append(((t / 255.0 - MEAN) / STD).transpose(2, 0, 1)); kept.append((xx, yy))
            if len(batch) == BATCH:
                x = torch.tensor(np.stack(batch), dtype=torch.float32, device=dev)
                feats.append(m(x).cpu().numpy()); batch = []
        if batch:
            x = torch.tensor(np.stack(batch), dtype=torch.float32, device=dev)
            feats.append(m(x).cpu().numpy())
    F = np.vstack(feats).astype(np.float32) if feats else np.zeros((0, 1536), np.float32)
    tmp = out + ".part"
    with h5py.File(tmp, "w") as h:
        h.create_dataset("features", data=F)
        h.create_dataset("coords", data=np.array(kept, dtype=np.int32))
        h.attrs["slide_path"] = path; h.attrs["level"] = lvl; h.attrs["mpp_used"] = mpp0 * ds
    os.replace(tmp, out)
    print(f"[done] {out} {F.shape} in {time.time()-t0:.0f}s")
finally:
    try: os.rmdir(lock)
    except OSError: pass

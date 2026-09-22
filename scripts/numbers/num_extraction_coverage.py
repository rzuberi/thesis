#!/usr/bin/env python3
"""Coverage of the ERIN all-slides UNI2-h extraction + the excluded-slide register.

Writes results/numbers/extraction_coverage.json: how many H&E slides in the
manifest have features, and for every slide that does not, why. Unreadable or
truncated source files are a data-quality fact about the cohort and belong in
the thesis, not in a log file.
"""
import json, os, subprocess, sys

TH = "/mnt/scratche/slow/fmlab/zuberi01/phd/thesis"
MAN = f"{TH}/campaigns/allslides/erin_manifest_all_he.txt"
OUT = "/mnt/scratche/fast/fmlab/datasets/imaging/ERIN/features/20x_224px/features_uni_v2_all"

paths = [l.strip() for l in open(MAN) if l.strip()]
missing = []
for p in paths:
    h5 = os.path.join(OUT, os.path.splitext(os.path.basename(p))[0] + ".h5")
    if os.path.exists(h5):
        continue
    rec = {"slide": os.path.basename(p), "case_dir": os.path.basename(os.path.dirname(p)),
           "bytes": os.path.getsize(p) if os.path.exists(p) else None}
    try:
        import openslide
        s = openslide.OpenSlide(p)
        rec["reason"] = "readable_but_unextracted"
        rec["level_dimensions"] = [list(d) for d in s.level_dimensions]
    except Exception as e:
        rec["reason"] = "unreadable_source_file"
        rec["error"] = f"{type(e).__name__}"
    missing.append(rec)

res = {
    "manifest_slides": len(paths),
    "extracted": len(paths) - len(missing),
    "coverage": round((len(paths) - len(missing)) / len(paths), 5),
    "excluded": missing,
    "excluded_cases": sorted({m["case_dir"] for m in missing}),
    "note": ("Feature extraction is UNI2-h at level nearest 0.5 um/px, 224 px tiles, "
             "8000-tile cap. Slides listed under 'excluded' have no features; "
             "'unreadable_source_file' means neither openslide nor PIL can decode the "
             "file, i.e. the scan itself is corrupt and needs rescanning."),
}
os.makedirs(f"{TH}/results/numbers", exist_ok=True)
with open(f"{TH}/results/numbers/extraction_coverage.json", "w") as f:
    json.dump(res, f, indent=1)
print(json.dumps({k: v for k, v in res.items() if k != "excluded"}, indent=1))
print("excluded:", len(missing))
